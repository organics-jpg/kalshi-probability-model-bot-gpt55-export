from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path
from typing import Any

import pandas as pd

from probe_truffle_signal_tool_variants import compact_indicator_payload
from probe_truffle_single_call_indicator_variants import build_payload
from probe_truffle_two_stage_predictor import build_cases

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "post_entry_rule_mining_latest.json"


def btc_support_score(side: str, snapshot: dict[str, Any]) -> int:
    rsi = str(snapshot.get("rsi14_state") or "")
    slope = str(snapshot.get("rsi14_slope_state") or "")
    macd = str(snapshot.get("macd_state") or "")
    hist = str(snapshot.get("macd_hist_state") or "")
    ema = str(snapshot.get("price_vs_ema21_state") or "")
    score = 0
    if side == "YES":
        score += 1 if rsi == "bullish" else 0
        score -= 1 if rsi == "bearish" else 0
        score += 1 if slope in {"rising", "rising_fast"} else 0
        score -= 1 if slope in {"falling", "falling_fast"} else 0
        score += 1 if macd == "bullish" else 0
        score -= 1 if macd == "bearish" else 0
        score += 1 if hist == "positive_expanding" else 0
        score -= 1 if hist == "negative_expanding" else 0
        score += 1 if ema == "above" else 0
        score -= 1 if ema == "below" else 0
    else:
        score += 1 if rsi == "bearish" else 0
        score -= 1 if rsi == "bullish" else 0
        score += 1 if slope in {"falling", "falling_fast"} else 0
        score -= 1 if slope in {"rising", "rising_fast"} else 0
        score += 1 if macd == "bearish" else 0
        score -= 1 if macd == "bullish" else 0
        score += 1 if hist == "negative_expanding" else 0
        score -= 1 if hist == "positive_expanding" else 0
        score += 1 if ema == "below" else 0
        score -= 1 if ema == "above" else 0
    return score


def build_row(case: Any, *, seconds: int) -> dict[str, Any]:
    payload = build_payload(case, seconds=seconds, include_indicators=True)
    payload = compact_indicator_payload(payload, indicator_mode="states_only")
    post = payload.get("post_entry", {})
    pre = payload.get("pre_entry", {})
    tech = payload.get("technicals", {}).get("post_entry", {})
    return {
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
        "btc_support_score": btc_support_score(str(payload.get("side") or ""), tech),
    }


def summarize_binary(mask: pd.Series, frame: pd.DataFrame, *, truth_key: str) -> dict[str, Any]:
    n = int(mask.sum())
    positives = int(frame.loc[mask, truth_key].sum())
    false_positives = n - positives
    truth_total = int(frame[truth_key].sum())
    return {
        "n": n,
        "positives": positives,
        "false_positives": false_positives,
        "precision": round(positives / n, 4) if n else None,
        "recall": round(positives / truth_total, 4) if truth_total else None,
        "positive_rate": round(positives / len(frame), 4) if len(frame) else None,
    }


