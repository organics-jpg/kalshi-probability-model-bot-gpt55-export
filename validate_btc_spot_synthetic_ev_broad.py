from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from probe_codex_entry_timing_edges import delayed_entry_pnl
from probe_codex_terminal_salvage_all_trades import (
    EDGE_DIR,
    discover_datasets,
    load_dataset_cases,
    run_baseline,
)
from probe_stop_touch_confirmation import (
    append_ledger,
    estimated_order_fee_cents,
    idea_key,
    result_distance,
    strategy_id,
    update_strategy_memory,
)
from research_pipeline import add_btc_technical_columns, fetch_binance_btc_spot_candles


UTC = timezone.utc
ROOT = Path(__file__).resolve().parent

PRIOR_SYNTHETIC_EV_PARAMS = {
    "delay_seconds": 0,
    "intercept": 1.5,
    "location_weight": 1.0,
    "macd_weight": 0.0,
    "max_entry_ask": 90,
    "max_opp_pressure": 0.5,
    "max_spread": 4,
    "min_bid_sum": 0,
    "min_ev_cents": 2.0,
    "move_scale": 0.25,
    "pressure_penalty": 0.5,
    "range_penalty": 0.25,
    "rsi_weight": 0.15,
    "spread_penalty": 0.03,
    "w_15m": 0.0,
    "w_1m": 0.0,
    "w_5m": 1.0,
    "side_polarity": 1,
}


@dataclass(frozen=True)
class StrategySpec:
    family: str
    theorem: str
    equation: str
    params: dict[str, Any]
    simulator: Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], tuple[float, dict[str, Any]]]


