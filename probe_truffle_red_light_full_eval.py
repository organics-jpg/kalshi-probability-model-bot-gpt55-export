from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import pandas as pd

from probe_truffle_signal_tool_variants import (
    build_prompt_variants,
    compact_indicator_payload,
    issue_tool_decision,
    normalize_signal_output,
)
from probe_truffle_single_call_indicator_variants import build_payload
from probe_truffle_two_stage_predictor import build_cases

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "truffle_red_light_full_eval_latest.json"
DEFAULT_ENDPOINT = "http://192.168.1.234/if2/v1/chat/completions"
DEFAULT_MODEL = "Qwen3.6-35B-A3B"


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
    variant: str,
    delay_seconds: int,
    started_at: str,
) -> dict[str, Any]:
    return {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "started_at": started_at,
        "dataset": dataset,
        "endpoint": endpoint,
        "model": model,
        "variant": variant,
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
    variant: str,
    delay_seconds: int,
    started_at: str,
) -> None:
    summary = build_summary(
        rows=rows,
        dataset=dataset,
        endpoint=endpoint,
        model=model,
        variant=variant,
        delay_seconds=delay_seconds,
        started_at=started_at,
    )
    checkpoint_path = output_path.with_suffix(output_path.suffix + ".partial")
    checkpoint_path.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Full historical RED_LIGHT evaluation for one Qwen Truffle variant.")
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout-ms", type=int, default=120000)
    parser.add_argument("--entry-low", type=int, default=89)
    parser.add_argument("--entry-high", type=int, default=92)
    parser.add_argument("--stop-threshold", type=float, default=70.0)
    parser.add_argument("--delay-seconds", type=int, default=90)
    parser.add_argument("--variant", default="signal_baseline_with_indicator_states_reasoning_off")
    parser.add_argument("--bucket-filter", default="")
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--progress-every", type=int, default=1)
    parser.add_argument("--sleep-ms", type=int, default=0)
    args = parser.parse_args()

    variants = {variant.name: variant for variant in build_prompt_variants()}
    if str(args.variant) not in variants:
        raise SystemExit(f"Unknown variant: {args.variant}")
    variant = variants[str(args.variant)]

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
    rows: list[dict[str, Any]] = []
    started_at = pd.Timestamp.utcnow().isoformat()
    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    for index, case in enumerate(cases, start=1):
        payload = build_payload(case, seconds=int(args.delay_seconds), include_indicators=variant.indicator_mode != "none")
        payload = compact_indicator_payload(payload, indicator_mode=variant.indicator_mode)
        strict_baseline_red = evaluate_strict_baseline(payload)
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
                "predicted_decision": output["decision"],
                "predicted_red": output["decision"] == "RED_LIGHT",
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
                "raw_reasoning": raw_reasoning,
            }
        )
        if int(args.progress_every) > 0 and (index % int(args.progress_every) == 0 or index == len(cases)):
            valid = parse_error == ""
            print(
                f"[{index}/{len(cases)}] market={case.market} bucket={case.bucket} "
                f"decision={output['decision']} valid={valid} elapsed={elapsed_seconds}s",
                flush=True,
            )
            write_checkpoint(
                output_path=output_path,
                rows=rows,
                dataset=str(args.dataset),
                endpoint=str(args.endpoint),
                model=str(args.model),
                variant=str(args.variant),
                delay_seconds=int(args.delay_seconds),
                started_at=started_at,
            )
        if int(args.sleep_ms) > 0 and index < len(cases):
            time.sleep(max(0.0, float(args.sleep_ms) / 1000.0))

    summary = build_summary(
        rows=rows,
        dataset=str(args.dataset),
        endpoint=str(args.endpoint),
        model=str(args.model),
        variant=str(args.variant),
        delay_seconds=int(args.delay_seconds),
        started_at=started_at,
    )
    output_path.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2), encoding="utf-8")

    print(f"Saved RED_LIGHT full eval to {output_path}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
