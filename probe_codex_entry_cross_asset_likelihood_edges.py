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
from research_pipeline import dataset_paths, load_parquet_tree


UTC = timezone.utc


@dataclass(frozen=True)
class StrategySpec:
    family: str
    theorem: str
    equation: str
    params: dict[str, Any]
    scope: str
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


def logit_from_cents(cents: float) -> float:
    p = clamp(cents / 100.0, 0.001, 0.999)
    return math.log(p / (1.0 - p))


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


def quote_gate(point: dict[str, Any], params: dict[str, Any]) -> bool:
    held_ask = safe_float(point.get("held_ask"))
    pressure = safe_float(point.get("pressure"))
    bid_sum = safe_float(point.get("bid_sum"))
    spread = safe_float(point.get("spread"))
    if any(math.isnan(value) for value in (held_ask, pressure, bid_sum, spread)):
        return False
    return (
        held_ask <= float(params["max_entry_ask"])
        and pressure <= float(params["max_opp_pressure"])
        and bid_sum >= float(params["min_bid_sum"])
        and spread <= float(params["max_spread"])
    )


def quote_history_features(history: list[dict[str, float]]) -> dict[str, Any] | None:
    if len(history) < 2:
        return None
    first = history[0]
    last = history[-1]
    asks = [point["held_ask"] for point in history]
    logits = [logit_from_cents(ask) for ask in asks]
    dlogits = [logits[idx] - logits[idx - 1] for idx in range(1, len(logits))]
    dasks = [asks[idx] - asks[idx - 1] for idx in range(1, len(asks))]
    span = max(1.0, last["elapsed"] - first["elapsed"])
    nonzero_moves = [move for move in dasks if abs(move) > 1e-9]
    return {
        **last,
        "points": history,
        "span": span,
        "point_count": len(history),
        "state_changes": len(nonzero_moves),
        "start_ask": first["held_ask"],
        "net_ask": last["held_ask"] - first["held_ask"],
        "ask_range": max(asks) - min(asks),
        "net_logit": logits[-1] - logits[0],
        "qv_logit": sum(move * move for move in dlogits),
        "realized_abs_logit": sum(abs(move) for move in dlogits),
        "mean_pressure": mean([point["pressure"] for point in history]),
        "mean_spread": mean([point["spread"] for point in history]),
    }


def prepare_quote_case(case: dict[str, Any], delays: tuple[int, ...]) -> dict[str, Any]:
    path = [point for point in (compact_quote_point(raw) for raw in case.get("path", [])) if point is not None]
    path = sorted(path, key=lambda point: point["elapsed"])
    snapshots: dict[str, dict[str, Any] | None] = {}
    for delay in delays:
        history: list[dict[str, float]] = []
        for point in path:
            history.append(point)
            if point["elapsed"] >= delay:
                break
        if not history or history[-1]["elapsed"] < delay:
            snapshots[str(delay)] = None
            continue
        snapshots[str(delay)] = quote_history_features(history)
    return snapshots


def load_feature_bundles(dataset: str) -> dict[str, dict[str, Any]]:
    paths = dataset_paths(dataset)
    features = load_parquet_tree(paths["features_root"])
    if features.empty or "market_ticker" not in features.columns or "ts" not in features.columns:
        return {}
    features = features.copy()
    features["ts"] = pd.to_datetime(features["ts"], utc=True, errors="coerce")
    features = features[features["ts"].notna()].sort_values(["market_ticker", "ts"])
    columns = [
        "ts",
        "yes_bid_cents",
        "yes_ask_cents",
        "no_bid_cents",
        "no_ask_cents",
        "yes_bid_size",
        "no_bid_size",
        "btc_move_1m_bps",
        "btc_move_5m_bps",
        "btc_move_15m_bps",
        "btc_range_15m_bps",
        "btc_distance_to_15m_high_bps",
        "btc_distance_to_15m_low_bps",
        "btc_rsi14",
        "btc_macd_hist",
        "btc_price_vs_ema21",
    ]
    available = [column for column in columns if column in features.columns]
    bundles: dict[str, dict[str, Any]] = {}
    for market, group in features.groupby("market_ticker", sort=False):
        compact = group[available].sort_values("ts").reset_index(drop=True)
        bundles[str(market)] = {
            "ts_ns": compact["ts"].astype("int64").to_numpy(),
            "rows": compact.to_dict("records"),
        }
    return bundles


