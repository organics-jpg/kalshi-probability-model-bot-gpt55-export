# v35 Anti-Persistence Materiality Sweep

Generated UTC: `2026-05-04T20:33:38.758696+00:00`

## Scope

- Pure FV probability-model sweep, not trade scoring.
- Tests whether anti-persistence materiality should be measured in sigma units rather than fixed dollars.
- Primary ranking uses validation splits; holdout is shown as a forward-style check.
- No live bot code/process or orders are touched.

## Reference Surfaces

| dataset | split | model | rows | Brier | logloss | side acc | mean p_yes | yes rate |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `all_heartbeats` | validation | `v28_live_surface` | 3818 | 0.136672 | 0.410485 | 78.58% | 52.11% | 51.89% |
| `all_heartbeats` | holdout | `v28_live_surface` | 3805 | 0.148720 | 0.443827 | 77.42% | 47.80% | 43.23% |
| `all_heartbeats` | validation | `v32_avg110_final60_exact` | 3818 | 0.136017 | 0.406971 | 78.58% | 52.01% | 51.89% |
| `all_heartbeats` | holdout | `v32_avg110_final60_exact` | 3805 | 0.147142 | 0.438480 | 77.32% | 47.51% | 43.23% |
| `all_heartbeats` | validation | `v33_antipersist3` | 3818 | 0.135380 | 0.404928 | 78.71% | 51.99% | 51.89% |
| `all_heartbeats` | holdout | `v33_antipersist3` | 3805 | 0.147029 | 0.438362 | 76.66% | 47.47% | 43.23% |
| `all_heartbeats` | validation | `v34_material_antipersist3` | 3818 | 0.134346 | 0.401956 | 79.10% | 51.96% | 51.89% |
| `all_heartbeats` | holdout | `v34_material_antipersist3` | 3805 | 0.147009 | 0.438003 | 76.98% | 47.44% | 43.23% |
| `minute_bucket` | validation | `v28_live_surface` | 982 | 0.140475 | 0.421010 | 77.60% | 52.01% | 51.83% |
| `minute_bucket` | holdout | `v28_live_surface` | 978 | 0.152618 | 0.454326 | 76.69% | 47.98% | 43.35% |
| `minute_bucket` | validation | `v32_avg110_final60_exact` | 982 | 0.139558 | 0.415930 | 77.60% | 51.93% | 51.83% |
| `minute_bucket` | holdout | `v32_avg110_final60_exact` | 978 | 0.150618 | 0.446803 | 76.58% | 47.69% | 43.35% |
| `minute_bucket` | validation | `v33_antipersist3` | 982 | 0.138692 | 0.413334 | 77.80% | 51.92% | 51.83% |
| `minute_bucket` | holdout | `v33_antipersist3` | 978 | 0.150490 | 0.446548 | 75.97% | 47.64% | 43.35% |
| `minute_bucket` | validation | `v34_material_antipersist3` | 982 | 0.137455 | 0.409868 | 78.21% | 51.89% | 51.83% |
| `minute_bucket` | holdout | `v34_material_antipersist3` | 978 | 0.150513 | 0.446279 | 76.18% | 47.59% | 43.35% |

## Best Validation Candidate

- `sweep_sigma_ss1.25_asm0.90_w0.125_c0.650_gw0.050_t1.00`
- kind/shift/anchor/weight/center/width/temp: `sigma` / `1.25` / `0.9` / `0.125` / `0.65` / `0.05` / `1.0`
- validation mean Brier delta vs v32: -0.002980
- holdout mean Brier delta vs v32: +0.000353

## Best Robust Candidate

- `sweep_dollar_ss1.00_asm1.00_w0.125_c40.000_gw5.000_t0.98`
- validation mean Brier delta vs v32: -0.002281
- holdout mean Brier delta vs v32: -0.000054

## Top Validation Rows

