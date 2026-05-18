# Current v28 Prior Failure Modes

Generated UTC: `20260502_152508Z`

## Scope

- Research-only analysis; no bot files or running processes are touched.
- Compares current v28 filled entries, current v28 first websocket opportunities, and the supplemental live_90_70 replay.
- Focus is falsification of physical priors: v28 probability, edge, boundary cushion, realized-vol cushion, and adverse drift.

## `current_v28_live_fills`

- Rows: 127
- Contracts: 251
- Baseline: 202/251 contracts = 80.48%; 102/127 trades = 80.31%

### Prior Checks

| prior | contracts | contract acc | contract ret | trades | trade acc |
|---|---:|---:|---:|---:|---:|
| `v28 p_side>=0.85 and ask<=90` | 202/251 | 80.48% | 100.00% | 102/127 | 80.31% |
| `v28 edge>=2c and ask<=90` | 202/251 | 80.48% | 100.00% | 102/127 | 80.31% |
| `margin/v28_sigma>=0.5` | 184/223 | 82.51% | 88.84% | 93/113 | 82.30% |
| `margin/v28_sigma>=1.0` | 74/88 | 84.09% | 35.06% | 37/44 | 84.09% |
| `margin/rv15>=0.5` | 174/207 | 84.06% | 82.47% | 88/105 | 83.81% |
| `Brownian rv15 p>=0.70` | 170/201 | 84.58% | 80.08% | 86/102 | 84.31% |
| `projected_margin_3m>=50` | 178/213 | 83.57% | 84.86% | 90/108 | 83.33% |
| `adverse15<10 or v28 cushion>0.5` | 196/243 | 80.66% | 96.81% | 99/123 | 80.49% |

### Strongest Single-Feature Separators

| feature | winner median [IQR] | loser median [IQR] | direction | separation |
|---|---:|---:|---|---:|
| Margin / realized-vol sigma 15m | 0.8397 [0.584, 1.096] | 0.6751 [0.4446, 0.8778] | higher_wins | 0.631 |
| Brownian p via realized vol 15m | 0.7994 [0.7204, 0.8635] | 0.7502 [0.6717, 0.81] | higher_wins | 0.631 |
| Margin / v28 sigma | 0.9084 [0.8154, 1.138] | 0.835 [0.5686, 1.072] | higher_wins | 0.615 |
| Brownian p via v28 sigma | 0.8182 [0.7926, 0.8724] | 0.7981 [0.7152, 0.858] | higher_wins | 0.615 |
| Signed BTC move 15m | 92.38 [32.74, 150.2] | 47.62 [16.35, 119.9] | higher_wins | 0.593 |
| Signed BTC move 3m | 59.75 [35.29, 86.71] | 30.95 [5.33, 102] | higher_wins | 0.589 |
| 3m drift-projected margin | 265.9 [95.88, 410.4] | 133 [48.82, 422.7] | higher_wins | 0.588 |
| Signed BTC move 5m | 75.61 [36.68, 108.7] | 45.13 [10.47, 132.1] | higher_wins | 0.585 |
| 5m drift-projected margin | 208 [90.78, 321.9] | 134.1 [49.71, 244.5] | higher_wins | 0.571 |
| Adverse BTC move 5m | 0 [0, 0] | 0 [0, 0] | lower_wins | 0.560 |

## `current_v28_first_opportunities`

- Rows: 69
- Contracts: 138
- Baseline: 112/138 contracts = 81.16%; 56/69 trades = 81.16%

### Prior Checks

| prior | contracts | contract acc | contract ret | trades | trade acc |
|---|---:|---:|---:|---:|---:|
| `v28 p_side>=0.85 and ask<=90` | 112/138 | 81.16% | 100.00% | 56/69 | 81.16% |
| `v28 edge>=2c and ask<=90` | 112/138 | 81.16% | 100.00% | 56/69 | 81.16% |
| `margin/v28_sigma>=0.5` | 102/126 | 80.95% | 91.30% | 51/63 | 80.95% |
| `margin/v28_sigma>=1.0` | 18/22 | 81.82% | 15.94% | 9/11 | 81.82% |
| `margin/rv15>=0.5` | 98/116 | 84.48% | 84.06% | 49/58 | 84.48% |
| `Brownian rv15 p>=0.70` | 92/108 | 85.19% | 78.26% | 46/54 | 85.19% |
| `projected_margin_3m>=50` | 102/126 | 80.95% | 91.30% | 51/63 | 80.95% |
| `adverse15<10 or v28 cushion>0.5` | 108/132 | 81.82% | 95.65% | 54/66 | 81.82% |

### Strongest Single-Feature Separators

