"""Refine v34 settlement/proxy horizon with posterior temperature.

This is a pure FV probability probe, not a trade scorer.

The horizon sweep found that longer v34 horizons improve Brier but worsen
logloss, which is a classic sign of useful direction with too much posterior
sharpness. This probe keeps the same physics and tests whether a softer
temperature makes the longer-horizon prior stable.

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
REPORT_MD = OUT_DIR / "v35_horizon_temperature_refine_latest.md"
REPORT_JSON = OUT_DIR / "v35_horizon_temperature_refine_latest.json"
SUMMARY_CSV = OUT_DIR / "v35_horizon_temperature_refine_summary_latest.csv"
RANK_CSV = OUT_DIR / "v35_horizon_temperature_refine_rank_latest.csv"

MODES = ["two_side_all_heartbeats", "two_side_minute_bucket"]
HORIZONS = [110.0, 120.0, 130.0, 140.0, 150.0]
TEMPERATURES = [0.98, 1.00, 1.02]
REFERENCE_MODEL = "v34_h110_t098"


def make_engines() -> list[EngineSpec]:
    engines: list[EngineSpec] = []
    for seconds in HORIZONS:
        for temp in TEMPERATURES:
            h_tag = int(seconds)
            t_tag = int(round(temp * 100))
            engines.append(
                EngineSpec(
                    f"v34_h{h_tag}_t{t_tag:03d}",
                    FastMushroomFVEngineV34(
                        FastMushroomV34Config(
                            settlement_average_seconds=seconds,
                            exact_average_inside_seconds=60.0,
                            anti_persistence_lag_minutes=3,
                            anti_persistence_velocity_weight=-0.50,
                            anti_persistence_time_damp_power=2.0,
                            anti_persistence_sigma_mult=1.00,
                            anti_persistence_max_logit_weight=0.10,
                            anti_persistence_shift_gate_center_dollars=40.0,
                            anti_persistence_shift_gate_width_dollars=5.0,
                            posterior_temperature=temp,
                        )
                    ),
                    f"v34 anti-persistence, {h_tag}s settlement/proxy horizon, posterior temperature {temp:.2f}",
                )
            )
    return engines


def horizon_from_model(model: str) -> int:
    return int(model.split("_h", 1)[1].split("_", 1)[0])


def temperature_from_model(model: str) -> float:
    return int(model.split("_t", 1)[1]) / 100.0


def metric_row(rows: pd.DataFrame, model: str, split: str, mode: str) -> dict[str, Any]:
    part = rows if split == "all" else rows[rows["split"].astype(str).eq(split)]
    y = part["win"].astype(bool).astype(float).to_numpy()
    p = pd.to_numeric(part[f"{model}_p_side"], errors="coerce").to_numpy(dtype=float)
    wins, total, acc = side_choice_accuracy(part, model)
    return {
        "mode": mode,
        "split": split,
        "model": model,
        "horizon_seconds": horizon_from_model(model),
        "posterior_temperature": temperature_from_model(model),
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
            "horizon_seconds": int(first["horizon_seconds"]),
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
        rec["validation_mean_logloss_delta_ref"] = float(
            np.mean([rec[f"{mode}_validation_logloss_delta_ref"] for mode in MODES])
        )
        rec["holdout_mean_logloss_delta_ref"] = float(
            np.mean([rec[f"{mode}_holdout_logloss_delta_ref"] for mode in MODES])
        )
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
            "validation_mean_logloss_delta_ref",
            "holdout_mean_logloss_delta_ref",
        ],
        ascending=True,
    )


def write_report(summary: pd.DataFrame, rank: pd.DataFrame) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    best_validation = rank.iloc[0]
    robust_brier = rank[rank["beats_ref_all_validation_holdout_brier"]].copy()
    robust_both = robust_brier[robust_brier["beats_ref_all_validation_holdout_logloss"]].copy()

    lines = [
        "# v35 Horizon/Temperature Refine",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Pure FV probability-model replay, not trade scoring.",
        "- Tests whether longer v34 settlement/proxy horizons need a softer posterior temperature.",
        "- Reference is current research best `v34_h110_t098`.",
        "- No live bot code/process or orders are touched.",
        "",
        "## Ranked Versus v34_h110_t098",
        "",
        "| model | horizon | temp | val dBrier | hold dBrier | val dLogloss | hold dLogloss | all Brier cells? | all logloss cells? |",
        "|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for _, row in rank.iterrows():
        lines.append(
            f"| `{row['model']}` | {int(row['horizon_seconds'])} | {row['posterior_temperature']:.2f} | "
            f"{row['validation_mean_brier_delta_ref']:+.6f} | {row['holdout_mean_brier_delta_ref']:+.6f} | "
            f"{row['validation_mean_logloss_delta_ref']:+.6f} | {row['holdout_mean_logloss_delta_ref']:+.6f} | "
            f"{row['beats_ref_all_validation_holdout_brier']} | {row['beats_ref_all_validation_holdout_logloss']} |"
        )
    lines += [
        "",
        "## Split Metrics",
        "",
        "| mode | split | model | horizon | temp | Brier | logloss | ECE10 | side acc |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary[summary["split"].isin(["validation", "holdout"])].sort_values(["mode", "split", "brier"]).iterrows():
        lines.append(
            f"| `{row['mode']}` | {row['split']} | `{row['model']}` | {int(row['horizon_seconds'])} | "
            f"{row['posterior_temperature']:.2f} | {row['brier']:.6f} | {row['logloss']:.6f} | "
            f"{row['ece10']:.6f} | {pct(row['side_choice_accuracy'])} |"
        )
    lines += [
        "",
        "## Read",
        "",
        f"- Best validation candidate: `{best_validation['model']}`.",
        f"- Candidates beating the reference on every validation/holdout Brier cell: {len(robust_brier)}.",
        f"- Candidates beating the reference on every validation/holdout Brier and logloss cell: {len(robust_both)}.",
        "- If the Brier gain requires worse logloss, treat it as sharper but less trustworthy probability, not a promotion-ready FV model.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "best_validation": best_validation.to_dict(),
                    "robust_brier": robust_brier.to_dict("records"),
                    "robust_brier_and_logloss": robust_both.to_dict("records"),
                    "rank": rank.to_dict("records"),
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
    print("v35 horizon temperature refine complete")
    print(f"summary_rows={len(summary)} report={REPORT_MD}")
    print(
        "best_validation="
        f"{rank.iloc[0]['model']} validation_mean_brier_delta_ref={rank.iloc[0]['validation_mean_brier_delta_ref']:+.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
