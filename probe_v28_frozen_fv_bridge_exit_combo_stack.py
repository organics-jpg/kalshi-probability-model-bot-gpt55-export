"""Frozen-forward monitor for FV bridge + reduce/collapse exit combo.

Research-only; no live bot changes or orders.

Freeze the strongest simple combo from the diagnostic bakeoff:
lead FV bridge + reduce-geometry suppression + collapse suppression when
fair drawdown at exit is <= 12c.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import probe_v28_fv_bridge_exit_combo_bakeoff as combo
import probe_v28_fv_bridge_exit_geometry_stack as stack


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_fv_bridge_exit_combo_stack_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_fv_bridge_exit_combo_stack_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_fv_bridge_exit_combo_stack_latest.md"

MIN_SETTLED = 30
MIN_COVERAGE = 75.0
MAX_COVERAGE = 90.0
POLICY_NAME = "reduce_geometry_plus_collapse_drawdown_lte_12"
POLICY_RULES = [combo.reduce_geometry, combo.collapse_drawdown_lte(12.0)]


def freeze_state() -> dict[str, Any]:
    state = stack.load_json(STATE_JSON)
    if state.get("freeze_ts_utc"):
        return state
    state = {
        "candidate": "lead_fv_bridge_plus_reduce_geometry_plus_collapse_drawdown_lte_12",
        "freeze_ts_utc": datetime.now(timezone.utc).isoformat(),
        "fv_bridge": "first_eligible_top80_escape_energy+escape_edge6_or_p65_or_far_edge4+continuous_recross_forget",
        "exit_rules": [
            "Suppress mushroom_v28_probability_reduce when p_hold >= 0.75 and fair_drawdown sign agrees with held side.",
            "Suppress mushroom_v28_probability_collapse_full when fair_drawdown_cents <= 12.",
        ],
        "physics": "Recover still-valid high-conviction theses clipped by reduce exits, and avoid full-collapse exits when drawdown is shallow enough to look like turbulence.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def filter_after_freeze(scenario: dict[str, Any], freeze_ts: Any) -> dict[str, Any]:
    rows = scenario.get("rows")
    kept = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        ts = stack.parse_ts(row.get("ts_wall"))
        if freeze_ts is not None and (ts is None or ts <= freeze_ts):
            continue
        kept.append(row)
    out = dict(scenario)
    out["rows"] = kept
    out["entries"] = len(kept)
    return out


def add_blockers(summary: dict[str, Any]) -> dict[str, Any]:
    settled = stack.as_float(summary.get("settled")) or 0.0
    coverage = stack.as_float(summary.get("coverage_pct"))
    net = stack.as_float(summary.get("candidate_net_cents")) or 0.0
    matched = stack.as_float(summary.get("matched_rows")) or 0.0
    blockers = []
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or coverage < MIN_COVERAGE:
        blockers.append("coverage_too_low")
    if coverage is not None and coverage > MAX_COVERAGE:
        blockers.append("coverage_too_high")
    if net <= 0.0:
        blockers.append("candidate_net_not_positive")
    if settled > 0 and matched / settled < 0.70:
        blockers.append("matched_exit_share_lt_70pct")
    out = dict(summary)
    out["blockers"] = blockers
    out["candidate_ready"] = not blockers
    return out


def build_report() -> dict[str, Any]:
    state = freeze_state()
    freeze_ts = stack.parse_ts(state.get("freeze_ts_utc"))
    bridge_payload = stack.load_json(stack.BRIDGE_SOURCE_JSON)
    exit_payload = stack.load_json(stack.EXIT_ROWS_JSON)
    exit_index = stack.indexed_exit_rows(exit_payload)
    windows = []
    for window in stack.bridge_windows(bridge_payload):
        filtered = []
        denominator = 0
        for scenario in window.get("scenarios") or []:
            if not isinstance(scenario, dict):
                continue
            scenario_after = filter_after_freeze(scenario, freeze_ts)
            filtered.append(scenario_after)
            denominator = max(denominator, int(stack.as_float(scenario_after.get("entries")) or 0))
        scenarios = []
        for scenario_after in filtered:
            entries = int(stack.as_float(scenario_after.get("entries")) or 0)
            scenario_after = dict(scenario_after)
            scenario_after["coverage_pct"] = None if denominator <= 0 else (entries / denominator) * 100.0
            scored = combo.score_scenario(scenario_after, exit_index, POLICY_NAME, POLICY_RULES)
            scenarios.append(add_blockers(scored))
        windows.append({
            "window": window.get("window"),
            "source_freeze_ts_utc": window.get("freeze_ts_utc"),
            "future_denominator_after_combo_freeze": denominator,
            "scenarios": scenarios,
        })
    approved = None
    for window in windows:
        if window.get("window") == "post_freeze_candidate":
            approved = next((s for s in window.get("scenarios", []) if s.get("scenario") == "lead_approved_only"), None)
            break
    interpretation = [
        f"Frozen combo timestamp is {state.get('freeze_ts_utc')}.",
        "Rows before that timestamp are excluded from promotion evidence.",
    ]
    if approved:
        interpretation.append(
            f"Approved-only future combo has {approved.get('settled')} settled rows, "
            f"coverage {approved.get('coverage_pct')}, candidate net {approved.get('candidate_net_cents')}c, "
            f"matched exits {approved.get('matched_rows')}, suppressed exits {approved.get('suppressed_rows')}."
        )
    return {
        "purpose": "Frozen-forward monitor for FV bridge plus reduce/collapse exit combo.",
        "requirements": [
            "research-only, no live bot changes, no orders",
            "count only rows after combo freeze",
            "approved-only source rows remain separately visible",
            "candidate needs >=30 settled, 75-90% coverage, positive net, and enough matched exits",
        ],
        "freeze": state,
        "policy": POLICY_NAME,
        "interpretation": interpretation,
        "windows": windows,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Frozen FV Bridge Exit Combo Stack",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- FV bridge: `{freeze.get('fv_bridge')}`",
        f"- Policy: `{report.get('policy')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for window in report.get("windows") or []:
        lines.extend(["", f"## {window.get('window')}", ""])
        lines.append("| scenario | settled | coverage | dir W/L | current c | candidate c | hold c | matched | suppressed | ready | blockers |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|")
        for scenario in window.get("scenarios") or []:
            lines.append(
                f"| `{scenario.get('scenario')}` | {scenario.get('settled')} | "
                f"{fmt(scenario.get('coverage_pct'))} | "
                f"{scenario.get('directional_wins')}/{scenario.get('directional_losses')} | "
                f"{fmt(scenario.get('realized_net_cents'))} | {fmt(scenario.get('candidate_net_cents'))} | "
                f"{fmt(scenario.get('hold_to_settlement_net_cents'))} | "
                f"{scenario.get('matched_rows')} | {scenario.get('suppressed_rows')} | "
                f"{scenario.get('candidate_ready')} | {', '.join(scenario.get('blockers') or []) or 'none'} |"
            )
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
