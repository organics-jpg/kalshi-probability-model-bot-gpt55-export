# v28 p50 Book-Edge Source Failure Drilldown

Research-only drilldown of the frozen p50 book-edge entry lane. No live orders.

- Generated UTC: `2026-05-11T03:10:50.690354+00:00`
- Candidate: `p50_book_plus_05_edge_nonnegative`
- Future denominator markets: `118`
- Base entries/settled/W-L: `104/104/64-40`
- Base gross/coverage/source share: `660.000000c/88.135593%/0.788462`
- Base blockers: `simulated_share_gt_35pct`
- Candidate live-ready: `False`

## Interpretation

- The broad p50 book-edge lane is profitable but remains source-blocked; source labels are audit-only and cannot be used as a live rule.
- Approved rows are very clean but too sparse; the rejected-actionable slice still contributes positive PnL while carrying most of the full-loss risk.
- The strongest observable failure clue is side asymmetry: YES rows are strongly positive while NO rows are net negative in this sample.
- All variants here are diagnostic repairs. Any live-testable child needs its own frozen forward birth and the controlled live-test gate.

## Source Splits

| Source | Entries | W-L | Gross c | Coverage % | Rejected share |
|---|---:|---:|---:|---:|---:|
| `rejected_actionable` | 82 | 45-37 | 484.000000 | 69.491525 | 1.000000 |
| `approved_entry` | 22 | 19-3 | 176.000000 | 18.644068 | 0.000000 |

## Top Observable Buckets

| Bucket | Entries | W-L | Gross c | Coverage % |
|---|---:|---:|---:|---:|
| `recross_gte_075` | 32 | 20-12 | 870.000000 | 27.118644 |
| `edge_lt_3` | 41 | 31-10 | 642.000000 | 34.745763 |
| `raw_edge_lt_5` | 41 | 31-10 | 642.000000 | 34.745763 |
| `abs_d_lt_025` | 36 | 17-19 | 426.000000 | 30.508475 |
| `abs_d_gte_065` | 34 | 29-5 | 378.000000 | 28.813559 |
| `side_no` | 45 | 30-15 | 332.000000 | 38.135593 |
| `side_yes` | 59 | 34-25 | 328.000000 | 50.000000 |
| `early_gt_720s` | 57 | 34-23 | 324.000000 | 48.305085 |
| `yes_side_abs_d_gte_065` | 17 | 14-3 | 288.000000 | 14.406780 |
| `no_side_abs_d_lt_065` | 28 | 15-13 | 242.000000 | 23.728814 |
| `abs_d_050_065` | 9 | 7-2 | 216.000000 | 7.627119 |
| `late_lt_240s` | 4 | 3-1 | 28.000000 | 3.389831 |
| `edge_gte_3` | 63 | 33-30 | 18.000000 | 53.389831 |
| `depth_lt_200` | 47 | 29-18 | 10.000000 | 39.830508 |
| `recross_gte_060` | 56 | 27-29 | -46.000000 | 47.457627 |
| `no_side_recross_gte_060` | 23 | 11-12 | -48.000000 | 19.491525 |

## Loss Tags

| Tag | Losses | Loss gross c |
|---|---:|---:|
| `source_quality_error` | 37 | -3360.000000 |
| `early_clock` | 23 | -2204.000000 |
| `near_strike_boundary` | 19 | -1408.000000 |
| `low_depth` | 18 | -1640.000000 |
| `high_recross_hazard` | 17 | -1558.000000 |
| `weak_boundary_distance` | 16 | -1650.000000 |
| `no_side_error` | 15 | -1312.000000 |
| `extreme_recross_hazard` | 12 | -1114.000000 |
| `thin_fee_edge` | 10 | -1066.000000 |
| `thin_raw_edge` | 10 | -1066.000000 |
| `stale_source_age` | 3 | -358.000000 |
| `late_clock` | 1 | -106.000000 |

## Variant Bakeoff

