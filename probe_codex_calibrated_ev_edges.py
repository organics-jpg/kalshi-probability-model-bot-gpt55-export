from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from research_pipeline import parse_market_close_from_ticker
from probe_codex_terminal_salvage_all_trades import (
    DEFAULT_PARAMS as TERMINAL_BASELINE_PARAMS,
    EDGE_DIR,
    discover_datasets,
    load_dataset_cases,
    run_baseline,
    run_terminal,
)
from probe_stop_touch_confirmation import (
    append_ledger,
    estimated_order_fee_cents,
    exit_pnl,
    idea_key,
    result_distance,
    strategy_id,
    summarize_rows,
    update_strategy_memory,
)


UTC = timezone.utc


@dataclass(frozen=True)
class StrategySpec:
    family: str
    theorem: str
    equation: str
    params: dict[str, Any]
    simulator: Callable[[dict[str, Any], list[dict[str, Any]], dict[str, Any], dict[str, Any] | None], tuple[float, dict[str, Any]]]
    model_builder: Callable[[list[tuple[dict[str, Any], list[dict[str, Any]]]], dict[str, Any]], dict[str, Any]] | None = None


def case_entry_dt(case: dict[str, Any]) -> datetime:
    return datetime.fromisoformat(str(case["entry_ts"]))


def seconds_to_close(case: dict[str, Any], point: dict[str, Any]) -> float | None:
    close_dt = parse_market_close_from_ticker(str(case.get("market") or ""))
    if close_dt is None:
        return None
    now_dt = case_entry_dt(case) + timedelta(seconds=float(point["elapsed"]))
    return float((close_dt - now_dt).total_seconds())


