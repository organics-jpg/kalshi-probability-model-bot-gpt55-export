# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-13T22:07:29+00:00
- research_only: True
- contexts_written: 834
- issue_count: 2
- distinct_markets: 2
- checkpoint_rows_read: 836
- spot_ticks_read: 5298
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-13T21:51:00+00:00
- first_context_ts_utc: 2026-05-13T21:51:32.612613+00:00
- last_context_ts_utc: 2026-05-13T22:06:31.195957+00:00
- min_current_calibrated_p_yes: 1e-08
- max_current_calibrated_p_yes: 0.7530247012581066
- output: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T215130Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T215130Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
