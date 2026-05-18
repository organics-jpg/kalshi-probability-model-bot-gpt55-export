# v28 NO Mid-Edge Entry Repair

Research-only; no live bot changes and no orders.

- Policy: `skip_no_edge_5_8pp_repair_farthest_boundary`
- Delta vs target: `34.000000c`
- Coverage repaired: `True`
- LOO worst / negative exclusions: `-713.000000/114`

## Interpretation

- Skipped NO mid-edge rows: 14; repair rows added: 16.
- Target net -606.0c; candidate net -572.0c at 75.0% coverage.
- Candidate is not live-promotable until net PnL is positive in frozen forward validation.
- Discovery-only; freeze separately if this remains useful.

## Summaries

| slice | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| target | 112 | 112 | 64/48 | 73.684211 | -606.000000 | -5.410714 |
| skipped | 14 | 14 | 8/6 | 9.210526 | -97.000000 | -6.928571 |
| kept | 98 | 98 | 56/42 | 64.473684 | -509.000000 | -5.193878 |
| repairs | 16 | 16 | 12/4 | 10.526316 | -63.000000 | -3.937500 |
| candidate | 114 | 114 | 68/46 | 75.000000 | -572.000000 | -5.017544 |

## Skipped Rows

| market | side | won | net c | p | ask | edge | recross | abs d |
|---|---|---|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY052015-15 | no | False | -102.000000 | 0.567861 | 0.490000 | 0.077861 | 0.945709 | 0.150360 |
| KXBTC15M-26MAY052245-45 | no | False | -118.000000 | 0.643789 | 0.570000 | 0.073789 | 0.663374 | 0.362082 |
| KXBTC15M-26MAY060330-30 | no | False | -118.000000 | 0.630880 | 0.570000 | 0.060880 | 0.689280 | 0.287388 |
| KXBTC15M-26MAY060500-00 | no | False | -126.000000 | 0.674136 | 0.610000 | 0.064136 | 0.620318 | 0.377919 |
| KXBTC15M-26MAY060915-15 | no | True | 76.000000 | 0.672099 | 0.600000 | 0.072099 | 0.831637 | 0.431641 |
| KXBTC15M-26MAY061015-15 | no | True | 92.000000 | 0.595554 | 0.520000 | 0.075554 | 1.130150 | 0.274143 |
| KXBTC15M-26MAY061700-00 | no | False | -102.000000 | 0.547299 | 0.490000 | 0.057299 | 0.799916 | 0.145303 |
| KXBTC15M-26MAY061815-15 | no | True | 53.000000 | 0.794472 | 0.720000 | 0.074472 | 0.363637 | 0.683153 |
| KXBTC15M-26MAY061915-15 | no | True | 22.000000 | 0.923342 | 0.870000 | 0.053342 | 0.229504 | 1.171707 |
| KXBTC15M-26MAY062215-15 | no | True | 78.000000 | 0.661831 | 0.590000 | 0.071831 | 0.669869 | 0.404187 |
| KXBTC15M-26MAY062245-45 | no | False | -112.000000 | 0.605951 | 0.540000 | 0.065951 | 0.786584 | 0.278629 |
| KXBTC15M-26MAY062315-15 | no | True | 60.000000 | 0.744580 | 0.680000 | 0.064580 | 0.455010 | 0.562923 |
| KXBTC15M-26MAY070530-30 | no | True | 100.000000 | 0.540822 | 0.480000 | 0.060822 | 0.894668 | 0.132673 |
| KXBTC15M-26MAY070945-45 | no | True | 100.000000 | 0.532085 | 0.480000 | 0.052085 | 1.088863 | 0.067417 |
