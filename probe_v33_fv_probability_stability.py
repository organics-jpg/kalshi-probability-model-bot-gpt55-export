"""Stability audit for the v34 FV probability surface.

This is a probability-model audit, not a scorer. It checks whether the v34
materiality-gated anti-persistence gain over v32 is broad across chronological
blocks and physics regimes, using the already-generated FV replay prediction
files.

No live bot code/process or orders are touched.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from probe_market_interval_80coverage import clean_json, pct
from probe_mushroom_v29_fv_surface import PROB_EPS


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
INPUTS = {
    "all_heartbeats": OUT_DIR / "mushroom_v29_fv_surface_predictions_two_side_all_heartbeats_latest.csv",
    "minute_bucket": OUT_DIR / "mushroom_v29_fv_surface_predictions_two_side_minute_bucket_latest.csv",
}
REPORT_MD = OUT_DIR / "v34_fv_probability_stability_latest.md"
REPORT_JSON = OUT_DIR / "v34_fv_probability_stability_latest.json"
BLOCK_CSV = OUT_DIR / "v34_fv_probability_stability_blocks_latest.csv"
BUCKET_CSV = OUT_DIR / "v34_fv_probability_stability_buckets_latest.csv"
SUMMARY_CSV = OUT_DIR / "v34_fv_probability_stability_summary_latest.csv"

MODELS = [
    "v28_live_surface",
    "v28_avg90",
    "v32_avg110_final60_exact",
    "v33_antipersist3",
    "v34_material_antipersist3",
]
BASE_MODEL = "v32_avg110_final60_exact"
CANDIDATE_MODEL = "v34_material_antipersist3"


def finite_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)


def opportunity_rows(rows: pd.DataFrame) -> pd.DataFrame:
    yes = rows[rows["side"].astype(str).eq("yes")].drop_duplicates("opportunity_key").copy()
    yes["entry_dt"] = pd.to_datetime(yes["entry_dt"], utc=True, errors="coerce")
    yes["outcome_yes"] = yes["outcome"].astype(str).str.lower().eq("yes").astype(float)
    for model in MODELS:
        yes[f"{model}_p_yes"] = finite_float(yes[f"{model}_p_yes"])
    for col in [
        "seconds_to_close",
        "v32_avg110_final60_exact_d_sigma",
        "v34_material_antipersist3_anti_persistence_shift_dollars",
        "v34_material_antipersist3_anti_persistence_materiality_gate",
        "v34_material_antipersist3_anti_persistence_logit_weight",
        "signed_velocity_dps_3m",
    ]:
        if col in yes.columns:
            yes[col] = finite_float(yes[col])
    return yes.dropna(subset=["entry_dt", "market", "outcome_yes"]).sort_values("entry_dt").reset_index(drop=True)


def metric(y: np.ndarray, p: np.ndarray) -> dict[str, Any]:
    p = np.asarray(p, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(p) & np.isfinite(y)
    if not mask.any():
        return {"rows": 0, "brier": None, "logloss": None, "side_accuracy": None, "mean_p_yes": None, "yes_rate": None}
    p = np.clip(p[mask], PROB_EPS, 1.0 - PROB_EPS)
    y = y[mask]
    return {
        "rows": int(len(p)),
        "brier": float(np.mean((p - y) ** 2)),
        "logloss": float(-(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)).mean()),
        "side_accuracy": float(((p >= 0.5) == (y >= 0.5)).mean()),
        "mean_p_yes": float(p.mean()),
        "yes_rate": float(y.mean()),
    }


def add_market_blocks(rows: pd.DataFrame) -> pd.DataFrame:
    markets = (
        rows.groupby("market", as_index=False)
        .agg(first_entry=("entry_dt", "min"), split=("split", "first"))
        .sort_values("first_entry")
        .reset_index(drop=True)
    )
    markets["block10"] = pd.qcut(np.arange(len(markets)), q=10, labels=False)
    markets["block20"] = pd.qcut(np.arange(len(markets)), q=20, labels=False)
    return rows.merge(markets[["market", "block10", "block20"]], on="market", how="left")


def summarize(rows: pd.DataFrame, dataset: str) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for split in ["all", "train", "validation", "holdout"]:
        part = rows if split == "all" else rows[rows["split"].astype(str).eq(split)]
        for model in MODELS:
            records.append({"dataset": dataset, "split": split, "model": model, **metric_for_model(part, model)})
    return pd.DataFrame(records)


def metric_for_model(rows: pd.DataFrame, model: str) -> dict[str, Any]:
    return metric(rows["outcome_yes"].to_numpy(dtype=float), finite_float(rows[f"{model}_p_yes"]).to_numpy(dtype=float))


def block_rows(rows: pd.DataFrame, dataset: str) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for block_kind in ["block10", "block20"]:
        for block, part in rows.groupby(block_kind, dropna=True):
            base = metric_for_model(part, BASE_MODEL)
            cand = metric_for_model(part, CANDIDATE_MODEL)
            records.append(
                {
                    "dataset": dataset,
                    "block_kind": block_kind,
                    "block": int(block),
                    "rows": int(cand["rows"] or 0),
                    "base_brier": base["brier"],
                    "candidate_brier": cand["brier"],
                    "brier_delta": None if base["brier"] is None or cand["brier"] is None else cand["brier"] - base["brier"],
                    "base_logloss": base["logloss"],
                    "candidate_logloss": cand["logloss"],
                    "logloss_delta": None
                    if base["logloss"] is None or cand["logloss"] is None
                    else cand["logloss"] - base["logloss"],
                    "base_side_accuracy": base["side_accuracy"],
                    "candidate_side_accuracy": cand["side_accuracy"],
                }
            )
    return pd.DataFrame(records)


def bucket_labels(rows: pd.DataFrame, feature: str) -> pd.Series:
    values = finite_float(rows[feature])
    if feature == "seconds_to_close":
        return pd.cut(values, [0, 60, 90, 120, 180, 300, 600, 900], include_lowest=True).astype(str)
    if feature == "abs_v32_d_sigma":
        return pd.cut(values, [0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, np.inf], include_lowest=True).astype(str)
    try:
        return pd.qcut(values, q=8, duplicates="drop").astype(str)
    except ValueError:
        return pd.Series(["nan"] * len(rows), index=rows.index)


def bucket_rows(rows: pd.DataFrame, dataset: str) -> pd.DataFrame:
    work = rows.copy()
    work["abs_v32_d_sigma"] = finite_float(work["v32_avg110_final60_exact_d_sigma"]).abs()
    features = [
        "seconds_to_close",
        "abs_v32_d_sigma",
        "v34_material_antipersist3_anti_persistence_shift_dollars",
        "v34_material_antipersist3_anti_persistence_materiality_gate",
        "v34_material_antipersist3_anti_persistence_logit_weight",
        "signed_velocity_dps_3m",
    ]
    records: list[dict[str, Any]] = []
    for feature in features:
        if feature not in work.columns:
            continue
        work["_bucket"] = bucket_labels(work, feature)
        for split in ["all", "validation", "holdout"]:
            split_rows = work if split == "all" else work[work["split"].astype(str).eq(split)]
            for bucket, part in split_rows.groupby("_bucket", dropna=False):
                if str(bucket).lower() in {"nan", "nat"}:
                    continue
                base = metric_for_model(part, BASE_MODEL)
                cand = metric_for_model(part, CANDIDATE_MODEL)
                records.append(
                    {
                        "dataset": dataset,
                        "split": split,
                        "feature": feature,
                        "bucket": str(bucket),
                        "rows": int(cand["rows"] or 0),
                        "brier_delta": None
                        if base["brier"] is None or cand["brier"] is None
                        else cand["brier"] - base["brier"],
                        "logloss_delta": None
                        if base["logloss"] is None or cand["logloss"] is None
                        else cand["logloss"] - base["logloss"],
                        "candidate_brier": cand["brier"],
                        "candidate_logloss": cand["logloss"],
                        "candidate_side_accuracy": cand["side_accuracy"],
                        "mean_p_yes": cand["mean_p_yes"],
                        "yes_rate": cand["yes_rate"],
                    }
                )
    return pd.DataFrame(records)


def stability_summary(blocks: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (dataset, block_kind), group in blocks.groupby(["dataset", "block_kind"]):
        bd = finite_float(group["brier_delta"])
        ld = finite_float(group["logloss_delta"])
        rows.append(
            {
                "dataset": dataset,
                "block_kind": block_kind,
                "blocks": int(len(group)),
                "brier_improved_blocks": int(bd.lt(0).sum()),
                "logloss_improved_blocks": int(ld.lt(0).sum()),
                "mean_brier_delta": float(bd.mean()),
                "worst_brier_delta": float(bd.max()),
                "mean_logloss_delta": float(ld.mean()),
                "worst_logloss_delta": float(ld.max()),
            }
        )
    return pd.DataFrame(rows)


def write_report(summary: pd.DataFrame, blocks: pd.DataFrame, buckets: pd.DataFrame) -> None:
    stab = stability_summary(blocks)
    high_rows = buckets[buckets["rows"].ge(100)].copy()
    worse = high_rows.sort_values(["brier_delta", "rows"], ascending=[False, False]).head(16)
    better = high_rows.sort_values(["brier_delta", "rows"], ascending=[True, False]).head(12)

    lines = [
        "# v34 FV Probability Stability",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Scope",
        "",
        "- Research-only stability audit for pure FV probability, not scoring.",
        "- Candidate: v34 materiality-gated anti-persistence FV surface versus v32 settlement/proxy FV surface.",
        "- No live bot code/process or orders are touched.",
        "",
        "## Split Metrics",
        "",
        "| dataset | split | model | rows | Brier | logloss | side acc | mean p_yes | yes rate |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    show_models = {BASE_MODEL, CANDIDATE_MODEL, "v28_live_surface"}
    for _, row in summary[summary["model"].isin(show_models)].iterrows():
        lines.append(
            f"| `{row['dataset']}` | {row['split']} | `{row['model']}` | {int(row['rows'])} | "
            f"{row['brier']:.6f} | {row['logloss']:.6f} | {pct(row['side_accuracy'])} | "
            f"{pct(row['mean_p_yes'])} | {pct(row['yes_rate'])} |"
        )
    lines += [
        "",
        "## Chronological Blocks",
        "",
        "| dataset | block kind | Brier improved | logloss improved | mean Brier delta | worst Brier delta | mean logloss delta | worst logloss delta |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in stab.iterrows():
        lines.append(
            f"| `{row['dataset']}` | `{row['block_kind']}` | {int(row['brier_improved_blocks'])}/{int(row['blocks'])} | "
            f"{int(row['logloss_improved_blocks'])}/{int(row['blocks'])} | {row['mean_brier_delta']:+.6f} | "
            f"{row['worst_brier_delta']:+.6f} | {row['mean_logloss_delta']:+.6f} | {row['worst_logloss_delta']:+.6f} |"
        )
    lines += [
        "",
        "## Worst v34 Buckets",
        "",
        "Rows floor: 100. Positive delta means v34 is worse than v32.",
        "",
        "| dataset | split | feature | bucket | rows | Brier delta | logloss delta | mean p_yes | yes rate |",
        "|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in worse.iterrows():
        lines.append(
            f"| `{row['dataset']}` | {row['split']} | `{row['feature']}` | `{row['bucket']}` | {int(row['rows'])} | "
            f"{row['brier_delta']:+.6f} | {row['logloss_delta']:+.6f} | {pct(row['mean_p_yes'])} | {pct(row['yes_rate'])} |"
        )
    lines += [
        "",
        "## Best v34 Buckets",
        "",
        "| dataset | split | feature | bucket | rows | Brier delta | logloss delta | mean p_yes | yes rate |",
        "|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in better.iterrows():
        lines.append(
            f"| `{row['dataset']}` | {row['split']} | `{row['feature']}` | `{row['bucket']}` | {int(row['rows'])} | "
            f"{row['brier_delta']:+.6f} | {row['logloss_delta']:+.6f} | {pct(row['mean_p_yes'])} | {pct(row['yes_rate'])} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "- v34 should not be promoted if the block improvement is narrow or if a large physics bucket is consistently worse.",
        "- Stable improvement here is still retrospective evidence; strict-forward rows remain mandatory.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": datetime.now(timezone.utc).isoformat(),
                    "summary": summary.to_dict("records"),
                    "stability": stab.to_dict("records"),
                }
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    summary_frames: list[pd.DataFrame] = []
    block_frames: list[pd.DataFrame] = []
    bucket_frames: list[pd.DataFrame] = []
    for dataset, path in INPUTS.items():
        if not path.exists():
            raise SystemExit(f"Missing predictions file: {path}")
        rows = add_market_blocks(opportunity_rows(pd.read_csv(path, low_memory=False)))
        summary_frames.append(summarize(rows, dataset))
        block_frames.append(block_rows(rows, dataset))
        bucket_frames.append(bucket_rows(rows, dataset))
    summary = pd.concat(summary_frames, ignore_index=True, sort=False)
    blocks = pd.concat(block_frames, ignore_index=True, sort=False)
    buckets = pd.concat(bucket_frames, ignore_index=True, sort=False)
    summary.to_csv(SUMMARY_CSV, index=False)
    blocks.to_csv(BLOCK_CSV, index=False)
    buckets.to_csv(BUCKET_CSV, index=False)
    write_report(summary, blocks, buckets)
    print("v34 FV probability stability complete")
    print(f"summary_rows={len(summary)} block_rows={len(blocks)} bucket_rows={len(buckets)} report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
