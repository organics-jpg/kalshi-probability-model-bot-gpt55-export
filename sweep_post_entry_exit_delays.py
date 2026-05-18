from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from analyze_post_entry_exit_rules import build_exit_frame
from evaluate_post_entry_exit_candidates import named_policy_masks, summarize_mask, walkforward_select

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "post_entry_exit_delay_sweep_latest.json"


def parse_delay_list(value: str) -> list[int]:
    return [int(chunk.strip()) for chunk in value.split(",") if chunk.strip()]


def evaluate_delay(
    *,
    dataset: str,
    entry_low: int,
    entry_high: int,
    stop_threshold: float,
    delay_seconds: int,
    include_estimated_exit_fee: bool,
) -> dict[str, Any]:
    frame = build_exit_frame(
        dataset=dataset,
        entry_low=entry_low,
        entry_high=entry_high,
        stop_threshold=stop_threshold,
        delay_seconds=delay_seconds,
        include_estimated_exit_fee=include_estimated_exit_fee,
    )
    if frame.empty:
        return {
            "delay_seconds": delay_seconds,
            "case_count": 0,
            "error": "no_rows",
        }
    frame["day"] = frame["market"].str.extract(r"(\d{2}[A-Z]{3}\d{2})")[0]
    masks = named_policy_masks(frame)
    policy_summaries = {
        name: summarize_mask(frame, mask, label=name)
        for name, mask in masks.items()
    }
    ranked = sorted(
        policy_summaries.values(),
        key=lambda row: (
            float(row["delta_dollars"]),
            float(row["avg_positive_delta"] or 0.0),
            -float(row["avg_negative_delta_abs"] or 0.0),
            int(row["count"]),
        ),
        reverse=True,
    )
    return {
        "delay_seconds": delay_seconds,
        "case_count": int(len(frame)),
        "baseline_actual_net_pnl_dollars": round(float(frame["net_pnl_dollars"].sum()), 4),
        "policy_summaries": policy_summaries,
        "top_policies_by_delta": ranked[:8],
        "walkforward_select_best_curated_policy": walkforward_select(frame, masks),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Sweep post-entry exit candidate policies across supervisor delay timings.")
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--entry-low", type=int, default=89)
    parser.add_argument("--entry-high", type=int, default=92)
    parser.add_argument("--stop-threshold", type=float, default=70.0)
    parser.add_argument("--delays", default="45,60,75,90,105,120,150,180")
    parser.add_argument("--include-estimated-exit-fee", action="store_true")
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    delay_values = parse_delay_list(str(args.delays))
    results = [
        evaluate_delay(
            dataset=str(args.dataset),
            entry_low=int(args.entry_low),
            entry_high=int(args.entry_high),
            stop_threshold=float(args.stop_threshold),
            delay_seconds=delay,
            include_estimated_exit_fee=bool(args.include_estimated_exit_fee),
        )
        for delay in delay_values
    ]

    payload = {
        "summary": {
            "dataset": str(args.dataset),
            "entry_low": int(args.entry_low),
            "entry_high": int(args.entry_high),
            "stop_threshold": float(args.stop_threshold),
            "delays": delay_values,
            "include_estimated_exit_fee": bool(args.include_estimated_exit_fee),
        },
        "results": results,
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved post-entry exit delay sweep to {output_path}")
    for result in results:
        if result.get("error"):
            print(result["delay_seconds"], result["error"])
            continue
        best = result["top_policies_by_delta"][0]
        wf = result["walkforward_select_best_curated_policy"]
        print(
            f"delay={result['delay_seconds']}s",
            f"cases={result['case_count']}",
            f"best={best['label']}",
            f"best_delta={best['delta_dollars']}",
            f"wf_delta={wf['aggregate_delta_dollars']}",
        )


if __name__ == "__main__":
    main()
