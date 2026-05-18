# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-15T02:43:28+00:00
- research_only: True
- contexts_written: 28
- issue_count: 0
- distinct_markets: 1
- checkpoint_rows_read: 28
- spot_ticks_read: 426
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-15T02:36:00+00:00
- first_context_ts_utc: 2026-05-15T02:36:56.171919+00:00
- last_context_ts_utc: 2026-05-15T02:37:23.675198+00:00
- min_current_calibrated_p_yes: 0.2507039823095906
- max_current_calibrated_p_yes: 0.33376477774792723
- output: `logs\particle_research\preflight\rv600_preflight_pairing_20260515T023653Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\preflight\rv600_preflight_pairing_20260515T023653Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
