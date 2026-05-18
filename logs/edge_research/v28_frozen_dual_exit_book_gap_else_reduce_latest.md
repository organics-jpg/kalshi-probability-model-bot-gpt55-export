# v28 Frozen Dual Exit Book-Gap Else Reduce

Research-only frozen forward watch. No live bot changes.

- Freeze timestamp UTC: `2026-05-06T21:15:42.381999+00:00`
- Candidate: `dual_exit_book_gap_else_reduce`
- Rule: `For each post-freeze settled live v28 exit row, use suppress_soft_gap15_or_p_hold75 when that ledger has the row; otherwise use suppress_reduce_p_hold_ge_075.`
- Future rows/settled: `59/59`
- Current/candidate gross: `340.0c/128.0c`
- Delta vs current: `-212.0c`
- W/L: `41/18`
- Full-loss cushion estimate: `1`
- Source counts: `{'book_gap': 59, 'reduce_fallback': 0}`
- Blockers: `delta_not_positive, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3, degenerates_to_book_gap_on_shared_window`

## Interpretation

- Dual exit composite has 59 settled post-freeze rows.
- Selected source counts are {'book_gap': 59, 'reduce_fallback': 0}.
- Candidate/current/delta are 128.0c/340.0c/-212.0c.
- If reduce_fallback stays zero, the clean future composite is simply the book-gap exit candidate.

## Rows

