from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from typing import Any

import requests

from truffle_regime_lease import (
    extract_json_dict,
    resolve_truffle_chat_completion_endpoint,
    resolve_truffle_model_id,
    utc_now_iso,
)

POST_ENTRY_SHADOW_DECISION_SCHEMA_VERSION = "post_entry_shadow_decision_v1"
POST_ENTRY_EXIT_SUPERVISOR_DECISION_SCHEMA_VERSION = "post_entry_exit_supervisor_decision_v1"
VALID_RISKS = {"LOW", "MEDIUM", "HIGH"}
VALID_BIASES = {"FAVORABLE", "UNCLEAR", "UNFAVORABLE"}
VALID_EXIT_SUPERVISOR_DECISIONS = {"HOLD", "EXIT_NOW"}
DEFAULT_POST_ENTRY_SHADOW_MAX_TOKENS = 90
POST_ENTRY_EXIT_SUPERVISOR_TOOL_NAME = "emit_exit_supervisor_decision"

DEFAULT_TRUFFLE_POST_ENTRY_SHADOW_PROMPT = """You are evaluating one live Kalshi BTC 15 minute trade from a single compact context snapshot.
Return JSON only.

Goal:
- identify trades with high reversal risk before settlement
- identify only the clearest favorable holds
- avoid false green calls
- if mixed or unclear, prefer MEDIUM and UNCLEAR

Definitions:
- reversal_risk means the chance the position still makes or continues a strong adverse move and hits 70 or lower before settlement
- settlement_bias means the chance the specified side still settles in the money

Interpretation:
- pre_entry fields describe how the market moved into the entry
- post_entry fields describe how the trade is behaving now
- post_entry behavior should matter more than pre_entry context
- optional btc_spot fields are secondary supporting context only
- FAVORABLE should be rare and should require clearly supportive post_entry behavior
- if current_vs_entry_state is well_below_entry, reversal_risk should usually be HIGH
- if damage_state is heavy, do not use FAVORABLE
- if current_strength is strong but current_vs_entry_state is only near_entry or below_entry, that is not enough by itself for FAVORABLE
- a clean FAVORABLE usually needs: current_vs_entry_state above_entry, damage_state light, and rebound_state moderate or strong
- if pre_entry context looks adverse but post_entry is clearly strong, you may still use FAVORABLE
- if uncertain, choose UNCLEAR rather than FAVORABLE

Required output:
{
  "reversal_risk": "LOW or MEDIUM or HIGH",
  "settlement_bias": "FAVORABLE or UNCLEAR or UNFAVORABLE",
  "confidence": 0.0,
  "reason_code": "short_code"
}
"""


