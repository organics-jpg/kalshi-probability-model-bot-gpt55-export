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


def clamp_probability(value: float) -> float:
    return min(0.99, max(0.01, value))


def logit(probability: float) -> float:
    p = clamp_probability(probability)
    return math.log(p / (1.0 - p))


def sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def pressure(point: dict[str, Any]) -> float:
    own_bid = safe_float(point.get("own_bid"))
    opp_bid = safe_float(point.get("opp_bid"))
    denom = own_bid + opp_bid
    return opp_bid / denom if denom > 0 else math.nan


def spread(point: dict[str, Any]) -> float:
    own_bid = safe_float(point.get("own_bid"))
    own_ask = safe_float(point.get("own_ask"))
    return own_ask - own_bid if not math.isnan(own_bid) and not math.isnan(own_ask) else math.nan


def mean(values: list[float]) -> float:
    clean = [value for value in values if not math.isnan(value)]
    return sum(clean) / len(clean) if clean else math.nan


def stddev(values: list[float]) -> float:
    clean = [value for value in values if not math.isnan(value)]
    if len(clean) < 2:
        return 0.0
    avg = sum(clean) / len(clean)
    return math.sqrt(sum((value - avg) ** 2 for value in clean) / (len(clean) - 1))


def point_features(points: list[dict[str, Any]]) -> dict[str, Any] | None:
    valid = [
        point
        for point in points
        if not math.isnan(safe_float(point.get("held_ask")))
        and not math.isnan(safe_float(point.get("elapsed")))
    ]
    if len(valid) < 2:
        return None

    asks = [safe_float(point.get("held_ask")) for point in valid]
    logits = [logit(ask / 100.0) for ask in asks]
    moves = [logits[idx] - logits[idx - 1] for idx in range(1, len(logits))]
    realized_logit_path = math.sqrt(sum(move * move for move in moves))
    logit_drift = logits[-1] - logits[0]
    logit_snr = logit_drift / (realized_logit_path + 1e-9)
    elapsed = safe_float(valid[-1].get("elapsed"))
    pressures = [pressure(point) for point in valid]
    spreads = [spread(point) for point in valid]
    bid_sums = [safe_float(point.get("bid_sum")) for point in valid]
    return {
        "elapsed": elapsed,
        "held_ask": asks[-1],
        "start_ask": asks[0],
        "low_ask": min(asks),
        "high_ask": max(asks),
        "mean_logit": mean(logits),
        "std_logit": stddev(logits),
        "last_logit": logits[-1],
        "logit_drift": logit_drift,
        "realized_logit_path": realized_logit_path,
        "logit_snr": logit_snr,
        "pressure_end": pressures[-1],
        "pressure_mean": mean(pressures),
        "spread_end": spreads[-1],
        "spread_mean": mean(spreads),
        "bid_sum_end": bid_sums[-1],
        "bid_sum_mean": mean(bid_sums),
    }


def prepare_case(case: dict[str, Any], delays: tuple[int, ...]) -> dict[str, Any]:
    path = [
        point
        for point in case.get("path", [])
        if not math.isnan(safe_float(point.get("elapsed"))) and not math.isnan(safe_float(point.get("held_ask")))
    ]
    snapshots: dict[str, dict[str, Any] | None] = {}
    for delay in delays:
        history: list[dict[str, Any]] = []
        target_seen = False
        for point in path:
            history.append(point)
            if safe_float(point.get("elapsed")) >= delay:
                target_seen = True
                break
        snapshots[str(delay)] = point_features(history) if target_seen else None
    return snapshots


