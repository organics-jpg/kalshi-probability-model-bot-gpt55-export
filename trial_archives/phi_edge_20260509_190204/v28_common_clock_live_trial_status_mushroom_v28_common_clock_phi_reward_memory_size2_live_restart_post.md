# v28 Common-Clock Live Trial Status

- Generated UTC: `2026-05-09T20:38:53.141962+00:00`
- Status: `not_running_lock_missing_or_other_strategy`
- Strategy: `mushroom_v28_common_clock_phi_reward_memory_size2_live`
- Lock/process: `False` / `False`
- Score entries/round trips/net: `30` / `28` / `$-1.20`
- Latest event: `mushroom_v28_rejected` / `book_stale` at `2026-05-09T20:25:26.933896+00:00`
- Event counts: `{'mushroom_v28_rejected': 111, 'mushroom_v28_approved': 8, 'signal_seen': 8, 'plan_built': 8, 'order_submit_start': 12, 'order_submit_success': 12, 'fill_full': 3, 'exit_signal_seen': 4, 'exit_snapshot_built': 4, 'exit_capacity_estimated': 4, 'exit_plan_built': 4, 'exit_submit_start': 4, 'exit_submit_zero_fill': 3, 'exit_execution_deferred': 6, 'exit_submit_full': 1, 'exit_submit_success': 1, 'exit_reconciled': 1, 'execution_deferred': 6}`
- Reject reasons: `{'book_stale': 45, 'edge_below_floor': 38, 'feature_gate': 11, 'depth_ratio': 8, 'warming': 2, 'btc_stale': 2, 'ask_too_high': 5, '<blank>': 16, 'single_shot_abundant_depth': 32, 'exit_trigger': 12, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 29}`
- Exchange positions: `[]`
- Exchange active positions count: `0`
- Exchange resting orders: `[]`
- Exchange resting orders count: `0`
- Recent fills returned: `100`
- Candidate recent fills since run start: `0`
- Kalshi balance cents / portfolio cents: `2123` / `0`
- Kalshi fills/fees since run: `0` / `$0.00`
- Kalshi gross/net realized since run: `$0.00` / `$0.00`
- Reconciliation snapshot appended: `True`

## Artifacts
- bot_log: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\bot.log` exists=`True`
- execution_events: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\execution_events.ndjson` exists=`True`
- guard_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\mushroom_v28_exit_guard_shadow.ndjson` exists=`False`
- reconciliation_ledger: `logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live\exchange_reconciliation.ndjson` exists=`True`
- score_summary: `stats\mushroom_v28_common_clock_phi_reward_memory_size2_live\summary.json` exists=`True`
