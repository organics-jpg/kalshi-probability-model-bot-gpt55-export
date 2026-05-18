# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-14T03:29:57+00:00
- research_only: True
- contexts_written: 837
- issue_count: 2
- distinct_markets: 2
- checkpoint_rows_read: 839
- spot_ticks_read: 6418
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-14T03:14:00+00:00
- first_context_ts_utc: 2026-05-14T03:14:22.666870+00:00
- last_context_ts_utc: 2026-05-14T03:29:21.901820+00:00
- min_current_calibrated_p_yes: 1e-08
- max_current_calibrated_p_yes: 0.992568052863448
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T031420Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T031420Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
