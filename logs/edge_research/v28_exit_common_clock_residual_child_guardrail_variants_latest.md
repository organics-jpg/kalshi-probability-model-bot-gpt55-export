# v28 Exit Common-Clock Residual Child Guardrail Variants

Research-only guardrail scan. No live bot changes or orders.

- Generated UTC: `2026-05-07T15:07:13.223860+00:00`
- Child freeze UTC: `2026-05-07T08:06:06.929631+00:00`

## Interpretation

- Research-only guardrail scan; no live bot changes or orders.
- All variants use observable exit fields only; source labels and settlement are audit outcomes, not rule inputs.
- Base strict residual child: 20 settled, 4 child suppressions, helpful/harmful 2/2, child delta -202.0c, blockers ['settled_lt_30', 'child_suppressed_decisions_lt_30', 'delta_vs_current_not_positive', 'child_delta_vs_parent_not_positive', 'child_loss_control_cost_negative', 'full_loss_cushion_lt_3', 'strict_or_window_false_holds_present'].
- Best clean strict guard by child delta is book_gap_le_neg_0_5pp: 2 child suppressions, helpful/harmful 2/0, child delta 102.0c, candidate net 494.0c, blockers ['settled_lt_30', 'child_suppressed_decisions_lt_30'].
- These are guardrail diagnostics only; any new child would need its own freeze and future rows.

## Lane Summary

| lane | variant | strict | settled | child supp | help/harm | child delta | candidate net | delta vs current | cushion | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `diagnostic_v2_common_clock_context` | `base_exit70_79` | False | 45 | 7 | 5/2 | -52.00 | 374.00 | 60.00 | 3 | child_suppressed_decisions_lt_30, child_delta_vs_parent_not_positive, child_loss_control_cost_negative, strict_or_window_false_holds_present |
| `diagnostic_v2_common_clock_context` | `exclude_probability_reduce_p75_79` | False | 45 | 4 | 4/0 | 210.00 | 636.00 | 322.00 | 6 | child_suppressed_decisions_lt_30 |
| `diagnostic_v2_common_clock_context` | `value_over_hold_only` | False | 45 | 3 | 3/0 | 154.00 | 580.00 | 266.00 | 5 | child_suppressed_decisions_lt_30 |
| `diagnostic_v2_common_clock_context` | `book_gap_le_neg_0_5pp` | False | 45 | 5 | 5/0 | 252.00 | 678.00 | 364.00 | 6 | child_suppressed_decisions_lt_30 |
| `diagnostic_v2_common_clock_context` | `p_hold_lt75_or_book_gap_le_neg_0_5pp` | False | 45 | 5 | 5/0 | 252.00 | 678.00 | 364.00 | 6 | child_suppressed_decisions_lt_30 |
| `diagnostic_v2_common_clock_context` | `prob_reduce_requires_book_gap_le_neg_0_5pp` | False | 45 | 5 | 5/0 | 252.00 | 678.00 | 364.00 | 6 | child_suppressed_decisions_lt_30 |
| `diagnostic_v3_common_clock_context` | `base_exit70_79` | False | 33 | 6 | 4/2 | -104.00 | 346.00 | -20.00 | 3 | child_suppressed_decisions_lt_30, delta_vs_current_not_positive, child_delta_vs_parent_not_positive, child_loss_control_cost_negative, strict_or_window_false_holds_present |
| `diagnostic_v3_common_clock_context` | `exclude_probability_reduce_p75_79` | False | 33 | 3 | 3/0 | 158.00 | 608.00 | 242.00 | 6 | child_suppressed_decisions_lt_30 |
| `diagnostic_v3_common_clock_context` | `value_over_hold_only` | False | 33 | 2 | 2/0 | 102.00 | 552.00 | 186.00 | 5 | child_suppressed_decisions_lt_30 |
| `diagnostic_v3_common_clock_context` | `book_gap_le_neg_0_5pp` | False | 33 | 4 | 4/0 | 200.00 | 650.00 | 284.00 | 6 | child_suppressed_decisions_lt_30 |
| `diagnostic_v3_common_clock_context` | `p_hold_lt75_or_book_gap_le_neg_0_5pp` | False | 33 | 4 | 4/0 | 200.00 | 650.00 | 284.00 | 6 | child_suppressed_decisions_lt_30 |
| `diagnostic_v3_common_clock_context` | `prob_reduce_requires_book_gap_le_neg_0_5pp` | False | 33 | 4 | 4/0 | 200.00 | 650.00 | 284.00 | 6 | child_suppressed_decisions_lt_30 |
| `post_child_birth` | `base_exit70_79` | True | 20 | 4 | 2/2 | -202.00 | 190.00 | -148.00 | 1 | settled_lt_30, child_suppressed_decisions_lt_30, delta_vs_current_not_positive, child_delta_vs_parent_not_positive, child_loss_control_cost_negative, full_loss_cushion_lt_3, strict_or_window_false_holds_present |
| `post_child_birth` | `exclude_probability_reduce_p75_79` | True | 20 | 1 | 1/0 | 60.00 | 452.00 | 114.00 | 4 | settled_lt_30, child_suppressed_decisions_lt_30 |
| `post_child_birth` | `value_over_hold_only` | True | 20 | 1 | 1/0 | 60.00 | 452.00 | 114.00 | 4 | settled_lt_30, child_suppressed_decisions_lt_30 |
| `post_child_birth` | `book_gap_le_neg_0_5pp` | True | 20 | 2 | 2/0 | 102.00 | 494.00 | 156.00 | 4 | settled_lt_30, child_suppressed_decisions_lt_30 |
| `post_child_birth` | `p_hold_lt75_or_book_gap_le_neg_0_5pp` | True | 20 | 2 | 2/0 | 102.00 | 494.00 | 156.00 | 4 | settled_lt_30, child_suppressed_decisions_lt_30 |
| `post_child_birth` | `prob_reduce_requires_book_gap_le_neg_0_5pp` | True | 20 | 2 | 2/0 | 102.00 | 494.00 | 156.00 | 4 | settled_lt_30, child_suppressed_decisions_lt_30 |

