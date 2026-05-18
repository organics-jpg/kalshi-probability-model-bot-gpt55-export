$ErrorActionPreference = 'Stop'

param(
    [string]$StorageTag = 'live_90_78',
    [switch]$KeepTradedMarkets
)

$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$stateDir = Join-Path $repo ("state\$StorageTag")
$statePath = Join-Path $stateDir 'bot_state.json'
$lockPath = Join-Path $repo 'state\live_trading.lock'

if (-not (Test-Path $stateDir)) {
    throw "State directory not found for storage tag '$StorageTag'."
}

if (Test-Path $statePath) {
    $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $backupPath = Join-Path $stateDir ("bot_state.backup_$timestamp.json")
    Copy-Item $statePath $backupPath -Force
    $state = Get-Content $statePath -Raw -Encoding UTF8 | ConvertFrom-Json
} else {
    $state = [pscustomobject]@{ pending_order = $null; position = $null; traded_markets = @() }
}

if (-not ($state.PSObject.Properties.Name -contains 'pending_order')) {
    $state | Add-Member -NotePropertyName pending_order -NotePropertyValue $null
}
if (-not ($state.PSObject.Properties.Name -contains 'position')) {
    $state | Add-Member -NotePropertyName position -NotePropertyValue $null
}
if (-not ($state.PSObject.Properties.Name -contains 'traded_markets')) {
    $state | Add-Member -NotePropertyName traded_markets -NotePropertyValue @()
}

$state.pending_order = $null
$state.position = $null
if (-not $KeepTradedMarkets) {
    $state.traded_markets = @()
}

$json = $state | ConvertTo-Json -Depth 8
[System.IO.File]::WriteAllText($statePath, $json, [System.Text.UTF8Encoding]::new($false))

if (Test-Path $lockPath) {
    Remove-Item $lockPath -Force
}

Write-Host "Reset clean-copy bot state for '$StorageTag'."
Write-Host "Position cleared: yes"
Write-Host "Pending order cleared: yes"
Write-Host "Traded markets kept: $KeepTradedMarkets"
