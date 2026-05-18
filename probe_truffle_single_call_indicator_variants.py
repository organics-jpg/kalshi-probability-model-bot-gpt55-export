from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from probe_truffle_ambiguity_router import extract_json_object
from probe_truffle_single_call_context import (
    PROMPT as BASE_PROMPT,
    build_payload as build_base_payload,
    normalize_output,
    summarize_rows,
)
from probe_truffle_two_stage_predictor import build_cases, load_feature_frame, sample_cases
from truffle_regime_lease import resolve_truffle_chat_completion_endpoint, resolve_truffle_model_id

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "truffle_single_call_indicator_variants_latest.json"
DEFAULT_ENDPOINT = "http://192.168.1.234/if2/v1/chat/completions"
DEFAULT_MODEL = "Qwen3.6-35B-A3B"


@dataclass(frozen=True)
class PromptVariant:
    name: str
    prompt_text: str
    include_indicators: bool
    reasoning_enabled: bool
    response_format: str = "json_object"
    max_tokens: int = 110


def build_prompt_variants() -> list[PromptVariant]:
    indicator_prompt = """
You are evaluating one live Kalshi BTC 15 minute trade from a single compact context snapshot.
Return JSON only.

Goal:
- identify trades with high reversal risk before settlement
- identify only the clearest favorable holds
- avoid false green calls
- if mixed or unclear, prefer MEDIUM and UNCLEAR

Interpretation:
- pre_entry fields describe how the market moved into the entry
- post_entry fields describe how the trade is behaving now
- post_entry behavior should matter more than pre_entry context
- technicals.pre_entry and technicals.post_entry are compact technical indicator snapshots
- if technicals.price_series is same_side_mid_5s, bullish signals support the specified side
- if technicals.price_series is btc_spot_1m, bullish BTC usually supports YES and hurts NO, while bearish BTC usually supports NO and hurts YES
- RSI is mainly an exhaustion or recovery clue, not a trigger by itself
- MACD and MACD histogram are mainly continuation or momentum-decay clues
- if current_vs_entry_state is well_below_entry, reversal_risk should usually be HIGH
- if damage_state is heavy, do not use FAVORABLE
- if post_entry is strong but technicals are mixed, prefer UNCLEAR over FAVORABLE
- if post_entry is weak and technicals are deteriorating, reversal_risk should usually be HIGH

Required output:
{
  "reversal_risk": "LOW or MEDIUM or HIGH",
  "settlement_bias": "FAVORABLE or UNCLEAR or UNFAVORABLE",
  "confidence": 0.0,
  "reason_code": "short_code"
}
""".strip()

    indicator_guard_prompt = """
You are evaluating one live Kalshi BTC 15 minute trade from a compact state snapshot.
Return one JSON object only.

Decision order:
1. Post-entry damage and current-vs-entry state matter most.
2. RSI and MACD are secondary confirmation or warning signals.
3. Favor UNCLEAR over aggressive FAVORABLE calls.

Indicator rules:
- overbought + falling RSI is an exhaustion warning
- oversold + rising RSI is a rebound clue
- bullish MACD with positive histogram supports continuation
- bearish MACD with negative histogram warns of deterioration
- one indicator alone should not override clearly weak or clearly strong post-entry behavior

Output schema:
{
  "reversal_risk": "LOW or MEDIUM or HIGH",
  "settlement_bias": "FAVORABLE or UNCLEAR or UNFAVORABLE",
  "confidence": 0.0,
  "reason_code": "short_code"
}
""".strip()

    return [
        PromptVariant(
            name="baseline_json_reasoning_off",
            prompt_text=BASE_PROMPT.strip(),
            include_indicators=False,
            reasoning_enabled=False,
        ),
        PromptVariant(
            name="baseline_json_reasoning_on",
            prompt_text=BASE_PROMPT.strip(),
            include_indicators=False,
            reasoning_enabled=True,
            max_tokens=160,
        ),
        PromptVariant(
            name="indicator_json_reasoning_off",
            prompt_text=indicator_prompt,
            include_indicators=True,
            reasoning_enabled=False,
        ),
        PromptVariant(
            name="indicator_json_reasoning_on",
            prompt_text=indicator_prompt,
            include_indicators=True,
            reasoning_enabled=True,
            max_tokens=160,
        ),
        PromptVariant(
            name="indicator_guard_json_reasoning_off",
            prompt_text=indicator_guard_prompt,
            include_indicators=True,
            reasoning_enabled=False,
        ),
    ]