def build_single_feature_summary(frame: pd.DataFrame, *, features: list[str]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for feature in features:
        entries: list[dict[str, Any]] = []
        for value, group in frame.groupby(feature, dropna=False):
            n = int(len(group))
            if n < 3:
                continue
            losers = int(group["settlement_loser"].sum())
            stop_hits = int(group["stop_hit"].sum())
            entries.append(
                {
                    "value": value,
                    "n": n,
                    "settlement_losers": losers,
                    "stop_hits": stop_hits,
                    "loser_rate": round(losers / n, 4),
                    "stop_hit_rate": round(stop_hits / n, 4),
                }
            )
        summary[feature] = sorted(entries, key=lambda item: (item["loser_rate"], item["n"]), reverse=True)
    return summary


def build_top_rules(frame: pd.DataFrame, *, features: list[str], min_n: int, max_rules: int) -> list[dict[str, Any]]:
    candidate_values: dict[str, list[Any]] = {}
    for feature in features:
        counts = frame[feature].dropna().value_counts()
        candidate_values[feature] = [value for value, count in counts.items() if int(count) >= min_n]

    results: list[dict[str, Any]] = []
    for width in (1, 2, 3):
        for chosen_features in combinations(features, width):
            value_lists = [candidate_values[feature] for feature in chosen_features]
            if not all(value_lists):
                continue
            combos = [[]]
            for values in value_lists:
                combos = [existing + [value] for existing in combos for value in values]
            for values in combos:
                mask = pd.Series(True, index=frame.index)
                parts: list[str] = []
                for feature, value in zip(chosen_features, values):
                    mask &= frame[feature] == value
                    parts.append(f"{feature}={value}")
                if int(mask.sum()) < min_n:
                    continue
                loser_summary = summarize_binary(mask, frame, truth_key="settlement_loser")
                stop_summary = summarize_binary(mask, frame, truth_key="stop_hit")
                precision = loser_summary["precision"] or 0.0
                recall = loser_summary["recall"] or 0.0
                results.append(
                    {
                        "rule": " & ".join(parts),
                        "n": loser_summary["n"],
                        "settlement_losers": loser_summary["positives"],
                        "false_positives": loser_summary["false_positives"],
                        "settlement_precision": loser_summary["precision"],
                        "settlement_recall": loser_summary["recall"],
                        "stop_hit_precision": stop_summary["precision"],
                        "score": round(float(precision) * float(recall), 6),
                    }
                )
    results.sort(
        key=lambda item: (
            item["score"],
            item["settlement_precision"] or 0.0,
            item["settlement_recall"] or 0.0,
            -item["false_positives"],
        ),
        reverse=True,
    )
    return results[:max_rules]


def build_hypotheses(frame: pd.DataFrame) -> dict[str, Any]:
    mask_weak = frame["current_strength"] == "weak"
    mask_no_strong_light_weak = (
        (frame["side"] == "NO")
        & (frame["current_strength"] == "strong")
        & (frame["damage_state"] == "light")
        & (frame["rebound_state"] == "weak")
    )
    mask_no_strong_light_weak_belowish = mask_no_strong_light_weak & frame["current_vs_entry_state"].isin(
        ["below_entry", "near_entry"]
    )
    return {
        "weak_strength_hard_red": summarize_binary(mask_weak, frame, truth_key="settlement_loser"),
        "no_strong_light_weak_ambiguity": summarize_binary(mask_no_strong_light_weak, frame, truth_key="settlement_loser"),
        "no_strong_light_weak_below_or_near": summarize_binary(
            mask_no_strong_light_weak_belowish,
            frame,
            truth_key="settlement_loser",
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Mine compact post-entry rule candidates from historical trade payloads.")
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--entry-low", type=int, default=89)
    parser.add_argument("--entry-high", type=int, default=92)
    parser.add_argument("--stop-threshold", type=float, default=70.0)
    parser.add_argument("--delay-seconds", type=int, default=90)
    parser.add_argument("--min-n", type=int, default=3)
    parser.add_argument("--max-rules", type=int, default=25)
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    cases = build_cases(
        str(args.dataset),
        entry_low=int(args.entry_low),
        entry_high=int(args.entry_high),
        stop_threshold=float(args.stop_threshold),
    )
    rows = [build_row(case, seconds=int(args.delay_seconds)) for case in cases]
    frame = pd.DataFrame(rows)
    features = [
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

    payload = {
        "summary": {
            "dataset": str(args.dataset),
            "delay_seconds": int(args.delay_seconds),
            "case_count": int(len(frame)),
            "settlement_loser_count": int(frame["settlement_loser"].sum()),
            "stop_hit_count": int(frame["stop_hit"].sum()),
            "bucket_counts": frame["bucket"].value_counts(dropna=False).to_dict(),
        },
        "single_feature_summary": build_single_feature_summary(frame, features=features),
        "top_loser_rules": build_top_rules(
            frame,
            features=features,
            min_n=int(args.min_n),
            max_rules=int(args.max_rules),
        ),
        "named_hypotheses": build_hypotheses(frame),
        "loser_rows": frame[frame["settlement_loser"] == 1].to_dict(orient="records"),
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved post-entry rule mining summary to {output_path}")
    print(json.dumps(payload["summary"], indent=2))
    print(json.dumps(payload["named_hypotheses"], indent=2))


if __name__ == "__main__":
    main()