## Strict Child Rows

### base_exit70_79

| market | side | won | reason | exit | p_hold | gap | current | hold | child delta | tags |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY071015-15` | `no` | False | `mushroom_v28_probability_reduce` | 79.00 | 0.79 | -0.00 | 2.00 | -156.00 | -158.00 | child_residual_suppressed, settlement_loser, probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_shallow, exitable_at_70_79, probability_reduce_exit, p_hold_75_79_guard_zone |
| `KXBTC15M-26MAY071015-15` | `no` | False | `mushroom_v28_probability_reduce` | 73.00 | 0.76 | 0.03 | -16.00 | -162.00 | -146.00 | child_residual_suppressed, settlement_loser, probability_reduce, p_hold_75_79, book_gap_0_5pp, fair_drawdown_positive, exitable_at_70_79, probability_reduce_exit, p_hold_75_79_guard_zone |
| `KXBTC15M-26MAY071000-00` | `no` | True | `mushroom_v28_probability_reduce` | 79.00 | 0.78 | -0.01 | 16.00 | 58.00 | 42.00 | child_residual_suppressed, settlement_winner, probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_positive, exitable_at_70_79, probability_reduce_exit, p_hold_75_79_guard_zone, book_gap_le_neg_0_5pp |
| `KXBTC15M-26MAY070830-30` | `no` | True | `mushroom_v28_exit_value_over_hold` | 70.00 | 0.61 | -0.09 | -14.00 | 46.00 | 60.00 | child_residual_suppressed, settlement_winner, value_over_hold, p_hold_lt_75, book_gap_negative, fair_drawdown_positive, exitable_at_70_79, value_over_hold_exit, book_gap_le_neg_0_5pp |

### exclude_probability_reduce_p75_79

| market | side | won | reason | exit | p_hold | gap | current | hold | child delta | tags |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY070830-30` | `no` | True | `mushroom_v28_exit_value_over_hold` | 70.00 | 0.61 | -0.09 | -14.00 | 46.00 | 60.00 | child_residual_suppressed, settlement_winner, value_over_hold, p_hold_lt_75, book_gap_negative, fair_drawdown_positive, exitable_at_70_79, value_over_hold_exit, book_gap_le_neg_0_5pp |

