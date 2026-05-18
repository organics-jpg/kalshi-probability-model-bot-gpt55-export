# v28 Successor Calibration Report

Research-only candidate training/scoring artifact. Live trading code, state, orders, thresholds, and processes were not touched.

## Summary

- Generated UTC: `2026-05-12T07:29:25Z`
- Feature table: `research_particle/v28_successor/features_logged_events_latest.csv`
- Feature table hash: `e4dea4b07de3169c96139cba6e704336537d63676d193a9e0efac6c3fa63f0d5`
- Feature manifest hash: `03d1ec494e707394a3d8c39e`
- Rows: `1745`
- Candidates: `10`
- Promotion verdict: `not_promotable`

## Splits

| split | rows | markets | start decision UTC | end decision UTC |
|---|---:|---:|---|---|
| `train` | 938 | 70 | `2026-05-05T20:07:17.198Z` | `2026-05-06T23:40:50.816Z` |
| `validation` | 395 | 24 | `2026-05-06T23:53:30.356Z` | `2026-05-07T09:56:23.295Z` |
| `chronological_holdout` | 412 | 24 | `2026-05-07T10:03:17.732Z` | `2026-05-07T17:11:41.297Z` |
| `post_freeze_forward` | 0 | 0 |  |  |

## Chronological Holdout

| candidate | track | Brier | logloss | ECE | side acc | proxy-boundary Brier | true-boundary Brier | high-recross Brier | shadow net c | gate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `v28_raw` | `baseline` | 0.099513 | 0.337648 | 0.042257 | 88.35% | NA | 0.131077 | NA | 2800.0 | `baseline_not_candidate` |
| `v28s_logistic_calibration_v001` | `pure_physics` | 0.158277 | 0.502165 | 0.230233 | 88.35% | NA | 0.184572 | NA | -264.0 | `fail` |
| `v28s_logistic_boundary_physics_v001` | `pure_physics` | 0.125383 | 0.410227 | 0.131032 | 82.52% | NA | 0.168494 | NA | 1820.0 | `fail` |
| `v28s_logistic_book_reliability_diag_v001` | `book_aware_diagnostic` | 0.141137 | 0.461074 | 0.176175 | 88.35% | NA | 0.150899 | NA | 223.0 | `fail` |
| `v28s_monotonic_tabular_v001` | `pure_physics` | 0.106165 | 0.370710 | 0.086345 | 88.35% | NA | 0.132433 | NA | 1568.0 | `fail` |
| `v28s_boundary_monotonic_blend_v001` | `pure_physics` | 0.102511 | 0.354912 | 0.072622 | 88.35% | NA | 0.132433 | NA | 2152.0 | `fail` |
| `v28s_boundary_monotonic_light_v001` | `pure_physics` | 0.099676 | 0.340365 | 0.052277 | 88.35% | NA | 0.130785 | NA | 2800.0 | `fail` |
| `v28s_boundary_monotonic_time_safe_v001` | `pure_physics` | 0.099413 | 0.337571 | 0.044625 | 88.35% | NA | 0.130950 | NA | 2800.0 | `fail` |
| `v28s_boundary_monotonic_micro_time_safe_v001` | `pure_physics` | 0.099478 | 0.337601 | 0.042967 | 88.35% | NA | 0.131034 | NA | 2800.0 | `fail` |
| `v28s_late_dsigma_residual_tilt_v001` | `pure_physics` | 0.099709 | 0.337699 | 0.043240 | 88.35% | NA | 0.131468 | NA | 2800.0 | `fail` |

## Gate Read

