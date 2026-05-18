# v28 Frozen Target-Coverage p70 Empirical Bayes

- Freeze timestamp UTC: `2026-05-06T04:22:07.414318+00:00`
- Entry policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Variant: `p70_empirical_bayes_prior6`
- Future entries/settled/denominator: `96/96/132`
- Adjusted evidence count/current scale: `25/1.201613`
- Coverage: `72.727273`
- Best variant: `p70_empirical_bayes_prior6`

## Current Read

- Frozen empirical-Bayes p70 FV has 96 entries over 132 future markets.
- Current earned scale is 1.2016129032258065.
- Best variant is p70_empirical_bayes_prior6 with Brier/logloss deltas 0.00020287969881573994/-0.001017654351857106.

## Ranking

| rank | variant | rows | adjusted | W/L | net c | brier mean | brier p95 | logloss mean | logloss p95 | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `p70_empirical_bayes_prior6` | 96 | 25 | 53/43 | -663.000000 | 0.000203 | 0.002809 | -0.001018 | 0.006672 | mean_brier_not_better, brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| 2 | `raw_probability` | 96 | 0 | 53/43 | -663.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | none |
