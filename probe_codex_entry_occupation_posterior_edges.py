from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

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


UTC = timezone.utc


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


def pressure(point: dict[str, Any]) -> float:
    own_bid = safe_float(point.get("own_bid"))
    opp_bid = safe_float(point.get("opp_bid"))
    denom = own_bid + opp_bid
    return opp_bid / denom if denom > 0 else math.nan


def spread(point: dict[str, Any]) -> float:
    own_bid = safe_float(point.get("own_bid"))
    own_ask = safe_float(point.get("own_ask"))
    return own_ask - own_bid if not math.isnan(own_bid) and not math.isnan(own_ask) else math.nan


def clamp(value: float, lo: float, hi: float) -> float:
    return min(hi, max(lo, value))


def compact_path(case: dict[str, Any]) -> list[dict[str, float]]:
    out: list[dict[str, float]] = []
    for raw in case.get("path", []):
        elapsed = safe_float(raw.get("elapsed"))
        held_ask = safe_float(raw.get("held_ask"))
        own_bid = safe_float(raw.get("own_bid"))
        own_ask = safe_float(raw.get("own_ask"))
        opp_bid = safe_float(raw.get("opp_bid"))
        bid_sum = safe_float(raw.get("bid_sum"))
        if any(math.isnan(value) for value in (elapsed, held_ask, own_bid, own_ask, opp_bid, bid_sum)):
            continue
        out.append(
            {
                "elapsed": elapsed,
                "held_ask": held_ask,
                "own_bid": own_bid,
                "own_ask": own_ask,
                "opp_bid": opp_bid,
                "bid_sum": bid_sum,
                "spread": own_ask - own_bid,
                "pressure": pressure(raw),
            }
        )
    return sorted(out, key=lambda point: point["elapsed"])


def time_segments(history: list[dict[str, float]]) -> list[tuple[dict[str, float], float]]:
    if not history:
        return []
    segments: list[tuple[dict[str, float], float]] = []
    if len(history) == 1:
        return [(history[0], 1.0)]
    for idx in range(1, len(history)):
        prev = history[idx - 1]
        cur = history[idx]
        dt = max(0.0, cur["elapsed"] - prev["elapsed"])
        segments.append((prev, dt))
    tail_dt = max(1.0, min(5.0, history[-1]["elapsed"] - history[-2]["elapsed"]))
    segments.append((history[-1], tail_dt))
    return segments


def weighted_share(history: list[dict[str, float]], predicate: Callable[[float], bool]) -> float:
    total = 0.0
    selected = 0.0
    for point, dt in time_segments(history):
        if dt <= 0:
            continue
        total += dt
        if predicate(point["held_ask"]):
            selected += dt
    return selected / total if total > 0 else 0.0


def time_weighted_mean(history: list[dict[str, float]], key: str) -> float:
    total = 0.0
    weighted = 0.0
    for point, dt in time_segments(history):
        if dt <= 0:
            continue
        total += dt
        weighted += float(point[key]) * dt
    return weighted / total if total > 0 else math.nan


def unique_state_changes(history: list[dict[str, float]]) -> int:
    changes = 0
    for prev, cur in zip(history, history[1:]):
        if any(abs(cur[key] - prev[key]) > 1e-9 for key in ("held_ask", "own_bid", "opp_bid", "bid_sum")):
            changes += 1
    return changes


