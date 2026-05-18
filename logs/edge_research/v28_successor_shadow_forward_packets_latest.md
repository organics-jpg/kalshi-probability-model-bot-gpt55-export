# v28 Successor Shadow Forward Packets

Research-only bridge from paired passive shadow captures into the v28 successor packet contract. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T07:29:30Z`
- Run root: `logs/particle_research/real_shadow/particle_shadow_forward_20260511T053741Z-long900`
- Candidate snapshots: `753`
- Packet side rows: `1506`
- Markets: `2`
- Labels joined rows: `1506`
- Registered before close rows: `840`
- Packet-ready rows: `0`
- Forward promotion rows: `0`

## Packet Missing Groups

| group | rows missing |
|---|---:|
| `identity_and_clock` | 0 |
| `causality` | 0 |
| `market_and_book` | 0 |
| `btc_and_feed` | 1506 |
| `v28_baseline` | 1506 |
| `candidate_prediction` | 0 |

## Top Missing Fields

| field | rows |
|---|---:|
| `btc_return_900s` | 1506 |
| `max_adverse_move_15m` | 1506 |
| `v28_p_anchor` | 1506 |
| `v28_p_static_boundary_field` | 1506 |
| `v28_p_recent_transport` | 1506 |
| `v28_p_long_transport` | 1506 |
| `v28_edge_gate` | 1506 |
| `v28_static_gate` | 1506 |
| `v28_transport_recent_n` | 1506 |
| `v28_transport_long_n` | 1506 |
| `v28_learned_horizon_minutes` | 1506 |
| `btc_return_300s` | 574 |
| `signed_move_5m_dollars` | 574 |
| `max_adverse_move_5m` | 574 |
| `btc_return_180s` | 348 |
| `signed_move_3m_dollars` | 348 |
| `max_adverse_move_3m` | 348 |
| `btc_return_60s` | 116 |
| `signed_move_1m_dollars` | 116 |
| `btc_return_15s` | 30 |

## Exclusions

| reason | rows |
|---|---:|
| `candidate_recorded_after_close` | 666 |
| `native_v28_component_fields_incomplete` | 1506 |
| `not_v28_successor_frozen_manifest` | 1506 |
| `shadow_sidecar_particle_candidate_not_promotable` | 1506 |

## Temporal Blockers

| blocker | rows |
|---|---:|
| `is_recomputed_after_resolution_true` | 666 |

## Read

- These rows are useful for proving the paired passive capture path can produce causal packet-shaped evidence.
- They are not promotion evidence because the candidate is a shadow particle diagnostic, not a frozen v28 successor challenger.
- Native v28 component fields such as p_anchor and transport components are still missing, so the packet contract correctly keeps packet-ready rows at zero.