def issue_json_decision(
    payload: dict[str, Any],
    *,
    endpoint: str,
    model: str,
    timeout_ms: int,
    prompt_text: str,
    max_tokens: int,
    reasoning_enabled: bool,
    response_format: str,
) -> dict[str, Any]:
    resolved_endpoint = resolve_truffle_chat_completion_endpoint(endpoint)
    resolved_model = resolve_truffle_model_id(model, endpoint=resolved_endpoint, timeout_ms=timeout_ms) or model
    request_body: dict[str, Any] = {
        "model": resolved_model,
        "temperature": 0,
        "max_tokens": int(max_tokens),
        "messages": [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": json.dumps(payload, sort_keys=True)},
        ],
        "reasoning": {"enabled": bool(reasoning_enabled)},
    }
    if str(response_format).strip().lower() == "json_object":
        request_body["response_format"] = {"type": "json_object"}

    response = requests.post(
        resolved_endpoint,
        headers={"Content-Type": "application/json"},
        json=request_body,
        timeout=max(1.0, float(timeout_ms) / 1000.0),
    )
    response.raise_for_status()
    body = response.json()
    content = ""
    finish_reason = ""
    usage = body.get("usage") if isinstance(body, dict) and isinstance(body.get("usage"), dict) else {}
    if isinstance(body, dict):
        choices = body.get("choices")
        if isinstance(choices, list) and choices:
            choice = choices[0] if isinstance(choices[0], dict) else {}
            finish_reason = str(choice.get("finish_reason") or "")
            message = choice.get("message") if isinstance(choice, dict) else None
            if isinstance(message, dict):
                content = str(message.get("content") or "")
    parsed = extract_json_object(content)
    return {
        "body": body,
        "content": content,
        "finish_reason": finish_reason,
        "parsed": parsed,
        "usage": usage,
    }


def resample_same_side_mid(feature_df: pd.DataFrame, *, side: str, cutoff: pd.Timestamp) -> pd.Series:
    yes_side = side == "yes"
    bid_col = "yes_bid_cents" if yes_side else "no_bid_cents"
    ask_col = "yes_ask_cents" if yes_side else "no_ask_cents"
    subset = feature_df[feature_df["ts"] <= cutoff][["ts", bid_col, ask_col]].copy()
    subset[bid_col] = pd.to_numeric(subset[bid_col], errors="coerce")
    subset[ask_col] = pd.to_numeric(subset[ask_col], errors="coerce")
    subset = subset.dropna(subset=[bid_col, ask_col])
    if subset.empty:
        return pd.Series(dtype="float64")
    subset["same_mid"] = (subset[bid_col] + subset[ask_col]) / 2.0
    series = subset.set_index("ts")["same_mid"].sort_index().resample("5s").last().ffill().dropna()
    return series.astype("float64")


def bucket_rsi_state(value: float | None) -> str:
    if value is None:
        return "unknown"
    if value >= 70:
        return "overbought"
    if value >= 60:
        return "bullish"
    if value >= 40:
        return "neutral"
    if value >= 30:
        return "bearish"
    return "oversold"


def bucket_delta_state(value: float | None, *, fast: float, slow: float) -> str:
    if value is None:
        return "unknown"
    if value >= fast:
        return "rising_fast"
    if value >= slow:
        return "rising"
    if value <= -fast:
        return "falling_fast"
    if value <= -slow:
        return "falling"
    return "flat"


def bucket_macd_state(macd_line: float | None, signal_line: float | None) -> str:
    if macd_line is None or signal_line is None:
        return "unknown"
    gap = macd_line - signal_line
    if gap >= 0.08:
        return "bullish"
    if gap <= -0.08:
        return "bearish"
    return "neutral"


