# v35 Horizon/Temperature Refine

Generated UTC: `2026-05-04T20:44:44.045352+00:00`

## Scope

- Pure FV probability-model replay, not trade scoring.
- Tests whether longer v34 settlement/proxy horizons need a softer posterior temperature.
- Reference is current research best `v34_h110_t098`.
- No live bot code/process or orders are touched.

## Ranked Versus v34_h110_t098

| model | horizon | temp | val dBrier | hold dBrier | val dLogloss | hold dLogloss | all Brier cells? | all logloss cells? |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `v34_h150_t102` | 150 | 1.02 | -0.000208 | -0.000121 | -0.000580 | -0.000057 | True | True |
| `v34_h140_t102` | 140 | 1.02 | -0.000164 | -0.000090 | -0.000399 | +0.000019 | True | False |
| `v34_h150_t100` | 150 | 1.00 | -0.000156 | -0.000150 | -0.000290 | +0.000078 | True | False |
| `v34_h140_t100` | 140 | 1.00 | -0.000120 | -0.000128 | -0.000146 | +0.000117 | True | False |
| `v34_h130_t102` | 130 | 1.02 | -0.000116 | -0.000016 | -0.000212 | +0.000151 | False | False |
| `v34_h120_t102` | 120 | 1.02 | -0.000116 | +0.000092 | -0.000140 | +0.000435 | False | False |
| `v34_h150_t098` | 150 | 0.98 | -0.000090 | -0.000168 | +0.000080 | +0.000277 | False | False |
| `v34_h120_t100` | 120 | 1.00 | -0.000087 | +0.000040 | +0.000035 | +0.000461 | False | False |
| `v34_h130_t100` | 130 | 1.00 | -0.000080 | -0.000061 | +0.000003 | +0.000211 | True | False |
| `v34_h110_t102` | 110 | 1.02 | -0.000070 | +0.000091 | -0.000408 | -0.000100 | False | False |
| `v34_h140_t098` | 140 | 0.98 | -0.000062 | -0.000154 | +0.000187 | +0.000278 | False | False |
| `v34_h120_t098` | 120 | 0.98 | -0.000045 | -0.000001 | +0.000286 | +0.000547 | False | False |
| `v34_h110_t100` | 110 | 1.00 | -0.000042 | +0.000040 | -0.000242 | -0.000080 | False | True |
| `v34_h130_t098` | 130 | 0.98 | -0.000029 | -0.000095 | +0.000297 | +0.000334 | False | False |
| `v34_h110_t098` | 110 | 0.98 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | False | False |

## Split Metrics

