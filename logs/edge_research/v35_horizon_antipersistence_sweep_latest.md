# v35 Horizon/Anti-Persistence Sweep

Generated UTC: `2026-05-04T20:39:20.870046+00:00`

## Scope

- Pure FV probability-model replay, not trade scoring.
- Tests settlement/proxy horizons from 90s to 150s with and without v34 anti-persistence.
- Reference is current research best `v34_h110_antipersist`.
- No live bot code/process or orders are touched.

## Split Metrics

| mode | split | model | family | horizon | Brier | logloss | ECE10 | side acc |
|---|---|---|---|---:|---:|---:|---:|---:|
| `two_side_all_heartbeats` | holdout | `v34_h140_antipersist` | `v34_antipersist` | 140 | 0.146873 | 0.438271 | 0.009449 | 76.98% |
| `two_side_all_heartbeats` | holdout | `v34_h130_antipersist` | `v34_antipersist` | 130 | 0.146902 | 0.438151 | 0.009204 | 76.98% |
| `two_side_all_heartbeats` | holdout | `v34_h150_antipersist` | `v34_antipersist` | 150 | 0.146924 | 0.438498 | 0.009810 | 76.95% |
| `two_side_all_heartbeats` | holdout | `v34_h120_antipersist` | `v34_antipersist` | 120 | 0.146979 | 0.438221 | 0.009933 | 76.98% |
| `two_side_all_heartbeats` | holdout | `v32_h140_settle` | `v32_settle` | 140 | 0.147007 | 0.438723 | 0.009359 | 77.32% |
| `two_side_all_heartbeats` | holdout | `v34_h110_antipersist` | `v34_antipersist` | 110 | 0.147009 | 0.438003 | 0.010775 | 76.98% |
| `two_side_all_heartbeats` | holdout | `v32_h130_settle` | `v32_settle` | 130 | 0.147036 | 0.438612 | 0.009782 | 77.32% |
| `two_side_all_heartbeats` | holdout | `v32_h150_settle` | `v32_settle` | 150 | 0.147057 | 0.438945 | 0.008304 | 77.32% |
| `two_side_all_heartbeats` | holdout | `v34_h100_antipersist` | `v34_antipersist` | 100 | 0.147061 | 0.438048 | 0.011188 | 76.98% |
| `two_side_all_heartbeats` | holdout | `v32_h120_settle` | `v32_settle` | 120 | 0.147113 | 0.438688 | 0.011359 | 77.32% |
| `two_side_all_heartbeats` | holdout | `v32_h110_settle` | `v32_settle` | 110 | 0.147142 | 0.438480 | 0.011438 | 77.32% |
| `two_side_all_heartbeats` | holdout | `v34_h90_antipersist` | `v34_antipersist` | 90 | 0.147144 | 0.438231 | 0.012389 | 76.98% |
| `two_side_all_heartbeats` | holdout | `v32_h100_settle` | `v32_settle` | 100 | 0.147195 | 0.438537 | 0.012125 | 77.35% |
| `two_side_all_heartbeats` | holdout | `v32_h90_settle` | `v32_settle` | 90 | 0.147278 | 0.438720 | 0.013349 | 77.35% |
| `two_side_all_heartbeats` | validation | `v34_h90_antipersist` | `v34_antipersist` | 90 | 0.134328 | 0.401862 | 0.009193 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h120_antipersist` | `v34_antipersist` | 120 | 0.134330 | 0.402037 | 0.009950 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h110_antipersist` | `v34_antipersist` | 110 | 0.134346 | 0.401956 | 0.010299 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h150_antipersist` | `v34_antipersist` | 150 | 0.134347 | 0.402341 | 0.011867 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h140_antipersist` | `v34_antipersist` | 140 | 0.134365 | 0.402290 | 0.010963 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h100_antipersist` | `v34_antipersist` | 100 | 0.134366 | 0.401972 | 0.008699 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h130_antipersist` | `v34_antipersist` | 130 | 0.134394 | 0.402308 | 0.010887 | 79.10% |
| `two_side_all_heartbeats` | validation | `v32_h90_settle` | `v32_settle` | 90 | 0.135996 | 0.406863 | 0.010873 | 78.58% |
| `two_side_all_heartbeats` | validation | `v32_h120_settle` | `v32_settle` | 120 | 0.136004 | 0.407064 | 0.013876 | 78.58% |
| `two_side_all_heartbeats` | validation | `v32_h110_settle` | `v32_settle` | 110 | 0.136017 | 0.406971 | 0.012900 | 78.58% |
| `two_side_all_heartbeats` | validation | `v32_h150_settle` | `v32_settle` | 150 | 0.136030 | 0.407410 | 0.016686 | 78.58% |
| `two_side_all_heartbeats` | validation | `v32_h100_settle` | `v32_settle` | 100 | 0.136035 | 0.406978 | 0.011902 | 78.58% |
| `two_side_all_heartbeats` | validation | `v32_h140_settle` | `v32_settle` | 140 | 0.136044 | 0.407344 | 0.015779 | 78.58% |
| `two_side_all_heartbeats` | validation | `v32_h130_settle` | `v32_settle` | 130 | 0.136072 | 0.407342 | 0.014861 | 78.58% |
| `two_side_minute_bucket` | holdout | `v34_h150_antipersist` | `v34_antipersist` | 150 | 0.150261 | 0.446338 | 0.015884 | 76.07% |
| `two_side_minute_bucket` | holdout | `v34_h140_antipersist` | `v34_antipersist` | 140 | 0.150341 | 0.446566 | 0.011656 | 76.18% |
| `two_side_minute_bucket` | holdout | `v32_h150_settle` | `v32_settle` | 150 | 0.150370 | 0.446852 | 0.008527 | 76.58% |
| `two_side_minute_bucket` | holdout | `v34_h130_antipersist` | `v34_antipersist` | 130 | 0.150430 | 0.446798 | 0.011479 | 76.18% |
| `two_side_minute_bucket` | holdout | `v32_h140_settle` | `v32_settle` | 140 | 0.150454 | 0.447099 | 0.009337 | 76.58% |
| `two_side_minute_bucket` | holdout | `v34_h110_antipersist` | `v34_antipersist` | 110 | 0.150513 | 0.446279 | 0.011302 | 76.18% |
| `two_side_minute_bucket` | holdout | `v34_h120_antipersist` | `v34_antipersist` | 120 | 0.150541 | 0.447154 | 0.010729 | 76.18% |
| `two_side_minute_bucket` | holdout | `v32_h130_settle` | `v32_settle` | 130 | 0.150544 | 0.447344 | 0.010920 | 76.58% |
| `two_side_minute_bucket` | holdout | `v32_h110_settle` | `v32_settle` | 110 | 0.150618 | 0.446803 | 0.012593 | 76.58% |
| `two_side_minute_bucket` | holdout | `v34_h100_antipersist` | `v34_antipersist` | 100 | 0.150623 | 0.446785 | 0.013030 | 76.07% |
| `two_side_minute_bucket` | holdout | `v32_h120_settle` | `v32_settle` | 120 | 0.150659 | 0.447726 | 0.012714 | 76.58% |
| `two_side_minute_bucket` | holdout | `v32_h100_settle` | `v32_settle` | 100 | 0.150727 | 0.447285 | 0.014732 | 76.58% |
| `two_side_minute_bucket` | holdout | `v34_h90_antipersist` | `v34_antipersist` | 90 | 0.150747 | 0.447131 | 0.014333 | 76.07% |
| `two_side_minute_bucket` | holdout | `v32_h90_settle` | `v32_settle` | 90 | 0.150853 | 0.447654 | 0.016042 | 76.58% |
| `two_side_minute_bucket` | validation | `v34_h150_antipersist` | `v34_antipersist` | 150 | 0.137273 | 0.409643 | 0.011274 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h140_antipersist` | `v34_antipersist` | 140 | 0.137312 | 0.409908 | 0.009384 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h130_antipersist` | `v34_antipersist` | 130 | 0.137348 | 0.410110 | 0.009399 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h100_antipersist` | `v34_antipersist` | 100 | 0.137362 | 0.409549 | 0.013761 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h120_antipersist` | `v34_antipersist` | 120 | 0.137381 | 0.410360 | 0.009232 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h90_antipersist` | `v34_antipersist` | 90 | 0.137409 | 0.409942 | 0.013893 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h110_antipersist` | `v34_antipersist` | 110 | 0.137455 | 0.409868 | 0.012260 | 78.21% |
| `two_side_minute_bucket` | validation | `v32_h150_settle` | `v32_settle` | 150 | 0.139400 | 0.415798 | 0.015574 | 77.60% |
| `two_side_minute_bucket` | validation | `v32_h140_settle` | `v32_settle` | 140 | 0.139436 | 0.416055 | 0.014299 | 77.60% |
| `two_side_minute_bucket` | validation | `v32_h100_settle` | `v32_settle` | 100 | 0.139458 | 0.415598 | 0.016033 | 77.60% |
| `two_side_minute_bucket` | validation | `v32_h130_settle` | `v32_settle` | 130 | 0.139469 | 0.416253 | 0.015205 | 77.60% |
| `two_side_minute_bucket` | validation | `v32_h120_settle` | `v32_settle` | 120 | 0.139500 | 0.416491 | 0.011687 | 77.60% |
| `two_side_minute_bucket` | validation | `v32_h90_settle` | `v32_settle` | 90 | 0.139504 | 0.415985 | 0.015959 | 77.60% |
| `two_side_minute_bucket` | validation | `v32_h110_settle` | `v32_settle` | 110 | 0.139558 | 0.415930 | 0.013575 | 77.60% |