def bucket_hist_state(hist: float | None, hist_change: float | None) -> str:
    if hist is None or hist_change is None:
        return "unknown"
    if hist >= 0.08 and hist_change >= 0.02:
        return "positive_expanding"
    if hist >= 0.08:
        return "positive_fading"
    if hist <= -0.08 and hist_change <= -0.02:
        return "negative_expanding"
    if hist <= -0.08:
        return "negative_fading"
    return "flat"


def bucket_price_vs_ema_state(value: float | None) -> str:
    if value is None:
        return "unknown"
    if value >= 0.8:
        return "above"
    if value <= -0.8:
        return "below"
    return "near"


def compute_indicator_snapshot(feature_df: pd.DataFrame, *, side: str, cutoff: pd.Timestamp) -> dict[str, Any]:
    series = resample_same_side_mid(feature_df, side=side, cutoff=cutoff)
    if series.empty:
        return {
            "sample_count": 0,
            "price_series": "same_side_mid_5s",
            "rsi14": None,
            "rsi14_state": "unknown",
            "rsi14_slope_state": "unknown",
            "macd_line": None,
            "macd_signal": None,
            "macd_hist": None,
            "macd_state": "unknown",
            "macd_hist_state": "unknown",
            "price_vs_ema21": None,
            "price_vs_ema21_state": "unknown",
        }

    delta = series.diff()
    gain = delta.clip(lower=0).fillna(0.0)
    loss = (-delta.clip(upper=0)).fillna(0.0)
    avg_gain = gain.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    rs = avg_gain / avg_loss.replace(0.0, float("nan"))
    rsi = (100 - (100 / (1 + rs))).clip(lower=0, upper=100).fillna(50.0)

    ema12 = series.ewm(span=12, adjust=False, min_periods=1).mean()
    ema26 = series.ewm(span=26, adjust=False, min_periods=1).mean()
    macd_line = ema12 - ema26
    macd_signal = macd_line.ewm(span=9, adjust=False, min_periods=1).mean()
    macd_hist = macd_line - macd_signal
    ema21 = series.ewm(span=21, adjust=False, min_periods=1).mean()

    last_rsi = float(rsi.iloc[-1]) if not rsi.empty else None
    prev_rsi = float(rsi.iloc[-4]) if len(rsi) >= 4 else last_rsi
    last_macd = float(macd_line.iloc[-1]) if not macd_line.empty else None
    last_signal = float(macd_signal.iloc[-1]) if not macd_signal.empty else None
    last_hist = float(macd_hist.iloc[-1]) if not macd_hist.empty else None
    prev_hist = float(macd_hist.iloc[-4]) if len(macd_hist) >= 4 else last_hist
    last_price_vs_ema = float(series.iloc[-1] - ema21.iloc[-1]) if not ema21.empty else None

    rsi_delta = None if last_rsi is None or prev_rsi is None else last_rsi - prev_rsi
    hist_delta = None if last_hist is None or prev_hist is None else last_hist - prev_hist

    return {
        "sample_count": int(len(series)),
        "price_series": "same_side_mid_5s",
        "rsi14": round(last_rsi, 2) if last_rsi is not None else None,
        "rsi14_state": bucket_rsi_state(last_rsi),
        "rsi14_slope_state": bucket_delta_state(rsi_delta, fast=6.0, slow=1.5),
        "macd_line": round(last_macd, 4) if last_macd is not None else None,
        "macd_signal": round(last_signal, 4) if last_signal is not None else None,
        "macd_hist": round(last_hist, 4) if last_hist is not None else None,
        "macd_state": bucket_macd_state(last_macd, last_signal),
        "macd_hist_state": bucket_hist_state(last_hist, hist_delta),
        "price_vs_ema21": round(last_price_vs_ema, 4) if last_price_vs_ema is not None else None,
        "price_vs_ema21_state": bucket_price_vs_ema_state(last_price_vs_ema),
    }


