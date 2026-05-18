from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_codex_terminal_path_edges import seconds_to_close
from probe_codex_terminal_salvage_all_trades import (
    EDGE_DIR,
    discover_datasets,
    load_dataset_cases,
    run_baseline,
)
from probe_stop_touch_confirmation import (
    append_ledger,
    exit_pnl,
    idea_key,
    load_truffle_reference,
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
    simulator: Callable[
        [dict[str, Any], list[dict[str, Any]], "EmpiricalCalibrator", dict[str, Any]],
        tuple[float, dict[str, Any]],
    ]


def finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def bucket(value: float, cuts: tuple[float, ...]) -> str:
    for cut in cuts:
        if value <= cut:
            return f"<= {cut:g}"
    return f"> {cuts[-1]:g}"


def quote_features(case: dict[str, Any], point: dict[str, Any]) -> dict[str, Any] | None:
    remaining = seconds_to_close(case, point)
    if remaining is None or remaining <= 0 or remaining > 900:
        return None
    own_bid = float(point.get("own_bid", math.nan))
    held_ask = float(point.get("held_ask", math.nan))
    own_ask = float(point.get("own_ask", held_ask))
    opp_bid = float(point.get("opp_bid", math.nan))
    bid_sum = float(point.get("bid_sum", math.nan))
    if not finite(own_bid) or not finite(held_ask):
        return None
    pressure = opp_bid / (own_bid + opp_bid + 1e-9) if finite(opp_bid) else math.nan
    if not finite(own_ask):
        own_ask = held_ask
    quote_mid = max(0.01, min(0.99, ((own_bid + own_ask) / 2.0) / 100.0))
    return {
        "elapsed": float(point["elapsed"]),
        "remaining": float(remaining),
        "own_bid": own_bid,
        "held_ask": held_ask,
        "own_ask": own_ask,
        "opp_bid": opp_bid,
        "bid_sum": bid_sum,
        "pressure": pressure,
        "quote_mid": quote_mid,
        "rem_bucket": bucket(float(remaining), (30, 60, 120, 240, 900)),
        "held_bucket": bucket(held_ask, (10, 20, 35, 50, 65, 80, 90, 101)),
        "pressure_bucket": bucket(pressure if finite(pressure) else 0.5, (0.55, 0.70, 0.85, 0.95, 1.01)),
        "side": str(case.get("side", "")),
    }


def prepared_events(case: dict[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for idx, point in enumerate(case["path"]):
        features = quote_features(case, point)
        if features is None:
            continue
        features["idx"] = idx
        events.append(features)
    return events


def calibration_keys(features: dict[str, Any]) -> list[tuple[Any, ...]]:
    side = features["side"]
    rem = features["rem_bucket"]
    held = features["held_bucket"]
    pressure = features["pressure_bucket"]
    return [
        ("side_rem_held_pressure", side, rem, held, pressure),
        ("side_rem_held", side, rem, held),
        ("rem_held_pressure", rem, held, pressure),
        ("rem_held", rem, held),
        ("side_held", side, held),
        ("held", held),
        ("all",),
    ]


class EmpiricalCalibrator:
    def __init__(self, counts: dict[tuple[Any, ...], dict[str, int]]) -> None:
        self.counts = counts

    @classmethod
    def fit(cls, prepared: list[tuple[dict[str, Any], list[dict[str, Any]]]]) -> "EmpiricalCalibrator":
        counts: dict[tuple[Any, ...], dict[str, int]] = defaultdict(lambda: {"n": 0, "wins": 0})
        for case, events in prepared:
            seen: set[tuple[Any, ...]] = set()
            won = bool(case["settlement_win"])
            for event in events:
                for key in calibration_keys(event):
                    if key in seen:
                        continue
                    seen.add(key)
                    counts[key]["n"] += 1
                    counts[key]["wins"] += int(won)
        return cls(dict(counts))

    def estimate(self, features: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        min_n = int(params["min_bin_n"])
        prior_strength = float(params["prior_strength"])
        use_side = bool(params["use_side"])
        use_pressure = bool(params["use_pressure"])
        side = features["side"]
        rem = features["rem_bucket"]
        held = features["held_bucket"]
        pressure = features["pressure_bucket"]
        candidates: list[tuple[Any, ...]] = []
        if use_side and use_pressure:
            candidates.append(("side_rem_held_pressure", side, rem, held, pressure))
        if use_side:
            candidates.append(("side_rem_held", side, rem, held))
        if use_pressure:
            candidates.append(("rem_held_pressure", rem, held, pressure))
        candidates.extend(
            [
                ("rem_held", rem, held),
                ("side_held", side, held),
                ("held", held),
                ("all",),
            ]
        )
        quote_p = float(features["quote_mid"])
        chosen_key = ("all",)
        chosen = {"n": 0, "wins": 0}
        for key in candidates:
            item = self.counts.get(key)
            if item and item["n"] >= min_n:
                chosen_key = key
                chosen = item
                break
        n = int(chosen["n"])
        wins = int(chosen["wins"])
        p_win = (wins + prior_strength * quote_p) / (n + prior_strength) if n + prior_strength > 0 else quote_p
        return {
            "p_win": max(0.001, min(0.999, p_win)),
            "n": n,
            "wins": wins,
            "key": chosen_key,
            "quote_p": quote_p,
        }


def terminal_pnls(case: dict[str, Any]) -> tuple[float, float]:
    qty = int(case["qty"])
    entry = float(case["entry"])
    entry_fee = float(case.get("entry_fee_cents", 0.0) or 0.0)
    win_pnl = round((qty * (100.0 - entry) - entry_fee) / 100.0, 4)
    loss_pnl = round(-(qty * entry + entry_fee) / 100.0, 4)
    return win_pnl, loss_pnl


def row_for(case: dict[str, Any], pnl: float, meta: dict[str, Any], label: str) -> dict[str, Any]:
    exit_bid = meta.get("exit_bid")
    return {
        "label": label,
        "dataset": case.get("dataset", "unknown"),
        "market": case["market"],
        "side": case.get("side"),
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


def summarize_by_side(label: str, rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        side: summarize_label(label, [row for row in rows if row["side"] == side])
        for side in sorted({str(row["side"]) for row in rows})
    }


def eligible_events(events: list[dict[str, Any]], params: dict[str, Any]) -> list[dict[str, Any]]:
    min_elapsed = float(params["min_elapsed_seconds"])
    max_remaining = float(params["max_remaining_seconds"])
    return [
        event
        for event in events
        if event["elapsed"] >= min_elapsed and event["remaining"] <= max_remaining
    ]


def sim_calibrated_break_even_ev(
    case: dict[str, Any],
    events: list[dict[str, Any]],
    calibrator: EmpiricalCalibrator,
    params: dict[str, Any],
) -> tuple[float, dict[str, Any]]:
    min_probability_edge = float(params["min_probability_edge"])
    min_ev_dollars = float(params["min_ev_dollars"])
    win_pnl, loss_pnl = terminal_pnls(case)
    denom = max(1e-9, win_pnl - loss_pnl)
    for event in eligible_events(events, params):
        bid = float(event["own_bid"])
        sale_pnl = exit_pnl(case, bid)
        p_break_even = max(0.0, min(1.0, (sale_pnl - loss_pnl) / denom))
        estimate = calibrator.estimate(event, params)
        p_win = float(estimate["p_win"])
        expected_hold = p_win * win_pnl + (1.0 - p_win) * loss_pnl
        ev_gap = sale_pnl - expected_hold
        probability_gap = p_break_even - p_win
        if probability_gap >= min_probability_edge and ev_gap >= min_ev_dollars:
            return sale_pnl, {
                "exit": True,
                "exit_bid": bid,
                "exit_elapsed": event["elapsed"],
                "p_win": round(p_win, 4),
                "p_break_even": round(p_break_even, 4),
                "ev_gap": round(ev_gap, 4),
                "calibration_n": estimate["n"],
                "calibration_key": list(estimate["key"]),
                "remaining": round(event["remaining"], 3),
            }
    return float(case["hold_pnl"]), {"exit": False}


def sim_calibrated_log_utility(
    case: dict[str, Any],
    events: list[dict[str, Any]],
    calibrator: EmpiricalCalibrator,
    params: dict[str, Any],
) -> tuple[float, dict[str, Any]]:
    bankroll = float(params["bankroll_dollars"])
    min_utility_gap = float(params["min_utility_gap"])
    win_pnl, loss_pnl = terminal_pnls(case)
    for event in eligible_events(events, params):
        bid = float(event["own_bid"])
        sale_pnl = exit_pnl(case, bid)
        if bankroll + loss_pnl <= 0 or bankroll + sale_pnl <= 0:
            continue
        estimate = calibrator.estimate(event, params)
        p_win = float(estimate["p_win"])
        hold_utility = p_win * math.log(bankroll + win_pnl) + (1.0 - p_win) * math.log(bankroll + loss_pnl)
        sale_utility = math.log(bankroll + sale_pnl)
        utility_gap = sale_utility - hold_utility
        if utility_gap >= min_utility_gap:
            return sale_pnl, {
                "exit": True,
                "exit_bid": bid,
                "exit_elapsed": event["elapsed"],
                "p_win": round(p_win, 4),
                "utility_gap": round(utility_gap, 8),
                "calibration_n": estimate["n"],
                "calibration_key": list(estimate["key"]),
                "remaining": round(event["remaining"], 3),
            }
    return float(case["hold_pnl"]), {"exit": False}


def sim_empirical_survival_hazard(
    case: dict[str, Any],
    events: list[dict[str, Any]],
    calibrator: EmpiricalCalibrator,
    params: dict[str, Any],
) -> tuple[float, dict[str, Any]]:
    min_loss_hazard = float(params["min_loss_hazard"])
    held_ask_max = float(params["held_ask_max"])
    for event in eligible_events(events, params):
        if float(event["held_ask"]) > held_ask_max:
            continue
        estimate = calibrator.estimate(event, params)
        p_win = float(estimate["p_win"])
        remaining_minutes = max(float(event["remaining"]) / 60.0, 1.0 / 60.0)
        loss_hazard = -math.log(max(p_win, 0.001)) / math.sqrt(remaining_minutes)
        if loss_hazard >= min_loss_hazard:
            bid = float(event["own_bid"])
            return exit_pnl(case, bid), {
                "exit": True,
                "exit_bid": bid,
                "exit_elapsed": event["elapsed"],
                "p_win": round(p_win, 4),
                "loss_hazard": round(loss_hazard, 6),
                "calibration_n": estimate["n"],
                "calibration_key": list(estimate["key"]),
                "remaining": round(event["remaining"], 3),
                "held_ask": round(float(event["held_ask"]), 4),
            }
    return float(case["hold_pnl"]), {"exit": False}


def calibration_param_grid() -> list[dict[str, Any]]:
    params: list[dict[str, Any]] = []
    for min_elapsed_seconds in (30, 60):
        for max_remaining_seconds in (90, 240, 900):
            for min_bin_n in (3, 8):
                for use_side in (False, True):
                    for use_pressure in (False, True):
                        params.append(
                            {
                                "min_elapsed_seconds": min_elapsed_seconds,
                                "max_remaining_seconds": max_remaining_seconds,
                                "min_bin_n": min_bin_n,
                                "prior_strength": 5,
                                "use_side": use_side,
                                "use_pressure": use_pressure,
                            }
                        )
    return params


def build_strategy_grid() -> list[StrategySpec]:
    strategies: list[StrategySpec] = []
    base_grid = calibration_param_grid()

    def add(
        family: str,
        theorem: str,
        equation: str,
        params: dict[str, Any],
        simulator: Callable[
            [dict[str, Any], list[dict[str, Any]], EmpiricalCalibrator, dict[str, Any]],
            tuple[float, dict[str, Any]],
        ],
    ) -> None:
        strategies.append(StrategySpec(family, theorem, equation, params, simulator))

    for base in base_grid:
        for min_probability_edge in (0.0, 0.03, 0.06):
            for min_ev_dollars in (0.0, 0.05):
                params = {**base, "min_probability_edge": min_probability_edge, "min_ev_dollars": min_ev_dollars}
                add(
                    "calibrated_break_even_ev",
                    "A held position should be sold when empirical state-calibrated win probability is below the fee-adjusted probability needed to prefer holding over selling now.",
                    "p_be=(exit_pnl-loss_pnl)/(win_pnl-loss_pnl); exit when p_calibrated + M <= p_be and exit_pnl - E[hold_pnl|p_calibrated] >= G.",
                    params,
                    sim_calibrated_break_even_ev,
                )

    for base in base_grid:
        for bankroll_dollars in (500, 2000):
            for min_utility_gap in (0.0, 0.00002):
                params = {**base, "bankroll_dollars": bankroll_dollars, "min_utility_gap": min_utility_gap}
                add(
                    "calibrated_log_utility_exit",
                    "Risk-adjusted utility can justify selling before raw expected value is decisively negative when terminal loss utility dominates small settlement upside.",
                    "Exit when log(W+exit_pnl) - [p_calibrated*log(W+win_pnl)+(1-p_calibrated)*log(W+loss_pnl)] >= U.",
                    params,
                    sim_calibrated_log_utility,
                )

    for base in base_grid:
        for held_ask_max in (50, 80, 100):
            for min_loss_hazard in (0.05, 0.10, 0.20):
                params = {**base, "held_ask_max": held_ask_max, "min_loss_hazard": min_loss_hazard}
                add(
                    "empirical_survival_loss_hazard",
                    "A low calibrated survival probability is more urgent when little clock remains, so loss risk should be normalized as a survival hazard rather than a raw threshold.",
                    "h=-ln(p_calibrated_win)/sqrt(seconds_to_close/60); exit when h >= H and held_ask <= A.",
                    params,
                    sim_empirical_survival_hazard,
                )
    return strategies


def run_strategy(
    prepared: list[tuple[dict[str, Any], list[dict[str, Any]]]],
    calibrator: EmpiricalCalibrator,
    strategy: StrategySpec,
) -> dict[str, Any]:
    sid = strategy_id(strategy.family, strategy.params)
    rows = [
        row_for(case, *strategy.simulator(case, events, calibrator, strategy.params), sid)
        for case, events in prepared
    ]
    return {
        "strategy_id": sid,
        "family": strategy.family,
        "theorem": strategy.theorem,
        "equation": strategy.equation,
        "params": strategy.params,
        "summary": summarize_label(sid, rows),
        "by_dataset": summarize_by_dataset(sid, rows),
        "by_side": summarize_by_side(sid, rows),
        "interesting_examples": sorted(
            rows,
            key=lambda row: (float(row["sim_pnl"]) - float(row["hold_pnl"]), -float(row["max_drawdown"])),
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


def walk_forward_summary(
    train_prepared: list[tuple[dict[str, Any], list[dict[str, Any]]]],
    holdout_prepared: list[tuple[dict[str, Any], list[dict[str, Any]]]],
    full_prepared: list[tuple[dict[str, Any], list[dict[str, Any]]]],
    calibrator: EmpiricalCalibrator,
    strategies: list[StrategySpec],
) -> dict[str, Any]:
    by_family: dict[str, list[StrategySpec]] = {}
    for strategy in strategies:
        by_family.setdefault(strategy.family, []).append(strategy)
    output: dict[str, Any] = {
        "train_n": len(train_prepared),
        "holdout_n": len(holdout_prepared),
        "split_entry_ts": holdout_prepared[0][0]["entry_ts"] if holdout_prepared else None,
        "calibration_note": "The calibrator is fitted on the chronological 70% training split; holdout summaries are out-of-sample for calibration and parameter selection.",
        "families": {},
    }
    for family, items in by_family.items():
        train_results = [run_strategy(train_prepared, calibrator, strategy) for strategy in items]
        selected = max(train_results, key=lambda result: result["summary"]["sim_pnl"])
        selected_spec = next(
            strategy for strategy in items if strategy_id(strategy.family, strategy.params) == selected["strategy_id"]
        )
        output["families"][family] = {
            "selected_strategy_id": selected["strategy_id"],
            "selected_params": selected["params"],
            "train_summary": selected["summary"],
            "holdout_summary": run_strategy(holdout_prepared, calibrator, selected_spec)["summary"],
            "full_selected_summary": run_strategy(full_prepared, calibrator, selected_spec)["summary"],
        }
    return output


def status_for(result: dict[str, Any], holdout_summary: dict[str, Any]) -> str:
    summary = result["summary"]
    if (
        summary["delta_vs_actual"] > 0
        and summary["delta_vs_no_stop"] > 0
        and holdout_summary["delta_vs_no_stop"] > 0
    ):
        if summary["false_exit_rate"] <= 0.05 and summary["missed_true_loser_rate"] <= 0.25:
            return "candidate_for_human_review"
        return "watchlist_positive_but_noisy"
    if summary["delta_vs_no_stop"] > 0 and holdout_summary["delta_vs_no_stop"] > 0:
        return "watchlist_no_stop_positive_but_worse_than_actual"
    return "tested_not_robust"


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    actual = payload["baselines"]["actual"]["summary"]
    no_stop = payload["baselines"]["no_stop"]["summary"]
    stop70 = payload["baselines"]["held_ask_stop_70"]["summary"]
    lines = [
        "# Codex Calibrated Utility Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Cases: `{payload['case_count']}`",
        f"- Calibration train / holdout: `{payload['walk_forward']['train_n']} / {payload['walk_forward']['holdout_n']}`",
        f"- Actual recorded PnL: `${actual['sim_pnl']}`",
        f"- No-stop hold-to-settlement PnL: `${no_stop['sim_pnl']}`",
        f"- First held-ask <=70 baseline PnL: `${stop70['sim_pnl']}`",
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
            "## Side Check",
            "",
            "| Family | YES PnL | NO PnL | YES false/missed | NO false/missed |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for family, result in payload["best_by_family"].items():
        by_side = result.get("by_side", {})
        yes = by_side.get("yes", {})
        no = by_side.get("no", {})
        lines.append(
            f"| `{family}` | {yes.get('sim_pnl')} | {no.get('sim_pnl')} | "
            f"{yes.get('false_exit_settlement_winners')}/{yes.get('missed_true_losers')} | "
            f"{no.get('false_exit_settlement_winners')}/{no.get('missed_true_losers')} |"
        )
    lines.extend(
        [
            "",
            "## Truffle Reference",
            "",
            f"- Current reference: `{json.dumps(payload['truffle_reference'], sort_keys=True)}`",
            "- This is reference-only because the available Truffle-supervised output is a delayed stop-slice policy eval on `live_90_70`, not this all-trade calibrated full replay.",
        ]
    )
    lines.extend(
        [
            "",
            "## Audit Notes",
            "",
            "- The empirical calibrator is fitted only on the chronological 70% training split; holdout rows are out-of-sample for calibration and parameter selection.",
            "- Features are current quote fields available at decision time: own bid/ask, held-side ask, opponent bid pressure, side, elapsed time, and ticker-derived seconds to close.",
            "- These are distinct from prior terminal confirmation rules: they use calibrated probability, fee-adjusted break-even probability, log utility, or survival hazard instead of raw terminal quote thresholds.",
            "- This run is research-only and does not modify live entry logic, live exit logic, production config, run scripts, or bot processes.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only calibrated probability and utility probes.")
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
    prepared = [(case, prepared_events(case)) for case in cases]
    prepared = [(case, events) for case, events in prepared if events]
    split = int(len(prepared) * 0.7)
    train_prepared = prepared[:split]
    holdout_prepared = prepared[split:]
    calibrator = EmpiricalCalibrator.fit(train_prepared)
    strategies = build_strategy_grid()
    results = [run_strategy(prepared, calibrator, strategy) for strategy in strategies]
    best_by_family = select_family_best(results)
    walk = walk_forward_summary(train_prepared, holdout_prepared, prepared, calibrator, strategies)
    sens = sensitivity(results, best_by_family)
    all_cases = [case for case, _events in prepared]
    baselines = {
        "actual": run_baseline(all_cases, "actual"),
        "no_stop": run_baseline(all_cases, "no_stop"),
        "held_ask_stop_70": run_baseline(all_cases, "held_ask_stop_70"),
    }

    generated_at = datetime.now(UTC).isoformat()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"codex_calibrated_utility_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_calibrated_utility_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_calibrated_utility_research_latest.json"
    latest_md = EDGE_DIR / "codex_calibrated_utility_research_latest.md"
    payload = {
        "generated_at": generated_at,
        "dataset": "all_quote_path_trades",
        "datasets": sorted({str(case.get("dataset")) for case in all_cases}),
        "requested_datasets": datasets,
        "case_count": len(all_cases),
        "calibration_bin_count": len(calibrator.counts),
        "baselines": baselines,
        "best_by_family": best_by_family,
        "walk_forward": walk,
        "sensitivity": sens,
        "truffle_reference": load_truffle_reference(),
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "feature_availability": {
            "calibrated_break_even_ev": "current quote state calibrated on prior training trades plus entry/fee/quantity-specific terminal payoff",
            "calibrated_log_utility_exit": "same state calibration with bankroll-normalized log utility at the decision point",
            "empirical_survival_loss_hazard": "same state calibration converted into a time-normalized survival hazard using seconds to close",
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
                "source": "probe_codex_calibrated_utility_edges.py",
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
        f"Cases={len(all_cases)} datasets={','.join(payload['datasets'])} "
        f"actual={baselines['actual']['summary']['sim_pnl']} no_stop={baselines['no_stop']['summary']['sim_pnl']} "
        f"stop70={baselines['held_ask_stop_70']['summary']['sim_pnl']} calibration_bins={len(calibrator.counts)}"
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
