$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repo

$stdout = Join-Path $repo "logs\edge_research\live_liquidity_dwell_size2_log_backfill_watcher.stdout.log"
$stderr = Join-Path $repo "logs\edge_research\live_liquidity_dwell_size2_log_backfill_watcher.stderr.log"
$python = "C:\Python312\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    $python = "python"
}

& $python ".\research_live_bot_log_backfill.py" `
    --dataset "live_liquidity_dwell_size2" `
    --storage-tag "live_liquidity_dwell_size2" `
    --watch `
    --interval-seconds 30 `
    >> $stdout 2>> $stderr
