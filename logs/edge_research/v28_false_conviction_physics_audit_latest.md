# v28 False-Conviction Physics Audit

Research-only diagnostic. No live bot changes or orders.

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Forward denominator: `152`
- Current entries/settled/coverage: `112/112/73.684211`
- Current W/L/net: `64/48/-626.000000c`

## Read

- mid_edge_boundary_4_8pp is a repeated negative-expectancy pocket: 21 settled, W/L 10/11, net -290.0c.
- Best adjusted-FV valve for mid_edge_boundary_4_8pp is full_to_50: coverage 60.526315789473685%, net -228.0c, delta 398.0c.
- cheap_near_boundary_turbulence is a repeated negative-expectancy pocket: 24 settled, W/L 11/13, net -80.0c.
- Best adjusted-FV valve for cheap_near_boundary_turbulence is full_to_book: coverage 57.89473684210527%, net -546.0c, delta 80.0c.
- early_no_boundary_decay is a repeated negative-expectancy pocket: 30 settled, W/L 12/18, net -875.0c.
- Best adjusted-FV valve for early_no_boundary_decay is half_to_50: coverage 60.526315789473685%, net 200.0c, delta 826.0c.
- composite_false_conviction_zone is a repeated negative-expectancy pocket: 50 settled, W/L 21/29, net -1017.0c.
- Best adjusted-FV valve for composite_false_conviction_zone is half_to_50: coverage 56.57894736842105%, net 274.0c, delta 900.0c.

## mid_edge_boundary_4_8pp

- Inside settled/W-L/net: `21/10-11/-290.000000c`
- Outside settled/W-L/net: `91/54-37/-336.000000c`

### Probability Shrinkage Inside Mask

| overlay | scored | avg p | win rate | brier d | logloss d |
|---|---:|---:|---:|---:|---:|
| `full_to_50` | 21 | 0.500000 | 0.476190 | -0.023883 | -0.049129 |
| `half_to_50` | 21 | 0.542997 | 0.476190 | -0.014425 | -0.030097 |
| `full_to_book` | 21 | 0.525238 | 0.476190 | -0.011783 | -0.024688 |
| `half_to_book` | 21 | 0.555616 | 0.476190 | -0.006843 | -0.014469 |
| `raw` | 21 | 0.585995 | 0.476190 | 0.000000 | 0.000000 |

### Adjusted-FV Entry Impact

| overlay | kept coverage | kept settled | kept net c | delta c | removed settled | removed net c |
|---|---:|---:|---:|---:|---:|---:|
| `half_to_50` | 63.815789 | 97 | -322.000000 | 304.000000 | 15 | -304.000000 |
| `full_to_50` | 60.526316 | 92 | -228.000000 | 398.000000 | 20 | -398.000000 |
| `half_to_book` | 63.815789 | 97 | -666.000000 | -40.000000 | 15 | 40.000000 |
| `full_to_book` | 61.184211 | 93 | -386.000000 | 240.000000 | 19 | -240.000000 |

## cheap_near_boundary_turbulence

- Inside settled/W-L/net: `24/11-13/-80.000000c`
- Outside settled/W-L/net: `88/53-35/-546.000000c`

### Probability Shrinkage Inside Mask

| overlay | scored | avg p | win rate | brier d | logloss d |
|---|---:|---:|---:|---:|---:|
| `full_to_book` | 24 | 0.455000 | 0.458333 | -0.012096 | -0.024440 |
| `half_to_book` | 24 | 0.501386 | 0.458333 | -0.008653 | -0.017438 |
| `full_to_50` | 24 | 0.500000 | 0.458333 | -0.007821 | -0.015819 |
| `half_to_50` | 24 | 0.523886 | 0.458333 | -0.004681 | -0.009523 |
| `raw` | 24 | 0.547771 | 0.458333 | 0.000000 | 0.000000 |

### Adjusted-FV Entry Impact

| overlay | kept coverage | kept settled | kept net c | delta c | removed settled | removed net c |
|---|---:|---:|---:|---:|---:|---:|
| `half_to_50` | 69.736842 | 106 | -586.000000 | 40.000000 | 6 | -40.000000 |
| `full_to_50` | 63.815789 | 97 | -700.000000 | -74.000000 | 15 | 74.000000 |
| `half_to_book` | 65.789474 | 100 | -600.000000 | 26.000000 | 12 | -26.000000 |
| `full_to_book` | 57.894737 | 88 | -546.000000 | 80.000000 | 24 | -80.000000 |

## early_no_boundary_decay

- Inside settled/W-L/net: `30/12-18/-875.000000c`
- Outside settled/W-L/net: `82/52-30/249.000000c`

### Probability Shrinkage Inside Mask

| overlay | scored | avg p | win rate | brier d | logloss d |
|---|---:|---:|---:|---:|---:|
| `full_to_50` | 30 | 0.500000 | 0.400000 | -0.034235 | -0.070568 |
| `full_to_book` | 30 | 0.526333 | 0.400000 | -0.021572 | -0.045961 |
| `half_to_50` | 30 | 0.555826 | 0.400000 | -0.020742 | -0.043405 |
| `half_to_book` | 30 | 0.568993 | 0.400000 | -0.014552 | -0.030391 |
| `raw` | 30 | 0.611652 | 0.400000 | 0.000000 | 0.000000 |

