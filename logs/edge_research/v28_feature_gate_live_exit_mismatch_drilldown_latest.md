# v28 Feature-Gate Live Exit Mismatch Drilldown

Research-only attribution drilldown. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:54:28.575584+00:00`
- Candidate: `post_feature_freeze_entry_raw03_recross70_abs075`
- Target tag: `theory_win_selected_side_live_loss`

## Interpretation

- This is an attribution drilldown only; it does not change live exits or entries.
- 12 theory-win/live-selected-loss markets total 287.0c theoretical settlement PnL but -458.0c live selected-side PnL.
- Classifications: {'exit_policy_error': 12, 'value_over_hold_clipped_winner': 6, 'same_side_state_churn': 9, 'exited_before_settlement': 12, 'theory_win_selected_live_loss': 12, 'probability_reduce_clipped_winner': 10, 'opposite_side_state_churn': 1}.
- Exit reasons: {'mushroom_v28_exit_value_over_hold': 44, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 70, 'mushroom_v28_probability_collapse_full': 20, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 34, 'mushroom_v28_probability_reduce': 160, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 278}.

## Markets

| market | source | side | theory c | live selected c | per contract c | entry | exit | clip vs hold/ct | exits | reasons | classes |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY070030-30 | approved_entry | yes | 15.000000 | -100.000000 | -16.666667 | 84.333333 | 70.333333 | 32.333333 | 42 | {'mushroom_v28_exit_value_over_hold': 12, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 19, 'mushroom_v28_probability_collapse_full': 4, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 7} | exit_policy_error, value_over_hold_clipped_winner, same_side_state_churn, exited_before_settlement, theory_win_selected_live_loss |
| KXBTC15M-26MAY062315-15 | approved_entry | no | 15.000000 | -72.000000 | -12.000000 | 80.666667 | 71.833333 | 31.333333 | 55 | {'mushroom_v28_probability_reduce': 20, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 35} | exit_policy_error, probability_reduce_clipped_winner, same_side_state_churn, exited_before_settlement, theory_win_selected_live_loss |
| KXBTC15M-26MAY071000-00 | approved_entry | no | 27.000000 | -72.000000 | -6.000000 | 80.000000 | 72.000000 | 26.000000 | 96 | {'mushroom_v28_probability_reduce': 24, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 41, 'mushroom_v28_probability_collapse_full': 4, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 7, 'mushroom_v28_exit_value_over_hold': 8, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 12} | exit_policy_error, probability_reduce_clipped_winner, value_over_hold_clipped_winner, same_side_state_churn, exited_before_settlement, theory_win_selected_live_loss |
| KXBTC15M-26MAY070830-30 | approved_entry | no | 21.000000 | -53.000000 | -8.833333 | 81.666667 | 76.000000 | 27.166667 | 65 | {'mushroom_v28_probability_reduce': 20, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 35, 'mushroom_v28_exit_value_over_hold': 4, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 6} | exit_policy_error, probability_reduce_clipped_winner, value_over_hold_clipped_winner, same_side_state_churn, exited_before_settlement, theory_win_selected_live_loss |
| KXBTC15M-26MAY062015-15 | approved_entry | no | 56.000000 | -47.000000 | -23.500000 | 86.000000 | 65.500000 | 37.500000 | 42 | {'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 13, 'mushroom_v28_probability_collapse_full': 8, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 13} | exit_policy_error, probability_reduce_clipped_winner, opposite_side_state_churn, exited_before_settlement, theory_win_selected_live_loss |
| KXBTC15M-26MAY070930-30 | approved_entry | yes | 17.000000 | -40.000000 | -10.000000 | 80.000000 | 73.000000 | 30.000000 | 33 | {'mushroom_v28_probability_reduce': 12, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 21} | exit_policy_error, probability_reduce_clipped_winner, exited_before_settlement, theory_win_selected_live_loss |
| KXBTC15M-26MAY071230-30 | approved_entry | yes | 21.000000 | -22.000000 | -3.666667 | 80.666667 | 69.500000 | 23.000000 | 33 | {'mushroom_v28_probability_reduce': 8, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 14, 'mushroom_v28_probability_collapse_full': 4, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 7} | exit_policy_error, probability_reduce_clipped_winner, same_side_state_churn, exited_before_settlement, theory_win_selected_live_loss |
| KXBTC15M-26MAY070745-45 | approved_entry | yes | 30.000000 | -19.000000 | -3.166667 | 79.333333 | 68.250000 | 23.833333 | 34 | {'mushroom_v28_probability_reduce': 12, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 22} | exit_policy_error, probability_reduce_clipped_winner, same_side_state_churn, exited_before_settlement, theory_win_selected_live_loss |
| KXBTC15M-26MAY061400-00 | approved_entry | no | 10.000000 | -14.000000 | -7.000000 | 89.000000 | 84.000000 | 18.000000 | 11 | {'mushroom_v28_exit_value_over_hold': 4, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 7} | exit_policy_error, value_over_hold_clipped_winner, exited_before_settlement, theory_win_selected_live_loss |
| KXBTC15M-26MAY062100-00 | approved_entry | yes | 37.000000 | -9.000000 | -1.500000 | 81.000000 | 82.400000 | 20.500000 | 65 | {'mushroom_v28_probability_reduce': 16, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 28, 'mushroom_v28_exit_value_over_hold': 8, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 13} | exit_policy_error, probability_reduce_clipped_winner, value_over_hold_clipped_winner, same_side_state_churn, exited_before_settlement, theory_win_selected_live_loss |
| KXBTC15M-26MAY071315-15 | approved_entry | yes | 20.000000 | -8.000000 | -1.000000 | 79.000000 | 81.050000 | 22.000000 | 86 | {'mushroom_v28_probability_reduce': 24, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 41, 'mushroom_v28_exit_value_over_hold': 8, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 13} | exit_policy_error, probability_reduce_clipped_winner, value_over_hold_clipped_winner, same_side_state_churn, exited_before_settlement, theory_win_selected_live_loss |
| KXBTC15M-26MAY062045-45 | approved_entry | no | 18.000000 | -2.000000 | -0.333333 | 76.000000 | 67.750000 | 24.333333 | 44 | {'mushroom_v28_probability_reduce': 16, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 28} | exit_policy_error, probability_reduce_clipped_winner, same_side_state_churn, exited_before_settlement, theory_win_selected_live_loss |

## Exit Event Tails

### KXBTC15M-26MAY070030-30

| ts | event | reason | result | trigger | bid | p_hold | drawdown | hold net | depth | book age |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-05-07T04:26:54.903371+00:00 | exit_execution_deferred | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | retry_signal_cleared | 91 | None | None | None | None | 550.00 | 15.000000 |
| 2026-05-07T04:27:06.845989+00:00 | exit_signal_seen | mushroom_v28_exit_value_over_hold |  | 85 | 85 | 0.836353 | 4.364744 | 82.635256 | 10.00 | 15.000000 |
| 2026-05-07T04:27:06.845989+00:00 | exit_snapshot_built | mushroom_v28_exit_value_over_hold |  | 85 | 85 | 0.836353 | 4.364744 | 82.635256 | 10.00 | 15.000000 |
| 2026-05-07T04:27:06.846988+00:00 | exit_capacity_estimated | mushroom_v28_exit_value_over_hold |  | 85 | 85 | 0.836353 | 4.364744 | 82.635256 | 10.00 | 15.000000 |
| 2026-05-07T04:27:06.846988+00:00 | exit_plan_built | mushroom_v28_exit_value_over_hold |  | 85 | 85 | 0.836353 | 4.364744 | 82.635256 | 10.00 | 15.000000 |
| 2026-05-07T04:27:06.859609+00:00 | exit_submit_start | mushroom_v28_exit_value_over_hold_single_shot_visible_depth |  | 85 | None | None | None | None | 10.00 | 15.000000 |
| 2026-05-07T04:27:06.859609+00:00 | order_submit_start | mushroom_v28_exit_value_over_hold_single_shot_visible_depth |  | 85 | None | None | None | None | 10.00 | 15.000000 |
| 2026-05-07T04:27:06.960734+00:00 | order_submit_success | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 85 | None | None | None | None | 10.00 | 15.000000 |
| 2026-05-07T04:27:06.961772+00:00 | exit_submit_full | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 85 | None | None | None | None | 10.00 | 15.000000 |
| 2026-05-07T04:27:06.961772+00:00 | fill_full | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 85 | None | None | None | None | 10.00 | 15.000000 |
| 2026-05-07T04:27:06.961772+00:00 | exit_submit_success | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 85 | None | None | None | None | 10.00 | 15.000000 |
| 2026-05-07T04:27:06.971194+00:00 | exit_reconciled | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 85 | None | None | None | None | 10.00 | 15.000000 |

### KXBTC15M-26MAY062315-15

| ts | event | reason | result | trigger | bid | p_hold | drawdown | hold net | depth | book age |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-05-07T03:08:11.805821+00:00 | exit_reconciled | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 74 | None | None | None | None | 50.00 | 125.000000 |
| 2026-05-07T03:08:12.640964+00:00 | exit_signal_seen | mushroom_v28_probability_reduce |  | 75 | 75 | 0.793309 | 3.669125 | 78.330875 | 4.00 | 0.000000 |
| 2026-05-07T03:08:12.640964+00:00 | exit_snapshot_built | mushroom_v28_probability_reduce |  | 75 | 75 | 0.793309 | 3.669125 | 78.330875 | 4.00 | 0.000000 |
| 2026-05-07T03:08:12.641964+00:00 | exit_capacity_estimated | mushroom_v28_probability_reduce |  | 75 | 75 | 0.793309 | 3.669125 | 78.330875 | 4.00 | 0.000000 |
| 2026-05-07T03:08:12.641964+00:00 | exit_plan_built | mushroom_v28_probability_reduce |  | 75 | 75 | 0.793309 | 3.669125 | 78.330875 | 4.00 | 0.000000 |
| 2026-05-07T03:08:12.644200+00:00 | exit_submit_start | mushroom_v28_probability_reduce_single_shot_visible_depth |  | 75 | None | None | None | None | 4.00 | 0.000000 |
| 2026-05-07T03:08:12.644200+00:00 | order_submit_start | mushroom_v28_probability_reduce_single_shot_visible_depth |  | 75 | None | None | None | None | 4.00 | 0.000000 |
| 2026-05-07T03:08:12.735807+00:00 | order_submit_success | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 75 | None | None | None | None | 4.00 | 0.000000 |
| 2026-05-07T03:08:12.735807+00:00 | exit_submit_full | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 75 | None | None | None | None | 4.00 | 0.000000 |
| 2026-05-07T03:08:12.735807+00:00 | fill_full | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 75 | None | None | None | None | 4.00 | 0.000000 |
| 2026-05-07T03:08:12.736808+00:00 | exit_submit_success | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 75 | None | None | None | None | 4.00 | 0.000000 |
| 2026-05-07T03:08:12.742808+00:00 | exit_reconciled | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 75 | None | None | None | None | 4.00 | 0.000000 |

### KXBTC15M-26MAY071000-00

| ts | event | reason | result | trigger | bid | p_hold | drawdown | hold net | depth | book age |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-05-07T13:58:05.753622+00:00 | exit_execution_deferred | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | ioc_zero_fill | 93 | None | None | None | None | 10.00 | 16.000000 |
| 2026-05-07T13:58:05.753622+00:00 | exit_execution_deferred | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | retry_signal_cleared | 93 | None | None | None | None | 10.00 | 16.000000 |
| 2026-05-07T13:58:07.704501+00:00 | exit_signal_seen | mushroom_v28_exit_value_over_hold |  | 93 | 93 | 0.920444 | -13.044359 | 91.044359 | 55.00 | 31.000000 |
| 2026-05-07T13:58:07.706514+00:00 | exit_snapshot_built | mushroom_v28_exit_value_over_hold |  | 93 | 93 | 0.920444 | -13.044359 | 91.044359 | 55.00 | 31.000000 |
| 2026-05-07T13:58:07.708523+00:00 | exit_capacity_estimated | mushroom_v28_exit_value_over_hold |  | 93 | 93 | 0.920444 | -13.044359 | 91.044359 | 55.00 | 31.000000 |
| 2026-05-07T13:58:07.708523+00:00 | exit_plan_built | mushroom_v28_exit_value_over_hold |  | 93 | 93 | 0.920444 | -13.044359 | 91.044359 | 55.00 | 31.000000 |
| 2026-05-07T13:58:07.712542+00:00 | exit_submit_start | mushroom_v28_exit_value_over_hold_single_shot_visible_depth |  | 93 | None | None | None | None | 55.00 | 31.000000 |
| 2026-05-07T13:58:07.712542+00:00 | order_submit_start | mushroom_v28_exit_value_over_hold_single_shot_visible_depth |  | 93 | None | None | None | None | 55.00 | 31.000000 |
| 2026-05-07T13:58:07.770178+00:00 | order_submit_success | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | canceled | 93 | None | None | None | None | 55.00 | 31.000000 |
| 2026-05-07T13:58:07.772185+00:00 | exit_submit_zero_fill | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | ioc_zero_fill | 93 | None | None | None | None | 55.00 | 31.000000 |
| 2026-05-07T13:58:07.772185+00:00 | exit_execution_deferred | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | ioc_zero_fill | 93 | None | None | None | None | 55.00 | 31.000000 |
| 2026-05-07T13:58:07.772185+00:00 | exit_execution_deferred | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | retry_signal_cleared | 93 | None | None | None | None | 55.00 | 31.000000 |

### KXBTC15M-26MAY070830-30

| ts | event | reason | result | trigger | bid | p_hold | drawdown | hold net | depth | book age |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-05-07T12:25:27.995209+00:00 | exit_reconciled | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 78 | None | None | None | None | 2.00 | 78.000000 |
| 2026-05-07T12:25:28.863572+00:00 | exit_signal_seen | mushroom_v28_probability_reduce |  | 76 | 76 | 0.784478 | 5.552206 | 77.447794 | 40.00 | 15.000000 |
| 2026-05-07T12:25:28.864570+00:00 | exit_snapshot_built | mushroom_v28_probability_reduce |  | 76 | 76 | 0.784478 | 5.552206 | 77.447794 | 40.00 | 15.000000 |
| 2026-05-07T12:25:28.865570+00:00 | exit_capacity_estimated | mushroom_v28_probability_reduce |  | 76 | 76 | 0.784478 | 5.552206 | 77.447794 | 40.00 | 15.000000 |
| 2026-05-07T12:25:28.865570+00:00 | exit_plan_built | mushroom_v28_probability_reduce |  | 76 | 76 | 0.784478 | 5.552206 | 77.447794 | 40.00 | 15.000000 |
| 2026-05-07T12:25:28.868569+00:00 | exit_submit_start | mushroom_v28_probability_reduce_single_shot_visible_depth |  | 76 | None | None | None | None | 40.00 | 15.000000 |
| 2026-05-07T12:25:28.869569+00:00 | order_submit_start | mushroom_v28_probability_reduce_single_shot_visible_depth |  | 76 | None | None | None | None | 40.00 | 15.000000 |
| 2026-05-07T12:25:28.936901+00:00 | order_submit_success | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 76 | None | None | None | None | 40.00 | 15.000000 |
| 2026-05-07T12:25:28.937901+00:00 | exit_submit_full | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 76 | None | None | None | None | 40.00 | 15.000000 |
| 2026-05-07T12:25:28.937901+00:00 | fill_full | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 76 | None | None | None | None | 40.00 | 15.000000 |
| 2026-05-07T12:25:28.939073+00:00 | exit_submit_success | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 76 | None | None | None | None | 40.00 | 15.000000 |
| 2026-05-07T12:25:28.949253+00:00 | exit_reconciled | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 76 | None | None | None | None | 40.00 | 15.000000 |

### KXBTC15M-26MAY062015-15

| ts | event | reason | result | trigger | bid | p_hold | drawdown | hold net | depth | book age |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-05-07T00:09:10.653383+00:00 | exit_execution_deferred | mushroom_v28_probability_collapse_full_single_shot_visible_depth | retry_signal_cleared | 66 | None | None | None | None | 100.00 | 0.000000 |
| 2026-05-07T00:09:11.593474+00:00 | exit_signal_seen | mushroom_v28_probability_collapse_full |  | 60 | 60 | 0.595741 | 26.425934 | 58.574066 | 100.00 | 0.000000 |
| 2026-05-07T00:09:11.594483+00:00 | exit_snapshot_built | mushroom_v28_probability_collapse_full |  | 60 | 60 | 0.595741 | 26.425934 | 58.574066 | 100.00 | 0.000000 |
| 2026-05-07T00:09:11.595481+00:00 | exit_capacity_estimated | mushroom_v28_probability_collapse_full |  | 60 | 60 | 0.595741 | 26.425934 | 58.574066 | 100.00 | 0.000000 |
| 2026-05-07T00:09:11.596480+00:00 | exit_plan_built | mushroom_v28_probability_collapse_full |  | 60 | 60 | 0.595741 | 26.425934 | 58.574066 | 100.00 | 0.000000 |
| 2026-05-07T00:09:11.599481+00:00 | exit_submit_start | mushroom_v28_probability_collapse_full_single_shot_visible_depth |  | 60 | None | None | None | None | 100.00 | 0.000000 |
| 2026-05-07T00:09:11.600480+00:00 | order_submit_start | mushroom_v28_probability_collapse_full_single_shot_visible_depth |  | 60 | None | None | None | None | 100.00 | 0.000000 |
| 2026-05-07T00:09:11.658450+00:00 | order_submit_success | mushroom_v28_probability_collapse_full_single_shot_visible_depth | executed | 60 | None | None | None | None | 100.00 | 0.000000 |
| 2026-05-07T00:09:11.659449+00:00 | exit_submit_full | mushroom_v28_probability_collapse_full_single_shot_visible_depth | executed | 60 | None | None | None | None | 100.00 | 0.000000 |
| 2026-05-07T00:09:11.659449+00:00 | fill_full | mushroom_v28_probability_collapse_full_single_shot_visible_depth | executed | 60 | None | None | None | None | 100.00 | 0.000000 |
| 2026-05-07T00:09:11.660452+00:00 | exit_submit_success | mushroom_v28_probability_collapse_full_single_shot_visible_depth | executed | 60 | None | None | None | None | 100.00 | 0.000000 |
| 2026-05-07T00:09:11.670450+00:00 | exit_reconciled | mushroom_v28_probability_collapse_full_single_shot_visible_depth | executed | 60 | None | None | None | None | 100.00 | 0.000000 |

### KXBTC15M-26MAY070930-30

| ts | event | reason | result | trigger | bid | p_hold | drawdown | hold net | depth | book age |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-05-07T13:27:22.937401+00:00 | exit_reconciled | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 73 | None | None | None | None | 50.00 | 79.000000 |
| 2026-05-07T13:27:23.774047+00:00 | exit_signal_seen | mushroom_v28_probability_reduce |  | 73 | 73 | 0.748870 | 5.112974 | 73.887026 | 88.61 | 15.000000 |
| 2026-05-07T13:27:23.774047+00:00 | exit_snapshot_built | mushroom_v28_probability_reduce |  | 73 | 73 | 0.748870 | 5.112974 | 73.887026 | 88.61 | 15.000000 |
| 2026-05-07T13:27:23.779282+00:00 | exit_capacity_estimated | mushroom_v28_probability_reduce |  | 73 | 73 | 0.748870 | 5.112974 | 73.887026 | 88.61 | 15.000000 |
| 2026-05-07T13:27:23.779282+00:00 | exit_plan_built | mushroom_v28_probability_reduce |  | 73 | 73 | 0.748870 | 5.112974 | 73.887026 | 88.61 | 15.000000 |
| 2026-05-07T13:27:23.789838+00:00 | exit_submit_start | mushroom_v28_probability_reduce_single_shot_visible_depth |  | 73 | None | None | None | None | 88.61 | 15.000000 |
| 2026-05-07T13:27:23.789838+00:00 | order_submit_start | mushroom_v28_probability_reduce_single_shot_visible_depth |  | 73 | None | None | None | None | 88.61 | 15.000000 |
| 2026-05-07T13:27:23.856869+00:00 | order_submit_success | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 73 | None | None | None | None | 88.61 | 15.000000 |
| 2026-05-07T13:27:23.857887+00:00 | exit_submit_full | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 73 | None | None | None | None | 88.61 | 15.000000 |
| 2026-05-07T13:27:23.857887+00:00 | fill_full | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 73 | None | None | None | None | 88.61 | 15.000000 |
| 2026-05-07T13:27:23.858904+00:00 | exit_submit_success | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 73 | None | None | None | None | 88.61 | 15.000000 |
| 2026-05-07T13:27:23.872253+00:00 | exit_reconciled | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 73 | None | None | None | None | 88.61 | 15.000000 |

### KXBTC15M-26MAY071230-30

| ts | event | reason | result | trigger | bid | p_hold | drawdown | hold net | depth | book age |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-05-07T16:23:37.972830+00:00 | exit_reconciled | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 72 | None | None | None | None | 2655.93 | 62.000000 |
| 2026-05-07T16:24:31.846590+00:00 | exit_signal_seen | mushroom_v28_probability_collapse_full |  | 67 | 67 | 0.666135 | 18.386512 | 65.613488 | 760.00 | 16.000000 |
| 2026-05-07T16:24:31.846590+00:00 | exit_snapshot_built | mushroom_v28_probability_collapse_full |  | 67 | 67 | 0.666135 | 18.386512 | 65.613488 | 760.00 | 16.000000 |
| 2026-05-07T16:24:31.847589+00:00 | exit_capacity_estimated | mushroom_v28_probability_collapse_full |  | 67 | 67 | 0.666135 | 18.386512 | 65.613488 | 760.00 | 16.000000 |
| 2026-05-07T16:24:31.847589+00:00 | exit_plan_built | mushroom_v28_probability_collapse_full |  | 67 | 67 | 0.666135 | 18.386512 | 65.613488 | 760.00 | 16.000000 |
| 2026-05-07T16:24:31.849588+00:00 | exit_submit_start | mushroom_v28_probability_collapse_full_single_shot_visible_depth |  | 67 | None | None | None | None | 760.00 | 16.000000 |
| 2026-05-07T16:24:31.849588+00:00 | order_submit_start | mushroom_v28_probability_collapse_full_single_shot_visible_depth |  | 67 | None | None | None | None | 760.00 | 16.000000 |
| 2026-05-07T16:24:31.897557+00:00 | order_submit_success | mushroom_v28_probability_collapse_full_single_shot_visible_depth | executed | 67 | None | None | None | None | 760.00 | 16.000000 |
| 2026-05-07T16:24:31.897557+00:00 | exit_submit_full | mushroom_v28_probability_collapse_full_single_shot_visible_depth | executed | 67 | None | None | None | None | 760.00 | 16.000000 |
| 2026-05-07T16:24:31.898556+00:00 | fill_full | mushroom_v28_probability_collapse_full_single_shot_visible_depth | executed | 67 | None | None | None | None | 760.00 | 16.000000 |
| 2026-05-07T16:24:31.898556+00:00 | exit_submit_success | mushroom_v28_probability_collapse_full_single_shot_visible_depth | executed | 67 | None | None | None | None | 760.00 | 16.000000 |
| 2026-05-07T16:24:31.904557+00:00 | exit_reconciled | mushroom_v28_probability_collapse_full_single_shot_visible_depth | executed | 67 | None | None | None | None | 760.00 | 16.000000 |

### KXBTC15M-26MAY070745-45

| ts | event | reason | result | trigger | bid | p_hold | drawdown | hold net | depth | book age |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-05-07T11:37:02.051440+00:00 | exit_reconciled | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 68 | None | None | None | None | 74.00 | 31.000000 |
| 2026-05-07T11:37:02.054439+00:00 | exit_signal_seen | mushroom_v28_probability_reduce |  | 68 | 68 | 0.788457 | 1.154256 | 77.845744 | 60.00 | 78.000000 |
| 2026-05-07T11:37:02.054439+00:00 | exit_snapshot_built | mushroom_v28_probability_reduce |  | 68 | 68 | 0.788457 | 1.154256 | 77.845744 | 60.00 | 78.000000 |
| 2026-05-07T11:37:02.055440+00:00 | exit_capacity_estimated | mushroom_v28_probability_reduce |  | 68 | 68 | 0.788457 | 1.154256 | 77.845744 | 60.00 | 78.000000 |
| 2026-05-07T11:37:02.055440+00:00 | exit_plan_built | mushroom_v28_probability_reduce |  | 68 | 68 | 0.788457 | 1.154256 | 77.845744 | 60.00 | 78.000000 |
| 2026-05-07T11:37:02.057440+00:00 | exit_submit_start | mushroom_v28_probability_reduce_single_shot_visible_depth |  | 68 | None | None | None | None | 60.00 | 78.000000 |
| 2026-05-07T11:37:02.058441+00:00 | order_submit_start | mushroom_v28_probability_reduce_single_shot_visible_depth |  | 68 | None | None | None | None | 60.00 | 78.000000 |
| 2026-05-07T11:37:02.103592+00:00 | order_submit_success | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 68 | None | None | None | None | 60.00 | 78.000000 |
| 2026-05-07T11:37:02.104592+00:00 | exit_submit_full | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 68 | None | None | None | None | 60.00 | 78.000000 |
| 2026-05-07T11:37:02.104592+00:00 | fill_full | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 68 | None | None | None | None | 60.00 | 78.000000 |
| 2026-05-07T11:37:02.105593+00:00 | exit_submit_success | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 68 | None | None | None | None | 60.00 | 78.000000 |
| 2026-05-07T11:37:02.116594+00:00 | exit_reconciled | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 68 | None | None | None | None | 60.00 | 78.000000 |

### KXBTC15M-26MAY061400-00

| ts | event | reason | result | trigger | bid | p_hold | drawdown | hold net | depth | book age |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-05-06T17:57:01.207546+00:00 | exit_signal_seen | mushroom_v28_exit_value_over_hold |  | 84 | 84 | 0.742300 | 14.769975 | 73.230025 | 342.34 | 15.000000 |
| 2026-05-06T17:57:01.207546+00:00 | exit_snapshot_built | mushroom_v28_exit_value_over_hold |  | 84 | 84 | 0.742300 | 14.769975 | 73.230025 | 342.34 | 15.000000 |
| 2026-05-06T17:57:01.208546+00:00 | exit_capacity_estimated | mushroom_v28_exit_value_over_hold |  | 84 | 84 | 0.742300 | 14.769975 | 73.230025 | 342.34 | 15.000000 |
| 2026-05-06T17:57:01.208546+00:00 | exit_plan_built | mushroom_v28_exit_value_over_hold |  | 84 | 84 | 0.742300 | 14.769975 | 73.230025 | 342.34 | 15.000000 |
| 2026-05-06T17:57:01.212546+00:00 | exit_submit_start | mushroom_v28_exit_value_over_hold_single_shot_visible_depth |  | 84 | None | None | None | None | 342.34 | 15.000000 |
| 2026-05-06T17:57:01.213546+00:00 | order_submit_start | mushroom_v28_exit_value_over_hold_single_shot_visible_depth |  | 84 | None | None | None | None | 342.34 | 15.000000 |
| 2026-05-06T17:57:01.265551+00:00 | order_submit_success | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 84 | None | None | None | None | 342.34 | 15.000000 |
| 2026-05-06T17:57:01.265551+00:00 | exit_submit_full | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 84 | None | None | None | None | 342.34 | 15.000000 |
| 2026-05-06T17:57:01.266552+00:00 | fill_full | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 84 | None | None | None | None | 342.34 | 15.000000 |
| 2026-05-06T17:57:01.266552+00:00 | exit_submit_success | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 84 | None | None | None | None | 342.34 | 15.000000 |
| 2026-05-06T17:57:01.274551+00:00 | exit_reconciled | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 84 | None | None | None | None | 342.34 | 15.000000 |

### KXBTC15M-26MAY062100-00

| ts | event | reason | result | trigger | bid | p_hold | drawdown | hold net | depth | book age |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-05-07T00:50:56.947423+00:00 | exit_reconciled | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 75 | None | None | None | None | 54.00 | 78.000000 |
| 2026-05-07T00:57:06.909320+00:00 | exit_signal_seen | mushroom_v28_exit_value_over_hold |  | 95 | 95 | 0.936637 | -4.663664 | 92.663664 | 877.19 | 141.000000 |
| 2026-05-07T00:57:06.909320+00:00 | exit_snapshot_built | mushroom_v28_exit_value_over_hold |  | 95 | 95 | 0.936637 | -4.663664 | 92.663664 | 877.19 | 141.000000 |
| 2026-05-07T00:57:06.910318+00:00 | exit_capacity_estimated | mushroom_v28_exit_value_over_hold |  | 95 | 95 | 0.936637 | -4.663664 | 92.663664 | 877.19 | 141.000000 |
| 2026-05-07T00:57:06.910318+00:00 | exit_plan_built | mushroom_v28_exit_value_over_hold |  | 95 | 95 | 0.936637 | -4.663664 | 92.663664 | 877.19 | 141.000000 |
| 2026-05-07T00:57:06.921202+00:00 | exit_submit_start | mushroom_v28_exit_value_over_hold_single_shot_visible_depth |  | 95 | None | None | None | None | 877.19 | 141.000000 |
| 2026-05-07T00:57:06.921202+00:00 | order_submit_start | mushroom_v28_exit_value_over_hold_single_shot_visible_depth |  | 95 | None | None | None | None | 877.19 | 141.000000 |
| 2026-05-07T00:57:06.974204+00:00 | order_submit_success | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 95 | None | None | None | None | 877.19 | 141.000000 |
| 2026-05-07T00:57:06.975203+00:00 | exit_submit_full | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 95 | None | None | None | None | 877.19 | 141.000000 |
| 2026-05-07T00:57:06.975203+00:00 | fill_full | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 95 | None | None | None | None | 877.19 | 141.000000 |
| 2026-05-07T00:57:06.975203+00:00 | exit_submit_success | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 95 | None | None | None | None | 877.19 | 141.000000 |
| 2026-05-07T00:57:06.984203+00:00 | exit_reconciled | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 95 | None | None | None | None | 877.19 | 141.000000 |

### KXBTC15M-26MAY071315-15

| ts | event | reason | result | trigger | bid | p_hold | drawdown | hold net | depth | book age |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-05-07T17:12:11.746740+00:00 | exit_execution_deferred | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | retry_signal_cleared | 94 | None | None | None | None | 121.00 | 62.000000 |
| 2026-05-07T17:12:13.613651+00:00 | exit_signal_seen | mushroom_v28_exit_value_over_hold |  | 94 | 94 | 0.926891 | -15.689061 | 91.689061 | 125.00 | 0.000000 |
| 2026-05-07T17:12:13.616171+00:00 | exit_snapshot_built | mushroom_v28_exit_value_over_hold |  | 94 | 94 | 0.926891 | -15.689061 | 91.689061 | 125.00 | 0.000000 |
| 2026-05-07T17:12:13.616171+00:00 | exit_capacity_estimated | mushroom_v28_exit_value_over_hold |  | 94 | 94 | 0.926891 | -15.689061 | 91.689061 | 125.00 | 0.000000 |
| 2026-05-07T17:12:13.616171+00:00 | exit_plan_built | mushroom_v28_exit_value_over_hold |  | 94 | 94 | 0.926891 | -15.689061 | 91.689061 | 125.00 | 0.000000 |
| 2026-05-07T17:12:13.618179+00:00 | exit_submit_start | mushroom_v28_exit_value_over_hold_single_shot_visible_depth |  | 94 | None | None | None | None | 125.00 | 0.000000 |
| 2026-05-07T17:12:13.621822+00:00 | order_submit_start | mushroom_v28_exit_value_over_hold_single_shot_visible_depth |  | 94 | None | None | None | None | 125.00 | 0.000000 |
| 2026-05-07T17:12:13.679927+00:00 | order_submit_success | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 94 | None | None | None | None | 125.00 | 0.000000 |
| 2026-05-07T17:12:13.679927+00:00 | exit_submit_full | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 94 | None | None | None | None | 125.00 | 0.000000 |
| 2026-05-07T17:12:13.683555+00:00 | fill_full | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 94 | None | None | None | None | 125.00 | 0.000000 |
| 2026-05-07T17:12:13.684068+00:00 | exit_submit_success | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 94 | None | None | None | None | 125.00 | 0.000000 |
| 2026-05-07T17:12:13.706367+00:00 | exit_reconciled | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | executed | 94 | None | None | None | None | 125.00 | 0.000000 |

### KXBTC15M-26MAY062045-45

| ts | event | reason | result | trigger | bid | p_hold | drawdown | hold net | depth | book age |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-05-07T00:35:32.182895+00:00 | exit_reconciled | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 71 | None | None | None | None | 597.30 | 0.000000 |
| 2026-05-07T00:35:32.185369+00:00 | exit_signal_seen | mushroom_v28_probability_reduce |  | 71 | 71 | 0.794753 | -3.475345 | 78.475345 | 596.30 | 78.000000 |
| 2026-05-07T00:35:32.185369+00:00 | exit_snapshot_built | mushroom_v28_probability_reduce |  | 71 | 71 | 0.794753 | -3.475345 | 78.475345 | 596.30 | 78.000000 |
| 2026-05-07T00:35:32.186463+00:00 | exit_capacity_estimated | mushroom_v28_probability_reduce |  | 71 | 71 | 0.794753 | -3.475345 | 78.475345 | 596.30 | 78.000000 |
| 2026-05-07T00:35:32.186463+00:00 | exit_plan_built | mushroom_v28_probability_reduce |  | 71 | 71 | 0.794753 | -3.475345 | 78.475345 | 596.30 | 78.000000 |
| 2026-05-07T00:35:32.188469+00:00 | exit_submit_start | mushroom_v28_probability_reduce_single_shot_visible_depth |  | 71 | None | None | None | None | 596.30 | 78.000000 |
| 2026-05-07T00:35:32.188469+00:00 | order_submit_start | mushroom_v28_probability_reduce_single_shot_visible_depth |  | 71 | None | None | None | None | 596.30 | 78.000000 |
| 2026-05-07T00:35:32.234215+00:00 | order_submit_success | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 71 | None | None | None | None | 596.30 | 78.000000 |
| 2026-05-07T00:35:32.234215+00:00 | exit_submit_full | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 71 | None | None | None | None | 596.30 | 78.000000 |
| 2026-05-07T00:35:32.235216+00:00 | fill_full | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 71 | None | None | None | None | 596.30 | 78.000000 |
| 2026-05-07T00:35:32.235216+00:00 | exit_submit_success | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 71 | None | None | None | None | 596.30 | 78.000000 |
| 2026-05-07T00:35:32.242215+00:00 | exit_reconciled | mushroom_v28_probability_reduce_single_shot_visible_depth | executed | 71 | None | None | None | None | 596.30 | 78.000000 |

