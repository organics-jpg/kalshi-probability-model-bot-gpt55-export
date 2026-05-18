param(
    [int]$MaxHeartbeatAgeMinutes = 10,
    [string]$SourceWorkspace = '',
    [switch]$CheckOnly
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoDir = Split-Path -Parent $scriptDir
$launcher = Join-Path $scriptDir 'run_mushroom_v21_live_size1.ps1'
$storageTag = 'live_mushroom_v21_physical_size1'
$expectedStrategyTag = 'mushroom_v21_physical_size1_live_test'
$botScript = 'kalshi_btc15m_bot_ws.py'
$logDir = Join-Path $repoDir "logs\$storageTag"
$botLog = Join-Path $logDir 'bot.log'
$monitorLog = Join-Path $logDir 'hourly_monitor.log'
$liveLock = Join-Path $repoDir 'state\live_trading.lock'

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Write-MonitorLog {
    param([string]$Message)
    $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'
    $line = "$stamp | $Message"
    Add-Content -Path $monitorLog -Value $line -Encoding UTF8
    Write-Output $line
}

function Get-LiveLock {
    if (-not (Test-Path $liveLock)) {
        return $null
    }
    try {
        return Get-Content -Path $liveLock -Raw | ConvertFrom-Json
    } catch {
        [void](Write-MonitorLog "LOCK_READ_FAILED | path=$liveLock error=$($_.Exception.Message)")
        return $null
    }
}

function Test-PidRunning {
    param([int]$ProcessId)
    if ($ProcessId -le 0) {
        return $false
    }
    try {
        $proc = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        return $null -ne $proc
    } catch {
        [void](Write-MonitorLog "PROCESS_CHECK_DENIED | pid=$ProcessId error=$($_.Exception.Message)")
        return $null
    }
}

function Resolve-SourceWorkspace {
    if ($SourceWorkspace) {
        return $SourceWorkspace
    }
    if (Test-Path (Join-Path $repoDir '.env')) {
        return $repoDir
    }
    return 'C:\Users\organ\Desktop\KALSHI + TRUFFLE BOT'
}

function Start-LiveBot {
    $resolvedSource = Resolve-SourceWorkspace
    if (-not (Test-Path $launcher)) {
        throw "Missing launcher: $launcher"
    }
    if (-not (Test-Path (Join-Path $resolvedSource '.env'))) {
        throw "Missing .env in source workspace: $resolvedSource"
    }

    $argString = "-NoProfile -ExecutionPolicy Bypass -File `"$launcher`" -SourceWorkspace `"$resolvedSource`""
    Write-MonitorLog "START requested | launcher=$launcher source_workspace=$resolvedSource"
    Start-Process -FilePath 'powershell.exe' -ArgumentList $argString -WorkingDirectory $repoDir -WindowStyle Hidden
}

$now = Get-Date
$heartbeatAge = $null
$heartbeatOk = $false

if (Test-Path $botLog) {
    $lastWrite = (Get-Item $botLog).LastWriteTime
    $heartbeatAge = ($now - $lastWrite).TotalMinutes
    $heartbeatOk = $heartbeatAge -le $MaxHeartbeatAgeMinutes
}

$lock = Get-LiveLock
$lockPid = 0
$lockStrategy = ''
if ($lock) {
    $lockPid = [int]($lock.pid -as [int])
    $lockStrategy = [string]($lock.strategy_tag)
}
$strategyOk = $lockStrategy -eq $expectedStrategyTag
$pidStatus = if ($lockPid -gt 0) { Test-PidRunning -ProcessId $lockPid } else { $false }
$pidRunning = $pidStatus -eq $true
$pidUnverified = $null -eq $pidStatus
$processOk = $strategyOk -and ($pidRunning -or ($pidUnverified -and $heartbeatOk))

if ($processOk -and $heartbeatOk) {
    $processState = if ($pidRunning) { 'running' } else { 'unverified' }
    Write-MonitorLog ("OK | pid={0} process={1} heartbeat_age_min={2:N2}" -f $lockPid, $processState, $heartbeatAge)
    exit 0
}

$reasonParts = @()
if (-not $lock) {
    $reasonParts += 'missing_live_lock'
} elseif (-not $strategyOk) {
    $reasonParts += "wrong_live_lock_strategy_$lockStrategy"
}
if ($lockPid -le 0) {
    $reasonParts += 'missing_lock_pid'
} elseif ($pidUnverified) {
    $reasonParts += 'process_unverified'
} elseif (-not $pidRunning) {
    $reasonParts += "pid_not_running_$lockPid"
}
if (-not $heartbeatOk) {
    if ($heartbeatAge -eq $null) {
        $reasonParts += 'missing_bot_log'
    } else {
        $reasonParts += ("stale_bot_log_{0:N2}min" -f $heartbeatAge)
    }
}
$reason = $reasonParts -join ','
Write-MonitorLog "UNHEALTHY | reason=$reason pid=$lockPid"

if ($CheckOnly) {
    Write-MonitorLog 'CHECK_ONLY | restart skipped'
    exit 2
}

if ($lockPid -gt 0 -and -not $strategyOk) {
    Write-MonitorLog "REFUSE_RESTART | other_live_strategy_present strategy=$lockStrategy pid=$lockPid"
    exit 3
}

if ($lockPid -gt 0) {
    try {
        Write-MonitorLog "STOP stale bot process | pid=$lockPid"
        Stop-Process -Id $lockPid -Force -ErrorAction Stop
    } catch {
        Write-MonitorLog "STOP failed | pid=$lockPid error=$($_.Exception.Message)"
    }
}

Start-LiveBot
Start-Sleep -Seconds 8

$newLock = Get-LiveLock
$newPid = if ($newLock) { [int]($newLock.pid -as [int]) } else { 0 }
$newPidStatus = if ($newPid -gt 0) { Test-PidRunning -ProcessId $newPid } else { $false }
$newHeartbeatOk = $false
if (Test-Path $botLog) {
    $newHeartbeatOk = ((Get-Date) - (Get-Item $botLog).LastWriteTime).TotalMinutes -le $MaxHeartbeatAgeMinutes
}
if ($newPid -gt 0 -and ($newPidStatus -eq $true -or ($null -eq $newPidStatus -and $newHeartbeatOk)) -and $newHeartbeatOk) {
    $newProcessState = if ($newPidStatus -eq $true) { 'running' } else { 'unverified' }
    Write-MonitorLog "RESTARTED | pid=$newPid process=$newProcessState"
    exit 0
}

Write-MonitorLog 'RESTART_FAILED | no live bot process detected after launch'
exit 1