| model | kind | ss | asm | weight | center | width | temp | val dBrier | hold dBrier | val dLogloss | hold dLogloss | hold both? |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `sweep_sigma_ss1.25_asm0.90_w0.125_c0.650_gw0.050_t1.00` | `sigma` | 1.25 | 0.90 | 0.125 | 0.650 | 0.050 | 1.00 | -0.002980 | +0.000353 | -0.008895 | +0.000442 | False |
| `sweep_sigma_ss1.25_asm0.90_w0.125_c0.650_gw0.050_t0.99` | `sigma` | 1.25 | 0.90 | 0.125 | 0.650 | 0.050 | 0.99 | -0.002973 | +0.000332 | -0.008838 | +0.000473 | False |
| `sweep_sigma_ss1.25_asm0.90_w0.125_c0.650_gw0.050_t0.98` | `sigma` | 1.25 | 0.90 | 0.125 | 0.650 | 0.050 | 0.98 | -0.002962 | +0.000315 | -0.008763 | +0.000520 | False |
| `sweep_sigma_ss1.25_asm0.90_w0.125_c0.650_gw0.100_t1.00` | `sigma` | 1.25 | 0.90 | 0.125 | 0.650 | 0.100 | 1.00 | -0.002888 | +0.000333 | -0.008654 | +0.000389 | False |
| `sweep_sigma_ss1.25_asm0.90_w0.125_c0.650_gw0.100_t0.99` | `sigma` | 1.25 | 0.90 | 0.125 | 0.650 | 0.100 | 0.99 | -0.002880 | +0.000312 | -0.008595 | +0.000419 | False |
| `sweep_sigma_ss1.25_asm0.90_w0.125_c0.650_gw0.100_t0.98` | `sigma` | 1.25 | 0.90 | 0.125 | 0.650 | 0.100 | 0.98 | -0.002869 | +0.000294 | -0.008517 | +0.000465 | False |
| `sweep_sigma_ss1.25_asm1.00_w0.125_c0.650_gw0.050_t1.00` | `sigma` | 1.25 | 1.00 | 0.125 | 0.650 | 0.050 | 1.00 | -0.002832 | +0.000258 | -0.008528 | +0.000195 | False |
| `sweep_sigma_ss1.25_asm1.00_w0.125_c0.650_gw0.050_t0.99` | `sigma` | 1.25 | 1.00 | 0.125 | 0.650 | 0.050 | 0.99 | -0.002823 | +0.000237 | -0.008468 | +0.000225 | False |
| `sweep_sigma_ss1.25_asm1.00_w0.125_c0.650_gw0.050_t0.98` | `sigma` | 1.25 | 1.00 | 0.125 | 0.650 | 0.050 | 0.98 | -0.002811 | +0.000219 | -0.008389 | +0.000271 | False |
| `sweep_dollar_ss1.25_asm1.00_w0.125_c40.000_gw5.000_t1.00` | `dollar` | 1.25 | 1.00 | 0.125 | 40.000 | 5.000 | 1.00 | -0.002807 | +0.000180 | -0.008420 | -0.000115 | False |
| `sweep_dollar_ss1.25_asm1.00_w0.125_c40.000_gw5.000_t0.99` | `dollar` | 1.25 | 1.00 | 0.125 | 40.000 | 5.000 | 0.99 | -0.002798 | +0.000155 | -0.008356 | -0.000101 | False |
| `sweep_dollar_ss1.25_asm1.00_w0.125_c40.000_gw5.000_t0.98` | `dollar` | 1.25 | 1.00 | 0.125 | 40.000 | 5.000 | 0.98 | -0.002785 | +0.000132 | -0.008272 | -0.000072 | False |
| `sweep_sigma_ss1.25_asm0.90_w0.125_c0.650_gw0.200_t1.00` | `sigma` | 1.25 | 0.90 | 0.125 | 0.650 | 0.200 | 1.00 | -0.002766 | +0.000295 | -0.008348 | +0.000335 | False |
| `sweep_dollar_ss1.25_asm1.00_w0.125_c60.000_gw5.000_t1.00` | `dollar` | 1.25 | 1.00 | 0.125 | 60.000 | 5.000 | 1.00 | -0.002765 | +0.000205 | -0.008142 | -0.000032 | False |
| `sweep_sigma_ss1.25_asm0.90_w0.125_c0.650_gw0.200_t0.99` | `sigma` | 1.25 | 0.90 | 0.125 | 0.650 | 0.200 | 0.99 | -0.002757 | +0.000273 | -0.008286 | +0.000365 | False |
| `sweep_dollar_ss1.25_asm1.00_w0.125_c60.000_gw5.000_t0.99` | `dollar` | 1.25 | 1.00 | 0.125 | 60.000 | 5.000 | 0.99 | -0.002751 | +0.000181 | -0.008059 | -0.000012 | False |
| `sweep_sigma_ss1.25_asm1.00_w0.125_c0.650_gw0.100_t1.00` | `sigma` | 1.25 | 1.00 | 0.125 | 0.650 | 0.100 | 1.00 | -0.002749 | +0.000240 | -0.008307 | +0.000145 | False |
| `sweep_sigma_ss1.25_asm0.90_w0.125_c0.650_gw0.200_t0.98` | `sigma` | 1.25 | 0.90 | 0.125 | 0.650 | 0.200 | 0.98 | -0.002745 | +0.000255 | -0.008205 | +0.000411 | False |
| `sweep_sigma_ss1.25_asm1.00_w0.125_c0.650_gw0.100_t0.99` | `sigma` | 1.25 | 1.00 | 0.125 | 0.650 | 0.100 | 0.99 | -0.002740 | +0.000219 | -0.008245 | +0.000174 | False |
| `sweep_dollar_ss1.25_asm1.00_w0.125_c60.000_gw5.000_t0.98` | `dollar` | 1.25 | 1.00 | 0.125 | 60.000 | 5.000 | 0.98 | -0.002734 | +0.000160 | -0.007956 | +0.000024 | False |
| `sweep_sigma_ss1.25_asm1.00_w0.125_c0.650_gw0.100_t0.98` | `sigma` | 1.25 | 1.00 | 0.125 | 0.650 | 0.100 | 0.98 | -0.002728 | +0.000201 | -0.008164 | +0.000219 | False |
| `sweep_dollar_ss1.25_asm1.00_w0.125_c40.000_gw10.000_t1.00` | `dollar` | 1.25 | 1.00 | 0.125 | 40.000 | 10.000 | 1.00 | -0.002717 | +0.000186 | -0.008174 | -0.000086 | False |
| `sweep_dollar_ss1.25_asm1.00_w0.125_c40.000_gw10.000_t0.99` | `dollar` | 1.25 | 1.00 | 0.125 | 40.000 | 10.000 | 0.99 | -0.002707 | +0.000160 | -0.008107 | -0.000071 | False |
| `sweep_dollar_ss1.25_asm1.00_w0.125_c40.000_gw10.000_t0.98` | `dollar` | 1.25 | 1.00 | 0.125 | 40.000 | 10.000 | 0.98 | -0.002694 | +0.000137 | -0.008022 | -0.000042 | False |
| `sweep_dollar_ss1.25_asm1.00_w0.125_c60.000_gw10.000_t1.00` | `dollar` | 1.25 | 1.00 | 0.125 | 60.000 | 10.000 | 1.00 | -0.002687 | +0.000193 | -0.007968 | -0.000048 | False |
| `sweep_sigma_ss1.25_asm0.90_w0.125_c0.500_gw0.100_t1.00` | `sigma` | 1.25 | 0.90 | 0.125 | 0.500 | 0.100 | 1.00 | -0.002687 | +0.000306 | -0.008185 | +0.000280 | False |
| `sweep_sigma_ss1.25_asm0.90_w0.125_c0.500_gw0.100_t0.99` | `sigma` | 1.25 | 0.90 | 0.125 | 0.500 | 0.100 | 0.99 | -0.002680 | +0.000283 | -0.008129 | +0.000305 | False |
| `sweep_sigma_ss1.25_asm1.10_w0.125_c0.650_gw0.050_t1.00` | `sigma` | 1.25 | 1.10 | 0.125 | 0.650 | 0.050 | 1.00 | -0.002677 | +0.000190 | -0.008142 | +0.000022 | False |
| `sweep_dollar_ss1.25_asm1.00_w0.125_c60.000_gw10.000_t0.99` | `dollar` | 1.25 | 1.00 | 0.125 | 60.000 | 10.000 | 0.99 | -0.002673 | +0.000169 | -0.007885 | -0.000028 | False |
| `sweep_sigma_ss1.25_asm0.90_w0.125_c0.500_gw0.100_t0.98` | `sigma` | 1.25 | 0.90 | 0.125 | 0.500 | 0.100 | 0.98 | -0.002670 | +0.000263 | -0.008054 | +0.000345 | False |

## Read

- A sigma-gated winner supports replacing v34's fixed-dollar materiality prior.
- A dollar-gated or fixed-weight winner means the current v34/v33 family is already close and v35 should not be forced.
- The holdout columns are not used to tune the first ranking; they are the stability check.
