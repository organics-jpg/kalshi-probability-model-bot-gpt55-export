# Paired Sidecar Spot Packet Enrichment

Research-only enrichment of sidecar packet rows with independent public BTC spot ticks available at or before each packet decision timestamp.

## Summary

- Generated UTC: `2026-05-13T02:01:16.336262+00:00`
- Run id: `20260512T200449Z-7fbf4128`
- Promotion allowed: `False`
- Enrichment ready: `True`
- Packet rows read: `4098`
- Matching packet rows: `18`
- Enriched packet rows: `18`
- Issue count: `0`
- Spot ticks: `98`

## Rows

| market | side | candidate | decision ts | independent spot | age ms | delta vs candle bps | ready | issue |
|---|---|---|---|---:|---:|---:|---|---|
| `KXBTC15M-26MAY121615-15` | `yes` | `v28s_logistic_calibration_v001` | `2026-05-12T20:04:50.058Z` | 80869.83000000 | 304.767 | -0.190426 | `True` | `` |
| `KXBTC15M-26MAY121615-15` | `yes` | `v28s_logistic_boundary_physics_v001` | `2026-05-12T20:04:50.058Z` | 80869.83000000 | 304.767 | -0.190426 | `True` | `` |
| `KXBTC15M-26MAY121615-15` | `yes` | `v28s_logistic_book_reliability_diag_v001` | `2026-05-12T20:04:50.058Z` | 80869.83000000 | 304.767 | -0.190426 | `True` | `` |
| `KXBTC15M-26MAY121615-15` | `yes` | `v28s_monotonic_tabular_v001` | `2026-05-12T20:04:50.058Z` | 80869.83000000 | 304.767 | -0.190426 | `True` | `` |
| `KXBTC15M-26MAY121615-15` | `yes` | `v28s_boundary_monotonic_blend_v001` | `2026-05-12T20:04:50.058Z` | 80869.83000000 | 304.767 | -0.190426 | `True` | `` |
| `KXBTC15M-26MAY121615-15` | `yes` | `v28s_boundary_monotonic_light_v001` | `2026-05-12T20:04:50.058Z` | 80869.83000000 | 304.767 | -0.190426 | `True` | `` |
| `KXBTC15M-26MAY121615-15` | `yes` | `v28s_boundary_monotonic_time_safe_v001` | `2026-05-12T20:04:50.058Z` | 80869.83000000 | 304.767 | -0.190426 | `True` | `` |
| `KXBTC15M-26MAY121615-15` | `yes` | `v28s_boundary_monotonic_micro_time_safe_v001` | `2026-05-12T20:04:50.058Z` | 80869.83000000 | 304.767 | -0.190426 | `True` | `` |
| `KXBTC15M-26MAY121615-15` | `yes` | `v28s_late_dsigma_residual_tilt_v001` | `2026-05-12T20:04:50.058Z` | 80869.83000000 | 304.767 | -0.190426 | `True` | `` |
| `KXBTC15M-26MAY121615-15` | `no` | `v28s_logistic_calibration_v001` | `2026-05-12T20:04:50.058Z` | 80869.83000000 | 304.767 | -0.190426 | `True` | `` |
| `KXBTC15M-26MAY121615-15` | `no` | `v28s_logistic_boundary_physics_v001` | `2026-05-12T20:04:50.058Z` | 80869.83000000 | 304.767 | -0.190426 | `True` | `` |
| `KXBTC15M-26MAY121615-15` | `no` | `v28s_logistic_book_reliability_diag_v001` | `2026-05-12T20:04:50.058Z` | 80869.83000000 | 304.767 | -0.190426 | `True` | `` |
| `KXBTC15M-26MAY121615-15` | `no` | `v28s_monotonic_tabular_v001` | `2026-05-12T20:04:50.058Z` | 80869.83000000 | 304.767 | -0.190426 | `True` | `` |
| `KXBTC15M-26MAY121615-15` | `no` | `v28s_boundary_monotonic_blend_v001` | `2026-05-12T20:04:50.058Z` | 80869.83000000 | 304.767 | -0.190426 | `True` | `` |
| `KXBTC15M-26MAY121615-15` | `no` | `v28s_boundary_monotonic_light_v001` | `2026-05-12T20:04:50.058Z` | 80869.83000000 | 304.767 | -0.190426 | `True` | `` |
| `KXBTC15M-26MAY121615-15` | `no` | `v28s_boundary_monotonic_time_safe_v001` | `2026-05-12T20:04:50.058Z` | 80869.83000000 | 304.767 | -0.190426 | `True` | `` |
| `KXBTC15M-26MAY121615-15` | `no` | `v28s_boundary_monotonic_micro_time_safe_v001` | `2026-05-12T20:04:50.058Z` | 80869.83000000 | 304.767 | -0.190426 | `True` | `` |
| `KXBTC15M-26MAY121615-15` | `no` | `v28s_late_dsigma_residual_tilt_v001` | `2026-05-12T20:04:50.058Z` | 80869.83000000 | 304.767 | -0.190426 | `True` | `` |

## Read

- This artifact does not modify frozen sidecar rows or any live bot state.
- It is input-quality evidence only; probability, EV ranking, PnL, and promotion gates remain separate.
