"""Frozen-forward monitor for the FV bridge + geometry-exit stack.

Research-only; no live bot changes or orders.

This freezes the combined hypothesis:
lead FV bridge rows + side-geometry probability_reduce suppression on matched
actual v28 exits. Rows are counted only when their bridge timestamp is after the
freeze timestamp created by this script.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import probe_v28_fv_bridge_exit_geometry_stack as stack


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_fv_bridge_exit_geometry_stack_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_fv_bridge_exit_geometry_stack_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_fv_bridge_exit_geometry_stack_latest.md"

MIN_SETTLED = 30
MIN_COVERAGE = 75.0
MAX_COVERAGE = 90.0


def freeze_state() -> dict[str, Any]:
    state = stack.load_json(STATE_JSON)
    if state.get("freeze_ts_utc"):
        return state
    state = {
        "candidate": "lead_fv_bridge_plus_side_geometry_reduce_suppression",
        "freeze_ts_utc": datetime.now(timezone.utc).isoformat(),
        "fv_bridge": "first_eligible_top80_escape_energy+escape_edge6_or_p65_or_far_edge4+continuous_recross_forget",
        "exit_rule": "Suppress mushroom_v28_probability_reduce only when p_hold >= 0.75 and fair_drawdown sign agrees with held side.",
        "physics": "FV selects broad high-escape sides; exit rule avoids clipping still-valid theses when fair geometry agrees.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def filter_scenario_after_freeze(scenario: dict[str, Any], freeze_ts: datetime | None) -> dict[str, Any]:
    rows = scenario.get("rows")
    kept = []
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            ts = stack.parse_ts(row.get("ts_wall"))
            if freeze_ts is not None and (ts is None or ts <= freeze_ts):
                continue
            kept.append(row)
    filtered = dict(scenario)
    filtered["rows"] = kept
    filtered["entries"] = len(kept)
    return filtered


def add_blockers(summary: dict[str, Any]) -> dict[str, Any]:
    blockers = []
    settled = stack.as_float(summary.get("settled")) or 0.0
    coverage = stack.as_float(summary.get("coverage_pct"))
    net = stack.as_float(summary.get("stack_net_cents")) or 0.0
    matched = stack.as_float(summary.get("matched_rows")) or 0.0
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or coverage < MIN_COVERAGE:
        blockers.append("coverage_too_low")
    if coverage is not None and coverage > MAX_COVERAGE:
        blockers.append("coverage_too_high")
    if net <= 0.0:
        blockers.append("stack_net_not_positive")
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
        filtered_scenarios = []
        future_denominator = 0
        for scenario in window.get("scenarios") or []:
            if not isinstance(scenario, dict):
                continue
            filtered = filter_scenario_after_freeze(scenario, freeze_ts)
            filtered_scenarios.append(filtered)
            future_denominator = max(future_denominator, int(stack.as_float(filtered.get("entries")) or 0))
        scored_scenarios = []
        for filtered in filtered_scenarios:
            entries = int(stack.as_float(filtered.get("entries")) or 0)
            filtered = dict(filtered)
            filtered["coverage_pct"] = None if future_denominator <= 0 else (entries / future_denominator) * 100.0
            scored_scenarios.append(add_blockers(stack.score_scenario(filtered, exit_index)))
        windows.append({
            "window": window.get("window"),
            "source_freeze_ts_utc": window.get("freeze_ts_utc"),
            "future_denominator_after_stack_freeze": future_denominator,
            "scenarios": scored_scenarios,
        })
    approved_post = None
    for window in windows:
        if window.get("window") == "post_freeze_candidate":
            approved_post = next((s for s in window["scenarios"] if s.get("scenario") == "lead_approved_only"), None)
            break
    if approved_post is None and windows:
        approved_post = next((s for s in windows[-1]["scenarios"] if s.get("scenario") == "lead_approved_only"), None)
    interpretation = [
        f"Frozen stack timestamp is {state.get('freeze_ts_utc')}.",
        "Rows before that timestamp are excluded from promotion evidence.",
    ]
    if approved_post:
        interpretation.append(
            f"Approved-only future stack has {approved_post.get('settled')} settled rows, "
            f"coverage {approved_post.get('coverage_pct')}, stack net {approved_post.get('stack_net_cents')}c, "
            f"matched {approved_post.get('matched_rows')}, suppressed {approved_post.get('geometry_suppressed_rows')}."
        )
    return {
        "purpose": "Frozen-forward monitor for the lead FV bridge plus geometry-aware reduce-exit suppression.",
        "requirements": [
            "research-only, no live bot changes, no orders",
            "count only rows after stack freeze",
            "approved-only source rows remain separately visible",
            "candidate needs >=30 settled, 75-90% coverage, positive stack net, and enough matched exits",
        ],
        "freeze": state,
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
        "# v28 Frozen FV Bridge + Exit Geometry Stack",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- FV bridge: `{freeze.get('fv_bridge')}`",
        f"- Exit rule: `{freeze.get('exit_rule')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for window in report.get("windows") or []:
        lines.extend(["", f"## {window.get('window')}", ""])
        lines.append("| scenario | settled | coverage | dir W/L | realized c | stack c | hold c | matched | suppressed | ready | blockers |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|")
        for scenario in window.get("scenarios") or []:
            lines.append(
                f"| `{scenario.get('scenario')}` | {scenario.get('settled')} | "
                f"{fmt(scenario.get('coverage_pct'))} | "
                f"{scenario.get('directional_wins')}/{scenario.get('directional_losses')} | "
                f"{fmt(scenario.get('realized_net_cents'))} | {fmt(scenario.get('stack_net_cents'))} | "
                f"{fmt(scenario.get('hold_to_settlement_net_cents'))} | "
                f"{scenario.get('matched_rows')} | {scenario.get('geometry_suppressed_rows')} | "
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
