from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from analyze_post_entry_exit_rules import build_exit_frame

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "post_entry_exit_candidate_eval_latest.json"


def named_policy_masks(frame: pd.DataFrame) -> dict[str, pd.Series]:
    hard_red = frame["current_strength"] == "weak"
    damage_heavy_rsi_slope_flat = (
        (frame["damage_state"] == "heavy")
        & (frame["btc_rsi14_slope_state"] == "flat")
    )
    no_strong_light_weak_below_or_near = (
        (frame["side"] == "NO")
        & (frame["current_strength"] == "strong")
        & (frame["damage_state"] == "light")
        & (frame["rebound_state"] == "weak")
        & frame["current_vs_entry_state"].isin(["below_entry", "near_entry"])
    )
    broad_no_neutral_neutral = (
        (frame["side"] == "NO")
        & (frame["btc_rsi14_state"] == "neutral")
        & (frame["btc_macd_state"] == "neutral")
    )
    narrow_no_down_neutral_neutral = (
        (frame["side"] == "NO")
        & (frame["last60_move_state"] == "down")
        & (frame["btc_rsi14_state"] == "neutral")
        & (frame["btc_macd_state"] == "neutral")
    )
    return {
        "NO_ACTION": pd.Series(False, index=frame.index),
        "hard_red_weak_strength": hard_red,
        "damage_heavy_rsi_slope_flat": damage_heavy_rsi_slope_flat,
        "no_strong_light_weak_below_or_near": no_strong_light_weak_below_or_near,
        "broad_no_neutral_neutral": broad_no_neutral_neutral,
        "narrow_no_down_neutral_neutral": narrow_no_down_neutral_neutral,
        "hard_red_or_damage_heavy_rsi_slope_flat": hard_red | damage_heavy_rsi_slope_flat,
        "hard_red_or_no_strong_light_weak_below_or_near": hard_red | no_strong_light_weak_below_or_near,
        "hard_red_or_broad_no_neutral_neutral": hard_red | broad_no_neutral_neutral,
        "hard_red_or_narrow_no_down_neutral_neutral": hard_red | narrow_no_down_neutral_neutral,
        "hard_red_or_broad_no_neutral_or_damage_heavy_rsi_flat": (
            hard_red | broad_no_neutral_neutral | damage_heavy_rsi_slope_flat
        ),
    }


def score_delta(frame: pd.DataFrame, mask: pd.Series) -> tuple[float, int]:
    subset = frame.loc[mask].copy()
    delta = subset["exit_delay_net_pnl_dollars"] - subset["net_pnl_dollars"]
    return float(delta.sum()), int(len(subset))


def summarize_mask(frame: pd.DataFrame, mask: pd.Series, *, label: str) -> dict[str, Any]:
    subset = frame.loc[mask].copy()
    delta = subset["exit_delay_net_pnl_dollars"] - subset["net_pnl_dollars"]
    return {
        "label": label,
        "count": int(len(subset)),
        "actual_net_pnl_dollars": round(float(subset["net_pnl_dollars"].sum()), 4),
        "exit_delay_net_pnl_dollars": round(float(subset["exit_delay_net_pnl_dollars"].sum()), 4),
        "delta_dollars": round(float(delta.sum()), 4),
        "improved_trade_count": int((delta > 0).sum()),
        "harmed_trade_count": int((delta < 0).sum()),
        "avg_positive_delta": round(float(delta[delta > 0].mean()), 4) if int((delta > 0).sum()) else None,
        "avg_negative_delta_abs": round(float((-delta[delta < 0]).mean()), 4) if int((delta < 0).sum()) else None,
    }


