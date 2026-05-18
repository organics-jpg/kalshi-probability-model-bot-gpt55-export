# v28 Soft-Frontier Delayed-Recheck Rescue Path Risk

Research-only path-risk audit. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:54:58.397224+00:00`

## Interpretation

- Research-only path-risk audit; no live bot changes or orders.
- drop15_bid60 has 35 suppressed rows, worst post-recheck excursion -54.0c, adverse 10/25/50 rows 2/1/1.

## Summary

- Variant: `drop15_bid60`
- Suppressed rows: `35`
- Helpful/harmful rows: `33/0`
- Weighted delta: `608.00c`
- Worst min after exit bid: `-47.00c`
- Worst min after recheck bid: `-54.00c`
- Adverse after recheck 10/25/50c rows: `2 / 1 / 1`
- Blockers: `['large_post_recheck_adverse_marks_present']`

## Worst Rows

| market | side | source | reason | exit bid | recheck bid | drop | min bid post-recheck | last bid | min-after recheck c | delta c |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY062100-00 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 67.00 | 74.00 | 12.00 | 20.00 | 99.00 | -54.00 | 64.00 |
| KXBTC15M-26MAY060600-00 | no | approved_entry | mushroom_v28_exit_value_over_hold | 83.00 | 75.00 | 3.00 | 58.00 | 100.00 | -17.00 | 38.00 |
| KXBTC15M-26MAY070030-30 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 94.00 | 91.00 | 3.00 | 85.00 | 100.00 | -6.00 | 6.00 |
| KXBTC15M-26MAY062245-45 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 91.00 | 90.00 | 1.00 | 88.00 | 100.00 | -2.00 | 20.00 |
| KXBTC15M-26MAY062030-30 | no | approved_entry | mushroom_v28_exit_value_over_hold | 88.00 | 94.00 | 0.00 | 92.00 | 100.00 | -2.00 | 34.00 |
| KXBTC15M-26MAY060530-30 | no | approved_entry | mushroom_v28_exit_value_over_hold | 96.00 | 96.00 | 3.00 | 95.00 | 100.00 | -1.00 | 10.00 |
| KXBTC15M-26MAY060445-45 | yes | rejected_actionable | mushroom_v28_exit_value_over_hold | 99.00 | 100.00 | 0.00 | 100.00 | 100.00 | 0.00 | 2.00 |
| KXBTC15M-26MAY061445-45 | no | approved_entry | mushroom_v28_exit_value_over_hold | 97.00 | 99.00 | 0.00 | 99.00 | 100.00 | 0.00 | 2.00 |
| KXBTC15M-26MAY061615-15 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 95.00 | 96.00 | 0.00 | 96.00 | 100.00 | 0.00 | 12.00 |
| KXBTC15M-26MAY061830-30 | no | approved_entry | mushroom_v28_exit_value_over_hold | 99.00 | 100.00 | 0.00 | 100.00 | 100.00 | 0.00 | 2.00 |
| KXBTC15M-26MAY070815-15 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 91.00 | 94.00 | 0.00 | 94.00 | 100.00 | 0.00 | 18.00 |
| KXBTC15M-26MAY061400-00 | no | approved_entry | mushroom_v28_exit_value_over_hold | 81.00 | 92.00 | 0.00 | 92.00 | 100.00 | 0.00 | 32.00 |
| KXBTC15M-26MAY061915-15 | no | approved_entry | mushroom_v28_exit_value_over_hold | 98.00 | 100.00 | 0.00 | 100.00 | 100.00 | 0.00 | 2.00 |
| KXBTC15M-26MAY062300-00 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 95.00 | 94.00 | 1.00 | 94.00 | 100.00 | 0.00 | 10.00 |
| KXBTC15M-26MAY061815-15 | no | approved_entry | mushroom_v28_exit_value_over_hold | 96.00 | 96.00 | 0.00 | 96.00 | 100.00 | 0.00 | 8.00 |
| KXBTC15M-26MAY061545-45 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 97.00 | 94.00 | 4.00 | 94.00 | 100.00 | 0.00 | 10.00 |
| KXBTC15M-26MAY070115-15 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 79.00 | 85.00 | 0.00 | 85.00 | 100.00 | 0.00 | 36.00 |
| KXBTC15M-26MAY070545-45 | no | approved_entry | mushroom_v28_exit_value_over_hold | 89.00 | 96.00 | 9.00 | 96.00 | 100.00 | 0.00 | 18.00 |
| KXBTC15M-26MAY061045-45 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 98.00 | 100.00 | 0.00 | 100.00 | 100.00 | 0.00 | 4.00 |
| KXBTC15M-26MAY062045-45 | no | approved_entry | mushroom_v28_exit_value_over_hold | 94.00 | 95.00 | 2.00 | 95.00 | 100.00 | 0.00 | 16.00 |
| KXBTC15M-26MAY060630-30 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 99.00 | 99.00 | 1.00 | 99.00 | 100.00 | 0.00 | 2.00 |
| KXBTC15M-26MAY060645-45 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 95.00 | 99.00 | 0.00 | 99.00 | 100.00 | 0.00 | 6.00 |
| KXBTC15M-26MAY070000-00 | no | approved_entry | mushroom_v28_exit_value_over_hold | 81.00 | 91.00 | 10.00 | 91.00 | 100.00 | 0.00 | 42.00 |
| KXBTC15M-26MAY060830-30 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 100.00 | 100.00 | 0.00 | 100.00 | 100.00 | 0.00 | 0.00 |
| KXBTC15M-26MAY060915-15 | no | approved_entry | mushroom_v28_exit_value_over_hold | 99.00 | 100.00 | 0.00 | 100.00 | 100.00 | 0.00 | 0.00 |
| KXBTC15M-26MAY060515-15 | no | approved_entry | mushroom_v28_exit_value_over_hold | 94.00 | 100.00 | 0.00 | 100.00 | 100.00 | 0.00 | 10.00 |
| KXBTC15M-26MAY060700-00 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 88.00 | 100.00 | 0.00 | 100.00 | 100.00 | 0.00 | 22.00 |
| KXBTC15M-26MAY060715-15 | yes | rejected_actionable | mushroom_v28_exit_value_over_hold | 99.00 | 100.00 | 0.00 | 100.00 | 100.00 | 0.00 | 2.00 |
| KXBTC15M-26MAY060900-00 | no | approved_entry | mushroom_v28_exit_value_over_hold | 96.00 | 100.00 | 0.00 | 100.00 | 100.00 | 0.00 | 8.00 |
| KXBTC15M-26MAY062115-15 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 99.00 | 100.00 | 0.00 | 100.00 | 100.00 | 0.00 | 2.00 |
