from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable

import pandas as pd

from analyze_post_entry_rule_mining import build_row
from probe_truffle_two_stage_predictor import build_cases

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "ambiguity_policy_eval_latest.json"


def load_case_frame(*, dataset: str, entry_low: int, entry_high: int, stop_threshold: float, delay_seconds: int) -> pd.DataFrame:
    cases = build_cases(dataset, entry_low=entry_low, entry_high=entry_high, stop_threshold=stop_threshold)
    frame = pd.DataFrame([build_row(case, seconds=delay_seconds) for case in cases])
    trades = pd.read_csv(ROOT / "stats" / dataset / "trades.csv")
    trades = trades[trades["entry_trigger_cents"].between(entry_low, entry_high)].copy()
    trades = (
        trades.sort_values(["market", "entry_ts"])
        .drop_duplicates(subset=["market"], keep="last")[["market", "net_pnl_dollars", "gross_pnl_dollars", "entry_trigger_cents"]]
        .copy()
    )
    frame = frame.merge(trades, on="market", how="left")
    frame["net_pnl_dollars"] = pd.to_numeric(frame["net_pnl_dollars"], errors="coerce").fillna(0.0)
    frame["not_good_trade"] = (1 - pd.to_numeric(frame["good_trade"], errors="coerce").fillna(0).astype(int)).astype(int)
    frame["net_negative"] = (frame["net_pnl_dollars"] < 0).astype(int)
    return frame


def summarize_mask(frame: pd.DataFrame, mask: pd.Series, *, label: str) -> dict[str, float | int | str]:
    subset = frame.loc[mask].copy()
    n = int(len(subset))
    losers = int(subset["settlement_loser"].sum())
    bad_trades = int(subset["not_good_trade"].sum())
    net_negative = int(subset["net_negative"].sum())
    winners = n - losers
    stop_hits = int(subset["stop_hit"].sum())
    net_pnl = float(subset["net_pnl_dollars"].sum())
    baseline_net = float(frame["net_pnl_dollars"].sum())
    negative_pnl_subset = subset.loc[subset["net_pnl_dollars"] < 0, "net_pnl_dollars"]
    positive_pnl_subset = subset.loc[subset["net_pnl_dollars"] > 0, "net_pnl_dollars"]
    return {
        "label": label,
        "count": n,
        "losers": losers,
        "winners": winners,
        "stop_hits": stop_hits,
        "bad_trades": bad_trades,
        "net_negative_count": net_negative,
        "precision_loser": round(losers / n, 4) if n else None,
        "recall_loser": round(losers / max(1, int(frame["settlement_loser"].sum())), 4),
        "precision_bad_trade": round(bad_trades / n, 4) if n else None,
        "recall_bad_trade": round(bad_trades / max(1, int(frame["not_good_trade"].sum())), 4),
        "precision_net_negative": round(net_negative / n, 4) if n else None,
        "recall_net_negative": round(net_negative / max(1, int(frame["net_negative"].sum())), 4),
        "net_pnl_dollars": round(net_pnl, 4),
        "avg_negative_pnl_abs": round(float((-negative_pnl_subset).mean()), 4) if len(negative_pnl_subset) else None,
        "avg_positive_pnl": round(float(positive_pnl_subset.mean()), 4) if len(positive_pnl_subset) else None,
        "delta_if_all_blocked_dollars": round(-net_pnl, 4),
        "new_net_if_all_blocked_dollars": round(baseline_net - net_pnl, 4),
    }


