# v28 Raw p52 Shadow Mid-Edge Skip

Discovery diagnostic only. The rule is frozen separately before forward validation.

- Base policy: `v28_raw_p52_edge0`
- Candidate: `raw_p52_skip_rejected_mid_edge_5_10pp`
- Rule: `Start from v28_raw_p52_edge0; preserve approved_entry rows; skip rejected_actionable rows with edge in [5pp, 10pp).`
- Watched markets: `181`
- Delta vs base: `-101.000000c`

## Summary

| row | entries | settled | W/L | coverage | win rate | avg edge | net c | actual/sim |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| base | 169 | 169 | 104/65 | 93.370166 | 0.615385 | 0.058265 | 71.000000 | 12/157 |
| candidate_summary | 142 | 142 | 88/54 | 78.453039 | 0.619718 | 0.056236 | -30.000000 | 12/130 |
| skipped_summary | 27 | 27 | 16/11 | 14.917127 | 0.592593 | 0.068933 | 101.000000 | 0/27 |

## Skipped Rows

| market | side | source | p | ask | edge | won | net c |
|---|---|---|---:|---:|---:|---|---:|
| KXBTC15M-26MAY051600-00 | no | rejected_actionable | 0.547953 | 0.460000 | 0.087953 | True | 104.000000 |
| KXBTC15M-26MAY051745-45 | no | rejected_actionable | 0.780220 | 0.710000 | 0.070220 | True | 55.000000 |
| KXBTC15M-26MAY052015-15 | no | rejected_actionable | 0.567861 | 0.490000 | 0.077861 | False | -102.000000 |
| KXBTC15M-26MAY052030-30 | yes | rejected_actionable | 0.540780 | 0.470000 | 0.070780 | False | -98.000000 |
| KXBTC15M-26MAY052230-30 | no | rejected_actionable | 0.730624 | 0.650000 | 0.080624 | True | 66.000000 |
| KXBTC15M-26MAY052245-45 | no | rejected_actionable | 0.643789 | 0.570000 | 0.073789 | False | -118.000000 |
| KXBTC15M-26MAY060215-15 | yes | rejected_actionable | 0.583024 | 0.530000 | 0.053024 | False | -110.000000 |
| KXBTC15M-26MAY060330-30 | no | rejected_actionable | 0.630880 | 0.570000 | 0.060880 | False | -118.000000 |
| KXBTC15M-26MAY060500-00 | no | rejected_actionable | 0.674136 | 0.610000 | 0.064136 | False | -126.000000 |
| KXBTC15M-26MAY060800-00 | yes | rejected_actionable | 0.523411 | 0.470000 | 0.053411 | True | 102.000000 |
| KXBTC15M-26MAY060915-15 | no | rejected_actionable | 0.672099 | 0.600000 | 0.072099 | True | 76.000000 |
| KXBTC15M-26MAY061015-15 | no | rejected_actionable | 0.595554 | 0.520000 | 0.075554 | True | 92.000000 |
| KXBTC15M-26MAY061700-00 | no | rejected_actionable | 0.547299 | 0.490000 | 0.057299 | False | -102.000000 |
| KXBTC15M-26MAY061815-15 | no | rejected_actionable | 0.794472 | 0.720000 | 0.074472 | True | 53.000000 |
| KXBTC15M-26MAY061930-30 | yes | rejected_actionable | 0.551364 | 0.470000 | 0.081364 | True | 102.000000 |
| KXBTC15M-26MAY062000-00 | yes | rejected_actionable | 0.582435 | 0.500000 | 0.082435 | True | 96.000000 |
| KXBTC15M-26MAY062215-15 | no | rejected_actionable | 0.661831 | 0.590000 | 0.071831 | True | 78.000000 |
| KXBTC15M-26MAY062245-45 | no | rejected_actionable | 0.605951 | 0.540000 | 0.065951 | False | -112.000000 |
| KXBTC15M-26MAY062315-15 | no | rejected_actionable | 0.744580 | 0.680000 | 0.064580 | True | 60.000000 |
| KXBTC15M-26MAY070115-15 | yes | rejected_actionable | 0.773654 | 0.720000 | 0.053654 | True | 53.000000 |
| KXBTC15M-26MAY070530-30 | no | rejected_actionable | 0.540822 | 0.480000 | 0.060822 | True | 100.000000 |
| KXBTC15M-26MAY070600-00 | yes | rejected_actionable | 0.723960 | 0.670000 | 0.053960 | True | 62.000000 |
| KXBTC15M-26MAY070700-00 | yes | rejected_actionable | 0.654812 | 0.560000 | 0.094812 | False | -116.000000 |
| KXBTC15M-26MAY070715-15 | yes | rejected_actionable | 0.560435 | 0.510000 | 0.050435 | True | 94.000000 |
| KXBTC15M-26MAY070730-30 | yes | rejected_actionable | 0.530778 | 0.460000 | 0.070778 | False | -96.000000 |
| KXBTC15M-26MAY070800-00 | yes | rejected_actionable | 0.536385 | 0.450000 | 0.086385 | False | -94.000000 |
| KXBTC15M-26MAY070945-45 | no | rejected_actionable | 0.532085 | 0.480000 | 0.052085 | True | 100.000000 |
