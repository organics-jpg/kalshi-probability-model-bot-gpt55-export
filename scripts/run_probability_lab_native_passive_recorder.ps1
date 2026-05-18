param(
    [string]$DatasetTag = 'live_mushroom_v21_size2',
    [string]$StrategyTag = 'mushroom_v21_broad_p80_edge2_size2',
    [string]$BotTag = 'live_mushroom_v21_size2',
    [string]$SourceWorkspace = 'C:\Users\organ\Desktop\KALSHI + TRUFFLE BOT'
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoDir = Split-Path -Parent $scriptDir
Set-Location $repoDir

function Import-DotEnv {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        throw "Missing source .env: $Path"
    }
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith('#') -or -not $line.Contains('=')) {
            return
        }
        $parts = $line.Split('=', 2)
        $name = $parts[0].Trim()
        $value = $parts[1].Trim().Trim('"').Trim("'")
        if ($name) {
            [Environment]::SetEnvironmentVariable($name, $value, 'Process')
        }
    }
}

Import-DotEnv (Join-Path $SourceWorkspace '.env')
if ($env:KALSHI_PRIVATE_KEY_PATH -and -not [System.IO.Path]::IsPathRooted($env:KALSHI_PRIVATE_KEY_PATH)) {
    $env:KALSHI_PRIVATE_KEY_PATH = Join-Path $SourceWorkspace $env:KALSHI_PRIVATE_KEY_PATH
}

$python = Join-Path $repoDir 'venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    $python = 'python'
}

& $python '.\research_native_passive_ws_recorder.py' --dataset $DatasetTag --strategy-tag $StrategyTag --bot-tag $BotTag --market-refresh-seconds 10
