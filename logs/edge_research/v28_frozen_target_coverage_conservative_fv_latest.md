# v28 Frozen Target-Coverage Conservative FV

- Freeze timestamp UTC: `2026-05-06T03:26:44.025585+00:00`
- Entry policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Variant: `logit125_p60_calm_mid_or_p75`
- Future entries/settled/denominator: `98/98/136`
- Coverage: `72.058824`
- Best variant: `logit125_p60_calm_mid_or_p75`

## Current Read

- Frozen conservative target-coverage FV has 98 entries over 136 future markets.
- Best variant is logit125_p60_calm_mid_or_p75 with Brier/logloss deltas -0.0019986929824834733/-0.006824434041934604.

## Ranking

| rank | variant | rows | W/L | net c | brier mean | brier p95 | logloss mean | logloss p95 | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `logit125_p60_calm_mid_or_p75` | 98 | 54/44 | -699.000000 | -0.001999 | 0.000537 | -0.006824 | 0.000995 | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| 2 | `raw_probability` | 98 | 54/44 | -699.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | none |
