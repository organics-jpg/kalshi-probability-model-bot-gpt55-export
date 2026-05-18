# v28 Broad BTC-REST Live Policy

- Generated local: 2026-05-08 00:08 ET
- Strategy tag: `mushroom_v28_common_clock_exit_guard_v1_sourcefix_broad_btcrest_size1_live`
- Log source tag: `live_mushroom_v28_common_clock_exit_guard_sourcefix_broad_btcrest_size1`
- Launcher: `scripts/run_v28_common_clock_exit_guard_sourcefix_broad_btcrest_live_size1.ps1`
- Status: `active_live_test`

## Policy

- Entry rule: v28 common-clock mushroom fair-value entry, feature gate disabled, minimum edge 2.0c, max ask 90c, minimum side probability 0.85 from the underlying size-1 runner, minimum 70 seconds to close, synced book/BTC/account checks, entry book age gates at 1000ms.
- Exit/state rule: existing v28 common-clock exit guard, single-shot IOC when visible depth is sufficient, value-over-hold exit trigger, 30s post-fill exit delay, one market position at a time.
- Sizing rule: size 1 contract, multi-entry disabled by the base size-1 launcher, max market risk 100c.
- Risk/kill rule: live monitor active every 60s; kill/downgrade gates include max loss cluster 3, max drawdown 200c, max zero-fill count 8, source stale reject share above 70% after at least 100 source rejects, plus live lock and exchange-position checks.
- Live-test rule: real Kalshi orders only under the strategy/log tags above, separate bot log, execution ledger, exchange reconciliation ledger, live-only score directory, and monitor log.
- Accounting/PnL rule: score in `live_only` mode; exchange reconciliation fills override local log fill price and fees; fractional fee cents are preserved in `score_bot_log.py`.
- Iteration rule: keep running while monitor is OK and exchange exposure is flat or expected; revise or stop on kill-rule breach, execution blocker, stale source-quality cluster, or live evidence that after-fee PnL/risk is worse than refreshed v28 baseline.

## Current Live Evidence

- As of 2026-05-07 23:56:36 ET status refresh: `decision=ok`, entries `2`, round trips `2`, net `5c`, exchange positions `0`, exchange resting orders `0`, process/lock both live on PID `23156`.
- Exchange reconciliation as of 2026-05-08T03:56:36Z: 4 candidate fills since run start, active positions 0, resting orders 0, balance 2344c.
- Current scored live-only result: 2 entries, 2 completed round trips, +5c net after exchange fill/fee override, 3 resolved markets and 1 unresolved market in the scorer.
- Broad-log rejection audit as of 2026-05-08T03:57:46Z: 408 rejects total, with `btc_stale=154`, `p_below_floor=138`, `book_stale=86`, `ask_too_high=18`, `time_window=8`, `missing_horizon=2`, `warming=2`.
- Freshness-only blocker count remains 0: no `btc_stale`/`book_stale` rejection had otherwise-passing ask, balance, time, risk, edge, probability, and model-price gates.
- Correct broad-log zero-entry classifier: 4 markets seen, 2 mature skipped markets, 2 markets with entry/order activity, 0 stale-only blockers, no no-entry review due until 8 mature markets.
- Latest broad-log near-miss read: market `KXBTC15M-26MAY080000-00`, source stale `122/197` (61.9%), `otherwise-approved book-stale rows=0`; near rows split between probability failures and negative/invalid price-edge cases.
- Dual-lane checkpoint refresh at 2026-05-08T03:55Z remains `no_live_test`: dual-lane forced strict precheck is 16 settled, 13/3, +59c, but live v28 on same candidate markets is +412c, so dual-lane trails by -353c and remains a paper/coordinator watch rather than a real-money replacement.
- Rollover check at 2026-05-08 00:00:31 ET passed: bot moved to `KXBTC15M-26MAY080015-15`, connected/subscribed websocket channels, loaded an orderbook snapshot, and remained flat with no pending order.
- Status refresh at 2026-05-08T04:01:02Z: entries 2, round trips 2, net +$0.05, positions 0, resting orders 0, candidate fills since run start 4, latest reject `p_below_floor`.
- Correct broad-log zero-entry classifier at 2026-05-08T04:01:00Z: 5 markets seen, 2 entry/order markets, 2 mature selective-wait markets, current 00:15 market still immature, stale-only blockers still 0, no-entry review not due.
- Status refresh at 2026-05-08T04:08:08Z: lock/process live, entries 2, round trips 2, net +$0.05, exchange positions 0, exchange resting orders 0, candidate fills since run start 4, latest reject `book_stale`.
- Correct broad-log zero-entry classifier at 2026-05-08T04:08:07Z: 5 markets seen, 3 mature markets, 2 entry/order markets, 3 selective-wait markets, stale-only blockers still 0, no-entry review not due for 5 more mature markets. Current market max p reached 0.864137 with max edge 18.622997c, so low coverage is currently a p/price gate issue, not a failed-entry-path issue.
- Scored live-only rows:
  - `KXBTC15M-26MAY072315-15`: buy YES 7.0c, sell 9.4c, fees 2.4c, net 0.0c.
  - `KXBTC15M-26MAY072330-30`: buy YES 60.0c, sell 69.0c, fees 4.0c, net 5.0c.

## Current Read

This is a controlled active live trial, not a completed strategy proof. It has positive after-fee live PnL so far, but the sample is only 2 round trips and remains far short of the goal's meaningful-sample requirement. Coverage is being watched closely. The current skipped markets are explained by the active v28 probability floor, edge, and ask gates rather than stale-only blockers or failed order submission, so any coverage expansion must be versioned and evidence-led instead of silently widening the live policy.

## Watch Items

- The second trade exited YES at 69c and the same market later printed heartbeats as high as 98c. This is not enough evidence to change the exit rule, but it is an early live watch item for whether the value-over-hold exit is clipping winners.
- The current broad runner is less broad than its launcher name implies because `MUSHROOM_V28_MIN_P_SIDE` remains 0.85. If repeated profitable skips accumulate around p=0.78-0.85, test a separately tagged p-floor relaxation rather than mutating this live tag in place.