def safe_float(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return math.nan
    return parsed if not math.isnan(parsed) else math.nan


def trailing_points(case: dict[str, Any], idx: int, lookback_seconds: float) -> list[dict[str, Any]]:
    now_elapsed = float(case["path"][idx]["elapsed"])
    lower = now_elapsed - lookback_seconds
    return [point for point in case["path"][: idx + 1] if float(point["elapsed"]) >= lower]


def realized_path_vol(points: list[dict[str, Any]]) -> float:
    held_asks = [safe_float(point.get("held_ask")) for point in points]
    held_asks = [value for value in held_asks if not math.isnan(value)]
    if len(held_asks) < 2:
        return math.nan
    diffs = [held_asks[idx] - held_asks[idx - 1] for idx in range(1, len(held_asks))]
    span = max(1.0, float(points[-1]["elapsed"]) - float(points[0]["elapsed"]))
    return math.sqrt(sum(diff * diff for diff in diffs)) / math.sqrt(span / 60.0)


def prepared_events(case: dict[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for idx, point in enumerate(case["path"]):
        remaining = seconds_to_close(case, point)
        if remaining is None or remaining < 1 or remaining > 240:
            continue
        own_bid = safe_float(point.get("own_bid"))
        opp_bid = safe_float(point.get("opp_bid"))
        own_ask = safe_float(point.get("own_ask"))
        opp_ask = safe_float(point.get("opp_ask"))
        held_ask = safe_float(point.get("held_ask"))
        bid_sum = safe_float(point.get("bid_sum"))
        if math.isnan(own_bid) or math.isnan(held_ask):
            continue
        pressure = opp_bid / (own_bid + opp_bid + 1e-9) if not math.isnan(opp_bid) else math.nan
        spread = own_ask - own_bid if not math.isnan(own_ask) else math.nan
        parity_gap = abs(held_ask + opp_bid - 100.0) if not math.isnan(opp_bid) else math.nan
        lookbacks: dict[int, dict[str, float]] = {}
        for lookback in (30, 60, 90):
            points = trailing_points(case, idx, float(lookback))
            held_asks = [safe_float(item.get("held_ask")) for item in points]
            held_asks = [value for value in held_asks if not math.isnan(value)]
            span = max(1.0, float(points[-1]["elapsed"]) - float(points[0]["elapsed"])) if len(points) >= 2 else 1.0
            lookbacks[lookback] = {
                "n": float(len(points)),
                "drop_from_recent_high": max(held_asks) - held_ask if held_asks else math.nan,
                "net_drop": held_asks[0] - held_ask if held_asks else math.nan,
                "slope_per_second": (held_ask - held_asks[0]) / span if len(held_asks) >= 2 else math.nan,
                "vol_cents_per_sqrt_min": realized_path_vol(points),
            }
        events.append(
            {
                "idx": idx,
                "elapsed": float(point["elapsed"]),
                "remaining": remaining,
                "own_bid": own_bid,
                "opp_bid": opp_bid,
                "own_ask": own_ask,
                "opp_ask": opp_ask,
                "held_ask": held_ask,
                "bid_sum": bid_sum,
                "pressure": pressure,
                "spread": spread,
                "parity_gap": parity_gap,
                "lookbacks": lookbacks,
            }
        )
    return events


def quantize(value: float, width: float, max_bucket: int = 1000) -> int:
    if math.isnan(value):
        return -1
    return max(-1, min(max_bucket, int(math.floor(value / width))))


def bucketize(value: float, cuts: tuple[float, ...]) -> int:
    if math.isnan(value):
        return -1
    for idx, cut in enumerate(cuts):
        if value <= cut:
            return idx
    return len(cuts)


def terminal_ev_keys(event: dict[str, Any], params: dict[str, Any]) -> list[tuple[Any, ...]]:
    r = quantize(float(event["remaining"]), float(params["remaining_bucket_seconds"]))
    h = quantize(float(event["held_ask"]), float(params["held_ask_bucket_cents"]))
    p = quantize(float(event["pressure"]), float(params["pressure_bucket"])) if not math.isnan(float(event["pressure"])) else -1
    return [
        ("terminal_ev", r, h, p),
        ("terminal_ev_hp", h, p),
        ("terminal_ev_h", h),
        ("global",),
    ]


def recovery_z(event: dict[str, Any], params: dict[str, Any]) -> float:
    lookback = int(params["vol_lookback_seconds"])
    vol = float(event["lookbacks"][lookback]["vol_cents_per_sqrt_min"])
    vol_floor = float(params["vol_floor"])
    denom = max(vol_floor, vol) * math.sqrt(max(float(event["remaining"]), 1.0) / 60.0)
    return (float(params["recovery_target_ask"]) - float(event["held_ask"])) / max(denom, 1e-6)


def recovery_ev_keys(event: dict[str, Any], params: dict[str, Any]) -> list[tuple[Any, ...]]:
    z = recovery_z(event, params)
    z_bucket = bucketize(z, (-1.0, 0.0, 0.75, 1.5, 2.5, 4.0, 6.0))
    p = quantize(float(event["pressure"]), float(params["pressure_bucket"])) if not math.isnan(float(event["pressure"])) else -1
    r = quantize(float(event["remaining"]), float(params["remaining_bucket_seconds"]))
    return [
        ("recovery_z", z_bucket, p, r),
        ("recovery_zp", z_bucket, p),
        ("recovery_z_only", z_bucket),
        ("global",),
    ]


def event_passes_terminal_ev(event: dict[str, Any], params: dict[str, Any]) -> bool:
    return (
        float(params["min_remaining_seconds"])
        <= float(event["remaining"])
        <= float(params["max_remaining_seconds"])
        and float(event["held_ask"]) <= float(params["held_ask_ceiling"])
        and not math.isnan(float(event["pressure"]))
    )


def event_passes_recovery_ev(event: dict[str, Any], params: dict[str, Any]) -> bool:
    if not event_passes_terminal_ev(event, params):
        return False
    return recovery_z(event, params) >= float(params["min_recovery_z"])


def fit_calibration(
    prepped: list[tuple[dict[str, Any], list[dict[str, Any]]]],
    params: dict[str, Any],
    *,
    event_filter: Callable[[dict[str, Any], dict[str, Any]], bool],
    key_func: Callable[[dict[str, Any], dict[str, Any]], list[tuple[Any, ...]]],
) -> dict[str, Any]:
    counts: dict[tuple[Any, ...], dict[str, float]] = {}
    total = 0
    wins = 0
    for case, events in prepped:
        total += 1
        wins += 1 if bool(case["settlement_win"]) else 0
        seen: set[tuple[Any, ...]] = set()
        for event in events:
            if not event_filter(event, params):
                continue
            for key in key_func(event, params):
                if key in seen:
                    continue
                bucket = counts.setdefault(key, {"n": 0.0, "wins": 0.0})
                bucket["n"] += 1.0
                bucket["wins"] += 1.0 if bool(case["settlement_win"]) else 0.0
                seen.add(key)
    global_q = wins / total if total else 0.5
    encoded_counts = {"|".join(map(str, key)): value for key, value in counts.items()}
    return {"counts": encoded_counts, "global_q": global_q, "train_cases": total}


def q_from_model(model: dict[str, Any], event: dict[str, Any], params: dict[str, Any], key_func: Callable[[dict[str, Any], dict[str, Any]], list[tuple[Any, ...]]]) -> tuple[float, dict[str, Any]]:
    min_cell_cases = float(params["min_cell_cases"])
    prior_strength = float(params["prior_strength"])
    global_q = float(model.get("global_q", 0.5))
    counts = model.get("counts", {})
    for key in key_func(event, params):
        text_key = "|".join(map(str, key))
        bucket = counts.get(text_key)
        if not bucket or float(bucket.get("n", 0.0)) < min_cell_cases:
            continue
        n = float(bucket["n"])
        wins = float(bucket["wins"])
        q = (wins + prior_strength * global_q) / (n + prior_strength)
        return q, {"calibration_key": text_key, "cell_n": n, "cell_wins": wins}
    return global_q, {"calibration_key": "global_fallback", "cell_n": float(model.get("train_cases", 0)), "cell_wins": global_q * float(model.get("train_cases", 0))}


def exit_advantage_cents(case: dict[str, Any], event: dict[str, Any], q_hat: float) -> float:
    qty = max(1, int(case["qty"]))
    exit_fee_per_contract = estimated_order_fee_cents(float(event["own_bid"]), qty) / qty
    return float(event["own_bid"]) - exit_fee_per_contract - 100.0 * q_hat


def sim_terminal_calibrated_ev(
    case: dict[str, Any], events: list[dict[str, Any]], params: dict[str, Any], model: dict[str, Any] | None
) -> tuple[float, dict[str, Any]]:
    if model is None:
        raise ValueError("terminal calibrated EV requires a model")
    for event in events:
        if not event_passes_terminal_ev(event, params):
            continue
        q_hat, q_meta = q_from_model(model, event, params, terminal_ev_keys)
        advantage = exit_advantage_cents(case, event, q_hat)
        if advantage < float(params["min_exit_advantage_cents"]):
            continue
        pnl = exit_pnl(case, float(event["own_bid"]))
        return pnl, {
            "exit": True,
            "exit_bid": float(event["own_bid"]),
            "exit_elapsed": float(event["elapsed"]),
            "held_ask": float(event["held_ask"]),
            "seconds_to_close": round(float(event["remaining"]), 3),
            "q_hat": round(q_hat, 6),
            "exit_advantage_cents": round(advantage, 4),
            **q_meta,
        }
    return float(case["hold_pnl"]), {"exit": False}


def sim_recovery_zscore_ev(
    case: dict[str, Any], events: list[dict[str, Any]], params: dict[str, Any], model: dict[str, Any] | None
) -> tuple[float, dict[str, Any]]:
    if model is None:
        raise ValueError("recovery z-score EV requires a model")
    for event in events:
        if not event_passes_recovery_ev(event, params):
            continue
        q_hat, q_meta = q_from_model(model, event, params, recovery_ev_keys)
        advantage = exit_advantage_cents(case, event, q_hat)
        if advantage < float(params["min_exit_advantage_cents"]):
            continue
        pnl = exit_pnl(case, float(event["own_bid"]))
        return pnl, {
            "exit": True,
            "exit_bid": float(event["own_bid"]),
            "exit_elapsed": float(event["elapsed"]),
            "held_ask": float(event["held_ask"]),
            "seconds_to_close": round(float(event["remaining"]), 3),
            "recovery_z": round(recovery_z(event, params), 4),
            "q_hat": round(q_hat, 6),
            "exit_advantage_cents": round(advantage, 4),
            **q_meta,
        }
    return float(case["hold_pnl"]), {"exit": False}


def sim_book_parity_consistency(
    case: dict[str, Any], events: list[dict[str, Any]], params: dict[str, Any], model: dict[str, Any] | None
) -> tuple[float, dict[str, Any]]:
    del model
    for event in events:
        if not (
            float(params["min_remaining_seconds"])
            <= float(event["remaining"])
            <= float(params["max_remaining_seconds"])
        ):
            continue
        held_ask = float(event["held_ask"])
        parity_gap = float(event["parity_gap"])
        spread = float(event["spread"])
        bid_sum = float(event["bid_sum"])
        if any(math.isnan(value) for value in (held_ask, parity_gap, spread, bid_sum)):
            continue
        if held_ask > float(params["held_ask_ceiling"]):
            continue
        if parity_gap > float(params["max_parity_gap"]):
            continue
        if spread > float(params["max_spread"]):
            continue
        quality = bid_sum / (1.0 + spread + parity_gap)
        if quality < float(params["min_quality"]):
            continue
        pnl = exit_pnl(case, float(event["own_bid"]))
        return pnl, {
            "exit": True,
            "exit_bid": float(event["own_bid"]),
            "exit_elapsed": float(event["elapsed"]),
            "held_ask": held_ask,
            "seconds_to_close": round(float(event["remaining"]), 3),
            "parity_gap": round(parity_gap, 4),
            "spread": round(spread, 4),
            "signal_quality": round(quality, 4),
        }
    return float(case["hold_pnl"]), {"exit": False}


def build_terminal_ev_model(
    prepped: list[tuple[dict[str, Any], list[dict[str, Any]]]], params: dict[str, Any]
) -> dict[str, Any]:
    return fit_calibration(prepped, params, event_filter=event_passes_terminal_ev, key_func=terminal_ev_keys)


def build_recovery_ev_model(
    prepped: list[tuple[dict[str, Any], list[dict[str, Any]]]], params: dict[str, Any]
) -> dict[str, Any]:
    return fit_calibration(prepped, params, event_filter=event_passes_recovery_ev, key_func=recovery_ev_keys)


def build_strategy_grid() -> list[StrategySpec]:
    strategies: list[StrategySpec] = []

    def add(
        family: str,
        theorem: str,
        equation: str,
        params: dict[str, Any],
        simulator: Callable[[dict[str, Any], list[dict[str, Any]], dict[str, Any], dict[str, Any] | None], tuple[float, dict[str, Any]]],
        model_builder: Callable[[list[tuple[dict[str, Any], list[dict[str, Any]]]], dict[str, Any]], dict[str, Any]] | None = None,
    ) -> None:
        strategies.append(StrategySpec(family, theorem, equation, params, simulator, model_builder))

    for held_ask_ceiling in (40, 45, 50, 55):
        for max_remaining_seconds in (45, 60, 75, 90):
            for min_remaining_seconds in (10, 15, 20):
                for min_cell_cases in (5, 10, 20):
                    for min_exit_advantage_cents in (0, 2, 5):
                        add(
                            "calibrated_terminal_ev_gap",
                            "A terminal exit is justified only when a beta-shrunk empirical settlement probability makes holding worth less than selling now after fees.",
                            "q_hat=BetaBinomial(P(win)|bucket(seconds_to_close,held_ask,pressure)); exit when own_bid-exit_fee_per_contract-100*q_hat >= M.",
                            {
                                "held_ask_ceiling": held_ask_ceiling,
                                "max_remaining_seconds": max_remaining_seconds,
                                "min_remaining_seconds": min_remaining_seconds,
                                "min_cell_cases": min_cell_cases,
                                "min_exit_advantage_cents": min_exit_advantage_cents,
                                "prior_strength": 8,
                                "remaining_bucket_seconds": 15,
                                "held_ask_bucket_cents": 10,
                                "pressure_bucket": 0.1,
                            },
                            sim_terminal_calibrated_ev,
                            build_terminal_ev_model,
                        )

    for held_ask_ceiling in (45, 50, 55, 60):
        for max_remaining_seconds in (60, 75, 90, 120):
            for recovery_target_ask in (60, 70, 80):
                for min_recovery_z in (1.0, 1.5, 2.0, 2.5):
                    for min_exit_advantage_cents in (0, 2, 5):
                        add(
                            "recovery_zscore_calibrated_ev",
                            "A low ask is worse when the ask must travel several realized-volatility units before close to regain a tradable recovery level.",
                            "z=(target_ask-held_ask)/(realized_vol_L*sqrt(seconds_to_close/60)); q_hat=BetaBinomial(P(win)|bucket(z,pressure,time)); exit when z>=Z and own_bid-fee-100*q_hat >= M.",
                            {
                                "held_ask_ceiling": held_ask_ceiling,
                                "max_remaining_seconds": max_remaining_seconds,
                                "min_remaining_seconds": 10,
                                "recovery_target_ask": recovery_target_ask,
                                "min_recovery_z": min_recovery_z,
                                "min_exit_advantage_cents": min_exit_advantage_cents,
                                "min_cell_cases": 5,
                                "prior_strength": 8,
                                "vol_lookback_seconds": 60,
                                "vol_floor": 4,
                                "remaining_bucket_seconds": 15,
                                "pressure_bucket": 0.1,
                            },
                            sim_recovery_zscore_ev,
                            build_recovery_ev_model,
                        )

    for held_ask_ceiling in (35, 40, 45, 50, 55):
        for max_remaining_seconds in (45, 60, 75, 90):
            for min_remaining_seconds in (5, 10, 15):
                for max_parity_gap in (1, 2, 4, 6):
                    for max_spread in (2, 4, 6, 10):
                        for min_quality in (8, 12, 16, 20):
                            add(
                                "book_parity_consistency_exit",
                                "A low held-side ask is more trustworthy when it agrees with the opposite bid and the own-side spread is not too wide.",
                                "quality=(own_bid+opp_bid)/(1+own_ask-own_bid+abs(held_ask+opp_bid-100)); exit when held_ask<=H, parity_gap<=G, spread<=S, and quality>=Q.",
                                {
                                    "held_ask_ceiling": held_ask_ceiling,
                                    "max_remaining_seconds": max_remaining_seconds,
                                    "min_remaining_seconds": min_remaining_seconds,
                                    "max_parity_gap": max_parity_gap,
                                    "max_spread": max_spread,
                                    "min_quality": min_quality,
                                },
                                sim_book_parity_consistency,
                            )
    return strategies


def row_for(case: dict[str, Any], pnl: float, meta: dict[str, Any], label: str) -> dict[str, Any]:
    exit_bid = meta.get("exit_bid")
    return {
        "label": label,
        "dataset": case.get("dataset", "unknown"),
        "market": case["market"],
        "entry_day_et": case["entry_day_et"],
        "settlement_win": bool(case["settlement_win"]),
        "actual_net_pnl": float(case["actual_net_pnl"]),
        "hold_pnl": float(case["hold_pnl"]),
        "sim_pnl": float(pnl),
        "action": "exit" if meta.get("exit") else "hold",
        "exit_bid": float(exit_bid) if exit_bid is not None else None,
        "entry": float(case["entry"]),
        "min_bid": float(case["min_bid"]),
        "max_drawdown": float(case["max_drawdown"]),
    }


def summarize_label(label: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary = summarize_rows(label, rows)
    summary["datasets"] = sorted({str(row["dataset"]) for row in rows})
    return summary


def summarize_by_dataset(label: str, rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        dataset: summarize_label(label, [row for row in rows if row["dataset"] == dataset])
        for dataset in sorted({str(row["dataset"]) for row in rows})
    }


def run_strategy(
    eval_prepped: list[tuple[dict[str, Any], list[dict[str, Any]]]],
    strategy: StrategySpec,
    fit_prepped: list[tuple[dict[str, Any], list[dict[str, Any]]]] | None = None,
) -> dict[str, Any]:
    sid = strategy_id(strategy.family, strategy.params)
    model = strategy.model_builder(fit_prepped or eval_prepped, strategy.params) if strategy.model_builder else None
    rows = [row_for(case, *strategy.simulator(case, events, strategy.params, model), sid) for case, events in eval_prepped]
    return {
        "strategy_id": sid,
        "family": strategy.family,
        "theorem": strategy.theorem,
        "equation": strategy.equation,
        "params": strategy.params,
        "summary": summarize_label(sid, rows),
        "by_dataset": summarize_by_dataset(sid, rows),
        "model_diagnostics": {
            "train_cases": model.get("train_cases") if model else None,
            "global_q": round(float(model.get("global_q")), 6) if model else None,
            "cell_count": len(model.get("counts", {})) if model else None,
        },
        "interesting_examples": sorted(
            rows,
            key=lambda row: (float(row["sim_pnl"]) - float(row["hold_pnl"]), -float(row["max_drawdown"])),
            reverse=True,
        )[:10],
    }


def walk_forward_results(
    cases: list[dict[str, Any]], strategies: list[StrategySpec]
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    ordered = sorted(cases, key=lambda case: case["entry_ts"])
    split = int(len(ordered) * 0.7)
    train_cases = ordered[:split]
    holdout_cases = ordered[split:]
    train_prepped = [(case, prepared_events(case)) for case in train_cases]
    holdout_prepped = [(case, prepared_events(case)) for case in holdout_cases]
    full_prepped = [(case, prepared_events(case)) for case in ordered]
    by_family: dict[str, list[StrategySpec]] = {}
    for strategy in strategies:
        by_family.setdefault(strategy.family, []).append(strategy)

    walk: dict[str, Any] = {
        "train_n": len(train_cases),
        "holdout_n": len(holdout_cases),
        "split_entry_ts": ordered[split]["entry_ts"] if holdout_cases else None,
        "selection_basis": "Max train sim PnL; calibration models fit on chronological train only; holdout is out-of-sample.",
        "families": {},
    }
    best_by_family: dict[str, dict[str, Any]] = {}
    sensitivity_by_family: dict[str, list[dict[str, Any]]] = {}
    for family, family_specs in by_family.items():
        train_results = [run_strategy(train_prepped, strategy, train_prepped) for strategy in family_specs]
        selected_train = max(train_results, key=lambda result: result["summary"]["sim_pnl"])
        selected_spec = next(
            strategy
            for strategy in family_specs
            if strategy_id(strategy.family, strategy.params) == selected_train["strategy_id"]
        )
        holdout_result = run_strategy(holdout_prepped, selected_spec, train_prepped)
        full_result = run_strategy(full_prepped, selected_spec, train_prepped)
        full_result["train_summary"] = selected_train["summary"]
        full_result["holdout_summary"] = holdout_result["summary"]
        best_by_family[family] = full_result
        walk["families"][family] = {
            "selected_strategy_id": selected_train["strategy_id"],
            "selected_params": selected_train["params"],
            "train_summary": selected_train["summary"],
            "holdout_summary": holdout_result["summary"],
            "full_selected_summary": full_result["summary"],
        }
        ranked = sorted(
            train_results,
            key=lambda result: (result_distance(result["params"], selected_train["params"]), -result["summary"]["sim_pnl"]),
        )
        excerpt: list[dict[str, Any]] = []
        for result in ranked[:10]:
            spec = next(
                strategy
                for strategy in family_specs
                if strategy_id(strategy.family, strategy.params) == result["strategy_id"]
            )
            hold = run_strategy(holdout_prepped, spec, train_prepped)["summary"]
            excerpt.append(
                {
                    "strategy_id": result["strategy_id"],
                    "params": result["params"],
                    "train_sim_pnl": result["summary"]["sim_pnl"],
                    "holdout_sim_pnl": hold["sim_pnl"],
                    "holdout_delta_vs_actual": hold["delta_vs_actual"],
                    "holdout_delta_vs_no_stop": hold["delta_vs_no_stop"],
                    "holdout_exits": hold["exits"],
                    "holdout_false_exits": hold["false_exit_settlement_winners"],
                    "holdout_missed_true_losers": hold["missed_true_losers"],
                }
            )
        sensitivity_by_family[family] = excerpt
    return walk, best_by_family, sensitivity_by_family


def status_for(result: dict[str, Any]) -> str:
    holdout = result["holdout_summary"]
    full = result["summary"]
    if holdout["delta_vs_actual"] > 0 and holdout["delta_vs_no_stop"] > 0:
        if holdout["false_exit_rate"] <= 0.05 and holdout["missed_true_loser_rate"] <= 0.15:
            return "candidate_for_human_review"
        return "watchlist_positive_but_noisy"
    if full["delta_vs_actual"] > 0 and full["delta_vs_no_stop"] > 0:
        return "in_sample_positive_holdout_failed"
    return "tested_not_robust"


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    actual = payload["baselines"]["actual"]["summary"]
    no_stop = payload["baselines"]["no_stop"]["summary"]
    stop70 = payload["baselines"]["held_ask_stop_70"]["summary"]
    terminal = payload["terminal_window_baseline"]["summary"]
    lines = [
        "# Codex Calibrated EV Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Cases: `{payload['case_count']}`",
        f"- Actual recorded PnL: `${actual['sim_pnl']}`",
        f"- No-stop hold-to-settlement PnL: `${no_stop['sim_pnl']}`",
        f"- First held-ask <=70 baseline PnL: `${stop70['sim_pnl']}`",
        f"- Prior terminal-window salvage baseline PnL: `${terminal['sim_pnl']}`",
        f"- Walk-forward split: `{payload['walk_forward']['split_entry_ts']}`",
        "",
        "## New Hypotheses Tested",
    ]
    for family, result in payload["best_by_family"].items():
        summary = result["summary"]
        train = result["train_summary"]
        holdout = result["holdout_summary"]
        lines.extend(
            [
                "",
                f"### {family} `{result['strategy_id']}`",
                "",
                f"- Status: {status_for(result)}",
                f"- Theorem: {result['theorem']}",
                f"- Equation: `{result['equation']}`",
                f"- Train-selected params: `{json.dumps(result['params'], sort_keys=True)}`",
                f"- Full selected sim PnL: `${summary['sim_pnl']}`",
                f"- Full selected delta vs actual / no-stop: `${summary['delta_vs_actual']}` / `${summary['delta_vs_no_stop']}`",
                f"- Train sim PnL: `${train['sim_pnl']}`",
                f"- Holdout sim PnL: `${holdout['sim_pnl']}`",
                f"- Holdout delta vs actual / no-stop: `${holdout['delta_vs_actual']}` / `${holdout['delta_vs_no_stop']}`",
                f"- Holdout exits / false exits / missed true losers: `{holdout['exits']} / {holdout['false_exit_settlement_winners']} / {holdout['missed_true_losers']}`",
                f"- Holdout false-exit / missed-loser rate: `{holdout['false_exit_rate']} / {holdout['missed_true_loser_rate']}`",
                f"- Model diagnostics: `{json.dumps(result['model_diagnostics'], sort_keys=True)}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Holdout Sensitivity Near Train Selection",
            "",
            "| Family | Strategy | Holdout PnL | Delta vs actual | Delta vs no-stop | Exits | False | Missed losers |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for family, items in payload["sensitivity"].items():
        for item in items[:5]:
            lines.append(
                f"| `{family}` | `{item['strategy_id']}` | {item['holdout_sim_pnl']} | "
                f"{item['holdout_delta_vs_actual']} | {item['holdout_delta_vs_no_stop']} | "
                f"{item['holdout_exits']} | {item['holdout_false_exits']} | {item['holdout_missed_true_losers']} |"
            )
    lines.extend(
        [
            "",
            "## Audit Notes",
            "",
            "- Calibration models are fit on the chronological 70% train split only before holdout scoring.",
            "- The fee-adjusted EV comparison cancels sunk entry cost and compares current sale proceeds with calibrated expected settlement proceeds.",
            "- Features are available at decision time: close time from ticker, own/opposite bids, own ask, held ask, bid sum, and trailing quote path.",
            "- This run is research-only and does not modify live entry logic, live exit logic, production config, run scripts, or bot processes.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only calibrated EV probes for Kalshi BTC 15m exits.")
    parser.add_argument("--refresh-cache", action="store_true")
    parser.add_argument("--datasets", nargs="*", default=None)
    args = parser.parse_args()

    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    datasets = args.datasets or discover_datasets()
    dataset_payloads = [load_dataset_cases(dataset, refresh_cache=args.refresh_cache) for dataset in datasets]
    cases: list[dict[str, Any]] = []
    for payload in dataset_payloads:
        for case in payload.get("cases", []):
            case.setdefault("dataset", payload.get("dataset"))
            cases.append(case)
    cases = sorted(cases, key=lambda case: (case["entry_ts"], case["market"], case["side"]))
    strategies = build_strategy_grid()
    walk, best_by_family, sens = walk_forward_results(cases, strategies)

    baselines = {
        "actual": run_baseline(cases, "actual"),
        "no_stop": run_baseline(cases, "no_stop"),
        "held_ask_stop_70": run_baseline(cases, "held_ask_stop_70"),
    }
    terminal_window_baseline = run_terminal(cases, dict(TERMINAL_BASELINE_PARAMS), "terminal_window_salvage_fixed")

    generated_at = datetime.now(UTC).isoformat()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"codex_calibrated_ev_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_calibrated_ev_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_calibrated_ev_research_latest.json"
    latest_md = EDGE_DIR / "codex_calibrated_ev_research_latest.md"
    payload = {
        "generated_at": generated_at,
        "dataset": "all_quote_path_trades",
        "datasets": sorted({str(case.get("dataset")) for case in cases}),
        "requested_datasets": datasets,
        "case_count": len(cases),
        "baselines": baselines,
        "terminal_window_baseline": terminal_window_baseline,
        "walk_forward": walk,
        "best_by_family": best_by_family,
        "sensitivity": sens,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "feature_availability": {
            "calibrated_terminal_ev_gap": "current own bid, held ask, pressure, seconds to close, actual quantity for fee estimate",
            "recovery_zscore_calibrated_ev": "trailing held-ask path volatility, current held ask, pressure, seconds to close, current own bid",
            "book_parity_consistency_exit": "current own bid/ask, opponent bid, held ask, bid sum, and seconds to close",
        },
        "live_logic_changed": False,
    }
    json_text = json.dumps(payload, indent=2, sort_keys=True)
    json_path.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")
    write_markdown(md_path, payload)
    write_markdown(latest_md, payload)

    ledger_records: list[dict[str, Any]] = []
    for family, result in best_by_family.items():
        ledger_records.append(
            {
                "recorded_at": datetime.now(UTC).isoformat(),
                "status": status_for(result),
                "source": "probe_codex_calibrated_ev_edges.py",
                "dataset": "all_quote_path_trades",
                "datasets": payload["datasets"],
                "strategy_id": result["strategy_id"],
                "idea_key": idea_key(result["family"], result["equation"], result["params"]),
                "family": result["family"],
                "theorem": result["theorem"],
                "equation": result["equation"],
                "params": result["params"],
                "param_grid_size": len([item for item in strategies if item.family == family]),
                "generated_at": generated_at,
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "summary": result["summary"],
                "train_summary": result["train_summary"],
                "holdout_summary": result["holdout_summary"],
                "walk_forward_selected_strategy_id": walk["families"][family]["selected_strategy_id"],
                "walk_forward_selected_params": walk["families"][family]["selected_params"],
                "sensitivity_excerpt": sens.get(family, [])[:5],
            }
        )
    append_ledger(ledger_records)
    update_strategy_memory(payload, best_by_family)

    print(f"Saved JSON: {json_path}")
    print(f"Saved Markdown: {md_path}")
    print(
        f"Cases={len(cases)} datasets={','.join(payload['datasets'])} "
        f"actual={baselines['actual']['summary']['sim_pnl']} no_stop={baselines['no_stop']['summary']['sim_pnl']} "
        f"terminal_fixed={terminal_window_baseline['summary']['sim_pnl']} split={walk['split_entry_ts']}"
    )
    for family, result in best_by_family.items():
        summary = result["summary"]
        holdout = result["holdout_summary"]
        print(
            f"{family} {result['strategy_id']} status={status_for(result)} "
            f"full_sim={summary['sim_pnl']} full_delta_actual={summary['delta_vs_actual']} "
            f"holdout_sim={holdout['sim_pnl']} holdout_delta_actual={holdout['delta_vs_actual']} "
            f"holdout_delta_no_stop={holdout['delta_vs_no_stop']} exits={holdout['exits']} "
            f"false={holdout['false_exit_settlement_winners']} missed_losers={holdout['missed_true_losers']}"
        )


if __name__ == "__main__":
    main()
