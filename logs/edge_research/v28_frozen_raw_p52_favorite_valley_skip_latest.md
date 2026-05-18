# v28 Frozen Raw p52 Favorite-Valley Skip

Future-only validator. No live orders.

- Candidate live-ready: `False`
- Freeze timestamp UTC: `2026-05-06T11:52:57.665782+00:00`
- Rule: `Start from v28_raw_p52_edge0 and skip selected entries with executable ask in [65c, 75c).`
- Future denominator: `102`
- Delta vs base: `-279.000000c`
- Blockers: `net_not_positive, simulated_share_gt_35pct`

## Summary

| row | entries | settled | W/L | coverage | win rate | avg ask | net c | actual/sim |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| base | 100 | 100 | 58/42 | 98.039216 | 0.580000 | 0.577200 | -452.000000 | 7/93 |
| candidate_summary | 84 | 84 | 45/39 | 82.352941 | 0.535714 | 0.553929 | -731.000000 | 6/78 |
| skipped_summary | 16 | 16 | 13/3 | 15.686275 | 0.812500 | 0.699375 | 279.000000 | 1/15 |

## Skipped Future Rows

| market | side | source | p | ask | won | net c |
|---|---|---|---:|---:|---|---:|
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
