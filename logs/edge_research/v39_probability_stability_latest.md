# v39 Probability Stability

Generated UTC: `2026-05-04T23:50:35.057190+00:00`

## Scope

- Pure FV probability block audit, not trade scoring.
- Candidate: v39 mid-band v28 fallback versus live v28 and v38.
- No live bot code/process or orders are touched.

## Split Metrics

| dataset | split | model | rows | Brier | logloss | side acc | mean p_yes | yes rate |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `all_heartbeats` | all | `v28_live_surface` | 19021 | 0.147196 | 0.441154 | 77.66% | 50.78% | 49.58% |
| `all_heartbeats` | all | `v38_long60_antipersist` | 19021 | 0.145917 | 0.440021 | 77.64% | 50.66% | 49.58% |
| `all_heartbeats` | all | `v39_midband_v28_fallback` | 19021 | 0.145878 | 0.439751 | 77.69% | 50.67% | 49.58% |
| `all_heartbeats` | train | `v28_live_surface` | 11398 | 0.150212 | 0.450534 | 77.43% | 51.33% | 50.93% |
| `all_heartbeats` | train | `v38_long60_antipersist` | 11398 | 0.149531 | 0.453791 | 77.37% | 51.31% | 50.93% |
| `all_heartbeats` | train | `v39_midband_v28_fallback` | 11398 | 0.149573 | 0.453646 | 77.39% | 51.31% | 50.93% |
| `all_heartbeats` | validation | `v28_live_surface` | 3818 | 0.136672 | 0.410485 | 78.58% | 52.11% | 51.89% |
| `all_heartbeats` | validation | `v38_long60_antipersist` | 3818 | 0.134234 | 0.401405 | 79.10% | 51.96% | 51.89% |
| `all_heartbeats` | validation | `v39_midband_v28_fallback` | 3818 | 0.134003 | 0.400991 | 79.10% | 51.97% | 51.89% |
| `all_heartbeats` | holdout | `v28_live_surface` | 3805 | 0.148720 | 0.443827 | 77.42% | 47.80% | 43.23% |
| `all_heartbeats` | holdout | `v38_long60_antipersist` | 3805 | 0.146815 | 0.437520 | 76.95% | 47.41% | 43.23% |
| `all_heartbeats` | holdout | `v39_midband_v28_fallback` | 3805 | 0.146727 | 0.437022 | 77.16% | 47.44% | 43.23% |
| `minute_bucket` | all | `v28_live_surface` | 4898 | 0.150816 | 0.451037 | 76.77% | 50.75% | 49.63% |
| `minute_bucket` | all | `v38_long60_antipersist` | 4898 | 0.148799 | 0.443461 | 76.77% | 50.64% | 49.63% |
| `minute_bucket` | all | `v39_midband_v28_fallback` | 4898 | 0.148781 | 0.443325 | 76.81% | 50.65% | 49.63% |
| `minute_bucket` | train | `v28_live_surface` | 2938 | 0.153673 | 0.459979 | 76.51% | 51.25% | 50.99% |
| `minute_bucket` | train | `v38_long60_antipersist` | 2938 | 0.152138 | 0.454207 | 76.51% | 51.25% | 50.99% |
| `minute_bucket` | train | `v39_midband_v28_fallback` | 2938 | 0.152198 | 0.454185 | 76.51% | 51.25% | 50.99% |
| `minute_bucket` | validation | `v28_live_surface` | 982 | 0.140475 | 0.421010 | 77.60% | 52.01% | 51.83% |
| `minute_bucket` | validation | `v38_long60_antipersist` | 982 | 0.137317 | 0.409154 | 78.21% | 51.89% | 51.83% |
| `minute_bucket` | validation | `v39_midband_v28_fallback` | 982 | 0.137129 | 0.408921 | 78.21% | 51.90% | 51.83% |
| `minute_bucket` | holdout | `v28_live_surface` | 978 | 0.152618 | 0.454326 | 76.69% | 47.98% | 43.35% |
| `minute_bucket` | holdout | `v38_long60_antipersist` | 978 | 0.150299 | 0.445625 | 76.07% | 47.56% | 43.35% |
| `minute_bucket` | holdout | `v39_midband_v28_fallback` | 978 | 0.150215 | 0.445246 | 76.28% | 47.59% | 43.35% |

## Chronological Blocks

| dataset | base | block kind | Brier improved | logloss improved | mean Brier delta | worst Brier delta | mean logloss delta | worst logloss delta |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `all_heartbeats` | `v28_live_surface` | `block10` | 8/10 | 7/10 | -0.001317 | +0.001200 | -0.001386 | +0.022551 |
| `all_heartbeats` | `v28_live_surface` | `block20` | 16/20 | 17/20 | -0.001313 | +0.003097 | -0.001302 | +0.058735 |
| `all_heartbeats` | `v38_long60_antipersist` | `block10` | 6/10 | 6/10 | -0.000039 | +0.000818 | -0.000272 | +0.002194 |
| `all_heartbeats` | `v38_long60_antipersist` | `block20` | 9/20 | 11/20 | -0.000042 | +0.001472 | -0.000278 | +0.004270 |
| `minute_bucket` | `v28_live_surface` | `block10` | 8/10 | 8/10 | -0.002039 | +0.000886 | -0.007705 | +0.003429 |
| `minute_bucket` | `v28_live_surface` | `block20` | 17/20 | 17/20 | -0.002036 | +0.003123 | -0.007686 | +0.018812 |
| `minute_bucket` | `v38_long60_antipersist` | `block10` | 6/10 | 6/10 | -0.000019 | +0.000758 | -0.000139 | +0.001969 |
| `minute_bucket` | `v38_long60_antipersist` | `block20` | 9/20 | 11/20 | -0.000021 | +0.001344 | -0.000143 | +0.003852 |

## Read

- v39 should become the leading FV probability candidate only if it improves v38 without material block-level damage.
