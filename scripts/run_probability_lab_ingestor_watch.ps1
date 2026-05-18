param(
    [string]$DatasetTag = 'live_mushroom_v21_size2',
    [int]$IntervalSeconds = 300
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoDir = Split-Path -Parent $scriptDir
Set-Location $repoDir

$python = Join-Path $repoDir 'venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    $python = 'python'
}

& $python '.\research_ingestor.py' --dataset $DatasetTag --watch --interval-seconds $IntervalSeconds
