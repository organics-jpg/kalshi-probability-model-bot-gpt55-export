"""Replay v28/v29 FV probability surfaces on resolved BTC 15m heartbeat states.

This is a model-quality probe, not a trade scorer. It feeds historical Coinbase
1m candles into candidate FV engines exactly as the live worker would, asks for
P(YES) at each resolved heartbeat opportunity, and compares probability
calibration against the eventual market outcome.

Primary metrics are Brier score, logloss, and expected calibration error. A
side-choice accuracy line is included only as a sanity check.

Research-only: no orders are submitted, no live bot files are imported, and no
running process is touched.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from btc_mushroom_forecaster_v28_fast import FastMushroomFVEngineV28, FastMushroomV28Config
from btc_mushroom_forecaster_v29_fast import FastMushroomFVEngineV29, FastMushroomV29Config
from btc_mushroom_forecaster_v30_fast import FastMushroomFVEngineV30, FastMushroomV30Config
from btc_mushroom_forecaster_v31_fast import FastMushroomFVEngineV31, FastMushroomV31Config
from btc_mushroom_forecaster_v32_fast import FastMushroomFVEngineV32, FastMushroomV32Config
from btc_mushroom_forecaster_v33_fast import FastMushroomFVEngineV33, FastMushroomV33Config
from btc_mushroom_forecaster_v34_fast import FastMushroomFVEngineV34, FastMushroomV34Config
from btc_mushroom_forecaster_v35_fast import FastMushroomFVEngineV35, FastMushroomV35Config
from btc_mushroom_forecaster_v36_fast import FastMushroomFVEngineV36, FastMushroomV36Config
from btc_mushroom_forecaster_v37_fast import FastMushroomFVEngineV37, FastMushroomV37Config
from btc_mushroom_forecaster_v38_fast import FastMushroomFVEngineV38, FastMushroomV38Config
from btc_mushroom_forecaster_v39_fast import FastMushroomFVEngineV39, FastMushroomV39Config
from probe_market_interval_80coverage import clean_json, pct


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
LEDGER_PATH = OUT_DIR / "live_heartbeat_two_side_fv_ledger_latest.csv"
CANDLE_PATH = OUT_DIR / "coinbase_btc_usd_1m_cache.parquet"

REPORT_MD = OUT_DIR / "mushroom_v29_fv_surface_latest.md"
REPORT_JSON = OUT_DIR / "mushroom_v29_fv_surface_latest.json"
SUMMARY_CSV = OUT_DIR / "mushroom_v29_fv_surface_summary_latest.csv"
CALIBRATION_CSV = OUT_DIR / "mushroom_v29_fv_surface_calibration_latest.csv"
PREDICTIONS_CSV = OUT_DIR / "mushroom_v29_fv_surface_predictions_latest.csv"

DEFAULT_MODE = "two_side_minute_bucket"
PROB_EPS = 1e-6
CALIBRATION_BINS = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.975, 1.000001]


@dataclass
class EngineSpec:
    name: str
    engine: Any
    thesis: str


def make_engines() -> list[EngineSpec]:
    return [
        EngineSpec(
            "v28_live_surface",
            FastMushroomFVEngineV28(FastMushroomV28Config()),
            "current v28 FV surface: Brownian anchor plus symmetric transport, close-to-close horizon",
        ),
        EngineSpec(
            "v28_avg60",
            FastMushroomFVEngineV28(FastMushroomV28Config(settlement_average_seconds=60.0)),
            "v28 with final-minute settlement-average horizon adjustment",
        ),
        EngineSpec(
            "v28_avg30",
            FastMushroomFVEngineV28(FastMushroomV28Config(settlement_average_seconds=30.0)),
            "v28 settlement-average sensitivity with a 30-second averaging window",
        ),
        EngineSpec(
            "v28_avg45",
            FastMushroomFVEngineV28(FastMushroomV28Config(settlement_average_seconds=45.0)),
            "v28 settlement-average sensitivity with a 45-second averaging window",
        ),
        EngineSpec(
            "v28_avg75",
            FastMushroomFVEngineV28(FastMushroomV28Config(settlement_average_seconds=75.0)),
            "v28 settlement-average sensitivity with a 75-second averaging window",
        ),
        EngineSpec(
            "v28_avg90",
            FastMushroomFVEngineV28(FastMushroomV28Config(settlement_average_seconds=90.0)),
            "v28 settlement-average sensitivity with a 90-second averaging window",
        ),
        EngineSpec(
            "v30_avg60_exact_var",
            FastMushroomFVEngineV30(FastMushroomV30Config(settlement_average_seconds=60.0)),
            "v30 exact Brownian variance inside a 60-second settlement-average window",
        ),
        EngineSpec(
            "v30_avg75_exact_var",
            FastMushroomFVEngineV30(FastMushroomV30Config(settlement_average_seconds=75.0)),
            "v30 exact Brownian variance inside a 75-second settlement-average window",
        ),
        EngineSpec(
            "v30_avg90_exact_var",
            FastMushroomFVEngineV30(FastMushroomV30Config(settlement_average_seconds=90.0)),
            "v30 exact Brownian variance inside a 90-second settlement-average window",
        ),
        EngineSpec(
            "v31_avg90_final60_exact",
            FastMushroomFVEngineV31(
                FastMushroomV31Config(settlement_average_seconds=90.0, exact_average_inside_seconds=60.0)
            ),
            "v31 proxy-aware surface: 90s effective settlement horizon, exact average collapse in final 60s",
        ),
        EngineSpec(
            "v32_avg110_final60_exact",
            FastMushroomFVEngineV32(
                FastMushroomV32Config(settlement_average_seconds=110.0, exact_average_inside_seconds=60.0)
            ),
            "v32 proxy-aware surface: 110s effective settlement/proxy horizon, exact average collapse in final 60s",
        ),
        EngineSpec(
            "v33_antipersist3",
            FastMushroomFVEngineV33(
                FastMushroomV33Config(
                    settlement_average_seconds=110.0,
                    exact_average_inside_seconds=60.0,
                    anti_persistence_lag_minutes=3,
                    anti_persistence_velocity_weight=-0.50,
                    anti_persistence_time_damp_power=2.0,
                    anti_persistence_sigma_mult=1.00,
                    anti_persistence_logit_weight=0.05,
                    posterior_temperature=0.98,
                )
            ),
            "v33: v32 plus a small time-damped 3m anti-persistence Brownian anchor",
        ),
        EngineSpec(
            "v34_material_antipersist3",
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
            "v34: v32 plus materiality-gated 3m anti-persistence",
        ),
        EngineSpec(
            "v35_h150_t102_antipersist3",
            FastMushroomFVEngineV35(
                FastMushroomV35Config(
                    settlement_average_seconds=150.0,
                    exact_average_inside_seconds=60.0,
                    anti_persistence_lag_minutes=3,
                    anti_persistence_velocity_weight=-0.50,
                    anti_persistence_time_damp_power=2.0,
                    anti_persistence_sigma_mult=1.00,
                    anti_persistence_max_logit_weight=0.10,
                    anti_persistence_shift_gate_center_dollars=40.0,
                    anti_persistence_shift_gate_width_dollars=5.0,
                    posterior_temperature=1.02,
                )
            ),
            "v35: v34 path prior with 150s proxy horizon and softer 1.02 posterior temperature",
        ),
        EngineSpec(
            "v36_piecewise_h150_t102_antipersist3",
            FastMushroomFVEngineV36(FastMushroomV36Config()),
            "v36: v34 near expiry, smooth 120-300s blend to v35 proxy horizon, 1.02 temperature",
        ),
        EngineSpec(
            "v37_piecewise_dynamic_temp_antipersist3",
            FastMushroomFVEngineV37(FastMushroomV37Config()),
            "v37: v36 proxy blend plus dynamic 0.98-to-1.02 posterior temperature",
        ),
        EngineSpec(
            "v38_long60_antipersist",
            FastMushroomFVEngineV38(FastMushroomV38Config()),
            "v38: v37 plus a gated 60m long-memory anti-persistence anchor",
        ),
        EngineSpec(
            "v39_midband_v28_fallback",
            FastMushroomFVEngineV39(FastMushroomV39Config()),
            "v39: v38 except live-v28 FV fallback in the 420-600s mid-market band",
        ),
        EngineSpec(
            "v28_avg60_temp104",
            FastMushroomFVEngineV28(
                FastMushroomV28Config(settlement_average_seconds=60.0, transport_temperature=1.04)
            ),
            "settlement-average horizon plus softer probability temperature",
        ),
        EngineSpec(
            "v29_signed_small",
            FastMushroomFVEngineV29(
                FastMushroomV29Config(signed_transport_recent_weight=0.05, signed_transport_long_weight=0.02)
            ),
            "v29 final-average physics with a very small gated signed-transport term",
        ),
        EngineSpec(
            "v29_signed_default",
            FastMushroomFVEngineV29(FastMushroomV29Config()),
            "v29 final-average physics with small gated signed transport and volshock temperature shrinkage",
        ),
        EngineSpec(
            "v29_signed_more",
            FastMushroomFVEngineV29(
                FastMushroomV29Config(signed_transport_recent_weight=0.16, signed_transport_long_weight=0.06)
            ),
            "v29 sensitivity with larger signed-regime transport",
        ),
        EngineSpec(
            "v29_no_signed_temp112",
            FastMushroomFVEngineV29(
                FastMushroomV29Config(
                    transport_temperature=1.12,
                    signed_transport_recent_weight=0.0,
                    signed_transport_long_weight=0.0,
                )
            ),
            "final-average horizon with stronger global overconfidence shrinkage and no signed transport",
        ),
    ]


def bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def load_ledger(mode: str) -> pd.DataFrame:
    if not LEDGER_PATH.exists():
        raise SystemExit(f"Missing heartbeat ledger: {LEDGER_PATH}. Run probe_live_heartbeat_two_side_fv.py first.")
    rows = pd.read_csv(LEDGER_PATH, low_memory=False)
    rows = rows[rows["two_side_mode"].astype(str).eq(mode)].copy()
    if rows.empty:
        raise SystemExit(f"No rows for mode={mode} in {LEDGER_PATH}")
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    rows["win"] = bool_series(rows["win"])
    rows["outcome_available"] = bool_series(rows["outcome_available"])
    for col in ["strike", "seconds_to_close", "ask_cents", "book_p_side"]:
        rows[col] = pd.to_numeric(rows.get(col), errors="coerce")
    rows = rows[
        rows["outcome_available"]
        & rows["entry_dt"].notna()
        & rows["market"].notna()
        & rows["side"].isin(["yes", "no"])
        & rows["strike"].notna()
        & rows["seconds_to_close"].gt(0)
    ].copy()
    if rows.empty:
        raise SystemExit("No resolved usable heartbeat rows after filtering.")
    return rows.sort_values(["entry_dt", "opportunity_key", "side"]).reset_index(drop=True)


def load_candles() -> pd.DataFrame:
    if not CANDLE_PATH.exists():
        raise SystemExit(f"Missing Coinbase candle cache: {CANDLE_PATH}")
    candles = pd.read_parquet(CANDLE_PATH)
    for col in ["open_dt", "close_dt"]:
        candles[col] = pd.to_datetime(candles[col], utc=True, errors="coerce")
    for col in ["open", "high", "low", "close", "volume"]:
        candles[col] = pd.to_numeric(candles[col], errors="coerce")
    candles = candles.dropna(subset=["close_dt", "open", "high", "low", "close"]).copy()
    candles = candles.drop_duplicates("close_dt", keep="last")
    return candles.sort_values("close_dt").reset_index(drop=True)


def market_splits(rows: pd.DataFrame) -> pd.DataFrame:
    base = rows.copy()
    base["close_dt"] = base["entry_dt"] + pd.to_timedelta(base["seconds_to_close"], unit="s")
    markets = (
        base.groupby("market", as_index=False, sort=False)
        .agg(first_entry_dt=("entry_dt", "min"), close_dt=("close_dt", "max"), outcome=("outcome", "first"))
        .sort_values(["close_dt", "market"])
        .reset_index(drop=True)
    )
    n = len(markets)
    train_end = int(math.floor(n * 0.60))
    validation_end = int(math.floor(n * 0.80))
    split = np.full(n, "holdout", dtype=object)
    split[:train_end] = "train"
    split[train_end:validation_end] = "validation"
    markets["split"] = split
    return markets


def opportunity_frame(rows: pd.DataFrame) -> pd.DataFrame:
    first = (
        rows.sort_values(["entry_dt", "opportunity_key", "side"])
        .groupby("opportunity_key", as_index=False, sort=False)
        .first()
    )
    return first[["opportunity_key", "entry_dt", "market", "strike", "seconds_to_close"]].sort_values("entry_dt")


def replay_predictions(rows: pd.DataFrame, candles: pd.DataFrame, engines: list[EngineSpec]) -> pd.DataFrame:
    opportunities = opportunity_frame(rows)
    min_entry = opportunities["entry_dt"].min()
    max_entry = opportunities["entry_dt"].max()
    candles = candles[candles["close_dt"].le(max_entry)].copy()
    if candles.empty:
        raise SystemExit("No candles at or before heartbeat opportunities.")

    predictions: list[dict[str, Any]] = []
    candle_idx = 0
    for _, opp in opportunities.iterrows():
        entry_dt = pd.Timestamp(opp["entry_dt"])
        while candle_idx < len(candles) and pd.Timestamp(candles.iloc[candle_idx]["close_dt"]) <= entry_dt:
            candle = candles.iloc[candle_idx]
            for spec in engines:
                spec.engine.update_bar(
                    open=float(candle["open"]),
                    high=float(candle["high"]),
                    low=float(candle["low"]),
                    close=float(candle["close"]),
                    volume=float(candle.get("volume") or 0.0),
                    ts=pd.Timestamp(candle["close_dt"]).to_pydatetime(),
                )
            candle_idx += 1

        row: dict[str, Any] = {
            "opportunity_key": opp["opportunity_key"],
            "entry_dt": entry_dt.isoformat(),
            "market": opp["market"],
            "strike": float(opp["strike"]),
            "seconds_to_close": float(opp["seconds_to_close"]),
        }
        for spec in engines:
            if not spec.engine.ready():
                row[f"{spec.name}_p_yes"] = np.nan
                continue
            try:
                pred = spec.engine.predict_many(
                    strikes=np.asarray([float(opp["strike"])], dtype=float),
                    horizon_seconds=float(opp["seconds_to_close"]),
                )
            except Exception:
                row[f"{spec.name}_p_yes"] = np.nan
                continue
            row[f"{spec.name}_p_yes"] = float(pred.p_yes[0])
            row[f"{spec.name}_sigma_t_dollars"] = float(pred.sigma_t_dollars)
            row[f"{spec.name}_d_sigma"] = float(pred.d_sigma[0])
            if spec.name.startswith(("v29", "v30", "v31", "v32", "v33", "v34", "v35", "v36", "v37", "v38", "v39")):
                row[f"{spec.name}_effective_horizon_minutes"] = float(pred.components.get("effective_horizon_minutes", np.nan))
                if spec.name.startswith("v29"):
                    row[f"{spec.name}_effective_temperature"] = float(pred.components.get("effective_temperature", np.nan))
                    row[f"{spec.name}_signed_pressure_gate"] = float(pred.components.get("signed_pressure_gate", np.nan))
                if spec.name.startswith(("v33", "v34", "v35", "v36", "v37", "v38", "v39")):
                    row[f"{spec.name}_anti_persistence_shift_dollars"] = float(
                        pred.components.get("anti_persistence_shift_dollars", np.nan)
                    )
                    row[f"{spec.name}_anti_persistence_time_damp"] = float(
                        pred.components.get("anti_persistence_time_damp", np.nan)
                    )
                    row[f"{spec.name}_anti_persistence_logit_weight"] = float(
                        pred.components.get("anti_persistence_logit_weight", np.nan)
                    )
                    row[f"{spec.name}_anti_persistence_materiality_gate"] = float(
                        pred.components.get("anti_persistence_materiality_gate", np.nan)
                    )
                    if spec.name.startswith(("v38", "v39")):
                        row[f"{spec.name}_long_anti_persistence_shift_dollars"] = float(
                            pred.components.get("long_anti_persistence_shift_dollars", np.nan)
                        )
                        row[f"{spec.name}_long_anti_persistence_time_damp"] = float(
                            pred.components.get("long_anti_persistence_time_damp", np.nan)
                        )
                        row[f"{spec.name}_long_anti_persistence_logit_weight"] = float(
                            pred.components.get("long_anti_persistence_logit_weight", np.nan)
                        )
                        row[f"{spec.name}_long_anti_persistence_materiality_gate"] = float(
                            pred.components.get("long_anti_persistence_materiality_gate", np.nan)
                        )
                    if spec.name.startswith("v39"):
                        row[f"{spec.name}_mid_horizon_v28_weight"] = float(
                            pred.components.get("v39_mid_horizon_v28_weight", np.nan)
                        )
        predictions.append(row)

    pred_df = pd.DataFrame(predictions)
    merged = rows.merge(pred_df, on=["opportunity_key", "market"], how="left", suffixes=("", "_pred"))
    for spec in engines:
        p_yes_col = f"{spec.name}_p_yes"
        p_side_col = f"{spec.name}_p_side"
        merged[p_side_col] = np.where(
            merged["side"].eq("yes"),
            pd.to_numeric(merged[p_yes_col], errors="coerce"),
            1.0 - pd.to_numeric(merged[p_yes_col], errors="coerce"),
        )
    return merged


def brier(y: np.ndarray, p: np.ndarray) -> float | None:
    mask = np.isfinite(p)
    if not mask.any():
        return None
    y = y[mask]
    p = np.clip(p[mask], PROB_EPS, 1.0 - PROB_EPS)
    return float(np.mean((p - y) ** 2))


def logloss(y: np.ndarray, p: np.ndarray) -> float | None:
    mask = np.isfinite(p)
    if not mask.any():
        return None
    y = y[mask]
    p = np.clip(p[mask], PROB_EPS, 1.0 - PROB_EPS)
    return float(-(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)).mean())


def ece(y: np.ndarray, p: np.ndarray) -> float | None:
    mask = np.isfinite(p)
    if not mask.any():
        return None
    y = y[mask]
    p = np.clip(p[mask], PROB_EPS, 1.0 - PROB_EPS)
    bins = np.linspace(0.0, 1.0, 11)
    total = len(p)
    out = 0.0
    for lo, hi in zip(bins[:-1], bins[1:]):
        in_bin = (p >= lo) & (p < hi if hi < 1.0 else p <= hi)
        if not in_bin.any():
            continue
        out += float(in_bin.sum()) / total * abs(float(p[in_bin].mean()) - float(y[in_bin].mean()))
    return float(out)


def side_choice_accuracy(rows: pd.DataFrame, model: str) -> tuple[int, int, float | None]:
    p_yes = pd.to_numeric(rows[f"{model}_p_yes"], errors="coerce")
    choices = rows[["opportunity_key", "market", "outcome"]].drop_duplicates("opportunity_key").copy()
    p_by_key = rows[["opportunity_key", f"{model}_p_yes"]].drop_duplicates("opportunity_key")
    choices = choices.merge(p_by_key, on="opportunity_key", how="left")
    choices = choices[choices[f"{model}_p_yes"].notna()].copy()
    if choices.empty:
        return 0, 0, None
    predicted = np.where(pd.to_numeric(choices[f"{model}_p_yes"], errors="coerce").ge(0.5), "yes", "no")
    wins = int((predicted == choices["outcome"].astype(str)).sum())
    total = int(len(choices))
    return wins, total, wins / total if total else None


def metric_row(rows: pd.DataFrame, model: str, split: str) -> dict[str, Any]:
    part = rows if split == "all" else rows[rows["split"].eq(split)]
    y = part["win"].astype(bool).astype(float).to_numpy()
    p = pd.to_numeric(part[f"{model}_p_side"], errors="coerce").to_numpy(dtype=float)
    wins, total, acc = side_choice_accuracy(part, model)
    high = part[pd.to_numeric(part[f"{model}_p_side"], errors="coerce").ge(0.80)].copy()
    high_y = high["win"].astype(bool).astype(float).to_numpy()
    high_p = pd.to_numeric(high[f"{model}_p_side"], errors="coerce").to_numpy(dtype=float)
    return {
        "model": model,
        "split": split,
        "side_rows": int(np.isfinite(p).sum()),
        "opportunities": int(total),
        "brier": brier(y, p),
        "logloss": logloss(y, p),
        "ece10": ece(y, p),
        "side_choice_wins": int(wins),
        "side_choice_accuracy": acc,
        "high_p_rows": int(len(high)),
        "high_p_mean_pred": float(np.nanmean(high_p)) if len(high) else None,
        "high_p_realized": float(np.mean(high_y)) if len(high) else None,
        "high_p_overconfidence": float(np.nanmean(high_p) - np.mean(high_y)) if len(high) else None,
    }


def calibration_rows(rows: pd.DataFrame, model: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    p = pd.to_numeric(rows[f"{model}_p_side"], errors="coerce")
    for split in ["all", "train", "validation", "holdout"]:
        part = rows if split == "all" else rows[rows["split"].eq(split)]
        p_part = p.loc[part.index]
        for lo, hi in zip(CALIBRATION_BINS[:-1], CALIBRATION_BINS[1:]):
            mask = p_part.ge(lo) & (p_part.lt(hi) if hi <= 1.0 else p_part.le(hi))
            bin_rows = part[mask].copy()
            if bin_rows.empty:
                continue
            pred = pd.to_numeric(bin_rows[f"{model}_p_side"], errors="coerce")
            realized = bin_rows["win"].astype(bool).astype(float)
            out.append(
                {
                    "model": model,
                    "split": split,
                    "bin": f"[{lo:.3f},{min(hi, 1.0):.3f}]",
                    "rows": int(len(bin_rows)),
                    "mean_pred": float(pred.mean()),
                    "realized": float(realized.mean()),
                    "error": float(pred.mean() - realized.mean()),
                }
            )
    return out


def write_report(
    path: Path,
    generated: str,
    mode: str,
    engines: list[EngineSpec],
    rows: pd.DataFrame,
    summary: pd.DataFrame,
    calibration: pd.DataFrame,
) -> None:
    all_rows = summary[summary["split"].eq("all")].copy()
    holdout_rows = summary[summary["split"].eq("holdout")].copy()
    best_brier = holdout_rows.sort_values("brier", ascending=True).iloc[0]
    best_logloss = holdout_rows.sort_values("logloss", ascending=True).iloc[0]
    baseline = summary[summary["model"].eq("v28_live_surface")].set_index("split")
    lines: list[str] = [
        "# Mushroom v29 FV Surface Probe",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only replay of FV probability engines on resolved live heartbeat states.",
        "- Primary metrics are probability calibration: Brier, logloss, and ECE.",
        "- Side-choice accuracy is shown only as a sanity check; this is not an entry/exit scorer.",
        f"- Heartbeat mode: `{mode}`.",
        f"- Resolved side rows: {len(rows)}; resolved markets: {rows['market'].nunique()}; opportunities: {rows['opportunity_key'].nunique()}.",
        "",
        "## Candidate Surfaces",
        "",
    ]
    for spec in engines:
        lines.append(f"- `{spec.name}`: {spec.thesis}.")
    lines += [
        "",
        "## Probability Metrics",
        "",
        "| model | split | Brier | logloss | ECE10 | side acc | high-p rows | high-p pred/realized | high-p overconf |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    ordered = summary.sort_values(["split", "brier"])
    for _, row in ordered.iterrows():
        if row["split"] not in {"all", "validation", "holdout"}:
            continue
        lines.append(
            f"| `{row['model']}` | {row['split']} | {row['brier']:.5f} | {row['logloss']:.5f} | "
            f"{row['ece10']:.5f} | {pct(row['side_choice_accuracy'])} | {int(row['high_p_rows'])} | "
            f"{pct(row['high_p_mean_pred'])}/{pct(row['high_p_realized'])} | {pct(row['high_p_overconfidence'])} |"
        )
    lines += [
        "",
        "## Deltas vs v28",
        "",
        "| model | all Brier delta | holdout Brier delta | all logloss delta | holdout logloss delta |",
        "|---|---:|---:|---:|---:|",
    ]
    for model in all_rows.sort_values("brier")["model"].tolist():
        model_summary = summary[summary["model"].eq(model)].set_index("split")
        all_delta_brier = float(model_summary.loc["all", "brier"] - baseline.loc["all", "brier"])
        hold_delta_brier = float(model_summary.loc["holdout", "brier"] - baseline.loc["holdout", "brier"])
        all_delta_ll = float(model_summary.loc["all", "logloss"] - baseline.loc["all", "logloss"])
        hold_delta_ll = float(model_summary.loc["holdout", "logloss"] - baseline.loc["holdout", "logloss"])
        lines.append(
            f"| `{model}` | {all_delta_brier:+.5f} | {hold_delta_brier:+.5f} | {all_delta_ll:+.5f} | {hold_delta_ll:+.5f} |"
        )
    lines += [
        "",
        "## Calibration Bins",
        "",
        "Holdout bins for the baseline and best holdout-Brier model:",
        "",
        "| model | bin | rows | mean pred | realized | error |",
        "|---|---|---:|---:|---:|---:|",
    ]
    show_models = {"v28_live_surface", str(best_brier["model"])}
    cal_show = calibration[calibration["split"].eq("holdout") & calibration["model"].isin(show_models)].copy()
    for _, row in cal_show.sort_values(["model", "bin"]).iterrows():
        lines.append(
            f"| `{row['model']}` | {row['bin']} | {int(row['rows'])} | "
            f"{pct(row['mean_pred'])} | {pct(row['realized'])} | {pct(row['error'])} |"
        )
    lines += [
        "",
        "## Read",
        "",
        f"- Best holdout Brier: `{best_brier['model']}` at {best_brier['brier']:.5f}.",
        f"- Best holdout logloss: `{best_logloss['model']}` at {best_logloss['logloss']:.5f}.",
    ]
    if str(best_brier["model"]) != "v28_live_surface":
        delta = float(best_brier["brier"] - baseline.loc["holdout", "brier"])
        lines.append(f"- Holdout Brier improvement versus v28 baseline: {delta:+.5f}.")
    else:
        lines.append("- v29 variants did not beat the v28 baseline on holdout Brier in this replay.")
    lines.append(
        "- A model change is only useful if it improves calibration without depending on a post-hoc trade filter; this report keeps those separate."
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default=DEFAULT_MODE)
    args = parser.parse_args()

    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    safe_mode = str(args.mode).replace("/", "_").replace("\\", "_")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ledger = load_ledger(args.mode)
    candles = load_candles()
    engines = make_engines()
    rows = replay_predictions(ledger, candles, engines)
    splits = market_splits(rows)
    rows = rows.merge(splits[["market", "split"]], on="market", how="left")

    summary_rows: list[dict[str, Any]] = []
    cal_rows: list[dict[str, Any]] = []
    for spec in engines:
        for split in ["all", "train", "validation", "holdout"]:
            summary_rows.append(metric_row(rows, spec.name, split))
        cal_rows.extend(calibration_rows(rows, spec.name))
    summary = pd.DataFrame(summary_rows)
    calibration = pd.DataFrame(cal_rows)

    mode_report_md = OUT_DIR / f"mushroom_v29_fv_surface_{safe_mode}_latest.md"
    stamp_report_md = OUT_DIR / f"mushroom_v29_fv_surface_{safe_mode}_{generated}.md"
    mode_report_json = OUT_DIR / f"mushroom_v29_fv_surface_{safe_mode}_latest.json"
    stamp_report_json = OUT_DIR / f"mushroom_v29_fv_surface_{safe_mode}_{generated}.json"
    mode_summary_csv = OUT_DIR / f"mushroom_v29_fv_surface_summary_{safe_mode}_latest.csv"
    stamp_summary_csv = OUT_DIR / f"mushroom_v29_fv_surface_summary_{safe_mode}_{generated}.csv"
    mode_calibration_csv = OUT_DIR / f"mushroom_v29_fv_surface_calibration_{safe_mode}_latest.csv"
    stamp_calibration_csv = OUT_DIR / f"mushroom_v29_fv_surface_calibration_{safe_mode}_{generated}.csv"
    mode_predictions_csv = OUT_DIR / f"mushroom_v29_fv_surface_predictions_{safe_mode}_latest.csv"

    for path in [PREDICTIONS_CSV, mode_predictions_csv]:
        rows.to_csv(path, index=False)
    for path in [SUMMARY_CSV, mode_summary_csv, stamp_summary_csv]:
        summary.to_csv(path, index=False)
    for path in [CALIBRATION_CSV, mode_calibration_csv, stamp_calibration_csv]:
        calibration.to_csv(path, index=False)
    payload = {
        "generated_utc": generated,
        "mode": args.mode,
        "ledger_path": str(LEDGER_PATH),
        "candle_path": str(CANDLE_PATH),
        "rows": int(len(rows)),
        "markets": int(rows["market"].nunique()),
        "opportunities": int(rows["opportunity_key"].nunique()),
        "summary": summary.to_dict("records"),
        "candidate_surfaces": [{"name": spec.name, "thesis": spec.thesis} for spec in engines],
    }
    for path in [REPORT_JSON, mode_report_json, stamp_report_json]:
        path.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True), encoding="utf-8")
    for path in [REPORT_MD, mode_report_md, stamp_report_md]:
        write_report(path, generated, args.mode, engines, rows, summary, calibration)

    print("Mushroom v29 FV surface probe complete")
    print(f"mode={args.mode} rows={len(rows)} markets={rows['market'].nunique()} opportunities={rows['opportunity_key'].nunique()}")
    best = summary[summary["split"].eq("holdout")].sort_values("brier").iloc[0]
    print(f"best_holdout_brier={best['model']} {best['brier']:.6f}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
