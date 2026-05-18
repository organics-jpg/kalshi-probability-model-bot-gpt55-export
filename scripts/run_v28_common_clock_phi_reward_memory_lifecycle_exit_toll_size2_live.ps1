param(
    [string]$SourceWorkspace = ''
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$launcher = Join-Path $scriptDir 'run_v28_common_clock_exit_guard_live_size1.ps1'

& $launcher `
    -SourceWorkspace $SourceWorkspace `
    -StrategyTag 'mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live' `
    -BotStorageTag 'live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live' `
    -PositionSize '2' `
    -MultiEntrySameMarketEnabled 'true' `
    -MultiEntryMaxPositionContracts '3' `
    -MultiEntryMinSecondsBetweenEntries '0' `
    -EntryBaseBookAgeMs '750' `
    -EntryFinalMinuteBookAgeMs '750' `
    -EntryFinalSecondsBookAgeMs '750' `
    -EntryBlockedSuppressionMs '0' `
    -BtcMaxAgeMs '10000' `
    -BtcWsStaleReconnectMs '3000' `
    -BtcWsUrl 'wss://ws-feed.exchange.coinbase.com' `
    -BtcWsFallbackUrls '__none__' `
    -BtcRestFallbackEnabled 'true' `
    -BtcRestFallbackUrl 'https://api.coinbase.com/v2/prices/BTC-USD/spot' `
    -BtcRestFallbackMinIntervalMs '1000' `
    -FastFillGateEnabled 'false' `
    -FastFillMinSecondsToClose '120' `
    -FastFillMinDepthContracts '0' `
    -FastFillMinDepthRatio '8' `
    -FastFillMinWindowMs '0' `
    -FastFillSlippageBudgetCents '0' `
    -FastFillMinNetEdgeCents '0' `
    -FeatureGateEnabled 'true' `
    -FeatureGateRawEdgeProbMin '-999' `
    -FeatureGateRecrossMax '999' `
    -FeatureGateAbsDMin '0.80' `
    -FeatureGateAbsDMax '1.10' `
    -FeatureGateAskProbMin '0.0' `
    -MushroomV28MinPSide '0.0' `
    -MushroomV28MinEdgeCents '3.0' `
    -MushroomV28ModelBufferCents '0.0' `
    -MushroomV28SlippageCents '0.0' `
    -MushroomV28MaxAskCents '85' `
    -MushroomV28MinSecondsToClose '120' `
    -MushroomV28MaxSecondsToClose '99999' `
    -MushroomV28MaxMarketRiskCents '300' `
    -PostFillExitDelaySeconds '30' `
    -MushroomV28ExitGuardMode 'disabled' `
    -MushroomV28PhiMemoryEnabled 'true' `
    -MushroomV28PhiMemoryMode 'enforce' `
    -MushroomV28PhiMemoryEntryCapCents '1.0' `
    -MushroomV28PhiMemoryExitCapCents '0.0' `
    -MushroomV28PhiMemoryAllowAddEntries 'true' `
    -MushroomV28PhiMemoryAllowSizeIncrease 'true' `
    -MushroomV28PhiMemoryAllowSideFlipLive 'false' `
    -MushroomV28PhiMemoryKillSwitch 'false' `
    -MushroomV28PhiMemoryKillNetPnlDollars '-999999.0' `
    -MushroomV28PhiMemoryKillLossCluster '999999' `
    -MushroomV28PhiMemoryNearEdgeMinCents '2.0' `
    -MushroomV28PhiMemoryNearDepthRatioMin '6.0' `
    -MushroomV28PhiMemoryRequiredDepthRatio '8.0' `
    -MushroomV28PhiMemoryNearAbsDMin '0.75' `
    -MushroomV28PhiMemoryNearAbsDMax '1.15' `
    -MushroomV28PhiMemoryRichExitRecheckBidCents '80' `
    -MushroomV28PhiMemoryRichExitRecheckSeconds '5' `
    -MushroomV28PhiMemoryReportIntervalSeconds '900' `
    -MushroomV28AdaptiveExitEnabled 'true' `
    -MushroomV28AdaptiveExitMode 'enforce' `
    -MushroomV28AdaptiveExitCheapNoEntryMaxCents '15.0' `
    -MushroomV28AdaptiveExitReduceFraction '0.5' `
    -MushroomV28AdaptiveExitRecheckSeconds '5.0' `
    -MushroomV28AdaptiveExitPanicPHoldFloor '0.03' `
    -MushroomV28AdaptiveExitDisableMinObservations '3' `
    -MushroomV28AdaptiveExitDisableDeltaCents '-150.0' `
    -MushroomV28AdaptiveExitRestoreMinObservations '5' `
    -MushroomV28AdaptiveExitRestoreDeltaCents '150.0' `
    -MushroomV28LifecycleEnabled 'true' `
    -MushroomV28LifecycleMode 'exit_only_enforce' `
    -MushroomV28LifecycleExitTollCents '2.5' `
    -MushroomV28LifecycleRecheckSeconds '5' `
    -MushroomV28LifecycleCheapEntryMaxCents '15' `
    -MushroomV28LifecyclePromoteDeltaCents '100' `
    -MushroomV28LifecycleDisableBadSettles '3' `
    -MushroomV28LifecycleMinPromoteObservations '5'
