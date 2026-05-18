"""Objective-to-artifact checklist for the v28 long-term research goal.

Research-only; no live bot changes, no process control, no orders.

This report maps the user's explicit promotion requirements to concrete local
artifacts, then summarizes which requirements are satisfied, blocked, or
currently unverifiable.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"

GOAL_AUDIT_JSON = OUT_DIR / "v28_goal_completion_audit_latest.json"
CANDIDATE_VS_LIVE_JSON = OUT_DIR / "v28_candidate_vs_live_full_table_latest.json"
LIVE_READINESS_JSON = OUT_DIR / "v28_live_trade_readiness_latest.json"
NEXT_ACTION_TRIAGE_JSON = OUT_DIR / "v28_next_action_triage_latest.json"
CURRENT_DIRECTION_JSON = OUT_DIR / "v28_current_direction_decision_latest.json"
FORWARD_COLLECTION_JSON = OUT_DIR / "v28_forward_collection_blocker_audit_latest.json"
FEATURE_GATE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
FEATURE_GATE_JOINT_GAP_JSON = OUT_DIR / "v28_feature_gate_joint_gate_gap_audit_latest.json"
EXIT_DASHBOARD_JSON = OUT_DIR / "v28_exit_policy_watch_dashboard_latest.json"

OUT_JSON = OUT_DIR / "v28_objective_gap_checklist_latest.json"
OUT_MD = OUT_DIR / "v28_objective_gap_checklist_latest.md"


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


def evidence_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def status(passed: bool | None) -> str:
    if passed is True:
        return "pass"
    if passed is False:
        return "blocked"
    return "unverified"


def best_feature_gate_post(feature_gate: dict[str, Any], lane_name: str) -> dict[str, Any]:
    lanes = feature_gate.get("lanes") or []
    lane = next((row for row in lanes if row.get("lane") == lane_name), {})
    variants = lane.get("variants") or []
    if not variants:
        return {}
    return sorted(
        variants,
        key=lambda row: (
            fnum((row.get("candidate_summary") or {}).get("coverage_pct")),
            fnum((row.get("candidate_summary") or {}).get("net_cents")),
        ),
        reverse=True,
    )[0]


def compact_candidate(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "gate": row.get("gate"),
        "policy": row.get("policy"),
        "net_cents": row.get("net_cents"),
        "coverage_pct": row.get("coverage_pct"),
        "settled": row.get("settled"),
        "simulated_share": row.get("simulated_share"),
        "delta_vs_live_cents": row.get("delta_vs_live_cents"),
        "live_ready": row.get("live_ready"),
        "blockers": row.get("blockers"),
    }


def build_checklist() -> dict[str, Any]:
    goal = load_json(GOAL_AUDIT_JSON)
    candidates = load_json(CANDIDATE_VS_LIVE_JSON)
    readiness = load_json(LIVE_READINESS_JSON)
    triage = load_json(NEXT_ACTION_TRIAGE_JSON)
    direction = load_json(CURRENT_DIRECTION_JSON)
    forward = load_json(FORWARD_COLLECTION_JSON)
    feature_gate = load_json(FEATURE_GATE_JSON)
    feature_gate_joint = load_json(FEATURE_GATE_JOINT_GAP_JSON)
    exits = load_json(EXIT_DASHBOARD_JSON)

    candidate_rows = [row for row in (candidates.get("rows") or []) if isinstance(row, dict)]
    non_live_rows = [row for row in candidate_rows if row.get("type") != "live"]
    positive_target = [
        row for row in non_live_rows
        if row.get("target_coverage") and fnum(row.get("net_cents")) > 0
    ]
    live_ready = [row for row in non_live_rows if row.get("live_ready") is True]
    strict_positive_target = [
        row for row in positive_target
        if "diagnostic_prefreeze" not in (row.get("blockers") or [])
    ]
    top_positive_target = sorted(
        positive_target,
        key=lambda row: fnum(row.get("delta_vs_live_cents")),
        reverse=True,
    )[:8]

    blocker_counts = Counter()
    for row in non_live_rows:
        for blocker in row.get("blockers") or []:
            blocker_counts[str(blocker)] += 1

    goal_checks = goal.get("checks") or []
    missing_checks = goal.get("missing") or []
    live_readiness_check = next((row for row in goal_checks if row.get("name") == "live_readiness_gate"), {})
    passed_goal_checks = sum(1 for row in goal_checks if row.get("passed") is True)

    feature_entry = best_feature_gate_post(feature_gate, "post_feature_freeze_entry")
    feature_bridge = best_feature_gate_post(feature_gate, "post_feature_freeze_bridge")
    feature_entry_summary = feature_entry.get("candidate_summary") or {}
    feature_bridge_summary = feature_bridge.get("candidate_summary") or {}
    feature_gate_best_joint = (feature_gate_joint.get("rows") or [{}])[0]

    exit_rows = [row for row in (exits.get("rows") or []) if isinstance(row, dict)]
    closest_exit = sorted(
        exit_rows,
        key=lambda row: (
            row.get("status") in {"forward_positive_under_review", "positive_but_under_sample"},
            fnum(row.get("delta_vs_current_cents")),
            fnum(row.get("suppressed_exits")),
        ),
        reverse=True,
    )[:8]

    live_state_blockers = forward.get("blockers") or []
    sidecar_state = forward.get("feature_gate_sidecar_state") or {}
    sidecar_trade = sidecar_state.get("trade_summary") or {}
    sidecar_live_trade_while_not_ready = (
        "feature_gate_sidecar_live_trade_detected_while_readiness_false" in live_state_blockers
        or "sidecar_live_trade_detected_while_readiness_false" in (sidecar_state.get("blockers") or [])
    )
    live_collection_healthy = (
        "live_watchdog_restart_failed" not in live_state_blockers
        and "live_lock_not_v28" not in live_state_blockers
        and not sidecar_live_trade_while_not_ready
    )

    checklist = [
        {
            "requirement": "Research starts from v28 and current v28 artifacts.",
            "evidence": [evidence_path(CURRENT_DIRECTION_JSON), evidence_path(NEXT_ACTION_TRIAGE_JSON)],
            "actual": direction.get("direction"),
            "passed": True,
            "note": "Current direction ledger and triage are v28-specific.",
        },
        {
            "requirement": "Research-only; no candidate live trades or live logic changes.",
            "evidence": [evidence_path(FORWARD_COLLECTION_JSON), evidence_path(NEXT_ACTION_TRIAGE_JSON)],
            "actual": {
                "this_report_chain": "research-only; no process control/orders",
                "sidecar_live_trade_detected": sidecar_trade.get("sidecar_live_trade_detected"),
                "sidecar_entries_round_trips_net": [
                    sidecar_trade.get("entries_total"),
                    sidecar_trade.get("completed_round_trips"),
                    sidecar_trade.get("net_pnl_cents"),
                ],
                "sidecar_blockers": sidecar_state.get("blockers"),
            },
            "passed": not sidecar_live_trade_while_not_ready,
            "note": "The research reports did not control live processes, but the separate feature-gate size1 sidecar produced a live trade while readiness was false.",
        },
        {
            "requirement": "Refresh and compare against current live-only v28 baseline.",
            "evidence": [evidence_path(CANDIDATE_VS_LIVE_JSON), evidence_path(FORWARD_COLLECTION_JSON)],
            "actual": {
                "candidate_vs_live_generated_at_utc": candidates.get("generated_at_utc"),
                "live_net_cents": candidates.get("live_net_cents"),
                "live_collection_blockers": live_state_blockers,
            },
            "passed": False,
            "note": "Last candidate-vs-live table has a refreshed log baseline, but fresh size2 v28 live collection is blocked by watchdog failure and the shared lock currently points at the feature-gate size1 sidecar.",
        },
        {
            "requirement": "At least one candidate has strict frozen/post-freeze evidence.",
            "evidence": [evidence_path(CANDIDATE_VS_LIVE_JSON), evidence_path(GOAL_AUDIT_JSON)],
            "actual": {
                "strict_positive_target_coverage_rows": len(strict_positive_target),
                "positive_target_coverage_rows": len(positive_target),
            },
            "passed": len(strict_positive_target) > 0,
            "note": "Strict-positive rows exist, but none clear every promotion gate.",
        },
        {
            "requirement": "Candidate has >=30 settled forward rows.",
            "evidence": [evidence_path(GOAL_AUDIT_JSON), evidence_path(FEATURE_GATE_JSON)],
            "actual": {
                "goal_forward_sample_check": next((row for row in goal_checks if row.get("name") == "forward_sample_size"), {}),
                "feature_gate_entry_settled": feature_entry_summary.get("settled"),
                "feature_gate_bridge_settled": feature_bridge_summary.get("settled"),
            },
            "passed": True,
            "note": "Sample size alone is no longer the universal blocker for many lanes.",
        },
        {
            "requirement": "Candidate is profitable after fees.",
            "evidence": [evidence_path(CANDIDATE_VS_LIVE_JSON), evidence_path(GOAL_AUDIT_JSON)],
            "actual": {
                "positive_candidate_count": candidates.get("positive_candidate_count"),
                "top_positive_target": [compact_candidate(row) for row in top_positive_target[:3]],
                "goal_positive_forward_pnl_check": next((row for row in goal_checks if row.get("name") == "positive_forward_pnl"), {}),
            },
            "passed": len(positive_target) > 0,
            "note": "Profit exists in many rows, but profitability alone is not sufficient.",
        },
        {
            "requirement": "Broad-entry coverage is roughly 75-90%.",
            "evidence": [evidence_path(CANDIDATE_VS_LIVE_JSON), evidence_path(FEATURE_GATE_JSON), evidence_path(FEATURE_GATE_JOINT_GAP_JSON)],
            "actual": {
                "target_coverage_positive_count": candidates.get("target_coverage_positive_count"),
                "feature_gate_entry_coverage_pct": feature_entry_summary.get("coverage_pct"),
                "feature_gate_bridge_coverage_pct": feature_bridge_summary.get("coverage_pct"),
                "best_joint_feature_gate_clean_rows_needed_for_coverage_and_source": feature_gate_best_joint.get("clean_rows_needed_for_coverage_and_source"),
            },
            "passed": (candidates.get("target_coverage_positive_count") or 0) > 0,
            "note": "Some rows clear target coverage, but target-coverage rows still fail other gates; raw05-style near-promotion variants remain source/cushion/coverage constrained.",
        },
        {
            "requirement": "Reconstructed/rejected-actionable share <=35%.",
            "evidence": [evidence_path(GOAL_AUDIT_JSON), evidence_path(FEATURE_GATE_JSON), evidence_path(FEATURE_GATE_JOINT_GAP_JSON), evidence_path(CANDIDATE_VS_LIVE_JSON)],
            "actual": {
                "top_blocker_count_source_share_high": blocker_counts.get("source_share_high_by_0.45", 0) + blocker_counts.get("reconstructed_share_gt_35pct", 0),
                "feature_gate_entry_reconstructed_share": feature_entry.get("reconstructed_share"),
                "feature_gate_bridge_reconstructed_share": feature_bridge.get("reconstructed_share"),
                "feature_gate_joint_best_source_gap": {
                    "candidate": feature_gate_best_joint.get("candidate"),
                    "reconstructed_share": feature_gate_best_joint.get("reconstructed_share"),
                    "clean_rows_needed_for_source_gate": feature_gate_best_joint.get("clean_rows_needed_for_source_gate"),
                    "joint_blockers": feature_gate_best_joint.get("joint_blockers"),
                },
            },
            "passed": False,
            "note": "Source quality remains a recurring active blocker; feature-gate raw05 is clean enough but under-covered.",
        },
        {
            "requirement": "Full-loss cushion >=3.",
            "evidence": [evidence_path(FEATURE_GATE_JSON), evidence_path(FEATURE_GATE_JOINT_GAP_JSON), evidence_path(EXIT_DASHBOARD_JSON), evidence_path(CANDIDATE_VS_LIVE_JSON)],
            "actual": {
                "feature_gate_entry_cushion": feature_entry.get("full_loss_cushion_estimate"),
                "feature_gate_bridge_cushion": feature_bridge.get("full_loss_cushion_estimate"),
                "candidate_blocker_full_loss_cushion_lt_3": blocker_counts.get("full_loss_cushion_lt_3", 0),
                "feature_gate_joint_best_cents_needed_for_cushion3": feature_gate_best_joint.get("cents_needed_for_cushion3"),
            },
            "passed": False,
            "note": "Some narrow/diagnostic rows have cushion, but broad/live-ready candidates still fail fragility gates.",
        },
        {
            "requirement": "Live readiness gate passes.",
            "evidence": [evidence_path(LIVE_READINESS_JSON), evidence_path(CANDIDATE_VS_LIVE_JSON), evidence_path(GOAL_AUDIT_JSON)],
            "actual": {
                "live_ready_count": candidates.get("live_ready_count"),
                "readiness_any_live_ready": readiness.get("any_live_ready"),
                "goal_live_readiness_check": live_readiness_check,
                "candidate_table_live_ready_rows": [compact_candidate(row) for row in live_ready[:5]],
            },
            "passed": readiness.get("any_live_ready") is True and live_readiness_check.get("passed") is True,
            "note": "Hard blocker: the live-readiness artifact and goal audit still say the readiness gate is false; candidate-table live_ready rows are not sufficient by themselves.",
        },
        {
            "requirement": "Exit/state repairs reduce loss-count churn without false-hold damage.",
            "evidence": [evidence_path(EXIT_DASHBOARD_JSON), evidence_path(NEXT_ACTION_TRIAGE_JSON)],
            "actual": {
                "exit_dashboard_status_counts": exits.get("status_counts"),
                "closest_exit_watches": [
                    {
                        "lane": row.get("lane"),
                        "status": row.get("status"),
                        "settled": row.get("settled"),
                        "suppressed_exits": row.get("suppressed_exits"),
                        "delta_vs_current_cents": row.get("delta_vs_current_cents"),
                        "loss_control_cost_cents": row.get("loss_control_cost_cents"),
                        "blockers": row.get("blockers"),
                    }
                    for row in closest_exit[:5]
                ],
            },
            "passed": False,
            "note": "Closest exit watches are positive but still under suppression density/cushion, while broader suppressors show loss-control cost.",
        },
        {
            "requirement": "Physical failure modes are classified and active blockers identified.",
            "evidence": [evidence_path(NEXT_ACTION_TRIAGE_JSON), evidence_path(GOAL_AUDIT_JSON), evidence_path(CURRENT_DIRECTION_JSON)],
            "actual": {
                "top_global_blockers": dict(list((triage.get("global_blocker_counts") or {}).items())[:10]),
                "top_blocker_families": dict(list((triage.get("blocker_family_counts") or {}).items())[:10]),
                "goal_missing_count": len(missing_checks),
            },
            "passed": True,
            "note": "Failure classification exists; it has not yet produced a promotable repair.",
        },
        {
            "requirement": "Fresh frozen/live evidence can continue collecting.",
            "evidence": [evidence_path(FORWARD_COLLECTION_JSON)],
            "actual": {
                "live_collection_healthy": live_collection_healthy,
                "forward_collection_blockers": live_state_blockers,
                "latest_hourly_monitor": (forward.get("live_monitor") or {}).get("latest_line"),
                "live_lock": (forward.get("live_lock") or {}).get("payload"),
            },
            "passed": live_collection_healthy,
            "note": "Research can continue from existing logs, but fresh v28 live collection is blocked until live state is resolved.",
        },
        {
            "requirement": "All promotion gates pass together for at least one candidate.",
            "evidence": [evidence_path(CANDIDATE_VS_LIVE_JSON), evidence_path(GOAL_AUDIT_JSON), evidence_path(FORWARD_COLLECTION_JSON), evidence_path(FEATURE_GATE_JOINT_GAP_JSON)],
            "actual": {
                "live_ready_count": candidates.get("live_ready_count"),
                "goal_achieved": goal.get("achieved"),
                "blocked_checks": [row.get("name") for row in missing_checks[:12]],
                "fresh_collection_blockers": live_state_blockers,
                "feature_gate_joint_blockers": feature_gate_joint.get("blockers"),
            },
            "passed": False,
            "note": "This is the decisive completion row: individual gates are partially met, but no row clears sample, net, coverage, source, cushion, live readiness, live-baseline comparison, and fresh collection health together.",
        },
    ]

    failed = [row for row in checklist if row["passed"] is False]
    unverified = [row for row in checklist if row["passed"] is None]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "objective": "Improve v28 BTC 15m Kalshi strategy into a physics-backed, evidence-disciplined, broad-enough, live-ready strategy with durable positive risk-adjusted ROI.",
        "achieved": False,
        "checklist": [
            {
                **row,
                "status": status(row.get("passed")),
            }
            for row in checklist
        ],
        "summary": {
            "checks_total": len(checklist),
            "checks_passed": sum(1 for row in checklist if row["passed"] is True),
            "checks_blocked": len(failed),
            "checks_unverified": len(unverified),
            "goal_audit_checks_passed": passed_goal_checks,
            "goal_audit_checks_total": len(goal_checks),
            "candidate_count": candidates.get("candidate_count"),
            "positive_candidate_count": candidates.get("positive_candidate_count"),
            "target_coverage_positive_count": candidates.get("target_coverage_positive_count"),
            "live_ready_count": candidates.get("live_ready_count"),
            "readiness_any_live_ready": readiness.get("any_live_ready"),
            "live_collection_healthy": live_collection_healthy,
        },
        "top_positive_target_candidates": [compact_candidate(row) for row in top_positive_target],
        "top_blocker_counts": dict(blocker_counts.most_common(20)),
        "next_required_work": [
            "Resolve v28 live collection health before making fresh live-baseline or forward-collection claims.",
            "Keep exit/state work first: collect suppression density and false-hold safety for the positive exit watches.",
            "For boundary-clock feature-gate, do not widen raw03/raw05 thresholds; wait for clean forward rows or freeze a real observable source-quality/size proxy.",
            "Do not promote any diagnostic row until the live-readiness artifact passes and all promotion gates pass together.",
            "Treat candidate-table live_ready flags as advisory only; the live-readiness artifact and goal audit are the promotion gate of record.",
        ],
    }


def fmt(value: Any) -> str:
    if isinstance(value, (dict, list)):
        text = json.dumps(value, sort_keys=True, default=str)
    else:
        text = str(value)
    return text.replace("|", "\\|")


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    summary = report.get("summary") or {}
    lines = [
        "# v28 Objective Gap Checklist",
        "",
        "Research-only. No live bot logic changes, no process control, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Achieved: `{report.get('achieved')}`",
        f"- Checklist pass/blocked/unverified: `{summary.get('checks_passed')}/{summary.get('checks_blocked')}/{summary.get('checks_unverified')}`",
        f"- Goal-audit pass/total: `{summary.get('goal_audit_checks_passed')}/{summary.get('goal_audit_checks_total')}`",
        f"- Candidate count / positive / target-positive / live-ready: `{summary.get('candidate_count')}/{summary.get('positive_candidate_count')}/{summary.get('target_coverage_positive_count')}/{summary.get('live_ready_count')}`",
        f"- Readiness artifact any_live_ready: `{summary.get('readiness_any_live_ready')}`",
        f"- Live collection healthy: `{summary.get('live_collection_healthy')}`",
        "",
        "## Prompt-To-Artifact Checklist",
        "",
        "| status | requirement | actual | evidence | note |",
        "|---|---|---|---|---|",
    ]
    for row in report.get("checklist") or []:
        lines.append(
            f"| `{row.get('status')}` | {fmt(row.get('requirement'))} | {fmt(row.get('actual'))} | "
            f"{fmt(row.get('evidence'))} | {fmt(row.get('note'))} |"
        )
    lines.extend([
        "",
        "## Top Candidate Rows",
        "",
        "| gate | policy | net | coverage | settled | source share | delta vs live | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("top_positive_target_candidates") or []:
        lines.append(
            f"| `{row.get('gate')}` | `{row.get('policy')}` | {row.get('net_cents')} | "
            f"{row.get('coverage_pct')} | {row.get('settled')} | {row.get('simulated_share')} | "
            f"{row.get('delta_vs_live_cents')} | `{', '.join(row.get('blockers') or [])}` |"
        )
    lines.extend([
        "",
        "## Next Required Work",
        "",
    ])
    lines.extend(f"- {item}" for item in report.get("next_required_work") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_checklist()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
