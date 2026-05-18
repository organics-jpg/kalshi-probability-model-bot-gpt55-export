# v28 Logged-Event API Replay

Research-only reconstructed replay. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T07:29:17Z`
- Replay verdict: `research_reconstructed_v28_api_replay_available_not_promotion`
- Rows: `1745`
- Replayed rows: `1745`
- Blocked rows: `0`
- Markets: `118`
- BTC cache: `2026-03-14T00:54:00.000Z` to `2026-05-07T17:14:59.999Z` rows=`78736`
- Bars fed to v28 engine: `4582`
- Promotion allowed: `False`

## Delta Summary

| quantity | count | mean abs | median abs | p95 abs | max abs |
|---|---:|---:|---:|---:|---:|
| `p_yes` | 1745 | 0.05821168 | 0.04873358 | 0.10827411 | 0.44930925 |
| `fair_yes_cents` | 1745 | 5.82117023 | 4.87339560 | 10.82741327 | 44.93095437 |
| `spot_dollars` | 1745 | 0.00000000 | 0.00000000 | 0.00000000 | 0.00000000 |

## Component Coverage

| component | rows |
|---|---:|
| `replay_p_anchor` | 1745 |
| `replay_p_static_boundary_field` | 1745 |
| `replay_p_recent_transport` | 1745 |
| `replay_p_long_transport` | 1745 |
| `replay_arrow` | 1745 |
| `replay_transport_recent_n` | 1745 |
| `replay_transport_long_n` | 1745 |

## Blocked Reasons

| reason | rows |
|---|---:|

## Read

- This is the first true v28 API call path in the successor pipeline.
- It proves the replay harness can regenerate v28 component columns from predecision BTC bars and logged market geometry.
- It is not exact live-state replay because the original tick stream and serialized live engine transport state were not captured with each decision.
- It is not promotion evidence because labels are still posthoc diagnostic labels and no frozen forward candidate predictions are registered.
