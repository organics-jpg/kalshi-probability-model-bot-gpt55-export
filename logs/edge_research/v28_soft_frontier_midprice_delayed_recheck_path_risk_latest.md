# v28 Soft-Frontier Mid-Price Delayed-Recheck Path Risk

Research-only path-risk audit. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:54:54.000561+00:00`

## Interpretation

- Research-only path-risk audit; no live bot changes or orders.
- Diagnostic suppressed rows with post-recheck path: 33/33; worst post-recheck bid excursion -17.0c.
- If large post-recheck adverse marks remain, the candidate needs a disaster guard before live-readiness.

## diagnostic_prefreeze_context

- Suppressed rows: `33`
- Rows with post-recheck path: `33`
- Weighted delta: `444.00c`
- Avg min after exit bid: `-2.03c`
- Worst min after exit bid: `-25.00c`
- Avg min after recheck bid: `-0.85c`
- Worst min after recheck bid: `-17.00c`
- Adverse after recheck 10/25/50c rows: `1 / 0 / 0`
- Blockers: `[]`

| market | side | source | reason | exit bid | recheck bid | min bid after recheck | last bid | min-after exit c | min-after recheck c | delta c | pts |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY060600-00 | no | approved_entry | mushroom_v28_exit_value_over_hold | 83.00 | 75.00 | 58.00 | 100.00 | -25.00 | -17.00 | 38.00 | 24 |
| KXBTC15M-26MAY070030-30 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 94.00 | 91.00 | 85.00 | 100.00 | -9.00 | -6.00 | 6.00 | 12 |
| KXBTC15M-26MAY062245-45 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 91.00 | 90.00 | 88.00 | 100.00 | -3.00 | -2.00 | 20.00 | 23 |
| KXBTC15M-26MAY062030-30 | no | approved_entry | mushroom_v28_exit_value_over_hold | 88.00 | 94.00 | 92.00 | 100.00 | 0.00 | -2.00 | 34.00 | 34 |
| KXBTC15M-26MAY060530-30 | no | approved_entry | mushroom_v28_exit_value_over_hold | 96.00 | 96.00 | 95.00 | 100.00 | -3.00 | -1.00 | 10.00 | 24 |
| KXBTC15M-26MAY060445-45 | yes | rejected_actionable | mushroom_v28_exit_value_over_hold | 99.00 | 100.00 | 100.00 | 100.00 | 0.00 | 0.00 | 2.00 | 8 |
| KXBTC15M-26MAY061445-45 | no | approved_entry | mushroom_v28_exit_value_over_hold | 97.00 | 99.00 | 99.00 | 100.00 | 0.00 | 0.00 | 2.00 | 15 |
| KXBTC15M-26MAY061615-15 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 95.00 | 96.00 | 96.00 | 100.00 | 0.00 | 0.00 | 12.00 | 27 |
| KXBTC15M-26MAY061830-30 | no | approved_entry | mushroom_v28_exit_value_over_hold | 99.00 | 100.00 | 100.00 | 100.00 | 0.00 | 0.00 | 2.00 | 7 |
| KXBTC15M-26MAY070815-15 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 91.00 | 94.00 | 94.00 | 100.00 | 0.00 | 0.00 | 18.00 | 22 |
| KXBTC15M-26MAY061400-00 | no | approved_entry | mushroom_v28_exit_value_over_hold | 81.00 | 92.00 | 92.00 | 100.00 | 0.00 | 0.00 | 32.00 | 8 |
| KXBTC15M-26MAY061915-15 | no | approved_entry | mushroom_v28_exit_value_over_hold | 98.00 | 100.00 | 100.00 | 100.00 | 0.00 | 0.00 | 2.00 | 4 |
| KXBTC15M-26MAY062300-00 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 95.00 | 94.00 | 94.00 | 100.00 | -1.00 | 0.00 | 10.00 | 27 |
| KXBTC15M-26MAY061815-15 | no | approved_entry | mushroom_v28_exit_value_over_hold | 96.00 | 96.00 | 96.00 | 100.00 | 0.00 | 0.00 | 8.00 | 27 |
| KXBTC15M-26MAY061545-45 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 97.00 | 94.00 | 94.00 | 100.00 | -4.00 | 0.00 | 10.00 | 16 |
| KXBTC15M-26MAY070115-15 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 79.00 | 85.00 | 85.00 | 100.00 | 0.00 | 0.00 | 36.00 | 25 |
| KXBTC15M-26MAY070545-45 | no | approved_entry | mushroom_v28_exit_value_over_hold | 89.00 | 96.00 | 96.00 | 100.00 | -9.00 | 0.00 | 18.00 | 11 |
| KXBTC15M-26MAY061045-45 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 98.00 | 100.00 | 100.00 | 100.00 | 0.00 | 0.00 | 4.00 | 3 |
| KXBTC15M-26MAY062045-45 | no | approved_entry | mushroom_v28_exit_value_over_hold | 94.00 | 95.00 | 95.00 | 100.00 | -2.00 | 0.00 | 16.00 | 29 |
| KXBTC15M-26MAY060630-30 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 99.00 | 99.00 | 99.00 | 100.00 | -1.00 | 0.00 | 2.00 | 2 |
| KXBTC15M-26MAY060645-45 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 95.00 | 99.00 | 99.00 | 100.00 | 0.00 | 0.00 | 6.00 | 8 |
| KXBTC15M-26MAY070000-00 | no | approved_entry | mushroom_v28_exit_value_over_hold | 81.00 | 91.00 | 91.00 | 100.00 | -10.00 | 0.00 | 42.00 | 18 |
| KXBTC15M-26MAY060830-30 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 100.00 | 100.00 | 100.00 | 100.00 | 0.00 | 0.00 | 0.00 | 2 |
| KXBTC15M-26MAY060915-15 | no | approved_entry | mushroom_v28_exit_value_over_hold | 99.00 | 100.00 | 100.00 | 100.00 | 0.00 | 0.00 | 0.00 | 2 |
| KXBTC15M-26MAY060515-15 | no | approved_entry | mushroom_v28_exit_value_over_hold | 94.00 | 100.00 | 100.00 | 100.00 | 0.00 | 0.00 | 10.00 | 3 |
| KXBTC15M-26MAY060700-00 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 88.00 | 100.00 | 100.00 | 100.00 | 0.00 | 0.00 | 22.00 | 2 |
| KXBTC15M-26MAY060715-15 | yes | rejected_actionable | mushroom_v28_exit_value_over_hold | 99.00 | 100.00 | 100.00 | 100.00 | 0.00 | 0.00 | 2.00 | 4 |
| KXBTC15M-26MAY060900-00 | no | approved_entry | mushroom_v28_exit_value_over_hold | 96.00 | 100.00 | 100.00 | 100.00 | 0.00 | 0.00 | 8.00 | 5 |
| KXBTC15M-26MAY062115-15 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 99.00 | 100.00 | 100.00 | 100.00 | 0.00 | 0.00 | 2.00 | 1 |
| KXBTC15M-26MAY060945-45 | no | approved_entry | mushroom_v28_exit_value_over_hold | 92.00 | 100.00 | 100.00 | 100.00 | 0.00 | 0.00 | 8.00 | 1 |

## post_delayed_recheck_birth

- Suppressed rows: `3`
- Rows with post-recheck path: `3`
- Weighted delta: `66.00c`
- Avg min after exit bid: `-3.00c`
- Worst min after exit bid: `-9.00c`
- Avg min after recheck bid: `0.00c`
- Worst min after recheck bid: `0.00c`
- Adverse after recheck 10/25/50c rows: `0 / 0 / 0`
- Blockers: `['post_birth_rows_required', 'suppressed_rows_lt_30']`

| market | side | source | reason | exit bid | recheck bid | min bid after recheck | last bid | min-after exit c | min-after recheck c | delta c | pts |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY070815-15 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 91.00 | 94.00 | 94.00 | 100.00 | 0.00 | 0.00 | 18.00 | 22 |
| KXBTC15M-26MAY070545-45 | no | approved_entry | mushroom_v28_exit_value_over_hold | 89.00 | 96.00 | 96.00 | 100.00 | -9.00 | 0.00 | 18.00 | 11 |
| KXBTC15M-26MAY070745-45 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 93.00 | 97.00 | 97.00 | 100.00 | 0.00 | 0.00 | 30.00 | 19 |
