# v28 Feature-Gate Exit Bid Suppression Watch

Research-only frozen watch. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:54:31.731321+00:00`
- Freeze UTC: `2026-05-07T07:32:00.852069+00:00`
- Candidate: `feature_gate_exit_bid_min_ge_60_suppress`
- Rule: suppress selected-side feature-gate exits when `exit_bid_min >= 60.0`.

## Interpretation

- Research-only frozen watch; it does not change live exits or entries.
- Diagnostic lane: 40 rows, 25 suppressions, delta 935.5999999999999c, helpful/harmful 22/3.
- Post-birth lane: 13 rows, 11 suppressions, delta -246.39999999999998c, blockers ['settled_lt_30', 'suppressed_decisions_lt_30', 'net_not_positive', 'delta_not_positive', 'suppressed_losers_present', 'suppressed_loss_control_cost_negative', 'full_loss_cushion_lt_3'].
- Only the post-birth lane can become forward evidence.

## diagnostic_feature_gate_exit_bid

- Settled/scored: `40`
- Suppressed exits: `25`
- Helpful/harmful suppressions: `22 / 3`
- Live selected net: `311.000000c`
- Candidate net: `1246.600000c`
- Delta vs live: `935.600000c`
- Full-loss cushion: `12`
- Blockers: `['suppressed_decisions_lt_30', 'suppressed_losers_present', 'suppressed_loss_control_cost_negative', 'diagnostic_prefreeze']`

| market | source | side | won | first exit | live c | hold c | candidate c | delta c | bid min | p_hold avg | reason counts |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY070030-30 | approved_entry | yes | True | 2026-05-07T04:23:17.847640+00:00 | -100.000000 | 78.000000 | 78.000000 | 178.000000 | 63.000000 | 0.784403 | {'mushroom_v28_exit_value_over_hold': 12, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 19, 'mushroom_v28_probability_collapse_full': 4, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 7} |
| KXBTC15M-26MAY062315-15 | approved_entry | no | True | 2026-05-07T03:03:53.641219+00:00 | -72.000000 | 97.000000 | 97.000000 | 169.000000 | 67.000000 | 0.781109 | {'mushroom_v28_probability_reduce': 20, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 35} |
| KXBTC15M-26MAY071315-15 | approved_entry | yes | True | 2026-05-07T17:10:37.610036+00:00 | -8.000000 | 143.600000 | 143.600000 | 151.600000 | 75.000000 | 0.826012 | {'mushroom_v28_probability_reduce': 24, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 41, 'mushroom_v28_exit_value_over_hold': 8, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 13} |
| KXBTC15M-26MAY070830-30 | approved_entry | no | True | 2026-05-07T12:21:08.864051+00:00 | -53.000000 | 91.000000 | 91.000000 | 144.000000 | 73.000000 | 0.798596 | {'mushroom_v28_probability_reduce': 20, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 35, 'mushroom_v28_exit_value_over_hold': 4, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 6} |
| KXBTC15M-26MAY062215-15 | approved_entry | no | True | 2026-05-07T02:02:39.227731+00:00 | 23.000000 | 159.000000 | 159.000000 | 136.000000 | 65.000000 | 0.713473 | {'mushroom_v28_probability_collapse_full': 12, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 20} |
| KXBTC15M-26MAY062045-45 | approved_entry | no | True | 2026-05-07T00:33:15.114276+00:00 | -2.000000 | 127.000000 | 127.000000 | 129.000000 | 64.000000 | 0.767832 | {'mushroom_v28_probability_reduce': 16, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 28} |
| KXBTC15M-26MAY070745-45 | approved_entry | yes | True | 2026-05-07T11:37:01.110847+00:00 | -19.000000 | 108.000000 | 108.000000 | 127.000000 | 68.000000 | 0.788411 | {'mushroom_v28_probability_reduce': 12, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 22} |
| KXBTC15M-26MAY071230-30 | approved_entry | yes | True | 2026-05-07T16:23:37.845359+00:00 | -22.000000 | 100.000000 | 100.000000 | 122.000000 | 67.000000 | 0.723591 | {'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 14, 'mushroom_v28_probability_collapse_full': 4, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 7} |
| KXBTC15M-26MAY070930-30 | approved_entry | yes | True | 2026-05-07T13:27:22.777039+00:00 | -40.000000 | 68.000000 | 68.000000 | 108.000000 | 73.000000 | 0.756617 | {'mushroom_v28_probability_reduce': 12, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 21} |
| KXBTC15M-26MAY062100-00 | approved_entry | yes | True | 2026-05-07T00:49:12.783309+00:00 | -9.000000 | 96.600000 | 96.600000 | 105.600000 | 75.000000 | 0.803171 | {'mushroom_v28_probability_reduce': 16, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 28, 'mushroom_v28_exit_value_over_hold': 8, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 13} |
| KXBTC15M-26MAY061800-00 | approved_entry | no | True | 2026-05-06T21:47:39.270716+00:00 | 6.000000 | 94.000000 | 94.000000 | 88.000000 | 70.000000 | 0.799718 | {'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 14, 'mushroom_v28_exit_value_over_hold': 4, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 7} |
| KXBTC15M-26MAY070115-15 | approved_entry | yes | True | 2026-05-07T05:07:14.490359+00:00 | 20.000000 | 96.200000 | 96.200000 | 76.200000 | 85.000000 | 0.844946 | {'mushroom_v28_exit_value_over_hold': 8, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 14} |

## post_exit_bid_birth

- Settled/scored: `13`
- Suppressed exits: `11`
- Helpful/harmful suppressions: `8 / 3`
- Live selected net: `-56.000000c`
- Candidate net: `-302.400000c`
- Delta vs live: `-246.400000c`
- Full-loss cushion: `0`
- Blockers: `['settled_lt_30', 'suppressed_decisions_lt_30', 'net_not_positive', 'delta_not_positive', 'suppressed_losers_present', 'suppressed_loss_control_cost_negative', 'full_loss_cushion_lt_3']`

| market | source | side | won | first exit | live c | hold c | candidate c | delta c | bid min | p_hold avg | reason counts |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071315-15 | approved_entry | yes | True | 2026-05-07T17:10:37.610036+00:00 | -8.000000 | 143.600000 | 143.600000 | 151.600000 | 75.000000 | 0.826012 | {'mushroom_v28_probability_reduce': 24, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 41, 'mushroom_v28_exit_value_over_hold': 8, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 13} |
| KXBTC15M-26MAY070830-30 | approved_entry | no | True | 2026-05-07T12:21:08.864051+00:00 | -53.000000 | 91.000000 | 91.000000 | 144.000000 | 73.000000 | 0.798596 | {'mushroom_v28_probability_reduce': 20, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 35, 'mushroom_v28_exit_value_over_hold': 4, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 6} |
| KXBTC15M-26MAY070745-45 | approved_entry | yes | True | 2026-05-07T11:37:01.110847+00:00 | -19.000000 | 108.000000 | 108.000000 | 127.000000 | 68.000000 | 0.788411 | {'mushroom_v28_probability_reduce': 12, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 22} |
| KXBTC15M-26MAY071230-30 | approved_entry | yes | True | 2026-05-07T16:23:37.845359+00:00 | -22.000000 | 100.000000 | 100.000000 | 122.000000 | 67.000000 | 0.723591 | {'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 14, 'mushroom_v28_probability_collapse_full': 4, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 7} |
| KXBTC15M-26MAY070930-30 | approved_entry | yes | True | 2026-05-07T13:27:22.777039+00:00 | -40.000000 | 68.000000 | 68.000000 | 108.000000 | 73.000000 | 0.756617 | {'mushroom_v28_probability_reduce': 12, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 21} |
| KXBTC15M-26MAY071045-45 | approved_entry | no | True | 2026-05-07T14:31:53.315753+00:00 | 23.000000 | 91.000000 | 91.000000 | 68.000000 | 66.000000 | 0.771498 | {'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 14} |
| KXBTC15M-26MAY070915-15 | approved_entry | no | True | 2026-05-07T13:02:17.635811+00:00 | 56.000000 | 124.000000 | 124.000000 | 68.000000 | 65.000000 | 0.785310 | {'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 14} |
| KXBTC15M-26MAY071030-30 | approved_entry | no | True | 2026-05-07T14:16:37.960097+00:00 | 37.000000 | 104.000000 | 104.000000 | 67.000000 | 64.000000 | 0.773009 | {'mushroom_v28_probability_reduce': 16, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 26} |
| KXBTC15M-26MAY070615-15 | rejected_actionable | yes | False | 2026-05-07T10:09:39.154775+00:00 | -9.000000 | -161.000000 | -161.000000 | -152.000000 | 76.000000 | 0.775618 | {'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 14} |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | 2026-05-07T14:06:02.487135+00:00 | -32.000000 | -494.000000 | -494.000000 | -462.000000 | 74.000000 | 0.783026 | {'mushroom_v28_exit_value_over_hold': 4, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 7, 'mushroom_v28_probability_reduce': 16, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 28} |
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | 2026-05-07T14:52:08.181653+00:00 | -23.000000 | -511.000000 | -511.000000 | -488.000000 | 77.000000 | 0.800165 | {'mushroom_v28_probability_reduce': 12, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 20, 'mushroom_v28_exit_value_over_hold': 8, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 14} |
