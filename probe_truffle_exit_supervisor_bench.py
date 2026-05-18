from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from truffle_regime_lease import load_prompt_text, resolve_truffle_chat_completion_endpoint, resolve_truffle_model_id

ROOT = Path(__file__).resolve().parent
DEFAULT_BENCH_PATH = ROOT / "logs" / "truffle_exit_supervisor_bench_latest.json"
DEFAULT_PROMPT_PATH = ROOT / "truffle_exit_supervisor_prompt.txt"
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "truffle_exit_supervisor_bench_eval_latest.json"
DEFAULT_ENDPOINT = "http://192.168.1.234/if2/v1/chat/completions"
DEFAULT_MODEL = "Qwen3.6-35B-A3B"
TOOL_NAME = "emit_exit_supervisor_decision"


def build_tool_schema() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": TOOL_NAME,
                "description": "Emit one post-entry exit-supervisor decision.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "decision": {"type": "string", "enum": ["HOLD", "EXIT_NOW"]},
                        "confidence": {"type": "number"},
                        "reason_code": {"type": "string"},
                    },
                    "required": ["decision", "confidence", "reason_code"],
                    "additionalProperties": False,
                },
            },
        }
    ]


def extract_json_object(text: str) -> dict[str, Any] | None:
    body = str(text or "").strip()
    if not body:
        return None
    start = body.find("{")
    end = body.rfind("}")
    if start < 0 or end < start:
        return None
    try:
        parsed = json.loads(body[start : end + 1])
    except Exception:
        return None
    return parsed if isinstance(parsed, dict) else None


def extract_tool_arguments(payload: Any) -> dict[str, Any] | None:
    if isinstance(payload, dict):
        tool_calls = payload.get("tool_calls")
        if isinstance(tool_calls, list):
            for tool_call in tool_calls:
                if not isinstance(tool_call, dict):
                    continue
                function = tool_call.get("function")
                if not isinstance(function, dict) or str(function.get("name") or "") != TOOL_NAME:
                    continue
                return extract_tool_arguments(function.get("arguments"))
        message = payload.get("message")
        if isinstance(message, dict):
            found = extract_tool_arguments(message)
            if found is not None:
                return found
        choices = payload.get("choices")
        if isinstance(choices, list):
            for choice in choices:
                found = extract_tool_arguments(choice)
                if found is not None:
                    return found
        return None
    if isinstance(payload, str):
        try:
            parsed = json.loads(payload)
        except Exception:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def normalize_decision(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {"decision": None, "confidence": None, "reason_code": "", "is_valid": False}
    raw_decision = str(value.get("decision") or "").strip().upper()
    decision = raw_decision if raw_decision in {"HOLD", "EXIT_NOW"} else None
    raw_confidence = value.get("confidence")
    confidence = None
    if isinstance(raw_confidence, (int, float)):
        confidence = max(0.0, min(1.0, float(raw_confidence)))
    reason_code = str(value.get("reason_code") or "").strip()[:80]
    return {
        "decision": decision,
        "confidence": confidence,
        "reason_code": reason_code,
        "is_valid": bool(decision is not None and confidence is not None and reason_code),
    }


def classify_side_relative_technical(side: str, snapshot: dict[str, Any]) -> dict[str, Any]:
    side_upper = str(side or "").strip().upper()
    yes_side = side_upper == "YES"
    score = 0

    rsi = str(snapshot.get("rsi14_state") or "")
    rsi_slope = str(snapshot.get("rsi14_slope_state") or "")
    macd = str(snapshot.get("macd_state") or "")
    hist = str(snapshot.get("macd_hist_state") or "")
    ema = str(snapshot.get("price_vs_ema21_state") or "")

    if yes_side:
        score += 1 if rsi in {"bullish", "overbought"} else 0
        score -= 1 if rsi in {"bearish", "oversold"} else 0
        score += 1 if rsi_slope in {"rising", "rising_fast"} else 0
        score -= 1 if rsi_slope in {"falling", "falling_fast"} else 0
        score += 1 if macd == "bullish" else 0
        score -= 1 if macd == "bearish" else 0
        score += 1 if hist in {"positive_expanding", "positive_fading"} else 0
        score -= 1 if hist in {"negative_expanding", "negative_fading"} else 0
        score += 1 if ema == "above" else 0
        score -= 1 if ema == "below" else 0
    else:
        score += 1 if rsi in {"bearish", "oversold"} else 0
        score -= 1 if rsi in {"bullish", "overbought"} else 0
        score += 1 if rsi_slope in {"falling", "falling_fast"} else 0
        score -= 1 if rsi_slope in {"rising", "rising_fast"} else 0
        score += 1 if macd == "bearish" else 0
        score -= 1 if macd == "bullish" else 0
        score += 1 if hist in {"negative_expanding", "negative_fading"} else 0
        score -= 1 if hist in {"positive_expanding", "positive_fading"} else 0
        score += 1 if ema == "below" else 0
        score -= 1 if ema == "above" else 0

    if score >= 2:
        state = "supports_hold"
    elif score <= -2:
        state = "warns_exit"
    else:
        state = "mixed"

    return {
        "score": int(score),
        "state": state,
        "macd_hist_relative": (
            "supports_hold"
            if (yes_side and hist in {"positive_expanding", "positive_fading"})
            or ((not yes_side) and hist in {"negative_expanding", "negative_fading"})
            else "warns_exit"
            if (yes_side and hist in {"negative_expanding", "negative_fading"})
            or ((not yes_side) and hist in {"positive_expanding", "positive_fading"})
            else "mixed"
        ),
        "rsi_slope_relative": (
            "supports_hold"
            if (yes_side and rsi_slope in {"rising", "rising_fast"})
            or ((not yes_side) and rsi_slope in {"falling", "falling_fast"})
            else "warns_exit"
            if (yes_side and rsi_slope in {"falling", "falling_fast"})
            or ((not yes_side) and rsi_slope in {"rising", "rising_fast"})
            else "mixed"
        ),
    }


def build_user_payload(row: dict[str, Any]) -> dict[str, Any]:
    context = row.get("payload") or {}
    technicals = context.get("technicals") if isinstance(context, dict) else {}
    post_tech = technicals.get("post_entry") if isinstance(technicals, dict) else {}
    return {
        "schema_version": "exit_supervisor_case_v1",
        "market": row.get("market"),
        "side": row.get("side"),
        "seconds_since_entry": context.get("seconds_since_entry") if isinstance(context, dict) else None,
        "current_exit_bid_cents": row.get("same_bid_at_delay"),
        "candidate_slice_tags": row.get("slice_tags") or [],
        "supervisor_scope": "called_only_after_deterministic_suspicious_slice",
        "side_relative_technicals": classify_side_relative_technical(str(row.get("side") or ""), post_tech if isinstance(post_tech, dict) else {}),
        "context": context,
    }


def build_request_body(*, prompt_text: str, user_payload: dict[str, Any], model: str, mode: str, max_tokens: int) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": model,
        "temperature": 0,
        "max_tokens": int(max_tokens),
        "messages": [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": json.dumps(user_payload, sort_keys=True, separators=(",", ":"))},
        ],
        "reasoning": {"enabled": False},
    }
    if mode == "tool":
        body["tools"] = build_tool_schema()
        body["tool_choice"] = {
            "type": "function",
            "function": {"name": TOOL_NAME},
        }
    else:
        body["response_format"] = {"type": "json_object"}
    return body


