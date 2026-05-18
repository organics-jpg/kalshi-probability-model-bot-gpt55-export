# v28 Composite False-Conviction Repair Bakeoff

Diagnostic-only: replace composite false-conviction rows with clean observable repair rows.

- Danger rule: `composite false-conviction zone from v28_false_conviction_physics_audit`
- Coverage floor: `75.0`

## Interpretation

- Composite false-conviction rows are 34 settled for -1000.0c.
- Best ex-ante repair scorer is prob_edge_stability with coverage 75.67567567567568%, net 450.0c, delta 944.0c.
- This is diagnostic only; a separate frozen validator is required before live use.

## Ranking

| rank | scorer | repairs | coverage | net c | delta c | W/L | danger net c | repair net c |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | prob_edge_stability | 37 | 75.675676 | 450.000000 | 944.000000 | 58/26 | -1000.000000 | -56.000000 |
| 2 | farthest_boundary | 37 | 75.675676 | 400.000000 | 894.000000 | 60/24 | -1000.000000 | -106.000000 |
| 3 | lowest_recross | 37 | 75.675676 | 390.000000 | 884.000000 | 59/25 | -1000.000000 | -116.000000 |
| 4 | highest_raw_p | 37 | 75.675676 | 298.000000 | 792.000000 | 59/25 | -1000.000000 | -208.000000 |
| 5 | edge_minus_price_friction | 37 | 75.675676 | 153.000000 | 647.000000 | 53/31 | -1000.000000 | -353.000000 |
| 6 | chronological | 37 | 75.675676 | -57.000000 | 437.000000 | 53/31 | -1000.000000 | -563.000000 |

## Best Scorer Chosen Rows

