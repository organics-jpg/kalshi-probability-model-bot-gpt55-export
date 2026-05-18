# v28 Frozen Raw p52 Book-Shrink Entry

Future-only validator. No live orders.

- Candidate live-ready: `False`
- Freeze timestamp UTC: `2026-05-06T12:12:25.258308+00:00`
- Rule: `If raw p - executable ask > 15pp, blend 50% toward executable ask; then require p>=0.52 and edge>=0.`
- Future denominator: `101`
- Delta vs base: `-105.000000c`
- Blockers: `coverage_too_high, net_not_positive, simulated_share_gt_35pct`

## Summary

| row | entries | settled | W/L | coverage | net c | avg brier | shrunk | actual/sim |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| base | 99 | 99 | 57/42 | 98.019802 | -540.000000 | 0.218517 | 0 | 7/92 |
| candidate_summary | 99 | 99 | 59/40 | 98.019802 | -645.000000 | 0.215265 | 7 | 11/88 |
