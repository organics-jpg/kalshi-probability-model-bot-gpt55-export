# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-13T15:36:54+00:00
- research_only: True
- contexts_written: 403
- issue_count: 3
- distinct_markets: 1
- checkpoint_rows_read: 406
- spot_ticks_read: 7694
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-13T15:22:00+00:00
- first_context_ts_utc: 2026-05-13T15:22:39.228676+00:00
- last_context_ts_utc: 2026-05-13T15:29:59.130915+00:00
- min_current_calibrated_p_yes: 1e-08
- max_current_calibrated_p_yes: 0.2513018943380874
- output: `logs\particle_research\real_shadow\rv600_forward_native_shadow_offline_v28_20260513T1522Z_1530\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_forward_native_shadow_offline_v28_20260513T1522Z_1530\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
