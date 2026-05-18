# v28 Feature-Gate BTC-REST Live Policy

- Generated local: 2026-05-08 00:26 ET
- Status: `active_live_test`
- Strategy tag: `mushroom_v28_common_clock_exit_guard_v1_sourcefix_featuregate_btcrest_size1_live`
- Log source: `live_mushroom_v28_common_clock_exit_guard_sourcefix_featuregate_btcrest_size1`
- Launcher: `scripts/run_v28_common_clock_exit_guard_sourcefix_featuregate_btcrest_live_size1.ps1`
- Active lock PID: `7768`
- Run id: `c5ec8aa0-252f-4f29-982c-fe11c3ddbe4d`

## Why This Exists

Dual-lane remains the top historical candidate family: diagnostic parent-fill primary lanes show $20.91-$22.33 projected net and the best diagnostic union shows $18.43. The full dual-lane stack is not currently live-runnable as an independent real-money bot because the live runtime has one account-wide position/exit state and one live lock. Running a second live process would contaminate attribution and can cause exit-state conflicts.

This feature-gate BTC-REST policy is the nearest live-adaptable v28-derived slice from the dual-lane/source-quality family. It uses existing production entry, exit, sizing, logging, scoring, reconciliation, and kill-rule machinery while testing observable feature-gate controls in real trades.

## Full Policy

| component | rule |
|---|---|
| entry | v28 common-clock mushroom fair-value engine, BTC Coinbase REST fallback enabled, book/BTC/account/risk checks, ask <= 90c, raw edge probability >= 0.05, recross hazard <= 0.60, abs d sigma >= 0.85, min seconds to close 70 |
| selectivity guard | `MUSHROOM_V28_MIN_P_SIDE=0.01`, `MUSHROOM_V28_MIN_EDGE_CENTS=0.0`, buffer/slippage set to 0.0 so the observable feature gate is the real decision gate rather than the inherited 0.85 p-side floor |
| exit/state | existing v28 common-clock live exit guard, probability-collapse/value-over-hold IOC exit, 30s post-fill delay, one market position at a time |
| sizing | size 1, multi-entry disabled, max market risk 100c |
| risk/kill | monitor every 60s; stop/downgrade on loss cluster >= 3, drawdown <= -200c, zero-fill count >= 8, source-stale share > 70% after >= 100 rejects with no fills, stale lock/process failure, unresolved exchange exposure/order mismatch, or exit-guard kill state |
| live-test | real Kalshi orders under the strategy/log tags above; separate live monitor and stats directory |
| accounting | `score_bot_log.py` in `live_only` mode, exchange fill reconciliation, fee-aware PnL from entry/exit fills; compare against exchange positions/fills/orders |
| iteration | keep running only while monitor is OK; after 8 mature no-entry markets run zero-entry/near-miss review; do not widen thresholds silently; each tweak gets a new strategy/log tag |

## Current Live Evidence

- First live entry: `KXBTC15M-26MAY080030-30`, NO, size 1, bought at 23c at 2026-05-08 00:23:07 ET.
- Exit: sold at 20c at 2026-05-08 00:24:05 ET via `mushroom_v28_probability_collapse_full_single_shot_visible_depth`.
- Gross PnL: -3c.
- Fees: 4c total in scorer output.
- Current scorer net: -7c; monitor/status may briefly show -5c until its next score refresh, so scorer plus exchange reconciliation is the accounting source of truth.
- Exchange reconciliation after exit: active positions 0, resting orders 0, recent candidate fills 2.

## Current Read

This policy has adequate coverage to fire real orders, so it is not stuck behind the old 0.85 p-side floor. The current blockers are source freshness and feature-gate timing, especially abs d sigma around the 0.85 boundary, plus one early losing exit. It remains a live test, not a viable completed strategy.

Do not mark the goal complete. Continue only under kill rules and compare every completed round trip against the refreshed v28 live baseline.
