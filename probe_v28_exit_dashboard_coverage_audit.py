"""Audit whether active v28 exit/state watches are visible on the dashboard.

Research-only; no live bot changes or orders.

The candidate tracker intentionally contains more than the exit dashboard:
entry/exit stacks, old diagnostic rows, and active frozen exit watches all land
in one table. This audit keeps that distinction explicit so a real active exit
watch is not silently missing from the dashboard.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TRACKER_JSON = OUT_DIR / "v28_candidate_pnl_tracker_latest.json"
DASHBOARD_JSON = OUT_DIR / "v28_exit_policy_watch_dashboard_latest.json"
REGISTRY_JSON = OUT_DIR / "v28_candidate_registry_coverage_audit_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_dashboard_coverage_audit_latest.json"
OUT_MD = OUT_DIR / "v28_exit_dashboard_coverage_audit_latest.md"


DASHBOARD_GATE_MAP = {
    "exit_book_gap_suppression": "book_gap_suppression",
    "exit_book_gap_loss_guard": "book_gap_loss_guard",
    "exit_book_gap_loss_guard_v2": "book_gap_loss_guard_v2",
    "exit_book_gap_loss_guard_v3": "book_gap_loss_guard_v3",
    "exit_book_gap_value_only": "book_gap_value_only",
    "exit_value_reduce_depth_composite": "value_reduce_depth_composite",
    "exit_reduce_depth_gate": "reduce_depth_gate",
    "exit_reduce_loss_control_refinement": "reduce_loss_control_refinement",
    "exit_reduce_observable_loss_control": "reduce_observable_loss_control",
    "exit_reduce_geometry_suppression": "reduce_side_geometry",
    "exit_reduce_geometry_relaxed_watch": "reduce_geometry_relaxed",
    "exit_reduce_drift_guard": "exit_reduce_drift_guard",
    "exit_midband_reduce_rescue": "midband_reduce_rescue",
    "exit_clip_separator_watch": "exit_clip_separator_watch",
    "matched_unchanged_loss_guard_watch": "matched_unchanged_loss_guard_watch",
    "exit_shallow_drawdown": "exit_shallow_drawdown",
    "exit_shallow_duration_lte52": "exit_shallow_duration_lte52",
    "dual_exit_book_gap_else_reduce": "dual_exit_book_gap_else_reduce",
    "exit_common_clock_residual_child_watch": "common_clock_residual_child_exit70_79",
    "soft_frontier_midprice_delayed_recheck_exit": "soft_frontier_midprice_delayed_recheck_exit",
    "soft_frontier_midprice_delayed_recheck_rescue": "soft_frontier_midprice_delayed_recheck_rescue",
    "frozen_feature_gate_value_exit_watch": "feature_gate_value_exit",
    "feature_gate_exit_bid_suppression_watch": "feature_gate_exit_bid_suppression",
    "feature_gate_exit_bid_delayed_recheck": "feature_gate_exit_bid_delayed_recheck",
    "frozen_value_exit_feature_side_guard": "value_exit_feature_side_guard",
}


INTENTIONAL_EXCLUSIONS = {
    "exit_reduce_suppression": "legacy_blanket_reduce_watch_superseded_by_guarded_children",
    "exit_reduce_yes_suppression": "legacy_side_specific_reduce_watch_not_current_dashboard_child",
    "feature_gate_book_gap_exit_stack": "entry_exit_stack_tracked_in_candidate_table_not_exit_dashboard",
    "feature_gate_soft_frontier_exit_stack": "entry_exit_stack_tracked_in_candidate_table_not_exit_dashboard",
    "feature_gate_size_shrink_exit_overlay": "coverage_size_entry_overlay_tracked_with_feature_gate_family",
    "feature_gate_size_shrink_delayed_recheck_exit": "coverage_size_entry_overlay_tracked_with_feature_gate_family",
    "feature_gate_size_shrink_delayed_recheck_rescue": "coverage_size_entry_overlay_tracked_with_feature_gate_family",
    "soft_frontier_midprice_boundary_exit_stack": "entry_exit_stack_tracked_in_candidate_table_not_exit_dashboard",
    "soft_frontier_midprice_boundary_clip_exit_stack": "entry_exit_stack_tracked_in_candidate_table_not_exit_dashboard",
    "soft_frontier_midprice_boundary_dual_exit_stack": "entry_exit_stack_tracked_in_candidate_table_not_exit_dashboard",
    "soft_frontier_midprice_boundary_dual_exit_guard": "entry_exit_stack_tracked_in_candidate_table_not_exit_dashboard",
}


REVIEW_MISSING_HINTS = {
    "exit_book_gap_loss_guard_v3": "current_direction_mentions_v3_freeze_running",
    "exit_book_gap_value_only": "current_direction_evidence_tracks_value_only_strict_watch",
    "exit_value_reduce_depth_composite": "current_direction_evidence_tracks_value_reduce_depth_strict_watch",
    "exit_reduce_observable_loss_control": "current_direction_mentions_observable_loss_control_child_running",
    "exit_reduce_geometry_relaxed_watch": "current_direction_mentions_relaxed_geometry_freeze_running",
    "exit_midband_reduce_rescue": "current_direction_mentions_midband_or_shallow_loss_separator_family",
}


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


def is_exit_like_gate(gate: str) -> bool:
    return (
        gate.startswith("exit_")
        or gate.startswith("dual_exit_")
        or "exit_" in gate
        or gate in DASHBOARD_GATE_MAP
        or gate in INTENTIONAL_EXCLUSIONS
    )


def tracker_exit_gates(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    gates: dict[str, dict[str, Any]] = {}
    for row in payload.get("rows") or []:
        if not isinstance(row, dict):
            continue
        gate = str(row.get("gate") or "")
        if not gate or not is_exit_like_gate(gate):
            continue
        item = gates.setdefault(
            gate,
            {
                "gate": gate,
                "tracker_rows": 0,
                "policies": [],
                "post_birth_rows": 0,
                "diagnostic_rows": 0,
                "positive_rows": 0,
                "target_coverage_rows": 0,
                "live_ready_rows": 0,
                "max_settled": 0,
                "max_net_cents_after_entry_fee": None,
            },
        )
        item["tracker_rows"] += 1
        policy = str(row.get("policy") or "")
        if policy and len(item["policies"]) < 8:
            item["policies"].append(policy)
        if policy.startswith("post_") or "post_birth" in policy or "post_" in policy:
            item["post_birth_rows"] += 1
        if policy.startswith("diagnostic") or "prefreeze" in policy:
            item["diagnostic_rows"] += 1
        net = row.get("net_cents_after_entry_fee")
        if isinstance(net, (int, float)) and net > 0:
            item["positive_rows"] += 1
        if bool(row.get("target_coverage")):
            item["target_coverage_rows"] += 1
        if bool(row.get("live_ready")):
            item["live_ready_rows"] += 1
        settled = row.get("settled")
        if isinstance(settled, (int, float)):
            item["max_settled"] = max(int(settled), int(item["max_settled"]))
        if isinstance(net, (int, float)):
            current = item["max_net_cents_after_entry_fee"]
            item["max_net_cents_after_entry_fee"] = net if current is None else max(current, net)
    return gates


def dashboard_lanes(payload: dict[str, Any]) -> set[str]:
    lanes = set()
    for row in payload.get("rows") or []:
        if isinstance(row, dict) and row.get("lane"):
            lanes.add(str(row.get("lane")))
    return lanes


def registry_missing_count(payload: dict[str, Any]) -> int | None:
    value = payload.get("active_missing_rows")
    if isinstance(value, int):
        return value
    if isinstance(value, list):
        return len(value)
    return None


def classify_gate(gate: str, lanes: set[str]) -> tuple[str, str | None]:
    mapped_lane = DASHBOARD_GATE_MAP.get(gate)
    if mapped_lane:
        if mapped_lane in lanes:
            return "dashboard_covered", mapped_lane
        return "mapped_dashboard_lane_missing", mapped_lane
    reason = INTENTIONAL_EXCLUSIONS.get(gate)
    if reason:
        return f"intentionally_excluded:{reason}", None
    hint = REVIEW_MISSING_HINTS.get(gate)
    if hint:
        return f"missing_dashboard_review:{hint}", None
    return "unclassified_exit_like_tracker_gate", None


def build_report() -> dict[str, Any]:
    tracker = load_json(TRACKER_JSON)
    dashboard = load_json(DASHBOARD_JSON)
    registry = load_json(REGISTRY_JSON)
    lanes = dashboard_lanes(dashboard)
    gates = tracker_exit_gates(tracker)
    rows = []
    for gate, item in sorted(gates.items()):
        status, mapped_lane = classify_gate(gate, lanes)
        rows.append({
            **item,
            "dashboard_status": status,
            "dashboard_lane": mapped_lane,
        })

    counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("dashboard_status") or "")
        bucket = status.split(":", 1)[0]
        counts[bucket] = counts.get(bucket, 0) + 1

    missing_review = [
        row for row in rows
        if str(row.get("dashboard_status") or "").startswith("missing_dashboard_review")
        or row.get("dashboard_status") == "mapped_dashboard_lane_missing"
        or row.get("dashboard_status") == "unclassified_exit_like_tracker_gate"
    ]
    covered = [row for row in rows if row.get("dashboard_status") == "dashboard_covered"]
    excluded = [row for row in rows if str(row.get("dashboard_status") or "").startswith("intentionally_excluded")]
    stale_lanes = sorted(lane for lane in lanes if lane not in set(DASHBOARD_GATE_MAP.values()) and not lane.startswith("common_clock_strict_forward"))
    report = {
        "generated_at_utc": utc_now_iso(),
        "tracker_source": str(TRACKER_JSON),
        "dashboard_source": str(DASHBOARD_JSON),
        "registry_source": str(REGISTRY_JSON),
        "registry_active_missing_rows": registry_missing_count(registry),
        "tracker_exit_like_gates": len(rows),
        "dashboard_lanes": len(lanes),
        "dashboard_status_counts": dict(sorted(counts.items())),
        "covered_gates": [row["gate"] for row in covered],
        "intentionally_excluded_gates": [
            {"gate": row["gate"], "reason": str(row["dashboard_status"]).split(":", 1)[1]}
            for row in excluded
        ],
        "missing_dashboard_review_gates": [
            {
                "gate": row["gate"],
                "status": row["dashboard_status"],
                "tracker_rows": row["tracker_rows"],
                "post_birth_rows": row["post_birth_rows"],
                "max_settled": row["max_settled"],
                "max_net_cents_after_entry_fee": row["max_net_cents_after_entry_fee"],
                "sample_policies": row["policies"],
            }
            for row in missing_review
        ],
        "dashboard_lanes_without_gate_map": stale_lanes,
        "rows": rows,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    missing = report.get("missing_dashboard_review_gates") or []
    notes = [
        "Research-only dashboard coverage audit; it checks reporting visibility, not candidate quality.",
        f"Tracker has {report.get('tracker_exit_like_gates')} exit-like gates; dashboard has {report.get('dashboard_lanes')} lanes.",
        f"Dashboard status counts: {report.get('dashboard_status_counts')}.",
        f"Registry active missing rows: {report.get('registry_active_missing_rows')}.",
    ]
    if missing:
        notes.append(
            "Exit/state gates needing dashboard review: "
            + str([row.get("gate") for row in missing])
            + "."
        )
    else:
        notes.append("No active exit/state tracker gate is missing dashboard coverage or an explicit exclusion.")
    return notes


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    if value is None:
        return "n/a"
    return str(value)


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Dashboard Coverage Audit",
        "",
        "Research-only reporting coverage audit. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Tracker exit-like gates: `{report.get('tracker_exit_like_gates')}`",
        f"- Dashboard lanes: `{report.get('dashboard_lanes')}`",
        f"- Dashboard status counts: `{report.get('dashboard_status_counts')}`",
        f"- Registry active missing rows: `{report.get('registry_active_missing_rows')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Gates Needing Dashboard Review",
        "",
        "| gate | status | rows | post rows | max settled | max net c | sample policies |",
        "|---|---|---:|---:|---:|---:|---|",
    ])
    for row in report.get("missing_dashboard_review_gates") or []:
        lines.append(
            f"| `{row.get('gate')}` | `{row.get('status')}` | {row.get('tracker_rows')} | "
            f"{row.get('post_birth_rows')} | {row.get('max_settled')} | "
            f"{fmt(row.get('max_net_cents_after_entry_fee'))} | "
            f"{'; '.join(row.get('sample_policies') or [])} |"
        )
    if not report.get("missing_dashboard_review_gates"):
        lines.append("| none | n/a | 0 | 0 | 0 | n/a | n/a |")
    lines.extend([
        "",
        "## Covered Gates",
        "",
    ])
    lines.extend(f"- `{gate}`" for gate in report.get("covered_gates") or [])
    lines.extend([
        "",
        "## Intentional Exclusions",
        "",
    ])
    for row in report.get("intentionally_excluded_gates") or []:
        lines.append(f"- `{row.get('gate')}`: {row.get('reason')}")
    lines.extend([
        "",
        "## Dashboard Lanes Without Gate Map",
        "",
    ])
    if report.get("dashboard_lanes_without_gate_map"):
        lines.extend(f"- `{lane}`" for lane in report.get("dashboard_lanes_without_gate_map") or [])
    else:
        lines.append("- none")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
