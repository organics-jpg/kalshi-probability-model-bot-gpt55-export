from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

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


def clamp(value: float, lo: float, hi: float) -> float:
    return min(hi, max(lo, value))


def mean(values: list[float]) -> float:
    clean = [value for value in values if not math.isnan(value)]
    return sum(clean) / len(clean) if clean else math.nan


def side_is_win(case: dict[str, Any], side: str) -> bool:
    original = str(case.get("side") or "").lower()
    original_win = bool(case.get("settlement_win"))
    return original_win if side == original else not original_win


def side_entry_pnl(case: dict[str, Any], side: str, ask_cents: float, contracts: int | None = None) -> float:
    qty = max(0, int(case["qty"] if contracts is None else contracts))
    if qty <= 0:
        return 0.0
    fee = estimated_order_fee_cents(ask_cents, qty)
    if side_is_win(case, side):
        return round((qty * (100.0 - ask_cents) - fee) / 100.0, 4)
    return round(-(qty * ask_cents + fee) / 100.0, 4)


def compact_pair_point(case: dict[str, Any], point: dict[str, Any]) -> dict[str, float] | None:
    elapsed = safe_float(point.get("elapsed"))
    own_bid = safe_float(point.get("own_bid"))
    opp_bid = safe_float(point.get("opp_bid"))
    own_ask = safe_float(point.get("own_ask"))
    opp_ask = safe_float(point.get("opp_ask"))
    if any(math.isnan(value) for value in (elapsed, own_bid, opp_bid, own_ask, opp_ask)):
        return None

    original = str(case.get("side") or "").lower()
    if original == "yes":
        yes_bid, yes_ask = own_bid, own_ask
        no_bid, no_ask = opp_bid, opp_ask
    elif original == "no":
        no_bid, no_ask = own_bid, own_ask
        yes_bid, yes_ask = opp_bid, opp_ask
    else:
        return None

    bid_sum = yes_bid + no_bid
    ask_sum = yes_ask + no_ask
    mid_yes = 0.5 * (yes_bid + yes_ask)
    mid_no = 0.5 * (no_bid + no_ask)
    pair_mid_gap = abs(mid_yes + mid_no - 100.0)
    fair_yes = clamp(0.5 * (mid_yes + (100.0 - mid_no)), 0.01, 99.99)
    fair_no = 100.0 - fair_yes
    pair_friction = max(0.0, 100.0 - bid_sum) + max(0.0, ask_sum - 100.0)
    denom = bid_sum if bid_sum > 0 else math.nan
    return {
        "elapsed": elapsed,
        "yes_bid": yes_bid,
        "yes_ask": yes_ask,
        "no_bid": no_bid,
        "no_ask": no_ask,
        "bid_sum": bid_sum,
        "ask_sum": ask_sum,
        "spread_yes": yes_ask - yes_bid,
        "spread_no": no_ask - no_bid,
        "mid_yes": mid_yes,
        "mid_no": mid_no,
        "fair_yes": fair_yes,
        "fair_no": fair_no,
        "pair_mid_gap": pair_mid_gap,
        "pair_friction": pair_friction,
        "yes_pressure": no_bid / denom if denom and not math.isnan(denom) else math.nan,
        "no_pressure": yes_bid / denom if denom and not math.isnan(denom) else math.nan,
    }


def pair_history_features(points: list[dict[str, float]]) -> dict[str, Any]:
    last = points[-1]
    fairs_yes = [point["fair_yes"] for point in points]
    frictions = [point["pair_friction"] for point in points]
    gaps = [point["pair_mid_gap"] for point in points]
    return {
        **last,
        "points": points,
        "elapsed_span": max(1.0, last["elapsed"] - points[0]["elapsed"]),
        "fair_yes_mean": mean(fairs_yes),
        "fair_yes_min": min(fairs_yes),
        "fair_yes_max": max(fairs_yes),
        "fair_yes_net": fairs_yes[-1] - fairs_yes[0],
        "pair_friction_mean": mean(frictions),
        "pair_friction_max": max(frictions),
        "pair_mid_gap_mean": mean(gaps),
    }


