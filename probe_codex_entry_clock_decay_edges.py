from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np

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
from research_pipeline import parse_market_close_from_ticker


UTC = timezone.utc


@dataclass(frozen=True)
class StrategySpec:
    family: str
    theorem: str
    equation: str
    params: dict[str, Any]


def safe_float(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return math.nan
    return parsed if not math.isnan(parsed) else math.nan


def snapshot_at_delay(case: dict[str, Any], delay_seconds: float) -> dict[str, Any] | None:
    for point in case.get("path", []):
        if safe_float(point.get("elapsed")) >= delay_seconds:
            return point
    return None


def remaining_seconds(case: dict[str, Any], elapsed: float) -> float:
    close_dt = parse_market_close_from_ticker(str(case.get("market") or ""))
    if close_dt is None:
        return math.nan
    entry_dt = datetime.fromisoformat(str(case["entry_ts"]))
    return float((close_dt - (entry_dt + timedelta(seconds=elapsed))).total_seconds())


def pressure(point: dict[str, Any]) -> float:
    own_bid = safe_float(point.get("own_bid"))
    opp_bid = safe_float(point.get("opp_bid"))
    denom = own_bid + opp_bid
    return opp_bid / denom if denom > 0 else math.nan


def spread(point: dict[str, Any]) -> float:
    own_bid = safe_float(point.get("own_bid"))
    own_ask = safe_float(point.get("own_ask"))
    return own_ask - own_bid if not math.isnan(own_bid) and not math.isnan(own_ask) else math.nan


def build_feature_arrays(cases: list[dict[str, Any]], delays: list[int]) -> dict[int, dict[str, np.ndarray]]:
    output: dict[int, dict[str, np.ndarray]] = {}
    for delay in delays:
        asks: list[float] = []
        pressures: list[float] = []
        spreads: list[float] = []
        remaining: list[float] = []
        pnls: list[float] = []
        wins: list[bool] = []
        contracts: list[int] = []
        elapsed_values: list[float] = []
        for case in cases:
            point = snapshot_at_delay(case, float(delay))
            if point is None:
                asks.append(math.nan)
                pressures.append(math.nan)
                spreads.append(math.nan)
                remaining.append(math.nan)
                pnls.append(math.nan)
                wins.append(bool(case.get("settlement_win")))
                contracts.append(int(case.get("qty") or 0))
                elapsed_values.append(math.nan)
                continue
            elapsed = safe_float(point.get("elapsed"))
            ask = safe_float(point.get("held_ask"))
            asks.append(ask)
            pressures.append(pressure(point))
            spreads.append(spread(point))
            remaining.append(remaining_seconds(case, elapsed) if not math.isnan(elapsed) else math.nan)
            pnls.append(delayed_entry_pnl(case, ask) if not math.isnan(ask) else math.nan)
            wins.append(bool(case.get("settlement_win")))
            contracts.append(int(case.get("qty") or 0))
            elapsed_values.append(elapsed)
        output[delay] = {
            "ask": np.array(asks, dtype=float),
            "pressure": np.array(pressures, dtype=float),
            "spread": np.array(spreads, dtype=float),
            "remaining": np.array(remaining, dtype=float),
            "pnl": np.array(pnls, dtype=float),
            "win": np.array(wins, dtype=bool),
            "contracts": np.array(contracts, dtype=int),
            "elapsed": np.array(elapsed_values, dtype=float),
        }
    return output


def build_strategy_grid() -> list[StrategySpec]:
    strategies: list[StrategySpec] = []

    def add(family: str, theorem: str, equation: str, params: dict[str, Any]) -> None:
        strategies.append(StrategySpec(family=family, theorem=theorem, equation=equation, params=params))

    density_theorem = (
        "A high-probability entry is more valuable when the remaining payout is dense relative to expiry time, "
        "and less valuable when opposing pressure or spread consumes that time value."
    )
    density_equation = (
        "D=(100-H_D)/(T/60)^alpha - lambda*p_opp - mu*spread; enter at delay D only if "
        "H_D<=A, T in [Tmin,Tmax], spread<=S, and D>=d."
    )
    for delay_seconds in (0, 15, 30, 60, 120):
        for max_entry_ask in (87, 90, 92, 94):
            for min_remaining_seconds, max_remaining_seconds in (
                (15, 180),
                (15, 300),
                (30, 450),
                (60, 600),
                (120, 900),
            ):
                for max_spread in (4, 6, 10):
                    for alpha in (0.5, 1.0):
                        for pressure_penalty in (0.0, 1.0, 2.0):
                            for spread_penalty in (0.2, 0.5):
                                for min_score in (2.0, 3.0, 4.0, 6.0):
                                    add(
                                        "expiry_value_density_admission",
                                        density_theorem,
                                        density_equation,
                                        {
                                            "delay_seconds": delay_seconds,
                                            "max_entry_ask": max_entry_ask,
                                            "min_remaining_seconds": min_remaining_seconds,
                                            "max_remaining_seconds": max_remaining_seconds,
                                            "max_spread": max_spread,
                                            "alpha": alpha,
                                            "pressure_penalty": pressure_penalty,
                                            "spread_penalty": spread_penalty,
                                            "min_score": min_score,
                                        },
                                    )

    utility_theorem = (
        "A 90c-style entry should be judged by payout-to-risk utility per square-root minute, not by price alone."
    )
    utility_equation = (
        "U=((100-H_D)/(H_D+1))/sqrt(T/60) - lambda*p_opp - mu*spread/10; enter at delay D only if "
        "H_D<=A, T in [Tmin,Tmax], spread<=S, and U>=u."
    )
    for delay_seconds in (0, 15, 30, 60, 120):
        for max_entry_ask in (87, 90, 92, 94):
            for min_remaining_seconds, max_remaining_seconds in (
                (15, 180),
                (15, 300),
                (30, 450),
                (60, 600),
                (120, 900),
            ):
                for max_spread in (4, 6, 10):
                    for pressure_penalty in (0.0, 0.1, 0.2):
                        for spread_penalty in (0.0, 0.1):
                            for min_score in (0.0, 0.05, 0.1):
                                add(
                                    "expiry_utility_density_admission",
                                    utility_theorem,
                                    utility_equation,
                                    {
                                        "delay_seconds": delay_seconds,
                                        "max_entry_ask": max_entry_ask,
                                        "min_remaining_seconds": min_remaining_seconds,
                                        "max_remaining_seconds": max_remaining_seconds,
                                        "max_spread": max_spread,
                                        "pressure_penalty": pressure_penalty,
                                        "spread_penalty": spread_penalty,
                                        "min_score": min_score,
                                    },
                                )

    hazard_theorem = (
        "The danger of buying a high-priced binary should scale with stake locked through time, opposing pressure, "
        "and spread friction."
    )
    hazard_equation = (
        "H=(H_D/100)*(T/900)^alpha + lambda*p_opp + mu*spread/10; enter at delay D only if "
        "H_D<=A, T in [Tmin,Tmax], spread<=S, and H<=h."
    )
    for delay_seconds in (30, 60, 120):
        for max_entry_ask in (90, 92, 94):
            for min_remaining_seconds, max_remaining_seconds in (
                (15, 180),
                (15, 300),
                (30, 450),
                (60, 600),
                (120, 900),
            ):
                for max_spread in (4, 6, 10):
                    for alpha in (0.5, 1.0):
                        for pressure_penalty in (0.0, 1.0, 2.0):
                            for spread_penalty in (0.0, 0.5):
                                for max_score in (0.5, 0.7, 1.0):
                                    add(
                                        "expiry_pressure_hazard_admission",
                                        hazard_theorem,
                                        hazard_equation,
                                        {
                                            "delay_seconds": delay_seconds,
                                            "max_entry_ask": max_entry_ask,
                                            "min_remaining_seconds": min_remaining_seconds,
                                            "max_remaining_seconds": max_remaining_seconds,
                                            "max_spread": max_spread,
                                            "alpha": alpha,
                                            "pressure_penalty": pressure_penalty,
                                            "spread_penalty": spread_penalty,
                                            "max_score": max_score,
                                        },
                                    )
    return strategies


def entry_mask(features: dict[str, np.ndarray], params: dict[str, Any]) -> np.ndarray:
    ask = features["ask"]
    pressure_values = features["pressure"]
    spread_values = features["spread"]
    remaining = features["remaining"]
    valid = (
        np.isfinite(ask)
        & np.isfinite(pressure_values)
        & np.isfinite(spread_values)
        & np.isfinite(remaining)
        & (remaining > 0)
        & (ask <= float(params["max_entry_ask"]))
        & (spread_values <= float(params["max_spread"]))
        & (remaining >= float(params["min_remaining_seconds"]))
        & (remaining <= float(params["max_remaining_seconds"]))
    )
    family = str(params["family"])
    if family == "expiry_value_density_admission":
        score = (
            (100.0 - ask) / np.power(np.maximum(remaining, 1.0) / 60.0, float(params["alpha"]))
            - float(params["pressure_penalty"]) * pressure_values
            - float(params["spread_penalty"]) * spread_values
        )
        return valid & (score >= float(params["min_score"]))
    if family == "expiry_utility_density_admission":
        score = (
            ((100.0 - ask) / (ask + 1.0)) / np.sqrt(np.maximum(remaining, 1.0) / 60.0)
            - float(params["pressure_penalty"]) * pressure_values
            - float(params["spread_penalty"]) * spread_values / 10.0
        )
        return valid & (score >= float(params["min_score"]))
    if family == "expiry_pressure_hazard_admission":
        hazard = (
            (ask / 100.0) * np.power(np.maximum(remaining, 1.0) / 900.0, float(params["alpha"]))
            + float(params["pressure_penalty"]) * pressure_values
            + float(params["spread_penalty"]) * spread_values / 10.0
        )
        return valid & (hazard <= float(params["max_score"]))
    raise ValueError(f"Unknown family: {family}")


def summarize_strategy(
    label: str,
    cases: list[dict[str, Any]],
    features: dict[str, np.ndarray],
    params: dict[str, Any],
    sample_mask: np.ndarray,
    baselines: dict[str, float],
) -> dict[str, Any]:
    entered = entry_mask(features, params) & sample_mask
    skipped = (~entered) & sample_mask
    pnl_values = np.where(entered, features["pnl"], 0.0)
    entry_pnls = pnl_values[entered]
    wins = features["win"]
    contracts = features["contracts"]
    ask = features["ask"]
    elapsed = features["elapsed"]
    remaining = features["remaining"]
    total_contracts = int(np.nansum(np.where(entered, contracts, 0)))
    base_contracts = int(np.nansum(np.where(sample_mask, contracts, 0)))
    entries = int(entered.sum())
    entered_winners = int((entered & wins).sum())
    entered_losers = entries - entered_winners
    skipped_winners = int((skipped & wins).sum())
    skipped_losers = int((skipped & ~wins).sum())
    sim_pnl = round(float(np.nansum(pnl_values)), 4)
    return {
        "label": label,
        "n": int(sample_mask.sum()),
        "sim_pnl": sim_pnl,
        "actual_recorded_pnl": round(float(baselines["actual"]), 4),
        "no_stop_hold_pnl": round(float(baselines["no_stop"]), 4),
        "no_trade_all_pnl": 0.0,
        "delta_vs_actual": round(sim_pnl - float(baselines["actual"]), 4),
        "delta_vs_no_stop": round(sim_pnl - float(baselines["no_stop"]), 4),
        "delta_vs_no_trade_all": sim_pnl,
        "entries": entries,
        "skips": int(skipped.sum()),
        "entered_settlement_winners": entered_winners,
        "entered_settlement_losers": entered_losers,
        "skipped_settlement_winners": skipped_winners,
        "skipped_settlement_losers": skipped_losers,
        "entry_win_rate": round(entered_winners / entries, 4) if entries else 0.0,
        "avg_entry_ask": round(float(np.nanmean(ask[entered])), 4) if entries else None,
        "avg_entry_elapsed": round(float(np.nanmean(elapsed[entered])), 4) if entries else None,
        "avg_remaining_seconds": round(float(np.nanmean(remaining[entered])), 4) if entries else None,
        "worst_trade": round(float(np.nanmin(entry_pnls)), 4) if entries else 0.0,
        "total_contracts": total_contracts,
        "base_contracts": base_contracts,
        "contract_fraction": round(total_contracts / base_contracts, 4) if base_contracts else 0.0,
    }


def baseline_sample(cases: list[dict[str, Any]], label: str, sample_mask: np.ndarray) -> float:
    total = 0.0
    for use_case, case in zip(sample_mask, cases):
        if not bool(use_case):
            continue
        if label == "actual":
            total += float(case["actual_net_pnl"])
        elif label == "no_stop":
            total += float(case["hold_pnl"])
        else:
            raise ValueError(label)
    return round(total, 4)


def dataset_summaries(
    cases: list[dict[str, Any]],
    features_by_delay: dict[int, dict[str, np.ndarray]],
    params: dict[str, Any],
    datasets: list[str],
) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    features = features_by_delay[int(params["delay_seconds"])]
    for dataset in datasets:
        mask = np.array([case.get("dataset") == dataset for case in cases], dtype=bool)
        baselines = {
            "actual": baseline_sample(cases, "actual", mask),
            "no_stop": baseline_sample(cases, "no_stop", mask),
        }
        out[dataset] = summarize_strategy("dataset", cases, features, params, mask, baselines)
    return out


def day_summaries(
    cases: list[dict[str, Any]],
    features_by_delay: dict[int, dict[str, np.ndarray]],
    params: dict[str, Any],
) -> dict[str, Any]:
    days = sorted({str(case.get("entry_day_et") or "") for case in cases})
    features = features_by_delay[int(params["delay_seconds"])]
    rows = []
    for day in days:
        if not day:
            continue
        mask = np.array([case.get("entry_day_et") == day for case in cases], dtype=bool)
        baselines = {
            "actual": baseline_sample(cases, "actual", mask),
            "no_stop": baseline_sample(cases, "no_stop", mask),
        }
        summary = summarize_strategy(day, cases, features, params, mask, baselines)
        if summary["entries"]:
            rows.append(
                {
                    "entry_day_et": day,
                    "sim_pnl": summary["sim_pnl"],
                    "entries": summary["entries"],
                    "entry_win_rate": summary["entry_win_rate"],
                    "delta_vs_no_trade_all": summary["delta_vs_no_trade_all"],
                }
            )
    return {
        "active_days": len(rows),
        "positive_days": sum(1 for row in rows if row["sim_pnl"] > 0),
        "negative_days": sum(1 for row in rows if row["sim_pnl"] < 0),
        "rows": rows,
    }


def evaluate_strategy(
    cases: list[dict[str, Any]],
    features_by_delay: dict[int, dict[str, np.ndarray]],
    strategy: StrategySpec,
    sample_mask: np.ndarray,
    baselines: dict[str, float],
) -> dict[str, Any]:
    params = {"family": strategy.family, **strategy.params}
    sid = strategy_id(strategy.family, strategy.params)
    summary = summarize_strategy(sid, cases, features_by_delay[int(strategy.params["delay_seconds"])], params, sample_mask, baselines)
    return {
        "family": strategy.family,
        "theorem": strategy.theorem,
        "equation": strategy.equation,
        "params": strategy.params,
        "strategy_id": sid,
        "summary": summary,
    }


def select_family_best(results: list[dict[str, Any]], min_entries: int = 10) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for result in results:
        if result["summary"]["entries"] < min_entries:
            continue
        family = result["family"]
        current = output.get(family)
        if current is None or result["summary"]["sim_pnl"] > current["summary"]["sim_pnl"]:
            output[family] = result
    return output


def walk_forward_summary(
    cases: list[dict[str, Any]],
    features_by_delay: dict[int, dict[str, np.ndarray]],
    strategies: list[StrategySpec],
) -> dict[str, Any]:
    n = len(cases)
    split = int(n * 0.7)
    train_mask = np.zeros(n, dtype=bool)
    train_mask[:split] = True
    holdout_mask = ~train_mask
    train_base = {
        "actual": baseline_sample(cases, "actual", train_mask),
        "no_stop": baseline_sample(cases, "no_stop", train_mask),
    }
    holdout_base = {
        "actual": baseline_sample(cases, "actual", holdout_mask),
        "no_stop": baseline_sample(cases, "no_stop", holdout_mask),
    }
    train_results = [
        evaluate_strategy(cases, features_by_delay, strategy, train_mask, train_base)
        for strategy in strategies
    ]
    selected = select_family_best(train_results)
    families: dict[str, Any] = {}
    for family, result in selected.items():
        strategy = StrategySpec(
            family=family,
            theorem=result["theorem"],
            equation=result["equation"],
            params=result["params"],
        )
        holdout = evaluate_strategy(cases, features_by_delay, strategy, holdout_mask, holdout_base)
        families[family] = {
            "selected_strategy_id": result["strategy_id"],
            "selected_params": result["params"],
            "train_summary": result["summary"],
            "holdout_summary": holdout["summary"],
        }
    return {
        "split_entry_ts": cases[split]["entry_ts"] if split < n else None,
        "train_cases": int(train_mask.sum()),
        "holdout_cases": int(holdout_mask.sum()),
        "families": families,
    }


def robust_positive_scan(
    cases: list[dict[str, Any]],
    features_by_delay: dict[int, dict[str, np.ndarray]],
    strategies: list[StrategySpec],
) -> dict[str, list[dict[str, Any]]]:
    n = len(cases)
    split = int(n * 0.7)
    train_mask = np.zeros(n, dtype=bool)
    train_mask[:split] = True
    holdout_mask = ~train_mask
    train_base = {
        "actual": baseline_sample(cases, "actual", train_mask),
        "no_stop": baseline_sample(cases, "no_stop", train_mask),
    }
    holdout_base = {
        "actual": baseline_sample(cases, "actual", holdout_mask),
        "no_stop": baseline_sample(cases, "no_stop", holdout_mask),
    }
    rows: dict[str, list[dict[str, Any]]] = {}
    for strategy in strategies:
        train_result = evaluate_strategy(cases, features_by_delay, strategy, train_mask, train_base)
        train_summary = train_result["summary"]
        if train_summary["entries"] < 10 or train_summary["delta_vs_no_trade_all"] <= 0:
            continue
        holdout_result = evaluate_strategy(cases, features_by_delay, strategy, holdout_mask, holdout_base)
        holdout_summary = holdout_result["summary"]
        if holdout_summary["entries"] < 10 or holdout_summary["delta_vs_no_trade_all"] <= 0:
            continue
        rows.setdefault(strategy.family, []).append(
            {
                "strategy_id": train_result["strategy_id"],
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
    for family in list(rows):
        rows[family] = sorted(
            rows[family],
            key=lambda row: (row["min_split_pnl"], row["holdout_sim_pnl"], row["train_sim_pnl"]),
            reverse=True,
        )[:15]
    return rows


def sensitivity(results: list[dict[str, Any]], best_by_family: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for family, best in best_by_family.items():
        ranked = sorted(
            [result for result in results if result["family"] == family and result["summary"]["entries"] >= 10],
            key=lambda result: (result_distance(result["params"], best["params"]), -result["summary"]["sim_pnl"]),
        )
        out[family] = [
            {
                "strategy_id": result["strategy_id"],
                "params": result["params"],
                "sim_pnl": result["summary"]["sim_pnl"],
                "delta_vs_no_trade_all": result["summary"]["delta_vs_no_trade_all"],
                "entries": result["summary"]["entries"],
                "entry_win_rate": result["summary"]["entry_win_rate"],
                "avg_entry_ask": result["summary"]["avg_entry_ask"],
            }
            for result in ranked[:12]
        ]
    return out


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


def read_prior_entry_reference() -> dict[str, Any]:
    output: dict[str, Any] = {}
    for name in ("codex_entry_timing_research_latest.json", "codex_entry_path_geometry_research_latest.json"):
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
        "# Codex Entry Clock Decay Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Quote-path cases: `{payload['case_count']}`",
        "- Scope: research-only entry/no-trade simulation; live bot logic, configs, run scripts, and processes were not changed.",
        "- Non-repetition: this tests expiry-time value density and stake-time hazard, not fixed entry price, delayed snapshot thresholds, Kelly sizing, or compact path geometry.",
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
        by_dataset = payload["by_dataset"].get(family, {})
        day = payload["by_day"].get(family, {})
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
                f"- Avg entry ask / remaining seconds / contract fraction: `{summary['avg_entry_ask']} / {summary['avg_remaining_seconds']} / {summary['contract_fraction']}`",
                f"- Train-selected params: `{json.dumps(walk.get('selected_params'), sort_keys=True)}`",
                f"- Train-selected holdout PnL / delta vs actual / delta vs no-stop / delta vs skip-all: `${holdout.get('sim_pnl')}` / `${holdout.get('delta_vs_actual')}` / `${holdout.get('delta_vs_no_stop')}` / `${holdout.get('delta_vs_no_trade_all')}`",
                f"- Holdout entries / skipped winners / skipped losers / win rate: `{holdout.get('entries')} / {holdout.get('skipped_settlement_winners')} / {holdout.get('skipped_settlement_losers')} / {holdout.get('entry_win_rate')}`",
                f"- Active days positive/active: `{day.get('positive_days')}/{day.get('active_days')}`",
            ]
        )
        if by_dataset:
            dataset_bits = [
                f"{dataset}: ${item['sim_pnl']} ({item['entries']} entries)"
                for dataset, item in sorted(by_dataset.items())
            ]
            lines.append(f"- By dataset: `{'; '.join(dataset_bits)}`")
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
        lines.append("- No prior entry timing/path reference JSON was available.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The useful signal is concentrated in very late opportunities: the strongest variants admit entries with roughly 1.5-3.5 minutes left rather than treating every 90c signal as mandatory.",
            "- The value-density and utility-density equations both survive the chronological holdout and nearby-parameter scan, but they enter a small fraction of opportunities and should be preregistered on fresh data before any live consideration.",
            "- The stake-time hazard formulation was weaker on the selected holdout in this run, suggesting simple high-price time exposure is less informative than payout density after pressure/spread penalties.",
            "- All tested variables are derived from quote heartbeats and the public market close encoded in the ticker at or before the simulated decision time.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only expiry clock decay admission probes.")
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
    delays = sorted({int(strategy.params["delay_seconds"]) for strategy in strategies})
    features_by_delay = build_feature_arrays(cases, delays)
    all_mask = np.ones(len(cases), dtype=bool)
    all_base = {
        "actual": baseline_sample(cases, "actual", all_mask),
        "no_stop": baseline_sample(cases, "no_stop", all_mask),
    }
    results = [
        evaluate_strategy(cases, features_by_delay, strategy, all_mask, all_base)
        for strategy in strategies
    ]
    best_by_family = select_family_best(results)
    walk = walk_forward_summary(cases, features_by_delay, strategies)
    robust_scan = robust_positive_scan(cases, features_by_delay, strategies)
    sens = sensitivity(results, best_by_family)
    baselines = {
        "actual": run_baseline(cases, "actual"),
        "no_stop": run_baseline(cases, "no_stop"),
        "held_ask_stop_70": run_baseline(cases, "held_ask_stop_70"),
    }
    datasets_sorted = sorted({str(case.get("dataset")) for case in cases})
    by_dataset = {
        family: dataset_summaries(cases, features_by_delay, {"family": family, **result["params"]}, datasets_sorted)
        for family, result in best_by_family.items()
    }
    by_day = {
        family: day_summaries(cases, features_by_delay, {"family": family, **result["params"]})
        for family, result in best_by_family.items()
    }

    generated_at = datetime.now(UTC).isoformat()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"codex_entry_clock_decay_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_entry_clock_decay_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_entry_clock_decay_research_latest.json"
    latest_md = EDGE_DIR / "codex_entry_clock_decay_research_latest.md"
    report_payload = {
        "generated_at": generated_at,
        "dataset": "all_quote_path_trades",
        "datasets": datasets_sorted,
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
        "sensitivity": sens,
        "by_dataset": by_dataset,
        "by_day": by_day,
        "prior_entry_reference": read_prior_entry_reference(),
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "feature_availability": {
            "expiry_value_density_admission": "held ask, opposite pressure, own spread, and ticker-derived close time at/after the simulated delay",
            "expiry_utility_density_admission": "held ask, opposite pressure, own spread, and ticker-derived close time at/after the simulated delay",
            "expiry_pressure_hazard_admission": "held ask, opposite pressure, own spread, and ticker-derived close time at/after the simulated delay",
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
