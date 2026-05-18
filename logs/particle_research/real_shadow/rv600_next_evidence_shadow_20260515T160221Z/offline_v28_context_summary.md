# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-15T16:17:47+00:00
- research_only: True
- contexts_written: 835
- issue_count: 2
- distinct_markets: 2
- checkpoint_rows_read: 837
- spot_ticks_read: 9359
- warmup_candle_rows: 239
- warmup_end_utc: 2026-05-15T16:02:00+00:00
- first_context_ts_utc: 2026-05-15T16:02:42.302054+00:00
- last_context_ts_utc: 2026-05-15T16:17:40.828232+00:00
- min_current_calibrated_p_yes: 0.29018823582170655
- max_current_calibrated_p_yes: 0.996813717477603
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T160221Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T160221Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
