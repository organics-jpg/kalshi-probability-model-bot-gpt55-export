# Paired Sidecar Spot Packet Enrichment

Research-only enrichment of sidecar packet rows with independent public BTC spot ticks available at or before each packet decision timestamp.

## Summary

- Generated UTC: `2026-05-13T11:19:48.489633+00:00`
- Run id: `20260512T120500Z-368311e2`
- Promotion allowed: `False`
- Enrichment ready: `True`
- Packet rows read: `4728`
- Matching packet rows: `18`
- Enriched packet rows: `18`
- Issue count: `0`
- Spot ticks: `75`

## Rows

| market | side | candidate | decision ts | independent spot | age ms | delta vs candle bps | ready | issue |
|---|---|---|---|---:|---:|---:|---|---|
| `KXBTC15M-26MAY120815-15` | `yes` | `v28s_logistic_calibration_v001` | `2026-05-12T12:05:01.710Z` | 80728.59000000 | 731.946 | -0.350545 | `True` | `` |
| `KXBTC15M-26MAY120815-15` | `yes` | `v28s_logistic_boundary_physics_v001` | `2026-05-12T12:05:01.710Z` | 80728.59000000 | 731.946 | -0.350545 | `True` | `` |
| `KXBTC15M-26MAY120815-15` | `yes` | `v28s_logistic_book_reliability_diag_v001` | `2026-05-12T12:05:01.710Z` | 80728.59000000 | 731.946 | -0.350545 | `True` | `` |
| `KXBTC15M-26MAY120815-15` | `yes` | `v28s_monotonic_tabular_v001` | `2026-05-12T12:05:01.710Z` | 80728.59000000 | 731.946 | -0.350545 | `True` | `` |
| `KXBTC15M-26MAY120815-15` | `yes` | `v28s_boundary_monotonic_blend_v001` | `2026-05-12T12:05:01.710Z` | 80728.59000000 | 731.946 | -0.350545 | `True` | `` |
| `KXBTC15M-26MAY120815-15` | `yes` | `v28s_boundary_monotonic_light_v001` | `2026-05-12T12:05:01.710Z` | 80728.59000000 | 731.946 | -0.350545 | `True` | `` |
| `KXBTC15M-26MAY120815-15` | `yes` | `v28s_boundary_monotonic_time_safe_v001` | `2026-05-12T12:05:01.710Z` | 80728.59000000 | 731.946 | -0.350545 | `True` | `` |
| `KXBTC15M-26MAY120815-15` | `yes` | `v28s_boundary_monotonic_micro_time_safe_v001` | `2026-05-12T12:05:01.710Z` | 80728.59000000 | 731.946 | -0.350545 | `True` | `` |
| `KXBTC15M-26MAY120815-15` | `yes` | `v28s_late_dsigma_residual_tilt_v001` | `2026-05-12T12:05:01.710Z` | 80728.59000000 | 731.946 | -0.350545 | `True` | `` |
| `KXBTC15M-26MAY120815-15` | `no` | `v28s_logistic_calibration_v001` | `2026-05-12T12:05:01.710Z` | 80728.59000000 | 731.946 | -0.350545 | `True` | `` |
| `KXBTC15M-26MAY120815-15` | `no` | `v28s_logistic_boundary_physics_v001` | `2026-05-12T12:05:01.710Z` | 80728.59000000 | 731.946 | -0.350545 | `True` | `` |
| `KXBTC15M-26MAY120815-15` | `no` | `v28s_logistic_book_reliability_diag_v001` | `2026-05-12T12:05:01.710Z` | 80728.59000000 | 731.946 | -0.350545 | `True` | `` |
| `KXBTC15M-26MAY120815-15` | `no` | `v28s_monotonic_tabular_v001` | `2026-05-12T12:05:01.710Z` | 80728.59000000 | 731.946 | -0.350545 | `True` | `` |
| `KXBTC15M-26MAY120815-15` | `no` | `v28s_boundary_monotonic_blend_v001` | `2026-05-12T12:05:01.710Z` | 80728.59000000 | 731.946 | -0.350545 | `True` | `` |
| `KXBTC15M-26MAY120815-15` | `no` | `v28s_boundary_monotonic_light_v001` | `2026-05-12T12:05:01.710Z` | 80728.59000000 | 731.946 | -0.350545 | `True` | `` |
| `KXBTC15M-26MAY120815-15` | `no` | `v28s_boundary_monotonic_time_safe_v001` | `2026-05-12T12:05:01.710Z` | 80728.59000000 | 731.946 | -0.350545 | `True` | `` |
| `KXBTC15M-26MAY120815-15` | `no` | `v28s_boundary_monotonic_micro_time_safe_v001` | `2026-05-12T12:05:01.710Z` | 80728.59000000 | 731.946 | -0.350545 | `True` | `` |
| `KXBTC15M-26MAY120815-15` | `no` | `v28s_late_dsigma_residual_tilt_v001` | `2026-05-12T12:05:01.710Z` | 80728.59000000 | 731.946 | -0.350545 | `True` | `` |

## Read

- This artifact does not modify frozen sidecar rows or any live bot state.
- It is input-quality evidence only; probability, EV ranking, PnL, and promotion gates remain separate.
