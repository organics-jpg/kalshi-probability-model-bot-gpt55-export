# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-15T05:10:07+00:00
- research_only: True
- contexts_written: 828
- issue_count: 2
- distinct_markets: 2
- checkpoint_rows_read: 830
- spot_ticks_read: 3837
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-15T04:55:00+00:00
- first_context_ts_utc: 2026-05-15T04:55:02.429197+00:00
- last_context_ts_utc: 2026-05-15T05:10:00.938080+00:00
- min_current_calibrated_p_yes: 1e-08
- max_current_calibrated_p_yes: 0.7919830509205424
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T045448Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T045448Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
