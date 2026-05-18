# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-15T11:45:52+00:00
- research_only: True
- contexts_written: 831
- issue_count: 1
- distinct_markets: 2
- checkpoint_rows_read: 832
- spot_ticks_read: 3034
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-15T11:30:00+00:00
- first_context_ts_utc: 2026-05-15T11:30:46.625309+00:00
- last_context_ts_utc: 2026-05-15T11:45:44.997235+00:00
- min_current_calibrated_p_yes: 0.20556116197254737
- max_current_calibrated_p_yes: 0.9999993178656611
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T113027Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T113027Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
