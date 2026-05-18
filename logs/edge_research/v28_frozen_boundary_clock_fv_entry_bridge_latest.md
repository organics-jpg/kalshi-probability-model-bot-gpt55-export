# v28 Frozen Boundary-Clock FV Entry Bridge

- Freeze timestamp UTC: `2026-05-06T07:35:02.597585+00:00`
- Candidate: `boundary_clock_adjusted_edge_floor_0p02_repair_lowest_recross`
- Future denominator: `119`
- Needed/missed repairs: `31/25`
- Delta vs target: `530.000000c`
- Blockers: `none`

## Interpretation

- Future candidate has 90 entries and 90 settled rows.
- Candidate net is 229.0c versus target -301.0c.
- Skipped rows: 28; repair rows added: 31.

## Summaries

| slice | entries | settled | W/L | coverage | net c | avg net c |
|---|---:|---:|---:|---:|---:|---:|
| target | 87 | 87 | 49/38 | 73.109244 | -301.000000 | -3.459770 |
| skipped | 28 | 28 | 13/15 | 23.529412 | -862.000000 | -30.785714 |
| kept | 59 | 59 | 36/23 | 49.579832 | 561.000000 | 9.508475 |
| repairs | 31 | 31 | 19/12 | 26.050420 | -332.000000 | -10.709677 |
| candidate | 90 | 90 | 55/35 | 75.630252 | 229.000000 | 2.544444 |

## Skipped Rows

| market | source | side | won | net c | raw p | adj p | ask | adj edge | stc | abs d | recross |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY060415-15 | rejected_actionable | yes | True | 62.000000 | 0.676831 | 0.500000 | 0.670000 | -0.170000 | 792.955000 | 0.394255 | 0.625830 |
| KXBTC15M-26MAY060530-30 | rejected_actionable | yes | False | -112.000000 | 0.588889 | 0.500000 | 0.540000 | -0.040000 | 829.016000 | 0.202598 | 0.884715 |
| KXBTC15M-26MAY060630-30 | rejected_actionable | no | False | -136.000000 | 0.675344 | 0.500000 | 0.660000 | -0.160000 | 868.927000 | 0.393798 | 0.762043 |
| KXBTC15M-26MAY060645-45 | rejected_actionable | yes | True | 78.000000 | 0.598639 | 0.500000 | 0.590000 | -0.090000 | 884.203000 | 0.277816 | 0.856108 |
| KXBTC15M-26MAY060730-30 | rejected_actionable | yes | True | 84.000000 | 0.594884 | 0.500000 | 0.560000 | -0.060000 | 867.397000 | 0.270357 | 0.863859 |
| KXBTC15M-26MAY060830-30 | rejected_actionable | no | False | -122.000000 | 0.600730 | 0.500000 | 0.590000 | -0.090000 | 884.233000 | 0.286154 | 0.943700 |
| KXBTC15M-26MAY060930-30 | rejected_actionable | yes | False | -124.000000 | 0.604377 | 0.500000 | 0.600000 | -0.100000 | 864.340000 | 0.244982 | 1.150583 |
| KXBTC15M-26MAY061015-15 | rejected_actionable | no | True | 92.000000 | 0.595554 | 0.500000 | 0.520000 | -0.020000 | 883.995000 | 0.274143 | 1.130150 |
| KXBTC15M-26MAY061030-30 | rejected_actionable | yes | True | 74.000000 | 0.618153 | 0.618153 | 0.610000 | 0.008153 | 868.942000 | 0.232373 | 1.168280 |
| KXBTC15M-26MAY061045-45 | rejected_actionable | no | False | -118.000000 | 0.601767 | 0.500000 | 0.570000 | -0.070000 | 868.842000 | 0.212683 | 1.191443 |
| KXBTC15M-26MAY061100-00 | rejected_actionable | yes | False | -151.000000 | 0.740374 | 0.500000 | 0.740000 | -0.240000 | 865.321000 | 0.597049 | 0.809587 |
| KXBTC15M-26MAY061130-30 | rejected_actionable | yes | True | 66.000000 | 0.653101 | 0.500000 | 0.650000 | -0.150000 | 883.089000 | 0.341283 | 1.056221 |
| KXBTC15M-26MAY061230-30 | rejected_actionable | yes | False | -140.000000 | 0.681329 | 0.500000 | 0.680000 | -0.180000 | 829.291000 | 0.451740 | 0.862457 |
| KXBTC15M-26MAY061430-30 | rejected_actionable | yes | True | 62.000000 | 0.678512 | 0.500000 | 0.670000 | -0.170000 | 864.426000 | 0.424290 | 0.893555 |
| KXBTC15M-26MAY061445-45 | rejected_actionable | no | True | 55.000000 | 0.724164 | 0.500000 | 0.710000 | -0.210000 | 884.401000 | 0.536135 | 0.800263 |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -124.000000 | 0.610883 | 0.610883 | 0.600000 | 0.010883 | 717.804000 | 0.229994 | 0.723320 |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 70.000000 | 0.631665 | 0.631665 | 0.630000 | 0.001665 | 505.823000 | 0.294854 | 0.450319 |
| KXBTC15M-26MAY061700-00 | rejected_actionable | no | False | -102.000000 | 0.547299 | 0.500000 | 0.490000 | 0.010000 | 759.628000 | 0.145303 | 0.799916 |
| KXBTC15M-26MAY062015-15 | rejected_actionable | yes | False | -106.000000 | 0.526847 | 0.526847 | 0.510000 | 0.016847 | 869.507000 | 0.086972 | 0.736601 |
| KXBTC15M-26MAY062145-45 | rejected_actionable | yes | True | 82.000000 | 0.600378 | 0.500000 | 0.570000 | -0.070000 | 800.015000 | 0.250555 | 0.820982 |
| KXBTC15M-26MAY062245-45 | rejected_actionable | no | False | -112.000000 | 0.605951 | 0.500000 | 0.540000 | -0.040000 | 841.408000 | 0.278629 | 0.786584 |
| KXBTC15M-26MAY070130-30 | rejected_actionable | no | True | 78.000000 | 0.604140 | 0.604140 | 0.590000 | 0.014140 | 585.641000 | 0.227698 | 0.544225 |
| KXBTC15M-26MAY070715-15 | rejected_actionable | yes | True | 94.000000 | 0.560435 | 0.500000 | 0.510000 | -0.010000 | 812.253000 | 0.157545 | 0.877232 |
| KXBTC15M-26MAY070900-00 | rejected_actionable | yes | True | 86.000000 | 0.597604 | 0.500000 | 0.550000 | -0.050000 | 773.230000 | 0.238237 | 0.771689 |
| KXBTC15M-26MAY071015-15 | rejected_actionable | no | False | -124.000000 | 0.609894 | 0.500000 | 0.600000 | -0.100000 | 864.225000 | 0.287274 | 1.102864 |
| KXBTC15M-26MAY071115-15 | rejected_actionable | no | False | -128.000000 | 0.635838 | 0.635838 | 0.620000 | 0.015838 | 843.330000 | 0.346131 | 0.982771 |
| KXBTC15M-26MAY071200-00 | rejected_actionable | yes | False | -124.000000 | 0.606055 | 0.500000 | 0.600000 | -0.100000 | 793.821000 | 0.250754 | 1.096302 |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -122.000000 | 0.636040 | 0.500000 | 0.590000 | -0.090000 | 842.515000 | 0.289227 | 1.011545 |
