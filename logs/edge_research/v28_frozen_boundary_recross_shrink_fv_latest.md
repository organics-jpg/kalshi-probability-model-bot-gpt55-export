# v28 Frozen Boundary/Recross Shrink FV

- Freeze timestamp UTC: `2026-05-06T05:29:47.434585+00:00`
- Entry policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Variant: `boundary_recross_shrink_probability`
- Future entries/settled/denominator: `93/93/128`
- Coverage: `72.656250`
- Best variant: `boundary_recross_shrink_probability`

## Current Read

- Frozen boundary/recross shrink has 93 entries over 128 future markets.
- This starts from its own freeze timestamp and is not promotion evidence until it reaches forward sample size.

## Ranking

| rank | variant | rows | adjusted | W/L | net c | brier mean | brier p95 | logloss mean | logloss p95 | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `boundary_recross_shrink_probability` | 93 | 74 | 51/42 | -619.000000 | -0.006722 | 0.002298 | -0.014190 | 0.005186 | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| 2 | `raw_probability` | 93 | 0 | 51/42 | -619.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | none |
