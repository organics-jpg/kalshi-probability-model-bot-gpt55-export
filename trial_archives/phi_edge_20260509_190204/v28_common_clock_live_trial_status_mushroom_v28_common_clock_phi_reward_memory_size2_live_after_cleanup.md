# v28 Common-Clock Live Trial Status

- Generated UTC: `2026-05-09T20:22:36.016040+00:00`
- Status: `running_scored_round_trips`
- Strategy: `mushroom_v28_common_clock_phi_reward_memory_size2_live`
- Lock/process: `True` / `True`
- Score entries/round trips/net: `29` / `27` / `$-1.04`
- Latest event: `mushroom_v28_rejected` / `edge_below_floor` at `2026-05-09T20:22:24.577634+00:00`
- Event counts: `{'mushroom_v28_approved': 3, 'signal_seen': 3, 'plan_built': 3, 'order_submit_start': 9, 'order_submit_success': 9, 'fill_full': 5, 'exit_signal_seen': 6, 'exit_snapshot_built': 6, 'exit_capacity_estimated': 6, 'exit_plan_built': 6, 'exit_submit_start': 6, 'exit_submit_zero_fill': 4, 'exit_execution_deferred': 8, 'exit_submit_full': 2, 'exit_submit_success': 2, 'exit_reconciled': 2, 'mushroom_v28_rejected': 120}`
- Reject reasons: `{'<blank>': 6, 'single_shot_abundant_depth': 12, 'exit_trigger': 18, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 36, 'edge_below_floor': 38, 'ask_too_high': 5, 'book_stale': 44, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 8, 'warming': 4, 'time_window': 8, 'missing_horizon': 4, 'feature_gate': 9, 'depth_ratio': 6, 'btc_stale': 2}`
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
