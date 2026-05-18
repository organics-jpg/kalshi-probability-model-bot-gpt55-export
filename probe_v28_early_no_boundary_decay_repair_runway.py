"""Runway monitor for frozen early-NO boundary decay repair entry.

Research-only; no live bot changes or orders.

This candidate is one of the few target-coverage-ish frozen lanes with positive
forward P&L. The point of this report is to keep it honest: sample size,
coverage, delta versus the target surface, pending danger rows, and how fragile
the current P&L buffer is to future losses.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FROZEN_JSON = OUT_DIR / "v28_frozen_early_no_boundary_decay_repair_entry_latest.json"
OUT_JSON = OUT_DIR / "v28_early_no_boundary_decay_repair_runway_latest.json"
OUT_MD = OUT_DIR / "v28_early_no_boundary_decay_repair_runway_latest.md"

MIN_SETTLED = 30
COVERAGE_MIN = 75.0
COVERAGE_MAX = 90.0


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


def checks(report: dict[str, Any]) -> list[dict[str, Any]]:
    candidate = report.get("candidate_summary") or {}
    settled = int(as_float(candidate.get("settled")) or 0)
    coverage = as_float(candidate.get("coverage_pct"))
    net = as_float(candidate.get("net_cents")) or 0.0
    delta = as_float(report.get("delta_vs_target_cents")) or 0.0
    return [
        {
            "name": "settled_rows_ge_30",
            "passed": settled >= MIN_SETTLED,
            "actual": settled,
            "required": f">={MIN_SETTLED}",
            "remaining": max(0, MIN_SETTLED - settled),
        },
        {
            "name": "coverage_75_to_90",
            "passed": coverage is not None and COVERAGE_MIN <= coverage <= COVERAGE_MAX,
            "actual": coverage,
            "required": f"{COVERAGE_MIN}-{COVERAGE_MAX}",
            "remaining": None,
        },
        {
            "name": "net_positive",
            "passed": net > 0.0,
            "actual": net,
            "required": ">0c",
            "remaining": None,
        },
        {
            "name": "delta_vs_target_positive",
            "passed": delta > 0.0,
            "actual": delta,
            "required": ">0c",
            "remaining": None,
        },
    ]


def pending_danger_stress(report: dict[str, Any]) -> dict[str, Any]:
    danger_rows = report.get("danger_rows") if isinstance(report.get("danger_rows"), list) else []
    pending = [row for row in danger_rows if row.get("side_won") is None]
    current_delta = as_float(report.get("delta_vs_target_cents")) or 0.0
    # If a pending danger row would have won, the skip hurts by the profit that
    # the base target surface would have kept. Use 100c if economics are absent.
    adverse = 0.0
    for row in pending:
        net = as_float(row.get("net_cents"))
        adverse += net if net is not None and net > 0 else 100.0
    return {
        "pending_danger_rows": len(pending),
        "pending_markets": [row.get("market") for row in pending],
        "current_delta_cents": current_delta,
        "adverse_if_all_pending_danger_would_win_cents": adverse,
        "stressed_delta_cents": current_delta - adverse,
    }


def fragility(report: dict[str, Any]) -> dict[str, Any]:
    candidate = report.get("candidate_summary") or {}
    net = as_float(candidate.get("net_cents")) or 0.0
    delta = as_float(report.get("delta_vs_target_cents")) or 0.0
    settled = int(as_float(candidate.get("settled")) or 0)
    rows_needed = max(0, MIN_SETTLED - settled)
    return {
        "rows_needed_for_30": rows_needed,
        "net_cushion_cents": net,
        "delta_cushion_cents": delta,
        "full_100c_losses_before_net_flat": int(max(0.0, net) // 100.0),
        "full_100c_losses_before_delta_flat": int(max(0.0, delta) // 100.0),
        "net_after_one_full_loss_cents": net - 100.0,
        "net_after_two_full_losses_cents": net - 200.0,
        "delta_after_two_full_losses_cents": delta - 200.0,
    }


def leave_one(report: dict[str, Any], section: str) -> list[dict[str, Any]]:
    rows = report.get(section) if isinstance(report.get(section), list) else []
    candidate = report.get("candidate_summary") or {}
    base_net = as_float(candidate.get("net_cents")) or 0.0
    out = []
    for row in rows:
        net = as_float(row.get("net_cents"))
        if net is None:
            continue
        out.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "row_net_cents": net,
            "candidate_net_without_row_cents": base_net - net,
            "source_section": section,
        })
    return sorted(out, key=lambda row: float(row["candidate_net_without_row_cents"]))


def build_report() -> dict[str, Any]:
    frozen = load_json(FROZEN_JSON)
    runway_checks = checks(frozen)
    ready = bool(runway_checks) and all(row["passed"] for row in runway_checks)
    notes = interpretation(frozen, runway_checks)
    return {
        "source": str(FROZEN_JSON),
        "freeze": frozen.get("freeze") or {},
        "future_denominator": frozen.get("future_denominator"),
        "candidate_live_ready": frozen.get("candidate_live_ready"),
        "ready_for_consideration": ready,
        "checks": runway_checks,
        "blockers": frozen.get("blockers") or [],
        "target_summary": frozen.get("target_summary") or {},
        "danger_summary": frozen.get("danger_summary") or {},
        "repair_summary": frozen.get("repair_summary") or {},
        "candidate_summary": frozen.get("candidate_summary") or {},
        "delta_vs_target_cents": frozen.get("delta_vs_target_cents"),
        "pending_danger_stress": pending_danger_stress(frozen),
        "fragility": fragility(frozen),
        "worst_leave_one_repair": leave_one(frozen, "repair_rows")[:5],
        "danger_rows": frozen.get("danger_rows") or [],
        "repair_rows": frozen.get("repair_rows") or [],
        "interpretation": notes,
    }


def interpretation(report: dict[str, Any], runway_checks: list[dict[str, Any]]) -> list[str]:
    candidate = report.get("candidate_summary") or {}
    target = report.get("target_summary") or {}
    settled = int(as_float(candidate.get("settled")) or 0)
    rows_needed = max(0, MIN_SETTLED - settled)
    notes = [
        f"Need {rows_needed} more settled candidate rows before the sample-size gate is met.",
        f"Candidate net is {candidate.get('net_cents')}c versus target {target.get('net_cents')}c.",
        "The rule has a clean physics story, but current evidence can be broken by a small number of adverse future rows.",
    ]
    failed = [row["name"] for row in runway_checks if not row["passed"]]
    if failed:
        notes.append(f"Current failed checks: {', '.join(failed)}.")
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
    freeze = report.get("freeze") or {}
    stress = report.get("pending_danger_stress") or {}
    frag = report.get("fragility") or {}
    lines = [
        "# v28 Early-NO Boundary Decay Repair Runway",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Future denominator: `{report.get('future_denominator')}`",
        f"- Candidate live-ready: `{report.get('candidate_live_ready')}`",
        f"- Ready for consideration: `{report.get('ready_for_consideration')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Checks",
        "",
        "| check | passed | actual | required | remaining |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in report.get("checks") or []:
        lines.append(
            f"| {row.get('name')} | {row.get('passed')} | {fmt(row.get('actual'))} | "
            f"{fmt(row.get('required'))} | {fmt(row.get('remaining'))} |"
        )
    lines.extend([
        "",
        "## Scorecard",
        "",
        "| surface | entries | settled | W/L | coverage | net c | avg c |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for name in ["target_summary", "danger_summary", "repair_summary", "candidate_summary"]:
        row = report.get(name) or {}
        lines.append(
            f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    lines.extend([
        "",
        "## Fragility",
        "",
        f"- Rows needed for 30: `{frag.get('rows_needed_for_30')}`",
        f"- Net cushion: `{fmt(frag.get('net_cushion_cents'))}c`",
        f"- Delta cushion: `{fmt(frag.get('delta_cushion_cents'))}c`",
        f"- Full 100c losses before net flat: `{frag.get('full_100c_losses_before_net_flat')}`",
        f"- Full 100c losses before delta flat: `{frag.get('full_100c_losses_before_delta_flat')}`",
        "",
        "## Pending Danger Stress",
        "",
        f"- Pending danger rows: `{stress.get('pending_danger_rows')}`",
        f"- Pending markets: `{', '.join(str(x) for x in stress.get('pending_markets') or []) or 'none'}`",
        f"- Stressed delta if all pending danger rows would have won: `{fmt(stress.get('stressed_delta_cents'))}c`",
        "",
        "## Current Read",
        "",
    ])
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Worst Leave-One Repair Rows",
        "",
        "| market | side | row net c | candidate net without row c |",
        "|---|---|---:|---:|",
    ])
    for row in report.get("worst_leave_one_repair") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('row_net_cents'))} | "
            f"{fmt(row.get('candidate_net_without_row_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
