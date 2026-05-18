# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-15T17:03:58+00:00
- research_only: True
- contexts_written: 869
- issue_count: 2
- distinct_markets: 2
- checkpoint_rows_read: 871
- spot_ticks_read: 7767
- warmup_candle_rows: 239
- warmup_end_utc: 2026-05-15T16:48:00+00:00
- first_context_ts_utc: 2026-05-15T16:48:53.069590+00:00
- last_context_ts_utc: 2026-05-15T17:03:51.879296+00:00
- min_current_calibrated_p_yes: 0.2286866651611994
- max_current_calibrated_p_yes: 0.9997319089641762
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T164836Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T164836Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
