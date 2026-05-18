param(
    [int]$IntervalSeconds = 60
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoDir = Split-Path -Parent $scriptDir
$python = Join-Path $repoDir 'venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    $python = 'python'
}

$logDir = Join-Path $repoDir 'logs\shadow_mushroom_v28_reactivation_size2'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$loopLog = Join-Path $logDir 'status_loop.log'
$probeTimeoutSeconds = 45
$script:probeFailures = 0

function Invoke-Probe {
    param(
        [string]$ProbeName,
        [int]$TimeoutSeconds = $probeTimeoutSeconds
    )
    $probePath = Join-Path $repoDir $ProbeName
    $proc = Start-Process -FilePath $python -ArgumentList @("`"$probePath`"") -WindowStyle Hidden -PassThru
    Wait-Process -Id $proc.Id -Timeout $TimeoutSeconds -ErrorAction SilentlyContinue
    $stillRunning = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
    if ($stillRunning) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $timeoutStamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'
        Add-Content -Path $loopLog -Value "$timeoutStamp | probe_timeout | $ProbeName" -Encoding UTF8
        $script:probeFailures += 1
        return $false
    }
    if ($proc.ExitCode -ne 0) {
        $failStamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'
        Add-Content -Path $loopLog -Value "$failStamp | probe_failed | $ProbeName | exit_code=$($proc.ExitCode)" -Encoding UTF8
        $script:probeFailures += 1
        return $false
    }
    return $true
}

if (-not $env:V28_TRIAL_START_BALANCE_CENTS) {
    $env:V28_TRIAL_START_BALANCE_CENTS = '1276'
}
if (-not $env:V28_CURRENT_ACCOUNT_BALANCE_CENTS) {
    $env:V28_CURRENT_ACCOUNT_BALANCE_CENTS = '2640'
}
if (-not $env:V28_MEDIUM_RISK_LOSS_STOP_COUNT) {
    $env:V28_MEDIUM_RISK_LOSS_STOP_COUNT = '5'
}
if (-not $env:V28_MEDIUM_RISK_DRAWDOWN_STOP_PCT) {
    $env:V28_MEDIUM_RISK_DRAWDOWN_STOP_PCT = '0.40'
}

while ($true) {
    $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'
    try {
        $script:probeFailures = 0
        Invoke-Probe 'probe_v28_reactivated_shadow_status.py' | Out-Null
        Invoke-Probe 'probe_v28_common_clock_live_trial_status.py' | Out-Null
        Invoke-Probe 'probe_v28_common_clock_live_execution_diagnostics.py' | Out-Null
        Invoke-Probe 'probe_v28_forward_physics_registry.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_branch_diagnostic.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_policy_candidates.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_reduce_threshold_bakeoff.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_exit_reduce_suppression.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_reduce_suppression_risk_ledger.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_reduce_loss_control_signature.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_reduce_loss_control_actionability.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_exit_reduce_loss_control_refinement.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_exit_reduce_depth_gate.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_exit_reduce_observable_loss_control_watch.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_reduce_observable_loss_control_opportunity.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_reduce_depth_gate_runway.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_reduce_depth_gate_opportunity.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_exit_reduce_yes_suppression.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_reduce_suppression_robustness.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_reduce_side_split_attribution.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_reduce_promotion_runway.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_reduce_geometry_suppression.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_exit_reduce_geometry_suppression.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_reduce_geometry_opportunity.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_exit_reduce_geometry_relaxed_watch.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_book_gap_candidates.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_exit_book_gap_suppression.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_exit_book_gap_loss_guard.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_exit_book_gap_loss_guard_v2.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_exit_book_gap_loss_guard_v3.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_book_gap_loss_guard_v2_opportunity.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_book_gap_loss_guard_v3_opportunity.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_loss_guard_v1_v2_contrast.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_loss_guard_v1_v2_v3_contrast.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_loss_guard_v1_v2_runway.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_exit_value_reduce_depth_composite.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_exit_value_reduce_depth_opportunity.py' | Out-Null
        Invoke-Probe 'probe_v28_shadow_observation_availability.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_book_gap_loss_guard_opportunity.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_book_gap_value_only_opportunity.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_policy_common_clock_watch.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_policy_strict_failure_drilldown.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_dual_exit_book_gap_else_reduce.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_policy_watch_dashboard.py' | Out-Null
        Invoke-Probe 'probe_v28_active_trade_sensitivity.py' | Out-Null
        Invoke-Probe 'probe_v28_post_exit_path.py' | Out-Null
        Invoke-Probe 'probe_v28_market_churn.py' | Out-Null
        Invoke-Probe 'probe_v28_reentry_throttle_candidates.py' | Out-Null
        Invoke-Probe 'probe_v28_rejected_opportunity_score.py' | Out-Null
        Invoke-Probe 'probe_v28_forward_calibration.py' | Out-Null
        Invoke-Probe 'probe_v28_book_disagreement_calibration.py' | Out-Null
        Invoke-Probe 'probe_v28_shadow_fv_variants.py' | Out-Null
        Invoke-Probe 'probe_v28_information_decay_diagnostic.py' | Out-Null
        Invoke-Probe 'probe_v28_rmt_regime_diagnostic.py' | Out-Null
        Invoke-Probe 'probe_v28_state_aware_fv_candidates.py' | Out-Null
        Invoke-Probe 'probe_v28_rmt_forgetting_entry_bakeoff.py' | Out-Null
        Invoke-Probe 'probe_v28_book_favorite_edge_diagnostic.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_book_exact_entry_gate.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_forward_candidates.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_threshold_challengers.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_timing_diagnostic.py' | Out-Null
        Invoke-Probe 'probe_v28_side_flip_path_diagnostic.py' | Out-Null
        Invoke-Probe 'probe_v28_side_agreement_meta_candidate.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_side_agreement_challengers.py' | Out-Null
        Invoke-Probe 'probe_v28_convex_raw_escape_candidate.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_convex_escape_challengers.py' | Out-Null
        Invoke-Probe 'probe_v28_raw_conviction_override_diagnostic.py' | Out-Null
        Invoke-Probe 'probe_v28_forward_coverage_pressure_audit.py' | Out-Null
        Invoke-Probe 'probe_v28_raw_physics_penalty_candidates.py' | Out-Null
        Invoke-Probe 'probe_v28_raw_p52_forward_loss_cluster.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_raw_p52_boundary_turbulence_skip.py' | Out-Null
        Invoke-Probe 'probe_v28_uncertainty_lower_bound_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_ev_breakeven_attribution.py' | Out-Null
        Invoke-Probe 'probe_v28_raw_p52_favorite_valley_skip.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_raw_p52_favorite_valley_skip.py' | Out-Null
        Invoke-Probe 'probe_v28_raw_p52_mid_edge_skip.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_raw_p52_mid_edge_skip.py' | Out-Null
        Invoke-Probe 'probe_v28_raw_p52_shadow_mid_edge_skip.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_raw_p52_shadow_mid_edge_skip.py' | Out-Null
        Invoke-Probe 'probe_v28_raw_p52_book_disagreement_skip.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_raw_p52_book_disagreement_skip.py' | Out-Null
        Invoke-Probe 'probe_v28_raw_p52_book_shrink_entry.py' | Out-Null
        Invoke-Probe 'probe_v28_book_disagreement_replacement_attribution.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_raw_p52_book_shrink_entry.py' | Out-Null
        Invoke-Probe 'probe_v28_raw_p52_early_no_boundary_skip.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_raw_p52_early_no_boundary_skip.py' | Out-Null
        Invoke-Probe 'probe_v28_raw_p52_early_no_boundary_band_skip.py' | Out-Null
        Invoke-Probe 'probe_v28_raw_p52_early_no_boundary_band_robustness.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_raw_p52_early_no_boundary_band_skip.py' | Out-Null
        Invoke-Probe 'probe_v28_raw_p52_early_no_boundary_band_runway.py' | Out-Null
        Invoke-Probe 'probe_v28_raw_p52_delta_diagnostic.py' | Out-Null
        Invoke-Probe 'probe_v28_raw_p52_confirmation_path.py' | Out-Null
        Invoke-Probe 'probe_v28_raw_p52_sideflip_candidate.py' | Out-Null
        Invoke-Probe 'probe_v28_raw_p52_recross_escape_candidate.py' | Out-Null
        Invoke-Probe 'probe_v28_recross_escape_probability_calibration.py' | Out-Null
        Invoke-Probe 'probe_v28_noise_floor_shrinkage_candidates.py' | Out-Null
        Invoke-Probe 'probe_v28_confidence_shrink_schedule_bakeoff.py' | Out-Null
        Invoke-Probe 'probe_v28_hybrid_confidence_shrink_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_raw_entry_calibrated_probability.py' | Out-Null
        Invoke-Probe 'probe_v28_probability_profit_bridge.py' | Out-Null
        Invoke-Probe 'probe_v28_approved_entry_fv_overlay_validator.py' | Out-Null
        Invoke-Probe 'probe_v28_approved_entry_book_fv_robustness.py' | Out-Null
        Invoke-Probe 'probe_v28_approved_entry_book_raw_blend.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_approved_entry_book_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_approved_entry_book_raw_blend.py' | Out-Null
        Invoke-Probe 'probe_v28_approved_entry_book_fv_regime_attribution.py' | Out-Null
        Invoke-Probe 'probe_v28_approved_entry_book_edge_actionability.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_approved_entry_book_edge_gate.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_approved_entry_conditional_book_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_entry_conditioned_posterior_diagnostic.py' | Out-Null
        Invoke-Probe 'probe_v28_source_aware_fv_overlay_validator.py' | Out-Null
        Invoke-Probe 'probe_v28_source_aware_fv_robustness_audit.py' | Out-Null
        Invoke-Probe 'probe_v28_source_aware_fv_promotion_audit.py' | Out-Null
        Invoke-Probe 'probe_v28_approved_entry_state_valves.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_approved_entry_state_valve.py' | Out-Null
        Invoke-Probe 'probe_v28_danger_zone_entry_valve.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_danger_zone_entry_valve.py' | Out-Null
        Invoke-Probe 'probe_v28_danger_zone_fv_calibration.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_danger_zone_fv_calibration.py' | Out-Null
        Invoke-Probe 'probe_v28_danger_zone_robustness_audit.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_danger_zone_robustness.py' | Out-Null
        Invoke-Probe 'probe_v28_book_disagreement_trajectory_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_book_trajectory_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_book_trajectory_entry_projection.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_pending_monitor.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_forward_scorecard.py' | Out-Null
        Invoke-Probe 'probe_v28_entry_conditioned_lift_plateau.py' | Out-Null
        Invoke-Probe 'probe_v28_entry_conditioned_jackknife.py' | Out-Null
        Invoke-Probe 'probe_v28_entry_conditioned_data_quality.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_raw_physics_challengers.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_raw_p52_sideflip_challenger.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_raw_p52_recross_escape_challenger.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_recross_escape_probability_calibration.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_recross_escape_attribution.py' | Out-Null
        Invoke-Probe 'probe_v28_recross_escape_sample_plan.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_noise_floor_shrinkage_challengers.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_raw_entry_calibrated_probability.py' | Out-Null
        Invoke-Probe 'probe_v28_calibrated_fv_forward_monitor.py' | Out-Null
        Invoke-Probe 'probe_v28_calibrated_fv_sequential_evidence.py' | Out-Null
        Invoke-Probe 'probe_v28_calibrated_fv_physics_attribution.py' | Out-Null
        Invoke-Probe 'probe_v28_calibrated_fv_path_contradiction.py' | Out-Null
        Invoke-Probe 'probe_v28_path_confirmed_entry_candidates.py' | Out-Null
        Invoke-Probe 'probe_v28_path_rmt_forward_gate.py' | Out-Null
        Invoke-Probe 'probe_v28_fv_model_readiness.py' | Out-Null
        Invoke-Probe 'probe_v28_fv_overlay_challenger_readiness.py' | Out-Null
        Invoke-Probe 'probe_v28_calibrated_fv_sample_plan.py' | Out-Null
        Invoke-Probe 'probe_v28_raw_entry_coverage_valve.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_fv_overlay_validator.py' | Out-Null
        Invoke-Probe 'probe_v28_target_surface_hybrid_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_target_hybrid_veto_repair.py' | Out-Null
        Invoke-Probe 'probe_v28_hybrid_boundary_entry_stack.py' -TimeoutSeconds 180 | Out-Null
        Invoke-Probe 'probe_v28_hybrid_boundary_entry_stack_source_stress.py' -TimeoutSeconds 60 | Out-Null
        Invoke-Probe 'probe_v28_hybrid_boundary_entry_stack_stress.py' | Out-Null
        Invoke-Probe 'probe_v28_hybrid_boundary_source_frontier.py' | Out-Null
        Invoke-Probe 'probe_v28_hybrid_boundary_source_dilution_runway.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_loss_attribution.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_price_friction.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_entropy_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_false_conviction_physics_audit.py' | Out-Null
        Invoke-Probe 'probe_v28_composite_false_conviction_repair_bakeoff.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_composite_false_conviction_repair_robustness.py' | Out-Null
        Invoke-Probe 'probe_v28_composite_false_conviction_repair_stress.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_target_loss_tag_repair_entry.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_early_no_boundary_decay_repair_entry.py' | Out-Null
        Invoke-Probe 'probe_v28_early_no_boundary_decay_repair_runway.py' | Out-Null
        Invoke-Probe 'probe_v28_early_no_boundary_decay_repair_stress.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_mid_edge_boundary_deception_repair_entry.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_composite_false_conviction_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_composite_false_conviction_repair_entry.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_goldilocks_edge_repair_entry.py' | Out-Null
        Invoke-Probe 'probe_v28_goldilocks_edge_repair_stress.py' | Out-Null
        Invoke-Probe 'probe_v28_false_conviction_source_quality_repair.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_false_conviction_approved_repair.py' | Out-Null
        Invoke-Probe 'probe_v28_false_conviction_fv_entry_bridge.py' | Out-Null
        Invoke-Probe 'probe_v28_book_dislocation_regime_attribution.py' | Out-Null
        Invoke-Probe 'probe_v28_book_dislocation_fv_bridge.py' | Out-Null
        Invoke-Probe 'probe_v28_fv_bridge_source_quality.py' | Out-Null
        Invoke-Probe 'probe_v28_fv_bridge_direction_vs_realized.py' | Out-Null
        Invoke-Probe 'probe_v28_fv_bridge_exit_geometry_stack.py' | Out-Null
        Invoke-Probe 'probe_v28_fv_bridge_stack_residual_exit_attribution.py' | Out-Null
        Invoke-Probe 'probe_v28_fv_bridge_exit_combo_bakeoff.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_fv_bridge_exit_geometry_stack.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_fv_bridge_exit_combo_stack.py' | Out-Null
        Invoke-Probe 'probe_v28_btc_activity_memory_escape_bridge.py' | Out-Null
        Invoke-Probe 'probe_v28_false_conviction_family_scorecard.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_fv_sequential_evidence.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_fv_attribution.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_promotion_audit.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_sample_runway.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_fv_fragility_audit.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_fv_bucket_reliability.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_fv_live_evidence_audit.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_danger_overlap.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_pnl_attribution.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_failure_clusters.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_cluster_penalty_watch.py' | Out-Null
        Invoke-Probe 'probe_v28_target_cluster_penalty_runway.py' | Out-Null
        Invoke-Probe 'probe_v28_target_cluster_penalty_source_feasibility.py' -TimeoutSeconds 90 | Out-Null
        Invoke-Probe 'probe_v28_target_cluster_penalty_source_aware_watch.py' | Out-Null
        Invoke-Probe 'probe_v28_target_cluster_penalty_source_displacement.py' -TimeoutSeconds 90 | Out-Null
        Invoke-Probe 'probe_v28_target_cluster_penalty_observable_stability_proxy.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_conservative_fv_variants.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_boundary_temperature_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_boundary_temperature_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_boundary_energy_fv_entry.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_early_no_boundary_fv_entry.py' | Out-Null
        Invoke-Probe 'probe_v28_early_no_boundary_fv_jackknife.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_source_split_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_p70_jackknife.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_p70_sequential_evidence.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_confidence_temperature_bakeoff.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_p70_fragility_stress.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_p70_scale_bakeoff.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_p70_empirical_bayes.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_target_coverage_conservative_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_target_coverage_p70_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_target_coverage_p70_empirical_bayes.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_path_state_p70_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_boundary_recross_shrink_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_target_coverage_book_edge_gate.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_mid_edge_false_conviction_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_recross_phase_fv_bakeoff.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_reversal_opportunity.py' | Out-Null
        Invoke-Probe 'probe_v28_weak_boundary_reversal_strategy.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_weak_boundary_reversal_bakeoff.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_weak_reversal_residual_attribution.py' | Out-Null
        Invoke-Probe 'probe_v28_weak_reversal_residual_fv_shrink.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_weak_reversal_residual_fv_shrink.py' | Out-Null
        Invoke-Probe 'probe_v28_no_mid_edge_fv_generalization.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_no_mid_edge_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_no_mid_edge_entry_repair.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_weak_reversal_residual_repair.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_frozen_weak_reversal_residual_repair.py' | Out-Null
        Invoke-Probe 'probe_v28_early_clock_wait_bakeoff.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_frozen_early_boundary_wait_repair.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_early_boundary_opposite_wait_repair.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_gamma_repair_entry.py' | Out-Null
        Invoke-Probe 'probe_v28_danger_tag_replacement_diagnostic.py' | Out-Null
        Invoke-Probe 'probe_v28_coverage_repair_pool_diagnostic.py' | Out-Null
        Invoke-Probe 'probe_v28_danger_repair_bakeoff.py' | Out-Null
        Invoke-Probe 'probe_v28_repair_scoring_bakeoff.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_adjusted_fv_repair_bakeoff.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_frozen_high_raw_p_repair_entry.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_hazard_repair.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_robustness_audit.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_fv_overlay.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_fv_robustness.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_residual_attribution.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_boundary_clock_residual_registry.py' | Out-Null
        Invoke-Probe 'probe_v28_side_asymmetry_fv_diagnostic.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_side_asymmetry_registry.py' | Out-Null
        Invoke-Probe 'probe_v28_side_asymmetry_fv_overlay.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_side_asymmetry_fv_overlay.py' | Out-Null
        Invoke-Probe 'probe_v28_side_asymmetry_fv_entry_bridge.py' -TimeoutSeconds 180 | Out-Null
        Invoke-Probe 'probe_v28_side_asymmetry_bridge_repair_bakeoff.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_side_asymmetry_bridge_strict_repair.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_frozen_side_asymmetry_entry_bridge.py' -TimeoutSeconds 180 | Out-Null
        Invoke-Probe 'probe_v28_side_asymmetry_promotion_runway.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_promotion_runway.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_source_stress.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_approved_oracle_frontier.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_feature_contrast.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_feature_gate_candidate.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_near_promotion_watch.py' | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_near_promotion_exit_attribution.py' | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_live_outcome_alignment.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_live_exit_hold_counterfactual.py' | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_live_exit_mismatch_drilldown.py' | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_exit_state_repair_frontier.py' | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_exit_suppression_separator.py' | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_exit_bid_suppression_watch.py' | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_exit_bid_path_risk.py' | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_exit_bid_delayed_recheck.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_feature_gate_exit_bid_delayed_recheck.py' | Out-Null
        Invoke-Probe 'probe_v28_soft_frontier_midprice_delayed_recheck_exit.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_soft_frontier_midprice_delayed_recheck_exit.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_soft_frontier_midprice_delayed_recheck_rescue.py' | Out-Null
        Invoke-Probe 'probe_v28_soft_frontier_midprice_delayed_recheck_path_risk.py' | Out-Null
        Invoke-Probe 'probe_v28_soft_frontier_delayed_recheck_clean_rescue_path_risk.py' | Out-Null
        Invoke-Probe 'probe_v28_soft_frontier_midprice_delayed_recheck_failure_modes.py' | Out-Null
        Invoke-Probe 'probe_v28_soft_frontier_delayed_recheck_rescue_frontier.py' | Out-Null
        Invoke-Probe 'probe_v28_soft_frontier_delayed_recheck_rescue_path_risk.py' | Out-Null
        Invoke-Probe 'probe_v28_soft_frontier_delayed_recheck_disaster_guard.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_feature_gate_value_exit_watch.py' | Out-Null
        Invoke-Probe 'probe_v28_value_exit_feature_gate_contrast.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_value_exit_feature_side_guard.py' | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_core_expansion_mix.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_feature_gate_runway.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_feature_gate_failure_modes.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_feature_gate_loss_analog_monitor.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_feature_gate_row_ledger.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_feature_gate_coverage_recovery.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_feature_gate_source_denominator_audit.py' | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_source_feasibility_bound.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_feature_gate_coverage_source_frontier.py' -TimeoutSeconds 300 | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_coverage_repair.py' -TimeoutSeconds 240 | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_coverage_size_shrink.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_coverage_size_shrink_exit_attribution.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_coverage_size_shrink_runway.py' | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_observable_selection_mix.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_size_shrink_exit_overlay.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_size_shrink_delayed_recheck_exit.py' -TimeoutSeconds 180 | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_size_shrink_delayed_recheck_rescue.py' -TimeoutSeconds 180 | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_source_confirmation_replacement.py' -TimeoutSeconds 240 | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_late_collapse_recheck_rescue.py' -TimeoutSeconds 180 | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_dual_clock_recheck_rescue.py' -TimeoutSeconds 240 | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_confirmed_dual_clock_fill.py' -TimeoutSeconds 240 | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_confirmed_dual_clock_fill_stress.py' | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_source_quality_proxy.py' -TimeoutSeconds 180 | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_source_proxy_coverage_repair.py' -TimeoutSeconds 180 | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_source_blocker_mechanism.py' -TimeoutSeconds 180 | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_feature_gate_frontier_runway.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_feature_gate_frontier_mechanism.py' -TimeoutSeconds 180 | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_feature_gate_outlier_stress.py' -TimeoutSeconds 90 | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_feature_gate_clean_broad_frontier_watch.py' -TimeoutSeconds 240 | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_feature_gate_soft_frontier_watch.py' -TimeoutSeconds 480 | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_feature_gate_ask_floor_mechanism.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_feature_gate_continuous_penalty.py' -TimeoutSeconds 480 | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_feature_gate_continuous_penalty_stress.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_clock_feature_gate_residual_loss_mechanism.py' | Out-Null
        Invoke-Probe 'probe_v28_soft_frontier_size_shrink_portfolio.py' -TimeoutSeconds 180 | Out-Null
        Invoke-Probe 'probe_v28_soft_frontier_midprice_boundary_shrink_watch.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_soft_frontier_midprice_boundary_source_stress.py' -TimeoutSeconds 30 | Out-Null
        Invoke-Probe 'probe_v28_soft_frontier_midprice_boundary_exit_stack.py' -TimeoutSeconds 30 | Out-Null
        Invoke-Probe 'probe_v28_soft_frontier_midprice_boundary_clip_exit_stack.py' -TimeoutSeconds 30 | Out-Null
        Invoke-Probe 'probe_v28_soft_frontier_midprice_boundary_dual_exit_stack.py' -TimeoutSeconds 30 | Out-Null
        Invoke-Probe 'probe_v28_soft_frontier_midprice_boundary_dual_exit_guard_refinement.py' -TimeoutSeconds 30 | Out-Null
        Invoke-Probe 'probe_v28_midprice_dual_exit_guard_runway.py' -TimeoutSeconds 30 | Out-Null
        Invoke-Probe 'probe_v28_midprice_source_dilution_watch.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_midprice_source_dilution_stability.py' -TimeoutSeconds 60 | Out-Null
        Invoke-Probe 'probe_v28_midprice_source_dilution_mechanism.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_midprice_source_dilution_runway.py' -TimeoutSeconds 60 | Out-Null
        Invoke-Probe 'probe_v28_soft_frontier_midprice_boundary_exit_stack_stress.py' -TimeoutSeconds 30 | Out-Null
        Invoke-Probe 'probe_v28_soft_frontier_midprice_boundary_exit_stack_runway.py' -TimeoutSeconds 30 | Out-Null
        Invoke-Probe 'probe_v28_top_component_mix_portfolio.py' -TimeoutSeconds 240 | Out-Null
        Invoke-Probe 'probe_v28_top_component_loss_cluster_drilldown.py' -TimeoutSeconds 30 | Out-Null
        Invoke-Probe 'probe_v28_top_component_false_negative_rescue_child.py' -TimeoutSeconds 30 | Out-Null
        Invoke-Probe 'probe_v28_top_component_parent_fill_repair_child.py' -TimeoutSeconds 30 | Out-Null
        Invoke-Probe 'probe_v28_top_observable_stack_runway.py' -TimeoutSeconds 30 | Out-Null
        Invoke-Probe 'probe_v28_top_observable_stack_coverage_gap.py' -TimeoutSeconds 30 | Out-Null
        # Heavy guarded-exit stack is refreshed by the dedicated loss-guard loop.
        Invoke-Probe 'probe_v28_boundary_clock_fv_entry_bridge.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_frozen_boundary_clock_fv_entry_bridge.py' | Out-Null
        Invoke-Probe 'probe_v28_target_coverage_fv_edge_gate_diagnostic.py' | Out-Null
        Invoke-Probe 'probe_v28_edge_gate_opposite_side_diagnostic.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_edge_phase_shrink_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_edge_phase_edge_gate.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_edge_gate_opposite_side.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_target_coverage_p70_runway.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_target_coverage_p70_empirical_bayes_runway.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_target_coverage_p70_quality_registry.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_target_coverage_p70_pending_sensitivity.py' | Out-Null
        Invoke-Probe 'probe_v28_live_current_market_attribution.py' | Out-Null
        Invoke-Probe 'probe_v28_live_p70_quality_registry.py' | Out-Null
        Invoke-Probe 'probe_v28_live_collapse_reentry_registry.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_target_coverage_conservative_pending.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_thin_recross_midp_entry_gate.py' | Out-Null
        Invoke-Probe 'probe_v28_boundary_memory_fv_candidates.py' | Out-Null
        Invoke-Probe 'probe_v28_phi_forgetting_fv_candidates.py' | Out-Null
        Invoke-Probe 'probe_v28_reward_memory_fv_candidates.py' | Out-Null
        Invoke-Probe 'probe_v28_reward_memory_jackknife.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_boundary_clock_fv_overlay.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_low_recross_repair_entry.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_boundary_clock_repair_entry.py' | Out-Null
        Invoke-Probe 'probe_v28_fv_candidate_decision_matrix.py' | Out-Null
        Invoke-Probe 'probe_v28_pending_fv_sensitivity.py' -TimeoutSeconds 120 | Out-Null
        Invoke-Probe 'probe_v28_anti_overfit_freeze_audit.py' | Out-Null
        Invoke-Probe 'probe_v28_continuous_scorecard.py' | Out-Null
        Invoke-Probe 'probe_v28_control_risk_stop_audit.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_policy_loss_churn_effect.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_clip_separator_diagnostic.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_exit_clip_separator_watch.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_clip_separator_replay.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_policy_strict_failure_drilldown.py' | Out-Null
        Invoke-Probe 'probe_v28_exit_reduce_suppression_drift_audit.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_exit_reduce_drift_guard_watch.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_exit_midband_reduce_rescue_watch.py' | Out-Null
        Invoke-Probe 'probe_v28_live_trade_readiness.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_candidate_leaderboard.py' | Out-Null
        Invoke-Probe 'probe_v28_candidate_pnl_tracker.py' | Out-Null
        Invoke-Probe 'probe_v28_all_candidates_sorted_by_pnl.py' | Out-Null
        Invoke-Probe 'probe_v28_strict_candidate_runway_frontier.py' | Out-Null
        Invoke-Probe 'probe_v28_top_candidate_mix_match.py' | Out-Null
        Invoke-Probe 'probe_v28_high_win_core_broad_fill_mix.py' | Out-Null
        Invoke-Probe 'probe_v28_dual_lane_overlap_portfolio.py' | Out-Null
        Invoke-Probe 'probe_v28_dual_lane_own_freeze_watch.py' | Out-Null
        Invoke-Probe 'probe_v28_dual_lane_freeze_collection_monitor.py' | Out-Null
        Invoke-Probe 'probe_v28_dual_lane_shadow_feature_preview.py' | Out-Null
        Invoke-Probe 'probe_v28_dual_lane_live_readiness_gate.py' | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_frontier_drift_audit.py' | Out-Null
        Invoke-Probe 'probe_v28_feature_gate_size_shrink_strict_drilldown.py' | Out-Null
        Invoke-Probe 'probe_v28_candidate_registry_coverage_audit.py' | Out-Null
        Invoke-Probe 'probe_v28_candidate_readiness_distance.py' | Out-Null
        Invoke-Probe 'probe_v28_sidecar_live_test_watch.py' | Out-Null
        Invoke-Probe 'probe_v28_continuous_penalty_sidecar_runway.py' | Out-Null
        Invoke-Probe 'probe_v28_controlled_live_test_gate.py' | Out-Null
        Invoke-Probe 'probe_v28_full_policy_candidate_scorecard.py' | Out-Null
        Invoke-Probe 'probe_v28_common_clock_exit_guard_runway.py' | Out-Null
        Invoke-Probe 'probe_v28_common_clock_exit_guard_frontier.py' | Out-Null
        Invoke-Probe 'probe_v28_common_clock_exit_guard_live_test_spec.py' | Out-Null
        Invoke-Probe 'probe_v28_common_clock_exit_guard_implementation_gap.py' | Out-Null
        Invoke-Probe 'probe_v28_common_clock_exit_guard_safety_verifier.py' | Out-Null
        Invoke-Probe 'probe_v28_immediate_live_test_queue.py' | Out-Null
        Invoke-Probe 'probe_v28_end_to_end_strategy_goal_audit.py' | Out-Null
        Invoke-Probe 'probe_v28_top_strict_target_source_fragility.py' -TimeoutSeconds 240 | Out-Null
        Invoke-Probe 'probe_v28_candidate_integrity_scorecard.py' | Out-Null
        Invoke-Probe 'probe_v28_control_risk_candidate_triage.py' | Out-Null
        Invoke-Probe 'probe_v28_candidate_vs_live_table.py' | Out-Null
        Invoke-Probe 'probe_v28_strict_forward_candidate_leaderboard.py' | Out-Null
        Invoke-Probe 'probe_v28_goal_completion_audit.py' | Out-Null
        Invoke-Probe 'probe_v28_current_direction_decision.py' | Out-Null
        Invoke-Probe 'probe_v28_next_action_triage.py' | Out-Null
        Invoke-Probe 'probe_v28_shadow_entry_policy_bakeoff.py' | Out-Null
        Invoke-Probe 'probe_v28_candidate_vs_control_overlap.py' | Out-Null
        Invoke-Probe 'probe_v28_candidate_live_validation_runway.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_p50_book_edge_entry.py' | Out-Null
        Invoke-Probe 'probe_v28_p50_book_edge_source_failure_drilldown.py' | Out-Null
        Invoke-Probe 'probe_v28_p50_book_edge_source_feasibility_bound.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_p50_book_edge_no_side_shrink_watch.py' | Out-Null
        Invoke-Probe 'probe_v28_p50_soft_frontier_overlap_mix.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_book_plus05_entry.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_book_plus05_no_cheap_yes_entry.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_book_edge_fv_calibration.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_recross_book_shrink_fv.py' | Out-Null
        Invoke-Probe 'probe_v28_frozen_book_edge_pending_sensitivity.py' | Out-Null
        Invoke-Probe 'probe_v28_candidate_portfolio_trial_gate.py' | Out-Null
        Invoke-Probe 'probe_v28_policy_fv_matrix.py' | Out-Null
        Invoke-Probe 'probe_v28_policy_failure_modes.py' | Out-Null
        Invoke-Probe 'probe_v28_broad_book_edge_source_audit.py' | Out-Null
        Invoke-Probe 'probe_v28_promotion_readiness.py' | Out-Null
        Invoke-Probe 'probe_v28_candidate_watchlist.py' | Out-Null
        if ($script:probeFailures -gt 0) {
            Add-Content -Path $loopLog -Value "$stamp | status_physics_scorecard_refresh_done_with_failures | failures=$script:probeFailures" -Encoding UTF8
        } else {
            Add-Content -Path $loopLog -Value "$stamp | status_physics_scorecard_refresh_ok" -Encoding UTF8
        }
    } catch {
        Add-Content -Path $loopLog -Value "$stamp | status_refresh_failed | $($_.Exception.Message)" -Encoding UTF8
    }
    Start-Sleep -Seconds ([Math]::Max(10, $IntervalSeconds))
}
