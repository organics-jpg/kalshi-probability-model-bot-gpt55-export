# v28 Boundary-Clock Hazard Repair

Diagnostic-only: no live bot changes and no orders.

- Physics: Early near-boundary high-recross rows can be unresolved path turbulence rather than durable FV edge.
- Coverage floor: `75.0`

## Interpretation

- Best rule is early_boundary_recross with net 541.0c and delta 704.0c.
- Coverage is 75.177304964539% after removing 53 target rows and adding 52 repairs.
- Removed rows alone had net -1014.0c.
- This is diagnostic only; a live candidate would need a fresh frozen-forward gate.

## Ranking

| rank | rule | removed | repairs | coverage | net c | delta c | W/L | removed net c | repair net c |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | early_boundary_recross | 53 | 52 | 75.177305 | 541.000000 | 704.000000 | 73/32 | -1014.000000 | -310.000000 |
| 2 | clock_composite | 46 | 45 | 75.177305 | 467.000000 | 630.000000 | 73/32 | -687.000000 | -57.000000 |
| 3 | early_midprob_boundary | 60 | 59 | 75.177305 | 378.000000 | 541.000000 | 74/31 | -700.000000 | -159.000000 |
| 4 | expensive_low_edge_clock | 9 | 8 | 75.177305 | 89.000000 | 252.000000 | 63/43 | -477.000000 | -225.000000 |
| 5 | early_boundary_cheap_recross | 37 | 36 | 75.177305 | -82.000000 | 81.000000 | 69/36 | -210.000000 | -129.000000 |

## Best Removed Rows