def safe_float(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return math.nan
    return parsed if not math.isnan(parsed) else math.nan


def clamp(value: float, lo: float, hi: float) -> float:
    return min(hi, max(lo, value))


def sigmoid(value: float) -> float:
    if value >= 40:
        return 1.0
    if value <= -40:
        return 0.0
    return 1.0 / (1.0 + math.exp(-value))


def mean(values: list[float]) -> float:
    clean = [value for value in values if not math.isnan(value)]
    return sum(clean) / len(clean) if clean else math.nan


def pressure_from_values(own_bid: float, opp_bid: float) -> float:
    denom = own_bid + opp_bid
    return opp_bid / denom if denom > 0 else math.nan


def compact_quote_point(point: dict[str, Any]) -> dict[str, float] | None:
    elapsed = safe_float(point.get("elapsed"))
    own_bid = safe_float(point.get("own_bid"))
    opp_bid = safe_float(point.get("opp_bid"))
    own_ask = safe_float(point.get("own_ask"))
    held_ask = safe_float(point.get("held_ask"))
    bid_sum = safe_float(point.get("bid_sum"))
    if any(math.isnan(value) for value in (elapsed, own_bid, opp_bid, own_ask, held_ask, bid_sum)):
        return None
    return {
        "elapsed": elapsed,
        "own_bid": own_bid,
        "opp_bid": opp_bid,
        "own_ask": own_ask,
        "held_ask": held_ask,
        "bid_sum": bid_sum,
        "spread": own_ask - own_bid,
        "pressure": pressure_from_values(own_bid, opp_bid),
    }


def quote_snapshot_at_or_after(case: dict[str, Any], delay_seconds: int) -> dict[str, Any] | None:
    path = [point for point in (compact_quote_point(raw) for raw in case.get("path", [])) if point is not None]
    for point in sorted(path, key=lambda item: item["elapsed"]):
        if point["elapsed"] >= float(delay_seconds):
            return point
    return None


def quote_history_until(case: dict[str, Any], elapsed_seconds: float) -> list[dict[str, float]]:
    path = [point for point in (compact_quote_point(raw) for raw in case.get("path", [])) if point is not None]
    return [point for point in sorted(path, key=lambda item: item["elapsed"]) if point["elapsed"] <= elapsed_seconds]


def side_sign(case: dict[str, Any], params: dict[str, Any]) -> float:
    base = 1.0 if str(case.get("side") or "").lower() == "yes" else -1.0
    return base * float(params.get("side_polarity", 1))


def quote_gate(features: dict[str, Any], params: dict[str, Any]) -> bool:
    held_ask = safe_float(features.get("held_ask"))
    pressure = safe_float(features.get("pressure"))
    bid_sum = safe_float(features.get("bid_sum"))
    spread = safe_float(features.get("spread"))
    if any(math.isnan(value) for value in (held_ask, pressure, bid_sum, spread)):
        return False
    return (
        held_ask <= float(params["max_entry_ask"])
        and pressure <= float(params["max_opp_pressure"])
        and bid_sum >= float(params["min_bid_sum"])
        and spread <= float(params["max_spread"])
    )


def candle_cache_path(start: pd.Timestamp, end: pd.Timestamp) -> Path:
    start_key = start.strftime("%Y%m%dT%H%M")
    end_key = end.strftime("%Y%m%dT%H%M")
    return EDGE_DIR / f"btc_1m_candles_broad_validation_{start_key}_{end_key}.csv"


def load_or_fetch_candles(cases: list[dict[str, Any]], refresh_cache: bool) -> pd.DataFrame:
    entry_times = pd.to_datetime([case["entry_ts"] for case in cases], utc=True, errors="coerce")
    start = (entry_times.min() - pd.Timedelta(hours=3)).floor("min")
    end = (entry_times.max() + pd.Timedelta(minutes=15)).ceil("min")
    path = candle_cache_path(start, end)
    latest = EDGE_DIR / "btc_1m_candles_broad_validation_latest.csv"
    if path.exists() and not refresh_cache:
        raw = pd.read_csv(path)
        for col in ("open_dt", "close_dt"):
            raw[col] = pd.to_datetime(raw[col], utc=True, errors="coerce")
    else:
        raw = fetch_binance_btc_spot_candles(start, end)
        EDGE_DIR.mkdir(parents=True, exist_ok=True)
        raw.to_csv(path, index=False)
        raw.to_csv(latest, index=False)
    enriched = add_btc_technical_columns(raw)
    if "close_dt" not in enriched.columns:
        raise RuntimeError("BTC candle table is missing close_dt")
    enriched["close_dt"] = pd.to_datetime(enriched["close_dt"], utc=True, errors="coerce")
    return enriched[enriched["close_dt"].notna()].sort_values("close_dt").reset_index(drop=True)


def candle_snapshot(candles: pd.DataFrame, target: pd.Timestamp) -> dict[str, Any] | None:
    idx = int(candles["close_dt"].searchsorted(target, side="right") - 1)
    if idx < 0:
        return None
    row = candles.iloc[idx].to_dict()
    age_seconds = (target - pd.Timestamp(row["close_dt"])).total_seconds()
    if age_seconds < 0 or age_seconds > 120:
        return None
    return {
        "btc_age_seconds": age_seconds,
        "btc_close": safe_float(row.get("close")),
        "btc_move_1m_bps": safe_float(row.get("move_1m_bps")),
        "btc_move_5m_bps": safe_float(row.get("move_5m_bps")),
        "btc_move_15m_bps": safe_float(row.get("move_15m_bps")),
        "btc_range_15m_bps": safe_float(row.get("range_15m_bps")),
        "btc_distance_to_15m_high_bps": safe_float(row.get("distance_to_15m_high_bps")),
        "btc_distance_to_15m_low_bps": safe_float(row.get("distance_to_15m_low_bps")),
        "btc_rsi14": safe_float(row.get("rsi14")),
        "btc_macd_hist": safe_float(row.get("macd_hist")),
        "btc_source_close_dt": pd.Timestamp(row["close_dt"]).isoformat(),
    }


def quality_dwell_share(history: list[dict[str, float]], params: dict[str, Any]) -> tuple[float, float]:
    if len(history) < 2:
        return 0.0, 0.0
    elapsed_span = max(1.0, history[-1]["elapsed"] - history[0]["elapsed"])
    quality_seconds = 0.0
    for idx in range(1, len(history)):
        prev = history[idx - 1]
        cur = history[idx]
        dt = max(0.0, cur["elapsed"] - prev["elapsed"])
        if quote_gate(prev, params):
            quality_seconds += dt
    return quality_seconds / elapsed_span, quality_seconds


def prepare_case(case: dict[str, Any], candles: pd.DataFrame, delays: tuple[int, ...]) -> dict[str, Any]:
    snapshots: dict[str, dict[str, Any] | None] = {}
    entry_ts = pd.Timestamp(case["entry_ts"])
    if entry_ts.tzinfo is None:
        entry_ts = entry_ts.tz_localize("UTC")
    else:
        entry_ts = entry_ts.tz_convert("UTC")
    for delay in delays:
        quote = quote_snapshot_at_or_after(case, delay)
        if not quote:
            snapshots[str(delay)] = None
            continue
        actual_elapsed = float(quote["elapsed"])
        target = entry_ts + pd.Timedelta(seconds=actual_elapsed)
        btc = candle_snapshot(candles, target)
        if not btc:
            snapshots[str(delay)] = None
            continue
        history = quote_history_until(case, actual_elapsed)
        snapshots[str(delay)] = {
            **quote,
            **btc,
            "requested_delay_seconds": delay,
            "actual_quote_elapsed": actual_elapsed,
            "quality_history": history,
        }
    return snapshots


def side_move_score(case: dict[str, Any], features: dict[str, Any], params: dict[str, Any]) -> float:
    move_1m = safe_float(features.get("btc_move_1m_bps"))
    move_5m = safe_float(features.get("btc_move_5m_bps"))
    move_15m = safe_float(features.get("btc_move_15m_bps"))
    btc_range = max(1.0, safe_float(features.get("btc_range_15m_bps")))
    if any(math.isnan(value) for value in (move_1m, move_5m, move_15m, btc_range)):
        return math.nan
    weighted_move = (
        float(params.get("w_1m", 0.0)) * move_1m
        + float(params.get("w_5m", 0.0)) * move_5m
        + float(params.get("w_15m", 0.0)) * move_15m
    )
    return side_sign(case, params) * weighted_move / math.sqrt(btc_range)


def side_location_score(case: dict[str, Any], features: dict[str, Any], params: dict[str, Any]) -> float:
    dist_high = safe_float(features.get("btc_distance_to_15m_high_bps"))
    dist_low = safe_float(features.get("btc_distance_to_15m_low_bps"))
    btc_range = max(1.0, safe_float(features.get("btc_range_15m_bps")))
    if any(math.isnan(value) for value in (dist_high, dist_low, btc_range)):
        return math.nan
    return side_sign(case, params) * (dist_low - dist_high) / btc_range


def side_rsi_score(case: dict[str, Any], features: dict[str, Any], params: dict[str, Any]) -> float:
    rsi = safe_float(features.get("btc_rsi14"))
    if math.isnan(rsi):
        return 0.0
    return side_sign(case, params) * (rsi - 50.0) / 20.0


def side_macd_score(case: dict[str, Any], features: dict[str, Any], params: dict[str, Any]) -> float:
    macd_hist = safe_float(features.get("btc_macd_hist"))
    if math.isnan(macd_hist):
        return 0.0
    return side_sign(case, params) * macd_hist / 20.0


def synthetic_ev_score(case: dict[str, Any], features: dict[str, Any], params: dict[str, Any]) -> dict[str, float] | None:
    move = side_move_score(case, features, params)
    location = side_location_score(case, features, params)
    btc_range = safe_float(features.get("btc_range_15m_bps"))
    ask = safe_float(features.get("held_ask"))
    if any(math.isnan(value) for value in (move, location, btc_range, ask)):
        return None
    z = (
        float(params["intercept"])
        + float(params["move_scale"]) * move
        + float(params["location_weight"]) * location
        + float(params.get("rsi_weight", 0.0)) * side_rsi_score(case, features, params)
        + float(params.get("macd_weight", 0.0)) * side_macd_score(case, features, params)
        - float(params["range_penalty"]) * btc_range / 100.0
        - float(params["pressure_penalty"]) * safe_float(features.get("pressure"))
        - float(params["spread_penalty"]) * safe_float(features.get("spread"))
    )
    q_spot = sigmoid(z)
    fee_per_contract = estimated_order_fee_cents(ask, max(1, int(case["qty"]))) / max(1, int(case["qty"]))
    ev_cents = 100.0 * q_spot - ask - fee_per_contract
    return {
        "z": z,
        "q_spot": q_spot,
        "ev_cents": ev_cents,
        "side_move_score": move,
        "side_location_score": location,
        "fee_per_contract": fee_per_contract,
    }


def entry_meta(case: dict[str, Any], features: dict[str, Any], extra: dict[str, Any], contracts: int | None = None) -> tuple[float, dict[str, Any]]:
    ask = float(features["held_ask"])
    qty = int(case["qty"] if contracts is None else contracts)
    return delayed_entry_pnl(case, ask, contracts=qty), {
        "enter": True,
        "entry_ask": ask,
        "entry_elapsed": float(features["actual_quote_elapsed"]),
        "contracts": qty,
        "pressure": round(float(features["pressure"]), 6),
        "spread": round(float(features["spread"]), 4),
        "bid_sum": round(float(features["bid_sum"]), 4),
        "btc_age_seconds": round(float(features["btc_age_seconds"]), 4),
        **extra,
    }


def sim_btc_spot_synthetic_ev_broad(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not quote_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    scored = synthetic_ev_score(case, features, params)
    if scored is None:
        return 0.0, {"enter": False, "skip_reason": "missing_btc_features"}
    if scored["ev_cents"] < float(params["min_ev_cents"]):
        return 0.0, {"enter": False, "skip_reason": "synthetic_ev_too_low", "score": round(scored["ev_cents"], 6)}
    return entry_meta(
        case,
        features,
        {
            "score": round(scored["ev_cents"], 6),
            "q_spot": round(scored["q_spot"], 6),
            "z": round(scored["z"], 6),
            "side_move_score": round(scored["side_move_score"], 6),
            "side_location_score": round(scored["side_location_score"], 6),
            "polarity": "yes_up" if int(params.get("side_polarity", 1)) == 1 else "yes_down",
        },
    )


def sim_btc_spot_ev_dwell_combo_broad(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not quote_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    scored = synthetic_ev_score(case, features, params)
    if scored is None:
        return 0.0, {"enter": False, "skip_reason": "missing_btc_features"}
    dwell_share, quality_seconds = quality_dwell_share(features.get("quality_history") or [], params)
    combo_score = scored["ev_cents"] + float(params["dwell_bonus_cents"]) * dwell_share
    if dwell_share < float(params["min_quality_share"]) or quality_seconds < float(params["min_quality_seconds"]):
        return 0.0, {
            "enter": False,
            "skip_reason": "insufficient_quality_dwell",
            "score": round(combo_score, 6),
        }
    if combo_score < float(params["min_combo_score"]):
        return 0.0, {"enter": False, "skip_reason": "combo_score_too_low", "score": round(combo_score, 6)}
    return entry_meta(
        case,
        features,
        {
            "score": round(combo_score, 6),
            "raw_ev_cents": round(scored["ev_cents"], 6),
            "q_spot": round(scored["q_spot"], 6),
            "quality_share": round(dwell_share, 6),
            "quality_seconds": round(quality_seconds, 4),
            "polarity": "yes_up" if int(params.get("side_polarity", 1)) == 1 else "yes_down",
        },
    )


def build_strategy_grid() -> list[StrategySpec]:
    strategies: list[StrategySpec] = []

    synthetic_theorem = (
        "A BTC 15-minute binary entry should clear an independent BTC spot-implied EV check using only the latest "
        "closed candle before the quote decision; this validates whether the prior feature-row signal survives a broader, coarser data source."
    )
    synthetic_equation = (
        "q=sigmoid(c+a*s*(w1*m1+w5*m5+w15*m15)/sqrt(R15)+b*s*(dist_low-dist_high)/R15"
        "+r*s*(RSI-50)/20+h*s*MACD/20-rho*R15/100-lambda*p_opp-mu*spread); EV=100*q-H-fee; enter if EV>=e."
    )
    for delay_seconds in (0, 60, 120):
        for max_entry_ask in (88, 90, 92, 94):
            for max_opp_pressure in (0.30, 0.50):
                for max_spread in (4, 10):
                    for intercept in (1.0, 1.5, 2.0):
                        for move_scale in (0.0, 0.25, 0.50):
                            for location_weight in (0.5, 1.0):
                                for rsi_weight in (0.0, 0.15):
                                    for range_penalty in (0.0, 0.25):
                                        for min_ev_cents in (-2.0, 2.0, 5.0):
                                            for side_polarity in (1, -1):
                                                strategies.append(
                                                    StrategySpec(
                                                        "btc_spot_synthetic_ev_broad_validation",
                                                        synthetic_theorem,
                                                        synthetic_equation,
                                                        {
                                                            "delay_seconds": delay_seconds,
                                                            "max_entry_ask": max_entry_ask,
                                                            "max_opp_pressure": max_opp_pressure,
                                                            "min_bid_sum": 0,
                                                            "max_spread": max_spread,
                                                            "intercept": intercept,
                                                            "move_scale": move_scale,
                                                            "location_weight": location_weight,
                                                            "w_1m": 0.0,
                                                            "w_5m": 1.0,
                                                            "w_15m": 0.0,
                                                            "rsi_weight": rsi_weight,
                                                            "macd_weight": 0.0,
                                                            "range_penalty": range_penalty,
                                                            "pressure_penalty": 0.5,
                                                            "spread_penalty": 0.03,
                                                            "min_ev_cents": min_ev_cents,
                                                            "side_polarity": side_polarity,
                                                        },
                                                        sim_btc_spot_synthetic_ev_broad,
                                                    )
                                                )

    combo_theorem = (
        "The BTC spot EV signal should be more reliable when the executable quote state also dwelled in a supported state; "
        "a high spot score attached to a fleeting or wide quote is less trustworthy."
    )
    combo_equation = (
        "C=EV_spot+d*Q, Q=(1/T)integral 1{H<=A, spread<=S, bid_sum>=B, p_opp<=P}dt; "
        "enter if Q>=q, quality_seconds>=s, and C>=c."
    )
    for delay_seconds in (60, 120, 180):
        for max_entry_ask in (88, 90, 92):
            for max_opp_pressure in (0.30, 0.50):
                for max_spread in (4, 10):
                    for min_quality_share in (0.50, 0.75, 0.90):
                        for min_quality_seconds in (10, 30):
                            for dwell_bonus_cents in (0.0, 2.0, 5.0):
                                for min_combo_score in (0.0, 2.0, 5.0):
                                    for side_polarity in (1, -1):
                                        params = {
                                            **PRIOR_SYNTHETIC_EV_PARAMS,
                                            "delay_seconds": delay_seconds,
                                            "max_entry_ask": max_entry_ask,
                                            "max_opp_pressure": max_opp_pressure,
                                            "max_spread": max_spread,
                                            "min_quality_share": min_quality_share,
                                            "min_quality_seconds": min_quality_seconds,
                                            "dwell_bonus_cents": dwell_bonus_cents,
                                            "min_combo_score": min_combo_score,
                                            "side_polarity": side_polarity,
                                        }
                                        strategies.append(
                                            StrategySpec(
                                                "btc_spot_ev_dwell_combo_broad",
                                                combo_theorem,
                                                combo_equation,
                                                params,
                                                sim_btc_spot_ev_dwell_combo_broad,
                                            )
                                        )
    return strategies


def row_for(case: dict[str, Any], pnl: float, meta: dict[str, Any], label: str) -> dict[str, Any]:
    entered = bool(meta.get("enter"))
    return {
        "label": label,
        "dataset": case["dataset"],
        "market": case["market"],
        "side": case.get("side"),
        "entry_day_et": case["entry_day_et"],
        "entry_ts": case["entry_ts"],
        "settlement_win": bool(case["settlement_win"]),
        "actual_net_pnl": float(case["actual_net_pnl"]),
        "hold_pnl": float(case["hold_pnl"]),
        "sim_pnl": float(pnl),
        "action": "enter" if entered else "skip",
        "entry_ask": meta.get("entry_ask") if entered else None,
        "entry_elapsed": meta.get("entry_elapsed") if entered else None,
        "contracts": int(meta.get("contracts") or 0) if entered else 0,
        "base_contracts": int(case["qty"]),
        "skip_reason": meta.get("skip_reason"),
        "score": meta.get("score"),
    }


def summarize_entry_rows(label: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    entered = [row for row in rows if row["action"] == "enter"]
    skipped = [row for row in rows if row["action"] == "skip"]
    entered_winners = [row for row in entered if row["settlement_win"]]
    entered_losers = [row for row in entered if not row["settlement_win"]]
    skipped_winners = [row for row in skipped if row["settlement_win"]]
    skipped_losers = [row for row in skipped if not row["settlement_win"]]
    actual = sum(float(row["actual_net_pnl"]) for row in rows)
    no_stop = sum(float(row["hold_pnl"]) for row in rows)
    sim = sum(float(row["sim_pnl"]) for row in rows)
    total_contracts = sum(int(row["contracts"]) for row in entered)
    base_contracts = sum(int(row["base_contracts"]) for row in rows)
    return {
        "label": label,
        "n": len(rows),
        "actual_recorded_pnl": round(actual, 2),
        "no_stop_hold_pnl": round(no_stop, 2),
        "no_trade_all_pnl": 0.0,
        "sim_pnl": round(sim, 2),
        "delta_vs_actual": round(sim - actual, 2),
        "delta_vs_no_stop": round(sim - no_stop, 2),
        "delta_vs_no_trade_all": round(sim, 2),
        "entries": len(entered),
        "skips": len(skipped),
        "entered_settlement_winners": len(entered_winners),
        "entered_settlement_losers": len(entered_losers),
        "skipped_settlement_winners": len(skipped_winners),
        "skipped_settlement_losers": len(skipped_losers),
        "entry_win_rate": round(len(entered_winners) / len(entered), 4) if entered else 0.0,
        "avg_entry_ask": round(mean([float(row["entry_ask"]) for row in entered if row["entry_ask"] is not None]), 4)
        if entered
        else None,
        "avg_entry_elapsed": round(
            mean([float(row["entry_elapsed"]) for row in entered if row["entry_elapsed"] is not None]), 4
        )
        if entered
        else None,
        "avg_score": round(mean([safe_float(row.get("score")) for row in entered]), 6) if entered else None,
        "total_contracts": total_contracts,
        "base_contracts": base_contracts,
        "contract_fraction": round(total_contracts / base_contracts, 4) if base_contracts else 0.0,
        "worst_trade": round(min(float(row["sim_pnl"]) for row in entered), 4) if entered else 0.0,
    }


def summarize_by_group(label: str, rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {
        value: summarize_entry_rows(label, [row for row in rows if str(row.get(key)) == value])
        for value in sorted({str(row.get(key)) for row in rows})
    }


def run_strategy(prepped: list[tuple[dict[str, Any], dict[str, Any]]], strategy: StrategySpec) -> dict[str, Any]:
    sid = strategy_id(strategy.family, strategy.params)
    rows = [row_for(case, *strategy.simulator(case, prepared, strategy.params), sid) for case, prepared in prepped]
    return {
        "strategy_id": sid,
        "family": strategy.family,
        "theorem": strategy.theorem,
        "equation": strategy.equation,
        "params": strategy.params,
        "summary": summarize_entry_rows(sid, rows),
        "by_dataset": summarize_by_group(sid, rows, "dataset"),
        "by_side": summarize_by_group(sid, rows, "side"),
        "by_day": summarize_by_group(sid, rows, "entry_day_et"),
        "interesting_examples": sorted(rows, key=lambda row: (float(row["sim_pnl"]), row["market"]))[:10],
    }


def min_entries(holdout: bool = False) -> int:
    return 10 if holdout else 25


def select_family_best(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for family in sorted({result["family"] for result in results}):
        family_results = [result for result in results if result["family"] == family]
        candidates = [result for result in family_results if result["summary"]["entries"] >= min_entries()] or family_results
        output[family] = max(
            candidates,
            key=lambda result: (
                result["summary"]["sim_pnl"],
                result["summary"]["entry_win_rate"],
                -(result["summary"]["avg_entry_ask"] or 0.0),
            ),
        )
    return output


def walk_forward_summary(prepped: list[tuple[dict[str, Any], dict[str, Any]]], strategies: list[StrategySpec]) -> dict[str, Any]:
    ordered = sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
    split = int(len(ordered) * 0.7)
    train = ordered[:split]
    holdout = ordered[split:]
    output: dict[str, Any] = {
        "train_n": len(train),
        "holdout_n": len(holdout),
        "split_entry_ts": ordered[split][0]["entry_ts"] if holdout else None,
        "selection_basis": "Max train simulated PnL among variants with at least 25 train entries.",
        "families": {},
    }
    for family in sorted({strategy.family for strategy in strategies}):
        family_strategies = [strategy for strategy in strategies if strategy.family == family]
        train_results = [run_strategy(train, strategy) for strategy in family_strategies]
        train_candidates = [result for result in train_results if result["summary"]["entries"] >= min_entries()]
        selected = max(train_candidates or train_results, key=lambda result: result["summary"]["sim_pnl"])
        selected_spec = next(
            strategy
            for strategy in family_strategies
            if strategy_id(strategy.family, strategy.params) == selected["strategy_id"]
        )
        holdout_result = run_strategy(holdout, selected_spec)
        output["families"][family] = {
            "selected_strategy_id": selected["strategy_id"],
            "selected_params": selected["params"],
            "train_summary": selected["summary"],
            "holdout_summary": holdout_result["summary"],
            "holdout_by_dataset": holdout_result["by_dataset"],
            "holdout_by_side": holdout_result["by_side"],
        }
    return output


def robust_positive_scan(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]],
    strategies: list[StrategySpec],
    full_results: list[dict[str, Any]],
    max_candidates_per_family: int,
) -> dict[str, list[dict[str, Any]]]:
    ordered = sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
    split = int(len(ordered) * 0.7)
    train = ordered[:split]
    holdout = ordered[split:]
    output: dict[str, list[dict[str, Any]]] = {}
    full_by_id = {result["strategy_id"]: result for result in full_results}
    for family in sorted({strategy.family for strategy in strategies}):
        rows: list[dict[str, Any]] = []
        family_strategies = [item for item in strategies if item.family == family]
        screened = sorted(
            [
                strategy
                for strategy in family_strategies
                if full_by_id.get(strategy_id(strategy.family, strategy.params), {})
                .get("summary", {})
                .get("sim_pnl", 0.0)
                > 0
                and full_by_id.get(strategy_id(strategy.family, strategy.params), {})
                .get("summary", {})
                .get("entries", 0)
                >= min_entries()
            ],
            key=lambda strategy: full_by_id[strategy_id(strategy.family, strategy.params)]["summary"]["sim_pnl"],
            reverse=True,
        )[:max_candidates_per_family]
        for strategy in screened:
            train_result = run_strategy(train, strategy)
            holdout_result = run_strategy(holdout, strategy)
            train_summary = train_result["summary"]
            holdout_summary = holdout_result["summary"]
            if (
                train_summary["sim_pnl"] <= 0
                or holdout_summary["sim_pnl"] <= 0
                or train_summary["entries"] < min_entries()
                or holdout_summary["entries"] < min_entries(holdout=True)
            ):
                continue
            rows.append(
                {
                    "strategy_id": train_result["strategy_id"],
                    "params": train_result["params"],
                    "train_sim_pnl": train_summary["sim_pnl"],
                    "train_entries": train_summary["entries"],
                    "train_entry_win_rate": train_summary["entry_win_rate"],
                    "holdout_sim_pnl": holdout_summary["sim_pnl"],
                    "holdout_entries": holdout_summary["entries"],
                    "holdout_entry_win_rate": holdout_summary["entry_win_rate"],
                    "min_split_pnl": min(train_summary["sim_pnl"], holdout_summary["sim_pnl"]),
                }
            )
        output[family] = sorted(
            rows,
            key=lambda row: (row["min_split_pnl"], row["holdout_sim_pnl"], row["train_sim_pnl"]),
            reverse=True,
        )[:20]
    return output


def sensitivity(results: list[dict[str, Any]], best_by_family: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    for family, best in best_by_family.items():
        ranked = sorted(
            [
                result
                for result in results
                if result["family"] == family and result["summary"]["entries"] >= min_entries()
            ],
            key=lambda result: (result_distance(result["params"], best["params"]), -result["summary"]["sim_pnl"]),
        )
        output[family] = [
            {
                "strategy_id": result["strategy_id"],
                "params": result["params"],
                "sim_pnl": result["summary"]["sim_pnl"],
                "delta_vs_actual": result["summary"]["delta_vs_actual"],
                "delta_vs_no_stop": result["summary"]["delta_vs_no_stop"],
                "delta_vs_no_trade_all": result["summary"]["delta_vs_no_trade_all"],
                "entries": result["summary"]["entries"],
                "entry_win_rate": result["summary"]["entry_win_rate"],
                "avg_entry_ask": result["summary"]["avg_entry_ask"],
            }
            for result in ranked[:12]
        ]
    return output


def status_for(family: str, result: dict[str, Any], payload: dict[str, Any]) -> str:
    holdout = payload["walk_forward"]["families"].get(family, {}).get("holdout_summary", {})
    robust_rows = payload["robust_positive_scan"].get(family, [])
    if (
        result["summary"]["delta_vs_no_trade_all"] > 0
        and holdout.get("delta_vs_no_trade_all", 0) > 0
        and len(robust_rows) >= 5
    ):
        return "candidate_for_human_review"
    if result["summary"]["delta_vs_no_trade_all"] > 0 and robust_rows:
        return "watchlist_positive_but_selection_sensitive"
    if result["summary"]["delta_vs_no_trade_all"] > 0:
        return "watchlist_positive_but_not_robust"
    return "tested_negative"


def baseline_payload(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "actual": run_baseline(cases, "actual"),
        "no_stop": run_baseline(cases, "no_stop"),
        "held_ask_stop_70": run_baseline(cases, "held_ask_stop_70"),
        "no_trade_all": {"summary": {"sim_pnl": 0.0}},
    }


def polarity_counts(results: list[dict[str, Any]], family: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for polarity in (1, -1):
        subset = [
            result
            for result in results
            if result["family"] == family
            and int(result["params"].get("side_polarity", 1)) == polarity
            and result["summary"]["entries"] >= min_entries()
        ]
        if not subset:
            continue
        best = max(subset, key=lambda result: result["summary"]["sim_pnl"])
        out["yes_up" if polarity == 1 else "yes_down"] = {
            "strategy_id": best["strategy_id"],
            "sim_pnl": best["summary"]["sim_pnl"],
            "entries": best["summary"]["entries"],
            "entry_win_rate": best["summary"]["entry_win_rate"],
            "params": best["params"],
        }
    return out


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    base = payload["baselines"]
    prior = payload["locked_prior_result"]["summary"]
    lines = [
        "# BTC Spot Synthetic EV Broad Validation",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Quote-path cases with BTC closed-candle features: `{payload['case_count']}`",
        f"- BTC candle source: `{payload['btc_candle_source']}`",
        "- Scope: research-only validation/backtest; live entry logic, live exit logic, configs, run scripts, and bot processes were not changed.",
        "- Validation note: BTC features use the latest fully closed 1-minute candle before the quote decision. This is broader but coarser than the previous 129-case live feature-row test.",
        "",
        "## Baselines",
        "",
        f"- Actual recorded PnL: `${base['actual']['summary']['sim_pnl']}`",
        f"- No-stop hold-to-settlement PnL using original entries: `${base['no_stop']['summary']['sim_pnl']}`",
        f"- First held-ask <=70 exit baseline: `${base['held_ask_stop_70']['summary']['sim_pnl']}`",
        "- Skip every opportunity baseline: `$0.0`",
        "",
        "## Locked Prior Rule",
        "",
        f"- Strategy ID: `{payload['locked_prior_result']['strategy_id']}`",
        f"- Prior params: `{json.dumps(payload['locked_prior_result']['params'], sort_keys=True)}`",
        f"- PnL / delta vs actual / delta vs no-stop / delta vs skip-all: `${prior['sim_pnl']}` / `${prior['delta_vs_actual']}` / `${prior['delta_vs_no_stop']}` / `${prior['delta_vs_no_trade_all']}`",
        f"- Entries / win rate / avg ask / worst trade: `{prior['entries']} / {prior['entry_win_rate']} / {prior['avg_entry_ask']} / {prior['worst_trade']}`",
        "",
        "## Best Variants",
        "",
    ]
    for family, result in payload["best_by_family"].items():
        summary = result["summary"]
        walk = payload["walk_forward"]["families"].get(family, {})
        holdout = walk.get("holdout_summary", {})
        lines.extend(
            [
                f"### {family} `{result['strategy_id']}`",
                "",
                f"- Status: {status_for(family, result, payload)}",
                f"- Theorem: {result['theorem']}",
                f"- Equation: `{result['equation']}`",
                f"- Full-sample best params: `{json.dumps(result['params'], sort_keys=True)}`",
                f"- Full-sample PnL / delta vs actual / delta vs no-stop / delta vs skip-all: `${summary['sim_pnl']}` / `${summary['delta_vs_actual']}` / `${summary['delta_vs_no_stop']}` / `${summary['delta_vs_no_trade_all']}`",
                f"- Entries / skipped winners / skipped losers / win rate: `{summary['entries']} / {summary['skipped_settlement_winners']} / {summary['skipped_settlement_losers']} / {summary['entry_win_rate']}`",
                f"- Avg entry ask / elapsed / avg score / contract fraction: `{summary['avg_entry_ask']} / {summary['avg_entry_elapsed']} / {summary['avg_score']} / {summary['contract_fraction']}`",
                f"- Train-selected params: `{json.dumps(walk.get('selected_params'), sort_keys=True)}`",
                f"- Train-selected holdout PnL / delta vs actual / delta vs no-stop / delta vs skip-all: `${holdout.get('sim_pnl')}` / `${holdout.get('delta_vs_actual')}` / `${holdout.get('delta_vs_no_stop')}` / `${holdout.get('delta_vs_no_trade_all')}`",
                f"- Holdout entries / skipped winners / skipped losers / win rate: `{holdout.get('entries')} / {holdout.get('skipped_settlement_winners')} / {holdout.get('skipped_settlement_losers')} / {holdout.get('entry_win_rate')}`",
            ]
        )
        by_dataset = result.get("by_dataset", {})
        if by_dataset:
            lines.append(
                "- By dataset: `"
                + "; ".join(f"{dataset}: ${item['sim_pnl']} ({item['entries']} entries)" for dataset, item in sorted(by_dataset.items()))
                + "`"
            )
        by_side = result.get("by_side", {})
        if by_side:
            lines.append(
                "- By side: `"
                + "; ".join(f"{side}: ${item['sim_pnl']} ({item['entries']} entries)" for side, item in sorted(by_side.items()))
                + "`"
            )
        lines.append("")
    lines.extend(
        [
            "## Polarity Check",
            "",
            "- `yes_up` means YES receives positive credit from upward BTC movement and NO from downward movement.",
            "- `yes_down` is the inverted sanity check; if it wins, the side mapping assumption is suspect.",
        ]
    )
    for family, rows in payload["polarity_best"].items():
        lines.append(f"- `{family}`: `{json.dumps(rows, sort_keys=True)}`")
    lines.extend(
        [
            "",
            "## Robust Positive Split Scan",
            "",
            "| Family | Strategy | Train PnL | Holdout PnL | Holdout entries | Holdout win rate | Params |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for family, rows in payload["robust_positive_scan"].items():
        if not rows:
            lines.append(f"| `{family}` | none |  |  |  |  | no train-positive and holdout-positive parameterization found |")
            continue
        for row in rows[:8]:
            lines.append(
                f"| `{family}` | `{row['strategy_id']}` | {row['train_sim_pnl']} | {row['holdout_sim_pnl']} | "
                f"{row['holdout_entries']} | {row['holdout_entry_win_rate']} | `{json.dumps(row['params'], sort_keys=True)}` |"
            )
    lines.extend(
        [
            "",
            "## Nearby Sensitivity",
            "",
            "| Family | Params | PnL | Entries | Win rate | Avg ask |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for family, rows in payload["sensitivity"].items():
        for row in rows[:8]:
            lines.append(
                f"| `{family}` | `{json.dumps(row['params'], sort_keys=True)}` | {row['sim_pnl']} | "
                f"{row['entries']} | {row['entry_win_rate']} | {row['avg_entry_ask']} |"
            )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This validates the previous BTC synthetic EV idea on a much wider sample, but the data source changed from sub-minute feature rows to closed 1-minute candles.",
            "- The locked prior rule is the cleanest validation target; the optimized variants are useful for research direction but should be judged by holdout and polarity stability.",
            "- Any live consideration still needs market-definition verification for side mapping and a pre-registered forward test.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Broader validation and variant search for BTC spot synthetic EV entry admission.")
    parser.add_argument("--refresh-cache", action="store_true")
    parser.add_argument("--datasets", nargs="*", default=None)
    args = parser.parse_args()

    datasets = args.datasets or discover_datasets()
    payloads = [load_dataset_cases(dataset, refresh_cache=False) for dataset in datasets]
    cases: list[dict[str, Any]] = []
    for payload in payloads:
        dataset = payload.get("dataset")
        for case in payload.get("cases", []):
            case.setdefault("dataset", dataset)
            cases.append(case)
    cases = sorted(cases, key=lambda item: (item["entry_ts"], item["market"], item["side"]))

    candles = load_or_fetch_candles(cases, refresh_cache=args.refresh_cache)
    strategies = build_strategy_grid()
    locked_prior = StrategySpec(
        "btc_spot_synthetic_ev_broad_validation",
        "Locked prior from the 129-case feature-row run, replayed on broad closed-candle BTC features.",
        "q=sigmoid(c+a*s*move/sqrt(R15)+b*s*location+r*s*rsi-rho*R15/100-lambda*p_opp-mu*spread); EV=100*q-H-fee.",
        dict(PRIOR_SYNTHETIC_EV_PARAMS),
        sim_btc_spot_synthetic_ev_broad,
    )
    all_specs = [locked_prior, *strategies]
    delays = tuple(sorted({int(strategy.params["delay_seconds"]) for strategy in all_specs}))
    prepped_all = [(case, prepare_case(case, candles, delays)) for case in cases]
    prepped = [(case, prepared) for case, prepared in prepped_all if any(value is not None for value in prepared.values())]

    results = [run_strategy(prepped, strategy) for strategy in strategies]
    best_by_family = select_family_best(results)
    walk = walk_forward_summary(prepped, strategies)
    robust_scan = robust_positive_scan(prepped, strategies, results, max_candidates_per_family=350)
    locked_prior_result = run_strategy(prepped, locked_prior)
    sens = sensitivity(results, best_by_family)
    polarity_best = {
        family: polarity_counts(results, family)
        for family in sorted({result["family"] for result in results})
    }

    generated_at = datetime.now(UTC).isoformat()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"btc_spot_synthetic_ev_broad_validation_{stamp}.json"
    md_path = EDGE_DIR / f"btc_spot_synthetic_ev_broad_validation_{stamp}.md"
    latest_json = EDGE_DIR / "btc_spot_synthetic_ev_broad_validation_latest.json"
    latest_md = EDGE_DIR / "btc_spot_synthetic_ev_broad_validation_latest.md"

    report_payload = {
        "generated_at": generated_at,
        "dataset": "all_quote_path_trades_with_closed_1m_btc",
        "datasets": sorted({str(case.get("dataset")) for case, _prepared in prepped}),
        "requested_datasets": datasets,
        "dataset_payloads": [
            {
                "dataset": payload.get("dataset"),
                "raw_trades_total": payload.get("raw_trades_total"),
                "trades_total": payload.get("trades_total"),
                "case_count": len(payload.get("cases", [])),
                "cache_path": payload.get("cache_path"),
            }
            for payload in payloads
        ],
        "case_count": len(prepped),
        "raw_case_count": len(cases),
        "strategy_count": len(strategies),
        "btc_candle_source": "Binance public 1m candles; latest closed candle before quote snapshot target",
        "baselines": baseline_payload([case for case, _prepared in prepped]),
        "locked_prior_result": locked_prior_result,
        "best_by_family": best_by_family,
        "walk_forward": walk,
        "robust_positive_scan": robust_scan,
        "sensitivity": sens,
        "polarity_best": polarity_best,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "feature_availability": {
            "btc_spot_synthetic_ev_broad_validation": "quote heartbeat snapshot plus latest fully closed 1m BTC candle before decision time",
            "btc_spot_ev_dwell_combo_broad": "same broad BTC candle features plus quote-path quality dwell through the simulated delay",
        },
        "live_logic_changed": False,
    }

    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(report_payload, indent=2, sort_keys=True)
    json_path.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")
    write_markdown(md_path, report_payload)
    write_markdown(latest_md, report_payload)

    ledger_records: list[dict[str, Any]] = []
    for family, result in best_by_family.items():
        walk_family = walk["families"].get(family, {})
        ledger_records.append(
            {
                "recorded_at": generated_at,
                "generated_at": generated_at,
                "source": Path(__file__).name,
                "status": status_for(family, result, report_payload),
                "dataset": report_payload["dataset"],
                "datasets": report_payload["datasets"],
                "family": family,
                "theorem": result["theorem"],
                "equation": result["equation"],
                "params": result["params"],
                "strategy_id": result["strategy_id"],
                "idea_key": idea_key(family, result["equation"], result["params"]),
                "summary": result["summary"],
                "train_summary": walk_family.get("train_summary"),
                "holdout_summary": walk_family.get("holdout_summary"),
                "walk_forward_selected_strategy_id": walk_family.get("selected_strategy_id"),
                "walk_forward_selected_params": walk_family.get("selected_params"),
                "robust_positive_count": len(robust_scan.get(family, [])),
                "json_path": str(json_path),
                "markdown_path": str(md_path),
            }
        )
    append_ledger(ledger_records)
    update_strategy_memory(report_payload, best_by_family)

    print(f"Saved JSON: {json_path}")
    print(f"Saved Markdown: {md_path}")
    print(f"Cases={len(prepped)} raw_cases={len(cases)} strategies={len(strategies)}")
    prior_summary = locked_prior_result["summary"]
    print(
        f"locked_prior {locked_prior_result['strategy_id']} sim={prior_summary['sim_pnl']} "
        f"delta_actual={prior_summary['delta_vs_actual']} delta_skip={prior_summary['delta_vs_no_trade_all']} "
        f"entries={prior_summary['entries']}"
    )
    for family, result in best_by_family.items():
        summary = result["summary"]
        holdout = walk["families"].get(family, {}).get("holdout_summary", {})
        print(
            f"{family} {result['strategy_id']} status={status_for(family, result, report_payload)} "
            f"full_sim={summary['sim_pnl']} full_delta_actual={summary['delta_vs_actual']} "
            f"full_delta_skip={summary['delta_vs_no_trade_all']} entries={summary['entries']} "
            f"holdout_sim={holdout.get('sim_pnl')} holdout_delta_skip={holdout.get('delta_vs_no_trade_all')} "
            f"holdout_entries={holdout.get('entries')}"
        )


if __name__ == "__main__":
    main()
