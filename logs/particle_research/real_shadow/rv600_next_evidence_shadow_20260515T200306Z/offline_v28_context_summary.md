# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-15T20:18:28+00:00
- research_only: True
- contexts_written: 865
- issue_count: 3
- distinct_markets: 2
- checkpoint_rows_read: 868
- spot_ticks_read: 6406
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-15T20:03:00+00:00
- first_context_ts_utc: 2026-05-15T20:03:22.916288+00:00
- last_context_ts_utc: 2026-05-15T20:18:21.965567+00:00
- min_current_calibrated_p_yes: 0.0016490124083335283
- max_current_calibrated_p_yes: 0.675070992766091
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T200306Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T200306Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
