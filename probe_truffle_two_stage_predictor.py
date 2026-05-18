from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd
import requests

from probe_truffle_ambiguity_router import extract_json_object
from truffle_regime_lease import load_prompt_text, resolve_truffle_chat_completion_endpoint, resolve_truffle_model_id

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "truffle_two_stage_predictor_latest.json"
DEFAULT_ENDPOINT = "http://192.168.1.234/if2/v1/chat/completions"
DEFAULT_MODEL = "Qwen3.5-2B"

PRIOR_PROMPT = """You are forecasting one Kalshi BTC 15 minute trade before entry.
Return JSON only.

The candidate trade is a high-side entry near 90 on the specified side.

Definitions:
- reversal_risk means the chance the position later makes a strong adverse move and hits 70 or lower before settlement
- settlement_bias means the chance the specified side still settles in the money

Be conservative.
If unclear, use MEDIUM and UNCLEAR.

Required output:
{
  "reversal_risk": "LOW or MEDIUM or HIGH",
  "settlement_bias": "FAVORABLE or UNCLEAR or UNFAVORABLE",
  "confidence": 0.0,
  "reason_code": "short_code"
}
"""

UPDATE_PROMPT = """You are updating the forecast for one live Kalshi BTC 15 minute trade after entry.
Return JSON only.

Definitions:
- reversal_risk means the chance the position still makes or continues a strong adverse move and hits 70 or lower before settlement
- settlement_bias means the chance the specified side still settles in the money

Use current post-entry state as stronger evidence than the prior.
If prior fields are missing or weak, ignore them.
If mixed or unclear, use MEDIUM and UNCLEAR.

Required output:
{
  "reversal_risk": "LOW or MEDIUM or HIGH",
  "settlement_bias": "FAVORABLE or UNCLEAR or UNFAVORABLE",
  "confidence": 0.0,
  "reason_code": "short_code"
}
"""

VALID_RISKS = {"LOW", "MEDIUM", "HIGH"}
VALID_BIASES = {"FAVORABLE", "UNCLEAR", "UNFAVORABLE"}


@dataclass(frozen=True)
class PredictorCase:
    market: str
    bucket: str
    day: str
    side: str
    entry_fill_cents: float
    settlement_win: bool
    stop_hit_after_entry: bool
    actual_good_trade: bool
    feature_path: str
    entry_dt_local: pd.Timestamp


