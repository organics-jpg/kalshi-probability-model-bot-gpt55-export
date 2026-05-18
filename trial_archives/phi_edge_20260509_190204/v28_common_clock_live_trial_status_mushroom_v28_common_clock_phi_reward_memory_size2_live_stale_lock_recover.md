# v28 Common-Clock Live Trial Status

- Generated UTC: `2026-05-09T20:20:09.449585+00:00`
- Status: `not_running_stale_lock`
- Strategy: `mushroom_v28_common_clock_phi_reward_memory_size2_live`
- Lock/process: `True` / `False`
- Score entries/round trips/net: `29` / `27` / `$-1.04`
- Latest event: `mushroom_v28_rejected` / `edge_below_floor` at `2026-05-09T20:19:23.032185+00:00`
- Event counts: `{'mushroom_v28_rejected': 108, 'mushroom_v28_approved': 5, 'signal_seen': 5, 'plan_built': 5, 'order_submit_start': 11, 'order_submit_success': 11, 'execution_deferred': 1, 'fill_full': 6, 'exit_signal_seen': 6, 'exit_snapshot_built': 6, 'exit_capacity_estimated': 6, 'exit_plan_built': 6, 'exit_submit_start': 6, 'exit_submit_zero_fill': 4, 'exit_execution_deferred': 8, 'exit_submit_full': 2, 'exit_submit_success': 2, 'exit_reconciled': 2}`
- Reject reasons: `{'book_stale': 42, 'ask_too_high': 9, 'edge_below_floor': 31, 'feature_gate': 7, '<blank>': 10, 'single_shot_abundant_depth': 20, 'depth_ratio': 5, 'exit_trigger': 18, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 36, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 8, 'warming': 2, 'time_window': 8, 'missing_horizon': 4}`
- Exchange positions: `[]`
- Exchange active positions count: `0`
- Exchange resting orders: `[]`
- Exchange resting orders count: `0`
- Recent fills returned: `100`
- Candidate recent fills since run start: `0`
- Kalshi balance cents / portfolio cents: `2141` / `0`
- Kalshi fills/fees since run: `0` / `$0.00`
- Kalshi gross/net realized since run: `$0.00` / `$0.00`
- Reconciliation snapshot appended: `True`

## Artifacts
- bot_log: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\bot.log` exists=`True`
- execution_events: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\execution_events.ndjson` exists=`True`
- guard_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\mushroom_v28_exit_guard_shadow.ndjson` exists=`False`
- reconciliation_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\exchange_reconciliation.ndjson` exists=`True`
- score_summary: `stats\mushroom_v28_common_clock_phi_reward_memory_size2_live\summary.json` exists=`True`
