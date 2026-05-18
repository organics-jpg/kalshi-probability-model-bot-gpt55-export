# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-15T14:47:39+00:00
- research_only: True
- contexts_written: 843
- issue_count: 3
- distinct_markets: 2
- checkpoint_rows_read: 846
- spot_ticks_read: 20224
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-15T14:32:00+00:00
- first_context_ts_utc: 2026-05-15T14:32:33.925510+00:00
- last_context_ts_utc: 2026-05-15T14:47:32.185686+00:00
- min_current_calibrated_p_yes: 0.15742528429071395
- max_current_calibrated_p_yes: 0.99999999
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T143222Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T143222Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
