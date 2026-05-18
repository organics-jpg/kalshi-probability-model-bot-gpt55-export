from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from analyze_post_entry_exit_rules import build_exit_frame

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "truffle_exit_policy_sensitivity_latest.json"


def truth_label(delta: float) -> str:
    if delta >= 1.0:
        return "EXIT_NOW"
    if delta <= -1.0:
        return "HOLD"
    return "NEUTRAL"


def named_masks(frame: pd.DataFrame) -> dict[str, pd.Series]:
    hard_red = frame["current_strength"] == "weak"
    broad_no_neutral_neutral = (
        (frame["side"] == "NO")
        & (frame["btc_rsi14_state"] == "neutral")
        & (frame["btc_macd_state"] == "neutral")
    )
    broad_no_neutral_neutral_macd_flat = broad_no_neutral_neutral & (
        frame["btc_macd_hist_state"] == "flat"
    )
    narrow_no_down_neutral_neutral = broad_no_neutral_neutral & (
        frame["last60_move_state"] == "down"
    )
    damage_heavy_rsi_flat = (
        (frame["damage_state"] == "heavy")
        & (frame["btc_rsi14_slope_state"] == "flat")
    )
    broad_no_side_relative_mixed = broad_no_neutral_neutral & (
        frame["btc_macd_hist_state"].isin(["flat", "unknown"])
    )
    return {
        "hard_red_weak_strength": hard_red,
        "broad_no_neutral_neutral": broad_no_neutral_neutral,
        "broad_no_neutral_neutral_macd_flat": broad_no_neutral_neutral_macd_flat,
        "narrow_no_down_neutral_neutral": narrow_no_down_neutral_neutral,
        "damage_heavy_rsi_slope_flat": damage_heavy_rsi_flat,
        "hard_red_or_broad_no_neutral_neutral": hard_red | broad_no_neutral_neutral,
        "broad_no_side_relative_mixed": broad_no_side_relative_mixed,
    }


def summarize_slice(frame: pd.DataFrame, mask: pd.Series, *, label: str) -> dict[str, Any]:
    subset = frame.loc[mask].copy()
    if subset.empty:
        return {
            "label": label,
            "count": 0,
        }
    delta = subset["exit_delta_dollars"]
    positive = delta[delta > 0]
    negative = delta[delta < 0]
    labels = subset["exit_truth_label"].value_counts().to_dict()
    avg_positive = float(positive.mean()) if len(positive) else None
    avg_negative_abs = float((-negative).mean()) if len(negative) else None
    break_even_precision = (
        avg_negative_abs / (avg_positive + avg_negative_abs)
        if avg_positive is not None and avg_negative_abs not in (None, 0.0)
        else None
    )
    exit_all_delta = float(delta.sum())
    oracle_delta = float(positive.sum())
    deterministic_false_exit_cost = float((-negative).sum())
    return {
        "label": label,
        "count": int(len(subset)),
        "exit_now_truth_count": int(labels.get("EXIT_NOW", 0)),
        "neutral_truth_count": int(labels.get("NEUTRAL", 0)),
        "hold_truth_count": int(labels.get("HOLD", 0)),
        "exit_all_delta_dollars": round(exit_all_delta, 4),
        "oracle_exit_positive_only_delta_dollars": round(oracle_delta, 4),
        "truffle_room_vs_exit_all_dollars": round(oracle_delta - exit_all_delta, 4),
        "deterministic_false_exit_cost_dollars": round(deterministic_false_exit_cost, 4),
        "avg_positive_exit_value": round(avg_positive, 4) if avg_positive is not None else None,
        "avg_wrong_exit_cost": round(avg_negative_abs, 4) if avg_negative_abs is not None else None,
        "break_even_exit_precision": round(break_even_precision, 4) if break_even_precision is not None else None,
        "positive_rate": round(float((delta > 0).mean()), 4),
        "hold_truth_rate": round(float((subset["exit_truth_label"] == "HOLD").mean()), 4),
    }


def analyze_delay(args: argparse.Namespace, delay_seconds: int) -> dict[str, Any]:
    frame = build_exit_frame(
        dataset=str(args.dataset),
        entry_low=int(args.entry_low),
        entry_high=int(args.entry_high),
        stop_threshold=float(args.stop_threshold),
        delay_seconds=int(delay_seconds),
        include_estimated_exit_fee=bool(args.include_estimated_exit_fee),
    )
    if frame.empty:
        return {
            "delay_seconds": delay_seconds,
            "case_count": 0,
            "slices": {},
        }
    frame = frame.copy()
    frame["exit_delta_dollars"] = frame["exit_delay_net_pnl_dollars"] - frame["net_pnl_dollars"]
    frame["exit_truth_label"] = frame["exit_delta_dollars"].apply(lambda value: truth_label(float(value)))
    masks = named_masks(frame)
    slices = {
        name: summarize_slice(frame, mask, label=name)
        for name, mask in masks.items()
    }
    ranked_by_exit_all = sorted(
        slices.values(),
        key=lambda row: (float(row.get("exit_all_delta_dollars") or 0.0), int(row.get("count") or 0)),
        reverse=True,
    )
    ranked_by_truffle_room = sorted(
        slices.values(),
        key=lambda row: (float(row.get("truffle_room_vs_exit_all_dollars") or 0.0), int(row.get("count") or 0)),
        reverse=True,
    )
    return {
        "delay_seconds": int(delay_seconds),
        "case_count": int(len(frame)),
        "baseline_actual_net_pnl_dollars": round(float(frame["net_pnl_dollars"].sum()), 4),
        "slices": slices,
        "top_exit_all": ranked_by_exit_all[:5],
        "top_truffle_room": ranked_by_truffle_room[:5],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Estimate where Truffle can add incremental value over deterministic post-entry exit slices."
    )
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--entry-low", type=int, default=89)
    parser.add_argument("--entry-high", type=int, default=92)
    parser.add_argument("--stop-threshold", type=float, default=70.0)
    parser.add_argument("--delays", nargs="*", type=int, default=[45, 60, 75, 90, 105, 120])
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
            "include_estimated_exit_fee": bool(args.include_estimated_exit_fee),
        },
        "delays": [analyze_delay(args, int(delay)) for delay in args.delays],
    }
    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved Truffle exit policy sensitivity to {output_path}")
    for delay in payload["delays"]:
        print(f"delay={delay['delay_seconds']} cases={delay['case_count']}")
        best_exit = delay["top_exit_all"][0] if delay["top_exit_all"] else {}
        best_room = delay["top_truffle_room"][0] if delay["top_truffle_room"] else {}
        print(
            " best_exit_all",
            best_exit.get("label"),
            f"delta={best_exit.get('exit_all_delta_dollars')}",
            f"count={best_exit.get('count')}",
            f"precision_needed={best_exit.get('break_even_exit_precision')}",
        )
        print(
            " best_truffle_room",
            best_room.get("label"),
            f"room={best_room.get('truffle_room_vs_exit_all_dollars')}",
            f"false_cost={best_room.get('deterministic_false_exit_cost_dollars')}",
        )


if __name__ == "__main__":
    main()