def prepare_quote_case(case: dict[str, Any], delays: tuple[int, ...]) -> dict[str, Any]:
    path = [point for point in (compact_pair_point(case, raw) for raw in case.get("path", [])) if point is not None]
    path = sorted(path, key=lambda item: item["elapsed"])
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
        snapshots[str(delay)] = pair_history_features(history)
    return snapshots


def side_values(features: dict[str, Any], side: str, params: dict[str, Any]) -> dict[str, float]:
    ask = float(features[f"{side}_ask"])
    bid = float(features[f"{side}_bid"])
    fair = float(features[f"fair_{side}"])
    spread = float(features[f"spread_{side}"])
    pressure = float(features[f"{side}_pressure"])
    gap_penalty = float(params.get("gap_penalty", 0.0)) * float(features["pair_mid_gap"])
    spread_penalty = float(params.get("spread_penalty", 0.0)) * spread
    pressure_penalty = float(params.get("pressure_penalty", 0.0)) * 100.0 * pressure
    drift_bonus = float(params.get("drift_bonus", 0.0)) * (
        float(features["fair_yes_net"]) if side == "yes" else -float(features["fair_yes_net"])
    )
    conservative_fair = fair - gap_penalty - spread_penalty - pressure_penalty + drift_bonus
    fee_per_contract = estimated_order_fee_cents(ask, max(1, int(params.get("fee_contracts", 1)))) / max(
        1, int(params.get("fee_contracts", 1))
    )
    ev_cents = conservative_fair - ask - fee_per_contract
    return {
        "ask": ask,
        "bid": bid,
        "fair": fair,
        "spread": spread,
        "pressure": pressure,
        "conservative_fair": conservative_fair,
        "fee_per_contract": fee_per_contract,
        "ev_cents": ev_cents,
    }


def pair_gate(features: dict[str, Any], values: dict[str, float], params: dict[str, Any]) -> bool:
    required = (
        values["ask"],
        values["spread"],
        values["ev_cents"],
        float(features["bid_sum"]),
        float(features["pair_friction"]),
    )
    if any(math.isnan(value) for value in required):
        return False
    return (
        values["ask"] <= float(params["max_entry_ask"])
        and values["spread"] <= float(params["max_spread"])
        and float(features["bid_sum"]) >= float(params["min_bid_sum"])
        and float(features["pair_friction"]) <= float(params["max_pair_friction"])
        and values["ev_cents"] >= float(params["min_edge_cents"])
    )


def selected_contracts(case: dict[str, Any], values: dict[str, float], params: dict[str, Any]) -> int:
    qty = int(case["qty"])
    if not bool(params.get("use_fractional_size", False)):
        return qty
    max_gain = max(1.0, 100.0 - values["ask"])
    raw_fraction = float(params.get("size_scale", 1.0)) * max(0.0, values["ev_cents"]) / max_gain
    fraction = min(float(params.get("max_fraction", 1.0)), raw_fraction)
    return max(0, int(math.floor(qty * fraction)))


