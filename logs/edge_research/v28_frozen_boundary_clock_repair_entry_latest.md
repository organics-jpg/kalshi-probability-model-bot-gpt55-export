# v28 Frozen Boundary-Clock Repair Entry

- Freeze timestamp UTC: `2026-05-06T07:07:27.790042+00:00`
- Candidate: `skip_boundary_clock_composite_repair_lowest_recross`
- Future denominator: `121`
- Needed/missed repairs: `40/25`
- Delta vs target: `348.000000c`
- Blockers: `net_not_positive`

## Interpretation

- Future candidate has 91 entries and 91 settled rows.
- Candidate net is -151.0c versus target -499.0c.
- Boundary-clock rows removed: 38; repair rows added: 40.
- Promotion blockers: net_not_positive.

## Summaries

| slice | entries | settled | W/L | coverage | net c | avg net c |
|---|---:|---:|---:|---:|---:|---:|
| target | 89 | 89 | 49/40 | 73.553719 | -499.000000 | -5.606742 |
| danger_removed | 38 | 38 | 18/20 | 31.404959 | -570.000000 | -15.000000 |
| kept | 51 | 51 | 31/20 | 42.148760 | 71.000000 | 1.392157 |
| repairs | 40 | 40 | 27/13 | 33.057851 | -222.000000 | -5.550000 |
| candidate | 91 | 91 | 58/33 | 75.206612 | -151.000000 | -1.659341 |

## Removed Rows