def parse_iso(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None


def coerce_float(value: Any, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
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


def bucket_bps_move(value: float) -> str:
    if value >= 60:
        return "up_fast"
    if value >= 20:
        return "up"
    if value <= -60:
        return "down_fast"
    if value <= -20:
        return "down"
    return "flat"


def bucket_bps_range(value: float) -> str:
    if value <= 20:
        return "calm"
    if value <= 60:
        return "normal"
    return "fast"


def bucket_range_location(*, distance_to_high_bps: float | None, distance_to_low_bps: float | None) -> str:
    if distance_to_high_bps is None or distance_to_low_bps is None:
        return "unknown"
    high = float(distance_to_high_bps)
    low = float(distance_to_low_bps)
    if abs(high - low) <= 10:
        return "mid_range"
    if high < low:
        return "upper_range"
    return "lower_range"


def _side_bid_ask(row: dict[str, Any], side: str) -> tuple[float | None, float | None]:
    same_bid_key = "yes_bid" if side == "yes" else "no_bid"
    same_ask_key = "yes_ask" if side == "yes" else "no_ask"
    same_bid = row.get(same_bid_key)
    same_ask = row.get(same_ask_key)
    bid = None if same_bid in (None, "") else coerce_float(same_bid)
    ask = None if same_ask in (None, "") else coerce_float(same_ask)
    return bid, ask


def _rows_for_market(history_rows: list[dict[str, Any]], market_ticker: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in history_rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("market") or "") != str(market_ticker or ""):
            continue
        ts = parse_iso(row.get("ts"))
        if ts is None:
            continue
        rows.append({**row, "_ts": ts})
    rows.sort(key=lambda item: item["_ts"])
    return rows


def _first_row_on_or_after(rows: list[dict[str, Any]], threshold: datetime) -> dict[str, Any] | None:
    for row in rows:
        if row["_ts"] >= threshold:
            return row
    return None


def _collect_valid_side_rows(rows: list[dict[str, Any]], *, side: str) -> list[dict[str, Any]]:
    collected: list[dict[str, Any]] = []
    for row in rows:
        same_bid, same_ask = _side_bid_ask(row, side)
        if same_bid is None or same_ask is None:
            continue
        collected.append(row)
    return collected


def build_pre_entry_context(
    history_rows: list[dict[str, Any]],
    *,
    market_ticker: str,
    side: str,
    entry_dt: datetime,
) -> dict[str, Any]:
    market_rows = _rows_for_market(history_rows, market_ticker)
    side_rows = _collect_valid_side_rows([row for row in market_rows if row["_ts"] <= entry_dt], side=side)
    if not side_rows:
        side_rows = _collect_valid_side_rows(market_rows, side=side)
    if not side_rows:
        return {
            "opening_price_zone": "mid",
            "entry_location_in_range": "mid_range",
            "open_to_entry_runup": "flat_to_small",
            "last30_move_state": "flat",
            "last60_move_state": "flat",
            "entry_spread_state": "normal",
            "entry_pressure_state": "neutral",
            "volatility_state": "normal",
            "entry_timing_state": "mid_entry",
        }
    pre_last = side_rows[-1]
    first_row = side_rows[0]
    open_bid = coerce_float(_side_bid_ask(first_row, side)[0])
    entry_bid = coerce_float(_side_bid_ask(pre_last, side)[0], open_bid)
    same_bids = [coerce_float(_side_bid_ask(row, side)[0], entry_bid) for row in side_rows]
    pre_high = max(same_bids) if same_bids else entry_bid
    pre_low = min(same_bids) if same_bids else entry_bid
    pre_range = pre_high - pre_low
    entry_location = 0.5 if pre_range <= 0 else (entry_bid - pre_low) / pre_range
    window30_row = _first_row_on_or_after(side_rows, entry_dt - timedelta(seconds=30)) or first_row
    window60_row = _first_row_on_or_after(side_rows, entry_dt - timedelta(seconds=60)) or first_row
    pressure = coerce_float(pre_last.get("depth_imbalance"), 0.0)
    if side == "no":
        pressure = -pressure
    seconds_to_close_at_entry = pre_last.get("seconds_to_close")
    seconds_into_market = 0.0
    if first_row.get("seconds_to_close") not in (None, "") and seconds_to_close_at_entry not in (None, ""):
        seconds_into_market = max(
            0.0,
            coerce_float(first_row.get("seconds_to_close")) - coerce_float(seconds_to_close_at_entry),
        )
    else:
        seconds_into_market = max(0.0, (entry_dt - first_row["_ts"]).total_seconds())
    same_ask = coerce_float(_side_bid_ask(pre_last, side)[1], entry_bid)
    return {
        "opening_price_zone": bucket_price(open_bid),
        "entry_location_in_range": bucket_entry_location(entry_location),
        "open_to_entry_runup": bucket_runup(entry_bid - open_bid),
        "last30_move_state": bucket_move(entry_bid - coerce_float(_side_bid_ask(window30_row, side)[0], entry_bid)),
        "last60_move_state": bucket_move(entry_bid - coerce_float(_side_bid_ask(window60_row, side)[0], entry_bid)),
        "entry_spread_state": bucket_spread(same_ask - entry_bid),
        "entry_pressure_state": bucket_pressure(pressure),
        "volatility_state": bucket_volatility(pre_range),
        "entry_timing_state": bucket_seconds_into_market(seconds_into_market),
    }


def build_post_entry_context(
    history_rows: list[dict[str, Any]],
    *,
    market_ticker: str,
    side: str,
    entry_dt: datetime,
    as_of_dt: datetime,
    entry_fill_cents: float,
) -> dict[str, Any]:
    market_rows = _rows_for_market(history_rows, market_ticker)
    side_rows = _collect_valid_side_rows(
        [row for row in market_rows if row["_ts"] >= entry_dt and row["_ts"] <= as_of_dt],
        side=side,
    )
    if not side_rows:
        side_rows = _collect_valid_side_rows(market_rows, side=side)
    if not side_rows:
        return {
            "current_strength": "weak",
            "damage_state": "heavy",
            "rebound_state": "weak",
            "current_vs_entry_state": "well_below_entry",
            "spread_state": "wide",
        }
    current_bid = coerce_float(_side_bid_ask(side_rows[-1], side)[0], entry_fill_cents)
    current_ask = coerce_float(_side_bid_ask(side_rows[-1], side)[1], current_bid)
    low_bid = min(coerce_float(_side_bid_ask(row, side)[0], current_bid) for row in side_rows)
    drop = float(entry_fill_cents) - low_bid
    rebound = current_bid - low_bid
    end_vs_entry = current_bid - float(entry_fill_cents)
    return {
        "current_strength": bucket_current_strength(current_bid),
        "damage_state": bucket_damage(drop),
        "rebound_state": bucket_rebound(rebound),
        "current_vs_entry_state": bucket_vs_entry(end_vs_entry),
        "spread_state": bucket_spread(current_ask - current_bid),
    }


def build_btc_spot_context(snapshot: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        return {}
    last_price = snapshot.get("last_price")
    move_1m_bps = snapshot.get("move_1m_bps")
    move_5m_bps = snapshot.get("move_5m_bps")
    move_15m_bps = snapshot.get("move_15m_bps")
    range_15m_bps = snapshot.get("range_15m_bps")
    distance_to_high_bps = snapshot.get("distance_to_15m_high_bps")
    distance_to_low_bps = snapshot.get("distance_to_15m_low_bps")
    if last_price in (None, ""):
        return {}
    context = {
        "price_zone_15m": bucket_range_location(
            distance_to_high_bps=coerce_float(distance_to_high_bps, 0.0),
            distance_to_low_bps=coerce_float(distance_to_low_bps, 0.0),
        ),
        "move_1m_state": bucket_bps_move(coerce_float(move_1m_bps, 0.0)),
        "move_5m_state": bucket_bps_move(coerce_float(move_5m_bps, 0.0)),
        "move_15m_state": bucket_bps_move(coerce_float(move_15m_bps, 0.0)),
        "range_15m_state": bucket_bps_range(coerce_float(range_15m_bps, 0.0)),
    }
    technical_keys = [
        "rsi14",
        "rsi14_state",
        "rsi14_slope_state",
        "macd_line",
        "macd_signal",
        "macd_hist",
        "macd_state",
        "macd_hist_state",
        "price_vs_ema21",
        "price_vs_ema21_state",
    ]
    for key in technical_keys:
        value = snapshot.get(key)
        if value not in (None, ""):
            context[key] = round(float(value), 4) if isinstance(value, (int, float)) else str(value)
    return context


def current_side_bid_at(
    history_rows: list[dict[str, Any]],
    *,
    market_ticker: str,
    side: str,
    as_of_dt: datetime,
) -> float | None:
    rows = _rows_for_market(history_rows, market_ticker)
    side_rows = _collect_valid_side_rows([row for row in rows if row["_ts"] <= as_of_dt], side=side)
    if not side_rows:
        return None
    bid, _ = _side_bid_ask(side_rows[-1], side)
    return bid


def classify_side_relative_technicals(side: str, snapshot: dict[str, Any] | None) -> dict[str, Any]:
    data = snapshot if isinstance(snapshot, dict) else {}
    yes_side = str(side or "").strip().upper() == "YES"
    score = 0

    rsi = str(data.get("rsi14_state") or "")
    rsi_slope = str(data.get("rsi14_slope_state") or "")
    macd = str(data.get("macd_state") or "")
    hist = str(data.get("macd_hist_state") or "")
    ema = str(data.get("price_vs_ema21_state") or "")

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


def classify_exit_supervisor_slice_tags(
    *,
    side: str,
    pre_entry: dict[str, Any],
    post_entry: dict[str, Any],
    btc_spot: dict[str, Any],
) -> list[str]:
    tags: list[str] = []
    side_upper = str(side or "").strip().upper()
    rsi_state = str(btc_spot.get("rsi14_state") or "")
    macd_state = str(btc_spot.get("macd_state") or "")
    macd_hist_state = str(btc_spot.get("macd_hist_state") or "")
    if str(post_entry.get("current_strength") or "") == "weak":
        tags.append("hard_red_weak_strength")
    if side_upper == "NO" and rsi_state == "neutral" and macd_state == "neutral":
        tags.append("broad_no_neutral_neutral")
        if macd_hist_state == "flat":
            tags.append("broad_no_neutral_neutral_macd_flat")
        if str(pre_entry.get("last60_move_state") or "") == "down":
            tags.append("narrow_no_down_neutral_neutral")
    if str(post_entry.get("damage_state") or "") == "heavy" and str(btc_spot.get("rsi14_slope_state") or "") == "flat":
        tags.append("damage_heavy_rsi_slope_flat")
    return tags


def classify_exit_supervisor_policy_hints(
    *,
    post_entry: dict[str, Any],
    side_relative_technicals: dict[str, Any],
    candidate_slice_tags: list[str],
    seconds_since_entry: float | int | None = None,
) -> dict[str, Any]:
    strength = str(post_entry.get("current_strength") or "").strip()
    vs_entry = str(post_entry.get("current_vs_entry_state") or "").strip()
    damage = str(post_entry.get("damage_state") or "").strip()
    side_tech_state = str(side_relative_technicals.get("state") or "").strip()
    seconds_open = max(0.0, coerce_float(seconds_since_entry, 0.0))

    conservative_hold_guard = (
        strength == "strong"
        and vs_entry == "above_entry"
        and damage in {"light", "medium"}
    )
    early_recovery_window = seconds_open <= 120.0
    recoverable_flush_guard = (
        early_recovery_window
        and strength in {"weak", "recovering"}
        and vs_entry in {"below_entry", "well_below_entry"}
        and damage == "heavy"
        and side_tech_state != "warns_exit"
    )
    exit_pressure = (
        strength in {"weak", "recovering"}
        or vs_entry in {"below_entry", "well_below_entry"}
        or damage == "heavy"
    )
    exit_confirmation_ready = side_tech_state == "warns_exit" and (
        damage == "heavy"
        or vs_entry == "well_below_entry"
        or "damage_heavy_rsi_slope_flat" in candidate_slice_tags
    )

    if conservative_hold_guard:
        default_decision = "HOLD"
        reason = "strong_above_entry_light_or_medium_damage"
    elif recoverable_flush_guard:
        default_decision = "HOLD"
        reason = "early_flush_without_btc_confirmation"
    elif exit_pressure and exit_confirmation_ready:
        default_decision = "EXIT_CANDIDATE"
        reason = "post_entry_damage_confirmed_by_side_technicals"
    else:
        default_decision = "HOLD"
        reason = "insufficient_exit_confirmation"

    return {
        "schema_version": "exit_supervisor_policy_hints_v1",
        "default_decision_hint": default_decision,
        "reason": reason,
        "seconds_since_entry": round(float(seconds_open), 4),
        "early_recovery_window": bool(early_recovery_window),
        "conservative_hold_guard": bool(conservative_hold_guard),
        "recoverable_flush_guard": bool(recoverable_flush_guard),
        "exit_pressure": bool(exit_pressure),
        "exit_confirmation_ready": bool(exit_confirmation_ready),
        "requires_extra_confirmation_for_exit": bool(
            conservative_hold_guard or recoverable_flush_guard or not exit_confirmation_ready
        ),
        "guardrail_note": "false_exit_guard_strong_or_early_flush_without_btc_confirmation",
    }


def classify_exit_supervisor_memory_hint(
    shadow_exit_memory: dict[str, Any] | None,
    candidate_slice_tags: list[str],
) -> dict[str, Any]:
    memory = shadow_exit_memory if isinstance(shadow_exit_memory, dict) else {}
    by_tag = memory.get("candidate_tags") if isinstance(memory.get("candidate_tags"), dict) else {}
    best_tag = ""
    best_count = 0
    best_summary: dict[str, Any] = {}
    for tag in candidate_slice_tags:
        summary = by_tag.get(str(tag)) if isinstance(by_tag.get(str(tag)), dict) else {}
        count = int(summary.get("count") or 0)
        if count > best_count:
            best_tag = str(tag)
            best_count = count
            best_summary = summary

    if not candidate_slice_tags:
        state = "no_candidate_slice"
        reason = "no_same_slice_memory_needed"
    elif best_count < 2:
        state = "insufficient_same_slice_memory"
        reason = "same_slice_count_below_2"
    else:
        last2_delta = float(best_summary.get("last2_delta_sum") or 0.0)
        last3_delta = float(best_summary.get("last3_delta_sum") or 0.0)
        last5_delta = float(best_summary.get("last5_delta_sum") or 0.0)
        last5_false_cost = float(best_summary.get("last5_false_exit_cost_dollars") or 0.0)
        last5_oracle = float(best_summary.get("last5_oracle_exit_value_dollars") or 0.0)
        if bool(best_summary.get("last2_all_positive")) or (best_count >= 3 and last3_delta > 0):
            state = "same_slice_recent_positive"
            reason = "recent_same_slice_exit_delta_positive"
        elif last2_delta < 0 or (best_count >= 5 and last5_delta <= 0):
            state = "same_slice_recent_negative"
            reason = "recent_same_slice_exit_delta_negative"
        elif last5_false_cost > last5_oracle:
            state = "same_slice_false_exit_drag_high"
            reason = "same_slice_false_exit_cost_exceeds_oracle_value"
        else:
            state = "same_slice_mixed"
            reason = "same_slice_memory_mixed"

    return {
        "schema_version": "exit_supervisor_memory_hint_v1",
        "state": state,
        "reason": reason,
        "best_tag": best_tag,
        "same_slice_count": int(best_count),
        "last2_delta_sum": round(float(best_summary.get("last2_delta_sum") or 0.0), 4),
        "last3_delta_sum": round(float(best_summary.get("last3_delta_sum") or 0.0), 4),
        "last5_delta_sum": round(float(best_summary.get("last5_delta_sum") or 0.0), 4),
        "last5_false_exit_cost_dollars": round(float(best_summary.get("last5_false_exit_cost_dollars") or 0.0), 4),
        "last5_oracle_exit_value_dollars": round(float(best_summary.get("last5_oracle_exit_value_dollars") or 0.0), 4),
    }


def build_exit_supervisor_payload(
    *,
    base_payload: dict[str, Any],
    current_exit_bid_cents: float | None,
    candidate_slice_tags: list[str],
    btc_spot: dict[str, Any],
    entry_context: dict[str, Any],
    execution_health: dict[str, Any],
    recent_market_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    side = str(base_payload.get("side") or "").strip().upper()
    side_relative_technicals = classify_side_relative_technicals(side, btc_spot)
    post_entry = base_payload.get("post_entry") if isinstance(base_payload.get("post_entry"), dict) else {}
    recent_context = recent_market_context if isinstance(recent_market_context, dict) else {}
    shadow_exit_memory = recent_context.get("shadow_exit_memory") if isinstance(recent_context.get("shadow_exit_memory"), dict) else {}
    model_recent_context = dict(recent_context)
    model_recent_context.pop("shadow_exit_memory", None)
    payload = {
        "schema_version": "exit_supervisor_live_shadow_v1",
        "market": base_payload.get("market"),
        "side": side,
        "seconds_since_entry": base_payload.get("seconds_since_entry"),
        "current_exit_bid_cents": current_exit_bid_cents,
        "candidate_slice_tags": candidate_slice_tags,
        "supervisor_scope": "shadow_post_entry_suspicious_slice" if candidate_slice_tags else "shadow_post_entry_all_entries",
        "side_relative_technicals": side_relative_technicals,
        "deterministic_policy_hints": classify_exit_supervisor_policy_hints(
            post_entry=post_entry,
            side_relative_technicals=side_relative_technicals,
            candidate_slice_tags=candidate_slice_tags,
            seconds_since_entry=base_payload.get("seconds_since_entry"),
        ),
        "shadow_memory_policy_hint": classify_exit_supervisor_memory_hint(
            shadow_exit_memory,
            candidate_slice_tags,
        ),
        "context": {
            "pre_entry": base_payload.get("pre_entry") or {},
            "post_entry": post_entry,
            "technicals": {"post_entry": btc_spot},
            "entry": entry_context,
            "execution_health": execution_health,
        },
    }
    if model_recent_context:
        payload["context"]["recent_market_context"] = model_recent_context
    return payload
@dataclass
class PostEntryShadowDecision:
    schema_version: str = POST_ENTRY_SHADOW_DECISION_SCHEMA_VERSION
    decision_schema: str = "reversal_risk"
    market: str = ""
    side: str = ""
    seconds_since_entry: int = 0
    decision: str = ""
    reversal_risk: str = "MEDIUM"
    settlement_bias: str = "UNCLEAR"
    confidence: float = 0.0
    reason_code: str = ""
    issued_at: str = ""
    raw_response: str = ""
    parse_error: str = ""
    input_payload: dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return not self.parse_error

    @property
    def is_green(self) -> bool:
        if self.decision_schema == "exit_supervisor":
            return False
        return self.settlement_bias == "FAVORABLE" and self.reversal_risk != "HIGH"

    @property
    def is_red(self) -> bool:
        if self.decision_schema == "exit_supervisor":
            return self.decision == "EXIT_NOW" and self.is_valid
        return self.reversal_risk == "HIGH"

    @property
    def effective_exit_supervisor_decision(self) -> str:
        if self.decision_schema != "exit_supervisor":
            return ""
        return "EXIT_NOW" if self.decision == "EXIT_NOW" and self.is_valid else "HOLD"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def parse_post_entry_shadow_decision(
    parsed: dict[str, Any] | None,
    *,
    input_payload: dict[str, Any],
    raw_response: str,
    decision_schema: str = "reversal_risk",
) -> PostEntryShadowDecision:
    market = str(input_payload.get("market") or "")
    side = str(input_payload.get("side") or "").strip().upper()
    seconds_since_entry = int(coerce_float(input_payload.get("seconds_since_entry"), 0.0))
    normalized_schema = str(decision_schema or "reversal_risk").strip().lower()
    if not isinstance(parsed, dict):
        return PostEntryShadowDecision(
            schema_version=(
                POST_ENTRY_EXIT_SUPERVISOR_DECISION_SCHEMA_VERSION
                if normalized_schema == "exit_supervisor"
                else POST_ENTRY_SHADOW_DECISION_SCHEMA_VERSION
            ),
            decision_schema=normalized_schema,
            market=market,
            side=side,
            seconds_since_entry=seconds_since_entry,
            issued_at=utc_now_iso(),
            raw_response=raw_response,
            reason_code=("parse_failure_default_hold" if normalized_schema == "exit_supervisor" else ""),
            parse_error="missing_json_object",
            input_payload=input_payload,
        )
    if normalized_schema == "exit_supervisor":
        decision = str(parsed.get("decision") or "").strip().upper()
        if decision not in VALID_EXIT_SUPERVISOR_DECISIONS:
            return PostEntryShadowDecision(
                schema_version=POST_ENTRY_EXIT_SUPERVISOR_DECISION_SCHEMA_VERSION,
                decision_schema=normalized_schema,
                market=market,
                side=side,
                seconds_since_entry=seconds_since_entry,
                issued_at=utc_now_iso(),
                raw_response=raw_response,
                reason_code="parse_failure_default_hold",
                parse_error="invalid_exit_supervisor_decision",
                input_payload=input_payload,
            )
        confidence = max(0.0, min(1.0, coerce_float(parsed.get("confidence"), 0.0)))
        reason_code = str(parsed.get("reason_code") or "").strip()
        if not reason_code:
            return PostEntryShadowDecision(
                schema_version=POST_ENTRY_EXIT_SUPERVISOR_DECISION_SCHEMA_VERSION,
                decision_schema=normalized_schema,
                market=market,
                side=side,
                seconds_since_entry=seconds_since_entry,
                decision=decision,
                confidence=confidence,
                issued_at=utc_now_iso(),
                raw_response=raw_response,
                reason_code="parse_failure_default_hold",
                parse_error="missing_reason_code",
                input_payload=input_payload,
            )
        return PostEntryShadowDecision(
            schema_version=POST_ENTRY_EXIT_SUPERVISOR_DECISION_SCHEMA_VERSION,
            decision_schema=normalized_schema,
            market=market,
            side=side,
            seconds_since_entry=seconds_since_entry,
            decision=decision,
            confidence=confidence,
            reason_code=reason_code,
            issued_at=utc_now_iso(),
            raw_response=raw_response,
            input_payload=input_payload,
        )
    reversal_risk = str(parsed.get("reversal_risk") or "").strip().upper()
    settlement_bias = str(parsed.get("settlement_bias") or "").strip().upper()
    if reversal_risk not in VALID_RISKS:
        return PostEntryShadowDecision(
            decision_schema=normalized_schema,
            market=market,
            side=side,
            seconds_since_entry=seconds_since_entry,
            issued_at=utc_now_iso(),
            raw_response=raw_response,
            parse_error="invalid_reversal_risk",
            input_payload=input_payload,
        )
    if settlement_bias not in VALID_BIASES:
        return PostEntryShadowDecision(
            decision_schema=normalized_schema,
            market=market,
            side=side,
            seconds_since_entry=seconds_since_entry,
            issued_at=utc_now_iso(),
            raw_response=raw_response,
            parse_error="invalid_settlement_bias",
            input_payload=input_payload,
        )
    confidence = max(0.0, min(1.0, coerce_float(parsed.get("confidence"), 0.0)))
    return PostEntryShadowDecision(
        decision_schema=normalized_schema,
        market=market,
        side=side,
        seconds_since_entry=seconds_since_entry,
        reversal_risk=reversal_risk,
        settlement_bias=settlement_bias,
        confidence=confidence,
        reason_code=str(parsed.get("reason_code") or "").strip(),
        issued_at=utc_now_iso(),
        raw_response=raw_response,
        input_payload=input_payload,
    )


def extract_tool_arguments(payload: Any, *, tool_name: str) -> dict[str, Any] | None:
    if isinstance(payload, dict):
        tool_calls = payload.get("tool_calls")
        if isinstance(tool_calls, list):
            for tool_call in tool_calls:
                if not isinstance(tool_call, dict):
                    continue
                function = tool_call.get("function")
                if not isinstance(function, dict) or str(function.get("name") or "") != tool_name:
                    continue
                return extract_tool_arguments(function.get("arguments"), tool_name=tool_name)
        message = payload.get("message")
        if isinstance(message, dict):
            found = extract_tool_arguments(message, tool_name=tool_name)
            if found is not None:
                return found
        choices = payload.get("choices")
        if isinstance(choices, list):
            for choice in choices:
                found = extract_tool_arguments(choice, tool_name=tool_name)
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


def build_exit_supervisor_tool_schema() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": POST_ENTRY_EXIT_SUPERVISOR_TOOL_NAME,
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


def issue_truffle_post_entry_shadow(
    payload: dict[str, Any],
    *,
    endpoint: str,
    model: str,
    timeout_ms: int,
    prompt_text: str,
    api_key: str = "",
    max_tokens: int = DEFAULT_POST_ENTRY_SHADOW_MAX_TOKENS,
    decision_schema: str = "reversal_risk",
    output_mode: str = "json",
    reasoning_enabled: str = "false",
) -> PostEntryShadowDecision:
    normalized_schema = str(decision_schema or "reversal_risk").strip().lower()
    resolved_endpoint = resolve_truffle_chat_completion_endpoint(endpoint)
    if not resolved_endpoint:
        return PostEntryShadowDecision(
            schema_version=(
                POST_ENTRY_EXIT_SUPERVISOR_DECISION_SCHEMA_VERSION
                if normalized_schema == "exit_supervisor"
                else POST_ENTRY_SHADOW_DECISION_SCHEMA_VERSION
            ),
            decision_schema=normalized_schema,
            market=str(payload.get("market") or ""),
            side=str(payload.get("side") or "").strip().upper(),
            seconds_since_entry=int(coerce_float(payload.get("seconds_since_entry"), 0.0)),
            issued_at=utc_now_iso(),
            parse_error="missing_endpoint",
            input_payload=payload,
        )
    resolved_model = resolve_truffle_model_id(model, endpoint=resolved_endpoint, timeout_ms=timeout_ms)
    if not resolved_model:
        return PostEntryShadowDecision(
            schema_version=(
                POST_ENTRY_EXIT_SUPERVISOR_DECISION_SCHEMA_VERSION
                if normalized_schema == "exit_supervisor"
                else POST_ENTRY_SHADOW_DECISION_SCHEMA_VERSION
            ),
            decision_schema=normalized_schema,
            market=str(payload.get("market") or ""),
            side=str(payload.get("side") or "").strip().upper(),
            seconds_since_entry=int(coerce_float(payload.get("seconds_since_entry"), 0.0)),
            issued_at=utc_now_iso(),
            parse_error="missing_model",
            input_payload=payload,
        )
    headers = {"Content-Type": "application/json"}
    if str(api_key or "").strip():
        headers["Authorization"] = f"Bearer {str(api_key).strip()}"
    request_body: dict[str, Any] = {
        "model": resolved_model,
        "temperature": 0,
        "max_tokens": max(32, int(max_tokens or DEFAULT_POST_ENTRY_SHADOW_MAX_TOKENS)),
        "messages": [
            {"role": "system", "content": str(prompt_text or DEFAULT_TRUFFLE_POST_ENTRY_SHADOW_PROMPT)},
            {"role": "user", "content": json.dumps(payload, sort_keys=True, separators=(",", ":"))},
        ],
    }
    normalized_output_mode = str(output_mode or "json").strip().lower()
    if normalized_output_mode == "tool" and normalized_schema == "exit_supervisor":
        request_body["tools"] = build_exit_supervisor_tool_schema()
        request_body["tool_choice"] = {
            "type": "function",
            "function": {"name": POST_ENTRY_EXIT_SUPERVISOR_TOOL_NAME},
        }
    else:
        request_body["response_format"] = {"type": "json_object"}
    normalized_reasoning = str(reasoning_enabled or "false").strip().lower()
    if normalized_reasoning in {"true", "false"}:
        request_body["reasoning"] = {"enabled": normalized_reasoning == "true"}
    try:
        response = requests.post(
            resolved_endpoint,
            headers=headers,
            json=request_body,
            timeout=max(1.0, float(timeout_ms) / 1000.0),
        )
        response.raise_for_status()
        raw_response = response.text
        body = response.json()
    except Exception as exc:
        return PostEntryShadowDecision(
            schema_version=(
                POST_ENTRY_EXIT_SUPERVISOR_DECISION_SCHEMA_VERSION
                if normalized_schema == "exit_supervisor"
                else POST_ENTRY_SHADOW_DECISION_SCHEMA_VERSION
            ),
            decision_schema=normalized_schema,
            market=str(payload.get("market") or ""),
            side=str(payload.get("side") or "").strip().upper(),
            seconds_since_entry=int(coerce_float(payload.get("seconds_since_entry"), 0.0)),
            issued_at=utc_now_iso(),
            raw_response="",
            parse_error=f"http_error:{exc}",
            input_payload=payload,
        )
    parsed = None
    if normalized_output_mode == "tool" and normalized_schema == "exit_supervisor":
        parsed = extract_tool_arguments(body, tool_name=POST_ENTRY_EXIT_SUPERVISOR_TOOL_NAME)
        if parsed is None:
            # Qwen sometimes honors the requested JSON contract but returns it in
            # message content instead of the tool-call envelope.
            parsed = extract_json_dict(body)
    else:
        parsed = extract_json_dict(body)
    return parse_post_entry_shadow_decision(
        parsed,
        input_payload=payload,
        raw_response=raw_response,
        decision_schema=normalized_schema,
    )
