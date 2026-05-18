$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
$venvPython = Join-Path $scriptDir 'venv\Scripts\python.exe'
$dashboard = Join-Path $scriptDir 'dashboard.py'
$python = $venvPython
if (-not (Test-Path $python)) {
    $python = 'python'
}
& $python -c "import streamlit" 2>$null
if ($LASTEXITCODE -ne 0) {
    throw 'Streamlit is not available. Run .\setup_dashboard.ps1 first.'
}
& $python -m streamlit run $dashboard --server.address 127.0.0.1 --server.port 8501
