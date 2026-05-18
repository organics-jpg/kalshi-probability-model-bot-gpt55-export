# Mushroom v29 FV Surface Probe

Generated UTC: `20260505_054141Z`

## Scope

- Research-only replay of FV probability engines on resolved live heartbeat states.
- Primary metrics are probability calibration: Brier, logloss, and ECE.
- Side-choice accuracy is shown only as a sanity check; this is not an entry/exit scorer.
- Heartbeat mode: `two_side_all_heartbeats`.
- Resolved side rows: 42890; resolved markets: 372; opportunities: 21445.

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
| `v38_long60_antipersist` | all | 0.14288 | 0.43156 | 0.01872 | 78.27% | 9867 | 94.63%/94.62% | 0.01% |
| `v39_midband_v28_fallback` | all | 0.14290 | 0.43152 | 0.02151 | 78.32% | 9670 | 94.71%/94.91% | -0.21% |
| `v37_piecewise_dynamic_temp_antipersist3` | all | 0.14290 | 0.43161 | 0.01860 | 78.26% | 9873 | 94.63%/94.61% | 0.01% |
| `v34_material_antipersist3` | all | 0.14294 | 0.43184 | 0.01884 | 78.27% | 9838 | 94.63%/94.66% | -0.03% |
| `v36_piecewise_h150_t102_antipersist3` | all | 0.14296 | 0.43168 | 0.01876 | 78.26% | 9849 | 94.56%/94.63% | -0.06% |
| `v35_h150_t102_antipersist3` | all | 0.14299 | 0.43255 | 0.01903 | 78.26% | 9879 | 94.58%/94.56% | 0.01% |
| `v33_antipersist3` | all | 0.14310 | 0.43245 | 0.01742 | 78.12% | 9836 | 94.61%/94.63% | -0.02% |
| `v30_avg90_exact_var` | all | 0.14317 | 0.43237 | 0.01859 | 78.20% | 9799 | 94.57%/94.67% | -0.10% |
| `v32_avg110_final60_exact` | all | 0.14324 | 0.43273 | 0.01759 | 78.17% | 9872 | 94.52%/94.48% | 0.04% |
| `v28_avg90` | all | 0.14326 | 0.43021 | 0.01891 | 78.20% | 9689 | 94.32%/94.81% | -0.49% |
| `v31_avg90_final60_exact` | all | 0.14331 | 0.43249 | 0.01940 | 78.20% | 9743 | 94.46%/94.71% | -0.25% |
| `v30_avg75_exact_var` | all | 0.14331 | 0.43232 | 0.02037 | 78.21% | 9663 | 94.47%/94.91% | -0.44% |
| `v28_avg75` | all | 0.14337 | 0.43055 | 0.02048 | 78.21% | 9586 | 94.26%/95.00% | -0.74% |
| `v30_avg60_exact_var` | all | 0.14349 | 0.43250 | 0.02166 | 78.23% | 9543 | 94.34%/95.01% | -0.67% |
| `v28_avg60` | all | 0.14353 | 0.43121 | 0.02177 | 78.23% | 9485 | 94.18%/95.09% | -0.91% |
| `v28_avg45` | all | 0.14368 | 0.43153 | 0.02322 | 78.23% | 9384 | 94.10%/95.22% | -1.12% |
| `v29_signed_more` | all | 0.14376 | 0.43136 | 0.02634 | 78.19% | 9230 | 94.00%/95.42% | -1.42% |
| `v29_signed_default` | all | 0.14376 | 0.43138 | 0.02660 | 78.20% | 9210 | 94.01%/95.46% | -1.45% |
| `v29_signed_small` | all | 0.14377 | 0.43140 | 0.02684 | 78.20% | 9195 | 94.02%/95.49% | -1.47% |
| `v28_avg30` | all | 0.14389 | 0.43222 | 0.02497 | 78.24% | 9255 | 94.04%/95.38% | -1.34% |
| `v28_avg60_temp104` | all | 0.14418 | 0.43301 | 0.03064 | 78.23% | 9016 | 93.86%/95.70% | -1.84% |
| `v28_live_surface` | all | 0.14442 | 0.43427 | 0.02967 | 78.24% | 9021 | 93.77%/95.62% | -1.85% |
| `v29_no_signed_temp112` | all | 0.14443 | 0.43345 | 0.03508 | 78.20% | 8869 | 93.64%/95.97% | -2.34% |
| `v38_long60_antipersist` | holdout | 0.14318 | 0.43031 | 0.03227 | 78.80% | 1847 | 94.97%/95.13% | -0.16% |
| `v39_midband_v28_fallback` | holdout | 0.14325 | 0.43027 | 0.03561 | 78.89% | 1813 | 95.07%/95.26% | -0.18% |
| `v37_piecewise_dynamic_temp_antipersist3` | holdout | 0.14337 | 0.43071 | 0.03078 | 78.66% | 1848 | 94.96%/95.08% | -0.12% |
| `v34_material_antipersist3` | holdout | 0.14342 | 0.43084 | 0.03168 | 78.71% | 1835 | 95.03%/95.10% | -0.07% |
| `v36_piecewise_h150_t102_antipersist3` | holdout | 0.14343 | 0.43093 | 0.03089 | 78.66% | 1844 | 94.89%/95.12% | -0.23% |
| `v35_h150_t102_antipersist3` | holdout | 0.14347 | 0.43119 | 0.03114 | 78.66% | 1858 | 94.85%/95.16% | -0.31% |
| `v33_antipersist3` | holdout | 0.14348 | 0.43109 | 0.02491 | 78.08% | 1839 | 95.02%/95.00% | 0.02% |
| `v30_avg90_exact_var` | holdout | 0.14365 | 0.43163 | 0.02835 | 78.34% | 1839 | 94.93%/95.05% | -0.12% |
| `v32_avg110_final60_exact` | holdout | 0.14368 | 0.43132 | 0.02611 | 78.27% | 1845 | 94.89%/94.96% | -0.07% |
| `v31_avg90_final60_exact` | holdout | 0.14388 | 0.43187 | 0.02877 | 78.34% | 1822 | 94.84%/95.17% | -0.33% |
| `v30_avg75_exact_var` | holdout | 0.14392 | 0.43217 | 0.03015 | 78.36% | 1812 | 94.84%/95.36% | -0.53% |
| `v28_avg90` | holdout | 0.14421 | 0.43356 | 0.02991 | 78.34% | 1808 | 94.66%/95.19% | -0.53% |
| `v30_avg60_exact_var` | holdout | 0.14422 | 0.43300 | 0.03185 | 78.38% | 1786 | 94.73%/95.46% | -0.74% |
| `v28_avg75` | holdout | 0.14438 | 0.43407 | 0.03157 | 78.36% | 1789 | 94.61%/95.42% | -0.81% |
| `v28_avg60` | holdout | 0.14460 | 0.43485 | 0.03321 | 78.38% | 1771 | 94.52%/95.48% | -0.96% |
| `v28_avg45` | holdout | 0.14478 | 0.43529 | 0.03489 | 78.38% | 1756 | 94.42%/95.73% | -1.31% |
| `v29_signed_more` | holdout | 0.14489 | 0.43522 | 0.03765 | 78.31% | 1737 | 94.25%/95.68% | -1.43% |
| `v29_signed_default` | holdout | 0.14491 | 0.43529 | 0.03806 | 78.34% | 1733 | 94.27%/95.73% | -1.46% |
| `v29_signed_small` | holdout | 0.14492 | 0.43534 | 0.03817 | 78.34% | 1731 | 94.28%/95.73% | -1.44% |
| `v28_avg30` | holdout | 0.14504 | 0.43604 | 0.03698 | 78.38% | 1733 | 94.36%/95.90% | -1.55% |
| `v28_avg60_temp104` | holdout | 0.14551 | 0.43730 | 0.04181 | 78.38% | 1695 | 94.14%/96.22% | -2.08% |
| `v29_no_signed_temp112` | holdout | 0.14579 | 0.43791 | 0.04563 | 78.34% | 1662 | 93.99%/96.57% | -2.58% |
| `v28_live_surface` | holdout | 0.14581 | 0.43882 | 0.04126 | 78.41% | 1688 | 94.09%/96.33% | -2.24% |
| `v39_midband_v28_fallback` | validation | 0.12932 | 0.38747 | 0.01249 | 79.86% | 2220 | 95.04%/95.99% | -0.95% |
| `v35_h150_t102_antipersist3` | validation | 0.12933 | 0.38752 | 0.01053 | 79.86% | 2272 | 94.89%/95.64% | -0.75% |
| `v37_piecewise_dynamic_temp_antipersist3` | validation | 0.12937 | 0.38747 | 0.01028 | 79.86% | 2275 | 94.90%/95.60% | -0.70% |
| `v34_material_antipersist3` | validation | 0.12941 | 0.38772 | 0.00961 | 79.88% | 2268 | 94.91%/95.68% | -0.77% |
| `v36_piecewise_h150_t102_antipersist3` | validation | 0.12942 | 0.38777 | 0.00998 | 79.86% | 2271 | 94.86%/95.60% | -0.74% |
| `v38_long60_antipersist` | validation | 0.12950 | 0.38774 | 0.00923 | 79.77% | 2273 | 94.91%/95.60% | -0.69% |
| `v33_antipersist3` | validation | 0.12980 | 0.38884 | 0.00828 | 79.91% | 2280 | 94.83%/95.48% | -0.66% |
| `v32_avg110_final60_exact` | validation | 0.13007 | 0.38994 | 0.00898 | 80.14% | 2304 | 94.64%/95.01% | -0.36% |
| `v31_avg90_final60_exact` | validation | 0.13011 | 0.39014 | 0.01089 | 80.16% | 2276 | 94.60%/95.12% | -0.53% |
| `v30_avg90_exact_var` | validation | 0.13015 | 0.38975 | 0.01144 | 80.16% | 2283 | 94.67%/95.09% | -0.42% |
| `v30_avg75_exact_var` | validation | 0.13021 | 0.39029 | 0.01149 | 80.19% | 2252 | 94.63%/95.38% | -0.75% |
| `v30_avg60_exact_var` | validation | 0.13033 | 0.39107 | 0.01195 | 80.19% | 2231 | 94.52%/95.38% | -0.86% |
| `v28_avg90` | validation | 0.13039 | 0.39129 | 0.01028 | 80.16% | 2269 | 94.52%/95.11% | -0.59% |
| `v28_avg75` | validation | 0.13047 | 0.39167 | 0.01173 | 80.19% | 2246 | 94.48%/95.37% | -0.89% |
| `v28_avg60` | validation | 0.13061 | 0.39227 | 0.01254 | 80.19% | 2224 | 94.43%/95.37% | -0.94% |
| `v29_signed_small` | validation | 0.13066 | 0.39274 | 0.01711 | 80.16% | 2132 | 94.39%/95.87% | -1.48% |
| `v29_signed_default` | validation | 0.13068 | 0.39277 | 0.01688 | 80.16% | 2133 | 94.39%/95.83% | -1.43% |
| `v28_avg45` | validation | 0.13068 | 0.39274 | 0.01255 | 80.21% | 2199 | 94.39%/95.45% | -1.06% |
| `v29_signed_more` | validation | 0.13069 | 0.39281 | 0.01627 | 80.16% | 2135 | 94.39%/95.78% | -1.39% |
| `v28_avg30` | validation | 0.13082 | 0.39347 | 0.01357 | 80.23% | 2165 | 94.40%/95.66% | -1.26% |
| `v28_avg60_temp104` | validation | 0.13093 | 0.39381 | 0.02061 | 80.19% | 2098 | 94.29%/96.04% | -1.76% |
| `v29_no_signed_temp112` | validation | 0.13108 | 0.39465 | 0.02823 | 80.16% | 2062 | 94.03%/96.65% | -2.62% |
| `v28_live_surface` | validation | 0.13124 | 0.39555 | 0.01769 | 80.23% | 2114 | 94.25%/95.88% | -1.64% |

