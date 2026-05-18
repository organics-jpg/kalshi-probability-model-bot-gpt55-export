"""Live-validation runway for shadow entry candidates.

Research-only; no live bot changes or orders.

Some entry candidates beat the v28 control in shadow, but much of their sample
comes from actionable rejected rows rather than actual approved entries. This
report estimates how much future non-simulated evidence is needed before those
candidate results become operationally credible.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OVERLAP_JSON = OUT_DIR / "v28_candidate_vs_control_overlap_latest.json"
OUT_JSON = OUT_DIR / "v28_candidate_live_validation_runway_latest.json"
OUT_MD = OUT_DIR / "v28_candidate_live_validation_runway_latest.md"

MAX_SIMULATED_SHARE = 0.35
MIN_SETTLED = 30
TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0


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


def future_actual_needed_for_sim_share(added_rejects: int, entries: int, max_share: float) -> int:
    if entries <= 0:
        return 0
    if added_rejects / entries <= max_share:
        return 0
    return max(0, math.ceil(added_rejects / max_share - entries))


def build_report() -> dict[str, Any]:
    overlap = load_json(OVERLAP_JSON)
    rows = overlap.get("rows") if isinstance(overlap.get("rows"), list) else []
    out_rows = []
    for row in rows:
        entries = int(as_float(row.get("candidate_entries")) or 0)
        settled = int(as_float(row.get("candidate_settled")) or 0)
        added = int(as_float(row.get("candidate_added_reject_count")) or 0)
        gross = as_float(row.get("candidate_gross_cents")) or 0.0
        coverage = as_float(row.get("candidate_coverage_pct"))
        future_actual_needed = future_actual_needed_for_sim_share(added, entries, MAX_SIMULATED_SHARE)
        settled_needed = max(0, MIN_SETTLED - settled)
        target_coverage = coverage is not None and TARGET_COVERAGE_MIN <= coverage <= TARGET_COVERAGE_MAX
        validation_needed = max(future_actual_needed, settled_needed)
        out_rows.append({
            "policy": row.get("policy"),
            "coverage_pct": coverage,
            "target_coverage": target_coverage,
            "entries": entries,
            "settled": settled,
            "wins": row.get("candidate_wins"),
            "losses": row.get("candidate_losses"),
            "gross_cents": gross,
            "overlap_delta_cents": row.get("overlap_delta_cents"),
            "added_reject_count": added,
            "approved_entry_count": row.get("candidate_approved_entry_count"),
            "simulated_share": row.get("candidate_simulated_share"),
            "future_actual_entries_needed_for_sim_share_lte_35": future_actual_needed,
            "settled_rows_needed_for_30": settled_needed,
            "minimum_future_validation_rows_needed": validation_needed,
            "loss_cushion_cents_before_flat": max(0.0, gross),
            "full_100c_losses_absorbable_before_flat": int(max(0.0, gross) // 100),
            "blockers": row.get("blockers") or [],
        })
    ranked = sorted(
        out_rows,
        key=lambda row: (
            bool(row.get("target_coverage")),
            -int(row.get("minimum_future_validation_rows_needed") or 999999),
            float(row.get("gross_cents") or -999999.0),
        ),
        reverse=True,
    )
    return {
        "source": str(OVERLAP_JSON),
        "max_simulated_share": MAX_SIMULATED_SHARE,
        "min_settled": MIN_SETTLED,
        "rows": out_rows,
        "ranked": ranked,
        "interpretation": current_read(ranked),
    }


def current_read(rows: list[dict[str, Any]]) -> list[str]:
    notes: list[str] = []
    target_rows = [row for row in rows if row.get("target_coverage")]
    if target_rows:
        best = max(target_rows, key=lambda row: float(row.get("gross_cents") or -999999.0))
        notes.append(
            f"Best target-coverage gross row is {best['policy']} at {best['gross_cents']}c, but it needs {best['future_actual_entries_needed_for_sim_share_lte_35']} future actual-only entries to bring simulated share to <=35%."
        )
    closest = min(rows, key=lambda row: int(row.get("minimum_future_validation_rows_needed") or 999999), default=None)
    if closest:
        notes.append(
            f"Closest row to validation by count is {closest['policy']} needing {closest['minimum_future_validation_rows_needed']} future validation rows, coverage {closest['coverage_pct']}."
        )
    notes.append("This runway is not a live-trading instruction; it defines how much forward evidence is still missing.")
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
        "# v28 Candidate Live-Validation Runway",
        "",
        "How much future non-simulated evidence shadow candidates still need. No candidate is promoted here.",
        "",
        f"- Max simulated share: `{report.get('max_simulated_share')}`",
        f"- Minimum settled rows: `{report.get('min_settled')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Runway",
        "",
        "| policy | coverage | gross c | sim share | future actual needed | settled needed | min validation rows | loss cushion c | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("ranked") or []:
        lines.append(
            f"| `{row.get('policy')}` | {fmt(row.get('coverage_pct'))} | {fmt(row.get('gross_cents'))} | "
            f"{fmt(row.get('simulated_share'))} | {row.get('future_actual_entries_needed_for_sim_share_lte_35')} | "
            f"{row.get('settled_rows_needed_for_30')} | {row.get('minimum_future_validation_rows_needed')} | "
            f"{fmt(row.get('loss_cushion_cents_before_flat'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
