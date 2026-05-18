# v28 Goal Completion Live-Trial Audit

- Generated local: 2026-05-08 00:26 ET
- Goal status: `not_complete`
- Active live policy: `mushroom_v28_common_clock_exit_guard_v1_sourcefix_featuregate_btcrest_size1_live`
- Current evidence source: `stats/mushroom_v28_common_clock_exit_guard_v1_sourcefix_featuregate_btcrest_size1_live/summary.json`, `trades.csv`, `logs/live_mushroom_v28_common_clock_exit_guard_sourcefix_featuregate_btcrest_size1/exchange_reconciliation.ndjson`, `live_trial_monitor.log`

## Candidate Handling

| candidate family | current handling | status |
|---|---|---|
| broad BTC-REST v28 | stopped flat after exchange reconciliation; produced 2 round trips and +5c net before switch | archived_live_sample |
| dual-lane parent-fill / rescue family | still top historical/diagnostic family; parent-fill primary lanes show $20.91-$22.33 and diagnostic dual union shows $18.43 | priority_candidate_but_not_direct_live_runnable |
| strict dual-lane union | refreshed checkpoint still says `no_live_test`; strict precheck 16 settled, 13/3, +59c, zero full-loss cushion, trails same-window live v28 by -353c | blocked |
| feature-gate BTC-REST slice | launched as nearest live-adaptable v28/dual-lane/source-quality slice under one live lock, size 1, separate logs and kill rules | active_live_test |

## Success Criteria Checklist

| requirement | current evidence | status |
|---|---|---|
| coherent v28-derived entry rule | documented in `v28_featuregate_btcrest_live_policy_latest.md`; uses v28 common-clock FV entry plus observable raw-edge/recross/abs-d feature gate | pass |
| coherent exit/state rule | documented; existing v28 common-clock exit guard, probability-collapse/value-over-hold IOC exit, 30s post-fill delay | pass |
| sizing rule | size 1, multi-entry disabled, max market risk 100c | pass |
| active risk/kill rule | monitor active every 60s with loss-cluster, drawdown, zero-fill, source-stale, exposure/order checks | pass |
| real live trades | feature-gate test has 1 real round trip, 2 exchange fills | pass_but_small |
| after-fee profitability | first feature-gate round trip is negative after fees; scorer net -7c, monitor may temporarily lag | fail |
| accurate accounting | scorer uses exchange fill reconciliation and fee-aware PnL; exchange shows active positions 0 and orders 0 after exit | pass_but_watch_fee_lag |
| no unresolved exposure/orders | latest exchange reconciliation shows active positions 0 and resting orders 0 | pass |
| operational stability | live lock matches PID 7768; process running; monitor decision OK | pass |
| source quality controlled | source-stale share has been ~49%-57%, below 70% kill threshold but still a coverage blocker | pass_but_watch |
| meaningful live sample | only 1 completed feature-gate round trip | fail |
| controlled loss clusters | current loss cluster 1, below kill threshold 3 | weak |
| favorable comparison to refreshed v28 baseline | not enough live feature-gate data; dual-lane strict same-window comparison currently trails live v28 by -353c | fail |
| no single-outlier dependency | current feature-gate sample is one losing row | fail |
| clearly better to keep running than stop | yes for continued controlled trial under kill rules; no for goal completion | partial |

## Current Decision

Do not mark the goal complete. The active policy is tradeable and operationally stable, but it is not profitable yet and has only one completed live round trip. Keep the feature-gate BTC-REST live test running under kill rules unless loss cluster, drawdown, source freshness, or execution limits trigger. Do not silently widen thresholds for coverage.

Dual-lane should not be buried. The older >$20 evidence is real, but it is diagnostic parent-fill evidence rather than a complete production live policy. The current full dual-lane live blocker is architectural: a single-process coordinator/adapter is required before real dual-lane orders can be safely attributed and exited. Until that exists, live testing should use live-adaptable slices or a paper coordinator replay.
