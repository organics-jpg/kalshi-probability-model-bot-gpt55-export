# Mushroom v29 FV Surface Probe

Generated UTC: `20260504_233309Z`

## Scope

- Research-only replay of FV probability engines on resolved live heartbeat states.
- Primary metrics are probability calibration: Brier, logloss, and ECE.
- Side-choice accuracy is shown only as a sanity check; this is not an entry/exit scorer.
- Heartbeat mode: `two_side_minute_bucket`.
- Resolved side rows: 9796; resolved markets: 330; opportunities: 4898.

## Candidate Surfaces

- `v28_live_surface`: current v28 FV surface: Brownian anchor plus symmetric transport, close-to-close horizon.
- `v28_avg60`: v28 with final-minute settlement-average horizon adjustment.
- `v28_avg30`: v28 settlement-average sensitivity with a 30-second averaging window.
- `v28_avg45`: v28 settlement-average sensitivity with a 45-second averaging window.
- `v28_avg75`: v28 settlement-average sensitivity with a 75-second averaging window.
- `v28_avg90`: v28 settlement-average sensitivity with a 90-second averaging window.
- `v30_avg60_exact_var`: v30 exact Brownian variance inside a 60-second settlement-average window.
- `v30_avg75_exact_var`: v30 exact Brownian variance inside a 75-second settlement-average window.
- `v30_avg90_exact_var`: v30 exact Brownian variance inside a 90-second settlement-average window.
- `v31_avg90_final60_exact`: v31 proxy-aware surface: 90s effective settlement horizon, exact average collapse in final 60s.
- `v32_avg110_final60_exact`: v32 proxy-aware surface: 110s effective settlement/proxy horizon, exact average collapse in final 60s.
- `v33_antipersist3`: v33: v32 plus a small time-damped 3m anti-persistence Brownian anchor.
- `v34_material_antipersist3`: v34: v32 plus materiality-gated 3m anti-persistence.
- `v35_h150_t102_antipersist3`: v35: v34 path prior with 150s proxy horizon and softer 1.02 posterior temperature.
- `v36_piecewise_h150_t102_antipersist3`: v36: v34 near expiry, smooth 120-300s blend to v35 proxy horizon, 1.02 temperature.
- `v37_piecewise_dynamic_temp_antipersist3`: v37: v36 proxy blend plus dynamic 0.98-to-1.02 posterior temperature.
- `v38_long60_antipersist`: v38: v37 plus a gated 60m long-memory anti-persistence anchor.
- `v39_midband_v28_fallback`: v39: v38 except live-v28 FV fallback in the 420-600s mid-market band.
- `v28_avg60_temp104`: settlement-average horizon plus softer probability temperature.
- `v29_signed_small`: v29 final-average physics with a very small gated signed-transport term.
- `v29_signed_default`: v29 final-average physics with small gated signed transport and volshock temperature shrinkage.
- `v29_signed_more`: v29 sensitivity with larger signed-regime transport.
- `v29_no_signed_temp112`: final-average horizon with stronger global overconfidence shrinkage and no signed transport.

## Probability Metrics

