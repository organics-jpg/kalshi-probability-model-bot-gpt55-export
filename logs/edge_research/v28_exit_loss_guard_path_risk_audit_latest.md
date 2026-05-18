# v28 Exit Loss-Guard Path Risk Audit

Research-only. No live bot logic changes, no orders, no process control.

- Generated UTC: `2026-05-07T11:43:18.785784+00:00`

## Interpretation

- Research-only path-risk audit; no live bot changes or orders.
- A clean hold-to-settlement delta is not sufficient if the row requires surviving large adverse marks after the skipped exit.
- book_gap_loss_guard: 8 suppressed rows, worst adverse vs exit -24.0c, adverse 10/25/50 rows 2/0/0.
- book_gap_loss_guard_v3: 2 suppressed rows, worst adverse vs exit 0.0c, adverse 10/25/50 rows 0/0/0.

## Lane Summary

| lane | strict rows | suppressed | path rows | delta c | worst adverse vs exit | avg adverse | worst mark | adverse 10/25/50 | below zero | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| `book_gap_loss_guard` | 28 | 8 | 8 | 76.00 | -24.00 | -6.00 | -4.00 | 2/0/0 | 1 | suppressed_rows_lt_30, post_exit_mark_below_zero_present |
| `book_gap_loss_guard_v3` | 15 | 2 | 2 | 24.00 | 0.00 | 0.00 | 10.00 | 0/0/0 | 0 | suppressed_rows_lt_30 |

## Worst Suppressed Rows

### book_gap_loss_guard

| market | side | reason | current | hold | delta | worst mark | adverse vs exit | p_hold | gap |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY070030-30` | `yes` | `mushroom_v28_exit_value_over_hold` | 30.00 | 36.00 | 6.00 | 6.00 | -24.00 | 0.92 | -0.05 |
| `KXBTC15M-26MAY070545-45` | `no` | `mushroom_v28_exit_value_over_hold` | 18.00 | 36.00 | 18.00 | -4.00 | -22.00 | 0.89 | -0.02 |
| `KXBTC15M-26MAY061915-15` | `no` | `mushroom_v28_exit_value_over_hold` | 24.00 | 26.00 | 2.00 | 22.00 | -2.00 | 0.98 | -0.01 |
| `KXBTC15M-26MAY061815-15` | `no` | `mushroom_v28_exit_value_over_hold` | 24.00 | 32.00 | 8.00 | 24.00 | 0.00 | 0.95 | -0.01 |
| `KXBTC15M-26MAY061830-30` | `no` | `mushroom_v28_exit_value_over_hold` | 20.00 | 22.00 | 2.00 | 20.00 | 0.00 | 0.98 | -0.01 |
| `KXBTC15M-26MAY062045-45` | `no` | `mushroom_v28_exit_value_over_hold` | 24.00 | 40.00 | 16.00 | 24.00 | 0.00 | 0.89 | -0.03 |
| `KXBTC15M-26MAY062115-15` | `yes` | `mushroom_v28_exit_value_over_hold` | 22.00 | 24.00 | 2.00 | 22.00 | 0.00 | 0.98 | -0.01 |
| `KXBTC15M-26MAY062215-15` | `no` | `mushroom_v28_exit_value_over_hold` | 10.00 | 32.00 | 22.00 | 10.00 | 0.00 | 0.86 | -0.03 |

### book_gap_loss_guard_v3

| market | side | reason | current | hold | delta | worst mark | adverse vs exit | p_hold | gap |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY062115-15` | `yes` | `mushroom_v28_exit_value_over_hold` | 22.00 | 24.00 | 2.00 | 22.00 | 0.00 | 0.98 | -0.01 |
| `KXBTC15M-26MAY062215-15` | `no` | `mushroom_v28_exit_value_over_hold` | 10.00 | 32.00 | 22.00 | 10.00 | 0.00 | 0.86 | -0.03 |