### value_over_hold_only

| market | side | won | reason | exit | p_hold | gap | current | hold | child delta | tags |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY070830-30` | `no` | True | `mushroom_v28_exit_value_over_hold` | 70.00 | 0.61 | -0.09 | -14.00 | 46.00 | 60.00 | child_residual_suppressed, settlement_winner, value_over_hold, p_hold_lt_75, book_gap_negative, fair_drawdown_positive, exitable_at_70_79, value_over_hold_exit, book_gap_le_neg_0_5pp |

### book_gap_le_neg_0_5pp

| market | side | won | reason | exit | p_hold | gap | current | hold | child delta | tags |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY071000-00` | `no` | True | `mushroom_v28_probability_reduce` | 79.00 | 0.78 | -0.01 | 16.00 | 58.00 | 42.00 | child_residual_suppressed, settlement_winner, probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_positive, exitable_at_70_79, probability_reduce_exit, p_hold_75_79_guard_zone, book_gap_le_neg_0_5pp |
| `KXBTC15M-26MAY070830-30` | `no` | True | `mushroom_v28_exit_value_over_hold` | 70.00 | 0.61 | -0.09 | -14.00 | 46.00 | 60.00 | child_residual_suppressed, settlement_winner, value_over_hold, p_hold_lt_75, book_gap_negative, fair_drawdown_positive, exitable_at_70_79, value_over_hold_exit, book_gap_le_neg_0_5pp |

### p_hold_lt75_or_book_gap_le_neg_0_5pp

| market | side | won | reason | exit | p_hold | gap | current | hold | child delta | tags |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY071000-00` | `no` | True | `mushroom_v28_probability_reduce` | 79.00 | 0.78 | -0.01 | 16.00 | 58.00 | 42.00 | child_residual_suppressed, settlement_winner, probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_positive, exitable_at_70_79, probability_reduce_exit, p_hold_75_79_guard_zone, book_gap_le_neg_0_5pp |
| `KXBTC15M-26MAY070830-30` | `no` | True | `mushroom_v28_exit_value_over_hold` | 70.00 | 0.61 | -0.09 | -14.00 | 46.00 | 60.00 | child_residual_suppressed, settlement_winner, value_over_hold, p_hold_lt_75, book_gap_negative, fair_drawdown_positive, exitable_at_70_79, value_over_hold_exit, book_gap_le_neg_0_5pp |

### prob_reduce_requires_book_gap_le_neg_0_5pp

| market | side | won | reason | exit | p_hold | gap | current | hold | child delta | tags |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY071000-00` | `no` | True | `mushroom_v28_probability_reduce` | 79.00 | 0.78 | -0.01 | 16.00 | 58.00 | 42.00 | child_residual_suppressed, settlement_winner, probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_positive, exitable_at_70_79, probability_reduce_exit, p_hold_75_79_guard_zone, book_gap_le_neg_0_5pp |
| `KXBTC15M-26MAY070830-30` | `no` | True | `mushroom_v28_exit_value_over_hold` | 70.00 | 0.61 | -0.09 | -14.00 | 46.00 | 60.00 | child_residual_suppressed, settlement_winner, value_over_hold, p_hold_lt_75, book_gap_negative, fair_drawdown_positive, exitable_at_70_79, value_over_hold_exit, book_gap_le_neg_0_5pp |

