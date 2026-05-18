# v28 Raw p52 Early-NO Boundary Band Runway

Research-only; no live bot changes or orders.

- Candidate: `raw_p52_skip_midconf_early_no_boundary`
- Freeze timestamp UTC: `2026-05-06T12:20:19.153557+00:00`
- Future denominator: `100`
- Candidate live-ready: `False`
- Ready for consideration: `False`
- Delta vs raw p52: `-186.000000c`
- Blockers: `coverage_too_high, net_not_positive, simulated_share_gt_35pct`

## Checks

| check | passed | value | needed |
|---|---|---:|---:|
| settled_rows_ge_30 | True | 93 | 0 |
| coverage_75_to_90 | False | 93.000000 | 75.0-90.0 |
| candidate_net_positive | False | -604.000000 | >0 |
| delta_vs_raw_positive | False | -186.000000 | >0 |
| simulated_share_lte_35pct | False | 0.924731 | <=0.35 |

## Scorecard

| row | entries | settled | W/L | coverage | net c | actual/sim | sim share |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 98 | 98 | 57/41 | 98.000000 | -418.000000 | 7/91 | 0.928571 |
| candidate_summary | 93 | 93 | 53/40 | 93.000000 | -604.000000 | 7/86 | 0.924731 |
| skipped_summary | 5 | 5 | 4/1 | 5.000000 | 186.000000 | 0/5 | 1.000000 |

## Pending Sensitivity

- Pending skipped rows: `0`
- Adverse swing if all pending skips would have won: `0c`
- Delta after that stress: `-186.000000c`
- Pending markets: `none`

## Current Read

- Need 0 more settled post-freeze candidate rows to reach the 30-row evidence floor.
- Discovery robustness pass is True; forward validation is still separate.
- Promotion remains blocked unless the candidate keeps target coverage, positive net, positive delta versus raw p52, and acceptable simulated share.
