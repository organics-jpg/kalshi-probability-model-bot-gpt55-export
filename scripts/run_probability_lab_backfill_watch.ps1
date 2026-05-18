param(
    [string]$DatasetTag = 'live_liquidity_dwell_size2',
    [string]$StorageTag = 'live_liquidity_dwell_size2',
    [int]$IntervalSeconds = 30
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoDir = Split-Path -Parent $scriptDir
Set-Location $repoDir

$python = Join-Path $repoDir 'venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    $python = 'python'
}

& $python '.\research_live_bot_log_backfill.py' --dataset $DatasetTag --storage-tag $StorageTag --watch --interval-seconds $IntervalSeconds
