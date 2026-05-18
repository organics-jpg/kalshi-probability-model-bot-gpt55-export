from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from probe_truffle_single_call_indicator_variants import build_payload
from probe_truffle_two_stage_predictor import build_cases, sample_cases
from truffle_regime_lease import resolve_truffle_chat_completion_endpoint, resolve_truffle_model_id

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "truffle_signal_tool_variants_latest.json"
DEFAULT_ENDPOINT = "http://192.168.1.234/if2/v1/chat/completions"
DEFAULT_MODEL = "Qwen3.6-35B-A3B"
SIGNAL_TOOL_NAME = "emit_trade_signal"
VALID_DECISIONS = {"GREEN_LIGHT", "NEUTRAL", "RED_LIGHT"}
HTTP_SESSION = requests.Session()


@dataclass(frozen=True)
class PromptVariant:
    name: str
    prompt_text: str
    indicator_mode: str
    reasoning_enabled: bool
    max_tokens: int = 1800
    tool_choice_mode: str = "auto"


def build_signal_tool_schema() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": SIGNAL_TOOL_NAME,
                "description": "Emit the structured supervisory trade signal.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "decision": {
                            "type": "string",
                            "enum": sorted(VALID_DECISIONS),
                        },
                        "confidence": {"type": "number"},
                        "reason_code": {"type": "string"},
                    },
                    "required": ["decision", "confidence", "reason_code"],
                    "additionalProperties": False,
                },
            },
        }
    ]


