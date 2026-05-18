# v28 Common-Clock Live Trial Status

- Generated UTC: `2026-05-11T02:11:20.382095+00:00`
- Status: `running_scored_round_trips`
- Strategy: `mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live`
- Lock/process: `True` / `True`
- Score entries/round trips/net: `25` / `22` / `$-0.89`
- Latest event: `mushroom_v28_rejected` / `edge_below_floor` at `2026-05-11T02:11:02.758914+00:00`
- Event counts: `{'mushroom_v28_rejected': 126, 'mushroom_v28_approved': 18, 'signal_seen': 18, 'plan_built': 3, 'order_submit_start': 4, 'order_submit_success': 4, 'execution_deferred': 17, 'fill_full': 2, 'exit_signal_seen': 1, 'exit_snapshot_built': 1, 'exit_capacity_estimated': 1, 'exit_plan_built': 1, 'exit_submit_start': 1, 'exit_submit_full': 1, 'exit_submit_success': 1, 'exit_reconciled': 1}`
- Reject reasons: `{'edge_below_floor': 48, 'book_stale': 50, 'feature_gate': 10, 'depth_ratio': 7, 'risk_or_depth': 2, 'btc_stale': 1, '<blank>': 51, 'single_shot_abundant_depth': 12, 'ask_too_high': 8, 'exit_trigger': 3, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 8}`
- Lifecycle actions/buckets: `{'cap_addon': 299, 'allow_bucket_disabled': 1}` / `{'danger': 300}`
- Lifecycle latest/reward tail: `lifecycle_exit_decision` / `allow_bucket_disabled` / `danger` / `0`c
- Exchange positions: `[{'fees_paid_dollars': '0.040000', 'last_updated_ts': '2026-05-11T02:11:01.18858Z', 'market_exposure_dollars': '0.000000', 'position_fp': '0.00', 'realized_pnl_dollars': '-0.020000', 'resting_orders_count': 0, 'ticker': 'KXBTC15M-26MAY102215-15', 'total_traded_dollars': '2.020000'}]`
- Exchange active positions count: `0`
- Exchange resting orders: `[]`
- Exchange resting orders count: `0`
- Recent fills returned: `100`
- Candidate recent fills since run start: `61`
- Kalshi balance cents / portfolio cents: `906` / `0`
- Kalshi fills/fees since run: `61` / `$1.19`
- Kalshi gross/net realized since run: `$2.13` / `$0.94`
- Reconciliation snapshot appended: `True`

## Artifacts
- bot_log: `logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\bot.log` exists=`True`
- execution_events: `logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\execution_events.ndjson` exists=`True`
- guard_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\mushroom_v28_exit_guard_shadow.ndjson` exists=`False`
- reconciliation_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\exchange_reconciliation.ndjson` exists=`True`
- lifecycle_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\v28_trade_lifecycle.ndjson` exists=`True`
- score_summary: `stats\mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\summary.json` exists=`True`
