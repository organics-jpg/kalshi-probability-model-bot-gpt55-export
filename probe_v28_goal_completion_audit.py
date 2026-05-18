"""Completion audit for the active v28 FV improvement goal.

Research-only; no live bot changes or orders.

This turns the long-running objective into concrete success criteria and checks
the current artifacts against real evidence. It is intentionally strict: the
goal is not complete until a candidate is accurate, profitable, broad enough,
forward-validated, and live-safe by the existing gates.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_goal_completion_audit_latest.json"
OUT_MD = OUT_DIR / "v28_goal_completion_audit_latest.md"

TARGET_SEQ_JSON = OUT_DIR / "v28_target_coverage_fv_sequential_evidence_latest.json"
TARGET_P70_SEQ_JSON = OUT_DIR / "v28_target_coverage_p70_sequential_evidence_latest.json"
TARGET_OVERLAY_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
TARGET_LIVE_EVIDENCE_JSON = OUT_DIR / "v28_target_coverage_fv_live_evidence_audit_latest.json"
TARGET_PROMO_JSON = OUT_DIR / "v28_target_coverage_promotion_audit_latest.json"
TARGET_PRICE_FRICTION_JSON = OUT_DIR / "v28_target_coverage_price_friction_latest.json"
TARGET_FAILURE_CLUSTERS_JSON = OUT_DIR / "v28_target_coverage_failure_clusters_latest.json"
TARGET_CLUSTER_PENALTY_WATCH_JSON = OUT_DIR / "v28_target_coverage_cluster_penalty_watch_latest.json"
TARGET_CLUSTER_PENALTY_RUNWAY_JSON = OUT_DIR / "v28_target_cluster_penalty_runway_latest.json"
TARGET_CLUSTER_PENALTY_SOURCE_FEASIBILITY_JSON = OUT_DIR / "v28_target_cluster_penalty_source_feasibility_latest.json"
TARGET_CLUSTER_PENALTY_SOURCE_DISPLACEMENT_JSON = OUT_DIR / "v28_target_cluster_penalty_source_displacement_latest.json"
FROZEN_APPROVED_ENTRY_BOOK_FV_JSON = OUT_DIR / "v28_frozen_approved_entry_book_fv_latest.json"
FROZEN_APPROVED_ENTRY_BOOK_RAW_BLEND_JSON = OUT_DIR / "v28_frozen_approved_entry_book_raw_blend_latest.json"
FROZEN_CONSERVATIVE_JSON = OUT_DIR / "v28_frozen_target_coverage_conservative_fv_latest.json"
FROZEN_P70_JSON = OUT_DIR / "v28_frozen_target_coverage_p70_fv_latest.json"
FROZEN_P70_EB_JSON = OUT_DIR / "v28_frozen_target_coverage_p70_empirical_bayes_latest.json"
FROZEN_PATH_STATE_P70_JSON = OUT_DIR / "v28_frozen_path_state_p70_fv_latest.json"
FROZEN_BOUNDARY_RECROSS_SHRINK_JSON = OUT_DIR / "v28_frozen_boundary_recross_shrink_fv_latest.json"
FROZEN_BOUNDARY_TEMPERATURE_FV_JSON = OUT_DIR / "v28_frozen_boundary_temperature_fv_latest.json"
FROZEN_BOUNDARY_ENERGY_FV_ENTRY_JSON = OUT_DIR / "v28_frozen_boundary_energy_fv_entry_latest.json"
FROZEN_EARLY_NO_BOUNDARY_FV_ENTRY_JSON = OUT_DIR / "v28_frozen_early_no_boundary_fv_entry_latest.json"
FROZEN_MID_EDGE_FALSE_CONVICTION_FV_JSON = OUT_DIR / "v28_frozen_mid_edge_false_conviction_fv_latest.json"
FROZEN_BOUNDARY_CLOCK_FV_JSON = OUT_DIR / "v28_frozen_boundary_clock_fv_overlay_latest.json"
FROZEN_SIDE_ASYMMETRY_FV_JSON = OUT_DIR / "v28_frozen_side_asymmetry_fv_overlay_latest.json"
FROZEN_EDGE_PHASE_SHRINK_JSON = OUT_DIR / "v28_frozen_edge_phase_shrink_fv_latest.json"
FROZEN_EDGE_PHASE_EDGE_GATE_JSON = OUT_DIR / "v28_frozen_edge_phase_edge_gate_latest.json"
FROZEN_EDGE_GATE_OPPOSITE_JSON = OUT_DIR / "v28_frozen_edge_gate_opposite_side_latest.json"
FROZEN_EARLY_NO_BOUNDARY_DECAY_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_early_no_boundary_decay_repair_entry_latest.json"
FROZEN_FALSE_CONVICTION_APPROVED_REPAIR_JSON = OUT_DIR / "v28_frozen_false_conviction_approved_repair_latest.json"
FROZEN_MID_EDGE_BOUNDARY_DECEPTION_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_mid_edge_boundary_deception_repair_entry_latest.json"
FROZEN_LOW_RECROSS_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_low_recross_repair_entry_latest.json"
FROZEN_HIGH_RAW_P_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_high_raw_p_repair_entry_latest.json"
FROZEN_P50_BOOK_EDGE_ENTRY_JSON = OUT_DIR / "v28_frozen_p50_book_edge_entry_latest.json"
FROZEN_BOOK_PLUS05_ENTRY_JSON = OUT_DIR / "v28_frozen_book_plus05_entry_latest.json"
FROZEN_BOOK_PLUS05_NO_CHEAP_YES_ENTRY_JSON = OUT_DIR / "v28_frozen_book_plus05_no_cheap_yes_entry_latest.json"
FROZEN_BOUNDARY_CLOCK_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_boundary_clock_repair_entry_latest.json"
FROZEN_BOUNDARY_CLOCK_FV_ENTRY_BRIDGE_JSON = OUT_DIR / "v28_frozen_boundary_clock_fv_entry_bridge_latest.json"
BOUNDARY_CLOCK_SOURCE_STRESS_JSON = OUT_DIR / "v28_boundary_clock_source_stress_latest.json"
BOUNDARY_CLOCK_APPROVED_FRONTIER_JSON = OUT_DIR / "v28_boundary_clock_approved_oracle_frontier_latest.json"
BOUNDARY_CLOCK_FEATURE_GATE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
BOUNDARY_CLOCK_FEATURE_GATE_RUNWAY_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_runway_latest.json"
BOUNDARY_CLOCK_FEATURE_GATE_FAILURE_MODES_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_failure_modes_latest.json"
BOUNDARY_CLOCK_FEATURE_GATE_LOSS_ANALOG_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_loss_analog_monitor_latest.json"
BOUNDARY_CLOCK_FEATURE_GATE_ROW_LEDGER_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_row_ledger_latest.json"
BOUNDARY_CLOCK_FEATURE_GATE_COVERAGE_RECOVERY_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_coverage_recovery_latest.json"
BOUNDARY_CLOCK_FEATURE_GATE_SOURCE_DENOMINATOR_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_source_denominator_audit_latest.json"
BOUNDARY_CLOCK_FEATURE_GATE_CHEAP_TAIL_RISK_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_cheap_tail_risk_audit_latest.json"
BOUNDARY_CLOCK_FEATURE_GATE_COVERAGE_SOURCE_FRONTIER_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_coverage_source_frontier_latest.json"
FEATURE_GATE_SOURCE_FEASIBILITY_BOUND_JSON = OUT_DIR / "v28_feature_gate_source_feasibility_bound_latest.json"
BOUNDARY_CLOCK_FEATURE_GATE_FRONTIER_RUNWAY_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_frontier_runway_latest.json"
BOUNDARY_CLOCK_FEATURE_GATE_FRONTIER_MECHANISM_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_frontier_mechanism_latest.json"
BOUNDARY_CLOCK_FEATURE_GATE_OUTLIER_STRESS_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_outlier_stress_latest.json"
BOUNDARY_CLOCK_FEATURE_GATE_CLEAN_BROAD_FRONTIER_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_clean_broad_frontier_watch_latest.json"
FEATURE_GATE_FRONTIER_DRIFT_AUDIT_JSON = OUT_DIR / "v28_feature_gate_frontier_drift_audit_latest.json"
BOUNDARY_CLOCK_FEATURE_GATE_SOFT_FRONTIER_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_soft_frontier_watch_latest.json"
SOFT_FRONTIER_POST_BIRTH_FAILURE_DRILLDOWN_JSON = OUT_DIR / "v28_soft_frontier_post_birth_failure_drilldown_latest.json"
BOUNDARY_CLOCK_FEATURE_GATE_SOFT_FRONTIER_EXIT_STACK_JSON = OUT_DIR / "v28_frozen_feature_gate_soft_frontier_exit_stack_latest.json"
FEATURE_GATE_CHEAP_TAIL_SHRINK_WATCH_JSON = OUT_DIR / "v28_frozen_feature_gate_cheap_tail_shrink_watch_latest.json"
SOFT_FRONTIER_SIZE_SHRINK_JSON = OUT_DIR / "v28_soft_frontier_size_shrink_portfolio_latest.json"
SOFT_FRONTIER_MIDPRICE_BOUNDARY_SHRINK_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_shrink_latest.json"
SOFT_FRONTIER_MIDPRICE_BOUNDARY_EXIT_STACK_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_exit_stack_latest.json"
SOFT_FRONTIER_MIDPRICE_BOUNDARY_EXIT_STACK_RUNWAY_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_exit_stack_runway_latest.json"
BOUNDARY_CLOCK_FEATURE_GATE_ASK_FLOOR_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_ask_floor_mechanism_latest.json"
BOUNDARY_CLOCK_FEATURE_GATE_CONTINUOUS_PENALTY_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_continuous_penalty_latest.json"
BOUNDARY_CLOCK_FEATURE_GATE_CONTINUOUS_PENALTY_STRESS_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_continuous_penalty_stress_latest.json"
BOUNDARY_CLOCK_FEATURE_GATE_RESIDUAL_LOSS_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_residual_loss_mechanism_latest.json"
FROZEN_WEAK_REVERSAL_RESIDUAL_REPAIR_JSON = OUT_DIR / "v28_frozen_weak_reversal_residual_repair_latest.json"
FROZEN_WEAK_REVERSAL_RESIDUAL_FV_SHRINK_JSON = OUT_DIR / "v28_frozen_weak_reversal_residual_fv_shrink_latest.json"
FROZEN_NO_MID_EDGE_FV_JSON = OUT_DIR / "v28_frozen_no_mid_edge_fv_latest.json"
FROZEN_EARLY_BOUNDARY_WAIT_REPAIR_JSON = OUT_DIR / "v28_frozen_early_boundary_wait_repair_latest.json"
FROZEN_EARLY_BOUNDARY_OPPOSITE_WAIT_REPAIR_JSON = OUT_DIR / "v28_frozen_early_boundary_opposite_wait_repair_latest.json"
PHI_FORGETTING_FV_JSON = OUT_DIR / "v28_phi_forgetting_fv_candidates_latest.json"
CONFIDENCE_SHRINK_BAKEOFF_JSON = OUT_DIR / "v28_confidence_shrink_schedule_bakeoff_latest.json"
HYBRID_CONFIDENCE_SHRINK_JSON = OUT_DIR / "v28_hybrid_confidence_shrink_fv_latest.json"
TARGET_SURFACE_HYBRID_JSON = OUT_DIR / "v28_target_surface_hybrid_fv_latest.json"
TARGET_HYBRID_VETO_REPAIR_JSON = OUT_DIR / "v28_target_hybrid_veto_repair_latest.json"
HYBRID_BOUNDARY_ENTRY_STACK_JSON = OUT_DIR / "v28_hybrid_boundary_entry_stack_latest.json"
HYBRID_BOUNDARY_ENTRY_STACK_SOURCE_STRESS_JSON = OUT_DIR / "v28_hybrid_boundary_entry_stack_source_stress_latest.json"
HYBRID_BOUNDARY_ENTRY_STACK_STRESS_JSON = OUT_DIR / "v28_hybrid_boundary_entry_stack_stress_latest.json"
HYBRID_BOUNDARY_SOURCE_FRONTIER_JSON = OUT_DIR / "v28_hybrid_boundary_source_frontier_latest.json"
HYBRID_BOUNDARY_SOURCE_DILUTION_JSON = OUT_DIR / "v28_hybrid_boundary_source_dilution_runway_latest.json"
FROZEN_EXIT_REDUCE_SUPPRESSION_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
EXIT_REDUCE_SUPPRESSION_RISK_LEDGER_JSON = OUT_DIR / "v28_exit_reduce_suppression_risk_ledger_latest.json"
EXIT_REDUCE_BLOCKER_DECISION_JSON = OUT_DIR / "v28_exit_reduce_blocker_decision_latest.json"
EXIT_REDUCE_DRIFT_GUARD_WATCH_JSON = OUT_DIR / "v28_frozen_exit_reduce_drift_guard_watch_latest.json"
EXIT_REDUCE_LOSS_CONTROL_SIGNATURE_JSON = OUT_DIR / "v28_exit_reduce_loss_control_signature_latest.json"
EXIT_REDUCE_LOSS_CONTROL_ACTIONABILITY_JSON = OUT_DIR / "v28_exit_reduce_loss_control_actionability_latest.json"
EXIT_REDUCE_REFINEMENT_JSON = OUT_DIR / "v28_frozen_exit_reduce_loss_control_refinement_latest.json"
EXIT_REDUCE_DEPTH_GATE_JSON = OUT_DIR / "v28_frozen_exit_reduce_depth_gate_latest.json"
EXIT_REDUCE_DEPTH_GATE_RUNWAY_JSON = OUT_DIR / "v28_exit_reduce_depth_gate_runway_latest.json"
EXIT_REDUCE_DEPTH_GATE_OPPORTUNITY_JSON = OUT_DIR / "v28_exit_reduce_depth_gate_opportunity_latest.json"
EXIT_REDUCE_OBSERVABLE_LOSS_CONTROL_JSON = OUT_DIR / "v28_frozen_exit_reduce_observable_loss_control_watch_latest.json"
EXIT_REDUCE_OBSERVABLE_LOSS_CONTROL_OPPORTUNITY_JSON = OUT_DIR / "v28_exit_reduce_observable_loss_control_opportunity_latest.json"
EXIT_POLICY_LOSS_CHURN_JSON = OUT_DIR / "v28_exit_policy_loss_churn_effect_latest.json"
LIVE_LOSS_ESCAPE_JSON = OUT_DIR / "v28_live_loss_escape_analysis_latest.json"
COLLAPSE_SUPPRESS_SHADOW_JSON = OUT_DIR / "live_v28_collapse_suppress_shadow_monitor_latest.json"
COLLAPSE_REENTRY_JSON = OUT_DIR / "v28_live_collapse_reentry_registry_latest.json"
EXIT_REDUCE_GEOMETRY_SUPPRESSION_JSON = OUT_DIR / "v28_exit_reduce_geometry_suppression_latest.json"
FROZEN_EXIT_REDUCE_GEOMETRY_SUPPRESSION_JSON = OUT_DIR / "v28_frozen_exit_reduce_geometry_suppression_latest.json"
EXIT_REDUCE_GEOMETRY_OPPORTUNITY_JSON = OUT_DIR / "v28_exit_reduce_geometry_opportunity_latest.json"
FROZEN_EXIT_REDUCE_GEOMETRY_RELAXED_WATCH_JSON = OUT_DIR / "v28_frozen_exit_reduce_geometry_relaxed_watch_latest.json"
EXIT_BOOK_GAP_LOSS_GUARD_OPPORTUNITY_JSON = OUT_DIR / "v28_exit_book_gap_loss_guard_opportunity_latest.json"
EXIT_BOOK_GAP_VALUE_ONLY_OPPORTUNITY_JSON = OUT_DIR / "v28_exit_book_gap_value_only_opportunity_latest.json"
EXIT_LOSS_GUARD_V1_V2_RUNWAY_JSON = OUT_DIR / "v28_exit_loss_guard_v1_v2_runway_latest.json"
EXIT_LOSS_GUARD_V1_V2_V3_CONTRAST_JSON = OUT_DIR / "v28_exit_loss_guard_v1_v2_v3_contrast_latest.json"
EXIT_STRICT_FAILURE_DRILLDOWN_JSON = OUT_DIR / "v28_exit_policy_strict_failure_drilldown_latest.json"
FROZEN_EXIT_BOOK_GAP_LOSS_GUARD_V3_JSON = OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v3_latest.json"
EXIT_BOOK_GAP_LOSS_GUARD_V3_OPPORTUNITY_JSON = OUT_DIR / "v28_exit_book_gap_loss_guard_v3_opportunity_latest.json"
FROZEN_EXIT_VALUE_REDUCE_DEPTH_COMPOSITE_JSON = OUT_DIR / "v28_frozen_exit_value_reduce_depth_composite_latest.json"
EXIT_VALUE_REDUCE_DEPTH_OPPORTUNITY_JSON = OUT_DIR / "v28_exit_value_reduce_depth_opportunity_latest.json"
FROZEN_FV_BRIDGE_EXIT_GEOMETRY_STACK_JSON = OUT_DIR / "v28_frozen_fv_bridge_exit_geometry_stack_latest.json"
FROZEN_FV_BRIDGE_EXIT_COMBO_STACK_JSON = OUT_DIR / "v28_frozen_fv_bridge_exit_combo_stack_latest.json"
LIVE_READY_JSON = OUT_DIR / "v28_live_trade_readiness_latest.json"
ANTI_OVERFIT_JSON = OUT_DIR / "v28_anti_overfit_freeze_audit_latest.json"
WATCHLIST_JSON = OUT_DIR / "v28_candidate_watchlist_latest.json"
CANDIDATE_INTEGRITY_SCORECARD_JSON = OUT_DIR / "v28_candidate_integrity_scorecard_latest.json"
STRICT_FORWARD_LEADERBOARD_JSON = OUT_DIR / "v28_strict_forward_candidate_leaderboard_latest.json"
FALSE_CONVICTION_FAMILY_SCORECARD_JSON = OUT_DIR / "v28_false_conviction_family_scorecard_latest.json"
CANDIDATE_REGISTRY_COVERAGE_JSON = OUT_DIR / "v28_candidate_registry_coverage_audit_latest.json"
STATUS_JSON = OUT_DIR / "v28_reactivated_shadow_status_latest.json"


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


def check(name: str, passed: bool, actual: Any, required: str, evidence: Path, note: str) -> dict[str, Any]:
    return {
        "name": name,
        "passed": bool(passed),
        "actual": actual,
        "required": required,
        "evidence": str(evidence),
        "note": note,
    }


def build_report() -> dict[str, Any]:
    target_seq = load_json(TARGET_SEQ_JSON)
    target_p70_seq = load_json(TARGET_P70_SEQ_JSON)
    target_overlay = load_json(TARGET_OVERLAY_JSON)
    target_live_evidence = load_json(TARGET_LIVE_EVIDENCE_JSON)
    target_promo = load_json(TARGET_PROMO_JSON)
    target_price_friction = load_json(TARGET_PRICE_FRICTION_JSON)
    target_failure_clusters = load_json(TARGET_FAILURE_CLUSTERS_JSON)
    target_cluster_penalty_watch = load_json(TARGET_CLUSTER_PENALTY_WATCH_JSON)
    target_cluster_penalty_runway = load_json(TARGET_CLUSTER_PENALTY_RUNWAY_JSON)
    target_cluster_penalty_source_feasibility = load_json(TARGET_CLUSTER_PENALTY_SOURCE_FEASIBILITY_JSON)
    target_cluster_penalty_source_displacement = load_json(TARGET_CLUSTER_PENALTY_SOURCE_DISPLACEMENT_JSON)
    frozen_approved_entry_book_fv = load_json(FROZEN_APPROVED_ENTRY_BOOK_FV_JSON)
    frozen_approved_entry_book_raw_blend = load_json(FROZEN_APPROVED_ENTRY_BOOK_RAW_BLEND_JSON)
    frozen_conservative = load_json(FROZEN_CONSERVATIVE_JSON)
    frozen_p70 = load_json(FROZEN_P70_JSON)
    frozen_p70_eb = load_json(FROZEN_P70_EB_JSON)
    frozen_path_state_p70 = load_json(FROZEN_PATH_STATE_P70_JSON)
    frozen_boundary_recross = load_json(FROZEN_BOUNDARY_RECROSS_SHRINK_JSON)
    frozen_boundary_temperature = load_json(FROZEN_BOUNDARY_TEMPERATURE_FV_JSON)
    frozen_boundary_energy_fv_entry = load_json(FROZEN_BOUNDARY_ENERGY_FV_ENTRY_JSON)
    frozen_early_no_boundary_fv_entry = load_json(FROZEN_EARLY_NO_BOUNDARY_FV_ENTRY_JSON)
    frozen_mid_edge_false_conviction = load_json(FROZEN_MID_EDGE_FALSE_CONVICTION_FV_JSON)
    frozen_boundary_clock_fv = load_json(FROZEN_BOUNDARY_CLOCK_FV_JSON)
    frozen_side_asymmetry_fv = load_json(FROZEN_SIDE_ASYMMETRY_FV_JSON)
    frozen_edge_phase = load_json(FROZEN_EDGE_PHASE_SHRINK_JSON)
    frozen_edge_phase_gate = load_json(FROZEN_EDGE_PHASE_EDGE_GATE_JSON)
    frozen_edge_gate_opposite = load_json(FROZEN_EDGE_GATE_OPPOSITE_JSON)
    frozen_early_no_boundary_decay_repair = load_json(FROZEN_EARLY_NO_BOUNDARY_DECAY_REPAIR_ENTRY_JSON)
    frozen_false_conviction_approved_repair = load_json(FROZEN_FALSE_CONVICTION_APPROVED_REPAIR_JSON)
    frozen_mid_edge_boundary_deception_repair = load_json(FROZEN_MID_EDGE_BOUNDARY_DECEPTION_REPAIR_ENTRY_JSON)
    frozen_low_recross_repair = load_json(FROZEN_LOW_RECROSS_REPAIR_ENTRY_JSON)
    frozen_high_raw_p_repair = load_json(FROZEN_HIGH_RAW_P_REPAIR_ENTRY_JSON)
    frozen_p50_book_edge_entry = load_json(FROZEN_P50_BOOK_EDGE_ENTRY_JSON)
    frozen_book_plus05_entry = load_json(FROZEN_BOOK_PLUS05_ENTRY_JSON)
    frozen_book_plus05_no_cheap_yes_entry = load_json(FROZEN_BOOK_PLUS05_NO_CHEAP_YES_ENTRY_JSON)
    frozen_boundary_clock_repair = load_json(FROZEN_BOUNDARY_CLOCK_REPAIR_ENTRY_JSON)
    frozen_boundary_clock_fv_entry_bridge = load_json(FROZEN_BOUNDARY_CLOCK_FV_ENTRY_BRIDGE_JSON)
    boundary_clock_source_stress = load_json(BOUNDARY_CLOCK_SOURCE_STRESS_JSON)
    boundary_clock_approved_frontier = load_json(BOUNDARY_CLOCK_APPROVED_FRONTIER_JSON)
    boundary_clock_feature_gate = load_json(BOUNDARY_CLOCK_FEATURE_GATE_JSON)
    boundary_clock_feature_gate_runway = load_json(BOUNDARY_CLOCK_FEATURE_GATE_RUNWAY_JSON)
    boundary_clock_feature_gate_failure_modes = load_json(BOUNDARY_CLOCK_FEATURE_GATE_FAILURE_MODES_JSON)
    boundary_clock_feature_gate_loss_analog = load_json(BOUNDARY_CLOCK_FEATURE_GATE_LOSS_ANALOG_JSON)
    boundary_clock_feature_gate_row_ledger = load_json(BOUNDARY_CLOCK_FEATURE_GATE_ROW_LEDGER_JSON)
    boundary_clock_feature_gate_coverage_recovery = load_json(BOUNDARY_CLOCK_FEATURE_GATE_COVERAGE_RECOVERY_JSON)
    boundary_clock_feature_gate_source_denominator = load_json(BOUNDARY_CLOCK_FEATURE_GATE_SOURCE_DENOMINATOR_JSON)
    boundary_clock_feature_gate_cheap_tail = load_json(BOUNDARY_CLOCK_FEATURE_GATE_CHEAP_TAIL_RISK_JSON)
    boundary_clock_feature_gate_coverage_source_frontier = load_json(BOUNDARY_CLOCK_FEATURE_GATE_COVERAGE_SOURCE_FRONTIER_JSON)
    feature_gate_source_feasibility_bound = load_json(FEATURE_GATE_SOURCE_FEASIBILITY_BOUND_JSON)
    boundary_clock_feature_gate_frontier_runway = load_json(BOUNDARY_CLOCK_FEATURE_GATE_FRONTIER_RUNWAY_JSON)
    boundary_clock_feature_gate_frontier_mechanism = load_json(BOUNDARY_CLOCK_FEATURE_GATE_FRONTIER_MECHANISM_JSON)
    boundary_clock_feature_gate_outlier_stress = load_json(BOUNDARY_CLOCK_FEATURE_GATE_OUTLIER_STRESS_JSON)
    boundary_clock_feature_gate_clean_broad_frontier = load_json(BOUNDARY_CLOCK_FEATURE_GATE_CLEAN_BROAD_FRONTIER_JSON)
    feature_gate_frontier_drift_audit = load_json(FEATURE_GATE_FRONTIER_DRIFT_AUDIT_JSON)
    boundary_clock_feature_gate_soft_frontier = load_json(BOUNDARY_CLOCK_FEATURE_GATE_SOFT_FRONTIER_JSON)
    soft_frontier_post_birth_failure_drilldown = load_json(SOFT_FRONTIER_POST_BIRTH_FAILURE_DRILLDOWN_JSON)
    boundary_clock_feature_gate_soft_frontier_exit_stack = load_json(BOUNDARY_CLOCK_FEATURE_GATE_SOFT_FRONTIER_EXIT_STACK_JSON)
    feature_gate_cheap_tail_shrink_watch = load_json(FEATURE_GATE_CHEAP_TAIL_SHRINK_WATCH_JSON)
    soft_frontier_size_shrink = load_json(SOFT_FRONTIER_SIZE_SHRINK_JSON)
    soft_frontier_midprice_boundary_shrink = load_json(SOFT_FRONTIER_MIDPRICE_BOUNDARY_SHRINK_JSON)
    soft_frontier_midprice_boundary_exit_stack = load_json(SOFT_FRONTIER_MIDPRICE_BOUNDARY_EXIT_STACK_JSON)
    soft_frontier_midprice_boundary_exit_stack_runway = load_json(SOFT_FRONTIER_MIDPRICE_BOUNDARY_EXIT_STACK_RUNWAY_JSON)
    boundary_clock_feature_gate_ask_floor = load_json(BOUNDARY_CLOCK_FEATURE_GATE_ASK_FLOOR_JSON)
    boundary_clock_feature_gate_continuous_penalty = load_json(BOUNDARY_CLOCK_FEATURE_GATE_CONTINUOUS_PENALTY_JSON)
    boundary_clock_feature_gate_continuous_penalty_stress = load_json(BOUNDARY_CLOCK_FEATURE_GATE_CONTINUOUS_PENALTY_STRESS_JSON)
    boundary_clock_feature_gate_residual_loss = load_json(BOUNDARY_CLOCK_FEATURE_GATE_RESIDUAL_LOSS_JSON)
    frozen_weak_reversal_residual_repair = load_json(FROZEN_WEAK_REVERSAL_RESIDUAL_REPAIR_JSON)
    frozen_weak_reversal_residual_fv_shrink = load_json(FROZEN_WEAK_REVERSAL_RESIDUAL_FV_SHRINK_JSON)
    frozen_no_mid_edge_fv = load_json(FROZEN_NO_MID_EDGE_FV_JSON)
    frozen_early_boundary_wait_repair = load_json(FROZEN_EARLY_BOUNDARY_WAIT_REPAIR_JSON)
    frozen_early_boundary_opposite_wait_repair = load_json(FROZEN_EARLY_BOUNDARY_OPPOSITE_WAIT_REPAIR_JSON)
    phi_forgetting_fv = load_json(PHI_FORGETTING_FV_JSON)
    confidence_shrink_bakeoff = load_json(CONFIDENCE_SHRINK_BAKEOFF_JSON)
    hybrid_confidence_shrink = load_json(HYBRID_CONFIDENCE_SHRINK_JSON)
    target_surface_hybrid = load_json(TARGET_SURFACE_HYBRID_JSON)
    target_hybrid_veto_repair = load_json(TARGET_HYBRID_VETO_REPAIR_JSON)
    hybrid_boundary_entry_stack = load_json(HYBRID_BOUNDARY_ENTRY_STACK_JSON)
    hybrid_boundary_entry_stack_source_stress = load_json(HYBRID_BOUNDARY_ENTRY_STACK_SOURCE_STRESS_JSON)
    hybrid_boundary_entry_stack_stress = load_json(HYBRID_BOUNDARY_ENTRY_STACK_STRESS_JSON)
    hybrid_boundary_source_frontier = load_json(HYBRID_BOUNDARY_SOURCE_FRONTIER_JSON)
    hybrid_boundary_source_dilution = load_json(HYBRID_BOUNDARY_SOURCE_DILUTION_JSON)
    frozen_exit_reduce_suppression = load_json(FROZEN_EXIT_REDUCE_SUPPRESSION_JSON)
    exit_reduce_risk_ledger = load_json(EXIT_REDUCE_SUPPRESSION_RISK_LEDGER_JSON)
    exit_reduce_blocker_decision = load_json(EXIT_REDUCE_BLOCKER_DECISION_JSON)
    exit_reduce_drift_guard_watch = load_json(EXIT_REDUCE_DRIFT_GUARD_WATCH_JSON)
    exit_reduce_signature = load_json(EXIT_REDUCE_LOSS_CONTROL_SIGNATURE_JSON)
    exit_reduce_actionability = load_json(EXIT_REDUCE_LOSS_CONTROL_ACTIONABILITY_JSON)
    exit_reduce_refinement = load_json(EXIT_REDUCE_REFINEMENT_JSON)
    exit_reduce_depth_gate = load_json(EXIT_REDUCE_DEPTH_GATE_JSON)
    exit_reduce_depth_gate_runway = load_json(EXIT_REDUCE_DEPTH_GATE_RUNWAY_JSON)
    exit_reduce_depth_gate_opportunity = load_json(EXIT_REDUCE_DEPTH_GATE_OPPORTUNITY_JSON)
    exit_reduce_observable_loss_control = load_json(EXIT_REDUCE_OBSERVABLE_LOSS_CONTROL_JSON)
    exit_reduce_observable_loss_control_opportunity = load_json(EXIT_REDUCE_OBSERVABLE_LOSS_CONTROL_OPPORTUNITY_JSON)
    exit_policy_loss_churn = load_json(EXIT_POLICY_LOSS_CHURN_JSON)
    live_loss_escape_analysis = load_json(LIVE_LOSS_ESCAPE_JSON)
    collapse_suppress_shadow = load_json(COLLAPSE_SUPPRESS_SHADOW_JSON)
    collapse_reentry_registry = load_json(COLLAPSE_REENTRY_JSON)
    exit_reduce_geometry = load_json(EXIT_REDUCE_GEOMETRY_SUPPRESSION_JSON)
    frozen_exit_reduce_geometry = load_json(FROZEN_EXIT_REDUCE_GEOMETRY_SUPPRESSION_JSON)
    exit_reduce_geometry_opportunity = load_json(EXIT_REDUCE_GEOMETRY_OPPORTUNITY_JSON)
    frozen_exit_reduce_geometry_relaxed_watch = load_json(FROZEN_EXIT_REDUCE_GEOMETRY_RELAXED_WATCH_JSON)
    exit_book_gap_loss_guard_opportunity = load_json(EXIT_BOOK_GAP_LOSS_GUARD_OPPORTUNITY_JSON)
    exit_book_gap_value_only_opportunity = load_json(EXIT_BOOK_GAP_VALUE_ONLY_OPPORTUNITY_JSON)
    exit_loss_guard_v1_v2_runway = load_json(EXIT_LOSS_GUARD_V1_V2_RUNWAY_JSON)
    exit_loss_guard_v1_v2_v3_contrast = load_json(EXIT_LOSS_GUARD_V1_V2_V3_CONTRAST_JSON)
    exit_strict_failure_drilldown = load_json(EXIT_STRICT_FAILURE_DRILLDOWN_JSON)
    frozen_exit_book_gap_loss_guard_v3 = load_json(FROZEN_EXIT_BOOK_GAP_LOSS_GUARD_V3_JSON)
    exit_book_gap_loss_guard_v3_opportunity = load_json(EXIT_BOOK_GAP_LOSS_GUARD_V3_OPPORTUNITY_JSON)
    frozen_exit_value_reduce_depth_composite = load_json(FROZEN_EXIT_VALUE_REDUCE_DEPTH_COMPOSITE_JSON)
    exit_value_reduce_depth_opportunity = load_json(EXIT_VALUE_REDUCE_DEPTH_OPPORTUNITY_JSON)
    frozen_fv_bridge_exit_geometry_stack = load_json(FROZEN_FV_BRIDGE_EXIT_GEOMETRY_STACK_JSON)
    frozen_fv_bridge_exit_combo_stack = load_json(FROZEN_FV_BRIDGE_EXIT_COMBO_STACK_JSON)
    live_ready = load_json(LIVE_READY_JSON)
    anti = load_json(ANTI_OVERFIT_JSON)
    candidate_integrity = load_json(CANDIDATE_INTEGRITY_SCORECARD_JSON)
    strict_forward_leaderboard = load_json(STRICT_FORWARD_LEADERBOARD_JSON)
    false_conviction_family = load_json(FALSE_CONVICTION_FAMILY_SCORECARD_JSON)
    candidate_registry_coverage = load_json(CANDIDATE_REGISTRY_COVERAGE_JSON)
    status = load_json(STATUS_JSON)

    target_coverage = as_float(target_seq.get("coverage_pct"))
    target_settled = int(as_float(target_seq.get("settled_rows")) or 0)
    target_net = as_float(target_seq.get("net_cents_after_entry_fee"))
    brier = target_seq.get("brier") or {}
    logloss = target_seq.get("logloss") or {}
    brier_p95 = as_float((brier.get("bootstrap") or {}).get("p95"))
    logloss_p95 = as_float((logloss.get("bootstrap") or {}).get("p95"))
    p70_brier = target_p70_seq.get("brier") or {}
    p70_logloss = target_p70_seq.get("logloss") or {}
    p70_brier_p95 = as_float((p70_brier.get("bootstrap") or {}).get("p95"))
    p70_logloss_p95 = as_float((p70_logloss.get("bootstrap") or {}).get("p95"))
    p70_settled = int(as_float(target_p70_seq.get("settled_rows")) or 0)
    target_overlay_forward = target_overlay.get("forward") if isinstance(target_overlay.get("forward"), list) else []
    current_overlay_best = target_overlay_forward[0] if target_overlay_forward else {}
    current_overlay_entries = int(as_float(current_overlay_best.get("entries")) or 0)
    current_overlay_settled = int(as_float(current_overlay_best.get("settled")) or 0)
    current_overlay_coverage = as_float(current_overlay_best.get("coverage_pct"))
    current_overlay_net = as_float(current_overlay_best.get("net_cents_after_entry_fee"))
    current_overlay_brier_delta = as_float(current_overlay_best.get("brier_delta_vs_raw"))
    current_overlay_logloss_delta = as_float(current_overlay_best.get("logloss_delta_vs_raw"))
    approved_entry_rows = int(as_float(target_live_evidence.get("approved_entry_rows")) or 0)
    simulated_share = as_float(target_live_evidence.get("simulated_share"))
    live_evidence_blockers = target_live_evidence.get("blockers") if isinstance(target_live_evidence.get("blockers"), list) else []
    price_summary = target_price_friction.get("summary") or {}
    price_tags = target_price_friction.get("tag_rollups") if isinstance(target_price_friction.get("tag_rollups"), list) else []
    worst_price_tag = price_tags[0] if price_tags else {}
    price_rows = int(as_float(price_summary.get("settled")) or 0)
    price_net = as_float(price_summary.get("net_cents"))
    failure_clusters = target_failure_clusters.get("clusters") if isinstance(target_failure_clusters.get("clusters"), list) else []
    top_failure_cluster = failure_clusters[0] if failure_clusters else {}
    cluster_penalty_lanes = target_cluster_penalty_watch.get("lanes") if isinstance(target_cluster_penalty_watch.get("lanes"), list) else []
    cluster_penalty_diag = next((row for row in cluster_penalty_lanes if row.get("lane") == "diagnostic_target_window"), {})
    cluster_penalty_post = next((row for row in cluster_penalty_lanes if row.get("lane") == "post_cluster_penalty_birth"), {})
    cluster_penalty_diag_best = (cluster_penalty_diag.get("variants") or [{}])[0]
    cluster_penalty_post_best = (cluster_penalty_post.get("variants") or [{}])[0]
    cluster_penalty_diag_summary = cluster_penalty_diag_best.get("candidate_summary") or {}
    cluster_penalty_post_summary = cluster_penalty_post_best.get("candidate_summary") or {}
    cluster_penalty_post_runway = target_cluster_penalty_runway.get("post_birth_runway") or {}
    cluster_penalty_diag_runway = target_cluster_penalty_runway.get("diagnostic_runway") or {}
    cluster_penalty_post_source_runway = cluster_penalty_post_runway.get("source_runway") or {}
    cluster_penalty_diag_source_runway = cluster_penalty_diag_runway.get("source_runway") or {}
    source_feasibility_lanes = target_cluster_penalty_source_feasibility.get("lanes") or []
    source_feasibility_post = next((row for row in source_feasibility_lanes if row.get("lane") == "post_cluster_penalty_birth"), {})
    source_feasibility_diag = next((row for row in source_feasibility_lanes if row.get("lane") == "diagnostic_target_window"), {})
    source_feasibility_post_best = source_feasibility_post.get("best") or {}
    source_feasibility_diag_best = source_feasibility_diag.get("best") or {}
    displacement_lanes = target_cluster_penalty_source_displacement.get("lanes") or []
    displacement_post = next((row for row in displacement_lanes if row.get("lane") == "post_cluster_penalty_birth"), {})
    displacement_diag = next((row for row in displacement_lanes if row.get("lane") == "diagnostic_target_window"), {})
    displacement_post_best = displacement_post.get("best") or {}
    displacement_diag_best = displacement_diag.get("best") or {}
    displacement_post_rejected = displacement_post_best.get("selected_rejected_summary") or {}
    displacement_post_omitted = displacement_post_best.get("omitted_approved_summary") or {}
    displacement_post_preferred = displacement_post_best.get("approved_preferred_summary") or {}
    displacement_diag_rejected = displacement_diag_best.get("selected_rejected_summary") or {}
    displacement_diag_omitted = displacement_diag_best.get("omitted_approved_summary") or {}
    approved_book_candidate = frozen_approved_entry_book_fv.get("candidate") or {}
    approved_book_rows = int(as_float(approved_book_candidate.get("settled")) or 0)
    approved_book_brier_delta = as_float(approved_book_candidate.get("brier_delta_vs_raw"))
    approved_book_logloss_delta = as_float(approved_book_candidate.get("logloss_delta_vs_raw"))
    approved_book_raw_blend_freeze = frozen_approved_entry_book_raw_blend.get("freeze") or {}
    approved_book_raw_blend_future = frozen_approved_entry_book_raw_blend.get("future") or {}
    approved_book_raw_blend_prefreeze = frozen_approved_entry_book_raw_blend.get("prefreeze_context") or {}
    approved_book_raw_blend_future_primary = (
        approved_book_raw_blend_future.get("primary") if isinstance(approved_book_raw_blend_future, dict) else {}
    )
    approved_book_raw_blend_prefreeze_primary = (
        approved_book_raw_blend_prefreeze.get("primary") if isinstance(approved_book_raw_blend_prefreeze, dict) else {}
    )
    approved_book_raw_blend_future_rows = int(
        as_float(approved_book_raw_blend_future_primary.get("settled")) or 0
    )

    frozen_best = (frozen_conservative.get("ranked") or [{}])[0]
    frozen_rows = int(as_float(frozen_best.get("rows")) or 0)
    frozen_entries = int(as_float(frozen_conservative.get("entries")) or 0)
    frozen_settled = int(as_float(frozen_conservative.get("settled")) or 0)
    frozen_p70_best = (frozen_p70.get("ranked") or [{}])[0]
    frozen_p70_rows = int(as_float(frozen_p70_best.get("rows")) or 0)
    frozen_p70_entries = int(as_float(frozen_p70.get("entries")) or 0)
    frozen_p70_settled = int(as_float(frozen_p70.get("settled")) or 0)
    frozen_p70_eb_best = (frozen_p70_eb.get("ranked") or [{}])[0]
    frozen_p70_eb_rows = int(as_float(frozen_p70_eb_best.get("rows")) or 0)
    frozen_p70_eb_entries = int(as_float(frozen_p70_eb.get("entries")) or 0)
    frozen_p70_eb_settled = int(as_float(frozen_p70_eb.get("settled")) or 0)
    frozen_path_state_best = next(
        (
            row for row in (frozen_path_state_p70.get("ranked") or [])
            if row.get("variant") == ((frozen_path_state_p70.get("freeze") or {}).get("variant"))
        ),
        (frozen_path_state_p70.get("ranked") or [{}])[0],
    )
    frozen_path_state_rows = int(as_float(frozen_path_state_best.get("rows")) or 0)
    frozen_path_state_entries = int(as_float(frozen_path_state_p70.get("future_entries")) or 0)
    frozen_path_state_settled = int(as_float(frozen_path_state_p70.get("future_settled")) or 0)
    frozen_boundary_recross_best = next(
        (
            row for row in (frozen_boundary_recross.get("ranked") or [])
            if row.get("variant") == ((frozen_boundary_recross.get("freeze") or {}).get("variant"))
        ),
        (frozen_boundary_recross.get("ranked") or [{}])[0],
    )
    frozen_boundary_recross_rows = int(as_float(frozen_boundary_recross_best.get("rows")) or 0)
    frozen_boundary_recross_entries = int(as_float(frozen_boundary_recross.get("entries")) or 0)
    frozen_boundary_recross_settled = int(as_float(frozen_boundary_recross.get("settled")) or 0)
    frozen_boundary_temperature_candidate = frozen_boundary_temperature.get("candidate") or {}
    frozen_boundary_temperature_rows = int(as_float(frozen_boundary_temperature_candidate.get("rows")) or 0)
    frozen_boundary_temperature_entries = int(as_float(frozen_boundary_temperature.get("entries")) or 0)
    frozen_boundary_temperature_adjusted = int(as_float(frozen_boundary_temperature_candidate.get("adjusted_rows")) or 0)
    frozen_boundary_temperature_denominator = int(as_float(frozen_boundary_temperature.get("future_denominator")) or 0)
    frozen_boundary_temperature_brier = as_float(frozen_boundary_temperature_candidate.get("brier_mean_delta"))
    frozen_boundary_temperature_logloss = as_float(frozen_boundary_temperature_candidate.get("logloss_mean_delta"))
    frozen_boundary_energy_summary = frozen_boundary_energy_fv_entry.get("future_candidate_summary") or {}
    frozen_boundary_energy_rows = int(as_float(frozen_boundary_energy_summary.get("settled")) or 0)
    frozen_boundary_energy_entries = int(as_float(frozen_boundary_energy_summary.get("entries")) or 0)
    frozen_boundary_energy_coverage = as_float(frozen_boundary_energy_summary.get("coverage_pct"))
    frozen_boundary_energy_net = as_float(frozen_boundary_energy_summary.get("net_cents"))
    frozen_boundary_energy_delta = as_float(frozen_boundary_energy_fv_entry.get("future_delta_net_cents"))
    frozen_boundary_energy_diag_delta = as_float(frozen_boundary_energy_fv_entry.get("diagnostic_delta_net_cents"))
    frozen_early_no_boundary_summary = frozen_early_no_boundary_fv_entry.get("future_candidate_summary") or {}
    frozen_early_no_boundary_rows = int(as_float(frozen_early_no_boundary_summary.get("settled")) or 0)
    frozen_early_no_boundary_entries = int(as_float(frozen_early_no_boundary_summary.get("entries")) or 0)
    frozen_early_no_boundary_coverage = as_float(frozen_early_no_boundary_summary.get("coverage_pct"))
    frozen_early_no_boundary_net = as_float(frozen_early_no_boundary_summary.get("net_cents"))
    frozen_early_no_boundary_brier = as_float(frozen_early_no_boundary_summary.get("avg_brier"))
    frozen_early_no_boundary_delta = as_float(frozen_early_no_boundary_fv_entry.get("future_delta_net_cents"))
    frozen_early_no_boundary_diag_delta = as_float(frozen_early_no_boundary_fv_entry.get("diagnostic_delta_net_cents"))
    frozen_mid_edge_false_conviction_best = next(
        (
            row for row in (frozen_mid_edge_false_conviction.get("ranked") or [])
            if row.get("variant") == ((frozen_mid_edge_false_conviction.get("freeze") or {}).get("variant"))
        ),
        (frozen_mid_edge_false_conviction.get("ranked") or [{}])[0],
    )
    frozen_mid_edge_false_conviction_rows = int(as_float(frozen_mid_edge_false_conviction_best.get("rows")) or 0)
    frozen_mid_edge_false_conviction_entries = int(as_float(frozen_mid_edge_false_conviction.get("entries")) or 0)
    frozen_mid_edge_false_conviction_settled = int(as_float(frozen_mid_edge_false_conviction.get("settled")) or 0)
    frozen_boundary_clock_candidate = frozen_boundary_clock_fv.get("candidate") or {}
    frozen_boundary_clock_fv_rows = int(as_float(frozen_boundary_clock_candidate.get("settled")) or 0)
    frozen_boundary_clock_fv_entries = int(as_float(frozen_boundary_clock_candidate.get("entries")) or 0)
    frozen_boundary_clock_fv_adjusted = int(as_float(frozen_boundary_clock_candidate.get("adjusted_rows")) or 0)
    frozen_boundary_clock_fv_brier = as_float(frozen_boundary_clock_candidate.get("brier_mean_delta"))
    frozen_boundary_clock_fv_logloss = as_float(frozen_boundary_clock_candidate.get("logloss_mean_delta"))
    frozen_side_asymmetry_candidate = frozen_side_asymmetry_fv.get("candidate") or {}
    frozen_side_asymmetry_rows = int(as_float(frozen_side_asymmetry_candidate.get("settled")) or 0)
    frozen_side_asymmetry_entries = int(as_float(frozen_side_asymmetry_candidate.get("entries")) or 0)
    frozen_side_asymmetry_adjusted = int(as_float(frozen_side_asymmetry_candidate.get("adjusted_rows")) or 0)
    frozen_side_asymmetry_brier = as_float(frozen_side_asymmetry_candidate.get("brier_mean_delta"))
    frozen_side_asymmetry_logloss = as_float(frozen_side_asymmetry_candidate.get("logloss_mean_delta"))
    frozen_edge_phase_best = next(
        (
            row for row in (frozen_edge_phase.get("ranked") or [])
            if row.get("variant") == ((frozen_edge_phase.get("freeze") or {}).get("variant"))
        ),
        (frozen_edge_phase.get("ranked") or [{}])[0],
    )
    frozen_edge_phase_rows = int(as_float(frozen_edge_phase_best.get("rows")) or 0)
    frozen_edge_phase_entries = int(as_float(frozen_edge_phase.get("entries")) or 0)
    frozen_edge_phase_settled = int(as_float(frozen_edge_phase.get("settled")) or 0)
    frozen_edge_phase_gate_candidate = frozen_edge_phase_gate.get("candidate") or {}
    frozen_edge_phase_gate_rows = int(as_float(frozen_edge_phase_gate_candidate.get("settled")) or 0)
    frozen_edge_phase_gate_entries = int(as_float(frozen_edge_phase_gate_candidate.get("entries")) or 0)
    frozen_edge_gate_opposite_candidate = frozen_edge_gate_opposite.get("candidate") or {}
    frozen_edge_gate_opposite_rows = int(as_float(frozen_edge_gate_opposite_candidate.get("settled")) or 0)
    frozen_edge_gate_opposite_entries = int(as_float(frozen_edge_gate_opposite_candidate.get("entries")) or 0)
    frozen_early_no_boundary_decay_candidate = frozen_early_no_boundary_decay_repair.get("candidate_summary") or {}
    frozen_early_no_boundary_decay_rows = int(as_float(frozen_early_no_boundary_decay_candidate.get("settled")) or 0)
    frozen_early_no_boundary_decay_entries = int(as_float(frozen_early_no_boundary_decay_candidate.get("entries")) or 0)
    frozen_early_no_boundary_decay_coverage = as_float(frozen_early_no_boundary_decay_candidate.get("coverage_pct"))
    frozen_early_no_boundary_decay_net = as_float(frozen_early_no_boundary_decay_candidate.get("net_cents"))
    frozen_false_conviction_approved_candidate = frozen_false_conviction_approved_repair.get("candidate_summary") or {}
    frozen_false_conviction_approved_rows = int(as_float(frozen_false_conviction_approved_candidate.get("settled")) or 0)
    frozen_false_conviction_approved_entries = int(as_float(frozen_false_conviction_approved_candidate.get("entries")) or 0)
    frozen_false_conviction_approved_coverage = as_float(frozen_false_conviction_approved_candidate.get("coverage_pct"))
    frozen_false_conviction_approved_net = as_float(frozen_false_conviction_approved_candidate.get("net_cents"))
    frozen_false_conviction_approved_recon = as_float(frozen_false_conviction_approved_repair.get("reconstructed_share"))
    frozen_mid_edge_boundary_deception_candidate = frozen_mid_edge_boundary_deception_repair.get("candidate_summary") or {}
    frozen_mid_edge_boundary_deception_rows = int(as_float(frozen_mid_edge_boundary_deception_candidate.get("settled")) or 0)
    frozen_mid_edge_boundary_deception_entries = int(as_float(frozen_mid_edge_boundary_deception_candidate.get("entries")) or 0)
    frozen_mid_edge_boundary_deception_coverage = as_float(frozen_mid_edge_boundary_deception_candidate.get("coverage_pct"))
    frozen_mid_edge_boundary_deception_net = as_float(frozen_mid_edge_boundary_deception_candidate.get("net_cents"))
    frozen_low_recross_candidate = frozen_low_recross_repair.get("candidate_summary") or {}
    frozen_low_recross_rows = int(as_float(frozen_low_recross_candidate.get("settled")) or 0)
    frozen_low_recross_entries = int(as_float(frozen_low_recross_candidate.get("entries")) or 0)
    frozen_low_recross_coverage = as_float(frozen_low_recross_candidate.get("coverage_pct"))
    frozen_low_recross_net = as_float(frozen_low_recross_candidate.get("net_cents"))
    frozen_high_raw_p_candidate = frozen_high_raw_p_repair.get("candidate_summary") or {}
    frozen_high_raw_p_rows = int(as_float(frozen_high_raw_p_candidate.get("settled")) or 0)
    frozen_high_raw_p_entries = int(as_float(frozen_high_raw_p_candidate.get("entries")) or 0)
    frozen_high_raw_p_coverage = as_float(frozen_high_raw_p_candidate.get("coverage_pct"))
    frozen_high_raw_p_net = as_float(frozen_high_raw_p_candidate.get("net_cents"))
    frozen_p50_book_edge_summary = frozen_p50_book_edge_entry.get("summary") or {}
    frozen_p50_book_edge_rows = int(as_float(frozen_p50_book_edge_summary.get("settled")) or 0)
    frozen_p50_book_edge_entries = int(as_float(frozen_p50_book_edge_summary.get("entries")) or 0)
    frozen_p50_book_edge_coverage = as_float(frozen_p50_book_edge_summary.get("coverage_pct"))
    frozen_p50_book_edge_net = as_float(frozen_p50_book_edge_summary.get("gross_cents"))
    frozen_book_plus05_summary = frozen_book_plus05_entry.get("summary") or {}
    frozen_book_plus05_rows = int(as_float(frozen_book_plus05_summary.get("settled")) or 0)
    frozen_book_plus05_entries = int(as_float(frozen_book_plus05_summary.get("entries")) or 0)
    frozen_book_plus05_coverage = as_float(frozen_book_plus05_summary.get("coverage_pct"))
    frozen_book_plus05_net = as_float(frozen_book_plus05_summary.get("gross_cents"))
    frozen_book_plus05_no_cheap_yes_summary = frozen_book_plus05_no_cheap_yes_entry.get("summary") or {}
    frozen_book_plus05_no_cheap_yes_rows = int(as_float(frozen_book_plus05_no_cheap_yes_summary.get("settled")) or 0)
    frozen_book_plus05_no_cheap_yes_entries = int(as_float(frozen_book_plus05_no_cheap_yes_summary.get("entries")) or 0)
    frozen_book_plus05_no_cheap_yes_coverage = as_float(frozen_book_plus05_no_cheap_yes_summary.get("coverage_pct"))
    frozen_book_plus05_no_cheap_yes_net = as_float(frozen_book_plus05_no_cheap_yes_summary.get("gross_cents"))
    frozen_boundary_clock_candidate = frozen_boundary_clock_repair.get("candidate_summary") or {}
    frozen_boundary_clock_rows = int(as_float(frozen_boundary_clock_candidate.get("settled")) or 0)
    frozen_boundary_clock_entries = int(as_float(frozen_boundary_clock_candidate.get("entries")) or 0)
    frozen_boundary_clock_coverage = as_float(frozen_boundary_clock_candidate.get("coverage_pct"))
    frozen_boundary_clock_net = as_float(frozen_boundary_clock_candidate.get("net_cents"))
    frozen_boundary_clock_bridge_candidate = frozen_boundary_clock_fv_entry_bridge.get("candidate_summary") or {}
    frozen_boundary_clock_bridge_rows = int(as_float(frozen_boundary_clock_bridge_candidate.get("settled")) or 0)
    frozen_boundary_clock_bridge_entries = int(as_float(frozen_boundary_clock_bridge_candidate.get("entries")) or 0)
    frozen_boundary_clock_bridge_coverage = as_float(frozen_boundary_clock_bridge_candidate.get("coverage_pct"))
    frozen_boundary_clock_bridge_net = as_float(frozen_boundary_clock_bridge_candidate.get("net_cents"))
    boundary_clock_source_lanes = boundary_clock_source_stress.get("lanes") or []
    boundary_clock_entry_source_stress = next(
        (row for row in boundary_clock_source_lanes if row.get("lane") == "boundary_clock_repair_entry"),
        {},
    )
    boundary_clock_bridge_source_stress = next(
        (row for row in boundary_clock_source_lanes if row.get("lane") == "boundary_clock_fv_entry_bridge"),
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
    boundary_clock_feature_lanes = boundary_clock_feature_gate.get("lanes") or []
    boundary_clock_feature_diag_entry = next((row for row in boundary_clock_feature_lanes if row.get("lane") == "diagnostic_entry"), {})
    boundary_clock_feature_diag_bridge = next((row for row in boundary_clock_feature_lanes if row.get("lane") == "diagnostic_bridge"), {})
    boundary_clock_feature_post_entry = next((row for row in boundary_clock_feature_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    boundary_clock_feature_post_bridge = next((row for row in boundary_clock_feature_lanes if row.get("lane") == "post_feature_freeze_bridge"), {})
    boundary_clock_feature_diag_entry_best = (boundary_clock_feature_diag_entry.get("variants") or [{}])[0]
    boundary_clock_feature_diag_bridge_best = (boundary_clock_feature_diag_bridge.get("variants") or [{}])[0]
    boundary_clock_feature_post_entry_best = (boundary_clock_feature_post_entry.get("variants") or [{}])[0]
    boundary_clock_feature_post_bridge_best = (boundary_clock_feature_post_bridge.get("variants") or [{}])[0]
    boundary_clock_feature_diag_entry_summary = boundary_clock_feature_diag_entry_best.get("candidate_summary") or {}
    boundary_clock_feature_diag_bridge_summary = boundary_clock_feature_diag_bridge_best.get("candidate_summary") or {}
    boundary_clock_feature_post_entry_summary = boundary_clock_feature_post_entry_best.get("candidate_summary") or {}
    boundary_clock_feature_post_bridge_summary = boundary_clock_feature_post_bridge_best.get("candidate_summary") or {}
    boundary_clock_feature_runway_post = (boundary_clock_feature_gate_runway.get("post_freeze_top") or [{}])[0]
    boundary_clock_feature_failure_lanes = boundary_clock_feature_gate_failure_modes.get("lanes") or {}
    boundary_clock_feature_failure_post = (boundary_clock_feature_failure_lanes.get("post_feature_freeze_entry") or [{}])[0]
    boundary_clock_feature_failure_diag = (boundary_clock_feature_failure_lanes.get("diagnostic_entry") or [{}])[0]
    boundary_clock_feature_loss_lanes = boundary_clock_feature_gate_loss_analog.get("lanes") or {}
    boundary_clock_feature_loss_post = boundary_clock_feature_loss_lanes.get("post_feature_freeze_entry") or {}
    boundary_clock_feature_loss_diag = boundary_clock_feature_loss_lanes.get("diagnostic_entry") or {}
    boundary_clock_feature_row_lanes = boundary_clock_feature_gate_row_ledger.get("lanes") or []
    boundary_clock_feature_row_entry = next((row for row in boundary_clock_feature_row_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    boundary_clock_feature_row_bridge = next((row for row in boundary_clock_feature_row_lanes if row.get("lane") == "post_feature_freeze_bridge"), {})
    boundary_clock_feature_row_entry_best = (boundary_clock_feature_row_entry.get("rules") or [{}])[0]
    boundary_clock_feature_row_bridge_best = (boundary_clock_feature_row_bridge.get("rules") or [{}])[0]
    boundary_clock_feature_recovery_lanes = boundary_clock_feature_gate_coverage_recovery.get("lanes") or []
    boundary_clock_feature_recovery_entry = next((row for row in boundary_clock_feature_recovery_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    boundary_clock_feature_recovery_bridge = next((row for row in boundary_clock_feature_recovery_lanes if row.get("lane") == "post_feature_freeze_bridge"), {})
    boundary_clock_feature_recovery_entry_strict = boundary_clock_feature_recovery_entry.get("strict_summary") or {}
    boundary_clock_feature_recovery_bridge_strict = boundary_clock_feature_recovery_bridge.get("strict_summary") or {}
    boundary_clock_feature_recovery_entry_broad = next(
        (row for row in boundary_clock_feature_recovery_entry.get("variants") or [] if row.get("rule") != boundary_clock_feature_recovery_entry.get("strict_rule")),
        {},
    )
    boundary_clock_feature_recovery_bridge_broad = next(
        (row for row in boundary_clock_feature_recovery_bridge.get("variants") or [] if row.get("rule") != boundary_clock_feature_recovery_bridge.get("strict_rule")),
        {},
    )
    boundary_clock_feature_recovery_entry_broad_summary = boundary_clock_feature_recovery_entry_broad.get("summary") or {}
    boundary_clock_feature_recovery_bridge_broad_summary = boundary_clock_feature_recovery_bridge_broad.get("summary") or {}
    boundary_clock_feature_recovery_entry_broad_comparison = boundary_clock_feature_recovery_entry_broad.get("strict_comparison") or {}
    boundary_clock_feature_recovery_bridge_broad_comparison = boundary_clock_feature_recovery_bridge_broad.get("strict_comparison") or {}
    boundary_clock_feature_source_lanes = boundary_clock_feature_gate_source_denominator.get("lanes") or []
    boundary_clock_feature_source_entry = next((row for row in boundary_clock_feature_source_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    boundary_clock_feature_source_bridge = next((row for row in boundary_clock_feature_source_lanes if row.get("lane") == "post_feature_freeze_bridge"), {})
    boundary_clock_feature_source_entry_best = (boundary_clock_feature_source_entry.get("rules") or [{}])[0]
    boundary_clock_feature_source_bridge_best = (boundary_clock_feature_source_bridge.get("rules") or [{}])[0]
    boundary_clock_feature_cheap_tail_lanes = boundary_clock_feature_gate_cheap_tail.get("lanes") or []
    boundary_clock_feature_cheap_tail_entry = next(
        (row for row in boundary_clock_feature_cheap_tail_lanes if row.get("lane") == "post_feature_freeze_entry"),
        {},
    )
    boundary_clock_feature_cheap_tail_bridge = next(
        (row for row in boundary_clock_feature_cheap_tail_lanes if row.get("lane") == "post_feature_freeze_bridge"),
        {},
    )
    boundary_clock_feature_cheap_tail_entry_added = boundary_clock_feature_cheap_tail_entry.get("cheap_added_vs_strict_summary") or {}
    boundary_clock_feature_cheap_tail_entry_half = next(
        (
            row
            for row in boundary_clock_feature_cheap_tail_entry.get("notional_shrink_policies") or []
            if row.get("policy") == "cheap_lt10_half"
        ),
        {},
    )
    boundary_clock_feature_frontier_lanes = boundary_clock_feature_gate_coverage_source_frontier.get("lanes") or []
    boundary_clock_feature_frontier_entry = next((row for row in boundary_clock_feature_frontier_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    boundary_clock_feature_frontier_bridge = next((row for row in boundary_clock_feature_frontier_lanes if row.get("lane") == "post_feature_freeze_bridge"), {})
    boundary_clock_feature_frontier_entry_best = (boundary_clock_feature_frontier_entry.get("pareto_frontier") or [{}])[0]
    boundary_clock_feature_frontier_bridge_best = (boundary_clock_feature_frontier_bridge.get("pareto_frontier") or [{}])[0]
    boundary_clock_feature_frontier_entry_summary = boundary_clock_feature_frontier_entry_best.get("summary") or {}
    boundary_clock_feature_frontier_bridge_summary = boundary_clock_feature_frontier_bridge_best.get("summary") or {}
    feature_gate_feasibility_lanes = feature_gate_source_feasibility_bound.get("lanes") or []
    feature_gate_feasibility_entry = next((row for row in feature_gate_feasibility_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    feature_gate_feasibility_bridge = next((row for row in feature_gate_feasibility_lanes if row.get("lane") == "post_feature_freeze_bridge"), {})
    feature_gate_feasibility_entry_75 = next(
        (row for row in feature_gate_feasibility_entry.get("target_bounds") or [] if row.get("target_coverage_pct") == 75.0),
        {},
    )
    feature_gate_feasibility_bridge_75 = next(
        (row for row in feature_gate_feasibility_bridge.get("target_bounds") or [] if row.get("target_coverage_pct") == 75.0),
        {},
    )
    boundary_clock_feature_frontier_runway_lanes = boundary_clock_feature_gate_frontier_runway.get("lanes") or []
    boundary_clock_feature_frontier_runway_entry = next((row for row in boundary_clock_feature_frontier_runway_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    boundary_clock_feature_frontier_runway_entry_current = boundary_clock_feature_frontier_runway_entry.get("current") or {}
    boundary_clock_feature_frontier_runway_entry_runway = boundary_clock_feature_frontier_runway_entry.get("runway") or {}
    boundary_clock_feature_frontier_mechanism_lanes = boundary_clock_feature_gate_frontier_mechanism.get("lanes") or []
    boundary_clock_feature_frontier_mechanism_entry = next((row for row in boundary_clock_feature_frontier_mechanism_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    boundary_clock_feature_frontier_mechanism_entry_summary = boundary_clock_feature_frontier_mechanism_entry.get("frontier_selected_summary") or {}
    boundary_clock_feature_frontier_mechanism_gained = boundary_clock_feature_frontier_mechanism_entry.get("gained_summary") or {}
    boundary_clock_feature_frontier_mechanism_omitted = boundary_clock_feature_frontier_mechanism_entry.get("omitted_summary") or {}
    boundary_clock_feature_outlier_lanes = boundary_clock_feature_gate_outlier_stress.get("lanes") or []
    boundary_clock_feature_outlier_entry = next((row for row in boundary_clock_feature_outlier_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    boundary_clock_feature_clean_broad_lanes = boundary_clock_feature_gate_clean_broad_frontier.get("lanes") or []
    boundary_clock_feature_clean_broad_diag_entry = next((row for row in boundary_clock_feature_clean_broad_lanes if row.get("lane") == "diagnostic_parent_entry"), {})
    boundary_clock_feature_clean_broad_post_entry = next((row for row in boundary_clock_feature_clean_broad_lanes if row.get("lane") == "post_clean_broad_freeze_entry"), {})
    boundary_clock_feature_clean_broad_diag_entry_summary = boundary_clock_feature_clean_broad_diag_entry.get("candidate_summary") or {}
    boundary_clock_feature_clean_broad_post_entry_summary = boundary_clock_feature_clean_broad_post_entry.get("candidate_summary") or {}
    feature_gate_frontier_drift_lanes = feature_gate_frontier_drift_audit.get("lanes") or []
    feature_gate_frontier_drift_entry = next((row for row in feature_gate_frontier_drift_lanes if row.get("label") == "entry"), {})
    feature_gate_frontier_drift_bridge = next((row for row in feature_gate_frontier_drift_lanes if row.get("label") == "bridge"), {})
    feature_gate_frontier_drift_entry_parent = feature_gate_frontier_drift_entry.get("parent_frontier") or {}
    feature_gate_frontier_drift_entry_strict = feature_gate_frontier_drift_entry.get("strict_watch") or {}
    feature_gate_frontier_drift_entry_delta = feature_gate_frontier_drift_entry.get("delta") or {}
    feature_gate_frontier_drift_bridge_parent = feature_gate_frontier_drift_bridge.get("parent_frontier") or {}
    feature_gate_frontier_drift_bridge_strict = feature_gate_frontier_drift_bridge.get("strict_watch") or {}
    feature_gate_frontier_drift_bridge_delta = feature_gate_frontier_drift_bridge.get("delta") or {}
    boundary_clock_feature_soft_lanes = boundary_clock_feature_gate_soft_frontier.get("lanes") or []
    boundary_clock_feature_soft_diag_entry = next((row for row in boundary_clock_feature_soft_lanes if row.get("lane") == "diagnostic_entry"), {})
    boundary_clock_feature_soft_post_entry = next((row for row in boundary_clock_feature_soft_lanes if row.get("lane") == "post_soft_frontier_birth_entry"), {})
    boundary_clock_feature_soft_diag_entry_best = (boundary_clock_feature_soft_diag_entry.get("variants") or [{}])[0]
    boundary_clock_feature_soft_post_entry_best = (boundary_clock_feature_soft_post_entry.get("variants") or [{}])[0]
    boundary_clock_feature_soft_diag_entry_summary = boundary_clock_feature_soft_diag_entry_best.get("candidate_summary") or {}
    boundary_clock_feature_soft_post_entry_summary = boundary_clock_feature_soft_post_entry_best.get("candidate_summary") or {}
    soft_frontier_failure_lanes = soft_frontier_post_birth_failure_drilldown.get("lanes") or []
    soft_frontier_failure_entry = next((row for row in soft_frontier_failure_lanes if row.get("lane") == "post_soft_frontier_birth_entry"), {})
    soft_frontier_failure_entry_summary = soft_frontier_failure_entry.get("summary") or {}
    soft_frontier_failure_bridge = next((row for row in soft_frontier_failure_lanes if row.get("lane") == "post_soft_frontier_birth_bridge"), {})
    soft_frontier_failure_bridge_summary = soft_frontier_failure_bridge.get("summary") or {}
    boundary_clock_feature_soft_exit_stack_lanes = boundary_clock_feature_gate_soft_frontier_exit_stack.get("lanes") or []
    boundary_clock_feature_soft_exit_stack_best = next(
        (
            variant
            for lane in boundary_clock_feature_soft_exit_stack_lanes
            for variant in (lane.get("variants") or [])
            if isinstance(variant, dict)
        ),
        {},
    )
    boundary_clock_feature_soft_exit_stack_best_summary = boundary_clock_feature_soft_exit_stack_best.get("entry_summary") or {}
    feature_gate_cheap_tail_shrink_lanes = feature_gate_cheap_tail_shrink_watch.get("lanes") or []
    feature_gate_cheap_tail_shrink_entry = next(
        (row for row in feature_gate_cheap_tail_shrink_lanes if row.get("lane") == "post_cheap_tail_shrink_birth_entry"),
        {},
    )
    feature_gate_cheap_tail_shrink_best = (feature_gate_cheap_tail_shrink_entry.get("policies") or [{}])[0]
    soft_frontier_size_shrink_lanes = soft_frontier_size_shrink.get("lanes") or []
    soft_frontier_size_shrink_diag_best = next(
        (
            variant
            for lane in soft_frontier_size_shrink_lanes
            if isinstance(lane, dict) and not lane.get("strict_forward")
            for variant in (lane.get("variants") or [])
            if isinstance(variant, dict)
        ),
        {},
    )
    soft_frontier_size_shrink_strict_best = next(
        (
            variant
            for lane in soft_frontier_size_shrink_lanes
            if isinstance(lane, dict) and lane.get("strict_forward")
            for variant in (lane.get("variants") or [])
            if isinstance(variant, dict)
        ),
        {},
    )
    soft_frontier_size_shrink_diag_summary = soft_frontier_size_shrink_diag_best.get("summary") or {}
    soft_frontier_size_shrink_strict_summary = soft_frontier_size_shrink_strict_best.get("summary") or {}
    soft_frontier_midprice_lanes = soft_frontier_midprice_boundary_shrink.get("lanes") or []
    soft_frontier_midprice_diag_best = next(
        (
            variant
            for lane in soft_frontier_midprice_lanes
            if isinstance(lane, dict) and not lane.get("strict_forward")
            for variant in (lane.get("variants") or [])
            if isinstance(variant, dict)
        ),
        {},
    )
    soft_frontier_midprice_strict_best = next(
        (
            variant
            for lane in soft_frontier_midprice_lanes
            if isinstance(lane, dict) and lane.get("strict_forward")
            for variant in (lane.get("variants") or [])
            if isinstance(variant, dict)
        ),
        {},
    )
    soft_frontier_midprice_diag_summary = soft_frontier_midprice_diag_best.get("summary") or {}
    soft_frontier_midprice_strict_summary = soft_frontier_midprice_strict_best.get("summary") or {}
    soft_frontier_midprice_exit_stack_variants = soft_frontier_midprice_boundary_exit_stack.get("variants") or []
    soft_frontier_midprice_exit_stack_best = (
        soft_frontier_midprice_exit_stack_variants[0]
        if soft_frontier_midprice_exit_stack_variants
        else {}
    )
    soft_frontier_midprice_exit_stack_runway_rows = soft_frontier_midprice_boundary_exit_stack_runway.get("rows") or []
    soft_frontier_midprice_exit_stack_runway_best = (
        soft_frontier_midprice_exit_stack_runway_rows[0]
        if soft_frontier_midprice_exit_stack_runway_rows
        else {}
    )
    soft_frontier_midprice_exit_stack_entry_summary = soft_frontier_midprice_exit_stack_best.get("entry_summary") or {}
    boundary_clock_feature_ask_lanes = boundary_clock_feature_gate_ask_floor.get("lanes") or []
    boundary_clock_feature_ask_post_entry = next((row for row in boundary_clock_feature_ask_lanes if row.get("lane") == "post_feature_freeze_entry"), {})
    boundary_clock_feature_ask_diag_entry = next((row for row in boundary_clock_feature_ask_lanes if row.get("lane") == "diagnostic_entry"), {})
    boundary_clock_feature_penalty_lanes = boundary_clock_feature_gate_continuous_penalty.get("lanes") or []
    boundary_clock_feature_penalty_pre_entry = next((row for row in boundary_clock_feature_penalty_lanes if row.get("lane") == "pre_penalty_birth_feature_entry"), {})
    boundary_clock_feature_penalty_post_entry = next((row for row in boundary_clock_feature_penalty_lanes if row.get("lane") == "post_penalty_birth_entry"), {})
    boundary_clock_feature_penalty_diag_entry = next((row for row in boundary_clock_feature_penalty_lanes if row.get("lane") == "diagnostic_entry"), {})
    boundary_clock_feature_penalty_pre_entry_best = (boundary_clock_feature_penalty_pre_entry.get("variants") or [{}])[0]
    boundary_clock_feature_penalty_post_entry_best = (boundary_clock_feature_penalty_post_entry.get("variants") or [{}])[0]
    boundary_clock_feature_penalty_diag_entry_best = (boundary_clock_feature_penalty_diag_entry.get("variants") or [{}])[0]
    boundary_clock_feature_penalty_pre_entry_summary = boundary_clock_feature_penalty_pre_entry_best.get("candidate_summary") or {}
    boundary_clock_feature_penalty_post_entry_summary = boundary_clock_feature_penalty_post_entry_best.get("candidate_summary") or {}
    boundary_clock_feature_penalty_diag_entry_summary = boundary_clock_feature_penalty_diag_entry_best.get("candidate_summary") or {}
    boundary_clock_feature_penalty_stress_lanes = boundary_clock_feature_gate_continuous_penalty_stress.get("lanes") or []
    boundary_clock_feature_penalty_stress_post_entry = next((row for row in boundary_clock_feature_penalty_stress_lanes if row.get("lane") == "post_penalty_birth_entry"), {})
    boundary_clock_feature_penalty_stress_diag_entry = next((row for row in boundary_clock_feature_penalty_stress_lanes if row.get("lane") == "diagnostic_entry"), {})
    boundary_clock_feature_residual_lanes = boundary_clock_feature_gate_residual_loss.get("lanes") or {}
    boundary_clock_feature_residual_diag_entry = boundary_clock_feature_residual_lanes.get("diagnostic_entry") or {}
    boundary_clock_feature_residual_pre_entry = boundary_clock_feature_residual_lanes.get("pre_penalty_birth_feature_entry") or {}
    boundary_clock_feature_residual_post_entry = boundary_clock_feature_residual_lanes.get("post_penalty_birth_entry") or {}
    frozen_weak_reversal_residual_repair_candidate = frozen_weak_reversal_residual_repair.get("candidate_summary") or {}
    frozen_weak_reversal_residual_repair_rows = int(as_float(frozen_weak_reversal_residual_repair_candidate.get("settled")) or 0)
    frozen_weak_reversal_residual_repair_entries = int(as_float(frozen_weak_reversal_residual_repair_candidate.get("entries")) or 0)
    frozen_weak_reversal_residual_repair_coverage = as_float(frozen_weak_reversal_residual_repair_candidate.get("coverage_pct"))
    frozen_weak_reversal_residual_repair_net = as_float(frozen_weak_reversal_residual_repair_candidate.get("net_cents"))
    frozen_weak_reversal_residual_fv_rows = int(as_float((frozen_weak_reversal_residual_fv_shrink.get("variant_all") or {}).get("rows")) or 0)
    frozen_weak_reversal_residual_fv_denominator = int(as_float(frozen_weak_reversal_residual_fv_shrink.get("future_denominator")) or 0)
    frozen_weak_reversal_residual_fv_brier = as_float(frozen_weak_reversal_residual_fv_shrink.get("brier_delta_vs_raw"))
    frozen_weak_reversal_residual_fv_logloss = as_float(frozen_weak_reversal_residual_fv_shrink.get("logloss_delta_vs_raw"))
    frozen_no_mid_edge_fv_rows = int(as_float((frozen_no_mid_edge_fv.get("variant") or {}).get("rows")) or 0)
    frozen_no_mid_edge_fv_denominator = int(as_float(frozen_no_mid_edge_fv.get("future_denominator")) or 0)
    frozen_no_mid_edge_fv_brier = as_float(frozen_no_mid_edge_fv.get("brier_delta_vs_raw"))
    frozen_no_mid_edge_fv_logloss = as_float(frozen_no_mid_edge_fv.get("logloss_delta_vs_raw"))
    frozen_early_boundary_wait_candidate = frozen_early_boundary_wait_repair.get("candidate_summary") or {}
    frozen_early_boundary_wait_rows = int(as_float(frozen_early_boundary_wait_candidate.get("settled")) or 0)
    frozen_early_boundary_wait_entries = int(as_float(frozen_early_boundary_wait_candidate.get("entries")) or 0)
    frozen_early_boundary_wait_coverage = as_float(frozen_early_boundary_wait_candidate.get("coverage_pct"))
    frozen_early_boundary_wait_net = as_float(frozen_early_boundary_wait_candidate.get("net_cents"))
    frozen_early_boundary_opposite_wait_candidate = frozen_early_boundary_opposite_wait_repair.get("candidate_summary") or {}
    frozen_early_boundary_opposite_wait_rows = int(as_float(frozen_early_boundary_opposite_wait_candidate.get("settled")) or 0)
    frozen_early_boundary_opposite_wait_entries = int(as_float(frozen_early_boundary_opposite_wait_candidate.get("entries")) or 0)
    frozen_early_boundary_opposite_wait_coverage = as_float(frozen_early_boundary_opposite_wait_candidate.get("coverage_pct"))
    frozen_early_boundary_opposite_wait_net = as_float(frozen_early_boundary_opposite_wait_candidate.get("net_cents"))
    phi_forward = phi_forgetting_fv.get("forward") if isinstance(phi_forgetting_fv.get("forward"), list) else []
    phi_best = phi_forward[0] if phi_forward else {}
    phi_best_overlay = phi_best.get("overlay")
    phi_rows = int(as_float(phi_best.get("settled")) or 0)
    phi_coverage = as_float(phi_best.get("coverage_pct"))
    phi_brier_delta = as_float(phi_best.get("brier_delta_vs_raw"))
    phi_logloss_delta = as_float(phi_best.get("logloss_delta_vs_raw"))
    shrink_forward = confidence_shrink_bakeoff.get("forward") if isinstance(confidence_shrink_bakeoff.get("forward"), list) else []
    shrink_discovery = confidence_shrink_bakeoff.get("discovery") if isinstance(confidence_shrink_bakeoff.get("discovery"), list) else []
    shrink_best = shrink_forward[0] if shrink_forward else {}
    shrink_diag_best = shrink_discovery[0] if shrink_discovery else {}
    shrink_best_overlay = shrink_best.get("overlay")
    shrink_rows = int(as_float(shrink_best.get("settled")) or 0)
    shrink_coverage = as_float(shrink_best.get("coverage_pct"))
    shrink_brier_delta = as_float(shrink_best.get("brier_delta_vs_raw"))
    shrink_logloss_delta = as_float(shrink_best.get("logloss_delta_vs_raw"))
    hybrid_forward = hybrid_confidence_shrink.get("forward") if isinstance(hybrid_confidence_shrink.get("forward"), list) else []
    hybrid_discovery = hybrid_confidence_shrink.get("discovery") if isinstance(hybrid_confidence_shrink.get("discovery"), list) else []
    hybrid_best = hybrid_forward[0] if hybrid_forward else {}
    hybrid_diag_best = hybrid_discovery[0] if hybrid_discovery else {}
    hybrid_best_overlay = hybrid_best.get("overlay")
    hybrid_rows = int(as_float(hybrid_best.get("settled")) or 0)
    hybrid_coverage = as_float(hybrid_best.get("coverage_pct"))
    hybrid_brier_delta = as_float(hybrid_best.get("brier_delta_vs_raw"))
    hybrid_logloss_delta = as_float(hybrid_best.get("logloss_delta_vs_raw"))
    target_hybrid_rows = target_surface_hybrid.get("ranked") if isinstance(target_surface_hybrid.get("ranked"), list) else []
    target_hybrid_best = target_hybrid_rows[0] if target_hybrid_rows else {}
    target_hybrid_candidate = next((row for row in target_hybrid_rows if row.get("overlay") == "hybrid_confidence_shrink"), {})
    target_hybrid_settled = int(as_float(target_hybrid_candidate.get("settled")) or 0)
    target_hybrid_coverage = as_float(target_hybrid_candidate.get("coverage_pct"))
    target_hybrid_net = as_float(target_hybrid_candidate.get("net_cents_after_entry_fee"))
    target_hybrid_brier_delta = as_float(target_hybrid_candidate.get("brier_delta_vs_raw"))
    target_hybrid_logloss_delta = as_float(target_hybrid_candidate.get("logloss_delta_vs_raw"))
    target_hybrid_veto_post = {}
    target_hybrid_veto_diag = {}
    for window in target_hybrid_veto_repair.get("windows") or []:
        if not isinstance(window, dict):
            continue
        if window.get("window") == "post_repair_freeze_window":
            target_hybrid_veto_post = window
        if window.get("window") == "diagnostic_existing_target_window":
            target_hybrid_veto_diag = window
    target_hybrid_veto_post_best = (target_hybrid_veto_post.get("variants") or [{}])[0]
    target_hybrid_veto_post_summary = target_hybrid_veto_post_best.get("candidate_summary") or {}
    target_hybrid_veto_post_rows = int(as_float(target_hybrid_veto_post_summary.get("settled")) or 0)
    target_hybrid_veto_post_entries = int(as_float(target_hybrid_veto_post_summary.get("entries")) or 0)
    target_hybrid_veto_post_coverage = as_float(target_hybrid_veto_post_summary.get("coverage_pct"))
    target_hybrid_veto_post_net = as_float(target_hybrid_veto_post_summary.get("net_cents"))
    target_hybrid_veto_diag_best = (target_hybrid_veto_diag.get("variants") or [{}])[0]
    target_hybrid_veto_diag_summary = target_hybrid_veto_diag_best.get("candidate_summary") or {}
    target_hybrid_veto_diag_net = as_float(target_hybrid_veto_diag_summary.get("net_cents"))
    target_hybrid_veto_diag_delta = as_float(target_hybrid_veto_diag_best.get("delta_vs_target_cents"))
    hybrid_boundary_stack_post = {}
    hybrid_boundary_stack_diag = {}
    for window in hybrid_boundary_entry_stack.get("windows") or []:
        if not isinstance(window, dict):
            continue
        if window.get("window") == "post_stack_freeze_window":
            hybrid_boundary_stack_post = window
        if window.get("window") == "diagnostic_existing_target_window":
            hybrid_boundary_stack_diag = window
    hybrid_boundary_stack_post_best = (hybrid_boundary_stack_post.get("variants") or [{}])[0]
    hybrid_boundary_stack_post_summary = hybrid_boundary_stack_post_best.get("candidate_summary") or {}
    hybrid_boundary_stack_post_rows = int(as_float(hybrid_boundary_stack_post_summary.get("settled")) or 0)
    hybrid_boundary_stack_post_entries = int(as_float(hybrid_boundary_stack_post_summary.get("entries")) or 0)
    hybrid_boundary_stack_post_coverage = as_float(hybrid_boundary_stack_post_summary.get("coverage_pct"))
    hybrid_boundary_stack_post_net = as_float(hybrid_boundary_stack_post_summary.get("net_cents"))
    hybrid_boundary_stack_diag_best = (hybrid_boundary_stack_diag.get("variants") or [{}])[0]
    hybrid_boundary_stack_diag_summary = hybrid_boundary_stack_diag_best.get("candidate_summary") or {}
    hybrid_boundary_stack_diag_net = as_float(hybrid_boundary_stack_diag_summary.get("net_cents"))
    hybrid_boundary_stack_diag_delta = as_float(hybrid_boundary_stack_diag_best.get("delta_vs_target_cents"))
    hybrid_boundary_stack_stress_diag = hybrid_boundary_entry_stack_stress.get("diagnostic") or {}
    hybrid_boundary_stack_stress_best = hybrid_boundary_stack_stress_diag.get("best_broad_positive") or {}
    hybrid_boundary_stack_stress_watch = hybrid_boundary_stack_stress_diag.get("best_watch_source_broad_positive") or {}
    hybrid_boundary_stack_stress_lowest = hybrid_boundary_stack_stress_diag.get("lowest_reconstructed_broad_positive") or {}
    hybrid_boundary_source_stress_lanes = hybrid_boundary_entry_stack_source_stress.get("lanes") or []
    hybrid_boundary_source_stress_diag = next(
        (row for row in hybrid_boundary_source_stress_lanes if row.get("window") == "diagnostic_existing_target_window"),
        {},
    )
    hybrid_boundary_source_stress_post = next(
        (row for row in hybrid_boundary_source_stress_lanes if row.get("window") == "post_stack_freeze_window"),
        {},
    )
    hybrid_boundary_frontier_diag = {}
    hybrid_boundary_frontier_post = {}
    for window in hybrid_boundary_source_frontier.get("windows") or []:
        if not isinstance(window, dict):
            continue
        if window.get("window") == "diagnostic_existing_target_window":
            hybrid_boundary_frontier_diag = window
        if window.get("window") == "post_stack_freeze_window":
            hybrid_boundary_frontier_post = window
    hybrid_boundary_frontier_diag_best = (hybrid_boundary_frontier_diag.get("variants") or [{}])[0]
    hybrid_boundary_frontier_diag_summary = hybrid_boundary_frontier_diag_best.get("candidate_summary") or {}
    hybrid_boundary_frontier_diag_integrity = hybrid_boundary_frontier_diag_best.get("integrity_preview") or {}
    hybrid_boundary_frontier_post_best = (hybrid_boundary_frontier_post.get("variants") or [{}])[0]
    hybrid_boundary_frontier_post_summary = hybrid_boundary_frontier_post_best.get("candidate_summary") or {}
    hybrid_boundary_frontier_post_integrity = hybrid_boundary_frontier_post_best.get("integrity_preview") or {}
    hybrid_boundary_dilution_diag = (hybrid_boundary_source_dilution.get("diagnostic_top") or [{}])[0]
    hybrid_boundary_dilution_post = (hybrid_boundary_source_dilution.get("post_freeze_top") or [{}])[0]
    frozen_exit_reduce_summary = frozen_exit_reduce_suppression.get("summary") or {}
    frozen_exit_reduce_rows = int(as_float(frozen_exit_reduce_summary.get("settled")) or 0)
    frozen_exit_reduce_delta = as_float(frozen_exit_reduce_summary.get("delta_vs_current_cents"))
    exit_reduce_risk_suppressed = exit_reduce_risk_ledger.get("suppressed_summary") or {}
    exit_reduce_risk_helpful = exit_reduce_risk_ledger.get("helpful_suppressed_summary") or {}
    exit_reduce_risk_harmful = exit_reduce_risk_ledger.get("harmful_suppressed_summary") or {}
    exit_reduce_risk_groups = exit_reduce_risk_ledger.get("suppressed_group_summaries") or {}
    exit_reduce_drift_guard_diag = (exit_reduce_drift_guard_watch.get("diagnostic_since_base_freeze") or [{}])[0]
    exit_reduce_drift_guard_post = (exit_reduce_drift_guard_watch.get("post_drift_guard_birth") or [{}])[0]
    exit_reduce_signature_summary = exit_reduce_signature.get("summary") or {}
    exit_reduce_signature_best = (exit_reduce_signature.get("candidate_separators") or [{}])[0]
    exit_reduce_actionability_best_hindsight = exit_reduce_actionability.get("best_hindsight") or {}
    exit_reduce_actionability_best_observable = exit_reduce_actionability.get("best_observable") or {}
    exit_reduce_actionability_needs_freeze = exit_reduce_actionability.get("observable_needing_new_freeze") or []
    exit_reduce_refinement_lanes = exit_reduce_refinement.get("lanes") or []
    exit_reduce_refinement_diag = next((row for row in exit_reduce_refinement_lanes if row.get("lane") == "diagnostic_from_reduce_freeze"), {})
    exit_reduce_refinement_post = next((row for row in exit_reduce_refinement_lanes if row.get("lane") == "post_refinement_birth"), {})
    exit_reduce_refinement_diag_best = (exit_reduce_refinement_diag.get("variants") or [{}])[0]
    exit_reduce_refinement_post_best = (exit_reduce_refinement_post.get("variants") or [{}])[0]
    exit_reduce_refinement_diag_summary = exit_reduce_refinement_diag_best.get("summary") or {}
    exit_reduce_refinement_post_summary = exit_reduce_refinement_post_best.get("summary") or {}
    exit_reduce_depth_lanes = exit_reduce_depth_gate.get("lanes") or []
    exit_reduce_depth_diag = next((row for row in exit_reduce_depth_lanes if row.get("lane") == "diagnostic_from_reduce_freeze"), {})
    exit_reduce_depth_post = next((row for row in exit_reduce_depth_lanes if row.get("lane") == "post_depth_gate_birth"), {})
    exit_reduce_depth_diag_best = (exit_reduce_depth_diag.get("variants") or [{}])[0]
    exit_reduce_depth_post_best = (exit_reduce_depth_post.get("variants") or [{}])[0]
    exit_reduce_depth_diag_summary = exit_reduce_depth_diag_best.get("summary") or {}
    exit_reduce_depth_post_summary = exit_reduce_depth_post_best.get("summary") or {}
    exit_reduce_depth_runway_post = exit_reduce_depth_gate_runway.get("post_birth_best") or {}
    exit_reduce_depth_opportunity_rules = exit_reduce_depth_gate_opportunity.get("rules") or []
    exit_reduce_depth_opportunity_best = exit_reduce_depth_opportunity_rules[0] if exit_reduce_depth_opportunity_rules else {}
    exit_reduce_observable_lanes = exit_reduce_observable_loss_control.get("lanes") or []
    exit_reduce_observable_diag = next((row for row in exit_reduce_observable_lanes if row.get("lane") == "diagnostic_from_reduce_freeze"), {})
    exit_reduce_observable_post = next((row for row in exit_reduce_observable_lanes if row.get("lane") == "post_observable_birth"), {})
    exit_reduce_observable_diag_best = (exit_reduce_observable_diag.get("variants") or [{}])[0]
    exit_reduce_observable_post_best = (exit_reduce_observable_post.get("variants") or [{}])[0]
    exit_reduce_observable_diag_summary = exit_reduce_observable_diag_best.get("summary") or {}
    exit_reduce_observable_post_summary = exit_reduce_observable_post_best.get("summary") or {}
    exit_reduce_observable_opportunity_rules = exit_reduce_observable_loss_control_opportunity.get("rules") or []
    exit_reduce_observable_opportunity_best = exit_reduce_observable_opportunity_rules[0] if exit_reduce_observable_opportunity_rules else {}
    exit_policy_loss_churn_rows = exit_policy_loss_churn.get("rows") or []
    exit_policy_loss_churn_best = exit_policy_loss_churn_rows[0] if exit_policy_loss_churn_rows else {}
    live_loss_escape_counts = live_loss_escape_analysis.get("escape_class_counts") or {}
    collapse_suppress_summary = collapse_suppress_shadow.get("summary") or {}
    collapse_reentry_summary = collapse_reentry_registry.get("future_summary") or {}
    exit_strict_failure_summaries = exit_strict_failure_drilldown.get("summaries") or []
    exit_strict_failure_common = [
        row for row in exit_strict_failure_summaries
        if str(row.get("window") or "").startswith("new_exit_mix_common_forward")
    ]
    book_gap_loss_guard_opportunity_rows = int(as_float(exit_book_gap_loss_guard_opportunity.get("total_rows")) or 0)
    book_gap_loss_guard_opportunity_soft = int(as_float(exit_book_gap_loss_guard_opportunity.get("soft_exit_rows")) or 0)
    book_gap_loss_guard_opportunity_suppress = int(as_float(exit_book_gap_loss_guard_opportunity.get("would_suppress_rows")) or 0)
    book_gap_value_only_opportunity_rows = int(as_float(exit_book_gap_value_only_opportunity.get("total_rows")) or 0)
    book_gap_value_only_opportunity_value = int(as_float(exit_book_gap_value_only_opportunity.get("value_over_hold_rows")) or 0)
    book_gap_value_only_opportunity_suppress = int(as_float(exit_book_gap_value_only_opportunity.get("would_suppress_rows")) or 0)
    exit_loss_guard_v2_runway = exit_loss_guard_v1_v2_runway.get("v2_strict_runway") or {}
    exit_loss_guard_v1_runway = exit_loss_guard_v1_v2_runway.get("v1_strict_runway") or {}
    exit_loss_guard_v3_runway = exit_loss_guard_v1_v2_runway.get("v3_strict_runway") or {}
    exit_loss_guard_variant_runways = exit_loss_guard_v1_v2_runway.get("strict_variant_runways") or []
    exit_loss_guard_v2_opportunity = exit_loss_guard_v1_v2_runway.get("v2_opportunity") or {}
    exit_loss_guard_v1_v2_v3_windows = exit_loss_guard_v1_v2_v3_contrast.get("windows") or []
    exit_loss_guard_v1_v2_v3_diag = next(
        (row for row in exit_loss_guard_v1_v2_v3_windows if row.get("window") == "all_exit_rows_diagnostic"),
        {},
    )
    exit_loss_guard_v1_v2_v3_v3_strict = next(
        (row for row in exit_loss_guard_v1_v2_v3_windows if row.get("window") == "v3_strict_forward"),
        {},
    )
    exit_book_gap_loss_guard_v3_summary = frozen_exit_book_gap_loss_guard_v3.get("summary") or {}
    exit_book_gap_loss_guard_v3_discovery = frozen_exit_book_gap_loss_guard_v3.get("discovery_summary_existing_exit_sample") or {}
    exit_reduce_geometry_best = (exit_reduce_geometry.get("policies") or [{}])[0]
    frozen_exit_reduce_geometry_summary = frozen_exit_reduce_geometry.get("summary") or {}
    frozen_exit_reduce_geometry_policies = frozen_exit_reduce_geometry.get("counterfactual_policies") or []
    frozen_exit_reduce_geometry_base = next(
        (row for row in frozen_exit_reduce_geometry_policies if row.get("policy") == "base_suppress_reduce_p_hold_ge_075"),
        {},
    )
    frozen_exit_reduce_geometry_side = next(
        (row for row in frozen_exit_reduce_geometry_policies if row.get("policy") == "side_geometry_suppress_reduce_p_hold_ge_075"),
        frozen_exit_reduce_geometry_summary,
    )
    exit_reduce_geometry_opportunity_summary = exit_reduce_geometry_opportunity.get("summary") or {}
    frozen_exit_reduce_geometry_relaxed_summary = frozen_exit_reduce_geometry_relaxed_watch.get("summary") or {}
    frozen_exit_reduce_geometry_relaxed_diag = (frozen_exit_reduce_geometry_relaxed_watch.get("diagnostic") or {}).get("best") or {}
    exit_value_reduce_depth_summary = frozen_exit_value_reduce_depth_composite.get("summary") or {}
    exit_value_reduce_depth_lanes = frozen_exit_value_reduce_depth_composite.get("lanes") or []
    exit_value_reduce_depth_diag = next(
        (lane for lane in exit_value_reduce_depth_lanes if lane.get("lane") == "diagnostic_from_exit_freezes"),
        {},
    )
    exit_value_reduce_depth_diag_best = (exit_value_reduce_depth_diag.get("variants") or [{}])[0]
    exit_value_reduce_depth_diag_summary = exit_value_reduce_depth_diag_best.get("summary") or {}
    exit_value_reduce_depth_opportunity_primary = exit_value_reduce_depth_opportunity.get("primary") or {}
    frozen_stack_post = {}
    for window in frozen_fv_bridge_exit_geometry_stack.get("windows") or []:
        if not isinstance(window, dict) or window.get("window") != "post_freeze_candidate":
            continue
        for scenario in window.get("scenarios") or []:
            if isinstance(scenario, dict) and scenario.get("scenario") == "lead_approved_only":
                frozen_stack_post = scenario
                break
    frozen_stack_rows = int(as_float(frozen_stack_post.get("settled")) or 0)
    frozen_stack_coverage = as_float(frozen_stack_post.get("coverage_pct"))
    frozen_stack_net = as_float(frozen_stack_post.get("stack_net_cents"))
    frozen_stack_matched = int(as_float(frozen_stack_post.get("matched_rows")) or 0)
    frozen_stack_suppressed = int(as_float(frozen_stack_post.get("geometry_suppressed_rows")) or 0)
    frozen_combo_post = {}
    for window in frozen_fv_bridge_exit_combo_stack.get("windows") or []:
        if not isinstance(window, dict) or window.get("window") != "post_freeze_candidate":
            continue
        for scenario in window.get("scenarios") or []:
            if isinstance(scenario, dict) and scenario.get("scenario") == "lead_approved_only":
                frozen_combo_post = scenario
                break
    frozen_combo_rows = int(as_float(frozen_combo_post.get("settled")) or 0)
    frozen_combo_coverage = as_float(frozen_combo_post.get("coverage_pct"))
    frozen_combo_net = as_float(frozen_combo_post.get("candidate_net_cents"))
    frozen_combo_matched = int(as_float(frozen_combo_post.get("matched_rows")) or 0)
    frozen_combo_suppressed = int(as_float(frozen_combo_post.get("suppressed_rows")) or 0)
    integrity_candidates = candidate_integrity.get("candidates") if isinstance(candidate_integrity.get("candidates"), list) else []
    integrity_candidate_count = int(as_float(candidate_integrity.get("candidate_count")) or len(integrity_candidates))
    integrity_pass_count = int(as_float(candidate_integrity.get("integrity_pass_count")) or 0)
    top_integrity = integrity_candidates[0] if integrity_candidates else {}
    top_integrity_blockers = top_integrity.get("blockers") if isinstance(top_integrity.get("blockers"), list) else []
    strict_forward_summary = strict_forward_leaderboard.get("summary") or {}
    strict_forward_top = (strict_forward_leaderboard.get("top_strict_forward_positive") or [{}])[0]
    strict_forward_target_top = (strict_forward_leaderboard.get("closest_strict_target_positive") or [{}])[0]
    strict_forward_excluded_top = (strict_forward_leaderboard.get("excluded_top_diagnostics") or [{}])[0]
    false_family_rows = false_conviction_family.get("ranked") if isinstance(false_conviction_family.get("ranked"), list) else []
    false_family_top = false_family_rows[0] if false_family_rows else {}
    false_family_pass_count = int(as_float(false_conviction_family.get("integrity_pass_count")) or 0)
    registry_complete = candidate_registry_coverage.get("active_registry_complete") is True
    registry_tracker_rows = int(as_float(candidate_registry_coverage.get("tracker_rows")) or 0)
    registry_expected_rows = int(as_float(candidate_registry_coverage.get("active_expected_rows")) or 0)
    registry_missing_rows = len(candidate_registry_coverage.get("active_missing_rows") or [])
    registry_diagnostic_untracked = int(as_float(candidate_registry_coverage.get("diagnostic_candidate_like_untracked_count")) or 0)

    checks = [
        check(
            "broad_market_coverage",
            current_overlay_coverage is not None and 75.0 <= current_overlay_coverage <= 90.0,
            current_overlay_coverage,
            "75-90% forward coverage",
            TARGET_OVERLAY_JSON,
            "Latest target-overlay validator is the current broad-entry FV scoreboard.",
        ),
        check(
            "forward_sample_size",
            current_overlay_settled >= 30,
            current_overlay_settled,
            ">=30 settled forward rows",
            TARGET_OVERLAY_JSON,
            "Hard blocker for promotion; small samples are not accepted.",
        ),
        check(
            "positive_forward_pnl",
            current_overlay_net is not None and current_overlay_net > 0.0,
            current_overlay_net,
            ">0 net cents on forward selected rows",
            TARGET_OVERLAY_JSON,
            "Profitability is necessary but not sufficient.",
        ),
        check(
            "brier_interval_better_than_raw",
            brier_p95 is not None and brier_p95 < 0.0,
            brier_p95,
            "bootstrap Brier p95 < 0",
            TARGET_SEQ_JSON,
            "Current p60 overlay fails this after the newest rows.",
        ),
        check(
            "logloss_interval_better_than_raw",
            logloss_p95 is not None and logloss_p95 < 0.0,
            logloss_p95,
            "bootstrap logloss p95 < 0",
            TARGET_SEQ_JSON,
            "Logloss remains stricter-than-raw on current target surface.",
        ),
        check(
            "p70_interval_better_than_raw",
            p70_brier_p95 is not None and p70_brier_p95 < 0.0 and p70_logloss_p95 is not None and p70_logloss_p95 < 0.0,
            {"settled": p70_settled, "brier_p95": p70_brier_p95, "logloss_p95": p70_logloss_p95},
            "p70 bootstrap Brier p95 < 0 and logloss p95 < 0",
            TARGET_P70_SEQ_JSON,
            "Candidate-specific interval check for the current p70 FV concept; still diagnostic until frozen forward rows arrive.",
        ),
        check(
            "latest_target_overlay_directional_calibration",
            current_overlay_brier_delta is not None and current_overlay_brier_delta < 0.0 and current_overlay_logloss_delta is not None and current_overlay_logloss_delta < 0.0,
            {
                "overlay": current_overlay_best.get("overlay"),
                "settled": current_overlay_settled,
                "coverage_pct": current_overlay_coverage,
                "net_cents": current_overlay_net,
                "brier_delta_vs_raw": current_overlay_brier_delta,
                "logloss_delta_vs_raw": current_overlay_logloss_delta,
            },
            "latest target-overlay best has negative Brier and logloss deltas versus raw",
            TARGET_OVERLAY_JSON,
            "Directional check only; interval/sample gates still control promotion.",
        ),
        check(
            "live_evidence_quality",
            not live_evidence_blockers,
            {
                "approved_entry_rows": approved_entry_rows,
                "simulated_share": simulated_share,
                "blockers": live_evidence_blockers,
            },
            ">=30 settled rows, >=10 approved-entry rows, and simulated/rejected share <=35%",
            TARGET_LIVE_EVIDENCE_JSON,
            "The active target-coverage surface must be backed by enough actual live-approved evidence, not mostly rejected-actionable shadow rows.",
        ),
        check(
            "target_price_friction_attribution_started",
            price_rows > 0,
            {
                "settled": price_rows,
                "net_cents": price_net,
                "worst_tag": worst_price_tag.get("bucket"),
                "worst_tag_settled": worst_price_tag.get("settled"),
                "worst_tag_net_cents": worst_price_tag.get("net_cents"),
            },
            ">0 settled rows in target-coverage price-friction attribution",
            TARGET_PRICE_FRICTION_JSON,
            "This explains whether negative broad-surface PnL is directional FV failure, execution friction, or exit-shaped damage.",
        ),
        check(
            "target_failure_clusters_started",
            bool(failure_clusters),
            {
                "direction_wrong_rows": target_failure_clusters.get("total_direction_wrong_rows"),
                "direction_wrong_net_cents": target_failure_clusters.get("total_direction_wrong_net_cents"),
                "top_cluster": top_failure_cluster.get("cluster"),
                "top_cluster_rows": top_failure_cluster.get("rows"),
                "top_cluster_net_cents": top_failure_cluster.get("net_cents"),
            },
            "mutually exclusive physical failure clusters exist for target-coverage direction-wrong losses",
            TARGET_FAILURE_CLUSTERS_JSON,
            "Prevents overlapping target-loss tags from double-counting the broad-surface failure modes.",
        ),
        check(
            "target_cluster_penalty_watch_started",
            bool(cluster_penalty_lanes),
            {
                "freeze_ts_utc": (target_cluster_penalty_watch.get("state") or {}).get("freeze_ts_utc"),
                "diagnostic_best": cluster_penalty_diag_best.get("candidate"),
                "diagnostic_settled": cluster_penalty_diag_summary.get("settled"),
                "diagnostic_coverage": cluster_penalty_diag_summary.get("coverage_pct"),
                "diagnostic_net_cents": cluster_penalty_diag_summary.get("net_cents"),
                "diagnostic_delta_vs_target_cents": cluster_penalty_diag_best.get("delta_vs_target_cents"),
                "diagnostic_reconstructed_share": cluster_penalty_diag_best.get("reconstructed_share"),
                "diagnostic_blockers": cluster_penalty_diag_best.get("blockers"),
                "post_birth_settled": cluster_penalty_post_summary.get("settled"),
                "post_birth_net_cents": cluster_penalty_post_summary.get("net_cents"),
                "post_birth_blockers": cluster_penalty_post_best.get("blockers"),
            },
            "watch-only cluster-penalty branch exists with strict post-birth tracking",
            TARGET_CLUSTER_PENALTY_WATCH_JSON,
            "Keeps the target failure-cluster repair as continuous penalties while requiring new forward evidence.",
        ),
        check(
            "target_cluster_penalty_runway_started",
            bool(target_cluster_penalty_runway),
            {
                "post_birth_settled": cluster_penalty_post_runway.get("settled"),
                "post_birth_coverage": cluster_penalty_post_runway.get("coverage_pct"),
                "post_birth_net_cents": cluster_penalty_post_runway.get("net_cents"),
                "post_birth_reconstructed_share": cluster_penalty_post_source_runway.get("reconstructed_share"),
                "post_birth_rows_needed": cluster_penalty_post_runway.get("future_settled_rows_needed_for_sample"),
                "post_birth_clean_rows_needed": cluster_penalty_post_source_runway.get("future_clean_approved_rows_needed_for_source_gate"),
                "post_birth_cushion_cents_needed": cluster_penalty_post_runway.get("future_net_cents_needed_for_cushion3"),
                "diagnostic_reconstructed_share": cluster_penalty_diag_source_runway.get("reconstructed_share"),
                "diagnostic_clean_rows_needed": cluster_penalty_diag_source_runway.get("future_clean_approved_rows_needed_for_source_gate"),
            },
            "cluster-penalty source/sample/cushion runway is tracked",
            TARGET_CLUSTER_PENALTY_RUNWAY_JSON,
            "Quantifies how far the continuous target-cluster repair is from sample, source-quality, and full-loss-cushion gates.",
        ),
        check(
            "target_cluster_penalty_source_feasibility_started",
            bool(target_cluster_penalty_source_feasibility),
            {
                "post_birth_required_entries": source_feasibility_post_best.get("required_entries_for_75pct_coverage"),
                "post_birth_approved_available": source_feasibility_post_best.get("approved_available_markets"),
                "post_birth_selected_reconstructed_share": source_feasibility_post_best.get("selected_reconstructed_share"),
                "post_birth_minimum_reconstructed_share": source_feasibility_post_best.get("minimum_reconstructed_share_for_75pct_coverage"),
                "post_birth_source_gate_feasible": source_feasibility_post_best.get("source_gate_feasible_at_current_denominator"),
                "diagnostic_required_entries": source_feasibility_diag_best.get("required_entries_for_75pct_coverage"),
                "diagnostic_approved_available": source_feasibility_diag_best.get("approved_available_markets"),
                "diagnostic_source_gate_feasible": source_feasibility_diag_best.get("source_gate_feasible_at_current_denominator"),
            },
            "cluster-penalty approved-source availability is audited",
            TARGET_CLUSTER_PENALTY_SOURCE_FEASIBILITY_JSON,
            "Checks whether the <=35% reconstructed-share gate is achievable from the current cluster-penalty denominators.",
        ),
        check(
            "target_cluster_penalty_source_displacement_started",
            bool(target_cluster_penalty_source_displacement),
            {
                "post_birth_selected_rejected_settled": displacement_post_rejected.get("settled"),
                "post_birth_selected_rejected_net_cents": displacement_post_rejected.get("net_cents"),
                "post_birth_omitted_approved_settled": displacement_post_omitted.get("settled"),
                "post_birth_omitted_approved_net_cents": displacement_post_omitted.get("net_cents"),
                "post_birth_approved_preferred_net_cents": displacement_post_preferred.get("net_cents"),
                "diagnostic_selected_rejected_net_cents": displacement_diag_rejected.get("net_cents"),
                "diagnostic_omitted_approved_net_cents": displacement_diag_omitted.get("net_cents"),
            },
            "cluster-penalty source displacement mechanism is audited",
            TARGET_CLUSTER_PENALTY_SOURCE_DISPLACEMENT_JSON,
            "Compares selected rejected-actionable rows against omitted approved-entry rows using observable features before proposing any live-usable proxy.",
        ),
        check(
            "approved_entry_book_fv_forward_started",
            approved_book_rows > 0,
            {
                "settled": approved_book_rows,
                "brier_delta_vs_raw": approved_book_brier_delta,
                "logloss_delta_vs_raw": approved_book_logloss_delta,
            },
            ">0 post-freeze settled/scored rows for frozen actual-approved book FV",
            FROZEN_APPROVED_ENTRY_BOOK_FV_JSON,
            "Actual-approved book-anchor calibration is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "approved_entry_book_raw_blend_forward_started",
            approved_book_raw_blend_future_rows > 0,
            {
                "freeze_ts_utc": approved_book_raw_blend_freeze.get("freeze_ts_utc"),
                "primary_candidate": approved_book_raw_blend_freeze.get("primary_candidate"),
                "future_settled": approved_book_raw_blend_future_rows,
                "future_brier_delta_vs_raw": approved_book_raw_blend_future_primary.get("brier_delta_vs_raw"),
                "future_logloss_delta_vs_raw": approved_book_raw_blend_future_primary.get("logloss_delta_vs_raw"),
                "prefreeze_settled": approved_book_raw_blend_prefreeze_primary.get("settled"),
                "prefreeze_brier_delta_vs_raw": approved_book_raw_blend_prefreeze_primary.get("brier_delta_vs_raw"),
                "prefreeze_logloss_delta_vs_raw": approved_book_raw_blend_prefreeze_primary.get("logloss_delta_vs_raw"),
                "blockers": frozen_approved_entry_book_raw_blend.get("blockers"),
            },
            ">0 strict post-freeze settled/scored approved-entry rows for frozen book/raw blend FV",
            FROZEN_APPROVED_ENTRY_BOOK_RAW_BLEND_JSON,
            "Smooth executable-book plus raw-v28 blend is a physics-backed calibration watch, but pre-freeze strength is not promotion evidence.",
        ),
        check(
            "conservative_candidate_scored_forward_started",
            frozen_rows > 0,
            frozen_rows,
            ">0 post-freeze settled/scored rows for frozen conservative FV",
            FROZEN_CONSERVATIVE_JSON,
            "The new better-looking conservative variant has a future entry only after it settles.",
        ),
        check(
            "p70_candidate_scored_forward_started",
            frozen_p70_rows > 0,
            frozen_p70_rows,
            ">0 post-freeze settled/scored rows for frozen p70 FV",
            FROZEN_P70_JSON,
            "The latest diagnostic winner is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "p70_empirical_bayes_candidate_scored_forward_started",
            frozen_p70_eb_rows > 0,
            frozen_p70_eb_rows,
            ">0 post-freeze settled/scored rows for frozen p70 empirical-Bayes FV",
            FROZEN_P70_EB_JSON,
            "The anti-overfit p70 throttle is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "path_state_p70_candidate_scored_forward_started",
            frozen_path_state_rows > 0,
            frozen_path_state_rows,
            ">0 post-freeze settled/scored rows for frozen path-state p70 FV",
            FROZEN_PATH_STATE_P70_JSON,
            "The path/state p70 challenger is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "boundary_recross_shrink_candidate_scored_forward_started",
            frozen_boundary_recross_rows > 0,
            frozen_boundary_recross_rows,
            ">0 post-freeze settled/scored rows for frozen boundary-recross shrink FV",
            FROZEN_BOUNDARY_RECROSS_SHRINK_JSON,
            "The shallow high-recross boundary shrink challenger is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "boundary_temperature_fv_scored_forward_started",
            frozen_boundary_temperature_rows > 0,
            {
                "entries": frozen_boundary_temperature_entries,
                "future_denominator": frozen_boundary_temperature_denominator,
                "rows": frozen_boundary_temperature_rows,
                "adjusted": frozen_boundary_temperature_adjusted,
                "brier_delta_vs_raw": frozen_boundary_temperature_brier,
                "logloss_delta_vs_raw": frozen_boundary_temperature_logloss,
            },
            ">0 post-freeze settled/scored rows for frozen boundary-temperature FV",
            FROZEN_BOUNDARY_TEMPERATURE_FV_JSON,
            "The boundary-temperature FV shrink challenger is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "boundary_energy_fv_entry_scored_forward_started",
            frozen_boundary_energy_rows > 0,
            {
                "entries": frozen_boundary_energy_entries,
                "settled": frozen_boundary_energy_rows,
                "coverage_pct": frozen_boundary_energy_coverage,
                "net_cents": frozen_boundary_energy_net,
                "delta_vs_base": frozen_boundary_energy_delta,
                "diagnostic_delta_vs_base": frozen_boundary_energy_diag_delta,
            },
            ">0 post-freeze settled/scored rows for frozen boundary-energy FV entry bridge",
            FROZEN_BOUNDARY_ENERGY_FV_ENTRY_JSON,
            "The boundary-energy FV entry bridge is frozen separately and must earn future rows from its own timestamp; diagnostic delta is not promotion evidence.",
        ),
        check(
            "early_no_boundary_fv_entry_scored_forward_started",
            frozen_early_no_boundary_rows > 0,
            {
                "entries": frozen_early_no_boundary_entries,
                "settled": frozen_early_no_boundary_rows,
                "coverage_pct": frozen_early_no_boundary_coverage,
                "net_cents": frozen_early_no_boundary_net,
                "avg_brier": frozen_early_no_boundary_brier,
                "delta_vs_base": frozen_early_no_boundary_delta,
                "diagnostic_delta_vs_base": frozen_early_no_boundary_diag_delta,
            },
            ">0 post-freeze settled/scored rows for frozen early-NO boundary FV entry bridge",
            FROZEN_EARLY_NO_BOUNDARY_FV_ENTRY_JSON,
            "The early-NO boundary FV entry bridge is frozen separately and must earn future rows from its own timestamp; diagnostic calibration improvement is not promotion evidence.",
        ),
        check(
            "mid_edge_false_conviction_fv_scored_forward_started",
            frozen_mid_edge_false_conviction_rows > 0,
            frozen_mid_edge_false_conviction_rows,
            ">0 post-freeze settled/scored rows for frozen mid-edge false-conviction FV",
            FROZEN_MID_EDGE_FALSE_CONVICTION_FV_JSON,
            "The mid-edge false-conviction FV shrink challenger is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "boundary_clock_fv_overlay_scored_forward_started",
            frozen_boundary_clock_fv_rows > 0,
            {
                "entries": frozen_boundary_clock_fv_entries,
                "settled": frozen_boundary_clock_fv_rows,
                "adjusted": frozen_boundary_clock_fv_adjusted,
                "brier_delta": frozen_boundary_clock_fv_brier,
                "logloss_delta": frozen_boundary_clock_fv_logloss,
            },
            ">0 post-freeze settled/scored rows for frozen boundary-clock FV overlay",
            FROZEN_BOUNDARY_CLOCK_FV_JSON,
            "The boundary-clock FV overlay is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "side_asymmetry_fv_overlay_scored_forward_started",
            frozen_side_asymmetry_rows > 0,
            {
                "entries": frozen_side_asymmetry_entries,
                "settled": frozen_side_asymmetry_rows,
                "adjusted": frozen_side_asymmetry_adjusted,
                "brier_delta": frozen_side_asymmetry_brier,
                "logloss_delta": frozen_side_asymmetry_logloss,
            },
            ">0 post-freeze settled/scored rows for frozen side-asymmetry FV overlay",
            FROZEN_SIDE_ASYMMETRY_FV_JSON,
            "The combined boundary-clock plus side-asymmetry FV overlay is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "edge_phase_shrink_candidate_scored_forward_started",
            frozen_edge_phase_rows > 0,
            frozen_edge_phase_rows,
            ">0 post-freeze settled/scored rows for frozen edge-phase shrink FV",
            FROZEN_EDGE_PHASE_SHRINK_JSON,
            "The phase-aware boundary shrink challenger is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "edge_phase_edge_gate_scored_forward_started",
            frozen_edge_phase_gate_rows > 0,
            frozen_edge_phase_gate_rows,
            ">0 post-freeze settled/scored rows for frozen edge-phase adjusted-FV edge gate",
            FROZEN_EDGE_PHASE_EDGE_GATE_JSON,
            "The paid-price safety valve is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "edge_gate_opposite_side_scored_forward_started",
            frozen_edge_gate_opposite_rows > 0,
            frozen_edge_gate_opposite_rows,
            ">0 post-freeze settled/scored rows for frozen edge-gate opposite-side replacement",
            FROZEN_EDGE_GATE_OPPOSITE_JSON,
            "The opposite-side replacement challenger is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "early_no_boundary_decay_repair_entry_scored_forward_started",
            frozen_early_no_boundary_decay_rows > 0,
            {
                "entries": frozen_early_no_boundary_decay_entries,
                "settled": frozen_early_no_boundary_decay_rows,
                "coverage_pct": frozen_early_no_boundary_decay_coverage,
                "net_cents": frozen_early_no_boundary_decay_net,
            },
            ">0 post-freeze settled/scored rows for frozen early NO boundary-decay repair entry",
            FROZEN_EARLY_NO_BOUNDARY_DECAY_REPAIR_ENTRY_JSON,
            "The early NO boundary-decay repair challenger is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "false_conviction_approved_repair_scored_forward_started",
            frozen_false_conviction_approved_rows > 0,
            {
                "entries": frozen_false_conviction_approved_entries,
                "settled": frozen_false_conviction_approved_rows,
                "coverage_pct": frozen_false_conviction_approved_coverage,
                "net_cents": frozen_false_conviction_approved_net,
                "reconstructed_share": frozen_false_conviction_approved_recon,
            },
            ">0 post-freeze settled/scored rows for frozen approved-heavy false-conviction repair",
            FROZEN_FALSE_CONVICTION_APPROVED_REPAIR_JSON,
            "The approved-heavy source-quality repair is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "mid_edge_boundary_deception_repair_entry_scored_forward_started",
            frozen_mid_edge_boundary_deception_rows > 0,
            {
                "entries": frozen_mid_edge_boundary_deception_entries,
                "settled": frozen_mid_edge_boundary_deception_rows,
                "coverage_pct": frozen_mid_edge_boundary_deception_coverage,
                "net_cents": frozen_mid_edge_boundary_deception_net,
            },
            ">0 post-freeze settled/scored rows for frozen mid-edge boundary-deception repair entry",
            FROZEN_MID_EDGE_BOUNDARY_DECEPTION_REPAIR_ENTRY_JSON,
            "The mid-edge boundary-deception repair challenger is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "low_recross_repair_entry_scored_forward_started",
            frozen_low_recross_rows > 0,
            {
                "entries": frozen_low_recross_entries,
                "settled": frozen_low_recross_rows,
                "coverage_pct": frozen_low_recross_coverage,
                "net_cents": frozen_low_recross_net,
            },
            ">0 post-freeze settled/scored rows for frozen low-recross repair entry",
            FROZEN_LOW_RECROSS_REPAIR_ENTRY_JSON,
            "The low-recross repair challenger is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "high_raw_p_repair_entry_scored_forward_started",
            frozen_high_raw_p_rows > 0,
            {
                "entries": frozen_high_raw_p_entries,
                "settled": frozen_high_raw_p_rows,
                "coverage_pct": frozen_high_raw_p_coverage,
                "net_cents": frozen_high_raw_p_net,
            },
            ">0 post-freeze settled/scored rows for frozen high-raw-p repair entry",
            FROZEN_HIGH_RAW_P_REPAIR_ENTRY_JSON,
            "The high-raw-p repair challenger is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "p50_book_edge_entry_scored_forward_started",
            frozen_p50_book_edge_rows > 0,
            {
                "entries": frozen_p50_book_edge_entries,
                "settled": frozen_p50_book_edge_rows,
                "coverage_pct": frozen_p50_book_edge_coverage,
                "net_cents": frozen_p50_book_edge_net,
            },
            ">0 post-freeze settled/scored rows for frozen p50 book-edge entry",
            FROZEN_P50_BOOK_EDGE_ENTRY_JSON,
            "The closest validation-count book-edge challenger is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "book_plus05_entry_scored_forward_started",
            frozen_book_plus05_rows > 0,
            {
                "entries": frozen_book_plus05_entries,
                "settled": frozen_book_plus05_rows,
                "coverage_pct": frozen_book_plus05_coverage,
                "net_cents": frozen_book_plus05_net,
            },
            ">0 post-freeze settled/scored rows for frozen book-plus-5pp entry",
            FROZEN_BOOK_PLUS05_ENTRY_JSON,
            "The broad positive-gross book-edge challenger is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "book_plus05_no_cheap_yes_entry_scored_forward_started",
            frozen_book_plus05_no_cheap_yes_rows > 0,
            {
                "entries": frozen_book_plus05_no_cheap_yes_entries,
                "settled": frozen_book_plus05_no_cheap_yes_rows,
                "coverage_pct": frozen_book_plus05_no_cheap_yes_coverage,
                "net_cents": frozen_book_plus05_no_cheap_yes_net,
            },
            ">0 post-freeze settled/scored rows for frozen book-plus-5pp no-cheap-YES entry",
            FROZEN_BOOK_PLUS05_NO_CHEAP_YES_ENTRY_JSON,
            "The broad book-edge challenger with cheap YES boundary-pull rows removed is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "boundary_clock_repair_entry_scored_forward_started",
            frozen_boundary_clock_rows > 0,
            {
                "entries": frozen_boundary_clock_entries,
                "settled": frozen_boundary_clock_rows,
                "coverage_pct": frozen_boundary_clock_coverage,
                "net_cents": frozen_boundary_clock_net,
            },
            ">0 post-freeze settled/scored rows for frozen boundary-clock repair entry",
            FROZEN_BOUNDARY_CLOCK_REPAIR_ENTRY_JSON,
            "The boundary-clock repair challenger is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "boundary_clock_fv_entry_bridge_scored_forward_started",
            frozen_boundary_clock_bridge_rows > 0,
            {
                "entries": frozen_boundary_clock_bridge_entries,
                "settled": frozen_boundary_clock_bridge_rows,
                "coverage_pct": frozen_boundary_clock_bridge_coverage,
                "net_cents": frozen_boundary_clock_bridge_net,
            },
            ">0 post-freeze settled/scored rows for frozen boundary-clock FV entry bridge",
            FROZEN_BOUNDARY_CLOCK_FV_ENTRY_BRIDGE_JSON,
            "The boundary-clock adjusted-edge entry bridge is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "boundary_clock_feature_gate_runway_started",
            bool(boundary_clock_feature_runway_post),
            {
                "candidate": boundary_clock_feature_runway_post.get("candidate"),
                "settled": boundary_clock_feature_runway_post.get("settled"),
                "coverage_pct": boundary_clock_feature_runway_post.get("coverage_pct"),
                "net_cents": boundary_clock_feature_runway_post.get("net_cents"),
                "delta_vs_live_cents": boundary_clock_feature_runway_post.get("delta_vs_live_cents"),
                "future_clean_selected_needed_for_all_gates": boundary_clock_feature_runway_post.get("future_clean_selected_needed_for_all_gates"),
            },
            ">0 post-freeze runway row for frozen observable feature-gate candidate",
            BOUNDARY_CLOCK_FEATURE_GATE_RUNWAY_JSON,
            "Feature-gate runway tracks sample, coverage, source quality, full-loss cushion, and live-baseline delta while the frozen lane matures.",
        ),
        check(
            "boundary_clock_feature_gate_failure_modes_started",
            bool(boundary_clock_feature_failure_post or boundary_clock_feature_failure_diag),
            {
                "post_structural_modes": boundary_clock_feature_failure_post.get("structural_failure_modes"),
                "diagnostic_row_counts": boundary_clock_feature_failure_diag.get("selected_row_failure_counts"),
            },
            "selected-row failure-mode classification for frozen feature-gate candidate",
            BOUNDARY_CLOCK_FEATURE_GATE_FAILURE_MODES_JSON,
            "Maps the feature-gate branch to FV, timing, execution/friction, regime, source-quality, and fragility families without searching new thresholds.",
        ),
        check(
            "boundary_clock_feature_gate_loss_analog_started",
            bool(boundary_clock_feature_loss_post),
            {
                "post_summary_scores": boundary_clock_feature_loss_post.get("summary_scores"),
                "diagnostic_summary_scores": boundary_clock_feature_loss_diag.get("summary_scores"),
            },
            "loss-analog monitor for frozen feature-gate selected rows",
            BOUNDARY_CLOCK_FEATURE_GATE_LOSS_ANALOG_JSON,
            "Tracks whether post-freeze selections resemble frozen diagnostic loss prototypes without creating a new gate or threshold.",
        ),
        check(
            "boundary_clock_feature_gate_row_ledger_started",
            bool(boundary_clock_feature_row_entry_best or boundary_clock_feature_row_bridge_best),
            {
                "entry_best_rule": boundary_clock_feature_row_entry_best.get("rule"),
                "entry_omission_counts": boundary_clock_feature_row_entry_best.get("omission_reason_counts"),
                "bridge_best_rule": boundary_clock_feature_row_bridge_best.get("rule"),
                "bridge_omission_counts": boundary_clock_feature_row_bridge_best.get("omission_reason_counts"),
            },
            "post-freeze row/omission ledger for frozen feature-gate candidate",
            BOUNDARY_CLOCK_FEATURE_GATE_ROW_LEDGER_JSON,
            "Explains coverage misses from observable gate features without changing candidate thresholds.",
        ),
        check(
            "boundary_clock_feature_gate_source_denominator_audit_started",
            bool(boundary_clock_feature_source_entry_best),
            {
                "entry_best_rule": boundary_clock_feature_source_entry_best.get("rule"),
                "entry_selected_reconstructed_share": boundary_clock_feature_source_entry_best.get("selected_reconstructed_share"),
                "entry_approved_source_coverage_pct": boundary_clock_feature_source_entry_best.get("approved_observed_coverage_pct"),
                "entry_reconstructed_source_coverage_pct": boundary_clock_feature_source_entry_best.get("reconstructed_observed_coverage_pct"),
                "entry_omitted_source_net_cents": boundary_clock_feature_source_entry_best.get("omitted_source_net_cents"),
                "bridge_best_rule": boundary_clock_feature_source_bridge_best.get("rule"),
            },
            "post-freeze feature-gate source-denominator audit exists",
            BOUNDARY_CLOCK_FEATURE_GATE_SOURCE_DENOMINATOR_JSON,
            "Shows whether low total coverage comes from missing approved-entry markets or intentionally avoiding reconstructed/source-risk rows.",
        ),
        check(
            "boundary_clock_feature_gate_cheap_tail_risk_audit_started",
            bool(boundary_clock_feature_cheap_tail_entry),
            {
                "entry_broad_settled": (boundary_clock_feature_cheap_tail_entry.get("broad_summary") or {}).get("settled"),
                "entry_broad_coverage_pct": (boundary_clock_feature_cheap_tail_entry.get("broad_summary") or {}).get("coverage_pct"),
                "entry_broad_net_cents": (boundary_clock_feature_cheap_tail_entry.get("broad_summary") or {}).get("net_cents"),
                "entry_broad_reconstructed_share": boundary_clock_feature_cheap_tail_entry.get("broad_reconstructed_share"),
                "entry_cheap_added_rows": boundary_clock_feature_cheap_tail_entry_added.get("rows"),
                "entry_cheap_added_net_cents": boundary_clock_feature_cheap_tail_entry_added.get("net_cents"),
                "entry_cheap_added_wl": boundary_clock_feature_cheap_tail_entry_added.get("wl"),
                "entry_reconstructed_net_without_top_win_cents": boundary_clock_feature_cheap_tail_entry.get("reconstructed_net_without_top_win_cents"),
                "entry_cheap_lt10_half_weighted_net_cents": boundary_clock_feature_cheap_tail_entry_half.get("weighted_net_cents"),
                "bridge_broad_reconstructed_share": boundary_clock_feature_cheap_tail_bridge.get("broad_reconstructed_share"),
            },
            "cheap-tail/source-quality failure-mode audit exists for the frozen feature-gate branch",
            BOUNDARY_CLOCK_FEATURE_GATE_CHEAP_TAIL_RISK_JSON,
            "Tests whether observable cheap-tail rows explain the source-quality blocker and whether continuous size shrinkage helps without creating promotion evidence.",
        ),
        check(
            "boundary_clock_feature_gate_coverage_source_frontier_started",
            bool(boundary_clock_feature_frontier_entry_best),
            {
                "entry_best_rule": boundary_clock_feature_frontier_entry_best.get("rule"),
                "entry_settled": boundary_clock_feature_frontier_entry_summary.get("settled"),
                "entry_coverage_pct": boundary_clock_feature_frontier_entry_summary.get("coverage_pct"),
                "entry_net_cents": boundary_clock_feature_frontier_entry_summary.get("net_cents"),
                "entry_reconstructed_share": boundary_clock_feature_frontier_entry_best.get("reconstructed_share"),
                "entry_clean_broad_positive_count": len(boundary_clock_feature_frontier_entry.get("clean_broad_positive") or []),
                "bridge_best_rule": boundary_clock_feature_frontier_bridge_best.get("rule"),
            },
            "observable-only post-freeze coverage/source frontier audit exists",
            BOUNDARY_CLOCK_FEATURE_GATE_COVERAGE_SOURCE_FRONTIER_JSON,
            "Scans observable threshold tradeoffs after the freeze; source labels are audit-only and no frontier row is promotable by itself.",
        ),
        check(
            "boundary_clock_feature_gate_source_feasibility_bound_started",
            bool(feature_gate_feasibility_entry_75),
            {
                "entry_denominator": feature_gate_feasibility_entry.get("future_denominator"),
                "entry_approved_markets_available": feature_gate_feasibility_entry.get("approved_markets_available"),
                "entry_75pct_source_gate_feasible": feature_gate_feasibility_entry_75.get("source_gate_feasible"),
                "entry_min_reconstructed_share_needed_for_75pct": feature_gate_feasibility_entry_75.get("min_reconstructed_share_needed"),
                "entry_max_source_clean_coverage_pct": feature_gate_feasibility_entry_75.get("max_source_clean_coverage_pct"),
                "bridge_75pct_source_gate_feasible": feature_gate_feasibility_bridge_75.get("source_gate_feasible"),
                "bridge_max_source_clean_coverage_pct": feature_gate_feasibility_bridge_75.get("max_source_clean_coverage_pct"),
            },
            "mathematical feasibility bound for feature-gate coverage plus source-quality gates",
            FEATURE_GATE_SOURCE_FEASIBILITY_BOUND_JSON,
            "Separates a true threshold failure from an observation-supply failure when approved-entry markets are too sparse to hit coverage and source gates together.",
        ),
        check(
            "boundary_clock_feature_gate_frontier_runway_started",
            bool(boundary_clock_feature_frontier_runway_entry),
            {
                "entry_rule": boundary_clock_feature_frontier_runway_entry.get("rule"),
                "entry_entries": boundary_clock_feature_frontier_runway_entry_current.get("entries"),
                "entry_denominator": boundary_clock_feature_frontier_runway_entry_current.get("denominator"),
                "entry_net_cents": boundary_clock_feature_frontier_runway_entry_current.get("net_cents"),
                "entry_reconstructed_share": boundary_clock_feature_frontier_runway_entry_current.get("reconstructed_share"),
                "clean_rows_needed_for_coverage": boundary_clock_feature_frontier_runway_entry_runway.get("clean_rows_needed_for_coverage_gate"),
                "clean_rows_needed_for_source": boundary_clock_feature_frontier_runway_entry_runway.get("clean_rows_needed_for_source_gate"),
                "settled_rows_needed_for_sample": boundary_clock_feature_frontier_runway_entry_runway.get("settled_rows_needed_for_sample_gate"),
                "net_cents_needed_for_cushion": boundary_clock_feature_frontier_runway_entry_runway.get("net_cents_needed"),
            },
            "runway audit for the current observable frontier row exists",
            BOUNDARY_CLOCK_FEATURE_GATE_FRONTIER_RUNWAY_JSON,
            "Quantifies how much clean future evidence the feature-gate frontier needs before source, coverage, sample, and fragility gates can clear.",
        ),
        check(
            "boundary_clock_feature_gate_frontier_mechanism_started",
            bool(boundary_clock_feature_frontier_mechanism_entry),
            {
                "entry_frontier_rule": (boundary_clock_feature_frontier_mechanism_entry.get("frontier_rule") or {}).get("rule_name"),
                "entry_selected": boundary_clock_feature_frontier_mechanism_entry_summary.get("entries"),
                "entry_denominator": boundary_clock_feature_frontier_mechanism_entry.get("future_denominator"),
                "entry_net_cents": boundary_clock_feature_frontier_mechanism_entry_summary.get("net_cents"),
                "gained_net_cents": boundary_clock_feature_frontier_mechanism_gained.get("net_cents"),
                "omitted_net_cents": boundary_clock_feature_frontier_mechanism_omitted.get("net_cents"),
                "omitted_fail_reasons": boundary_clock_feature_frontier_mechanism_entry.get("omitted_fail_reason_counts"),
            },
            "observable frontier mechanism drilldown exists",
            BOUNDARY_CLOCK_FEATURE_GATE_FRONTIER_MECHANISM_JSON,
            "Explains which observable failure mechanisms remain after the soft frontier row; audit-only and not promotion evidence.",
        ),
        check(
            "boundary_clock_feature_gate_outlier_stress_started",
            bool(boundary_clock_feature_outlier_entry),
            {
                "entry_frontier_rule": boundary_clock_feature_outlier_entry.get("frontier_rule"),
                "entry_settled": boundary_clock_feature_outlier_entry.get("settled"),
                "entry_net_cents": boundary_clock_feature_outlier_entry.get("net_cents"),
                "entry_approved_only_net_cents": boundary_clock_feature_outlier_entry.get("approved_only_net_cents"),
                "entry_reconstructed_only_net_cents": boundary_clock_feature_outlier_entry.get("reconstructed_only_net_cents"),
                "entry_top_win_net_cents": boundary_clock_feature_outlier_entry.get("top_win_net_cents"),
                "entry_net_without_top_win_cents": boundary_clock_feature_outlier_entry.get("net_without_top_win_cents"),
                "entry_stress_blockers": boundary_clock_feature_outlier_entry.get("stress_blockers"),
            },
            "observable frontier outlier/source stress audit exists",
            BOUNDARY_CLOCK_FEATURE_GATE_OUTLIER_STRESS_JSON,
            "Tests whether the broad frontier survives source split, top-win concentration, and one-full-loss stress.",
        ),
        check(
            "boundary_clock_feature_gate_frontier_drift_audit_started",
            bool(feature_gate_frontier_drift_entry),
            {
                "entry_parent_rule": feature_gate_frontier_drift_entry_parent.get("rule"),
                "entry_parent_settled": feature_gate_frontier_drift_entry_parent.get("settled"),
                "entry_parent_net_cents": feature_gate_frontier_drift_entry_parent.get("net_cents"),
                "entry_parent_reconstructed_share": feature_gate_frontier_drift_entry_parent.get("reconstructed_share"),
                "entry_strict_settled": feature_gate_frontier_drift_entry_strict.get("settled"),
                "entry_strict_net_cents": feature_gate_frontier_drift_entry_strict.get("net_cents"),
                "entry_strict_reconstructed_share": feature_gate_frontier_drift_entry_strict.get("reconstructed_share"),
                "entry_net_delta_cents": feature_gate_frontier_drift_entry_delta.get("net_delta_cents"),
                "entry_reconstructed_share_delta": feature_gate_frontier_drift_entry_delta.get("reconstructed_share_delta"),
                "entry_blockers": feature_gate_frontier_drift_entry_delta.get("blockers"),
                "bridge_parent_net_cents": feature_gate_frontier_drift_bridge_parent.get("net_cents"),
                "bridge_strict_net_cents": feature_gate_frontier_drift_bridge_strict.get("net_cents"),
                "bridge_blockers": feature_gate_frontier_drift_bridge_delta.get("blockers"),
            },
            "parent frontier versus separately frozen strict clean-broad watch drift audit exists",
            FEATURE_GATE_FRONTIER_DRIFT_AUDIT_JSON,
            "Prevents the attractive parent frontier row from being mistaken for deployable evidence when the strict post-freeze watch has not earned its own gates.",
        ),
        check(
            "boundary_clock_feature_gate_coverage_recovery_started",
            bool(boundary_clock_feature_recovery_entry_broad),
            {
                "entry_strict_settled": boundary_clock_feature_recovery_entry_strict.get("settled"),
                "entry_strict_coverage_pct": boundary_clock_feature_recovery_entry_strict.get("coverage_pct"),
                "entry_strict_net_cents": boundary_clock_feature_recovery_entry_strict.get("net_cents"),
                "entry_strict_reconstructed_share": boundary_clock_feature_recovery_entry.get("strict_reconstructed_share"),
                "entry_broader_rule": boundary_clock_feature_recovery_entry_broad.get("rule"),
                "entry_broader_coverage_pct": boundary_clock_feature_recovery_entry_broad_summary.get("coverage_pct"),
                "entry_broader_net_cents": boundary_clock_feature_recovery_entry_broad_summary.get("net_cents"),
                "entry_broader_reconstructed_share": boundary_clock_feature_recovery_entry_broad.get("reconstructed_share"),
                "entry_broader_added_markets": boundary_clock_feature_recovery_entry_broad_comparison.get("added_markets"),
                "entry_broader_added_net_cents": boundary_clock_feature_recovery_entry_broad_comparison.get("added_net_cents"),
                "entry_broader_rows_needed_for_75pct": boundary_clock_feature_recovery_entry_broad_comparison.get("rows_needed_for_75pct_coverage"),
                "entry_broader_clean_rows_needed_for_source": boundary_clock_feature_recovery_entry_broad_comparison.get("clean_rows_needed_for_source_gate"),
                "bridge_broader_rule": boundary_clock_feature_recovery_bridge_broad.get("rule"),
                "bridge_broader_coverage_pct": boundary_clock_feature_recovery_bridge_broad_summary.get("coverage_pct"),
                "bridge_broader_net_cents": boundary_clock_feature_recovery_bridge_broad_summary.get("net_cents"),
                "bridge_broader_reconstructed_share": boundary_clock_feature_recovery_bridge_broad.get("reconstructed_share"),
                "bridge_broader_added_markets": boundary_clock_feature_recovery_bridge_broad_comparison.get("added_markets"),
                "bridge_broader_added_net_cents": boundary_clock_feature_recovery_bridge_broad_comparison.get("added_net_cents"),
            },
            "post-freeze strict-vs-broader feature-gate coverage recovery audit exists",
            BOUNDARY_CLOCK_FEATURE_GATE_COVERAGE_RECOVERY_JSON,
            "Separates true coverage recovery from source-quality dilution by comparing strict ask-floor rows against broader observable rows market-by-market.",
        ),
        check(
            "boundary_clock_feature_gate_soft_frontier_watch_started",
            bool(boundary_clock_feature_soft_post_entry_best or boundary_clock_feature_soft_diag_entry_best),
            {
                "freeze_ts": (boundary_clock_feature_gate_soft_frontier.get("state") or {}).get("freeze_ts_utc"),
                "diagnostic_best": boundary_clock_feature_soft_diag_entry_best.get("candidate"),
                "diagnostic_settled": boundary_clock_feature_soft_diag_entry_summary.get("settled"),
                "diagnostic_coverage_pct": boundary_clock_feature_soft_diag_entry_summary.get("coverage_pct"),
                "diagnostic_net_cents": boundary_clock_feature_soft_diag_entry_summary.get("net_cents"),
                "post_birth_settled": boundary_clock_feature_soft_post_entry_summary.get("settled"),
                "post_birth_net_cents": boundary_clock_feature_soft_post_entry_summary.get("net_cents"),
                "post_birth_blockers": boundary_clock_feature_soft_post_entry_best.get("blockers"),
            },
            "forward-only soft-frontier watch exists",
            BOUNDARY_CLOCK_FEATURE_GATE_SOFT_FRONTIER_JSON,
            "Freezes the observable soft frontier from its own timestamp; diagnostic rows are not promotion evidence.",
        ),
        check(
            "soft_frontier_post_birth_failure_drilldown_started",
            bool(soft_frontier_failure_entry),
            {
                "generated_at_utc": soft_frontier_post_birth_failure_drilldown.get("generated_at_utc"),
                "rule": soft_frontier_post_birth_failure_drilldown.get("rule"),
                "entry_settled": soft_frontier_failure_entry_summary.get("settled"),
                "entry_coverage_pct": soft_frontier_failure_entry_summary.get("coverage_pct"),
                "entry_net_cents": soft_frontier_failure_entry_summary.get("net_cents"),
                "entry_reconstructed_share": soft_frontier_failure_entry.get("reconstructed_share"),
                "entry_full_loss_cushion": soft_frontier_failure_entry.get("full_loss_cushion"),
                "entry_loss_tag_counts": soft_frontier_failure_entry.get("loss_tag_counts"),
                "entry_loss_exit_delta_vs_hold_cents": soft_frontier_failure_entry.get("loss_exit_delta_vs_hold_cents"),
                "bridge_settled": soft_frontier_failure_bridge_summary.get("settled"),
                "bridge_net_cents": soft_frontier_failure_bridge_summary.get("net_cents"),
                "bridge_loss_tag_counts": soft_frontier_failure_bridge.get("loss_tag_counts"),
            },
            "strict post-birth soft-frontier failure drilldown exists",
            SOFT_FRONTIER_POST_BIRTH_FAILURE_DRILLDOWN_JSON,
            "Classifies the current soft-frontier losses and checks whether current exits helped or hurt versus holding.",
        ),
        check(
            "boundary_clock_feature_gate_soft_frontier_exit_stack_started",
            bool(boundary_clock_feature_gate_soft_frontier_exit_stack),
            {
                "freeze_ts": (boundary_clock_feature_gate_soft_frontier_exit_stack.get("freeze") or {}).get("freeze_ts_utc"),
                "exit_rows_available": boundary_clock_feature_gate_soft_frontier_exit_stack.get("exit_rows_available"),
                "best_candidate": boundary_clock_feature_soft_exit_stack_best.get("candidate"),
                "best_entry_settled": boundary_clock_feature_soft_exit_stack_best_summary.get("settled"),
                "best_joined_exit_rows": boundary_clock_feature_soft_exit_stack_best.get("joined_exit_rows"),
                "best_joined_exit_net_cents": boundary_clock_feature_soft_exit_stack_best.get("joined_exit_candidate_cents"),
                "blockers": boundary_clock_feature_soft_exit_stack_best.get("blockers"),
            },
            "frozen soft-frontier entry plus guarded-exit stack watch exists",
            BOUNDARY_CLOCK_FEATURE_GATE_SOFT_FRONTIER_EXIT_STACK_JSON,
            "This is the broad-entry mix/match lane; only post-stack-freeze joined rows count for promotion.",
        ),
        check(
            "feature_gate_cheap_tail_shrink_watch_started",
            bool(feature_gate_cheap_tail_shrink_watch),
            {
                "freeze_ts": (feature_gate_cheap_tail_shrink_watch.get("state") or {}).get("freeze_ts_utc"),
                "best_policy": feature_gate_cheap_tail_shrink_best.get("policy"),
                "strict_settled": feature_gate_cheap_tail_shrink_best.get("settled"),
                "strict_coverage_pct": feature_gate_cheap_tail_shrink_best.get("coverage_pct"),
                "strict_weighted_net_cents": feature_gate_cheap_tail_shrink_best.get("weighted_net_cents"),
                "strict_blockers": feature_gate_cheap_tail_shrink_best.get("blockers"),
            },
            "frozen feature-gate cheap-tail notional-shrink watch exists",
            FEATURE_GATE_CHEAP_TAIL_SHRINK_WATCH_JSON,
            "Freezes observable cheap-tail size shrinkage from its own timestamp; older cheap-tail audit rows stay diagnostic.",
        ),
        check(
            "soft_frontier_size_shrink_portfolio_started",
            bool(soft_frontier_size_shrink),
            {
                "freeze_ts": (soft_frontier_size_shrink.get("state") or {}).get("freeze_ts_utc"),
                "diagnostic_best": soft_frontier_size_shrink_diag_best.get("candidate"),
                "diagnostic_settled": soft_frontier_size_shrink_diag_summary.get("settled"),
                "diagnostic_coverage_pct": soft_frontier_size_shrink_diag_summary.get("coverage_pct"),
                "diagnostic_net_cents": soft_frontier_size_shrink_diag_summary.get("net_cents"),
                "strict_best": soft_frontier_size_shrink_strict_best.get("candidate"),
                "strict_settled": soft_frontier_size_shrink_strict_summary.get("settled"),
                "strict_net_cents": soft_frontier_size_shrink_strict_summary.get("net_cents"),
                "strict_blockers": soft_frontier_size_shrink_strict_best.get("blockers"),
            },
            "frozen soft-frontier size/risk overlay watch exists",
            SOFT_FRONTIER_SIZE_SHRINK_JSON,
            "Tests continuous size shrinkage for near-boundary/mid-cheap fragility; only post-shrink-freeze rows count for promotion.",
        ),
        check(
            "soft_frontier_midprice_boundary_shrink_started",
            bool(soft_frontier_midprice_boundary_shrink),
            {
                "freeze_ts": (soft_frontier_midprice_boundary_shrink.get("state") or {}).get("freeze_ts_utc"),
                "diagnostic_best": soft_frontier_midprice_diag_best.get("candidate"),
                "diagnostic_settled": soft_frontier_midprice_diag_summary.get("settled"),
                "diagnostic_coverage_pct": soft_frontier_midprice_diag_summary.get("coverage_pct"),
                "diagnostic_net_cents": soft_frontier_midprice_diag_summary.get("net_cents"),
                "diagnostic_delta_vs_raw": soft_frontier_midprice_diag_summary.get("delta_vs_unweighted_cents"),
                "diagnostic_band_rows": soft_frontier_midprice_diag_summary.get("midprice_boundary_rows"),
                "diagnostic_band_raw_net_cents": soft_frontier_midprice_diag_summary.get("midprice_boundary_raw_net_cents"),
                "diagnostic_band_weighted_net_cents": soft_frontier_midprice_diag_summary.get("midprice_boundary_weighted_net_cents"),
                "strict_best": soft_frontier_midprice_strict_best.get("candidate"),
                "strict_settled": soft_frontier_midprice_strict_summary.get("settled"),
                "strict_net_cents": soft_frontier_midprice_strict_summary.get("net_cents"),
                "strict_blockers": soft_frontier_midprice_strict_best.get("blockers"),
            },
            "frozen soft-frontier mid-price boundary size/risk overlay watch exists",
            SOFT_FRONTIER_MIDPRICE_BOUNDARY_SHRINK_JSON,
            "Tests whether a narrow observable near-boundary mid-price loss pocket can be repaired by size shrinkage without losing broad coverage; only post-midprice-shrink rows count for promotion.",
        ),
        check(
            "soft_frontier_midprice_boundary_exit_stack_runway_started",
            bool(soft_frontier_midprice_boundary_exit_stack_runway),
            {
                "stack_freeze_ts": (soft_frontier_midprice_boundary_exit_stack.get("freeze") or {}).get("freeze_ts_utc"),
                "best_overlap": soft_frontier_midprice_exit_stack_best.get("candidate"),
                "best_overlap_entry_settled": soft_frontier_midprice_exit_stack_entry_summary.get("settled"),
                "best_overlap_joined_exits": soft_frontier_midprice_exit_stack_best.get("joined_exit_rows"),
                "best_overlap_post_stack_joined_exits": soft_frontier_midprice_exit_stack_best.get("post_stack_joined_exit_rows"),
                "best_overlap_weighted_exit_net_cents": soft_frontier_midprice_exit_stack_best.get("weighted_joined_exit_candidate_cents"),
                "best_overlap_post_stack_net_cents": soft_frontier_midprice_exit_stack_best.get("post_stack_weighted_exit_candidate_cents"),
                "runway_best": soft_frontier_midprice_exit_stack_runway_best.get("candidate"),
                "post_stack_joined_rows_needed": soft_frontier_midprice_exit_stack_runway_best.get("post_stack_joined_rows_needed_for_sample_gate"),
                "post_stack_weighted_cents_needed_for_cushion3": soft_frontier_midprice_exit_stack_runway_best.get("post_stack_weighted_cents_needed_for_cushion3"),
                "runway_blockers": soft_frontier_midprice_exit_stack_runway_best.get("runway_blockers"),
            },
            "frozen soft-frontier mid-price boundary entry+exit stack runway exists",
            SOFT_FRONTIER_MIDPRICE_BOUNDARY_EXIT_STACK_RUNWAY_JSON,
            "Separates diagnostic overlap from promotion-relevant post-stack joined exits for the combined broad-entry shrink plus guarded-exit branch.",
        ),
        check(
            "boundary_clock_feature_gate_ask_floor_mechanism_started",
            bool(boundary_clock_feature_ask_post_entry or boundary_clock_feature_ask_diag_entry),
            {
                "post_delta_net_cents": boundary_clock_feature_ask_post_entry.get("delta_net_cents"),
                "post_switched_tags": boundary_clock_feature_ask_post_entry.get("switched_failure_tag_counts"),
                "diagnostic_delta_net_cents": boundary_clock_feature_ask_diag_entry.get("delta_net_cents"),
                "diagnostic_switched_tags": boundary_clock_feature_ask_diag_entry.get("switched_failure_tag_counts"),
            },
            "ask-floor mechanism audit for frozen feature-gate candidate",
            BOUNDARY_CLOCK_FEATURE_GATE_ASK_FLOOR_JSON,
            "Compares frozen base rule versus frozen ask-floor variant to test whether omitted/replaced rows share a physical failure pattern.",
        ),
        check(
            "boundary_clock_feature_gate_continuous_penalty_started",
            bool(boundary_clock_feature_penalty_post_entry or boundary_clock_feature_penalty_diag_entry),
            {
                "freeze_ts": (boundary_clock_feature_gate_continuous_penalty.get("state") or {}).get("freeze_ts_utc"),
                "diagnostic_best": boundary_clock_feature_penalty_diag_entry_best.get("candidate"),
                "diagnostic_settled": boundary_clock_feature_penalty_diag_entry_summary.get("settled"),
                "diagnostic_coverage": boundary_clock_feature_penalty_diag_entry_summary.get("coverage_pct"),
                "diagnostic_net_cents": boundary_clock_feature_penalty_diag_entry_summary.get("net_cents"),
                "pre_birth_best": boundary_clock_feature_penalty_pre_entry_best.get("candidate"),
                "pre_birth_coverage": boundary_clock_feature_penalty_pre_entry_summary.get("coverage_pct"),
                "pre_birth_net_cents": boundary_clock_feature_penalty_pre_entry_summary.get("net_cents"),
                "post_birth_settled": boundary_clock_feature_penalty_post_entry_summary.get("settled"),
                "post_birth_net_cents": boundary_clock_feature_penalty_post_entry_summary.get("net_cents"),
            },
            "continuous cheap-side penalty watch for boundary-clock feature gate",
            BOUNDARY_CLOCK_FEATURE_GATE_CONTINUOUS_PENALTY_JSON,
            "Starts a new post-birth forward monitor; older rows are diagnostic only and cannot satisfy promotion gates.",
        ),
        check(
            "boundary_clock_feature_gate_continuous_penalty_stress_started",
            bool(boundary_clock_feature_penalty_stress_post_entry or boundary_clock_feature_penalty_stress_diag_entry),
            {
                "post_birth_settled": boundary_clock_feature_penalty_stress_post_entry.get("settled"),
                "post_birth_coverage": boundary_clock_feature_penalty_stress_post_entry.get("coverage_pct"),
                "post_birth_net_cents": boundary_clock_feature_penalty_stress_post_entry.get("net_cents"),
                "post_birth_clean_rows_needed": boundary_clock_feature_penalty_stress_post_entry.get("future_clean_selected_needed_for_all_count_gates"),
                "post_birth_cushion_cents_needed": boundary_clock_feature_penalty_stress_post_entry.get("net_cents_needed_for_cushion3"),
                "post_birth_top_win_net_cents": boundary_clock_feature_penalty_stress_post_entry.get("top_win_net_cents"),
                "post_birth_stress_blockers": boundary_clock_feature_penalty_stress_post_entry.get("stress_blockers"),
            },
            "continuous penalty source/runway/outlier stress audit exists",
            BOUNDARY_CLOCK_FEATURE_GATE_CONTINUOUS_PENALTY_STRESS_JSON,
            "Quantifies clean-row runway, source split, top-win concentration, and full-loss cushion for the continuous cheap-side penalty watch.",
        ),
        check(
            "boundary_clock_feature_gate_residual_loss_mechanism_started",
            bool(boundary_clock_feature_residual_diag_entry),
            {
                "prototype_tags": boundary_clock_feature_gate_residual_loss.get("prototype_tag_counts"),
                "diagnostic_scores": boundary_clock_feature_residual_diag_entry.get("residual_summary"),
                "pre_birth_scores": boundary_clock_feature_residual_pre_entry.get("residual_summary"),
                "post_birth_scores": boundary_clock_feature_residual_post_entry.get("residual_summary"),
            },
            "residual loss mechanism audit after cheap-side repair",
            BOUNDARY_CLOCK_FEATURE_GATE_RESIDUAL_LOSS_JSON,
            "Identifies remaining expensive-boundary/reversal loss prototypes and watches post-birth rows for similarity; warning-only because many wins also resemble the prototypes.",
        ),
        check(
            "weak_reversal_residual_repair_scored_forward_started",
            frozen_weak_reversal_residual_repair_rows > 0,
            {
                "entries": frozen_weak_reversal_residual_repair_entries,
                "settled": frozen_weak_reversal_residual_repair_rows,
                "coverage_pct": frozen_weak_reversal_residual_repair_coverage,
                "net_cents": frozen_weak_reversal_residual_repair_net,
            },
            ">0 post-freeze settled/scored rows for frozen weak-reversal residual repair",
            FROZEN_WEAK_REVERSAL_RESIDUAL_REPAIR_JSON,
            "The weak-boundary reversal plus NO-side 5-8pp residual repair is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "weak_reversal_residual_fv_shrink_scored_forward_started",
            frozen_weak_reversal_residual_fv_rows > 0,
            {
                "future_denominator": frozen_weak_reversal_residual_fv_denominator,
                "rows": frozen_weak_reversal_residual_fv_rows,
                "brier_delta_vs_raw": frozen_weak_reversal_residual_fv_brier,
                "logloss_delta_vs_raw": frozen_weak_reversal_residual_fv_logloss,
            },
            ">0 post-freeze scored rows for frozen weak-reversal residual FV shrink",
            FROZEN_WEAK_REVERSAL_RESIDUAL_FV_SHRINK_JSON,
            "The weak-reversal residual half-to-50 calibration overlay is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "no_mid_edge_fv_scored_forward_started",
            frozen_no_mid_edge_fv_rows > 0,
            {
                "future_denominator": frozen_no_mid_edge_fv_denominator,
                "rows": frozen_no_mid_edge_fv_rows,
                "brier_delta_vs_raw": frozen_no_mid_edge_fv_brier,
                "logloss_delta_vs_raw": frozen_no_mid_edge_fv_logloss,
            },
            ">0 post-freeze scored rows for frozen broader NO mid-edge FV shrink",
            FROZEN_NO_MID_EDGE_FV_JSON,
            "The broader NO 5-8pp book-anchor FV shrink is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "early_boundary_wait_repair_scored_forward_started",
            frozen_early_boundary_wait_rows > 0,
            {
                "entries": frozen_early_boundary_wait_entries,
                "settled": frozen_early_boundary_wait_rows,
                "coverage_pct": frozen_early_boundary_wait_coverage,
                "net_cents": frozen_early_boundary_wait_net,
            },
            ">0 post-freeze settled/scored rows for frozen early-boundary wait repair",
            FROZEN_EARLY_BOUNDARY_WAIT_REPAIR_JSON,
            "The early-boundary wait/repair challenger is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "early_boundary_opposite_wait_repair_scored_forward_started",
            frozen_early_boundary_opposite_wait_rows > 0,
            {
                "entries": frozen_early_boundary_opposite_wait_entries,
                "settled": frozen_early_boundary_opposite_wait_rows,
                "coverage_pct": frozen_early_boundary_opposite_wait_coverage,
                "net_cents": frozen_early_boundary_opposite_wait_net,
            },
            ">0 post-freeze settled/scored rows for frozen early-boundary opposite wait repair",
            FROZEN_EARLY_BOUNDARY_OPPOSITE_WAIT_REPAIR_JSON,
            "The early-boundary opposite-side wait/repair challenger is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "phi_forgetting_fv_scored_forward_started",
            phi_rows > 0,
            {
                "overlay": phi_best_overlay,
                "settled": phi_rows,
                "coverage_pct": phi_coverage,
                "brier_delta_vs_raw": phi_brier_delta,
                "logloss_delta_vs_raw": phi_logloss_delta,
            },
            ">0 post-freeze settled/scored rows for frozen phi-forgetting FV overlays",
            PHI_FORGETTING_FV_JSON,
            "The phi half-shrink idea is frozen separately; discovery calibration improvement is not promotion evidence.",
        ),
        check(
            "confidence_shrink_bakeoff_scored_forward_started",
            shrink_rows > 0,
            {
                "overlay": shrink_best_overlay,
                "settled": shrink_rows,
                "coverage_pct": shrink_coverage,
                "brier_delta_vs_raw": shrink_brier_delta,
                "logloss_delta_vs_raw": shrink_logloss_delta,
                "diagnostic_best": shrink_diag_best.get("overlay"),
            },
            ">0 post-freeze settled/scored rows for frozen confidence-shrink schedule bakeoff",
            CONFIDENCE_SHRINK_BAKEOFF_JSON,
            "The shrink-schedule bakeoff is frozen separately; diagnostic winner does not count until forward rows arrive.",
        ),
        check(
            "hybrid_confidence_shrink_fv_scored_forward_started",
            hybrid_rows > 0,
            {
                "overlay": hybrid_best_overlay,
                "settled": hybrid_rows,
                "coverage_pct": hybrid_coverage,
                "brier_delta_vs_raw": hybrid_brier_delta,
                "logloss_delta_vs_raw": hybrid_logloss_delta,
                "diagnostic_best": hybrid_diag_best.get("overlay"),
            },
            ">0 post-freeze settled/scored rows for frozen hybrid confidence-shrink FV overlay",
            HYBRID_CONFIDENCE_SHRINK_JSON,
            "The hybrid shrink overlay is frozen separately; discovery improvement is not promotion evidence.",
        ),
        check(
            "target_surface_hybrid_fv_scored_forward_started",
            target_hybrid_settled > 0,
            {
                "best_overlay": target_hybrid_best.get("overlay"),
                "hybrid_settled": target_hybrid_settled,
                "hybrid_coverage_pct": target_hybrid_coverage,
                "hybrid_net_cents": target_hybrid_net,
                "hybrid_brier_delta_vs_raw": target_hybrid_brier_delta,
                "hybrid_logloss_delta_vs_raw": target_hybrid_logloss_delta,
            },
            ">0 scored rows for hybrid FV on the fixed target-coverage surface",
            TARGET_SURFACE_HYBRID_JSON,
            "Target-surface hybrid FV must improve calibration on the goal-relevant rows; P&L still comes from selected trades.",
        ),
        check(
            "target_hybrid_veto_repair_scored_forward_started",
            target_hybrid_veto_post_rows > 0,
            {
                "best_candidate": target_hybrid_veto_post_best.get("candidate"),
                "entries": target_hybrid_veto_post_entries,
                "settled": target_hybrid_veto_post_rows,
                "coverage_pct": target_hybrid_veto_post_coverage,
                "net_cents": target_hybrid_veto_post_net,
                "diagnostic_best": target_hybrid_veto_diag_best.get("candidate"),
                "diagnostic_net_cents": target_hybrid_veto_diag_net,
                "diagnostic_delta_vs_target_cents": target_hybrid_veto_diag_delta,
            },
            ">0 post-freeze settled rows for target hybrid-veto repair",
            TARGET_HYBRID_VETO_REPAIR_JSON,
            "Hybrid-veto repair is frozen separately; diagnostic loss reduction is not promotion evidence.",
        ),
        check(
            "hybrid_boundary_entry_stack_scored_forward_started",
            hybrid_boundary_stack_post_rows > 0,
            {
                "best_candidate": hybrid_boundary_stack_post_best.get("candidate"),
                "entries": hybrid_boundary_stack_post_entries,
                "settled": hybrid_boundary_stack_post_rows,
                "coverage_pct": hybrid_boundary_stack_post_coverage,
                "net_cents": hybrid_boundary_stack_post_net,
                "diagnostic_best": hybrid_boundary_stack_diag_best.get("candidate"),
                "diagnostic_net_cents": hybrid_boundary_stack_diag_net,
                "diagnostic_delta_vs_target_cents": hybrid_boundary_stack_diag_delta,
                "promotion_blockers": hybrid_boundary_stack_post_best.get("promotion_blockers"),
                "source_stress_post_reconstructed_share": hybrid_boundary_source_stress_post.get("reconstructed_share"),
                "source_stress_post_clean_rows_needed": hybrid_boundary_source_stress_post.get("clean_rows_needed_for_source_gate"),
                "source_stress_post_sample_rows_needed": hybrid_boundary_source_stress_post.get("settled_rows_needed_for_sample_gate"),
                "source_stress_post_cushion_cents_needed": hybrid_boundary_source_stress_post.get("net_cents_needed_for_cushion3"),
                "source_stress_post_blockers": hybrid_boundary_source_stress_post.get("stress_blockers"),
                "frontier_diagnostic_best": hybrid_boundary_frontier_diag_best.get("candidate"),
                "frontier_diagnostic_coverage_pct": hybrid_boundary_frontier_diag_summary.get("coverage_pct"),
                "frontier_diagnostic_net_cents": hybrid_boundary_frontier_diag_summary.get("net_cents"),
                "frontier_diagnostic_reconstructed_share": hybrid_boundary_frontier_diag_integrity.get("reconstructed_share"),
                "frontier_diagnostic_blockers": hybrid_boundary_frontier_diag_best.get("blockers"),
                "dilution_diagnostic_clean_rows_needed": hybrid_boundary_dilution_diag.get("approved_needed_for_recon35"),
                "dilution_diagnostic_max_full_losses_positive": hybrid_boundary_dilution_diag.get("max_full_losses_while_positive"),
                "dilution_post_clean_rows_needed_for_gate": hybrid_boundary_dilution_post.get("future_approved_selected_needed_for_gate"),
            },
            ">0 post-freeze settled rows for combined hybrid/boundary entry stack",
            HYBRID_BOUNDARY_ENTRY_STACK_JSON,
            "The combined stack is newly frozen; diagnostic profitability is not promotion evidence, and source-quality remains a blocker even in the frontier audit.",
        ),
        check(
            "exit_reduce_suppression_scored_forward_started",
            frozen_exit_reduce_rows > 0,
            frozen_exit_reduce_rows,
            ">0 post-freeze settled/scored rows for frozen probability-reduce suppression",
            FROZEN_EXIT_REDUCE_SUPPRESSION_JSON,
            "The exit-policy challenger is frozen separately and must earn future rows from its own timestamp.",
        ),
        check(
            "exit_reduce_suppression_risk_ledger_started",
            int(as_float(exit_reduce_risk_suppressed.get("rows")) or 0) > 0,
            {
                "suppressed_rows": exit_reduce_risk_suppressed.get("rows"),
                "suppressed_net_delta_cents": exit_reduce_risk_suppressed.get("net_delta_cents"),
                "helpful_rows": exit_reduce_risk_helpful.get("rows"),
                "helpful_net_delta_cents": exit_reduce_risk_helpful.get("net_delta_cents"),
                "harmful_rows": exit_reduce_risk_harmful.get("rows"),
                "harmful_net_delta_cents": exit_reduce_risk_harmful.get("net_delta_cents"),
            },
            ">0 classified suppressed exits in the reduce-suppression risk ledger",
            EXIT_REDUCE_SUPPRESSION_RISK_LEDGER_JSON,
            "Explains the exit-policy blocker by separating recovered winners from harmful loss-control suppression; this is diagnostic, not promotion evidence.",
        ),
        check(
            "exit_reduce_blocker_decision_started",
            bool(exit_reduce_blocker_decision.get("decision")),
            {
                "decision": exit_reduce_blocker_decision.get("decision"),
                "blanket_helpful_harmful": (
                    f"{(exit_reduce_blocker_decision.get('base_blanket_suppression') or {}).get('suppressed_helpful_rows')}/"
                    f"{(exit_reduce_blocker_decision.get('base_blanket_suppression') or {}).get('suppressed_harmful_rows')}"
                ),
                "blanket_loss_control_cost_cents": (exit_reduce_blocker_decision.get("base_blanket_suppression") or {}).get("suppressed_loss_control_cost_cents"),
                "child_watch_summaries": exit_reduce_blocker_decision.get("child_watch_summaries"),
            },
            "consolidated blocker decision for blanket reducer and child loss-control watches",
            EXIT_REDUCE_BLOCKER_DECISION_JSON,
            "Keeps the exit-policy conclusion durable: blanket reduce suppression remains not promotable, while cleaner child watches need their own strict post-freeze suppressions.",
        ),
        check(
            "exit_reduce_drift_guard_watch_started",
            bool((exit_reduce_drift_guard_watch.get("state") or {}).get("freeze_ts_utc")),
            {
                "freeze_ts": (exit_reduce_drift_guard_watch.get("state") or {}).get("freeze_ts_utc"),
                "diagnostic_best": exit_reduce_drift_guard_diag.get("policy"),
                "diagnostic_suppressed_wl": f"{exit_reduce_drift_guard_diag.get('suppressed_helpful')}/{exit_reduce_drift_guard_diag.get('suppressed_harmful')}",
                "diagnostic_delta_vs_current_cents": exit_reduce_drift_guard_diag.get("delta_vs_current_cents"),
                "strict_settled": exit_reduce_drift_guard_post.get("settled"),
                "strict_suppressed": exit_reduce_drift_guard_post.get("suppressed"),
                "strict_delta_vs_current_cents": exit_reduce_drift_guard_post.get("delta_vs_current_cents"),
                "strict_blockers": exit_reduce_drift_guard_post.get("blockers"),
            },
            "frozen child watch exists for drift-guarded probability-reduce suppression",
            EXIT_REDUCE_DRIFT_GUARD_WATCH_JSON,
            "Tests whether the physical loss-control repair survives after its own freeze; diagnostic 9/0 suppressions are mechanism evidence only.",
        ),
        check(
            "exit_reduce_loss_control_signature_started",
            int(as_float(exit_reduce_signature_summary.get("suppressed_rows")) or 0) > 0,
            {
                "suppressed_rows": exit_reduce_signature_summary.get("suppressed_rows"),
                "helpful_rows": exit_reduce_signature_summary.get("helpful_rows"),
                "harmful_rows": exit_reduce_signature_summary.get("harmful_rows"),
                "total_delta_cents": exit_reduce_signature_summary.get("total_delta_cents"),
                "best_separator": {
                    "feature": exit_reduce_signature_best.get("feature"),
                    "direction": exit_reduce_signature_best.get("direction"),
                    "threshold": exit_reduce_signature_best.get("threshold"),
                    "selected_rows": exit_reduce_signature_best.get("selected_rows"),
                    "selected_wl": f"{exit_reduce_signature_best.get('selected_helpful')}/{exit_reduce_signature_best.get('selected_harmful')}",
                    "selected_delta_cents": exit_reduce_signature_best.get("selected_delta_cents"),
                    "excluded_helpful": exit_reduce_signature_best.get("helpful_excluded"),
                    "excluded_harmful": exit_reduce_signature_best.get("harmful_excluded"),
                },
            },
            ">0 suppressed exits in the reduce loss-control signature report",
            EXIT_REDUCE_LOSS_CONTROL_SIGNATURE_JSON,
            "Diagnostic-only row signature for harmful versus helpful reduce suppressions; separators must be frozen separately before use.",
        ),
        check(
            "exit_reduce_loss_control_actionability_started",
            bool(exit_reduce_actionability_best_observable or exit_reduce_actionability_best_hindsight),
            {
                "best_hindsight_feature": exit_reduce_actionability_best_hindsight.get("feature"),
                "best_hindsight_direction": exit_reduce_actionability_best_hindsight.get("direction"),
                "best_hindsight_threshold": exit_reduce_actionability_best_hindsight.get("threshold"),
                "best_observable_feature": exit_reduce_actionability_best_observable.get("feature"),
                "best_observable_direction": exit_reduce_actionability_best_observable.get("direction"),
                "best_observable_threshold": exit_reduce_actionability_best_observable.get("threshold"),
                "best_observable_selected_wl": f"{exit_reduce_actionability_best_observable.get('selected_helpful')}/{exit_reduce_actionability_best_observable.get('selected_harmful')}",
                "best_observable_delta_cents": exit_reduce_actionability_best_observable.get("selected_delta_cents"),
                "best_observable_frozen_watch": exit_reduce_actionability_best_observable.get("frozen_watch"),
                "observable_needing_new_freeze_count": len(exit_reduce_actionability_needs_freeze),
            },
            "loss-control signature actionability audit exists",
            EXIT_REDUCE_LOSS_CONTROL_ACTIONABILITY_JSON,
            "Separates hindsight post-exit diagnostics from observable exit-time separators before deciding what deserves a frozen watch.",
        ),
        check(
            "exit_reduce_loss_control_refinement_started",
            bool(exit_reduce_refinement_post_best or exit_reduce_refinement_diag_best),
            {
                "freeze_ts": (exit_reduce_refinement.get("state") or {}).get("freeze_ts_utc"),
                "diagnostic_best": exit_reduce_refinement_diag_best.get("candidate"),
                "diagnostic_settled": exit_reduce_refinement_diag_summary.get("settled"),
                "diagnostic_delta_vs_current_cents": exit_reduce_refinement_diag_summary.get("delta_vs_current_cents"),
                "diagnostic_suppressed_wl": f"{exit_reduce_refinement_diag_summary.get('suppressed_winners')}/{exit_reduce_refinement_diag_summary.get('suppressed_losers')}",
                "diagnostic_loss_control_cost_cents": exit_reduce_refinement_diag_summary.get("loss_control_cost_cents"),
                "post_birth_settled": exit_reduce_refinement_post_summary.get("settled"),
                "post_birth_delta_vs_current_cents": exit_reduce_refinement_post_summary.get("delta_vs_current_cents"),
                "post_birth_blockers": exit_reduce_refinement_post_best.get("blockers"),
            },
            "forward-only reduce-exit loss-control refinement exists",
            EXIT_REDUCE_REFINEMENT_JSON,
            "Freezes p-hold/drawdown refinements from their own timestamp; diagnostic rows still include suppressed losers and cannot promote the rule.",
        ),
        check(
            "exit_reduce_depth_gate_started",
            bool(exit_reduce_depth_post_best or exit_reduce_depth_diag_best),
            {
                "freeze_ts": (exit_reduce_depth_gate.get("state") or {}).get("freeze_ts_utc"),
                "diagnostic_best": exit_reduce_depth_diag_best.get("candidate"),
                "diagnostic_settled": exit_reduce_depth_diag_summary.get("settled"),
                "diagnostic_delta_vs_current_cents": exit_reduce_depth_diag_summary.get("delta_vs_current_cents"),
                "diagnostic_suppressed_wl": f"{exit_reduce_depth_diag_summary.get('suppressed_winners')}/{exit_reduce_depth_diag_summary.get('suppressed_losers')}",
                "diagnostic_loss_cost_cents": exit_reduce_depth_diag_summary.get("loss_control_cost_cents"),
                "post_birth_settled": exit_reduce_depth_post_summary.get("settled"),
                "post_birth_delta_vs_current_cents": exit_reduce_depth_post_summary.get("delta_vs_current_cents"),
                "post_birth_blockers": exit_reduce_depth_post_best.get("blockers"),
            },
            "forward-only entry-depth gate watch exists for reduce-exit suppression",
            EXIT_REDUCE_DEPTH_GATE_JSON,
            "Freezes the retrospective entry-depth separator from its own timestamp; post-birth rows are required before promotion evidence exists.",
        ),
        check(
            "exit_reduce_depth_gate_runway_started",
            bool(exit_reduce_depth_runway_post),
            {
                "post_birth_candidate": exit_reduce_depth_runway_post.get("candidate"),
                "post_birth_settled": exit_reduce_depth_runway_post.get("settled"),
                "post_birth_suppressed_exits": exit_reduce_depth_runway_post.get("suppressed_exits"),
                "future_settled_rows_needed": exit_reduce_depth_runway_post.get("future_settled_rows_needed"),
                "future_suppressed_exits_needed": exit_reduce_depth_runway_post.get("future_suppressed_exits_needed"),
                "net_cents_needed_for_cushion3": exit_reduce_depth_runway_post.get("net_cents_needed_for_cushion3"),
                "ready_for_consideration": exit_reduce_depth_runway_post.get("ready_for_consideration"),
            },
            "post-birth exit-depth gate runway is tracked",
            EXIT_REDUCE_DEPTH_GATE_RUNWAY_JSON,
            "Quantifies sample, suppressed-exit, and full-loss-cushion distance for the frozen exit repair.",
        ),
        check(
            "exit_reduce_depth_gate_opportunity_started",
            bool(exit_reduce_depth_opportunity_best),
            {
                "post_birth_rows": exit_reduce_depth_gate_opportunity.get("post_birth_rows"),
                "first_rule": exit_reduce_depth_opportunity_best.get("candidate"),
                "probability_reduce_rows": exit_reduce_depth_opportunity_best.get("probability_reduce_rows"),
                "p_hold_candidate_rows": exit_reduce_depth_opportunity_best.get("p_hold_candidate_rows"),
                "entry_depth_candidate_rows": exit_reduce_depth_opportunity_best.get("entry_depth_candidate_rows"),
                "would_suppress_rows": exit_reduce_depth_opportunity_best.get("would_suppress_rows"),
                "fail_reason_counts": exit_reduce_depth_opportunity_best.get("fail_reason_counts"),
            },
            "post-birth exit-depth gate opportunity denominator is tracked",
            EXIT_REDUCE_DEPTH_GATE_OPPORTUNITY_JSON,
            "Distinguishes no suppressible exits from p-hold/depth/data failures while the frozen exit repair matures.",
        ),
        check(
            "exit_reduce_observable_loss_control_started",
            bool(exit_reduce_observable_post_best or exit_reduce_observable_diag_best),
            {
                "freeze_ts": (exit_reduce_observable_loss_control.get("state") or {}).get("freeze_ts_utc"),
                "diagnostic_best": exit_reduce_observable_diag_best.get("candidate"),
                "diagnostic_settled": exit_reduce_observable_diag_summary.get("settled"),
                "diagnostic_delta_vs_current_cents": exit_reduce_observable_diag_summary.get("delta_vs_current_cents"),
                "diagnostic_suppressed_wl": f"{exit_reduce_observable_diag_summary.get('suppressed_winners')}/{exit_reduce_observable_diag_summary.get('suppressed_losers')}",
                "diagnostic_loss_cost_cents": exit_reduce_observable_diag_summary.get("loss_control_cost_cents"),
                "post_birth_settled": exit_reduce_observable_post_summary.get("settled"),
                "post_birth_delta_vs_current_cents": exit_reduce_observable_post_summary.get("delta_vs_current_cents"),
                "post_birth_blockers": exit_reduce_observable_post_best.get("blockers"),
            },
            "forward-only observable reduce-exit loss-control watch exists",
            EXIT_REDUCE_OBSERVABLE_LOSS_CONTROL_JSON,
            "Freezes the observable time/depth/volatility reduce-loss-control separators from their own timestamp; diagnostic rows are mechanism evidence only.",
        ),
        check(
            "exit_reduce_observable_loss_control_opportunity_started",
            bool(exit_reduce_observable_opportunity_best),
            {
                "post_birth_rows": exit_reduce_observable_loss_control_opportunity.get("post_birth_rows"),
                "first_rule": exit_reduce_observable_opportunity_best.get("candidate"),
                "probability_reduce_rows": exit_reduce_observable_opportunity_best.get("probability_reduce_rows"),
                "p_hold_candidate_rows": exit_reduce_observable_opportunity_best.get("p_hold_candidate_rows"),
                "would_suppress_rows": exit_reduce_observable_opportunity_best.get("would_suppress_rows"),
                "would_suppress_delta_cents": exit_reduce_observable_opportunity_best.get("would_suppress_delta_cents"),
                "fail_reason_counts": exit_reduce_observable_opportunity_best.get("fail_reason_counts"),
            },
            "post-birth observable reduce-loss-control opportunity denominator is tracked",
            EXIT_REDUCE_OBSERVABLE_LOSS_CONTROL_OPPORTUNITY_JSON,
            "Distinguishes zero post-birth opportunity from no reduce exits, p-hold misses, or observable feature gate failures.",
        ),
        check(
            "exit_policy_loss_churn_effect_tracked",
            bool(exit_policy_loss_churn_best),
            {
                "top_lane": exit_policy_loss_churn_best.get("label"),
                "top_candidate": exit_policy_loss_churn_best.get("candidate"),
                "rows": exit_policy_loss_churn_best.get("rows"),
                "current_wl": f"{exit_policy_loss_churn_best.get('current_wins')}/{exit_policy_loss_churn_best.get('current_losses')}",
                "candidate_wl": f"{exit_policy_loss_churn_best.get('candidate_wins')}/{exit_policy_loss_churn_best.get('candidate_losses')}",
                "loss_count_reduction": exit_policy_loss_churn_best.get("loss_count_reduction"),
                "delta_cents": exit_policy_loss_churn_best.get("delta_cents"),
                "blockers": exit_policy_loss_churn_best.get("blockers"),
            },
            "exit candidates are scored by loss-count reduction as well as PnL",
            EXIT_POLICY_LOSS_CHURN_JSON,
            "The active live-readiness blocker is loss-count churn, so exit candidates must prove they reduce losing-row count without creating new loss-control failures.",
        ),
        check(
            "live_loss_escape_analysis_tracked",
            bool(live_loss_escape_analysis),
            {
                "loss_rows": live_loss_escape_analysis.get("loss_rows"),
                "escape_class_counts": live_loss_escape_counts,
                "best_repair_policy_counts": live_loss_escape_analysis.get("best_repair_policy_counts"),
                "largest_escaped_loss": (live_loss_escape_analysis.get("largest_escaped_losses") or [{}])[0],
            },
            "control/live losing rows are mapped to frozen exit-repair row effects",
            LIVE_LOSS_ESCAPE_JSON,
            "Separates losses that exit-reduce can flip from losses that escape current soft-exit repairs or lack tracked exit observations.",
        ),
        check(
            "collapse_suppression_forward_shadow_tracked",
            bool(collapse_suppress_summary),
            {
                "registered": collapse_suppress_summary.get("registered"),
                "resolved": collapse_suppress_summary.get("resolved"),
                "actual_exit_pnl_dollars": collapse_suppress_summary.get("actual_exit_pnl_dollars"),
                "hold_to_settlement_pnl_dollars": collapse_suppress_summary.get("hold_to_settlement_pnl_dollars"),
                "suppress_exit_delta_dollars": collapse_suppress_summary.get("suppress_exit_delta_dollars"),
                "help_hurt": [
                    collapse_suppress_summary.get("suppression_would_help"),
                    collapse_suppress_summary.get("suppression_would_hurt"),
                ],
            },
            "collapse-exit suppression is tracked with forward registered rows",
            COLLAPSE_SUPPRESS_SHADOW_JSON,
            "Recent forward evidence says broad collapse suppression would hurt; collapse losses require entry/FV/state filtering, not naive hold-through.",
        ),
        check(
            "collapse_reentry_registry_tracked",
            bool(collapse_reentry_summary),
            {
                "future_rows": collapse_reentry_summary.get("future_rows"),
                "future_closed_rows": collapse_reentry_summary.get("future_closed_rows"),
                "future_gross_cents": collapse_reentry_summary.get("future_gross_cents"),
                "future_skip_delta_cents": collapse_reentry_summary.get("future_skip_delta_cents"),
                "future_tag_rollups": collapse_reentry_registry.get("future_tag_rollups"),
            },
            "collapse-reentry state/FV confidence registry is tracked",
            COLLAPSE_REENTRY_JSON,
            "Separates same-side thin-edge reentry churn from opposite-side/high-confidence recovery after collapse.",
        ),
        check(
            "exit_policy_strict_failure_drilldown_tracked",
            bool(exit_strict_failure_common),
            {
                "strict_harmful_suppressions": exit_strict_failure_drilldown.get("strict_harmful_suppressions"),
                "strict_net_harm_cents": exit_strict_failure_drilldown.get("strict_net_harm_cents"),
                "common_windows": [
                    {
                        "window": row.get("window"),
                        "rows": row.get("rows"),
                        "harmful_suppressions": row.get("harmful_suppressions"),
                        "net_harm_cents": row.get("net_harm_cents"),
                        "avoided_by_v1": row.get("avoided_by_v1"),
                        "avoided_by_v2": row.get("avoided_by_v2"),
                        "tag_counts": row.get("tag_counts"),
                    }
                    for row in exit_strict_failure_common
                ],
            },
            "strict common-clock harmful suppressions are classified by physical mechanism",
            EXIT_STRICT_FAILURE_DRILLDOWN_JSON,
            "The top exit candidates must avoid rich-exit/negative-book-gap holds before any sidecar live test.",
        ),
        check(
            "exit_book_gap_loss_guard_opportunity_started",
            bool(exit_book_gap_loss_guard_opportunity),
            {
                "post_freeze_rows": book_gap_loss_guard_opportunity_rows,
                "soft_exit_rows": book_gap_loss_guard_opportunity_soft,
                "would_suppress_rows": book_gap_loss_guard_opportunity_suppress,
                "value_over_hold_rows": exit_book_gap_loss_guard_opportunity.get("value_over_hold_rows"),
                "probability_reduce_rows": exit_book_gap_loss_guard_opportunity.get("probability_reduce_rows"),
                "fail_reason_counts": exit_book_gap_loss_guard_opportunity.get("fail_reason_counts"),
            },
            "post-freeze book-gap loss-guard opportunity denominator is tracked",
            EXIT_BOOK_GAP_LOSS_GUARD_OPPORTUNITY_JSON,
            "Distinguishes no post-freeze exit rows from rule-specific book-gap or p-hold failures.",
        ),
        check(
            "exit_book_gap_value_only_opportunity_started",
            bool(exit_book_gap_value_only_opportunity),
            {
                "post_freeze_rows": book_gap_value_only_opportunity_rows,
                "value_over_hold_rows": book_gap_value_only_opportunity_value,
                "would_suppress_rows": book_gap_value_only_opportunity_suppress,
                "probability_reduce_rows": exit_book_gap_value_only_opportunity.get("probability_reduce_rows"),
                "would_suppress_delta_cents": exit_book_gap_value_only_opportunity.get("would_suppress_delta_cents"),
                "fail_reason_counts": exit_book_gap_value_only_opportunity.get("fail_reason_counts"),
            },
            "post-freeze value-only book-gap opportunity denominator is tracked",
            EXIT_BOOK_GAP_VALUE_ONLY_OPPORTUNITY_JSON,
            "Distinguishes no post-freeze value-over-hold exits from value-only p-hold/book-gap rule failures.",
        ),
        check(
            "exit_loss_guard_v1_v2_v3_runway_started",
            bool(exit_loss_guard_v1_v2_runway),
            {
                "v1_freeze_ts_utc": exit_loss_guard_v1_v2_runway.get("v1_freeze_ts_utc"),
                "v2_freeze_ts_utc": exit_loss_guard_v1_v2_runway.get("v2_freeze_ts_utc"),
                "v3_freeze_ts_utc": exit_loss_guard_v1_v2_runway.get("v3_freeze_ts_utc"),
                "v2_strict_settled": exit_loss_guard_v2_runway.get("settled"),
                "v2_suppressed_decisions": exit_loss_guard_v2_runway.get("v2_suppressed_decisions"),
                "v2_delta_cents": exit_loss_guard_v2_runway.get("v2_delta_cents"),
                "v2_rows_needed": exit_loss_guard_v2_runway.get("rows_needed"),
                "v2_suppressed_needed": exit_loss_guard_v2_runway.get("v2_suppressed_needed"),
                "v2_cushion_cents_needed": exit_loss_guard_v2_runway.get("net_cents_needed_for_cushion3"),
                "v2_v1_only_opportunity_cost_cents": exit_loss_guard_v2_runway.get("v1_only_opportunity_cost_cents"),
                "v1_strict_v1_only_opportunity_cost_cents": exit_loss_guard_v1_runway.get("v1_only_opportunity_cost_cents"),
                "v3_strict_settled": exit_loss_guard_v3_runway.get("settled"),
                "v3_suppressed_decisions": exit_loss_guard_v3_runway.get("suppressed_decisions"),
                "v3_delta_cents": exit_loss_guard_v3_runway.get("delta_cents"),
                "v3_rows_needed": exit_loss_guard_v3_runway.get("rows_needed"),
                "v3_suppressed_needed": exit_loss_guard_v3_runway.get("suppressed_needed"),
                "v3_cushion_cents_needed": exit_loss_guard_v3_runway.get("net_cents_needed_for_cushion3"),
                "v3_blockers": exit_loss_guard_v3_runway.get("blockers"),
                "strict_variant_runways": exit_loss_guard_variant_runways,
                "v2_opportunity": exit_loss_guard_v2_opportunity,
                "v2_blockers": exit_loss_guard_v2_runway.get("blockers"),
            },
            "strict v1/v2/v3 loss-guard runway is tracked",
            EXIT_LOSS_GUARD_V1_V2_RUNWAY_JSON,
            "Quantifies whether v1/v2/v3 loss guards have enough sample, suppressions, and full-loss cushion after their own freezes.",
        ),
        check(
            "exit_loss_guard_v1_v2_v3_contrast_started",
            bool(exit_loss_guard_v1_v2_v3_contrast),
            {
                "v3_freeze_ts_utc": exit_loss_guard_v1_v2_v3_contrast.get("v3_freeze_ts_utc"),
                "diagnostic_rows": exit_loss_guard_v1_v2_v3_diag.get("rows"),
                "diagnostic_buckets": exit_loss_guard_v1_v2_v3_diag.get("buckets"),
                "v3_strict_rows": exit_loss_guard_v1_v2_v3_v3_strict.get("rows"),
                "v3_strict_buckets": exit_loss_guard_v1_v2_v3_v3_strict.get("buckets"),
            },
            "v1/v2/v3 loss-guard contrast is tracked on identical rows",
            EXIT_LOSS_GUARD_V1_V2_V3_CONTRAST_JSON,
            "Shows whether V3 recovers v1-only extreme-p winners while rejecting the lower-confidence rich-exit risk bucket.",
        ),
        check(
            "exit_book_gap_loss_guard_v3_extreme_p_started",
            bool(frozen_exit_book_gap_loss_guard_v3),
            {
                "freeze_ts": (frozen_exit_book_gap_loss_guard_v3.get("freeze") or {}).get("freeze_ts_utc"),
                "candidate": (frozen_exit_book_gap_loss_guard_v3.get("freeze") or {}).get("candidate"),
                "strict_settled": exit_book_gap_loss_guard_v3_summary.get("settled"),
                "strict_delta_cents": exit_book_gap_loss_guard_v3_summary.get("delta_vs_current_cents"),
                "strict_suppressed": exit_book_gap_loss_guard_v3_summary.get("suppressed_exits"),
                "diagnostic_settled": exit_book_gap_loss_guard_v3_discovery.get("settled"),
                "diagnostic_delta_cents": exit_book_gap_loss_guard_v3_discovery.get("delta_vs_current_cents"),
                "diagnostic_suppressed_wl": f"{exit_book_gap_loss_guard_v3_discovery.get('suppressed_winners')}/{exit_book_gap_loss_guard_v3_discovery.get('suppressed_losers')}",
                "opportunity_rows": exit_book_gap_loss_guard_v3_opportunity.get("total_rows"),
                "v3_only_would_suppress_rows": exit_book_gap_loss_guard_v3_opportunity.get("v3_only_would_suppress_rows"),
                "v3_only_delta_cents": exit_book_gap_loss_guard_v3_opportunity.get("v3_only_delta_cents"),
                "blockers": frozen_exit_book_gap_loss_guard_v3.get("blockers"),
            },
            "v3 extreme-p loss guard is frozen from its own timestamp",
            FROZEN_EXIT_BOOK_GAP_LOSS_GUARD_V3_JSON,
            "Tests whether p_hold>=0.95 can recover v1-only winner clips without reopening lower-confidence rich-exit failures.",
        ),
        check(
            "exit_book_gap_loss_guard_v3_opportunity_started",
            bool(exit_book_gap_loss_guard_v3_opportunity),
            {
                "post_freeze_rows": exit_book_gap_loss_guard_v3_opportunity.get("total_rows"),
                "soft_exit_rows": exit_book_gap_loss_guard_v3_opportunity.get("soft_exit_rows"),
                "value_over_hold_rows": exit_book_gap_loss_guard_v3_opportunity.get("value_over_hold_rows"),
                "probability_reduce_rows": exit_book_gap_loss_guard_v3_opportunity.get("probability_reduce_rows"),
                "v2_would_suppress_rows": exit_book_gap_loss_guard_v3_opportunity.get("v2_would_suppress_rows"),
                "v3_would_suppress_rows": exit_book_gap_loss_guard_v3_opportunity.get("would_suppress_rows"),
                "v3_only_would_suppress_rows": exit_book_gap_loss_guard_v3_opportunity.get("v3_only_would_suppress_rows"),
                "v3_only_delta_cents": exit_book_gap_loss_guard_v3_opportunity.get("v3_only_delta_cents"),
                "fail_reason_counts": exit_book_gap_loss_guard_v3_opportunity.get("fail_reason_counts"),
            },
            "post-freeze V3 opportunity denominator is tracked",
            EXIT_BOOK_GAP_LOSS_GUARD_V3_OPPORTUNITY_JSON,
            "Separates no V3 rows from no soft exits, no extreme-p opportunities, and actual V3-only suppressions.",
        ),
        check(
            "exit_value_reduce_depth_composite_scored_forward_started",
            int(as_float(exit_value_reduce_depth_summary.get("settled")) or 0) > 0,
            {
                "freeze_ts_utc": (frozen_exit_value_reduce_depth_composite.get("freeze") or {}).get("freeze_ts_utc"),
                "primary_rule": (frozen_exit_value_reduce_depth_composite.get("freeze") or {}).get("candidate"),
                "diagnostic_rule": exit_value_reduce_depth_diag_best.get("rule"),
                "diagnostic_settled": exit_value_reduce_depth_diag_summary.get("settled"),
                "diagnostic_delta_vs_current_cents": exit_value_reduce_depth_diag_summary.get("delta_vs_current_cents"),
                "diagnostic_suppressed_winners": exit_value_reduce_depth_diag_summary.get("suppressed_winners"),
                "diagnostic_suppressed_losers": exit_value_reduce_depth_diag_summary.get("suppressed_losers"),
                "diagnostic_loss_control_cost_cents": exit_value_reduce_depth_diag_summary.get("loss_control_cost_cents"),
                "strict_settled": exit_value_reduce_depth_summary.get("settled"),
                "strict_delta_vs_current_cents": exit_value_reduce_depth_summary.get("delta_vs_current_cents"),
                "strict_suppressed": exit_value_reduce_depth_summary.get("suppressed_exits"),
                "strict_value_suppressed": exit_value_reduce_depth_summary.get("value_suppressed"),
                "strict_reduce_suppressed": exit_value_reduce_depth_summary.get("reduce_suppressed"),
                "strict_blockers": frozen_exit_value_reduce_depth_composite.get("blockers"),
            },
            ">0 post-freeze settled/scored rows for frozen value-exit plus reduce-depth composite",
            FROZEN_EXIT_VALUE_REDUCE_DEPTH_COMPOSITE_JSON,
            "This is the mixed top-candidate branch: keep value-exit and probability-reduce mechanisms separate, then require its own strict post-freeze suppressions before promotion.",
        ),
        check(
            "exit_value_reduce_depth_opportunity_started",
            bool(exit_value_reduce_depth_opportunity),
            {
                "freeze_ts_utc": exit_value_reduce_depth_opportunity.get("freeze_ts_utc"),
                "primary_rule": exit_value_reduce_depth_opportunity.get("primary_rule"),
                "post_freeze_rows": exit_value_reduce_depth_opportunity_primary.get("total_rows"),
                "value_over_hold_rows": exit_value_reduce_depth_opportunity_primary.get("value_over_hold_rows"),
                "probability_reduce_rows": exit_value_reduce_depth_opportunity_primary.get("probability_reduce_rows"),
                "would_suppress_rows": exit_value_reduce_depth_opportunity_primary.get("would_suppress_rows"),
                "would_suppress_value_rows": exit_value_reduce_depth_opportunity_primary.get("would_suppress_value_rows"),
                "would_suppress_reduce_rows": exit_value_reduce_depth_opportunity_primary.get("would_suppress_reduce_rows"),
                "would_suppress_delta_cents": exit_value_reduce_depth_opportunity_primary.get("would_suppress_delta_cents"),
                "rows_needed": exit_value_reduce_depth_opportunity_primary.get("rows_needed"),
                "suppressed_needed": exit_value_reduce_depth_opportunity_primary.get("suppressed_needed"),
                "cushion_cents_needed": exit_value_reduce_depth_opportunity_primary.get("net_cents_needed_for_cushion3"),
                "fail_reason_counts": exit_value_reduce_depth_opportunity_primary.get("fail_reason_counts"),
            },
            "post-freeze value/reduce-depth composite opportunity denominator is tracked",
            EXIT_VALUE_REDUCE_DEPTH_OPPORTUNITY_JSON,
            "Distinguishes no post-freeze exit rows from value-guard, reduce-depth, and p-hold rule failures.",
        ),
        check(
            "exit_reduce_geometry_suppression_scored_forward_started",
            int(as_float(frozen_exit_reduce_geometry_summary.get("settled")) or 0) > 0,
            {
                "diagnostic_best": exit_reduce_geometry_best.get("policy"),
                "diagnostic_delta_vs_current_cents": exit_reduce_geometry_best.get("delta_vs_current_cents"),
                "diagnostic_suppressed_winners": exit_reduce_geometry_best.get("suppressed_winners"),
                "diagnostic_suppressed_losers": exit_reduce_geometry_best.get("suppressed_losers"),
                "frozen_settled": frozen_exit_reduce_geometry_summary.get("settled"),
                "frozen_delta_vs_current_cents": frozen_exit_reduce_geometry_summary.get("delta_vs_current_cents"),
                "frozen_suppressed": frozen_exit_reduce_geometry_summary.get("suppressed"),
                "post_freeze_base_delta_cents": frozen_exit_reduce_geometry_base.get("delta_vs_current_cents"),
                "post_freeze_base_suppressed_winners": frozen_exit_reduce_geometry_base.get("suppressed_winners"),
                "post_freeze_base_suppressed_losers": frozen_exit_reduce_geometry_base.get("suppressed_losers"),
                "post_freeze_side_geometry_delta_cents": frozen_exit_reduce_geometry_side.get("delta_vs_current_cents"),
                "opportunity_probability_reduce_rows": exit_reduce_geometry_opportunity_summary.get("probability_reduce_rows"),
                "opportunity_base_candidates": exit_reduce_geometry_opportunity_summary.get("base_p_hold_candidates"),
                "opportunity_geometry_would_suppress_rows": exit_reduce_geometry_opportunity_summary.get("geometry_would_suppress_rows"),
                "opportunity_rejected_base_candidates": exit_reduce_geometry_opportunity_summary.get("geometry_rejected_base_candidates"),
                "opportunity_rejected_base_delta_cents": exit_reduce_geometry_opportunity_summary.get("geometry_rejected_base_delta_cents"),
                "opportunity_blockers": exit_reduce_geometry_opportunity_summary.get("blockers"),
            },
            ">0 post-freeze settled/scored rows for frozen side-geometry probability-reduce suppression",
            EXIT_REDUCE_GEOMETRY_OPPORTUNITY_JSON,
            "Side-geometry fixes the known loss-control failure diagnostically, but its own post-freeze opportunity audit must show actual suppressions and not reject positive base p-hold opportunities.",
        ),
        check(
            "exit_reduce_geometry_relaxed_watch_started",
            bool(frozen_exit_reduce_geometry_relaxed_watch.get("freeze")),
            {
                "freeze_ts": (frozen_exit_reduce_geometry_relaxed_watch.get("freeze") or {}).get("freeze_ts_utc"),
                "diagnostic_best": frozen_exit_reduce_geometry_relaxed_diag.get("policy"),
                "diagnostic_delta_vs_current_cents": frozen_exit_reduce_geometry_relaxed_diag.get("delta_vs_current_cents"),
                "diagnostic_suppressed_winners": frozen_exit_reduce_geometry_relaxed_diag.get("suppressed_winners"),
                "diagnostic_suppressed_losers": frozen_exit_reduce_geometry_relaxed_diag.get("suppressed_losers"),
                "strict_settled": frozen_exit_reduce_geometry_relaxed_summary.get("settled"),
                "strict_suppressed": frozen_exit_reduce_geometry_relaxed_summary.get("suppressed"),
                "strict_delta_vs_current_cents": frozen_exit_reduce_geometry_relaxed_summary.get("delta_vs_current_cents"),
                "strict_blockers": frozen_exit_reduce_geometry_relaxed_watch.get("blockers"),
            },
            "frozen child watch for relaxed side-geometry probability-reduce suppression exists",
            FROZEN_EXIT_REDUCE_GEOMETRY_RELAXED_WATCH_JSON,
            "Freezes the smallest observed relaxation of side-geometry from its own timestamp; diagnostic 13/0 suppressions are mechanism evidence only.",
        ),
        check(
            "fv_bridge_exit_geometry_stack_scored_forward_started",
            frozen_stack_rows > 0,
            {
                "settled": frozen_stack_rows,
                "coverage_pct": frozen_stack_coverage,
                "stack_net_cents": frozen_stack_net,
                "matched_rows": frozen_stack_matched,
                "suppressed_rows": frozen_stack_suppressed,
            },
            ">0 post-freeze settled approved-only rows for frozen FV bridge plus geometry-exit stack",
            FROZEN_FV_BRIDGE_EXIT_GEOMETRY_STACK_JSON,
            "The combined FV-entry plus exit-geometry stack is frozen separately; diagnostic gains are not promotion evidence.",
        ),
        check(
            "fv_bridge_exit_combo_stack_scored_forward_started",
            frozen_combo_rows > 0,
            {
                "settled": frozen_combo_rows,
                "coverage_pct": frozen_combo_coverage,
                "candidate_net_cents": frozen_combo_net,
                "matched_rows": frozen_combo_matched,
                "suppressed_rows": frozen_combo_suppressed,
            },
            ">0 post-freeze settled approved-only rows for frozen FV bridge plus reduce/collapse exit combo",
            FROZEN_FV_BRIDGE_EXIT_COMBO_STACK_JSON,
            "The reduce-geometry plus shallow-collapse combo is frozen separately; diagnostic gains are not promotion evidence.",
        ),
        check(
            "anti_overfit_freeze_clear",
            anti.get("all_clear") is True and int(anti.get("fail_count") or 0) == 0,
            {"all_clear": anti.get("all_clear"), "fail_count": anti.get("fail_count")},
            "anti-overfit all_clear true and fail_count 0",
            ANTI_OVERFIT_JSON,
            "Frozen artifacts exist and have no hard audit failures.",
        ),
        check(
            "live_readiness_gate",
            live_ready.get("any_live_ready") is True,
            live_ready.get("any_live_ready"),
            "any_live_ready true only after all blockers clear",
            LIVE_READY_JSON,
            "Must remain false until sample, calibration, coverage, and risk blockers clear.",
        ),
        check(
            "candidate_integrity_gate",
            integrity_pass_count > 0,
            {
                "candidate_count": integrity_candidate_count,
                "integrity_pass_count": integrity_pass_count,
                "top_gate": top_integrity.get("gate"),
                "top_policy": top_integrity.get("policy"),
                "top_blockers": top_integrity_blockers,
            },
            ">=1 positive target-coverage lane passing sample, source-quality, and full-loss-cushion gates",
            CANDIDATE_INTEGRITY_SCORECARD_JSON,
            "Prevents tiny or reconstructed positive PnL lanes from satisfying the objective.",
        ),
        check(
            "strict_forward_promotion_surface_present",
            bool(strict_forward_summary),
            {
                "strict_forward_rows": strict_forward_summary.get("strict_forward_rows"),
                "diagnostic_or_prefreeze_rows": strict_forward_summary.get("diagnostic_or_prefreeze_rows"),
                "strict_positive_rows": strict_forward_summary.get("strict_positive_rows"),
                "strict_target_positive_rows": strict_forward_summary.get("strict_target_positive_rows"),
                "strict_live_ready_rows": strict_forward_summary.get("strict_live_ready_rows"),
                "top_strict_forward": {
                    "gate": strict_forward_top.get("gate"),
                    "policy": strict_forward_top.get("policy"),
                    "settled": strict_forward_top.get("settled"),
                    "net_cents": strict_forward_top.get("net_cents"),
                    "missing_gates": strict_forward_top.get("missing_gates"),
                },
                "top_excluded_diagnostic": {
                    "gate": strict_forward_excluded_top.get("gate"),
                    "policy": strict_forward_excluded_top.get("policy"),
                    "settled": strict_forward_excluded_top.get("settled"),
                    "net_cents": strict_forward_excluded_top.get("net_cents"),
                    "missing_gates": strict_forward_excluded_top.get("missing_gates"),
                },
            },
            "strict-forward leaderboard separates promotion evidence from diagnostic/pre-freeze evidence",
            STRICT_FORWARD_LEADERBOARD_JSON,
            "Prevents high-PnL diagnostic rows from being treated as live-test/promotable candidates.",
        ),
        check(
            "active_candidate_registry_coverage",
            registry_complete,
            {
                "tracker_rows": registry_tracker_rows,
                "active_expected_rows": registry_expected_rows,
                "active_missing_rows": registry_missing_rows,
                "diagnostic_candidate_like_untracked": registry_diagnostic_untracked,
            },
            "all active frozen/special candidate lanes represented in consolidated table",
            CANDIDATE_REGISTRY_COVERAGE_JSON,
            "Prevents active candidates from disappearing from sorted PnL/readiness tables; diagnostic scans still require explicit registration.",
        ),
        check(
            "current_exit_edge_tracked",
            status.get("summary") is not None or bool(status),
            bool(status),
            "v28 control status artifact exists",
            STATUS_JSON,
            "Control v28/live-shadow evidence remains the baseline comparator.",
        ),
    ]
    missing = [row for row in checks if not row["passed"]]
    return {
        "objective": "Create a more accurate, physics-backed FV model that can be profitable while trading at least 75-80% of BTC 15m markets, without overfit, verified by live/forward data and sample size.",
        "achieved": not missing,
        "checks": checks,
        "missing": missing,
        "current_best_read": [
            f"Target-coverage p60 sharpening has {target_settled} settled rows, coverage {target_coverage}, net {target_net}c.",
            f"Latest target-overlay best is {current_overlay_best.get('overlay')} with {current_overlay_settled} settled rows, coverage {current_overlay_coverage}, net {current_overlay_net}c, Brier/logloss deltas {current_overlay_brier_delta}/{current_overlay_logloss_delta}.",
            f"Current Brier p95 is {brier_p95}; logloss p95 is {logloss_p95}.",
            f"Live-evidence quality has {approved_entry_rows} approved-entry rows and simulated/rejected share {simulated_share}.",
            f"Candidate integrity scorecard has {integrity_candidate_count} positive target-coverage lanes and {integrity_pass_count} integrity-pass lanes; top diagnostic lane is {top_integrity.get('gate')} / {top_integrity.get('policy')} at {top_integrity.get('net_cents')}c, coverage {top_integrity.get('coverage_pct')}, reconstructed share {top_integrity.get('reconstructed_share')}, with blockers {top_integrity_blockers}.",
            f"Strict-forward leaderboard has {strict_forward_summary.get('strict_forward_rows')} strict rows, {strict_forward_summary.get('strict_positive_rows')} strict positive rows, {strict_forward_summary.get('strict_target_positive_rows')} strict positive target-coverage rows, and {strict_forward_summary.get('strict_live_ready_rows')} strict live-ready rows; top strict row is {strict_forward_top.get('gate')} / {strict_forward_top.get('policy')} at {strict_forward_top.get('net_cents')}c with missing gates {strict_forward_top.get('missing_gates')}; top excluded diagnostic is {strict_forward_excluded_top.get('gate')} / {strict_forward_excluded_top.get('policy')} at {strict_forward_excluded_top.get('net_cents')}c.",
            f"Candidate registry coverage audit checked {registry_expected_rows} active rows against {registry_tracker_rows} tracker rows; missing active rows {registry_missing_rows}; diagnostic-like untracked rows {registry_diagnostic_untracked}.",
            f"False-conviction family scorecard has {false_family_pass_count} integrity-pass lanes; top lane is {false_family_top.get('name')} with settled {false_family_top.get('settled')}, coverage {false_family_top.get('coverage_pct')}, net {false_family_top.get('net_cents')}c.",
            f"Price-friction attribution has {price_rows} settled rows, net {price_net}c; worst repeated tag is {worst_price_tag.get('bucket')} with {worst_price_tag.get('settled')} settled rows and {worst_price_tag.get('net_cents')}c.",
            f"Target failure clusters assign {target_failure_clusters.get('total_direction_wrong_rows')} direction-wrong rows to mutually exclusive physical clusters; top cluster is {top_failure_cluster.get('cluster')} with {top_failure_cluster.get('rows')} rows and {top_failure_cluster.get('net_cents')}c.",
            f"Target cluster-penalty watch diagnostic best is {cluster_penalty_diag_best.get('candidate')} with {cluster_penalty_diag_summary.get('settled')} settled, coverage {cluster_penalty_diag_summary.get('coverage_pct')}%, net {cluster_penalty_diag_summary.get('net_cents')}c, delta {cluster_penalty_diag_best.get('delta_vs_target_cents')}c, reconstructed share {cluster_penalty_diag_best.get('reconstructed_share')}; post-birth has {cluster_penalty_post_summary.get('settled')} settled and blockers {cluster_penalty_post_best.get('blockers')}.",
            f"Target cluster-penalty runway says post-birth needs {cluster_penalty_post_runway.get('future_settled_rows_needed_for_sample')} settled rows, {cluster_penalty_post_source_runway.get('future_clean_approved_rows_needed_for_source_gate')} clean approved rows for source, and {cluster_penalty_post_runway.get('future_net_cents_needed_for_cushion3')}c cushion; diagnostic source still needs {cluster_penalty_diag_source_runway.get('future_clean_approved_rows_needed_for_source_gate')} clean rows.",
            f"Target cluster-penalty source feasibility says post-birth has {source_feasibility_post_best.get('approved_available_markets')} approved markets available for {source_feasibility_post_best.get('required_entries_for_75pct_coverage')} required entries, minimum reconstructed share {source_feasibility_post_best.get('minimum_reconstructed_share_for_75pct_coverage')}, source feasible {source_feasibility_post_best.get('source_gate_feasible_at_current_denominator')}; diagnostic feasibility is {source_feasibility_diag_best.get('source_gate_feasible_at_current_denominator')}.",
            f"Target cluster-penalty displacement says post-birth selected rejected rows net {displacement_post_rejected.get('net_cents')}c while omitted approved rows net {displacement_post_omitted.get('net_cents')}c; approved-preferred nondeployable oracle net {displacement_post_preferred.get('net_cents')}c.",
            f"Frozen approved-entry book FV has {approved_book_rows} settled/scored rows with Brier/logloss deltas {approved_book_brier_delta}/{approved_book_logloss_delta}.",
            f"Frozen approved-entry book/raw blend FV has {approved_book_raw_blend_future_rows} strict post-freeze settled rows; pre-freeze primary had {approved_book_raw_blend_prefreeze_primary.get('settled')} settled, Brier/logloss deltas {approved_book_raw_blend_prefreeze_primary.get('brier_delta_vs_raw')}/{approved_book_raw_blend_prefreeze_primary.get('logloss_delta_vs_raw')}, and blockers {frozen_approved_entry_book_raw_blend.get('blockers')}.",
            f"p70 candidate interval has {p70_settled} settled rows with Brier/logloss p95 {p70_brier_p95}/{p70_logloss_p95}.",
            f"Frozen conservative FV has {frozen_entries} post-freeze entries and {frozen_settled} settled/scored rows so far.",
            f"Frozen p70 FV has {frozen_p70_entries} post-freeze entries and {frozen_p70_settled} settled/scored rows so far.",
            f"Frozen p70 empirical-Bayes FV has {frozen_p70_eb_entries} post-freeze entries and {frozen_p70_eb_settled} settled/scored rows so far.",
            f"Frozen path-state p70 FV has {frozen_path_state_entries} post-freeze entries and {frozen_path_state_settled} settled/scored rows so far.",
            f"Frozen boundary-recross shrink FV has {frozen_boundary_recross_entries} post-freeze entries and {frozen_boundary_recross_settled} settled/scored rows so far.",
            f"Frozen boundary-temperature FV has denominator {frozen_boundary_temperature_denominator}, {frozen_boundary_temperature_rows} scored rows, adjusted {frozen_boundary_temperature_adjusted}, Brier/logloss deltas {frozen_boundary_temperature_brier}/{frozen_boundary_temperature_logloss}.",
            f"Frozen boundary-energy FV entry has {frozen_boundary_energy_entries} post-freeze entries and {frozen_boundary_energy_rows} settled/scored rows, coverage {frozen_boundary_energy_coverage}, net {frozen_boundary_energy_net}c, diagnostic delta {frozen_boundary_energy_diag_delta}c.",
            f"Frozen early-NO boundary FV entry has {frozen_early_no_boundary_entries} post-freeze entries and {frozen_early_no_boundary_rows} settled/scored rows, coverage {frozen_early_no_boundary_coverage}, net {frozen_early_no_boundary_net}c, diagnostic delta {frozen_early_no_boundary_diag_delta}c.",
            f"Frozen mid-edge false-conviction FV has {frozen_mid_edge_false_conviction_entries} post-freeze entries and {frozen_mid_edge_false_conviction_settled} settled/scored rows so far.",
            f"Frozen boundary-clock FV overlay has {frozen_boundary_clock_fv_entries} post-freeze entries and {frozen_boundary_clock_fv_rows} settled/scored rows so far, adjusted {frozen_boundary_clock_fv_adjusted}, Brier/logloss {frozen_boundary_clock_fv_brier}/{frozen_boundary_clock_fv_logloss}.",
            f"Frozen side-asymmetry FV overlay has {frozen_side_asymmetry_entries} post-freeze entries and {frozen_side_asymmetry_rows} settled/scored rows so far, adjusted {frozen_side_asymmetry_adjusted}, Brier/logloss {frozen_side_asymmetry_brier}/{frozen_side_asymmetry_logloss}.",
            f"Frozen edge-phase shrink FV has {frozen_edge_phase_entries} post-freeze entries and {frozen_edge_phase_settled} settled/scored rows so far.",
            f"Frozen edge-phase edge gate has {frozen_edge_phase_gate_entries} post-freeze entries and {frozen_edge_phase_gate_rows} settled/scored rows so far.",
            f"Frozen edge-gate opposite-side replacement has {frozen_edge_gate_opposite_entries} post-freeze entries and {frozen_edge_gate_opposite_rows} settled/scored rows so far.",
            f"Frozen early NO boundary-decay repair entry has {frozen_early_no_boundary_decay_entries} post-freeze entries and {frozen_early_no_boundary_decay_rows} settled/scored rows so far, coverage {frozen_early_no_boundary_decay_coverage}, net {frozen_early_no_boundary_decay_net}c.",
            f"Frozen approved-heavy false-conviction repair has {frozen_false_conviction_approved_entries} post-freeze entries and {frozen_false_conviction_approved_rows} settled/scored rows so far, coverage {frozen_false_conviction_approved_coverage}, net {frozen_false_conviction_approved_net}c, reconstructed share {frozen_false_conviction_approved_recon}.",
            f"Frozen mid-edge boundary-deception repair entry has {frozen_mid_edge_boundary_deception_entries} post-freeze entries and {frozen_mid_edge_boundary_deception_rows} settled/scored rows so far, coverage {frozen_mid_edge_boundary_deception_coverage}, net {frozen_mid_edge_boundary_deception_net}c.",
            f"Frozen low-recross repair entry has {frozen_low_recross_entries} post-freeze entries and {frozen_low_recross_rows} settled/scored rows so far, coverage {frozen_low_recross_coverage}, net {frozen_low_recross_net}c.",
            f"Frozen high-raw-p repair entry has {frozen_high_raw_p_entries} post-freeze entries and {frozen_high_raw_p_rows} settled/scored rows so far, coverage {frozen_high_raw_p_coverage}, net {frozen_high_raw_p_net}c.",
            f"Frozen p50 book-edge entry has {frozen_p50_book_edge_entries} post-freeze entries and {frozen_p50_book_edge_rows} settled/scored rows so far, coverage {frozen_p50_book_edge_coverage}, net {frozen_p50_book_edge_net}c.",
            f"Frozen book-plus-5pp entry has {frozen_book_plus05_entries} post-freeze entries and {frozen_book_plus05_rows} settled/scored rows so far, coverage {frozen_book_plus05_coverage}, net {frozen_book_plus05_net}c.",
            f"Frozen book-plus-5pp no-cheap-YES entry has {frozen_book_plus05_no_cheap_yes_entries} post-freeze entries and {frozen_book_plus05_no_cheap_yes_rows} settled/scored rows so far, coverage {frozen_book_plus05_no_cheap_yes_coverage}, net {frozen_book_plus05_no_cheap_yes_net}c.",
            f"Frozen boundary-clock repair entry has {frozen_boundary_clock_entries} post-freeze entries and {frozen_boundary_clock_rows} settled/scored rows so far, coverage {frozen_boundary_clock_coverage}, net {frozen_boundary_clock_net}c.",
            f"Frozen boundary-clock FV entry bridge has {frozen_boundary_clock_bridge_entries} post-freeze entries and {frozen_boundary_clock_bridge_rows} settled/scored rows so far, coverage {frozen_boundary_clock_bridge_coverage}, net {frozen_boundary_clock_bridge_net}c.",
            f"Boundary-clock source stress: entry reconstructed share {boundary_clock_entry_source_stress.get('reconstructed_share')}, clean rows needed {boundary_clock_entry_source_stress.get('future_clean_rows_for_sample_source_gate')}, full-loss cushion {boundary_clock_entry_source_stress.get('full_loss_cushion_estimate')}; FV bridge reconstructed share {boundary_clock_bridge_source_stress.get('reconstructed_share')}, clean rows needed {boundary_clock_bridge_source_stress.get('future_clean_rows_for_sample_source_gate')}, full-loss cushion {boundary_clock_bridge_source_stress.get('full_loss_cushion_estimate')}.",
            f"Boundary-clock approved-source frontier is a non-deployable feature target: entry best {boundary_clock_entry_frontier_best.get('candidate')} has {boundary_clock_entry_frontier_summary.get('settled')} settled, net {boundary_clock_entry_frontier_summary.get('net_cents')}c, blockers {boundary_clock_entry_frontier_best.get('blockers')}; FV bridge best {boundary_clock_bridge_frontier_best.get('candidate')} has {boundary_clock_bridge_frontier_summary.get('settled')} settled, net {boundary_clock_bridge_frontier_summary.get('net_cents')}c, blockers {boundary_clock_bridge_frontier_best.get('blockers')}.",
            f"Boundary-clock feature-gate candidate is frozen from {(boundary_clock_feature_gate.get('state') or {}).get('freeze_ts_utc')}: diagnostic entry best {boundary_clock_feature_diag_entry_best.get('candidate')} has {boundary_clock_feature_diag_entry_summary.get('settled')} settled, coverage {boundary_clock_feature_diag_entry_summary.get('coverage_pct')}, net {boundary_clock_feature_diag_entry_summary.get('net_cents')}c, reconstructed share {boundary_clock_feature_diag_entry_best.get('reconstructed_share')}, blockers {boundary_clock_feature_diag_entry_best.get('blockers')}; diagnostic bridge best {boundary_clock_feature_diag_bridge_best.get('candidate')} has {boundary_clock_feature_diag_bridge_summary.get('settled')} settled, coverage {boundary_clock_feature_diag_bridge_summary.get('coverage_pct')}, net {boundary_clock_feature_diag_bridge_summary.get('net_cents')}c, reconstructed share {boundary_clock_feature_diag_bridge_best.get('reconstructed_share')}, blockers {boundary_clock_feature_diag_bridge_best.get('blockers')}; post-freeze entry/bridge settled {boundary_clock_feature_post_entry_summary.get('settled')}/{boundary_clock_feature_post_bridge_summary.get('settled')}, best runway clean rows needed {boundary_clock_feature_runway_post.get('future_clean_selected_needed_for_all_gates')}, delta vs live {boundary_clock_feature_runway_post.get('delta_vs_live_cents')}c, post structural modes {boundary_clock_feature_failure_post.get('structural_failure_modes')}, post analog scores {boundary_clock_feature_loss_post.get('summary_scores')}, row-ledger omissions entry/bridge {boundary_clock_feature_row_entry_best.get('omission_reason_counts')}/{boundary_clock_feature_row_bridge_best.get('omission_reason_counts')}, ask-floor mechanism post/diagnostic deltas {boundary_clock_feature_ask_post_entry.get('delta_net_cents')}/{boundary_clock_feature_ask_diag_entry.get('delta_net_cents')}c with post switched tags {boundary_clock_feature_ask_post_entry.get('switched_failure_tag_counts')}; continuous-penalty watch is frozen from {(boundary_clock_feature_gate_continuous_penalty.get('state') or {}).get('freeze_ts_utc')} with diagnostic best {boundary_clock_feature_penalty_diag_entry_best.get('candidate')} at {boundary_clock_feature_penalty_diag_entry_summary.get('settled')} settled, coverage {boundary_clock_feature_penalty_diag_entry_summary.get('coverage_pct')}, net {boundary_clock_feature_penalty_diag_entry_summary.get('net_cents')}c, pre-birth best {boundary_clock_feature_penalty_pre_entry_best.get('candidate')} at coverage {boundary_clock_feature_penalty_pre_entry_summary.get('coverage_pct')}, net {boundary_clock_feature_penalty_pre_entry_summary.get('net_cents')}c, post-birth settled {boundary_clock_feature_penalty_post_entry_summary.get('settled')}, and stress needs {boundary_clock_feature_penalty_stress_post_entry.get('future_clean_selected_needed_for_all_count_gates')} clean rows plus {boundary_clock_feature_penalty_stress_post_entry.get('net_cents_needed_for_cushion3')}c cushion with blockers {boundary_clock_feature_penalty_stress_post_entry.get('stress_blockers')}; residual loss prototypes after cheap-side repair have tags {boundary_clock_feature_gate_residual_loss.get('prototype_tag_counts')} with diagnostic residual scores {boundary_clock_feature_residual_diag_entry.get('residual_summary')} and post-birth residual scores {boundary_clock_feature_residual_post_entry.get('residual_summary')}.",
            f"Boundary-clock feature-gate coverage recovery says strict {boundary_clock_feature_recovery_entry.get('strict_rule')} entry is clean but under-covered at {boundary_clock_feature_recovery_entry_strict.get('settled')} settled, coverage {boundary_clock_feature_recovery_entry_strict.get('coverage_pct')}%, net {boundary_clock_feature_recovery_entry_strict.get('net_cents')}c, reconstructed share {boundary_clock_feature_recovery_entry.get('strict_reconstructed_share')}; broader {boundary_clock_feature_recovery_entry_broad.get('rule')} reaches coverage {boundary_clock_feature_recovery_entry_broad_summary.get('coverage_pct')}%, net {boundary_clock_feature_recovery_entry_broad_summary.get('net_cents')}c, reconstructed share {boundary_clock_feature_recovery_entry_broad.get('reconstructed_share')}, adds {boundary_clock_feature_recovery_entry_broad_comparison.get('added_markets')} markets for {boundary_clock_feature_recovery_entry_broad_comparison.get('added_net_cents')}c, still needs {boundary_clock_feature_recovery_entry_broad_comparison.get('rows_needed_for_75pct_coverage')} rows for 75% coverage and {boundary_clock_feature_recovery_entry_broad_comparison.get('clean_rows_needed_for_source_gate')} clean rows for the source gate.",
            f"Boundary-clock feature-gate source-denominator audit says entry best {boundary_clock_feature_source_entry_best.get('rule')} has selected reconstructed share {boundary_clock_feature_source_entry_best.get('selected_reconstructed_share')}, approved-source market coverage {boundary_clock_feature_source_entry_best.get('approved_observed_coverage_pct')}%, reconstructed-source market coverage {boundary_clock_feature_source_entry_best.get('reconstructed_observed_coverage_pct')}%, and omitted net by source {boundary_clock_feature_source_entry_best.get('omitted_source_net_cents')}.",
            f"Boundary-clock feature-gate cheap-tail risk audit says broad entry has {(boundary_clock_feature_cheap_tail_entry.get('broad_summary') or {}).get('settled')} settled, coverage {(boundary_clock_feature_cheap_tail_entry.get('broad_summary') or {}).get('coverage_pct')}%, net {(boundary_clock_feature_cheap_tail_entry.get('broad_summary') or {}).get('net_cents')}c, reconstructed share {boundary_clock_feature_cheap_tail_entry.get('broad_reconstructed_share')}; cheap added rows versus the strict ask-floor are {boundary_clock_feature_cheap_tail_entry_added.get('rows')} rows for {boundary_clock_feature_cheap_tail_entry_added.get('net_cents')}c with W/L {boundary_clock_feature_cheap_tail_entry_added.get('wl')}, and the reconstructed slice is {boundary_clock_feature_cheap_tail_entry.get('reconstructed_net_without_top_win_cents')}c without its top reconstructed win. Cheap_lt10 half-size keeps weighted net {boundary_clock_feature_cheap_tail_entry_half.get('weighted_net_cents')}c but is mechanism evidence only.",
            f"Boundary-clock feature-gate coverage/source frontier audit says no row is promotable from the scan; entry Pareto best {boundary_clock_feature_frontier_entry_best.get('rule')} has {boundary_clock_feature_frontier_entry_summary.get('entries')}/{boundary_clock_feature_frontier_entry.get('future_denominator')} entries, coverage {boundary_clock_feature_frontier_entry_summary.get('coverage_pct')}%, net {boundary_clock_feature_frontier_entry_summary.get('net_cents')}c, reconstructed share {boundary_clock_feature_frontier_entry_best.get('reconstructed_share')}, and clean-broad-positive count {len(boundary_clock_feature_frontier_entry.get('clean_broad_positive') or [])}.",
            f"Boundary-clock feature-gate source-feasibility bound says entry denominator {feature_gate_feasibility_entry.get('future_denominator')} has {feature_gate_feasibility_entry.get('approved_markets_available')} approved markets available; 75% coverage with <=35% reconstructed share is feasible={feature_gate_feasibility_entry_75.get('source_gate_feasible')}, minimum reconstructed share needed is {feature_gate_feasibility_entry_75.get('min_reconstructed_share_needed')}, and max source-clean coverage is {feature_gate_feasibility_entry_75.get('max_source_clean_coverage_pct')}%.",
            f"Boundary-clock feature-gate frontier runway says entry Pareto best {boundary_clock_feature_frontier_runway_entry.get('rule')} needs {boundary_clock_feature_frontier_runway_entry_runway.get('clean_rows_needed_for_coverage_gate')} clean row for coverage, {boundary_clock_feature_frontier_runway_entry_runway.get('clean_rows_needed_for_source_gate')} for source, {boundary_clock_feature_frontier_runway_entry_runway.get('settled_rows_needed_for_sample_gate')} settled rows for sample, and {boundary_clock_feature_frontier_runway_entry_runway.get('net_cents_needed')}c for a three-full-loss cushion.",
            f"Boundary-clock feature-gate frontier mechanism drilldown says the soft frontier selected {boundary_clock_feature_frontier_mechanism_entry_summary.get('entries')}/{boundary_clock_feature_frontier_mechanism_entry.get('future_denominator')} rows for {boundary_clock_feature_frontier_mechanism_entry_summary.get('net_cents')}c; gained-row net {boundary_clock_feature_frontier_mechanism_gained.get('net_cents')}c with tags {boundary_clock_feature_frontier_mechanism_entry.get('gained_mechanism_tag_counts')}; omitted-row net {boundary_clock_feature_frontier_mechanism_omitted.get('net_cents')}c with fail reasons {boundary_clock_feature_frontier_mechanism_entry.get('omitted_fail_reason_counts')}.",
            f"Boundary-clock feature-gate outlier stress says the current frontier has approved-only net {boundary_clock_feature_outlier_entry.get('approved_only_net_cents')}c, reconstructed-only net {boundary_clock_feature_outlier_entry.get('reconstructed_only_net_cents')}c, top win {boundary_clock_feature_outlier_entry.get('top_win_net_cents')}c, net without top win {boundary_clock_feature_outlier_entry.get('net_without_top_win_cents')}c, and blockers {boundary_clock_feature_outlier_entry.get('stress_blockers')}.",
            f"Boundary-clock clean-broad frontier watch is frozen from {(boundary_clock_feature_gate_clean_broad_frontier.get('state') or {}).get('freeze_ts_utc')}: diagnostic parent entry {boundary_clock_feature_clean_broad_diag_entry.get('candidate')} has {boundary_clock_feature_clean_broad_diag_entry_summary.get('settled')} settled, coverage {boundary_clock_feature_clean_broad_diag_entry_summary.get('coverage_pct')}%, net {boundary_clock_feature_clean_broad_diag_entry_summary.get('net_cents')}c, reconstructed share {boundary_clock_feature_clean_broad_diag_entry.get('reconstructed_share')}; strict post-freeze entry has {boundary_clock_feature_clean_broad_post_entry_summary.get('settled')} settled, {boundary_clock_feature_clean_broad_post_entry.get('pending_unsettled_rows') or 0} pending unsettled, coverage {boundary_clock_feature_clean_broad_post_entry_summary.get('coverage_pct')}%, net {boundary_clock_feature_clean_broad_post_entry_summary.get('net_cents')}c, blockers {boundary_clock_feature_clean_broad_post_entry.get('blockers')}.",
            f"Boundary-clock clean-broad frontier drift audit says parent entry net {feature_gate_frontier_drift_entry_parent.get('net_cents')}c on {feature_gate_frontier_drift_entry_parent.get('settled')} settled with reconstructed share {feature_gate_frontier_drift_entry_parent.get('reconstructed_share')}, while strict watch is {feature_gate_frontier_drift_entry_strict.get('net_cents')}c on {feature_gate_frontier_drift_entry_strict.get('settled')} settled with reconstructed share {feature_gate_frontier_drift_entry_strict.get('reconstructed_share')}; delta {feature_gate_frontier_drift_entry_delta.get('net_delta_cents')}c and blockers {feature_gate_frontier_drift_entry_delta.get('blockers')}.",
            f"Boundary-clock soft-frontier watch is frozen from {(boundary_clock_feature_gate_soft_frontier.get('state') or {}).get('freeze_ts_utc')}: diagnostic best {boundary_clock_feature_soft_diag_entry_best.get('candidate')} has {boundary_clock_feature_soft_diag_entry_summary.get('settled')} settled, coverage {boundary_clock_feature_soft_diag_entry_summary.get('coverage_pct')}%, net {boundary_clock_feature_soft_diag_entry_summary.get('net_cents')}c, reconstructed share {boundary_clock_feature_soft_diag_entry_best.get('reconstructed_share')}, blockers {boundary_clock_feature_soft_diag_entry_best.get('blockers')}; post-birth settled {boundary_clock_feature_soft_post_entry_summary.get('settled')} with blockers {boundary_clock_feature_soft_post_entry_best.get('blockers')}.",
            f"Soft-frontier post-birth failure drilldown says strict entry {soft_frontier_failure_entry.get('rule')} has {soft_frontier_failure_entry_summary.get('settled')} settled, coverage {soft_frontier_failure_entry_summary.get('coverage_pct')}%, net {soft_frontier_failure_entry_summary.get('net_cents')}c, reconstructed share {soft_frontier_failure_entry.get('reconstructed_share')}, cushion {soft_frontier_failure_entry.get('full_loss_cushion')}, loss tags {soft_frontier_failure_entry.get('loss_tag_counts')}, and current exits changed loss rows by {soft_frontier_failure_entry.get('loss_exit_delta_vs_hold_cents')}c versus holding.",
            f"Boundary-clock soft-frontier exit stack is frozen from {(boundary_clock_feature_gate_soft_frontier_exit_stack.get('freeze') or {}).get('freeze_ts_utc')}: exit rows available {boundary_clock_feature_gate_soft_frontier_exit_stack.get('exit_rows_available')}, best candidate {boundary_clock_feature_soft_exit_stack_best.get('candidate')} has entry settled {boundary_clock_feature_soft_exit_stack_best_summary.get('settled')}, joined exits {boundary_clock_feature_soft_exit_stack_best.get('joined_exit_rows')}, joined net {boundary_clock_feature_soft_exit_stack_best.get('joined_exit_candidate_cents')}c, blockers {boundary_clock_feature_soft_exit_stack_best.get('blockers')}.",
            f"Feature-gate cheap-tail shrink watch is frozen from {(feature_gate_cheap_tail_shrink_watch.get('state') or {}).get('freeze_ts_utc')}: best strict policy {feature_gate_cheap_tail_shrink_best.get('policy')} has settled {feature_gate_cheap_tail_shrink_best.get('settled')}, coverage {feature_gate_cheap_tail_shrink_best.get('coverage_pct')}%, weighted net {feature_gate_cheap_tail_shrink_best.get('weighted_net_cents')}c, blockers {feature_gate_cheap_tail_shrink_best.get('blockers')}.",
            f"Soft-frontier size-shrink portfolio is frozen from {(soft_frontier_size_shrink.get('state') or {}).get('freeze_ts_utc')}: diagnostic best {soft_frontier_size_shrink_diag_best.get('candidate')} has settled {soft_frontier_size_shrink_diag_summary.get('settled')}, coverage {soft_frontier_size_shrink_diag_summary.get('coverage_pct')}%, net {soft_frontier_size_shrink_diag_summary.get('net_cents')}c; strict best {soft_frontier_size_shrink_strict_best.get('candidate')} has settled {soft_frontier_size_shrink_strict_summary.get('settled')}, net {soft_frontier_size_shrink_strict_summary.get('net_cents')}c, blockers {soft_frontier_size_shrink_strict_best.get('blockers')}.",
            f"Soft-frontier mid-price boundary shrink is frozen from {(soft_frontier_midprice_boundary_shrink.get('state') or {}).get('freeze_ts_utc')}: diagnostic best {soft_frontier_midprice_diag_best.get('candidate')} has settled {soft_frontier_midprice_diag_summary.get('settled')}, coverage {soft_frontier_midprice_diag_summary.get('coverage_pct')}%, net {soft_frontier_midprice_diag_summary.get('net_cents')}c, delta {soft_frontier_midprice_diag_summary.get('delta_vs_unweighted_cents')}c, band raw/weighted {soft_frontier_midprice_diag_summary.get('midprice_boundary_raw_net_cents')}/{soft_frontier_midprice_diag_summary.get('midprice_boundary_weighted_net_cents')}c; strict best {soft_frontier_midprice_strict_best.get('candidate')} has settled {soft_frontier_midprice_strict_summary.get('settled')}, net {soft_frontier_midprice_strict_summary.get('net_cents')}c, blockers {soft_frontier_midprice_strict_best.get('blockers')}.",
            f"Soft-frontier mid-price boundary entry+exit stack is frozen from {(soft_frontier_midprice_boundary_exit_stack.get('freeze') or {}).get('freeze_ts_utc')}: best diagnostic overlap {soft_frontier_midprice_exit_stack_best.get('candidate')} has entry settled {soft_frontier_midprice_exit_stack_entry_summary.get('settled')}, joined exits {soft_frontier_midprice_exit_stack_best.get('joined_exit_rows')}, post-stack joined exits {soft_frontier_midprice_exit_stack_best.get('post_stack_joined_exit_rows')}, weighted diagnostic net {soft_frontier_midprice_exit_stack_best.get('weighted_joined_exit_candidate_cents')}c; runway needs {soft_frontier_midprice_exit_stack_runway_best.get('post_stack_joined_rows_needed_for_sample_gate')} post-stack joined rows and {soft_frontier_midprice_exit_stack_runway_best.get('post_stack_weighted_cents_needed_for_cushion3')}c cushion.",
            f"Frozen weak-reversal residual repair has {frozen_weak_reversal_residual_repair_entries} post-freeze entries and {frozen_weak_reversal_residual_repair_rows} settled/scored rows so far, coverage {frozen_weak_reversal_residual_repair_coverage}, net {frozen_weak_reversal_residual_repair_net}c.",
            f"Frozen weak-reversal residual FV shrink has denominator {frozen_weak_reversal_residual_fv_denominator}, {frozen_weak_reversal_residual_fv_rows} scored rows, Brier/logloss deltas {frozen_weak_reversal_residual_fv_brier}/{frozen_weak_reversal_residual_fv_logloss}.",
            f"Frozen broader NO mid-edge FV shrink has denominator {frozen_no_mid_edge_fv_denominator}, {frozen_no_mid_edge_fv_rows} scored rows, Brier/logloss deltas {frozen_no_mid_edge_fv_brier}/{frozen_no_mid_edge_fv_logloss}.",
            f"Frozen early-boundary wait repair has {frozen_early_boundary_wait_entries} post-freeze entries and {frozen_early_boundary_wait_rows} settled/scored rows so far, coverage {frozen_early_boundary_wait_coverage}, net {frozen_early_boundary_wait_net}c.",
            f"Frozen early-boundary opposite wait repair has {frozen_early_boundary_opposite_wait_entries} post-freeze entries and {frozen_early_boundary_opposite_wait_rows} settled/scored rows so far, coverage {frozen_early_boundary_opposite_wait_coverage}, net {frozen_early_boundary_opposite_wait_net}c.",
            f"Frozen phi-forgetting FV best forward overlay is {phi_best_overlay} with {phi_rows} settled rows, coverage {phi_coverage}, Brier/logloss deltas {phi_brier_delta}/{phi_logloss_delta}.",
            f"Frozen confidence-shrink bakeoff diagnostic best is {shrink_diag_best.get('overlay')}; forward best is {shrink_best_overlay} with {shrink_rows} settled rows, coverage {shrink_coverage}, Brier/logloss deltas {shrink_brier_delta}/{shrink_logloss_delta}.",
            f"Frozen hybrid confidence-shrink FV diagnostic best is {hybrid_diag_best.get('overlay')}; forward best is {hybrid_best_overlay} with {hybrid_rows} settled rows, coverage {hybrid_coverage}, Brier/logloss deltas {hybrid_brier_delta}/{hybrid_logloss_delta}.",
            f"Target-surface hybrid FV has {target_hybrid_settled} settled rows, coverage {target_hybrid_coverage}, net {target_hybrid_net}c, Brier/logloss deltas {target_hybrid_brier_delta}/{target_hybrid_logloss_delta}.",
            f"Frozen target hybrid-veto repair has {target_hybrid_veto_post_entries} post-freeze entries and {target_hybrid_veto_post_rows} settled rows so far, coverage {target_hybrid_veto_post_coverage}, net {target_hybrid_veto_post_net}c; diagnostic best net {target_hybrid_veto_diag_net}c and delta {target_hybrid_veto_diag_delta}c.",
            f"Frozen hybrid/boundary entry stack has {hybrid_boundary_stack_post_entries} post-freeze entries and {hybrid_boundary_stack_post_rows} settled rows so far, coverage {hybrid_boundary_stack_post_coverage}, net {hybrid_boundary_stack_post_net}c; diagnostic best net {hybrid_boundary_stack_diag_net}c and delta {hybrid_boundary_stack_diag_delta}c.",
            f"Hybrid/boundary formal source-stress audit says diagnostic reconstructed share is {hybrid_boundary_source_stress_diag.get('reconstructed_share')} with {hybrid_boundary_source_stress_diag.get('clean_rows_needed_for_source_gate')} clean rows needed for source; post-freeze reconstructed share is {hybrid_boundary_source_stress_post.get('reconstructed_share')}, needs {hybrid_boundary_source_stress_post.get('clean_rows_needed_for_source_gate')} clean rows for source, {hybrid_boundary_source_stress_post.get('settled_rows_needed_for_sample_gate')} settled rows for sample, and {hybrid_boundary_source_stress_post.get('net_cents_needed_for_cushion3')}c for a three-full-loss cushion; blockers {hybrid_boundary_source_stress_post.get('stress_blockers')}.",
            f"Hybrid/boundary stack stress best diagnostic is {hybrid_boundary_stack_stress_best.get('candidate')} at net {hybrid_boundary_stack_stress_best.get('net_cents')}c with reconstructed share {hybrid_boundary_stack_stress_best.get('reconstructed_share')}; watch-source best is {hybrid_boundary_stack_stress_watch.get('candidate')} at net {hybrid_boundary_stack_stress_watch.get('net_cents')}c with reconstructed share {hybrid_boundary_stack_stress_watch.get('reconstructed_share')}; lowest-recon broad positive is {hybrid_boundary_stack_stress_lowest.get('candidate')} at net {hybrid_boundary_stack_stress_lowest.get('net_cents')}c with reconstructed share {hybrid_boundary_stack_stress_lowest.get('reconstructed_share')}.",
            f"Hybrid/boundary source frontier best diagnostic is {hybrid_boundary_frontier_diag_best.get('candidate')} at coverage {hybrid_boundary_frontier_diag_summary.get('coverage_pct')}, net {hybrid_boundary_frontier_diag_summary.get('net_cents')}c, reconstructed share {hybrid_boundary_frontier_diag_integrity.get('reconstructed_share')}, blockers {hybrid_boundary_frontier_diag_best.get('blockers')}; post-freeze frontier best is {hybrid_boundary_frontier_post_best.get('candidate')} with settled {hybrid_boundary_frontier_post_summary.get('settled')}, net {hybrid_boundary_frontier_post_summary.get('net_cents')}c, reconstructed share {hybrid_boundary_frontier_post_integrity.get('reconstructed_share')}.",
            f"Hybrid/boundary source dilution runway says diagnostic best needs {hybrid_boundary_dilution_diag.get('approved_needed_for_recon35')} additional clean approved selected rows to clear <=35% reconstructed share and can absorb {hybrid_boundary_dilution_diag.get('max_full_losses_while_positive')} full-loss rows before net turns non-positive; post-freeze best needs {hybrid_boundary_dilution_post.get('future_approved_selected_needed_for_gate')} future clean approved settled rows to satisfy sample/source gates together.",
            f"Frozen exit reduce-suppression has {frozen_exit_reduce_rows} settled rows and {frozen_exit_reduce_delta}c delta versus current exits so far.",
            f"Exit reduce-suppression risk ledger has {exit_reduce_risk_suppressed.get('rows')} suppressed exits: helpful recovery {exit_reduce_risk_helpful.get('rows')} rows / {exit_reduce_risk_helpful.get('net_delta_cents')}c, harmful loss-control cost {exit_reduce_risk_harmful.get('rows')} rows / {exit_reduce_risk_harmful.get('net_delta_cents')}c; p_hold>=0.79 group net {((exit_reduce_risk_groups.get('p_hold_ge_079') or {}).get('net_delta_cents'))}c and drawdown<=2.5 group net {((exit_reduce_risk_groups.get('drawdown_lte_2p5') or {}).get('net_delta_cents'))}c.",
            f"Exit reduce drift-guard watch is frozen from {(exit_reduce_drift_guard_watch.get('state') or {}).get('freeze_ts_utc')}: diagnostic best {exit_reduce_drift_guard_diag.get('policy')} has suppressed W/L {exit_reduce_drift_guard_diag.get('suppressed_helpful')}/{exit_reduce_drift_guard_diag.get('suppressed_harmful')} and delta {exit_reduce_drift_guard_diag.get('delta_vs_current_cents')}c; strict post-birth settled/suppressed/delta are {exit_reduce_drift_guard_post.get('settled')}/{exit_reduce_drift_guard_post.get('suppressed')}/{exit_reduce_drift_guard_post.get('delta_vs_current_cents')}c with blockers {exit_reduce_drift_guard_post.get('blockers')}.",
            f"Exit reduce loss-control signature says suppressed rows are {exit_reduce_signature_summary.get('helpful_rows')}/{exit_reduce_signature_summary.get('harmful_rows')} helpful/harmful with net {exit_reduce_signature_summary.get('total_delta_cents')}c; best retrospective separator is {exit_reduce_signature_best.get('feature')} {exit_reduce_signature_best.get('direction')} {exit_reduce_signature_best.get('threshold')} with selected W/L {exit_reduce_signature_best.get('selected_helpful')}/{exit_reduce_signature_best.get('selected_harmful')} and delta {exit_reduce_signature_best.get('selected_delta_cents')}c.",
            f"Exit reduce loss-control actionability says best separator overall is hindsight-only {exit_reduce_actionability_best_hindsight.get('feature')} {exit_reduce_actionability_best_hindsight.get('direction')} {exit_reduce_actionability_best_hindsight.get('threshold')}; best observable is {exit_reduce_actionability_best_observable.get('feature')} {exit_reduce_actionability_best_observable.get('direction')} {exit_reduce_actionability_best_observable.get('threshold')} with selected W/L {exit_reduce_actionability_best_observable.get('selected_helpful')}/{exit_reduce_actionability_best_observable.get('selected_harmful')}, delta {exit_reduce_actionability_best_observable.get('selected_delta_cents')}c, and frozen watch {exit_reduce_actionability_best_observable.get('frozen_watch')}.",
            f"Exit reduce loss-control refinement is frozen from {(exit_reduce_refinement.get('state') or {}).get('freeze_ts_utc')}: diagnostic best {exit_reduce_refinement_diag_best.get('candidate')} has delta {exit_reduce_refinement_diag_summary.get('delta_vs_current_cents')}c with suppressed W/L {exit_reduce_refinement_diag_summary.get('suppressed_winners')}/{exit_reduce_refinement_diag_summary.get('suppressed_losers')} and loss-control cost {exit_reduce_refinement_diag_summary.get('loss_control_cost_cents')}c; post-birth settled {exit_reduce_refinement_post_summary.get('settled')} with blockers {exit_reduce_refinement_post_best.get('blockers')}.",
            f"Exit reduce entry-depth gate is frozen from {(exit_reduce_depth_gate.get('state') or {}).get('freeze_ts_utc')}: diagnostic best {exit_reduce_depth_diag_best.get('candidate')} has delta {exit_reduce_depth_diag_summary.get('delta_vs_current_cents')}c with suppressed W/L {exit_reduce_depth_diag_summary.get('suppressed_winners')}/{exit_reduce_depth_diag_summary.get('suppressed_losers')} and loss-control cost {exit_reduce_depth_diag_summary.get('loss_control_cost_cents')}c; post-birth settled {exit_reduce_depth_post_summary.get('settled')} with blockers {exit_reduce_depth_post_best.get('blockers')}.",
            f"Exit reduce depth-gate runway says post-birth needs {exit_reduce_depth_runway_post.get('future_settled_rows_needed')} settled rows, {exit_reduce_depth_runway_post.get('future_suppressed_exits_needed')} suppressed exits, and {exit_reduce_depth_runway_post.get('net_cents_needed_for_cushion3')}c for a three-full-loss cushion before promotion review.",
            f"Exit reduce depth-gate opportunity denominator has {exit_reduce_depth_opportunity_best.get('probability_reduce_rows')} probability-reduce rows and {exit_reduce_depth_opportunity_best.get('would_suppress_rows')} would-suppress rows post-birth; fail reasons {exit_reduce_depth_opportunity_best.get('fail_reason_counts')}.",
            f"Exit reduce observable loss-control watch is frozen from {(exit_reduce_observable_loss_control.get('state') or {}).get('freeze_ts_utc')}: diagnostic best {exit_reduce_observable_diag_best.get('candidate')} has delta {exit_reduce_observable_diag_summary.get('delta_vs_current_cents')}c with suppressed W/L {exit_reduce_observable_diag_summary.get('suppressed_winners')}/{exit_reduce_observable_diag_summary.get('suppressed_losers')} and loss-control cost {exit_reduce_observable_diag_summary.get('loss_control_cost_cents')}c; post-birth settled {exit_reduce_observable_post_summary.get('settled')} with blockers {exit_reduce_observable_post_best.get('blockers')}.",
            f"Exit reduce observable loss-control opportunity denominator has {exit_reduce_observable_opportunity_best.get('probability_reduce_rows')} probability-reduce rows, {exit_reduce_observable_opportunity_best.get('p_hold_candidate_rows')} p-hold candidates, and {exit_reduce_observable_opportunity_best.get('would_suppress_rows')} would-suppress rows post-birth for {exit_reduce_observable_opportunity_best.get('would_suppress_delta_cents')}c; fail reasons {exit_reduce_observable_opportunity_best.get('fail_reason_counts')}.",
            f"Exit policy loss-count churn effect says best lane is {exit_policy_loss_churn_best.get('label')} with rows {exit_policy_loss_churn_best.get('rows')}, loss-count reduction {exit_policy_loss_churn_best.get('loss_count_reduction')}, current W/L {exit_policy_loss_churn_best.get('current_wins')}/{exit_policy_loss_churn_best.get('current_losses')}, candidate W/L {exit_policy_loss_churn_best.get('candidate_wins')}/{exit_policy_loss_churn_best.get('candidate_losses')}, delta {exit_policy_loss_churn_best.get('delta_cents')}c, and blockers {exit_policy_loss_churn_best.get('blockers')}.",
            f"Live loss escape analysis maps {live_loss_escape_analysis.get('loss_rows')} losing rows to frozen exit repairs: escape counts {live_loss_escape_counts}, best repair policy counts {live_loss_escape_analysis.get('best_repair_policy_counts')}, largest escaped loss {(live_loss_escape_analysis.get('largest_escaped_losses') or [{}])[0]}.",
            f"Collapse suppression forward shadow has {collapse_suppress_summary.get('registered')} registered rows, {collapse_suppress_summary.get('resolved')} resolved, actual exit PnL {collapse_suppress_summary.get('actual_exit_pnl_dollars')}$, hold PnL {collapse_suppress_summary.get('hold_to_settlement_pnl_dollars')}$, suppress delta {collapse_suppress_summary.get('suppress_exit_delta_dollars')}$, help/hurt {collapse_suppress_summary.get('suppression_would_help')}/{collapse_suppress_summary.get('suppression_would_hurt')}.",
            f"Collapse reentry registry has future rows/closed {collapse_reentry_summary.get('rows')}/{collapse_reentry_summary.get('closed')}, future gross {collapse_reentry_summary.get('gross_cents')}c, skip delta {collapse_reentry_summary.get('skip_delta_cents')}c, tag rollups {collapse_reentry_registry.get('future_tag_rollups')}.",
            f"Exit strict-failure drilldown says strict common-forward harmful suppressions are {exit_strict_failure_drilldown.get('strict_harmful_suppressions')} for {exit_strict_failure_drilldown.get('strict_net_harm_cents')}c; common-window tags are {[row.get('tag_counts') for row in exit_strict_failure_common]}.",
            f"Exit book-gap loss-guard opportunity denominator has {book_gap_loss_guard_opportunity_rows} post-freeze rows, {book_gap_loss_guard_opportunity_soft} soft exits, and {book_gap_loss_guard_opportunity_suppress} would-suppress rows; fail reasons {exit_book_gap_loss_guard_opportunity.get('fail_reason_counts')}.",
            f"Exit book-gap value-only opportunity denominator has {book_gap_value_only_opportunity_rows} post-freeze rows, {book_gap_value_only_opportunity_value} value-over-hold exits, and {book_gap_value_only_opportunity_suppress} would-suppress rows for {exit_book_gap_value_only_opportunity.get('would_suppress_delta_cents')}c; fail reasons {exit_book_gap_value_only_opportunity.get('fail_reason_counts')}.",
            f"Exit book-gap loss-guard v1/v2/v3 runway says v2 strict-forward has {exit_loss_guard_v2_runway.get('settled')} settled rows, {exit_loss_guard_v2_runway.get('v2_suppressed_decisions')} v2 suppressions, {exit_loss_guard_v2_runway.get('v2_delta_cents')}c v2 delta, {exit_loss_guard_v2_runway.get('v1_only_opportunity_cost_cents')}c v1-only opportunity cost, and still needs {exit_loss_guard_v2_runway.get('rows_needed')} rows, {exit_loss_guard_v2_runway.get('v2_suppressed_needed')} suppressions, and {exit_loss_guard_v2_runway.get('net_cents_needed_for_cushion3')}c cushion; v3 strict-forward has {exit_loss_guard_v3_runway.get('settled')} settled rows, {exit_loss_guard_v3_runway.get('suppressed_decisions')} suppressions, {exit_loss_guard_v3_runway.get('delta_cents')}c delta, and still needs {exit_loss_guard_v3_runway.get('rows_needed')} rows, {exit_loss_guard_v3_runway.get('suppressed_needed')} suppressions, and {exit_loss_guard_v3_runway.get('net_cents_needed_for_cushion3')}c cushion; variant runways {exit_loss_guard_variant_runways}.",
            f"Exit loss-guard v1/v2/v3 contrast diagnostic buckets are {exit_loss_guard_v1_v2_v3_diag.get('buckets')}; v3 strict rows {exit_loss_guard_v1_v2_v3_v3_strict.get('rows')} with buckets {exit_loss_guard_v1_v2_v3_v3_strict.get('buckets')}.",
            f"Frozen exit book-gap loss-guard v3 extreme-p branch is frozen from {(frozen_exit_book_gap_loss_guard_v3.get('freeze') or {}).get('freeze_ts_utc')}; strict settled {exit_book_gap_loss_guard_v3_summary.get('settled')}, delta {exit_book_gap_loss_guard_v3_summary.get('delta_vs_current_cents')}c, suppressed {exit_book_gap_loss_guard_v3_summary.get('suppressed_exits')}, blockers {frozen_exit_book_gap_loss_guard_v3.get('blockers')}; diagnostic delta {exit_book_gap_loss_guard_v3_discovery.get('delta_vs_current_cents')}c with suppressed W/L {exit_book_gap_loss_guard_v3_discovery.get('suppressed_winners')}/{exit_book_gap_loss_guard_v3_discovery.get('suppressed_losers')}; post-freeze opportunity rows {exit_book_gap_loss_guard_v3_opportunity.get('total_rows')}, v3-only would-suppress rows {exit_book_gap_loss_guard_v3_opportunity.get('v3_only_would_suppress_rows')} for {exit_book_gap_loss_guard_v3_opportunity.get('v3_only_delta_cents')}c.",
            f"Frozen exit value/reduce-depth composite primary {(frozen_exit_value_reduce_depth_composite.get('freeze') or {}).get('candidate')} has strict post-freeze settled {exit_value_reduce_depth_summary.get('settled')}, delta {exit_value_reduce_depth_summary.get('delta_vs_current_cents')}c, suppressed value/reduce {exit_value_reduce_depth_summary.get('value_suppressed')}/{exit_value_reduce_depth_summary.get('reduce_suppressed')}, and blockers {frozen_exit_value_reduce_depth_composite.get('blockers')}; diagnostic best {exit_value_reduce_depth_diag_best.get('rule')} had {exit_value_reduce_depth_diag_summary.get('settled')} rows, delta {exit_value_reduce_depth_diag_summary.get('delta_vs_current_cents')}c, suppressed W/L {exit_value_reduce_depth_diag_summary.get('suppressed_winners')}/{exit_value_reduce_depth_diag_summary.get('suppressed_losers')}, and loss-control cost {exit_value_reduce_depth_diag_summary.get('loss_control_cost_cents')}c.",
            f"Exit value/reduce-depth opportunity denominator says primary {exit_value_reduce_depth_opportunity.get('primary_rule')} has {exit_value_reduce_depth_opportunity_primary.get('total_rows')} post-freeze rows, value/reduce exits {exit_value_reduce_depth_opportunity_primary.get('value_over_hold_rows')}/{exit_value_reduce_depth_opportunity_primary.get('probability_reduce_rows')}, would-suppress value/reduce {exit_value_reduce_depth_opportunity_primary.get('would_suppress_value_rows')}/{exit_value_reduce_depth_opportunity_primary.get('would_suppress_reduce_rows')} for {exit_value_reduce_depth_opportunity_primary.get('would_suppress_delta_cents')}c, and runway needs {exit_value_reduce_depth_opportunity_primary.get('rows_needed')} rows, {exit_value_reduce_depth_opportunity_primary.get('suppressed_needed')} suppressions, {exit_value_reduce_depth_opportunity_primary.get('net_cents_needed_for_cushion3')}c cushion; fail reasons {exit_value_reduce_depth_opportunity_primary.get('fail_reason_counts')}.",
            f"Exit reduce side-geometry diagnostic best is {exit_reduce_geometry_best.get('policy')} with delta {exit_reduce_geometry_best.get('delta_vs_current_cents')}c and suppressed W/L {exit_reduce_geometry_best.get('suppressed_winners')}/{exit_reduce_geometry_best.get('suppressed_losers')}; post-geometry-freeze contrast is base delta {frozen_exit_reduce_geometry_base.get('delta_vs_current_cents')}c with suppressed W/L {frozen_exit_reduce_geometry_base.get('suppressed_winners')}/{frozen_exit_reduce_geometry_base.get('suppressed_losers')} versus side-geometry delta {frozen_exit_reduce_geometry_side.get('delta_vs_current_cents')}c with suppressed W/L {frozen_exit_reduce_geometry_side.get('suppressed_winners')}/{frozen_exit_reduce_geometry_side.get('suppressed_losers')}.",
            f"Exit reduce geometry opportunity audit says post-freeze rows {exit_reduce_geometry_opportunity_summary.get('post_freeze_rows')}, probability-reduce rows {exit_reduce_geometry_opportunity_summary.get('probability_reduce_rows')}, base candidates {exit_reduce_geometry_opportunity_summary.get('base_p_hold_candidates')}, geometry would-suppress rows {exit_reduce_geometry_opportunity_summary.get('geometry_would_suppress_rows')}, rejected base candidates {exit_reduce_geometry_opportunity_summary.get('geometry_rejected_base_candidates')} for {exit_reduce_geometry_opportunity_summary.get('geometry_rejected_base_delta_cents')}c; blockers {exit_reduce_geometry_opportunity_summary.get('blockers')}.",
            f"Frozen relaxed side-geometry exit watch is frozen from {(frozen_exit_reduce_geometry_relaxed_watch.get('freeze') or {}).get('freeze_ts_utc')}: diagnostic best {frozen_exit_reduce_geometry_relaxed_diag.get('policy')} has delta {frozen_exit_reduce_geometry_relaxed_diag.get('delta_vs_current_cents')}c with suppressed W/L {frozen_exit_reduce_geometry_relaxed_diag.get('suppressed_winners')}/{frozen_exit_reduce_geometry_relaxed_diag.get('suppressed_losers')}; strict post-freeze settled/suppressed/delta are {frozen_exit_reduce_geometry_relaxed_summary.get('settled')}/{frozen_exit_reduce_geometry_relaxed_summary.get('suppressed')}/{frozen_exit_reduce_geometry_relaxed_summary.get('delta_vs_current_cents')}c with blockers {frozen_exit_reduce_geometry_relaxed_watch.get('blockers')}.",
            f"Frozen FV bridge plus geometry-exit stack has {frozen_stack_rows} approved-only settled rows, coverage {frozen_stack_coverage}, stack net {frozen_stack_net}c, matched exits {frozen_stack_matched}, suppressed exits {frozen_stack_suppressed}.",
            f"Frozen FV bridge plus reduce/collapse exit combo has {frozen_combo_rows} approved-only settled rows, coverage {frozen_combo_coverage}, candidate net {frozen_combo_net}c, matched exits {frozen_combo_matched}, suppressed exits {frozen_combo_suppressed}.",
        ],
        "next_required_work": next_required_work(missing),
    }


def next_required_work(missing: list[dict[str, Any]]) -> list[str]:
    names = {row["name"] for row in missing}
    out: list[str] = []
    if (
        "conservative_candidate_scored_forward_started" in names
        or "p70_candidate_scored_forward_started" in names
        or "p70_empirical_bayes_candidate_scored_forward_started" in names
        or "path_state_p70_candidate_scored_forward_started" in names
        or "boundary_recross_shrink_candidate_scored_forward_started" in names
        or "boundary_temperature_fv_scored_forward_started" in names
        or "boundary_energy_fv_entry_scored_forward_started" in names
        or "early_no_boundary_fv_entry_scored_forward_started" in names
        or "mid_edge_false_conviction_fv_scored_forward_started" in names
        or "boundary_clock_fv_overlay_scored_forward_started" in names
        or "side_asymmetry_fv_overlay_scored_forward_started" in names
        or "edge_phase_shrink_candidate_scored_forward_started" in names
        or "edge_phase_edge_gate_scored_forward_started" in names
        or "edge_gate_opposite_side_scored_forward_started" in names
        or "early_no_boundary_decay_repair_entry_scored_forward_started" in names
        or "false_conviction_approved_repair_scored_forward_started" in names
        or "mid_edge_boundary_deception_repair_entry_scored_forward_started" in names
        or "low_recross_repair_entry_scored_forward_started" in names
        or "high_raw_p_repair_entry_scored_forward_started" in names
        or "p50_book_edge_entry_scored_forward_started" in names
        or "book_plus05_entry_scored_forward_started" in names
        or "book_plus05_no_cheap_yes_entry_scored_forward_started" in names
        or "boundary_clock_repair_entry_scored_forward_started" in names
        or "boundary_clock_fv_entry_bridge_scored_forward_started" in names
        or "weak_reversal_residual_repair_scored_forward_started" in names
        or "weak_reversal_residual_fv_shrink_scored_forward_started" in names
        or "no_mid_edge_fv_scored_forward_started" in names
        or "early_boundary_wait_repair_scored_forward_started" in names
        or "early_boundary_opposite_wait_repair_scored_forward_started" in names
        or "phi_forgetting_fv_scored_forward_started" in names
        or "confidence_shrink_bakeoff_scored_forward_started" in names
        or "hybrid_confidence_shrink_fv_scored_forward_started" in names
        or "target_hybrid_veto_repair_scored_forward_started" in names
        or "hybrid_boundary_entry_stack_scored_forward_started" in names
        or "fv_bridge_exit_combo_stack_scored_forward_started" in names
        or "approved_entry_book_fv_forward_started" in names
        or "forward_sample_size" in names
    ):
        out.append("Keep collecting post-freeze target-coverage rows until frozen FV challengers reach 30 settled rows.")
    if "brier_interval_better_than_raw" in names:
        out.append("Prefer conservative sharpening over broad p>=60 sharpening unless future Brier interval recovers.")
    if "p70_interval_better_than_raw" in names:
        out.append("Keep refreshing the p70 sequential-evidence artifact and reject p70 if its interval turns positive before frozen validation matures.")
    if "candidate_integrity_gate" in names:
        out.append("Keep validating positive broad-coverage lanes until at least one clears sample size, source-quality, and full-loss fragility gates.")
    if "live_readiness_gate" in names:
        out.append("Do not place live trades from candidates while live_readiness remains false.")
    return out or ["No missing work detected."]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Goal Completion Audit",
        "",
        f"- Achieved: `{report.get('achieved')}`",
        f"- Objective: {report.get('objective')}",
        "",
        "## Current Best Read",
        "",
    ]
    for note in report.get("current_best_read") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Checklist",
        "",
        "| requirement | pass | actual | required | evidence | note |",
        "|---|---:|---|---|---|---|",
    ])
    for row in report.get("checks") or []:
        lines.append(
            f"| `{row.get('name')}` | `{row.get('passed')}` | `{fmt(row.get('actual'))}` | "
            f"{row.get('required')} | `{row.get('evidence')}` | {row.get('note')} |"
        )
    lines.extend(["", "## Next Required Work", ""])
    for item in report.get("next_required_work") or []:
        lines.append(f"- {item}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