def build_prompt_variants() -> list[PromptVariant]:
    baseline_prompt = """
You are the post-entry supervisor for a Kalshi BTC 15 minute trading bot.
Use the input to decide whether the open trade should be tagged GREEN_LIGHT, NEUTRAL, or RED_LIGHT.
Your only final action is to call emit_trade_signal exactly once. Never answer in normal text.

Objective:
- RED_LIGHT means reversal risk looks materially elevated
- GREEN_LIGHT means settlement path still looks clearly supportive
- NEUTRAL means mixed or unclear
- if uncertain, choose NEUTRAL

Interpretation:
- post_entry evidence matters most
- pre_entry evidence is background context
- if current_vs_entry_state is below_entry or well_below_entry and damage is not light, lean RED_LIGHT
- if post_entry is strong but current_vs_entry_state is only near_entry or below_entry, prefer NEUTRAL over GREEN_LIGHT
- GREEN_LIGHT should be rare

Field rules:
- decision must be GREEN_LIGHT or NEUTRAL or RED_LIGHT
- confidence must be between 0 and 1
- reason_code must be short and machine-friendly
""".strip()

    indicator_prompt = """
You are the post-entry supervisor for a Kalshi BTC 15 minute trading bot.
Use the input to decide whether the open trade should be tagged GREEN_LIGHT, NEUTRAL, or RED_LIGHT.
Your only final action is to call emit_trade_signal exactly once. Never answer in normal text.

Objective:
- RED_LIGHT means reversal risk looks materially elevated
- GREEN_LIGHT means settlement path still looks clearly supportive
- NEUTRAL means mixed or unclear
- if uncertain, choose NEUTRAL

Interpretation priority:
1. post_entry evidence matters most
2. pre_entry evidence is background context
3. technicals are secondary confirmation or warning signals

Indicator interpretation:
- technicals.pre_entry and technicals.post_entry are compact technical indicator snapshots
- if technicals.price_series is same_side_mid_5s, bullish signals support the side
- if technicals.price_series is btc_spot_1m, bullish BTC usually supports YES and hurts NO, while bearish BTC usually supports NO and hurts YES
- RSI is mainly exhaustion or recovery context, not a trigger by itself
- MACD and MACD histogram mainly signal continuation or momentum decay
- price_vs_ema21 is supportive context, not a standalone override

Decision guidance:
- if current_vs_entry_state is below_entry or well_below_entry and technicals are deteriorating, lean RED_LIGHT
- if damage_state is heavy, do not use GREEN_LIGHT
- if post_entry is strong but technicals are mixed, prefer NEUTRAL
- if post_entry is strong and technicals are supportive, GREEN_LIGHT is allowed but should still be rare

Field rules:
- decision must be GREEN_LIGHT or NEUTRAL or RED_LIGHT
- confidence must be between 0 and 1
- reason_code must be short and machine-friendly
""".strip()

    force_tool_prompt = """
You are the post-entry supervisor for a Kalshi BTC 15 minute trading bot.
Do not explain the input. Do not restate the trade. Do not write analysis in normal text.
Respond only by calling emit_trade_signal exactly once.

Decision meaning:
- RED_LIGHT = elevated reversal or settlement-failure risk
- NEUTRAL = mixed or unclear
- GREEN_LIGHT = clearly favorable hold

Priority:
1. post_entry state
2. pre_entry context
3. technicals as confirmation only

Interpretation:
- if current_vs_entry_state is below_entry or well_below_entry and damage is not light, lean RED_LIGHT
- if damage_state is heavy, do not use GREEN_LIGHT
- if technicals.price_series is btc_spot_1m, bullish BTC usually supports YES and hurts NO, while bearish BTC usually supports NO and hurts YES
- if mixed, choose NEUTRAL
- GREEN_LIGHT should be rare

Fields:
- decision must be GREEN_LIGHT or NEUTRAL or RED_LIGHT
- confidence between 0 and 1
- reason_code short and machine-friendly
""".strip()

    compact_indicator_prompt = """
You are the post-entry supervisor for a Kalshi BTC 15 minute trading bot.
Call emit_trade_signal exactly once. Never answer in normal text.

Decision meaning:
- RED_LIGHT = elevated reversal or settlement-failure risk
- NEUTRAL = mixed or unclear
- GREEN_LIGHT = clearly favorable hold

Rules:
- post_entry matters most
- technicals.post_entry is secondary same-side indicator context
- bearish technicals hurt the side; bullish technicals support it
- if below_entry or well_below_entry with weak rebound, lean RED_LIGHT
- if heavy damage, do not use GREEN_LIGHT
- if mixed, choose NEUTRAL
- GREEN_LIGHT should be rare

Fields:
- decision must be GREEN_LIGHT or NEUTRAL or RED_LIGHT
- confidence between 0 and 1
- reason_code short and machine-friendly
""".strip()

    indicator_guard_prompt = """
You are the post-entry supervisor for a Kalshi BTC 15 minute trading bot.
Think privately in the reasoning channel only.
When ready, call emit_trade_signal exactly once.
Do not answer in normal text.

Action meanings:
- GREEN_LIGHT: favorable continuation is clear enough to justify holding confidence
- NEUTRAL: mixed or underdetermined
- RED_LIGHT: elevated reversal or settlement-failure risk

Decision order:
1. post_entry damage and current-vs-entry state
2. post_entry strength and rebound
3. technicals as confirmation only
4. if mixed, choose NEUTRAL

Guardrails:
- do not issue GREEN_LIGHT on weak or damaged post_entry behavior
- do not ignore clearly adverse MACD and price-vs-EMA context when the trade is already below entry
- if unsure, choose NEUTRAL

Field rules:
- decision must be GREEN_LIGHT or NEUTRAL or RED_LIGHT
- confidence must be between 0 and 1
- reason_code must be short and machine-friendly
""".strip()

    return [
        PromptVariant(
            name="signal_baseline_no_indicators_reasoning_off",
            prompt_text=baseline_prompt,
            indicator_mode="none",
            reasoning_enabled=False,
        ),
        PromptVariant(
            name="signal_baseline_with_indicator_states_reasoning_off",
            prompt_text=indicator_prompt,
            indicator_mode="states_only",
            reasoning_enabled=False,
        ),
        PromptVariant(
            name="signal_force_tool_with_indicator_states_reasoning_off",
            prompt_text=force_tool_prompt,
            indicator_mode="states_only",
            reasoning_enabled=False,
            max_tokens=700,
            tool_choice_mode="required",
        ),
        PromptVariant(
            name="signal_compact_indicator_states_reasoning_off",
            prompt_text=compact_indicator_prompt,
            indicator_mode="states_only",
            reasoning_enabled=False,
            max_tokens=1400,
        ),
        PromptVariant(
            name="signal_guard_with_indicators_reasoning_on",
            prompt_text=indicator_guard_prompt,
            indicator_mode="full",
            reasoning_enabled=True,
            max_tokens=2200,
        ),
    ]


