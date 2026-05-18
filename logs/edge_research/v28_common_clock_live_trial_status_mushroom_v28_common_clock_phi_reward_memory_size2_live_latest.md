# v28 Common-Clock Live Trial Status

- Generated UTC: `2026-05-11T03:46:24.611928+00:00`
- Status: `not_running_lock_missing_or_other_strategy`
- Strategy: `mushroom_v28_common_clock_phi_reward_memory_size2_live`
- Lock/process: `False` / `False`
- Score entries/round trips/net: `45` / `40` / `$-0.58`
- Latest event: `mushroom_v28_rejected` / `book_stale` at `2026-05-10T23:20:02.674639+00:00`
- Event counts: `{'exit_snapshot_built': 15, 'exit_capacity_estimated': 15, 'exit_plan_built': 15, 'exit_submit_start': 15, 'order_submit_start': 15, 'order_submit_reject': 15, 'exit_execution_deferred': 30, 'exit_signal_seen': 14, 'mushroom_v28_rejected': 66}`
- Reject reasons: `{'exit_trigger': 44, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 90, 'missing_horizon': 4, 'edge_below_floor': 28, 'book_stale': 28, 'feature_gate': 4, 'depth_ratio': 1, 'btc_stale': 1}`
- Lifecycle actions/buckets: `{}` / `{}`
- Lifecycle latest/reward tail: `None` / `None` / `None` / `0`c
- Exchange positions: `[]`
- Exchange active positions count: `0`
- Exchange resting orders: `[]`
- Exchange resting orders count: `0`
- Recent fills returned: `100`
- Candidate recent fills since run start: `19`
- Kalshi balance cents / portfolio cents: `832` / `0`
- Kalshi fills/fees since run: `19` / `$0.31`
- Kalshi gross/net realized since run: `$-0.09` / `$-0.40`
- Reconciliation snapshot appended: `True`

## Artifacts
- bot_log: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\bot.log` exists=`True`
- execution_events: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\execution_events.ndjson` exists=`True`
- guard_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\mushroom_v28_exit_guard_shadow.ndjson` exists=`False`
- reconciliation_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\exchange_reconciliation.ndjson` exists=`True`
- lifecycle_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\v28_trade_lifecycle.ndjson` exists=`False`
- score_summary: `stats\mushroom_v28_common_clock_phi_reward_memory_size2_live\summary.json` exists=`True`
