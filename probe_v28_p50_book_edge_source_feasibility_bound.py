"""Source-feasibility bound for frozen p50 book-edge entry.

Research-only; no live bot changes or orders.

This checks whether the p50 book-edge parent can satisfy the broad-entry source
gate from its current selected row pool. It is a hard arithmetic bound, not a
new candidate: if the selected pool does not contain enough approved rows, no
observable reshuffle of those rows can reach both target coverage and <=35%
rejected-actionable share.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_frozen_p50_book_edge_entry_latest.json"
DRILLDOWN_JSON = OUT_DIR / "v28_p50_book_edge_source_failure_drilldown_latest.json"
OUT_JSON = OUT_DIR / "v28_p50_book_edge_source_feasibility_bound_latest.json"
OUT_MD = OUT_DIR / "v28_p50_book_edge_source_feasibility_bound_latest.md"

TARGET_COVERAGE_MIN = 0.75
TARGET_COVERAGE_MAX = 0.90
MAX_REJECTED_SHARE = 0.35


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


def row_net(row: dict[str, Any]) -> float:
    return as_float(row.get("gross_cents")) or as_float(row.get("weighted_net_cents")) or as_float(row.get("net_cents")) or 0.0


def summarize_source(rows: list[dict[str, Any]]) -> dict[str, Any]:
    approved = [row for row in rows if row.get("source") == "approved_entry"]
    rejected = [row for row in rows if row.get("source") == "rejected_actionable"]
    return {
        "entries": len(rows),
        "approved": len(approved),
        "rejected": len(rejected),
        "rejected_share": len(rejected) / len(rows) if rows else None,
        "net_cents": sum(row_net(row) for row in rows),
        "wins": sum(1 for row in rows if row.get("side_won") is True),
        "losses": sum(1 for row in rows if row.get("side_won") is False),
    }


def bound_for(denominator: int, approved_available: int) -> dict[str, Any]:
    target_min_entries = math.ceil(denominator * TARGET_COVERAGE_MIN)
    target_max_entries = math.floor(denominator * TARGET_COVERAGE_MAX)
    approved_needed_at_min = math.ceil(target_min_entries * (1.0 - MAX_REJECTED_SHARE))
    max_entries_source_clean = math.floor(approved_available / (1.0 - MAX_REJECTED_SHARE)) if approved_available else 0
    return {
        "denominator_markets": denominator,
        "target_min_entries": target_min_entries,
        "target_max_entries": target_max_entries,
        "approved_available": approved_available,
        "approved_needed_at_min_coverage": approved_needed_at_min,
        "approved_deficit_at_min_coverage": max(0, approved_needed_at_min - approved_available),
        "max_entries_at_source_gate_from_available_approved": max_entries_source_clean,
        "max_coverage_at_source_gate_pct": (max_entries_source_clean / denominator * 100.0) if denominator else 0.0,
        "source_gate_feasible_at_target_coverage": max_entries_source_clean >= target_min_entries,
    }


def build_report() -> dict[str, Any]:
    p50 = load_json(SOURCE_JSON)
    drilldown = load_json(DRILLDOWN_JSON)
    rows = [row for row in p50.get("rows") or [] if isinstance(row, dict)]
    denominator = int(as_float(p50.get("future_denominator_markets")) or 0)
    source = summarize_source(rows)
    bound = bound_for(denominator, int(source.get("approved") or 0))

    variants = []
    for variant in drilldown.get("variants") or []:
        if not isinstance(variant, dict):
            continue
        variants.append({
            "variant": variant.get("variant"),
            "entries": variant.get("entries"),
            "wins": variant.get("wins"),
            "losses": variant.get("losses"),
            "gross_cents": variant.get("gross_cents"),
            "coverage_pct": variant.get("coverage_pct"),
            "rejected_share": variant.get("rejected_actionable_share"),
            "weighted_rejected_share": variant.get("weighted_rejected_actionable_share"),
            "blockers": variant.get("blockers"),
        })
    variants.sort(key=lambda row: as_float(row.get("gross_cents")) or -999999.0, reverse=True)

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_artifact": str(SOURCE_JSON),
        "candidate": "p50_book_plus_05_edge_nonnegative",
        "selected_source_summary": source,
        "feasibility_bound": bound,
        "top_variant_source_status": variants[:12],
        "candidate_live_ready": False,
        "interpretation": [
            f"At {denominator} denominator markets, 75% coverage needs {bound.get('target_min_entries')} selected markets.",
            f"With a 35% rejected-actionable cap, that minimum target needs {bound.get('approved_needed_at_min_coverage')} approved rows.",
            f"The current selected p50 pool has only {source.get('approved')} approved rows, so its source-clean max coverage is {bound.get('max_coverage_at_source_gate_pct')}%.",
            "Therefore p50 book-edge cannot be made broad-and-source-clean by reshuffling its current selected rows; it needs new clean approved evidence or a different approved-rich entry surface.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    source = report.get("selected_source_summary") or {}
    bound = report.get("feasibility_bound") or {}
    lines = [
        "# v28 p50 Book-Edge Source Feasibility Bound",
        "",
        "Research-only arithmetic source-quality bound. No live orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Candidate: `{report.get('candidate')}`",
        f"- Selected entries/approved/rejected/share: `{source.get('entries')}/{source.get('approved')}/{source.get('rejected')}/{fmt(source.get('rejected_share'))}`",
        f"- Selected W-L/net: `{source.get('wins')}-{source.get('losses')}/{fmt(source.get('net_cents'))}c`",
        f"- Target min/max entries: `{bound.get('target_min_entries')}/{bound.get('target_max_entries')}`",
        f"- Approved needed at min target coverage: `{bound.get('approved_needed_at_min_coverage')}`",
        f"- Approved deficit at min target coverage: `{bound.get('approved_deficit_at_min_coverage')}`",
        f"- Max source-clean entries/coverage from current selected approved pool: `{bound.get('max_entries_at_source_gate_from_available_approved')}/{fmt(bound.get('max_coverage_at_source_gate_pct'))}%`",
        f"- Source gate feasible at target coverage: `{bound.get('source_gate_feasible_at_target_coverage')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Top Variant Source Status",
        "",
        "| variant | entries | W-L | gross c | coverage % | rejected share | weighted rejected share | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("top_variant_source_status") or []:
        lines.append(
            f"| `{row.get('variant')}` | {row.get('entries')} | {row.get('wins')}-{row.get('losses')} | "
            f"{fmt(row.get('gross_cents'))} | {fmt(row.get('coverage_pct'))} | {fmt(row.get('rejected_share'))} | "
            f"{fmt(row.get('weighted_rejected_share'))} | `{', '.join(row.get('blockers') or []) or 'none'}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
