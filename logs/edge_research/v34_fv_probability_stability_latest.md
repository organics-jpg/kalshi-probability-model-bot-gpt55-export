# v34 FV Probability Stability

Generated UTC: `2026-05-04T20:30:07.969684+00:00`

## Scope

- Research-only stability audit for pure FV probability, not scoring.
- Candidate: v34 materiality-gated anti-persistence FV surface versus v32 settlement/proxy FV surface.
- No live bot code/process or orders are touched.

## Split Metrics

| dataset | split | model | rows | Brier | logloss | side acc | mean p_yes | yes rate |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `all_heartbeats` | all | `v28_live_surface` | 19021 | 0.147196 | 0.441154 | 77.66% | 50.78% | 49.58% |
| `all_heartbeats` | all | `v32_avg110_final60_exact` | 19021 | 0.146350 | 0.441336 | 77.61% | 50.70% | 49.58% |
| `all_heartbeats` | all | `v34_material_antipersist3` | 19021 | 0.145993 | 0.440330 | 77.64% | 50.67% | 49.58% |
| `all_heartbeats` | train | `v28_live_surface` | 11398 | 0.150212 | 0.450534 | 77.43% | 51.33% | 50.93% |
| `all_heartbeats` | train | `v32_avg110_final60_exact` | 11398 | 0.149547 | 0.453800 | 77.39% | 51.33% | 50.93% |
| `all_heartbeats` | train | `v34_material_antipersist3` | 11398 | 0.149555 | 0.453961 | 77.37% | 51.31% | 50.93% |
| `all_heartbeats` | validation | `v28_live_surface` | 3818 | 0.136672 | 0.410485 | 78.58% | 52.11% | 51.89% |
| `all_heartbeats` | validation | `v32_avg110_final60_exact` | 3818 | 0.136017 | 0.406971 | 78.58% | 52.01% | 51.89% |
| `all_heartbeats` | validation | `v34_material_antipersist3` | 3818 | 0.134346 | 0.401956 | 79.10% | 51.96% | 51.89% |
| `all_heartbeats` | holdout | `v28_live_surface` | 3805 | 0.148720 | 0.443827 | 77.42% | 47.80% | 43.23% |
| `all_heartbeats` | holdout | `v32_avg110_final60_exact` | 3805 | 0.147142 | 0.438480 | 77.32% | 47.51% | 43.23% |
| `all_heartbeats` | holdout | `v34_material_antipersist3` | 3805 | 0.147009 | 0.438003 | 76.98% | 47.44% | 43.23% |
| `minute_bucket` | all | `v28_live_surface` | 4898 | 0.150816 | 0.451037 | 76.77% | 50.75% | 49.63% |
| `minute_bucket` | all | `v32_avg110_final60_exact` | 4898 | 0.149348 | 0.445275 | 76.75% | 50.68% | 49.63% |
| `minute_bucket` | all | `v34_material_antipersist3` | 4898 | 0.148914 | 0.443946 | 76.77% | 50.65% | 49.63% |
| `minute_bucket` | train | `v28_live_surface` | 2938 | 0.153673 | 0.459979 | 76.51% | 51.25% | 50.99% |
| `minute_bucket` | train | `v32_avg110_final60_exact` | 2938 | 0.152197 | 0.454575 | 76.51% | 51.26% | 50.99% |
| `minute_bucket` | train | `v34_material_antipersist3` | 2938 | 0.152212 | 0.454560 | 76.48% | 51.25% | 50.99% |
| `minute_bucket` | validation | `v28_live_surface` | 982 | 0.140475 | 0.421010 | 77.60% | 52.01% | 51.83% |
| `minute_bucket` | validation | `v32_avg110_final60_exact` | 982 | 0.139558 | 0.415930 | 77.60% | 51.93% | 51.83% |
| `minute_bucket` | validation | `v34_material_antipersist3` | 982 | 0.137455 | 0.409868 | 78.21% | 51.89% | 51.83% |
| `minute_bucket` | holdout | `v28_live_surface` | 978 | 0.152618 | 0.454326 | 76.69% | 47.98% | 43.35% |
| `minute_bucket` | holdout | `v32_avg110_final60_exact` | 978 | 0.150618 | 0.446803 | 76.58% | 47.69% | 43.35% |
| `minute_bucket` | holdout | `v34_material_antipersist3` | 978 | 0.150513 | 0.446279 | 76.18% | 47.59% | 43.35% |

## Chronological Blocks

| dataset | block kind | Brier improved | logloss improved | mean Brier delta | worst Brier delta | mean logloss delta | worst logloss delta |
|---|---|---:|---:|---:|---:|---:|---:|
| `all_heartbeats` | `block10` | 6/10 | 6/10 | -0.000359 | +0.000724 | -0.001005 | +0.001773 |
| `all_heartbeats` | `block20` | 12/20 | 14/20 | -0.000368 | +0.002173 | -0.001023 | +0.005122 |
| `minute_bucket` | `block10` | 5/10 | 6/10 | -0.000436 | +0.000852 | -0.001332 | +0.001639 |
| `minute_bucket` | `block20` | 12/20 | 12/20 | -0.000447 | +0.002430 | -0.001356 | +0.005562 |

## Worst v34 Buckets

Rows floor: 100. Positive delta means v34 is worse than v32.