def entry_meta(case: dict[str, Any], ask: float, extra: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    pnl = delayed_entry_pnl(case, ask)
    return pnl, {
        "enter": True,
        "entry_ask": ask,
        "entry_elapsed": extra.get("elapsed"),
        "contracts": int(case["qty"]),
        **extra,
    }


def base_gate(features: dict[str, Any], params: dict[str, Any]) -> bool:
    held_ask = safe_float(features.get("held_ask"))
    pressure_end = safe_float(features.get("pressure_end"))
    bid_sum_end = safe_float(features.get("bid_sum_end"))
    spread_end = safe_float(features.get("spread_end"))
    if any(math.isnan(value) for value in (held_ask, pressure_end, bid_sum_end, spread_end)):
        return False
    return (
        held_ask <= float(params["max_entry_ask"])
        and bid_sum_end >= float(params["min_bid_sum"])
        and spread_end <= float(params["max_spread"])
        and pressure_end <= float(params["max_opp_pressure"])
    )


def sim_logit_drift_snr_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not base_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    score = (
        float(features["logit_snr"])
        - float(params["pressure_penalty"]) * float(features["pressure_end"])
        - float(params["spread_penalty"]) * float(features["spread_end"])
    )
    if score < float(params["min_score"]):
        return 0.0, {"enter": False, "skip_reason": "logit_snr_too_low", "score": round(score, 6)}
    return entry_meta(
        case,
        float(features["held_ask"]),
        {
            "elapsed": features["elapsed"],
            "score": round(score, 6),
            "logit_snr": round(float(features["logit_snr"]), 6),
            "logit_drift": round(float(features["logit_drift"]), 6),
            "realized_logit_path": round(float(features["realized_logit_path"]), 6),
            "pressure_end": round(float(features["pressure_end"]), 6),
            "spread_end": round(float(features["spread_end"]), 4),
            "bid_sum_end": round(float(features["bid_sum_end"]), 4),
        },
    )


def sim_odds_lcb_ev_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not base_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    ask = float(features["held_ask"])
    adjusted_logit = (
        float(features["mean_logit"])
        - float(params["vol_multiplier"]) * float(features["std_logit"])
        - float(params["pressure_penalty"]) * float(features["pressure_end"])
        - float(params["spread_penalty"]) * float(features["spread_end"])
    )
    q_lcb = sigmoid(adjusted_logit)
    fee_per_contract = estimated_order_fee_cents(ask, max(1, int(case["qty"]))) / max(1, int(case["qty"]))
    edge_cents = 100.0 * q_lcb - ask - fee_per_contract
    if edge_cents < float(params["min_edge_cents"]):
        return 0.0, {
            "enter": False,
            "skip_reason": "lcb_edge_too_low",
            "q_lcb": round(q_lcb, 6),
            "edge_cents": round(edge_cents, 4),
        }
    return entry_meta(
        case,
        ask,
        {
            "elapsed": features["elapsed"],
            "q_lcb": round(q_lcb, 6),
            "edge_cents": round(edge_cents, 4),
            "mean_logit": round(float(features["mean_logit"]), 6),
            "std_logit": round(float(features["std_logit"]), 6),
            "pressure_end": round(float(features["pressure_end"]), 6),
            "spread_end": round(float(features["spread_end"]), 4),
            "bid_sum_end": round(float(features["bid_sum_end"]), 4),
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

    snr_theorem = (
        "A high-priced binary entry is safer when its implied odds move in a statistically smooth favorable "
        "direction before entry; raw cents can hide volatility that log-odds exposes."
    )
    snr_equation = (
        "S=(logit(H_D/100)-logit(H_0/100))/(sqrt(sum(delta logit(H)^2))+eps) "
        "- lambda*p_opp(D) - mu*spread(D); enter if H_D<=A, bid_sum>=B, spread<=Smax, p_opp<=P, and S>=s."
    )
    for delay_seconds in (15, 30, 60, 120):
        for max_entry_ask in (90, 92, 94):
            for max_opp_pressure in (0.30, 0.50):
                for min_bid_sum in (0, 98):
                    for max_spread in (4, 10):
                        for pressure_penalty in (0.0, 0.5):
                            for spread_penalty in (0.0, 0.03):
                                for min_score in (0.0, 0.25, 0.5):
                                    add(
                                        "logit_drift_snr_admission",
                                        snr_theorem,
                                        snr_equation,
                                        {
                                            "delay_seconds": delay_seconds,
                                            "max_entry_ask": max_entry_ask,
                                            "max_opp_pressure": max_opp_pressure,
                                            "min_bid_sum": min_bid_sum,
                                            "max_spread": max_spread,
                                            "pressure_penalty": pressure_penalty,
                                            "spread_penalty": spread_penalty,
                                            "min_score": min_score,
                                        },
                                        sim_logit_drift_snr_admission,
                                    )

    lcb_theorem = (
        "The market ask should be compared with a conservative lower confidence bound of the quote-path "
        "implied probability, not just the last observed price."
    )
    lcb_equation = (
        "q_LCB=sigmoid(mean(logit(H_t))-k*std(logit(H_t))-lambda*p_opp(D)-mu*spread(D)); "
        "EV=100*q_LCB-H_D-fee_per_contract; enter if H_D<=A, bid_sum>=B, spread<=Smax, p_opp<=P, and EV>=e."
    )
    for delay_seconds in (15, 30, 60, 120):
        for max_entry_ask in (90, 92, 94):
            for max_opp_pressure in (0.30, 0.50):
                for min_bid_sum in (0, 98):
                    for max_spread in (4, 10):
                        for vol_multiplier in (0.5, 1.0, 1.5):
                            for pressure_penalty in (0.0, 0.5):
                                for spread_penalty in (0.0, 0.02):
                                    for min_edge_cents in (0.0, 1.0, 2.0):
                                        add(
                                            "odds_lcb_ev_admission",
                                            lcb_theorem,
                                            lcb_equation,
                                            {
                                                "delay_seconds": delay_seconds,
                                                "max_entry_ask": max_entry_ask,
                                                "max_opp_pressure": max_opp_pressure,
                                                "min_bid_sum": min_bid_sum,
                                                "max_spread": max_spread,
                                                "vol_multiplier": vol_multiplier,
                                                "pressure_penalty": pressure_penalty,
                                                "spread_penalty": spread_penalty,
                                                "min_edge_cents": min_edge_cents,
                                            },
                                            sim_odds_lcb_ev_admission,
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
        "q_lcb": meta.get("q_lcb"),
        "edge_cents": meta.get("edge_cents"),
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
        "interesting_examples": sorted(rows, key=lambda row: (float(row["sim_pnl"]), row["market"]))[:10],
    }


def select_family_best(results: list[dict[str, Any]], min_entries: int = 8) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for result in results:
        family = result["family"]
        if result["summary"]["entries"] < min_entries:
            continue
        current = output.get(family)
        key = (
            result["summary"]["sim_pnl"],
            result["summary"]["entry_win_rate"],
            -result["summary"]["avg_entry_ask"] if result["summary"]["avg_entry_ask"] is not None else 0.0,
        )
        if current is None:
            output[family] = result
            continue
        old = current["summary"]
        old_key = (
            old["sim_pnl"],
            old["entry_win_rate"],
            -old["avg_entry_ask"] if old["avg_entry_ask"] is not None else 0.0,
        )
        if key > old_key:
            output[family] = result
    if output:
        return output
    for result in results:
        family = result["family"]
        current = output.get(family)
        if current is None or result["summary"]["sim_pnl"] > current["summary"]["sim_pnl"]:
            output[family] = result
    return output


def walk_forward_summary(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]],
    strategies: list[StrategySpec],
) -> dict[str, Any]:
    ordered = sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
    split = int(len(ordered) * 0.7)
    train = ordered[:split]
    holdout = ordered[split:]
    by_family: dict[str, list[StrategySpec]] = {}
    for strategy in strategies:
        by_family.setdefault(strategy.family, []).append(strategy)
    output: dict[str, Any] = {
        "train_n": len(train),
        "holdout_n": len(holdout),
        "split_entry_ts": ordered[split][0]["entry_ts"] if holdout else None,
        "selection_basis": "Max train simulated PnL among variants with at least 8 entries.",
        "families": {},
    }
    for family, family_strategies in by_family.items():
        train_results = [run_strategy(train, strategy) for strategy in family_strategies]
        selected_by_family = select_family_best(train_results, min_entries=8)
        selected_train = selected_by_family.get(family) or max(train_results, key=lambda result: result["summary"]["sim_pnl"])
        selected_spec = next(
            strategy
            for strategy in family_strategies
            if strategy_id(strategy.family, strategy.params) == selected_train["strategy_id"]
        )
        holdout_result = run_strategy(holdout, selected_spec)
        output["families"][family] = {
            "selected_strategy_id": selected_train["strategy_id"],
            "selected_params": selected_train["params"],
            "train_summary": selected_train["summary"],
            "holdout_summary": holdout_result["summary"],
            "holdout_by_dataset": holdout_result["by_dataset"],
            "holdout_by_side": holdout_result["by_side"],
        }
    return output


def robust_positive_scan(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]],
    strategies: list[StrategySpec],
) -> dict[str, list[dict[str, Any]]]:
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
                or train_summary["entries"] < 8
                or holdout_summary["entries"] < 5
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
                if result["family"] == family and result["summary"]["entries"] >= 8
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
        and holdout.get("entries", 0) >= 5
        and len(robust_rows) >= 3
    ):
        return "candidate_for_human_review"
    if result["summary"]["delta_vs_no_trade_all"] > 0 and robust_rows:
        return "watchlist_positive_but_selection_sensitive"
    return "tested_not_robust"


