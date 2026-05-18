param(
    [int]$IntervalSeconds = 60
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$logDir = Join-Path $root "logs\edge_research"
$logPath = Join-Path $logDir "v28_dual_lane_overlay_v2_loop.log"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Write-LoopLog {
    param([string]$Message)
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"
    "$stamp | $Message" | Tee-Object -FilePath $logPath -Append | Out-Null
}

Write-LoopLog "dual_lane_overlay_v2_loop_started | interval_seconds=$IntervalSeconds"
$cycle = 0
while ($true) {
    $cycle += 1
    Write-LoopLog "cycle_start | cycle=$cycle"
    foreach ($probe in @(
        "probe_v28_dual_lane_overlay_filter_frontier.py",
        "probe_v28_dual_lane_overlay_filter_v2_watch.py",
        "probe_v28_dual_lane_overlay_v2_same_window_compare.py",
        "probe_v28_dual_lane_overlay_v2_readiness.py"
    )) {
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        try {
            Push-Location $root
            python ".\$probe" | Out-Null
            Pop-Location
            $sw.Stop()
            Write-LoopLog "probe_ok | $probe | elapsed_s=$([math]::Round($sw.Elapsed.TotalSeconds, 2))"
        } catch {
            try { Pop-Location } catch {}
            $sw.Stop()
            Write-LoopLog "probe_error | $probe | elapsed_s=$([math]::Round($sw.Elapsed.TotalSeconds, 2)) | $($_.Exception.Message)"
        }
    }
    Write-LoopLog "cycle_done | cycle=$cycle"
    Start-Sleep -Seconds $IntervalSeconds
}
