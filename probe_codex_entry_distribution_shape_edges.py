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


def clamp(value: float, lo: float, hi: float) -> float:
    return min(hi, max(lo, value))


def logit_from_cents(cents: float) -> float:
    p = clamp(cents / 100.0, 0.001, 0.999)
    return math.log(p / (1.0 - p))


def mean(values: list[float]) -> float:
    clean = [value for value in values if not math.isnan(value)]
    return sum(clean) / len(clean) if clean else math.nan


def quantile(values: list[float], q: float) -> float:
    clean = sorted(value for value in values if not math.isnan(value))
    if not clean:
        return math.nan
    idx = min(len(clean) - 1, max(0, int(math.ceil(q * len(clean))) - 1))
    return clean[idx]


def pressure(point: dict[str, Any]) -> float:
    own_bid = safe_float(point.get("own_bid"))
    opp_bid = safe_float(point.get("opp_bid"))
    denom = own_bid + opp_bid
    return opp_bid / denom if denom > 0 else math.nan


def spread(point: dict[str, Any]) -> float:
    own_bid = safe_float(point.get("own_bid"))
    own_ask = safe_float(point.get("own_ask"))
    return own_ask - own_bid if not math.isnan(own_bid) and not math.isnan(own_ask) else math.nan


def base_gate(features: dict[str, Any], params: dict[str, Any]) -> bool:
    values = (
        safe_float(features.get("held_ask")),
        safe_float(features.get("pressure_end")),
        safe_float(features.get("bid_sum_end")),
        safe_float(features.get("spread_end")),
    )
    if any(math.isnan(value) for value in values):
        return False
    held_ask, pressure_end, bid_sum_end, spread_end = values
    return (
        held_ask <= float(params["max_entry_ask"])
        and pressure_end <= float(params["max_opp_pressure"])
        and bid_sum_end >= float(params["min_bid_sum"])
        and spread_end <= float(params["max_spread"])
    )


def cvar(values: list[float], q: float) -> float:
    clean = sorted(value for value in values if not math.isnan(value))
    if not clean:
        return 0.0
    cutoff = quantile(clean, q)
    tail = [value for value in clean if value >= cutoff]
    return mean(tail) if tail else 0.0


def cusum_scores(logit_moves: list[float], drift_allowance: float) -> tuple[float, float]:
    positive = 0.0
    negative = 0.0
    for move in logit_moves:
        positive = max(0.0, positive + move - drift_allowance)
        negative = max(0.0, negative - move - drift_allowance)
    return positive, negative


def point_features(points: list[dict[str, Any]]) -> dict[str, Any] | None:
    valid = [
        point
        for point in points
        if not math.isnan(safe_float(point.get("elapsed")))
        and not math.isnan(safe_float(point.get("held_ask")))
    ]
    if len(valid) < 3:
        return None
    asks = [safe_float(point.get("held_ask")) for point in valid]
    logits = [logit_from_cents(ask) for ask in asks]
    cent_moves = [asks[idx] - asks[idx - 1] for idx in range(1, len(asks))]
    logit_moves = [logits[idx] - logits[idx - 1] for idx in range(1, len(logits))]
    positive_moves = [max(0.0, move) for move in cent_moves]
    adverse_moves = [max(0.0, -move) for move in cent_moves]
    positive_logit = [max(0.0, move) for move in logit_moves]
    adverse_logit = [max(0.0, -move) for move in logit_moves]
    elapsed = safe_float(valid[-1].get("elapsed"))
    span = max(1.0, elapsed - safe_float(valid[0].get("elapsed")))
    up_cusum, down_cusum = cusum_scores(logit_moves, drift_allowance=0.0025)
    return {
        "elapsed": elapsed,
        "span": span,
        "held_ask": asks[-1],
        "start_ask": asks[0],
        "low_ask": min(asks),
        "high_ask": max(asks),
        "ask_net": asks[-1] - asks[0],
        "ask_range": max(asks) - min(asks),
        "positive_energy": sum(move * move for move in positive_moves),
        "adverse_energy": sum(move * move for move in adverse_moves),
        "positive_logit_energy": sum(move * move for move in positive_logit),
        "adverse_logit_energy": sum(move * move for move in adverse_logit),
        "omega_logit": (sum(positive_logit) + 1e-6) / (sum(adverse_logit) + 1e-6),
        "jump_skew": sum(move * move for move in positive_moves) - sum(move * move for move in adverse_moves),
        "adverse_cvar_70": cvar(adverse_moves, 0.70),
        "adverse_cvar_85": cvar(adverse_moves, 0.85),
        "positive_cvar_70": cvar(positive_moves, 0.70),
        "realized_abs_move": sum(abs(move) for move in cent_moves),
        "logit_realized_abs_move": sum(abs(move) for move in logit_moves),
        "up_cusum": up_cusum,
        "down_cusum": down_cusum,
        "pressure_end": pressure(valid[-1]),
        "pressure_mean": mean([pressure(point) for point in valid]),
        "spread_end": spread(valid[-1]),
        "bid_sum_end": safe_float(valid[-1].get("bid_sum")),
        "state_changes": sum(1 for move in cent_moves if abs(move) > 1e-9),
    }


