"""Compact watchlist for the active v28 improvement goal.

This script does not optimize or promote rules. It consolidates forward-only
diagnostics into the few candidates that currently deserve continued shadowing.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SCORECARD_JSON = OUT_DIR / "v28_continuous_scorecard_latest.json"
EXIT_JSON = OUT_DIR / "v28_exit_policy_candidates_latest.json"
BRANCH_JSON = OUT_DIR / "v28_exit_branch_diagnostic_latest.json"
FROZEN_EXIT_REDUCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
FROZEN_EXIT_REDUCE_YES_JSON = OUT_DIR / "v28_frozen_exit_reduce_yes_suppression_latest.json"
EXIT_REDUCE_ROBUSTNESS_JSON = OUT_DIR / "v28_exit_reduce_suppression_robustness_latest.json"
EXIT_REDUCE_SIDE_SPLIT_JSON = OUT_DIR / "v28_exit_reduce_side_split_attribution_latest.json"
EXIT_REDUCE_RUNWAY_JSON = OUT_DIR / "v28_exit_reduce_promotion_runway_latest.json"
EXIT_BOOK_GAP_JSON = OUT_DIR / "v28_exit_book_gap_candidates_latest.json"
FROZEN_EXIT_BOOK_GAP_JSON = OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json"
ACTIVE_TRADE_SENSITIVITY_JSON = OUT_DIR / "v28_active_trade_sensitivity_latest.json"
BAKEOFF_JSON = OUT_DIR / "v28_shadow_entry_policy_bakeoff_latest.json"
DECAY_JSON = OUT_DIR / "v28_information_decay_diagnostic_latest.json"
FV_VARIANTS_JSON = OUT_DIR / "v28_shadow_fv_variants_latest.json"
REENTRY_JSON = OUT_DIR / "v28_reentry_throttle_candidates_latest.json"
RMT_JSON = OUT_DIR / "v28_rmt_regime_diagnostic_latest.json"
STATE_AWARE_FV_JSON = OUT_DIR / "v28_state_aware_fv_candidates_latest.json"
RMT_FORGETTING_ENTRY_JSON = OUT_DIR / "v28_rmt_forgetting_entry_bakeoff_latest.json"
BOOK_FAVORITE_EDGE_JSON = OUT_DIR / "v28_book_favorite_edge_diagnostic_latest.json"
FROZEN_FORWARD_JSON = OUT_DIR / "v28_frozen_forward_candidates_latest.json"
THRESHOLD_CHALLENGERS_JSON = OUT_DIR / "v28_frozen_threshold_challengers_latest.json"
FROZEN_TIMING_JSON = OUT_DIR / "v28_frozen_timing_diagnostic_latest.json"
SIDE_FLIP_JSON = OUT_DIR / "v28_side_flip_path_diagnostic_latest.json"
SIDE_AGREEMENT_META_JSON = OUT_DIR / "v28_side_agreement_meta_candidate_latest.json"
FROZEN_SIDE_AGREEMENT_JSON = OUT_DIR / "v28_frozen_side_agreement_challengers_latest.json"
CONVEX_ESCAPE_JSON = OUT_DIR / "v28_convex_raw_escape_candidate_latest.json"
FROZEN_CONVEX_ESCAPE_JSON = OUT_DIR / "v28_frozen_convex_escape_challengers_latest.json"
RAW_CONVICTION_JSON = OUT_DIR / "v28_raw_conviction_override_diagnostic_latest.json"
COVERAGE_PRESSURE_JSON = OUT_DIR / "v28_forward_coverage_pressure_audit_latest.json"
RAW_PHYSICS_JSON = OUT_DIR / "v28_raw_physics_penalty_candidates_latest.json"
RAW_P52_DELTA_JSON = OUT_DIR / "v28_raw_p52_delta_diagnostic_latest.json"
RAW_P52_CONFIRMATION_JSON = OUT_DIR / "v28_raw_p52_confirmation_path_latest.json"
FROZEN_RAW_PHYSICS_JSON = OUT_DIR / "v28_frozen_raw_physics_challengers_latest.json"
RAW_P52_SIDEFLIP_JSON = OUT_DIR / "v28_raw_p52_sideflip_candidate_latest.json"
FROZEN_RAW_P52_SIDEFLIP_JSON = OUT_DIR / "v28_frozen_raw_p52_sideflip_challenger_latest.json"
RAW_P52_RECROSS_ESCAPE_JSON = OUT_DIR / "v28_raw_p52_recross_escape_candidate_latest.json"
FROZEN_RAW_P52_RECROSS_ESCAPE_JSON = OUT_DIR / "v28_frozen_raw_p52_recross_escape_challenger_latest.json"
RECROSS_ESCAPE_PROBABILITY_JSON = OUT_DIR / "v28_recross_escape_probability_calibration_latest.json"
FROZEN_RECROSS_ESCAPE_ATTRIBUTION_JSON = OUT_DIR / "v28_frozen_recross_escape_attribution_latest.json"
RECROSS_ESCAPE_SAMPLE_PLAN_JSON = OUT_DIR / "v28_recross_escape_sample_plan_latest.json"
NOISE_SHRINKAGE_JSON = OUT_DIR / "v28_noise_floor_shrinkage_candidates_latest.json"
FROZEN_NOISE_SHRINKAGE_JSON = OUT_DIR / "v28_frozen_noise_floor_shrinkage_challengers_latest.json"
RAW_ENTRY_CALIBRATED_JSON = OUT_DIR / "v28_raw_entry_calibrated_probability_latest.json"
PROBABILITY_PROFIT_BRIDGE_JSON = OUT_DIR / "v28_probability_profit_bridge_latest.json"
APPROVED_ENTRY_FV_OVERLAY_JSON = OUT_DIR / "v28_approved_entry_fv_overlay_validator_latest.json"
APPROVED_ENTRY_BOOK_EDGE_ACTIONABILITY_JSON = OUT_DIR / "v28_approved_entry_book_edge_actionability_latest.json"
FROZEN_APPROVED_ENTRY_BOOK_EDGE_GATE_JSON = OUT_DIR / "v28_frozen_approved_entry_book_edge_gate_latest.json"
ENTRY_POSTERIOR_DIAGNOSTIC_JSON = OUT_DIR / "v28_entry_conditioned_posterior_diagnostic_latest.json"
SOURCE_AWARE_FV_OVERLAY_JSON = OUT_DIR / "v28_source_aware_fv_overlay_validator_latest.json"
SOURCE_AWARE_FV_ROBUSTNESS_AUDIT_JSON = OUT_DIR / "v28_source_aware_fv_robustness_audit_latest.json"
SOURCE_AWARE_FV_PROMOTION_AUDIT_JSON = OUT_DIR / "v28_source_aware_fv_promotion_audit_latest.json"
APPROVED_ENTRY_STATE_VALVES_JSON = OUT_DIR / "v28_approved_entry_state_valves_latest.json"
FROZEN_APPROVED_ENTRY_STATE_VALVE_JSON = OUT_DIR / "v28_frozen_approved_entry_state_valve_latest.json"
DANGER_ZONE_ENTRY_VALVE_JSON = OUT_DIR / "v28_danger_zone_entry_valve_latest.json"
FROZEN_DANGER_ZONE_ENTRY_VALVE_JSON = OUT_DIR / "v28_frozen_danger_zone_entry_valve_latest.json"
DANGER_ZONE_FV_CALIBRATION_JSON = OUT_DIR / "v28_danger_zone_fv_calibration_latest.json"
FROZEN_DANGER_ZONE_FV_CALIBRATION_JSON = OUT_DIR / "v28_frozen_danger_zone_fv_calibration_latest.json"
DANGER_ZONE_ROBUSTNESS_AUDIT_JSON = OUT_DIR / "v28_danger_zone_robustness_audit_latest.json"
BOOK_TRAJECTORY_FV_JSON = OUT_DIR / "v28_book_disagreement_trajectory_fv_latest.json"
FROZEN_BOOK_TRAJECTORY_FV_JSON = OUT_DIR / "v28_frozen_book_trajectory_fv_latest.json"
BOOK_TRAJECTORY_ENTRY_PROJECTION_JSON = OUT_DIR / "v28_book_trajectory_entry_projection_latest.json"
FROZEN_PENDING_MONITOR_JSON = OUT_DIR / "v28_frozen_pending_monitor_latest.json"
FROZEN_FORWARD_SCORECARD_JSON = OUT_DIR / "v28_frozen_forward_scorecard_latest.json"
ENTRY_LIFT_PLATEAU_JSON = OUT_DIR / "v28_entry_conditioned_lift_plateau_latest.json"
ENTRY_JACKKNIFE_JSON = OUT_DIR / "v28_entry_conditioned_jackknife_latest.json"
ENTRY_DATA_QUALITY_JSON = OUT_DIR / "v28_entry_conditioned_data_quality_latest.json"
FROZEN_RAW_ENTRY_CALIBRATED_JSON = OUT_DIR / "v28_frozen_raw_entry_calibrated_probability_latest.json"
CALIBRATED_FV_FORWARD_MONITOR_JSON = OUT_DIR / "v28_calibrated_fv_forward_monitor_latest.json"
CALIBRATED_FV_SEQUENTIAL_EVIDENCE_JSON = OUT_DIR / "v28_calibrated_fv_sequential_evidence_latest.json"
CALIBRATED_FV_PHYSICS_ATTRIBUTION_JSON = OUT_DIR / "v28_calibrated_fv_physics_attribution_latest.json"
CALIBRATED_FV_PATH_CONTRADICTION_JSON = OUT_DIR / "v28_calibrated_fv_path_contradiction_latest.json"
PATH_CONFIRMED_ENTRY_JSON = OUT_DIR / "v28_path_confirmed_entry_candidates_latest.json"
PATH_RMT_FORWARD_GATE_JSON = OUT_DIR / "v28_path_rmt_forward_gate_latest.json"
FV_MODEL_READINESS_JSON = OUT_DIR / "v28_fv_model_readiness_latest.json"
FV_OVERLAY_CHALLENGER_READINESS_JSON = OUT_DIR / "v28_fv_overlay_challenger_readiness_latest.json"
CALIBRATED_FV_SAMPLE_PLAN_JSON = OUT_DIR / "v28_calibrated_fv_sample_plan_latest.json"
RAW_ENTRY_COVERAGE_VALVE_JSON = OUT_DIR / "v28_raw_entry_coverage_valve_latest.json"
TARGET_COVERAGE_FV_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
TARGET_COVERAGE_FV_SEQ_JSON = OUT_DIR / "v28_target_coverage_fv_sequential_evidence_latest.json"
TARGET_COVERAGE_FV_ATTRIBUTION_JSON = OUT_DIR / "v28_target_coverage_fv_attribution_latest.json"
TARGET_COVERAGE_PROMOTION_AUDIT_JSON = OUT_DIR / "v28_target_coverage_promotion_audit_latest.json"
TARGET_COVERAGE_SAMPLE_RUNWAY_JSON = OUT_DIR / "v28_target_coverage_sample_runway_latest.json"
TARGET_COVERAGE_FV_FRAGILITY_AUDIT_JSON = OUT_DIR / "v28_target_coverage_fv_fragility_audit_latest.json"
TARGET_COVERAGE_FV_BUCKET_RELIABILITY_JSON = OUT_DIR / "v28_target_coverage_fv_bucket_reliability_latest.json"
TARGET_COVERAGE_FV_LIVE_EVIDENCE_AUDIT_JSON = OUT_DIR / "v28_target_coverage_fv_live_evidence_audit_latest.json"
TARGET_COVERAGE_DANGER_OVERLAP_JSON = OUT_DIR / "v28_target_coverage_danger_overlap_latest.json"
TARGET_COVERAGE_PRICE_FRICTION_JSON = OUT_DIR / "v28_target_coverage_price_friction_latest.json"
FALSE_CONVICTION_PHYSICS_JSON = OUT_DIR / "v28_false_conviction_physics_audit_latest.json"
FALSE_CONVICTION_FAMILY_SCORECARD_JSON = OUT_DIR / "v28_false_conviction_family_scorecard_latest.json"
FALSE_CONVICTION_SOURCE_QUALITY_REPAIR_JSON = OUT_DIR / "v28_false_conviction_source_quality_repair_latest.json"
COMPOSITE_FALSE_CONVICTION_REPAIR_ROBUSTNESS_JSON = OUT_DIR / "v28_composite_false_conviction_repair_robustness_latest.json"
COMPOSITE_FALSE_CONVICTION_REPAIR_STRESS_JSON = OUT_DIR / "v28_composite_false_conviction_repair_stress_latest.json"
WEAK_BOUNDARY_REVERSAL_STRATEGY_JSON = OUT_DIR / "v28_weak_boundary_reversal_strategy_latest.json"
WEAK_BOUNDARY_REVERSAL_BAKEOFF_JSON = OUT_DIR / "v28_weak_boundary_reversal_bakeoff_latest.json"
WEAK_REVERSAL_RESIDUAL_ATTRIBUTION_JSON = OUT_DIR / "v28_weak_reversal_residual_attribution_latest.json"
WEAK_REVERSAL_RESIDUAL_FV_SHRINK_JSON = OUT_DIR / "v28_weak_reversal_residual_fv_shrink_latest.json"
FROZEN_WEAK_REVERSAL_RESIDUAL_FV_SHRINK_JSON = OUT_DIR / "v28_frozen_weak_reversal_residual_fv_shrink_latest.json"
NO_MID_EDGE_FV_GENERALIZATION_JSON = OUT_DIR / "v28_no_mid_edge_fv_generalization_latest.json"
FROZEN_NO_MID_EDGE_FV_JSON = OUT_DIR / "v28_frozen_no_mid_edge_fv_latest.json"
NO_MID_EDGE_ENTRY_REPAIR_JSON = OUT_DIR / "v28_no_mid_edge_entry_repair_latest.json"
WEAK_REVERSAL_RESIDUAL_REPAIR_JSON = OUT_DIR / "v28_weak_reversal_residual_repair_latest.json"
FROZEN_WEAK_REVERSAL_RESIDUAL_REPAIR_JSON = OUT_DIR / "v28_frozen_weak_reversal_residual_repair_latest.json"
EARLY_CLOCK_WAIT_BAKEOFF_JSON = OUT_DIR / "v28_early_clock_wait_bakeoff_latest.json"
FROZEN_EARLY_BOUNDARY_WAIT_REPAIR_JSON = OUT_DIR / "v28_frozen_early_boundary_wait_repair_latest.json"
FROZEN_EARLY_BOUNDARY_OPPOSITE_WAIT_REPAIR_JSON = OUT_DIR / "v28_frozen_early_boundary_opposite_wait_repair_latest.json"
TARGET_COVERAGE_CONSERVATIVE_FV_JSON = OUT_DIR / "v28_target_coverage_conservative_fv_variants_latest.json"
TARGET_COVERAGE_SOURCE_SPLIT_FV_JSON = OUT_DIR / "v28_target_coverage_source_split_fv_latest.json"
TARGET_COVERAGE_P70_JACKKNIFE_JSON = OUT_DIR / "v28_target_coverage_p70_jackknife_latest.json"
FROZEN_TARGET_COVERAGE_CONSERVATIVE_FV_JSON = OUT_DIR / "v28_frozen_target_coverage_conservative_fv_latest.json"
FROZEN_TARGET_COVERAGE_CONSERVATIVE_PENDING_JSON = OUT_DIR / "v28_frozen_target_coverage_conservative_pending_latest.json"
FROZEN_TARGET_COVERAGE_P70_FV_JSON = OUT_DIR / "v28_frozen_target_coverage_p70_fv_latest.json"
FROZEN_TARGET_COVERAGE_P70_RUNWAY_JSON = OUT_DIR / "v28_frozen_target_coverage_p70_runway_latest.json"
FROZEN_TARGET_COVERAGE_P70_EB_RUNWAY_JSON = OUT_DIR / "v28_frozen_target_coverage_p70_empirical_bayes_runway_latest.json"
FROZEN_TARGET_COVERAGE_P70_PENDING_JSON = OUT_DIR / "v28_frozen_target_coverage_p70_pending_sensitivity_latest.json"
FROZEN_TARGET_COVERAGE_BOOK_EDGE_GATE_JSON = OUT_DIR / "v28_frozen_target_coverage_book_edge_gate_latest.json"
FROZEN_MID_EDGE_FALSE_CONVICTION_FV_JSON = OUT_DIR / "v28_frozen_mid_edge_false_conviction_fv_latest.json"
FROZEN_COMPOSITE_FALSE_CONVICTION_FV_JSON = OUT_DIR / "v28_frozen_composite_false_conviction_fv_latest.json"
SIDE_ASYMMETRY_RUNWAY_JSON = OUT_DIR / "v28_side_asymmetry_promotion_runway_latest.json"
SIDE_ASYMMETRY_FV_ENTRY_BRIDGE_JSON = OUT_DIR / "v28_side_asymmetry_fv_entry_bridge_latest.json"
SIDE_ASYMMETRY_BRIDGE_REPAIR_BAKEOFF_JSON = OUT_DIR / "v28_side_asymmetry_bridge_repair_bakeoff_latest.json"
SIDE_ASYMMETRY_BRIDGE_STRICT_REPAIR_JSON = OUT_DIR / "v28_side_asymmetry_bridge_strict_repair_latest.json"
FROZEN_SIDE_ASYMMETRY_ENTRY_BRIDGE_JSON = OUT_DIR / "v28_frozen_side_asymmetry_entry_bridge_latest.json"
FROZEN_THIN_RECROSS_MIDP_ENTRY_GATE_JSON = OUT_DIR / "v28_frozen_thin_recross_midp_entry_gate_latest.json"
FROZEN_RAW_P52_BOUNDARY_TURBULENCE_SKIP_JSON = OUT_DIR / "v28_frozen_raw_p52_boundary_turbulence_skip_latest.json"
FROZEN_TARGET_LOSS_TAG_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_target_loss_tag_repair_entry_latest.json"
FROZEN_EARLY_NO_BOUNDARY_DECAY_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_early_no_boundary_decay_repair_entry_latest.json"
EARLY_NO_BOUNDARY_DECAY_REPAIR_RUNWAY_JSON = OUT_DIR / "v28_early_no_boundary_decay_repair_runway_latest.json"
EARLY_NO_BOUNDARY_DECAY_REPAIR_STRESS_JSON = OUT_DIR / "v28_early_no_boundary_decay_repair_stress_latest.json"
FROZEN_MID_EDGE_BOUNDARY_DECEPTION_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_mid_edge_boundary_deception_repair_entry_latest.json"
FROZEN_COMPOSITE_FALSE_CONVICTION_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_composite_false_conviction_repair_entry_latest.json"
FROZEN_GOLDILOCKS_EDGE_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_goldilocks_edge_repair_entry_latest.json"
BOUNDARY_MEMORY_FV_JSON = OUT_DIR / "v28_boundary_memory_fv_candidates_latest.json"
REWARD_MEMORY_FV_JSON = OUT_DIR / "v28_reward_memory_fv_candidates_latest.json"
REWARD_MEMORY_JACKKNIFE_JSON = OUT_DIR / "v28_reward_memory_jackknife_latest.json"
FV_DECISION_MATRIX_JSON = OUT_DIR / "v28_fv_candidate_decision_matrix_latest.json"
PENDING_FV_SENSITIVITY_JSON = OUT_DIR / "v28_pending_fv_sensitivity_latest.json"
ANTI_OVERFIT_FREEZE_AUDIT_JSON = OUT_DIR / "v28_anti_overfit_freeze_audit_latest.json"
GOAL_COMPLETION_AUDIT_JSON = OUT_DIR / "v28_goal_completion_audit_latest.json"
FROZEN_LEADERBOARD_JSON = OUT_DIR / "v28_frozen_candidate_leaderboard_latest.json"
CANDIDATE_INTEGRITY_SCORECARD_JSON = OUT_DIR / "v28_candidate_integrity_scorecard_latest.json"
CANDIDATE_VS_CONTROL_OVERLAP_JSON = OUT_DIR / "v28_candidate_vs_control_overlap_latest.json"
CANDIDATE_LIVE_VALIDATION_RUNWAY_JSON = OUT_DIR / "v28_candidate_live_validation_runway_latest.json"
BROAD_BOOK_EDGE_SOURCE_AUDIT_JSON = OUT_DIR / "v28_broad_book_edge_source_audit_latest.json"
FROZEN_BOOK_EDGE_PENDING_SENSITIVITY_JSON = OUT_DIR / "v28_frozen_book_edge_pending_sensitivity_latest.json"
LIVE_READINESS_JSON = OUT_DIR / "v28_live_trade_readiness_latest.json"
WATCHLIST_JSON = OUT_DIR / "v28_candidate_watchlist_latest.json"
WATCHLIST_MD = OUT_DIR / "v28_candidate_watchlist_latest.md"

MIN_ENTRY_PROMOTION_RESOLVED = 30
MAX_ENTRY_SIMULATED_SHARE = 0.35
MIN_EXIT_PROMOTION_TRADES = 30


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def find_policy(summary_rows: list[dict[str, Any]], name: str) -> dict[str, Any]:
    for row in summary_rows:
        if row.get("policy") == name:
            return row
    return {}


def safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def entry_promotion_checks(row: dict[str, Any]) -> dict[str, Any]:
    entries = safe_float(row.get("entries")) or 0.0
    settled = safe_float(row.get("settled")) or 0.0
    added = safe_float(row.get("added_reject_count")) or 0.0
    simulated_share = (added / entries) if entries else None
    blockers: list[str] = []
    if settled < MIN_ENTRY_PROMOTION_RESOLVED:
        blockers.append(f"settled_sample_lt_{MIN_ENTRY_PROMOTION_RESOLVED}")
    if simulated_share is None or simulated_share > MAX_ENTRY_SIMULATED_SHARE:
        blockers.append(f"simulated_share_gt_{MAX_ENTRY_SIMULATED_SHARE:.0%}")
    return {
        "resolved_min": MIN_ENTRY_PROMOTION_RESOLVED,
        "settled_min": MIN_ENTRY_PROMOTION_RESOLVED,
        "max_simulated_share": MAX_ENTRY_SIMULATED_SHARE,
        "simulated_share": simulated_share,
        "blockers": blockers,
        "promotable": not blockers,
    }


def exit_promotion_checks(row: dict[str, Any], frozen: dict[str, Any], readiness: dict[str, Any]) -> dict[str, Any]:
    summary = frozen.get("summary") or {}
    trades = safe_float(summary.get("settled")) or 0.0
    readiness_row = next(
        (
            item for item in readiness.get("candidates") or []
            if item.get("gate") == "exit_reduce_suppression"
        ),
        {},
    )
    blockers: list[str] = []
    if trades < MIN_EXIT_PROMOTION_TRADES:
        blockers.append(f"scored_trade_sample_lt_{MIN_EXIT_PROMOTION_TRADES}")
    if summary.get("delta_vs_current_cents") is None and row.get("delta_vs_current_cents") is None:
        blockers.append("missing_candidate_delta")
    if readiness.get("control_risk_stop") is True:
        blockers.append("control_risk_stop_active")
    if readiness_row.get("live_ready") is not True:
        blockers.extend(f"readiness:{blocker}" for blocker in (readiness_row.get("blockers") or []))
    return {
        "scored_trade_min": MIN_EXIT_PROMOTION_TRADES,
        "scored_trades": trades,
        "live_ready": readiness_row.get("live_ready"),
        "blockers": blockers,
        "promotable": not blockers,
    }


def build_watchlist() -> dict[str, Any]:
    scorecard = load_json(SCORECARD_JSON)
    exit_candidates = load_json(EXIT_JSON)
    branch_diag = load_json(BRANCH_JSON)
    frozen_exit_reduce = load_json(FROZEN_EXIT_REDUCE_JSON)
    frozen_exit_reduce_yes = load_json(FROZEN_EXIT_REDUCE_YES_JSON)
    exit_reduce_robustness = load_json(EXIT_REDUCE_ROBUSTNESS_JSON)
    exit_reduce_side_split = load_json(EXIT_REDUCE_SIDE_SPLIT_JSON)
    exit_reduce_runway = load_json(EXIT_REDUCE_RUNWAY_JSON)
    exit_book_gap = load_json(EXIT_BOOK_GAP_JSON)
    frozen_exit_book_gap = load_json(FROZEN_EXIT_BOOK_GAP_JSON)
    active_trade_sensitivity = load_json(ACTIVE_TRADE_SENSITIVITY_JSON)
    bakeoff = load_json(BAKEOFF_JSON)
    decay = load_json(DECAY_JSON)
    fv_variants = load_json(FV_VARIANTS_JSON)
    reentry = load_json(REENTRY_JSON)
    rmt = load_json(RMT_JSON)
    state_aware_fv = load_json(STATE_AWARE_FV_JSON)
    rmt_forgetting_entry = load_json(RMT_FORGETTING_ENTRY_JSON)
    book_favorite_edge = load_json(BOOK_FAVORITE_EDGE_JSON)
    frozen_forward = load_json(FROZEN_FORWARD_JSON)
    threshold_challengers = load_json(THRESHOLD_CHALLENGERS_JSON)
    frozen_timing = load_json(FROZEN_TIMING_JSON)
    side_flip = load_json(SIDE_FLIP_JSON)
    side_agreement_meta = load_json(SIDE_AGREEMENT_META_JSON)
    frozen_side_agreement = load_json(FROZEN_SIDE_AGREEMENT_JSON)
    convex_escape = load_json(CONVEX_ESCAPE_JSON)
    frozen_convex_escape = load_json(FROZEN_CONVEX_ESCAPE_JSON)
    raw_conviction = load_json(RAW_CONVICTION_JSON)
    coverage_pressure = load_json(COVERAGE_PRESSURE_JSON)
    raw_physics = load_json(RAW_PHYSICS_JSON)
    raw_p52_delta = load_json(RAW_P52_DELTA_JSON)
    raw_p52_confirmation = load_json(RAW_P52_CONFIRMATION_JSON)
    frozen_raw_physics = load_json(FROZEN_RAW_PHYSICS_JSON)
    raw_p52_sideflip = load_json(RAW_P52_SIDEFLIP_JSON)
    frozen_raw_p52_sideflip = load_json(FROZEN_RAW_P52_SIDEFLIP_JSON)
    raw_p52_recross_escape = load_json(RAW_P52_RECROSS_ESCAPE_JSON)
    frozen_raw_p52_recross_escape = load_json(FROZEN_RAW_P52_RECROSS_ESCAPE_JSON)
    recross_escape_probability = load_json(RECROSS_ESCAPE_PROBABILITY_JSON)
    frozen_recross_escape_attribution = load_json(FROZEN_RECROSS_ESCAPE_ATTRIBUTION_JSON)
    recross_escape_sample_plan = load_json(RECROSS_ESCAPE_SAMPLE_PLAN_JSON)
    noise_shrinkage = load_json(NOISE_SHRINKAGE_JSON)
    frozen_noise_shrinkage = load_json(FROZEN_NOISE_SHRINKAGE_JSON)
    raw_entry_calibrated = load_json(RAW_ENTRY_CALIBRATED_JSON)
    probability_profit_bridge = load_json(PROBABILITY_PROFIT_BRIDGE_JSON)
    approved_entry_fv_overlay = load_json(APPROVED_ENTRY_FV_OVERLAY_JSON)
    approved_entry_book_edge_actionability = load_json(APPROVED_ENTRY_BOOK_EDGE_ACTIONABILITY_JSON)
    frozen_approved_entry_book_edge_gate = load_json(FROZEN_APPROVED_ENTRY_BOOK_EDGE_GATE_JSON)
    entry_posterior_diagnostic = load_json(ENTRY_POSTERIOR_DIAGNOSTIC_JSON)
    source_aware_fv_overlay = load_json(SOURCE_AWARE_FV_OVERLAY_JSON)
    source_aware_fv_robustness_audit = load_json(SOURCE_AWARE_FV_ROBUSTNESS_AUDIT_JSON)
    source_aware_fv_promotion_audit = load_json(SOURCE_AWARE_FV_PROMOTION_AUDIT_JSON)
    approved_entry_state_valves = load_json(APPROVED_ENTRY_STATE_VALVES_JSON)
    frozen_approved_entry_state_valve = load_json(FROZEN_APPROVED_ENTRY_STATE_VALVE_JSON)
    danger_zone_entry_valve = load_json(DANGER_ZONE_ENTRY_VALVE_JSON)
    frozen_danger_zone_entry_valve = load_json(FROZEN_DANGER_ZONE_ENTRY_VALVE_JSON)
    danger_zone_fv_calibration = load_json(DANGER_ZONE_FV_CALIBRATION_JSON)
    frozen_danger_zone_fv_calibration = load_json(FROZEN_DANGER_ZONE_FV_CALIBRATION_JSON)
    danger_zone_robustness_audit = load_json(DANGER_ZONE_ROBUSTNESS_AUDIT_JSON)
    book_trajectory_fv = load_json(BOOK_TRAJECTORY_FV_JSON)
    frozen_book_trajectory_fv = load_json(FROZEN_BOOK_TRAJECTORY_FV_JSON)
    book_trajectory_entry_projection = load_json(BOOK_TRAJECTORY_ENTRY_PROJECTION_JSON)
    frozen_pending_monitor = load_json(FROZEN_PENDING_MONITOR_JSON)
    frozen_forward_scorecard = load_json(FROZEN_FORWARD_SCORECARD_JSON)
    entry_lift_plateau = load_json(ENTRY_LIFT_PLATEAU_JSON)
    entry_jackknife = load_json(ENTRY_JACKKNIFE_JSON)
    entry_data_quality = load_json(ENTRY_DATA_QUALITY_JSON)
    frozen_raw_entry_calibrated = load_json(FROZEN_RAW_ENTRY_CALIBRATED_JSON)
    calibrated_fv_forward_monitor = load_json(CALIBRATED_FV_FORWARD_MONITOR_JSON)
    calibrated_fv_sequential = load_json(CALIBRATED_FV_SEQUENTIAL_EVIDENCE_JSON)
    calibrated_fv_physics_attribution = load_json(CALIBRATED_FV_PHYSICS_ATTRIBUTION_JSON)
    calibrated_fv_path_contradiction = load_json(CALIBRATED_FV_PATH_CONTRADICTION_JSON)
    path_confirmed_entry = load_json(PATH_CONFIRMED_ENTRY_JSON)
    path_rmt_forward_gate = load_json(PATH_RMT_FORWARD_GATE_JSON)
    fv_model_readiness = load_json(FV_MODEL_READINESS_JSON)
    fv_overlay_challenger_readiness = load_json(FV_OVERLAY_CHALLENGER_READINESS_JSON)
    calibrated_fv_sample_plan = load_json(CALIBRATED_FV_SAMPLE_PLAN_JSON)
    raw_entry_coverage_valve = load_json(RAW_ENTRY_COVERAGE_VALVE_JSON)
    target_coverage_fv = load_json(TARGET_COVERAGE_FV_JSON)
    target_coverage_fv_seq = load_json(TARGET_COVERAGE_FV_SEQ_JSON)
    target_coverage_fv_attribution = load_json(TARGET_COVERAGE_FV_ATTRIBUTION_JSON)
    target_coverage_promotion_audit = load_json(TARGET_COVERAGE_PROMOTION_AUDIT_JSON)
    target_coverage_sample_runway = load_json(TARGET_COVERAGE_SAMPLE_RUNWAY_JSON)
    target_coverage_fv_fragility_audit = load_json(TARGET_COVERAGE_FV_FRAGILITY_AUDIT_JSON)
    target_coverage_fv_bucket_reliability = load_json(TARGET_COVERAGE_FV_BUCKET_RELIABILITY_JSON)
    target_coverage_fv_live_evidence_audit = load_json(TARGET_COVERAGE_FV_LIVE_EVIDENCE_AUDIT_JSON)
    target_coverage_danger_overlap = load_json(TARGET_COVERAGE_DANGER_OVERLAP_JSON)
    target_coverage_price_friction = load_json(TARGET_COVERAGE_PRICE_FRICTION_JSON)
    false_conviction_physics = load_json(FALSE_CONVICTION_PHYSICS_JSON)
    false_conviction_family_scorecard = load_json(FALSE_CONVICTION_FAMILY_SCORECARD_JSON)
    false_conviction_source_quality_repair = load_json(FALSE_CONVICTION_SOURCE_QUALITY_REPAIR_JSON)
    composite_false_conviction_repair_robustness = load_json(COMPOSITE_FALSE_CONVICTION_REPAIR_ROBUSTNESS_JSON)
    composite_false_conviction_repair_stress = load_json(COMPOSITE_FALSE_CONVICTION_REPAIR_STRESS_JSON)
    weak_boundary_reversal_strategy = load_json(WEAK_BOUNDARY_REVERSAL_STRATEGY_JSON)
    weak_boundary_reversal_bakeoff = load_json(WEAK_BOUNDARY_REVERSAL_BAKEOFF_JSON)
    weak_reversal_residual_attribution = load_json(WEAK_REVERSAL_RESIDUAL_ATTRIBUTION_JSON)
    weak_reversal_residual_fv_shrink = load_json(WEAK_REVERSAL_RESIDUAL_FV_SHRINK_JSON)
    frozen_weak_reversal_residual_fv_shrink = load_json(FROZEN_WEAK_REVERSAL_RESIDUAL_FV_SHRINK_JSON)
    no_mid_edge_fv_generalization = load_json(NO_MID_EDGE_FV_GENERALIZATION_JSON)
    frozen_no_mid_edge_fv = load_json(FROZEN_NO_MID_EDGE_FV_JSON)
    no_mid_edge_entry_repair = load_json(NO_MID_EDGE_ENTRY_REPAIR_JSON)
    weak_reversal_residual_repair = load_json(WEAK_REVERSAL_RESIDUAL_REPAIR_JSON)
    frozen_weak_reversal_residual_repair = load_json(FROZEN_WEAK_REVERSAL_RESIDUAL_REPAIR_JSON)
    early_clock_wait_bakeoff = load_json(EARLY_CLOCK_WAIT_BAKEOFF_JSON)
    frozen_early_boundary_wait_repair = load_json(FROZEN_EARLY_BOUNDARY_WAIT_REPAIR_JSON)
    frozen_early_boundary_opposite_wait_repair = load_json(FROZEN_EARLY_BOUNDARY_OPPOSITE_WAIT_REPAIR_JSON)
    target_coverage_conservative_fv = load_json(TARGET_COVERAGE_CONSERVATIVE_FV_JSON)
    target_coverage_source_split_fv = load_json(TARGET_COVERAGE_SOURCE_SPLIT_FV_JSON)
    target_coverage_p70_jackknife = load_json(TARGET_COVERAGE_P70_JACKKNIFE_JSON)
    frozen_target_coverage_conservative_fv = load_json(FROZEN_TARGET_COVERAGE_CONSERVATIVE_FV_JSON)
    frozen_target_coverage_conservative_pending = load_json(FROZEN_TARGET_COVERAGE_CONSERVATIVE_PENDING_JSON)
    frozen_target_coverage_p70_fv = load_json(FROZEN_TARGET_COVERAGE_P70_FV_JSON)
    frozen_target_coverage_p70_runway = load_json(FROZEN_TARGET_COVERAGE_P70_RUNWAY_JSON)
    frozen_target_coverage_p70_eb_runway = load_json(FROZEN_TARGET_COVERAGE_P70_EB_RUNWAY_JSON)
    frozen_target_coverage_p70_pending = load_json(FROZEN_TARGET_COVERAGE_P70_PENDING_JSON)
    frozen_target_coverage_book_edge_gate = load_json(FROZEN_TARGET_COVERAGE_BOOK_EDGE_GATE_JSON)
    frozen_mid_edge_false_conviction_fv = load_json(FROZEN_MID_EDGE_FALSE_CONVICTION_FV_JSON)
    frozen_composite_false_conviction_fv = load_json(FROZEN_COMPOSITE_FALSE_CONVICTION_FV_JSON)
    side_asymmetry_runway = load_json(SIDE_ASYMMETRY_RUNWAY_JSON)
    side_asymmetry_fv_entry_bridge = load_json(SIDE_ASYMMETRY_FV_ENTRY_BRIDGE_JSON)
    side_asymmetry_bridge_repair_bakeoff = load_json(SIDE_ASYMMETRY_BRIDGE_REPAIR_BAKEOFF_JSON)
    side_asymmetry_bridge_strict_repair = load_json(SIDE_ASYMMETRY_BRIDGE_STRICT_REPAIR_JSON)
    frozen_side_asymmetry_entry_bridge = load_json(FROZEN_SIDE_ASYMMETRY_ENTRY_BRIDGE_JSON)
    frozen_thin_recross_midp_entry_gate = load_json(FROZEN_THIN_RECROSS_MIDP_ENTRY_GATE_JSON)
    frozen_raw_p52_boundary_turbulence_skip = load_json(FROZEN_RAW_P52_BOUNDARY_TURBULENCE_SKIP_JSON)
    frozen_target_loss_tag_repair_entry = load_json(FROZEN_TARGET_LOSS_TAG_REPAIR_ENTRY_JSON)
    frozen_early_no_boundary_decay_repair_entry = load_json(FROZEN_EARLY_NO_BOUNDARY_DECAY_REPAIR_ENTRY_JSON)
    early_no_boundary_decay_repair_runway = load_json(EARLY_NO_BOUNDARY_DECAY_REPAIR_RUNWAY_JSON)
    early_no_boundary_decay_repair_stress = load_json(EARLY_NO_BOUNDARY_DECAY_REPAIR_STRESS_JSON)
    frozen_mid_edge_boundary_deception_repair_entry = load_json(FROZEN_MID_EDGE_BOUNDARY_DECEPTION_REPAIR_ENTRY_JSON)
    frozen_composite_false_conviction_repair_entry = load_json(FROZEN_COMPOSITE_FALSE_CONVICTION_REPAIR_ENTRY_JSON)
    frozen_goldilocks_edge_repair_entry = load_json(FROZEN_GOLDILOCKS_EDGE_REPAIR_ENTRY_JSON)
    boundary_memory_fv = load_json(BOUNDARY_MEMORY_FV_JSON)
    reward_memory_fv = load_json(REWARD_MEMORY_FV_JSON)
    reward_memory_jackknife = load_json(REWARD_MEMORY_JACKKNIFE_JSON)
    fv_decision_matrix = load_json(FV_DECISION_MATRIX_JSON)
    pending_fv_sensitivity = load_json(PENDING_FV_SENSITIVITY_JSON)
    anti_overfit_freeze_audit = load_json(ANTI_OVERFIT_FREEZE_AUDIT_JSON)
    goal_completion_audit = load_json(GOAL_COMPLETION_AUDIT_JSON)
    frozen_leaderboard = load_json(FROZEN_LEADERBOARD_JSON)
    candidate_integrity = load_json(CANDIDATE_INTEGRITY_SCORECARD_JSON)
    candidate_vs_control_overlap = load_json(CANDIDATE_VS_CONTROL_OVERLAP_JSON)
    candidate_live_validation_runway = load_json(CANDIDATE_LIVE_VALIDATION_RUNWAY_JSON)
    broad_book_edge_source_audit = load_json(BROAD_BOOK_EDGE_SOURCE_AUDIT_JSON)
    frozen_book_edge_pending_sensitivity = load_json(FROZEN_BOOK_EDGE_PENDING_SENSITIVITY_JSON)
    live_readiness = load_json(LIVE_READINESS_JSON)

    exit_rows = exit_candidates.get("summary") if isinstance(exit_candidates.get("summary"), list) else []
    branch_summary = branch_diag.get("summary", {}).get("by_branch", {})
    bakeoff_summary = bakeoff.get("ranked") if isinstance(bakeoff.get("ranked"), list) else []

    reduce_only = find_policy(exit_rows, "suppress_reduce_p_hold_ge_075")
    exit_candidate = reduce_only
    voh_only = find_policy(exit_rows, "suppress_voh_p_hold_ge_075")
    entry_candidate = find_policy(bakeoff_summary, "book_plus_05_no_cheap_yes_boundary")
    baseline = find_policy(bakeoff_summary, "baseline_v28_approved")

    score = scorecard.get("summary", {})
    return {
        "scorecard_summary": score,
        "exit_watch": {
            "candidate": "suppress_reduce_p_hold_ge_075",
            "status": "shadow_only",
            "reason": "Frozen forward validator targets probability-reduce exits that clip a still-strong held-side thesis.",
            "candidate_row": exit_candidate,
            "reduce_only_row": reduce_only,
            "voh_only_row": voh_only,
            "branch_summary": branch_summary,
            "frozen_exit_reduce_summary": frozen_exit_reduce,
            "frozen_exit_reduce_yes_summary": frozen_exit_reduce_yes,
            "exit_reduce_robustness_summary": exit_reduce_robustness,
            "exit_reduce_side_split_summary": exit_reduce_side_split,
            "exit_reduce_runway_summary": exit_reduce_runway,
            "exit_book_gap_summary": exit_book_gap,
            "frozen_exit_book_gap_summary": frozen_exit_book_gap,
            "active_trade_sensitivity_summary": active_trade_sensitivity,
            "promotion_checks": exit_promotion_checks(exit_candidate, frozen_exit_reduce, live_readiness),
        },
        "entry_watch": {
            "candidate": "book_plus_05_no_cheap_yes_boundary",
            "status": "shadow_only",
            "reason": "Best current broad discovery row after removing cheap YES boundary-pull traps; frozen future validation has just started and still includes rejected-actionable rows.",
            "candidate_row": entry_candidate,
            "baseline_row": baseline,
            "promotion_checks": entry_promotion_checks(entry_candidate),
            "rmt_forgetting_entry_summary": rmt_forgetting_entry,
            "book_favorite_edge_summary": book_favorite_edge,
            "frozen_forward_summary": frozen_forward,
            "threshold_challenger_summary": threshold_challengers,
            "frozen_timing_summary": frozen_timing,
            "side_flip_summary": side_flip,
            "side_agreement_meta_summary": side_agreement_meta,
            "frozen_side_agreement_summary": frozen_side_agreement,
            "convex_escape_summary": convex_escape,
            "frozen_convex_escape_summary": frozen_convex_escape,
            "raw_conviction_override_summary": raw_conviction,
            "coverage_pressure_summary": coverage_pressure,
            "raw_physics_summary": raw_physics,
            "raw_p52_delta_summary": raw_p52_delta,
            "raw_p52_confirmation_summary": raw_p52_confirmation,
            "frozen_raw_physics_summary": frozen_raw_physics,
            "raw_p52_sideflip_summary": raw_p52_sideflip,
            "frozen_raw_p52_sideflip_summary": frozen_raw_p52_sideflip,
            "raw_p52_recross_escape_summary": raw_p52_recross_escape,
            "frozen_raw_p52_recross_escape_summary": frozen_raw_p52_recross_escape,
            "recross_escape_probability_summary": recross_escape_probability,
            "frozen_recross_escape_attribution_summary": frozen_recross_escape_attribution,
            "recross_escape_sample_plan_summary": recross_escape_sample_plan,
            "noise_shrinkage_summary": noise_shrinkage,
            "frozen_noise_shrinkage_summary": frozen_noise_shrinkage,
            "raw_entry_calibrated_summary": raw_entry_calibrated,
            "probability_profit_bridge_summary": probability_profit_bridge,
            "approved_entry_fv_overlay_summary": approved_entry_fv_overlay,
            "approved_entry_book_edge_actionability_summary": approved_entry_book_edge_actionability,
            "frozen_approved_entry_book_edge_gate_summary": frozen_approved_entry_book_edge_gate,
            "entry_posterior_diagnostic_summary": entry_posterior_diagnostic,
            "source_aware_fv_overlay_summary": source_aware_fv_overlay,
            "source_aware_fv_robustness_audit_summary": source_aware_fv_robustness_audit,
            "source_aware_fv_promotion_audit_summary": source_aware_fv_promotion_audit,
            "approved_entry_state_valves_summary": approved_entry_state_valves,
            "frozen_approved_entry_state_valve_summary": frozen_approved_entry_state_valve,
            "danger_zone_entry_valve_summary": danger_zone_entry_valve,
            "frozen_danger_zone_entry_valve_summary": frozen_danger_zone_entry_valve,
            "danger_zone_fv_calibration_summary": danger_zone_fv_calibration,
            "frozen_danger_zone_fv_calibration_summary": frozen_danger_zone_fv_calibration,
            "danger_zone_robustness_audit_summary": danger_zone_robustness_audit,
            "book_trajectory_fv_summary": book_trajectory_fv,
            "frozen_book_trajectory_fv_summary": frozen_book_trajectory_fv,
            "book_trajectory_entry_projection_summary": book_trajectory_entry_projection,
            "frozen_pending_monitor_summary": frozen_pending_monitor,
            "frozen_forward_scorecard_summary": frozen_forward_scorecard,
            "entry_lift_plateau_summary": entry_lift_plateau,
            "entry_jackknife_summary": entry_jackknife,
            "entry_data_quality_summary": entry_data_quality,
            "frozen_raw_entry_calibrated_summary": frozen_raw_entry_calibrated,
            "calibrated_fv_forward_monitor_summary": calibrated_fv_forward_monitor,
            "calibrated_fv_sequential_summary": calibrated_fv_sequential,
            "calibrated_fv_physics_attribution_summary": calibrated_fv_physics_attribution,
            "calibrated_fv_path_contradiction_summary": calibrated_fv_path_contradiction,
            "path_confirmed_entry_summary": path_confirmed_entry,
            "path_rmt_forward_gate_summary": path_rmt_forward_gate,
            "fv_model_readiness_summary": fv_model_readiness,
            "fv_overlay_challenger_readiness_summary": fv_overlay_challenger_readiness,
            "calibrated_fv_sample_plan_summary": calibrated_fv_sample_plan,
            "raw_entry_coverage_valve_summary": raw_entry_coverage_valve,
            "target_coverage_fv_summary": target_coverage_fv,
            "target_coverage_fv_sequential_summary": target_coverage_fv_seq,
            "target_coverage_fv_attribution_summary": target_coverage_fv_attribution,
            "target_coverage_promotion_audit_summary": target_coverage_promotion_audit,
            "target_coverage_sample_runway_summary": target_coverage_sample_runway,
            "target_coverage_fv_fragility_audit_summary": target_coverage_fv_fragility_audit,
            "target_coverage_fv_bucket_reliability_summary": target_coverage_fv_bucket_reliability,
            "target_coverage_fv_live_evidence_audit_summary": target_coverage_fv_live_evidence_audit,
            "target_coverage_danger_overlap_summary": target_coverage_danger_overlap,
            "target_coverage_price_friction_summary": target_coverage_price_friction,
            "false_conviction_physics_summary": false_conviction_physics,
            "false_conviction_family_scorecard_summary": false_conviction_family_scorecard,
            "false_conviction_source_quality_repair_summary": false_conviction_source_quality_repair,
            "composite_false_conviction_repair_robustness_summary": composite_false_conviction_repair_robustness,
            "composite_false_conviction_repair_stress_summary": composite_false_conviction_repair_stress,
            "weak_boundary_reversal_strategy_summary": weak_boundary_reversal_strategy,
            "weak_boundary_reversal_bakeoff_summary": weak_boundary_reversal_bakeoff,
            "weak_reversal_residual_attribution_summary": weak_reversal_residual_attribution,
            "weak_reversal_residual_fv_shrink_summary": weak_reversal_residual_fv_shrink,
            "frozen_weak_reversal_residual_fv_shrink_summary": frozen_weak_reversal_residual_fv_shrink,
            "no_mid_edge_fv_generalization_summary": no_mid_edge_fv_generalization,
            "frozen_no_mid_edge_fv_summary": frozen_no_mid_edge_fv,
            "no_mid_edge_entry_repair_summary": no_mid_edge_entry_repair,
            "weak_reversal_residual_repair_summary": weak_reversal_residual_repair,
            "frozen_weak_reversal_residual_repair_summary": frozen_weak_reversal_residual_repair,
            "early_clock_wait_bakeoff_summary": early_clock_wait_bakeoff,
            "frozen_early_boundary_wait_repair_summary": frozen_early_boundary_wait_repair,
            "frozen_early_boundary_opposite_wait_repair_summary": frozen_early_boundary_opposite_wait_repair,
            "target_coverage_conservative_fv_summary": target_coverage_conservative_fv,
            "target_coverage_source_split_fv_summary": target_coverage_source_split_fv,
            "target_coverage_p70_jackknife_summary": target_coverage_p70_jackknife,
            "frozen_target_coverage_conservative_fv_summary": frozen_target_coverage_conservative_fv,
            "frozen_target_coverage_conservative_pending_summary": frozen_target_coverage_conservative_pending,
            "frozen_target_coverage_p70_fv_summary": frozen_target_coverage_p70_fv,
            "frozen_target_coverage_p70_runway_summary": frozen_target_coverage_p70_runway,
            "frozen_target_coverage_p70_empirical_bayes_runway_summary": frozen_target_coverage_p70_eb_runway,
            "frozen_target_coverage_p70_pending_sensitivity_summary": frozen_target_coverage_p70_pending,
            "frozen_target_coverage_book_edge_gate_summary": frozen_target_coverage_book_edge_gate,
            "frozen_mid_edge_false_conviction_fv_summary": frozen_mid_edge_false_conviction_fv,
            "frozen_composite_false_conviction_fv_summary": frozen_composite_false_conviction_fv,
            "side_asymmetry_promotion_runway_summary": side_asymmetry_runway,
            "side_asymmetry_fv_entry_bridge_summary": side_asymmetry_fv_entry_bridge,
            "side_asymmetry_bridge_repair_bakeoff_summary": side_asymmetry_bridge_repair_bakeoff,
            "side_asymmetry_bridge_strict_repair_summary": side_asymmetry_bridge_strict_repair,
            "frozen_side_asymmetry_entry_bridge_summary": frozen_side_asymmetry_entry_bridge,
            "frozen_thin_recross_midp_entry_gate_summary": frozen_thin_recross_midp_entry_gate,
            "frozen_raw_p52_boundary_turbulence_skip_summary": frozen_raw_p52_boundary_turbulence_skip,
            "frozen_target_loss_tag_repair_entry_summary": frozen_target_loss_tag_repair_entry,
            "frozen_early_no_boundary_decay_repair_entry_summary": frozen_early_no_boundary_decay_repair_entry,
            "early_no_boundary_decay_repair_runway_summary": early_no_boundary_decay_repair_runway,
            "early_no_boundary_decay_repair_stress_summary": early_no_boundary_decay_repair_stress,
            "frozen_mid_edge_boundary_deception_repair_entry_summary": frozen_mid_edge_boundary_deception_repair_entry,
            "frozen_composite_false_conviction_repair_entry_summary": frozen_composite_false_conviction_repair_entry,
            "frozen_goldilocks_edge_repair_entry_summary": frozen_goldilocks_edge_repair_entry,
            "boundary_memory_fv_summary": boundary_memory_fv,
            "reward_memory_fv_summary": reward_memory_fv,
            "reward_memory_jackknife_summary": reward_memory_jackknife,
            "fv_decision_matrix_summary": fv_decision_matrix,
            "pending_fv_sensitivity_summary": pending_fv_sensitivity,
            "anti_overfit_freeze_audit_summary": anti_overfit_freeze_audit,
            "goal_completion_audit_summary": goal_completion_audit,
            "frozen_leaderboard_summary": frozen_leaderboard,
            "candidate_integrity_scorecard_summary": candidate_integrity,
            "candidate_vs_control_overlap_summary": candidate_vs_control_overlap,
            "candidate_live_validation_runway_summary": candidate_live_validation_runway,
            "broad_book_edge_source_audit_summary": broad_book_edge_source_audit,
            "frozen_book_edge_pending_sensitivity_summary": frozen_book_edge_pending_sensitivity,
            "live_readiness_summary": live_readiness,
        },
        "state_watch": {
            "candidate": "no_same_side_reentry",
            "status": "shadow_only",
            "reason": "Allows side flips but blocks repeated entries on the same side in the same 15m market.",
            "rows": reentry.get("summary", []),
        },
        "fv_watch": {
            "candidate": "information_decay_state_penalty",
            "status": "diagnostic_only",
            "reason": "Tests whether stale same-market evidence should be forgotten faster after live probability/book updates.",
            "decay_summary": decay.get("summary", {}),
            "fv_variant_summary": fv_variants.get("summary", {}),
            "rmt_regime_summary": rmt.get("summary", {}),
            "state_aware_fv_summary": state_aware_fv,
        },
        "avoid_watch": {
            "status": "do_not_promote",
            "reason": "Cheap low-probability/near-boundary expansion keeps producing losses in forward rows.",
        },
    }


def fmt_cents(value: Any) -> str:
    try:
        return f"{float(value):.0f}c"
    except (TypeError, ValueError):
        return "None"


def fmt_pct(value: Any) -> str:
    try:
        return f"{float(value) * 100.0:.1f}%"
    except (TypeError, ValueError):
        return "None"


def write_md(payload: dict[str, Any]) -> None:
    score = payload["scorecard_summary"]
    exit_watch = payload["exit_watch"]
    entry_watch = payload["entry_watch"]
    state_watch = payload["state_watch"]
    fv_watch = payload["fv_watch"]
    exit_row = exit_watch.get("candidate_row") or {}
    entry_row = entry_watch.get("candidate_row") or {}
    baseline_row = entry_watch.get("baseline_row") or {}
    exit_checks = exit_watch.get("promotion_checks") or {}
    entry_checks = entry_watch.get("promotion_checks") or {}
    lines = [
        "# v28 Candidate Watchlist",
        "",
        "Forward-only watchlist for the active v28 improvement goal. No candidate here is promoted.",
        "",
        "## Current Control",
        "",
        f"- Entries: `{score.get('entries')}`",
        f"- Gross P&L: `${float(score.get('gross_cents') or 0) / 100.0:.2f}`",
        f"- Current balance reference: `${float(score.get('current_account_balance_cents') or 0) / 100.0:.2f}`",
        f"- Risk stop active: `{score.get('risk_stop')}`",
        "",
        "## Exit Watch",
        "",
        f"- Candidate: `{exit_watch['candidate']}`",
        f"- Status: `{exit_watch['status']}`",
        f"- Reason: {exit_watch['reason']}",
        f"- Candidate gross: `{fmt_cents(exit_row.get('gross_cents'))}`",
        f"- Delta vs current: `{fmt_cents(exit_row.get('delta_vs_current_cents'))}`",
        f"- Worst mark: `{fmt_cents(exit_row.get('worst_intratrade_mark_cents'))}`",
        f"- Live readiness: `{exit_checks.get('live_ready')}`",
        f"- Promotion status: `{'eligible' if exit_checks.get('promotable') else 'blocked'}`",
        f"- Promotion blockers: `{', '.join(exit_checks.get('blockers') or []) or 'none'}`",
        "",
    ]
    frozen_exit_reduce = exit_watch.get("frozen_exit_reduce_summary") or {}
    if frozen_exit_reduce:
        frozen_summary = frozen_exit_reduce.get("summary") or {}
        lines.extend([
            "### Frozen Reduce-Suppression Validator",
            "",
            f"- Future settled rows: `{frozen_summary.get('settled')}`",
            f"- Frozen delta vs current: `{fmt_cents(frozen_summary.get('delta_vs_current_cents'))}`",
            f"- Suppressed exits: `{frozen_summary.get('suppressed_exits')}`",
            f"- Frozen blockers: `{', '.join(frozen_exit_reduce.get('blockers') or []) or 'none'}`",
            "",
        ])
    frozen_exit_reduce_yes = exit_watch.get("frozen_exit_reduce_yes_summary") or {}
    if frozen_exit_reduce_yes:
        frozen_yes_summary = frozen_exit_reduce_yes.get("summary") or {}
        lines.extend([
            "### Frozen YES-Only Reduce-Suppression Validator",
            "",
            "- Narrow side-asymmetric validator created because the full reduce-suppression evidence has not proven NO-side behavior.",
            f"- Future settled rows: `{frozen_yes_summary.get('settled')}`",
            f"- Frozen delta vs current: `{fmt_cents(frozen_yes_summary.get('delta_vs_current_cents'))}`",
            f"- Suppressed exits: `{frozen_yes_summary.get('suppressed_exits')}`",
            f"- Suppressed W/L: `{frozen_yes_summary.get('suppressed_winners')}/{frozen_yes_summary.get('suppressed_losers')}`",
            f"- Frozen blockers: `{', '.join(frozen_exit_reduce_yes.get('blockers') or []) or 'none'}`",
            "",
        ])
    exit_reduce_robustness = exit_watch.get("exit_reduce_robustness_summary") or {}
    if exit_reduce_robustness:
        lines.extend([
            "### Reduce-Suppression Robustness",
            "",
            f"- Shadow interest: `{exit_reduce_robustness.get('shadow_interest')}`",
            f"- Promotion ready: `{exit_reduce_robustness.get('promotion_ready')}`",
            f"- Robustness blockers: `{', '.join(exit_reduce_robustness.get('blockers') or []) or 'none'}`",
            "",
        ])
    exit_reduce_side_split = exit_watch.get("exit_reduce_side_split_summary") or {}
    if exit_reduce_side_split:
        lines.extend([
            "### Reduce-Suppression Side Split",
            "",
            "- Diagnostic split of the frozen reduce-suppression window; this is not promotion evidence for the fresh YES-only validator.",
        ])
        for row in exit_reduce_side_split.get("policies") or []:
            lines.append(
                f"- `{row.get('policy')}`: settled `{row.get('settled')}`, "
                f"delta `{fmt_cents(row.get('delta_vs_current_cents'))}`, "
                f"suppressed `{row.get('suppressed')}`, W/L `{row.get('suppressed_winners')}/{row.get('suppressed_losers')}`, "
                f"loss cost `{fmt_cents(row.get('loss_control_cost_cents'))}`"
            )
        lines.append("")
    exit_reduce_runway = exit_watch.get("exit_reduce_runway_summary") or {}
    if exit_reduce_runway:
        runway = exit_reduce_runway.get("runway") or {}
        lines.extend([
            "### Exit Reduce Promotion Runway",
            "",
            "- Defines what still has to happen before reduce-suppression can be considered.",
            f"- Rows needed for 30: `{runway.get('rows_needed_for_30')}`",
            f"- Current delta: `{fmt_cents(runway.get('current_delta_cents'))}`",
            f"- Suppressed exits: `{runway.get('current_suppressed_exits')}`",
            f"- Invalidators now: `{', '.join(exit_reduce_runway.get('invalidators_now') or []) or 'none'}`",
            "",
        ])
    exit_book_gap = exit_watch.get("exit_book_gap_summary") or {}
    if exit_book_gap:
        lines.extend([
            "### Exit Book-Gap Candidates",
            "",
            "- Tests whether soft exits should be suppressed when p_hold exceeds executable exit bid.",
        ])
        for note in exit_book_gap.get("interpretation") or []:
            lines.append(f"- {note}")
        for row in (exit_book_gap.get("summary") or [])[:5]:
            lines.append(
                f"- `{row.get('policy')}`: trades `{row.get('trades')}`, W/L `{row.get('wins')}/{row.get('losses')}`, "
                f"gross/delta `{fmt_cents(row.get('gross_cents'))}/{fmt_cents(row.get('delta_vs_current_cents'))}`, "
                f"suppressed `{row.get('suppressed_exits')}`, worst mark `{fmt_cents(row.get('worst_intratrade_mark_cents'))}`"
            )
        lines.append("")
    frozen_exit_book_gap = exit_watch.get("frozen_exit_book_gap_summary") or {}
    if frozen_exit_book_gap:
        frozen_gap_summary = frozen_exit_book_gap.get("summary") or {}
        lines.extend([
            "### Frozen Exit Book-Gap Suppression",
            "",
            "- Future-only validator for suppressing soft exits when held-side FV still dominates the executable exit bid.",
            f"- Candidate: `{(frozen_exit_book_gap.get('freeze') or {}).get('candidate')}`",
            f"- Future settled rows: `{frozen_gap_summary.get('settled')}`",
            f"- Frozen delta vs current: `{fmt_cents(frozen_gap_summary.get('delta_vs_current_cents'))}`",
            f"- Suppressed exits: `{frozen_gap_summary.get('suppressed_exits')}`",
            f"- Frozen blockers: `{', '.join(frozen_exit_book_gap.get('blockers') or []) or 'none'}`",
            "",
        ])
    active_sensitivity = exit_watch.get("active_trade_sensitivity_summary") or {}
    if active_sensitivity:
        lines.extend([
            "### Active Trade Sensitivity",
            "",
            "- Shows unresolved trades and what settlement outcomes imply for current exit value and frozen candidates.",
            f"- Active/unresolved trades: `{active_sensitivity.get('active_count')}`",
        ])
        for note in active_sensitivity.get("interpretation") or []:
            lines.append(f"- {note}")
        lines.append("")
    lines.extend([
        "## Entry Watch",
        "",
        f"- Candidate: `{entry_watch['candidate']}`",
        f"- Status: `{entry_watch['status']}`",
        f"- Reason: {entry_watch['reason']}",
        f"- Candidate entries/resolved/settled/wins/losses: `{entry_row.get('entries')}/{entry_row.get('resolved')}/{entry_row.get('settled')}/{entry_row.get('wins')}/{entry_row.get('losses')}`",
        f"- Candidate actual/simulated rows: `{entry_row.get('approved_entry_count')}/{entry_row.get('added_reject_count')}`",
        f"- Candidate simulated share: `{fmt_pct(entry_checks.get('simulated_share'))}`",
        f"- Candidate coverage: `{entry_row.get('coverage_pct')}`",
        f"- Candidate gross: `{fmt_cents(entry_row.get('gross_cents'))}`",
        f"- Baseline entries/resolved/settled/wins/losses: `{baseline_row.get('entries')}/{baseline_row.get('resolved')}/{baseline_row.get('settled')}/{baseline_row.get('wins')}/{baseline_row.get('losses')}`",
        f"- Baseline gross: `{fmt_cents(baseline_row.get('gross_cents'))}`",
        f"- Promotion status: `{'eligible' if entry_checks.get('promotable') else 'blocked'}`",
        f"- Promotion blockers: `{', '.join(entry_checks.get('blockers') or []) or 'none'}`",
    ])
    rmt_entry = entry_watch.get("rmt_forgetting_entry_summary") or {}
    broad_rows = rmt_entry.get("ranked_broad_coverage") or []
    if broad_rows:
        lines.extend([
            "",
            "### RMT Forgetting Broad Entry Watch",
            "",
        "- These rows target roughly 70-90% market coverage and remain shadow-only.",
        ])
        temporal = rmt_entry.get("temporal") or {}
        for row in broad_rows[:5]:
            checks = entry_promotion_checks(row)
            trow = temporal.get(str(row.get("policy") or ""), {})
            brow = (rmt_entry.get("bootstrap") or {}).get(str(row.get("policy") or ""), {})
            early_gross = ((trow.get("early") or {}).get("net_gross_cents_after_entry_fee"))
            late_gross = ((trow.get("late") or {}).get("net_gross_cents_after_entry_fee"))
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"wins/losses `{row.get('wins')}/{row.get('losses')}`, coverage `{row.get('coverage_pct')}`, "
                f"gross/net `{fmt_cents(row.get('gross_cents'))}/{fmt_cents(row.get('net_gross_cents_after_entry_fee'))}`, brier `{row.get('avg_brier')}`, "
                f"actual/sim `{row.get('approved_entry_count')}/{row.get('added_reject_count')}`, "
                f"early/late net `{fmt_cents(early_gross)}/{fmt_cents(late_gross)}`, "
                f"boot net p10/p50 `{fmt_cents(brow.get('gross_p10'))}/{fmt_cents(brow.get('gross_p50'))}`, "
                f"boot p>0 `{brow.get('prob_gross_positive')}`, "
                f"blockers `{', '.join(checks.get('blockers') or []) or 'none'}`"
            )
    book_edge = entry_watch.get("book_favorite_edge_summary") or {}
    book_summary = book_edge.get("summary") or []
    if book_summary:
        lines.extend([
            "",
            "### Book-Favorite Edge Check",
            "",
            "- Checks whether book-anchored candidate rows beat executable ask after estimated entry fees.",
        ])
        for policy in ["first_side_raw_later_book_p60_edge0", "rmt_repetition_forget_p60_edge0", "book_ask_prior_p60_edge0"]:
            for group in ["all", "mode_book_exact"]:
                row = next((item for item in book_summary if item.get("policy") == policy and item.get("group") == group), None)
                if not row:
                    continue
                lines.append(
                    f"- `{policy}` `{group}`: count `{row.get('count')}`, wins/losses `{row.get('wins')}/{row.get('losses')}`, "
                    f"avg ask `{row.get('avg_ask_prob')}`, realized edge vs ask `{row.get('realized_edge_vs_ask_prob')}`, "
                    f"net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`"
                )
    frozen = entry_watch.get("frozen_forward_summary") or {}
    frozen_rows = frozen.get("summary") or []
    if frozen:
        lines.extend([
            "",
            "### Frozen Forward Candidate Gate",
            "",
            f"- Freeze timestamp UTC: `{frozen.get('freeze_ts')}`",
            f"- Forward market denominator: `{frozen.get('forward_market_denominator')}`",
            f"- Excluded in-progress post-freeze markets: `{len(frozen.get('excluded_in_progress_markets') or [])}`",
            f"- Future candidate rows: `{frozen.get('future_candidate_rows')}`",
        ])
        for row in frozen_rows:
            fv_checks = row.get("fv_validation_checks") or {}
            exec_checks = row.get("execution_promotion_checks") or row.get("promotion_checks") or {}
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"wins/losses `{row.get('wins')}/{row.get('losses')}`, coverage `{row.get('coverage_pct')}`, "
                f"net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, brier `{row.get('avg_brier')}`, "
                f"actual/sim `{row.get('approved_entry_count')}/{row.get('added_reject_count')}`, "
                f"fv blockers `{', '.join(fv_checks.get('blockers') or []) or 'none'}`, "
                f"execution blockers `{', '.join(exec_checks.get('blockers') or []) or 'none'}`"
            )
    challengers = entry_watch.get("threshold_challenger_summary") or {}
    challenger_rows = challengers.get("summary") or []
    if challengers:
        lines.extend([
            "",
            "### Frozen Threshold Challengers",
            "",
            f"- Freeze timestamp UTC: `{challengers.get('freeze_ts')}`",
            f"- Forward market denominator: `{challengers.get('forward_market_denominator')}`",
            f"- Future candidate rows: `{challengers.get('future_candidate_rows')}`",
        ])
        for row in challenger_rows:
            fv_checks = row.get("fv_validation_checks") or {}
            exec_checks = row.get("execution_promotion_checks") or {}
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"coverage `{row.get('coverage_pct')}`, net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, "
                f"brier `{row.get('avg_brier')}`, missed `{row.get('missed_forward_market_count')}`, "
                f"fv blockers `{', '.join(fv_checks.get('blockers') or []) or 'none'}`, "
                f"execution blockers `{', '.join(exec_checks.get('blockers') or []) or 'none'}`"
            )
    timing = entry_watch.get("frozen_timing_summary") or {}
    timing_rows = timing.get("rows") or []
    if timing_rows:
        lines.extend([
            "",
            "### Frozen Timing Diagnostic",
            "",
            f"- Markets with selected rows: `{timing.get('markets')}`",
        ])
        for row in timing_rows[-8:]:
            lines.append(
                f"- `{row.get('market')}` `{row.get('gate')}` `{row.get('policy')}`: "
                f"delay `{row.get('delay_vs_first_seconds')}`, side `{row.get('side')}`, "
                f"same_first `{row.get('same_side_as_first')}`, p_eff `{row.get('p_eff')}`, "
                f"ask `{row.get('ask_prob')}`, edge `{row.get('eff_edge_prob')}`, won `{row.get('side_won')}`"
            )
    side_flip = entry_watch.get("side_flip_summary") or {}
    side_summary = side_flip.get("summary") or []
    if side_summary:
        lines.extend([
            "",
            "### Side-Flip Path Diagnostic",
            "",
            "- Compares raw broad first entry against later/book-anchored entries when side agrees or flips.",
        ])
        for row in side_summary:
            if row.get("status") in {"same_side", "side_flip"}:
                lines.append(
                    f"- `{row.get('late_policy')}` `{row.get('status')}`: count `{row.get('count')}`, "
                    f"settled `{row.get('settled')}`, early wins `{row.get('early_wins')}`, "
                    f"late wins `{row.get('late_wins')}`, early net `{fmt_cents(row.get('early_net_cents'))}`, "
                    f"late net `{fmt_cents(row.get('late_net_cents'))}`, "
                    f"late-early `{fmt_cents(row.get('late_minus_early_net_cents'))}`"
                )
    side_meta = entry_watch.get("side_agreement_meta_summary") or {}
    if side_meta.get("summary"):
        lines.extend([
            "",
            "### Side-Agreement Meta Candidate",
            "",
            "- Discovery-only until its frozen gate accumulates future rows.",
        ])
        for row in side_meta.get("summary") or []:
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"coverage `{row.get('coverage_pct')}`, net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, "
                f"brier `{row.get('avg_brier')}`, same/raw `{row.get('same_side_use_raw')}`, "
                f"flip/wait `{row.get('side_flip_use_wait')}`"
            )
    frozen_side = entry_watch.get("frozen_side_agreement_summary") or {}
    if frozen_side:
        lines.extend([
            "",
            "### Frozen Side-Agreement Challengers",
            "",
            f"- Freeze timestamp UTC: `{frozen_side.get('freeze_ts')}`",
            f"- Forward market denominator: `{frozen_side.get('forward_market_denominator')}`",
            f"- Future candidate rows: `{frozen_side.get('future_candidate_rows')}`",
        ])
        for row in frozen_side.get("summary") or []:
            fv_checks = row.get("fv_validation_checks") or {}
            exec_checks = row.get("execution_promotion_checks") or {}
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"coverage `{row.get('coverage_pct')}`, net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, "
                f"brier `{row.get('avg_brier')}`, missed `{row.get('missed_forward_market_count')}`, "
                f"fv blockers `{', '.join(fv_checks.get('blockers') or []) or 'none'}`, "
                f"execution blockers `{', '.join(exec_checks.get('blockers') or []) or 'none'}`"
            )
    convex = entry_watch.get("convex_escape_summary") or {}
    if convex.get("summary"):
        lines.extend([
            "",
            "### Convex Raw-Escape Candidate",
            "",
            "- Discovery-only until its frozen gate accumulates future rows.",
        ])
        for row in convex.get("summary") or []:
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"coverage `{row.get('coverage_pct')}`, net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, "
                f"brier `{row.get('avg_brier')}`, raw_escape `{row.get('raw_high_convex_edge')}`, "
                f"wait `{row.get('use_wait_policy')}`"
            )
    frozen_convex = entry_watch.get("frozen_convex_escape_summary") or {}
    if frozen_convex:
        lines.extend([
            "",
            "### Frozen Convex Raw-Escape Challengers",
            "",
            f"- Freeze timestamp UTC: `{frozen_convex.get('freeze_ts')}`",
            f"- Forward market denominator: `{frozen_convex.get('forward_market_denominator')}`",
            f"- Future candidate rows: `{frozen_convex.get('future_candidate_rows')}`",
        ])
        for row in frozen_convex.get("summary") or []:
            fv_checks = row.get("fv_validation_checks") or {}
            exec_checks = row.get("execution_promotion_checks") or {}
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"coverage `{row.get('coverage_pct')}`, net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, "
                f"brier `{row.get('avg_brier')}`, raw_escape `{row.get('raw_high_convex_edge')}`, "
                f"wait `{row.get('use_wait_policy')}`, "
                f"fv blockers `{', '.join(fv_checks.get('blockers') or []) or 'none'}`, "
                f"execution blockers `{', '.join(exec_checks.get('blockers') or []) or 'none'}`"
            )
    raw_conviction = entry_watch.get("raw_conviction_override_summary") or {}
    raw_conviction_summary = raw_conviction.get("summary") or {}
    status_rows = raw_conviction_summary.get("by_alt_status") or []
    edge_status_rows = raw_conviction_summary.get("by_status_edge") or []
    if status_rows:
        lines.extend([
            "",
            "### Raw-Conviction Override Diagnostic",
            "",
            "- Tests whether strong raw v28 executable edge should override later book/RMT side flips.",
        ])
        for row in status_rows:
            bucket = str(row.get("bucket") or "")
            if ":side_flip" in bucket or ":same_side" in bucket:
                lines.append(
                    f"- `{bucket}`: count `{row.get('count')}`, settled `{row.get('settled')}`, "
                    f"raw W/L `{row.get('raw_wins')}/{row.get('raw_losses')}`, "
                    f"raw net `{fmt_cents(row.get('raw_net_cents'))}`, "
                    f"alt W/L `{row.get('alt_wins')}/{row.get('alt_losses')}`, "
                    f"alt net `{fmt_cents(row.get('alt_net_cents'))}`, "
                    f"alt-raw `{fmt_cents(row.get('alt_minus_raw_cents'))}`"
                )
        high_edge_flip_rows = [
            row for row in edge_status_rows
            if ":side_flip:raw_edge_ge_20pp" in str(row.get("bucket") or "")
            or ":side_flip:raw_edge_0_5pp" in str(row.get("bucket") or "")
        ]
        if high_edge_flip_rows:
            lines.append("- Side-flip edge buckets:")
            for row in high_edge_flip_rows:
                lines.append(
                    f"  - `{row.get('bucket')}`: settled `{row.get('settled')}`, "
                    f"raw net `{fmt_cents(row.get('raw_net_cents'))}`, "
                    f"alt net `{fmt_cents(row.get('alt_net_cents'))}`, "
                    f"alt-raw `{fmt_cents(row.get('alt_minus_raw_cents'))}`"
                )
    coverage_pressure = entry_watch.get("coverage_pressure_summary") or {}
    coverage_rows = coverage_pressure.get("summary") or []
    if coverage_rows:
        lines.extend([
            "",
            "### Coverage Pressure Audit",
            "",
            "- Scores missed forward markets after settlement to distinguish healthy abstentions from coverage mistakes.",
        ])
        for row in coverage_rows:
            lines.append(
                f"- `{row.get('source')}` `{row.get('policy')}`: misses `{row.get('misses')}`, "
                f"resolved `{row.get('resolved')}`, pending `{row.get('pending')}`, "
                f"near-miss net `{fmt_cents(row.get('near_miss_net_cents'))}`, "
                f"saved losses `{row.get('healthy_abstentions')}`, "
                f"missed profits `{row.get('coverage_mistakes')}`, "
                f"negative-edge winners `{row.get('profitable_negative_edge_misses')}`"
            )
    raw_physics = entry_watch.get("raw_physics_summary") or {}
    raw_physics_rows = raw_physics.get("ranked") or []
    if raw_physics_rows:
        lines.extend([
            "",
            "### Raw Physics Penalty Candidates",
            "",
            "- Discovery-only physics penalties around raw v28; frozen challengers below must earn forward rows.",
        ])
        for row in raw_physics_rows[:6]:
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"coverage `{row.get('coverage_pct')}`, net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, "
                f"brier `{row.get('avg_brier')}`, actual/sim `{row.get('approved_entry_count')}/{row.get('added_reject_count')}`"
            )
    noise_shrinkage = entry_watch.get("noise_shrinkage_summary") or {}
    noise_rows = noise_shrinkage.get("ranked") or []
    if noise_rows:
        lines.extend([
            "",
            "### Noise-Floor Shrinkage Candidates",
            "",
            "- Discovery-only FV candidates that shrink raw v28 toward 50 in noisy physical states instead of flipping sides.",
        ])
        for row in noise_rows[:6]:
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"coverage `{row.get('coverage_pct')}`, net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, "
                f"brier `{row.get('avg_brier')}`, actual/sim `{row.get('approved_entry_count')}/{row.get('added_reject_count')}`"
            )
    raw_entry_calibrated = entry_watch.get("raw_entry_calibrated_summary") or {}
    calibrated_rows = raw_entry_calibrated.get("ranked") or []
    if calibrated_rows:
        lines.extend([
            "",
            "### Raw Entry Calibrated Probability",
            "",
            "- Keeps raw v28 p50 entry selection fixed and compares probability overlays on the same selected rows.",
        ])
        for row in calibrated_rows[:6]:
            lines.append(
                f"- `{row.get('overlay')}`: count `{row.get('count')}`, "
                f"brier `{row.get('avg_brier')}` delta `{row.get('brier_delta_vs_raw')}`, "
                f"logloss `{row.get('avg_logloss')}` delta `{row.get('logloss_delta_vs_raw')}`, "
                f"ece `{row.get('ece_10bucket')}` delta `{row.get('ece_delta_vs_raw')}`, "
                f"net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`"
            )
    profit_bridge = entry_watch.get("probability_profit_bridge_summary") or {}
    if profit_bridge:
        overall = profit_bridge.get("overall") or {}
        lines.extend([
            "",
            "### Probability Profit Bridge",
            "",
            "- Compares settlement calibration with realized exit P&L and hold-to-settlement P&L.",
            f"- Rows/settled: `{profit_bridge.get('rows')}/{profit_bridge.get('settled')}`",
            f"- Overall actual/hold/exit value: `{fmt_cents(overall.get('actual_gross_cents'))}/{fmt_cents(overall.get('hold_gross_cents'))}/{fmt_cents(overall.get('exit_value_cents'))}`",
        ])
        for note in profit_bridge.get("interpretation") or []:
            lines.append(f"- {note}")
        for row in (profit_bridge.get("by_raw_book_gap") or []):
            lines.append(
                f"- gap `{row.get('bucket')}`: settled `{row.get('settled')}`, W/L `{row.get('wins')}/{row.get('losses')}`, "
                f"actual/hold/exit `{fmt_cents(row.get('actual_gross_cents'))}/{fmt_cents(row.get('hold_gross_cents'))}/{fmt_cents(row.get('exit_value_cents'))}`"
            )
        for row in (profit_bridge.get("by_reentry") or []):
            lines.append(
                f"- reentry `{row.get('bucket')}`: settled `{row.get('settled')}`, W/L `{row.get('wins')}/{row.get('losses')}`, "
                f"actual/hold `{fmt_cents(row.get('actual_gross_cents'))}/{fmt_cents(row.get('hold_gross_cents'))}`"
            )
    approved_fv = entry_watch.get("approved_entry_fv_overlay_summary") or {}
    if approved_fv:
        lines.extend([
            "",
            "### Approved-Entry FV Overlay Validator",
            "",
            "- FV overlay calibration on actual v28-approved entries only.",
            f"- Rows/settled: `{approved_fv.get('rows')}/{approved_fv.get('settled')}`",
            f"- Best overlay: `{approved_fv.get('best_overlay')}`",
        ])
        for note in approved_fv.get("interpretation") or []:
            lines.append(f"- {note}")
        for row in (approved_fv.get("ranked") or [])[:5]:
            lines.append(
                f"- `{row.get('overlay')}`: settled `{row.get('settled')}`, W/L `{row.get('wins')}-{row.get('losses')}`, "
                f"avg p `{row.get('avg_p')}`, brier d `{row.get('brier_delta_vs_raw')}`, "
                f"logloss d `{row.get('logloss_delta_vs_raw')}`"
            )
    book_actionability = entry_watch.get("approved_entry_book_edge_actionability_summary") or {}
    if book_actionability:
        useful = book_actionability.get("useful") or []
        best = useful[0] if useful else {}
        retained = best.get("retained") or {}
        skipped = best.get("skipped") or {}
        lines.extend([
            "",
            "### Approved-Entry Book-Edge Actionability",
            "",
            "- Tests whether book-vs-raw disagreement changes actual v28-approved entry decisions without relying on rejected-actionable rows.",
            f"- Future actual-approved entries: `{book_actionability.get('future_entries')}`",
            f"- Useful policies: `{len(useful)}`",
        ])
        if best:
            lines.append(
                f"- Best useful policy `{best.get('policy')}` keeps coverage `{retained.get('coverage_pct')}`, "
                f"net `{fmt_cents(retained.get('net_cents'))}`, delta `{fmt_cents(best.get('delta_net_vs_keep_all_cents'))}`, "
                f"skipped W/L/net `{skipped.get('wins')}/{skipped.get('losses')}/{fmt_cents(skipped.get('net_cents'))}`"
            )
        for note in book_actionability.get("interpretation") or []:
            lines.append(f"- {note}")
    frozen_book_gate = entry_watch.get("frozen_approved_entry_book_edge_gate_summary") or {}
    if frozen_book_gate:
        candidate = frozen_book_gate.get("candidate") or {}
        skipped = frozen_book_gate.get("skipped") or {}
        lines.extend([
            "",
            "### Frozen Approved-Entry Book-Edge Gate",
            "",
            "- Future-only validator for the fixed book-edge skip rule; earlier actionability rows are discovery only.",
            f"- Freeze timestamp UTC: `{(frozen_book_gate.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Future entries/retained settled/coverage: `{frozen_book_gate.get('future_entries')}/{candidate.get('settled')}/{candidate.get('coverage_pct')}`",
            f"- Retained net/delta: `{fmt_cents(candidate.get('net_cents'))}/{fmt_cents(frozen_book_gate.get('delta_net_vs_control_cents'))}`",
            f"- Skipped W/L/net: `{skipped.get('wins')}/{skipped.get('losses')}/{fmt_cents(skipped.get('net_cents'))}`",
            f"- Blockers: `{', '.join(frozen_book_gate.get('blockers') or []) or 'none'}`",
        ])
    posterior_diag = entry_watch.get("entry_posterior_diagnostic_summary") or {}
    posterior_rows = posterior_diag.get("summary") or []
    if posterior_rows:
        lines.extend([
            "",
            "### Entry-Conditioned Posterior Diagnostic",
            "",
            "- Checks whether the +5pp posterior lift survives across physical buckets on the fixed raw p50 entry slice.",
        ])
        for row in posterior_rows:
            if row.get("settled", 0) >= 5 or row.get("bucket") in {"all", "early_markets", "late_markets"}:
                plus05 = row.get("plus05") or {}
                best = row.get("best_overlay") or {}
                lines.append(
                    f"- `{row.get('bucket')}`: settled `{row.get('settled')}`, W/L `{row.get('wins')}/{row.get('losses')}`, "
                    f"best `{best.get('overlay')}`, best brier `{best.get('avg_brier')}`, "
                f"plus05 delta `{plus05.get('brier_delta_vs_raw')}`"
            )
    source_aware = entry_watch.get("source_aware_fv_overlay_summary") or {}
    if source_aware:
        lines.extend([
            "",
            "### Source-Aware FV Overlay Validator",
            "",
            "- Tests approved-entry book anchoring plus target-coverage strong-row sharpening as one FV overlay.",
            f"- Rows/settled: `{source_aware.get('rows')}/{source_aware.get('settled')}`",
            f"- Approved/rejected settled: `{source_aware.get('approved_settled')}/{source_aware.get('simulated_settled')}`",
            f"- Simulated share: `{fmt_pct(source_aware.get('simulated_share'))}`",
            f"- Best overlay: `{source_aware.get('best_overlay')}`",
            f"- Evidence blockers: `{', '.join(source_aware.get('evidence_blockers') or []) or 'none'}`",
        ])
        for note in source_aware.get("interpretation") or []:
            lines.append(f"- {note}")
        for row in (source_aware.get("ranked") or [])[:4]:
            lines.append(
                f"- `{row.get('overlay')}`: Brier/logloss d "
                f"`{row.get('brier_delta_vs_raw')}/{row.get('logloss_delta_vs_raw')}`, "
                f"cal err `{row.get('calibration_error')}`"
            )
    source_robustness = entry_watch.get("source_aware_fv_robustness_audit_summary") or {}
    if source_robustness:
        lines.extend([
            "",
            "### Source-Aware FV Robustness Audit",
            "",
            "- Perturbs the candidate by removing each market and checking source slices.",
            f"- Full Brier/logloss delta: `{source_robustness.get('full_brier_delta_vs_raw')}/{source_robustness.get('full_logloss_delta_vs_raw')}`",
            f"- Leave-one-market failures: `{source_robustness.get('leave_one_market_failures')}`",
            f"- Dominant market Brier-delta share: `{fmt_pct(source_robustness.get('dominant_market_brier_delta_share'))}`",
            f"- Blockers: `{', '.join(source_robustness.get('blockers') or []) or 'none'}`",
        ])
        for row in (source_robustness.get("source_slices") or [])[:3]:
            lines.append(
                f"- source `{row.get('source')}`: settled `{row.get('settled')}`, "
                f"best `{row.get('best_overlay')}`, source-aware rank `{row.get('expected_rank')}`, "
                f"d brier/logloss `{row.get('expected_brier_delta_vs_raw')}/{row.get('expected_logloss_delta_vs_raw')}`"
            )
        for row in (source_robustness.get("top_market_contributions") or [])[:3]:
            lines.append(
                f"- top market contribution `{row.get('market')}`: contribution `{row.get('brier_delta_contribution')}`, "
                f"kept d brier `{row.get('kept_brier_delta_vs_raw')}`"
            )
    source_audit = entry_watch.get("source_aware_fv_promotion_audit_summary") or {}
    if source_audit:
        c = source_audit.get("candidate") or {}
        lines.extend([
            "",
            "### Source-Aware FV Promotion Audit",
            "",
            f"- Ready for implementation planning: `{source_audit.get('ready_for_implementation_planning')}`",
            f"- Overlay: `{c.get('overlay')}`",
            f"- Settled/approved/simulated/share: `{c.get('settled')}/{c.get('approved_settled')}/{c.get('simulated_settled')}/{fmt_pct(c.get('simulated_share'))}`",
            f"- Brier/logloss delta: `{c.get('brier_delta_vs_raw')}/{c.get('logloss_delta_vs_raw')}`",
            f"- Robustness blockers: `{', '.join(c.get('robustness_blockers') or []) or 'none'}`",
        ])
        for item in source_audit.get("checks") or []:
            if item.get("passed") is not True:
                lines.append(
                    f"- blocker `{item.get('name')}`: actual `{item.get('actual')}`, required `{item.get('required')}`"
                )
    state_valves = entry_watch.get("approved_entry_state_valves_summary") or {}
    if state_valves:
        lines.extend([
            "",
            "### Approved-Entry State Valves",
            "",
            "- Actual-only diagnostic for same-market reentry and raw/book disagreement.",
            f"- Rows/markets: `{state_valves.get('total_rows')}/{state_valves.get('markets')}`",
            f"- Best policy: `{state_valves.get('best_policy')}`",
        ])
        for note in state_valves.get("interpretation") or []:
            lines.append(f"- {note}")
        for row in (state_valves.get("ranked") or [])[:5]:
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, W/L `{row.get('wins')}/{row.get('losses')}`, "
                f"coverage `{fmt_pct((row.get('market_coverage_pct') or 0) / 100 if row.get('market_coverage_pct') is not None else None)}`, "
                f"gross/delta `{fmt_cents(row.get('gross_cents'))}/{fmt_cents(row.get('delta_vs_current_cents'))}`, "
                f"skipped gross `{fmt_cents(row.get('skipped_gross_cents'))}`"
            )
    frozen_state_valve = entry_watch.get("frozen_approved_entry_state_valve_summary") or {}
    if frozen_state_valve:
        c = frozen_state_valve.get("candidate") or {}
        control = frozen_state_valve.get("control") or {}
        lines.extend([
            "",
            "### Frozen Approved-Entry State Valve",
            "",
            "- Forward-only validator for the fixed same-side reentry gap valve.",
            f"- Freeze timestamp UTC: `{(frozen_state_valve.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Candidate entries/W-L/gross: `{c.get('entries')}/{c.get('wins')}-{c.get('losses')}/{fmt_cents(c.get('gross_cents'))}`",
            f"- Control entries/W-L/gross: `{control.get('entries')}/{control.get('wins')}-{control.get('losses')}/{fmt_cents(control.get('gross_cents'))}`",
            f"- Delta/coverage/skipped: `{fmt_cents(c.get('delta_vs_control_cents'))}/{fmt_pct((c.get('market_coverage_pct') or 0) / 100 if c.get('market_coverage_pct') is not None else None)}/{c.get('skipped_entries')}`",
            f"- Blockers: `{', '.join(frozen_state_valve.get('blockers') or []) or 'none'}`",
        ])
    danger_valve = entry_watch.get("danger_zone_entry_valve_summary") or {}
    if danger_valve:
        lines.extend([
            "",
            "### Danger-Zone Entry Valve",
            "",
            "- Actual-only diagnostic for raw/book overconfidence and repeated same-side entries.",
            f"- Rows/markets: `{danger_valve.get('rows')}/{danger_valve.get('markets')}`",
            f"- Best policy: `{danger_valve.get('best_policy')}`",
        ])
        for note in danger_valve.get("interpretation") or []:
            lines.append(f"- {note}")
        for row in (danger_valve.get("ranked") or [])[:5]:
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, W/L `{row.get('wins')}/{row.get('losses')}`, "
                f"coverage `{fmt_pct((row.get('market_coverage_pct') or 0) / 100 if row.get('market_coverage_pct') is not None else None)}`, "
                f"gross/delta `{fmt_cents(row.get('gross_cents'))}/{fmt_cents(row.get('delta_vs_current_cents'))}`, "
                f"skipped gross `{fmt_cents(row.get('skipped_gross_cents'))}`"
            )
    frozen_danger_valve = entry_watch.get("frozen_danger_zone_entry_valve_summary") or {}
    if frozen_danger_valve:
        c = frozen_danger_valve.get("candidate") or {}
        control = frozen_danger_valve.get("control") or {}
        lines.extend([
            "",
            "### Frozen Danger-Zone Entry Valve",
            "",
            "- Forward-only validator for the fixed skip_reentry_gap15_or_gap30 rule.",
            f"- Freeze timestamp UTC: `{(frozen_danger_valve.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Candidate entries/W-L/gross: `{c.get('entries')}/{c.get('wins')}-{c.get('losses')}/{fmt_cents(c.get('gross_cents'))}`",
            f"- Control entries/W-L/gross: `{control.get('entries')}/{control.get('wins')}-{control.get('losses')}/{fmt_cents(control.get('gross_cents'))}`",
            f"- Delta/coverage/skipped: `{fmt_cents(c.get('delta_vs_control_cents'))}/{fmt_pct((c.get('market_coverage_pct') or 0) / 100 if c.get('market_coverage_pct') is not None else None)}/{c.get('skipped_entries')}`",
            f"- Blockers: `{', '.join(frozen_danger_valve.get('blockers') or []) or 'none'}`",
        ])
    danger_fv = entry_watch.get("danger_zone_fv_calibration_summary") or {}
    if danger_fv:
        lines.extend([
            "",
            "### Danger-Zone FV Calibration",
            "",
            "- Tests whether raw/book overconfidence is a probability error, not only an entry P&L problem.",
            f"- Rows/markets: `{danger_fv.get('rows')}/{danger_fv.get('markets')}`",
            f"- Best overlay: `{danger_fv.get('best_overlay')}`",
        ])
        for note in danger_fv.get("interpretation") or []:
            lines.append(f"- {note}")
        for row in (danger_fv.get("ranked") or [])[:5]:
            lines.append(
                f"- `{row.get('overlay')}`: rows `{row.get('settled')}`, W/L `{row.get('wins')}/{row.get('losses')}`, "
                f"avg p/win `{row.get('avg_p')}/{row.get('win_rate')}`, "
                f"d brier/logloss `{row.get('brier_delta_vs_raw')}/{row.get('logloss_delta_vs_raw')}`"
            )
    frozen_danger_fv = entry_watch.get("frozen_danger_zone_fv_calibration_summary") or {}
    if frozen_danger_fv:
        lines.extend([
            "",
            "### Frozen Danger-Zone FV Calibration",
            "",
            "- Forward-only validator for fixed raw/book/danger_to_book probability overlays.",
            f"- Freeze timestamp UTC: `{(frozen_danger_fv.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Future rows/markets/danger rows: `{frozen_danger_fv.get('future_rows')}/{frozen_danger_fv.get('future_markets')}/{frozen_danger_fv.get('danger_rows')}`",
            f"- Best overlay: `{frozen_danger_fv.get('best_overlay')}`",
        ])
        for row in (frozen_danger_fv.get("ranked") or [])[:3]:
            lines.append(
                f"- `{row.get('overlay')}`: rows `{row.get('rows')}`, "
                f"d brier/logloss `{row.get('brier_delta_vs_raw')}/{row.get('logloss_delta_vs_raw')}`, "
                f"blockers `{', '.join(row.get('blockers') or []) or 'none'}`"
            )
    danger_robustness = entry_watch.get("danger_zone_robustness_audit_summary") or {}
    if danger_robustness:
        entry = danger_robustness.get("full_entry") or {}
        fv = danger_robustness.get("full_fv") or {}
        lines.extend([
            "",
            "### Danger-Zone Robustness Audit",
            "",
            "- Leave-one-market-out check for the danger-zone entry valve and danger-to-book FV overlay.",
            f"- Entry robustness pass: `{danger_robustness.get('pass_entry_robustness')}`",
            f"- FV robustness pass: `{danger_robustness.get('pass_fv_robustness')}`",
            f"- Entry full-sample delta: `{fmt_cents(entry.get('delta_cents'))}`",
            f"- FV Brier/logloss delta: `{fv.get('brier_delta_vs_raw')}/{fv.get('logloss_delta_vs_raw')}`",
            f"- Leave-one failures entry/FV: `{danger_robustness.get('entry_leave_one_failures')}/{danger_robustness.get('fv_leave_one_failures')}`",
        ])
        for row in (danger_robustness.get("leave_one") or [])[:3]:
            lines.append(
                f"- remove `{row.get('removed_market')}`: entry delta `{fmt_cents(row.get('entry_delta_cents'))}`, "
                f"FV d brier/logloss `{row.get('fv_brier_delta_vs_raw')}/{row.get('fv_logloss_delta_vs_raw')}`"
            )
    book_traj = entry_watch.get("book_trajectory_fv_summary") or {}
    if book_traj:
        lines.extend([
            "",
            "### Book-Disagreement Trajectory FV",
            "",
            "- Tests whether raw FV should shrink toward book when book rejects the same-side thesis.",
            f"- Rows/markets/market-sides: `{book_traj.get('rows')}/{book_traj.get('markets')}/{book_traj.get('market_sides')}`",
        ])
        for note in book_traj.get("interpretation") or []:
            lines.append(f"- {note}")
        for view in (book_traj.get("views") or [])[:3]:
            ranked = view.get("ranked") or []
            best = ranked[0] if ranked else {}
            cand = next((row for row in ranked if row.get("variant") == "gap15_or_drawdown10"), {})
            lines.append(
                f"- view `{view.get('view')}`: best `{best.get('variant')}` d brier/logloss "
                f"`{best.get('brier_delta_vs_raw')}/{best.get('logloss_delta_vs_raw')}`; "
                f"candidate d `{cand.get('brier_delta_vs_raw')}/{cand.get('logloss_delta_vs_raw')}`"
            )
    frozen_book_traj = entry_watch.get("frozen_book_trajectory_fv_summary") or {}
    if frozen_book_traj:
        lines.extend([
            "",
            "### Frozen Book-Trajectory FV",
            "",
            "- Forward-only validator for fixed gap15_or_drawdown10 FV shrinkage.",
            f"- Freeze timestamp UTC: `{(frozen_book_traj.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Future rows/markets/market-sides: `{frozen_book_traj.get('future_rows')}/{frozen_book_traj.get('future_markets')}/{frozen_book_traj.get('future_market_sides')}`",
        ])
        for view in frozen_book_traj.get("views") or []:
            c = view.get("candidate") or {}
            lines.append(
                f"- view `{view.get('view')}`: rows `{c.get('rows')}`, d brier/logloss "
                f"`{c.get('brier_delta_vs_raw')}/{c.get('logloss_delta_vs_raw')}`, "
                f"blockers `{', '.join(view.get('blockers') or []) or 'none'}`"
            )
    book_traj_entry = entry_watch.get("book_trajectory_entry_projection_summary") or {}
    if book_traj_entry:
        lines.extend([
            "",
            "### Book-Trajectory Entry Projection",
            "",
            "- Discovery-only test of whether trajectory-adjusted FV creates broad entry economics.",
            f"- Denominator markets: `{book_traj_entry.get('denominator_markets')}`",
        ])
        for note in book_traj_entry.get("interpretation") or []:
            lines.append(f"- {note}")
        for row in (book_traj_entry.get("ranked") or [])[:6]:
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, W/L `{row.get('wins')}/{row.get('losses')}`, "
                f"coverage `{fmt_pct((row.get('coverage_pct') or 0) / 100 if row.get('coverage_pct') is not None else None)}`, "
                f"gross `{fmt_cents(row.get('gross_cents'))}`, avg edge `{row.get('avg_edge')}`"
            )
    frozen_pending = entry_watch.get("frozen_pending_monitor_summary") or {}
    if frozen_pending:
        lines.extend([
            "",
            "### Frozen Pending Monitor",
            "",
            "- Shows unresolved post-freeze rows that will affect frozen validators after settlement.",
            f"- Pending state-valve/book-trajectory rows: `{frozen_pending.get('pending_state_valve_count')}/{frozen_pending.get('pending_book_trajectory_count')}`",
        ])
        for row in (frozen_pending.get("pending_state_valve_rows") or [])[:5]:
            lines.append(
                f"- state pending `{row.get('market')}` `{row.get('side')}`: p/ask/gap "
                f"`{row.get('p_side')}/{row.get('ask_cents')}/{row.get('raw_book_gap')}`, keep `{row.get('state_valve_keep')}`"
            )
        pending_book = frozen_pending.get("pending_book_trajectory_rows") or []
        changed = [row for row in pending_book if row.get("candidate_p") != row.get("raw_p")]
        lines.append(f"- book-trajectory pending adjusted rows in displayed tail: `{len(changed)}`")
    frozen_scorecard = entry_watch.get("frozen_forward_scorecard_summary") or {}
    if frozen_scorecard:
        state = frozen_scorecard.get("state_valve") or {}
        book = frozen_scorecard.get("book_trajectory_fv") or {}
        all_obs = book.get("all_observations") or {}
        control = frozen_scorecard.get("control") or {}
        lines.extend([
            "",
            "### Frozen Forward Scorecard",
            "",
            "- Unified post-freeze scorecard for frozen state/FV candidates.",
        ])
        for note in frozen_scorecard.get("interpretation") or []:
            lines.append(f"- {note}")
        lines.extend([
            f"- State settled/gross/delta: `{state.get('settled')}/{fmt_cents(state.get('gross_cents'))}/{fmt_cents(state.get('delta_vs_control_cents'))}`",
            f"- Book trajectory all-observation rows and Brier/logloss delta: `{all_obs.get('rows')}/{all_obs.get('brier_delta_vs_raw')}/{all_obs.get('logloss_delta_vs_raw')}`",
            f"- Control gross/hold/exit value: `{fmt_cents(control.get('gross_cents'))}/{fmt_cents(control.get('hold_gross_cents'))}/{fmt_cents(control.get('exit_value_cents'))}`",
        ])
    lift_plateau = entry_watch.get("entry_lift_plateau_summary") or {}
    if lift_plateau.get("by_lift"):
        ranked_lifts = lift_plateau.get("ranked") or []
        improving = lift_plateau.get("improving_lift_pp") or []
        lines.extend([
            "",
            "### Entry-Conditioned Lift Plateau",
            "",
            "- Tests whether the posterior lift is broad or point-fit. +5pp remains the frozen conservative challenger.",
            f"- Best discovery lift: `{lift_plateau.get('best_lift_pp')}pp`",
            f"- Improving lift values: `{improving}`",
        ])
        for row in ranked_lifts[:5]:
            lines.append(
                f"- lift `{row.get('lift_pp')}pp`: brier `{row.get('avg_brier')}`, "
                f"delta `{row.get('brier_delta_vs_raw')}`, logloss delta `{row.get('logloss_delta_vs_raw')}`, "
                f"avg p `{row.get('avg_p')}`"
            )
    jackknife = entry_watch.get("entry_jackknife_summary") or {}
    if jackknife:
        full = jackknife.get("full_sample") or {}
        lines.extend([
            "",
            "### Entry-Conditioned Jackknife",
            "",
            "- Removes one market at a time and checks whether +5pp still improves calibration versus raw.",
            f"- Jackknife pass: `{jackknife.get('jackknife_pass')}`",
            f"- Failure count: `{jackknife.get('failure_count')}`",
            f"- Full-sample Brier/logloss deltas: `{full.get('brier_delta_vs_raw')}/{full.get('logloss_delta_vs_raw')}`",
        ])
        for row in (jackknife.get("worst_removals") or [])[:3]:
            lines.append(
                f"- worst removal `{row.get('removed_market')}`: kept count `{row.get('count')}`, "
                f"brier delta `{row.get('brier_delta_vs_raw')}`, logloss delta `{row.get('logloss_delta_vs_raw')}`"
            )
    data_quality = entry_watch.get("entry_data_quality_summary") or {}
    if data_quality:
        lines.extend([
            "",
            "### Entry-Conditioned Data Quality",
            "",
            "- Causality and row-quality audit for the raw p50 fixed entry slice.",
            f"- Data-quality pass: `{data_quality.get('data_quality_pass')}`",
            f"- Selected/unique/settled: `{data_quality.get('selected_entries')}/{data_quality.get('unique_markets')}/{data_quality.get('settled_entries')}`",
            f"- Approved/shadow rows: `{data_quality.get('approved_entries')}/{data_quality.get('shadow_rejected_actionable')}`",
            f"- Flag counts: `{data_quality.get('flag_counts')}`",
        ])
    raw_p52_delta = entry_watch.get("raw_p52_delta_summary") or {}
    p52_summary = raw_p52_delta.get("summary") or {}
    if p52_summary:
        skipped = p52_summary.get("skipped_by_p52") or {}
        base_kept = p52_summary.get("base_rows_kept_by_p52") or {}
        actual_p52 = p52_summary.get("actual_p52_rows") or {}
        lines.extend([
            "",
            "### Raw p52 Delta Diagnostic",
            "",
            "- Explains what raw p52 removes from raw p50 without treating the discovery slice as promotion evidence.",
            f"- Base rows kept by p52: count `{base_kept.get('count')}`, settled `{base_kept.get('settled')}`, "
            f"net `{fmt_cents(base_kept.get('net_cents_after_fee'))}`, brier `{base_kept.get('avg_brier')}`",
            f"- Actual p52 rows: count `{actual_p52.get('count')}`, settled `{actual_p52.get('settled')}`, "
            f"net `{fmt_cents(actual_p52.get('net_cents_after_fee'))}`, brier `{actual_p52.get('avg_brier')}`",
            f"- Skipped by p52: count `{skipped.get('count')}`, settled `{skipped.get('settled')}`, "
            f"net `{fmt_cents(skipped.get('net_cents_after_fee'))}`, brier `{skipped.get('avg_brier')}`",
            f"- Changed p52 selections among kept markets: `{p52_summary.get('changed_selection_count')}`",
            f"- Changed-selection net delta: `{fmt_cents(p52_summary.get('changed_selection_net_delta_cents'))}`",
        ])
        tag_rows = raw_p52_delta.get("skipped_tag_summary") or []
        if tag_rows:
            lines.append("- Skipped-row tags:")
            for row in tag_rows:
                if row.get("count"):
                    lines.append(
                        f"  - `{row.get('tag')}`: count `{row.get('count')}`, "
                        f"net `{fmt_cents(row.get('net_cents_after_fee'))}`, brier `{row.get('avg_brier')}`"
                    )
    raw_p52_confirmation = entry_watch.get("raw_p52_confirmation_summary") or {}
    confirm_summary = raw_p52_confirmation.get("summary") or {}
    if confirm_summary:
        lines.extend([
            "",
            "### Raw p52 Confirmation Path",
            "",
            "- Separates p52 waiting behavior into side flips, same-side confirmation, and pay-up paths.",
            f"- Changed paths: `{confirm_summary.get('count')}`, resolved `{confirm_summary.get('resolved')}`, "
            f"confirm-base net `{fmt_cents(confirm_summary.get('confirm_minus_base_net_cents'))}`, "
            f"avg delay `{confirm_summary.get('avg_delay_seconds')}` seconds",
            f"- Avg Brier base/confirm: `{confirm_summary.get('avg_base_brier')}/{confirm_summary.get('avg_confirm_brier')}`",
        ])
        for row in raw_p52_confirmation.get("by_path_type") or []:
            lines.append(
                f"- `{row.get('path_type')}`: count `{row.get('count')}`, "
                f"base net `{fmt_cents(row.get('base_net_cents'))}`, "
                f"confirm net `{fmt_cents(row.get('confirm_net_cents'))}`, "
                f"delta `{fmt_cents(row.get('confirm_minus_base_net_cents'))}`"
            )
    frozen_raw_physics = entry_watch.get("frozen_raw_physics_summary") or {}
    if frozen_raw_physics:
        lines.extend([
            "",
            "### Frozen Raw Physics Challengers",
            "",
            f"- Freeze timestamp UTC: `{frozen_raw_physics.get('freeze_ts')}`",
            f"- Forward market denominator: `{frozen_raw_physics.get('forward_market_denominator')}`",
            f"- Future candidate rows: `{frozen_raw_physics.get('future_candidate_rows')}`",
        ])
        for row in frozen_raw_physics.get("summary") or []:
            fv_checks = row.get("fv_validation_checks") or {}
            exec_checks = row.get("execution_promotion_checks") or {}
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"coverage `{row.get('coverage_pct')}`, net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, "
                f"brier `{row.get('avg_brier')}`, "
                f"fv blockers `{', '.join(fv_checks.get('blockers') or []) or 'none'}`, "
                f"execution blockers `{', '.join(exec_checks.get('blockers') or []) or 'none'}`"
            )
    raw_p52_sideflip = entry_watch.get("raw_p52_sideflip_summary") or {}
    if raw_p52_sideflip.get("summary"):
        lines.extend([
            "",
            "### Raw p52 Side-Flip Candidate",
            "",
            "- Discovery-only candidate: raw p50 entries, except use p52 when it confirms the opposite side.",
        ])
        for row in raw_p52_sideflip.get("summary") or []:
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"coverage `{row.get('coverage_pct')}`, net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, "
                f"brier `{row.get('avg_brier')}`, modes base/sideflip `{row.get('base_raw_count')}/{row.get('sideflip_confirm_count')}`"
            )
    frozen_sideflip = entry_watch.get("frozen_raw_p52_sideflip_summary") or {}
    if frozen_sideflip:
        lines.extend([
            "",
            "### Frozen Raw p52 Side-Flip Challenger",
            "",
            f"- Freeze timestamp UTC: `{frozen_sideflip.get('freeze_ts')}`",
            f"- Forward market denominator: `{frozen_sideflip.get('forward_market_denominator')}`",
            f"- Future candidate rows: `{frozen_sideflip.get('future_candidate_rows')}`",
        ])
        for row in frozen_sideflip.get("summary") or []:
            fv_checks = row.get("fv_validation_checks") or {}
            exec_checks = row.get("execution_promotion_checks") or {}
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"coverage `{row.get('coverage_pct')}`, net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, "
                f"brier `{row.get('avg_brier')}`, modes base/sideflip `{row.get('base_raw_count')}/{row.get('sideflip_confirm_count')}`, "
                f"fv blockers `{', '.join(fv_checks.get('blockers') or []) or 'none'}`, "
                f"execution blockers `{', '.join(exec_checks.get('blockers') or []) or 'none'}`"
            )
    recross_escape = entry_watch.get("raw_p52_recross_escape_summary") or {}
    recross_rows = recross_escape.get("summaries") or []
    if recross_rows:
        lines.extend([
            "",
            "### Raw p52 Recross-Escape Candidate",
            "",
            "- Discovery-only candidate: keeps broad raw p52, but weak near-strike/high-recross rows may follow a later opposite p52 confirmation with >=5pp edge.",
        ])
        for row in recross_rows[:5]:
            boot = row.get("bootstrap") or {}
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"coverage `{row.get('coverage_pct')}`, net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, "
                f"brier `{row.get('avg_brier')}`, modes `{row.get('mode_counts')}`, "
                f"boot p10/p>0 `{fmt_cents(boot.get('net_p10'))}/{boot.get('prob_positive')}`"
            )
    frozen_recross = entry_watch.get("frozen_raw_p52_recross_escape_summary") or {}
    if frozen_recross:
        lines.extend([
            "",
            "### Frozen Raw p52 Recross-Escape Challenger",
            "",
            f"- Freeze timestamp UTC: `{frozen_recross.get('freeze_ts')}`",
            f"- Forward market denominator: `{frozen_recross.get('forward_market_denominator')}`",
            f"- Future candidate rows: `{frozen_recross.get('future_candidate_rows')}`",
        ])
        for row in frozen_recross.get("summary") or []:
            fv_checks = row.get("fv_validation_checks") or {}
            exec_checks = row.get("execution_promotion_checks") or {}
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"coverage `{row.get('coverage_pct')}`, net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, "
                f"brier `{row.get('avg_brier')}`, modes `{row.get('mode_counts')}`, "
                f"fv blockers `{', '.join(fv_checks.get('blockers') or []) or 'none'}`, "
                f"execution blockers `{', '.join(exec_checks.get('blockers') or []) or 'none'}`"
            )
    recross_probability = entry_watch.get("recross_escape_probability_summary") or {}
    recross_probability_rows = recross_probability.get("summaries") or []
    if recross_probability_rows:
        lines.extend([
            "",
            "### Recross-Escape Probability Calibration",
            "",
            "- Discovery-only fixed-row FV calibration for the recross-escape selector; P&L is unchanged.",
            f"- Policy: `{recross_probability.get('policy')}`, entries/settled `{recross_probability.get('entries')}/{recross_probability.get('settled')}`",
        ])
        for row in recross_probability_rows[:5]:
            lines.append(
                f"- `{row.get('probability')}`: Brier `{row.get('avg_brier')}` "
                f"delta `{row.get('brier_delta_vs_raw')}`, logloss `{row.get('avg_logloss')}` "
                f"delta `{row.get('logloss_delta_vs_raw')}`, ECE `{row.get('ece')}`"
            )
        plateau = recross_probability.get("lift_plateau") or {}
        jackknife = recross_probability.get("plus05_jackknife") or {}
        if plateau:
            lines.append(
                f"- Lift plateau: best lift `{plateau.get('best_lift')}`, "
                f"improving lifts `{plateau.get('improving_lifts')}`"
            )
        if jackknife:
            lines.append(
                f"- +5pp jackknife: Brier improved `{jackknife.get('brier_improved_slices')}/{jackknife.get('slice_count')}` slices, "
                f"logloss improved `{jackknife.get('logloss_improved_slices')}/{jackknife.get('slice_count')}`, "
                f"worst Brier delta `{jackknife.get('worst_brier_delta')}`"
            )
    frozen_recross_attribution = entry_watch.get("frozen_recross_escape_attribution_summary") or {}
    if frozen_recross_attribution:
        challenger = frozen_recross_attribution.get("challenger") or {}
        baseline = frozen_recross_attribution.get("baseline") or {}
        overlays = frozen_recross_attribution.get("probability_overlays") or []
        tags = frozen_recross_attribution.get("tagged_raw_probability") or []
        lines.extend([
            "",
            "### Frozen Recross-Escape Attribution",
            "",
            "- Forward-only physical attribution for the recross-escape challenger.",
            f"- Freeze timestamp UTC: `{frozen_recross_attribution.get('source_freeze_ts')}`",
            f"- Baseline entries/settled/W-L/net: `{baseline.get('entries')}/{baseline.get('settled')}/{baseline.get('wins')}-{baseline.get('losses')}/{fmt_cents(baseline.get('net_cents'))}`",
            f"- Challenger entries/settled/W-L/net: `{challenger.get('entries')}/{challenger.get('settled')}/{challenger.get('wins')}-{challenger.get('losses')}/{fmt_cents(challenger.get('net_cents'))}`",
        ])
        settled_overlays = [row for row in overlays if row.get("avg_brier") is not None]
        if settled_overlays:
            best = min(
                settled_overlays,
                key=lambda row: float(row.get("avg_brier")),
            )
            lines.append(
                f"- Best settled FV overlay so far: `{best.get('probability')}` "
                f"Brier `{best.get('avg_brier')}`, logloss `{best.get('avg_logloss')}`"
            )
        else:
            lines.append("- Best settled FV overlay so far: `none yet`")
        for row in tags[:8]:
            lines.append(
                f"- `{row.get('tag')}`: entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"W/L `{row.get('wins')}/{row.get('losses')}`, net `{fmt_cents(row.get('net_cents'))}`, "
                f"Brier `{row.get('avg_brier')}`"
            )
    recross_sample_plan = entry_watch.get("recross_escape_sample_plan_summary") or {}
    if recross_sample_plan:
        runway = recross_sample_plan.get("runway") or {}
        blockers = recross_sample_plan.get("blockers") or {}
        lines.extend([
            "",
            "### Recross-Escape Sample Plan",
            "",
            f"- Candidate: `{recross_sample_plan.get('candidate')}`",
            f"- Freeze timestamp UTC: `{recross_sample_plan.get('freeze_ts')}`",
            f"- Forward denominator: `{recross_sample_plan.get('forward_denominator')}`, excluded in-progress `{recross_sample_plan.get('excluded_in_progress_count')}`",
            f"- Settled rows to 30: `{runway.get('settled_rows_to_30')}`, pending `{runway.get('pending_rows')}`, additional after pending `{runway.get('additional_settled_after_pending_to_30')}`",
            f"- Actual entries needed for simulated share <=35%: `{runway.get('actual_entries_needed_for_sim_share_lte_35pct')}`",
            f"- FV blockers: `{', '.join(blockers.get('fv') or []) or 'none'}`",
            f"- Execution blockers: `{', '.join(blockers.get('execution') or []) or 'none'}`",
        ])
    frozen_noise = entry_watch.get("frozen_noise_shrinkage_summary") or {}
    if frozen_noise:
        lines.extend([
            "",
            "### Frozen Noise-Floor Shrinkage Challengers",
            "",
            f"- Freeze timestamp UTC: `{frozen_noise.get('freeze_ts')}`",
            f"- Forward market denominator: `{frozen_noise.get('forward_market_denominator')}`",
            f"- Future candidate rows: `{frozen_noise.get('future_candidate_rows')}`",
        ])
        for row in frozen_noise.get("summary") or []:
            fv_checks = row.get("fv_validation_checks") or {}
            exec_checks = row.get("execution_promotion_checks") or {}
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"coverage `{row.get('coverage_pct')}`, net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, "
                f"brier `{row.get('avg_brier')}`, "
                f"fv blockers `{', '.join(fv_checks.get('blockers') or []) or 'none'}`, "
                f"execution blockers `{', '.join(exec_checks.get('blockers') or []) or 'none'}`"
            )
    frozen_calibrated = entry_watch.get("frozen_raw_entry_calibrated_summary") or {}
    if frozen_calibrated:
        lines.extend([
            "",
            "### Frozen Raw Entry Calibrated Probability",
            "",
            f"- Freeze timestamp UTC: `{frozen_calibrated.get('freeze_ts')}`",
            f"- Forward market denominator: `{frozen_calibrated.get('forward_market_denominator')}`",
            f"- Future entry rows: `{frozen_calibrated.get('future_entry_rows')}`",
        ])
        for row in frozen_calibrated.get("ranked") or []:
            lines.append(
                f"- `{row.get('overlay')}`: entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"coverage `{row.get('coverage_pct')}`, brier `{row.get('avg_brier')}`, "
                f"delta `{row.get('brier_delta_vs_raw')}`, net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, "
                f"blockers `{', '.join(row.get('blockers') or []) or 'none'}`"
            )
    forward_monitor = entry_watch.get("calibrated_fv_forward_monitor_summary") or {}
    if forward_monitor:
        wl = forward_monitor.get("selected_win_loss") or {}
        cal = forward_monitor.get("calibration_delta") or {}
        lines.extend([
            "",
            "### Calibrated FV Forward Monitor",
            "",
            "- Tracks clean forward markets, pending selections, and missed markets after the calibrated-FV freeze.",
            f"- Clean forward markets: `{forward_monitor.get('clean_forward_market_count')}`",
            f"- Selected/settled/pending/missed: `{forward_monitor.get('selected_clean_count')}/{forward_monitor.get('settled_selected_count')}/{forward_monitor.get('pending_selected_count')}/{forward_monitor.get('missed_clean_count')}`",
            f"- Coverage: `{forward_monitor.get('coverage_pct')}`",
            f"- Settled W/L net: `{wl.get('wins')}/{wl.get('losses')}` `{fmt_cents(forward_monitor.get('selected_net_cents'))}`",
            f"- Calibration deltas +5 minus raw Brier/logloss: `{cal.get('brier_delta_sum')}/{cal.get('logloss_delta_sum')}`",
        ])
        for item in forward_monitor.get("clean_details") or []:
            selected = item.get("selected_row") or {}
            lines.append(
                f"- `{item.get('market')}` selected `{item.get('selected')}` close `{selected.get('close_state')}` "
                f"sec_to/since_close `{selected.get('seconds_to_or_since_close_at_last_observation')}` side `{selected.get('side')}` "
                f"p_raw/+5/ask `{selected.get('p_raw')}/{selected.get('p_plus05')}/{selected.get('ask_prob')}` "
                f"won `{selected.get('side_won')}` net `{fmt_cents(selected.get('net_gross_cents_after_entry_fee'))}` "
                f"brier/logloss d `{selected.get('brier_delta_plus05_minus_raw')}/{selected.get('logloss_delta_plus05_minus_raw')}`"
            )
    sequential = entry_watch.get("calibrated_fv_sequential_summary") or {}
    if sequential:
        brier = sequential.get("brier") or {}
        logloss = sequential.get("logloss") or {}
        lines.extend([
            "",
            "### Calibrated FV Sequential Evidence",
            "",
            "- Paired forward raw-vs-+5 calibration evidence on settled selected rows.",
            f"- Status: `{sequential.get('evidence_status')}`",
            f"- Settled rows: `{sequential.get('settled_rows')}`",
            f"- Blockers: `{', '.join(sequential.get('blockers') or []) or 'none'}`",
            f"- Brier mean delta negative/positive: `{brier.get('mean_delta')}` `{brier.get('negative_count')}/{brier.get('positive_count')}`",
            f"- Logloss mean delta negative/positive: `{logloss.get('mean_delta')}` `{logloss.get('negative_count')}/{logloss.get('positive_count')}`",
        ])
    physics_attribution = entry_watch.get("calibrated_fv_physics_attribution_summary") or {}
    if physics_attribution:
        lines.extend([
            "",
            "### Calibrated FV Physics Attribution",
            "",
            "- Predeclared physics buckets for the frozen raw-entry +5pp FV overlay.",
            f"- Selected/settled/pending: `{physics_attribution.get('selected_clean_count')}/{physics_attribution.get('settled_selected_count')}/{physics_attribution.get('pending_selected_count')}`",
            f"- Blockers: `{', '.join(physics_attribution.get('blockers') or []) or 'none'}`",
        ])
        bucket_rows = physics_attribution.get("buckets") or []
        ranked = sorted(
            [row for row in bucket_rows if row.get("settled")],
            key=lambda row: (
                -(safe_float(row.get("settled")) or 0.0),
                safe_float(row.get("brier_delta_mean_plus05_minus_raw")) or 999.0,
                str(row.get("bucket") or ""),
            ),
        )
        for row in ranked[:8]:
            lines.append(
                f"- `{row.get('bucket')}`: selected `{row.get('selected')}`, settled `{row.get('settled')}`, "
                f"W/L `{row.get('wins')}/{row.get('losses')}`, net `{fmt_cents(row.get('net_cents'))}`, "
                f"brier mean delta `{row.get('brier_delta_mean_plus05_minus_raw')}`, "
                f"logloss mean delta `{row.get('logloss_delta_mean_plus05_minus_raw')}`"
            )
    path_contradiction = entry_watch.get("calibrated_fv_path_contradiction_summary") or {}
    if path_contradiction:
        lines.extend([
            "",
            "### Calibrated FV Path Contradiction",
            "",
            "- Compares the early raw-p50 selected side against later actual v28 approvals in the same market.",
            f"- Selected/settled rows: `{path_contradiction.get('selected_rows')}/{path_contradiction.get('settled_rows')}`",
            f"- Rows with later opposite approval: `{path_contradiction.get('later_opposite_approval_rows')}`",
            f"- Settled contradiction W/L for early selected side: `{path_contradiction.get('settled_later_opposite_selected_wins')}/{path_contradiction.get('settled_later_opposite_selected_losses')}`",
            f"- Blockers: `{', '.join(path_contradiction.get('blockers') or []) or 'none'}`",
        ])
        for row in path_contradiction.get("rows") or []:
            if row.get("has_later_opposite_approval") or row.get("later_approval_count"):
                opp = row.get("first_later_opposite_approval") or {}
                lines.append(
                    f"- `{row.get('market')}` early `{row.get('selected_side')}` p/ask "
                    f"`{row.get('selected_p_raw')}/{row.get('selected_ask_prob')}` won `{row.get('selected_side_won')}`; "
                    f"later approvals `{row.get('later_approval_count')}`, opposite `{row.get('later_opposite_side_count')}`, "
                    f"first opposite `{opp.get('side')}` after `{opp.get('delay_seconds')}` sec"
                )
    path_confirmed = entry_watch.get("path_confirmed_entry_summary") or {}
    if path_confirmed:
        lines.extend([
            "",
            "### Path-Confirmed Entry Candidates",
            "",
            "- Live-realistic delay challengers for broad raw-p50 entries after the path-contradiction loss.",
            f"- Forward denominator/base entries: `{path_confirmed.get('forward_market_denominator')}/{path_confirmed.get('base_entries')}`",
        ])
        for row in path_confirmed.get("summaries") or []:
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"W/L `{row.get('wins')}/{row.get('losses')}`, coverage `{row.get('coverage_pct')}`, "
                f"net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, "
                f"brier/logloss delta `{row.get('brier_delta_mean_plus05_minus_raw')}/{row.get('logloss_delta_mean_plus05_minus_raw')}`, "
                f"blocked `{row.get('blocked_count')}` {row.get('blocked_reasons')}"
            )
    path_rmt_gate = entry_watch.get("path_rmt_forward_gate_summary") or {}
    if path_rmt_gate:
        lines.extend([
            "",
            "### Path/RMT Fresh Forward Gate",
            "",
            "- Fresh post-discovery freeze for the current best path/RMT challenger.",
            f"- Freeze timestamp UTC: `{path_rmt_gate.get('freeze_ts')}`",
            f"- Forward denominator/base entries: `{path_rmt_gate.get('forward_market_denominator')}/{path_rmt_gate.get('base_entries')}`",
            f"- Any promotable: `{path_rmt_gate.get('any_promotable')}`",
            f"- Future clean markets needed for denominator 10: `{(path_rmt_gate.get('runway') or {}).get('future_clean_markets_to_denominator_10')}`",
            f"- Future clean markets needed for denominator 30: `{(path_rmt_gate.get('runway') or {}).get('future_clean_markets_to_denominator_30')}`",
        ])
        for row in path_rmt_gate.get("summaries") or []:
            runway = row.get("runway") or {}
            vs_base = row.get("vs_baseline") or {}
            lines.append(
                f"- `{row.get('policy')}`: entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"W/L `{row.get('wins')}/{row.get('losses')}`, coverage `{row.get('coverage_pct')}`, "
                f"net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, brier `{row.get('avg_brier')}`, "
                f"net_vs_base `{fmt_cents(vs_base.get('net_cents_delta'))}`, brier_vs_base `{vs_base.get('brier_delta')}`, "
                f"settled_to_30 `{runway.get('settled_rows_to_min_30')}`, "
                f"actual_needed_for_sim35 `{runway.get('actual_entries_needed_for_simulated_share_lte_35pct')}`, "
                f"blockers `{', '.join(row.get('promotion_blockers') or []) or 'none'}`"
            )
    fv_model = entry_watch.get("fv_model_readiness_summary") or {}
    if fv_model:
        candidate = fv_model.get("candidate") or {}
        readiness = fv_model.get("readiness") or {}
        frozen = fv_model.get("frozen_forward") or {}
        discovery = fv_model.get("discovery") or {}
        plus05 = discovery.get("plus05") or {}
        lines.extend([
            "",
            "### FV Model Readiness",
            "",
            f"- Candidate: `{candidate.get('name')}`",
            f"- FV probability: `{candidate.get('fv_probability')}`",
            f"- Ready: `{readiness.get('fv_model_ready')}`",
            f"- Blockers: `{', '.join(readiness.get('blockers') or []) or 'none'}`",
            f"- Discovery +5pp Brier/logloss deltas: `{plus05.get('brier_delta_vs_raw')}/{plus05.get('logloss_delta_vs_raw')}`",
            f"- Frozen forward denominator/rows: `{frozen.get('forward_market_denominator')}/{frozen.get('future_entry_rows')}`",
        ])
    overlay_readiness = entry_watch.get("fv_overlay_challenger_readiness_summary") or {}
    if overlay_readiness:
        lines.extend([
            "",
            "### FV Overlay Challenger Readiness",
            "",
            "- Fixed raw-v28 p50 entry surface; compares FV overlays only.",
            f"- Forward denominator/entry rows: `{overlay_readiness.get('forward_market_denominator')}/{overlay_readiness.get('future_entry_rows')}`",
            f"- Best forward overlay: `{overlay_readiness.get('best_forward_overlay')}`",
            f"- Any ready: `{overlay_readiness.get('any_ready')}`",
        ])
        for row in (overlay_readiness.get("candidates") or [])[:6]:
            fwd = row.get("forward") or {}
            disc = row.get("discovery") or {}
            lines.append(
                f"- `{row.get('overlay')}`: ready `{row.get('ready')}`, settled `{fwd.get('settled')}`, "
                f"coverage `{fwd.get('coverage_pct')}`, fwd Brier/logloss d "
                f"`{fwd.get('brier_delta_vs_raw')}/{fwd.get('logloss_delta_vs_raw')}`, "
                f"disc Brier/logloss d `{disc.get('brier_delta_vs_raw')}/{disc.get('logloss_delta_vs_raw')}`, "
                f"blockers `{', '.join(row.get('blockers') or []) or 'none'}`"
            )
    sample_plan = entry_watch.get("calibrated_fv_sample_plan_summary") or {}
    if sample_plan:
        current = sample_plan.get("current") or {}
        remaining = sample_plan.get("remaining") or {}
        path_runway = sample_plan.get("path_confirmed_runway") or {}
        lines.extend([
            "",
            "### Calibrated FV Sample Plan",
            "",
            "- Forward-evidence runway for the raw-entry +5pp FV overlay.",
            f"- Current denominator/selected/settled/pending: `{current.get('forward_denominator')}/{current.get('selected_rows')}/{current.get('settled_selected_rows')}/{current.get('pending_selected_rows')}`",
            f"- Remaining settled rows to 30: `{remaining.get('settled_rows_to_min_30')}`",
            f"- Additional selected after pending to 30: `{remaining.get('additional_selected_rows_after_pending_to_min_30')}`",
            f"- Misses needed for current high coverage <=90%: `{remaining.get('misses_needed_to_reduce_current_high_coverage_to_90pct')}`",
            f"- Miss budget after 30 selected before coverage <70%: `{remaining.get('miss_budget_after_reaching_30_selected_before_coverage_below_70pct')}`",
        ])
        if path_runway:
            lines.extend([
                "",
                "### Path/RMT Candidate Runway",
                "",
                f"- Current best target-coverage path policy: `{path_runway.get('policy')}`",
                f"- Entries/settled: `{path_runway.get('entries')}/{path_runway.get('settled')}`",
                f"- Actual/simulated entries: `{path_runway.get('approved_entry_count')}/{path_runway.get('added_reject_count')}`; simulated share `{path_runway.get('simulated_share')}`",
                f"- Coverage/net/Brier: `{path_runway.get('coverage_pct')}` / `{fmt_cents(path_runway.get('net_cents_after_entry_fee'))}` / `{path_runway.get('avg_brier')}`",
                f"- Settled rows still needed for 30: `{path_runway.get('settled_rows_to_min_30')}`",
                f"- Additional actual entries needed for simulated share <=35%: `{path_runway.get('actual_entries_needed_for_simulated_share_lte_35pct')}`",
            ])
    coverage_valve = entry_watch.get("raw_entry_coverage_valve_summary") or {}
    if coverage_valve:
        lines.extend([
            "",
            "### Raw-Entry Coverage Valve",
            "",
            "- Shadow-only coverage valve for raw-v28 p50 entries using the current best FV overlay.",
            f"- Best current policy: `{coverage_valve.get('best_policy')}`",
            f"- Forward denominator: `{coverage_valve.get('forward_denominator')}`",
        ])
        for row in (coverage_valve.get("ranked") or [])[:4]:
            disc = (row.get("discovery") or {}).get("coverage_valve") or {}
            fwd = (row.get("forward") or {}).get("coverage_valve") or {}
            lines.append(
                f"- `{row.get('policy')}`: discovery coverage/net `{disc.get('coverage_pct')}/{fmt_cents(disc.get('net_cents_after_entry_fee'))}`, "
                f"forward entries/settled/W-L `{fwd.get('entries')}/{fwd.get('settled')}/{fwd.get('wins')}-{fwd.get('losses')}`, "
                f"coverage/net/Brier `{fwd.get('coverage_pct')}/{fmt_cents(fwd.get('net_cents_after_entry_fee'))}/{fwd.get('avg_brier')}`, "
                f"blockers `{', '.join((row.get('forward') or {}).get('blockers') or []) or 'none'}`"
            )
    target_coverage_fv = entry_watch.get("target_coverage_fv_summary") or {}
    if target_coverage_fv:
        lines.extend([
            "",
            "### Target-Coverage FV Overlay Validator",
            "",
            "- Scores FV overlays on the current best raw-entry coverage valve, not the broad raw-p50 surface.",
            f"- Policy: `{target_coverage_fv.get('policy')}`",
            f"- Forward denominator: `{target_coverage_fv.get('forward_denominator')}`",
        ])
        for row in (target_coverage_fv.get("forward") or [])[:5]:
            lines.append(
                f"- `{row.get('overlay')}`: entries/settled `{row.get('entries')}/{row.get('settled')}`, "
                f"coverage `{row.get('coverage_pct')}`, W/L `{row.get('wins')}-{row.get('losses')}`, "
                f"net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, Brier/logloss d "
                f"`{row.get('brier_delta_vs_raw')}/{row.get('logloss_delta_vs_raw')}`, "
                f"blockers `{', '.join(row.get('blockers') or []) or 'none'}`"
            )
    target_seq = entry_watch.get("target_coverage_fv_sequential_summary") or {}
    if target_seq:
        brier = target_seq.get("brier") or {}
        logloss = target_seq.get("logloss") or {}
        b_boot = brier.get("bootstrap") or {}
        l_boot = logloss.get("bootstrap") or {}
        lines.extend([
            "",
            "### Target-Coverage FV Sequential Evidence",
            "",
            "- Paired evidence for the best target-coverage FV overlay versus raw FV.",
            f"- Policy/overlay: `{target_seq.get('policy')}` / `{target_seq.get('overlay')}`",
            f"- Entries/settled/coverage: `{target_seq.get('entries')}/{target_seq.get('settled_rows')}/{target_seq.get('coverage_pct')}`",
            f"- Brier mean/p95/prob-negative: `{brier.get('mean_delta')}/{b_boot.get('p95')}/{b_boot.get('prob_negative')}`",
            f"- Logloss mean/p95/prob-negative: `{logloss.get('mean_delta')}/{l_boot.get('p95')}/{l_boot.get('prob_negative')}`",
            f"- Settled rows to 30: `{target_seq.get('settled_rows_to_30')}`; blockers `{', '.join(target_seq.get('blockers') or []) or 'none'}`",
        ])
    target_attr = entry_watch.get("target_coverage_fv_attribution_summary") or {}
    if target_attr:
        lines.extend([
            "",
            "### Target-Coverage FV Attribution",
            "",
            "- Bucket attribution for where the target-coverage FV improvement comes from.",
        ])
        for note in target_attr.get("interpretation") or []:
            lines.append(f"- {note}")
        for row in (target_attr.get("buckets") or [])[:8]:
            lines.append(
                f"- `{row.get('bucket')}`: rows `{row.get('rows')}`, W/L `{row.get('wins')}-{row.get('losses')}`, "
                f"net `{fmt_cents(row.get('net_cents'))}`, Brier sum `{row.get('brier_delta_sum')}`, "
                f"logloss sum `{row.get('logloss_delta_sum')}`"
            )
    target_audit = entry_watch.get("target_coverage_promotion_audit_summary") or {}
    if target_audit:
        candidate = target_audit.get("candidate") or {}
        lines.extend([
            "",
            "### Target-Coverage Promotion Audit",
            "",
            f"- Ready for promotion review: `{target_audit.get('ready_for_promotion_review')}`",
            f"- Candidate: `{candidate.get('policy')}` / `{candidate.get('overlay')}`",
            f"- Entries/settled/coverage: `{candidate.get('entries')}/{candidate.get('settled_rows')}/{candidate.get('coverage_pct')}`",
            f"- Net/Brier p95/Logloss p95: `{candidate.get('net_cents_after_entry_fee')}/{candidate.get('brier_p95_delta')}/{candidate.get('logloss_p95_delta')}`",
            f"- Settled rows to 30: `{(target_audit.get('remaining') or {}).get('settled_rows_to_30')}`",
        ])
        for item in target_audit.get("checks") or []:
            if item.get("passed") is not True:
                lines.append(
                    f"- blocker `{item.get('name')}`: actual `{item.get('actual')}`, required `{item.get('required')}`"
                )
    target_runway = entry_watch.get("target_coverage_sample_runway_summary") or {}
    if target_runway:
        runway = target_runway.get("coverage_runway") or {}
        lines.extend([
            "",
            "### Target-Coverage Sample Runway",
            "",
            "- Coverage/sample fragility for the current target-coverage FV candidate.",
            f"- Entries/settled/pending/denominator: `{target_runway.get('entries')}/{target_runway.get('settled')}/{target_runway.get('pending')}/{target_runway.get('forward_denominator')}`",
            f"- Coverage: `{target_runway.get('coverage_pct')}`; settled rows to 30 `{target_runway.get('settled_rows_to_30')}`",
            f"- Miss runway before below 75%: `{runway.get('max_consecutive_future_misses_before_below_75')}`; entry runway before above 90%: `{runway.get('max_consecutive_future_entries_before_above_90')}`",
        ])
        for row in target_runway.get("pending_rows") or []:
            lines.append(
                f"- pending `{row.get('market')}` `{row.get('side')}`: raw/ask/edge "
                f"`{row.get('p_raw')}/{row.get('ask_prob')}/{row.get('raw_edge_prob')}`, "
                f"reason `{row.get('coverage_valve_reason')}`"
            )
    target_fragility = entry_watch.get("target_coverage_fv_fragility_audit_summary") or {}
    if target_fragility:
        lines.extend([
            "",
            "### Target-Coverage FV Fragility Audit",
            "",
            "- Stress-tests whether the active overlay edge is concentrated in one row or one fragile bucket.",
            f"- Rows/W/L: `{target_fragility.get('rows')}/{target_fragility.get('wins')}/{target_fragility.get('losses')}`",
            f"- Brier mean/sum: `{target_fragility.get('brier_delta_mean')}/{target_fragility.get('brier_delta_sum')}`",
            f"- Logloss mean/sum: `{target_fragility.get('logloss_delta_mean')}/{target_fragility.get('logloss_delta_sum')}`",
            f"- Negative/positive Brier rows: `{target_fragility.get('negative_brier_rows')}/{target_fragility.get('positive_brier_rows')}`",
            f"- Fragility flags: `{', '.join(target_fragility.get('fragility_flags') or []) or 'none'}`",
        ])
        for row in target_fragility.get("geometry_bucket_summary") or []:
            lines.append(
                f"- geometry `{row.get('bucket')}`: rows/W-L `{row.get('rows')}/{row.get('wins')}-{row.get('losses')}`, "
                f"brier sum `{row.get('brier_delta_sum')}`"
            )
    target_reliability = entry_watch.get("target_coverage_fv_bucket_reliability_summary") or {}
    if target_reliability:
        lines.extend([
            "",
            "### Target-Coverage FV Bucket Reliability",
            "",
            "- Bucket calibration for raw FV versus the active target-coverage overlay.",
            f"- Rows: `{target_reliability.get('rows')}`",
            f"- Raw/overlay ECE: `{target_reliability.get('raw_ece')}/{target_reliability.get('overlay_ece')}`",
            f"- ECE delta overlay-minus-raw: `{target_reliability.get('ece_delta_overlay_minus_raw')}`",
            f"- Flags: `{', '.join(target_reliability.get('flags') or []) or 'none'}`",
        ])
        for row in target_reliability.get("overlay_summary") or []:
            if not row.get("count"):
                continue
            lines.append(
                f"- overlay bucket `{row.get('bucket')}`: count `{row.get('count')}`, "
                f"W/L `{row.get('wins')}-{row.get('losses')}`, avg p `{row.get('avg_p')}`, "
                f"win rate `{row.get('win_rate')}`, reliable `{row.get('bucket_reliable_enough')}`"
            )
    target_live_evidence = entry_watch.get("target_coverage_fv_live_evidence_audit_summary") or {}
    if target_live_evidence:
        total = target_live_evidence.get("total") or {}
        lines.extend([
            "",
            "### Target-Coverage FV Live Evidence Audit",
            "",
            "- Separates approved-entry evidence from actionable rejected shadow rows.",
            f"- Total rows/W-L/net: `{total.get('rows')}/{total.get('wins')}-{total.get('losses')}/{fmt_cents(total.get('net_cents'))}`",
            f"- Approved-entry rows: `{target_live_evidence.get('approved_entry_rows')}`",
            f"- Simulated/rejected rows/share: `{target_live_evidence.get('simulated_or_rejected_rows')}/{fmt_pct(target_live_evidence.get('simulated_share'))}`",
            f"- Blockers: `{', '.join(target_live_evidence.get('blockers') or []) or 'none'}`",
        ])
        for source, row in (target_live_evidence.get("by_source") or {}).items():
            lines.append(
                f"- source `{source}`: rows/W-L `{row.get('rows')}/{row.get('wins')}-{row.get('losses')}`, "
                f"brier d mean `{row.get('brier_delta_mean')}`"
            )
    target_danger_overlap = entry_watch.get("target_coverage_danger_overlap_summary") or {}
    if target_danger_overlap:
        max_row = target_danger_overlap.get("max_gap_row") or {}
        lines.extend([
            "",
            "### Target-Coverage Danger Overlap",
            "",
            "- Checks whether the target-coverage surface actually enters the raw/book danger-zone regime.",
            f"- Entries/settled/scored: `{target_danger_overlap.get('entries')}/{target_danger_overlap.get('settled')}/{target_danger_overlap.get('scored')}`",
            f"- Danger rows >30pp/>20pp: `{target_danger_overlap.get('danger_gt30_count')}/{target_danger_overlap.get('danger_gt20_count')}`",
            f"- Max gap row: `{max_row.get('market')}` `{max_row.get('side')}` gap `{max_row.get('raw_book_gap')}` won `{max_row.get('won')}`",
        ])
        for note in target_danger_overlap.get("interpretation") or []:
            lines.append(f"- {note}")
    price_friction = entry_watch.get("target_coverage_price_friction_summary") or {}
    if price_friction:
        summary = price_friction.get("summary") or {}
        lines.extend([
            "",
            "### Target-Coverage Price Friction",
            "",
            "- Separates directional FV failure from entry-price and boundary-friction damage.",
            f"- Entries/settled/coverage: `{summary.get('rows')}/{summary.get('settled')}/{summary.get('coverage_pct')}`",
            f"- Net cents: `{fmt_cents(summary.get('net_cents'))}`",
            "",
            "| tag | settled | W/L | win rate | net c | avg ask | avg edge |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ])
        for row in (price_friction.get("tag_rollups") or [])[:8]:
            if int(row.get("settled") or 0) == 0:
                continue
            lines.append(
                f"| {row.get('bucket')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
                f"{row.get('win_rate')} | {fmt_cents(row.get('net_cents'))} | "
                f"{row.get('avg_ask')} | {row.get('avg_raw_edge')} |"
            )
    false_conviction = entry_watch.get("false_conviction_physics_summary") or {}
    if false_conviction:
        current = false_conviction.get("current") or {}
        lines.extend([
            "",
            "### False-Conviction Physics Audit",
            "",
            "- Tests whether medium-edge early boundary rows are over-sharp FV rather than real edge.",
            f"- Entries/settled/coverage: `{current.get('entries')}/{current.get('settled')}/{current.get('coverage_pct')}`",
            f"- Current W/L/net: `{current.get('wins')}/{current.get('losses')}/{fmt_cents(current.get('net_cents'))}`",
        ])
        for note in false_conviction.get("interpretation") or []:
            lines.append(f"- {note}")
        for report in false_conviction.get("mask_reports") or []:
            if report.get("mask") not in {"mid_edge_boundary_4_8pp", "composite_false_conviction_zone"}:
                continue
            inside = report.get("inside") or {}
            best = sorted(
                report.get("adjusted_valves") or [],
                key=lambda row: float(((row.get("kept") or {}).get("delta_vs_current_net_cents")) or -999999.0),
                reverse=True,
            )[0] if report.get("adjusted_valves") else {}
            kept = best.get("kept") or {}
            lines.append(
                f"- `{report.get('mask')}`: inside settled/net `{inside.get('settled')}/{fmt_cents(inside.get('net_cents'))}`, "
                f"best shrink `{best.get('overlay')}` kept coverage/net/delta "
                f"`{kept.get('coverage_pct')}/{fmt_cents(kept.get('net_cents'))}/{fmt_cents(kept.get('delta_vs_current_net_cents'))}`"
            )
    composite_repair_robustness = entry_watch.get("composite_false_conviction_repair_robustness_summary") or {}
    if composite_repair_robustness:
        ranked = composite_repair_robustness.get("ranked") or []
        best = ranked[0] if ranked else {}
        full = best.get("full") or {}
        candidate = full.get("candidate_summary") or {}
        lines.extend([
            "",
            "### Composite False-Conviction Repair Robustness",
            "",
            "- Leave-one-market-out check for replacing composite false-conviction rows while preserving target coverage.",
            f"- Best scorer: `{best.get('scorer')}`",
            f"- Full net/coverage: `{fmt_cents(candidate.get('net_cents'))}/{candidate.get('coverage_pct')}`",
            f"- Worst leave-one-out net: `{fmt_cents(best.get('worst_net'))}`",
            f"- Negative-net leaveouts: `{best.get('negative_net_count')}`",
            f"- Robust positive: `{best.get('robust_positive')}`",
        ])
        for note in composite_repair_robustness.get("interpretation") or []:
            lines.append(f"- {note}")
    composite_repair_stress = entry_watch.get("composite_false_conviction_repair_stress_summary") or {}
    if composite_repair_stress:
        cand = composite_repair_stress.get("candidate_summary") or {}
        target = composite_repair_stress.get("target_summary") or {}
        warnings = composite_repair_stress.get("warnings") or []
        lines.extend([
            "",
            "### Composite False-Conviction Repair Stress",
            "",
            "- Source-mix and full-loss fragility check for the frozen composite repair candidate.",
            f"- Candidate settled/W-L/net/coverage: `{cand.get('settled')}/{cand.get('wins')}-{cand.get('losses')}/{fmt_cents(cand.get('net_cents'))}/{cand.get('coverage_pct')}`",
            f"- Target settled/W-L/net/coverage: `{target.get('settled')}/{target.get('wins')}-{target.get('losses')}/{fmt_cents(target.get('net_cents'))}/{target.get('coverage_pct')}`",
            f"- Delta vs target: `{fmt_cents(composite_repair_stress.get('delta_vs_target_cents'))}`",
            f"- Source counts: `{composite_repair_stress.get('source_counts')}`",
            f"- Warnings: `{'; '.join(warnings) if warnings else 'none'}`",
        ])
        for note in composite_repair_stress.get("current_read") or []:
            lines.append(f"- {note}")
    weak_reversal_bakeoff = entry_watch.get("weak_boundary_reversal_bakeoff_summary") or {}
    if weak_reversal_bakeoff:
        best = weak_reversal_bakeoff.get("best") or {}
        cand = best.get("candidate_summary") or {}
        weak = best.get("weak_summary") or {}
        repl = best.get("replacement_summary") or {}
        repair = best.get("repair_summary") or {}
        loo = best.get("loo") or {}
        lines.extend([
            "",
            "### Weak-Boundary Reversal Bakeoff",
            "",
            "- Tests whether weak near-boundary high-recross entries should wait for a same-market opposite-side signal.",
            f"- Best policy: `{best.get('policy')}`",
            f"- Candidate net/coverage/delta: `{fmt_cents(cand.get('net_cents'))}/{cand.get('coverage_pct')}/{fmt_cents(best.get('delta_vs_target_cents'))}`",
            f"- Weak removed net / opposite replacement net / repair net: `{fmt_cents(weak.get('net_cents'))}/{fmt_cents(repl.get('net_cents'))}/{fmt_cents(repair.get('net_cents'))}`",
            f"- Leave-one-out worst net / negative exclusions: `{fmt_cents(loo.get('worst_net_cents'))}/{loo.get('negative_exclusions')}`",
        ])
        for note in weak_reversal_bakeoff.get("interpretation") or []:
            lines.append(f"- {note}")
    weak_reversal_residual = entry_watch.get("weak_reversal_residual_attribution_summary") or {}
    if weak_reversal_residual:
        lines.extend([
            "",
            "### Weak-Reversal Residual Attribution",
            "",
            "- Shows what still loses after the best weak-boundary reversal repair.",
            f"- Best policy: `{weak_reversal_residual.get('best_policy')}`",
        ])
        for note in weak_reversal_residual.get("interpretation") or []:
            lines.append(f"- {note}")
        for row in (weak_reversal_residual.get("worst_tags") or [])[:5]:
            lines.append(
                f"- `{row.get('tag')}`: settled `{row.get('settled')}`, "
                f"W/L `{row.get('wins')}/{row.get('losses')}`, net `{fmt_cents(row.get('net_cents'))}`"
            )
    weak_reversal_fv = entry_watch.get("weak_reversal_residual_fv_shrink_summary") or {}
    if weak_reversal_fv:
        best = weak_reversal_fv.get("best") or {}
        zone = best.get("zone") or {}
        lines.extend([
            "",
            "### Weak-Reversal Residual FV Shrink",
            "",
            "- Discovery-only FV calibration test for the residual NO-side 5-8pp raw-edge zone.",
            f"- Best variant: `{best.get('variant')}`",
            f"- All Brier/logloss delta: `{best.get('all_brier_delta_vs_raw')}/{best.get('all_logloss_delta_vs_raw')}`",
            f"- Zone rows/avg p/win rate: `{zone.get('rows')}/{zone.get('avg_p')}/{zone.get('win_rate')}`",
            f"- Zone Brier/logloss delta: `{best.get('zone_brier_delta_vs_raw')}/{best.get('zone_logloss_delta_vs_raw')}`",
        ])
        for note in weak_reversal_fv.get("interpretation") or []:
            lines.append(f"- {note}")
    frozen_weak_reversal_fv = entry_watch.get("frozen_weak_reversal_residual_fv_shrink_summary") or {}
    if frozen_weak_reversal_fv:
        lines.extend([
            "",
            "### Frozen Weak-Reversal Residual FV Shrink",
            "",
            "- Future-only calibration validator for the residual FV shrink.",
            f"- Freeze timestamp UTC: `{(frozen_weak_reversal_fv.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Brier/logloss delta: `{frozen_weak_reversal_fv.get('brier_delta_vs_raw')}/{frozen_weak_reversal_fv.get('logloss_delta_vs_raw')}`",
            f"- Ready: `{frozen_weak_reversal_fv.get('ready_for_consideration')}`; blockers `{', '.join(frozen_weak_reversal_fv.get('blockers') or []) or 'none'}`",
        ])
        for note in frozen_weak_reversal_fv.get("interpretation") or []:
            lines.append(f"- {note}")
    no_mid_general = entry_watch.get("no_mid_edge_fv_generalization_summary") or {}
    if no_mid_general:
        best = no_mid_general.get("best") or {}
        all_m = best.get("all") or {}
        no_mid = best.get("no_mid") or {}
        lines.extend([
            "",
            "### NO Mid-Edge FV Generalization",
            "",
            "- Checks whether NO-side 5-8pp overconfidence exists on the broader target surface.",
            f"- Best variant: `{best.get('variant')}`",
            f"- All Brier/logloss delta: `{all_m.get('brier_delta_vs_raw')}/{all_m.get('logloss_delta_vs_raw')}`",
            f"- NO-mid rows/W-L/net/avg p/win rate: `{no_mid.get('rows')}/{no_mid.get('wins')}-{no_mid.get('losses')}/{fmt_cents(no_mid.get('net_cents'))}/{no_mid.get('avg_p')}/{no_mid.get('win_rate')}`",
        ])
        for note in no_mid_general.get("interpretation") or []:
            lines.append(f"- {note}")
    frozen_no_mid = entry_watch.get("frozen_no_mid_edge_fv_summary") or {}
    if frozen_no_mid:
        lines.extend([
            "",
            "### Frozen NO Mid-Edge FV",
            "",
            "- Future-only validator for the broader NO-side 5-8pp book-anchor FV shrink.",
            f"- Freeze timestamp UTC: `{(frozen_no_mid.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Brier/logloss delta: `{frozen_no_mid.get('brier_delta_vs_raw')}/{frozen_no_mid.get('logloss_delta_vs_raw')}`",
            f"- Ready: `{frozen_no_mid.get('ready_for_consideration')}`; blockers `{', '.join(frozen_no_mid.get('blockers') or []) or 'none'}`",
        ])
        for note in frozen_no_mid.get("interpretation") or []:
            lines.append(f"- {note}")
    no_mid_entry = entry_watch.get("no_mid_edge_entry_repair_summary") or {}
    if no_mid_entry:
        target = no_mid_entry.get("target_summary") or {}
        cand = no_mid_entry.get("candidate_summary") or {}
        skipped = no_mid_entry.get("skipped_summary") or {}
        repair = no_mid_entry.get("repair_summary") or {}
        loo = no_mid_entry.get("loo") or {}
        lines.extend([
            "",
            "### NO Mid-Edge Entry Repair",
            "",
            "- Discovery-only broader entry translation of the NO-side 5-8pp FV overconfidence clue.",
            f"- Policy: `{no_mid_entry.get('policy')}`",
            f"- Target net / candidate net / delta: `{fmt_cents(target.get('net_cents'))}/{fmt_cents(cand.get('net_cents'))}/{fmt_cents(no_mid_entry.get('delta_vs_target_cents'))}`",
            f"- Candidate coverage: `{cand.get('coverage_pct')}`; skipped/repair net `{fmt_cents(skipped.get('net_cents'))}/{fmt_cents(repair.get('net_cents'))}`",
            f"- Leave-one-out worst net / negative exclusions: `{fmt_cents(loo.get('worst_net_cents'))}/{loo.get('negative_exclusions')}`",
        ])
        for note in no_mid_entry.get("interpretation") or []:
            lines.append(f"- {note}")
    weak_reversal_repair = entry_watch.get("weak_reversal_residual_repair_summary") or {}
    if weak_reversal_repair:
        best = weak_reversal_repair.get("best") or {}
        cand = best.get("candidate_summary") or {}
        loo = best.get("loo") or {}
        lines.extend([
            "",
            "### Weak-Reversal Residual Repair",
            "",
            "- Discovery-only repair for the residual 5-8pp NO-side price-geometry loss cluster.",
            f"- Best policy: `{best.get('policy')}`",
            f"- Candidate net/coverage/delta: `{fmt_cents(cand.get('net_cents'))}/{cand.get('coverage_pct')}/{fmt_cents(best.get('delta_vs_weak_reversal_cents'))}`",
            f"- Leave-one-out worst net / negative exclusions: `{fmt_cents(loo.get('worst_net_cents'))}/{loo.get('negative_exclusions')}`",
        ])
        for note in weak_reversal_repair.get("interpretation") or []:
            lines.append(f"- {note}")
    frozen_weak_reversal_repair = entry_watch.get("frozen_weak_reversal_residual_repair_summary") or {}
    if frozen_weak_reversal_repair:
        cand = frozen_weak_reversal_repair.get("candidate_summary") or {}
        lines.extend([
            "",
            "### Frozen Weak-Reversal Residual Repair",
            "",
            "- Future-only validator for the positive weak-reversal residual repair discovery.",
            f"- Freeze timestamp UTC: `{(frozen_weak_reversal_repair.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Candidate entries/settled/net/coverage: `{cand.get('entries')}/{cand.get('settled')}/{fmt_cents(cand.get('net_cents'))}/{cand.get('coverage_pct')}`",
            f"- Live ready: `{frozen_weak_reversal_repair.get('live_ready')}`; blockers `{', '.join(frozen_weak_reversal_repair.get('blockers') or []) or 'none'}`",
        ])
        for note in frozen_weak_reversal_repair.get("interpretation") or []:
            lines.append(f"- {note}")
    early_clock_wait = entry_watch.get("early_clock_wait_bakeoff_summary") or {}
    if early_clock_wait:
        best = early_clock_wait.get("best") or {}
        cand = best.get("candidate_summary") or {}
        target = best.get("target_summary") or {}
        loo = best.get("loo") or {}
        lines.extend([
            "",
            "### Early-Clock Wait Bakeoff",
            "",
            "- Discovery-only test of whether very early boundary-churn rows should age before entry.",
            f"- Best policy: `{early_clock_wait.get('best_policy')}`",
            f"- Candidate entries/settled/net/coverage: `{cand.get('entries')}/{cand.get('settled')}/{fmt_cents(cand.get('net_cents'))}/{cand.get('coverage_pct')}`",
            f"- Target net/delta: `{fmt_cents(target.get('net_cents'))}/{fmt_cents(best.get('delta_vs_target_cents'))}`",
            f"- LOO worst/negative exclusions: `{fmt_cents(loo.get('worst_delta_cents'))}/{loo.get('negative_exclusions')}`",
        ])
    frozen_early_boundary_wait = entry_watch.get("frozen_early_boundary_wait_repair_summary") or {}
    if frozen_early_boundary_wait:
        cand = frozen_early_boundary_wait.get("candidate_summary") or {}
        lines.extend([
            "",
            "### Frozen Early-Boundary Wait Repair",
            "",
            "- Future-only validator for the early boundary-churn wait/repair discovery.",
            f"- Freeze timestamp UTC: `{(frozen_early_boundary_wait.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Candidate entries/settled/net/coverage: `{cand.get('entries')}/{cand.get('settled')}/{fmt_cents(cand.get('net_cents'))}/{cand.get('coverage_pct')}`",
            f"- Live ready: `{frozen_early_boundary_wait.get('live_ready')}`; blockers `{', '.join(frozen_early_boundary_wait.get('blockers') or []) or 'none'}`",
        ])
        for note in frozen_early_boundary_wait.get("interpretation") or []:
            lines.append(f"- {note}")
    frozen_early_boundary_opposite_wait = entry_watch.get("frozen_early_boundary_opposite_wait_repair_summary") or {}
    if frozen_early_boundary_opposite_wait:
        cand = frozen_early_boundary_opposite_wait.get("candidate_summary") or {}
        repl = frozen_early_boundary_opposite_wait.get("replacement_summary") or {}
        lines.extend([
            "",
            "### Frozen Early-Boundary Opposite Wait Repair",
            "",
            "- Future-only validator for the same-market opposite-side wait/repair discovery.",
            f"- Freeze timestamp UTC: `{(frozen_early_boundary_opposite_wait.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Candidate entries/settled/net/coverage: `{cand.get('entries')}/{cand.get('settled')}/{fmt_cents(cand.get('net_cents'))}/{cand.get('coverage_pct')}`",
            f"- Opposite replacements entries/net: `{repl.get('entries')}/{fmt_cents(repl.get('net_cents'))}`",
            f"- Live ready: `{frozen_early_boundary_opposite_wait.get('live_ready')}`; blockers `{', '.join(frozen_early_boundary_opposite_wait.get('blockers') or []) or 'none'}`",
        ])
        for note in frozen_early_boundary_opposite_wait.get("interpretation") or []:
            lines.append(f"- {note}")
    weak_reversal_strategy = entry_watch.get("weak_boundary_reversal_strategy_summary") or {}
    if weak_reversal_strategy and not weak_reversal_bakeoff:
        cand = weak_reversal_strategy.get("candidate_summary") or {}
        repl = weak_reversal_strategy.get("replacement_summary") or {}
        lines.extend([
            "",
            "### Weak-Boundary Reversal Strategy",
            "",
            f"- Candidate net/coverage/delta: `{fmt_cents(cand.get('net_cents'))}/{cand.get('coverage_pct')}/{fmt_cents(weak_reversal_strategy.get('delta_vs_target_cents'))}`",
            f"- Opposite replacement net: `{fmt_cents(repl.get('net_cents'))}`",
        ])
        for note in weak_reversal_strategy.get("interpretation") or []:
            lines.append(f"- {note}")
    side_bridge = entry_watch.get("side_asymmetry_fv_entry_bridge_summary") or {}
    if side_bridge:
        best = (side_bridge.get("ranked") or [{}])[0]
        cand = best.get("candidate_summary") or {}
        skipped = best.get("skipped_summary") or {}
        repair = best.get("repair_summary") or {}
        lines.extend([
            "",
            "### Side-Asymmetry FV Entry Bridge",
            "",
            "- Tests whether the side-asymmetry probability correction can become entry economics.",
            f"- Best adjusted-edge floor: `{best.get('edge_floor')}`",
            f"- Candidate net/coverage/delta: `{fmt_cents(cand.get('net_cents'))}/{cand.get('coverage_pct')}/{fmt_cents(best.get('delta_vs_target_cents'))}`",
            f"- Skipped net / repair net: `{fmt_cents(skipped.get('net_cents'))}/{fmt_cents(repair.get('net_cents'))}`",
        ])
        for note in side_bridge.get("interpretation") or []:
            lines.append(f"- {note}")
    side_bridge_repair = entry_watch.get("side_asymmetry_bridge_repair_bakeoff_summary") or {}
    if side_bridge_repair:
        best = (side_bridge_repair.get("ranked") or [{}])[0]
        cand = best.get("candidate_summary") or {}
        repair = best.get("repair_summary") or {}
        lines.extend([
            "",
            "### Side-Asymmetry Bridge Repair Bakeoff",
            "",
            "- Compares ex-ante repair scorers after the side-asymmetry bridge skip.",
            f"- Best repair scorer: `{best.get('scorer')}`",
            f"- Candidate net/coverage/delta: `{fmt_cents(cand.get('net_cents'))}/{cand.get('coverage_pct')}/{fmt_cents(best.get('delta_vs_target_cents'))}`",
            f"- Repair net: `{fmt_cents(repair.get('net_cents'))}`",
        ])
        for note in side_bridge_repair.get("interpretation") or []:
            lines.append(f"- {note}")
    side_bridge_strict = entry_watch.get("side_asymmetry_bridge_strict_repair_summary") or {}
    if side_bridge_strict:
        best = (side_bridge_strict.get("ranked") or [{}])[0]
        cand = best.get("candidate_summary") or {}
        repair = best.get("repair_summary") or {}
        lines.extend([
            "",
            "### Side-Asymmetry Bridge Strict Repair",
            "",
            "- Requires repair rows to clear the same adjusted-FV edge floor as kept rows.",
            f"- Best repair scorer: `{best.get('scorer')}`",
            f"- Coverage repaired: `{best.get('coverage_repaired')}`",
            f"- Candidate net/coverage/delta: `{fmt_cents(cand.get('net_cents'))}/{cand.get('coverage_pct')}/{fmt_cents(best.get('delta_vs_target_cents'))}`",
            f"- Strict repair net: `{fmt_cents(repair.get('net_cents'))}`",
        ])
        for note in side_bridge_strict.get("interpretation") or []:
            lines.append(f"- {note}")
    frozen_side_bridge = entry_watch.get("frozen_side_asymmetry_entry_bridge_summary") or {}
    if frozen_side_bridge:
        cand = frozen_side_bridge.get("candidate_summary") or {}
        target = frozen_side_bridge.get("target_summary") or {}
        skipped = frozen_side_bridge.get("skipped_summary") or {}
        repair = frozen_side_bridge.get("repair_summary") or {}
        lines.extend([
            "",
            "### Frozen Side-Asymmetry Entry Bridge",
            "",
            "- Future-only validator for the fixed side-asymmetry adjusted-edge skip plus strict far-boundary repair.",
            f"- Candidate: `{(frozen_side_bridge.get('freeze') or {}).get('candidate')}`",
            f"- Future denominator: `{frozen_side_bridge.get('future_denominator')}`",
            f"- Candidate entries/settled/coverage: `{cand.get('entries')}/{cand.get('settled')}/{cand.get('coverage_pct')}`",
            f"- Candidate net vs target: `{fmt_cents(cand.get('net_cents'))}/{fmt_cents(target.get('net_cents'))}`",
            f"- Delta vs target: `{fmt_cents(frozen_side_bridge.get('delta_vs_target_cents'))}`",
            f"- Skipped net / repair net: `{fmt_cents(skipped.get('net_cents'))}/{fmt_cents(repair.get('net_cents'))}`",
            f"- Blockers: `{', '.join(frozen_side_bridge.get('blockers') or []) or 'none'}`",
        ])
        for note in frozen_side_bridge.get("interpretation") or []:
            lines.append(f"- {note}")
    conservative_fv = entry_watch.get("target_coverage_conservative_fv_summary") or {}
    if conservative_fv:
        best = (conservative_fv.get("ranked") or [{}])[0]
        lines.extend([
            "",
            "### Target-Coverage Conservative FV Variants",
            "",
            "- Diagnostic variants that reduce sharpening in churny mid-confidence rows.",
            f"- Entries/settled/denominator: `{conservative_fv.get('entries')}/{conservative_fv.get('settled')}/{conservative_fv.get('forward_denominator')}`",
            f"- Best variant: `{conservative_fv.get('best_variant')}`",
            f"- Best Brier/logloss mean: `{best.get('brier_mean_delta')}/{best.get('logloss_mean_delta')}`",
            f"- Best Brier/logloss p95: `{(best.get('brier_bootstrap') or {}).get('p95')}/{(best.get('logloss_bootstrap') or {}).get('p95')}`",
        ])
        for row in (conservative_fv.get("ranked") or [])[:4]:
            lines.append(
                f"- `{row.get('variant')}`: brier/logloss mean `{row.get('brier_mean_delta')}/{row.get('logloss_mean_delta')}`, "
                f"p95 `{(row.get('brier_bootstrap') or {}).get('p95')}/{(row.get('logloss_bootstrap') or {}).get('p95')}`, "
                f"blockers `{', '.join(row.get('blockers') or []) or 'none'}`"
            )
    source_split_fv = entry_watch.get("target_coverage_source_split_fv_summary") or {}
    if source_split_fv:
        lines.extend([
            "",
            "### Target-Coverage Source-Split FV",
            "",
            "- Splits target-coverage FV calibration by approved-entry versus rejected-actionable rows.",
            f"- Entries/settled/denominator: `{source_split_fv.get('entries')}/{source_split_fv.get('settled')}/{source_split_fv.get('forward_denominator')}`",
        ])
        for note in source_split_fv.get("interpretation") or []:
            lines.append(f"- {note}")
        for group in source_split_fv.get("source_groups") or []:
            best_group = (group.get("ranked") or [{}])[0]
            lines.append(
                f"- `{group.get('source')}` best `{best_group.get('variant')}`: rows `{group.get('rows')}`, "
                f"Brier/logloss `{best_group.get('brier_mean_delta')}/{best_group.get('logloss_mean_delta')}`, "
                f"neg/pos Brier `{best_group.get('brier_negative_count')}/{best_group.get('brier_positive_count')}`"
            )
    p70_jackknife = entry_watch.get("target_coverage_p70_jackknife_summary") or {}
    if p70_jackknife:
        full = p70_jackknife.get("full") or {}
        worst_brier = p70_jackknife.get("worst_brier") or {}
        worst_logloss = p70_jackknife.get("worst_logloss") or {}
        lines.extend([
            "",
            "### Target-Coverage P70 Jackknife",
            "",
            "- Leave-one-market-out robustness for p70 FV versus raw.",
            f"- Pass/failures: `{p70_jackknife.get('pass')}/{p70_jackknife.get('failure_count')}`",
            f"- Full rows/adjusted: `{full.get('rows')}/{full.get('adjusted')}`",
            f"- Full Brier/logloss: `{full.get('brier_mean_delta')}/{full.get('logloss_mean_delta')}`",
            f"- Worst Brier leave-out: `{worst_brier.get('left_out_market')}` `{worst_brier.get('brier_mean_delta')}`",
            f"- Worst logloss leave-out: `{worst_logloss.get('left_out_market')}` `{worst_logloss.get('logloss_mean_delta')}`",
        ])
    frozen_conservative_fv = entry_watch.get("frozen_target_coverage_conservative_fv_summary") or {}
    if frozen_conservative_fv:
        best = (frozen_conservative_fv.get("ranked") or [{}])[0]
        lines.extend([
            "",
            "### Frozen Target-Coverage Conservative FV",
            "",
            "- Forward-only validator for logit125_p60_calm_mid_or_p75.",
            f"- Freeze timestamp UTC: `{(frozen_conservative_fv.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Future entries/settled/denominator: `{frozen_conservative_fv.get('entries')}/{frozen_conservative_fv.get('settled')}/{frozen_conservative_fv.get('future_denominator')}`",
            f"- Coverage: `{fmt_pct((frozen_conservative_fv.get('coverage_pct') or 0) / 100 if frozen_conservative_fv.get('coverage_pct') is not None else None)}`",
            f"- Best variant: `{frozen_conservative_fv.get('best_variant')}`",
            f"- Best Brier/logloss mean: `{best.get('brier_mean_delta')}/{best.get('logloss_mean_delta')}`",
            f"- Blockers: `{', '.join(best.get('blockers') or []) or 'none'}`",
        ])
    frozen_p70_fv = entry_watch.get("frozen_target_coverage_p70_fv_summary") or {}
    if frozen_p70_fv:
        best = (frozen_p70_fv.get("ranked") or [{}])[0]
        lines.extend([
            "",
            "### Frozen Target-Coverage P70 FV",
            "",
            "- Forward-only validator for high-confidence-only p70 sharpening.",
            f"- Freeze timestamp UTC: `{(frozen_p70_fv.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Future entries/settled/denominator: `{frozen_p70_fv.get('entries')}/{frozen_p70_fv.get('settled')}/{frozen_p70_fv.get('future_denominator')}`",
            f"- Coverage: `{fmt_pct((frozen_p70_fv.get('coverage_pct') or 0) / 100 if frozen_p70_fv.get('coverage_pct') is not None else None)}`",
            f"- Best variant: `{frozen_p70_fv.get('best_variant')}`",
            f"- Best Brier/logloss mean: `{best.get('brier_mean_delta')}/{best.get('logloss_mean_delta')}`",
            f"- Blockers: `{', '.join(best.get('blockers') or []) or 'none'}`",
        ])
    p70_runway = entry_watch.get("frozen_target_coverage_p70_runway_summary") or {}
    if p70_runway:
        lines.extend([
            "",
            "### Frozen Target-Coverage P70 Runway",
            "",
            "- Explains post-freeze p70 denominator markets without selected target-coverage entries.",
            f"- Future denominator/selected/base-seen: `{p70_runway.get('future_denominator')}/{p70_runway.get('selected_entries')}/{p70_runway.get('base_seen_markets')}`",
            f"- Coverage: `{fmt_pct((p70_runway.get('coverage_pct') or 0) / 100 if p70_runway.get('coverage_pct') is not None else None)}`",
        ])
        for note in p70_runway.get("interpretation") or []:
            lines.append(f"- {note}")
        for row in p70_runway.get("markets") or []:
            lines.append(
                f"- `{row.get('market')}` `{row.get('status')}`: base `{row.get('base_row_count')}`, selected `{row.get('selected_row_count')}`"
            )
    p70_eb_runway = entry_watch.get("frozen_target_coverage_p70_empirical_bayes_runway_summary") or {}
    if p70_eb_runway:
        lines.extend([
            "",
            "### Frozen Target-Coverage P70 Empirical-Bayes Runway",
            "",
            "- Explains post-freeze empirical-Bayes p70 denominator markets without selected target-coverage entries.",
            f"- Future denominator/selected/base-seen: `{p70_eb_runway.get('future_denominator')}/{p70_eb_runway.get('selected_entries')}/{p70_eb_runway.get('base_seen_markets')}`",
            f"- Coverage: `{fmt_pct((p70_eb_runway.get('coverage_pct') or 0) / 100 if p70_eb_runway.get('coverage_pct') is not None else None)}`",
        ])
        for note in p70_eb_runway.get("interpretation") or []:
            lines.append(f"- {note}")
        for row in p70_eb_runway.get("markets") or []:
            lines.append(
                f"- `{row.get('market')}` `{row.get('status')}`: base `{row.get('base_row_count')}`, selected `{row.get('selected_row_count')}`"
            )
    p70_pending = entry_watch.get("frozen_target_coverage_p70_pending_sensitivity_summary") or {}
    if p70_pending:
        lines.extend([
            "",
            "### Frozen Target-Coverage P70 Pending Sensitivity",
            "",
            "- Separates raw-only settled rows from pending p70-adjusted rows.",
        ])
        for note in p70_pending.get("interpretation") or []:
            lines.append(f"- {note}")
        for validator in p70_pending.get("validators") or []:
            summary = validator.get("summary") or {}
            lines.append(
                f"- `{validator.get('validator')}`: entries `{validator.get('entries')}`, "
                f"pending-adjusted `{summary.get('pending_adjusted')}`, settled-adjusted `{summary.get('settled_adjusted')}`, "
                f"raw-only losses `{summary.get('settled_raw_only_losses')}`"
            )
    frozen_target_book_gate = entry_watch.get("frozen_target_coverage_book_edge_gate_summary") or {}
    if frozen_target_book_gate:
        candidate = frozen_target_book_gate.get("candidate_summary") or {}
        skipped = frozen_target_book_gate.get("skipped_summary") or {}
        lines.extend([
            "",
            "### Frozen Target-Coverage Book-Edge Gate",
            "",
            "- Future-only broad validator for the raw-over-book overconfidence signal on the target-coverage surface.",
            f"- Freeze timestamp UTC: `{(frozen_target_book_gate.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Denominator/entries/settled: `{frozen_target_book_gate.get('future_denominator')}/{candidate.get('entries')}/{candidate.get('settled')}`",
            f"- Coverage/net/delta: `{candidate.get('coverage_pct')}/{fmt_cents(candidate.get('net_cents'))}/{fmt_cents(frozen_target_book_gate.get('delta_vs_target_cents'))}`",
            f"- Skipped W/L/net: `{skipped.get('wins')}/{skipped.get('losses')}/{fmt_cents(skipped.get('net_cents'))}`",
            f"- Blockers: `{', '.join(frozen_target_book_gate.get('blockers') or []) or 'none'}`",
        ])
    frozen_conservative_pending = entry_watch.get("frozen_target_coverage_conservative_pending_summary") or {}
    if frozen_conservative_pending:
        lines.extend([
            "",
            "### Frozen Conservative FV Pending Sensitivity",
            "",
            "- Shows unresolved frozen conservative FV rows before settlement.",
            f"- Pending rows: `{frozen_conservative_pending.get('pending_count')}`",
        ])
        for note in frozen_conservative_pending.get("interpretation") or []:
            lines.append(f"- {note}")
        for row in frozen_conservative_pending.get("pending_rows") or []:
            win = row.get("if_selected_side_wins") or {}
            loss = row.get("if_selected_side_loses") or {}
            lines.append(
                f"- pending `{row.get('market')}` `{row.get('side')}`: raw/variant/ask/edge/recross "
                f"`{row.get('p_raw')}/{row.get('p_variant')}/{row.get('ask_prob')}/{row.get('raw_edge_prob')}/{row.get('recross_hazard_score')}`, "
                f"if win Brier/logloss d `{win.get('brier_delta')}/{win.get('logloss_delta')}`, "
                f"if loss `{loss.get('brier_delta')}/{loss.get('logloss_delta')}`"
            )
    mid_edge_false_fv = entry_watch.get("frozen_mid_edge_false_conviction_fv_summary") or {}
    if mid_edge_false_fv:
        target_variant = (mid_edge_false_fv.get("freeze") or {}).get("variant")
        ranked = mid_edge_false_fv.get("ranked") or []
        best = next((row for row in ranked if row.get("variant") == target_variant), ranked[0] if ranked else {})
        lines.extend([
            "",
            "### Frozen Mid-Edge False-Conviction FV",
            "",
            "- Forward-only probability shrink for early high-recross 4-8pp edge rows.",
            f"- Freeze timestamp UTC: `{(mid_edge_false_fv.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Future entries/settled/denominator: `{mid_edge_false_fv.get('entries')}/{mid_edge_false_fv.get('settled')}/{mid_edge_false_fv.get('future_denominator')}`",
            f"- Best variant: `{mid_edge_false_fv.get('best_variant')}`",
            f"- Target variant rows/adjusted/false-conviction: `{best.get('rows')}/{best.get('adjusted_rows')}/{best.get('false_conviction_rows')}`",
            f"- Brier/logloss mean: `{best.get('brier_mean_delta')}/{best.get('logloss_mean_delta')}`",
            f"- Blockers: `{', '.join(best.get('blockers') or []) or 'none'}`",
        ])
    composite_false_fv = entry_watch.get("frozen_composite_false_conviction_fv_summary") or {}
    if composite_false_fv:
        target_variant = (composite_false_fv.get("freeze") or {}).get("variant")
        ranked = composite_false_fv.get("ranked") or []
        best = next((row for row in ranked if row.get("variant") == target_variant), ranked[0] if ranked else {})
        lines.extend([
            "",
            "### Frozen Composite False-Conviction FV",
            "",
            "- Forward-only probability shrink for the broader early boundary/recross false-conviction zone.",
            f"- Freeze timestamp UTC: `{(composite_false_fv.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Future entries/settled/denominator: `{composite_false_fv.get('entries')}/{composite_false_fv.get('settled')}/{composite_false_fv.get('future_denominator')}`",
            f"- Best variant: `{composite_false_fv.get('best_variant')}`",
            f"- Target variant rows/adjusted/false-zone: `{best.get('rows')}/{best.get('adjusted_rows')}/{best.get('false_conviction_rows')}`",
            f"- Brier/logloss mean: `{best.get('brier_mean_delta')}/{best.get('logloss_mean_delta')}`",
            f"- Blockers: `{', '.join(best.get('blockers') or []) or 'none'}`",
        ])
    side_asymmetry_runway = entry_watch.get("side_asymmetry_promotion_runway_summary") or {}
    if side_asymmetry_runway:
        lines.extend([
            "",
            "### Side-Asymmetry FV Promotion Runway",
            "",
            "- Tracks whether the small positive calibration lead can mature without overfit.",
            f"- Freeze timestamp UTC: `{side_asymmetry_runway.get('freeze_ts')}`",
            f"- Entries/settled/denominator: `{side_asymmetry_runway.get('entries')}/{side_asymmetry_runway.get('settled')}/{side_asymmetry_runway.get('future_denominator')}`",
            f"- Adjusted clock/side/total: `{side_asymmetry_runway.get('clock_adjusted')}/{side_asymmetry_runway.get('side_adjusted')}/{side_asymmetry_runway.get('adjusted')}`",
            f"- Brier/logloss delta: `{side_asymmetry_runway.get('brier_mean_delta')}/{side_asymmetry_runway.get('logloss_mean_delta')}`",
            f"- Ready for consideration: `{side_asymmetry_runway.get('ready_for_consideration')}`",
        ])
        for row in side_asymmetry_runway.get("checks") or []:
            if not row.get("passed"):
                lines.append(
                    f"- blocker `{row.get('name')}`: actual `{row.get('actual')}`, required `{row.get('required')}`"
                )
    thin_recross_gate = entry_watch.get("frozen_thin_recross_midp_entry_gate_summary") or {}
    if thin_recross_gate:
        base = thin_recross_gate.get("base") or {}
        candidate = thin_recross_gate.get("candidate") or {}
        lines.extend([
            "",
            "### Frozen Thin-Recross Mid-P Entry Gate",
            "",
            "- Forward-only entry-policy candidate for thin-edge high-recross p60-75 rows.",
            f"- Freeze timestamp UTC: `{(thin_recross_gate.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Base entries/settled/net: `{base.get('entries')}/{base.get('settled')}/{fmt_cents(base.get('net_cents'))}`",
            f"- Candidate entries/settled/net: `{candidate.get('entries')}/{candidate.get('settled')}/{fmt_cents(candidate.get('net_cents'))}`",
            f"- Delta net: `{fmt_cents(thin_recross_gate.get('delta_net_cents'))}`; blockers `{', '.join(candidate.get('blockers') or []) or 'none'}`",
        ])
        for note in thin_recross_gate.get("interpretation") or []:
            lines.append(f"- {note}")
        for row in thin_recross_gate.get("skipped_rows") or []:
            lines.append(
                f"- skipped `{row.get('market')}` `{row.get('side')}`: raw/ask/edge/recross "
                f"`{row.get('p_raw')}/{row.get('ask_prob')}/{row.get('raw_edge_prob')}/{row.get('recross_hazard_score')}`, "
                f"won/net `{row.get('side_won')}/{fmt_cents(row.get('net_cents'))}`"
            )
    raw_p52_boundary_skip = entry_watch.get("frozen_raw_p52_boundary_turbulence_skip_summary") or {}
    if raw_p52_boundary_skip:
        base = raw_p52_boundary_skip.get("base") or {}
        candidate = raw_p52_boundary_skip.get("candidate") or {}
        lines.extend([
            "",
            "### Frozen Raw-p52 Boundary-Turbulence Skip",
            "",
            "- Future-only entry-policy candidate for weak raw near-strike high-recross rows.",
            f"- Freeze timestamp UTC: `{(raw_p52_boundary_skip.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Base entries/settled/net: `{base.get('entries')}/{base.get('settled')}/{fmt_cents(base.get('net_cents'))}`",
            f"- Candidate entries/settled/net: `{candidate.get('entries')}/{candidate.get('settled')}/{fmt_cents(candidate.get('net_cents'))}`",
            f"- Delta net: `{fmt_cents(raw_p52_boundary_skip.get('delta_net_cents'))}`; blockers `{', '.join(candidate.get('blockers') or []) or 'none'}`",
        ])
        for note in raw_p52_boundary_skip.get("interpretation") or []:
            lines.append(f"- {note}")
        for row in raw_p52_boundary_skip.get("skipped_rows") or []:
            lines.append(
                f"- skipped `{row.get('market')}` `{row.get('side')}`: raw/ask/edge/abs_d/recross "
                f"`{row.get('p_raw')}/{row.get('ask_prob')}/{row.get('raw_edge_prob')}/{row.get('abs_d_sigma')}/{row.get('recross_hazard_score')}`, "
                f"won/net `{row.get('side_won')}/{fmt_cents(row.get('net_cents'))}`"
            )
    target_loss_repair = entry_watch.get("frozen_target_loss_tag_repair_entry_summary") or {}
    if target_loss_repair:
        target = target_loss_repair.get("target_summary") or {}
        candidate = target_loss_repair.get("candidate_summary") or {}
        lines.extend([
            "",
            "### Frozen Target-Loss Tag Repair Entry",
            "",
            "- Future-only repair candidate for weak-boundary and paid-thin-edge target-coverage loss tags.",
            f"- Freeze timestamp UTC: `{(target_loss_repair.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Target entries/settled/net: `{target.get('entries')}/{target.get('settled')}/{fmt_cents(target.get('net_cents'))}`",
            f"- Candidate entries/settled/net: `{candidate.get('entries')}/{candidate.get('settled')}/{fmt_cents(candidate.get('net_cents'))}`",
            f"- Delta net: `{fmt_cents(target_loss_repair.get('delta_vs_target_cents'))}`; blockers `{', '.join(target_loss_repair.get('blockers') or []) or 'none'}`",
        ])
        for note in target_loss_repair.get("interpretation") or []:
            lines.append(f"- {note}")
    early_no_decay_repair = entry_watch.get("frozen_early_no_boundary_decay_repair_entry_summary") or {}
    if early_no_decay_repair:
        target = early_no_decay_repair.get("target_summary") or {}
        candidate = early_no_decay_repair.get("candidate_summary") or {}
        danger = early_no_decay_repair.get("danger_summary") or {}
        lines.extend([
            "",
            "### Frozen Early NO Boundary-Decay Repair Entry",
            "",
            "- Future-only repair candidate for early NO-side boundary decay and cheap near-boundary turbulence.",
            f"- Freeze timestamp UTC: `{(early_no_decay_repair.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Target entries/settled/net: `{target.get('entries')}/{target.get('settled')}/{fmt_cents(target.get('net_cents'))}`",
            f"- Danger entries/settled/net: `{danger.get('entries')}/{danger.get('settled')}/{fmt_cents(danger.get('net_cents'))}`",
            f"- Candidate entries/settled/net: `{candidate.get('entries')}/{candidate.get('settled')}/{fmt_cents(candidate.get('net_cents'))}`",
            f"- Delta net: `{fmt_cents(early_no_decay_repair.get('delta_vs_target_cents'))}`; blockers `{', '.join(early_no_decay_repair.get('blockers') or []) or 'none'}`",
        ])
        for note in early_no_decay_repair.get("interpretation") or []:
            lines.append(f"- {note}")
    early_no_decay_runway = entry_watch.get("early_no_boundary_decay_repair_runway_summary") or {}
    if early_no_decay_runway:
        candidate = early_no_decay_runway.get("candidate_summary") or {}
        frag = early_no_decay_runway.get("fragility") or {}
        stress = early_no_decay_runway.get("pending_danger_stress") or {}
        lines.extend([
            "",
            "### Early NO Boundary-Decay Repair Runway",
            "",
            "- Promotion runway for the frozen early-NO boundary-decay repair lane.",
            f"- Candidate entries/settled/net/coverage: `{candidate.get('entries')}/{candidate.get('settled')}/{fmt_cents(candidate.get('net_cents'))}/{candidate.get('coverage_pct')}`",
            f"- Rows needed for 30: `{frag.get('rows_needed_for_30')}`",
            f"- Full 100c losses before net flat: `{frag.get('full_100c_losses_before_net_flat')}`",
            f"- Pending danger rows / stressed delta: `{stress.get('pending_danger_rows')}/{fmt_cents(stress.get('stressed_delta_cents'))}`",
            f"- Ready for consideration: `{early_no_decay_runway.get('ready_for_consideration')}`",
        ])
        for note in early_no_decay_runway.get("interpretation") or []:
            lines.append(f"- {note}")
    early_no_decay_stress = entry_watch.get("early_no_boundary_decay_repair_stress_summary") or {}
    if early_no_decay_stress:
        candidate = early_no_decay_stress.get("candidate_summary") or {}
        source_counts = early_no_decay_stress.get("source_counts") or {}
        lines.extend([
            "",
            "### Early NO Boundary-Decay Repair Stress",
            "",
            "- Anti-overfit/source-quality stress for the frozen early-NO boundary-decay repair lane.",
            f"- Candidate settled/net/coverage: `{candidate.get('settled')}/{fmt_cents(candidate.get('net_cents'))}/{candidate.get('coverage_pct')}`",
            f"- Source counts: candidate `{source_counts.get('candidate')}`, danger `{source_counts.get('danger')}`, repair `{source_counts.get('repair')}`",
        ])
        for note in early_no_decay_stress.get("warnings") or []:
            lines.append(f"- warning: {note}")
    mid_edge_repair = entry_watch.get("frozen_mid_edge_boundary_deception_repair_entry_summary") or {}
    if mid_edge_repair:
        target = mid_edge_repair.get("target_summary") or {}
        candidate = mid_edge_repair.get("candidate_summary") or {}
        danger = mid_edge_repair.get("danger_summary") or {}
        lines.extend([
            "",
            "### Frozen Mid-Edge Boundary-Deception Repair Entry",
            "",
            "- Future-only repair candidate for early high-recross 4-8pp edge rows that may be false conviction.",
            f"- Freeze timestamp UTC: `{(mid_edge_repair.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Target entries/settled/net: `{target.get('entries')}/{target.get('settled')}/{fmt_cents(target.get('net_cents'))}`",
            f"- Danger entries/settled/net: `{danger.get('entries')}/{danger.get('settled')}/{fmt_cents(danger.get('net_cents'))}`",
            f"- Candidate entries/settled/net: `{candidate.get('entries')}/{candidate.get('settled')}/{fmt_cents(candidate.get('net_cents'))}`",
            f"- Delta net: `{fmt_cents(mid_edge_repair.get('delta_vs_target_cents'))}`; blockers `{', '.join(mid_edge_repair.get('blockers') or []) or 'none'}`",
        ])
        for note in mid_edge_repair.get("interpretation") or []:
            lines.append(f"- {note}")
    composite_repair = entry_watch.get("frozen_composite_false_conviction_repair_entry_summary") or {}
    if composite_repair:
        target = composite_repair.get("target_summary") or {}
        candidate = composite_repair.get("candidate_summary") or {}
        danger = composite_repair.get("danger_summary") or {}
        repair = composite_repair.get("repair_summary") or {}
        lines.extend([
            "",
            "### Frozen Composite False-Conviction Repair Entry",
            "",
            "- Future-only repair candidate for the broader false-conviction zone using highest raw-p clean replacements.",
            f"- Freeze timestamp UTC: `{(composite_repair.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Target entries/settled/net: `{target.get('entries')}/{target.get('settled')}/{fmt_cents(target.get('net_cents'))}`",
            f"- Danger entries/settled/net: `{danger.get('entries')}/{danger.get('settled')}/{fmt_cents(danger.get('net_cents'))}`",
            f"- Repair entries/settled/net: `{repair.get('entries')}/{repair.get('settled')}/{fmt_cents(repair.get('net_cents'))}`",
            f"- Candidate entries/settled/net: `{candidate.get('entries')}/{candidate.get('settled')}/{fmt_cents(candidate.get('net_cents'))}`",
            f"- Candidate coverage: `{fmt_pct((candidate.get('coverage_pct') or 0) / 100 if candidate.get('coverage_pct') is not None else None)}`",
            f"- Delta net: `{fmt_cents(composite_repair.get('delta_vs_target_cents'))}`; blockers `{', '.join(composite_repair.get('blockers') or []) or 'none'}`",
        ])
        for note in composite_repair.get("interpretation") or []:
            lines.append(f"- {note}")
    goldilocks_edge_repair = entry_watch.get("frozen_goldilocks_edge_repair_entry_summary") or {}
    if goldilocks_edge_repair:
        diagnostic = goldilocks_edge_repair.get("diagnostic") or {}
        future = goldilocks_edge_repair.get("frozen_future") or {}
        diag_target = diagnostic.get("target_summary") or {}
        diag_candidate = diagnostic.get("candidate_summary") or {}
        fut_candidate = future.get("candidate_summary") or {}
        lines.extend([
            "",
            "### Frozen Goldilocks Edge Repair Entry",
            "",
            "- Forward-only candidate for false-conviction edge phases; diagnostic read uses existing target-surface evidence only.",
            f"- Freeze timestamp UTC: `{(goldilocks_edge_repair.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Diagnostic target entries/settled/net: `{diag_target.get('entries')}/{diag_target.get('settled')}/{fmt_cents(diag_target.get('net_cents'))}`",
            f"- Diagnostic candidate entries/settled/coverage/net: `{diag_candidate.get('entries')}/{diag_candidate.get('settled')}/{diag_candidate.get('coverage_pct')}/{fmt_cents(diag_candidate.get('net_cents'))}`",
            f"- Diagnostic delta net: `{fmt_cents(diagnostic.get('delta_vs_target_cents'))}`",
            f"- Frozen future entries/settled/net: `{fut_candidate.get('entries')}/{fut_candidate.get('settled')}/{fmt_cents(fut_candidate.get('net_cents'))}`",
            f"- Frozen blockers: `{', '.join(goldilocks_edge_repair.get('blockers') or []) or 'none'}`",
        ])
        for note in goldilocks_edge_repair.get("interpretation") or []:
            lines.append(f"- {note}")
    false_conviction_family = entry_watch.get("false_conviction_family_scorecard_summary") or {}
    if false_conviction_family:
        lines.extend([
            "",
            "### False-Conviction Family Scorecard",
            "",
            "- Consolidates the current lead direction: early boundary/high-recross rows where FV edge may be false conviction.",
            f"- Integrity-pass candidates: `{false_conviction_family.get('integrity_pass_count')}`",
        ])
        for note in false_conviction_family.get("current_direction") or []:
            lines.append(f"- {note}")
        for row in (false_conviction_family.get("ranked") or [])[:6]:
            lines.append(
                f"- `{row.get('name')}`: mode `{row.get('mode')}`, settled `{row.get('settled')}`, "
                f"W/L `{row.get('wins')}/{row.get('losses')}`, coverage `{row.get('coverage_pct')}`, "
                f"net `{fmt_cents(row.get('net_cents'))}`, recon share `{row.get('reconstructed_share')}`, "
                f"loss cushion `{row.get('full_loss_cushion')}`, pass `{row.get('integrity_pass')}`, "
                f"blockers `{', '.join(row.get('blockers') or []) or 'none'}`"
            )
    source_quality_repair = entry_watch.get("false_conviction_source_quality_repair_summary") or {}
    if source_quality_repair:
        lines.extend([
            "",
            "### False-Conviction Source-Quality Repair",
            "",
            "- Tests whether the lead false-conviction lane can preserve 75%+ coverage while keeping reconstructed evidence under 35%.",
        ])
        for note in source_quality_repair.get("current_read") or []:
            lines.append(f"- {note}")
        for row in source_quality_repair.get("scenarios") or []:
            summary = row.get("candidate_summary") or {}
            lines.append(
                f"- `{row.get('scenario')}`: entries `{summary.get('entries')}`, settled `{summary.get('settled')}`, "
                f"coverage `{summary.get('coverage_pct')}`, net `{fmt_cents(summary.get('net_cents'))}`, "
                f"approved/recon `{row.get('approved_count')}/{row.get('reconstructed_count')}`, "
                f"recon share `{row.get('reconstructed_share')}`, blockers `{', '.join(row.get('blockers') or []) or 'none'}`"
            )
    leaderboard = entry_watch.get("frozen_leaderboard_summary") or {}
    leaderboard_rows = leaderboard.get("ranked") or []
    if leaderboard_rows:
        lines.extend([
            "",
            "### Frozen Candidate Leaderboard",
            "",
            "- Consolidated forward-only view across frozen candidate families.",
        ])
        for row in leaderboard_rows[:6]:
            lines.append(
                f"- `{row.get('gate')}` `{row.get('policy')}`: entries `{row.get('entries')}`, "
                f"settled `{row.get('settled')}`, coverage `{row.get('coverage_pct')}`, "
                f"net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, "
                f"brier `{row.get('avg_brier')}`, live_ready `{row.get('live_ready')}`"
            )
    integrity = entry_watch.get("candidate_integrity_scorecard_summary") or {}
    if integrity:
        lines.extend([
            "",
            "### Candidate Integrity Scorecard",
            "",
            "- Separates positive PnL lanes from lanes with enough sample, source quality, and loss cushion.",
            f"- Positive target-coverage lanes: `{integrity.get('candidate_count')}`",
            f"- Integrity-pass lanes: `{integrity.get('integrity_pass_count')}`",
            f"- Any live-ready candidate: `{integrity.get('any_live_ready')}`",
        ])
        for note in integrity.get("interpretation") or []:
            lines.append(f"- {note}")
        for row in (integrity.get("candidates") or [])[:6]:
            lines.append(
                f"- `{row.get('gate')}` `{row.get('policy')}`: settled `{row.get('settled')}`, "
                f"coverage `{row.get('coverage_pct')}`, net `{fmt_cents(row.get('net_cents'))}`, "
                f"recon share `{row.get('stress_reconstructed_share')}`, loss cushion `{row.get('stress_full_loss_cushion')}`, "
                f"pass `{row.get('integrity_pass')}`, blockers `{', '.join(row.get('blockers') or []) or 'none'}`"
            )
    overlap = entry_watch.get("candidate_vs_control_overlap_summary") or {}
    if overlap:
        base = overlap.get("baseline") or {}
        lines.extend([
            "",
            "### Candidate vs Control Overlap",
            "",
            "- Same-market comparison against `baseline_v28_approved`, plus candidate-only simulated exposure.",
            f"- Baseline entries/settled/W-L/gross: `{base.get('rows')}/{base.get('settled')}/{base.get('wins')}-{base.get('losses')}/{fmt_cents(base.get('gross_cents'))}`",
        ])
        for note in overlap.get("interpretation") or []:
            lines.append(f"- {note}")
        for row in (overlap.get("target_coverage_ranked") or [])[:4]:
            lines.append(
                f"- `{row.get('policy')}`: coverage `{row.get('candidate_coverage_pct')}`, "
                f"gross `{fmt_cents(row.get('candidate_gross_cents'))}`, overlap delta "
                f"`{fmt_cents(row.get('overlap_delta_cents'))}`, sim share `{fmt_pct(row.get('candidate_simulated_share'))}`, "
                f"blockers `{', '.join(row.get('blockers') or []) or 'none'}`"
            )
    live_runway = entry_watch.get("candidate_live_validation_runway_summary") or {}
    if live_runway:
        lines.extend([
            "",
            "### Candidate Live-Validation Runway",
            "",
            "- Estimates future non-simulated evidence needed before shadow candidates are operationally credible.",
        ])
        for note in live_runway.get("interpretation") or []:
            lines.append(f"- {note}")
        for row in (live_runway.get("ranked") or [])[:6]:
            lines.append(
                f"- `{row.get('policy')}`: coverage `{row.get('coverage_pct')}`, "
                f"gross `{fmt_cents(row.get('gross_cents'))}`, sim share `{fmt_pct(row.get('simulated_share'))}`, "
                f"future actual needed `{row.get('future_actual_entries_needed_for_sim_share_lte_35')}`, "
                f"settled needed `{row.get('settled_rows_needed_for_30')}`"
            )
    source_audit = entry_watch.get("broad_book_edge_source_audit_summary") or {}
    if source_audit:
        summary = source_audit.get("summary") or {}
        lines.extend([
            "",
            "### Broad Book-Edge Source Audit",
            "",
            "- Diagnostic-only source/physics check for the current broad book-edge lane.",
            f"- Policy: `{source_audit.get('policy')}`",
            f"- Diagnostic supported: `{source_audit.get('diagnostic_supported')}`",
            f"- Entries/settled/W-L/gross: `{summary.get('entries')}/{summary.get('settled')}/{summary.get('wins')}-{summary.get('losses')}/{fmt_cents(summary.get('gross_cents'))}`",
            f"- Simulated share: `{fmt_pct(source_audit.get('simulated_share'))}`",
            f"- Blockers: `{', '.join(source_audit.get('blockers') or []) or 'none'}`",
        ])
        for row in source_audit.get("source_rows") or []:
            lines.append(
                f"- `{row.get('source')}`: settled `{row.get('settled')}`, "
                f"W-L `{row.get('wins')}-{row.get('losses')}`, gross `{fmt_cents(row.get('gross_cents'))}`"
            )
    book_edge_pending = entry_watch.get("frozen_book_edge_pending_sensitivity_summary") or {}
    if book_edge_pending:
        lines.extend([
            "",
            "### Frozen Book-Edge Pending Sensitivity",
            "",
            "- Pre-settlement raw-vs-book sensitivity for frozen book-edge rows.",
            f"- Pending rows: `{book_edge_pending.get('pending_rows')}`",
            f"- Unique pending markets: `{book_edge_pending.get('unique_pending_markets')}`",
        ])
        for row in book_edge_pending.get("unique_rows") or []:
            win = (row.get("if_win") or [{}])[0]
            loss = (row.get("if_loss") or [{}])[0]
            lines.append(
                f"- `{row.get('market')}` `{row.get('side')}` lanes `{', '.join(str(item) for item in row.get('lanes') or [])}`: "
                f"p/ask/edge `{row.get('p_side')}/{row.get('ask_prob')}/{row.get('edge_cents')}`; "
                f"if win best `{win.get('variant')}` d `{win.get('brier_delta_vs_raw')}/{win.get('logloss_delta_vs_raw')}`, "
                f"if loss best `{loss.get('variant')}` d `{loss.get('brier_delta_vs_raw')}/{loss.get('logloss_delta_vs_raw')}`"
            )
    readiness = entry_watch.get("live_readiness_summary") or {}
    if readiness:
        lines.extend([
            "",
            "### Live Trade Readiness",
            "",
            f"- Any live-ready candidate: `{readiness.get('any_live_ready')}`",
            f"- Control risk stop active: `{readiness.get('control_risk_stop')}`",
        ])
        for row in readiness.get("candidates") or []:
            lines.append(
                f"- `{row.get('gate')}` `{row.get('policy')}`: live_ready `{row.get('live_ready')}`, "
                f"entries `{row.get('entries')}`, settled `{row.get('settled')}`, "
                f"net `{fmt_cents(row.get('net_cents_after_entry_fee'))}`, "
                f"blockers `{', '.join(row.get('blockers') or []) or 'none'}`"
            )
    lines.extend([
        "",
        "## State Watch",
        "",
        f"- Candidate: `{state_watch['candidate']}`",
        f"- Status: `{state_watch['status']}`",
        f"- Reason: {state_watch['reason']}",
    ])
    for row in state_watch.get("rows") or []:
        if row.get("policy") in {"current_v28", state_watch["candidate"], "first_entry_per_market"}:
            lines.append(
                f"- `{row.get('policy')}`: trades `{row.get('trades')}`, gross `{fmt_cents(row.get('gross_cents'))}`, "
                f"delta `{fmt_cents(row.get('delta_vs_current_cents'))}`"
            )
    lines.extend([
        "## FV Watch",
        "",
        f"- Candidate: `{fv_watch['candidate']}`",
        f"- Status: `{fv_watch['status']}`",
        f"- Reason: {fv_watch['reason']}",
    ])
    decay_half_lives = ((fv_watch.get("decay_summary") or {}).get("by_half_life") or {})
    for half_life in ["15", "45", "120", "300"]:
        row = decay_half_lives.get(half_life) or {}
        lines.append(
            f"- Half-life `{half_life}s` retained-current Brier: `{row.get('retained_minus_current_p_brier')}` "
            f"(comparable `{row.get('comparable')}`)"
        )
    state_ranked = (((fv_watch.get("decay_summary") or {}).get("state_variants") or {}).get("ranked") or [])
    if not state_ranked:
        state_ranked = ((((load_json(DECAY_JSON).get("state_variants") or {}).get("ranked")) or []))
    if state_ranked:
        lines.append("- State FV variants by Brier:")
        for row in state_ranked[:4]:
            lines.append(
                f"  - `{row.get('variant')}`: avg_brier `{row.get('avg_brier')}`, "
                f"vs_current `{row.get('brier_minus_current_v28')}`"
            )
    fv_summary = fv_watch.get("fv_variant_summary") or {}
    fv_ranked = fv_summary.get("ranked") or []
    if fv_ranked:
        lines.append("- FV variant robustness:")
        for row in fv_ranked[:4]:
            lines.append(
                f"  - `{row.get('variant')}`: avg_brier `{row.get('avg_brier')}`, "
                f"vs_raw `{row.get('brier_minus_v28_raw')}`"
            )
    fv_views = fv_summary.get("views") or {}
    for view_name in ["source_entry", "first_per_market_side_source", "last_per_market_side_source"]:
        ranked = (fv_views.get(view_name) or {}).get("ranked") or []
        if ranked:
            best = ranked[0]
            lines.append(
                f"- FV view `{view_name}` best: `{best.get('variant')}` "
                f"avg_brier `{best.get('avg_brier')}`, vs_raw `{best.get('brier_minus_v28_raw')}`"
            )
    rmt_summary = fv_watch.get("rmt_regime_summary") or {}
    rmt_tags = rmt_summary.get("by_spectral_tag") or {}
    if rmt_tags:
        lines.append("- RMT spectral regime diagnostic:")
        for tag, bucket in rmt_tags.items():
            scores = bucket.get("variant_scores") or {}
            ranked = sorted(
                (
                    {"variant": name, **score}
                    for name, score in scores.items()
                    if score.get("avg_brier") is not None
                ),
                key=lambda item: (item["avg_brier"], item["variant"]),
            )
            best = ranked[0] if ranked else {}
            lines.append(
                f"  - `{tag}`: obs `{bucket.get('observations')}`, settled `{bucket.get('settled')}`, "
                f"best `{best.get('variant')}`, avg_brier `{best.get('avg_brier')}`, "
                f"vs_raw `{best.get('brier_minus_v28_raw')}`"
            )
        for view_name, bucket in (rmt_summary.get("views") or {}).items():
            if view_name not in {"approved_entries", "first_per_market_side_source", "last_per_market_side_source"}:
                continue
            scores = bucket.get("variant_scores") or {}
            ranked = sorted(
                (
                    {"variant": name, **score}
                    for name, score in scores.items()
                    if score.get("avg_brier") is not None
                ),
                key=lambda item: (item["avg_brier"], item["variant"]),
            )
            best = ranked[0] if ranked else {}
            lines.append(
                f"  - view `{view_name}`: obs `{bucket.get('observations')}`, settled `{bucket.get('settled')}`, "
                f"best `{best.get('variant')}`, avg_brier `{best.get('avg_brier')}`, "
                f"vs_raw `{best.get('brier_minus_v28_raw')}`"
            )
    state_aware = fv_watch.get("state_aware_fv_summary") or {}
    state_ranked_fv = ((state_aware.get("summary") or {}).get("ranked") or [])
    if state_ranked_fv:
        lines.append("- State-aware FV candidates:")
        for row in state_ranked_fv[:4]:
            lines.append(
                f"  - `{row.get('candidate')}`: count `{row.get('count')}`, "
                f"avg_brier `{row.get('avg_brier')}`, vs_raw `{row.get('brier_minus_v28_raw')}`"
            )
        state_views = state_aware.get("views") or {}
        for view_name in ["approved_entries", "first_per_market_side_source", "last_per_market_side_source"]:
            ranked = ((state_views.get(view_name) or {}).get("ranked") or [])
            if ranked:
                best = ranked[0]
                lines.append(
                    f"  - view `{view_name}` best `{best.get('candidate')}`, "
                    f"avg_brier `{best.get('avg_brier')}`, vs_raw `{best.get('brier_minus_v28_raw')}`"
                )
    boundary_memory = entry_watch.get("boundary_memory_fv_summary") or {}
    if boundary_memory:
        lines.extend([
            "",
            "### Boundary-Memory FV Candidates",
            "",
            "- Frozen forward validator for catastrophic-forgetting-style FV overlays.",
            f"- Freeze timestamp UTC: `{boundary_memory.get('freeze_ts')}`",
            f"- Forward denominator: `{boundary_memory.get('forward_denominator')}`",
        ])
        for row in (boundary_memory.get("forward") or [])[:4]:
            lines.append(
                f"- `{row.get('overlay')}`: entries/settled `{row.get('entries')}/{row.get('settled')}`, "
                f"Brier/logloss d `{row.get('brier_delta_vs_raw')}/{row.get('logloss_delta_vs_raw')}`, "
                f"avg p `{row.get('avg_p')}`, blockers `{', '.join(row.get('blockers') or []) or 'none'}`"
            )
    reward_memory = entry_watch.get("reward_memory_fv_summary") or {}
    if reward_memory:
        lines.extend([
            "",
            "### Reward-Memory FV Candidates",
            "",
            "- Frozen forward validator for constrained reward-calibrated FV memory controllers.",
            f"- Freeze timestamp UTC: `{reward_memory.get('freeze_ts')}`",
            f"- Forward denominator: `{reward_memory.get('forward_denominator')}`",
        ])
        for row in (reward_memory.get("forward") or [])[:5]:
            lines.append(
                f"- `{row.get('overlay')}`: entries/settled `{row.get('entries')}/{row.get('settled')}`, "
                f"Brier/logloss d `{row.get('brier_delta_vs_raw')}/{row.get('logloss_delta_vs_raw')}`, "
                f"avg p `{row.get('avg_p')}`, blockers `{', '.join(row.get('blockers') or []) or 'none'}`"
            )
        controllers = reward_memory.get("controllers") or {}
        for name, controller in controllers.items():
            lines.append(
                f"- controller `{name}`: training rows `{controller.get('training_settled_rows')}`, "
                f"objective `{controller.get('objective')}`, weights `{controller.get('weights')}`"
            )
    reward_jackknife = entry_watch.get("reward_memory_jackknife_summary") or {}
    if reward_jackknife:
        lines.extend([
            "",
            "### Reward-Memory Jackknife",
            "",
            "- Leave-one-market-out anti-overfit check for reward-memory FV overlays.",
            f"- Selected/settled/markets: `{reward_jackknife.get('selected_entries')}/{reward_jackknife.get('settled_entries')}/{reward_jackknife.get('markets')}`",
        ])
        for row in reward_jackknife.get("robustness") or []:
            lines.append(
                f"- `{row.get('overlay')}`: pass `{row.get('pass')}`, failures `{row.get('failure_count')}`, "
                f"full Brier/logloss d `{row.get('full_brier_delta_vs_raw')}/{row.get('full_logloss_delta_vs_raw')}`, "
                f"worst Brier d `{row.get('worst_brier_delta_vs_raw')}`"
            )
    decision_matrix = entry_watch.get("fv_decision_matrix_summary") or {}
    if decision_matrix:
        lines.extend([
            "",
            "### FV Candidate Decision Matrix",
            "",
            "- Evidence-ranked comparison across simple posterior, selective memory, boundary memory, and reward memory.",
        ])
        for note in decision_matrix.get("current_read") or []:
            lines.append(f"- {note}")
        for row in (decision_matrix.get("candidate_rows") or [])[:6]:
            lines.append(
                f"- `{row.get('family')}` `{row.get('candidate')}`: fwd `{row.get('forward_entries')}/{row.get('forward_settled')}`, "
                f"coverage `{row.get('forward_coverage_pct')}`, fwd Brier/logloss d "
                f"`{row.get('forward_brier_delta_vs_raw')}/{row.get('forward_logloss_delta_vs_raw')}`, "
                f"disc Brier d `{row.get('discovery_brier_delta_vs_raw')}`, blockers `{', '.join(row.get('blockers') or []) or 'none'}`"
            )
    pending_sensitivity = entry_watch.get("pending_fv_sensitivity_summary") or {}
    if pending_sensitivity:
        lines.extend([
            "",
            "### Pending FV Sensitivity",
            "",
            "- Pre-settlement scoring impact for unresolved forward FV rows.",
            f"- Pending rows: `{pending_sensitivity.get('pending_rows')}`",
        ])
        for row in pending_sensitivity.get("rows") or []:
            lines.append(
                f"- `{row.get('family')}` `{row.get('market')}` `{row.get('side')}`: status/result "
                f"`{row.get('status')}/{row.get('result')}`, raw/ask/edge "
                f"`{row.get('p_raw')}/{row.get('ask_prob')}/{row.get('raw_edge_prob')}`"
            )
            for item in (row.get("overlay_sensitivity") or [])[:4]:
                lines.append(
                    f"  - `{item.get('overlay')}` p `{item.get('p')}`; if win Brier/logloss d "
                    f"`{item.get('if_win_brier_delta_vs_raw')}/{item.get('if_win_logloss_delta_vs_raw')}`, "
                    f"if loss `{item.get('if_loss_brier_delta_vs_raw')}/{item.get('if_loss_logloss_delta_vs_raw')}`"
                )
    anti_overfit = entry_watch.get("anti_overfit_freeze_audit_summary") or {}
    if anti_overfit:
        lines.extend([
            "",
            "### Anti-Overfit Freeze Audit",
            "",
            "- Checks that forward evidence is tied to frozen candidate/state definitions, not moving best-row selection.",
            f"- All clear: `{anti_overfit.get('all_clear')}`; fail/watch counts `{anti_overfit.get('fail_count')}/{anti_overfit.get('watch_count')}`",
        ])
        for row in anti_overfit.get("rows") or []:
            failures = ", ".join(item.get("name") or "" for item in row.get("failures") or []) or "none"
            lines.append(
                f"- `{row.get('artifact')}`: status `{row.get('status')}`, "
                f"freeze `{row.get('freeze_ts')}`, dynamic-best risk `{row.get('dynamic_best_risk')}`, "
                f"failures `{failures}`"
            )
    goal_audit = entry_watch.get("goal_completion_audit_summary") or {}
    if goal_audit:
        missing = goal_audit.get("missing") or []
        lines.extend([
            "",
            "### Goal Completion Audit",
            "",
            "- Strict checklist against the active long-term objective.",
            f"- Achieved: `{goal_audit.get('achieved')}`",
            f"- Missing checks: `{len(missing)}`",
        ])
        for row in missing[:6]:
            lines.append(
                f"- `{row.get('name')}`: actual `{row.get('actual')}`, required `{row.get('required')}`"
            )
        for item in goal_audit.get("next_required_work") or []:
            lines.append(f"- next: {item}")
    lines.extend([
        "- Interpretation: positive retained-current Brier means current/live evidence beat stale retained evidence.",
        "",
        "## Avoid Watch",
        "",
        f"- Status: `{payload['avoid_watch']['status']}`",
        f"- Reason: {payload['avoid_watch']['reason']}",
    ])
    WATCHLIST_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_watchlist()
    WATCHLIST_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(payload)
    print(str(WATCHLIST_MD))


if __name__ == "__main__":
    main()
