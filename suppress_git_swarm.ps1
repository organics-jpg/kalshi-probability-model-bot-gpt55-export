$ErrorActionPreference = 'SilentlyContinue'

$deadline = (Get-Date).AddMinutes(30)
while ((Get-Date) -lt $deadline) {
    Get-Process git | Stop-Process -Force
    Start-Sleep -Milliseconds 500
}
