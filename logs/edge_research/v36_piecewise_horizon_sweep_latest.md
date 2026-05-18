# v36 Piecewise Horizon Sweep

Generated UTC: `2026-05-04T21:09:57.762546+00:00`

## Scope

- Pure FV probability-model replay, not trade scoring.
- Tests keeping v34's proxy horizon near expiry while blending toward v35 earlier.
- Reference is current v34; v35 is included as a comparison.
- No live bot code/process or orders are touched.

## Ranked Versus v34

| model | family | start | end | temp | train dBrier | val dBrier | hold dBrier | val dLogloss | hold dLogloss | all val+hold Brier+LL? |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `v35_h150_t102` | `v35_ref` | 0 | 0 | 1.02 | +0.000237 | -0.000208 | -0.000121 | -0.000580 | -0.000057 | True |
| `v36_s120_e300_t104` | `v36_piecewise` | 120 | 300 | 1.04 | +0.000112 | -0.000114 | -0.000052 | -0.000548 | -0.000291 | True |
| `v36_s120_e300_t102` | `v36_piecewise` | 120 | 300 | 1.02 | +0.000030 | -0.000075 | -0.000093 | -0.000336 | -0.000235 | True |
| `v36_s120_e300_t100` | `v36_piecewise` | 120 | 300 | 1.00 | -0.000043 | -0.000023 | -0.000123 | -0.000049 | -0.000119 | False |
| `v36_s180_e450_t104` | `v36_piecewise` | 180 | 450 | 1.04 | +0.000198 | -0.000019 | +0.000050 | -0.000189 | -0.000101 | False |
| `v36_s300_e900_t104` | `v36_piecewise` | 300 | 900 | 1.04 | +0.000239 | -0.000011 | +0.000157 | -0.000180 | -0.000026 | False |
| `v34_h110_t098` | `v34_ref` | 0 | 0 | 0.98 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | False |
| `v36_s180_e600_t104` | `v36_piecewise` | 180 | 600 | 1.04 | +0.000211 | +0.000009 | +0.000126 | -0.000109 | +0.000045 | False |
| `v36_s300_e900_t102` | `v36_piecewise` | 300 | 900 | 1.02 | +0.000138 | +0.000010 | +0.000101 | -0.000056 | -0.000046 | False |
| `v36_s180_e450_t102` | `v36_piecewise` | 180 | 450 | 1.02 | +0.000109 | +0.000014 | +0.000002 | -0.000010 | -0.000078 | False |
| `v36_s300_e600_t104` | `v36_piecewise` | 300 | 600 | 1.04 | +0.000227 | +0.000033 | +0.000175 | -0.000008 | +0.000101 | False |
| `v36_s180_e600_t102` | `v36_piecewise` | 180 | 600 | 1.02 | +0.000117 | +0.000038 | +0.000076 | +0.000052 | +0.000055 | False |
| `v36_s300_e900_t100` | `v36_piecewise` | 300 | 900 | 1.00 | +0.000047 | +0.000044 | +0.000054 | +0.000139 | -0.000009 | False |
| `v36_s300_e600_t102` | `v36_piecewise` | 300 | 600 | 1.02 | +0.000130 | +0.000059 | +0.000122 | +0.000139 | +0.000100 | False |
| `v36_s180_e450_t100` | `v36_piecewise` | 180 | 450 | 1.00 | +0.000029 | +0.000060 | -0.000036 | +0.000241 | +0.000003 | False |
| `v36_s180_e600_t100` | `v36_piecewise` | 180 | 600 | 1.00 | +0.000034 | +0.000080 | +0.000035 | +0.000286 | +0.000122 | False |
| `v36_s300_e600_t100` | `v36_piecewise` | 300 | 600 | 1.00 | +0.000044 | +0.000099 | +0.000079 | +0.000360 | +0.000155 | False |

## Split Metrics

