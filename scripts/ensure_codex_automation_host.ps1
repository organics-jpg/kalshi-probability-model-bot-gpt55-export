$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$logDir = Join-Path $repoRoot 'logs\edge_research'
$logPath = Join-Path $logDir 'codex_automation_host_watchdog.log'
$appId = 'OpenAI.Codex_2p2nqsd0c76g0!App'

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Write-WatchdogLog {
    param([string]$Message)
    $ts = [DateTimeOffset]::Now.ToString('yyyy-MM-ddTHH:mm:sszzz')
    Add-Content -LiteralPath $logPath -Value "$ts $Message" -Encoding UTF8
}

$codexProcesses = @(Get-Process -Name 'Codex' -ErrorAction SilentlyContinue)
if ($codexProcesses.Count -gt 0) {
    $pids = ($codexProcesses | Select-Object -ExpandProperty Id) -join ','
    Write-WatchdogLog "Codex running; pid=$pids"
    exit 0
}

Write-WatchdogLog "Codex not running; launching app_id=$appId"
Start-Process -FilePath 'explorer.exe' -ArgumentList "shell:AppsFolder\$appId"
Start-Sleep -Seconds 15

$afterLaunch = @(Get-Process -Name 'Codex' -ErrorAction SilentlyContinue)
if ($afterLaunch.Count -gt 0) {
    $pids = ($afterLaunch | Select-Object -ExpandProperty Id) -join ','
    Write-WatchdogLog "Codex launch verified; pid=$pids"
    exit 0
}

Write-WatchdogLog "WARN Codex launch attempted but no Codex process found after 15s"
exit 1