| market | source | side | won | net c | p | ask | edge | stc | abs d | recross |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY052015-15 | rejected_actionable | no | False | -102.000000 | 0.567861 | 0.490000 | 0.077861 | 873.050000 | 0.150360 | 0.945709 |
| KXBTC15M-26MAY052030-30 | rejected_actionable | yes | False | -98.000000 | 0.540780 | 0.470000 | 0.070780 | 879.629000 | 0.144729 | 1.053237 |
| KXBTC15M-26MAY052100-00 | rejected_actionable | yes | True | 104.000000 | 0.565554 | 0.460000 | 0.105554 | 808.178000 | 0.155800 | 0.915520 |
| KXBTC15M-26MAY052115-15 | rejected_actionable | yes | True | 90.000000 | 0.571476 | 0.530000 | 0.041476 | 850.512000 | 0.195783 | 0.945077 |
| KXBTC15M-26MAY052245-45 | rejected_actionable | no | False | -118.000000 | 0.643789 | 0.570000 | 0.073789 | 752.490000 | 0.362082 | 0.663374 |
| KXBTC15M-26MAY052345-45 | rejected_actionable | no | True | 70.000000 | 0.636767 | 0.630000 | 0.006767 | 850.023000 | 0.275785 | 0.899454 |
| KXBTC15M-26MAY060030-30 | rejected_actionable | yes | False | -106.000000 | 0.617077 | 0.510000 | 0.107077 | 853.033000 | 0.270552 | 0.831869 |
| KXBTC15M-26MAY060130-30 | rejected_actionable | no | True | 78.000000 | 0.616779 | 0.590000 | 0.026779 | 849.758000 | 0.294972 | 0.777744 |
| KXBTC15M-26MAY060200-00 | rejected_actionable | yes | True | 76.000000 | 0.618277 | 0.600000 | 0.018277 | 849.377000 | 0.248684 | 0.767680 |
| KXBTC15M-26MAY060215-15 | rejected_actionable | yes | False | -110.000000 | 0.583024 | 0.530000 | 0.053024 | 884.651000 | 0.228362 | 0.792609 |
| KXBTC15M-26MAY060245-45 | rejected_actionable | no | False | -134.000000 | 0.660829 | 0.650000 | 0.010829 | 868.740000 | 0.346255 | 0.663720 |
| KXBTC15M-26MAY060330-30 | rejected_actionable | no | False | -118.000000 | 0.630880 | 0.570000 | 0.060880 | 884.146000 | 0.287388 | 0.689280 |
| KXBTC15M-26MAY060345-45 | rejected_actionable | yes | False | -80.000000 | 0.515105 | 0.380000 | 0.135105 | 868.842000 | 0.064212 | 0.911219 |
| KXBTC15M-26MAY060445-45 | rejected_actionable | no | False | -94.000000 | 0.636374 | 0.450000 | 0.186374 | 864.716000 | 0.322198 | 0.666569 |
| KXBTC15M-26MAY060515-15 | rejected_actionable | yes | False | -86.000000 | 0.532512 | 0.410000 | 0.122512 | 825.119000 | 0.141500 | 0.958625 |
| KXBTC15M-26MAY060530-30 | rejected_actionable | yes | False | -112.000000 | 0.588889 | 0.540000 | 0.048889 | 829.016000 | 0.202598 | 0.884715 |
| KXBTC15M-26MAY060545-45 | rejected_actionable | no | False | -92.000000 | 0.626642 | 0.440000 | 0.186642 | 807.560000 | 0.323422 | 0.689053 |
| KXBTC15M-26MAY060630-30 | rejected_actionable | no | False | -136.000000 | 0.675344 | 0.660000 | 0.015344 | 868.927000 | 0.393798 | 0.762043 |
| KXBTC15M-26MAY060645-45 | rejected_actionable | yes | True | 78.000000 | 0.598639 | 0.590000 | 0.008639 | 884.203000 | 0.277816 | 0.856108 |
| KXBTC15M-26MAY060730-30 | rejected_actionable | yes | True | 84.000000 | 0.594884 | 0.560000 | 0.034884 | 867.397000 | 0.270357 | 0.863859 |
| KXBTC15M-26MAY060800-00 | rejected_actionable | yes | True | 102.000000 | 0.523411 | 0.470000 | 0.053411 | 884.129000 | 0.027808 | 1.358871 |
| KXBTC15M-26MAY060830-30 | rejected_actionable | no | False | -122.000000 | 0.600730 | 0.590000 | 0.010730 | 884.233000 | 0.286154 | 0.943700 |
| KXBTC15M-26MAY060930-30 | rejected_actionable | yes | False | -124.000000 | 0.604377 | 0.600000 | 0.004377 | 864.340000 | 0.244982 | 1.150583 |
| KXBTC15M-26MAY061015-15 | rejected_actionable | no | True | 92.000000 | 0.595554 | 0.520000 | 0.075554 | 883.995000 | 0.274143 | 1.130150 |
| KXBTC15M-26MAY061030-30 | rejected_actionable | yes | True | 74.000000 | 0.618153 | 0.610000 | 0.008153 | 868.942000 | 0.232373 | 1.168280 |
| KXBTC15M-26MAY061045-45 | rejected_actionable | no | False | -118.000000 | 0.601767 | 0.570000 | 0.031767 | 868.842000 | 0.212683 | 1.191443 |
| KXBTC15M-26MAY061130-30 | rejected_actionable | yes | True | 66.000000 | 0.653101 | 0.650000 | 0.003101 | 883.089000 | 0.341283 | 1.056221 |
| KXBTC15M-26MAY061700-00 | rejected_actionable | no | False | -102.000000 | 0.547299 | 0.490000 | 0.057299 | 759.628000 | 0.145303 | 0.799916 |
| KXBTC15M-26MAY061715-15 | rejected_actionable | yes | False | -104.000000 | 0.633073 | 0.500000 | 0.133073 | 804.817000 | 0.324075 | 0.683095 |
| KXBTC15M-26MAY061900-00 | rejected_actionable | yes | True | 128.000000 | 0.501794 | 0.340000 | 0.161794 | 766.143000 | 0.001392 | 0.794136 |
| KXBTC15M-26MAY061930-30 | rejected_actionable | yes | True | 102.000000 | 0.551364 | 0.470000 | 0.081364 | 810.397000 | 0.100563 | 0.905378 |
| KXBTC15M-26MAY061945-45 | rejected_actionable | yes | False | -88.000000 | 0.542407 | 0.420000 | 0.122407 | 809.092000 | 0.132650 | 0.801256 |
| KXBTC15M-26MAY062000-00 | rejected_actionable | yes | True | 96.000000 | 0.582435 | 0.500000 | 0.082435 | 849.989000 | 0.192858 | 0.673972 |
| KXBTC15M-26MAY062015-15 | rejected_actionable | yes | False | -106.000000 | 0.526847 | 0.510000 | 0.016847 | 869.507000 | 0.086972 | 0.736601 |
| KXBTC15M-26MAY062030-30 | rejected_actionable | yes | False | -68.000000 | 0.544418 | 0.320000 | 0.224418 | 804.712000 | 0.107412 | 0.680770 |
| KXBTC15M-26MAY062130-30 | rejected_actionable | yes | True | 114.000000 | 0.586142 | 0.410000 | 0.176142 | 753.109000 | 0.212967 | 0.800157 |
| KXBTC15M-26MAY062145-45 | rejected_actionable | yes | True | 82.000000 | 0.600378 | 0.570000 | 0.030378 | 800.015000 | 0.250555 | 0.820982 |
| KXBTC15M-26MAY062245-45 | rejected_actionable | no | False | -112.000000 | 0.605951 | 0.540000 | 0.065951 | 841.408000 | 0.278629 | 0.786584 |
| KXBTC15M-26MAY062345-45 | rejected_actionable | no | False | -96.000000 | 0.608623 | 0.460000 | 0.148623 | 723.265000 | 0.276153 | 0.675325 |
| KXBTC15M-26MAY070030-30 | rejected_actionable | no | False | -70.000000 | 0.523605 | 0.330000 | 0.193605 | 770.113000 | 0.059362 | 0.901651 |
| KXBTC15M-26MAY070045-45 | rejected_actionable | no | True | 100.000000 | 0.582164 | 0.480000 | 0.102164 | 810.351000 | 0.187292 | 0.830545 |
| KXBTC15M-26MAY070530-30 | rejected_actionable | no | True | 100.000000 | 0.540822 | 0.480000 | 0.060822 | 879.618000 | 0.132673 | 0.894668 |
| KXBTC15M-26MAY070630-30 | rejected_actionable | yes | False | -98.000000 | 0.606974 | 0.470000 | 0.136974 | 875.963000 | 0.230767 | 0.826469 |
| KXBTC15M-26MAY070700-00 | rejected_actionable | yes | False | -116.000000 | 0.654812 | 0.560000 | 0.094812 | 869.636000 | 0.375634 | 0.760124 |
| KXBTC15M-26MAY070715-15 | rejected_actionable | yes | True | 94.000000 | 0.560435 | 0.510000 | 0.050435 | 812.253000 | 0.157545 | 0.877232 |
| KXBTC15M-26MAY070730-30 | rejected_actionable | yes | False | -96.000000 | 0.530778 | 0.460000 | 0.070778 | 819.643000 | 0.091964 | 0.936121 |
| KXBTC15M-26MAY070800-00 | rejected_actionable | yes | False | -94.000000 | 0.536385 | 0.450000 | 0.086385 | 771.226000 | 0.080069 | 0.865475 |
| KXBTC15M-26MAY070815-15 | rejected_actionable | yes | True | 108.000000 | 0.501147 | 0.440000 | 0.061147 | 882.524000 | 0.024626 | 1.067161 |
| KXBTC15M-26MAY070830-30 | rejected_actionable | yes | False | -86.000000 | 0.514492 | 0.410000 | 0.104492 | 811.825000 | 0.078942 | 0.952791 |
| KXBTC15M-26MAY070900-00 | rejected_actionable | yes | True | 86.000000 | 0.597604 | 0.550000 | 0.047604 | 773.230000 | 0.238237 | 0.771689 |
| KXBTC15M-26MAY070945-45 | rejected_actionable | no | True | 100.000000 | 0.532085 | 0.480000 | 0.052085 | 860.716000 | 0.067417 | 1.088863 |
| KXBTC15M-26MAY071015-15 | rejected_actionable | no | False | -124.000000 | 0.609894 | 0.600000 | 0.009894 | 864.225000 | 0.287274 | 1.102864 |
| KXBTC15M-26MAY071030-30 | rejected_actionable | no | True | 72.000000 | 0.646380 | 0.620000 | 0.026380 | 852.539000 | 0.326478 | 1.053270 |
