"""Decision matrix for v28 FV candidate families.

Research-only; no live bot changes or orders.

The project now has several FV ideas:
- simple posterior lift;
- conditional/logit selective memory;
- boundary-memory catastrophic forgetting;
- reward-calibrated memory.

This artifact compares them by evidence tier, not by cleverness. A candidate
should be preferred only when it has forward evidence, calibration improvement,
coverage fit, and lower or justified complexity.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
RAW_ENTRY_JSON = OUT_DIR / "v28_raw_entry_calibrated_probability_latest.json"
FROZEN_RAW_ENTRY_JSON = OUT_DIR / "v28_frozen_raw_entry_calibrated_probability_latest.json"
OVERLAY_READY_JSON = OUT_DIR / "v28_fv_overlay_challenger_readiness_latest.json"
BOUNDARY_JSON = OUT_DIR / "v28_boundary_memory_fv_candidates_latest.json"
REWARD_JSON = OUT_DIR / "v28_reward_memory_fv_candidates_latest.json"
REWARD_JACKKNIFE_JSON = OUT_DIR / "v28_reward_memory_jackknife_latest.json"
COVERAGE_VALVE_JSON = OUT_DIR / "v28_raw_entry_coverage_valve_latest.json"
APPROVED_ENTRY_BOOK_ROBUSTNESS_JSON = OUT_DIR / "v28_approved_entry_book_fv_robustness_latest.json"
APPROVED_ENTRY_BOOK_RAW_BLEND_JSON = OUT_DIR / "v28_approved_entry_book_raw_blend_latest.json"
FROZEN_APPROVED_ENTRY_BOOK_FV_JSON = OUT_DIR / "v28_frozen_approved_entry_book_fv_latest.json"
APPROVED_ENTRY_BOOK_FV_REGIME_JSON = OUT_DIR / "v28_approved_entry_book_fv_regime_attribution_latest.json"
APPROVED_ENTRY_BOOK_EDGE_ACTIONABILITY_JSON = OUT_DIR / "v28_approved_entry_book_edge_actionability_latest.json"
FROZEN_APPROVED_ENTRY_BOOK_EDGE_GATE_JSON = OUT_DIR / "v28_frozen_approved_entry_book_edge_gate_latest.json"
FROZEN_APPROVED_ENTRY_CONDITIONAL_BOOK_FV_JSON = OUT_DIR / "v28_frozen_approved_entry_conditional_book_fv_latest.json"
TARGET_COVERAGE_FV_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
TARGET_COVERAGE_FV_SEQ_JSON = OUT_DIR / "v28_target_coverage_fv_sequential_evidence_latest.json"
TARGET_COVERAGE_FV_ATTRIBUTION_JSON = OUT_DIR / "v28_target_coverage_fv_attribution_latest.json"
TARGET_COVERAGE_PNL_ATTRIBUTION_JSON = OUT_DIR / "v28_target_coverage_pnl_attribution_latest.json"
DANGER_ZONE_FV_JSON = OUT_DIR / "v28_danger_zone_fv_calibration_latest.json"
FROZEN_DANGER_ZONE_FV_JSON = OUT_DIR / "v28_frozen_danger_zone_fv_calibration_latest.json"
DANGER_ZONE_ROBUSTNESS_JSON = OUT_DIR / "v28_danger_zone_robustness_audit_latest.json"
TARGET_CONSERVATIVE_FV_JSON = OUT_DIR / "v28_target_coverage_conservative_fv_variants_latest.json"
FROZEN_TARGET_CONSERVATIVE_FV_JSON = OUT_DIR / "v28_frozen_target_coverage_conservative_fv_latest.json"
FROZEN_TARGET_P70_FV_JSON = OUT_DIR / "v28_frozen_target_coverage_p70_fv_latest.json"
TARGET_P70_JACKKNIFE_JSON = OUT_DIR / "v28_target_coverage_p70_jackknife_latest.json"
TARGET_P70_SEQ_JSON = OUT_DIR / "v28_target_coverage_p70_sequential_evidence_latest.json"
TARGET_CONFIDENCE_TEMP_JSON = OUT_DIR / "v28_target_coverage_confidence_temperature_bakeoff_latest.json"
TARGET_P70_FRAGILITY_JSON = OUT_DIR / "v28_target_coverage_p70_fragility_stress_latest.json"
TARGET_P70_SCALE_JSON = OUT_DIR / "v28_target_coverage_p70_scale_bakeoff_latest.json"
TARGET_P70_EMPIRICAL_BAYES_JSON = OUT_DIR / "v28_target_coverage_p70_empirical_bayes_latest.json"
TARGET_SOURCE_SPLIT_JSON = OUT_DIR / "v28_target_coverage_source_split_fv_latest.json"
FROZEN_TARGET_P70_RUNWAY_JSON = OUT_DIR / "v28_frozen_target_coverage_p70_runway_latest.json"
FROZEN_TARGET_P70_EB_RUNWAY_JSON = OUT_DIR / "v28_frozen_target_coverage_p70_empirical_bayes_runway_latest.json"
FROZEN_TARGET_P70_QUALITY_JSON = OUT_DIR / "v28_frozen_target_coverage_p70_quality_registry_latest.json"
FROZEN_TARGET_P70_PENDING_JSON = OUT_DIR / "v28_frozen_target_coverage_p70_pending_sensitivity_latest.json"
FROZEN_TARGET_COVERAGE_BOOK_EDGE_GATE_JSON = OUT_DIR / "v28_frozen_target_coverage_book_edge_gate_latest.json"
FROZEN_PATH_STATE_P70_JSON = OUT_DIR / "v28_frozen_path_state_p70_fv_latest.json"
FROZEN_BOUNDARY_RECROSS_SHRINK_JSON = OUT_DIR / "v28_frozen_boundary_recross_shrink_fv_latest.json"
FROZEN_EDGE_PHASE_SHRINK_JSON = OUT_DIR / "v28_frozen_edge_phase_shrink_fv_latest.json"
BOUNDARY_REVERSAL_JSON = OUT_DIR / "v28_boundary_reversal_opportunity_latest.json"
DANGER_TAG_REPLACEMENT_JSON = OUT_DIR / "v28_danger_tag_replacement_diagnostic_latest.json"
COVERAGE_REPAIR_POOL_JSON = OUT_DIR / "v28_coverage_repair_pool_diagnostic_latest.json"
DANGER_REPAIR_BAKEOFF_JSON = OUT_DIR / "v28_danger_repair_bakeoff_latest.json"
REPAIR_SCORING_BAKEOFF_JSON = OUT_DIR / "v28_repair_scoring_bakeoff_latest.json"
BOUNDARY_CLOCK_HAZARD_REPAIR_JSON = OUT_DIR / "v28_boundary_clock_hazard_repair_latest.json"
BOUNDARY_CLOCK_ROBUSTNESS_JSON = OUT_DIR / "v28_boundary_clock_robustness_audit_latest.json"
BOUNDARY_CLOCK_FV_OVERLAY_JSON = OUT_DIR / "v28_boundary_clock_fv_overlay_latest.json"
BOUNDARY_CLOCK_FV_ROBUSTNESS_JSON = OUT_DIR / "v28_boundary_clock_fv_robustness_latest.json"
BOUNDARY_CLOCK_RESIDUAL_JSON = OUT_DIR / "v28_boundary_clock_residual_attribution_latest.json"
FROZEN_BOUNDARY_CLOCK_RESIDUAL_REGISTRY_JSON = OUT_DIR / "v28_frozen_boundary_clock_residual_registry_latest.json"
SIDE_ASYMMETRY_FV_DIAGNOSTIC_JSON = OUT_DIR / "v28_side_asymmetry_fv_diagnostic_latest.json"
FROZEN_SIDE_ASYMMETRY_REGISTRY_JSON = OUT_DIR / "v28_frozen_side_asymmetry_registry_latest.json"
SIDE_ASYMMETRY_FV_OVERLAY_JSON = OUT_DIR / "v28_side_asymmetry_fv_overlay_latest.json"
FROZEN_SIDE_ASYMMETRY_FV_OVERLAY_JSON = OUT_DIR / "v28_frozen_side_asymmetry_fv_overlay_latest.json"
FROZEN_SIDE_ASYMMETRY_ENTRY_BRIDGE_JSON = OUT_DIR / "v28_frozen_side_asymmetry_entry_bridge_latest.json"
BOUNDARY_CLOCK_PROMOTION_RUNWAY_JSON = OUT_DIR / "v28_boundary_clock_promotion_runway_latest.json"
BOUNDARY_CLOCK_FV_ENTRY_BRIDGE_JSON = OUT_DIR / "v28_boundary_clock_fv_entry_bridge_latest.json"
TARGET_FV_EDGE_GATE_JSON = OUT_DIR / "v28_target_coverage_fv_edge_gate_diagnostic_latest.json"
EDGE_GATE_OPPOSITE_JSON = OUT_DIR / "v28_edge_gate_opposite_side_diagnostic_latest.json"
FROZEN_EDGE_PHASE_EDGE_GATE_JSON = OUT_DIR / "v28_frozen_edge_phase_edge_gate_latest.json"
FROZEN_EDGE_GATE_OPPOSITE_JSON = OUT_DIR / "v28_frozen_edge_gate_opposite_side_latest.json"
FROZEN_LOW_RECROSS_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_low_recross_repair_entry_latest.json"
FROZEN_HIGH_RAW_P_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_high_raw_p_repair_entry_latest.json"
FROZEN_BOUNDARY_CLOCK_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_boundary_clock_repair_entry_latest.json"
FROZEN_BOUNDARY_CLOCK_FV_OVERLAY_JSON = OUT_DIR / "v28_frozen_boundary_clock_fv_overlay_latest.json"
FROZEN_BOUNDARY_CLOCK_FV_ENTRY_BRIDGE_JSON = OUT_DIR / "v28_frozen_boundary_clock_fv_entry_bridge_latest.json"
RAW_P52_BOOK_DISAGREEMENT_SKIP_JSON = OUT_DIR / "v28_raw_p52_book_disagreement_skip_latest.json"
FROZEN_RAW_P52_BOOK_DISAGREEMENT_SKIP_JSON = OUT_DIR / "v28_frozen_raw_p52_book_disagreement_skip_latest.json"
RAW_P52_BOOK_SHRINK_ENTRY_JSON = OUT_DIR / "v28_raw_p52_book_shrink_entry_latest.json"
FROZEN_RAW_P52_BOOK_SHRINK_ENTRY_JSON = OUT_DIR / "v28_frozen_raw_p52_book_shrink_entry_latest.json"
BOOK_DISAGREEMENT_REPLACEMENT_JSON = OUT_DIR / "v28_book_disagreement_replacement_attribution_latest.json"
RAW_P52_EARLY_NO_BOUNDARY_BAND_JSON = OUT_DIR / "v28_raw_p52_early_no_boundary_band_skip_latest.json"
FROZEN_RAW_P52_EARLY_NO_BOUNDARY_BAND_JSON = OUT_DIR / "v28_frozen_raw_p52_early_no_boundary_band_skip_latest.json"
RAW_P52_EARLY_NO_BOUNDARY_BAND_ROBUSTNESS_JSON = OUT_DIR / "v28_raw_p52_early_no_boundary_band_robustness_latest.json"
RAW_P52_EARLY_NO_BOUNDARY_BAND_RUNWAY_JSON = OUT_DIR / "v28_raw_p52_early_no_boundary_band_runway_latest.json"
BOUNDARY_ENTROPY_FV_JSON = OUT_DIR / "v28_boundary_entropy_fv_latest.json"
EARLY_NO_BOUNDARY_DECAY_REPAIR_RUNWAY_JSON = OUT_DIR / "v28_early_no_boundary_decay_repair_runway_latest.json"
OUT_JSON = OUT_DIR / "v28_fv_candidate_decision_matrix_latest.json"
OUT_MD = OUT_DIR / "v28_fv_candidate_decision_matrix_latest.md"

TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0
MIN_FORWARD_SETTLED = 30


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


def by_overlay(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("overlay") or ""): row for row in rows if row.get("overlay")}


def coverage_fit(coverage: Any) -> str:
    value = as_float(coverage)
    if value is None:
        return "unknown"
    if value < TARGET_COVERAGE_MIN:
        return "low"
    if value > TARGET_COVERAGE_MAX:
        return "high"
    return "target"


def candidate_score(row: dict[str, Any]) -> tuple[int, float, float, int]:
    """Sort key: lower is better."""
    forward_settled = int(as_float(row.get("forward_settled")) or 0)
    readyish = 0 if row.get("forward_brier_delta_vs_raw") is not None and as_float(row.get("forward_brier_delta_vs_raw")) < 0 else 1
    settled_penalty = max(0, MIN_FORWARD_SETTLED - forward_settled)
    complexity = int(as_float(row.get("complexity")) or 9)
    brier = as_float(row.get("forward_brier_delta_vs_raw"))
    disc = as_float(row.get("discovery_brier_delta_vs_raw"))
    return (
        readyish,
        settled_penalty,
        brier if brier is not None else 999.0,
        complexity,
        disc if disc is not None else 999.0,
    )


def build_report() -> dict[str, Any]:
    raw_entry = load_json(RAW_ENTRY_JSON)
    frozen = load_json(FROZEN_RAW_ENTRY_JSON)
    overlay_ready = load_json(OVERLAY_READY_JSON)
    boundary = load_json(BOUNDARY_JSON)
    reward = load_json(REWARD_JSON)
    reward_jackknife = load_json(REWARD_JACKKNIFE_JSON)
    coverage_valve = load_json(COVERAGE_VALVE_JSON)
    approved_book_robustness = load_json(APPROVED_ENTRY_BOOK_ROBUSTNESS_JSON)
    approved_book_raw_blend = load_json(APPROVED_ENTRY_BOOK_RAW_BLEND_JSON)
    frozen_approved_entry_book_fv = load_json(FROZEN_APPROVED_ENTRY_BOOK_FV_JSON)
    approved_book_regime = load_json(APPROVED_ENTRY_BOOK_FV_REGIME_JSON)
    approved_book_edge_actionability = load_json(APPROVED_ENTRY_BOOK_EDGE_ACTIONABILITY_JSON)
    frozen_approved_book_edge_gate = load_json(FROZEN_APPROVED_ENTRY_BOOK_EDGE_GATE_JSON)
    frozen_approved_conditional_book_fv = load_json(FROZEN_APPROVED_ENTRY_CONDITIONAL_BOOK_FV_JSON)
    target_coverage_fv = load_json(TARGET_COVERAGE_FV_JSON)
    target_coverage_seq = load_json(TARGET_COVERAGE_FV_SEQ_JSON)
    target_coverage_attr = load_json(TARGET_COVERAGE_FV_ATTRIBUTION_JSON)
    target_coverage_pnl_attr = load_json(TARGET_COVERAGE_PNL_ATTRIBUTION_JSON)
    danger_zone_fv = load_json(DANGER_ZONE_FV_JSON)
    frozen_danger_zone_fv = load_json(FROZEN_DANGER_ZONE_FV_JSON)
    danger_zone_robustness = load_json(DANGER_ZONE_ROBUSTNESS_JSON)
    target_conservative_fv = load_json(TARGET_CONSERVATIVE_FV_JSON)
    frozen_target_conservative_fv = load_json(FROZEN_TARGET_CONSERVATIVE_FV_JSON)
    frozen_target_p70_fv = load_json(FROZEN_TARGET_P70_FV_JSON)
    target_p70_jackknife = load_json(TARGET_P70_JACKKNIFE_JSON)
    target_p70_seq = load_json(TARGET_P70_SEQ_JSON)
    target_confidence_temp = load_json(TARGET_CONFIDENCE_TEMP_JSON)
    target_p70_fragility = load_json(TARGET_P70_FRAGILITY_JSON)
    target_p70_scale = load_json(TARGET_P70_SCALE_JSON)
    target_p70_empirical_bayes = load_json(TARGET_P70_EMPIRICAL_BAYES_JSON)
    target_source_split = load_json(TARGET_SOURCE_SPLIT_JSON)
    frozen_target_p70_runway = load_json(FROZEN_TARGET_P70_RUNWAY_JSON)
    frozen_target_p70_eb_runway = load_json(FROZEN_TARGET_P70_EB_RUNWAY_JSON)
    frozen_target_p70_quality = load_json(FROZEN_TARGET_P70_QUALITY_JSON)
    frozen_target_p70_pending = load_json(FROZEN_TARGET_P70_PENDING_JSON)
    frozen_target_book_edge_gate = load_json(FROZEN_TARGET_COVERAGE_BOOK_EDGE_GATE_JSON)
    frozen_path_state_p70 = load_json(FROZEN_PATH_STATE_P70_JSON)
    frozen_boundary_recross = load_json(FROZEN_BOUNDARY_RECROSS_SHRINK_JSON)
    frozen_edge_phase = load_json(FROZEN_EDGE_PHASE_SHRINK_JSON)
    boundary_reversal = load_json(BOUNDARY_REVERSAL_JSON)
    danger_tag_replacement = load_json(DANGER_TAG_REPLACEMENT_JSON)
    coverage_repair_pool = load_json(COVERAGE_REPAIR_POOL_JSON)
    danger_repair_bakeoff = load_json(DANGER_REPAIR_BAKEOFF_JSON)
    repair_scoring_bakeoff = load_json(REPAIR_SCORING_BAKEOFF_JSON)
    boundary_clock_hazard_repair = load_json(BOUNDARY_CLOCK_HAZARD_REPAIR_JSON)
    boundary_clock_robustness = load_json(BOUNDARY_CLOCK_ROBUSTNESS_JSON)
    boundary_clock_fv_overlay = load_json(BOUNDARY_CLOCK_FV_OVERLAY_JSON)
    boundary_clock_fv_robustness = load_json(BOUNDARY_CLOCK_FV_ROBUSTNESS_JSON)
    boundary_clock_residual = load_json(BOUNDARY_CLOCK_RESIDUAL_JSON)
    frozen_boundary_clock_residual_registry = load_json(FROZEN_BOUNDARY_CLOCK_RESIDUAL_REGISTRY_JSON)
    side_asymmetry = load_json(SIDE_ASYMMETRY_FV_DIAGNOSTIC_JSON)
    frozen_side_asymmetry_registry = load_json(FROZEN_SIDE_ASYMMETRY_REGISTRY_JSON)
    side_asymmetry_overlay = load_json(SIDE_ASYMMETRY_FV_OVERLAY_JSON)
    frozen_side_asymmetry_fv_overlay = load_json(FROZEN_SIDE_ASYMMETRY_FV_OVERLAY_JSON)
    frozen_side_asymmetry_entry_bridge = load_json(FROZEN_SIDE_ASYMMETRY_ENTRY_BRIDGE_JSON)
    boundary_clock_promotion_runway = load_json(BOUNDARY_CLOCK_PROMOTION_RUNWAY_JSON)
    boundary_clock_fv_entry_bridge = load_json(BOUNDARY_CLOCK_FV_ENTRY_BRIDGE_JSON)
    target_fv_edge_gate = load_json(TARGET_FV_EDGE_GATE_JSON)
    edge_gate_opposite = load_json(EDGE_GATE_OPPOSITE_JSON)
    frozen_edge_phase_edge_gate = load_json(FROZEN_EDGE_PHASE_EDGE_GATE_JSON)
    frozen_edge_gate_opposite = load_json(FROZEN_EDGE_GATE_OPPOSITE_JSON)
    frozen_low_recross_repair = load_json(FROZEN_LOW_RECROSS_REPAIR_ENTRY_JSON)
    frozen_high_raw_p_repair = load_json(FROZEN_HIGH_RAW_P_REPAIR_ENTRY_JSON)
    frozen_boundary_clock_repair = load_json(FROZEN_BOUNDARY_CLOCK_REPAIR_ENTRY_JSON)
    frozen_boundary_clock_fv = load_json(FROZEN_BOUNDARY_CLOCK_FV_OVERLAY_JSON)
    frozen_boundary_clock_fv_entry_bridge = load_json(FROZEN_BOUNDARY_CLOCK_FV_ENTRY_BRIDGE_JSON)

    discovery_rows = by_overlay(raw_entry.get("ranked") if isinstance(raw_entry.get("ranked"), list) else [])
    frozen_rows = by_overlay(frozen.get("ranked") if isinstance(frozen.get("ranked"), list) else [])
    ready_rows = {
        str(item.get("overlay") or ""): item
        for item in (overlay_ready.get("candidates") if isinstance(overlay_ready.get("candidates"), list) else [])
    }
    boundary_disc = by_overlay(boundary.get("discovery") if isinstance(boundary.get("discovery"), list) else [])
    boundary_fwd = by_overlay(boundary.get("forward") if isinstance(boundary.get("forward"), list) else [])
    reward_disc = by_overlay(reward.get("discovery") if isinstance(reward.get("discovery"), list) else [])
    reward_fwd = by_overlay(reward.get("forward") if isinstance(reward.get("forward"), list) else [])
    jack = {
        str(row.get("overlay") or ""): row
        for row in (reward_jackknife.get("robustness") if isinstance(reward_jackknife.get("robustness"), list) else [])
    }

    rows: list[dict[str, Any]] = []

    for overlay, complexity, family, note in [
        ("entry_conditioned_plus05_probability", 1, "simple_posterior", "Simple +5pp posterior lift on fixed raw-v28 entries."),
        ("entry_conditioned_logit125_p60_only_probability", 2, "selective_memory", "Forget weak p<60 rows, sharpen only stronger raw FV."),
        ("entry_conditioned_logit125_probability", 2, "selective_memory", "Sharpen raw FV everywhere."),
        ("noise_shrink_light_probability", 2, "rmt_shrink", "Shrink noisy/RMT rows toward 50."),
        ("book_probability", 1, "book_anchor", "Use executable book as probability."),
    ]:
        disc = discovery_rows.get(overlay, {})
        fwd = frozen_rows.get(overlay, {})
        ready = ready_rows.get(overlay, {})
        rows.append({
            "family": family,
            "candidate": overlay,
            "complexity": complexity,
            "note": note,
            "freeze_ts": frozen.get("freeze_ts"),
            "forward_entries": fwd.get("entries"),
            "forward_settled": fwd.get("settled"),
            "forward_coverage_pct": fwd.get("coverage_pct"),
            "coverage_fit": coverage_fit(fwd.get("coverage_pct")),
            "forward_brier_delta_vs_raw": fwd.get("brier_delta_vs_raw"),
            "forward_logloss_delta_vs_raw": fwd.get("logloss_delta_vs_raw"),
            "discovery_brier_delta_vs_raw": disc.get("brier_delta_vs_raw"),
            "discovery_logloss_delta_vs_raw": disc.get("logloss_delta_vs_raw"),
            "jackknife_pass": None,
            "blockers": ready.get("blockers") or fwd.get("blockers") or [],
        })

    for overlay, complexity, note in [
        ("boundary_memory_plus05", 3, "Physics-declared retention erases most adjustment in weak/thin/turbulent boundary states."),
        ("boundary_memory_logit125", 3, "Physics-declared retention on logit sharpening."),
        ("conditional_logit125_p60_only", 2, "Boundary report's conditional logit control."),
    ]:
        disc = boundary_disc.get(overlay, {})
        fwd = boundary_fwd.get(overlay, {})
        rows.append({
            "family": "boundary_memory",
            "candidate": overlay,
            "complexity": complexity,
            "note": note,
            "freeze_ts": boundary.get("freeze_ts"),
            "forward_entries": fwd.get("entries"),
            "forward_settled": fwd.get("settled"),
            "forward_coverage_pct": fwd.get("coverage_pct"),
            "coverage_fit": coverage_fit(fwd.get("coverage_pct")),
            "forward_brier_delta_vs_raw": fwd.get("brier_delta_vs_raw"),
            "forward_logloss_delta_vs_raw": fwd.get("logloss_delta_vs_raw"),
            "discovery_brier_delta_vs_raw": disc.get("brier_delta_vs_raw"),
            "discovery_logloss_delta_vs_raw": disc.get("logloss_delta_vs_raw"),
            "jackknife_pass": None,
            "blockers": fwd.get("blockers") or [],
        })

    for overlay, complexity, note in [
        ("plus05_probability", 1, "Reward report control: plain +5pp."),
        ("reward_memory_plus05", 4, "Tiny reward-calibrated retention controller for +5pp."),
        ("reward_memory_logit125", 4, "Tiny reward-calibrated retention controller for logit sharpening."),
        ("logit125_probability", 2, "Reward report control: plain logit sharpening."),
    ]:
        disc = reward_disc.get(overlay, {})
        fwd = reward_fwd.get(overlay, {})
        jack_row = jack.get(overlay, {})
        rows.append({
            "family": "reward_memory",
            "candidate": overlay,
            "complexity": complexity,
            "note": note,
            "freeze_ts": reward.get("freeze_ts"),
            "forward_entries": fwd.get("entries"),
            "forward_settled": fwd.get("settled"),
            "forward_coverage_pct": fwd.get("coverage_pct"),
            "coverage_fit": coverage_fit(fwd.get("coverage_pct")),
            "forward_brier_delta_vs_raw": fwd.get("brier_delta_vs_raw"),
            "forward_logloss_delta_vs_raw": fwd.get("logloss_delta_vs_raw"),
            "discovery_brier_delta_vs_raw": disc.get("brier_delta_vs_raw"),
            "discovery_logloss_delta_vs_raw": disc.get("logloss_delta_vs_raw"),
            "jackknife_pass": jack_row.get("pass"),
            "jackknife_worst_brier_delta_vs_raw": jack_row.get("worst_brier_delta_vs_raw"),
            "blockers": fwd.get("blockers") or [],
        })

    approved_book_candidate = frozen_approved_entry_book_fv.get("candidate") or {}
    approved_book_blend_best = approved_book_raw_blend.get("best") or {}
    rows.append({
        "family": "approved_entry_book_fv",
        "candidate": "book_probability_on_actual_approved_entries",
        "complexity": 1,
        "note": "Actual-approved FV calibration challenger: v28 may select direction while executable book is the better calibrated probability anchor.",
        "freeze_ts": (frozen_approved_entry_book_fv.get("freeze") or {}).get("freeze_ts_utc"),
        "forward_entries": frozen_approved_entry_book_fv.get("future_entries"),
        "forward_settled": frozen_approved_entry_book_fv.get("future_settled"),
        "forward_coverage_pct": None,
        "coverage_fit": "actual-approved-only",
        "forward_brier_delta_vs_raw": approved_book_candidate.get("brier_delta_vs_raw"),
        "forward_logloss_delta_vs_raw": approved_book_candidate.get("logloss_delta_vs_raw"),
        "discovery_brier_delta_vs_raw": None,
        "discovery_logloss_delta_vs_raw": None,
        "jackknife_pass": None,
        "blockers": approved_book_candidate.get("blockers")
        if "blockers" in approved_book_candidate
        else ["settled_lt_30"],
    })
    rows.append({
        "family": "approved_entry_book_raw_blend",
        "candidate": f"book_plus_alpha_raw_memory_alpha_{approved_book_blend_best.get('alpha_raw_weight')}",
        "complexity": 2,
        "note": "Diagnostic blend p = book + alpha * (raw - book); tests whether raw v28 adds useful residual memory after executable-book anchoring.",
        "freeze_ts": None,
        "forward_entries": approved_book_blend_best.get("rows"),
        "forward_settled": approved_book_blend_best.get("rows"),
        "forward_coverage_pct": None,
        "coverage_fit": "actual-approved-diagnostic",
        "forward_brier_delta_vs_raw": approved_book_blend_best.get("brier_delta_vs_raw"),
        "forward_logloss_delta_vs_raw": approved_book_blend_best.get("logloss_delta_vs_raw"),
        "discovery_brier_delta_vs_raw": approved_book_blend_best.get("brier_delta_vs_raw"),
        "discovery_logloss_delta_vs_raw": approved_book_blend_best.get("logloss_delta_vs_raw"),
        "jackknife_pass": len(approved_book_raw_blend.get("best_leave_one_failures") or []) == 0 if approved_book_raw_blend else None,
        "blockers": approved_book_raw_blend.get("blockers") or [],
    })
    book_action_useful = approved_book_edge_actionability.get("useful") or []
    book_action_best = book_action_useful[0] if book_action_useful else {}
    book_action_retained = book_action_best.get("retained") or {}
    rows.append({
        "family": "approved_entry_book_edge_actionability",
        "candidate": book_action_best.get("policy") or "none",
        "complexity": 2,
        "note": "Actual-approved entry actionability: skip entries only when raw overconfidence is contradicted by a weak executable-book edge.",
        "freeze_ts": (approved_book_edge_actionability.get("freeze") or {}).get("freeze_ts_utc"),
        "forward_entries": book_action_retained.get("entries"),
        "forward_settled": book_action_retained.get("settled"),
        "forward_coverage_pct": book_action_retained.get("coverage_pct"),
        "coverage_fit": coverage_fit(book_action_retained.get("coverage_pct")),
        "forward_brier_delta_vs_raw": None,
        "forward_logloss_delta_vs_raw": None,
        "discovery_brier_delta_vs_raw": None,
        "discovery_logloss_delta_vs_raw": None,
        "jackknife_pass": None,
        "forward_net_cents": book_action_retained.get("net_cents"),
        "forward_delta_net_cents": book_action_best.get("delta_net_vs_keep_all_cents"),
        "blockers": (book_action_best.get("blockers") or ["entry_actionability_not_fv_calibration"])
        if book_action_best
        else ["no_useful_policy"],
    })
    frozen_book_gate_candidate = frozen_approved_book_edge_gate.get("candidate") or {}
    rows.append({
        "family": "frozen_approved_entry_book_edge_gate",
        "candidate": (frozen_approved_book_edge_gate.get("freeze") or {}).get("candidate")
        or "skip_discount15_book_edge_lt_5pp",
        "complexity": 2,
        "note": "Future-only validator for the fixed actual-approved book-edge skip rule.",
        "freeze_ts": (frozen_approved_book_edge_gate.get("freeze") or {}).get("freeze_ts_utc"),
        "forward_entries": frozen_approved_book_edge_gate.get("future_entries"),
        "forward_settled": frozen_book_gate_candidate.get("settled"),
        "forward_coverage_pct": frozen_book_gate_candidate.get("coverage_pct"),
        "coverage_fit": coverage_fit(frozen_book_gate_candidate.get("coverage_pct")),
        "forward_brier_delta_vs_raw": None,
        "forward_logloss_delta_vs_raw": None,
        "discovery_brier_delta_vs_raw": None,
        "discovery_logloss_delta_vs_raw": None,
        "jackknife_pass": None,
        "forward_net_cents": frozen_book_gate_candidate.get("net_cents"),
        "forward_delta_net_cents": frozen_approved_book_edge_gate.get("delta_net_vs_control_cents"),
        "blockers": frozen_approved_book_edge_gate.get("blockers") or ["settled_lt_30"],
    })
    broad_book_gate_candidate = frozen_target_book_edge_gate.get("candidate_summary") or {}
    rows.append({
        "family": "frozen_target_coverage_book_edge_gate",
        "candidate": (frozen_target_book_edge_gate.get("freeze") or {}).get("candidate")
        or "target_coverage_skip_raw_edge_ge_15pp",
        "complexity": 2,
        "note": "Future-only broad target-coverage validator for the raw-over-book overconfidence skip.",
        "freeze_ts": (frozen_target_book_edge_gate.get("freeze") or {}).get("freeze_ts_utc"),
        "forward_entries": broad_book_gate_candidate.get("entries"),
        "forward_settled": broad_book_gate_candidate.get("settled"),
        "forward_coverage_pct": broad_book_gate_candidate.get("coverage_pct"),
        "coverage_fit": coverage_fit(broad_book_gate_candidate.get("coverage_pct")),
        "forward_brier_delta_vs_raw": None,
        "forward_logloss_delta_vs_raw": None,
        "discovery_brier_delta_vs_raw": None,
        "discovery_logloss_delta_vs_raw": None,
        "jackknife_pass": None,
        "forward_net_cents": broad_book_gate_candidate.get("net_cents"),
        "forward_delta_net_cents": frozen_target_book_edge_gate.get("delta_vs_target_cents"),
        "blockers": frozen_target_book_edge_gate.get("blockers") or ["settled_lt_30"],
    })
    conditional_future = frozen_approved_conditional_book_fv.get("future") or {}
    conditional_candidate = conditional_future.get("candidate") or {}
    conditional_prefreeze = (frozen_approved_conditional_book_fv.get("prefreeze_context") or {}).get("candidate") or {}
    rows.append({
        "family": "approved_entry_conditional_book_fv",
        "candidate": "conditional_book_no_late_discount",
        "complexity": 3,
        "note": "Frozen actual-approved FV: use book as humility anchor only for NO, late, or raw-minus-book >=10pp rows; otherwise keep raw conviction.",
        "freeze_ts": (frozen_approved_conditional_book_fv.get("freeze") or {}).get("freeze_ts_utc"),
        "forward_entries": conditional_future.get("entries"),
        "forward_settled": conditional_future.get("settled"),
        "forward_coverage_pct": None,
        "coverage_fit": "actual-approved-only",
        "forward_brier_delta_vs_raw": conditional_candidate.get("brier_delta_vs_raw"),
        "forward_logloss_delta_vs_raw": conditional_candidate.get("logloss_delta_vs_raw"),
        "discovery_brier_delta_vs_raw": conditional_prefreeze.get("brier_delta_vs_raw"),
        "discovery_logloss_delta_vs_raw": conditional_prefreeze.get("logloss_delta_vs_raw"),
        "jackknife_pass": None,
        "blockers": conditional_candidate.get("blockers") or ["settled_lt_30"],
    })

    danger_discovery = by_overlay(danger_zone_fv.get("ranked") if isinstance(danger_zone_fv.get("ranked"), list) else [])
    danger_forward = by_overlay(frozen_danger_zone_fv.get("ranked") if isinstance(frozen_danger_zone_fv.get("ranked"), list) else [])
    for overlay, complexity, note in [
        ("danger_to_book", 2, "Use raw v28 except fixed danger zones where raw/book disagreement is large; then fall back to executable book probability."),
        ("book_probability", 1, "Approved-entry control: use executable book as probability on every row."),
    ]:
        disc = danger_discovery.get(overlay, {})
        fwd = danger_forward.get(overlay, {})
        rows.append({
            "family": "danger_zone_fv",
            "candidate": overlay,
            "complexity": complexity,
            "note": note,
            "freeze_ts": (frozen_danger_zone_fv.get("freeze") or {}).get("freeze_ts_utc"),
            "forward_entries": fwd.get("rows"),
            "forward_settled": fwd.get("rows"),
            "forward_coverage_pct": None,
            "coverage_fit": "approved-entry-only",
            "forward_brier_delta_vs_raw": fwd.get("brier_delta_vs_raw"),
            "forward_logloss_delta_vs_raw": fwd.get("logloss_delta_vs_raw"),
            "discovery_brier_delta_vs_raw": disc.get("brier_delta_vs_raw"),
            "discovery_logloss_delta_vs_raw": disc.get("logloss_delta_vs_raw"),
            "jackknife_pass": danger_zone_robustness.get("pass_fv_robustness"),
            "entry_robustness_pass": danger_zone_robustness.get("pass_entry_robustness"),
            "blockers": fwd.get("blockers") or ["settled_lt_30"],
        })

    conservative_disc = {
        str(row.get("variant") or ""): row
        for row in (target_conservative_fv.get("ranked") if isinstance(target_conservative_fv.get("ranked"), list) else [])
    }
    conservative_fwd = {
        str(row.get("variant") or ""): row
        for row in (frozen_target_conservative_fv.get("ranked") if isinstance(frozen_target_conservative_fv.get("ranked"), list) else [])
    }
    for variant, complexity, note in [
        ("logit125_p60_calm_mid_or_p75", 3, "Target-coverage challenger: sharpen p>=75, and p60-75 only when recross is calm and ask<=70c."),
    ]:
        disc = conservative_disc.get(variant, {})
        fwd = conservative_fwd.get(variant, {})
        rows.append({
            "family": "target_coverage_conservative_fv",
            "candidate": variant,
            "complexity": complexity,
            "note": note,
            "freeze_ts": (frozen_target_conservative_fv.get("freeze") or {}).get("freeze_ts_utc"),
            "forward_entries": frozen_target_conservative_fv.get("entries"),
            "forward_settled": fwd.get("rows"),
            "forward_coverage_pct": frozen_target_conservative_fv.get("coverage_pct"),
            "coverage_fit": coverage_fit(frozen_target_conservative_fv.get("coverage_pct")),
            "forward_brier_delta_vs_raw": fwd.get("brier_mean_delta"),
            "forward_logloss_delta_vs_raw": fwd.get("logloss_mean_delta"),
            "discovery_brier_delta_vs_raw": disc.get("brier_mean_delta"),
            "discovery_logloss_delta_vs_raw": disc.get("logloss_mean_delta"),
            "jackknife_pass": None,
            "blockers": fwd.get("blockers") or ["settled_lt_30"],
        })
    frozen_p70_best = (frozen_target_p70_fv.get("ranked") or [{}])[0]
    p70_disc = conservative_disc.get("logit125_p70", {})
    rows.append({
        "family": "target_coverage_p70_fv",
        "candidate": "logit125_p70",
        "complexity": 2,
        "note": "Target-coverage FV: sharpen only raw p>=70, leaving mid-confidence boundary rows unsharpened.",
        "freeze_ts": (frozen_target_p70_fv.get("freeze") or {}).get("freeze_ts_utc"),
        "forward_entries": frozen_target_p70_fv.get("entries"),
        "forward_settled": frozen_p70_best.get("rows"),
        "forward_coverage_pct": frozen_target_p70_fv.get("coverage_pct"),
        "coverage_fit": coverage_fit(frozen_target_p70_fv.get("coverage_pct")),
        "forward_brier_delta_vs_raw": frozen_p70_best.get("brier_mean_delta"),
        "forward_logloss_delta_vs_raw": frozen_p70_best.get("logloss_mean_delta"),
        "discovery_brier_delta_vs_raw": p70_disc.get("brier_mean_delta"),
        "discovery_logloss_delta_vs_raw": p70_disc.get("logloss_mean_delta"),
        "diagnostic_brier_p95_vs_raw": ((target_p70_seq.get("brier") or {}).get("bootstrap") or {}).get("p95"),
        "diagnostic_logloss_p95_vs_raw": ((target_p70_seq.get("logloss") or {}).get("bootstrap") or {}).get("p95"),
        "diagnostic_adjusted_rows": target_p70_seq.get("adjusted_rows"),
        "jackknife_pass": target_p70_jackknife.get("pass"),
        "jackknife_worst_brier_delta_vs_raw": (target_p70_jackknife.get("worst_brier") or {}).get("brier_mean_delta"),
        "jackknife_worst_logloss_delta_vs_raw": (target_p70_jackknife.get("worst_logloss") or {}).get("logloss_mean_delta"),
        "blockers": frozen_p70_best.get("blockers") or ["settled_lt_30"],
    })
    path_state_ranked = frozen_path_state_p70.get("ranked") or []
    path_state_variant = (frozen_path_state_p70.get("freeze") or {}).get("variant")
    path_state_best = next(
        (row for row in path_state_ranked if row.get("variant") == path_state_variant),
        path_state_ranked[0] if path_state_ranked else {},
    )
    path_state_diag = (frozen_path_state_p70.get("diagnostic") or {}).get("ranked") or []
    path_state_disc = next(
        (row for row in path_state_diag if row.get("variant") == path_state_variant),
        {},
    )
    rows.append({
        "family": "path_state_p70_fv",
        "candidate": path_state_variant or "path_state_guarded_p70_logit125",
        "complexity": 3,
        "note": "Target-coverage FV: sharpen p>=70 only when strong book discount or deep geometry confirms the state.",
        "freeze_ts": (frozen_path_state_p70.get("freeze") or {}).get("freeze_ts_utc"),
        "forward_entries": frozen_path_state_p70.get("future_entries"),
        "forward_settled": path_state_best.get("rows"),
        "forward_coverage_pct": frozen_path_state_p70.get("future_coverage_pct"),
        "coverage_fit": coverage_fit(frozen_path_state_p70.get("future_coverage_pct")),
        "forward_brier_delta_vs_raw": path_state_best.get("brier_mean_delta"),
        "forward_logloss_delta_vs_raw": path_state_best.get("logloss_mean_delta"),
        "discovery_brier_delta_vs_raw": path_state_disc.get("brier_mean_delta"),
        "discovery_logloss_delta_vs_raw": path_state_disc.get("logloss_mean_delta"),
        "jackknife_pass": None,
        "blockers": path_state_best.get("blockers") or ["settled_lt_30"],
    })
    boundary_recross_ranked = frozen_boundary_recross.get("ranked") or []
    boundary_recross_variant = (frozen_boundary_recross.get("freeze") or {}).get("variant")
    boundary_recross_best = next(
        (row for row in boundary_recross_ranked if row.get("variant") == boundary_recross_variant),
        boundary_recross_ranked[0] if boundary_recross_ranked else {},
    )
    target_forward = by_overlay(
        target_coverage_fv.get("forward") if isinstance(target_coverage_fv.get("forward"), list) else []
    )
    boundary_recross_disc = target_forward.get(boundary_recross_variant or "boundary_recross_shrink_probability", {})
    rows.append({
        "family": "boundary_recross_shrink_fv",
        "candidate": boundary_recross_variant or "boundary_recross_shrink_probability",
        "complexity": 3,
        "note": "Target-coverage FV: shrink shallow high-recross boundary probabilities toward 50 instead of sharpening them.",
        "freeze_ts": (frozen_boundary_recross.get("freeze") or {}).get("freeze_ts_utc"),
        "forward_entries": frozen_boundary_recross.get("entries"),
        "forward_settled": boundary_recross_best.get("rows"),
        "forward_coverage_pct": frozen_boundary_recross.get("coverage_pct"),
        "coverage_fit": coverage_fit(frozen_boundary_recross.get("coverage_pct")),
        "forward_brier_delta_vs_raw": boundary_recross_best.get("brier_mean_delta"),
        "forward_logloss_delta_vs_raw": boundary_recross_best.get("logloss_mean_delta"),
        "discovery_brier_delta_vs_raw": boundary_recross_disc.get("brier_delta_vs_raw"),
        "discovery_logloss_delta_vs_raw": boundary_recross_disc.get("logloss_delta_vs_raw"),
        "jackknife_pass": None,
        "blockers": boundary_recross_best.get("blockers") or ["settled_lt_30"],
    })
    edge_phase_ranked = frozen_edge_phase.get("ranked") or []
    edge_phase_variant = (frozen_edge_phase.get("freeze") or {}).get("variant")
    edge_phase_best = next(
        (row for row in edge_phase_ranked if row.get("variant") == edge_phase_variant),
        edge_phase_ranked[0] if edge_phase_ranked else {},
    )
    phase_bakeoff = load_json(OUT_DIR / "v28_boundary_recross_phase_fv_bakeoff_latest.json")
    phase_diag = next(
        (row for row in (phase_bakeoff.get("ranked") or []) if row.get("variant") == (edge_phase_variant or "edge_phase_shrink")),
        {},
    )
    rows.append({
        "family": "edge_phase_shrink_fv",
        "candidate": edge_phase_variant or "edge_phase_shrink",
        "complexity": 4,
        "note": "Target-coverage FV: phase-aware shrink that preserves wide-edge boundary acceleration.",
        "freeze_ts": (frozen_edge_phase.get("freeze") or {}).get("freeze_ts_utc"),
        "forward_entries": frozen_edge_phase.get("entries"),
        "forward_settled": edge_phase_best.get("rows"),
        "forward_coverage_pct": frozen_edge_phase.get("coverage_pct"),
        "coverage_fit": coverage_fit(frozen_edge_phase.get("coverage_pct")),
        "forward_brier_delta_vs_raw": edge_phase_best.get("brier_mean_delta"),
        "forward_logloss_delta_vs_raw": edge_phase_best.get("logloss_mean_delta"),
        "discovery_brier_delta_vs_raw": phase_diag.get("brier_mean_delta"),
        "discovery_logloss_delta_vs_raw": phase_diag.get("logloss_mean_delta"),
        "jackknife_pass": None,
        "blockers": edge_phase_best.get("blockers") or ["settled_lt_30"],
    })
    edge_gate_candidate = frozen_edge_phase_edge_gate.get("candidate") or {}
    edge_gate_base = frozen_edge_phase_edge_gate.get("base") or {}
    rows.append({
        "family": "edge_phase_edge_gate",
        "candidate": f"{(frozen_edge_phase_edge_gate.get('freeze') or {}).get('fv_variant')}_floor_{(frozen_edge_phase_edge_gate.get('freeze') or {}).get('adjusted_edge_floor')}",
        "complexity": 4,
        "note": "Target-coverage entry gate: skip rare rows where phase-aware FV is far below executable ask.",
        "freeze_ts": (frozen_edge_phase_edge_gate.get("freeze") or {}).get("freeze_ts_utc"),
        "forward_entries": edge_gate_candidate.get("entries"),
        "forward_settled": edge_gate_candidate.get("settled"),
        "forward_coverage_pct": edge_gate_candidate.get("coverage_pct"),
        "coverage_fit": coverage_fit(edge_gate_candidate.get("coverage_pct")),
        "forward_brier_delta_vs_raw": None,
        "forward_logloss_delta_vs_raw": None,
        "discovery_brier_delta_vs_raw": None,
        "discovery_logloss_delta_vs_raw": None,
        "jackknife_pass": None,
        "forward_net_cents": edge_gate_candidate.get("net_cents"),
        "forward_delta_net_cents": frozen_edge_phase_edge_gate.get("delta_net_cents"),
        "base_net_cents": edge_gate_base.get("net_cents"),
        "blockers": edge_gate_candidate.get("blockers") or ["settled_lt_30"],
    })

    edge_gate_opp_candidate = frozen_edge_gate_opposite.get("candidate") or {}
    edge_gate_opp_base = frozen_edge_gate_opposite.get("base") or {}
    rows.append({
        "family": "edge_gate_opposite_side",
        "candidate": "edge_phase_skip_then_same_or_later_opposite",
        "complexity": 5,
        "note": "Target-coverage entry replacement: when edge-phase FV rejects the selected paid price, use first coherent same-or-later opposite side if it exists.",
        "freeze_ts": (frozen_edge_gate_opposite.get("freeze") or {}).get("freeze_ts_utc"),
        "forward_entries": edge_gate_opp_candidate.get("entries"),
        "forward_settled": edge_gate_opp_candidate.get("settled"),
        "forward_coverage_pct": edge_gate_opp_candidate.get("coverage_pct"),
        "coverage_fit": coverage_fit(edge_gate_opp_candidate.get("coverage_pct")),
        "forward_brier_delta_vs_raw": None,
        "forward_logloss_delta_vs_raw": None,
        "discovery_brier_delta_vs_raw": None,
        "discovery_logloss_delta_vs_raw": None,
        "jackknife_pass": None,
        "forward_delta_net_cents": frozen_edge_gate_opposite.get("delta_net_cents"),
        "base_net_cents": edge_gate_opp_base.get("net_cents"),
        "blockers": edge_gate_opp_candidate.get("blockers") or ["settled_lt_30"],
    })

    low_recross_candidate = frozen_low_recross_repair.get("candidate_summary") or {}
    rows.append({
        "family": "low_recross_repair_entry",
        "candidate": (frozen_low_recross_repair.get("freeze") or {}).get("candidate") or "skip_paid_or_weak_boundary_repair_lowest_recross",
        "complexity": 5,
        "note": "Entry-stack repair: skip paid-price fragile or weak boundary turbulence rows, then restore target coverage with clean missed-market opportunities ranked by lowest recross hazard.",
        "freeze_ts": (frozen_low_recross_repair.get("freeze") or {}).get("freeze_ts_utc"),
        "forward_entries": low_recross_candidate.get("entries"),
        "forward_settled": low_recross_candidate.get("settled"),
        "forward_coverage_pct": low_recross_candidate.get("coverage_pct"),
        "coverage_fit": coverage_fit(low_recross_candidate.get("coverage_pct")),
        "forward_brier_delta_vs_raw": None,
        "forward_logloss_delta_vs_raw": None,
        "discovery_brier_delta_vs_raw": None,
        "discovery_logloss_delta_vs_raw": None,
        "jackknife_pass": None,
        "forward_net_cents": low_recross_candidate.get("net_cents"),
        "forward_delta_net_cents": frozen_low_recross_repair.get("delta_vs_target_cents"),
        "blockers": frozen_low_recross_repair.get("blockers") or ["settled_lt_30"],
    })

    boundary_clock_candidate = frozen_boundary_clock_repair.get("candidate_summary") or {}
    rows.append({
        "family": "boundary_clock_repair_entry",
        "candidate": (frozen_boundary_clock_repair.get("freeze") or {}).get("candidate") or "skip_boundary_clock_composite_repair_lowest_recross",
        "complexity": 5,
        "note": "Entry-stack repair: skip early boundary-clock turbulence and expensive low-edge rows, then restore target coverage with clean missed-market rows ranked by lowest recross hazard.",
        "freeze_ts": (frozen_boundary_clock_repair.get("freeze") or {}).get("freeze_ts_utc"),
        "forward_entries": boundary_clock_candidate.get("entries"),
        "forward_settled": boundary_clock_candidate.get("settled"),
        "forward_coverage_pct": boundary_clock_candidate.get("coverage_pct"),
        "coverage_fit": coverage_fit(boundary_clock_candidate.get("coverage_pct")),
        "forward_brier_delta_vs_raw": None,
        "forward_logloss_delta_vs_raw": None,
        "discovery_brier_delta_vs_raw": None,
        "discovery_logloss_delta_vs_raw": None,
        "jackknife_pass": None,
        "forward_net_cents": boundary_clock_candidate.get("net_cents"),
        "forward_delta_net_cents": frozen_boundary_clock_repair.get("delta_vs_target_cents"),
        "blockers": frozen_boundary_clock_repair.get("blockers") or ["settled_lt_30"],
    })

    high_raw_p_repair_candidate = frozen_high_raw_p_repair.get("candidate_summary") or {}
    rows.append({
        "family": "high_raw_p_repair_entry",
        "candidate": (frozen_high_raw_p_repair.get("freeze") or {}).get("candidate") or "skip_paid_or_weak_boundary_repair_highest_raw_p",
        "complexity": 5,
        "note": "Entry-stack repair: skip paid/weak-boundary danger rows, then restore target coverage with clean missed-market rows ranked by highest raw p.",
        "freeze_ts": (frozen_high_raw_p_repair.get("freeze") or {}).get("freeze_ts_utc"),
        "forward_entries": high_raw_p_repair_candidate.get("entries"),
        "forward_settled": high_raw_p_repair_candidate.get("settled"),
        "forward_coverage_pct": high_raw_p_repair_candidate.get("coverage_pct"),
        "coverage_fit": coverage_fit(high_raw_p_repair_candidate.get("coverage_pct")),
        "forward_brier_delta_vs_raw": None,
        "forward_logloss_delta_vs_raw": None,
        "discovery_brier_delta_vs_raw": None,
        "discovery_logloss_delta_vs_raw": None,
        "jackknife_pass": None,
        "forward_net_cents": high_raw_p_repair_candidate.get("net_cents"),
        "forward_delta_net_cents": frozen_high_raw_p_repair.get("delta_vs_target_cents"),
        "blockers": frozen_high_raw_p_repair.get("blockers") or ["settled_lt_30"],
    })

    boundary_clock_fv_candidate = frozen_boundary_clock_fv.get("candidate") or {}
    rows.append({
        "family": "boundary_clock_fv_overlay",
        "candidate": (frozen_boundary_clock_fv.get("freeze") or {}).get("variant") or "clock_shrink_0p00",
        "complexity": 4,
        "note": "FV overlay: collapse unresolved boundary-clock hazard rows to 50 while leaving non-hazard raw v28 probabilities unchanged.",
        "freeze_ts": (frozen_boundary_clock_fv.get("freeze") or {}).get("freeze_ts_utc"),
        "forward_entries": boundary_clock_fv_candidate.get("entries"),
        "forward_settled": boundary_clock_fv_candidate.get("settled"),
        "forward_coverage_pct": boundary_clock_fv_candidate.get("coverage_pct"),
        "coverage_fit": coverage_fit(boundary_clock_fv_candidate.get("coverage_pct")),
        "forward_brier_delta_vs_raw": boundary_clock_fv_candidate.get("brier_mean_delta"),
        "forward_logloss_delta_vs_raw": boundary_clock_fv_candidate.get("logloss_mean_delta"),
        "discovery_brier_delta_vs_raw": None,
        "discovery_logloss_delta_vs_raw": None,
        "jackknife_pass": None,
        "forward_net_cents": boundary_clock_fv_candidate.get("net_cents"),
        "blockers": frozen_boundary_clock_fv.get("blockers") or ["settled_lt_30"],
    })

    side_asymmetry_fv_candidate = frozen_side_asymmetry_fv_overlay.get("candidate") or {}
    rows.append({
        "family": "side_asymmetry_fv_overlay",
        "candidate": (frozen_side_asymmetry_fv_overlay.get("freeze") or {}).get("variant") or "clock_then_side_no_midboundary_0p00",
        "complexity": 5,
        "note": "FV overlay: collapse boundary-clock hazard and NO p60-70 mid-boundary mid-recross unresolved path states to 50.",
        "freeze_ts": (frozen_side_asymmetry_fv_overlay.get("freeze") or {}).get("freeze_ts_utc"),
        "forward_entries": side_asymmetry_fv_candidate.get("entries"),
        "forward_settled": side_asymmetry_fv_candidate.get("settled"),
        "forward_coverage_pct": side_asymmetry_fv_candidate.get("coverage_pct"),
        "coverage_fit": coverage_fit(side_asymmetry_fv_candidate.get("coverage_pct")),
        "forward_brier_delta_vs_raw": side_asymmetry_fv_candidate.get("brier_mean_delta"),
        "forward_logloss_delta_vs_raw": side_asymmetry_fv_candidate.get("logloss_mean_delta"),
        "discovery_brier_delta_vs_raw": None,
        "discovery_logloss_delta_vs_raw": None,
        "jackknife_pass": None,
        "forward_net_cents": side_asymmetry_fv_candidate.get("net_cents"),
        "blockers": frozen_side_asymmetry_fv_overlay.get("blockers") or ["settled_lt_30"],
    })

    side_bridge_candidate = frozen_side_asymmetry_entry_bridge.get("candidate_summary") or {}
    rows.append({
        "family": "side_asymmetry_fv_entry_bridge",
        "candidate": (frozen_side_asymmetry_entry_bridge.get("freeze") or {}).get("candidate")
        or "target_coverage_side_asymmetry_adjusted_edge2pp_strict_farthest_boundary_repair",
        "complexity": 6,
        "note": "Entry bridge: use side-asymmetry adjusted FV directly, skip adjusted edge below 2pp, repair coverage with strict clean far-boundary rows.",
        "freeze_ts": (frozen_side_asymmetry_entry_bridge.get("freeze") or {}).get("freeze_ts_utc"),
        "forward_entries": side_bridge_candidate.get("entries"),
        "forward_settled": side_bridge_candidate.get("settled"),
        "forward_coverage_pct": side_bridge_candidate.get("coverage_pct"),
        "coverage_fit": coverage_fit(side_bridge_candidate.get("coverage_pct")),
        "forward_brier_delta_vs_raw": None,
        "forward_logloss_delta_vs_raw": None,
        "discovery_brier_delta_vs_raw": None,
        "discovery_logloss_delta_vs_raw": None,
        "jackknife_pass": None,
        "forward_net_cents": side_bridge_candidate.get("net_cents"),
        "forward_delta_net_cents": frozen_side_asymmetry_entry_bridge.get("delta_vs_target_cents"),
        "blockers": frozen_side_asymmetry_entry_bridge.get("blockers") or ["settled_lt_30"],
    })

    bridge_candidate = frozen_boundary_clock_fv_entry_bridge.get("candidate_summary") or {}
    rows.append({
        "family": "boundary_clock_fv_entry_bridge",
        "candidate": (frozen_boundary_clock_fv_entry_bridge.get("freeze") or {}).get("candidate") or "boundary_clock_adjusted_edge_floor_0p02_repair_lowest_recross",
        "complexity": 5,
        "note": "Entry bridge: use boundary-clock adjusted FV directly, skip rows with adjusted edge below 2pp, repair coverage with clean low-recross rows.",
        "freeze_ts": (frozen_boundary_clock_fv_entry_bridge.get("freeze") or {}).get("freeze_ts_utc"),
        "forward_entries": bridge_candidate.get("entries"),
        "forward_settled": bridge_candidate.get("settled"),
        "forward_coverage_pct": bridge_candidate.get("coverage_pct"),
        "coverage_fit": coverage_fit(bridge_candidate.get("coverage_pct")),
        "forward_brier_delta_vs_raw": None,
        "forward_logloss_delta_vs_raw": None,
        "discovery_brier_delta_vs_raw": None,
        "discovery_logloss_delta_vs_raw": None,
        "jackknife_pass": None,
        "forward_net_cents": bridge_candidate.get("net_cents"),
        "forward_delta_net_cents": frozen_boundary_clock_fv_entry_bridge.get("delta_vs_target_cents"),
        "blockers": frozen_boundary_clock_fv_entry_bridge.get("blockers") or ["settled_lt_30"],
    })

    rows.sort(key=candidate_score)
    best_coverage = None
    ranked_valves = coverage_valve.get("ranked") if isinstance(coverage_valve.get("ranked"), list) else []
    if ranked_valves:
        best_coverage = {
            "policy": ranked_valves[0].get("policy"),
            "forward": ranked_valves[0].get("forward"),
            "discovery": ranked_valves[0].get("discovery"),
        }
    return {
        "target": "More accurate FV while preserving roughly 75-80%+ BTC 15m coverage.",
        "requirements": [
            "fixed raw-v28 p50 entry comparison for FV-only overlays",
            "future-only validation after each freeze timestamp",
            "at least 30 settled forward rows before promotion",
            "target coverage 75-90% in broad-entry strategy views",
            "Brier and logloss improvement versus raw",
            "prefer simpler candidate when evidence is comparable",
        ],
        "candidate_rows": rows,
        "current_read": current_read(rows, best_coverage),
        "best_coverage_valve": best_coverage,
        "approved_entry_book_fv_robustness": approved_book_robustness,
        "approved_entry_book_raw_blend": approved_book_raw_blend,
        "frozen_approved_entry_book_fv": frozen_approved_entry_book_fv,
        "approved_entry_book_fv_regime_attribution": approved_book_regime,
        "frozen_approved_entry_conditional_book_fv": frozen_approved_conditional_book_fv,
        "target_coverage_fv": target_coverage_fv,
        "target_coverage_sequential": target_coverage_seq,
        "target_coverage_attribution": target_coverage_attr,
        "target_coverage_pnl_attribution": target_coverage_pnl_attr,
        "danger_zone_robustness": danger_zone_robustness,
        "target_conservative_fv": target_conservative_fv,
        "frozen_target_conservative_fv": frozen_target_conservative_fv,
        "frozen_target_p70_fv": frozen_target_p70_fv,
        "target_p70_jackknife": target_p70_jackknife,
        "target_p70_sequential": target_p70_seq,
        "target_confidence_temperature": target_confidence_temp,
        "target_p70_fragility": target_p70_fragility,
        "target_p70_scale": target_p70_scale,
        "target_p70_empirical_bayes": target_p70_empirical_bayes,
        "target_source_split": target_source_split,
        "frozen_target_p70_runway": frozen_target_p70_runway,
        "frozen_target_p70_empirical_bayes_runway": frozen_target_p70_eb_runway,
        "frozen_target_p70_quality_registry": frozen_target_p70_quality,
        "frozen_target_p70_pending_sensitivity": frozen_target_p70_pending,
        "frozen_path_state_p70_fv": frozen_path_state_p70,
        "frozen_boundary_recross_shrink_fv": frozen_boundary_recross,
        "frozen_edge_phase_shrink_fv": frozen_edge_phase,
        "boundary_reversal_opportunity": boundary_reversal,
        "danger_tag_replacement_diagnostic": danger_tag_replacement,
        "coverage_repair_pool_diagnostic": coverage_repair_pool,
        "danger_repair_bakeoff": danger_repair_bakeoff,
        "repair_scoring_bakeoff": repair_scoring_bakeoff,
        "boundary_clock_hazard_repair": boundary_clock_hazard_repair,
        "boundary_clock_robustness_audit": boundary_clock_robustness,
        "boundary_clock_fv_overlay": boundary_clock_fv_overlay,
        "boundary_clock_fv_robustness": boundary_clock_fv_robustness,
        "boundary_clock_residual_attribution": boundary_clock_residual,
        "frozen_boundary_clock_residual_registry": frozen_boundary_clock_residual_registry,
        "side_asymmetry_fv_diagnostic": side_asymmetry,
        "frozen_side_asymmetry_registry": frozen_side_asymmetry_registry,
        "side_asymmetry_fv_overlay": side_asymmetry_overlay,
        "frozen_side_asymmetry_fv_overlay": frozen_side_asymmetry_fv_overlay,
        "boundary_clock_promotion_runway": boundary_clock_promotion_runway,
        "boundary_clock_fv_entry_bridge": boundary_clock_fv_entry_bridge,
        "target_fv_edge_gate_diagnostic": target_fv_edge_gate,
        "edge_gate_opposite_side_diagnostic": edge_gate_opposite,
        "frozen_edge_phase_edge_gate": frozen_edge_phase_edge_gate,
        "frozen_edge_gate_opposite_side": frozen_edge_gate_opposite,
        "frozen_low_recross_repair_entry": frozen_low_recross_repair,
        "frozen_high_raw_p_repair_entry": frozen_high_raw_p_repair,
        "frozen_boundary_clock_repair_entry": frozen_boundary_clock_repair,
        "frozen_boundary_clock_fv_overlay": frozen_boundary_clock_fv,
        "frozen_boundary_clock_fv_entry_bridge": frozen_boundary_clock_fv_entry_bridge,
    }


def current_read(rows: list[dict[str, Any]], best_coverage: dict[str, Any] | None) -> list[str]:
    notes: list[str] = []
    discovery_sorted = sorted(
        [row for row in rows if as_float(row.get("discovery_brier_delta_vs_raw")) is not None],
        key=lambda row: float(row.get("discovery_brier_delta_vs_raw") or 999.0),
    )
    if discovery_sorted:
        best = discovery_sorted[0]
        notes.append(
            f"Discovery best by Brier is {best['candidate']} ({best['discovery_brier_delta_vs_raw']}); this is not promotion evidence."
        )
    forward_with_rows = [row for row in rows if int(as_float(row.get("forward_entries")) or 0) > 0]
    if forward_with_rows:
        mature = sum(1 for row in forward_with_rows if int(as_float(row.get("forward_settled")) or 0) >= MIN_FORWARD_SETTLED)
        notes.append(
            f"{len(forward_with_rows)} candidate rows have at least one post-freeze forward entry; {mature} have at least {MIN_FORWARD_SETTLED} settled rows."
        )
    reward = next((row for row in rows if row.get("candidate") == "reward_memory_plus05"), {})
    simple = next((row for row in rows if row.get("candidate") == "plus05_probability"), {})
    if reward and simple:
        notes.append(
            f"Reward-memory +5pp is robust but discovery Brier delta ({reward.get('discovery_brier_delta_vs_raw')}) is weaker than simple +5pp ({simple.get('discovery_brier_delta_vs_raw')})."
        )
    if best_coverage:
        fwd = (best_coverage.get("forward") or {}).get("coverage_valve") or {}
        notes.append(
            f"Best coverage valve is {best_coverage.get('policy')} with forward coverage {fwd.get('coverage_pct')} and net {fwd.get('net_cents_after_entry_fee')}c."
        )
    approved_book = load_json(FROZEN_APPROVED_ENTRY_BOOK_FV_JSON)
    approved_book_actionability = load_json(APPROVED_ENTRY_BOOK_EDGE_ACTIONABILITY_JSON)
    frozen_book_gate = load_json(FROZEN_APPROVED_ENTRY_BOOK_EDGE_GATE_JSON)
    approved_conditional = load_json(FROZEN_APPROVED_ENTRY_CONDITIONAL_BOOK_FV_JSON)
    if approved_book:
        cand = approved_book.get("candidate") or {}
        notes.append(
            f"Cleanest actual-approved FV evidence is book_probability: {approved_book.get('future_settled')} settled rows, Brier/logloss deltas {cand.get('brier_delta_vs_raw')}/{cand.get('logloss_delta_vs_raw')}."
        )
    if approved_book_actionability:
        useful = approved_book_actionability.get("useful") or []
        best = useful[0] if useful else {}
        retained = best.get("retained") or {}
        if best:
            notes.append(
                f"Approved-entry book-edge actionability best is {best.get('policy')}: retained coverage {retained.get('coverage_pct')}, net {retained.get('net_cents')}c, delta {best.get('delta_net_vs_keep_all_cents')}c versus keeping all actual v28-approved entries."
            )
    if frozen_book_gate:
        candidate = frozen_book_gate.get("candidate") or {}
        notes.append(
            f"Frozen approved-entry book-edge gate now has future entries/settled {frozen_book_gate.get('future_entries')}/{candidate.get('settled')}; delta {frozen_book_gate.get('delta_net_vs_control_cents')}c and blockers {frozen_book_gate.get('blockers')}."
        )
    broad_book_gate = load_json(FROZEN_TARGET_COVERAGE_BOOK_EDGE_GATE_JSON)
    if broad_book_gate:
        candidate = broad_book_gate.get("candidate_summary") or {}
        notes.append(
            f"Frozen target-coverage book-edge gate has denominator/entries/settled {broad_book_gate.get('future_denominator')}/{candidate.get('entries')}/{candidate.get('settled')}; coverage {candidate.get('coverage_pct')}, delta {broad_book_gate.get('delta_vs_target_cents')}c, blockers {broad_book_gate.get('blockers')}."
        )
    if approved_conditional:
        future = approved_conditional.get("future") or {}
        pre = approved_conditional.get("prefreeze_context") or {}
        pre_cand = pre.get("candidate") or {}
        notes.append(
            f"Conditional approved-entry book FV is now frozen for future validation: future settled {future.get('settled')}, pre-freeze Brier/logloss deltas {pre_cand.get('brier_delta_vs_raw')}/{pre_cand.get('logloss_delta_vs_raw')}."
        )
    target = load_json(TARGET_COVERAGE_FV_JSON)
    target_rows = target.get("forward") if isinstance(target.get("forward"), list) else []
    if target_rows:
        best = target_rows[0]
        notes.append(
            f"On the target-coverage surface, best FV overlay is {best.get('overlay')} with coverage {best.get('coverage_pct')}, Brier delta {best.get('brier_delta_vs_raw')}, and logloss delta {best.get('logloss_delta_vs_raw')}."
        )
    crowd_skip = load_json(RAW_P52_BOOK_DISAGREEMENT_SKIP_JSON)
    if crowd_skip:
        base = crowd_skip.get("base") or {}
        cand = crowd_skip.get("candidate_summary") or {}
        skip = crowd_skip.get("skipped_summary") or {}
        notes.append(
            f"Raw-p52 crowd-prior skip discovery keeps coverage {cand.get('coverage_pct')} versus base {base.get('coverage_pct')}, net {cand.get('net_cents')}c versus {base.get('net_cents')}c; skipped rows are {skip.get('wins')}/{skip.get('losses')} for {skip.get('net_cents')}c."
        )
    frozen_crowd_skip = load_json(FROZEN_RAW_P52_BOOK_DISAGREEMENT_SKIP_JSON)
    if frozen_crowd_skip:
        cand = frozen_crowd_skip.get("candidate_summary") or {}
        notes.append(
            f"Frozen raw-p52 crowd-prior skip has denominator {frozen_crowd_skip.get('future_denominator')}, settled {cand.get('settled')}, and blockers {frozen_crowd_skip.get('blockers')}; it is watch-only."
        )
    crowd_shrink = load_json(RAW_P52_BOOK_SHRINK_ENTRY_JSON)
    if crowd_shrink:
        ranked = crowd_shrink.get("ranked") or []
        base = next((row for row in ranked if row.get("policy") == "raw_probability_p52_edge0"), {})
        shrink50 = next((row for row in ranked if row.get("policy") == "gap15_book50_p52_edge0"), {})
        shrink75 = next((row for row in ranked if row.get("policy") == "gap15_book75_p52_edge0"), {})
        notes.append(
            f"Book-disagreement shrink is not currently stronger than raw: raw p52 net {base.get('net_cents')}c, 50% shrink {shrink50.get('net_cents')}c, 75% shrink {shrink75.get('net_cents')}c."
        )
    replacement = load_json(BOOK_DISAGREEMENT_REPLACEMENT_JSON)
    if replacement:
        reports = replacement.get("reports") or []
        shrink50 = next((row for row in reports if row.get("policy") == "gap15_book50_p52_edge0"), {})
        notes.append(
            f"Shrink underperformance is partly entry-order interaction: 50% shrink replacement delta is {shrink50.get('replacement_delta_cents')}c across {shrink50.get('replacement_count')} replacements, so hard abstention is cleaner than side-search replacement."
        )
    early_no_band = load_json(RAW_P52_EARLY_NO_BOUNDARY_BAND_JSON)
    if early_no_band:
        base = early_no_band.get("base") or {}
        cand = early_no_band.get("candidate_summary") or {}
        skipped = early_no_band.get("skipped_summary") or {}
        notes.append(
            f"Raw-p52 middle-confidence early-NO boundary skip is the strongest discovery row right now: coverage {cand.get('coverage_pct')} versus base {base.get('coverage_pct')}, net {cand.get('net_cents')}c versus {base.get('net_cents')}c; skipped bucket {skipped.get('wins')}/{skipped.get('losses')} for {skipped.get('net_cents')}c."
        )
    early_no_robustness = load_json(RAW_P52_EARLY_NO_BOUNDARY_BAND_ROBUSTNESS_JSON)
    if early_no_robustness:
        canonical = early_no_robustness.get("canonical") or {}
        cand = canonical.get("candidate_summary") or {}
        notes.append(
            f"Early-NO band robustness pass is {early_no_robustness.get('passes_basic_robustness')}; canonical coverage/net {cand.get('coverage_pct')}/{cand.get('net_cents')}c and worst leave-one-skipped delta {(early_no_robustness.get('leave_one_skipped') or [{}])[0].get('delta_vs_base_with_returned_market')}c."
        )
    frozen_early_no_band = load_json(FROZEN_RAW_P52_EARLY_NO_BOUNDARY_BAND_JSON)
    if frozen_early_no_band:
        cand = frozen_early_no_band.get("candidate_summary") or {}
        notes.append(
            f"Frozen early-NO boundary band skip has denominator {frozen_early_no_band.get('future_denominator')}, settled {cand.get('settled')}, and blockers {frozen_early_no_band.get('blockers')}; it needs fresh forward rows before use."
        )
    early_no_runway = load_json(RAW_P52_EARLY_NO_BOUNDARY_BAND_RUNWAY_JSON)
    if early_no_runway:
        pending = early_no_runway.get("pending_sensitivity") or {}
        notes.append(
            f"Early-NO boundary band runway ready={early_no_runway.get('ready_for_consideration')} with checks {early_no_runway.get('checks')}; pending skipped rows {pending.get('pending_skipped_rows')} and stressed delta {pending.get('delta_after_all_pending_skips_win_cents')}c."
        )
    decay_repair_runway = load_json(EARLY_NO_BOUNDARY_DECAY_REPAIR_RUNWAY_JSON)
    if decay_repair_runway:
        candidate = decay_repair_runway.get("candidate_summary") or {}
        frag = decay_repair_runway.get("fragility") or {}
        notes.append(
            f"Early-NO boundary decay repair runway has entries/settled/net {candidate.get('entries')}/{candidate.get('settled')}/{candidate.get('net_cents')}c at coverage {candidate.get('coverage_pct')}; rows needed {frag.get('rows_needed_for_30')} and full-loss cushion {frag.get('full_100c_losses_before_net_flat')}."
        )
    seq = load_json(TARGET_COVERAGE_FV_SEQ_JSON)
    if seq:
        brier = seq.get("brier") or {}
        logloss = seq.get("logloss") or {}
        b_boot = brier.get("bootstrap") or {}
        l_boot = logloss.get("bootstrap") or {}
        notes.append(
            f"Target-coverage paired evidence has {seq.get('settled_rows')} settled rows; Brier mean/p95 {brier.get('mean_delta')}/{b_boot.get('p95')}, logloss mean/p95 {logloss.get('mean_delta')}/{l_boot.get('p95')}."
        )
    attr = load_json(TARGET_COVERAGE_FV_ATTRIBUTION_JSON)
    if attr:
        notes.extend(attr.get("interpretation") or [])
    pnl_attr = load_json(TARGET_COVERAGE_PNL_ATTRIBUTION_JSON)
    if pnl_attr:
        classes = pnl_attr.get("class_rollups") or {}
        wrong = classes.get("direction_wrong") or {}
        won_negative = classes.get("side_won_but_negative_pnl") or {}
        notes.append(
            f"Target-coverage PnL attribution: direction-wrong rows are {wrong.get('settled')} rows for {wrong.get('net_cents')}c; side-won negative-PnL rows are {won_negative.get('settled')} rows for {won_negative.get('net_cents')}c."
        )
    boundary_entropy = load_json(BOUNDARY_ENTROPY_FV_JSON)
    if boundary_entropy:
        best_fv = (boundary_entropy.get("ranked_fv") or [{}])[0]
        best_bridge = (boundary_entropy.get("ranked_target_coverage_entry_bridges") or [{}])[0]
        notes.append(
            f"Boundary-entropy FV diagnostic best is {best_fv.get('variant')} with Brier/logloss {best_fv.get('brier_delta_vs_raw')}/{best_fv.get('logloss_delta_vs_raw')}; best target-coverage bridge {best_bridge.get('variant')} net {best_bridge.get('net_cents')}c, so entropy shrink is diagnostic rather than stronger than book-anchor right now."
        )
    danger = load_json(DANGER_ZONE_ROBUSTNESS_JSON)
    if danger:
        full_fv = danger.get("full_fv") or {}
        full_entry = danger.get("full_entry") or {}
        notes.append(
            f"Danger-zone entry valve has {full_entry.get('delta_cents')}c discovery P&L lift but entry robustness pass is {danger.get('pass_entry_robustness')}; treat it as watched, not promotable."
        )
        notes.append(
            f"Danger-zone FV shrink has Brier/logloss deltas {full_fv.get('brier_delta_vs_raw')}/{full_fv.get('logloss_delta_vs_raw')} and FV robustness pass {danger.get('pass_fv_robustness')}."
        )
    conservative = load_json(TARGET_CONSERVATIVE_FV_JSON)
    if conservative:
        best = (conservative.get("ranked") or [{}])[0]
        notes.append(
            f"Target-coverage conservative FV best diagnostic variant is {best.get('variant')} with Brier/logloss mean deltas {best.get('brier_mean_delta')}/{best.get('logloss_mean_delta')}; frozen forward evidence starts separately."
        )
    p70_jackknife = load_json(TARGET_P70_JACKKNIFE_JSON)
    if p70_jackknife:
        full = p70_jackknife.get("full") or {}
        worst_brier = p70_jackknife.get("worst_brier") or {}
        notes.append(
            f"P70 diagnostic jackknife pass is {p70_jackknife.get('pass')} with {p70_jackknife.get('failure_count')} failures; full Brier/logloss {full.get('brier_mean_delta')}/{full.get('logloss_mean_delta')}, worst Brier leave-out {worst_brier.get('brier_mean_delta')}."
        )
    p70_seq = load_json(TARGET_P70_SEQ_JSON)
    if p70_seq:
        brier = p70_seq.get("brier") or {}
        logloss = p70_seq.get("logloss") or {}
        b_boot = brier.get("bootstrap") or {}
        l_boot = logloss.get("bootstrap") or {}
        notes.append(
            f"P70 paired interval has {p70_seq.get('settled_rows')} settled rows and {p70_seq.get('adjusted_rows')} adjusted rows; Brier/logloss p95 {b_boot.get('p95')}/{l_boot.get('p95')}."
        )
    confidence_temp = load_json(TARGET_CONFIDENCE_TEMP_JSON)
    if confidence_temp:
        best = (confidence_temp.get("ranked") or [{}])[0]
        hard_p70 = next((row for row in confidence_temp.get("ranked") or [] if row.get("variant") == "hard_logit125_p70"), {})
        notes.append(
            f"Confidence-temperature bakeoff best is {best.get('variant')} with Brier/logloss {best.get('brier_mean_delta')}/{best.get('logloss_mean_delta')}; hard p70 is {hard_p70.get('brier_mean_delta')}/{hard_p70.get('logloss_mean_delta')}."
        )
    p70_fragility = load_json(TARGET_P70_FRAGILITY_JSON)
    if p70_fragility:
        breaks = p70_fragility.get("first_breaks") or {}
        row_75 = breaks.get("0.75") or {}
        row_80 = breaks.get("0.8") or {}
        notes.append(
            f"P70 fragility stress: one adverse p75 row breaks interval evidence at count {row_75.get('first_interval_break_count')}; one adverse p80 row breaks mean at count {row_80.get('first_mean_break_count')}."
        )
    p70_scale = load_json(TARGET_P70_SCALE_JSON)
    if p70_scale:
        best = (p70_scale.get("ranked") or [{}])[0]
        notes.append(
            f"P70 scale bakeoff best robustness-ranked scale is {best.get('scale')} with first adverse p80 break count {best.get('first_any_break_count')}; scale tuning has not solved fragility."
        )
    p70_eb = load_json(TARGET_P70_EMPIRICAL_BAYES_JSON)
    if p70_eb:
        best = (p70_eb.get("ranked") or [{}])[0]
        notes.append(
            f"P70 empirical-Bayes throttle best is {best.get('variant')} scale {best.get('scale')} with Brier/logloss p95 {best.get('brier_p95')}/{best.get('logloss_p95')} and first adverse p80 break {best.get('first_any_break_count')}."
        )
    source_split = load_json(TARGET_SOURCE_SPLIT_JSON)
    if source_split:
        for group in source_split.get("source_groups") or []:
            best = (group.get("ranked") or [{}])[0]
            notes.append(
                f"P70 source split {group.get('source')} best {best.get('variant')} over {group.get('rows')} rows with Brier/logloss {best.get('brier_mean_delta')}/{best.get('logloss_mean_delta')}."
            )
    p70_runway = load_json(FROZEN_TARGET_P70_RUNWAY_JSON)
    if p70_runway:
        notes.append(
            f"Frozen p70 runway has denominator/selected/base-seen {p70_runway.get('future_denominator')}/{p70_runway.get('selected_entries')}/{p70_runway.get('base_seen_markets')}; current zero rows are explained by target-policy abstention if selected remains 0."
        )
    p70_eb_runway = load_json(FROZEN_TARGET_P70_EB_RUNWAY_JSON)
    if p70_eb_runway:
        notes.append(
            f"Frozen p70 empirical-Bayes runway has denominator/selected/base-seen {p70_eb_runway.get('future_denominator')}/{p70_eb_runway.get('selected_entries')}/{p70_eb_runway.get('base_seen_markets')}."
        )
    p70_quality = load_json(FROZEN_TARGET_P70_QUALITY_JSON)
    if p70_quality:
        notes.append(
            f"Frozen p70 quality registry has denominator/target-entries/p70-rows {p70_quality.get('future_denominator')}/{p70_quality.get('target_entries')}/{p70_quality.get('p70_rows')}."
        )
    p70_pending = load_json(FROZEN_TARGET_P70_PENDING_JSON)
    if p70_pending:
        for validator in p70_pending.get("validators") or []:
            summary = validator.get("summary") or {}
            notes.append(
                f"{validator.get('validator')} pending sensitivity: pending-adjusted {summary.get('pending_adjusted')}, settled-adjusted {summary.get('settled_adjusted')}, raw-only losses {summary.get('settled_raw_only_losses')}."
            )
    approved_book_robustness = load_json(APPROVED_ENTRY_BOOK_ROBUSTNESS_JSON)
    if approved_book_robustness:
        full = approved_book_robustness.get("full") or {}
        boot = approved_book_robustness.get("bootstrap") or {}
        notes.append(
            f"Approved-entry book FV robustness has {approved_book_robustness.get('rows')} actual rows; full Brier/logloss deltas {full.get('brier_delta_mean')}/{full.get('logloss_delta_mean')}, bootstrap p95 {boot.get('brier_p95')}/{boot.get('logloss_p95')}, blockers {approved_book_robustness.get('blockers')}."
        )
    approved_book_blend = load_json(APPROVED_ENTRY_BOOK_RAW_BLEND_JSON)
    if approved_book_blend:
        best = approved_book_blend.get("best") or {}
        boot = best.get("bootstrap_vs_raw") or {}
        notes.append(
            f"Approved-entry book/raw blend best alpha is {best.get('alpha_raw_weight')}; Brier/logloss deltas {best.get('brier_delta_vs_raw')}/{best.get('logloss_delta_vs_raw')}, bootstrap p95 {boot.get('brier_delta_p95')}/{boot.get('logloss_delta_p95')}."
        )
    approved_book = load_json(FROZEN_APPROVED_ENTRY_BOOK_FV_JSON)
    if approved_book:
        candidate = approved_book.get("candidate") or {}
        notes.append(
            f"Frozen approved-entry book FV has entries/settled {approved_book.get('future_entries')}/{approved_book.get('future_settled')}; Brier/logloss deltas {candidate.get('brier_delta_vs_raw')}/{candidate.get('logloss_delta_vs_raw')}."
        )
    path_state = load_json(FROZEN_PATH_STATE_P70_JSON)
    if path_state:
        ranked = path_state.get("ranked") or []
        target_variant = (path_state.get("freeze") or {}).get("variant")
        best = next((row for row in ranked if row.get("variant") == target_variant), ranked[0] if ranked else {})
        notes.append(
            f"Frozen path-state p70 has denominator/entries/settled {path_state.get('future_denominator')}/{path_state.get('future_entries')}/{path_state.get('future_settled')}; {best.get('variant')} Brier/logloss {best.get('brier_mean_delta')}/{best.get('logloss_mean_delta')}."
        )
    boundary_recross = load_json(FROZEN_BOUNDARY_RECROSS_SHRINK_JSON)
    if boundary_recross:
        ranked = boundary_recross.get("ranked") or []
        target_variant = (boundary_recross.get("freeze") or {}).get("variant")
        best = next((row for row in ranked if row.get("variant") == target_variant), ranked[0] if ranked else {})
        notes.append(
            f"Frozen boundary-recross shrink has denominator/entries/settled {boundary_recross.get('future_denominator')}/{boundary_recross.get('entries')}/{boundary_recross.get('settled')}; {best.get('variant')} Brier/logloss {best.get('brier_mean_delta')}/{best.get('logloss_mean_delta')}."
        )
    boundary_reversal = load_json(BOUNDARY_REVERSAL_JSON)
    if boundary_reversal:
        repl = boundary_reversal.get("replacement_summary") or {}
        replaced = boundary_reversal.get("replaced_strategy_summary") or {}
        notes.append(
            f"Boundary reversal diagnostic found {boundary_reversal.get('boundary_with_replacement')}/{boundary_reversal.get('boundary_rows')} boundary rows with opposite replacements; replacement-only net {repl.get('net_cents')}c and non-boundary-plus-replacement coverage {replaced.get('coverage_pct')}."
        )
    danger_replacement = load_json(DANGER_TAG_REPLACEMENT_JSON)
    if danger_replacement:
        target = danger_replacement.get("target_summary") or {}
        candidate = danger_replacement.get("candidate_summary") or {}
        notes.append(
            f"Danger-tag replacement diagnostic found {danger_replacement.get('danger_with_replacement')}/{danger_replacement.get('danger_rows')} replacements; target net {target.get('net_cents')}c versus replacement net {candidate.get('net_cents')}c."
        )
    coverage_repair = load_json(COVERAGE_REPAIR_POOL_JSON)
    if coverage_repair:
        target = coverage_repair.get("target_summary") or {}
        candidate = coverage_repair.get("candidate_summary") or {}
        notes.append(
            f"Coverage-repair diagnostic removes toxic rows and repairs from missed markets: target net {target.get('net_cents')}c versus candidate net {candidate.get('net_cents')}c at coverage {candidate.get('coverage_pct')}."
        )
    danger_repair = load_json(DANGER_REPAIR_BAKEOFF_JSON)
    if danger_repair:
        best = (danger_repair.get("ranked") or [{}])[0]
        summary = best.get("candidate_summary") or {}
        notes.append(
            f"Danger-repair bakeoff best diagnostic variant is {best.get('variant')} with net {summary.get('net_cents')}c and coverage {summary.get('coverage_pct')}; realized-order repair rows make this diagnostic only."
        )
    repair_scoring = load_json(REPAIR_SCORING_BAKEOFF_JSON)
    if repair_scoring:
        best = (repair_scoring.get("ranked") or [{}])[0]
        summary = best.get("candidate_summary") or {}
        notes.append(
            f"Ex-ante repair scoring best is {best.get('scorer')} with net {summary.get('net_cents')}c, coverage {summary.get('coverage_pct')}, and delta {best.get('delta_vs_target_cents')}c; it is frozen separately as low-recross repair."
        )
    boundary_clock = load_json(BOUNDARY_CLOCK_HAZARD_REPAIR_JSON)
    if boundary_clock:
        best = (boundary_clock.get("ranked") or [{}])[0]
        summary = best.get("candidate_summary") or {}
        removed = best.get("removed_summary") or {}
        notes.append(
            f"Boundary-clock hazard repair best diagnostic rule is {best.get('rule')} with net {summary.get('net_cents')}c, coverage {summary.get('coverage_pct')}, and removed-row net {removed.get('net_cents')}c; it is frozen separately for future-only validation."
        )
    boundary_clock_robustness = load_json(BOUNDARY_CLOCK_ROBUSTNESS_JSON)
    if boundary_clock_robustness:
        worst = boundary_clock_robustness.get("worst_leave_one") or {}
        pending = boundary_clock_robustness.get("pending_adverse") or {}
        notes.append(
            f"Boundary-clock robustness pass is {boundary_clock_robustness.get('passes_basic_robustness')}; worst leave-one delta {worst.get('delta_without_market_cents')}c and pending-adverse delta {pending.get('delta_vs_target_cents')}c."
        )
    boundary_clock_fv = load_json(BOUNDARY_CLOCK_FV_OVERLAY_JSON)
    if boundary_clock_fv:
        best = (boundary_clock_fv.get("ranked") or [{}])[0]
        notes.append(
            f"Boundary-clock FV diagnostic best overlay is {best.get('overlay')} with Brier/logloss deltas {best.get('brier_delta_vs_raw')}/{best.get('logloss_delta_vs_raw')} over {best.get('settled')} settled rows."
        )
    boundary_clock_fv_robustness = load_json(BOUNDARY_CLOCK_FV_ROBUSTNESS_JSON)
    if boundary_clock_fv_robustness:
        worst_brier = boundary_clock_fv_robustness.get("worst_leave_one_brier") or {}
        worst_logloss = boundary_clock_fv_robustness.get("worst_leave_one_logloss") or {}
        notes.append(
            f"Boundary-clock FV robustness pass is {boundary_clock_fv_robustness.get('passes_basic_robustness')}; worst leave-one Brier/logloss means {worst_brier.get('brier_mean_without_row')}/{worst_logloss.get('logloss_mean_without_row')}."
        )
    residual = load_json(BOUNDARY_CLOCK_RESIDUAL_JSON)
    if residual:
        clock_wrong = residual.get("clock_wrong_summary") or {}
        residual_wrong = residual.get("residual_wrong_summary") or {}
        notes.append(
            f"Boundary-clock residual attribution: clock hazard explains {clock_wrong.get('rows')} direction-wrong rows for {clock_wrong.get('net_cents')}c; residual non-clock errors are {residual_wrong.get('rows')} rows for {residual_wrong.get('net_cents')}c."
        )
    residual_registry = load_json(FROZEN_BOUNDARY_CLOCK_RESIDUAL_REGISTRY_JSON)
    if residual_registry:
        bucket = residual_registry.get("bucket_summary") or {}
        notes.append(
            f"Frozen boundary-clock residual registry has denominator/entries/settled/net {residual_registry.get('future_denominator')}/{bucket.get('entries')}/{bucket.get('settled')}/{bucket.get('net_cents')}c; registry only, not a candidate."
        )
    side_asymmetry = load_json(SIDE_ASYMMETRY_FV_DIAGNOSTIC_JSON)
    if side_asymmetry:
        top = (side_asymmetry.get("suspicious_buckets") or [{}])[0]
        notes.append(
            f"Side-asymmetry diagnostic top bucket is {top.get('bucket')} with settled {top.get('settled')}, net {top.get('net_cents')}c, avg p {top.get('avg_p_side')}, and win rate {top.get('win_rate')}; registry-only until future rows validate it."
        )
    side_registry = load_json(FROZEN_SIDE_ASYMMETRY_REGISTRY_JSON)
    if side_registry:
        bucket = side_registry.get("bucket_summary") or {}
        non_clock = side_registry.get("non_clock_bucket_summary") or {}
        notes.append(
            f"Frozen side-asymmetry registry has denominator/bucket/non-clock settled {side_registry.get('future_denominator')}/{bucket.get('settled')}/{non_clock.get('settled')}; net {bucket.get('net_cents')}c, registry only."
        )
    side_overlay = load_json(SIDE_ASYMMETRY_FV_OVERLAY_JSON)
    if side_overlay:
        best = (side_overlay.get("ranked") or [{}])[0]
        notes.append(
            f"Side-asymmetry FV overlay diagnostic best is {best.get('overlay')} with Brier/logloss deltas {best.get('brier_delta_vs_raw')}/{best.get('logloss_delta_vs_raw')} and adjusted rows {best.get('adjusted_rows')}."
        )
    side_overlay_frozen = load_json(FROZEN_SIDE_ASYMMETRY_FV_OVERLAY_JSON)
    if side_overlay_frozen:
        candidate = side_overlay_frozen.get("candidate") or {}
        notes.append(
            f"Frozen side-asymmetry FV overlay has denominator/entries/settled/adjusted {side_overlay_frozen.get('future_denominator')}/{candidate.get('entries')}/{candidate.get('settled')}/{candidate.get('adjusted_rows')}; Brier/logloss {candidate.get('brier_mean_delta')}/{candidate.get('logloss_mean_delta')}, blockers {side_overlay_frozen.get('blockers')}."
        )
    runway = load_json(BOUNDARY_CLOCK_PROMOTION_RUNWAY_JSON)
    if runway:
        blockers = [row for row in runway.get("checks") or [] if not row.get("passed") and not str(row.get("name") or "").startswith("residual_registry")]
        notes.append(
            f"Boundary-clock promotion runway ready={runway.get('ready_for_consideration')} with {len(blockers)} frozen promotion blockers; FV/entry robustness {runway.get('diagnostic_fv_robustness_pass')}/{runway.get('diagnostic_entry_robustness_pass')}."
        )
    bridge = load_json(BOUNDARY_CLOCK_FV_ENTRY_BRIDGE_JSON)
    if bridge:
        best = (bridge.get("ranked") or [{}])[0]
        cand = best.get("candidate_summary") or {}
        notes.append(
            f"Boundary-clock FV entry bridge diagnostic best floor {best.get('edge_floor')} has net {cand.get('net_cents')}c, coverage {cand.get('coverage_pct')}, and delta {best.get('delta_vs_target_cents')}c."
        )
    edge_phase = load_json(FROZEN_EDGE_PHASE_SHRINK_JSON)
    if edge_phase:
        ranked = edge_phase.get("ranked") or []
        target_variant = (edge_phase.get("freeze") or {}).get("variant")
        best = next((row for row in ranked if row.get("variant") == target_variant), ranked[0] if ranked else {})
        notes.append(
            f"Frozen edge-phase shrink has denominator/entries/settled {edge_phase.get('future_denominator')}/{edge_phase.get('entries')}/{edge_phase.get('settled')}; {best.get('variant')} Brier/logloss {best.get('brier_mean_delta')}/{best.get('logloss_mean_delta')}."
        )
    edge_gate = load_json(TARGET_FV_EDGE_GATE_JSON)
    if edge_gate:
        ranked = edge_gate.get("ranked") or []
        positive = [row for row in ranked if as_float(row.get("net_cents")) is not None and float(row.get("net_cents") or 0.0) > 0.0]
        best_positive = sorted(positive, key=lambda row: -float(row.get("net_cents") or 0.0))[0] if positive else {}
        if best_positive:
            notes.append(
                f"Adjusted-FV edge gate diagnostic best positive row is {best_positive.get('variant')} floor {best_positive.get('adjusted_edge_floor')} with coverage {best_positive.get('coverage_pct')}, net {best_positive.get('net_cents')}c, blockers {best_positive.get('blockers')}."
            )
    edge_gate_opp = load_json(EDGE_GATE_OPPOSITE_JSON)
    if edge_gate_opp:
        replaced = edge_gate_opp.get("replaced_strategy_summary") or {}
        notes.append(
            f"Edge-gate opposite-side diagnostic found {edge_gate_opp.get('skips_with_opposite')}/{edge_gate_opp.get('target_skipped')} skips with a same-or-later opposite replacement; kept-plus-replacement coverage {replaced.get('coverage_pct')} and net {replaced.get('net_cents')}c, blockers {edge_gate_opp.get('blockers')}."
        )
    frozen_edge_gate = load_json(FROZEN_EDGE_PHASE_EDGE_GATE_JSON)
    if frozen_edge_gate:
        candidate = frozen_edge_gate.get("candidate") or {}
        base = frozen_edge_gate.get("base") or {}
        notes.append(
            f"Frozen edge-phase edge gate has denominator/base/candidate {frozen_edge_gate.get('future_denominator')}/{base.get('entries')}/{candidate.get('entries')}; coverage {candidate.get('coverage_pct')}, net {candidate.get('net_cents')}c."
        )
    frozen_edge_gate_opp = load_json(FROZEN_EDGE_GATE_OPPOSITE_JSON)
    if frozen_edge_gate_opp:
        candidate = frozen_edge_gate_opp.get("candidate") or {}
        notes.append(
            f"Frozen edge-gate opposite replacement has denominator/entries/replacements {frozen_edge_gate_opp.get('future_denominator')}/{candidate.get('entries')}/{frozen_edge_gate_opp.get('skips_with_opposite')}; coverage {candidate.get('coverage_pct')}, net {candidate.get('net_cents')}c."
        )
    low_recross = load_json(FROZEN_LOW_RECROSS_REPAIR_ENTRY_JSON)
    if low_recross:
        candidate = low_recross.get("candidate_summary") or {}
        notes.append(
            f"Frozen low-recross repair entry has denominator/entries/settled {low_recross.get('future_denominator')}/{candidate.get('entries')}/{candidate.get('settled')}; coverage {candidate.get('coverage_pct')}, net {candidate.get('net_cents')}c, blockers {low_recross.get('blockers')}."
        )
    high_raw_p = load_json(FROZEN_HIGH_RAW_P_REPAIR_ENTRY_JSON)
    if high_raw_p:
        candidate = high_raw_p.get("candidate_summary") or {}
        notes.append(
            f"Frozen high-raw-p repair entry has denominator/entries/settled {high_raw_p.get('future_denominator')}/{candidate.get('entries')}/{candidate.get('settled')}; coverage {candidate.get('coverage_pct')}, net {candidate.get('net_cents')}c, blockers {high_raw_p.get('blockers')}."
        )
    boundary_clock_frozen = load_json(FROZEN_BOUNDARY_CLOCK_REPAIR_ENTRY_JSON)
    if boundary_clock_frozen:
        candidate = boundary_clock_frozen.get("candidate_summary") or {}
        notes.append(
            f"Frozen boundary-clock repair entry has denominator/entries/settled {boundary_clock_frozen.get('future_denominator')}/{candidate.get('entries')}/{candidate.get('settled')}; coverage {candidate.get('coverage_pct')}, net {candidate.get('net_cents')}c, blockers {boundary_clock_frozen.get('blockers')}."
        )
    boundary_clock_fv_frozen = load_json(FROZEN_BOUNDARY_CLOCK_FV_OVERLAY_JSON)
    if boundary_clock_fv_frozen:
        candidate = boundary_clock_fv_frozen.get("candidate") or {}
        notes.append(
            f"Frozen boundary-clock FV overlay has denominator/entries/settled/adjusted {boundary_clock_fv_frozen.get('future_denominator')}/{candidate.get('entries')}/{candidate.get('settled')}/{candidate.get('adjusted_rows')}; Brier/logloss {candidate.get('brier_mean_delta')}/{candidate.get('logloss_mean_delta')}, blockers {boundary_clock_fv_frozen.get('blockers')}."
        )
    bridge_frozen = load_json(FROZEN_BOUNDARY_CLOCK_FV_ENTRY_BRIDGE_JSON)
    if bridge_frozen:
        candidate = bridge_frozen.get("candidate_summary") or {}
        notes.append(
            f"Frozen boundary-clock FV entry bridge has denominator/entries/settled/net {bridge_frozen.get('future_denominator')}/{candidate.get('entries')}/{candidate.get('settled')}/{candidate.get('net_cents')}c, blockers {bridge_frozen.get('blockers')}."
        )
    return notes


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
        "# v28 FV Candidate Decision Matrix",
        "",
        "Evidence-ranked FV candidate comparison. This does not promote or trade.",
        "",
        f"- Target: {report.get('target')}",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("current_read") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Candidates",
        "",
        "| family | candidate | complexity | fwd entries | fwd settled | coverage | fit | fwd brier d | fwd logloss d | disc brier d | jackknife | blockers |",
        "|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|---|",
    ])
    for row in report.get("candidate_rows") or []:
        lines.append(
            f"| {row.get('family')} | {row.get('candidate')} | {row.get('complexity')} | "
            f"{row.get('forward_entries')} | {row.get('forward_settled')} | {fmt(row.get('forward_coverage_pct'))} | "
            f"{row.get('coverage_fit')} | {fmt(row.get('forward_brier_delta_vs_raw'))} | "
            f"{fmt(row.get('forward_logloss_delta_vs_raw'))} | {fmt(row.get('discovery_brier_delta_vs_raw'))} | "
            f"{row.get('jackknife_pass')} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    target_fv = report.get("target_coverage_fv") or {}
    if target_fv:
        lines.extend([
            "",
            "## Target-Coverage FV View",
            "",
            f"- Policy: `{target_fv.get('policy')}`",
            f"- Forward denominator: `{target_fv.get('forward_denominator')}`",
            "",
            "| overlay | entries | settled | coverage | W/L | brier d | logloss d | net c | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for row in (target_fv.get("forward") or [])[:7]:
            lines.append(
                f"| {row.get('overlay')} | {row.get('entries')} | {row.get('settled')} | "
                f"{fmt(row.get('coverage_pct'))} | {row.get('wins')}/{row.get('losses')} | "
                f"{fmt(row.get('brier_delta_vs_raw'))} | {fmt(row.get('logloss_delta_vs_raw'))} | "
                f"{fmt(row.get('net_cents_after_entry_fee'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
            )
    target_seq = report.get("target_coverage_sequential") or {}
    if target_seq:
        brier = target_seq.get("brier") or {}
        logloss = target_seq.get("logloss") or {}
        b_boot = brier.get("bootstrap") or {}
        l_boot = logloss.get("bootstrap") or {}
        lines.extend([
            "",
            "## Target-Coverage Sequential Evidence",
            "",
            f"- Overlay: `{target_seq.get('overlay')}`",
            f"- Settled rows: `{target_seq.get('settled_rows')}`",
            f"- Brier mean/p95/prob-negative: `{fmt(brier.get('mean_delta'))}/{fmt(b_boot.get('p95'))}/{fmt(b_boot.get('prob_negative'))}`",
            f"- Logloss mean/p95/prob-negative: `{fmt(logloss.get('mean_delta'))}/{fmt(l_boot.get('p95'))}/{fmt(l_boot.get('prob_negative'))}`",
            f"- Blockers: `{', '.join(target_seq.get('blockers') or []) or 'none'}`",
        ])
    p70_seq = report.get("target_p70_sequential") or {}
    if p70_seq:
        brier = p70_seq.get("brier") or {}
        logloss = p70_seq.get("logloss") or {}
        b_boot = brier.get("bootstrap") or {}
        l_boot = logloss.get("bootstrap") or {}
        lines.extend([
            "",
            "## Target-Coverage p70 Sequential Evidence",
            "",
            f"- Variant: `{p70_seq.get('variant')}`",
            f"- Settled/adjusted rows: `{p70_seq.get('settled_rows')}/{p70_seq.get('adjusted_rows')}`",
            f"- Brier mean/p95/prob-negative: `{fmt(brier.get('mean_delta'))}/{fmt(b_boot.get('p95'))}/{fmt(b_boot.get('prob_negative'))}`",
            f"- Logloss mean/p95/prob-negative: `{fmt(logloss.get('mean_delta'))}/{fmt(l_boot.get('p95'))}/{fmt(l_boot.get('prob_negative'))}`",
            f"- Blockers: `{', '.join(p70_seq.get('blockers') or []) or 'none'}`",
        ])
    confidence_temp = report.get("target_confidence_temperature") or {}
    if confidence_temp:
        lines.extend([
            "",
            "## Confidence Temperature Bakeoff",
            "",
            f"- Best variant: `{confidence_temp.get('best_variant')}`",
            "",
            "| variant | rows | adjusted | brier mean | brier p95 | logloss mean | logloss p95 | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
        ])
        for row in (confidence_temp.get("ranked") or [])[:6]:
            bboot = row.get("brier_bootstrap") or {}
            lboot = row.get("logloss_bootstrap") or {}
            lines.append(
                f"| {row.get('variant')} | {row.get('rows')} | {row.get('adjusted_rows')} | "
                f"{fmt(row.get('brier_mean_delta'))} | {fmt(bboot.get('p95'))} | "
                f"{fmt(row.get('logloss_mean_delta'))} | {fmt(lboot.get('p95'))} | "
                f"{', '.join(row.get('blockers') or []) or 'none'} |"
            )
    p70_fragility = report.get("target_p70_fragility") or {}
    if p70_fragility:
        lines.extend([
            "",
            "## p70 Fragility Stress",
            "",
            f"- Base rows/adjusted rows: `{p70_fragility.get('base_rows')}/{p70_fragility.get('base_adjusted_rows')}`",
            f"- First breaks: `{p70_fragility.get('first_breaks')}`",
        ])
    p70_scale = report.get("target_p70_scale") or {}
    if p70_scale:
        lines.extend([
            "",
            "## p70 Scale Bakeoff",
            "",
            f"- Best scale: `{p70_scale.get('best_scale')}`",
            "",
            "| scale | brier mean | brier p95 | logloss mean | logloss p95 | first any break |",
            "|---:|---:|---:|---:|---:|---:|",
        ])
        for row in (p70_scale.get("ranked") or [])[:6]:
            lines.append(
                f"| {fmt(row.get('scale'))} | {fmt(row.get('brier_mean_delta'))} | "
                f"{fmt(row.get('brier_p95'))} | {fmt(row.get('logloss_mean_delta'))} | "
                f"{fmt(row.get('logloss_p95'))} | {row.get('first_any_break_count')} |"
            )
    p70_eb = report.get("target_p70_empirical_bayes") or {}
    if p70_eb:
        lines.extend([
            "",
            "## p70 Empirical Bayes",
            "",
            f"- Best variant: `{p70_eb.get('best_variant')}`",
            "",
            "| variant | scale | brier mean | brier p95 | logloss mean | logloss p95 | first break |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ])
        for row in (p70_eb.get("ranked") or [])[:6]:
            lines.append(
                f"| {row.get('variant')} | {fmt(row.get('scale'))} | {fmt(row.get('brier_mean_delta'))} | "
                f"{fmt(row.get('brier_p95'))} | {fmt(row.get('logloss_mean_delta'))} | "
                f"{fmt(row.get('logloss_p95'))} | {row.get('first_any_break_count')} |"
            )
    p70_eb_runway = report.get("frozen_target_p70_empirical_bayes_runway") or {}
    if p70_eb_runway:
        lines.extend([
            "",
            "## p70 Empirical Bayes Runway",
            "",
            f"- Future denominator/selected/base-seen: `{p70_eb_runway.get('future_denominator')}/{p70_eb_runway.get('selected_entries')}/{p70_eb_runway.get('base_seen_markets')}`",
            f"- Coverage: `{fmt(p70_eb_runway.get('coverage_pct'))}`",
            f"- Base opportunity summary: `{p70_eb_runway.get('base_opportunity_summary')}`",
        ])
        for note in p70_eb_runway.get("interpretation") or []:
            lines.append(f"- {note}")
    p70_quality = report.get("frozen_target_p70_quality_registry") or {}
    if p70_quality:
        lines.extend([
            "",
            "## p70 Quality Registry",
            "",
            f"- Future denominator/target entries/p70 rows/settled p70: `{p70_quality.get('future_denominator')}/{p70_quality.get('target_entries')}/{p70_quality.get('p70_rows')}/{p70_quality.get('settled_p70_rows')}`",
            "",
            "| tag | rows | settled | W/L | net c | avg raw p |",
            "|---|---:|---:|---:|---:|---:|",
        ])
        for row in (p70_quality.get("tag_rollups") or [])[:10]:
            lines.append(
                f"| {row.get('tag')} | {row.get('rows')} | {row.get('settled')} | "
                f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_raw_p'))} |"
            )
    p70_pending = report.get("frozen_target_p70_pending_sensitivity") or {}
    if p70_pending:
        lines.extend([
            "",
            "## p70 Pending Sensitivity",
            "",
            "| validator | entries | pending adjusted | settled adjusted | raw-only losses |",
            "|---|---:|---:|---:|---:|",
        ])
        for validator in p70_pending.get("validators") or []:
            summary = validator.get("summary") or {}
            lines.append(
                f"| {validator.get('validator')} | {validator.get('entries')} | "
                f"{summary.get('pending_adjusted')} | {summary.get('settled_adjusted')} | "
                f"{summary.get('settled_raw_only_losses')} |"
            )
    target_attr = report.get("target_coverage_attribution") or {}
    if target_attr:
        lines.extend([
            "",
            "## Target-Coverage Attribution",
            "",
        ])
        for note in target_attr.get("interpretation") or []:
            lines.append(f"- {note}")
    lines.extend(["", "## Requirements", ""])
    for requirement in report.get("requirements") or []:
        lines.append(f"- {requirement}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
