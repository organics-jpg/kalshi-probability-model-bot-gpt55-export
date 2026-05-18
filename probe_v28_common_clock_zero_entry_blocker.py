"""Classify why the active common-clock live trial has not entered.

This probe is intentionally narrow and operational: it reads the current
sourcefix live-trial execution events, groups rejections by market, and
distinguishes a healthy selective wait from an execution/order-path blocker.
"""
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LOG_TAG = os.getenv(
    "V28_COMMON_CLOCK_LOG_SOURCE_TAG",
    "live_mushroom_v28_common_clock_exit_guard_sourcefix_size1",
)
STRATEGY_TAG = os.getenv(
    "V28_COMMON_CLOCK_STRATEGY_TAG",
    "mushroom_v28_common_clock_exit_guard_v1_sourcefix_size1_live",
)
EVENTS_PATH = ROOT / "logs" / LOG_TAG / "execution_events.ndjson"
OUT_DIR = ROOT / "logs" / "edge_research"


def env_path(name: str, default: Path) -> Path:
    value = os.getenv(name)
    if not value:
        return default
    return Path(value).expanduser().resolve()


OUT_JSON = env_path(
    "V28_COMMON_CLOCK_ZERO_ENTRY_JSON",
    OUT_DIR / "v28_common_clock_zero_entry_blocker_latest.json",
)
OUT_MD = env_path(
    "V28_COMMON_CLOCK_ZERO_ENTRY_MD",
    OUT_DIR / "v28_common_clock_zero_entry_blocker_latest.md",
)
NO_ENTRY_REVIEW_MARKETS = int(os.getenv("V28_COMMON_CLOCK_NO_ENTRY_REVIEW_MARKETS", "8"))
MATURE_MARKET_MIN_SCORED_ROWS = int(os.getenv("V28_COMMON_CLOCK_MATURE_MARKET_MIN_SCORED_ROWS", "50"))


def as_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def load_events() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not EVENTS_PATH.exists():
        return rows
    with EVENTS_PATH.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def market_sort_key(market: str) -> str:
    return market or ""


def all_entry_gates_except(row: dict[str, Any], excluded: set[str]) -> bool:
    checks = {
        "p": bool(row.get("mushroom_v28_p_ok")),
        "edge": bool(row.get("mushroom_v28_edge_ok")),
        "model_price": bool(row.get("mushroom_v28_model_price_ok")),
        "ask": bool(row.get("mushroom_v28_ask_ok")),
        "book": bool(row.get("mushroom_v28_book_ok")),
        "btc": bool(row.get("mushroom_v28_btc_ok")),
        "time": bool(row.get("mushroom_v28_time_ok")),
        "risk": bool(row.get("mushroom_v28_risk_ok")),
        "balance": bool(row.get("mushroom_v28_balance_ok")),
        "block": not bool(row.get("mushroom_v28_block_reason")),
    }
    return all(value for key, value in checks.items() if key not in excluded)


