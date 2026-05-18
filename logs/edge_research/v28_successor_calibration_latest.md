# v28 Successor Calibration Report

Research-only candidate training/scoring artifact. Live trading code, state, orders, thresholds, and processes were not touched.

## Summary

- Generated UTC: `2026-05-12T07:29:20Z`
- Feature table: `research_particle/v28_successor/features_latest.csv`
- Feature table hash: `5e97c9adf75860f1005f2d798c3b7c8b428e7e3225b830fff312672483e11228`
- Feature manifest hash: `a58dc512780c61f24226431e`
- Rows: `795`
- Candidates: `10`
- Promotion verdict: `not_promotable`

## Splits

| split | rows | markets | start decision UTC | end decision UTC |
|---|---:|---:|---|---|
| `train` | 497 | 105 | `2026-05-05T12:50:05.753Z` | `2026-05-06T16:28:39.164Z` |
| `validation` | 139 | 35 | `2026-05-06T16:30:15.772Z` | `2026-05-07T01:10:20.216Z` |
| `chronological_holdout` | 159 | 36 | `2026-05-07T01:20:14.359Z` | `2026-05-07T13:18:57.437Z` |
| `post_freeze_forward` | 0 | 0 |  |  |

## Chronological Holdout

| candidate | track | Brier | logloss | ECE | side acc | proxy-boundary Brier | true-boundary Brier | high-recross Brier | shadow net c | gate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `v28_raw` | `baseline` | 0.158210 | 0.475022 | 0.091158 | 74.21% | 0.239507 | NA | 0.236970 | 328.0 | `baseline_not_candidate` |
| `v28s_logistic_calibration_v001` | `pure_physics` | 0.185406 | 0.556000 | 0.192033 | 72.96% | 0.246695 | NA | 0.242671 | -193.0 | `fail` |
| `v28s_logistic_boundary_physics_v001` | `pure_physics` | 0.187875 | 0.561928 | 0.191517 | 77.36% | 0.241238 | NA | 0.241234 | 45.0 | `fail` |
| `v28s_logistic_book_reliability_diag_v001` | `book_aware_diagnostic` | 0.186627 | 0.560506 | 0.165844 | 73.58% | 0.243201 | NA | 0.243626 | -142.0 | `fail` |
| `v28s_monotonic_tabular_v001` | `pure_physics` | 0.164690 | 0.490692 | 0.099097 | 74.21% | 0.244773 | NA | 0.246763 | 94.0 | `fail` |
| `v28s_boundary_monotonic_blend_v001` | `pure_physics` | 0.164690 | 0.490692 | 0.099097 | 74.21% | 0.244773 | NA | 0.246763 | 94.0 | `fail` |
| `v28s_boundary_monotonic_light_v001` | `pure_physics` | 0.160072 | 0.479497 | 0.092231 | 74.21% | 0.241119 | NA | 0.239953 | 96.0 | `fail` |
| `v28s_boundary_monotonic_time_safe_v001` | `pure_physics` | 0.158698 | 0.476088 | 0.091447 | 74.21% | 0.239998 | NA | 0.237829 | 298.0 | `fail` |
| `v28s_boundary_monotonic_micro_time_safe_v001` | `pure_physics` | 0.158355 | 0.475338 | 0.091245 | 74.21% | 0.239653 | NA | 0.237225 | 328.0 | `fail` |
| `v28s_late_dsigma_residual_tilt_v001` | `pure_physics` | 0.158210 | 0.475022 | 0.091158 | 74.21% | 0.239507 | NA | 0.236970 | 328.0 | `fail` |

## Gate Read

