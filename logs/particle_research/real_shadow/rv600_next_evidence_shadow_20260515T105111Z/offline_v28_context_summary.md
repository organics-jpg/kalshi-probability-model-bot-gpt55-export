# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-15T11:06:32+00:00
- research_only: True
- contexts_written: 733
- issue_count: 1
- distinct_markets: 2
- checkpoint_rows_read: 734
- spot_ticks_read: 2846
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-15T10:51:00+00:00
- first_context_ts_utc: 2026-05-15T10:51:26.825077+00:00
- last_context_ts_utc: 2026-05-15T11:06:26.076529+00:00
- min_current_calibrated_p_yes: 0.13185620697214973
- max_current_calibrated_p_yes: 0.99999999
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T105111Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T105111Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
