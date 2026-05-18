# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-14T02:59:05+00:00
- research_only: True
- contexts_written: 805
- issue_count: 2
- distinct_markets: 2
- checkpoint_rows_read: 807
- spot_ticks_read: 4932
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-14T02:40:00+00:00
- first_context_ts_utc: 2026-05-14T02:40:45.035319+00:00
- last_context_ts_utc: 2026-05-14T02:55:43.998325+00:00
- min_current_calibrated_p_yes: 1e-08
- max_current_calibrated_p_yes: 0.473335267366894
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T024042Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T024042Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