def feature_snapshot_for_case(
    case: dict[str, Any],
    delay_seconds: int,
    feature_by_market: dict[str, dict[str, Any]],
    *,
    tolerance_seconds: float = 2.0,
) -> dict[str, Any] | None:
    market = str(case.get("market") or "")
    bundle = feature_by_market.get(market)
    if not bundle:
        return None
    target = pd.Timestamp(case["entry_ts"]) + pd.Timedelta(seconds=int(delay_seconds))
    if target.tzinfo is None:
        target = target.tz_localize("UTC")
    else:
        target = target.tz_convert("UTC")
    idx = int(bundle["ts_ns"].searchsorted(target.value, side="right") - 1)
    if idx < 0:
        return None
    row = bundle["rows"][idx]
    row_ts = row.get("ts")
    if pd.isna(row_ts):
        return None
    age_seconds = (target - pd.Timestamp(row_ts)).total_seconds()
    if age_seconds < 0 or age_seconds > tolerance_seconds:
        return None

    side = str(case.get("side") or "").lower()
    yes_bid = safe_float(row.get("yes_bid_cents"))
    no_bid = safe_float(row.get("no_bid_cents"))
    yes_ask = safe_float(row.get("yes_ask_cents"))
    no_ask = safe_float(row.get("no_ask_cents"))
    yes_size = safe_float(row.get("yes_bid_size"))
    no_size = safe_float(row.get("no_bid_size"))
    if side == "yes":
        own_bid, opp_bid, held_ask = yes_bid, no_bid, yes_ask
        own_depth, opp_depth = yes_size, no_size
        side_sign = 1.0
    else:
        own_bid, opp_bid, held_ask = no_bid, yes_bid, no_ask
        own_depth, opp_depth = no_size, yes_size
        side_sign = -1.0
    if any(math.isnan(value) for value in (own_bid, opp_bid, held_ask)):
        return None
    return {
        "elapsed": float(delay_seconds),
        "target_ts": target.isoformat(),
        "feature_age_seconds": age_seconds,
        "own_bid": own_bid,
        "opp_bid": opp_bid,
        "held_ask": held_ask,
        "bid_sum": own_bid + opp_bid,
        "spread": held_ask - own_bid,
        "pressure": pressure_from_values(own_bid, opp_bid),
        "own_depth": own_depth,
        "opp_depth": opp_depth,
        "side_sign": side_sign,
        "btc_move_1m_bps": safe_float(row.get("btc_move_1m_bps")),
        "btc_move_5m_bps": safe_float(row.get("btc_move_5m_bps")),
        "btc_move_15m_bps": safe_float(row.get("btc_move_15m_bps")),
        "btc_range_15m_bps": safe_float(row.get("btc_range_15m_bps")),
        "btc_distance_to_15m_high_bps": safe_float(row.get("btc_distance_to_15m_high_bps")),
        "btc_distance_to_15m_low_bps": safe_float(row.get("btc_distance_to_15m_low_bps")),
        "btc_rsi14": safe_float(row.get("btc_rsi14")),
        "btc_macd_hist": safe_float(row.get("btc_macd_hist")),
        "btc_price_vs_ema21": safe_float(row.get("btc_price_vs_ema21")),
    }


