# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-14T05:51:47+00:00
- research_only: True
- contexts_written: 790
- issue_count: 2
- distinct_markets: 2
- checkpoint_rows_read: 792
- spot_ticks_read: 3605
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-14T05:34:00+00:00
- first_context_ts_utc: 2026-05-14T05:34:25.111765+00:00
- last_context_ts_utc: 2026-05-14T05:49:23.885283+00:00
- min_current_calibrated_p_yes: 0.7093145205969309
- max_current_calibrated_p_yes: 0.99999999
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T053423Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T053423Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