def issue_decision(
    *,
    endpoint: str,
    request_body: dict[str, Any],
    timeout_ms: int,
    mode: str,
) -> dict[str, Any]:
    started = time.perf_counter()
    response = requests.post(
        endpoint,
        headers={"Content-Type": "application/json"},
        json=request_body,
        timeout=max(1.0, float(timeout_ms) / 1000.0),
    )
    latency_ms = round((time.perf_counter() - started) * 1000.0, 2)
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
    parsed = extract_tool_arguments(body) if mode == "tool" else extract_json_object(content)
    if parsed is None and mode == "tool":
        parsed = extract_json_object(content)
    usage = body.get("usage") if isinstance(body, dict) and isinstance(body.get("usage"), dict) else {}
    return {
        "latency_ms": latency_ms,
        "finish_reason": finish_reason,
        "content": content,
        "parsed": parsed,
        "usage": usage,
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"case_count": 0}
    frame = pd.DataFrame(rows)
    valid = frame["is_valid"].fillna(False).astype(bool)
    valid_frame = frame.loc[valid].copy()
    pred_exit = valid_frame["decision"].fillna("") == "EXIT_NOW"
    truth_exit = valid_frame["expected_decision"].fillna("") == "EXIT_NOW"
    tp = int((pred_exit & truth_exit).sum())
    fp = int((pred_exit & ~truth_exit).sum())
    tn = int((~pred_exit & ~truth_exit).sum())
    fn = int((~pred_exit & truth_exit).sum())
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    selected = valid_frame[pred_exit].copy()
    return {
        "case_count": int(len(frame)),
        "valid_count": int(valid.sum()),
        "invalid_count": int((~valid).sum()),
        "valid_rate": round(float(valid.mean()), 4),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision_exit_now": round(float(precision), 4) if precision is not None else None,
        "recall_exit_now": round(float(recall), 4) if recall is not None else None,
        "predicted_exit_count": int(pred_exit.sum()),
        "expected_exit_count": int(truth_exit.sum()),
        "shadow_delta_if_predicted_exits_dollars": round(float(selected["delta_dollars"].sum()), 4) if not selected.empty else 0.0,
        "avg_latency_ms": round(float(valid_frame["latency_ms"].mean()), 2) if valid.any() else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay the post-entry exit-supervisor bench through Truffle/Qwen.")
    parser.add_argument("--bench-path", default=str(DEFAULT_BENCH_PATH))
    parser.add_argument("--prompt-path", default=str(DEFAULT_PROMPT_PATH))
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--mode", choices=["tool", "json"], default="tool")
    parser.add_argument("--timeout-ms", type=int, default=60000)
    parser.add_argument("--max-tokens", type=int, default=90)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    bench_path = Path(args.bench_path)
    if not bench_path.is_absolute():
        bench_path = ROOT / bench_path
    prompt_path = Path(args.prompt_path)
    if not prompt_path.is_absolute():
        prompt_path = ROOT / prompt_path
    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path

    bench = json.loads(bench_path.read_text(encoding="utf-8"))
    prompt_text = load_prompt_text(prompt_path)
    rows = list(bench.get("rows") or [])
    if int(args.limit) > 0:
        rows = rows[: int(args.limit)]

    endpoint = resolve_truffle_chat_completion_endpoint(str(args.endpoint))
    resolved_model = str(args.model)
    if not bool(args.dry_run):
        resolved_model = resolve_truffle_model_id(str(args.model), endpoint=endpoint, timeout_ms=int(args.timeout_ms)) or str(args.model)

    output_rows: list[dict[str, Any]] = []
    dry_run_requests: list[dict[str, Any]] = []
    dry_run_request_chars: list[int] = []
    for row in rows:
        user_payload = build_user_payload(row)
        request_body = build_request_body(
            prompt_text=prompt_text,
            user_payload=user_payload,
            model=resolved_model,
            mode=str(args.mode),
            max_tokens=int(args.max_tokens),
        )
        expected_decision = "EXIT_NOW" if str(row.get("shadow_label") or "") == "RED_LIGHT" else "HOLD"
        if bool(args.dry_run):
            approx_request_chars = len(json.dumps(request_body, separators=(",", ":")))
            dry_run_request_chars.append(approx_request_chars)
            dry_run_requests.append(
                {
                    "market": row.get("market"),
                    "expected_decision": expected_decision,
                    "delta_dollars": row.get("delta_dollars"),
                    "request_body": request_body,
                    "approx_request_chars": approx_request_chars,
                }
            )
            continue
        try:
            raw = issue_decision(
                endpoint=endpoint,
                request_body=request_body,
                timeout_ms=int(args.timeout_ms),
                mode=str(args.mode),
            )
            normalized = normalize_decision(raw.get("parsed"))
            error = ""
        except Exception as exc:
            raw = {"latency_ms": None, "finish_reason": "", "content": "", "parsed": None, "usage": {}}
            normalized = normalize_decision(None)
            error = f"{type(exc).__name__}:{exc}"
        output_rows.append(
            {
                "market": row.get("market"),
                "side": row.get("side"),
                "slice_tags": row.get("slice_tags"),
                "expected_decision": expected_decision,
                "shadow_label": row.get("shadow_label"),
                "delta_dollars": row.get("delta_dollars"),
                "decision": normalized["decision"],
                "confidence": normalized["confidence"],
                "reason_code": normalized["reason_code"],
                "is_valid": normalized["is_valid"],
                "latency_ms": raw.get("latency_ms"),
                "finish_reason": raw.get("finish_reason"),
                "content": raw.get("content"),
                "parsed": raw.get("parsed"),
                "usage": raw.get("usage"),
                "error": error,
            }
        )

    payload = {
        "summary": {
            "bench_path": str(bench_path),
            "prompt_path": str(prompt_path),
            "endpoint": endpoint,
            "model": resolved_model,
            "mode": str(args.mode),
            "reasoning_enabled": False,
            "dry_run": bool(args.dry_run),
            **(
                {
                    "dry_run_count": len(dry_run_requests),
                    "approx_request_chars_min": min(dry_run_request_chars) if dry_run_request_chars else None,
                    "approx_request_chars_avg": round(sum(dry_run_request_chars) / len(dry_run_request_chars), 2)
                    if dry_run_request_chars
                    else None,
                    "approx_request_chars_max": max(dry_run_request_chars) if dry_run_request_chars else None,
                }
                if bool(args.dry_run)
                else summarize_rows(output_rows)
            ),
        },
        "rows": output_rows,
        "dry_run_requests": dry_run_requests[:5],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved Truffle exit supervisor bench eval to {output_path}")
    print(json.dumps(payload["summary"], indent=2))


if __name__ == "__main__":
    main()
