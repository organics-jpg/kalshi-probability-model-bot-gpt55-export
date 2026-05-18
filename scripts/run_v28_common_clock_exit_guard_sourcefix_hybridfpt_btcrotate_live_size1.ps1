param(
    [string]$SourceWorkspace = ''
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$launcher = Join-Path $scriptDir 'run_v28_common_clock_exit_guard_live_size1.ps1'

& $launcher `
    -SourceWorkspace $SourceWorkspace `
    -StrategyTag 'mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_btcrotate_size1_live' `
    -BotStorageTag 'live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_btcrotate_size1' `
    -EntryBaseBookAgeMs '750' `
    -EntryFinalMinuteBookAgeMs '750' `
    -EntryFinalSecondsBookAgeMs '750' `
    -EntryBlockedSuppressionMs '2000' `
    -BtcMaxAgeMs '1500' `
    -BtcWsStaleReconnectMs '3000' `
    -BtcWsUrl 'wss://stream.binance.us:9443/ws/btcusdt@bookTicker' `
    -BtcWsFallbackUrls 'wss://stream.binance.us:9443/ws/btcusdt@trade,wss://ws-feed.exchange.coinbase.com' `
    -FastFillGateEnabled 'true' `
    -FastFillMinSecondsToClose '120' `
    -FastFillMinDepthContracts '8' `
    -FastFillMinWindowMs '150' `
    -FastFillSlippageBudgetCents '1' `
    -FastFillMinNetEdgeCents '3' `
    -FeatureGateEnabled 'true' `
    -FeatureGateRawEdgeProbMin '0.03' `
    -FeatureGateRecrossMax '0.60' `
    -FeatureGateAbsDMin '0.85' `
    -FeatureGateAbsDMax '1.10' `
    -FeatureGateAskProbMin '0.0' `
    -MushroomV28MinEdgeCents '3.0' `
    -MushroomV28MaxAskCents '83' `
    -MushroomV28MinSecondsToClose '120'