def prepare_case(case: dict[str, Any], delays: tuple[int, ...]) -> dict[str, Any]:
    path = [
        point
        for point in case.get("path", [])
        if not math.isnan(safe_float(point.get("elapsed")))
        and not math.isnan(safe_float(point.get("held_ask")))
    ]
    snapshots: dict[str, dict[str, Any] | None] = {}
    for delay in delays:
        history: list[dict[str, Any]] = []
        for point in path:
            history.append(point)
            if safe_float(point.get("elapsed")) >= delay:
                break
        if not history or safe_float(history[-1].get("elapsed")) < delay:
            snapshots[str(delay)] = None
            continue
        snapshots[str(delay)] = point_features(history)
    return snapshots


def entry_meta(case: dict[str, Any], features: dict[str, Any], extra: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    ask = float(features["held_ask"])
    return delayed_entry_pnl(case, ask), {
        "enter": True,
        "entry_ask": ask,
        "entry_elapsed": float(features["elapsed"]),
        "contracts": int(case["qty"]),
        "pressure_end": round(float(features["pressure_end"]), 6),
        "spread_end": round(float(features["spread_end"]), 4),
        "bid_sum_end": round(float(features["bid_sum_end"]), 4),
        **extra,
    }


def sim_quote_return_omega_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not base_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    if int(features["state_changes"]) < int(params["min_state_changes"]):
        return 0.0, {"enter": False, "skip_reason": "too_few_state_changes"}
    score = (
        math.log(float(features["omega_logit"]))
        + float(params["net_weight"]) * float(features["ask_net"]) / 100.0
        - float(params["pressure_penalty"]) * float(features["pressure_end"])
        - float(params["spread_penalty"]) * float(features["spread_end"])
    )
    if score < float(params["min_score"]):
        return 0.0, {"enter": False, "skip_reason": "omega_score_too_low", "score": round(score, 6)}
    return entry_meta(
        case,
        features,
        {
            "score": round(score, 6),
            "omega_logit": round(float(features["omega_logit"]), 6),
            "ask_net": round(float(features["ask_net"]), 4),
            "state_changes": int(features["state_changes"]),
        },
    )


def sim_cusum_breakout_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not base_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    breakout = (
        float(features["up_cusum"])
        - float(params["adverse_weight"]) * float(features["down_cusum"])
        - float(params["range_penalty"]) * float(features["ask_range"]) / 100.0
        - float(params["pressure_penalty"]) * float(features["pressure_end"])
        - float(params["spread_penalty"]) * float(features["spread_end"])
    )
    if breakout < float(params["min_breakout"]):
        return 0.0, {
            "enter": False,
            "skip_reason": "cusum_breakout_too_low",
            "breakout": round(breakout, 6),
        }
    return entry_meta(
        case,
        features,
        {
            "score": round(breakout, 6),
            "up_cusum": round(float(features["up_cusum"]), 6),
            "down_cusum": round(float(features["down_cusum"]), 6),
            "ask_range": round(float(features["ask_range"]), 4),
        },
    )


def sim_path_cvar_reserve_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not base_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    adverse_cvar = float(features[f"adverse_cvar_{int(params['cvar_q'])}"])
    payoff_reserve = max(0.0, 100.0 - float(features["held_ask"]))
    jump_balance = float(features["positive_cvar_70"]) - adverse_cvar
    score = (
        payoff_reserve / (1.0 + adverse_cvar)
        + float(params["jump_balance_weight"]) * jump_balance
        - float(params["range_penalty"]) * float(features["ask_range"]) / 10.0
        - float(params["pressure_penalty"]) * float(features["pressure_end"])
        - float(params["spread_penalty"]) * float(features["spread_end"])
    )
    if score < float(params["min_reserve_score"]):
        return 0.0, {"enter": False, "skip_reason": "reserve_score_too_low", "score": round(score, 6)}
    return entry_meta(
        case,
        features,
        {
            "score": round(score, 6),
            "payoff_reserve": round(payoff_reserve, 4),
            "adverse_cvar": round(adverse_cvar, 4),
            "positive_cvar_70": round(float(features["positive_cvar_70"]), 4),
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

    omega_theorem = (
        "A pre-entry quote path is stronger when favorable odds-space returns dominate adverse returns across "
        "the whole observed distribution, not merely at the last quote."
    )
    omega_equation = (
        "Omega=sum(max(dlogit(H),0))/(sum(max(-dlogit(H),0))+eps); "
        "S=ln(Omega)+w*(H_D-H_0)/100-lambda*p_opp-mu*spread; enter if gates pass and S>=s."
    )
    for delay_seconds in (60, 120, 180):
        for max_entry_ask in (88, 90, 92):
            for max_opp_pressure in (0.30,):
                for max_spread in (4, 10):
                    for min_state_changes in (1, 3):
                        for min_score in (-0.25, 0.0, 0.25, 0.50):
                            for net_weight in (0.0, 0.5):
                                add(
                                    "quote_return_omega_admission",
                                    omega_theorem,
                                    omega_equation,
                                    {
                                        "delay_seconds": delay_seconds,
                                        "max_entry_ask": max_entry_ask,
                                        "max_opp_pressure": max_opp_pressure,
                                        "min_bid_sum": 0,
                                        "max_spread": max_spread,
                                        "min_state_changes": min_state_changes,
                                        "min_score": min_score,
                                        "net_weight": net_weight,
                                        "pressure_penalty": 0.5,
                                        "spread_penalty": 0.03,
                                    },
                                    sim_quote_return_omega_admission,
                                )

    cusum_theorem = (
        "A high-price entry should resemble a sequential positive change-point in implied odds; one late print "
        "is weaker if adverse CUSUM remains high."
    )
    cusum_equation = (
        "C+=max(0,C+ + dlogit(H)-nu), C-=max(0,C- - dlogit(H)-nu); "
        "B=C+ - k*C- - r*range/100 - lambda*p_opp - mu*spread; enter if B>=b."
    )
    for delay_seconds in (60, 120, 180):
        for max_entry_ask in (88, 90, 92):
            for max_opp_pressure in (0.30,):
                for max_spread in (4, 10):
                    for adverse_weight in (0.5, 1.0):
                        for range_penalty in (0.0, 0.5):
                            for min_breakout in (0.0, 0.10, 0.25):
                                add(
                                    "cusum_breakout_admission",
                                    cusum_theorem,
                                    cusum_equation,
                                    {
                                        "delay_seconds": delay_seconds,
                                        "max_entry_ask": max_entry_ask,
                                        "max_opp_pressure": max_opp_pressure,
                                        "min_bid_sum": 0,
                                        "max_spread": max_spread,
                                        "adverse_weight": adverse_weight,
                                        "range_penalty": range_penalty,
                                        "min_breakout": min_breakout,
                                        "pressure_penalty": 0.5,
                                        "spread_penalty": 0.03,
                                    },
                                    sim_cusum_breakout_admission,
                                )

    reserve_theorem = (
        "A lower-price entry is not automatically better; the remaining payoff must be large relative to the "
        "pre-entry adverse jump tail and quote range."
    )
    reserve_equation = (
        "R=(100-H_D)/(1+CVaR_q(max(-dH,0))) + a*(CVaR70(max(dH,0))-CVaR_q(max(-dH,0))) "
        "- r*range/10-lambda*p_opp-mu*spread; enter if R>=rho."
    )
    for delay_seconds in (60, 120, 180):
        for max_entry_ask in (80, 85, 90, 92):
            for max_opp_pressure in (0.30,):
                for max_spread in (4, 10):
                    for cvar_q_value in (70, 85):
                        for jump_balance_weight in (0.0, 0.5):
                            for range_penalty in (0.25, 0.5):
                                for min_reserve_score in (2.0, 4.0, 6.0):
                                    add(
                                        "path_cvar_reserve_admission",
                                        reserve_theorem,
                                        reserve_equation,
                                        {
                                            "delay_seconds": delay_seconds,
                                            "max_entry_ask": max_entry_ask,
                                            "max_opp_pressure": max_opp_pressure,
                                            "min_bid_sum": 0,
                                            "max_spread": max_spread,
                                            "cvar_q": cvar_q_value,
                                            "jump_balance_weight": jump_balance_weight,
                                            "range_penalty": range_penalty,
                                            "min_reserve_score": min_reserve_score,
                                            "pressure_penalty": 0.5,
                                            "spread_penalty": 0.03,
                                        },
                                        sim_path_cvar_reserve_admission,
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


def run_strategy(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]],
    strategy: StrategySpec,
) -> dict[str, Any]:
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
    }


def min_entries(holdout: bool = False) -> int:
    return 5 if holdout else 12


def select_family_best(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for family in sorted({result["family"] for result in results}):
        candidates = [
            result
            for result in results
            if result["family"] == family and int(result["summary"]["entries"]) >= min_entries()
        ]
        if not candidates:
            candidates = [result for result in results if result["family"] == family]
        output[family] = max(
            candidates,
            key=lambda result: (
                result["summary"]["sim_pnl"],
                result["summary"]["entry_win_rate"],
                -result["summary"]["entries"],
            ),
        )
    return output


def run_on_subset(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]], strategy: StrategySpec, suffix: str
) -> dict[str, Any]:
    result = run_strategy(prepped, strategy)
    result["strategy_id"] = f"{result['strategy_id']}_{suffix}"
    result["summary"]["label"] = result["strategy_id"]
    return result


