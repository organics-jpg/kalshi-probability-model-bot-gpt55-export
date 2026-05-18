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


def pressure_from_values(own_bid: float, opp_bid: float) -> float:
    denom = own_bid + opp_bid
    return opp_bid / denom if denom > 0 else math.nan


def compact_quote_point(point: dict[str, Any]) -> dict[str, float] | None:
    elapsed = safe_float(point.get("elapsed"))
    own_bid = safe_float(point.get("own_bid"))
    opp_bid = safe_float(point.get("opp_bid"))
    own_ask = safe_float(point.get("own_ask"))
    opp_ask = safe_float(point.get("opp_ask"))
    held_ask = safe_float(point.get("held_ask"))
    bid_sum = safe_float(point.get("bid_sum"))
    if any(math.isnan(value) for value in (elapsed, own_bid, opp_bid, own_ask, opp_ask, held_ask, bid_sum)):
        return None
    ask_sum = own_ask + opp_ask
    no_arb_friction = max(0.0, 100.0 - bid_sum) + max(0.0, ask_sum - 100.0)
    return {
        "elapsed": elapsed,
        "own_bid": own_bid,
        "opp_bid": opp_bid,
        "own_ask": own_ask,
        "opp_ask": opp_ask,
        "held_ask": held_ask,
        "bid_sum": bid_sum,
        "ask_sum": ask_sum,
        "spread": own_ask - own_bid,
        "pressure": pressure_from_values(own_bid, opp_bid),
        "no_arb_friction": no_arb_friction,
    }


def mean(values: list[float]) -> float:
    clean = [value for value in values if not math.isnan(value)]
    return sum(clean) / len(clean) if clean else math.nan


def stddev(values: list[float]) -> float:
    clean = [value for value in values if not math.isnan(value)]
    if len(clean) < 2:
        return 0.0
    avg = sum(clean) / len(clean)
    return math.sqrt(sum((value - avg) ** 2 for value in clean) / (len(clean) - 1))


def time_weighted_mean(points: list[dict[str, float]], key: str) -> float:
    weighted = 0.0
    span = 0.0
    for idx in range(1, len(points)):
        prev = points[idx - 1]
        cur = points[idx]
        dt = max(0.0, cur["elapsed"] - prev["elapsed"])
        weighted += float(prev[key]) * dt
        span += dt
    if span <= 0:
        return float(points[-1][key]) if points else math.nan
    return weighted / span