def prepare_feature_cases(
    cases: list[dict[str, Any]],
    delays: tuple[int, ...],
    dataset: str,
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    bundles = load_feature_bundles(dataset)
    if not bundles:
        return []
    prepped: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for case in cases:
        if str(case.get("dataset")) != dataset:
            continue
        snapshots = {str(delay): feature_snapshot_for_case(case, delay, bundles) for delay in delays}
        if any(snapshot is not None for snapshot in snapshots.values()):
            prepped.append((case, snapshots))
    return prepped


def entry_meta(case: dict[str, Any], features: dict[str, Any], extra: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    ask = float(features["held_ask"])
    return delayed_entry_pnl(case, ask), {
        "enter": True,
        "entry_ask": ask,
        "entry_elapsed": float(features["elapsed"]),
        "contracts": int(case["qty"]),
        "pressure": round(float(features["pressure"]), 6),
        "spread": round(float(features["spread"]), 4),
        "bid_sum": round(float(features["bid_sum"]), 4),
        **extra,
    }


def side_move_score(features: dict[str, Any], params: dict[str, Any]) -> float:
    side_sign = safe_float(features.get("side_sign"))
    move_1m = safe_float(features.get("btc_move_1m_bps"))
    move_5m = safe_float(features.get("btc_move_5m_bps"))
    move_15m = safe_float(features.get("btc_move_15m_bps"))
    btc_range = max(1.0, safe_float(features.get("btc_range_15m_bps")))
    if any(math.isnan(value) for value in (side_sign, move_1m, move_5m, move_15m, btc_range)):
        return math.nan
    weighted_move = (
        float(params.get("w_1m", 0.0)) * move_1m
        + float(params.get("w_5m", 0.0)) * move_5m
        + float(params.get("w_15m", 0.0)) * move_15m
    )
    return side_sign * weighted_move / math.sqrt(btc_range)


def side_location_score(features: dict[str, Any]) -> float:
    side_sign = safe_float(features.get("side_sign"))
    dist_high = safe_float(features.get("btc_distance_to_15m_high_bps"))
    dist_low = safe_float(features.get("btc_distance_to_15m_low_bps"))
    btc_range = max(1.0, safe_float(features.get("btc_range_15m_bps")))
    if any(math.isnan(value) for value in (side_sign, dist_high, dist_low, btc_range)):
        return math.nan
    return side_sign * (dist_low - dist_high) / btc_range


def side_rsi_score(features: dict[str, Any]) -> float:
    side_sign = safe_float(features.get("side_sign"))
    rsi = safe_float(features.get("btc_rsi14"))
    if any(math.isnan(value) for value in (side_sign, rsi)):
        return 0.0
    return side_sign * (rsi - 50.0) / 20.0


def side_macd_score(features: dict[str, Any]) -> float:
    side_sign = safe_float(features.get("side_sign"))
    macd_hist = safe_float(features.get("btc_macd_hist"))
    if any(math.isnan(value) for value in (side_sign, macd_hist)):
        return 0.0
    return side_sign * macd_hist / 20.0


def sim_girsanov_drift_likelihood_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not quote_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    if int(features["state_changes"]) < int(params["min_state_changes"]):
        return 0.0, {"enter": False, "skip_reason": "too_few_state_changes"}
    theta = float(params["theta"])
    qv = float(features["qv_logit"]) + float(params["variance_floor"])
    score = (
        theta * float(features["net_logit"])
        - 0.5 * theta * theta * qv
        - float(params["pressure_penalty"]) * float(features["pressure"])
        - float(params["spread_penalty"]) * float(features["spread"])
        - float(params["range_penalty"]) * float(features["ask_range"]) / 100.0
    )
    if score < float(params["min_log_likelihood"]):
        return 0.0, {"enter": False, "skip_reason": "likelihood_too_low", "score": round(score, 6)}
    return entry_meta(
        case,
        features,
        {
            "score": round(score, 6),
            "net_logit": round(float(features["net_logit"]), 6),
            "qv_logit": round(float(features["qv_logit"]), 6),
            "state_changes": int(features["state_changes"]),
            "ask_range": round(float(features["ask_range"]), 4),
        },
    )


def sim_btc_momentum_concordance_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not quote_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    move_score = side_move_score(features, params)
    if math.isnan(move_score):
        return 0.0, {"enter": False, "skip_reason": "missing_btc_momentum"}
    score = (
        move_score
        + float(params["rsi_weight"]) * side_rsi_score(features)
        + float(params["macd_weight"]) * side_macd_score(features)
        - float(params["range_penalty"]) * safe_float(features.get("btc_range_15m_bps")) / 100.0
        - float(params["pressure_penalty"]) * safe_float(features.get("pressure"))
        - float(params["spread_penalty"]) * safe_float(features.get("spread"))
    )
    if score < float(params["min_score"]):
        return 0.0, {"enter": False, "skip_reason": "btc_momentum_too_low", "score": round(score, 6)}
    return entry_meta(
        case,
        features,
        {
            "score": round(score, 6),
            "side_move_score": round(move_score, 6),
            "side_rsi_score": round(side_rsi_score(features), 6),
            "side_macd_score": round(side_macd_score(features), 6),
            "btc_range_15m_bps": round(safe_float(features.get("btc_range_15m_bps")), 6),
        },
    )


def sim_btc_range_location_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not quote_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    location = side_location_score(features)
    btc_range = safe_float(features.get("btc_range_15m_bps"))
    if any(math.isnan(value) for value in (location, btc_range)):
        return 0.0, {"enter": False, "skip_reason": "missing_btc_location"}
    if btc_range > float(params["max_btc_range_bps"]):
        return 0.0, {"enter": False, "skip_reason": "btc_range_too_wide", "score": round(location, 6)}
    score = (
        location
        - float(params["range_penalty"]) * btc_range / 100.0
        - float(params["pressure_penalty"]) * safe_float(features.get("pressure"))
        - float(params["spread_penalty"]) * safe_float(features.get("spread"))
    )
    if location < float(params["min_location"]) or score < float(params["min_score"]):
        return 0.0, {"enter": False, "skip_reason": "btc_location_too_low", "score": round(score, 6)}
    return entry_meta(
        case,
        features,
        {
            "score": round(score, 6),
            "location": round(location, 6),
            "btc_range_15m_bps": round(btc_range, 6),
            "distance_to_high_bps": round(safe_float(features.get("btc_distance_to_15m_high_bps")), 6),
            "distance_to_low_bps": round(safe_float(features.get("btc_distance_to_15m_low_bps")), 6),
        },
    )


def sim_btc_spot_synthetic_ev_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not quote_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    move = side_move_score(features, params)
    location = side_location_score(features)
    btc_range = safe_float(features.get("btc_range_15m_bps"))
    if any(math.isnan(value) for value in (move, location, btc_range)):
        return 0.0, {"enter": False, "skip_reason": "missing_btc_ev_features"}
    z = (
        float(params["intercept"])
        + float(params["move_scale"]) * move
        + float(params["location_weight"]) * location
        + float(params["rsi_weight"]) * side_rsi_score(features)
        + float(params["macd_weight"]) * side_macd_score(features)
        - float(params["range_penalty"]) * btc_range / 100.0
        - float(params["pressure_penalty"]) * safe_float(features.get("pressure"))
        - float(params["spread_penalty"]) * safe_float(features.get("spread"))
    )
    q_spot = sigmoid(z)
    ask = safe_float(features.get("held_ask"))
    fee_per_contract = estimated_order_fee_cents(ask, max(1, int(case["qty"]))) / max(1, int(case["qty"]))
    ev_cents = 100.0 * q_spot - ask - fee_per_contract
    if ev_cents < float(params["min_ev_cents"]):
        return 0.0, {
            "enter": False,
            "skip_reason": "spot_synthetic_ev_too_low",
            "score": round(ev_cents, 6),
        }
    return entry_meta(
        case,
        features,
        {
            "score": round(ev_cents, 6),
            "q_spot": round(q_spot, 6),
            "z": round(z, 6),
            "side_move_score": round(move, 6),
            "side_location_score": round(location, 6),
            "fee_per_contract": round(fee_per_contract, 6),
        },
    )


def build_strategy_grid() -> list[StrategySpec]:
    strategies: list[StrategySpec] = []

    def add(
        family: str,
        theorem: str,
        equation: str,
        params: dict[str, Any],
        scope: str,
        simulator: Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], tuple[float, dict[str, Any]]],
    ) -> None:
        strategies.append(StrategySpec(family, theorem, equation, params, scope, simulator))

    girsanov_theorem = (
        "A high-priced entry should look like a positive drift likelihood under the observed quote path, not merely "
        "a large final quote; stochastic variance in the path is a cost because noisy favorable prints reverse more often."
    )
    girsanov_equation = (
        "G=theta*(logit(H_D)-logit(H_0))-0.5*theta^2*sum(dlogit(H)^2)"
        "-lambda*p_opp-mu*spread-rho*range/100; enter if quote gates pass and G>=g."
    )
    for delay_seconds in (30, 60, 120, 180):
        for max_entry_ask in (88, 90, 92):
            for max_opp_pressure in (0.30, 0.50):
                for max_spread in (4, 10):
                    for theta in (0.50, 1.00, 1.50):
                        for min_log_likelihood in (-0.50, 0.0, 0.25):
                            for min_state_changes in (1, 3):
                                add(
                                    "girsanov_drift_likelihood_admission",
                                    girsanov_theorem,
                                    girsanov_equation,
                                    {
                                        "delay_seconds": delay_seconds,
                                        "max_entry_ask": max_entry_ask,
                                        "max_opp_pressure": max_opp_pressure,
                                        "min_bid_sum": 0,
                                        "max_spread": max_spread,
                                        "theta": theta,
                                        "variance_floor": 0.0005,
                                        "min_log_likelihood": min_log_likelihood,
                                        "min_state_changes": min_state_changes,
                                        "pressure_penalty": 0.5,
                                        "spread_penalty": 0.03,
                                        "range_penalty": 0.5,
                                    },
                                    "quote_path",
                                    sim_girsanov_drift_likelihood_admission,
                                )

    momentum_theorem = (
        "If YES behaves like the upside contract and NO like the downside contract, a marketable entry should be "
        "confirmed by same-direction BTC spot momentum after normalizing by current 15-minute spot range."
    )
    momentum_equation = (
        "M=s*(w1*m1+w5*m5+w15*m15)/sqrt(R_15)+a*s*(RSI-50)/20+b*s*MACD_hist/20"
        "-lambda*p_opp-mu*spread-rho*R_15/100; enter if M>=m."
    )
    for delay_seconds in (0, 30, 60, 120):
        for max_entry_ask in (90, 92, 94):
            for max_opp_pressure in (0.30, 0.50):
                for max_spread in (4, 10):
                    for weights in (
                        {"w_1m": 0.0, "w_5m": 1.0, "w_15m": 0.0},
                        {"w_1m": 0.5, "w_5m": 1.0, "w_15m": 0.0},
                        {"w_1m": 0.0, "w_5m": 0.5, "w_15m": 1.0},
                    ):
                        for min_score in (-1.0, 0.0, 0.5, 1.0):
                            add(
                                "btc_momentum_concordance_admission",
                                momentum_theorem,
                                momentum_equation,
                                {
                                    "delay_seconds": delay_seconds,
                                    "max_entry_ask": max_entry_ask,
                                    "max_opp_pressure": max_opp_pressure,
                                    "min_bid_sum": 0,
                                    "max_spread": max_spread,
                                    **weights,
                                    "min_score": min_score,
                                    "rsi_weight": 0.25,
                                    "macd_weight": 0.10,
                                    "range_penalty": 0.25,
                                    "pressure_penalty": 0.5,
                                    "spread_penalty": 0.03,
                                },
                                "feature_spot_btc",
                                sim_btc_momentum_concordance_admission,
                            )

    location_theorem = (
        "A side is healthier when BTC spot is located near the corresponding extreme of its current 15-minute range: "
        "YES near the high, NO near the low. Wide ranges should pay a reserve penalty."
    )
    location_equation = (
        "L=s*(dist_low-dist_high)/(R_15+eps)-rho*R_15/100-lambda*p_opp-mu*spread; "
        "enter if L>=l, location>=ell, and R_15<=Rmax."
    )
    for delay_seconds in (0, 30, 60, 120):
        for max_entry_ask in (90, 92, 94):
            for max_opp_pressure in (0.30, 0.50):
                for max_spread in (4, 10):
                    for min_location in (0.0, 0.25, 0.50):
                        for max_btc_range_bps in (40, 60, 1000):
                            for min_score in (-0.50, 0.0, 0.20):
                                add(
                                    "btc_range_location_admission",
                                    location_theorem,
                                    location_equation,
                                    {
                                        "delay_seconds": delay_seconds,
                                        "max_entry_ask": max_entry_ask,
                                        "max_opp_pressure": max_opp_pressure,
                                        "min_bid_sum": 0,
                                        "max_spread": max_spread,
                                        "min_location": min_location,
                                        "max_btc_range_bps": max_btc_range_bps,
                                        "min_score": min_score,
                                        "range_penalty": 0.25,
                                        "pressure_penalty": 0.5,
                                        "spread_penalty": 0.03,
                                    },
                                    "feature_spot_btc",
                                    sim_btc_range_location_admission,
                                )

    spot_ev_theorem = (
        "BTC spot state can be treated as an independent synthetic probability check; enter only when the logistic "
        "spot-implied probability clears the delayed ask after fees and book friction."
    )
    spot_ev_equation = (
        "q=sigmoid(c+a*s*move/sqrt(R_15)+b*s*(dist_low-dist_high)/R_15+r*s*(RSI-50)/20"
        "-rho*R_15/100-lambda*p_opp-mu*spread); EV=100*q-H_D-fee; enter if EV>=e."
    )
    for delay_seconds in (0, 30, 60, 120):
        for max_entry_ask in (90, 92, 94):
            for max_opp_pressure in (0.30, 0.50):
                for max_spread in (4, 10):
                    for intercept in (1.5, 2.0, 2.5):
                        for move_scale in (0.25, 0.50, 1.0):
                            for location_weight in (0.50, 1.0):
                                for min_ev_cents in (-5.0, 0.0, 2.0):
                                    add(
                                        "btc_spot_synthetic_ev_admission",
                                        spot_ev_theorem,
                                        spot_ev_equation,
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
                                            "rsi_weight": 0.15,
                                            "macd_weight": 0.0,
                                            "range_penalty": 0.25,
                                            "pressure_penalty": 0.5,
                                            "spread_penalty": 0.03,
                                            "min_ev_cents": min_ev_cents,
                                        },
                                        "feature_spot_btc",
                                        sim_btc_spot_synthetic_ev_admission,
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