def walk_forward_summary(prepped: list[tuple[dict[str, Any], dict[str, Any]]], strategies: list[StrategySpec]) -> dict[str, Any]:
    ordered = sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
    split = int(len(ordered) * 0.70)
    train = ordered[:split]
    holdout = ordered[split:]
    families: dict[str, dict[str, Any]] = {}
    for family in sorted({strategy.family for strategy in strategies}):
        family_strategies = [strategy for strategy in strategies if strategy.family == family]
        train_results = [run_on_subset(train, strategy, "train") for strategy in family_strategies]
        train_candidates = [
            result for result in train_results if int(result["summary"]["entries"]) >= min_entries(False)
        ]
        if not train_candidates:
            families[family] = {"status": "no_train_strategy_met_entry_floor"}
            continue
        selected_train = max(train_candidates, key=lambda result: result["summary"]["sim_pnl"])
        selected_strategy = next(
            strategy for strategy in family_strategies if strategy.params == selected_train["params"]
        )
        holdout_result = run_on_subset(holdout, selected_strategy, "holdout")
        families[family] = {
            "selected_strategy_id": strategy_id(family, selected_train["params"]),
            "selected_params": selected_train["params"],
            "train_summary": selected_train["summary"],
            "holdout_summary": holdout_result["summary"],
            "holdout_by_dataset": holdout_result["by_dataset"],
            "holdout_by_side": holdout_result["by_side"],
        }
    return {
        "train_n": len(train),
        "holdout_n": len(holdout),
        "split_entry_ts": ordered[split][0]["entry_ts"] if holdout else None,
        "selection_basis": "Max train simulated PnL among variants with at least 12 entries.",
        "families": families,
    }


