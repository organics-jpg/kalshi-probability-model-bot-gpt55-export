# v28 Frozen Raw p52 Mid-Edge Skip

Future-only validator. No live orders.

- Candidate live-ready: `False`
- Freeze timestamp UTC: `2026-05-06T11:57:26.075880+00:00`
- Rule: `Start from v28_raw_p52_edge0 and skip selected entries with raw/effective edge in [5pp, 10pp).`
- Future denominator: `102`
- Delta vs base: `-511.000000c`
- Blockers: `net_not_positive, simulated_share_gt_35pct`

## Summary

| row | entries | settled | W/L | coverage | win rate | avg edge | net c | actual/sim |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| base | 100 | 100 | 58/42 | 98.039216 | 0.580000 | 0.065197 | -452.000000 | 7/93 |
| candidate_summary | 77 | 77 | 40/37 | 75.490196 | 0.519481 | 0.064132 | -963.000000 | 1/76 |
| skipped_summary | 23 | 23 | 18/5 | 22.549020 | 0.782609 | 0.068765 | 511.000000 | 6/17 |

## Skipped Future Rows

| market | side | source | p | ask | edge | won | net c |
|---|---|---|---:|---:|---:|---|---:|
| KXBTC15M-26MAY060915-15 | no | rejected_actionable | 0.672099 | 0.600000 | 0.072099 | True | 76.000000 |
| KXBTC15M-26MAY061015-15 | no | rejected_actionable | 0.595554 | 0.520000 | 0.075554 | True | 92.000000 |
| KXBTC15M-26MAY061400-00 | no | approved_entry | 0.973640 | 0.890000 | 0.083640 | True | -11.000000 |
| KXBTC15M-26MAY061700-00 | no | rejected_actionable | 0.547299 | 0.490000 | 0.057299 | False | -102.000000 |
| KXBTC15M-26MAY061815-15 | no | rejected_actionable | 0.794472 | 0.720000 | 0.074472 | True | 53.000000 |
| KXBTC15M-26MAY061915-15 | no | approved_entry | 0.923342 | 0.870000 | 0.053342 | True | 22.000000 |
| KXBTC15M-26MAY061930-30 | yes | rejected_actionable | 0.551364 | 0.470000 | 0.081364 | True | 102.000000 |
| KXBTC15M-26MAY062000-00 | yes | rejected_actionable | 0.582435 | 0.500000 | 0.082435 | True | 96.000000 |
| KXBTC15M-26MAY062215-15 | no | rejected_actionable | 0.661831 | 0.590000 | 0.071831 | True | 78.000000 |
| KXBTC15M-26MAY062245-45 | no | rejected_actionable | 0.605951 | 0.540000 | 0.065951 | False | -112.000000 |
| KXBTC15M-26MAY062315-15 | no | rejected_actionable | 0.744580 | 0.680000 | 0.064580 | True | 60.000000 |
| KXBTC15M-26MAY070000-00 | no | approved_entry | 0.863962 | 0.780000 | 0.083962 | True | 2 |
| KXBTC15M-26MAY070115-15 | yes | rejected_actionable | 0.773654 | 0.720000 | 0.053654 | True | 53.000000 |
| KXBTC15M-26MAY070530-30 | no | rejected_actionable | 0.540822 | 0.480000 | 0.060822 | True | 100.000000 |
| KXBTC15M-26MAY070600-00 | yes | rejected_actionable | 0.723960 | 0.670000 | 0.053960 | True | 62.000000 |
| KXBTC15M-26MAY070645-45 | yes | approved_entry | 0.895399 | 0.810000 | 0.085399 | True | 35.000000 |
| KXBTC15M-26MAY070700-00 | yes | rejected_actionable | 0.654812 | 0.560000 | 0.094812 | False | -116.000000 |
| KXBTC15M-26MAY070715-15 | yes | rejected_actionable | 0.560435 | 0.510000 | 0.050435 | True | 94.000000 |
| KXBTC15M-26MAY070730-30 | yes | rejected_actionable | 0.530778 | 0.460000 | 0.070778 | False | -96.000000 |
| KXBTC15M-26MAY070800-00 | yes | rejected_actionable | 0.536385 | 0.450000 | 0.086385 | False | -94.000000 |
| KXBTC15M-26MAY070815-15 | yes | approved_entry | 0.950799 | 0.900000 | 0.050799 | True | 1.000000 |
| KXBTC15M-26MAY070830-30 | no | approved_entry | 0.875926 | 0.820000 | 0.055926 | True | 16.000000 |
| KXBTC15M-26MAY070945-45 | no | rejected_actionable | 0.532085 | 0.480000 | 0.052085 | True | 100.000000 |