def quote_history_features(history: list[dict[str, float]]) -> dict[str, Any] | None:
    if len(history) < 2:
        return None
    last = history[-1]
    first = history[0]
    asks = [point["held_ask"] for point in history]
    low = min(asks)
    high = max(asks)
    ask_range = high - low
    span = max(1.0, last["elapsed"] - first["elapsed"])
    moves = [asks[idx] - asks[idx - 1] for idx in range(1, len(asks))]
    realized_abs_move = sum(abs(move) for move in moves)
    realized_vol = math.sqrt(sum(move * move for move in moves)) / math.sqrt(span / 60.0) if moves else 0.0
    tw_mean_ask = time_weighted_mean(history, "held_ask")
    return {
        **last,
        "points": history,
        "span": span,
        "start_ask": first["held_ask"],
        "low_ask": low,
        "high_ask": high,
        "ask_range": ask_range,
        "range_location": (last["held_ask"] - low) / (ask_range + 1e-9),
        "time_weighted_mean_ask": tw_mean_ask,
        "realized_abs_move": realized_abs_move,
        "realized_vol": realized_vol,
        "state_changes": unique_state_changes(history),
        "mean_pressure": mean([point["pressure"] for point in history]),
        "mean_spread": mean([point["spread"] for point in history]),
    }


def prepare_case(case: dict[str, Any], delays: tuple[int, ...]) -> dict[str, Any]:
    path = compact_path(case)
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


def quote_gate(features: dict[str, Any], params: dict[str, Any]) -> bool:
    values = (
        safe_float(features.get("held_ask")),
        safe_float(features.get("pressure")),
        safe_float(features.get("bid_sum")),
        safe_float(features.get("spread")),
    )
    if any(math.isnan(value) for value in values):
        return False
    held_ask, pressure_end, bid_sum, spread_end = values
    return (
        held_ask <= float(params["max_entry_ask"])
        and pressure_end <= float(params["max_opp_pressure"])
        and bid_sum >= float(params["min_bid_sum"])
        and spread_end <= float(params["max_spread"])
    )


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


def beta_path_posterior(features: dict[str, Any], params: dict[str, Any]) -> dict[str, float]:
    history = features["points"]
    prior_strength = float(params["prior_strength"])
    prior_mean = float(params["prior_mean"])
    half_life = max(1.0, float(params["evidence_half_life_seconds"]))
    evidence_scale = float(params["evidence_scale"])
    alpha = prior_strength * prior_mean
    beta = prior_strength * (1.0 - prior_mean)
    last_elapsed = float(features["elapsed"])
    raw_weight_total = 0.0
    for point, dt in time_segments(history):
        age = max(0.0, last_elapsed - point["elapsed"])
        recency_weight = 0.5 ** (age / half_life)
        spread_discount = 1.0 / (1.0 + max(0.0, point["spread"]) / 10.0)
        weight = max(0.0, dt / 60.0) * evidence_scale * recency_weight * spread_discount
        p = clamp(point["held_ask"] / 100.0, 0.001, 0.999)
        alpha += weight * p
        beta += weight * (1.0 - p)
        raw_weight_total += weight
    total = alpha + beta
    mean_q = alpha / total if total > 0 else prior_mean
    variance = (alpha * beta) / ((total * total) * (total + 1.0)) if total > 0 else 0.25
    return {
        "posterior_mean": mean_q,
        "posterior_std": math.sqrt(max(0.0, variance)),
        "effective_weight": raw_weight_total,
    }


def sim_beta_evidence_pullback_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not quote_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    if int(features["state_changes"]) < int(params["min_state_changes"]):
        return 0.0, {"enter": False, "skip_reason": "too_few_state_changes"}
    posterior = beta_path_posterior(features, params)
    q_lcb = posterior["posterior_mean"] - float(params["lcb_z"]) * posterior["posterior_std"]
    ask = float(features["held_ask"])
    fee_per_contract = estimated_order_fee_cents(ask, max(1, int(case["qty"]))) / max(1, int(case["qty"]))
    ev_cents = (
        100.0 * q_lcb
        - ask
        - fee_per_contract
        - float(params["pressure_penalty_cents"]) * float(features["pressure"])
        - float(params["spread_penalty"]) * float(features["spread"])
    )
    pullback = float(features["time_weighted_mean_ask"]) - ask
    if pullback < float(params["min_pullback_from_mean"]):
        return 0.0, {"enter": False, "skip_reason": "insufficient_pullback", "score": round(ev_cents, 6)}
    if ev_cents < float(params["min_ev_cents"]):
        return 0.0, {"enter": False, "skip_reason": "posterior_ev_too_low", "score": round(ev_cents, 6)}
    return entry_meta(
        case,
        features,
        {
            "score": round(ev_cents, 6),
            "q_lcb": round(q_lcb, 6),
            "posterior_mean": round(posterior["posterior_mean"], 6),
            "posterior_std": round(posterior["posterior_std"], 6),
            "effective_weight": round(posterior["effective_weight"], 6),
            "pullback_from_mean": round(pullback, 4),
            "state_changes": int(features["state_changes"]),
        },
    )


