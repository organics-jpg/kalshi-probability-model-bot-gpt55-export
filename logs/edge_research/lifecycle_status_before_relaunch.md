# v28 Common-Clock Live Trial Status

- Generated UTC: `2026-05-11T02:15:52.902125+00:00`
- Status: `not_running_stale_lock`
- Strategy: `mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live`
- Lock/process: `True` / `False`
- Score entries/round trips/net: `25` / `22` / `$-0.89`
- Latest event: `mushroom_v28_rejected` / `feature_gate` at `2026-05-11T02:11:42.698557+00:00`
- Event counts: `{'mushroom_v28_rejected': 126, 'mushroom_v28_approved': 18, 'signal_seen': 18, 'plan_built': 3, 'order_submit_start': 4, 'order_submit_success': 4, 'execution_deferred': 17, 'fill_full': 2, 'exit_signal_seen': 1, 'exit_snapshot_built': 1, 'exit_capacity_estimated': 1, 'exit_plan_built': 1, 'exit_submit_start': 1, 'exit_submit_full': 1, 'exit_submit_success': 1, 'exit_reconciled': 1}`
- Reject reasons: `{'edge_below_floor': 45, 'book_stale': 50, 'feature_gate': 11, 'depth_ratio': 8, 'risk_or_depth': 2, 'btc_stale': 1, '<blank>': 51, 'single_shot_abundant_depth': 12, 'ask_too_high': 9, 'exit_trigger': 3, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 8}`
- Lifecycle actions/buckets: `{}` / `{}`
- Lifecycle latest/reward tail: `None` / `None` / `None` / `0`c
- Exchange positions: `[]`
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
- lifecycle_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\v28_trade_lifecycle.ndjson` exists=`False`
- score_summary: `stats\mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\summary.json` exists=`True`