## Deltas vs v28

| model | all Brier delta | holdout Brier delta | all logloss delta | holdout logloss delta |
|---|---:|---:|---:|---:|
| `v38_long60_antipersist` | -0.00155 | -0.00263 | -0.00271 | -0.00850 |
| `v39_midband_v28_fallback` | -0.00153 | -0.00256 | -0.00276 | -0.00854 |
| `v37_piecewise_dynamic_temp_antipersist3` | -0.00153 | -0.00245 | -0.00266 | -0.00810 |
| `v34_material_antipersist3` | -0.00148 | -0.00239 | -0.00243 | -0.00797 |
| `v36_piecewise_h150_t102_antipersist3` | -0.00147 | -0.00239 | -0.00260 | -0.00789 |
| `v35_h150_t102_antipersist3` | -0.00143 | -0.00235 | -0.00172 | -0.00762 |
| `v33_antipersist3` | -0.00132 | -0.00233 | -0.00182 | -0.00773 |
| `v30_avg90_exact_var` | -0.00125 | -0.00216 | -0.00190 | -0.00718 |
| `v32_avg110_final60_exact` | -0.00118 | -0.00213 | -0.00155 | -0.00749 |
| `v28_avg90` | -0.00117 | -0.00160 | -0.00407 | -0.00526 |
| `v31_avg90_final60_exact` | -0.00112 | -0.00193 | -0.00178 | -0.00694 |
| `v30_avg75_exact_var` | -0.00111 | -0.00190 | -0.00195 | -0.00665 |
| `v28_avg75` | -0.00106 | -0.00143 | -0.00373 | -0.00475 |
| `v30_avg60_exact_var` | -0.00093 | -0.00159 | -0.00177 | -0.00582 |
| `v28_avg60` | -0.00090 | -0.00121 | -0.00306 | -0.00397 |
| `v28_avg45` | -0.00075 | -0.00103 | -0.00274 | -0.00353 |
| `v29_signed_more` | -0.00067 | -0.00093 | -0.00291 | -0.00359 |
| `v29_signed_default` | -0.00066 | -0.00091 | -0.00289 | -0.00353 |
| `v29_signed_small` | -0.00065 | -0.00089 | -0.00287 | -0.00347 |
| `v28_avg30` | -0.00054 | -0.00078 | -0.00205 | -0.00278 |
| `v28_avg60_temp104` | -0.00024 | -0.00031 | -0.00127 | -0.00152 |
| `v28_live_surface` | +0.00000 | +0.00000 | +0.00000 | +0.00000 |
| `v29_no_signed_temp112` | +0.00001 | -0.00002 | -0.00083 | -0.00091 |

