# v28 Repair Scoring Bakeoff

Diagnostic-only: ranks repair rows by observable ex-ante scores.

- Danger rule: `paid_price_fragile OR weak_boundary_turbulence`
- Coverage floor: `75.0`

## Interpretation

- Best ex-ante scorer is highest_raw_edge with net -170.0c and delta 674.0c.
- Best coverage is 75.29411764705883%.
- This is still diagnostic until frozen forward validation exists.

## Ranking

| rank | scorer | repairs | coverage | net c | delta c | W/L | repair net c |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | highest_raw_edge | 32 | 75.294118 | -170.000000 | 674.000000 | 42/21 | 39.000000 |
| 2 | edge_minus_price_friction | 32 | 75.294118 | -170.000000 | 674.000000 | 42/21 | 39.000000 |
| 3 | raw_p_plus_2edge | 32 | 75.294118 | -174.000000 | 670.000000 | 43/20 | 35.000000 |
| 4 | lowest_recross | 32 | 75.294118 | -197.000000 | 647.000000 | 44/19 | 12.000000 |
| 5 | farthest_boundary | 32 | 75.294118 | -246.000000 | 598.000000 | 44/19 | -37.000000 |
| 6 | cheapest_ask | 32 | 75.294118 | -283.000000 | 561.000000 | 39/24 | -74.000000 |
| 7 | highest_raw_p | 32 | 75.294118 | -446.000000 | 398.000000 | 42/21 | -237.000000 |
| 8 | chronological | 32 | 75.294118 | -701.000000 | 143.000000 | 37/26 | -492.000000 |

## Best Scorer Chosen Rows

