from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from analyze_post_entry_exit_rules import build_exit_frame
from export_ambiguity_slice_cases import build_case_payloads
from truffle_post_entry_shadow import (
    classify_exit_supervisor_policy_hints,
    classify_side_relative_technicals,
)

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "truffle_exit_supervisor_bench_latest.json"


def classify_shadow_label(delta_dollars: float) -> str:
    if delta_dollars >= 1.0:
        return "RED_LIGHT"
    if delta_dollars <= -1.0:
        return "GREEN_LIGHT"
    return "NEUTRAL"


def attach_policy_hints(payload: dict[str, Any], candidate_tags: list[str]) -> dict[str, Any]:
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
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Export compact post-entry Truffle exit-supervisor bench cases with expected labels.")
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--entry-low", type=int, default=89)
    parser.add_argument("--entry-high", type=int, default=92)
    parser.add_argument("--stop-threshold", type=float, default=70.0)
    parser.add_argument("--delay-seconds", type=int, default=90)
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
        exit_frame[
            [
                "market",
                "same_bid_at_delay",
                "exit_delay_net_pnl_dollars",
                "net_pnl_dollars",
            ]
        ],
        on=["market", "net_pnl_dollars"],
        how="inner",
        suffixes=("", "_exit"),
    )
    if frame.empty:
        raise RuntimeError("No merged payload/exit rows found for exit supervisor bench.")

    frame["delta_dollars"] = frame["exit_delay_net_pnl_dollars"] - frame["net_pnl_dollars"]
    frame["shadow_label"] = frame["delta_dollars"].apply(lambda value: classify_shadow_label(float(value)))
    frame["slice_tags"] = [[] for _ in range(len(frame))]

    mask_hard_red = frame["current_strength"] == "weak"
    mask_broad_no_neutral_neutral = (
        (frame["side"] == "NO")
        & (frame["btc_rsi14_state"] == "neutral")
        & (frame["btc_macd_state"] == "neutral")
    )
    mask_broad_no_neutral_neutral_macd_flat = (
        mask_broad_no_neutral_neutral
        & (frame["btc_macd_hist_state"] == "flat")
    )
    mask_narrow_no_down_neutral_neutral = (
        (frame["side"] == "NO")
        & (frame["last60_move_state"] == "down")
        & (frame["btc_rsi14_state"] == "neutral")
        & (frame["btc_macd_state"] == "neutral")
    )
    mask_damage_heavy_rsi_flat = (
        (frame["damage_state"] == "heavy")
        & (frame["btc_rsi14_slope_state"] == "flat")
    )

    tag_rules = {
        "hard_red_weak_strength": mask_hard_red,
        "broad_no_neutral_neutral": mask_broad_no_neutral_neutral,
        "broad_no_neutral_neutral_macd_flat": mask_broad_no_neutral_neutral_macd_flat,
        "narrow_no_down_neutral_neutral": mask_narrow_no_down_neutral_neutral,
        "damage_heavy_rsi_slope_flat": mask_damage_heavy_rsi_flat,
    }
    for tag, mask in tag_rules.items():
        frame.loc[mask, "slice_tags"] = frame.loc[mask, "slice_tags"].apply(lambda tags, value=tag: tags + [value])

    tagged = frame[frame["slice_tags"].map(bool)].copy()
    neutral_holdout = frame[(frame["slice_tags"].map(len) == 0) & (frame["shadow_label"] == "GREEN_LIGHT")].copy().head(10)
    bench = pd.concat([tagged, neutral_holdout], ignore_index=True)
    bench = bench.sort_values(["shadow_label", "delta_dollars", "market"], ascending=[True, False, True]).reset_index(drop=True)

    rows: list[dict[str, Any]] = []
    for _, row in bench.iterrows():
        rows.append(
            {
                "market": row["market"],
                "side": row["side"],
                "slice_tags": list(row["slice_tags"]),
                "shadow_label": row["shadow_label"],
                "delta_dollars": round(float(row["delta_dollars"]), 4),
                "actual_net_pnl_dollars": round(float(row["net_pnl_dollars"]), 4),
                "exit_delay_net_pnl_dollars": round(float(row["exit_delay_net_pnl_dollars"]), 4),
                "same_bid_at_delay": round(float(row["same_bid_at_delay"]), 4),
                "payload": attach_policy_hints(row["payload"] if isinstance(row["payload"], dict) else {}, list(row["slice_tags"])),
            }
        )

    summary = {
        "dataset": str(args.dataset),
        "delay_seconds": int(args.delay_seconds),
        "case_count": int(len(frame)),
        "bench_count": int(len(rows)),
        "label_counts": bench["shadow_label"].value_counts().to_dict(),
        "tag_counts": {tag: int(mask.sum()) for tag, mask in tag_rules.items()},
        "include_estimated_exit_fee": bool(args.include_estimated_exit_fee),
    }
    payload = {
        "summary": summary,
        "rows": rows,
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved Truffle exit supervisor bench to {output_path}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