def has_btc_indicator_columns(feature_df: pd.DataFrame) -> bool:
    wanted = {
        "btc_rsi14_state",
        "btc_macd_state",
        "btc_macd_hist_state",
        "btc_price_vs_ema21_state",
    }
    return wanted.issubset(set(feature_df.columns))


def compute_btc_indicator_snapshot(feature_df: pd.DataFrame, *, cutoff: pd.Timestamp) -> dict[str, Any]:
    subset = feature_df[feature_df["ts"] <= cutoff].copy()
    if subset.empty:
        return {
            "sample_count": 0,
            "price_series": "btc_spot_1m",
            "rsi14": None,
            "rsi14_state": "unknown",
            "rsi14_slope_state": "unknown",
            "macd_line": None,
            "macd_signal": None,
            "macd_hist": None,
            "macd_state": "unknown",
            "macd_hist_state": "unknown",
            "price_vs_ema21": None,
            "price_vs_ema21_state": "unknown",
        }
    valid_mask = pd.Series(False, index=subset.index)
    for col in (
        "btc_close",
        "btc_rsi14",
        "btc_rsi14_state",
        "btc_macd_state",
        "btc_macd_hist_state",
        "btc_price_vs_ema21_state",
    ):
        if col in subset.columns:
            valid_mask = valid_mask | subset[col].notna()
    valid = subset[valid_mask].copy()
    if valid.empty:
        return {
            "sample_count": 0,
            "price_series": "btc_spot_1m",
            "rsi14": None,
            "rsi14_state": "unknown",
            "rsi14_slope_state": "unknown",
            "macd_line": None,
            "macd_signal": None,
            "macd_hist": None,
            "macd_state": "unknown",
            "macd_hist_state": "unknown",
            "price_vs_ema21": None,
            "price_vs_ema21_state": "unknown",
        }
    last_row = valid.iloc[-1]
    sample_count = 0
    if "close_dt" in valid.columns:
        sample_count = int(pd.to_datetime(valid["close_dt"], utc=True, errors="coerce").dropna().nunique())
    elif "btc_close" in valid.columns:
        sample_count = int(valid["btc_close"].notna().sum())
    return {
        "sample_count": int(sample_count),
        "price_series": "btc_spot_1m",
        "rsi14": round(float(last_row["btc_rsi14"]), 2) if pd.notna(last_row.get("btc_rsi14")) else None,
        "rsi14_state": str(last_row.get("btc_rsi14_state") or "unknown"),
        "rsi14_slope_state": str(last_row.get("btc_rsi14_slope_state") or "unknown"),
        "macd_line": round(float(last_row["btc_macd_line"]), 4) if pd.notna(last_row.get("btc_macd_line")) else None,
        "macd_signal": round(float(last_row["btc_macd_signal"]), 4) if pd.notna(last_row.get("btc_macd_signal")) else None,
        "macd_hist": round(float(last_row["btc_macd_hist"]), 4) if pd.notna(last_row.get("btc_macd_hist")) else None,
        "macd_state": str(last_row.get("btc_macd_state") or "unknown"),
        "macd_hist_state": str(last_row.get("btc_macd_hist_state") or "unknown"),
        "price_vs_ema21": round(float(last_row["btc_price_vs_ema21"]), 4) if pd.notna(last_row.get("btc_price_vs_ema21")) else None,
        "price_vs_ema21_state": str(last_row.get("btc_price_vs_ema21_state") or "unknown"),
    }


def build_payload(case: Any, *, seconds: int, include_indicators: bool) -> dict[str, Any]:
    payload = build_base_payload(case, seconds=seconds)
    if not include_indicators:
        return payload
    feature_df = load_feature_frame(case.feature_path)
    as_of = case.entry_dt_local + pd.Timedelta(seconds=int(seconds))
    if has_btc_indicator_columns(feature_df):
        payload["technicals"] = {
            "pre_entry": compute_btc_indicator_snapshot(feature_df, cutoff=case.entry_dt_local),
            "post_entry": compute_btc_indicator_snapshot(feature_df, cutoff=as_of),
        }
        return payload
    payload["technicals"] = {
        "pre_entry": compute_indicator_snapshot(feature_df, side=case.side, cutoff=case.entry_dt_local),
        "post_entry": compute_indicator_snapshot(feature_df, side=case.side, cutoff=as_of),
    }
    return payload