def issue_json_decision(
    payload: dict[str, Any],
    *,
    endpoint: str,
    model: str,
    timeout_ms: int,
    prompt_text: str,
    max_tokens: int = 80,
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
    return {"content": content, "finish_reason": finish_reason, "parsed": parsed}


def coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def bucket_price(value: float) -> str:
    if value >= 80:
        return "high"
    if value >= 60:
        return "mid"
    if value >= 40:
        return "low"
    return "very_low"


def bucket_spread(value: float) -> str:
    if value <= 2:
        return "tight"
    if value <= 5:
        return "normal"
    return "wide"


def bucket_pressure(value: float) -> str:
    if value >= 0.2:
        return "supports_side"
    if value <= -0.2:
        return "against_side"
    return "neutral"


def bucket_move(value: float) -> str:
    if value >= 2:
        return "up"
    if value <= -2:
        return "down"
    return "flat"


def bucket_volatility(value: float) -> str:
    if value <= 3:
        return "calm"
    if value <= 8:
        return "normal"
    return "fast"


def bucket_open_phase(seconds_to_close: float) -> str:
    if seconds_to_close >= 840:
        return "near_open"
    if seconds_to_close >= 720:
        return "early"
    return "mid_market"


def bucket_current_strength(value: float) -> str:
    if value >= 80:
        return "strong"
    if value >= 62:
        return "recovering"
    return "weak"


def bucket_damage(value: float) -> str:
    if value <= 8:
        return "light"
    if value <= 15:
        return "medium"
    return "heavy"


def bucket_rebound(value: float) -> str:
    if value >= 10:
        return "strong"
    if value >= 5:
        return "moderate"
    return "weak"


def bucket_vs_entry(value: float) -> str:
    if value >= 0:
        return "above_entry"
    if value >= -4:
        return "near_entry"
    if value >= -12:
        return "below_entry"
    return "well_below_entry"


def build_cases(dataset_tag: str, *, entry_low: int, entry_high: int, stop_threshold: float) -> list[PredictorCase]:
    trades = pd.read_csv(ROOT / "stats" / dataset_tag / "trades.csv")
    market_results = pd.read_csv(ROOT / "stats" / dataset_tag / "market_results.csv")[["market", "result"]]
    work = trades.merge(market_results, on="market", how="left", suffixes=("_trade", "_market"))
    work = work[work["entry_trigger_cents"].between(entry_low, entry_high)].copy()

    feature_map = {
        path.parent.name.split("=", 1)[1]: str(path)
        for path in (ROOT / "research_data" / dataset_tag / "features").rglob("part-latest.parquet")
    }
    work = work[work["market"].isin(feature_map)].copy()
    work["entry_dt_local"] = pd.to_datetime(work["entry_ts"]).dt.tz_localize("America/New_York")
    work["day"] = work["entry_dt_local"].dt.strftime("%Y-%m-%d")

    con = duckdb.connect()
    cases: list[PredictorCase] = []
    for _, row in work.sort_values("entry_dt_local").iterrows():
        feature_path = feature_map[str(row["market"])]
        quote_df = con.execute(
            f"select ts, yes_bid_cents, no_bid_cents from read_parquet('{feature_path}') order by ts"
        ).df()
        quote_df["ts"] = pd.to_datetime(quote_df["ts"])
        side = str(row["side"]).lower()
        bid_col = "yes_bid_cents" if side == "yes" else "no_bid_cents"
        series = quote_df[["ts", bid_col]].rename(columns={bid_col: "same_bid"}).dropna()
        series = series[series["ts"] >= row["entry_dt_local"]].copy()
        if series.empty:
            continue
        settlement_win = str(row["result_market"] or "").strip().lower() == side
        stop_hit = bool(float(series["same_bid"].min()) <= float(stop_threshold))
        bucket = "settlement_loser"
        if settlement_win and stop_hit:
            bucket = "winner_with_stop_hit"
        elif settlement_win and not stop_hit:
            bucket = "clean_winner"
        cases.append(
            PredictorCase(
                market=str(row["market"]),
                bucket=bucket,
                day=str(row["day"]),
                side=side,
                entry_fill_cents=coerce_float(row.get("entry_fill_cents_used"), coerce_float(row.get("entry_trigger_cents"), 90.0)),
                settlement_win=bool(settlement_win),
                stop_hit_after_entry=stop_hit,
                actual_good_trade=bool(settlement_win and not stop_hit),
                feature_path=feature_path,
                entry_dt_local=row["entry_dt_local"],
            )
        )
    return cases


def evenly_spaced_subset(cases: list[PredictorCase], max_count: int) -> list[PredictorCase]:
    ordered = sorted(cases, key=lambda item: (item.day, item.market))
    if len(ordered) <= max_count:
        return ordered
    if max_count <= 1:
        return [ordered[0]]
    index_values = sorted({round(i * (len(ordered) - 1) / (max_count - 1)) for i in range(max_count)})
    return [ordered[int(idx)] for idx in index_values]


def sample_cases(cases: list[PredictorCase], *, per_bucket: int, buckets: list[str] | None = None) -> list[PredictorCase]:
    sampled: list[PredictorCase] = []
    bucket_order = buckets or ["settlement_loser", "winner_with_stop_hit", "clean_winner"]
    for bucket in bucket_order:
        bucket_cases = [case for case in cases if case.bucket == bucket]
        sampled.extend(evenly_spaced_subset(bucket_cases, max_count=int(per_bucket)))
    return sorted(sampled, key=lambda item: (item.day, item.market))


def load_feature_frame(feature_path: str) -> pd.DataFrame:
    con = duckdb.connect()
    frame = con.execute(f"select * from read_parquet('{feature_path}') order by ts").df()
    frame["ts"] = pd.to_datetime(frame["ts"])
    return frame


def build_prior_payload(case: PredictorCase, feature_df: pd.DataFrame) -> dict[str, Any]:
    row = feature_df.iloc[0]
    yes_side = case.side == "yes"
    same_bid = coerce_float(row["yes_bid_cents"] if yes_side else row["no_bid_cents"])
    same_ask = coerce_float(row["yes_ask_cents"] if yes_side else row["no_ask_cents"])
    same_move_30s = coerce_float(row["yes_move_30s"] if yes_side else row["no_move_30s"])
    same_range_30s = coerce_float(row["yes_range_30s"] if yes_side else row["no_range_30s"])
    signed_imbalance = coerce_float(row["depth_imbalance"])
    if not yes_side:
        signed_imbalance = -signed_imbalance
    return {
        "schema_version": "market_start_prior_v1",
        "market": case.market,
        "candidate_side": case.side.upper(),
        "candidate_entry_band": "89_91",
        "opening_price_zone": bucket_price(same_bid),
        "opening_spread_state": bucket_spread(same_ask - same_bid),
        "opening_pressure": bucket_pressure(signed_imbalance),
        "opening_move_state": bucket_move(same_move_30s),
        "opening_volatility_state": bucket_volatility(same_range_30s),
        "open_phase": bucket_open_phase(coerce_float(row["seconds_to_close"], 0.0)),
    }


def build_update_payload(case: PredictorCase, feature_df: pd.DataFrame, *, seconds: int, include_prior: bool, prior_output: dict[str, Any] | None) -> dict[str, Any]:
    yes_side = case.side == "yes"
    bid_col = "yes_bid_cents" if yes_side else "no_bid_cents"
    ask_col = "yes_ask_cents" if yes_side else "no_ask_cents"
    series = feature_df[["ts", bid_col, ask_col]].rename(columns={bid_col: "same_bid", ask_col: "same_ask"}).dropna()
    series = series[series["ts"] >= case.entry_dt_local].copy()
    if series.empty:
        fallback = feature_df[["ts", bid_col, ask_col]].rename(columns={bid_col: "same_bid", ask_col: "same_ask"}).dropna()
        if fallback.empty:
            payload: dict[str, Any] = {
                "schema_version": "post_entry_update_v1",
                "market": case.market,
                "side": case.side.upper(),
                "seconds_since_entry": int(seconds),
                "entry_band": "89_91",
                "current_strength": "weak",
                "damage_state": "heavy",
                "rebound_state": "weak",
                "current_vs_entry_state": "well_below_entry",
                "spread_state": "wide",
            }
            if include_prior and isinstance(prior_output, dict):
                payload["prior_reversal_risk"] = str(prior_output.get("reversal_risk") or "MEDIUM")
                payload["prior_settlement_bias"] = str(prior_output.get("settlement_bias") or "UNCLEAR")
            return payload
        series = fallback.iloc[:1].copy()
    horizon = case.entry_dt_local + pd.Timedelta(seconds=int(seconds))
    sub = series[series["ts"] <= horizon].copy()
    if sub.empty:
        sub = series.iloc[:1].copy()
    current_bid = coerce_float(sub.iloc[-1]["same_bid"])
    current_ask = coerce_float(sub.iloc[-1]["same_ask"])
    low_bid = coerce_float(sub["same_bid"].min())
    drop = case.entry_fill_cents - low_bid
    rebound = current_bid - low_bid
    end_vs_entry = current_bid - case.entry_fill_cents
    payload: dict[str, Any] = {
        "schema_version": "post_entry_update_v1",
        "market": case.market,
        "side": case.side.upper(),
        "seconds_since_entry": int(seconds),
        "entry_band": "89_91",
        "current_strength": bucket_current_strength(current_bid),
        "damage_state": bucket_damage(drop),
        "rebound_state": bucket_rebound(rebound),
        "current_vs_entry_state": bucket_vs_entry(end_vs_entry),
        "spread_state": bucket_spread(current_ask - current_bid),
    }
    if include_prior and isinstance(prior_output, dict):
        payload["prior_reversal_risk"] = str(prior_output.get("reversal_risk") or "MEDIUM")
        payload["prior_settlement_bias"] = str(prior_output.get("settlement_bias") or "UNCLEAR")
    return payload


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


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    frame = pd.DataFrame(rows)
    if frame.empty:
        return {"case_count": 0}

    def metric_subset(mask: pd.Series, truth_col: str) -> dict[str, Any]:
        predicted = frame[mask]
        true_count = int(frame[truth_col].sum())
        hit_count = int((mask & frame[truth_col]).sum())
        precision = round(hit_count / len(predicted), 4) if len(predicted) else None
        recall = round(hit_count / true_count, 4) if true_count else None
        return {
            "predicted_count": int(len(predicted)),
            "true_count": true_count,
            "hit_count": hit_count,
            "precision": precision,
            "recall": recall,
        }

    favorable_mask = frame["predicted_settlement_bias"] == "FAVORABLE"
    high_risk_mask = frame["predicted_reversal_risk"] == "HIGH"
    green_mask = (frame["predicted_settlement_bias"] == "FAVORABLE") & (frame["predicted_reversal_risk"] != "HIGH")
    return {
        "case_count": int(len(frame)),
        "settlement_accuracy_binary": round(float((favorable_mask == frame["actual_settlement_win"]).mean()), 4),
        "reversal_accuracy_binary": round(float((high_risk_mask == frame["actual_stop_hit"]).mean()), 4),
        "favorable_metrics": metric_subset(favorable_mask, "actual_settlement_win"),
        "high_risk_metrics": metric_subset(high_risk_mask, "actual_stop_hit"),
        "green_metrics": metric_subset(green_mask, "actual_good_trade"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe two-stage Truffle predictor permutations on historical BTC15m trades.")
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout-ms", type=int, default=20000)
    parser.add_argument("--entry-low", type=int, default=89)
    parser.add_argument("--entry-high", type=int, default=91)
    parser.add_argument("--stop-threshold", type=float, default=70.0)
    parser.add_argument("--per-bucket", type=int, default=8)
    parser.add_argument("--bucket-filter", default="")
    parser.add_argument("--delays", default="0,30,60,120")
    parser.add_argument("--include-no-prior-all-delays", action="store_true")
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    all_cases = build_cases(
        str(args.dataset),
        entry_low=int(args.entry_low),
        entry_high=int(args.entry_high),
        stop_threshold=float(args.stop_threshold),
    )
    bucket_filter = [chunk.strip() for chunk in str(args.bucket_filter).split(",") if chunk.strip()]
    sampled_cases = sample_cases(
        all_cases,
        per_bucket=int(args.per_bucket),
        buckets=bucket_filter or None,
    )
    delays = [int(chunk.strip()) for chunk in str(args.delays).split(",") if chunk.strip()]

    rows: list[dict[str, Any]] = []
    prior_cache: dict[str, dict[str, Any]] = {}
    frame_cache: dict[str, pd.DataFrame] = {}

    for case in sampled_cases:
        feature_df = frame_cache.get(case.market)
        if feature_df is None:
            feature_df = load_feature_frame(case.feature_path)
            frame_cache[case.market] = feature_df

        prior_payload = build_prior_payload(case, feature_df)
        prior_response = issue_json_decision(
            prior_payload,
            endpoint=str(args.endpoint),
            model=str(args.model),
            timeout_ms=int(args.timeout_ms),
            prompt_text=PRIOR_PROMPT,
        )
        prior_output = normalize_output(prior_response.get("parsed") if isinstance(prior_response, dict) else None)
        prior_cache[case.market] = prior_output
        rows.append(
            {
                "case_type": "prior_only",
                "market": case.market,
                "bucket": case.bucket,
                "day": case.day,
                "actual_settlement_win": case.settlement_win,
                "actual_stop_hit": case.stop_hit_after_entry,
                "actual_good_trade": case.actual_good_trade,
                "payload": prior_payload,
                "predicted_reversal_risk": prior_output["reversal_risk"],
                "predicted_settlement_bias": prior_output["settlement_bias"],
                "confidence": prior_output["confidence"],
                "reason_code": prior_output["reason_code"],
                "finish_reason": str(prior_response.get("finish_reason") or ""),
            }
        )

        for seconds in delays:
            update_payload = build_update_payload(
                case,
                feature_df,
                seconds=int(seconds),
                include_prior=True,
                prior_output=prior_output,
            )
            update_response = issue_json_decision(
                update_payload,
                endpoint=str(args.endpoint),
                model=str(args.model),
                timeout_ms=int(args.timeout_ms),
                prompt_text=UPDATE_PROMPT,
            )
            update_output = normalize_output(update_response.get("parsed") if isinstance(update_response, dict) else None)
            rows.append(
                {
                    "case_type": f"prior_plus_update_{seconds}s",
                    "market": case.market,
                    "bucket": case.bucket,
                    "day": case.day,
                    "actual_settlement_win": case.settlement_win,
                    "actual_stop_hit": case.stop_hit_after_entry,
                    "actual_good_trade": case.actual_good_trade,
                    "payload": update_payload,
                    "predicted_reversal_risk": update_output["reversal_risk"],
                    "predicted_settlement_bias": update_output["settlement_bias"],
                    "confidence": update_output["confidence"],
                    "reason_code": update_output["reason_code"],
                    "finish_reason": str(update_response.get("finish_reason") or ""),
                }
            )

        no_prior_delays = delays if bool(args.include_no_prior_all_delays) else ([max(delays)] if delays else [])
        for seconds in no_prior_delays:
            no_prior_payload = build_update_payload(
                case,
                feature_df,
                seconds=int(seconds),
                include_prior=False,
                prior_output=None,
            )
            no_prior_response = issue_json_decision(
                no_prior_payload,
                endpoint=str(args.endpoint),
                model=str(args.model),
                timeout_ms=int(args.timeout_ms),
                prompt_text=UPDATE_PROMPT,
            )
            no_prior_output = normalize_output(no_prior_response.get("parsed") if isinstance(no_prior_response, dict) else None)
            rows.append(
                {
                    "case_type": f"update_{seconds}s_no_prior",
                    "market": case.market,
                    "bucket": case.bucket,
                    "day": case.day,
                    "actual_settlement_win": case.settlement_win,
                    "actual_stop_hit": case.stop_hit_after_entry,
                    "actual_good_trade": case.actual_good_trade,
                    "payload": no_prior_payload,
                    "predicted_reversal_risk": no_prior_output["reversal_risk"],
                    "predicted_settlement_bias": no_prior_output["settlement_bias"],
                    "confidence": no_prior_output["confidence"],
                    "reason_code": no_prior_output["reason_code"],
                    "finish_reason": str(no_prior_response.get("finish_reason") or ""),
                }
            )

    summary: dict[str, Any] = {
        "sampled_case_count": int(len(sampled_cases)),
        "sample_buckets": {
            bucket: int(sum(1 for case in sampled_cases if case.bucket == bucket))
            for bucket in ["settlement_loser", "winner_with_stop_hit", "clean_winner"]
        },
        "bucket_filter": bucket_filter,
        "permutation_summaries": {},
    }
    for case_type in sorted({row["case_type"] for row in rows}):
        summary["permutation_summaries"][case_type] = summarize_rows([row for row in rows if row["case_type"] == case_type])

    payload = {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "dataset": args.dataset,
        "endpoint": args.endpoint,
        "model": args.model,
        "per_bucket": int(args.per_bucket),
        "delays": delays,
        "sampled_markets": [case.market for case in sampled_cases],
        "summary": summary,
        "rows": rows,
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved two-stage predictor probe to {output_path}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