def robust_positive_scan(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]], strategies: list[StrategySpec]
) -> dict[str, list[dict[str, Any]]]:
    ordered = sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
    split = int(len(ordered) * 0.70)
    train = ordered[:split]
    holdout = ordered[split:]
    output: dict[str, list[dict[str, Any]]] = {}
    for family in sorted({strategy.family for strategy in strategies}):
        rows: list[dict[str, Any]] = []
        for strategy in [item for item in strategies if item.family == family]:
            train_result = run_on_subset(train, strategy, "train")
            holdout_result = run_on_subset(holdout, strategy, "holdout")
            train_summary = train_result["summary"]
            holdout_summary = holdout_result["summary"]
            if (
                train_summary["sim_pnl"] <= 0
                or holdout_summary["sim_pnl"] <= 0
                or train_summary["entries"] < min_entries(False)
                or holdout_summary["entries"] < min_entries(True)
            ):
                continue
            rows.append(
                {
                    "strategy_id": strategy_id(strategy.family, strategy.params),
                    "params": strategy.params,
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
    if (
        full.get("delta_vs_no_trade_all", -999999.0) > 0.0
        and holdout.get("delta_vs_no_trade_all", -999999.0) > 0.0
        and holdout.get("entries", 0) >= min_entries(True)
        and len(robust_rows) >= 3
    ):
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
        "codex_entry_logit_snr_research_latest.json",
        "codex_entry_microstructure_research_latest.json",
        "codex_entry_barrier_parity_research_latest.json",
        "codex_entry_side_switch_research_latest.json",
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
    actual = payload["baselines"]["actual"]["summary"]
    no_stop = payload["baselines"]["no_stop"]["summary"]
    stop70 = payload["baselines"]["held_ask_stop_70"]["summary"]
    lines = [
        "# Codex Entry Distribution-Shape Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Quote-path cases: `{payload['case_count']}`",
        "- Scope: research-only entry/no-trade simulation; live entry logic, live exit logic, configs, run scripts, and bot processes were not changed.",
        "- Non-repetition: this tests pre-entry return distribution shape, sequential CUSUM evidence, and path-CVaR payoff reserve rather than dwell time, quote renewal count, first-passage barriers, side switching, fixed entry price, or stop exits.",
        "",
        "## Baselines",
        "",
        f"- Actual recorded PnL: `${actual['sim_pnl']}`",
        f"- No-stop hold-to-settlement PnL using original entries: `${no_stop['sim_pnl']}`",
        f"- First held-ask <=70 exit baseline: `${stop70['sim_pnl']}`",
        "- Skip every opportunity baseline: `$0.0`",
        f"- Walk-forward split: `{payload['walk_forward']['split_entry_ts']}`",
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
                f"- Train-selected params: `{json.dumps(walk.get('selected_params'), sort_keys=True)}`",
                f"- Train-selected holdout PnL / delta vs actual / delta vs no-stop / delta vs skip-all: `${holdout.get('sim_pnl')}` / `${holdout.get('delta_vs_actual')}` / `${holdout.get('delta_vs_no_stop')}` / `${holdout.get('delta_vs_no_trade_all')}`",
                f"- Holdout entries / skipped winners / skipped losers / win rate: `{holdout.get('entries')} / {holdout.get('skipped_settlement_winners')} / {holdout.get('skipped_settlement_losers')} / {holdout.get('entry_win_rate')}`",
                f"- Active days positive/active: `{len(positive_days)}/{len(active_days)}`",
            ]
        )
        dataset_bits = [
            f"{dataset}: ${item['sim_pnl']} ({item['entries']} entries)"
            for dataset, item in sorted(result.get("by_dataset", {}).items())
        ]
        side_bits = [
            f"{side}: ${item['sim_pnl']} ({item['entries']} entries)"
            for side, item in sorted(result.get("by_side", {}).items())
        ]
        if dataset_bits:
            lines.append(f"- By dataset: `{'; '.join(dataset_bits)}`")
        if side_bits:
            lines.append(f"- By side: `{'; '.join(side_bits)}`")
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
            "- The Omega branch scores the whole pre-entry odds-return distribution, so one favorable terminal quote is insufficient if adverse odds moves dominate.",
            "- The CUSUM branch asks whether the quote path has accumulated sequential positive change-point evidence after penalizing adverse CUSUM and range.",
            "- The path-CVaR branch compares remaining payoff to adverse jump tail size; it can accept lower-price entries only when the tail reserve is strong enough.",
            "- Strategy inputs are quote-heartbeat values at or before the simulated delay. Settlement labels are used only for backtest scoring.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only pre-entry distribution-shape admission probes.")
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

    generated_at = datetime.now(UTC).isoformat()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"codex_entry_distribution_shape_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_entry_distribution_shape_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_entry_distribution_shape_research_latest.json"
    latest_md = EDGE_DIR / "codex_entry_distribution_shape_research_latest.md"

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
        "sensitivity": sensitivity(results, best_by_family),
        "prior_entry_reference": read_prior_entry_reference(),
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "feature_availability": {
            "quote_return_omega_admission": "held-side ask path, own/opposite bids, bid sum, and spread through the simulated delay",
            "cusum_breakout_admission": "held-side ask logit path plus final book pressure/spread through the simulated delay",
            "path_cvar_reserve_admission": "held-side ask path jump distribution plus final book pressure/spread through the simulated delay",
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
        f"stop70={report_payload['baselines']['held_ask_stop_70']['summary']['sim_pnl']} "
        f"split={walk['split_entry_ts']}"
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
