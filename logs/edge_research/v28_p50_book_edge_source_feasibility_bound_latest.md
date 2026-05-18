# v28 p50 Book-Edge Source Feasibility Bound

Research-only arithmetic source-quality bound. No live orders.

- Generated UTC: `2026-05-11T03:10:50.889181+00:00`
- Candidate: `p50_book_plus_05_edge_nonnegative`
- Selected entries/approved/rejected/share: `104/22/82/0.788462`
- Selected W-L/net: `64-40/660.000000c`
- Target min/max entries: `89/106`
- Approved needed at min target coverage: `58`
- Approved deficit at min target coverage: `36`
- Max source-clean entries/coverage from current selected approved pool: `33/27.966102%`
- Source gate feasible at target coverage: `False`

## Interpretation

- At 118 denominator markets, 75% coverage needs 89 selected markets.
- With a 35% rejected-actionable cap, that minimum target needs 58 approved rows.
- The current selected p50 pool has only 22 approved rows, so its source-clean max coverage is 27.966101694915253%.
- Therefore p50 book-edge cannot be made broad-and-source-clean by reshuffling its current selected rows; it needs new clean approved evidence or a different approved-rich entry surface.

## Top Variant Source Status

| variant | entries | W-L | gross c | coverage % | rejected share | weighted rejected share | blockers |
|---|---:|---:|---:|---:|---:|---:|---|
| `yes_or_no_recross_lt_060` | 81 | 53-28 | 708.000000 | 68.644068 | 0.728395 | 0.728395 | `coverage_too_low, rejected_actionable_share_gt_35pct` |
| `drop_recross_gte_060` | 48 | 37-11 | 706.000000 | 40.677966 | 0.541667 | 0.541667 | `coverage_too_low, rejected_actionable_share_gt_35pct` |
| `base` | 104 | 64-40 | 660.000000 | 88.135593 | 0.788462 | 0.788462 | `rejected_actionable_share_gt_35pct` |
| `drop_depth_lt_200` | 57 | 35-22 | 650.000000 | 48.305085 | 0.824561 | 0.824561 | `coverage_too_low, rejected_actionable_share_gt_35pct` |
| `drop_recross60_absd65` | 50 | 38-12 | 626.000000 | 42.372881 | 0.560000 | 0.560000 | `coverage_too_low, rejected_actionable_share_gt_35pct` |
| `drop_abs_d_lt_050` | 43 | 36-7 | 594.000000 | 36.440678 | 0.488372 | 0.488372 | `coverage_too_low, rejected_actionable_share_gt_35pct` |
| `half_weak_or_recross` | 104 | 64-40 | 559.000000 | 88.135593 | 0.788462 | 0.676471 | `rejected_actionable_share_gt_35pct` |
| `half_no_weak_or_recross` | 104 | 64-40 | 539.000000 | 88.135593 | 0.788462 | 0.755556 | `rejected_actionable_share_gt_35pct` |
| `quarter_weak_or_recross` | 104 | 64-40 | 508.500000 | 88.135593 | 0.788462 | 0.560000 | `rejected_actionable_share_gt_35pct` |
| `half_no_side` | 104 | 64-40 | 494.000000 | 88.135593 | 0.788462 | 0.797546 | `rejected_actionable_share_gt_35pct` |
| `quarter_no_weak_or_recross` | 104 | 64-40 | 478.500000 | 88.135593 | 0.788462 | 0.734940 | `rejected_actionable_share_gt_35pct` |
| `yes_or_absd_gte_065` | 76 | 49-27 | 418.000000 | 64.406780 | 0.710526 | 0.710526 | `coverage_too_low, rejected_actionable_share_gt_35pct` |
