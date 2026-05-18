from __future__ import annotations

import argparse
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from probe_codex_terminal_salvage_all_trades import discover_datasets, load_dataset_cases
from probe_stop_touch_confirmation import append_ledger, idea_key, strategy_id, update_strategy_memory
from validate_btc_spot_synthetic_ev_broad import (
    EDGE_DIR,
    UTC,
    StrategySpec,
    baseline_payload,
    entry_meta,
    load_or_fetch_candles,
    prepare_case,
    quote_gate,
    row_for,
    run_strategy,
    safe_float,
    summarize_by_group,
    summarize_entry_rows,
    synthetic_ev_score,
)


BASE_CANDIDATE_PARAMS = {
    "delay_seconds": 120,
    "intercept": 1.5,
    "location_weight": 1.0,
    "macd_weight": 0.0,
    "max_entry_ask": 88,
    "max_opp_pressure": 0.3,
    "max_spread": 4,
    "min_bid_sum": 0,
    "min_ev_cents": 2.0,
    "move_scale": 0.25,
    "pressure_penalty": 0.5,
    "range_penalty": 0.0,
    "rsi_weight": 0.0,
    "side_polarity": 1,
    "spread_penalty": 0.03,
    "w_15m": 0.0,
    "w_1m": 0.0,
    "w_5m": 1.0,
}

BASE_THEOREM = (
    "The broad BTC spot EV candidate should survive stress tests when treated as a fixed decision rule, not only as "
    "the full-sample winner from a larger grid."
)
BASE_EQUATION = (
    "q=sigmoid(c+a*s*m5/sqrt(R15)+b*s*(dist_low-dist_high)/R15-lambda*p_opp-mu*spread); "
    "EV=100*q-H-fee; enter if EV>=e and quote gates pass."
)


