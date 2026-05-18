"""Feature-gate live selected-side exit hold counterfactual.

Research-only; no live bot changes or orders.

This probe measures whether live exits helped or hurt on markets selected by
the frozen feature-gate row. It uses actual live selected-side entries, then
compares realized live PnL to a counterfactual where those same contracts were
held to settlement. This separates winner clipping from loss control.
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
OUT_JSON = OUT_DIR / "v28_feature_gate_live_exit_hold_counterfactual_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_live_exit_hold_counterfactual_latest.md"

TARGET_CANDIDATE = "post_feature_freeze_entry_raw03_recross70_abs075"


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
    return grouped


def target_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for variant in payload.get("variants") or []:
        if variant.get("candidate") == TARGET_CANDIDATE:
            return [row for row in variant.get("rows") or [] if isinstance(row, dict)]
    return []


def selected_side_trades(trades: list[dict[str, Any]], side: str) -> list[dict[str, Any]]:
    return [row for row in trades if str(row.get("side") or "") == side]


def live_net_cents(trades: list[dict[str, Any]]) -> float:
    return sum(100.0 * fnum(row.get("net_pnl_dollars")) for row in trades)


def qty(trades: list[dict[str, Any]]) -> float:
    return sum(fnum(row.get("qty")) for row in trades)


def hold_net_for_trade(row: dict[str, Any], side_won: bool) -> float:
    quantity = fnum(row.get("qty"))
    entry = fnum(row.get("entry_fill_cents_used"))
    entry_fee = fnum(row.get("entry_fee_cents"))
    exit_fee = fnum(row.get("exit_fee_cents"))
    settlement_value = 100.0 if side_won else 0.0
    return quantity * (settlement_value - entry) - entry_fee - exit_fee


def hold_net_cents(trades: list[dict[str, Any]], side_won: bool) -> float:
    return sum(hold_net_for_trade(row, side_won) for row in trades)


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


def avg_fill(trades: list[dict[str, Any]], field: str) -> float | None:
    usable = [row for row in trades if row.get(field) not in (None, "")]
    total_qty = qty(usable)
    if not total_qty:
        return None
    return sum(fnum(row.get(field)) * fnum(row.get("qty")) for row in usable) / total_qty


def market_row(align: dict[str, Any], trades: list[dict[str, Any]], events: list[dict[str, Any]]) -> dict[str, Any]:
    side = str(align.get("side") or "")
    selected = selected_side_trades(trades, side)
    side_won = bool(align.get("side_won"))
    selected_live = live_net_cents(selected)
    selected_hold = hold_net_cents(selected, side_won)
    delta = selected_live - selected_hold
    selected_exits = exit_events(events, side)
    reasons = Counter(event_exit_reason(row) for row in selected_exits if event_exit_reason(row))
    outcomes = Counter(str(row.get("outcome") or "unknown") for row in selected)
    tags = []
    if not selected:
        tags.append("no_selected_side_live_trade")
    elif delta < 0:
        tags.append("exit_hurt_vs_settlement_hold")
    elif delta > 0:
        tags.append("exit_helped_vs_settlement_hold")
    else:
        tags.append("exit_neutral_vs_settlement_hold")
    tags.append("settlement_winner" if side_won else "settlement_loser")
    if selected and any(str(row.get("outcome") or "") == "exited_before_settlement" for row in selected):
        tags.append("exited_before_settlement")
    if any("probability_reduce" in reason for reason in reasons):
        tags.append("probability_reduce")
    if any("value_over_hold" in reason for reason in reasons):
        tags.append("value_over_hold")
    if any("probability_collapse" in reason for reason in reasons):
        tags.append("probability_collapse")
    return {
        "market": align.get("market"),
        "source": align.get("source"),
        "side": side,
        "side_won": side_won,
        "theory_net_cents": align.get("theory_net_cents"),
        "selected_side_trade_count": len(selected),
        "selected_side_qty": qty(selected),
        "selected_live_net_cents": selected_live,
        "selected_hold_to_settlement_net_cents": selected_hold,
        "exit_delta_vs_hold_cents": delta,
        "entry_fill_avg_cents": avg_fill(selected, "entry_fill_cents_used"),
        "exit_fill_avg_cents": avg_fill(selected, "exit_fill_cents_used"),
        "trade_outcomes": dict(outcomes),
        "exit_reason_counts": dict(reasons),
        "exit_event_count": len(selected_exits),
        "tags": tags,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    traded = [row for row in rows if fnum(row.get("selected_side_qty")) > 0]
    winners = [row for row in traded if row.get("side_won")]
    losers = [row for row in traded if not row.get("side_won")]
    hurt = [row for row in traded if fnum(row.get("exit_delta_vs_hold_cents")) < 0]
    helped = [row for row in traded if fnum(row.get("exit_delta_vs_hold_cents")) > 0]
    return {
        "rows": len(rows),
        "selected_side_live_traded_markets": len(traded),
        "selected_side_no_live_trade_markets": len(rows) - len(traded),
        "selected_side_qty": sum(fnum(row.get("selected_side_qty")) for row in traded),
        "theory_net_cents": sum(fnum(row.get("theory_net_cents")) for row in rows),
        "live_selected_net_cents": sum(fnum(row.get("selected_live_net_cents")) for row in traded),
        "hold_to_settlement_net_cents": sum(fnum(row.get("selected_hold_to_settlement_net_cents")) for row in traded),
        "exit_delta_vs_hold_cents": sum(fnum(row.get("exit_delta_vs_hold_cents")) for row in traded),
        "winner_markets": len(winners),
        "winner_live_net_cents": sum(fnum(row.get("selected_live_net_cents")) for row in winners),
        "winner_hold_net_cents": sum(fnum(row.get("selected_hold_to_settlement_net_cents")) for row in winners),
        "winner_exit_delta_vs_hold_cents": sum(fnum(row.get("exit_delta_vs_hold_cents")) for row in winners),
        "loser_markets": len(losers),
        "loser_live_net_cents": sum(fnum(row.get("selected_live_net_cents")) for row in losers),
        "loser_hold_net_cents": sum(fnum(row.get("selected_hold_to_settlement_net_cents")) for row in losers),
        "loser_exit_delta_vs_hold_cents": sum(fnum(row.get("exit_delta_vs_hold_cents")) for row in losers),
        "exit_hurt_markets": len(hurt),
        "exit_hurt_cents": sum(fnum(row.get("exit_delta_vs_hold_cents")) for row in hurt),
        "exit_helped_markets": len(helped),
        "exit_helped_cents": sum(fnum(row.get("exit_delta_vs_hold_cents")) for row in helped),
        "tag_counts": dict(Counter(tag for row in rows for tag in row.get("tags") or [])),
        "source_delta_vs_hold_cents": {
            source: sum(fnum(row.get("exit_delta_vs_hold_cents")) for row in traded if row.get("source") == source)
            for source in sorted({str(row.get("source") or "unknown") for row in traded})
        },
        "exit_reason_counts": dict(Counter(
            reason for row in rows for reason, count in (row.get("exit_reason_counts") or {}).items() for _ in range(int(count or 0))
        )),
    }


def interpretation(summary: dict[str, Any]) -> list[str]:
    return [
        "Research-only hold counterfactual; it does not change live exits or entries.",
        (
            f"Selected-side live traded {summary.get('selected_side_live_traded_markets')}/"
            f"{summary.get('rows')} feature-gate markets with live selected-side PnL "
            f"{summary.get('live_selected_net_cents')}c."
        ),
        (
            f"Holding those same selected-side live entries to settlement would have been "
            f"{summary.get('hold_to_settlement_net_cents')}c, so realized exits/state changed PnL by "
            f"{summary.get('exit_delta_vs_hold_cents')}c versus settlement hold."
        ),
        (
            f"Winner rows: live {summary.get('winner_live_net_cents')}c vs hold "
            f"{summary.get('winner_hold_net_cents')}c; loser rows: live {summary.get('loser_live_net_cents')}c vs hold "
            f"{summary.get('loser_hold_net_cents')}c."
        ),
        f"Exit hurt/help counts: {summary.get('exit_hurt_markets')}/{summary.get('exit_helped_markets')}.",
        f"Exit reasons: {summary.get('exit_reason_counts')}.",
    ]


def build_report() -> dict[str, Any]:
    alignment = load_json(ALIGNMENT_JSON)
    rows = target_rows(alignment)
    markets = {str(row.get("market") or "") for row in rows if row.get("market")}
    trades = load_trades(TRADES_CSV, markets)
    events = load_events(EXECUTION_EVENTS, markets)
    market_rows = [
        market_row(row, trades.get(str(row.get("market") or ""), []), events.get(str(row.get("market") or ""), []))
        for row in rows
    ]
    market_rows.sort(key=lambda row: fnum(row.get("exit_delta_vs_hold_cents")))
    summary = summarize(market_rows)
    return {
        "generated_at_utc": utc_now_iso(),
        "alignment_source": str(ALIGNMENT_JSON),
        "trades_source": str(TRADES_CSV),
        "execution_events_source": str(EXECUTION_EVENTS),
        "target_candidate": TARGET_CANDIDATE,
        "summary": summary,
        "interpretation": interpretation(summary),
        "markets": market_rows,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Live Exit Hold Counterfactual",
        "",
        "Research-only counterfactual. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Candidate: `{report.get('target_candidate')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    summary = report.get("summary") or {}
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Selected-side live traded markets: `{summary.get('selected_side_live_traded_markets')} / {summary.get('rows')}`",
            f"- Live selected-side PnL: `{fmt(summary.get('live_selected_net_cents'))}c`",
            f"- Hold-to-settlement counterfactual PnL on same live selected-side entries: `{fmt(summary.get('hold_to_settlement_net_cents'))}c`",
            f"- Exit/state delta versus settlement hold: `{fmt(summary.get('exit_delta_vs_hold_cents'))}c`",
            f"- Winner-row exit delta: `{fmt(summary.get('winner_exit_delta_vs_hold_cents'))}c`",
            f"- Loser-row exit delta: `{fmt(summary.get('loser_exit_delta_vs_hold_cents'))}c`",
            f"- Exit hurt/help markets: `{summary.get('exit_hurt_markets')} / {summary.get('exit_helped_markets')}`",
            f"- Source delta versus hold: `{summary.get('source_delta_vs_hold_cents')}`",
            f"- Tag counts: `{summary.get('tag_counts')}`",
            "",
            "## Markets",
            "",
            "| market | source | side | won | qty | theory c | live c | hold c | exit delta c | entry | exit | reasons | tags |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in report.get("markets") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('selected_side_qty'))} | {fmt(row.get('theory_net_cents'))} | "
            f"{fmt(row.get('selected_live_net_cents'))} | {fmt(row.get('selected_hold_to_settlement_net_cents'))} | "
            f"{fmt(row.get('exit_delta_vs_hold_cents'))} | {fmt(row.get('entry_fill_avg_cents'))} | "
            f"{fmt(row.get('exit_fill_avg_cents'))} | {row.get('exit_reason_counts')} | "
            f"{', '.join(row.get('tags') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