def classify_market(rows: list[dict[str, Any]]) -> dict[str, Any]:
    reasons = Counter(str(row.get("mushroom_v28_reject_reason") or row.get("decision_reason") or row.get("event_type")) for row in rows)
    event_types = Counter(str(row.get("event_type") or "") for row in rows)
    approved = sum(1 for row in rows if row.get("event_type") == "mushroom_v28_approved" or row.get("mushroom_v28_approved") is True)
    order_like = sum(1 for row in rows if "order" in str(row.get("event_type") or "").lower())
    filled = sum(1 for row in rows if row.get("fill_count") or row.get("actual_fill_price_cents") is not None)
    scored = [row for row in rows if row.get("mushroom_v28_status") == "ok"]
    max_p = max((as_float(row.get("mushroom_v28_p_side")) or -1.0 for row in scored), default=None)
    max_edge = max((as_float(row.get("mushroom_v28_edge_cents")) or -999.0 for row in scored), default=None)
    max_raw_edge_prob = max((as_float(row.get("mushroom_v28_feature_gate_raw_edge_prob")) or -999.0 for row in scored), default=None)
    p_true_edge_false = sum(
        1
        for row in scored
        if row.get("mushroom_v28_p_ok") is True
        and (row.get("mushroom_v28_edge_ok") is not True or row.get("mushroom_v28_model_price_ok") is not True)
    )
    edge_true_p_false = sum(
        1
        for row in scored
        if row.get("mushroom_v28_edge_ok") is True
        and row.get("mushroom_v28_model_price_ok") is True
        and row.get("mushroom_v28_p_ok") is not True
    )
    otherwise_approved_book_stale = sum(1 for row in scored if row.get("mushroom_v28_book_ok") is not True and all_entry_gates_except(row, {"book"}))
    otherwise_approved_btc_stale = sum(1 for row in scored if row.get("mushroom_v28_btc_ok") is not True and all_entry_gates_except(row, {"btc"}))
    otherwise_approved_balance = sum(1 for row in scored if row.get("mushroom_v28_balance_ok") is not True and all_entry_gates_except(row, {"balance"}))
    latest_ts = max((str(row.get("ts_wall") or "") for row in rows), default="")
    first_ts = min((str(row.get("ts_wall") or "") for row in rows), default="")
    if approved or order_like or filled:
        decision = "entry_or_order_seen"
    elif otherwise_approved_balance:
        decision = "blocked_by_balance_or_account_state"
    elif otherwise_approved_book_stale or otherwise_approved_btc_stale:
        decision = "blocked_by_source_freshness"
    elif scored and p_true_edge_false and edge_true_p_false:
        decision = "selective_wait_split_probability_vs_price"
    elif scored and edge_true_p_false:
        decision = "selective_wait_probability_floor"
    elif scored and p_true_edge_false:
        decision = "selective_wait_price_or_edge"
    else:
        decision = "warming_or_no_scored_rows"
    return {
        "first_ts": first_ts,
        "latest_ts": latest_ts,
        "events": len(rows),
        "event_types": dict(event_types),
        "reasons": dict(reasons),
        "approved": approved,
        "order_like": order_like,
        "filled": filled,
        "scored_rows": len(scored),
        "max_p_side": max_p,
        "max_edge_cents": max_edge,
        "max_raw_edge_prob": max_raw_edge_prob,
        "p_true_edge_or_price_false_rows": p_true_edge_false,
        "edge_price_true_p_false_rows": edge_true_p_false,
        "otherwise_approved_book_stale": otherwise_approved_book_stale,
        "otherwise_approved_btc_stale": otherwise_approved_btc_stale,
        "otherwise_approved_balance": otherwise_approved_balance,
        "decision": decision,
    }


