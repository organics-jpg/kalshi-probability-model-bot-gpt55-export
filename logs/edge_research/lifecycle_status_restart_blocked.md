# v28 Common-Clock Live Trial Status

- Generated UTC: `2026-05-11T02:10:53.935286+00:00`
- Status: `running_with_exchange_exposure`
- Strategy: `mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live`
- Lock/process: `True` / `True`
- Score entries/round trips/net: `25` / `22` / `$-0.89`
- Latest event: `fill_full` / `single_shot_abundant_depth` at `2026-05-11T02:10:30.337749+00:00`
- Event counts: `{'exit_reconciled': 1, 'mushroom_v28_rejected': 142, 'mushroom_v28_approved': 14, 'signal_seen': 14, 'execution_deferred': 12, 'plan_built': 5, 'order_submit_start': 5, 'order_submit_success': 5, 'fill_full': 2}`
- Reject reasons: `{'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 1, 'ask_too_high': 8, '<blank>': 37, 'single_shot_abundant_depth': 20, 'missing_horizon': 2, 'edge_below_floor': 56, 'book_stale': 58, 'feature_gate': 9, 'depth_ratio': 6, 'risk_or_depth': 2, 'btc_stale': 1}`
- Lifecycle actions/buckets: `{'cap_addon': 300}` / `{'danger': 300}`
- Lifecycle latest/reward tail: `lifecycle_addon_capped` / `cap_addon` / `danger` / `0`c
- Exchange positions: `[{'fees_paid_dollars': '0.020000', 'last_updated_ts': '2026-05-11T02:10:30.400324Z', 'market_exposure_dollars': '0.260000', 'position_fp': '2.00', 'realized_pnl_dollars': '0.000000', 'resting_orders_count': 0, 'ticker': 'KXBTC15M-26MAY102215-15', 'total_traded_dollars': '0.260000'}]`
- Exchange active positions count: `1`
- Exchange resting orders: `[]`
- Exchange resting orders count: `0`
- Recent fills returned: `100`
- Candidate recent fills since run start: `60`
- Kalshi balance cents / portfolio cents: `884` / `22`
- Kalshi fills/fees since run: `60` / `$1.17`
- Kalshi gross/net realized since run: `$2.15` / `$0.98`
- Reconciliation snapshot appended: `True`

## Artifacts
- bot_log: `logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\bot.log` exists=`True`
- execution_events: `logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\execution_events.ndjson` exists=`True`
- guard_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\mushroom_v28_exit_guard_shadow.ndjson` exists=`False`
- reconciliation_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\exchange_reconciliation.ndjson` exists=`True`
- lifecycle_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\v28_trade_lifecycle.ndjson` exists=`True`
- score_summary: `stats\mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\summary.json` exists=`True`
