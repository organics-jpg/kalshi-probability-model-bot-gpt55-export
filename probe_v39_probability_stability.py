"""Block-stability audit for the v39 FV probability surface.

This is a pure probability audit, not a scorer or execution backtest. It
compares v39 with v38 and v28 across chronological market blocks in both replay
denominators.

No live bot files/processes are touched and no orders are submitted.
"""
from __future__ import annotations

import json
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
REPORT_MD = OUT_DIR / "v39_probability_stability_latest.md"
REPORT_JSON = OUT_DIR / "v39_probability_stability_latest.json"
SUMMARY_CSV = OUT_DIR / "v39_probability_stability_summary_latest.csv"
BLOCK_CSV = OUT_DIR / "v39_probability_stability_blocks_latest.csv"

MODELS = [
    "v28_live_surface",
    "v38_long60_antipersist",
    "v39_midband_v28_fallback",
]
CANDIDATE = "v39_midband_v28_fallback"
BASES = ["v28_live_surface", "v38_long60_antipersist"]


def finite_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)


def opportunity_rows(rows: pd.DataFrame) -> pd.DataFrame:
    yes = rows[rows["side"].astype(str).eq("yes")].drop_duplicates("opportunity_key").copy()
    yes["entry_dt"] = pd.to_datetime(yes["entry_dt"], utc=True, errors="coerce")
    yes["outcome_yes"] = yes["outcome"].astype(str).str.lower().eq("yes").astype(float)
    for model in MODELS:
        yes[f"{model}_p_yes"] = finite_float(yes[f"{model}_p_yes"])
    return yes.dropna(subset=["entry_dt", "market", "outcome_yes"]).sort_values("entry_dt").reset_index(drop=True)


def metric(y: np.ndarray, p: np.ndarray) -> dict[str, Any]:
    mask = np.isfinite(y) & np.isfinite(p)
    if not mask.any():
        return {"rows": 0, "brier": None, "logloss": None, "side_accuracy": None, "mean_p_yes": None, "yes_rate": None}
    y = np.asarray(y, dtype=float)[mask]
    p = np.clip(np.asarray(p, dtype=float)[mask], PROB_EPS, 1.0 - PROB_EPS)
    return {
        "rows": int(len(p)),
        "brier": float(np.mean((p - y) ** 2)),
        "logloss": float(-(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)).mean()),
        "side_accuracy": float(((p >= 0.5) == (y >= 0.5)).mean()),
        "mean_p_yes": float(p.mean()),
        "yes_rate": float(y.mean()),
    }


def metric_for_model(rows: pd.DataFrame, model: str) -> dict[str, Any]:
    return metric(rows["outcome_yes"].to_numpy(dtype=float), finite_float(rows[f"{model}_p_yes"]).to_numpy(dtype=float))


def add_blocks(rows: pd.DataFrame) -> pd.DataFrame:
    markets = (
        rows.groupby("market", as_index=False)
        .agg(first_entry=("entry_dt", "min"))
        .sort_values("first_entry")
        .reset_index(drop=True)
    )
    markets["block10"] = pd.qcut(np.arange(len(markets)), q=10, labels=False)
    markets["block20"] = pd.qcut(np.arange(len(markets)), q=20, labels=False)
    return rows.merge(markets[["market", "block10", "block20"]], on="market", how="left")


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_records: list[dict[str, Any]] = []
    block_records: list[dict[str, Any]] = []
    for dataset, path in INPUTS.items():
        rows = add_blocks(opportunity_rows(pd.read_csv(path, low_memory=False)))
        for split in ["all", "train", "validation", "holdout"]:
            part = rows if split == "all" else rows[rows["split"].astype(str).eq(split)]
            for model in MODELS:
                summary_records.append({"dataset": dataset, "split": split, "model": model, **metric_for_model(part, model)})
        for base in BASES:
            for block_kind in ["block10", "block20"]:
                for block, part in rows.groupby(block_kind, dropna=True):
                    base_m = metric_for_model(part, base)
                    cand_m = metric_for_model(part, CANDIDATE)
                    block_records.append(
                        {
                            "dataset": dataset,
                            "base_model": base,
                            "block_kind": block_kind,
                            "block": int(block),
                            "rows": int(cand_m["rows"] or 0),
                            "brier_delta": None
                            if base_m["brier"] is None or cand_m["brier"] is None
                            else cand_m["brier"] - base_m["brier"],
                            "logloss_delta": None
                            if base_m["logloss"] is None or cand_m["logloss"] is None
                            else cand_m["logloss"] - base_m["logloss"],
                        }
                    )
    return pd.DataFrame(summary_records), pd.DataFrame(block_records)


def block_summary(blocks: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for (dataset, base, block_kind), group in blocks.groupby(["dataset", "base_model", "block_kind"]):
        bd = finite_float(group["brier_delta"])
        ld = finite_float(group["logloss_delta"])
        records.append(
            {
                "dataset": dataset,
                "base_model": base,
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
    return pd.DataFrame(records)


def write_report(summary: pd.DataFrame, blocks: pd.DataFrame) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    stab = block_summary(blocks)
    lines = [
        "# v39 Probability Stability",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Pure FV probability block audit, not trade scoring.",
        "- Candidate: v39 mid-band v28 fallback versus live v28 and v38.",
        "- No live bot code/process or orders are touched.",
        "",
        "## Split Metrics",
        "",
        "| dataset | split | model | rows | Brier | logloss | side acc | mean p_yes | yes rate |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| `{row['dataset']}` | {row['split']} | `{row['model']}` | {int(row['rows'])} | "
            f"{row['brier']:.6f} | {row['logloss']:.6f} | {pct(row['side_accuracy'])} | "
            f"{pct(row['mean_p_yes'])} | {pct(row['yes_rate'])} |"
        )
    lines += [
        "",
        "## Chronological Blocks",
        "",
        "| dataset | base | block kind | Brier improved | logloss improved | mean Brier delta | worst Brier delta | mean logloss delta | worst logloss delta |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in stab.iterrows():
        lines.append(
            f"| `{row['dataset']}` | `{row['base_model']}` | `{row['block_kind']}` | "
            f"{int(row['brier_improved_blocks'])}/{int(row['blocks'])} | "
            f"{int(row['logloss_improved_blocks'])}/{int(row['blocks'])} | "
            f"{row['mean_brier_delta']:+.6f} | {row['worst_brier_delta']:+.6f} | "
            f"{row['mean_logloss_delta']:+.6f} | {row['worst_logloss_delta']:+.6f} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "- v39 should become the leading FV probability candidate only if it improves v38 without material block-level damage.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json({"generated_utc": generated, "summary": summary.to_dict("records"), "blocks": stab.to_dict("records")}),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    summary, blocks = build()
    summary.to_csv(SUMMARY_CSV, index=False)
    blocks.to_csv(BLOCK_CSV, index=False)
    write_report(summary, blocks)
    print("v39 probability stability complete")
    print(f"summary_rows={len(summary)} block_rows={len(blocks)} report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
