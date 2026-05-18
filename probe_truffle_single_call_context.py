from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from probe_truffle_two_stage_predictor import (
    VALID_BIASES,
    VALID_RISKS,
    build_cases,
    bucket_current_strength,
    bucket_damage,
    bucket_move,
    bucket_pressure,
    bucket_price,
    bucket_rebound,
    bucket_spread,
    bucket_volatility,
    bucket_vs_entry,
    load_feature_frame,
    resolve_truffle_chat_completion_endpoint,
    resolve_truffle_model_id,
    sample_cases,
)
from probe_truffle_ambiguity_router import extract_json_object

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "truffle_single_call_context_latest.json"
DEFAULT_ENDPOINT = "http://192.168.1.234/if2/v1/chat/completions"
DEFAULT_MODEL = "Qwen3.5-2B"
DEFAULT_PROMPT_PATH = ROOT / "truffle_single_call_context_prompt.txt"

PROMPT = """You are evaluating one live Kalshi BTC 15 minute trade from a single compact context snapshot.
Return JSON only.

Goal:
- identify trades with high reversal risk before settlement
- identify only the clearest favorable holds
- if mixed or unclear, prefer MEDIUM and UNCLEAR

Definitions:
- reversal_risk means the chance the position still makes or continues a strong adverse move and hits 70 or lower before settlement
- settlement_bias means the chance the specified side still settles in the money

Interpretation:
- pre_entry fields describe how the market moved into the entry
- post_entry fields describe how the trade is behaving now
- post_entry behavior should matter more than pre_entry context
- FAVORABLE should be rare and should require clearly supportive post_entry behavior
- if current_vs_entry_state is well_below_entry, reversal_risk should usually be HIGH
- if damage_state is heavy and rebound_state is weak, reversal_risk should usually be HIGH
- if current_strength is strong but current_vs_entry_state is only near_entry or below_entry, that is not enough by itself for FAVORABLE

Required output:
{
  "reversal_risk": "LOW or MEDIUM or HIGH",
  "settlement_bias": "FAVORABLE or UNCLEAR or UNFAVORABLE",
  "confidence": 0.0,
  "reason_code": "short_code"
}
"""


def load_prompt_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8").strip()
    return text or PROMPT


def coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def bucket_entry_location(value: float) -> str:
    if value >= 0.95:
        return "top_of_range"
    if value >= 0.7:
        return "upper_range"
    if value >= 0.3:
        return "mid_range"
    return "lower_range"


def bucket_runup(value: float) -> str:
    if value >= 30:
        return "strong_runup"
    if value >= 12:
        return "moderate_runup"
    if value <= -8:
        return "drawdown"
    return "flat_to_small"


def bucket_seconds_into_market(value: float) -> str:
    if value >= 600:
        return "late_entry"
    if value >= 300:
        return "mid_entry"
    return "early_entry"


def issue_json_decision(
    payload: dict[str, Any],
    *,
    endpoint: str,
    model: str,
    timeout_ms: int,
    prompt_text: str,
    max_tokens: int = 90,
) -> dict[str, Any]:
    resolved_endpoint = resolve_truffle_chat_completion_endpoint(endpoint)
    resolved_model = resolve_truffle_model_id(model, endpoint=resolved_endpoint, timeout_ms=timeout_ms) or model
    response = requests.post(
        resolved_endpoint,
        headers={"Content-Type": "application/json"},
        json={
            "model": resolved_model,
            "temperature": 0,
            "max_tokens": int(max_tokens),
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": prompt_text},
                {"role": "user", "content": json.dumps(payload, sort_keys=True)},
            ],
        },
        timeout=max(1.0, float(timeout_ms) / 1000.0),
    )
    response.raise_for_status()
    body = response.json()
    content = ""
    finish_reason = ""
    if isinstance(body, dict):
        choices = body.get("choices")
        if isinstance(choices, list) and choices:
            choice = choices[0] if isinstance(choices[0], dict) else {}
            finish_reason = str(choice.get("finish_reason") or "")
            message = choice.get("message") if isinstance(choice, dict) else None
            if isinstance(message, dict):
                content = str(message.get("content") or "")
    parsed = extract_json_object(content)
    return {"parsed": parsed, "content": content, "finish_reason": finish_reason}


def normalize_output(parsed: dict[str, Any] | None) -> dict[str, Any]:
    reversal_risk = str(parsed.get("reversal_risk") or "").strip().upper() if isinstance(parsed, dict) else ""
    settlement_bias = str(parsed.get("settlement_bias") or "").strip().upper() if isinstance(parsed, dict) else ""
    if reversal_risk not in VALID_RISKS:
        reversal_risk = "MEDIUM"
    if settlement_bias not in VALID_BIASES:
        settlement_bias = "UNCLEAR"
    return {
        "reversal_risk": reversal_risk,
        "settlement_bias": settlement_bias,
        "confidence": parsed.get("confidence") if isinstance(parsed, dict) else None,
        "reason_code": parsed.get("reason_code") if isinstance(parsed, dict) else "",
    }