| model | split | Brier | logloss | ECE10 | side acc | high-p rows | high-p pred/realized | high-p overconf |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `v39_midband_v28_fallback` | all | 0.14878 | 0.44333 | 0.01688 | 76.81% | 2103 | 94.58%/94.91% | -0.34% |
| `v38_long60_antipersist` | all | 0.14880 | 0.44346 | 0.01528 | 76.77% | 2145 | 94.49%/94.50% | -0.01% |
| `v37_piecewise_dynamic_temp_antipersist3` | all | 0.14883 | 0.44354 | 0.01548 | 76.77% | 2147 | 94.48%/94.50% | -0.02% |
| `v36_piecewise_h150_t102_antipersist3` | all | 0.14888 | 0.44371 | 0.01420 | 76.77% | 2143 | 94.42%/94.49% | -0.08% |
| `v34_material_antipersist3` | all | 0.14891 | 0.44395 | 0.01503 | 76.77% | 2143 | 94.45%/94.54% | -0.09% |
| `v35_h150_t102_antipersist3` | all | 0.14903 | 0.44452 | 0.01462 | 76.77% | 2148 | 94.43%/94.37% | 0.06% |
| `v33_antipersist3` | all | 0.14915 | 0.44470 | 0.01540 | 76.70% | 2140 | 94.46%/94.58% | -0.12% |
| `v32_avg110_final60_exact` | all | 0.14935 | 0.44528 | 0.01433 | 76.75% | 2152 | 94.34%/94.33% | 0.01% |
| `v31_avg90_final60_exact` | all | 0.14940 | 0.44515 | 0.01609 | 76.75% | 2123 | 94.29%/94.68% | -0.39% |
| `v30_avg90_exact_var` | all | 0.14940 | 0.44516 | 0.01609 | 76.75% | 2123 | 94.29%/94.68% | -0.39% |
| `v30_avg75_exact_var` | all | 0.14954 | 0.44564 | 0.01731 | 76.75% | 2089 | 94.22%/94.88% | -0.66% |
| `v28_avg90` | all | 0.14958 | 0.44636 | 0.01642 | 76.75% | 2107 | 94.03%/94.73% | -0.70% |
| `v30_avg60_exact_var` | all | 0.14974 | 0.44647 | 0.01694 | 76.75% | 2065 | 94.05%/94.96% | -0.91% |
| `v28_avg75` | all | 0.14979 | 0.44719 | 0.01737 | 76.75% | 2070 | 93.96%/94.93% | -0.96% |
| `v28_avg45` | all | 0.14998 | 0.44755 | 0.01876 | 76.77% | 2040 | 93.86%/94.95% | -1.09% |
| `v29_signed_more` | all | 0.15001 | 0.44743 | 0.02230 | 76.75% | 2002 | 93.69%/95.30% | -1.62% |
| `v29_signed_default` | all | 0.15001 | 0.44745 | 0.02252 | 76.75% | 1999 | 93.69%/95.30% | -1.61% |
| `v29_signed_small` | all | 0.15002 | 0.44747 | 0.02272 | 76.75% | 1997 | 93.69%/95.34% | -1.66% |
| `v28_avg60` | all | 0.15006 | 0.44830 | 0.01812 | 76.75% | 2043 | 93.82%/95.01% | -1.19% |
| `v28_avg30` | all | 0.15026 | 0.44878 | 0.02048 | 76.77% | 2004 | 93.76%/95.16% | -1.39% |
| `v29_no_signed_temp112` | all | 0.15062 | 0.44942 | 0.03098 | 76.75% | 1926 | 93.25%/95.79% | -2.54% |
| `v28_avg60_temp104` | all | 0.15067 | 0.45013 | 0.02739 | 76.75% | 1943 | 93.40%/95.42% | -2.02% |
| `v28_live_surface` | all | 0.15082 | 0.45104 | 0.02495 | 76.77% | 1957 | 93.47%/95.25% | -1.78% |
| `v39_midband_v28_fallback` | holdout | 0.15021 | 0.44525 | 0.01386 | 76.28% | 409 | 94.97%/94.62% | 0.35% |
| `v38_long60_antipersist` | holdout | 0.15030 | 0.44562 | 0.01164 | 76.07% | 414 | 94.93%/94.44% | 0.49% |
| `v35_h150_t102_antipersist3` | holdout | 0.15034 | 0.44617 | 0.01249 | 76.07% | 416 | 94.79%/94.71% | 0.08% |
| `v37_piecewise_dynamic_temp_antipersist3` | holdout | 0.15039 | 0.44582 | 0.01151 | 76.07% | 415 | 94.90%/94.46% | 0.44% |
| `v36_piecewise_h150_t102_antipersist3` | holdout | 0.15042 | 0.44603 | 0.01202 | 76.07% | 414 | 94.84%/94.44% | 0.40% |
| `v33_antipersist3` | holdout | 0.15049 | 0.44655 | 0.01316 | 75.97% | 415 | 94.88%/94.22% | 0.66% |
| `v34_material_antipersist3` | holdout | 0.15051 | 0.44628 | 0.01130 | 76.18% | 414 | 94.88%/94.44% | 0.44% |
| `v32_avg110_final60_exact` | holdout | 0.15062 | 0.44680 | 0.01259 | 76.58% | 417 | 94.75%/94.24% | 0.50% |
| `v30_avg90_exact_var` | holdout | 0.15085 | 0.44765 | 0.01604 | 76.58% | 410 | 94.78%/94.39% | 0.39% |
| `v31_avg90_final60_exact` | holdout | 0.15085 | 0.44765 | 0.01604 | 76.58% | 410 | 94.78%/94.39% | 0.39% |
| `v30_avg75_exact_var` | holdout | 0.15105 | 0.44831 | 0.01784 | 76.58% | 403 | 94.74%/94.79% | -0.05% |
| `v30_avg60_exact_var` | holdout | 0.15132 | 0.44937 | 0.01774 | 76.58% | 399 | 94.56%/95.24% | -0.67% |
| `v28_avg90` | holdout | 0.15148 | 0.45033 | 0.01779 | 76.58% | 407 | 94.48%/94.35% | 0.13% |
| `v28_avg45` | holdout | 0.15165 | 0.45072 | 0.02084 | 76.69% | 394 | 94.37%/95.18% | -0.80% |
| `v28_avg75` | holdout | 0.15168 | 0.45102 | 0.01966 | 76.58% | 399 | 94.46%/94.74% | -0.27% |
| `v29_signed_more` | holdout | 0.15178 | 0.45093 | 0.02684 | 76.58% | 384 | 94.29%/95.31% | -1.03% |
| `v29_signed_default` | holdout | 0.15180 | 0.45097 | 0.02697 | 76.58% | 384 | 94.28%/95.31% | -1.03% |
| `v29_signed_small` | holdout | 0.15181 | 0.45100 | 0.02709 | 76.58% | 384 | 94.27%/95.31% | -1.04% |
| `v28_avg60` | holdout | 0.15196 | 0.45206 | 0.01963 | 76.58% | 393 | 94.37%/95.17% | -0.80% |
| `v28_avg30` | holdout | 0.15200 | 0.45206 | 0.02290 | 76.69% | 384 | 94.41%/95.05% | -0.65% |
| `v29_no_signed_temp112` | holdout | 0.15235 | 0.45259 | 0.03100 | 76.58% | 368 | 94.05%/95.65% | -1.60% |
| `v28_avg60_temp104` | holdout | 0.15248 | 0.45337 | 0.02860 | 76.58% | 374 | 94.08%/95.45% | -1.38% |
| `v28_live_surface` | holdout | 0.15262 | 0.45433 | 0.02731 | 76.69% | 374 | 94.21%/95.45% | -1.25% |
| `v39_midband_v28_fallback` | validation | 0.13713 | 0.40892 | 0.01192 | 78.21% | 481 | 95.50%/95.84% | -0.34% |
| `v35_h150_t102_antipersist3` | validation | 0.13719 | 0.40915 | 0.00892 | 78.21% | 496 | 95.20%/95.16% | 0.04% |
| `v38_long60_antipersist` | validation | 0.13732 | 0.40915 | 0.01094 | 78.21% | 494 | 95.30%/95.14% | 0.16% |
| `v37_piecewise_dynamic_temp_antipersist3` | validation | 0.13734 | 0.40922 | 0.00891 | 78.21% | 494 | 95.31%/95.14% | 0.17% |
| `v36_piecewise_h150_t102_antipersist3` | validation | 0.13737 | 0.40946 | 0.00668 | 78.21% | 494 | 95.25%/95.14% | 0.11% |
| `v34_material_antipersist3` | validation | 0.13745 | 0.40987 | 0.01226 | 78.21% | 493 | 95.31%/95.13% | 0.18% |
| `v33_antipersist3` | validation | 0.13869 | 0.41333 | 0.01670 | 77.80% | 494 | 95.25%/94.94% | 0.32% |
| `v30_avg90_exact_var` | validation | 0.13950 | 0.41598 | 0.01596 | 77.60% | 500 | 94.83%/94.60% | 0.23% |
| `v31_avg90_final60_exact` | validation | 0.13950 | 0.41598 | 0.01596 | 77.60% | 500 | 94.83%/94.60% | 0.23% |
| `v32_avg110_final60_exact` | validation | 0.13956 | 0.41593 | 0.01358 | 77.60% | 500 | 95.07%/94.40% | 0.67% |
| `v30_avg75_exact_var` | validation | 0.13957 | 0.41644 | 0.01170 | 77.60% | 495 | 94.75%/94.75% | -0.00% |
| `v30_avg60_exact_var` | validation | 0.13972 | 0.41722 | 0.01093 | 77.60% | 488 | 94.71%/94.88% | -0.16% |
| `v28_avg90` | validation | 0.13986 | 0.41761 | 0.01503 | 77.60% | 498 | 94.69%/94.58% | 0.11% |
| `v29_signed_small` | validation | 0.13989 | 0.41768 | 0.01650 | 77.60% | 471 | 94.48%/95.54% | -1.06% |
| `v28_avg45` | validation | 0.13990 | 0.41818 | 0.00981 | 77.60% | 482 | 94.64%/94.81% | -0.17% |
| `v29_signed_default` | validation | 0.13991 | 0.41773 | 0.01627 | 77.60% | 472 | 94.47%/95.34% | -0.87% |
| `v29_signed_more` | validation | 0.13993 | 0.41779 | 0.01502 | 77.60% | 472 | 94.49%/95.34% | -0.85% |
| `v28_avg75` | validation | 0.13994 | 0.41812 | 0.01155 | 77.60% | 493 | 94.59%/94.73% | -0.14% |
| `v29_no_signed_temp112` | validation | 0.14009 | 0.41863 | 0.02123 | 77.60% | 458 | 94.02%/96.29% | -2.26% |
| `v28_avg60` | validation | 0.14009 | 0.41893 | 0.01026 | 77.60% | 485 | 94.58%/94.85% | -0.27% |
| `v28_avg30` | validation | 0.14010 | 0.41921 | 0.01481 | 77.60% | 476 | 94.55%/95.38% | -0.82% |
| `v28_avg60_temp104` | validation | 0.14021 | 0.41940 | 0.01828 | 77.60% | 462 | 94.27%/95.67% | -1.40% |
| `v28_live_surface` | validation | 0.14048 | 0.42101 | 0.01712 | 77.60% | 468 | 94.32%/95.51% | -1.19% |

