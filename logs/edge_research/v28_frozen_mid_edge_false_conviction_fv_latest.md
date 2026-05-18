# v28 Frozen Mid-Edge False-Conviction FV

- Freeze timestamp UTC: `2026-05-06T09:29:25.082774+00:00`
- Entry policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Variant: `mid_edge_false_conviction_shrink`
- Future entries/settled/denominator: `82/82/112`
- Coverage: `73.214286`
- Best variant: `mid_edge_false_conviction_shrink`

## Current Read

- Frozen mid-edge false-conviction FV has 82 entries over 112 future markets.
- This is a probability calibration challenger, not an entry rule; it starts earning evidence only after its freeze timestamp.

## Ranking

| rank | variant | rows | adjusted | false-conviction | W/L | net c | brier mean | brier p95 | logloss mean | logloss p95 | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `mid_edge_false_conviction_shrink` | 82 | 13 | 13 | 48/34 | 35.000000 | 0.001180 | 0.004277 | 0.002486 | 0.008890 | mean_brier_not_better, brier_interval_not_strictly_negative, mean_logloss_not_better, logloss_interval_not_strictly_negative |
| 2 | `raw_probability` | 82 | 0 | 13 | 48/34 | 35.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | none |
