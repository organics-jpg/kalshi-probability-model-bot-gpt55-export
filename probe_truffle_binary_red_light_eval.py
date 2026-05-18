from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from probe_truffle_signal_tool_variants import compact_indicator_payload
from probe_truffle_single_call_indicator_variants import build_payload
from probe_truffle_two_stage_predictor import build_cases
from truffle_regime_lease import resolve_truffle_chat_completion_endpoint, resolve_truffle_model_id

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "truffle_binary_red_light_eval_latest.json"
DEFAULT_ENDPOINT = "http://192.168.1.234/if2/v1/chat/completions"
DEFAULT_MODEL = "Qwen3.6-35B-A3B"
RED_TOOL_NAME = "emit_red_light_flag"


def build_red_tool_schema() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": RED_TOOL_NAME,
                "description": "Emit whether the trade should be treated as RED_LIGHT.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "red_light": {"type": "boolean"},
                        "confidence": {"type": "number"},
                        "reason_code": {"type": "string"},
                    },
                    "required": ["red_light", "confidence", "reason_code"],
                    "additionalProperties": False,
                },
            },
        }
    ]


def build_prompt_text() -> str:
    return """
You are the post-entry risk supervisor for a Kalshi BTC 15 minute trading bot.
Decide only whether the open trade deserves a RED_LIGHT warning.
Respond only by calling emit_red_light_flag exactly once. Never answer in normal text.

Meaning:
- red_light=true only when short-term reversal or settlement-failure risk looks materially elevated
- red_light=false for all other cases, including mixed or unclear cases

Priority:
1. post_entry evidence matters most
2. pre_entry evidence is background context
3. technicals are confirmation only

Interpretation:
- if current_vs_entry_state is below_entry or well_below_entry and damage is not light, lean red_light=true
- if damage_state is heavy and the move is adverse relative to the side, lean red_light=true
- if the trade is mixed, recovering, or underdetermined, choose red_light=false
- if technicals.price_series is btc_spot_1m, bullish BTC usually supports YES and hurts NO, while bearish BTC usually supports NO and hurts YES
- do not narrate the trade; call the tool directly

Fields:
- red_light must be true or false
- confidence must be between 0 and 1
- reason_code must be short and machine-friendly
""".strip()


