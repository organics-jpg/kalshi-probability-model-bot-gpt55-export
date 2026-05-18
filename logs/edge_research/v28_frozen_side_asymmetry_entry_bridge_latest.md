# v28 Frozen Side-Asymmetry Entry Bridge

Research-only; no live bot changes and no orders.

- Candidate: `target_coverage_side_asymmetry_adjusted_edge2pp_strict_farthest_boundary_repair`
- Freeze timestamp UTC: `2026-05-06T13:24:47.507897+00:00`
- Edge floor: `0.02`
- Repair ranker: `farthest_boundary`
- Future denominator: `96`
- Candidate live-ready: `True`
- Blockers: `none`

## Current Read

- Frozen side-asymmetry entry bridge has denominator 96, candidate entries/settled 72/72.
- Coverage 75.0%; candidate net 233.0c versus target 142.0c; delta 91.0c.
- Skipped rows were 12/11 for -420.0c; repairs were 13/9 for -329.0c.
- Strict repairs chosen/needed/available: 22/22/17.
- Promotion blockers: none.

## Scorecard

| surface | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| target_summary | 73 | 73 | 43/30 | 76.041667 | 142.000000 | 1.945205 |
| candidate_summary | 72 | 72 | 44/28 | 75.000000 | 233.000000 | 3.236111 |
| skipped_summary | 23 | 23 | 12/11 | 23.958333 | -420.000000 | -18.260870 |
| repair_summary | 22 | 22 | 13/9 | 22.916667 | -329.000000 | -14.954545 |

## Skipped Rows

| market | source | side | won | net c | raw p | adj p | adj edge | ask | stc | abs d | recross |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY061015-15 | rejected_actionable | no | True | 92.000000 | 0.595554 | 0.500000 | -0.020000 | 0.520000 | 883.995000 | 0.274143 | 1.130150 |
| KXBTC15M-26MAY061030-30 | rejected_actionable | yes | True | 74.000000 | 0.618153 | 0.618153 | 0.008153 | 0.610000 | 868.942000 | 0.232373 | 1.168280 |
| KXBTC15M-26MAY061045-45 | rejected_actionable | no | False | -118.000000 | 0.601767 | 0.500000 | -0.070000 | 0.570000 | 868.842000 | 0.212683 | 1.191443 |
| KXBTC15M-26MAY061100-00 | rejected_actionable | yes | False | -151.000000 | 0.740374 | 0.500000 | -0.240000 | 0.740000 | 865.321000 | 0.597049 | 0.809587 |
| KXBTC15M-26MAY061130-30 | rejected_actionable | yes | True | 66.000000 | 0.653101 | 0.500000 | -0.150000 | 0.650000 | 883.089000 | 0.341283 | 1.056221 |
| KXBTC15M-26MAY061230-30 | rejected_actionable | yes | False | -140.000000 | 0.681329 | 0.500000 | -0.180000 | 0.680000 | 829.291000 | 0.451740 | 0.862457 |
| KXBTC15M-26MAY061430-30 | rejected_actionable | yes | True | 62.000000 | 0.678512 | 0.500000 | -0.170000 | 0.670000 | 864.426000 | 0.424290 | 0.893555 |
| KXBTC15M-26MAY061445-45 | rejected_actionable | no | True | 55.000000 | 0.724164 | 0.500000 | -0.210000 | 0.710000 | 884.401000 | 0.536135 | 0.800263 |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -124.000000 | 0.610883 | 0.610883 | 0.010883 | 0.600000 | 717.804000 | 0.229994 | 0.723320 |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 70.000000 | 0.631665 | 0.631665 | 0.001665 | 0.630000 | 505.823000 | 0.294854 | 0.450319 |
| KXBTC15M-26MAY061700-00 | rejected_actionable | no | False | -102.000000 | 0.547299 | 0.500000 | 0.010000 | 0.490000 | 759.628000 | 0.145303 | 0.799916 |
| KXBTC15M-26MAY062015-15 | rejected_actionable | yes | False | -106.000000 | 0.526847 | 0.526847 | 0.016847 | 0.510000 | 869.507000 | 0.086972 | 0.736601 |
| KXBTC15M-26MAY062045-45 | rejected_actionable | no | True | 94.000000 | 0.617920 | 0.500000 | -0.010000 | 0.510000 | 834.661000 | 0.321769 | 0.590304 |
| KXBTC15M-26MAY062145-45 | rejected_actionable | yes | True | 82.000000 | 0.600378 | 0.500000 | -0.070000 | 0.570000 | 800.015000 | 0.250555 | 0.820982 |
| KXBTC15M-26MAY062215-15 | rejected_actionable | no | True | 78.000000 | 0.661831 | 0.500000 | -0.090000 | 0.590000 | 850.282000 | 0.404187 | 0.669869 |
| KXBTC15M-26MAY062245-45 | rejected_actionable | no | False | -112.000000 | 0.605951 | 0.500000 | -0.040000 | 0.540000 | 841.408000 | 0.278629 | 0.786584 |
| KXBTC15M-26MAY070130-30 | rejected_actionable | no | True | 78.000000 | 0.604140 | 0.604140 | 0.014140 | 0.590000 | 585.641000 | 0.227698 | 0.544225 |
| KXBTC15M-26MAY070715-15 | rejected_actionable | yes | True | 94.000000 | 0.560435 | 0.500000 | -0.010000 | 0.510000 | 812.253000 | 0.157545 | 0.877232 |
| KXBTC15M-26MAY070900-00 | rejected_actionable | yes | True | 86.000000 | 0.597604 | 0.500000 | -0.050000 | 0.550000 | 773.230000 | 0.238237 | 0.771689 |
| KXBTC15M-26MAY071015-15 | rejected_actionable | no | False | -124.000000 | 0.609894 | 0.500000 | -0.100000 | 0.600000 | 864.225000 | 0.287274 | 1.102864 |
| KXBTC15M-26MAY071115-15 | rejected_actionable | no | False | -128.000000 | 0.635838 | 0.635838 | 0.015838 | 0.620000 | 843.330000 | 0.346131 | 0.982771 |
| KXBTC15M-26MAY071200-00 | rejected_actionable | yes | False | -124.000000 | 0.606055 | 0.500000 | -0.100000 | 0.600000 | 793.821000 | 0.250754 | 1.096302 |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -122.000000 | 0.636040 | 0.500000 | -0.090000 | 0.590000 | 842.515000 | 0.289227 | 1.011545 |

