"""Frozen forward validator for the early-boundary wait/repair candidate.

Research-only; no live bot changes or orders.

Frozen rule:
    Start from the target 75% coverage policy. For rows with seconds_to_close
    >= 780, abs_d_sigma <= 0.45, and recross_hazard_score >= 0.55, do not buy
    immediately. Wait for a same-market row aged to <=480 seconds-to-close
    with p>=0.50 and nonnegative executable edge; if none appears, abstain.
    Restore the 75% coverage floor with clean calmer repair rows.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_early_clock_wait_bakeoff import score_policy
from probe_v28_frozen_early_no_boundary_decay_repair_entry import future_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_early_boundary_wait_repair_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_early_boundary_wait_repair_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_early_boundary_wait_repair_latest.md"

POLICY = "raw_p50_turbulence_valve_edge4_p60_recross75_near25"
MIN_SETTLED = 30
MIN_COVERAGE = 75.0
MAX_COVERAGE = 90.0


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
        "base_policy": POLICY,
        "candidate": "early_boundary_wait480_p50_any_side",
        "danger_rule": "seconds_to_close>=780 and abs_d_sigma<=0.45 and recross_hazard_score>=0.55",
        "wait_rule": "first same-market any-side row with seconds_to_close<=480, p>=0.50, executable raw edge>=0, max delay 360s",
        "repair_rule": "clean repair rows ranked by farthest boundary geometry",
        "coverage_floor": MIN_COVERAGE,
        "coverage_ceiling": MAX_COVERAGE,
        "physics": (
            "Very early near-boundary high-recross entries often express unresolved path churn, "
            "not stable fair value. Clock decay should reveal whether the thesis survives; "
            "otherwise broad coverage should be repaired from calmer geometry rather than paid for immediately."
        ),
        "params": {
            "danger_mode": "early_boundary",
            "wait_stc": 480.0,
            "p_floor": 0.50,
            "side_mode": "any_side",
        },
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def blockers(candidate: dict[str, Any]) -> list[str]:
    summary = candidate.get("candidate_summary") or {}
    settled = int(float(summary.get("settled") or 0))
    net = float(summary.get("net_cents") or 0.0)
    coverage = summary.get("coverage_pct")
    out = []
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if net <= 0.0:
        out.append("net_not_positive")
    if coverage is None or float(coverage) < MIN_COVERAGE:
        out.append("coverage_below_floor")
    if coverage is not None and float(coverage) > MAX_COVERAGE:
        out.append("coverage_above_ceiling")
    return out


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    all_rows, target, denominator = future_surfaces(state["freeze_ts_utc"])
    params = state["params"]
    candidate = score_policy(
        all_rows,
        target,
        denominator,
        wait_stc=float(params["wait_stc"]),
        p_floor=float(params["p_floor"]),
        danger_mode=str(params["danger_mode"]),
        side_mode=str(params["side_mode"]),
    )
    block = blockers(candidate)
    summary = candidate.get("candidate_summary") or {}
    target_summary = candidate.get("target_summary") or {}
    return {
        "diagnostic": "frozen_early_boundary_wait_repair",
        "freeze": state,
        "future_denominator": denominator,
        "policy": state["candidate"],
        "target_summary": target_summary,
        "danger_summary": candidate.get("danger_summary"),
        "replacement_summary": candidate.get("replacement_summary"),
        "repair_summary": candidate.get("repair_summary"),
        "candidate_summary": summary,
        "delta_vs_target_cents": candidate.get("delta_vs_target_cents"),
        "needed_repairs": candidate.get("needed_repairs"),
        "chosen_repairs": candidate.get("chosen_repairs"),
        "blockers": block,
        "live_ready": not block,
        "cases": candidate.get("cases"),
        "interpretation": [
            f"Frozen forward denominator is {denominator}; candidate has {summary.get('settled')} settled rows and net {summary.get('net_cents')}c.",
            f"Target net is {target_summary.get('net_cents')}c; candidate delta is {candidate.get('delta_vs_target_cents')}c.",
            f"Promotion blocked by: {', '.join(block) if block else 'none'}.",
            "This is a forward validator, not live order logic.",
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
    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Frozen Early-Boundary Wait Repair",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate: `{report.get('policy')}`",
        f"- Future denominator: `{report.get('future_denominator')}`",
        f"- Live ready: `{report.get('live_ready')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Summaries",
        "",
        "| surface | entries | settled | W/L | coverage | net c | avg c |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for label, key in [
        ("target", "target_summary"),
        ("danger_removed", "danger_summary"),
        ("wait_replacements", "replacement_summary"),
        ("repair_added", "repair_summary"),
        ("candidate", "candidate_summary"),
    ]:
        row = report.get(key) or {}
        lines.append(
            f"| {label} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    lines.extend([
        "",
        "## Danger Cases",
        "",
        "| market | target side | target won | target net | stc | abs d | recross | repl side | repl won | repl net | delay |",
        "|---|---|---|---:|---:|---:|---:|---|---|---:|---:|",
    ])
    for case in (report.get("cases") or [])[:30]:
        target = case.get("target") or {}
        repl = case.get("replacement") or {}
        lines.append(
            f"| {target.get('market')} | {target.get('side')} | {target.get('side_won')} | {fmt(target.get('net_cents'))} | "
            f"{fmt(target.get('seconds_to_close'))} | {fmt(target.get('abs_d_sigma'))} | {fmt(target.get('recross_hazard_score'))} | "
            f"{repl.get('side')} | {repl.get('side_won')} | {fmt(repl.get('net_cents'))} | {fmt(repl.get('replacement_delay_seconds'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
