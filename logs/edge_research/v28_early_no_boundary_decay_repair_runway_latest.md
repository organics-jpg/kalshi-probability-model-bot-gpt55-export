# v28 Early-NO Boundary Decay Repair Runway

Research-only; no live bot changes or orders.

- Candidate: `skip_early_no_boundary_decay_repair_calm_geometry`
- Freeze timestamp UTC: `2026-05-06T09:10:09.146392+00:00`
- Future denominator: `113`
- Candidate live-ready: `True`
- Ready for consideration: `True`
- Blockers: `none`

## Checks

| check | passed | actual | required | remaining |
|---|---:|---:|---:|---:|
| settled_rows_ge_30 | True | 85 | >=30 | 0 |
| coverage_75_to_90 | True | 75.221239 | 75.0-90.0 | None |
| net_positive | True | 27.000000 | >0c | None |
| delta_vs_target_positive | True | 84.000000 | >0c | None |

## Scorecard

| surface | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| target_summary | 83 | 83 | 48/35 | 73.451327 | -57.000000 | -0.686747 |
| danger_summary | 30 | 30 | 14/16 | 26.548673 | -314.000000 | -10.466667 |
| repair_summary | 32 | 32 | 22/10 | 28.318584 | -230.000000 | -7.187500 |
| candidate_summary | 85 | 85 | 56/29 | 75.221239 | 27.000000 | 0.317647 |

## Fragility

- Rows needed for 30: `0`
- Net cushion: `27.000000c`
- Delta cushion: `84.000000c`
- Full 100c losses before net flat: `0`
- Full 100c losses before delta flat: `0`

## Pending Danger Stress

- Pending danger rows: `0`
- Pending markets: `none`
- Stressed delta if all pending danger rows would have won: `84.000000c`

## Current Read

- Need 0 more settled candidate rows before the sample-size gate is met.
- Candidate net is 27.0c versus target -57.0c.
- The rule has a clean physics story, but current evidence can be broken by a small number of adverse future rows.

## Worst Leave-One Repair Rows

| market | side | row net c | candidate net without row c |
|---|---|---:|---:|
| KXBTC15M-26MAY060845-45 | no | 37.000000 | -10.000000 |
| KXBTC15M-26MAY061415-15 | no | 34.000000 | -7.000000 |
| KXBTC15M-26MAY062215-15 | no | 33.000000 | -6.000000 |
| KXBTC15M-26MAY061000-00 | no | 31.000000 | -4.000000 |
| KXBTC15M-26MAY061145-45 | no | 27.000000 | 0.000000 |