def load_cases(datasets: list[str] | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected = datasets or discover_datasets()
    payloads = [load_dataset_cases(dataset, refresh_cache=False) for dataset in selected]
    cases: list[dict[str, Any]] = []
    for payload in payloads:
        dataset = payload.get("dataset")
        for case in payload.get("cases", []):
            case.setdefault("dataset", dataset)
            cases.append(case)
    return sorted(cases, key=lambda item: (item["entry_ts"], item["market"], item["side"])), payloads


def enriched_score(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[dict[str, Any] | None, dict[str, float] | None]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not quote_gate(features, params):
        return None, None
    scored = synthetic_ev_score(case, features, params)
    if scored is None:
        return None, None
    ask = safe_float(features.get("held_ask"))
    fee = safe_float(scored.get("fee_per_contract"))
    ev = safe_float(scored.get("ev_cents"))
    q_spot = safe_float(scored.get("q_spot"))
    btc_range = safe_float(features.get("btc_range_15m_bps"))
    if any(math.isnan(value) for value in (ask, fee, ev, q_spot, btc_range)):
        return None, None
    roi = ev / max(1.0, ask + fee)
    scored = {
        **scored,
        "entry_ask": ask,
        "roi": roi,
        "btc_range_15m_bps": btc_range,
        "btc_move_5m_bps": safe_float(features.get("btc_move_5m_bps")),
        "btc_age_seconds": safe_float(features.get("btc_age_seconds")),
    }
    return features, scored


def passes_quality_filters(features: dict[str, Any], scored: dict[str, float], params: dict[str, Any]) -> tuple[bool, str]:
    if scored["ev_cents"] < float(params["min_ev_cents"]):
        return False, "ev_too_low"
    if scored["roi"] < float(params.get("min_roi", 0.0)):
        return False, "roi_too_low"
    min_q = float(params.get("min_q_spot", 0.0))
    if min_q and scored["q_spot"] < min_q:
        return False, "q_too_low"
    max_range = params.get("max_range_15m_bps")
    if max_range is not None and scored["btc_range_15m_bps"] > float(max_range):
        return False, "range_too_high"
    return True, "ok"


def sim_base_fixed_candidate(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features, scored = enriched_score(case, prepared, params)
    if not features or not scored:
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    passed, reason = passes_quality_filters(features, scored, params)
    if not passed:
        return 0.0, {"enter": False, "skip_reason": reason, "score": round(scored["ev_cents"], 6)}
    return entry_meta(
        case,
        features,
        {
            "score": round(scored["ev_cents"], 6),
            "q_spot": round(scored["q_spot"], 6),
            "roi": round(scored["roi"], 6),
            "btc_range_15m_bps": round(scored["btc_range_15m_bps"], 6),
        },
    )


def sim_score_scaled_sizer(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features, scored = enriched_score(case, prepared, params)
    if not features or not scored:
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    passed, reason = passes_quality_filters(features, scored, params)
    if not passed:
        return 0.0, {"enter": False, "skip_reason": reason, "score": round(scored["ev_cents"], 6)}

    edge = max(0.0, scored["ev_cents"] - float(params["min_ev_cents"]))
    raw_multiplier = 1.0 + edge / max(1.0, float(params["score_unit_cents"]))
    multiplier = min(float(params["max_multiplier"]), raw_multiplier)
    base_qty = max(1, int(case["qty"]))
    contracts = min(int(params["max_contracts"]), max(1, int(math.floor(base_qty * multiplier))))
    return entry_meta(
        case,
        features,
        {
            "score": round(scored["ev_cents"], 6),
            "q_spot": round(scored["q_spot"], 6),
            "roi": round(scored["roi"], 6),
            "size_multiplier": round(contracts / base_qty, 4),
            "btc_range_15m_bps": round(scored["btc_range_15m_bps"], 6),
        },
        contracts=contracts,
    )


def build_refinement_grid() -> list[StrategySpec]:
    strategies: list[StrategySpec] = []

    strategies.append(
        StrategySpec(
            "btc_spot_ev_fixed_candidate_stress",
            BASE_THEOREM,
            BASE_EQUATION,
            dict(BASE_CANDIDATE_PARAMS),
            sim_base_fixed_candidate,
        )
    )

    roi_theorem = (
        "The BTC EV signal should be stronger when the cents edge is large relative to entry risk and when the "
        "recent BTC range is not too expanded."
    )
    roi_equation = (
        "q=sigmoid(c+a*s*m5/sqrt(R15)+b*s*location-lambda*p_opp-mu*spread); "
        "EV=100*q-H-fee; ROI=EV/(H+fee); enter if EV>=e, ROI>=r, R15<=Rmax, and q>=qmin."
    )
    for delay_seconds in (90, 120, 150):
        for max_entry_ask in (86, 88, 90):
            for max_opp_pressure in (0.25, 0.30):
                for max_spread in (4, 6):
                    for min_ev_cents in (2.0, 4.0, 6.0):
                        for min_roi in (0.0, 0.04, 0.08):
                            for max_range_15m_bps in (None, 75.0, 100.0):
                                for min_q_spot in (0.0, 0.90):
                                    params = {
                                        **BASE_CANDIDATE_PARAMS,
                                        "delay_seconds": delay_seconds,
                                        "max_entry_ask": max_entry_ask,
                                        "max_opp_pressure": max_opp_pressure,
                                        "max_spread": max_spread,
                                        "min_ev_cents": min_ev_cents,
                                        "min_roi": min_roi,
                                        "max_range_15m_bps": max_range_15m_bps,
                                        "min_q_spot": min_q_spot,
                                    }
                                    strategies.append(
                                        StrategySpec(
                                            "btc_spot_ev_roi_volatility_refinement",
                                            roi_theorem,
                                            roi_equation,
                                            params,
                                            sim_base_fixed_candidate,
                                        )
                                    )

    sizing_theorem = (
        "If the EV score is calibrated enough for admission, higher edge should support modestly larger size while "
        "still clipping per-trade exposure."
    )
    sizing_equation = (
        "contracts=min(Cmax,floor(qty*min(Mmax,1+(EV-e)/u))); enter through the same EV/ROI/range gates, then size by "
        "score margin."
    )
    for max_entry_ask in (88, 90):
        for max_opp_pressure in (0.25, 0.30):
            for min_ev_cents in (2.0, 4.0, 6.0):
                for min_roi in (0.0, 0.04):
                    for max_range_15m_bps in (None, 75.0, 100.0):
                        for max_multiplier in (1.5, 2.0, 3.0):
                            for score_unit_cents in (5.0, 10.0):
                                for max_contracts in (20, 30):
                                    params = {
                                        **BASE_CANDIDATE_PARAMS,
                                        "max_entry_ask": max_entry_ask,
                                        "max_opp_pressure": max_opp_pressure,
                                        "min_ev_cents": min_ev_cents,
                                        "min_roi": min_roi,
                                        "max_range_15m_bps": max_range_15m_bps,
                                        "max_multiplier": max_multiplier,
                                        "score_unit_cents": score_unit_cents,
                                        "max_contracts": max_contracts,
                                    }
                                    strategies.append(
                                        StrategySpec(
                                            "btc_spot_ev_score_scaled_sizer",
                                            sizing_theorem,
                                            sizing_equation,
                                            params,
                                            sim_score_scaled_sizer,
                                        )
                                    )
    return strategies


def rows_for_strategy(prepped: list[tuple[dict[str, Any], dict[str, Any]]], strategy: StrategySpec) -> list[dict[str, Any]]:
    sid = strategy_id(strategy.family, strategy.params)
    rows: list[dict[str, Any]] = []
    for case, prepared in prepped:
        pnl, meta = strategy.simulator(case, prepared, strategy.params)
        row = row_for(case, pnl, meta, sid)
        for key in ("q_spot", "roi", "btc_range_15m_bps", "size_multiplier", "pressure", "spread", "bid_sum"):
            if key in meta:
                row[key] = meta[key]
        rows.append(row)
    return rows


def max_drawdown(rows: list[dict[str, Any]]) -> float:
    cumulative = 0.0
    peak = 0.0
    worst = 0.0
    for row in sorted(rows, key=lambda item: (item["entry_ts"], item["market"], item["side"])):
        cumulative += float(row["sim_pnl"])
        peak = max(peak, cumulative)
        worst = min(worst, cumulative - peak)
    return round(worst, 2)


def day_bootstrap(rows: list[dict[str, Any]], iterations: int = 2000) -> dict[str, Any]:
    by_day: dict[str, float] = {}
    for row in rows:
        by_day[row["entry_day_et"]] = by_day.get(row["entry_day_et"], 0.0) + float(row["sim_pnl"])
    values = [round(value, 6) for value in by_day.values()]
    if not values:
        return {"day_count": 0}
    rng = random.Random(1701)
    samples = []
    for _ in range(iterations):
        samples.append(sum(rng.choice(values) for _ in values))
    samples.sort()
    active_day_pnls = [
        sum(float(row["sim_pnl"]) for row in rows if row["entry_day_et"] == day and row["action"] == "enter")
        for day in sorted(by_day)
    ]
    active_day_pnls = [value for value in active_day_pnls if abs(value) > 1e-12]
    return {
        "day_count": len(values),
        "active_day_count": len(active_day_pnls),
        "negative_active_days": sum(1 for value in active_day_pnls if value < 0),
        "positive_active_days": sum(1 for value in active_day_pnls if value > 0),
        "worst_day_pnl": round(min(values), 2),
        "best_day_pnl": round(max(values), 2),
        "bootstrap_p05": round(samples[int(0.05 * (len(samples) - 1))], 2),
        "bootstrap_p50": round(samples[int(0.50 * (len(samples) - 1))], 2),
        "bootstrap_p95": round(samples[int(0.95 * (len(samples) - 1))], 2),
        "bootstrap_prob_positive": round(sum(1 for sample in samples if sample > 0) / len(samples), 4),
    }


def risk_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    entered = [row for row in rows if row["action"] == "enter"]
    losers = sorted((float(row["sim_pnl"]) for row in entered if float(row["sim_pnl"]) < 0))
    return {
        "max_drawdown": max_drawdown(rows),
        "loss_count": len(losers),
        "loss_sum": round(sum(losers), 2),
        "avg_loss": round(sum(losers) / len(losers), 4) if losers else 0.0,
        "worst_3_loss_sum": round(sum(losers[:3]), 2) if losers else 0.0,
        "day_bootstrap": day_bootstrap(rows),
    }


def result_with_rows(prepped: list[tuple[dict[str, Any], dict[str, Any]]], strategy: StrategySpec) -> dict[str, Any]:
    sid = strategy_id(strategy.family, strategy.params)
    rows = rows_for_strategy(prepped, strategy)
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
        "risk": risk_summary(rows),
        "worst_examples": sorted(rows, key=lambda row: (float(row["sim_pnl"]), row["market"]))[:10],
    }


def select_best_by_family(results: list[dict[str, Any]], min_entries: int = 25) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for family in sorted({result["family"] for result in results}):
        family_results = [result for result in results if result["family"] == family]
        candidates = [result for result in family_results if result["summary"]["entries"] >= min_entries] or family_results
        output[family] = max(
            candidates,
            key=lambda result: (
                result["summary"]["sim_pnl"],
                result["summary"]["entry_win_rate"],
                -abs(result["summary"]["total_contracts"]),
            ),
        )
    return output


def top_candidates(results: list[dict[str, Any]], per_family: int = 80) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for family in sorted({result["family"] for result in results}):
        family_rows = [
            result
            for result in results
            if result["family"] == family and result["summary"]["entries"] >= 20 and result["summary"]["sim_pnl"] > 0
        ]
        selected.extend(
            sorted(
                family_rows,
                key=lambda result: (
                    result["summary"]["sim_pnl"],
                    result["summary"]["entry_win_rate"],
                    -result["summary"]["total_contracts"],
                ),
                reverse=True,
            )[:per_family]
        )
    return selected


def find_spec(strategies: list[StrategySpec], result: dict[str, Any]) -> StrategySpec:
    sid = result["strategy_id"]
    return next(strategy for strategy in strategies if strategy_id(strategy.family, strategy.params) == sid)


def chronological_holdout(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]], strategies: list[StrategySpec], candidates: list[dict[str, Any]]
) -> dict[str, Any]:
    ordered = sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
    split = int(len(ordered) * 0.7)
    train = ordered[:split]
    holdout = ordered[split:]
    output: dict[str, Any] = {}
    for family in sorted({result["family"] for result in candidates}):
        family_candidates = [result for result in candidates if result["family"] == family]
        train_scored = []
        for result in family_candidates:
            strategy = find_spec(strategies, result)
            train_scored.append(run_strategy(train, strategy))
        train_candidates = [item for item in train_scored if item["summary"]["entries"] >= 20] or train_scored
        selected = max(train_candidates, key=lambda item: item["summary"]["sim_pnl"])
        strategy = find_spec(strategies, selected)
        holdout_result = run_strategy(holdout, strategy)
        output[family] = {
            "selected_strategy_id": selected["strategy_id"],
            "selected_params": selected["params"],
            "train_summary": selected["summary"],
            "holdout_summary": holdout_result["summary"],
            "holdout_by_dataset": holdout_result["by_dataset"],
            "holdout_by_side": holdout_result["by_side"],
        }
    return output


def leave_one_dataset(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]], strategies: list[StrategySpec], candidates: list[dict[str, Any]]
) -> dict[str, Any]:
    datasets = sorted({case["dataset"] for case, _prepared in prepped})
    output: dict[str, Any] = {}
    for family in sorted({result["family"] for result in candidates}):
        output[family] = {}
        family_candidates = [result for result in candidates if result["family"] == family]
        for dataset in datasets:
            train = [item for item in prepped if item[0]["dataset"] != dataset]
            test = [item for item in prepped if item[0]["dataset"] == dataset]
            train_results = []
            for result in family_candidates:
                strategy = find_spec(strategies, result)
                train_results.append(run_strategy(train, strategy))
            train_candidates = [item for item in train_results if item["summary"]["entries"] >= 20] or train_results
            selected = max(train_candidates, key=lambda item: item["summary"]["sim_pnl"])
            test_result = run_strategy(test, find_spec(strategies, selected))
            output[family][dataset] = {
                "selected_strategy_id": selected["strategy_id"],
                "selected_params": selected["params"],
                "train_summary": selected["summary"],
                "test_summary": test_result["summary"],
            }
    return output