## Calibration Bins

Holdout bins for the baseline and best holdout-Brier model:

| model | bin | rows | mean pred | realized | error |
|---|---|---:|---:|---:|---:|
| `v28_live_surface` | [0.500,0.550] | 772 | 52.41% | 52.46% | -0.05% |
| `v28_live_surface` | [0.550,0.600] | 549 | 57.24% | 69.22% | -11.97% |
| `v28_live_surface` | [0.600,0.650] | 422 | 62.28% | 70.14% | -7.87% |
| `v28_live_surface` | [0.650,0.700] | 328 | 67.22% | 71.34% | -4.12% |
| `v28_live_surface` | [0.700,0.750] | 322 | 72.67% | 80.43% | -7.76% |
| `v28_live_surface` | [0.750,0.800] | 226 | 77.49% | 78.32% | -0.83% |
| `v28_live_surface` | [0.800,0.850] | 182 | 82.55% | 90.66% | -8.11% |
| `v28_live_surface` | [0.850,0.900] | 250 | 87.54% | 96.80% | -9.26% |
| `v28_live_surface` | [0.900,0.950] | 321 | 92.95% | 92.83% | 0.11% |
| `v28_live_surface` | [0.950,0.975] | 269 | 96.35% | 96.28% | 0.07% |
| `v28_live_surface` | [0.975,1.000] | 666 | 99.33% | 99.40% | -0.07% |
| `v38_long60_antipersist` | [0.500,0.550] | 763 | 52.54% | 55.70% | -3.16% |
| `v38_long60_antipersist` | [0.550,0.600] | 521 | 57.39% | 63.53% | -6.14% |
| `v38_long60_antipersist` | [0.600,0.650] | 380 | 62.39% | 68.68% | -6.29% |
| `v38_long60_antipersist` | [0.650,0.700] | 292 | 67.37% | 73.29% | -5.92% |
| `v38_long60_antipersist` | [0.700,0.750] | 248 | 72.71% | 80.65% | -7.94% |
| `v38_long60_antipersist` | [0.750,0.800] | 256 | 77.34% | 80.47% | -3.13% |
| `v38_long60_antipersist` | [0.800,0.850] | 185 | 82.48% | 83.78% | -1.31% |
| `v38_long60_antipersist` | [0.850,0.900] | 194 | 87.59% | 90.72% | -3.13% |
| `v38_long60_antipersist` | [0.900,0.950] | 306 | 92.71% | 92.48% | 0.22% |
| `v38_long60_antipersist` | [0.950,0.975] | 267 | 96.40% | 95.13% | 1.27% |
| `v38_long60_antipersist` | [0.975,1.000] | 895 | 99.49% | 99.33% | 0.16% |

## Read

- Best holdout Brier: `v38_long60_antipersist` at 0.14318.
- Best holdout logloss: `v39_midband_v28_fallback` at 0.43027.
- Holdout Brier improvement versus v28 baseline: -0.00263.
- A model change is only useful if it improves calibration without depending on a post-hoc trade filter; this report keeps those separate.
