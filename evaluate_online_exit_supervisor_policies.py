from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from analyze_post_entry_exit_rules import build_exit_frame

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "online_exit_supervisor_policy_eval_latest.json"

MONTHS = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12,
}


def market_sort_key(market: str) -> tuple[int, int, int, int, int, str]:
    match = re.search(r"-(\d{2})([A-Z]{3})(\d{2})(\d{2})(\d{2})-", str(market or ""))
    if not match:
        return (9999, 12, 31, 23, 59, str(market or ""))
    yy, mon, dd, hh, mm = match.groups()
    return (
        2000 + int(yy),
        int(MONTHS.get(mon, 12)),
        int(dd),
        int(hh),
        int(mm),
        str(market or ""),
    )


def day_label(market: str) -> str:
    match = re.search(r"(\d{2}[A-Z]{3}\d{2})", str(market or ""))
    return match.group(1) if match else "unknown"


def rule_mask(frame: pd.DataFrame, rule: str) -> pd.Series:
    if rule == "last60_down_macd_neutral":
        return (frame["last60_move_state"] == "down") & (frame["btc_macd_state"] == "neutral")
    if rule == "side_no_macd_neutral":
        return (frame["side"] == "NO") & (frame["btc_macd_state"] == "neutral")
    if rule == "side_no_rsi_neutral":
        return (frame["side"] == "NO") & (frame["btc_rsi14_state"] == "neutral")
    if rule == "broad_no_neutral_neutral":
        return (frame["side"] == "NO") & (frame["btc_rsi14_state"] == "neutral") & (frame["btc_macd_state"] == "neutral")
    if rule == "broad_no_neutral_neutral_macd_flat":
        return (
            (frame["side"] == "NO")
            & (frame["btc_rsi14_state"] == "neutral")
            & (frame["btc_macd_state"] == "neutral")
            & (frame["btc_macd_hist_state"] == "flat")
        )
    if rule == "last60_down_macd_hist_flat":
        return (frame["last60_move_state"] == "down") & (frame["btc_macd_hist_state"] == "flat")
    if rule == "rsi_neutral_macd_hist_flat":
        return (frame["btc_rsi14_state"] == "neutral") & (frame["btc_macd_hist_state"] == "flat")
    if rule == "damage_heavy_macd_hist_flat":
        return (frame["damage_state"] == "heavy") & (frame["btc_macd_hist_state"] == "flat")
    raise ValueError(f"Unknown rule: {rule}")


def trailing_sum(values: list[float], count: int) -> float:
    if count <= 0:
        return 0.0
    return float(sum(values[-count:]))


def trailing_positive_fraction(values: list[float], count: int) -> float:
    subset = values[-count:] if count > 0 else []
    if not subset:
        return 0.0
    return float(sum(1 for value in subset if value > 0) / len(subset))


def summarize_policy(frame: pd.DataFrame, exit_mask: pd.Series, *, policy: str, rule: str, delay_seconds: int) -> dict[str, Any]:
    subset = frame.loc[exit_mask].copy()
    deltas = subset["exit_delta_dollars"] if not subset.empty else pd.Series(dtype="float64")
    by_day: list[dict[str, Any]] = []
    if not subset.empty:
        grouped = subset.groupby("day", sort=True)["exit_delta_dollars"].agg(["count", "sum"]).reset_index()
        by_day = [
            {
                "day": str(row["day"]),
                "count": int(row["count"]),
                "delta_dollars": round(float(row["sum"]), 4),
            }
            for _, row in grouped.iterrows()
        ]
    return {
        "policy": policy,
        "rule": rule,
        "delay_seconds": int(delay_seconds),
        "exit_count": int(len(subset)),
        "delta_dollars": round(float(deltas.sum()), 4) if not deltas.empty else 0.0,
        "positive_count": int((deltas > 0).sum()) if not deltas.empty else 0,
        "negative_count": int((deltas < 0).sum()) if not deltas.empty else 0,
        "hold_truth_count": int((deltas <= -1.0).sum()) if not deltas.empty else 0,
        "exit_now_truth_count": int((deltas >= 1.0).sum()) if not deltas.empty else 0,
        "false_exit_cost_dollars": round(float((-deltas[deltas < 0]).sum()), 4) if not deltas.empty else 0.0,
        "oracle_positive_only_delta_dollars": round(float(deltas[deltas > 0].sum()), 4) if not deltas.empty else 0.0,
        "by_day": by_day,
        "markets": [str(value) for value in subset["market"].tolist()],
    }


