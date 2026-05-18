# v28 Common-Clock Live Trial Status

- Generated UTC: `2026-05-09T20:23:50.990146+00:00`
- Status: `running_scored_round_trips`
- Strategy: `mushroom_v28_common_clock_phi_reward_memory_size2_live`
- Lock/process: `True` / `True`
- Score entries/round trips/net: `29` / `27` / `$-1.04`
- Latest event: `mushroom_v28_rejected` / `feature_gate` at `2026-05-09T20:23:48.436137+00:00`
- Event counts: `{'order_submit_success': 7, 'exit_submit_zero_fill': 3, 'exit_execution_deferred': 6, 'exit_signal_seen': 4, 'exit_snapshot_built': 4, 'exit_capacity_estimated': 4, 'exit_plan_built': 4, 'exit_submit_start': 4, 'order_submit_start': 6, 'exit_submit_full': 2, 'fill_full': 4, 'exit_submit_success': 2, 'exit_reconciled': 2, 'mushroom_v28_rejected': 142, 'mushroom_v28_approved': 2, 'signal_seen': 2, 'plan_built': 2}`
- Reject reasons: `{'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 26, 'exit_trigger': 12, 'edge_below_floor': 45, 'ask_too_high': 6, 'book_stale': 52, '<blank>': 4, 'single_shot_abundant_depth': 8, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 8, 'warming': 4, 'time_window': 8, 'missing_horizon': 4, 'feature_gate': 13, 'depth_ratio': 8, 'btc_stale': 2}`
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
