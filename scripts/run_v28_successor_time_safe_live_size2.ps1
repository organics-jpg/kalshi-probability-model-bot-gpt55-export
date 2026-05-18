param(
    [string]$SourceWorkspace = 'C:\Users\organ\Desktop\KALSHI + TRUFFLE BOT'
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoDir = Split-Path -Parent $scriptDir
Set-Location $repoDir

function Import-DotEnv {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        throw "Missing source .env: $Path"
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

Import-DotEnv (Join-Path $SourceWorkspace '.env')
if ($env:KALSHI_PRIVATE_KEY_PATH -and -not [System.IO.Path]::IsPathRooted($env:KALSHI_PRIVATE_KEY_PATH)) {
    $env:KALSHI_PRIVATE_KEY_PATH = Join-Path $SourceWorkspace $env:KALSHI_PRIVATE_KEY_PATH
}

$env:STRATEGY_TAG = 'v28_successor_time_safe_live_size2'
$env:BOT_STORAGE_TAG = 'live_v28_successor_time_safe_size2'
$env:TARGET_ENTRY_ODDS_CENTS = '90'
$env:POSITION_SIZE = '2'
$env:MULTI_ENTRY_SAME_MARKET_ENABLED = 'true'
$env:MULTI_ENTRY_MAX_POSITION_CONTRACTS = '10'
$env:MULTI_ENTRY_MIN_SECONDS_BETWEEN_ENTRIES = '120'

$env:LIQUIDITY_DWELL_ENTRY_ENABLED = 'false'
$env:EXIT_DROP_ODDS_CENTS = '78'
$env:EXIT_STOP_LOSS_ENABLED = 'false'
$env:PRE_ENTRY_STDDEV_FILTER_ENABLED = 'false'
$env:BTC_VOL_REGIME_GATE_ENABLED = 'false'
$env:DRY_RUN = 'false'
$env:LIVE_APPROVED_STRATEGY_TAG = 'v28_successor_time_safe_live_size2'

$env:LIVE_ENTRY_IOC_FIRST = 'true'
$env:LIVE_ENTRY_MIN_VISIBLE_DEPTH_FOR_IOC = '2'
$env:LIVE_ENTRY_BOOK_DIAGNOSTICS_LEVELS = '5'
$env:LIVE_ENTRY_BASE_BOOK_AGE_MS = '1000'
$env:LIVE_ENTRY_FINAL_MINUTE_BOOK_AGE_MS = '1000'
$env:LIVE_ENTRY_FINAL_SECONDS_BOOK_AGE_MS = '1000'
$env:LIVE_ENTRY_DEFAULT_TIF = 'immediate_or_cancel'
$env:LIVE_ENTRY_ALLOW_FOK_WHEN_FULL_DEPTH = 'true'
$env:LIVE_ENTRY_SLICE_ENABLED = 'false'
$env:LIVE_ENTRY_SLICE_PATTERN = '2'
$env:LIVE_ENTRY_SLICE_DELAY_MS = '0'
$env:LIVE_ENTRY_SLICE_STOP_ON_ZERO_FILL = 'true'
$env:LIVE_ENTRY_PARTIAL_COMPLETION_ENABLED = 'false'
$env:LIVE_ENTRY_DEAD_MARKET_SUPPRESSION_MS = '2000'
$env:LIVE_ENTRY_MATERIAL_BOOK_CHANGE_TICKS = '1'
$env:LIVE_ENTRY_STALE_SUPPRESSION_MS = '100'
$env:LIVE_ENTRY_STALE_DEPTH_CHANGE_CONTRACTS = '5'
$env:LIVE_ENTRY_BLOCKED_SUPPRESSION_MS = '250'
$env:LIVE_ENTRY_SINGLE_ORDER_DEPTH_MULTIPLE = '1.0'
$env:LIVE_ENTRY_ADAPTIVE_SLICE_ENABLED = 'false'
$env:LIVE_ENTRY_FAST_FILL_GATE_ENABLED = 'false'
$env:LIVE_ENTRY_FAST_FILL_MIN_DEPTH_CONTRACTS = '2'
$env:LIVE_ACCOUNT_STATE_MAX_AGE_MS = '1500'
$env:EXECUTION_TELEMETRY_ENABLED = 'true'

$env:TRUFFLE_REGIME_LEASE_MODE = 'disabled'
$env:TRUFFLE_POST_ENTRY_SHADOW_ENABLED = 'false'
$env:TRUFFLE_POST_ENTRY_SHADOW_LIVE_EXIT_ENABLED = 'false'

$env:MUSHROOM_SHADOW_ENABLED = 'true'
$env:MUSHROOM_BTC_HISTORY_MINUTES = '1800'
$env:MUSHROOM_V21_DECISION_ENGINE_ENABLED = 'false'
$env:MUSHROOM_V28_SHADOW_ENABLED = 'true'
$env:MUSHROOM_V28_DECISION_ENGINE_ENABLED = 'true'
$env:MUSHROOM_V28_LIVE_EXIT_ENABLED = 'false'
$env:MUSHROOM_V28_MIN_P_SIDE = '0.85'
$env:MUSHROOM_V28_MIN_EDGE_CENTS_15M = '2.0'
$env:MUSHROOM_V28_MODEL_BUFFER_CENTS = '1.0'
$env:MUSHROOM_V28_SLIPPAGE_CENTS = '1.0'
$env:MUSHROOM_V28_MAX_ASK_CENTS = '90'
$env:MUSHROOM_V28_MIN_SECONDS_TO_CLOSE = '70'
$env:MUSHROOM_V28_MAX_SECONDS_TO_CLOSE = '900'
$env:MUSHROOM_V28_MAX_MARKET_RISK_CENTS = '200'
$env:MUSHROOM_V28_BTC_MAX_AGE_MS = '1500'
$env:MUSHROOM_V28_BTC_WS_ENABLED = 'true'
$env:MUSHROOM_V28_BTC_WS_URL = 'wss://ws-feed.exchange.coinbase.com'
$env:MUSHROOM_V28_BTC_WS_FALLBACK_URLS = 'wss://stream.binance.us:9443/ws/btcusdt@bookTicker,wss://stream.binance.us:9443/ws/btcusdt@trade'
$env:MUSHROOM_V28_FEATURE_GATE_ENABLED = 'false'
$env:MUSHROOM_V28_EXIT_GUARD_MODE = 'disabled'
$env:MUSHROOM_V28_EXIT_GUARD_KILL_SWITCH = 'false'
$env:MUSHROOM_V28_PHI_MEMORY_ENABLED = 'false'
$env:MUSHROOM_V28_PHI_MEMORY_KILL_SWITCH = 'false'
$env:MUSHROOM_V28_ADAPTIVE_EXIT_ENABLED = 'false'
$env:MUSHROOM_V28_LIFECYCLE_ENABLED = 'false'

$env:MUSHROOM_V28_SUCCESSOR_SURFACE_ENABLED = 'true'
$env:MUSHROOM_V28_SUCCESSOR_MANIFEST_PATH = 'research_particle\v28_successor\candidate_manifests_logged_events_latest.json'
$env:MUSHROOM_V28_SUCCESSOR_CANDIDATE_ID = 'v28s_boundary_monotonic_time_safe_v001'
$env:MUSHROOM_V28_SUCCESSOR_MODEL_HASH = '9b461a310d06c06b55af2e2d'
$env:MUSHROOM_V28_SUCCESSOR_ENTRY_MODE = 'tested_shadow_rule'
$env:MUSHROOM_V28_SUCCESSOR_SHADOW_MIN_EDGE_CENTS = '1.0'

$python = Join-Path $repoDir 'venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    $python = 'python'
}

& $python '.\kalshi_btc15m_bot_ws.py'
