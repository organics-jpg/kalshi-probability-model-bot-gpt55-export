# v36 Block Stability

Generated UTC: `2026-05-04T21:18:21.262481+00:00`

## Scope

- Pure FV probability block audit, not trade scoring.
- Candidate: v36 piecewise proxy horizon versus v34 and v35.
- No live bot code/process or orders are touched.

## Split Metrics

| dataset | split | model | rows | Brier | logloss | side acc | mean p_yes | yes rate |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `all_heartbeats` | all | `v34_material_antipersist3` | 19021 | 0.145993 | 0.440330 | 77.64% | 50.67% | 49.58% |
| `all_heartbeats` | all | `v35_h150_t102_antipersist3` | 19021 | 0.146034 | 0.441083 | 77.64% | 50.67% | 49.58% |
| `all_heartbeats` | all | `v36_piecewise_h150_t102_antipersist3` | 19021 | 0.145995 | 0.440074 | 77.64% | 50.67% | 49.58% |
| `all_heartbeats` | train | `v34_material_antipersist3` | 11398 | 0.149555 | 0.453961 | 77.37% | 51.31% | 50.93% |
| `all_heartbeats` | train | `v35_h150_t102_antipersist3` | 11398 | 0.149696 | 0.455369 | 77.37% | 51.32% | 50.93% |
| `all_heartbeats` | train | `v36_piecewise_h150_t102_antipersist3` | 11398 | 0.149612 | 0.453696 | 77.37% | 51.32% | 50.93% |
| `all_heartbeats` | validation | `v34_material_antipersist3` | 3818 | 0.134346 | 0.401956 | 79.10% | 51.96% | 51.89% |
| `all_heartbeats` | validation | `v35_h150_t102_antipersist3` | 3818 | 0.134198 | 0.401509 | 79.10% | 51.96% | 51.89% |
| `all_heartbeats` | validation | `v36_piecewise_h150_t102_antipersist3` | 3818 | 0.134282 | 0.401691 | 79.10% | 51.97% | 51.89% |
| `all_heartbeats` | holdout | `v34_material_antipersist3` | 3805 | 0.147009 | 0.438003 | 76.98% | 47.44% | 43.23% |
| `all_heartbeats` | holdout | `v35_h150_t102_antipersist3` | 3805 | 0.146942 | 0.438000 | 76.95% | 47.43% | 43.23% |
| `all_heartbeats` | holdout | `v36_piecewise_h150_t102_antipersist3` | 3805 | 0.146913 | 0.437782 | 76.95% | 47.44% | 43.23% |
| `minute_bucket` | all | `v34_material_antipersist3` | 4898 | 0.148914 | 0.443946 | 76.77% | 50.65% | 49.63% |
| `minute_bucket` | all | `v35_h150_t102_antipersist3` | 4898 | 0.149025 | 0.444524 | 76.77% | 50.65% | 49.63% |
| `minute_bucket` | all | `v36_piecewise_h150_t102_antipersist3` | 4898 | 0.148880 | 0.443714 | 76.77% | 50.65% | 49.63% |
| `minute_bucket` | train | `v34_material_antipersist3` | 2938 | 0.152212 | 0.454560 | 76.48% | 51.25% | 50.99% |
| `minute_bucket` | train | `v35_h150_t102_antipersist3` | 2938 | 0.152545 | 0.455799 | 76.51% | 51.26% | 50.99% |
| `minute_bucket` | train | `v36_piecewise_h150_t102_antipersist3` | 2938 | 0.152214 | 0.454391 | 76.51% | 51.26% | 50.99% |
| `minute_bucket` | validation | `v34_material_antipersist3` | 982 | 0.137455 | 0.409868 | 78.21% | 51.89% | 51.83% |
| `minute_bucket` | validation | `v35_h150_t102_antipersist3` | 982 | 0.137187 | 0.409154 | 78.21% | 51.89% | 51.83% |
| `minute_bucket` | validation | `v36_piecewise_h150_t102_antipersist3` | 982 | 0.137368 | 0.409462 | 78.21% | 51.90% | 51.83% |
| `minute_bucket` | holdout | `v34_material_antipersist3` | 978 | 0.150513 | 0.446279 | 76.18% | 47.59% | 43.35% |
| `minute_bucket` | holdout | `v35_h150_t102_antipersist3` | 978 | 0.150338 | 0.446168 | 76.07% | 47.58% | 43.35% |
| `minute_bucket` | holdout | `v36_piecewise_h150_t102_antipersist3` | 978 | 0.150424 | 0.446031 | 76.07% | 47.59% | 43.35% |

## Chronological Blocks

| dataset | base | block kind | Brier improved | logloss improved | mean Brier delta | worst Brier delta | mean logloss delta | worst logloss delta |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `all_heartbeats` | `v34_material_antipersist3` | `block10` | 5/10 | 6/10 | +0.000002 | +0.000133 | -0.000257 | +0.000590 |
| `all_heartbeats` | `v34_material_antipersist3` | `block20` | 7/20 | 13/20 | +0.000001 | +0.000167 | -0.000260 | +0.000596 |
| `all_heartbeats` | `v35_h150_t102_antipersist3` | `block10` | 5/10 | 6/10 | -0.000041 | +0.000111 | -0.001011 | +0.000344 |
| `all_heartbeats` | `v35_h150_t102_antipersist3` | `block20` | 10/20 | 12/20 | -0.000040 | +0.000223 | -0.001032 | +0.000983 |
| `minute_bucket` | `v34_material_antipersist3` | `block10` | 6/10 | 9/10 | -0.000034 | +0.000116 | -0.000233 | +0.000414 |
| `minute_bucket` | `v34_material_antipersist3` | `block20` | 10/20 | 15/20 | -0.000035 | +0.000181 | -0.000237 | +0.000525 |
| `minute_bucket` | `v35_h150_t102_antipersist3` | `block10` | 7/10 | 5/10 | -0.000145 | +0.000346 | -0.000804 | +0.000966 |
| `minute_bucket` | `v35_h150_t102_antipersist3` | `block20` | 12/20 | 11/20 | -0.000146 | +0.000506 | -0.000818 | +0.001651 |

## Read

- v36 should replace v35 as the forward candidate if it keeps the recent split gains while reducing train/block damage.
