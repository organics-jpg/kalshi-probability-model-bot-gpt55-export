# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-13T20:05:21+00:00
- research_only: True
- contexts_written: 830
- issue_count: 2
- distinct_markets: 2
- checkpoint_rows_read: 832
- spot_ticks_read: 5302
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-13T19:50:00+00:00
- first_context_ts_utc: 2026-05-13T19:50:03.349516+00:00
- last_context_ts_utc: 2026-05-13T20:05:02.418266+00:00
- min_current_calibrated_p_yes: 0.28456276408612513
- max_current_calibrated_p_yes: 0.99999999
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T195001Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T195001Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