def compact_indicator_payload(payload: dict[str, Any], *, indicator_mode: str) -> dict[str, Any]:
    if indicator_mode == "none":
        payload.pop("technicals", None)
        return payload
    if indicator_mode != "states_only":
        return payload
    technicals = payload.get("technicals")
    if not isinstance(technicals, dict):
        return payload

    def compact_snapshot(snapshot: Any) -> dict[str, Any]:
        if not isinstance(snapshot, dict):
            return {}
        keep = (
            "sample_count",
            "price_series",
            "rsi14_state",
            "rsi14_slope_state",
            "macd_state",
            "macd_hist_state",
            "price_vs_ema21_state",
        )
        return {key: snapshot.get(key) for key in keep if key in snapshot}

    payload["technicals"] = {
        "pre_entry": compact_snapshot(technicals.get("pre_entry")),
        "post_entry": compact_snapshot(technicals.get("post_entry")),
    }
    return payload


def extract_tool_call_dict(payload: Any) -> dict[str, Any] | None:
    if isinstance(payload, dict):
        tool_calls = payload.get("tool_calls")
        if isinstance(tool_calls, list):
            for tool_call in tool_calls:
                if not isinstance(tool_call, dict):
                    continue
                function = tool_call.get("function")
                if not isinstance(function, dict):
                    continue
                if str(function.get("name") or "").strip() != SIGNAL_TOOL_NAME:
                    continue
                return extract_tool_call_dict(function.get("arguments"))
        message = payload.get("message")
        if isinstance(message, dict):
            extracted = extract_tool_call_dict(message)
            if extracted is not None:
                return extracted
        choices = payload.get("choices")
        if isinstance(choices, list):
            for choice in choices:
                extracted = extract_tool_call_dict(choice)
                if extracted is not None:
                    return extracted
        return None
    if isinstance(payload, list):
        for item in payload:
            extracted = extract_tool_call_dict(item)
            if extracted is not None:
                return extracted
        return None
    if payload in (None, ""):
        return None
    text = str(payload).strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
    except Exception:
        return None
    return parsed if isinstance(parsed, dict) else None


def normalize_signal_output(parsed: dict[str, Any] | None) -> dict[str, Any]:
    decision = str(parsed.get("decision") or "").strip().upper() if isinstance(parsed, dict) else ""
    if decision not in VALID_DECISIONS:
        decision = "NEUTRAL"
    confidence = None
    if isinstance(parsed, dict):
        try:
            confidence = float(parsed.get("confidence"))
        except Exception:
            confidence = None
    return {
        "decision": decision,
        "confidence": confidence,
        "reason_code": str(parsed.get("reason_code") or "").strip() if isinstance(parsed, dict) else "",
    }


