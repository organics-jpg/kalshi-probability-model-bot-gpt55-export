# v28 Common-Clock Exit Guard Live-Test Spec

Research-only. This probe does not place orders or edit live bot logic.

- Generated UTC: `2026-05-07T21:40:41.310274+00:00`
- Decision: `blocked_do_not_live_test`
- Live baseline: `1361c ($13.61)`
- Best strict window: `new_exit_mix_common_forward_v3`
- Readiness frontier window: `new_exit_mix_common_forward_v2`

## Candidate Contract

- entry rule: Current v28 approved-entry stream.
- exit state rule: Suppress selected current v28 exits using loss_guard_value_p85_reduce_p79_gap0.
- sizing rule: Start at size=1, max same-market position=1 for any future live trial.
- risk kill rule: Stop candidate on any harmful suppressed hold, any net loss cluster >=3, drawdown >=200c, accounting mismatch, stale account state, or exchange reconciliation failure.
- live test rule: Only one DRY_RUN=false process may own real exits. Until a production switch exists, run paper/virtual ledger only.
- accounting pnl rule: Separate BOT_STORAGE_TAG, logs, stats, execution_events, exchange fills/orders/fees reconciliation, and live-only score comparison.
- iteration rule: No threshold tweaks during a live trial; version a new candidate after post-trial scoring names the blocker.

## Go/No-Go Gates

| gate | required | current | evidence |
|---|---|---|---|
| `strict_forward_density` | >=30 strict suppressions in the selected common-clock window | `blocked` | new_exit_mix_common_forward_v2 has 17 suppressions; missing ['live_ready_false', 'suppressed_needed_13'] |
| `loss_control` | 0 harmful suppressions and non-negative loss-control cost | `pass` | harmful=0 loss_cost=0.0c |
| `full_policy_live_gate` | full-policy scorecard allows live test | `blocked` | no_live_test |
| `single_process_exit_owner` | candidate exit rule owns exits in the same live process or runs only as paper shadow | `pass` | Source has live-lock, v28 exit path, guard mode, evaluator, and paper shadow ledger. |
| `candidate_kill_state` | candidate stops on harmful suppressed hold, loss cluster, drawdown, stale account, or accounting mismatch | `pass` | Candidate kill-state source hooks present. |
| `exchange_reconciliation_plan` | pre/post Kalshi balance, positions, fills, realized PnL, fees, exposure, and orders reconciled | `planned_not_executed` | No live candidate trial has started. |

## Proposed Live Env If Gates Pass

| key | value |
|---|---|
| `STRATEGY_TAG` | `mushroom_v28_common_clock_exit_guard_v1_size1` |
| `BOT_STORAGE_TAG` | `live_mushroom_v28_common_clock_exit_guard_size1` |
| `POSITION_SIZE` | `1` |
| `MULTI_ENTRY_SAME_MARKET_ENABLED` | `false` |
| `MULTI_ENTRY_MAX_POSITION_CONTRACTS` | `1` |
| `DRY_RUN` | `false only after all go/no-go gates pass` |
| `LIVE_APPROVED_STRATEGY_TAG` | `mushroom_v28_common_clock_exit_guard_v1_size1` |

## Required Artifacts

| artifact | path/value |
|---|---|
| `logs` | `logs/live_mushroom_v28_common_clock_exit_guard_size1/` |
| `state` | `state/live_mushroom_v28_common_clock_exit_guard_size1/` |
| `stats` | `stats/live_mushroom_v28_common_clock_exit_guard_size1/` |
| `execution_events` | `logs/live_mushroom_v28_common_clock_exit_guard_size1/execution_events.ndjson` |
| `exchange_reconciliation` | `logs/live_mushroom_v28_common_clock_exit_guard_size1/exchange_reconciliation.ndjson` |
| `score_mode` | `live_only` |

## Current Evidence

- Candidate/current: `692c ($6.92)` / `478c ($4.78)`
- Delta: `214c ($2.14)`
- Suppressions: `13`
- Helpful/harmful: `13/0`
- Loss-control cost: `0c ($0.00)`
- Missing gates: `live_ready_false, suppressed_needed_17`
- Readiness frontier suppressions: `17/30`; missing `13`
