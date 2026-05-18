from __future__ import annotations

import argparse
import json
from itertools import combinations, product
from pathlib import Path
from typing import Any

import pandas as pd

from analyze_post_entry_exit_rules import build_exit_frame

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "stable_post_entry_exit_rule_mining_latest.json"

FEATURES = [
    "side",
    "current_strength",
    "damage_state",
    "rebound_state",
    "current_vs_entry_state",
    "spread_state",
    "entry_location_in_range",
    "entry_pressure_state",
    "entry_timing_state",
    "open_to_entry_runup",
    "last30_move_state",
    "last60_move_state",
    "volatility_state",
    "btc_rsi14_state",
    "btc_rsi14_slope_state",
    "btc_macd_state",
    "btc_macd_hist_state",
    "btc_price_vs_ema21_state",
]


def normalize_value(value: Any) -> str:
    if value is None or pd.isna(value):
        return "NA"
    return str(value)


def split_rule(rule: str) -> list[tuple[str, str]]:
    parts: list[tuple[str, str]] = []
    for raw_part in rule.split(" & "):
        if "=" not in raw_part:
            continue
        key, value = raw_part.split("=", 1)
        parts.append((key, value))
    return parts


def mask_for_rule(frame: pd.DataFrame, rule: str) -> pd.Series:
    mask = pd.Series(True, index=frame.index)
    for feature, value in split_rule(rule):
        if feature not in frame.columns:
            return pd.Series(False, index=frame.index)
        mask &= frame[feature].map(normalize_value) == value
    return mask


def summarize_subset(frame: pd.DataFrame, mask: pd.Series, *, rule: str, delay_seconds: int) -> dict[str, Any]:
    subset = frame.loc[mask].copy()
    if subset.empty:
        return {
            "rule": rule,
            "delay_seconds": int(delay_seconds),
            "count": 0,
        }
    delta = subset["exit_delta_dollars"]
    positive = delta[delta > 0]
    negative = delta[delta < 0]
    day_summary: list[dict[str, Any]] = []
    if "day" in subset.columns:
        grouped = subset.groupby("day", sort=True)["exit_delta_dollars"].agg(["count", "sum"]).reset_index()
        day_summary = [
            {
                "day": str(row["day"]),
                "count": int(row["count"]),
                "delta_dollars": round(float(row["sum"]), 4),
            }
            for _, row in grouped.iterrows()
        ]
    return {
        "rule": rule,
        "delay_seconds": int(delay_seconds),
        "count": int(len(subset)),
        "delta_dollars": round(float(delta.sum()), 4),
        "positive_count": int((delta > 0).sum()),
        "negative_count": int((delta < 0).sum()),
        "neutralish_count": int((delta.abs() < 1.0).sum()),
        "hold_truth_count": int((delta <= -1.0).sum()),
        "exit_now_truth_count": int((delta >= 1.0).sum()),
        "avg_positive_delta": round(float(positive.mean()), 4) if len(positive) else None,
        "avg_negative_delta_abs": round(float((-negative).mean()), 4) if len(negative) else None,
        "false_exit_cost_dollars": round(float((-negative).sum()), 4),
        "oracle_positive_only_delta_dollars": round(float(positive.sum()), 4),
        "day_count": int(len(day_summary)),
        "positive_day_count": int(sum(1 for row in day_summary if float(row["delta_dollars"]) > 0)),
        "negative_day_count": int(sum(1 for row in day_summary if float(row["delta_dollars"]) < 0)),
        "day_summary": day_summary,
        "markets": [str(value) for value in subset["market"].tolist()[:20]] if "market" in subset.columns else [],
    }


def build_delay_frame(args: argparse.Namespace, delay_seconds: int) -> pd.DataFrame:
    frame = build_exit_frame(
        dataset=str(args.dataset),
        entry_low=int(args.entry_low),
        entry_high=int(args.entry_high),
        stop_threshold=float(args.stop_threshold),
        delay_seconds=int(delay_seconds),
        include_estimated_exit_fee=bool(args.include_estimated_exit_fee),
    )
    if frame.empty:
        return frame
    frame = frame.copy()
    frame["exit_delta_dollars"] = frame["exit_delay_net_pnl_dollars"] - frame["net_pnl_dollars"]
    frame["day"] = frame["market"].astype(str).str.extract(r"(\d{2}[A-Z]{3}\d{2})")[0].fillna("unknown")
    return frame


def candidate_rules_for_frame(frame: pd.DataFrame, *, min_count: int, max_width: int) -> list[str]:
    available_features = [feature for feature in FEATURES if feature in frame.columns]
    values_by_feature = {
        feature: [
            normalize_value(value)
            for value, count in frame[feature].map(normalize_value).value_counts().items()
            if int(count) >= min_count and normalize_value(value) != "NA"
        ]
        for feature in available_features
    }
    rules: set[str] = set()
    for width in range(1, max_width + 1):
        for features in combinations(available_features, width):
            value_lists = [values_by_feature.get(feature, []) for feature in features]
            if not all(value_lists):
                continue
            for values in product(*value_lists):
                mask = pd.Series(True, index=frame.index)
                parts: list[str] = []
                for feature, value in zip(features, values):
                    mask &= frame[feature].map(normalize_value) == value
                    parts.append(f"{feature}={value}")
                if int(mask.sum()) >= min_count:
                    rules.add(" & ".join(parts))
    return sorted(rules)