## Ranked Versus v34_h110

| model | family | horizon | val dBrier | hold dBrier | val dLogloss | hold dLogloss | beats all val+hold? |
|---|---|---:|---:|---:|---:|---:|---|
| `v34_h150_antipersist` | `v34_antipersist` | 150 | -0.000090 | -0.000168 | +0.000080 | +0.000277 | False |
| `v34_h140_antipersist` | `v34_antipersist` | 140 | -0.000062 | -0.000154 | +0.000187 | +0.000278 | False |
| `v34_h120_antipersist` | `v34_antipersist` | 120 | -0.000045 | -0.000001 | +0.000286 | +0.000547 | False |
| `v34_h100_antipersist` | `v34_antipersist` | 100 | -0.000036 | +0.000081 | -0.000151 | +0.000276 | False |
| `v34_h90_antipersist` | `v34_antipersist` | 90 | -0.000032 | +0.000184 | -0.000010 | +0.000540 | False |
| `v34_h130_antipersist` | `v34_antipersist` | 130 | -0.000029 | -0.000095 | +0.000297 | +0.000334 | False |
| `v34_h110_antipersist` | `v34_antipersist` | 110 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | False |
| `v32_h150_settle` | `v32_settle` | 150 | +0.001815 | -0.000048 | +0.005692 | +0.000758 | False |
| `v32_h140_settle` | `v32_settle` | 140 | +0.001840 | -0.000031 | +0.005787 | +0.000770 | False |
| `v32_h100_settle` | `v32_settle` | 100 | +0.001846 | +0.000200 | +0.005376 | +0.000770 | False |
| `v32_h90_settle` | `v32_settle` | 90 | +0.001850 | +0.000304 | +0.005512 | +0.001046 | False |
| `v32_h120_settle` | `v32_settle` | 120 | +0.001852 | +0.000125 | +0.005866 | +0.001066 | False |
| `v32_h130_settle` | `v32_settle` | 130 | +0.001870 | +0.000029 | +0.005886 | +0.000837 | False |
| `v32_h110_settle` | `v32_settle` | 110 | +0.001887 | +0.000119 | +0.005539 | +0.000501 | False |

## Read

- Best validation candidate: `v34_h150_antipersist`.
- No horizon candidate beats current v34 on every validation/holdout Brier cell.
- If longer horizons only improve validation while weakening holdout, keep v34 at 110s and do not promote a horizon change.
