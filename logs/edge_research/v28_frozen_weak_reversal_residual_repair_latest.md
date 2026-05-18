# v28 Frozen Weak-Reversal Residual Repair

Research-only; no live bot changes and no orders.

- Policy: `weak_reversal_skip_edge_5_8pp_no_repair_farthest_boundary`
- Freeze timestamp UTC: `2026-05-06T10:25:15.561162+00:00`
- Live ready: `False`
- Blockers: `net_not_positive`

## Interpretation

- Frozen forward denominator is 108; candidate has 81 settled rows and net -1127.0c.
- Promotion blocked by: net_not_positive.
- This is a forward validator, not live order logic.

## Summaries

| slice | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| target | 79 | 79 | 47/32 | 73.148148 | 236.000000 | 2.987342 |
| weak_reversal | 81 | 81 | 45/36 | 75.000000 | -721.000000 | -8.901235 |
| skipped | 7 | 7 | 6/1 | 6.481481 | 269.000000 | 38.428571 |
| repairs | 7 | 7 | 4/3 | 6.481481 | -139.000000 | -19.857143 |
| candidate | 81 | 81 | 43/38 | 75.000000 | -1127.000000 | -13.913580 |
