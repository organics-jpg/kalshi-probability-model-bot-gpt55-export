# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-14T02:30:11+00:00
- research_only: True
- contexts_written: 842
- issue_count: 1
- distinct_markets: 2
- checkpoint_rows_read: 843
- spot_ticks_read: 5344
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-14T02:12:00+00:00
- first_context_ts_utc: 2026-05-14T02:12:12.208428+00:00
- last_context_ts_utc: 2026-05-14T02:27:10.711054+00:00
- min_current_calibrated_p_yes: 1e-08
- max_current_calibrated_p_yes: 0.9327637723948878
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T021209Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T021209Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
