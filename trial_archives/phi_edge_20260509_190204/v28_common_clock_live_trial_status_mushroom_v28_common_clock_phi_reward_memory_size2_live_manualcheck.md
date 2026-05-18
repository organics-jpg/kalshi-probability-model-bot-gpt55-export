# v28 Common-Clock Live Trial Status

- Generated UTC: `2026-05-09T20:11:01.018577+00:00`
- Status: `running_scored_round_trips`
- Strategy: `mushroom_v28_common_clock_phi_reward_memory_size2_live`
- Lock/process: `True` / `True`
- Score entries/round trips/net: `28` / `26` / `$-0.66`
- Latest event: `mushroom_v28_rejected` / `book_stale` at `2026-05-09T20:10:43.449559+00:00`
- Event counts: `{'mushroom_v28_rejected': 63, 'mushroom_v28_approved': 7, 'signal_seen': 7, 'plan_built': 7, 'order_submit_start': 16, 'order_submit_success': 16, 'fill_full': 11, 'exit_signal_seen': 9, 'exit_snapshot_built': 9, 'exit_capacity_estimated': 9, 'exit_plan_built': 9, 'exit_submit_start': 9, 'exit_submit_full': 5, 'exit_submit_success': 5, 'exit_reconciled': 5, 'execution_deferred': 1, 'exit_submit_zero_fill': 4, 'exit_execution_deferred': 8}`
- Reject reasons: `{'edge_below_floor': 23, 'feature_gate': 3, 'book_stale': 27, 'depth_ratio': 2, '<blank>': 14, 'single_shot_abundant_depth': 28, 'exit_trigger': 27, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 32, 'ask_too_high': 8, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 36}`
- Exchange positions: `[{'fees_paid_dollars': '0.234000', 'last_updated_ts': '2026-05-09T20:10:43.233093Z', 'market_exposure_dollars': '0.000000', 'position_fp': '0.00', 'realized_pnl_dollars': '-0.316000', 'resting_orders_count': 0, 'ticker': 'KXBTC15M-26MAY091615-15', 'total_traded_dollars': '9.316000'}]`
- Exchange active positions count: `0`
- Exchange resting orders: `[]`
- Exchange resting orders count: `0`
- Recent fills returned: `100`
- Candidate recent fills since run start: `12`
- Kalshi balance cents / portfolio cents: `2150` / `0`
- Kalshi fills/fees since run: `12` / `$0.23`
- Kalshi gross/net realized since run: `$-0.32` / `$-0.55`
- Reconciliation snapshot appended: `True`

## Artifacts
- bot_log: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\bot.log` exists=`True`
- execution_events: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\execution_events.ndjson` exists=`True`
- guard_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\mushroom_v28_exit_guard_shadow.ndjson` exists=`False`
- reconciliation_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\exchange_reconciliation.ndjson` exists=`True`
- score_summary: `stats\mushroom_v28_common_clock_phi_reward_memory_size2_live\summary.json` exists=`True`
