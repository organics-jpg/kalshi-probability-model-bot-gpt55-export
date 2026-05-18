# Paired Sidecar Spot Packet Enrichment

Research-only enrichment of sidecar packet rows with independent public BTC spot ticks available at or before each packet decision timestamp.

## Summary

- Generated UTC: `2026-05-18T18:27:18.335294+00:00`
- Run id: `20260512T045334Z-44ba5b16`
- Promotion allowed: `False`
- Enrichment ready: `True`
- Packet rows read: `16302`
- Matching packet rows: `14`
- Enriched packet rows: `14`
- Issue count: `0`
- Spot ticks: `77`

## Rows

| market | side | candidate | decision ts | independent spot | age ms | delta vs candle bps | ready | issue |
|---|---|---|---|---:|---:|---:|---|---|
| `KXBTC15M-26MAY120100-00` | `yes` | `v28s_logistic_calibration_v001` | `2026-05-12T04:53:35.688Z` | 81188.88000000 | 54.279 | 0.001232 | `True` | `` |
| `KXBTC15M-26MAY120100-00` | `yes` | `v28s_logistic_boundary_physics_v001` | `2026-05-12T04:53:35.688Z` | 81188.88000000 | 54.279 | 0.001232 | `True` | `` |
| `KXBTC15M-26MAY120100-00` | `yes` | `v28s_logistic_book_reliability_diag_v001` | `2026-05-12T04:53:35.688Z` | 81188.88000000 | 54.279 | 0.001232 | `True` | `` |
| `KXBTC15M-26MAY120100-00` | `yes` | `v28s_monotonic_tabular_v001` | `2026-05-12T04:53:35.688Z` | 81188.88000000 | 54.279 | 0.001232 | `True` | `` |
| `KXBTC15M-26MAY120100-00` | `yes` | `v28s_boundary_monotonic_blend_v001` | `2026-05-12T04:53:35.688Z` | 81188.88000000 | 54.279 | 0.001232 | `True` | `` |
| `KXBTC15M-26MAY120100-00` | `yes` | `v28s_boundary_monotonic_light_v001` | `2026-05-12T04:53:35.688Z` | 81188.88000000 | 54.279 | 0.001232 | `True` | `` |
| `KXBTC15M-26MAY120100-00` | `yes` | `v28s_boundary_monotonic_time_safe_v001` | `2026-05-12T04:53:35.688Z` | 81188.88000000 | 54.279 | 0.001232 | `True` | `` |
| `KXBTC15M-26MAY120100-00` | `no` | `v28s_logistic_calibration_v001` | `2026-05-12T04:53:35.688Z` | 81188.88000000 | 54.279 | 0.001232 | `True` | `` |
| `KXBTC15M-26MAY120100-00` | `no` | `v28s_logistic_boundary_physics_v001` | `2026-05-12T04:53:35.688Z` | 81188.88000000 | 54.279 | 0.001232 | `True` | `` |
| `KXBTC15M-26MAY120100-00` | `no` | `v28s_logistic_book_reliability_diag_v001` | `2026-05-12T04:53:35.688Z` | 81188.88000000 | 54.279 | 0.001232 | `True` | `` |
| `KXBTC15M-26MAY120100-00` | `no` | `v28s_monotonic_tabular_v001` | `2026-05-12T04:53:35.688Z` | 81188.88000000 | 54.279 | 0.001232 | `True` | `` |
| `KXBTC15M-26MAY120100-00` | `no` | `v28s_boundary_monotonic_blend_v001` | `2026-05-12T04:53:35.688Z` | 81188.88000000 | 54.279 | 0.001232 | `True` | `` |
| `KXBTC15M-26MAY120100-00` | `no` | `v28s_boundary_monotonic_light_v001` | `2026-05-12T04:53:35.688Z` | 81188.88000000 | 54.279 | 0.001232 | `True` | `` |
| `KXBTC15M-26MAY120100-00` | `no` | `v28s_boundary_monotonic_time_safe_v001` | `2026-05-12T04:53:35.688Z` | 81188.88000000 | 54.279 | 0.001232 | `True` | `` |

## Read

- This artifact does not modify frozen sidecar rows or any live bot state.
- It is input-quality evidence only; probability, EV ranking, PnL, and promotion gates remain separate.
