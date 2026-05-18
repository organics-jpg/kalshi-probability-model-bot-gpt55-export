# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-13T21:35:24+00:00
- research_only: True
- contexts_written: 837
- issue_count: 2
- distinct_markets: 2
- checkpoint_rows_read: 839
- spot_ticks_read: 2706
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-13T21:19:00+00:00
- first_context_ts_utc: 2026-05-13T21:19:51.564973+00:00
- last_context_ts_utc: 2026-05-13T21:34:50.672631+00:00
- min_current_calibrated_p_yes: 0.00010444340332192369
- max_current_calibrated_p_yes: 0.7010953606021033
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T211949Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T211949Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
