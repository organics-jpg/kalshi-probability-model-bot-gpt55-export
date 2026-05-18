# v35 FV Probability Stability

Generated UTC: `2026-05-04T20:53:02.326406+00:00`

## Scope

- Research-only stability audit for pure FV probability, not scoring.
- Candidate: v35 longer proxy horizon plus softer temperature versus v34.
- No live bot code/process or orders are touched.

## Split Metrics

| dataset | split | model | rows | Brier | logloss | side acc | mean p_yes | yes rate |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `all_heartbeats` | all | `v28_live_surface` | 19021 | 0.147196 | 0.441154 | 77.66% | 50.78% | 49.58% |
| `all_heartbeats` | all | `v32_avg110_final60_exact` | 19021 | 0.146350 | 0.441336 | 77.61% | 50.70% | 49.58% |
| `all_heartbeats` | all | `v34_material_antipersist3` | 19021 | 0.145993 | 0.440330 | 77.64% | 50.67% | 49.58% |
| `all_heartbeats` | all | `v35_h150_t102_antipersist3` | 19021 | 0.146034 | 0.441083 | 77.64% | 50.67% | 49.58% |
| `all_heartbeats` | train | `v28_live_surface` | 11398 | 0.150212 | 0.450534 | 77.43% | 51.33% | 50.93% |
| `all_heartbeats` | train | `v32_avg110_final60_exact` | 11398 | 0.149547 | 0.453800 | 77.39% | 51.33% | 50.93% |
| `all_heartbeats` | train | `v34_material_antipersist3` | 11398 | 0.149555 | 0.453961 | 77.37% | 51.31% | 50.93% |
| `all_heartbeats` | train | `v35_h150_t102_antipersist3` | 11398 | 0.149696 | 0.455369 | 77.37% | 51.32% | 50.93% |
| `all_heartbeats` | validation | `v28_live_surface` | 3818 | 0.136672 | 0.410485 | 78.58% | 52.11% | 51.89% |
| `all_heartbeats` | validation | `v32_avg110_final60_exact` | 3818 | 0.136017 | 0.406971 | 78.58% | 52.01% | 51.89% |
| `all_heartbeats` | validation | `v34_material_antipersist3` | 3818 | 0.134346 | 0.401956 | 79.10% | 51.96% | 51.89% |
| `all_heartbeats` | validation | `v35_h150_t102_antipersist3` | 3818 | 0.134198 | 0.401509 | 79.10% | 51.96% | 51.89% |
| `all_heartbeats` | holdout | `v28_live_surface` | 3805 | 0.148720 | 0.443827 | 77.42% | 47.80% | 43.23% |
| `all_heartbeats` | holdout | `v32_avg110_final60_exact` | 3805 | 0.147142 | 0.438480 | 77.32% | 47.51% | 43.23% |
| `all_heartbeats` | holdout | `v34_material_antipersist3` | 3805 | 0.147009 | 0.438003 | 76.98% | 47.44% | 43.23% |
| `all_heartbeats` | holdout | `v35_h150_t102_antipersist3` | 3805 | 0.146942 | 0.438000 | 76.95% | 47.43% | 43.23% |
| `minute_bucket` | all | `v28_live_surface` | 4898 | 0.150816 | 0.451037 | 76.77% | 50.75% | 49.63% |
| `minute_bucket` | all | `v32_avg110_final60_exact` | 4898 | 0.149348 | 0.445275 | 76.75% | 50.68% | 49.63% |
| `minute_bucket` | all | `v34_material_antipersist3` | 4898 | 0.148914 | 0.443946 | 76.77% | 50.65% | 49.63% |
| `minute_bucket` | all | `v35_h150_t102_antipersist3` | 4898 | 0.149025 | 0.444524 | 76.77% | 50.65% | 49.63% |
| `minute_bucket` | train | `v28_live_surface` | 2938 | 0.153673 | 0.459979 | 76.51% | 51.25% | 50.99% |
| `minute_bucket` | train | `v32_avg110_final60_exact` | 2938 | 0.152197 | 0.454575 | 76.51% | 51.26% | 50.99% |
| `minute_bucket` | train | `v34_material_antipersist3` | 2938 | 0.152212 | 0.454560 | 76.48% | 51.25% | 50.99% |
| `minute_bucket` | train | `v35_h150_t102_antipersist3` | 2938 | 0.152545 | 0.455799 | 76.51% | 51.26% | 50.99% |
| `minute_bucket` | validation | `v28_live_surface` | 982 | 0.140475 | 0.421010 | 77.60% | 52.01% | 51.83% |
| `minute_bucket` | validation | `v32_avg110_final60_exact` | 982 | 0.139558 | 0.415930 | 77.60% | 51.93% | 51.83% |
| `minute_bucket` | validation | `v34_material_antipersist3` | 982 | 0.137455 | 0.409868 | 78.21% | 51.89% | 51.83% |
| `minute_bucket` | validation | `v35_h150_t102_antipersist3` | 982 | 0.137187 | 0.409154 | 78.21% | 51.89% | 51.83% |
| `minute_bucket` | holdout | `v28_live_surface` | 978 | 0.152618 | 0.454326 | 76.69% | 47.98% | 43.35% |
| `minute_bucket` | holdout | `v32_avg110_final60_exact` | 978 | 0.150618 | 0.446803 | 76.58% | 47.69% | 43.35% |
| `minute_bucket` | holdout | `v34_material_antipersist3` | 978 | 0.150513 | 0.446279 | 76.18% | 47.59% | 43.35% |
| `minute_bucket` | holdout | `v35_h150_t102_antipersist3` | 978 | 0.150338 | 0.446168 | 76.07% | 47.58% | 43.35% |

