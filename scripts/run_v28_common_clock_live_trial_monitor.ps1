param(
    [string]$StrategyTag = 'mushroom_v28_common_clock_exit_guard_v1_size1_live',
    [string]$LogSourceTag = 'live_mushroom_v28_common_clock_exit_guard_size1',
    [int]$IntervalSeconds = 60,
    [int]$MaxLossCluster = 3,
    [int]$MaxDrawdownCents = 200,
    [int]$MaxZeroFillCount = 3,
    [int]$MinSourceRejectEvents = 100,
    [double]$MaxSourceStaleRejectShare = 0.70
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoDir = Split-Path -Parent $scriptDir
Set-Location $repoDir

$python = Join-Path $repoDir 'venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    $python = 'python'
}

$strategyTag = $StrategyTag
$logSourceTag = $LogSourceTag
$safeStrategyTag = ($strategyTag -replace '[^A-Za-z0-9_.-]', '_')
$logDir = Join-Path $repoDir "logs\$logSourceTag"
$statsDir = Join-Path $repoDir "stats\$strategyTag"
$stateDir = Join-Path $repoDir "state\$logSourceTag"
$monitorLog = Join-Path $logDir 'live_trial_monitor.log'
$summaryPath = Join-Path $statsDir 'summary.json'
$tradesPath = Join-Path $statsDir 'trades.csv'
$statusJson = Join-Path $repoDir ("logs\edge_research\v28_common_clock_live_trial_status_{0}_latest.json" -f $safeStrategyTag)
$executionDiagJson = Join-Path $repoDir ("logs\edge_research\v28_common_clock_live_execution_diagnostics_{0}_latest.json" -f $safeStrategyTag)
$zeroEntryJson = Join-Path $repoDir ("logs\edge_research\v28_common_clock_zero_entry_blocker_{0}_latest.json" -f $safeStrategyTag)
$lockPath = Join-Path $repoDir 'state\live_trading.lock'
$killStatePath = Join-Path $stateDir 'mushroom_v28_exit_guard_kill_state.json'

New-Item -ItemType Directory -Force -Path $logDir, $statsDir, $stateDir | Out-Null

function Write-MonitorLine {
    param([string]$Line)
    $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'
    Add-Content -Path $monitorLog -Value "$stamp | $Line" -Encoding UTF8
}

function Get-LossCluster {
    if (-not (Test-Path $tradesPath)) {
        return 0
    }
    $rows = @(Import-Csv -Path $tradesPath)
    $cluster = 0
    foreach ($row in $rows) {
        $net = 0.0
        if (-not [double]::TryParse([string]$row.net_pnl_dollars, [ref]$net)) {
            continue
        }
        if ($net -lt 0) {
            $cluster += 1
        } elseif ($net -gt 0) {
            $cluster = 0
        }
    }
    return $cluster
}

function Write-KillState {
    param(
        [string]$Reason,
        [double]$NetCents,
        [int]$LossCluster
    )
    $payload = [ordered]@{
        killed = $true
        reason = $Reason
        updated_at = (Get-Date).ToUniversalTime().ToString('o')
        net_cents = [math]::Round($NetCents, 2)
        loss_cluster = $LossCluster
        max_loss_cluster = $MaxLossCluster
        max_drawdown_cents = $MaxDrawdownCents
        source = 'run_v28_common_clock_live_trial_monitor.ps1'
    }
    $payload | ConvertTo-Json -Depth 6 | Set-Content -Path $killStatePath -Encoding UTF8
}

function Stop-LiveProcessIfFlat {
    param([string]$Reason)
    if (-not (Test-Path $lockPath)) {
        Write-MonitorLine "kill=$Reason action=no_lock"
        return
    }
    $lock = Get-Content -LiteralPath $lockPath -Raw | ConvertFrom-Json
    if ($lock.strategy_tag -ne $strategyTag) {
        Write-MonitorLine "kill=$Reason action=lock_other_strategy strategy=$($lock.strategy_tag)"
        return
    }
    $statusReport = Get-Content -LiteralPath $statusJson -Raw | ConvertFrom-Json
    $positions = @($statusReport.exchange_active_positions)
    $orders = @($statusReport.exchange.resting_orders)
    if ($positions.Count -gt 0 -or $orders.Count -gt 0) {
        Write-MonitorLine "kill=$Reason action=kill_state_only exposure_positions=$($positions.Count) exposure_orders=$($orders.Count)"
        return
    }
    $proc = Get-Process -Id ([int]$lock.pid) -ErrorAction SilentlyContinue
    if ($proc) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    if (Test-Path $lockPath) {
        $post = Get-Content -LiteralPath $lockPath -Raw | ConvertFrom-Json
        if ($post.pid -eq $lock.pid -and $post.strategy_tag -eq $strategyTag) {
            Remove-Item -LiteralPath $lockPath -Force
        }
    }
    Write-MonitorLine "kill=$Reason action=stopped_flat_process pid=$($lock.pid)"
}

Write-MonitorLine "started strategy=$strategyTag interval_seconds=$IntervalSeconds max_loss_cluster=$MaxLossCluster max_drawdown_cents=$MaxDrawdownCents max_zero_fill_count=$MaxZeroFillCount min_source_reject_events=$MinSourceRejectEvents max_source_stale_reject_share=$MaxSourceStaleRejectShare status_json=$statusJson"

