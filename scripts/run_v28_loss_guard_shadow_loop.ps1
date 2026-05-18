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

$logDir = Join-Path $repoDir 'logs\edge_research'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$loopLog = Join-Path $logDir 'v28_loss_guard_shadow_loop.log'
$probeTimeoutSeconds = 45

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
        return $false
    }
    if ($proc.ExitCode -ne 0) {
        $failStamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'
        Add-Content -Path $loopLog -Value "$failStamp | probe_failed | $ProbeName | exit_code=$($proc.ExitCode)" -Encoding UTF8
        return $false
    }
    return $true
}

while ($true) {
    $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'
    try {
        $failures = 0
        foreach ($probe in @(
            'probe_v28_frozen_exit_book_gap_loss_guard.py',
            'probe_v28_frozen_exit_book_gap_loss_guard_v2.py',
            'probe_v28_frozen_exit_book_gap_loss_guard_v3.py',
            'probe_v28_frozen_exit_book_gap_value_only.py',
            @{ Name = 'probe_v28_frozen_exit_value_reduce_depth_composite.py'; TimeoutSeconds = 120 },
            'probe_v28_frozen_exit_reduce_observable_loss_control_watch.py',
            'probe_v28_exit_reduce_observable_loss_control_opportunity.py',
            'probe_v28_exit_value_reduce_depth_opportunity.py',
            'probe_v28_exit_book_gap_loss_guard_v2_opportunity.py',
            'probe_v28_exit_book_gap_loss_guard_v3_opportunity.py',
            'probe_v28_exit_loss_guard_v1_v2_contrast.py',
            'probe_v28_exit_loss_guard_v1_v2_v3_contrast.py',
            'probe_v28_shadow_observation_availability.py',
            'probe_v28_exit_policy_common_clock_watch.py',
            'probe_v28_exit_policy_strict_failure_drilldown.py',
            'probe_v28_frozen_dual_exit_book_gap_else_reduce.py',
            @{ Name = 'probe_v28_frozen_feature_gate_book_gap_exit_stack.py'; TimeoutSeconds = 180 },
            @{ Name = 'probe_v28_frozen_feature_gate_soft_frontier_exit_stack.py'; TimeoutSeconds = 180 },
            # Heavy on-demand report; keep out of the high-frequency loop until it is cached.
            # 'probe_v28_feature_gate_cheap_tail_quarantine.py',
            'probe_v28_candidate_pnl_tracker.py',
            'probe_v28_candidate_readiness_distance.py',
            'probe_v28_sidecar_live_test_watch.py',
            'probe_v28_top_candidate_mix_match.py',
            'probe_v28_control_risk_stop_audit.py',
            'probe_v28_exit_policy_loss_churn_effect.py',
            'probe_v28_live_loss_escape_analysis.py',
            'probe_live_v28_exit_value_audit.py',
            'probe_live_v28_probability_collapse_branch_audit.py',
            'probe_live_v28_collapse_suppress_shadow_monitor.py',
            'probe_v28_live_collapse_reentry_registry.py',
            'probe_v28_current_direction_decision.py',
            'probe_v28_next_action_triage.py',
            'probe_v28_goal_completion_audit.py'
        )) {
            if ($probe -is [hashtable]) {
                $ok = Invoke-Probe $probe.Name -TimeoutSeconds $probe.TimeoutSeconds
            } else {
                $ok = Invoke-Probe $probe
            }
            if (-not $ok) {
                $failures += 1
            }
        }
        if ($failures -gt 0) {
            Add-Content -Path $loopLog -Value "$stamp | loss_guard_refresh_done_with_failures | failures=$failures" -Encoding UTF8
        } else {
            Add-Content -Path $loopLog -Value "$stamp | loss_guard_refresh_ok" -Encoding UTF8
        }
    } catch {
        Add-Content -Path $loopLog -Value "$stamp | loss_guard_refresh_failed | $($_.Exception.Message)" -Encoding UTF8
    }
    Start-Sleep -Seconds ([Math]::Max(10, $IntervalSeconds))
}
