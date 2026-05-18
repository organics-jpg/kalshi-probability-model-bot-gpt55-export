# v28 Coverage Repair Pool Diagnostic

Diagnostic-only: skip danger-tagged target rows and repair coverage from clean opportunities.

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Forward denominator: `152`
- Needed repairs for floor: `39`
- Available missed-market repairs: `33`

## Interpretation

- Removing danger rows leaves 75 entries; 39 repairs are needed to restore the 75.0% floor.
- Clean repairs available from otherwise missed markets: 33.
- Candidate coverage 75.0% with net -513.0c versus target net -606.0c.

## Summaries

| slice | entries | settled | W/L | coverage | net c | avg net c |
|---|---:|---:|---:|---:|---:|---:|
| target | 112 | 112 | 64/48 | 73.684211 | -606.000000 | -5.410714 |
| danger_removed | 37 | 37 | 18/19 | 24.342105 | -677.000000 | -18.297297 |
| kept_after_danger_skip | 75 | 75 | 46/29 | 49.342105 | 71.000000 | 0.946667 |
| repair_rows | 39 | 39 | 21/18 | 25.657895 | -584.000000 | -14.974359 |
| kept_plus_repair | 114 | 114 | 67/47 | 75.000000 | -513.000000 | -4.500000 |

## Chosen Repairs

| market | source | side | won | net c | p | ask | edge |
|---|---|---|---|---:|---:|---:|---:|
| KXBTC15M-26MAY052045-45 | rejected_actionable | yes | False | -61.000000 | 0.658389 | 0.570000 | 0.088389 |
| KXBTC15M-26MAY052200-00 | approved_entry | yes | True | 19.000000 | 0.850777 | 0.790000 | 0.060777 |
| KXBTC15M-26MAY060000-00 | rejected_actionable | no | False | -67.000000 | 0.678147 | 0.630000 | 0.048147 |
| KXBTC15M-26MAY060015-15 | rejected_actionable | no | True | 40.000000 | 0.643392 | 0.560000 | 0.083392 |
| KXBTC15M-26MAY060115-15 | rejected_actionable | no | True | 28.000000 | 0.726160 | 0.680000 | 0.046160 |
| KXBTC15M-26MAY060145-45 | rejected_actionable | no | True | 38.000000 | 0.602935 | 0.580000 | 0.022935 |
| KXBTC15M-26MAY060230-30 | rejected_actionable | no | False | -71.000000 | 0.717693 | 0.670000 | 0.047693 |
| KXBTC15M-26MAY060315-15 | rejected_actionable | yes | True | 24.000000 | 0.783841 | 0.730000 | 0.053841 |
| KXBTC15M-26MAY060615-15 | rejected_actionable | yes | True | 24.000000 | 0.777865 | 0.730000 | 0.047865 |
| KXBTC15M-26MAY060700-00 | rejected_actionable | no | False | -63.000000 | 0.600088 | 0.590000 | 0.010088 |
| KXBTC15M-26MAY060715-15 | rejected_actionable | yes | True | 31.000000 | 0.706716 | 0.650000 | 0.056716 |
| KXBTC15M-26MAY060745-45 | rejected_actionable | yes | False | -57.000000 | 0.627260 | 0.530000 | 0.097260 |
| KXBTC15M-26MAY060815-15 | rejected_actionable | no | True | 34.000000 | 0.643430 | 0.620000 | 0.023430 |
| KXBTC15M-26MAY060845-45 | rejected_actionable | no | True | 37.000000 | 0.605958 | 0.590000 | 0.015958 |
| KXBTC15M-26MAY060900-00 | rejected_actionable | yes | False | -80.000000 | 0.802760 | 0.770000 | 0.032760 |
| KXBTC15M-26MAY061000-00 | rejected_actionable | no | True | 42.000000 | 0.661616 | 0.540000 | 0.121616 |
| KXBTC15M-26MAY061115-15 | rejected_actionable | yes | False | -60.000000 | 0.600113 | 0.560000 | 0.040113 |
| KXBTC15M-26MAY061145-45 | rejected_actionable | yes | False | -69.000000 | 0.685968 | 0.650000 | 0.035968 |
| KXBTC15M-26MAY061215-15 | rejected_actionable | no | False | -62.000000 | 0.614405 | 0.580000 | 0.034405 |
| KXBTC15M-26MAY061245-45 | rejected_actionable | no | False | -72.000000 | 0.740496 | 0.690000 | 0.050496 |
| KXBTC15M-26MAY061300-00 | rejected_actionable | no | True | 39.000000 | 0.621955 | 0.570000 | 0.051955 |
| KXBTC15M-26MAY061415-15 | rejected_actionable | no | True | 34.000000 | 0.661034 | 0.620000 | 0.041034 |
| KXBTC15M-26MAY061530-30 | rejected_actionable | yes | True | 27.000000 | 0.735905 | 0.700000 | 0.035905 |
| KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 25.000000 | 0.942571 | 0.730000 | 0.212571 |
| KXBTC15M-26MAY070015-15 | rejected_actionable | no | False | -70.000000 | 0.720379 | 0.660000 | 0.060379 |
| KXBTC15M-26MAY070930-30 | rejected_actionable | no | False | -66.000000 | 0.652332 | 0.620000 | 0.032332 |
| KXBTC15M-26MAY071000-00 | rejected_actionable | no | True | 30.000000 | 0.720981 | 0.660000 | 0.060981 |
| KXBTC15M-26MAY071045-45 | rejected_actionable | no | True | 24.000000 | 0.826507 | 0.730000 | 0.096507 |
| KXBTC15M-26MAY071100-00 | rejected_actionable | yes | False | -63.000000 | 0.626780 | 0.590000 | 0.036780 |
| KXBTC15M-26MAY071215-15 | rejected_actionable | yes | False | -63.000000 | 0.615913 | 0.590000 | 0.025913 |
| KXBTC15M-26MAY071245-45 | rejected_actionable | yes | False | -60.000000 | 0.624800 | 0.560000 | 0.064800 |
| KXBTC15M-26MAY071315-15 | rejected_actionable | yes | True | 27.000000 | 0.743772 | 0.700000 | 0.043772 |
| KXBTC15M-26MAY071330-30 | rejected_actionable | no | True | 20.000000 | 0.810790 | 0.770000 | 0.040790 |
| KXBTC15M-26MAY052030-30 | rejected_actionable | yes | False | -57.000000 | 0.781441 | 0.530000 | 0.251441 |
| KXBTC15M-26MAY052100-00 | rejected_actionable | no | False | -77.000000 | 0.806447 | 0.740000 | 0.066447 |
| KXBTC15M-26MAY052115-15 | approved_entry | yes | True | 19.000000 | 0.941543 | 0.780000 | 0.161543 |
| KXBTC15M-26MAY052345-45 | rejected_actionable | no | True | 42.000000 | 0.640384 | 0.540000 | 0.100384 |
| KXBTC15M-26MAY060100-00 | rejected_actionable | yes | False | -85.000000 | 0.851837 | 0.820000 | 0.031837 |
| KXBTC15M-26MAY060200-00 | rejected_actionable | yes | True | 15.000000 | 0.858683 | 0.820000 | 0.038683 |
