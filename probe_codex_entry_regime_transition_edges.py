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
    ET,
    append_ledger,
    estimated_order_fee_cents,
    idea_key,
    result_distance,
    strategy_id,
    update_strategy_memory,
)
from research_pipeline import parse_market_close_from_ticker


UTC = timezone.utc
ROOT = Path(__file__).resolve().parent
ALL_LOOKBACK = 1000000


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


def mean(values: list[float]) -> float:
    clean = [value for value in values if not math.isnan(value)]
    return sum(clean) / len(clean) if clean else math.nan


def entropy01(probability: float) -> float:
    p = min(0.999999, max(0.000001, probability))
    return -(p * math.log(p) + (1.0 - p) * math.log(1.0 - p))


def parse_ts(value: Any) -> pd.Timestamp | None:
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        return None
    return pd.Timestamp(ts).tz_convert("UTC")


def market_close_ts(market: str, explicit_close: Any = None) -> pd.Timestamp | None:
    parsed = parse_ts(explicit_close)
    if parsed is not None:
        return parsed
    close_dt = parse_market_close_from_ticker(str(market or ""))
    if close_dt is None:
        return None
    return pd.Timestamp(close_dt).tz_convert("UTC")


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


def load_market_result_history(datasets: list[str]) -> list[dict[str, Any]]:
    by_market: dict[str, dict[str, Any]] = {}
    for dataset in datasets:
        path = ROOT / "stats" / dataset / "market_results.csv"
        if not path.exists():
            continue
        rows = pd.read_csv(path)
        for _, row in rows.iterrows():
            market = str(row.get("market") or "")
            result = str(row.get("result") or row.get("market_result") or "").lower().strip()
            if not market.startswith("KXBTC15M") or result not in {"yes", "no"}:
                continue
            close_ts = market_close_ts(market, row.get("close_time"))
            if close_ts is None:
                close_ts = market_close_ts(market, row.get("settlement_ts"))
            if close_ts is None:
                continue
            existing = by_market.get(market)
            item = {
                "market": market,
                "result": result,
                "close_ts": close_ts,
                "available_ts": close_ts + pd.Timedelta(seconds=30),
                "dataset": dataset,
            }
            if existing is None or close_ts < existing["close_ts"]:
                by_market[market] = item
    return sorted(by_market.values(), key=lambda item: (item["close_ts"], item["market"]))


def window_history(history: list[dict[str, Any]], decision_ts: pd.Timestamp, lookback: int) -> list[dict[str, Any]]:
    available = [row for row in history if row["available_ts"] <= decision_ts]
    if lookback >= ALL_LOOKBACK:
        return available
    return available[-int(lookback) :]


def trailing_streak(results: list[str]) -> tuple[str | None, int]:
    if not results:
        return None, 0
    last = results[-1]
    length = 0
    for value in reversed(results):
        if value != last:
            break
        length += 1
    return last, length


def streak_at(results: list[str], idx: int) -> int:
    value = results[idx]
    length = 0
    for pos in range(idx, -1, -1):
        if results[pos] != value:
            break
        length += 1
    return length


def count_yes_no(values: list[str]) -> dict[str, int]:
    return {
        "n": len(values),
        "yes": sum(1 for value in values if value == "yes"),
        "no": sum(1 for value in values if value == "no"),
    }


def markov_counts(history: list[dict[str, Any]], lookback: int, streak_cap: int) -> dict[str, Any]:
    rows = history[-int(lookback) :] if lookback < ALL_LOOKBACK else history
    results = [str(row["result"]) for row in rows]
    prev_result, current_streak = trailing_streak(results)
    current_bucket = min(current_streak, int(streak_cap))
    global_next: list[str] = []
    prev_next: list[str] = []
    state_next: list[str] = []
    if len(results) >= 2 and prev_result is not None:
        for idx in range(len(results) - 1):
            source = results[idx]
            nxt = results[idx + 1]
            global_next.append(nxt)
            if source == prev_result:
                prev_next.append(nxt)
                if min(streak_at(results, idx), int(streak_cap)) == current_bucket:
                    state_next.append(nxt)
    return {
        "prev_result": prev_result,
        "streak": current_streak,
        "streak_bucket": current_bucket,
        "global": count_yes_no(global_next),
        "prev": count_yes_no(prev_next),
        "state": count_yes_no(state_next),
    }