| mode | split | model | Brier | logloss | ECE10 | side acc |
|---|---|---|---:|---:|---:|---:|
| `two_side_all_heartbeats` | holdout | `v36_s120_e300_t100` | 0.146895 | 0.437970 | 0.009460 | 76.95% |
| `two_side_all_heartbeats` | holdout | `v36_s120_e300_t102` | 0.146913 | 0.437782 | 0.009915 | 76.95% |
| `two_side_all_heartbeats` | holdout | `v35_h150_t102` | 0.146942 | 0.438000 | 0.010788 | 76.95% |
| `two_side_all_heartbeats` | holdout | `v36_s120_e300_t104` | 0.146943 | 0.437656 | 0.012155 | 76.95% |
| `two_side_all_heartbeats` | holdout | `v36_s180_e450_t100` | 0.146986 | 0.438034 | 0.010720 | 76.95% |
| `two_side_all_heartbeats` | holdout | `v34_h110_t098` | 0.147009 | 0.438003 | 0.010775 | 76.98% |
| `two_side_all_heartbeats` | holdout | `v36_s180_e450_t102` | 0.147011 | 0.437881 | 0.011012 | 76.95% |
| `two_side_all_heartbeats` | holdout | `v36_s180_e600_t100` | 0.147042 | 0.438077 | 0.010860 | 76.95% |
| `two_side_all_heartbeats` | holdout | `v36_s180_e450_t104` | 0.147047 | 0.437789 | 0.013213 | 76.95% |
| `two_side_all_heartbeats` | holdout | `v36_s300_e900_t100` | 0.147058 | 0.437948 | 0.011199 | 76.95% |
| `two_side_all_heartbeats` | holdout | `v36_s180_e600_t102` | 0.147070 | 0.437940 | 0.011543 | 76.95% |
| `two_side_all_heartbeats` | holdout | `v36_s300_e600_t100` | 0.147082 | 0.438096 | 0.010464 | 76.95% |
| `two_side_all_heartbeats` | holdout | `v36_s300_e900_t102` | 0.147092 | 0.437841 | 0.012165 | 76.95% |
| `two_side_all_heartbeats` | holdout | `v36_s180_e600_t104` | 0.147109 | 0.437863 | 0.013225 | 76.95% |
| `two_side_all_heartbeats` | holdout | `v36_s300_e600_t102` | 0.147112 | 0.437970 | 0.011481 | 76.95% |
| `two_side_all_heartbeats` | holdout | `v36_s300_e900_t104` | 0.147137 | 0.437794 | 0.013849 | 76.95% |
| `two_side_all_heartbeats` | holdout | `v36_s300_e600_t104` | 0.147154 | 0.437906 | 0.013217 | 76.95% |
| `two_side_all_heartbeats` | validation | `v35_h150_t102` | 0.134198 | 0.401509 | 0.009396 | 79.10% |
| `two_side_all_heartbeats` | validation | `v36_s120_e300_t104` | 0.134229 | 0.401402 | 0.008087 | 79.10% |
| `two_side_all_heartbeats` | validation | `v36_s120_e300_t102` | 0.134282 | 0.401691 | 0.009163 | 79.10% |
| `two_side_all_heartbeats` | validation | `v36_s300_e900_t104` | 0.134296 | 0.401578 | 0.010145 | 79.10% |
| `two_side_all_heartbeats` | validation | `v36_s180_e450_t104` | 0.134318 | 0.401679 | 0.008785 | 79.10% |
| `two_side_all_heartbeats` | validation | `v36_s300_e900_t102` | 0.134330 | 0.401774 | 0.010824 | 79.10% |
| `two_side_all_heartbeats` | validation | `v36_s180_e600_t104` | 0.134341 | 0.401759 | 0.009050 | 79.10% |
| `two_side_all_heartbeats` | validation | `v34_h110_t098` | 0.134346 | 0.401956 | 0.010299 | 79.10% |
| `two_side_all_heartbeats` | validation | `v36_s120_e300_t100` | 0.134348 | 0.402057 | 0.009583 | 79.10% |
| `two_side_all_heartbeats` | validation | `v36_s300_e600_t104` | 0.134355 | 0.401819 | 0.009370 | 79.10% |
| `two_side_all_heartbeats` | validation | `v36_s180_e450_t102` | 0.134364 | 0.401933 | 0.008332 | 79.10% |
| `two_side_all_heartbeats` | validation | `v36_s300_e900_t100` | 0.134378 | 0.402045 | 0.008321 | 79.10% |
| `two_side_all_heartbeats` | validation | `v36_s180_e600_t102` | 0.134384 | 0.401995 | 0.007840 | 79.10% |
| `two_side_all_heartbeats` | validation | `v36_s300_e600_t102` | 0.134395 | 0.402040 | 0.008480 | 79.10% |
| `two_side_all_heartbeats` | validation | `v36_s180_e450_t100` | 0.134424 | 0.402263 | 0.008959 | 79.10% |
| `two_side_all_heartbeats` | validation | `v36_s180_e600_t100` | 0.134440 | 0.402307 | 0.008277 | 79.10% |
| `two_side_all_heartbeats` | validation | `v36_s300_e600_t100` | 0.134448 | 0.402338 | 0.008018 | 79.10% |
| `two_side_minute_bucket` | holdout | `v35_h150_t102` | 0.150338 | 0.446168 | 0.012490 | 76.07% |
| `two_side_minute_bucket` | holdout | `v36_s120_e300_t100` | 0.150382 | 0.446074 | 0.010139 | 76.07% |
| `two_side_minute_bucket` | holdout | `v36_s120_e300_t102` | 0.150424 | 0.446031 | 0.012017 | 76.07% |
| `two_side_minute_bucket` | holdout | `v36_s180_e450_t100` | 0.150465 | 0.446254 | 0.011631 | 76.07% |
| `two_side_minute_bucket` | holdout | `v36_s120_e300_t104` | 0.150477 | 0.446044 | 0.014112 | 76.07% |
| `two_side_minute_bucket` | holdout | `v34_h110_t098` | 0.150513 | 0.446279 | 0.011302 | 76.18% |
| `two_side_minute_bucket` | holdout | `v36_s180_e450_t102` | 0.150515 | 0.446245 | 0.012293 | 76.07% |
| `two_side_minute_bucket` | holdout | `v36_s180_e600_t100` | 0.150551 | 0.446449 | 0.011238 | 76.07% |
| `two_side_minute_bucket` | holdout | `v36_s300_e900_t100` | 0.150573 | 0.446316 | 0.012337 | 76.07% |
| `two_side_minute_bucket` | holdout | `v36_s180_e450_t104` | 0.150574 | 0.446291 | 0.015008 | 76.07% |
| `two_side_minute_bucket` | holdout | `v36_s300_e600_t100` | 0.150599 | 0.446496 | 0.011432 | 76.07% |
| `two_side_minute_bucket` | holdout | `v36_s180_e600_t102` | 0.150604 | 0.446452 | 0.012723 | 76.07% |
| `two_side_minute_bucket` | holdout | `v36_s300_e900_t102` | 0.150631 | 0.446350 | 0.013481 | 76.07% |
| `two_side_minute_bucket` | holdout | `v36_s300_e600_t102` | 0.150653 | 0.446511 | 0.013124 | 76.07% |
| `two_side_minute_bucket` | holdout | `v36_s180_e600_t104` | 0.150666 | 0.446509 | 0.014991 | 76.07% |
| `two_side_minute_bucket` | holdout | `v36_s300_e900_t104` | 0.150699 | 0.446436 | 0.015695 | 76.07% |
| `two_side_minute_bucket` | holdout | `v36_s300_e600_t104` | 0.150718 | 0.446578 | 0.015238 | 76.07% |
| `two_side_minute_bucket` | validation | `v35_h150_t102` | 0.137187 | 0.409154 | 0.008921 | 78.21% |
| `two_side_minute_bucket` | validation | `v36_s120_e300_t104` | 0.137344 | 0.409327 | 0.007107 | 78.21% |
| `two_side_minute_bucket` | validation | `v36_s120_e300_t102` | 0.137368 | 0.409462 | 0.006679 | 78.21% |
| `two_side_minute_bucket` | validation | `v36_s120_e300_t100` | 0.137406 | 0.409669 | 0.010132 | 78.21% |
| `two_side_minute_bucket` | validation | `v36_s180_e450_t104` | 0.137445 | 0.409767 | 0.007517 | 78.21% |
| `two_side_minute_bucket` | validation | `v34_h110_t098` | 0.137455 | 0.409868 | 0.012260 | 78.21% |
| `two_side_minute_bucket` | validation | `v36_s180_e450_t102` | 0.137464 | 0.409870 | 0.006134 | 78.21% |
| `two_side_minute_bucket` | validation | `v36_s180_e600_t104` | 0.137476 | 0.409846 | 0.007412 | 78.21% |
| `two_side_minute_bucket` | validation | `v36_s300_e900_t104` | 0.137484 | 0.409887 | 0.007170 | 78.21% |
| `two_side_minute_bucket` | validation | `v36_s300_e900_t102` | 0.137491 | 0.409937 | 0.008675 | 78.21% |
| `two_side_minute_bucket` | validation | `v36_s180_e600_t102` | 0.137492 | 0.409932 | 0.006764 | 78.21% |
| `two_side_minute_bucket` | validation | `v36_s180_e450_t100` | 0.137495 | 0.410043 | 0.011180 | 78.21% |
| `two_side_minute_bucket` | validation | `v36_s300_e900_t100` | 0.137511 | 0.410056 | 0.011075 | 78.21% |
| `two_side_minute_bucket` | validation | `v36_s300_e600_t104` | 0.137512 | 0.409989 | 0.007511 | 78.21% |
| `two_side_minute_bucket` | validation | `v36_s180_e600_t100` | 0.137520 | 0.410088 | 0.011440 | 78.21% |
| `two_side_minute_bucket` | validation | `v36_s300_e600_t102` | 0.137524 | 0.410062 | 0.007671 | 78.21% |
| `two_side_minute_bucket` | validation | `v36_s300_e600_t100` | 0.137550 | 0.410205 | 0.011713 | 78.21% |

## Read

- Best validation row: `v35_h150_t102`.
- Candidates beating v34 on every validation/holdout Brier and logloss cell: 3.
- If no piecewise row improves train damage while preserving recent-split gains, keep v35 only as a forward-shadow candidate.