def entry_meta(
    case: dict[str, Any], features: dict[str, Any], side: str, values: dict[str, float], params: dict[str, Any], extra: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    contracts = selected_contracts(case, values, params)
    if contracts <= 0:
        return 0.0, {
            "enter": False,
            "skip_reason": "fractional_size_zero",
            "selected_side": side,
            "entry_ask": round(values["ask"], 4),
            "ev_cents": round(values["ev_cents"], 4),
        }
    pnl = side_entry_pnl(case, side, values["ask"], contracts)
    return pnl, {
        "enter": True,
        "selected_side": side,
        "switched_side": side != str(case.get("side") or "").lower(),
        "selected_side_win": side_is_win(case, side),
        "entry_ask": values["ask"],
        "entry_elapsed": float(features["elapsed"]),
        "contracts": contracts,
        "base_contracts": int(case["qty"]),
        "ev_cents": round(values["ev_cents"], 4),
        "conservative_fair": round(values["conservative_fair"], 4),
        "fair_yes": round(float(features["fair_yes"]), 4),
        "fair_no": round(float(features["fair_no"]), 4),
        "pair_friction": round(float(features["pair_friction"]), 4),
        "pair_mid_gap": round(float(features["pair_mid_gap"]), 4),
        **extra,
    }


def sim_cross_side_consensus_ev_switch(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features:
        return 0.0, {"enter": False, "skip_reason": "missing_snapshot"}
    candidates: list[tuple[str, dict[str, float]]] = []
    for side in ("yes", "no"):
        values = side_values(features, side, params)
        if pair_gate(features, values, params):
            candidates.append((side, values))
    if not candidates:
        return 0.0, {"enter": False, "skip_reason": "no_side_passed_gate"}
    side, values = max(candidates, key=lambda item: (item[1]["ev_cents"], -item[1]["ask"]))
    return entry_meta(case, features, side, values, params, {"score": round(values["ev_cents"], 4)})


def binary_entropy(p: float) -> float:
    p = clamp(p, 1e-6, 1.0 - 1e-6)
    return -(p * math.log(p) + (1.0 - p) * math.log(1.0 - p))


def sim_entropy_directional_side_gate(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features:
        return 0.0, {"enter": False, "skip_reason": "missing_snapshot"}
    p_yes = clamp(float(features["fair_yes"]) / 100.0, 0.001, 0.999)
    entropy = binary_entropy(p_yes)
    side = "yes" if p_yes >= 0.5 else "no"
    values = side_values(features, side, params)
    conviction = abs(p_yes - 0.5) / math.sqrt(entropy + 1e-6)
    score = (
        conviction
        - float(params.get("gap_score_penalty", 0.0)) * float(features["pair_mid_gap"]) / 100.0
        - float(params.get("spread_score_penalty", 0.0)) * values["spread"] / 100.0
    )
    if entropy > float(params["max_entropy"]):
        return 0.0, {"enter": False, "skip_reason": "entropy_too_high", "entropy": round(entropy, 6)}
    if score < float(params["min_score"]):
        return 0.0, {"enter": False, "skip_reason": "score_too_low", "score": round(score, 6)}
    if not pair_gate(features, values, params):
        return 0.0, {"enter": False, "skip_reason": "pair_gate_failed", "score": round(score, 6)}
    return entry_meta(
        case,
        features,
        side,
        values,
        params,
        {"entropy": round(entropy, 6), "p_yes_consensus": round(p_yes, 6), "score": round(score, 6)},
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

    consensus_theorem = (
        "The historical trigger side is only one candidate side; when the pair book implies a different conservative "
        "fee-adjusted value, the research policy should be allowed to skip or switch sides."
    )
    consensus_equation = (
        "F_yes=0.5*((Y_bid+Y_ask)/2 + 100-(N_bid+N_ask)/2); "
        "F_no=100-F_yes; Ftilde_s=F_s-k*|mid_yes+mid_no-100|-lambda*spread_s-rho*p_opp; "
        "choose s=argmax(Ftilde_s-ask_s-fee_s), enter if EV_s>=e and pair gates pass."
    )
    for delay in (0, 30, 60, 120):
        for max_entry_ask in (70, 80, 90, 92):
            for max_pair_friction in (4.0, 8.0, 20.0):
                for min_edge_cents in (-3.0, 0.0, 2.0):
                    for gap_penalty in (0.0, 0.5):
                        for spread_penalty in (0.0, 0.25):
                            add(
                                "cross_side_consensus_ev_switch",
                                consensus_theorem,
                                consensus_equation,
                                {
                                    "delay_seconds": delay,
                                    "max_entry_ask": max_entry_ask,
                                    "max_pair_friction": max_pair_friction,
                                    "min_edge_cents": min_edge_cents,
                                    "gap_penalty": gap_penalty,
                                    "spread_penalty": spread_penalty,
                                    "pressure_penalty": 0.0,
                                    "drift_bonus": 0.0,
                                    "max_spread": 10,
                                    "min_bid_sum": 0,
                                    "use_fractional_size": False,
                                },
                                sim_cross_side_consensus_ev_switch,
                            )

    entropy_theorem = (
        "A side switch is safer when the pair-implied probability is away from 50/50; high entropy means the side "
        "decision is mostly spread/noise, not directional information."
    )
    entropy_equation = (
        "H(p)=-p*ln(p)-(1-p)*ln(1-p), p=F_yes/100; choose yes if p>=0.5 else no; "
        "C=|p-0.5|/sqrt(H(p)+eps)-g*pair_gap-s*spread; enter if H<=h, C>=c, EV_s>=e."
    )
    for delay in (0, 30, 60, 120):
        for max_entry_ask in (70, 80, 90, 92):
            for max_pair_friction in (4.0, 8.0, 20.0):
                for max_entropy in (0.25, 0.45, 0.62, 0.70):
                    for min_score in (0.02, 0.05, 0.10):
                        for min_edge_cents in (-5.0, -2.0, 0.0):
                            add(
                                "entropy_directional_side_gate",
                                entropy_theorem,
                                entropy_equation,
                                {
                                    "delay_seconds": delay,
                                    "max_entry_ask": max_entry_ask,
                                    "max_pair_friction": max_pair_friction,
                                    "max_entropy": max_entropy,
                                    "min_score": min_score,
                                    "min_edge_cents": min_edge_cents,
                                    "gap_penalty": 0.25,
                                    "spread_penalty": 0.10,
                                    "pressure_penalty": 0.0,
                                    "drift_bonus": 0.0,
                                    "gap_score_penalty": 0.5,
                                    "spread_score_penalty": 0.5,
                                    "max_spread": 10,
                                    "min_bid_sum": 0,
                                    "use_fractional_size": False,
                                },
                                sim_entropy_directional_side_gate,
                            )

    kelly_theorem = (
        "Even when consensus EV is positive, stake should scale with payoff asymmetry; a high ask with a small edge "
        "should not receive the same size as a lower-price asymmetric payoff."
    )
    kelly_equation = (
        "Use the cross-side consensus EV, but size f=min(f_max, c*max(0,EV_s)/(100-ask_s)); "
        "contracts=floor(qty*f), with the selected side still chosen by max EV."
    )
    for delay in (0, 60, 120):
        for max_entry_ask in (80, 90, 92):
            for max_pair_friction in (8.0, 20.0):
                for min_edge_cents in (0.0, 1.0, 2.0):
                    for size_scale in (1.0, 3.0, 6.0):
                        for max_fraction in (0.25, 0.5, 1.0):
                            add(
                                "consensus_kelly_side_sizer",
                                kelly_theorem,
                                kelly_equation,
                                {
                                    "delay_seconds": delay,
                                    "max_entry_ask": max_entry_ask,
                                    "max_pair_friction": max_pair_friction,
                                    "min_edge_cents": min_edge_cents,
                                    "gap_penalty": 0.25,
                                    "spread_penalty": 0.10,
                                    "pressure_penalty": 0.0,
                                    "drift_bonus": 0.0,
                                    "max_spread": 10,
                                    "min_bid_sum": 0,
                                    "use_fractional_size": True,
                                    "size_scale": size_scale,
                                    "max_fraction": max_fraction,
                                },
                                sim_cross_side_consensus_ev_switch,
                            )

    return strategies


def row_for(case: dict[str, Any], pnl: float, meta: dict[str, Any], label: str) -> dict[str, Any]:
    entered = bool(meta.get("enter"))
    selected_side = str(meta.get("selected_side") or "")
    return {
        "label": label,
        "dataset": case["dataset"],
        "market": case["market"],
        "entry_ts": case["entry_ts"],
        "entry_day_et": case["entry_day_et"],
        "original_side": str(case.get("side") or "").lower(),
        "selected_side": selected_side if entered else None,
        "switched_side": bool(meta.get("switched_side")) if entered else False,
        "settlement_win": bool(case["settlement_win"]),
        "selected_side_win": bool(meta.get("selected_side_win")) if entered else False,
        "actual_net_pnl": float(case["actual_net_pnl"]),
        "hold_pnl": float(case["hold_pnl"]),
        "sim_pnl": float(pnl),
        "enter": entered,
        "entry_ask": float(meta["entry_ask"]) if entered and meta.get("entry_ask") is not None else None,
        "entry_elapsed": float(meta["entry_elapsed"]) if entered and meta.get("entry_elapsed") is not None else None,
        "contracts": int(meta.get("contracts", 0) or 0) if entered else 0,
        "base_contracts": int(case["qty"]),
        "ev_cents": float(meta["ev_cents"]) if entered and meta.get("ev_cents") is not None else None,
        "pair_friction": float(meta["pair_friction"]) if entered and meta.get("pair_friction") is not None else None,
        "pair_mid_gap": float(meta["pair_mid_gap"]) if entered and meta.get("pair_mid_gap") is not None else None,
        "score": float(meta["score"]) if entered and meta.get("score") is not None else None,
    }


def summarize_entry_rows(label: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    entered = [row for row in rows if row["enter"]]
    winners = [row for row in entered if row["selected_side_win"]]
    losers = [row for row in entered if not row["selected_side_win"]]
    switched = [row for row in entered if row["switched_side"]]
    original_side_entries = [row for row in entered if not row["switched_side"]]
    sim = sum(float(row["sim_pnl"]) for row in rows)
    actual = sum(float(row["actual_net_pnl"]) for row in rows)
    no_stop = sum(float(row["hold_pnl"]) for row in rows)
    contracts = sum(int(row["contracts"]) for row in entered)
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
        "skips": len(rows) - len(entered),
        "entry_win_rate": round(len(winners) / len(entered), 4) if entered else 0.0,
        "entered_settlement_winners": len(winners),
        "entered_settlement_losers": len(losers),
        "switch_entries": len(switched),
        "original_side_entries": len(original_side_entries),
        "switch_rate": round(len(switched) / len(entered), 4) if entered else 0.0,
        "avg_entry_ask": round(mean([row["entry_ask"] for row in entered if row["entry_ask"] is not None]), 4)
        if entered
        else None,
        "avg_entry_elapsed": round(mean([row["entry_elapsed"] for row in entered if row["entry_elapsed"] is not None]), 4)
        if entered
        else None,
        "avg_ev_cents": round(mean([row["ev_cents"] for row in entered if row["ev_cents"] is not None]), 4)
        if entered
        else None,
        "total_contracts": contracts,
        "base_contracts": base_contracts,
        "contract_fraction": round(contracts / base_contracts, 4) if base_contracts else 0.0,
        "worst_trade": round(min(float(row["sim_pnl"]) for row in rows), 2) if rows else None,
    }


def summarize_by_group(label: str, rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(str(row.get(key)), []).append(row)
    return {name: summarize_entry_rows(label, group_rows) for name, group_rows in sorted(groups.items())}


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
        "by_original_side": summarize_by_group(sid, rows, "original_side"),
        "by_selected_side": summarize_by_group(sid, [row for row in rows if row["enter"]], "selected_side"),
    }


def min_entries(holdout: bool = False) -> int:
    return 5 if holdout else 20


def select_family_best(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for family in sorted({result["family"] for result in results}):
        family_results = [result for result in results if result["family"] == family]
        candidates = [
            result for result in family_results if int(result["summary"]["entries"]) >= min_entries()
        ]
        if not candidates:
            candidates = family_results
        best[family] = max(
            candidates,
            key=lambda result: (result["summary"]["sim_pnl"], result["summary"]["entries"]),
        )
    return best


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
        train_results = [
            result for result in train_results if int(result["summary"]["entries"]) >= min_entries(holdout=False)
        ]
        if not train_results:
            families[family] = {"status": "no_train_strategy_met_entry_floor"}
            continue
        selected_train = max(train_results, key=lambda result: result["summary"]["sim_pnl"])
        selected_params = selected_train["params"]
        selected_strategy = next(strategy for strategy in family_strategies if strategy.params == selected_params)
        holdout_result = run_on_subset(holdout, selected_strategy, "holdout")
        families[family] = {
            "selected_strategy_id": strategy_id(family, selected_params),
            "selected_params": selected_params,
            "train_summary": selected_train["summary"],
            "holdout_summary": holdout_result["summary"],
        }
    return {"train_n": len(train), "holdout_n": len(holdout), "families": families}


def robust_positive_scan(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]], strategies: list[StrategySpec]
) -> dict[str, list[dict[str, Any]]]:
    ordered = sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
    split = int(len(ordered) * 0.70)
    train = ordered[:split]
    holdout = ordered[split:]
    by_family: dict[str, list[dict[str, Any]]] = {}
    for strategy in strategies:
        train_result = run_on_subset(train, strategy, "train")
        holdout_result = run_on_subset(holdout, strategy, "holdout")
        train_summary = train_result["summary"]
        holdout_summary = holdout_result["summary"]
        if (
            int(train_summary["entries"]) >= min_entries(False)
            and int(holdout_summary["entries"]) >= min_entries(True)
            and float(train_summary["sim_pnl"]) > 0.0
            and float(holdout_summary["sim_pnl"]) > 0.0
        ):
            by_family.setdefault(strategy.family, []).append(
                {
                    "strategy_id": strategy_id(strategy.family, strategy.params),
                    "params": strategy.params,
                    "train_sim_pnl": train_summary["sim_pnl"],
                    "train_entries": train_summary["entries"],
                    "train_win_rate": train_summary["entry_win_rate"],
                    "holdout_sim_pnl": holdout_summary["sim_pnl"],
                    "holdout_entries": holdout_summary["entries"],
                    "holdout_win_rate": holdout_summary["entry_win_rate"],
                    "holdout_switch_rate": holdout_summary["switch_rate"],
                    "holdout_delta_vs_actual": holdout_summary["delta_vs_actual"],
                }
            )
    for family, rows in by_family.items():
        rows.sort(key=lambda item: (item["holdout_sim_pnl"], item["train_sim_pnl"]), reverse=True)
        by_family[family] = rows[:15]
    return by_family


def sensitivity(results: list[dict[str, Any]], best_by_family: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    for family, best in best_by_family.items():
        best_params = best["params"]
        rows = [
            {
                "strategy_id": result["strategy_id"],
                "distance": result_distance(result["params"], best_params),
                "params": result["params"],
                "summary": result["summary"],
            }
            for result in results
            if result["family"] == family
            and result["strategy_id"] != best["strategy_id"]
            and result_distance(result["params"], best_params) <= 3.0
            and int(result["summary"]["entries"]) >= min_entries()
        ]
        rows.sort(key=lambda item: (item["summary"]["sim_pnl"], -item["distance"]), reverse=True)
        output[family] = rows[:10]
    return output


def baseline_payload(cases: list[dict[str, Any]]) -> dict[str, Any]:
    actual = run_baseline(cases, "actual")["summary"]
    no_stop = run_baseline(cases, "no_stop")["summary"]
    return {"actual": actual, "no_stop": no_stop, "no_trade_all": {"sim_pnl": 0.0}}


def status_for(family: str, result: dict[str, Any], payload: dict[str, Any]) -> str:
    holdout = payload["walk_forward"]["families"].get(family, {}).get("holdout_summary", {})
    robust_rows = payload["robust_positive_scan"].get(family, [])
    full = result["summary"]
    if (
        full.get("sim_pnl", 0.0) > 0.0
        and full.get("delta_vs_actual", -999999.0) > 0.0
        and holdout.get("sim_pnl", -999999.0) > 0.0
        and robust_rows
    ):
        return "candidate_for_human_review"
    if full.get("sim_pnl", 0.0) > 0.0 and robust_rows:
        return "watchlist_positive_needs_validation"
    if full.get("sim_pnl", 0.0) > 0.0:
        return "watchlist_positive_but_not_robust"
    return "tested_negative"


def read_prior_entry_reference() -> dict[str, Any]:
    references: dict[str, Any] = {}
    for pattern in (
        "codex_entry_microstructure_research_latest.json",
        "codex_entry_barrier_parity_research_latest.json",
        "codex_entry_timing_research_latest.json",
    ):
        path = EDGE_DIR / pattern
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        references[pattern] = {
            "generated_at": payload.get("generated_at"),
            "best_by_family": {
                family: result.get("summary", {})
                for family, result in payload.get("best_by_family", {}).items()
            },
        }
    return references


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    base = payload["baselines"]
    lines = [
        "# Codex Entry Side-Switch Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Quote-path cases: `{payload['case_count']}`",
        f"- Actual recorded PnL: `${base['actual']['sim_pnl']:.2f}`",
        f"- No-stop hold-to-settlement PnL: `${base['no_stop']['sim_pnl']:.2f}`",
        "- No-trade-all PnL: `$0.00`",
        "",
        "## Tested New Equation Families",
        "",
    ]
    for family, result in payload["best_by_family"].items():
        summary = result["summary"]
        walk = payload["walk_forward"]["families"].get(family, {})
        holdout = walk.get("holdout_summary", {})
        lines.extend(
            [
                f"### `{family}`",
                "",
                f"- Strategy ID: `{result['strategy_id']}`",
                f"- Status: {status_for(family, result, payload)}",
                f"- Equation: `{result['equation']}`",
                f"- Best params: `{json.dumps(result['params'], sort_keys=True)}`",
                (
                    f"- Full sample: PnL `${summary['sim_pnl']:.2f}`, delta vs actual "
                    f"`${summary['delta_vs_actual']:.2f}`, delta vs no-stop `${summary['delta_vs_no_stop']:.2f}`, "
                    f"entries `{summary['entries']}`, win rate `{summary['entry_win_rate']:.2%}`, "
                    f"switch rate `{summary['switch_rate']:.2%}`, avg ask `{summary['avg_entry_ask']}`."
                ),
            ]
        )
        if holdout:
            lines.append(
                f"- Train-selected holdout: PnL `${holdout['sim_pnl']:.2f}`, entries `{holdout['entries']}`, "
                f"win rate `{holdout['entry_win_rate']:.2%}`, switch rate `{holdout['switch_rate']:.2%}`."
            )
        lines.append("")

    lines.extend(["## Robust Positive Scan", ""])
    lines.append("| Family | Robust rows | Best holdout PnL | Holdout entries | Holdout win rate | Note |")
    lines.append("|---|---:|---:|---:|---:|---|")
    for family in sorted({result["family"] for result in payload["all_results"]}):
        rows = payload["robust_positive_scan"].get(family, [])
        if not rows:
            lines.append(f"| `{family}` | 0 |  |  |  | no train-positive and holdout-positive parameterization |")
            continue
        top = rows[0]
        lines.append(
            f"| `{family}` | {len(rows)} | `${top['holdout_sim_pnl']:.2f}` | {top['holdout_entries']} | "
            f"{top['holdout_win_rate']:.2%} | `{top['strategy_id']}` |"
        )

    lines.extend(["", "## Sensitivity Near Full-Sample Best", ""])
    lines.append("| Family | Nearby rows | Best nearby PnL | Worst nearby PnL |")
    lines.append("|---|---:|---:|---:|")
    for family, rows in payload["sensitivity"].items():
        if rows:
            pnls = [row["summary"]["sim_pnl"] for row in rows]
            lines.append(f"| `{family}` | {len(rows)} | `${max(pnls):.2f}` | `${min(pnls):.2f}` |")
        else:
            lines.append(f"| `{family}` | 0 |  |  |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This run deliberately challenges fixed side choice: every strategy can select YES, NO, or no trade from quote data available at the simulated decision delay.",
            "- The equations are not renamed dwell, parity-friction, delayed-snapshot, or first-passage rules; they score both contracts as alternative entries and track switch rate explicitly.",
            "- Settlement labels are used only for scoring. The side decision uses only quote-path fields available at or before the delay.",
            "- These are research-only results. No live entry logic, live exit logic, production config, run scripts, or bot process was changed.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only side-switch entry probes for Kalshi BTC 15m.")
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
    all_results = [run_strategy(prepped, strategy) for strategy in strategies]
    best_by_family = select_family_best(all_results)

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"codex_entry_side_switch_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_entry_side_switch_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_entry_side_switch_research_latest.json"
    latest_md = EDGE_DIR / "codex_entry_side_switch_research_latest.md"

    report_payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset": "all_quote_path_trades",
        "datasets": sorted({str(case.get("dataset")) for case in all_cases}),
        "requested_datasets": datasets,
        "dataset_payloads": [
            {
                "dataset": payload.get("dataset"),
                "cases": len(payload.get("cases", [])),
                "trades_total": payload.get("trades_total"),
                "raw_trades_total": payload.get("raw_trades_total"),
                "cache_path": payload.get("cache_path"),
            }
            for payload in payloads
        ],
        "case_count": len(all_cases),
        "strategy_count": len(strategies),
        "baselines": baseline_payload(all_cases),
        "best_by_family": best_by_family,
        "all_results": [
            {
                "strategy_id": result["strategy_id"],
                "family": result["family"],
                "params": result["params"],
                "summary": result["summary"],
            }
            for result in all_results
        ],
        "walk_forward": walk_forward_summary(prepped, strategies),
        "robust_positive_scan": robust_positive_scan(prepped, strategies),
        "sensitivity": sensitivity(all_results, best_by_family),
        "prior_entry_reference": read_prior_entry_reference(),
        "feature_availability": {
            "cross_side_consensus_ev_switch": "YES/NO bid and ask quotes through the simulated delay",
            "entropy_directional_side_gate": "same pair quotes converted to consensus probability and binary entropy",
            "consensus_kelly_side_sizer": "same consensus EV with payoff-normalized fractional sizing",
        },
        "json_path": str(json_path),
        "markdown_path": str(md_path),
    }

    json_text = json.dumps(report_payload, indent=2, sort_keys=True)
    json_path.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")
    write_markdown(md_path, report_payload)
    write_markdown(latest_md, report_payload)

    ledger_records: list[dict[str, Any]] = []
    for family, result in best_by_family.items():
        ledger_records.append(
            {
                "recorded_at": report_payload["generated_at"],
                "generated_at": report_payload["generated_at"],
                "source": Path(__file__).name,
                "family": family,
                "status": status_for(family, result, report_payload),
                "dataset": report_payload["dataset"],
                "datasets": report_payload["datasets"],
                "strategy_id": result["strategy_id"],
                "idea_key": idea_key(family, result["equation"], result["params"]),
                "theorem": result["theorem"],
                "equation": result["equation"],
                "params": result["params"],
                "summary": result["summary"],
                "train_summary": report_payload["walk_forward"]["families"].get(family, {}).get("train_summary"),
                "holdout_summary": report_payload["walk_forward"]["families"].get(family, {}).get("holdout_summary"),
                "robust_positive_count": len(report_payload["robust_positive_scan"].get(family, [])),
                "json_path": str(json_path),
                "markdown_path": str(md_path),
            }
        )
    append_ledger(ledger_records)
    update_strategy_memory(report_payload, best_by_family)

    print(
        f"Wrote {md_path} and {json_path}. "
        f"Cases={len(all_cases)} strategies={len(strategies)} baselines actual="
        f"{report_payload['baselines']['actual']['sim_pnl']:.2f} no_stop="
        f"{report_payload['baselines']['no_stop']['sim_pnl']:.2f}"
    )
    for family, result in best_by_family.items():
        summary = result["summary"]
        holdout = report_payload["walk_forward"]["families"].get(family, {}).get("holdout_summary", {})
        print(
            f"{family} {result['strategy_id']} status={status_for(family, result, report_payload)} "
            f"sim={summary['sim_pnl']:.2f} delta_actual={summary['delta_vs_actual']:.2f} "
            f"entries={summary['entries']} switch_rate={summary['switch_rate']:.2%} "
            f"holdout={holdout.get('sim_pnl')}"
        )


if __name__ == "__main__":
    main()
