"""Current direction decision for the v28 FV improvement goal.

Research-only; no live bot changes or orders.

This synthesizes the latest forward artifacts into a small decision ledger so
the ongoing work stays pointed at durable, physics-backed candidates instead of
chasing every fresh leaderboard wiggle.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_current_direction_decision_latest.json"
OUT_MD = OUT_DIR / "v28_current_direction_decision_latest.md"


FILES = {
    "goal_audit": OUT_DIR / "v28_goal_completion_audit_latest.json",
    "confidence_shrink": OUT_DIR / "v28_confidence_shrink_schedule_bakeoff_latest.json",
    "hybrid_shrink": OUT_DIR / "v28_hybrid_confidence_shrink_fv_latest.json",
    "raw_entry_calibration": OUT_DIR / "v28_frozen_raw_entry_calibrated_probability_latest.json",
    "early_no_boundary": OUT_DIR / "v28_frozen_early_no_boundary_decay_repair_entry_latest.json",
    "early_no_boundary_stress": OUT_DIR / "v28_early_no_boundary_decay_repair_stress_latest.json",
    "target_failure_clusters": OUT_DIR / "v28_target_coverage_failure_clusters_latest.json",
    "target_cluster_penalty_watch": OUT_DIR / "v28_target_coverage_cluster_penalty_watch_latest.json",
    "target_cluster_penalty_runway": OUT_DIR / "v28_target_cluster_penalty_runway_latest.json",
    "target_cluster_penalty_source_feasibility": OUT_DIR / "v28_target_cluster_penalty_source_feasibility_latest.json",
    "target_cluster_penalty_source_displacement": OUT_DIR / "v28_target_cluster_penalty_source_displacement_latest.json",
    "target_hybrid_veto": OUT_DIR / "v28_target_hybrid_veto_repair_latest.json",
    "hybrid_boundary_stack": OUT_DIR / "v28_hybrid_boundary_entry_stack_latest.json",
    "hybrid_boundary_stack_source_stress": OUT_DIR / "v28_hybrid_boundary_entry_stack_source_stress_latest.json",
    "hybrid_boundary_stack_stress": OUT_DIR / "v28_hybrid_boundary_entry_stack_stress_latest.json",
    "hybrid_boundary_source_frontier": OUT_DIR / "v28_hybrid_boundary_source_frontier_latest.json",
    "hybrid_boundary_source_dilution": OUT_DIR / "v28_hybrid_boundary_source_dilution_runway_latest.json",
    "boundary_clock_entry": OUT_DIR / "v28_frozen_boundary_clock_repair_entry_latest.json",
    "boundary_clock_fv_bridge": OUT_DIR / "v28_frozen_boundary_clock_fv_entry_bridge_latest.json",
    "boundary_clock_runway": OUT_DIR / "v28_boundary_clock_promotion_runway_latest.json",
    "boundary_clock_source_stress": OUT_DIR / "v28_boundary_clock_source_stress_latest.json",
    "boundary_clock_approved_frontier": OUT_DIR / "v28_boundary_clock_approved_oracle_frontier_latest.json",
    "boundary_clock_feature_gate": OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json",
    "feature_gate_near_promotion_watch": OUT_DIR / "v28_feature_gate_near_promotion_watch_latest.json",
    "feature_gate_near_promotion_denominator_gap": OUT_DIR / "v28_feature_gate_near_promotion_denominator_gap_latest.json",
    "feature_gate_pending_resolution_audit": OUT_DIR / "v28_feature_gate_pending_resolution_audit_latest.json",
    "feature_gate_outcome_linkage_overlay": OUT_DIR / "v28_feature_gate_outcome_linkage_overlay_latest.json",
    "feature_gate_linked_source_runway": OUT_DIR / "v28_feature_gate_linked_source_runway_latest.json",
    "feature_gate_live_outcome_alignment": OUT_DIR / "v28_feature_gate_live_outcome_alignment_latest.json",
    "feature_gate_live_exit_mismatch_drilldown": OUT_DIR / "v28_feature_gate_live_exit_mismatch_drilldown_latest.json",
    "feature_gate_live_exit_hold_counterfactual": OUT_DIR / "v28_feature_gate_live_exit_hold_counterfactual_latest.json",
    "feature_gate_exit_state_repair_frontier": OUT_DIR / "v28_feature_gate_exit_state_repair_frontier_latest.json",
    "feature_gate_value_exit_watch": OUT_DIR / "v28_frozen_feature_gate_value_exit_watch_latest.json",
    "value_exit_feature_gate_contrast": OUT_DIR / "v28_value_exit_feature_gate_contrast_latest.json",
    "value_exit_feature_side_guard": OUT_DIR / "v28_frozen_value_exit_feature_side_guard_latest.json",
    "feature_gate_exit_suppression_separator": OUT_DIR / "v28_feature_gate_exit_suppression_separator_latest.json",
    "feature_gate_exit_bid_suppression_watch": OUT_DIR / "v28_feature_gate_exit_bid_suppression_watch_latest.json",
    "feature_gate_exit_bid_path_risk": OUT_DIR / "v28_feature_gate_exit_bid_path_risk_latest.json",
    "feature_gate_exit_bid_delayed_recheck": OUT_DIR / "v28_frozen_feature_gate_exit_bid_delayed_recheck_latest.json",
    "soft_frontier_midprice_delayed_recheck_exit": OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_exit_latest.json",
    "soft_frontier_midprice_delayed_recheck_path_risk": OUT_DIR / "v28_soft_frontier_midprice_delayed_recheck_path_risk_latest.json",
    "soft_frontier_midprice_delayed_recheck_failure_modes": OUT_DIR / "v28_soft_frontier_midprice_delayed_recheck_failure_modes_latest.json",
    "soft_frontier_delayed_recheck_rescue_frontier": OUT_DIR / "v28_soft_frontier_delayed_recheck_rescue_frontier_latest.json",
    "soft_frontier_delayed_recheck_rescue_path_risk": OUT_DIR / "v28_soft_frontier_delayed_recheck_rescue_path_risk_latest.json",
    "soft_frontier_midprice_delayed_recheck_clean_rescue": OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_rescue_latest.json",
    "soft_frontier_delayed_recheck_clean_rescue_path_risk": OUT_DIR / "v28_soft_frontier_delayed_recheck_clean_rescue_path_risk_latest.json",
    "soft_frontier_delayed_recheck_disaster_guard": OUT_DIR / "v28_soft_frontier_delayed_recheck_disaster_guard_latest.json",
    "top_component_mix_portfolio": OUT_DIR / "v28_top_component_mix_portfolio_latest.json",
    "top_component_loss_cluster": OUT_DIR / "v28_top_component_loss_cluster_drilldown_latest.json",
    "top_component_false_negative_rescue": OUT_DIR / "v28_top_component_false_negative_rescue_child_latest.json",
    "top_component_parent_fill_repair": OUT_DIR / "v28_top_component_parent_fill_repair_child_latest.json",
    "top_component_observable_quarantine": OUT_DIR / "v28_top_component_observable_quarantine_child_latest.json",
    "top_component_strict_row_autopsy": OUT_DIR / "v28_top_component_strict_row_autopsy_latest.json",
    "feature_gate_near_promotion_exit_attribution": OUT_DIR / "v28_feature_gate_near_promotion_exit_attribution_latest.json",
    "feature_gate_core_expansion_mix": OUT_DIR / "v28_feature_gate_core_expansion_mix_latest.json",
    "feature_gate_coverage_repair": OUT_DIR / "v28_feature_gate_coverage_repair_latest.json",
    "feature_gate_coverage_size_shrink": OUT_DIR / "v28_feature_gate_coverage_size_shrink_latest.json",
    "feature_gate_size_shrink_source_slice": OUT_DIR / "v28_feature_gate_size_shrink_source_slice_latest.json",
    "feature_gate_middle_distance_core_watch": OUT_DIR / "v28_feature_gate_middle_distance_core_watch_latest.json",
    "feature_gate_middle_core_expansion_bound": OUT_DIR / "v28_feature_gate_middle_core_expansion_bound_latest.json",
    "feature_gate_middle_core_exit_attribution": OUT_DIR / "v28_feature_gate_middle_core_exit_attribution_latest.json",
    "feature_gate_middle_core_exit_guard_watch": OUT_DIR / "v28_feature_gate_middle_core_exit_guard_watch_latest.json",
    "feature_gate_size_shrink_strict_drilldown": OUT_DIR / "v28_feature_gate_size_shrink_strict_drilldown_latest.json",
    "feature_gate_coverage_size_shrink_exit_attribution": OUT_DIR / "v28_feature_gate_coverage_size_shrink_exit_attribution_latest.json",
    "feature_gate_coverage_size_shrink_runway": OUT_DIR / "v28_feature_gate_coverage_size_shrink_runway_latest.json",
    "feature_gate_observable_selection_mix": OUT_DIR / "v28_feature_gate_observable_selection_mix_latest.json",
    "feature_gate_size_shrink_exit_overlay": OUT_DIR / "v28_feature_gate_size_shrink_exit_overlay_latest.json",
    "feature_gate_size_shrink_delayed_recheck_exit": OUT_DIR / "v28_feature_gate_size_shrink_delayed_recheck_exit_latest.json",
    "feature_gate_size_shrink_delayed_recheck_rescue": OUT_DIR / "v28_feature_gate_size_shrink_delayed_recheck_rescue_latest.json",
    "feature_gate_source_confirmation_replacement": OUT_DIR / "v28_feature_gate_source_confirmation_replacement_latest.json",
    "feature_gate_late_collapse_recheck_rescue": OUT_DIR / "v28_feature_gate_late_collapse_recheck_rescue_latest.json",
    "feature_gate_dual_clock_recheck_rescue": OUT_DIR / "v28_feature_gate_dual_clock_recheck_rescue_latest.json",
    "feature_gate_confirmed_dual_clock_fill": OUT_DIR / "v28_feature_gate_confirmed_dual_clock_fill_latest.json",
    "feature_gate_confirmed_dual_clock_fill_stress": OUT_DIR / "v28_feature_gate_confirmed_dual_clock_fill_stress_latest.json",
    "feature_gate_source_quality_proxy": OUT_DIR / "v28_feature_gate_source_quality_proxy_latest.json",
    "feature_gate_source_proxy_coverage_repair": OUT_DIR / "v28_feature_gate_source_proxy_coverage_repair_latest.json",
    "feature_gate_source_proxy_strict_autopsy": OUT_DIR / "v28_feature_gate_source_proxy_strict_autopsy_latest.json",
    "feature_gate_source_blocker_mechanism": OUT_DIR / "v28_feature_gate_source_blocker_mechanism_latest.json",
    "high_win_core_broad_fill_mix": OUT_DIR / "v28_high_win_core_broad_fill_mix_latest.json",
    "p50_book_edge_source_failure_drilldown": OUT_DIR / "v28_p50_book_edge_source_failure_drilldown_latest.json",
    "p50_book_edge_source_feasibility_bound": OUT_DIR / "v28_p50_book_edge_source_feasibility_bound_latest.json",
    "p50_book_edge_no_side_shrink_watch": OUT_DIR / "v28_frozen_p50_book_edge_no_side_shrink_watch_latest.json",
    "p50_soft_frontier_overlap_mix": OUT_DIR / "v28_p50_soft_frontier_overlap_mix_latest.json",
    "boundary_clock_feature_gate_runway": OUT_DIR / "v28_boundary_clock_feature_gate_runway_latest.json",
    "boundary_clock_feature_gate_failure_modes": OUT_DIR / "v28_boundary_clock_feature_gate_failure_modes_latest.json",
    "boundary_clock_feature_gate_loss_analog": OUT_DIR / "v28_boundary_clock_feature_gate_loss_analog_monitor_latest.json",
    "boundary_clock_feature_gate_row_ledger": OUT_DIR / "v28_boundary_clock_feature_gate_row_ledger_latest.json",
    "boundary_clock_feature_gate_coverage_recovery": OUT_DIR / "v28_boundary_clock_feature_gate_coverage_recovery_latest.json",
    "boundary_clock_feature_gate_source_denominator": OUT_DIR / "v28_boundary_clock_feature_gate_source_denominator_audit_latest.json",
    "boundary_clock_feature_gate_coverage_source_frontier": OUT_DIR / "v28_boundary_clock_feature_gate_coverage_source_frontier_latest.json",
    "feature_gate_source_feasibility_bound": OUT_DIR / "v28_feature_gate_source_feasibility_bound_latest.json",
    "feature_gate_promotion_gap": OUT_DIR / "v28_feature_gate_promotion_gap_audit_latest.json",
    "boundary_clock_feature_gate_frontier_runway": OUT_DIR / "v28_boundary_clock_feature_gate_frontier_runway_latest.json",
    "boundary_clock_feature_gate_frontier_mechanism": OUT_DIR / "v28_boundary_clock_feature_gate_frontier_mechanism_latest.json",
    "boundary_clock_feature_gate_outlier_stress": OUT_DIR / "v28_boundary_clock_feature_gate_outlier_stress_latest.json",
    "boundary_clock_feature_gate_clean_broad_frontier": OUT_DIR / "v28_boundary_clock_feature_gate_clean_broad_frontier_watch_latest.json",
    "boundary_clock_feature_gate_soft_frontier": OUT_DIR / "v28_boundary_clock_feature_gate_soft_frontier_watch_latest.json",
    "soft_frontier_post_birth_failure_drilldown": OUT_DIR / "v28_soft_frontier_post_birth_failure_drilldown_latest.json",
    "feature_gate_cheap_tail_shrink_watch": OUT_DIR / "v28_frozen_feature_gate_cheap_tail_shrink_watch_latest.json",
    "soft_frontier_midprice_boundary_shrink": OUT_DIR / "v28_soft_frontier_midprice_boundary_shrink_latest.json",
    "midprice_source_dilution": OUT_DIR / "v28_midprice_source_dilution_watch_latest.json",
    "midprice_source_dilution_stability": OUT_DIR / "v28_midprice_source_dilution_stability_latest.json",
    "midprice_source_dilution_mechanism": OUT_DIR / "v28_midprice_source_dilution_mechanism_latest.json",
    "midprice_source_dilution_runway": OUT_DIR / "v28_midprice_source_dilution_runway_latest.json",
    "soft_frontier_midprice_boundary_exit_stack": OUT_DIR / "v28_soft_frontier_midprice_boundary_exit_stack_latest.json",
    "soft_frontier_midprice_boundary_exit_stack_runway": OUT_DIR / "v28_soft_frontier_midprice_boundary_exit_stack_runway_latest.json",
    "boundary_clock_feature_gate_ask_floor": OUT_DIR / "v28_boundary_clock_feature_gate_ask_floor_mechanism_latest.json",
    "feature_gate_ask_floor_tradeoff_autopsy": OUT_DIR / "v28_feature_gate_ask_floor_tradeoff_autopsy_latest.json",
    "feature_gate_side_displacement_guard": OUT_DIR / "v28_feature_gate_side_displacement_guard_latest.json",
    "feature_gate_guarded_coverage_repair_scan": OUT_DIR / "v28_feature_gate_guarded_coverage_repair_scan_latest.json",
    "boundary_clock_feature_gate_continuous_penalty": OUT_DIR / "v28_boundary_clock_feature_gate_continuous_penalty_latest.json",
    "boundary_clock_feature_gate_continuous_penalty_stress": OUT_DIR / "v28_boundary_clock_feature_gate_continuous_penalty_stress_latest.json",
    "boundary_clock_feature_gate_residual_loss": OUT_DIR / "v28_boundary_clock_feature_gate_residual_loss_mechanism_latest.json",
    "boundary_clock_feature_gate_quick_status": OUT_DIR / "v28_boundary_clock_feature_gate_quick_status_latest.json",
    "feature_gate_raw03_vs_raw05_autopsy": OUT_DIR / "v28_feature_gate_raw03_vs_raw05_autopsy_latest.json",
    "feature_gate_raw05_coverage_gap": OUT_DIR / "v28_feature_gate_raw05_coverage_gap_audit_latest.json",
    "feature_gate_joint_gate_gap": OUT_DIR / "v28_feature_gate_joint_gate_gap_audit_latest.json",
    "feature_gate_gap_mechanism_synthesis": OUT_DIR / "v28_feature_gate_gap_mechanism_synthesis_latest.json",
    "feature_gate_current_margin_size_proxy": OUT_DIR / "v28_feature_gate_current_margin_size_proxy_latest.json",
    "feature_gate_cheap_tail_quarantine": OUT_DIR / "v28_feature_gate_cheap_tail_quarantine_latest.json",
    "feature_gate_source_risk_shrink_watch": OUT_DIR / "v28_feature_gate_source_risk_shrink_watch_latest.json",
    "sidecar_live_test_watch": OUT_DIR / "v28_sidecar_live_test_watch_latest.json",
    "continuous_penalty_sidecar_runway": OUT_DIR / "v28_continuous_penalty_sidecar_runway_latest.json",
    "near_gate_runway": OUT_DIR / "v28_near_gate_runway_latest.json",
    "controlled_live_test_gate": OUT_DIR / "v28_controlled_live_test_gate_latest.json",
    "dual_lane_overlap_portfolio": OUT_DIR / "v28_dual_lane_overlap_portfolio_latest.json",
    "dual_lane_own_freeze_watch": OUT_DIR / "v28_dual_lane_own_freeze_watch_latest.json",
    "dual_lane_same_window_delta_autopsy": OUT_DIR / "v28_dual_lane_same_window_delta_autopsy_latest.json",
    "dual_lane_same_window_sequence_mechanism": OUT_DIR / "v28_dual_lane_same_window_sequence_mechanism_latest.json",
    "dual_lane_state_exposure_sequence_repair": OUT_DIR / "v28_dual_lane_state_exposure_sequence_repair_latest.json",
    "dual_lane_side_flip_feasibility": OUT_DIR / "v28_dual_lane_side_flip_feasibility_latest.json",
    "control_risk_candidate_triage": OUT_DIR / "v28_control_risk_candidate_triage_latest.json",
    "exit_combo": OUT_DIR / "v28_frozen_fv_bridge_exit_combo_stack_latest.json",
    "exit_reduce": OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json",
    "exit_reduce_risk": OUT_DIR / "v28_exit_reduce_suppression_risk_ledger_latest.json",
    "exit_reduce_blocker_decision": OUT_DIR / "v28_exit_reduce_blocker_decision_latest.json",
    "exit_reduce_drift_guard_watch": OUT_DIR / "v28_frozen_exit_reduce_drift_guard_watch_latest.json",
    "exit_reduce_signature": OUT_DIR / "v28_exit_reduce_loss_control_signature_latest.json",
    "exit_reduce_actionability": OUT_DIR / "v28_exit_reduce_loss_control_actionability_latest.json",
    "exit_reduce_refinement": OUT_DIR / "v28_frozen_exit_reduce_loss_control_refinement_latest.json",
    "exit_reduce_depth_gate": OUT_DIR / "v28_frozen_exit_reduce_depth_gate_latest.json",
    "exit_reduce_depth_gate_runway": OUT_DIR / "v28_exit_reduce_depth_gate_runway_latest.json",
    "exit_reduce_depth_gate_opportunity": OUT_DIR / "v28_exit_reduce_depth_gate_opportunity_latest.json",
    "exit_reduce_observable_loss_control": OUT_DIR / "v28_frozen_exit_reduce_observable_loss_control_watch_latest.json",
    "exit_reduce_observable_loss_control_opportunity": OUT_DIR / "v28_exit_reduce_observable_loss_control_opportunity_latest.json",
    "exit_reduce_observable_false_hold_autopsy": OUT_DIR / "v28_exit_reduce_observable_false_hold_autopsy_latest.json",
    "exit_policy_loss_churn": OUT_DIR / "v28_exit_policy_loss_churn_effect_latest.json",
    "loss_churn_guarded_frontier": OUT_DIR / "v28_loss_churn_guarded_repair_frontier_latest.json",
    "loss_churn_observable_full_denominator_replay": OUT_DIR / "v28_loss_churn_observable_full_denominator_replay_latest.json",
    "loss_churn_recross_clock_feasibility": OUT_DIR / "v28_loss_churn_recross_clock_feasibility_latest.json",
    "loss_churn_recross_exit_clock_join_audit": OUT_DIR / "v28_loss_churn_recross_exit_clock_join_audit_latest.json",
    "loss_churn_recross_threshold_frontier": OUT_DIR / "v28_loss_churn_recross_threshold_frontier_latest.json",
    "exit_clock_source_stability": OUT_DIR / "v28_exit_clock_source_stability_latest.json",
    "exit_clock_low_edge_hold_guard_tradeoff": OUT_DIR / "v28_exit_clock_low_edge_hold_guard_tradeoff_latest.json",
    "exit_clock_broad_hold_neighbor_autopsy": OUT_DIR / "v28_exit_clock_broad_hold_neighbor_autopsy_latest.json",
    "exit_unresolved_state_separator": OUT_DIR / "v28_exit_unresolved_state_separator_latest.json",
    "exit_shallow_drawdown_watch": OUT_DIR / "v28_frozen_exit_shallow_drawdown_watch_latest.json",
    "exit_shallow_drawdown_harm_audit": OUT_DIR / "v28_exit_shallow_drawdown_harm_audit_latest.json",
    "exit_shallow_duration_watch": OUT_DIR / "v28_frozen_exit_shallow_duration_watch_latest.json",
    "exit_clip_separator": OUT_DIR / "v28_exit_clip_separator_diagnostic_latest.json",
    "exit_clip_separator_watch": OUT_DIR / "v28_frozen_exit_clip_separator_watch_latest.json",
    "exit_clip_separator_replay": OUT_DIR / "v28_exit_clip_separator_replay_latest.json",
    "matched_unchanged_loss_guard_watch": OUT_DIR / "v28_frozen_matched_unchanged_loss_guard_watch_latest.json",
    "exit_true_loser_hold_risk": OUT_DIR / "v28_exit_true_loser_hold_risk_audit_latest.json",
    "exit_false_hold_guardrail_bridge": OUT_DIR / "v28_exit_false_hold_guardrail_bridge_latest.json",
    "exit_false_hold_rule_overlap": OUT_DIR / "v28_exit_false_hold_rule_overlap_audit_latest.json",
    "exit_loss_guard_mechanism": OUT_DIR / "v28_exit_loss_guard_mechanism_audit_latest.json",
    "exit_loss_guard_threshold_margin_stress": OUT_DIR / "v28_exit_loss_guard_threshold_margin_stress_latest.json",
    "exit_loss_guard_path_risk": OUT_DIR / "v28_exit_loss_guard_path_risk_audit_latest.json",
    "exit_book_gap": OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json",
    "exit_book_gap_loss_guard": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_latest.json",
    "exit_book_gap_loss_guard_v2": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v2_latest.json",
    "exit_book_gap_value_only": OUT_DIR / "v28_frozen_exit_book_gap_value_only_latest.json",
    "exit_value_reduce_depth_composite": OUT_DIR / "v28_frozen_exit_value_reduce_depth_composite_latest.json",
    "exit_value_reduce_depth_suppressed_loser": OUT_DIR / "v28_exit_value_reduce_depth_suppressed_loser_audit_latest.json",
    "exit_reduce_current_floor_guard_frontier": OUT_DIR / "v28_exit_reduce_current_floor_guard_frontier_latest.json",
    "exit_value_reduce_depth_opportunity": OUT_DIR / "v28_exit_value_reduce_depth_opportunity_latest.json",
    "exit_book_gap_loss_guard_opportunity": OUT_DIR / "v28_exit_book_gap_loss_guard_opportunity_latest.json",
    "exit_book_gap_value_only_opportunity": OUT_DIR / "v28_exit_book_gap_value_only_opportunity_latest.json",
    "exit_book_gap_loss_guard_v2_opportunity": OUT_DIR / "v28_exit_book_gap_loss_guard_v2_opportunity_latest.json",
    "exit_loss_guard_v1_v2_runway": OUT_DIR / "v28_exit_loss_guard_v1_v2_runway_latest.json",
    "exit_loss_guard_v3_residual_size_shrink": OUT_DIR / "v28_exit_loss_guard_v3_residual_bucket_size_shrink_latest.json",
    "exit_policy_common_clock": OUT_DIR / "v28_exit_policy_common_clock_watch_latest.json",
    "exit_common_clock_runway": OUT_DIR / "v28_exit_common_clock_promotion_runway_latest.json",
    "exit_common_clock_suppression_scarcity": OUT_DIR / "v28_exit_common_clock_suppression_scarcity_latest.json",
    "exit_common_clock_residual_frontier": OUT_DIR / "v28_exit_common_clock_residual_frontier_latest.json",
    "dual_exit_book_gap_else_reduce": OUT_DIR / "v28_frozen_dual_exit_book_gap_else_reduce_latest.json",
    "soft_frontier_midprice_boundary_dual_exit_stack": OUT_DIR / "v28_soft_frontier_midprice_boundary_dual_exit_stack_latest.json",
    "soft_frontier_midprice_boundary_dual_exit_guard": OUT_DIR / "v28_soft_frontier_midprice_boundary_dual_exit_guard_refinement_latest.json",
    "soft_frontier_midprice_boundary_dual_exit_guard_runway": OUT_DIR / "v28_midprice_dual_exit_guard_runway_latest.json",
    "exit_reduce_geometry": OUT_DIR / "v28_exit_reduce_geometry_suppression_latest.json",
    "frozen_exit_reduce_geometry": OUT_DIR / "v28_frozen_exit_reduce_geometry_suppression_latest.json",
    "exit_reduce_geometry_opportunity": OUT_DIR / "v28_exit_reduce_geometry_opportunity_latest.json",
    "exit_reduce_geometry_relaxed_watch": OUT_DIR / "v28_frozen_exit_reduce_geometry_relaxed_watch_latest.json",
    "approved_book": OUT_DIR / "v28_frozen_approved_entry_book_fv_latest.json",
    "conditional_book": OUT_DIR / "v28_frozen_approved_entry_conditional_book_fv_latest.json",
    "approved_book_raw_blend": OUT_DIR / "v28_frozen_approved_entry_book_raw_blend_latest.json",
    "phi": OUT_DIR / "v28_phi_forgetting_fv_candidates_latest.json",
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def first_rank(payload: dict[str, Any], key: str = "forward") -> dict[str, Any]:
    rows = payload.get(key)
    return rows[0] if isinstance(rows, list) and rows else {}


def find_rank(payload: dict[str, Any], overlay: str, key: str = "ranking") -> dict[str, Any]:
    rows = payload.get(key)
    if not isinstance(rows, list):
        rows = payload.get("forward")
    if not isinstance(rows, list):
        rows = payload.get("discovery")
    if not isinstance(rows, list):
        return {}
    return next((row for row in rows if row.get("overlay") == overlay or row.get("policy") == overlay), {})


def early_summary(payload: dict[str, Any], name: str) -> dict[str, Any]:
    summaries = payload.get("summaries")
    if isinstance(summaries, dict):
        return summaries.get(name) or {}
    rows = payload.get("scorecard")
    if isinstance(rows, list):
        return next((row for row in rows if row.get("surface") == name), {})
    return {}


def find_window(payload: dict[str, Any], name: str) -> dict[str, Any]:
    for window in payload.get("windows") or []:
        if isinstance(window, dict) and window.get("window") == name:
            return window
    return {}


def first_variant(window: dict[str, Any]) -> dict[str, Any]:
    variants = window.get("variants")
    return variants[0] if isinstance(variants, list) and variants else {}


def find_lane(payload: dict[str, Any], lane: str) -> dict[str, Any]:
    rows = payload.get("lanes")
    if not isinstance(rows, list):
        return {}
    return next((row for row in rows if isinstance(row, dict) and row.get("lane") == lane), {})


def build_report() -> dict[str, Any]:
    data = {name: load_json(path) for name, path in FILES.items()}

    goal = data["goal_audit"]
    shrink = data["confidence_shrink"]
    hybrid = data["hybrid_shrink"]
    raw_cal = data["raw_entry_calibration"]
    early = data["early_no_boundary"]
    early_stress = data["early_no_boundary_stress"]
    target_failure_clusters = data["target_failure_clusters"]
    target_cluster_penalty_watch = data["target_cluster_penalty_watch"]
    target_cluster_penalty_runway = data["target_cluster_penalty_runway"]
    target_cluster_penalty_source_feasibility = data["target_cluster_penalty_source_feasibility"]
    target_cluster_penalty_source_displacement = data["target_cluster_penalty_source_displacement"]
    target_hybrid_veto = data["target_hybrid_veto"]
    hybrid_boundary_stack = data["hybrid_boundary_stack"]
    hybrid_boundary_stack_source_stress = data["hybrid_boundary_stack_source_stress"]
    hybrid_boundary_stack_stress = data["hybrid_boundary_stack_stress"]
    hybrid_boundary_source_frontier = data["hybrid_boundary_source_frontier"]
    hybrid_boundary_source_dilution = data["hybrid_boundary_source_dilution"]
    boundary_clock_entry = data["boundary_clock_entry"]
    boundary_clock_bridge = data["boundary_clock_fv_bridge"]
    boundary_clock_runway = data["boundary_clock_runway"]
    boundary_clock_source_stress = data["boundary_clock_source_stress"]
    boundary_clock_approved_frontier = data["boundary_clock_approved_frontier"]
    boundary_clock_feature_gate = data["boundary_clock_feature_gate"]
    feature_gate_near_promotion_watch = data["feature_gate_near_promotion_watch"]
    feature_gate_near_promotion_denominator_gap = data["feature_gate_near_promotion_denominator_gap"]
    feature_gate_pending_resolution_audit = data["feature_gate_pending_resolution_audit"]
    feature_gate_outcome_linkage_overlay = data["feature_gate_outcome_linkage_overlay"]
    feature_gate_linked_source_runway = data["feature_gate_linked_source_runway"]
    feature_gate_live_outcome_alignment = data["feature_gate_live_outcome_alignment"]
    feature_gate_live_exit_mismatch_drilldown = data["feature_gate_live_exit_mismatch_drilldown"]
    feature_gate_live_exit_hold_counterfactual = data["feature_gate_live_exit_hold_counterfactual"]
    feature_gate_exit_state_repair_frontier = data["feature_gate_exit_state_repair_frontier"]
    feature_gate_value_exit_watch = data["feature_gate_value_exit_watch"]
    value_exit_feature_gate_contrast = data["value_exit_feature_gate_contrast"]
    value_exit_feature_side_guard = data["value_exit_feature_side_guard"]
    feature_gate_exit_suppression_separator = data["feature_gate_exit_suppression_separator"]
    feature_gate_exit_bid_suppression_watch = data["feature_gate_exit_bid_suppression_watch"]
    feature_gate_exit_bid_path_risk = data["feature_gate_exit_bid_path_risk"]
    feature_gate_exit_bid_delayed_recheck = data["feature_gate_exit_bid_delayed_recheck"]
    soft_frontier_midprice_delayed_recheck_exit = data["soft_frontier_midprice_delayed_recheck_exit"]
    soft_frontier_midprice_delayed_recheck_path_risk = data["soft_frontier_midprice_delayed_recheck_path_risk"]
    soft_frontier_midprice_delayed_recheck_failure_modes = data["soft_frontier_midprice_delayed_recheck_failure_modes"]
    soft_frontier_delayed_recheck_rescue_frontier = data["soft_frontier_delayed_recheck_rescue_frontier"]
    soft_frontier_delayed_recheck_rescue_path_risk = data["soft_frontier_delayed_recheck_rescue_path_risk"]
    soft_frontier_midprice_delayed_recheck_clean_rescue = data["soft_frontier_midprice_delayed_recheck_clean_rescue"]
    soft_frontier_delayed_recheck_clean_rescue_path_risk = data["soft_frontier_delayed_recheck_clean_rescue_path_risk"]
    soft_frontier_delayed_recheck_disaster_guard = data["soft_frontier_delayed_recheck_disaster_guard"]
    top_component_mix_portfolio = data["top_component_mix_portfolio"]
    top_component_loss_cluster = data["top_component_loss_cluster"]
    top_component_false_negative_rescue = data["top_component_false_negative_rescue"]
    top_component_parent_fill_repair = data["top_component_parent_fill_repair"]
    top_component_observable_quarantine = data["top_component_observable_quarantine"]
    top_component_strict_row_autopsy = data["top_component_strict_row_autopsy"]
    feature_gate_near_promotion_exit_attribution = data["feature_gate_near_promotion_exit_attribution"]
    feature_gate_core_expansion_mix = data["feature_gate_core_expansion_mix"]
    feature_gate_coverage_repair = data["feature_gate_coverage_repair"]
    feature_gate_coverage_size_shrink = data["feature_gate_coverage_size_shrink"]
    feature_gate_size_shrink_source_slice = data["feature_gate_size_shrink_source_slice"]
    feature_gate_middle_distance_core_watch = data["feature_gate_middle_distance_core_watch"]
    feature_gate_middle_core_expansion_bound = data["feature_gate_middle_core_expansion_bound"]
    feature_gate_middle_core_exit_attribution = data["feature_gate_middle_core_exit_attribution"]
    feature_gate_middle_core_exit_guard_watch = data["feature_gate_middle_core_exit_guard_watch"]
    feature_gate_size_shrink_strict_drilldown = data["feature_gate_size_shrink_strict_drilldown"]
    feature_gate_coverage_size_shrink_exit_attribution = data["feature_gate_coverage_size_shrink_exit_attribution"]
    feature_gate_coverage_size_shrink_runway = data["feature_gate_coverage_size_shrink_runway"]
    feature_gate_observable_selection_mix = data["feature_gate_observable_selection_mix"]
    feature_gate_size_shrink_exit_overlay = data["feature_gate_size_shrink_exit_overlay"]
    feature_gate_size_shrink_delayed_recheck_exit = data["feature_gate_size_shrink_delayed_recheck_exit"]
    feature_gate_size_shrink_delayed_recheck_rescue = data["feature_gate_size_shrink_delayed_recheck_rescue"]
    feature_gate_source_confirmation_replacement = data["feature_gate_source_confirmation_replacement"]
    feature_gate_late_collapse_recheck_rescue = data["feature_gate_late_collapse_recheck_rescue"]
    feature_gate_dual_clock_recheck_rescue = data["feature_gate_dual_clock_recheck_rescue"]
    feature_gate_confirmed_dual_clock_fill = data["feature_gate_confirmed_dual_clock_fill"]
    feature_gate_confirmed_dual_clock_fill_stress = data["feature_gate_confirmed_dual_clock_fill_stress"]
    feature_gate_source_quality_proxy = data["feature_gate_source_quality_proxy"]
    feature_gate_source_proxy_coverage_repair = data["feature_gate_source_proxy_coverage_repair"]
    feature_gate_source_proxy_strict_autopsy = data["feature_gate_source_proxy_strict_autopsy"]
    feature_gate_source_blocker_mechanism = data["feature_gate_source_blocker_mechanism"]
    high_win_core_broad_fill_mix = data["high_win_core_broad_fill_mix"]
    p50_book_edge_source_failure_drilldown = data["p50_book_edge_source_failure_drilldown"]
    p50_book_edge_source_feasibility_bound = data["p50_book_edge_source_feasibility_bound"]
    p50_book_edge_no_side_shrink_watch = data["p50_book_edge_no_side_shrink_watch"]
    p50_soft_frontier_overlap_mix = data["p50_soft_frontier_overlap_mix"]
    boundary_clock_feature_gate_runway = data["boundary_clock_feature_gate_runway"]
    boundary_clock_feature_gate_failure_modes = data["boundary_clock_feature_gate_failure_modes"]
    boundary_clock_feature_gate_loss_analog = data["boundary_clock_feature_gate_loss_analog"]
    boundary_clock_feature_gate_row_ledger = data["boundary_clock_feature_gate_row_ledger"]
    boundary_clock_feature_gate_coverage_recovery = data["boundary_clock_feature_gate_coverage_recovery"]
    boundary_clock_feature_gate_source_denominator = data["boundary_clock_feature_gate_source_denominator"]
    boundary_clock_feature_gate_coverage_source_frontier = data["boundary_clock_feature_gate_coverage_source_frontier"]
    feature_gate_source_feasibility_bound = data["feature_gate_source_feasibility_bound"]
    feature_gate_promotion_gap = data["feature_gate_promotion_gap"]
    boundary_clock_feature_gate_frontier_runway = data["boundary_clock_feature_gate_frontier_runway"]
    boundary_clock_feature_gate_frontier_mechanism = data["boundary_clock_feature_gate_frontier_mechanism"]
    boundary_clock_feature_gate_outlier_stress = data["boundary_clock_feature_gate_outlier_stress"]
    boundary_clock_feature_gate_clean_broad_frontier = data["boundary_clock_feature_gate_clean_broad_frontier"]
    boundary_clock_feature_gate_soft_frontier = data["boundary_clock_feature_gate_soft_frontier"]
    soft_frontier_post_birth_failure_drilldown = data["soft_frontier_post_birth_failure_drilldown"]
    feature_gate_cheap_tail_shrink_watch = data["feature_gate_cheap_tail_shrink_watch"]
    soft_frontier_midprice_boundary_shrink = data["soft_frontier_midprice_boundary_shrink"]
    midprice_source_dilution = data["midprice_source_dilution"]
    midprice_source_dilution_stability = data["midprice_source_dilution_stability"]
    midprice_source_dilution_mechanism = data["midprice_source_dilution_mechanism"]
    midprice_source_dilution_runway = data["midprice_source_dilution_runway"]
    soft_frontier_midprice_boundary_exit_stack = data["soft_frontier_midprice_boundary_exit_stack"]
    soft_frontier_midprice_boundary_exit_stack_runway = data["soft_frontier_midprice_boundary_exit_stack_runway"]
    boundary_clock_feature_gate_ask_floor = data["boundary_clock_feature_gate_ask_floor"]
    feature_gate_ask_floor_tradeoff_autopsy = data["feature_gate_ask_floor_tradeoff_autopsy"]
    feature_gate_side_displacement_guard = data["feature_gate_side_displacement_guard"]
    feature_gate_guarded_coverage_repair_scan = data["feature_gate_guarded_coverage_repair_scan"]
    boundary_clock_feature_gate_continuous_penalty = data["boundary_clock_feature_gate_continuous_penalty"]
    boundary_clock_feature_gate_continuous_penalty_stress = data["boundary_clock_feature_gate_continuous_penalty_stress"]
    boundary_clock_feature_gate_residual_loss = data["boundary_clock_feature_gate_residual_loss"]
    boundary_clock_feature_gate_quick_status = data["boundary_clock_feature_gate_quick_status"]
    feature_gate_raw03_vs_raw05_autopsy = data["feature_gate_raw03_vs_raw05_autopsy"]
    feature_gate_raw05_coverage_gap = data["feature_gate_raw05_coverage_gap"]
    feature_gate_joint_gate_gap = data["feature_gate_joint_gate_gap"]
    feature_gate_gap_mechanism_synthesis = data["feature_gate_gap_mechanism_synthesis"]
    feature_gate_current_margin_size_proxy = data["feature_gate_current_margin_size_proxy"]
    feature_gate_cheap_tail_quarantine = data["feature_gate_cheap_tail_quarantine"]
    feature_gate_source_risk_shrink_watch = data["feature_gate_source_risk_shrink_watch"]
    sidecar_live_test_watch = data["sidecar_live_test_watch"]
    continuous_penalty_sidecar_runway = data["continuous_penalty_sidecar_runway"]
    near_gate_runway = data["near_gate_runway"]
    controlled_live_test_gate = data["controlled_live_test_gate"]
    dual_lane_overlap_portfolio = data["dual_lane_overlap_portfolio"]
    dual_lane_own_freeze_watch = data["dual_lane_own_freeze_watch"]
    dual_lane_same_window_delta_autopsy = data["dual_lane_same_window_delta_autopsy"]
    dual_lane_same_window_sequence_mechanism = data["dual_lane_same_window_sequence_mechanism"]
    dual_lane_state_exposure_sequence_repair = data["dual_lane_state_exposure_sequence_repair"]
    dual_lane_side_flip_feasibility = data["dual_lane_side_flip_feasibility"]
    control_risk_candidate_triage = data["control_risk_candidate_triage"]
    combo = data["exit_combo"]
    reduce = data["exit_reduce"]
    reduce_risk = data["exit_reduce_risk"]
    reduce_blocker_decision = data["exit_reduce_blocker_decision"]
    reduce_drift_guard_watch = data["exit_reduce_drift_guard_watch"]
    reduce_signature = data["exit_reduce_signature"]
    reduce_actionability = data["exit_reduce_actionability"]
    reduce_refinement = data["exit_reduce_refinement"]
    reduce_depth_gate = data["exit_reduce_depth_gate"]
    reduce_depth_gate_runway = data["exit_reduce_depth_gate_runway"]
    reduce_depth_gate_opportunity = data["exit_reduce_depth_gate_opportunity"]
    reduce_observable_loss_control = data["exit_reduce_observable_loss_control"]
    reduce_observable_loss_control_opportunity = data["exit_reduce_observable_loss_control_opportunity"]
    reduce_observable_false_hold_autopsy = data["exit_reduce_observable_false_hold_autopsy"]
    exit_policy_loss_churn = data["exit_policy_loss_churn"]
    loss_churn_guarded_frontier = data["loss_churn_guarded_frontier"]
    loss_churn_observable_full_denominator_replay = data["loss_churn_observable_full_denominator_replay"]
    loss_churn_recross_clock_feasibility = data["loss_churn_recross_clock_feasibility"]
    loss_churn_recross_exit_clock_join_audit = data["loss_churn_recross_exit_clock_join_audit"]
    loss_churn_recross_threshold_frontier = data["loss_churn_recross_threshold_frontier"]
    exit_clock_source_stability = data["exit_clock_source_stability"]
    exit_clock_low_edge_hold_guard_tradeoff = data["exit_clock_low_edge_hold_guard_tradeoff"]
    exit_clock_broad_hold_neighbor_autopsy = data["exit_clock_broad_hold_neighbor_autopsy"]
    exit_unresolved_state_separator = data["exit_unresolved_state_separator"]
    exit_shallow_drawdown_watch = data["exit_shallow_drawdown_watch"]
    exit_shallow_drawdown_harm_audit = data["exit_shallow_drawdown_harm_audit"]
    exit_shallow_duration_watch = data["exit_shallow_duration_watch"]
    exit_clip_separator = data["exit_clip_separator"]
    exit_clip_separator_watch = data["exit_clip_separator_watch"]
    exit_clip_separator_replay = data["exit_clip_separator_replay"]
    matched_unchanged_loss_guard_watch = data["matched_unchanged_loss_guard_watch"]
    exit_true_loser_hold_risk = data["exit_true_loser_hold_risk"]
    exit_false_hold_guardrail_bridge = data["exit_false_hold_guardrail_bridge"]
    exit_false_hold_rule_overlap = data["exit_false_hold_rule_overlap"]
    exit_loss_guard_mechanism = data["exit_loss_guard_mechanism"]
    exit_loss_guard_threshold_margin_stress = data["exit_loss_guard_threshold_margin_stress"]
    exit_loss_guard_path_risk = data["exit_loss_guard_path_risk"]
    exit_book_gap = data["exit_book_gap"]
    exit_book_gap_loss_guard = data["exit_book_gap_loss_guard"]
    exit_book_gap_loss_guard_v2 = data["exit_book_gap_loss_guard_v2"]
    exit_book_gap_value_only = data["exit_book_gap_value_only"]
    exit_value_reduce_depth_composite = data["exit_value_reduce_depth_composite"]
    exit_value_reduce_depth_suppressed_loser = data["exit_value_reduce_depth_suppressed_loser"]
    exit_reduce_current_floor_guard_frontier = data["exit_reduce_current_floor_guard_frontier"]
    exit_value_reduce_depth_opportunity = data["exit_value_reduce_depth_opportunity"]
    exit_book_gap_loss_guard_opportunity = data["exit_book_gap_loss_guard_opportunity"]
    exit_book_gap_value_only_opportunity = data["exit_book_gap_value_only_opportunity"]
    exit_book_gap_loss_guard_v2_opportunity = data["exit_book_gap_loss_guard_v2_opportunity"]
    exit_loss_guard_v1_v2_runway = data["exit_loss_guard_v1_v2_runway"]
    exit_loss_guard_v3_residual_size_shrink = data["exit_loss_guard_v3_residual_size_shrink"]
    exit_policy_common_clock = data["exit_policy_common_clock"]
    exit_common_clock_runway = data["exit_common_clock_runway"]
    exit_common_clock_suppression_scarcity = data["exit_common_clock_suppression_scarcity"]
    exit_common_clock_residual_frontier = data["exit_common_clock_residual_frontier"]
    dual_exit = data["dual_exit_book_gap_else_reduce"]
    soft_frontier_midprice_boundary_dual_exit_stack = data["soft_frontier_midprice_boundary_dual_exit_stack"]
    soft_frontier_midprice_boundary_dual_exit_guard = data["soft_frontier_midprice_boundary_dual_exit_guard"]
    soft_frontier_midprice_boundary_dual_exit_guard_runway = data["soft_frontier_midprice_boundary_dual_exit_guard_runway"]
    reduce_geometry = data["exit_reduce_geometry"]
    frozen_reduce_geometry = data["frozen_exit_reduce_geometry"]
    reduce_geometry_opportunity = data["exit_reduce_geometry_opportunity"]
    reduce_geometry_relaxed_watch = data["exit_reduce_geometry_relaxed_watch"]
    approved_book = data["approved_book"]
    conditional_book = data["conditional_book"]
    approved_book_raw_blend = data["approved_book_raw_blend"]
    phi = data["phi"]

    shrink_diag = first_rank(shrink, "discovery")
    shrink_forward = first_rank(shrink, "forward")
    hybrid_diag = first_rank(hybrid, "discovery")
    hybrid_forward = first_rank(hybrid, "forward")
    raw_cal_bucket = next((row for row in raw_cal.get("bucket_summary") or [] if row.get("bucket") == "all"), {})
    raw_cal_rows = raw_cal_bucket.get("overlays") if isinstance(raw_cal_bucket.get("overlays"), list) else []
    raw_noise = next((row for row in raw_cal_rows if row.get("overlay") == "noise_shrink_light_probability"), {})
    early_candidate = early_summary(early, "candidate") or early.get("candidate_summary") or {}
    early_target = early_summary(early, "target") or early.get("target_summary") or {}
    early_blockers = early.get("blockers") or []
    early_net_cents = as_float(early_candidate.get("net_cents"))
    early_is_positive = early_net_cents is not None and early_net_cents > 0
    stress_warnings = early_stress.get("warnings") or []
    reduce_summary = reduce.get("summary") or {}
    reduce_risk_suppressed = reduce_risk.get("suppressed_summary") or {}
    reduce_risk_helpful = reduce_risk.get("helpful_suppressed_summary") or {}
    reduce_risk_harmful = reduce_risk.get("harmful_suppressed_summary") or {}
    reduce_risk_groups = reduce_risk.get("suppressed_group_summaries") or {}
    book_gap_summary = exit_book_gap.get("summary") or {}
    book_gap_loss_guard_summary = exit_book_gap_loss_guard.get("summary") or {}
    book_gap_loss_guard_discovery = exit_book_gap_loss_guard.get("discovery_summary_existing_exit_sample") or {}
    book_gap_loss_guard_comparable = exit_book_gap_loss_guard.get("discovery_summary_comparable_book_gap_freeze_sample") or {}
    book_gap_loss_guard_v2_summary = exit_book_gap_loss_guard_v2.get("summary") or {}
    book_gap_loss_guard_v2_discovery = exit_book_gap_loss_guard_v2.get("discovery_summary_existing_exit_sample") or {}
    book_gap_loss_guard_v2_comparable = exit_book_gap_loss_guard_v2.get("discovery_summary_comparable_book_gap_freeze_sample") or {}
    book_gap_value_only_summary = exit_book_gap_value_only.get("summary") or {}
    book_gap_value_only_diag_lane = next(
        (
            lane for lane in exit_book_gap_value_only.get("lanes") or []
            if lane.get("lane") == "diagnostic_from_book_gap_freeze"
        ),
        {},
    )
    book_gap_value_only_diag_best = (book_gap_value_only_diag_lane.get("variants") or [{}])[0]
    book_gap_value_only_diag_summary = book_gap_value_only_diag_best.get("summary") or {}
    exit_value_reduce_depth_summary = exit_value_reduce_depth_composite.get("summary") or {}
    exit_value_reduce_depth_lanes = exit_value_reduce_depth_composite.get("lanes") or []
    exit_value_reduce_depth_diag = next(
        (lane for lane in exit_value_reduce_depth_lanes if lane.get("lane") == "diagnostic_from_exit_freezes"),
        {},
    )
    exit_value_reduce_depth_diag_best = (exit_value_reduce_depth_diag.get("variants") or [{}])[0]
    exit_value_reduce_depth_diag_summary = exit_value_reduce_depth_diag_best.get("summary") or {}
    exit_value_reduce_depth_opportunity_primary = exit_value_reduce_depth_opportunity.get("primary") or {}
    book_gap_loss_guard_opportunity_rows = int(as_float(exit_book_gap_loss_guard_opportunity.get("total_rows")) or 0)
    book_gap_loss_guard_opportunity_soft = int(as_float(exit_book_gap_loss_guard_opportunity.get("soft_exit_rows")) or 0)
    book_gap_loss_guard_opportunity_suppress = int(as_float(exit_book_gap_loss_guard_opportunity.get("would_suppress_rows")) or 0)
    book_gap_value_only_opportunity_rows = int(as_float(exit_book_gap_value_only_opportunity.get("total_rows")) or 0)
    book_gap_value_only_opportunity_value = int(as_float(exit_book_gap_value_only_opportunity.get("value_over_hold_rows")) or 0)
    book_gap_value_only_opportunity_suppress = int(as_float(exit_book_gap_value_only_opportunity.get("would_suppress_rows")) or 0)
    book_gap_loss_guard_v2_opportunity_rows = int(as_float(exit_book_gap_loss_guard_v2_opportunity.get("total_rows")) or 0)
    book_gap_loss_guard_v2_opportunity_soft = int(as_float(exit_book_gap_loss_guard_v2_opportunity.get("soft_exit_rows")) or 0)
    book_gap_loss_guard_v2_opportunity_suppress = int(as_float(exit_book_gap_loss_guard_v2_opportunity.get("would_suppress_rows")) or 0)
    loss_guard_v2_strict_runway = exit_loss_guard_v1_v2_runway.get("v2_strict_runway") or {}
    loss_guard_v1_strict_runway = exit_loss_guard_v1_v2_runway.get("v1_strict_runway") or {}
    loss_guard_v3_strict_runway = exit_loss_guard_v1_v2_runway.get("v3_strict_runway") or {}
    loss_guard_strict_variant_runways = exit_loss_guard_v1_v2_runway.get("strict_variant_runways") or []
    loss_guard_v3_residual_windows = exit_loss_guard_v3_residual_size_shrink.get("windows") or []
    loss_guard_v3_residual_diagnostic = next(
        (row for row in loss_guard_v3_residual_windows if row.get("window") == "all_exit_rows_diagnostic"),
        {},
    )
    loss_guard_v3_residual_strict = next(
        (row for row in loss_guard_v3_residual_windows if row.get("window") == "v3_strict_forward"),
        {},
    )
    loss_guard_v3_residual_diagnostic_bucket = loss_guard_v3_residual_diagnostic.get("residual_v1_only_bucket") or {}
    loss_guard_v3_residual_strict_bucket = loss_guard_v3_residual_strict.get("residual_v1_only_bucket") or {}
    loss_guard_v3_residual_strict_full = next(
        (
            row
            for row in loss_guard_v3_residual_strict.get("policies") or []
            if row.get("policy") == "v3_plus_residual_full_v1_like"
        ),
        {},
    )
    loss_guard_path_risk_lanes = exit_loss_guard_path_risk.get("lanes") or []
    loss_guard_path_risk_v1 = next(
        (row for row in loss_guard_path_risk_lanes if row.get("lane") == "book_gap_loss_guard"),
        {},
    )
    loss_guard_path_risk_v3 = next(
        (row for row in loss_guard_path_risk_lanes if row.get("lane") == "book_gap_loss_guard_v3"),
        {},
    )
    common_clock_windows = exit_policy_common_clock.get("windows") or []
    common_clock_strict_v1 = next((row for row in common_clock_windows if row.get("window") == "new_exit_mix_common_forward_v1"), {})
    common_clock_strict_v1_best = (common_clock_strict_v1.get("summaries") or [{}])[0]
    common_clock_strict_v2 = next((row for row in common_clock_windows if row.get("window") == "new_exit_mix_common_forward_v2"), {})
    common_clock_strict_v2_best = (common_clock_strict_v2.get("summaries") or [{}])[0]
    common_clock_strict_v3 = next((row for row in common_clock_windows if row.get("window") == "new_exit_mix_common_forward_v3"), {})
    common_clock_strict_v3_best = (common_clock_strict_v3.get("summaries") or [{}])[0]
    common_clock_comparable = next((row for row in common_clock_windows if row.get("window") == "book_gap_freeze_comparable"), {})
    common_clock_comparable_best = (common_clock_comparable.get("summaries") or [{}])[0]
    common_clock_runway_best = (exit_common_clock_runway.get("rows") or [{}])[0]
    common_clock_scarcity_best = (exit_common_clock_suppression_scarcity.get("policies") or [{}])[0]
    common_clock_scarcity_control = next(
        (row for row in exit_common_clock_suppression_scarcity.get("policies") or [] if row.get("policy") == "v2_control"),
        {},
    )
    common_clock_residual_windows = exit_common_clock_residual_frontier.get("windows") or []
    common_clock_residual_v2 = next(
        (row for row in common_clock_residual_windows if row.get("window") == "new_exit_mix_common_forward_v2"),
        {},
    )
    common_clock_residual_v3 = next(
        (row for row in common_clock_residual_windows if row.get("window") == "new_exit_mix_common_forward_v3"),
        {},
    )
    common_clock_residual_v2_candidates = common_clock_residual_v2.get("candidates") or []
    common_clock_residual_v3_candidates = common_clock_residual_v3.get("candidates") or []
    common_clock_residual_v2_best = common_clock_residual_v2_candidates[0] if common_clock_residual_v2_candidates else {}
    common_clock_residual_v2_clean = next(
        (
            row for row in common_clock_residual_v2_candidates
            if "residual_harmful_false_holds_present" not in (row.get("blockers") or [])
        ),
        {},
    )
    common_clock_residual_v3_clean = next(
        (
            row for row in common_clock_residual_v3_candidates
            if "residual_harmful_false_holds_present" not in (row.get("blockers") or [])
        ),
        {},
    )
    dual_midprice_variants = soft_frontier_midprice_boundary_dual_exit_stack.get("variants") or []
    dual_midprice_best = dual_midprice_variants[0] if dual_midprice_variants else {}
    dual_midprice_strict = next((row for row in dual_midprice_variants if isinstance(row, dict) and row.get("strict_forward")), {})
    dual_midprice_guard_variants = soft_frontier_midprice_boundary_dual_exit_guard.get("variants") or []
    dual_midprice_guard_best = dual_midprice_guard_variants[0] if dual_midprice_guard_variants else {}
    dual_midprice_guard_runway_variants = soft_frontier_midprice_boundary_dual_exit_guard_runway.get("variants") or []
    dual_midprice_guard_runway_best = dual_midprice_guard_runway_variants[0] if dual_midprice_guard_runway_variants else {}
    dual_exit_summary = dual_exit.get("summary") or {}
    reduce_signature_summary = reduce_signature.get("summary") or {}
    reduce_signature_best = (reduce_signature.get("candidate_separators") or [{}])[0]
    reduce_actionability_best_hindsight = reduce_actionability.get("best_hindsight") or {}
    reduce_actionability_best_observable = reduce_actionability.get("best_observable") or {}
    reduce_actionability_needs_freeze = reduce_actionability.get("observable_needing_new_freeze") or []
    reduce_drift_guard_diag = (reduce_drift_guard_watch.get("diagnostic_since_base_freeze") or [{}])[0]
    reduce_drift_guard_post = (reduce_drift_guard_watch.get("post_drift_guard_birth") or [{}])[0]
    reduce_refinement_lanes = reduce_refinement.get("lanes") or []
    reduce_refinement_diag = next((row for row in reduce_refinement_lanes if row.get("lane") == "diagnostic_from_reduce_freeze"), {})
    reduce_refinement_post = next((row for row in reduce_refinement_lanes if row.get("lane") == "post_refinement_birth"), {})
    reduce_refinement_diag_best = (reduce_refinement_diag.get("variants") or [{}])[0]
    reduce_refinement_post_best = (reduce_refinement_post.get("variants") or [{}])[0]
    reduce_refinement_diag_summary = reduce_refinement_diag_best.get("summary") or {}
    reduce_refinement_post_summary = reduce_refinement_post_best.get("summary") or {}
    reduce_depth_lanes = reduce_depth_gate.get("lanes") or []
    reduce_depth_diag = next((row for row in reduce_depth_lanes if row.get("lane") == "diagnostic_from_reduce_freeze"), {})
    reduce_depth_post = next((row for row in reduce_depth_lanes if row.get("lane") == "post_depth_gate_birth"), {})
    reduce_depth_diag_best = (reduce_depth_diag.get("variants") or [{}])[0]
    reduce_depth_post_best = (reduce_depth_post.get("variants") or [{}])[0]
    reduce_depth_diag_summary = reduce_depth_diag_best.get("summary") or {}
    reduce_depth_post_summary = reduce_depth_post_best.get("summary") or {}
    reduce_depth_runway_post = reduce_depth_gate_runway.get("post_birth_best") or {}
    reduce_depth_opportunity_rules = reduce_depth_gate_opportunity.get("rules") or []
    reduce_depth_opportunity_best = reduce_depth_opportunity_rules[0] if reduce_depth_opportunity_rules else {}
    reduce_observable_lanes = reduce_observable_loss_control.get("lanes") or []
    reduce_observable_diag = next((row for row in reduce_observable_lanes if row.get("lane") == "diagnostic_from_reduce_freeze"), {})
    reduce_observable_post = next((row for row in reduce_observable_lanes if row.get("lane") == "post_observable_birth"), {})
    reduce_observable_diag_best = (reduce_observable_diag.get("variants") or [{}])[0]
    reduce_observable_post_best = (reduce_observable_post.get("variants") or [{}])[0]
    reduce_observable_diag_summary = reduce_observable_diag_best.get("summary") or {}
    reduce_observable_post_summary = reduce_observable_post_best.get("summary") or {}
    reduce_observable_opportunity_rules = reduce_observable_loss_control_opportunity.get("rules") or []
    reduce_observable_opportunity_best = reduce_observable_opportunity_rules[0] if reduce_observable_opportunity_rules else {}
    reduce_observable_false_hold_windows = reduce_observable_false_hold_autopsy.get("windows") or []
    reduce_observable_false_hold_diag = next(
        (row for row in reduce_observable_false_hold_windows if row.get("window") == "diagnostic_from_reduce_freeze"),
        {},
    )
    reduce_observable_false_hold_post = next(
        (row for row in reduce_observable_false_hold_windows if row.get("window") == "post_observable_birth"),
        {},
    )
    reduce_observable_false_hold_diag_summary = reduce_observable_false_hold_diag.get("candidate_summary") or {}
    reduce_observable_false_hold_post_summary = reduce_observable_false_hold_post.get("candidate_summary") or {}
    reduce_observable_false_hold_best_post_guard = (
        reduce_observable_false_hold_post.get("zero_harm_guards")
        or reduce_observable_false_hold_post.get("best_guards")
        or [{}]
    )[0]
    exit_policy_loss_churn_rows = exit_policy_loss_churn.get("rows") or []
    exit_policy_loss_churn_best = exit_policy_loss_churn_rows[0] if exit_policy_loss_churn_rows else {}
    loss_churn_clean_frontier = loss_churn_guarded_frontier.get("clean_frontier") or []
    loss_churn_best_clean = loss_churn_clean_frontier[0] if loss_churn_clean_frontier else {}
    loss_churn_observable_frontier = loss_churn_guarded_frontier.get("observable_clean_frontier") or []
    loss_churn_best_observable = loss_churn_observable_frontier[0] if loss_churn_observable_frontier else {}
    loss_churn_full_denom_best = loss_churn_observable_full_denominator_replay.get("best_clean_replay") or {}
    exit_unresolved_separator_summary = exit_unresolved_state_separator.get("summary") or {}
    exit_unresolved_separator_best_clean = exit_unresolved_state_separator.get("best_clean_diagnostic_rule") or {}
    exit_unresolved_separator_best_nice = exit_unresolved_state_separator.get("best_nice_clean_diagnostic_rule") or {}
    exit_shallow_drawdown_best_diag = exit_shallow_drawdown_watch.get("best_diagnostic") or {}
    exit_shallow_drawdown_best_strict = exit_shallow_drawdown_watch.get("best_strict_forward") or {}
    exit_shallow_harm_summary = exit_shallow_drawdown_harm_audit.get("summary") or {}
    exit_shallow_harm_best_clean = exit_shallow_drawdown_harm_audit.get("best_clean_child_rule") or {}
    exit_shallow_duration_best_diag = exit_shallow_duration_watch.get("best_diagnostic") or {}
    exit_shallow_duration_best_strict = exit_shallow_duration_watch.get("best_strict_forward") or {}
    exit_clip_separator_summary = exit_clip_separator.get("summary") or {}
    exit_clip_separator_best = (exit_clip_separator.get("top_rules") or [{}])[0]
    exit_clip_separator_watch_state = exit_clip_separator_watch.get("state") or {}
    exit_clip_separator_watch_summary = exit_clip_separator_watch.get("candidate_summary") or {}
    matched_guard_state = matched_unchanged_loss_guard_watch.get("state") or {}
    matched_guard_diag = matched_unchanged_loss_guard_watch.get("diagnostic_summary") or {}
    matched_guard_post = matched_unchanged_loss_guard_watch.get("post_freeze_summary") or {}
    true_loser_hold_summary = exit_true_loser_hold_risk.get("summary") or {}
    true_loser_hold_true = true_loser_hold_summary.get("true_loser") or {}
    true_loser_hold_clip = true_loser_hold_summary.get("clipped_winner") or {}
    true_loser_avoid_tags = exit_true_loser_hold_risk.get("avoid_broad_hold_tags") or []
    false_hold_bridge_summary = exit_false_hold_guardrail_bridge.get("summary") or {}
    exit_clip_separator_replay_summaries = exit_clip_separator_replay.get("summaries") or []
    exit_clip_separator_replay_diag = next(
        (row for row in exit_clip_separator_replay_summaries if row.get("label") == "diagnostic_from_exit_reduce_freeze"),
        {},
    )
    exit_clip_separator_replay_post = next(
        (row for row in exit_clip_separator_replay_summaries if row.get("label") == "post_clip_watch_freeze"),
        {},
    )
    reduce_geometry_best = (reduce_geometry.get("policies") or [{}])[0]
    frozen_reduce_geometry_summary = frozen_reduce_geometry.get("summary") or {}
    frozen_reduce_geometry_policies = frozen_reduce_geometry.get("counterfactual_policies") or []
    frozen_reduce_geometry_base = next(
        (row for row in frozen_reduce_geometry_policies if row.get("policy") == "base_suppress_reduce_p_hold_ge_075"),
        {},
    )
    frozen_reduce_geometry_side = next(
        (row for row in frozen_reduce_geometry_policies if row.get("policy") == "side_geometry_suppress_reduce_p_hold_ge_075"),
        frozen_reduce_geometry_summary,
    )
    reduce_geometry_opportunity_summary = reduce_geometry_opportunity.get("summary") or {}
    reduce_geometry_relaxed_summary = reduce_geometry_relaxed_watch.get("summary") or {}
    reduce_geometry_relaxed_diag = (reduce_geometry_relaxed_watch.get("diagnostic") or {}).get("best") or {}
    target_veto_diag = find_window(target_hybrid_veto, "diagnostic_existing_target_window")
    target_veto_post = find_window(target_hybrid_veto, "post_repair_freeze_window")
    target_veto_diag_best = first_variant(target_veto_diag)
    target_veto_post_best = first_variant(target_veto_post)
    target_veto_diag_summary = target_veto_diag_best.get("candidate_summary") or {}
    target_veto_post_summary = target_veto_post_best.get("candidate_summary") or {}
    target_veto_diag_cluster = target_veto_diag.get("hybrid_veto_summary") or {}
    target_veto_post_cluster = target_veto_post.get("hybrid_veto_summary") or {}
    target_failure_cluster_rows = target_failure_clusters.get("clusters") or []
    target_failure_top = target_failure_cluster_rows[0] if target_failure_cluster_rows else {}
    target_cluster_penalty_lanes = target_cluster_penalty_watch.get("lanes") or []
    target_cluster_penalty_diag = next((row for row in target_cluster_penalty_lanes if row.get("lane") == "diagnostic_target_window"), {})
    target_cluster_penalty_post = next((row for row in target_cluster_penalty_lanes if row.get("lane") == "post_cluster_penalty_birth"), {})
    target_cluster_penalty_diag_best = (target_cluster_penalty_diag.get("variants") or [{}])[0]
    target_cluster_penalty_post_best = (target_cluster_penalty_post.get("variants") or [{}])[0]
    target_cluster_penalty_diag_summary = target_cluster_penalty_diag_best.get("candidate_summary") or {}
    target_cluster_penalty_post_summary = target_cluster_penalty_post_best.get("candidate_summary") or {}
    target_cluster_penalty_post_runway = target_cluster_penalty_runway.get("post_birth_runway") or {}
    target_cluster_penalty_post_source = target_cluster_penalty_post_runway.get("source_runway") or {}
    target_cluster_penalty_diag_runway = target_cluster_penalty_runway.get("diagnostic_runway") or {}
    target_cluster_penalty_diag_source = target_cluster_penalty_diag_runway.get("source_runway") or {}
    source_feasibility_lanes = target_cluster_penalty_source_feasibility.get("lanes") or []
    source_feasibility_post = next((row for row in source_feasibility_lanes if row.get("lane") == "post_cluster_penalty_birth"), {})
    source_feasibility_diag = next((row for row in source_feasibility_lanes if row.get("lane") == "diagnostic_target_window"), {})
    source_feasibility_post_best = source_feasibility_post.get("best") or {}
    source_feasibility_diag_best = source_feasibility_diag.get("best") or {}
    displacement_lanes = target_cluster_penalty_source_displacement.get("lanes") or []
    displacement_post = next((row for row in displacement_lanes if row.get("lane") == "post_cluster_penalty_birth"), {})
    displacement_post_best = displacement_post.get("best") or {}
    displacement_post_rejected = displacement_post_best.get("selected_rejected_summary") or {}
    displacement_post_omitted = displacement_post_best.get("omitted_approved_summary") or {}
    displacement_post_preferred = displacement_post_best.get("approved_preferred_summary") or {}
    stack_diag = find_window(hybrid_boundary_stack, "diagnostic_existing_target_window")
    stack_post = find_window(hybrid_boundary_stack, "post_stack_freeze_window")
    stack_diag_best = first_variant(stack_diag)
    stack_post_best = first_variant(stack_post)
    stack_diag_summary = stack_diag_best.get("candidate_summary") or {}
    stack_post_summary = stack_post_best.get("candidate_summary") or {}
    stack_diag_integrity = stack_diag_best.get("integrity_preview") or {}
    stack_post_integrity = stack_post_best.get("integrity_preview") or {}
    stack_stress_diag = hybrid_boundary_stack_stress.get("diagnostic") or {}
    stack_stress_best = stack_stress_diag.get("best_broad_positive") or {}
    stack_stress_watch = stack_stress_diag.get("best_watch_source_broad_positive") or {}
    stack_stress_lowest_recon = stack_stress_diag.get("lowest_reconstructed_broad_positive") or {}
    stack_source_stress_lanes = hybrid_boundary_stack_source_stress.get("lanes") or []
    stack_source_stress_diag = next(
        (row for row in stack_source_stress_lanes if row.get("window") == "diagnostic_existing_target_window"),
        {},
    )
    stack_source_stress_post = next(
        (row for row in stack_source_stress_lanes if row.get("window") == "post_stack_freeze_window"),
        {},
    )
    stack_frontier_diag = find_window(hybrid_boundary_source_frontier, "diagnostic_existing_target_window")
    stack_frontier_post = find_window(hybrid_boundary_source_frontier, "post_stack_freeze_window")
    stack_frontier_diag_best = first_variant(stack_frontier_diag)
    stack_frontier_diag_summary = stack_frontier_diag_best.get("candidate_summary") or {}
    stack_frontier_diag_integrity = stack_frontier_diag_best.get("integrity_preview") or {}
    stack_frontier_post_best = first_variant(stack_frontier_post)
    stack_frontier_post_summary = stack_frontier_post_best.get("candidate_summary") or {}
    stack_frontier_post_integrity = stack_frontier_post_best.get("integrity_preview") or {}
    stack_dilution_diag = (hybrid_boundary_source_dilution.get("diagnostic_top") or [{}])[0]
    stack_dilution_post = (hybrid_boundary_source_dilution.get("post_freeze_top") or [{}])[0]
    boundary_clock_candidate = boundary_clock_entry.get("candidate_summary") or {}
    boundary_clock_bridge_candidate = boundary_clock_bridge.get("candidate_summary") or {}
    boundary_clock_stress_lanes = boundary_clock_source_stress.get("lanes") or []
    boundary_clock_entry_stress = next(
        (row for row in boundary_clock_stress_lanes if row.get("lane") == "boundary_clock_repair_entry"),
        {},
    )
    boundary_clock_bridge_stress = next(
        (row for row in boundary_clock_stress_lanes if row.get("lane") == "boundary_clock_fv_entry_bridge"),
        {},
    )
    boundary_clock_frontier_lanes = boundary_clock_approved_frontier.get("lanes") or []
    boundary_clock_entry_frontier = next(
        (row for row in boundary_clock_frontier_lanes if row.get("lane") == "boundary_clock_repair_entry"),
        {},
    )
    boundary_clock_bridge_frontier = next(
        (row for row in boundary_clock_frontier_lanes if row.get("lane") == "boundary_clock_fv_entry_bridge"),
        {},
    )
    boundary_clock_entry_frontier_best = (boundary_clock_entry_frontier.get("variants") or [{}])[0]
    boundary_clock_bridge_frontier_best = (boundary_clock_bridge_frontier.get("variants") or [{}])[0]
    boundary_clock_entry_frontier_summary = boundary_clock_entry_frontier_best.get("candidate_summary") or {}
    boundary_clock_bridge_frontier_summary = boundary_clock_bridge_frontier_best.get("candidate_summary") or {}
    feature_gate_lanes = boundary_clock_feature_gate.get("lanes") or []
    feature_gate_diag_entry = next((row for row in feature_gate_lanes if row.get("lane") == "diagnostic_entry"), {})
    feature_gate_diag_bridge = next((row for row in feature_gate_lanes if row.get("lane") == "diagnostic_bridge"), {})
    feature_gate_post_entry = next((row for row in feature_gate_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    feature_gate_post_bridge = next((row for row in feature_gate_lanes if row.get("lane") == "post_feature_freeze_bridge"), {})
    feature_gate_diag_entry_best = (feature_gate_diag_entry.get("variants") or [{}])[0]
    feature_gate_diag_bridge_best = (feature_gate_diag_bridge.get("variants") or [{}])[0]
    feature_gate_post_entry_best = (feature_gate_post_entry.get("variants") or [{}])[0]
    feature_gate_post_bridge_best = (feature_gate_post_bridge.get("variants") or [{}])[0]
    feature_gate_diag_entry_summary = feature_gate_diag_entry_best.get("candidate_summary") or {}
    feature_gate_diag_bridge_summary = feature_gate_diag_bridge_best.get("candidate_summary") or {}
    feature_gate_post_entry_summary = feature_gate_post_entry_best.get("candidate_summary") or {}
    feature_gate_post_bridge_summary = feature_gate_post_bridge_best.get("candidate_summary") or {}
    feature_gate_near_rows = feature_gate_near_promotion_watch.get("rows") or []
    feature_gate_near_best = feature_gate_near_rows[0] if feature_gate_near_rows else {}
    feature_gate_near_gap_selected = feature_gate_near_promotion_denominator_gap.get("selected_summary") or {}
    feature_gate_near_gap_pending = feature_gate_near_promotion_denominator_gap.get("pending_selected_summary") or {}
    feature_gate_near_gap_omitted = feature_gate_near_promotion_denominator_gap.get("omitted_summary") or {}
    feature_gate_pending_resolution = feature_gate_pending_resolution_audit or {}
    feature_gate_linkage_rows = feature_gate_outcome_linkage_overlay.get("rows") or []
    feature_gate_linkage_best = feature_gate_linkage_rows[0] if feature_gate_linkage_rows else {}
    feature_gate_linkage_best_summary = feature_gate_linkage_best.get("linked_summary") or {}
    feature_gate_source_runway_rows = feature_gate_linked_source_runway.get("rows") or []
    feature_gate_source_runway_best = feature_gate_source_runway_rows[0] if feature_gate_source_runway_rows else {}
    feature_gate_source_runway_approved = feature_gate_source_runway_best.get("approved_summary") or {}
    feature_gate_source_runway_rejected = feature_gate_source_runway_best.get("rejected_or_reconstructed_summary") or {}
    feature_gate_live_alignment_variants = feature_gate_live_outcome_alignment.get("variants") or []
    feature_gate_live_alignment_raw03_entry = next(
        (
            row for row in feature_gate_live_alignment_variants
            if row.get("candidate") == "post_feature_freeze_entry_raw03_recross70_abs075"
        ),
        {},
    )
    feature_gate_live_alignment_raw03_summary = feature_gate_live_alignment_raw03_entry.get("alignment_summary") or {}
    feature_gate_exit_drilldown_markets = feature_gate_live_exit_mismatch_drilldown.get("markets") or []
    feature_gate_exit_drilldown_class_counts: dict[str, int] = {}
    feature_gate_exit_drilldown_reason_counts: dict[str, int] = {}
    for row in feature_gate_exit_drilldown_markets:
        for cls in row.get("classifications") or []:
            feature_gate_exit_drilldown_class_counts[cls] = feature_gate_exit_drilldown_class_counts.get(cls, 0) + 1
        for reason, count in (row.get("exit_reason_counts") or {}).items():
            feature_gate_exit_drilldown_reason_counts[reason] = (
                feature_gate_exit_drilldown_reason_counts.get(reason, 0) + int(count or 0)
            )
    feature_gate_exit_drilldown_theory_net = sum(
        float(row.get("theory_net_cents") or 0) for row in feature_gate_exit_drilldown_markets
    )
    feature_gate_exit_drilldown_live_selected_net = sum(
        float(row.get("live_selected_side_net_cents") or 0) for row in feature_gate_exit_drilldown_markets
    )
    feature_gate_hold_counterfactual_summary = feature_gate_live_exit_hold_counterfactual.get("summary") or {}
    feature_gate_exit_state_frontier_variants = feature_gate_exit_state_repair_frontier.get("variants") or []
    feature_gate_exit_state_frontier_best = feature_gate_exit_state_frontier_variants[0] if feature_gate_exit_state_frontier_variants else {}
    feature_gate_exit_state_frontier_value = next(
        (
            row for row in feature_gate_exit_state_frontier_variants
            if row.get("variant") == "suppress_value_over_hold"
        ),
        {},
    )
    feature_gate_exit_state_frontier_value_phold80 = next(
        (
            row for row in feature_gate_exit_state_frontier_variants
            if row.get("variant") == "suppress_value_or_reduce_p_hold80"
        ),
        {},
    )
    feature_gate_value_exit_lanes = feature_gate_value_exit_watch.get("lanes") or []
    feature_gate_value_exit_post = next(
        (row for row in feature_gate_value_exit_lanes if row.get("label") == "post_value_exit_birth"),
        {},
    )
    feature_gate_value_exit_post_best = (feature_gate_value_exit_post.get("variants") or [{}])[0]
    value_exit_contrast_post = next(
        (row for row in (value_exit_feature_gate_contrast.get("lanes") or []) if row.get("lane") == "post_value_only_birth"),
        {},
    )
    value_exit_contrast_post_summary = value_exit_contrast_post.get("summary") or {}
    value_exit_guard_lanes = value_exit_feature_side_guard.get("lanes") or []
    value_exit_guard_post = next(
        (row for row in value_exit_guard_lanes if row.get("label") == "post_feature_side_guard_birth"),
        {},
    )
    value_exit_guard_post_summary = value_exit_guard_post.get("summary") or {}
    feature_gate_exit_separator_best = (feature_gate_exit_suppression_separator.get("observable_candidate_separators") or [{}])[0]
    feature_gate_exit_separator_oracle_best = (feature_gate_exit_suppression_separator.get("diagnostic_oracle_separators") or [{}])[0]
    feature_gate_exit_bid_watch_lanes = feature_gate_exit_bid_suppression_watch.get("lanes") or []
    feature_gate_exit_bid_watch_diag = next(
        (row for row in feature_gate_exit_bid_watch_lanes if row.get("lane") == "diagnostic_feature_gate_exit_bid"),
        {},
    ).get("summary") or {}
    feature_gate_exit_bid_watch_post = next(
        (row for row in feature_gate_exit_bid_watch_lanes if row.get("lane") == "post_exit_bid_birth"),
        {},
    ).get("summary") or {}
    feature_gate_exit_bid_path_lanes = feature_gate_exit_bid_path_risk.get("lanes") or []
    feature_gate_exit_bid_path_diag = next(
        (row for row in feature_gate_exit_bid_path_lanes if row.get("lane") == "diagnostic_feature_gate_exit_bid"),
        {},
    ).get("summary") or {}
    feature_gate_exit_bid_path_post = next(
        (row for row in feature_gate_exit_bid_path_lanes if row.get("lane") == "post_exit_bid_birth"),
        {},
    ).get("summary") or {}
    feature_gate_exit_bid_delayed_lanes = feature_gate_exit_bid_delayed_recheck.get("lanes") or []
    feature_gate_exit_bid_delayed_diag = next(
        (row for row in feature_gate_exit_bid_delayed_lanes if row.get("lane") == "diagnostic_prefreeze_context"),
        {},
    ).get("summary") or {}
    feature_gate_exit_bid_delayed_post = next(
        (row for row in feature_gate_exit_bid_delayed_lanes if row.get("lane") == "post_delayed_recheck_birth"),
        {},
    ).get("summary") or {}
    soft_midprice_delayed_lanes = soft_frontier_midprice_delayed_recheck_exit.get("lanes") or []
    soft_midprice_delayed_diag = next(
        (row for row in soft_midprice_delayed_lanes if row.get("lane") == "diagnostic_prefreeze_context"),
        {},
    ).get("summary") or {}
    soft_midprice_delayed_post = next(
        (row for row in soft_midprice_delayed_lanes if row.get("lane") == "post_delayed_recheck_birth"),
        {},
    ).get("summary") or {}
    soft_midprice_delayed_path_lanes = soft_frontier_midprice_delayed_recheck_path_risk.get("lanes") or []
    soft_midprice_delayed_path_diag = next(
        (row for row in soft_midprice_delayed_path_lanes if row.get("lane") == "diagnostic_prefreeze_context"),
        {},
    ).get("summary") or {}
    soft_midprice_delayed_failure_summary = soft_frontier_midprice_delayed_recheck_failure_modes.get("summary") or {}
    soft_midprice_rescue_variants = soft_frontier_delayed_recheck_rescue_frontier.get("variants") or []
    soft_midprice_rescue_best = soft_midprice_rescue_variants[0] if soft_midprice_rescue_variants else {}
    soft_midprice_rescue_path_summary = soft_frontier_delayed_recheck_rescue_path_risk.get("summary") or {}
    soft_midprice_clean_rescue_lanes = soft_frontier_midprice_delayed_recheck_clean_rescue.get("lanes") or []
    soft_midprice_clean_rescue_diag = next(
        (row for row in soft_midprice_clean_rescue_lanes if row.get("lane") == "diagnostic_prefreeze_context"),
        {},
    ).get("summary") or {}
    soft_midprice_clean_rescue_post = next(
        (row for row in soft_midprice_clean_rescue_lanes if row.get("lane") == "post_clean_rescue_birth"),
        {},
    ).get("summary") or {}
    soft_midprice_clean_rescue_path_lanes = soft_frontier_delayed_recheck_clean_rescue_path_risk.get("lanes") or []
    soft_midprice_clean_rescue_path_diag = next(
        (row for row in soft_midprice_clean_rescue_path_lanes if row.get("lane") == "diagnostic_prefreeze_context"),
        {},
    ).get("summary") or {}
    soft_midprice_disaster_guard_rows = soft_frontier_delayed_recheck_disaster_guard.get("guards") or []
    soft_midprice_disaster_guard_best = soft_midprice_disaster_guard_rows[0] if soft_midprice_disaster_guard_rows else {}
    top_component_mix_variants = top_component_mix_portfolio.get("variants") or []
    top_component_mix_best = top_component_mix_variants[0] if top_component_mix_variants else {}
    top_component_loss_by_mode = top_component_loss_cluster.get("by_mode") or {}
    top_component_loss_by_source = top_component_loss_cluster.get("by_source") or {}
    top_component_false_negative_variants = top_component_false_negative_rescue.get("variants") or []
    top_component_false_negative_best = top_component_false_negative_variants[0] if top_component_false_negative_variants else {}
    top_component_parent_fill_variants = top_component_parent_fill_repair.get("variants") or []
    top_component_parent_fill_best = top_component_parent_fill_variants[0] if top_component_parent_fill_variants else {}
    top_component_quarantine_diag = top_component_observable_quarantine.get("diagnostic") or []
    top_component_quarantine_autopsy = top_component_observable_quarantine.get("autopsy_context") or []
    top_component_quarantine_strict = top_component_observable_quarantine.get("strict") or []
    top_component_quarantine_diag_best = top_component_quarantine_diag[0] if top_component_quarantine_diag else {}
    top_component_quarantine_autopsy_best = top_component_quarantine_autopsy[0] if top_component_quarantine_autopsy else {}
    top_component_quarantine_strict_best = top_component_quarantine_strict[0] if top_component_quarantine_strict else {}
    feature_gate_near_exit_failure_classes = feature_gate_near_promotion_exit_attribution.get("failure_class_counts") or {}
    feature_gate_near_exit_loss_sources = feature_gate_near_promotion_exit_attribution.get("loss_source_counts") or {}
    feature_gate_core_mix_rows = feature_gate_core_expansion_mix.get("rows") or []
    feature_gate_core_mix_best = feature_gate_core_mix_rows[0] if feature_gate_core_mix_rows else {}
    feature_gate_coverage_repair_lanes = feature_gate_coverage_repair.get("lanes") or []
    feature_gate_coverage_repair_entry = next(
        (row for row in feature_gate_coverage_repair_lanes if row.get("lane") == "post_feature_freeze_entry"),
        {},
    )
    feature_gate_coverage_repair_bridge = next(
        (row for row in feature_gate_coverage_repair_lanes if row.get("lane") == "post_feature_freeze_bridge"),
        {},
    )
    feature_gate_coverage_repair_entry_near = (feature_gate_coverage_repair_entry.get("near_misses") or [{}])[0]
    feature_gate_coverage_repair_bridge_near = (feature_gate_coverage_repair_bridge.get("near_misses") or [{}])[0]
    feature_gate_coverage_repair_entry_near_summary = feature_gate_coverage_repair_entry_near.get("summary") or {}
    feature_gate_coverage_repair_bridge_near_summary = feature_gate_coverage_repair_bridge_near.get("summary") or {}
    feature_gate_quick_entry_lane = find_lane(boundary_clock_feature_gate_quick_status, "post_feature_freeze_entry")
    feature_gate_quick_bridge_lane = find_lane(boundary_clock_feature_gate_quick_status, "post_feature_freeze_bridge")
    feature_gate_quick_entry_best = first_variant(feature_gate_quick_entry_lane)
    feature_gate_quick_bridge_best = first_variant(feature_gate_quick_bridge_lane)
    raw03_autopsy_entry = find_lane(feature_gate_raw03_vs_raw05_autopsy, "post_feature_freeze_entry")
    raw03_autopsy_bridge = find_lane(feature_gate_raw03_vs_raw05_autopsy, "post_feature_freeze_bridge")
    raw03_autopsy_entry_raw05 = raw03_autopsy_entry.get("raw05") or {}
    raw03_autopsy_entry_raw03 = raw03_autopsy_entry.get("raw03") or {}
    raw03_autopsy_entry_marginal = raw03_autopsy_entry.get("marginal_raw03_minus_raw05") or {}
    raw03_autopsy_bridge_raw05 = raw03_autopsy_bridge.get("raw05") or {}
    raw03_autopsy_bridge_raw03 = raw03_autopsy_bridge.get("raw03") or {}
    raw03_autopsy_bridge_marginal = raw03_autopsy_bridge.get("marginal_raw03_minus_raw05") or {}
    raw05_gap_entry = find_lane(feature_gate_raw05_coverage_gap, "post_feature_freeze_entry")
    raw05_gap_bridge = find_lane(feature_gate_raw05_coverage_gap, "post_feature_freeze_bridge")
    raw05_gap_entry_any_oracle = raw05_gap_entry.get("best_any_source_oracle_add_missing") or {}
    raw05_gap_bridge_any_oracle = raw05_gap_bridge.get("best_any_source_oracle_add_missing") or {}
    raw05_gap_entry_approved_oracle = raw05_gap_entry.get("approved_only_oracle_add_missing") or {}
    raw05_gap_bridge_approved_oracle = raw05_gap_bridge.get("approved_only_oracle_add_missing") or {}
    feature_gate_joint_best_by_lane = feature_gate_joint_gate_gap.get("best_by_lane") or {}
    feature_gate_joint_raw05_entry = feature_gate_joint_best_by_lane.get("post_feature_freeze_entry") or {}
    feature_gate_joint_raw05_bridge = feature_gate_joint_best_by_lane.get("post_feature_freeze_bridge") or {}
    feature_gate_joint_raw03_bridge = feature_gate_gap_mechanism_synthesis.get("raw03_bridge") or {}
    feature_gate_gap_mechanism_attr = feature_gate_gap_mechanism_synthesis.get("near_promotion_exit_attribution") or {}
    feature_gate_gap_exit_state_best = feature_gate_gap_mechanism_synthesis.get("exit_state_frontier_best") or {}
    feature_gate_margin_proxy_best = feature_gate_current_margin_size_proxy.get("best_exposure_clean") or {}
    feature_gate_margin_proxy_rows = feature_gate_current_margin_size_proxy.get("rows") or []
    feature_gate_margin_proxy_raw05 = next(
        (
            row for row in feature_gate_margin_proxy_rows
            if row.get("policy") == "raw05_anchor_plus_raw03_marginal_weight_0"
        ),
        {},
    )
    feature_gate_coverage_size_lanes = feature_gate_coverage_size_shrink.get("lanes") or []
    feature_gate_coverage_size_entry = next(
        (row for row in feature_gate_coverage_size_lanes if row.get("lane") == "post_feature_freeze_entry"),
        {},
    )
    feature_gate_coverage_size_bridge = next(
        (row for row in feature_gate_coverage_size_lanes if row.get("lane") == "post_feature_freeze_bridge"),
        {},
    )
    feature_gate_coverage_size_entry_best = (feature_gate_coverage_size_entry.get("rows") or [{}])[0]
    feature_gate_coverage_size_bridge_best = (feature_gate_coverage_size_bridge.get("rows") or [{}])[0]
    feature_gate_coverage_size_attr_lanes = feature_gate_coverage_size_shrink_exit_attribution.get("lanes") or []
    feature_gate_coverage_size_attr_entry = next(
        (row for row in feature_gate_coverage_size_attr_lanes if row.get("lane") == "post_feature_freeze_entry"),
        {},
    )
    feature_gate_coverage_size_attr_bridge = next(
        (row for row in feature_gate_coverage_size_attr_lanes if row.get("lane") == "post_feature_freeze_bridge"),
        {},
    )
    feature_gate_coverage_size_runway_lanes = feature_gate_coverage_size_shrink_runway.get("lanes") or []
    feature_gate_coverage_size_runway_entry = next(
        (row for row in feature_gate_coverage_size_runway_lanes if row.get("lane") == "post_feature_freeze_entry"),
        {},
    )
    feature_gate_coverage_size_runway_bridge = next(
        (row for row in feature_gate_coverage_size_runway_lanes if row.get("lane") == "post_feature_freeze_bridge"),
        {},
    )
    feature_gate_size_source_slice_lanes = feature_gate_size_shrink_source_slice.get("lanes") or []
    feature_gate_size_source_slice_entry = next(
        (row for row in feature_gate_size_source_slice_lanes if row.get("lane") == "post_feature_freeze_entry"),
        {},
    )
    feature_gate_size_source_slice_bridge = next(
        (row for row in feature_gate_size_source_slice_lanes if row.get("lane") == "post_feature_freeze_bridge"),
        {},
    )
    feature_gate_middle_core_lanes = feature_gate_middle_distance_core_watch.get("lanes") or []
    feature_gate_middle_core_diag_entry = next(
        (row for row in feature_gate_middle_core_lanes if row.get("lane") == "diagnostic_feature_window_entry"),
        {},
    )
    feature_gate_middle_core_post_entry = next(
        (row for row in feature_gate_middle_core_lanes if row.get("lane") == "post_middle_core_freeze_entry"),
        {},
    )
    feature_gate_middle_core_diag_best = (feature_gate_middle_core_diag_entry.get("rules") or [{}])[0]
    feature_gate_middle_core_post_best = (feature_gate_middle_core_post_entry.get("rules") or [{}])[0]
    feature_gate_middle_core_bound_lanes = feature_gate_middle_core_expansion_bound.get("lanes") or []
    feature_gate_middle_core_bound_entry = next(
        (row for row in feature_gate_middle_core_bound_lanes if row.get("lane") == "diagnostic_feature_window_entry"),
        {},
    )
    feature_gate_middle_core_bound_bridge = next(
        (row for row in feature_gate_middle_core_bound_lanes if row.get("lane") == "diagnostic_feature_window_bridge"),
        {},
    )
    feature_gate_middle_core_attr_lanes = feature_gate_middle_core_exit_attribution.get("lanes") or []
    feature_gate_middle_core_attr_entry = next(
        (row for row in feature_gate_middle_core_attr_lanes if row.get("lane") == "diagnostic_feature_window_entry"),
        {},
    )
    feature_gate_middle_exit_guard_lanes = feature_gate_middle_core_exit_guard_watch.get("lanes") or []
    feature_gate_middle_exit_guard_diag_entry = next(
        (row for row in feature_gate_middle_exit_guard_lanes if row.get("lane") == "diagnostic_feature_window_entry"),
        {},
    )
    feature_gate_middle_exit_guard_post_entry = next(
        (row for row in feature_gate_middle_exit_guard_lanes if row.get("lane") == "post_middle_exit_guard_freeze_entry"),
        {},
    )
    feature_gate_middle_exit_guard_diag_best = feature_gate_middle_exit_guard_diag_entry.get("best") or {}
    feature_gate_middle_exit_guard_post_best = feature_gate_middle_exit_guard_post_entry.get("best") or {}
    feature_gate_size_strict_drilldown_summary = {
        "entries": feature_gate_size_shrink_strict_drilldown.get("entries"),
        "settled": feature_gate_size_shrink_strict_drilldown.get("settled"),
        "wins": feature_gate_size_shrink_strict_drilldown.get("wins"),
        "losses": feature_gate_size_shrink_strict_drilldown.get("losses"),
        "coverage_pct": feature_gate_size_shrink_strict_drilldown.get("coverage_pct"),
        "weighted_net_cents": feature_gate_size_shrink_strict_drilldown.get("weighted_net_cents"),
        "delta_vs_live_cents": feature_gate_size_shrink_strict_drilldown.get("delta_vs_live_cents"),
        "reconstructed_share": feature_gate_size_shrink_strict_drilldown.get("reconstructed_share"),
        "clean_rows_needed_for_source": feature_gate_size_shrink_strict_drilldown.get("clean_rows_needed_for_source"),
        "clean_full_wins_needed_for_live": feature_gate_size_shrink_strict_drilldown.get("clean_full_wins_needed_for_live"),
        "omitted_positive_approved_count": feature_gate_size_shrink_strict_drilldown.get("omitted_positive_approved_count"),
        "omitted_positive_reconstructed_count": feature_gate_size_shrink_strict_drilldown.get("omitted_positive_reconstructed_count"),
        "loss_tag_counts": feature_gate_size_shrink_strict_drilldown.get("loss_tag_counts"),
        "blockers": feature_gate_size_shrink_strict_drilldown.get("blockers"),
    }
    feature_gate_observable_selection_lanes = feature_gate_observable_selection_mix.get("lanes") or []
    feature_gate_observable_selection_entry = next(
        (row for row in feature_gate_observable_selection_lanes if row.get("lane") == "post_feature_freeze_entry"),
        {},
    )
    feature_gate_observable_selection_bridge = next(
        (row for row in feature_gate_observable_selection_lanes if row.get("lane") == "post_feature_freeze_bridge"),
        {},
    )
    feature_gate_size_exit_overlay_lanes = feature_gate_size_shrink_exit_overlay.get("lanes") or []
    feature_gate_size_exit_overlay_entry = next(
        (row for row in feature_gate_size_exit_overlay_lanes if row.get("lane") == "post_feature_freeze_entry"),
        {},
    )
    feature_gate_size_exit_overlay_bridge = next(
        (row for row in feature_gate_size_exit_overlay_lanes if row.get("lane") == "post_feature_freeze_bridge"),
        {},
    )
    feature_gate_size_delayed_exit_lanes = feature_gate_size_shrink_delayed_recheck_exit.get("lanes") or []
    feature_gate_size_delayed_exit_diag = next(
        (row for row in feature_gate_size_delayed_exit_lanes if row.get("lane") == "diagnostic_prefreeze_context"),
        {},
    )
    feature_gate_size_delayed_exit_post = next(
        (row for row in feature_gate_size_delayed_exit_lanes if row.get("lane") == "post_delayed_recheck_overlay_birth"),
        {},
    )
    feature_gate_size_delayed_exit_diag_best = feature_gate_size_delayed_exit_diag.get("best") or {}
    feature_gate_size_delayed_exit_post_best = feature_gate_size_delayed_exit_post.get("best") or {}
    feature_gate_size_delayed_rescue_lanes = feature_gate_size_shrink_delayed_recheck_rescue.get("lanes") or []
    feature_gate_size_delayed_rescue_diag = next(
        (row for row in feature_gate_size_delayed_rescue_lanes if row.get("lane") == "diagnostic_prefreeze_context"),
        {},
    )
    feature_gate_size_delayed_rescue_post = next(
        (row for row in feature_gate_size_delayed_rescue_lanes if row.get("lane") == "post_rescue_overlay_birth"),
        {},
    )
    feature_gate_size_delayed_rescue_diag_best = feature_gate_size_delayed_rescue_diag.get("best") or {}
    feature_gate_size_delayed_rescue_post_best = feature_gate_size_delayed_rescue_post.get("best") or {}
    feature_gate_source_confirmation_lanes = feature_gate_source_confirmation_replacement.get("lanes") or []
    feature_gate_source_confirmation_diag = next(
        (row for row in feature_gate_source_confirmation_lanes if row.get("lane") == "diagnostic_prefreeze_context"),
        {},
    )
    feature_gate_source_confirmation_post = next(
        (row for row in feature_gate_source_confirmation_lanes if row.get("lane") == "post_confirmation_replacement_birth"),
        {},
    )
    feature_gate_source_confirmation_diag_best = feature_gate_source_confirmation_diag.get("replacement_rescue_best") or {}
    feature_gate_source_confirmation_post_best = feature_gate_source_confirmation_post.get("replacement_rescue_best") or {}
    feature_gate_late_collapse_lanes = feature_gate_late_collapse_recheck_rescue.get("lanes") or []
    feature_gate_late_collapse_diag = next(
        (row for row in feature_gate_late_collapse_lanes if row.get("lane") == "diagnostic_prefreeze_context"),
        {},
    )
    feature_gate_late_collapse_post = next(
        (row for row in feature_gate_late_collapse_lanes if row.get("lane") == "post_late_collapse_rescue_birth"),
        {},
    )
    feature_gate_late_collapse_diag_best = feature_gate_late_collapse_diag.get("best") or {}
    feature_gate_late_collapse_post_best = feature_gate_late_collapse_post.get("best") or {}
    feature_gate_dual_clock_lanes = feature_gate_dual_clock_recheck_rescue.get("lanes") or []
    feature_gate_dual_clock_diag = next(
        (row for row in feature_gate_dual_clock_lanes if row.get("lane") == "diagnostic_prefreeze_context"),
        {},
    )
    feature_gate_dual_clock_post = next(
        (row for row in feature_gate_dual_clock_lanes if row.get("lane") == "post_dual_clock_rescue_birth"),
        {},
    )
    feature_gate_dual_clock_diag_best = feature_gate_dual_clock_diag.get("best") or {}
    feature_gate_dual_clock_post_best = feature_gate_dual_clock_post.get("best") or {}
    feature_gate_confirmed_dual_lanes = feature_gate_confirmed_dual_clock_fill.get("lanes") or []
    feature_gate_confirmed_dual_diag = next(
        (row for row in feature_gate_confirmed_dual_lanes if row.get("lane") == "diagnostic_prefreeze_context"),
        {},
    )
    feature_gate_confirmed_dual_post = next(
        (row for row in feature_gate_confirmed_dual_lanes if row.get("lane") == "post_confirmed_dual_clock_fill_birth"),
        {},
    )
    feature_gate_confirmed_dual_diag_best = feature_gate_confirmed_dual_diag.get("best") or {}
    feature_gate_confirmed_dual_post_best = feature_gate_confirmed_dual_post.get("best") or {}
    feature_gate_confirmed_dual_stress_candidate = feature_gate_confirmed_dual_clock_fill_stress.get("candidate") or {}
    feature_gate_confirmed_dual_stress_blockers = feature_gate_confirmed_dual_clock_fill_stress.get("stress_blockers") or []
    feature_gate_confirmed_dual_rule_stress = feature_gate_confirmed_dual_clock_fill_stress.get("rule_component_stress") or []
    feature_gate_source_proxy_lanes = feature_gate_source_quality_proxy.get("lanes") or []
    feature_gate_source_proxy_diag_entry = next(
        (row for row in feature_gate_source_proxy_lanes if row.get("lane") == "diagnostic_feature_freeze_entry"),
        {},
    )
    feature_gate_source_proxy_diag_bridge = next(
        (row for row in feature_gate_source_proxy_lanes if row.get("lane") == "diagnostic_feature_freeze_bridge"),
        {},
    )
    feature_gate_source_proxy_post_entry = next(
        (row for row in feature_gate_source_proxy_lanes if row.get("lane") == "post_source_proxy_birth_entry"),
        {},
    )
    feature_gate_source_proxy_post_bridge = next(
        (row for row in feature_gate_source_proxy_lanes if row.get("lane") == "post_source_proxy_birth_bridge"),
        {},
    )
    feature_gate_source_proxy_repair_lanes = feature_gate_source_proxy_coverage_repair.get("lanes") or []
    feature_gate_source_proxy_repair_diag_entry = next(
        (row for row in feature_gate_source_proxy_repair_lanes if row.get("lane") == "diagnostic_feature_freeze_entry"),
        {},
    )
    feature_gate_source_proxy_repair_diag_bridge = next(
        (row for row in feature_gate_source_proxy_repair_lanes if row.get("lane") == "diagnostic_feature_freeze_bridge"),
        {},
    )
    feature_gate_source_proxy_repair_post_entry = next(
        (row for row in feature_gate_source_proxy_repair_lanes if row.get("lane") == "post_source_proxy_birth_entry"),
        {},
    )
    feature_gate_source_proxy_repair_post_bridge = next(
        (row for row in feature_gate_source_proxy_repair_lanes if row.get("lane") == "post_source_proxy_birth_bridge"),
        {},
    )
    feature_gate_source_proxy_autopsy_lanes = feature_gate_source_proxy_strict_autopsy.get("lanes") or []
    feature_gate_source_proxy_autopsy_entry = next(
        (row for row in feature_gate_source_proxy_autopsy_lanes if row.get("lane") == "post_source_proxy_birth_entry"),
        {},
    )
    feature_gate_source_proxy_autopsy_bridge = next(
        (row for row in feature_gate_source_proxy_autopsy_lanes if row.get("lane") == "post_source_proxy_birth_bridge"),
        {},
    )
    feature_gate_source_blocker_lanes = feature_gate_source_blocker_mechanism.get("lanes") or []
    feature_gate_source_blocker_entry = next(
        (row for row in feature_gate_source_blocker_lanes if row.get("lane") == "post_feature_freeze_entry"),
        {},
    )
    feature_gate_source_blocker_bridge = next(
        (row for row in feature_gate_source_blocker_lanes if row.get("lane") == "post_feature_freeze_bridge"),
        {},
    )
    def compact_source_blocker_summary(row: dict[str, Any]) -> dict[str, Any]:
        selected = row.get("selected_summary") or {}
        approved = row.get("approved_selected_summary") or {}
        source = row.get("source_selected_summary") or {}
        oracle = row.get("source_oracle_replacement") or {}
        return {
            "selected_entries": selected.get("entries"),
            "selected_settled": selected.get("settled"),
            "selected_wl": f"{selected.get('wins')}/{selected.get('losses')}",
            "selected_weighted_net_cents": selected.get("weighted_net_cents"),
            "selected_row_reconstructed_share": selected.get("row_reconstructed_share"),
            "approved_entries": approved.get("entries"),
            "approved_weighted_net_cents": approved.get("weighted_net_cents"),
            "source_entries": source.get("entries"),
            "source_weighted_net_cents": source.get("weighted_net_cents"),
            "same_market_alternates": len(row.get("same_market_alternates") or []),
            "oracle_omitted_approved_available": oracle.get("omitted_approved_available"),
            "oracle_first_clear": oracle.get("first_oracle_clear"),
        }
    feature_gate_source_blocker_entry_summary = {
        **compact_source_blocker_summary(feature_gate_source_blocker_entry),
    }
    feature_gate_source_blocker_bridge_summary = {
        **compact_source_blocker_summary(feature_gate_source_blocker_bridge),
    }
    high_win_core_broad_fill_best = (high_win_core_broad_fill_mix.get("rows") or [{}])[0]
    p50_book_edge_best_child = p50_book_edge_source_failure_drilldown.get("best_positive_target_coverage_variant") or {}
    p50_book_edge_source_bound = p50_book_edge_source_feasibility_bound.get("feasibility_bound") or {}
    p50_book_edge_no_side_shrink_summary = p50_book_edge_no_side_shrink_watch.get("summary") or {}
    p50_soft_frontier_best_mix = p50_soft_frontier_overlap_mix.get("best_positive_target_coverage") or {}
    feature_gate_runway_post = (boundary_clock_feature_gate_runway.get("post_freeze_top") or [{}])[0]
    feature_gate_failure_lanes = boundary_clock_feature_gate_failure_modes.get("lanes") or {}
    feature_gate_failure_post = (feature_gate_failure_lanes.get("post_feature_freeze_entry") or [{}])[0]
    feature_gate_failure_diag = (feature_gate_failure_lanes.get("diagnostic_entry") or [{}])[0]
    feature_gate_loss_lanes = boundary_clock_feature_gate_loss_analog.get("lanes") or {}
    feature_gate_loss_post = feature_gate_loss_lanes.get("post_feature_freeze_entry") or {}
    feature_gate_loss_diag = feature_gate_loss_lanes.get("diagnostic_entry") or {}
    feature_gate_row_lanes = boundary_clock_feature_gate_row_ledger.get("lanes") or []
    feature_gate_row_entry = next((row for row in feature_gate_row_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    feature_gate_row_bridge = next((row for row in feature_gate_row_lanes if row.get("lane") == "post_feature_freeze_bridge"), {})
    feature_gate_row_entry_best = (feature_gate_row_entry.get("rules") or [{}])[0]
    feature_gate_row_bridge_best = (feature_gate_row_bridge.get("rules") or [{}])[0]
    feature_gate_recovery_lanes = boundary_clock_feature_gate_coverage_recovery.get("lanes") or []
    feature_gate_recovery_entry = next((row for row in feature_gate_recovery_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    feature_gate_recovery_entry_strict = feature_gate_recovery_entry.get("strict_summary") or {}
    feature_gate_recovery_entry_broad = next(
        (row for row in feature_gate_recovery_entry.get("variants") or [] if row.get("rule") != feature_gate_recovery_entry.get("strict_rule")),
        {},
    )
    feature_gate_recovery_entry_broad_summary = feature_gate_recovery_entry_broad.get("summary") or {}
    feature_gate_recovery_entry_broad_comparison = feature_gate_recovery_entry_broad.get("strict_comparison") or {}
    feature_gate_source_lanes = boundary_clock_feature_gate_source_denominator.get("lanes") or []
    feature_gate_source_entry = next((row for row in feature_gate_source_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    feature_gate_source_entry_best = (feature_gate_source_entry.get("rules") or [{}])[0]
    feature_gate_frontier_lanes = boundary_clock_feature_gate_coverage_source_frontier.get("lanes") or []
    feature_gate_frontier_entry = next((row for row in feature_gate_frontier_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    feature_gate_frontier_entry_best = (feature_gate_frontier_entry.get("pareto_frontier") or [{}])[0]
    feature_gate_frontier_entry_summary = feature_gate_frontier_entry_best.get("summary") or {}
    feature_gate_feasibility_lanes = feature_gate_source_feasibility_bound.get("lanes") or []
    feature_gate_feasibility_entry = next((row for row in feature_gate_feasibility_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    feature_gate_feasibility_entry_75 = next(
        (row for row in feature_gate_feasibility_entry.get("target_bounds") or [] if row.get("target_coverage_pct") == 75.0),
        {},
    )
    feature_gate_promotion_rows = feature_gate_promotion_gap.get("official_feature_gate_rows") or []
    feature_gate_promotion_broad = next(
        (row for row in feature_gate_promotion_rows if row.get("candidate") == "post_feature_freeze_entry_raw03_recross70_abs075"),
        feature_gate_promotion_rows[0] if feature_gate_promotion_rows else {},
    )
    feature_gate_frontier_runway_lanes = boundary_clock_feature_gate_frontier_runway.get("lanes") or []
    feature_gate_frontier_runway_entry = next((row for row in feature_gate_frontier_runway_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    feature_gate_frontier_runway_entry_runway = feature_gate_frontier_runway_entry.get("runway") or {}
    feature_gate_frontier_mechanism_lanes = boundary_clock_feature_gate_frontier_mechanism.get("lanes") or []
    feature_gate_frontier_mechanism_entry = next((row for row in feature_gate_frontier_mechanism_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    feature_gate_frontier_mechanism_entry_summary = feature_gate_frontier_mechanism_entry.get("frontier_selected_summary") or {}
    feature_gate_frontier_mechanism_gained = feature_gate_frontier_mechanism_entry.get("gained_summary") or {}
    feature_gate_frontier_mechanism_omitted = feature_gate_frontier_mechanism_entry.get("omitted_summary") or {}
    feature_gate_outlier_lanes = boundary_clock_feature_gate_outlier_stress.get("lanes") or []
    feature_gate_outlier_entry = next((row for row in feature_gate_outlier_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    feature_gate_clean_broad_lanes = boundary_clock_feature_gate_clean_broad_frontier.get("lanes") or []
    feature_gate_clean_broad_diag_entry = next((row for row in feature_gate_clean_broad_lanes if row.get("lane") == "diagnostic_parent_entry"), {})
    feature_gate_clean_broad_post_entry = next((row for row in feature_gate_clean_broad_lanes if row.get("lane") == "post_clean_broad_freeze_entry"), {})
    feature_gate_clean_broad_diag_entry_summary = feature_gate_clean_broad_diag_entry.get("candidate_summary") or {}
    feature_gate_clean_broad_post_entry_summary = feature_gate_clean_broad_post_entry.get("candidate_summary") or {}
    feature_gate_soft_lanes = boundary_clock_feature_gate_soft_frontier.get("lanes") or []
    feature_gate_soft_diag_entry = next((row for row in feature_gate_soft_lanes if row.get("lane") == "diagnostic_entry"), {})
    feature_gate_soft_post_entry = next((row for row in feature_gate_soft_lanes if row.get("lane") == "post_soft_frontier_birth_entry"), {})
    feature_gate_soft_diag_entry_best = (feature_gate_soft_diag_entry.get("variants") or [{}])[0]
    feature_gate_soft_post_entry_best = (feature_gate_soft_post_entry.get("variants") or [{}])[0]
    feature_gate_soft_diag_entry_summary = feature_gate_soft_diag_entry_best.get("candidate_summary") or {}
    feature_gate_soft_post_entry_summary = feature_gate_soft_post_entry_best.get("candidate_summary") or {}
    soft_frontier_failure_lanes = soft_frontier_post_birth_failure_drilldown.get("lanes") or []
    soft_frontier_failure_entry = next((row for row in soft_frontier_failure_lanes if row.get("lane") == "post_soft_frontier_birth_entry"), {})
    soft_frontier_failure_entry_summary = soft_frontier_failure_entry.get("summary") or {}
    midprice_lanes = soft_frontier_midprice_boundary_shrink.get("lanes") or []
    midprice_diag_best = next(
        (
            variant
            for lane in midprice_lanes
            if isinstance(lane, dict) and not lane.get("strict_forward")
            for variant in (lane.get("variants") or [])
            if isinstance(variant, dict)
        ),
        {},
    )
    midprice_strict_best = next(
        (
            variant
            for lane in midprice_lanes
            if isinstance(lane, dict) and lane.get("strict_forward")
            for variant in (lane.get("variants") or [])
            if isinstance(variant, dict)
        ),
        {},
    )
    midprice_diag_summary = midprice_diag_best.get("summary") or {}
    midprice_strict_summary = midprice_strict_best.get("summary") or {}
    midprice_dilution_lanes = midprice_source_dilution.get("lanes") or []
    midprice_dilution_diag_entry = next(
        (lane for lane in midprice_dilution_lanes if lane.get("lane") == "diagnostic_parent_entry"),
        {},
    )
    midprice_dilution_post_entry = next(
        (lane for lane in midprice_dilution_lanes if lane.get("lane") == "post_dilution_birth_entry"),
        {},
    )
    midprice_dilution_diag_best = (midprice_dilution_diag_entry.get("variants") or [{}])[0]
    midprice_dilution_post_best = (midprice_dilution_post_entry.get("variants") or [{}])[0]
    midprice_dilution_stability_entry = (midprice_source_dilution_stability.get("lanes") or [{}])[0]
    midprice_dilution_mechanism_summary = {
        "selected_summary": midprice_source_dilution_mechanism.get("selected_summary"),
        "approved_selected_summary": midprice_source_dilution_mechanism.get("approved_selected_summary"),
        "source_selected_summary": midprice_source_dilution_mechanism.get("source_selected_summary"),
        "source_oracle_replacement": midprice_source_dilution_mechanism.get("source_oracle_replacement"),
        "interpretation": midprice_source_dilution_mechanism.get("interpretation"),
    }
    midprice_exit_stack_variants = soft_frontier_midprice_boundary_exit_stack.get("variants") or []
    midprice_exit_stack_best = midprice_exit_stack_variants[0] if midprice_exit_stack_variants else {}
    midprice_exit_stack_entry_summary = midprice_exit_stack_best.get("entry_summary") or {}
    midprice_exit_stack_runway_best = (soft_frontier_midprice_boundary_exit_stack_runway.get("rows") or [{}])[0]
    feature_gate_ask_floor_lanes = boundary_clock_feature_gate_ask_floor.get("lanes") or []
    feature_gate_ask_floor_post_entry = next((row for row in feature_gate_ask_floor_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    feature_gate_ask_floor_diag_entry = next((row for row in feature_gate_ask_floor_lanes if row.get("lane") == "diagnostic_entry"), {})
    feature_gate_penalty_lanes = boundary_clock_feature_gate_continuous_penalty.get("lanes") or []
    feature_gate_penalty_pre_entry = next((row for row in feature_gate_penalty_lanes if row.get("lane") == "pre_penalty_birth_feature_entry"), {})
    feature_gate_penalty_post_entry = next((row for row in feature_gate_penalty_lanes if row.get("lane") == "post_penalty_birth_entry"), {})
    feature_gate_penalty_diag_entry = next((row for row in feature_gate_penalty_lanes if row.get("lane") == "diagnostic_entry"), {})
    feature_gate_penalty_pre_entry_best = (feature_gate_penalty_pre_entry.get("variants") or [{}])[0]
    feature_gate_penalty_post_entry_best = (feature_gate_penalty_post_entry.get("variants") or [{}])[0]
    feature_gate_penalty_diag_entry_best = (feature_gate_penalty_diag_entry.get("variants") or [{}])[0]
    feature_gate_penalty_pre_entry_summary = feature_gate_penalty_pre_entry_best.get("candidate_summary") or {}
    feature_gate_penalty_post_entry_summary = feature_gate_penalty_post_entry_best.get("candidate_summary") or {}
    feature_gate_penalty_diag_entry_summary = feature_gate_penalty_diag_entry_best.get("candidate_summary") or {}
    feature_gate_penalty_stress_lanes = boundary_clock_feature_gate_continuous_penalty_stress.get("lanes") or []
    feature_gate_penalty_stress_post_entry = next((row for row in feature_gate_penalty_stress_lanes if row.get("lane") == "post_penalty_birth_entry"), {})
    feature_gate_residual_lanes = boundary_clock_feature_gate_residual_loss.get("lanes") or {}
    feature_gate_residual_diag_entry = feature_gate_residual_lanes.get("diagnostic_entry") or {}
    feature_gate_residual_pre_entry = feature_gate_residual_lanes.get("pre_penalty_birth_feature_entry") or {}
    feature_gate_residual_post_entry = feature_gate_residual_lanes.get("post_penalty_birth_entry") or {}
    cheap_tail_lanes = feature_gate_cheap_tail_quarantine.get("lanes") or []
    cheap_tail_diag_entry = next((row for row in cheap_tail_lanes if row.get("lane") == "diagnostic_feature_window_entry"), {})
    cheap_tail_post_entry = next((row for row in cheap_tail_lanes if row.get("lane") == "post_quarantine_freeze_entry"), {})
    cheap_tail_diag_core = (cheap_tail_diag_entry.get("core_rules") or [{}])[0]
    cheap_tail_diag_tail = (cheap_tail_diag_entry.get("tail_rules") or [{}])[0]
    cheap_tail_post_core = (cheap_tail_post_entry.get("core_rules") or [{}])[0]
    cheap_tail_post_tail = (cheap_tail_post_entry.get("tail_rules") or [{}])[0]
    cheap_tail_diag_core_summary = cheap_tail_diag_core.get("summary") or {}
    cheap_tail_diag_tail_summary = cheap_tail_diag_tail.get("summary") or {}
    cheap_tail_post_core_summary = cheap_tail_post_core.get("summary") or {}
    cheap_tail_post_tail_summary = cheap_tail_post_tail.get("summary") or {}
    cheap_tail_shrink_lanes = feature_gate_cheap_tail_shrink_watch.get("lanes") or []
    cheap_tail_shrink_entry = next(
        (row for row in cheap_tail_shrink_lanes if row.get("lane") == "post_cheap_tail_shrink_birth_entry"),
        {},
    )
    cheap_tail_shrink_best = (cheap_tail_shrink_entry.get("policies") or [{}])[0]
    source_risk_shrink_lanes = feature_gate_source_risk_shrink_watch.get("lanes") or []
    source_risk_shrink_diag_entry = next(
        (row for row in source_risk_shrink_lanes if row.get("lane") == "diagnostic_feature_window_entry"),
        {},
    )
    source_risk_shrink_post_entry = next(
        (row for row in source_risk_shrink_lanes if row.get("lane") == "post_source_risk_birth_entry"),
        {},
    )
    source_risk_shrink_diag_best = (source_risk_shrink_diag_entry.get("policies") or [{}])[0]
    source_risk_shrink_post_best = (source_risk_shrink_post_entry.get("policies") or [{}])[0]
    sidecar_counts = sidecar_live_test_watch.get("counts") or {}
    sidecar_closest = (sidecar_live_test_watch.get("closest_positive") or [{}])[0]
    continuous_penalty_sidecar_best = continuous_penalty_sidecar_runway.get("best") or {}
    near_gate_counts = near_gate_runway.get("counts") or {}
    near_gate_closest_strict = (near_gate_runway.get("top_strict_target_positive") or [{}])[0]
    sidecar_top_net = (sidecar_live_test_watch.get("top_net") or [{}])[0]
    dual_lane_counts = dual_lane_overlap_portfolio.get("lane_counts") or {}
    dual_lane_top_strict = (dual_lane_overlap_portfolio.get("top_strict_post_portfolios") or [{}])[0]
    dual_lane_top_diag = (dual_lane_overlap_portfolio.get("top_portfolios") or [{}])[0]
    dual_lane_top_confirmation = (dual_lane_overlap_portfolio.get("top_confirmations") or [{}])[0]
    dual_lane_top_strict_confirmation = (dual_lane_overlap_portfolio.get("top_strict_confirmations") or [{}])[0]
    dual_lane_own_freeze_unions = dual_lane_own_freeze_watch.get("unions") or []
    dual_lane_own_freeze_best = dual_lane_own_freeze_unions[0] if dual_lane_own_freeze_unions else {}
    dual_lane_delta_classes = dual_lane_same_window_delta_autopsy.get("classification_summary") or []
    dual_lane_delta_worst = dual_lane_delta_classes[0] if dual_lane_delta_classes else {}
    dual_lane_sequence_mechanisms = dual_lane_same_window_sequence_mechanism.get("mechanism_summary") or []
    dual_lane_sequence_worst = dual_lane_sequence_mechanisms[0] if dual_lane_sequence_mechanisms else {}
    dual_lane_state_repair_best = dual_lane_state_exposure_sequence_repair.get("best_variant") or {}
    dual_lane_side_flip_candidate_summary = dual_lane_side_flip_feasibility.get("candidate_side_flip_summary") or {}
    dual_lane_side_flip_rescue_summary = dual_lane_side_flip_feasibility.get("candidate_opposite_rescue_summary") or {}
    control_risk_triage_summary = control_risk_candidate_triage.get("summary") or {}
    control_risk_triage_risk = control_risk_candidate_triage.get("risk_summary") or {}
    control_risk_top_apparent = (control_risk_candidate_triage.get("top_apparent_tracker_control_only") or [{}])[0]

    combo_post = {}
    for window in combo.get("windows") or []:
        if window.get("window") != "post_freeze_candidate":
            continue
        for scenario in window.get("scenarios") or []:
            if scenario.get("scenario") == "lead_approved_only":
                combo_post = scenario
                break

    approved_rows = approved_book.get("ranked") if isinstance(approved_book.get("ranked"), list) else []
    approved_book_raw = next((row for row in approved_rows if row.get("overlay") == "raw_probability"), {})
    approved_book_book = next((row for row in approved_rows if row.get("overlay") == "book_probability"), {})
    conditional_future = conditional_book.get("future") or {}
    conditional_candidate = conditional_future.get("candidate") if isinstance(conditional_future, dict) else {}
    blend_freeze = approved_book_raw_blend.get("freeze") or {}
    blend_future = approved_book_raw_blend.get("future") or {}
    blend_prefreeze = approved_book_raw_blend.get("prefreeze_context") or {}
    blend_future_primary = blend_future.get("primary") if isinstance(blend_future, dict) else {}
    blend_prefreeze_primary = blend_prefreeze.get("primary") if isinstance(blend_prefreeze, dict) else {}
    phi_diag = first_rank(phi, "discovery")
    phi_forward = first_rank(phi, "forward")

    decisions = [
        {
            "lane": "exit_policy",
            "decision": "pursue_forward",
            "candidate": "midprice_boundary_book_gap_or_clip_no_boundary_suppress / reduce_drift_guard / shallow_duration_lte52_watch / value_v2_reduce_depth384",
            "why": "Best diagnostic exit stacks recover clipped winners. The new mid-price boundary book-gap/clip union is the strongest broad diagnostic mix so far, and the no-boundary-suppress guard removes its diagnostic suppressed-loser flaw by respecting the entry system's own downweighting. Blanket probability-reduce suppression is explicitly not promotable because one suppressed loser turned a controlled reduce exit into a large loss; cleaner child guards remain watch-only until their own strict post-freeze suppressions arrive. The common-clock runway keeps the nearest strict exit row watch-only because it is positive but far below suppression-count and cushion gates. The residual frontier now explains the next temptation: broad low-p_hold residual suppression adds a lot of PnL but reintroduces false holds, while the clean collapse-full residual is only a 4-5 row child-watch clue. The unresolved-loss separator adds a sharper diagnostic: shallow fair-value drawdown at exit isolates a hold-helpful matched-loss pocket, but the broad full-denominator watch still has harmful suppressions. The matched-unchanged loss guard is now a guarded frozen watch that removed the diagnostic harmful rows, but it has to earn strict post-freeze rows before it can influence any exit stack. The true-loser hold-risk audit is the safety boundary for this work: there is a large FV/entry-timing population where holding would make losses worse, so broad exit suppression must prove it avoids those states. The false-hold guardrail bridge translates strict harmful suppressions into concrete rejection signals: rich or 60c+ exits with p_hold in the 0.75-0.85 band and positive fair drawdown must be treated as dangerous until a strict child proves otherwise. The refreshed loss-churn guarded frontier clarifies the core blocker: diagnostic labels can separate many clipped-winner losses, but the best observable-only clean guard is still sparse. The new full-denominator replay makes that observable clue more credible: recross_ge_045 selected 15 known rows, flipped 5 losses, added 574c, and created no harmful holds or new losses, but it remains diagnostic and under the 30-decision evidence floor. The clock-feasibility audit says recross is observable at row/entry scope, but the scorecard lacks exit_ts and some selected rows have no exit event fields. A materialized exit-clock snapshot fixed the denominator; on that snapshot recross_ge_045 is clean but only 8 rows and +124c, while looser thresholds add harmful/new-loss rows. The low-edge hold-guard tradeoff closes another simple broadening path: the broad exit-hold pocket is strong but has one low-edge false hold, and the best clean raw-edge guard has only 19 selected decisions with no clean >=30 policy. The neighbor autopsy makes the mechanism sharper: the low-edge slice is mixed rather than useless, but the clean high-edge survivor is still only 19 rows. This means recross and low-edge guarding are sparse mechanism clues, not candidates to freeze. The new rule-overlap audit clarifies that book_gap_loss_guard has clean current strict suppressions so far, but its false-hold blocker is still prior mechanism risk plus immature density, while book_gap_suppression and dual_exit have observed current strict harm. The loss-guard mechanism audit explains the physical separation: current false-hold danger rows were left unsuppressed by p-hold/book-gap floors, while the clean helpful suppressions are still sparse and some sit close to the value p-hold floor. The threshold-margin stress says the branch is still fragile: v1 survives a tiny p-hold nudge to 0.86 but is flat by 0.88, while v3 remains clean but has only two suppressions and loses almost all delta if the fair-drawdown allowance is tightened. The new v3 residual size-shrink audit rejects an easy relaxation: the v1-only residual bucket is positive in the tiny strict-v3 sample but negative in all-exit diagnostic evidence due to a rare false hold, so v3's hard rejection remains the safer default until a separately frozen residual watch earns rows. The observable reduce false-hold autopsy downgrades that branch again: its post-birth p_hold>=0.75 probability-reduce denominator is negative, and the tiny zero-harm post-hoc splits are not evidence to broaden suppression. The path-risk audit adds a separate survival constraint: v1 has no 25c adverse excursions but did require two 10c+ adverse holds and one below-zero mark, while v3 has cleaner path marks on only two suppressions. The feature-gate hold counterfactual shows exits saved losers but clipped winners much more, and the new feature-gate exit/state frontier says value_over_hold suppression is cleaner than broad reduce/collapse suppression on live-selected overlap. The value-exit/feature-gate contrast found that same-side entry geometry filtered the current value-only suppressed loser, so the high-exit-bid clip, feature-gate value-over-hold, and value-exit feature-side guards are now separate frozen watches. The high-exit-bid path-risk audit adds a survival blocker: several diagnostic winner holds had 25-50c adverse marks after the exit. The delayed-recheck child is the first frozen answer to that path-survival problem. The new broad soft-frontier/mid-price delayed-recheck composition is stronger diagnostically than the prior top stack and has no harmful suppressions in context; its path-risk audit shows only one diagnostic suppressed row worse than -10c after recheck and none worse than -25c. A looser drop15 rescue improves diagnostic PnL but reintroduces a -54c post-recheck adverse mark; the disaster-guard scan cannot remove that risk without nearly giving back the improvement. The clean drop11 rescue is now frozen as the better child: it keeps the extra false-negative recovery, improves diagnostic net versus the base delayed-recheck, and has clean diagnostic path risk. Broad delayed-recheck children and the matched-unchanged guard remain strict-row waits; recross and low-edge hold guarding stay mechanism-only.",
            "evidence": {
                "frozen_rows": combo_post.get("settled"),
                "candidate_net_cents": combo_post.get("candidate_net_cents"),
                "reduce_delta_cents": reduce_summary.get("delta_vs_current_cents"),
                "reduce_rows": reduce_summary.get("settled"),
                "reduce_blocker_decision": reduce_blocker_decision.get("decision"),
                "reduce_blocker_interpretation": reduce_blocker_decision.get("interpretation"),
                "reduce_blanket_helpful_harmful": (
                    f"{(reduce_blocker_decision.get('base_blanket_suppression') or {}).get('suppressed_helpful_rows')}/"
                    f"{(reduce_blocker_decision.get('base_blanket_suppression') or {}).get('suppressed_harmful_rows')}"
                ),
                "reduce_blanket_loss_control_cost_cents": (reduce_blocker_decision.get("base_blanket_suppression") or {}).get("suppressed_loss_control_cost_cents"),
                "reduce_child_watch_summaries": reduce_blocker_decision.get("child_watch_summaries"),
                "book_gap_delta_cents": book_gap_summary.get("delta_vs_current_cents"),
                "book_gap_rows": book_gap_summary.get("settled"),
                "book_gap_loss_guard_freeze_ts": (exit_book_gap_loss_guard.get("freeze") or {}).get("freeze_ts_utc"),
                "book_gap_loss_guard_rows": book_gap_loss_guard_summary.get("settled"),
                "book_gap_loss_guard_delta_cents": book_gap_loss_guard_summary.get("delta_vs_current_cents"),
                "book_gap_loss_guard_discovery_net_cents": book_gap_loss_guard_discovery.get("candidate_gross_cents"),
                "book_gap_loss_guard_discovery_delta_cents": book_gap_loss_guard_discovery.get("delta_vs_current_cents"),
                "book_gap_loss_guard_discovery_loss_cost_cents": book_gap_loss_guard_discovery.get("loss_control_cost_cents"),
                "book_gap_loss_guard_comparable_net_cents": book_gap_loss_guard_comparable.get("candidate_gross_cents"),
                "book_gap_loss_guard_comparable_delta_cents": book_gap_loss_guard_comparable.get("delta_vs_current_cents"),
                "book_gap_loss_guard_comparable_loss_cost_cents": book_gap_loss_guard_comparable.get("loss_control_cost_cents"),
                "book_gap_loss_guard_blockers": exit_book_gap_loss_guard.get("blockers"),
                "book_gap_loss_guard_v2_freeze_ts": (exit_book_gap_loss_guard_v2.get("freeze") or {}).get("freeze_ts_utc"),
                "book_gap_loss_guard_v2_rows": book_gap_loss_guard_v2_summary.get("settled"),
                "book_gap_loss_guard_v2_delta_cents": book_gap_loss_guard_v2_summary.get("delta_vs_current_cents"),
                "book_gap_loss_guard_v2_discovery_net_cents": book_gap_loss_guard_v2_discovery.get("candidate_gross_cents"),
                "book_gap_loss_guard_v2_discovery_delta_cents": book_gap_loss_guard_v2_discovery.get("delta_vs_current_cents"),
                "book_gap_loss_guard_v2_discovery_loss_cost_cents": book_gap_loss_guard_v2_discovery.get("loss_control_cost_cents"),
                "book_gap_loss_guard_v2_comparable_net_cents": book_gap_loss_guard_v2_comparable.get("candidate_gross_cents"),
                "book_gap_loss_guard_v2_comparable_delta_cents": book_gap_loss_guard_v2_comparable.get("delta_vs_current_cents"),
                "book_gap_loss_guard_v2_comparable_loss_cost_cents": book_gap_loss_guard_v2_comparable.get("loss_control_cost_cents"),
                "book_gap_loss_guard_v2_blockers": exit_book_gap_loss_guard_v2.get("blockers"),
                "book_gap_value_only_freeze_ts": (exit_book_gap_value_only.get("freeze") or {}).get("freeze_ts_utc"),
                "book_gap_value_only_rows": book_gap_value_only_summary.get("settled"),
                "book_gap_value_only_delta_cents": book_gap_value_only_summary.get("delta_vs_current_cents"),
                "book_gap_value_only_loss_cost_cents": book_gap_value_only_summary.get("loss_control_cost_cents"),
                "book_gap_value_only_diag_net_cents": book_gap_value_only_diag_summary.get("candidate_gross_cents"),
                "book_gap_value_only_diag_delta_cents": book_gap_value_only_diag_summary.get("delta_vs_current_cents"),
                "book_gap_value_only_diag_suppressed_wl": (
                    book_gap_value_only_diag_summary.get("suppressed_winners"),
                    book_gap_value_only_diag_summary.get("suppressed_losers"),
                ),
                "book_gap_value_only_diag_loss_cost_cents": book_gap_value_only_diag_summary.get("loss_control_cost_cents"),
                "book_gap_value_only_blockers": exit_book_gap_value_only.get("blockers"),
                "book_gap_value_only_opportunity_rows": book_gap_value_only_opportunity_rows,
                "book_gap_value_only_opportunity_value_exits": book_gap_value_only_opportunity_value,
                "book_gap_value_only_opportunity_would_suppress": book_gap_value_only_opportunity_suppress,
                "book_gap_value_only_opportunity_delta_cents": exit_book_gap_value_only_opportunity.get("would_suppress_delta_cents"),
                "book_gap_value_only_opportunity_fail_reasons": exit_book_gap_value_only_opportunity.get("fail_reason_counts"),
                "exit_value_reduce_depth_freeze_ts": (exit_value_reduce_depth_composite.get("freeze") or {}).get("freeze_ts_utc"),
                "exit_value_reduce_depth_rows": exit_value_reduce_depth_summary.get("settled"),
                "exit_value_reduce_depth_delta_cents": exit_value_reduce_depth_summary.get("delta_vs_current_cents"),
                "exit_value_reduce_depth_diag_rule": exit_value_reduce_depth_diag_best.get("rule"),
                "exit_value_reduce_depth_diag_delta_cents": exit_value_reduce_depth_diag_summary.get("delta_vs_current_cents"),
                "exit_value_reduce_depth_diag_suppressed_wl": (
                    exit_value_reduce_depth_diag_summary.get("suppressed_winners"),
                    exit_value_reduce_depth_diag_summary.get("suppressed_losers"),
                ),
                "exit_value_reduce_depth_diag_loss_cost_cents": exit_value_reduce_depth_diag_summary.get("loss_control_cost_cents"),
                "exit_value_reduce_depth_blockers": exit_value_reduce_depth_composite.get("blockers"),
                "exit_value_reduce_depth_suppressed_loser_generated_at_utc": exit_value_reduce_depth_suppressed_loser.get("generated_at_utc"),
                "exit_value_reduce_depth_suppressed_loser_post_birth_hits": exit_value_reduce_depth_suppressed_loser.get("post_birth_suppressed_loser_hits"),
                "exit_value_reduce_depth_suppressed_loser_tag_counts": exit_value_reduce_depth_suppressed_loser.get("tag_counts"),
                "exit_value_reduce_depth_suppressed_loser_rows": exit_value_reduce_depth_suppressed_loser.get("rows"),
                "exit_reduce_current_floor_guard_generated_at_utc": exit_reduce_current_floor_guard_frontier.get("generated_at_utc"),
                "exit_reduce_current_floor_guard_lanes": exit_reduce_current_floor_guard_frontier.get("lanes"),
                "exit_reduce_current_floor_guard_interpretation": exit_reduce_current_floor_guard_frontier.get("interpretation"),
                "exit_value_reduce_depth_opportunity_rows": exit_value_reduce_depth_opportunity_primary.get("total_rows"),
                "exit_value_reduce_depth_opportunity_value_exits": exit_value_reduce_depth_opportunity_primary.get("value_over_hold_rows"),
                "exit_value_reduce_depth_opportunity_reduce_exits": exit_value_reduce_depth_opportunity_primary.get("probability_reduce_rows"),
                "exit_value_reduce_depth_opportunity_would_suppress": exit_value_reduce_depth_opportunity_primary.get("would_suppress_rows"),
                "exit_value_reduce_depth_opportunity_value_reduce_suppress": (
                    exit_value_reduce_depth_opportunity_primary.get("would_suppress_value_rows"),
                    exit_value_reduce_depth_opportunity_primary.get("would_suppress_reduce_rows"),
                ),
                "exit_value_reduce_depth_opportunity_delta_cents": exit_value_reduce_depth_opportunity_primary.get("would_suppress_delta_cents"),
                "exit_value_reduce_depth_opportunity_rows_needed": exit_value_reduce_depth_opportunity_primary.get("rows_needed"),
                "exit_value_reduce_depth_opportunity_suppressed_needed": exit_value_reduce_depth_opportunity_primary.get("suppressed_needed"),
                "exit_value_reduce_depth_opportunity_cushion_needed": exit_value_reduce_depth_opportunity_primary.get("net_cents_needed_for_cushion3"),
                "exit_value_reduce_depth_opportunity_fail_reasons": exit_value_reduce_depth_opportunity_primary.get("fail_reason_counts"),
                "book_gap_loss_guard_v2_opportunity_rows": book_gap_loss_guard_v2_opportunity_rows,
                "book_gap_loss_guard_v2_opportunity_soft_exits": book_gap_loss_guard_v2_opportunity_soft,
                "book_gap_loss_guard_v2_opportunity_would_suppress": book_gap_loss_guard_v2_opportunity_suppress,
                "book_gap_loss_guard_v2_opportunity_fail_reasons": exit_book_gap_loss_guard_v2_opportunity.get("fail_reason_counts"),
                "book_gap_loss_guard_v2_runway_rows_needed": loss_guard_v2_strict_runway.get("rows_needed"),
                "book_gap_loss_guard_v2_runway_suppressed_needed": loss_guard_v2_strict_runway.get("v2_suppressed_needed"),
                "book_gap_loss_guard_v2_runway_cushion_cents_needed": loss_guard_v2_strict_runway.get("net_cents_needed_for_cushion3"),
                "book_gap_loss_guard_v2_runway_v1_only_cost_cents": loss_guard_v2_strict_runway.get("v1_only_opportunity_cost_cents"),
                "book_gap_loss_guard_v2_runway_blockers": loss_guard_v2_strict_runway.get("blockers"),
                "book_gap_loss_guard_v1_strict_v1_only_cost_cents": loss_guard_v1_strict_runway.get("v1_only_opportunity_cost_cents"),
                "book_gap_loss_guard_v3_runway_rows_needed": loss_guard_v3_strict_runway.get("rows_needed"),
                "book_gap_loss_guard_v3_runway_suppressed_needed": loss_guard_v3_strict_runway.get("suppressed_needed"),
                "book_gap_loss_guard_v3_runway_cushion_cents_needed": loss_guard_v3_strict_runway.get("net_cents_needed_for_cushion3"),
                "book_gap_loss_guard_v3_runway_blockers": loss_guard_v3_strict_runway.get("blockers"),
                "book_gap_loss_guard_v3_residual_audit_generated_at_utc": exit_loss_guard_v3_residual_size_shrink.get("generated_at_utc"),
                "book_gap_loss_guard_v3_residual_strict_bucket": loss_guard_v3_residual_strict_bucket,
                "book_gap_loss_guard_v3_residual_diagnostic_bucket": loss_guard_v3_residual_diagnostic_bucket,
                "book_gap_loss_guard_v3_residual_strict_full_policy": loss_guard_v3_residual_strict_full,
                "book_gap_loss_guard_v3_residual_interpretation": exit_loss_guard_v3_residual_size_shrink.get("interpretation"),
                "book_gap_loss_guard_strict_variant_runways": loss_guard_strict_variant_runways,
                "book_gap_loss_guard_opportunity_rows": book_gap_loss_guard_opportunity_rows,
                "book_gap_loss_guard_opportunity_soft_exits": book_gap_loss_guard_opportunity_soft,
                "book_gap_loss_guard_opportunity_would_suppress": book_gap_loss_guard_opportunity_suppress,
                "book_gap_loss_guard_opportunity_fail_reasons": exit_book_gap_loss_guard_opportunity.get("fail_reason_counts"),
                "common_clock_strict_windows": exit_policy_common_clock.get("strict_forward_windows"),
                "common_clock_v1_strict_rows": common_clock_strict_v1.get("row_count"),
                "common_clock_v1_strict_best_policy": common_clock_strict_v1_best.get("policy"),
                "common_clock_v1_strict_best_net_cents": common_clock_strict_v1_best.get("candidate_gross_cents"),
                "common_clock_v1_strict_best_blockers": common_clock_strict_v1_best.get("blockers"),
                "common_clock_v2_strict_rows": common_clock_strict_v2.get("row_count"),
                "common_clock_v2_strict_best_policy": common_clock_strict_v2_best.get("policy"),
                "common_clock_v2_strict_best_net_cents": common_clock_strict_v2_best.get("candidate_gross_cents"),
                "common_clock_v2_strict_best_blockers": common_clock_strict_v2_best.get("blockers"),
                "common_clock_v3_strict_rows": common_clock_strict_v3.get("row_count"),
                "common_clock_v3_strict_best_policy": common_clock_strict_v3_best.get("policy"),
                "common_clock_v3_strict_best_net_cents": common_clock_strict_v3_best.get("candidate_gross_cents"),
                "common_clock_v3_strict_best_blockers": common_clock_strict_v3_best.get("blockers"),
                "common_clock_comparable_best_policy": common_clock_comparable_best.get("policy"),
                "common_clock_comparable_best_net_cents": common_clock_comparable_best.get("candidate_gross_cents"),
                "common_clock_comparable_best_loss_cost_cents": common_clock_comparable_best.get("loss_control_cost_cents"),
                "common_clock_runway_best": common_clock_runway_best,
                "common_clock_suppression_scarcity_best_policy": common_clock_scarcity_best.get("policy"),
                "common_clock_suppression_scarcity_best_suppressed": common_clock_scarcity_best.get("suppressed"),
                "common_clock_suppression_scarcity_best_candidate_net_cents": common_clock_scarcity_best.get(
                    "candidate_net_cents"
                ),
                "common_clock_suppression_scarcity_best_delta_cents": common_clock_scarcity_best.get("delta_cents"),
                "common_clock_suppression_scarcity_best_loss_cost_cents": common_clock_scarcity_best.get(
                    "loss_cost_cents"
                ),
                "common_clock_suppression_scarcity_best_blockers": common_clock_scarcity_best.get("blockers"),
                "common_clock_suppression_scarcity_v2_control_suppressed": common_clock_scarcity_control.get(
                    "suppressed"
                ),
                "common_clock_suppression_scarcity_v2_control_delta_cents": common_clock_scarcity_control.get(
                    "delta_cents"
                ),
                "common_clock_residual_frontier_generated_at_utc": exit_common_clock_residual_frontier.get(
                    "generated_at_utc"
                ),
                "common_clock_residual_v2_best": common_clock_residual_v2_best,
                "common_clock_residual_v2_clean": common_clock_residual_v2_clean,
                "common_clock_residual_v3_clean": common_clock_residual_v3_clean,
                "feature_gate_hold_counterfactual_selected_live_markets": feature_gate_hold_counterfactual_summary.get(
                    "selected_side_live_traded_markets"
                ),
                "feature_gate_hold_counterfactual_live_selected_net_cents": feature_gate_hold_counterfactual_summary.get(
                    "live_selected_net_cents"
                ),
                "feature_gate_hold_counterfactual_hold_net_cents": feature_gate_hold_counterfactual_summary.get(
                    "hold_to_settlement_net_cents"
                ),
                "feature_gate_hold_counterfactual_exit_delta_vs_hold_cents": feature_gate_hold_counterfactual_summary.get(
                    "exit_delta_vs_hold_cents"
                ),
                "feature_gate_hold_counterfactual_winner_delta_cents": feature_gate_hold_counterfactual_summary.get(
                    "winner_exit_delta_vs_hold_cents"
                ),
                "feature_gate_hold_counterfactual_loser_delta_cents": feature_gate_hold_counterfactual_summary.get(
                    "loser_exit_delta_vs_hold_cents"
                ),
                "feature_gate_hold_counterfactual_hurt_help_markets": (
                    f"{feature_gate_hold_counterfactual_summary.get('exit_hurt_markets')}/"
                    f"{feature_gate_hold_counterfactual_summary.get('exit_helped_markets')}"
                ),
                "feature_gate_hold_counterfactual_reason_counts": feature_gate_hold_counterfactual_summary.get(
                    "exit_reason_counts"
                ),
                "feature_gate_exit_state_frontier_best_variant": feature_gate_exit_state_frontier_best.get("variant"),
                "feature_gate_exit_state_frontier_best_net_cents": feature_gate_exit_state_frontier_best.get("simulated_net_cents"),
                "feature_gate_exit_state_frontier_best_delta_vs_live_cents": feature_gate_exit_state_frontier_best.get("delta_vs_baseline_cents"),
                "feature_gate_exit_state_frontier_value_net_cents": feature_gate_exit_state_frontier_value.get("simulated_net_cents"),
                "feature_gate_exit_state_frontier_value_delta_vs_live_cents": feature_gate_exit_state_frontier_value.get("delta_vs_baseline_cents"),
                "feature_gate_exit_state_frontier_p_hold80_net_cents": feature_gate_exit_state_frontier_value_phold80.get("simulated_net_cents"),
                "feature_gate_exit_state_frontier_p_hold80_delta_vs_live_cents": feature_gate_exit_state_frontier_value_phold80.get("delta_vs_baseline_cents"),
                "feature_gate_exit_state_frontier_best_blockers": feature_gate_exit_state_frontier_best.get("blockers"),
                "feature_gate_value_exit_watch_freeze_ts": (feature_gate_value_exit_watch.get("state") or {}).get("freeze_ts_utc"),
                "feature_gate_value_exit_watch_post_best": feature_gate_value_exit_post_best.get("variant"),
                "feature_gate_value_exit_watch_post_settled": feature_gate_value_exit_post_best.get("settled"),
                "feature_gate_value_exit_watch_post_net_cents": feature_gate_value_exit_post_best.get("candidate_net_cents"),
                "feature_gate_value_exit_watch_post_blockers": feature_gate_value_exit_post_best.get("blockers"),
                "value_exit_feature_gate_contrast_post_value_only_net_cents": value_exit_contrast_post_summary.get("value_only_net_cents"),
                "value_exit_feature_gate_contrast_post_guarded_net_cents": value_exit_contrast_post_summary.get("feature_side_guard_net_cents"),
                "value_exit_feature_gate_contrast_post_guard_delta_vs_value_cents": value_exit_contrast_post_summary.get("feature_side_guard_delta_vs_value_only_cents"),
                "value_exit_feature_gate_contrast_suppressed_loser_cost_cents": value_exit_contrast_post_summary.get("suppressed_loser_cost_cents"),
                "value_exit_feature_side_guard_freeze_ts": (value_exit_feature_side_guard.get("state") or {}).get("freeze_ts_utc"),
                "value_exit_feature_side_guard_post_rows": value_exit_guard_post_summary.get("rows"),
                "value_exit_feature_side_guard_post_net_cents": value_exit_guard_post_summary.get("feature_side_guard_net_cents"),
                "value_exit_feature_side_guard_post_blockers": value_exit_guard_post_summary.get("blockers"),
                "feature_gate_exit_separator_best_feature": feature_gate_exit_separator_best.get("feature"),
                "feature_gate_exit_separator_best_direction": feature_gate_exit_separator_best.get("direction"),
                "feature_gate_exit_separator_best_threshold": feature_gate_exit_separator_best.get("threshold"),
                "feature_gate_exit_separator_best_selected": feature_gate_exit_separator_best.get("selected_rows"),
                "feature_gate_exit_separator_best_helpful_harmful": (
                    f"{feature_gate_exit_separator_best.get('selected_helpful')}/"
                    f"{feature_gate_exit_separator_best.get('selected_harmful')}"
                ),
                "feature_gate_exit_separator_best_suppression_delta_cents": feature_gate_exit_separator_best.get(
                    "selected_suppression_delta_cents"
                ),
                "feature_gate_exit_separator_oracle_feature": feature_gate_exit_separator_oracle_best.get("feature"),
                "feature_gate_exit_bid_watch_freeze_ts": (
                    feature_gate_exit_bid_suppression_watch.get("state") or {}
                ).get("freeze_ts_utc"),
                "feature_gate_exit_bid_watch_diag_delta_cents": feature_gate_exit_bid_watch_diag.get("delta_vs_live_cents"),
                "feature_gate_exit_bid_watch_diag_helpful_harmful": (
                    f"{feature_gate_exit_bid_watch_diag.get('suppressed_helpful')}/"
                    f"{feature_gate_exit_bid_watch_diag.get('suppressed_harmful')}"
                ),
                "feature_gate_exit_bid_watch_post_settled": feature_gate_exit_bid_watch_post.get("settled"),
                "feature_gate_exit_bid_watch_post_suppressed": feature_gate_exit_bid_watch_post.get("suppressed_exits"),
                "feature_gate_exit_bid_watch_post_delta_cents": feature_gate_exit_bid_watch_post.get("delta_vs_live_cents"),
                "feature_gate_exit_bid_watch_post_blockers": feature_gate_exit_bid_watch_post.get("blockers"),
                "feature_gate_exit_bid_path_diag_rows_with_path": feature_gate_exit_bid_path_diag.get("rows_with_post_exit_path"),
                "feature_gate_exit_bid_path_diag_worst_min_after_exit_cents": feature_gate_exit_bid_path_diag.get("worst_min_after_exit_bid_cents"),
                "feature_gate_exit_bid_path_diag_adverse_10_25_50": (
                    feature_gate_exit_bid_path_diag.get("adverse_10c_rows"),
                    feature_gate_exit_bid_path_diag.get("adverse_25c_rows"),
                    feature_gate_exit_bid_path_diag.get("adverse_50c_rows"),
                ),
                "feature_gate_exit_bid_path_diag_blockers": feature_gate_exit_bid_path_diag.get("blockers"),
                "feature_gate_exit_bid_path_post_rows_with_path": feature_gate_exit_bid_path_post.get("rows_with_post_exit_path"),
                "feature_gate_exit_bid_delayed_freeze_ts": (
                    feature_gate_exit_bid_delayed_recheck.get("state") or {}
                ).get("freeze_ts_utc"),
                "feature_gate_exit_bid_delayed_diag_rows": feature_gate_exit_bid_delayed_diag.get("rows"),
                "feature_gate_exit_bid_delayed_diag_net_cents": feature_gate_exit_bid_delayed_diag.get("candidate_net_cents"),
                "feature_gate_exit_bid_delayed_diag_delta_cents": feature_gate_exit_bid_delayed_diag.get("delta_vs_live_cents"),
                "feature_gate_exit_bid_delayed_diag_helpful_harmful": (
                    f"{feature_gate_exit_bid_delayed_diag.get('helpful_suppressed')}/"
                    f"{feature_gate_exit_bid_delayed_diag.get('harmful_suppressed')}"
                ),
                "feature_gate_exit_bid_delayed_post_rows": feature_gate_exit_bid_delayed_post.get("rows"),
                "feature_gate_exit_bid_delayed_post_suppressed": feature_gate_exit_bid_delayed_post.get("suppressed"),
                "feature_gate_exit_bid_delayed_post_net_cents": feature_gate_exit_bid_delayed_post.get("candidate_net_cents"),
                "feature_gate_exit_bid_delayed_post_delta_cents": feature_gate_exit_bid_delayed_post.get("delta_vs_live_cents"),
                "feature_gate_exit_bid_delayed_post_blockers": feature_gate_exit_bid_delayed_post.get("blockers"),
                "soft_midprice_delayed_freeze_ts": (
                    soft_frontier_midprice_delayed_recheck_exit.get("state") or {}
                ).get("freeze_ts_utc"),
                "soft_midprice_delayed_diag_rows": soft_midprice_delayed_diag.get("rows"),
                "soft_midprice_delayed_diag_suppressed": soft_midprice_delayed_diag.get("suppressed"),
                "soft_midprice_delayed_diag_helpful_harmful": (
                    f"{soft_midprice_delayed_diag.get('helpful_suppressed')}/"
                    f"{soft_midprice_delayed_diag.get('harmful_suppressed')}"
                ),
                "soft_midprice_delayed_diag_net_cents": soft_midprice_delayed_diag.get("weighted_candidate_cents"),
                "soft_midprice_delayed_diag_delta_cents": soft_midprice_delayed_diag.get("weighted_delta_cents"),
                "soft_midprice_delayed_diag_reconstructed_share": soft_midprice_delayed_diag.get("reconstructed_share"),
                "soft_midprice_delayed_post_rows": soft_midprice_delayed_post.get("rows"),
                "soft_midprice_delayed_post_suppressed": soft_midprice_delayed_post.get("suppressed"),
                "soft_midprice_delayed_post_net_cents": soft_midprice_delayed_post.get("weighted_candidate_cents"),
                "soft_midprice_delayed_post_blockers": soft_midprice_delayed_post.get("blockers"),
                "soft_midprice_delayed_path_rows_with_post_recheck_path": soft_midprice_delayed_path_diag.get(
                    "rows_with_post_recheck_path"
                ),
                "soft_midprice_delayed_path_worst_after_exit_cents": soft_midprice_delayed_path_diag.get(
                    "worst_min_after_exit_bid_cents"
                ),
                "soft_midprice_delayed_path_worst_after_recheck_cents": soft_midprice_delayed_path_diag.get(
                    "worst_min_after_recheck_bid_cents"
                ),
                "soft_midprice_delayed_path_adverse_recheck_10_25_50": (
                    soft_midprice_delayed_path_diag.get("adverse_recheck_10c_rows"),
                    soft_midprice_delayed_path_diag.get("adverse_recheck_25c_rows"),
                    soft_midprice_delayed_path_diag.get("adverse_recheck_50c_rows"),
                ),
                "soft_midprice_delayed_path_blockers": soft_midprice_delayed_path_diag.get("blockers"),
                "soft_midprice_delayed_failure_loss_tag_counts": soft_midprice_delayed_failure_summary.get(
                    "loss_tag_counts"
                ),
                "soft_midprice_delayed_failure_false_negative_losses": soft_midprice_delayed_failure_summary.get(
                    "false_negative_suppression_losses"
                ),
                "soft_midprice_delayed_failure_false_negative_recoverable_cents": soft_midprice_delayed_failure_summary.get(
                    "false_negative_suppression_recoverable_cents"
                ),
                "soft_midprice_rescue_best_variant": (soft_midprice_rescue_best.get("variant") or {}).get("name"),
                "soft_midprice_rescue_best_net_cents": soft_midprice_rescue_best.get("candidate_net_cents"),
                "soft_midprice_rescue_best_delta_vs_base_cents": soft_midprice_rescue_best.get(
                    "delta_vs_base_delayed_cents"
                ),
                "soft_midprice_rescue_best_helpful_harmful": (
                    f"{soft_midprice_rescue_best.get('helpful_suppressed')}/"
                    f"{soft_midprice_rescue_best.get('harmful_suppressed')}"
                ),
                "soft_midprice_rescue_path_worst_after_recheck_cents": soft_midprice_rescue_path_summary.get(
                    "worst_min_after_recheck_bid_cents"
                ),
                "soft_midprice_rescue_path_adverse_recheck_10_25_50": (
                    soft_midprice_rescue_path_summary.get("adverse_recheck_10c_rows"),
                    soft_midprice_rescue_path_summary.get("adverse_recheck_25c_rows"),
                    soft_midprice_rescue_path_summary.get("adverse_recheck_50c_rows"),
                ),
                "soft_midprice_rescue_path_blockers": soft_midprice_rescue_path_summary.get("blockers"),
                "soft_midprice_clean_rescue_freeze_ts": (
                    soft_frontier_midprice_delayed_recheck_clean_rescue.get("state") or {}
                ).get("freeze_ts_utc"),
                "soft_midprice_clean_rescue_diag_rows": soft_midprice_clean_rescue_diag.get("rows"),
                "soft_midprice_clean_rescue_diag_suppressed": soft_midprice_clean_rescue_diag.get("suppressed"),
                "soft_midprice_clean_rescue_diag_helpful_harmful": (
                    f"{soft_midprice_clean_rescue_diag.get('helpful_suppressed')}/"
                    f"{soft_midprice_clean_rescue_diag.get('harmful_suppressed')}"
                ),
                "soft_midprice_clean_rescue_diag_net_cents": soft_midprice_clean_rescue_diag.get("weighted_candidate_cents"),
                "soft_midprice_clean_rescue_diag_delta_cents": soft_midprice_clean_rescue_diag.get("weighted_delta_cents"),
                "soft_midprice_clean_rescue_post_rows": soft_midprice_clean_rescue_post.get("rows"),
                "soft_midprice_clean_rescue_post_suppressed": soft_midprice_clean_rescue_post.get("suppressed"),
                "soft_midprice_clean_rescue_post_net_cents": soft_midprice_clean_rescue_post.get("weighted_candidate_cents"),
                "soft_midprice_clean_rescue_post_blockers": soft_midprice_clean_rescue_post.get("blockers"),
                "soft_midprice_clean_rescue_path_worst_after_recheck_cents": soft_midprice_clean_rescue_path_diag.get(
                    "worst_min_after_recheck_bid_cents"
                ),
                "soft_midprice_clean_rescue_path_adverse_recheck_10_25_50": (
                    soft_midprice_clean_rescue_path_diag.get("adverse_recheck_10c_rows"),
                    soft_midprice_clean_rescue_path_diag.get("adverse_recheck_25c_rows"),
                    soft_midprice_clean_rescue_path_diag.get("adverse_recheck_50c_rows"),
                ),
                "soft_midprice_clean_rescue_path_blockers": soft_midprice_clean_rescue_path_diag.get("blockers"),
                "soft_midprice_disaster_guard_best": (soft_midprice_disaster_guard_best.get("guard") or {}).get("name"),
                "soft_midprice_disaster_guard_best_net_cents": soft_midprice_disaster_guard_best.get("candidate_net_cents"),
                "soft_midprice_disaster_guard_best_delta_vs_base_cents": soft_midprice_disaster_guard_best.get(
                    "delta_vs_base_delayed_cents"
                ),
                "soft_midprice_disaster_guard_best_worst_pre_guard_cents": soft_midprice_disaster_guard_best.get(
                    "worst_min_until_guard_from_recheck_cents"
                ),
                "soft_midprice_disaster_guard_best_blockers": soft_midprice_disaster_guard_best.get("blockers"),
                "midprice_dual_exit_freeze_ts": (soft_frontier_midprice_boundary_dual_exit_stack.get("freeze") or {}).get("freeze_ts_utc"),
                "midprice_dual_exit_best_policy": dual_midprice_best.get("policy"),
                "midprice_dual_exit_best_exit_policy": dual_midprice_best.get("exit_policy"),
                "midprice_dual_exit_best_weighted_net_cents": dual_midprice_best.get("weighted_candidate_cents"),
                "midprice_dual_exit_best_delta_cents": dual_midprice_best.get("weighted_delta_cents"),
                "midprice_dual_exit_best_wl": (
                    f"{(dual_midprice_best.get('entry_summary') or {}).get('wins')}/"
                    f"{(dual_midprice_best.get('entry_summary') or {}).get('losses')}"
                ),
                "midprice_dual_exit_best_joined_rows": dual_midprice_best.get("joined_exit_rows"),
                "midprice_dual_exit_best_suppressed_losers": dual_midprice_best.get("suppressed_losers"),
                "midprice_dual_exit_best_blockers": dual_midprice_best.get("blockers"),
                "midprice_dual_exit_strict_policy": dual_midprice_strict.get("policy"),
                "midprice_dual_exit_strict_post_rows": dual_midprice_strict.get("post_stack_joined_rows"),
                "midprice_dual_exit_strict_blockers": dual_midprice_strict.get("blockers"),
                "midprice_dual_exit_guard_freeze_ts": (soft_frontier_midprice_boundary_dual_exit_guard.get("freeze") or {}).get("freeze_ts_utc"),
                "midprice_dual_exit_guard_best_policy": dual_midprice_guard_best.get("policy"),
                "midprice_dual_exit_guard_best_guard": dual_midprice_guard_best.get("guard"),
                "midprice_dual_exit_guard_best_weighted_net_cents": dual_midprice_guard_best.get("weighted_candidate_cents"),
                "midprice_dual_exit_guard_best_delta_cents": dual_midprice_guard_best.get("weighted_delta_cents"),
                "midprice_dual_exit_guard_best_suppressed_losers": dual_midprice_guard_best.get("suppressed_losers"),
                "midprice_dual_exit_guard_best_blockers": dual_midprice_guard_best.get("blockers"),
                "dual_exit_freeze_ts": (dual_exit.get("freeze") or {}).get("freeze_ts_utc"),
                "dual_exit_rows": dual_exit_summary.get("settled"),
                "dual_exit_delta_cents": dual_exit_summary.get("delta_vs_current_cents"),
                "dual_exit_source_counts": dual_exit.get("source_counts"),
                "dual_exit_blockers": dual_exit.get("blockers"),
                "suppressed_rows": reduce_risk_suppressed.get("rows"),
                "suppressed_net_delta_cents": reduce_risk_suppressed.get("net_delta_cents"),
                "helpful_suppressed_rows": reduce_risk_helpful.get("rows"),
                "helpful_suppressed_net_delta_cents": reduce_risk_helpful.get("net_delta_cents"),
                "harmful_suppressed_rows": reduce_risk_harmful.get("rows"),
                "harmful_suppressed_net_delta_cents": reduce_risk_harmful.get("net_delta_cents"),
                "p_hold_ge_079_net_delta_cents": (reduce_risk_groups.get("p_hold_ge_079") or {}).get("net_delta_cents"),
                "drawdown_lte_2p5_net_delta_cents": (reduce_risk_groups.get("drawdown_lte_2p5") or {}).get("net_delta_cents"),
                "loss_control_signature_suppressed_wl": f"{reduce_signature_summary.get('helpful_rows')}/{reduce_signature_summary.get('harmful_rows')}",
                "loss_control_signature_best_separator": f"{reduce_signature_best.get('feature')} {reduce_signature_best.get('direction')} {reduce_signature_best.get('threshold')}",
                "loss_control_signature_best_selected_wl": f"{reduce_signature_best.get('selected_helpful')}/{reduce_signature_best.get('selected_harmful')}",
                "loss_control_signature_best_delta_cents": reduce_signature_best.get("selected_delta_cents"),
                "loss_control_actionability_best_hindsight": f"{reduce_actionability_best_hindsight.get('feature')} {reduce_actionability_best_hindsight.get('direction')} {reduce_actionability_best_hindsight.get('threshold')}",
                "loss_control_actionability_best_observable": f"{reduce_actionability_best_observable.get('feature')} {reduce_actionability_best_observable.get('direction')} {reduce_actionability_best_observable.get('threshold')}",
                "loss_control_actionability_best_observable_wl": f"{reduce_actionability_best_observable.get('selected_helpful')}/{reduce_actionability_best_observable.get('selected_harmful')}",
                "loss_control_actionability_best_observable_delta_cents": reduce_actionability_best_observable.get("selected_delta_cents"),
                "loss_control_actionability_best_observable_frozen_watch": reduce_actionability_best_observable.get("frozen_watch"),
                "loss_control_actionability_needs_new_freeze_count": len(reduce_actionability_needs_freeze),
                "loss_control_refinement_freeze_ts": (reduce_refinement.get("state") or {}).get("freeze_ts_utc"),
                "loss_control_refinement_diagnostic_best": reduce_refinement_diag_best.get("candidate"),
                "loss_control_refinement_diagnostic_delta_cents": reduce_refinement_diag_summary.get("delta_vs_current_cents"),
                "loss_control_refinement_diagnostic_suppressed_wl": f"{reduce_refinement_diag_summary.get('suppressed_winners')}/{reduce_refinement_diag_summary.get('suppressed_losers')}",
                "loss_control_refinement_diagnostic_loss_cost_cents": reduce_refinement_diag_summary.get("loss_control_cost_cents"),
                "loss_control_refinement_post_settled": reduce_refinement_post_summary.get("settled"),
                "loss_control_refinement_post_delta_cents": reduce_refinement_post_summary.get("delta_vs_current_cents"),
                "loss_control_refinement_post_blockers": reduce_refinement_post_best.get("blockers"),
                "entry_depth_gate_freeze_ts": (reduce_depth_gate.get("state") or {}).get("freeze_ts_utc"),
                "entry_depth_gate_diagnostic_best": reduce_depth_diag_best.get("candidate"),
                "entry_depth_gate_diagnostic_delta_cents": reduce_depth_diag_summary.get("delta_vs_current_cents"),
                "entry_depth_gate_diagnostic_suppressed_wl": f"{reduce_depth_diag_summary.get('suppressed_winners')}/{reduce_depth_diag_summary.get('suppressed_losers')}",
                "entry_depth_gate_post_settled": reduce_depth_post_summary.get("settled"),
                "entry_depth_gate_post_delta_cents": reduce_depth_post_summary.get("delta_vs_current_cents"),
                "entry_depth_gate_post_blockers": reduce_depth_post_best.get("blockers"),
                "entry_depth_gate_runway_settled_needed": reduce_depth_runway_post.get("future_settled_rows_needed"),
                "entry_depth_gate_runway_suppressed_needed": reduce_depth_runway_post.get("future_suppressed_exits_needed"),
                "entry_depth_gate_runway_cushion_cents_needed": reduce_depth_runway_post.get("net_cents_needed_for_cushion3"),
                "entry_depth_gate_runway_ready": reduce_depth_runway_post.get("ready_for_consideration"),
                "entry_depth_gate_opportunity_probability_reduce_rows": reduce_depth_opportunity_best.get("probability_reduce_rows"),
                "entry_depth_gate_opportunity_would_suppress_rows": reduce_depth_opportunity_best.get("would_suppress_rows"),
                "entry_depth_gate_opportunity_fail_reasons": reduce_depth_opportunity_best.get("fail_reason_counts"),
                "observable_loss_control_freeze_ts": (reduce_observable_loss_control.get("state") or {}).get("freeze_ts_utc"),
                "observable_loss_control_diagnostic_best": reduce_observable_diag_best.get("candidate"),
                "observable_loss_control_diagnostic_delta_cents": reduce_observable_diag_summary.get("delta_vs_current_cents"),
                "observable_loss_control_diagnostic_suppressed_wl": f"{reduce_observable_diag_summary.get('suppressed_winners')}/{reduce_observable_diag_summary.get('suppressed_losers')}",
                "observable_loss_control_diagnostic_loss_cost_cents": reduce_observable_diag_summary.get("loss_control_cost_cents"),
                "observable_loss_control_post_settled": reduce_observable_post_summary.get("settled"),
                "observable_loss_control_post_delta_cents": reduce_observable_post_summary.get("delta_vs_current_cents"),
                "observable_loss_control_post_blockers": reduce_observable_post_best.get("blockers"),
                "observable_loss_control_opportunity_probability_reduce_rows": reduce_observable_opportunity_best.get("probability_reduce_rows"),
                "observable_loss_control_opportunity_p_hold_candidates": reduce_observable_opportunity_best.get("p_hold_candidate_rows"),
                "observable_loss_control_opportunity_would_suppress_rows": reduce_observable_opportunity_best.get("would_suppress_rows"),
                "observable_loss_control_opportunity_fail_reasons": reduce_observable_opportunity_best.get("fail_reason_counts"),
                "observable_false_hold_autopsy_generated_at_utc": reduce_observable_false_hold_autopsy.get("generated_at_utc"),
                "observable_false_hold_diagnostic_summary": reduce_observable_false_hold_diag_summary,
                "observable_false_hold_post_birth_summary": reduce_observable_false_hold_post_summary,
                "observable_false_hold_best_post_zero_harm_guard": reduce_observable_false_hold_best_post_guard,
                "observable_false_hold_interpretation": reduce_observable_false_hold_autopsy.get("interpretation"),
                "loss_churn_guarded_frontier_generated_at_utc": loss_churn_guarded_frontier.get("generated_at_utc"),
                "loss_churn_best_clean_diagnostic": loss_churn_best_clean,
                "loss_churn_best_observable_clean": loss_churn_best_observable,
                "loss_churn_guarded_frontier_interpretation": loss_churn_guarded_frontier.get("interpretation"),
                "loss_churn_full_denominator_generated_at_utc": loss_churn_observable_full_denominator_replay.get("generated_at_utc"),
                "loss_churn_full_denominator_best_clean": loss_churn_full_denom_best,
                "loss_churn_full_denominator_live_baseline_cents": loss_churn_observable_full_denominator_replay.get("live_baseline_cents"),
                "loss_churn_full_denominator_interpretation": loss_churn_observable_full_denominator_replay.get("interpretation"),
                "loss_churn_recross_clock_feasibility_generated_at_utc": loss_churn_recross_clock_feasibility.get("generated_at_utc"),
                "loss_churn_recross_clock_field_availability": loss_churn_recross_clock_feasibility.get("field_availability"),
                "loss_churn_recross_clock_blockers": loss_churn_recross_clock_feasibility.get("blockers"),
                "loss_churn_recross_clock_interpretation": loss_churn_recross_clock_feasibility.get("interpretation"),
                "loss_churn_recross_exit_clock_join_audit": loss_churn_recross_exit_clock_join_audit,
                "loss_churn_recross_threshold_frontier": loss_churn_recross_threshold_frontier,
                "exit_clock_source_stability": exit_clock_source_stability,
                "exit_clock_low_edge_hold_guard_tradeoff": exit_clock_low_edge_hold_guard_tradeoff,
                "exit_clock_broad_hold_neighbor_autopsy": exit_clock_broad_hold_neighbor_autopsy,
                "drift_guard_freeze_ts": (reduce_drift_guard_watch.get("state") or {}).get("freeze_ts_utc"),
                "drift_guard_diagnostic_best": reduce_drift_guard_diag.get("policy"),
                "drift_guard_diagnostic_delta_cents": reduce_drift_guard_diag.get("delta_vs_current_cents"),
                "drift_guard_diagnostic_suppressed_wl": f"{reduce_drift_guard_diag.get('suppressed_helpful')}/{reduce_drift_guard_diag.get('suppressed_harmful')}",
                "drift_guard_post_settled": reduce_drift_guard_post.get("settled"),
                "drift_guard_post_suppressed": reduce_drift_guard_post.get("suppressed"),
                "drift_guard_post_delta_cents": reduce_drift_guard_post.get("delta_vs_current_cents"),
                "drift_guard_post_blockers": reduce_drift_guard_post.get("blockers"),
                "loss_churn_best_lane": exit_policy_loss_churn_best.get("label"),
                "loss_churn_best_loss_count_reduction": exit_policy_loss_churn_best.get("loss_count_reduction"),
                "loss_churn_best_delta_cents": exit_policy_loss_churn_best.get("delta_cents"),
                "loss_churn_best_current_wl": f"{exit_policy_loss_churn_best.get('current_wins')}/{exit_policy_loss_churn_best.get('current_losses')}",
                "loss_churn_best_candidate_wl": f"{exit_policy_loss_churn_best.get('candidate_wins')}/{exit_policy_loss_churn_best.get('candidate_losses')}",
                "loss_churn_best_blockers": exit_policy_loss_churn_best.get("blockers"),
                "unresolved_separator_rows": exit_unresolved_separator_summary.get("rows"),
                "unresolved_separator_hold_helpful_harmful": (
                    f"{exit_unresolved_separator_summary.get('hold_helpful_rows')}/"
                    f"{exit_unresolved_separator_summary.get('hold_harmful_rows')}"
                ),
                "unresolved_separator_best_clean_rule": exit_unresolved_separator_best_clean.get("rule"),
                "unresolved_separator_best_clean_wl": (
                    f"{exit_unresolved_separator_best_clean.get('helpful_hold_rows')}/"
                    f"{exit_unresolved_separator_best_clean.get('harmful_hold_rows')}"
                ),
                "unresolved_separator_best_clean_delta_cents": exit_unresolved_separator_best_clean.get("hold_delta_cents_selected"),
                "unresolved_separator_best_rounded_rule": exit_unresolved_separator_best_nice.get("rule"),
                "unresolved_separator_best_rounded_wl": (
                    f"{exit_unresolved_separator_best_nice.get('helpful_hold_rows')}/"
                    f"{exit_unresolved_separator_best_nice.get('harmful_hold_rows')}"
                ),
                "unresolved_separator_best_rounded_delta_cents": exit_unresolved_separator_best_nice.get("hold_delta_cents_selected"),
                "unresolved_separator_blockers": exit_unresolved_separator_best_nice.get("blockers"),
                "shallow_drawdown_watch_freeze_ts": (exit_shallow_drawdown_watch.get("state") or {}).get("freeze_ts_utc"),
                "shallow_drawdown_diag_best_policy": exit_shallow_drawdown_best_diag.get("policy"),
                "shallow_drawdown_diag_delta_cents": exit_shallow_drawdown_best_diag.get("delta_vs_current_cents"),
                "shallow_drawdown_diag_suppressed_wl": (
                    f"{exit_shallow_drawdown_best_diag.get('suppressed_helpful')}/"
                    f"{exit_shallow_drawdown_best_diag.get('suppressed_harmful')}"
                ),
                "shallow_drawdown_diag_loss_cost_cents": exit_shallow_drawdown_best_diag.get("loss_control_cost_cents"),
                "shallow_drawdown_strict_policy": exit_shallow_drawdown_best_strict.get("policy"),
                "shallow_drawdown_strict_settled": exit_shallow_drawdown_best_strict.get("settled"),
                "shallow_drawdown_strict_suppressed": exit_shallow_drawdown_best_strict.get("suppressed_exits"),
                "shallow_drawdown_strict_delta_cents": exit_shallow_drawdown_best_strict.get("delta_vs_current_cents"),
                "shallow_drawdown_strict_blockers": exit_shallow_drawdown_best_strict.get("blockers"),
                "shallow_harm_audit_base_selected_helpful_harmful": (
                    f"{exit_shallow_harm_summary.get('base_selected_rows')}/"
                    f"{exit_shallow_harm_summary.get('base_helpful')}/"
                    f"{exit_shallow_harm_summary.get('base_harmful')}"
                ),
                "shallow_harm_audit_best_clean_rule": exit_shallow_harm_best_clean.get("rule"),
                "shallow_harm_audit_best_clean_wl": (
                    f"{exit_shallow_harm_best_clean.get('helpful')}/"
                    f"{exit_shallow_harm_best_clean.get('harmful')}"
                ),
                "shallow_harm_audit_best_clean_delta_cents": exit_shallow_harm_best_clean.get("selected_delta_cents"),
                "shallow_duration_watch_freeze_ts": (exit_shallow_duration_watch.get("state") or {}).get("freeze_ts_utc"),
                "shallow_duration_diag_delta_cents": exit_shallow_duration_best_diag.get("delta_vs_current_cents"),
                "shallow_duration_diag_suppressed_wl": (
                    f"{exit_shallow_duration_best_diag.get('suppressed_helpful')}/"
                    f"{exit_shallow_duration_best_diag.get('suppressed_harmful')}"
                ),
                "shallow_duration_diag_loss_cost_cents": exit_shallow_duration_best_diag.get("loss_control_cost_cents"),
                "shallow_duration_strict_settled": exit_shallow_duration_best_strict.get("settled"),
                "shallow_duration_strict_suppressed": exit_shallow_duration_best_strict.get("suppressed_exits"),
                "shallow_duration_strict_delta_cents": exit_shallow_duration_best_strict.get("delta_vs_current_cents"),
                "shallow_duration_strict_blockers": exit_shallow_duration_best_strict.get("blockers"),
                "clip_separator_known_helpful_harmful_unknown": (
                    f"{exit_clip_separator_summary.get('hold_helpful_rows')}/"
                    f"{exit_clip_separator_summary.get('hold_harmful_rows')}/"
                    f"{exit_clip_separator_summary.get('hold_unknown_rows')}"
                ),
                "clip_separator_best_rule": exit_clip_separator_best.get("rule"),
                "clip_separator_best_helpful_harmful_unknown": (
                    f"{exit_clip_separator_best.get('helpful_rows')}/"
                    f"{exit_clip_separator_best.get('harmful_rows')}/"
                    f"{exit_clip_separator_best.get('unknown_rows')}"
                ),
                "clip_separator_best_known_delta_cents": exit_clip_separator_best.get("known_hold_delta_cents"),
                "clip_separator_best_failure_classes": exit_clip_separator_best.get("failure_class_counts"),
                "clip_separator_watch_freeze_ts": exit_clip_separator_watch_state.get("freeze_ts_utc"),
                "clip_separator_watch_post_freeze_rows": exit_clip_separator_watch.get("post_freeze_matched_unchanged_rows"),
                "clip_separator_watch_selected_rows": exit_clip_separator_watch_summary.get("rows"),
                "clip_separator_watch_helpful_harmful_unknown": (
                    f"{exit_clip_separator_watch_summary.get('helpful_rows')}/"
                    f"{exit_clip_separator_watch_summary.get('harmful_rows')}/"
                    f"{exit_clip_separator_watch_summary.get('unknown_rows')}"
                ),
                "clip_separator_watch_blockers": exit_clip_separator_watch_summary.get("blockers"),
                "matched_unchanged_guard_freeze_ts": matched_guard_state.get("freeze_ts_utc"),
                "matched_unchanged_guard_diagnostic_selected": matched_guard_diag.get("selected_rows"),
                "matched_unchanged_guard_diagnostic_helpful_harmful": (
                    f"{matched_guard_diag.get('helpful_rows')}/"
                    f"{matched_guard_diag.get('harmful_rows')}"
                ),
                "matched_unchanged_guard_diagnostic_delta_cents": matched_guard_diag.get("selected_hold_delta_cents"),
                "matched_unchanged_guard_post_rows": matched_guard_post.get("rows"),
                "matched_unchanged_guard_post_selected": matched_guard_post.get("selected_rows"),
                "matched_unchanged_guard_post_delta_cents": matched_guard_post.get("delta_vs_current_cents"),
                "matched_unchanged_guard_post_blockers": matched_guard_post.get("blockers"),
                "true_loser_hold_risk_rows": true_loser_hold_summary.get("true_loser_rows"),
                "true_loser_hold_delta_cents": true_loser_hold_true.get("hold_delta_cents"),
                "clipped_winner_hold_rows": true_loser_hold_summary.get("clipped_winner_rows"),
                "clipped_winner_hold_delta_cents": true_loser_hold_clip.get("hold_delta_cents"),
                "true_loser_avoid_broad_hold_tags": [row.get("tag") for row in true_loser_avoid_tags[:8]],
                "false_hold_bridge_strict_harmful_suppressions": exit_false_hold_guardrail_bridge.get("strict_harmful_suppressions"),
                "false_hold_bridge_strict_net_harm_cents": exit_false_hold_guardrail_bridge.get("strict_net_harm_cents"),
                "false_hold_bridge_top_guardrail_tags": false_hold_bridge_summary.get("top_guardrail_tags"),
                "false_hold_rule_overlap_generated_at_utc": exit_false_hold_rule_overlap.get("generated_at_utc"),
                "false_hold_rule_overlap_rows": exit_false_hold_rule_overlap.get("rows"),
                "false_hold_rule_overlap_interpretation": exit_false_hold_rule_overlap.get("interpretation"),
                "exit_loss_guard_mechanism_generated_at_utc": exit_loss_guard_mechanism.get("generated_at_utc"),
                "exit_loss_guard_mechanism_lanes": exit_loss_guard_mechanism.get("lanes"),
                "exit_loss_guard_mechanism_interpretation": exit_loss_guard_mechanism.get("interpretation"),
                "exit_loss_guard_threshold_margin_stress_generated_at_utc": exit_loss_guard_threshold_margin_stress.get("generated_at_utc"),
                "exit_loss_guard_threshold_margin_stress_lanes": exit_loss_guard_threshold_margin_stress.get("lanes"),
                "exit_loss_guard_threshold_margin_stress_interpretation": exit_loss_guard_threshold_margin_stress.get("interpretation"),
                "exit_loss_guard_path_risk_generated_at_utc": exit_loss_guard_path_risk.get("generated_at_utc"),
                "exit_loss_guard_path_risk_v1": loss_guard_path_risk_v1,
                "exit_loss_guard_path_risk_v3": loss_guard_path_risk_v3,
                "exit_loss_guard_path_risk_interpretation": exit_loss_guard_path_risk.get("interpretation"),
                "clip_separator_replay_diagnostic_current_wl": (
                    f"{exit_clip_separator_replay_diag.get('current_wins')}/"
                    f"{exit_clip_separator_replay_diag.get('current_losses')}"
                ),
                "clip_separator_replay_diagnostic_candidate_wl": (
                    f"{exit_clip_separator_replay_diag.get('candidate_wins')}/"
                    f"{exit_clip_separator_replay_diag.get('candidate_losses')}"
                ),
                "clip_separator_replay_diagnostic_delta_cents": exit_clip_separator_replay_diag.get("delta_cents"),
                "clip_separator_replay_diagnostic_loss_reduction": exit_clip_separator_replay_diag.get("loss_count_reduction"),
                "clip_separator_replay_diagnostic_suppressed_losers": exit_clip_separator_replay_diag.get("suppressed_losers"),
                "clip_separator_replay_post_rows": exit_clip_separator_replay_post.get("rows"),
                "clip_separator_replay_post_blockers": exit_clip_separator_replay_post.get("blockers"),
                "side_geometry_diagnostic_best": reduce_geometry_best.get("policy"),
                "side_geometry_diagnostic_delta_cents": reduce_geometry_best.get("delta_vs_current_cents"),
                "side_geometry_diagnostic_suppressed_wl": f"{reduce_geometry_best.get('suppressed_winners')}/{reduce_geometry_best.get('suppressed_losers')}",
                "side_geometry_frozen_settled": frozen_reduce_geometry_summary.get("settled"),
                "side_geometry_frozen_suppressed": frozen_reduce_geometry_summary.get("suppressed"),
                "side_geometry_frozen_delta_cents": frozen_reduce_geometry_summary.get("delta_vs_current_cents"),
                "post_geometry_freeze_base_delta_cents": frozen_reduce_geometry_base.get("delta_vs_current_cents"),
                "post_geometry_freeze_base_suppressed_wl": f"{frozen_reduce_geometry_base.get('suppressed_winners')}/{frozen_reduce_geometry_base.get('suppressed_losers')}",
                "post_geometry_freeze_side_delta_cents": frozen_reduce_geometry_side.get("delta_vs_current_cents"),
                "side_geometry_opportunity_probability_reduce_rows": reduce_geometry_opportunity_summary.get("probability_reduce_rows"),
                "side_geometry_opportunity_base_candidates": reduce_geometry_opportunity_summary.get("base_p_hold_candidates"),
                "side_geometry_opportunity_would_suppress_rows": reduce_geometry_opportunity_summary.get("geometry_would_suppress_rows"),
                "side_geometry_opportunity_rejected_base_candidates": reduce_geometry_opportunity_summary.get("geometry_rejected_base_candidates"),
                "side_geometry_opportunity_rejected_base_delta_cents": reduce_geometry_opportunity_summary.get("geometry_rejected_base_delta_cents"),
                "side_geometry_opportunity_blockers": reduce_geometry_opportunity_summary.get("blockers"),
                "relaxed_geometry_freeze_ts": (reduce_geometry_relaxed_watch.get("freeze") or {}).get("freeze_ts_utc"),
                "relaxed_geometry_diagnostic_best": reduce_geometry_relaxed_diag.get("policy"),
                "relaxed_geometry_diagnostic_delta_cents": reduce_geometry_relaxed_diag.get("delta_vs_current_cents"),
                "relaxed_geometry_diagnostic_suppressed_wl": f"{reduce_geometry_relaxed_diag.get('suppressed_winners')}/{reduce_geometry_relaxed_diag.get('suppressed_losers')}",
                "relaxed_geometry_strict_settled": reduce_geometry_relaxed_summary.get("settled"),
                "relaxed_geometry_strict_suppressed": reduce_geometry_relaxed_summary.get("suppressed"),
                "relaxed_geometry_strict_delta_cents": reduce_geometry_relaxed_summary.get("delta_vs_current_cents"),
                "relaxed_geometry_strict_blockers": reduce_geometry_relaxed_watch.get("blockers"),
            },
            "next": "Keep reduce, drift-guard, book-gap, loss-guarded book-gap v1/v2/v3, entry-depth, observable loss-control, shallow-duration, relaxed geometry, and dual-exit freezes running; judge each only on rows after its own freeze timestamp. The shallow-duration branch needs post-birth rows before it can matter.",
        },
        {
            "lane": "fv_calibration",
            "decision": "pursue_forward_as_overlay",
            "candidate": "hybrid_confidence_shrink",
            "why": "Hybrid shrink improves the fixed-row discovery calibration more than noise_shrink_light while preserving fixed entry selection.",
            "evidence": {
                "diagnostic_best": shrink_diag.get("overlay"),
                "diagnostic_brier_delta": shrink_diag.get("brier_delta_vs_raw"),
                "diagnostic_logloss_delta": shrink_diag.get("logloss_delta_vs_raw"),
                "hybrid_diagnostic_best": hybrid_diag.get("overlay"),
                "hybrid_diagnostic_brier_delta": hybrid_diag.get("brier_delta_vs_raw"),
                "hybrid_diagnostic_logloss_delta": hybrid_diag.get("logloss_delta_vs_raw"),
                "hybrid_forward_best": hybrid_forward.get("overlay"),
                "hybrid_forward_settled": hybrid_forward.get("settled"),
                "forward_fixed_brier_delta": raw_noise.get("brier_delta_vs_raw"),
                "forward_fixed_logloss_delta": raw_noise.get("logloss_delta_vs_raw"),
                "forward_fixed_net_cents": raw_noise.get("net_cents_after_entry_fee"),
            },
            "next": "Let the frozen hybrid rows accumulate; do not use it as an entry selector or promotion evidence until it has forward rows.",
        },
        {
            "lane": "hybrid_veto_repair",
            "decision": "monitor_as_warning_feature",
            "candidate": "target_hybrid_veto_repair",
            "why": "Hybrid-veto identifies a real loss cluster, but the best repaired diagnostic surface still loses money and the post-freeze stream is currently negative and under sample.",
            "evidence": {
                "diagnostic_best": target_veto_diag_best.get("candidate"),
                "diagnostic_settled": target_veto_diag_summary.get("settled"),
                "diagnostic_coverage": target_veto_diag_summary.get("coverage_pct"),
                "diagnostic_net_cents": target_veto_diag_summary.get("net_cents"),
                "diagnostic_delta_cents": target_veto_diag_best.get("delta_vs_target_cents"),
                "diagnostic_veto_cluster_settled": target_veto_diag_cluster.get("settled"),
                "diagnostic_veto_cluster_net_cents": target_veto_diag_cluster.get("net_cents"),
                "post_freeze_best": target_veto_post_best.get("candidate"),
                "post_freeze_settled": target_veto_post_summary.get("settled"),
                "post_freeze_coverage": target_veto_post_summary.get("coverage_pct"),
                "post_freeze_net_cents": target_veto_post_summary.get("net_cents"),
                "post_freeze_veto_cluster_settled": target_veto_post_cluster.get("settled"),
                "post_freeze_veto_cluster_net_cents": target_veto_post_cluster.get("net_cents"),
                "blockers": target_veto_post_best.get("blockers"),
            },
            "next": "Keep hybrid-veto as a warning and coverage-repair component; only freeze a combined stack after it is positive, broad, and integrity-clean on forward rows.",
        },
        {
            "lane": "boundary_clock_entry",
            "decision": "monitor_not_promote",
            "candidate": "boundary_clock_repair_entry / boundary_clock_fv_entry_bridge",
            "why": "Boundary-clock repair remains broad, but the refreshed base entry lane is negative and the slightly positive FV bridge is still source-stressed with too little full-loss cushion. The feature-gate live drilldown shows theory wins are being clipped by live exit/state churn, so entry-threshold work is secondary to exit/state alignment. The current ask-floor tradeoff autopsy says the clean ask65 core is source-clean but too narrow, raw05 gets coverage from cheap rejected-actionable tail rows with many losses and a few outsized wins, and raw03's extra broad-coverage rows are rejected-actionable and net negative. The same-market high-ask displacement guard improves source share and PnL by replacing obvious cheap-side conflicts, but still cannot solve coverage or live-baseline gates; the guarded coverage-repair scan now shows coverage can be forced over 75% only with post-hoc rejected-actionable relaxations that keep source/live blockers open. The refreshed promotion-gap audit shows post-feature-freeze rows are no longer a zero-row wait, but the broad lane still misses coverage, source quality, cushion, and refreshed live-baseline gates.",
            "evidence": {
                "entry_settled": boundary_clock_candidate.get("settled"),
                "entry_coverage": boundary_clock_candidate.get("coverage_pct"),
                "entry_net_cents": boundary_clock_candidate.get("net_cents"),
                "entry_blockers": boundary_clock_entry.get("blockers"),
                "fv_bridge_settled": boundary_clock_bridge_candidate.get("settled"),
                "fv_bridge_coverage": boundary_clock_bridge_candidate.get("coverage_pct"),
                "fv_bridge_net_cents": boundary_clock_bridge_candidate.get("net_cents"),
                "fv_bridge_blockers": boundary_clock_bridge.get("blockers"),
                "runway_ready": boundary_clock_runway.get("ready_for_consideration"),
                "diagnostic_entry_robustness_pass": boundary_clock_runway.get("diagnostic_entry_robustness_pass"),
                "diagnostic_fv_robustness_pass": boundary_clock_runway.get("diagnostic_fv_robustness_pass"),
                "entry_reconstructed_share": boundary_clock_entry_stress.get("reconstructed_share"),
                "entry_full_loss_cushion": boundary_clock_entry_stress.get("full_loss_cushion_estimate"),
                "entry_clean_rows_needed_for_gate": boundary_clock_entry_stress.get("future_clean_rows_for_sample_source_gate"),
                "entry_source_stress_blockers": boundary_clock_entry_stress.get("blockers"),
                "fv_bridge_reconstructed_share": boundary_clock_bridge_stress.get("reconstructed_share"),
                "fv_bridge_full_loss_cushion": boundary_clock_bridge_stress.get("full_loss_cushion_estimate"),
                "fv_bridge_clean_rows_needed_for_gate": boundary_clock_bridge_stress.get("future_clean_rows_for_sample_source_gate"),
                "fv_bridge_source_stress_blockers": boundary_clock_bridge_stress.get("blockers"),
                "approved_frontier_entry_best": boundary_clock_entry_frontier_best.get("candidate"),
                "approved_frontier_entry_settled": boundary_clock_entry_frontier_summary.get("settled"),
                "approved_frontier_entry_net_cents": boundary_clock_entry_frontier_summary.get("net_cents"),
                "approved_frontier_entry_blockers": boundary_clock_entry_frontier_best.get("blockers"),
                "approved_frontier_bridge_best": boundary_clock_bridge_frontier_best.get("candidate"),
                "approved_frontier_bridge_settled": boundary_clock_bridge_frontier_summary.get("settled"),
                "approved_frontier_bridge_net_cents": boundary_clock_bridge_frontier_summary.get("net_cents"),
                "approved_frontier_bridge_blockers": boundary_clock_bridge_frontier_best.get("blockers"),
                "feature_gate_freeze_ts": (boundary_clock_feature_gate.get("state") or {}).get("freeze_ts_utc"),
                "feature_gate_diagnostic_entry": feature_gate_diag_entry_best.get("candidate"),
                "feature_gate_diagnostic_entry_settled": feature_gate_diag_entry_summary.get("settled"),
                "feature_gate_diagnostic_entry_coverage": feature_gate_diag_entry_summary.get("coverage_pct"),
                "feature_gate_diagnostic_entry_net_cents": feature_gate_diag_entry_summary.get("net_cents"),
                "feature_gate_diagnostic_entry_reconstructed_share": feature_gate_diag_entry_best.get("reconstructed_share"),
                "feature_gate_diagnostic_entry_blockers": feature_gate_diag_entry_best.get("blockers"),
                "feature_gate_diagnostic_bridge": feature_gate_diag_bridge_best.get("candidate"),
                "feature_gate_diagnostic_bridge_settled": feature_gate_diag_bridge_summary.get("settled"),
                "feature_gate_diagnostic_bridge_coverage": feature_gate_diag_bridge_summary.get("coverage_pct"),
                "feature_gate_diagnostic_bridge_net_cents": feature_gate_diag_bridge_summary.get("net_cents"),
                "feature_gate_diagnostic_bridge_reconstructed_share": feature_gate_diag_bridge_best.get("reconstructed_share"),
                "feature_gate_diagnostic_bridge_blockers": feature_gate_diag_bridge_best.get("blockers"),
                "feature_gate_post_entry_settled": feature_gate_post_entry_summary.get("settled"),
                "feature_gate_post_entry_net_cents": feature_gate_post_entry_summary.get("net_cents"),
                "feature_gate_post_entry_blockers": feature_gate_post_entry_best.get("blockers"),
                "feature_gate_promotion_gap_live_net_cents": feature_gate_promotion_gap.get("live_net_cents"),
                "feature_gate_promotion_gap_broad": feature_gate_promotion_broad,
                "feature_gate_promotion_gap_interpretation": feature_gate_promotion_gap.get("promotion_gap"),
                "feature_gate_post_bridge_settled": feature_gate_post_bridge_summary.get("settled"),
                "feature_gate_post_bridge_net_cents": feature_gate_post_bridge_summary.get("net_cents"),
                "feature_gate_post_bridge_blockers": feature_gate_post_bridge_best.get("blockers"),
                "feature_gate_near_best_candidate": feature_gate_near_best.get("candidate"),
                "feature_gate_near_settled": feature_gate_near_best.get("settled"),
                "feature_gate_near_pending": feature_gate_near_best.get("pending"),
                "feature_gate_near_pending_approved": feature_gate_near_best.get("pending_approved"),
                "feature_gate_near_coverage": feature_gate_near_best.get("coverage_pct"),
                "feature_gate_near_net_cents": feature_gate_near_best.get("net_cents"),
                "feature_gate_near_reconstructed_share": feature_gate_near_best.get("reconstructed_share"),
                "feature_gate_near_coverage_entries_needed": feature_gate_near_best.get("coverage_entries_needed"),
                "feature_gate_near_settled_rows_needed": feature_gate_near_best.get("settled_rows_needed"),
                "feature_gate_near_clean_rows_needed": feature_gate_near_best.get("clean_rows_needed_for_source"),
                "feature_gate_near_cushion_cents_needed": feature_gate_near_best.get("net_cents_needed_for_cushion3"),
                "feature_gate_near_avg_future_net_needed_cushion3": feature_gate_near_best.get("avg_future_net_needed_for_cushion3"),
                "feature_gate_near_gap_candidate": feature_gate_near_promotion_denominator_gap.get("candidate"),
                "feature_gate_near_gap_denominator": feature_gate_near_promotion_denominator_gap.get("future_denominator"),
                "feature_gate_near_gap_selected_entries": feature_gate_near_promotion_denominator_gap.get("selected_entries"),
                "feature_gate_near_gap_settled_selected": feature_gate_near_promotion_denominator_gap.get("settled_selected"),
                "feature_gate_near_gap_pending_selected": feature_gate_near_gap_pending.get("rows"),
                "feature_gate_near_gap_pending_approved": (feature_gate_near_gap_pending.get("source_counts") or {}).get("approved_entry"),
                "feature_gate_near_gap_selected_net_cents": feature_gate_near_gap_selected.get("net_cents"),
                "feature_gate_near_gap_reconstructed_share": feature_gate_near_gap_selected.get("reconstructed_share"),
                "feature_gate_near_gap_coverage_entries_needed": feature_gate_near_promotion_denominator_gap.get("coverage_entries_needed"),
                "feature_gate_near_gap_approved_rows_needed_for_source": feature_gate_near_promotion_denominator_gap.get("approved_selected_rows_needed_for_source_gate"),
                "feature_gate_near_gap_cushion_cents_needed": feature_gate_near_promotion_denominator_gap.get("cushion_cents_needed"),
                "feature_gate_near_gap_omitted_source_counts": feature_gate_near_gap_omitted.get("source_counts"),
                "feature_gate_near_gap_omitted_net_cents": feature_gate_near_gap_omitted.get("net_cents"),
                "feature_gate_near_gap_omitted_fail_reasons": feature_gate_near_promotion_denominator_gap.get("omitted_fail_reason_counts"),
                "feature_gate_pending_resolution_resolved_rows": feature_gate_pending_resolution.get("pending_resolved_in_market_results"),
                "feature_gate_pending_resolution_projected_settled": feature_gate_pending_resolution.get("projected_settled_if_market_results_linked"),
                "feature_gate_pending_resolution_projected_net_cents": feature_gate_pending_resolution.get("projected_net_cents_if_market_results_linked"),
                "feature_gate_pending_resolution_cushion_cents_needed": feature_gate_pending_resolution.get("projected_cushion_cents_needed"),
                "feature_gate_pending_resolution_source_gate": feature_gate_pending_resolution.get("source_gate_unchanged"),
                "feature_gate_pending_resolution_coverage_entries_needed": feature_gate_pending_resolution.get("coverage_entries_needed_unchanged"),
                "feature_gate_pending_resolution_live_pnl_dollars": feature_gate_pending_resolution.get("pending_recent_live_pnl_dollars"),
                "feature_gate_outcome_linkage_best_candidate": feature_gate_linkage_best.get("candidate"),
                "feature_gate_outcome_linkage_best_settled": feature_gate_linkage_best_summary.get("settled"),
                "feature_gate_outcome_linkage_best_net_cents": feature_gate_linkage_best_summary.get("net_cents"),
                "feature_gate_outcome_linkage_best_coverage_pct": feature_gate_linkage_best_summary.get("coverage_pct"),
                "feature_gate_outcome_linkage_best_reconstructed_share": feature_gate_linkage_best.get("reconstructed_share"),
                "feature_gate_outcome_linkage_best_blockers": feature_gate_linkage_best.get("linked_blockers"),
                "feature_gate_outcome_linkage_live_ready_rows": len([row for row in feature_gate_linkage_rows if not row.get("linked_blockers")]),
                "feature_gate_linked_source_runway_best_candidate": feature_gate_source_runway_best.get("candidate"),
                "feature_gate_linked_source_runway_clean_rows_needed": feature_gate_source_runway_best.get("approved_future_rows_needed_for_source_gate"),
                "feature_gate_linked_source_runway_approved_net_cents": feature_gate_source_runway_approved.get("net_cents"),
                "feature_gate_linked_source_runway_approved_wl": (
                    f"{feature_gate_source_runway_approved.get('wins')}/{feature_gate_source_runway_approved.get('losses')}"
                ),
                "feature_gate_linked_source_runway_rejected_net_cents": feature_gate_source_runway_rejected.get("net_cents"),
                "feature_gate_linked_source_runway_rejected_wl": (
                    f"{feature_gate_source_runway_rejected.get('wins')}/{feature_gate_source_runway_rejected.get('losses')}"
                ),
                "feature_gate_live_alignment_raw03_theory_net_cents": feature_gate_live_alignment_raw03_summary.get(
                    "theory_net_cents"
                ),
                "feature_gate_live_alignment_raw03_live_traded_markets": feature_gate_live_alignment_raw03_summary.get(
                    "live_traded_markets"
                ),
                "feature_gate_live_alignment_raw03_no_live_trade_markets": feature_gate_live_alignment_raw03_summary.get(
                    "no_live_trade_markets"
                ),
                "feature_gate_live_alignment_raw03_live_total_cents": feature_gate_live_alignment_raw03_summary.get(
                    "live_net_cents_total"
                ),
                "feature_gate_live_alignment_raw03_live_per_contract_market_sum_cents": (
                    feature_gate_live_alignment_raw03_summary.get("live_net_cents_per_contract_market_sum")
                ),
                "feature_gate_live_alignment_raw03_selected_side_per_contract_market_sum_cents": (
                    feature_gate_live_alignment_raw03_summary.get("selected_side_live_net_cents_per_contract_market_sum")
                ),
                "feature_gate_live_alignment_raw03_tag_counts": feature_gate_live_alignment_raw03_summary.get(
                    "tag_counts"
                ),
                "feature_gate_live_exit_mismatch_markets": len(feature_gate_exit_drilldown_markets),
                "feature_gate_live_exit_mismatch_theory_net_cents": feature_gate_exit_drilldown_theory_net,
                "feature_gate_live_exit_mismatch_live_selected_net_cents": feature_gate_exit_drilldown_live_selected_net,
                "feature_gate_live_exit_mismatch_class_counts": feature_gate_exit_drilldown_class_counts,
                "feature_gate_live_exit_mismatch_reason_counts": feature_gate_exit_drilldown_reason_counts,
                "feature_gate_near_loss_tags": feature_gate_near_best.get("loss_tag_counts"),
                "feature_gate_near_missing_gates": feature_gate_near_best.get("missing_gates"),
                "feature_gate_near_exit_failure_classes": feature_gate_near_exit_failure_classes,
                "feature_gate_near_exit_loss_sources": feature_gate_near_exit_loss_sources,
                "feature_gate_post_best_delta_vs_live_cents": feature_gate_runway_post.get("delta_vs_live_cents"),
                "feature_gate_post_clean_rows_needed_for_all_gates": feature_gate_runway_post.get("future_clean_selected_needed_for_all_gates"),
                "feature_gate_post_avg_future_net_needed_cushion3": feature_gate_runway_post.get("avg_future_net_needed_cushion3_cents"),
                "feature_gate_post_structural_failure_modes": feature_gate_failure_post.get("structural_failure_modes"),
                "feature_gate_diagnostic_row_failure_counts": feature_gate_failure_diag.get("selected_row_failure_counts"),
                "feature_gate_post_loss_analog": feature_gate_loss_post.get("summary_scores"),
                "feature_gate_diagnostic_loss_analog": feature_gate_loss_diag.get("summary_scores"),
                "feature_gate_post_entry_omission_counts": feature_gate_row_entry_best.get("omission_reason_counts"),
                "feature_gate_post_bridge_omission_counts": feature_gate_row_bridge_best.get("omission_reason_counts"),
                "feature_gate_coverage_recovery_strict_rule": feature_gate_recovery_entry.get("strict_rule"),
                "feature_gate_coverage_recovery_strict_coverage": feature_gate_recovery_entry_strict.get("coverage_pct"),
                "feature_gate_coverage_recovery_strict_net_cents": feature_gate_recovery_entry_strict.get("net_cents"),
                "feature_gate_coverage_recovery_strict_reconstructed_share": feature_gate_recovery_entry.get("strict_reconstructed_share"),
                "feature_gate_coverage_recovery_broader_rule": feature_gate_recovery_entry_broad.get("rule"),
                "feature_gate_coverage_recovery_broader_coverage": feature_gate_recovery_entry_broad_summary.get("coverage_pct"),
                "feature_gate_coverage_recovery_broader_net_cents": feature_gate_recovery_entry_broad_summary.get("net_cents"),
                "feature_gate_coverage_recovery_broader_reconstructed_share": feature_gate_recovery_entry_broad.get("reconstructed_share"),
                "feature_gate_coverage_recovery_broader_added_markets": feature_gate_recovery_entry_broad_comparison.get("added_markets"),
                "feature_gate_coverage_recovery_broader_added_net_cents": feature_gate_recovery_entry_broad_comparison.get("added_net_cents"),
                "feature_gate_coverage_recovery_rows_needed_for_75pct": feature_gate_recovery_entry_broad_comparison.get("rows_needed_for_75pct_coverage"),
                "feature_gate_coverage_recovery_clean_rows_needed_for_source": feature_gate_recovery_entry_broad_comparison.get("clean_rows_needed_for_source_gate"),
                "feature_gate_source_denominator_entry_best_rule": feature_gate_source_entry_best.get("rule"),
                "feature_gate_source_denominator_approved_source_coverage": feature_gate_source_entry_best.get("approved_observed_coverage_pct"),
                "feature_gate_source_denominator_reconstructed_source_coverage": feature_gate_source_entry_best.get("reconstructed_observed_coverage_pct"),
                "feature_gate_source_denominator_selected_reconstructed_share": feature_gate_source_entry_best.get("selected_reconstructed_share"),
                "feature_gate_source_denominator_omitted_net_by_source": feature_gate_source_entry_best.get("omitted_source_net_cents"),
                "feature_gate_coverage_source_frontier_entry_best_rule": feature_gate_frontier_entry_best.get("rule"),
                "feature_gate_coverage_source_frontier_entry_coverage": feature_gate_frontier_entry_summary.get("coverage_pct"),
                "feature_gate_coverage_source_frontier_entry_net_cents": feature_gate_frontier_entry_summary.get("net_cents"),
                "feature_gate_coverage_source_frontier_entry_reconstructed_share": feature_gate_frontier_entry_best.get("reconstructed_share"),
                "feature_gate_coverage_source_frontier_clean_broad_positive_count": len(feature_gate_frontier_entry.get("clean_broad_positive") or []),
                "feature_gate_source_feasibility_denominator": feature_gate_feasibility_entry.get("future_denominator"),
                "feature_gate_source_feasibility_approved_markets": feature_gate_feasibility_entry.get("approved_markets_available"),
                "feature_gate_source_feasibility_75pct_possible": feature_gate_feasibility_entry_75.get("source_gate_feasible"),
                "feature_gate_source_feasibility_min_recon_share_for_75pct": feature_gate_feasibility_entry_75.get("min_reconstructed_share_needed"),
                "feature_gate_source_feasibility_max_clean_coverage": feature_gate_feasibility_entry_75.get("max_source_clean_coverage_pct"),
                "feature_gate_frontier_runway_clean_rows_for_coverage": feature_gate_frontier_runway_entry_runway.get("clean_rows_needed_for_coverage_gate"),
                "feature_gate_frontier_runway_clean_rows_for_source": feature_gate_frontier_runway_entry_runway.get("clean_rows_needed_for_source_gate"),
                "feature_gate_frontier_runway_settled_rows_for_sample": feature_gate_frontier_runway_entry_runway.get("settled_rows_needed_for_sample_gate"),
                "feature_gate_frontier_runway_net_cents_for_cushion": feature_gate_frontier_runway_entry_runway.get("net_cents_needed"),
                "feature_gate_frontier_mechanism_entry_selected": feature_gate_frontier_mechanism_entry_summary.get("entries"),
                "feature_gate_frontier_mechanism_entry_denominator": feature_gate_frontier_mechanism_entry.get("future_denominator"),
                "feature_gate_frontier_mechanism_entry_net_cents": feature_gate_frontier_mechanism_entry_summary.get("net_cents"),
                "feature_gate_frontier_mechanism_gained_net_cents": feature_gate_frontier_mechanism_gained.get("net_cents"),
                "feature_gate_frontier_mechanism_omitted_net_cents": feature_gate_frontier_mechanism_omitted.get("net_cents"),
                "feature_gate_frontier_mechanism_omitted_fail_reasons": feature_gate_frontier_mechanism_entry.get("omitted_fail_reason_counts"),
                "feature_gate_outlier_frontier_rule": feature_gate_outlier_entry.get("frontier_rule"),
                "feature_gate_outlier_approved_only_net_cents": feature_gate_outlier_entry.get("approved_only_net_cents"),
                "feature_gate_outlier_reconstructed_only_net_cents": feature_gate_outlier_entry.get("reconstructed_only_net_cents"),
                "feature_gate_outlier_top_win_net_cents": feature_gate_outlier_entry.get("top_win_net_cents"),
                "feature_gate_outlier_net_without_top_win_cents": feature_gate_outlier_entry.get("net_without_top_win_cents"),
                "feature_gate_outlier_stress_blockers": feature_gate_outlier_entry.get("stress_blockers"),
                "feature_gate_clean_broad_freeze_ts": (boundary_clock_feature_gate_clean_broad_frontier.get("state") or {}).get("freeze_ts_utc"),
                "feature_gate_clean_broad_rule": (boundary_clock_feature_gate_clean_broad_frontier.get("state") or {}).get("candidate"),
                "feature_gate_clean_broad_diagnostic_settled": feature_gate_clean_broad_diag_entry_summary.get("settled"),
                "feature_gate_clean_broad_diagnostic_coverage": feature_gate_clean_broad_diag_entry_summary.get("coverage_pct"),
                "feature_gate_clean_broad_diagnostic_net_cents": feature_gate_clean_broad_diag_entry_summary.get("net_cents"),
                "feature_gate_clean_broad_diagnostic_reconstructed_share": feature_gate_clean_broad_diag_entry.get("reconstructed_share"),
                "feature_gate_clean_broad_post_settled": feature_gate_clean_broad_post_entry_summary.get("settled"),
                "feature_gate_clean_broad_post_coverage": feature_gate_clean_broad_post_entry_summary.get("coverage_pct"),
                "feature_gate_clean_broad_post_net_cents": feature_gate_clean_broad_post_entry_summary.get("net_cents"),
                "feature_gate_clean_broad_post_blockers": feature_gate_clean_broad_post_entry.get("blockers"),
                "feature_gate_soft_frontier_freeze_ts": (boundary_clock_feature_gate_soft_frontier.get("state") or {}).get("freeze_ts_utc"),
                "feature_gate_soft_frontier_diagnostic_best": feature_gate_soft_diag_entry_best.get("candidate"),
                "feature_gate_soft_frontier_diagnostic_settled": feature_gate_soft_diag_entry_summary.get("settled"),
                "feature_gate_soft_frontier_diagnostic_coverage": feature_gate_soft_diag_entry_summary.get("coverage_pct"),
                "feature_gate_soft_frontier_diagnostic_net_cents": feature_gate_soft_diag_entry_summary.get("net_cents"),
                "feature_gate_soft_frontier_diagnostic_reconstructed_share": feature_gate_soft_diag_entry_best.get("reconstructed_share"),
                "feature_gate_soft_frontier_post_birth_settled": feature_gate_soft_post_entry_summary.get("settled"),
                "feature_gate_soft_frontier_post_birth_net_cents": feature_gate_soft_post_entry_summary.get("net_cents"),
                "feature_gate_soft_frontier_post_birth_blockers": feature_gate_soft_post_entry_best.get("blockers"),
                "soft_frontier_failure_drilldown_rule": soft_frontier_failure_entry.get("rule"),
                "soft_frontier_failure_drilldown_settled": soft_frontier_failure_entry_summary.get("settled"),
                "soft_frontier_failure_drilldown_coverage": soft_frontier_failure_entry_summary.get("coverage_pct"),
                "soft_frontier_failure_drilldown_net_cents": soft_frontier_failure_entry_summary.get("net_cents"),
                "soft_frontier_failure_drilldown_loss_tags": soft_frontier_failure_entry.get("loss_tag_counts"),
                "soft_frontier_failure_drilldown_exit_delta_vs_hold_cents": soft_frontier_failure_entry.get("loss_exit_delta_vs_hold_cents"),
                "feature_gate_ask_floor_post_delta_cents": feature_gate_ask_floor_post_entry.get("delta_net_cents"),
                "feature_gate_ask_floor_post_switched_tags": feature_gate_ask_floor_post_entry.get("switched_failure_tag_counts"),
                "feature_gate_ask_floor_diagnostic_delta_cents": feature_gate_ask_floor_diag_entry.get("delta_net_cents"),
                "feature_gate_ask_floor_tradeoff_generated_at_utc": feature_gate_ask_floor_tradeoff_autopsy.get("generated_at_utc"),
                "feature_gate_ask_floor_tradeoff_lanes": feature_gate_ask_floor_tradeoff_autopsy.get("lanes"),
                "feature_gate_ask_floor_tradeoff_interpretation": feature_gate_ask_floor_tradeoff_autopsy.get("interpretation"),
                "feature_gate_side_displacement_guard_generated_at_utc": feature_gate_side_displacement_guard.get("generated_at_utc"),
                "feature_gate_side_displacement_guard_lanes": feature_gate_side_displacement_guard.get("lanes"),
                "feature_gate_side_displacement_guard_interpretation": feature_gate_side_displacement_guard.get("interpretation"),
                "feature_gate_guarded_coverage_repair_generated_at_utc": feature_gate_guarded_coverage_repair_scan.get("generated_at_utc"),
                "feature_gate_guarded_coverage_repair_lanes": feature_gate_guarded_coverage_repair_scan.get("lanes"),
                "feature_gate_guarded_coverage_repair_interpretation": feature_gate_guarded_coverage_repair_scan.get("interpretation"),
                "feature_gate_continuous_penalty_freeze_ts": (boundary_clock_feature_gate_continuous_penalty.get("state") or {}).get("freeze_ts_utc"),
                "feature_gate_continuous_penalty_diagnostic_best": feature_gate_penalty_diag_entry_best.get("candidate"),
                "feature_gate_continuous_penalty_diagnostic_settled": feature_gate_penalty_diag_entry_summary.get("settled"),
                "feature_gate_continuous_penalty_diagnostic_coverage": feature_gate_penalty_diag_entry_summary.get("coverage_pct"),
                "feature_gate_continuous_penalty_diagnostic_net_cents": feature_gate_penalty_diag_entry_summary.get("net_cents"),
                "feature_gate_continuous_penalty_pre_birth_best": feature_gate_penalty_pre_entry_best.get("candidate"),
                "feature_gate_continuous_penalty_pre_birth_coverage": feature_gate_penalty_pre_entry_summary.get("coverage_pct"),
                "feature_gate_continuous_penalty_pre_birth_net_cents": feature_gate_penalty_pre_entry_summary.get("net_cents"),
                "feature_gate_continuous_penalty_pre_birth_reconstructed_share": feature_gate_penalty_pre_entry_best.get("reconstructed_share"),
                "feature_gate_continuous_penalty_post_birth_settled": feature_gate_penalty_post_entry_summary.get("settled"),
                "feature_gate_continuous_penalty_post_birth_net_cents": feature_gate_penalty_post_entry_summary.get("net_cents"),
                "feature_gate_continuous_penalty_post_birth_blockers": feature_gate_penalty_post_entry_best.get("blockers"),
                "feature_gate_continuous_penalty_stress_clean_rows_needed": feature_gate_penalty_stress_post_entry.get("future_clean_selected_needed_for_all_count_gates"),
                "feature_gate_continuous_penalty_stress_cushion_cents_needed": feature_gate_penalty_stress_post_entry.get("net_cents_needed_for_cushion3"),
                "feature_gate_continuous_penalty_stress_top_win_net_cents": feature_gate_penalty_stress_post_entry.get("top_win_net_cents"),
                "feature_gate_continuous_penalty_stress_blockers": feature_gate_penalty_stress_post_entry.get("stress_blockers"),
                "feature_gate_residual_loss_prototype_tags": boundary_clock_feature_gate_residual_loss.get("prototype_tag_counts"),
                "feature_gate_residual_loss_diagnostic_scores": feature_gate_residual_diag_entry.get("residual_summary"),
                "feature_gate_residual_loss_pre_birth_scores": feature_gate_residual_pre_entry.get("residual_summary"),
                "feature_gate_residual_loss_post_birth_scores": feature_gate_residual_post_entry.get("residual_summary"),
                "feature_gate_cheap_tail_quarantine_freeze_ts": (feature_gate_cheap_tail_quarantine.get("state") or {}).get("freeze_ts_utc"),
                "feature_gate_quarantine_diag_core": cheap_tail_diag_core.get("label"),
                "feature_gate_quarantine_diag_core_settled": cheap_tail_diag_core_summary.get("settled"),
                "feature_gate_quarantine_diag_core_coverage": cheap_tail_diag_core_summary.get("coverage_pct"),
                "feature_gate_quarantine_diag_core_net_cents": cheap_tail_diag_core_summary.get("net_cents"),
                "feature_gate_quarantine_diag_core_reconstructed_share": cheap_tail_diag_core.get("reconstructed_share"),
                "feature_gate_quarantine_diag_core_blockers": cheap_tail_diag_core.get("blockers"),
                "feature_gate_quarantine_diag_tail": cheap_tail_diag_tail.get("label"),
                "feature_gate_quarantine_diag_tail_settled": cheap_tail_diag_tail_summary.get("settled"),
                "feature_gate_quarantine_diag_tail_wl": f"{cheap_tail_diag_tail_summary.get('wins')}/{cheap_tail_diag_tail_summary.get('losses')}",
                "feature_gate_quarantine_diag_tail_net_cents": cheap_tail_diag_tail_summary.get("net_cents"),
                "feature_gate_quarantine_diag_tail_reconstructed_share": cheap_tail_diag_tail.get("reconstructed_share"),
                "feature_gate_quarantine_diag_tail_net_without_top_win_cents": cheap_tail_diag_tail.get("net_without_top_win_cents"),
                "feature_gate_quarantine_diag_tail_blockers": cheap_tail_diag_tail.get("blockers"),
                "feature_gate_quarantine_post_core_settled": cheap_tail_post_core_summary.get("settled"),
                "feature_gate_quarantine_post_tail_settled": cheap_tail_post_tail_summary.get("settled"),
                "feature_gate_cheap_tail_shrink_freeze_ts": (feature_gate_cheap_tail_shrink_watch.get("state") or {}).get("freeze_ts_utc"),
                "feature_gate_cheap_tail_shrink_best_policy": cheap_tail_shrink_best.get("policy"),
                "feature_gate_cheap_tail_shrink_settled": cheap_tail_shrink_best.get("settled"),
                "feature_gate_cheap_tail_shrink_coverage": cheap_tail_shrink_best.get("coverage_pct"),
                "feature_gate_cheap_tail_shrink_weighted_net_cents": cheap_tail_shrink_best.get("weighted_net_cents"),
                "feature_gate_cheap_tail_shrink_blockers": cheap_tail_shrink_best.get("blockers"),
                "feature_gate_source_risk_shrink_freeze_ts": (
                    feature_gate_source_risk_shrink_watch.get("state") or {}
                ).get("freeze_ts_utc"),
                "feature_gate_source_risk_shrink_diag_best_policy": source_risk_shrink_diag_best.get("policy"),
                "feature_gate_source_risk_shrink_diag_weighted_net_cents": source_risk_shrink_diag_best.get(
                    "weighted_net_cents"
                ),
                "feature_gate_source_risk_shrink_diag_row_source_share": source_risk_shrink_diag_best.get(
                    "row_source_share"
                ),
                "feature_gate_source_risk_shrink_diag_exposure_source_share": source_risk_shrink_diag_best.get(
                    "exposure_source_share"
                ),
                "feature_gate_source_risk_shrink_diag_blockers": source_risk_shrink_diag_best.get("blockers"),
                "feature_gate_source_risk_shrink_post_settled": source_risk_shrink_post_best.get("settled"),
                "feature_gate_source_risk_shrink_post_blockers": source_risk_shrink_post_best.get("blockers"),
            },
            "next": "Keep boundary-clock in the lead entry-watch group, but require clean approved forward rows plus a larger full-loss cushion before promotion talk.",
        },
        {
            "lane": "feature_gate_cheap_tail_shrink",
            "decision": "freeze_and_monitor",
            "candidate": "cheap_tail_notional_shrink",
            "why": "The post-freeze feature-gate source blocker now has a physical cheap-tail explanation: tiny-ask rejected/reconstructed rows add coverage and PnL, but their reconstructed slice depends on one large tail win. The watch uses continuous size shrinkage, not a new hard cutoff, and starts from its own freeze timestamp.",
            "evidence": {
                "freeze_ts": (feature_gate_cheap_tail_shrink_watch.get("state") or {}).get("freeze_ts_utc"),
                "parent_feature_gate_freeze_ts": (feature_gate_cheap_tail_shrink_watch.get("state") or {}).get("parent_feature_gate_freeze_ts_utc"),
                "best_policy": cheap_tail_shrink_best.get("policy"),
                "strict_settled": cheap_tail_shrink_best.get("settled"),
                "strict_coverage": cheap_tail_shrink_best.get("coverage_pct"),
                "strict_weighted_net_cents": cheap_tail_shrink_best.get("weighted_net_cents"),
                "strict_row_reconstructed_share": cheap_tail_shrink_best.get("row_reconstructed_share"),
                "strict_blockers": cheap_tail_shrink_best.get("blockers"),
            },
            "next": "Collect post-watch-freeze rows only; require >=30 settled, target coverage, <=35% row-source share, positive weighted net, and cushion >=3 before this can influence live entry sizing.",
        },
        {
            "lane": "feature_gate_source_risk_shrink",
            "decision": "freeze_and_monitor",
            "candidate": "cheap_thin_fifth_observable_notional_shrink",
            "why": "A new observable source-risk shrink watch targets the rejected-slice mechanism without using source labels for the rule. Diagnostic feature-window evidence keeps broad raw03 coverage, lifts weighted net above the three-full-loss cushion, and reduces exposure-source share under 35%, but the official row-count source gate still fails and strict post-watch rows are zero.",
            "evidence": {
                "freeze_ts": (feature_gate_source_risk_shrink_watch.get("state") or {}).get("freeze_ts_utc"),
                "feature_freeze_ts": feature_gate_source_risk_shrink_watch.get("feature_freeze_ts_utc"),
                "diagnostic_policy": source_risk_shrink_diag_best.get("policy"),
                "diagnostic_entries": source_risk_shrink_diag_best.get("entries"),
                "diagnostic_settled": source_risk_shrink_diag_best.get("settled"),
                "diagnostic_coverage": source_risk_shrink_diag_best.get("coverage_pct"),
                "diagnostic_weighted_net_cents": source_risk_shrink_diag_best.get("weighted_net_cents"),
                "diagnostic_row_source_share": source_risk_shrink_diag_best.get("row_source_share"),
                "diagnostic_exposure_source_share": source_risk_shrink_diag_best.get("exposure_source_share"),
                "diagnostic_cushion": source_risk_shrink_diag_best.get("full_loss_cushion"),
                "diagnostic_blockers": source_risk_shrink_diag_best.get("blockers"),
                "strict_post_settled": source_risk_shrink_post_best.get("settled"),
                "strict_post_blockers": source_risk_shrink_post_best.get("blockers"),
            },
            "next": "Collect only rows after this watch freeze. This can support sizing or risk-control research only if strict rows clear sample, coverage, weighted net, cushion, exposure-source, and the hard row-source gate.",
        },
        {
            "lane": "feature_gate_core_expansion_mix",
            "decision": "watch_only_not_improved",
            "candidate": "ask65_core_plus_raw03_expansion",
            "why": "The clean high-win ask65 core and broader raw03 bridge were tested as a dual/portfolio idea. The broad full-control row still has the best PnL, while fractional expansion only reduces notional source exposure; it does not clear official row-source or full-loss-cushion gates.",
            "evidence": {
                "core_candidate": feature_gate_core_expansion_mix.get("core_candidate"),
                "broad_candidate": feature_gate_core_expansion_mix.get("broad_candidate"),
                "best_policy": feature_gate_core_mix_best.get("policy"),
                "entries": feature_gate_core_mix_best.get("entries"),
                "settled": feature_gate_core_mix_best.get("settled"),
                "wl": f"{feature_gate_core_mix_best.get('wins')}/{feature_gate_core_mix_best.get('losses')}",
                "coverage": feature_gate_core_mix_best.get("coverage_pct"),
                "weighted_net_cents": feature_gate_core_mix_best.get("weighted_net_cents"),
                "row_source_share": feature_gate_core_mix_best.get("row_source_share"),
                "exposure_source_share": feature_gate_core_mix_best.get("exposure_source_share"),
                "full_loss_cushion": feature_gate_core_mix_best.get("full_loss_cushion"),
                "coverage_entries_needed": feature_gate_core_mix_best.get("coverage_entries_needed"),
                "settled_rows_needed": feature_gate_core_mix_best.get("settled_rows_needed"),
                "clean_rows_needed_for_source": feature_gate_core_mix_best.get("clean_rows_needed_for_source"),
                "net_cents_needed_for_cushion3": feature_gate_core_mix_best.get("net_cents_needed_for_cushion3"),
                "blockers": feature_gate_core_mix_best.get("blockers"),
            },
            "next": "Do not promote the mix. Keep watching the broad bridge for five additional clean approved selections and at least 60c more cushion; otherwise prioritize source-quality repair over portfolio weighting.",
        },
        {
            "lane": "feature_gate_coverage_repair",
            "decision": "no_simple_relaxation_repair",
            "candidate": "raw05_anchor_plus_observable_relaxations",
            "why": "A focused coverage-repair scan tested observable relaxations around the near-promotion raw05 gate. The nearest target-coverage relaxation buys coverage by adding source-fragile rows with negative added PnL and still fails source/cushion gates, so a simple broader threshold is not the repair.",
            "evidence": {
                "freeze_ts": feature_gate_coverage_repair.get("freeze_ts_utc"),
                "entry_anchor_rule": feature_gate_coverage_repair_entry.get("anchor_rule"),
                "entry_anchor": feature_gate_coverage_repair_entry.get("anchor_summary"),
                "entry_nearest_rule": feature_gate_coverage_repair_entry_near.get("rule"),
                "entry_nearest_summary": feature_gate_coverage_repair_entry_near_summary,
                "entry_nearest_added_summary": feature_gate_coverage_repair_entry_near.get("added_summary"),
                "entry_nearest_blockers": feature_gate_coverage_repair_entry_near.get("blockers"),
                "bridge_anchor_rule": feature_gate_coverage_repair_bridge.get("anchor_rule"),
                "bridge_anchor": feature_gate_coverage_repair_bridge.get("anchor_summary"),
                "bridge_nearest_rule": feature_gate_coverage_repair_bridge_near.get("rule"),
                "bridge_nearest_summary": feature_gate_coverage_repair_bridge_near_summary,
                "bridge_nearest_added_summary": feature_gate_coverage_repair_bridge_near.get("added_summary"),
                "bridge_nearest_blockers": feature_gate_coverage_repair_bridge_near.get("blockers"),
            },
            "next": "Keep the raw05 near-promotion lane on forward watch. For active research, test continuous penalties or exit-state repairs on the added rows; do not widen entry thresholds as a standalone candidate.",
        },
        {
            "lane": "feature_gate_raw05_gap_audit",
            "decision": "do_not_repair_with_raw03_relaxation",
            "candidate": "raw05_anchor_vs_raw03_relaxation",
            "why": (
                "The current-denominator joint-gap audit replaces the older moving-denominator read: raw05 bridge is cleaner and has cushion 3, but only "
                f"{fmt(feature_gate_joint_raw05_bridge.get('coverage_pct'))}% coverage and still trails the live snapshot by "
                f"{fmt(feature_gate_joint_raw05_bridge.get('cents_needed_to_match_live_snapshot'))}c. raw03 bridge reaches "
                f"{fmt(feature_gate_joint_raw03_bridge.get('coverage_pct'))}% coverage, but source share "
                f"{fmt(feature_gate_joint_raw03_bridge.get('reconstructed_share'))}, cushion "
                f"{feature_gate_joint_raw03_bridge.get('full_loss_cushion')}, and live-snapshot gap "
                f"{fmt(feature_gate_joint_raw03_bridge.get('cents_needed_to_match_live_snapshot'))}c keep it blocked. "
                "The mechanism synthesis also blocks broad exit suppression: raw05 bridge losses are mostly no-exit/source observations, and the approved losing rows were helped by live exits versus holding. This is a clean-core coverage/source wait, not a threshold-tuning or blanket-exit repair."
            ),
            "evidence": {
                "quick_status_generated_at_utc": boundary_clock_feature_gate_quick_status.get("generated_at_utc"),
                "quick_entry_best": feature_gate_quick_entry_best,
                "quick_bridge_best": feature_gate_quick_bridge_best,
                "joint_gap_generated_at_utc": feature_gate_joint_gate_gap.get("generated_at_utc"),
                "joint_raw05_entry": feature_gate_joint_raw05_entry,
                "joint_raw05_bridge": feature_gate_joint_raw05_bridge,
                "joint_raw03_bridge": feature_gate_joint_raw03_bridge,
                "gap_mechanism_conclusion": feature_gate_gap_mechanism_synthesis.get("conclusion"),
                "gap_mechanism_exit_attribution": feature_gate_gap_mechanism_attr,
                "gap_mechanism_exit_state_best": feature_gate_gap_exit_state_best,
                "raw03_autopsy_generated_at_utc": feature_gate_raw03_vs_raw05_autopsy.get("generated_at_utc"),
                "entry_raw05_summary": raw03_autopsy_entry_raw05.get("summary"),
                "entry_raw03_summary": raw03_autopsy_entry_raw03.get("summary"),
                "entry_raw03_minus_raw05_marginal": raw03_autopsy_entry_marginal.get("summary"),
                "bridge_raw05_summary": raw03_autopsy_bridge_raw05.get("summary"),
                "bridge_raw03_summary": raw03_autopsy_bridge_raw03.get("summary"),
                "bridge_raw03_minus_raw05_marginal": raw03_autopsy_bridge_marginal.get("summary"),
                "raw05_gap_generated_at_utc": feature_gate_raw05_coverage_gap.get("generated_at_utc"),
                "entry_omitted_source_counts": raw05_gap_entry.get("omitted_source_counts"),
                "entry_omitted_fail_reasons": raw05_gap_entry.get("omitted_fail_reason_counts"),
                "entry_approved_omitted_count": raw05_gap_entry.get("approved_omitted_count"),
                "entry_missing_entries_for_75pct": raw05_gap_entry.get("missing_entries_for_75pct"),
                "entry_approved_only_oracle": raw05_gap_entry_approved_oracle.get("summary"),
                "entry_any_source_oracle": raw05_gap_entry_any_oracle.get("summary"),
                "entry_any_source_oracle_blockers": raw05_gap_entry_any_oracle.get("blockers"),
                "bridge_omitted_source_counts": raw05_gap_bridge.get("omitted_source_counts"),
                "bridge_omitted_fail_reasons": raw05_gap_bridge.get("omitted_fail_reason_counts"),
                "bridge_approved_omitted_count": raw05_gap_bridge.get("approved_omitted_count"),
                "bridge_missing_entries_for_75pct": raw05_gap_bridge.get("missing_entries_for_75pct"),
                "bridge_approved_only_oracle": raw05_gap_bridge_approved_oracle.get("summary"),
                "bridge_any_source_oracle": raw05_gap_bridge_any_oracle.get("summary"),
                "bridge_any_source_oracle_blockers": raw05_gap_bridge_any_oracle.get("blockers"),
            },
            "next": "Do not widen raw05/raw03 thresholds or add broad exit suppression as the next candidate. Keep the existing feature-gate watches alive, and only pursue a new coverage repair if it introduces independently frozen clean-row expansion or a true observable source-quality proxy that proves itself on post-freeze rows.",
        },
        {
            "lane": "feature_gate_coverage_size_shrink",
            "decision": "watch_only_near_gate",
            "candidate": "raw05_anchor_plus_low_absd_repair_size_shrink",
            "why": (
                "The coverage-repair rows are weak as full-size entries, and current-denominator marginal sizing does not turn them into a promotion repair. "
                f"The best exposure-clean proxy reaches {fmt(feature_gate_margin_proxy_best.get('coverage_pct'))}% coverage, "
                f"{fmt(feature_gate_margin_proxy_best.get('weighted_net_cents'))}c weighted net, cushion "
                f"{feature_gate_margin_proxy_best.get('full_loss_cushion')}, and exposure-source share "
                f"{fmt(feature_gate_margin_proxy_best.get('exposure_source_share'))}, but official row-source share remains "
                f"{fmt(feature_gate_margin_proxy_best.get('row_source_share'))} and the policy's delta versus the live snapshot is "
                f"{fmt(feature_gate_margin_proxy_best.get('delta_vs_live_snapshot_cents'))}c. Zeroing the raw03-only marginal rows restores raw05 source share "
                f"{fmt(feature_gate_margin_proxy_raw05.get('row_source_share'))}, but coverage falls to "
                f"{fmt(feature_gate_margin_proxy_raw05.get('coverage_pct'))}%. The strict source-proxy autopsy adds that the current post-birth proxy rows need clean-row replacement/addition plus cushion, not another inherited diagnostic relaxation. The older size-shrink and delayed-recheck overlays stay useful as risk context and child watches, but each child needs its own post-birth evidence before any promotion discussion."
            ),
            "evidence": {
                "freeze_ts": feature_gate_coverage_size_shrink.get("freeze_ts_utc"),
                "entry_best": feature_gate_coverage_size_entry_best,
                "bridge_best": feature_gate_coverage_size_bridge_best,
                "current_margin_size_proxy_generated_at_utc": feature_gate_current_margin_size_proxy.get("generated_at_utc"),
                "current_margin_size_proxy_best": feature_gate_margin_proxy_best,
                "current_margin_size_proxy_raw05_anchor": feature_gate_margin_proxy_raw05,
                "current_margin_size_proxy_interpretation": feature_gate_current_margin_size_proxy.get("interpretation"),
                "entry_exit_attribution": feature_gate_coverage_size_attr_entry,
                "bridge_exit_attribution": feature_gate_coverage_size_attr_bridge,
                "entry_runway": feature_gate_coverage_size_runway_entry,
                "bridge_runway": feature_gate_coverage_size_runway_bridge,
                "source_slice_entry": feature_gate_size_source_slice_entry,
                "source_slice_bridge": feature_gate_size_source_slice_bridge,
                "source_slice_interpretation": feature_gate_size_shrink_source_slice.get("interpretation"),
                "strict_drilldown": feature_gate_size_strict_drilldown_summary,
                "observable_selection_mix_entry": feature_gate_observable_selection_entry,
                "observable_selection_mix_bridge": feature_gate_observable_selection_bridge,
                "exit_overlay_entry": feature_gate_size_exit_overlay_entry,
                "exit_overlay_bridge": feature_gate_size_exit_overlay_bridge,
                "delayed_recheck_exit_overlay_freeze_ts": (feature_gate_size_shrink_delayed_recheck_exit.get("state") or {}).get("freeze_ts_utc"),
                "delayed_recheck_exit_diag_best": feature_gate_size_delayed_exit_diag_best,
                "delayed_recheck_exit_post_best": feature_gate_size_delayed_exit_post_best,
                "delayed_recheck_rescue_freeze_ts": (feature_gate_size_shrink_delayed_recheck_rescue.get("state") or {}).get("freeze_ts_utc"),
                "delayed_recheck_rescue_diag_best": feature_gate_size_delayed_rescue_diag_best,
                "delayed_recheck_rescue_post_best": feature_gate_size_delayed_rescue_post_best,
                "source_confirmation_replacement_freeze_ts": (feature_gate_source_confirmation_replacement.get("state") or {}).get("freeze_ts_utc"),
                "source_confirmation_replacement_diag_best": feature_gate_source_confirmation_diag_best,
                "source_confirmation_replacement_post_best": feature_gate_source_confirmation_post_best,
                "late_collapse_recheck_freeze_ts": (feature_gate_late_collapse_recheck_rescue.get("state") or {}).get("variant_set_freeze_ts_utc"),
                "late_collapse_recheck_diag_best": feature_gate_late_collapse_diag_best,
                "late_collapse_recheck_post_best": feature_gate_late_collapse_post_best,
                "dual_clock_recheck_freeze_ts": (feature_gate_dual_clock_recheck_rescue.get("state") or {}).get("freeze_ts_utc"),
                "dual_clock_recheck_diag_best": feature_gate_dual_clock_diag_best,
                "dual_clock_recheck_post_best": feature_gate_dual_clock_post_best,
                "confirmed_dual_clock_fill_freeze_ts": (feature_gate_confirmed_dual_clock_fill.get("state") or {}).get("freeze_ts_utc"),
                "confirmed_dual_clock_fill_diag_best": feature_gate_confirmed_dual_diag_best,
                "confirmed_dual_clock_fill_post_best": feature_gate_confirmed_dual_post_best,
                "confirmed_dual_clock_fill_stress_candidate": feature_gate_confirmed_dual_stress_candidate,
                "confirmed_dual_clock_fill_stress_blockers": feature_gate_confirmed_dual_stress_blockers,
                "confirmed_dual_clock_fill_rule_component_stress": feature_gate_confirmed_dual_rule_stress,
                "source_quality_proxy_diag_entry": feature_gate_source_proxy_diag_entry,
                "source_quality_proxy_diag_bridge": feature_gate_source_proxy_diag_bridge,
                "source_quality_proxy_post_entry": feature_gate_source_proxy_post_entry,
                "source_quality_proxy_post_bridge": feature_gate_source_proxy_post_bridge,
                "source_proxy_coverage_repair_diag_entry": feature_gate_source_proxy_repair_diag_entry,
                "source_proxy_coverage_repair_diag_bridge": feature_gate_source_proxy_repair_diag_bridge,
                "source_proxy_coverage_repair_post_entry": feature_gate_source_proxy_repair_post_entry,
                "source_proxy_coverage_repair_post_bridge": feature_gate_source_proxy_repair_post_bridge,
                "source_proxy_strict_autopsy_generated_at_utc": feature_gate_source_proxy_strict_autopsy.get("generated_at_utc"),
                "source_proxy_strict_autopsy_entry": feature_gate_source_proxy_autopsy_entry,
                "source_proxy_strict_autopsy_bridge": feature_gate_source_proxy_autopsy_bridge,
                "source_blocker_mechanism_entry": feature_gate_source_blocker_entry_summary,
                "source_blocker_mechanism_bridge": feature_gate_source_blocker_bridge_summary,
                "interpretation": feature_gate_coverage_size_shrink.get("interpretation"),
            },
            "next": "Track the confirmed dual-clock fill watch from its own freeze, but open the next research branch around clean approved-row expansion for the abs 0.75-1.25 middle-distance pocket. It needs >=30 post-birth rows, target coverage, <=35% reconstructed share, positive net after fees, cushion >=3, and a refreshed live-baseline win before any live-test discussion.",
        },
        {
            "lane": "feature_gate_middle_distance_core_watch",
            "decision": "freeze_and_monitor_sidecar_only",
            "candidate": (feature_gate_middle_core_diag_best.get("rule")),
            "why": "The source-slice audit says the near-gate size-shrink branch is not failing because the clean core is bad; it is failing because low-abs repair filler adds coverage with weak source quality and weak PnL. The new middle-distance watch freezes an observable abs-floor core as a sidecar hypothesis: diagnostically clean, high win-rate, and low reconstructed share, but too narrow and still below the refreshed live baseline. Exit attribution found real winner clipping inside this core, but the frozen exit-guard child is also narrow, below live, and has zero post-birth rows so far.",
            "evidence": {
                "freeze_ts": (feature_gate_middle_distance_core_watch.get("state") or {}).get("freeze_ts_utc"),
                "diagnostic_best": feature_gate_middle_core_diag_best,
                "post_birth_best": feature_gate_middle_core_post_best,
                "expansion_bound_entry": feature_gate_middle_core_bound_entry,
                "expansion_bound_bridge": feature_gate_middle_core_bound_bridge,
                "expansion_bound_interpretation": feature_gate_middle_core_expansion_bound.get("interpretation"),
                "exit_attribution_entry": feature_gate_middle_core_attr_entry,
                "exit_attribution_interpretation": feature_gate_middle_core_exit_attribution.get("interpretation"),
                "exit_guard_freeze_ts": (feature_gate_middle_core_exit_guard_watch.get("state") or {}).get("freeze_ts_utc"),
                "exit_guard_diagnostic_best": feature_gate_middle_exit_guard_diag_best,
                "exit_guard_post_birth_best": feature_gate_middle_exit_guard_post_best,
                "exit_guard_interpretation": feature_gate_middle_core_exit_guard_watch.get("interpretation"),
                "interpretation": feature_gate_middle_distance_core_watch.get("interpretation"),
            },
            "next": "Track post_middle_core_freeze_entry/bridge and post_middle_exit_guard_freeze_entry/bridge only. The current parent pool lacks enough approved addable rows to reach broad coverage, so do not widen the low-abs repair tail. Do not use diagnostic parent rows for live testing; this branch needs its own >=30 settled rows, positive PnL, <=35% reconstructed share, cushion >=3, and a controlled live-test gate pass.",
        },
        {
            "lane": "high_win_core_broad_fill_mix",
            "decision": "diagnostic_watch_only",
            "candidate": high_win_core_broad_fill_best.get("candidate"),
            "why": "High-win p_side/source-quality cores are attractive as a nucleus, but filling them back to 75% coverage either reopens source share or misses the three-full-loss cushion. This is a useful physical direction, not promotion evidence.",
            "evidence": {
                "feature_gate_freeze_ts": high_win_core_broad_fill_mix.get("feature_gate_freeze_ts_utc"),
                "source_proxy_freeze_ts": high_win_core_broad_fill_mix.get("source_proxy_freeze_ts_utc"),
                "best_mix": high_win_core_broad_fill_best,
                "interpretation": high_win_core_broad_fill_mix.get("interpretation"),
            },
            "next": "Keep this as a watch branch from the source-proxy freeze. A future strict version needs >=30 post-birth rows, target coverage, <=35% reconstructed share, positive PnL, cushion >=3, and a refreshed live-baseline comparison.",
        },
        {
            "lane": "top_component_mix_portfolio",
            "decision": "freeze_candidate_blueprint_next",
            "candidate": top_component_mix_best.get("label"),
            "why": "The strongest current diagnostic improvement is to combine the top soft-frontier delayed-recheck rescue exit with the high-win parent midprice entry lane, then fill parent rows that lacked exit-clock rescue rows using conservative hold-to-settlement scoring. This repairs the hidden exit-clock subset problem: rows-only rescue PnL is high but only covers about 61%. The safer abs_d-ranked observable parent-fill variant restores 75% coverage with reconstructed share near 32% and remains far above the refreshed live baseline after top-row and no-suppression stress. The loss drilldown says the remaining damage is not one thing: missed exit-rescue false negatives, parent-fill entry/FV losses, and true FV/entry losers all remain. The false-negative rescue child cleanly repairs the three approved-entry missed rescues diagnostically. A new parent-fill repair child then tests confidence-sizing on the remaining rejected-actionable fill pocket and lifts diagnostic net above 20 full-loss rows, but it has its own freeze and only immature strict evidence. The strict-row autopsy now shows that the first five unique strict rows are all parent-fill/no-exit-clock rows, four are rejected-actionable, and the losses look like source-quality plus FV/entry false positives. The observable quarantine child says low-ask/weak-boundary zeroing explains the tiny strict autopsy loss pocket, but it costs diagnostic coverage and has zero own post-birth rows. This is still diagnostic/prefreeze evidence, not a live candidate.",
            "evidence": {
                "generated_at_utc": top_component_mix_portfolio.get("generated_at_utc"),
                "denominator": top_component_mix_portfolio.get("denominator"),
                "best_rescue_variant": top_component_mix_portfolio.get("best_rescue_variant"),
                "best_mix": top_component_mix_best,
                "loss_cluster_variant": top_component_loss_cluster.get("variant"),
                "loss_cluster_loss_count": top_component_loss_cluster.get("loss_count"),
                "loss_cluster_loss_net_cents": top_component_loss_cluster.get("loss_net_cents"),
                "loss_cluster_by_mode": top_component_loss_by_mode,
                "loss_cluster_by_source": top_component_loss_by_source,
                "loss_cluster_hold_delta_on_losses_cents": top_component_loss_cluster.get("counterfactual_hold_delta_on_losses_cents"),
                "false_negative_child_freeze_ts": (top_component_false_negative_rescue.get("state") or {}).get("freeze_ts_utc"),
                "false_negative_child_best": top_component_false_negative_best,
                "false_negative_child_interpretation": top_component_false_negative_rescue.get("interpretation"),
                "parent_fill_repair_child_freeze_ts": (top_component_parent_fill_repair.get("state") or {}).get("freeze_ts_utc"),
                "parent_fill_repair_child_best": top_component_parent_fill_best,
                "parent_fill_repair_child_interpretation": top_component_parent_fill_repair.get("interpretation"),
                "observable_quarantine_child_freeze_ts": (top_component_observable_quarantine.get("state") or {}).get("freeze_ts_utc"),
                "observable_quarantine_diag_best": top_component_quarantine_diag_best,
                "observable_quarantine_autopsy_best": top_component_quarantine_autopsy_best,
                "observable_quarantine_strict_best": top_component_quarantine_strict_best,
                "observable_quarantine_interpretation": top_component_observable_quarantine.get("interpretation"),
                "strict_row_autopsy_generated_at_utc": top_component_strict_row_autopsy.get("generated_at_utc"),
                "strict_row_autopsy_unique_rows": top_component_strict_row_autopsy.get("strict_unique_rows"),
                "strict_row_autopsy_net_cents": top_component_strict_row_autopsy.get("strict_net_cents"),
                "strict_row_autopsy_tag_counts": top_component_strict_row_autopsy.get("tag_counts"),
                "strict_row_autopsy_source_counts": top_component_strict_row_autopsy.get("source_counts"),
                "strict_row_autopsy_source_net_cents": top_component_strict_row_autopsy.get("source_net_cents"),
                "strict_row_autopsy_interpretation": top_component_strict_row_autopsy.get("interpretation"),
                "interpretation": top_component_mix_portfolio.get("interpretation"),
                "loss_cluster_interpretation": top_component_loss_cluster.get("interpretation"),
            },
            "next": "Track each variant from its own freeze and require fresh rows before promotion. The false-negative rescue child, parent-fill repair child, and observable quarantine child now form the top diagnostic stack, but none can enter live-test discussion until its own strict post-child rows clear sample, source, cushion, coverage, and live-readiness gates.",
        },
        {
            "lane": "p50_book_edge_no_side_shrink_watch",
            "decision": "freeze_and_monitor",
            "candidate": "p50_book_plus_05_edge_nonnegative_quarter_no_side",
            "why": "The p50 book-edge parent is broad and positive but source-blocked; its cleanest observable repair is side-aware sizing because NO-side rows were net negative while YES rows carried the sample. Quarter-sizing NO improves the diagnostic parent PnL while preserving broad coverage, but the child starts with zero post-birth rows.",
            "evidence": {
                "diagnostic_best_child": p50_book_edge_best_child,
                "source_feasibility_bound": p50_book_edge_source_bound,
                "watch_freeze_ts": (p50_book_edge_no_side_shrink_watch.get("freeze") or {}).get("freeze_ts_utc"),
                "watch_summary": p50_book_edge_no_side_shrink_summary,
                "watch_blockers": p50_book_edge_no_side_shrink_watch.get("blockers"),
                "source_drilldown_interpretation": p50_book_edge_source_failure_drilldown.get("interpretation"),
                "source_bound_interpretation": p50_book_edge_source_feasibility_bound.get("interpretation"),
            },
            "next": "Track post-birth rows only. Parent evidence cannot satisfy broad coverage plus the source gate from its current selected row pool, so the child needs genuinely new clean approved rows, not another diagnostic reshuffle.",
        },
        {
            "lane": "p50_soft_frontier_overlap_mix",
            "decision": "diagnostic_do_not_freeze_yet",
            "candidate": "p50_yes_only_plus_soft_frontier_quarter_midprice_boundary",
            "why": "The p50/book-edge and soft-frontier/midprice families are partially complementary on PnL, but the high-PnL union gets its gain by reopening a large source-quality share. The cleaner soft-primary union adds only a few p50 non-overlap rows, so p50 does not currently repair the soft-frontier source blocker.",
            "evidence": {
                "best_mix": p50_soft_frontier_best_mix,
                "lane_counts": p50_soft_frontier_overlap_mix.get("lane_counts"),
                "interpretation": p50_soft_frontier_overlap_mix.get("interpretation"),
            },
            "next": "Do not freeze the high-PnL p50+soft union until source-quality is repaired. If future p50 post-birth rows become cleaner, re-run overlap and look for positive non-overlap rows with <=35% reconstructed share.",
        },
        {
            "lane": "soft_frontier_midprice_boundary_shrink",
            "decision": "freeze_and_monitor",
            "candidate": "quarter_midprice_boundary",
            "why": "The best new entry-side mix preserves broad soft-frontier coverage while shrinking a repeated near-boundary mid-price loss pocket; it is physically cleaner than another hard cutoff, but has zero strict post-birth settled rows so far.",
            "evidence": {
                "freeze_ts": (soft_frontier_midprice_boundary_shrink.get("state") or {}).get("freeze_ts_utc"),
                "diagnostic_best": midprice_diag_best.get("candidate"),
                "diagnostic_settled": midprice_diag_summary.get("settled"),
                "diagnostic_wl": f"{midprice_diag_summary.get('wins')}/{midprice_diag_summary.get('losses')}",
                "diagnostic_coverage": midprice_diag_summary.get("coverage_pct"),
                "diagnostic_net_cents": midprice_diag_summary.get("net_cents"),
                "diagnostic_delta_vs_unweighted_cents": midprice_diag_summary.get("delta_vs_unweighted_cents"),
                "diagnostic_band_rows": midprice_diag_summary.get("midprice_boundary_rows"),
                "diagnostic_band_raw_net_cents": midprice_diag_summary.get("midprice_boundary_raw_net_cents"),
                "diagnostic_band_weighted_net_cents": midprice_diag_summary.get("midprice_boundary_weighted_net_cents"),
                "diagnostic_reconstructed_share": midprice_diag_best.get("reconstructed_share"),
                "strict_best": midprice_strict_best.get("candidate"),
                "strict_settled": midprice_strict_summary.get("settled"),
                "strict_coverage": midprice_strict_summary.get("coverage_pct"),
                "strict_net_cents": midprice_strict_summary.get("net_cents"),
                "strict_blockers": midprice_strict_best.get("blockers"),
            },
            "next": "Keep the mid-price boundary shrink watch running; require >=30 post-freeze settled rows, <=35% reconstructed share, positive net, and cushion >=3 before any live-test discussion.",
        },
        {
            "lane": "midprice_source_dilution",
            "decision": "freeze_and_monitor",
            "candidate": (midprice_source_dilution.get("state") or {}).get("candidate"),
            "why": "The strict post-feature midprice lane misses source quality by a tiny margin. An observable weak-boundary dilution drops one close-boundary rejected loser, clears target coverage, source share, and cushion in parent diagnostic evidence, and is now frozen for its own forward proof.",
            "evidence": {
                "freeze_ts": (midprice_source_dilution.get("state") or {}).get("freeze_ts_utc"),
                "diagnostic_best": midprice_dilution_diag_best,
                "post_birth_best": midprice_dilution_post_best,
                "runway_entry": midprice_source_dilution_runway.get("entry_runway"),
                "runway_bridge": midprice_source_dilution_runway.get("bridge_runway"),
                "runway_any_live_ready": midprice_source_dilution_runway.get("any_live_ready"),
                "stability": {
                    "kept_summary": midprice_dilution_stability_entry.get("kept_summary"),
                    "dropped_summary": midprice_dilution_stability_entry.get("dropped_summary"),
                    "source_split": midprice_dilution_stability_entry.get("source_split"),
                    "leave_one_out": midprice_dilution_stability_entry.get("leave_one_out"),
                    "flags": midprice_dilution_stability_entry.get("stability_flags"),
                },
                "mechanism": midprice_dilution_mechanism_summary,
                "interpretation": midprice_source_dilution.get("interpretation"),
            },
            "next": "Track post_dilution_birth_entry/bridge only. Parent stability is not top-win dependent, but it is source/coverage-margin thin and the remaining source-risk slice has no omitted approved market pool to replace it. Do not promote until this new dilution rule has >=30 settled rows, target coverage, <=35% reconstructed share, positive PnL, and cushion >=3 from its own freeze.",
        },
        {
            "lane": "soft_frontier_midprice_boundary_exit_stack",
            "decision": "freeze_and_monitor",
            "candidate": "quarter_midprice_boundary_plus_book_gap_exit",
            "why": "The top broad-entry shrink and book-gap exit overlap is diagnostically strong, but the combined stack has zero post-stack joined exits; this is an overlap hypothesis, not promotion evidence.",
            "evidence": {
                "freeze_ts": (soft_frontier_midprice_boundary_exit_stack.get("freeze") or {}).get("freeze_ts_utc"),
                "best_overlap": midprice_exit_stack_best.get("candidate"),
                "best_overlap_entry_settled": midprice_exit_stack_entry_summary.get("settled"),
                "best_overlap_joined_exits": midprice_exit_stack_best.get("joined_exit_rows"),
                "best_overlap_post_stack_joined_exits": midprice_exit_stack_best.get("post_stack_joined_exit_rows"),
                "best_overlap_weighted_exit_net_cents": midprice_exit_stack_best.get("weighted_joined_exit_candidate_cents"),
                "best_overlap_post_stack_net_cents": midprice_exit_stack_best.get("post_stack_weighted_exit_candidate_cents"),
                "runway_candidate": midprice_exit_stack_runway_best.get("candidate"),
                "post_stack_joined_rows_needed": midprice_exit_stack_runway_best.get("post_stack_joined_rows_needed_for_sample_gate"),
                "post_stack_weighted_cents_needed_for_cushion3": midprice_exit_stack_runway_best.get("post_stack_weighted_cents_needed_for_cushion3"),
                "runway_blockers": midprice_exit_stack_runway_best.get("runway_blockers"),
            },
            "next": "Keep the combined stack frozen and watch post-stack joined-exit density; do not treat diagnostic entry and exit gains as additive until >=30 post-stack joined exits and cushion >=3 exist.",
        },
        {
            "lane": "soft_frontier_midprice_boundary_dual_exit_guard",
            "decision": "freeze_and_monitor",
            "candidate": "book_gap_or_clip_with_midprice_boundary_guard",
            "why": "The strongest current mix uses the broad soft-frontier entry, shrinks near-boundary midprice danger rows, then combines book-gap and clip-style exit suppression while refusing to suppress rows the entry model already downweighted. This removed the diagnostic suppressed-loser flaw, but has no post-guard joined rows yet.",
            "evidence": {
                "freeze_ts": (soft_frontier_midprice_boundary_dual_exit_guard.get("freeze") or {}).get("freeze_ts_utc"),
                "best_policy": dual_midprice_guard_best.get("policy"),
                "diagnostic_joined_rows": dual_midprice_guard_best.get("joined_exit_rows"),
                "diagnostic_suppressed_rows": dual_midprice_guard_best.get("suppressed_rows"),
                "diagnostic_weighted_net_cents": dual_midprice_guard_best.get("weighted_candidate_cents"),
                "diagnostic_weighted_delta_cents": dual_midprice_guard_best.get("weighted_delta_cents"),
                "diagnostic_blockers": dual_midprice_guard_best.get("blockers"),
                "runway_best_policy": dual_midprice_guard_runway_best.get("policy"),
                "runway_post_joined_rows": dual_midprice_guard_runway_best.get("post_joined_rows"),
                "runway_post_suppressed_rows": dual_midprice_guard_runway_best.get("post_suppressed_rows"),
                "runway_post_net_cents": dual_midprice_guard_runway_best.get("post_net_cents"),
                "runway_post_reconstructed_share": dual_midprice_guard_runway_best.get("post_reconstructed_share"),
                "runway_post_full_loss_cushion": dual_midprice_guard_runway_best.get("post_full_loss_cushion"),
                "runway_missing_gates": dual_midprice_guard_runway_best.get("missing_gates"),
            },
            "next": "Track the dedicated guard runway. Do not live-test until the post-guard overlap has >=30 joined rows, >=30 suppressed decisions, positive post net, cushion >=3, and source share <=35%.",
        },
        {
            "lane": "sidecar_live_test",
            "decision": "watch_only_none_ready",
            "candidate": sidecar_closest.get("policy"),
            "why": "A narrow live-test lane is tracked separately from broad-entry promotion, but no sidecar currently clears sample, source-quality, cushion, and live-readiness gates together. The top-PnL plus top-win union is diagnostically the closest broad row, and it now has its own frozen watch so future rows can count. At birth it has zero settled rows, so the old high PnL remains diagnostic context only. Confirmation/veto is cleaner, but it cuts the best parent-fill lane down to roughly half-market coverage, so it remains a narrow diagnostic rather than a deployable broad strategy. The same-window delta autopsy adds a harder blocker: the current forced strict precheck is behind actual live v28 on the same post-freeze markets, with the largest deficit coming from rows where the candidate is positive but live captured more. The sequence audit makes the mechanism concrete: live is beating the one-shot candidate through larger terminal same-side exposure, same-side exit capture at scale, and side-flip escapes after candidate-side damage. A simple observable exposure-weighting repair improves the diagnostic gap but still trails live and fails cushion, so do not freeze it as-is. The side-flip feasibility audit says the escape behavior is real but sparse and not triggerable from the static candidate row; a deployable child would need an explicit state-transition trigger and its own freeze. This branch must prove both own-freeze promotion gates and refreshed live-baseline superiority.",
            "evidence": {
                "candidate_rows": sidecar_counts.get("candidate_rows"),
                "positive_rows": sidecar_counts.get("positive_rows"),
                "sidecar_ready_rows": sidecar_counts.get("sidecar_ready_rows"),
                "controlled_live_test_decision": controlled_live_test_gate.get("decision"),
                "controlled_live_test_counts": controlled_live_test_gate.get("counts"),
                "controlled_live_test_live_baseline": controlled_live_test_gate.get("live_baseline"),
                "continuous_penalty_sidecar_best": continuous_penalty_sidecar_best,
                "continuous_penalty_sidecar_interpretation": continuous_penalty_sidecar_runway.get("interpretation"),
                "near_gate_counts": near_gate_counts,
                "near_gate_closest_strict_target_positive": near_gate_closest_strict,
                "near_gate_interpretation": near_gate_runway.get("interpretation"),
                "closest_gate": sidecar_closest.get("gate"),
                "closest_policy": sidecar_closest.get("policy"),
                "closest_settled": sidecar_closest.get("settled"),
                "closest_net_cents": sidecar_closest.get("net_cents"),
                "closest_simulated_share": sidecar_closest.get("simulated_share"),
                "closest_missing_gates": sidecar_closest.get("missing_gates"),
                "top_net_gate": sidecar_top_net.get("gate"),
                "top_net_policy": sidecar_top_net.get("policy"),
                "top_net_settled": sidecar_top_net.get("settled"),
                "top_net_cents": sidecar_top_net.get("net_cents"),
                "top_net_missing_gates": sidecar_top_net.get("missing_gates"),
                "dual_lane_counts": dual_lane_counts,
                "dual_lane_top_diagnostic": {
                    "primary": (dual_lane_top_diag.get("primary") or {}).get("policy"),
                    "sidecar": (dual_lane_top_diag.get("sidecar") or {}).get("policy"),
                    "union": dual_lane_top_diag.get("union"),
                    "sidecar_add_net_cents": dual_lane_top_diag.get("sidecar_add_net_cents"),
                    "blockers": dual_lane_top_diag.get("blockers"),
                },
                "dual_lane_top_strict_post": {
                    "primary": (dual_lane_top_strict.get("primary") or {}).get("policy"),
                    "sidecar": (dual_lane_top_strict.get("sidecar") or {}).get("policy"),
                    "union": dual_lane_top_strict.get("union"),
                    "sidecar_add_net_cents": dual_lane_top_strict.get("sidecar_add_net_cents"),
                    "blockers": dual_lane_top_strict.get("blockers"),
                },
                "dual_lane_top_confirmation": {
                    "primary": (dual_lane_top_confirmation.get("primary") or {}).get("policy"),
                    "confirmer": (dual_lane_top_confirmation.get("sidecar") or {}).get("policy"),
                    "kept": dual_lane_top_confirmation.get("confirmed"),
                    "same_side_net_cents": (dual_lane_top_confirmation.get("same_side") or {}).get("net_cents"),
                    "omitted_primary_net_cents": (dual_lane_top_confirmation.get("omitted_primary") or {}).get("net_cents"),
                    "blockers": dual_lane_top_confirmation.get("blockers"),
                },
                "dual_lane_top_strict_confirmation": {
                    "primary": (dual_lane_top_strict_confirmation.get("primary") or {}).get("policy"),
                    "confirmer": (dual_lane_top_strict_confirmation.get("sidecar") or {}).get("policy"),
                    "kept": dual_lane_top_strict_confirmation.get("confirmed"),
                    "same_side_net_cents": (dual_lane_top_strict_confirmation.get("same_side") or {}).get("net_cents"),
                    "omitted_primary_net_cents": (dual_lane_top_strict_confirmation.get("omitted_primary") or {}).get("net_cents"),
                    "blockers": dual_lane_top_strict_confirmation.get("blockers"),
                },
                "dual_lane_own_freeze_watch": {
                    "freeze_ts": (dual_lane_own_freeze_watch.get("state") or {}).get("freeze_ts_utc"),
                    "best_summary": dual_lane_own_freeze_best.get("summary"),
                    "best_blockers": dual_lane_own_freeze_best.get("blockers"),
                    "live_ready": dual_lane_own_freeze_best.get("live_ready"),
                    "interpretation": dual_lane_own_freeze_watch.get("interpretation"),
                },
                "dual_lane_same_window_delta_autopsy": {
                    "generated_at_utc": dual_lane_same_window_delta_autopsy.get("generated_at_utc"),
                    "candidate_minus_live_same_markets_cents": dual_lane_same_window_delta_autopsy.get(
                        "candidate_minus_live_same_markets_cents"
                    ),
                    "deficit_rows": dual_lane_same_window_delta_autopsy.get("deficit_rows"),
                    "deficit_cents": dual_lane_same_window_delta_autopsy.get("deficit_cents"),
                    "surplus_rows": dual_lane_same_window_delta_autopsy.get("surplus_rows"),
                    "surplus_cents": dual_lane_same_window_delta_autopsy.get("surplus_cents"),
                    "worst_class": dual_lane_delta_worst,
                    "top_deficits": dual_lane_same_window_delta_autopsy.get("top_deficits"),
                },
                "dual_lane_same_window_sequence_mechanism": {
                    "generated_at_utc": dual_lane_same_window_sequence_mechanism.get("generated_at_utc"),
                    "worst_mechanism": dual_lane_sequence_worst,
                    "mechanism_summary": dual_lane_sequence_mechanisms,
                    "deficit_rows": dual_lane_same_window_sequence_mechanism.get("rows"),
                    "interpretation": dual_lane_same_window_sequence_mechanism.get("interpretation"),
                },
                "dual_lane_state_exposure_sequence_repair": {
                    "generated_at_utc": dual_lane_state_exposure_sequence_repair.get("generated_at_utc"),
                    "best_variant": dual_lane_state_repair_best,
                    "variants": dual_lane_state_exposure_sequence_repair.get("variants"),
                    "interpretation": dual_lane_state_exposure_sequence_repair.get("interpretation"),
                },
                "dual_lane_side_flip_feasibility": {
                    "generated_at_utc": dual_lane_side_flip_feasibility.get("generated_at_utc"),
                    "candidate_side_flip_summary": dual_lane_side_flip_candidate_summary,
                    "candidate_opposite_rescue_summary": dual_lane_side_flip_rescue_summary,
                    "all_live_side_flip_summary": dual_lane_side_flip_feasibility.get("all_live_side_flip_summary"),
                    "blockers": dual_lane_side_flip_feasibility.get("blockers"),
                    "interpretation": dual_lane_side_flip_feasibility.get("interpretation"),
                },
            },
            "next": "Do not live-test sidecars until the controlled live-test gate reports an eligible row. Track the new dual-lane own-freeze watch from its 2026-05-07 birth; it needs >=30 settled rows, 75-90% coverage, <=35% reconstructed share, positive PnL, cushion >=3, and a refreshed live-baseline win before any controlled live-test review.",
        },
        {
            "lane": "control_risk_gate",
            "decision": "do_not_override",
            "candidate": control_risk_top_apparent.get("policy"),
            "why": "Tracker-only blocker lists can make several positive broad rows look blocked only by the global risk stop, but the integrity-merged view shows zero target-coverage rows are actually control-only. Source quality, sample, and full-loss cushion remain real blockers.",
            "evidence": {
                "positive_rows": control_risk_triage_summary.get("positive_rows"),
                "positive_target_rows": control_risk_triage_summary.get("positive_target_rows"),
                "tracker_apparent_control_only_target": control_risk_triage_summary.get("tracker_apparent_control_only_target"),
                "integrity_merged_control_only_target": control_risk_triage_summary.get("integrity_merged_control_only_target"),
                "integrity_merged_control_only_target_strict": control_risk_triage_summary.get("integrity_merged_control_only_target_strict"),
                "risk_stop_reason": control_risk_triage_risk.get("risk_stop_reason"),
                "losing_trades": control_risk_triage_risk.get("losing_trades"),
                "max_drawdown_pct": control_risk_triage_risk.get("max_drawdown_pct"),
                "top_apparent_policy": control_risk_top_apparent.get("policy"),
                "top_apparent_missing": control_risk_top_apparent.get("merged_non_global_missing"),
            },
            "next": "Keep the risk stop as a hard blocker. Repair source quality and full-loss cushion before treating any control-risk-blocked broad row as live-testable.",
        },
        {
            "lane": "combined_entry_stack",
            "decision": "freeze_and_monitor",
            "candidate": "hybrid_veto_plus_early_no / boundary_clock stacks",
            "why": "The combined diagnostic stack can turn the old target window positive at the required coverage, but formal source stress still shows the current best lanes are reconstructed-heavy.",
            "evidence": {
                "diagnostic_best": stack_diag_best.get("candidate"),
                "diagnostic_settled": stack_diag_summary.get("settled"),
                "diagnostic_coverage": stack_diag_summary.get("coverage_pct"),
                "diagnostic_net_cents": stack_diag_summary.get("net_cents"),
                "diagnostic_delta_cents": stack_diag_best.get("delta_vs_target_cents"),
                "diagnostic_reconstructed_share": stack_diag_integrity.get("reconstructed_share"),
                "diagnostic_loss_cushion": stack_diag_integrity.get("full_loss_cushion_estimate"),
                "post_freeze_best": stack_post_best.get("candidate"),
                "post_freeze_settled": stack_post_summary.get("settled"),
                "post_freeze_coverage": stack_post_summary.get("coverage_pct"),
                "post_freeze_net_cents": stack_post_summary.get("net_cents"),
                "post_freeze_reconstructed_share": stack_post_integrity.get("reconstructed_share"),
                "post_freeze_loss_cushion": stack_post_integrity.get("full_loss_cushion_estimate"),
                "promotion_blockers": stack_post_best.get("promotion_blockers"),
                "source_stress_diagnostic_reconstructed_share": stack_source_stress_diag.get("reconstructed_share"),
                "source_stress_diagnostic_clean_rows_needed": stack_source_stress_diag.get("clean_rows_needed_for_source_gate"),
                "source_stress_post_reconstructed_share": stack_source_stress_post.get("reconstructed_share"),
                "source_stress_post_clean_rows_needed": stack_source_stress_post.get("clean_rows_needed_for_source_gate"),
                "source_stress_post_sample_rows_needed": stack_source_stress_post.get("settled_rows_needed_for_sample_gate"),
                "source_stress_post_cushion_cents_needed": stack_source_stress_post.get("net_cents_needed_for_cushion3"),
                "source_stress_post_blockers": stack_source_stress_post.get("stress_blockers"),
                "stress_best_pnl_candidate": stack_stress_best.get("candidate"),
                "stress_best_pnl_net_cents": stack_stress_best.get("net_cents"),
                "stress_best_pnl_reconstructed_share": stack_stress_best.get("reconstructed_share"),
                "stress_watch_candidate": stack_stress_watch.get("candidate"),
                "stress_watch_net_cents": stack_stress_watch.get("net_cents"),
                "stress_watch_reconstructed_share": stack_stress_watch.get("reconstructed_share"),
                "stress_lowest_recon_candidate": stack_stress_lowest_recon.get("candidate"),
                "stress_lowest_recon_net_cents": stack_stress_lowest_recon.get("net_cents"),
                "stress_lowest_recon_share": stack_stress_lowest_recon.get("reconstructed_share"),
                "frontier_diagnostic_best": stack_frontier_diag_best.get("candidate"),
                "frontier_diagnostic_settled": stack_frontier_diag_summary.get("settled"),
                "frontier_diagnostic_coverage": stack_frontier_diag_summary.get("coverage_pct"),
                "frontier_diagnostic_net_cents": stack_frontier_diag_summary.get("net_cents"),
                "frontier_diagnostic_reconstructed_share": stack_frontier_diag_integrity.get("reconstructed_share"),
                "frontier_diagnostic_blockers": stack_frontier_diag_best.get("blockers"),
                "frontier_post_freeze_best": stack_frontier_post_best.get("candidate"),
                "frontier_post_freeze_settled": stack_frontier_post_summary.get("settled"),
                "frontier_post_freeze_coverage": stack_frontier_post_summary.get("coverage_pct"),
                "frontier_post_freeze_net_cents": stack_frontier_post_summary.get("net_cents"),
                "frontier_post_freeze_reconstructed_share": stack_frontier_post_integrity.get("reconstructed_share"),
                "frontier_post_freeze_blockers": stack_frontier_post_best.get("blockers"),
                "dilution_diagnostic_clean_rows_needed": stack_dilution_diag.get("approved_needed_for_recon35"),
                "dilution_diagnostic_max_full_losses_positive": stack_dilution_diag.get("max_full_losses_while_positive"),
                "dilution_post_clean_rows_needed_for_gate": stack_dilution_post.get("future_approved_selected_needed_for_gate"),
                "dilution_post_avg_net_needed_cushion3_cents": stack_dilution_post.get("avg_future_net_needed_cushion3_cents"),
            },
            "next": "Keep the stack as a watch lane, but treat source quality as the active repair target; do not promote from diagnostic P&L until approved-entry forward evidence replaces the reconstructed-heavy slice.",
        },
        {
            "lane": "entry_policy",
            "decision": "monitor_not_promote" if early_is_positive else "downgrade_reject_current_freeze",
            "candidate": "skip_early_no_boundary_decay_repair_calm_geometry",
            "why": (
                "Early-NO remains barely positive at broad coverage with a physical turbulence/decay story, but the edge is too small and source/fragility blockers dominate."
                if early_is_positive
                else "The frozen early-NO repair is broad, but current forward PnL is negative; keep its turbulence/decay tags as failure diagnostics rather than a promotable entry gate."
            ),
            "evidence": {
                "candidate_settled": early_candidate.get("settled"),
                "candidate_coverage": early_candidate.get("coverage_pct"),
                "candidate_net_cents": early_candidate.get("net_cents"),
                "target_net_cents": early_target.get("net_cents"),
                "target_direction_wrong_rows": target_failure_clusters.get("total_direction_wrong_rows"),
                "target_direction_wrong_net_cents": target_failure_clusters.get("total_direction_wrong_net_cents"),
                "target_top_failure_cluster": target_failure_top.get("cluster"),
                "target_top_failure_cluster_rows": target_failure_top.get("rows"),
                "target_top_failure_cluster_net_cents": target_failure_top.get("net_cents"),
                "target_cluster_penalty_freeze_ts": (target_cluster_penalty_watch.get("state") or {}).get("freeze_ts_utc"),
                "target_cluster_penalty_diagnostic_best": target_cluster_penalty_diag_best.get("candidate"),
                "target_cluster_penalty_diagnostic_settled": target_cluster_penalty_diag_summary.get("settled"),
                "target_cluster_penalty_diagnostic_coverage": target_cluster_penalty_diag_summary.get("coverage_pct"),
                "target_cluster_penalty_diagnostic_net_cents": target_cluster_penalty_diag_summary.get("net_cents"),
                "target_cluster_penalty_diagnostic_delta_vs_target_cents": target_cluster_penalty_diag_best.get("delta_vs_target_cents"),
                "target_cluster_penalty_diagnostic_reconstructed_share": target_cluster_penalty_diag_best.get("reconstructed_share"),
                "target_cluster_penalty_diagnostic_blockers": target_cluster_penalty_diag_best.get("blockers"),
                "target_cluster_penalty_post_birth_settled": target_cluster_penalty_post_summary.get("settled"),
                "target_cluster_penalty_post_birth_net_cents": target_cluster_penalty_post_summary.get("net_cents"),
                "target_cluster_penalty_post_birth_blockers": target_cluster_penalty_post_best.get("blockers"),
                "target_cluster_penalty_post_birth_reconstructed_share": target_cluster_penalty_post_source.get("reconstructed_share"),
                "target_cluster_penalty_post_birth_rows_needed": target_cluster_penalty_post_runway.get("future_settled_rows_needed_for_sample"),
                "target_cluster_penalty_post_birth_clean_rows_needed": target_cluster_penalty_post_source.get("future_clean_approved_rows_needed_for_source_gate"),
                "target_cluster_penalty_post_birth_cushion_cents_needed": target_cluster_penalty_post_runway.get("future_net_cents_needed_for_cushion3"),
                "target_cluster_penalty_diagnostic_clean_rows_needed": target_cluster_penalty_diag_source.get("future_clean_approved_rows_needed_for_source_gate"),
                "target_cluster_penalty_post_birth_approved_available": source_feasibility_post_best.get("approved_available_markets"),
                "target_cluster_penalty_post_birth_required_entries": source_feasibility_post_best.get("required_entries_for_75pct_coverage"),
                "target_cluster_penalty_post_birth_min_reconstructed_share": source_feasibility_post_best.get("minimum_reconstructed_share_for_75pct_coverage"),
                "target_cluster_penalty_post_birth_source_feasible": source_feasibility_post_best.get("source_gate_feasible_at_current_denominator"),
                "target_cluster_penalty_diagnostic_source_feasible": source_feasibility_diag_best.get("source_gate_feasible_at_current_denominator"),
                "target_cluster_penalty_post_birth_selected_rejected_net_cents": displacement_post_rejected.get("net_cents"),
                "target_cluster_penalty_post_birth_omitted_approved_net_cents": displacement_post_omitted.get("net_cents"),
                "target_cluster_penalty_post_birth_approved_preferred_net_cents": displacement_post_preferred.get("net_cents"),
                "blockers": early_blockers,
                "warnings": stress_warnings,
            },
            "next": (
                "Do not promote on the current tiny positive edge; require approved-entry/source-quality repair and a full-loss cushion before using as live entry logic."
                if early_is_positive
                else "Do not promote this freeze; mine its losing rows for boundary-turbulence mechanisms and prefer boundary-clock/feature-gate repairs that prove positive forward PnL."
            ),
        },
        {
            "lane": "book_anchor",
            "decision": "watch_frozen_blend",
            "candidate": "book_probability / conditional_book_no_late_discount / book_raw_blend_alpha_0p50",
            "why": "Strict book anchoring stayed uneven, but the smooth book/raw blend gives a physical humility anchor without throwing away raw v28 conviction. It is motivation-only until post-freeze rows settle.",
            "evidence": {
                "approved_raw_brier": approved_book_raw.get("avg_brier"),
                "approved_book_brier_delta": approved_book_book.get("brier_delta_vs_raw"),
                "approved_book_logloss_delta": approved_book_book.get("logloss_delta_vs_raw"),
                "conditional_future_brier_delta": conditional_candidate.get("brier_delta_vs_raw"),
                "conditional_future_logloss_delta": conditional_candidate.get("logloss_delta_vs_raw"),
                "blend_freeze_ts": blend_freeze.get("freeze_ts_utc"),
                "blend_future_settled": blend_future_primary.get("settled"),
                "blend_future_brier_delta": blend_future_primary.get("brier_delta_vs_raw"),
                "blend_future_logloss_delta": blend_future_primary.get("logloss_delta_vs_raw"),
                "blend_prefreeze_settled": blend_prefreeze_primary.get("settled"),
                "blend_prefreeze_brier_delta": blend_prefreeze_primary.get("brier_delta_vs_raw"),
                "blend_prefreeze_logloss_delta": blend_prefreeze_primary.get("logloss_delta_vs_raw"),
                "blend_blockers": approved_book_raw_blend.get("blockers"),
            },
            "next": "Keep book as disagreement/regime context and let the frozen blend earn strict approved-entry forward rows before promotion consideration.",
        },
        {
            "lane": "phi_forgetting",
            "decision": "monitor_as_control",
            "candidate": "phi_half/quarter_shrink_to50",
            "why": "Phi shrink supports the gentle-confidence-shrink mechanism, but it trails the existing physics shrink overall.",
            "evidence": {
                "diagnostic_best": phi_diag.get("overlay"),
                "diagnostic_brier_delta": phi_diag.get("brier_delta_vs_raw"),
                "diagnostic_logloss_delta": phi_diag.get("logloss_delta_vs_raw"),
                "forward_best": phi_forward.get("overlay"),
                "forward_settled": phi_forward.get("settled"),
            },
            "next": "Let frozen rows accumulate; do not prioritize phi over noise_shrink_light unless forward data flips the ranking.",
        },
    ]

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "objective_achieved": goal.get("achieved"),
        "direction": "Pursue exit-policy validation first, with the top-component soft-frontier delayed-recheck plus parent-fill mix as the newest diagnostic blueprint to freeze/watch. Keep hybrid confidence shrink and hybrid-veto as calibration/warning overlays, keep boundary-clock/feature-gate branches in forward watch, and track the cheap-tail plus mid-price size-shrink overlays until strict rows mature.",
        "decisions": decisions,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Current Direction Decision",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Goal achieved: `{report.get('objective_achieved')}`",
        f"- Direction: {report.get('direction')}",
        "",
        "## Decision Ledger",
        "",
        "| lane | decision | candidate | why | next |",
        "|---|---|---|---|---|",
    ]
    for row in report.get("decisions") or []:
        lines.append(
            f"| {row.get('lane')} | `{row.get('decision')}` | `{row.get('candidate')}` | "
            f"{row.get('why')} | {row.get('next')} |"
        )
    lines.extend(["", "## Evidence", ""])
    for row in report.get("decisions") or []:
        lines.append(f"### {row.get('lane')}")
        for key, value in (row.get("evidence") or {}).items():
            lines.append(f"- `{key}`: `{fmt(value)}`")
        lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    report = build_report()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
