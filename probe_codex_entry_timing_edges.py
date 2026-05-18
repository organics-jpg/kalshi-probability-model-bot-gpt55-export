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
    simulator: Callable[
        [dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any] | None],
        tuple[float, dict[str, Any]],
    ]
    model_builder: Callable[[list[tuple[dict[str, Any], dict[str, Any]]], dict[str, Any]], dict[str, Any]] | None = None


def safe_float(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return math.nan
    return parsed if not math.isnan(parsed) else math.nan


def snapshot_at_delay(case: dict[str, Any], delay_seconds: float) -> dict[str, Any] | None:
    for point in case["path"]:
        if safe_float(point.get("elapsed")) < delay_seconds:
            continue
        own_bid = safe_float(point.get("own_bid"))
        opp_bid = safe_float(point.get("opp_bid"))
        own_ask = safe_float(point.get("own_ask"))
        held_ask = safe_float(point.get("held_ask"))
        bid_sum = safe_float(point.get("bid_sum"))
        if math.isnan(own_bid) or math.isnan(opp_bid) or math.isnan(own_ask) or math.isnan(held_ask):
            return None
        denom = own_bid + opp_bid
        pressure = opp_bid / denom if denom > 0 else math.nan
        return {
            "elapsed": safe_float(point.get("elapsed")),
            "own_bid": own_bid,
            "opp_bid": opp_bid,
            "own_ask": own_ask,
            "held_ask": held_ask,
            "bid_sum": bid_sum,
            "spread": own_ask - own_bid,
            "pressure": pressure,
        }
    return None


def prepare_case(case: dict[str, Any], delays: tuple[int, ...]) -> dict[str, Any]:
    return {str(delay): snapshot_at_delay(case, float(delay)) for delay in delays}


def delayed_entry_pnl(case: dict[str, Any], ask_cents: float, contracts: int | None = None) -> float:
    qty = max(0, int(case["qty"] if contracts is None else contracts))
    if qty <= 0:
        return 0.0
    fee = estimated_order_fee_cents(ask_cents, qty)
    if bool(case["settlement_win"]):
        return round((qty * (100.0 - ask_cents) - fee) / 100.0, 4)
    return round(-(qty * ask_cents + fee) / 100.0, 4)


def entry_conditions_pass(snapshot: dict[str, Any], params: dict[str, Any]) -> bool:
    values = (
        safe_float(snapshot.get("held_ask")),
        safe_float(snapshot.get("pressure")),
        safe_float(snapshot.get("bid_sum")),
        safe_float(snapshot.get("spread")),
    )
    if any(math.isnan(value) for value in values):
        return False
    held_ask, pressure, bid_sum, spread = values
    return (
        held_ask <= float(params["max_entry_ask"])
        and pressure <= float(params["max_opp_pressure"])
        and bid_sum >= float(params["min_bid_sum"])
        and spread <= float(params["max_spread"])
    )


def sim_delayed_entry_survival_filter(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any], model: dict[str, Any] | None
) -> tuple[float, dict[str, Any]]:
    del model
    snapshot = prepared.get(str(int(params["delay_seconds"])))
    if not snapshot or not entry_conditions_pass(snapshot, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_failed_gate"}
    ask = safe_float(snapshot["held_ask"])
    pnl = delayed_entry_pnl(case, ask)
    return pnl, {
        "enter": True,
        "entry_ask": ask,
        "entry_elapsed": safe_float(snapshot["elapsed"]),
        "contracts": int(case["qty"]),
        "pressure": round(safe_float(snapshot["pressure"]), 4),
        "bid_sum": round(safe_float(snapshot["bid_sum"]), 4),
        "spread": round(safe_float(snapshot["spread"]), 4),
    }


def quantize(value: float, width: float, max_bucket: int = 1000) -> int:
    if math.isnan(value):
        return -1
    return max(-1, min(max_bucket, int(math.floor(value / width))))


def kelly_keys(case: dict[str, Any], snapshot: dict[str, Any], params: dict[str, Any]) -> list[tuple[Any, ...]]:
    ask_bucket = quantize(safe_float(snapshot.get("held_ask")), float(params["ask_bucket_cents"]))
    pressure_bucket = quantize(safe_float(snapshot.get("pressure")), float(params["pressure_bucket"]))
    side = str(case.get("side") or "").lower() if bool(params.get("use_side", True)) else "all"
    return [
        ("kelly_entry", side, ask_bucket, pressure_bucket),
        ("kelly_entry_side_ask", side, ask_bucket),
        ("kelly_entry_ask", ask_bucket),
        ("global",),
    ]


def build_kelly_model(prepped: list[tuple[dict[str, Any], dict[str, Any]]], params: dict[str, Any]) -> dict[str, Any]:
    counts: dict[tuple[Any, ...], dict[str, float]] = {}
    total = 0
    wins = 0
    delay = str(int(params["delay_seconds"]))
    for case, prepared in prepped:
        snapshot = prepared.get(delay)
        if not snapshot or not entry_conditions_pass(snapshot, params):
            continue
        total += 1
        wins += 1 if bool(case["settlement_win"]) else 0
        seen: set[tuple[Any, ...]] = set()
        for key in kelly_keys(case, snapshot, params):
            if key in seen:
                continue
            bucket = counts.setdefault(key, {"n": 0.0, "wins": 0.0})
            bucket["n"] += 1.0
            bucket["wins"] += 1.0 if bool(case["settlement_win"]) else 0.0
            seen.add(key)
    global_q = wins / total if total else 0.5
    return {
        "counts": {"|".join(map(str, key)): value for key, value in counts.items()},
        "global_q": global_q,
        "train_cases": total,
    }


def q_from_kelly_model(
    case: dict[str, Any], snapshot: dict[str, Any], params: dict[str, Any], model: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    global_q = float(model.get("global_q", 0.5))
    min_cell_cases = float(params["min_cell_cases"])
    prior_strength = float(params["prior_strength"])
    counts = model.get("counts", {})
    for key in kelly_keys(case, snapshot, params):
        text_key = "|".join(map(str, key))
        bucket = counts.get(text_key)
        if not bucket or float(bucket.get("n", 0.0)) < min_cell_cases:
            continue
        n = float(bucket["n"])
        wins = float(bucket["wins"])
        q_hat = (wins + prior_strength * global_q) / (n + prior_strength)
        return q_hat, {"calibration_key": text_key, "cell_n": n, "cell_wins": wins}
    return global_q, {
        "calibration_key": "global_fallback",
        "cell_n": float(model.get("train_cases", 0)),
        "cell_wins": global_q * float(model.get("train_cases", 0)),
    }


def sim_empirical_kelly_entry_sizer(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any], model: dict[str, Any] | None
) -> tuple[float, dict[str, Any]]:
    if model is None:
        raise ValueError("empirical Kelly entry sizing requires a calibration model")
    snapshot = prepared.get(str(int(params["delay_seconds"])))
    if not snapshot or not entry_conditions_pass(snapshot, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_failed_gate"}
    ask = safe_float(snapshot["held_ask"])
    q_hat, q_meta = q_from_kelly_model(case, snapshot, params, model)
    fee_per_contract = estimated_order_fee_cents(ask, max(1, int(case["qty"]))) / max(1, int(case["qty"]))
    edge_cents = 100.0 * q_hat - ask - fee_per_contract
    max_gain = max(1e-9, 100.0 - ask)
    raw_kelly = edge_cents / max_gain
    scaled_fraction = float(params["kelly_scale"]) * raw_kelly
    fraction = max(0.0, min(float(params["max_fraction"]), scaled_fraction))
    if edge_cents < float(params["min_edge_cents"]) or fraction <= 0:
        return 0.0, {
            "enter": False,
            "skip_reason": "nonpositive_edge",
            "entry_ask": ask,
            "q_hat": round(q_hat, 6),
            "edge_cents": round(edge_cents, 4),
            **q_meta,
        }
    contracts = min(int(case["qty"]), max(0, int(round(int(case["qty"]) * fraction))))
    if contracts <= 0:
        return 0.0, {
            "enter": False,
            "skip_reason": "rounded_to_zero_contracts",
            "entry_ask": ask,
            "q_hat": round(q_hat, 6),
            "edge_cents": round(edge_cents, 4),
            "kelly_fraction": round(fraction, 6),
            **q_meta,
        }
    pnl = delayed_entry_pnl(case, ask, contracts=contracts)
    return pnl, {
        "enter": True,
        "entry_ask": ask,
        "entry_elapsed": safe_float(snapshot["elapsed"]),
        "contracts": contracts,
        "base_contracts": int(case["qty"]),
        "q_hat": round(q_hat, 6),
        "edge_cents": round(edge_cents, 4),
        "kelly_fraction": round(fraction, 6),
        "pressure": round(safe_float(snapshot["pressure"]), 4),
        "bid_sum": round(safe_float(snapshot["bid_sum"]), 4),
        "spread": round(safe_float(snapshot["spread"]), 4),
        **q_meta,
    }


def build_strategy_grid() -> list[StrategySpec]:
    strategies: list[StrategySpec] = []

    def add(
        family: str,
        theorem: str,
        equation: str,
        params: dict[str, Any],
        simulator: Callable[
            [dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any] | None],
            tuple[float, dict[str, Any]],
        ],
        model_builder: Callable[[list[tuple[dict[str, Any], dict[str, Any]]], dict[str, Any]], dict[str, Any]] | None = None,
    ) -> None:
        strategies.append(StrategySpec(family, theorem, equation, params, simulator, model_builder))

    for delay_seconds in (30, 60, 90, 120, 180):
        for max_entry_ask in (83, 85, 87, 90, 91, 93):
            for max_opp_pressure in (0.15, 0.30, 0.50):
                for min_bid_sum in (0, 94, 96, 98):
                    for max_spread in (4, 6, 10):
                        add(
                            "delayed_entry_survival_filter",
                            "A 90c signal should not be treated as mandatory; waiting for the quote to survive a short interval can transform weak high-price entries into no-trades or lower-price entries.",
                            "At delay D, enter at held_ask only if held_ask<=A, opp_bid/(own_bid+opp_bid)<=P, own_bid+opp_bid>=B, and own_ask-own_bid<=S; otherwise skip the trade.",
                            {
                                "delay_seconds": delay_seconds,
                                "max_entry_ask": max_entry_ask,
                                "max_opp_pressure": max_opp_pressure,
                                "min_bid_sum": min_bid_sum,
                                "max_spread": max_spread,
                            },
                            sim_delayed_entry_survival_filter,
                        )

    for delay_seconds in (60, 90, 120):
        for max_entry_ask in (87, 90, 92):
            for max_opp_pressure in (0.30, 0.50):
                for ask_bucket_cents in (5, 10):
                    for kelly_scale in (0.50, 1.00):
                        for max_fraction in (0.50, 1.00):
                            for min_edge_cents in (0, 2):
                                add(
                                    "empirical_kelly_entry_sizer",
                                    "Entry size should shrink or go to zero when a train-only empirical win probability does not pay for the delayed ask and fees.",
                                    "q_hat=BetaBinomial(P(win)|side, bucket(delayed_ask), bucket(pressure)); edge=100*q_hat-delayed_ask-fee; contracts=round(base_qty*clip(scale*edge/(100-delayed_ask),0,F)).",
                                    {
                                        "delay_seconds": delay_seconds,
                                        "max_entry_ask": max_entry_ask,
                                        "max_opp_pressure": max_opp_pressure,
                                        "min_bid_sum": 94,
                                        "max_spread": 6,
                                        "ask_bucket_cents": ask_bucket_cents,
                                        "pressure_bucket": 0.10,
                                        "min_cell_cases": 10,
                                        "prior_strength": 8,
                                        "kelly_scale": kelly_scale,
                                        "max_fraction": max_fraction,
                                        "min_edge_cents": min_edge_cents,
                                        "use_side": True,
                                    },
                                    sim_empirical_kelly_entry_sizer,
                                    build_kelly_model,
                                )

    return strategies


def row_for(case: dict[str, Any], pnl: float, meta: dict[str, Any], label: str) -> dict[str, Any]:
    return {
        "label": label,
        "dataset": case["dataset"],
        "market": case["market"],
        "side": case.get("side"),
        "entry_day_et": case["entry_day_et"],
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
        "avg_entry_ask": round(sum(float(row["entry_ask"]) for row in entered) / len(entered), 2) if entered else None,
        "total_contracts": total_contracts,
        "base_contracts": base_contracts,
        "contract_fraction": round(total_contracts / base_contracts, 4) if base_contracts else 0.0,
        "worst_trade": round(min(float(row["sim_pnl"]) for row in rows), 2) if rows else None,
    }


def summarize_by_dataset(label: str, rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        dataset: summarize_entry_rows(label, [row for row in rows if row["dataset"] == dataset])
        for dataset in sorted({row["dataset"] for row in rows})
    }


def summarize_by_side(label: str, rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        side: summarize_entry_rows(label, [row for row in rows if str(row.get("side")) == side])
        for side in sorted({str(row.get("side")) for row in rows})
    }


def run_strategy(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]],
    strategy: StrategySpec,
    *,
    model_prepped: list[tuple[dict[str, Any], dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    sid = strategy_id(strategy.family, strategy.params)
    model = strategy.model_builder(model_prepped or prepped, strategy.params) if strategy.model_builder else None
    rows: list[dict[str, Any]] = []
    for case, prepared in prepped:
        pnl, meta = strategy.simulator(case, prepared, strategy.params, model)
        rows.append(row_for(case, pnl, meta, sid))
    return {
        "strategy_id": sid,
        "family": strategy.family,
        "theorem": strategy.theorem,
        "equation": strategy.equation,
        "params": strategy.params,
        "model_summary": {
            "train_cases": model.get("train_cases") if model else None,
            "global_q": round(float(model.get("global_q")), 6) if model else None,
            "cells": len(model.get("counts", {})) if model else None,
        },
        "summary": summarize_entry_rows(sid, rows),
        "by_dataset": summarize_by_dataset(sid, rows),
        "by_side": summarize_by_side(sid, rows),
        "interesting_examples": sorted(rows, key=lambda row: (float(row["sim_pnl"]), row["market"]))[:10],
    }


def select_family_best(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for result in results:
        family = result["family"]
        summary = result["summary"]
        key = (summary["sim_pnl"], summary["delta_vs_no_trade_all"], -summary["skipped_settlement_winners"])
        if family not in best:
            best[family] = result
            continue
        old_summary = best[family]["summary"]
        old_key = (
            old_summary["sim_pnl"],
            old_summary["delta_vs_no_trade_all"],
            -old_summary["skipped_settlement_winners"],
        )
        if key > old_key:
            best[family] = result
    return best


def sensitivity(results: list[dict[str, Any]], best_by_family: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    for family, best in best_by_family.items():
        ranked = sorted(
            [result for result in results if result["family"] == family],
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
                "skipped_winners": result["summary"]["skipped_settlement_winners"],
                "skipped_losers": result["summary"]["skipped_settlement_losers"],
            }
            for result in ranked[:12]
        ]
    return output


def walk_forward_summary(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]], strategies: list[StrategySpec]
) -> dict[str, Any]:
    ordered = sorted(prepped, key=lambda item: item[0]["entry_ts"])
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
        "families": {},
    }
    for family, family_strategies in by_family.items():
        train_results = [
            run_strategy(train, strategy, model_prepped=train)
            for strategy in family_strategies
        ]
        selected_train = max(train_results, key=lambda result: result["summary"]["sim_pnl"])
        selected_spec = next(
            strategy
            for strategy in family_strategies
            if strategy_id(strategy.family, strategy.params) == selected_train["strategy_id"]
        )
        holdout_result = run_strategy(holdout, selected_spec, model_prepped=train)
        output["families"][family] = {
            "selected_strategy_id": selected_train["strategy_id"],
            "selected_params": selected_train["params"],
            "train_summary": selected_train["summary"],
            "holdout_summary": holdout_result["summary"],
            "holdout_by_dataset": holdout_result["by_dataset"],
            "holdout_by_side": holdout_result["by_side"],
        }
    return output