| market | source | side | won | net c | p | ask | edge | recross | abs d | score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 25.000000 | 0.942571 | 0.730000 | 0.212571 | 0.239053 | 1.308547 | 1.314902 |
| KXBTC15M-26MAY061000-00 | approved_entry | no | True | 31.000000 | 0.854748 | 0.650000 | 0.204748 | 0.586664 | 0.901711 | 1.177622 |
| KXBTC15M-26MAY060745-45 | rejected_actionable | yes | False | -64.000000 | 0.805231 | 0.600000 | 0.205231 | 0.420164 | 0.732436 | 1.128691 |
| KXBTC15M-26MAY060900-00 | approved_entry | no | True | 25.000000 | 0.855256 | 0.730000 | 0.125256 | 0.145613 | 0.858522 | 1.078785 |
| KXBTC15M-26MAY060700-00 | approved_entry | yes | True | 23.000000 | 0.852084 | 0.750000 | 0.102084 | 0.192044 | 0.872216 | 1.039219 |
| KXBTC15M-26MAY060615-15 | approved_entry | yes | True | 23.000000 | 0.852040 | 0.750000 | 0.102040 | 0.328333 | 0.888798 | 1.033123 |
| KXBTC15M-26MAY052045-45 | rejected_actionable | yes | False | -73.000000 | 0.819741 | 0.700000 | 0.119741 | 0.100982 | 0.766279 | 1.032617 |
| KXBTC15M-26MAY060715-15 | approved_entry | yes | True | 17.000000 | 0.872115 | 0.810000 | 0.062115 | 0.333271 | 0.965012 | 0.996875 |
| KXBTC15M-26MAY060815-15 | approved_entry | no | True | 18.000000 | 0.860153 | 0.790000 | 0.070153 | 0.395024 | 0.900687 | 0.990666 |
| KXBTC15M-26MAY061300-00 | approved_entry | yes | False | -82.000000 | 0.860906 | 0.800000 | 0.060906 | 0.301730 | 0.913273 | 0.982842 |
| KXBTC15M-26MAY060115-15 | rejected_actionable | no | True | 24.000000 | 0.819858 | 0.730000 | 0.089858 | 0.405225 | 0.766642 | 0.972716 |
| KXBTC15M-26MAY052200-00 | approved_entry | yes | True | 19.000000 | 0.850777 | 0.790000 | 0.060777 | 0.404344 | 0.880811 | 0.965766 |
| KXBTC15M-26MAY060315-15 | rejected_actionable | yes | True | 16.000000 | 0.854395 | 0.810000 | 0.044395 | 0.163136 | 0.837534 | 0.954707 |
| KXBTC15M-26MAY061530-30 | rejected_actionable | yes | True | 56.000000 | 0.608780 | 0.400000 | 0.208780 | 0.228156 | 0.226282 | 0.921856 |
| KXBTC15M-26MAY060230-30 | rejected_actionable | yes | True | 16.000000 | 0.830361 | 0.810000 | 0.020361 | 0.160401 | 0.775897 | 0.891677 |
| KXBTC15M-26MAY061245-45 | rejected_actionable | no | False | -72.000000 | 0.740496 | 0.690000 | 0.050496 | 0.671557 | 0.583513 | 0.811838 |
| KXBTC15M-26MAY061115-15 | rejected_actionable | yes | False | -72.000000 | 0.727568 | 0.690000 | 0.037568 | 0.603892 | 0.509565 | 0.779204 |
| KXBTC15M-26MAY060145-45 | rejected_actionable | no | True | 28.000000 | 0.723254 | 0.690000 | 0.033254 | 0.477849 | 0.517714 | 0.775128 |
| KXBTC15M-26MAY061145-45 | rejected_actionable | no | True | 27.000000 | 0.726968 | 0.700000 | 0.026968 | 0.437401 | 0.540451 | 0.772573 |
| KXBTC15M-26MAY060015-15 | rejected_actionable | no | True | 40.000000 | 0.643392 | 0.560000 | 0.083392 | 0.509785 | 0.322451 | 0.759113 |
| KXBTC15M-26MAY060000-00 | rejected_actionable | no | False | -67.000000 | 0.678147 | 0.630000 | 0.048147 | 0.435236 | 0.417064 | 0.749459 |
| KXBTC15M-26MAY061415-15 | rejected_actionable | no | True | 34.000000 | 0.661034 | 0.620000 | 0.041034 | 0.655098 | 0.381932 | 0.708927 |
| KXBTC15M-26MAY061215-15 | rejected_actionable | no | False | -62.000000 | 0.614405 | 0.580000 | 0.034405 | 0.815053 | 0.273193 | 0.638920 |
| KXBTC15M-26MAY060845-45 | rejected_actionable | no | True | 37.000000 | 0.605958 | 0.590000 | 0.015958 | 0.940026 | 0.234273 | 0.594607 |
| KXBTC15M-26MAY060330-30 | approved_entry | no | False | -11.000000 | 0.999788 | 0.090000 | 0.909788 | 0.002807 | 3.991247 | 2.563892 |
| KXBTC15M-26MAY052245-45 | approved_entry | no | False | -42.000000 | 0.916618 | 0.400000 | 0.516618 | 0.141331 | 1.218811 | 1.745419 |
| KXBTC15M-26MAY052345-45 | rejected_actionable | yes | False | -36.000000 | 0.805869 | 0.320000 | 0.485869 | 0.171066 | 0.746818 | 1.563460 |
| KXBTC15M-26MAY061700-00 | rejected_actionable | no | False | -42.000000 | 0.788347 | 0.380000 | 0.408347 | 0.196391 | 0.665443 | 1.424320 |
| KXBTC15M-26MAY061945-45 | rejected_actionable | no | True | 51.000000 | 0.798947 | 0.450000 | 0.348947 | 0.396347 | 0.680058 | 1.336553 |
| KXBTC15M-26MAY052100-00 | approved_entry | yes | True | 42.000000 | 0.856314 | 0.560000 | 0.296314 | 0.241416 | 0.903393 | 1.333884 |
| KXBTC15M-26MAY062215-15 | approved_entry | no | True | 33.000000 | 0.889241 | 0.650000 | 0.239241 | 0.319525 | 1.024084 | 1.283330 |
| KXBTC15M-26MAY052115-15 | approved_entry | yes | True | 19.000000 | 0.941543 | 0.780000 | 0.161543 | 0.215078 | 1.395955 | 1.242901 |
| KXBTC15M-26MAY060800-00 | approved_entry | yes | True | 32.000000 | 0.874265 | 0.660000 | 0.214265 | 0.130377 | 0.931829 | 1.235735 |
| KXBTC15M-26MAY062345-45 | rejected_actionable | no | False | -60.000000 | 0.806238 | 0.560000 | 0.246238 | 0.264802 | 0.726970 | 1.198703 |
| KXBTC15M-26MAY052030-30 | rejected_actionable | yes | False | -57.000000 | 0.781441 | 0.530000 | 0.251441 | 0.541297 | 0.690834 | 1.166079 |
| KXBTC15M-26MAY062045-45 | approved_entry | no | True | 18.000000 | 0.925277 | 0.800000 | 0.125277 | 0.180083 | 1.216600 | 1.165018 |
| KXBTC15M-26MAY061015-15 | approved_entry | no | True | 30.000000 | 0.859312 | 0.680000 | 0.179312 | 0.581489 | 0.912125 | 1.144812 |
