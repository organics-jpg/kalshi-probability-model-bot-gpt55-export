# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-13T19:36:43+00:00
- research_only: True
- contexts_written: 115
- issue_count: 0
- distinct_markets: 1
- checkpoint_rows_read: 115
- spot_ticks_read: 545
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-13T19:33:00+00:00
- first_context_ts_utc: 2026-05-13T19:33:17.652854+00:00
- last_context_ts_utc: 2026-05-13T19:35:16.044914+00:00
- min_current_calibrated_p_yes: 0.46879271087364693
- max_current_calibrated_p_yes: 0.5647196546148997
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_smoke_20260513T193315Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_smoke_20260513T193315Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
