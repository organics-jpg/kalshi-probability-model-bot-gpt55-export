$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
$venvDir = Join-Path $scriptDir 'venv'
$venvPython = Join-Path $venvDir 'Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    python -m venv $venvDir
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not create .\venv. Confirm Python is available on PATH.'
    }
}
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install --upgrade -r .\dashboard_requirements.txt
Write-Host "Dashboard dependencies installed."
