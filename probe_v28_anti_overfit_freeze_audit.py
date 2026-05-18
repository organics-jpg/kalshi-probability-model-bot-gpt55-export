"""Anti-overfit freeze audit for v28 FV/entry candidate probes.

Research-only; no live bot changes or orders.

The active goal explicitly rejects historical overfit. One easy way to violate
that accidentally is to keep re-selecting the "best" policy as new rows arrive
and then describe the result as forward evidence. This audit checks the current
research artifacts for frozen state, post-freeze validation intent, and obvious
state/report drift.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_anti_overfit_freeze_audit_latest.json"
OUT_MD = OUT_DIR / "v28_anti_overfit_freeze_audit_latest.md"


CANDIDATES = [
    {
        "family": "target_coverage_fv",
        "artifact": "v28_target_coverage_fv_overlay_validator",
        "state": OUT_DIR / "v28_target_coverage_fv_overlay_validator_state.json",
        "report": OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json",
        "expected_state_fields": ["freeze_ts", "policy", "entry_surface", "source_coverage_freeze_ts", "overlay_names"],
        "expected_report_fields": ["freeze_ts", "policy", "entry_surface", "forward_denominator", "forward"],
        "fixed_selection_fields": ["policy", "entry_surface", "source_coverage_freeze_ts"],
        "note": "Current best target-coverage FV candidate; should remain fixed while forward rows accumulate.",
    },
    {
        "family": "raw_entry_calibrated_fv",
        "artifact": "v28_frozen_raw_entry_calibrated_probability",
        "state": OUT_DIR / "v28_frozen_raw_entry_calibrated_probability_state.json",
        "report": OUT_DIR / "v28_frozen_raw_entry_calibrated_probability_latest.json",
        "expected_state_fields": ["freeze_ts", "entry_policy", "overlays", "promotion_floor"],
        "expected_report_fields": ["freeze_ts", "entry_policy", "ranked"],
        "fixed_selection_fields": ["entry_policy"],
        "note": "Frozen FV overlays on the broad raw-v28 p50 entry surface.",
    },
    {
        "family": "boundary_memory_fv",
        "artifact": "v28_boundary_memory_fv_candidates",
        "state": OUT_DIR / "v28_boundary_memory_fv_candidates_state.json",
        "report": OUT_DIR / "v28_boundary_memory_fv_candidates_latest.json",
        "expected_state_fields": ["freeze_ts", "entry_policy", "hypothesis", "promotion_floor"],
        "expected_report_fields": ["freeze_ts", "entry_policy", "forward_denominator", "forward"],
        "fixed_selection_fields": ["entry_policy"],
        "note": "Catastrophic-forgetting boundary-memory candidate; valid only as post-freeze evidence.",
    },
    {
        "family": "reward_memory_fv",
        "artifact": "v28_reward_memory_fv_candidates",
        "state": OUT_DIR / "v28_reward_memory_fv_candidates_state.json",
        "report": OUT_DIR / "v28_reward_memory_fv_candidates_latest.json",
        "expected_state_fields": ["freeze_ts", "entry_policy", "controllers", "promotion_floor"],
        "expected_report_fields": ["freeze_ts", "entry_policy", "forward_denominator", "forward"],
        "fixed_selection_fields": ["entry_policy"],
        "note": "Constrained reward-memory controller; controller weights must be frozen before forward scoring.",
    },
    {
        "family": "book_exact_entry_gate",
        "artifact": "v28_frozen_book_exact_entry_gate",
        "state": OUT_DIR / "v28_frozen_book_exact_entry_gate_state.json",
        "report": OUT_DIR / "v28_frozen_book_exact_entry_gate_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "candidate", "policies", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "forward_denominator_markets", "summaries"],
        "fixed_selection_fields": [],
        "note": "Frozen book-exact entry gate; validates whether full FV collapse to book probability has forward edge rather than historical book-favorite luck.",
    },
    {
        "family": "approved_entry_state_valve",
        "artifact": "v28_frozen_approved_entry_state_valve",
        "state": OUT_DIR / "v28_frozen_approved_entry_state_valve_state.json",
        "report": OUT_DIR / "v28_frozen_approved_entry_state_valve_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "policy", "rule"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "freeze.policy", "candidate", "control"],
        "fixed_selection_fields": [],
        "note": "Frozen actual-approved same-side reentry valve; validates state/entry physics without rejected-row simulation.",
    },
    {
        "family": "approved_entry_book_fv",
        "artifact": "v28_frozen_approved_entry_book_fv",
        "state": OUT_DIR / "v28_frozen_approved_entry_book_fv_state.json",
        "report": OUT_DIR / "v28_frozen_approved_entry_book_fv_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "entry_surface", "candidate", "overlays", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_entries", "future_settled", "ranked", "candidate"],
        "fixed_selection_fields": [],
        "note": "Frozen actual-approved FV calibration challenger; tests whether book probability remains better calibrated than raw v28 on future approved entries.",
    },
    {
        "family": "danger_zone_entry_valve",
        "artifact": "v28_frozen_danger_zone_entry_valve",
        "state": OUT_DIR / "v28_frozen_danger_zone_entry_valve_state.json",
        "report": OUT_DIR / "v28_frozen_danger_zone_entry_valve_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "policy", "rule", "source_artifact"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "freeze.policy", "candidate", "control"],
        "fixed_selection_fields": [],
        "note": "Frozen actual-approved danger-zone valve; validates raw/book overconfidence and same-side reentry risk on post-freeze v28 entries.",
    },
    {
        "family": "danger_zone_fv_calibration",
        "artifact": "v28_frozen_danger_zone_fv_calibration",
        "state": OUT_DIR / "v28_frozen_danger_zone_fv_calibration_state.json",
        "report": OUT_DIR / "v28_frozen_danger_zone_fv_calibration_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "entry_surface", "overlays", "danger_rule"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "freeze.entry_surface", "ranked"],
        "fixed_selection_fields": [],
        "note": "Frozen actual-approved probability overlays for the danger-zone raw/book disagreement signal.",
    },
    {
        "family": "danger_zone_robustness",
        "artifact": "v28_frozen_danger_zone_robustness",
        "state": OUT_DIR / "v28_frozen_danger_zone_fv_calibration_state.json",
        "report": OUT_DIR / "v28_frozen_danger_zone_robustness_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "entry_surface", "overlays", "danger_rule"],
        "expected_report_fields": ["fv_freeze.freeze_ts_utc", "future_rows", "full_entry", "full_fv", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen-only robustness check for danger-zone FV/entry lift; detects single-row future dependence.",
    },
    {
        "family": "target_coverage_conservative_fv",
        "artifact": "v28_frozen_target_coverage_conservative_fv",
        "state": OUT_DIR / "v28_frozen_target_coverage_conservative_fv_state.json",
        "report": OUT_DIR / "v28_frozen_target_coverage_conservative_fv_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "entry_policy", "variant", "rule", "source_artifact"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "freeze.entry_policy", "ranked"],
        "fixed_selection_fields": [],
        "note": "Frozen conservative target-coverage FV challenger; validates calm-mid-or-high-conviction sharpening on future rows only.",
    },
    {
        "family": "target_coverage_p70_fv",
        "artifact": "v28_frozen_target_coverage_p70_fv",
        "state": OUT_DIR / "v28_frozen_target_coverage_p70_fv_state.json",
        "report": OUT_DIR / "v28_frozen_target_coverage_p70_fv_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "entry_policy", "variant", "rule", "source_artifact"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "freeze.entry_policy", "ranked"],
        "fixed_selection_fields": [],
        "note": "Frozen target-coverage p70 FV challenger; validates high-confidence-only sharpening on future rows only.",
    },
    {
        "family": "target_coverage_p70_empirical_bayes",
        "artifact": "v28_frozen_target_coverage_p70_empirical_bayes",
        "state": OUT_DIR / "v28_frozen_target_coverage_p70_empirical_bayes_state.json",
        "report": OUT_DIR / "v28_frozen_target_coverage_p70_empirical_bayes_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "entry_policy", "variant", "prior_count", "full_scale", "rule", "source_artifact"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "freeze.entry_policy", "ranked", "scale"],
        "fixed_selection_fields": [],
        "note": "Frozen empirical-Bayes p70 FV challenger; validates evidence-weighted high-confidence sharpening on future rows only.",
    },
    {
        "family": "boundary_temperature_fv",
        "artifact": "v28_frozen_boundary_temperature_fv",
        "state": OUT_DIR / "v28_frozen_boundary_temperature_fv_state.json",
        "report": OUT_DIR / "v28_frozen_boundary_temperature_fv_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "entry_policy", "variant", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "entries", "settled", "candidate", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen continuous boundary-temperature FV challenger; validates recross-heat deconfidence on future target-coverage rows.",
    },
    {
        "family": "boundary_energy_fv_entry",
        "artifact": "v28_frozen_boundary_energy_fv_entry",
        "state": OUT_DIR / "v28_frozen_boundary_energy_fv_entry_state.json",
        "report": OUT_DIR / "v28_frozen_boundary_energy_fv_entry_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "base_policy", "candidate", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "future_candidate_summary", "diagnostic_candidate_summary", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen boundary-energy FV entry bridge; validates path-energy deconfidence under the unchanged target policy on future rows.",
    },
    {
        "family": "early_no_boundary_fv_entry",
        "artifact": "v28_frozen_early_no_boundary_fv_entry",
        "state": OUT_DIR / "v28_frozen_early_no_boundary_fv_entry_state.json",
        "report": OUT_DIR / "v28_frozen_early_no_boundary_fv_entry_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "base_policy", "candidate", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "future_candidate_summary", "diagnostic_candidate_summary", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen early-NO boundary FV entry bridge; validates side-asymmetric path-decay deconfidence on future rows.",
    },
    {
        "family": "path_state_p70_fv",
        "artifact": "v28_frozen_path_state_p70_fv",
        "state": OUT_DIR / "v28_frozen_path_state_p70_fv_state.json",
        "report": OUT_DIR / "v28_frozen_path_state_p70_fv_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "entry_policy", "variant", "rule", "physics", "parameters"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "future_entries", "ranked", "path_state_action_rollups"],
        "fixed_selection_fields": [],
        "note": "Frozen path/state p70 FV challenger; sharpens only high-confidence rows with strong confirmation energy.",
    },
    {
        "family": "boundary_recross_shrink_fv",
        "artifact": "v28_frozen_boundary_recross_shrink_fv",
        "state": OUT_DIR / "v28_frozen_boundary_recross_shrink_fv_state.json",
        "report": OUT_DIR / "v28_frozen_boundary_recross_shrink_fv_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "entry_policy", "variant", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "entries", "ranked"],
        "fixed_selection_fields": [],
        "note": "Frozen boundary/recross FV shrink; validates shallow high-recross confidence decay on future rows only.",
    },
    {
        "family": "mid_edge_false_conviction_fv",
        "artifact": "v28_frozen_mid_edge_false_conviction_fv",
        "state": OUT_DIR / "v28_frozen_mid_edge_false_conviction_fv_state.json",
        "report": OUT_DIR / "v28_frozen_mid_edge_false_conviction_fv_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "entry_policy", "variant", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "entries", "ranked"],
        "fixed_selection_fields": [],
        "note": "Frozen FV shrink; validates early high-recross 4-8pp edge false-conviction confidence decay on future rows only.",
    },
    {
        "family": "boundary_clock_fv_overlay",
        "artifact": "v28_frozen_boundary_clock_fv_overlay",
        "state": OUT_DIR / "v28_frozen_boundary_clock_fv_overlay_state.json",
        "report": OUT_DIR / "v28_frozen_boundary_clock_fv_overlay_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "entry_policy", "variant", "rule", "physics", "source_artifact"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "candidate", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen boundary-clock FV overlay; validates p=50 collapse for unresolved boundary-clock hazard rows on future rows only.",
    },
    {
        "family": "boundary_clock_residual_registry",
        "artifact": "v28_frozen_boundary_clock_residual_registry",
        "state": OUT_DIR / "v28_frozen_boundary_clock_residual_registry_state.json",
        "report": OUT_DIR / "v28_frozen_boundary_clock_residual_registry_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "registry", "rule", "hypothesis", "promotion_note"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "target_summary", "bucket_summary", "rows"],
        "fixed_selection_fields": [],
        "note": "Frozen residual registry after boundary-clock correction; watches mid-confidence NO-side boundary hesitation before any new FV knob is considered.",
    },
    {
        "family": "side_asymmetry_registry",
        "artifact": "v28_frozen_side_asymmetry_registry",
        "state": OUT_DIR / "v28_frozen_side_asymmetry_registry_state.json",
        "report": OUT_DIR / "v28_frozen_side_asymmetry_registry_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "registry", "rule", "hypothesis", "promotion_note"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "target_summary", "bucket_summary", "non_clock_bucket_summary", "rows"],
        "fixed_selection_fields": [],
        "note": "Frozen side-asymmetry registry; watches NO p60-70 mid-boundary mid-recross rows before any asymmetric FV penalty is considered.",
    },
    {
        "family": "side_asymmetry_fv_overlay",
        "artifact": "v28_frozen_side_asymmetry_fv_overlay",
        "state": OUT_DIR / "v28_frozen_side_asymmetry_fv_overlay_state.json",
        "report": OUT_DIR / "v28_frozen_side_asymmetry_fv_overlay_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "entry_policy", "variant", "rule", "physics", "source_artifact"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "candidate", "adjusted_rows", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen combined boundary-clock plus side-asymmetry FV overlay; validates coin-flip collapse on future rows only.",
    },
    {
        "family": "edge_phase_shrink_fv",
        "artifact": "v28_frozen_edge_phase_shrink_fv",
        "state": OUT_DIR / "v28_frozen_edge_phase_shrink_fv_state.json",
        "report": OUT_DIR / "v28_frozen_edge_phase_shrink_fv_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "entry_policy", "variant", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "entries", "ranked"],
        "fixed_selection_fields": [],
        "note": "Frozen edge-phase FV shrink; validates phase-aware boundary confidence decay on future rows only.",
    },
    {
        "family": "edge_phase_edge_gate",
        "artifact": "v28_frozen_edge_phase_edge_gate",
        "state": OUT_DIR / "v28_frozen_edge_phase_edge_gate_state.json",
        "report": OUT_DIR / "v28_frozen_edge_phase_edge_gate_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "base_entry_policy", "fv_variant", "adjusted_edge_floor", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "base", "candidate", "skipped_rows"],
        "fixed_selection_fields": [],
        "note": "Frozen adjusted-FV paid-price safety valve; validates rare extreme negative edge-phase disagreement on future rows only.",
    },
    {
        "family": "edge_gate_opposite_side",
        "artifact": "v28_frozen_edge_gate_opposite_side",
        "state": OUT_DIR / "v28_frozen_edge_gate_opposite_side_state.json",
        "report": OUT_DIR / "v28_frozen_edge_gate_opposite_side_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "base_entry_policy", "fv_variant", "adjusted_edge_floor", "opposite_min_raw_p", "opposite_min_raw_edge", "opposite_min_adjusted_edge", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "base", "candidate", "cases"],
        "fixed_selection_fields": [],
        "note": "Frozen opposite-side replacement for edge-gate skips; validates whether bad paid-price rows can preserve coverage via coherent same-or-later opposite entries.",
    },
    {
        "family": "exit_reduce_suppression",
        "artifact": "v28_frozen_exit_reduce_suppression",
        "state": OUT_DIR / "v28_frozen_exit_reduce_suppression_state.json",
        "report": OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "candidate", "p_hold_floor", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "summary", "rows", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen exit-policy challenger; validates suppressing probability_reduce only when held-side probability remains >=75%.",
    },
    {
        "family": "exit_reduce_yes_suppression",
        "artifact": "v28_frozen_exit_reduce_yes_suppression",
        "state": OUT_DIR / "v28_frozen_exit_reduce_yes_suppression_state.json",
        "report": OUT_DIR / "v28_frozen_exit_reduce_yes_suppression_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "candidate", "side", "p_hold_floor", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "summary", "rows", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen exit-policy challenger; validates the side-asymmetric YES-only interpretation of probability_reduce suppression on future rows.",
    },
    {
        "family": "exit_book_gap_suppression",
        "artifact": "v28_frozen_exit_book_gap_suppression",
        "state": OUT_DIR / "v28_frozen_exit_book_gap_suppression_state.json",
        "report": OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "candidate", "gap_floor", "p_hold_floor", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "summary", "rows", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen soft-exit book-gap challenger; validates suppressing spread/turbulence exits while keeping collapse exits intact.",
    },
    {
        "family": "target_coverage_p70_quality_registry",
        "artifact": "v28_frozen_target_coverage_p70_quality_registry",
        "state": OUT_DIR / "v28_frozen_target_coverage_p70_quality_registry_state.json",
        "report": OUT_DIR / "v28_frozen_target_coverage_p70_quality_registry_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "entry_policy", "registry", "rule", "tag_definitions"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "tag_rollups", "rows"],
        "fixed_selection_fields": [],
        "note": "Frozen p70 quality-tag registry; validates physical high-confidence tags on future rows before any tag-conditioned model is considered.",
    },
    {
        "family": "live_p70_quality_registry",
        "artifact": "v28_live_p70_quality_registry",
        "state": OUT_DIR / "v28_live_p70_quality_registry_state.json",
        "report": OUT_DIR / "v28_live_p70_quality_registry_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "registry", "rule", "tag_definitions"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "row_count", "settled_count", "tag_rollups", "rows"],
        "fixed_selection_fields": [],
        "note": "Future-only live v28 p70 quality registry; validates physical live high-confidence tags before any live candidate gets promoted.",
    },
    {
        "family": "live_collapse_reentry_registry",
        "artifact": "v28_live_collapse_reentry_registry",
        "state": OUT_DIR / "v28_live_collapse_reentry_registry_state.json",
        "report": OUT_DIR / "v28_live_collapse_reentry_registry_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "registry", "hypothesis", "candidate_action", "tag_definitions"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_summary", "future_tag_rollups", "future_rows"],
        "fixed_selection_fields": [],
        "note": "Future-only live registry for same-market reentries after probability-collapse exits; tests whether collapse should penalize FV confidence.",
    },
    {
        "family": "thin_recross_midp_entry_gate",
        "artifact": "v28_frozen_thin_recross_midp_entry_gate",
        "state": OUT_DIR / "v28_frozen_thin_recross_midp_entry_gate_state.json",
        "report": OUT_DIR / "v28_frozen_thin_recross_midp_entry_gate_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "base_entry_policy", "candidate", "edge_ceiling", "recross_floor"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "freeze.candidate", "base", "candidate", "skipped_rows"],
        "fixed_selection_fields": [],
        "note": "Frozen entry gate for thin-edge high-recross mid-p rows; validates a narrow turbulence skip on future rows only.",
    },
    {
        "family": "raw_p52_boundary_turbulence_skip",
        "artifact": "v28_frozen_raw_p52_boundary_turbulence_skip",
        "state": OUT_DIR / "v28_frozen_raw_p52_boundary_turbulence_skip_state.json",
        "report": OUT_DIR / "v28_frozen_raw_p52_boundary_turbulence_skip_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "base_policy", "candidate", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "base", "candidate", "skipped_rows"],
        "fixed_selection_fields": [],
        "note": "Frozen raw-p52 boundary-turbulence skip; validates weak raw near-strike high-recross rows on future rows only.",
    },
    {
        "family": "target_loss_tag_repair_entry",
        "artifact": "v28_frozen_target_loss_tag_repair_entry",
        "state": OUT_DIR / "v28_frozen_target_loss_tag_repair_entry_state.json",
        "report": OUT_DIR / "v28_frozen_target_loss_tag_repair_entry_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "base_policy", "candidate", "danger_rule", "repair_rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "target_summary", "candidate_summary", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen target-loss tag repair candidate; skips weak-boundary and paid-thin-edge rows, then repairs coverage from low-recross clean rows.",
    },
    {
        "family": "low_recross_repair_entry",
        "artifact": "v28_frozen_low_recross_repair_entry",
        "state": OUT_DIR / "v28_frozen_low_recross_repair_entry_state.json",
        "report": OUT_DIR / "v28_frozen_low_recross_repair_entry_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "base_policy", "candidate", "coverage_floor", "danger_rule", "repair_rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "target_summary", "candidate_summary", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen target-coverage repair candidate; skips paid/weak-boundary danger rows and repairs coverage with lowest-recross clean rows.",
    },
    {
        "family": "early_no_boundary_decay_repair_entry",
        "artifact": "v28_frozen_early_no_boundary_decay_repair_entry",
        "state": OUT_DIR / "v28_frozen_early_no_boundary_decay_repair_entry_state.json",
        "report": OUT_DIR / "v28_frozen_early_no_boundary_decay_repair_entry_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "base_policy", "candidate", "coverage_floor", "danger_rule", "repair_rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "target_summary", "candidate_summary", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen target-coverage repair candidate; skips early NO boundary-decay and cheap boundary-turbulence rows, then repairs coverage with calmer geometry.",
    },
    {
        "family": "mid_edge_boundary_deception_repair_entry",
        "artifact": "v28_frozen_mid_edge_boundary_deception_repair_entry",
        "state": OUT_DIR / "v28_frozen_mid_edge_boundary_deception_repair_entry_state.json",
        "report": OUT_DIR / "v28_frozen_mid_edge_boundary_deception_repair_entry_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "base_policy", "candidate", "coverage_floor", "danger_rule", "repair_rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "target_summary", "candidate_summary", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen target-coverage repair candidate; skips early high-recross 4-8pp edge rows that look like boundary false-conviction.",
    },
    {
        "family": "high_raw_p_repair_entry",
        "artifact": "v28_frozen_high_raw_p_repair_entry",
        "state": OUT_DIR / "v28_frozen_high_raw_p_repair_entry_state.json",
        "report": OUT_DIR / "v28_frozen_high_raw_p_repair_entry_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "base_policy", "candidate", "coverage_floor", "danger_rule", "repair_rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "target_summary", "candidate_summary", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen target-coverage repair candidate; skips paid/weak-boundary danger rows and repairs coverage with highest raw-p clean rows.",
    },
    {
        "family": "p50_book_edge_entry",
        "artifact": "v28_frozen_p50_book_edge_entry",
        "state": OUT_DIR / "v28_frozen_p50_book_edge_entry_state.json",
        "report": OUT_DIR / "v28_frozen_p50_book_edge_entry_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "candidate", "rule", "physics", "source"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator_markets", "summary", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen closest broad book-edge entry lane; validates p50, book-plus-5pp, nonnegative-edge rule on future rows only.",
    },
    {
        "family": "book_plus05_entry",
        "artifact": "v28_frozen_book_plus05_entry",
        "state": OUT_DIR / "v28_frozen_book_plus05_entry_state.json",
        "report": OUT_DIR / "v28_frozen_book_plus05_entry_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "candidate", "rule", "physics", "source"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator_markets", "summary", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen broad book-plus-5pp entry lane; validates book-disagreement edge on future rows only.",
    },
    {
        "family": "book_plus05_no_cheap_yes_entry",
        "artifact": "v28_frozen_book_plus05_no_cheap_yes_entry",
        "state": OUT_DIR / "v28_frozen_book_plus05_no_cheap_yes_entry_state.json",
        "report": OUT_DIR / "v28_frozen_book_plus05_no_cheap_yes_entry_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "candidate", "rule", "physics", "source"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator_markets", "summary", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen broad book-plus-5pp entry lane with cheap-YES boundary-pull rows removed; validates whether the boundary-pull filter preserves broad coverage and improves PnL on future rows only.",
    },
    {
        "family": "book_edge_fv_calibration",
        "artifact": "v28_frozen_book_edge_fv_calibration",
        "state": OUT_DIR / "v28_frozen_book_plus05_entry_state.json",
        "report": OUT_DIR / "v28_frozen_book_edge_fv_calibration_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "candidate", "rule", "physics", "source"],
        "expected_report_fields": ["lanes", "any_fv_ready", "min_settled"],
        "fixed_selection_fields": [],
        "allow_report_without_freeze_ts": True,
        "note": "Companion FV calibration report for frozen book-edge entry lanes; compares raw, book, and predeclared blends on future rows only.",
    },
    {
        "family": "recross_book_shrink_fv",
        "artifact": "v28_frozen_recross_book_shrink_fv",
        "state": OUT_DIR / "v28_frozen_recross_book_shrink_fv_state.json",
        "report": OUT_DIR / "v28_frozen_recross_book_shrink_fv_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "entry_policy", "variant", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator_markets", "summary", "score", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen recross/book-disagreement FV shrinkage challenger; validates future-only book anchoring in unstable path geometry.",
    },
    {
        "family": "boundary_clock_repair_entry",
        "artifact": "v28_frozen_boundary_clock_repair_entry",
        "state": OUT_DIR / "v28_frozen_boundary_clock_repair_entry_state.json",
        "report": OUT_DIR / "v28_frozen_boundary_clock_repair_entry_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "base_policy", "candidate", "coverage_floor", "danger_rule", "repair_rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "target_summary", "candidate_summary", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen target-coverage repair candidate; skips boundary-clock hazard rows and repairs coverage with lowest-recross clean rows.",
    },
    {
        "family": "boundary_clock_fv_entry_bridge",
        "artifact": "v28_frozen_boundary_clock_fv_entry_bridge",
        "state": OUT_DIR / "v28_frozen_boundary_clock_fv_entry_bridge_state.json",
        "report": OUT_DIR / "v28_frozen_boundary_clock_fv_entry_bridge_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "base_policy", "candidate", "adjusted_edge_floor", "coverage_floor", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "target_summary", "candidate_summary", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen entry bridge from boundary-clock adjusted FV; validates adjusted-edge skip plus low-recross repair on future rows only.",
    },
    {
        "family": "book_trajectory_fv",
        "artifact": "v28_frozen_book_trajectory_fv",
        "state": OUT_DIR / "v28_frozen_book_trajectory_fv_state.json",
        "report": OUT_DIR / "v28_frozen_book_trajectory_fv_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "candidate", "rule"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "candidate", "views"],
        "fixed_selection_fields": ["candidate"],
        "note": "Frozen book-trajectory FV shrinkage candidate; validates fixed physics thresholds on post-freeze observations.",
    },
    {
        "family": "weak_reversal_residual_repair",
        "artifact": "v28_frozen_weak_reversal_residual_repair",
        "state": OUT_DIR / "v28_frozen_weak_reversal_residual_repair_freeze.json",
        "report": OUT_DIR / "v28_frozen_weak_reversal_residual_repair_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "policy", "base_target_policy", "weak_reversal", "residual_skip"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "policy", "future_denominator", "candidate_summary", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen entry repair candidate for weak-boundary reversal plus NO-side 5-8pp residual rows.",
    },
    {
        "family": "weak_reversal_residual_fv_shrink",
        "artifact": "v28_frozen_weak_reversal_residual_fv_shrink",
        "state": OUT_DIR / "v28_frozen_weak_reversal_residual_fv_shrink_freeze.json",
        "report": OUT_DIR / "v28_frozen_weak_reversal_residual_fv_shrink_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "variant", "target_policy", "weak_reversal", "fv_adjustment"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "raw_all", "variant_all", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen calibration validator for half-to-50 residual shrink after weak-boundary reversal.",
    },
    {
        "family": "no_mid_edge_fv",
        "artifact": "v28_frozen_no_mid_edge_fv",
        "state": OUT_DIR / "v28_frozen_no_mid_edge_fv_freeze.json",
        "report": OUT_DIR / "v28_frozen_no_mid_edge_fv_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "variant", "target_policy", "fv_adjustment"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "raw", "variant", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen broader NO 5-8pp book-anchor FV shrink; validates whether mid-edge NO conviction is overconfident out of sample.",
    },
    {
        "family": "early_boundary_wait_repair",
        "artifact": "v28_frozen_early_boundary_wait_repair",
        "state": OUT_DIR / "v28_frozen_early_boundary_wait_repair_state.json",
        "report": OUT_DIR / "v28_frozen_early_boundary_wait_repair_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "candidate", "danger_rule", "wait_rule", "repair_rule", "params"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "target_summary", "candidate_summary", "blockers"],
        "fixed_selection_fields": ["candidate"],
        "note": "Frozen early-boundary wait/repair candidate; validates whether very early high-recross boundary states should be aged before entry.",
    },
    {
        "family": "early_boundary_opposite_wait_repair",
        "artifact": "v28_frozen_early_boundary_opposite_wait_repair",
        "state": OUT_DIR / "v28_frozen_early_boundary_opposite_wait_repair_state.json",
        "report": OUT_DIR / "v28_frozen_early_boundary_opposite_wait_repair_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "candidate", "danger_rule", "wait_rule", "repair_rule", "params"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "target_summary", "candidate_summary", "blockers"],
        "fixed_selection_fields": ["candidate"],
        "note": "Frozen early-boundary opposite-side wait/repair candidate; validates whether the first boundary thesis should be reversed after clock decay.",
    },
    {
        "family": "gamma_repair_entry",
        "artifact": "v28_frozen_gamma_repair_entry",
        "state": OUT_DIR / "v28_frozen_gamma_repair_entry_state.json",
        "report": OUT_DIR / "v28_frozen_gamma_repair_entry_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "base_policy", "candidate", "repair_rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "target_summary", "candidate_summary", "repair_summary", "blockers"],
        "fixed_selection_fields": [],
        "note": "Frozen gamma/recross repair bridge; tests whether cheap near-boundary optionality can repair target coverage without broad exposure.",
    },
    {
        "family": "raw_entry_coverage_valve",
        "artifact": "v28_raw_entry_coverage_valve",
        "state": OUT_DIR / "v28_frozen_raw_entry_calibrated_probability_state.json",
        "report": OUT_DIR / "v28_raw_entry_coverage_valve_latest.json",
        "expected_state_fields": ["freeze_ts", "entry_policy"],
        "expected_report_fields": ["freeze_ts", "best_policy", "ranked"],
        "fixed_selection_fields": [],
        "note": "Coverage-valve artifact can rank rows, but downstream target FV must freeze the chosen policy before promotion evidence.",
    },
    {
        "family": "raw_p52_favorite_valley_skip",
        "artifact": "v28_frozen_raw_p52_favorite_valley_skip",
        "state": OUT_DIR / "v28_frozen_raw_p52_favorite_valley_skip_state.json",
        "report": OUT_DIR / "v28_frozen_raw_p52_favorite_valley_skip_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "candidate", "base_policy", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "base", "candidate_summary", "skipped_summary"],
        "fixed_selection_fields": [],
        "note": "Frozen raw-p52 payoff-geometry challenger; validates whether skipping the 65-75c middle-favorite valley preserves target coverage while improving EV.",
    },
    {
        "family": "raw_p52_mid_edge_skip",
        "artifact": "v28_frozen_raw_p52_mid_edge_skip",
        "state": OUT_DIR / "v28_frozen_raw_p52_mid_edge_skip_state.json",
        "report": OUT_DIR / "v28_frozen_raw_p52_mid_edge_skip_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "candidate", "base_policy", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "base", "candidate_summary", "skipped_summary"],
        "fixed_selection_fields": [],
        "note": "Frozen raw-p52 false-conviction challenger; validates whether skipping the whole 5-10pp edge band improves EV without unacceptable coverage loss.",
    },
    {
        "family": "raw_p52_shadow_mid_edge_skip",
        "artifact": "v28_frozen_raw_p52_shadow_mid_edge_skip",
        "state": OUT_DIR / "v28_frozen_raw_p52_shadow_mid_edge_skip_state.json",
        "report": OUT_DIR / "v28_frozen_raw_p52_shadow_mid_edge_skip_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "candidate", "base_policy", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "base", "candidate_summary", "skipped_summary"],
        "fixed_selection_fields": [],
        "note": "Frozen raw-p52 expansion-surface challenger; preserves approved-entry rows and validates whether rejected-actionable 5-10pp edge rows are false-conviction traps.",
    },
    {
        "family": "raw_p52_book_disagreement_skip",
        "artifact": "v28_frozen_raw_p52_book_disagreement_skip",
        "state": OUT_DIR / "v28_frozen_raw_p52_book_disagreement_skip_state.json",
        "report": OUT_DIR / "v28_frozen_raw_p52_book_disagreement_skip_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "candidate", "base_policy", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "base", "candidate_summary", "skipped_summary"],
        "fixed_selection_fields": [],
        "note": "Frozen raw-p52 crowd-prior challenger; validates whether large selected-side FV disagreement above executable book marks overconfidence.",
    },
    {
        "family": "raw_p52_book_shrink_entry",
        "artifact": "v28_frozen_raw_p52_book_shrink_entry",
        "state": OUT_DIR / "v28_frozen_raw_p52_book_shrink_entry_state.json",
        "report": OUT_DIR / "v28_frozen_raw_p52_book_shrink_entry_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "candidate", "base_policy", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "base", "candidate_summary"],
        "fixed_selection_fields": [],
        "note": "Frozen raw-p52 probabilistic crowd-prior shrink challenger for large selected-side FV disagreement above executable book.",
    },
    {
        "family": "raw_p52_early_no_boundary_skip",
        "artifact": "v28_frozen_raw_p52_early_no_boundary_skip",
        "state": OUT_DIR / "v28_frozen_raw_p52_early_no_boundary_skip_state.json",
        "report": OUT_DIR / "v28_frozen_raw_p52_early_no_boundary_skip_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "candidate", "base_policy", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "base", "candidate_summary", "skipped_summary"],
        "fixed_selection_fields": [],
        "note": "Frozen raw-p52 early NO boundary-decay skip; broad physics check that is likely too selective.",
    },
    {
        "family": "raw_p52_early_no_boundary_band_skip",
        "artifact": "v28_frozen_raw_p52_early_no_boundary_band_skip",
        "state": OUT_DIR / "v28_frozen_raw_p52_early_no_boundary_band_skip_state.json",
        "report": OUT_DIR / "v28_frozen_raw_p52_early_no_boundary_band_skip_latest.json",
        "expected_state_fields": ["freeze_ts_utc", "candidate", "base_policy", "rule", "physics"],
        "expected_report_fields": ["freeze.freeze_ts_utc", "future_denominator", "base", "candidate_summary", "skipped_summary"],
        "fixed_selection_fields": [],
        "note": "Frozen raw-p52 middle-confidence early NO boundary skip; preserves target coverage in discovery while testing recross/path fragility.",
    },
    {
        "family": "live_readiness",
        "artifact": "v28_live_trade_readiness",
        "state": None,
        "report": OUT_DIR / "v28_live_trade_readiness_latest.json",
        "expected_state_fields": [],
        "expected_report_fields": ["any_live_ready", "candidates"],
        "fixed_selection_fields": [],
        "note": "Gate artifact; does not itself create candidates, but must not promote anything while evidence blockers remain.",
        "gate_only": True,
    },
]


def load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def get_path(payload: dict[str, Any], dotted: str) -> Any:
    current: Any = payload
    for part in dotted.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def missing_fields(payload: dict[str, Any], fields: list[str]) -> list[str]:
    return [field for field in fields if get_path(payload, field) in (None, "")]


def report_has_selected_rows(report: dict[str, Any]) -> bool:
    for key in ["forward", "ranked", "candidates", "rows", "future_rows"]:
        rows = report.get(key)
        if isinstance(rows, list) and rows:
            return True
    ranked = report.get("ranked")
    return isinstance(ranked, dict) and bool(ranked)


def audit_candidate(spec: dict[str, Any]) -> dict[str, Any]:
    state_path = spec.get("state")
    report_path = spec.get("report")
    state = load_json(state_path)
    report = load_json(report_path)
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: Any) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    gate_only = bool(spec.get("gate_only"))
    state_freeze_ts = state.get("freeze_ts") or state.get("freeze_ts_utc")
    report_freeze_ts = report.get("freeze_ts") or get_path(report, "freeze.freeze_ts_utc")
    add("report_exists", bool(report), str(report_path))
    if not gate_only:
        add("state_exists", bool(state), str(state_path))
        add("state_has_freeze_ts", bool(state_freeze_ts), state_freeze_ts)
    missing_state = missing_fields(state, spec.get("expected_state_fields") or [])
    missing_report = missing_fields(report, spec.get("expected_report_fields") or [])
    if missing_state:
        add("state_required_fields_present", False, missing_state)
    elif spec.get("expected_state_fields"):
        add("state_required_fields_present", True, spec.get("expected_state_fields"))
    if missing_report:
        add("report_required_fields_present", False, missing_report)
    elif spec.get("expected_report_fields"):
        add("report_required_fields_present", True, spec.get("expected_report_fields"))

    if state and report and state_freeze_ts and not spec.get("allow_report_without_freeze_ts"):
        add("report_matches_state_freeze_ts", report_freeze_ts == state_freeze_ts, {
            "state_freeze_ts": state_freeze_ts,
            "report_freeze_ts": report_freeze_ts,
        })
    for field in spec.get("fixed_selection_fields") or []:
        if state and report and field in report:
            add(f"report_matches_state_{field}", report.get(field) == state.get(field), {
                "state": state.get(field),
                "report": report.get(field),
            })
    if report:
        add("report_has_scored_rows", report_has_selected_rows(report), "forward/ranked/candidates rows")

    dynamic_best_risk = False
    if spec.get("artifact") == "v28_raw_entry_coverage_valve":
        dynamic_best_risk = True
    if not gate_only and not state:
        dynamic_best_risk = True

    failed = [item for item in checks if item["passed"] is not True]
    hard_failed = [item for item in failed if item.get("name") != "report_has_scored_rows"]
    status = "pass" if not failed and not dynamic_best_risk else "watch"
    if hard_failed:
        status = "fail"
    return {
        "family": spec.get("family"),
        "artifact": spec.get("artifact"),
        "status": status,
        "dynamic_best_risk": dynamic_best_risk,
        "note": spec.get("note"),
        "state_path": str(state_path) if state_path else None,
        "report_path": str(report_path) if report_path else None,
        "freeze_ts": state_freeze_ts or report_freeze_ts,
        "checks": checks,
        "failures": failed,
        "hard_failures": hard_failed,
    }


def build_report() -> dict[str, Any]:
    rows = [audit_candidate(spec) for spec in CANDIDATES]
    failures = [row for row in rows if row.get("status") == "fail"]
    watches = [row for row in rows if row.get("status") == "watch"]
    return {
        "purpose": "Catch candidate-selection drift and dynamic-best leakage before interpreting forward evidence.",
        "all_clear": not failures,
        "fail_count": len(failures),
        "watch_count": len(watches),
        "rows": rows,
        "interpretation": [
            "Pass means the artifact has a frozen state/report relationship suitable for continued forward monitoring.",
            "Watch means the artifact is diagnostic or dynamic-ranked and should not be treated as promotion evidence by itself.",
            "Fail means a report/state mismatch or missing freeze metadata needs attention before relying on the artifact.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, bool):
        return str(value)
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Anti-Overfit Freeze Audit",
        "",
        f"- All clear: `{report.get('all_clear')}`",
        f"- Fail/watch counts: `{report.get('fail_count')}/{report.get('watch_count')}`",
        "",
        "## Candidate Artifacts",
        "",
        "| family | artifact | status | freeze ts | dynamic-best risk | failures |",
        "|---|---|---:|---|---:|---|",
    ]
    for row in report.get("rows") or []:
        failures = ", ".join(item.get("name") or "" for item in row.get("failures") or []) or "none"
        lines.append(
            f"| {row.get('family')} | `{row.get('artifact')}` | `{row.get('status')}` | "
            f"`{fmt(row.get('freeze_ts'))}` | `{row.get('dynamic_best_risk')}` | {failures} |"
        )
    lines.extend(["", "## Interpretation", ""])
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(["", "## Notes", ""])
    for row in report.get("rows") or []:
        lines.append(f"- `{row.get('artifact')}`: {row.get('note')}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
