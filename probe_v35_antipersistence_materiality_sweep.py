"""Sweep low-parameter anti-persistence priors for the FV probability surface.

This is a probability-model probe, not a trade scorer.

v34 gates the short-memory anti-persistence anchor by an absolute dollar shift.
That is a questionable physics prior for BTC: a $40 projected reversion is not
equally material when the remaining sigma is $35 versus $150. This probe tests
the same Brownian anti-persistence idea with materiality measured in sigma
units, using already-replayed v32/v34 prediction files.

No live bot files/processes are touched and no orders are submitted.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from btc_mushroom_forecaster_v25_fast import _normal_cdf_np
from probe_market_interval_80coverage import clean_json, pct
from probe_mushroom_v29_fv_surface import PROB_EPS


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
INPUTS = {
    "all_heartbeats": OUT_DIR / "mushroom_v29_fv_surface_predictions_two_side_all_heartbeats_latest.csv",
    "minute_bucket": OUT_DIR / "mushroom_v29_fv_surface_predictions_two_side_minute_bucket_latest.csv",
}
REPORT_MD = OUT_DIR / "v35_antipersistence_materiality_sweep_latest.md"
REPORT_JSON = OUT_DIR / "v35_antipersistence_materiality_sweep_latest.json"
SUMMARY_CSV = OUT_DIR / "v35_antipersistence_materiality_sweep_summary_latest.csv"
RANK_CSV = OUT_DIR / "v35_antipersistence_materiality_sweep_rank_latest.csv"

BASE_MODEL = "v32_avg110_final60_exact"
REFERENCE_MODELS = [
    "v28_live_surface",
    "v32_avg110_final60_exact",
    "v33_antipersist3",
    "v34_material_antipersist3",
]


def finite_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)


def logit(p: Any) -> np.ndarray:
    arr = np.clip(np.asarray(p, dtype=float), PROB_EPS, 1.0 - PROB_EPS)
    return np.log(arr / (1.0 - arr))


def sigmoid(x: Any) -> np.ndarray:
    x_arr = np.asarray(x, dtype=float)
    pos = x_arr >= 0
    out = np.empty_like(x_arr, dtype=float)
    out[pos] = 1.0 / (1.0 + np.exp(-x_arr[pos]))
    ex = np.exp(x_arr[~pos])
    out[~pos] = ex / (1.0 + ex)
    return out


def normal_cdf(x: Any) -> np.ndarray:
    return np.asarray(_normal_cdf_np(np.asarray(x, dtype=float)), dtype=float)


def load_opportunities(path: Path) -> pd.DataFrame:
    rows = pd.read_csv(path, low_memory=False)
    yes = rows[rows["side"].astype(str).eq("yes")].drop_duplicates("opportunity_key").copy()
    yes["entry_dt"] = pd.to_datetime(yes["entry_dt"], utc=True, errors="coerce")
    yes["outcome_yes"] = yes["outcome"].astype(str).str.lower().eq("yes").astype(float)
    needed = [
        "entry_dt",
        "market",
        "split",
        "outcome_yes",
        "v32_avg110_final60_exact_p_yes",
        "v32_avg110_final60_exact_sigma_t_dollars",
        "v32_avg110_final60_exact_d_sigma",
        "v34_material_antipersist3_anti_persistence_shift_dollars",
    ]
    for col in needed:
        if col not in yes.columns:
            raise SystemExit(f"Missing required column {col} in {path}")
    numeric_cols = [
        "outcome_yes",
        "v32_avg110_final60_exact_p_yes",
        "v32_avg110_final60_exact_sigma_t_dollars",
        "v32_avg110_final60_exact_d_sigma",
        "v34_material_antipersist3_anti_persistence_shift_dollars",
        *[f"{model}_p_yes" for model in REFERENCE_MODELS if f"{model}_p_yes" in yes.columns],
    ]
    for col in numeric_cols:
        yes[col] = finite_float(yes[col])
    return yes.dropna(subset=needed).sort_values("entry_dt").reset_index(drop=True)


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


def metric_rows(rows: pd.DataFrame, dataset: str, model: str, p: np.ndarray, params: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    y_all = rows["outcome_yes"].to_numpy(dtype=float)
    for split in ["all", "train", "validation", "holdout"]:
        mask = np.ones(len(rows), dtype=bool) if split == "all" else rows["split"].astype(str).eq(split).to_numpy()
        out.append(
            {
                "dataset": dataset,
                "split": split,
                "model": model,
                **params,
                **metric(y_all[mask], p[mask]),
            }
        )
    return out


def candidate_probability(rows: pd.DataFrame, params: dict[str, Any]) -> np.ndarray:
    base_p = rows["v32_avg110_final60_exact_p_yes"].to_numpy(dtype=float)
    sigma = np.clip(rows["v32_avg110_final60_exact_sigma_t_dollars"].to_numpy(dtype=float), 1e-9, None)
    d_sigma = rows["v32_avg110_final60_exact_d_sigma"].to_numpy(dtype=float)
    base_shift = rows["v34_material_antipersist3_anti_persistence_shift_dollars"].to_numpy(dtype=float)

    shift = base_shift * float(params["shift_scale"])
    anchor_sigma_mult = max(float(params["anchor_sigma_mult"]), 1e-6)
    anchor_z = (-d_sigma + shift / sigma) / anchor_sigma_mult
    anchor = np.clip(normal_cdf(anchor_z), PROB_EPS, 1.0 - PROB_EPS)

    gate_kind = str(params["gate_kind"])
    if gate_kind == "fixed":
        gate = np.ones(len(rows), dtype=float)
    elif gate_kind == "dollar":
        width = max(float(params["gate_width"]), 1e-6)
        gate = sigmoid((np.abs(shift) - float(params["gate_center"])) / width)
    elif gate_kind == "sigma":
        width = max(float(params["gate_width"]), 1e-6)
        shift_sigma = np.abs(shift) / sigma
        gate = sigmoid((shift_sigma - float(params["gate_center"])) / width)
    else:
        raise ValueError(f"Unknown gate_kind={gate_kind}")

    weight = np.clip(float(params["max_weight"]) * gate, 0.0, 1.0)
    ell = (1.0 - weight) * logit(base_p) + weight * logit(anchor)
    temp = max(float(params["posterior_temperature"]), 1e-6)
    return np.clip(sigmoid(ell / temp), PROB_EPS, 1.0 - PROB_EPS)


def candidate_grid() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for shift_scale in [0.50, 0.75, 1.00, 1.25]:
        for max_weight in [0.02, 0.03, 0.05, 0.075]:
            for temp in [0.98, 0.99, 1.00]:
                out.append(
                    {
                        "gate_kind": "fixed",
                        "shift_scale": shift_scale,
                        "anchor_sigma_mult": 1.0,
                        "max_weight": max_weight,
                        "gate_center": 0.0,
                        "gate_width": 1.0,
                        "posterior_temperature": temp,
                    }
                )
    for shift_scale in [0.50, 0.75, 1.00, 1.25]:
        for max_weight in [0.05, 0.075, 0.10, 0.125]:
            for center in [20.0, 40.0, 60.0, 80.0]:
                for width in [5.0, 10.0, 20.0]:
                    for temp in [0.98, 0.99, 1.00]:
                        out.append(
                            {
                                "gate_kind": "dollar",
                                "shift_scale": shift_scale,
                                "anchor_sigma_mult": 1.0,
                                "max_weight": max_weight,
                                "gate_center": center,
                                "gate_width": width,
                                "posterior_temperature": temp,
                            }
                        )
    for shift_scale in [0.50, 0.75, 1.00, 1.25]:
        for anchor_sigma_mult in [0.90, 1.00, 1.10]:
            for max_weight in [0.05, 0.075, 0.10, 0.125]:
                for center in [0.20, 0.30, 0.40, 0.50, 0.65]:
                    for width in [0.05, 0.10, 0.20]:
                        for temp in [0.98, 0.99, 1.00]:
                            out.append(
                                {
                                    "gate_kind": "sigma",
                                    "shift_scale": shift_scale,
                                    "anchor_sigma_mult": anchor_sigma_mult,
                                    "max_weight": max_weight,
                                    "gate_center": center,
                                    "gate_width": width,
                                    "posterior_temperature": temp,
                                }
                            )
    return out


def model_name(params: dict[str, Any]) -> str:
    return (
        f"sweep_{params['gate_kind']}_ss{params['shift_scale']:.2f}"
        f"_asm{params['anchor_sigma_mult']:.2f}_w{params['max_weight']:.3f}"
        f"_c{params['gate_center']:.3f}_gw{params['gate_width']:.3f}_t{params['posterior_temperature']:.2f}"
    )


def add_baseline_rows(frames: dict[str, pd.DataFrame], records: list[dict[str, Any]]) -> None:
    for dataset, rows in frames.items():
        for model in REFERENCE_MODELS:
            col = f"{model}_p_yes"
            if col not in rows.columns:
                continue
            params = {
                "gate_kind": "reference",
                "shift_scale": np.nan,
                "anchor_sigma_mult": np.nan,
                "max_weight": np.nan,
                "gate_center": np.nan,
                "gate_width": np.nan,
                "posterior_temperature": np.nan,
            }
            records.extend(metric_rows(rows, dataset, model, rows[col].to_numpy(dtype=float), params))


def rank_candidates(summary: pd.DataFrame) -> pd.DataFrame:
    base = summary[summary["model"].eq(BASE_MODEL)].set_index(["dataset", "split"])
    candidates = summary[~summary["gate_kind"].eq("reference")].copy()
    rank_records: list[dict[str, Any]] = []
    for model, group in candidates.groupby("model", sort=False):
        first = group.iloc[0]
        rec: dict[str, Any] = {
            "model": model,
            "gate_kind": first["gate_kind"],
            "shift_scale": first["shift_scale"],
            "anchor_sigma_mult": first["anchor_sigma_mult"],
            "max_weight": first["max_weight"],
            "gate_center": first["gate_center"],
            "gate_width": first["gate_width"],
            "posterior_temperature": first["posterior_temperature"],
        }
        for dataset in INPUTS:
            for split in ["train", "validation", "holdout", "all"]:
                row = group[group["dataset"].eq(dataset) & group["split"].eq(split)].iloc[0]
                brier_delta = float(row["brier"] - base.loc[(dataset, split), "brier"])
                logloss_delta = float(row["logloss"] - base.loc[(dataset, split), "logloss"])
                rec[f"{dataset}_{split}_brier"] = float(row["brier"])
                rec[f"{dataset}_{split}_logloss"] = float(row["logloss"])
                rec[f"{dataset}_{split}_brier_delta"] = brier_delta
                rec[f"{dataset}_{split}_logloss_delta"] = logloss_delta
        rec["validation_mean_brier_delta"] = float(
            np.mean([rec["all_heartbeats_validation_brier_delta"], rec["minute_bucket_validation_brier_delta"]])
        )
        rec["validation_mean_logloss_delta"] = float(
            np.mean([rec["all_heartbeats_validation_logloss_delta"], rec["minute_bucket_validation_logloss_delta"]])
        )
        rec["holdout_mean_brier_delta"] = float(
            np.mean([rec["all_heartbeats_holdout_brier_delta"], rec["minute_bucket_holdout_brier_delta"]])
        )
        rec["holdout_mean_logloss_delta"] = float(
            np.mean([rec["all_heartbeats_holdout_logloss_delta"], rec["minute_bucket_holdout_logloss_delta"]])
        )
        rec["all_splits_mean_brier_delta"] = float(
            np.mean(
                [
                    rec[f"{dataset}_{split}_brier_delta"]
                    for dataset in INPUTS
                    for split in ["train", "validation", "holdout"]
                ]
            )
        )
        rec["validation_both_datasets_brier_improved"] = bool(
            rec["all_heartbeats_validation_brier_delta"] < 0
            and rec["minute_bucket_validation_brier_delta"] < 0
        )
        rec["holdout_both_datasets_brier_improved"] = bool(
            rec["all_heartbeats_holdout_brier_delta"] < 0
            and rec["minute_bucket_holdout_brier_delta"] < 0
        )
        rank_records.append(rec)
    return pd.DataFrame(rank_records).sort_values(
        [
            "validation_mean_brier_delta",
            "validation_mean_logloss_delta",
            "holdout_mean_brier_delta",
            "all_splits_mean_brier_delta",
        ],
        ascending=True,
    )


def write_report(summary: pd.DataFrame, rank: pd.DataFrame) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    references = summary[summary["gate_kind"].eq("reference")].copy()
    robust = rank[
        rank["validation_both_datasets_brier_improved"]
        & rank["holdout_both_datasets_brier_improved"]
    ].copy()
    best_validation = rank.iloc[0]
    best_robust = robust.iloc[0] if not robust.empty else best_validation

    lines = [
        "# v35 Anti-Persistence Materiality Sweep",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Pure FV probability-model sweep, not trade scoring.",
        "- Tests whether anti-persistence materiality should be measured in sigma units rather than fixed dollars.",
        "- Primary ranking uses validation splits; holdout is shown as a forward-style check.",
        "- No live bot code/process or orders are touched.",
        "",
        "## Reference Surfaces",
        "",
        "| dataset | split | model | rows | Brier | logloss | side acc | mean p_yes | yes rate |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in references[references["split"].isin(["validation", "holdout"])].iterrows():
        lines.append(
            f"| `{row['dataset']}` | {row['split']} | `{row['model']}` | {int(row['rows'])} | "
            f"{row['brier']:.6f} | {row['logloss']:.6f} | {pct(row['side_accuracy'])} | "
            f"{pct(row['mean_p_yes'])} | {pct(row['yes_rate'])} |"
        )
    lines += [
        "",
        "## Best Validation Candidate",
        "",
        f"- `{best_validation['model']}`",
        f"- kind/shift/anchor/weight/center/width/temp: `{best_validation['gate_kind']}` / "
        f"`{best_validation['shift_scale']}` / `{best_validation['anchor_sigma_mult']}` / "
        f"`{best_validation['max_weight']}` / `{best_validation['gate_center']}` / "
        f"`{best_validation['gate_width']}` / `{best_validation['posterior_temperature']}`",
        f"- validation mean Brier delta vs v32: {best_validation['validation_mean_brier_delta']:+.6f}",
        f"- holdout mean Brier delta vs v32: {best_validation['holdout_mean_brier_delta']:+.6f}",
        "",
        "## Best Robust Candidate",
        "",
        f"- `{best_robust['model']}`",
        f"- validation mean Brier delta vs v32: {best_robust['validation_mean_brier_delta']:+.6f}",
        f"- holdout mean Brier delta vs v32: {best_robust['holdout_mean_brier_delta']:+.6f}",
        "",
        "## Top Validation Rows",
        "",
        "| model | kind | ss | asm | weight | center | width | temp | val dBrier | hold dBrier | val dLogloss | hold dLogloss | hold both? |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for _, row in rank.head(30).iterrows():
        lines.append(
            f"| `{row['model']}` | `{row['gate_kind']}` | {float(row['shift_scale']):.2f} | "
            f"{float(row['anchor_sigma_mult']):.2f} | {float(row['max_weight']):.3f} | "
            f"{float(row['gate_center']):.3f} | {float(row['gate_width']):.3f} | "
            f"{float(row['posterior_temperature']):.2f} | {row['validation_mean_brier_delta']:+.6f} | "
            f"{row['holdout_mean_brier_delta']:+.6f} | {row['validation_mean_logloss_delta']:+.6f} | "
            f"{row['holdout_mean_logloss_delta']:+.6f} | {row['holdout_both_datasets_brier_improved']} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "- A sigma-gated winner supports replacing v34's fixed-dollar materiality prior.",
        "- A dollar-gated or fixed-weight winner means the current v34/v33 family is already close and v35 should not be forced.",
        "- The holdout columns are not used to tune the first ranking; they are the stability check.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "best_validation": best_validation.to_dict(),
                    "best_robust": best_robust.to_dict(),
                    "top_validation": rank.head(50).to_dict("records"),
                }
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    frames = {name: load_opportunities(path) for name, path in INPUTS.items()}
    records: list[dict[str, Any]] = []
    add_baseline_rows(frames, records)
    grid = candidate_grid()
    for params in grid:
        name = model_name(params)
        for dataset, rows in frames.items():
            records.extend(metric_rows(rows, dataset, name, candidate_probability(rows, params), params))
    summary = pd.DataFrame(records)
    rank = rank_candidates(summary)
    summary.to_csv(SUMMARY_CSV, index=False)
    rank.to_csv(RANK_CSV, index=False)
    write_report(summary, rank)
    print("v35 anti-persistence materiality sweep complete")
    print(f"candidates={len(grid)} summary_rows={len(summary)} report={REPORT_MD}")
    print(f"best_validation={rank.iloc[0]['model']} validation_mean_brier_delta={rank.iloc[0]['validation_mean_brier_delta']:+.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
