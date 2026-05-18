param(
    [int]$Iterations = 100000,
    [int]$SleepSeconds = 75,
    [int]$MaxMarkets = 80
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoDir = Split-Path -Parent $scriptDir
Set-Location $repoDir

$python = Join-Path $repoDir 'venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    $python = 'python'
}

& $python '.\run_v28_successor_market_coverage_loop.py' `
    --collect-mode public-rest `
    --all-open-closes `
    --iterations $Iterations `
    --sleep-seconds $SleepSeconds `
    --max-markets $MaxMarkets `
    --write
