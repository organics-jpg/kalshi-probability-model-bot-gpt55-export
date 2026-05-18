"""Execution diagnostics for the live v28 common-clock trial.

Observational only: scans the live trial execution ledger, reconciles submitted
orders and fills through Kalshi, and summarizes whether approved signals are
turning into real fills or zero-fill IOC attempts.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
LOG_SOURCE_TAG = os.getenv(
    "V28_COMMON_CLOCK_LOG_SOURCE_TAG",
    "live_mushroom_v28_common_clock_exit_guard_size1",
)
EXECUTION_EVENTS = ROOT / "logs" / LOG_SOURCE_TAG / "execution_events.ndjson"


def env_path(name: str, default: Path) -> Path:
    value = os.getenv(name)
    if not value:
        return default
    return Path(value).expanduser().resolve()


OUT_JSON = env_path(
    "V28_COMMON_CLOCK_EXECUTION_DIAGNOSTICS_JSON",
    OUT_DIR / "v28_common_clock_live_execution_diagnostics_latest.json",
)
OUT_MD = env_path(
    "V28_COMMON_CLOCK_EXECUTION_DIAGNOSTICS_MD",
    OUT_DIR / "v28_common_clock_live_execution_diagnostics_latest.md",
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_events() -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if not EXECUTION_EVENTS.exists():
        return events
    for line in EXECUTION_EVENTS.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)
    return events


def reconcile_orders(order_ids: list[str], tickers: list[str]) -> dict[str, Any]:
    try:
        from kalshi_btc15m_bot_ws import KalshiClient, load_config

        client = KalshiClient(load_config())
        orders = {}
        for order_id in order_ids:
            try:
                orders[order_id] = client.get_order(order_id)
            except Exception as exc:  # noqa: BLE001
                orders[order_id] = {"error": repr(exc)}
        fills_by_market = {}
        for ticker in tickers:
            try:
                fills_by_market[ticker] = client.get_fills(ticker, limit=50)
            except Exception as exc:  # noqa: BLE001
                fills_by_market[ticker] = {"error": repr(exc)}
        return {
            "available": True,
            "orders": orders,
            "fills_by_market": fills_by_market,
        }
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "error": repr(exc)}


def compact_event(event: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "ts_wall",
        "event_type",
        "market",
        "side",
        "trigger_price_cents",
        "top_of_book_limit_cents",
        "time_in_force",
        "decision_reason",
        "result",
        "exchange_status",
        "order_id",
        "client_order_id",
        "fill_count",
        "remaining_count",
        "actual_fill_price_cents",
        "actual_fee_cents",
        "mushroom_v28_p_side",
        "mushroom_v28_edge_cents",
        "mushroom_v28_eligible_depth",
        "book_age_ms",
        "feed_age_ms",
        "local_reaction_ms",
        "book_summary",
    ]
    return {key: event.get(key) for key in keys if key in event}


def build_report() -> dict[str, Any]:
    events = load_events()
    approved = [event for event in events if event.get("event_type") == "mushroom_v28_approved"]
    starts = [event for event in events if event.get("event_type") == "order_submit_start"]
    successes = [event for event in events if event.get("event_type") == "order_submit_success"]
    zero_fills = [
        event
        for event in events
        if event.get("event_type") in {"order_submit_success", "execution_deferred"}
        and int(event.get("fill_count") or 0) == 0
        and (event.get("result") in {"canceled", "ioc_zero_fill"} or event.get("exchange_status") == "canceled")
    ]
    zero_fill_attempt_keys = {
        str(event.get("order_id") or event.get("client_order_id") or f"{event.get('market')}:{event.get('ts_wall')}")
        for event in zero_fills
    }
    filled = [
        event
        for event in events
        if event.get("event_type") in {"fill_partial", "fill_full", "order_submit_success"}
        and int(event.get("fill_count") or 0) > 0
    ]
    order_ids = sorted({str(event.get("order_id")) for event in successes if event.get("order_id")})
    tickers = sorted({str(event.get("market")) for event in approved + successes if event.get("market")})
    reconciliation = reconcile_orders(order_ids, tickers)
    latest_attempt = compact_event((successes or starts or approved or [{}])[-1])
    decision = "watch_wait_for_filled_entry"
    if filled:
        decision = "filled_entry_seen_continue_scoring"
    elif len(zero_fills) >= 3:
        decision = "execution_quality_review_zero_fill_cluster"
    elif zero_fills:
        decision = "watch_zero_fill_execution_quality"
    return {
        "generated_at_utc": utc_now_iso(),
        "decision": decision,
        "counts": {
            "events": len(events),
            "approved_signals": len(approved),
            "order_submit_start": len(starts),
            "order_submit_success": len(successes),
            "zero_fill_events": len(zero_fills),
            "zero_fill_attempts": len(zero_fill_attempt_keys),
            "filled_events": len(filled),
        },
        "latest_attempt": latest_attempt,
        "recent_zero_fills": [compact_event(event) for event in zero_fills[-5:]],
        "recent_fills": [compact_event(event) for event in filled[-5:]],
        "reconciliation": reconciliation,
        "artifacts": {
            "execution_events": str(EXECUTION_EVENTS.relative_to(ROOT)),
        },
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    counts = report["counts"]
    latest = report.get("latest_attempt") or {}
    lines = [
        "# v28 Common-Clock Live Execution Diagnostics",
        "",
        f"- Generated UTC: `{report['generated_at_utc']}`",
        f"- Decision: `{report['decision']}`",
        f"- Approved/order starts/order successes: `{counts['approved_signals']}` / `{counts['order_submit_start']}` / `{counts['order_submit_success']}`",
        f"- Zero-fill attempts/events / filled events: `{counts['zero_fill_attempts']}` / `{counts['zero_fill_events']}` / `{counts['filled_events']}`",
        f"- Latest attempt: `{latest.get('market')}` `{latest.get('side')}` trigger=`{latest.get('trigger_price_cents')}` result=`{latest.get('result')}` status=`{latest.get('exchange_status')}` fills=`{latest.get('fill_count')}`",
        "",
        "## Latest Attempt",
        "",
        "```json",
        json.dumps(latest, indent=2, sort_keys=True, default=str),
        "```",
        "",
        "## Reconciliation",
        "",
        f"- Available: `{(report.get('reconciliation') or {}).get('available')}`",
        f"- Orders checked: `{len((report.get('reconciliation') or {}).get('orders') or {})}`",
        f"- Markets checked for fills: `{len((report.get('reconciliation') or {}).get('fills_by_market') or {})}`",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_report(build_report())
    print(OUT_MD)


if __name__ == "__main__":
    main()
