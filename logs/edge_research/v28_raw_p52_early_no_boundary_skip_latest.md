# v28 Raw p52 Early-NO Boundary Skip

Discovery diagnostic only. Frozen validator fixes this rule before forward validation.

- Base policy: `v28_raw_p52_edge0`
- Candidate: `raw_p52_skip_early_no_boundary_decay`
- Rule: `Start from v28_raw_p52_edge0 and skip NO rows with stc>=720, p<0.70, abs_d<=0.45, recross>=0.55.`
- Watched markets: `181`
- Delta vs base: `578.000000c`

## Summary

| row | entries | settled | W/L | coverage | win rate | avg p | avg ask | avg abs d | avg recross | net c | actual/sim |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| base | 169 | 169 | 104/65 | 93.370166 | 0.615385 | 0.644300 | 0.586036 | 0.353552 | 0.771407 | 71.000000 | 12/157 |
| candidate_summary | 123 | 123 | 81/42 | 67.955801 | 0.658537 | 0.663919 | 0.602195 | 0.402592 | 0.714067 | 649.000000 | 12/111 |
| skipped_summary | 46 | 46 | 23/23 | 25.414365 | 0.500000 | 0.591842 | 0.542826 | 0.222423 | 0.924730 | -578.000000 | 0/46 |

## Skipped Rows

