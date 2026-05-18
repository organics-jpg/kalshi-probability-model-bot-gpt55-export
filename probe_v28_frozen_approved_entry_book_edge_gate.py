"""Frozen forward validator for the approved-entry book-edge gate.

Research-only; no live bot changes or orders.

Frozen candidate:
    On actual v28-approved entries, skip an entry when raw v28 probability
    exceeds executable book probability by at least 15pp and the book-implied
    edge to the ask is below 5pp.

This turns the current actual-approved actionability discovery into a
future-only validation stream so it cannot quietly become a hindsight rule.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_approved_entry_book_edge_actionability import (
    future_rows,
    summarize,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_approved_entry_book_edge_gate_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_approved_entry_book_edge_gate_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_approved_entry_book_edge_gate_latest.md"

MIN_SETTLED = 30
MIN_COVERAGE = 75.0
MAX_COVERAGE = 100.0


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


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate": "skip_discount15_book_edge_lt_5pp",
        "entry_surface": "actual_v28_approved_entries_only",
        "rule": "Skip when raw_probability - book_probability >= 0.15 and book_probability - ask_probability < 0.05.",
        "physics": (
            "A large raw-minus-book gap with weak executable edge means the private FV is claiming conviction "
            "that the touch is not confirming; this is likely overconfidence rather than free edge."
        ),
        "min_settled": MIN_SETTLED,
        "coverage_floor": MIN_COVERAGE,
        "source_discovery": "v28_approved_entry_book_edge_actionability_latest",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def should_skip(row: dict[str, Any]) -> bool:
    discount = as_float(row.get("book_discount_prob"))
    book_edge = as_float(row.get("book_edge_prob"))
    return discount is not None and book_edge is not None and discount >= 0.15 and book_edge < 0.05


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "entry_ts": row.get("entry_ts"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "gross_cents": row.get("actual_gross_cents"),
        "ask_prob": row.get("ask_prob"),
        "raw_probability": row.get("raw_probability"),
        "book_probability": row.get("book_probability"),
        "book_discount_prob": row.get("book_discount_prob"),
        "book_edge_prob": row.get("book_edge_prob"),
        "seconds_to_close": row.get("seconds_to_close"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "abs_d_sigma": row.get("abs_d_sigma"),
    }


def full_loss_runway(candidate_net: float, settled: int) -> list[dict[str, Any]]:
    rows = []
    for losses in range(1, 6):
        stressed_net = candidate_net - 100.0 * losses
        rows.append({
            "added_full_losses": losses,
            "stressed_settled": settled + losses,
            "stressed_net_cents": stressed_net,
            "still_positive": stressed_net > 0.0,
            "sample_gate_met": settled + losses >= MIN_SETTLED,
        })
    return rows


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    rows = future_rows(str(state["freeze_ts_utc"]))
    denominator = len(rows)
    skipped = [row for row in rows if should_skip(row)]
    retained = [row for row in rows if not should_skip(row)]
    control_summary = summarize(rows, denominator)
    retained_summary = summarize(retained, denominator)
    skipped_summary = summarize(skipped, denominator)

    control_net = as_float(control_summary.get("net_cents")) or 0.0
    retained_net = as_float(retained_summary.get("net_cents")) or 0.0
    delta = retained_net - control_net
    coverage = as_float(retained_summary.get("coverage_pct"))
    settled = int(as_float(retained_summary.get("settled")) or 0)
    blockers = []
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or coverage < MIN_COVERAGE:
        blockers.append("coverage_lt_75")
    if coverage is not None and coverage > MAX_COVERAGE:
        blockers.append("coverage_gt_100")
    if delta <= 0.0:
        blockers.append("delta_not_positive")

    interpretation = [
        f"Frozen candidate has {denominator} future actual-approved entries and {settled} retained settled rows.",
        f"Control net {control_net}c; retained net {retained_net}c; delta {delta}c.",
        f"Retained coverage {coverage}; skipped rows {skipped_summary.get('wins')}/{skipped_summary.get('losses')} for {skipped_summary.get('net_cents')}c.",
        f"Promotion blockers: {', '.join(blockers) if blockers else 'none'}.",
        "This validator starts after its own freeze timestamp; earlier actionability results are discovery only.",
    ]
    return {
        "freeze": state,
        "future_entries": denominator,
        "control": control_summary,
        "candidate": retained_summary,
        "skipped": skipped_summary,
        "delta_net_vs_control_cents": delta,
        "candidate_live_ready": not blockers,
        "blockers": blockers,
        "full_loss_runway": full_loss_runway(retained_net, settled),
        "skipped_rows": [compact(row) for row in skipped],
        "interpretation": interpretation,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    freeze = report.get("freeze") or {}
    candidate = report.get("candidate") or {}
    control = report.get("control") or {}
    skipped = report.get("skipped") or {}
    lines = [
        "# v28 Frozen Approved-Entry Book-Edge Gate",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Future actual-approved entries: `{report.get('future_entries')}`",
        f"- Candidate live-ready: `{report.get('candidate_live_ready')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Scorecard",
        "",
        "| surface | entries | settled | W/L | coverage | net c | book brier d | book logloss d |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        (
            f"| keep_all_control | {control.get('entries')} | {control.get('settled')} | "
            f"{control.get('wins')}/{control.get('losses')} | {fmt(control.get('coverage_pct'))} | "
            f"{fmt(control.get('net_cents'))} | {fmt(control.get('book_brier_delta_vs_raw'))} | "
            f"{fmt(control.get('book_logloss_delta_vs_raw'))} |"
        ),
        (
            f"| retained_candidate | {candidate.get('entries')} | {candidate.get('settled')} | "
            f"{candidate.get('wins')}/{candidate.get('losses')} | {fmt(candidate.get('coverage_pct'))} | "
            f"{fmt(candidate.get('net_cents'))} | {fmt(candidate.get('book_brier_delta_vs_raw'))} | "
            f"{fmt(candidate.get('book_logloss_delta_vs_raw'))} |"
        ),
        (
            f"| skipped_rows | {skipped.get('entries')} | {skipped.get('settled')} | "
            f"{skipped.get('wins')}/{skipped.get('losses')} | {fmt(skipped.get('coverage_pct'))} | "
            f"{fmt(skipped.get('net_cents'))} | {fmt(skipped.get('book_brier_delta_vs_raw'))} | "
            f"{fmt(skipped.get('book_logloss_delta_vs_raw'))} |"
        ),
        "",
        "## Full-Loss Runway",
        "",
        "| added full losses | stressed settled | stressed net c | still positive | sample gate met |",
        "|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("full_loss_runway") or []:
        lines.append(
            f"| {row.get('added_full_losses')} | {row.get('stressed_settled')} | "
            f"{fmt(row.get('stressed_net_cents'))} | {row.get('still_positive')} | {row.get('sample_gate_met')} |"
        )
    lines.extend(["", "## Skipped Rows", "", "| market | side | won | gross c | raw | book | ask | discount | book edge |", "|---|---|---:|---:|---:|---:|---:|---:|---:|"])
    for row in report.get("skipped_rows") or []:
        lines.append(
            f"| `{row.get('market')}` | {row.get('side')} | {row.get('side_won')} | {fmt(row.get('gross_cents'))} | "
            f"{fmt(row.get('raw_probability'))} | {fmt(row.get('book_probability'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('book_discount_prob'))} | {fmt(row.get('book_edge_prob'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