| Variant | Entries | W-L | Gross c | Coverage % | Rejected share | Cushion | Blockers |
|---|---:|---:|---:|---:|---:|---:|---|
| `yes_or_no_recross_lt_060` | 81 | 53-28 | 708.000000 | 68.644068 | 0.728395 | 7 | `coverage_too_low, rejected_actionable_share_gt_35pct` |
| `drop_recross_gte_060` | 48 | 37-11 | 706.000000 | 40.677966 | 0.541667 | 7 | `coverage_too_low, rejected_actionable_share_gt_35pct` |
| `base` | 104 | 64-40 | 660.000000 | 88.135593 | 0.788462 | 6 | `rejected_actionable_share_gt_35pct` |
| `drop_depth_lt_200` | 57 | 35-22 | 650.000000 | 48.305085 | 0.824561 | 6 | `coverage_too_low, rejected_actionable_share_gt_35pct` |
| `drop_recross60_absd65` | 50 | 38-12 | 626.000000 | 42.372881 | 0.560000 | 6 | `coverage_too_low, rejected_actionable_share_gt_35pct` |
| `drop_abs_d_lt_050` | 43 | 36-7 | 594.000000 | 36.440678 | 0.488372 | 5 | `coverage_too_low, rejected_actionable_share_gt_35pct` |
| `half_weak_or_recross` | 104 | 64-40 | 559.000000 | 88.135593 | 0.676471 | 5 | `rejected_actionable_share_gt_35pct` |
| `half_no_weak_or_recross` | 104 | 64-40 | 539.000000 | 88.135593 | 0.755556 | 5 | `rejected_actionable_share_gt_35pct` |
| `quarter_weak_or_recross` | 104 | 64-40 | 508.500000 | 88.135593 | 0.560000 | 5 | `rejected_actionable_share_gt_35pct` |
| `half_no_side` | 104 | 64-40 | 494.000000 | 88.135593 | 0.797546 | 4 | `rejected_actionable_share_gt_35pct` |
| `quarter_no_weak_or_recross` | 104 | 64-40 | 478.500000 | 88.135593 | 0.734940 | 4 | `rejected_actionable_share_gt_35pct` |
| `yes_or_absd_gte_065` | 76 | 49-27 | 418.000000 | 64.406780 | 0.710526 | 4 | `coverage_too_low, rejected_actionable_share_gt_35pct` |
| `yes_or_no_absd065_recross060` | 76 | 49-27 | 418.000000 | 64.406780 | 0.710526 | 4 | `coverage_too_low, rejected_actionable_share_gt_35pct` |
| `drop_no_weak_or_high_recross` | 76 | 49-27 | 418.000000 | 64.406780 | 0.710526 | 4 | `coverage_too_low, rejected_actionable_share_gt_35pct` |
| `quarter_no_side` | 104 | 64-40 | 411.000000 | 88.135593 | 0.804270 | 4 | `rejected_actionable_share_gt_35pct` |
| `drop_abs_d_lt_065` | 34 | 29-5 | 378.000000 | 28.813559 | 0.352941 | 3 | `coverage_too_low, rejected_actionable_share_gt_35pct` |
| `drop_early_gt_720` | 47 | 30-17 | 336.000000 | 39.830508 | 0.702128 | 3 | `coverage_too_low, rejected_actionable_share_gt_35pct` |
| `no_only` | 45 | 30-15 | 332.000000 | 38.135593 | 0.755556 | 3 | `coverage_too_low, rejected_actionable_share_gt_35pct` |
| `yes_only` | 59 | 34-25 | 328.000000 | 50.000000 | 0.813559 | 3 | `coverage_too_low, rejected_actionable_share_gt_35pct` |
| `drop_no_side` | 59 | 34-25 | 328.000000 | 50.000000 | 0.813559 | 3 | `coverage_too_low, rejected_actionable_share_gt_35pct` |
| `drop_edge_lt_3` | 63 | 33-30 | 18.000000 | 53.389831 | 0.809524 | 0 | `coverage_too_low, rejected_actionable_share_gt_35pct, full_loss_cushion_lt_3` |
| `drop_raw_edge_lt_5` | 63 | 33-30 | 18.000000 | 53.389831 | 0.809524 | 0 | `coverage_too_low, rejected_actionable_share_gt_35pct, full_loss_cushion_lt_3` |
| `drop_recross_gte_075` | 72 | 44-28 | -210.000000 | 61.016949 | 0.694444 | 0 | `coverage_too_low, gross_not_positive, rejected_actionable_share_gt_35pct, full_loss_cushion_lt_3` |

## Best Positive Target-Coverage Variant

- Variant: `base`
- Entries/settled/W-L: `104/104/64-40`
- Gross/coverage/rejected share/cushion: `660.000000c/88.135593%/0.788462/6`
- Blockers: `rejected_actionable_share_gt_35pct`
