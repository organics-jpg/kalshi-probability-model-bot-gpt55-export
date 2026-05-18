# v28 Successor Forward Source Readiness

Research-only source readiness audit. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-18T20:51:50Z`
- Overall status: `blocked_missing_freeze_ready_sources`
- Passive rows / markets: `1750` / `2`
- Research datasets / markets: `16` / `61`
- Live v28 event rows: `16078`
- Live v28 base-field rows: `4233`
- Live v28 native component rows: `0`
- Forward packet prediction rows: `13554`
- Freeze-eligible packet prediction rows: `0`
- Sidecar collector status: `contract_demo_ready_not_evidence`
- Sidecar collector demo packet-ready rows: `18`
- Sidecar collector promotion allowed: `False`
- Sidecar batch joined rows / markets: `16860` / `195`
- Sidecar batch evidence status: `scored_sidecar_batch_evidence`
- Sidecar batch evidence promotion allowed: `False`
- Frozen forward rows: `16896`
- Forward registry rows: `16896`
- Forward labeled rows: `16860`
- Source contract promotion-ready: `True`
- Promotion allowed by this report: `False`

## Blockers

- `live_v28_events_missing_native_component_fields`
- `no_freeze_eligible_forward_packet_candidate_predictions`
- `packet_predictions_not_allowed_for_forward_registry`
- `passive_market_coverage_below_forward_floor`
- `passive_rows_missing_btc_state`
- `passive_rows_missing_candidate_prediction`
- `passive_rows_missing_settlement_label`
- `passive_rows_missing_top_book`
- `passive_rows_missing_v28_baseline`
- `recorded_research_datasets_do_not_include_settlement_labels`
- `recorded_research_datasets_do_not_include_strategy_decisions`
- `sidecar_packet_collector_rows_are_demo_not_forward_evidence`

## Passive Snapshot Coverage

- Path: `research_particle/v28_successor/passive_forward_snapshots_latest.csv`
- Rows: `1750`
- Markets: `2`
- Registered pre-resolution rows: `0`
- Missing counts: `{'btc_state': 1750, 'v28_baseline': 1750, 'candidate_prediction': 1750, 'settlement_label': 1750, 'top_book': 128}`

## Live v28 Event Coverage

- Path: `logs/live_mushroom_v28_size2/execution_events.ndjson`
- Rows with v28 base fields: `4233`
- Rows with native v28 component fields: `0`
- Rows with legacy component fields: `3155`
- Required native component fields: `['mushroom_v28_p_anchor', 'mushroom_v28_p_static_boundary_field', 'mushroom_v28_p_recent_transport', 'mushroom_v28_p_long_transport', 'mushroom_v28_transport_recent_n', 'mushroom_v28_transport_long_n']`

## Sidecar Collector

- Path: `research_particle/v28_successor/forward_sidecar_packet_collection_demo_latest.csv`
- Rows: `18`
- Packet-ready-like rows: `18`
- Simulated rows: `18`
- Diagnostic rows: `18`
- Collector status: `contract_demo_ready_not_evidence`
- Promotion allowed: `False`

## Sidecar Batch Evidence

- Path: `research_particle/v28_successor/sidecar_bundle_batch_labeled_latest.csv`
- Joined rows: `16860`
- Joined markets: `195`
- Evidence status: `scored_sidecar_batch_evidence`
- Candidate count: `9`
- Promotable candidates by this evidence alone: `1`
- Promotion allowed: `False`

## Research Datasets

| dataset | markets | checkpoints | raw event types | labels | decisions |
|---|---:|---:|---|---:|---:|
| `particle_dynamic600_oos_20260511TLOCKEDNEXT2` | 6 | 3543 | `{'market_rotated': 2, 'orderbook_delta': 2, 'orderbook_snapshot': 2, 'ticker': 2, 'watch_market': 2, 'ws_connected': 2, 'ws_subscribed': 2}` | False | False |
| `particle_dynamic_oos_20260511TLOCKEDNEXT` | 5 | 3587 | `{'market_rotated': 2, 'orderbook_delta': 2, 'orderbook_snapshot': 2, 'ticker': 2, 'watch_market': 2, 'ws_connected': 2, 'ws_subscribed': 2}` | False | False |
| `particle_fixed_terminal_oos_GAUSS45LOCK001` | 6 | 3537 | `{'market_rotated': 2, 'orderbook_delta': 2, 'orderbook_snapshot': 2, 'ticker': 2, 'watch_market': 2, 'ws_connected': 2, 'ws_subscribed': 2}` | False | False |
| `particle_fixed_terminal_oos_GAUSS45LOCK002` | 7 | 5068 | `{'market_rotated': 2, 'orderbook_delta': 3, 'orderbook_snapshot': 3, 'ticker': 3, 'watch_market': 3, 'ws_connected': 3, 'ws_subscribed': 3}` | False | False |
| `particle_fixed_terminal_oos_GAUSS45LOCK003` | 7 | 4990 | `{'market_rotated': 2, 'orderbook_delta': 2, 'orderbook_snapshot': 2, 'ticker': 2, 'watch_market': 2, 'ws_connected': 2, 'ws_subscribed': 2}` | False | False |
| `particle_residual_blend_oos_RESIDLOCK001` | 5 | 3633 | `{'market_rotated': 2, 'orderbook_delta': 2, 'orderbook_snapshot': 2, 'ticker': 2, 'watch_market': 2, 'ws_connected': 2, 'ws_subscribed': 2}` | False | False |
| `particle_shadow_forward_20260511T053112Z-47457a12` | 1 | 29 | `{'orderbook_delta': 1, 'orderbook_snapshot': 1, 'ticker': 1, 'watch_market': 1, 'ws_connected': 1, 'ws_subscribed': 1}` | False | False |
| `particle_shadow_forward_20260511T053340Z-0dc86f34` | 1 | 29 | `{'orderbook_delta': 1, 'orderbook_snapshot': 1, 'ticker': 1, 'watch_market': 1, 'ws_connected': 1, 'ws_subscribed': 1}` | False | False |
| `particle_shadow_forward_20260511T053741Z-long900` | 2 | 818 | `{'market_rotated': 1, 'orderbook_delta': 1, 'orderbook_snapshot': 1, 'ticker': 1, 'watch_market': 1, 'ws_connected': 1, 'ws_subscribed': 1}` | False | False |
| `particle_shadow_readonly` | 1 | 72 | `{'orderbook_delta': 1, 'orderbook_snapshot': 1, 'ticker': 1, 'watch_market': 1, 'ws_connected': 1, 'ws_subscribed': 1}` | False | False |
| `particle_shadow_readonly_fresh_20260511T113926Z` | 1 | 175 | `{'orderbook_delta': 1, 'orderbook_snapshot': 1, 'ticker': 1, 'watch_market': 1, 'ws_connected': 1, 'ws_subscribed': 1}` | False | False |
| `particle_shadow_spotmerge_oos_20260511T121730Z` | 2 | 772 | `{'market_rotated': 1, 'orderbook_delta': 1, 'orderbook_snapshot': 1, 'ticker': 1, 'watch_market': 1, 'ws_connected': 1, 'ws_subscribed': 1}` | False | False |
| `particle_shadow_spotmerge_smoke_20260511T120911Z` | 1 | 29 | `{'orderbook_delta': 1, 'orderbook_snapshot': 1, 'ticker': 1, 'watch_market': 1, 'ws_connected': 1, 'ws_subscribed': 1}` | False | False |
| `particle_side_consensus_oos_CONSENSUSLOCK001` | 6 | 3520 | `{'market_rotated': 2, 'orderbook_delta': 3, 'orderbook_snapshot': 3, 'ticker': 3, 'watch_market': 3, 'ws_connected': 3, 'ws_subscribed': 3}` | False | False |
| `particle_side_safety_oos_20260511TLOCKED` | 5 | 3559 | `{'market_rotated': 2, 'orderbook_delta': 2, 'orderbook_snapshot': 2, 'ticker': 2, 'watch_market': 2, 'ws_connected': 2, 'ws_subscribed': 2}` | False | False |
| `particle_spot_rv_terminal_oos_RVTERMLOCK001` | 7 | 4884 | `{'market_rotated': 2, 'orderbook_delta': 3, 'orderbook_snapshot': 3, 'ticker': 3, 'watch_market': 3, 'ws_connected': 3, 'ws_subscribed': 3}` | False | False |

## Read

- Passive book data exists, but current rows are not freeze-ready because they are not paired with BTC state, native v28 component packets, and candidate predictions at capture time.
- Sidecar batch evidence is now scored separately, but it remains below coverage floors and does not replace the canonical promotion ledger.
- Existing live v28 logs contain many base FV fields, but the native p_anchor/static/recent/long component fields are not present under the v28 names required for promotion-grade packets.
- This report is diagnostic and does not grant promotion.
