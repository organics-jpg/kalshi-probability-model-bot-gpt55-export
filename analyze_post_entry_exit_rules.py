from __future__ import annotations

import argparse
import json
from itertools import combinations, product
from pathlib import Path
from typing import Any

import pandas as pd

from evaluate_ambiguity_policy import load_case_frame
from probe_truffle_two_stage_predictor import build_cases, load_feature_frame

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "post_entry_exit_rule_analysis_latest.json"


def estimated_order_fee_cents(price_cents: float, count: int) -> int:
    bounded_price = max(1, min(99, int(round(float(price_cents)))))
    numerator = 7 * int(count) * bounded_price * (100 - bounded_price)
    return max(1, (numerator + 9999) // 10000)


def build_exit_frame(
    *,
    dataset: str,
    entry_low: int,
    entry_high: int,
    stop_threshold: float,
    delay_seconds: int,
    include_estimated_exit_fee: bool,
) -> pd.DataFrame:
    frame = load_case_frame(
        dataset=dataset,
        entry_low=entry_low,
        entry_high=entry_high,
        stop_threshold=stop_threshold,
        delay_seconds=delay_seconds,
    ).copy()

    trades = pd.read_csv(ROOT / "stats" / dataset / "trades.csv")
    trades = trades[trades["entry_trigger_cents"].between(entry_low, entry_high)].copy()
    trades = trades.sort_values(["market", "entry_ts"]).drop_duplicates(subset=["market"], keep="last")
    trades = trades[
        [
            "market",
            "qty",
            "entry_fill_cents_used",
            "entry_trigger_cents",
            "entry_fee_cents",
        ]
    ].copy()

    cases = build_cases(dataset, entry_low=entry_low, entry_high=entry_high, stop_threshold=stop_threshold)
    exit_rows: list[dict[str, Any]] = []
    for case in cases:
        feature_df = load_feature_frame(case.feature_path)
        yes_side = case.side == "yes"
        bid_col = "yes_bid_cents" if yes_side else "no_bid_cents"
        series = feature_df[["ts", bid_col]].rename(columns={bid_col: "same_bid"}).dropna().copy()
        series = series[series["ts"] >= case.entry_dt_local].copy()
        if series.empty:
            continue
        horizon = case.entry_dt_local + pd.Timedelta(seconds=delay_seconds)
        early = series[series["ts"] <= horizon].copy()
        if early.empty:
            continue
        exit_rows.append(
            {
                "market": case.market,
                "same_bid_at_delay": float(early.iloc[-1]["same_bid"]),
            }
        )

    exit_frame = pd.DataFrame(exit_rows)
    if exit_frame.empty:
        return frame.iloc[0:0].copy()

    frame = frame.merge(trades, on="market", how="left")
    frame = frame.merge(exit_frame, on="market", how="left")
    frame["qty"] = pd.to_numeric(frame["qty"], errors="coerce").fillna(10.0)
    frame["entry_fill_cents"] = pd.to_numeric(frame["entry_fill_cents_used"], errors="coerce")
    trigger_columns = [column for column in ("entry_trigger_cents", "entry_trigger_cents_x", "entry_trigger_cents_y") if column in frame.columns]
    trigger_fallback = (
        frame[trigger_columns].bfill(axis=1).iloc[:, 0]
        if trigger_columns
        else pd.Series(pd.NA, index=frame.index, dtype="object")
    )
    frame["entry_fill_cents"] = frame["entry_fill_cents"].fillna(pd.to_numeric(trigger_fallback, errors="coerce")).fillna(90.0)
    frame["entry_fee_cents"] = pd.to_numeric(frame["entry_fee_cents"], errors="coerce").fillna(0.0)
    frame["same_bid_at_delay"] = pd.to_numeric(frame["same_bid_at_delay"], errors="coerce")
    frame = frame.dropna(subset=["same_bid_at_delay"]).copy()

    frame["exit_delay_gross_pnl_dollars"] = (
        frame["qty"] * (frame["same_bid_at_delay"] - frame["entry_fill_cents"]) / 100.0
    )
    if include_estimated_exit_fee:
        frame["exit_delay_fee_cents"] = frame.apply(
            lambda row: estimated_order_fee_cents(float(row["same_bid_at_delay"]), int(row["qty"])),
            axis=1,
        )
    else:
        frame["exit_delay_fee_cents"] = 0
    frame["exit_delay_net_pnl_dollars"] = (
        frame["exit_delay_gross_pnl_dollars"]
        - ((frame["entry_fee_cents"] + frame["exit_delay_fee_cents"]) / 100.0)
    ).round(4)
    frame["exit_delay_improves_trade"] = (frame["exit_delay_net_pnl_dollars"] > frame["net_pnl_dollars"]).astype(int)
    frame["exit_delay_harms_trade"] = (frame["exit_delay_net_pnl_dollars"] < frame["net_pnl_dollars"]).astype(int)
    return frame


def summarize_exit_mask(frame: pd.DataFrame, mask: pd.Series, *, label: str) -> dict[str, Any]:
    subset = frame.loc[mask].copy()
    n = int(len(subset))
    deltas = subset["exit_delay_net_pnl_dollars"] - subset["net_pnl_dollars"]
    improved = int((deltas > 0).sum())
    harmed = int((deltas < 0).sum())
    unchanged = n - improved - harmed
    return {
        "label": label,
        "count": n,
        "actual_net_pnl_dollars": round(float(subset["net_pnl_dollars"].sum()), 4),
        "exit_delay_net_pnl_dollars": round(float(subset["exit_delay_net_pnl_dollars"].sum()), 4),
        "delta_dollars": round(float(deltas.sum()), 4),
        "improved_trade_count": improved,
        "harmed_trade_count": harmed,
        "unchanged_trade_count": unchanged,
        "improvement_rate": round(improved / n, 4) if n else None,
        "harm_rate": round(harmed / n, 4) if n else None,
        "avg_improvement_when_better": round(float(deltas[deltas > 0].mean()), 4) if improved else None,
        "avg_harm_when_worse": round(float((-deltas[deltas < 0]).mean()), 4) if harmed else None,
    }


def candidate_policy_masks(frame: pd.DataFrame) -> dict[str, pd.Series]:
    return {
        "hard_red_weak_strength": frame["current_strength"] == "weak",
        "recovering_strength": frame["current_strength"] == "recovering",
        "hard_red_or_recovering": frame["current_strength"].isin(["weak", "recovering"]),
        "no_strong_light_weak_below_or_near": (
            (frame["side"] == "NO")
            & (frame["current_strength"] == "strong")
            & (frame["damage_state"] == "light")
            & (frame["rebound_state"] == "weak")
            & frame["current_vs_entry_state"].isin(["below_entry", "near_entry"])
        ),
        "damage_heavy_rsi_slope_flat": (
            (frame["damage_state"] == "heavy")
            & (frame["btc_rsi14_slope_state"] == "flat")
        ),
        "recovering_well_below_entry": (
            (frame["current_strength"] == "recovering")
            & (frame["current_vs_entry_state"] == "well_below_entry")
        ),
    }


def search_top_exit_rules(frame: pd.DataFrame, *, min_n: int, max_rules: int) -> list[dict[str, Any]]:
    features = [
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
    candidate_values = {
        feature: [value for value, count in frame[feature].dropna().value_counts().items() if int(count) >= min_n]
        for feature in features
    }

    rows: list[dict[str, Any]] = []
    for width in (1, 2, 3):
        for chosen_features in combinations(features, width):
            value_lists = [candidate_values[feature] for feature in chosen_features]
            if not all(value_lists):
                continue
            for combo in product(*value_lists):
                mask = pd.Series(True, index=frame.index)
                parts: list[str] = []
                for feature, value in zip(chosen_features, combo):
                    mask &= frame[feature] == value
                    parts.append(f"{feature}={value}")
                if int(mask.sum()) < min_n:
                    continue
                summary = summarize_exit_mask(frame, mask, label="candidate")
                rows.append(
                    {
                        "rule": " & ".join(parts),
                        **summary,
                    }
                )

    rows.sort(
        key=lambda item: (
            float(item["delta_dollars"]),
            float(item["improvement_rate"] or 0.0),
            -float(item["harm_rate"] or 0.0),
            int(item["count"]),
        ),
        reverse=True,
    )
    return rows[:max_rules]


def main() -> None:
    parser = argparse.ArgumentParser(description="Score compact 90-second post-entry exit rules against actual trade outcomes.")
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--entry-low", type=int, default=89)
    parser.add_argument("--entry-high", type=int, default=92)
    parser.add_argument("--stop-threshold", type=float, default=70.0)
    parser.add_argument("--delay-seconds", type=int, default=90)
    parser.add_argument("--min-n", type=int, default=3)
    parser.add_argument("--max-rules", type=int, default=25)
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
        raise RuntimeError("No exit-delay rows were available for analysis.")

    named_policies = {
        name: summarize_exit_mask(frame, mask.fillna(False).astype(bool), label=name)
        for name, mask in candidate_policy_masks(frame).items()
    }

    payload = {
        "summary": {
            "dataset": str(args.dataset),
            "delay_seconds": int(args.delay_seconds),
            "case_count": int(len(frame)),
            "baseline_actual_net_pnl_dollars": round(float(frame["net_pnl_dollars"].sum()), 4),
            "baseline_exit_delay_net_pnl_dollars": round(float(frame["exit_delay_net_pnl_dollars"].sum()), 4),
            "include_estimated_exit_fee": bool(args.include_estimated_exit_fee),
        },
        "named_policies": named_policies,
        "top_exit_rules": search_top_exit_rules(
            frame,
            min_n=int(args.min_n),
            max_rules=int(args.max_rules),
        ),
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved post-entry exit rule analysis to {output_path}")
    print(json.dumps(payload["summary"], indent=2))
    for name, summary in payload["named_policies"].items():
        print(name, json.dumps(summary, sort_keys=True))
    print("Top exit rules:")
    for row in payload["top_exit_rules"][:10]:
        print(
            row["rule"],
            "count=",
            row["count"],
            "delta=",
            row["delta_dollars"],
            "improve_rate=",
            row["improvement_rate"],
            "harm_rate=",
            row["harm_rate"],
        )


if __name__ == "__main__":
    main()
