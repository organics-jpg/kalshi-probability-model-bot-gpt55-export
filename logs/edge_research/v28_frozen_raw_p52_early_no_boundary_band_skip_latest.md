# v28 Frozen Raw p52 Middle-Confidence Early-NO Boundary Skip

Future-only validator. No live orders.

- Candidate live-ready: `False`
- Freeze timestamp UTC: `2026-05-06T12:20:19.153557+00:00`
- Rule: `Start from v28_raw_p52_edge0 and skip NO rows with 0.62<=p<0.70, stc>=720, abs_d<=0.45, recross>=0.55.`
- Future denominator: `100`
- Delta vs base: `-186.000000c`
- Blockers: `coverage_too_high, net_not_positive, simulated_share_gt_35pct`

## Summary

| row | entries | settled | W/L | coverage | win rate | avg p | avg ask | avg abs d | avg recross | net c | actual/sim |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| base | 98 | 98 | 57/41 | 98.000000 | 0.581633 | 0.643864 | 0.577449 | 0.356376 | 0.782032 | -418.000000 | 7/91 |
| candidate_summary | 93 | 93 | 53/40 | 93.000000 | 0.569892 | 0.643235 | 0.576559 | 0.355016 | 0.775442 | -604.000000 | 7/86 |
| skipped_summary | 5 | 5 | 4/1 | 5.000000 | 0.800000 | 0.655553 | 0.594000 | 0.381682 | 0.904591 | 186.000000 | 0/5 |
