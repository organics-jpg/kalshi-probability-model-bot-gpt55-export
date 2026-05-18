# v28 Frozen Raw p52 Book-Disagreement Skip

Future-only validator. No live orders.

- Candidate live-ready: `False`
- Freeze timestamp UTC: `2026-05-06T12:06:41.849306+00:00`
- Rule: `Start from v28_raw_p52_edge0 and skip rows where p_eff - executable ask probability > 15pp.`
- Future denominator: `101`
- Delta vs base: `-79.000000c`
- Blockers: `net_not_positive, simulated_share_gt_35pct`

## Summary

| row | entries | settled | W/L | coverage | win rate | avg p | avg ask | avg p-book | net c | actual/sim |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| base | 99 | 99 | 57/42 | 98.019802 | 0.575758 | 0.643428 | 0.577576 | 0.065852 | -540.000000 | 7/92 |
| candidate_summary | 88 | 88 | 52/36 | 87.128713 | 0.590909 | 0.643212 | 0.601364 | 0.041849 | -619.000000 | 6/82 |
| skipped_summary | 11 | 11 | 5/6 | 10.891089 | 0.454545 | 0.645155 | 0.387273 | 0.257882 | 79.000000 | 1/10 |

## Skipped Future Rows

| market | side | source | p | ask | p-book | won | net c |
|---|---|---|---:|---:|---:|---|---:|
| KXBTC15M-26MAY060945-45 | no | rejected_actionable | 0.761891 | 0.500000 | 0.261891 | True | 96.000000 |
| KXBTC15M-26MAY061830-30 | yes | rejected_actionable | 0.553162 | 0.230000 | 0.323162 | False | -49.000000 |
| KXBTC15M-26MAY061900-00 | no | rejected_actionable | 0.661389 | 0.450000 | 0.211389 | False | -94.000000 |
| KXBTC15M-26MAY062030-30 | yes | rejected_actionable | 0.544418 | 0.320000 | 0.224418 | False | -68.000000 |
| KXBTC15M-26MAY062100-00 | no | rejected_actionable | 0.615588 | 0.220000 | 0.395588 | False | -47.000000 |
| KXBTC15M-26MAY062130-30 | yes | rejected_actionable | 0.586142 | 0.410000 | 0.176142 | True | 114.000000 |
| KXBTC15M-26MAY062200-00 | no | rejected_actionable | 0.617816 | 0.460000 | 0.157816 | True | 104.000000 |
| KXBTC15M-26MAY062230-30 | yes | rejected_actionable | 0.718015 | 0.380000 | 0.338015 | False | -80.000000 |
| KXBTC15M-26MAY070030-30 | no | rejected_actionable | 0.523605 | 0.330000 | 0.193605 | False | -70.000000 |
| KXBTC15M-26MAY070615-15 | no | rejected_actionable | 0.610872 | 0.280000 | 0.330872 | True | 141.000000 |
| KXBTC15M-26MAY070745-45 | yes | approved_entry | 0.903807 | 0.680000 | 0.223807 | True | 32.000000 |
