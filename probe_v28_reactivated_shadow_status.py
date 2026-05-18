"""Status and forward scoring for the reactivated v28 dry-run shadow.

This intentionally scores only the fresh shadow storage tag. It does not select
rules, optimize thresholds, or touch live bot state.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent
STORAGE_TAG = "shadow_mushroom_v28_reactivation_size2"
LOG_PATH = ROOT / "logs" / STORAGE_TAG / "bot.log"
EVENTS_PATH = ROOT / "logs" / STORAGE_TAG / "execution_events.ndjson"
STATE_PATH = ROOT / "state" / STORAGE_TAG / "bot_state.json"
REPORT_PATH = ROOT / "logs" / "edge_research" / "v28_reactivated_shadow_status_latest.md"
JSON_PATH = ROOT / "logs" / "edge_research" / "v28_reactivated_shadow_status_latest.json"
MARKET_RESULT_CACHE_PATH = ROOT / "logs" / "edge_research" / "kalshi_market_result_cache.json"
MARKET_RESULT_ACTIVE_TTL_SECONDS = 180.0
MARKET_RESULT_POST_CLOSE_ACTIVE_TTL_SECONDS = 15.0
EASTERN = ZoneInfo("America/New_York")
BTC15M_TICKER_RE = re.compile(r"^KXBTC15M-(\d{2})([A-Z]{3})(\d{2})(\d{2})(\d{2})-")
MONTHS = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12,
}


@dataclass
class ShadowTrade:
    market: str
    side: str
    qty: int
    entry_cents: int
    exit_cents: int | None = None
    exit_filled_qty: int = 0
    exit_value_cents: int = 0
    entry_ts: str = ""
    exit_ts: str = ""
    entry_reason: str = ""
    exit_reason: str = ""
    entry_features: dict[str, Any] | None = None
    exit_features: dict[str, Any] | None = None


ENTRY_FEATURE_KEYS = [
    "mushroom_v28_p_side",
    "mushroom_v28_edge_cents",
    "mushroom_v28_raw_edge_cents",
    "mushroom_v28_net_edge_cents",
    "mushroom_v28_ask_cents",
    "mushroom_v28_fair_side_cents",
    "mushroom_v28_seconds_to_close",
    "mushroom_v28_d_sigma",
    "mushroom_v28_abs_d_sigma",
    "mushroom_v28_sigma_t_dollars",
    "mushroom_v28_btc_age_ms",
    "mushroom_v28_book_age_ms",
    "mushroom_v28_eligible_depth",
    "mushroom_v28_btc_price",
    "mushroom_v28_strike",
    "mushroom_v28_volshock",
]


EXIT_FEATURE_KEYS = [
    "mushroom_v28_exit_reason",
    "mushroom_v28_exit_bid_cents",
    "mushroom_v28_p_hold",
    "mushroom_v28_fair_hold_cents",
    "mushroom_v28_exit_net_cents",
    "mushroom_v28_hold_net_cents",
    "mushroom_v28_fair_drawdown_cents",
    "mushroom_v28_sigma_t_dollars",
    "mushroom_v28_d_sigma",
    "mushroom_v28_btc_age_ms",
    "mushroom_v28_book_age_ms",
]


def feature_subset(event: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    return {key: event.get(key) for key in keys if key in event}


def read_events() -> list[dict[str, Any]]:
    if not EVENTS_PATH.exists():
        return []
    events: list[dict[str, Any]] = []
    with EVENTS_PATH.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def cache_age_seconds(row: dict[str, Any]) -> float | None:
    fetched_at = str(row.get("fetched_at") or "")
    if not fetched_at:
        return None
    try:
        dt = datetime.fromisoformat(fetched_at)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max(0.0, (datetime.now(timezone.utc) - dt).total_seconds())


def btc15m_close_time_from_ticker(ticker: str) -> datetime | None:
    match = BTC15M_TICKER_RE.match(str(ticker or "").upper())
    if not match:
        return None
    year_s, mon_s, day_s, hour_s, minute_s = match.groups()
    month = MONTHS.get(mon_s)
    if month is None:
        return None
    try:
        local_close = datetime(
            year=2000 + int(year_s),
            month=month,
            day=int(day_s),
            hour=int(hour_s),
            minute=int(minute_s),
            tzinfo=EASTERN,
        )
    except ValueError:
        return None
    return local_close.astimezone(timezone.utc)


def active_cache_ttl_seconds(ticker: str) -> float:
    close_time = btc15m_close_time_from_ticker(ticker)
    if close_time is not None and datetime.now(timezone.utc) >= close_time:
        return MARKET_RESULT_POST_CLOSE_ACTIVE_TTL_SECONDS
    return MARKET_RESULT_ACTIVE_TTL_SECONDS


def load_market_result_cache() -> dict[str, dict[str, Any]]:
    if not MARKET_RESULT_CACHE_PATH.exists():
        return {}
    try:
        payload = json.loads(MARKET_RESULT_CACHE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def save_market_result_cache(cache: dict[str, dict[str, Any]]) -> None:
    MARKET_RESULT_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    MARKET_RESULT_CACHE_PATH.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def market_result(ticker: str) -> tuple[str, str]:
    cache = load_market_result_cache()
    cached = cache.get(ticker)
    if isinstance(cached, dict):
        cached_status = str(cached.get("status") or "")
        cached_result = str(cached.get("result") or "").lower()
        age = cache_age_seconds(cached)
        ttl_seconds = active_cache_ttl_seconds(ticker)
        if cached_status in {"finalized", "settled"} or (age is not None and age <= ttl_seconds):
            return cached_status, cached_result

    url = f"https://api.elections.kalshi.com/trade-api/v2/markets/{ticker}"
    try:
        with urlopen(url, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, TimeoutError, json.JSONDecodeError):
        if isinstance(cached, dict):
            return str(cached.get("status") or ""), str(cached.get("result") or "").lower()
        return "", ""
    market = payload.get("market") if isinstance(payload, dict) else None
    if not isinstance(market, dict):
        market = payload if isinstance(payload, dict) else {}
    status = str(market.get("status") or "")
    result = str(market.get("result") or "").lower()
    cache[ticker] = {
        "status": status,
        "result": result,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    save_market_result_cache(cache)
    return status, result


def reconstruct_trades(events: list[dict[str, Any]]) -> list[ShadowTrade]:
    trades: list[ShadowTrade] = []
    open_trades: dict[tuple[str, str], ShadowTrade] = {}
    pending_entry_reason: dict[tuple[str, str], str] = {}
    pending_entry_features: dict[tuple[str, str], dict[str, Any]] = {}
    pending_exit_reason: dict[tuple[str, str], str] = {}
    pending_exit_features: dict[tuple[str, str], dict[str, Any]] = {}

    for event in events:
        event_type = str(event.get("event_type") or "")
        market = str(event.get("market") or "")
        side = str(event.get("side") or "").lower()
        if not market or side not in {"yes", "no"}:
            continue
        key = (market, side)
        if event_type in {"mushroom_v28_approved", "signal_seen"}:
            reason = str(event.get("decision_reason") or event_type)
            if "mushroom" in reason or event_type == "mushroom_v28_approved":
                pending_entry_reason[key] = reason
                if event_type == "mushroom_v28_approved":
                    pending_entry_features[key] = feature_subset(event, ENTRY_FEATURE_KEYS)
        elif event_type == "exit_signal_seen":
            pending_exit_reason[key] = str(event.get("decision_reason") or event.get("mushroom_v28_exit_reason") or event_type)
            pending_exit_features[key] = feature_subset(event, EXIT_FEATURE_KEYS)
        elif event_type == "fill_full" and str(event.get("decision_reason") or "").startswith("mushroom_v28_"):
            # Exit fills also use fill_full; handle them below using the exit decision reason.
            pass

        is_entry_fill = event_type in {"fill_full", "fill_partial"} and not str(event.get("decision_reason") or "").startswith("mushroom_v28_")
        if is_entry_fill:
            qty = int(event.get("fill_count") or event.get("position_size") or 0)
            price = int(event.get("actual_fill_price_cents") or event.get("top_of_book_limit_cents") or event.get("trigger_price_cents") or 0)
            if qty > 0 and price > 0 and key not in open_trades:
                trade = ShadowTrade(
                    market=market,
                    side=side,
                    qty=qty,
                    entry_cents=price,
                    entry_ts=str(event.get("ts_wall") or ""),
                    entry_reason=pending_entry_reason.get(key, ""),
                    entry_features=pending_entry_features.get(key, {}),
                )
                trades.append(trade)
                open_trades[key] = trade
            continue

        is_exit_fill = event_type == "exit_submit_full"
        if is_exit_fill and key in open_trades:
            trade = open_trades[key]
            price = int(event.get("actual_fill_price_cents") or event.get("top_of_book_limit_cents") or event.get("trigger_price_cents") or 0)
            fill_qty = int(event.get("fill_count") or event.get("position_size") or 0)
            remaining_qty = max(0, trade.qty - trade.exit_filled_qty)
            fill_qty = min(fill_qty, remaining_qty)
            if price > 0 and fill_qty > 0:
                trade.exit_filled_qty += fill_qty
                trade.exit_value_cents += price * fill_qty
                trade.exit_cents = round(trade.exit_value_cents / trade.exit_filled_qty)
                trade.exit_ts = str(event.get("ts_wall") or "")
                trade.exit_reason = pending_exit_reason.get(key, str(event.get("decision_reason") or ""))
                trade.exit_features = pending_exit_features.get(key, {})
                if trade.exit_filled_qty >= trade.qty:
                    open_trades.pop(key, None)

    return sorted(trades, key=lambda t: t.entry_ts)


def score_trade(trade: ShadowTrade) -> dict[str, Any]:
    status, result = market_result(trade.market)
    actual_gross = None
    hold_gross = None
    if trade.exit_filled_qty > 0:
        actual_gross = trade.exit_value_cents - (trade.entry_cents * trade.exit_filled_qty)
    if result in {"yes", "no"}:
        hold_gross = ((100 if result == trade.side else 0) - trade.entry_cents) * trade.qty
        remaining_qty = max(0, trade.qty - trade.exit_filled_qty)
        if remaining_qty > 0:
            settlement_value = 100 if result == trade.side else 0
            actual_gross = (actual_gross or 0) + ((settlement_value - trade.entry_cents) * remaining_qty)
    entry_features = trade.entry_features or {}
    exit_features = trade.exit_features or {}
    btc_age = as_float(entry_features.get("mushroom_v28_btc_age_ms"))
    depth = as_float(entry_features.get("mushroom_v28_eligible_depth"))
    edge = as_float(entry_features.get("mushroom_v28_edge_cents"))
    exit_reason = str(exit_features.get("mushroom_v28_exit_reason") or trade.exit_reason or "")
    exit_sigma = as_float(exit_features.get("mushroom_v28_sigma_t_dollars"))
    exit_drawdown = as_float(exit_features.get("mushroom_v28_fair_drawdown_cents"))
    hypothesis_flags = {
        "h1_entry_btc_fresh": btc_age is not None and btc_age <= 600.0,
        "h2_depth_not_crowded": depth is not None and depth <= 1300.0,
        "prior_guard_entry_pass_edge_depth": (
            edge is not None and edge >= 2.1 and depth is not None and depth <= 1300.0
        ),
        "h3_probability_collapse_turbulence_candidate": (
            exit_reason == "mushroom_v28_probability_collapse_full"
            and exit_sigma is not None
            and exit_sigma >= 50.0
            and exit_drawdown is not None
            and exit_drawdown <= 15.0
        ),
    }
    return {
        "market": trade.market,
        "side": trade.side,
        "qty": trade.qty,
        "entry_cents": trade.entry_cents,
        "exit_cents": trade.exit_cents,
        "exit_filled_qty": trade.exit_filled_qty,
        "status": status,
        "result": result,
        "actual_gross_cents": actual_gross,
        "hold_gross_cents": hold_gross,
        "exit_value_cents": None if actual_gross is None or hold_gross is None else actual_gross - hold_gross,
        "entry_ts": trade.entry_ts,
        "exit_ts": trade.exit_ts,
        "entry_reason": trade.entry_reason,
        "exit_reason": trade.exit_reason,
        "entry_features": entry_features,
        "exit_features": exit_features,
        "hypothesis_flags": hypothesis_flags,
    }


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main() -> None:
    events = read_events()
    trades = reconstruct_trades(events)
    scored = [score_trade(trade) for trade in trades]
    counts = defaultdict(int)
    for event in events:
        counts[str(event.get("event_type") or "")] += 1

    resolved = [row for row in scored if row["actual_gross_cents"] is not None]
    gross = sum(float(row["actual_gross_cents"]) for row in resolved)
    hold = sum(float(row["hold_gross_cents"]) for row in resolved if row["hold_gross_cents"] is not None)
    exit_value = sum(float(row["exit_value_cents"]) for row in resolved if row["exit_value_cents"] is not None)

    payload = {
        "storage_tag": STORAGE_TAG,
        "log_exists": LOG_PATH.exists(),
        "events_path": str(EVENTS_PATH),
        "state_path": str(STATE_PATH),
        "event_counts": dict(sorted(counts.items())),
        "trades": scored,
        "summary": {
            "trades": len(scored),
            "resolved_or_exited": len(resolved),
            "gross_cents": gross,
            "hold_gross_cents": hold,
            "exit_value_cents": exit_value,
        },
    }
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# v28 Reactivated Shadow Status",
        "",
        f"- Storage tag: `{STORAGE_TAG}`",
        f"- Events: `{len(events)}`",
        f"- Trades reconstructed: `{len(scored)}`",
        f"- Resolved/exited scored rows: `{len(resolved)}`",
        f"- Gross P&L: `${gross / 100.0:.2f}`",
        f"- Hold-to-settlement gross on resolved rows: `${hold / 100.0:.2f}`",
        f"- Exit value over hold: `${exit_value / 100.0:.2f}`",
        "",
        "## Event Counts",
        "",
    ]
    for key, value in sorted(counts.items()):
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Trades", ""])
    if scored:
        lines.append("| market | side | entry | exit | status | result | gross c | hold c | exit value c |")
        lines.append("|---|---|---:|---:|---|---|---:|---:|---:|")
        for row in scored:
            lines.append(
                "| {market} | {side} | {entry_cents} | {exit_cents} | {status} | {result} | {actual_gross_cents} | {hold_gross_cents} | {exit_value_cents} |".format(
                    **row
                )
            )
        lines.extend(["", "## Fresh Feature Read", ""])
        for row in scored:
            entry = row["entry_features"]
            exit_f = row["exit_features"]
            flags = row["hypothesis_flags"]
            lines.append(f"### {row['market']}")
            lines.append("")
            lines.append(
                "- Entry: side={side}, ask={ask}, p={p}, edge={edge}, d_sigma={d}, sigma=${sigma}, btc_age_ms={btc_age}, depth={depth}".format(
                    side=row["side"],
                    ask=entry.get("mushroom_v28_ask_cents"),
                    p=entry.get("mushroom_v28_p_side"),
                    edge=entry.get("mushroom_v28_edge_cents"),
                    d=entry.get("mushroom_v28_d_sigma"),
                    sigma=entry.get("mushroom_v28_sigma_t_dollars"),
                    btc_age=entry.get("mushroom_v28_btc_age_ms"),
                    depth=entry.get("mushroom_v28_eligible_depth"),
                )
            )
            lines.append(
                "- Exit: reason={reason}, bid={bid}, p_hold={p_hold}, fair_hold={fair}, fair_drawdown={drawdown}, sigma=${sigma}".format(
                    reason=exit_f.get("mushroom_v28_exit_reason") or row["exit_reason"],
                    bid=exit_f.get("mushroom_v28_exit_bid_cents") or row["exit_cents"],
                    p_hold=exit_f.get("mushroom_v28_p_hold"),
                    fair=exit_f.get("mushroom_v28_fair_hold_cents"),
                    drawdown=exit_f.get("mushroom_v28_fair_drawdown_cents"),
                    sigma=exit_f.get("mushroom_v28_sigma_t_dollars"),
                )
            )
            lines.append(
                "- Hypothesis flags: "
                + ", ".join(f"`{key}={value}`" for key, value in flags.items())
            )
            lines.append("")
    else:
        lines.append("No dry-run v28 fills yet.")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(str(REPORT_PATH))


if __name__ == "__main__":
    main()