def summarize_variant_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    valid_rows = [row for row in rows if row.get("valid")]
    invalid_rows = [row for row in rows if not row.get("valid")]
    finish_reason_counts = pd.Series([str(row.get("finish_reason") or "") for row in rows]).value_counts(dropna=False).to_dict()
    parse_error_counts = pd.Series([str(row.get("parse_error") or "") for row in invalid_rows]).value_counts(dropna=False).to_dict()
    usage_prompt = [int(row.get("prompt_tokens") or 0) for row in rows if row.get("prompt_tokens") is not None]
    usage_completion = [int(row.get("completion_tokens") or 0) for row in rows if row.get("completion_tokens") is not None]

    summary: dict[str, Any] = {
        "case_count": int(total),
        "valid_count": int(len(valid_rows)),
        "invalid_count": int(len(invalid_rows)),
        "valid_rate": round(len(valid_rows) / max(1, total), 4),
        "finish_reason_counts": {str(key): int(value) for key, value in finish_reason_counts.items()},
        "parse_error_counts": {str(key): int(value) for key, value in parse_error_counts.items()},
        "avg_prompt_tokens": round(sum(usage_prompt) / len(usage_prompt), 2) if usage_prompt else None,
        "avg_completion_tokens": round(sum(usage_completion) / len(usage_completion), 2) if usage_completion else None,
    }
    if rows:
        summary["metrics_all_rows"] = summarize_rows(rows)
    if valid_rows:
        summary["metrics_valid_rows"] = summarize_rows(valid_rows)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare Qwen single-call prompt variants with indicator-enriched payloads.")
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout-ms", type=int, default=45000)
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

    results_by_variant: dict[str, list[dict[str, Any]]] = {variant.name: [] for variant in variants}
    started_at = pd.Timestamp.utcnow().isoformat()

    for variant in variants:
        for case in cases:
            for seconds in delays:
                payload = build_payload(case, seconds=int(seconds), include_indicators=variant.include_indicators)
                start = time.perf_counter()
                parse_error = ""
                finish_reason = ""
                prompt_tokens = None
                completion_tokens = None
                raw_content = ""
                try:
                    response = issue_json_decision(
                        payload,
                        endpoint=str(args.endpoint),
                        model=str(args.model),
                        timeout_ms=int(args.timeout_ms),
                        prompt_text=variant.prompt_text,
                        max_tokens=int(variant.max_tokens),
                        reasoning_enabled=bool(variant.reasoning_enabled),
                        response_format=variant.response_format,
                    )
                    finish_reason = str(response.get("finish_reason") or "")
                    raw_content = str(response.get("content") or "")
                    usage = response.get("usage") if isinstance(response, dict) else {}
                    if isinstance(usage, dict):
                        prompt_tokens = usage.get("prompt_tokens")
                        completion_tokens = usage.get("completion_tokens")
                    output = normalize_output(response.get("parsed") if isinstance(response, dict) else None)
                    if not isinstance(response.get("parsed"), dict):
                        parse_error = "missing_json_object"
                except Exception as exc:
                    output = {
                        "reversal_risk": "MEDIUM",
                        "settlement_bias": "UNCLEAR",
                        "confidence": None,
                        "reason_code": "",
                    }
                    parse_error = f"http_error:{exc}"
                elapsed_seconds = round(time.perf_counter() - start, 3)
                results_by_variant[variant.name].append(
                    {
                        "variant": variant.name,
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
                        "finish_reason": finish_reason,
                        "parse_error": parse_error,
                        "valid": parse_error == "",
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "elapsed_seconds": elapsed_seconds,
                        "raw_content": raw_content,
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

    print(f"Saved indicator variant probe to {output_path}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
