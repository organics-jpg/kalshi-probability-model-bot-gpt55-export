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
    EDGE_DIR,
    DEFAULT_PARAMS as TERMINAL_BASELINE_PARAMS,
    discover_datasets,
    load_dataset_cases,
    run_baseline,
    run_terminal,
)
from probe_codex_terminal_path_edges import sim_terminal_window_salvage
from probe_stop_touch_confirmation import (
    append_ledger,
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
    simulator: Callable[[dict[str, Any], list[dict[str, Any]], dict[str, Any]], tuple[float, dict[str, Any]]]


def case_entry_dt(case: dict[str, Any]) -> datetime:
    return datetime.fromisoformat(str(case["entry_ts"]))


def seconds_to_close(case: dict[str, Any], point: dict[str, Any]) -> float | None:
    close_dt = parse_market_close_from_ticker(str(case.get("market") or ""))
    if close_dt is None:
        return None
    now_dt = case_entry_dt(case) + timedelta(seconds=float(point["elapsed"]))
    return float((close_dt - now_dt).total_seconds())


def trailing_points(case: dict[str, Any], idx: int, lookback_seconds: float) -> list[dict[str, Any]]:
    now_elapsed = float(case["path"][idx]["elapsed"])
    lower = now_elapsed - lookback_seconds
    return [point for point in case["path"][: idx + 1] if float(point["elapsed"]) >= lower]


def prepared_events(case: dict[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for idx, point in enumerate(case["path"]):
        remaining = seconds_to_close(case, point)
        if remaining is None or remaining < 1 or remaining > 150:
            continue
        own_bid = float(point["own_bid"])
        opp_bid = float(point["opp_bid"])
        held_ask = float(point["held_ask"])
        bid_sum = float(point["bid_sum"])
        lookbacks: dict[int, dict[str, float]] = {}
        for lookback in (15, 30, 60):
            points = trailing_points(case, idx, float(lookback))
            held_asks = [float(item["held_ask"]) for item in points]
            if len(points) >= 2:
                span = max(1.0, float(points[-1]["elapsed"]) - float(points[0]["elapsed"]))
                slope = (held_ask - float(points[0]["held_ask"])) / span
            else:
                slope = math.nan
            lookbacks[lookback] = {
                "n": float(len(points)),
                "drop_from_recent_high": max(held_asks) - held_ask if held_asks else math.nan,
                "slope_per_second": slope,
            }
        events.append(
            {
                "idx": idx,
                "remaining": remaining,
                "own_bid": own_bid,
                "opp_bid": opp_bid,
                "held_ask": held_ask,
                "bid_sum": bid_sum,
                "pressure": opp_bid / (own_bid + opp_bid + 1e-9),
                "lookbacks": lookbacks,
            }
        )
    return events


def sim_terminal_baseline(case: dict[str, Any], events: list[dict[str, Any]], params: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    del events
    return sim_terminal_window_salvage(case, params)


def sim_terminal_breakdown_confirmation(
    case: dict[str, Any], events: list[dict[str, Any]], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    held_ask_max = float(params["held_ask_max"])
    final_window = float(params["final_window_seconds"])
    min_remaining = float(params["min_remaining_seconds"])
    lookback = int(params["lookback_seconds"])
    min_drop = float(params["min_recent_drop"])
    for event in events:
        if event["remaining"] < min_remaining or event["remaining"] > final_window:
            continue
        if event["held_ask"] > held_ask_max:
            continue
        look = event["lookbacks"][lookback]
        if look["n"] < 2 or look["drop_from_recent_high"] < min_drop:
            continue
        return exit_pnl(case, event["own_bid"]), {
            "exit": True,
            "exit_bid": event["own_bid"],
            "exit_elapsed": float(case["path"][event["idx"]]["elapsed"]),
            "held_ask": event["held_ask"],
            "seconds_to_close": round(event["remaining"], 3),
            "recent_drop": round(look["drop_from_recent_high"], 4),
        }
    return float(case["hold_pnl"]), {"exit": False}


def sim_terminal_pressure_floor(
    case: dict[str, Any], events: list[dict[str, Any]], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    held_ask_max = float(params["held_ask_max"])
    final_window = float(params["final_window_seconds"])
    min_remaining = float(params["min_remaining_seconds"])
    min_bid_sum = float(params["min_bid_sum"])
    pressure_min = float(params["pressure_min"])
    for event in events:
        if event["remaining"] < min_remaining or event["remaining"] > final_window:
            continue
        if event["held_ask"] > held_ask_max:
            continue
        if event["bid_sum"] < min_bid_sum or event["pressure"] < pressure_min:
            continue
        return exit_pnl(case, event["own_bid"]), {
            "exit": True,
            "exit_bid": event["own_bid"],
            "exit_elapsed": float(case["path"][event["idx"]]["elapsed"]),
            "held_ask": event["held_ask"],
            "seconds_to_close": round(event["remaining"], 3),
            "pressure": round(event["pressure"], 4),
            "bid_sum": round(event["bid_sum"], 4),
        }
    return float(case["hold_pnl"]), {"exit": False}


def sim_terminal_decay_projection(
    case: dict[str, Any], events: list[dict[str, Any]], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    held_ask_ceiling = float(params["held_ask_ceiling"])
    final_window = float(params["final_window_seconds"])
    min_remaining = float(params["min_remaining_seconds"])
    lookback = int(params["lookback_seconds"])
    projected_ask_max = float(params["projected_ask_max"])
    max_slope_per_second = float(params["max_slope_per_second"])
    for event in events:
        if event["remaining"] < min_remaining or event["remaining"] > final_window:
            continue
        if event["held_ask"] > held_ask_ceiling:
            continue
        look = event["lookbacks"][lookback]
        slope = float(look["slope_per_second"])
        if math.isnan(slope) or slope > max_slope_per_second:
            continue
        projected = event["held_ask"] + slope * event["remaining"]
        if projected > projected_ask_max:
            continue
        return exit_pnl(case, event["own_bid"]), {
            "exit": True,
            "exit_bid": event["own_bid"],
            "exit_elapsed": float(case["path"][event["idx"]]["elapsed"]),
            "held_ask": event["held_ask"],
            "seconds_to_close": round(event["remaining"], 3),
            "slope_per_second": round(slope, 6),
            "projected_ask_at_close": round(projected, 4),
        }
    return float(case["hold_pnl"]), {"exit": False}


def build_strategy_grid() -> list[StrategySpec]:
    strategies: list[StrategySpec] = []

    def add(
        family: str,
        theorem: str,
        equation: str,
        params: dict[str, Any],
        simulator: Callable[[dict[str, Any], list[dict[str, Any]], dict[str, Any]], tuple[float, dict[str, Any]]],
    ) -> None:
        strategies.append(StrategySpec(family, theorem, equation, params, simulator))

    for held_ask_max in (40, 45, 50, 55):
        for final_window_seconds in (45, 60, 75):
            for min_remaining_seconds in (10, 15, 20):
                for lookback_seconds in (15, 30, 60):
                    for min_recent_drop in (1, 2, 4, 6, 8):
                        add(
                            "terminal_breakdown_confirmation",
                            "A terminal low held-side ask is more reliable when it is part of a recent downward repricing, not a stale low print.",
                            "Exit when m <= seconds_to_close <= W, held_ask <= H, and max(held_ask over trailing L seconds)-held_ask >= D.",
                            {
                                "held_ask_max": held_ask_max,
                                "final_window_seconds": final_window_seconds,
                                "min_remaining_seconds": min_remaining_seconds,
                                "lookback_seconds": lookback_seconds,
                                "min_recent_drop": min_recent_drop,
                            },
                            sim_terminal_breakdown_confirmation,
                        )

    for held_ask_max in (40, 45, 50, 55):
        for final_window_seconds in (45, 60, 75):
            for min_remaining_seconds in (10, 15, 20):
                for min_bid_sum in (94, 96, 98):
                    for pressure_min in (0.85, 0.90, 0.93, 0.95):
                        add(
                            "terminal_pressure_floor",
                            "A low terminal held-side ask should be confirmed by opponent-side bid pressure and an intact two-sided book.",
                            "Exit when m <= seconds_to_close <= W, held_ask <= H, bid_sum >= B, and opp_bid/(own_bid+opp_bid) >= P.",
                            {
                                "held_ask_max": held_ask_max,
                                "final_window_seconds": final_window_seconds,
                                "min_remaining_seconds": min_remaining_seconds,
                                "min_bid_sum": min_bid_sum,
                                "pressure_min": pressure_min,
                            },
                            sim_terminal_pressure_floor,
                        )

    for held_ask_ceiling in (45, 50, 55):
        for final_window_seconds in (45, 60, 75):
            for min_remaining_seconds in (10, 15, 20):
                for lookback_seconds in (15, 30, 60):
                    for projected_ask_max in (5, 10, 15, 20):
                        for max_slope_per_second in (-0.05, -0.02, 0.0):
                            add(
                                "terminal_decay_projection",
                                "A terminal quote is more trustworthy when its recent held-ask slope projects to a low ask by close.",
                                "Let slope=(held_ask_t-held_ask_{t-L})/dt and projected=held_ask_t+slope*seconds_to_close; exit when projected <= T and slope <= S.",
                                {
                                    "held_ask_ceiling": held_ask_ceiling,
                                    "final_window_seconds": final_window_seconds,
                                    "min_remaining_seconds": min_remaining_seconds,
                                    "lookback_seconds": lookback_seconds,
                                    "projected_ask_max": projected_ask_max,
                                    "max_slope_per_second": max_slope_per_second,
                                },
                                sim_terminal_decay_projection,
                            )
    return strategies


def row_for(case: dict[str, Any], pnl: float, meta: dict[str, Any], label: str) -> dict[str, Any]:
    exit_bid = meta.get("exit_bid")
    return {
        "label": label,
        "dataset": case.get("dataset", "live_90_70"),
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


def run_strategy(prepped: list[tuple[dict[str, Any], list[dict[str, Any]]]], strategy: StrategySpec) -> dict[str, Any]:
    sid = strategy_id(strategy.family, strategy.params)
    rows = [row_for(case, *strategy.simulator(case, events, strategy.params), sid) for case, events in prepped]
    return {
        "strategy_id": sid,
        "family": strategy.family,
        "theorem": strategy.theorem,
        "equation": strategy.equation,
        "params": strategy.params,
        "summary": summarize_label(sid, rows),
        "by_dataset": summarize_by_dataset(sid, rows),
        "interesting_examples": sorted(
            rows,
            key=lambda row: (float(row["sim_pnl"]) - float(row["hold_pnl"]), -float(row["max_drawdown"])),
            reverse=True,
        )[:10],
    }


def run_on_cases(cases: list[dict[str, Any]], strategy: StrategySpec) -> dict[str, Any]:
    return run_strategy([(case, prepared_events(case)) for case in cases], strategy)


def select_family_best(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for result in results:
        family = result["family"]
        if family not in best or result["summary"]["sim_pnl"] > best[family]["summary"]["sim_pnl"]:
            best[family] = result
    return best


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
                "false_exit_rate": result["summary"]["false_exit_rate"],
                "missed_true_loser_rate": result["summary"]["missed_true_loser_rate"],
            }
            for result in ranked[:12]
        ]
    return output


def walk_forward_summary(cases: list[dict[str, Any]], strategies: list[StrategySpec]) -> dict[str, Any]:
    ordered = sorted(cases, key=lambda case: case["entry_ts"])
    split = int(len(ordered) * 0.7)
    train = ordered[:split]
    holdout = ordered[split:]
    train_prepped = [(case, prepared_events(case)) for case in train]
    holdout_prepped = [(case, prepared_events(case)) for case in holdout]
    full_prepped = [(case, prepared_events(case)) for case in ordered]
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
        train_results = [run_strategy(train_prepped, strategy) for strategy in items]
        selected = max(train_results, key=lambda result: result["summary"]["sim_pnl"])
        selected_spec = next(
            strategy for strategy in items if strategy_id(strategy.family, strategy.params) == selected["strategy_id"]
        )
        output["families"][family] = {
            "selected_strategy_id": selected["strategy_id"],
            "selected_params": selected["params"],
            "train_summary": selected["summary"],
            "holdout_summary": run_strategy(holdout_prepped, selected_spec)["summary"],
            "full_selected_summary": run_strategy(full_prepped, selected_spec)["summary"],
        }
    return output


def status_for(result: dict[str, Any], holdout_summary: dict[str, Any]) -> str:
    summary = result["summary"]
    if (
        summary["delta_vs_actual"] > 0
        and summary["delta_vs_no_stop"] > 0
        and holdout_summary["delta_vs_no_stop"] > 0
    ):
        if summary["false_exit_rate"] <= 0.01 and summary["missed_true_loser_rate"] <= 0.15:
            return "candidate_for_human_review"
        return "watchlist_positive_but_noisy"
    if summary["delta_vs_no_stop"] > 0 and holdout_summary["delta_vs_no_stop"] > 0:
        return "watchlist_no_stop_positive_but_worse_than_actual"
    return "tested_not_robust"


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    actual = payload["baselines"]["actual"]["summary"]
    no_stop = payload["baselines"]["no_stop"]["summary"]
    stop70 = payload["baselines"]["held_ask_stop_70"]["summary"]
    terminal = payload["terminal_window_baseline"]["summary"]
    lines = [
        "# Codex Terminal Confirmation Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Cases: `{payload['case_count']}`",
        f"- Actual recorded PnL: `${actual['sim_pnl']}`",
        f"- No-stop hold-to-settlement PnL: `${no_stop['sim_pnl']}`",
        f"- First held-ask <=70 baseline PnL: `${stop70['sim_pnl']}`",
        f"- Prior terminal-window salvage baseline PnL: `${terminal['sim_pnl']}`",
        "",
        "## New Hypotheses Tested",
    ]
    for family, result in payload["best_by_family"].items():
        summary = result["summary"]
        walk_family = payload["walk_forward"]["families"][family]
        holdout = walk_family["holdout_summary"]
        status = status_for(result, holdout)
        lines.extend(
            [
                "",
                f"### {family} `{result['strategy_id']}`",
                "",
                f"- Status: {status}",
                f"- Theorem: {result['theorem']}",
                f"- Equation: `{result['equation']}`",
                f"- Full-sample best params: `{json.dumps(result['params'], sort_keys=True)}`",
                f"- Full-sample sim PnL: `${summary['sim_pnl']}`",
                f"- Delta vs actual: `${summary['delta_vs_actual']}`",
                f"- Delta vs no-stop hold: `${summary['delta_vs_no_stop']}`",
                f"- Exits / false exits / missed true losers: `{summary['exits']} / {summary['false_exit_settlement_winners']} / {summary['missed_true_losers']}`",
                f"- False-exit rate / missed-loser rate: `{summary['false_exit_rate']} / {summary['missed_true_loser_rate']}`",
                f"- Train-selected params: `{json.dumps(walk_family['selected_params'], sort_keys=True)}`",
                f"- Train-selected holdout sim PnL: `${holdout['sim_pnl']}`",
                f"- Train-selected holdout delta vs no-stop: `${holdout['delta_vs_no_stop']}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Live 90/70 Reference",
            "",
            "| Family | PnL | Delta vs actual | Delta vs no-stop | Exits | False | Missed losers |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for family, result in payload["live_90_70_best_by_family"].items():
        summary = result["summary"]
        lines.append(
            f"| `{family}` | {summary['sim_pnl']} | {summary['delta_vs_actual']} | {summary['delta_vs_no_stop']} | "
            f"{summary['exits']} | {summary['false_exit_settlement_winners']} | {summary['missed_true_losers']} |"
        )
    lines.extend(
        [
            "",
            "## Audit Notes",
            "",
            "- This is a distinct follow-up to terminal-window salvage: each rule requires breakdown, pressure, or slope confirmation beyond time-to-close plus low ask.",
            "- `seconds_to_close` is derived from the market ticker close time and the live heartbeat timestamp.",
            "- Features are post-entry quote fields available at decision time: own bid, opposite bid, held-side ask, bid sum, and elapsed time.",
            "- This run is research-only and does not modify live entry logic, live exit logic, production config, run scripts, or bot processes.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only terminal confirmation probes for Kalshi BTC 15m exits.")
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
    live_cases = [case for case in cases if case.get("dataset") == "live_90_70"]

    prepped = [(case, prepared_events(case)) for case in cases]
    live_prepped = [(case, prepared_events(case)) for case in live_cases]
    strategies = build_strategy_grid()
    results = [run_strategy(prepped, strategy) for strategy in strategies]
    live_results = [run_strategy(live_prepped, strategy) for strategy in strategies] if live_prepped else []
    best_by_family = select_family_best(results)
    live_best_by_family = select_family_best(live_results) if live_results else {}
    walk = walk_forward_summary(cases, strategies)
    sens = sensitivity(results, best_by_family)

    baselines = {
        "actual": run_baseline(cases, "actual"),
        "no_stop": run_baseline(cases, "no_stop"),
        "held_ask_stop_70": run_baseline(cases, "held_ask_stop_70"),
    }
    terminal_window_baseline = run_terminal(cases, dict(TERMINAL_BASELINE_PARAMS), "terminal_window_salvage_fixed")

    generated_at = datetime.now(UTC).isoformat()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"codex_terminal_confirmation_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_terminal_confirmation_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_terminal_confirmation_research_latest.json"
    latest_md = EDGE_DIR / "codex_terminal_confirmation_research_latest.md"
    payload = {
        "generated_at": generated_at,
        "dataset": "all_quote_path_trades",
        "datasets": sorted({str(case.get("dataset")) for case in cases}),
        "requested_datasets": datasets,
        "case_count": len(cases),
        "live_90_70_case_count": len(live_cases),
        "baselines": baselines,
        "terminal_window_baseline": terminal_window_baseline,
        "best_by_family": best_by_family,
        "live_90_70_best_by_family": live_best_by_family,
        "walk_forward": walk,
        "sensitivity": sens,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "feature_availability": {
            "terminal_breakdown_confirmation": "held-side ask path over trailing seconds plus close time and current own bid",
            "terminal_pressure_floor": "current own bid, opponent bid, bid sum, held-side ask, and close time",
            "terminal_decay_projection": "trailing held-side ask slope, current held-side ask, close time, and current own bid",
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
        holdout = walk["families"][family]["holdout_summary"]
        ledger_records.append(
            {
                "recorded_at": datetime.now(UTC).isoformat(),
                "status": status_for(result, holdout),
                "source": "probe_codex_terminal_confirmation_edges.py",
                "dataset": "all_quote_path_trades",
                "datasets": payload["datasets"],
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
                "holdout_summary": holdout,
                "live_90_70_summary": live_best_by_family.get(family, {}).get("summary"),
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
        f"terminal_fixed={terminal_window_baseline['summary']['sim_pnl']}"
    )
    for family, result in best_by_family.items():
        summary = result["summary"]
        holdout = walk["families"][family]["holdout_summary"]
        print(
            f"{family} {result['strategy_id']} status={status_for(result, holdout)} "
            f"sim={summary['sim_pnl']} delta_actual={summary['delta_vs_actual']} "
            f"delta_no_stop={summary['delta_vs_no_stop']} exits={summary['exits']} "
            f"false={summary['false_exit_settlement_winners']} missed_losers={summary['missed_true_losers']} "
            f"holdout_delta_no_stop={holdout['delta_vs_no_stop']}"
        )


if __name__ == "__main__":
    main()
