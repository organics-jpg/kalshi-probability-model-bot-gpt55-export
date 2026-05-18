# v28 Frozen Raw p52 Early-NO Boundary Skip

Future-only validator. No live orders.

- Candidate live-ready: `False`
- Freeze timestamp UTC: `2026-05-06T12:18:20.259368+00:00`
- Rule: `Start from v28_raw_p52_edge0 and skip NO rows with stc>=720, p<0.70, abs_d<=0.45, recross>=0.55.`
- Future denominator: `100`
- Delta vs base: `-26.000000c`
- Blockers: `coverage_too_low, net_not_positive, simulated_share_gt_35pct`

## Summary

| row | entries | settled | W/L | coverage | win rate | avg p | avg ask | avg abs d | avg recross | net c | actual/sim |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| base | 98 | 98 | 57/41 | 98.000000 | 0.581633 | 0.643864 | 0.577449 | 0.356376 | 0.782032 | -418.000000 | 7/91 |
| candidate_summary | 73 | 73 | 43/30 | 73.000000 | 0.589041 | 0.663203 | 0.592055 | 0.402151 | 0.716494 | -444.000000 | 7/66 |
| skipped_summary | 25 | 25 | 14/11 | 25.000000 | 0.560000 | 0.587393 | 0.534800 | 0.222713 | 0.973403 | 26.000000 | 0/25 |
