# v28 Common-Clock Live Trial Status

- Generated UTC: `2026-05-10T17:07:29.334102+00:00`
- Status: `running_with_exchange_exposure`
- Strategy: `mushroom_v28_common_clock_phi_reward_memory_size2_live`
- Lock/process: `True` / `True`
- Score entries/round trips/net: `84` / `78` / `$-6.84`
- Latest event: `fill_full` / `single_shot_abundant_depth` at `2026-05-10T17:06:50.636077+00:00`
- Event counts: `{'mushroom_v28_rejected': 155, 'mushroom_v28_approved': 4, 'signal_seen': 4, 'plan_built': 4, 'order_submit_start': 6, 'order_submit_success': 6, 'fill_full': 5, 'exit_signal_seen': 2, 'exit_snapshot_built': 2, 'exit_capacity_estimated': 2, 'exit_plan_built': 2, 'exit_submit_start': 2, 'exit_submit_zero_fill': 1, 'exit_execution_deferred': 2, 'exit_submit_full': 1, 'exit_submit_success': 1, 'exit_reconciled': 1}`
- Reject reasons: `{'book_stale': 64, 'ask_too_high': 17, 'edge_below_floor': 47, 'time_window': 12, 'missing_horizon': 4, 'btc_stale': 1, 'feature_gate': 7, 'depth_ratio': 3, '<blank>': 8, 'single_shot_abundant_depth': 16, 'exit_trigger': 6, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 15}`
- Exchange positions: `[{'fees_paid_dollars': '0.150000', 'last_updated_ts': '2026-05-10T17:06:50.708553Z', 'market_exposure_dollars': '2.250000', 'position_fp': '-3.00', 'realized_pnl_dollars': '-1.190000', 'resting_orders_count': 0, 'ticker': 'KXBTC15M-26MAY101315-15', 'total_traded_dollars': '6.440000'}]`
- Exchange active positions count: `1`
- Exchange resting orders: `[]`
- Exchange resting orders count: `0`
- Recent fills returned: `100`
- Candidate recent fills since run start: `56`
- Kalshi balance cents / portfolio cents: `617` / `231`
- Kalshi fills/fees since run: `56` / `$1.36`
- Kalshi gross/net realized since run: `$-1.19` / `$-2.55`
- Reconciliation snapshot appended: `True`

## Artifacts
- bot_log: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\bot.log` exists=`True`
- execution_events: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\execution_events.ndjson` exists=`True`
- guard_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\mushroom_v28_exit_guard_shadow.ndjson` exists=`False`
- reconciliation_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\exchange_reconciliation.ndjson` exists=`True`
- score_summary: `stats\mushroom_v28_common_clock_phi_reward_memory_size2_live\summary.json` exists=`True`
