$ErrorActionPreference = 'Stop'

if (-not (Test-Path .\venv\Scripts\python.exe)) {
    throw 'Virtual environment not found. Run .\setup_windows.ps1 first.'
}

$env:STRATEGY_TAG = 'entry_90_stop_78'
$env:EXIT_DROP_ODDS_CENTS = '78'
$env:PRE_ENTRY_STDDEV_FILTER_ENABLED = 'false'
$env:POSITION_SIZE = '2'
$env:LIVE_ENTRY_IOC_FIRST = 'true'
$env:LIVE_ENTRY_MIN_VISIBLE_DEPTH_FOR_IOC = '1'
$env:LIVE_ENTRY_BOOK_DIAGNOSTICS_LEVELS = '5'
$env:LIVE_ENTRY_DEFAULT_TIF = 'immediate_or_cancel'
$env:LIVE_ENTRY_ALLOW_FOK_WHEN_FULL_DEPTH = 'true'
$env:LIVE_ENTRY_SLICE_ENABLED = 'false'
$env:LIVE_ENTRY_SLICE_PATTERN = '2'
$env:LIVE_ENTRY_SLICE_DELAY_MS = '0'
$env:LIVE_ENTRY_SLICE_STOP_ON_ZERO_FILL = 'true'
$env:LIVE_ENTRY_DEAD_MARKET_SUPPRESSION_MS = '2000'
$env:LIVE_ENTRY_MATERIAL_BOOK_CHANGE_TICKS = '1'
$env:LIVE_ACCOUNT_STATE_MAX_AGE_MS = '1500'
$env:EXECUTION_TELEMETRY_ENABLED = 'true'
$env:DRY_RUN = 'true'

.\venv\Scripts\python.exe .\kalshi_btc15m_bot_ws.py
