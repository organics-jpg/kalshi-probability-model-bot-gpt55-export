# v28 Common-Clock Live Trial Status

- Generated UTC: `2026-05-09T20:12:34.196841+00:00`
- Status: `running_scored_round_trips`
- Strategy: `mushroom_v28_common_clock_phi_reward_memory_size2_live`
- Lock/process: `True` / `True`
- Score entries/round trips/net: `29` / `27` / `$-1.04`
- Latest event: `mushroom_v28_rejected` / `book_stale` at `2026-05-09T20:12:18.588869+00:00`
- Event counts: `{'exit_snapshot_built': 9, 'exit_capacity_estimated': 9, 'exit_plan_built': 9, 'exit_submit_start': 9, 'order_submit_start': 16, 'order_submit_success': 16, 'exit_submit_full': 5, 'fill_full': 11, 'exit_submit_success': 5, 'exit_reconciled': 5, 'mushroom_v28_rejected': 64, 'mushroom_v28_approved': 7, 'signal_seen': 7, 'plan_built': 7, 'exit_signal_seen': 8, 'execution_deferred': 1, 'exit_submit_zero_fill': 4, 'exit_execution_deferred': 8}`
- Reject reasons: `{'exit_trigger': 26, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 24, 'edge_below_floor': 19, 'book_stale': 30, '<blank>': 14, 'single_shot_abundant_depth': 28, 'ask_too_high': 12, 'feature_gate': 2, 'depth_ratio': 1, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 36, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 8}`
- Exchange positions: `[{'fees_paid_dollars': '0.279000', 'last_updated_ts': '2026-05-09T20:11:38.364162Z', 'market_exposure_dollars': '0.000000', 'position_fp': '0.00', 'realized_pnl_dollars': '-0.361000', 'resting_orders_count': 0, 'ticker': 'KXBTC15M-26MAY091615-15', 'total_traded_dollars': '12.361000'}]`
- Exchange active positions count: `0`
- Exchange resting orders: `[]`
- Exchange resting orders count: `0`
- Recent fills returned: `100`
- Candidate recent fills since run start: `15`
- Kalshi balance cents / portfolio cents: `2141` / `0`
- Kalshi fills/fees since run: `15` / `$0.28`
- Kalshi gross/net realized since run: `$-0.36` / `$-0.64`
- Reconciliation snapshot appended: `True`

## Artifacts
- bot_log: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\bot.log` exists=`True`
- execution_events: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\execution_events.ndjson` exists=`True`
- guard_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\mushroom_v28_exit_guard_shadow.ndjson` exists=`False`
- reconciliation_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\exchange_reconciliation.ndjson` exists=`True`
- score_summary: `stats\mushroom_v28_common_clock_phi_reward_memory_size2_live\summary.json` exists=`True`