def quote_history_features(history: list[dict[str, float]]) -> dict[str, Any]:
    last = history[-1]
    first = history[0]
    elapsed_span = max(1.0, last["elapsed"] - first["elapsed"])
    ask_moves = [history[idx]["held_ask"] - history[idx - 1]["held_ask"] for idx in range(1, len(history))]
    elapsed_deltas = [
        max(1e-6, history[idx]["elapsed"] - history[idx - 1]["elapsed"])
        for idx in range(1, len(history))
    ]
    total_move = last["held_ask"] - first["held_ask"]
    drift_per_second = total_move / elapsed_span
    residuals = [
        move - drift_per_second * dt
        for move, dt in zip(ask_moves, elapsed_deltas)
    ]
    variance_rate = sum(residual * residual for residual in residuals) / elapsed_span
    frictions = [point["no_arb_friction"] for point in history]
    pressures = [point["pressure"] for point in history]
    spreads = [point["spread"] for point in history]
    return {
        **last,
        "points": history,
        "first_elapsed": first["elapsed"],
        "elapsed_span": elapsed_span,
        "held_ask_start": first["held_ask"],
        "held_ask_min": min(point["held_ask"] for point in history),
        "held_ask_max": max(point["held_ask"] for point in history),
        "held_ask_net": total_move,
        "drift_per_second": drift_per_second,
        "variance_rate": variance_rate,
        "realized_path": sum(abs(move) for move in ask_moves),
        "mean_pressure": mean(pressures),
        "mean_spread": mean(spreads),
        "mean_no_arb_friction": time_weighted_mean(history, "no_arb_friction"),
        "std_no_arb_friction": stddev(frictions),
        "max_no_arb_friction": max(frictions),
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


def bounded_first_passage_probability(x: float, lower: float, upper: float, drift: float, variance_rate: float) -> float:
    if x <= lower:
        return 0.0
    if x >= upper:
        return 1.0
    width = upper - lower
    if width <= 0:
        return 0.0
    if variance_rate <= 1e-9 or abs(drift) <= 1e-9:
        return (x - lower) / width
    exponent_x = -2.0 * drift * (x - lower) / variance_rate
    exponent_u = -2.0 * drift * width / variance_rate
    if exponent_x > 60 or exponent_u > 60:
        return 0.0 if drift < 0 else 1.0
    if exponent_x < -60 or exponent_u < -60:
        return 1.0 if drift > 0 else 0.0
    denom = 1.0 - math.exp(exponent_u)
    if abs(denom) <= 1e-12:
        return (x - lower) / width
    probability = (1.0 - math.exp(exponent_x)) / denom
    return min(0.999, max(0.001, probability))


def entry_meta(case: dict[str, Any], ask: float, extra: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    return delayed_entry_pnl(case, ask), {
        "enter": True,
        "entry_ask": ask,
        "entry_elapsed": extra.get("elapsed"),
        "contracts": int(case["qty"]),
        **extra,
    }


def sim_binary_ruin_probability_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not quote_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    ask = float(features["held_ask"])
    variance_rate = max(float(params["variance_floor"]), float(features["variance_rate"]))
    p_hit_upper = bounded_first_passage_probability(
        ask,
        float(params["lower_barrier"]),
        100.0,
        float(features["drift_per_second"]),
        variance_rate,
    )
    fee_per_contract = estimated_order_fee_cents(ask, max(1, int(case["qty"]))) / max(1, int(case["qty"]))
    ev_cents = 100.0 * p_hit_upper - ask - fee_per_contract
    if ev_cents < float(params["min_ev_cents"]):
        return 0.0, {
            "enter": False,
            "skip_reason": "first_passage_ev_too_low",
            "score": round(ev_cents, 6),
        }
    return entry_meta(
        case,
        ask,
        {
            "elapsed": features["elapsed"],
            "score": round(ev_cents, 6),
            "p_hit_upper": round(p_hit_upper, 6),
            "drift_per_second": round(float(features["drift_per_second"]), 6),
            "variance_rate": round(variance_rate, 6),
            "pressure": round(float(features["pressure"]), 6),
            "spread": round(float(features["spread"]), 4),
            "bid_sum": round(float(features["bid_sum"]), 4),
        },
    )


def sim_parity_friction_compression_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not quote_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    mean_friction = float(features["mean_no_arb_friction"])
    end_friction = float(features["no_arb_friction"])
    shock = max(0.0, end_friction - mean_friction)
    score = (
        -mean_friction
        - float(params["end_weight"]) * end_friction
        - float(params["shock_weight"]) * shock
        - float(params["pressure_weight"]) * float(features["pressure"])
    )
    if mean_friction > float(params["max_mean_friction"]):
        return 0.0, {"enter": False, "skip_reason": "mean_parity_friction_too_high", "score": round(score, 6)}
    if end_friction > float(params["max_end_friction"]):
        return 0.0, {"enter": False, "skip_reason": "end_parity_friction_too_high", "score": round(score, 6)}
    if shock > float(params["max_friction_shock"]):
        return 0.0, {"enter": False, "skip_reason": "parity_friction_shock_too_high", "score": round(score, 6)}
    return entry_meta(
        case,
        float(features["held_ask"]),
        {
            "elapsed": features["elapsed"],
            "score": round(score, 6),
            "mean_no_arb_friction": round(mean_friction, 6),
            "end_no_arb_friction": round(end_friction, 6),
            "friction_shock": round(shock, 6),
            "ask_sum": round(float(features["ask_sum"]), 4),
            "bid_sum": round(float(features["bid_sum"]), 4),
            "pressure": round(float(features["pressure"]), 6),
            "spread": round(float(features["spread"]), 4),
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

    ruin_theorem = (
        "A high-priced binary entry should clear a first-passage expected-value test: from the observed quote path, "
        "the held ask should be more likely to hit settlement-like upper boundary than a loss boundary after fees."
    )
    ruin_equation = (
        "p=Pr_X[tau_100<tau_L] for dX=mu*dt+sigma*dW, "
        "p=(1-exp(-2*mu*(H-L)/sigma^2))/(1-exp(-2*mu*(100-L)/sigma^2)); "
        "EV=100*p-H-fee; enter if EV>=e and book gates pass."
    )
    for delay_seconds in (30, 60, 120, 180):
        for lower_barrier in (55, 65, 70, 75, 80):
            for variance_floor in (0.02, 0.10, 0.25, 0.50):
                for max_entry_ask in (90, 92, 94):
                    for max_opp_pressure in (0.30, 0.50):
                        for min_bid_sum in (0, 98):
                            for max_spread in (4, 10):
                                for min_ev_cents in (-2.0, 0.0, 1.0, 2.0, 4.0):
                                    add(
                                        "binary_ruin_probability_admission",
                                        ruin_theorem,
                                        ruin_equation,
                                        {
                                            "delay_seconds": delay_seconds,
                                            "lower_barrier": lower_barrier,
                                            "variance_floor": variance_floor,
                                            "max_entry_ask": max_entry_ask,
                                            "max_opp_pressure": max_opp_pressure,
                                            "min_bid_sum": min_bid_sum,
                                            "max_spread": max_spread,
                                            "min_ev_cents": min_ev_cents,
                                        },
                                        sim_binary_ruin_probability_admission,
                                    )

    parity_theorem = (
        "A quote is safer when the full binary pair is no-arbitrage compressed; slack bid sums and expensive "
        "complementary asks imply friction that can make an otherwise acceptable held-side ask a bad entry."
    )
    parity_equation = (
        "F=(1/T)*integral(max(0,100-(bid_yes+bid_no))+max(0,ask_yes+ask_no-100))dt; "
        "shock=max(0,F_T-F); enter if H<=A, F<=f, F_T<=g, shock<=s, and book gates pass."
    )
    for delay_seconds in (30, 60, 120, 180):
        for max_entry_ask in (90, 92, 94):
            for max_opp_pressure in (0.30, 0.50):
                for min_bid_sum in (0, 98):
                    for max_spread in (4, 10):
                        for max_mean_friction in (2.0, 3.0, 4.0, 6.0):
                            for max_end_friction in (2.0, 3.0, 4.0, 6.0):
                                for max_friction_shock in (0.0, 1.0, 2.0, 4.0):
                                    add(
                                        "parity_friction_compression_admission",
                                        parity_theorem,
                                        parity_equation,
                                        {
                                            "delay_seconds": delay_seconds,
                                            "max_entry_ask": max_entry_ask,
                                            "max_opp_pressure": max_opp_pressure,
                                            "min_bid_sum": min_bid_sum,
                                            "max_spread": max_spread,
                                            "max_mean_friction": max_mean_friction,
                                            "max_end_friction": max_end_friction,
                                            "max_friction_shock": max_friction_shock,
                                            "end_weight": 0.5,
                                            "shock_weight": 0.5,
                                            "pressure_weight": 1.0,
                                        },
                                        sim_parity_friction_compression_admission,
                                    )
    return strategies


def row_for(case: dict[str, Any], pnl: float, meta: dict[str, Any], label: str) -> dict[str, Any]:
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
        "action": "enter" if meta.get("enter") else "skip",
        "entry_ask": meta.get("entry_ask"),
        "entry_elapsed": meta.get("entry_elapsed"),
        "contracts": int(meta.get("contracts") or 0),
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
        "avg_entry_ask": round(sum(float(row["entry_ask"]) for row in entered) / len(entered), 4) if entered else None,
        "avg_entry_elapsed": round(sum(float(row["entry_elapsed"]) for row in entered) / len(entered), 4) if entered else None,
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
    return "tested_not_robust"


def baseline_payload(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "actual": run_baseline(cases, "actual"),
        "no_stop": run_baseline(cases, "no_stop"),
        "held_ask_stop_70": run_baseline(cases, "held_ask_stop_70"),
    }


def read_prior_entry_reference() -> dict[str, Any]:
    output: dict[str, Any] = {}
    for name in (
        "codex_entry_timing_research_latest.json",
        "codex_entry_path_geometry_research_latest.json",
        "codex_entry_clock_decay_research_latest.json",
        "codex_entry_logit_snr_research_latest.json",
        "codex_entry_microstructure_research_latest.json",
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
    base = payload["baselines"]
    lines = [
        "# Codex Entry Barrier-Parity Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Quote-path cases: `{payload['case_count']}`",
        "- Scope: research-only entry/no-trade simulation; live entry logic, live exit logic, configs, run scripts, and bot processes were not changed.",
        "- Non-repetition: this tests Brownian first-passage EV and binary-pair no-arbitrage friction, not delayed snapshot gates, dwell, renewal cadence, logit SNR, path coherence, pullback limits, Kelly sizing, or expiry density.",
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
                f"- Avg entry ask / elapsed / contract fraction: `{summary['avg_entry_ask']} / {summary['avg_entry_elapsed']} / {summary['contract_fraction']}`",
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
    prior = payload.get("prior_entry_reference") or {}
    if prior:
        for source, families in prior.items():
            for family, item in families.items():
                lines.append(
                    f"- `{source}` `{family}` `{item.get('strategy_id')}` full `${item.get('sim_pnl')}`, holdout `${item.get('holdout_sim_pnl')}`."
                )
    else:
        lines.append("- No prior entry reference JSON was available.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The first-passage branch turns path drift and realized quote variance into a fee-adjusted upper-boundary hit probability. It is not a fixed-price or fixed-delay rule.",
            "- The parity-friction branch uses both YES and NO bids/asks to measure binary-pair slack; it is distinct from simple spread and bid-sum gates because the complementary ask contributes to the no-arbitrage cost.",
            "- All strategy inputs are quote heartbeats observed at or before the simulated decision delay; settlement labels are used only for scoring.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only entry barrier/parity edge probes.")
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
    delays = tuple(sorted({int(strategy.params["delay_seconds"]) for strategy in strategies}))
    prepped = [(case, prepare_quote_case(case, delays)) for case in all_cases]

    results = [run_strategy(prepped, strategy) for strategy in strategies]
    best_by_family = select_family_best(results)
    walk = walk_forward_summary(prepped, strategies)
    robust_scan = robust_positive_scan(prepped, strategies)
    sens = sensitivity(results, best_by_family)

    generated_at = datetime.now(UTC).isoformat()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"codex_entry_barrier_parity_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_entry_barrier_parity_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_entry_barrier_parity_research_latest.json"
    latest_md = EDGE_DIR / "codex_entry_barrier_parity_research_latest.md"
    report_payload = {
        "generated_at": generated_at,
        "dataset": "all_quote_path_trades",
        "datasets": sorted({str(case.get("dataset")) for case in all_cases}),
        "requested_datasets": datasets,
        "dataset_payloads": [
            {
                "dataset": item.get("dataset"),
                "raw_trades_total": item.get("raw_trades_total"),
                "trades_total": item.get("trades_total"),
                "case_count": len(item.get("cases", [])),
                "cache_path": item.get("cache_path"),
            }
            for item in payloads
        ],
        "case_count": len(all_cases),
        "strategy_count": len(strategies),
        "baselines": baseline_payload(all_cases),
        "best_by_family": best_by_family,
        "walk_forward": walk,
        "robust_positive_scan": robust_scan,
        "sensitivity": sens,
        "prior_entry_reference": read_prior_entry_reference(),
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "feature_availability": {
            "binary_ruin_probability_admission": "quote heartbeat path through simulated delay",
            "parity_friction_compression_admission": "YES/NO bid and ask quotes through simulated delay",
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
    print(f"Cases={len(prepped)} strategies={len(strategies)}")
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