def extract_red_tool_dict(payload: Any) -> dict[str, Any] | None:
    if isinstance(payload, dict):
        tool_calls = payload.get("tool_calls")
        if isinstance(tool_calls, list):
            for tool_call in tool_calls:
                if not isinstance(tool_call, dict):
                    continue
                function = tool_call.get("function")
                if not isinstance(function, dict):
                    continue
                if str(function.get("name") or "").strip() != RED_TOOL_NAME:
                    continue
                return extract_red_tool_dict(function.get("arguments"))
        message = payload.get("message")
        if isinstance(message, dict):
            extracted = extract_red_tool_dict(message)
            if extracted is not None:
                return extracted
        choices = payload.get("choices")
        if isinstance(choices, list):
            for choice in choices:
                extracted = extract_red_tool_dict(choice)
                if extracted is not None:
                    return extracted
        return None
    if isinstance(payload, list):
        for item in payload:
            extracted = extract_red_tool_dict(item)
            if extracted is not None:
                return extracted
        return None
    if isinstance(payload, str):
        text = payload.strip()
        if not text:
            return None
        try:
            parsed = json.loads(text)
        except Exception:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def normalize_red_output(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {"red_light": False, "confidence": None, "reason_code": ""}
    raw_flag = payload.get("red_light")
    if isinstance(raw_flag, bool):
        red_light = raw_flag
    elif isinstance(raw_flag, str):
        red_light = raw_flag.strip().lower() in {"1", "true", "yes", "red", "red_light"}
    else:
        red_light = bool(raw_flag)
    raw_confidence = payload.get("confidence")
    confidence = None
    if isinstance(raw_confidence, (int, float)):
        confidence = max(0.0, min(1.0, float(raw_confidence)))
    reason_code = str(payload.get("reason_code") or "").strip()
    return {
        "red_light": red_light,
        "confidence": confidence,
        "reason_code": reason_code,
    }


def issue_red_decision(
    payload: dict[str, Any],
    *,
    endpoint: str,
    model: str,
    timeout_ms: int,
    prompt_text: str,
    max_tokens: int,
) -> dict[str, Any]:
    resolved_endpoint = resolve_truffle_chat_completion_endpoint(endpoint)
    resolved_model = resolve_truffle_model_id(model, endpoint=resolved_endpoint, timeout_ms=timeout_ms) or model
    request_body: dict[str, Any] = {
        "model": resolved_model,
        "temperature": 0,
        "max_tokens": int(max_tokens),
        "tools": build_red_tool_schema(),
        "tool_choice": "auto",
        "reasoning": {"enabled": False},
        "messages": [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": json.dumps(payload, sort_keys=True, separators=(",", ":"))},
        ],
    }
    response = requests.post(
        resolved_endpoint,
        headers={"Content-Type": "application/json"},
        json=request_body,
        timeout=max(1.0, float(timeout_ms) / 1000.0),
    )
    response.raise_for_status()
    body = response.json()
    finish_reason = ""
    content = ""
    if isinstance(body, dict):
        choices = body.get("choices")
        if isinstance(choices, list) and choices:
            choice = choices[0] if isinstance(choices[0], dict) else {}
            finish_reason = str(choice.get("finish_reason") or "")
            message = choice.get("message") if isinstance(choice, dict) else None
            if isinstance(message, dict):
                content = str(message.get("content") or "")
    parsed = extract_red_tool_dict(body)
    usage = body.get("usage") if isinstance(body, dict) and isinstance(body.get("usage"), dict) else {}
    return {
        "body": body,
        "parsed": parsed,
        "finish_reason": finish_reason,
        "content": content,
        "usage": usage,
    }


def binary_confusion(rows: list[dict[str, Any]], *, pred_key: str, truth_key: str) -> dict[str, Any]:
    if not rows:
        return {
            "case_count": 0,
            "tp": 0,
            "fp": 0,
            "tn": 0,
            "fn": 0,
            "precision": None,
            "recall": None,
            "specificity": None,
            "f1": None,
            "predicted_positive_rate": None,
            "truth_positive_rate": None,
        }
    frame = pd.DataFrame(rows)
    pred = frame[pred_key].fillna(False).astype(bool)
    truth = frame[truth_key].fillna(False).astype(bool)
    tp = int((pred & truth).sum())
    fp = int((pred & (~truth)).sum())
    tn = int(((~pred) & (~truth)).sum())
    fn = int(((~pred) & truth).sum())
    precision = (tp / (tp + fp)) if (tp + fp) else None
    recall = (tp / (tp + fn)) if (tp + fn) else None
    specificity = (tn / (tn + fp)) if (tn + fp) else None
    f1 = (2 * precision * recall / (precision + recall)) if precision is not None and recall is not None and (precision + recall) else None
    return {
        "case_count": int(len(frame)),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": round(float(precision), 4) if precision is not None else None,
        "recall": round(float(recall), 4) if recall is not None else None,
        "specificity": round(float(specificity), 4) if specificity is not None else None,
        "f1": round(float(f1), 4) if f1 is not None else None,
        "predicted_positive_rate": round(float(pred.mean()), 4),
        "truth_positive_rate": round(float(truth.mean()), 4),
    }


def evaluate_strict_baseline(payload: dict[str, Any]) -> bool:
    post = payload.get("post_entry") if isinstance(payload, dict) else {}
    if not isinstance(post, dict):
        return False
    return (
        str(post.get("current_vs_entry_state") or "") == "well_below_entry"
        and str(post.get("damage_state") or "") == "heavy"
        and str(post.get("rebound_state") or "") == "weak"
    )


def build_summary(
    *,
    rows: list[dict[str, Any]],
    dataset: str,
    endpoint: str,
    model: str,
    delay_seconds: int,
    started_at: str,
) -> dict[str, Any]:
    return {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "started_at": started_at,
        "dataset": dataset,
        "endpoint": endpoint,
        "model": model,
        "delay_seconds": delay_seconds,
        "case_count": int(len(rows)),
        "bucket_counts": {
            bucket: int(sum(1 for row in rows if row["bucket"] == bucket))
            for bucket in ["settlement_loser", "winner_with_stop_hit", "clean_winner"]
        },
        "valid_count": int(sum(1 for row in rows if row["valid"])),
        "invalid_count": int(sum(1 for row in rows if not row["valid"])),
        "valid_rate": round(sum(1 for row in rows if row["valid"]) / max(1, len(rows)), 4),
        "finish_reason_counts": pd.Series([str(row.get("finish_reason") or "") for row in rows]).value_counts(dropna=False).to_dict(),
        "qwen_confusions": {
            "settlement_loser": binary_confusion(rows, pred_key="predicted_red", truth_key="actual_settlement_loser"),
            "stop_hit": binary_confusion(rows, pred_key="predicted_red", truth_key="actual_stop_hit"),
            "not_good_trade": binary_confusion(rows, pred_key="predicted_red", truth_key="actual_not_good_trade"),
        },
        "strict_baseline_confusions": {
            "settlement_loser": binary_confusion(rows, pred_key="strict_baseline_red", truth_key="actual_settlement_loser"),
            "stop_hit": binary_confusion(rows, pred_key="strict_baseline_red", truth_key="actual_stop_hit"),
            "not_good_trade": binary_confusion(rows, pred_key="strict_baseline_red", truth_key="actual_not_good_trade"),
        },
    }


def write_checkpoint(
    *,
    output_path: Path,
    rows: list[dict[str, Any]],
    dataset: str,
    endpoint: str,
    model: str,
    delay_seconds: int,
    started_at: str,
) -> None:
    summary = build_summary(
        rows=rows,
        dataset=dataset,
        endpoint=endpoint,
        model=model,
        delay_seconds=delay_seconds,
        started_at=started_at,
    )
    checkpoint_path = output_path.with_suffix(output_path.suffix + ".partial")
    checkpoint_path.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Full historical binary RED_LIGHT evaluation for one Qwen Truffle shape.")
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout-ms", type=int, default=120000)
    parser.add_argument("--entry-low", type=int, default=89)
    parser.add_argument("--entry-high", type=int, default=92)
    parser.add_argument("--stop-threshold", type=float, default=70.0)
    parser.add_argument("--delay-seconds", type=int, default=90)
    parser.add_argument("--bucket-filter", default="")
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--progress-every", type=int, default=1)
    parser.add_argument("--max-tokens", type=int, default=600)
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    cases = build_cases(
        str(args.dataset),
        entry_low=int(args.entry_low),
        entry_high=int(args.entry_high),
        stop_threshold=float(args.stop_threshold),
    )
    bucket_filter = [chunk.strip() for chunk in str(args.bucket_filter).split(",") if chunk.strip()]
    if bucket_filter:
        cases = [case for case in cases if case.bucket in set(bucket_filter)]
    if int(args.max_cases) > 0:
        cases = cases[: int(args.max_cases)]

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    started_at = pd.Timestamp.utcnow().isoformat()
    prompt_text = build_prompt_text()

    for index, case in enumerate(cases, start=1):
        payload = build_payload(case, seconds=int(args.delay_seconds), include_indicators=True)
        payload = compact_indicator_payload(payload, indicator_mode="states_only")
        strict_baseline_red = evaluate_strict_baseline(payload)
        start = time.perf_counter()
        finish_reason = ""
        parse_error = ""
        prompt_tokens = None
        completion_tokens = None
        raw_content = ""
        try:
            response = issue_red_decision(
                payload,
                endpoint=str(args.endpoint),
                model=str(args.model),
                timeout_ms=int(args.timeout_ms),
                prompt_text=prompt_text,
                max_tokens=int(args.max_tokens),
            )
            finish_reason = str(response.get("finish_reason") or "")
            raw_content = str(response.get("content") or "")
            usage = response.get("usage") if isinstance(response, dict) else {}
            if isinstance(usage, dict):
                prompt_tokens = usage.get("prompt_tokens")
                completion_tokens = usage.get("completion_tokens")
            output = normalize_red_output(response.get("parsed") if isinstance(response, dict) else None)
            if not isinstance(response.get("parsed"), dict):
                parse_error = "missing_tool_call"
        except Exception as exc:
            output = {"red_light": False, "confidence": None, "reason_code": ""}
            parse_error = f"http_error:{exc}"
        elapsed_seconds = round(time.perf_counter() - start, 3)
        rows.append(
            {
                "index": index,
                "market": case.market,
                "bucket": case.bucket,
                "actual_settlement_win": bool(case.settlement_win),
                "actual_settlement_loser": bool(not case.settlement_win),
                "actual_stop_hit": bool(case.stop_hit_after_entry),
                "actual_good_trade": bool(case.actual_good_trade),
                "actual_not_good_trade": bool(not case.actual_good_trade),
                "predicted_red": bool(output["red_light"]),
                "confidence": output["confidence"],
                "reason_code": output["reason_code"],
                "strict_baseline_red": bool(strict_baseline_red),
                "valid": parse_error == "",
                "finish_reason": finish_reason,
                "parse_error": parse_error,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "elapsed_seconds": elapsed_seconds,
                "payload": payload,
                "raw_content": raw_content,
            }
        )
        if int(args.progress_every) > 0 and (index % int(args.progress_every) == 0 or index == len(cases)):
            print(
                f"[{index}/{len(cases)}] market={case.market} bucket={case.bucket} "
                f"red_light={bool(output['red_light'])} valid={parse_error == ''} elapsed={elapsed_seconds}s",
                flush=True,
            )
            write_checkpoint(
                output_path=output_path,
                rows=rows,
                dataset=str(args.dataset),
                endpoint=str(args.endpoint),
                model=str(args.model),
                delay_seconds=int(args.delay_seconds),
                started_at=started_at,
            )

    summary = build_summary(
        rows=rows,
        dataset=str(args.dataset),
        endpoint=str(args.endpoint),
        model=str(args.model),
        delay_seconds=int(args.delay_seconds),
        started_at=started_at,
    )
    output_path.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2), encoding="utf-8")

    print(f"Saved binary RED_LIGHT eval to {output_path}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