| market | side | result | source | reason | current c | candidate c | delta c | suppressed |
|---|---|---|---|---|---:|---:|---:|---|
| KXBTC15M-26MAY061800-00 | no | no | book_gap | mushroom_v28_probability_collapse_full | -86.0 | -86.0 | 0.000000 | False |
| KXBTC15M-26MAY061815-15 | no | no | book_gap | mushroom_v28_exit_value_over_hold | 24.0 | 32.0 | 8.000000 | True |
| KXBTC15M-26MAY061830-30 | no | no | book_gap | mushroom_v28_exit_value_over_hold | 20.0 | 22.0 | 2.000000 | True |
| KXBTC15M-26MAY061900-00 | yes | yes | book_gap |  | 20.0 | 20.0 | 0.000000 | False |
| KXBTC15M-26MAY061915-15 | no | no | book_gap | mushroom_v28_exit_value_over_hold | 24.0 | 26.0 | 2.000000 | True |
| KXBTC15M-26MAY062015-15 | no | no | book_gap | mushroom_v28_probability_collapse_full | -60.0 | -60.0 | 0.000000 | False |
| KXBTC15M-26MAY062015-15 | yes | no | book_gap | mushroom_v28_exit_value_over_hold | 8.0 | -172.0 | -180.000000 | True |
| KXBTC15M-26MAY062015-15 | yes | no | book_gap |  | -134.0 | -134.0 | 0.000000 | False |
| KXBTC15M-26MAY062030-30 | no | no | book_gap | mushroom_v28_exit_value_over_hold | 32.0 | 32.0 | 0.000000 | False |
| KXBTC15M-26MAY062045-45 | no | no | book_gap | mushroom_v28_exit_value_over_hold | 24.0 | 40.0 | 16.000000 | True |
| KXBTC15M-26MAY062100-00 | yes | yes | book_gap | mushroom_v28_exit_value_over_hold | -4.0 | -4.0 | 0.000000 | False |
| KXBTC15M-26MAY062100-00 | yes | yes | book_gap | mushroom_v28_exit_value_over_hold | -20.0 | -20.0 | 0.000000 | False |
| KXBTC15M-26MAY062100-00 | yes | yes | book_gap | mushroom_v28_exit_value_over_hold | 14.0 | 14.0 | 0.000000 | False |
| KXBTC15M-26MAY062115-15 | yes | yes | book_gap | mushroom_v28_exit_value_over_hold | -12.0 | -12.0 | 0.000000 | False |
| KXBTC15M-26MAY062115-15 | no | yes | book_gap | mushroom_v28_exit_value_over_hold | -34.0 | -34.0 | 0.000000 | False |
| KXBTC15M-26MAY062115-15 | yes | yes | book_gap | mushroom_v28_exit_value_over_hold | 22.0 | 24.0 | 2.000000 | True |
| KXBTC15M-26MAY062130-30 | no | yes | book_gap | mushroom_v28_probability_reduce | -32.0 | -152.0 | -120.000000 | True |
| KXBTC15M-26MAY062215-15 | no | no | book_gap | mushroom_v28_probability_collapse_full | 14.0 | 14.0 | 0.000000 | False |
| KXBTC15M-26MAY062215-15 | no | no | book_gap | mushroom_v28_exit_value_over_hold | 10.0 | 32.0 | 22.000000 | True |
| KXBTC15M-26MAY062245-45 | yes | yes | book_gap | mushroom_v28_exit_value_over_hold | 8.0 | 8.0 | 0.000000 | False |
| KXBTC15M-26MAY062300-00 | yes | yes | book_gap | mushroom_v28_exit_value_over_hold | 16.0 | 16.0 | 0.000000 | False |
| KXBTC15M-26MAY062315-15 | no | no | book_gap | mushroom_v28_exit_value_over_hold | 6.0 | 32.0 | 26.000000 | True |
| KXBTC15M-26MAY070000-00 | no | no | book_gap | mushroom_v28_exit_value_over_hold | 2.0 | 2.0 | 0.000000 | False |
| KXBTC15M-26MAY070015-15 | no | yes | book_gap | mushroom_v28_exit_value_over_hold | -2.0 | -2.0 | 0.000000 | False |
| KXBTC15M-26MAY070030-30 | yes | yes | book_gap | mushroom_v28_exit_value_over_hold | 30.0 | 36.0 | 6.000000 | True |
| KXBTC15M-26MAY070115-15 | yes | yes | book_gap | mushroom_v28_exit_value_over_hold | 0.0 | 0.0 | 0.000000 | False |
| KXBTC15M-26MAY070545-45 | no | no | book_gap | mushroom_v28_exit_value_over_hold | 18.0 | 36.0 | 18.000000 | True |
| KXBTC15M-26MAY070645-45 | yes | yes | book_gap |  | 38.0 | 38.0 | 0.000000 | False |
| KXBTC15M-26MAY070745-45 | yes | yes | book_gap | mushroom_v28_exit_value_over_hold | 34.0 | 64.0 | 30.000000 | True |
| KXBTC15M-26MAY070815-15 | yes | yes | book_gap | mushroom_v28_exit_value_over_hold | 2.0 | 20.0 | 18.000000 | True |
| KXBTC15M-26MAY070830-30 | no | no | book_gap | mushroom_v28_exit_value_over_hold | 18.0 | 36.0 | 18.000000 | True |
| KXBTC15M-26MAY070830-30 | no | no | book_gap | mushroom_v28_exit_value_over_hold | -14.0 | -14.0 | 0.000000 | False |
| KXBTC15M-26MAY070830-30 | no | no | book_gap |  | 46.0 | 46.0 | 0.000000 | False |
| KXBTC15M-26MAY070915-15 | no | no | book_gap |  | 46.0 | 46.0 | 0.000000 | False |
| KXBTC15M-26MAY070930-30 | yes | yes | book_gap | mushroom_v28_exit_value_over_hold | 34.0 | 40.0 | 6.000000 | True |
| KXBTC15M-26MAY070945-45 | no | no | book_gap |  | 62.0 | 62.0 | 0.000000 | False |
| KXBTC15M-26MAY071000-00 | no | no | book_gap | mushroom_v28_probability_collapse_full | -36.0 | -36.0 | 0.000000 | False |
| KXBTC15M-26MAY071000-00 | no | no | book_gap | mushroom_v28_probability_reduce | 16.0 | 58.0 | 42.000000 | True |
| KXBTC15M-26MAY071015-15 | no | yes | book_gap | mushroom_v28_probability_reduce | 2.0 | -156.0 | -158.000000 | True |
| KXBTC15M-26MAY071015-15 | no | yes | book_gap | mushroom_v28_probability_reduce | -16.0 | -162.0 | -146.000000 | True |
| KXBTC15M-26MAY071015-15 | yes | yes | book_gap | mushroom_v28_exit_value_over_hold | 20.0 | 32.0 | 12.000000 | True |
| KXBTC15M-26MAY071030-30 | no | no | book_gap | mushroom_v28_probability_collapse_full | -24.0 | -24.0 | 0.000000 | False |
| KXBTC15M-26MAY071030-30 | no | no | book_gap |  | 48.0 | 48.0 | 0.000000 | False |
| KXBTC15M-26MAY071045-45 | no | no | book_gap | mushroom_v28_probability_reduce | -10.0 | 52.0 | 62.000000 | True |
| KXBTC15M-26MAY071045-45 | no | no | book_gap |  | 50.0 | 50.0 | 0.000000 | False |
| KXBTC15M-26MAY071100-00 | yes | no | book_gap | mushroom_v28_exit_value_over_hold | 4.0 | -166.0 | -170.000000 | True |
| KXBTC15M-26MAY071115-15 | yes | yes | book_gap | mushroom_v28_exit_value_over_hold | 14.0 | 32.0 | 18.000000 | True |
| KXBTC15M-26MAY071130-30 | no | no | book_gap |  | 30.0 | 30.0 | 0.000000 | False |
| KXBTC15M-26MAY071145-45 | yes | yes | book_gap | mushroom_v28_exit_value_over_hold | 44.0 | 46.0 | 2.000000 | True |
| KXBTC15M-26MAY071200-00 | no | no | book_gap | mushroom_v28_exit_value_over_hold | 42.0 | 46.0 | 4.000000 | True |
| KXBTC15M-26MAY071215-15 | no | no | book_gap | mushroom_v28_probability_reduce | -16.0 | 32.0 | 48.000000 | True |
| KXBTC15M-26MAY071215-15 | no | no | book_gap | mushroom_v28_exit_value_over_hold | 2.0 | 44.0 | 42.000000 | True |
| KXBTC15M-26MAY071215-15 | no | no | book_gap | mushroom_v28_probability_reduce | -8.0 | 40.0 | 48.000000 | True |
| KXBTC15M-26MAY071230-30 | yes | yes | book_gap | mushroom_v28_probability_reduce | -10.0 | -10.0 | 0.000000 | False |
| KXBTC15M-26MAY071230-30 | yes | yes | book_gap | mushroom_v28_probability_collapse_full | -38.0 | -38.0 | 0.000000 | False |
| KXBTC15M-26MAY071230-30 | yes | yes | book_gap |  | 40.0 | 40.0 | 0.000000 | False |
| KXBTC15M-26MAY071315-15 | yes | yes | book_gap | mushroom_v28_probability_reduce | -6.0 | 40.0 | 46.000000 | True |
| KXBTC15M-26MAY071315-15 | yes | yes | book_gap | mushroom_v28_probability_reduce | -14.0 | 38.0 | 52.000000 | True |
| KXBTC15M-26MAY071315-15 | yes | yes | book_gap | mushroom_v28_exit_value_over_hold | 32.0 | 44.0 | 12.000000 | True |