## Deltas vs v28

| model | all Brier delta | holdout Brier delta | all logloss delta | holdout logloss delta |
|---|---:|---:|---:|---:|
| `v39_midband_v28_fallback` | -0.00204 | -0.00240 | -0.00771 | -0.00908 |
| `v38_long60_antipersist` | -0.00202 | -0.00232 | -0.00758 | -0.00870 |
| `v37_piecewise_dynamic_temp_antipersist3` | -0.00198 | -0.00223 | -0.00750 | -0.00851 |
| `v36_piecewise_h150_t102_antipersist3` | -0.00194 | -0.00219 | -0.00732 | -0.00829 |
| `v34_material_antipersist3` | -0.00190 | -0.00210 | -0.00709 | -0.00805 |
| `v35_h150_t102_antipersist3` | -0.00179 | -0.00228 | -0.00651 | -0.00816 |
| `v33_antipersist3` | -0.00167 | -0.00213 | -0.00634 | -0.00778 |
| `v32_avg110_final60_exact` | -0.00147 | -0.00200 | -0.00576 | -0.00752 |
| `v31_avg90_final60_exact` | -0.00142 | -0.00176 | -0.00589 | -0.00667 |
| `v30_avg90_exact_var` | -0.00141 | -0.00176 | -0.00588 | -0.00667 |
| `v30_avg75_exact_var` | -0.00128 | -0.00157 | -0.00539 | -0.00602 |
| `v28_avg90` | -0.00124 | -0.00114 | -0.00468 | -0.00399 |
| `v30_avg60_exact_var` | -0.00108 | -0.00130 | -0.00457 | -0.00496 |
| `v28_avg75` | -0.00102 | -0.00094 | -0.00385 | -0.00331 |
| `v28_avg45` | -0.00084 | -0.00096 | -0.00348 | -0.00360 |
| `v29_signed_more` | -0.00081 | -0.00084 | -0.00361 | -0.00340 |
| `v29_signed_default` | -0.00080 | -0.00082 | -0.00359 | -0.00336 |
| `v29_signed_small` | -0.00080 | -0.00081 | -0.00357 | -0.00332 |
| `v28_avg60` | -0.00075 | -0.00066 | -0.00274 | -0.00227 |
| `v28_avg30` | -0.00056 | -0.00062 | -0.00226 | -0.00227 |
| `v29_no_signed_temp112` | -0.00020 | -0.00027 | -0.00162 | -0.00174 |
| `v28_avg60_temp104` | -0.00014 | -0.00014 | -0.00091 | -0.00096 |
| `v28_live_surface` | +0.00000 | +0.00000 | +0.00000 | +0.00000 |

