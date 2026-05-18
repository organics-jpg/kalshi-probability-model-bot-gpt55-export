"""Replay settlement/proxy horizon variants for the FV probability surface.

This is a probability-model probe, not a trade scorer.

The v31->v32 improvement came from questioning the settlement/proxy horizon:
90 seconds was too short for the live Coinbase 1m proxy replay, and 110 seconds
worked better. This probe extends that physics sweep to 120-150 seconds and
tests the same horizons with the v34 anti-persistence prior.

No live bot files/processes are touched and no orders are submitted.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from btc_mushroom_forecaster_v32_fast import FastMushroomFVEngineV32, FastMushroomV32Config
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
REPORT_MD = OUT_DIR / "v35_horizon_antipersistence_sweep_latest.md"
REPORT_JSON = OUT_DIR / "v35_horizon_antipersistence_sweep_latest.json"
SUMMARY_CSV = OUT_DIR / "v35_horizon_antipersistence_sweep_summary_latest.csv"
RANK_CSV = OUT_DIR / "v35_horizon_antipersistence_sweep_rank_latest.csv"

MODES = ["two_side_all_heartbeats", "two_side_minute_bucket"]
HORIZONS = [90.0, 100.0, 110.0, 120.0, 130.0, 140.0, 150.0]
REFERENCE_MODEL = "v34_h110_antipersist"


def make_engines() -> list[EngineSpec]:
    engines: list[EngineSpec] = []
    for seconds in HORIZONS:
        tag = int(seconds)
        engines.append(
            EngineSpec(
                f"v32_h{tag}_settle",
                FastMushroomFVEngineV32(
                    FastMushroomV32Config(settlement_average_seconds=seconds, exact_average_inside_seconds=60.0)
                ),
                f"v32 settlement/proxy horizon {tag}s with exact final-60s collapse",
            )
        )
        engines.append(
            EngineSpec(
                f"v34_h{tag}_antipersist",
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
                        posterior_temperature=0.98,
                    )
                ),
                f"v34 anti-persistence with settlement/proxy horizon {tag}s",
            )
        )
    return engines


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
        "family": "v34_antipersist" if model.startswith("v34") else "v32_settle",
        "side_rows": int(np.isfinite(p).sum()),
        "opportunities": int(total),
        "brier": brier(y, p),
        "logloss": logloss(y, p),
        "ece10": ece(y, p),
        "side_choice_wins": int(wins),
        "side_choice_accuracy": acc,
    }


def horizon_from_model(model: str) -> int:
    marker = "_h"
    if marker not in model:
        return -1
    rest = model.split(marker, 1)[1]
    return int(rest.split("_", 1)[0])


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
            "horizon_seconds": int(first["horizon_seconds"]),
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
        records.append(rec)
    return pd.DataFrame(records).sort_values(
        [
            "validation_mean_brier_delta_ref",
            "validation_mean_logloss_delta_ref",
            "holdout_mean_brier_delta_ref",
            "holdout_mean_logloss_delta_ref",
        ],
        ascending=True,
    )


def write_report(summary: pd.DataFrame, rank: pd.DataFrame) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    best_validation = rank.iloc[0]
    robust = rank[rank["beats_ref_all_validation_holdout_brier"]].copy()
    best_robust = robust.iloc[0] if not robust.empty else None

    lines = [
        "# v35 Horizon/Anti-Persistence Sweep",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Pure FV probability-model replay, not trade scoring.",
        "- Tests settlement/proxy horizons from 90s to 150s with and without v34 anti-persistence.",
        "- Reference is current research best `v34_h110_antipersist`.",
        "- No live bot code/process or orders are touched.",
        "",
        "## Split Metrics",
        "",
        "| mode | split | model | family | horizon | Brier | logloss | ECE10 | side acc |",
        "|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    show = summary[summary["split"].isin(["validation", "holdout"])].copy()
    for _, row in show.sort_values(["mode", "split", "brier"]).iterrows():
        lines.append(
            f"| `{row['mode']}` | {row['split']} | `{row['model']}` | `{row['family']}` | "
            f"{int(row['horizon_seconds'])} | {row['brier']:.6f} | {row['logloss']:.6f} | "
            f"{row['ece10']:.6f} | {pct(row['side_choice_accuracy'])} |"
        )
    lines += [
        "",
        "## Ranked Versus v34_h110",
        "",
        "| model | family | horizon | val dBrier | hold dBrier | val dLogloss | hold dLogloss | beats all val+hold? |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for _, row in rank.iterrows():
        lines.append(
            f"| `{row['model']}` | `{row['family']}` | {int(row['horizon_seconds'])} | "
            f"{row['validation_mean_brier_delta_ref']:+.6f} | {row['holdout_mean_brier_delta_ref']:+.6f} | "
            f"{row['validation_mean_logloss_delta_ref']:+.6f} | {row['holdout_mean_logloss_delta_ref']:+.6f} | "
            f"{row['beats_ref_all_validation_holdout_brier']} |"
        )
    lines += [
        "",
        "## Read",
        "",
        f"- Best validation candidate: `{best_validation['model']}`.",
    ]
    if best_robust is not None:
        lines.append(f"- Robust candidate beating current v34 on every validation/holdout Brier cell: `{best_robust['model']}`.")
    else:
        lines.append("- No horizon candidate beats current v34 on every validation/holdout Brier cell.")
    lines.append("- If longer horizons only improve validation while weakening holdout, keep v34 at 110s and do not promote a horizon change.")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "best_validation": best_validation.to_dict(),
                    "best_robust": None if best_robust is None else best_robust.to_dict(),
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
    print("v35 horizon anti-persistence sweep complete")
    print(f"summary_rows={len(summary)} report={REPORT_MD}")
    print(
        "best_validation="
        f"{rank.iloc[0]['model']} validation_mean_brier_delta_ref={rank.iloc[0]['validation_mean_brier_delta_ref']:+.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
