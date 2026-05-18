# v28 Danger Repair Bakeoff

Diagnostic-only bakeoff for named physical danger removals plus coverage repair.

- Forward denominator: `152`
- Target net/coverage: `-606.000000/73.684211`

## Interpretation

- Best diagnostic variant is paid_price_fragile_only with net -140.0c versus target -606.0c.
- Coverage for best variant is 75.0%.
- Rows repaired from non-missed markets use realized-net ordering only as diagnostic opportunity mapping; this is not promotion evidence.

## Ranking

| rank | variant | removed | repairs | coverage | net c | delta c | W/L | repair net c |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | paid_price_fragile_only | 18 | 20 | 75.000000 | -140.000000 | 466.000000 | 66/48 | -345.000000 |
| 2 | paid_or_weak_boundary | 37 | 39 | 75.000000 | -165.000000 | 441.000000 | 70/44 | -236.000000 |
| 3 | weak_boundary_turbulence_only | 19 | 21 | 75.000000 | -1046.000000 | -440.000000 | 65/49 | -306.000000 |

## Best Variant Repairs

| market | source | side | won | net c | p | ask | tags |
|---|---|---|---|---:|---:|---:|---|
| KXBTC15M-26MAY052045-45 | rejected_actionable | yes | False | -61.000000 | 0.658389 | 0.570000 |  |
| KXBTC15M-26MAY052200-00 | approved_entry | yes | True | 19.000000 | 0.850777 | 0.790000 |  |
| KXBTC15M-26MAY060000-00 | rejected_actionable | no | False | -67.000000 | 0.678147 | 0.630000 |  |
| KXBTC15M-26MAY060015-15 | rejected_actionable | no | True | 40.000000 | 0.643392 | 0.560000 |  |
| KXBTC15M-26MAY060115-15 | rejected_actionable | no | True | 28.000000 | 0.726160 | 0.680000 |  |
| KXBTC15M-26MAY060145-45 | rejected_actionable | no | True | 38.000000 | 0.602935 | 0.580000 |  |
| KXBTC15M-26MAY060230-30 | rejected_actionable | no | False | -71.000000 | 0.717693 | 0.670000 |  |
| KXBTC15M-26MAY060315-15 | rejected_actionable | yes | True | 24.000000 | 0.783841 | 0.730000 |  |
| KXBTC15M-26MAY060615-15 | rejected_actionable | yes | True | 24.000000 | 0.777865 | 0.730000 |  |
| KXBTC15M-26MAY060700-00 | rejected_actionable | no | False | -63.000000 | 0.600088 | 0.590000 |  |
| KXBTC15M-26MAY060715-15 | rejected_actionable | yes | True | 31.000000 | 0.706716 | 0.650000 |  |
| KXBTC15M-26MAY060745-45 | rejected_actionable | yes | False | -57.000000 | 0.627260 | 0.530000 |  |
| KXBTC15M-26MAY060815-15 | rejected_actionable | no | True | 34.000000 | 0.643430 | 0.620000 |  |
| KXBTC15M-26MAY060845-45 | rejected_actionable | no | True | 37.000000 | 0.605958 | 0.590000 |  |
| KXBTC15M-26MAY060900-00 | rejected_actionable | yes | False | -80.000000 | 0.802760 | 0.770000 |  |
| KXBTC15M-26MAY061000-00 | rejected_actionable | no | True | 42.000000 | 0.661616 | 0.540000 |  |
| KXBTC15M-26MAY061115-15 | rejected_actionable | yes | False | -60.000000 | 0.600113 | 0.560000 |  |
| KXBTC15M-26MAY061145-45 | rejected_actionable | yes | False | -69.000000 | 0.685968 | 0.650000 |  |
| KXBTC15M-26MAY061215-15 | rejected_actionable | no | False | -62.000000 | 0.614405 | 0.580000 |  |
| KXBTC15M-26MAY061245-45 | rejected_actionable | no | False | -72.000000 | 0.740496 | 0.690000 |  |
