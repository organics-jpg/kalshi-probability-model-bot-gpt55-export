#!/usr/bin/env python3
"""Summarize near-miss blockers for the active v28 common-clock live trial."""

from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_common_clock_live_near_miss_latest.json"
OUT_MD = OUT_DIR / "v28_common_clock_live_near_miss_latest.md"

DEFAULT_LOG_SOURCE_TAG = "live_mushroom_v28_common_clock_exit_guard_size1"


REQUIRED_BOOL_FIELDS = [
    "mushroom_v28_time_ok",
    "mushroom_v28_ask_ok",
    "mushroom_v28_balance_ok",
    "mushroom_v28_risk_ok",
    "mushroom_v28_btc_ok",
    "mushroom_v28_edge_ok",
    "mushroom_v28_p_ok",
    "mushroom_v28_model_price_ok",
]


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def load_events(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            rows.append(data)
    return rows


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "ts_wall": row.get("ts_wall"),
        "market": row.get("market"),
        "reason": row.get("decision_reason"),
        "side": row.get("side"),
        "ask_cents": row.get("mushroom_v28_ask_cents"),
        "p_side": row.get("mushroom_v28_p_side"),
        "net_edge_cents": row.get("mushroom_v28_net_edge_cents"),
        "raw_edge_cents": row.get("mushroom_v28_raw_edge_cents"),
        "book_age_ms": row.get("mushroom_v28_book_age_ms"),
        "btc_age_ms": row.get("mushroom_v28_btc_age_ms"),
        "depth_count": row.get("mushroom_v28_depth_count"),
        "p_ok": row.get("mushroom_v28_p_ok"),
        "edge_ok": row.get("mushroom_v28_edge_ok"),
        "book_ok": row.get("mushroom_v28_book_ok"),
        "model_price_ok": row.get("mushroom_v28_model_price_ok"),
        "recross_hazard": row.get("mushroom_v28_feature_gate_recross_hazard_score"),
    }


def main() -> None:
    log_source_tag = os.getenv("V28_COMMON_CLOCK_LOG_SOURCE_TAG", DEFAULT_LOG_SOURCE_TAG).strip() or DEFAULT_LOG_SOURCE_TAG
    execution_events_path = ROOT / "logs" / log_source_tag / "execution_events.ndjson"
    rows = load_events(execution_events_path)
    rejected = [row for row in rows if row.get("event_type") == "mushroom_v28_rejected"]
    order_like = [row for row in rows if str(row.get("event_type") or "").startswith("order_")]
    approved = [row for row in rows if row.get("mushroom_v28_approved") is True]

    by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rejected:
        by_market[str(row.get("market") or "unknown")].append(row)
    latest_market = str(rejected[-1].get("market") or "unknown") if rejected else "unknown"
    latest_rows = by_market.get(latest_market, [])

    def summarize(scope_rows: list[dict[str, Any]]) -> dict[str, Any]:
        reason_counts = Counter(str(row.get("decision_reason") or "unknown") for row in scope_rows)
        source_stale = int(reason_counts.get("btc_stale", 0) + reason_counts.get("book_stale", 0))
        otherwise_approved_book_stale: list[dict[str, Any]] = []
        near_rows: list[dict[str, Any]] = []
        p_values: list[float] = []
        edge_values: list[float] = []
        for row in scope_rows:
            p_side = as_float(row.get("mushroom_v28_p_side"))
            net_edge = as_float(row.get("mushroom_v28_net_edge_cents"), default=-999.0)
            p_values.append(p_side)
            edge_values.append(net_edge)
            all_other_ok = all(row.get(field) is True for field in REQUIRED_BOOL_FIELDS)
            if row.get("decision_reason") == "book_stale" and all_other_ok:
                otherwise_approved_book_stale.append(compact_row(row))
            if p_side >= 0.80 or net_edge >= 2.0 or (p_side >= 0.75 and net_edge >= 1.0):
                near_rows.append(compact_row(row))
        total = len(scope_rows)
        source_stale_share = (source_stale / total) if total else 0.0
        max_p = max(p_values) if p_values else None
        max_edge = max(edge_values) if edge_values else None
        if otherwise_approved_book_stale:
            decision = "review_book_freshness_gate_before_continuing"
        elif approved or order_like:
            decision = "reconcile_order_like_events"
        elif total >= 100 and source_stale_share >= 0.70:
            decision = "source_quality_stop_condition_near_or_met"
        else:
            decision = "continue_collecting_no_threshold_change"
        return {
            "decision": decision,
            "events": total,
            "reason_counts": dict(reason_counts),
            "source_stale_count": source_stale,
            "source_stale_share": source_stale_share,
            "otherwise_approved_book_stale_count": len(otherwise_approved_book_stale),
            "otherwise_approved_book_stale_examples": otherwise_approved_book_stale[-10:],
            "near_rows_count": len(near_rows),
            "near_rows_examples": near_rows[-20:],
            "max_p_side": max_p,
            "max_net_edge_cents": max_edge,
        }

    report = {
        "log_source_tag": log_source_tag,
        "execution_events_path": str(execution_events_path),
        "events_total": len(rows),
        "rejected_total": len(rejected),
        "approved_total": len(approved),
        "order_like_total": len(order_like),
        "latest_market": latest_market,
        "all_rejected": summarize(rejected),
        "latest_market_rejected": summarize(latest_rows),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    latest = report["latest_market_rejected"]
    lines = [
        "# v28 Common-Clock Live Near-Miss",
        "",
        f"- Log source: `{log_source_tag}`",
        f"- Latest market: `{latest_market}`",
        f"- Events/rejected/approved/order-like: `{len(rows)}` / `{len(rejected)}` / `{len(approved)}` / `{len(order_like)}`",
        f"- Latest-market decision: `{latest['decision']}`",
        f"- Latest-market source stale: `{latest['source_stale_count']}/{latest['events']}` ({latest['source_stale_share']:.1%})",
        f"- Otherwise-approved book-stale rows: `{latest['otherwise_approved_book_stale_count']}`",
        f"- Near rows: `{latest['near_rows_count']}`",
        f"- Max p_side / net edge: `{latest['max_p_side']}` / `{latest['max_net_edge_cents']}`",
        "",
        "## Latest-Market Reasons",
        "",
    ]
    for reason, count in sorted(latest["reason_counts"].items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- `{reason}`: `{count}`")
    lines.extend(["", "## Near Rows", ""])
    if latest["near_rows_examples"]:
        for row in latest["near_rows_examples"][-10:]:
            lines.append(
                "- `{ts_wall}` `{reason}` `{side}` ask=`{ask_cents}` p=`{p_side}` edge=`{net_edge_cents}` "
                "book_ms=`{book_age_ms}` p_ok=`{p_ok}` edge_ok=`{edge_ok}` model_price_ok=`{model_price_ok}`".format(**row)
            )
    else:
        lines.append("- none")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT_MD)


if __name__ == "__main__":
    main()
