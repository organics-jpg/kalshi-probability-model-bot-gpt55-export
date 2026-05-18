# v28 Frozen Target-Coverage P70 FV

- Freeze timestamp UTC: `2026-05-06T03:45:32.798460+00:00`
- Entry policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Variant: `logit125_p70`
- Future entries/settled/denominator: `97/97/135`
- Coverage: `71.851852`
- Best variant: `logit125_p70`

## Current Read

- Frozen target-coverage p70 FV has 97 entries over 135 future markets.
- Best variant is logit125_p70 with Brier/logloss deltas 0.0003572449270448449/-0.0008767815212288292.

## Ranking

| rank | variant | rows | W/L | net c | brier mean | brier p95 | logloss mean | logloss p95 | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `logit125_p70` | 97 | 53/44 | -769.000000 | 0.000357 | 0.003511 | -0.000877 | 0.008481 | mean_brier_not_better, brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| 2 | `raw_probability` | 97 | 53/44 | -769.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | none |
