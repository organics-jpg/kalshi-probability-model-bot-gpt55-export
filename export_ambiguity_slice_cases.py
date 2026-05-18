from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from probe_truffle_signal_tool_variants import compact_indicator_payload
from probe_truffle_single_call_indicator_variants import build_payload
from probe_truffle_two_stage_predictor import build_cases

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "ambiguity_slice_cases_latest.json"


def build_case_payloads(*, dataset: str, entry_low: int, entry_high: int, stop_threshold: float, delay_seconds: int) -> pd.DataFrame:
    cases = build_cases(dataset, entry_low=entry_low, entry_high=entry_high, stop_threshold=stop_threshold)
    rows: list[dict[str, object]] = []
    for case in cases:
        payload = compact_indicator_payload(build_payload(case, seconds=delay_seconds, include_indicators=True), indicator_mode="states_only")
        post = payload.get("post_entry", {})
        pre = payload.get("pre_entry", {})
        tech = payload.get("technicals", {}).get("post_entry", {})
        rows.append(
            {
                "market": case.market,
                "bucket": case.bucket,
                "settlement_loser": int(not case.settlement_win),
                "stop_hit": int(case.stop_hit_after_entry),
                "good_trade": int(case.actual_good_trade),
                "side": payload.get("side"),
                "current_strength": post.get("current_strength"),
                "damage_state": post.get("damage_state"),
                "rebound_state": post.get("rebound_state"),
                "current_vs_entry_state": post.get("current_vs_entry_state"),
                "spread_state": post.get("spread_state"),
                "entry_location_in_range": pre.get("entry_location_in_range"),
                "entry_pressure_state": pre.get("entry_pressure_state"),
                "entry_timing_state": pre.get("entry_timing_state"),
                "open_to_entry_runup": pre.get("open_to_entry_runup"),
                "last30_move_state": pre.get("last30_move_state"),
                "last60_move_state": pre.get("last60_move_state"),
                "volatility_state": pre.get("volatility_state"),
                "btc_rsi14_state": tech.get("rsi14_state"),
                "btc_rsi14_slope_state": tech.get("rsi14_slope_state"),
                "btc_macd_state": tech.get("macd_state"),
                "btc_macd_hist_state": tech.get("macd_hist_state"),
                "btc_price_vs_ema21_state": tech.get("price_vs_ema21_state"),
                "payload": payload,
            }
        )
    frame = pd.DataFrame(rows)
    trades = pd.read_csv(ROOT / "stats" / dataset / "trades.csv")
    trades = trades[trades["entry_trigger_cents"].between(entry_low, entry_high)].copy()
    trades = trades.sort_values(["market", "entry_ts"]).drop_duplicates(subset=["market"], keep="last")
    frame = frame.merge(
        trades[["market", "net_pnl_dollars", "gross_pnl_dollars", "entry_fill_cents_used", "entry_trigger_cents"]],
        on="market",
        how="left",
    )
    frame["net_pnl_dollars"] = pd.to_numeric(frame["net_pnl_dollars"], errors="coerce").fillna(0.0)
    frame["net_negative"] = (frame["net_pnl_dollars"] < 0).astype(int)
    return frame


def main() -> None:
    parser = argparse.ArgumentParser(description="Export high-value ambiguity slices for later Truffle evaluation.")
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--entry-low", type=int, default=89)
    parser.add_argument("--entry-high", type=int, default=92)
    parser.add_argument("--stop-threshold", type=float, default=70.0)
    parser.add_argument("--delay-seconds", type=int, default=90)
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    frame = build_case_payloads(
        dataset=str(args.dataset),
        entry_low=int(args.entry_low),
        entry_high=int(args.entry_high),
        stop_threshold=float(args.stop_threshold),
        delay_seconds=int(args.delay_seconds),
    )

    hard_red_mask = frame["current_strength"] == "weak"
    raw_slices = {
        "hard_red_weak_strength": hard_red_mask,
        "ambiguity_no_strong_light_weak_below_or_near": (
            (frame["side"] == "NO")
            & (frame["current_strength"] == "strong")
            & (frame["damage_state"] == "light")
            & (frame["rebound_state"] == "weak")
            & frame["current_vs_entry_state"].isin(["below_entry", "near_entry"])
        ),
        "ambiguity_no_rebound_weak_strong_runup_up30": (
            (frame["side"] == "NO")
            & (frame["rebound_state"] == "weak")
            & (frame["open_to_entry_runup"] == "strong_runup")
            & (frame["last30_move_state"] == "up")
        ),
        "ambiguity_rebound_weak_tight_mid_flat_hist": (
            (frame["rebound_state"] == "weak")
            & (frame["spread_state"] == "tight")
            & (frame["entry_timing_state"] == "mid_entry")
            & (frame["btc_macd_hist_state"] == "flat")
        ),
    }

    export = {
        "summary": {
            "dataset": str(args.dataset),
            "delay_seconds": int(args.delay_seconds),
            "case_count": int(len(frame)),
        },
        "slices": {},
    }

    for name, raw_mask in raw_slices.items():
        mask = raw_mask if name == "hard_red_weak_strength" else (raw_mask & ~hard_red_mask)
        subset = frame.loc[mask].copy()
        subset_records = subset[
            [
                "market",
                "bucket",
                "side",
                "settlement_loser",
                "stop_hit",
                "good_trade",
                "net_negative",
                "net_pnl_dollars",
                "current_strength",
                "damage_state",
                "rebound_state",
                "current_vs_entry_state",
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
                "payload",
            ]
        ].to_dict(orient="records")
        export["slices"][name] = {
            "slice_mode": "hard_red" if name == "hard_red_weak_strength" else "ambiguity_only_excluding_hard_red",
            "raw_count": int(raw_mask.sum()),
            "hard_red_overlap_count": int((raw_mask & hard_red_mask).sum()) if name != "hard_red_weak_strength" else 0,
            "count": int(len(subset)),
            "settlement_losers": int(subset["settlement_loser"].sum()),
            "bad_trades": int((1 - subset["good_trade"]).sum()),
            "net_negative_count": int(subset["net_negative"].sum()),
            "net_pnl_dollars": round(float(subset["net_pnl_dollars"].sum()), 4),
            "rows": subset_records,
        }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(export, indent=2), encoding="utf-8")

    print(f"Saved ambiguity slice export to {output_path}")
    print(json.dumps(export["summary"], indent=2))
    for name, payload in export["slices"].items():
        print(name, payload["count"], payload["settlement_losers"], payload["net_pnl_dollars"])


if __name__ == "__main__":
    main()