def sim_price_occupation_arcsine_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not quote_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    history = features["points"]
    low = float(features["low_ask"])
    high = float(features["high_ask"])
    width = max(1.0, high - low)
    upper_line = low + float(params["upper_range_fraction"]) * width
    lower_line = low + float(params["lower_range_fraction"]) * width
    upper_share = weighted_share(history, lambda ask: ask >= upper_line)
    lower_share = weighted_share(history, lambda ask: ask <= lower_line)
    close_location = float(features["range_location"])
    score = (
        upper_share * close_location
        - float(params["lower_share_penalty"]) * lower_share * (1.0 - close_location)
        - float(params["pressure_penalty"]) * float(features["pressure"])
        - float(params["spread_penalty"]) * float(features["spread"])
        - float(params["range_penalty"]) * float(features["ask_range"]) / 100.0
    )
    if upper_share < float(params["min_upper_share"]):
        return 0.0, {"enter": False, "skip_reason": "upper_occupation_too_low", "score": round(score, 6)}
    if close_location < float(params["min_close_location"]):
        return 0.0, {"enter": False, "skip_reason": "not_near_path_high", "score": round(score, 6)}
    if score < float(params["min_score"]):
        return 0.0, {"enter": False, "skip_reason": "occupation_score_too_low", "score": round(score, 6)}
    return entry_meta(
        case,
        features,
        {
            "score": round(score, 6),
            "upper_share": round(upper_share, 6),
            "lower_share": round(lower_share, 6),
            "close_location": round(close_location, 6),
            "ask_range": round(float(features["ask_range"]), 4),
        },
    )


