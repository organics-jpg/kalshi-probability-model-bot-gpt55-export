"""Pending-row resolution audit for the v28 feature-gate near-promotion lane.

Research-only; no live bot changes or orders.

This joins the latest denominator-gap pending selected rows against refreshed
live scorer result artifacts. It does not alter candidate scoring; it shows
whether pending rows are genuinely unresolved or only missing outcome linkage
inside the research surface.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_danger_tag_replacement_diagnostic import row_net_after_fee


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
DENOM_JSON = OUT_DIR / "v28_feature_gate_near_promotion_denominator_gap_latest.json"
MARKET_RESULTS_CSV = ROOT / "stats" / "live_mushroom_v28_size2" / "market_results.csv"
TRADES_CSV = ROOT / "stats" / "live_mushroom_v28_size2" / "trades.csv"
RECENT_OUTCOMES_JSON = ROOT / "state" / "live_mushroom_v28_size2" / "recent_market_outcomes.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_pending_resolution_audit_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_pending_resolution_audit_latest.md"

MIN_CUSHION_CENTS = 300.0
MAX_RECONSTRUCTED_SHARE = 0.35


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


def load_csv_by_market(path: Path) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = {}
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            market = str(row.get("market") or "")
            if market:
                out.setdefault(market, []).append(row)
    return out


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def recent_outcomes_by_market() -> dict[str, dict[str, Any]]:
    payload = load_json(RECENT_OUTCOMES_JSON)
    records = payload.get("records") if isinstance(payload.get("records"), list) else []
    out: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        market = str(record.get("market") or "")
        if market:
            out[market] = record
    return out


def side_won(side: str, result: str) -> bool | None:
    if side not in {"yes", "no"} or result not in {"yes", "no"}:
        return None
    return side == result


def resolved_net_cents(row: dict[str, Any], won: bool | None) -> float | None:
    if won is None:
        return None
    enriched = dict(row)
    enriched["side_won"] = won
    return row_net_after_fee(enriched)


def trade_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    if not rows:
        return {"rows": 0, "net_pnl_dollars": 0.0, "outcomes": {}}
    return {
        "rows": len(rows),
        "net_pnl_dollars": sum(as_float(row.get("net_pnl_dollars")) or 0.0 for row in rows),
        "outcomes": dict(Counter(str(row.get("outcome") or "") for row in rows)),
    }


def build_report() -> dict[str, Any]:
    denom = load_json(DENOM_JSON)
    selected = denom.get("selected_summary") or {}
    pending = [row for row in denom.get("pending_selected_rows") or [] if isinstance(row, dict)]
    market_results = load_csv_by_market(MARKET_RESULTS_CSV)
    trades = load_csv_by_market(TRADES_CSV)
    recent = recent_outcomes_by_market()

    rows = []
    resolved_count = 0
    resolved_net = 0.0
    live_recent_pnl = 0.0
    for row in pending:
        market = str(row.get("market") or "")
        side = str(row.get("side") or "")
        result_rows = market_results.get(market) or []
        result_row = result_rows[-1] if result_rows else {}
        result = str(result_row.get("result") or "")
        won = side_won(side, result)
        net_cents = resolved_net_cents(row, won)
        if net_cents is not None:
            resolved_count += 1
            resolved_net += net_cents
        recent_row = recent.get(market) or {}
        recent_pnl = as_float(recent_row.get("pnl_dollars"))
        if recent_pnl is not None:
            live_recent_pnl += recent_pnl
        rows.append(
            {
                "market": market,
                "side": side,
                "source": row.get("source"),
                "research_pending": row.get("settled") is False,
                "market_result": result,
                "market_status": result_row.get("status"),
                "settlement_ts": result_row.get("settlement_ts"),
                "side_won_from_market_result": won,
                "resolved_entry_net_cents_estimate": net_cents,
                "ask_prob": row.get("ask_prob"),
                "raw_edge": row.get("raw_edge"),
                "recross_hazard_score": row.get("recross_hazard_score"),
                "abs_d_sigma": row.get("abs_d_sigma"),
                "recent_outcome_type": recent_row.get("outcome_type"),
                "recent_pnl_dollars": recent_pnl,
                "recent_resolved_at": recent_row.get("resolved_at"),
                "trade_summary": trade_summary(trades.get(market) or []),
            }
        )

    current_net = as_float(selected.get("net_cents")) or 0.0
    current_settled = int(as_float(selected.get("settled")) or 0)
    projected_settled = current_settled + resolved_count
    projected_net = current_net + resolved_net
    projected_cushion_needed = max(0.0, MIN_CUSHION_CENTS - projected_net)
    reconstructed_share = selected.get("reconstructed_share")
    source_gate = reconstructed_share is not None and float(reconstructed_share) <= MAX_RECONSTRUCTED_SHARE
    return {
        "generated_at_utc": utc_now_iso(),
        "source_denominator_gap": str(DENOM_JSON),
        "candidate": denom.get("candidate"),
        "freeze_ts_utc": denom.get("freeze_ts_utc"),
        "selected_entries": denom.get("selected_entries"),
        "future_denominator": denom.get("future_denominator"),
        "current_selected_net_cents": current_net,
        "current_settled_selected": current_settled,
        "pending_rows": len(pending),
        "pending_resolved_in_market_results": resolved_count,
        "pending_resolved_entry_net_cents_estimate": resolved_net,
        "pending_recent_live_pnl_dollars": live_recent_pnl,
        "projected_settled_if_market_results_linked": projected_settled,
        "projected_net_cents_if_market_results_linked": projected_net,
        "projected_cushion_cents_needed": projected_cushion_needed,
        "reconstructed_share_unchanged": reconstructed_share,
        "source_gate_unchanged": source_gate,
        "coverage_entries_needed_unchanged": denom.get("coverage_entries_needed"),
        "interpretation": interpretation(resolved_count, pending, projected_net, source_gate, denom),
        "rows": rows,
    }


def interpretation(
    resolved_count: int,
    pending: list[dict[str, Any]],
    projected_net: float,
    source_gate: bool,
    denom: dict[str, Any],
) -> list[str]:
    notes = [
        "This audit is linkage-only: it does not change the official frozen candidate score.",
        f"{resolved_count}/{len(pending)} pending selected rows have finalized market results in the refreshed live scorer artifacts.",
        (
            f"If those results are linked back into the research surface, selected net would be about "
            f"{projected_net:.1f}c before any new coverage rows."
        ),
        (
            f"Coverage still needs {denom.get('coverage_entries_needed')} additional selected denominator rows because "
            "the pending rows were already counted as entries."
        ),
    ]
    if not source_gate:
        notes.append("Source share is unchanged by resolving pending rows, so the source-quality gate still fails.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Pending Resolution Audit",
        "",
        "Research-only linkage audit. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Candidate: `{report.get('candidate')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Pending rows: `{report.get('pending_rows')}`",
            f"- Pending resolved in market-results artifact: `{report.get('pending_resolved_in_market_results')}`",
            f"- Current selected settled/net: `{report.get('current_settled_selected')}` / `{fmt(report.get('current_selected_net_cents'))}c`",
            f"- Projected selected settled/net if linked: `{report.get('projected_settled_if_market_results_linked')}` / `{fmt(report.get('projected_net_cents_if_market_results_linked'))}c`",
            f"- Projected cushion cents still needed: `{fmt(report.get('projected_cushion_cents_needed'))}`",
            f"- Reconstructed share unchanged: `{fmt(report.get('reconstructed_share_unchanged'))}`",
            f"- Source gate unchanged: `{report.get('source_gate_unchanged')}`",
            f"- Coverage entries needed unchanged: `{report.get('coverage_entries_needed_unchanged')}`",
            f"- Recent-outcome live PnL across pending markets: `${fmt(report.get('pending_recent_live_pnl_dollars'))}`",
            "",
            "## Rows",
            "",
            "| market | side | result | won | est entry net c | live outcome | live pnl $ | trades | ask | edge | recross | abs d |",
            "|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("rows") or []:
        trades = row.get("trade_summary") or {}
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('market_result')} | "
            f"{row.get('side_won_from_market_result')} | {fmt(row.get('resolved_entry_net_cents_estimate'))} | "
            f"{row.get('recent_outcome_type')} | {fmt(row.get('recent_pnl_dollars'))} | {trades.get('rows')} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
