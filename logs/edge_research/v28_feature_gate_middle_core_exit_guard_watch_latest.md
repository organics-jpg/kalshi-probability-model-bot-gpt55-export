# v28 Feature-Gate Middle-Core Exit-Guard Watch

Research-only. No live bot logic changes, no orders, no process control.

- Generated UTC: `2026-05-07T13:46:47.959298+00:00`
- Watch freeze UTC: `2026-05-07T12:17:14.970836+00:00`
- Feature-gate parent freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Live baseline: `925.000c`
- Possible 15m windows since watch freeze: `5`
- Pre-sample short-circuit: `True`

## Interpretation

- Research-only middle-core exit-guard watch; no live bot changes or orders.
- Own-freeze watch has only 5 possible 15m windows since birth, so heavy replay was skipped.
- This cannot be live-ready until at least 30 post-freeze market windows exist and then clear sample/source/PnL/cushion/live-baseline gates.

## post_middle_exit_guard_freeze_entry

- Future denominator: `0`
- Entry rows: `0`

| rank | variant | W/L | coverage | source | candidate | current exit | entry hold | delta current | delta live | joined | suppressed | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `entry_hold_or_no_exit_control` | 0/0 | 0.000% |  | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 2 | `book_gap_current_exit_control` | 0/0 | 0.000% |  | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 3 | `book_gap_hold_if_suppressed` | 0/0 | 0.000% |  | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 4 | `loss_guard_v1_hold_if_suppressed` | 0/0 | 0.000% |  | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 5 | `loss_guard_v2_hold_if_suppressed` | 0/0 | 0.000% |  | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 6 | `loss_guard_v3_hold_if_suppressed` | 0/0 | 0.000% |  | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 7 | `reduce_hold_if_suppressed` | 0/0 | 0.000% |  | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 | own_freeze_presample_window_lt_30, settled_lt_30 |

## post_middle_exit_guard_freeze_bridge

- Future denominator: `0`
- Entry rows: `0`

| rank | variant | W/L | coverage | source | candidate | current exit | entry hold | delta current | delta live | joined | suppressed | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `entry_hold_or_no_exit_control` | 0/0 | 0.000% |  | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 2 | `book_gap_current_exit_control` | 0/0 | 0.000% |  | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 3 | `book_gap_hold_if_suppressed` | 0/0 | 0.000% |  | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 4 | `loss_guard_v1_hold_if_suppressed` | 0/0 | 0.000% |  | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 5 | `loss_guard_v2_hold_if_suppressed` | 0/0 | 0.000% |  | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 6 | `loss_guard_v3_hold_if_suppressed` | 0/0 | 0.000% |  | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 7 | `reduce_hold_if_suppressed` | 0/0 | 0.000% |  | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 | own_freeze_presample_window_lt_30, settled_lt_30 |