def build_payload(case: Any, *, seconds: int) -> dict[str, Any]:
    feature_df = load_feature_frame(case.feature_path)
    yes_side = case.side == "yes"
    bid_col = "yes_bid_cents" if yes_side else "no_bid_cents"
    ask_col = "yes_ask_cents" if yes_side else "no_ask_cents"

    pre_all = feature_df[[ "ts", bid_col, ask_col, "depth_imbalance", "seconds_to_close"]].rename(columns={bid_col: "same_bid", ask_col: "same_ask"})
    pre_all = pre_all.dropna(subset=["same_bid", "same_ask"])

    pre = feature_df[feature_df["ts"] <= case.entry_dt_local].copy()
    pre = pre[[ "ts", bid_col, ask_col, "depth_imbalance", "seconds_to_close"]].rename(columns={bid_col: "same_bid", ask_col: "same_ask"})
    pre = pre.dropna(subset=["same_bid", "same_ask"])
    if pre.empty:
        pre = pre_all.iloc[:1].copy()
    if pre.empty:
        pre = pd.DataFrame(
            [{
                "ts": case.entry_dt_local,
                "same_bid": float(case.entry_fill_cents),
                "same_ask": float(case.entry_fill_cents),
                "depth_imbalance": 0.0,
                "seconds_to_close": float("nan"),
            }]
        )

    pre_last = pre.iloc[-1]
    open_bid = coerce_float(pre.iloc[0]["same_bid"])
    entry_bid = coerce_float(pre_last["same_bid"])
    pre_high = coerce_float(pre["same_bid"].max())
    pre_low = coerce_float(pre["same_bid"].min())
    pre_range = pre_high - pre_low
    loc = 0.5 if pre_range <= 0 else (entry_bid - pre_low) / pre_range
    last30 = pre[pre["ts"] >= (case.entry_dt_local - pd.Timedelta(seconds=30))]
    last60 = pre[pre["ts"] >= (case.entry_dt_local - pd.Timedelta(seconds=60))]
    entry_pressure = coerce_float(pre_last["depth_imbalance"])
    if not yes_side:
        entry_pressure = -entry_pressure
    seconds_into_market = coerce_float(pre.iloc[0]["seconds_to_close"]) - coerce_float(pre_last["seconds_to_close"])

    post_all = feature_df[[ "ts", bid_col, ask_col]].rename(columns={bid_col: "same_bid", ask_col: "same_ask"}).dropna()
    post = feature_df[feature_df["ts"] >= case.entry_dt_local].copy()
    post = post[[ "ts", bid_col, ask_col]].rename(columns={bid_col: "same_bid", ask_col: "same_ask"}).dropna()
    if post.empty:
        post = post_all.iloc[:1].copy()
    if post.empty:
        post = pd.DataFrame(
            [{
                "ts": case.entry_dt_local,
                "same_bid": float(case.entry_fill_cents),
                "same_ask": float(case.entry_fill_cents),
            }]
        )
    horizon = case.entry_dt_local + pd.Timedelta(seconds=int(seconds))
    sub = post[post["ts"] <= horizon].copy()
    if sub.empty:
        sub = post.iloc[:1].copy()
    current_bid = coerce_float(sub.iloc[-1]["same_bid"])
    current_ask = coerce_float(sub.iloc[-1]["same_ask"])
    low_bid = coerce_float(sub["same_bid"].min())
    drop = case.entry_fill_cents - low_bid
    rebound = current_bid - low_bid
    end_vs_entry = current_bid - case.entry_fill_cents

    return {
        "schema_version": "single_call_trade_context_v1",
        "market": case.market,
        "side": case.side.upper(),
        "seconds_since_entry": int(seconds),
        "pre_entry": {
            "opening_price_zone": bucket_price(open_bid),
            "entry_location_in_range": bucket_entry_location(loc),
            "open_to_entry_runup": bucket_runup(entry_bid - open_bid),
            "last30_move_state": bucket_move(entry_bid - coerce_float(last30.iloc[0]["same_bid"])) if not last30.empty else "flat",
            "last60_move_state": bucket_move(entry_bid - coerce_float(last60.iloc[0]["same_bid"])) if not last60.empty else "flat",
            "entry_spread_state": bucket_spread(coerce_float(pre_last["same_ask"] - pre_last["same_bid"])),
            "entry_pressure_state": bucket_pressure(entry_pressure),
            "volatility_state": bucket_volatility(pre_range),
            "entry_timing_state": bucket_seconds_into_market(seconds_into_market),
        },
        "post_entry": {
            "current_strength": bucket_current_strength(current_bid),
            "damage_state": bucket_damage(drop),
            "rebound_state": bucket_rebound(rebound),
            "current_vs_entry_state": bucket_vs_entry(end_vs_entry),
            "spread_state": bucket_spread(current_ask - current_bid),
        },
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    frame = pd.DataFrame(rows)
    favorable = frame["predicted_settlement_bias"] == "FAVORABLE"
    high_risk = frame["predicted_reversal_risk"] == "HIGH"
    green = favorable & (frame["predicted_reversal_risk"] != "HIGH")
    return {
        "case_count": int(len(frame)),
        "settlement_accuracy_binary": round(float((favorable == frame["actual_settlement_win"]).mean()), 4),
        "reversal_accuracy_binary": round(float((high_risk == frame["actual_stop_hit"]).mean()), 4),
        "favorable_metrics": {
            "predicted_count": int(favorable.sum()),
            "hit_count": int((favorable & frame["actual_settlement_win"]).sum()),
            "precision": round(float((favorable & frame["actual_settlement_win"]).sum() / max(1, favorable.sum())), 4) if int(favorable.sum()) else None,
            "recall": round(float((favorable & frame["actual_settlement_win"]).sum() / max(1, frame["actual_settlement_win"].sum())), 4) if int(frame["actual_settlement_win"].sum()) else None,
        },
        "high_risk_metrics": {
            "predicted_count": int(high_risk.sum()),
            "hit_count": int((high_risk & frame["actual_stop_hit"]).sum()),
            "precision": round(float((high_risk & frame["actual_stop_hit"]).sum() / max(1, high_risk.sum())), 4) if int(high_risk.sum()) else None,
            "recall": round(float((high_risk & frame["actual_stop_hit"]).sum() / max(1, frame["actual_stop_hit"].sum())), 4) if int(frame["actual_stop_hit"].sum()) else None,
        },
        "green_metrics": {
            "predicted_count": int(green.sum()),
            "hit_count": int((green & frame["actual_good_trade"]).sum()),
            "precision": round(float((green & frame["actual_good_trade"]).sum() / max(1, green.sum())), 4) if int(green.sum()) else None,
            "recall": round(float((green & frame["actual_good_trade"]).sum() / max(1, frame["actual_good_trade"].sum())), 4) if int(frame["actual_good_trade"].sum()) else None,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe a single post-entry Truffle call using pre-entry and post-entry context.")
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout-ms", type=int, default=20000)
    parser.add_argument("--per-bucket", type=int, default=6)
    parser.add_argument("--bucket-filter", default="")
    parser.add_argument("--delays", default="30,60,120")
    parser.add_argument("--prompt-path", default=str(DEFAULT_PROMPT_PATH))
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    all_cases = build_cases(str(args.dataset), entry_low=89, entry_high=91, stop_threshold=70.0)
    bucket_filter = [chunk.strip() for chunk in str(args.bucket_filter).split(",") if chunk.strip()]
    cases = sample_cases(all_cases, per_bucket=int(args.per_bucket), buckets=bucket_filter or None)
    delays = [int(chunk.strip()) for chunk in str(args.delays).split(",") if chunk.strip()]
    prompt_path = Path(str(args.prompt_path))
    if not prompt_path.is_absolute():
        prompt_path = ROOT / prompt_path
    prompt_text = load_prompt_text(prompt_path) if prompt_path.exists() else PROMPT

    rows: list[dict[str, Any]] = []
    for case in cases:
        for seconds in delays:
            payload = build_payload(case, seconds=int(seconds))
            response = issue_json_decision(
                payload,
                endpoint=str(args.endpoint),
                model=str(args.model),
                timeout_ms=int(args.timeout_ms),
                prompt_text=prompt_text,
            )
            output = normalize_output(response.get("parsed") if isinstance(response, dict) else None)
            rows.append(
                {
                    "case_type": f"single_call_{seconds}s",
                    "market": case.market,
                    "bucket": case.bucket,
                    "actual_settlement_win": case.settlement_win,
                    "actual_stop_hit": case.stop_hit_after_entry,
                    "actual_good_trade": case.actual_good_trade,
                    "payload": payload,
                    "predicted_reversal_risk": output["reversal_risk"],
                    "predicted_settlement_bias": output["settlement_bias"],
                    "confidence": output["confidence"],
                    "reason_code": output["reason_code"],
                    "finish_reason": str(response.get("finish_reason") or ""),
                }
            )

    summary = {
        "sampled_case_count": int(len(cases)),
        "sample_buckets": {
            bucket: int(sum(1 for case in cases if case.bucket == bucket))
            for bucket in ["settlement_loser", "winner_with_stop_hit", "clean_winner"]
        },
        "bucket_filter": bucket_filter,
        "permutation_summaries": {
            case_type: summarize_rows([row for row in rows if row["case_type"] == case_type])
            for case_type in sorted({row["case_type"] for row in rows})
        },
    }

    payload = {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "dataset": args.dataset,
        "endpoint": args.endpoint,
        "model": args.model,
        "prompt_path": str(prompt_path),
        "delays": delays,
        "summary": summary,
        "rows": rows,
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved single-call context probe to {output_path}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