def aggregate_rule(rule: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    non_empty = [row for row in rows if int(row.get("count") or 0) > 0]
    deltas = [float(row.get("delta_dollars") or 0.0) for row in non_empty]
    counts = [int(row.get("count") or 0) for row in non_empty]
    false_costs = [float(row.get("false_exit_cost_dollars") or 0.0) for row in non_empty]
    oracle_values = [float(row.get("oracle_positive_only_delta_dollars") or 0.0) for row in non_empty]
    days = sorted(
        {
            str(day.get("day") or "")
            for row in non_empty
            for day in list(row.get("day_summary") or [])
            if str(day.get("day") or "")
        }
    )
    day_deltas: dict[str, float] = {}
    for row in non_empty:
        for day in list(row.get("day_summary") or []):
            key = str(day.get("day") or "")
            if not key:
                continue
            day_deltas[key] = day_deltas.get(key, 0.0) + float(day.get("delta_dollars") or 0.0)
    return {
        "rule": rule,
        "present_delay_count": int(len(non_empty)),
        "positive_delay_count": int(sum(1 for value in deltas if value > 0)),
        "negative_delay_count": int(sum(1 for value in deltas if value < 0)),
        "present_day_count": int(len(days)),
        "positive_aggregate_day_count": int(sum(1 for value in day_deltas.values() if value > 0)),
        "negative_aggregate_day_count": int(sum(1 for value in day_deltas.values() if value < 0)),
        "total_count": int(sum(counts)),
        "avg_count_per_present_delay": round(float(sum(counts) / len(counts)), 4) if counts else None,
        "total_delta_dollars": round(float(sum(deltas)), 4),
        "avg_delta_dollars": round(float(sum(deltas) / len(deltas)), 4) if deltas else None,
        "min_delta_dollars": round(float(min(deltas)), 4) if deltas else None,
        "max_delta_dollars": round(float(max(deltas)), 4) if deltas else None,
        "total_false_exit_cost_dollars": round(float(sum(false_costs)), 4),
        "total_oracle_positive_only_delta_dollars": round(float(sum(oracle_values)), 4),
        "truffle_room_vs_exit_all_dollars": round(float(sum(oracle_values) - sum(deltas)), 4),
        "aggregate_day_deltas": {day: round(day_deltas.get(day, 0.0), 4) for day in days},
        "rows_by_delay": non_empty,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Mine post-entry exit rules that stay positive across multiple shadow delays.")
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--entry-low", type=int, default=89)
    parser.add_argument("--entry-high", type=int, default=92)
    parser.add_argument("--stop-threshold", type=float, default=70.0)
    parser.add_argument("--delays", nargs="*", type=int, default=[45, 60, 75, 90, 105, 120])
    parser.add_argument("--min-count", type=int, default=5)
    parser.add_argument("--min-days", type=int, default=2)
    parser.add_argument("--max-width", type=int, default=2)
    parser.add_argument("--max-rules", type=int, default=25)
    parser.add_argument("--include-estimated-exit-fee", action="store_true")
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    frames = {
        int(delay): build_delay_frame(args, int(delay))
        for delay in args.delays
    }
    all_rules: set[str] = set()
    for frame in frames.values():
        if not frame.empty:
            all_rules.update(
                candidate_rules_for_frame(
                    frame,
                    min_count=int(args.min_count),
                    max_width=int(args.max_width),
                )
            )

    aggregates: list[dict[str, Any]] = []
    for rule in sorted(all_rules):
        rows = []
        for delay, frame in frames.items():
            if frame.empty:
                continue
            mask = mask_for_rule(frame, rule)
            if int(mask.sum()) < int(args.min_count):
                continue
            summary = summarize_subset(frame, mask, rule=rule, delay_seconds=int(delay))
            rows.append(summary)
        if rows and sum(float(row.get("delta_dollars") or 0.0) for row in rows) > 0:
            aggregate = aggregate_rule(rule, rows)
            if int(aggregate["present_day_count"]) >= int(args.min_days):
                aggregates.append(aggregate)

    aggregates.sort(
        key=lambda row: (
            int(row["positive_delay_count"]),
            int(row["present_day_count"]),
            float(row["min_delta_dollars"] or -9999.0),
            float(row["total_delta_dollars"]),
            float(row["truffle_room_vs_exit_all_dollars"]),
        ),
        reverse=True,
    )

    payload = {
        "summary": {
            "dataset": str(args.dataset),
            "entry_low": int(args.entry_low),
            "entry_high": int(args.entry_high),
            "stop_threshold": float(args.stop_threshold),
            "delays": [int(delay) for delay in args.delays],
            "min_count": int(args.min_count),
            "min_days": int(args.min_days),
            "max_width": int(args.max_width),
            "include_estimated_exit_fee": bool(args.include_estimated_exit_fee),
            "candidate_rule_count": int(len(all_rules)),
            "positive_rule_count": int(len(aggregates)),
        },
        "top_stable_rules": aggregates[: int(args.max_rules)],
        "top_truffle_room_rules": sorted(
            aggregates,
            key=lambda row: (
                float(row["truffle_room_vs_exit_all_dollars"]),
                int(row["positive_delay_count"]),
                float(row["total_delta_dollars"]),
            ),
            reverse=True,
        )[: int(args.max_rules)],
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved stable post-entry exit rule mining to {output_path}")
    print(json.dumps(payload["summary"], indent=2))
    for row in payload["top_stable_rules"][:8]:
        print(
            row["rule"],
            f"positive_delays={row['positive_delay_count']}",
            f"min_delta={row['min_delta_dollars']}",
            f"total_delta={row['total_delta_dollars']}",
            f"room={row['truffle_room_vs_exit_all_dollars']}",
        )


if __name__ == "__main__":
    main()
