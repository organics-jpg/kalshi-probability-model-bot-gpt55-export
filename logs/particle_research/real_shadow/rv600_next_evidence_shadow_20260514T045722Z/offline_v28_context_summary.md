# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-14T05:14:10+00:00
- research_only: True
- contexts_written: 842
- issue_count: 5
- distinct_markets: 2
- checkpoint_rows_read: 847
- spot_ticks_read: 3714
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-14T04:57:00+00:00
- first_context_ts_utc: 2026-05-14T04:57:25.085131+00:00
- last_context_ts_utc: 2026-05-14T05:12:24.299413+00:00
- min_current_calibrated_p_yes: 0.40380315350894835
- max_current_calibrated_p_yes: 0.99999999
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T045722Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T045722Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