## Chronological Blocks

| dataset | block kind | Brier improved | logloss improved | mean Brier delta | worst Brier delta | mean logloss delta | worst logloss delta |
|---|---|---:|---:|---:|---:|---:|---:|
| `all_heartbeats` | `block10` | 3/10 | 4/10 | +0.000043 | +0.000274 | +0.000754 | +0.005288 |
| `all_heartbeats` | `block20` | 6/20 | 7/20 | +0.000042 | +0.000352 | +0.000772 | +0.010637 |
| `minute_bucket` | `block10` | 3/10 | 5/10 | +0.000111 | +0.000565 | +0.000571 | +0.005049 |
| `minute_bucket` | `block20` | 9/20 | 10/20 | +0.000111 | +0.000996 | +0.000581 | +0.011123 |

## Worst v35 Buckets

Rows floor: 100. Positive delta means v35 is worse than v34.

| dataset | split | feature | bucket | rows | Brier delta | logloss delta | mean p_yes | yes rate |
|---|---|---|---|---:|---:|---:|---:|---:|
| `minute_bucket` | train | `seconds_to_close` | `(90.0, 120.0]` | 196 | +0.004846 | +0.011793 | 52.50% | 51.02% |
| `minute_bucket` | train | `v35_h150_t102_antipersist3_anti_persistence_materiality_gate` | `(-0.000665, 0.000342]` | 392 | +0.002966 | +0.013518 | 50.66% | 50.77% |
| `minute_bucket` | train | `v35_h150_t102_antipersist3_anti_persistence_logit_weight` | `(-0.0009665, 3.42e-05]` | 392 | +0.002966 | +0.013518 | 50.66% | 50.77% |
| `minute_bucket` | all | `seconds_to_close` | `(90.0, 120.0]` | 328 | +0.002924 | +0.010835 | 51.41% | 49.70% |
| `minute_bucket` | train | `seconds_to_close` | `(-0.001, 60.0]` | 198 | +0.002233 | +0.014705 | 52.23% | 50.51% |
| `minute_bucket` | train | `abs_v35_d_sigma` | `(0.5, 0.75]` | 316 | +0.002037 | +0.006798 | 48.91% | 50.00% |
| `minute_bucket` | all | `v35_h150_t102_antipersist3_anti_persistence_materiality_gate` | `(-0.000665, 0.000342]` | 613 | +0.001746 | +0.008560 | 49.61% | 48.94% |
| `minute_bucket` | all | `v35_h150_t102_antipersist3_anti_persistence_logit_weight` | `(-0.0009665, 3.42e-05]` | 613 | +0.001746 | +0.008560 | 49.61% | 48.94% |
| `all_heartbeats` | holdout | `v35_h150_t102_antipersist3_anti_persistence_materiality_gate` | `(0.000339, 0.00037]` | 390 | +0.001519 | +0.006575 | 43.62% | 38.72% |
| `all_heartbeats` | holdout | `v35_h150_t102_antipersist3_anti_persistence_logit_weight` | `(3.39e-05, 3.7e-05]` | 390 | +0.001519 | +0.006575 | 43.62% | 38.72% |
| `all_heartbeats` | train | `seconds_to_close` | `(120.0, 180.0]` | 783 | +0.001488 | +0.004110 | 50.81% | 50.96% |
| `minute_bucket` | train | `abs_v32_d_sigma` | `(0.75, 1.0]` | 230 | +0.001459 | +0.005287 | 49.08% | 48.26% |
| `minute_bucket` | train | `v35_h150_t102_antipersist3_anti_persistence_shift_dollars` | `(-0.748, -0.00101]` | 380 | +0.001338 | +0.006887 | 59.72% | 58.16% |
| `minute_bucket` | train | `v35_h150_t102_antipersist3_anti_persistence_shift_dollars` | `(-0.00101, 0.677]` | 384 | +0.001284 | +0.003847 | 43.70% | 41.41% |
| `all_heartbeats` | train | `seconds_to_close` | `(90.0, 120.0]` | 391 | +0.001181 | +0.001451 | 52.63% | 51.15% |
| `all_heartbeats` | train | `seconds_to_close` | `(-0.001, 60.0]` | 790 | +0.001162 | +0.020152 | 52.20% | 50.63% |

