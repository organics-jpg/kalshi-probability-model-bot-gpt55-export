"""Live-trade readiness gate for v28 FV candidates.

This report exists because live trading may be permitted before it is justified.
It does not place orders. It only states whether frozen forward evidence clears
the minimum bar for risking capital.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FROZEN_JSON = OUT_DIR / "v28_frozen_forward_candidates_latest.json"
THRESHOLD_JSON = OUT_DIR / "v28_frozen_threshold_challengers_latest.json"
SIDE_AGREEMENT_JSON = OUT_DIR / "v28_frozen_side_agreement_challengers_latest.json"
CONVEX_ESCAPE_JSON = OUT_DIR / "v28_frozen_convex_escape_challengers_latest.json"
RAW_PHYSICS_JSON = OUT_DIR / "v28_frozen_raw_physics_challengers_latest.json"
RAW_P52_SIDEFLIP_JSON = OUT_DIR / "v28_frozen_raw_p52_sideflip_challenger_latest.json"
RAW_P52_RECROSS_ESCAPE_JSON = OUT_DIR / "v28_frozen_raw_p52_recross_escape_challenger_latest.json"
NOISE_SHRINKAGE_JSON = OUT_DIR / "v28_frozen_noise_floor_shrinkage_challengers_latest.json"
PATH_CONFIRMED_JSON = OUT_DIR / "v28_path_confirmed_entry_candidates_latest.json"
RAW_ENTRY_COVERAGE_VALVE_JSON = OUT_DIR / "v28_raw_entry_coverage_valve_latest.json"
FROZEN_APPROVED_ENTRY_BOOK_FV_JSON = OUT_DIR / "v28_frozen_approved_entry_book_fv_latest.json"
TARGET_COVERAGE_FV_SEQ_JSON = OUT_DIR / "v28_target_coverage_fv_sequential_evidence_latest.json"
TARGET_COVERAGE_FV_LIVE_EVIDENCE_JSON = OUT_DIR / "v28_target_coverage_fv_live_evidence_audit_latest.json"
FROZEN_TARGET_COVERAGE_CONSERVATIVE_FV_JSON = OUT_DIR / "v28_frozen_target_coverage_conservative_fv_latest.json"
FROZEN_TARGET_COVERAGE_P70_FV_JSON = OUT_DIR / "v28_frozen_target_coverage_p70_fv_latest.json"
FROZEN_TARGET_COVERAGE_P70_EB_JSON = OUT_DIR / "v28_frozen_target_coverage_p70_empirical_bayes_latest.json"
FROZEN_PATH_STATE_P70_FV_JSON = OUT_DIR / "v28_frozen_path_state_p70_fv_latest.json"
FROZEN_BOUNDARY_RECROSS_SHRINK_FV_JSON = OUT_DIR / "v28_frozen_boundary_recross_shrink_fv_latest.json"
FROZEN_BOUNDARY_TEMPERATURE_FV_JSON = OUT_DIR / "v28_frozen_boundary_temperature_fv_latest.json"
FROZEN_BOUNDARY_ENERGY_FV_ENTRY_JSON = OUT_DIR / "v28_frozen_boundary_energy_fv_entry_latest.json"
FROZEN_EARLY_NO_BOUNDARY_FV_ENTRY_JSON = OUT_DIR / "v28_frozen_early_no_boundary_fv_entry_latest.json"
FROZEN_MID_EDGE_FALSE_CONVICTION_FV_JSON = OUT_DIR / "v28_frozen_mid_edge_false_conviction_fv_latest.json"
FROZEN_COMPOSITE_FALSE_CONVICTION_FV_JSON = OUT_DIR / "v28_frozen_composite_false_conviction_fv_latest.json"
FROZEN_BOUNDARY_CLOCK_FV_JSON = OUT_DIR / "v28_frozen_boundary_clock_fv_overlay_latest.json"
FROZEN_SIDE_ASYMMETRY_FV_JSON = OUT_DIR / "v28_frozen_side_asymmetry_fv_overlay_latest.json"
FROZEN_EDGE_PHASE_SHRINK_FV_JSON = OUT_DIR / "v28_frozen_edge_phase_shrink_fv_latest.json"
FROZEN_EDGE_PHASE_EDGE_GATE_JSON = OUT_DIR / "v28_frozen_edge_phase_edge_gate_latest.json"
FROZEN_EDGE_GATE_OPPOSITE_JSON = OUT_DIR / "v28_frozen_edge_gate_opposite_side_latest.json"
FROZEN_THIN_RECROSS_MIDP_ENTRY_GATE_JSON = OUT_DIR / "v28_frozen_thin_recross_midp_entry_gate_latest.json"
FROZEN_RAW_P52_BOUNDARY_TURBULENCE_SKIP_JSON = OUT_DIR / "v28_frozen_raw_p52_boundary_turbulence_skip_latest.json"
FROZEN_RAW_P52_FAVORITE_VALLEY_SKIP_JSON = OUT_DIR / "v28_frozen_raw_p52_favorite_valley_skip_latest.json"
FROZEN_RAW_P52_MID_EDGE_SKIP_JSON = OUT_DIR / "v28_frozen_raw_p52_mid_edge_skip_latest.json"
FROZEN_RAW_P52_SHADOW_MID_EDGE_SKIP_JSON = OUT_DIR / "v28_frozen_raw_p52_shadow_mid_edge_skip_latest.json"
FROZEN_RAW_P52_BOOK_DISAGREEMENT_SKIP_JSON = OUT_DIR / "v28_frozen_raw_p52_book_disagreement_skip_latest.json"
FROZEN_RAW_P52_BOOK_SHRINK_ENTRY_JSON = OUT_DIR / "v28_frozen_raw_p52_book_shrink_entry_latest.json"
FROZEN_RAW_P52_EARLY_NO_BOUNDARY_SKIP_JSON = OUT_DIR / "v28_frozen_raw_p52_early_no_boundary_skip_latest.json"
FROZEN_RAW_P52_EARLY_NO_BOUNDARY_BAND_SKIP_JSON = OUT_DIR / "v28_frozen_raw_p52_early_no_boundary_band_skip_latest.json"
FROZEN_TARGET_LOSS_TAG_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_target_loss_tag_repair_entry_latest.json"
FROZEN_EARLY_NO_BOUNDARY_DECAY_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_early_no_boundary_decay_repair_entry_latest.json"
FROZEN_MID_EDGE_BOUNDARY_DECEPTION_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_mid_edge_boundary_deception_repair_entry_latest.json"
FROZEN_COMPOSITE_FALSE_CONVICTION_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_composite_false_conviction_repair_entry_latest.json"
FROZEN_GOLDILOCKS_EDGE_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_goldilocks_edge_repair_entry_latest.json"
FROZEN_FALSE_CONVICTION_APPROVED_REPAIR_JSON = OUT_DIR / "v28_frozen_false_conviction_approved_repair_latest.json"
FROZEN_LOW_RECROSS_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_low_recross_repair_entry_latest.json"
FROZEN_HIGH_RAW_P_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_high_raw_p_repair_entry_latest.json"
FROZEN_P50_BOOK_EDGE_ENTRY_JSON = OUT_DIR / "v28_frozen_p50_book_edge_entry_latest.json"
FROZEN_BOOK_PLUS05_ENTRY_JSON = OUT_DIR / "v28_frozen_book_plus05_entry_latest.json"
FROZEN_BOOK_PLUS05_NO_CHEAP_YES_ENTRY_JSON = OUT_DIR / "v28_frozen_book_plus05_no_cheap_yes_entry_latest.json"
FROZEN_BOUNDARY_CLOCK_REPAIR_ENTRY_JSON = OUT_DIR / "v28_frozen_boundary_clock_repair_entry_latest.json"
FROZEN_BOUNDARY_CLOCK_FV_ENTRY_BRIDGE_JSON = OUT_DIR / "v28_frozen_boundary_clock_fv_entry_bridge_latest.json"
FROZEN_WEAK_REVERSAL_RESIDUAL_FV_SHRINK_JSON = OUT_DIR / "v28_frozen_weak_reversal_residual_fv_shrink_latest.json"
FROZEN_NO_MID_EDGE_FV_JSON = OUT_DIR / "v28_frozen_no_mid_edge_fv_latest.json"
FROZEN_WEAK_REVERSAL_RESIDUAL_REPAIR_JSON = OUT_DIR / "v28_frozen_weak_reversal_residual_repair_latest.json"
FROZEN_EARLY_BOUNDARY_WAIT_REPAIR_JSON = OUT_DIR / "v28_frozen_early_boundary_wait_repair_latest.json"
FROZEN_EARLY_BOUNDARY_OPPOSITE_WAIT_REPAIR_JSON = OUT_DIR / "v28_frozen_early_boundary_opposite_wait_repair_latest.json"
FROZEN_EXIT_REDUCE_SUPPRESSION_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
FROZEN_EXIT_REDUCE_YES_SUPPRESSION_JSON = OUT_DIR / "v28_frozen_exit_reduce_yes_suppression_latest.json"
FROZEN_EXIT_BOOK_GAP_SUPPRESSION_JSON = OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json"
SCORECARD_JSON = OUT_DIR / "v28_continuous_scorecard_latest.json"
OUT_JSON = OUT_DIR / "v28_live_trade_readiness_latest.json"
OUT_MD = OUT_DIR / "v28_live_trade_readiness_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def build_report() -> dict[str, Any]:
    frozen = load_json(FROZEN_JSON)
    threshold = load_json(THRESHOLD_JSON)
    side_agreement = load_json(SIDE_AGREEMENT_JSON)
    convex_escape = load_json(CONVEX_ESCAPE_JSON)
    raw_physics = load_json(RAW_PHYSICS_JSON)
    raw_p52_sideflip = load_json(RAW_P52_SIDEFLIP_JSON)
    raw_p52_recross_escape = load_json(RAW_P52_RECROSS_ESCAPE_JSON)
    noise_shrinkage = load_json(NOISE_SHRINKAGE_JSON)
    path_confirmed = load_json(PATH_CONFIRMED_JSON)
    raw_entry_coverage_valve = load_json(RAW_ENTRY_COVERAGE_VALVE_JSON)
    frozen_approved_entry_book_fv = load_json(FROZEN_APPROVED_ENTRY_BOOK_FV_JSON)
    target_coverage_fv_seq = load_json(TARGET_COVERAGE_FV_SEQ_JSON)
    target_coverage_live_evidence = load_json(TARGET_COVERAGE_FV_LIVE_EVIDENCE_JSON)
    frozen_target_conservative = load_json(FROZEN_TARGET_COVERAGE_CONSERVATIVE_FV_JSON)
    frozen_target_p70 = load_json(FROZEN_TARGET_COVERAGE_P70_FV_JSON)
    frozen_target_p70_eb = load_json(FROZEN_TARGET_COVERAGE_P70_EB_JSON)
    frozen_path_state_p70 = load_json(FROZEN_PATH_STATE_P70_FV_JSON)
    frozen_boundary_recross = load_json(FROZEN_BOUNDARY_RECROSS_SHRINK_FV_JSON)
    frozen_boundary_temperature = load_json(FROZEN_BOUNDARY_TEMPERATURE_FV_JSON)
    frozen_boundary_energy_fv_entry = load_json(FROZEN_BOUNDARY_ENERGY_FV_ENTRY_JSON)
    frozen_early_no_boundary_fv_entry = load_json(FROZEN_EARLY_NO_BOUNDARY_FV_ENTRY_JSON)
    frozen_mid_edge_false_conviction = load_json(FROZEN_MID_EDGE_FALSE_CONVICTION_FV_JSON)
    frozen_composite_false_conviction = load_json(FROZEN_COMPOSITE_FALSE_CONVICTION_FV_JSON)
    frozen_boundary_clock_fv = load_json(FROZEN_BOUNDARY_CLOCK_FV_JSON)
    frozen_side_asymmetry_fv = load_json(FROZEN_SIDE_ASYMMETRY_FV_JSON)
    frozen_edge_phase = load_json(FROZEN_EDGE_PHASE_SHRINK_FV_JSON)
    frozen_edge_phase_gate = load_json(FROZEN_EDGE_PHASE_EDGE_GATE_JSON)
    frozen_edge_gate_opposite = load_json(FROZEN_EDGE_GATE_OPPOSITE_JSON)
    frozen_thin_recross_gate = load_json(FROZEN_THIN_RECROSS_MIDP_ENTRY_GATE_JSON)
    frozen_raw_p52_boundary_skip = load_json(FROZEN_RAW_P52_BOUNDARY_TURBULENCE_SKIP_JSON)
    frozen_raw_p52_favorite_valley_skip = load_json(FROZEN_RAW_P52_FAVORITE_VALLEY_SKIP_JSON)
    frozen_raw_p52_mid_edge_skip = load_json(FROZEN_RAW_P52_MID_EDGE_SKIP_JSON)
    frozen_raw_p52_shadow_mid_edge_skip = load_json(FROZEN_RAW_P52_SHADOW_MID_EDGE_SKIP_JSON)
    frozen_raw_p52_book_disagreement_skip = load_json(FROZEN_RAW_P52_BOOK_DISAGREEMENT_SKIP_JSON)
    frozen_raw_p52_book_shrink_entry = load_json(FROZEN_RAW_P52_BOOK_SHRINK_ENTRY_JSON)
    frozen_raw_p52_early_no_boundary_skip = load_json(FROZEN_RAW_P52_EARLY_NO_BOUNDARY_SKIP_JSON)
    frozen_raw_p52_early_no_boundary_band_skip = load_json(FROZEN_RAW_P52_EARLY_NO_BOUNDARY_BAND_SKIP_JSON)
    frozen_target_loss_tag_repair = load_json(FROZEN_TARGET_LOSS_TAG_REPAIR_ENTRY_JSON)
    frozen_early_no_boundary_decay_repair = load_json(FROZEN_EARLY_NO_BOUNDARY_DECAY_REPAIR_ENTRY_JSON)
    frozen_mid_edge_boundary_deception_repair = load_json(FROZEN_MID_EDGE_BOUNDARY_DECEPTION_REPAIR_ENTRY_JSON)
    frozen_composite_false_conviction_repair = load_json(FROZEN_COMPOSITE_FALSE_CONVICTION_REPAIR_ENTRY_JSON)
    frozen_goldilocks_edge_repair = load_json(FROZEN_GOLDILOCKS_EDGE_REPAIR_ENTRY_JSON)
    frozen_false_conviction_approved_repair = load_json(FROZEN_FALSE_CONVICTION_APPROVED_REPAIR_JSON)
    frozen_low_recross_repair = load_json(FROZEN_LOW_RECROSS_REPAIR_ENTRY_JSON)
    frozen_high_raw_p_repair = load_json(FROZEN_HIGH_RAW_P_REPAIR_ENTRY_JSON)
    frozen_p50_book_edge_entry = load_json(FROZEN_P50_BOOK_EDGE_ENTRY_JSON)
    frozen_book_plus05_entry = load_json(FROZEN_BOOK_PLUS05_ENTRY_JSON)
    frozen_book_plus05_no_cheap_yes_entry = load_json(FROZEN_BOOK_PLUS05_NO_CHEAP_YES_ENTRY_JSON)
    frozen_boundary_clock_repair = load_json(FROZEN_BOUNDARY_CLOCK_REPAIR_ENTRY_JSON)
    frozen_boundary_clock_fv_entry_bridge = load_json(FROZEN_BOUNDARY_CLOCK_FV_ENTRY_BRIDGE_JSON)
    frozen_weak_reversal_residual_fv_shrink = load_json(FROZEN_WEAK_REVERSAL_RESIDUAL_FV_SHRINK_JSON)
    frozen_no_mid_edge_fv = load_json(FROZEN_NO_MID_EDGE_FV_JSON)
    frozen_weak_reversal_residual_repair = load_json(FROZEN_WEAK_REVERSAL_RESIDUAL_REPAIR_JSON)
    frozen_early_boundary_wait_repair = load_json(FROZEN_EARLY_BOUNDARY_WAIT_REPAIR_JSON)
    frozen_early_boundary_opposite_wait_repair = load_json(FROZEN_EARLY_BOUNDARY_OPPOSITE_WAIT_REPAIR_JSON)
    frozen_exit_reduce_suppression = load_json(FROZEN_EXIT_REDUCE_SUPPRESSION_JSON)
    frozen_exit_reduce_yes_suppression = load_json(FROZEN_EXIT_REDUCE_YES_SUPPRESSION_JSON)
    frozen_exit_book_gap_suppression = load_json(FROZEN_EXIT_BOOK_GAP_SUPPRESSION_JSON)
    scorecard = load_json(SCORECARD_JSON).get("summary", {})
    rows = []
    for gate_name, payload in [
        ("primary_p60", frozen),
        ("threshold_p58", threshold),
        ("side_agreement", side_agreement),
        ("convex_escape", convex_escape),
        ("raw_physics", raw_physics),
        ("raw_p52_sideflip", raw_p52_sideflip),
        ("raw_p52_recross_escape", raw_p52_recross_escape),
        ("noise_shrinkage", noise_shrinkage),
    ]:
        for row in payload.get("summary") or []:
            rows.append({"gate": gate_name, **row})
    candidates: list[dict[str, Any]] = []
    for row in rows:
        fv_checks = row.get("fv_validation_checks") or {}
        exec_checks = row.get("execution_promotion_checks") or {}
        blockers = []
        blockers.extend(f"fv:{item}" for item in (fv_checks.get("blockers") or []))
        blockers.extend(f"execution:{item}" for item in (exec_checks.get("blockers") or []))
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": row.get("gate"),
            "policy": row.get("policy"),
            "entries": row.get("entries"),
            "settled": row.get("settled"),
            "coverage_pct": row.get("coverage_pct"),
            "net_cents_after_entry_fee": row.get("net_cents_after_entry_fee"),
            "avg_brier": row.get("avg_brier"),
            "blockers": blockers,
            "live_ready": not blockers,
        })
    for row in path_confirmed.get("summaries") or []:
        blockers = path_candidate_blockers(row)
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "path_confirmed",
            "policy": row.get("policy"),
            "entries": row.get("entries"),
            "settled": row.get("settled"),
            "approved_entry_count": row.get("approved_entry_count"),
            "added_reject_count": row.get("added_reject_count"),
            "simulated_share": row.get("simulated_share"),
            "coverage_pct": row.get("coverage_pct"),
            "net_cents_after_entry_fee": row.get("net_cents_after_entry_fee"),
            "avg_brier": row.get("avg_brier"),
            "avg_logloss": row.get("avg_logloss"),
            "blockers": blockers,
            "live_ready": not blockers,
        })
    for row in raw_entry_coverage_valve.get("ranked") or []:
        forward = row.get("forward") or {}
        score = forward.get("coverage_valve") or {}
        blockers = [f"fv:{item}" for item in (forward.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "raw_entry_coverage_valve",
            "policy": row.get("policy"),
            "entries": score.get("entries"),
            "settled": score.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": score.get("coverage_pct"),
            "net_cents_after_entry_fee": score.get("net_cents_after_entry_fee"),
            "avg_brier": score.get("avg_brier"),
            "avg_logloss": score.get("avg_logloss"),
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_approved_entry_book_fv:
        candidate = frozen_approved_entry_book_fv.get("candidate") or {}
        blockers = [f"fv:{item}" for item in (candidate.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "approved_entry_book_fv",
            "policy": "actual_approved_entries + book_probability",
            "entries": frozen_approved_entry_book_fv.get("future_entries"),
            "settled": frozen_approved_entry_book_fv.get("future_settled"),
            "approved_entry_count": frozen_approved_entry_book_fv.get("future_settled"),
            "added_reject_count": 0,
            "simulated_share": 0.0,
            "coverage_pct": None,
            "net_cents_after_entry_fee": candidate.get("gross_cents"),
            "avg_brier": candidate.get("brier_delta_vs_raw"),
            "avg_logloss": candidate.get("logloss_delta_vs_raw"),
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if target_coverage_fv_seq:
        blockers = [f"fv:{item}" for item in (target_coverage_fv_seq.get("blockers") or [])]
        blockers.extend(f"live_evidence:{item}" for item in (target_coverage_live_evidence.get("blockers") or []))
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        brier = target_coverage_fv_seq.get("brier") or {}
        logloss = target_coverage_fv_seq.get("logloss") or {}
        candidates.append({
            "gate": "target_coverage_fv",
            "policy": f"{target_coverage_fv_seq.get('policy')} + {target_coverage_fv_seq.get('overlay')}",
            "entries": target_coverage_fv_seq.get("entries"),
            "settled": target_coverage_fv_seq.get("settled_rows"),
            "approved_entry_count": target_coverage_live_evidence.get("approved_entry_rows"),
            "added_reject_count": target_coverage_live_evidence.get("simulated_or_rejected_rows"),
            "simulated_share": target_coverage_live_evidence.get("simulated_share"),
            "coverage_pct": target_coverage_fv_seq.get("coverage_pct"),
            "net_cents_after_entry_fee": target_coverage_fv_seq.get("net_cents_after_entry_fee"),
            "avg_brier": brier.get("mean_delta"),
            "avg_logloss": logloss.get("mean_delta"),
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_target_conservative:
        best = (frozen_target_conservative.get("ranked") or [{}])[0]
        blockers = [f"fv:{item}" for item in (best.get("blockers") or [])]
        coverage = frozen_target_conservative.get("coverage_pct")
        if coverage is None:
            blockers.append("fv:no_forward_coverage_yet")
        elif float(coverage) < 75.0:
            blockers.append("fv:coverage_too_low")
        elif float(coverage) > 90.0:
            blockers.append("fv:coverage_too_high")
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "target_coverage_conservative_fv",
            "policy": f"{(frozen_target_conservative.get('freeze') or {}).get('entry_policy')} + {best.get('variant')}",
            "entries": frozen_target_conservative.get("entries"),
            "settled": frozen_target_conservative.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": coverage,
            "net_cents_after_entry_fee": best.get("net_cents"),
            "avg_brier": best.get("brier_mean_delta"),
            "avg_logloss": best.get("logloss_mean_delta"),
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_target_p70:
        best = (frozen_target_p70.get("ranked") or [{}])[0]
        blockers = [f"fv:{item}" for item in (best.get("blockers") or [])]
        coverage = frozen_target_p70.get("coverage_pct")
        if coverage is None:
            blockers.append("fv:no_forward_coverage_yet")
        elif float(coverage) < 75.0:
            blockers.append("fv:coverage_too_low")
        elif float(coverage) > 90.0:
            blockers.append("fv:coverage_too_high")
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "target_coverage_p70_fv",
            "policy": f"{(frozen_target_p70.get('freeze') or {}).get('entry_policy')} + {best.get('variant')}",
            "entries": frozen_target_p70.get("entries"),
            "settled": frozen_target_p70.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": coverage,
            "net_cents_after_entry_fee": best.get("net_cents"),
            "avg_brier": best.get("brier_mean_delta"),
            "avg_logloss": best.get("logloss_mean_delta"),
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_target_p70_eb:
        best = (frozen_target_p70_eb.get("ranked") or [{}])[0]
        blockers = [f"fv:{item}" for item in (best.get("blockers") or [])]
        coverage = frozen_target_p70_eb.get("coverage_pct")
        if coverage is None:
            blockers.append("fv:no_forward_coverage_yet")
        elif float(coverage) < 75.0:
            blockers.append("fv:coverage_too_low")
        elif float(coverage) > 90.0:
            blockers.append("fv:coverage_too_high")
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "target_coverage_p70_empirical_bayes",
            "policy": f"{(frozen_target_p70_eb.get('freeze') or {}).get('entry_policy')} + {best.get('variant')}",
            "entries": frozen_target_p70_eb.get("entries"),
            "settled": frozen_target_p70_eb.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": coverage,
            "net_cents_after_entry_fee": best.get("net_cents"),
            "avg_brier": best.get("brier_mean_delta"),
            "avg_logloss": best.get("logloss_mean_delta"),
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_path_state_p70:
        ranked = frozen_path_state_p70.get("ranked") or []
        target_variant = (frozen_path_state_p70.get("freeze") or {}).get("variant")
        best = next((row for row in ranked if row.get("variant") == target_variant), ranked[0] if ranked else {})
        blockers = [f"fv:{item}" for item in (best.get("blockers") or [])]
        coverage = frozen_path_state_p70.get("future_coverage_pct")
        if coverage is None:
            blockers.append("fv:no_forward_coverage_yet")
        elif float(coverage) < 75.0:
            blockers.append("fv:coverage_too_low")
        elif float(coverage) > 90.0:
            blockers.append("fv:coverage_too_high")
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "path_state_p70_fv",
            "policy": f"{(frozen_path_state_p70.get('freeze') or {}).get('entry_policy')} + {best.get('variant')}",
            "entries": frozen_path_state_p70.get("future_entries"),
            "settled": frozen_path_state_p70.get("future_settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": coverage,
            "net_cents_after_entry_fee": best.get("net_cents"),
            "avg_brier": best.get("brier_mean_delta"),
            "avg_logloss": best.get("logloss_mean_delta"),
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_boundary_recross:
        ranked = frozen_boundary_recross.get("ranked") or []
        target_variant = (frozen_boundary_recross.get("freeze") or {}).get("variant")
        best = next((row for row in ranked if row.get("variant") == target_variant), ranked[0] if ranked else {})
        blockers = [f"fv:{item}" for item in (best.get("blockers") or [])]
        coverage = frozen_boundary_recross.get("coverage_pct")
        if coverage is None:
            blockers.append("fv:no_forward_coverage_yet")
        elif float(coverage) < 75.0:
            blockers.append("fv:coverage_too_low")
        elif float(coverage) > 90.0:
            blockers.append("fv:coverage_too_high")
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "boundary_recross_shrink_fv",
            "policy": f"{(frozen_boundary_recross.get('freeze') or {}).get('entry_policy')} + {best.get('variant')}",
            "entries": frozen_boundary_recross.get("entries"),
            "settled": frozen_boundary_recross.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": coverage,
            "net_cents_after_entry_fee": best.get("net_cents"),
            "avg_brier": best.get("brier_mean_delta"),
            "avg_logloss": best.get("logloss_mean_delta"),
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_boundary_temperature:
        candidate = frozen_boundary_temperature.get("candidate") or {}
        blockers = [f"fv:{item}" for item in (frozen_boundary_temperature.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "boundary_temperature_fv",
            "policy": f"{(frozen_boundary_temperature.get('freeze') or {}).get('entry_policy')} + {(frozen_boundary_temperature.get('freeze') or {}).get('variant')}",
            "entries": frozen_boundary_temperature.get("entries"),
            "settled": candidate.get("rows"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": None,
            "net_cents_after_entry_fee": None,
            "avg_brier": candidate.get("brier_mean_delta"),
            "avg_logloss": candidate.get("logloss_mean_delta"),
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_boundary_energy_fv_entry:
        summary = frozen_boundary_energy_fv_entry.get("future_candidate_summary") or {}
        blockers = [f"fv_entry:{item}" for item in (frozen_boundary_energy_fv_entry.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "boundary_energy_fv_entry",
            "policy": (frozen_boundary_energy_fv_entry.get("freeze") or {}).get("candidate"),
            "entries": summary.get("entries"),
            "settled": summary.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": summary.get("coverage_pct"),
            "net_cents_after_entry_fee": summary.get("net_cents"),
            "avg_brier": summary.get("avg_brier"),
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_early_no_boundary_fv_entry:
        summary = frozen_early_no_boundary_fv_entry.get("future_candidate_summary") or {}
        blockers = [f"fv_entry:{item}" for item in (frozen_early_no_boundary_fv_entry.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "early_no_boundary_fv_entry",
            "policy": (frozen_early_no_boundary_fv_entry.get("freeze") or {}).get("candidate"),
            "entries": summary.get("entries"),
            "settled": summary.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": summary.get("coverage_pct"),
            "net_cents_after_entry_fee": summary.get("net_cents"),
            "avg_brier": summary.get("avg_brier"),
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_mid_edge_false_conviction:
        ranked = frozen_mid_edge_false_conviction.get("ranked") or []
        target_variant = (frozen_mid_edge_false_conviction.get("freeze") or {}).get("variant")
        best = next((row for row in ranked if row.get("variant") == target_variant), ranked[0] if ranked else {})
        blockers = [f"fv:{item}" for item in (best.get("blockers") or [])]
        coverage = frozen_mid_edge_false_conviction.get("coverage_pct")
        if coverage is None:
            blockers.append("fv:no_forward_coverage_yet")
        elif float(coverage) < 75.0:
            blockers.append("fv:coverage_too_low")
        elif float(coverage) > 90.0:
            blockers.append("fv:coverage_too_high")
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "mid_edge_false_conviction_fv",
            "policy": f"{(frozen_mid_edge_false_conviction.get('freeze') or {}).get('entry_policy')} + {best.get('variant')}",
            "entries": frozen_mid_edge_false_conviction.get("entries"),
            "settled": frozen_mid_edge_false_conviction.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": coverage,
            "net_cents_after_entry_fee": best.get("net_cents"),
            "avg_brier": best.get("brier_mean_delta"),
            "avg_logloss": best.get("logloss_mean_delta"),
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_composite_false_conviction:
        ranked = frozen_composite_false_conviction.get("ranked") or []
        target_variant = (frozen_composite_false_conviction.get("freeze") or {}).get("variant")
        best = next((row for row in ranked if row.get("variant") == target_variant), ranked[0] if ranked else {})
        blockers = [f"fv:{item}" for item in (best.get("blockers") or [])]
        coverage = frozen_composite_false_conviction.get("coverage_pct")
        if coverage is None:
            blockers.append("fv:no_forward_coverage_yet")
        elif float(coverage) < 75.0:
            blockers.append("fv:coverage_too_low")
        elif float(coverage) > 90.0:
            blockers.append("fv:coverage_too_high")
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "composite_false_conviction_fv",
            "policy": f"{(frozen_composite_false_conviction.get('freeze') or {}).get('entry_policy')} + {best.get('variant')}",
            "entries": frozen_composite_false_conviction.get("entries"),
            "settled": frozen_composite_false_conviction.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": coverage,
            "net_cents_after_entry_fee": best.get("net_cents"),
            "avg_brier": best.get("brier_mean_delta"),
            "avg_logloss": best.get("logloss_mean_delta"),
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_boundary_clock_fv:
        candidate = frozen_boundary_clock_fv.get("candidate") or {}
        blockers = [f"fv:{item}" for item in (frozen_boundary_clock_fv.get("blockers") or [])]
        coverage = candidate.get("coverage_pct")
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "boundary_clock_fv_overlay",
            "policy": f"{(frozen_boundary_clock_fv.get('freeze') or {}).get('entry_policy')} + {(frozen_boundary_clock_fv.get('freeze') or {}).get('variant')}",
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": coverage,
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": candidate.get("brier_mean_delta"),
            "avg_logloss": candidate.get("logloss_mean_delta"),
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_side_asymmetry_fv:
        candidate = frozen_side_asymmetry_fv.get("candidate") or {}
        blockers = [f"fv:{item}" for item in (frozen_side_asymmetry_fv.get("blockers") or [])]
        coverage = candidate.get("coverage_pct")
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "side_asymmetry_fv_overlay",
            "policy": f"{(frozen_side_asymmetry_fv.get('freeze') or {}).get('entry_policy')} + {(frozen_side_asymmetry_fv.get('freeze') or {}).get('variant')}",
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": coverage,
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": candidate.get("brier_mean_delta"),
            "avg_logloss": candidate.get("logloss_mean_delta"),
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_edge_phase:
        ranked = frozen_edge_phase.get("ranked") or []
        target_variant = (frozen_edge_phase.get("freeze") or {}).get("variant")
        best = next((row for row in ranked if row.get("variant") == target_variant), ranked[0] if ranked else {})
        blockers = [f"fv:{item}" for item in (best.get("blockers") or [])]
        coverage = frozen_edge_phase.get("coverage_pct")
        if coverage is None:
            blockers.append("fv:no_forward_coverage_yet")
        elif float(coverage) < 75.0:
            blockers.append("fv:coverage_too_low")
        elif float(coverage) > 90.0:
            blockers.append("fv:coverage_too_high")
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "edge_phase_shrink_fv",
            "policy": f"{(frozen_edge_phase.get('freeze') or {}).get('entry_policy')} + {best.get('variant')}",
            "entries": frozen_edge_phase.get("entries"),
            "settled": frozen_edge_phase.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": coverage,
            "net_cents_after_entry_fee": best.get("net_cents"),
            "avg_brier": best.get("brier_mean_delta"),
            "avg_logloss": best.get("logloss_mean_delta"),
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_edge_phase_gate:
        candidate = frozen_edge_phase_gate.get("candidate") or {}
        blockers = [f"entry:{item}" for item in (candidate.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "edge_phase_edge_gate",
            "policy": f"{(frozen_edge_phase_gate.get('freeze') or {}).get('fv_variant')} adjusted_edge_floor={(frozen_edge_phase_gate.get('freeze') or {}).get('adjusted_edge_floor')}",
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_edge_gate_opposite:
        candidate = frozen_edge_gate_opposite.get("candidate") or {}
        blockers = [f"entry:{item}" for item in (candidate.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "edge_gate_opposite_side",
            "policy": "edge_phase_skip_then_same_or_later_opposite",
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_thin_recross_gate:
        candidate = frozen_thin_recross_gate.get("candidate") or {}
        blockers = [f"entry:{item}" for item in (candidate.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "thin_recross_midp_entry_gate",
            "policy": (frozen_thin_recross_gate.get("freeze") or {}).get("candidate"),
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_raw_p52_boundary_skip:
        candidate = frozen_raw_p52_boundary_skip.get("candidate") or {}
        blockers = [f"entry:{item}" for item in (candidate.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "raw_p52_boundary_turbulence_skip",
            "policy": (frozen_raw_p52_boundary_skip.get("freeze") or {}).get("candidate"),
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": candidate.get("avg_brier"),
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    for gate, payload in [
        ("raw_p52_favorite_valley_skip", frozen_raw_p52_favorite_valley_skip),
        ("raw_p52_mid_edge_skip", frozen_raw_p52_mid_edge_skip),
        ("raw_p52_shadow_mid_edge_skip", frozen_raw_p52_shadow_mid_edge_skip),
        ("raw_p52_book_disagreement_skip", frozen_raw_p52_book_disagreement_skip),
        ("raw_p52_book_shrink_entry", frozen_raw_p52_book_shrink_entry),
        ("raw_p52_early_no_boundary_skip", frozen_raw_p52_early_no_boundary_skip),
        ("raw_p52_early_no_boundary_band_skip", frozen_raw_p52_early_no_boundary_band_skip),
    ]:
        if not payload:
            continue
        candidate = payload.get("candidate_summary") or {}
        entries = candidate.get("entries") or 0
        sim_count = candidate.get("sim_count") or 0
        simulated_share = (float(sim_count) / float(entries)) if entries else None
        blockers = [f"entry:{item}" for item in (payload.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": gate,
            "policy": (payload.get("freeze") or {}).get("candidate"),
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": candidate.get("actual_count"),
            "added_reject_count": candidate.get("sim_count"),
            "simulated_share": simulated_share,
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_target_loss_tag_repair:
        candidate = frozen_target_loss_tag_repair.get("candidate_summary") or {}
        blockers = [f"entry:{item}" for item in (frozen_target_loss_tag_repair.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "target_loss_tag_repair_entry",
            "policy": (frozen_target_loss_tag_repair.get("freeze") or {}).get("candidate"),
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_early_no_boundary_decay_repair:
        candidate = frozen_early_no_boundary_decay_repair.get("candidate_summary") or {}
        blockers = [f"entry:{item}" for item in (frozen_early_no_boundary_decay_repair.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "early_no_boundary_decay_repair_entry",
            "policy": (frozen_early_no_boundary_decay_repair.get("freeze") or {}).get("candidate"),
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_mid_edge_boundary_deception_repair:
        candidate = frozen_mid_edge_boundary_deception_repair.get("candidate_summary") or {}
        blockers = [f"entry:{item}" for item in (frozen_mid_edge_boundary_deception_repair.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "mid_edge_boundary_deception_repair_entry",
            "policy": (frozen_mid_edge_boundary_deception_repair.get("freeze") or {}).get("candidate"),
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_composite_false_conviction_repair:
        candidate = frozen_composite_false_conviction_repair.get("candidate_summary") or {}
        blockers = [f"entry:{item}" for item in (frozen_composite_false_conviction_repair.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "composite_false_conviction_repair_entry",
            "policy": (frozen_composite_false_conviction_repair.get("freeze") or {}).get("candidate"),
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_goldilocks_edge_repair:
        future = frozen_goldilocks_edge_repair.get("frozen_future") or {}
        candidate = future.get("candidate_summary") or {}
        blockers = [f"entry:{item}" for item in (future.get("blockers") or frozen_goldilocks_edge_repair.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "goldilocks_edge_repair_entry",
            "policy": (frozen_goldilocks_edge_repair.get("freeze") or {}).get("candidate"),
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_false_conviction_approved_repair:
        candidate = frozen_false_conviction_approved_repair.get("candidate_summary") or {}
        blockers = [f"entry:{item}" for item in (frozen_false_conviction_approved_repair.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "false_conviction_approved_repair",
            "policy": (frozen_false_conviction_approved_repair.get("freeze") or {}).get("candidate"),
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": frozen_false_conviction_approved_repair.get("approved_count"),
            "added_reject_count": frozen_false_conviction_approved_repair.get("reconstructed_count"),
            "simulated_share": frozen_false_conviction_approved_repair.get("reconstructed_share"),
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_low_recross_repair:
        candidate = frozen_low_recross_repair.get("candidate_summary") or {}
        blockers = [f"entry:{item}" for item in (frozen_low_recross_repair.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "low_recross_repair_entry",
            "policy": (frozen_low_recross_repair.get("freeze") or {}).get("candidate"),
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_high_raw_p_repair:
        candidate = frozen_high_raw_p_repair.get("candidate_summary") or {}
        blockers = [f"entry:{item}" for item in (frozen_high_raw_p_repair.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "high_raw_p_repair_entry",
            "policy": (frozen_high_raw_p_repair.get("freeze") or {}).get("candidate"),
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_p50_book_edge_entry:
        candidate = frozen_p50_book_edge_entry.get("summary") or {}
        blockers = [f"entry:{item}" for item in (frozen_p50_book_edge_entry.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "p50_book_edge_entry",
            "policy": (frozen_p50_book_edge_entry.get("freeze") or {}).get("candidate"),
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": candidate.get("approved_entry_count"),
            "added_reject_count": candidate.get("simulated_or_rejected_count"),
            "simulated_share": candidate.get("simulated_share"),
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("gross_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_book_plus05_entry:
        candidate = frozen_book_plus05_entry.get("summary") or {}
        blockers = [f"entry:{item}" for item in (frozen_book_plus05_entry.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "book_plus05_entry",
            "policy": (frozen_book_plus05_entry.get("freeze") or {}).get("candidate"),
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": candidate.get("approved_entry_count"),
            "added_reject_count": candidate.get("simulated_or_rejected_count"),
            "simulated_share": candidate.get("simulated_share"),
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("gross_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_book_plus05_no_cheap_yes_entry:
        candidate = frozen_book_plus05_no_cheap_yes_entry.get("summary") or {}
        blockers = [f"entry:{item}" for item in (frozen_book_plus05_no_cheap_yes_entry.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "book_plus05_no_cheap_yes_entry",
            "policy": (frozen_book_plus05_no_cheap_yes_entry.get("freeze") or {}).get("candidate"),
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": candidate.get("approved_entry_count"),
            "added_reject_count": candidate.get("simulated_or_rejected_count"),
            "simulated_share": candidate.get("simulated_share"),
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("gross_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_boundary_clock_repair:
        candidate = frozen_boundary_clock_repair.get("candidate_summary") or {}
        blockers = [f"entry:{item}" for item in (frozen_boundary_clock_repair.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "boundary_clock_repair_entry",
            "policy": (frozen_boundary_clock_repair.get("freeze") or {}).get("candidate"),
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_boundary_clock_fv_entry_bridge:
        candidate = frozen_boundary_clock_fv_entry_bridge.get("candidate_summary") or {}
        blockers = [f"entry:{item}" for item in (frozen_boundary_clock_fv_entry_bridge.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "boundary_clock_fv_entry_bridge",
            "policy": (frozen_boundary_clock_fv_entry_bridge.get("freeze") or {}).get("candidate"),
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_weak_reversal_residual_repair:
        candidate = frozen_weak_reversal_residual_repair.get("candidate_summary") or {}
        blockers = [f"entry:{item}" for item in (frozen_weak_reversal_residual_repair.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "weak_reversal_residual_repair",
            "policy": frozen_weak_reversal_residual_repair.get("policy"),
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_weak_reversal_residual_fv_shrink:
        weak = frozen_weak_reversal_residual_fv_shrink.get("weak_summary") or {}
        blockers = [f"fv:{item}" for item in (frozen_weak_reversal_residual_fv_shrink.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "weak_reversal_residual_fv_shrink",
            "policy": (frozen_weak_reversal_residual_fv_shrink.get("freeze") or {}).get("variant"),
            "entries": weak.get("entries"),
            "settled": (frozen_weak_reversal_residual_fv_shrink.get("variant_all") or {}).get("rows"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": weak.get("coverage_pct"),
            "net_cents_after_entry_fee": weak.get("net_cents"),
            "avg_brier": frozen_weak_reversal_residual_fv_shrink.get("brier_delta_vs_raw"),
            "avg_logloss": frozen_weak_reversal_residual_fv_shrink.get("logloss_delta_vs_raw"),
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_no_mid_edge_fv:
        target_summary = frozen_no_mid_edge_fv.get("target_summary") or {}
        blockers = [f"fv:{item}" for item in (frozen_no_mid_edge_fv.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "no_mid_edge_fv",
            "policy": (frozen_no_mid_edge_fv.get("freeze") or {}).get("variant"),
            "entries": target_summary.get("entries"),
            "settled": (frozen_no_mid_edge_fv.get("variant") or {}).get("rows"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": target_summary.get("coverage_pct"),
            "net_cents_after_entry_fee": target_summary.get("net_cents"),
            "avg_brier": frozen_no_mid_edge_fv.get("brier_delta_vs_raw"),
            "avg_logloss": frozen_no_mid_edge_fv.get("logloss_delta_vs_raw"),
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_early_boundary_wait_repair:
        candidate = frozen_early_boundary_wait_repair.get("candidate_summary") or {}
        blockers = [f"entry:{item}" for item in (frozen_early_boundary_wait_repair.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "early_boundary_wait_repair",
            "policy": frozen_early_boundary_wait_repair.get("policy"),
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_early_boundary_opposite_wait_repair:
        candidate = frozen_early_boundary_opposite_wait_repair.get("candidate_summary") or {}
        blockers = [f"entry:{item}" for item in (frozen_early_boundary_opposite_wait_repair.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "early_boundary_opposite_wait_repair",
            "policy": frozen_early_boundary_opposite_wait_repair.get("policy"),
            "entries": candidate.get("entries"),
            "settled": candidate.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": candidate.get("coverage_pct"),
            "net_cents_after_entry_fee": candidate.get("net_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_exit_reduce_suppression:
        summary = frozen_exit_reduce_suppression.get("summary") or {}
        blockers = [f"exit:{item}" for item in (frozen_exit_reduce_suppression.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "exit_reduce_suppression",
            "policy": (frozen_exit_reduce_suppression.get("freeze") or {}).get("candidate"),
            "entries": summary.get("rows"),
            "settled": summary.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": None,
            "net_cents_after_entry_fee": summary.get("delta_vs_current_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_exit_reduce_yes_suppression:
        summary = frozen_exit_reduce_yes_suppression.get("summary") or {}
        blockers = [f"exit:{item}" for item in (frozen_exit_reduce_yes_suppression.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "exit_reduce_yes_suppression",
            "policy": (frozen_exit_reduce_yes_suppression.get("freeze") or {}).get("candidate"),
            "entries": summary.get("rows"),
            "settled": summary.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": None,
            "net_cents_after_entry_fee": summary.get("delta_vs_current_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    if frozen_exit_book_gap_suppression:
        summary = frozen_exit_book_gap_suppression.get("summary") or {}
        blockers = [f"exit:{item}" for item in (frozen_exit_book_gap_suppression.get("blockers") or [])]
        if scorecard.get("risk_stop") is True:
            blockers.append("control_risk_stop_active")
        candidates.append({
            "gate": "exit_book_gap_suppression",
            "policy": (frozen_exit_book_gap_suppression.get("freeze") or {}).get("candidate"),
            "entries": summary.get("rows"),
            "settled": summary.get("settled"),
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "coverage_pct": None,
            "net_cents_after_entry_fee": summary.get("delta_vs_current_cents"),
            "avg_brier": None,
            "avg_logloss": None,
            "blockers": blockers,
            "live_ready": not blockers,
        })
    return {
        "permission_note": "User has allowed trades if deemed necessary; this gate decides whether they are justified by evidence.",
        "risk_note": "No candidate should be traded live while this report says live_ready=false.",
        "freeze_ts": frozen.get("freeze_ts"),
        "threshold_freeze_ts": threshold.get("freeze_ts"),
        "side_agreement_freeze_ts": side_agreement.get("freeze_ts"),
        "convex_escape_freeze_ts": convex_escape.get("freeze_ts"),
        "raw_physics_freeze_ts": raw_physics.get("freeze_ts"),
        "raw_p52_sideflip_freeze_ts": raw_p52_sideflip.get("freeze_ts"),
        "raw_p52_recross_escape_freeze_ts": raw_p52_recross_escape.get("freeze_ts"),
        "noise_shrinkage_freeze_ts": noise_shrinkage.get("freeze_ts"),
        "path_confirmed_freeze_ts": path_confirmed.get("freeze_ts"),
        "raw_entry_coverage_valve_freeze_ts": raw_entry_coverage_valve.get("freeze_ts"),
        "approved_entry_book_fv_freeze_ts": (frozen_approved_entry_book_fv.get("freeze") or {}).get("freeze_ts_utc"),
        "target_coverage_fv_policy": target_coverage_fv_seq.get("policy"),
        "target_coverage_fv_overlay": target_coverage_fv_seq.get("overlay"),
        "target_coverage_conservative_fv_freeze_ts": (frozen_target_conservative.get("freeze") or {}).get("freeze_ts_utc"),
        "target_coverage_p70_fv_freeze_ts": (frozen_target_p70.get("freeze") or {}).get("freeze_ts_utc"),
        "target_coverage_p70_empirical_bayes_freeze_ts": (frozen_target_p70_eb.get("freeze") or {}).get("freeze_ts_utc"),
        "path_state_p70_fv_freeze_ts": (frozen_path_state_p70.get("freeze") or {}).get("freeze_ts_utc"),
        "boundary_recross_shrink_fv_freeze_ts": (frozen_boundary_recross.get("freeze") or {}).get("freeze_ts_utc"),
        "boundary_temperature_fv_freeze_ts": (frozen_boundary_temperature.get("freeze") or {}).get("freeze_ts_utc"),
        "boundary_energy_fv_entry_freeze_ts": (frozen_boundary_energy_fv_entry.get("freeze") or {}).get("freeze_ts_utc"),
        "early_no_boundary_fv_entry_freeze_ts": (frozen_early_no_boundary_fv_entry.get("freeze") or {}).get("freeze_ts_utc"),
        "mid_edge_false_conviction_fv_freeze_ts": (frozen_mid_edge_false_conviction.get("freeze") or {}).get("freeze_ts_utc"),
        "boundary_clock_fv_overlay_freeze_ts": (frozen_boundary_clock_fv.get("freeze") or {}).get("freeze_ts_utc"),
        "side_asymmetry_fv_overlay_freeze_ts": (frozen_side_asymmetry_fv.get("freeze") or {}).get("freeze_ts_utc"),
        "edge_phase_shrink_fv_freeze_ts": (frozen_edge_phase.get("freeze") or {}).get("freeze_ts_utc"),
        "edge_phase_edge_gate_freeze_ts": (frozen_edge_phase_gate.get("freeze") or {}).get("freeze_ts_utc"),
        "edge_gate_opposite_side_freeze_ts": (frozen_edge_gate_opposite.get("freeze") or {}).get("freeze_ts_utc"),
        "thin_recross_midp_entry_gate_freeze_ts": (frozen_thin_recross_gate.get("freeze") or {}).get("freeze_ts_utc"),
        "raw_p52_boundary_turbulence_skip_freeze_ts": (frozen_raw_p52_boundary_skip.get("freeze") or {}).get("freeze_ts_utc"),
        "raw_p52_favorite_valley_skip_freeze_ts": (frozen_raw_p52_favorite_valley_skip.get("freeze") or {}).get("freeze_ts_utc"),
        "raw_p52_mid_edge_skip_freeze_ts": (frozen_raw_p52_mid_edge_skip.get("freeze") or {}).get("freeze_ts_utc"),
        "raw_p52_shadow_mid_edge_skip_freeze_ts": (frozen_raw_p52_shadow_mid_edge_skip.get("freeze") or {}).get("freeze_ts_utc"),
        "raw_p52_book_disagreement_skip_freeze_ts": (frozen_raw_p52_book_disagreement_skip.get("freeze") or {}).get("freeze_ts_utc"),
        "raw_p52_book_shrink_entry_freeze_ts": (frozen_raw_p52_book_shrink_entry.get("freeze") or {}).get("freeze_ts_utc"),
        "raw_p52_early_no_boundary_skip_freeze_ts": (frozen_raw_p52_early_no_boundary_skip.get("freeze") or {}).get("freeze_ts_utc"),
        "raw_p52_early_no_boundary_band_skip_freeze_ts": (frozen_raw_p52_early_no_boundary_band_skip.get("freeze") or {}).get("freeze_ts_utc"),
        "target_loss_tag_repair_entry_freeze_ts": (frozen_target_loss_tag_repair.get("freeze") or {}).get("freeze_ts_utc"),
        "early_no_boundary_decay_repair_entry_freeze_ts": (frozen_early_no_boundary_decay_repair.get("freeze") or {}).get("freeze_ts_utc"),
        "mid_edge_boundary_deception_repair_entry_freeze_ts": (frozen_mid_edge_boundary_deception_repair.get("freeze") or {}).get("freeze_ts_utc"),
        "low_recross_repair_entry_freeze_ts": (frozen_low_recross_repair.get("freeze") or {}).get("freeze_ts_utc"),
        "high_raw_p_repair_entry_freeze_ts": (frozen_high_raw_p_repair.get("freeze") or {}).get("freeze_ts_utc"),
        "p50_book_edge_entry_freeze_ts": (frozen_p50_book_edge_entry.get("freeze") or {}).get("freeze_ts_utc"),
        "book_plus05_entry_freeze_ts": (frozen_book_plus05_entry.get("freeze") or {}).get("freeze_ts_utc"),
        "book_plus05_no_cheap_yes_entry_freeze_ts": (frozen_book_plus05_no_cheap_yes_entry.get("freeze") or {}).get("freeze_ts_utc"),
        "boundary_clock_repair_entry_freeze_ts": (frozen_boundary_clock_repair.get("freeze") or {}).get("freeze_ts_utc"),
        "boundary_clock_fv_entry_bridge_freeze_ts": (frozen_boundary_clock_fv_entry_bridge.get("freeze") or {}).get("freeze_ts_utc"),
        "weak_reversal_residual_fv_shrink_freeze_ts": (frozen_weak_reversal_residual_fv_shrink.get("freeze") or {}).get("freeze_ts_utc"),
        "no_mid_edge_fv_freeze_ts": (frozen_no_mid_edge_fv.get("freeze") or {}).get("freeze_ts_utc"),
        "weak_reversal_residual_repair_freeze_ts": (frozen_weak_reversal_residual_repair.get("freeze") or {}).get("freeze_ts_utc"),
        "early_boundary_wait_repair_freeze_ts": (frozen_early_boundary_wait_repair.get("freeze") or {}).get("freeze_ts_utc"),
        "early_boundary_opposite_wait_repair_freeze_ts": (frozen_early_boundary_opposite_wait_repair.get("freeze") or {}).get("freeze_ts_utc"),
        "exit_reduce_suppression_freeze_ts": (frozen_exit_reduce_suppression.get("freeze") or {}).get("freeze_ts_utc"),
        "exit_reduce_yes_suppression_freeze_ts": (frozen_exit_reduce_yes_suppression.get("freeze") or {}).get("freeze_ts_utc"),
        "exit_book_gap_suppression_freeze_ts": (frozen_exit_book_gap_suppression.get("freeze") or {}).get("freeze_ts_utc"),
        "forward_market_denominator": frozen.get("forward_market_denominator"),
        "threshold_forward_market_denominator": threshold.get("forward_market_denominator"),
        "side_agreement_forward_market_denominator": side_agreement.get("forward_market_denominator"),
        "convex_escape_forward_market_denominator": convex_escape.get("forward_market_denominator"),
        "raw_physics_forward_market_denominator": raw_physics.get("forward_market_denominator"),
        "raw_p52_sideflip_forward_market_denominator": raw_p52_sideflip.get("forward_market_denominator"),
        "raw_p52_recross_escape_forward_market_denominator": raw_p52_recross_escape.get("forward_market_denominator"),
        "noise_shrinkage_forward_market_denominator": noise_shrinkage.get("forward_market_denominator"),
        "path_confirmed_forward_market_denominator": path_confirmed.get("forward_market_denominator"),
        "raw_entry_coverage_valve_forward_market_denominator": raw_entry_coverage_valve.get("forward_denominator"),
        "approved_entry_book_fv_forward_entries": frozen_approved_entry_book_fv.get("future_entries"),
        "target_coverage_fv_forward_market_denominator": target_coverage_fv_seq.get("forward_denominator"),
        "target_coverage_p70_fv_forward_market_denominator": frozen_target_p70.get("future_denominator"),
        "target_coverage_p70_empirical_bayes_forward_market_denominator": frozen_target_p70_eb.get("future_denominator"),
        "path_state_p70_fv_forward_market_denominator": frozen_path_state_p70.get("future_denominator"),
        "boundary_recross_shrink_fv_forward_market_denominator": frozen_boundary_recross.get("future_denominator"),
        "boundary_temperature_fv_forward_market_denominator": frozen_boundary_temperature.get("future_denominator"),
        "boundary_energy_fv_entry_forward_market_denominator": frozen_boundary_energy_fv_entry.get("future_denominator"),
        "early_no_boundary_fv_entry_forward_market_denominator": frozen_early_no_boundary_fv_entry.get("future_denominator"),
        "mid_edge_false_conviction_fv_forward_market_denominator": frozen_mid_edge_false_conviction.get("future_denominator"),
        "boundary_clock_fv_overlay_forward_market_denominator": frozen_boundary_clock_fv.get("future_denominator"),
        "side_asymmetry_fv_overlay_forward_market_denominator": frozen_side_asymmetry_fv.get("future_denominator"),
        "edge_phase_shrink_fv_forward_market_denominator": frozen_edge_phase.get("future_denominator"),
        "edge_phase_edge_gate_forward_market_denominator": frozen_edge_phase_gate.get("future_denominator"),
        "edge_gate_opposite_side_forward_market_denominator": frozen_edge_gate_opposite.get("future_denominator"),
        "thin_recross_midp_entry_gate_forward_market_denominator": frozen_thin_recross_gate.get("future_denominator"),
        "raw_p52_boundary_turbulence_skip_forward_market_denominator": frozen_raw_p52_boundary_skip.get("future_denominator"),
        "raw_p52_favorite_valley_skip_forward_market_denominator": frozen_raw_p52_favorite_valley_skip.get("future_denominator"),
        "raw_p52_mid_edge_skip_forward_market_denominator": frozen_raw_p52_mid_edge_skip.get("future_denominator"),
        "raw_p52_shadow_mid_edge_skip_forward_market_denominator": frozen_raw_p52_shadow_mid_edge_skip.get("future_denominator"),
        "raw_p52_book_disagreement_skip_forward_market_denominator": frozen_raw_p52_book_disagreement_skip.get("future_denominator"),
        "raw_p52_book_shrink_entry_forward_market_denominator": frozen_raw_p52_book_shrink_entry.get("future_denominator"),
        "raw_p52_early_no_boundary_skip_forward_market_denominator": frozen_raw_p52_early_no_boundary_skip.get("future_denominator"),
        "raw_p52_early_no_boundary_band_skip_forward_market_denominator": frozen_raw_p52_early_no_boundary_band_skip.get("future_denominator"),
        "target_loss_tag_repair_entry_forward_market_denominator": frozen_target_loss_tag_repair.get("future_denominator"),
        "early_no_boundary_decay_repair_entry_forward_market_denominator": frozen_early_no_boundary_decay_repair.get("future_denominator"),
        "mid_edge_boundary_deception_repair_entry_forward_market_denominator": frozen_mid_edge_boundary_deception_repair.get("future_denominator"),
        "low_recross_repair_entry_forward_market_denominator": frozen_low_recross_repair.get("future_denominator"),
        "high_raw_p_repair_entry_forward_market_denominator": frozen_high_raw_p_repair.get("future_denominator"),
        "p50_book_edge_entry_forward_market_denominator": frozen_p50_book_edge_entry.get("future_denominator_markets"),
        "book_plus05_entry_forward_market_denominator": frozen_book_plus05_entry.get("future_denominator_markets"),
        "book_plus05_no_cheap_yes_entry_forward_market_denominator": frozen_book_plus05_no_cheap_yes_entry.get("future_denominator_markets"),
        "boundary_clock_repair_entry_forward_market_denominator": frozen_boundary_clock_repair.get("future_denominator"),
        "boundary_clock_fv_entry_bridge_forward_market_denominator": frozen_boundary_clock_fv_entry_bridge.get("future_denominator"),
        "weak_reversal_residual_fv_shrink_forward_market_denominator": frozen_weak_reversal_residual_fv_shrink.get("future_denominator"),
        "no_mid_edge_fv_forward_market_denominator": frozen_no_mid_edge_fv.get("future_denominator"),
        "weak_reversal_residual_repair_forward_market_denominator": frozen_weak_reversal_residual_repair.get("future_denominator"),
        "early_boundary_wait_repair_forward_market_denominator": frozen_early_boundary_wait_repair.get("future_denominator"),
        "early_boundary_opposite_wait_repair_forward_market_denominator": frozen_early_boundary_opposite_wait_repair.get("future_denominator"),
        "exit_reduce_suppression_forward_rows": (frozen_exit_reduce_suppression.get("summary") or {}).get("rows"),
        "exit_reduce_yes_suppression_forward_rows": (frozen_exit_reduce_yes_suppression.get("summary") or {}).get("rows"),
        "exit_book_gap_suppression_forward_rows": (frozen_exit_book_gap_suppression.get("summary") or {}).get("rows"),
        "control_risk_stop": scorecard.get("risk_stop"),
        "control_entries": scorecard.get("entries"),
        "control_gross_cents": scorecard.get("gross_cents"),
        "candidates": candidates,
        "any_live_ready": any(row.get("live_ready") for row in candidates),
    }


def path_candidate_blockers(row: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    entries = float(row.get("entries") or 0.0)
    added_reject = float(row.get("added_reject_count") or 0.0)
    simulated_share = added_reject / entries if entries else None
    settled = float(row.get("settled") or 0.0)
    coverage = row.get("coverage_pct")
    net = float(row.get("net_cents_after_entry_fee") or 0.0)
    brier_delta = row.get("brier_delta_mean_plus05_minus_raw")
    logloss_delta = row.get("logloss_delta_mean_plus05_minus_raw")
    if settled < 30.0:
        blockers.append("fv:settled_lt_30")
        blockers.append("execution:settled_lt_30")
    if coverage is None or float(coverage) < 70.0:
        blockers.append("fv:coverage_too_low")
        blockers.append("execution:coverage_too_low")
    if coverage is not None and float(coverage) > 90.0:
        blockers.append("fv:coverage_too_high")
        blockers.append("execution:coverage_too_high")
    if net <= 0.0:
        blockers.append("fv:net_not_positive")
        blockers.append("execution:net_not_positive")
    if brier_delta is None or float(brier_delta) >= 0.0:
        blockers.append("fv:brier_delta_not_negative")
    if logloss_delta is None or float(logloss_delta) >= 0.0:
        blockers.append("fv:logloss_delta_not_negative")
    if simulated_share is None or simulated_share > 0.35:
        blockers.append("execution:simulated_share_gt_0.35")
    return blockers


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Live Trade Readiness",
        "",
        report["permission_note"],
        "",
        f"- Any live-ready candidate: `{report['any_live_ready']}`",
        f"- Frozen validation timestamp: `{report['freeze_ts']}`",
        f"- Threshold challenger timestamp: `{report['threshold_freeze_ts']}`",
        f"- Side-agreement challenger timestamp: `{report['side_agreement_freeze_ts']}`",
        f"- Convex-escape challenger timestamp: `{report['convex_escape_freeze_ts']}`",
        f"- Raw-physics challenger timestamp: `{report['raw_physics_freeze_ts']}`",
        f"- Raw-p52 sideflip challenger timestamp: `{report['raw_p52_sideflip_freeze_ts']}`",
        f"- Raw-p52 recross-escape challenger timestamp: `{report['raw_p52_recross_escape_freeze_ts']}`",
        f"- Noise-shrinkage challenger timestamp: `{report['noise_shrinkage_freeze_ts']}`",
        f"- Path-confirmed challenger timestamp: `{report['path_confirmed_freeze_ts']}`",
        f"- Raw-entry coverage valve timestamp: `{report['raw_entry_coverage_valve_freeze_ts']}`",
        f"- Approved-entry book FV timestamp: `{report['approved_entry_book_fv_freeze_ts']}`",
        f"- Target-coverage FV policy/overlay: `{report['target_coverage_fv_policy']}` / `{report['target_coverage_fv_overlay']}`",
        f"- Target-coverage conservative FV timestamp: `{report['target_coverage_conservative_fv_freeze_ts']}`",
        f"- Target-coverage p70 FV timestamp: `{report['target_coverage_p70_fv_freeze_ts']}`",
        f"- Target-coverage p70 empirical-Bayes FV timestamp: `{report['target_coverage_p70_empirical_bayes_freeze_ts']}`",
        f"- Path-state p70 FV timestamp: `{report['path_state_p70_fv_freeze_ts']}`",
        f"- Boundary-recross shrink FV timestamp: `{report['boundary_recross_shrink_fv_freeze_ts']}`",
        f"- Boundary-temperature FV timestamp: `{report['boundary_temperature_fv_freeze_ts']}`",
        f"- Boundary-energy FV entry timestamp: `{report['boundary_energy_fv_entry_freeze_ts']}`",
        f"- Early-NO boundary FV entry timestamp: `{report['early_no_boundary_fv_entry_freeze_ts']}`",
        f"- Mid-edge false-conviction FV timestamp: `{report['mid_edge_false_conviction_fv_freeze_ts']}`",
        f"- Side-asymmetry FV overlay timestamp: `{report['side_asymmetry_fv_overlay_freeze_ts']}`",
        f"- Edge-phase shrink FV timestamp: `{report['edge_phase_shrink_fv_freeze_ts']}`",
        f"- Edge-phase edge gate timestamp: `{report['edge_phase_edge_gate_freeze_ts']}`",
        f"- Edge-gate opposite-side timestamp: `{report['edge_gate_opposite_side_freeze_ts']}`",
        f"- Thin-recross mid-p entry gate timestamp: `{report['thin_recross_midp_entry_gate_freeze_ts']}`",
        f"- Raw-p52 boundary-turbulence skip timestamp: `{report['raw_p52_boundary_turbulence_skip_freeze_ts']}`",
        f"- Raw-p52 favorite-valley skip timestamp: `{report['raw_p52_favorite_valley_skip_freeze_ts']}`",
        f"- Raw-p52 mid-edge skip timestamp: `{report['raw_p52_mid_edge_skip_freeze_ts']}`",
        f"- Raw-p52 shadow mid-edge skip timestamp: `{report['raw_p52_shadow_mid_edge_skip_freeze_ts']}`",
        f"- Raw-p52 book-disagreement skip timestamp: `{report['raw_p52_book_disagreement_skip_freeze_ts']}`",
        f"- Raw-p52 book-shrink entry timestamp: `{report['raw_p52_book_shrink_entry_freeze_ts']}`",
        f"- Raw-p52 early-NO boundary skip timestamp: `{report['raw_p52_early_no_boundary_skip_freeze_ts']}`",
        f"- Raw-p52 early-NO boundary band skip timestamp: `{report['raw_p52_early_no_boundary_band_skip_freeze_ts']}`",
        f"- Target-loss tag repair entry timestamp: `{report['target_loss_tag_repair_entry_freeze_ts']}`",
        f"- Early NO boundary-decay repair entry timestamp: `{report['early_no_boundary_decay_repair_entry_freeze_ts']}`",
        f"- Mid-edge boundary-deception repair entry timestamp: `{report['mid_edge_boundary_deception_repair_entry_freeze_ts']}`",
        f"- Low-recross repair entry timestamp: `{report['low_recross_repair_entry_freeze_ts']}`",
        f"- High-raw-p repair entry timestamp: `{report['high_raw_p_repair_entry_freeze_ts']}`",
        f"- p50 book-edge entry timestamp: `{report['p50_book_edge_entry_freeze_ts']}`",
        f"- book plus 05 entry timestamp: `{report['book_plus05_entry_freeze_ts']}`",
        f"- book plus 05 no cheap YES entry timestamp: `{report['book_plus05_no_cheap_yes_entry_freeze_ts']}`",
        f"- Weak-reversal residual FV shrink timestamp: `{report['weak_reversal_residual_fv_shrink_freeze_ts']}`",
        f"- NO mid-edge FV timestamp: `{report['no_mid_edge_fv_freeze_ts']}`",
        f"- Weak-reversal residual repair timestamp: `{report['weak_reversal_residual_repair_freeze_ts']}`",
        f"- Early-boundary wait repair timestamp: `{report['early_boundary_wait_repair_freeze_ts']}`",
        f"- Early-boundary opposite wait repair timestamp: `{report['early_boundary_opposite_wait_repair_freeze_ts']}`",
        f"- Exit reduce-suppression timestamp: `{report['exit_reduce_suppression_freeze_ts']}`",
        f"- Exit reduce YES-only suppression timestamp: `{report['exit_reduce_yes_suppression_freeze_ts']}`",
        f"- Exit book-gap suppression timestamp: `{report['exit_book_gap_suppression_freeze_ts']}`",
        f"- Forward market denominator: `{report['forward_market_denominator']}`",
        f"- Threshold forward market denominator: `{report['threshold_forward_market_denominator']}`",
        f"- Side-agreement forward market denominator: `{report['side_agreement_forward_market_denominator']}`",
        f"- Convex-escape forward market denominator: `{report['convex_escape_forward_market_denominator']}`",
        f"- Raw-physics forward market denominator: `{report['raw_physics_forward_market_denominator']}`",
        f"- Raw-p52 sideflip forward market denominator: `{report['raw_p52_sideflip_forward_market_denominator']}`",
        f"- Raw-p52 recross-escape forward market denominator: `{report['raw_p52_recross_escape_forward_market_denominator']}`",
        f"- Noise-shrinkage forward market denominator: `{report['noise_shrinkage_forward_market_denominator']}`",
        f"- Path-confirmed forward market denominator: `{report['path_confirmed_forward_market_denominator']}`",
        f"- Raw-entry coverage valve forward market denominator: `{report['raw_entry_coverage_valve_forward_market_denominator']}`",
        f"- Approved-entry book FV forward entries: `{report['approved_entry_book_fv_forward_entries']}`",
        f"- Target-coverage FV forward market denominator: `{report['target_coverage_fv_forward_market_denominator']}`",
        f"- Target-coverage p70 FV forward market denominator: `{report['target_coverage_p70_fv_forward_market_denominator']}`",
        f"- Target-coverage p70 empirical-Bayes FV forward market denominator: `{report['target_coverage_p70_empirical_bayes_forward_market_denominator']}`",
        f"- Path-state p70 FV forward market denominator: `{report['path_state_p70_fv_forward_market_denominator']}`",
        f"- Boundary-recross shrink FV forward market denominator: `{report['boundary_recross_shrink_fv_forward_market_denominator']}`",
        f"- Boundary-temperature FV forward market denominator: `{report['boundary_temperature_fv_forward_market_denominator']}`",
        f"- Boundary-energy FV entry forward market denominator: `{report['boundary_energy_fv_entry_forward_market_denominator']}`",
        f"- Early-NO boundary FV entry forward market denominator: `{report['early_no_boundary_fv_entry_forward_market_denominator']}`",
        f"- Mid-edge false-conviction FV forward market denominator: `{report['mid_edge_false_conviction_fv_forward_market_denominator']}`",
        f"- Side-asymmetry FV overlay forward market denominator: `{report['side_asymmetry_fv_overlay_forward_market_denominator']}`",
        f"- Edge-phase shrink FV forward market denominator: `{report['edge_phase_shrink_fv_forward_market_denominator']}`",
        f"- Edge-phase edge gate forward market denominator: `{report['edge_phase_edge_gate_forward_market_denominator']}`",
        f"- Edge-gate opposite-side forward market denominator: `{report['edge_gate_opposite_side_forward_market_denominator']}`",
        f"- Thin-recross mid-p entry gate forward market denominator: `{report['thin_recross_midp_entry_gate_forward_market_denominator']}`",
        f"- Raw-p52 boundary-turbulence skip forward market denominator: `{report['raw_p52_boundary_turbulence_skip_forward_market_denominator']}`",
        f"- Raw-p52 favorite-valley skip forward market denominator: `{report['raw_p52_favorite_valley_skip_forward_market_denominator']}`",
        f"- Raw-p52 mid-edge skip forward market denominator: `{report['raw_p52_mid_edge_skip_forward_market_denominator']}`",
        f"- Raw-p52 shadow mid-edge skip forward market denominator: `{report['raw_p52_shadow_mid_edge_skip_forward_market_denominator']}`",
        f"- Raw-p52 book-disagreement skip forward market denominator: `{report['raw_p52_book_disagreement_skip_forward_market_denominator']}`",
        f"- Raw-p52 book-shrink entry forward market denominator: `{report['raw_p52_book_shrink_entry_forward_market_denominator']}`",
        f"- Raw-p52 early-NO boundary skip forward market denominator: `{report['raw_p52_early_no_boundary_skip_forward_market_denominator']}`",
        f"- Raw-p52 early-NO boundary band skip forward market denominator: `{report['raw_p52_early_no_boundary_band_skip_forward_market_denominator']}`",
        f"- Target-loss tag repair entry forward market denominator: `{report['target_loss_tag_repair_entry_forward_market_denominator']}`",
        f"- Early NO boundary-decay repair entry forward market denominator: `{report['early_no_boundary_decay_repair_entry_forward_market_denominator']}`",
        f"- Mid-edge boundary-deception repair entry forward market denominator: `{report['mid_edge_boundary_deception_repair_entry_forward_market_denominator']}`",
        f"- Low-recross repair entry forward market denominator: `{report['low_recross_repair_entry_forward_market_denominator']}`",
        f"- High-raw-p repair entry forward market denominator: `{report['high_raw_p_repair_entry_forward_market_denominator']}`",
        f"- p50 book-edge entry forward market denominator: `{report['p50_book_edge_entry_forward_market_denominator']}`",
        f"- book plus 05 entry forward market denominator: `{report['book_plus05_entry_forward_market_denominator']}`",
        f"- book plus 05 no cheap YES entry forward market denominator: `{report['book_plus05_no_cheap_yes_entry_forward_market_denominator']}`",
        f"- Weak-reversal residual FV shrink forward market denominator: `{report['weak_reversal_residual_fv_shrink_forward_market_denominator']}`",
        f"- NO mid-edge FV forward market denominator: `{report['no_mid_edge_fv_forward_market_denominator']}`",
        f"- Weak-reversal residual repair forward market denominator: `{report['weak_reversal_residual_repair_forward_market_denominator']}`",
        f"- Early-boundary wait repair forward market denominator: `{report['early_boundary_wait_repair_forward_market_denominator']}`",
        f"- Early-boundary opposite wait repair forward market denominator: `{report['early_boundary_opposite_wait_repair_forward_market_denominator']}`",
        f"- Exit reduce-suppression forward rows: `{report['exit_reduce_suppression_forward_rows']}`",
        f"- Exit reduce YES-only suppression forward rows: `{report['exit_reduce_yes_suppression_forward_rows']}`",
        f"- Exit book-gap suppression forward rows: `{report['exit_book_gap_suppression_forward_rows']}`",
        f"- Control risk stop active: `{report['control_risk_stop']}`",
        f"- Control entries/gross cents: `{report['control_entries']}/{report['control_gross_cents']}`",
        "",
        "## Candidates",
        "",
        "| gate | policy | live ready | entries | settled | actual/sim | sim share | coverage | net c | brier | blockers |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["candidates"]:
        lines.append(
            f"| {row['gate']} | {row['policy']} | {row['live_ready']} | {row['entries']} | {row['settled']} | "
            f"{row.get('approved_entry_count')}/{row.get('added_reject_count')} | {fmt(row.get('simulated_share'))} | "
            f"{fmt(row['coverage_pct'])} | {fmt(row['net_cents_after_entry_fee'])} | {fmt(row['avg_brier'])} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
