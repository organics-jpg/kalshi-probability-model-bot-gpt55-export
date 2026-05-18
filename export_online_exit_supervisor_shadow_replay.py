from __future__ import annotations

import argparse
import json
import re
from collections import deque
from pathlib import Path
from typing import Any

import pandas as pd

from analyze_post_entry_exit_rules import build_exit_frame
from export_ambiguity_slice_cases import build_case_payloads
from export_truffle_exit_supervisor_bench import classify_shadow_label
from truffle_post_entry_shadow import (
    classify_exit_supervisor_policy_hints,
    classify_exit_supervisor_memory_hint,
    classify_side_relative_technicals,
)

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "online_exit_supervisor_shadow_replay_latest.json"

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
    yy, mon, dd, hh, minute = match.groups()
    return (2000 + int(yy), int(MONTHS.get(mon, 12)), int(dd), int(hh), int(minute), str(market or ""))


def classify_tags(row: pd.Series) -> list[str]:
    tags: list[str] = []
    if str(row.get("current_strength") or "") == "weak":
        tags.append("hard_red_weak_strength")
    broad_no_neutral = (
        str(row.get("side") or "") == "NO"
        and str(row.get("btc_rsi14_state") or "") == "neutral"
        and str(row.get("btc_macd_state") or "") == "neutral"
    )
    if broad_no_neutral:
        tags.append("broad_no_neutral_neutral")
        if str(row.get("btc_macd_hist_state") or "") == "flat":
            tags.append("broad_no_neutral_neutral_macd_flat")
        if str(row.get("last60_move_state") or "") == "down":
            tags.append("narrow_no_down_neutral_neutral")
    if str(row.get("damage_state") or "") == "heavy" and str(row.get("btc_rsi14_slope_state") or "") == "flat":
        tags.append("damage_heavy_rsi_slope_flat")
    return tags


def summarize_memory_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    deltas = [float(row.get("delta_vs_actual_dollars") or 0.0) for row in rows]
    last2 = deltas[-2:]
    last3 = deltas[-3:]
    last5 = deltas[-5:]
    return {
        "count": int(len(rows)),
        "last2_delta_sum": round(float(sum(last2)), 4),
        "last3_delta_sum": round(float(sum(last3)), 4),
        "last5_delta_sum": round(float(sum(last5)), 4),
        "last2_all_positive": bool(len(last2) == 2 and all(value > 0 for value in last2)),
        "last5_positive_count": int(sum(1 for value in last5 if value > 0)),
        "last5_negative_count": int(sum(1 for value in last5 if value < 0)),
        "last5_false_exit_cost_dollars": round(float(-sum(value for value in last5 if value < 0)), 4),
        "last5_oracle_exit_value_dollars": round(float(sum(value for value in last5 if value > 0)), 4),
        "last5_truth_sequence": [str(row.get("truth_label") or "") for row in rows[-5:]],
    }


def summarize_shadow_exit_memory(memory: deque[dict[str, Any]], candidate_tags: list[str]) -> dict[str, Any]:
    rows = list(memory)
    by_tag: dict[str, Any] = {}
    for tag in candidate_tags:
        tagged = [row for row in rows if tag in list(row.get("tags") or [])]
        by_tag[tag] = summarize_memory_rows(tagged) if tagged else {"count": 0}
    return {
        "schema_version": "shadow_exit_memory_v1",
        "source": "historical_replay_prior_rows_only",
        "global": summarize_memory_rows(rows) if rows else {"count": 0},
        "candidate_tags": by_tag,
    }


