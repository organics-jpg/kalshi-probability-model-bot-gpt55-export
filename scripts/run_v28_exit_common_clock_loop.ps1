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
$loopLog = Join-Path $logDir 'v28_exit_common_clock_loop.log'

while ($true) {
    $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'
    try {
        $probePath = Join-Path $repoDir 'probe_v28_exit_policy_common_clock_watch.py'
        $proc = Start-Process -FilePath $python -ArgumentList @("`"$probePath`"") -WindowStyle Hidden -PassThru
        Wait-Process -Id $proc.Id -Timeout 45 -ErrorAction SilentlyContinue
        $stillRunning = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
        if ($stillRunning) {
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            Add-Content -Path $loopLog -Value "$stamp | common_clock_probe_timeout" -Encoding UTF8
        } elseif ($proc.ExitCode -ne 0) {
            Add-Content -Path $loopLog -Value "$stamp | common_clock_probe_failed | exit_code=$($proc.ExitCode)" -Encoding UTF8
        } else {
            Add-Content -Path $loopLog -Value "$stamp | common_clock_refresh_ok" -Encoding UTF8
        }
    } catch {
        Add-Content -Path $loopLog -Value "$stamp | common_clock_refresh_failed | $($_.Exception.Message)" -Encoding UTF8
    }
    Start-Sleep -Seconds ([Math]::Max(10, $IntervalSeconds))
}
