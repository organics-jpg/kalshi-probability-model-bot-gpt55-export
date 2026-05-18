# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-13T20:36:24+00:00
- research_only: True
- contexts_written: 840
- issue_count: 2
- distinct_markets: 2
- checkpoint_rows_read: 842
- spot_ticks_read: 3916
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-13T20:20:00+00:00
- first_context_ts_utc: 2026-05-13T20:20:36.510758+00:00
- last_context_ts_utc: 2026-05-13T20:35:35.780283+00:00
- min_current_calibrated_p_yes: 1e-08
- max_current_calibrated_p_yes: 0.8571796543821498
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T202034Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T202034Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