### Adjusted-FV Entry Impact

| overlay | kept coverage | kept settled | kept net c | delta c | removed settled | removed net c |
|---|---:|---:|---:|---:|---:|---:|
| `half_to_50` | 60.526316 | 92 | 200.000000 | 826.000000 | 20 | -826.000000 |
| `full_to_50` | 57.236842 | 87 | 104.000000 | 730.000000 | 25 | -730.000000 |
| `half_to_book` | 68.421053 | 104 | -362.000000 | 264.000000 | 8 | -264.000000 |
| `full_to_book` | 60.526316 | 92 | -235.000000 | 391.000000 | 20 | -391.000000 |

## composite_false_conviction_zone

- Inside settled/W-L/net: `50/21-29/-1017.000000c`
- Outside settled/W-L/net: `62/43-19/391.000000c`

### Probability Shrinkage Inside Mask

| overlay | scored | avg p | win rate | brier d | logloss d |
|---|---:|---:|---:|---:|---:|
| `full_to_50` | 50 | 0.500000 | 0.420000 | -0.025614 | -0.052703 |
| `full_to_book` | 50 | 0.502000 | 0.420000 | -0.017062 | -0.035818 |
| `half_to_50` | 50 | 0.544359 | 0.420000 | -0.015408 | -0.032163 |
| `half_to_book` | 50 | 0.545359 | 0.420000 | -0.011745 | -0.024364 |
| `raw` | 50 | 0.588718 | 0.420000 | 0.000000 | 0.000000 |

### Adjusted-FV Entry Impact

| overlay | kept coverage | kept settled | kept net c | delta c | removed settled | removed net c |
|---|---:|---:|---:|---:|---:|---:|
| `half_to_50` | 56.578947 | 86 | 274.000000 | 900.000000 | 26 | -900.000000 |
| `full_to_50` | 49.342105 | 75 | 162.000000 | 788.000000 | 37 | -788.000000 |
| `half_to_book` | 62.500000 | 95 | -426.000000 | 200.000000 | 17 | -200.000000 |
| `full_to_book` | 47.368421 | 72 | -93.000000 | 533.000000 | 40 | -533.000000 |

## Worst Rows

| market | side | won | net c | raw p | adj p | ask | edge | stc | abs d | recross |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY060100-00 | yes | False | -161.000000 | 0.799928 |  | 0.790000 | 0.009928 | 684.076000 | 0.694496 | 0.407561 |
| KXBTC15M-26MAY061100-00 | yes | False | -151.000000 | 0.740374 |  | 0.740000 | 0.000374 | 865.321000 | 0.597049 | 0.809587 |
| KXBTC15M-26MAY071230-30 | no | False | -143.000000 | 0.729882 |  | 0.700000 | 0.029882 | 863.492000 | 0.573733 | 0.815016 |
| KXBTC15M-26MAY061230-30 | yes | False | -140.000000 | 0.681329 |  | 0.680000 | 0.001329 | 829.291000 | 0.451740 | 0.862457 |
| KXBTC15M-26MAY060630-30 | no | False | -136.000000 | 0.675344 |  | 0.660000 | 0.015344 | 868.927000 | 0.393798 | 0.762043 |
| KXBTC15M-26MAY060245-45 | no | False | -134.000000 | 0.660829 |  | 0.650000 | 0.010829 | 868.740000 | 0.346255 | 0.663720 |
| KXBTC15M-26MAY052330-30 | no | False | -130.000000 | 0.659176 |  | 0.630000 | 0.029176 | 654.661000 | 0.369967 | 0.572942 |
| KXBTC15M-26MAY071115-15 | no | False | -128.000000 | 0.635838 |  | 0.620000 | 0.015838 | 843.330000 | 0.346131 | 0.982771 |
| KXBTC15M-26MAY060500-00 | no | False | -126.000000 | 0.674136 |  | 0.610000 | 0.064136 | 783.254000 | 0.377919 | 0.620318 |
| KXBTC15M-26MAY060930-30 | yes | False | -124.000000 | 0.604377 |  | 0.600000 | 0.004377 | 864.340000 | 0.244982 | 1.150583 |
| KXBTC15M-26MAY061600-00 | no | False | -124.000000 | 0.610883 |  | 0.600000 | 0.010883 | 717.804000 | 0.229994 | 0.723320 |
| KXBTC15M-26MAY070545-45 | yes | False | -124.000000 | 0.707647 |  | 0.600000 | 0.107647 | 855.690000 | 0.462750 | 0.622015 |
| KXBTC15M-26MAY071015-15 | no | False | -124.000000 | 0.609894 |  | 0.600000 | 0.009894 | 864.225000 | 0.287274 | 1.102864 |
| KXBTC15M-26MAY071200-00 | yes | False | -124.000000 | 0.606055 |  | 0.600000 | 0.006055 | 793.821000 | 0.250754 | 1.096302 |
| KXBTC15M-26MAY060830-30 | no | False | -122.000000 | 0.600730 |  | 0.590000 | 0.010730 | 884.233000 | 0.286154 | 0.943700 |
