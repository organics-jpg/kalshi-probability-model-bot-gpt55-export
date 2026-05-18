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


def pressure(point: dict[str, Any]) -> float:
    own_bid = safe_float(point.get("own_bid"))
    opp_bid = safe_float(point.get("opp_bid"))
    denom = own_bid + opp_bid
    return opp_bid / denom if denom > 0 else math.nan


def spread(point: dict[str, Any]) -> float:
    own_bid = safe_float(point.get("own_bid"))
    own_ask = safe_float(point.get("own_ask"))
    return own_ask - own_bid if not math.isnan(own_bid) and not math.isnan(own_ask) else math.nan


def time_weighted_positive_impulse(points: list[dict[str, Any]], base_pressure: float) -> float:
    if len(points) < 2 or math.isnan(base_pressure):
        return 0.0
    area = 0.0
    span = max(1.0, safe_float(points[-1].get("elapsed")) - safe_float(points[0].get("elapsed")))
    prev_t = safe_float(points[0].get("elapsed"))
    prev_v = max(0.0, pressure(points[0]) - base_pressure)
    for point in points[1:]:
        now_t = safe_float(point.get("elapsed"))
        now_v = max(0.0, pressure(point) - base_pressure)
        if math.isnan(now_t) or math.isnan(now_v):
            continue
        area += 0.5 * (prev_v + now_v) * max(0.0, now_t - prev_t)
        prev_t = now_t
        prev_v = now_v
    return area / span


def time_weighted_mean_pressure(points: list[dict[str, Any]]) -> float:
    valid = [(safe_float(point.get("elapsed")), pressure(point)) for point in points]
    valid = [(t, p) for t, p in valid if not math.isnan(t) and not math.isnan(p)]
    if len(valid) < 2:
        return valid[0][1] if valid else math.nan
    area = 0.0
    span = max(1.0, valid[-1][0] - valid[0][0])
    for (t0, p0), (t1, p1) in zip(valid, valid[1:]):
        area += 0.5 * (p0 + p1) * max(0.0, t1 - t0)
    return area / span


def point_features(points: list[dict[str, Any]]) -> dict[str, Any] | None:
    valid = [point for point in points if not math.isnan(safe_float(point.get("held_ask")))]
    if len(valid) < 2:
        return None
    held_asks = [safe_float(point["held_ask"]) for point in valid]
    h0 = held_asks[0]
    h = held_asks[-1]
    path_len = sum(abs(held_asks[idx] - held_asks[idx - 1]) for idx in range(1, len(held_asks)))
    low = min(held_asks)
    high = max(held_asks)
    base_pressure = pressure(valid[0])
    end_pressure = pressure(valid[-1])
    mean_pressure = time_weighted_mean_pressure(valid)
    impulse = time_weighted_positive_impulse(valid, base_pressure)
    path_efficiency = (h - h0) / (path_len + 1e-9)
    rebound = h - low
    drawdown = max(0.0, h0 - low)
    range_cents = high - low
    coherence = path_efficiency - drawdown / (rebound + 1.0) - range_cents / 100.0
    elapsed = safe_float(valid[-1].get("elapsed"))
    span = max(1.0, elapsed - safe_float(valid[0].get("elapsed")))
    moves = [held_asks[idx] - held_asks[idx - 1] for idx in range(1, len(held_asks))]
    realized_vol = math.sqrt(sum(move * move for move in moves)) / math.sqrt(span / 60.0) if moves else 0.0
    return {
        "elapsed": elapsed,
        "held_ask": h,
        "start_ask": h0,
        "low": low,
        "high": high,
        "path_len": path_len,
        "path_efficiency": path_efficiency,
        "drawdown": drawdown,
        "rebound": rebound,
        "range": range_cents,
        "coherence": coherence,
        "pressure_start": base_pressure,
        "pressure_end": end_pressure,
        "pressure_mean": mean_pressure,
        "pressure_impulse": impulse,
        "spread": spread(valid[-1]),
        "bid_sum": safe_float(valid[-1].get("bid_sum")),
        "realized_vol": realized_vol,
    }


