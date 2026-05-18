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
$loopLog = Join-Path $logDir 'v28_exit_guard_v2_loop.log'
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
            'probe_v28_frozen_exit_book_gap_loss_guard_v2.py',
            'probe_v28_exit_book_gap_loss_guard_v2_opportunity.py',
            'probe_v28_exit_loss_guard_v1_v2_contrast.py',
            'probe_v28_shadow_observation_availability.py',
            'probe_v28_exit_policy_common_clock_watch.py',
            'probe_v28_candidate_pnl_tracker.py',
            'probe_v28_candidate_integrity_scorecard.py',
            'probe_v28_top_candidate_mix_match.py',
            'probe_v28_current_direction_decision.py',
            'probe_v28_next_action_triage.py',
            'probe_v28_goal_completion_audit.py'
        )) {
            if (-not (Invoke-Probe $probe)) {
                $failures += 1
            }
        }
        if ($failures -gt 0) {
            Add-Content -Path $loopLog -Value "$stamp | exit_guard_v2_refresh_done_with_failures | failures=$failures" -Encoding UTF8
        } else {
            Add-Content -Path $loopLog -Value "$stamp | exit_guard_v2_refresh_ok" -Encoding UTF8
        }
    } catch {
        Add-Content -Path $loopLog -Value "$stamp | exit_guard_v2_refresh_failed | $($_.Exception.Message)" -Encoding UTF8
    }
    Start-Sleep -Seconds ([Math]::Max(10, $IntervalSeconds))
}
