# v28 Frozen Edge-Phase Shrink FV

- Freeze timestamp UTC: `2026-05-06T05:40:31.466696+00:00`
- Entry policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Variant: `edge_phase_shrink`
- Future entries/settled/denominator: `93/93/127`
- Coverage: `73.228346`
- Best variant: `edge_phase_shrink`

## Current Read

- Frozen edge-phase shrink has 93 entries over 127 future markets.
- This starts from its own freeze timestamp and is not promotion evidence until it reaches forward sample size.

## Ranking

| rank | variant | rows | adjusted | W/L | net c | brier mean | brier p95 | logloss mean | logloss p95 | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `edge_phase_shrink` | 93 | 42 | 51/42 | -619.000000 | -0.005423 | 0.001950 | -0.011602 | 0.003538 | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| 2 | `raw_probability` | 93 | 0 | 51/42 | -619.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | none |
