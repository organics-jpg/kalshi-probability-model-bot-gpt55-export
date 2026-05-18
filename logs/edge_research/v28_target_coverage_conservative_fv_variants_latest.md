# v28 Target-Coverage Conservative FV Variants

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Forward entries/settled/denominator: `112/112/152`
- Best variant: `logit125_p60_calm_mid_or_p75`

## Current Read

- Best conservative target-coverage FV variant is logit125_p60_calm_mid_or_p75 with Brier/logloss mean deltas -0.0022095221651635597/-0.008271439367388467.
- Its Brier/logloss p95 deltas are 0.00023302876583982003/-0.0010341869828960474.
- Discovery/diagnostic only unless frozen forward from this timestamp.

## Ranking

| rank | variant | rows | W/L | avg p | brier mean | brier p95 | brier -/+ | logloss mean | logloss p95 | logloss -/+ | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `logit125_p60_calm_mid_or_p75` | 112 | 64/48 | 0.666383 | -0.002210 | 0.000233 | 30/4 | -0.008271 | -0.001034 | 30/4 | brier_interval_not_strictly_negative |
| 2 | `logit125_p75` | 112 | 64/48 | 0.662127 | -0.001577 | 0.000103 | 20/1 | -0.006753 | -0.000926 | 20/1 | brier_interval_not_strictly_negative |
| 3 | `logit125_p80` | 112 | 64/48 | 0.658604 | -0.001090 | -0.000600 | 13/0 | -0.005465 | -0.003229 | 13/0 | none |
| 4 | `logit125_p70` | 112 | 64/48 | 0.666195 | -0.000377 | 0.002382 | 26/5 | -0.003572 | 0.004777 | 26/5 | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| 5 | `logit125_p60` | 112 | 64/48 | 0.678692 | 0.003992 | 0.008480 | 47/29 | 0.006047 | 0.017422 | 47/29 | mean_brier_not_better, brier_interval_not_strictly_negative, mean_logloss_not_better, logloss_interval_not_strictly_negative |
| 6 | `raw_probability` | 112 | 64/48 | 0.653763 | 0.000000 | 0.000000 | 0/0 | 0.000000 | 0.000000 | 0/0 | none |
