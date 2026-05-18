# v28 Feature-Gate Middle-Distance Core Watch

Research-only. No live bot logic changes, no orders, no process control.

- Generated UTC: `2026-05-07T13:46:47.922942+00:00`
- Watch freeze UTC: `2026-05-07T12:00:53.752707+00:00`
- Feature-gate parent freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Live baseline: `925.000c`
- Possible 15m windows since watch freeze: `7`
- Pre-sample short-circuit: `True`

## Interpretation

- Research-only middle-distance core watch; no live bot changes or orders.
- Own-freeze watch has only 7 possible 15m windows since birth, so heavy replay was skipped.
- This cannot be live-ready until at least 30 post-freeze market windows exist and then clear sample/source/PnL/cushion/live-baseline gates.

## post_middle_core_freeze_entry

- Future denominator: `0`
- Broad coverage required in this report: `False`

| rank | rule | entries | settled | W/L | coverage | net c | delta live c | source share | cushion | no-top-win c | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `middle_core_raw03_recross50_abs075_125_ask35` | 0 | 0 | 0/0 | 0.000% | 0.000 | 0.000 |  | 0 | 0.000 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 2 | `middle_core_raw05_recross60_abs075_125_ask35` | 0 | 0 | 0/0 | 0.000% | 0.000 | 0.000 |  | 0 | 0.000 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 3 | `abs_floor_raw03_recross50_abs075_ask35` | 0 | 0 | 0/0 | 0.000% | 0.000 | 0.000 |  | 0 | 0.000 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 4 | `abs_floor_raw05_recross60_abs075_ask35` | 0 | 0 | 0/0 | 0.000% | 0.000 | 0.000 |  | 0 | 0.000 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 5 | `upper_abs_tail_raw03_recross50_abs125_ask35` | 0 | 0 | 0/0 | 0.000% | 0.000 | 0.000 |  | 0 | 0.000 | own_freeze_presample_window_lt_30, settled_lt_30 |

## post_middle_core_freeze_bridge

- Future denominator: `0`
- Broad coverage required in this report: `False`

| rank | rule | entries | settled | W/L | coverage | net c | delta live c | source share | cushion | no-top-win c | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `middle_core_raw03_recross50_abs075_125_ask35` | 0 | 0 | 0/0 | 0.000% | 0.000 | 0.000 |  | 0 | 0.000 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 2 | `middle_core_raw05_recross60_abs075_125_ask35` | 0 | 0 | 0/0 | 0.000% | 0.000 | 0.000 |  | 0 | 0.000 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 3 | `abs_floor_raw03_recross50_abs075_ask35` | 0 | 0 | 0/0 | 0.000% | 0.000 | 0.000 |  | 0 | 0.000 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 4 | `abs_floor_raw05_recross60_abs075_ask35` | 0 | 0 | 0/0 | 0.000% | 0.000 | 0.000 |  | 0 | 0.000 | own_freeze_presample_window_lt_30, settled_lt_30 |
| 5 | `upper_abs_tail_raw03_recross50_abs125_ask35` | 0 | 0 | 0/0 | 0.000% | 0.000 | 0.000 |  | 0 | 0.000 | own_freeze_presample_window_lt_30, settled_lt_30 |
