param(
    [int]$IntervalSeconds = 60,
    [int]$LiveRefreshEveryCycles = 5
)

$ErrorActionPreference = "Continue"
$repo = Split-Path -Parent $PSScriptRoot
$logDir = Join-Path $repo "logs\edge_research"
$loopLog = Join-Path $logDir "v28_dual_lane_watch_loop.log"

New-Item -ItemType Directory -Force -Path $logDir | Out-Null
Set-Location $repo

function Add-LoopLog {
    param([string]$Message)
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"
    Add-Content -Path $loopLog -Value "$stamp | $Message" -Encoding UTF8
}

function Invoke-DualProbe {
    param(
        [string]$ScriptName,
        [int]$TimeoutSeconds = 90
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
        Add-LoopLog "probe_timeout | $ScriptName"
        return $false
    }
    $stderr = $proc.StandardError.ReadToEnd()
    $elapsed = [math]::Round(((Get-Date) - $start).TotalSeconds, 2)
    if ($proc.ExitCode -ne 0) {
        $err = ($stderr -replace "\s+", " ").Trim()
        Add-LoopLog "probe_failed | $ScriptName | exit=$($proc.ExitCode) | elapsed_s=$elapsed | stderr=$err"
        return $false
    }
    Add-LoopLog "probe_ok | $ScriptName | elapsed_s=$elapsed"
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
        Invoke-DualProbe -ScriptName "score_bot_log.py" -TimeoutSeconds 120 | Out-Null
    } finally {
        $env:OUTPUT_STRATEGY_TAG = $oldOutput
        $env:LOG_SOURCE_TAG = $oldSource
        $env:SCORE_MODE = $oldMode
    }
}

Add-LoopLog "dual_lane_watch_loop_started | interval_seconds=$IntervalSeconds | live_refresh_every_cycles=$LiveRefreshEveryCycles"
$cycle = 0

while ($true) {
    $cycle += 1
    Add-LoopLog "cycle_start | cycle=$cycle"
    if ($LiveRefreshEveryCycles -gt 0 -and (($cycle -eq 1) -or (($cycle - 1) % $LiveRefreshEveryCycles -eq 0))) {
        Invoke-LiveBaselineRefresh
    }
    Invoke-DualProbe -ScriptName "probe_v28_dual_lane_own_freeze_watch.py" -TimeoutSeconds 900 | Out-Null
    Invoke-DualProbe -ScriptName "probe_v28_dual_lane_freeze_collection_monitor.py" -TimeoutSeconds 180 | Out-Null
    Invoke-DualProbe -ScriptName "probe_v28_dual_lane_shadow_feature_preview.py" -TimeoutSeconds 180 | Out-Null
    Invoke-DualProbe -ScriptName "probe_v28_dual_lane_live_readiness_gate.py" -TimeoutSeconds 60 | Out-Null
    Invoke-DualProbe -ScriptName "probe_v28_dual_lane_live_readiness_runway.py" -TimeoutSeconds 60 | Out-Null
    Invoke-DualProbe -ScriptName "probe_v28_dual_lane_proxy_mechanism_audit.py" -TimeoutSeconds 60 | Out-Null
    Invoke-DualProbe -ScriptName "probe_v28_dual_lane_live_market_update.py" -TimeoutSeconds 60 | Out-Null
    Invoke-DualProbe -ScriptName "probe_v28_dual_lane_readiness_checklist.py" -TimeoutSeconds 60 | Out-Null
    Add-LoopLog "cycle_done | cycle=$cycle"
    Start-Sleep -Seconds $IntervalSeconds
}
