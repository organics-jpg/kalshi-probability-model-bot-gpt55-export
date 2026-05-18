# v28 Successor Sidecar Batch Evidence Score

Research-only scorer for settled sidecar batch evidence. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Evidence status: `scored_sidecar_batch_evidence`
- Evidence family: `sidecar_batch`
- Canonical promotion ledger: `False`
- Clean rows: `16860`
- Clean markets: `195`
- Candidates: `9`
- Promotable by sidecar evidence alone: `1`
- Promotion allowed: `False`

## Candidate Gates

| candidate | status | fail reasons |
|---|---|---|
| `v28s_boundary_monotonic_blend_v001` | `fail` | `['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded']` |
| `v28s_boundary_monotonic_light_v001` | `fail` | `['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded']` |
| `v28s_boundary_monotonic_micro_time_safe_v001` | `fail` | `['forward_brier_not_better_than_v28', 'near_boundary_brier_degraded']` |
| `v28s_boundary_monotonic_time_safe_v001` | `fail` | `['forward_brier_not_better_than_v28', 'near_boundary_brier_degraded']` |
| `v28s_late_dsigma_residual_tilt_v001` | `pass` | `[]` |
| `v28s_logistic_book_reliability_diag_v001` | `fail` | `['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded']` |
| `v28s_logistic_boundary_physics_v001` | `fail` | `['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded']` |
| `v28s_logistic_calibration_v001` | `fail` | `['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded']` |
| `v28s_monotonic_tabular_v001` | `fail` | `['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded']` |

## All-Rows Metrics

| candidate | rows | markets | cand brier | v28 brier | cand logloss | v28 logloss |
|---|---:|---:|---:|---:|---:|---:|
| `v28s_boundary_monotonic_blend_v001` | 1760 | 154 | 0.1321759146359767 | 0.12977074979326159 | 0.40808588593984546 | 0.40136129117148994 |
| `v28s_boundary_monotonic_light_v001` | 1754 | 152 | 0.13042472169015282 | 0.12983777073802324 | 0.402964036320415 | 0.4013560536591946 |
| `v28s_boundary_monotonic_micro_time_safe_v001` | 1620 | 117 | 0.12538712637510288 | 0.12536515381938892 | 0.39110122139483255 | 0.39112811704141115 |
| `v28s_boundary_monotonic_time_safe_v001` | 1752 | 151 | 0.1298566763239932 | 0.12978757052266648 | 0.40115376553867277 | 0.40119845542318927 |
| `v28s_late_dsigma_residual_tilt_v001` | 1558 | 111 | 0.12316849545223837 | 0.12413020974731291 | 0.3832706236570643 | 0.38707369130158936 |
| `v28s_logistic_book_reliability_diag_v001` | 2104 | 195 | 0.3719319953153969 | 0.13346673942163315 | 1.189291481840989 | 0.40742561881652267 |
| `v28s_logistic_boundary_physics_v001` | 2104 | 195 | 0.4758989785447385 | 0.13346673942163315 | 2.3142608193576826 | 0.40742561881652267 |
| `v28s_logistic_calibration_v001` | 2104 | 195 | 0.1699900542900075 | 0.13346673942163315 | 0.5128939712888949 | 0.40742561881652267 |
| `v28s_monotonic_tabular_v001` | 2104 | 195 | 0.1391230223920663 | 0.13346673942163315 | 0.4351752496476201 | 0.40742561881652267 |

## Read

- These rows are scored with the same probability-first metrics as canonical forward evidence.
- This artifact is useful evidence plumbing, not promotion approval.
- Promotion remains blocked until canonical/source-contract coverage and verifier gates pass.
