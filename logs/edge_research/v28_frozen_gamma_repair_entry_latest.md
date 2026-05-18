# v28 Frozen Gamma Repair Entry

Future-only target-coverage repair. No live orders.

- Freeze timestamp UTC: `2026-05-06T11:43:09.046274+00:00`
- Base policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Candidate: `target_plus_gamma_repair_to_75pct`
- Future denominator: `103`
- Promotion ready: `False`
- Blockers: `repairs_all_simulated`

## Current Read

- Candidate has 78 entries, coverage 75.72815533980582, net 43.0c.
- Repairs used/needed/available: 1/1/14.
- Delta versus target: -31.0c.
- Blockers: repairs_all_simulated.

## Scorecard

| window | entries | settled | W/L | coverage | net c |
|---|---:|---:|---:|---:|---:|
| target | 77 | 77 | 45/32 | 74.757282 | 74.000000 |
| repairs | 1 | 1 | 0/1 | 0.970874 | -31.000000 |
| candidate | 78 | 78 | 45/33 | 75.728155 | 43.000000 |

## Repair Rows

| market | ts | side | source | p | ask | edge | abs d | recross | won | net c |
|---|---|---|---|---:|---:|---:|---:|---:|---|---:|
| KXBTC15M-26MAY060845-45 | 2026-05-06T12:38:51.250094+00:00 | yes | rejected_actionable | 0.322909 | 28.000000 | 0.042909 | 0.414768 | 0.356454 | False | -31.000000 |