| feature | winner median [IQR] | loser median [IQR] | direction | separation |
|---|---:|---:|---|---:|
| Signed BTC move 15m | 77.49 [26.05, 151.3] | 32.18 [5.69, 81.49] | higher_wins | 0.666 |
| Margin / realized-vol sigma 15m | 0.8497 [0.575, 1.041] | 0.7493 [0.4893, 0.9175] | higher_wins | 0.609 |
| Brownian p via realized vol 15m | 0.8023 [0.7174, 0.8511] | 0.7732 [0.6877, 0.8206] | higher_wins | 0.609 |
| v28 side probability | 0.869 [0.8549, 0.8892] | 0.8554 [0.8547, 0.8749] | higher_wins | 0.593 |
| Margin / v28 sigma | 0.8502 [0.8053, 0.9296] | 0.8317 [0.7937, 0.8506] | higher_wins | 0.588 |
| Brownian p via v28 sigma | 0.8024 [0.7897, 0.8237] | 0.7972 [0.7863, 0.8025] | higher_wins | 0.588 |
| Adverse BTC move 15m | 0 [0, 0] | 0 [0, 0] | lower_wins | 0.562 |
| Signed BTC move 5m | 73.59 [34.12, 95.85] | 70.04 [33.59, 163.5] | lower_wins | 0.554 |
| Seconds to close | 646.7 [398.9, 804.7] | 560.3 [489.6, 722.2] | higher_wins | 0.544 |
| v28 edge cents | 7.442 [4.066, 12.57] | 5.037 [4.727, 7.991] | higher_wins | 0.536 |

## `live_90_70_replay`

- Rows: 509
- Contracts: 4983
- Baseline: 4903/4983 contracts = 98.39%; 501/509 trades = 98.43%

### Prior Checks

| prior | contracts | contract acc | contract ret | trades | trade acc |
|---|---:|---:|---:|---:|---:|
| `v28 p_side>=0.85 and ask<=90` | 570/570 | 100.00% | 11.44% | 57/57 | 100.00% |
| `v28 edge>=2c and ask<=90` | 300/300 | 100.00% | 6.02% | 30/30 | 100.00% |
| `margin/v28_sigma>=0.5` | 2864/2904 | 98.62% | 58.28% | 292/296 | 98.65% |
| `margin/v28_sigma>=1.0` | 607/607 | 100.00% | 12.18% | 62/62 | 100.00% |
| `margin/rv15>=0.5` | 3760/3830 | 98.17% | 76.86% | 385/392 | 98.21% |
| `Brownian rv15 p>=0.70` | 3690/3760 | 98.14% | 75.46% | 378/385 | 98.18% |
| `projected_margin_3m>=50` | 3481/3551 | 98.03% | 71.26% | 356/363 | 98.07% |
| `adverse15<10 or v28 cushion>0.5` | 4220/4290 | 98.37% | 86.09% | 431/438 | 98.40% |

### Strongest Single-Feature Separators

| feature | winner median [IQR] | loser median [IQR] | direction | separation |
|---|---:|---:|---|---:|
| Seconds to close | 373 [217, 535] | 524 [451.8, 627.8] | lower_wins | 0.725 |
| 5m drift-projected margin | 114.1 [46.18, 236.8] | 211.3 [182.3, 346.1] | lower_wins | 0.692 |
| Signed BTC move 5m | 50.27 [9.96, 99.22] | 96.68 [62.62, 128] | lower_wins | 0.663 |
| 3m drift-projected margin | 126.1 [43.72, 284.5] | 278.6 [210, 336.2] | lower_wins | 0.656 |
| Spot-strike margin | 63.02 [30.31, 98.57] | 71.61 [65.33, 114.6] | lower_wins | 0.644 |
| Signed BTC move 15m | 53.17 [10.44, 117.8] | 114.1 [38.04, 164.8] | lower_wins | 0.631 |
| Signed BTC move 3m | 40.55 [5.82, 83.31] | 69.58 [42.95, 114.1] | lower_wins | 0.629 |
| Margin / realized-vol sigma 15m | 0.8649 [0.5369, 1.175] | 1.003 [0.9056, 1.355] | lower_wins | 0.626 |
| Brownian p via realized vol 15m | 0.8064 [0.7043, 0.88] | 0.8419 [0.8155, 0.912] | lower_wins | 0.626 |
| Margin / sqrt(seconds) | 3.388 [2.002, 4.985] | 3.528 [2.888, 5.592] | lower_wins | 0.575 |

## Readout

- Current v28 fills are only 80.48% on 251 contracts; first websocket opportunities are similarly weak at 81.16% on 138 contracts.
- The supplemental live_90_70 replay is a different regime: 98.39% on 4983 contracts before filtering.
- The current-v28 failure is therefore not just order execution noise. The same overconfidence appears in the approved websocket opportunity set before fills.
- The adverse-drift prior is not sufficient on current v28 because many current losers already have favorable signed short-window movement; high-volume adverse filters mostly preserve the losing holdout.
- Several physical features flip direction across regimes. In current v28, higher signed movement and larger cushion weakly help; in live_90_70, the few losses often occur at larger cushions and longer time-to-close. That argues for regime gating before trusting a monotonic fair-value prior.
- This falsifies promotion of the current v28 fair-value prior. The honest next evidence is fresh post-lock shadow validation, not more threshold tuning on the old current-v28 holdout.
