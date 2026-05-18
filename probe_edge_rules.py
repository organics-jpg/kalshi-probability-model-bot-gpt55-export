from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pandas as pd

from probe_truffle_historical_replay import build_ordered_market_records

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "edge_rule_scan_latest.json"


@dataclass(frozen=True)
class RuleSpec:
    name: str
    description: str


def build_case_frame(dataset_tag: str) -> pd.DataFrame:
    records = build_ordered_market_records(dataset_tag)
    rows: list[dict[str, object]] = []
    for idx, record in enumerate(records):
        if not record.traded or idx < 4:
            continue
        recent4 = records[idx - 4 : idx]
        traded_recent4 = [row for row in recent4 if row.traded]
        latency_samples = [value for row in recent4 for value in row.submit_latency_samples_ms]
        rows.append(
            {
                "market": record.market,
                "entry_date": (
                    pd.Timestamp(record.market_close_time).tz_convert("America/New_York").strftime("%Y-%m-%d")
                    if record.market_close_time
                    else ""
                ),
                "next_pnl": float(record.pnl_dollars),
                "wins4": int(sum(1 for row in traded_recent4 if row.pnl_dollars > 0)),
                "exits4": int(sum(1 for row in traded_recent4 if row.outcome_type == "exit")),
                "pnl4": round(float(sum(row.pnl_dollars for row in traded_recent4)), 4),
                "traded4": int(len(traded_recent4)),
                "pf4": round(
                    float(sum(1 for row in traded_recent4 if row.pnl_dollars > 0) / max(1, len(traded_recent4))),
                    4,
                ),
                "lat95": round(float(pd.Series(latency_samples).quantile(0.95)), 4) if latency_samples else 0.0,
                "ioc4": int(sum(row.ioc_zero_fill_count for row in recent4)),
                "stale4": int(sum(row.stale_book_deferral_count for row in recent4)),
                "signal_sum4": int(sum(row.signal_count for row in recent4)),
            }
        )
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    frame["stale_per_signal4"] = frame["stale4"] / frame["signal_sum4"].clip(lower=1)
    return frame


def candidate_rules() -> dict[str, tuple[RuleSpec, Callable[[pd.DataFrame], pd.Series]]]:
    return {
        "baseline": (
            RuleSpec("baseline", "Always trade the next qualifying market."),
            lambda part: pd.Series(True, index=part.index),
        ),
        "block_win3": (
            RuleSpec("block_win3", "Block after 3 or more winning trades in the recent 4-market window."),
            lambda part: part["wins4"] < 3,
        ),
        "block_pnl3": (
            RuleSpec("block_pnl3", "Block when recent 4-market realized PnL is at least $3."),
            lambda part: part["pnl4"] < 3.0,
        ),
        "block_staleps15": (
            RuleSpec("block_staleps15", "Block when stale deferrals exceed 1.5 per signal in the recent 4-market window."),
            lambda part: part["stale_per_signal4"] < 1.5,
        ),
        "block_pnl3_or_staleps15": (
            RuleSpec(
                "block_pnl3_or_staleps15",
                "Block when recent realized PnL is hot or stale deferrals per signal are extreme.",
            ),
            lambda part: ~((part["pnl4"] >= 3.0) | (part["stale_per_signal4"] >= 1.5)),
        ),
        "block_pnl3_or_staleps15_unless_exit3": (
            RuleSpec(
                "block_pnl3_or_staleps15_unless_exit3",
                "Same as hot-or-stale block, but do not block when 3 or more recent exits suggest a washout.",
            ),
            lambda part: ~(((part["pnl4"] >= 3.0) | (part["stale_per_signal4"] >= 1.5)) & ~(part["exits4"] >= 3)),
        ),
        "block_win3_or_lat101": (
            RuleSpec(
                "block_win3_or_lat101",
                "Block after hot streaks or when recent submit latency is at least 101ms.",
            ),
            lambda part: ~((part["wins4"] >= 3) | (part["lat95"] >= 101.0)),
        ),
    }


def summarize_partition(part: pd.DataFrame, keep_mask: pd.Series) -> dict[str, float | int]:
    kept = part.loc[keep_mask].copy()
    net = float(kept["next_pnl"].sum()) if not kept.empty else 0.0
    return {
        "trades": int(keep_mask.sum()),
        "net_pnl_dollars": round(net, 4),
        "win_rate": round(float((kept["next_pnl"] > 0).mean()), 4) if not kept.empty else 0.0,
        "avg_pnl_dollars": round(float(kept["next_pnl"].mean()), 4) if not kept.empty else 0.0,
    }


def evaluate_rules(case_df: pd.DataFrame) -> dict[str, object]:
    dates = sorted(str(value) for value in case_df["entry_date"].dropna().unique())
    half_split = len(dates) // 2
    first_half_dates = set(dates[:half_split])
    second_half_dates = set(dates[half_split:])
    folds = [dates[i::4] for i in range(4)]

    output: dict[str, object] = {
        "case_count": int(len(case_df)),
        "unique_days": int(len(dates)),
        "first_half_dates": len(first_half_dates),
        "second_half_dates": len(second_half_dates),
        "rules": {},
    }

    for key, (spec, predicate) in candidate_rules().items():
        first_half = case_df[case_df["entry_date"].isin(first_half_dates)].copy()
        second_half = case_df[case_df["entry_date"].isin(second_half_dates)].copy()
        first_half_mask = predicate(first_half)
        second_half_mask = predicate(second_half)
        fold_summaries: list[dict[str, object]] = []
        fold_nets: list[float] = []
        for idx, fold_dates in enumerate(folds, start=1):
            fold_frame = case_df[case_df["entry_date"].isin(fold_dates)].copy()
            fold_mask = predicate(fold_frame)
            summary = summarize_partition(fold_frame, fold_mask)
            summary["fold_index"] = idx
            summary["fold_day_count"] = len(fold_dates)
            fold_summaries.append(summary)
            fold_nets.append(float(summary["net_pnl_dollars"]))
        output["rules"][key] = {
            "name": spec.name,
            "description": spec.description,
            "first_half": summarize_partition(first_half, first_half_mask),
            "second_half": summarize_partition(second_half, second_half_mask),
            "all_days": summarize_partition(case_df, predicate(case_df)),
            "folds": fold_summaries,
            "avg_fold_net_pnl_dollars": round(sum(fold_nets) / max(1, len(fold_nets)), 4),
            "min_fold_net_pnl_dollars": round(min(fold_nets), 4) if fold_nets else 0.0,
        }
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan simple deterministic edge rules over recent-window 90_78 cases.")
    parser.add_argument("--dataset-tag", default="live_90_78")
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    case_df = build_case_frame(args.dataset_tag)
    if case_df.empty:
        raise RuntimeError(f"No cases found for dataset {args.dataset_tag}")

    payload = {
        "dataset_tag": args.dataset_tag,
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        **evaluate_rules(case_df),
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Saved edge rule scan to {output_path}")
    for key, result in payload["rules"].items():
        all_days = result["all_days"]
        print(
            f"{key}: trades={all_days['trades']} net={all_days['net_pnl_dollars']:.2f} "
            f"win_rate={all_days['win_rate']:.2%} min_fold={result['min_fold_net_pnl_dollars']:.2f}"
        )


if __name__ == "__main__":
    main()