## Repair Rows

| market | source | side | won | net c | raw p | adj p | adj edge | ask | stc | abs d | recross |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.963659 | 0.963659 | 0.263659 | 0.700000 | 279.632000 | 1.543579 | 0.073753 |
| KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 25.000000 | 0.942571 | 0.942571 | 0.212571 | 0.730000 | 774.658000 | 1.308547 | 0.239053 |
| KXBTC15M-26MAY071045-45 | approved_entry | no | True | 22.000000 | 0.865260 | 0.865260 | 0.115260 | 0.750000 | 737.262000 | 0.953688 | 0.469918 |
| KXBTC15M-26MAY071000-00 | approved_entry | no | True | 25.000000 | 0.861629 | 0.861629 | 0.131629 | 0.730000 | 841.121000 | 0.928896 | 0.483183 |
| KXBTC15M-26MAY071330-30 | rejected_actionable | no | True | 16.000000 | 0.864780 | 0.864780 | 0.044780 | 0.820000 | 689.739000 | 0.927901 | 0.391694 |
| KXBTC15M-26MAY061300-00 | approved_entry | yes | False | -82.000000 | 0.860906 | 0.860906 | 0.060906 | 0.800000 | 486.266000 | 0.913273 | 0.301730 |
| KXBTC15M-26MAY071100-00 | rejected_actionable | yes | False | -84.000000 | 0.853486 | 0.853486 | 0.043486 | 0.810000 | 500.459000 | 0.906587 | 0.339564 |
| KXBTC15M-26MAY071215-15 | approved_entry | no | True | 18.000000 | 0.855912 | 0.855912 | 0.055912 | 0.800000 | 361.476000 | 0.904673 | 0.237930 |
| KXBTC15M-26MAY061000-00 | approved_entry | no | True | 31.000000 | 0.854748 | 0.854748 | 0.204748 | 0.650000 | 835.709000 | 0.901711 | 0.586664 |
| KXBTC15M-26MAY071315-15 | approved_entry | yes | True | 20.000000 | 0.850827 | 0.850827 | 0.070827 | 0.780000 | 211.581000 | 0.850077 | 0.132426 |
| KXBTC15M-26MAY061245-45 | rejected_actionable | no | False | -72.000000 | 0.740496 | 0.740496 | 0.050496 | 0.690000 | 738.970000 | 0.583513 | 0.671557 |
| KXBTC15M-26MAY061145-45 | rejected_actionable | no | True | 27.000000 | 0.726968 | 0.726968 | 0.026968 | 0.700000 | 442.779000 | 0.540451 | 0.437401 |
| KXBTC15M-26MAY061530-30 | rejected_actionable | yes | True | 27.000000 | 0.735905 | 0.735905 | 0.035905 | 0.700000 | 273.267000 | 0.527347 | 0.218517 |
| KXBTC15M-26MAY070930-30 | rejected_actionable | no | False | -65.000000 | 0.656126 | 0.656126 | 0.046126 | 0.610000 | 89.291000 | 0.394183 | 0.081541 |
| KXBTC15M-26MAY071245-45 | rejected_actionable | yes | False | -53.000000 | 0.636765 | 0.636765 | 0.146765 | 0.490000 | 678.736000 | 0.350996 | 0.806353 |
| KXBTC15M-26MAY061115-15 | rejected_actionable | yes | False | -63.000000 | 0.647368 | 0.647368 | 0.057368 | 0.590000 | 272.028000 | 0.324579 | 0.338898 |
| KXBTC15M-26MAY061215-15 | rejected_actionable | no | False | -62.000000 | 0.614405 | 0.614405 | 0.034405 | 0.580000 | 621.427000 | 0.273193 | 0.815053 |
| KXBTC15M-26MAY062045-45 | approved_entry | no | True | 18.000000 | 0.925277 | 0.925277 | 0.125277 | 0.800000 | 611.277000 | 1.216600 | 0.180083 |
| KXBTC15M-26MAY062215-15 | approved_entry | no | True | 33.000000 | 0.889241 | 0.889241 | 0.239241 | 0.650000 | 761.901000 | 1.024084 | 0.319525 |
| KXBTC15M-26MAY061130-30 | approved_entry | yes | True | 17.000000 | 0.877418 | 0.877418 | 0.077418 | 0.800000 | 832.260000 | 0.989346 | 0.536330 |
| KXBTC15M-26MAY062015-15 | approved_entry | yes | False | -71.000000 | 0.885657 | 0.885657 | 0.215657 | 0.670000 | 90.328000 | 0.973796 | 0.032091 |
| KXBTC15M-26MAY061100-00 | approved_entry | no | True | 16.000000 | 0.868814 | 0.868814 | 0.058814 | 0.810000 | 476.106000 | 0.935905 | 0.331063 |