def summarize_by_day(frame: pd.DataFrame, mask: pd.Series) -> list[dict[str, Any]]:
    subset = frame.loc[mask].copy()
    if subset.empty:
        return []
    subset["delta_dollars"] = subset["exit_delay_net_pnl_dollars"] - subset["net_pnl_dollars"]
    grouped = (
        subset.groupby("day", sort=True)
        .agg(
            count=("market", "size"),
            actual_net_pnl_dollars=("net_pnl_dollars", "sum"),
            exit_delay_net_pnl_dollars=("exit_delay_net_pnl_dollars", "sum"),
            delta_dollars=("delta_dollars", "sum"),
        )
        .reset_index()
    )
    return grouped.to_dict(orient="records")


def walkforward_select(frame: pd.DataFrame, policy_masks: dict[str, pd.Series]) -> dict[str, Any]:
    days = sorted(str(day) for day in frame["day"].dropna().unique())
    parts: list[dict[str, Any]] = []
    total_delta = 0.0
    for idx in range(1, len(days)):
        train = frame[frame["day"].isin(days[:idx])].copy()
        test = frame[frame["day"] == days[idx]].copy()
        best_name = "NO_ACTION"
        best_delta = 0.0
        best_count = 0
        for name, mask in policy_masks.items():
            train_delta, train_count = score_delta(train, mask.loc[train.index])
            if (
                train_delta > best_delta + 1e-9
                or (abs(train_delta - best_delta) <= 1e-9 and train_count < best_count)
                or (name == "NO_ACTION" and best_name == "NO_ACTION")
            ):
                best_name = name
                best_delta = train_delta
                best_count = train_count
        test_mask = policy_masks[best_name].loc[test.index]
        test_delta, test_count = score_delta(test, test_mask)
        total_delta += test_delta
        parts.append(
            {
                "test_day": days[idx],
                "selected_policy": best_name,
                "train_delta_dollars": round(best_delta, 4),
                "train_count": int(best_count),
                "test_delta_dollars": round(test_delta, 4),
                "test_count": int(test_count),
            }
        )
    return {
        "parts": parts,
        "aggregate_delta_dollars": round(total_delta, 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate curated 90-second post-entry exit candidate slices and walk-forward selection.")
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--entry-low", type=int, default=89)
    parser.add_argument("--entry-high", type=int, default=92)
    parser.add_argument("--stop-threshold", type=float, default=70.0)
    parser.add_argument("--delay-seconds", type=int, default=90)
    parser.add_argument("--include-estimated-exit-fee", action="store_true")
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    frame = build_exit_frame(
        dataset=str(args.dataset),
        entry_low=int(args.entry_low),
        entry_high=int(args.entry_high),
        stop_threshold=float(args.stop_threshold),
        delay_seconds=int(args.delay_seconds),
        include_estimated_exit_fee=bool(args.include_estimated_exit_fee),
    )
    if frame.empty:
        raise RuntimeError("No candidate rows found for post-entry exit evaluation.")
    frame["day"] = frame["market"].str.extract(r"(\d{2}[A-Z]{3}\d{2})")[0]

    policy_masks = named_policy_masks(frame)
    payload = {
        "summary": {
            "dataset": str(args.dataset),
            "delay_seconds": int(args.delay_seconds),
            "case_count": int(len(frame)),
            "baseline_actual_net_pnl_dollars": round(float(frame["net_pnl_dollars"].sum()), 4),
            "include_estimated_exit_fee": bool(args.include_estimated_exit_fee),
        },
        "policies": {
            name: {
                "summary": summarize_mask(frame, mask, label=name),
                "by_day": summarize_by_day(frame, mask),
            }
            for name, mask in policy_masks.items()
        },
        "walkforward_select_best_curated_policy": walkforward_select(frame, policy_masks),
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved post-entry exit candidate evaluation to {output_path}")
    print(json.dumps(payload["summary"], indent=2))
    for name, info in payload["policies"].items():
        print(name, json.dumps(info["summary"], sort_keys=True))
    print(json.dumps(payload["walkforward_select_best_curated_policy"], indent=2))


if __name__ == "__main__":
    main()
