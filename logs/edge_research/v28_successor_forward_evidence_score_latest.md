# v28 Successor Forward Evidence Score

Research-only scorer for settled frozen-forward evidence. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-18T20:51:46Z`
- Evidence status: `scored_forward_evidence`
- Raw joined-label rows: `16860`
- Clean forward rows: `16860`
- Clean forward markets: `195`
- Candidates: `9`
- Promotable by forward evidence alone: `1`
- Promotion allowed: `False`

## Candidate Gates

| candidate | status | rows | markets | est. addl markets | brier delta | logloss delta | fail reasons |
|---|---|---:|---:|---:|---:|---:|---|
| `v28s_boundary_monotonic_blend_v001` | `fail` | 1760/200 | 154/40 | 0 | 0.0024051648427151073 | 0.0067245947683555185 | `['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded']` |
| `v28s_boundary_monotonic_light_v001` | `fail` | 1754/200 | 152/40 | 0 | 0.0005869509521295724 | 0.0016079826612204196 | `['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded']` |
| `v28s_boundary_monotonic_micro_time_safe_v001` | `fail` | 1620/200 | 117/40 | 0 | 2.1972555713956066e-05 | -2.6895646578595223e-05 | `['forward_brier_not_better_than_v28', 'near_boundary_brier_degraded']` |
| `v28s_boundary_monotonic_time_safe_v001` | `fail` | 1752/200 | 151/40 | 0 | 6.910580132671318e-05 | -4.468988451650224e-05 | `['forward_brier_not_better_than_v28', 'near_boundary_brier_degraded']` |
| `v28s_late_dsigma_residual_tilt_v001` | `pass` | 1558/200 | 111/40 | 0 | -0.0009617142950745367 | -0.0038030676445250378 | `[]` |
| `v28s_logistic_book_reliability_diag_v001` | `fail` | 2104/200 | 195/40 | 0 | 0.23846525589376374 | 0.7818658630244664 | `['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded']` |
| `v28s_logistic_boundary_physics_v001` | `fail` | 2104/200 | 195/40 | 0 | 0.3424322391231054 | 1.90683520054116 | `['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded']` |
| `v28s_logistic_calibration_v001` | `fail` | 2104/200 | 195/40 | 0 | 0.036523314868374346 | 0.10546835247237224 | `['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded']` |
| `v28s_monotonic_tabular_v001` | `fail` | 2104/200 | 195/40 | 0 | 0.005656282970433163 | 0.027749630831097438 | `['forward_brier_not_better_than_v28', 'forward_logloss_not_better_than_v28', 'near_boundary_brier_degraded']` |

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

- This scorer only accepts rows joined after frozen prediction and resolution.
- Probability metrics are scored before any economics fields.
- Empty output is expected until real frozen forward rows settle.