def build_report() -> dict[str, Any]:
    events = load_events()
    by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in events:
        by_market[str(row.get("market") or "UNKNOWN")].append(row)
    markets = [
        {"market": market, **classify_market(rows)}
        for market, rows in sorted(by_market.items(), key=lambda item: market_sort_key(item[0]))
    ]
    totals = {
        "events": len(events),
        "markets": len(markets),
        "mature_markets": sum(1 for m in markets if int(m.get("scored_rows") or 0) >= MATURE_MARKET_MIN_SCORED_ROWS),
        "approved": sum(m["approved"] for m in markets),
        "order_like": sum(m["order_like"] for m in markets),
        "filled": sum(m["filled"] for m in markets),
        "otherwise_approved_book_stale": sum(m["otherwise_approved_book_stale"] for m in markets),
        "otherwise_approved_btc_stale": sum(m["otherwise_approved_btc_stale"] for m in markets),
        "otherwise_approved_balance": sum(m["otherwise_approved_balance"] for m in markets),
        "p_true_edge_or_price_false_rows": sum(m["p_true_edge_or_price_false_rows"] for m in markets),
        "edge_price_true_p_false_rows": sum(m["edge_price_true_p_false_rows"] for m in markets),
    }
    decision_counts = Counter(str(m["decision"]) for m in markets)
    markets_until_review = max(0, NO_ENTRY_REVIEW_MARKETS - int(totals["mature_markets"]))
    no_entry_review_due = (
        int(totals["approved"]) == 0
        and int(totals["order_like"]) == 0
        and int(totals["filled"]) == 0
        and int(totals["mature_markets"]) >= NO_ENTRY_REVIEW_MARKETS
    )
    if totals["filled"] or totals["order_like"] or totals["approved"]:
        decision = "entry_path_active_rescore_and_reconcile"
    elif totals["otherwise_approved_balance"]:
        decision = "account_state_blocker_investigate_before_continue"
    elif totals["otherwise_approved_book_stale"] or totals["otherwise_approved_btc_stale"]:
        decision = "source_freshness_blocker_continue_only_if_below_kill_threshold"
    elif no_entry_review_due:
        decision = "no_entry_runway_review_due"
    else:
        decision = "healthy_selective_wait_no_threshold_change"
    if no_entry_review_due:
        operator_next_action = (
            "Review the active candidate for low live opportunity density before another market. "
            "Do not widen p/edge/ask thresholds solely for coverage; either keep waiting with an explicit rationale, "
            "version an evidence-backed policy tweak, or stop the flat trial if a better existing candidate becomes launchable."
        )
    else:
        operator_next_action = (
            "Keep active trial running. Do not widen p/edge/ask thresholds; "
            "the zero-entry state is currently explained by the policy gates, not by failed order submission."
        )
    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "strategy_tag": STRATEGY_TAG,
        "log_source_tag": LOG_TAG,
        "events_path": str(EVENTS_PATH),
        "totals": totals,
        "no_entry_review_markets": NO_ENTRY_REVIEW_MARKETS,
        "mature_market_min_scored_rows": MATURE_MARKET_MIN_SCORED_ROWS,
        "markets_until_no_entry_review": markets_until_review,
        "no_entry_review_due": no_entry_review_due,
        "decision_counts": dict(decision_counts),
        "markets": markets,
        "decision": decision,
        "operator_next_action": operator_next_action,
    }


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Common-Clock Zero-Entry Blocker",
        "",
        "Operational classifier for the active sourcefix size-1 live trial. It does not place orders or change live logic.",
        "",
        f"- Generated UTC: `{report['generated_at_utc']}`",
        f"- Decision: `{report['decision']}`",
        f"- Strategy: `{report['strategy_tag']}`",
        f"- Log source: `{report['log_source_tag']}`",
        f"- Totals: `{report['totals']}`",
        f"- No-entry review due: `{report['no_entry_review_due']}`",
        f"- Markets until no-entry review: `{report['markets_until_no_entry_review']}`",
        f"- Mature-market rule: `{report['mature_market_min_scored_rows']}` scored rows, review at `{report['no_entry_review_markets']}` mature markets",
        f"- Decision counts: `{report['decision_counts']}`",
        "",
        "## Markets",
        "",
        "| market | events | scored | decision | max p | max edge c | p ok/price fail | edge ok/p fail | stale-only | orders/fills |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["markets"]:
        stale_only = int(row["otherwise_approved_book_stale"]) + int(row["otherwise_approved_btc_stale"])
        orders_fills = int(row["order_like"]) + int(row["filled"])
        lines.append(
            f"| `{row['market']}` | {row['events']} | {row['scored_rows']} | `{row['decision']}` | "
            f"{fmt(row['max_p_side'])} | {fmt(row['max_edge_cents'])} | "
            f"{row['p_true_edge_or_price_false_rows']} | {row['edge_price_true_p_false_rows']} | "
            f"{stale_only} | {orders_fills} |"
        )
    lines.extend(["", "## Operator Next Action", "", report["operator_next_action"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