| market | source | side | won | net c | p | ask | edge | recross | abs d | score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY061530-30 | rejected_actionable | yes | True | 56.000000 | 0.608780 | 0.400000 | 0.208780 | 0.228156 | 0.226282 | 0.208780 |
| KXBTC15M-26MAY060745-45 | rejected_actionable | yes | False | -64.000000 | 0.805231 | 0.600000 | 0.205231 | 0.420164 | 0.732436 | 0.205231 |
| KXBTC15M-26MAY061000-00 | approved_entry | no | True | 31.000000 | 0.854748 | 0.650000 | 0.204748 | 0.586664 | 0.901711 | 0.204748 |
| KXBTC15M-26MAY060900-00 | approved_entry | no | True | 25.000000 | 0.855256 | 0.730000 | 0.125256 | 0.145613 | 0.858522 | 0.125256 |
| KXBTC15M-26MAY052045-45 | rejected_actionable | yes | False | -73.000000 | 0.819741 | 0.700000 | 0.119741 | 0.100982 | 0.766279 | 0.119741 |
| KXBTC15M-26MAY061300-00 | rejected_actionable | no | True | 42.000000 | 0.643026 | 0.540000 | 0.103026 | 0.734550 | 0.311542 | 0.103026 |
| KXBTC15M-26MAY060700-00 | approved_entry | yes | True | 23.000000 | 0.852084 | 0.750000 | 0.102084 | 0.192044 | 0.872216 | 0.102084 |
| KXBTC15M-26MAY060615-15 | approved_entry | yes | True | 23.000000 | 0.852040 | 0.750000 | 0.102040 | 0.328333 | 0.888798 | 0.102040 |
| KXBTC15M-26MAY060315-15 | rejected_actionable | yes | True | 34.000000 | 0.718049 | 0.620000 | 0.098049 | 0.406023 | 0.504701 | 0.098049 |
| KXBTC15M-26MAY060115-15 | rejected_actionable | no | True | 24.000000 | 0.819858 | 0.730000 | 0.089858 | 0.405225 | 0.766642 | 0.089858 |
| KXBTC15M-26MAY060015-15 | rejected_actionable | no | True | 40.000000 | 0.643392 | 0.560000 | 0.083392 | 0.509785 | 0.322451 | 0.083392 |
| KXBTC15M-26MAY060715-15 | rejected_actionable | yes | True | 27.000000 | 0.781432 | 0.700000 | 0.081432 | 0.506860 | 0.703124 | 0.081432 |
| KXBTC15M-26MAY060815-15 | approved_entry | no | True | 18.000000 | 0.860153 | 0.790000 | 0.070153 | 0.395024 | 0.900687 | 0.070153 |
| KXBTC15M-26MAY052200-00 | approved_entry | yes | True | 19.000000 | 0.850777 | 0.790000 | 0.060777 | 0.404344 | 0.880811 | 0.060777 |
| KXBTC15M-26MAY061115-15 | rejected_actionable | yes | False | -63.000000 | 0.647368 | 0.590000 | 0.057368 | 0.338898 | 0.324579 | 0.057368 |
| KXBTC15M-26MAY061245-45 | rejected_actionable | no | False | -72.000000 | 0.740496 | 0.690000 | 0.050496 | 0.671557 | 0.583513 | 0.050496 |
| KXBTC15M-26MAY060000-00 | rejected_actionable | no | False | -67.000000 | 0.678147 | 0.630000 | 0.048147 | 0.435236 | 0.417064 | 0.048147 |
| KXBTC15M-26MAY060230-30 | rejected_actionable | no | False | -71.000000 | 0.717693 | 0.670000 | 0.047693 | 0.506108 | 0.518373 | 0.047693 |
| KXBTC15M-26MAY060145-45 | rejected_actionable | no | True | 37.000000 | 0.632841 | 0.590000 | 0.042841 | 0.564323 | 0.322984 | 0.042841 |
| KXBTC15M-26MAY061415-15 | rejected_actionable | no | True | 34.000000 | 0.661034 | 0.620000 | 0.041034 | 0.655098 | 0.381932 | 0.041034 |
| KXBTC15M-26MAY061145-45 | rejected_actionable | yes | False | -69.000000 | 0.685968 | 0.650000 | 0.035968 | 0.729351 | 0.428045 | 0.035968 |
| KXBTC15M-26MAY061215-15 | rejected_actionable | no | False | -62.000000 | 0.614405 | 0.580000 | 0.034405 | 0.815053 | 0.273193 | 0.034405 |
| KXBTC15M-26MAY060845-45 | rejected_actionable | no | True | 37.000000 | 0.605958 | 0.590000 | 0.015958 | 0.940026 | 0.234273 | 0.015958 |
| KXBTC15M-26MAY052345-45 | rejected_actionable | yes | False | -36.000000 | 0.805869 | 0.320000 | 0.485869 | 0.171066 | 0.746818 | 0.485869 |
| KXBTC15M-26MAY052100-00 | approved_entry | yes | True | 42.000000 | 0.856314 | 0.560000 | 0.296314 | 0.241416 | 0.903393 | 0.296314 |
| KXBTC15M-26MAY052030-30 | rejected_actionable | yes | False | -57.000000 | 0.781441 | 0.530000 | 0.251441 | 0.541297 | 0.690834 | 0.251441 |
| KXBTC15M-26MAY060800-00 | approved_entry | yes | True | 32.000000 | 0.874265 | 0.660000 | 0.214265 | 0.130377 | 0.931829 | 0.214265 |
| KXBTC15M-26MAY061015-15 | approved_entry | no | True | 30.000000 | 0.859312 | 0.680000 | 0.179312 | 0.581489 | 0.912125 | 0.179312 |
| KXBTC15M-26MAY052115-15 | approved_entry | yes | True | 19.000000 | 0.941543 | 0.780000 | 0.161543 | 0.215078 | 1.395955 | 0.161543 |
| KXBTC15M-26MAY060345-45 | rejected_actionable | no | True | 32.000000 | 0.794409 | 0.640000 | 0.154409 | 0.420554 | 0.656178 | 0.154409 |
| KXBTC15M-26MAY060515-15 | approved_entry | no | True | 23.000000 | 0.884180 | 0.740000 | 0.144180 | 0.123272 | 0.969762 | 0.144180 |
| KXBTC15M-26MAY060930-30 | approved_entry | no | True | 25.000000 | 0.851733 | 0.730000 | 0.121733 | 0.353780 | 0.859473 | 0.121733 |
