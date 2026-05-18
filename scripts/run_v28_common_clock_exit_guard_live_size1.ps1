param(
    [string]$SourceWorkspace = '',
    [string]$StrategyTag = 'mushroom_v28_common_clock_exit_guard_v1_size1_live',
    [string]$BotStorageTag = 'live_mushroom_v28_common_clock_exit_guard_size1',
    [string]$EntryBaseBookAgeMs = '1000',
    [string]$EntryFinalMinuteBookAgeMs = '1000',
    [string]$EntryFinalSecondsBookAgeMs = '1000',
    [string]$EntryBlockedSuppressionMs = '2000',
    [string]$BtcMaxAgeMs = '1500',
    [string]$BtcWsStaleReconnectMs = '0',
    [string]$BtcWsUrl = 'wss://ws-feed.exchange.coinbase.com',
    [string]$BtcWsFallbackUrls = 'wss://stream.binance.us:9443/ws/btcusdt@bookTicker,wss://stream.binance.us:9443/ws/btcusdt@trade',
    [string]$BtcRestFallbackEnabled = 'false',
    [string]$BtcRestFallbackUrl = 'https://api.coinbase.com/v2/prices/BTC-USD/spot',
    [string]$BtcRestFallbackMinIntervalMs = '1000',
    [string]$FastFillGateEnabled = 'false',
    [string]$FastFillMinSecondsToClose = '60',
    [string]$FastFillMinDepthContracts = '2',
    [string]$FastFillMinDepthRatio = '0',
    [string]$FastFillMinWindowMs = '150',
    [string]$FastFillSlippageBudgetCents = '1',
    [string]$FastFillMinNetEdgeCents = '2',
    [string]$FeatureGateEnabled = 'false',
    [string]$FeatureGateRawEdgeProbMin = '0.05',
    [string]$FeatureGateRecrossMax = '0.60',
    [string]$FeatureGateAbsDMin = '0.85',
    [string]$FeatureGateAbsDMax = '0.0',
    [string]$FeatureGateAskProbMin = '0.0',
    [string]$PositionSize = '1',
    [string]$MultiEntrySameMarketEnabled = 'false',
    [string]$MultiEntryMaxPositionContracts = '1',
    [string]$MultiEntryMinSecondsBetweenEntries = '900',
    [string]$MushroomV28MinPSide = '0.85',
    [string]$MushroomV28MinEdgeCents = '2.0',
    [string]$MushroomV28ModelBufferCents = '1.0',
    [string]$MushroomV28SlippageCents = '1.0',
    [string]$MushroomV28MaxAskCents = '90',
    [string]$MushroomV28MinSecondsToClose = '70',
    [string]$MushroomV28MaxSecondsToClose = '900',
    [string]$MushroomV28MaxMarketRiskCents = '100',
    [string]$PostFillExitDelaySeconds = '30',
    [string]$MushroomV28ExitGuardMode = 'enforce',
    [string]$MushroomV28PhiMemoryEnabled = 'false',
    [string]$MushroomV28PhiMemoryMode = 'shadow',
    [string]$MushroomV28PhiMemoryEntryCapCents = '1.0',
    [string]$MushroomV28PhiMemoryExitCapCents = '2.0',
    [string]$MushroomV28PhiMemoryAllowAddEntries = 'true',
    [string]$MushroomV28PhiMemoryAllowSizeIncrease = 'true',
    [string]$MushroomV28PhiMemoryAllowSideFlipLive = 'false',
    [string]$MushroomV28PhiMemoryKillSwitch = 'false',
    [string]$MushroomV28PhiMemoryKillNetPnlDollars = '-4.0',
    [string]$MushroomV28PhiMemoryKillLossCluster = '6',
    [string]$MushroomV28PhiMemoryNearEdgeMinCents = '2.0',
    [string]$MushroomV28PhiMemoryNearDepthRatioMin = '6.0',
    [string]$MushroomV28PhiMemoryRequiredDepthRatio = '8.0',
    [string]$MushroomV28PhiMemoryNearAbsDMin = '0.75',
    [string]$MushroomV28PhiMemoryNearAbsDMax = '1.15',
    [string]$MushroomV28PhiMemoryRichExitRecheckBidCents = '80',
    [string]$MushroomV28PhiMemoryRichExitRecheckSeconds = '5',
    [string]$MushroomV28PhiMemoryReportIntervalSeconds = '900',
    [string]$MushroomV28AdaptiveExitEnabled = 'false',
    [string]$MushroomV28AdaptiveExitMode = 'shadow',
    [string]$MushroomV28AdaptiveExitCheapNoEntryMaxCents = '15.0',
    [string]$MushroomV28AdaptiveExitReduceFraction = '0.5',
    [string]$MushroomV28AdaptiveExitRecheckSeconds = '5.0',
    [string]$MushroomV28AdaptiveExitPanicPHoldFloor = '0.03',
    [string]$MushroomV28AdaptiveExitDisableMinObservations = '3',
    [string]$MushroomV28AdaptiveExitDisableDeltaCents = '-150.0',
    [string]$MushroomV28AdaptiveExitRestoreMinObservations = '5',
    [string]$MushroomV28AdaptiveExitRestoreDeltaCents = '150.0',
    [string]$MushroomV28LifecycleEnabled = 'false',
    [string]$MushroomV28LifecycleMode = 'shadow',
    [string]$MushroomV28LifecycleExitTollCents = '2.5',
    [string]$MushroomV28LifecycleRecheckSeconds = '5',
    [string]$MushroomV28LifecycleCheapEntryMaxCents = '15',
    [string]$MushroomV28LifecyclePromoteDeltaCents = '100',
    [string]$MushroomV28LifecycleDisableBadSettles = '3',
    [string]$MushroomV28LifecycleMinPromoteObservations = '5'
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoDir = Split-Path -Parent $scriptDir
Set-Location $repoDir

function Import-DotEnv {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        throw "Missing .env: $Path"
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

if (-not $SourceWorkspace) {
    $SourceWorkspace = $repoDir
}
Import-DotEnv (Join-Path $SourceWorkspace '.env')
if ($env:KALSHI_PRIVATE_KEY_PATH -and -not [System.IO.Path]::IsPathRooted($env:KALSHI_PRIVATE_KEY_PATH)) {
    $env:KALSHI_PRIVATE_KEY_PATH = Join-Path $SourceWorkspace $env:KALSHI_PRIVATE_KEY_PATH
}

$env:STRATEGY_TAG = $StrategyTag
$env:BOT_STORAGE_TAG = $BotStorageTag
$env:TARGET_ENTRY_ODDS_CENTS = '90'
$env:POSITION_SIZE = $PositionSize
$env:MULTI_ENTRY_SAME_MARKET_ENABLED = $MultiEntrySameMarketEnabled
$env:MULTI_ENTRY_MAX_POSITION_CONTRACTS = $MultiEntryMaxPositionContracts
$env:MULTI_ENTRY_MIN_SECONDS_BETWEEN_ENTRIES = $MultiEntryMinSecondsBetweenEntries

$env:LIQUIDITY_DWELL_ENTRY_ENABLED = 'false'

$env:EXIT_DROP_ODDS_CENTS = '78'
$env:EXIT_STOP_LOSS_ENABLED = 'false'
$env:EXIT_CONFIRM_CHECKS = '2'
$env:EXIT_CONFIRM_SECONDS = '15'
$env:EXIT_PANIC_ODDS_CENTS = '74'
$env:POST_FILL_EXIT_DELAY_SECONDS = $PostFillExitDelaySeconds

$env:PRE_ENTRY_STDDEV_FILTER_ENABLED = 'false'
$env:LIVE_ENTRY_IOC_FIRST = 'true'
$env:LIVE_ENTRY_MIN_VISIBLE_DEPTH_FOR_IOC = '1'
$env:LIVE_ENTRY_BOOK_DIAGNOSTICS_LEVELS = '5'
$env:LIVE_ENTRY_BASE_BOOK_AGE_MS = $EntryBaseBookAgeMs
$env:LIVE_ENTRY_FINAL_MINUTE_BOOK_AGE_MS = $EntryFinalMinuteBookAgeMs
$env:LIVE_ENTRY_FINAL_SECONDS_BOOK_AGE_MS = $EntryFinalSecondsBookAgeMs
$env:LIVE_ENTRY_DEFAULT_TIF = 'immediate_or_cancel'
$env:LIVE_ENTRY_ALLOW_FOK_WHEN_FULL_DEPTH = 'true'
$env:LIVE_ENTRY_SLICE_ENABLED = 'false'
$env:LIVE_ENTRY_PARTIAL_COMPLETION_ENABLED = 'false'
$env:LIVE_ENTRY_DEAD_MARKET_SUPPRESSION_MS = '2000'
$env:LIVE_ENTRY_MATERIAL_BOOK_CHANGE_TICKS = '1'
$env:LIVE_ENTRY_STALE_SUPPRESSION_MS = '100'
$env:LIVE_ENTRY_STALE_DEPTH_CHANGE_CONTRACTS = '5'
$env:LIVE_ENTRY_BLOCKED_SUPPRESSION_MS = $EntryBlockedSuppressionMs
$env:LIVE_ENTRY_SINGLE_ORDER_DEPTH_MULTIPLE = '1.0'
$env:LIVE_ENTRY_ADAPTIVE_SLICE_ENABLED = 'false'
$env:LIVE_ENTRY_FAST_FILL_GATE_ENABLED = $FastFillGateEnabled
$env:LIVE_ENTRY_FAST_FILL_MIN_SECONDS_TO_CLOSE = $FastFillMinSecondsToClose
$env:LIVE_ENTRY_FAST_FILL_MIN_DEPTH_CONTRACTS = $FastFillMinDepthContracts
$env:LIVE_ENTRY_FAST_FILL_MIN_DEPTH_RATIO = $FastFillMinDepthRatio
$env:LIVE_ENTRY_FAST_FILL_MIN_WINDOW_MS = $FastFillMinWindowMs
$env:LIVE_ENTRY_FAST_FILL_SLIPPAGE_BUDGET_CENTS = $FastFillSlippageBudgetCents
$env:LIVE_ENTRY_FAST_FILL_MIN_NET_EDGE_CENTS = $FastFillMinNetEdgeCents

$env:LIVE_ACCOUNT_STATE_MAX_AGE_MS = '1500'
$env:LIVE_BALANCE_MIN_BUFFER_CENTS = '300'
$env:LIVE_BALANCE_FEE_BUFFER_CENTS = '25'
$env:EXECUTION_TELEMETRY_ENABLED = 'true'
$env:BTC_VOL_REGIME_GATE_ENABLED = 'false'
$env:DRY_RUN = 'false'
$env:LIVE_APPROVED_STRATEGY_TAG = $StrategyTag

$env:TRUFFLE_REGIME_LEASE_MODE = 'disabled'
$env:TRUFFLE_POST_ENTRY_SHADOW_ENABLED = 'false'
$env:TRUFFLE_POST_ENTRY_SHADOW_LIVE_EXIT_ENABLED = 'false'

$env:MUSHROOM_SHADOW_ENABLED = 'true'
$env:MUSHROOM_BTC_HISTORY_MINUTES = '1800'
$env:MUSHROOM_MIN_P_SIDE = '0.80'
$env:MUSHROOM_STRICT_P_SIDE = '0.85'
$env:MUSHROOM_MIN_EDGE_CENTS_15M = '2.0'
$env:MUSHROOM_MODEL_BUFFER_CENTS = '0.0'
$env:MUSHROOM_V21_DECISION_ENGINE_ENABLED = 'false'

$env:MUSHROOM_V28_SHADOW_ENABLED = 'true'
$env:MUSHROOM_V28_DECISION_ENGINE_ENABLED = 'true'
$env:MUSHROOM_V28_LIVE_EXIT_ENABLED = 'true'
$env:MUSHROOM_V28_MIN_P_SIDE = $MushroomV28MinPSide
$env:MUSHROOM_V28_MIN_EDGE_CENTS_15M = $MushroomV28MinEdgeCents
$env:MUSHROOM_V28_MODEL_BUFFER_CENTS = $MushroomV28ModelBufferCents
$env:MUSHROOM_V28_SLIPPAGE_CENTS = $MushroomV28SlippageCents
$env:MUSHROOM_V28_MAX_ASK_CENTS = $MushroomV28MaxAskCents
$env:MUSHROOM_V28_MIN_SECONDS_TO_CLOSE = $MushroomV28MinSecondsToClose
$env:MUSHROOM_V28_MAX_SECONDS_TO_CLOSE = $MushroomV28MaxSecondsToClose
$env:MUSHROOM_V28_MAX_MARKET_RISK_CENTS = $MushroomV28MaxMarketRiskCents
$env:MUSHROOM_V28_BTC_MAX_AGE_MS = $BtcMaxAgeMs
$env:MUSHROOM_V28_BTC_WS_ENABLED = 'true'
$env:MUSHROOM_V28_BTC_WS_URL = $BtcWsUrl
if ($BtcWsFallbackUrls -eq '__none__') {
    $env:MUSHROOM_V28_BTC_WS_FALLBACK_URLS = '__none__'
} else {
    $env:MUSHROOM_V28_BTC_WS_FALLBACK_URLS = $BtcWsFallbackUrls
}
$env:MUSHROOM_V28_BTC_WS_STALE_RECONNECT_MS = $BtcWsStaleReconnectMs
$env:MUSHROOM_V28_BTC_REST_FALLBACK_ENABLED = $BtcRestFallbackEnabled
$env:MUSHROOM_V28_BTC_REST_FALLBACK_URL = $BtcRestFallbackUrl
$env:MUSHROOM_V28_BTC_REST_FALLBACK_MIN_INTERVAL_MS = $BtcRestFallbackMinIntervalMs
$env:MUSHROOM_V28_FEATURE_GATE_ENABLED = $FeatureGateEnabled
$env:MUSHROOM_V28_FEATURE_GATE_RAW_EDGE_PROB_MIN = $FeatureGateRawEdgeProbMin
$env:MUSHROOM_V28_FEATURE_GATE_RECROSS_MAX = $FeatureGateRecrossMax
$env:MUSHROOM_V28_FEATURE_GATE_ABS_D_MIN = $FeatureGateAbsDMin
$env:MUSHROOM_V28_FEATURE_GATE_ABS_D_MAX = $FeatureGateAbsDMax
$env:MUSHROOM_V28_FEATURE_GATE_ASK_PROB_MIN = $FeatureGateAskProbMin

$env:MUSHROOM_V28_EXIT_HYSTERESIS_CENTS = '0.25'
$env:MUSHROOM_V28_EXIT_HOLD_BUFFER_CENTS = '1.0'
$env:MUSHROOM_V28_EXIT_REDUCE_P_HOLD_FLOOR = '0.80'
$env:MUSHROOM_V28_EXIT_FULL_P_HOLD_FLOOR = '0.72'
$env:MUSHROOM_V28_EXIT_FAIR_DRAWDOWN_CENTS = '8.0'
$env:MUSHROOM_V28_EXIT_FULL_DRAWDOWN_CENTS = '15.0'
$env:MUSHROOM_V28_EXIT_REDUCE_FRACTION = '0.5'
$env:MUSHROOM_V28_EXIT_GUARD_MODE = $MushroomV28ExitGuardMode
$env:MUSHROOM_V28_EXIT_GUARD_LEDGER_PATH = "logs\$env:BOT_STORAGE_TAG\mushroom_v28_exit_guard_shadow.ndjson"
$env:MUSHROOM_V28_EXIT_GUARD_KILL_SWITCH = 'false'
$env:MUSHROOM_V28_EXIT_GUARD_KILL_STATE_PATH = "state\$env:BOT_STORAGE_TAG\mushroom_v28_exit_guard_kill_state.json"
$env:MUSHROOM_V28_EXIT_GUARD_MAX_LOSS_CLUSTER = '3'
$env:MUSHROOM_V28_EXIT_GUARD_MAX_DRAWDOWN_CENTS = '200'
$env:MUSHROOM_V28_EXIT_GUARD_RECONCILIATION_ENABLED = 'true'
$env:MUSHROOM_V28_EXIT_GUARD_RECONCILIATION_PATH = "logs\$env:BOT_STORAGE_TAG\exchange_reconciliation.ndjson"
$env:MUSHROOM_V28_EXIT_GUARD_RECONCILIATION_MAX_FILLS = '100'
$env:MUSHROOM_V28_REJECT_TELEMETRY_ENABLED = 'true'
$env:MUSHROOM_V28_REJECT_TELEMETRY_INTERVAL_SECONDS = '20'

$env:MUSHROOM_V28_PHI_MEMORY_ENABLED = $MushroomV28PhiMemoryEnabled
$env:MUSHROOM_V28_PHI_MEMORY_MODE = $MushroomV28PhiMemoryMode
$env:MUSHROOM_V28_PHI_MEMORY_STATE_PATH = "state\$env:BOT_STORAGE_TAG\v28_phi_reward_memory_state.json"
$env:MUSHROOM_V28_PHI_MEMORY_LOG_PATH = "logs\$env:BOT_STORAGE_TAG\v28_phi_reward_memory.ndjson"
$env:MUSHROOM_V28_PHI_MEMORY_ENTRY_CAP_CENTS = $MushroomV28PhiMemoryEntryCapCents
$env:MUSHROOM_V28_PHI_MEMORY_EXIT_CAP_CENTS = $MushroomV28PhiMemoryExitCapCents
$env:MUSHROOM_V28_PHI_MEMORY_ALLOW_ADD_ENTRIES = $MushroomV28PhiMemoryAllowAddEntries
$env:MUSHROOM_V28_PHI_MEMORY_ALLOW_SIZE_INCREASE = $MushroomV28PhiMemoryAllowSizeIncrease
$env:MUSHROOM_V28_PHI_MEMORY_ALLOW_SIDE_FLIP_LIVE = $MushroomV28PhiMemoryAllowSideFlipLive
$env:MUSHROOM_V28_PHI_MEMORY_KILL_SWITCH = $MushroomV28PhiMemoryKillSwitch
$env:MUSHROOM_V28_PHI_MEMORY_KILL_NET_PNL_DOLLARS = $MushroomV28PhiMemoryKillNetPnlDollars
$env:MUSHROOM_V28_PHI_MEMORY_KILL_LOSS_CLUSTER = $MushroomV28PhiMemoryKillLossCluster
$env:MUSHROOM_V28_PHI_MEMORY_NEAR_EDGE_MIN_CENTS = $MushroomV28PhiMemoryNearEdgeMinCents
$env:MUSHROOM_V28_PHI_MEMORY_NEAR_DEPTH_RATIO_MIN = $MushroomV28PhiMemoryNearDepthRatioMin
$env:MUSHROOM_V28_PHI_MEMORY_REQUIRED_DEPTH_RATIO = $MushroomV28PhiMemoryRequiredDepthRatio
$env:MUSHROOM_V28_PHI_MEMORY_NEAR_ABS_D_MIN = $MushroomV28PhiMemoryNearAbsDMin
$env:MUSHROOM_V28_PHI_MEMORY_NEAR_ABS_D_MAX = $MushroomV28PhiMemoryNearAbsDMax
$env:MUSHROOM_V28_PHI_MEMORY_RICH_EXIT_RECHECK_BID_CENTS = $MushroomV28PhiMemoryRichExitRecheckBidCents
$env:MUSHROOM_V28_PHI_MEMORY_RICH_EXIT_RECHECK_SECONDS = $MushroomV28PhiMemoryRichExitRecheckSeconds
$env:MUSHROOM_V28_PHI_MEMORY_REPORT_INTERVAL_SECONDS = $MushroomV28PhiMemoryReportIntervalSeconds
$env:MUSHROOM_V28_ADAPTIVE_EXIT_ENABLED = $MushroomV28AdaptiveExitEnabled
$env:MUSHROOM_V28_ADAPTIVE_EXIT_MODE = $MushroomV28AdaptiveExitMode
$env:MUSHROOM_V28_ADAPTIVE_EXIT_STATE_PATH = "state\$env:BOT_STORAGE_TAG\v28_adaptive_exit_supervisor_state.json"
$env:MUSHROOM_V28_ADAPTIVE_EXIT_LOG_PATH = "logs\$env:BOT_STORAGE_TAG\v28_adaptive_exit_supervisor.ndjson"
$env:MUSHROOM_V28_ADAPTIVE_EXIT_CHEAP_NO_ENTRY_MAX_CENTS = $MushroomV28AdaptiveExitCheapNoEntryMaxCents
$env:MUSHROOM_V28_ADAPTIVE_EXIT_REDUCE_FRACTION = $MushroomV28AdaptiveExitReduceFraction
$env:MUSHROOM_V28_ADAPTIVE_EXIT_RECHECK_SECONDS = $MushroomV28AdaptiveExitRecheckSeconds
$env:MUSHROOM_V28_ADAPTIVE_EXIT_PANIC_P_HOLD_FLOOR = $MushroomV28AdaptiveExitPanicPHoldFloor
$env:MUSHROOM_V28_ADAPTIVE_EXIT_DISABLE_MIN_OBSERVATIONS = $MushroomV28AdaptiveExitDisableMinObservations
$env:MUSHROOM_V28_ADAPTIVE_EXIT_DISABLE_DELTA_CENTS = $MushroomV28AdaptiveExitDisableDeltaCents
$env:MUSHROOM_V28_ADAPTIVE_EXIT_RESTORE_MIN_OBSERVATIONS = $MushroomV28AdaptiveExitRestoreMinObservations
$env:MUSHROOM_V28_ADAPTIVE_EXIT_RESTORE_DELTA_CENTS = $MushroomV28AdaptiveExitRestoreDeltaCents
$env:MUSHROOM_V28_LIFECYCLE_ENABLED = $MushroomV28LifecycleEnabled
$env:MUSHROOM_V28_LIFECYCLE_MODE = $MushroomV28LifecycleMode
$env:MUSHROOM_V28_LIFECYCLE_STATE_PATH = "state\$env:BOT_STORAGE_TAG\v28_trade_lifecycle_state.json"
$env:MUSHROOM_V28_LIFECYCLE_LOG_PATH = "logs\$env:BOT_STORAGE_TAG\v28_trade_lifecycle.ndjson"
$env:MUSHROOM_V28_LIFECYCLE_EXIT_TOLL_CENTS = $MushroomV28LifecycleExitTollCents
$env:MUSHROOM_V28_LIFECYCLE_RECHECK_SECONDS = $MushroomV28LifecycleRecheckSeconds
$env:MUSHROOM_V28_LIFECYCLE_CHEAP_ENTRY_MAX_CENTS = $MushroomV28LifecycleCheapEntryMaxCents
$env:MUSHROOM_V28_LIFECYCLE_PROMOTE_DELTA_CENTS = $MushroomV28LifecyclePromoteDeltaCents
$env:MUSHROOM_V28_LIFECYCLE_DISABLE_BAD_SETTLES = $MushroomV28LifecycleDisableBadSettles
$env:MUSHROOM_V28_LIFECYCLE_MIN_PROMOTE_OBSERVATIONS = $MushroomV28LifecycleMinPromoteObservations

$python = Join-Path $repoDir 'venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    $python = 'python'
}

& $python '.\kalshi_btc15m_bot_ws.py'
