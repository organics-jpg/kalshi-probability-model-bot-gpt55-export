"""Next-action triage for the active v28 improvement goal.

Research-only; no live bot changes or orders.

This artifact does not invent a candidate. It compresses the current frozen
evidence into the smallest set of honest next actions so iteration follows the
physics and blocker evidence instead of whichever report is loudest.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
READINESS_JSON = OUT_DIR / "v28_live_trade_readiness_latest.json"
TRACKER_JSON = OUT_DIR / "v28_candidate_pnl_tracker_latest.json"
LEADERBOARD_JSON = OUT_DIR / "v28_frozen_candidate_leaderboard_latest.json"
DECISION_MATRIX_JSON = OUT_DIR / "v28_fv_candidate_decision_matrix_latest.json"
GOAL_AUDIT_JSON = OUT_DIR / "v28_goal_completion_audit_latest.json"
EXIT_REDUCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
EXIT_REDUCE_DRIFT_AUDIT_JSON = OUT_DIR / "v28_exit_reduce_suppression_drift_audit_latest.json"
EXIT_REDUCE_DRIFT_GUARD_WATCH_JSON = OUT_DIR / "v28_frozen_exit_reduce_drift_guard_watch_latest.json"
EXIT_REDUCE_RUNWAY_JSON = OUT_DIR / "v28_exit_reduce_promotion_runway_latest.json"
EXIT_REDUCE_ACTIONABILITY_JSON = OUT_DIR / "v28_exit_reduce_loss_control_actionability_latest.json"
EXIT_REDUCE_GEOMETRY_OPPORTUNITY_JSON = OUT_DIR / "v28_exit_reduce_geometry_opportunity_latest.json"
EXIT_REDUCE_GEOMETRY_RELAXED_WATCH_JSON = OUT_DIR / "v28_frozen_exit_reduce_geometry_relaxed_watch_latest.json"
EXIT_BOOK_GAP_JSON = OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json"
EXIT_BOOK_GAP_LOSS_GUARD_JSON = OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_latest.json"
EXIT_BOOK_GAP_LOSS_GUARD_V2_JSON = OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v2_latest.json"
EXIT_BOOK_GAP_LOSS_GUARD_V3_JSON = OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v3_latest.json"
EXIT_BOOK_GAP_VALUE_ONLY_JSON = OUT_DIR / "v28_frozen_exit_book_gap_value_only_latest.json"
EXIT_BOOK_GAP_VALUE_ONLY_OPPORTUNITY_JSON = OUT_DIR / "v28_exit_book_gap_value_only_opportunity_latest.json"
EXIT_VALUE_REDUCE_DEPTH_COMPOSITE_JSON = OUT_DIR / "v28_frozen_exit_value_reduce_depth_composite_latest.json"
EXIT_VALUE_REDUCE_DEPTH_OPPORTUNITY_JSON = OUT_DIR / "v28_exit_value_reduce_depth_opportunity_latest.json"
EXIT_REDUCE_OBSERVABLE_LOSS_CONTROL_JSON = OUT_DIR / "v28_frozen_exit_reduce_observable_loss_control_watch_latest.json"
EXIT_REDUCE_OBSERVABLE_LOSS_CONTROL_OPPORTUNITY_JSON = OUT_DIR / "v28_exit_reduce_observable_loss_control_opportunity_latest.json"
EXIT_REDUCE_OBSERVABLE_FALSE_HOLD_AUTOPSY_JSON = OUT_DIR / "v28_exit_reduce_observable_false_hold_autopsy_latest.json"
EXIT_MIDBAND_REDUCE_RESCUE_JSON = OUT_DIR / "v28_frozen_exit_midband_reduce_rescue_watch_latest.json"
EXIT_BOOK_GAP_LOSS_GUARD_V2_OPPORTUNITY_JSON = OUT_DIR / "v28_exit_book_gap_loss_guard_v2_opportunity_latest.json"
EXIT_BOOK_GAP_LOSS_GUARD_V3_OPPORTUNITY_JSON = OUT_DIR / "v28_exit_book_gap_loss_guard_v3_opportunity_latest.json"
EXIT_LOSS_GUARD_V1_V2_V3_CONTRAST_JSON = OUT_DIR / "v28_exit_loss_guard_v1_v2_v3_contrast_latest.json"
EXIT_LOSS_GUARD_V3_RESIDUAL_SIZE_SHRINK_JSON = OUT_DIR / "v28_exit_loss_guard_v3_residual_bucket_size_shrink_latest.json"
EXIT_LOSS_GUARD_V1_V2_RUNWAY_JSON = OUT_DIR / "v28_exit_loss_guard_v1_v2_runway_latest.json"
EXIT_COMMON_CLOCK_JSON = OUT_DIR / "v28_exit_policy_common_clock_watch_latest.json"
EXIT_COMMON_CLOCK_RUNWAY_JSON = OUT_DIR / "v28_exit_common_clock_promotion_runway_latest.json"
EXIT_COMMON_CLOCK_RESIDUAL_FRONTIER_JSON = OUT_DIR / "v28_exit_common_clock_residual_frontier_latest.json"
EXIT_STRICT_FAILURE_DRILLDOWN_JSON = OUT_DIR / "v28_exit_policy_strict_failure_drilldown_latest.json"
EXIT_COMMON_CLOCK_RESIDUAL_CHILD_JSON = OUT_DIR / "v28_frozen_exit_common_clock_residual_child_watch_latest.json"
EXIT_COMMON_CLOCK_RESIDUAL_CHILD_PATH_RISK_JSON = OUT_DIR / "v28_exit_common_clock_residual_child_path_risk_latest.json"
EXIT_COMMON_CLOCK_RESIDUAL_CHILD_FALSE_HOLD_AUTOPSY_JSON = OUT_DIR / "v28_exit_common_clock_residual_child_false_hold_autopsy_latest.json"
EXIT_COMMON_CLOCK_RESIDUAL_CHILD_GUARDRAIL_VARIANTS_JSON = OUT_DIR / "v28_exit_common_clock_residual_child_guardrail_variants_latest.json"
EXIT_COMMON_CLOCK_RESIDUAL_CHILD_BOOK_GAP_GUARD_WATCH_JSON = OUT_DIR / "v28_frozen_exit_common_clock_residual_child_book_gap_guard_watch_latest.json"
EXIT_POLICY_WATCH_DASHBOARD_JSON = OUT_DIR / "v28_exit_policy_watch_dashboard_latest.json"
EXIT_PROMOTION_QUEUE_AUDIT_JSON = OUT_DIR / "v28_exit_promotion_queue_audit_latest.json"
DUAL_EXIT_JSON = OUT_DIR / "v28_frozen_dual_exit_book_gap_else_reduce_latest.json"
TARGET_LOSS_ATTRIBUTION_JSON = OUT_DIR / "v28_target_coverage_loss_attribution_latest.json"
TARGET_PRICE_FRICTION_JSON = OUT_DIR / "v28_target_coverage_price_friction_latest.json"
TARGET_CLUSTER_PENALTY_RUNWAY_JSON = OUT_DIR / "v28_target_cluster_penalty_runway_latest.json"
TARGET_CLUSTER_PENALTY_SOURCE_FEASIBILITY_JSON = OUT_DIR / "v28_target_cluster_penalty_source_feasibility_latest.json"
TARGET_CLUSTER_PENALTY_SOURCE_DISPLACEMENT_JSON = OUT_DIR / "v28_target_cluster_penalty_source_displacement_latest.json"
TARGET_CLUSTER_PENALTY_SOURCE_AWARE_JSON = OUT_DIR / "v28_target_cluster_penalty_source_aware_watch_latest.json"
TARGET_CLUSTER_PENALTY_OBSERVABLE_STABILITY_JSON = OUT_DIR / "v28_target_cluster_penalty_observable_stability_proxy_latest.json"
FEATURE_GATE_CLEAN_BROAD_FRONTIER_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_clean_broad_frontier_watch_latest.json"
FEATURE_GATE_SOFT_FRONTIER_EXIT_STACK_JSON = OUT_DIR / "v28_frozen_feature_gate_soft_frontier_exit_stack_latest.json"
FEATURE_GATE_CHEAP_TAIL_SHRINK_WATCH_JSON = OUT_DIR / "v28_frozen_feature_gate_cheap_tail_shrink_watch_latest.json"
FEATURE_GATE_NEAR_PROMOTION_WATCH_JSON = OUT_DIR / "v28_feature_gate_near_promotion_watch_latest.json"
FEATURE_GATE_NEAR_PROMOTION_EXIT_ATTRIBUTION_JSON = OUT_DIR / "v28_feature_gate_near_promotion_exit_attribution_latest.json"
FEATURE_GATE_NEAR_PROMOTION_DENOMINATOR_GAP_JSON = OUT_DIR / "v28_feature_gate_near_promotion_denominator_gap_latest.json"
FEATURE_GATE_QUICK_STATUS_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_quick_status_latest.json"
FEATURE_GATE_RAW03_VS_RAW05_AUTOPSY_JSON = OUT_DIR / "v28_feature_gate_raw03_vs_raw05_autopsy_latest.json"
FEATURE_GATE_RAW05_COVERAGE_GAP_JSON = OUT_DIR / "v28_feature_gate_raw05_coverage_gap_audit_latest.json"
FEATURE_GATE_CORE_EXPANSION_MIX_JSON = OUT_DIR / "v28_feature_gate_core_expansion_mix_latest.json"
FEATURE_GATE_COVERAGE_REPAIR_JSON = OUT_DIR / "v28_feature_gate_coverage_repair_latest.json"
FEATURE_GATE_COVERAGE_SIZE_SHRINK_JSON = OUT_DIR / "v28_feature_gate_coverage_size_shrink_latest.json"
FEATURE_GATE_COVERAGE_SIZE_SHRINK_EXIT_ATTR_JSON = OUT_DIR / "v28_feature_gate_coverage_size_shrink_exit_attribution_latest.json"
FEATURE_GATE_COVERAGE_SIZE_SHRINK_RUNWAY_JSON = OUT_DIR / "v28_feature_gate_coverage_size_shrink_runway_latest.json"
FEATURE_GATE_JOINT_GAP_JSON = OUT_DIR / "v28_feature_gate_joint_gate_gap_audit_latest.json"
FEATURE_GATE_GAP_MECHANISM_SYNTHESIS_JSON = OUT_DIR / "v28_feature_gate_gap_mechanism_synthesis_latest.json"
FEATURE_GATE_CURRENT_MARGIN_SIZE_PROXY_JSON = OUT_DIR / "v28_feature_gate_current_margin_size_proxy_latest.json"
SOFT_FRONTIER_SIZE_SHRINK_JSON = OUT_DIR / "v28_soft_frontier_size_shrink_portfolio_latest.json"
SOFT_FRONTIER_MIDPRICE_BOUNDARY_SHRINK_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_shrink_latest.json"
SOFT_FRONTIER_MIDPRICE_BOUNDARY_SOURCE_STRESS_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_source_stress_latest.json"
SOFT_FRONTIER_MIDPRICE_BOUNDARY_EXIT_STACK_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_exit_stack_latest.json"
SOFT_FRONTIER_MIDPRICE_BOUNDARY_EXIT_STACK_RUNWAY_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_exit_stack_runway_latest.json"
SOFT_FRONTIER_MIDPRICE_BOUNDARY_DUAL_EXIT_STACK_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_dual_exit_stack_latest.json"
SOFT_FRONTIER_MIDPRICE_BOUNDARY_DUAL_EXIT_GUARD_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_dual_exit_guard_refinement_latest.json"
CONTROL_RISK_STOP_AUDIT_JSON = OUT_DIR / "v28_control_risk_stop_audit_latest.json"
EXIT_POLICY_LOSS_CHURN_JSON = OUT_DIR / "v28_exit_policy_loss_churn_effect_latest.json"
LOSS_CHURN_GUARDED_FRONTIER_JSON = OUT_DIR / "v28_loss_churn_guarded_repair_frontier_latest.json"
LOSS_CHURN_FULL_DENOM_REPLAY_JSON = OUT_DIR / "v28_loss_churn_observable_full_denominator_replay_latest.json"
LOSS_CHURN_RECROSS_CLOCK_FEASIBILITY_JSON = OUT_DIR / "v28_loss_churn_recross_clock_feasibility_latest.json"
LOSS_CHURN_RECROSS_JOIN_AUDIT_JSON = OUT_DIR / "v28_loss_churn_recross_exit_clock_join_audit_latest.json"
LOSS_CHURN_RECROSS_THRESHOLD_FRONTIER_JSON = OUT_DIR / "v28_loss_churn_recross_threshold_frontier_latest.json"
EXIT_CLOCK_SOURCE_STABILITY_JSON = OUT_DIR / "v28_exit_clock_source_stability_latest.json"
EXIT_CLOCK_LOW_EDGE_HOLD_GUARD_TRADEOFF_JSON = OUT_DIR / "v28_exit_clock_low_edge_hold_guard_tradeoff_latest.json"
EXIT_CLOCK_BROAD_HOLD_NEIGHBOR_AUTOPSY_JSON = OUT_DIR / "v28_exit_clock_broad_hold_neighbor_autopsy_latest.json"
FORWARD_COLLECTION_BLOCKER_AUDIT_JSON = OUT_DIR / "v28_forward_collection_blocker_audit_latest.json"
LIVE_LOSS_ESCAPE_JSON = OUT_DIR / "v28_live_loss_escape_analysis_latest.json"
DUAL_LANE_SAME_WINDOW_DELTA_AUTOPSY_JSON = OUT_DIR / "v28_dual_lane_same_window_delta_autopsy_latest.json"
DUAL_LANE_SAME_WINDOW_SEQUENCE_MECHANISM_JSON = OUT_DIR / "v28_dual_lane_same_window_sequence_mechanism_latest.json"
DUAL_LANE_STATE_EXPOSURE_REPAIR_JSON = OUT_DIR / "v28_dual_lane_state_exposure_sequence_repair_latest.json"
DUAL_LANE_SIDE_FLIP_FEASIBILITY_JSON = OUT_DIR / "v28_dual_lane_side_flip_feasibility_latest.json"
EXIT_REPAIR_GAP_CLASSIFIER_JSON = OUT_DIR / "v28_exit_repair_gap_classifier_latest.json"
MATCHED_UNCHANGED_LOSS_SEPARATOR_JSON = OUT_DIR / "v28_matched_unchanged_loss_separator_latest.json"
MATCHED_UNCHANGED_LOSS_GUARD_WATCH_JSON = OUT_DIR / "v28_frozen_matched_unchanged_loss_guard_watch_latest.json"
MATCHED_UNCHANGED_LOSS_GUARD_OPPORTUNITY_JSON = OUT_DIR / "v28_matched_unchanged_loss_guard_opportunity_latest.json"
EXIT_TRUE_LOSER_HOLD_RISK_JSON = OUT_DIR / "v28_exit_true_loser_hold_risk_audit_latest.json"
EXIT_FALSE_HOLD_GUARDRAIL_BRIDGE_JSON = OUT_DIR / "v28_exit_false_hold_guardrail_bridge_latest.json"
EXIT_CLIP_SEPARATOR_JSON = OUT_DIR / "v28_exit_clip_separator_diagnostic_latest.json"
EXIT_CLIP_SEPARATOR_WATCH_JSON = OUT_DIR / "v28_frozen_exit_clip_separator_watch_latest.json"
EXIT_CLIP_SEPARATOR_OPPORTUNITY_JSON = OUT_DIR / "v28_exit_clip_separator_opportunity_latest.json"
EXIT_CLIP_SEPARATOR_REPLAY_JSON = OUT_DIR / "v28_exit_clip_separator_replay_latest.json"
APPROVED_ENTRY_STATE_VALVE_BRIDGE_JSON = OUT_DIR / "v28_approved_entry_state_valve_bridge_latest.json"
APPROVED_ENTRY_STATE_VALVE_FULL_SURFACE_JSON = OUT_DIR / "v28_approved_entry_state_valve_full_surface_latest.json"
HIGH_GAP_SKIPPED_FAILURE_MODES_JSON = OUT_DIR / "v28_high_gap_skipped_failure_modes_latest.json"
FEATURE_GATE_HIGH_GAP_SHRINK_DIAGNOSTIC_JSON = OUT_DIR / "v28_feature_gate_high_gap_shrink_diagnostic_latest.json"
COLLAPSE_SUPPRESS_SHADOW_JSON = OUT_DIR / "live_v28_collapse_suppress_shadow_monitor_latest.json"
COLLAPSE_REENTRY_JSON = OUT_DIR / "v28_live_collapse_reentry_registry_latest.json"
OUT_JSON = OUT_DIR / "v28_next_action_triage_latest.json"
OUT_MD = OUT_DIR / "v28_next_action_triage_latest.md"


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


def blocker_family(blocker: str) -> str:
    raw = blocker.split(":", 1)[-1]
    if "net_not_positive" in raw or "delta_not_positive" in raw:
        return "profitability"
    if "coverage_too_low" in raw or "coverage_below" in raw:
        return "coverage_low"
    if "coverage_too_high" in raw:
        return "coverage_high"
    if "settled_lt" in raw or "sample" in raw:
        return "sample_size"
    if "simulated_share" in raw or "actual_approved" in raw:
        return "live_evidence_quality"
    if "brier" in raw or "logloss" in raw or "calibration" in raw:
        return "calibration"
    if "risk_stop" in raw:
        return "risk_stop"
    return "other"


def candidate_score(row: dict[str, Any]) -> float:
    net = as_float(row.get("net_cents_after_entry_fee")) or -9999.0
    settled = as_float(row.get("settled")) or 0.0
    coverage = as_float(row.get("coverage_pct"))
    coverage_bonus = 0.0
    if coverage is not None:
        if 75.0 <= coverage <= 90.0:
            coverage_bonus = 250.0
        elif 70.0 <= coverage <= 95.0:
            coverage_bonus = 80.0
    return net + coverage_bonus + min(settled, 30.0) * 2.0


def candidate_row(row: dict[str, Any]) -> dict[str, Any]:
    blockers = row.get("blockers") or []
    families = Counter(blocker_family(str(blocker)) for blocker in blockers)
    return {
        "gate": row.get("gate"),
        "policy": row.get("policy"),
        "live_ready": row.get("live_ready"),
        "entries": row.get("entries"),
        "settled": row.get("settled"),
        "coverage_pct": row.get("coverage_pct"),
        "net_cents": row.get("net_cents_after_entry_fee"),
        "avg_brier": row.get("avg_brier"),
        "blockers": blockers,
        "blocker_families": dict(families),
        "triage_score": candidate_score(row),
    }


def exit_lane_status(payload: dict[str, Any], label: str) -> dict[str, Any]:
    summary = payload.get("summary") or {}
    discovery = payload.get("discovery_summary_existing_exit_sample") or {}
    return {
        "label": label,
        "candidate": (payload.get("freeze") or {}).get("candidate"),
        "settled": summary.get("settled"),
        "rows": summary.get("rows"),
        "delta_vs_current_cents": summary.get("delta_vs_current_cents"),
        "suppressed_exits": summary.get("suppressed_exits"),
        "winner_clip_recovered_cents": summary.get("winner_clip_recovered_cents"),
        "loss_control_cost_cents": summary.get("loss_control_cost_cents"),
        "discovery_candidate_gross_cents": discovery.get("candidate_gross_cents"),
        "discovery_delta_vs_current_cents": discovery.get("delta_vs_current_cents"),
        "discovery_loss_control_cost_cents": discovery.get("loss_control_cost_cents"),
        "blockers": payload.get("blockers") or [],
    }


def variant_lane_status(payload: dict[str, Any], label: str, lane_name: str) -> dict[str, Any]:
    lane = next((row for row in payload.get("lanes") or [] if row.get("lane") == lane_name), {})
    best = (lane.get("variants") or [{}])[0]
    summary = best.get("summary") or {}
    return {
        "label": label,
        "candidate": best.get("candidate"),
        "settled": summary.get("settled"),
        "rows": summary.get("rows"),
        "delta_vs_current_cents": summary.get("delta_vs_current_cents"),
        "suppressed_exits": summary.get("suppressed_exits"),
        "winner_clip_recovered_cents": summary.get("winner_clip_recovered_cents"),
        "loss_control_cost_cents": summary.get("loss_control_cost_cents"),
        "discovery_candidate_gross_cents": None,
        "discovery_delta_vs_current_cents": None,
        "discovery_loss_control_cost_cents": None,
        "blockers": best.get("blockers") or [],
    }


def build_recommendations(report: dict[str, Any]) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    exit_lanes = report["exit_lanes"]
    reduce_lane = next((row for row in exit_lanes if row["label"] == "reduce_suppression"), {})
    book_gap_lane = next((row for row in exit_lanes if row["label"] == "book_gap_suppression"), {})
    book_gap_loss_guard_lane = next((row for row in exit_lanes if row["label"] == "book_gap_loss_guard"), {})
    book_gap_loss_guard_v2_lane = next((row for row in exit_lanes if row["label"] == "book_gap_loss_guard_v2"), {})
    book_gap_loss_guard_v3_lane = next((row for row in exit_lanes if row["label"] == "book_gap_loss_guard_v3"), {})
    book_gap_value_only_lane = next((row for row in exit_lanes if row["label"] == "book_gap_value_only"), {})
    exit_value_reduce_depth_lane = next((row for row in exit_lanes if row["label"] == "exit_value_reduce_depth"), {})
    observable_loss_control_lane = next((row for row in exit_lanes if row["label"] == "exit_reduce_observable_loss_control"), {})
    dual_exit_lane = next((row for row in exit_lanes if row["label"] == "dual_exit_book_gap_else_reduce"), {})
    midband_rescue = report.get("exit_midband_reduce_rescue") or {}
    risk_audit = report.get("control_risk_stop_audit") or {}
    risk_summary = risk_audit.get("summary") or {}
    churn = report.get("exit_policy_loss_churn") or {}
    loss_churn_frontier = report.get("loss_churn_guarded_frontier") or {}
    loss_churn_full_denom_replay = report.get("loss_churn_observable_full_denominator_replay") or {}
    loss_churn_recross_clock = report.get("loss_churn_recross_clock_feasibility") or {}
    loss_churn_recross_join = report.get("loss_churn_recross_exit_clock_join_audit") or {}
    loss_churn_recross_threshold = report.get("loss_churn_recross_threshold_frontier") or {}
    exit_clock_stability = report.get("exit_clock_source_stability") or {}
    exit_clock_low_edge_hold_guard = report.get("exit_clock_low_edge_hold_guard_tradeoff") or {}
    exit_clock_broad_hold_autopsy = report.get("exit_clock_broad_hold_neighbor_autopsy") or {}
    forward_collection_blocker = report.get("forward_collection_blocker_audit") or {}
    loss_escape = report.get("live_loss_escape_analysis") or {}
    dual_lane_delta = report.get("dual_lane_same_window_delta_autopsy") or {}
    dual_lane_sequence = report.get("dual_lane_same_window_sequence_mechanism") or {}
    dual_lane_state_repair = report.get("dual_lane_state_exposure_sequence_repair") or {}
    dual_lane_side_flip = report.get("dual_lane_side_flip_feasibility") or {}
    exit_gap = report.get("exit_repair_gap_classifier") or {}
    matched_separator = report.get("matched_unchanged_loss_separator") or {}
    matched_guard_watch = report.get("matched_unchanged_loss_guard_watch") or {}
    matched_guard_opportunity = report.get("matched_unchanged_loss_guard_opportunity") or {}
    true_loser_hold_risk = report.get("exit_true_loser_hold_risk") or {}
    false_hold_bridge = report.get("exit_false_hold_guardrail_bridge") or {}
    common_clock_residual_frontier = report.get("exit_common_clock_residual_frontier") or {}
    residual_child = report.get("exit_common_clock_residual_child_watch") or {}
    residual_child_path_risk = report.get("exit_common_clock_residual_child_path_risk") or {}
    residual_child_false_hold = report.get("exit_common_clock_residual_child_false_hold_autopsy") or {}
    residual_child_guards = report.get("exit_common_clock_residual_child_guardrail_variants") or {}
    residual_child_book_gap_guard = report.get("exit_common_clock_residual_child_book_gap_guard_watch") or {}
    exit_clip = report.get("exit_clip_separator") or {}
    exit_clip_watch = report.get("exit_clip_separator_watch") or {}
    exit_clip_opportunity = report.get("exit_clip_separator_opportunity") or {}
    exit_clip_replay = report.get("exit_clip_separator_replay") or {}
    exit_queue = report.get("exit_promotion_queue_audit") or {}
    approved_valve_bridge = report.get("approved_entry_state_valve_bridge") or {}
    approved_valve_full_surface = report.get("approved_entry_state_valve_full_surface") or {}
    high_gap_skipped_failure_modes = report.get("high_gap_skipped_failure_modes") or {}
    feature_gate_high_gap_shrink = report.get("feature_gate_high_gap_shrink_diagnostic") or {}
    feature_gate_quick_status = report.get("feature_gate_quick_status") or {}
    feature_gate_raw03_vs_raw05 = report.get("feature_gate_raw03_vs_raw05_autopsy") or {}
    feature_gate_raw05_gap = report.get("feature_gate_raw05_coverage_gap_audit") or {}
    feature_gate_joint_gap = report.get("feature_gate_joint_gate_gap_audit") or {}
    feature_gate_gap_mechanism = report.get("feature_gate_gap_mechanism_synthesis") or {}
    feature_gate_current_margin_size = report.get("feature_gate_current_margin_size_proxy") or {}
    exit_loss_guard_v3_residual_size_shrink = report.get("exit_loss_guard_v3_residual_size_shrink") or {}
    reduce_observable_false_hold = report.get("exit_reduce_observable_false_hold_autopsy") or {}
    collapse_shadow = report.get("collapse_suppress_shadow") or {}
    collapse_reentry = report.get("collapse_reentry_registry") or {}
    churn_rows = churn.get("rows") or []
    top_churn = churn_rows[0] if churn_rows else {}
    gap_summary = exit_gap.get("summary") or {}
    clip_summary = exit_clip.get("summary") or {}
    clip_best = (exit_clip.get("top_rules") or [{}])[0]
    clip_watch_summary = exit_clip_watch.get("candidate_summary") or {}
    clip_opp_selected = exit_clip_opportunity.get("selected_summary") or {}
    clip_opp_near = exit_clip_opportunity.get("near_miss_summary") or {}
    clip_replay_summaries = exit_clip_replay.get("summaries") or []
    clip_replay_diag = next((row for row in clip_replay_summaries if row.get("label") == "diagnostic_from_exit_reduce_freeze"), {})
    clip_replay_post = next((row for row in clip_replay_summaries if row.get("label") == "post_clip_watch_freeze"), {})
    if "live_watchdog_restart_failed" in (forward_collection_blocker.get("blockers") or []):
        monitor = forward_collection_blocker.get("live_monitor") or {}
        lock = forward_collection_blocker.get("live_lock") or {}
        lock_payload = lock.get("payload") or {}
        recommendations.append({
            "rank": 0.79,
            "action": "pause_fresh_v28_live_collection_claims_until_live_state_is_resolved",
            "why": (
                "The forward collection blocker audit says fresh v28 frozen/live evidence is not currently flowing from the live bot. "
                f"Latest watchdog line is `{monitor.get('latest_line')}`. "
                f"The shared live lock currently points at pid {lock_payload.get('pid')} / tag {lock_payload.get('strategy_tag')}, "
                "so candidate-vs-live claims should be treated as log-snapshot claims until v28 live collection is explicitly healthy again. "
                "This is a research blocker report only; do not restart or stop live processes without explicit user direction."
            ),
            "evidence": forward_collection_blocker,
        })
    if risk_summary.get("risk_stop_by_loss_count") and not risk_summary.get("risk_stop_by_drawdown"):
        recommendations.append({
            "rank": 0.8,
            "action": "repair_loss_count_churn_before_sidecar_live_test",
            "why": (
                "The global live-readiness blocker is loss-count churn, not drawdown: "
                f"{risk_summary.get('losing_trades')} losing scored trades, "
                f"{risk_summary.get('full_loss_events')} full-loss events, "
                f"{risk_summary.get('near_full_loss_events_50_99c')} near-full losses, and max drawdown "
                f"{risk_summary.get('max_drawdown_pct')}%. The current best churn lens is "
                f"{top_churn.get('label')} with loss-count reduction {top_churn.get('loss_count_reduction')} "
                f"and delta {top_churn.get('delta_cents')}c. Exit repairs must reduce small/medium loss clusters before a sidecar trial."
            ),
            "evidence": {
                "risk_stop": risk_audit,
                "exit_policy_loss_churn_top": churn_rows[:5],
                "live_loss_escape_analysis": {
                    "escape_class_counts": loss_escape.get("escape_class_counts"),
                    "best_repair_policy_counts": loss_escape.get("best_repair_policy_counts"),
                    "largest_escaped_losses": loss_escape.get("largest_escaped_losses"),
                },
            },
        })
    if loss_churn_frontier:
        clean = loss_churn_frontier.get("clean_frontier") or []
        observable = loss_churn_frontier.get("observable_clean_frontier") or []
        best_clean = clean[0] if clean else {}
        best_observable = observable[0] if observable else {}
        recommendations.append({
            "rank": 0.801,
            "action": "use_loss_churn_frontier_to_find_observable_state_trigger_not_hindsight_label",
            "why": (
                "The refreshed guarded loss-churn frontier explains the blocker but does not produce a freezeable rule. "
                f"Best clean diagnostic separator is {best_clean.get('rule')} with {best_clean.get('loss_flips')} loss flips "
                f"and {fmt(best_clean.get('hold_delta_cents'))}c hold delta, but that relies on diagnostic labels. "
                f"Best observable-only clean guard is {best_observable.get('rule')} with {best_observable.get('loss_flips')} flips, "
                f"{best_observable.get('selected_loss_rows')} selected loss rows, and blockers {best_observable.get('blockers')}. "
                "Next exit work should search for a pre-registered observable state trigger that approximates the diagnostic separation across the full denominator."
            ),
            "evidence": loss_churn_frontier,
        })
    if loss_churn_full_denom_replay:
        best_replay = loss_churn_full_denom_replay.get("best_clean_replay") or {}
        recommendations.append({
            "rank": 0.802,
            "action": "freeze_or_track_recross_loss_churn_guard_only_after_strict_clock_definition",
            "why": (
                "The observable loss-churn replay passed the full-denominator harm check but is still not promotion evidence. "
                f"Best clean replay is {best_replay.get('rule')} with {best_replay.get('selected_rows')} selected rows, "
                f"{best_replay.get('loss_flips')} loss flips, {fmt(best_replay.get('delta_cents'))}c delta, "
                f"candidate net {fmt(best_replay.get('candidate_net_cents'))}c versus live baseline "
                f"{fmt(loss_churn_full_denom_replay.get('live_baseline_cents'))}c, and "
                f"{best_replay.get('harmful_rows')} harmful / {best_replay.get('new_losses')} new-loss rows. "
                "The blocker is strict evidence: it is a diagnostic replay with fewer than 30 selected decisions. "
                f"Clock feasibility blockers are {loss_churn_recross_clock.get('blockers')}; "
                f"exit-clock join selected {(loss_churn_recross_join.get('tolerance_join') or {}).get('summary', {}).get('selected_rows')} rows; "
                f"source stability is {exit_clock_stability.get('stable_for_new_freeze')} with row counts {exit_clock_stability.get('row_count_values')}. "
                f"The materialized threshold frontier best clean point is {((loss_churn_recross_threshold.get('best_clean') or {}).get('threshold'))} "
                f"with {((loss_churn_recross_threshold.get('best_clean') or {}).get('selected_rows'))} selected rows and "
                f"{fmt(((loss_churn_recross_threshold.get('best_clean') or {}).get('delta_cents')))}c delta; looser thresholds introduce harmful/new-loss rows. "
                f"The low-edge broad-hold tradeoff also blocks a simple expansion: best clean policy "
                f"{((exit_clock_low_edge_hold_guard.get('best_clean') or {}).get('policy'))} has "
                f"{((exit_clock_low_edge_hold_guard.get('best_clean') or {}).get('selected_rows'))} selected rows and no clean >=30 policy. "
                f"The neighbor autopsy shows the low-edge slice is mixed: "
                f"{((exit_clock_broad_hold_autopsy.get('low_edge_lt7_summary') or {}).get('helpful_rows'))}/"
                f"{((exit_clock_broad_hold_autopsy.get('low_edge_lt7_summary') or {}).get('harmful_rows'))} helpful/harmful, "
                f"while the clean high-edge survivor has {((exit_clock_broad_hold_autopsy.get('high_edge_ge7_summary') or {}).get('rows'))} rows. "
                "Do not freeze this recross guard; keep it as a sparse mechanism clue."
            ),
            "evidence": {
                "full_denominator_replay": loss_churn_full_denom_replay,
                "clock_feasibility": loss_churn_recross_clock,
                "exit_clock_join_audit": loss_churn_recross_join,
                "threshold_frontier": loss_churn_recross_threshold,
                "exit_clock_source_stability": exit_clock_stability,
                "low_edge_hold_guard_tradeoff": exit_clock_low_edge_hold_guard,
                "broad_hold_neighbor_autopsy": exit_clock_broad_hold_autopsy,
            },
        })
    if dual_lane_state_repair:
        best = dual_lane_state_repair.get("best_variant") or {}
        recommendations.append({
            "rank": 0.806,
            "action": "do_not_freeze_simple_dual_lane_exposure_weighting_yet",
            "why": (
                f"The state/exposure sequencing probe confirms the mechanism is real but the simple observable repair is incomplete. "
                f"Best diagnostic variant {best.get('variant')} improves candidate net by "
                f"{fmt(best.get('delta_vs_baseline_candidate_cents'))}c to {fmt(best.get('adjusted_candidate_net_cents'))}c, "
                f"but still runs {fmt(best.get('adjusted_candidate_minus_live_cents'))}c behind live on the same markets, "
                f"has full-loss cushion {best.get('full_loss_cushion')}, and blockers {best.get('blockers')}. "
                "Do not freeze this simple weighting as a candidate; use it as evidence that the repair needs explicit state-transition/side-flip logic or more mature own-freeze rows."
            ),
            "evidence": dual_lane_state_repair,
        })
    if dual_lane_side_flip:
        candidate_flip = dual_lane_side_flip.get("candidate_side_flip_summary") or {}
        rescue = dual_lane_side_flip.get("candidate_opposite_rescue_summary") or {}
        all_flip = dual_lane_side_flip.get("all_live_side_flip_summary") or {}
        all_live = dual_lane_side_flip.get("all_live_summary") or {}
        recommendations.append({
            "rank": 0.8065,
            "action": "do_not_freeze_side_flip_repair_without_observable_state_trigger",
            "why": (
                "Side-flip escape is a real current deficit mechanism, but it is not yet an actionable candidate. "
                f"Candidate side-flip markets are {candidate_flip.get('markets')} with net {fmt(candidate_flip.get('net_cents'))}c; "
                f"candidate opposite-rescue markets are {rescue.get('markets')} with net {fmt(rescue.get('net_cents'))}c. "
                f"Across all post-freeze live markets, side flips are {all_flip.get('markets')} of {all_live.get('markets')} "
                f"and net {fmt(all_flip.get('net_cents'))}c. "
                f"Blockers are {dual_lane_side_flip.get('blockers')}. "
                "A deployable repair needs an explicit observable state-transition trigger and its own freeze."
            ),
            "evidence": dual_lane_side_flip,
        })
    if dual_lane_delta:
        classes = dual_lane_delta.get("classification_summary") or []
        worst = classes[0] if classes else {}
        mechanisms = dual_lane_sequence.get("mechanism_summary") or []
        worst_mechanism = mechanisms[0] if mechanisms else {}
        recommendations.append({
            "rank": 0.805,
            "action": "treat_dual_lane_same_window_delta_as_live_baseline_blocker",
            "why": (
                "The dual-lane forced strict precheck is still behind actual live v28 on the same post-freeze markets: "
                f"{fmt(dual_lane_delta.get('candidate_minus_live_same_markets_cents'))}c candidate-minus-live. "
                f"The deficit side has {dual_lane_delta.get('deficit_rows')} rows for "
                f"{fmt(dual_lane_delta.get('deficit_cents'))}c, partly offset by "
                f"{dual_lane_delta.get('surplus_rows')} surplus rows for {fmt(dual_lane_delta.get('surplus_cents'))}c. "
                f"The largest negative bucket is {worst.get('classification')} with {worst.get('rows')} row(s) and "
                f"{fmt(worst.get('candidate_minus_live_cents'))}c. "
                f"Sequence audit tags the largest mechanism as {worst_mechanism.get('mechanism')} with "
                f"{worst_mechanism.get('rows')} row(s) and {fmt(worst_mechanism.get('candidate_minus_live_cents'))}c. "
                "This must be treated as a live-baseline blocker until own-freeze rows mature and the candidate beats live on refreshed evidence."
            ),
            "evidence": {
                "delta_autopsy": dual_lane_delta,
                "sequence_mechanism": dual_lane_sequence,
            },
        })
    if exit_queue:
        queue = exit_queue.get("forward_positive_queue") or []
        closest = queue[0] if queue else {}
        missing = closest.get("missing") or {}
        recommendations.append({
            "rank": 0.807,
            "action": "collect_exit_suppression_density_before_review",
            "why": (
                "The refreshed exit promotion queue has zero review-ready rows. "
                f"Closest is {closest.get('lane')} with {closest.get('settled')} settled rows, "
                f"{closest.get('suppressed_exits')} suppressions, candidate/delta cushion "
                f"{closest.get('candidate_full_loss_cushion')}/{closest.get('delta_full_loss_cushion')}, "
                f"and delta {closest.get('delta_vs_current_cents')}c. It still needs "
                f"{missing.get('suppressed_decisions_needed')} suppressions and "
                f"{missing.get('delta_cents_needed_for_cushion3')}c of delta cushion, so the next exit work is "
                "strict-row collection and density tracking, not a new diagnostic rule."
            ),
            "evidence": {
                "exit_promotion_queue_audit": exit_queue,
            },
        })
    if common_clock_residual_frontier:
        windows = common_clock_residual_frontier.get("windows") or []
        v2 = next((row for row in windows if row.get("window") == "new_exit_mix_common_forward_v2"), {})
        v3 = next((row for row in windows if row.get("window") == "new_exit_mix_common_forward_v3"), {})
        v2_candidates = v2.get("candidates") or []
        v3_candidates = v3.get("candidates") or []
        v2_best = v2_candidates[0] if v2_candidates else {}
        v2_clean = next(
            (
                row for row in v2_candidates
                if "residual_harmful_false_holds_present" not in (row.get("blockers") or [])
            ),
            {},
        )
        v3_clean = next(
            (
                row for row in v3_candidates
                if "residual_harmful_false_holds_present" not in (row.get("blockers") or [])
            ),
            {},
        )
        recommendations.append({
            "rank": 0.8075,
            "action": "treat_common_clock_residual_rescue_as_child_watch_only",
            "why": (
                "The strict residual frontier explains why the common-clock exit guard should not be broadened by low-p_hold alone. "
                f"In v2, the best broad residual {v2_best.get('residual_policy')} adds "
                f"{fmt(v2_best.get('residual_delta_vs_base_cents'))}c versus base across "
                f"{v2_best.get('residual_suppressed')} residual rows, but has helpful/harmful "
                f"{v2_best.get('residual_helpful')}/{v2_best.get('residual_harmful')}. "
                f"The best clean v2 residual {v2_clean.get('residual_policy')} is "
                f"{v2_clean.get('residual_suppressed')} rows for {fmt(v2_clean.get('residual_delta_vs_base_cents'))}c, "
                f"and v3 clean residual {v3_clean.get('residual_policy')} is "
                f"{v3_clean.get('residual_suppressed')} rows for {fmt(v3_clean.get('residual_delta_vs_base_cents'))}c. "
                "These clean collapse-full add-ons are too sparse for promotion, so the next action is strict collection or a separately frozen child watch, not a live exit change."
            ),
            "evidence": common_clock_residual_frontier,
        })
    if exit_loss_guard_v3_residual_size_shrink:
        windows = exit_loss_guard_v3_residual_size_shrink.get("windows") or []
        strict_v3 = next((row for row in windows if row.get("window") == "v3_strict_forward"), {})
        diagnostic = next((row for row in windows if row.get("window") == "all_exit_rows_diagnostic"), {})
        strict_residual = strict_v3.get("residual_v1_only_bucket") or {}
        diagnostic_residual = diagnostic.get("residual_v1_only_bucket") or {}
        strict_full = next(
            (row for row in strict_v3.get("policies") or [] if row.get("policy") == "v3_plus_residual_full_v1_like"),
            {},
        )
        recommendations.append({
            "rank": 0.808,
            "action": "do_not_relax_v3_with_residual_bucket_yet",
            "why": (
                "The v3 loss-guard residual bucket is tempting but still physically suspect. "
                f"In strict v3-forward rows, v1-only residual exposure is only {strict_residual.get('rows')} row(s) "
                f"for {fmt(strict_residual.get('net_delta_cents'))}c and {fmt(strict_residual.get('harmful_delta_cents'))}c harmful delta. "
                f"Across all diagnostic exit rows, the same residual bucket is {diagnostic_residual.get('rows')} row(s), "
                f"{fmt(diagnostic_residual.get('net_delta_cents'))}c net, and "
                f"{fmt(diagnostic_residual.get('harmful_delta_cents'))}c harmful delta. "
                f"Even full residual relaxation in the strict v3 window has {strict_full.get('decision_count')} selected decisions, "
                f"delta cushion {strict_full.get('delta_full_loss_cushion')}, and blockers {strict_full.get('blockers')}. "
                "Treat v3 hard rejection as the safer default until a separately frozen residual or partial-size watch earns rows."
            ),
            "evidence": exit_loss_guard_v3_residual_size_shrink,
        })
    if reduce_observable_false_hold:
        windows = reduce_observable_false_hold.get("windows") or []
        diagnostic_window = next((row for row in windows if row.get("window") == "diagnostic_from_reduce_freeze"), {})
        post_window = next((row for row in windows if row.get("window") == "post_observable_birth"), {})
        diagnostic_summary = diagnostic_window.get("candidate_summary") or {}
        post_summary = post_window.get("candidate_summary") or {}
        best_post_guard = (post_window.get("zero_harm_guards") or post_window.get("best_guards") or [{}])[0]
        recommendations.append({
            "rank": 0.809,
            "action": "downgrade_observable_reduce_loss_control_until_false_hold_guard_freezes",
            "why": (
                "Observable reduce-loss-control still explains diagnostic loss churn, but the fresh p_hold>=0.75 "
                "probability-reduce denominator is not yet safe. "
                f"Diagnostic denominator: {diagnostic_summary.get('rows')} rows, "
                f"{fmt(diagnostic_summary.get('net_delta_cents'))}c net, "
                f"{diagnostic_summary.get('helpful_rows')}/{diagnostic_summary.get('harmful_rows')} helpful/harmful, "
                f"and {fmt(diagnostic_summary.get('harmful_delta_cents'))}c harmful delta. "
                f"Post-observable-birth denominator: {post_summary.get('rows')} rows, "
                f"{fmt(post_summary.get('net_delta_cents'))}c net, "
                f"{post_summary.get('helpful_rows')}/{post_summary.get('harmful_rows')} helpful/harmful, "
                f"and {fmt(post_summary.get('harmful_delta_cents'))}c harmful delta. "
                f"The best post-birth zero-harm split ({best_post_guard.get('feature')} {best_post_guard.get('direction')} "
                f"{best_post_guard.get('threshold')}) has only {best_post_guard.get('selected_rows')} rows, so it is a "
                "post-hoc child idea, not evidence to broaden exit suppression."
            ),
            "evidence": reduce_observable_false_hold,
        })
    clip_watch_state = exit_clip_watch.get("state") if isinstance(exit_clip_watch.get("state"), dict) else {}
    clip_watch_frozen = bool(clip_watch_state.get("freeze_ts_utc"))
    if clip_best.get("rule") and not clip_watch_frozen:
        recommendations.append({
            "rank": 0.81,
            "action": "freeze_observable_exit_clip_separator_watch",
            "why": (
                f"The matched-unchanged exit losses split into {clip_summary.get('hold_helpful_rows')} hold-helpful, "
                f"{clip_summary.get('hold_harmful_rows')} hold-harmful, and {clip_summary.get('hold_unknown_rows')} unknown rows. "
                f"The best diagnostic observable separator is {clip_best.get('rule')} with "
                f"{clip_best.get('helpful_rows')}/{clip_best.get('harmful_rows')} helpful/harmful known rows and "
                f"{clip_best.get('known_hold_delta_cents')}c known hold delta. Freeze this as a forward watch before "
                "broadening live exits."
            ),
            "evidence": {
                "exit_clip_separator": exit_clip,
                "exit_clip_separator_watch": exit_clip_watch,
            },
        })
    if exit_clip_watch:
        recommendations.append({
            "rank": 0.815,
            "action": "collect_exit_clip_separator_watch_rows",
            "why": (
                "The fair-drawdown/p_hold clip separator is now frozen as a forward watch. "
                f"It froze at {clip_watch_state.get('freeze_ts_utc')} and currently has "
                f"{exit_clip_watch.get('post_freeze_matched_unchanged_rows')} post-freeze matched rows "
                f"and selected {clip_watch_summary.get('rows')} row(s), so it needs fresh rows before any exit-stack use. "
                f"Opportunity audit shows selected helpful/harmful/unknown "
                f"{clip_opp_selected.get('helpful_rows')}/{clip_opp_selected.get('harmful_rows')}/{clip_opp_selected.get('unknown_rows')} "
                f"with {clip_opp_selected.get('known_hold_delta_cents')}c known delta, and "
                f"{exit_clip_opportunity.get('near_miss_rows')} near-miss row(s) with "
                f"{clip_opp_near.get('known_hold_delta_cents')}c known delta."
            ),
            "evidence": {
                "exit_clip_separator_watch": exit_clip_watch,
                "exit_clip_separator_opportunity": exit_clip_opportunity,
            },
        })
    if clip_replay_diag:
        recommendations.append({
            "rank": 0.817,
            "action": "treat_exit_clip_replay_as_mechanism_until_forward_rows_arrive",
            "why": (
                "The full replay of the frozen exit-reduce rows shows the clip separator is not just a loss-subset artifact: "
                f"diagnostic W/L moves from {clip_replay_diag.get('current_wins')}/{clip_replay_diag.get('current_losses')} "
                f"to {clip_replay_diag.get('candidate_wins')}/{clip_replay_diag.get('candidate_losses')}, net moves from "
                f"{clip_replay_diag.get('current_net_cents')}c to {clip_replay_diag.get('candidate_net_cents')}c, and losses fall by "
                f"{clip_replay_diag.get('loss_count_reduction')}. Keep it non-deployable because post-watch rows are "
                f"{clip_replay_post.get('rows', 0)} and diagnostic replay still has "
                f"{clip_replay_diag.get('suppressed_losers')} suppressed losers."
            ),
            "evidence": {
                "exit_clip_separator_replay": exit_clip_replay,
            },
        })
    if gap_summary:
        recommendations.append({
            "rank": 0.82,
            "action": "separate_exit_repair_denominator_gap_from_strategy_gap",
            "why": (
                f"The exit-repair gap classifier says {gap_summary.get('unresolved_rows')} of "
                f"{gap_summary.get('loss_rows')} losing rows remain unresolved: "
                f"{gap_summary.get('no_exit_repair_observation_rows')} have no frozen exit-repair observation "
                f"({gap_summary.get('no_exit_repair_observation_pre_first_freeze_rows')} predate the first exit-repair freeze) and "
                f"{gap_summary.get('matched_but_unchanged_rows')} are matched but unchanged. The observable post-birth "
                f"loss-control watch has only {gap_summary.get('observable_post_birth_probability_reduce_rows')} "
                "probability-reduce row and its first would-suppress row is harmful, so new exit work should first "
                "separate pre-freeze history from true collapse/value-exit states rather than broadening suppression."
            ),
            "evidence": exit_gap,
        })
    separator_full = (matched_separator.get("full_denominator_rule_audits") or [{}])[0]
    separator_loss = (matched_separator.get("top_clean_rules") or [{}])[0]
    matched_guard_state = matched_guard_watch.get("state") if isinstance(matched_guard_watch.get("state"), dict) else {}
    matched_guard_post = matched_guard_watch.get("post_freeze_summary") if isinstance(matched_guard_watch.get("post_freeze_summary"), dict) else {}
    matched_guard_diag = matched_guard_watch.get("diagnostic_summary") if isinstance(matched_guard_watch.get("diagnostic_summary"), dict) else {}
    if matched_guard_state.get("freeze_ts_utc"):
        opportunity_note = ""
        if matched_guard_opportunity:
            opportunity_note = (
                f" Opportunity audit has {matched_guard_opportunity.get('post_freeze_rows')} post-freeze scored rows, "
                f"{matched_guard_opportunity.get('selected_rows')} selected rows, "
                f"{matched_guard_opportunity.get('near_miss_rows')} near-miss rows, and fail reasons "
                f"{matched_guard_opportunity.get('fail_reason_counts')}."
            )
        recommendations.append({
            "rank": 0.823,
            "action": "collect_matched_unchanged_loss_guard_watch_rows",
            "why": (
                "The matched-unchanged separator now has a guarded frozen watch, so the next step is strict post-freeze collection, not another diagnostic freeze. "
                f"It froze at {matched_guard_state.get('freeze_ts_utc')} and currently has "
                f"{matched_guard_post.get('rows')} post-freeze scored row(s), selected {matched_guard_post.get('selected_rows')} row(s), "
                f"{matched_guard_post.get('helpful_rows')}/{matched_guard_post.get('harmful_rows')} helpful/harmful, "
                f"{matched_guard_post.get('delta_vs_current_cents')}c delta, and blockers {matched_guard_post.get('blockers')}. "
                f"Diagnostic context was {matched_guard_diag.get('selected_rows')} selected with "
                f"{matched_guard_diag.get('helpful_rows')}/{matched_guard_diag.get('harmful_rows')} helpful/harmful and "
                f"{matched_guard_diag.get('selected_hold_delta_cents')}c selected hold delta, but those rows are pre-freeze only."
                f"{opportunity_note}"
            ),
            "evidence": {
                "matched_unchanged_loss_separator": matched_separator,
                "matched_unchanged_loss_guard_watch": matched_guard_watch,
                "matched_unchanged_loss_guard_opportunity": matched_guard_opportunity,
            },
        })
    elif separator_full.get("rule"):
        recommendations.append({
            "rank": 0.823,
            "action": "treat_matched_unchanged_loss_separator_as_guarded_watch_hypothesis_only",
            "why": (
                "A diagnostic observable separator for matched-but-unchanged losses is promising but not clean enough to freeze blindly. "
                f"On loss rows, {separator_loss.get('rule')} selected {separator_loss.get('selected_rows')} rows with "
                f"{separator_loss.get('helpful_rows')}/{separator_loss.get('harmful_rows')} helpful/harmful and "
                f"{separator_loss.get('hold_delta_cents')}c hold delta. On the full scored-exit denominator it selected "
                f"{separator_full.get('selected_rows')} rows with {separator_full.get('helpful_rows')}/"
                f"{separator_full.get('harmful_rows')} helpful/harmful, {separator_full.get('hold_delta_cents')}c delta, "
                f"and worst harm {separator_full.get('worst_harm_cents')}c. The physical idea is rich-ish exits near the boundary "
                "can clip winners, but the harmful rows are still FV/entry failures, so this needs an additional guard before any watch freeze."
            ),
            "evidence": matched_separator,
        })
    if residual_child:
        lanes = {row.get("label"): row for row in residual_child.get("lanes") or []}
        post = lanes.get("post_child_birth") or {}
        path_lanes = {row.get("label"): row for row in residual_child_path_risk.get("lanes") or []}
        post_path = path_lanes.get("post_child_birth") or {}
        path_note = ""
        if post_path:
            path_note = (
                f" Path-risk audit matched {post_path.get('rows_with_path')}/"
                f"{post_path.get('child_suppressed')} strict child rows, worst adverse vs exit "
                f"{post_path.get('worst_adverse_vs_exit_cents')}c, adverse 10/25/50 rows "
                f"{post_path.get('adverse_10c_rows')}/{post_path.get('adverse_25c_rows')}/"
                f"{post_path.get('adverse_50c_rows')}, below-zero marks "
                f"{post_path.get('mark_below_zero_rows')}, and blockers {post_path.get('blockers')}."
            )
        false_hold_note = ""
        false_summary = residual_child_false_hold.get("strict_lane_summary") or {}
        harmful_summary = residual_child_false_hold.get("harmful_summary") or {}
        if false_summary:
            false_hold_note = (
                " False-hold autopsy adds blockers "
                f"{false_summary.get('autopsy_blockers')}; harmful rows are "
                f"{harmful_summary.get('rows')} rows for {harmful_summary.get('net_child_delta_cents')}c, "
                f"markets {harmful_summary.get('market_counts')}, reasons "
                f"{harmful_summary.get('exit_reason_counts')}, p-hold bands "
                f"{harmful_summary.get('p_hold_band_counts')}."
            )
        guard_note = ""
        clean_guards = residual_child_guards.get("clean_strict_variants") or []
        if clean_guards:
            best_guard = clean_guards[0]
            guard_note = (
                " Guardrail scan best clean strict variant is "
                f"{best_guard.get('variant')} with {best_guard.get('child_suppressed')} child suppressions, "
                f"helpful/harmful {best_guard.get('child_helpful')}/{best_guard.get('child_harmful')}, "
                f"child delta {best_guard.get('child_delta_vs_parent_cents')}c, candidate net "
                f"{best_guard.get('candidate_net_cents')}c, and blockers {best_guard.get('blockers')}. "
                "Treat this as a child-repair hypothesis requiring its own freeze, not promotion evidence."
            )
        recommendations.append({
            "rank": 0.826,
            "action": "collect_common_clock_residual_child_rows",
            "why": (
                "The residual exit70-79 child is now producing strict post-birth evidence, but it is still a sample wait: "
                f"{post.get('settled')} settled, {post.get('child_suppressed')} child suppressions, "
                f"helpful/harmful {post.get('child_helpful')}/{post.get('child_harmful')}, "
                f"child delta {post.get('child_delta_vs_parent_cents')}c, candidate net {post.get('candidate_net_cents')}c, "
                f"and blockers {post.get('blockers')}. Treat it as a promising clipped-winner residual watch, not an exit change."
                f"{path_note}"
                f"{false_hold_note}"
                f"{guard_note}"
            ),
            "evidence": {
                "exit_common_clock_residual_child_watch": residual_child,
                "exit_common_clock_residual_child_path_risk": residual_child_path_risk,
                "exit_common_clock_residual_child_false_hold_autopsy": residual_child_false_hold,
                "exit_common_clock_residual_child_guardrail_variants": residual_child_guards,
            },
        })
    if residual_child_book_gap_guard:
        guard_state = residual_child_book_gap_guard.get("state") or {}
        guard_lanes = {row.get("lane"): row for row in residual_child_book_gap_guard.get("lanes") or []}
        strict_guard = guard_lanes.get("post_book_gap_guard_birth") or {}
        diag_guard = guard_lanes.get("diagnostic_v2_common_clock_context") or {}
        recommendations.append({
            "rank": 0.827,
            "action": "collect_residual_child_book_gap_guard_watch_rows",
            "why": (
                "The book-gap residual child guard has its own freeze now, so only rows after "
                f"{guard_state.get('freeze_ts_utc')} count. Diagnostic v2 context selected "
                f"{diag_guard.get('child_suppressed')} child suppressions with helpful/harmful "
                f"{diag_guard.get('child_helpful')}/{diag_guard.get('child_harmful')} and child delta "
                f"{diag_guard.get('child_delta_vs_parent_cents')}c, but post-birth strict evidence is "
                f"{strict_guard.get('settled')} settled, {strict_guard.get('child_suppressed')} child suppressions, "
                f"helpful/harmful {strict_guard.get('child_helpful')}/{strict_guard.get('child_harmful')}, "
                f"child delta {strict_guard.get('child_delta_vs_parent_cents')}c, candidate net "
                f"{strict_guard.get('candidate_net_cents')}c, blockers {strict_guard.get('blockers')}. "
                "Treat it as an empty/immature child-repair watch, not as inherited evidence from the failed base child."
            ),
            "evidence": {
                "exit_common_clock_residual_child_book_gap_guard_watch": residual_child_book_gap_guard,
            },
        })
    true_loser_summary = true_loser_hold_risk.get("summary") or {}
    true_loser = true_loser_summary.get("true_loser") or {}
    clipped_winner = true_loser_summary.get("clipped_winner") or {}
    avoid_tags = true_loser_hold_risk.get("avoid_broad_hold_tags") or []
    if true_loser_summary:
        tag_names = [row.get("tag") for row in avoid_tags[:5]]
        recommendations.append({
            "rank": 0.824,
            "action": "use_true_loser_hold_risk_as_exit_suppression_guardrail",
            "why": (
                "The exit-repair denominator has a real false-hold risk, not just clipped winners. "
                f"True-loser/FV-entry rows would lose {true_loser.get('hold_delta_cents')}c if held across "
                f"{true_loser.get('rows')} rows, while clipped-winner rows would gain {clipped_winner.get('hold_delta_cents')}c "
                f"across {clipped_winner.get('rows')} rows. Avoid broad hold rules around tags {tag_names} unless a strict "
                "post-freeze watch proves the guard avoids FV/entry losers."
            ),
            "evidence": true_loser_hold_risk,
        })
    false_hold_summary = false_hold_bridge.get("summary") or {}
    if false_hold_summary:
        recommendations.append({
            "rank": 0.825,
            "action": "require_false_hold_guardrails_in_exit_watch_review",
            "why": (
                "Strict harmful suppressions identify the concrete false-hold states promotion reviews must reject. "
                f"The strict common-clock windows show {false_hold_bridge.get('strict_harmful_suppressions')} harmful suppressions "
                f"for {false_hold_bridge.get('strict_net_harm_cents')}c, with top guardrail tags "
                f"{false_hold_summary.get('top_guardrail_tags')}. Candidate exit watches should show they avoid these states "
                "before clipped-winner recovery is trusted."
            ),
            "evidence": false_hold_bridge,
        })
    collapse_summary = collapse_shadow.get("summary") or {}
    if collapse_summary:
        recommendations.append({
            "rank": 0.85,
            "action": "do_not_broaden_collapse_exit_suppression_without_new_evidence",
            "why": (
                "The refreshed forward collapse-suppression registry says holding registered collapse exits would have hurt, "
                f"with suppress delta {collapse_summary.get('suppress_exit_delta_dollars')}$ over {collapse_summary.get('registered')} registered rows."
            ),
            "evidence": {
                "collapse_suppress_shadow": collapse_shadow,
                "collapse_reentry_registry": collapse_reentry,
            },
        })
    if (as_float(reduce_lane.get("delta_vs_current_cents")) or 0.0) > 0:
        suppressed = as_float(reduce_lane.get("suppressed_exits")) or 0.0
        blockers = reduce_lane.get("blockers") or []
        geometry_opportunity = (report.get("exit_reduce_geometry_opportunity") or {}).get("summary") or {}
        actionability = report.get("exit_reduce_actionability") or {}
        drift_audit = report.get("exit_reduce_drift_audit") or {}
        if suppressed < 30:
            why = (
                "It is the only frozen exit lane currently showing positive forward delta, "
                f"but it has only {suppressed:.0f} suppressed-exit decisions; keep collecting loss-control evidence."
            )
        elif blockers:
            why = (
                "It has enough settled markets and positive forward delta, but loss-control/readiness blockers remain: "
                + ", ".join(str(blocker) for blocker in blockers[:3])
            )
        else:
            why = "It has positive forward delta; keep watching for loss-control invalidators before promotion."
        recommendations.append({
            "rank": 1,
            "action": "keep_collecting_exit_reduce_suppression",
            "why": why,
            "evidence": {
                "runway": report.get("exit_reduce_runway") or reduce_lane,
                "actionability": actionability,
                "drift_audit": drift_audit,
                "geometry_opportunity": geometry_opportunity,
            },
        })
        drift_overall = drift_audit.get("overall") or {}
        latest_suppression = drift_audit.get("latest_suppression") or {}
        drift_guard_watch = report.get("exit_reduce_drift_guard_watch") or {}
        drift_guard_diag = (drift_guard_watch.get("diagnostic_since_base_freeze") or [{}])[0]
        drift_guard_post = (drift_guard_watch.get("post_drift_guard_birth") or [{}])[0]
        if (as_float(drift_overall.get("harmful_delta_cents")) or 0.0) < 0.0:
            recommendations.append({
                "rank": 1.08,
                "action": "isolate_recent_reduce_suppression_harm_before_broadening",
                "why": (
                    "The reduce-suppression aggregate is still positive, but the drift audit shows "
                    f"{drift_overall.get('harmful_rows')} harmful suppressed rows for "
                    f"{drift_overall.get('harmful_delta_cents')}c, with the latest suppression "
                    f"adding {latest_suppression.get('delta_cents')}c. Treat loss-control cost as a "
                    "physical failure mode, not a harmless sample artifact."
                ),
                "evidence": drift_audit,
            })
        if drift_guard_watch:
            recommendations.append({
                "rank": 1.09,
                "action": "collect_drift_guarded_reduce_suppression_forward_rows",
                "why": (
                    f"The frozen drift-guard watch converted the diagnostic blanket suppressor into "
                    f"{drift_guard_diag.get('policy')} with {drift_guard_diag.get('suppressed_helpful')}/"
                    f"{drift_guard_diag.get('suppressed_harmful')} suppressed W/L and "
                    f"{drift_guard_diag.get('delta_vs_current_cents')}c, but its own post-birth rows are "
                    f"{drift_guard_post.get('settled')} settled with {drift_guard_post.get('suppressed')} suppressions. "
                    "Treat it as a clean mechanism watch only."
                ),
                "evidence": drift_guard_watch,
            })
        if (as_float(geometry_opportunity.get("geometry_rejected_base_delta_cents")) or 0.0) > 0:
            relaxed_watch = report.get("exit_reduce_geometry_relaxed_watch") or {}
            relaxed_summary = relaxed_watch.get("summary") or {}
            recommendations.append({
                "rank": 1.5,
                "action": "downgrade_side_geometry_until_it_stops_rejecting_positive_base_opportunities",
                "why": "The side-geometry repair removed diagnostic harmful rows, but its frozen opportunity audit rejected the first positive base p-hold suppression; keep it as a warning signal until forward rows prove it is not too strict.",
                "evidence": geometry_opportunity,
            })
            recommendations.append({
                "rank": 1.55,
                "action": "collect_relaxed_geometry_guard_forward_rows",
                "why": (
                    "A frozen child watch now tests the smallest observed relaxation: side-geometry suppressions plus "
                    "NO-side sign-disagree cases where the current probability-reduce exit is already a deep realized loss. "
                    f"It has {relaxed_summary.get('settled')} strict settled rows and must prove itself after its own freeze."
                ),
                "evidence": relaxed_watch,
            })
    if midband_rescue:
        best_diag = (midband_rescue.get("diagnostic") or [{}])[0]
        best_post = (midband_rescue.get("post_birth") or [{}])[0]
        recommendations.append({
            "rank": 1.57,
            "action": "collect_midband_reduce_rescue_forward_rows",
            "why": (
                "A frozen watch now tests the lower-p_hold probability-reduce clip mechanism. "
                f"Diagnostic best {best_diag.get('candidate')} has delta {best_diag.get('delta_vs_current_cents')}c "
                f"on {best_diag.get('suppressed')} suppressions with {best_diag.get('helpful_suppressions')}/"
                f"{best_diag.get('harmful_suppressions')} helpful/harmful, but strict post-birth rows are "
                f"{best_post.get('rows')} with blockers {best_post.get('blockers')}. Treat as watch-only."
            ),
            "evidence": midband_rescue,
        })
    recommendations.append({
        "rank": 2,
        "action": "watch_book_gap_soft_exit_validator",
        "why": "Discovery signal was large, but the frozen validator has to earn future rows before it can inform live exits.",
        "evidence": book_gap_lane,
    })
    recommendations.append({
        "rank": 2.2,
        "action": "collect_loss_guarded_book_gap_forward_rows",
        "why": "This new frozen lane keeps the book-gap upside while requiring a real held-side book advantage before suppressing probability-reduce exits.",
        "evidence": book_gap_loss_guard_lane,
    })
    recommendations.append({
        "rank": 2.25,
        "action": "collect_loss_guarded_book_gap_v2_forward_rows",
        "why": "The stricter v2 lane gives up some upside but removes the current diagnostic suppressed-loss cost by rejecting deep negative-gap value-over-hold suppressions.",
        "evidence": {
            "lane": book_gap_loss_guard_v2_lane,
            "opportunity": report.get("exit_book_gap_loss_guard_v2_opportunity") or {},
            "runway": report.get("exit_loss_guard_v1_v2_runway") or {},
        },
    })
    recommendations.append({
        "rank": 2.255,
        "action": "collect_loss_guarded_book_gap_v3_extreme_p_forward_rows",
        "why": "V3 tests the smallest creative relaxation of v2: allow only extreme p_hold>=0.95 value-exit holds while keeping the rich-exit/negative-gap protection that avoided strict-forward harm.",
        "evidence": {
            "lane": book_gap_loss_guard_v3_lane,
            "opportunity": report.get("exit_book_gap_loss_guard_v3_opportunity") or {},
            "v1_v2_v3_contrast": report.get("exit_loss_guard_v1_v2_v3_contrast") or {},
            "strict_failure_drilldown": report.get("exit_strict_failure_drilldown") or {},
        },
    })
    recommendations.append({
        "rank": 2.27,
        "action": "track_value_only_book_gap_denominator",
        "why": "The value-only freeze isolates value-over-hold clipping from probability-reduce state warnings; the opportunity denominator shows whether the zero-row strict scorecard is sample scarcity or rule scarcity.",
        "evidence": {
            "lane": book_gap_value_only_lane,
            "opportunity": report.get("exit_book_gap_value_only_opportunity") or {},
        },
    })
    recommendations.append({
        "rank": 2.28,
        "action": "track_value_reduce_depth_composite_denominator",
        "why": "The value/reduce-depth composite is the cleanest diagnostic exit stack so far, but it has to prove post-freeze suppressible opportunities by mechanism before promotion.",
        "evidence": {
            "lane": exit_value_reduce_depth_lane,
            "opportunity": report.get("exit_value_reduce_depth_opportunity") or {},
        },
    })
    recommendations.append({
        "rank": 2.29,
        "action": "collect_observable_reduce_loss_control_forward_rows",
        "why": "Observable reduce-loss-control variants now have a separate frozen watch; the best diagnostic union removed suppressed losers, but post-birth rows have not produced suppressible probability-reduce opportunities yet.",
        "evidence": {
            "lane": observable_loss_control_lane,
            "opportunity": report.get("exit_reduce_observable_loss_control_opportunity") or {},
        },
    })
    common_clock = report.get("exit_common_clock") or {}
    common_clock_runway = report.get("exit_common_clock_runway") or {}
    strict_failure = report.get("exit_strict_failure_drilldown") or {}
    common_clock_best_runway = (common_clock_runway.get("rows") or [{}])[0]
    strict_windows = [
        row for row in common_clock.get("windows") or []
        if str(row.get("window") or "").startswith("new_exit_mix_common_forward")
    ]
    comparable_window = next(
        (row for row in common_clock.get("windows") or [] if row.get("window") == "book_gap_freeze_comparable"),
        {},
    )
    recommendations.append({
        "rank": 2.3,
        "action": "judge_exit_repairs_on_common_clock_window",
        "why": (
            "The common-clock report is the clean apples-to-apples promotion surface for reduce/book-gap/loss-guard/dual exits; "
            "the v1/v2/v3 strict windows have to fill before any live-test decision. The closest strict row is "
            f"{common_clock_best_runway.get('window')} / {common_clock_best_runway.get('policy')} with "
            f"{common_clock_best_runway.get('settled')} settled, {common_clock_best_runway.get('suppressed_exits')} suppressions, "
            f"{fmt(common_clock_best_runway.get('candidate_gross_cents'))}c net, and "
            f"{fmt(common_clock_best_runway.get('delta_vs_current_cents'))}c delta; it still needs "
            f"{common_clock_best_runway.get('suppressed_decisions_needed')} suppressions and "
            f"{fmt(common_clock_best_runway.get('net_cents_needed_for_cushion3'))}c cushion."
        ),
        "evidence": {
            "strict_forward_windows": common_clock.get("strict_forward_windows"),
            "strict_windows": strict_windows,
            "runway": common_clock_runway,
            "comparable_best": (comparable_window.get("summaries") or [{}])[0],
            "strict_failure_drilldown": {
                "strict_harmful_suppressions": strict_failure.get("strict_harmful_suppressions"),
                "strict_net_harm_cents": strict_failure.get("strict_net_harm_cents"),
                "interpretation": strict_failure.get("interpretation"),
            },
        },
    })
    recommendations.append({
        "rank": 2.5,
        "action": "collect_dual_exit_book_gap_else_reduce_forward_rows",
        "why": "The mix/match composite is now frozen from its own timestamp; do not rely on the diagnostic +990c union until this lane earns post-freeze rows.",
        "evidence": dual_exit_lane,
    })
    best_target = next((row for row in report["best_candidates"] if 75.0 <= (as_float(row.get("coverage_pct")) or -1.0) <= 90.0), None)
    if best_target and (as_float(best_target.get("net_cents")) or 0.0) <= 0.0:
        recommendations.append({
            "rank": 3,
            "action": "debug_negative_pnl_on_best_target_coverage_candidate",
            "why": "Coverage-compatible candidates still fail profitability; the next model work should explain these losses physically before adding new knobs.",
            "evidence": best_target,
        })
    target_loss = report.get("target_loss_attribution") or {}
    worst_tags = [
        row for row in target_loss.get("tag_summaries") or []
        if row.get("tag") != "all" and int(row.get("settled") or 0) >= 3
    ][:5]
    if worst_tags:
        recommendations.append({
            "rank": 3.5,
            "action": "prioritize_target_coverage_loss_tags",
            "why": "The next entry/FV work should explain these repeated losing physical states before adding broader exposure.",
            "evidence": worst_tags,
        })
    cluster_runway = report.get("target_cluster_penalty_runway") or {}
    post_cluster = cluster_runway.get("post_birth_runway") or {}
    if post_cluster:
        source_feasibility = report.get("target_cluster_penalty_source_feasibility") or {}
        feasibility_lanes = source_feasibility.get("lanes") or []
        feasibility_post = next((row for row in feasibility_lanes if row.get("lane") == "post_cluster_penalty_birth"), {})
        displacement = report.get("target_cluster_penalty_source_displacement") or {}
        displacement_lanes = displacement.get("lanes") or []
        displacement_post = next((row for row in displacement_lanes if row.get("lane") == "post_cluster_penalty_birth"), {})
        recommendations.append({
            "rank": 3.6,
            "action": "collect_clean_cluster_penalty_forward_rows",
            "why": "The continuous cluster-penalty repair is now post-birth positive at target coverage, but it is too reconstructed-heavy and fragile to promote.",
            "evidence": {
                "runway": post_cluster,
                "source_feasibility": feasibility_post.get("best") or {},
                "source_displacement": displacement_post.get("best") or {},
            },
        })
    source_aware = report.get("target_cluster_penalty_source_aware") or {}
    source_aware_lanes = source_aware.get("lanes") or []
    source_aware_diag = next((row for row in source_aware_lanes if row.get("lane") == "diagnostic_target_window"), {})
    source_aware_post = next((row for row in source_aware_lanes if row.get("lane") == "post_source_aware_birth"), {})
    source_aware_diag_best = (source_aware_diag.get("variants") or [{}])[0]
    source_aware_post_best = (source_aware_post.get("variants") or [{}])[0]
    if source_aware:
        recommendations.append({
            "rank": 3.65,
            "action": "collect_source_aware_cluster_penalty_forward_rows",
            "why": "The new source-aware stress almost cleans the diagnostic broad-entry cluster while staying positive, but strict post-birth evidence is still immature and the source label itself is research-only.",
            "evidence": {
                "diagnostic_cleanest": source_aware_diag_best,
                "post_source_aware_birth": source_aware_post_best,
            },
        })
    observable_stability = report.get("target_cluster_penalty_observable_stability") or {}
    observable_lanes = observable_stability.get("lanes") or []
    observable_diag = next((row for row in observable_lanes if row.get("lane") == "diagnostic_target_window"), {})
    observable_post = next((row for row in observable_lanes if row.get("lane") == "post_observable_proxy_birth"), {})
    observable_diag_best = (observable_diag.get("variants") or [{}])[0]
    observable_post_best = (observable_post.get("variants") or [{}])[0]
    if observable_stability:
        recommendations.append({
            "rank": 3.66,
            "action": "watch_observable_cluster_stability_proxy_without_promotion",
            "why": "The observable-only stability proxy translates the source-displacement clue into live-usable features, but diagnostic evidence still misses the source and full-loss cushion gates and strict post-birth evidence is still immature.",
            "evidence": {
                "diagnostic_best": observable_diag_best,
                "post_observable_proxy_birth": observable_post_best,
            },
        })
    clean_broad_frontier = report.get("feature_gate_clean_broad_frontier") or {}
    clean_broad_lanes = clean_broad_frontier.get("lanes") or []
    clean_broad_post = [
        row for row in clean_broad_lanes
        if isinstance(row, dict) and str(row.get("lane") or "").startswith("post_clean_broad_freeze_")
    ]
    if clean_broad_post:
        best_clean_broad_post = clean_broad_post[0]
        best_clean_broad_summary = best_clean_broad_post.get("candidate_summary") or {}
        settled = int(as_float(best_clean_broad_summary.get("settled")) or 0)
        pending = int(as_float(best_clean_broad_post.get("pending_unsettled_rows")) or 0)
        recommendations.append({
            "rank": 3.67,
            "action": "collect_clean_broad_feature_gate_forward_rows",
            "why": (
                "The soft clean-broad feature-gate rule was frozen after discovery, so only new post-freeze rows count; "
                f"it currently has {settled} settled strict row(s) and {pending} pending unsettled row(s)."
            ),
            "evidence": clean_broad_post,
        })
    soft_stack = report.get("feature_gate_soft_frontier_exit_stack") or {}
    if soft_stack:
        recommendations.append({
            "rank": 3.68,
            "action": "collect_soft_frontier_exit_stack_forward_rows",
            "why": "This freezes the broad clean feature-gate entry rule with guarded exits from its own timestamp; it is the correct mix/match watch for target coverage, but has no post-freeze joined exits yet.",
            "evidence": {
                "freeze": soft_stack.get("freeze"),
                "exit_rows_available": soft_stack.get("exit_rows_available"),
                "candidate_live_ready": soft_stack.get("candidate_live_ready"),
            },
        })
    cheap_tail_shrink = report.get("feature_gate_cheap_tail_shrink_watch") or {}
    if cheap_tail_shrink:
        entry_lane = next(
            (
                lane
                for lane in cheap_tail_shrink.get("lanes") or []
                if isinstance(lane, dict) and lane.get("lane") == "post_cheap_tail_shrink_birth_entry"
            ),
            {},
        )
        best_policy = (entry_lane.get("policies") or [{}])[0]
        recommendations.append({
            "rank": 3.685,
            "action": "collect_feature_gate_cheap_tail_shrink_forward_rows",
            "why": (
                "The broad feature-gate row is positive but source-fragile because cheap tail rows add coverage and depend on a large "
                "reconstructed payoff. This new watch freezes continuous notional shrinkage on cheap tails from its own timestamp; "
                "post-birth evidence is currently immature."
            ),
            "evidence": {
                "freeze": cheap_tail_shrink.get("state"),
                "best_policy": best_policy,
            },
        })
    near_promotion = report.get("feature_gate_near_promotion_watch") or {}
    near_attr = report.get("feature_gate_near_promotion_exit_attribution") or {}
    near_gap = report.get("feature_gate_near_promotion_denominator_gap") or {}
    if near_promotion:
        best_near = (near_promotion.get("rows") or [{}])[0]
        recommendations.append({
            "rank": 3.686,
            "action": "collect_feature_gate_near_promotion_forward_denominator_rows",
            "why": (
                f"The nearest broad feature-gate candidate is {near_promotion.get('best_candidate')} "
                f"with {best_near.get('settled')} settled, {fmt(best_near.get('coverage_pct'))}% coverage, "
                f"{fmt(best_near.get('net_cents'))}c net, W/L {best_near.get('wins')}/{best_near.get('losses')}, "
                f"and {fmt(best_near.get('reconstructed_share'))} reconstructed share. "
                f"It needs {best_near.get('coverage_entries_needed')} coverage row(s), "
                f"{best_near.get('clean_rows_needed_for_source') or 0} clean-source dilution row(s), and "
                f"{fmt(best_near.get('net_cents_needed_for_cushion3'))}c of cushion before live testing. "
                "The denominator-gap audit says omitted rows are rejected-actionable source rows, so this should be "
                "closed by fresh qualifying forward markets, not by relaxing the frozen rule."
            ),
            "evidence": {
                "watch": {
                    "best_candidate": near_promotion.get("best_candidate"),
                    "best_missing_gates": near_promotion.get("best_missing_gates"),
                    "best_row": best_near,
                },
                "exit_attribution": {
                    "loss_source_counts": near_attr.get("loss_source_counts"),
                    "failure_class_counts": near_attr.get("failure_class_counts"),
                },
                "denominator_gap": {
                    "coverage_entries_needed": near_gap.get("coverage_entries_needed"),
                    "omitted_fail_reason_counts": near_gap.get("omitted_fail_reason_counts"),
                    "omitted_source_counts": near_gap.get("omitted_source_counts"),
                    "counterfactual_source_gate": (
                        near_gap.get("top_counterfactual_added_omitted_rows") or {}
                    ).get("source_gate_if_added"),
                },
            },
        })
    if feature_gate_raw05_gap or feature_gate_raw03_vs_raw05 or feature_gate_quick_status or feature_gate_joint_gap:
        joint_best = feature_gate_joint_gap.get("best_by_lane") or {}
        joint_raw05_entry = joint_best.get("post_feature_freeze_entry") or {}
        joint_raw05_bridge = joint_best.get("post_feature_freeze_bridge") or {}
        raw03_current = feature_gate_gap_mechanism.get("raw03_bridge") or {}
        mechanism_attr = feature_gate_gap_mechanism.get("near_promotion_exit_attribution") or {}
        gap_lane = next(
            (
                lane for lane in feature_gate_raw05_gap.get("lanes") or []
                if lane.get("lane") == "post_feature_freeze_entry"
            ),
            {},
        )
        autopsy_lane = next(
            (
                lane for lane in feature_gate_raw03_vs_raw05.get("lanes") or []
                if lane.get("lane") == "post_feature_freeze_entry"
            ),
            {},
        )
        quick_lane = next(
            (
                lane for lane in feature_gate_quick_status.get("lanes") or []
                if lane.get("lane") == "post_feature_freeze_entry"
            ),
            {},
        )
        quick_raw05 = next(
            (
                row for row in quick_lane.get("variants") or []
                if row.get("rule") == "raw05_recross60_abs085"
            ),
            {},
        )
        quick_raw03 = next(
            (
                row for row in quick_lane.get("variants") or []
                if row.get("rule") == "raw03_recross70_abs075"
            ),
            {},
        )
        marginal = autopsy_lane.get("marginal_raw03_minus_raw05") or {}
        raw05_selected = ((autopsy_lane.get("raw05") or {}).get("summary") or {}) or gap_lane.get("raw05_selected") or {}
        any_oracle = gap_lane.get("best_any_source_oracle_add_missing") or {}
        any_oracle_summary = any_oracle.get("summary") or {}
        recommendations.append({
            "rank": 3.6865,
            "action": "do_not_repair_feature_gate_raw05_gap_with_raw03_relaxation",
            "why": (
                "The current-denominator feature-gate gap says raw03 relaxation is not a real repair. "
                f"raw05 bridge is cleaner with {joint_raw05_bridge.get('entries')} entries, "
                f"{fmt(joint_raw05_bridge.get('coverage_pct'))}% coverage, "
                f"{fmt(joint_raw05_bridge.get('net_cents'))}c net, reconstructed share "
                f"{fmt(joint_raw05_bridge.get('reconstructed_share'))}, cushion "
                f"{joint_raw05_bridge.get('full_loss_cushion')}, and live-snapshot gap "
                f"{fmt(joint_raw05_bridge.get('cents_needed_to_match_live_snapshot'))}c. "
                f"raw05 entry is similar but weaker at {joint_raw05_entry.get('entries')} entries, "
                f"{fmt(joint_raw05_entry.get('coverage_pct'))}% coverage, "
                f"{fmt(joint_raw05_entry.get('net_cents'))}c, cushion "
                f"{joint_raw05_entry.get('full_loss_cushion')}. "
                f"raw03 bridge reaches {fmt(raw03_current.get('coverage_pct'))}% coverage, but source share "
                f"{fmt(raw03_current.get('reconstructed_share'))}, cushion "
                f"{raw03_current.get('full_loss_cushion')}, and live-snapshot gap "
                f"{fmt(raw03_current.get('cents_needed_to_match_live_snapshot'))}c keep it blocked. "
                f"The mechanism synthesis says raw05 bridge losses are "
                f"{mechanism_attr.get('failure_class_counts') or {}} with source counts "
                f"{mechanism_attr.get('loss_source_counts') or {}}; approved losses were exit-helped, "
                "so broad exit suppression is not the missing repair. "
                f"The raw03-only marginal slice adds {(marginal.get('summary') or {}).get('entries')} rows, "
                f"all from {marginal.get('source_counts')}, with W/L "
                f"{marginal.get('wins')}/{marginal.get('losses')} and "
                f"{fmt(marginal.get('net_cents'))}c. "
                f"The best any-source oracle reaches {fmt(any_oracle_summary.get('coverage_pct'))}% coverage only by adding "
                f"{any_oracle.get('added_source_counts')}, leaving reconstructed share "
                f"{fmt(any_oracle_summary.get('reconstructed_share'))}. "
                "This closes the simple-relaxation path; wait for clean forward rows or freeze a true observable quality proxy."
            ),
            "evidence": {
                "quick_raw05": quick_raw05,
                "quick_raw03": quick_raw03,
                "joint_raw05_entry": joint_raw05_entry,
                "joint_raw05_bridge": joint_raw05_bridge,
                "joint_raw03_bridge": raw03_current,
                "gap_mechanism": {
                    "conclusion": feature_gate_gap_mechanism.get("conclusion"),
                    "near_promotion_exit_attribution": mechanism_attr,
                    "exit_state_frontier_best": feature_gate_gap_mechanism.get("exit_state_frontier_best"),
                },
                "raw03_vs_raw05_entry": autopsy_lane,
                "raw05_gap_entry": gap_lane,
            },
        })
    core_expansion = report.get("feature_gate_core_expansion_mix") or {}
    if core_expansion:
        best_mix = (core_expansion.get("rows") or [{}])[0]
        recommendations.append({
            "rank": 3.687,
            "action": "do_not_promote_core_expansion_mix_yet",
            "why": (
                "The strict-core plus broad-expansion mix was tested as a physical dual strategy. "
                f"Best weighted policy {best_mix.get('policy')} has {best_mix.get('entries')} entries and {best_mix.get('settled')} settled, "
                f"{fmt(best_mix.get('coverage_pct'))}% coverage, {fmt(best_mix.get('weighted_net_cents'))}c weighted net, "
                f"row/exposure source {fmt(best_mix.get('row_source_share'))}/{fmt(best_mix.get('exposure_source_share'))}, "
                f"and cushion {best_mix.get('full_loss_cushion')}. It is useful evidence, but not promotable."
            ),
            "evidence": best_mix,
        })
    coverage_repair = report.get("feature_gate_coverage_repair") or {}
    if coverage_repair:
        lanes = coverage_repair.get("lanes") or []
        entry_lane = next((lane for lane in lanes if lane.get("lane") == "post_feature_freeze_entry"), {})
        bridge_lane = next((lane for lane in lanes if lane.get("lane") == "post_feature_freeze_bridge"), {})
        entry_near = (entry_lane.get("near_misses") or [{}])[0]
        bridge_near = (bridge_lane.get("near_misses") or [{}])[0]
        recommendations.append({
            "rank": 3.688,
            "action": "do_not_repair_feature_gate_coverage_by_simple_relaxation",
            "why": (
                "The coverage-repair audit found no observable relaxation that clears coverage, source quality, "
                "and full-loss cushion together. The best entry relaxation "
                f"{entry_near.get('rule')} reaches {fmt((entry_near.get('summary') or {}).get('coverage_pct'))}% coverage "
                f"but has {fmt((entry_near.get('summary') or {}).get('reconstructed_share'))} reconstructed share and "
                f"{fmt((entry_near.get('summary') or {}).get('net_cents'))}c net; its added rows net "
                f"{fmt((entry_near.get('added_summary') or {}).get('net_cents'))}c. "
                "This says the next improvement should wait for clean forward rows or use a real continuous penalty, "
                "not a broad threshold relaxation."
            ),
            "evidence": {
                "entry_near": entry_near,
                "bridge_near": bridge_near,
                "interpretation": coverage_repair.get("interpretation"),
            },
        })
    coverage_size_shrink = report.get("feature_gate_coverage_size_shrink") or {}
    coverage_size_exit_attr = report.get("feature_gate_coverage_size_shrink_exit_attribution") or {}
    coverage_size_runway = report.get("feature_gate_coverage_size_shrink_runway") or {}
    if coverage_size_shrink or feature_gate_current_margin_size:
        lanes = coverage_size_shrink.get("lanes") or []
        entry_lane = next((lane for lane in lanes if lane.get("lane") == "post_feature_freeze_entry"), {})
        best = (entry_lane.get("rows") or [{}])[0]
        proxy_best = feature_gate_current_margin_size.get("best_exposure_clean") or {}
        proxy_rows = feature_gate_current_margin_size.get("rows") or []
        proxy_raw05 = next(
            (row for row in proxy_rows if row.get("policy") == "raw05_anchor_plus_raw03_marginal_weight_0"),
            {},
        )
        attr_entry = next(
            (lane for lane in coverage_size_exit_attr.get("lanes") or [] if lane.get("lane") == "post_feature_freeze_entry"),
            {},
        )
        runway_entry = next(
            (lane for lane in coverage_size_runway.get("lanes") or [] if lane.get("lane") == "post_feature_freeze_entry"),
            {},
        )
        first_viable = runway_entry.get("first_viable_clean_scenario") or {}
        recommendations.append({
            "rank": 3.689,
            "action": "watch_feature_gate_coverage_size_shrink_source_dilution",
            "why": (
                "The historical coverage-size-shrink audit is still useful as repair shape, but the current-denominator "
                "size proxy blocks promotion. The older shrink row preserves "
                f"{fmt(best.get('coverage_pct'))}% coverage, reaches W/L {best.get('wins')}/{best.get('losses')}, "
                f"and lifts weighted net to {fmt(best.get('weighted_net_cents'))}c with cushion "
                f"{best.get('full_loss_cushion')}. The remaining blocker is row-source share "
                f"{fmt(best.get('row_reconstructed_share'))}, while exposure-source share is only "
                f"{fmt(best.get('exposure_reconstructed_share'))}. On the current denominator, best exposure-clean bridge proxy "
                f"{proxy_best.get('policy')} reaches {fmt(proxy_best.get('coverage_pct'))}% coverage, "
                f"{fmt(proxy_best.get('weighted_net_cents'))}c weighted net, cushion "
                f"{proxy_best.get('full_loss_cushion')}, and exposure-source share "
                f"{fmt(proxy_best.get('exposure_source_share'))}, but official row-source share stays "
                f"{fmt(proxy_best.get('row_source_share'))} and its delta versus the live snapshot is "
                f"{fmt(proxy_best.get('delta_vs_live_snapshot_cents'))}c. "
                f"Zeroing marginal rows restores raw05 source at {fmt(proxy_raw05.get('row_source_share'))} but coverage drops to "
                f"{fmt(proxy_raw05.get('coverage_pct'))}%. Exit attribution shows failure classes "
                f"{attr_entry.get('failure_class_counts') or {}}. Runway says it needs "
                f"{runway_entry.get('clean_selected_rows_needed_for_source')} clean selected rows; first viable "
                f"count-gate scenario averages {first_viable.get('avg_future_net_cents')}c across "
                f"{first_viable.get('future_clean_selected_rows')} future clean rows. It is still "
                f"{fmt(runway_entry.get('delta_vs_live_cents'))}c versus its stored live-baseline snapshot, "
                "so exposure sizing is risk context, not an official source or live-gap repair."
            ),
            "evidence": {
                "entry_best": best,
                "current_margin_size_proxy_best": proxy_best,
                "current_margin_size_proxy_raw05_anchor": proxy_raw05,
                "exit_attribution": attr_entry,
                "runway": runway_entry,
                "interpretation": coverage_size_shrink.get("interpretation"),
                "current_margin_size_proxy_interpretation": feature_gate_current_margin_size.get("interpretation"),
            },
        })
    size_shrink = report.get("soft_frontier_size_shrink") or {}
    if size_shrink:
        strict_lanes = [
            lane for lane in size_shrink.get("lanes") or []
            if isinstance(lane, dict) and lane.get("strict_forward")
        ]
        diagnostic_lanes = [
            lane for lane in size_shrink.get("lanes") or []
            if isinstance(lane, dict) and not lane.get("strict_forward")
        ]
        recommendations.append({
            "rank": 3.69,
            "action": "collect_soft_frontier_size_shrink_forward_rows",
            "why": (
                "A frozen size/risk overlay now tests whether broad soft-frontier entries are better handled by "
                "continuous notional shrinkage in near-boundary and mid-cheap states, instead of another hard cutoff. "
                "Diagnostic rows are strong, but post-shrink-freeze evidence is still empty."
            ),
            "evidence": {
                "freeze": size_shrink.get("state"),
                "best_diagnostic": ((diagnostic_lanes[0].get("variants") or [{}])[0] if diagnostic_lanes else {}),
                "best_strict": ((strict_lanes[0].get("variants") or [{}])[0] if strict_lanes else {}),
            },
        })
    midprice_shrink = report.get("soft_frontier_midprice_boundary_shrink") or {}
    midprice_source = report.get("soft_frontier_midprice_boundary_source_stress") or {}
    if midprice_shrink:
        strict_lanes = [
            lane for lane in midprice_shrink.get("lanes") or []
            if isinstance(lane, dict) and lane.get("strict_forward")
        ]
        diagnostic_lanes = [
            lane for lane in midprice_shrink.get("lanes") or []
            if isinstance(lane, dict) and not lane.get("strict_forward")
        ]
        stress_policies = midprice_source.get("policies") or []
        recommendations.append({
            "rank": 3.695,
            "action": "collect_midprice_boundary_shrink_forward_rows",
            "why": (
                "The quarter-size mid-price boundary overlay is the strongest broad-entry mix so far: it preserves "
                "80%+ diagnostic coverage while shrinking the repeated near-boundary loss pocket. The source-stress "
                "audit shows weighted exposure can be cleaner than row-count source share, but official promotion "
                "still needs strict post-birth rows and the row-source gate."
            ),
            "evidence": {
                "freeze": midprice_shrink.get("state"),
                "best_diagnostic": ((diagnostic_lanes[0].get("variants") or [{}])[0] if diagnostic_lanes else {}),
                "best_strict": ((strict_lanes[0].get("variants") or [{}])[0] if strict_lanes else {}),
                "best_source_stress": (stress_policies[0] if stress_policies else {}),
            },
        })
    midprice_exit_stack = report.get("soft_frontier_midprice_boundary_exit_stack") or {}
    midprice_exit_runway = report.get("soft_frontier_midprice_boundary_exit_stack_runway") or {}
    if midprice_exit_stack:
        variants = midprice_exit_stack.get("variants") or []
        best = variants[0] if variants else {}
        strict = next((row for row in variants if isinstance(row, dict) and row.get("strict_forward")), {})
        runway_best = (midprice_exit_runway.get("rows") or [{}])[0]
        recommendations.append({
            "rank": 3.697,
            "action": "collect_midprice_boundary_exit_stack_forward_rows",
            "why": (
                "The new weighted entry+exit stack says the top broad diagnostic mix can beat live on matched "
                "book-gap exit rows, but the stack is newly frozen and strict combo overlap is still essentially "
                "empty. Watch overlap density before treating the entry and exit wins as additive; the runway "
                f"currently needs {runway_best.get('post_stack_joined_rows_needed_for_sample_gate')} joined rows "
                f"and {runway_best.get('post_stack_weighted_cents_needed_for_cushion3')}c of weighted cushion."
            ),
            "evidence": {
                "freeze": midprice_exit_stack.get("freeze"),
                "best_overlap": best,
                "best_strict_overlap": strict,
                "runway_best": runway_best,
            },
        })
    midprice_dual_exit_stack = report.get("soft_frontier_midprice_boundary_dual_exit_stack") or {}
    if midprice_dual_exit_stack:
        variants = midprice_dual_exit_stack.get("variants") or []
        best = variants[0] if variants else {}
        best_strict = next((row for row in variants if isinstance(row, dict) and row.get("strict_forward")), {})
        recommendations.append({
            "rank": 3.696,
            "action": "collect_midprice_boundary_dual_exit_stack_forward_rows",
            "why": (
                "The creative book-gap/clip union is now the strongest broad diagnostic stack: "
                f"{best.get('policy')} has weighted net {best.get('weighted_candidate_cents')}c, "
                f"delta {best.get('weighted_delta_cents')}c, joined rows {best.get('joined_exit_rows')}, "
                f"and suppressed losers {best.get('suppressed_losers')}. It is watch-only because post-stack rows are "
                f"{best.get('post_stack_joined_rows')} and the diagnostic suppressed-loser warning is unresolved."
            ),
            "evidence": {
                "freeze": midprice_dual_exit_stack.get("freeze"),
                "best_overlap": best,
                "best_strict_overlap": best_strict,
            },
        })
    midprice_dual_exit_guard = report.get("soft_frontier_midprice_boundary_dual_exit_guard") or {}
    if midprice_dual_exit_guard:
        variants = midprice_dual_exit_guard.get("variants") or []
        best = variants[0] if variants else {}
        recommendations.append({
            "rank": 3.6965,
            "action": "collect_midprice_boundary_dual_exit_guard_forward_rows",
            "why": (
                "The no-boundary-suppress guard repairs the new union stack's diagnostic loss-control flaw: "
                f"{best.get('policy')} has weighted net {best.get('weighted_candidate_cents')}c, "
                f"delta {best.get('weighted_delta_cents')}c, and suppressed losers {best.get('suppressed_losers')}. "
                "It remains watch-only because all rows before the guard freeze are diagnostic and post-stack rows are empty."
            ),
            "evidence": {
                "freeze": midprice_dual_exit_guard.get("freeze"),
                "best_guard": best,
            },
        })
    if approved_valve_bridge:
        rows = approved_valve_bridge.get("rows") or []
        best = rows[0] if rows else {}
        full_rows = approved_valve_full_surface.get("rows") or []
        best_full = full_rows[0] if full_rows else {}
        full_note = ""
        if best_full:
            full_summary = best_full.get("candidate_summary") or {}
            full_note = (
                f" Full-surface replay now says best broad adapter is {best_full.get('valve')} / "
                f"{best_full.get('surface')} with {full_summary.get('net_cents')}c net, "
                f"{best_full.get('delta_vs_base_cents')}c delta vs base, reconstructed share "
                f"{best_full.get('reconstructed_share')}, and blockers {best_full.get('blockers')}."
            )
        high_gap_note = ""
        high_gap_summary = high_gap_skipped_failure_modes.get("summary") or {}
        if high_gap_summary:
            high_gap_note = (
                f" High-gap skip forensics found {high_gap_summary.get('rows')} unique skipped rows, "
                f"W/L {high_gap_summary.get('wins')}/{high_gap_summary.get('losses')}, net "
                f"{high_gap_summary.get('net_cents')}c, and all skipped rows were rejected-actionable; "
                "the +141c skipped winner argues for a soft confidence penalty rather than a hard veto."
            )
        recommendations.append({
            "rank": 3.699,
            "action": "do_not_promote_approved_entry_state_valves_without_full_surface_repair",
            "why": (
                "Frozen approved-entry-only state valves are positive forward signals on actual v28-approved rows, "
                f"with strongest policy {best.get('policy')} at {best.get('settled')} settled, "
                f"{best.get('gross_cents')}c gross, and {best.get('delta_vs_approved_control_cents')}c versus approved-entry control. "
                "They are not promotion evidence yet because the bridge marks them as approved-entry-surface-only, "
                "absent from candidate-vs-live, not live-readiness evaluated, and below the refreshed live baseline on a naive cents comparison. "
                "The adapter result confirms this is a mechanism lead, not a live-test candidate."
                f"{full_note}"
                f"{high_gap_note}"
            ),
            "evidence": {
                "approved_entry_state_valve_bridge": approved_valve_bridge,
                "approved_entry_state_valve_full_surface": approved_valve_full_surface,
                "high_gap_skipped_failure_modes": high_gap_skipped_failure_modes,
            },
        })
    if feature_gate_high_gap_shrink:
        best_lane = {}
        best_policy = {}
        for lane in feature_gate_high_gap_shrink.get("lanes") or []:
            policy = (lane.get("policies") or [{}])[0]
            if not best_policy or (
                as_float(policy.get("delta_vs_control_cents")) or -999999.0
            ) > (as_float(best_policy.get("delta_vs_control_cents")) or -999999.0):
                best_lane = lane
                best_policy = policy
        recommendations.append({
            "rank": 3.701,
            "action": "do_not_shrink_feature_gate_on_high_raw_book_gap_alone",
            "why": (
                "The high-gap valve forensics do not transfer cleanly to feature-gate rows. "
                f"Best diagnostic policy is {best_policy.get('policy')} on {best_lane.get('candidate')} with "
                f"delta {best_policy.get('delta_vs_control_cents')}c versus control and weighted net "
                f"{best_policy.get('weighted_net_cents')}c. In the strict post-feature lanes the high-gap row is "
                "a +56c approved-entry winner, so shrinking raw/book gap alone cuts right-tail profit and does not "
                "repair coverage, source share, cushion, or live-baseline blockers."
            ),
            "evidence": {
                "feature_gate_high_gap_shrink_diagnostic": feature_gate_high_gap_shrink,
            },
        })
    price = report.get("target_price_friction") or {}
    tag_rollups = [
        row for row in price.get("tag_rollups") or []
        if int(row.get("settled") or 0) >= 5
    ][:5]
    if tag_rollups:
        recommendations.append({
            "rank": 3.75,
            "action": "separate_directional_failure_from_price_friction",
            "why": "The broad surface is losing mainly through direction-wrong rows; price/edge buckets identify where FV confidence is physically deceptive.",
            "evidence": tag_rollups,
        })
    book_fv = report.get("approved_entry_book_fv_robustness") or {}
    if not (book_fv.get("blockers") or []):
        recommendations.append({
            "rank": 4,
            "action": "preserve_book_probability_as_calibration_anchor",
            "why": "Book probability is the strongest actual-approved calibration signal, but it should be used as calibration evidence, not as a standalone entry edge.",
            "evidence": {
                "candidate": book_fv.get("candidate"),
                "bootstrap": book_fv.get("bootstrap"),
                "full": book_fv.get("full"),
            },
        })
    return recommendations


def build_report() -> dict[str, Any]:
    readiness = load_json(READINESS_JSON)
    tracker = load_json(TRACKER_JSON)
    leaderboard = load_json(LEADERBOARD_JSON)
    decision = load_json(DECISION_MATRIX_JSON)
    goal = load_json(GOAL_AUDIT_JSON)
    exit_reduce = load_json(EXIT_REDUCE_JSON)
    exit_reduce_drift_audit = load_json(EXIT_REDUCE_DRIFT_AUDIT_JSON)
    exit_reduce_drift_guard_watch = load_json(EXIT_REDUCE_DRIFT_GUARD_WATCH_JSON)
    exit_reduce_runway = load_json(EXIT_REDUCE_RUNWAY_JSON)
    exit_reduce_actionability = load_json(EXIT_REDUCE_ACTIONABILITY_JSON)
    exit_reduce_geometry_opportunity = load_json(EXIT_REDUCE_GEOMETRY_OPPORTUNITY_JSON)
    exit_reduce_geometry_relaxed_watch = load_json(EXIT_REDUCE_GEOMETRY_RELAXED_WATCH_JSON)
    exit_book_gap = load_json(EXIT_BOOK_GAP_JSON)
    exit_book_gap_loss_guard = load_json(EXIT_BOOK_GAP_LOSS_GUARD_JSON)
    exit_book_gap_loss_guard_v2 = load_json(EXIT_BOOK_GAP_LOSS_GUARD_V2_JSON)
    exit_book_gap_loss_guard_v3 = load_json(EXIT_BOOK_GAP_LOSS_GUARD_V3_JSON)
    exit_book_gap_value_only = load_json(EXIT_BOOK_GAP_VALUE_ONLY_JSON)
    exit_book_gap_value_only_opportunity = load_json(EXIT_BOOK_GAP_VALUE_ONLY_OPPORTUNITY_JSON)
    exit_value_reduce_depth_composite = load_json(EXIT_VALUE_REDUCE_DEPTH_COMPOSITE_JSON)
    exit_value_reduce_depth_opportunity = load_json(EXIT_VALUE_REDUCE_DEPTH_OPPORTUNITY_JSON)
    exit_reduce_observable_loss_control = load_json(EXIT_REDUCE_OBSERVABLE_LOSS_CONTROL_JSON)
    exit_reduce_observable_loss_control_opportunity = load_json(EXIT_REDUCE_OBSERVABLE_LOSS_CONTROL_OPPORTUNITY_JSON)
    exit_reduce_observable_false_hold_autopsy = load_json(EXIT_REDUCE_OBSERVABLE_FALSE_HOLD_AUTOPSY_JSON)
    exit_midband_reduce_rescue = load_json(EXIT_MIDBAND_REDUCE_RESCUE_JSON)
    exit_book_gap_loss_guard_v2_opportunity = load_json(EXIT_BOOK_GAP_LOSS_GUARD_V2_OPPORTUNITY_JSON)
    exit_book_gap_loss_guard_v3_opportunity = load_json(EXIT_BOOK_GAP_LOSS_GUARD_V3_OPPORTUNITY_JSON)
    exit_loss_guard_v1_v2_v3_contrast = load_json(EXIT_LOSS_GUARD_V1_V2_V3_CONTRAST_JSON)
    exit_loss_guard_v3_residual_size_shrink = load_json(EXIT_LOSS_GUARD_V3_RESIDUAL_SIZE_SHRINK_JSON)
    exit_loss_guard_v1_v2_runway = load_json(EXIT_LOSS_GUARD_V1_V2_RUNWAY_JSON)
    exit_common_clock = load_json(EXIT_COMMON_CLOCK_JSON)
    exit_common_clock_runway = load_json(EXIT_COMMON_CLOCK_RUNWAY_JSON)
    exit_common_clock_residual_frontier = load_json(EXIT_COMMON_CLOCK_RESIDUAL_FRONTIER_JSON)
    exit_strict_failure_drilldown = load_json(EXIT_STRICT_FAILURE_DRILLDOWN_JSON)
    exit_policy_watch_dashboard = load_json(EXIT_POLICY_WATCH_DASHBOARD_JSON)
    exit_promotion_queue_audit = load_json(EXIT_PROMOTION_QUEUE_AUDIT_JSON)
    dual_exit = load_json(DUAL_EXIT_JSON)
    target_loss = load_json(TARGET_LOSS_ATTRIBUTION_JSON)
    target_price_friction = load_json(TARGET_PRICE_FRICTION_JSON)
    target_cluster_penalty_runway = load_json(TARGET_CLUSTER_PENALTY_RUNWAY_JSON)
    target_cluster_penalty_source_feasibility = load_json(TARGET_CLUSTER_PENALTY_SOURCE_FEASIBILITY_JSON)
    target_cluster_penalty_source_displacement = load_json(TARGET_CLUSTER_PENALTY_SOURCE_DISPLACEMENT_JSON)
    target_cluster_penalty_source_aware = load_json(TARGET_CLUSTER_PENALTY_SOURCE_AWARE_JSON)
    target_cluster_penalty_observable_stability = load_json(TARGET_CLUSTER_PENALTY_OBSERVABLE_STABILITY_JSON)
    feature_gate_clean_broad_frontier = load_json(FEATURE_GATE_CLEAN_BROAD_FRONTIER_JSON)
    feature_gate_soft_frontier_exit_stack = load_json(FEATURE_GATE_SOFT_FRONTIER_EXIT_STACK_JSON)
    feature_gate_cheap_tail_shrink_watch = load_json(FEATURE_GATE_CHEAP_TAIL_SHRINK_WATCH_JSON)
    feature_gate_near_promotion_watch = load_json(FEATURE_GATE_NEAR_PROMOTION_WATCH_JSON)
    feature_gate_near_promotion_exit_attribution = load_json(FEATURE_GATE_NEAR_PROMOTION_EXIT_ATTRIBUTION_JSON)
    feature_gate_near_promotion_denominator_gap = load_json(FEATURE_GATE_NEAR_PROMOTION_DENOMINATOR_GAP_JSON)
    feature_gate_quick_status = load_json(FEATURE_GATE_QUICK_STATUS_JSON)
    feature_gate_raw03_vs_raw05_autopsy = load_json(FEATURE_GATE_RAW03_VS_RAW05_AUTOPSY_JSON)
    feature_gate_raw05_coverage_gap_audit = load_json(FEATURE_GATE_RAW05_COVERAGE_GAP_JSON)
    feature_gate_core_expansion_mix = load_json(FEATURE_GATE_CORE_EXPANSION_MIX_JSON)
    feature_gate_coverage_repair = load_json(FEATURE_GATE_COVERAGE_REPAIR_JSON)
    feature_gate_coverage_size_shrink = load_json(FEATURE_GATE_COVERAGE_SIZE_SHRINK_JSON)
    feature_gate_coverage_size_shrink_exit_attribution = load_json(FEATURE_GATE_COVERAGE_SIZE_SHRINK_EXIT_ATTR_JSON)
    feature_gate_coverage_size_shrink_runway = load_json(FEATURE_GATE_COVERAGE_SIZE_SHRINK_RUNWAY_JSON)
    feature_gate_joint_gate_gap_audit = load_json(FEATURE_GATE_JOINT_GAP_JSON)
    feature_gate_gap_mechanism_synthesis = load_json(FEATURE_GATE_GAP_MECHANISM_SYNTHESIS_JSON)
    feature_gate_current_margin_size_proxy = load_json(FEATURE_GATE_CURRENT_MARGIN_SIZE_PROXY_JSON)
    soft_frontier_size_shrink = load_json(SOFT_FRONTIER_SIZE_SHRINK_JSON)
    soft_frontier_midprice_boundary_shrink = load_json(SOFT_FRONTIER_MIDPRICE_BOUNDARY_SHRINK_JSON)
    soft_frontier_midprice_boundary_source_stress = load_json(SOFT_FRONTIER_MIDPRICE_BOUNDARY_SOURCE_STRESS_JSON)
    soft_frontier_midprice_boundary_exit_stack = load_json(SOFT_FRONTIER_MIDPRICE_BOUNDARY_EXIT_STACK_JSON)
    soft_frontier_midprice_boundary_exit_stack_runway = load_json(SOFT_FRONTIER_MIDPRICE_BOUNDARY_EXIT_STACK_RUNWAY_JSON)
    soft_frontier_midprice_boundary_dual_exit_stack = load_json(SOFT_FRONTIER_MIDPRICE_BOUNDARY_DUAL_EXIT_STACK_JSON)
    soft_frontier_midprice_boundary_dual_exit_guard = load_json(SOFT_FRONTIER_MIDPRICE_BOUNDARY_DUAL_EXIT_GUARD_JSON)
    control_risk_stop_audit = load_json(CONTROL_RISK_STOP_AUDIT_JSON)
    exit_policy_loss_churn = load_json(EXIT_POLICY_LOSS_CHURN_JSON)
    loss_churn_guarded_frontier = load_json(LOSS_CHURN_GUARDED_FRONTIER_JSON)
    loss_churn_observable_full_denominator_replay = load_json(LOSS_CHURN_FULL_DENOM_REPLAY_JSON)
    loss_churn_recross_clock_feasibility = load_json(LOSS_CHURN_RECROSS_CLOCK_FEASIBILITY_JSON)
    loss_churn_recross_exit_clock_join_audit = load_json(LOSS_CHURN_RECROSS_JOIN_AUDIT_JSON)
    loss_churn_recross_threshold_frontier = load_json(LOSS_CHURN_RECROSS_THRESHOLD_FRONTIER_JSON)
    exit_clock_source_stability = load_json(EXIT_CLOCK_SOURCE_STABILITY_JSON)
    exit_clock_low_edge_hold_guard_tradeoff = load_json(EXIT_CLOCK_LOW_EDGE_HOLD_GUARD_TRADEOFF_JSON)
    exit_clock_broad_hold_neighbor_autopsy = load_json(EXIT_CLOCK_BROAD_HOLD_NEIGHBOR_AUTOPSY_JSON)
    forward_collection_blocker_audit = load_json(FORWARD_COLLECTION_BLOCKER_AUDIT_JSON)
    live_loss_escape_analysis = load_json(LIVE_LOSS_ESCAPE_JSON)
    dual_lane_same_window_delta_autopsy = load_json(DUAL_LANE_SAME_WINDOW_DELTA_AUTOPSY_JSON)
    dual_lane_same_window_sequence_mechanism = load_json(DUAL_LANE_SAME_WINDOW_SEQUENCE_MECHANISM_JSON)
    dual_lane_state_exposure_sequence_repair = load_json(DUAL_LANE_STATE_EXPOSURE_REPAIR_JSON)
    dual_lane_side_flip_feasibility = load_json(DUAL_LANE_SIDE_FLIP_FEASIBILITY_JSON)
    exit_repair_gap_classifier = load_json(EXIT_REPAIR_GAP_CLASSIFIER_JSON)
    matched_unchanged_loss_separator = load_json(MATCHED_UNCHANGED_LOSS_SEPARATOR_JSON)
    matched_unchanged_loss_guard_watch = load_json(MATCHED_UNCHANGED_LOSS_GUARD_WATCH_JSON)
    matched_unchanged_loss_guard_opportunity = load_json(MATCHED_UNCHANGED_LOSS_GUARD_OPPORTUNITY_JSON)
    exit_true_loser_hold_risk = load_json(EXIT_TRUE_LOSER_HOLD_RISK_JSON)
    exit_false_hold_guardrail_bridge = load_json(EXIT_FALSE_HOLD_GUARDRAIL_BRIDGE_JSON)
    exit_common_clock_residual_child_watch = load_json(EXIT_COMMON_CLOCK_RESIDUAL_CHILD_JSON)
    exit_common_clock_residual_child_path_risk = load_json(EXIT_COMMON_CLOCK_RESIDUAL_CHILD_PATH_RISK_JSON)
    exit_common_clock_residual_child_false_hold_autopsy = load_json(EXIT_COMMON_CLOCK_RESIDUAL_CHILD_FALSE_HOLD_AUTOPSY_JSON)
    exit_common_clock_residual_child_guardrail_variants = load_json(EXIT_COMMON_CLOCK_RESIDUAL_CHILD_GUARDRAIL_VARIANTS_JSON)
    exit_common_clock_residual_child_book_gap_guard_watch = load_json(EXIT_COMMON_CLOCK_RESIDUAL_CHILD_BOOK_GAP_GUARD_WATCH_JSON)
    exit_clip_separator = load_json(EXIT_CLIP_SEPARATOR_JSON)
    exit_clip_separator_watch = load_json(EXIT_CLIP_SEPARATOR_WATCH_JSON)
    exit_clip_separator_opportunity = load_json(EXIT_CLIP_SEPARATOR_OPPORTUNITY_JSON)
    exit_clip_separator_replay = load_json(EXIT_CLIP_SEPARATOR_REPLAY_JSON)
    approved_entry_state_valve_bridge = load_json(APPROVED_ENTRY_STATE_VALVE_BRIDGE_JSON)
    approved_entry_state_valve_full_surface = load_json(APPROVED_ENTRY_STATE_VALVE_FULL_SURFACE_JSON)
    high_gap_skipped_failure_modes = load_json(HIGH_GAP_SKIPPED_FAILURE_MODES_JSON)
    feature_gate_high_gap_shrink_diagnostic = load_json(FEATURE_GATE_HIGH_GAP_SHRINK_DIAGNOSTIC_JSON)
    collapse_suppress_shadow = load_json(COLLAPSE_SUPPRESS_SHADOW_JSON)
    collapse_reentry_registry = load_json(COLLAPSE_REENTRY_JSON)
    control_risk_summary = control_risk_stop_audit.get("summary") or {}
    source_rows = tracker.get("rows") or readiness.get("candidates") or []
    candidates = [candidate_row(row) for row in source_rows]
    blocker_counts = Counter()
    blocker_family_counts = Counter()
    by_gate: dict[str, Counter[str]] = defaultdict(Counter)
    for row in candidates:
        for blocker in row.get("blockers") or []:
            blocker_counts[str(blocker)] += 1
            family = blocker_family(str(blocker))
            blocker_family_counts[family] += 1
            by_gate[str(row.get("gate"))][family] += 1
    best_candidates = sorted(candidates, key=candidate_score, reverse=True)[:12]
    report = {
        "objective_status": {
            "achieved": goal.get("achieved"),
            "any_live_ready": readiness.get("any_live_ready"),
            "control_risk_stop": readiness.get("control_risk_stop"),
            "control_entries": readiness.get("control_entries"),
            "control_gross_cents": readiness.get("control_gross_cents"),
            "control_risk_stop_reason": control_risk_summary.get("risk_stop_reason"),
            "control_risk_stop_by_loss_count": control_risk_summary.get("risk_stop_by_loss_count"),
            "control_risk_stop_by_drawdown": control_risk_summary.get("risk_stop_by_drawdown"),
            "control_max_drawdown_pct": control_risk_summary.get("max_drawdown_pct"),
            "control_full_loss_events": control_risk_summary.get("full_loss_events"),
            "control_near_full_loss_events": control_risk_summary.get("near_full_loss_events_50_99c"),
        },
        "global_blocker_counts": dict(blocker_counts.most_common()),
        "blocker_family_counts": dict(blocker_family_counts.most_common()),
        "blocker_family_by_gate": {gate: dict(counter.most_common()) for gate, counter in sorted(by_gate.items())},
        "best_candidates": best_candidates,
        "exit_lanes": [
            exit_lane_status(exit_reduce, "reduce_suppression"),
            exit_lane_status(exit_book_gap, "book_gap_suppression"),
            exit_lane_status(exit_book_gap_loss_guard, "book_gap_loss_guard"),
            exit_lane_status(exit_book_gap_loss_guard_v2, "book_gap_loss_guard_v2"),
            exit_lane_status(exit_book_gap_loss_guard_v3, "book_gap_loss_guard_v3"),
            exit_lane_status(exit_book_gap_value_only, "book_gap_value_only"),
            exit_lane_status(exit_value_reduce_depth_composite, "exit_value_reduce_depth"),
            variant_lane_status(exit_reduce_observable_loss_control, "exit_reduce_observable_loss_control", "post_observable_birth"),
            exit_lane_status(dual_exit, "dual_exit_book_gap_else_reduce"),
        ],
        "exit_common_clock": exit_common_clock,
        "exit_common_clock_runway": exit_common_clock_runway,
        "exit_common_clock_residual_frontier": exit_common_clock_residual_frontier,
        "exit_strict_failure_drilldown": exit_strict_failure_drilldown,
        "exit_policy_watch_dashboard": exit_policy_watch_dashboard,
        "exit_promotion_queue_audit": exit_promotion_queue_audit,
        "exit_book_gap_value_only_opportunity": exit_book_gap_value_only_opportunity,
        "exit_value_reduce_depth_opportunity": exit_value_reduce_depth_opportunity,
        "exit_reduce_observable_loss_control": exit_reduce_observable_loss_control,
        "exit_reduce_observable_loss_control_opportunity": exit_reduce_observable_loss_control_opportunity,
        "exit_reduce_observable_false_hold_autopsy": exit_reduce_observable_false_hold_autopsy,
        "exit_midband_reduce_rescue": exit_midband_reduce_rescue,
        "exit_book_gap_loss_guard_v2_opportunity": exit_book_gap_loss_guard_v2_opportunity,
        "exit_book_gap_loss_guard_v3_opportunity": exit_book_gap_loss_guard_v3_opportunity,
        "exit_loss_guard_v1_v2_v3_contrast": exit_loss_guard_v1_v2_v3_contrast,
        "exit_loss_guard_v3_residual_size_shrink": exit_loss_guard_v3_residual_size_shrink,
        "exit_loss_guard_v1_v2_runway": exit_loss_guard_v1_v2_runway,
        "exit_reduce_actionability": exit_reduce_actionability,
        "exit_reduce_drift_audit": exit_reduce_drift_audit,
        "exit_reduce_drift_guard_watch": exit_reduce_drift_guard_watch,
        "exit_reduce_geometry_opportunity": exit_reduce_geometry_opportunity,
        "exit_reduce_geometry_relaxed_watch": exit_reduce_geometry_relaxed_watch,
        "exit_reduce_runway": exit_reduce_runway,
        "target_loss_attribution": target_loss,
        "target_price_friction": target_price_friction,
        "target_cluster_penalty_runway": target_cluster_penalty_runway,
        "target_cluster_penalty_source_feasibility": target_cluster_penalty_source_feasibility,
        "target_cluster_penalty_source_displacement": target_cluster_penalty_source_displacement,
        "target_cluster_penalty_source_aware": target_cluster_penalty_source_aware,
        "target_cluster_penalty_observable_stability": target_cluster_penalty_observable_stability,
        "feature_gate_clean_broad_frontier": feature_gate_clean_broad_frontier,
        "feature_gate_soft_frontier_exit_stack": feature_gate_soft_frontier_exit_stack,
        "feature_gate_cheap_tail_shrink_watch": feature_gate_cheap_tail_shrink_watch,
        "feature_gate_near_promotion_watch": feature_gate_near_promotion_watch,
        "feature_gate_near_promotion_exit_attribution": feature_gate_near_promotion_exit_attribution,
        "feature_gate_near_promotion_denominator_gap": feature_gate_near_promotion_denominator_gap,
        "feature_gate_quick_status": feature_gate_quick_status,
        "feature_gate_raw03_vs_raw05_autopsy": feature_gate_raw03_vs_raw05_autopsy,
        "feature_gate_raw05_coverage_gap_audit": feature_gate_raw05_coverage_gap_audit,
        "feature_gate_core_expansion_mix": feature_gate_core_expansion_mix,
        "feature_gate_coverage_repair": feature_gate_coverage_repair,
        "feature_gate_coverage_size_shrink": feature_gate_coverage_size_shrink,
        "feature_gate_coverage_size_shrink_exit_attribution": feature_gate_coverage_size_shrink_exit_attribution,
        "feature_gate_coverage_size_shrink_runway": feature_gate_coverage_size_shrink_runway,
        "feature_gate_joint_gate_gap_audit": feature_gate_joint_gate_gap_audit,
        "feature_gate_gap_mechanism_synthesis": feature_gate_gap_mechanism_synthesis,
        "feature_gate_current_margin_size_proxy": feature_gate_current_margin_size_proxy,
        "soft_frontier_size_shrink": soft_frontier_size_shrink,
        "soft_frontier_midprice_boundary_shrink": soft_frontier_midprice_boundary_shrink,
        "soft_frontier_midprice_boundary_source_stress": soft_frontier_midprice_boundary_source_stress,
        "soft_frontier_midprice_boundary_exit_stack": soft_frontier_midprice_boundary_exit_stack,
        "soft_frontier_midprice_boundary_exit_stack_runway": soft_frontier_midprice_boundary_exit_stack_runway,
        "soft_frontier_midprice_boundary_dual_exit_stack": soft_frontier_midprice_boundary_dual_exit_stack,
        "soft_frontier_midprice_boundary_dual_exit_guard": soft_frontier_midprice_boundary_dual_exit_guard,
        "control_risk_stop_audit": control_risk_stop_audit,
        "exit_policy_loss_churn": exit_policy_loss_churn,
        "loss_churn_guarded_frontier": loss_churn_guarded_frontier,
        "loss_churn_observable_full_denominator_replay": loss_churn_observable_full_denominator_replay,
        "loss_churn_recross_clock_feasibility": loss_churn_recross_clock_feasibility,
        "loss_churn_recross_exit_clock_join_audit": loss_churn_recross_exit_clock_join_audit,
        "loss_churn_recross_threshold_frontier": loss_churn_recross_threshold_frontier,
        "exit_clock_source_stability": exit_clock_source_stability,
        "exit_clock_low_edge_hold_guard_tradeoff": exit_clock_low_edge_hold_guard_tradeoff,
        "exit_clock_broad_hold_neighbor_autopsy": exit_clock_broad_hold_neighbor_autopsy,
        "forward_collection_blocker_audit": forward_collection_blocker_audit,
        "live_loss_escape_analysis": live_loss_escape_analysis,
        "dual_lane_same_window_delta_autopsy": dual_lane_same_window_delta_autopsy,
        "dual_lane_same_window_sequence_mechanism": dual_lane_same_window_sequence_mechanism,
        "dual_lane_state_exposure_sequence_repair": dual_lane_state_exposure_sequence_repair,
        "dual_lane_side_flip_feasibility": dual_lane_side_flip_feasibility,
        "exit_repair_gap_classifier": exit_repair_gap_classifier,
        "matched_unchanged_loss_separator": matched_unchanged_loss_separator,
        "matched_unchanged_loss_guard_watch": matched_unchanged_loss_guard_watch,
        "matched_unchanged_loss_guard_opportunity": matched_unchanged_loss_guard_opportunity,
        "exit_true_loser_hold_risk": exit_true_loser_hold_risk,
        "exit_false_hold_guardrail_bridge": exit_false_hold_guardrail_bridge,
        "exit_common_clock_residual_child_watch": exit_common_clock_residual_child_watch,
        "exit_common_clock_residual_child_path_risk": exit_common_clock_residual_child_path_risk,
        "exit_common_clock_residual_child_false_hold_autopsy": exit_common_clock_residual_child_false_hold_autopsy,
        "exit_common_clock_residual_child_guardrail_variants": exit_common_clock_residual_child_guardrail_variants,
        "exit_common_clock_residual_child_book_gap_guard_watch": exit_common_clock_residual_child_book_gap_guard_watch,
        "exit_clip_separator": exit_clip_separator,
        "exit_clip_separator_watch": exit_clip_separator_watch,
        "exit_clip_separator_opportunity": exit_clip_separator_opportunity,
        "exit_clip_separator_replay": exit_clip_separator_replay,
        "approved_entry_state_valve_bridge": approved_entry_state_valve_bridge,
        "approved_entry_state_valve_full_surface": approved_entry_state_valve_full_surface,
        "high_gap_skipped_failure_modes": high_gap_skipped_failure_modes,
        "feature_gate_high_gap_shrink_diagnostic": feature_gate_high_gap_shrink_diagnostic,
        "collapse_suppress_shadow": collapse_suppress_shadow,
        "collapse_reentry_registry": collapse_reentry_registry,
        "approved_entry_book_fv_robustness": decision.get("approved_entry_book_fv_robustness") or {},
        "leaderboard_top": (leaderboard.get("ranked") or [])[:8],
    }
    report["recommendations"] = build_recommendations(report)
    return report


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Next Action Triage",
        "",
        "Research-only triage. This does not promote candidates or place orders.",
        "",
        "## Objective Status",
        "",
    ]
    status = report["objective_status"]
    for key in ["achieved", "any_live_ready", "control_risk_stop", "control_entries", "control_gross_cents"]:
        lines.append(f"- {key}: `{status.get(key)}`")
    lines.extend([
        f"- control_risk_stop_reason: `{status.get('control_risk_stop_reason')}`",
        f"- control_risk_stop_by_loss_count/drawdown: `{status.get('control_risk_stop_by_loss_count')}/{status.get('control_risk_stop_by_drawdown')}`",
        f"- control_max_drawdown_pct: `{fmt(status.get('control_max_drawdown_pct'))}`",
        f"- control_full_loss_events/near_full_loss_events: `{status.get('control_full_loss_events')}/{status.get('control_near_full_loss_events')}`",
    ])
    lines.extend([
        "",
        "## Next Actions",
        "",
    ])
    for rec in report.get("recommendations") or []:
        lines.append(f"{rec.get('rank')}. `{rec.get('action')}` - {rec.get('why')}")
    churn_rows = (report.get("exit_policy_loss_churn") or {}).get("rows") or []
    if churn_rows:
        lines.extend([
            "",
            "## Exit Policy Loss-Count Churn",
            "",
            "| lane | rows | current W/L | candidate W/L | loss-count delta | net delta | suppressed | new losses | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for row in churn_rows[:8]:
            lines.append(
                f"| {row.get('label')} | {row.get('rows')} | "
                f"{row.get('current_wins')}/{row.get('current_losses')} | "
                f"{row.get('candidate_wins')}/{row.get('candidate_losses')} | "
                f"{row.get('loss_count_reduction')} | {fmt(row.get('delta_cents'))} | "
                f"{row.get('suppressed_rows')} | {row.get('non_loss_to_loss')} | "
                f"{', '.join(row.get('blockers') or []) or 'none'} |"
            )
    exit_gap = report.get("exit_repair_gap_classifier") or {}
    exit_gap_summary = exit_gap.get("summary") or {}
    if exit_gap_summary:
        lines.extend([
            "",
            "## Exit Repair Gap Classifier",
            "",
            f"- Unresolved losses: `{exit_gap_summary.get('unresolved_rows')}/{exit_gap_summary.get('loss_rows')}` "
            f"({fmt(exit_gap_summary.get('unresolved_share'))}%)",
            f"- No frozen exit-repair observation: `{exit_gap_summary.get('no_exit_repair_observation_rows')}`",
            f"- No-observation pre/post first exit-repair freeze: "
            f"`{exit_gap_summary.get('no_exit_repair_observation_pre_first_freeze_rows')}/{exit_gap_summary.get('no_exit_repair_observation_post_first_freeze_rows')}`",
            f"- Matched but unchanged: `{exit_gap_summary.get('matched_but_unchanged_rows')}`",
            f"- Repair flips/worsens losses: `{exit_gap_summary.get('repair_flips_loss_rows')}/{exit_gap_summary.get('repair_would_worsen_rows')}`",
            f"- Observable post-birth probability-reduce/would-suppress rows: "
            f"`{exit_gap_summary.get('observable_post_birth_probability_reduce_rows')}/{exit_gap_summary.get('observable_post_birth_would_suppress_rows')}`",
            f"- Observable post-birth worst suppress delta: `{fmt(exit_gap_summary.get('observable_post_birth_worst_suppress_delta_cents'))}c`",
        ])
    exit_clip = report.get("exit_clip_separator") or {}
    clip_summary = exit_clip.get("summary") or {}
    clip_best = (exit_clip.get("top_rules") or [{}])[0]
    if clip_summary:
        lines.extend([
            "",
            "## Exit Clip Separator Diagnostic",
            "",
            f"- Matched unchanged rows: `{clip_summary.get('matched_unchanged_rows')}`",
            f"- Known hold helpful/harmful/unknown: `{clip_summary.get('hold_helpful_rows')}/{clip_summary.get('hold_harmful_rows')}/{clip_summary.get('hold_unknown_rows')}`",
            f"- Best rule: `{clip_best.get('rule')}`",
            f"- Best rule helpful/harmful/unknown: `{clip_best.get('helpful_rows')}/{clip_best.get('harmful_rows')}/{clip_best.get('unknown_rows')}`",
            f"- Best rule known hold delta: `{fmt(clip_best.get('known_hold_delta_cents'))}c`",
        ])
    clip_watch = report.get("exit_clip_separator_watch") or {}
    clip_watch_state = clip_watch.get("state") or {}
    clip_watch_summary = clip_watch.get("candidate_summary") or {}
    if clip_watch_summary:
        lines.extend([
            "",
            "## Frozen Exit Clip Separator Watch",
            "",
            f"- Freeze UTC: `{clip_watch_state.get('freeze_ts_utc')}`",
            f"- Post-freeze matched unchanged rows: `{clip_watch.get('post_freeze_matched_unchanged_rows')}`",
            f"- Selected rows: `{clip_watch_summary.get('rows')}`",
            f"- Known helpful/harmful/unknown: `{clip_watch_summary.get('helpful_rows')}/{clip_watch_summary.get('harmful_rows')}/{clip_watch_summary.get('unknown_rows')}`",
            f"- Known hold delta: `{fmt(clip_watch_summary.get('known_hold_delta_cents'))}c`",
            f"- Blockers: `{', '.join(clip_watch_summary.get('blockers') or []) or 'none'}`",
        ])
    clip_opp = report.get("exit_clip_separator_opportunity") or {}
    clip_opp_selected = clip_opp.get("selected_summary") or {}
    clip_opp_near = clip_opp.get("near_miss_summary") or {}
    if clip_opp:
        lines.extend([
            "",
            "## Exit Clip Separator Opportunity",
            "",
            f"- Post-freeze denominator rows: `{clip_opp.get('post_freeze_rows')}`",
            f"- Selected rows: `{clip_opp.get('selected_rows')}`",
            f"- Selected helpful/harmful/unknown: `{clip_opp_selected.get('helpful_rows')}/{clip_opp_selected.get('harmful_rows')}/{clip_opp_selected.get('unknown_rows')}`",
            f"- Selected known hold delta: `{fmt(clip_opp_selected.get('known_hold_delta_cents'))}c`",
            f"- Near-miss rows: `{clip_opp.get('near_miss_rows')}`",
            f"- Near-miss helpful/harmful/unknown: `{clip_opp_near.get('helpful_rows')}/{clip_opp_near.get('harmful_rows')}/{clip_opp_near.get('unknown_rows')}`",
            f"- Near-miss known hold delta: `{fmt(clip_opp_near.get('known_hold_delta_cents'))}c`",
            f"- Fail reasons: `{clip_opp.get('fail_reason_counts')}`",
            f"- Blockers: `{', '.join(clip_opp.get('blockers') or []) or 'none'}`",
        ])
    clip_replay = report.get("exit_clip_separator_replay") or {}
    clip_replay_summaries = clip_replay.get("summaries") or []
    if clip_replay_summaries:
        lines.extend([
            "",
            "## Exit Clip Separator Replay",
            "",
            "| label | rows | current W/L | candidate W/L | current net | candidate net | delta | suppressed | loss reduction | suppressed losers | cushion | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for row in clip_replay_summaries:
            lines.append(
                f"| `{row.get('label')}` | {row.get('rows')} | "
                f"{row.get('current_wins')}/{row.get('current_losses')} | "
                f"{row.get('candidate_wins')}/{row.get('candidate_losses')} | "
                f"{fmt(row.get('current_net_cents'))}c | {fmt(row.get('candidate_net_cents'))}c | "
                f"{fmt(row.get('delta_cents'))}c | {row.get('suppressed_rows')} | "
                f"{row.get('loss_count_reduction')} | {row.get('suppressed_losers')} | "
                f"{row.get('full_loss_cushion_estimate')} | "
                f"{', '.join(row.get('blockers') or []) or 'none'} |"
            )
        unresolved_failure = [
            row for row in exit_gap.get("unresolved_by_failure_class") or []
            if row.get("rows")
        ]
        if unresolved_failure:
            lines.extend([
                "",
                "| unresolved failure class | rows | actual loss c | hold helpful | hold harmful | hold unknown |",
                "|---|---:|---:|---:|---:|---:|",
            ])
            for row in unresolved_failure:
                lines.append(
                    f"| {row.get('failure_class')} | {row.get('rows')} | {fmt(row.get('actual_loss_cents'))} | "
                    f"{row.get('hold_helpful_rows')} | {row.get('hold_harmful_rows')} | {row.get('hold_unknown_rows')} |"
                )
    matched_guard = report.get("matched_unchanged_loss_guard_watch") or {}
    matched_guard_opp = report.get("matched_unchanged_loss_guard_opportunity") or {}
    matched_guard_state = matched_guard.get("state") or {}
    matched_guard_diag = matched_guard.get("diagnostic_summary") or {}
    matched_guard_post = matched_guard.get("post_freeze_summary") or {}
    if matched_guard_post:
        lines.extend([
            "",
            "## Frozen Matched-Unchanged Loss Guard Watch",
            "",
            f"- Freeze UTC: `{matched_guard_state.get('freeze_ts_utc')}`",
            f"- Diagnostic selected/helpful/harmful: `{matched_guard_diag.get('selected_rows')}/{matched_guard_diag.get('helpful_rows')}/{matched_guard_diag.get('harmful_rows')}`",
            f"- Diagnostic selected hold delta: `{fmt(matched_guard_diag.get('selected_hold_delta_cents'))}c`",
            f"- Post-freeze scored rows: `{matched_guard_post.get('rows')}`",
            f"- Post-freeze selected rows: `{matched_guard_post.get('selected_rows')}`",
            f"- Post-freeze helpful/harmful/flat: `{matched_guard_post.get('helpful_rows')}/{matched_guard_post.get('harmful_rows')}/{matched_guard_post.get('flat_rows')}`",
            f"- Post-freeze delta/cushion: `{fmt(matched_guard_post.get('delta_vs_current_cents'))}c / {matched_guard_post.get('full_loss_cushion')}`",
            f"- Blockers: `{', '.join(matched_guard_post.get('blockers') or []) or 'none'}`",
        ])
        if matched_guard_opp:
            lines.extend([
                f"- Opportunity post-freeze scored/selected/near-miss: `{matched_guard_opp.get('post_freeze_rows')}/{matched_guard_opp.get('selected_rows')}/{matched_guard_opp.get('near_miss_rows')}`",
                f"- Opportunity near-miss hold delta: `{fmt(matched_guard_opp.get('near_miss_hold_delta_cents'))}c`",
                f"- Opportunity fail reasons: `{matched_guard_opp.get('fail_reason_counts') or {}}`",
            ])
    true_loser_hold = report.get("exit_true_loser_hold_risk") or {}
    true_loser_summary = true_loser_hold.get("summary") or {}
    if true_loser_summary:
        true_loser = true_loser_summary.get("true_loser") or {}
        clipped = true_loser_summary.get("clipped_winner") or {}
        lines.extend([
            "",
            "## Exit True-Loser Hold Risk Guardrail",
            "",
            f"- True-loser hold-risk rows: `{true_loser_summary.get('true_loser_rows')}`",
            f"- True-loser hold delta: `{fmt(true_loser.get('hold_delta_cents'))}c`",
            f"- Clipped-winner rows: `{true_loser_summary.get('clipped_winner_rows')}`",
            f"- Clipped-winner hold delta: `{fmt(clipped.get('hold_delta_cents'))}c`",
            "",
            "| tag | true rows | true hold delta | clipped rows | clipped hold delta | read |",
            "|---|---:|---:|---:|---:|---|",
        ])
        for row in (true_loser_hold.get("avoid_broad_hold_tags") or [])[:10]:
            lines.append(
                f"| `{row.get('tag')}` | {row.get('true_loser_rows')} | "
                f"{fmt(row.get('true_loser_hold_delta_cents'))}c | {row.get('clipped_winner_rows')} | "
                f"{fmt(row.get('clipped_winner_hold_delta_cents'))}c | `{row.get('read')}` |"
            )
    false_hold_bridge = report.get("exit_false_hold_guardrail_bridge") or {}
    false_hold_summary = false_hold_bridge.get("summary") or {}
    if false_hold_summary:
        lines.extend([
            "",
            "## Exit False-Hold Guardrail Bridge",
            "",
            f"- Strict harmful suppressions: `{false_hold_bridge.get('strict_harmful_suppressions')}`",
            f"- Strict net harm: `{fmt(false_hold_bridge.get('strict_net_harm_cents'))}c`",
            f"- Top guardrail tags: `{false_hold_summary.get('top_guardrail_tags')}`",
            "",
            "| policy | harmful rows | net harm | top tags |",
            "|---|---:|---:|---|",
        ])
        for row in (false_hold_bridge.get("policy_rows") or [])[:8]:
            lines.append(
                f"| `{row.get('policy')}` | {row.get('harmful_rows')} | "
                f"{fmt(row.get('net_harm_cents'))}c | `{row.get('top_guardrail_tags')}` |"
            )
    strict_failure = report.get("exit_strict_failure_drilldown") or {}
    strict_summaries = [
        row for row in strict_failure.get("summaries") or []
        if str(row.get("window") or "").startswith("new_exit_mix_common_forward")
    ]
    if strict_summaries:
        lines.extend([
            "",
            "## Exit Strict Failure Drilldown",
            "",
            f"- Strict harmful suppressions: `{strict_failure.get('strict_harmful_suppressions')}`",
            f"- Strict net harm: `{fmt(strict_failure.get('strict_net_harm_cents'))}c`",
            "",
            "| window | rows | harmful suppressions | net harm | avoided by v1/v2 | top tags |",
            "|---|---:|---:|---:|---:|---|",
        ])
        for row in strict_summaries:
            tag_bits = ", ".join(
                f"{tag}:{count}"
                for tag, count in list((row.get("tag_counts") or {}).items())[:5]
            )
            lines.append(
                f"| {row.get('window')} | {row.get('rows')} | {row.get('harmful_suppressions')} | "
                f"{fmt(row.get('net_harm_cents'))} | {row.get('avoided_by_v1')}/{row.get('avoided_by_v2')} | "
                f"{tag_bits or 'none'} |"
            )
    dashboard = report.get("exit_policy_watch_dashboard") or {}
    dashboard_rows = dashboard.get("rows") or []
    if dashboard_rows:
        lines.extend([
            "",
            "## Exit Policy Watch Dashboard",
            "",
            f"- Status counts: `{dashboard.get('status_counts')}`",
            "",
            "| lane | status | settled | suppressed | current c | candidate c | delta c | loss cost c | blockers |",
            "|---|---|---:|---:|---:|---:|---:|---:|---|",
        ])
        for row in dashboard_rows:
            lines.append(
                f"| {row.get('lane')} | {row.get('status')} | {row.get('settled')} | "
                f"{row.get('suppressed_exits')} | {fmt(row.get('current_net_cents'))} | "
                f"{fmt(row.get('candidate_net_cents'))} | {fmt(row.get('delta_vs_current_cents'))} | "
                f"{fmt(row.get('loss_control_cost_cents'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
            )
    lines.extend([
        "",
        "## Blocker Families",
        "",
        "| family | count |",
        "|---|---:|",
    ])
    for family, count in report.get("blocker_family_counts", {}).items():
        lines.append(f"| {family} | {count} |")
    lines.extend([
        "",
        "## Target-Coverage Loss Tags",
        "",
        "| tag | settled | W/L | net c | avg c |",
        "|---|---:|---:|---:|---:|",
    ])
    for row in (report.get("target_loss_attribution") or {}).get("tag_summaries", [])[:8]:
        if int(row.get("settled") or 0) == 0:
            continue
        lines.append(
            f"| {row.get('tag')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    price = report.get("target_price_friction") or {}
    price_summary = price.get("summary") or {}
    if price:
        lines.extend([
            "",
            "## Target-Coverage Price Friction",
            "",
            f"- Entries/settled/coverage: `{price_summary.get('rows')}/{price_summary.get('settled')}/{fmt(price_summary.get('coverage_pct'))}`",
            f"- Net cents: `{fmt(price_summary.get('net_cents'))}`",
            "",
            "| tag | settled | W/L | win rate | net c | avg ask | avg edge |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ])
        for row in (price.get("tag_rollups") or [])[:8]:
            if int(row.get("settled") or 0) == 0:
                continue
            lines.append(
                f"| {row.get('bucket')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
                f"{fmt(row.get('win_rate'))} | {fmt(row.get('net_cents'))} | "
                f"{fmt(row.get('avg_ask'))} | {fmt(row.get('avg_raw_edge'))} |"
            )
    cluster_runway = report.get("target_cluster_penalty_runway") or {}
    post_cluster = cluster_runway.get("post_birth_runway") or {}
    post_source = post_cluster.get("source_runway") or {}
    source_feasibility = report.get("target_cluster_penalty_source_feasibility") or {}
    feasibility_lanes = source_feasibility.get("lanes") or []
    feasibility_post = next((row for row in feasibility_lanes if row.get("lane") == "post_cluster_penalty_birth"), {})
    feasibility_best = feasibility_post.get("best") or {}
    displacement = report.get("target_cluster_penalty_source_displacement") or {}
    displacement_lanes = displacement.get("lanes") or []
    displacement_post = next((row for row in displacement_lanes if row.get("lane") == "post_cluster_penalty_birth"), {})
    displacement_best = displacement_post.get("best") or {}
    displacement_rejected = displacement_best.get("selected_rejected_summary") or {}
    displacement_omitted = displacement_best.get("omitted_approved_summary") or {}
    source_aware = report.get("target_cluster_penalty_source_aware") or {}
    source_aware_lanes = source_aware.get("lanes") or []
    source_aware_diag = next((row for row in source_aware_lanes if row.get("lane") == "diagnostic_target_window"), {})
    source_aware_post = next((row for row in source_aware_lanes if row.get("lane") == "post_source_aware_birth"), {})
    source_aware_diag_best = (source_aware_diag.get("variants") or [{}])[0]
    source_aware_post_best = (source_aware_post.get("variants") or [{}])[0]
    source_aware_diag_summary = source_aware_diag_best.get("candidate_summary") or {}
    source_aware_post_summary = source_aware_post_best.get("candidate_summary") or {}
    observable_stability = report.get("target_cluster_penalty_observable_stability") or {}
    observable_lanes = observable_stability.get("lanes") or []
    observable_diag = next((row for row in observable_lanes if row.get("lane") == "diagnostic_target_window"), {})
    observable_post = next((row for row in observable_lanes if row.get("lane") == "post_observable_proxy_birth"), {})
    observable_diag_best = (observable_diag.get("variants") or [{}])[0]
    observable_post_best = (observable_post.get("variants") or [{}])[0]
    observable_diag_summary = observable_diag_best.get("candidate_summary") or {}
    observable_post_summary = observable_post_best.get("candidate_summary") or {}
    if post_cluster:
        lines.extend([
            "",
            "## Target Cluster-Penalty Runway",
            "",
            f"- Post-birth settled/coverage/net: `{post_cluster.get('settled')}/{fmt(post_cluster.get('coverage_pct'))}/{fmt(post_cluster.get('net_cents'))}c`",
            f"- Reconstructed share: `{fmt(post_source.get('reconstructed_share'))}`",
            f"- Rows/clean rows/cushion needed: `{post_cluster.get('future_settled_rows_needed_for_sample')}/{post_source.get('future_clean_approved_rows_needed_for_source_gate')}/{fmt(post_cluster.get('future_net_cents_needed_for_cushion3'))}c`",
            f"- Source feasible now: `{feasibility_best.get('source_gate_feasible_at_current_denominator')}` with `{feasibility_best.get('approved_available_markets')}/{feasibility_best.get('required_entries_for_75pct_coverage')}` approved/required markets and minimum reconstructed share `{fmt(feasibility_best.get('minimum_reconstructed_share_for_75pct_coverage'))}`",
            f"- Source displacement net: selected rejected `{fmt(displacement_rejected.get('net_cents'))}c`; omitted approved `{fmt(displacement_omitted.get('net_cents'))}c`",
            f"- Blockers: `{', '.join(post_cluster.get('blockers') or []) or 'none'}`",
        ])
    if source_aware:
        lines.extend([
            "",
            "## Source-Aware Cluster-Penalty Watch",
            "",
            f"- Freeze UTC: `{(source_aware.get('state') or {}).get('freeze_ts_utc')}`",
            f"- Diagnostic cleanest: `{source_aware_diag_best.get('candidate')}` settled/coverage/net/recon "
            f"`{source_aware_diag_summary.get('settled')}/{fmt(source_aware_diag_summary.get('coverage_pct'))}/{fmt(source_aware_diag_summary.get('net_cents'))}c/{fmt(source_aware_diag_best.get('reconstructed_share'))}`",
            f"- Strict post-birth cleanest: `{source_aware_post_best.get('candidate')}` settled/coverage/net/recon "
            f"`{source_aware_post_summary.get('settled')}/{fmt(source_aware_post_summary.get('coverage_pct'))}/{fmt(source_aware_post_summary.get('net_cents'))}c/{fmt(source_aware_post_best.get('reconstructed_share'))}`",
            f"- Blockers: `{', '.join(source_aware_post_best.get('blockers') or []) or 'none'}`",
        ])
    if observable_stability:
        observable_diag_runway = observable_diag_best.get("runway") or {}
        observable_post_runway = observable_post_best.get("runway") or {}
        lines.extend([
            "",
            "## Observable Stability Cluster-Penalty Proxy",
            "",
            f"- Freeze UTC: `{(observable_stability.get('state') or {}).get('freeze_ts_utc')}`",
            f"- Diagnostic best: `{observable_diag_best.get('candidate')}` settled/coverage/net/recon "
            f"`{observable_diag_summary.get('settled')}/{fmt(observable_diag_summary.get('coverage_pct'))}/{fmt(observable_diag_summary.get('net_cents'))}c/{fmt(observable_diag_best.get('reconstructed_share'))}`",
            f"- Diagnostic rows/clean/cushion needed: `{observable_diag_runway.get('settled_rows_needed_for_sample')}/{observable_diag_runway.get('clean_approved_rows_needed_for_source_gate')}/{fmt(observable_diag_runway.get('net_cents_needed_for_cushion3'))}c`",
            f"- Strict post-birth best: `{observable_post_best.get('candidate')}` settled/coverage/net/recon "
            f"`{observable_post_summary.get('settled')}/{fmt(observable_post_summary.get('coverage_pct'))}/{fmt(observable_post_summary.get('net_cents'))}c/{fmt(observable_post_best.get('reconstructed_share'))}`",
            f"- Strict post-birth rows/clean/cushion needed: `{observable_post_runway.get('settled_rows_needed_for_sample')}/{observable_post_runway.get('clean_approved_rows_needed_for_source_gate')}/{fmt(observable_post_runway.get('net_cents_needed_for_cushion3'))}c`",
            f"- Blockers: `{', '.join(observable_post_best.get('blockers') or []) or 'none'}`",
        ])
    clean_broad_frontier = report.get("feature_gate_clean_broad_frontier") or {}
    clean_broad_lanes = clean_broad_frontier.get("lanes") or []
    clean_broad_diag = [
        row for row in clean_broad_lanes
        if isinstance(row, dict) and str(row.get("lane") or "").startswith("diagnostic_parent_")
    ]
    clean_broad_post = [
        row for row in clean_broad_lanes
        if isinstance(row, dict) and str(row.get("lane") or "").startswith("post_clean_broad_freeze_")
    ]
    if clean_broad_lanes:
        best_diag = clean_broad_diag[0] if clean_broad_diag else {}
        best_post = clean_broad_post[0] if clean_broad_post else {}
        diag_summary = best_diag.get("candidate_summary") or {}
        post_summary = best_post.get("candidate_summary") or {}
        lines.extend([
            "",
            "## Clean-Broad Feature-Gate Frontier Watch",
            "",
            f"- Freeze UTC: `{(clean_broad_frontier.get('state') or {}).get('freeze_ts_utc')}`",
            f"- Rule: `{(clean_broad_frontier.get('state') or {}).get('candidate')}`",
            f"- Diagnostic parent: `{diag_summary.get('settled')}/{fmt(diag_summary.get('coverage_pct'))}/{fmt(diag_summary.get('net_cents'))}c/recon {fmt(best_diag.get('reconstructed_share'))}`",
            f"- Strict post-freeze: `{post_summary.get('settled')}/{fmt(post_summary.get('coverage_pct'))}/{fmt(post_summary.get('net_cents'))}c/recon {fmt(best_post.get('reconstructed_share'))}`",
            f"- Strict pending unsettled rows: `{best_post.get('pending_unsettled_rows') or 0}`",
            f"- Blockers: `{', '.join(best_post.get('blockers') or []) or 'none'}`",
        ])
    near_promotion = report.get("feature_gate_near_promotion_watch") or {}
    near_attr = report.get("feature_gate_near_promotion_exit_attribution") or {}
    near_gap = report.get("feature_gate_near_promotion_denominator_gap") or {}
    near_rows = near_promotion.get("rows") or []
    if near_rows:
        best_near = near_rows[0]
        counter = near_gap.get("top_counterfactual_added_omitted_rows") or {}
        lines.extend([
            "",
            "## Near-Promotion Feature-Gate Watch",
            "",
            f"- Best candidate: `{near_promotion.get('best_candidate')}`",
            f"- Settled/pending/pending approved: `{best_near.get('settled')}/{best_near.get('pending')}/{best_near.get('pending_approved')}`",
            f"- W/L, coverage, net: `{best_near.get('wins')}/{best_near.get('losses')}` / `{fmt(best_near.get('coverage_pct'))}%` / `{fmt(best_near.get('net_cents'))}c`",
            f"- Reconstructed share/cushion: `{fmt(best_near.get('reconstructed_share'))}` / `{best_near.get('full_loss_cushion')}`",
            f"- Rows/cushion needed: coverage `{best_near.get('coverage_entries_needed')}`, clean `{best_near.get('clean_rows_needed_for_source') or 0}`, settled `{best_near.get('settled_rows_needed')}`, cushion `{fmt(best_near.get('net_cents_needed_for_cushion3'))}c`, avg future `{fmt(best_near.get('avg_future_net_needed_for_cushion3'))}c/row`",
            f"- Missing gates: `{', '.join(near_promotion.get('best_missing_gates') or []) or 'none'}`",
            f"- Loss source counts: `{near_attr.get('loss_source_counts') or {}}`",
            f"- Failure classes: `{near_attr.get('failure_class_counts') or {}}`",
            f"- Denominator gap: omitted reasons `{near_gap.get('omitted_fail_reason_counts') or {}}`, omitted sources `{near_gap.get('omitted_source_counts') or {}}`, counterfactual source gate `{counter.get('source_gate_if_added')}`",
        ])
    raw03_autopsy = report.get("feature_gate_raw03_vs_raw05_autopsy") or {}
    raw05_gap = report.get("feature_gate_raw05_coverage_gap_audit") or {}
    if raw03_autopsy or raw05_gap:
        autopsy_entry = next(
            (lane for lane in raw03_autopsy.get("lanes") or [] if lane.get("lane") == "post_feature_freeze_entry"),
            {},
        )
        autopsy_bridge = next(
            (lane for lane in raw03_autopsy.get("lanes") or [] if lane.get("lane") == "post_feature_freeze_bridge"),
            {},
        )
        gap_entry = next(
            (lane for lane in raw05_gap.get("lanes") or [] if lane.get("lane") == "post_feature_freeze_entry"),
            {},
        )
        gap_bridge = next(
            (lane for lane in raw05_gap.get("lanes") or [] if lane.get("lane") == "post_feature_freeze_bridge"),
            {},
        )
        entry_raw05 = (autopsy_entry.get("raw05") or {}).get("summary") or {}
        entry_raw03 = (autopsy_entry.get("raw03") or {}).get("summary") or {}
        entry_marginal = autopsy_entry.get("marginal_raw03_minus_raw05") or {}
        bridge_raw05 = (autopsy_bridge.get("raw05") or {}).get("summary") or {}
        bridge_raw03 = (autopsy_bridge.get("raw03") or {}).get("summary") or {}
        bridge_marginal = autopsy_bridge.get("marginal_raw03_minus_raw05") or {}
        entry_any = gap_entry.get("best_any_source_oracle_add_missing") or {}
        bridge_any = gap_bridge.get("best_any_source_oracle_add_missing") or {}
        lines.extend([
            "",
            "## Feature-Gate raw05 Coverage Gap",
            "",
            f"- raw05 entry: `{entry_raw05.get('entries')}` entries, `{entry_raw05.get('settled')}` settled, "
            f"`{fmt(entry_raw05.get('coverage_pct'))}%` coverage, `{fmt(entry_raw05.get('net_cents'))}c`, "
            f"recon `{fmt(entry_raw05.get('reconstructed_share'))}`",
            f"- raw03 entry: `{entry_raw03.get('entries')}` entries, `{entry_raw03.get('settled')}` settled, "
            f"`{fmt(entry_raw03.get('coverage_pct'))}%` coverage, `{fmt(entry_raw03.get('net_cents'))}c`, "
            f"recon `{fmt(entry_raw03.get('reconstructed_share'))}`",
            f"- raw03-only entry slice: `{(entry_marginal.get('summary') or {}).get('entries')}` rows, "
            f"sources `{entry_marginal.get('source_counts') or {}}`, W/L `{entry_marginal.get('wins')}/{entry_marginal.get('losses')}`, "
            f"net `{fmt(entry_marginal.get('net_cents'))}c`",
            f"- raw05 bridge: `{bridge_raw05.get('entries')}` entries, `{bridge_raw05.get('settled')}` settled, "
            f"`{fmt(bridge_raw05.get('coverage_pct'))}%` coverage, `{fmt(bridge_raw05.get('net_cents'))}c`, "
            f"recon `{fmt(bridge_raw05.get('reconstructed_share'))}`",
            f"- raw03 bridge: `{bridge_raw03.get('entries')}` entries, `{bridge_raw03.get('settled')}` settled, "
            f"`{fmt(bridge_raw03.get('coverage_pct'))}%` coverage, `{fmt(bridge_raw03.get('net_cents'))}c`, "
            f"recon `{fmt(bridge_raw03.get('reconstructed_share'))}`",
            f"- raw03-only bridge slice: `{(bridge_marginal.get('summary') or {}).get('entries')}` rows, "
            f"sources `{bridge_marginal.get('source_counts') or {}}`, W/L `{bridge_marginal.get('wins')}/{bridge_marginal.get('losses')}`, "
            f"net `{fmt(bridge_marginal.get('net_cents'))}c`",
            f"- raw05 omitted entry rows: sources `{gap_entry.get('omitted_source_counts') or {}}`, "
            f"fail reasons `{gap_entry.get('omitted_fail_reason_counts') or {}}`, "
            f"best-any-source oracle blockers `{', '.join(entry_any.get('blockers') or []) or 'none'}`",
            f"- raw05 omitted bridge rows: sources `{gap_bridge.get('omitted_source_counts') or {}}`, "
            f"fail reasons `{gap_bridge.get('omitted_fail_reason_counts') or {}}`, "
            f"best-any-source oracle blockers `{', '.join(bridge_any.get('blockers') or []) or 'none'}`",
        ])
    core_expansion = report.get("feature_gate_core_expansion_mix") or {}
    mix_rows = core_expansion.get("rows") or []
    if mix_rows:
        best_mix = mix_rows[0]
        lines.extend([
            "",
            "## Feature-Gate Core/Expansion Mix",
            "",
            f"- Core: `{core_expansion.get('core_candidate')}`",
            f"- Broad parent: `{core_expansion.get('broad_candidate')}`",
            f"- Any live-ready mix: `{core_expansion.get('any_live_ready')}`",
            f"- Best mix: `{best_mix.get('policy')}` settled/W-L/coverage/net "
            f"`{best_mix.get('entries')} entries, {best_mix.get('settled')} settled/{best_mix.get('wins')}-{best_mix.get('losses')}/{fmt(best_mix.get('coverage_pct'))}%/{fmt(best_mix.get('weighted_net_cents'))}c`",
            f"- Row/exposure source: `{fmt(best_mix.get('row_source_share'))}/{fmt(best_mix.get('exposure_source_share'))}`",
            f"- Cushion/blockers: `{best_mix.get('full_loss_cushion')}` / `{', '.join(best_mix.get('blockers') or []) or 'none'}`",
        ])
    coverage_repair = report.get("feature_gate_coverage_repair") or {}
    repair_lanes = coverage_repair.get("lanes") or []
    if repair_lanes:
        lines.extend([
            "",
            "## Feature-Gate Coverage Repair",
            "",
        ])
        for lane in repair_lanes:
            near = (lane.get("near_misses") or [{}])[0]
            summary = near.get("summary") or {}
            added = near.get("added_summary") or {}
            anchor = lane.get("anchor_summary") or {}
            lines.extend([
                f"- `{lane.get('lane')}` anchor `{lane.get('anchor_rule')}`: "
                f"`{anchor.get('entries')}/{lane.get('future_denominator')}` entries, "
                f"W/L `{anchor.get('wins')}/{anchor.get('losses')}`, net `{fmt(anchor.get('net_cents'))}c`, "
                f"recon `{fmt(anchor.get('reconstructed_share'))}`",
                f"- nearest relaxation `{near.get('rule')}`: "
                f"`{summary.get('entries')}/{lane.get('future_denominator')}` entries, "
                f"W/L `{summary.get('wins')}/{summary.get('losses')}`, coverage `{fmt(summary.get('coverage_pct'))}%`, "
                f"net `{fmt(summary.get('net_cents'))}c`, recon `{fmt(summary.get('reconstructed_share'))}`, "
                f"added net `{fmt(added.get('net_cents'))}c`, blockers `{', '.join(near.get('blockers') or []) or 'none'}`",
            ])
    coverage_size_shrink = report.get("feature_gate_coverage_size_shrink") or {}
    coverage_size_exit_attr = report.get("feature_gate_coverage_size_shrink_exit_attribution") or {}
    coverage_size_runway = report.get("feature_gate_coverage_size_shrink_runway") or {}
    shrink_lanes = coverage_size_shrink.get("lanes") or []
    if shrink_lanes:
        lines.extend([
            "",
            "## Feature-Gate Coverage Size Shrink",
            "",
        ])
        for lane in shrink_lanes:
            best = (lane.get("rows") or [{}])[0]
            attr = next(
                (row for row in coverage_size_exit_attr.get("lanes") or [] if row.get("lane") == lane.get("lane")),
                {},
            )
            runway = next(
                (row for row in coverage_size_runway.get("lanes") or [] if row.get("lane") == lane.get("lane")),
                {},
            )
            first_viable = runway.get("first_viable_clean_scenario") or {}
            lines.append(
                f"- `{lane.get('lane')}` best `{best.get('policy')}`: "
                f"`{best.get('entries')}/{lane.get('future_denominator')}` entries, "
                f"W/L `{best.get('wins')}/{best.get('losses')}`, coverage `{fmt(best.get('coverage_pct'))}%`, "
                f"weighted net `{fmt(best.get('weighted_net_cents'))}c`, "
                f"row/exposure recon `{fmt(best.get('row_reconstructed_share'))}/{fmt(best.get('exposure_reconstructed_share'))}`, "
                f"cushion `{best.get('full_loss_cushion')}`, blockers `{', '.join(best.get('blockers') or []) or 'none'}`, "
                f"exit classes `{attr.get('failure_class_counts') or {}}`, "
                f"runway clean rows `{runway.get('clean_selected_rows_needed_for_source')}`, "
                f"delta vs live `{fmt(runway.get('delta_vs_live_cents'))}c`, "
                f"first viable `{first_viable}`"
            )
    lines.extend([
        "",
        "## Best Current Candidates By Triage Score",
        "",
        "| gate | policy | entries | settled | coverage | net c | brier | live ready | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ])
    for row in report.get("best_candidates") or []:
        blockers = ", ".join((row.get("blockers") or [])[:5])
        if len(row.get("blockers") or []) > 5:
            blockers += ", ..."
        lines.append(
            f"| {row.get('gate')} | {row.get('policy')} | {row.get('entries')} | {row.get('settled')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_brier'))} | "
            f"{row.get('live_ready')} | {blockers or 'none'} |"
        )
    lines.extend([
        "",
        "## Exit Lanes",
        "",
        "| lane | candidate | settled | delta c | suppressed | winner recovery | loss cost | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("exit_lanes") or []:
        lines.append(
            f"| {row.get('label')} | {row.get('candidate')} | {row.get('settled')} | "
            f"{fmt(row.get('delta_vs_current_cents'))} | {row.get('suppressed_exits')} | "
            f"{fmt(row.get('winner_clip_recovered_cents'))} | {fmt(row.get('loss_control_cost_cents'))} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    runway = (report.get("exit_reduce_runway") or {}).get("runway") or {}
    if runway:
        lines.extend([
            "",
            "## Exit Reduce Runway",
            "",
            f"- Rows needed for 30: `{runway.get('rows_needed_for_30')}`",
            f"- Current delta: `{fmt(runway.get('current_delta_cents'))}c`",
            f"- Suppressed exits: `{runway.get('current_suppressed_exits')}`",
            f"- Invalidators now: `{', '.join((report.get('exit_reduce_runway') or {}).get('invalidators_now') or []) or 'none'}`",
        ])
    drift_audit = report.get("exit_reduce_drift_audit") or {}
    if drift_audit:
        drift_overall = drift_audit.get("overall") or {}
        before_latest = drift_audit.get("before_latest_suppression") or {}
        latest = drift_audit.get("latest_suppression") or {}
        lines.extend([
            "",
            "## Exit Reduce Suppression Drift",
            "",
            f"- Suppressed exits/net delta: `{drift_overall.get('rows')}/{fmt(drift_overall.get('net_delta_cents'))}c`",
            f"- Helpful/harmful delta: `{fmt(drift_overall.get('helpful_delta_cents'))}c/{fmt(drift_overall.get('harmful_delta_cents'))}c`",
            f"- Before latest suppression: `{fmt(before_latest.get('net_delta_cents'))}c`",
            f"- Latest suppression: `{latest.get('market')}` `{fmt(latest.get('delta_cents'))}c` tags `{', '.join(latest.get('tags') or []) or 'none'}`",
        ])
    drift_guard = report.get("exit_reduce_drift_guard_watch") or {}
    if drift_guard:
        best_diag = (drift_guard.get("diagnostic_since_base_freeze") or [{}])[0]
        best_post = (drift_guard.get("post_drift_guard_birth") or [{}])[0]
        lines.extend([
            "",
            "## Exit Reduce Drift-Guard Watch",
            "",
            f"- Freeze UTC: `{(drift_guard.get('state') or {}).get('freeze_ts_utc')}`",
            f"- Best diagnostic: `{best_diag.get('policy')}` suppressed W/L `{best_diag.get('suppressed_helpful')}/{best_diag.get('suppressed_harmful')}` delta `{fmt(best_diag.get('delta_vs_current_cents'))}c`",
            f"- Best strict post-birth: `{best_post.get('policy')}` settled/suppressed/delta `{best_post.get('settled')}/{best_post.get('suppressed')}/{fmt(best_post.get('delta_vs_current_cents'))}c`",
            f"- Blockers: `{', '.join(best_post.get('blockers') or []) or 'none'}`",
        ])
    actionability = report.get("exit_reduce_actionability") or {}
    best_hindsight = actionability.get("best_hindsight") or {}
    best_observable = actionability.get("best_observable") or {}
    if best_hindsight or best_observable:
        lines.extend([
            "",
            "## Exit Reduce Loss-Control Actionability",
            "",
            f"- Best overall separator: `{best_hindsight.get('feature')} {best_hindsight.get('direction')} {best_hindsight.get('threshold')}` (hindsight-only)",
            f"- Best observable separator: `{best_observable.get('feature')} {best_observable.get('direction')} {best_observable.get('threshold')}`",
            f"- Observable selected W/L and delta: `{best_observable.get('selected_helpful')}/{best_observable.get('selected_harmful')} / {fmt(best_observable.get('selected_delta_cents'))}c`",
            f"- Existing frozen watch: `{best_observable.get('frozen_watch')}`",
        ])
    observable_opportunity = report.get("exit_reduce_observable_loss_control_opportunity") or {}
    observable_rules = observable_opportunity.get("rules") or []
    if observable_rules:
        best_observable_opp = observable_rules[0]
        lines.extend([
            "",
            "## Exit Reduce Observable Loss-Control Opportunity",
            "",
            f"- Freeze UTC: `{observable_opportunity.get('observable_loss_control_freeze_ts_utc')}`",
            f"- First rule rows/reduce/p-hold/would-suppress: `{best_observable_opp.get('total_rows')}/{best_observable_opp.get('probability_reduce_rows')}/{best_observable_opp.get('p_hold_candidate_rows')}/{best_observable_opp.get('would_suppress_rows')}`",
            f"- First rule delta if suppressed: `{fmt(best_observable_opp.get('would_suppress_delta_cents'))}c`",
            f"- First rule fail reasons: `{best_observable_opp.get('fail_reason_counts')}`",
        ])
    observable_false_hold = report.get("exit_reduce_observable_false_hold_autopsy") or {}
    if observable_false_hold:
        windows = observable_false_hold.get("windows") or []
        diagnostic_window = next((row for row in windows if row.get("window") == "diagnostic_from_reduce_freeze"), {})
        post_window = next((row for row in windows if row.get("window") == "post_observable_birth"), {})
        diagnostic_summary = diagnostic_window.get("candidate_summary") or {}
        post_summary = post_window.get("candidate_summary") or {}
        best_post_guard = (post_window.get("zero_harm_guards") or post_window.get("best_guards") or [{}])[0]
        lines.extend([
            "",
            "## Exit Reduce Observable False-Hold Autopsy",
            "",
            f"- Reduce/observable freeze UTC: `{observable_false_hold.get('reduce_freeze_ts_utc')}` / `{observable_false_hold.get('observable_freeze_ts_utc')}`",
            f"- Diagnostic p-hold reduce denominator rows/net/helpful-harmful/harmful: `{diagnostic_summary.get('rows')}/{fmt(diagnostic_summary.get('net_delta_cents'))}c/{diagnostic_summary.get('helpful_rows')}-{diagnostic_summary.get('harmful_rows')}/{fmt(diagnostic_summary.get('harmful_delta_cents'))}c`",
            f"- Post-birth p-hold reduce denominator rows/net/helpful-harmful/harmful: `{post_summary.get('rows')}/{fmt(post_summary.get('net_delta_cents'))}c/{post_summary.get('helpful_rows')}-{post_summary.get('harmful_rows')}/{fmt(post_summary.get('harmful_delta_cents'))}c`",
            f"- Best post-birth zero-harm split: `{best_post_guard.get('feature')} {best_post_guard.get('direction')} {best_post_guard.get('threshold')}` rows/net `{best_post_guard.get('selected_rows')}/{fmt(best_post_guard.get('net_delta_cents'))}c`",
        ])
    midband_rescue = report.get("exit_midband_reduce_rescue") or {}
    if midband_rescue:
        best_diag = (midband_rescue.get("diagnostic") or [{}])[0]
        best_post = (midband_rescue.get("post_birth") or [{}])[0]
        lines.extend([
            "",
            "## Exit Midband Reduce Rescue Watch",
            "",
            f"- Freeze UTC: `{(midband_rescue.get('state') or {}).get('freeze_ts_utc')}`",
            f"- Diagnostic best: `{best_diag.get('candidate')}` suppressed/delta/helpful-harmful "
            f"`{best_diag.get('suppressed')}/{fmt(best_diag.get('delta_vs_current_cents'))}c/"
            f"{best_diag.get('helpful_suppressions')}-{best_diag.get('harmful_suppressions')}`",
            f"- Strict post-birth rows/suppressed/delta: `{best_post.get('rows')}/{best_post.get('suppressed')}/{fmt(best_post.get('delta_vs_current_cents'))}c`",
            f"- Blockers: `{', '.join(best_post.get('blockers') or []) or 'none'}`",
        ])
    geometry_opportunity = (report.get("exit_reduce_geometry_opportunity") or {}).get("summary") or {}
    if geometry_opportunity:
        lines.extend([
            "",
            "## Exit Reduce Geometry Opportunity",
            "",
            f"- Probability-reduce/base/geometry rows: `{geometry_opportunity.get('probability_reduce_rows')}/{geometry_opportunity.get('base_p_hold_candidates')}/{geometry_opportunity.get('geometry_would_suppress_rows')}`",
            f"- Rejected base candidates/delta: `{geometry_opportunity.get('geometry_rejected_base_candidates')}/{fmt(geometry_opportunity.get('geometry_rejected_base_delta_cents'))}c`",
            f"- Blockers: `{', '.join(geometry_opportunity.get('blockers') or []) or 'none'}`",
        ])
    relaxed_watch = report.get("exit_reduce_geometry_relaxed_watch") or {}
    relaxed_summary = relaxed_watch.get("summary") or {}
    relaxed_diag = ((relaxed_watch.get("diagnostic") or {}).get("best") or {})
    if relaxed_watch:
        lines.extend([
            "",
            "## Exit Reduce Relaxed Geometry Watch",
            "",
            f"- Freeze UTC: `{(relaxed_watch.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Diagnostic best: `{relaxed_diag.get('policy')}` delta/suppressed W-L `{fmt(relaxed_diag.get('delta_vs_current_cents'))}c/{relaxed_diag.get('suppressed_winners')}/{relaxed_diag.get('suppressed_losers')}`",
            f"- Strict settled/suppressed/delta: `{relaxed_summary.get('settled')}/{relaxed_summary.get('suppressed')}/{fmt(relaxed_summary.get('delta_vs_current_cents'))}c`",
            f"- Blockers: `{', '.join(relaxed_watch.get('blockers') or []) or 'none'}`",
        ])
    value_only_opportunity = report.get("exit_book_gap_value_only_opportunity") or {}
    if value_only_opportunity:
        lines.extend([
            "",
            "## Exit Book-Gap Value-Only Opportunity",
            "",
            f"- Rows/value exits/would suppress: `{value_only_opportunity.get('total_rows')}/{value_only_opportunity.get('value_over_hold_rows')}/{value_only_opportunity.get('would_suppress_rows')}`",
            f"- Suppressed W/L and delta: `{value_only_opportunity.get('would_suppress_winners')}/{value_only_opportunity.get('would_suppress_losers')} / {fmt(value_only_opportunity.get('would_suppress_delta_cents'))}c`",
            f"- Fail reasons: `{value_only_opportunity.get('fail_reason_counts')}`",
        ])
    value_reduce_opportunity = (report.get("exit_value_reduce_depth_opportunity") or {}).get("primary") or {}
    if value_reduce_opportunity:
        lines.extend([
            "",
            "## Exit Value + Reduce-Depth Opportunity",
            "",
            f"- Rows/value exits/reduce exits: `{value_reduce_opportunity.get('total_rows')}/{value_reduce_opportunity.get('value_over_hold_rows')}/{value_reduce_opportunity.get('probability_reduce_rows')}`",
            f"- Would suppress value/reduce and delta: `{value_reduce_opportunity.get('would_suppress_value_rows')}/{value_reduce_opportunity.get('would_suppress_reduce_rows')} / {fmt(value_reduce_opportunity.get('would_suppress_delta_cents'))}c`",
            f"- Rows/suppressions/cushion needed: `{value_reduce_opportunity.get('rows_needed')}/{value_reduce_opportunity.get('suppressed_needed')}/{fmt(value_reduce_opportunity.get('net_cents_needed_for_cushion3'))}c`",
            f"- Fail reasons: `{value_reduce_opportunity.get('fail_reason_counts')}`",
        ])
    v1_v2_runway = report.get("exit_loss_guard_v1_v2_runway") or {}
    variant_runways = v1_v2_runway.get("strict_variant_runways") or []
    v2_summary = v1_v2_runway.get("v2_summary") or {}
    v2_promotion = v1_v2_runway.get("v2_strict_runway") or {}
    v1_only_cost = v2_promotion.get("v1_only_opportunity_cost_cents")
    if v2_summary or v2_promotion or variant_runways:
        lines.extend([
            "",
            "## Exit Loss-Guard V1/V2/V3 Runway",
            "",
            f"- V2 strict settled: `{v2_promotion.get('settled')}`",
            f"- V2 suppressions/delta: `{v2_promotion.get('v2_suppressed_decisions')}/{fmt(v2_promotion.get('v2_delta_cents'))}c`",
            f"- V1-only opportunity cost after v2 freeze: `{fmt(v1_only_cost)}c`",
            f"- Rows/suppressions/cushion needed: `{v2_promotion.get('rows_needed')}/{v2_promotion.get('v2_suppressed_needed')}/{fmt(v2_promotion.get('net_cents_needed_for_cushion3'))}c`",
            f"- Blockers: `{', '.join(v2_promotion.get('blockers') or []) or 'none'}`",
        ])
        if variant_runways:
            lines.extend([
                "",
                "| variant | settled | suppressions | delta c | rows needed | suppressions needed | cushion c needed | blockers |",
                "|---|---:|---:|---:|---:|---:|---:|---|",
            ])
            for row in variant_runways:
                lines.append(
                    f"| {row.get('variant')} | {row.get('settled')} | {row.get('suppressed_decisions')} | "
                    f"{fmt(row.get('delta_cents'))} | {row.get('rows_needed')} | {row.get('suppressed_needed')} | "
                    f"{fmt(row.get('net_cents_needed_for_cushion3'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
                )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
