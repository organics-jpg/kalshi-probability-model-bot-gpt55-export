# v28 Danger-Tag Replacement Diagnostic

Diagnostic-only: tests physical danger tags with same-market clean replacement.

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Forward denominator: `152`
- Danger rows/replacements: `37/33`

## Interpretation

- Danger-tag rows: 37 of 112 target entries.
- Same-market clean replacements found for 33 of 37 danger rows.
- Kept-plus-replacement coverage would be 71.05263157894737%.
- This replacement concept does not currently preserve the target coverage floor.

## Summaries

| slice | entries | settled | W/L | coverage | net c | avg net c |
|---|---:|---:|---:|---:|---:|---:|
| target | 112 | 112 | 64/48 | 73.684211 | -606.000000 | -5.410714 |
| danger_only | 37 | 37 | 18/19 | 24.342105 | -677.000000 | -18.297297 |
| kept_only | 75 | 75 | 46/29 | 49.342105 | 71.000000 | 0.946667 |
| replacement_only | 33 | 33 | 21/12 | 21.710526 | -342.000000 | -10.363636 |
| kept_plus_replacement | 108 | 108 | 67/41 | 71.052632 | -271.000000 | -2.509259 |

## Cases

| market | skipped side | tags | skipped won | skipped net | replacements | chosen side | same side | chosen won | chosen net | delay s |
|---|---|---|---|---:|---:|---|---|---|---:|---:|
| KXBTC15M-26MAY052015-15 | no | weak_boundary_turbulence | False | -53.000000 | 1 | yes | False | True | 13.000000 | 185.005681 |
| KXBTC15M-26MAY052030-30 | yes | weak_boundary_turbulence | False | -51.000000 | 2 | yes | True | False | -57.000000 | 101.359581 |
| KXBTC15M-26MAY052100-00 | yes | weak_boundary_turbulence | True | 50.000000 | 6 | no | False | False | -77.000000 | 71.289827 |
| KXBTC15M-26MAY052115-15 | yes | weak_boundary_turbulence | True | 43.000000 | 2 | yes | True | True | 19.000000 | 211.071552 |
| KXBTC15M-26MAY052345-45 | no | paid_price_fragile | True | 33.000000 | 2 | no | True | True | 42.000000 | 60.574779 |
| KXBTC15M-26MAY060100-00 | yes | paid_price_fragile | False | -82.000000 | 8 | yes | True | False | -85.000000 | 26.932383 |
| KXBTC15M-26MAY060200-00 | yes | paid_price_fragile | True | 36.000000 | 7 | yes | True | True | 15.000000 | 137.596413 |
| KXBTC15M-26MAY060215-15 | yes | weak_boundary_turbulence | False | -57.000000 | 9 | yes | True | False | -66.000000 | 20.003399 |
| KXBTC15M-26MAY060245-45 | no | paid_price_fragile | False | -69.000000 | 1 | no | True | False | -68.000000 | 20.000202 |
| KXBTC15M-26MAY060345-45 | yes | weak_boundary_turbulence | False | -42.000000 | 3 | no | False | True | 30.000000 | 120.589387 |
| KXBTC15M-26MAY060415-15 | yes | paid_price_fragile | True | 29.000000 | 1 | yes | True | True | 11.000000 | 91.090485 |
| KXBTC15M-26MAY060515-15 | yes | weak_boundary_turbulence | False | -45.000000 | 2 | no | False | True | 23.000000 | 20.345791 |
| KXBTC15M-26MAY060530-30 | yes | weak_boundary_turbulence | False | -58.000000 | 1 | no | False | True | 19.000000 | 312.577116 |
| KXBTC15M-26MAY060630-30 | no | paid_price_fragile | False | -70.000000 | 8 | no | True | False | -69.000000 | 60.000143 |
| KXBTC15M-26MAY060800-00 | yes | weak_boundary_turbulence | True | 49.000000 | 9 | yes | True | True | 28.000000 | 120.006181 |
| KXBTC15M-26MAY060930-30 | yes | paid_price_fragile | False | -64.000000 | 7 | no | False | True | 28.000000 | 240.118978 |
| KXBTC15M-26MAY061015-15 | no | weak_boundary_turbulence | True | 44.000000 | 8 | no | True | True | 36.000000 | 19.995767 |
| KXBTC15M-26MAY061030-30 | yes | paid_price_fragile | True | 35.000000 | 3 | yes | True | True | 27.000000 | 19.997338 |
| KXBTC15M-26MAY061100-00 | yes | paid_price_fragile | False | -77.000000 | 11 | yes | True | False | -73.000000 | 19.986080 |
| KXBTC15M-26MAY061130-30 | yes | paid_price_fragile | True | 31.000000 | 4 | yes | True | True | 28.000000 | 20.004677 |
| KXBTC15M-26MAY061230-30 | yes | paid_price_fragile | False | -72.000000 | 5 | no | False | True | 27.000000 | 191.026070 |
| KXBTC15M-26MAY061430-30 | yes | paid_price_fragile | True | 29.000000 | 2 | yes | True | True | 29.000000 | 43.074503 |
| KXBTC15M-26MAY061445-45 | no | paid_price_fragile | True | 26.000000 | 4 | no | True | True | 16.000000 | 164.877505 |
| KXBTC15M-26MAY061600-00 | no | paid_price_fragile | False | -64.000000 | 4 | no | True | False | -62.000000 | 122.579377 |
| KXBTC15M-26MAY061630-30 | no | paid_price_fragile | True | 33.000000 | 1 | no | True | True | 20.000000 | 82.372113 |
| KXBTC15M-26MAY061930-30 | yes | weak_boundary_turbulence | True | 49.000000 | 0 | None | None | None | None | None |
| KXBTC15M-26MAY061945-45 | yes | weak_boundary_turbulence | False | -46.000000 | 2 | no | False | True | 36.000000 | 41.551488 |
| KXBTC15M-26MAY070045-45 | no | weak_boundary_turbulence | True | 48.000000 | 1 | yes | False | False | -81.000000 | 104.422902 |
| KXBTC15M-26MAY070530-30 | no | weak_boundary_turbulence | True | 48.000000 | 1 | yes | False | False | -67.000000 | 122.215913 |
| KXBTC15M-26MAY070715-15 | yes | weak_boundary_turbulence | True | 45.000000 | 0 | None | None | None | None | None |
| KXBTC15M-26MAY070730-30 | yes | weak_boundary_turbulence | False | -50.000000 | 0 | None | None | None | None | None |
| KXBTC15M-26MAY070815-15 | yes | weak_boundary_turbulence | True | 52.000000 | 1 | yes | True | True | 9.000000 | 282.282708 |
| KXBTC15M-26MAY070830-30 | yes | weak_boundary_turbulence | False | -45.000000 | 1 | no | False | True | 16.000000 | 242.386234 |
| KXBTC15M-26MAY070945-45 | no | weak_boundary_turbulence | True | 48.000000 | 3 | no | True | True | 32.000000 | 60.211520 |
| KXBTC15M-26MAY071015-15 | no | paid_price_fragile | False | -64.000000 | 6 | no | True | False | -67.000000 | 223.653333 |
| KXBTC15M-26MAY071115-15 | no | paid_price_fragile | False | -66.000000 | 1 | no | True | False | -74.000000 | 300.222847 |
| KXBTC15M-26MAY071200-00 | yes | paid_price_fragile | False | -64.000000 | 0 | None | None | None | None | None |
