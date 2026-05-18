from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from research_pipeline import parse_market_close_from_ticker
from probe_stop_touch_confirmation import (
    DATASET,
    EDGE_DIR,
    append_ledger,
    baseline_rows,
    exit_pnl,
    idea_key,
    load_cases,
    load_truffle_reference,
    result_distance,
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
    simulator: Callable[[dict[str, Any], dict[str, Any]], tuple[float, dict[str, Any]]]


def strategy_id(family: str, params: dict[str, Any]) -> str:
    import hashlib

    encoded = json.dumps({"family": family, "params": params}, sort_keys=True)
    return f"{family}_{hashlib.sha1(encoded.encode('utf-8')).hexdigest()[:8]}"


def case_entry_dt(case: dict[str, Any]) -> datetime:
    return datetime.fromisoformat(str(case["entry_ts"]))


def seconds_to_close(case: dict[str, Any], point: dict[str, Any]) -> float | None:
    close_dt = parse_market_close_from_ticker(str(case.get("market") or ""))
    if close_dt is None:
        return None
    now_dt = case_entry_dt(case) + timedelta(seconds=float(point["elapsed"]))
    return float((close_dt - now_dt).total_seconds())


def sim_terminal_window_salvage(case: dict[str, Any], params: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    panic_trigger = float(params["held_ask_max"])
    final_window = float(params["final_window_seconds"])
    min_remaining = float(params["min_remaining_seconds"])
    for point in case["path"]:
        remaining = seconds_to_close(case, point)
        if remaining is None or remaining < min_remaining or remaining > final_window:
            continue
        held_ask = float(point.get("held_ask", math.nan))
        if math.isnan(held_ask) or held_ask > panic_trigger:
            continue
        bid = float(point["own_bid"])
        return exit_pnl(case, bid), {
            "exit": True,
            "exit_bid": bid,
            "exit_elapsed": float(point["elapsed"]),
            "held_ask": held_ask,
            "seconds_to_close": round(remaining, 3),
        }
    return float(case["hold_pnl"]), {"exit": False}


def sim_pressure_persistence(case: dict[str, Any], params: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    pressure_min = float(params["pressure_min"])
    min_pressure_gain = float(params["min_pressure_gain"])
    window = float(params["window_seconds"])
    min_elapsed = float(params["min_elapsed_seconds"])
    held_ask_max = float(params["held_ask_max"])
    for idx, point in enumerate(case["path"]):
        if float(point["elapsed"]) < min_elapsed:
            continue
        own_bid = float(point.get("own_bid", math.nan))
        opp_bid = float(point.get("opp_bid", math.nan))
        held_ask = float(point.get("held_ask", math.nan))
        if any(math.isnan(value) for value in (own_bid, opp_bid, held_ask)):
            continue
        if held_ask > held_ask_max:
            continue
        denom = own_bid + opp_bid
        if denom <= 0:
            continue
        pressure_now = opp_bid / denom
        window_start = float(point["elapsed"]) - window
        prior_points = [item for item in case["path"][: idx + 1] if float(item["elapsed"]) >= window_start]
        if len(prior_points) < 2:
            continue
        first = prior_points[0]
        first_own = float(first.get("own_bid", math.nan))
        first_opp = float(first.get("opp_bid", math.nan))
        first_denom = first_own + first_opp
        if math.isnan(first_own) or math.isnan(first_opp) or first_denom <= 0:
            continue
        pressure_gain = pressure_now - (first_opp / first_denom)
        if pressure_now >= pressure_min and pressure_gain >= min_pressure_gain:
            return exit_pnl(case, own_bid), {
                "exit": True,
                "exit_bid": own_bid,
                "exit_elapsed": float(point["elapsed"]),
                "held_ask": held_ask,
                "pressure": round(pressure_now, 4),
                "pressure_gain": round(pressure_gain, 4),
            }
    return float(case["hold_pnl"]), {"exit": False}


def sim_failed_safety_checkpoint(case: dict[str, Any], params: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    checkpoint = float(params["checkpoint_seconds"])
    safety_bid = float(params["safety_bid"])
    current_bid_max = float(params["current_bid_max"])
    min_peak_gap = float(params["min_peak_gap"])
    checkpoint_idx: int | None = None
    for idx, point in enumerate(case["path"]):
        if float(point["elapsed"]) >= checkpoint:
            checkpoint_idx = idx
            break
    if checkpoint_idx is None:
        return float(case["hold_pnl"]), {"exit": False}
    point = case["path"][checkpoint_idx]
    current_bid = float(point["own_bid"])
    peak_bid = max(float(item["own_bid"]) for item in case["path"][: checkpoint_idx + 1])
    if peak_bid < safety_bid and current_bid <= current_bid_max and peak_bid - current_bid >= min_peak_gap:
        return exit_pnl(case, current_bid), {
            "exit": True,
            "exit_bid": current_bid,
            "exit_elapsed": float(point["elapsed"]),
            "peak_bid": peak_bid,
        }
    return float(case["hold_pnl"]), {"exit": False}


def build_strategy_grid() -> list[StrategySpec]:
    strategies: list[StrategySpec] = []

    def add(
        family: str,
        theorem: str,
        equation: str,
        params: dict[str, Any],
        simulator: Callable[[dict[str, Any], dict[str, Any]], tuple[float, dict[str, Any]]],
    ) -> None:
        strategies.append(StrategySpec(family, theorem, equation, params, simulator))

    for held_ask_max in (10, 15, 20, 25, 30, 35, 40, 45, 50):
        for final_window_seconds in (30, 45, 60, 75, 90, 120, 150, 180):
            for min_remaining_seconds in (1, 5, 10, 15, 30):
                if min_remaining_seconds >= final_window_seconds:
                    continue
                add(
                    "terminal_window_salvage",
                    "A low held-side ask is much more informative in the final tradable minute than earlier in the contract.",
                    "Exit only when 0 < seconds_to_close <= W, seconds_to_close >= m, and held_ask <= H; otherwise hold to settlement.",
                    {
                        "held_ask_max": held_ask_max,
                        "final_window_seconds": final_window_seconds,
                        "min_remaining_seconds": min_remaining_seconds,
                    },
                    sim_terminal_window_salvage,
                )

    for pressure_min in (0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90):
        for min_pressure_gain in (0.05, 0.10, 0.15, 0.20, 0.25, 0.30):
            for window_seconds in (30, 45, 60, 90, 120):
                for held_ask_max in (40, 50, 70, 90, 101):
                    add(
                        "rival_pressure_persistence",
                        "Terminal losers should show persistent migration of bid probability toward the opposite side, not only a single stop touch.",
                        "pressure=opp_bid/(own_bid+opp_bid); exit when pressure >= P, pressure-pressure_window_start >= G, and held_ask <= H.",
                        {
                            "pressure_min": pressure_min,
                            "min_pressure_gain": min_pressure_gain,
                            "window_seconds": window_seconds,
                            "held_ask_max": held_ask_max,
                            "min_elapsed_seconds": 30,
                        },
                        sim_pressure_persistence,
                    )

    for checkpoint_seconds in (45, 60, 75, 90, 120, 150):
        for safety_bid in (90, 92, 94, 96):
            for current_bid_max in (75, 80, 85, 88, 90):
                for min_peak_gap in (0, 2, 5, 8, 12):
                    add(
                        "failed_safety_checkpoint",
                        "A good high-probability fill should usually prove itself quickly by reaching a safety bid; failure plus weakness may justify early de-risking.",
                        "At checkpoint T, exit if max_own_bid_since_entry < S, current_own_bid <= B, and peak-current >= G.",
                        {
                            "checkpoint_seconds": checkpoint_seconds,
                            "safety_bid": safety_bid,
                            "current_bid_max": current_bid_max,
                            "min_peak_gap": min_peak_gap,
                        },
                        sim_failed_safety_checkpoint,
                    )
    return strategies


def run_strategy(cases: list[dict[str, Any]], strategy: StrategySpec) -> dict[str, Any]:
    sid = strategy_id(strategy.family, strategy.params)
    rows: list[dict[str, Any]] = []
    for case in cases:
        pnl, meta = strategy.simulator(case, strategy.params)
        exit_bid = meta.get("exit_bid")
        rows.append(
            {
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
        )
    by_day: dict[str, dict[str, Any]] = {}
    for day in sorted({row["entry_day_et"] for row in rows}):
        by_day[day] = summarize_rows(day, [row for row in rows if row["entry_day_et"] == day])
    return {
        "strategy_id": sid,
        "family": strategy.family,
        "theorem": strategy.theorem,
        "equation": strategy.equation,
        "params": strategy.params,
        "summary": summarize_rows(sid, rows),
        "by_day": by_day,
        "interesting_examples": sorted(
            rows,
            key=lambda row: (
                float(row["sim_pnl"]) - float(row["hold_pnl"]),
                -float(row["max_drawdown"]),
            ),
            reverse=True,
        )[:10],
    }


def select_family_best(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for result in results:
        family = result["family"]
        if family not in best or result["summary"]["sim_pnl"] > best[family]["summary"]["sim_pnl"]:
            best[family] = result
    return best


def walk_forward_summary(cases: list[dict[str, Any]], strategies: list[StrategySpec]) -> dict[str, Any]:
    ordered = sorted(cases, key=lambda case: case["entry_ts"])
    split = int(len(ordered) * 0.7)
    train = ordered[:split]
    holdout = ordered[split:]
    by_family: dict[str, list[StrategySpec]] = {}
    for strategy in strategies:
        by_family.setdefault(strategy.family, []).append(strategy)
    output: dict[str, Any] = {
        "train_n": len(train),
        "holdout_n": len(holdout),
        "split_entry_ts": ordered[split]["entry_ts"] if holdout else None,
        "families": {},
    }
    for family, items in by_family.items():
        train_results = [run_strategy(train, strategy) for strategy in items]
        selected = max(train_results, key=lambda result: result["summary"]["sim_pnl"])
        selected_spec = next(
            strategy for strategy in items if strategy_id(strategy.family, strategy.params) == selected["strategy_id"]
        )
        output["families"][family] = {
            "selected_strategy_id": selected["strategy_id"],
            "selected_params": selected["params"],
            "train_summary": selected["summary"],
            "holdout_summary": run_strategy(holdout, selected_spec)["summary"],
            "full_summary": run_strategy(ordered, selected_spec)["summary"],
        }
    return output


def sensitivity(results: list[dict[str, Any]], best_by_family: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    for family, best in best_by_family.items():
        family_results = [result for result in results if result["family"] == family]
        ranked = sorted(
            family_results,
            key=lambda result: (result_distance(result["params"], best["params"]), -result["summary"]["sim_pnl"]),
        )
        output[family] = [
            {
                "strategy_id": result["strategy_id"],
                "params": result["params"],
                "sim_pnl": result["summary"]["sim_pnl"],
                "delta_vs_actual": result["summary"]["delta_vs_actual"],
                "delta_vs_no_stop": result["summary"]["delta_vs_no_stop"],
                "exits": result["summary"]["exits"],
                "false_exits": result["summary"]["false_exit_settlement_winners"],
                "missed_true_losers": result["summary"]["missed_true_losers"],
            }
            for result in ranked[:12]
        ]
    return output


def status_for(result: dict[str, Any], holdout_summary: dict[str, Any]) -> str:
    summary = result["summary"]
    if summary["delta_vs_no_stop"] > 0 and holdout_summary["delta_vs_no_stop"] > 0:
        if summary["false_exit_rate"] <= 0.05 and summary["missed_true_loser_rate"] <= 0.05:
            return "candidate_for_human_review"
        return "watchlist_positive_but_noisy"
    return "tested_not_robust"


def write_markdown_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Codex Terminal Path Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Dataset: `{payload['dataset']}`",
        f"- Cases: `{payload['case_count']}`",
        "- Settlement labels: corrected via `stats/live_90_70/market_results.csv` in the cross-book case cache.",
        f"- Actual recorded PnL: `${payload['baselines']['actual']['sim_pnl']}`",
        f"- No-stop hold-to-settlement PnL: `${payload['baselines']['no_stop']['sim_pnl']}`",
        f"- Deterministic confirmed held-ask stop 70 PnL: `${payload['baselines']['stop_70']['sim_pnl']}`",
        f"- Prior deep-panic candidate PnL: `${payload['prior_deep_panic_reference'].get('sim_pnl')}`",
        "",
        "## New Hypotheses Tested",
    ]
    for family, result in payload["best_by_family"].items():
        summary = result["summary"]
        family_walk = payload["walk_forward"]["families"][family]
        holdout = family_walk["holdout_summary"]
        lines.extend(
            [
                "",
                f"### {family} `{result['strategy_id']}`",
                "",
                f"- Status: {status_for(result, holdout)}",
                f"- Theorem: {result['theorem']}",
                f"- Equation: `{result['equation']}`",
                f"- Full-sample best params: `{json.dumps(result['params'], sort_keys=True)}`",
                f"- Full-sample sim PnL: `${summary['sim_pnl']}`",
                f"- Delta vs actual: `${summary['delta_vs_actual']}`",
                f"- Delta vs no-stop hold: `${summary['delta_vs_no_stop']}`",
                f"- Exits / false exits / missed true losers: `{summary['exits']} / {summary['false_exit_settlement_winners']} / {summary['missed_true_losers']}`",
                f"- Train-selected params: `{json.dumps(family_walk['selected_params'], sort_keys=True)}`",
                f"- Train-selected holdout sim PnL: `${holdout['sim_pnl']}`",
                f"- Train-selected holdout delta vs no-stop: `${holdout['delta_vs_no_stop']}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Truffle / Prior Policy Reference",
            "",
            f"- Online supervisor eval reference: `{json.dumps(payload['truffle_reference'], sort_keys=True)}`",
            "",
            "## Guardrail",
            "",
            "This run is research-only. It does not modify live entry logic, live exit logic, run scripts, or production config.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def prior_deep_panic_reference() -> dict[str, Any]:
    path = EDGE_DIR / "codex_stop_touch_research_latest.json"
    if not path.exists():
        return {"available": False}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"available": False}
    result = payload.get("best_by_family", {}).get("held_ask_deep_panic_salvage")
    if not result:
        return {"available": False}
    summary = result.get("summary", {})
    return {
        "available": True,
        "strategy_id": result.get("strategy_id"),
        "params": result.get("params"),
        "sim_pnl": summary.get("sim_pnl"),
        "delta_vs_actual": summary.get("delta_vs_actual"),
        "delta_vs_no_stop": summary.get("delta_vs_no_stop"),
        "false_exits": summary.get("false_exit_settlement_winners"),
        "missed_true_losers": summary.get("missed_true_losers"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only terminal path edge probes for live_90_70.")
    parser.add_argument("--refresh-cache", action="store_true")
    args = parser.parse_args()

    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    cases = load_cases(refresh_cache=args.refresh_cache)
    strategies = build_strategy_grid()
    results = [run_strategy(cases, strategy) for strategy in strategies]
    best_by_family = select_family_best(results)
    walk = walk_forward_summary(cases, strategies)
    sens = sensitivity(results, best_by_family)
    baselines = {
        "actual": summarize_rows("actual", baseline_rows(cases, "actual")),
        "no_stop": summarize_rows("no_stop_hold_to_settlement", baseline_rows(cases, "no_stop")),
        "stop_70": summarize_rows("first_touch_stop_70", baseline_rows(cases, "stop_70")),
    }

    generated_at = datetime.now(UTC).isoformat()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"codex_terminal_path_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_terminal_path_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_terminal_path_research_latest.json"
    latest_md = EDGE_DIR / "codex_terminal_path_research_latest.md"
    payload = {
        "generated_at": generated_at,
        "dataset": DATASET,
        "case_count": len(cases),
        "baselines": baselines,
        "prior_deep_panic_reference": prior_deep_panic_reference(),
        "best_by_family": best_by_family,
        "walk_forward": walk,
        "sensitivity": sens,
        "truffle_reference": load_truffle_reference(),
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "feature_availability": {
            "terminal_window_salvage": "market close time from ticker plus live held-side ask at decision time",
            "rival_pressure_persistence": "current and prior post-entry own/opposite bids from live quote heartbeats",
            "failed_safety_checkpoint": "own-side bid path up to a fixed post-entry checkpoint",
        },
        "live_logic_changed": False,
    }
    json_text = json.dumps(payload, indent=2, sort_keys=True)
    json_path.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")
    write_markdown_report(md_path, payload)
    write_markdown_report(latest_md, payload)

    ledger_records: list[dict[str, Any]] = []
    for family, result in best_by_family.items():
        holdout_summary = walk["families"][family]["holdout_summary"]
        ledger_records.append(
            {
                "recorded_at": datetime.now(UTC).isoformat(),
                "status": status_for(result, holdout_summary),
                "source": "probe_codex_terminal_path_edges.py",
                "dataset": DATASET,
                "strategy_id": result["strategy_id"],
                "idea_key": idea_key(result["family"], result["equation"], result["params"]),
                "family": result["family"],
                "theorem": result["theorem"],
                "equation": result["equation"],
                "params": result["params"],
                "param_grid_size": len([item for item in results if item["family"] == family]),
                "generated_at": generated_at,
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "summary": result["summary"],
                "holdout_summary": holdout_summary,
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
        f"Cases={len(cases)} actual={baselines['actual']['sim_pnl']} "
        f"no_stop={baselines['no_stop']['sim_pnl']} stop70={baselines['stop_70']['sim_pnl']}"
    )
    for family, result in best_by_family.items():
        summary = result["summary"]
        holdout = walk["families"][family]["holdout_summary"]
        print(
            f"{family} {result['strategy_id']} status={status_for(result, holdout)} "
            f"sim={summary['sim_pnl']} delta_actual={summary['delta_vs_actual']} "
            f"delta_no_stop={summary['delta_vs_no_stop']} exits={summary['exits']} "
            f"false={summary['false_exit_settlement_winners']} missed_losers={summary['missed_true_losers']} "
            f"train_selected_holdout_delta_no_stop={holdout['delta_vs_no_stop']}"
        )


if __name__ == "__main__":
    main()
