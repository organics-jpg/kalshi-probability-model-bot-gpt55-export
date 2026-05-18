# v28 Successor Forward Packet Contract

Research-only packet validator. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T07:29:27Z`
- Contract: `v28_successor_forward_packet_v1`
- Packet status: `blocked`
- Input rows: `1750`
- Packet-ready rows: `0`
- Packet-ready markets: `0`

## Missing Groups

| group | rows missing | required fields |
|---|---:|---|
| `identity_and_clock` | 0 | `row_id, market_ticker, decision_ts_utc, market_close_ts_utc, strike, seconds_to_close, side, source_file, source_line_or_offset, source_type, source_quality_tier` |
| `causality` | 0 | `is_pre_resolution, is_pre_resolution_registered, is_recomputed_after_resolution, is_backfilled, is_simulated, is_sidecar, is_diagnostic_only, allowed_for_forward_promotion, exclusion_reason` |
| `market_and_book` | 128 | `yes_bid_cents, yes_ask_cents, no_bid_cents, no_ask_cents, ask_cents, bid_cents, book_implied_yes_from_side_ask, book_mid_yes_cents, book_width_cents, book_source_event_count, raw_capture_ts_utc` |
| `btc_and_feed` | 1750 | `btc_spot, btc_source, btc_tick_ts_utc, btc_tick_age_ms, reference_spot, btc_stale_flag, btc_return_15s, btc_return_60s, btc_return_180s, btc_return_300s, btc_return_900s, signed_move_1m_dollars, signed_move_3m_dollars, signed_move_5m_dollars, max_adverse_move_3m, max_adverse_move_5m, max_adverse_move_15m` |
| `v28_baseline` | 1750 | `v28_p_yes, v28_p_no, v28_p_side, v28_best_side, v28_fair_yes_cents, v28_fair_no_cents, v28_best_fair_cents, v28_yes_edge_cents, v28_no_edge_cents, v28_best_edge_cents, v28_p_anchor, v28_p_static_boundary_field, v28_p_recent_transport, v28_p_long_transport, v28_edge_gate, v28_static_gate, v28_arrow, v28_volshock, v28_transport_recent_n, v28_transport_long_n, v28_learned_horizon_minutes, v28_effective_horizon_minutes, v28_sigma_t_dollars, v28_d_sigma` |
| `candidate_prediction` | 1750 | `candidate_id, model_hash, model_type, model_track, candidate_p_yes, candidate_fair_yes_cents, candidate_fair_no_cents, candidate_fair_side_cents, candidate_edge_cents, candidate_feature_manifest_hash, candidate_feature_table_hash` |

## Top Missing Fields

| field | rows missing |
|---|---:|
| `btc_spot` | 1750 |
| `btc_source` | 1750 |
| `btc_tick_ts_utc` | 1750 |
| `btc_tick_age_ms` | 1750 |
| `reference_spot` | 1750 |
| `btc_stale_flag` | 1750 |
| `btc_return_15s` | 1750 |
| `btc_return_60s` | 1750 |
| `btc_return_180s` | 1750 |
| `btc_return_300s` | 1750 |
| `btc_return_900s` | 1750 |
| `signed_move_1m_dollars` | 1750 |
| `signed_move_3m_dollars` | 1750 |
| `signed_move_5m_dollars` | 1750 |
| `max_adverse_move_3m` | 1750 |
| `max_adverse_move_5m` | 1750 |
| `max_adverse_move_15m` | 1750 |
| `v28_p_yes` | 1750 |
| `v28_p_no` | 1750 |
| `v28_p_side` | 1750 |
| `v28_best_side` | 1750 |
| `v28_fair_yes_cents` | 1750 |
| `v28_fair_no_cents` | 1750 |
| `v28_best_fair_cents` | 1750 |
| `v28_yes_edge_cents` | 1750 |
| `v28_no_edge_cents` | 1750 |
| `v28_best_edge_cents` | 1750 |
| `v28_p_anchor` | 1750 |
| `v28_p_static_boundary_field` | 1750 |
| `v28_p_recent_transport` | 1750 |
| `v28_p_long_transport` | 1750 |
| `v28_edge_gate` | 1750 |
| `v28_static_gate` | 1750 |
| `v28_arrow` | 1750 |
| `v28_volshock` | 1750 |
| `v28_transport_recent_n` | 1750 |
| `v28_transport_long_n` | 1750 |
| `v28_learned_horizon_minutes` | 1750 |
| `v28_effective_horizon_minutes` | 1750 |
| `v28_sigma_t_dollars` | 1750 |

## Temporal Blockers

| blocker | rows |
|---|---:|

## Forbidden Before Freeze

- `y_yes_win`
- `settlement_price`
- `settlement_ts_utc`
- `settlement_source`
- `settlement_margin_dollars`
- `settlement_side`
- `final_average_window_end_utc`

## Read

- This is the exact packet contract a future live/passive recorder must satisfy before freezing candidate predictions.
- Current passive rows fail because they lack BTC/feed, v28 baseline, and candidate prediction groups.
- Settlement fields are explicitly forbidden before freeze and should be joined only after market resolution.
