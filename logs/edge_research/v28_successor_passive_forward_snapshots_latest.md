# v28 Successor Passive Forward Snapshots

Research-only passive capture staging. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T07:29:26Z`
- Snapshot status: `staging_not_promotable`
- Datasets: `3`
- Checkpoints: `876`
- Rows: `1750`
- Markets: `2`
- Pre-resolution rows: `1750`
- Post-resolution rows rejected: `2`
- Registered-before-close rows: `0`
- Candidate-ready staging rows: `1622`
- Forward-promotion rows: `0`

## Missing Pieces

| item | rows missing |
|---|---:|
| `market_close_ts_utc` | 0 |
| `strike` | 0 |
| `ask_cents` | 64 |
| `btc_state` | 1750 |
| `v28_baseline` | 1750 |
| `candidate_prediction` | 1750 |
| `settlement_label` | 1750 |

## Source Datasets

| dataset | checkpoints | rows | markets | records labels | records decisions |
|---|---:|---:|---|---:|---:|
| `particle_shadow_forward_20260511T053112Z-47457a12` | 29 | 58 | `['KXBTC15M-26MAY110145-45']` | False | False |
| `particle_shadow_forward_20260511T053340Z-0dc86f34` | 29 | 58 | `['KXBTC15M-26MAY110145-45']` | False | False |
| `particle_shadow_forward_20260511T053741Z-long900` | 818 | 1634 | `['KXBTC15M-26MAY110145-45', 'KXBTC15M-26MAY110200-00']` | False | False |

## Exclusion Reasons

| reason | rows |
|---|---:|
| `missing_btc_state` | 1750 |
| `missing_candidate_prediction` | 1750 |
| `missing_settlement_label` | 1750 |
| `missing_top_book` | 128 |
| `missing_v28_baseline` | 1750 |
| `not_frozen_candidate_prediction_registry` | 1750 |

## Read

- These rows are useful staging inputs for a future frozen forward registry.
- They are not sufficient for promotion because they do not contain BTC state, v28 API outputs, candidate predictions, or settlement labels.
- Rows generated after a market close must remain non-promotable even if their raw capture timestamps were pre-resolution.
