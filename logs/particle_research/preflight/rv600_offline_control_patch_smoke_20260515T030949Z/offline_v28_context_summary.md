# RV600 Native Offline V28 Context Replay

- generated_utc: 2026-05-15T03:09:57+00:00
- research_only: True
- contexts_written: 2
- issue_count: 0
- distinct_markets: 1
- checkpoint_rows_read: 2
- spot_ticks_read: 25
- warmup_candle_rows: 240
- warmup_end_utc: 2026-05-15T03:09:00+00:00
- first_context_ts_utc: 2026-05-15T03:09:51.130096+00:00
- last_context_ts_utc: 2026-05-15T03:09:52.133128+00:00
- min_current_calibrated_p_yes: 0.08155305450922086
- max_current_calibrated_p_yes: 0.08189337593103344
- output: `logs\particle_research\preflight\rv600_offline_control_patch_smoke_20260515T030949Z\offline_v28_contexts.ndjson`
- issues: `logs\particle_research\preflight\rv600_offline_control_patch_smoke_20260515T030949Z\offline_v28_context_issues.ndjson`

## Modeling Choice

Causal offline v28 event replay from public Coinbase candles and native independent spot ticks; no live bot state, orders, or restarts.