def run_strategy(
    prepped_by_scope: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]],
    strategy: StrategySpec,
) -> dict[str, Any]:
    sid = strategy_id(strategy.family, strategy.params)
    rows: list[dict[str, Any]] = []
    for case, prepared in prepped_by_scope[strategy.scope]:
        pnl, meta = strategy.simulator(case, prepared, strategy.params)
        rows.append(row_for(case, pnl, meta, sid))
    return {
        "strategy_id": sid,
        "family": strategy.family,
        "theorem": strategy.theorem,
        "equation": strategy.equation,
        "params": strategy.params,
        "scope": strategy.scope,
        "summary": summarize_entry_rows(sid, rows),
        "by_dataset": summarize_by_group(sid, rows, "dataset"),
        "by_side": summarize_by_group(sid, rows, "side"),
        "by_day": summarize_by_group(sid, rows, "entry_day_et"),
        "interesting_examples": sorted(rows, key=lambda row: (float(row["sim_pnl"]), row["market"]))[:10],
    }


def min_entries_for_scope(scope: str, *, holdout: bool = False) -> int:
    if scope == "feature_spot_btc":
        return 3 if holdout else 5
    return 5 if holdout else 10


def select_family_best(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for family in sorted({result["family"] for result in results}):
        family_results = [result for result in results if result["family"] == family]
        scope = str(family_results[0]["scope"])
        candidates = [
            result for result in family_results if result["summary"]["entries"] >= min_entries_for_scope(scope)
        ] or family_results
        output[family] = max(
            candidates,
            key=lambda result: (
                result["summary"]["sim_pnl"],
                result["summary"]["entry_win_rate"],
                -(result["summary"]["avg_entry_ask"] or 0.0),
            ),
        )
    return output


def run_on_subset(prepped: list[tuple[dict[str, Any], dict[str, Any]]], strategy: StrategySpec) -> dict[str, Any]:
    return run_strategy({strategy.scope: prepped}, strategy)


def walk_forward_summary(
    prepped_by_scope: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]],
    strategies: list[StrategySpec],
) -> dict[str, Any]:
    output: dict[str, Any] = {"families": {}}
    for family in sorted({strategy.family for strategy in strategies}):
        family_strategies = [strategy for strategy in strategies if strategy.family == family]
        scope = family_strategies[0].scope
        ordered = sorted(prepped_by_scope[scope], key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
        split = int(len(ordered) * 0.7)
        train = ordered[:split]
        holdout = ordered[split:]
        train_results = [run_on_subset(train, strategy) for strategy in family_strategies]
        selected = select_family_best(train_results).get(family) or max(train_results, key=lambda result: result["summary"]["sim_pnl"])
        selected_spec = next(
            strategy
            for strategy in family_strategies
            if strategy_id(strategy.family, strategy.params) == selected["strategy_id"]
        )
        holdout_result = run_on_subset(holdout, selected_spec)
        output["families"][family] = {
            "scope": scope,
            "train_n": len(train),
            "holdout_n": len(holdout),
            "split_entry_ts": ordered[split][0]["entry_ts"] if holdout else None,
            "selected_strategy_id": selected["strategy_id"],
            "selected_params": selected["params"],
            "train_summary": selected["summary"],
            "holdout_summary": holdout_result["summary"],
            "holdout_by_dataset": holdout_result["by_dataset"],
            "holdout_by_side": holdout_result["by_side"],
        }
    return output


def robust_positive_scan(
    prepped_by_scope: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]],
    strategies: list[StrategySpec],
) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    for family in sorted({strategy.family for strategy in strategies}):
        family_strategies = [strategy for strategy in strategies if strategy.family == family]
        scope = family_strategies[0].scope
        ordered = sorted(prepped_by_scope[scope], key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
        split = int(len(ordered) * 0.7)
        train = ordered[:split]
        holdout = ordered[split:]
        rows: list[dict[str, Any]] = []
        for strategy in family_strategies:
            train_result = run_on_subset(train, strategy)
            holdout_result = run_on_subset(holdout, strategy)
            train_summary = train_result["summary"]
            holdout_summary = holdout_result["summary"]
            if (
                train_summary["sim_pnl"] <= 0
                or holdout_summary["sim_pnl"] <= 0
                or train_summary["entries"] < min_entries_for_scope(scope)
                or holdout_summary["entries"] < min_entries_for_scope(scope, holdout=True)
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
        )[:15]
    return output


def sensitivity(results: list[dict[str, Any]], best_by_family: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    for family, best in best_by_family.items():
        scope = str(best["scope"])
        ranked = sorted(
            [
                result
                for result in results
                if result["family"] == family and result["summary"]["entries"] >= min_entries_for_scope(scope)
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


def baseline_payload(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "actual": run_baseline(cases, "actual"),
        "no_stop": run_baseline(cases, "no_stop"),
        "held_ask_stop_70": run_baseline(cases, "held_ask_stop_70"),
        "no_trade_all": {"summary": {"sim_pnl": 0.0}},
    }


def status_for(family: str, result: dict[str, Any], payload: dict[str, Any]) -> str:
    holdout = payload["walk_forward"]["families"].get(family, {}).get("holdout_summary", {})
    robust_rows = payload["robust_positive_scan"].get(family, [])
    full = result["summary"]
    scope = str(result.get("scope"))
    if (
        full.get("delta_vs_no_trade_all", -999999.0) > 0.0
        and holdout.get("delta_vs_no_trade_all", -999999.0) > 0.0
        and len(robust_rows) >= 3
    ):
        if scope == "feature_spot_btc":
            return "watchlist_positive_limited_feature_sample"
        return "candidate_for_human_review"
    if full.get("delta_vs_no_trade_all", -999999.0) > 0.0 and robust_rows:
        return "watchlist_positive_but_selection_sensitive"
    if full.get("delta_vs_no_trade_all", -999999.0) > 0.0:
        return "watchlist_positive_but_not_robust"
    return "tested_negative"


def read_prior_entry_reference() -> dict[str, Any]:
    output: dict[str, Any] = {}
    for name in (
        "codex_entry_timing_research_latest.json",
        "codex_entry_path_geometry_research_latest.json",
        "codex_entry_clock_decay_research_latest.json",
        "codex_entry_logit_snr_research_latest.json",
        "codex_entry_microstructure_research_latest.json",
        "codex_entry_barrier_parity_research_latest.json",
        "codex_entry_side_switch_research_latest.json",
        "codex_entry_distribution_shape_research_latest.json",
        "codex_entry_occupation_posterior_research_latest.json",
    ):
        path = EDGE_DIR / name
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        output[name] = {
            family: {
                "strategy_id": result.get("strategy_id"),
                "sim_pnl": (result.get("summary") or {}).get("sim_pnl"),
                "holdout_sim_pnl": (
                    payload.get("walk_forward", {}).get("families", {}).get(family, {}).get("holdout_summary") or {}
                ).get("sim_pnl"),
            }
            for family, result in payload.get("best_by_family", {}).items()
        }
    return output


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    quote_base = payload["baselines_by_scope"]["quote_path"]
    feature_base = payload["baselines_by_scope"]["feature_spot_btc"]
    lines = [
        "# Codex Entry Cross-Asset Likelihood Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Quote-path datasets: `{', '.join(payload['datasets'])}`",
        f"- Quote-path cases: `{payload['scope_case_counts']['quote_path']}`",
        f"- BTC feature-covered cases: `{payload['scope_case_counts']['feature_spot_btc']}`",
        "- Scope: research-only entry/no-trade simulation; live entry logic, live exit logic, configs, run scripts, and bot processes were not changed.",
        "- Non-repetition: this tests stochastic quote-path drift likelihood and BTC spot directional/location confirmation, not fixed delayed gates, Kelly buckets, path occupation, CUSUM/Omega/CVaR, quote dwell/renewal, first-passage ruin, or depth-volatility reserve.",
        "",
        "## Baselines",
        "",
        f"- Quote-path actual / no-stop / first held-ask<=70 / skip-all: `${quote_base['actual']['summary']['sim_pnl']}` / `${quote_base['no_stop']['summary']['sim_pnl']}` / `${quote_base['held_ask_stop_70']['summary']['sim_pnl']}` / `$0.0`",
        f"- BTC-feature subset actual / no-stop / first held-ask<=70 / skip-all: `${feature_base['actual']['summary']['sim_pnl']}` / `${feature_base['no_stop']['summary']['sim_pnl']}` / `${feature_base['held_ask_stop_70']['summary']['sim_pnl']}` / `$0.0`",
        "",
        "## New Equation Families",
        "",
    ]
    for family, result in payload["best_by_family"].items():
        summary = result["summary"]
        walk = payload["walk_forward"]["families"].get(family, {})
        holdout = walk.get("holdout_summary", {})
        active_days = [item for item in result.get("by_day", {}).values() if item.get("entries", 0) > 0]
        positive_days = [item for item in active_days if item.get("sim_pnl", 0) > 0]
        lines.extend(
            [
                f"### {family} `{result['strategy_id']}`",
                "",
                f"- Status: {status_for(family, result, payload)}",
                f"- Scope: `{result['scope']}`",
                f"- Theorem: {result['theorem']}",
                f"- Equation: `{result['equation']}`",
                f"- Full-sample best params: `{json.dumps(result['params'], sort_keys=True)}`",
                f"- Full-sample PnL / delta vs actual / delta vs no-stop / delta vs skip-all: `${summary['sim_pnl']}` / `${summary['delta_vs_actual']}` / `${summary['delta_vs_no_stop']}` / `${summary['delta_vs_no_trade_all']}`",
                f"- Entries / skipped winners / skipped losers / win rate: `{summary['entries']} / {summary['skipped_settlement_winners']} / {summary['skipped_settlement_losers']} / {summary['entry_win_rate']}`",
                f"- Avg entry ask / elapsed / avg score / contract fraction: `{summary['avg_entry_ask']} / {summary['avg_entry_elapsed']} / {summary['avg_score']} / {summary['contract_fraction']}`",
                f"- Walk-forward split: `{walk.get('split_entry_ts')}`",
                f"- Train-selected params: `{json.dumps(walk.get('selected_params'), sort_keys=True)}`",
                f"- Train-selected holdout PnL / delta vs actual / delta vs no-stop / delta vs skip-all: `${holdout.get('sim_pnl')}` / `${holdout.get('delta_vs_actual')}` / `${holdout.get('delta_vs_no_stop')}` / `${holdout.get('delta_vs_no_trade_all')}`",
                f"- Holdout entries / skipped winners / skipped losers / win rate: `{holdout.get('entries')} / {holdout.get('skipped_settlement_winners')} / {holdout.get('skipped_settlement_losers')} / {holdout.get('entry_win_rate')}`",
                f"- Active days positive/active: `{len(positive_days)}/{len(active_days)}`",
            ]
        )
        by_dataset = result.get("by_dataset", {})
        by_side = result.get("by_side", {})
        if by_dataset:
            lines.append(
                "- By dataset: `"
                + "; ".join(f"{dataset}: ${item['sim_pnl']} ({item['entries']} entries)" for dataset, item in sorted(by_dataset.items()))
                + "`"
            )
        if by_side:
            lines.append(
                "- By side: `"
                + "; ".join(f"{side}: ${item['sim_pnl']} ({item['entries']} entries)" for side, item in sorted(by_side.items()))
                + "`"
            )
        lines.append("")
    lines.extend(
        [
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
        for row in rows[:5]:
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
        for row in rows[:6]:
            lines.append(
                f"| `{family}` | `{json.dumps(row['params'], sort_keys=True)}` | {row['sim_pnl']} | "
                f"{row['entries']} | {row['entry_win_rate']} | {row['avg_entry_ask']} |"
            )
    lines.extend(["", "## Prior Entry Reference", ""])
    prior = payload.get("prior_entry_reference") or {}
    if prior:
        for source, families in prior.items():
            for prior_family, item in families.items():
                lines.append(
                    f"- `{source}` `{prior_family}` `{item.get('strategy_id')}` full `${item.get('sim_pnl')}`, holdout `${item.get('holdout_sim_pnl')}`."
                )
    else:
        lines.append("- No prior entry reference JSON was available.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The Girsanov branch is a quote-path likelihood ratio: net log-odds drift must pay for quadratic variation, so noisy paths are penalized even when their final quote is high.",
            "- The BTC momentum branch is cross-asset confirmation: YES gets credit from upward spot movement and NO from downward spot movement, normalized by the current 15-minute BTC range.",
            "- The BTC range-location branch tests whether spot is near the side-consistent extreme of the current BTC range; the synthetic EV branch converts that spot state into a fee-adjusted probability check.",
            "- BTC feature results are limited by local feature coverage. Settlement labels are used only for scoring, not as strategy inputs.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only entry cross-asset and likelihood edge probes.")
    parser.add_argument("--refresh-cache", action="store_true")
    parser.add_argument("--datasets", nargs="*", default=None)
    args = parser.parse_args()

    datasets = args.datasets or discover_datasets()
    payloads = [load_dataset_cases(dataset, refresh_cache=args.refresh_cache) for dataset in datasets]
    all_cases: list[dict[str, Any]] = []
    for payload in payloads:
        dataset = payload.get("dataset")
        for case in payload.get("cases", []):
            case.setdefault("dataset", dataset)
            all_cases.append(case)
    all_cases = sorted(all_cases, key=lambda item: (item["entry_ts"], item["market"], item["side"]))

    strategies = build_strategy_grid()
    quote_delays = tuple(sorted({int(strategy.params["delay_seconds"]) for strategy in strategies if strategy.scope == "quote_path"}))
    feature_delays = tuple(sorted({int(strategy.params["delay_seconds"]) for strategy in strategies if strategy.scope == "feature_spot_btc"}))
    prepped_by_scope: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = {
        "quote_path": [(case, prepare_quote_case(case, quote_delays)) for case in all_cases],
        "feature_spot_btc": [],
    }
    for dataset in datasets:
        dataset_cases = [case for case in all_cases if str(case.get("dataset")) == dataset]
        prepped_by_scope["feature_spot_btc"].extend(prepare_feature_cases(dataset_cases, feature_delays, dataset))
    feature_cases = [case for case, _prepared in prepped_by_scope["feature_spot_btc"]]

    baselines_by_scope = {
        "quote_path": baseline_payload(all_cases),
        "feature_spot_btc": baseline_payload(feature_cases),
    }
    results = [run_strategy(prepped_by_scope, strategy) for strategy in strategies]
    best_by_family = select_family_best(results)
    walk = walk_forward_summary(prepped_by_scope, strategies)
    robust_scan = robust_positive_scan(prepped_by_scope, strategies)
    sens = sensitivity(results, best_by_family)

    generated_at = datetime.now(UTC).isoformat()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"codex_entry_cross_asset_likelihood_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_entry_cross_asset_likelihood_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_entry_cross_asset_likelihood_research_latest.json"
    latest_md = EDGE_DIR / "codex_entry_cross_asset_likelihood_research_latest.md"
    report_payload = {
        "generated_at": generated_at,
        "dataset": "all_quote_path_trades_plus_btc_feature_subset",
        "datasets": sorted({str(case.get("dataset")) for case in all_cases}),
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
        "scope_case_counts": {scope: len(rows) for scope, rows in prepped_by_scope.items()},
        "strategy_count": len(strategies),
        "baselines_by_scope": baselines_by_scope,
        "best_by_family": best_by_family,
        "walk_forward": walk,
        "robust_positive_scan": robust_scan,
        "sensitivity": sens,
        "prior_entry_reference": read_prior_entry_reference(),
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "feature_availability": {
            "girsanov_drift_likelihood_admission": "quote heartbeat path through the simulated delay",
            "btc_momentum_concordance_admission": "live feature rows with BTC 1m/5m/15m move, RSI, MACD, and book state through simulated delay",
            "btc_range_location_admission": "live feature rows with BTC distance to current 15m high/low and book state through simulated delay",
            "btc_spot_synthetic_ev_admission": "same BTC feature subset; deterministic logistic transform only, no label-trained coefficient fitting",
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
                "sample_scope": result["scope"],
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
    print(
        f"Scopes quote_path={len(prepped_by_scope['quote_path'])} "
        f"feature_spot_btc={len(prepped_by_scope['feature_spot_btc'])} "
        f"strategies={len(strategies)}"
    )
    for family, result in best_by_family.items():
        summary = result["summary"]
        holdout = walk["families"].get(family, {}).get("holdout_summary", {})
        print(
            f"{family} {result['strategy_id']} status={status_for(family, result, report_payload)} "
            f"scope={result['scope']} full_sim={summary['sim_pnl']} "
            f"full_delta_actual={summary['delta_vs_actual']} full_delta_skip={summary['delta_vs_no_trade_all']} "
            f"entries={summary['entries']} holdout_sim={holdout.get('sim_pnl')} "
            f"holdout_delta_actual={holdout.get('delta_vs_actual')} "
            f"holdout_delta_skip={holdout.get('delta_vs_no_trade_all')} "
            f"holdout_entries={holdout.get('entries')}"
        )


if __name__ == "__main__":
    main()
