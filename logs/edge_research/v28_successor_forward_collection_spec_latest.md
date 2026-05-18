# v28 Successor Forward Collection Spec

Research-only handoff for collecting complete future forward packets. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T07:30:47Z`
- Spec version: `v28_successor_forward_collection_spec_v1`
- Required fields: `83` across `6` groups
- Recommended collection candidates: `9`
- Passive packet-ready rows now: `0`
- Shadow packet-ready rows now: `0`
- Freeze-eligible scored packet predictions now: `0`
- Frozen prediction rows now: `3126`
- Sidecar adapter status: `contract_demo_ready`
- Sidecar adapter demo packet-ready rows: `9`
- Public REST sidecar bundle status: `contract_demo_ready_not_evidence`
- Public REST sidecar bundle ready: `True`
- Public REST sidecar bundle packet rows: `18`
- Public REST sidecar batch status: `contract_demo_ready_not_evidence`
- Public REST sidecar batch markets selected: `2`
- Public REST sidecar batch packet rows: `36`
- Sidecar input bundle status: `contract_demo_ready_not_evidence`
- Sidecar input bundle ready: `True`
- Sidecar collector status: `contract_demo_ready_not_evidence`
- Sidecar collector demo packet-ready rows: `18`
- Sidecar bundle freeze handoff status: `blocked_non_promotable_bundle_rows`
- Sidecar bundle freeze handoff frozen rows: `0`
- Sidecar bundle batch handoff status: `frozen_batch_handoff_ready_for_settlement_labels`
- Sidecar bundle batch input files: `290`
- Sidecar bundle batch frozen rows: `3126`
- Sidecar bundle batch label fetch status: `settlement_labels_available`
- Sidecar bundle batch label rows: `88`
- Sidecar bundle batch label markets: `88`
- Sidecar bundle batch label join status: `joined_batch_labels_available`
- Sidecar bundle batch labeled rows: `3126`
- Sidecar bundle batch joined rows: `3126`
- Sidecar batch evidence score status: `scored_sidecar_batch_evidence`
- Sidecar batch evidence clean rows: `3126`
- Sidecar batch evidence clean markets: `88`
- Sidecar collection cycle status: `sidecar_cycle_ready_for_external_promotion_verifier`
- Sidecar collection cycle clean rows: `3126`
- Sidecar collection cycle clean markets: `88`
- Freeze handoff status: `blocked_non_promotable_input_rows`
- Freeze handoff frozen prediction rows: `0`
- Freeze handoff registry rows: `0`
- Forward label join status: `joined_labels_available`
- Forward joined label rows now: `3126`
- Forward evidence score status: `scored_forward_evidence`
- Forward evidence clean rows now: `3126`

## Field Groups

| group | fields | source | current passive missing | current shadow missing |
|---|---:|---|---:|---:|
| `btc_and_feed` | 17 | BTC tick/history buffer | 1750 | 1506 |
| `candidate_prediction` | 11 | frozen collection candidate manifests | 1750 | 0 |
| `causality` | 9 | collector runtime flags | 0 | 0 |
| `identity_and_clock` | 11 | native passive market metadata plus checkpoint clock | 0 | 0 |
| `market_and_book` | 11 | Kalshi passive orderbook checkpoint | 128 | 0 |
| `v28_baseline` | 24 | v28 FV API called at decision time | 1750 | 1506 |

## Collection Candidates

| candidate | model type | track | model hash | promotion registry allowed |
|---|---|---|---|---:|
| `v28s_logistic_calibration_v001` | `regularized_logistic` | `pure_physics` | `065072105a4f4792a473a741` | False |
| `v28s_logistic_boundary_physics_v001` | `regularized_logistic` | `pure_physics` | `a938bf30c29577fc972b5a7d` | False |
| `v28s_logistic_book_reliability_diag_v001` | `regularized_logistic` | `book_aware_diagnostic` | `1612cf1a1fd3d451ff05ccad` | False |
| `v28s_monotonic_tabular_v001` | `monotonic_tabular_calibration` | `pure_physics` | `f01a85e32739def20cd8c3b0` | False |
| `v28s_boundary_monotonic_blend_v001` | `monotonic_tabular_calibration` | `pure_physics` | `db7461bb1e38cb2256cf3530` | False |
| `v28s_boundary_monotonic_light_v001` | `monotonic_tabular_calibration` | `pure_physics` | `c1edea2fdb0e0eb8b405faf0` | False |
| `v28s_boundary_monotonic_time_safe_v001` | `monotonic_tabular_calibration` | `pure_physics` | `9b461a310d06c06b55af2e2d` | False |
| `v28s_boundary_monotonic_micro_time_safe_v001` | `monotonic_tabular_calibration` | `pure_physics` | `9c831d7954e3c65fec6c0794` | False |
| `v28s_late_dsigma_residual_tilt_v001` | `fixed_logit_residual` | `pure_physics` | `b160fbf8edd98b998b089805` | False |

## Freeze Acceptance Gates

- row is written before market_close_ts_utc
- all packet contract groups are complete
- row has no temporal blockers
- candidate prediction comes from allowed_for_forward_collection manifest and frozen model_hash
- settlement fields are absent before freeze
- frozen prediction ledger is written before resolution

## Promotion Acceptance Gates

- settled labels joined only after freeze and resolution
- source contract reports promotion-grade forward rows
- chronological holdout and post-lock forward rows beat v28 on Brier/log loss/calibration
- near-boundary and recross slices improve or do not degrade
- broad market coverage floor is met
- promotion verifier reports promotable

## Latest Blockers

- `packet_contract`: `{'btc_and_feed': 1750, 'candidate_prediction': 1750, 'causality': 0, 'identity_and_clock': 0, 'market_and_book': 128, 'v28_baseline': 1750}`
- `shadow_packets`: `{'btc_and_feed': 1506, 'candidate_prediction': 0, 'causality': 0, 'identity_and_clock': 0, 'market_and_book': 0, 'v28_baseline': 1506}`
- `packet_scoring`: `{'incomplete_input_packet:btc_and_feed,v28_baseline': 13554, 'packet_not_registered_before_close': 5994, 'temporal_blockers:is_recomputed_after_resolution_true': 5994}`
- `forward_preflight`: `['insufficient_freeze_ready_markets', 'insufficient_freeze_ready_rows', 'market_already_closed_now', 'missing_btc_state', 'missing_candidate_prediction', 'missing_top_book', 'missing_v28_baseline', 'row_not_registered_pre_resolution', 'staging_registration_not_before_close']`
- `frozen_forward`: `{}`
- `packet_adapter`: `{'btc_and_feed': 0, 'candidate_prediction': 0, 'causality': 0, 'identity_and_clock': 0, 'market_and_book': 0, 'v28_baseline': 0}`
- `public_rest_sidecar_bundle`: `{}`
- `public_rest_sidecar_batch`: `{}`
- `sidecar_bundle_batch_settlement_labels`: `{}`
- `sidecar_bundle_batch_label_join`: `{}`
- `sidecar_batch_evidence_score`: `[{'candidate_id': 'v28s_boundary_monotonic_blend_v001', 'delta_brier_candidate_minus_v28': -0.0012990272728537477, 'delta_logloss_candidate_minus_v28': -0.013564709181522194, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': [], 'forward_evidence_promotable': True, 'market_shortfall': 0, 'markets': 47, 'near_boundary_delta_brier_candidate_minus_v28': -0.00029157806472454584, 'near_boundary_rows': 184, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 234, 'rows_per_market': 4.9787234042553195, 'status': 'pass'}, {'candidate_id': 'v28s_boundary_monotonic_light_v001', 'delta_brier_candidate_minus_v28': -0.0007212087458586536, 'delta_logloss_candidate_minus_v28': -0.006753968019003964, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': [], 'forward_evidence_promotable': True, 'market_shortfall': 0, 'markets': 45, 'near_boundary_delta_brier_candidate_minus_v28': -0.0003427968915931112, 'near_boundary_rows': 178, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 228, 'rows_per_market': 5.066666666666666, 'status': 'pass'}, {'candidate_id': 'v28s_boundary_monotonic_micro_time_safe_v001', 'delta_brier_candidate_minus_v28': -0.00016214996205315968, 'delta_logloss_candidate_minus_v28': -0.0018974969456564406, 'estimated_additional_markets_needed': 30, 'estimated_markets_to_row_floor': 12, 'fail_reasons': ['insufficient_forward_rows', 'insufficient_forward_markets'], 'forward_evidence_promotable': False, 'market_shortfall': 30, 'markets': 10, 'near_boundary_delta_brier_candidate_minus_v28': -2.0885070546511342e-05, 'near_boundary_rows': 74, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 106, 'rows': 94, 'rows_per_market': 9.4, 'status': 'fail'}, {'candidate_id': 'v28s_boundary_monotonic_time_safe_v001', 'delta_brier_candidate_minus_v28': -0.0002283605261196031, 'delta_logloss_candidate_minus_v28': -0.0023925328139765556, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': [], 'forward_evidence_promotable': True, 'market_shortfall': 0, 'markets': 44, 'near_boundary_delta_brier_candidate_minus_v28': -8.205392621885021e-05, 'near_boundary_rows': 176, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 226, 'rows_per_market': 5.136363636363637, 'status': 'pass'}, {'candidate_id': 'v28s_late_dsigma_residual_tilt_v001', 'delta_brier_candidate_minus_v28': 0.000737207094893666, 'delta_logloss_candidate_minus_v28': 0.0014705718642465948, 'estimated_additional_markets_needed': 36, 'estimated_markets_to_row_floor': 21, 'fail_reasons': ['insufficient_forward_rows', 'insufficient_forward_markets', 'forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 36, 'markets': 4, 'near_boundary_delta_brier_candidate_minus_v28': 0.002706024968356424, 'near_boundary_rows': 12, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 168, 'rows': 32, 'rows_per_market': 8.0, 'status': 'fail'}, {'candidate_id': 'v28s_logistic_book_reliability_diag_v001', 'delta_brier_candidate_minus_v28': 0.22590977076748825, 'delta_logloss_candidate_minus_v28': 0.7603210372694437, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 88, 'near_boundary_delta_brier_candidate_minus_v28': 0.16640232745409334, 'near_boundary_rows': 392, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 578, 'rows_per_market': 6.568181818181818, 'status': 'fail'}, {'candidate_id': 'v28s_logistic_boundary_physics_v001', 'delta_brier_candidate_minus_v28': 0.3267802484657371, 'delta_logloss_candidate_minus_v28': 1.84910706590922, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 88, 'near_boundary_delta_brier_candidate_minus_v28': 0.3013285260731586, 'near_boundary_rows': 392, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 578, 'rows_per_market': 6.568181818181818, 'status': 'fail'}, {'candidate_id': 'v28s_logistic_calibration_v001', 'delta_brier_candidate_minus_v28': 0.024120099963944097, 'delta_logloss_candidate_minus_v28': 0.06552818723765519, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 88, 'near_boundary_delta_brier_candidate_minus_v28': 0.017007574251918206, 'near_boundary_rows': 392, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 578, 'rows_per_market': 6.568181818181818, 'status': 'fail'}, {'candidate_id': 'v28s_monotonic_tabular_v001', 'delta_brier_candidate_minus_v28': 0.0007538697215135892, 'delta_logloss_candidate_minus_v28': 0.006744982807650235, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 88, 'near_boundary_delta_brier_candidate_minus_v28': -0.001653917396952892, 'near_boundary_rows': 392, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 578, 'rows_per_market': 6.568181818181818, 'status': 'fail'}]`
- `sidecar_collection_cycle`: `[]`

## Read

- This spec is the exact collection handoff for the next passive forward run.
- It separates forward collection from promotion: collection candidates can be recorded prospectively, but registry promotion remains closed.
- The shortest path to freeze-ready rows is to capture BTC history and native v28 component fields at decision time, then score the listed candidates before close.
