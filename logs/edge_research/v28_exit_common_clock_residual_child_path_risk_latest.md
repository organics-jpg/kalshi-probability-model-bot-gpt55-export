# v28 Exit Common-Clock Residual Child Path Risk

Research-only path-risk audit. No live bot changes or orders.

- Generated UTC: `2026-05-07T15:07:13.346995+00:00`
- Child watch source: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_frozen_exit_common_clock_residual_child_watch_latest.json`
- Post-exit path source: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_post_exit_path_latest.json`

## Interpretation

- Research-only path-risk audit; no live bot changes or orders.
- This audit checks whether residual-child held exits required surviving large adverse marks after the skipped exit.
- Strict post-child path rows 1/4; worst adverse vs exit -10.0c, adverse 10/25/50 rows 1/0/0, blockers ['settled_lt_30', 'child_suppressed_decisions_lt_30', 'full_loss_cushion_lt_3', 'post_exit_mark_below_zero_present', 'missing_post_exit_path_rows'].

## Lane Summary

| lane | strict | settled | child suppressed | path rows | child delta | candidate net | cushion | worst adverse | avg adverse | worst mark | adverse 10/25/50 | below zero | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| `diagnostic_v2_common_clock_context` | False | 45 | 7 | 4 | -52.00 | 374.00 | 3 | -108.00 | -41.00 | -128.00 | 4/2/1 | 4 | child_suppressed_decisions_lt_30, post_exit_adverse_25c_present, post_exit_mark_below_zero_present, missing_post_exit_path_rows |
| `diagnostic_v3_common_clock_context` | False | 33 | 6 | 3 | -104.00 | 346.00 | 3 | -30.00 | -18.67 | -24.00 | 3/1/0 | 3 | child_suppressed_decisions_lt_30, post_exit_adverse_25c_present, post_exit_mark_below_zero_present, missing_post_exit_path_rows |
| `post_child_birth` | True | 20 | 4 | 1 | -202.00 | 190.00 | 1 | -10.00 | -10.00 | -24.00 | 1/0/0 | 1 | settled_lt_30, child_suppressed_decisions_lt_30, full_loss_cushion_lt_3, post_exit_mark_below_zero_present, missing_post_exit_path_rows |

## Child Rows

### diagnostic_v2_common_clock_context

| market | side | current | parent | hold | child delta | worst mark | adverse vs exit | min bid | points | tags |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY062100-00` | `yes` | -20.00 | -20.00 | 32.00 | 52.00 | -128.00 | -108.00 | 20 | 31 | child_residual_suppressed, settlement_winner, value_over_hold, p_hold_lt_75, book_gap_negative, fair_drawdown_positive, exitable_at_70_79 |
| `KXBTC15M-26MAY062215-15` | `no` | 14.00 | 14.00 | 70.00 | 56.00 | -16.00 | -30.00 | 57 | 48 | child_residual_suppressed, settlement_winner, mushroom_v28_probability_collapse_full, p_hold_lt_75, book_gap_negative, fair_drawdown_deep, exitable_at_70_79 |
| `KXBTC15M-26MAY070000-00` | `no` | 2.00 | 2.00 | 44.00 | 42.00 | -14.00 | -16.00 | 71 | 22 | child_residual_suppressed, settlement_winner, value_over_hold, p_hold_lt_75, book_gap_negative, fair_drawdown_positive, exitable_at_70_79 |
| `KXBTC15M-26MAY070830-30` | `no` | -14.00 | -14.00 | 46.00 | 60.00 | -24.00 | -10.00 | 65 | 14 | child_residual_suppressed, settlement_winner, value_over_hold, p_hold_lt_75, book_gap_negative, fair_drawdown_positive, exitable_at_70_79 |
| `KXBTC15M-26MAY071000-00` | `no` | 16.00 | 16.00 | 58.00 | 42.00 | n/a | n/a | n/a | None | child_residual_suppressed, settlement_winner, probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_positive, exitable_at_70_79 |
| `KXBTC15M-26MAY071015-15` | `no` | -16.00 | -16.00 | -162.00 | -146.00 | n/a | n/a | n/a | None | child_residual_suppressed, settlement_loser, probability_reduce, p_hold_75_79, book_gap_0_5pp, fair_drawdown_positive, exitable_at_70_79 |
| `KXBTC15M-26MAY071015-15` | `no` | 2.00 | 2.00 | -156.00 | -158.00 | n/a | n/a | n/a | None | child_residual_suppressed, settlement_loser, probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_shallow, exitable_at_70_79 |

### diagnostic_v3_common_clock_context

| market | side | current | parent | hold | child delta | worst mark | adverse vs exit | min bid | points | tags |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY062215-15` | `no` | 14.00 | 14.00 | 70.00 | 56.00 | -16.00 | -30.00 | 57 | 48 | child_residual_suppressed, settlement_winner, mushroom_v28_probability_collapse_full, p_hold_lt_75, book_gap_negative, fair_drawdown_deep, exitable_at_70_79 |
| `KXBTC15M-26MAY070000-00` | `no` | 2.00 | 2.00 | 44.00 | 42.00 | -14.00 | -16.00 | 71 | 22 | child_residual_suppressed, settlement_winner, value_over_hold, p_hold_lt_75, book_gap_negative, fair_drawdown_positive, exitable_at_70_79 |
| `KXBTC15M-26MAY070830-30` | `no` | -14.00 | -14.00 | 46.00 | 60.00 | -24.00 | -10.00 | 65 | 14 | child_residual_suppressed, settlement_winner, value_over_hold, p_hold_lt_75, book_gap_negative, fair_drawdown_positive, exitable_at_70_79 |
| `KXBTC15M-26MAY071000-00` | `no` | 16.00 | 16.00 | 58.00 | 42.00 | n/a | n/a | n/a | None | child_residual_suppressed, settlement_winner, probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_positive, exitable_at_70_79 |
| `KXBTC15M-26MAY071015-15` | `no` | -16.00 | -16.00 | -162.00 | -146.00 | n/a | n/a | n/a | None | child_residual_suppressed, settlement_loser, probability_reduce, p_hold_75_79, book_gap_0_5pp, fair_drawdown_positive, exitable_at_70_79 |
| `KXBTC15M-26MAY071015-15` | `no` | 2.00 | 2.00 | -156.00 | -158.00 | n/a | n/a | n/a | None | child_residual_suppressed, settlement_loser, probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_shallow, exitable_at_70_79 |

### post_child_birth

| market | side | current | parent | hold | child delta | worst mark | adverse vs exit | min bid | points | tags |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY070830-30` | `no` | -14.00 | -14.00 | 46.00 | 60.00 | -24.00 | -10.00 | 65 | 14 | child_residual_suppressed, settlement_winner, value_over_hold, p_hold_lt_75, book_gap_negative, fair_drawdown_positive, exitable_at_70_79 |
| `KXBTC15M-26MAY071000-00` | `no` | 16.00 | 16.00 | 58.00 | 42.00 | n/a | n/a | n/a | None | child_residual_suppressed, settlement_winner, probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_positive, exitable_at_70_79 |
| `KXBTC15M-26MAY071015-15` | `no` | -16.00 | -16.00 | -162.00 | -146.00 | n/a | n/a | n/a | None | child_residual_suppressed, settlement_loser, probability_reduce, p_hold_75_79, book_gap_0_5pp, fair_drawdown_positive, exitable_at_70_79 |
| `KXBTC15M-26MAY071015-15` | `no` | 2.00 | 2.00 | -156.00 | -158.00 | n/a | n/a | n/a | None | child_residual_suppressed, settlement_loser, probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_shallow, exitable_at_70_79 |