def read_prior_entry_reference() -> dict[str, Any]:
    output: dict[str, Any] = {}
    for name in (
        "codex_entry_timing_research_latest.json",
        "codex_entry_path_geometry_research_latest.json",
        "codex_entry_clock_decay_research_latest.json",
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
        "# Codex Entry Logit SNR Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Quote-path cases: `{payload['case_count']}`",
        "- Scope: research-only entry/no-trade simulation; live bot logic, configs, run scripts, and processes were not changed.",
        "- Non-repetition: this tests implied-probability log-odds path statistics, not delayed snapshot thresholds, Kelly buckets, compact raw-cent path geometry, pressure impulse, or expiry value density.",
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
        by_dataset = result.get("by_dataset", {})
        by_side = result.get("by_side", {})
        active_days = [
            item for item in result.get("by_day", {}).values()
            if item.get("entries", 0) > 0
        ]
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
                f"- Train-selected params: `{json.dumps(walk.get('selected_params'), sort_keys=True)}`",
                f"- Train-selected holdout PnL / delta vs actual / delta vs no-stop / delta vs skip-all: `${holdout.get('sim_pnl')}` / `${holdout.get('delta_vs_actual')}` / `${holdout.get('delta_vs_no_stop')}` / `${holdout.get('delta_vs_no_trade_all')}`",
                f"- Holdout entries / skipped winners / skipped losers / win rate: `{holdout.get('entries')} / {holdout.get('skipped_settlement_winners')} / {holdout.get('skipped_settlement_losers')} / {holdout.get('entry_win_rate')}`",
                f"- Active days positive/active: `{len(positive_days)}/{len(active_days)}`",
            ]
        )
        if by_dataset:
            dataset_bits = [
                f"{dataset}: ${item['sim_pnl']} ({item['entries']} entries)"
                for dataset, item in sorted(by_dataset.items())
            ]
            lines.append(f"- By dataset: `{'; '.join(dataset_bits)}`")
        if by_side:
            side_bits = [
                f"{side}: ${item['sim_pnl']} ({item['entries']} entries)"
                for side, item in sorted(by_side.items())
            ]
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
            "- The logit SNR branch asks whether quote movement is statistically smooth in odds space; it is less sensitive to raw-cent scale near 90c than path geometry.",
            "- The lower-confidence-bound branch discounts the quote-implied probability by pre-entry logit volatility, spread, and opposing pressure before comparing it with the ask plus fees.",
            "- These equations remain entry-admission/no-trade simulations. Positive aggregate PnL should still be judged against skip-all and chronological holdout because sparse entries can overfit.",
            "- All features are quote-heartbeat values at or before the simulated delay, so there is no settlement-label leakage in the rule inputs.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only logit odds SNR entry probes.")
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
    baselines = {
        "actual": run_baseline(cases, "actual"),
        "no_stop": run_baseline(cases, "no_stop"),
        "held_ask_stop_70": run_baseline(cases, "held_ask_stop_70"),
    }

    generated_at = datetime.now(UTC).isoformat()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"codex_entry_logit_snr_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_entry_logit_snr_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_entry_logit_snr_research_latest.json"
    latest_md = EDGE_DIR / "codex_entry_logit_snr_research_latest.md"
    report_payload = {
        "generated_at": generated_at,
        "dataset": "all_quote_path_trades",
        "datasets": sorted({str(case.get("dataset")) for case in cases}),
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
        "case_count": len(cases),
        "strategy_count": len(strategies),
        "baselines": baselines,
        "best_by_family": best_by_family,
        "walk_forward": walk,
        "robust_positive_scan": robust_scan,
        "sensitivity": sensitivity(results, best_by_family),
        "prior_entry_reference": read_prior_entry_reference(),
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "feature_availability": {
            "logit_drift_snr_admission": "held ask path, own/opposite bids, bid sum, and own spread through the simulated delay",
            "odds_lcb_ev_admission": "held ask path, own/opposite bids, bid sum, own spread, and order fee estimate through the simulated delay",
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
                "dataset": "all_quote_path_trades",
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
        f"actual={baselines['actual']['summary']['sim_pnl']} "
        f"no_stop={baselines['no_stop']['summary']['sim_pnl']} "
        f"stop70={baselines['held_ask_stop_70']['summary']['sim_pnl']} "
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
