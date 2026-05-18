from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from probe_edge_rules import build_case_frame

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "daily_lease_rule_scan_latest.json"


def blocked_days_from_prev_net(case_df: pd.DataFrame, threshold: float) -> set[str]:
    daily = (
        case_df.groupby("entry_date", dropna=False)
        .agg(net=("next_pnl", "sum"))
        .reset_index()
        .sort_values("entry_date")
        .reset_index(drop=True)
    )
    blocked_days: set[str] = set()
    for idx in range(1, len(daily)):
        if float(daily.loc[idx - 1, "net"]) >= threshold:
            blocked_days.add(str(daily.loc[idx, "entry_date"]))
    return blocked_days


def market_rule_masks(frame: pd.DataFrame) -> dict[str, pd.Series]:
    return {
        "baseline": pd.Series(True, index=frame.index),
        "pnl_only_3": ~(frame["pnl4"] >= 3.0),
        "pnl_only_2_5": ~(frame["pnl4"] >= 2.5),
        "old_fixed": ~(((frame["pnl4"] >= 3.0) | (frame["stale_per_signal4"] >= 1.5)) & ~(frame["exits4"] >= 3)),
        "tuned_fixed": ~(((frame["pnl4"] >= 2.5) | (frame["stale_per_signal4"] >= 1.25)) & ~(frame["exits4"] >= 3)),
    }


def summarize_partition(frame: pd.DataFrame, keep_mask: pd.Series) -> dict[str, float | int]:
    kept = frame.loc[keep_mask].copy()
    return {
        "trades": int(len(kept)),
        "net_pnl_dollars": round(float(kept["next_pnl"].sum()), 4) if not kept.empty else 0.0,
        "win_rate": round(float((kept["next_pnl"] > 0).mean()), 4) if not kept.empty else 0.0,
        "avg_pnl_dollars": round(float(kept["next_pnl"].mean()), 4) if not kept.empty else 0.0,
    }


def evaluate_dataset(dataset_tag: str) -> dict[str, Any]:
    case_df = build_case_frame(dataset_tag).sort_values(["entry_date", "market"]).reset_index(drop=True)
    if case_df.empty:
        raise RuntimeError(f"No cases found for dataset {dataset_tag}")

    held_dates = sorted(str(value) for value in case_df["entry_date"].dropna().unique())[3:]
    held_df = case_df[case_df["entry_date"].isin(held_dates)].copy()
    if held_df.empty:
        raise RuntimeError(f"No held-out dates found for dataset {dataset_tag}")

    baseline = summarize_partition(held_df, pd.Series(True, index=held_df.index))
    market_masks = market_rule_masks(held_df)
    rows: list[dict[str, Any]] = []

    for day_threshold in [None, 2.0, 5.0, 10.0, 15.0]:
        blocked_days = set() if day_threshold is None else blocked_days_from_prev_net(case_df, day_threshold)
        day_mask = ~held_df["entry_date"].isin(blocked_days)
        for name, market_mask in market_masks.items():
            keep_mask = day_mask & market_mask
            summary = summarize_partition(held_df, keep_mask)
            rows.append(
                {
                    "day_threshold": day_threshold,
                    "blocked_days": sorted(blocked_days),
                    "blocked_day_count": int(len(blocked_days)),
                    "market_rule": name,
                    **summary,
                    "net_delta_dollars": round(float(summary["net_pnl_dollars"]) - float(baseline["net_pnl_dollars"]), 4),
                }
            )

    ranked = sorted(
        rows,
        key=lambda rec: (
            float(rec["net_pnl_dollars"]),
            float(rec["win_rate"]),
            -int(rec["blocked_day_count"]),
        ),
        reverse=True,
    )
    return {
        "dataset_tag": dataset_tag,
        "case_count": int(len(case_df)),
        "held_out_dates": held_dates,
        "baseline_held_out": baseline,
        "top_combinations": ranked[:20],
        "all_combinations": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan simple day-level lease and intraday block combinations.")
    parser.add_argument("--datasets", nargs="+", default=["live_90_78", "live_90_70"])
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    payload = {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "datasets": [evaluate_dataset(tag) for tag in args.datasets],
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Saved daily lease scan to {output_path}")
    for dataset in payload["datasets"]:
        best = dataset["top_combinations"][0]
        print(
            dataset["dataset_tag"],
            f"baseline={dataset['baseline_held_out']['net_pnl_dollars']:.2f}",
            f"best={best['net_pnl_dollars']:.2f}",
            f"rule={best['market_rule']}",
            f"day_threshold={best['day_threshold']}",
        )


if __name__ == "__main__":
    main()
