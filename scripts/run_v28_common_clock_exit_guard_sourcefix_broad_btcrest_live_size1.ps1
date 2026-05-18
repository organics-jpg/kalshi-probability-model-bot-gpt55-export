param(
    [string]$SourceWorkspace = ''
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$launcher = Join-Path $scriptDir 'run_v28_common_clock_exit_guard_live_size1.ps1'

& $launcher `
    -SourceWorkspace $SourceWorkspace `
    -StrategyTag 'mushroom_v28_common_clock_exit_guard_v1_sourcefix_broad_btcrest_size1_live' `
    -BotStorageTag 'live_mushroom_v28_common_clock_exit_guard_sourcefix_broad_btcrest_size1' `
    -EntryBaseBookAgeMs '1000' `
    -EntryFinalMinuteBookAgeMs '1000' `
    -EntryFinalSecondsBookAgeMs '1000' `
    -EntryBlockedSuppressionMs '2000' `
    -BtcMaxAgeMs '1500' `
    -BtcWsStaleReconnectMs '3000' `
    -BtcWsUrl 'wss://ws-feed.exchange.coinbase.com' `
    -BtcWsFallbackUrls '__none__' `
    -BtcRestFallbackEnabled 'true' `
    -BtcRestFallbackUrl 'https://api.coinbase.com/v2/prices/BTC-USD/spot' `
    -BtcRestFallbackMinIntervalMs '1000' `
    -FastFillGateEnabled 'false' `
    -FeatureGateEnabled 'false' `
    -MushroomV28MinEdgeCents '2.0' `
    -MushroomV28MaxAskCents '90' `
    -MushroomV28MinSecondsToClose '70' `
    -PostFillExitDelaySeconds '30'
