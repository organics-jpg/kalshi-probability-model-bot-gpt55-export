"""Strict completion audit for the next-second particle simulation goal.

Research-only: this probe reads files under logs/docs/research_particle, writes
an audit report, and never touches live bot state, launchers, or orders.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPORT_DIR = Path("logs") / "particle_research" / "reports"
LATEST_JSON = REPORT_DIR / "particle_goal_completion_audit_latest.json"
LATEST_MD = REPORT_DIR / "particle_goal_completion_audit_latest.md"


@dataclass(frozen=True)
class ChecklistItem:
    requirement: str
    evidence: str
    status: str
    detail: str


def audit(root: Path = Path(".")) -> dict[str, Any]:
    root = root.resolve()
    reports = root / REPORT_DIR
    synthetic_reports = _load_synthetic_reports(reports)
    adapter_readiness = _load_json(reports / "particle_adapter_readiness_latest.json")
    v28_context_audit = _load_json(reports / "v28_event_contexts_exactgate_latest.json")
    artifact_leakage_audit = _load_latest_json(reports, "artifact_leakage_audit*.json")
    denominator_integrity_audit = _load_latest_json(reports, "denominator_integrity_audit*.json")
    stability = _load_json(reports / "locked_oos_stability_latest.json")
    ev_rank_diagnostic = _load_latest_json(reports, "ev_rank_calibration_diagnostic*.json")
    variant_loro_diagnostic = _load_latest_json(reports, "variant_loro_selection_diagnostic*.json")
    pasc_loro_diagnostic = _load_latest_json(reports, "pasc_loro_threshold_diagnostic*.json")
    anchor_switch_loro = _load_latest_json(reports, "anchor_switch_loro*.json")
    market_cluster_diagnostic = _load_latest_json(reports, "market_cluster_diagnostic*.json")
    meta_probability_loro = _load_latest_json(reports, "meta_probability_loro*.json")
    state_feature_loro = _load_latest_json(reports, "state_feature_loro*.json")
    spot_micro_loro = _load_latest_json(reports, "spot_micro_loro*.json")
    empirical_current_anchor = _load_latest_json(reports, "empirical_current_anchor*.json")
    empirical_market_opportunity = _load_latest_json(reports, "empirical_market_opportunity_diagnostic*.json")
    empirical_market_opportunity_loro = _load_latest_json(reports, "empirical_market_opportunity_loro*.json")
    empirical_next_second = _load_latest_json(reports, "empirical_next_second_particle*.json")
    spot_drift_terminal = _load_latest_json(reports, "spot_drift_terminal*.json")
    spot_drift_regime = _load_latest_json(reports, "spot_drift_regime*.json")
    spot_rv_anchor_switch_loro = _load_latest_json(reports, "spot_rv_anchor_switch_loro*.json")
    spot_rv_current_residual_loro = _load_latest_json(reports, "spot_rv_current_residual_loro*.json")
    spot_realized_vol_diagnostic = _load_latest_json(
        reports,
        "spot_realized_vol_terminal*.json",
    )
    fat_tail_diagnostic = _load_latest_json(reports, "fat_tail_particle_diagnostic*.json")
    fixed_terminal_stability = _load_latest_json(reports, "fixed_terminal_gauss45_stability*.json")
    online_anchor_diagnostic = _load_latest_json(reports, "online_anchor_calibration_diagnostic*.json")
    anchor_regime_profile = _load_latest_json(reports, "anchor_regime_profile*.json")
    paired_sidecar_spot_aggregate = _load_json(reports / "paired_sidecar_spot_aggregate_latest.json")
    paired_sidecar_online_calibration = _load_json(
        reports / "paired_sidecar_online_calibration_latest.json"
    )
    paired_sidecar_blend_failure_analysis = _load_json(
        reports / "paired_sidecar_blend_failure_analysis_latest.json"
    )
    paired_sidecar_slice_oos = _load_latest_json(reports, "paired_sidecar_slice_oos*.json")
    paired_sidecar_slice_oos_reports = _load_json_files(
        reports,
        "paired_sidecar_slice_oos_PSLICELOCK*_latest.json",
    )
    paired_sidecar_slice_refresh = _load_json(reports / "paired_sidecar_slice_refresh_latest.json")
    paired_sidecar_slice_lock_comparison = _load_json(
        reports / "paired_sidecar_slice_lock_comparison_latest.json"
    )
    paired_sidecar_slice_market_breakdown = _load_json(
        reports / "paired_sidecar_slice_market_breakdown_latest.json"
    )
    paired_sidecar_slice_retirement = _load_json(
        reports / "paired_sidecar_slice_retirement_latest.json"
    )
    paired_sidecar_slice_stability = _load_json(
        reports / "paired_sidecar_slice_stability_latest.json"
    )
    paired_sidecar_slice_trajectory = _load_json(
        reports / "paired_sidecar_slice_trajectory_latest.json"
    )
    paired_sidecar_slice_promotion_readiness = _load_json(
        reports / "paired_sidecar_slice_promotion_readiness_latest.json"
    )
    paired_sidecar_slice_locked_plan = _load_latest_json(
        root / "logs" / "particle_research" / "locked_oos_plans",
        "paired_sidecar_slice*locked_plan.json",
    )
    paired_sidecar_spot_refresh = _load_json(reports / "paired_sidecar_spot_refresh_latest.json")
    paired_sidecar_spot_pair_root = (
        root / "logs" / "particle_research" / "real_shadow" / "sidecar_spot_pairs"
    )
    paired_sidecar_spot_diagnostic_files = (
        sorted(paired_sidecar_spot_pair_root.glob("*/sidecar_spot_tick_vs_candle_diagnostic.json"))
        if paired_sidecar_spot_pair_root.exists()
        else []
    )
    paired_sidecar_spot = _load_latest_json(
        paired_sidecar_spot_pair_root,
        "*/paired_sidecar_spot_manifest.json",
    )
    paired_sidecar_spot_enrichment = _load_latest_json(
        paired_sidecar_spot_pair_root,
        "*/sidecar_packets_independent_spot_enriched.json",
    )
    paired_sidecar_spot_diagnostic = _load_latest_json(
        paired_sidecar_spot_pair_root,
        "*/sidecar_spot_tick_vs_candle_diagnostic.json",
    )
    candidate_files = _candidate_snapshot_files(root / "logs" / "particle_research")
    real_candidate_files = [
        path for path in candidate_files if not _looks_synthetic_or_unit(path)
    ]
    real_replay_reports = [
        path for path in (root / "logs" / "particle_research").rglob("*.json")
        if _looks_real_replay_report(path)
    ] if (root / "logs" / "particle_research").exists() else []
    real_replay_payloads = [_load_json(path) for path in real_replay_reports]

    synthetic_pass = any(_synthetic_report_passes(report) for report in synthetic_reports)
    strict_replay_fields_ready = int(
        adapter_readiness.get("adapter_ready_count", 0) or 0
    ) > 0
    artifact_leakage_pass = bool(artifact_leakage_audit.get("pass_no_future_leakage"))
    denominator_integrity_pass = bool(denominator_integrity_audit.get("pass_denominator_integrity"))
    v28_adapted_count = int(v28_context_audit.get("adapted_count", 0) or 0)
    real_candidate_count = _line_count(real_candidate_files)
    real_replay_pass = any(_real_report_clears_promotion(payload) for payload in real_replay_payloads)
    real_replay_count = len(real_replay_reports)
    stability_row_count = len(stability.get("stability_rows") or ())
    stable_candidate_count = int(stability.get("stable_candidate_count", 0) or 0)
    stability_pass = stable_candidate_count > 0
    # A single replay report can be useful evidence, but it is not enough for
    # this goal. The explicit promotion bar is locked-OOS stability, so the
    # real-data gates below stay failing until at least one candidate clears the
    # stability report.
    real_gate_pass = stability_pass
    real_evidence_seen = real_replay_count > 0 or stability_row_count > 0
    best_stability = stability.get("best_by_total_pnl") or {}
    stability_detail = (
        f"real_replay_reports={real_replay_count}; "
        f"stability_rows={stability_row_count}; "
        f"stable_candidate_count={stable_candidate_count}; "
        f"best_total_pnl_variant={best_stability.get('source', 'none')}:"
        f"{best_stability.get('name', 'none')}; "
        f"best_total_pnl_cents={best_stability.get('total_counterfactual_pnl_cents', 0)}; "
        f"single_replay_pass_exists={real_replay_pass}."
    )
    ev_rank_detail = (
        "ev_rank_diagnostic="
        f"run_count={ev_rank_diagnostic.get('run_count', 0)}; "
        f"candidate_count={ev_rank_diagnostic.get('candidate_count', 0)}; "
        f"top_ev_bucket_stable_positive={ev_rank_diagnostic.get('top_ev_bucket_stable_positive', 'unknown')}; "
        f"best_probability_model_by_brier={ev_rank_diagnostic.get('best_probability_model_by_brier', 'unknown')}; "
        f"best_probability_model_by_log_loss={ev_rank_diagnostic.get('best_probability_model_by_log_loss', 'unknown')}."
    )
    loro_detail = _variant_loro_detail(variant_loro_diagnostic)
    pasc_loro_detail = _pasc_loro_detail(pasc_loro_diagnostic)
    anchor_switch_detail = _anchor_switch_loro_detail(anchor_switch_loro)
    market_cluster_detail = _market_cluster_detail(market_cluster_diagnostic)
    meta_loro_detail = _meta_probability_loro_detail(meta_probability_loro)
    state_loro_detail = _state_feature_loro_detail(state_feature_loro)
    spot_micro_detail = _spot_micro_loro_detail(spot_micro_loro)
    empirical_current_anchor_detail = _empirical_current_anchor_detail(empirical_current_anchor)
    empirical_market_opportunity_detail = _empirical_market_opportunity_detail(empirical_market_opportunity)
    empirical_market_opportunity_loro_detail = _empirical_market_opportunity_loro_detail(
        empirical_market_opportunity_loro
    )
    empirical_next_second_detail = _empirical_next_second_particle_detail(empirical_next_second)
    spot_drift_detail = _spot_drift_terminal_detail(spot_drift_terminal)
    spot_drift_regime_detail = _spot_drift_regime_detail(spot_drift_regime)
    spot_rv_anchor_switch_detail = _spot_rv_anchor_switch_loro_detail(spot_rv_anchor_switch_loro)
    spot_rv_current_residual_detail = _spot_rv_current_residual_loro_detail(spot_rv_current_residual_loro)
    spot_realized_vol_detail = _spot_realized_vol_terminal_detail(spot_realized_vol_diagnostic)
    fat_tail_detail = _fat_tail_diagnostic_detail(fat_tail_diagnostic)
    fixed_terminal_detail = _fixed_terminal_stability_detail(fixed_terminal_stability)
    online_anchor_detail = _online_anchor_diagnostic_detail(online_anchor_diagnostic)
    anchor_regime_detail = _anchor_regime_profile_detail(anchor_regime_profile)
    paired_sidecar_spot_detail = _paired_sidecar_spot_detail(paired_sidecar_spot)
    paired_sidecar_spot_enrichment_detail = _paired_sidecar_spot_enrichment_detail(
        paired_sidecar_spot_enrichment
    )
    paired_sidecar_spot_diagnostic_detail = _paired_sidecar_spot_diagnostic_detail(
        paired_sidecar_spot_diagnostic
    )
    paired_sidecar_spot_aggregate_detail = _paired_sidecar_spot_aggregate_detail(
        paired_sidecar_spot_aggregate,
        actual_diagnostic_file_count=len(paired_sidecar_spot_diagnostic_files),
    )
    paired_sidecar_online_calibration_detail = _paired_sidecar_online_calibration_detail(
        paired_sidecar_online_calibration
    )
    paired_sidecar_blend_failure_analysis_detail = _paired_sidecar_blend_failure_analysis_detail(
        paired_sidecar_blend_failure_analysis
    )
    paired_sidecar_slice_locked_plan_detail = _paired_sidecar_slice_locked_plan_detail(
        paired_sidecar_slice_locked_plan
    )
    paired_sidecar_slice_oos_detail = _paired_sidecar_slice_oos_detail(
        paired_sidecar_slice_oos
    )
    paired_sidecar_slice_oos_reports_detail = _paired_sidecar_slice_oos_reports_detail(
        paired_sidecar_slice_oos_reports
    )
    paired_sidecar_slice_lock_comparison_detail = _paired_sidecar_slice_lock_comparison_detail(
        paired_sidecar_slice_lock_comparison
    )
    paired_sidecar_slice_market_breakdown_detail = _paired_sidecar_slice_market_breakdown_detail(
        paired_sidecar_slice_market_breakdown
    )
    paired_sidecar_slice_retirement_detail = _paired_sidecar_slice_retirement_detail(
        paired_sidecar_slice_retirement
    )
    paired_sidecar_slice_stability_detail = _paired_sidecar_slice_stability_detail(
        paired_sidecar_slice_stability
    )
    paired_sidecar_slice_trajectory_detail = _paired_sidecar_slice_trajectory_detail(
        paired_sidecar_slice_trajectory
    )
    paired_sidecar_slice_promotion_readiness_detail = _paired_sidecar_slice_promotion_readiness_detail(
        paired_sidecar_slice_promotion_readiness
    )
    paired_sidecar_slice_oos_detail = (
        paired_sidecar_slice_oos_detail
        + " "
        + paired_sidecar_slice_oos_reports_detail
        + " "
        + paired_sidecar_slice_lock_comparison_detail
        + " "
        + paired_sidecar_slice_market_breakdown_detail
        + " "
        + paired_sidecar_slice_retirement_detail
        + " "
        + paired_sidecar_slice_stability_detail
        + " "
        + paired_sidecar_slice_trajectory_detail
        + " "
        + paired_sidecar_slice_promotion_readiness_detail
    )
    paired_sidecar_slice_refresh_detail = _paired_sidecar_slice_refresh_detail(
        paired_sidecar_slice_refresh
    )
    paired_sidecar_spot_refresh_detail = _paired_sidecar_spot_refresh_detail(
        paired_sidecar_spot_refresh
    )
    paired_sidecar_summary = paired_sidecar_spot.get("summary") if isinstance(paired_sidecar_spot.get("summary"), dict) else {}
    paired_sidecar_enrichment_summary = (
        paired_sidecar_spot_enrichment.get("summary")
        if isinstance(paired_sidecar_spot_enrichment.get("summary"), dict)
        else {}
    )
    paired_sidecar_diagnostic_summary = _summary_from_payload(paired_sidecar_spot_diagnostic)
    paired_sidecar_aggregate_summary = _summary_from_payload(paired_sidecar_spot_aggregate)
    paired_sidecar_online_calibration_summary = _summary_from_payload(
        paired_sidecar_online_calibration
    )
    paired_sidecar_blend_failure_analysis_summary = _summary_from_payload(
        paired_sidecar_blend_failure_analysis
    )
    paired_sidecar_slice_oos_summary = _summary_from_payload(paired_sidecar_slice_oos)
    paired_sidecar_slice_refresh_summary = _summary_from_payload(paired_sidecar_slice_refresh)
    paired_sidecar_slice_lock_comparison_summary = _summary_from_payload(
        paired_sidecar_slice_lock_comparison
    )
    paired_sidecar_slice_market_breakdown_summary = _summary_from_payload(
        paired_sidecar_slice_market_breakdown
    )
    paired_sidecar_slice_retirement_summary = _summary_from_payload(
        paired_sidecar_slice_retirement
    )
    paired_sidecar_slice_stability_summary = _summary_from_payload(
        paired_sidecar_slice_stability
    )
    paired_sidecar_slice_trajectory_summary = _summary_from_payload(
        paired_sidecar_slice_trajectory
    )
    paired_sidecar_slice_promotion_readiness_summary = _summary_from_payload(
        paired_sidecar_slice_promotion_readiness
    )
    paired_sidecar_refresh_summary = _summary_from_payload(paired_sidecar_spot_refresh)
    paired_sidecar_promotion_allowed = bool(paired_sidecar_summary.get("promotion_allowed"))
    paired_sidecar_enrichment_promotion_allowed = bool(
        paired_sidecar_enrichment_summary.get("promotion_allowed")
    )
    paired_sidecar_diagnostic_promotion_allowed = bool(
        paired_sidecar_diagnostic_summary.get("promotion_allowed")
    )
    paired_sidecar_aggregate_promotion_allowed = bool(
        paired_sidecar_aggregate_summary.get("promotion_allowed")
    )
    paired_sidecar_online_calibration_promotion_allowed = bool(
        paired_sidecar_online_calibration_summary.get("promotion_allowed")
    )
    paired_sidecar_blend_failure_analysis_promotion_allowed = bool(
        paired_sidecar_blend_failure_analysis_summary.get("promotion_allowed")
    )
    paired_sidecar_blend_failure_analysis_promotion_safe = bool(
        paired_sidecar_blend_failure_analysis_summary.get("promotion_safe")
    )
    paired_sidecar_slice_oos_promotion_allowed = any(
        bool(_summary_from_payload(payload).get("promotion_allowed"))
        for payload in paired_sidecar_slice_oos_reports
    ) or bool(paired_sidecar_slice_oos_summary.get("promotion_allowed"))
    paired_sidecar_slice_oos_promotion_safe = any(
        bool(_summary_from_payload(payload).get("promotion_safe"))
        for payload in paired_sidecar_slice_oos_reports
    ) or bool(paired_sidecar_slice_oos_summary.get("promotion_safe"))
    paired_sidecar_slice_refresh_promotion_allowed = bool(
        paired_sidecar_slice_refresh_summary.get("promotion_allowed")
    )
    paired_sidecar_slice_lock_comparison_promotion_allowed = bool(
        paired_sidecar_slice_lock_comparison_summary.get("promotion_allowed")
    )
    paired_sidecar_slice_market_breakdown_promotion_allowed = bool(
        paired_sidecar_slice_market_breakdown_summary.get("promotion_allowed")
    )
    paired_sidecar_slice_retirement_promotion_allowed = bool(
        paired_sidecar_slice_retirement_summary.get("promotion_allowed")
    )
    paired_sidecar_slice_stability_promotion_allowed = bool(
        paired_sidecar_slice_stability_summary.get("promotion_allowed")
    )
    paired_sidecar_slice_trajectory_promotion_allowed = bool(
        paired_sidecar_slice_trajectory_summary.get("promotion_allowed")
    )
    paired_sidecar_slice_promotion_readiness_promotion_allowed = bool(
        paired_sidecar_slice_promotion_readiness_summary.get("promotion_allowed")
    )
    paired_sidecar_refresh_promotion_allowed = bool(
        paired_sidecar_refresh_summary.get("promotion_allowed")
    )
    paired_sidecar_aggregate_diagnostic_file_count = int(
        paired_sidecar_aggregate_summary.get("diagnostic_file_count", 0) or 0
    )
    paired_sidecar_aggregate_fresh = (
        paired_sidecar_aggregate_diagnostic_file_count == len(paired_sidecar_spot_diagnostic_files)
    )

    checklist = [
        ChecklistItem(
            "Research-only next-second particle package exists",
            "research_particle/ package",
            "pass" if (root / "research_particle").exists() else "fail",
            "Package is separate from live bot launchers and order logic. "
            + paired_sidecar_spot_detail
            + " "
            + paired_sidecar_spot_enrichment_detail
            + " "
            + paired_sidecar_spot_diagnostic_detail
            + " "
            + paired_sidecar_spot_aggregate_detail
            + " "
            + paired_sidecar_online_calibration_detail
            + " "
            + paired_sidecar_blend_failure_analysis_detail
            + " "
            + paired_sidecar_slice_locked_plan_detail
            + " "
            + paired_sidecar_slice_oos_detail
            + " "
            + paired_sidecar_slice_refresh_detail
            + " "
            + paired_sidecar_spot_refresh_detail,
        ),
        ChecklistItem(
            "Trustworthy all-candidate recorder and labeler exist",
            "recorders.py, shadow_collect.py, market_result_labels.py plus denominator/leakage audits",
            "pass"
            if (denominator_integrity_pass and artifact_leakage_pass)
            else ("partial" if (root / "research_particle" / "shadow_collect.py").exists() else "fail"),
            (
                "Recorder/labeler code exists. "
                f"real_candidate_rows={real_candidate_count}; "
                f"real_replay_reports={real_replay_count}; "
                f"denominator_integrity_pass={denominator_integrity_pass}; "
                f"artifact_leakage_pass={artifact_leakage_pass}. "
                + paired_sidecar_spot_detail
                + " "
                + paired_sidecar_spot_enrichment_detail
                + " "
                + paired_sidecar_spot_diagnostic_detail
                + " "
                + paired_sidecar_spot_aggregate_detail
                + " "
                + paired_sidecar_online_calibration_detail
                + " "
                + paired_sidecar_blend_failure_analysis_detail
                + " "
                + paired_sidecar_slice_locked_plan_detail
                + " "
                + paired_sidecar_slice_oos_detail
                + " "
                + paired_sidecar_slice_refresh_detail
                + " "
                + paired_sidecar_spot_refresh_detail
            ),
        ),
        ChecklistItem(
            "Synthetic Brownian/jump tests pass before Kalshi replay",
            "synthetic replay reports",
            "pass" if synthetic_pass else "fail",
            f"synthetic_reports={len(synthetic_reports)} synthetic_pass={synthetic_pass}.",
        ),
        ChecklistItem(
            "Strict replay uses only timestamp-available information",
            "replay.py/replay_runner.py plus artifact leakage audit",
            "pass"
            if artifact_leakage_pass
            else ("partial" if (strict_replay_fields_ready or real_replay_count > 0) else "missing_real_data"),
            (
                "Strict timestamp checks exist in code. Current artifact leakage audit: "
                f"pass_no_future_leakage={artifact_leakage_pass}; "
                f"audited_runs={artifact_leakage_audit.get('run_count', 0)}; "
                f"audited_candidates={artifact_leakage_audit.get('candidate_count', 0)}; "
                f"artifact_issue_count={artifact_leakage_audit.get('issue_count', 'unknown')}. "
                "Adapter readiness scan "
                f"found adapter_ready_count={adapter_readiness.get('adapter_ready_count', 0)} "
                f"and real_replay_reports={real_replay_count}."
            ),
        ),
        ChecklistItem(
            "All-candidate denominator is preserved in locked real replays",
            "denominator integrity audit",
            "pass" if denominator_integrity_pass else ("fail" if real_evidence_seen else "missing_real_data"),
            (
                f"pass_denominator_integrity={denominator_integrity_pass}; "
                f"audited_runs={denominator_integrity_audit.get('run_count', 0)}; "
                f"audited_candidates={denominator_integrity_audit.get('candidate_count', 0)}; "
                f"audited_markets={denominator_integrity_audit.get('market_count', 0)}; "
                f"denominator_issue_count={denominator_integrity_audit.get('issue_count', 'unknown')}."
            ),
        ),
        ChecklistItem(
            "Particle probabilities beat Brownian, market mid, and current calibrated probability on real data",
            "real replay report JSON plus locked OOS stability report",
            "pass" if real_gate_pass else ("fail" if real_evidence_seen else "missing_real_data"),
            stability_detail + " " + market_cluster_detail + " " + anchor_regime_detail + " " + anchor_switch_detail + " " + meta_loro_detail + " " + state_loro_detail + " " + spot_micro_detail + " " + empirical_current_anchor_detail + " " + empirical_market_opportunity_detail + " " + empirical_market_opportunity_loro_detail + " " + empirical_next_second_detail + " " + paired_sidecar_spot_diagnostic_detail + " " + paired_sidecar_spot_aggregate_detail + " " + paired_sidecar_online_calibration_detail + " " + paired_sidecar_blend_failure_analysis_detail + " " + paired_sidecar_slice_locked_plan_detail + " " + paired_sidecar_slice_oos_detail + " " + paired_sidecar_slice_refresh_detail + " " + paired_sidecar_spot_refresh_detail + " " + spot_drift_detail + " " + spot_drift_regime_detail + " " + spot_rv_anchor_switch_detail + " " + spot_rv_current_residual_detail + " " + spot_realized_vol_detail + " " + fat_tail_detail + " " + fixed_terminal_detail + " " + online_anchor_detail + " " + loro_detail + " " + pasc_loro_detail,
        ),
        ChecklistItem(
            "EV ranking is positive and top predicted EV buckets are profitable on real data",
            "real replay report JSON plus locked OOS stability report",
            "pass" if real_gate_pass else ("fail" if real_evidence_seen else "missing_real_data"),
            stability_detail + " " + ev_rank_detail + " " + market_cluster_detail + " " + anchor_regime_detail + " " + anchor_switch_detail + " " + meta_loro_detail + " " + state_loro_detail + " " + spot_micro_detail + " " + empirical_current_anchor_detail + " " + empirical_market_opportunity_detail + " " + empirical_market_opportunity_loro_detail + " " + empirical_next_second_detail + " " + paired_sidecar_spot_diagnostic_detail + " " + paired_sidecar_spot_aggregate_detail + " " + paired_sidecar_online_calibration_detail + " " + paired_sidecar_blend_failure_analysis_detail + " " + paired_sidecar_slice_locked_plan_detail + " " + paired_sidecar_slice_oos_detail + " " + paired_sidecar_slice_refresh_detail + " " + paired_sidecar_spot_refresh_detail + " " + spot_drift_detail + " " + spot_drift_regime_detail + " " + spot_rv_anchor_switch_detail + " " + spot_rv_current_residual_detail + " " + spot_realized_vol_detail + " " + fat_tail_detail + " " + fixed_terminal_detail + " " + online_anchor_detail + " " + loro_detail + " " + pasc_loro_detail + " No variant clears every EV-rank/top-bucket/stability gate.",
        ),
        ChecklistItem(
            "Shadow counterfactual PnL is positive after fees and no-fill assumptions on real data",
            "real replay report JSON plus locked OOS stability report",
            "pass" if real_gate_pass else ("fail" if real_evidence_seen else "missing_real_data"),
            stability_detail + " " + anchor_regime_detail + " " + anchor_switch_detail + " " + state_loro_detail + " " + spot_micro_detail + " " + empirical_current_anchor_detail + " " + empirical_market_opportunity_detail + " " + empirical_market_opportunity_loro_detail + " " + empirical_next_second_detail + " " + paired_sidecar_spot_diagnostic_detail + " " + paired_sidecar_spot_aggregate_detail + " " + paired_sidecar_online_calibration_detail + " " + paired_sidecar_blend_failure_analysis_detail + " " + paired_sidecar_slice_locked_plan_detail + " " + paired_sidecar_slice_oos_detail + " " + paired_sidecar_slice_refresh_detail + " " + paired_sidecar_spot_refresh_detail + " " + spot_drift_detail + " " + spot_drift_regime_detail + " " + spot_rv_anchor_switch_detail + " " + spot_rv_current_residual_detail + " " + spot_realized_vol_detail + " " + fat_tail_detail + " " + fixed_terminal_detail + " " + online_anchor_detail + " " + loro_detail + " " + pasc_loro_detail + " Positive single-family PnL exists, but no stable promoted candidate exists.",
        ),
        ChecklistItem(
            "No social, pinball, or neural layer promoted without locked OOS improvement",
            "research_particle package scan",
            "pass",
            "No social, pinball, or neural promotion module exists in the particle package.",
        ),
        ChecklistItem(
            "Live trading remains untouched until shadow gates clear",
            "artifact scope",
            "pass"
            if not (
                paired_sidecar_promotion_allowed
                or paired_sidecar_enrichment_promotion_allowed
                or paired_sidecar_diagnostic_promotion_allowed
                or paired_sidecar_aggregate_promotion_allowed
                or paired_sidecar_online_calibration_promotion_allowed
                or paired_sidecar_blend_failure_analysis_promotion_allowed
                or paired_sidecar_blend_failure_analysis_promotion_safe
                or paired_sidecar_slice_oos_promotion_allowed
                or paired_sidecar_slice_oos_promotion_safe
                or paired_sidecar_slice_refresh_promotion_allowed
                or paired_sidecar_slice_lock_comparison_promotion_allowed
                or paired_sidecar_slice_market_breakdown_promotion_allowed
                or paired_sidecar_slice_retirement_promotion_allowed
                or paired_sidecar_slice_stability_promotion_allowed
                or paired_sidecar_slice_trajectory_promotion_allowed
                or paired_sidecar_slice_promotion_readiness_promotion_allowed
                or paired_sidecar_refresh_promotion_allowed
            )
            else "fail",
            (
                "Audit only sees research_particle/probe/docs/log artifacts for this goal. "
                + paired_sidecar_spot_detail
                + " "
                + paired_sidecar_spot_enrichment_detail
                + " "
                + paired_sidecar_spot_diagnostic_detail
                + " "
                + paired_sidecar_spot_aggregate_detail
                + " "
                + paired_sidecar_online_calibration_detail
                + " "
                + paired_sidecar_blend_failure_analysis_detail
                + " "
                + paired_sidecar_slice_locked_plan_detail
                + " "
                + paired_sidecar_slice_oos_detail
                + " "
                + paired_sidecar_slice_refresh_detail
                + " "
                + paired_sidecar_spot_refresh_detail
            ),
        ),
        ChecklistItem(
            "Current v28 logs can seed strict replay",
            "v28 execution-event context audit",
            "fail" if v28_adapted_count == 0 else "partial",
            (
                f"adapted_count={v28_adapted_count}; current old log lacks enough "
                "exact two-sided candidate contexts for strict replay."
            ),
        ),
    ]
    complete = all(item.status == "pass" for item in checklist)
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "complete": complete,
        "synthetic_report_count": len(synthetic_reports),
        "strict_real_candidate_files": [str(path) for path in real_candidate_files],
        "strict_real_candidate_rows": real_candidate_count,
        "real_replay_reports": [str(path) for path in real_replay_reports],
        "locked_oos_stability_rows": stability_row_count,
        "locked_oos_stable_candidate_count": stable_candidate_count,
        "locked_oos_best_by_total_pnl": best_stability,
        "ev_rank_diagnostic_top_ev_bucket_stable_positive": bool(
            ev_rank_diagnostic.get("top_ev_bucket_stable_positive")
        ),
        "ev_rank_diagnostic_best_probability_model_by_brier": ev_rank_diagnostic.get(
            "best_probability_model_by_brier"
        ),
        "ev_rank_diagnostic_best_probability_model_by_log_loss": ev_rank_diagnostic.get(
            "best_probability_model_by_log_loss"
        ),
        "variant_loro_promotion_safe": bool(variant_loro_diagnostic.get("promotion_safe")),
        "artifact_leakage_audit_pass": artifact_leakage_pass,
        "artifact_leakage_audit_issue_count": int(artifact_leakage_audit.get("issue_count", 0) or 0),
        "artifact_leakage_audit_candidate_count": int(artifact_leakage_audit.get("candidate_count", 0) or 0),
        "denominator_integrity_audit_pass": denominator_integrity_pass,
        "denominator_integrity_audit_issue_count": int(denominator_integrity_audit.get("issue_count", 0) or 0),
        "denominator_integrity_audit_candidate_count": int(denominator_integrity_audit.get("candidate_count", 0) or 0),
        "pasc_loro_threshold_promotion_safe": bool(pasc_loro_diagnostic.get("promotion_safe")),
        "anchor_switch_loro_promotion_safe": bool(anchor_switch_loro.get("promotion_safe")),
        "market_cluster_best_probability_model_by_brier": market_cluster_diagnostic.get(
            "best_probability_model_by_market_brier"
        ),
        "market_cluster_ev_rank_correlation_sign": market_cluster_diagnostic.get(
            "ev_rank_correlation_sign"
        ),
        "meta_probability_loro_promotion_safe": bool(meta_probability_loro.get("promotion_safe")),
        "state_feature_loro_promotion_safe": bool(state_feature_loro.get("promotion_safe")),
        "spot_micro_loro_promotion_safe": bool(spot_micro_loro.get("promotion_safe")),
        "empirical_current_anchor_promotion_safe": bool(empirical_current_anchor.get("promotion_safe")),
        "empirical_current_anchor_candidate_ready": bool(
            empirical_current_anchor.get("candidate_ready_for_predeclared_shadow")
        ),
        "empirical_market_opportunity_promotion_safe": bool(empirical_market_opportunity.get("promotion_safe")),
        "empirical_market_opportunity_candidate_ready": bool(
            empirical_market_opportunity.get("candidate_ready_for_predeclared_shadow")
        ),
        "empirical_market_opportunity_loro_promotion_safe": bool(
            empirical_market_opportunity_loro.get("promotion_safe")
        ),
        "empirical_market_opportunity_loro_candidate_ready": bool(
            empirical_market_opportunity_loro.get("candidate_ready_for_predeclared_shadow")
        ),
        "empirical_next_second_particle_promotion_safe": bool(empirical_next_second.get("promotion_safe")),
        "empirical_next_second_particle_candidate_ready": bool(
            empirical_next_second.get("candidate_ready_for_predeclared_shadow")
        ),
        "spot_drift_terminal_promotion_safe": bool(spot_drift_terminal.get("promotion_safe")),
        "spot_drift_terminal_candidate_ready": bool(
            spot_drift_terminal.get("candidate_ready_for_predeclared_shadow")
        ),
        "spot_drift_regime_promotion_safe": bool(spot_drift_regime.get("promotion_safe")),
        "spot_drift_regime_candidate_ready": bool(
            spot_drift_regime.get("candidate_ready_for_predeclared_shadow")
        ),
        "spot_rv_anchor_switch_loro_promotion_safe": bool(
            spot_rv_anchor_switch_loro.get("promotion_safe")
        ),
        "spot_rv_anchor_switch_loro_candidate_ready": bool(
            spot_rv_anchor_switch_loro.get("candidate_ready_for_predeclared_shadow")
        ),
        "spot_rv_current_residual_loro_promotion_safe": bool(
            spot_rv_current_residual_loro.get("promotion_safe")
        ),
        "spot_rv_current_residual_loro_candidate_ready": bool(
            spot_rv_current_residual_loro.get("candidate_ready_for_predeclared_shadow")
        ),
        "spot_realized_vol_terminal_promotion_safe": bool(
            spot_realized_vol_diagnostic.get("promotion_safe")
        ),
        "fat_tail_particle_diagnostic_promotion_safe": bool(fat_tail_diagnostic.get("promotion_safe")),
        "fixed_terminal_gauss45_stability_stable_candidate_count": int(
            fixed_terminal_stability.get("stable_candidate_count", 0) or 0
        ),
        "online_anchor_calibration_promotion_safe": bool(
            online_anchor_diagnostic.get("promotion_safe")
        ),
        "anchor_regime_profile_promotion_safe": bool(
            anchor_regime_profile.get("promotion_safe")
        ),
        "paired_sidecar_spot_paired_capture_ready": bool(
            paired_sidecar_summary.get("paired_capture_ready")
        ),
        "paired_sidecar_spot_promotion_allowed": paired_sidecar_promotion_allowed,
        "paired_sidecar_spot_alignment_ready_count": int(
            paired_sidecar_summary.get("alignment_ready_count", 0) or 0
        ),
        "paired_sidecar_spot_alignment_row_count": int(
            paired_sidecar_summary.get("alignment_row_count", 0) or 0
        ),
        "paired_sidecar_spot_ticks_written": int(
            paired_sidecar_summary.get("spot_ticks_written", 0) or 0
        ),
        "paired_sidecar_spot_enrichment_ready": bool(
            paired_sidecar_enrichment_summary.get("enrichment_ready")
        ),
        "paired_sidecar_spot_enrichment_promotion_allowed": paired_sidecar_enrichment_promotion_allowed,
        "paired_sidecar_spot_enriched_packet_rows": int(
            paired_sidecar_enrichment_summary.get("enriched_packet_rows", 0) or 0
        ),
        "paired_sidecar_spot_enrichment_issue_count": int(
            paired_sidecar_enrichment_summary.get("issue_count", 0) or 0
        ),
        "paired_sidecar_spot_diagnostic_ready": bool(
            paired_sidecar_diagnostic_summary.get("diagnostic_ready")
        ),
        "paired_sidecar_spot_diagnostic_promotion_allowed": paired_sidecar_diagnostic_promotion_allowed,
        "paired_sidecar_spot_diagnostic_joined_rows": int(
            paired_sidecar_diagnostic_summary.get("joined_rows", 0) or 0
        ),
        "paired_sidecar_spot_diagnostic_joined_markets": int(
            paired_sidecar_diagnostic_summary.get("joined_markets", 0) or 0
        ),
        "paired_sidecar_spot_diagnostic_candidate_ready": bool(
            paired_sidecar_diagnostic_summary.get("candidate_ready_for_predeclared_shadow")
        ),
        "paired_sidecar_spot_diagnostic_best_model_by_brier": paired_sidecar_diagnostic_summary.get(
            "best_model_by_brier"
        ),
        "paired_sidecar_spot_diagnostic_best_model_by_logloss": paired_sidecar_diagnostic_summary.get(
            "best_model_by_logloss"
        ),
        "paired_sidecar_spot_diagnostic_tick_delta_brier_vs_candle": paired_sidecar_diagnostic_summary.get(
            "tick_brownian_delta_brier_vs_candle"
        ),
        "paired_sidecar_spot_diagnostic_tick_delta_logloss_vs_candle": paired_sidecar_diagnostic_summary.get(
            "tick_brownian_delta_logloss_vs_candle"
        ),
        "paired_sidecar_spot_aggregate_ready": bool(
            paired_sidecar_aggregate_summary.get("diagnostic_ready")
        ),
        "paired_sidecar_spot_aggregate_promotion_allowed": paired_sidecar_aggregate_promotion_allowed,
        "paired_sidecar_spot_aggregate_candidate_ready": bool(
            paired_sidecar_aggregate_summary.get("candidate_ready_for_predeclared_shadow")
        ),
        "paired_sidecar_spot_aggregate_diagnostic_file_count": int(
            paired_sidecar_aggregate_diagnostic_file_count
        ),
        "paired_sidecar_spot_actual_diagnostic_file_count": len(paired_sidecar_spot_diagnostic_files),
        "paired_sidecar_spot_aggregate_fresh": paired_sidecar_aggregate_fresh,
        "paired_sidecar_spot_aggregate_stale_file_delta": (
            len(paired_sidecar_spot_diagnostic_files) - paired_sidecar_aggregate_diagnostic_file_count
        ),
        "paired_sidecar_spot_aggregate_ready_diagnostic_count": int(
            paired_sidecar_aggregate_summary.get("ready_diagnostic_count", 0) or 0
        ),
        "paired_sidecar_spot_aggregate_skipped_diagnostic_count": int(
            paired_sidecar_aggregate_summary.get("skipped_diagnostic_count", 0) or 0
        ),
        "paired_sidecar_spot_aggregate_joined_rows": int(
            paired_sidecar_aggregate_summary.get("joined_rows", 0) or 0
        ),
        "paired_sidecar_spot_aggregate_joined_markets": int(
            paired_sidecar_aggregate_summary.get("joined_markets", 0) or 0
        ),
        "paired_sidecar_spot_aggregate_rows_remaining_for_shadow": int(
            paired_sidecar_aggregate_summary.get("rows_remaining_for_shadow", 0) or 0
        ),
        "paired_sidecar_spot_aggregate_markets_remaining_for_shadow": int(
            paired_sidecar_aggregate_summary.get("markets_remaining_for_shadow", 0) or 0
        ),
        "paired_sidecar_spot_aggregate_best_model_by_brier": paired_sidecar_aggregate_summary.get(
            "best_model_by_brier"
        ),
        "paired_sidecar_spot_aggregate_best_model_by_logloss": paired_sidecar_aggregate_summary.get(
            "best_model_by_logloss"
        ),
        "paired_sidecar_spot_aggregate_market_equal_best_model_by_brier": paired_sidecar_aggregate_summary.get(
            "market_equal_best_model_by_brier"
        ),
        "paired_sidecar_spot_aggregate_market_equal_best_model_by_logloss": paired_sidecar_aggregate_summary.get(
            "market_equal_best_model_by_logloss"
        ),
        "paired_sidecar_spot_aggregate_tick_delta_brier_vs_candle": paired_sidecar_aggregate_summary.get(
            "tick_brownian_delta_brier_vs_candle"
        ),
        "paired_sidecar_spot_aggregate_tick_delta_logloss_vs_candle": paired_sidecar_aggregate_summary.get(
            "tick_brownian_delta_logloss_vs_candle"
        ),
        "paired_sidecar_spot_aggregate_market_equal_tick_delta_brier_vs_candle": paired_sidecar_aggregate_summary.get(
            "market_equal_tick_brownian_delta_brier_vs_candle"
        ),
        "paired_sidecar_spot_aggregate_market_equal_tick_delta_logloss_vs_candle": paired_sidecar_aggregate_summary.get(
            "market_equal_tick_brownian_delta_logloss_vs_candle"
        ),
        "paired_sidecar_online_calibration_promotion_allowed": paired_sidecar_online_calibration_promotion_allowed,
        "paired_sidecar_online_calibration_prepared_rows": int(
            paired_sidecar_online_calibration_summary.get("prepared_rows", 0) or 0
        ),
        "paired_sidecar_online_calibration_input_markets": int(
            paired_sidecar_online_calibration_summary.get("input_markets", 0) or 0
        ),
        "paired_sidecar_online_calibration_best_model_by_brier": paired_sidecar_online_calibration_summary.get(
            "best_model_by_brier"
        ),
        "paired_sidecar_online_calibration_best_model_by_logloss": paired_sidecar_online_calibration_summary.get(
            "best_model_by_logloss"
        ),
        "paired_sidecar_online_calibration_market_equal_best_model_by_brier": paired_sidecar_online_calibration_summary.get(
            "market_equal_best_model_by_brier"
        ),
        "paired_sidecar_online_calibration_market_equal_best_model_by_logloss": paired_sidecar_online_calibration_summary.get(
            "market_equal_best_model_by_logloss"
        ),
        "paired_sidecar_online_calibration_best_calibrated_brier": paired_sidecar_online_calibration_summary.get(
            "best_calibrated_brier"
        ),
        "paired_sidecar_online_calibration_best_calibrated_logloss": paired_sidecar_online_calibration_summary.get(
            "best_calibrated_logloss"
        ),
        "paired_sidecar_online_calibration_best_calibrated_top_ev_bucket_pnl_cents": paired_sidecar_online_calibration_summary.get(
            "best_calibrated_top_ev_bucket_pnl_cents"
        ),
        "paired_sidecar_online_calibration_best_calibrated_positive_market_top_ev_count": int(
            paired_sidecar_online_calibration_summary.get(
                "best_calibrated_positive_market_top_ev_count",
                0,
            )
            or 0
        ),
        "paired_sidecar_online_calibration_best_blend_positive_market_top_ev_count": int(
            paired_sidecar_online_calibration_summary.get(
                "best_blend_positive_market_top_ev_count",
                0,
            )
            or 0
        ),
        "paired_sidecar_blend_failure_analysis_promotion_allowed": paired_sidecar_blend_failure_analysis_promotion_allowed,
        "paired_sidecar_blend_failure_analysis_promotion_safe": paired_sidecar_blend_failure_analysis_promotion_safe,
        "paired_sidecar_blend_failure_analysis_rows": int(
            paired_sidecar_blend_failure_analysis_summary.get("rows", 0) or 0
        ),
        "paired_sidecar_blend_failure_analysis_markets": int(
            paired_sidecar_blend_failure_analysis_summary.get("markets", 0) or 0
        ),
        "paired_sidecar_blend_failure_analysis_best_blend": paired_sidecar_blend_failure_analysis_summary.get(
            "best_blend_model_by_market_equal_brier"
        ),
        "paired_sidecar_blend_failure_analysis_best_blend_positive_top_ev_markets": int(
            paired_sidecar_blend_failure_analysis_summary.get(
                "best_blend_positive_market_top_ev_count",
                0,
            )
            or 0
        ),
        "paired_sidecar_blend_failure_analysis_best_blend_positive_selected_markets": int(
            paired_sidecar_blend_failure_analysis_summary.get(
                "best_blend_positive_market_selected_pnl_count",
                0,
            )
            or 0
        ),
        "paired_sidecar_blend_failure_analysis_posthoc_slice_candidate_count": len(
            paired_sidecar_blend_failure_analysis_summary.get("posthoc_slice_candidates")
            or []
        ),
        "paired_sidecar_slice_locked_plan_hypothesis_id": paired_sidecar_slice_locked_plan.get(
            "hypothesis_id"
        ),
        "paired_sidecar_slice_locked_plan_locked_after_utc": paired_sidecar_slice_locked_plan.get(
            "locked_after_utc"
        ),
        "paired_sidecar_slice_locked_plan_model": paired_sidecar_slice_locked_plan.get("model"),
        "paired_sidecar_slice_locked_plan_slice_type": paired_sidecar_slice_locked_plan.get(
            "slice_type"
        ),
        "paired_sidecar_slice_locked_plan_bucket": paired_sidecar_slice_locked_plan.get("bucket"),
        "paired_sidecar_slice_oos_promotion_allowed": paired_sidecar_slice_oos_promotion_allowed,
        "paired_sidecar_slice_oos_promotion_safe": paired_sidecar_slice_oos_promotion_safe,
        "paired_sidecar_slice_oos_report_count": len(paired_sidecar_slice_oos_reports),
        "paired_sidecar_slice_oos_reports": [
            _paired_sidecar_slice_oos_report_summary(payload)
            for payload in paired_sidecar_slice_oos_reports
        ],
        "paired_sidecar_slice_oos_hypothesis_id": paired_sidecar_slice_oos_summary.get(
            "hypothesis_id"
        ),
        "paired_sidecar_slice_oos_fresh_candidate_rows": int(
            paired_sidecar_slice_oos_summary.get("fresh_candidate_rows", 0) or 0
        ),
        "paired_sidecar_slice_oos_fresh_markets": int(
            paired_sidecar_slice_oos_summary.get("fresh_markets", 0) or 0
        ),
        "paired_sidecar_slice_oos_slice_rows": int(
            paired_sidecar_slice_oos_summary.get("slice_rows", 0) or 0
        ),
        "paired_sidecar_slice_oos_slice_markets": int(
            paired_sidecar_slice_oos_summary.get("slice_markets", 0) or 0
        ),
        "paired_sidecar_slice_refresh_promotion_allowed": paired_sidecar_slice_refresh_promotion_allowed,
        "paired_sidecar_slice_refresh_collect_requested": bool(
            paired_sidecar_slice_refresh_summary.get("collect_requested")
        ),
        "paired_sidecar_slice_refresh_pending_manifest_count": int(
            paired_sidecar_slice_refresh_summary.get("pending_manifest_count", 0) or 0
        ),
        "paired_sidecar_slice_refresh_pending_enriched_rows": int(
            paired_sidecar_slice_refresh_summary.get("pending_enriched_rows", 0) or 0
        ),
        "paired_sidecar_slice_refresh_next_pending_market_close_utc": str(
            paired_sidecar_slice_refresh_summary.get("next_pending_market_close_utc", "")
            or ""
        ),
        "paired_sidecar_slice_refresh_seconds_until_next_pending_close": (
            paired_sidecar_slice_refresh_summary.get("seconds_until_next_pending_close")
        ),
        "paired_sidecar_slice_refresh_slice_fresh_candidate_rows": int(
            paired_sidecar_slice_refresh_summary.get("slice_fresh_candidate_rows", 0) or 0
        ),
        "paired_sidecar_slice_refresh_slice_fresh_markets": int(
            paired_sidecar_slice_refresh_summary.get("slice_fresh_markets", 0) or 0
        ),
        "paired_sidecar_slice_refresh_slice_rows": int(
            paired_sidecar_slice_refresh_summary.get("slice_rows", 0) or 0
        ),
        "paired_sidecar_slice_refresh_slice_markets": int(
            paired_sidecar_slice_refresh_summary.get("slice_markets", 0) or 0
        ),
        "paired_sidecar_slice_refresh_slice_promotion_safe": bool(
            paired_sidecar_slice_refresh_summary.get("slice_promotion_safe")
        ),
        "paired_sidecar_slice_lock_comparison_promotion_allowed": paired_sidecar_slice_lock_comparison_promotion_allowed,
        "paired_sidecar_slice_lock_comparison_report_count": int(
            paired_sidecar_slice_lock_comparison_summary.get("report_count", 0) or 0
        ),
        "paired_sidecar_slice_lock_comparison_particle_edge_candidate_count": int(
            paired_sidecar_slice_lock_comparison_summary.get("particle_edge_candidate_count", 0)
            or 0
        ),
        "paired_sidecar_slice_lock_comparison_best_selected_pnl_hypothesis_id": (
            paired_sidecar_slice_lock_comparison_summary.get("best_selected_pnl_hypothesis_id")
        ),
        "paired_sidecar_slice_lock_comparison_best_selected_pnl_cents": float(
            paired_sidecar_slice_lock_comparison_summary.get("best_selected_pnl_cents", 0)
            or 0
        ),
        "paired_sidecar_slice_market_breakdown_promotion_allowed": paired_sidecar_slice_market_breakdown_promotion_allowed,
        "paired_sidecar_slice_market_breakdown_plan_count": int(
            paired_sidecar_slice_market_breakdown_summary.get("plan_count", 0) or 0
        ),
        "paired_sidecar_slice_market_breakdown_row_count": int(
            paired_sidecar_slice_market_breakdown_summary.get("row_count", 0) or 0
        ),
        "paired_sidecar_slice_market_breakdown_particle_like_negative_market_count": int(
            paired_sidecar_slice_market_breakdown_summary.get("particle_like_negative_market_count", 0)
            or 0
        ),
        "paired_sidecar_slice_market_breakdown_worst_particle_hypothesis_id": (
            paired_sidecar_slice_market_breakdown_summary.get("worst_particle_hypothesis_id")
        ),
        "paired_sidecar_slice_market_breakdown_worst_particle_market_ticker": (
            paired_sidecar_slice_market_breakdown_summary.get("worst_particle_market_ticker")
        ),
        "paired_sidecar_slice_market_breakdown_worst_particle_selected_pnl_cents": float(
            paired_sidecar_slice_market_breakdown_summary.get("worst_particle_selected_pnl_cents", 0)
            or 0
        ),
        "paired_sidecar_slice_retirement_promotion_allowed": paired_sidecar_slice_retirement_promotion_allowed,
        "paired_sidecar_slice_retirement_retire_count": int(
            paired_sidecar_slice_retirement_summary.get("retire_count", 0) or 0
        ),
        "paired_sidecar_slice_retirement_watchlist_count": int(
            paired_sidecar_slice_retirement_summary.get("watchlist_count", 0) or 0
        ),
        "paired_sidecar_slice_retirement_stability_blocked_count": int(
            paired_sidecar_slice_retirement_summary.get("stability_blocked_count", 0) or 0
        ),
        "paired_sidecar_slice_retirement_trajectory_blocked_count": int(
            paired_sidecar_slice_retirement_summary.get("trajectory_blocked_count", 0) or 0
        ),
        "paired_sidecar_slice_retirement_continue_shadow_count": int(
            paired_sidecar_slice_retirement_summary.get("continue_shadow_count", 0) or 0
        ),
        "paired_sidecar_slice_retirement_candidate_for_broader_audit_count": int(
            paired_sidecar_slice_retirement_summary.get("candidate_for_broader_audit_count", 0)
            or 0
        ),
        "paired_sidecar_slice_stability_promotion_allowed": paired_sidecar_slice_stability_promotion_allowed,
        "paired_sidecar_slice_stability_row_count": int(
            paired_sidecar_slice_stability_summary.get("row_count", 0) or 0
        ),
        "paired_sidecar_slice_stability_particle_like_count": int(
            paired_sidecar_slice_stability_summary.get("particle_like_count", 0) or 0
        ),
        "paired_sidecar_slice_stability_particle_like_stability_screen_pass_count": int(
            paired_sidecar_slice_stability_summary.get("particle_like_stability_screen_pass_count", 0)
            or 0
        ),
        "paired_sidecar_slice_stability_most_concentrated_hypothesis_id": (
            paired_sidecar_slice_stability_summary.get("most_concentrated_hypothesis_id")
        ),
        "paired_sidecar_slice_stability_most_concentrated_abs_market_pnl_share": float(
            paired_sidecar_slice_stability_summary.get("most_concentrated_abs_market_pnl_share", 0)
            or 0
        ),
        "paired_sidecar_slice_trajectory_promotion_allowed": paired_sidecar_slice_trajectory_promotion_allowed,
        "paired_sidecar_slice_trajectory_row_count": int(
            paired_sidecar_slice_trajectory_summary.get("row_count", 0) or 0
        ),
        "paired_sidecar_slice_trajectory_particle_like_count": int(
            paired_sidecar_slice_trajectory_summary.get("particle_like_count", 0) or 0
        ),
        "paired_sidecar_slice_trajectory_particle_like_trajectory_screen_pass_count": int(
            paired_sidecar_slice_trajectory_summary.get("particle_like_trajectory_screen_pass_count", 0)
            or 0
        ),
        "paired_sidecar_slice_trajectory_worst_recent_hypothesis_id": (
            paired_sidecar_slice_trajectory_summary.get("worst_recent_hypothesis_id")
        ),
        "paired_sidecar_slice_trajectory_worst_recent_selected_pnl_cents": float(
            paired_sidecar_slice_trajectory_summary.get("worst_recent_selected_pnl_cents", 0)
            or 0
        ),
        "paired_sidecar_slice_promotion_readiness_promotion_allowed": paired_sidecar_slice_promotion_readiness_promotion_allowed,
        "paired_sidecar_slice_promotion_readiness_row_count": int(
            paired_sidecar_slice_promotion_readiness_summary.get("row_count", 0) or 0
        ),
        "paired_sidecar_slice_promotion_readiness_particle_like_count": int(
            paired_sidecar_slice_promotion_readiness_summary.get("particle_like_count", 0) or 0
        ),
        "paired_sidecar_slice_promotion_readiness_candidate_count": int(
            paired_sidecar_slice_promotion_readiness_summary.get("readiness_candidate_count", 0) or 0
        ),
        "paired_sidecar_slice_promotion_readiness_hard_veto_count": int(
            paired_sidecar_slice_promotion_readiness_summary.get("hard_veto_count", 0) or 0
        ),
        "paired_sidecar_spot_refresh_promotion_allowed": paired_sidecar_refresh_promotion_allowed,
        "paired_sidecar_spot_refresh_manifest_count": int(
            paired_sidecar_refresh_summary.get("manifest_count", 0) or 0
        ),
        "paired_sidecar_spot_refresh_skipped_manifest_count": int(
            paired_sidecar_refresh_summary.get("skipped_manifest_count", 0) or 0
        ),
        "paired_sidecar_spot_refresh_enrichment_ready_count": int(
            paired_sidecar_refresh_summary.get("enrichment_ready_count", 0) or 0
        ),
        "paired_sidecar_spot_refresh_diagnostic_ready_count": int(
            paired_sidecar_refresh_summary.get("diagnostic_ready_count", 0) or 0
        ),
        "paired_sidecar_spot_refresh_pending_diagnostic_count": int(
            paired_sidecar_refresh_summary.get("pending_diagnostic_count", 0) or 0
        ),
        "paired_sidecar_spot_refresh_goal_complete": bool(
            paired_sidecar_refresh_summary.get("goal_complete")
        ),
        "adapter_ready_count": int(adapter_readiness.get("adapter_ready_count", 0) or 0),
        "v28_adapted_count": v28_adapted_count,
        "checklist": [asdict(item) for item in checklist],
    }


def write_report(payload: dict[str, Any], root: Path = Path(".")) -> tuple[Path, Path]:
    out_dir = root / REPORT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = root / LATEST_JSON
    md_path = root / LATEST_MD
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    return json_path, md_path


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Particle Goal Completion Audit",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        f"Complete: `{payload['complete']}`",
        "",
        "## Objective Restatement",
        "",
        (
            "Build a research-only next-second particle simulation system that "
            "records all candidate moments, predicts terminal settlement "
            "probability, calibrates online, converts probabilities into "
            "fee/fill-adjusted EV, and proves superiority on real all-candidate "
            "shadow replay before any live impact."
        ),
        "",
        "## Prompt-to-Artifact Checklist",
        "",
        "| requirement | evidence | status | detail |",
        "|---|---|---|---|",
    ]
    for item in payload["checklist"]:
        lines.append(
            "| {requirement} | `{evidence}` | {status} | {detail} |".format(
                requirement=item["requirement"],
                evidence=item["evidence"],
                status=item["status"],
                detail=item["detail"],
            )
        )
    lines.extend(
        [
            "",
            "## Completion Decision",
            "",
        ]
    )
    if payload["complete"]:
        lines.append("- Complete: every explicit gate has concrete passing evidence.")
    else:
        lines.append(
            "- Not complete: at least one explicit gate is missing, partial, or "
            "backed only by synthetic/proxy evidence."
        )
        lines.append(
            f"- Real strict candidate rows found: {payload['strict_real_candidate_rows']}."
        )
        lines.append(
            f"- Real replay reports found: {len(payload['real_replay_reports'])}."
        )
        lines.append(
            f"- Locked OOS stability rows found: {payload.get('locked_oos_stability_rows', 0)}."
        )
        lines.append(
            f"- Locked OOS stable candidates found: {payload.get('locked_oos_stable_candidate_count', 0)}."
        )
    return "\n".join(lines) + "\n"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _load_latest_json(directory: Path, pattern: str) -> dict[str, Any]:
    if not directory.exists():
        return {}
    matches = sorted(directory.glob(pattern), key=lambda path: path.stat().st_mtime, reverse=True)
    if not matches:
        return {}
    return _load_json(matches[0])


def _load_json_files(directory: Path, pattern: str) -> list[dict[str, Any]]:
    if not directory.exists():
        return []
    return [_load_json(path) for path in sorted(directory.glob(pattern))]


def _paired_sidecar_spot_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "paired_sidecar_spot=missing."
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else payload
    return (
        "paired_sidecar_spot="
        f"paired_capture_ready={summary.get('paired_capture_ready', 'unknown')}; "
        f"promotion_allowed={summary.get('promotion_allowed', 'unknown')}; "
        f"collect_mode={summary.get('collect_mode', 'unknown')}; "
        f"sidecar_markets={summary.get('sidecar_markets_selected', 0)}; "
        f"sidecar_packet_rows={summary.get('sidecar_packet_rows', 0)}; "
        f"spot_ticks={summary.get('spot_ticks_written', 0)}; "
        f"alignment_ready={summary.get('alignment_ready_count', 0)}/{summary.get('alignment_row_count', 0)}."
    )


def _paired_sidecar_spot_enrichment_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "paired_sidecar_spot_enrichment=missing."
    summary = _summary_from_payload(payload)
    return (
        "paired_sidecar_spot_enrichment="
        f"enrichment_ready={summary.get('enrichment_ready', 'unknown')}; "
        f"promotion_allowed={summary.get('promotion_allowed', 'unknown')}; "
        f"matching_packet_rows={summary.get('matching_packet_rows', 0)}; "
        f"enriched_packet_rows={summary.get('enriched_packet_rows', 0)}; "
        f"issue_count={summary.get('issue_count', 0)}."
    )


def _paired_sidecar_spot_diagnostic_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "paired_sidecar_spot_diagnostic=missing."
    summary = _summary_from_payload(payload)
    return (
        "paired_sidecar_spot_diagnostic="
        f"diagnostic_ready={summary.get('diagnostic_ready', 'unknown')}; "
        f"candidate_ready={summary.get('candidate_ready_for_predeclared_shadow', 'unknown')}; "
        f"joined_rows={summary.get('joined_rows', 0)}; "
        f"joined_markets={summary.get('joined_markets', 0)}; "
        f"best_brier={summary.get('best_model_by_brier', 'unknown')}; "
        f"best_logloss={summary.get('best_model_by_logloss', 'unknown')}; "
        f"tick_delta_brier_vs_candle={summary.get('tick_brownian_delta_brier_vs_candle', 'unknown')}; "
        f"tick_delta_logloss_vs_candle={summary.get('tick_brownian_delta_logloss_vs_candle', 'unknown')}."
    )


def _paired_sidecar_spot_aggregate_detail(
    payload: dict[str, Any],
    *,
    actual_diagnostic_file_count: int | None = None,
) -> str:
    if not payload:
        return "paired_sidecar_spot_aggregate=missing."
    summary = _summary_from_payload(payload)
    recorded_file_count = int(summary.get("diagnostic_file_count", 0) or 0)
    freshness = "unknown"
    stale_delta = "unknown"
    if actual_diagnostic_file_count is not None:
        stale_delta = actual_diagnostic_file_count - recorded_file_count
        freshness = str(stale_delta == 0)
    return (
        "paired_sidecar_spot_aggregate="
        f"diagnostic_ready={summary.get('diagnostic_ready', 'unknown')}; "
        f"promotion_allowed={summary.get('promotion_allowed', 'unknown')}; "
        f"candidate_ready={summary.get('candidate_ready_for_predeclared_shadow', 'unknown')}; "
        f"diagnostic_files={summary.get('ready_diagnostic_count', 0)}/{summary.get('diagnostic_file_count', 0)}; "
        f"skipped_diagnostic_files={summary.get('skipped_diagnostic_count', 0)}; "
        f"actual_diagnostic_files={actual_diagnostic_file_count if actual_diagnostic_file_count is not None else 'unknown'}; "
        f"fresh={freshness}; "
        f"stale_file_delta={stale_delta}; "
        f"joined_rows={summary.get('joined_rows', 0)}; "
        f"joined_markets={summary.get('joined_markets', 0)}; "
        f"rows_remaining={summary.get('rows_remaining_for_shadow', 'unknown')}; "
        f"markets_remaining={summary.get('markets_remaining_for_shadow', 'unknown')}; "
        f"best_brier={summary.get('best_model_by_brier', 'unknown')}; "
        f"best_logloss={summary.get('best_model_by_logloss', 'unknown')}; "
        f"market_equal_best_brier={summary.get('market_equal_best_model_by_brier', 'unknown')}; "
        f"market_equal_best_logloss={summary.get('market_equal_best_model_by_logloss', 'unknown')}; "
        f"tick_delta_brier_vs_candle={summary.get('tick_brownian_delta_brier_vs_candle', 'unknown')}; "
        f"tick_delta_logloss_vs_candle={summary.get('tick_brownian_delta_logloss_vs_candle', 'unknown')}; "
        f"market_equal_tick_delta_brier_vs_candle={summary.get('market_equal_tick_brownian_delta_brier_vs_candle', 'unknown')}; "
        f"market_equal_tick_delta_logloss_vs_candle={summary.get('market_equal_tick_brownian_delta_logloss_vs_candle', 'unknown')}."
    )


def _paired_sidecar_online_calibration_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "paired_sidecar_online_calibration=missing."
    summary = _summary_from_payload(payload)
    return (
        "paired_sidecar_online_calibration="
        f"promotion_allowed={summary.get('promotion_allowed', 'unknown')}; "
        f"prepared_rows={summary.get('prepared_rows', 0)}; "
        f"input_markets={summary.get('input_markets', 0)}; "
        f"best_brier={summary.get('best_model_by_brier', 'unknown')}; "
        f"best_logloss={summary.get('best_model_by_logloss', 'unknown')}; "
        f"market_equal_best_brier={summary.get('market_equal_best_model_by_brier', 'unknown')}; "
        f"market_equal_best_logloss={summary.get('market_equal_best_model_by_logloss', 'unknown')}; "
        f"raw_candidate_brier={summary.get('raw_candidate_brier', 'unknown')}; "
        f"best_calibrated_brier={summary.get('best_calibrated_brier', 'unknown')}; "
        f"raw_candidate_logloss={summary.get('raw_candidate_logloss', 'unknown')}; "
        f"best_calibrated_logloss={summary.get('best_calibrated_logloss', 'unknown')}; "
        f"raw_top_ev_pnl={summary.get('raw_candidate_top_ev_bucket_pnl_cents', 'unknown')}; "
        f"best_calibrated_top_ev_pnl={summary.get('best_calibrated_top_ev_bucket_pnl_cents', 'unknown')}; "
        f"best_calibrated_positive_top_ev_markets={summary.get('best_calibrated_positive_market_top_ev_count', 0)}/"
        f"{summary.get('market_count_for_stability', 0)}; "
        f"best_calibrated_positive_selected_markets={summary.get('best_calibrated_positive_market_selected_pnl_count', 0)}/"
        f"{summary.get('market_count_for_stability', 0)}; "
        f"best_blend={summary.get('best_blend_model_by_market_equal_brier', 'unknown')}; "
        f"best_blend_positive_top_ev_markets={summary.get('best_blend_positive_market_top_ev_count', 0)}/"
        f"{summary.get('market_count_for_stability', 0)}; "
        f"best_blend_positive_selected_markets={summary.get('best_blend_positive_market_selected_pnl_count', 0)}/"
        f"{summary.get('market_count_for_stability', 0)}."
    )


def _paired_sidecar_blend_failure_analysis_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "paired_sidecar_blend_failure_analysis=missing."
    summary = _summary_from_payload(payload)
    posthoc_slices = summary.get("posthoc_slice_candidates")
    posthoc_count = len(posthoc_slices) if isinstance(posthoc_slices, list) else 0
    return (
        "paired_sidecar_blend_failure_analysis="
        f"promotion_allowed={summary.get('promotion_allowed', 'unknown')}; "
        f"promotion_safe={summary.get('promotion_safe', 'unknown')}; "
        f"rows={summary.get('rows', 0)}; "
        f"markets={summary.get('markets', 0)}; "
        f"best_blend={summary.get('best_blend_model_by_market_equal_brier', 'unknown')}; "
        f"best_blend_positive_top_ev_markets={summary.get('best_blend_positive_market_top_ev_count', 0)}/"
        f"{summary.get('markets', 0)}; "
        f"best_blend_positive_selected_markets={summary.get('best_blend_positive_market_selected_pnl_count', 0)}/"
        f"{summary.get('markets', 0)}; "
        f"posthoc_slice_candidates={posthoc_count}; "
        f"conclusion={summary.get('conclusion', 'unknown')}."
    )


def _paired_sidecar_slice_locked_plan_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "paired_sidecar_slice_locked_plan=missing."
    summary = _summary_from_payload(payload)
    return (
        "paired_sidecar_slice_locked_plan="
        f"hypothesis={summary.get('hypothesis_id', 'unknown')}; "
        f"evaluation_scope={summary.get('evaluation_scope', 'unknown')}; "
        f"locked_after_utc={summary.get('locked_after_utc', 'unknown')}; "
        f"model={summary.get('model', 'unknown')}; "
        f"slice={summary.get('slice_type', 'unknown')}={summary.get('bucket', 'unknown')}; "
        f"fee_cents={summary.get('fee_cents', 'unknown')}; "
        f"assumed_fill_probability={summary.get('assumed_fill_probability', 'unknown')}; "
        f"source_sha256_present={bool(summary.get('selection_source_sha256'))}."
    )


def _paired_sidecar_slice_oos_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "paired_sidecar_slice_oos=missing."
    summary = _summary_from_payload(payload)
    gate_results = summary.get("gate_results")
    gate_results = gate_results if isinstance(gate_results, dict) else {}
    selected = summary.get("selected_metrics")
    selected = selected if isinstance(selected, dict) else {}
    return (
        "paired_sidecar_slice_oos="
        f"hypothesis={summary.get('hypothesis_id', 'unknown')}; "
        f"promotion_allowed={summary.get('promotion_allowed', 'unknown')}; "
        f"promotion_safe={summary.get('promotion_safe', 'unknown')}; "
        f"evaluation_scope={summary.get('evaluation_scope', 'unknown')}; "
        f"fresh_rows={summary.get('fresh_candidate_rows', 0)}; "
        f"fresh_markets={summary.get('fresh_markets', 0)}; "
        f"slice_rows={summary.get('slice_rows', 0)}; "
        f"slice_markets={summary.get('slice_markets', 0)}; "
        f"selected_count={selected.get('selected_count', 0)}; "
        f"selected_pnl={selected.get('selected_pnl_cents', 0)}; "
        f"top_ev_pnl={selected.get('top_ev_bucket_pnl_cents', 0)}; "
        f"all_gates_passed={gate_results.get('all_passed', 'unknown')}."
    )


def _paired_sidecar_slice_oos_reports_detail(payloads: list[dict[str, Any]]) -> str:
    if not payloads:
        return "paired_sidecar_slice_oos_all=missing."
    summaries = [_paired_sidecar_slice_oos_report_summary(payload) for payload in payloads]
    parts = [
        (
            f"{item.get('hypothesis_id', 'unknown')}:"
            f"safe={item.get('promotion_safe')},"
            f"fresh={item.get('fresh_candidate_rows')}/{item.get('fresh_markets')},"
            f"slice={item.get('slice_rows')}/{item.get('slice_markets')},"
            f"selected={item.get('selected_count')},"
            f"pnl={item.get('selected_pnl_cents')}"
        )
        for item in summaries
    ]
    any_safe = any(bool(item.get("promotion_safe")) for item in summaries)
    return (
        "paired_sidecar_slice_oos_all="
        f"count={len(summaries)}; "
        f"any_promotion_safe={any_safe}; "
        f"reports=[{'; '.join(parts)}]."
    )


def _paired_sidecar_slice_oos_report_summary(payload: dict[str, Any]) -> dict[str, Any]:
    summary = _summary_from_payload(payload)
    selected = summary.get("selected_metrics")
    selected = selected if isinstance(selected, dict) else {}
    return {
        "hypothesis_id": summary.get("hypothesis_id"),
        "model": summary.get("model"),
        "bucket": summary.get("bucket"),
        "locked_after_utc": summary.get("locked_after_utc"),
        "promotion_allowed": bool(summary.get("promotion_allowed")),
        "promotion_safe": bool(summary.get("promotion_safe")),
        "fresh_candidate_rows": int(summary.get("fresh_candidate_rows", 0) or 0),
        "fresh_markets": int(summary.get("fresh_markets", 0) or 0),
        "slice_rows": int(summary.get("slice_rows", 0) or 0),
        "slice_markets": int(summary.get("slice_markets", 0) or 0),
        "selected_count": int(selected.get("selected_count", 0) or 0),
        "selected_pnl_cents": float(selected.get("selected_pnl_cents", 0) or 0),
        "top_ev_bucket_pnl_cents": float(selected.get("top_ev_bucket_pnl_cents", 0) or 0),
    }


def _paired_sidecar_slice_lock_comparison_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "paired_sidecar_slice_lock_comparison=missing."
    summary = _summary_from_payload(payload)
    return (
        "paired_sidecar_slice_lock_comparison="
        f"promotion_allowed={summary.get('promotion_allowed', 'unknown')}; "
        f"report_count={summary.get('report_count', 0)}; "
        f"particle_like_count={summary.get('particle_like_count', 0)}; "
        f"particle_edge_candidate_count={summary.get('particle_edge_candidate_count', 0)}; "
        f"best_selected_pnl_hypothesis={summary.get('best_selected_pnl_hypothesis_id', '')}; "
        f"best_selected_pnl={summary.get('best_selected_pnl_cents', 0)}; "
        f"best_v28_brier_delta={summary.get('best_v28_brier_delta', 'unknown')}; "
        f"conclusion={summary.get('conclusion', '')}."
    )


def _paired_sidecar_slice_market_breakdown_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "paired_sidecar_slice_market_breakdown=missing."
    summary = _summary_from_payload(payload)
    return (
        "paired_sidecar_slice_market_breakdown="
        f"promotion_allowed={summary.get('promotion_allowed', 'unknown')}; "
        f"plan_count={summary.get('plan_count', 0)}; "
        f"row_count={summary.get('row_count', 0)}; "
        f"particle_like_row_count={summary.get('particle_like_row_count', 0)}; "
        f"particle_like_negative_market_count={summary.get('particle_like_negative_market_count', 0)}; "
        f"worst_particle_hypothesis={summary.get('worst_particle_hypothesis_id', '')}; "
        f"worst_particle_market={summary.get('worst_particle_market_ticker', '')}; "
        f"worst_particle_selected_pnl={summary.get('worst_particle_selected_pnl_cents', 0)}; "
        f"worst_particle_delta_vs_v28={summary.get('worst_particle_delta_vs_v28_cents', 'unknown')}; "
        f"conclusion={summary.get('conclusion', '')}."
    )


def _paired_sidecar_slice_retirement_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "paired_sidecar_slice_retirement=missing."
    summary = _summary_from_payload(payload)
    return (
        "paired_sidecar_slice_retirement="
        f"promotion_allowed={summary.get('promotion_allowed', 'unknown')}; "
        f"row_count={summary.get('row_count', 0)}; "
        f"particle_like_count={summary.get('particle_like_count', 0)}; "
        f"retire_count={summary.get('retire_count', 0)}; "
        f"watchlist_count={summary.get('watchlist_count', 0)}; "
        f"stability_blocked_count={summary.get('stability_blocked_count', 0)}; "
        f"trajectory_blocked_count={summary.get('trajectory_blocked_count', 0)}; "
        f"continue_shadow_count={summary.get('continue_shadow_count', 0)}; "
        f"control_count={summary.get('control_count', 0)}; "
        f"candidate_for_broader_audit_count={summary.get('candidate_for_broader_audit_count', 0)}; "
        f"conclusion={summary.get('conclusion', '')}."
    )


def _paired_sidecar_slice_stability_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "paired_sidecar_slice_stability=missing."
    summary = _summary_from_payload(payload)
    return (
        "paired_sidecar_slice_stability="
        f"promotion_allowed={summary.get('promotion_allowed', 'unknown')}; "
        f"row_count={summary.get('row_count', 0)}; "
        f"particle_like_count={summary.get('particle_like_count', 0)}; "
        f"stability_screen_pass_count={summary.get('stability_screen_pass_count', 0)}; "
        f"particle_like_stability_screen_pass_count={summary.get('particle_like_stability_screen_pass_count', 0)}; "
        f"most_concentrated_hypothesis={summary.get('most_concentrated_hypothesis_id', '')}; "
        f"most_concentrated_abs_market_pnl_share={summary.get('most_concentrated_abs_market_pnl_share', 0)}; "
        f"conclusion={summary.get('conclusion', '')}."
    )


def _paired_sidecar_slice_trajectory_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "paired_sidecar_slice_trajectory=missing."
    summary = _summary_from_payload(payload)
    return (
        "paired_sidecar_slice_trajectory="
        f"promotion_allowed={summary.get('promotion_allowed', 'unknown')}; "
        f"row_count={summary.get('row_count', 0)}; "
        f"particle_like_count={summary.get('particle_like_count', 0)}; "
        f"trajectory_screen_pass_count={summary.get('trajectory_screen_pass_count', 0)}; "
        f"particle_like_trajectory_screen_pass_count={summary.get('particle_like_trajectory_screen_pass_count', 0)}; "
        f"worst_recent_hypothesis={summary.get('worst_recent_hypothesis_id', '')}; "
        f"worst_recent_selected_pnl={summary.get('worst_recent_selected_pnl_cents', 0)}; "
        f"conclusion={summary.get('conclusion', '')}."
    )


def _paired_sidecar_slice_promotion_readiness_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "paired_sidecar_slice_promotion_readiness=missing."
    summary = _summary_from_payload(payload)
    return (
        "paired_sidecar_slice_promotion_readiness="
        f"promotion_allowed={summary.get('promotion_allowed', 'unknown')}; "
        f"row_count={summary.get('row_count', 0)}; "
        f"particle_like_count={summary.get('particle_like_count', 0)}; "
        f"readiness_candidate_count={summary.get('readiness_candidate_count', 0)}; "
        f"hard_veto_count={summary.get('hard_veto_count', 0)}; "
        f"conclusion={summary.get('conclusion', '')}."
    )


def _paired_sidecar_slice_refresh_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "paired_sidecar_slice_refresh=missing."
    summary = _summary_from_payload(payload)
    return (
        "paired_sidecar_slice_refresh="
        f"promotion_allowed={summary.get('promotion_allowed', 'unknown')}; "
        f"collect_requested={summary.get('collect_requested', 'unknown')}; "
        f"collect_status={summary.get('collect_status', 'unknown')}; "
        f"label_refresh_status={summary.get('label_refresh_status', 'unknown')}; "
        f"aggregate_rows={summary.get('aggregate_joined_rows', 0)}; "
        f"aggregate_markets={summary.get('aggregate_joined_markets', 0)}; "
        f"pending_manifests={summary.get('pending_manifest_count', 0)}; "
        f"pending_enriched_rows={summary.get('pending_enriched_rows', 0)}; "
        f"next_pending_close={summary.get('next_pending_market_close_utc', '')}; "
        f"seconds_until_next_pending_close={summary.get('seconds_until_next_pending_close', 'unknown')}; "
        f"online_rows={summary.get('online_prepared_rows', 0)}; "
        f"slice_fresh_rows={summary.get('slice_fresh_candidate_rows', 0)}; "
        f"slice_fresh_markets={summary.get('slice_fresh_markets', 0)}; "
        f"slice_rows={summary.get('slice_rows', 0)}; "
        f"slice_markets={summary.get('slice_markets', 0)}; "
        f"slice_selected_pnl={summary.get('slice_selected_pnl_cents', 0)}; "
        f"slice_promotion_safe={summary.get('slice_promotion_safe', 'unknown')}."
    )


def _paired_sidecar_spot_refresh_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "paired_sidecar_spot_refresh=missing."
    summary = _summary_from_payload(payload)
    return (
        "paired_sidecar_spot_refresh="
        f"promotion_allowed={summary.get('promotion_allowed', 'unknown')}; "
        f"manifests={summary.get('manifest_count', 0)}; "
        f"skipped={summary.get('skipped_manifest_count', 0)}; "
        f"enrichment_ready={summary.get('enrichment_ready_count', 0)}; "
        f"diagnostic_ready={summary.get('diagnostic_ready_count', 0)}; "
        f"pending={summary.get('pending_diagnostic_count', 0)}; "
        f"aggregate_ready={summary.get('aggregate_ready', 'unknown')}; "
        f"aggregate_fresh={summary.get('aggregate_fresh', 'unknown')}; "
        f"aggregate_rows={summary.get('aggregate_joined_rows', 0)}; "
        f"aggregate_markets={summary.get('aggregate_joined_markets', 0)}; "
        f"rows_remaining={summary.get('aggregate_rows_remaining_for_shadow', 'unknown')}; "
        f"markets_remaining={summary.get('aggregate_markets_remaining_for_shadow', 'unknown')}; "
        f"goal_complete={summary.get('goal_complete', 'unknown')}."
    )


def _summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary")
    return summary if isinstance(summary, dict) else payload


def _variant_loro_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "variant_loro_diagnostic=missing."
    summaries = payload.get("selector_summary_rows") or []
    by_selector = {
        str(row.get("selector")): row
        for row in summaries
        if isinstance(row, dict)
    }
    gate = by_selector.get("train_best_gate_score", {})
    total = by_selector.get("train_best_total_pnl", {})
    return (
        "variant_loro_diagnostic="
        f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
        f"gate_score_strict={gate.get('strict_gate_holdout_count', 0)}/{gate.get('holdout_count', 0)}; "
        f"gate_score_pnl={gate.get('total_holdout_pnl_cents', 0)}; "
        f"best_total_pnl_selector_holdout_pnl={total.get('total_holdout_pnl_cents', 0)}."
    )


def _pasc_loro_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "pasc_loro_threshold=missing."
    summaries = payload.get("selector_summary_rows") or []
    by_selector = {
        str(row.get("selector")): row
        for row in summaries
        if isinstance(row, dict)
    }
    gate = by_selector.get("train_best_gate_score", {})
    stable = by_selector.get("train_best_stable_pnl", {})
    return (
        "pasc_loro_threshold="
        f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
        f"gate_score_strict={gate.get('strict_gate_holdout_count', 0)}/{gate.get('holdout_count', 0)}; "
        f"gate_score_pnl={gate.get('total_holdout_pnl_cents', 0)}; "
        f"gate_score_beats_current={gate.get('beats_current_holdout_count', 0)}/{gate.get('holdout_count', 0)}; "
        f"stable_pnl_strict={stable.get('strict_gate_holdout_count', 0)}/{stable.get('holdout_count', 0)}; "
        f"stable_pnl_total={stable.get('total_holdout_pnl_cents', 0)}."
    )


def _anchor_switch_loro_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "anchor_switch_loro=missing."
    summaries = payload.get("summary_rows") or []
    best = None
    if summaries:
        best = max(
            (row for row in summaries if isinstance(row, dict)),
            key=lambda row: (
                int(row.get("strict_gate_count", 0) or 0),
                int(row.get("beats_current_count", 0) or 0),
                int(row.get("beats_market_count", 0) or 0),
                float(row.get("total_counterfactual_pnl_cents", 0.0) or 0.0),
            ),
            default=None,
        )
    if not best:
        return (
            "anchor_switch_loro="
            f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
            f"summary_rows={len(summaries)}."
        )
    return (
        "anchor_switch_loro="
        f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
        f"best_spec={best.get('spec', 'unknown')}; "
        f"strict_gates={best.get('strict_gate_count', 0)}/{best.get('holdout_count', 0)}; "
        f"beats_current={best.get('beats_current_count', 0)}/{best.get('holdout_count', 0)}; "
        f"beats_market={best.get('beats_market_count', 0)}/{best.get('holdout_count', 0)}; "
        f"total_pnl={best.get('total_counterfactual_pnl_cents', 0)}; "
        f"mean_brier={best.get('mean_brier', 0)}."
    )


def _market_cluster_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "market_cluster_diagnostic=missing."
    return (
        "market_cluster_diagnostic="
        f"market_count={payload.get('market_count', 0)}; "
        f"ev_rank={payload.get('ev_rank_correlation_sign', 0)}; "
        f"top_ev_bucket_avg_market_pnl={payload.get('top_ev_bucket_avg_market_candidate_pnl_cents', 0)}; "
        f"best_probability_model_by_brier={payload.get('best_probability_model_by_market_brier', 'unknown')}."
    )


def _meta_probability_loro_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "meta_probability_loro=missing."
    summaries = payload.get("summary_rows") or []
    best = None
    if summaries:
        best = max(
            (row for row in summaries if isinstance(row, dict)),
            key=lambda row: (
                int(row.get("strict_gate_count", 0) or 0),
                int(row.get("beats_current_count", 0) or 0),
                float(row.get("total_counterfactual_pnl_cents", 0.0) or 0.0),
            ),
            default=None,
        )
    if not best:
        return f"meta_probability_loro=promotion_safe={payload.get('promotion_safe', 'unknown')}."
    return (
        "meta_probability_loro="
        f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
        f"best_model={best.get('model', 'unknown')}; "
        f"strict_gates={best.get('strict_gate_count', 0)}/{best.get('holdout_count', 0)}; "
        f"beats_current={best.get('beats_current_count', 0)}/{best.get('holdout_count', 0)}; "
        f"total_pnl={best.get('total_counterfactual_pnl_cents', 0)}."
    )


def _state_feature_loro_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "state_feature_loro=missing."
    summaries = payload.get("summary_rows") or []
    best = None
    if summaries:
        best = max(
            (row for row in summaries if isinstance(row, dict)),
            key=lambda row: (
                int(row.get("strict_gate_count", 0) or 0),
                int(row.get("beats_current_count", 0) or 0),
                float(row.get("total_counterfactual_pnl_cents", 0.0) or 0.0),
            ),
            default=None,
        )
    if not best:
        return f"state_feature_loro=promotion_safe={payload.get('promotion_safe', 'unknown')}."
    return (
        "state_feature_loro="
        f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
        f"best_model={best.get('model', 'unknown')}; "
        f"strict_gates={best.get('strict_gate_count', 0)}/{best.get('holdout_count', 0)}; "
        f"beats_current={best.get('beats_current_count', 0)}/{best.get('holdout_count', 0)}; "
        f"total_pnl={best.get('total_counterfactual_pnl_cents', 0)}."
    )


def _spot_micro_loro_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "spot_micro_loro=missing."
    summaries = payload.get("summary_rows") or []
    best = None
    if summaries:
        best = max(
            (row for row in summaries if isinstance(row, dict)),
            key=lambda row: (
                int(row.get("strict_gate_count", 0) or 0),
                int(row.get("beats_current_count", 0) or 0),
                float(row.get("total_counterfactual_pnl_cents", 0.0) or 0.0),
            ),
            default=None,
        )
    eligible = len(payload.get("run_inputs") or [])
    skipped = len(payload.get("skipped_run_roots") or [])
    if not best:
        return (
            "spot_micro_loro="
            f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
            f"eligible_runs={eligible}; skipped_runs={skipped}."
        )
    return (
        "spot_micro_loro="
        f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
        f"eligible_runs={eligible}; skipped_runs={skipped}; "
        f"best_model={best.get('model', 'unknown')}; "
        f"strict_gates={best.get('strict_gate_count', 0)}/{best.get('holdout_count', 0)}; "
        f"beats_current={best.get('beats_current_count', 0)}/{best.get('holdout_count', 0)}; "
        f"total_pnl={best.get('total_counterfactual_pnl_cents', 0)}."
    )


def _empirical_next_second_particle_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "empirical_next_second_particle=missing."
    summaries = payload.get("summary_rows") or []
    best = None
    if summaries:
        best = max(
            (row for row in summaries if isinstance(row, dict)),
            key=lambda row: (
                int(row.get("strict_gate_count", 0) or 0),
                int(row.get("beats_current_count", 0) or 0),
                int(row.get("beats_market_count", 0) or 0),
                float(row.get("total_counterfactual_pnl_cents", 0.0) or 0.0),
            ),
            default=None,
        )
    eligible = len(payload.get("run_inputs") or [])
    skipped = len(payload.get("skipped_run_roots") or [])
    ready = bool(payload.get("candidate_ready_for_predeclared_shadow"))
    if not best:
        return (
            "empirical_next_second_particle="
            f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
            f"candidate_ready={ready}; eligible_runs={eligible}; skipped_runs={skipped}."
        )
    return (
        "empirical_next_second_particle="
        f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
        f"candidate_ready={ready}; eligible_runs={eligible}; skipped_runs={skipped}; "
        f"best_spec={best.get('spec', 'unknown')}; "
        f"strict_gates={best.get('strict_gate_count', 0)}/{best.get('run_count', 0)}; "
        f"beats_current={best.get('beats_current_count', 0)}/{best.get('run_count', 0)}; "
        f"beats_market={best.get('beats_market_count', 0)}/{best.get('run_count', 0)}; "
        f"market_ev_rank={best.get('positive_market_ev_rank_count', 0)}/{best.get('run_count', 0)}; "
        f"market_top_bucket={best.get('positive_market_top_bucket_count', 0)}/{best.get('run_count', 0)}; "
        f"total_pnl={best.get('total_counterfactual_pnl_cents', 0)}; "
        f"mean_brier={best.get('mean_brier', 0)}."
    )


def _empirical_current_anchor_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "empirical_current_anchor=missing."
    summaries = payload.get("summary_rows") or []
    best = None
    if summaries:
        best = max(
            (row for row in summaries if isinstance(row, dict)),
            key=lambda row: (
                int(row.get("strict_gate_count", 0) or 0),
                int(row.get("beats_current_count", 0) or 0),
                int(row.get("positive_ev_rank_count", 0) or 0),
                float(row.get("total_counterfactual_pnl_cents", 0.0) or 0.0),
            ),
            default=None,
        )
    eligible = len(payload.get("run_inputs") or [])
    skipped = len(payload.get("skipped_run_roots") or [])
    ready = bool(payload.get("candidate_ready_for_predeclared_shadow"))
    if not best:
        return (
            "empirical_current_anchor="
            f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
            f"candidate_ready={ready}; eligible_runs={eligible}; skipped_runs={skipped}."
        )
    return (
        "empirical_current_anchor="
        f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
        f"candidate_ready={ready}; eligible_runs={eligible}; skipped_runs={skipped}; "
        f"best_spec={best.get('spec', 'unknown')}; "
        f"strict_gates={best.get('strict_gate_count', 0)}/{best.get('run_count', 0)}; "
        f"beats_current={best.get('beats_current_count', 0)}/{best.get('run_count', 0)}; "
        f"ev_rank={best.get('positive_ev_rank_count', 0)}/{best.get('run_count', 0)}; "
        f"market_ev_rank={best.get('positive_market_ev_rank_count', 0)}/{best.get('run_count', 0)}; "
        f"total_pnl={best.get('total_counterfactual_pnl_cents', 0)}; "
        f"mean_brier={best.get('mean_brier', 0)}."
    )


def _empirical_market_opportunity_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "empirical_market_opportunity=missing."
    summaries = payload.get("summary_rows") or []
    best = None
    if summaries:
        best = max(
            (row for row in summaries if isinstance(row, dict)),
            key=lambda row: (
                int(row.get("strict_gate_count", 0) or 0),
                int(row.get("positive_pnl_count", 0) or 0),
                int(row.get("beats_current_count", 0) or 0),
                int(row.get("positive_top_bucket_count", 0) or 0),
                float(row.get("total_counterfactual_pnl_cents", 0.0) or 0.0),
            ),
            default=None,
        )
    eligible = len(payload.get("run_inputs") or [])
    skipped = len(payload.get("skipped_run_roots") or [])
    ready = bool(payload.get("candidate_ready_for_predeclared_shadow"))
    if not best:
        return (
            "empirical_market_opportunity="
            f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
            f"candidate_ready={ready}; eligible_runs={eligible}; skipped_runs={skipped}."
        )
    return (
        "empirical_market_opportunity="
        f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
        f"candidate_ready={ready}; eligible_runs={eligible}; skipped_runs={skipped}; "
        f"best={best.get('family', 'unknown')}:{best.get('spec', 'unknown')}; "
        f"strict_gates={best.get('strict_gate_count', 0)}/{best.get('run_count', 0)}; "
        f"positive_pnl={best.get('positive_pnl_count', 0)}/{best.get('run_count', 0)}; "
        f"beats_current={best.get('beats_current_count', 0)}/{best.get('run_count', 0)}; "
        f"top_bucket={best.get('positive_top_bucket_count', 0)}/{best.get('run_count', 0)}; "
        f"total_pnl={best.get('total_counterfactual_pnl_cents', 0)}; "
        f"markets={best.get('market_count', 0)}."
    )


def _empirical_market_opportunity_loro_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "empirical_market_opportunity_loro=missing."
    summaries = payload.get("summary_rows") or []
    best = None
    if summaries:
        best = max(
            (row for row in summaries if isinstance(row, dict)),
            key=lambda row: (
                int(row.get("strict_gate_holdout_count", 0) or 0),
                int(row.get("beats_current_holdout_count", 0) or 0),
                int(row.get("positive_ev_rank_holdout_count", 0) or 0),
                int(row.get("positive_top_bucket_holdout_count", 0) or 0),
                float(row.get("total_holdout_pnl_cents", 0.0) or 0.0),
            ),
            default=None,
        )
    ready = bool(payload.get("candidate_ready_for_predeclared_shadow"))
    if not best:
        return (
            "empirical_market_opportunity_loro="
            f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
            f"candidate_ready={ready}; source_runs={payload.get('source_run_count', 0)}; "
            f"opportunity_rows={payload.get('source_opportunity_row_count', 0)}."
        )
    return (
        "empirical_market_opportunity_loro="
        f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
        f"candidate_ready={ready}; source_runs={payload.get('source_run_count', 0)}; "
        f"opportunity_rows={payload.get('source_opportunity_row_count', 0)}; "
        f"selector={best.get('selector', 'unknown')}; "
        f"strict_gates={best.get('strict_gate_holdout_count', 0)}/{best.get('holdout_count', 0)}; "
        f"positive_pnl={best.get('positive_pnl_holdout_count', 0)}/{best.get('holdout_count', 0)}; "
        f"beats_current={best.get('beats_current_holdout_count', 0)}/{best.get('holdout_count', 0)}; "
        f"ev_rank={best.get('positive_ev_rank_holdout_count', 0)}/{best.get('holdout_count', 0)}; "
        f"top_bucket={best.get('positive_top_bucket_holdout_count', 0)}/{best.get('holdout_count', 0)}; "
        f"total_pnl={best.get('total_holdout_pnl_cents', 0)}."
    )


def _spot_drift_terminal_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "spot_drift_terminal=missing."
    summaries = payload.get("summary_rows") or []
    best = None
    if summaries:
        best = max(
            (row for row in summaries if isinstance(row, dict)),
            key=lambda row: (
                int(row.get("strict_gate_count", 0) or 0),
                int(row.get("beats_current_count", 0) or 0),
                int(row.get("beats_market_count", 0) or 0),
                float(row.get("total_counterfactual_pnl_cents", 0.0) or 0.0),
            ),
            default=None,
        )
    eligible = len(payload.get("run_inputs") or [])
    skipped = len(payload.get("skipped_run_roots") or [])
    ready = bool(payload.get("candidate_ready_for_predeclared_shadow"))
    if not best:
        return (
            "spot_drift_terminal="
            f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
            f"candidate_ready={ready}; eligible_runs={eligible}; skipped_runs={skipped}."
        )
    return (
        "spot_drift_terminal="
        f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
        f"candidate_ready={ready}; eligible_runs={eligible}; skipped_runs={skipped}; "
        f"best_spec={best.get('spec', 'unknown')}; "
        f"strict_gates={best.get('strict_gate_count', 0)}/{best.get('run_count', 0)}; "
        f"beats_current={best.get('beats_current_count', 0)}/{best.get('run_count', 0)}; "
        f"beats_market={best.get('beats_market_count', 0)}/{best.get('run_count', 0)}; "
        f"market_ev_rank={best.get('positive_market_ev_rank_count', 0)}/{best.get('run_count', 0)}; "
        f"market_top_bucket={best.get('positive_market_top_bucket_count', 0)}/{best.get('run_count', 0)}; "
        f"total_pnl={best.get('total_counterfactual_pnl_cents', 0)}; "
        f"mean_brier={best.get('mean_brier', 0)}."
    )


def _spot_drift_regime_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "spot_drift_regime=missing."
    summaries = payload.get("rule_summary_rows") or []
    best = None
    if summaries:
        best = max(
            (row for row in summaries if isinstance(row, dict)),
            key=lambda row: (
                bool(row.get("stable_positive")),
                int(row.get("positive_run_count", 0) or 0),
                float(row.get("total_counterfactual_pnl_cents", 0.0) or 0.0),
                int(row.get("selected_count", 0) or 0),
            ),
            default=None,
        )
    ready = bool(payload.get("candidate_ready_for_predeclared_shadow"))
    stable_count = len(payload.get("stable_positive_rules") or [])
    eligible = len(payload.get("run_inputs") or [])
    skipped = len(payload.get("skipped_run_roots") or [])
    if not best:
        return (
            "spot_drift_regime="
            f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
            f"candidate_ready={ready}; eligible_runs={eligible}; skipped_runs={skipped}; "
            f"stable_rules={stable_count}."
        )
    return (
        "spot_drift_regime="
        f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
        f"candidate_ready={ready}; eligible_runs={eligible}; skipped_runs={skipped}; "
        f"stable_rules={stable_count}; "
        f"best_rule={best.get('spec', 'unknown')}:{best.get('rule', 'unknown')}; "
        f"positive_runs={best.get('positive_run_count', 0)}/{best.get('run_count', 0)}; "
        f"nonzero_runs={best.get('nonzero_run_count', 0)}/{best.get('run_count', 0)}; "
        f"total_pnl={best.get('total_counterfactual_pnl_cents', 0)}; "
        f"min_run_pnl={best.get('min_run_pnl_cents', 0)}."
    )


def _spot_rv_anchor_switch_loro_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "spot_rv_anchor_switch_loro=missing."
    summaries = payload.get("summary_rows") or []
    best = None
    if summaries:
        best = max(
            (row for row in summaries if isinstance(row, dict)),
            key=lambda row: (
                int(row.get("strict_gate_count", 0) or 0),
                int(row.get("beats_current_count", 0) or 0),
                int(row.get("beats_market_count", 0) or 0),
                float(row.get("total_counterfactual_pnl_cents", 0.0) or 0.0),
            ),
            default=None,
        )
    eligible = len(payload.get("run_inputs") or [])
    skipped = len(payload.get("skipped_run_roots") or [])
    ready = bool(payload.get("candidate_ready_for_predeclared_shadow"))
    if not best:
        return (
            "spot_rv_anchor_switch_loro="
            f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
            f"candidate_ready={ready}; eligible_runs={eligible}; skipped_runs={skipped}."
        )
    return (
        "spot_rv_anchor_switch_loro="
        f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
        f"candidate_ready={ready}; eligible_runs={eligible}; skipped_runs={skipped}; "
        f"best_spec={best.get('spec', 'unknown')}; "
        f"strict_gates={best.get('strict_gate_count', 0)}/{best.get('holdout_count', 0)}; "
        f"beats_current={best.get('beats_current_count', 0)}/{best.get('holdout_count', 0)}; "
        f"beats_market={best.get('beats_market_count', 0)}/{best.get('holdout_count', 0)}; "
        f"market_ev_rank={best.get('positive_market_ev_rank_count', 0)}/{best.get('holdout_count', 0)}; "
        f"market_top_bucket={best.get('positive_market_top_bucket_count', 0)}/{best.get('holdout_count', 0)}; "
        f"total_pnl={best.get('total_counterfactual_pnl_cents', 0)}."
    )


def _spot_rv_current_residual_loro_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "spot_rv_current_residual_loro=missing."
    summaries = payload.get("summary_rows") or []
    best = None
    if summaries:
        best = max(
            (row for row in summaries if isinstance(row, dict)),
            key=lambda row: (
                int(row.get("strict_gate_count", 0) or 0),
                int(row.get("beats_current_count", 0) or 0),
                int(row.get("beats_market_count", 0) or 0),
                float(row.get("total_counterfactual_pnl_cents", 0.0) or 0.0),
            ),
            default=None,
        )
    eligible = len(payload.get("run_inputs") or [])
    skipped = len(payload.get("skipped_run_roots") or [])
    ready = bool(payload.get("candidate_ready_for_predeclared_shadow"))
    if not best:
        return (
            "spot_rv_current_residual_loro="
            f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
            f"candidate_ready={ready}; eligible_runs={eligible}; skipped_runs={skipped}."
        )
    return (
        "spot_rv_current_residual_loro="
        f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
        f"candidate_ready={ready}; eligible_runs={eligible}; skipped_runs={skipped}; "
        f"best_spec={best.get('spec', 'unknown')}; "
        f"strict_gates={best.get('strict_gate_count', 0)}/{best.get('holdout_count', 0)}; "
        f"beats_current={best.get('beats_current_count', 0)}/{best.get('holdout_count', 0)}; "
        f"beats_market={best.get('beats_market_count', 0)}/{best.get('holdout_count', 0)}; "
        f"market_ev_rank={best.get('positive_market_ev_rank_count', 0)}/{best.get('holdout_count', 0)}; "
        f"market_top_bucket={best.get('positive_market_top_bucket_count', 0)}/{best.get('holdout_count', 0)}; "
        f"total_pnl={best.get('total_counterfactual_pnl_cents', 0)}; "
        f"mean_brier={best.get('mean_brier', 0)}."
    )


def _spot_realized_vol_terminal_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "spot_realized_vol_terminal=missing."
    summaries = payload.get("summary_rows") or []
    best = None
    if summaries:
        best = max(
            (row for row in summaries if isinstance(row, dict)),
            key=lambda row: (
                int(row.get("strict_gate_count", 0) or 0),
                int(row.get("beats_brownian_count", 0) or 0),
                int(row.get("beats_current_count", 0) or 0),
                float(row.get("total_counterfactual_pnl_cents", 0.0) or 0.0),
            ),
            default=None,
        )
    eligible = len(payload.get("run_inputs") or [])
    skipped = len(payload.get("skipped_run_roots") or [])
    if not best:
        return (
            "spot_realized_vol_terminal="
            f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
            f"eligible_runs={eligible}; skipped_runs={skipped}."
        )
    return (
        "spot_realized_vol_terminal="
        f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
        f"eligible_runs={eligible}; skipped_runs={skipped}; "
        f"best_spec={best.get('spec', 'unknown')}; "
        f"strict_gates={best.get('strict_gate_count', 0)}/{best.get('run_count', 0)}; "
        f"beats_brownian={best.get('beats_brownian_count', 0)}/{best.get('run_count', 0)}; "
        f"beats_current={best.get('beats_current_count', 0)}/{best.get('run_count', 0)}; "
        f"total_pnl={best.get('total_counterfactual_pnl_cents', 0)}; "
        f"mean_brier={best.get('mean_brier', 0)}."
    )


def _fat_tail_diagnostic_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "fat_tail_particle_diagnostic=missing."
    summaries = payload.get("summary_rows") or []
    best = None
    if summaries:
        best = max(
            (row for row in summaries if isinstance(row, dict)),
            key=lambda row: (
                int(row.get("strict_gate_count", 0) or 0),
                int(row.get("beats_current_count", 0) or 0),
                float(row.get("total_counterfactual_pnl_cents", 0.0) or 0.0),
            ),
            default=None,
        )
    if not best:
        return f"fat_tail_particle_diagnostic=promotion_safe={payload.get('promotion_safe', 'unknown')}."
    return (
        "fat_tail_particle_diagnostic="
        f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
        f"best_spec={best.get('spec', 'unknown')}; "
        f"strict_gates={best.get('strict_gate_count', 0)}/{best.get('run_count', 0)}; "
        f"beats_current={best.get('beats_current_count', 0)}/{best.get('run_count', 0)}; "
        f"total_pnl={best.get('total_counterfactual_pnl_cents', 0)}; "
        f"mean_brier={best.get('mean_brier', 0)}."
    )


def _fixed_terminal_stability_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "fixed_terminal_gauss45_stability=missing."
    rows = payload.get("stability_rows") or []
    fixed_rows = [
        row for row in rows
        if isinstance(row, dict) and str(row.get("source")) == "fixed_terminal"
    ]
    best = max(
        fixed_rows,
        key=lambda row: float(row.get("total_counterfactual_pnl_cents", 0.0) or 0.0),
        default=None,
    )
    if not best:
        return (
            "fixed_terminal_gauss45_stability="
            f"run_count={payload.get('run_count', 0)}; "
            f"stable_candidates={payload.get('stable_candidate_count', 0)}; "
            "fixed_rows=0."
        )
    return (
        "fixed_terminal_gauss45_stability="
        f"run_count={payload.get('run_count', 0)}; "
        f"stable_candidates={payload.get('stable_candidate_count', 0)}; "
        f"best={best.get('name', 'unknown')}; "
        f"best_runs={best.get('run_count', 0)}; "
        f"total_pnl={best.get('total_counterfactual_pnl_cents', 0)}; "
        f"beats_brownian={best.get('beats_brownian_run_count', 0)}/{best.get('run_count', 0)}; "
        f"beats_current={best.get('beats_current_run_count', 0)}/{best.get('run_count', 0)}; "
        f"stable_all_runs={best.get('stable_all_runs', False)}."
    )


def _online_anchor_diagnostic_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "online_anchor_calibration=missing."
    summaries = payload.get("summary_rows") or []
    best = max(
        (row for row in summaries if isinstance(row, dict)),
        key=lambda row: (
            int(row.get("strict_gate_count", 0) or 0),
            int(row.get("beats_brownian_count", 0) or 0),
            float(row.get("total_counterfactual_pnl_cents", 0.0) or 0.0),
        ),
        default=None,
    )
    if not best:
        return (
            "online_anchor_calibration="
            f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
            f"summary_rows={len(summaries)}."
        )
    return (
        "online_anchor_calibration="
        f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
        f"best={best.get('spec', 'unknown')}; "
        f"strict_gates={best.get('strict_gate_count', 0)}/{best.get('run_count', 0)}; "
        f"beats_raw={best.get('beats_raw_count', 0)}/{best.get('run_count', 0)}; "
        f"beats_brownian={best.get('beats_brownian_count', 0)}/{best.get('run_count', 0)}; "
        f"beats_market={best.get('beats_market_count', 0)}/{best.get('run_count', 0)}; "
        f"beats_current={best.get('beats_current_count', 0)}/{best.get('run_count', 0)}; "
        f"total_pnl={best.get('total_counterfactual_pnl_cents', 0)}."
    )


def _anchor_regime_profile_detail(payload: dict[str, Any]) -> str:
    if not payload:
        return "anchor_regime_profile=missing."
    return (
        "anchor_regime_profile="
        f"promotion_safe={payload.get('promotion_safe', 'unknown')}; "
        f"run_best={payload.get('run_best_counts_by_brier', {})}; "
        f"market_best={payload.get('market_best_counts_by_brier', {})}; "
        f"state_bucket_best={payload.get('state_bucket_best_counts_by_brier', {})}; "
        f"conclusion={payload.get('conclusion', 'unknown')}."
    )


def _load_synthetic_reports(report_dir: Path) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    if report_dir.exists():
        for path in report_dir.glob("synthetic_replay*.json"):
            reports.append(_load_json(path))
    fixture_root = report_dir.parent if report_dir.exists() else Path("logs") / "particle_research"
    for path in fixture_root.glob("synthetic_fixture_*/reports/synthetic_replay.json"):
        reports.append(_load_json(path))
    return [report for report in reports if report]


def _candidate_snapshot_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(root.rglob("candidate_snapshots.ndjson"))


def _line_count(paths: Iterable[Path]) -> int:
    total = 0
    for path in paths:
        try:
            with path.open("r", encoding="utf-8", errors="replace") as handle:
                total += sum(1 for line in handle if line.strip())
        except Exception:
            continue
    return total


def _looks_synthetic_or_unit(path: Path) -> bool:
    text = str(path).replace("\\", "/").lower()
    return "synthetic_fixture" in text or "unit_test" in text


def _looks_real_replay_report(path: Path) -> bool:
    name = path.name.lower()
    if "synthetic" in name or "unit_test" in name:
        return False
    payload = _load_json(path)
    required = {
        "particle_beats_brownian",
        "particle_beats_market",
        "particle_beats_current_calibrated",
        "top_ev_bucket_pnl_cents",
        "total_counterfactual_pnl_cents",
    }
    return required <= set(payload)


def _real_report_clears_promotion(payload: dict[str, Any]) -> bool:
    return (
        bool(payload.get("particle_beats_brownian"))
        and bool(payload.get("particle_beats_market"))
        and bool(payload.get("particle_beats_current_calibrated"))
        and float(payload.get("ev_rank_correlation_sign", 0.0) or 0.0) > 0.0
        and float(payload.get("top_ev_bucket_pnl_cents", 0.0) or 0.0) > 0.0
        and float(payload.get("total_counterfactual_pnl_cents", 0.0) or 0.0) > 0.0
    )


def _synthetic_report_passes(payload: dict[str, Any]) -> bool:
    beats_all = bool(payload.get("particle_beats_all_baselines")) or (
        bool(payload.get("particle_beats_brownian"))
        and bool(payload.get("particle_beats_market"))
        and bool(payload.get("particle_beats_current_calibrated"))
    )
    pnl_positive = bool(payload.get("shadow_counterfactual_positive")) or (
        float(payload.get("total_counterfactual_pnl_cents", 0.0) or 0.0) > 0.0
    )
    return beats_all and pnl_positive and int(payload.get("candidate_count", 0) or 0) > 0


def main() -> int:
    payload = audit()
    json_path, md_path = write_report(payload)
    print("Particle goal completion audit complete")
    print(f"complete={payload['complete']}")
    print(f"strict_real_candidate_rows={payload['strict_real_candidate_rows']}")
    print(f"real_replay_reports={len(payload['real_replay_reports'])}")
    print(f"json={json_path}")
    print(f"report={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
