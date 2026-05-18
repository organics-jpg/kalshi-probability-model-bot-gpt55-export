param(
    [string]$SourceWorkspace = ''
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$launcher = Join-Path $scriptDir 'run_v28_common_clock_exit_guard_live_size1.ps1'

& $launcher `
    -SourceWorkspace $SourceWorkspace `
    -StrategyTag 'mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_live' `
    -BotStorageTag 'live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi' `
    -PositionSize '2' `
    -MultiEntrySameMarketEnabled 'true' `
    -MultiEntryMaxPositionContracts '3' `
    -MultiEntryMinSecondsBetweenEntries '120' `
    -EntryBaseBookAgeMs '750' `
    -EntryFinalMinuteBookAgeMs '750' `
    -EntryFinalSecondsBookAgeMs '750' `
    -EntryBlockedSuppressionMs '2000' `
    -BtcMaxAgeMs '1500' `
    -BtcWsStaleReconnectMs '3000' `
    -BtcWsUrl 'wss://ws-feed.exchange.coinbase.com' `
    -BtcWsFallbackUrls '__none__' `
    -BtcRestFallbackEnabled 'true' `
    -BtcRestFallbackUrl 'https://api.coinbase.com/v2/prices/BTC-USD/spot' `
    -BtcRestFallbackMinIntervalMs '1000' `
    -FastFillGateEnabled 'true' `
    -FastFillMinSecondsToClose '120' `
    -FastFillMinDepthContracts '8' `
    -FastFillMinWindowMs '150' `
    -FastFillSlippageBudgetCents '1' `
    -FastFillMinNetEdgeCents '3' `
    -FeatureGateEnabled 'true' `
    -FeatureGateRawEdgeProbMin '0.03' `
    -FeatureGateRecrossMax '0.60' `
    -FeatureGateAbsDMin '0.80' `
    -FeatureGateAbsDMax '1.10' `
    -FeatureGateAskProbMin '0.0' `
    -MushroomV28MinEdgeCents '3.0' `
    -MushroomV28ModelBufferCents '0.0' `
    -MushroomV28SlippageCents '0.0' `
    -MushroomV28MaxAskCents '85' `
    -MushroomV28MinSecondsToClose '120' `
    -MushroomV28MaxMarketRiskCents '300' `
    -PostFillExitDelaySeconds '30'
