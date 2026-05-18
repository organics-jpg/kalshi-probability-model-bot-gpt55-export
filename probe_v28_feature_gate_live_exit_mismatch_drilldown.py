"""Drill down feature-gate theory-win/live-loss exit mismatches.

Research-only; no live bot changes or orders.

This starts from the live-outcome alignment report and inspects the markets
where the feature-gate selected side settled correctly but live selected-side
trading still lost money. It joins trade rows and execution events to classify
whether the failure is exit-policy clipping, side/state churn, or execution
friction.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
ALIGNMENT_JSON = OUT_DIR / "v28_feature_gate_live_outcome_alignment_latest.json"
TRADES_CSV = ROOT / "stats" / "live_mushroom_v28_size2" / "trades.csv"
EXECUTION_EVENTS = ROOT / "logs" / "live_mushroom_v28_size2" / "execution_events.ndjson"
OUT_JSON = OUT_DIR / "v28_feature_gate_live_exit_mismatch_drilldown_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_live_exit_mismatch_drilldown_latest.md"

TARGET_CANDIDATE = "post_feature_freeze_entry_raw03_recross70_abs075"
TARGET_TAG = "theory_win_selected_side_live_loss"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def load_trades(path: Path, markets: set[str]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    if not path.exists():
        return grouped
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            market = str(row.get("market") or "")
            if market in markets:
                grouped[market].append(row)
    return grouped


def load_events(path: Path, markets: set[str]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    if not path.exists():
        return grouped
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            market = str(row.get("market") or "")
            if market in markets:
                grouped[market].append(row)
    for market in grouped:
        grouped[market].sort(key=lambda row: str(row.get("ts_wall") or ""))
    return grouped


def selected_alignment_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for variant in payload.get("variants") or []:
        if variant.get("candidate") == TARGET_CANDIDATE:
            return [
                row for row in variant.get("rows") or []
                if TARGET_TAG in set(row.get("alignment_tags") or [])
            ]
    return []


def net_cents(rows: list[dict[str, Any]]) -> float:
    return sum(100.0 * fnum(row.get("net_pnl_dollars")) for row in rows)


def qty(rows: list[dict[str, Any]]) -> float:
    return sum(fnum(row.get("qty")) for row in rows)


def per_contract_net(rows: list[dict[str, Any]]) -> float | None:
    total_qty = qty(rows)
    return net_cents(rows) / total_qty if total_qty else None


def selected_side_trades(trades: list[dict[str, Any]], side: str) -> list[dict[str, Any]]:
    return [row for row in trades if str(row.get("side") or "") == side]


def opposite_side_trades(trades: list[dict[str, Any]], side: str) -> list[dict[str, Any]]:
    return [row for row in trades if str(row.get("side") or "") and str(row.get("side") or "") != side]


def event_exit_reason(row: dict[str, Any]) -> str:
    return str(
        row.get("mushroom_v28_exit_reason")
        or row.get("decision_reason")
        or row.get("stop_tier")
        or ""
    )


def exit_events(events: list[dict[str, Any]], side: str) -> list[dict[str, Any]]:
    out = []
    for row in events:
        event_type = str(row.get("event_type") or "")
        if "exit" not in event_type and not str(row.get("client_order_id") or "").startswith("btc15m-exit"):
            continue
        if str(row.get("side") or "") != side:
            continue
        out.append(row)
    return out


def compact_exit_event(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "ts_wall": row.get("ts_wall"),
        "event_type": row.get("event_type"),
        "reason": event_exit_reason(row),
        "result": row.get("result"),
        "exchange_status": row.get("exchange_status"),
        "position_size": row.get("position_size"),
        "trigger_price_cents": row.get("trigger_price_cents"),
        "top_of_book_limit_cents": row.get("top_of_book_limit_cents"),
        "mushroom_v28_entry_basis_cents": row.get("mushroom_v28_entry_basis_cents"),
        "mushroom_v28_exit_bid_cents": row.get("mushroom_v28_exit_bid_cents"),
        "mushroom_v28_p_hold": row.get("mushroom_v28_p_hold"),
        "mushroom_v28_fair_drawdown_cents": row.get("mushroom_v28_fair_drawdown_cents"),
        "mushroom_v28_hold_net_cents": row.get("mushroom_v28_hold_net_cents"),
        "eligible_depth": row.get("eligible_depth"),
        "book_age_ms": row.get("book_age_ms"),
        "feed_age_ms": row.get("feed_age_ms"),
        "submit_latency_ms": row.get("submit_latency_ms"),
    }


def entry_fill_avg(trades: list[dict[str, Any]]) -> float | None:
    total_qty = qty(trades)
    if not total_qty:
        return None
    return sum(fnum(row.get("entry_fill_cents_used")) * fnum(row.get("qty")) for row in trades) / total_qty


def exit_fill_avg(trades: list[dict[str, Any]]) -> float | None:
    exited = [row for row in trades if row.get("exit_fill_cents_used") not in (None, "")]
    total_qty = qty(exited)
    if not total_qty:
        return None
    return sum(fnum(row.get("exit_fill_cents_used")) * fnum(row.get("qty")) for row in exited) / total_qty


def hold_win_net_from_entry(entry_cents: float | None) -> float | None:
    if entry_cents is None:
        return None
    return 100.0 - entry_cents


def classifications(
    align: dict[str, Any],
    selected_trades: list[dict[str, Any]],
    opposite_trades: list[dict[str, Any]],
    selected_events: list[dict[str, Any]],
) -> list[str]:
    tags = ["exit_policy_error"]
    reasons = Counter(event_exit_reason(row) for row in selected_events if event_exit_reason(row))
    if any("probability_reduce" in reason for reason in reasons):
        tags.append("probability_reduce_clipped_winner")
    if any("value_over_hold" in reason for reason in reasons):
        tags.append("value_over_hold_clipped_winner")
    if len(selected_trades) > 1:
        tags.append("same_side_state_churn")
    if opposite_trades:
        tags.append("opposite_side_state_churn")
    if any(str(row.get("outcome") or "") == "exited_before_settlement" for row in selected_trades):
        tags.append("exited_before_settlement")
    if fnum(align.get("theory_net_cents")) > 0 and per_contract_net(selected_trades) is not None:
        tags.append("theory_win_selected_live_loss")
    return tags


def build_market_row(
    align: dict[str, Any],
    trades: list[dict[str, Any]],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    side = str(align.get("side") or "")
    selected = selected_side_trades(trades, side)
    opposite = opposite_side_trades(trades, side)
    selected_exit_events = exit_events(events, side)
    selected_entry = entry_fill_avg(selected)
    selected_exit = exit_fill_avg(selected)
    hold_win_net = hold_win_net_from_entry(selected_entry)
    selected_pc = per_contract_net(selected)
    return {
        "market": align.get("market"),
        "source": align.get("source"),
        "side": side,
        "theory_net_cents": align.get("theory_net_cents"),
        "live_selected_side_net_cents": net_cents(selected),
        "live_selected_side_per_contract_cents": selected_pc,
        "selected_side_qty": qty(selected),
        "selected_side_trade_count": len(selected),
        "opposite_side_trade_count": len(opposite),
        "opposite_side_net_cents": net_cents(opposite),
        "selected_entry_fill_avg_cents": selected_entry,
        "selected_exit_fill_avg_cents": selected_exit,
        "hold_win_net_from_entry_cents": hold_win_net,
        "estimated_clip_vs_hold_per_contract_cents": (
            None if hold_win_net is None or selected_pc is None else hold_win_net - selected_pc
        ),
        "trade_outcomes": dict(Counter(str(row.get("outcome") or "unknown") for row in selected)),
        "trade_resolution_sources": dict(Counter(str(row.get("resolution_source") or "unknown") for row in selected)),
        "exit_reason_counts": dict(Counter(event_exit_reason(row) for row in selected_exit_events if event_exit_reason(row))),
        "exit_event_count": len(selected_exit_events),
        "classifications": classifications(align, selected, opposite, selected_exit_events),
        "exit_events": [compact_exit_event(row) for row in selected_exit_events[-12:]],
        "trades": selected,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "markets": len(rows),
        "theory_net_cents": sum(fnum(row.get("theory_net_cents")) for row in rows),
        "live_selected_side_net_cents": sum(fnum(row.get("live_selected_side_net_cents")) for row in rows),
        "estimated_clip_vs_hold_per_contract_cents": sum(
            fnum(row.get("estimated_clip_vs_hold_per_contract_cents"))
            for row in rows
            if row.get("estimated_clip_vs_hold_per_contract_cents") is not None
        ),
        "classification_counts": dict(Counter(tag for row in rows for tag in row.get("classifications") or [])),
        "exit_reason_counts": dict(Counter(
            reason for row in rows for reason, count in (row.get("exit_reason_counts") or {}).items() for _ in range(count)
        )),
    }


def build_report() -> dict[str, Any]:
    alignment = load_json(ALIGNMENT_JSON)
    rows = selected_alignment_rows(alignment)
    markets = {str(row.get("market") or "") for row in rows if row.get("market")}
    trades = load_trades(TRADES_CSV, markets)
    events = load_events(EXECUTION_EVENTS, markets)
    market_rows = [build_market_row(row, trades.get(str(row.get("market")) or "", []), events.get(str(row.get("market")) or "", [])) for row in rows]
    market_rows.sort(key=lambda row: fnum(row.get("live_selected_side_net_cents")))
    report = {
        "generated_at_utc": utc_now_iso(),
        "alignment_source": str(ALIGNMENT_JSON),
        "trades_source": str(TRADES_CSV),
        "execution_events_source": str(EXECUTION_EVENTS),
        "target_candidate": TARGET_CANDIDATE,
        "target_tag": TARGET_TAG,
        "summary": summarize(market_rows),
        "markets": market_rows,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    summary = report.get("summary") or {}
    return [
        "This is an attribution drilldown only; it does not change live exits or entries.",
        (
            f"{summary.get('markets')} theory-win/live-selected-loss markets total "
            f"{summary.get('theory_net_cents')}c theoretical settlement PnL but "
            f"{summary.get('live_selected_side_net_cents')}c live selected-side PnL."
        ),
        f"Classifications: {summary.get('classification_counts')}.",
        f"Exit reasons: {summary.get('exit_reason_counts')}.",
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Live Exit Mismatch Drilldown",
        "",
        "Research-only attribution drilldown. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Candidate: `{report.get('target_candidate')}`",
        f"- Target tag: `{report.get('target_tag')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Markets",
            "",
            "| market | source | side | theory c | live selected c | per contract c | entry | exit | clip vs hold/ct | exits | reasons | classes |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in report.get("markets") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | "
            f"{fmt(row.get('theory_net_cents'))} | {fmt(row.get('live_selected_side_net_cents'))} | "
            f"{fmt(row.get('live_selected_side_per_contract_cents'))} | "
            f"{fmt(row.get('selected_entry_fill_avg_cents'))} | {fmt(row.get('selected_exit_fill_avg_cents'))} | "
            f"{fmt(row.get('estimated_clip_vs_hold_per_contract_cents'))} | {row.get('exit_event_count')} | "
            f"{row.get('exit_reason_counts')} | {', '.join(row.get('classifications') or [])} |"
        )
    lines.extend(
        [
            "",
            "## Exit Event Tails",
            "",
        ]
    )
    for row in report.get("markets") or []:
        lines.extend(
            [
                f"### {row.get('market')}",
                "",
                "| ts | event | reason | result | trigger | bid | p_hold | drawdown | hold net | depth | book age |",
                "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for event in row.get("exit_events") or []:
            lines.append(
                f"| {event.get('ts_wall')} | {event.get('event_type')} | {event.get('reason')} | "
                f"{event.get('result')} | {fmt(event.get('trigger_price_cents'))} | "
                f"{fmt(event.get('mushroom_v28_exit_bid_cents'))} | {fmt(event.get('mushroom_v28_p_hold'))} | "
                f"{fmt(event.get('mushroom_v28_fair_drawdown_cents'))} | "
                f"{fmt(event.get('mushroom_v28_hold_net_cents'))} | {fmt(event.get('eligible_depth'))} | "
                f"{fmt(event.get('book_age_ms'))} |"
            )
        lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