def robust_positive_scan(results: list[dict[str, Any]], walk: dict[str, Any], strategies: list[StrategySpec], prepped: list[tuple[dict[str, Any], dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
    del results
    ordered = sorted(prepped, key=lambda item: item[0]["entry_ts"])
    split = int(len(ordered) * 0.7)
    train = ordered[:split]
    holdout = ordered[split:]
    output: dict[str, list[dict[str, Any]]] = {}
    for family in walk["families"]:
        family_specs = [strategy for strategy in strategies if strategy.family == family]
        rows: list[dict[str, Any]] = []
        for strategy in family_specs:
            train_result = run_strategy(train, strategy, model_prepped=train)
            holdout_result = run_strategy(holdout, strategy, model_prepped=train)
            train_pnl = train_result["summary"]["sim_pnl"]
            holdout_pnl = holdout_result["summary"]["sim_pnl"]
            if train_pnl <= 0 or holdout_pnl <= 0:
                continue
            rows.append(
                {
                    "strategy_id": train_result["strategy_id"],
                    "params": train_result["params"],
                    "train_sim_pnl": train_pnl,
                    "holdout_sim_pnl": holdout_pnl,
                    "min_split_pnl": min(train_pnl, holdout_pnl),
                    "holdout_entries": holdout_result["summary"]["entries"],
                    "holdout_entry_win_rate": holdout_result["summary"]["entry_win_rate"],
                }
            )
        output[family] = sorted(rows, key=lambda row: (row["min_split_pnl"], row["holdout_sim_pnl"]), reverse=True)[:10]
    return output


def read_truffle_reference() -> dict[str, Any] | None:
    path = Path("logs/online_exit_supervisor_policy_eval_latest.json")
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    best: dict[str, Any] | None = None
    for delay in payload.get("delays", []):
        for row in delay.get("top_policies", [])[:3]:
            candidate = {
                "path": str(path),
                "delay_seconds": delay.get("delay_seconds"),
                "case_count": delay.get("case_count"),
                "policy": row.get("policy"),
                "rule": row.get("rule"),
                "delta_dollars": row.get("delta_dollars"),
                "exit_count": row.get("exit_count"),
            }
            if best is None or float(candidate.get("delta_dollars") or -999999) > float(best.get("delta_dollars") or -999999):
                best = candidate
    return best


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    actual = payload["baselines"]["actual"]["summary"]
    no_stop = payload["baselines"]["no_stop"]["summary"]
    stop70 = payload["baselines"]["held_ask_stop_70"]["summary"]
    lines = [
        "# Codex Entry Timing Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Quote-path cases: `{payload['case_count']}`",
        "- Scope: research-only entry/no-trade and sizing simulation; live bot logic, configs, run scripts, and processes were not changed.",
        "- Non-repetition: this intentionally avoids the prior stop-touch, terminal-salvage, calibrated-exit, path-efficiency, and parity-consistency families.",
        "",
        "## Baselines",
        "",
        f"- Actual recorded PnL: `${actual['sim_pnl']}`",
        f"- No-stop hold-to-settlement PnL using original entries: `${no_stop['sim_pnl']}`",
        f"- First held-ask <=70 exit baseline: `${stop70['sim_pnl']}`",
        "- Skip every opportunity baseline: `$0.0`",
        "",
        "## New Equation Families",
        "",
    ]
    for family, result in payload["best_by_family"].items():
        summary = result["summary"]
        walk = payload["walk_forward"]["families"][family]
        holdout = walk["holdout_summary"]
        lines.extend(
            [
                f"### {family} `{result['strategy_id']}`",
                "",
                f"- Theorem: {result['theorem']}",
                f"- Equation: `{result['equation']}`",
                f"- Full-sample best params: `{json.dumps(result['params'], sort_keys=True)}`",
                f"- Full-sample PnL / delta vs actual / delta vs no-stop / delta vs skip-all: `${summary['sim_pnl']}` / `${summary['delta_vs_actual']}` / `${summary['delta_vs_no_stop']}` / `${summary['delta_vs_no_trade_all']}`",
                f"- Entries / skipped winners / skipped losers / win rate: `{summary['entries']} / {summary['skipped_settlement_winners']} / {summary['skipped_settlement_losers']} / {summary['entry_win_rate']}`",
                f"- Avg entry ask / contract fraction: `{summary['avg_entry_ask']} / {summary['contract_fraction']}`",
                f"- Train-selected params: `{json.dumps(walk['selected_params'], sort_keys=True)}`",
                f"- Train-selected holdout PnL / delta vs actual / delta vs no-stop / delta vs skip-all: `${holdout['sim_pnl']}` / `${holdout['delta_vs_actual']}` / `${holdout['delta_vs_no_stop']}` / `${holdout['delta_vs_no_trade_all']}`",
                f"- Holdout entries / skipped winners / skipped losers / win rate: `{holdout['entries']} / {holdout['skipped_settlement_winners']} / {holdout['skipped_settlement_losers']} / {holdout['entry_win_rate']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Robust Positive Split Scan",
            "",
            "| Family | Strategy | Train PnL | Holdout PnL | Holdout entries | Params |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for family, rows in payload["robust_positive_scan"].items():
        for row in rows[:5]:
            lines.append(
                f"| `{family}` | `{row['strategy_id']}` | {row['train_sim_pnl']} | {row['holdout_sim_pnl']} | "
                f"{row['holdout_entries']} | `{json.dumps(row['params'], sort_keys=True)}` |"
            )
        if not rows:
            lines.append(f"| `{family}` | none |  |  |  | no train-positive and holdout-positive parameterization found |")
    lines.extend(
        [
            "",
            "## Nearby Sensitivity",
            "",
            "| Family | Params | PnL | Delta vs skip-all | Entries | Win rate | Skipped W/L |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for family, rows in payload["sensitivity"].items():
        for row in rows[:6]:
            lines.append(
                f"| `{family}` | `{json.dumps(row['params'], sort_keys=True)}` | {row['sim_pnl']} | "
                f"{row['delta_vs_no_trade_all']} | {row['entries']} | {row['entry_win_rate']} | "
                f"{row['skipped_winners']}/{row['skipped_losers']} |"
            )
    truffle = payload.get("truffle_reference")
    lines.extend(["", "## Truffle Reference", ""])
    if truffle:
        lines.append(
            f"- Reference-only: latest online exit supervisor eval best visible policy `{truffle['policy']}` / `{truffle['rule']}` at delay `{truffle['delay_seconds']}` had delta `${truffle['delta_dollars']}` on `{truffle['case_count']}` `live_90_70` stop-slice cases. This is not directly comparable to all-opportunity delayed entry admission."
        )
    else:
        lines.append("- No current Truffle policy reference file was available for a direct comparison.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Delayed entry admission is a materially new branch because skipped opportunities earn zero instead of forcing a 90c entry or looking for a later exit.",
            "- The best full-sample delayed-entry parameters are positive even against the skip-all baseline, but train-only selection does not pick the same robust setting; this needs a pre-registered validation split before any live consideration.",
            "- The Kelly-style sizing branch is useful as a calibration diagnostic, but any positive in-sample result should be discounted unless the train-selected holdout also beats skip-all.",
            "- All features are taken from the quote heartbeat at or after the configured delay, so the tested variables are available at decision time.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only delayed entry and Kelly sizing edge tests.")
    parser.add_argument("--refresh-cache", action="store_true")
    parser.add_argument("--datasets", nargs="*", default=None)
    args = parser.parse_args()

    datasets = args.datasets or discover_datasets()
    payloads = [load_dataset_cases(dataset, refresh_cache=args.refresh_cache) for dataset in datasets]
    cases: list[dict[str, Any]] = []
    for item in payloads:
        cases.extend(item.get("cases", []))
    cases = sorted(cases, key=lambda case: (case["entry_ts"], case["market"], case["side"]))

    strategies = build_strategy_grid()
    delays = tuple(sorted({int(strategy.params["delay_seconds"]) for strategy in strategies}))
    prepped = [(case, prepare_case(case, delays)) for case in cases]
    results = [run_strategy(prepped, strategy) for strategy in strategies]
    best_by_family = select_family_best(results)
    walk = walk_forward_summary(prepped, strategies)
    robust_scan = robust_positive_scan(results, walk, strategies, prepped)

    baselines = {
        "actual": run_baseline(cases, "actual"),
        "no_stop": run_baseline(cases, "no_stop"),
        "held_ask_stop_70": run_baseline(cases, "held_ask_stop_70"),
    }
    generated_at = datetime.now(UTC).isoformat()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"codex_entry_timing_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_entry_timing_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_entry_timing_research_latest.json"
    latest_md = EDGE_DIR / "codex_entry_timing_research_latest.md"

    report_payload = {
        "generated_at": generated_at,
        "datasets": sorted({case["dataset"] for case in cases}),
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
        "truffle_reference": read_truffle_reference(),
        "json_path": str(json_path),
        "markdown_path": str(md_path),
    }

    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_payload, indent=2, sort_keys=True), encoding="utf-8")
    latest_json.write_text(json.dumps(report_payload, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(md_path, report_payload)
    write_markdown(latest_md, report_payload)

    ledger_records: list[dict[str, Any]] = []
    for family, result in best_by_family.items():
        walk_family = walk["families"][family]
        status = "tested_not_robust"
        summary = result["summary"]
        holdout = walk_family["holdout_summary"]
        robust_rows = robust_scan.get(family, [])
        if summary["delta_vs_no_trade_all"] > 0 and holdout["delta_vs_no_trade_all"] > 0:
            status = "candidate_for_human_review"
        elif summary["delta_vs_no_trade_all"] > 0 and robust_rows:
            status = "watchlist_positive_but_selection_sensitive"
        ledger_records.append(
            {
                "recorded_at": generated_at,
                "generated_at": generated_at,
                "source": Path(__file__).name,
                "status": status,
                "dataset": "all_quote_path_trades",
                "datasets": sorted({case["dataset"] for case in cases}),
                "family": family,
                "theorem": result["theorem"],
                "equation": result["equation"],
                "params": result["params"],
                "strategy_id": result["strategy_id"],
                "idea_key": idea_key(family, result["equation"], result["params"]),
                "summary": summary,
                "train_summary": walk_family["train_summary"],
                "holdout_summary": holdout,
                "walk_forward_selected_strategy_id": walk_family["selected_strategy_id"],
                "walk_forward_selected_params": walk_family["selected_params"],
                "robust_positive_count": len(robust_rows),
                "json_path": str(json_path),
                "markdown_path": str(md_path),
            }
        )
    append_ledger(ledger_records)
    update_strategy_memory(report_payload, best_by_family)

    print(
        f"wrote {md_path} and {json_path}; "
        + ", ".join(
            f"{family} sim={result['summary']['sim_pnl']} holdout={walk['families'][family]['holdout_summary']['sim_pnl']}"
            for family, result in best_by_family.items()
        )
    )


if __name__ == "__main__":
    main()