def build_policy_masks(frame: pd.DataFrame, base_mask: pd.Series) -> dict[str, pd.Series]:
    frame = frame.copy()
    actual_pnls = [float(value) for value in frame["net_pnl_dollars"].tolist()]
    deltas = [float(value) for value in frame["exit_delta_dollars"].tolist()]
    base_flags = [bool(value) for value in base_mask.tolist()]

    policy_flags: dict[str, list[bool]] = {
        "static": [],
        "prior4_actual_pnl_negative": [],
        "prior8_actual_pnl_negative": [],
        "prior4_actual_positive_fraction_lte_50": [],
        "prior8_actual_positive_fraction_lte_50": [],
        "prior2_same_rule_delta_positive": [],
        "prior3_same_rule_delta_positive": [],
        "prior5_same_rule_delta_positive": [],
        "prior2_same_rule_all_positive": [],
        "prior_day_same_rule_positive": [],
        "same_day_rule_running_positive": [],
    }

    prior_matching_deltas: list[float] = []
    previous_day_rule_delta_by_day: dict[str, float] = {}
    current_day = ""
    running_day_rule_delta = 0.0
    seen_days: list[str] = []

    for idx, is_match in enumerate(base_flags):
        day = str(frame.iloc[idx]["day"])
        if day != current_day:
            if current_day:
                previous_day_rule_delta_by_day[current_day] = running_day_rule_delta
            current_day = day
            running_day_rule_delta = 0.0
            seen_days.append(day)

        prior4_pnl = trailing_sum(actual_pnls[:idx], 4)
        prior8_pnl = trailing_sum(actual_pnls[:idx], 8)
        prior4_pf = trailing_positive_fraction(actual_pnls[:idx], 4)
        prior8_pf = trailing_positive_fraction(actual_pnls[:idx], 8)
        prior2_delta = trailing_sum(prior_matching_deltas, 2)
        prior3_delta = trailing_sum(prior_matching_deltas, 3)
        prior5_delta = trailing_sum(prior_matching_deltas, 5)
        prior2_all_positive = len(prior_matching_deltas[-2:]) == 2 and all(value > 0 for value in prior_matching_deltas[-2:])
        previous_day = seen_days[-2] if len(seen_days) >= 2 else ""
        previous_day_delta = previous_day_rule_delta_by_day.get(previous_day, 0.0)

        policy_flags["static"].append(is_match)
        policy_flags["prior4_actual_pnl_negative"].append(is_match and prior4_pnl < 0)
        policy_flags["prior8_actual_pnl_negative"].append(is_match and prior8_pnl < 0)
        policy_flags["prior4_actual_positive_fraction_lte_50"].append(is_match and idx >= 4 and prior4_pf <= 0.5)
        policy_flags["prior8_actual_positive_fraction_lte_50"].append(is_match and idx >= 8 and prior8_pf <= 0.5)
        policy_flags["prior2_same_rule_delta_positive"].append(is_match and len(prior_matching_deltas) >= 2 and prior2_delta > 0)
        policy_flags["prior3_same_rule_delta_positive"].append(is_match and len(prior_matching_deltas) >= 3 and prior3_delta > 0)
        policy_flags["prior5_same_rule_delta_positive"].append(is_match and len(prior_matching_deltas) >= 5 and prior5_delta > 0)
        policy_flags["prior2_same_rule_all_positive"].append(is_match and prior2_all_positive)
        policy_flags["prior_day_same_rule_positive"].append(is_match and previous_day_delta > 0)
        policy_flags["same_day_rule_running_positive"].append(is_match and running_day_rule_delta > 0)

        if is_match:
            delta = float(deltas[idx])
            prior_matching_deltas.append(delta)
            running_day_rule_delta += delta

    return {
        name: pd.Series(flags, index=frame.index)
        for name, flags in policy_flags.items()
    }


