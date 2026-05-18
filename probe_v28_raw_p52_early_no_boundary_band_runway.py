"""Runway monitor for the frozen raw p52 early-NO boundary band skip.

Research-only; no live bot changes or orders.

This candidate is the strongest discovery row right now, but it only matters if
it survives post-freeze evidence. This report keeps the forward sample honest:
how many rows exist, how many are settled, what the delta is versus raw p52, and
how much more evidence is needed before the candidate is even discussable.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FROZEN_JSON = OUT_DIR / "v28_frozen_raw_p52_early_no_boundary_band_skip_latest.json"
ROBUSTNESS_JSON = OUT_DIR / "v28_raw_p52_early_no_boundary_band_robustness_latest.json"
OUT_JSON = OUT_DIR / "v28_raw_p52_early_no_boundary_band_runway_latest.json"
OUT_MD = OUT_DIR / "v28_raw_p52_early_no_boundary_band_runway_latest.md"

MIN_SETTLED = 30
TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0
MAX_SIMULATED_SHARE = 0.35


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


def sim_share(summary: dict[str, Any]) -> float | None:
    entries = int(as_float(summary.get("entries")) or 0)
    sim_count = int(as_float(summary.get("sim_count")) or 0)
    if entries <= 0:
        return None
    return sim_count / entries


def coverage_ok(summary: dict[str, Any]) -> bool:
    coverage = as_float(summary.get("coverage_pct"))
    return coverage is not None and TARGET_COVERAGE_MIN <= coverage <= TARGET_COVERAGE_MAX


def build_checks(frozen: dict[str, Any]) -> list[dict[str, Any]]:
    candidate = frozen.get("candidate_summary") or {}
    settled = int(as_float(candidate.get("settled")) or 0)
    net = as_float(candidate.get("net_cents")) or 0.0
    delta = as_float(frozen.get("delta_net_cents")) or 0.0
    share = sim_share(candidate)
    return [
        {
            "name": "settled_rows_ge_30",
            "passed": settled >= MIN_SETTLED,
            "value": settled,
            "needed": max(0, MIN_SETTLED - settled),
        },
        {
            "name": "coverage_75_to_90",
            "passed": coverage_ok(candidate),
            "value": candidate.get("coverage_pct"),
            "needed": f"{TARGET_COVERAGE_MIN}-{TARGET_COVERAGE_MAX}",
        },
        {
            "name": "candidate_net_positive",
            "passed": net > 0.0,
            "value": net,
            "needed": ">0",
        },
        {
            "name": "delta_vs_raw_positive",
            "passed": delta > 0.0,
            "value": delta,
            "needed": ">0",
        },
        {
            "name": "simulated_share_lte_35pct",
            "passed": share is not None and share <= MAX_SIMULATED_SHARE,
            "value": share,
            "needed": f"<={MAX_SIMULATED_SHARE}",
        },
    ]


def pending_sensitivity(frozen: dict[str, Any]) -> dict[str, Any]:
    skipped = frozen.get("skipped_rows") if isinstance(frozen.get("skipped_rows"), list) else []
    pending_skips = [row for row in skipped if row.get("side_won") is None]
    current_delta = as_float(frozen.get("delta_net_cents")) or 0.0
    # If a skipped row would have won, skipping it hurts by roughly the profit
    # the raw policy would have booked. Use a conservative 100c adverse stress
    # when fill economics are absent.
    adverse_per_pending = []
    for row in pending_skips:
        net = as_float(row.get("net_gross_cents_after_entry_fee"))
        if net is not None and net > 0:
            adverse_per_pending.append(net)
        else:
            adverse_per_pending.append(100.0)
    adverse_total = sum(adverse_per_pending)
    return {
        "pending_skipped_rows": len(pending_skips),
        "current_delta_cents": current_delta,
        "adverse_pending_swing_cents": adverse_total,
        "delta_after_all_pending_skips_win_cents": current_delta - adverse_total,
        "pending_markets": [row.get("market") for row in pending_skips],
    }


def build_report() -> dict[str, Any]:
    frozen = load_json(FROZEN_JSON)
    robustness = load_json(ROBUSTNESS_JSON)
    candidate = frozen.get("candidate_summary") or {}
    base = frozen.get("base") or {}
    skipped = frozen.get("skipped_summary") or {}
    checks = build_checks(frozen)
    ready_for_consideration = bool(checks) and all(row["passed"] for row in checks)
    rows_needed = max(0, MIN_SETTLED - int(as_float(candidate.get("settled")) or 0))
    notes = [
        f"Need {rows_needed} more settled post-freeze candidate rows to reach the 30-row evidence floor.",
        f"Discovery robustness pass is {robustness.get('passes_basic_robustness')}; forward validation is still separate.",
        "Promotion remains blocked unless the candidate keeps target coverage, positive net, positive delta versus raw p52, and acceptable simulated share.",
    ]
    if not frozen:
        notes = ["Frozen early-NO boundary band artifact is missing; run the frozen validator first."]
    return {
        "source": str(FROZEN_JSON),
        "freeze": frozen.get("freeze") or {},
        "future_denominator": frozen.get("future_denominator"),
        "excluded_in_progress_markets": frozen.get("excluded_in_progress_markets") or [],
        "candidate_live_ready": frozen.get("candidate_live_ready"),
        "ready_for_consideration": ready_for_consideration,
        "checks": checks,
        "base": base,
        "candidate_summary": candidate,
        "skipped_summary": skipped,
        "delta_net_cents": frozen.get("delta_net_cents"),
        "blockers": frozen.get("blockers") or [],
        "pending_sensitivity": pending_sensitivity(frozen),
        "robustness": {
            "passes_basic_robustness": robustness.get("passes_basic_robustness"),
            "top_target_coverage_positive_delta_count": robustness.get("top_target_coverage_positive_delta_count"),
            "worst_leave_one_skipped": (robustness.get("leave_one_skipped") or [{}])[0],
        },
        "interpretation": notes,
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
    freeze = report.get("freeze") or {}
    pending = report.get("pending_sensitivity") or {}
    lines = [
        "# v28 Raw p52 Early-NO Boundary Band Runway",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Future denominator: `{report.get('future_denominator')}`",
        f"- Candidate live-ready: `{report.get('candidate_live_ready')}`",
        f"- Ready for consideration: `{report.get('ready_for_consideration')}`",
        f"- Delta vs raw p52: `{fmt(report.get('delta_net_cents'))}c`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Checks",
        "",
        "| check | passed | value | needed |",
        "|---|---|---:|---:|",
    ]
    for row in report.get("checks") or []:
        lines.append(
            f"| {row.get('name')} | {row.get('passed')} | {fmt(row.get('value'))} | {fmt(row.get('needed'))} |"
        )
    lines.extend([
        "",
        "## Scorecard",
        "",
        "| row | entries | settled | W/L | coverage | net c | actual/sim | sim share |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for name in ["base", "candidate_summary", "skipped_summary"]:
        row = report.get(name) or {}
        lines.append(
            f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | "
            f"{row.get('actual_count')}/{row.get('sim_count')} | {fmt(sim_share(row))} |"
        )
    lines.extend([
        "",
        "## Pending Sensitivity",
        "",
        f"- Pending skipped rows: `{pending.get('pending_skipped_rows')}`",
        f"- Adverse swing if all pending skips would have won: `{fmt(pending.get('adverse_pending_swing_cents'))}c`",
        f"- Delta after that stress: `{fmt(pending.get('delta_after_all_pending_skips_win_cents'))}c`",
        f"- Pending markets: `{', '.join(str(x) for x in pending.get('pending_markets') or []) or 'none'}`",
        "",
        "## Current Read",
        "",
    ])
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
