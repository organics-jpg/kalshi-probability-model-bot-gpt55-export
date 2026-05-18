$ErrorActionPreference = 'Continue'

$logPath = Join-Path $PSScriptRoot 'logs\live_87_77_67\bot.log'

if (-not (Test-Path $logPath)) {
    Write-Host "Log not found: $logPath" -ForegroundColor Red
    exit 1
}

$host.UI.RawUI.WindowTitle = 'BTC Heartbeats Only'
Write-Host "Heartbeat-only tail: $logPath" -ForegroundColor Cyan

$pattern = 'Heartbeat \||Watching market|Starting WS bot|ENTRY signal|ENTRY immediate fill|EXIT signal|EXIT immediate fill|WS connected|Orderbook snapshot ready'

Get-Content -Path $logPath -Tail 40 -Wait | ForEach-Object {
    if ($_ -match $pattern) {
        $_
    }
}
