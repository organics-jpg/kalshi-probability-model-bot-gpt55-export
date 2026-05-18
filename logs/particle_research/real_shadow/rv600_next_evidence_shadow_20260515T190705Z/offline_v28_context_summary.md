# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-15T19:22:29+00:00
- research_only: True
- contexts_written: 810
- issue_count: 3
- distinct_markets: 2
- checkpoint_rows_read: 813
- spot_ticks_read: 10088
- warmup_candle_rows: 239
- warmup_end_utc: 2026-05-15T19:07:00+00:00
- first_context_ts_utc: 2026-05-15T19:07:24.488158+00:00
- last_context_ts_utc: 2026-05-15T19:22:22.814704+00:00
- min_current_calibrated_p_yes: 1e-08
- max_current_calibrated_p_yes: 0.7159730973223389
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T190705Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T190705Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
