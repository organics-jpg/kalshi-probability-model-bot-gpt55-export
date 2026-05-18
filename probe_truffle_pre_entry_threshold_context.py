from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from probe_truffle_ambiguity_router import extract_json_object
from probe_truffle_single_call_context import (
    DEFAULT_ENDPOINT,
    DEFAULT_MODEL,
    bucket_entry_location,
    bucket_runup,
    bucket_seconds_into_market,
)
from probe_truffle_two_stage_predictor import (
    VALID_BIASES,
    VALID_RISKS,
    build_cases,
    bucket_move,
    bucket_pressure,
    bucket_price,
    bucket_spread,
    bucket_volatility,
    load_feature_frame,
    resolve_truffle_chat_completion_endpoint,
    resolve_truffle_model_id,
    sample_cases,
)

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "truffle_pre_entry_threshold_context_latest.json"

PROMPT = """You are evaluating a possible future Kalshi BTC 15 minute trade before entry.
Return JSON only.

The trade has not entered yet.
The specified side has just reached the trigger level shown in the input.
The eventual planned entry, if allowed later, would be near 89 to 91 on the same side.

Definitions:
- reversal_risk means the chance that a later 89-91 entry on this side would eventually hit 70 or lower before settlement
- settlement_bias means the chance that a later 89-91 entry on this side would still settle in the money

Goal:
- find markets that already look dangerous before entry
- only use FAVORABLE for the clearest supportive setups
- if mixed or unclear, prefer MEDIUM and UNCLEAR

Interpretation:
- trigger_level tells you how far the market has advanced toward the eventual 89-91 entry zone
- pre_entry fields describe how the market moved into this trigger
- strong run-up with weak pressure can be exhaustion risk, not automatically favorable
- wide spread, adverse pressure, and very fast move should make you more cautious
- FAVORABLE should be rare at early trigger levels like 70 or 75

Required output:
{
  "reversal_risk": "LOW or MEDIUM or HIGH",
  "settlement_bias": "FAVORABLE or UNCLEAR or UNFAVORABLE",
  "confidence": 0.0,
  "reason_code": "short_code"
}
"""


def coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


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


def build_threshold_payload(case: Any, *, threshold: int) -> dict[str, Any] | None:
    feature_df = load_feature_frame(case.feature_path)
    yes_side = case.side == "yes"
    bid_col = "yes_bid_cents" if yes_side else "no_bid_cents"
    ask_col = "yes_ask_cents" if yes_side else "no_ask_cents"
    pre = feature_df[feature_df["ts"] <= case.entry_dt_local].copy()
    pre = pre[[ "ts", bid_col, ask_col, "depth_imbalance", "seconds_to_close"]].rename(columns={bid_col: "same_bid", ask_col: "same_ask"})
    pre = pre.dropna(subset=["same_bid", "same_ask"])
    if pre.empty:
        return None
    hit = pre[pre["same_bid"] >= float(threshold)]
    if hit.empty:
        return None
    idx = hit.index[0]
    threshold_frame = pre.loc[:idx].copy()
    row = threshold_frame.iloc[-1]
    open_bid = coerce_float(threshold_frame.iloc[0]["same_bid"])
    current_bid = coerce_float(row["same_bid"])
    high = coerce_float(threshold_frame["same_bid"].max())
    low = coerce_float(threshold_frame["same_bid"].min())
    rng = high - low
    loc = 0.5 if rng <= 0 else (current_bid - low) / rng
    last30 = threshold_frame[threshold_frame["ts"] >= (row["ts"] - pd.Timedelta(seconds=30))]
    last60 = threshold_frame[threshold_frame["ts"] >= (row["ts"] - pd.Timedelta(seconds=60))]
    pressure = coerce_float(row["depth_imbalance"])
    if not yes_side:
        pressure = -pressure
    seconds_into_market = coerce_float(threshold_frame.iloc[0]["seconds_to_close"]) - coerce_float(row["seconds_to_close"])

    return {
        "schema_version": "pre_entry_threshold_context_v1",
        "market": case.market,
        "side": case.side.upper(),
        "trigger_level": int(threshold),
        "planned_entry_band": "89_91",
        "pre_entry": {
            "opening_price_zone": bucket_price(open_bid),
            "trigger_location_in_range": bucket_entry_location(loc),
            "open_to_trigger_runup": bucket_runup(current_bid - open_bid),
            "last30_move_state": bucket_move(current_bid - coerce_float(last30.iloc[0]["same_bid"])) if not last30.empty else "flat",
            "last60_move_state": bucket_move(current_bid - coerce_float(last60.iloc[0]["same_bid"])) if not last60.empty else "flat",
            "trigger_spread_state": bucket_spread(coerce_float(row["same_ask"] - row["same_bid"])),
            "trigger_pressure_state": bucket_pressure(pressure),
            "volatility_state": bucket_volatility(rng),
            "timing_state": bucket_seconds_into_market(seconds_into_market),
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
    parser = argparse.ArgumentParser(description="Probe Truffle before entry when price first reaches threshold levels.")
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout-ms", type=int, default=20000)
    parser.add_argument("--per-bucket", type=int, default=6)
    parser.add_argument("--bucket-filter", default="")
    parser.add_argument("--thresholds", default="70,75,80,85")
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    all_cases = build_cases(str(args.dataset), entry_low=89, entry_high=91, stop_threshold=70.0)
    bucket_filter = [chunk.strip() for chunk in str(args.bucket_filter).split(",") if chunk.strip()]
    cases = sample_cases(all_cases, per_bucket=int(args.per_bucket), buckets=bucket_filter or None)
    thresholds = [int(chunk.strip()) for chunk in str(args.thresholds).split(",") if chunk.strip()]

    rows: list[dict[str, Any]] = []
    for case in cases:
        for threshold in thresholds:
            payload = build_threshold_payload(case, threshold=int(threshold))
            if payload is None:
                continue
            response = issue_json_decision(
                payload,
                endpoint=str(args.endpoint),
                model=str(args.model),
                timeout_ms=int(args.timeout_ms),
                prompt_text=PROMPT,
            )
            output = normalize_output(response.get("parsed") if isinstance(response, dict) else None)
            rows.append(
                {
                    "case_type": f"threshold_{threshold}",
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
        "threshold_summaries": {
            case_type: summarize_rows([row for row in rows if row["case_type"] == case_type])
            for case_type in sorted({row["case_type"] for row in rows})
        },
    }

    payload = {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "dataset": args.dataset,
        "endpoint": args.endpoint,
        "model": args.model,
        "thresholds": thresholds,
        "summary": summary,
        "rows": rows,
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved pre-entry threshold probe to {output_path}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
