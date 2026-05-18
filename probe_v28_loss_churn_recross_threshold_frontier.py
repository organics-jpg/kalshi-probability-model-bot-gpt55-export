"""Recross threshold frontier on the materialized exit-clock snapshot.

Research-only; no live bot changes or orders.

The recross_ge_045 clue weakened after moving from the continuous scorecard to
a fixed exit-clock denominator. This scan asks whether nearby thresholds form a
stable physical band or whether the signal is just a sparse threshold artifact.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_loss_churn_recross_exit_clock_join_audit import (
    JOIN_TOLERANCE_SECONDS,
    MATERIALIZED_EXIT_CLOCK_JSON,
    SCORECARD_JSON,
    joined_rows,
    load_json,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_loss_churn_recross_threshold_frontier_latest.json"
OUT_MD = OUT_DIR / "v28_loss_churn_recross_threshold_frontier_latest.md"

THRESHOLDS = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
WEIGHTS = [0.25, 0.50, 0.75, 1.00]


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def money(value: Any) -> str:
    cents = fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def selected_rows(rows: list[dict[str, Any]], threshold: float) -> list[dict[str, Any]]:
    return [
        row for row in rows
        if row.get("recross_hazard_score") is not None
        and fnum(row.get("recross_hazard_score"), -1.0) >= threshold
    ]


def summarize(rows: list[dict[str, Any]], threshold: float, hold_weight: float) -> dict[str, Any]:
    selected = selected_rows(rows, threshold)
    current_net = sum(fnum(row.get("actual_gross_cents")) for row in rows)
    candidate_values = []
    selected_delta = 0.0
    for row in rows:
        current = fnum(row.get("actual_gross_cents"))
        hold = fnum(row.get("hold_gross_cents"))
        if row in selected:
            delta = (hold - current) * hold_weight
            candidate_values.append(current + delta)
            selected_delta += delta
        else:
            candidate_values.append(current)
    helpful = [row for row in selected if fnum(row.get("hold_gross_cents")) > fnum(row.get("actual_gross_cents"))]
    harmful = [row for row in selected if fnum(row.get("hold_gross_cents")) < fnum(row.get("actual_gross_cents"))]
    flat = [row for row in selected if fnum(row.get("hold_gross_cents")) == fnum(row.get("actual_gross_cents"))]
    loss_flips = 0
    new_losses = 0
    for row in selected:
        current = fnum(row.get("actual_gross_cents"))
        hold = fnum(row.get("hold_gross_cents"))
        candidate = current + ((hold - current) * hold_weight)
        if current < 0 <= candidate:
            loss_flips += 1
        if current >= 0 > candidate:
            new_losses += 1
    candidate_net = sum(candidate_values)
    blockers = ["diagnostic_snapshot_frontier", "not_frozen_forward"]
    if len(selected) < 30:
        blockers.append("selected_decisions_lt_30")
    if selected_delta <= 0:
        blockers.append("delta_not_positive")
    if harmful:
        blockers.append("harmful_hold_rows_present")
    if new_losses:
        blockers.append("new_losses_created")
    if int(max(0.0, candidate_net) // 100.0) < 3:
        blockers.append("full_loss_cushion_lt_3")
    return {
        "threshold": threshold,
        "hold_weight": hold_weight,
        "rows": len(rows),
        "selected_rows": len(selected),
        "current_net_cents": current_net,
        "candidate_net_cents": candidate_net,
        "delta_cents": selected_delta,
        "helpful_rows": len(helpful),
        "harmful_rows": len(harmful),
        "flat_rows": len(flat),
        "loss_flips": loss_flips,
        "new_losses": new_losses,
        "full_loss_cushion": int(max(0.0, candidate_net) // 100.0),
        "blockers": blockers,
    }


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "exit_reason": row.get("exit_reason"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "actual_gross_cents": row.get("actual_gross_cents"),
        "hold_gross_cents": row.get("hold_gross_cents"),
        "hold_delta_cents": fnum(row.get("hold_gross_cents")) - fnum(row.get("actual_gross_cents")),
    }


def build_report() -> dict[str, Any]:
    scorecard = load_json(SCORECARD_JSON)
    snapshot = load_json(MATERIALIZED_EXIT_CLOCK_JSON)
    scorecard_rows = [row for row in scorecard.get("rows") or [] if isinstance(row, dict)]
    exit_rows = [row for row in snapshot.get("rows") or [] if isinstance(row, dict)]
    joined, unmatched, ambiguous = joined_rows(exit_rows, scorecard_rows, JOIN_TOLERANCE_SECONDS)
    rows = [
        row for row in joined
        if row.get("actual_gross_cents") is not None
        and row.get("hold_gross_cents") is not None
        and row.get("recross_hazard_score") is not None
    ]
    frontier = [
        summarize(rows, threshold, weight)
        for threshold in THRESHOLDS
        for weight in WEIGHTS
    ]
    frontier.sort(
        key=lambda row: (
            int(bool(row.get("harmful_rows"))),
            -fnum(row.get("delta_cents")),
            -fnum(row.get("selected_rows")),
        )
    )
    clean = [row for row in frontier if not row.get("harmful_rows") and not row.get("new_losses")]
    best_clean = clean[0] if clean else {}
    full_hold = [row for row in frontier if row.get("hold_weight") == 1.0]
    best_full_hold = full_hold[0] if full_hold else {}
    blockers = ["research_only", "not_frozen_forward", "snapshot_threshold_scan_not_watch"]
    if unmatched:
        blockers.append("unmatched_join_rows_present")
    if ambiguous:
        blockers.append("ambiguous_join_rows_present")
    if (best_clean.get("selected_rows") or 0) < 30:
        blockers.append("best_clean_selected_decisions_lt_30")
    interpretation = [
        "The fixed exit-clock denominator keeps the recross signal clean but sparse.",
        "No scanned threshold reaches the 30 selected-decision evidence floor.",
        "Use this as mechanism evidence only; do not freeze a recross exit watch from the snapshot scan.",
    ]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_snapshot": str(MATERIALIZED_EXIT_CLOCK_JSON),
        "snapshot_generated_at_utc": snapshot.get("generated_at_utc"),
        "join_tolerance_seconds": JOIN_TOLERANCE_SECONDS,
        "joined_rows": len(joined),
        "scored_rows_with_recross": len(rows),
        "unmatched_rows": len(unmatched),
        "ambiguous_rows": len(ambiguous),
        "frontier": frontier,
        "best_clean": best_clean,
        "best_full_hold": best_full_hold,
        "blockers": blockers,
        "selected_examples_best_clean": [
            compact(row)
            for row in selected_rows(rows, fnum(best_clean.get("threshold"), 999.0))[:12]
        ],
        "interpretation": interpretation,
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    best = report.get("best_clean") or {}
    full = report.get("best_full_hold") or {}
    lines = [
        "# v28 Loss-Churn Recross Threshold Frontier",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Source snapshot: `{report.get('source_snapshot')}`",
        f"- Joined / scored rows: `{report.get('joined_rows')}` / `{report.get('scored_rows_with_recross')}`",
        f"- Best clean threshold/weight: `{best.get('threshold')}` / `{best.get('hold_weight')}`",
        f"- Best clean selected/delta/net: `{best.get('selected_rows')}` / `{money(best.get('delta_cents'))}` / `{money(best.get('candidate_net_cents'))}`",
        f"- Best full-hold selected/delta/net: `{full.get('selected_rows')}` / `{money(full.get('delta_cents'))}` / `{money(full.get('candidate_net_cents'))}`",
        f"- Blockers: `{', '.join(report.get('blockers') or [])}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Frontier",
        "",
        "| threshold | weight | selected | delta | candidate net | helpful/harmful/flat | flips/new losses | cushion | blockers |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("frontier") or []:
        lines.append(
            f"| {row.get('threshold')} | {row.get('hold_weight')} | {row.get('selected_rows')} | "
            f"{money(row.get('delta_cents'))} | {money(row.get('candidate_net_cents'))} | "
            f"{row.get('helpful_rows')}/{row.get('harmful_rows')}/{row.get('flat_rows')} | "
            f"{row.get('loss_flips')}/{row.get('new_losses')} | {row.get('full_loss_cushion')} | "
            f"{', '.join(row.get('blockers') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