- `v28s_logistic_calibration_v001` is not promotable: `high_recross_brier_not_degraded`, `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `near_boundary_brier_not_degraded`, `no_post_lock_forward_rows`, `post_freeze_forward_rows_present`, `seed_rows_are_posthoc_diagnostic`, `source_quality_promotable`, `source_rows_are_diagnostic_not_forward_registered`, `strike_missing_in_current_seed_boundary_distance_is_proxy`, `true_boundary_abs_d_lte_1_brier_not_degraded`.
- `v28s_logistic_boundary_physics_v001` is not promotable: `high_recross_brier_not_degraded`, `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `near_boundary_brier_not_degraded`, `no_post_lock_forward_rows`, `post_freeze_forward_rows_present`, `seed_rows_are_posthoc_diagnostic`, `source_quality_promotable`, `source_rows_are_diagnostic_not_forward_registered`, `strike_missing_in_current_seed_boundary_distance_is_proxy`, `true_boundary_abs_d_lte_1_brier_not_degraded`.
- `v28s_logistic_book_reliability_diag_v001` is not promotable: `high_recross_brier_not_degraded`, `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `near_boundary_brier_not_degraded`, `no_post_lock_forward_rows`, `post_freeze_forward_rows_present`, `seed_rows_are_posthoc_diagnostic`, `source_quality_promotable`, `source_rows_are_diagnostic_not_forward_registered`, `strike_missing_in_current_seed_boundary_distance_is_proxy`, `true_boundary_abs_d_lte_1_brier_not_degraded`.
- `v28s_monotonic_tabular_v001` is not promotable: `high_recross_brier_not_degraded`, `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `near_boundary_brier_not_degraded`, `no_post_lock_forward_rows`, `post_freeze_forward_rows_present`, `seed_rows_are_posthoc_diagnostic`, `source_quality_promotable`, `source_rows_are_diagnostic_not_forward_registered`, `strike_missing_in_current_seed_boundary_distance_is_proxy`, `true_boundary_abs_d_lte_1_brier_not_degraded`.
- `v28s_boundary_monotonic_blend_v001` is not promotable: `high_recross_brier_not_degraded`, `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `near_boundary_brier_not_degraded`, `no_post_lock_forward_rows`, `post_freeze_forward_rows_present`, `seed_rows_are_posthoc_diagnostic`, `source_quality_promotable`, `source_rows_are_diagnostic_not_forward_registered`, `strike_missing_in_current_seed_boundary_distance_is_proxy`, `true_boundary_abs_d_lte_1_brier_not_degraded`.
- `v28s_boundary_monotonic_light_v001` is not promotable: `high_recross_brier_not_degraded`, `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `near_boundary_brier_not_degraded`, `no_post_lock_forward_rows`, `post_freeze_forward_rows_present`, `seed_rows_are_posthoc_diagnostic`, `source_quality_promotable`, `source_rows_are_diagnostic_not_forward_registered`, `strike_missing_in_current_seed_boundary_distance_is_proxy`, `true_boundary_abs_d_lte_1_brier_not_degraded`.
- `v28s_boundary_monotonic_time_safe_v001` is not promotable: `high_recross_brier_not_degraded`, `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `near_boundary_brier_not_degraded`, `no_post_lock_forward_rows`, `post_freeze_forward_rows_present`, `seed_rows_are_posthoc_diagnostic`, `source_quality_promotable`, `source_rows_are_diagnostic_not_forward_registered`, `strike_missing_in_current_seed_boundary_distance_is_proxy`, `true_boundary_abs_d_lte_1_brier_not_degraded`.
- `v28s_boundary_monotonic_micro_time_safe_v001` is not promotable: `high_recross_brier_not_degraded`, `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `near_boundary_brier_not_degraded`, `no_post_lock_forward_rows`, `post_freeze_forward_rows_present`, `seed_rows_are_posthoc_diagnostic`, `source_quality_promotable`, `source_rows_are_diagnostic_not_forward_registered`, `strike_missing_in_current_seed_boundary_distance_is_proxy`, `true_boundary_abs_d_lte_1_brier_not_degraded`.
- `v28s_late_dsigma_residual_tilt_v001` is not promotable: `holdout_logloss_better_than_v28`, `no_post_lock_forward_rows`, `post_freeze_forward_rows_present`, `seed_rows_are_posthoc_diagnostic`, `source_quality_promotable`, `source_rows_are_diagnostic_not_forward_registered`, `strike_missing_in_current_seed_boundary_distance_is_proxy`, `true_boundary_abs_d_lte_1_brier_not_degraded`.

## Candidate Manifests

| candidate | type | features | model hash | forward collection allowed | promotion registry allowed |
|---|---|---:|---|---:|---:|
| `v28_raw` | `baseline_v28_raw` | 0 | `92cd09ac8c08636c3053fd48` | False | False |
| `v28s_logistic_calibration_v001` | `regularized_logistic` | 1 | `7d371feef5f09d24d2b83d90` | True | False |
| `v28s_logistic_boundary_physics_v001` | `regularized_logistic` | 14 | `71c9c323a2b22c1cda078553` | True | False |
| `v28s_logistic_book_reliability_diag_v001` | `regularized_logistic` | 9 | `4fd4aac68789e9c885f46767` | True | False |
| `v28s_monotonic_tabular_v001` | `monotonic_tabular_calibration` | 1 | `be73833bdead411c157e790e` | True | False |
| `v28s_boundary_monotonic_blend_v001` | `monotonic_tabular_calibration` | 2 | `631a5c49f164f77440c3381c` | True | False |
| `v28s_boundary_monotonic_light_v001` | `monotonic_tabular_calibration` | 2 | `4b1b6170f9698bf3786aa5d7` | True | False |
| `v28s_boundary_monotonic_time_safe_v001` | `monotonic_tabular_calibration` | 3 | `8dfbc48a962472ac6230eede` | True | False |
| `v28s_boundary_monotonic_micro_time_safe_v001` | `monotonic_tabular_calibration` | 3 | `5229f8966bde26448e9c4403` | True | False |
| `v28s_late_dsigma_residual_tilt_v001` | `fixed_logit_residual` | 2 | `6c24b9d069769194cd6bf7fd` | True | False |

## Read

- Probability quality is scored before shadow economics.
- The holdout split is market-level chronological, so rows from the same market do not cross train/holdout.
- True near-boundary metrics use logged abs(d_sigma) when present; otherwise the report falls back to the v28 40-60 probability proxy.
- True near-boundary holdout rows: `0`.
- Non-baseline simple candidates may be frozen for future shadow collection, but no candidate can be promoted from this run because the available rows are diagnostic and there are no post-lock forward rows.

## Outputs

- Candidate predictions: `research_particle/v28_successor/candidate_predictions_latest.csv`
- Candidate manifests: `research_particle/v28_successor/candidate_manifests_latest.json`
- Metrics CSV: `logs/edge_research/v28_successor_calibration_metrics_latest.csv`
- Calibration bins CSV: `logs/edge_research/v28_successor_calibration_bins_latest.csv`
