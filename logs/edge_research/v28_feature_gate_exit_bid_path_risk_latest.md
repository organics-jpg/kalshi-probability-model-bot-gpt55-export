# v28 Feature-Gate Exit-Bid Path Risk

Research-only path-risk audit. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:54:32.245439+00:00`

## Interpretation

- Research-only path-risk audit; no live bot changes or orders.
- Diagnostic suppressed rows with path: 25/25; worst post-exit bid excursion -77.0c versus exit bid.
- High exit-bid suppression remains a watch-only exit repair. Large adverse marks would require a deployable disaster guard or delayed-recheck rule before any live-readiness discussion.

## diagnostic_feature_gate_exit_bid

- Suppressed rows: `25`
- Rows with post-exit path: `25`
- Delta vs live: `935.60c`
- Avg min after exit bid: `-21.52c`
- Worst min after exit bid: `-77.00c`
- Adverse 10/25/50c rows: `11 / 8 / 6`
- Blockers: `['suppressed_rows_lt_30', 'large_adverse_marks_present']`

| market | side | won | exit bid | min bid | max bid | last bid | min-after c | max-after c | delta live c | path pts | reasons |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071100-00 | yes | False | 77.00 | 0 | 93 | 0 | -77.00 | 16.00 | -488.00 | 32 | {'mushroom_v28_exit_value_over_hold': 8, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 14, 'mushroom_v28_probability_reduce': 12, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 20} |
| KXBTC15M-26MAY070615-15 | yes | False | 76.00 | 0 | 78 | 0 | -76.00 | 2.00 | -152.00 | 22 | {'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 14} |
| KXBTC15M-26MAY071015-15 | no | False | 74.00 | 0 | 85 | 0 | -74.00 | 11.00 | -462.00 | 36 | {'mushroom_v28_exit_value_over_hold': 4, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 7, 'mushroom_v28_probability_reduce': 16, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 28} |
| KXBTC15M-26MAY062115-15 | yes | True | 70.00 | 14 | 100 | 100 | -56.00 | 30.00 | 70.80 | 48 | {'mushroom_v28_exit_value_over_hold': 8, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 13, 'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 14} |
| KXBTC15M-26MAY062100-00 | yes | True | 75.00 | 20 | 99 | 99 | -55.00 | 24.00 | 105.60 | 44 | {'mushroom_v28_exit_value_over_hold': 8, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 13, 'mushroom_v28_probability_reduce': 16, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 28} |
| KXBTC15M-26MAY062015-15 | no | True | 60.00 | 9 | 99 | 99 | -51.00 | 39.00 | 69.00 | 24 | {'mushroom_v28_probability_collapse_full': 8, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 13, 'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 13} |
| KXBTC15M-26MAY061800-00 | no | True | 70.00 | 23 | 100 | 100 | -47.00 | 30.00 | 88.00 | 50 | {'mushroom_v28_exit_value_over_hold': 4, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 7, 'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 14} |
| KXBTC15M-26MAY070830-30 | no | True | 73.00 | 43 | 100 | 99 | -30.00 | 27.00 | 144.00 | 36 | {'mushroom_v28_exit_value_over_hold': 4, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 6, 'mushroom_v28_probability_reduce': 20, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 35} |
| KXBTC15M-26MAY070930-30 | yes | True | 73.00 | 52 | 100 | 100 | -21.00 | 27.00 | 108.00 | 10 | {'mushroom_v28_probability_reduce': 12, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 21} |
| KXBTC15M-26MAY070915-15 | no | True | 65.00 | 50 | 100 | 100 | -15.00 | 35.00 | 68.00 | 50 | {'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 14} |
| KXBTC15M-26MAY062030-30 | no | True | 76.00 | 65 | 100 | 100 | -11.00 | 24.00 | 48.00 | 43 | {'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 14} |
| KXBTC15M-26MAY062315-15 | no | True | 67.00 | 58 | 100 | 100 | -9.00 | 33.00 | 169.00 | 45 | {'mushroom_v28_probability_reduce': 20, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 35} |
| KXBTC15M-26MAY062215-15 | no | True | 65.00 | 57 | 100 | 100 | -8.00 | 35.00 | 136.00 | 49 | {'mushroom_v28_probability_collapse_full': 12, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 20} |
| KXBTC15M-26MAY070115-15 | yes | True | 85.00 | 79 | 100 | 100 | -6.00 | 15.00 | 76.20 | 31 | {'mushroom_v28_exit_value_over_hold': 8, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 14} |
| KXBTC15M-26MAY071315-15 | yes | True | 75.00 | 71 | 100 | 100 | -4.00 | 25.00 | 151.60 | 17 | {'mushroom_v28_exit_value_over_hold': 8, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 13, 'mushroom_v28_probability_reduce': 24, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 41} |
| KXBTC15M-26MAY061400-00 | no | True | 84.00 | 81 | 100 | 100 | -3.00 | 16.00 | 32.00 | 12 | {'mushroom_v28_exit_value_over_hold': 4, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 7} |
| KXBTC15M-26MAY062200-00 | no | True | 98.00 | 95 | 100 | 100 | -3.00 | 2.00 | 6.40 | 12 | {'mushroom_v28_exit_value_over_hold': 4, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 7} |
| KXBTC15M-26MAY062045-45 | no | True | 64.00 | 63 | 100 | 100 | -1.00 | 36.00 | 129.00 | 47 | {'mushroom_v28_probability_reduce': 16, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 28} |
| KXBTC15M-26MAY070745-45 | yes | True | 68.00 | 67 | 100 | 100 | -1.00 | 32.00 | 127.00 | 32 | {'mushroom_v28_probability_reduce': 12, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 22} |
| KXBTC15M-26MAY061615-15 | yes | True | 97.00 | 96 | 100 | 100 | -1.00 | 3.00 | 8.00 | 27 | {'mushroom_v28_exit_value_over_hold': 8, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 13} |
| KXBTC15M-26MAY071230-30 | yes | True | 67.00 | 67 | 100 | 100 | 0.00 | 33.00 | 122.00 | 25 | {'mushroom_v28_probability_collapse_full': 4, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 7, 'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 14} |
| KXBTC15M-26MAY071045-45 | no | True | 66.00 | 67 | 100 | 100 | 1.00 | 34.00 | 68.00 | 52 | {'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 14} |
| KXBTC15M-26MAY070030-30 | yes | True | 63.00 | 66 | 100 | 100 | 3.00 | 37.00 | 178.00 | 26 | {'mushroom_v28_exit_value_over_hold': 12, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 19, 'mushroom_v28_probability_collapse_full': 4, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 7} |
| KXBTC15M-26MAY071030-30 | no | True | 64.00 | 67 | 100 | 100 | 3.00 | 36.00 | 67.00 | 53 | {'mushroom_v28_probability_reduce': 16, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 26} |
| KXBTC15M-26MAY061815-15 | no | True | 66.00 | 70 | 100 | 100 | 4.00 | 34.00 | 66.00 | 40 | {'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 14} |

## post_exit_bid_birth

- Suppressed rows: `11`
- Rows with post-exit path: `11`
- Delta vs live: `-246.40c`
- Avg min after exit bid: `-26.73c`
- Worst min after exit bid: `-77.00c`
- Adverse 10/25/50c rows: `6 / 4 / 3`
- Blockers: `['post_birth_rows_required', 'suppressed_rows_lt_30', 'large_adverse_marks_present']`

| market | side | won | exit bid | min bid | max bid | last bid | min-after c | max-after c | delta live c | path pts | reasons |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071100-00 | yes | False | 77.00 | 0 | 93 | 0 | -77.00 | 16.00 | -488.00 | 32 | {'mushroom_v28_exit_value_over_hold': 8, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 14, 'mushroom_v28_probability_reduce': 12, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 20} |
| KXBTC15M-26MAY070615-15 | yes | False | 76.00 | 0 | 78 | 0 | -76.00 | 2.00 | -152.00 | 22 | {'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 14} |
| KXBTC15M-26MAY071015-15 | no | False | 74.00 | 0 | 85 | 0 | -74.00 | 11.00 | -462.00 | 36 | {'mushroom_v28_exit_value_over_hold': 4, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 7, 'mushroom_v28_probability_reduce': 16, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 28} |
| KXBTC15M-26MAY070830-30 | no | True | 73.00 | 43 | 100 | 99 | -30.00 | 27.00 | 144.00 | 36 | {'mushroom_v28_exit_value_over_hold': 4, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 6, 'mushroom_v28_probability_reduce': 20, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 35} |
| KXBTC15M-26MAY070930-30 | yes | True | 73.00 | 52 | 100 | 100 | -21.00 | 27.00 | 108.00 | 10 | {'mushroom_v28_probability_reduce': 12, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 21} |
| KXBTC15M-26MAY070915-15 | no | True | 65.00 | 50 | 100 | 100 | -15.00 | 35.00 | 68.00 | 50 | {'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 14} |
| KXBTC15M-26MAY071315-15 | yes | True | 75.00 | 71 | 100 | 100 | -4.00 | 25.00 | 151.60 | 17 | {'mushroom_v28_exit_value_over_hold': 8, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 13, 'mushroom_v28_probability_reduce': 24, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 41} |
| KXBTC15M-26MAY070745-45 | yes | True | 68.00 | 67 | 100 | 100 | -1.00 | 32.00 | 127.00 | 32 | {'mushroom_v28_probability_reduce': 12, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 22} |
| KXBTC15M-26MAY071230-30 | yes | True | 67.00 | 67 | 100 | 100 | 0.00 | 33.00 | 122.00 | 25 | {'mushroom_v28_probability_collapse_full': 4, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 7, 'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 14} |
| KXBTC15M-26MAY071045-45 | no | True | 66.00 | 67 | 100 | 100 | 1.00 | 34.00 | 68.00 | 52 | {'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 14} |
| KXBTC15M-26MAY071030-30 | no | True | 64.00 | 67 | 100 | 100 | 3.00 | 36.00 | 67.00 | 53 | {'mushroom_v28_probability_reduce': 16, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 26} |
