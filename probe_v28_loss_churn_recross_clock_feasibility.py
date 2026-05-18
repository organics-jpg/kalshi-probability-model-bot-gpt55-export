"""Feasibility check for a recross-based loss-churn shadow clock.

Research-only; no live bot changes or orders.

The full-denominator replay shows recross_ge_045 is an observable-looking
loss-churn guard, but a replay is not a frozen clock. This probe checks which
fields are present in the current scorecard and what is still needed before
creating a strict forward watch.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SCORECARD_JSON = OUT_DIR / "v28_continuous_scorecard_latest.json"
REPLAY_JSON = OUT_DIR / "v28_loss_churn_observable_full_denominator_replay_latest.json"
OUT_JSON = OUT_DIR / "v28_loss_churn_recross_clock_feasibility_latest.json"
OUT_MD = OUT_DIR / "v28_loss_churn_recross_clock_feasibility_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


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


def has_value(row: dict[str, Any], field: str) -> bool:
    return row.get(field) not in (None, "")


def build_report() -> dict[str, Any]:
    scorecard = load_json(SCORECARD_JSON)
    replay = load_json(REPLAY_JSON)
    rows = [row for row in scorecard.get("rows") or [] if isinstance(row, dict)]
    known = [
        row for row in rows
        if row.get("actual_gross_cents") is not None and row.get("hold_gross_cents") is not None
    ]
    selected = [row for row in known if fnum(row.get("recross_hazard_score"), -1.0) >= 0.45]
    fields = [
        "entry_ts",
        "market",
        "side",
        "recross_hazard_score",
        "h6_recross_hazard_high",
        "exit_cents",
        "exit_reason",
        "actual_gross_cents",
        "hold_gross_cents",
        "exit_ts",
    ]
    availability = {
        field: {
            "all_known_present": sum(1 for row in known if has_value(row, field)),
            "selected_present": sum(1 for row in selected if has_value(row, field)),
        }
        for field in fields
    }
    blockers = [
        "research_only",
        "not_frozen_forward",
        "full_denominator_replay_not_shadow_clock",
        "selected_decisions_lt_30",
    ]
    if availability["entry_ts"]["selected_present"] != len(selected):
        blockers.append("selected_rows_missing_entry_ts")
    if availability["recross_hazard_score"]["selected_present"] != len(selected):
        blockers.append("selected_rows_missing_recross_score")
    if availability["exit_ts"]["selected_present"] != len(selected):
        blockers.append("scorecard_missing_exit_ts_for_exit_clock")
    if availability["exit_cents"]["selected_present"] < len(selected):
        blockers.append("some_selected_rows_have_no_exit_event")
    best = replay.get("best_clean_replay") or {}
    interpretation = [
        "recross_ge_045 is observable in the current scorecard at row/entry scope.",
        "The current scorecard does not provide an exit_ts field, so a strict exit watch needs a separate exit-event clock or an existing exit-clock join source.",
        "Do not treat this as a frozen candidate until a pre-registered clock writes post-freeze rows.",
    ]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "rule": "recross_ge_045",
        "scorecard_rows": len(rows),
        "known_rows": len(known),
        "selected_rows": len(selected),
        "field_availability": availability,
        "best_replay": best,
        "blockers": blockers,
        "interpretation": interpretation,
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    best = report.get("best_replay") or {}
    lines = [
        "# v28 Loss-Churn Recross Clock Feasibility",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Rule: `{report.get('rule')}`",
        f"- Known / selected rows: `{report.get('known_rows')}` / `{report.get('selected_rows')}`",
        f"- Replay delta / candidate net: `{money(best.get('delta_cents'))}` / `{money(best.get('candidate_net_cents'))}`",
        f"- Replay harmful / new losses: `{best.get('harmful_rows')}` / `{best.get('new_losses')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or [])}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Field Availability",
        "",
        "| field | known present | selected present |",
        "|---|---:|---:|",
    ])
    for field, counts in (report.get("field_availability") or {}).items():
        lines.append(f"| `{field}` | {counts.get('all_known_present')} | {counts.get('selected_present')} |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
