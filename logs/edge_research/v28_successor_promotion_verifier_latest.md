# v28 Successor Promotion Verifier

Research-only hard gate. This report does not touch live bot state, orders, thresholds, or processes.

## Summary

- Generated UTC: `2026-05-18T20:51:50Z`
- Overall verdict: `blocked`
- Candidate count: `20`
- Blocked candidates: `20`
- Promotable candidates: `0`
- Hard blockers: `['forward_evidence_scored_and_promotable']`

## Candidate Verdicts

| variant | candidate | type | track | verdict | failed gates |
|---|---|---|---|---|---|
| `seed_diagnostic` | `v28_raw` | `baseline_v28_raw` | `baseline` | `blocked` | `candidate_is_not_baseline`, `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `forward_evidence_scored_and_promotable`, `candidate_manifest_frozen_and_inspectable` |
| `seed_diagnostic` | `v28s_logistic_calibration_v001` | `regularized_logistic` | `pure_physics` | `blocked` | `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `boundary_brier_not_degraded`, `recross_brier_not_degraded_or_unavailable`, `forward_evidence_scored_and_promotable` |
| `seed_diagnostic` | `v28s_logistic_boundary_physics_v001` | `regularized_logistic` | `pure_physics` | `blocked` | `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `boundary_brier_not_degraded`, `recross_brier_not_degraded_or_unavailable`, `forward_evidence_scored_and_promotable` |
| `seed_diagnostic` | `v28s_logistic_book_reliability_diag_v001` | `regularized_logistic` | `book_aware_diagnostic` | `blocked` | `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `boundary_brier_not_degraded`, `recross_brier_not_degraded_or_unavailable`, `forward_evidence_scored_and_promotable` |
| `seed_diagnostic` | `v28s_monotonic_tabular_v001` | `monotonic_tabular_calibration` | `pure_physics` | `blocked` | `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `boundary_brier_not_degraded`, `recross_brier_not_degraded_or_unavailable`, `forward_evidence_scored_and_promotable` |
| `seed_diagnostic` | `v28s_boundary_monotonic_blend_v001` | `monotonic_tabular_calibration` | `pure_physics` | `blocked` | `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `boundary_brier_not_degraded`, `recross_brier_not_degraded_or_unavailable`, `forward_evidence_scored_and_promotable` |
| `seed_diagnostic` | `v28s_boundary_monotonic_light_v001` | `monotonic_tabular_calibration` | `pure_physics` | `blocked` | `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `boundary_brier_not_degraded`, `recross_brier_not_degraded_or_unavailable`, `forward_evidence_scored_and_promotable` |
| `seed_diagnostic` | `v28s_boundary_monotonic_time_safe_v001` | `monotonic_tabular_calibration` | `pure_physics` | `blocked` | `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `boundary_brier_not_degraded`, `recross_brier_not_degraded_or_unavailable`, `forward_evidence_scored_and_promotable` |
| `seed_diagnostic` | `v28s_boundary_monotonic_micro_time_safe_v001` | `monotonic_tabular_calibration` | `pure_physics` | `blocked` | `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `boundary_brier_not_degraded`, `recross_brier_not_degraded_or_unavailable`, `forward_evidence_scored_and_promotable` |
| `seed_diagnostic` | `v28s_late_dsigma_residual_tilt_v001` | `fixed_logit_residual` | `pure_physics` | `blocked` | `holdout_logloss_better_than_v28` |
| `logged_events_diagnostic` | `v28_raw` | `baseline_v28_raw` | `baseline` | `blocked` | `candidate_is_not_baseline`, `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `forward_evidence_scored_and_promotable`, `candidate_manifest_frozen_and_inspectable` |
| `logged_events_diagnostic` | `v28s_logistic_calibration_v001` | `regularized_logistic` | `pure_physics` | `blocked` | `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `boundary_brier_not_degraded`, `forward_evidence_scored_and_promotable` |
| `logged_events_diagnostic` | `v28s_logistic_boundary_physics_v001` | `regularized_logistic` | `pure_physics` | `blocked` | `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `boundary_brier_not_degraded`, `forward_evidence_scored_and_promotable` |
| `logged_events_diagnostic` | `v28s_logistic_book_reliability_diag_v001` | `regularized_logistic` | `book_aware_diagnostic` | `blocked` | `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `boundary_brier_not_degraded`, `forward_evidence_scored_and_promotable` |
| `logged_events_diagnostic` | `v28s_monotonic_tabular_v001` | `monotonic_tabular_calibration` | `pure_physics` | `blocked` | `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `boundary_brier_not_degraded`, `forward_evidence_scored_and_promotable` |
| `logged_events_diagnostic` | `v28s_boundary_monotonic_blend_v001` | `monotonic_tabular_calibration` | `pure_physics` | `blocked` | `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `boundary_brier_not_degraded`, `forward_evidence_scored_and_promotable` |
| `logged_events_diagnostic` | `v28s_boundary_monotonic_light_v001` | `monotonic_tabular_calibration` | `pure_physics` | `blocked` | `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `forward_evidence_scored_and_promotable` |
| `logged_events_diagnostic` | `v28s_boundary_monotonic_time_safe_v001` | `monotonic_tabular_calibration` | `pure_physics` | `blocked` | `forward_evidence_scored_and_promotable` |
| `logged_events_diagnostic` | `v28s_boundary_monotonic_micro_time_safe_v001` | `monotonic_tabular_calibration` | `pure_physics` | `blocked` | `forward_evidence_scored_and_promotable` |
| `logged_events_diagnostic` | `v28s_late_dsigma_residual_tilt_v001` | `fixed_logit_residual` | `pure_physics` | `blocked` | `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `boundary_brier_not_degraded` |

## Gate Detail

### seed_diagnostic / v28_raw

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | False | candidate_id=v28_raw |
| `holdout_coverage` | True | rows=159 markets=36 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | False | candidate=0.15820989 baseline=0.15820989 |
| `holdout_logloss_better_than_v28` | False | candidate=0.47502182 baseline=0.47502182 |
| `boundary_brier_not_degraded` | True | slice=near_boundary_v28_40_60 candidate=0.23950671 baseline=0.23950671 rows=51 |
| `recross_brier_not_degraded_or_unavailable` | True | candidate=0.23697039 baseline=0.23697039 rows=75 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=328.00000000 shadow_expected_ev_cents=457.84290000 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | False | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={} |
| `candidate_manifest_frozen_and_inspectable` | False | model_type=baseline_v28_raw model_hash=92cd09ac8c08636c3053fd48 allowed_for_forward_collection=False diagnostic_promotion_status=baseline_not_candidate |

### seed_diagnostic / v28s_logistic_calibration_v001

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | True | candidate_id=v28s_logistic_calibration_v001 |
| `holdout_coverage` | True | rows=159 markets=36 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | False | candidate=0.18540583 baseline=0.15820989 |
| `holdout_logloss_better_than_v28` | False | candidate=0.55600000 baseline=0.47502182 |
| `boundary_brier_not_degraded` | False | slice=near_boundary_v28_40_60 candidate=0.24669493 baseline=0.23950671 rows=51 |
| `recross_brier_not_degraded_or_unavailable` | False | candidate=0.24267097 baseline=0.23697039 rows=75 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=-193.00000000 shadow_expected_ev_cents=182.84758667 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | False | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={'candidate_id': 'v28s_logistic_calibration_v001', 'delta_brier_candidate_minus_v28': 0.036523314868374346, 'delta_logloss_candidate_minus_v28': 0.10546835247237224, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 195, 'near_boundary_delta_brier_candidate_minus_v28': 0.027230451817453677, 'near_boundary_rows': 1364, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 2104, 'rows_per_market': 10.78974358974359, 'status': 'fail'} |
| `candidate_manifest_frozen_and_inspectable` | True | model_type=regularized_logistic model_hash=7d371feef5f09d24d2b83d90 allowed_for_forward_collection=True diagnostic_promotion_status=fail |

### seed_diagnostic / v28s_logistic_boundary_physics_v001

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | True | candidate_id=v28s_logistic_boundary_physics_v001 |
| `holdout_coverage` | True | rows=159 markets=36 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | False | candidate=0.18787532 baseline=0.15820989 |
| `holdout_logloss_better_than_v28` | False | candidate=0.56192761 baseline=0.47502182 |
| `boundary_brier_not_degraded` | False | slice=near_boundary_v28_40_60 candidate=0.24123810 baseline=0.23950671 rows=51 |
| `recross_brier_not_degraded_or_unavailable` | False | candidate=0.24123414 baseline=0.23697039 rows=75 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=45.00000000 shadow_expected_ev_cents=196.59438357 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | False | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={'candidate_id': 'v28s_logistic_boundary_physics_v001', 'delta_brier_candidate_minus_v28': 0.3424322391231054, 'delta_logloss_candidate_minus_v28': 1.90683520054116, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 195, 'near_boundary_delta_brier_candidate_minus_v28': 0.26328615430888, 'near_boundary_rows': 1364, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 2104, 'rows_per_market': 10.78974358974359, 'status': 'fail'} |
| `candidate_manifest_frozen_and_inspectable` | True | model_type=regularized_logistic model_hash=71c9c323a2b22c1cda078553 allowed_for_forward_collection=True diagnostic_promotion_status=fail |

### seed_diagnostic / v28s_logistic_book_reliability_diag_v001

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | True | candidate_id=v28s_logistic_book_reliability_diag_v001 |
| `holdout_coverage` | True | rows=159 markets=36 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | False | candidate=0.18662745 baseline=0.15820989 |
| `holdout_logloss_better_than_v28` | False | candidate=0.56050555 baseline=0.47502182 |
| `boundary_brier_not_degraded` | False | slice=near_boundary_v28_40_60 candidate=0.24320112 baseline=0.23950671 rows=51 |
| `recross_brier_not_degraded_or_unavailable` | False | candidate=0.24362562 baseline=0.23697039 rows=75 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=-142.00000000 shadow_expected_ev_cents=448.45303524 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | False | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={'candidate_id': 'v28s_logistic_book_reliability_diag_v001', 'delta_brier_candidate_minus_v28': 0.23846525589376374, 'delta_logloss_candidate_minus_v28': 0.7818658630244664, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 195, 'near_boundary_delta_brier_candidate_minus_v28': 0.143062724447518, 'near_boundary_rows': 1364, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 2104, 'rows_per_market': 10.78974358974359, 'status': 'fail'} |
| `candidate_manifest_frozen_and_inspectable` | True | model_type=regularized_logistic model_hash=4fd4aac68789e9c885f46767 allowed_for_forward_collection=True diagnostic_promotion_status=fail |

### seed_diagnostic / v28s_monotonic_tabular_v001

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | True | candidate_id=v28s_monotonic_tabular_v001 |
| `holdout_coverage` | True | rows=159 markets=36 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | False | candidate=0.16468951 baseline=0.15820989 |
| `holdout_logloss_better_than_v28` | False | candidate=0.49069237 baseline=0.47502182 |
| `boundary_brier_not_degraded` | False | slice=near_boundary_v28_40_60 candidate=0.24477283 baseline=0.23950671 rows=51 |
| `recross_brier_not_degraded_or_unavailable` | False | candidate=0.24676250 baseline=0.23697039 rows=75 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=94.00000000 shadow_expected_ev_cents=515.84433674 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | False | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={'candidate_id': 'v28s_monotonic_tabular_v001', 'delta_brier_candidate_minus_v28': 0.005656282970433163, 'delta_logloss_candidate_minus_v28': 0.027749630831097438, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 195, 'near_boundary_delta_brier_candidate_minus_v28': 0.001167911101211061, 'near_boundary_rows': 1364, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 2104, 'rows_per_market': 10.78974358974359, 'status': 'fail'} |
| `candidate_manifest_frozen_and_inspectable` | True | model_type=monotonic_tabular_calibration model_hash=be73833bdead411c157e790e allowed_for_forward_collection=True diagnostic_promotion_status=fail |

### seed_diagnostic / v28s_boundary_monotonic_blend_v001

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | True | candidate_id=v28s_boundary_monotonic_blend_v001 |
| `holdout_coverage` | True | rows=159 markets=36 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | False | candidate=0.16468951 baseline=0.15820989 |
| `holdout_logloss_better_than_v28` | False | candidate=0.49069237 baseline=0.47502182 |
| `boundary_brier_not_degraded` | False | slice=near_boundary_v28_40_60 candidate=0.24477283 baseline=0.23950671 rows=51 |
| `recross_brier_not_degraded_or_unavailable` | False | candidate=0.24676250 baseline=0.23697039 rows=75 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=94.00000000 shadow_expected_ev_cents=515.84433674 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | False | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={'candidate_id': 'v28s_boundary_monotonic_blend_v001', 'delta_brier_candidate_minus_v28': 0.0024051648427151073, 'delta_logloss_candidate_minus_v28': 0.0067245947683555185, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 154, 'near_boundary_delta_brier_candidate_minus_v28': 0.0018924878873253503, 'near_boundary_rows': 1156, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 1760, 'rows_per_market': 11.428571428571429, 'status': 'fail'} |
| `candidate_manifest_frozen_and_inspectable` | True | model_type=monotonic_tabular_calibration model_hash=631a5c49f164f77440c3381c allowed_for_forward_collection=True diagnostic_promotion_status=fail |

### seed_diagnostic / v28s_boundary_monotonic_light_v001

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | True | candidate_id=v28s_boundary_monotonic_light_v001 |
| `holdout_coverage` | True | rows=159 markets=36 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | False | candidate=0.16007210 baseline=0.15820989 |
| `holdout_logloss_better_than_v28` | False | candidate=0.47949743 baseline=0.47502182 |
| `boundary_brier_not_degraded` | False | slice=near_boundary_v28_40_60 candidate=0.24111896 baseline=0.23950671 rows=51 |
| `recross_brier_not_degraded_or_unavailable` | False | candidate=0.23995263 baseline=0.23697039 rows=75 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=96.00000000 shadow_expected_ev_cents=466.84889257 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | False | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={'candidate_id': 'v28s_boundary_monotonic_light_v001', 'delta_brier_candidate_minus_v28': 0.0005869509521295724, 'delta_logloss_candidate_minus_v28': 0.0016079826612204196, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 152, 'near_boundary_delta_brier_candidate_minus_v28': 0.00047868816614579646, 'near_boundary_rows': 1150, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 1754, 'rows_per_market': 11.539473684210526, 'status': 'fail'} |
| `candidate_manifest_frozen_and_inspectable` | True | model_type=monotonic_tabular_calibration model_hash=4b1b6170f9698bf3786aa5d7 allowed_for_forward_collection=True diagnostic_promotion_status=fail |

### seed_diagnostic / v28s_boundary_monotonic_time_safe_v001

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | True | candidate_id=v28s_boundary_monotonic_time_safe_v001 |
| `holdout_coverage` | True | rows=159 markets=36 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | False | candidate=0.15869814 baseline=0.15820989 |
| `holdout_logloss_better_than_v28` | False | candidate=0.47608821 baseline=0.47502182 |
| `boundary_brier_not_degraded` | False | slice=near_boundary_v28_40_60 candidate=0.23999761 baseline=0.23950671 rows=51 |
| `recross_brier_not_degraded_or_unavailable` | False | candidate=0.23782853 baseline=0.23697039 rows=75 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=298.00000000 shadow_expected_ev_cents=461.01772364 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | False | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={'candidate_id': 'v28s_boundary_monotonic_time_safe_v001', 'delta_brier_candidate_minus_v28': 6.910580132671318e-05, 'delta_logloss_candidate_minus_v28': -4.468988451650224e-05, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 151, 'near_boundary_delta_brier_candidate_minus_v28': 9.814580373065929e-05, 'near_boundary_rows': 1148, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 1752, 'rows_per_market': 11.602649006622517, 'status': 'fail'} |
| `candidate_manifest_frozen_and_inspectable` | True | model_type=monotonic_tabular_calibration model_hash=8dfbc48a962472ac6230eede allowed_for_forward_collection=True diagnostic_promotion_status=fail |

### seed_diagnostic / v28s_boundary_monotonic_micro_time_safe_v001

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | True | candidate_id=v28s_boundary_monotonic_micro_time_safe_v001 |
| `holdout_coverage` | True | rows=159 markets=36 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | False | candidate=0.15835472 baseline=0.15820989 |
| `holdout_logloss_better_than_v28` | False | candidate=0.47533780 baseline=0.47502182 |
| `boundary_brier_not_degraded` | False | slice=near_boundary_v28_40_60 candidate=0.23965286 baseline=0.23950671 rows=51 |
| `recross_brier_not_degraded_or_unavailable` | False | candidate=0.23722549 baseline=0.23697039 rows=75 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=328.00000000 shadow_expected_ev_cents=458.44384582 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | False | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={'candidate_id': 'v28s_boundary_monotonic_micro_time_safe_v001', 'delta_brier_candidate_minus_v28': 2.1972555713956066e-05, 'delta_logloss_candidate_minus_v28': -2.6895646578595223e-05, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 117, 'near_boundary_delta_brier_candidate_minus_v28': 3.438242945441594e-05, 'near_boundary_rows': 1046, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 1620, 'rows_per_market': 13.846153846153847, 'status': 'fail'} |
| `candidate_manifest_frozen_and_inspectable` | True | model_type=monotonic_tabular_calibration model_hash=5229f8966bde26448e9c4403 allowed_for_forward_collection=True diagnostic_promotion_status=fail |

### seed_diagnostic / v28s_late_dsigma_residual_tilt_v001

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | True | candidate_id=v28s_late_dsigma_residual_tilt_v001 |
| `holdout_coverage` | True | rows=159 markets=36 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | True | candidate=0.15820989 baseline=0.15820989 |
| `holdout_logloss_better_than_v28` | False | candidate=0.47502182 baseline=0.47502182 |
| `boundary_brier_not_degraded` | True | slice=near_boundary_v28_40_60 candidate=0.23950671 baseline=0.23950671 rows=51 |
| `recross_brier_not_degraded_or_unavailable` | True | candidate=0.23697039 baseline=0.23697039 rows=75 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=328.00000000 shadow_expected_ev_cents=457.84290000 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | True | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={'candidate_id': 'v28s_late_dsigma_residual_tilt_v001', 'delta_brier_candidate_minus_v28': -0.0009617142950745367, 'delta_logloss_candidate_minus_v28': -0.0038030676445250378, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': [], 'forward_evidence_promotable': True, 'market_shortfall': 0, 'markets': 111, 'near_boundary_delta_brier_candidate_minus_v28': -0.001071788171632393, 'near_boundary_rows': 984, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 1558, 'rows_per_market': 14.036036036036036, 'status': 'pass'} |
| `candidate_manifest_frozen_and_inspectable` | True | model_type=fixed_logit_residual model_hash=6c24b9d069769194cd6bf7fd allowed_for_forward_collection=True diagnostic_promotion_status=fail |

### logged_events_diagnostic / v28_raw

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | False | candidate_id=v28_raw |
| `holdout_coverage` | True | rows=412 markets=24 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | False | candidate=0.09951287 baseline=0.09951287 |
| `holdout_logloss_better_than_v28` | False | candidate=0.33764805 baseline=0.33764805 |
| `boundary_brier_not_degraded` | True | slice=near_boundary_abs_d_lte_1 candidate=0.13107656 baseline=0.13107656 rows=208 |
| `recross_brier_not_degraded_or_unavailable` | True | candidate=NA baseline=NA rows=0 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=2800.00000000 shadow_expected_ev_cents=3207.22560000 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | False | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={} |
| `candidate_manifest_frozen_and_inspectable` | False | model_type=baseline_v28_raw model_hash=92cd09ac8c08636c3053fd48 allowed_for_forward_collection=False diagnostic_promotion_status=baseline_not_candidate |

### logged_events_diagnostic / v28s_logistic_calibration_v001

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | True | candidate_id=v28s_logistic_calibration_v001 |
| `holdout_coverage` | True | rows=412 markets=24 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | False | candidate=0.15827708 baseline=0.09951287 |
| `holdout_logloss_better_than_v28` | False | candidate=0.50216490 baseline=0.33764805 |
| `boundary_brier_not_degraded` | False | slice=near_boundary_abs_d_lte_1 candidate=0.18457249 baseline=0.13107656 rows=208 |
| `recross_brier_not_degraded_or_unavailable` | True | candidate=NA baseline=NA rows=0 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=-264.00000000 shadow_expected_ev_cents=16.20296088 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | False | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={'candidate_id': 'v28s_logistic_calibration_v001', 'delta_brier_candidate_minus_v28': 0.036523314868374346, 'delta_logloss_candidate_minus_v28': 0.10546835247237224, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 195, 'near_boundary_delta_brier_candidate_minus_v28': 0.027230451817453677, 'near_boundary_rows': 1364, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 2104, 'rows_per_market': 10.78974358974359, 'status': 'fail'} |
| `candidate_manifest_frozen_and_inspectable` | True | model_type=regularized_logistic model_hash=065072105a4f4792a473a741 allowed_for_forward_collection=True diagnostic_promotion_status=fail |

### logged_events_diagnostic / v28s_logistic_boundary_physics_v001

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | True | candidate_id=v28s_logistic_boundary_physics_v001 |
| `holdout_coverage` | True | rows=412 markets=24 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | False | candidate=0.12538289 baseline=0.09951287 |
| `holdout_logloss_better_than_v28` | False | candidate=0.41022674 baseline=0.33764805 |
| `boundary_brier_not_degraded` | False | slice=near_boundary_abs_d_lte_1 candidate=0.16849443 baseline=0.13107656 rows=208 |
| `recross_brier_not_degraded_or_unavailable` | True | candidate=NA baseline=NA rows=0 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=1820.00000000 shadow_expected_ev_cents=1635.38960238 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | False | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={'candidate_id': 'v28s_logistic_boundary_physics_v001', 'delta_brier_candidate_minus_v28': 0.3424322391231054, 'delta_logloss_candidate_minus_v28': 1.90683520054116, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 195, 'near_boundary_delta_brier_candidate_minus_v28': 0.26328615430888, 'near_boundary_rows': 1364, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 2104, 'rows_per_market': 10.78974358974359, 'status': 'fail'} |
| `candidate_manifest_frozen_and_inspectable` | True | model_type=regularized_logistic model_hash=a938bf30c29577fc972b5a7d allowed_for_forward_collection=True diagnostic_promotion_status=fail |

### logged_events_diagnostic / v28s_logistic_book_reliability_diag_v001

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | True | candidate_id=v28s_logistic_book_reliability_diag_v001 |
| `holdout_coverage` | True | rows=412 markets=24 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | False | candidate=0.14113659 baseline=0.09951287 |
| `holdout_logloss_better_than_v28` | False | candidate=0.46107390 baseline=0.33764805 |
| `boundary_brier_not_degraded` | False | slice=near_boundary_abs_d_lte_1 candidate=0.15089898 baseline=0.13107656 rows=208 |
| `recross_brier_not_degraded_or_unavailable` | True | candidate=NA baseline=NA rows=0 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=223.00000000 shadow_expected_ev_cents=145.44358516 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | False | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={'candidate_id': 'v28s_logistic_book_reliability_diag_v001', 'delta_brier_candidate_minus_v28': 0.23846525589376374, 'delta_logloss_candidate_minus_v28': 0.7818658630244664, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 195, 'near_boundary_delta_brier_candidate_minus_v28': 0.143062724447518, 'near_boundary_rows': 1364, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 2104, 'rows_per_market': 10.78974358974359, 'status': 'fail'} |
| `candidate_manifest_frozen_and_inspectable` | True | model_type=regularized_logistic model_hash=1612cf1a1fd3d451ff05ccad allowed_for_forward_collection=True diagnostic_promotion_status=fail |

### logged_events_diagnostic / v28s_monotonic_tabular_v001

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | True | candidate_id=v28s_monotonic_tabular_v001 |
| `holdout_coverage` | True | rows=412 markets=24 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | False | candidate=0.10616549 baseline=0.09951287 |
| `holdout_logloss_better_than_v28` | False | candidate=0.37070987 baseline=0.33764805 |
| `boundary_brier_not_degraded` | False | slice=near_boundary_abs_d_lte_1 candidate=0.13243326 baseline=0.13107656 rows=208 |
| `recross_brier_not_degraded_or_unavailable` | True | candidate=NA baseline=NA rows=0 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=1568.00000000 shadow_expected_ev_cents=1279.85846853 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | False | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={'candidate_id': 'v28s_monotonic_tabular_v001', 'delta_brier_candidate_minus_v28': 0.005656282970433163, 'delta_logloss_candidate_minus_v28': 0.027749630831097438, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 195, 'near_boundary_delta_brier_candidate_minus_v28': 0.001167911101211061, 'near_boundary_rows': 1364, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 2104, 'rows_per_market': 10.78974358974359, 'status': 'fail'} |
| `candidate_manifest_frozen_and_inspectable` | True | model_type=monotonic_tabular_calibration model_hash=f01a85e32739def20cd8c3b0 allowed_for_forward_collection=True diagnostic_promotion_status=fail |

### logged_events_diagnostic / v28s_boundary_monotonic_blend_v001

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | True | candidate_id=v28s_boundary_monotonic_blend_v001 |
| `holdout_coverage` | True | rows=412 markets=24 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | False | candidate=0.10251092 baseline=0.09951287 |
| `holdout_logloss_better_than_v28` | False | candidate=0.35491173 baseline=0.33764805 |
| `boundary_brier_not_degraded` | False | slice=near_boundary_abs_d_lte_1 candidate=0.13243326 baseline=0.13107656 rows=208 |
| `recross_brier_not_degraded_or_unavailable` | True | candidate=NA baseline=NA rows=0 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=2152.00000000 shadow_expected_ev_cents=1406.25021763 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | False | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={'candidate_id': 'v28s_boundary_monotonic_blend_v001', 'delta_brier_candidate_minus_v28': 0.0024051648427151073, 'delta_logloss_candidate_minus_v28': 0.0067245947683555185, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 154, 'near_boundary_delta_brier_candidate_minus_v28': 0.0018924878873253503, 'near_boundary_rows': 1156, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 1760, 'rows_per_market': 11.428571428571429, 'status': 'fail'} |
| `candidate_manifest_frozen_and_inspectable` | True | model_type=monotonic_tabular_calibration model_hash=db7461bb1e38cb2256cf3530 allowed_for_forward_collection=True diagnostic_promotion_status=fail |

### logged_events_diagnostic / v28s_boundary_monotonic_light_v001

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | True | candidate_id=v28s_boundary_monotonic_light_v001 |
| `holdout_coverage` | True | rows=412 markets=24 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | False | candidate=0.09967610 baseline=0.09951287 |
| `holdout_logloss_better_than_v28` | False | candidate=0.34036483 baseline=0.33764805 |
| `boundary_brier_not_degraded` | True | slice=near_boundary_abs_d_lte_1 candidate=0.13078481 baseline=0.13107656 rows=208 |
| `recross_brier_not_degraded_or_unavailable` | True | candidate=NA baseline=NA rows=0 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=2800.00000000 shadow_expected_ev_cents=2524.46378484 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | False | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={'candidate_id': 'v28s_boundary_monotonic_light_v001', 'delta_brier_candidate_minus_v28': 0.0005869509521295724, 'delta_logloss_candidate_minus_v28': 0.0016079826612204196, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 152, 'near_boundary_delta_brier_candidate_minus_v28': 0.00047868816614579646, 'near_boundary_rows': 1150, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 1754, 'rows_per_market': 11.539473684210526, 'status': 'fail'} |
| `candidate_manifest_frozen_and_inspectable` | True | model_type=monotonic_tabular_calibration model_hash=c1edea2fdb0e0eb8b405faf0 allowed_for_forward_collection=True diagnostic_promotion_status=fail |

### logged_events_diagnostic / v28s_boundary_monotonic_time_safe_v001

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | True | candidate_id=v28s_boundary_monotonic_time_safe_v001 |
| `holdout_coverage` | True | rows=412 markets=24 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | True | candidate=0.09941267 baseline=0.09951287 |
| `holdout_logloss_better_than_v28` | True | candidate=0.33757095 baseline=0.33764805 |
| `boundary_brier_not_degraded` | True | slice=near_boundary_abs_d_lte_1 candidate=0.13095011 baseline=0.13107656 rows=208 |
| `recross_brier_not_degraded_or_unavailable` | True | candidate=NA baseline=NA rows=0 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=2800.00000000 shadow_expected_ev_cents=3050.45892571 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | False | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={'candidate_id': 'v28s_boundary_monotonic_time_safe_v001', 'delta_brier_candidate_minus_v28': 6.910580132671318e-05, 'delta_logloss_candidate_minus_v28': -4.468988451650224e-05, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 151, 'near_boundary_delta_brier_candidate_minus_v28': 9.814580373065929e-05, 'near_boundary_rows': 1148, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 1752, 'rows_per_market': 11.602649006622517, 'status': 'fail'} |
| `candidate_manifest_frozen_and_inspectable` | True | model_type=monotonic_tabular_calibration model_hash=9b461a310d06c06b55af2e2d allowed_for_forward_collection=True diagnostic_promotion_status=fail |

### logged_events_diagnostic / v28s_boundary_monotonic_micro_time_safe_v001

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | True | candidate_id=v28s_boundary_monotonic_micro_time_safe_v001 |
| `holdout_coverage` | True | rows=412 markets=24 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | True | candidate=0.09947776 baseline=0.09951287 |
| `holdout_logloss_better_than_v28` | True | candidate=0.33760147 baseline=0.33764805 |
| `boundary_brier_not_degraded` | True | slice=near_boundary_abs_d_lte_1 candidate=0.13103350 baseline=0.13107656 rows=208 |
| `recross_brier_not_degraded_or_unavailable` | True | candidate=NA baseline=NA rows=0 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=2800.00000000 shadow_expected_ev_cents=3160.19559771 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | False | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={'candidate_id': 'v28s_boundary_monotonic_micro_time_safe_v001', 'delta_brier_candidate_minus_v28': 2.1972555713956066e-05, 'delta_logloss_candidate_minus_v28': -2.6895646578595223e-05, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': ['forward_brier_not_better_than_v28', 'near_boundary_brier_degraded'], 'forward_evidence_promotable': False, 'market_shortfall': 0, 'markets': 117, 'near_boundary_delta_brier_candidate_minus_v28': 3.438242945441594e-05, 'near_boundary_rows': 1046, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 1620, 'rows_per_market': 13.846153846153847, 'status': 'fail'} |
| `candidate_manifest_frozen_and_inspectable` | True | model_type=monotonic_tabular_calibration model_hash=9c831d7954e3c65fec6c0794 allowed_for_forward_collection=True diagnostic_promotion_status=fail |

### logged_events_diagnostic / v28s_late_dsigma_residual_tilt_v001

| gate | pass | evidence |
|---|---:|---|
| `candidate_is_not_baseline` | True | candidate_id=v28s_late_dsigma_residual_tilt_v001 |
| `holdout_coverage` | True | rows=412 markets=24 required_rows=100 required_markets=20 |
| `holdout_brier_better_than_v28` | False | candidate=0.09970922 baseline=0.09951287 |
| `holdout_logloss_better_than_v28` | False | candidate=0.33769948 baseline=0.33764805 |
| `boundary_brier_not_degraded` | False | slice=near_boundary_abs_d_lte_1 candidate=0.13146838 baseline=0.13107656 rows=208 |
| `recross_brier_not_degraded_or_unavailable` | True | candidate=NA baseline=NA rows=0 |
| `shadow_economics_reported` | True | shadow_net_pnl_cents=2800.00000000 shadow_expected_ev_cents=3418.37968811 |
| `source_quality_forward_registered` | True | source_contract_ready=True evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 |
| `source_contract_promotion_ready` | True | promotion_contract_ready=True overall_verdict=promotion_grade missing_required_forward_datasets=[] |
| `frozen_forward_registry_present` | True | registry_status=active rows=16896 required_rows=200 |
| `forward_market_coverage` | True | forward_markets=196 required_markets=40 |
| `forward_evidence_scored_and_promotable` | True | evidence_status=scored_forward_evidence clean_rows=16860 clean_markets=195 candidate_gate={'candidate_id': 'v28s_late_dsigma_residual_tilt_v001', 'delta_brier_candidate_minus_v28': -0.0009617142950745367, 'delta_logloss_candidate_minus_v28': -0.0038030676445250378, 'estimated_additional_markets_needed': 0, 'estimated_markets_to_row_floor': 0, 'fail_reasons': [], 'forward_evidence_promotable': True, 'market_shortfall': 0, 'markets': 111, 'near_boundary_delta_brier_candidate_minus_v28': -0.001071788171632393, 'near_boundary_rows': 984, 'required_markets': 40, 'required_rows': 200, 'row_shortfall': 0, 'rows': 1558, 'rows_per_market': 14.036036036036036, 'status': 'pass'} |
| `candidate_manifest_frozen_and_inspectable` | True | model_type=fixed_logit_residual model_hash=b160fbf8edd98b998b089805 allowed_for_forward_collection=True diagnostic_promotion_status=fail |

## Read

- No candidate is promotable unless every gate passes at once.
- Probability quality gates are checked before economics.
- Frozen forward registry and source-quality gates are hard blockers, so diagnostic/posthoc wins cannot pass.
