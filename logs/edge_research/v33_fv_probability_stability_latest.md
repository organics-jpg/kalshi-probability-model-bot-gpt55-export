# v33 FV Probability Stability

Generated UTC: `2026-05-04T20:14:25.604217+00:00`

## Scope

- Research-only stability audit for pure FV probability, not scoring.
- Candidate: v33 anti-persistence FV surface versus v32 settlement/proxy FV surface.
- No live bot code/process or orders are touched.

## Split Metrics

| dataset | split | model | rows | Brier | logloss | side acc | mean p_yes | yes rate |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `all_heartbeats` | all | `v28_live_surface` | 19021 | 0.147196 | 0.441154 | 77.66% | 50.78% | 49.58% |
| `all_heartbeats` | all | `v32_avg110_final60_exact` | 19021 | 0.146350 | 0.441336 | 77.61% | 50.70% | 49.58% |
| `all_heartbeats` | all | `v33_antipersist3` | 19021 | 0.146197 | 0.441081 | 77.52% | 50.69% | 49.58% |
| `all_heartbeats` | train | `v28_live_surface` | 11398 | 0.150212 | 0.450534 | 77.43% | 51.33% | 50.93% |
| `all_heartbeats` | train | `v32_avg110_final60_exact` | 11398 | 0.149547 | 0.453800 | 77.39% | 51.33% | 50.93% |
| `all_heartbeats` | train | `v33_antipersist3` | 11398 | 0.149543 | 0.454100 | 77.42% | 51.33% | 50.93% |
| `all_heartbeats` | validation | `v28_live_surface` | 3818 | 0.136672 | 0.410485 | 78.58% | 52.11% | 51.89% |
| `all_heartbeats` | validation | `v32_avg110_final60_exact` | 3818 | 0.136017 | 0.406971 | 78.58% | 52.01% | 51.89% |
| `all_heartbeats` | validation | `v33_antipersist3` | 3818 | 0.135380 | 0.404928 | 78.71% | 51.99% | 51.89% |
| `all_heartbeats` | holdout | `v28_live_surface` | 3805 | 0.148720 | 0.443827 | 77.42% | 47.80% | 43.23% |
| `all_heartbeats` | holdout | `v32_avg110_final60_exact` | 3805 | 0.147142 | 0.438480 | 77.32% | 47.51% | 43.23% |
| `all_heartbeats` | holdout | `v33_antipersist3` | 3805 | 0.147029 | 0.438362 | 76.66% | 47.47% | 43.23% |
| `minute_bucket` | all | `v28_live_surface` | 4898 | 0.150816 | 0.451037 | 76.77% | 50.75% | 49.63% |
| `minute_bucket` | all | `v32_avg110_final60_exact` | 4898 | 0.149348 | 0.445275 | 76.75% | 50.68% | 49.63% |
| `minute_bucket` | all | `v33_antipersist3` | 4898 | 0.149147 | 0.444702 | 76.70% | 50.67% | 49.63% |
| `minute_bucket` | train | `v28_live_surface` | 2938 | 0.153673 | 0.459979 | 76.51% | 51.25% | 50.99% |
| `minute_bucket` | train | `v32_avg110_final60_exact` | 2938 | 0.152197 | 0.454575 | 76.51% | 51.26% | 50.99% |
| `minute_bucket` | train | `v33_antipersist3` | 2938 | 0.152194 | 0.454572 | 76.58% | 51.27% | 50.99% |
| `minute_bucket` | validation | `v28_live_surface` | 982 | 0.140475 | 0.421010 | 77.60% | 52.01% | 51.83% |
| `minute_bucket` | validation | `v32_avg110_final60_exact` | 982 | 0.139558 | 0.415930 | 77.60% | 51.93% | 51.83% |
| `minute_bucket` | validation | `v33_antipersist3` | 982 | 0.138692 | 0.413334 | 77.80% | 51.92% | 51.83% |
| `minute_bucket` | holdout | `v28_live_surface` | 978 | 0.152618 | 0.454326 | 76.69% | 47.98% | 43.35% |
| `minute_bucket` | holdout | `v32_avg110_final60_exact` | 978 | 0.150618 | 0.446803 | 76.58% | 47.69% | 43.35% |
| `minute_bucket` | holdout | `v33_antipersist3` | 978 | 0.150490 | 0.446548 | 75.97% | 47.64% | 43.35% |

## Chronological Blocks

| dataset | block kind | Brier improved | logloss improved | mean Brier delta | worst Brier delta | mean logloss delta | worst logloss delta |
|---|---|---:|---:|---:|---:|---:|---:|
| `all_heartbeats` | `block10` | 6/10 | 5/10 | -0.000153 | +0.000227 | -0.000252 | +0.000897 |
| `all_heartbeats` | `block20` | 13/20 | 11/20 | -0.000156 | +0.000781 | -0.000257 | +0.002448 |
| `minute_bucket` | `block10` | 6/10 | 6/10 | -0.000202 | +0.000324 | -0.000572 | +0.000668 |
| `minute_bucket` | `block20` | 13/20 | 14/20 | -0.000205 | +0.000860 | -0.000581 | +0.002364 |

## Worst V33 Buckets

Rows floor: 100. Positive delta means v33 is worse than v32.

