# v28 Side-Asymmetry Bridge Repair Bakeoff

Diagnostic-only: no live bot changes and no orders.

- Edge floor: `0.02`
- Coverage floor: `75.0`

## Interpretation

- Best repair scorer is prob_edge_stability with net 475.0c and coverage 75.0%.
- Skipped rows net -1293.0c; repair rows net -212.0c.
- This is diagnostic only; frozen future validation is required before promotion.

## Ranking

| rank | scorer | repairs | coverage | net c | delta c | W/L | skipped net c | repair net c |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | prob_edge_stability | 45 | 75.000000 | 475.000000 | 1081.000000 | 73/41 | -1293.000000 | -212.000000 |
| 2 | farthest_boundary | 45 | 75.000000 | 380.000000 | 986.000000 | 75/39 | -1293.000000 | -307.000000 |
| 3 | highest_raw_p | 45 | 75.000000 | 379.000000 | 985.000000 | 75/39 | -1293.000000 | -308.000000 |
| 4 | lowest_recross | 45 | 75.000000 | 331.000000 | 937.000000 | 73/41 | -1293.000000 | -356.000000 |

## Best Repair Rows

| market | source | side | won | net c | raw p | adj p | ask | adj edge | recross | abs d |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.963659 | 0.963659 | 0.700000 | 0.263659 | 0.073753 | 1.543579 |
| KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 25.000000 | 0.942571 | 0.942571 | 0.730000 | 0.212571 | 0.239053 | 1.308547 |
| KXBTC15M-26MAY061000-00 | approved_entry | no | True | 31.000000 | 0.854748 | 0.854748 | 0.650000 | 0.204748 | 0.586664 | 0.901711 |
| KXBTC15M-26MAY060745-45 | rejected_actionable | yes | False | -64.000000 | 0.805231 | 0.805231 | 0.600000 | 0.205231 | 0.420164 | 0.732436 |
| KXBTC15M-26MAY071000-00 | approved_entry | no | True | 27.000000 | 0.851825 | 0.851825 | 0.710000 | 0.141825 | 0.484111 | 0.895147 |
| KXBTC15M-26MAY060900-00 | approved_entry | no | True | 25.000000 | 0.855256 | 0.855256 | 0.730000 | 0.125256 | 0.145613 | 0.858522 |
| KXBTC15M-26MAY071045-45 | approved_entry | no | True | 22.000000 | 0.865260 | 0.865260 | 0.750000 | 0.115260 | 0.469918 | 0.953688 |
| KXBTC15M-26MAY060700-00 | approved_entry | yes | True | 23.000000 | 0.852084 | 0.852084 | 0.750000 | 0.102084 | 0.192044 | 0.872216 |
| KXBTC15M-26MAY060615-15 | approved_entry | yes | True | 23.000000 | 0.852040 | 0.852040 | 0.750000 | 0.102040 | 0.328333 | 0.888798 |
| KXBTC15M-26MAY052045-45 | rejected_actionable | yes | False | -73.000000 | 0.819741 | 0.819741 | 0.700000 | 0.119741 | 0.100982 | 0.766279 |
| KXBTC15M-26MAY071215-15 | rejected_actionable | yes | False | -75.000000 | 0.828282 | 0.828282 | 0.720000 | 0.108282 | 0.487740 | 0.790551 |
| KXBTC15M-26MAY060715-15 | approved_entry | yes | True | 17.000000 | 0.872115 | 0.872115 | 0.810000 | 0.062115 | 0.333271 | 0.965012 |
| KXBTC15M-26MAY071315-15 | approved_entry | yes | True | 20.000000 | 0.850827 | 0.850827 | 0.780000 | 0.070827 | 0.132426 | 0.850077 |
| KXBTC15M-26MAY060815-15 | approved_entry | no | True | 18.000000 | 0.860153 | 0.860153 | 0.790000 | 0.070153 | 0.395024 | 0.900687 |
| KXBTC15M-26MAY061300-00 | approved_entry | yes | False | -82.000000 | 0.860906 | 0.860906 | 0.800000 | 0.060906 | 0.301730 | 0.913273 |
| KXBTC15M-26MAY060115-15 | rejected_actionable | no | True | 24.000000 | 0.819858 | 0.819858 | 0.730000 | 0.089858 | 0.405225 | 0.766642 |
| KXBTC15M-26MAY052200-00 | approved_entry | yes | True | 19.000000 | 0.850777 | 0.850777 | 0.790000 | 0.060777 | 0.404344 | 0.880811 |
| KXBTC15M-26MAY070930-30 | approved_entry | yes | True | 17.000000 | 0.855936 | 0.855936 | 0.800000 | 0.055936 | 0.375669 | 0.878792 |
| KXBTC15M-26MAY071330-30 | rejected_actionable | no | True | 16.000000 | 0.864780 | 0.864780 | 0.820000 | 0.044780 | 0.391694 | 0.927901 |
| KXBTC15M-26MAY060315-15 | rejected_actionable | yes | True | 16.000000 | 0.854395 | 0.854395 | 0.810000 | 0.044395 | 0.163136 | 0.837534 |
| KXBTC15M-26MAY071100-00 | rejected_actionable | yes | False | -84.000000 | 0.853486 | 0.853486 | 0.810000 | 0.043486 | 0.339564 | 0.906587 |
| KXBTC15M-26MAY061530-30 | rejected_actionable | yes | True | 56.000000 | 0.608780 | 0.608780 | 0.400000 | 0.208780 | 0.228156 | 0.226282 |
| KXBTC15M-26MAY060230-30 | rejected_actionable | yes | True | 16.000000 | 0.830361 | 0.830361 | 0.810000 | 0.020361 | 0.160401 | 0.775897 |
| KXBTC15M-26MAY071245-45 | rejected_actionable | yes | False | -53.000000 | 0.636765 | 0.636765 | 0.490000 | 0.146765 | 0.806353 | 0.350996 |
| KXBTC15M-26MAY061245-45 | rejected_actionable | no | False | -72.000000 | 0.740496 | 0.740496 | 0.690000 | 0.050496 | 0.671557 | 0.583513 |
| KXBTC15M-26MAY061115-15 | rejected_actionable | yes | False | -72.000000 | 0.727568 | 0.727568 | 0.690000 | 0.037568 | 0.603892 | 0.509565 |
| KXBTC15M-26MAY060145-45 | rejected_actionable | no | True | 28.000000 | 0.723254 | 0.723254 | 0.690000 | 0.033254 | 0.477849 | 0.517714 |
| KXBTC15M-26MAY061145-45 | rejected_actionable | no | True | 27.000000 | 0.726968 | 0.726968 | 0.700000 | 0.026968 | 0.437401 | 0.540451 |
| KXBTC15M-26MAY060015-15 | rejected_actionable | no | True | 40.000000 | 0.643392 | 0.500000 | 0.560000 | -0.060000 | 0.509785 | 0.322451 |
| KXBTC15M-26MAY060000-00 | rejected_actionable | no | False | -67.000000 | 0.678147 | 0.678147 | 0.630000 | 0.048147 | 0.435236 | 0.417064 |
| KXBTC15M-26MAY061415-15 | rejected_actionable | no | True | 34.000000 | 0.661034 | 0.500000 | 0.620000 | -0.120000 | 0.655098 | 0.381932 |
| KXBTC15M-26MAY061215-15 | rejected_actionable | no | False | -62.000000 | 0.614405 | 0.614405 | 0.580000 | 0.034405 | 0.815053 | 0.273193 |
| KXBTC15M-26MAY060845-45 | rejected_actionable | no | True | 37.000000 | 0.605958 | 0.500000 | 0.590000 | -0.090000 | 0.940026 | 0.234273 |
| KXBTC15M-26MAY062145-45 | rejected_actionable | no | False | -14.000000 | 0.783823 | 0.783823 | 0.120000 | 0.663823 | 0.195824 | 0.666418 |
| KXBTC15M-26MAY052245-45 | approved_entry | no | False | -42.000000 | 0.916618 | 0.916618 | 0.400000 | 0.516618 | 0.141331 | 1.218811 |
| KXBTC15M-26MAY062015-15 | approved_entry | no | True | 56.000000 | 0.871622 | 0.871622 | 0.420000 | 0.451622 | 0.094396 | 0.916460 |
| KXBTC15M-26MAY052345-45 | rejected_actionable | yes | False | -36.000000 | 0.805869 | 0.805869 | 0.320000 | 0.485869 | 0.171066 | 0.746818 |
| KXBTC15M-26MAY061700-00 | rejected_actionable | no | False | -42.000000 | 0.788347 | 0.788347 | 0.380000 | 0.408347 | 0.196391 | 0.665443 |
| KXBTC15M-26MAY062215-15 | approved_entry | no | True | 33.000000 | 0.889241 | 0.889241 | 0.650000 | 0.239241 | 0.319525 | 1.024084 |
| KXBTC15M-26MAY052115-15 | approved_entry | yes | True | 19.000000 | 0.941543 | 0.941543 | 0.780000 | 0.161543 | 0.215078 | 1.395955 |
| KXBTC15M-26MAY062045-45 | approved_entry | no | True | 18.000000 | 0.925277 | 0.925277 | 0.800000 | 0.125277 | 0.180083 | 1.216600 |
| KXBTC15M-26MAY061015-15 | approved_entry | no | True | 30.000000 | 0.859312 | 0.859312 | 0.680000 | 0.179312 | 0.581489 | 0.912125 |
| KXBTC15M-26MAY052000-00 | rejected_actionable | yes | False | -58.000000 | 0.767756 | 0.767756 | 0.540000 | 0.227756 | 0.110461 | 0.639186 |
| KXBTC15M-26MAY060500-00 | approved_entry | yes | True | 18.000000 | 0.904525 | 0.904525 | 0.790000 | 0.114525 | 0.224287 | 1.081154 |
| KXBTC15M-26MAY060245-45 | approved_entry | yes | True | 21.000000 | 0.877828 | 0.877828 | 0.760000 | 0.117828 | 0.058673 | 0.931315 |
