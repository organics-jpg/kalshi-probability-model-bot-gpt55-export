# v28 Raw p52 Favorite-Valley Skip

Discovery diagnostic only. The rule is frozen separately before forward validation.

- Base policy: `v28_raw_p52_edge0`
- Candidate: `raw_p52_skip_ask65_75_favorite_valley`
- Rule: `Start from v28_raw_p52_edge0 and skip selected entries with executable ask in [65c, 75c).`
- Watched markets: `181`
- Delta vs base: `-167.000000c`

## Summary

| row | entries | settled | W/L | coverage | win rate | avg ask | net c | actual/sim |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| base | 169 | 169 | 104/65 | 93.370166 | 0.615385 | 0.586036 | 71.000000 | 12/157 |
| candidate_summary | 145 | 145 | 86/59 | 80.110497 | 0.593103 | 0.568552 | -96.000000 | 11/134 |
| skipped_summary | 24 | 24 | 18/6 | 13.259669 | 0.750000 | 0.691667 | 167.000000 | 1/23 |

## Skipped Rows

| market | side | source | p | ask | won | net c |
|---|---|---|---:|---:|---|---:|
| KXBTC15M-26MAY051730-30 | no | rejected_actionable | 0.681429 | 0.670000 | True | 62.000000 |
| KXBTC15M-26MAY051745-45 | no | rejected_actionable | 0.780220 | 0.710000 | True | 55.000000 |
| KXBTC15M-26MAY051815-15 | yes | rejected_actionable | 0.779130 | 0.740000 | False | -151.000000 |
| KXBTC15M-26MAY052230-30 | no | rejected_actionable | 0.730624 | 0.650000 | True | 66.000000 |
| KXBTC15M-26MAY060245-45 | no | rejected_actionable | 0.660829 | 0.650000 | False | -134.000000 |
| KXBTC15M-26MAY060345-45 | no | rejected_actionable | 0.702712 | 0.660000 | True | 64.000000 |
| KXBTC15M-26MAY060415-15 | yes | rejected_actionable | 0.676831 | 0.670000 | True | 62.000000 |
| KXBTC15M-26MAY060630-30 | no | rejected_actionable | 0.675344 | 0.660000 | False | -136.000000 |
| KXBTC15M-26MAY061100-00 | yes | rejected_actionable | 0.740374 | 0.740000 | False | -151.000000 |
| KXBTC15M-26MAY061130-30 | yes | rejected_actionable | 0.653101 | 0.650000 | True | 66.000000 |
| KXBTC15M-26MAY061230-30 | yes | rejected_actionable | 0.681329 | 0.680000 | False | -140.000000 |
| KXBTC15M-26MAY061430-30 | yes | rejected_actionable | 0.678512 | 0.670000 | True | 62.000000 |
| KXBTC15M-26MAY061445-45 | no | rejected_actionable | 0.724164 | 0.710000 | True | 55.000000 |
| KXBTC15M-26MAY061615-15 | yes | rejected_actionable | 0.770727 | 0.740000 | True | 49.000000 |
| KXBTC15M-26MAY061645-45 | no | rejected_actionable | 0.736529 | 0.710000 | True | 55.000000 |
| KXBTC15M-26MAY061800-00 | no | rejected_actionable | 0.700391 | 0.680000 | True | 60.000000 |
| KXBTC15M-26MAY061815-15 | no | rejected_actionable | 0.794472 | 0.720000 | True | 53.000000 |
| KXBTC15M-26MAY062300-00 | yes | rejected_actionable | 0.758354 | 0.730000 | True | 51.000000 |
| KXBTC15M-26MAY062315-15 | no | rejected_actionable | 0.744580 | 0.680000 | True | 60.000000 |
| KXBTC15M-26MAY070115-15 | yes | rejected_actionable | 0.773654 | 0.720000 | True | 53.000000 |
| KXBTC15M-26MAY070200-00 | no | rejected_actionable | 0.741860 | 0.710000 | True | 55.000000 |
| KXBTC15M-26MAY070600-00 | yes | rejected_actionable | 0.723960 | 0.670000 | True | 62.000000 |
| KXBTC15M-26MAY070745-45 | yes | approved_entry | 0.903807 | 0.680000 | True | 32.000000 |
| KXBTC15M-26MAY071230-30 | no | rejected_actionable | 0.729882 | 0.700000 | False | -143.000000 |