- `v28s_logistic_calibration_v001` is not promotable: `high_recross_brier_not_degraded`, `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `near_boundary_brier_not_degraded`, `no_post_lock_forward_rows`, `post_freeze_forward_rows_present`, `source_quality_promotable`, `source_rows_are_diagnostic_not_forward_registered`, `true_boundary_abs_d_lte_1_brier_not_degraded`.
- `v28s_logistic_boundary_physics_v001` is not promotable: `high_recross_brier_not_degraded`, `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `near_boundary_brier_not_degraded`, `no_post_lock_forward_rows`, `post_freeze_forward_rows_present`, `source_quality_promotable`, `source_rows_are_diagnostic_not_forward_registered`, `true_boundary_abs_d_lte_1_brier_not_degraded`.
- `v28s_logistic_book_reliability_diag_v001` is not promotable: `high_recross_brier_not_degraded`, `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `near_boundary_brier_not_degraded`, `no_post_lock_forward_rows`, `post_freeze_forward_rows_present`, `source_quality_promotable`, `source_rows_are_diagnostic_not_forward_registered`, `true_boundary_abs_d_lte_1_brier_not_degraded`.
- `v28s_monotonic_tabular_v001` is not promotable: `high_recross_brier_not_degraded`, `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `near_boundary_brier_not_degraded`, `no_post_lock_forward_rows`, `post_freeze_forward_rows_present`, `source_quality_promotable`, `source_rows_are_diagnostic_not_forward_registered`, `true_boundary_abs_d_lte_1_brier_not_degraded`.
- `v28s_boundary_monotonic_blend_v001` is not promotable: `high_recross_brier_not_degraded`, `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `near_boundary_brier_not_degraded`, `no_post_lock_forward_rows`, `post_freeze_forward_rows_present`, `source_quality_promotable`, `source_rows_are_diagnostic_not_forward_registered`, `true_boundary_abs_d_lte_1_brier_not_degraded`.
- `v28s_boundary_monotonic_light_v001` is not promotable: `high_recross_brier_not_degraded`, `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `no_post_lock_forward_rows`, `post_freeze_forward_rows_present`, `source_quality_promotable`, `source_rows_are_diagnostic_not_forward_registered`.
- `v28s_boundary_monotonic_time_safe_v001` is not promotable: `high_recross_brier_not_degraded`, `no_post_lock_forward_rows`, `post_freeze_forward_rows_present`, `source_quality_promotable`, `source_rows_are_diagnostic_not_forward_registered`.
- `v28s_boundary_monotonic_micro_time_safe_v001` is not promotable: `high_recross_brier_not_degraded`, `no_post_lock_forward_rows`, `post_freeze_forward_rows_present`, `source_quality_promotable`, `source_rows_are_diagnostic_not_forward_registered`.
- `v28s_late_dsigma_residual_tilt_v001` is not promotable: `high_recross_brier_not_degraded`, `holdout_brier_better_than_v28`, `holdout_logloss_better_than_v28`, `near_boundary_brier_not_degraded`, `no_post_lock_forward_rows`, `post_freeze_forward_rows_present`, `source_quality_promotable`, `source_rows_are_diagnostic_not_forward_registered`, `true_boundary_abs_d_lte_1_brier_not_degraded`.

## Candidate Manifests

| candidate | type | features | model hash | forward collection allowed | promotion registry allowed |
|---|---|---:|---|---:|---:|
| `v28_raw` | `baseline_v28_raw` | 0 | `92cd09ac8c08636c3053fd48` | False | False |
| `v28s_logistic_calibration_v001` | `regularized_logistic` | 1 | `065072105a4f4792a473a741` | True | False |
| `v28s_logistic_boundary_physics_v001` | `regularized_logistic` | 33 | `a938bf30c29577fc972b5a7d` | True | False |
| `v28s_logistic_book_reliability_diag_v001` | `regularized_logistic` | 23 | `1612cf1a1fd3d451ff05ccad` | True | False |
| `v28s_monotonic_tabular_v001` | `monotonic_tabular_calibration` | 1 | `f01a85e32739def20cd8c3b0` | True | False |
| `v28s_boundary_monotonic_blend_v001` | `monotonic_tabular_calibration` | 3 | `db7461bb1e38cb2256cf3530` | True | False |
| `v28s_boundary_monotonic_light_v001` | `monotonic_tabular_calibration` | 3 | `c1edea2fdb0e0eb8b405faf0` | True | False |
| `v28s_boundary_monotonic_time_safe_v001` | `monotonic_tabular_calibration` | 4 | `9b461a310d06c06b55af2e2d` | True | False |
| `v28s_boundary_monotonic_micro_time_safe_v001` | `monotonic_tabular_calibration` | 4 | `9c831d7954e3c65fec6c0794` | True | False |
| `v28s_late_dsigma_residual_tilt_v001` | `fixed_logit_residual` | 3 | `b160fbf8edd98b998b089805` | True | False |

## Read

- Probability quality is scored before shadow economics.
- The holdout split is market-level chronological, so rows from the same market do not cross train/holdout.
- True near-boundary metrics use logged abs(d_sigma) when present; otherwise the report falls back to the v28 40-60 probability proxy.
- True near-boundary holdout rows: `208`.
- Non-baseline simple candidates may be frozen for future shadow collection, but no candidate can be promoted from this run because the available rows are diagnostic and there are no post-lock forward rows.

## Outputs

- Candidate predictions: `research_particle/v28_successor/candidate_predictions_logged_events_latest.csv`
- Candidate manifests: `research_particle/v28_successor/candidate_manifests_logged_events_latest.json`
- Metrics CSV: `logs/edge_research/v28_successor_logged_event_calibration_metrics_latest.csv`
- Calibration bins CSV: `logs/edge_research/v28_successor_logged_event_calibration_bins_latest.csv`