| dataset | split | feature | bucket | rows | Brier delta | logloss delta | mean p_yes | yes rate |
|---|---|---|---|---:|---:|---:|---:|---:|
| `minute_bucket` | holdout | `abs_v32_d_sigma` | `(0.5, 0.75]` | 101 | +0.001686 | +0.003812 | 47.95% | 46.53% |
| `all_heartbeats` | holdout | `abs_v32_d_sigma` | `(0.5, 0.75]` | 397 | +0.000938 | +0.002098 | 47.36% | 45.59% |
| `minute_bucket` | validation | `v33_antipersist3_anti_persistence_shift_dollars` | `(-26.812, -6.676]` | 129 | +0.000878 | +0.002095 | 65.90% | 72.09% |
| `all_heartbeats` | validation | `v33_antipersist3_anti_persistence_shift_dollars` | `(-22.816, -5.332]` | 505 | +0.000781 | +0.001910 | 66.94% | 72.67% |
| `minute_bucket` | holdout | `signed_velocity_dps_3m` | `(0.273, 2.981]` | 235 | +0.000622 | +0.001020 | 70.66% | 69.79% |
| `minute_bucket` | validation | `seconds_to_close` | `(300.0, 600.0]` | 326 | +0.000516 | +0.000918 | 52.61% | 51.84% |
| `all_heartbeats` | validation | `v33_antipersist3_anti_persistence_shift_dollars` | `(4.79, 21.671]` | 467 | +0.000490 | +0.001174 | 40.42% | 36.83% |
| `all_heartbeats` | validation | `seconds_to_close` | `(300.0, 600.0]` | 1303 | +0.000473 | +0.000881 | 52.77% | 52.03% |
| `all_heartbeats` | holdout | `signed_velocity_dps_3m` | `(-0.257, -0.122]` | 453 | +0.000465 | +0.001101 | 36.37% | 30.91% |
| `minute_bucket` | validation | `v33_antipersist3_anti_persistence_shift_dollars` | `(6.12, 25.647]` | 122 | +0.000346 | +0.000718 | 40.14% | 37.70% |
| `minute_bucket` | holdout | `signed_velocity_dps_3m` | `(-0.256, -0.12]` | 116 | +0.000334 | +0.000803 | 36.78% | 31.90% |
| `minute_bucket` | validation | `v33_antipersist3_anti_persistence_shift_dollars` | `(0.677, 6.12]` | 130 | +0.000322 | +0.000764 | 44.81% | 35.38% |
| `minute_bucket` | validation | `signed_velocity_dps_3m` | `(-0.0533, 8.33e-05]` | 138 | +0.000319 | +0.000435 | 44.44% | 39.86% |
| `all_heartbeats` | validation | `signed_velocity_dps_3m` | `(-0.0533, 0.000278]` | 530 | +0.000300 | +0.000427 | 44.37% | 40.19% |
| `all_heartbeats` | holdout | `signed_velocity_dps_3m` | `(0.273, 2.981]` | 906 | +0.000290 | +0.000439 | 71.58% | 70.86% |
| `all_heartbeats` | validation | `signed_velocity_dps_3m` | `(0.0593, 0.134]` | 462 | +0.000237 | +0.000935 | 57.24% | 59.96% |

## Best V33 Buckets

| dataset | split | feature | bucket | rows | Brier delta | logloss delta | mean p_yes | yes rate |
|---|---|---|---|---:|---:|---:|---:|---:|
| `minute_bucket` | validation | `v33_antipersist3_anti_persistence_shift_dollars` | `(-920.275, -26.812]` | 106 | -0.005548 | -0.015437 | 71.12% | 66.98% |
| `all_heartbeats` | validation | `v33_antipersist3_anti_persistence_shift_dollars` | `(-920.275, -22.816]` | 418 | -0.004546 | -0.013069 | 72.45% | 68.66% |
| `minute_bucket` | validation | `v33_antipersist3_anti_persistence_shift_dollars` | `(25.647, 520.961]` | 109 | -0.003964 | -0.011023 | 32.39% | 41.28% |
| `all_heartbeats` | validation | `signed_velocity_dps_3m` | `(0.273, 2.981]` | 381 | -0.003956 | -0.011656 | 84.89% | 83.99% |
| `minute_bucket` | validation | `seconds_to_close` | `(600.0, 900.0]` | 327 | -0.003074 | -0.008382 | 50.27% | 51.99% |
| `all_heartbeats` | validation | `v33_antipersist3_anti_persistence_shift_dollars` | `(21.671, 520.961]` | 429 | -0.002840 | -0.008623 | 30.97% | 39.39% |
| `all_heartbeats` | validation | `abs_v32_d_sigma` | `(0.75, 1.0]` | 255 | -0.002599 | -0.008391 | 52.77% | 47.45% |
| `all_heartbeats` | validation | `seconds_to_close` | `(600.0, 900.0]` | 1198 | -0.002517 | -0.007244 | 50.38% | 52.09% |
| `all_heartbeats` | validation | `signed_velocity_dps_3m` | `(-3.35, -0.257]` | 297 | -0.001822 | -0.007436 | 28.75% | 31.99% |
| `minute_bucket` | validation | `abs_v32_d_sigma` | `(-0.001, 0.25]` | 251 | -0.001763 | -0.003685 | 49.59% | 49.00% |
| `minute_bucket` | validation | `signed_velocity_dps_3m` | `(-0.256, -0.12]` | 116 | -0.001630 | -0.003880 | 34.30% | 37.93% |
| `minute_bucket` | all | `v33_antipersist3_anti_persistence_shift_dollars` | `(25.647, 520.961]` | 613 | -0.001541 | -0.003882 | 34.06% | 35.56% |

## Read

- v33 should not be promoted if the block improvement is narrow or if a large physics bucket is consistently worse.
- Stable improvement here is still retrospective evidence; strict-forward rows remain mandatory.
