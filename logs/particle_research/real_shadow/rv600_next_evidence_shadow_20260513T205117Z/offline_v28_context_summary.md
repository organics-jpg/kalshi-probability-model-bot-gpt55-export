# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-13T21:06:56+00:00
- research_only: True
- contexts_written: 826
- issue_count: 2
- distinct_markets: 2
- checkpoint_rows_read: 828
- spot_ticks_read: 3490
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-13T20:51:00+00:00
- first_context_ts_utc: 2026-05-13T20:51:19.560041+00:00
- last_context_ts_utc: 2026-05-13T21:06:18.752489+00:00
- min_current_calibrated_p_yes: 9.688100254776747e-07
- max_current_calibrated_p_yes: 0.4785719220637593
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T205117Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T205117Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
