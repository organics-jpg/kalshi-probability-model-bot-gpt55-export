param(
    [string]$SourceWorkspace = ''
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$launcher = Join-Path $scriptDir 'run_v28_common_clock_exit_guard_live_size1.ps1'

& $launcher `
    -SourceWorkspace $SourceWorkspace `
    -StrategyTag 'mushroom_v28_common_clock_exit_guard_v1_sourcefix_size1_live' `
    -BotStorageTag 'live_mushroom_v28_common_clock_exit_guard_sourcefix_size1' `
    -EntryBaseBookAgeMs '250' `
    -EntryFinalMinuteBookAgeMs '150' `
    -EntryFinalSecondsBookAgeMs '80' `
    -EntryBlockedSuppressionMs '2000' `
    -BtcWsStaleReconnectMs '3000'