| market | source | side | won | net c | p | ask | edge | stc | abs d | recross |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY060345-45 | rejected_actionable | yes | False | -80.000000 | 0.515105 | 0.380000 | 0.135105 | 868.842000 | 0.064212 | 0.911219 |
| KXBTC15M-26MAY060415-15 | rejected_actionable | yes | True | 62.000000 | 0.676831 | 0.670000 | 0.006831 | 792.955000 | 0.394255 | 0.625830 |
| KXBTC15M-26MAY060515-15 | rejected_actionable | yes | False | -86.000000 | 0.532512 | 0.410000 | 0.122512 | 825.119000 | 0.141500 | 0.958625 |
| KXBTC15M-26MAY060530-30 | rejected_actionable | yes | False | -112.000000 | 0.588889 | 0.540000 | 0.048889 | 829.016000 | 0.202598 | 0.884715 |
| KXBTC15M-26MAY060630-30 | rejected_actionable | no | False | -136.000000 | 0.675344 | 0.660000 | 0.015344 | 868.927000 | 0.393798 | 0.762043 |
| KXBTC15M-26MAY060645-45 | rejected_actionable | yes | True | 78.000000 | 0.598639 | 0.590000 | 0.008639 | 884.203000 | 0.277816 | 0.856108 |
| KXBTC15M-26MAY060730-30 | rejected_actionable | yes | True | 84.000000 | 0.594884 | 0.560000 | 0.034884 | 867.397000 | 0.270357 | 0.863859 |
| KXBTC15M-26MAY060800-00 | rejected_actionable | yes | True | 102.000000 | 0.523411 | 0.470000 | 0.053411 | 884.129000 | 0.027808 | 1.358871 |
| KXBTC15M-26MAY060830-30 | rejected_actionable | no | False | -122.000000 | 0.600730 | 0.590000 | 0.010730 | 884.233000 | 0.286154 | 0.943700 |
| KXBTC15M-26MAY060930-30 | rejected_actionable | yes | False | -124.000000 | 0.604377 | 0.600000 | 0.004377 | 864.340000 | 0.244982 | 1.150583 |
| KXBTC15M-26MAY061015-15 | rejected_actionable | no | True | 92.000000 | 0.595554 | 0.520000 | 0.075554 | 883.995000 | 0.274143 | 1.130150 |
| KXBTC15M-26MAY061045-45 | rejected_actionable | no | False | -118.000000 | 0.601767 | 0.570000 | 0.031767 | 868.842000 | 0.212683 | 1.191443 |
| KXBTC15M-26MAY061100-00 | rejected_actionable | yes | False | -151.000000 | 0.740374 | 0.740000 | 0.000374 | 865.321000 | 0.597049 | 0.809587 |
| KXBTC15M-26MAY061130-30 | rejected_actionable | yes | True | 66.000000 | 0.653101 | 0.650000 | 0.003101 | 883.089000 | 0.341283 | 1.056221 |
| KXBTC15M-26MAY061230-30 | rejected_actionable | yes | False | -140.000000 | 0.681329 | 0.680000 | 0.001329 | 829.291000 | 0.451740 | 0.862457 |
| KXBTC15M-26MAY061430-30 | rejected_actionable | yes | True | 62.000000 | 0.678512 | 0.670000 | 0.008512 | 864.426000 | 0.424290 | 0.893555 |
| KXBTC15M-26MAY061445-45 | rejected_actionable | no | True | 55.000000 | 0.724164 | 0.710000 | 0.014164 | 884.401000 | 0.536135 | 0.800263 |
| KXBTC15M-26MAY061700-00 | rejected_actionable | no | False | -102.000000 | 0.547299 | 0.490000 | 0.057299 | 759.628000 | 0.145303 | 0.799916 |
| KXBTC15M-26MAY061900-00 | rejected_actionable | yes | True | 128.000000 | 0.501794 | 0.340000 | 0.161794 | 766.143000 | 0.001392 | 0.794136 |
| KXBTC15M-26MAY061930-30 | rejected_actionable | yes | True | 102.000000 | 0.551364 | 0.470000 | 0.081364 | 810.397000 | 0.100563 | 0.905378 |
| KXBTC15M-26MAY061945-45 | rejected_actionable | yes | False | -88.000000 | 0.542407 | 0.420000 | 0.122407 | 809.092000 | 0.132650 | 0.801256 |
| KXBTC15M-26MAY062130-30 | rejected_actionable | yes | True | 114.000000 | 0.586142 | 0.410000 | 0.176142 | 753.109000 | 0.212967 | 0.800157 |
| KXBTC15M-26MAY062145-45 | rejected_actionable | yes | True | 82.000000 | 0.600378 | 0.570000 | 0.030378 | 800.015000 | 0.250555 | 0.820982 |
| KXBTC15M-26MAY062245-45 | rejected_actionable | no | False | -112.000000 | 0.605951 | 0.540000 | 0.065951 | 841.408000 | 0.278629 | 0.786584 |
| KXBTC15M-26MAY070030-30 | rejected_actionable | no | False | -70.000000 | 0.523605 | 0.330000 | 0.193605 | 770.113000 | 0.059362 | 0.901651 |
| KXBTC15M-26MAY070045-45 | rejected_actionable | no | True | 100.000000 | 0.582164 | 0.480000 | 0.102164 | 810.351000 | 0.187292 | 0.830545 |
| KXBTC15M-26MAY070530-30 | rejected_actionable | no | True | 100.000000 | 0.540822 | 0.480000 | 0.060822 | 879.618000 | 0.132673 | 0.894668 |
| KXBTC15M-26MAY070630-30 | rejected_actionable | yes | False | -98.000000 | 0.606974 | 0.470000 | 0.136974 | 875.963000 | 0.230767 | 0.826469 |
| KXBTC15M-26MAY070715-15 | rejected_actionable | yes | True | 94.000000 | 0.560435 | 0.510000 | 0.050435 | 812.253000 | 0.157545 | 0.877232 |
| KXBTC15M-26MAY070730-30 | rejected_actionable | yes | False | -96.000000 | 0.530778 | 0.460000 | 0.070778 | 819.643000 | 0.091964 | 0.936121 |
| KXBTC15M-26MAY070800-00 | rejected_actionable | yes | False | -94.000000 | 0.536385 | 0.450000 | 0.086385 | 771.226000 | 0.080069 | 0.865475 |
| KXBTC15M-26MAY070815-15 | rejected_actionable | yes | True | 108.000000 | 0.501147 | 0.440000 | 0.061147 | 882.524000 | 0.024626 | 1.067161 |
| KXBTC15M-26MAY070830-30 | rejected_actionable | yes | False | -86.000000 | 0.514492 | 0.410000 | 0.104492 | 811.825000 | 0.078942 | 0.952791 |
| KXBTC15M-26MAY070900-00 | rejected_actionable | yes | True | 86.000000 | 0.597604 | 0.550000 | 0.047604 | 773.230000 | 0.238237 | 0.771689 |
| KXBTC15M-26MAY070945-45 | rejected_actionable | no | True | 100.000000 | 0.532085 | 0.480000 | 0.052085 | 860.716000 | 0.067417 | 1.088863 |
| KXBTC15M-26MAY071015-15 | rejected_actionable | no | False | -124.000000 | 0.609894 | 0.600000 | 0.009894 | 864.225000 | 0.287274 | 1.102864 |
| KXBTC15M-26MAY071200-00 | rejected_actionable | yes | False | -124.000000 | 0.606055 | 0.600000 | 0.006055 | 793.821000 | 0.250754 | 1.096302 |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -122.000000 | 0.636040 | 0.590000 | 0.046040 | 842.515000 | 0.289227 | 1.011545 |