## Best v35 Buckets

| dataset | split | feature | bucket | rows | Brier delta | logloss delta | mean p_yes | yes rate |
|---|---|---|---|---:|---:|---:|---:|---:|
| `minute_bucket` | holdout | `signed_velocity_dps_3m` | `(-0.256, -0.12]` | 116 | -0.002263 | -0.005758 | 36.87% | 31.90% |
| `minute_bucket` | validation | `v35_h150_t102_antipersist3_anti_persistence_materiality_gate` | `(-0.000665, 0.000342]` | 130 | -0.001575 | -0.002697 | 49.48% | 49.23% |
| `minute_bucket` | validation | `v35_h150_t102_antipersist3_anti_persistence_logit_weight` | `(-0.0009665, 3.42e-05]` | 130 | -0.001575 | -0.002697 | 49.48% | 49.23% |
| `all_heartbeats` | holdout | `abs_v35_d_sigma` | `(0.75, 1.0]` | 317 | -0.001560 | -0.006051 | 44.94% | 40.69% |
| `all_heartbeats` | train | `seconds_to_close` | `(60.0, 90.0]` | 394 | -0.001486 | -0.004008 | 52.22% | 50.51% |
| `minute_bucket` | validation | `abs_v32_d_sigma` | `(0.5, 0.75]` | 105 | -0.001472 | -0.004219 | 45.85% | 45.71% |
| `minute_bucket` | holdout | `abs_v32_d_sigma` | `(0.25, 0.5]` | 163 | -0.001376 | -0.003038 | 48.40% | 39.26% |
| `minute_bucket` | holdout | `abs_v32_d_sigma` | `(0.5, 0.75]` | 101 | -0.001319 | -0.004204 | 47.49% | 46.53% |
| `minute_bucket` | train | `seconds_to_close` | `(120.0, 180.0]` | 196 | -0.001302 | -0.003404 | 50.84% | 51.02% |
| `all_heartbeats` | holdout | `v35_h150_t102_antipersist3_anti_persistence_shift_dollars` | `(0.431, 4.79]` | 350 | -0.001216 | -0.003432 | 31.29% | 31.43% |
| `minute_bucket` | holdout | `abs_v35_d_sigma` | `(0.25, 0.5]` | 158 | -0.001215 | -0.002687 | 48.21% | 37.34% |
| `all_heartbeats` | holdout | `v35_h150_t102_antipersist3_anti_persistence_materiality_gate` | `(0.00037, 0.000494]` | 359 | -0.001199 | -0.002869 | 45.94% | 46.52% |
| `all_heartbeats` | holdout | `v35_h150_t102_antipersist3_anti_persistence_logit_weight` | `(3.7e-05, 4.94e-05]` | 359 | -0.001199 | -0.002869 | 45.94% | 46.52% |
| `minute_bucket` | validation | `abs_v35_d_sigma` | `(0.25, 0.5]` | 149 | -0.001088 | -0.002413 | 48.86% | 55.70% |
| `minute_bucket` | validation | `signed_velocity_dps_3m` | `(-0.0533, 8.33e-05]` | 138 | -0.001072 | -0.002870 | 44.27% | 39.86% |
| `minute_bucket` | validation | `v35_h150_t102_antipersist3_anti_persistence_shift_dollars` | `(-0.00101, 0.677]` | 136 | -0.001061 | -0.001892 | 39.84% | 38.97% |

## Read

- v35 is promotion-ready only if the recent validation/holdout gain survives block and bucket checks.
- Train degradation is a regime warning; strict-forward rows remain mandatory before live use.
