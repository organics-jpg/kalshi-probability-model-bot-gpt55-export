$ErrorActionPreference = 'Stop'

if (-not (Test-Path .\venv)) {
    py -m venv .\venv
}

.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r .\requirements.txt

if (-not (Test-Path .\.env)) {
    Copy-Item .\.env.example .\.env
}

if (-not (Test-Path .\secrets\kalshi_private_key.pem)) {
    Copy-Item .\secrets\kalshi_private_key.example.pem .\secrets\kalshi_private_key.pem
}

Write-Host "Setup complete. Edit .env and secrets\kalshi_private_key.pem before running."
