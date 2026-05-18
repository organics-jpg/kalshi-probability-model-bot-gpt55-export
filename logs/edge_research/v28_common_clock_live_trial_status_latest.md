# v28 Common-Clock Live Trial Status

- Generated UTC: `2026-05-11T03:46:34.868328+00:00`
- Status: `not_running_lock_missing_or_other_strategy`
- Strategy: `mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_depthratio_live`
- Lock/process: `False` / `False`
- Score entries/round trips/net: `14` / `13` / `$-0.15`
- Latest event: `mushroom_v28_rejected` / `book_stale` at `2026-05-08T21:25:40.347064+00:00`
- Event counts: `{'exit_plan_built': 11, 'exit_submit_start': 11, 'order_submit_start': 20, 'order_submit_success': 20, 'exit_submit_zero_fill': 4, 'exit_execution_deferred': 8, 'mushroom_v28_exit_guard_shadow': 10, 'exit_signal_seen': 10, 'exit_snapshot_built': 10, 'exit_capacity_estimated': 10, 'exit_submit_full': 7, 'fill_full': 13, 'exit_submit_success': 7, 'exit_reconciled': 7, 'mushroom_v28_rejected': 19, 'mushroom_v28_approved': 10, 'signal_seen': 10, 'plan_built': 9, 'execution_deferred': 4}`
- Reject reasons: `{'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 84, 'exit_trigger': 40, 'ask_too_high': 8, '<blank>': 21, 'single_shot_abundant_depth': 36, 'feature_gate': 4, 'book_stale': 6, 'edge_below_floor': 1}`
- Lifecycle actions/buckets: `{}` / `{}`
- Lifecycle latest/reward tail: `None` / `None` / `None` / `0`c
- Exchange positions: `[]`
- Exchange active positions count: `0`
- Exchange resting orders: `[]`
- Exchange resting orders count: `0`
- Recent fills returned: `100`
- Candidate recent fills since run start: `19`
- Kalshi balance cents / portfolio cents: `832` / `0`
- Kalshi fills/fees since run: `19` / `$0.31`
- Kalshi gross/net realized since run: `$-0.09` / `$-0.40`
- Reconciliation snapshot appended: `True`

## Artifacts
- bot_log: `logs\live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_depthratio\bot.log` exists=`True`
- execution_events: `logs\live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_depthratio\execution_events.ndjson` exists=`True`
- guard_ledger: `logs\live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_depthratio\mushroom_v28_exit_guard_shadow.ndjson` exists=`True`
- reconciliation_ledger: `logs\live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_depthratio\exchange_reconciliation.ndjson` exists=`True`
- lifecycle_ledger: `logs\live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_depthratio\v28_trade_lifecycle.ndjson` exists=`False`
- score_summary: `stats\mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_depthratio_live\summary.json` exists=`True`