while ($true) {
    try {
        $env:OUTPUT_STRATEGY_TAG = $strategyTag
        $env:LOG_SOURCE_TAG = $logSourceTag
        $env:SCORE_MODE = 'live_only'
        $env:V28_COMMON_CLOCK_STRATEGY_TAG = $strategyTag
        $env:V28_COMMON_CLOCK_LOG_SOURCE_TAG = $logSourceTag
        $env:V28_COMMON_CLOCK_STATUS_JSON = $statusJson
        $env:V28_COMMON_CLOCK_STATUS_MD = [IO.Path]::ChangeExtension($statusJson, '.md')
        $env:V28_COMMON_CLOCK_EXECUTION_DIAGNOSTICS_JSON = $executionDiagJson
        $env:V28_COMMON_CLOCK_EXECUTION_DIAGNOSTICS_MD = [IO.Path]::ChangeExtension($executionDiagJson, '.md')
        $env:V28_COMMON_CLOCK_ZERO_ENTRY_JSON = $zeroEntryJson
        $env:V28_COMMON_CLOCK_ZERO_ENTRY_MD = [IO.Path]::ChangeExtension($zeroEntryJson, '.md')
        & $python '.\score_bot_log.py' *> $null
        & $python '.\probe_v28_common_clock_live_trial_status.py' *> $null
        & $python '.\probe_v28_common_clock_live_execution_diagnostics.py' *> $null
        & $python '.\probe_v28_common_clock_zero_entry_blocker.py' *> $null

        $summary = Get-Content -LiteralPath $summaryPath -Raw | ConvertFrom-Json
        $statusReport = Get-Content -LiteralPath $statusJson -Raw | ConvertFrom-Json
        $executionDiag = Get-Content -LiteralPath $executionDiagJson -Raw | ConvertFrom-Json
        $zeroEntry = Get-Content -LiteralPath $zeroEntryJson -Raw | ConvertFrom-Json
        $netCents = 100.0 * [double]$summary.net_pnl_total_dollars
        $lossCluster = Get-LossCluster
        $zeroFillCount = [int]($executionDiag.counts.zero_fill_attempts)
        $filledEventCount = [int]($executionDiag.counts.filled_events)
        $positions = @($statusReport.exchange_active_positions)
        $orders = @($statusReport.exchange.resting_orders)
        $rejectTotal = 0
        $sourceStaleRejects = 0
        if ($statusReport.execution_events -and $statusReport.execution_events.reject_reasons) {
            foreach ($prop in $statusReport.execution_events.reject_reasons.PSObject.Properties) {
                $count = [int]$prop.Value
                $rejectTotal += $count
                if ($prop.Name -in @('btc_stale', 'book_stale')) {
                    $sourceStaleRejects += $count
                }
            }
        }
        $sourceStaleShare = 0.0
        if ($rejectTotal -gt 0) {
            $sourceStaleShare = [double]$sourceStaleRejects / [double]$rejectTotal
        }
        $sourceStaleKill = (
            $filledEventCount -eq 0 `
            -and $rejectTotal -ge $MinSourceRejectEvents `
            -and $sourceStaleShare -ge $MaxSourceStaleRejectShare
        )
        $decision = 'ok'
        if ($lossCluster -ge $MaxLossCluster) {
            $decision = "kill_loss_cluster_$lossCluster"
            Write-KillState -Reason $decision -NetCents $netCents -LossCluster $lossCluster
            Stop-LiveProcessIfFlat -Reason $decision
        } elseif ($netCents -le -1 * $MaxDrawdownCents) {
            $decision = "kill_drawdown_$([math]::Round($netCents, 2))c"
            Write-KillState -Reason $decision -NetCents $netCents -LossCluster $lossCluster
            Stop-LiveProcessIfFlat -Reason $decision
        } elseif ($zeroFillCount -ge $MaxZeroFillCount -and $filledEventCount -eq 0) {
            $decision = "stop_zero_fill_cluster_$zeroFillCount"
            Write-KillState -Reason $decision -NetCents $netCents -LossCluster $lossCluster
            Stop-LiveProcessIfFlat -Reason $decision
        } elseif ($sourceStaleKill) {
            $decision = "stop_source_stale_share_$([math]::Round(100.0 * $sourceStaleShare, 1))pct"
            Write-KillState -Reason $decision -NetCents $netCents -LossCluster $lossCluster
            Stop-LiveProcessIfFlat -Reason $decision
        }
        Write-MonitorLine ("decision={0} status={1} entries={2} round_trips={3} net_cents={4} loss_cluster={5} zero_fills={6} filled_events={7} positions={8} orders={9} source_stale={10}/{11}({12}pct) zero_entry={13} no_entry_review_due={14} mature_markets={15} markets_until_review={16} latest={17}/{18}" -f `
            $decision,
            $statusReport.status,
            $summary.entries_total,
            $summary.completed_round_trips,
            [math]::Round($netCents, 2),
            $lossCluster,
            $zeroFillCount,
            $filledEventCount,
            $positions.Count,
            $orders.Count,
            $sourceStaleRejects,
            $rejectTotal,
            [math]::Round(100.0 * $sourceStaleShare, 1),
            $zeroEntry.decision,
            $zeroEntry.no_entry_review_due,
            $zeroEntry.totals.mature_markets,
            $zeroEntry.markets_until_no_entry_review,
            $statusReport.execution_events.latest_event_type,
            $statusReport.execution_events.latest_decision_reason)
    } catch {
        $line = $_.InvocationInfo.ScriptLineNumber
        $command = ($_.InvocationInfo.Line -replace '\s+', ' ').Trim()
        Write-MonitorLine "monitor_error line=$line type=$($_.Exception.GetType().Name) message=$($_.Exception.Message) command=$command"
    }
    Start-Sleep -Seconds $IntervalSeconds
}