def hour_bucket(close_ts: pd.Timestamp, width: int) -> int:
    local = close_ts.tz_convert(ET)
    return int(local.hour // int(width))


def clock_counts(history: list[dict[str, Any]], close_ts: pd.Timestamp, lookback: int, width: int) -> dict[str, Any]:
    rows = history[-int(lookback) :] if lookback < ALL_LOOKBACK else history
    close_local = close_ts.tz_convert(ET)
    current_minute = int(close_local.minute)
    current_bucket = hour_bucket(close_ts, width)
    global_values: list[str] = []
    minute_values: list[str] = []
    phase_values: list[str] = []
    for row in rows:
        result = str(row["result"])
        row_close = row["close_ts"]
        row_local = row_close.tz_convert(ET)
        global_values.append(result)
        if int(row_local.minute) == current_minute:
            minute_values.append(result)
            if hour_bucket(row_close, width) == current_bucket:
                phase_values.append(result)
    return {
        "minute": current_minute,
        "hour_bucket": current_bucket,
        "global": count_yes_no(global_values),
        "minute_counts": count_yes_no(minute_values),
        "phase": count_yes_no(phase_values),
    }


def posterior_yes(
    primary: dict[str, int],
    fallback: dict[str, int],
    global_counts: dict[str, int],
    params: dict[str, Any],
) -> tuple[float, str, int]:
    min_cell = int(params["min_cell_n"])
    prior_strength = float(params["prior_strength"])
    source = "primary"
    selected = primary
    if int(primary.get("n", 0)) < min_cell:
        source = "fallback"
        selected = fallback
    if int(selected.get("n", 0)) < min_cell:
        source = "global"
        selected = global_counts
    global_n = max(0, int(global_counts.get("n", 0)))
    global_q = (float(global_counts.get("yes", 0)) + 1.0) / (global_n + 2.0) if global_n else 0.5
    n = int(selected.get("n", 0))
    yes = float(selected.get("yes", 0))
    q_yes = (yes + prior_strength * global_q) / (n + prior_strength) if n > 0 else global_q
    return q_yes, source, n


def q_side_from_yes(q_yes: float, side: Any) -> float:
    return q_yes if str(side or "").lower() == "yes" else 1.0 - q_yes


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


def ev_from_q_side(case: dict[str, Any], features: dict[str, Any], q_side: float, params: dict[str, Any]) -> dict[str, float]:
    ask = safe_float(features.get("held_ask"))
    fee_per_contract = estimated_order_fee_cents(ask, max(1, int(case["qty"]))) / max(1, int(case["qty"]))
    edge_cents = 100.0 * q_side - ask - fee_per_contract
    uncertainty_penalty = float(params.get("entropy_penalty_cents", 0.0)) * entropy01(q_side)
    score = (
        edge_cents
        - uncertainty_penalty
        - float(params.get("pressure_penalty", 0.0)) * safe_float(features.get("pressure"))
        - float(params.get("spread_penalty", 0.0)) * safe_float(features.get("spread"))
    )
    return {
        "fee_per_contract": fee_per_contract,
        "edge_cents": edge_cents,
        "score": score,
        "uncertainty_penalty": uncertainty_penalty,
    }


def sim_online_markov_transition_ev_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not quote_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    key = f"{int(params['lookback_markets'])}|{int(params['streak_cap'])}"
    counts = features.get("markov", {}).get(key)
    if not counts or counts["global"]["n"] < int(params["min_history_n"]):
        return 0.0, {"enter": False, "skip_reason": "insufficient_prior_history"}
    q_yes, source, cell_n = posterior_yes(counts["state"], counts["prev"], counts["global"], params)
    q_side = q_side_from_yes(q_yes, case.get("side"))
    ev = ev_from_q_side(case, features, q_side, params)
    if ev["score"] < float(params["min_ev_cents"]):
        return 0.0, {"enter": False, "skip_reason": "markov_ev_too_low", "score": round(ev["score"], 6)}
    return entry_meta(
        case,
        features,
        {
            "score": round(ev["score"], 6),
            "edge_cents": round(ev["edge_cents"], 6),
            "q_yes": round(q_yes, 6),
            "q_side": round(q_side, 6),
            "posterior_source": source,
            "cell_n": cell_n,
            "prev_result": counts.get("prev_result"),
            "streak": counts.get("streak"),
            "streak_bucket": counts.get("streak_bucket"),
            "fee_per_contract": round(ev["fee_per_contract"], 6),
        },
    )


def sim_online_clock_phase_prior_ev_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not quote_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    key = f"{int(params['lookback_markets'])}|{int(params['hour_bucket_width'])}"
    counts = features.get("clock", {}).get(key)
    if not counts or counts["global"]["n"] < int(params["min_history_n"]):
        return 0.0, {"enter": False, "skip_reason": "insufficient_prior_history"}
    q_yes, source, cell_n = posterior_yes(counts["phase"], counts["minute_counts"], counts["global"], params)
    q_side = q_side_from_yes(q_yes, case.get("side"))
    ev = ev_from_q_side(case, features, q_side, params)
    if ev["score"] < float(params["min_ev_cents"]):
        return 0.0, {"enter": False, "skip_reason": "clock_ev_too_low", "score": round(ev["score"], 6)}
    return entry_meta(
        case,
        features,
        {
            "score": round(ev["score"], 6),
            "edge_cents": round(ev["edge_cents"], 6),
            "q_yes": round(q_yes, 6),
            "q_side": round(q_side, 6),
            "posterior_source": source,
            "cell_n": cell_n,
            "minute": counts.get("minute"),
            "hour_bucket": counts.get("hour_bucket"),
            "fee_per_contract": round(ev["fee_per_contract"], 6),
        },
    )


def sim_online_regime_clock_mixture_ev_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not quote_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    markov_key = f"{int(params['markov_lookback_markets'])}|{int(params['streak_cap'])}"
    clock_key = f"{int(params['clock_lookback_markets'])}|{int(params['hour_bucket_width'])}"
    markov = features.get("markov", {}).get(markov_key)
    clock = features.get("clock", {}).get(clock_key)
    if (
        not markov
        or not clock
        or markov["global"]["n"] < int(params["min_history_n"])
        or clock["global"]["n"] < int(params["min_history_n"])
    ):
        return 0.0, {"enter": False, "skip_reason": "insufficient_prior_history"}
    q_markov_yes, markov_source, markov_n = posterior_yes(markov["state"], markov["prev"], markov["global"], params)
    q_clock_yes, clock_source, clock_n = posterior_yes(clock["phase"], clock["minute_counts"], clock["global"], params)
    blend = float(params["markov_weight"])
    q_yes = blend * q_markov_yes + (1.0 - blend) * q_clock_yes
    q_side = q_side_from_yes(q_yes, case.get("side"))
    ev = ev_from_q_side(case, features, q_side, params)
    if ev["score"] < float(params["min_ev_cents"]):
        return 0.0, {"enter": False, "skip_reason": "mixture_ev_too_low", "score": round(ev["score"], 6)}
    return entry_meta(
        case,
        features,
        {
            "score": round(ev["score"], 6),
            "edge_cents": round(ev["edge_cents"], 6),
            "q_yes": round(q_yes, 6),
            "q_side": round(q_side, 6),
            "q_markov_yes": round(q_markov_yes, 6),
            "q_clock_yes": round(q_clock_yes, 6),
            "markov_source": markov_source,
            "clock_source": clock_source,
            "markov_cell_n": markov_n,
            "clock_cell_n": clock_n,
            "fee_per_contract": round(ev["fee_per_contract"], 6),
        },
    )


def build_strategy_grid() -> list[StrategySpec]:
    strategies: list[StrategySpec] = []

    markov_theorem = (
        "BTC 15-minute outcomes may have short-run persistence or reversal independent of the quote path; "
        "an entry should clear a fee-adjusted EV check from an expanding Markov transition posterior built only from prior finalized markets."
    )
    markov_equation = (
        "q=P(Y_t=yes|Y_{t-1}, min(streak,c)) with Beta shrinkage to prior transitions; "
        "EV=100*q_side-H_D-fee-lambda*H(q_side)-mu*p_opp-nu*spread; enter if EV>=e."
    )
    for delay_seconds in (0, 60, 120):
        for lookback_markets in (80, ALL_LOOKBACK):
            for streak_cap in (2, 5):
                for min_cell_n in (3, 8):
                    for prior_strength in (4.0, 12.0):
                        for max_entry_ask in (88, 90, 94):
                            for max_opp_pressure in (0.30, 0.50):
                                for max_spread in (4, 10):
                                    for min_ev_cents in (-1.0, 2.0, 5.0):
                                        for entropy_penalty_cents in (0.0, 2.0):
                                            strategies.append(
                                                StrategySpec(
                                                    "online_markov_transition_ev_admission",
                                                    markov_theorem,
                                                    markov_equation,
                                                    {
                                                        "delay_seconds": delay_seconds,
                                                        "lookback_markets": lookback_markets,
                                                        "streak_cap": streak_cap,
                                                        "min_cell_n": min_cell_n,
                                                        "min_history_n": 20,
                                                        "prior_strength": prior_strength,
                                                        "max_entry_ask": max_entry_ask,
                                                        "max_opp_pressure": max_opp_pressure,
                                                        "min_bid_sum": 0,
                                                        "max_spread": max_spread,
                                                        "min_ev_cents": min_ev_cents,
                                                        "entropy_penalty_cents": entropy_penalty_cents,
                                                        "pressure_penalty": 0.5,
                                                        "spread_penalty": 0.03,
                                                    },
                                                    sim_online_markov_transition_ev_admission,
                                                )
                                            )

    clock_theorem = (
        "The BTC 15-minute series may carry clock-phase bias from liquidity and scheduled flow; a trade should "
        "pass an expanding posterior for this close-minute/hour phase rather than assuming every 15-minute slot is exchangeable."
    )
    clock_equation = (
        "q=P(Y_t=yes|minute_t, floor(hour_t/w)) with Beta shrinkage to same-minute and global priors; "
        "EV=100*q_side-H_D-fee-lambda*H(q_side)-mu*p_opp-nu*spread; enter if EV>=e."
    )
    for delay_seconds in (0, 60, 120):
        for lookback_markets in (80, ALL_LOOKBACK):
            for hour_bucket_width in (2, 4, 6):
                for min_cell_n in (3, 8):
                    for prior_strength in (4.0, 12.0):
                        for max_entry_ask in (88, 90, 94):
                            for max_opp_pressure in (0.30, 0.50):
                                for max_spread in (4, 10):
                                    for min_ev_cents in (-1.0, 2.0, 5.0):
                                        for entropy_penalty_cents in (0.0, 2.0):
                                            strategies.append(
                                                StrategySpec(
                                                    "online_clock_phase_prior_ev_admission",
                                                    clock_theorem,
                                                    clock_equation,
                                                    {
                                                        "delay_seconds": delay_seconds,
                                                        "lookback_markets": lookback_markets,
                                                        "hour_bucket_width": hour_bucket_width,
                                                        "min_cell_n": min_cell_n,
                                                        "min_history_n": 20,
                                                        "prior_strength": prior_strength,
                                                        "max_entry_ask": max_entry_ask,
                                                        "max_opp_pressure": max_opp_pressure,
                                                        "min_bid_sum": 0,
                                                        "max_spread": max_spread,
                                                        "min_ev_cents": min_ev_cents,
                                                        "entropy_penalty_cents": entropy_penalty_cents,
                                                        "pressure_penalty": 0.5,
                                                        "spread_penalty": 0.03,
                                                    },
                                                    sim_online_clock_phase_prior_ev_admission,
                                                )
                                            )

    mixture_theorem = (
        "A posterior should be more believable when short-run result dynamics and clock phase agree; blending "
        "the two independent expanding posteriors tests whether either source alone is overfit."
    )
    mixture_equation = (
        "q=w*q_markov+(1-w)*q_clock; EV=100*q_side-H_D-fee-lambda*H(q_side)-mu*p_opp-nu*spread; enter if EV>=e."
    )
    for delay_seconds in (0, 60, 120):
        for markov_lookback_markets in (80, ALL_LOOKBACK):
            for clock_lookback_markets in (160, ALL_LOOKBACK):
                for streak_cap in (2, 5):
                    for hour_bucket_width in (2, 4):
                        for markov_weight in (0.25, 0.5, 0.75):
                            for max_entry_ask in (88, 90, 94):
                                for max_opp_pressure in (0.30, 0.50):
                                    for max_spread in (4, 10):
                                        for min_ev_cents in (0.0, 2.0, 5.0):
                                            strategies.append(
                                                StrategySpec(
                                                    "online_regime_clock_mixture_ev_admission",
                                                    mixture_theorem,
                                                    mixture_equation,
                                                    {
                                                        "delay_seconds": delay_seconds,
                                                        "markov_lookback_markets": markov_lookback_markets,
                                                        "clock_lookback_markets": clock_lookback_markets,
                                                        "streak_cap": streak_cap,
                                                        "hour_bucket_width": hour_bucket_width,
                                                        "markov_weight": markov_weight,
                                                        "min_cell_n": 6,
                                                        "min_history_n": 20,
                                                        "prior_strength": 10.0,
                                                        "max_entry_ask": max_entry_ask,
                                                        "max_opp_pressure": max_opp_pressure,
                                                        "min_bid_sum": 0,
                                                        "max_spread": max_spread,
                                                        "min_ev_cents": min_ev_cents,
                                                        "entropy_penalty_cents": 2.0,
                                                        "pressure_penalty": 0.5,
                                                        "spread_penalty": 0.03,
                                                    },
                                                    sim_online_regime_clock_mixture_ev_admission,
                                                )
                                            )
    return strategies


def needed_precompute_keys(strategies: list[StrategySpec]) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    markov_keys: set[tuple[int, int]] = set()
    clock_keys: set[tuple[int, int]] = set()
    for strategy in strategies:
        params = strategy.params
        if "lookback_markets" in params and "streak_cap" in params:
            markov_keys.add((int(params["lookback_markets"]), int(params["streak_cap"])))
        if "markov_lookback_markets" in params and "streak_cap" in params:
            markov_keys.add((int(params["markov_lookback_markets"]), int(params["streak_cap"])))
        if "lookback_markets" in params and "hour_bucket_width" in params:
            clock_keys.add((int(params["lookback_markets"]), int(params["hour_bucket_width"])))
        if "clock_lookback_markets" in params and "hour_bucket_width" in params:
            clock_keys.add((int(params["clock_lookback_markets"]), int(params["hour_bucket_width"])))
    return markov_keys, clock_keys


def prepare_case(
    case: dict[str, Any],
    history: list[dict[str, Any]],
    delays: tuple[int, ...],
    markov_keys: set[tuple[int, int]],
    clock_keys: set[tuple[int, int]],
) -> dict[str, Any]:
    snapshots: dict[str, dict[str, Any] | None] = {}
    entry_ts = parse_ts(case.get("entry_ts"))
    close_ts = market_close_ts(str(case.get("market") or ""))
    if entry_ts is None or close_ts is None:
        return {str(delay): None for delay in delays}
    for delay in delays:
        quote = quote_snapshot_at_or_after(case, delay)
        if not quote:
            snapshots[str(delay)] = None
            continue
        decision_ts = entry_ts + pd.Timedelta(seconds=float(quote["elapsed"]))
        available_history = window_history(history, decision_ts, ALL_LOOKBACK)
        markov_payload = {
            f"{lookback}|{streak_cap}": markov_counts(available_history, lookback, streak_cap)
            for lookback, streak_cap in markov_keys
        }
        clock_payload = {
            f"{lookback}|{width}": clock_counts(available_history, close_ts, lookback, width)
            for lookback, width in clock_keys
        }
        snapshots[str(delay)] = {
            **quote,
            "decision_ts": decision_ts.isoformat(),
            "market_close_ts": close_ts.isoformat(),
            "seconds_to_close": round((close_ts - decision_ts).total_seconds(), 4),
            "available_history_n": len(available_history),
            "markov": markov_payload,
            "clock": clock_payload,
        }
    return snapshots


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
        "q_side": meta.get("q_side"),
        "posterior_source": meta.get("posterior_source") or meta.get("markov_source"),
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
        "avg_entry_ask": round(mean([safe_float(row["entry_ask"]) for row in entered]), 4) if entered else None,
        "avg_entry_elapsed": round(mean([safe_float(row["entry_elapsed"]) for row in entered]), 4) if entered else None,
        "avg_score": round(mean([safe_float(row.get("score")) for row in entered]), 6) if entered else None,
        "avg_q_side": round(mean([safe_float(row.get("q_side")) for row in entered]), 6) if entered else None,
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


def robust_positive_scan(prepped: list[tuple[dict[str, Any], dict[str, Any]]], strategies: list[StrategySpec]) -> dict[str, list[dict[str, Any]]]:
    ordered = sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
    split = int(len(ordered) * 0.7)
    train = ordered[:split]
    holdout = ordered[split:]
    output: dict[str, list[dict[str, Any]]] = {}
    for family in sorted({strategy.family for strategy in strategies}):
        rows: list[dict[str, Any]] = []
        for strategy in [item for item in strategies if item.family == family]:
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


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    base = payload["baselines"]
    lines = [
        "# Codex Entry Regime Transition Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Quote-path cases with prior-result features: `{payload['case_count']}`",
        f"- Market-result history rows: `{payload['market_result_history_count']}`",
        "- Scope: research-only entry/no-trade simulation; live entry logic, live exit logic, configs, run scripts, and bot processes were not changed.",
        "- Leakage guard: each decision uses only market results whose close time plus 30 seconds is before the simulated quote snapshot.",
        "",
        "## Baselines",
        "",
        f"- Actual recorded PnL: `${base['actual']['summary']['sim_pnl']}`",
        f"- No-stop hold-to-settlement PnL using original entries: `${base['no_stop']['summary']['sim_pnl']}`",
        f"- First held-ask <=70 exit baseline: `${base['held_ask_stop_70']['summary']['sim_pnl']}`",
        "- Skip every opportunity baseline: `$0.0`",
        "",
        "## New Equation Families",
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
                f"- Avg entry ask / elapsed / avg score / avg q_side / contract fraction: `{summary['avg_entry_ask']} / {summary['avg_entry_elapsed']} / {summary['avg_score']} / {summary['avg_q_side']} / {summary['contract_fraction']}`",
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
            "- The tested families intentionally avoid price-path geometry, quote renewal, liquidity dwell, terminal salvage, and BTC momentum equations already present in the ledger.",
            "- These priors are weak evidence unless they beat skip-all on holdout and avoid simply re-entering most historical 90c trades.",
            "- Any live consideration would need a forward shadow that confirms previous-result availability latency and avoids cross-run dataset leakage.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only online regime-transition entry admission probes.")
    parser.add_argument("--refresh-cache", action="store_true")
    parser.add_argument("--datasets", nargs="*", default=None)
    args = parser.parse_args()

    datasets = args.datasets or discover_datasets()
    payloads = [load_dataset_cases(dataset, refresh_cache=args.refresh_cache) for dataset in datasets]
    cases: list[dict[str, Any]] = []
    for payload in payloads:
        dataset = payload.get("dataset")
        for case in payload.get("cases", []):
            case.setdefault("dataset", dataset)
            cases.append(case)
    cases = sorted(cases, key=lambda item: (item["entry_ts"], item["market"], item["side"]))

    history = load_market_result_history(datasets)
    strategies = build_strategy_grid()
    delays = tuple(sorted({int(strategy.params["delay_seconds"]) for strategy in strategies}))
    markov_keys, clock_keys = needed_precompute_keys(strategies)
    prepped_all = [
        (case, prepare_case(case, history, delays, markov_keys, clock_keys))
        for case in cases
    ]
    prepped = [(case, prepared) for case, prepared in prepped_all if any(value is not None for value in prepared.values())]

    results = [run_strategy(prepped, strategy) for strategy in strategies]
    best_by_family = select_family_best(results)
    walk = walk_forward_summary(prepped, strategies)
    robust_scan = robust_positive_scan(prepped, strategies)
    sens = sensitivity(results, best_by_family)

    generated_at = datetime.now(UTC).isoformat()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"codex_entry_regime_transition_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_entry_regime_transition_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_entry_regime_transition_research_latest.json"
    latest_md = EDGE_DIR / "codex_entry_regime_transition_research_latest.md"

    report_payload = {
        "generated_at": generated_at,
        "dataset": "all_quote_path_trades_with_online_prior_results",
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
        "market_result_history_count": len(history),
        "baselines": baseline_payload([case for case, _prepared in prepped]),
        "best_by_family": best_by_family,
        "walk_forward": walk,
        "robust_positive_scan": robust_scan,
        "sensitivity": sens,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "feature_availability": {
            "online_markov_transition_ev_admission": "quote heartbeat snapshot plus prior finalized market outcomes available at decision time",
            "online_clock_phase_prior_ev_admission": "known market close phase plus prior finalized market outcomes available at decision time",
            "online_regime_clock_mixture_ev_admission": "blend of the two expanding priors above",
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
    print(f"Cases={len(prepped)} raw_cases={len(cases)} history={len(history)} strategies={len(strategies)}")
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
