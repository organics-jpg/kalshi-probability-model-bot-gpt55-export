# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-13T22:36:25+00:00
- research_only: True
- contexts_written: 817
- issue_count: 2
- distinct_markets: 2
- checkpoint_rows_read: 819
- spot_ticks_read: 4341
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-13T22:20:00+00:00
- first_context_ts_utc: 2026-05-13T22:20:23.059669+00:00
- last_context_ts_utc: 2026-05-13T22:35:22.170342+00:00
- min_current_calibrated_p_yes: 1e-08
- max_current_calibrated_p_yes: 0.5469228503648066
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T222021Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T222021Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