| mode | split | model | horizon | temp | Brier | logloss | ECE10 | side acc |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `two_side_all_heartbeats` | holdout | `v34_h140_t098` | 140 | 0.98 | 0.146873 | 0.438271 | 0.009449 | 76.98% |
| `two_side_all_heartbeats` | holdout | `v34_h140_t100` | 140 | 1.00 | 0.146883 | 0.438019 | 0.010683 | 76.98% |
| `two_side_all_heartbeats` | holdout | `v34_h130_t098` | 130 | 0.98 | 0.146902 | 0.438151 | 0.009204 | 76.98% |
| `two_side_all_heartbeats` | holdout | `v34_h140_t102` | 140 | 1.02 | 0.146905 | 0.437836 | 0.011090 | 76.98% |
| `two_side_all_heartbeats` | holdout | `v34_h130_t100` | 130 | 1.00 | 0.146918 | 0.437933 | 0.010555 | 76.98% |
| `two_side_all_heartbeats` | holdout | `v34_h150_t098` | 150 | 0.98 | 0.146924 | 0.438498 | 0.009810 | 76.95% |
| `two_side_all_heartbeats` | holdout | `v34_h150_t100` | 150 | 1.00 | 0.146927 | 0.438214 | 0.010237 | 76.95% |
| `two_side_all_heartbeats` | holdout | `v34_h150_t102` | 150 | 1.02 | 0.146942 | 0.438000 | 0.010788 | 76.95% |
| `two_side_all_heartbeats` | holdout | `v34_h130_t102` | 130 | 1.02 | 0.146946 | 0.437781 | 0.011966 | 76.98% |
| `two_side_all_heartbeats` | holdout | `v34_h120_t098` | 120 | 0.98 | 0.146979 | 0.438221 | 0.009933 | 76.98% |
| `two_side_all_heartbeats` | holdout | `v34_h120_t100` | 120 | 1.00 | 0.147001 | 0.438033 | 0.011587 | 76.98% |
| `two_side_all_heartbeats` | holdout | `v34_h110_t098` | 110 | 0.98 | 0.147009 | 0.438003 | 0.010775 | 76.98% |
| `two_side_all_heartbeats` | holdout | `v34_h120_t102` | 120 | 1.02 | 0.147035 | 0.437909 | 0.012752 | 76.98% |
| `two_side_all_heartbeats` | holdout | `v34_h110_t100` | 110 | 1.00 | 0.147037 | 0.437849 | 0.012178 | 76.98% |
| `two_side_all_heartbeats` | holdout | `v34_h110_t102` | 110 | 1.02 | 0.147076 | 0.437759 | 0.013247 | 76.98% |
| `two_side_all_heartbeats` | validation | `v34_h150_t102` | 150 | 1.02 | 0.134198 | 0.401509 | 0.009396 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h120_t102` | 120 | 1.02 | 0.134220 | 0.401406 | 0.010052 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h140_t102` | 140 | 1.02 | 0.134228 | 0.401521 | 0.009451 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h110_t102` | 110 | 1.02 | 0.134247 | 0.401393 | 0.009673 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h150_t100` | 150 | 1.00 | 0.134265 | 0.401883 | 0.009831 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h120_t100` | 120 | 1.00 | 0.134268 | 0.401681 | 0.008540 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h130_t102` | 130 | 1.02 | 0.134270 | 0.401601 | 0.009294 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h140_t100` | 140 | 1.00 | 0.134289 | 0.401864 | 0.009198 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h110_t100` | 110 | 1.00 | 0.134290 | 0.401635 | 0.007122 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h130_t100` | 130 | 1.00 | 0.134325 | 0.401913 | 0.009454 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h120_t098` | 120 | 0.98 | 0.134330 | 0.402037 | 0.009950 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h110_t098` | 110 | 0.98 | 0.134346 | 0.401956 | 0.010299 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h150_t098` | 150 | 0.98 | 0.134347 | 0.402341 | 0.011867 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h140_t098` | 140 | 0.98 | 0.134365 | 0.402290 | 0.010963 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h130_t098` | 130 | 0.98 | 0.134394 | 0.402308 | 0.010887 | 79.10% |
| `two_side_minute_bucket` | holdout | `v34_h150_t098` | 150 | 0.98 | 0.150261 | 0.446338 | 0.015884 | 76.07% |
| `two_side_minute_bucket` | holdout | `v34_h150_t100` | 150 | 1.00 | 0.150294 | 0.446222 | 0.012119 | 76.07% |
| `two_side_minute_bucket` | holdout | `v34_h150_t102` | 150 | 1.02 | 0.150338 | 0.446168 | 0.012490 | 76.07% |
| `two_side_minute_bucket` | holdout | `v34_h140_t098` | 140 | 0.98 | 0.150341 | 0.446566 | 0.011656 | 76.18% |
| `two_side_minute_bucket` | holdout | `v34_h140_t100` | 140 | 1.00 | 0.150383 | 0.446495 | 0.012602 | 76.18% |
| `two_side_minute_bucket` | holdout | `v34_h130_t098` | 130 | 0.98 | 0.150430 | 0.446798 | 0.011479 | 76.18% |
| `two_side_minute_bucket` | holdout | `v34_h140_t102` | 140 | 1.02 | 0.150436 | 0.446484 | 0.012339 | 76.18% |
| `two_side_minute_bucket` | holdout | `v34_h130_t100` | 130 | 1.00 | 0.150482 | 0.446771 | 0.012113 | 76.18% |
| `two_side_minute_bucket` | holdout | `v34_h110_t098` | 110 | 0.98 | 0.150513 | 0.446279 | 0.011302 | 76.18% |
| `two_side_minute_bucket` | holdout | `v34_h120_t098` | 120 | 0.98 | 0.150541 | 0.447154 | 0.010729 | 76.18% |
| `two_side_minute_bucket` | holdout | `v34_h130_t102` | 130 | 1.02 | 0.150543 | 0.446803 | 0.014122 | 76.18% |
| `two_side_minute_bucket` | holdout | `v34_h110_t100` | 110 | 1.00 | 0.150565 | 0.446273 | 0.013550 | 76.18% |
| `two_side_minute_bucket` | holdout | `v34_h120_t100` | 120 | 1.00 | 0.150601 | 0.447170 | 0.013682 | 76.18% |
| `two_side_minute_bucket` | holdout | `v34_h110_t102` | 110 | 1.02 | 0.150628 | 0.446323 | 0.015372 | 76.18% |
| `two_side_minute_bucket` | holdout | `v34_h120_t102` | 120 | 1.02 | 0.150672 | 0.447242 | 0.016337 | 76.18% |
| `two_side_minute_bucket` | validation | `v34_h150_t102` | 150 | 1.02 | 0.137187 | 0.409154 | 0.008921 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h150_t100` | 150 | 1.00 | 0.137223 | 0.409360 | 0.010118 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h140_t102` | 140 | 1.02 | 0.137244 | 0.409505 | 0.009582 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h140_t100` | 140 | 1.00 | 0.137271 | 0.409669 | 0.009977 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h150_t098` | 150 | 0.98 | 0.137273 | 0.409643 | 0.011274 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h130_t102` | 130 | 1.02 | 0.137297 | 0.409799 | 0.009821 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h140_t098` | 140 | 0.98 | 0.137312 | 0.409908 | 0.009384 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h130_t100` | 130 | 1.00 | 0.137316 | 0.409917 | 0.009614 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h120_t102` | 120 | 1.02 | 0.137348 | 0.410138 | 0.007632 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h130_t098` | 130 | 0.98 | 0.137348 | 0.410110 | 0.009399 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h120_t100` | 120 | 1.00 | 0.137358 | 0.410213 | 0.010262 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h120_t098` | 120 | 0.98 | 0.137381 | 0.410360 | 0.009232 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h110_t102` | 110 | 1.02 | 0.137413 | 0.409616 | 0.006184 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h110_t100` | 110 | 1.00 | 0.137427 | 0.409706 | 0.010625 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h110_t098` | 110 | 0.98 | 0.137455 | 0.409868 | 0.012260 | 78.21% |

## Read

- Best validation candidate: `v34_h150_t102`.
- Candidates beating the reference on every validation/holdout Brier cell: 5.
- Candidates beating the reference on every validation/holdout Brier and logloss cell: 1.
- If the Brier gain requires worse logloss, treat it as sharper but less trustworthy probability, not a promotion-ready FV model.
