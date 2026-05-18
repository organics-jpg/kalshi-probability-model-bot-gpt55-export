# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-13T17:22:38+00:00
- research_only: True
- contexts_written: 101
- issue_count: 2
- distinct_markets: 1
- checkpoint_rows_read: 103
- spot_ticks_read: 5411
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-13T17:12:00+00:00
- first_context_ts_utc: 2026-05-13T17:12:56.824291+00:00
- last_context_ts_utc: 2026-05-13T17:14:59.035039+00:00
- min_current_calibrated_p_yes: 0.9740807820477616
- max_current_calibrated_p_yes: 0.99999999
- output: `logs\particle_research\real_shadow\rv600_forward_native_shadow_offline_v28_20260513T1712Z_1715\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_forward_native_shadow_offline_v28_20260513T1712Z_1715\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
