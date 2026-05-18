# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-15T14:15:28+00:00
- research_only: True
- contexts_written: 661
- issue_count: 8
- distinct_markets: 1
- checkpoint_rows_read: 669
- spot_ticks_read: 21870
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-15T14:00:00+00:00
- first_context_ts_utc: 2026-05-15T14:00:24.212460+00:00
- last_context_ts_utc: 2026-05-15T14:14:59.468904+00:00
- min_current_calibrated_p_yes: 0.20325481928277062
- max_current_calibrated_p_yes: 0.99999999
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T140002Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T140002Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
