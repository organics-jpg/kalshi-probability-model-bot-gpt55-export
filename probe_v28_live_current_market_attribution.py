"""Research-only attribution for the newest live v28 market.

This does not place orders or change the live bot. It reads execution telemetry
and separates entry FV evidence, repeated-entry behavior, and exit value for the
most recent live BTC 15m market.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
EVENTS = ROOT / "logs" / "live_mushroom_v28_size2" / "execution_events.ndjson"
STATE = ROOT / "state" / "live_mushroom_v28_size2" / "bot_state.json"
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_live_current_market_attribution_latest.json"
OUT_MD = OUT_DIR / "v28_live_current_market_attribution_latest.md"


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        text = str(value).replace("Z", "+00:00")
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def as_int(value: Any) -> int | None:
    number = as_float(value)
    return int(round(number)) if number is not None else None


def load_events() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not EVENTS.exists():
        return rows
    with EVENTS.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                rows.append(row)
    return rows


def load_state() -> dict[str, Any]:
    if not STATE.exists():
        return {}
    try:
        payload = json.loads(STATE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def latest_market(events: list[dict[str, Any]], state: dict[str, Any]) -> str:
    position = state.get("position") if isinstance(state.get("position"), dict) else None
    if position and position.get("market_ticker"):
        return str(position["market_ticker"])
    candidates = [
        row for row in events
        if row.get("market") and row.get("event_type") in {"mushroom_v28_approved", "fill_full", "exit_reconciled"}
    ]
    candidates.sort(key=lambda row: parse_ts(row.get("ts_wall")) or datetime.min.replace(tzinfo=timezone.utc))
    return str(candidates[-1].get("market")) if candidates else ""


def quality_tags(row: dict[str, Any]) -> list[str]:
    p = as_float(row.get("mushroom_v28_p_side"))
    edge = as_float(row.get("mushroom_v28_edge_cents"))
    abs_d = as_float(row.get("mushroom_v28_abs_d_sigma"))
    stc = as_float(row.get("mushroom_v28_seconds_to_close"))
    depth = as_float(row.get("mushroom_v28_depth_count"))
    book_age = as_float(row.get("mushroom_v28_book_age_ms"))
    tags: list[str] = []
    if p is not None and p >= 0.70:
        tags.append("p70_adjustable")
    if p is not None and p >= 0.85:
        tags.append("live_v28_confident")
    if edge is not None and edge >= 4.0:
        tags.append("edge_ge_4c")
    if edge is not None and edge < 4.0:
        tags.append("thin_edge_lt_4c")
    if abs_d is not None and abs_d >= 0.90:
        tags.append("deep_geometry")
    if abs_d is not None and abs_d < 0.60:
        tags.append("boundary_geometry")
    if stc is not None and stc > 720:
        tags.append("early_gt_12m")
    if stc is not None and 120 <= stc <= 720:
        tags.append("middle_time")
    if depth is not None and depth >= 500:
        tags.append("crowded_or_deep_touch")
    if book_age is not None and book_age >= 500:
        tags.append("older_book_500ms")
    return tags or ["untagged"]


def summarize_entry(row: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "index": index,
        "ts_wall": row.get("ts_wall"),
        "side": row.get("mushroom_v28_side") or row.get("side"),
        "ask_cents": as_int(row.get("mushroom_v28_ask_cents") or row.get("trigger_price_cents")),
        "p_side": as_float(row.get("mushroom_v28_p_side")),
        "edge_cents": as_float(row.get("mushroom_v28_edge_cents")),
        "abs_d_sigma": as_float(row.get("mushroom_v28_abs_d_sigma")),
        "seconds_to_close": as_float(row.get("mushroom_v28_seconds_to_close") or row.get("seconds_to_close")),
        "depth_count": as_float(row.get("mushroom_v28_depth_count")),
        "book_age_ms": as_float(row.get("mushroom_v28_book_age_ms")),
        "btc_age_ms": as_float(row.get("mushroom_v28_btc_age_ms")),
        "tags": quality_tags(row),
    }


def build_report() -> dict[str, Any]:
    events = load_events()
    state = load_state()
    market = latest_market(events, state)
    exchange_market = fetch_exchange_market(market) if market else None
    market_events = [row for row in events if str(row.get("market") or "") == market]
    approvals = [
        row for row in market_events
        if row.get("event_type") == "mushroom_v28_approved" and row.get("mushroom_v28_approved") is True
    ]
    approvals.sort(key=lambda row: parse_ts(row.get("ts_wall")) or datetime.min.replace(tzinfo=timezone.utc))
    entry_fills_raw = [
        row for row in market_events
        if row.get("event_type") == "fill_full" and str(row.get("client_order_id") or "").startswith("btc15m-entry")
    ]
    exit_fills_raw = [
        row for row in market_events
        if row.get("event_type") in {"exit_reconciled", "fill_full"}
        and str(row.get("client_order_id") or "").startswith("btc15m-exit")
    ]
    entry_fills = dedupe_fills(entry_fills_raw)
    exit_fills = dedupe_fills(exit_fills_raw)
    active_position = state.get("position") if isinstance(state.get("position"), dict) else None
    entries = [summarize_entry(row, idx + 1) for idx, row in enumerate(approvals)]
    exit_rows = []
    for row in exit_fills:
        exit_rows.append({
            "ts_wall": row.get("ts_wall"),
            "side": row.get("side"),
            "fill_count": as_int(row.get("fill_count")),
            "trigger_price_cents": as_int(row.get("trigger_price_cents")),
            "decision_reason": row.get("decision_reason"),
            "p_hold": as_float(row.get("mushroom_v28_p_hold")),
            "fair_drawdown_cents": as_float(row.get("mushroom_v28_fair_drawdown_cents")),
            "remaining_position_size": as_int(row.get("remaining_position_size") or row.get("remaining_count")),
        })
    pnl = fifo_pnl(entry_fills, exit_fills)
    settlement_pnl = settlement_adjusted_pnl(pnl, exchange_market)
    high_conf = [row for row in entries if (row.get("p_side") or 0.0) >= 0.70]
    thin = [row for row in entries if (row.get("edge_cents") is not None and row.get("edge_cents") < 4.0)]
    notes = []
    if market:
        notes.append(f"Latest market is {market}.")
    if len(entries) > 1:
        notes.append(f"Same-market repeated entries observed: {len(entries)} approved v28 entries.")
    if high_conf:
        notes.append(f"{len(high_conf)} entries are p70-adjustable FV evidence, but settlement is required before calibration scoring.")
    if thin:
        notes.append(f"{len(thin)} entries have thin edge <4c; track separately from the stronger p70 rows.")
    if active_position:
        notes.append("Live state currently has an open position; mark-to-market is not settlement evidence.")
    if exchange_market and exchange_market.get("result") in {"yes", "no"}:
        notes.append(
            f"Exchange result is {exchange_market.get('result')} with status {exchange_market.get('status')}; "
            "open FIFO lots can be settlement-adjusted for attribution."
        )
    if settlement_pnl.get("open_settlement_gross_cents") is not None:
        notes.append(
            "Settlement-adjusted gross includes unexited open lots using the exchange result; "
            "this is attribution only and does not mutate live bot state."
        )
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "market": market,
        "exchange_market": exchange_market,
        "active_position": active_position,
        "entry_count": len(entries),
        "entry_fill_events": len(entry_fills),
        "exit_fill_events": len(exit_rows),
        "realized_fifo": pnl,
        "settlement_adjusted_fifo": settlement_pnl,
        "entries": entries,
        "exits": exit_rows,
        "notes": notes,
    }


def dedupe_fills(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_order: dict[str, dict[str, Any]] = {}
    anonymous: list[dict[str, Any]] = []
    for row in rows:
        order_key = str(row.get("client_order_id") or row.get("order_id") or "")
        if not order_key:
            anonymous.append(row)
            continue
        current = by_order.get(order_key)
        if current is None:
            by_order[order_key] = row
            continue
        cur_ts = parse_ts(current.get("ts_wall")) or datetime.min.replace(tzinfo=timezone.utc)
        row_ts = parse_ts(row.get("ts_wall")) or datetime.min.replace(tzinfo=timezone.utc)
        current_rank = fill_rank(str(current.get("event_type") or ""))
        row_rank = fill_rank(str(row.get("event_type") or ""))
        if row_rank > current_rank or (row_rank == current_rank and row_ts >= cur_ts):
            by_order[order_key] = row
    out = list(by_order.values()) + anonymous
    out.sort(key=lambda row: parse_ts(row.get("ts_wall")) or datetime.min.replace(tzinfo=timezone.utc))
    return out


def fill_rank(event_type: str) -> int:
    ranks = {
        "fill_full": 4,
        "exit_reconciled": 3,
        "exit_submit_success": 2,
        "order_submit_success": 2,
    }
    return ranks.get(event_type, 1)


def row_price(row: dict[str, Any]) -> int | None:
    return as_int(
        row.get("actual_fill_price_cents")
        or row.get("trigger_price_cents")
        or row.get("top_of_book_limit_cents")
        or row.get("cap_price_cents")
    )


def fifo_pnl(entry_fills: list[dict[str, Any]], exit_fills: list[dict[str, Any]]) -> dict[str, Any]:
    lots: list[dict[str, Any]] = []
    realized = 0
    realized_qty = 0
    for row in entry_fills:
        qty = as_int(row.get("fill_count") or row.get("position_size")) or 0
        price = row_price(row)
        if qty <= 0 or price is None:
            continue
        lots.append({"qty": qty, "price": price, "side": row.get("side"), "ts_wall": row.get("ts_wall")})
    for row in exit_fills:
        qty = as_int(row.get("fill_count") or row.get("position_size")) or 0
        price = row_price(row)
        if qty <= 0 or price is None:
            continue
        remaining = qty
        while remaining > 0 and lots:
            lot = lots[0]
            take = min(remaining, int(lot["qty"]))
            realized += take * (price - int(lot["price"]))
            realized_qty += take
            lot["qty"] = int(lot["qty"]) - take
            remaining -= take
            if int(lot["qty"]) <= 0:
                lots.pop(0)
        if remaining > 0:
            break
    open_qty = sum(int(lot["qty"]) for lot in lots)
    open_cost_cents = sum(int(lot["qty"]) * int(lot["price"]) for lot in lots)
    return {
        "realized_qty": realized_qty,
        "realized_gross_cents_ex_fees": realized,
        "open_qty": open_qty,
        "open_cost_cents": open_cost_cents,
        "open_lots": lots,
    }


def fetch_exchange_market(market: str) -> dict[str, Any] | None:
    try:
        from kalshi_btc15m_bot_ws import KalshiClient, load_config

        payload = KalshiClient(load_config()).get_market(market)
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    return {
        "ticker": payload.get("ticker"),
        "status": payload.get("status"),
        "result": str(payload.get("result") or "").strip().lower(),
        "close_time": payload.get("close_time"),
        "settlement_ts": payload.get("settlement_ts"),
    }


def settlement_adjusted_pnl(pnl: dict[str, Any], exchange_market: dict[str, Any] | None) -> dict[str, Any]:
    result = str((exchange_market or {}).get("result") or "").strip().lower()
    if result not in {"yes", "no"}:
        return {
            "exchange_result": result or None,
            "realized_gross_cents_ex_fees": pnl.get("realized_gross_cents_ex_fees"),
            "open_settlement_gross_cents": None,
            "total_gross_cents_ex_fees": pnl.get("realized_gross_cents_ex_fees"),
        }
    open_gross = 0
    for lot in pnl.get("open_lots") or []:
        qty = as_int(lot.get("qty")) or 0
        price = as_int(lot.get("price"))
        side = str(lot.get("side") or "").strip().lower()
        if qty <= 0 or price is None or side not in {"yes", "no"}:
            continue
        payout = 100 if side == result else 0
        open_gross += qty * (payout - price)
    realized = as_int(pnl.get("realized_gross_cents_ex_fees")) or 0
    return {
        "exchange_result": result,
        "realized_gross_cents_ex_fees": realized,
        "open_settlement_gross_cents": open_gross,
        "total_gross_cents_ex_fees": realized + open_gross,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Live Current Market Attribution",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Market: `{report.get('market')}`",
        f"- Entry approvals / entry fill events / exit fill events: `{report.get('entry_count')}/{report.get('entry_fill_events')}/{report.get('exit_fill_events')}`",
        f"- Active position: `{json.dumps(report.get('active_position'), sort_keys=True, default=str)}`",
        f"- FIFO realized gross ex-fees: `{(report.get('realized_fifo') or {}).get('realized_gross_cents_ex_fees')}c` on `{(report.get('realized_fifo') or {}).get('realized_qty')}` exited contracts; open qty `{(report.get('realized_fifo') or {}).get('open_qty')}`",
        f"- Exchange status/result: `{(report.get('exchange_market') or {}).get('status')}/{(report.get('exchange_market') or {}).get('result')}`",
        f"- Settlement-adjusted gross ex-fees: `{(report.get('settlement_adjusted_fifo') or {}).get('total_gross_cents_ex_fees')}c`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("notes") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Entries",
        "",
        "| # | ts | side | ask | p | edge c | abs d | stc | depth | book age | tags |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("entries") or []:
        lines.append(
            f"| {row.get('index')} | {row.get('ts_wall')} | {row.get('side')} | {fmt(row.get('ask_cents'))} | "
            f"{fmt(row.get('p_side'))} | {fmt(row.get('edge_cents'))} | {fmt(row.get('abs_d_sigma'))} | "
            f"{fmt(row.get('seconds_to_close'))} | {fmt(row.get('depth_count'))} | {fmt(row.get('book_age_ms'))} | "
            f"{', '.join(row.get('tags') or [])} |"
        )
    lines.extend([
        "",
        "## Exits",
        "",
        "| ts | side | qty | trigger | reason | p hold | fair drawdown | remaining |",
        "|---|---|---:|---:|---|---:|---:|---:|",
    ])
    for row in report.get("exits") or []:
        lines.append(
            f"| {row.get('ts_wall')} | {row.get('side')} | {fmt(row.get('fill_count'))} | "
            f"{fmt(row.get('trigger_price_cents'))} | {row.get('decision_reason')} | {fmt(row.get('p_hold'))} | "
            f"{fmt(row.get('fair_drawdown_cents'))} | {fmt(row.get('remaining_position_size'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