| dataset | split | feature | bucket | rows | Brier delta | logloss delta | mean p_yes | yes rate |
|---|---|---|---|---:|---:|---:|---:|---:|
| `minute_bucket` | holdout | `abs_v32_d_sigma` | `(0.5, 0.75]` | 101 | +0.003990 | +0.008521 | 47.59% | 46.53% |
| `all_heartbeats` | holdout | `abs_v32_d_sigma` | `(0.5, 0.75]` | 397 | +0.002110 | +0.004392 | 47.09% | 45.59% |
| `minute_bucket` | holdout | `signed_velocity_dps_3m` | `(0.273, 2.981]` | 235 | +0.001676 | +0.003081 | 69.94% | 69.79% |
| `minute_bucket` | holdout | `v34_material_antipersist3_anti_persistence_shift_dollars` | `(-920.275, -26.812]` | 186 | +0.001104 | +0.001813 | 65.50% | 59.68% |
| `all_heartbeats` | holdout | `signed_velocity_dps_3m` | `(0.273, 2.981]` | 906 | +0.000743 | +0.001321 | 71.01% | 70.86% |
| `all_heartbeats` | holdout | `signed_velocity_dps_3m` | `(-0.257, -0.122]` | 453 | +0.000541 | +0.001129 | 36.42% | 30.91% |
| `all_heartbeats` | validation | `v34_material_antipersist3_anti_persistence_shift_dollars` | `(4.79, 21.671]` | 467 | +0.000413 | +0.000893 | 40.04% | 36.83% |
| `minute_bucket` | all | `abs_v32_d_sigma` | `(0.5, 0.75]` | 527 | +0.000387 | +0.000600 | 47.76% | 47.06% |
| `minute_bucket` | validation | `v34_material_antipersist3_anti_persistence_shift_dollars` | `(6.12, 25.647]` | 122 | +0.000380 | +0.000564 | 39.70% | 37.70% |
| `minute_bucket` | holdout | `abs_v32_d_sigma` | `(-0.001, 0.25]` | 293 | +0.000367 | +0.000731 | 49.18% | 39.93% |
| `all_heartbeats` | validation | `v34_material_antipersist3_anti_persistence_materiality_gate` | `(0.000925, 0.0031]` | 478 | +0.000333 | +0.001299 | 55.49% | 51.46% |
| `all_heartbeats` | validation | `v34_material_antipersist3_anti_persistence_logit_weight` | `(9.25e-05, 0.00031]` | 478 | +0.000333 | +0.001299 | 55.49% | 51.46% |
| `minute_bucket` | holdout | `signed_velocity_dps_3m` | `(-0.256, -0.12]` | 116 | +0.000327 | +0.000679 | 36.87% | 31.90% |
| `all_heartbeats` | holdout | `v34_material_antipersist3_anti_persistence_shift_dollars` | `(-920.275, -22.816]` | 713 | +0.000302 | +0.000186 | 66.54% | 60.03% |
| `all_heartbeats` | holdout | `abs_v32_d_sigma` | `(-0.001, 0.25]` | 1051 | +0.000270 | +0.000532 | 49.19% | 39.68% |
| `minute_bucket` | all | `signed_velocity_dps_3m` | `(0.273, 2.981]` | 613 | +0.000224 | -0.001151 | 76.25% | 76.67% |

## Best v34 Buckets

| dataset | split | feature | bucket | rows | Brier delta | logloss delta | mean p_yes | yes rate |
|---|---|---|---|---:|---:|---:|---:|---:|
| `all_heartbeats` | validation | `v34_material_antipersist3_anti_persistence_materiality_gate` | `(0.826, 1.0]` | 331 | -0.018771 | -0.055907 | 53.92% | 52.87% |
| `all_heartbeats` | validation | `v34_material_antipersist3_anti_persistence_logit_weight` | `(0.0826, 0.1]` | 331 | -0.018771 | -0.055907 | 53.92% | 52.87% |
| `minute_bucket` | validation | `v34_material_antipersist3_anti_persistence_shift_dollars` | `(-920.275, -26.812]` | 106 | -0.011672 | -0.032394 | 70.19% | 66.98% |
| `all_heartbeats` | validation | `v34_material_antipersist3_anti_persistence_shift_dollars` | `(-920.275, -22.816]` | 418 | -0.009949 | -0.028428 | 71.84% | 68.66% |
| `all_heartbeats` | validation | `signed_velocity_dps_3m` | `(0.273, 2.981]` | 381 | -0.008258 | -0.025355 | 84.27% | 83.99% |
| `minute_bucket` | validation | `v34_material_antipersist3_anti_persistence_shift_dollars` | `(25.647, 520.961]` | 109 | -0.007556 | -0.021848 | 33.12% | 41.28% |
| `minute_bucket` | validation | `seconds_to_close` | `(600.0, 900.0]` | 327 | -0.006284 | -0.017151 | 50.21% | 51.99% |
| `all_heartbeats` | validation | `abs_v32_d_sigma` | `(0.75, 1.0]` | 255 | -0.005842 | -0.017001 | 52.68% | 47.45% |
| `all_heartbeats` | validation | `v34_material_antipersist3_anti_persistence_shift_dollars` | `(21.671, 520.961]` | 429 | -0.005330 | -0.016710 | 31.35% | 39.39% |
| `all_heartbeats` | validation | `seconds_to_close` | `(600.0, 900.0]` | 1198 | -0.005315 | -0.015094 | 50.30% | 52.09% |
| `all_heartbeats` | validation | `signed_velocity_dps_3m` | `(-3.35, -0.257]` | 297 | -0.004476 | -0.017526 | 29.13% | 31.99% |
| `minute_bucket` | validation | `abs_v32_d_sigma` | `(-0.001, 0.25]` | 251 | -0.004085 | -0.008735 | 49.55% | 49.00% |

## Read

- v34 should not be promoted if the block improvement is narrow or if a large physics bucket is consistently worse.
- Stable improvement here is still retrospective evidence; strict-forward rows remain mandatory.