def build_strategy_grid() -> list[StrategySpec]:
    strategies: list[StrategySpec] = []

    def add(
        family: str,
        theorem: str,
        equation: str,
        params: dict[str, Any],
        simulator: Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], tuple[float, dict[str, Any]]],
    ) -> None:
        strategies.append(StrategySpec(family, theorem, equation, params, simulator))

    posterior_theorem = (
        "A marketable delayed entry is healthier when the current ask is a pullback from sustained prior implied "
        "probability, and the lower credible bound of that path evidence still pays for fees and friction."
    )
    posterior_equation = (
        "alpha=a0+sum(w_t*H_t/100), beta=b0+sum(w_t*(1-H_t/100)), "
        "q_LCB=alpha/(alpha+beta)-z*sqrt(alpha*beta/((alpha+beta)^2*(alpha+beta+1))); "
        "EV=100*q_LCB-H_D-fee-lambda*p_opp-mu*spread; enter if EV>=e and H_mean-H_D>=r."
    )
    for delay_seconds in (60, 120, 180):
        for max_entry_ask in (88, 90):
            for max_opp_pressure in (0.30,):
                for min_bid_sum in (0, 98):
                    for max_spread in (4, 10):
                        for prior_strength in (2.0,):
                            for evidence_scale in (4.0, 8.0):
                                for lcb_z in (0.5, 1.0):
                                    for min_pullback in (0.0, 1.0):
                                        for min_ev_cents in (-2.0, 0.0):
                                            add(
                                                "beta_evidence_pullback_admission",
                                                posterior_theorem,
                                                posterior_equation,
                                                {
                                                    "delay_seconds": delay_seconds,
                                                    "max_entry_ask": max_entry_ask,
                                                    "max_opp_pressure": max_opp_pressure,
                                                    "min_bid_sum": min_bid_sum,
                                                    "max_spread": max_spread,
                                                    "prior_strength": prior_strength,
                                                    "prior_mean": 0.5,
                                                    "evidence_scale": evidence_scale,
                                                    "evidence_half_life_seconds": 90,
                                                    "lcb_z": lcb_z,
                                                    "min_pullback_from_mean": min_pullback,
                                                    "min_state_changes": 1,
                                                    "min_ev_cents": min_ev_cents,
                                                    "pressure_penalty_cents": 4.0,
                                                    "spread_penalty": 0.10,
                                                },
                                                sim_beta_evidence_pullback_admission,
                                            )

    occupation_theorem = (
        "For a binary quote path, settlement-favorable paths should spend a disproportionate amount of observed "
        "time in the upper part of their own pre-entry range rather than only printing there at the decision tick."
    )
    occupation_equation = (
        "O=occ(H_t>=L+u*(U-L))*loc_T-k*occ(H_t<=L+l*(U-L))*(1-loc_T)"
        "-lambda*p_opp-mu*spread-rho*(U-L)/100; loc_T=(H_D-L)/(U-L); enter if O>=o."
    )
    for delay_seconds in (60, 120, 180):
        for max_entry_ask in (88, 90):
            for max_opp_pressure in (0.30,):
                for min_bid_sum in (0, 98):
                    for max_spread in (4, 10):
                        for upper_range_fraction in (0.55, 0.70):
                            for lower_range_fraction in (0.25, 0.35):
                                for min_upper_share in (0.45, 0.65):
                                    for min_close_location in (0.50, 0.75):
                                        for min_score in (0.05, 0.20):
                                            add(
                                                "price_occupation_arcsine_admission",
                                                occupation_theorem,
                                                occupation_equation,
                                                {
                                                    "delay_seconds": delay_seconds,
                                                    "max_entry_ask": max_entry_ask,
                                                    "max_opp_pressure": max_opp_pressure,
                                                    "min_bid_sum": min_bid_sum,
                                                    "max_spread": max_spread,
                                                    "upper_range_fraction": upper_range_fraction,
                                                    "lower_range_fraction": lower_range_fraction,
                                                    "min_upper_share": min_upper_share,
                                                    "min_close_location": min_close_location,
                                                    "min_score": min_score,
                                                    "lower_share_penalty": 0.75,
                                                    "pressure_penalty": 0.5,
                                                    "spread_penalty": 0.03,
                                                    "range_penalty": 0.5,
                                                },
                                                sim_price_occupation_arcsine_admission,
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
        "avg_score": round(mean([float(row["score"]) for row in entered if row["score"] is not None]), 6)
        if entered
        else None,
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
    rows: list[dict[str, Any]] = []
    for case, prepared in prepped:
        pnl, meta = strategy.simulator(case, prepared, strategy.params)
        rows.append(row_for(case, pnl, meta, sid))
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
    return 5 if holdout else 10


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
    output: dict[str, Any] = {"families": {}}
    ordered = sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
    split = int(len(ordered) * 0.7)
    train = ordered[:split]
    holdout = ordered[split:]
    for family in sorted({strategy.family for strategy in strategies}):
        family_strategies = [strategy for strategy in strategies if strategy.family == family]
        train_results = [run_strategy(train, strategy) for strategy in family_strategies]
        selected = select_family_best(train_results).get(family) or max(train_results, key=lambda result: result["summary"]["sim_pnl"])
        selected_spec = next(
            strategy
            for strategy in family_strategies
            if strategy_id(strategy.family, strategy.params) == selected["strategy_id"]
        )
        holdout_result = run_strategy(holdout, selected_spec)
        output["families"][family] = {
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


def robust_positive_scan(prepped: list[tuple[dict[str, Any], dict[str, Any]]], strategies: list[StrategySpec]) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    ordered = sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
    split = int(len(ordered) * 0.7)
    train = ordered[:split]
    holdout = ordered[split:]
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
        )[:15]
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
        and len(robust_rows) >= 3
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


def read_truffle_reference() -> dict[str, Any]:
    references: dict[str, Any] = {}
    entry_triggered_path = Path("logs/truffle_entry_triggered_confirmation_variant.json")
    if entry_triggered_path.exists():
        try:
            payload = json.loads(entry_triggered_path.read_text(encoding="utf-8"))
            references["entry_triggered_confirmation"] = {
                "path": str(entry_triggered_path),
                "summary": payload.get("summary"),
                "note": "Sampled entry-triggered Truffle classification, not an all-case admission backtest.",
            }
        except json.JSONDecodeError:
            pass
    pre_entry_path = Path("logs/truffle_pre_entry_threshold_context_balanced.json")
    if pre_entry_path.exists():
        try:
            payload = json.loads(pre_entry_path.read_text(encoding="utf-8"))
            references["pre_entry_threshold_context"] = {
                "path": str(pre_entry_path),
                "summary": payload.get("summary"),
                "note": "Small threshold-context sample; not directly comparable with deterministic all-case replay.",
            }
        except json.JSONDecodeError:
            pass
    exit_policy_path = Path("logs/online_exit_supervisor_policy_eval_latest.json")
    if exit_policy_path.exists():
        try:
            payload = json.loads(exit_policy_path.read_text(encoding="utf-8"))
            best: dict[str, Any] | None = None
            for delay in payload.get("delays", []):
                for row in delay.get("top_policies", [])[:1]:
                    candidate = {
                        "path": str(exit_policy_path),
                        "delay_seconds": delay.get("delay_seconds"),
                        "case_count": delay.get("case_count"),
                        "policy": row.get("policy"),
                        "rule": row.get("rule"),
                        "delta_dollars": row.get("delta_dollars"),
                        "exit_count": row.get("exit_count"),
                    }
                    if best is None or float(candidate.get("delta_dollars") or -999999) > float(best.get("delta_dollars") or -999999):
                        best = candidate
            if best:
                best["note"] = "Exit-supervisor stop-slice result; reference-only for this entry admission research."
                references["online_exit_supervisor"] = best
        except json.JSONDecodeError:
            pass
    return references


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    base = payload["baselines"]
    lines = [
        "# Codex Entry Occupation-Posterior Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Quote-path cases: `{payload['case_count']}`",
        "- Scope: research-only entry/no-trade simulation; live entry logic, live exit logic, configs, run scripts, and bot processes were not changed.",
        "- Non-repetition: this tests price-occupation/arcsine support and Bayesian beta path evidence, not fixed delayed gates, stop exits, first-passage ruin, path-CVaR, Omega, CUSUM, logit SNR, or quote-quality dwell.",
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
        active_days = [item for item in result.get("by_day", {}).values() if item.get("entries", 0) > 0]
        positive_days = [item for item in active_days if item.get("sim_pnl", 0) > 0]
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
                f"- Walk-forward split: `{walk.get('split_entry_ts')}`",
                f"- Train-selected params: `{json.dumps(walk.get('selected_params'), sort_keys=True)}`",
                f"- Train-selected holdout PnL / delta vs actual / delta vs no-stop / delta vs skip-all: `${holdout.get('sim_pnl')}` / `${holdout.get('delta_vs_actual')}` / `${holdout.get('delta_vs_no_stop')}` / `${holdout.get('delta_vs_no_trade_all')}`",
                f"- Holdout entries / skipped winners / skipped losers / win rate: `{holdout.get('entries')} / {holdout.get('skipped_settlement_winners')} / {holdout.get('skipped_settlement_losers')} / {holdout.get('entry_win_rate')}`",
                f"- Active days positive/active: `{len(positive_days)}/{len(active_days)}`",
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
    for source, families in (payload.get("prior_entry_reference") or {}).items():
        for family, item in families.items():
            lines.append(
                f"- `{source}` `{family}` `{item.get('strategy_id')}` full `${item.get('sim_pnl')}`, holdout `${item.get('holdout_sim_pnl')}`."
            )
    lines.extend(["", "## Truffle Reference", ""])
    truffle = payload.get("truffle_reference") or {}
    if not truffle:
        lines.append("- No directly comparable current Truffle entry-admission backtest was available.")
    else:
        for name, item in truffle.items():
            lines.append(f"- `{name}`: `{json.dumps(item, sort_keys=True)}`")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The beta posterior branch treats the quote path as repeated noisy measurements of terminal probability, discounted for recency and spread; it only enters if the credible lower bound beats the current ask after fees.",
            "- The occupation branch is an arcsine-style support test: it asks whether the path spent real time in the upper part of its observed range instead of merely touching a good quote at the decision tick.",
            "- All strategy inputs are quote heartbeats at or before the simulated decision delay. Settlement labels are used only for scoring.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only entry occupation/posterior edge probes.")
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

    strategies = build_strategy_grid()
    delays = tuple(sorted({int(strategy.params["delay_seconds"]) for strategy in strategies}))
    prepped = [(case, prepare_case(case, delays)) for case in cases]
    results = [run_strategy(prepped, strategy) for strategy in strategies]
    best_by_family = select_family_best(results)
    walk = walk_forward_summary(prepped, strategies)
    robust_scan = robust_positive_scan(prepped, strategies)
    sens = sensitivity(results, best_by_family)

    generated_at = datetime.now(UTC).isoformat()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"codex_entry_occupation_posterior_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_entry_occupation_posterior_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_entry_occupation_posterior_research_latest.json"
    latest_md = EDGE_DIR / "codex_entry_occupation_posterior_research_latest.md"
    report_payload = {
        "generated_at": generated_at,
        "dataset": "all_quote_path_trades",
        "datasets": sorted({str(case.get("dataset")) for case in cases}),
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
        "case_count": len(cases),
        "strategy_count": len(strategies),
        "baselines": baseline_payload(cases),
        "best_by_family": best_by_family,
        "walk_forward": walk,
        "robust_positive_scan": robust_scan,
        "sensitivity": sens,
        "prior_entry_reference": read_prior_entry_reference(),
        "truffle_reference": read_truffle_reference(),
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "feature_availability": {
            "beta_evidence_pullback_admission": "held ask, own/opposite bids, bid sum, spread, and path timing through simulated delay",
            "price_occupation_arcsine_admission": "held ask path and final book state through simulated delay",
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
    print(
        f"Cases={len(cases)} strategies={len(strategies)} "
        f"actual={report_payload['baselines']['actual']['summary']['sim_pnl']} "
        f"no_stop={report_payload['baselines']['no_stop']['summary']['sim_pnl']} "
        f"stop70={report_payload['baselines']['held_ask_stop_70']['summary']['sim_pnl']}"
    )
    for family, result in best_by_family.items():
        summary = result["summary"]
        holdout = walk["families"].get(family, {}).get("holdout_summary", {})
        print(
            f"{family} {result['strategy_id']} status={status_for(family, result, report_payload)} "
            f"full_sim={summary['sim_pnl']} full_delta_actual={summary['delta_vs_actual']} "
            f"full_delta_skip={summary['delta_vs_no_trade_all']} entries={summary['entries']} "
            f"holdout_sim={holdout.get('sim_pnl')} holdout_delta_actual={holdout.get('delta_vs_actual')} "
            f"holdout_delta_skip={holdout.get('delta_vs_no_trade_all')} holdout_entries={holdout.get('entries')}"
        )


if __name__ == "__main__":
    main()
