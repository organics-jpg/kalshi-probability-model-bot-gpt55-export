# v38 Probability Stability

Generated UTC: `2026-05-04T23:16:16.347489+00:00`

## Scope

- Pure FV probability block audit, not trade scoring.
- Candidate: v38 long-memory anti-persistence versus v34 and v37.
- No live bot code/process or orders are touched.

## Split Metrics

| dataset | split | model | rows | Brier | logloss | side acc | mean p_yes | yes rate |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `all_heartbeats` | all | `v34_material_antipersist3` | 19021 | 0.145993 | 0.440330 | 77.64% | 50.67% | 49.58% |
| `all_heartbeats` | all | `v37_piecewise_dynamic_temp_antipersist3` | 19021 | 0.145949 | 0.440092 | 77.64% | 50.67% | 49.58% |
| `all_heartbeats` | all | `v38_long60_antipersist` | 19021 | 0.145917 | 0.440021 | 77.64% | 50.66% | 49.58% |
| `all_heartbeats` | train | `v34_material_antipersist3` | 11398 | 0.149555 | 0.453961 | 77.37% | 51.31% | 50.93% |
| `all_heartbeats` | train | `v37_piecewise_dynamic_temp_antipersist3` | 11398 | 0.149550 | 0.453833 | 77.37% | 51.32% | 50.93% |
| `all_heartbeats` | train | `v38_long60_antipersist` | 11398 | 0.149531 | 0.453791 | 77.37% | 51.31% | 50.93% |
| `all_heartbeats` | validation | `v34_material_antipersist3` | 3818 | 0.134346 | 0.401956 | 79.10% | 51.96% | 51.89% |
| `all_heartbeats` | validation | `v37_piecewise_dynamic_temp_antipersist3` | 3818 | 0.134257 | 0.401467 | 79.10% | 51.96% | 51.89% |
| `all_heartbeats` | validation | `v38_long60_antipersist` | 3818 | 0.134234 | 0.401405 | 79.10% | 51.96% | 51.89% |
| `all_heartbeats` | holdout | `v34_material_antipersist3` | 3805 | 0.147009 | 0.438003 | 76.98% | 47.44% | 43.23% |
| `all_heartbeats` | holdout | `v37_piecewise_dynamic_temp_antipersist3` | 3805 | 0.146894 | 0.437688 | 76.95% | 47.43% | 43.23% |
| `all_heartbeats` | holdout | `v38_long60_antipersist` | 3805 | 0.146815 | 0.437520 | 76.95% | 47.41% | 43.23% |
| `minute_bucket` | all | `v34_material_antipersist3` | 4898 | 0.148914 | 0.443946 | 76.77% | 50.65% | 49.63% |
| `minute_bucket` | all | `v37_piecewise_dynamic_temp_antipersist3` | 4898 | 0.148834 | 0.443541 | 76.77% | 50.65% | 49.63% |
| `minute_bucket` | all | `v38_long60_antipersist` | 4898 | 0.148799 | 0.443461 | 76.77% | 50.64% | 49.63% |
| `minute_bucket` | train | `v34_material_antipersist3` | 2938 | 0.152212 | 0.454560 | 76.48% | 51.25% | 50.99% |
| `minute_bucket` | train | `v37_piecewise_dynamic_temp_antipersist3` | 2938 | 0.152157 | 0.454253 | 76.51% | 51.25% | 50.99% |
| `minute_bucket` | train | `v38_long60_antipersist` | 2938 | 0.152138 | 0.454207 | 76.51% | 51.25% | 50.99% |
| `minute_bucket` | validation | `v34_material_antipersist3` | 982 | 0.137455 | 0.409868 | 78.21% | 51.89% | 51.83% |
| `minute_bucket` | validation | `v37_piecewise_dynamic_temp_antipersist3` | 982 | 0.137343 | 0.409225 | 78.21% | 51.89% | 51.83% |
| `minute_bucket` | validation | `v38_long60_antipersist` | 982 | 0.137317 | 0.409154 | 78.21% | 51.89% | 51.83% |
| `minute_bucket` | holdout | `v34_material_antipersist3` | 978 | 0.150513 | 0.446279 | 76.18% | 47.59% | 43.35% |
| `minute_bucket` | holdout | `v37_piecewise_dynamic_temp_antipersist3` | 978 | 0.150390 | 0.445819 | 76.07% | 47.58% | 43.35% |
| `minute_bucket` | holdout | `v38_long60_antipersist` | 978 | 0.150299 | 0.445625 | 76.07% | 47.56% | 43.35% |

## Chronological Blocks

| dataset | base | block kind | Brier improved | logloss improved | mean Brier delta | worst Brier delta | mean logloss delta | worst logloss delta |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `all_heartbeats` | `v34_material_antipersist3` | `block10` | 5/10 | 7/10 | -0.000076 | +0.000195 | -0.000309 | +0.000426 |
| `all_heartbeats` | `v34_material_antipersist3` | `block20` | 11/20 | 16/20 | -0.000074 | +0.000652 | -0.000305 | +0.001314 |
| `all_heartbeats` | `v37_piecewise_dynamic_temp_antipersist3` | `block10` | 7/10 | 7/10 | -0.000033 | +0.000324 | -0.000073 | +0.000706 |
| `all_heartbeats` | `v37_piecewise_dynamic_temp_antipersist3` | `block20` | 15/20 | 14/20 | -0.000031 | +0.000690 | -0.000070 | +0.001483 |
| `minute_bucket` | `v34_material_antipersist3` | `block10` | 6/10 | 8/10 | -0.000116 | +0.000261 | -0.000487 | +0.000285 |
| `minute_bucket` | `v34_material_antipersist3` | `block20` | 15/20 | 16/20 | -0.000115 | +0.000760 | -0.000484 | +0.001500 |
| `minute_bucket` | `v37_piecewise_dynamic_temp_antipersist3` | `block10` | 8/10 | 7/10 | -0.000036 | +0.000408 | -0.000083 | +0.000876 |
| `minute_bucket` | `v37_piecewise_dynamic_temp_antipersist3` | `block20` | 15/20 | 14/20 | -0.000035 | +0.000864 | -0.000080 | +0.001838 |

## Read

- v38 is acceptable as the next strict-forward FV probability shadow only if it improves v37 without adding block-level damage.
