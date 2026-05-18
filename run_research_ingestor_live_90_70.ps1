$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
$python = Join-Path $scriptDir 'venv\Scripts\python.exe'
if (-not (Test-Path $python)) { $python = 'python' }
& $python '.\research_ingestor.py' --dataset live_90_70 --watch --interval-seconds 300
