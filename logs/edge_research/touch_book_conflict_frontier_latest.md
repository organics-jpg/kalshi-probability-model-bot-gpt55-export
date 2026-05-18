# Touch-Book Conflict Frontier

Generated UTC: `20260504_135535Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Keeps `book_margin` as coverage base and tests whether an earlier opposite touch-hazard row should preempt later book confidence.
- Strict pass requires current+v21 coverage, positive all train/validation/holdout splits, positive OOS, and block stability.

## Summary

- Policies scanned: 145
- Strict pass rows: 0

| policy | strict | combined all net | combined OOS net | min split cov | current/v21 net | current/v21 acc | preempts current/v21 | block+ | worst block |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `touch_preempt_book0.65_touch0.5_ask55_age600` | False | 1248.0c | 732.0c | 97.78% | 805.0c/443.0c | 70.03%/71.23% | 5/2 | 0.593 | -296.0c |
| `touch_preempt_book0.7_touch0.5_ask55_age600` | False | 1163.0c | 732.0c | 97.78% | 720.0c/443.0c | 69.72%/71.23% | 6/2 | 0.593 | -296.0c |
| `book_margin_baseline` | False | 1465.0c | 714.0c | 97.78% | 1040.0c/425.0c | 70.98%/71.23% | 0/0 | 0.630 | -330.0c |
| `touch_preempt_book0.8_touch0.5_ask55_age600` | False | 1335.0c | 658.0c | 97.78% | 762.0c/573.0c | 69.72%/71.69% | 8/3 | 0.593 | -296.0c |
| `touch_preempt_book1_touch0.5_ask55_age600` | False | 1335.0c | 658.0c | 97.78% | 762.0c/573.0c | 69.72%/71.69% | 8/3 | 0.593 | -296.0c |
| `touch_preempt_book0.8_touch0.5_ask55_age180` | False | 1475.0c | 622.0c | 97.78% | 1012.0c/463.0c | 70.66%/71.23% | 5/2 | 0.630 | -330.0c |
| `touch_preempt_book1_touch0.5_ask55_age180` | False | 1475.0c | 622.0c | 97.78% | 1012.0c/463.0c | 70.66%/71.23% | 5/2 | 0.630 | -330.0c |
| `touch_preempt_book0.65_touch0.5_ask55_age180` | False | 1314.0c | 622.0c | 97.78% | 981.0c/333.0c | 70.66%/70.78% | 3/1 | 0.630 | -330.0c |
| `touch_preempt_book0.7_touch0.5_ask55_age180` | False | 1229.0c | 622.0c | 97.78% | 896.0c/333.0c | 70.35%/70.78% | 4/1 | 0.630 | -330.0c |
| `touch_preempt_book0.65_touch0.5_ask55_age300` | False | 1226.0c | 622.0c | 97.78% | 893.0c/333.0c | 70.35%/70.78% | 4/1 | 0.593 | -330.0c |
| `touch_preempt_book0.7_touch0.5_ask55_age300` | False | 1141.0c | 622.0c | 97.78% | 808.0c/333.0c | 70.03%/70.78% | 5/1 | 0.593 | -330.0c |
| `touch_preempt_book0.8_touch0.5_ask55_age300` | False | 1313.0c | 548.0c | 97.78% | 850.0c/463.0c | 70.03%/71.23% | 7/2 | 0.593 | -330.0c |
| `touch_preempt_book1_touch0.5_ask55_age300` | False | 1313.0c | 548.0c | 97.78% | 850.0c/463.0c | 70.03%/71.23% | 7/2 | 0.593 | -330.0c |
| `touch_preempt_book0.65_touch0.45_ask55_age600` | False | 515.0c | 464.0c | 97.78% | 97.0c/418.0c | 66.88%/70.78% | 33/9 | 0.556 | -425.0c |
| `touch_preempt_book0.65_touch0.45_ask55_age180` | False | 903.0c | 424.0c | 97.78% | 525.0c/378.0c | 68.45%/70.78% | 26/5 | 0.630 | -270.0c |

## Read

- No touch-book conflict rule clears the strict gate.
- This is post-hoc research and must be forward-locked before any live use.