def evaluate_delay(args: argparse.Namespace, delay_seconds: int, rules: list[str]) -> dict[str, Any]:
    frame = build_exit_frame(
        dataset=str(args.dataset),
        entry_low=int(args.entry_low),
        entry_high=int(args.entry_high),
        stop_threshold=float(args.stop_threshold),
        delay_seconds=int(delay_seconds),
        include_estimated_exit_fee=bool(args.include_estimated_exit_fee),
    ).copy()
    frame["sort_key"] = frame["market"].map(market_sort_key)
    frame["day"] = frame["market"].map(day_label)
    frame = frame.sort_values(["sort_key", "market"]).reset_index(drop=True)
    frame["exit_delta_dollars"] = frame["exit_delay_net_pnl_dollars"] - frame["net_pnl_dollars"]

    results: list[dict[str, Any]] = []
    for rule in rules:
        base = rule_mask(frame, rule).fillna(False).astype(bool)
        policy_masks = build_policy_masks(frame, base)
        for policy, mask in policy_masks.items():
            results.append(summarize_policy(frame, mask.fillna(False).astype(bool), policy=policy, rule=rule, delay_seconds=delay_seconds))
    results.sort(
        key=lambda row: (
            float(row["delta_dollars"]),
            -float(row["false_exit_cost_dollars"]),
            int(row["exit_count"]),
        ),
        reverse=True,
    )
    false_exit_penalty = float(args.false_exit_penalty)
    risk_adjusted = sorted(
        results,
        key=lambda row: (
            float(row["delta_dollars"]) - (false_exit_penalty * float(row["false_exit_cost_dollars"])),
            float(row["delta_dollars"]),
            -float(row["false_exit_cost_dollars"]),
        ),
        reverse=True,
    )
    low_false_cost = sorted(
        [row for row in results if float(row["delta_dollars"]) >= float(args.min_low_false_cost_delta)],
        key=lambda row: (
            float(row["false_exit_cost_dollars"]),
            -float(row["delta_dollars"]),
            int(row["exit_count"]),
        ),
    )
    return {
        "delay_seconds": int(delay_seconds),
        "case_count": int(len(frame)),
        "baseline_actual_net_pnl_dollars": round(float(frame["net_pnl_dollars"].sum()), 4),
        "top_policies": results[: int(args.max_results)],
        "top_risk_adjusted_policies": risk_adjusted[: int(args.max_results)],
        "top_low_false_cost_policies": low_false_cost[: int(args.max_results)],
        "all_policies": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate online-only post-entry exit override supervisors.")
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--entry-low", type=int, default=89)
    parser.add_argument("--entry-high", type=int, default=92)
    parser.add_argument("--stop-threshold", type=float, default=70.0)
    parser.add_argument("--delays", nargs="*", type=int, default=[45, 60, 75, 90, 105, 120])
    parser.add_argument("--rules", nargs="*", default=[
        "last60_down_macd_neutral",
        "broad_no_neutral_neutral",
        "broad_no_neutral_neutral_macd_flat",
        "last60_down_macd_hist_flat",
        "rsi_neutral_macd_hist_flat",
        "side_no_macd_neutral",
        "side_no_rsi_neutral",
        "damage_heavy_macd_hist_flat",
    ])
    parser.add_argument("--max-results", type=int, default=20)
    parser.add_argument("--false-exit-penalty", type=float, default=0.5)
    parser.add_argument("--min-low-false-cost-delta", type=float, default=10.0)
    parser.add_argument("--include-estimated-exit-fee", action="store_true")
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    payload = {
        "summary": {
            "dataset": str(args.dataset),
            "entry_low": int(args.entry_low),
            "entry_high": int(args.entry_high),
            "stop_threshold": float(args.stop_threshold),
            "delays": [int(delay) for delay in args.delays],
            "rules": [str(rule) for rule in args.rules],
            "false_exit_penalty": float(args.false_exit_penalty),
            "min_low_false_cost_delta": float(args.min_low_false_cost_delta),
            "include_estimated_exit_fee": bool(args.include_estimated_exit_fee),
        },
        "delays": [
            evaluate_delay(args, int(delay), [str(rule) for rule in args.rules])
            for delay in args.delays
        ],
    }
    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved online exit supervisor policy eval to {output_path}")
    for delay in payload["delays"]:
        print(f"delay={delay['delay_seconds']} cases={delay['case_count']}")
        for row in delay["top_policies"][:5]:
            print(
                row["rule"],
                row["policy"],
                f"delta={row['delta_dollars']}",
                f"exits={row['exit_count']}",
                f"false_cost={row['false_exit_cost_dollars']}",
            )
        print(" risk_adjusted")
        for row in delay["top_risk_adjusted_policies"][:3]:
            score = float(row["delta_dollars"]) - (float(args.false_exit_penalty) * float(row["false_exit_cost_dollars"]))
            print(
                row["rule"],
                row["policy"],
                f"score={round(score, 4)}",
                f"delta={row['delta_dollars']}",
                f"false_cost={row['false_exit_cost_dollars']}",
            )


if __name__ == "__main__":
    main()
