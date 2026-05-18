# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-15T17:50:53+00:00
- research_only: True
- contexts_written: 849
- issue_count: 2
- distinct_markets: 2
- checkpoint_rows_read: 851
- spot_ticks_read: 7885
- warmup_candle_rows: 239
- warmup_end_utc: 2026-05-15T17:35:00+00:00
- first_context_ts_utc: 2026-05-15T17:35:48.411937+00:00
- last_context_ts_utc: 2026-05-15T17:50:46.712577+00:00
- min_current_calibrated_p_yes: 0.03505086007960771
- max_current_calibrated_p_yes: 0.7648158657809748
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T173507Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T173507Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