| market | side | source | p | ask | stc | abs d | recross | won | net c |
|---|---|---|---:|---:|---:|---:|---:|---|---:|
| KXBTC15M-26MAY051600-00 | no | rejected_actionable | 0.547953 | 0.460000 | 856.344000 | 0.077742 | 1.113851 | True | 104.000000 |
| KXBTC15M-26MAY051700-00 | no | rejected_actionable | 0.570256 | 0.570000 | 884.255000 | 0.132227 | 1.086646 | True | 82.000000 |
| KXBTC15M-26MAY051715-15 | no | rejected_actionable | 0.520761 | 0.510000 | 884.029000 | 0.035293 | 1.100586 | True | 94.000000 |
| KXBTC15M-26MAY052015-15 | no | rejected_actionable | 0.567861 | 0.490000 | 873.050000 | 0.150360 | 0.945709 | False | -102.000000 |
| KXBTC15M-26MAY052200-00 | no | rejected_actionable | 0.551743 | 0.520000 | 823.452000 | 0.104813 | 0.987800 | False | -108.000000 |
| KXBTC15M-26MAY052245-45 | no | rejected_actionable | 0.643789 | 0.570000 | 752.490000 | 0.362082 | 0.663374 | False | -118.000000 |
| KXBTC15M-26MAY052345-45 | no | rejected_actionable | 0.636767 | 0.630000 | 850.023000 | 0.275785 | 0.899454 | True | 70.000000 |
| KXBTC15M-26MAY060000-00 | no | rejected_actionable | 0.576655 | 0.560000 | 752.798000 | 0.185582 | 0.862070 | False | -116.000000 |
| KXBTC15M-26MAY060115-15 | no | rejected_actionable | 0.577382 | 0.560000 | 844.619000 | 0.206681 | 0.859977 | True | 84.000000 |
| KXBTC15M-26MAY060130-30 | no | rejected_actionable | 0.616779 | 0.590000 | 849.758000 | 0.294972 | 0.777744 | True | 78.000000 |
| KXBTC15M-26MAY060145-45 | no | rejected_actionable | 0.557282 | 0.550000 | 869.229000 | 0.151652 | 0.849189 | True | 86.000000 |
| KXBTC15M-26MAY060230-30 | no | rejected_actionable | 0.574094 | 0.540000 | 884.495000 | 0.196217 | 0.789327 | False | -112.000000 |
| KXBTC15M-26MAY060245-45 | no | rejected_actionable | 0.660829 | 0.650000 | 868.740000 | 0.346255 | 0.663720 | False | -134.000000 |
| KXBTC15M-26MAY060330-30 | no | rejected_actionable | 0.630880 | 0.570000 | 884.146000 | 0.287388 | 0.689280 | False | -118.000000 |
| KXBTC15M-26MAY060445-45 | no | rejected_actionable | 0.636374 | 0.450000 | 864.716000 | 0.322198 | 0.666569 | False | -94.000000 |
| KXBTC15M-26MAY060500-00 | no | rejected_actionable | 0.674136 | 0.610000 | 783.254000 | 0.377919 | 0.620318 | False | -126.000000 |
| KXBTC15M-26MAY060545-45 | no | rejected_actionable | 0.626642 | 0.440000 | 807.560000 | 0.323422 | 0.689053 | False | -92.000000 |
| KXBTC15M-26MAY060630-30 | no | rejected_actionable | 0.675344 | 0.660000 | 868.927000 | 0.393798 | 0.762043 | False | -136.000000 |
| KXBTC15M-26MAY060745-45 | no | rejected_actionable | 0.553279 | 0.540000 | 848.000000 | 0.063119 | 1.217111 | True | 88.000000 |
| KXBTC15M-26MAY060815-15 | no | rejected_actionable | 0.540349 | 0.540000 | 804.527000 | 0.089986 | 1.015007 | True | 88.000000 |
| KXBTC15M-26MAY060830-30 | no | rejected_actionable | 0.600730 | 0.590000 | 884.233000 | 0.286154 | 0.943700 | False | -122.000000 |
| KXBTC15M-26MAY060845-45 | no | rejected_actionable | 0.528543 | 0.520000 | 849.050000 | 0.032503 | 1.238079 | True | 92.000000 |
| KXBTC15M-26MAY060900-00 | no | rejected_actionable | 0.586412 | 0.580000 | 809.138000 | 0.220177 | 0.886305 | True | 80.000000 |
| KXBTC15M-26MAY060915-15 | no | rejected_actionable | 0.672099 | 0.600000 | 869.636000 | 0.431641 | 0.831637 | True | 76.000000 |
| KXBTC15M-26MAY061000-00 | no | rejected_actionable | 0.661616 | 0.540000 | 864.383000 | 0.399973 | 0.985410 | True | 88.000000 |
| KXBTC15M-26MAY061015-15 | no | rejected_actionable | 0.595554 | 0.520000 | 883.995000 | 0.274143 | 1.130150 | True | 92.000000 |
| KXBTC15M-26MAY061045-45 | no | rejected_actionable | 0.601767 | 0.570000 | 868.842000 | 0.212683 | 1.191443 | False | -118.000000 |
| KXBTC15M-26MAY061215-15 | no | rejected_actionable | 0.536898 | 0.530000 | 805.930000 | 0.085521 | 1.278404 | False | -110.000000 |
| KXBTC15M-26MAY061245-45 | no | rejected_actionable | 0.555732 | 0.520000 | 884.395000 | 0.180237 | 1.211363 | False | -108.000000 |
| KXBTC15M-26MAY061300-00 | no | rejected_actionable | 0.544132 | 0.540000 | 884.627000 | 0.065489 | 1.327168 | True | 88.000000 |
| KXBTC15M-26MAY061530-30 | no | rejected_actionable | 0.548704 | 0.530000 | 829.956000 | 0.150647 | 0.995442 | False | -110.000000 |
| KXBTC15M-26MAY061700-00 | no | rejected_actionable | 0.547299 | 0.490000 | 759.628000 | 0.145303 | 0.799916 | False | -102.000000 |
| KXBTC15M-26MAY062045-45 | no | rejected_actionable | 0.617920 | 0.510000 | 834.661000 | 0.321769 | 0.590304 | True | 94.000000 |
| KXBTC15M-26MAY062215-15 | no | rejected_actionable | 0.661831 | 0.590000 | 850.282000 | 0.404187 | 0.669869 | True | 78.000000 |
| KXBTC15M-26MAY062245-45 | no | rejected_actionable | 0.605951 | 0.540000 | 841.408000 | 0.278629 | 0.786584 | False | -112.000000 |
| KXBTC15M-26MAY062345-45 | no | rejected_actionable | 0.608623 | 0.460000 | 723.265000 | 0.276153 | 0.675325 | False | -96.000000 |
| KXBTC15M-26MAY070030-30 | no | rejected_actionable | 0.523605 | 0.330000 | 770.113000 | 0.059362 | 0.901651 | False | -70.000000 |
| KXBTC15M-26MAY070045-45 | no | rejected_actionable | 0.582164 | 0.480000 | 810.351000 | 0.187292 | 0.830545 | True | 100.000000 |
| KXBTC15M-26MAY070530-30 | no | rejected_actionable | 0.540822 | 0.480000 | 879.618000 | 0.132673 | 0.894668 | True | 100.000000 |
| KXBTC15M-26MAY070930-30 | no | rejected_actionable | 0.580081 | 0.580000 | 856.599000 | 0.230727 | 0.881411 | False | -120.000000 |
| KXBTC15M-26MAY070945-45 | no | rejected_actionable | 0.532085 | 0.480000 | 860.716000 | 0.067417 | 1.088863 | True | 100.000000 |
| KXBTC15M-26MAY071015-15 | no | rejected_actionable | 0.609894 | 0.600000 | 864.225000 | 0.287274 | 1.102864 | False | -124.000000 |
| KXBTC15M-26MAY071030-30 | no | rejected_actionable | 0.646380 | 0.620000 | 852.539000 | 0.326478 | 1.053270 | True | 72.000000 |
| KXBTC15M-26MAY071100-00 | no | rejected_actionable | 0.578800 | 0.560000 | 817.821000 | 0.236964 | 1.073938 | True | 84.000000 |
| KXBTC15M-26MAY071115-15 | no | rejected_actionable | 0.635838 | 0.620000 | 843.330000 | 0.346131 | 0.982771 | False | -128.000000 |
| KXBTC15M-26MAY071130-30 | no | rejected_actionable | 0.582087 | 0.580000 | 721.923000 | 0.214446 | 0.927686 | True | 80.000000 |