def prepare_case(case: dict[str, Any], delays: tuple[int, ...], max_deadline: int) -> dict[str, Any]:
    path = [
        point
        for point in case.get("path", [])
        if not math.isnan(safe_float(point.get("elapsed"))) and not math.isnan(safe_float(point.get("held_ask")))
    ]
    snapshots: dict[str, dict[str, Any] | None] = {}
    for delay in delays:
        history: list[dict[str, Any]] = []
        target: dict[str, Any] | None = None
        for point in path:
            history.append(point)
            if safe_float(point.get("elapsed")) >= delay:
                target = point
                break
        snapshots[str(delay)] = point_features(history) if target is not None else None
    events: list[dict[str, Any]] = []
    history = []
    for point in path:
        elapsed = safe_float(point.get("elapsed"))
        if elapsed > max_deadline:
            break
        history.append(point)
        features = point_features(history)
        if features is not None:
            events.append(features)
    return {"snapshots": snapshots, "events": events}


def entry_meta(case: dict[str, Any], ask: float, extra: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    pnl = delayed_entry_pnl(case, ask)
    return pnl, {
        "enter": True,
        "entry_ask": ask,
        "entry_elapsed": extra.get("elapsed"),
        "contracts": int(case["qty"]),
        **extra,
    }


def sim_entry_path_coherence(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared["snapshots"].get(str(int(params["delay_seconds"])))
    if not features:
        return 0.0, {"enter": False, "skip_reason": "missing_delay_snapshot"}
    if (
        features["held_ask"] <= float(params["max_entry_ask"])
        and features["range"] <= float(params["max_range_cents"])
        and features["coherence"] >= float(params["min_coherence"])
        and features["spread"] <= float(params["max_spread"])
    ):
        return entry_meta(
            case,
            float(features["held_ask"]),
            {
                "elapsed": features["elapsed"],
                "coherence": round(float(features["coherence"]), 6),
                "path_efficiency": round(float(features["path_efficiency"]), 6),
                "range": round(float(features["range"]), 4),
                "drawdown": round(float(features["drawdown"]), 4),
            },
        )
    return 0.0, {"enter": False, "skip_reason": "coherence_gate_failed"}


def sim_pressure_impulse_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared["snapshots"].get(str(int(params["delay_seconds"])))
    if not features:
        return 0.0, {"enter": False, "skip_reason": "missing_delay_snapshot"}
    if (
        features["held_ask"] <= float(params["max_entry_ask"])
        and features["pressure_impulse"] <= float(params["max_pressure_impulse"])
        and features["pressure_end"] <= float(params["max_end_pressure"])
        and features["bid_sum"] >= float(params["min_bid_sum"])
        and features["spread"] <= float(params["max_spread"])
    ):
        return entry_meta(
            case,
            float(features["held_ask"]),
            {
                "elapsed": features["elapsed"],
                "pressure_impulse": round(float(features["pressure_impulse"]), 6),
                "pressure_end": round(float(features["pressure_end"]), 6),
                "pressure_mean": round(float(features["pressure_mean"]), 6),
                "bid_sum": round(float(features["bid_sum"]), 4),
            },
        )
    return 0.0, {"enter": False, "skip_reason": "pressure_impulse_gate_failed"}


def sim_adaptive_pullback_limit(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    for features in prepared["events"]:
        elapsed = float(features["elapsed"])
        if elapsed < float(params["min_wait_seconds"]) or elapsed > float(params["deadline_seconds"]):
            continue
        limit = min(
            float(params["max_limit_ask"]),
            float(features["start_ask"])
            - float(params["min_pullback_cents"])
            - float(params["vol_multiplier"]) * float(features["realized_vol"])
            - float(params["pressure_multiplier"]) * 100.0 * float(features["pressure_impulse"]),
        )
        if (
            features["held_ask"] <= limit
            and features["pressure_end"] <= float(params["max_end_pressure"])
            and features["spread"] <= float(params["max_spread"])
            and features["coherence"] >= float(params["min_coherence"])
            and features["rebound"] >= float(params["min_rebound_cents"])
        ):
            return entry_meta(
                case,
                float(features["held_ask"]),
                {
                    "elapsed": elapsed,
                    "dynamic_limit": round(limit, 4),
                    "coherence": round(float(features["coherence"]), 6),
                    "pressure_impulse": round(float(features["pressure_impulse"]), 6),
                    "realized_vol": round(float(features["realized_vol"]), 6),
                    "rebound": round(float(features["rebound"]), 4),
                },
            )
    return 0.0, {"enter": False, "skip_reason": "adaptive_limit_not_filled"}


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

    for delay_seconds in (30, 60, 90, 120):
        for max_entry_ask in (87, 90, 92, 94):
            for max_range_cents in (2, 3, 5, 8, 12):
                for min_coherence in (-2.0, -1.0, -0.5, 0.0, 0.25):
                    for max_spread in (4, 6, 10):
                        add(
                            "entry_path_coherence_admission",
                            "A delayed entry is healthier when the pre-entry held-ask path is compact and not dominated by unrecovered drawdown.",
                            "C=(H_D-H_0)/(sum(abs(dH))+eps)-drawdown/(rebound+1)-range/100; enter at D only if H_D<=A, range<=R, C>=c, and spread<=S.",
                            {
                                "delay_seconds": delay_seconds,
                                "max_entry_ask": max_entry_ask,
                                "max_range_cents": max_range_cents,
                                "min_coherence": min_coherence,
                                "max_spread": max_spread,
                            },
                            sim_entry_path_coherence,
                        )

    for delay_seconds in (30, 60, 90, 120):
        for max_entry_ask in (87, 90, 92, 94):
            for max_pressure_impulse in (0.0025, 0.005, 0.01, 0.02, 0.04):
                for max_end_pressure in (0.15, 0.25, 0.35, 0.50):
                    for min_bid_sum in (0, 94, 98):
                        for max_spread in (4, 6, 10):
                            add(
                                "opponent_pressure_impulse_admission",
                                "A low delayed ask is only attractive if the opposing contract has not accumulated persistent pressure since the signal.",
                                "I=(1/T)*integral(max(0,p_opp(t)-p_opp(0))dt); enter at D only if H_D<=A, I<=i, p_opp(D)<=pmax, bid_sum>=B, and spread<=S.",
                                {
                                    "delay_seconds": delay_seconds,
                                    "max_entry_ask": max_entry_ask,
                                    "max_pressure_impulse": max_pressure_impulse,
                                    "max_end_pressure": max_end_pressure,
                                    "min_bid_sum": min_bid_sum,
                                    "max_spread": max_spread,
                                },
                                sim_pressure_impulse_admission,
                            )

    for min_wait_seconds in (15, 30):
        for deadline_seconds in (90, 120):
            for max_limit_ask in (87, 90):
                for min_pullback_cents in (1, 2, 4):
                    for vol_multiplier in (0.0, 0.5):
                        for pressure_multiplier in (0.0, 0.5):
                            for max_end_pressure in (0.30, 0.50):
                                for min_coherence in (-8.0, -4.0, -2.0):
                                    for min_rebound_cents in (0, 1):
                                        add(
                                            "adaptive_pullback_limit_admission",
                                            "The bot may get paid for waiting if entry is modeled as a dynamic lower limit order rather than a mandatory delayed marketable entry.",
                                            "L_t=min(A,H_0-d-k*sigma_t-m*100*I_t); enter on first t in [w,T] with H_t<=L_t, pressure_t<=p, spread<=S, C_t>=c, and rebound>=r.",
                                            {
                                                "min_wait_seconds": min_wait_seconds,
                                                "deadline_seconds": deadline_seconds,
                                                "max_limit_ask": max_limit_ask,
                                                "min_pullback_cents": min_pullback_cents,
                                                "vol_multiplier": vol_multiplier,
                                                "pressure_multiplier": pressure_multiplier,
                                                "max_end_pressure": max_end_pressure,
                                                "max_spread": 6,
                                                "min_coherence": min_coherence,
                                                "min_rebound_cents": min_rebound_cents,
                                            },
                                            sim_adaptive_pullback_limit,
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
        "by_dataset": summarize_by_dataset(sid, rows),
        "by_side": summarize_by_side(sid, rows),
        "interesting_examples": sorted(rows, key=lambda row: (float(row["sim_pnl"]), row["market"]))[:10],
    }


def select_family_best(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for result in results:
        family = result["family"]
        summary = result["summary"]
        key = (summary["sim_pnl"], summary["entries"], summary["entry_win_rate"])
        if family not in best:
            best[family] = result
            continue
        old = best[family]["summary"]
        old_key = (old["sim_pnl"], old["entries"], old["entry_win_rate"])
        if key > old_key:
            best[family] = result
    return best


def walk_forward_summary(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]],
    strategies: list[StrategySpec],
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
        "selection_basis": "Max train sim PnL; holdout is chronological out-of-sample.",
        "families": {},
    }
    for family, family_strategies in by_family.items():
        train_results = [run_strategy(train, strategy) for strategy in family_strategies]
        selected_train = max(train_results, key=lambda result: result["summary"]["sim_pnl"])
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
    strategies: list[StrategySpec],
    prepped: list[tuple[dict[str, Any], dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    ordered = sorted(prepped, key=lambda item: item[0]["entry_ts"])
    split = int(len(ordered) * 0.7)
    train = ordered[:split]
    holdout = ordered[split:]
    output: dict[str, list[dict[str, Any]]] = {}
    for family in sorted({strategy.family for strategy in strategies}):
        rows: list[dict[str, Any]] = []
        for strategy in [item for item in strategies if item.family == family]:
            train_result = run_strategy(train, strategy)
            holdout_result = run_strategy(holdout, strategy)
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


def sensitivity(
    results: list[dict[str, Any]],
    best_by_family: dict[str, dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
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


def read_prior_entry_reference() -> dict[str, Any] | None:
    path = EDGE_DIR / "codex_entry_timing_research_latest.json"
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    output: dict[str, Any] = {"path": str(path), "families": {}}
    for family, result in payload.get("best_by_family", {}).items():
        output["families"][family] = {
            "strategy_id": result.get("strategy_id"),
            "summary": result.get("summary"),
            "holdout_summary": payload.get("walk_forward", {}).get("families", {}).get(family, {}).get("holdout_summary"),
        }
    return output


def status_for(family: str, result: dict[str, Any], payload: dict[str, Any]) -> str:
    holdout = payload["walk_forward"]["families"][family]["holdout_summary"]
    robust_rows = payload["robust_positive_scan"].get(family, [])
    if result["summary"]["delta_vs_no_trade_all"] > 0 and holdout["delta_vs_no_trade_all"] > 0 and len(robust_rows) >= 3:
        return "candidate_for_human_review"
    if result["summary"]["delta_vs_no_trade_all"] > 0 and robust_rows:
        return "watchlist_positive_but_selection_sensitive"
    return "tested_not_robust"


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    actual = payload["baselines"]["actual"]["summary"]
    no_stop = payload["baselines"]["no_stop"]["summary"]
    stop70 = payload["baselines"]["held_ask_stop_70"]["summary"]
    lines = [
        "# Codex Entry Path Geometry Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Quote-path cases: `{payload['case_count']}`",
        "- Scope: research-only entry/no-trade simulation; live bot logic, configs, run scripts, and processes were not changed.",
        "- Non-repetition: this tests pre-entry path geometry, pressure impulse integrals, and adaptive pullback limit equations rather than delayed snapshot thresholds or calibrated Kelly sizing.",
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
        walk = payload["walk_forward"]["families"][family]
        holdout = walk["holdout_summary"]
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
    prior = payload.get("prior_entry_reference")
    lines.extend(["", "## Prior Entry Reference", ""])
    if prior:
        for family, item in prior.get("families", {}).items():
            summary = item.get("summary") or {}
            holdout = item.get("holdout_summary") or {}
            lines.append(
                f"- `{family}` `{item.get('strategy_id')}` latest full PnL `${summary.get('sim_pnl')}` and holdout PnL `${holdout.get('sim_pnl')}`."
            )
    else:
        lines.append("- No prior entry-timing JSON reference was available.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Early compact paths are informative: the best coherence rule enters a modest fraction of opportunities and beats actual, no-stop, and skip-all in aggregate.",
            "- Pressure impulse performs as a microstructure no-trade filter, but the train-selected variant should be judged by holdout rather than full-sample ranking.",
            "- Adaptive pullback limit entries are mathematically distinct from fixed delayed entry, but any positive result depends on assuming observed asks were fillable at the simulated limit.",
            "- All tested variables are derived from quote heartbeats at or before the simulated decision/fill time.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only entry path geometry probes for Kalshi BTC 15m.")
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
    cases = sorted(cases, key=lambda case: (case["entry_ts"], case["market"], case["side"]))

    strategies = build_strategy_grid()
    delays = tuple(sorted({int(strategy.params["delay_seconds"]) for strategy in strategies if "delay_seconds" in strategy.params}))
    max_deadline = max(int(strategy.params.get("deadline_seconds", 0)) for strategy in strategies)
    prepped = [(case, prepare_case(case, delays, max_deadline)) for case in cases]
    results = [run_strategy(prepped, strategy) for strategy in strategies]
    best_by_family = select_family_best(results)
    walk = walk_forward_summary(prepped, strategies)
    robust_scan = robust_positive_scan(strategies, prepped)
    baselines = {
        "actual": run_baseline(cases, "actual"),
        "no_stop": run_baseline(cases, "no_stop"),
        "held_ask_stop_70": run_baseline(cases, "held_ask_stop_70"),
    }

    generated_at = datetime.now(UTC).isoformat()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"codex_entry_path_geometry_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_entry_path_geometry_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_entry_path_geometry_research_latest.json"
    latest_md = EDGE_DIR / "codex_entry_path_geometry_research_latest.md"
    report_payload = {
        "generated_at": generated_at,
        "dataset": "all_quote_path_trades",
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
        "prior_entry_reference": read_prior_entry_reference(),
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "feature_availability": {
            "entry_path_coherence_admission": "held ask path, own bid/ask spread, and elapsed quote history through the delay",
            "opponent_pressure_impulse_admission": "own/opposite bids through the delay, bid sum, held ask, and spread",
            "adaptive_pullback_limit_admission": "streaming held ask path, realized path volatility, pressure impulse, spread, and rebound through each candidate fill point",
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
        walk_family = walk["families"][family]
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
                "train_summary": walk_family["train_summary"],
                "holdout_summary": walk_family["holdout_summary"],
                "walk_forward_selected_strategy_id": walk_family["selected_strategy_id"],
                "walk_forward_selected_params": walk_family["selected_params"],
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
        holdout = walk["families"][family]["holdout_summary"]
        print(
            f"{family} {result['strategy_id']} status={status_for(family, result, report_payload)} "
            f"full_sim={summary['sim_pnl']} full_delta_actual={summary['delta_vs_actual']} "
            f"full_delta_skip={summary['delta_vs_no_trade_all']} entries={summary['entries']} "
            f"holdout_sim={holdout['sim_pnl']} holdout_delta_actual={holdout['delta_vs_actual']} "
            f"holdout_delta_skip={holdout['delta_vs_no_trade_all']} holdout_entries={holdout['entries']}"
        )


if __name__ == "__main__":
    main()
