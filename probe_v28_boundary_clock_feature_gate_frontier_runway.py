"""Runway audit for the boundary-clock feature-gate frontier.

Research-only; no live bot changes or orders.

This reads the observable coverage/source frontier and estimates how much
future clean evidence the current best Pareto row needs before it could satisfy
sample, coverage, source-quality, and full-loss-cushion gates. It does not
create a new candidate or use source labels for selection.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FRONTIER_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_coverage_source_frontier_latest.json"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_frontier_runway_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_frontier_runway_latest.md"

MIN_SETTLED = 30
MIN_COVERAGE = 75.0
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3
FULL_LOSS_CENTS = 100.0


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


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clean_rows_needed_for_source(rejected: int, selected: int) -> int:
    for rows in range(0, 500):
        total = selected + rows
        if total > 0 and rejected / total <= MAX_RECONSTRUCTED_SHARE:
            return rows
    return 500


def clean_rows_needed_for_coverage(selected: int, denominator: int) -> int:
    target = MIN_COVERAGE / 100.0
    for rows in range(0, 500):
        total_den = denominator + rows
        if total_den > 0 and (selected + rows) / total_den >= target:
            return rows
    return 500


def rows_needed_for_cushion(net_cents: float, avg_net_cents: float | None) -> dict[str, Any]:
    target_net = MIN_FULL_LOSS_CUSHION * FULL_LOSS_CENTS
    needed_cents = max(0.0, target_net - net_cents)
    if needed_cents <= 0:
        return {"net_cents_needed": 0.0, "rows_at_current_avg": 0}
    if avg_net_cents is None or avg_net_cents <= 0:
        return {"net_cents_needed": needed_cents, "rows_at_current_avg": None}
    return {
        "net_cents_needed": needed_cents,
        "rows_at_current_avg": int(math.ceil(needed_cents / avg_net_cents)),
    }


def best_frontier_row(lane: dict[str, Any]) -> dict[str, Any]:
    rows = lane.get("pareto_frontier")
    if not isinstance(rows, list) or not rows:
        return {}
    return rows[0] if isinstance(rows[0], dict) else {}


def summarize_lane(lane: dict[str, Any]) -> dict[str, Any]:
    row = best_frontier_row(lane)
    summary = row.get("summary") if isinstance(row.get("summary"), dict) else {}
    source_counts = row.get("source_counts") if isinstance(row.get("source_counts"), dict) else {}
    entries = int(as_float(summary.get("entries")) or 0)
    settled = int(as_float(summary.get("settled")) or 0)
    denominator = int(as_float(row.get("future_denominator")) or as_float(lane.get("future_denominator")) or 0)
    approved = int(as_float(source_counts.get("approved_entry")) or 0)
    rejected = int(as_float(source_counts.get("rejected_actionable")) or 0)
    net_cents = as_float(summary.get("net_cents")) or 0.0
    avg_net_cents = as_float(summary.get("avg_net_cents"))
    source_rows = clean_rows_needed_for_source(rejected, entries)
    coverage_rows = clean_rows_needed_for_coverage(entries, denominator)
    sample_rows = max(0, MIN_SETTLED - settled)
    cushion = rows_needed_for_cushion(net_cents, avg_net_cents)
    simultaneous_clean_rows = max(
        source_rows,
        coverage_rows,
        sample_rows,
        int(cushion["rows_at_current_avg"] or 0),
    )
    projected_den = denominator + simultaneous_clean_rows
    projected_entries = entries + simultaneous_clean_rows
    projected_settled = settled + simultaneous_clean_rows
    projected_net = net_cents + simultaneous_clean_rows * (avg_net_cents or 0.0)
    return {
        "lane": lane.get("lane"),
        "rule": row.get("rule"),
        "current": {
            "entries": entries,
            "settled": settled,
            "denominator": denominator,
            "coverage_pct": summary.get("coverage_pct"),
            "net_cents": net_cents,
            "avg_net_cents": avg_net_cents,
            "wins": summary.get("wins"),
            "losses": summary.get("losses"),
            "approved_entry": approved,
            "rejected_actionable": rejected,
            "reconstructed_share": row.get("reconstructed_share"),
            "full_loss_cushion_estimate": row.get("full_loss_cushion_estimate"),
            "blockers": row.get("blockers") or [],
        },
        "runway": {
            "clean_rows_needed_for_source_gate": source_rows,
            "clean_rows_needed_for_coverage_gate": coverage_rows,
            "settled_rows_needed_for_sample_gate": sample_rows,
            **cushion,
            "clean_rows_needed_for_all_gates_at_current_avg": simultaneous_clean_rows,
            "projected_entries": projected_entries,
            "projected_settled": projected_settled,
            "projected_denominator": projected_den,
            "projected_coverage_pct": None if projected_den <= 0 else 100.0 * projected_entries / projected_den,
            "projected_reconstructed_share": None if projected_entries <= 0 else rejected / projected_entries,
            "projected_net_cents_at_current_avg": projected_net,
            "projected_full_loss_cushion": int(max(0.0, projected_net) // FULL_LOSS_CENTS),
        },
    }


def build_report() -> dict[str, Any]:
    frontier = load_json(FRONTIER_JSON)
    lanes = [
        summarize_lane(lane)
        for lane in frontier.get("lanes") or []
        if isinstance(lane, dict) and str(lane.get("lane") or "").startswith("post_feature_freeze")
    ]
    report = {
        "generated_at_utc": utc_now_iso(),
        "frontier_generated_at_utc": frontier.get("generated_at_utc"),
        "freeze_ts_utc": frontier.get("freeze_ts_utc"),
        "lanes": lanes,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This is a runway audit of the current frontier row, not a promotion candidate or threshold search.",
    ]
    for lane in report.get("lanes") or []:
        current = lane.get("current") or {}
        runway = lane.get("runway") or {}
        notes.append(
            f"{lane.get('lane')}: best frontier {lane.get('rule')} is {current.get('entries')}/{current.get('denominator')} entries, "
            f"net {current.get('net_cents')}c, reconstructed share {current.get('reconstructed_share')}; needs "
            f"{runway.get('clean_rows_needed_for_coverage_gate')} clean selected row(s) for coverage, "
            f"{runway.get('clean_rows_needed_for_source_gate')} for source, "
            f"{runway.get('settled_rows_needed_for_sample_gate')} settled row(s) for sample, and "
            f"{runway.get('net_cents_needed')}c for a three-full-loss cushion."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Boundary-Clock Feature-Gate Frontier Runway",
        "",
        "Research-only audit; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Frontier generated UTC: `{report.get('frontier_generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Runway",
            "",
            "| lane | rule | entries/den | settled | W/L | net c | recon | blockers | clean rows for cov | clean rows for source | rows for sample | net c for cushion | clean rows all gates at avg | projected cov | projected recon | projected net c |",
            "|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for lane in report.get("lanes") or []:
        current = lane.get("current") or {}
        runway = lane.get("runway") or {}
        lines.append(
            f"| {lane.get('lane')} | {lane.get('rule')} | {current.get('entries')}/{current.get('denominator')} | "
            f"{current.get('settled')} | {current.get('wins')}/{current.get('losses')} | {fmt(current.get('net_cents'))} | "
            f"{fmt(current.get('reconstructed_share'))} | {', '.join(current.get('blockers') or []) or 'none'} | "
            f"{runway.get('clean_rows_needed_for_coverage_gate')} | {runway.get('clean_rows_needed_for_source_gate')} | "
            f"{runway.get('settled_rows_needed_for_sample_gate')} | {fmt(runway.get('net_cents_needed'))} | "
            f"{runway.get('clean_rows_needed_for_all_gates_at_current_avg')} | {fmt(runway.get('projected_coverage_pct'))} | "
            f"{fmt(runway.get('projected_reconstructed_share'))} | {fmt(runway.get('projected_net_cents_at_current_avg'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
