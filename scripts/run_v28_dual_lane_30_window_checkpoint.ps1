param(
    [switch]$RunStrictPrecheck
)

$ErrorActionPreference = "Continue"
$repo = Split-Path -Parent $PSScriptRoot
$logDir = Join-Path $repo "logs\edge_research"
$checkpointLog = Join-Path $logDir "v28_dual_lane_30_window_checkpoint.log"

New-Item -ItemType Directory -Force -Path $logDir | Out-Null
Set-Location $repo

function Add-CheckpointLog {
    param([string]$Message)
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"
    Add-Content -Path $checkpointLog -Value "$stamp | $Message" -Encoding UTF8
}

function Invoke-CheckpointProbe {
    param(
        [string]$ScriptName,
        [int]$TimeoutSeconds = 120
    )
    $start = Get-Date
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "python"
    $psi.Arguments = ".\$ScriptName"
    $psi.WorkingDirectory = $repo
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $proc = [System.Diagnostics.Process]::Start($psi)
    if (-not $proc.WaitForExit($TimeoutSeconds * 1000)) {
        try { $proc.Kill() } catch {}
        Add-CheckpointLog "probe_timeout | $ScriptName"
        return $false
    }
    $stderr = $proc.StandardError.ReadToEnd()
    $stdout = $proc.StandardOutput.ReadToEnd()
    $elapsed = [math]::Round(((Get-Date) - $start).TotalSeconds, 2)
    if ($proc.ExitCode -ne 0) {
        $err = ($stderr -replace "\s+", " ").Trim()
        Add-CheckpointLog "probe_failed | $ScriptName | exit=$($proc.ExitCode) | elapsed_s=$elapsed | stderr=$err"
        return $false
    }
    $out = ($stdout -replace "\s+", " ").Trim()
    Add-CheckpointLog "probe_ok | $ScriptName | elapsed_s=$elapsed | stdout=$out"
    return $true
}

function Invoke-LiveBaselineRefresh {
    $oldOutput = $env:OUTPUT_STRATEGY_TAG
    $oldSource = $env:LOG_SOURCE_TAG
    $oldMode = $env:SCORE_MODE
    try {
        $env:OUTPUT_STRATEGY_TAG = "live_mushroom_v28_size2"
        $env:LOG_SOURCE_TAG = "live_mushroom_v28_size2"
        $env:SCORE_MODE = "live_only"
        Invoke-CheckpointProbe -ScriptName "score_bot_log.py" -TimeoutSeconds 180 | Out-Null
    } finally {
        $env:OUTPUT_STRATEGY_TAG = $oldOutput
        $env:LOG_SOURCE_TAG = $oldSource
        $env:SCORE_MODE = $oldMode
    }
}

Add-CheckpointLog "checkpoint_started | run_strict_precheck=$RunStrictPrecheck"
Invoke-LiveBaselineRefresh
Invoke-CheckpointProbe -ScriptName "probe_v28_dual_lane_own_freeze_watch.py" -TimeoutSeconds 900 | Out-Null
Invoke-CheckpointProbe -ScriptName "probe_v28_dual_lane_live_readiness_gate.py" -TimeoutSeconds 120 | Out-Null
Invoke-CheckpointProbe -ScriptName "probe_v28_dual_lane_live_readiness_runway.py" -TimeoutSeconds 120 | Out-Null
Invoke-CheckpointProbe -ScriptName "probe_v28_dual_lane_freeze_collection_monitor.py" -TimeoutSeconds 240 | Out-Null
Invoke-CheckpointProbe -ScriptName "probe_v28_dual_lane_shadow_feature_preview.py" -TimeoutSeconds 240 | Out-Null
Invoke-CheckpointProbe -ScriptName "probe_v28_dual_lane_proxy_mechanism_audit.py" -TimeoutSeconds 120 | Out-Null
Invoke-CheckpointProbe -ScriptName "probe_v28_dual_lane_loss_bottleneck_audit.py" -TimeoutSeconds 120 | Out-Null
Invoke-CheckpointProbe -ScriptName "probe_v28_dual_lane_parent_shrink_watch.py" -TimeoutSeconds 900 | Out-Null
Invoke-CheckpointProbe -ScriptName "probe_v28_dual_lane_parent_shrink_frontier_watch.py" -TimeoutSeconds 900 | Out-Null

if ($RunStrictPrecheck) {
    Invoke-CheckpointProbe -ScriptName "probe_v28_dual_lane_strict_replay_precheck.py" -TimeoutSeconds 900 | Out-Null
    Invoke-CheckpointProbe -ScriptName "probe_v28_dual_lane_strict_replay_accounting_audit.py" -TimeoutSeconds 120 | Out-Null
    Invoke-CheckpointProbe -ScriptName "probe_v28_dual_lane_variant_contrast.py" -TimeoutSeconds 120 | Out-Null
    Invoke-CheckpointProbe -ScriptName "probe_v28_dual_lane_parent_shrink_repair_precheck.py" -TimeoutSeconds 900 | Out-Null
    Invoke-CheckpointProbe -ScriptName "probe_v28_dual_lane_parent_shrink_frontier_precheck.py" -TimeoutSeconds 900 | Out-Null
}

Invoke-CheckpointProbe -ScriptName "probe_v28_dual_lane_live_market_update.py" -TimeoutSeconds 120 | Out-Null
Invoke-CheckpointProbe -ScriptName "probe_v28_dual_lane_readiness_checklist.py" -TimeoutSeconds 120 | Out-Null
Invoke-CheckpointProbe -ScriptName "probe_v28_dual_lane_snapshot_ledger.py" -TimeoutSeconds 120 | Out-Null
Invoke-CheckpointProbe -ScriptName "probe_v28_dual_lane_live_ready_handoff.py" -TimeoutSeconds 120 | Out-Null

Add-CheckpointLog "checkpoint_done"
Write-Host "Wrote $checkpointLog"
Write-Host "Read logs\\edge_research\\v28_dual_lane_live_ready_handoff_latest.md"
