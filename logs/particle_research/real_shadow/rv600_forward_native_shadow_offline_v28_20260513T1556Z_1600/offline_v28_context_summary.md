# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-13T16:06:31+00:00
- research_only: True
- contexts_written: 147
- issue_count: 2
- distinct_markets: 1
- checkpoint_rows_read: 149
- spot_ticks_read: 17348
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-13T15:56:00+00:00
- first_context_ts_utc: 2026-05-13T15:56:23.359377+00:00
- last_context_ts_utc: 2026-05-13T15:59:58.919868+00:00
- min_current_calibrated_p_yes: 1e-08
- max_current_calibrated_p_yes: 0.0006168114877355199
- output: `logs\particle_research\real_shadow\rv600_forward_native_shadow_offline_v28_20260513T1556Z_1600\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_forward_native_shadow_offline_v28_20260513T1556Z_1600\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