## Calibration Bins

Holdout bins for the baseline and best holdout-Brier model:

| model | bin | rows | mean pred | realized | error |
|---|---|---:|---:|---:|---:|
| `v28_live_surface` | [0.500,0.550] | 177 | 52.56% | 54.24% | -1.68% |
| `v28_live_surface` | [0.550,0.600] | 134 | 57.44% | 64.18% | -6.74% |
| `v28_live_surface` | [0.600,0.650] | 81 | 62.36% | 59.26% | 3.10% |
| `v28_live_surface` | [0.650,0.700] | 82 | 67.37% | 70.73% | -3.36% |
| `v28_live_surface` | [0.700,0.750] | 59 | 72.40% | 83.05% | -10.65% |
| `v28_live_surface` | [0.750,0.800] | 71 | 77.50% | 78.87% | -1.38% |
| `v28_live_surface` | [0.800,0.850] | 50 | 82.75% | 90.00% | -7.25% |
| `v28_live_surface` | [0.850,0.900] | 42 | 87.34% | 92.86% | -5.51% |
| `v28_live_surface` | [0.900,0.950] | 60 | 92.39% | 90.00% | 2.39% |
| `v28_live_surface` | [0.950,0.975] | 59 | 96.34% | 96.61% | -0.27% |
| `v28_live_surface` | [0.975,1.000] | 163 | 99.38% | 99.39% | -0.00% |
| `v39_midband_v28_fallback` | [0.500,0.550] | 179 | 52.52% | 53.07% | -0.55% |
| `v39_midband_v28_fallback` | [0.550,0.600] | 126 | 57.23% | 57.14% | 0.09% |
| `v39_midband_v28_fallback` | [0.600,0.650] | 84 | 62.53% | 65.48% | -2.94% |
| `v39_midband_v28_fallback` | [0.650,0.700] | 72 | 67.24% | 76.39% | -9.15% |
| `v39_midband_v28_fallback` | [0.700,0.750] | 42 | 72.46% | 69.05% | 3.42% |
| `v39_midband_v28_fallback` | [0.750,0.800] | 66 | 77.31% | 80.30% | -2.99% |
| `v39_midband_v28_fallback` | [0.800,0.850] | 49 | 82.90% | 81.63% | 1.26% |
| `v39_midband_v28_fallback` | [0.850,0.900] | 44 | 87.63% | 90.91% | -3.28% |
| `v39_midband_v28_fallback` | [0.900,0.950] | 56 | 92.57% | 91.07% | 1.50% |
| `v39_midband_v28_fallback` | [0.950,0.975] | 44 | 96.38% | 93.18% | 3.20% |
| `v39_midband_v28_fallback` | [0.975,1.000] | 216 | 99.54% | 99.54% | 0.00% |

## Read

- Best holdout Brier: `v39_midband_v28_fallback` at 0.15021.
- Best holdout logloss: `v39_midband_v28_fallback` at 0.44525.
- Holdout Brier improvement versus v28 baseline: -0.00240.
- A model change is only useful if it improves calibration without depending on a post-hoc trade filter; this report keeps those separate.
