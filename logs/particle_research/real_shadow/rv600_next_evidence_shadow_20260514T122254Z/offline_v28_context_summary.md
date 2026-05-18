# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-14T12:40:37+00:00
- research_only: True
- contexts_written: 844
- issue_count: 6
- distinct_markets: 2
- checkpoint_rows_read: 850
- spot_ticks_read: 3470
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-14T12:23:00+00:00
- first_context_ts_utc: 2026-05-14T12:23:17.942353+00:00
- last_context_ts_utc: 2026-05-14T12:38:16.958974+00:00
- min_current_calibrated_p_yes: 0.3743524835958512
- max_current_calibrated_p_yes: 0.99999999
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T122254Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T122254Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
