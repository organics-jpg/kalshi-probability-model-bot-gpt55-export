# v28 Exit Common-Clock Residual Frontier

Research-only. No live bot logic changes, no process control, no orders.

- Generated UTC: `2026-05-07T18:05:49.823643+00:00`
- Source: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_exit_policy_common_clock_watch_latest.json`

## Interpretation

- This is a strict-row residual frontier only; it does not freeze or promote a live exit rule.
- new_exit_mix_common_forward_v2 best overall residual is fair_drawdown_positive_low_p with 17 residual rows, 15/2 helpful/harmful, and 642.0c versus base.
- new_exit_mix_common_forward_v2 best clean residual is collapse_full_any with 5 rows and 462.0c; blockers remain ['total_suppressed_lt_30', 'residual_suppressed_lt_10'].
- new_exit_mix_common_forward_v3 best overall residual is collapse_full_any with 4 residual rows, 4/0 helpful/harmful, and 286.0c versus base.
- new_exit_mix_common_forward_v3 best clean residual is collapse_full_any with 4 rows and 286.0c; blockers remain ['total_suppressed_lt_30', 'residual_suppressed_lt_10'].
- If the clean residual remains sparse, the correct action is continued strict collection or a separately frozen child watch, not promotion.

## new_exit_mix_common_forward_v2

- Freeze UTC: `2026-05-06T22:01:04.415577+00:00`
- Row count/base suppressed: `58` / `17`

| rank | residual policy | residual rows | helpful/harmful | base c | candidate c | residual delta | total suppressed | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `fair_drawdown_positive_low_p` | 17 | 15/2 | 668c | 1310c | 642c | 34 | 13 | `residual_harmful_false_holds_present` |
| 2 | `collapse_full_any` | 5 | 5/0 | 668c | 1130c | 462c | 22 | 11 | `total_suppressed_lt_30, residual_suppressed_lt_10` |
| 3 | `collapse_full_low_p` | 5 | 5/0 | 668c | 1130c | 462c | 22 | 11 | `total_suppressed_lt_30, residual_suppressed_lt_10` |
| 4 | `collapse_full_low_p_exit_below70` | 4 | 4/0 | 668c | 1074c | 406c | 21 | 10 | `total_suppressed_lt_30, residual_suppressed_lt_10` |
| 5 | `collapse_full_low_p_gap_0_to_15pp` | 4 | 4/0 | 668c | 1074c | 406c | 21 | 10 | `total_suppressed_lt_30, residual_suppressed_lt_10` |
| 6 | `low_p_exit_below70_gap_nonnegative` | 4 | 4/0 | 668c | 1074c | 406c | 21 | 10 | `total_suppressed_lt_30, residual_suppressed_lt_10` |
| 7 | `low_p_book_gap_5_to_15pp` | 3 | 3/0 | 668c | 1004c | 336c | 20 | 10 | `total_suppressed_lt_30, residual_suppressed_lt_10` |
| 8 | `value_low_p_book_negative` | 12 | 10/2 | 668c | 848c | 180c | 29 | 8 | `total_suppressed_lt_30, residual_harmful_false_holds_present` |
| 9 | `prob_reduce_p75_79_gap_0_to_5pp` | 3 | 2/1 | 668c | 622c | -46c | 20 | 6 | `total_suppressed_lt_30, residual_suppressed_lt_10, residual_delta_not_positive, residual_harmful_false_holds_present` |
| 10 | `value_low_p_book_negative_exit_below70` | 4 | 2/2 | 668c | 556c | -112c | 21 | 5 | `total_suppressed_lt_30, residual_suppressed_lt_10, residual_delta_not_positive, residual_harmful_false_holds_present` |
| 11 | `prob_reduce_p75_79_exit70_79` | 5 | 3/2 | 668c | 506c | -162c | 22 | 5 | `total_suppressed_lt_30, residual_suppressed_lt_10, residual_delta_not_positive, residual_harmful_false_holds_present` |

### Harmful Examples For Top Residual

- `KXBTC15M-26MAY070015-15` `no/yes` reason=`mushroom_v28_exit_value_over_hold` p_hold=`0.596562` gap=`-0.09343799999999991` drawdown=`10.343815` delta=`-138.0`
- `KXBTC15M-26MAY062115-15` `no/yes` reason=`mushroom_v28_exit_value_over_hold` p_hold=`0.455777` gap=`-0.06422300000000003` drawdown=`14.422271` delta=`-104.0`

## new_exit_mix_common_forward_v3

- Freeze UTC: `2026-05-07T01:01:45.501061+00:00`
- Row count/base suppressed: `46` / `13`

| rank | residual policy | residual rows | helpful/harmful | base c | candidate c | residual delta | total suppressed | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `collapse_full_any` | 4 | 4/0 | 692c | 978c | 286c | 17 | 9 | `total_suppressed_lt_30, residual_suppressed_lt_10` |
| 2 | `collapse_full_low_p` | 4 | 4/0 | 692c | 978c | 286c | 17 | 9 | `total_suppressed_lt_30, residual_suppressed_lt_10` |
| 3 | `collapse_full_low_p_exit_below70` | 3 | 3/0 | 692c | 922c | 230c | 16 | 9 | `total_suppressed_lt_30, residual_suppressed_lt_10` |
| 4 | `collapse_full_low_p_gap_0_to_15pp` | 3 | 3/0 | 692c | 922c | 230c | 16 | 9 | `total_suppressed_lt_30, residual_suppressed_lt_10` |
| 5 | `low_p_exit_below70_gap_nonnegative` | 3 | 3/0 | 692c | 922c | 230c | 16 | 9 | `total_suppressed_lt_30, residual_suppressed_lt_10` |
| 6 | `low_p_book_gap_5_to_15pp` | 2 | 2/0 | 692c | 852c | 160c | 15 | 8 | `total_suppressed_lt_30, residual_suppressed_lt_10` |
| 7 | `fair_drawdown_positive_low_p` | 12 | 10/2 | 692c | 970c | 278c | 25 | 9 | `total_suppressed_lt_30, residual_harmful_false_holds_present` |
| 8 | `prob_reduce_p75_79_gap_0_to_5pp` | 3 | 2/1 | 692c | 646c | -46c | 16 | 6 | `total_suppressed_lt_30, residual_suppressed_lt_10, residual_delta_not_positive, residual_harmful_false_holds_present` |
| 9 | `value_low_p_book_negative` | 8 | 6/2 | 692c | 684c | -8c | 21 | 6 | `total_suppressed_lt_30, residual_suppressed_lt_10, residual_delta_not_positive, residual_harmful_false_holds_present` |
| 10 | `prob_reduce_p75_79_exit70_79` | 5 | 3/2 | 692c | 530c | -162c | 18 | 5 | `total_suppressed_lt_30, residual_suppressed_lt_10, residual_delta_not_positive, residual_harmful_false_holds_present` |
| 11 | `value_low_p_book_negative_exit_below70` | 3 | 1/2 | 692c | 516c | -176c | 16 | 5 | `total_suppressed_lt_30, residual_suppressed_lt_10, residual_delta_not_positive, residual_harmful_false_holds_present` |
