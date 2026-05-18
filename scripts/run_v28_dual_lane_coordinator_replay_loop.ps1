param(
    [int]$IntervalSeconds = 60
)

$ErrorActionPreference = "Continue"
$repo = Split-Path -Parent $PSScriptRoot
$logDir = Join-Path $repo "logs\edge_research"
$loopLog = Join-Path $logDir "v28_dual_lane_coordinator_replay_loop.log"

New-Item -ItemType Directory -Force -Path $logDir | Out-Null
Set-Location $repo

function Add-LoopLog {
    param([string]$Message)
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"
    Add-Content -Path $loopLog -Value "$stamp | $Message" -Encoding UTF8
}

function Invoke-CoordinatorProbe {
    param(
        [string]$ScriptName,
        [int]$TimeoutSeconds = 60
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

Add-LoopLog "dual_lane_coordinator_replay_loop_started | interval_seconds=$IntervalSeconds"
$cycle = 0

while ($true) {
    $cycle += 1
    Add-LoopLog "cycle_start | cycle=$cycle"
    Invoke-CoordinatorProbe -ScriptName "probe_v28_dual_lane_same_window_live_compare.py" -TimeoutSeconds 60 | Out-Null
    Invoke-CoordinatorProbe -ScriptName "probe_v28_dual_lane_paper_coordinator_replay.py" -TimeoutSeconds 60 | Out-Null
    Invoke-CoordinatorProbe -ScriptName "probe_v28_dual_lane_live_test_blocker_audit.py" -TimeoutSeconds 60 | Out-Null
    Invoke-CoordinatorProbe -ScriptName "probe_v28_dual_lane_live_test_coordinator_spec.py" -TimeoutSeconds 60 | Out-Null
    Invoke-CoordinatorProbe -ScriptName "probe_v28_dual_lane_live_ready_handoff.py" -TimeoutSeconds 60 | Out-Null
    Add-LoopLog "cycle_done | cycle=$cycle"
    Start-Sleep -Seconds $IntervalSeconds
}
