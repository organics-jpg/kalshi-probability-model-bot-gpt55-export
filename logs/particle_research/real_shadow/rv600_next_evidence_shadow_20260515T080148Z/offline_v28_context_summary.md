# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-15T08:17:25+00:00
- research_only: True
- contexts_written: 799
- issue_count: 1
- distinct_markets: 2
- checkpoint_rows_read: 800
- spot_ticks_read: 2961
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-15T08:02:00+00:00
- first_context_ts_utc: 2026-05-15T08:02:20.070310+00:00
- last_context_ts_utc: 2026-05-15T08:17:18.784467+00:00
- min_current_calibrated_p_yes: 1e-08
- max_current_calibrated_p_yes: 0.5731638955392786
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T080148Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T080148Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
