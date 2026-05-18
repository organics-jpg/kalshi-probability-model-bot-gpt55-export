"""Sweep v36 piecewise proxy-horizon FV candidates.

This is a pure FV probability replay, not a trade scorer.

v35 improved recent validation/holdout but damaged older short-time-to-close
blocks. This probe tests whether keeping v34's 110s proxy horizon near expiry
and blending toward v35's 150s horizon earlier in the market preserves the
recent gain without the short-window damage.

No live bot files/processes are touched and no orders are submitted.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from btc_mushroom_forecaster_v34_fast import FastMushroomFVEngineV34, FastMushroomV34Config
from btc_mushroom_forecaster_v35_fast import FastMushroomFVEngineV35, FastMushroomV35Config
from btc_mushroom_forecaster_v36_fast import FastMushroomFVEngineV36, FastMushroomV36Config
from probe_market_interval_80coverage import clean_json, pct
from probe_mushroom_v29_fv_surface import (
    EngineSpec,
    brier,
    ece,
    load_candles,
    load_ledger,
    logloss,
    market_splits,
    replay_predictions,
    side_choice_accuracy,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v36_piecewise_horizon_sweep_latest.md"
REPORT_JSON = OUT_DIR / "v36_piecewise_horizon_sweep_latest.json"
SUMMARY_CSV = OUT_DIR / "v36_piecewise_horizon_sweep_summary_latest.csv"
RANK_CSV = OUT_DIR / "v36_piecewise_horizon_sweep_rank_latest.csv"

MODES = ["two_side_all_heartbeats", "two_side_minute_bucket"]
REFERENCE_MODEL = "v34_h110_t098"
V35_MODEL = "v35_h150_t102"
BLENDS = [(120.0, 300.0), (180.0, 450.0), (180.0, 600.0), (300.0, 600.0), (300.0, 900.0)]
TEMPERATURES = [1.00, 1.02, 1.04]


def make_engines() -> list[EngineSpec]:
    engines: list[EngineSpec] = [
        EngineSpec(
            REFERENCE_MODEL,
            FastMushroomFVEngineV34(
                FastMushroomV34Config(
                    settlement_average_seconds=110.0,
                    exact_average_inside_seconds=60.0,
                    anti_persistence_lag_minutes=3,
                    anti_persistence_velocity_weight=-0.50,
                    anti_persistence_time_damp_power=2.0,
                    anti_persistence_sigma_mult=1.00,
                    anti_persistence_max_logit_weight=0.10,
                    anti_persistence_shift_gate_center_dollars=40.0,
                    anti_persistence_shift_gate_width_dollars=5.0,
                    posterior_temperature=0.98,
                )
            ),
            "v34 reference: 110s proxy horizon, 0.98 temperature",
        ),
        EngineSpec(
            V35_MODEL,
            FastMushroomFVEngineV35(FastMushroomV35Config()),
            "v35 reference: 150s proxy horizon, 1.02 temperature",
        ),
    ]
    for start, end in BLENDS:
        for temp in TEMPERATURES:
            name = f"v36_s{int(start)}_e{int(end)}_t{int(round(temp * 100)):03d}"
            engines.append(
                EngineSpec(
                    name,
                    FastMushroomFVEngineV36(
                        FastMushroomV36Config(
                            short_settlement_average_seconds=110.0,
                            long_settlement_average_seconds=150.0,
                            proxy_blend_start_seconds=start,
                            proxy_blend_end_seconds=end,
                            posterior_temperature=temp,
                        )
                    ),
                    f"v36 piecewise proxy horizon, blend {int(start)}-{int(end)}s, temperature {temp:.2f}",
                )
            )
    return engines


def params_from_model(model: str) -> dict[str, Any]:
    if model == REFERENCE_MODEL:
        return {"family": "v34_ref", "blend_start_seconds": 0, "blend_end_seconds": 0, "posterior_temperature": 0.98}
    if model == V35_MODEL:
        return {"family": "v35_ref", "blend_start_seconds": 0, "blend_end_seconds": 0, "posterior_temperature": 1.02}
    parts = model.split("_")
    return {
        "family": "v36_piecewise",
        "blend_start_seconds": int(parts[1][1:]),
        "blend_end_seconds": int(parts[2][1:]),
        "posterior_temperature": int(parts[3][1:]) / 100.0,
    }


def metric_row(rows: pd.DataFrame, model: str, split: str, mode: str) -> dict[str, Any]:
    part = rows if split == "all" else rows[rows["split"].astype(str).eq(split)]
    y = part["win"].astype(bool).astype(float).to_numpy()
    p = pd.to_numeric(part[f"{model}_p_side"], errors="coerce").to_numpy(dtype=float)
    wins, total, acc = side_choice_accuracy(part, model)
    return {
        "mode": mode,
        "split": split,
        "model": model,
        **params_from_model(model),
        "side_rows": int(np.isfinite(p).sum()),
        "opportunities": int(total),
        "brier": brier(y, p),
        "logloss": logloss(y, p),
        "ece10": ece(y, p),
        "side_choice_wins": int(wins),
        "side_choice_accuracy": acc,
    }


def build_summary() -> pd.DataFrame:
    candles = load_candles()
    records: list[dict[str, Any]] = []
    for mode in MODES:
        ledger = load_ledger(mode)
        engines = make_engines()
        rows = replay_predictions(ledger, candles, engines)
        splits = market_splits(rows)
        rows = rows.merge(splits[["market", "split"]], on="market", how="left")
        for spec in engines:
            for split in ["all", "train", "validation", "holdout"]:
                records.append(metric_row(rows, spec.name, split, mode))
    return pd.DataFrame(records)


def rank_summary(summary: pd.DataFrame) -> pd.DataFrame:
    ref = summary[summary["model"].eq(REFERENCE_MODEL)].set_index(["mode", "split"])
    records: list[dict[str, Any]] = []
    for model, group in summary.groupby("model"):
        first = group.iloc[0]
        rec: dict[str, Any] = {
            "model": model,
            "family": first["family"],
            "blend_start_seconds": int(first["blend_start_seconds"]),
            "blend_end_seconds": int(first["blend_end_seconds"]),
            "posterior_temperature": float(first["posterior_temperature"]),
        }
        for mode in MODES:
            for split in ["train", "validation", "holdout", "all"]:
                row = group[group["mode"].eq(mode) & group["split"].eq(split)].iloc[0]
                rec[f"{mode}_{split}_brier"] = float(row["brier"])
                rec[f"{mode}_{split}_logloss"] = float(row["logloss"])
                rec[f"{mode}_{split}_brier_delta_ref"] = float(row["brier"] - ref.loc[(mode, split), "brier"])
                rec[f"{mode}_{split}_logloss_delta_ref"] = float(row["logloss"] - ref.loc[(mode, split), "logloss"])
        rec["validation_mean_brier_delta_ref"] = float(
            np.mean([rec[f"{mode}_validation_brier_delta_ref"] for mode in MODES])
        )
        rec["holdout_mean_brier_delta_ref"] = float(
            np.mean([rec[f"{mode}_holdout_brier_delta_ref"] for mode in MODES])
        )
        rec["train_mean_brier_delta_ref"] = float(np.mean([rec[f"{mode}_train_brier_delta_ref"] for mode in MODES]))
        rec["validation_mean_logloss_delta_ref"] = float(
            np.mean([rec[f"{mode}_validation_logloss_delta_ref"] for mode in MODES])
        )
        rec["holdout_mean_logloss_delta_ref"] = float(
            np.mean([rec[f"{mode}_holdout_logloss_delta_ref"] for mode in MODES])
        )
        rec["train_mean_logloss_delta_ref"] = float(np.mean([rec[f"{mode}_train_logloss_delta_ref"] for mode in MODES]))
        rec["beats_ref_all_validation_holdout_brier"] = bool(
            all(rec[f"{mode}_{split}_brier_delta_ref"] < 0 for mode in MODES for split in ["validation", "holdout"])
        )
        rec["beats_ref_all_validation_holdout_logloss"] = bool(
            all(rec[f"{mode}_{split}_logloss_delta_ref"] < 0 for mode in MODES for split in ["validation", "holdout"])
        )
        records.append(rec)
    return pd.DataFrame(records).sort_values(
        [
            "validation_mean_brier_delta_ref",
            "holdout_mean_brier_delta_ref",
            "train_mean_brier_delta_ref",
            "validation_mean_logloss_delta_ref",
        ],
        ascending=True,
    )


def write_report(summary: pd.DataFrame, rank: pd.DataFrame) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    robust = rank[
        rank["beats_ref_all_validation_holdout_brier"] & rank["beats_ref_all_validation_holdout_logloss"]
    ].copy()
    lines = [
        "# v36 Piecewise Horizon Sweep",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Pure FV probability-model replay, not trade scoring.",
        "- Tests keeping v34's proxy horizon near expiry while blending toward v35 earlier.",
        "- Reference is current v34; v35 is included as a comparison.",
        "- No live bot code/process or orders are touched.",
        "",
        "## Ranked Versus v34",
        "",
        "| model | family | start | end | temp | train dBrier | val dBrier | hold dBrier | val dLogloss | hold dLogloss | all val+hold Brier+LL? |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for _, row in rank.iterrows():
        lines.append(
            f"| `{row['model']}` | `{row['family']}` | {int(row['blend_start_seconds'])} | "
            f"{int(row['blend_end_seconds'])} | {row['posterior_temperature']:.2f} | "
            f"{row['train_mean_brier_delta_ref']:+.6f} | {row['validation_mean_brier_delta_ref']:+.6f} | "
            f"{row['holdout_mean_brier_delta_ref']:+.6f} | {row['validation_mean_logloss_delta_ref']:+.6f} | "
            f"{row['holdout_mean_logloss_delta_ref']:+.6f} | "
            f"{row['beats_ref_all_validation_holdout_brier'] and row['beats_ref_all_validation_holdout_logloss']} |"
        )
    lines += [
        "",
        "## Split Metrics",
        "",
        "| mode | split | model | Brier | logloss | ECE10 | side acc |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for _, row in summary[summary["split"].isin(["validation", "holdout"])].sort_values(["mode", "split", "brier"]).iterrows():
        lines.append(
            f"| `{row['mode']}` | {row['split']} | `{row['model']}` | {row['brier']:.6f} | "
            f"{row['logloss']:.6f} | {row['ece10']:.6f} | {pct(row['side_choice_accuracy'])} |"
        )
    lines += [
        "",
        "## Read",
        "",
        f"- Best validation row: `{rank.iloc[0]['model']}`.",
        f"- Candidates beating v34 on every validation/holdout Brier and logloss cell: {len(robust)}.",
        "- If no piecewise row improves train damage while preserving recent-split gains, keep v35 only as a forward-shadow candidate.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "rank": rank.to_dict("records"),
                    "robust": robust.to_dict("records"),
                }
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    summary = build_summary()
    rank = rank_summary(summary)
    summary.to_csv(SUMMARY_CSV, index=False)
    rank.to_csv(RANK_CSV, index=False)
    write_report(summary, rank)
    print("v36 piecewise horizon sweep complete")
    print(f"summary_rows={len(summary)} report={REPORT_MD}")
    print(f"best_validation={rank.iloc[0]['model']} validation_mean_brier_delta_ref={rank.iloc[0]['validation_mean_brier_delta_ref']:+.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