def issue_tool_decision(
    payload: dict[str, Any],
    *,
    endpoint: str,
    model: str,
    timeout_ms: int,
    prompt_text: str,
    max_tokens: int,
    reasoning_enabled: bool,
    tool_choice_mode: str = "auto",
) -> dict[str, Any]:
    resolved_endpoint = resolve_truffle_chat_completion_endpoint(endpoint)
    resolved_model = resolve_truffle_model_id(model, endpoint=resolved_endpoint, timeout_ms=timeout_ms) or model
    tool_choice: Any = "auto"
    if tool_choice_mode == "required":
        tool_choice = {"type": "function", "function": {"name": SIGNAL_TOOL_NAME}}
    request_body: dict[str, Any] = {
        "model": resolved_model,
        "temperature": 0,
        "max_tokens": int(max_tokens),
        "tools": build_signal_tool_schema(),
        "tool_choice": tool_choice,
        "messages": [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": json.dumps(payload, sort_keys=True, separators=(",", ":"))},
        ],
        "reasoning": {"enabled": bool(reasoning_enabled)},
    }

    response = HTTP_SESSION.post(
        resolved_endpoint,
        headers={"Content-Type": "application/json"},
        json=request_body,
        timeout=max(1.0, float(timeout_ms) / 1000.0),
    )
    response.raise_for_status()
    body = response.json()
    finish_reason = ""
    content = ""
    reasoning = ""
    if isinstance(body, dict):
        choices = body.get("choices")
        if isinstance(choices, list) and choices:
            choice = choices[0] if isinstance(choices[0], dict) else {}
            finish_reason = str(choice.get("finish_reason") or "")
            message = choice.get("message") if isinstance(choice, dict) else None
            if isinstance(message, dict):
                content = str(message.get("content") or "")
                reasoning = str(message.get("reasoning") or "")
    parsed = extract_tool_call_dict(body)
    usage = body.get("usage") if isinstance(body, dict) and isinstance(body.get("usage"), dict) else {}
    return {
        "body": body,
        "parsed": parsed,
        "finish_reason": finish_reason,
        "content": content,
        "reasoning": reasoning,
        "usage": usage,
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    frame = pd.DataFrame(rows)
    if frame.empty:
        return {"case_count": 0}
    green = frame["predicted_decision"] == "GREEN_LIGHT"
    red = frame["predicted_decision"] == "RED_LIGHT"
    valid = frame["valid"].fillna(False)
    return {
        "case_count": int(len(frame)),
        "valid_rate": round(float(valid.mean()), 4),
        "green_metrics": {
            "predicted_count": int(green.sum()),
            "hit_count": int((green & frame["actual_good_trade"]).sum()),
            "precision": round(float((green & frame["actual_good_trade"]).sum() / max(1, green.sum())), 4) if int(green.sum()) else None,
            "recall": round(float((green & frame["actual_good_trade"]).sum() / max(1, frame["actual_good_trade"].sum())), 4) if int(frame["actual_good_trade"].sum()) else None,
        },
        "red_stop_metrics": {
            "predicted_count": int(red.sum()),
            "hit_count": int((red & frame["actual_stop_hit"]).sum()),
            "precision": round(float((red & frame["actual_stop_hit"]).sum() / max(1, red.sum())), 4) if int(red.sum()) else None,
            "recall": round(float((red & frame["actual_stop_hit"]).sum() / max(1, frame["actual_stop_hit"].sum())), 4) if int(frame["actual_stop_hit"].sum()) else None,
        },
        "red_settlement_metrics": {
            "predicted_count": int(red.sum()),
            "hit_count": int((red & (~frame["actual_settlement_win"])).sum()),
            "precision": round(float((red & (~frame["actual_settlement_win"])).sum() / max(1, red.sum())), 4) if int(red.sum()) else None,
            "recall": round(float((red & (~frame["actual_settlement_win"])).sum() / max(1, (~frame["actual_settlement_win"]).sum())), 4) if int((~frame["actual_settlement_win"]).sum()) else None,
        },
    }


def summarize_variant_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    valid_rows = [row for row in rows if row.get("valid")]
    invalid_rows = [row for row in rows if not row.get("valid")]
    finish_reason_counts = pd.Series([str(row.get("finish_reason") or "") for row in rows]).value_counts(dropna=False).to_dict()
    parse_error_counts = pd.Series([str(row.get("parse_error") or "") for row in invalid_rows]).value_counts(dropna=False).to_dict()
    usage_prompt = [int(row.get("prompt_tokens") or 0) for row in rows if row.get("prompt_tokens") is not None]
    usage_completion = [int(row.get("completion_tokens") or 0) for row in rows if row.get("completion_tokens") is not None]
    return {
        "case_count": int(total),
        "valid_count": int(len(valid_rows)),
        "invalid_count": int(len(invalid_rows)),
        "valid_rate": round(len(valid_rows) / max(1, total), 4),
        "finish_reason_counts": {str(key): int(value) for key, value in finish_reason_counts.items()},
        "parse_error_counts": {str(key): int(value) for key, value in parse_error_counts.items()},
        "avg_prompt_tokens": round(sum(usage_prompt) / len(usage_prompt), 2) if usage_prompt else None,
        "avg_completion_tokens": round(sum(usage_completion) / len(usage_completion), 2) if usage_completion else None,
        "metrics_all_rows": summarize_rows(rows),
        "metrics_valid_rows": summarize_rows(valid_rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe Qwen tool-call supervisory trade-signal variants.")
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout-ms", type=int, default=120000)
    parser.add_argument("--per-bucket", type=int, default=3)
    parser.add_argument("--bucket-filter", default="")
    parser.add_argument("--delays", default="90")
    parser.add_argument("--variant-filter", default="")
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    all_cases = build_cases(str(args.dataset), entry_low=89, entry_high=92, stop_threshold=70.0)
    bucket_filter = [chunk.strip() for chunk in str(args.bucket_filter).split(",") if chunk.strip()]
    cases = sample_cases(all_cases, per_bucket=int(args.per_bucket), buckets=bucket_filter or None)
    delays = [int(chunk.strip()) for chunk in str(args.delays).split(",") if chunk.strip()]
    variants = build_prompt_variants()
    variant_filter = {chunk.strip() for chunk in str(args.variant_filter).split(",") if chunk.strip()}
    if variant_filter:
        variants = [variant for variant in variants if variant.name in variant_filter]

    started_at = pd.Timestamp.utcnow().isoformat()
    results_by_variant: dict[str, list[dict[str, Any]]] = {variant.name: [] for variant in variants}

    for variant in variants:
        for case in cases:
            for seconds in delays:
                payload = build_payload(case, seconds=int(seconds), include_indicators=variant.indicator_mode != "none")
                payload = compact_indicator_payload(payload, indicator_mode=variant.indicator_mode)
                start = time.perf_counter()
                finish_reason = ""
                parse_error = ""
                prompt_tokens = None
                completion_tokens = None
                raw_content = ""
                raw_reasoning = ""
                try:
                    response = issue_tool_decision(
                        payload,
                        endpoint=str(args.endpoint),
                        model=str(args.model),
                        timeout_ms=int(args.timeout_ms),
                        prompt_text=variant.prompt_text,
                        max_tokens=int(variant.max_tokens),
                        reasoning_enabled=bool(variant.reasoning_enabled),
                        tool_choice_mode=str(variant.tool_choice_mode),
                    )
                    finish_reason = str(response.get("finish_reason") or "")
                    raw_content = str(response.get("content") or "")
                    raw_reasoning = str(response.get("reasoning") or "")
                    usage = response.get("usage") if isinstance(response, dict) else {}
                    if isinstance(usage, dict):
                        prompt_tokens = usage.get("prompt_tokens")
                        completion_tokens = usage.get("completion_tokens")
                    output = normalize_signal_output(response.get("parsed") if isinstance(response, dict) else None)
                    if not isinstance(response.get("parsed"), dict):
                        parse_error = "missing_tool_call"
                except Exception as exc:
                    output = {"decision": "NEUTRAL", "confidence": None, "reason_code": ""}
                    parse_error = f"http_error:{exc}"
                elapsed_seconds = round(time.perf_counter() - start, 3)
                results_by_variant[variant.name].append(
                    {
                        "variant": variant.name,
                        "case_type": f"signal_tool_{seconds}s",
                        "market": case.market,
                        "bucket": case.bucket,
                        "actual_settlement_win": case.settlement_win,
                        "actual_stop_hit": case.stop_hit_after_entry,
                        "actual_good_trade": case.actual_good_trade,
                        "predicted_decision": output["decision"],
                        "confidence": output["confidence"],
                        "reason_code": output["reason_code"],
                        "finish_reason": finish_reason,
                        "parse_error": parse_error,
                        "valid": parse_error == "",
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "elapsed_seconds": elapsed_seconds,
                        "payload": payload,
                        "raw_content": raw_content,
                        "raw_reasoning": raw_reasoning,
                    }
                )

    summary = {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "started_at": started_at,
        "dataset": str(args.dataset),
        "endpoint": str(args.endpoint),
        "model": str(args.model),
        "sampled_case_count": int(len(cases)),
        "sample_buckets": {
            bucket: int(sum(1 for case in cases if case.bucket == bucket))
            for bucket in ["settlement_loser", "winner_with_stop_hit", "clean_winner"]
        },
        "variant_summaries": {
            variant.name: summarize_variant_rows(results_by_variant.get(variant.name, []))
            for variant in variants
        },
    }

    payload = {
        "summary": summary,
        "variants": [asdict(variant) for variant in variants],
        "rows": [row for variant in variants for row in results_by_variant.get(variant.name, [])],
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved signal tool variant probe to {output_path}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