def fixed_candidate_fold_stress(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]], base_strategy: StrategySpec, folds: int = 5
) -> list[dict[str, Any]]:
    ordered = sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
    output: list[dict[str, Any]] = []
    for fold in range(folds):
        lo = int(len(ordered) * fold / folds)
        hi = int(len(ordered) * (fold + 1) / folds)
        test = ordered[lo:hi]
        result = run_strategy(test, base_strategy)
        output.append(
            {
                "fold": fold + 1,
                "n": len(test),
                "start_entry_ts": test[0][0]["entry_ts"] if test else None,
                "end_entry_ts": test[-1][0]["entry_ts"] if test else None,
                "summary": result["summary"],
                "by_dataset": result["by_dataset"],
            }
        )
    return output


def status_for(family: str, result: dict[str, Any], base_summary: dict[str, Any], validation: dict[str, Any]) -> str:
    holdout = validation.get("chronological_holdout", {}).get(family, {}).get("holdout_summary", {})
    leaveouts = validation.get("leave_one_dataset", {}).get(family, {})
    positive_leaveouts = sum(1 for item in leaveouts.values() if item.get("test_summary", {}).get("sim_pnl", 0.0) > 0)
    if family == "btc_spot_ev_score_scaled_sizer":
        if result["summary"]["sim_pnl"] > base_summary["sim_pnl"] and holdout.get("sim_pnl", 0.0) > 0:
            return "watchlist_higher_pnl_but_size_risk"
        return "tested_size_variant_not_robust"
    if (
        result["summary"]["sim_pnl"] >= base_summary["sim_pnl"]
        and holdout.get("sim_pnl", 0.0) > 0
        and positive_leaveouts >= max(1, len(leaveouts) - 1)
    ):
        return "candidate_for_human_review"
    if result["summary"]["sim_pnl"] > 0 and holdout.get("sim_pnl", 0.0) > 0:
        return "watchlist_positive_selection_sensitive"
    if result["summary"]["sim_pnl"] > 0:
        return "watchlist_positive_not_robust"
    return "tested_negative"


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    base = payload["base_candidate"]["summary"]
    lines = [
        "# BTC Spot Synthetic EV Candidate Refinement",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Cases: `{payload['case_count']}` across `{', '.join(payload['datasets'])}`",
        f"- Variants tested: `{payload['strategy_count']}`",
        "- Scope: research-only; live entry/exit logic, configs, run scripts, and bot processes were not changed.",
        "",
        "## Baselines",
        "",
        f"- Actual recorded PnL: `${payload['baselines']['actual']['summary']['sim_pnl']}`",
        f"- No-stop hold-to-settlement PnL: `${payload['baselines']['no_stop']['summary']['sim_pnl']}`",
        f"- First held-ask <=70 baseline: `${payload['baselines']['held_ask_stop_70']['summary']['sim_pnl']}`",
        "- Skip-all baseline: `$0.0`",
        "",
        "## Fixed Candidate Stress",
        "",
        f"- Strategy: `{payload['base_candidate']['strategy_id']}`",
        f"- Params: `{json.dumps(payload['base_candidate']['params'], sort_keys=True)}`",
        f"- PnL / delta vs actual / delta vs no-stop / entries / win rate: `${base['sim_pnl']}` / `${base['delta_vs_actual']}` / `${base['delta_vs_no_stop']}` / `{base['entries']}` / `{base['entry_win_rate']}`",
        f"- Risk: `{json.dumps(payload['base_candidate']['risk'], sort_keys=True)}`",
        "",
        "### Five Chronological Folds",
        "",
        "| Fold | PnL | Entries | Win rate | Worst trade | Start | End |",
        "|---:|---:|---:|---:|---:|---|---|",
    ]
    for fold in payload["fixed_candidate_folds"]:
        summary = fold["summary"]
        lines.append(
            f"| {fold['fold']} | {summary['sim_pnl']} | {summary['entries']} | {summary['entry_win_rate']} | "
            f"{summary['worst_trade']} | `{fold['start_entry_ts']}` | `{fold['end_entry_ts']}` |"
        )

    lines.extend(["", "## Best Refinements", ""])
    for family, result in payload["best_by_family"].items():
        if family == "btc_spot_ev_fixed_candidate_stress":
            continue
        summary = result["summary"]
        risk = result["risk"]
        holdout = payload["chronological_holdout"].get(family, {}).get("holdout_summary", {})
        lines.extend(
            [
                f"### {family} `{result['strategy_id']}`",
                "",
                f"- Status: {status_for(family, result, base, payload)}",
                f"- Equation: `{result['equation']}`",
                f"- Params: `{json.dumps(result['params'], sort_keys=True)}`",
                f"- Full PnL / delta vs actual / delta vs no-stop / entries / win rate: `${summary['sim_pnl']}` / `${summary['delta_vs_actual']}` / `${summary['delta_vs_no_stop']}` / `{summary['entries']}` / `{summary['entry_win_rate']}`",
                f"- Holdout PnL / entries / win rate: `${holdout.get('sim_pnl')}` / `{holdout.get('entries')}` / `{holdout.get('entry_win_rate')}`",
                f"- Risk: `{json.dumps(risk, sort_keys=True)}`",
                "- By dataset: `"
                + "; ".join(
                    f"{dataset}: ${item['sim_pnl']} ({item['entries']} entries)"
                    for dataset, item in sorted(result["by_dataset"].items())
                )
                + "`",
                "",
            ]
        )

    lines.extend(
        [
            "## Leave-One-Dataset Selection",
            "",
            "| Family | Left-out dataset | Test PnL | Entries | Win rate | Selected strategy |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for family, datasets in payload["leave_one_dataset"].items():
        for dataset, item in datasets.items():
            summary = item["test_summary"]
            lines.append(
                f"| `{family}` | `{dataset}` | {summary['sim_pnl']} | {summary['entries']} | "
                f"{summary['entry_win_rate']} | `{item['selected_strategy_id']}` |"
            )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The fixed candidate remains the cleanest signal because it is not helped by additional sizing assumptions.",
            "- ROI/range refinements are useful only if they improve out-of-sample or dataset balance, not just full-sample PnL.",
            "- Score-scaled sizing can raise dollars but is not capital-neutral; it needs risk-budget review before any live discussion.",
            "- Side mapping and forward shadowing remain required before live consideration.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Focused refinement and stress testing for the broad BTC spot EV candidate.")
    parser.add_argument("--refresh-cache", action="store_true")
    parser.add_argument("--datasets", nargs="*", default=None)
    args = parser.parse_args()

    cases, dataset_payloads = load_cases(args.datasets)
    strategies = build_refinement_grid()
    delays = tuple(sorted({int(strategy.params["delay_seconds"]) for strategy in strategies}))
    candles = load_or_fetch_candles(cases, refresh_cache=args.refresh_cache)
    prepped = [(case, prepare_case(case, candles, delays)) for case in cases]

    results = [run_strategy(prepped, strategy) for strategy in strategies]
    best_shallow = select_best_by_family(results)
    best_by_family = {family: result_with_rows(prepped, find_spec(strategies, result)) for family, result in best_shallow.items()}
    top = top_candidates(results, per_family=80)
    validation = {
        "chronological_holdout": chronological_holdout(prepped, strategies, top),
        "leave_one_dataset": leave_one_dataset(prepped, strategies, top),
    }

    base_strategy = find_spec(strategies, best_by_family["btc_spot_ev_fixed_candidate_stress"])
    fixed_folds = fixed_candidate_fold_stress(prepped, base_strategy)

    generated_at = datetime.now(timezone.utc).isoformat()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"btc_spot_synthetic_ev_candidate_refinement_{stamp}.json"
    md_path = EDGE_DIR / f"btc_spot_synthetic_ev_candidate_refinement_{stamp}.md"
    latest_json = EDGE_DIR / "btc_spot_synthetic_ev_candidate_refinement_latest.json"
    latest_md = EDGE_DIR / "btc_spot_synthetic_ev_candidate_refinement_latest.md"

    payload = {
        "generated_at": generated_at,
        "dataset": "all_quote_path_trades_with_closed_1m_btc",
        "datasets": sorted({str(case.get("dataset")) for case, _prepared in prepped}),
        "requested_datasets": args.datasets or discover_datasets(),
        "dataset_payloads": [
            {
                "dataset": payload.get("dataset"),
                "raw_trades_total": payload.get("raw_trades_total"),
                "trades_total": payload.get("trades_total"),
                "case_count": len(payload.get("cases", [])),
                "cache_path": payload.get("cache_path"),
            }
            for payload in dataset_payloads
        ],
        "case_count": len(prepped),
        "raw_case_count": len(cases),
        "strategy_count": len(strategies),
        "baselines": baseline_payload([case for case, _prepared in prepped]),
        "base_candidate": best_by_family["btc_spot_ev_fixed_candidate_stress"],
        "fixed_candidate_folds": fixed_folds,
        "best_by_family": best_by_family,
        "top_candidates": top[:30],
        "chronological_holdout": validation["chronological_holdout"],
        "leave_one_dataset": validation["leave_one_dataset"],
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "live_logic_changed": False,
    }

    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(payload, indent=2, sort_keys=True)
    json_path.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")
    write_markdown(md_path, payload)
    write_markdown(latest_md, payload)

    base_summary = payload["base_candidate"]["summary"]
    ledger_records = []
    for family, result in best_by_family.items():
        if family == "btc_spot_ev_fixed_candidate_stress":
            status = "fixed_candidate_stress_update"
        else:
            status = status_for(family, result, base_summary, payload)
        ledger_records.append(
            {
                "recorded_at": generated_at,
                "generated_at": generated_at,
                "source": Path(__file__).name,
                "status": status,
                "dataset": payload["dataset"],
                "datasets": payload["datasets"],
                "family": family,
                "theorem": result["theorem"],
                "equation": result["equation"],
                "params": result["params"],
                "strategy_id": result["strategy_id"],
                "idea_key": idea_key(family, result["equation"], result["params"]),
                "summary": result["summary"],
                "risk": result["risk"],
                "chronological_holdout": payload["chronological_holdout"].get(family),
                "leave_one_dataset": payload["leave_one_dataset"].get(family),
                "json_path": str(json_path),
                "markdown_path": str(md_path),
            }
        )
    append_ledger(ledger_records)
    update_strategy_memory(payload, best_by_family)

    print(f"Saved JSON: {json_path}")
    print(f"Saved Markdown: {md_path}")
    print(f"Cases={len(prepped)} strategies={len(strategies)}")
    print(
        "base "
        f"{payload['base_candidate']['strategy_id']} sim={base_summary['sim_pnl']} entries={base_summary['entries']} "
        f"win_rate={base_summary['entry_win_rate']} max_dd={payload['base_candidate']['risk']['max_drawdown']}"
    )
    for family, result in best_by_family.items():
        if family == "btc_spot_ev_fixed_candidate_stress":
            continue
        summary = result["summary"]
        holdout = payload["chronological_holdout"].get(family, {}).get("holdout_summary", {})
        print(
            f"{family} {result['strategy_id']} status={status_for(family, result, base_summary, payload)} "
            f"full_sim={summary['sim_pnl']} entries={summary['entries']} win={summary['entry_win_rate']} "
            f"holdout_sim={holdout.get('sim_pnl')} holdout_entries={holdout.get('entries')} "
            f"max_dd={result['risk']['max_drawdown']}"
        )


if __name__ == "__main__":
    main()