def evaluate_policy(
    frame: pd.DataFrame,
    *,
    hard_red_mask: pd.Series,
    ambiguity_mask: pd.Series,
    policy_name: str,
) -> dict[str, object]:
    hard_red_mask = hard_red_mask.fillna(False).astype(bool)
    raw_ambiguity_mask = ambiguity_mask.fillna(False).astype(bool)
    ambiguity_mask = raw_ambiguity_mask & (~hard_red_mask)

    baseline_net = float(frame["net_pnl_dollars"].sum())
    hard_red_summary = summarize_mask(frame, hard_red_mask, label="hard_red")
    raw_ambiguity_summary = summarize_mask(frame, raw_ambiguity_mask, label="raw_ambiguity")
    ambiguity_summary = summarize_mask(frame, ambiguity_mask, label="ambiguity")

    # If we blocked all ambiguity cases too.
    blocked_all_mask = hard_red_mask | ambiguity_mask
    blocked_all_summary = summarize_mask(frame, blocked_all_mask, label="hard_red_plus_block_all_ambiguity")

    # Upper bound if a perfect ambiguity model blocks only the losers in ambiguity slice.
    perfect_ambiguity_mask = ambiguity_mask & (frame["settlement_loser"] == 1)
    perfect_ambiguity_summary = summarize_mask(frame, perfect_ambiguity_mask, label="perfect_ambiguity_blocks_only_losers")

    return {
        "policy_name": policy_name,
        "baseline_case_count": int(len(frame)),
        "baseline_net_pnl_dollars": round(baseline_net, 4),
        "hard_red": hard_red_summary,
        "raw_ambiguity": raw_ambiguity_summary,
        "hard_red_overlap_count": int((raw_ambiguity_mask & hard_red_mask).sum()),
        "ambiguity": ambiguity_summary,
        "hard_red_plus_block_all_ambiguity": blocked_all_summary,
        "upper_bound_if_ambiguity_perfect": {
            "count": int(hard_red_mask.sum()) + int(perfect_ambiguity_mask.sum()),
            "blocked_losers": int(frame.loc[hard_red_mask | perfect_ambiguity_mask, "settlement_loser"].sum()),
            "new_net_dollars": round(
                baseline_net - float(frame.loc[hard_red_mask | perfect_ambiguity_mask, "net_pnl_dollars"].sum()),
                4,
            ),
            "delta_dollars": round(
                -float(frame.loc[hard_red_mask | perfect_ambiguity_mask, "net_pnl_dollars"].sum()),
                4,
            ),
            "ambiguity_loser_only_summary": perfect_ambiguity_summary,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate deterministic hard-red plus ambiguity-only Truffle policy candidates.")
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--entry-low", type=int, default=89)
    parser.add_argument("--entry-high", type=int, default=92)
    parser.add_argument("--stop-threshold", type=float, default=70.0)
    parser.add_argument("--delay-seconds", type=int, default=90)
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    frame = load_case_frame(
        dataset=str(args.dataset),
        entry_low=int(args.entry_low),
        entry_high=int(args.entry_high),
        stop_threshold=float(args.stop_threshold),
        delay_seconds=int(args.delay_seconds),
    )

    hard_red = frame["current_strength"] == "weak"

    policies: dict[str, pd.Series] = {
        "no_strong_light_weak_below_or_near": (
            (frame["side"] == "NO")
            & (frame["current_strength"] == "strong")
            & (frame["damage_state"] == "light")
            & (frame["rebound_state"] == "weak")
            & frame["current_vs_entry_state"].isin(["below_entry", "near_entry"])
        ),
        "no_rebound_weak_strong_runup_up30": (
            (frame["side"] == "NO")
            & (frame["rebound_state"] == "weak")
            & (frame["open_to_entry_runup"] == "strong_runup")
            & (frame["last30_move_state"] == "up")
        ),
        "heavy_top_mid_neutral_macd": (
            (frame["damage_state"] == "heavy")
            & (frame["entry_location_in_range"] == "top_of_range")
            & (frame["entry_timing_state"] == "mid_entry")
            & (frame["btc_macd_state"] == "neutral")
        ),
        "rebound_weak_tight_mid_flat_hist": (
            (frame["rebound_state"] == "weak")
            & (frame["spread_state"] == "tight")
            & (frame["entry_timing_state"] == "mid_entry")
            & (frame["btc_macd_hist_state"] == "flat")
        ),
    }

    output = {
        "summary": {
            "dataset": str(args.dataset),
            "delay_seconds": int(args.delay_seconds),
            "case_count": int(len(frame)),
            "settlement_loser_count": int(frame["settlement_loser"].sum()),
            "stop_hit_count": int(frame["stop_hit"].sum()),
            "baseline_net_pnl_dollars": round(float(frame["net_pnl_dollars"].sum()), 4),
        },
        "policies": [
            evaluate_policy(frame, hard_red_mask=hard_red, ambiguity_mask=mask, policy_name=name)
            for name, mask in policies.items()
        ],
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(f"Saved ambiguity policy evaluation to {output_path}")
    print(json.dumps(output["summary"], indent=2))
    for policy in output["policies"]:
        print(json.dumps(policy, indent=2))


if __name__ == "__main__":
    main()
