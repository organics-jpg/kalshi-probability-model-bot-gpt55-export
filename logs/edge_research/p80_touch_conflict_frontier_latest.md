# P80 Touch-Conflict Frontier

Generated UTC: `20260504_142452Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Tests whether an earlier opposite touch-hazard row should preempt p80 terminal book confidence.
- Strict pass requires current+v21 coverage, positive all train/validation/holdout splits, positive OOS, and block stability.

## Summary

- Policies scanned: 290
- Strict pass rows: 0

| policy | strict | combined all net | combined OOS net | min split cov | current/v21 net | current/v21 acc | preempts current/v21 | block+ | worst block |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `p80_ask90_sec0_baseline` | False | 465.0c | 299.0c | 81.82% | 117.0c/348.0c | 85.62%/87.98% | 0/0 | 0.500 | -210.0c |
| `p80_ask90_sec0_touch_preempt_book0.85_touch0.5_ask55_age180` | False | 166.0c | 286.0c | 81.82% | -182.0c/348.0c | 83.99%/87.98% | 7/0 | 0.462 | -210.0c |
| `p80_ask90_sec0_touch_preempt_book0.9_touch0.5_ask55_age180` | False | 166.0c | 286.0c | 81.82% | -182.0c/348.0c | 83.99%/87.98% | 7/0 | 0.462 | -210.0c |
| `p80_ask90_sec0_touch_preempt_book1_touch0.5_ask55_age180` | False | 166.0c | 286.0c | 81.82% | -182.0c/348.0c | 83.99%/87.98% | 7/0 | 0.462 | -210.0c |
| `p80_ask95_sec120_baseline` | False | 343.0c | 244.0c | 84.09% | 44.0c/299.0c | 85.62%/88.54% | 0/0 | 0.538 | -240.0c |
| `p80_ask95_sec120_touch_preempt_book0.85_touch0.5_ask55_age180` | False | 44.0c | 231.0c | 84.09% | -255.0c/299.0c | 83.99%/88.54% | 7/0 | 0.500 | -240.0c |
| `p80_ask95_sec120_touch_preempt_book0.9_touch0.5_ask55_age180` | False | 44.0c | 231.0c | 84.09% | -255.0c/299.0c | 83.99%/88.54% | 7/0 | 0.500 | -240.0c |
| `p80_ask95_sec120_touch_preempt_book1_touch0.5_ask55_age180` | False | 44.0c | 231.0c | 84.09% | -255.0c/299.0c | 83.99%/88.54% | 7/0 | 0.500 | -240.0c |
| `p80_ask95_sec120_touch_preempt_book0.9_touch0.5_ask60_age180` | False | -542.0c | -19.0c | 84.09% | -841.0c/299.0c | 81.05%/88.54% | 20/0 | 0.462 | -240.0c |
| `p80_ask90_sec0_touch_preempt_book0.85_touch0.5_ask60_age180` | False | -403.0c | -20.0c | 81.82% | -751.0c/348.0c | 81.37%/87.98% | 17/0 | 0.423 | -212.0c |
| `p80_ask90_sec0_touch_preempt_book0.9_touch0.5_ask60_age180` | False | -491.0c | -35.0c | 81.82% | -839.0c/348.0c | 80.72%/87.98% | 21/0 | 0.385 | -212.0c |
| `p80_ask90_sec0_touch_preempt_book1_touch0.5_ask60_age180` | False | -491.0c | -35.0c | 81.82% | -839.0c/348.0c | 80.72%/87.98% | 21/0 | 0.385 | -212.0c |
| `p80_ask95_sec120_touch_preempt_book0.9_touch0.5_ask55_age900` | False | -1247.0c | -43.0c | 84.09% | -1750.0c/503.0c | 76.47%/89.06% | 32/3 | 0.462 | -542.0c |
| `p80_ask95_sec120_touch_preempt_book1_touch0.5_ask55_age900` | False | -1311.0c | -43.0c | 84.09% | -1750.0c/439.0c | 76.47%/88.54% | 32/4 | 0.462 | -542.0c |
| `p80_ask95_sec120_touch_preempt_book0.85_touch0.5_ask55_age300` | False | -447.0c | -44.0c | 84.09% | -883.0c/436.0c | 80.72%/89.06% | 19/1 | 0.462 | -287.0c |
| `p80_ask95_sec120_touch_preempt_book0.85_touch0.5_ask55_age600` | False | -586.0c | -44.0c | 84.09% | -1022.0c/436.0c | 80.07%/89.06% | 21/1 | 0.462 | -287.0c |
| `p80_ask95_sec120_touch_preempt_book0.85_touch0.5_ask55_age900` | False | -728.0c | -44.0c | 84.09% | -1164.0c/436.0c | 79.41%/89.06% | 23/1 | 0.462 | -340.0c |
| `p80_ask90_sec0_touch_preempt_book0.85_touch0.5_ask55_age300` | False | -388.0c | -52.0c | 81.82% | -873.0c/485.0c | 80.39%/88.52% | 20/1 | 0.500 | -281.0c |

## Read

- No p80 touch-conflict rule clears the strict gate.
- This is post-hoc research and must be forward-locked before any live use.