def attach_recent_context(payload: dict[str, Any], shadow_exit_memory: dict[str, Any], candidate_tags: list[str]) -> dict[str, Any]:
    out = dict(payload)
    out["candidate_slice_tags"] = list(candidate_tags)
    technicals = out.get("technicals") if isinstance(out.get("technicals"), dict) else {}
    post_entry_technicals = technicals.get("post_entry") if isinstance(technicals.get("post_entry"), dict) else {}
    post_entry = out.get("post_entry") if isinstance(out.get("post_entry"), dict) else {}
    side_relative = classify_side_relative_technicals(str(out.get("side") or ""), post_entry_technicals)
    out["side_relative_technicals"] = side_relative
    out["deterministic_policy_hints"] = classify_exit_supervisor_policy_hints(
        post_entry=post_entry,
        side_relative_technicals=side_relative,
        candidate_slice_tags=candidate_tags,
    )
    out["shadow_memory_policy_hint"] = classify_exit_supervisor_memory_hint(
        shadow_exit_memory,
        candidate_tags,
    )
    recent_market_context = dict(out.get("recent_market_context") or {})
    recent_market_context.pop("shadow_exit_memory", None)
    out["recent_market_context"] = recent_market_context
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export chronological Truffle exit-supervisor cases with prior-only shadow exit memory."
    )
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--entry-low", type=int, default=89)
    parser.add_argument("--entry-high", type=int, default=92)
    parser.add_argument("--stop-threshold", type=float, default=70.0)
    parser.add_argument("--delay-seconds", type=int, default=90)
    parser.add_argument("--tagged-only", action="store_true")
    parser.add_argument("--include-estimated-exit-fee", action="store_true")
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    exit_frame = build_exit_frame(
        dataset=str(args.dataset),
        entry_low=int(args.entry_low),
        entry_high=int(args.entry_high),
        stop_threshold=float(args.stop_threshold),
        delay_seconds=int(args.delay_seconds),
        include_estimated_exit_fee=bool(args.include_estimated_exit_fee),
    )
    payload_frame = build_case_payloads(
        dataset=str(args.dataset),
        entry_low=int(args.entry_low),
        entry_high=int(args.entry_high),
        stop_threshold=float(args.stop_threshold),
        delay_seconds=int(args.delay_seconds),
    )
    frame = payload_frame.merge(
        exit_frame[["market", "same_bid_at_delay", "exit_delay_net_pnl_dollars", "net_pnl_dollars"]],
        on=["market", "net_pnl_dollars"],
        how="inner",
        suffixes=("", "_exit"),
    )
    if frame.empty:
        raise RuntimeError("No merged rows available for online shadow replay export.")
    frame["delta_dollars"] = frame["exit_delay_net_pnl_dollars"] - frame["net_pnl_dollars"]
    frame["shadow_label"] = frame["delta_dollars"].apply(lambda value: classify_shadow_label(float(value)))
    frame["sort_key"] = frame["market"].map(market_sort_key)
    frame = frame.sort_values(["sort_key", "market"]).reset_index(drop=True)

    rows: list[dict[str, Any]] = []
    memory: deque[dict[str, Any]] = deque(maxlen=64)
    tag_counts: dict[str, int] = {}
    for _, row in frame.iterrows():
        tags = classify_tags(row)
        for tag in tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        if bool(args.tagged_only) and not tags:
            continue
        shadow_memory = summarize_shadow_exit_memory(memory, tags)
        payload = row["payload"] if isinstance(row["payload"], dict) else {}
        rows.append(
            {
                "market": row["market"],
                "side": row["side"],
                "slice_tags": tags,
                "shadow_label": row["shadow_label"],
                "expected_decision": "EXIT_NOW" if row["shadow_label"] == "RED_LIGHT" else "HOLD",
                "delta_dollars": round(float(row["delta_dollars"]), 4),
                "actual_net_pnl_dollars": round(float(row["net_pnl_dollars"]), 4),
                "exit_delay_net_pnl_dollars": round(float(row["exit_delay_net_pnl_dollars"]), 4),
                "same_bid_at_delay": round(float(row["same_bid_at_delay"]), 4),
                "shadow_exit_memory": shadow_memory,
                "payload": attach_recent_context(payload, shadow_memory, tags),
            }
        )
        memory.append(
            {
                "market": row["market"],
                "tags": tags,
                "delta_vs_actual_dollars": round(float(row["delta_dollars"]), 4),
                "truth_label": "EXIT_NOW" if float(row["delta_dollars"]) >= 1.0 else "HOLD" if float(row["delta_dollars"]) <= -1.0 else "NEUTRAL",
                "model_decision": "REPLAY_ORACLE_NOT_MODEL",
                "decision_schema": "exit_supervisor_replay",
            }
        )

    summary = {
        "dataset": str(args.dataset),
        "delay_seconds": int(args.delay_seconds),
        "case_count": int(len(frame)),
        "replay_count": int(len(rows)),
        "tagged_only": bool(args.tagged_only),
        "label_counts": pd.Series([row["shadow_label"] for row in rows]).value_counts().to_dict() if rows else {},
        "tag_counts": tag_counts,
        "include_estimated_exit_fee": bool(args.include_estimated_exit_fee),
        "memory_source": "prior_rows_only_oracle_replay_for_payload_testing",
    }
    payload = {"summary": summary, "rows": rows}

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved online Truffle exit shadow replay to {output_path}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
