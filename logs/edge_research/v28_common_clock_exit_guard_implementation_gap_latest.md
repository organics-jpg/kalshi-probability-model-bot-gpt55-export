# v28 Common-Clock Exit Guard Implementation Gap

Research-only. No live bot logic changes, no process control, no orders.

- Generated UTC: `2026-05-07T21:42:32.640842+00:00`
- Decision: `implementation_ready_for_paper_shadow_review`
- Target policy: `loss_guard_value_p85_reduce_p79_gap0`
- Readiness frontier: `new_exit_mix_common_forward_v2` with `17/30` suppressions; missing `13`
- Live-test spec decision: `blocked_do_not_live_test`

## Candidate Rule

- `value_over_hold`: suppress when p_hold >= 0.85 or hold_book_gap >= 0.00
- `probability_reduce`: suppress only when p_hold >= 0.79 and hold_book_gap >= 0.00
- `collapse_or_full_drawdown`: keep current live exit behavior
- `source`: probe_v28_frozen_exit_book_gap_loss_guard.py

## Existing Controls

| control | status | evidence | note |
|---|---|---|---|
| `single_live_lock` | `present` | `live_trading.lock + Live trading lock already held` | The bot already prevents a second independent live process. |
| `dry_run_strategy_approval` | `present` | `DRY_RUN=false is only allowed for strategy tag` | The existing approval tag gate can protect a future candidate launch. |
| `separate_storage_tags` | `present` | `BOT_STORAGE_TAG + resolve_strategy_paths` | The bot can already isolate state and logs by storage tag. |
| `v28_live_exit_owner_path` | `present` | `MUSHROOM_V28_LIVE_EXIT_ENABLED + detect_mushroom_v28_exit_signal` | There is a single-process v28 exit path to extend later. |
| `execution_telemetry` | `present` | `execution_events.ndjson + telemetry.emit` | Base telemetry exists, but candidate-specific guard decisions still need their own event. |
| `account_state_refresh` | `present` | `maybe_refresh_live_account_state/LIVE_ACCOUNT_STATE` | Account-state controls exist for the broader bot. |

## Missing Implementation Items

| item | status | required | note |
|---|---|---|---|
| `common_clock_guard_mode_env` | `present` | A disabled/paper/enforce switch for the exact loss_guard_value_p85_reduce_p79_gap0 rule. | A disabled/paper/enforce source-level switch is present. |
| `side_effect_free_guard_evaluator` | `present` | A real-time evaluator using only current exit features, not settled outcomes. | A real-time evaluator is present in source. |
| `paper_shadow_ledger` | `present` | Every would-suppress/keep decision must be logged before enforcement. | A dedicated candidate guard shadow ledger path/event is present. |
| `guard_applied_before_execute_exit_signal` | `present` | The candidate must decide keep/suppress before real exit submission. | The v28 exit path has a guard decision point before real exit submission. |
| `candidate_kill_state` | `present` | Stop on harmful suppressed hold, loss cluster, drawdown, stale account, or accounting mismatch. | Candidate-specific kill-state hooks are present. |
| `exchange_reconciliation_writer` | `present` | Pre/post balances, positions, fills, fees, exposure, and orders must be reconciled for live trial. | An exchange reconciliation writer is present. |

## Blockers


## Next Build Steps

- Exercise MUSHROOM_V28_EXIT_GUARD_MODE=paper in a dry-run or supervised shadow process before any enforce review.
- Add candidate kill-state and exchange reconciliation artifacts before DRY_RUN=false candidate approval.
- Only after density/live/kill/reconciliation gates pass, allow enforce mode to suppress qualifying soft exits before execute_exit_signal.
