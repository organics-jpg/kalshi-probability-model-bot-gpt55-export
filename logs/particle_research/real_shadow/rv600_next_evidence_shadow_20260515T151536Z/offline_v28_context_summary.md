# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-15T15:31:03+00:00
- research_only: True
- contexts_written: 848
- issue_count: 2
- distinct_markets: 2
- checkpoint_rows_read: 850
- spot_ticks_read: 10251
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-15T15:15:00+00:00
- first_context_ts_utc: 2026-05-15T15:15:53.301348+00:00
- last_context_ts_utc: 2026-05-15T15:30:50.675210+00:00
- min_current_calibrated_p_yes: 1e-08
- max_current_calibrated_p_yes: 0.8093430228347908
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T151536Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T151536Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
