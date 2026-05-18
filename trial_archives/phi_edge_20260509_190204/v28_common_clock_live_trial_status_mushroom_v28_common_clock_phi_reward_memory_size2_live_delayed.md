# v28 Common-Clock Live Trial Status

- Generated UTC: `2026-05-09T20:14:34.695622+00:00`
- Status: `running_scored_round_trips`
- Strategy: `mushroom_v28_common_clock_phi_reward_memory_size2_live`
- Lock/process: `True` / `True`
- Score entries/round trips/net: `29` / `27` / `$-1.04`
- Latest event: `mushroom_v28_rejected` / `time_window` at `2026-05-09T20:14:23.901959+00:00`
- Event counts: `{'exit_submit_success': 5, 'exit_reconciled': 5, 'mushroom_v28_rejected': 72, 'mushroom_v28_approved': 7, 'signal_seen': 7, 'plan_built': 7, 'order_submit_start': 15, 'order_submit_success': 15, 'fill_full': 10, 'exit_signal_seen': 8, 'exit_snapshot_built': 8, 'exit_capacity_estimated': 8, 'exit_plan_built': 8, 'exit_submit_start': 8, 'exit_submit_full': 4, 'execution_deferred': 1, 'exit_submit_zero_fill': 4, 'exit_execution_deferred': 8}`
- Reject reasons: `{'mushroom_v28_probability_reduce_single_shot_visible_depth': 18, 'edge_below_floor': 19, 'book_stale': 30, '<blank>': 14, 'single_shot_abundant_depth': 28, 'exit_trigger': 24, 'ask_too_high': 12, 'feature_gate': 2, 'depth_ratio': 1, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 36, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 8, 'warming': 2, 'time_window': 6}`
- Exchange positions: `[{'fees_paid_dollars': '0.279000', 'last_updated_ts': '2026-05-09T20:11:38.364162Z', 'market_exposure_dollars': '0.000000', 'position_fp': '0.00', 'realized_pnl_dollars': '-0.361000', 'resting_orders_count': 0, 'ticker': 'KXBTC15M-26MAY091615-15', 'total_traded_dollars': '12.361000'}]`
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
