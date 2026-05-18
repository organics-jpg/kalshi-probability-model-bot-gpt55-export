# v28 Target-Coverage Confidence Temperature Bakeoff

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Entries/settled/denominator: `112/112/152`
- Best variant: `hard_logit125_p72`

## Current Read

- Best confidence-temperature diagnostic is hard_logit125_p72 with Brier/logloss mean deltas -0.0013255736275738735/-0.006030666765288752.
- Hard p70 has Brier/logloss mean deltas -0.0003773633313270222/-0.003571990138160214 and p95s 0.0023892238258019617/0.004690031549703919.
- If a smooth variant only wins by adjusting more boundary rows, it needs a stronger physics argument and a frozen validator before promotion.

## Ranking

| rank | variant | rows | adjusted | W/L | avg p | brier mean | brier p95 | brier -/+ /0 | logloss mean | logloss p95 | logloss -/+ /0 | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `hard_logit125_p72` | 112 | 28 | 64/48 | 0.665026 | -0.001326 | 0.001015 | 25/3/84 | -0.006031 | 0.001355 | 25/3/84 | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| 2 | `smooth_logit_ramp_70_90` | 112 | 31 | 64/48 | 0.659792 | -0.000899 | 0.000026 | 30/5/77 | -0.004506 | -0.001260 | 30/5/77 | brier_interval_not_strictly_negative |
| 3 | `smooth_logit_ramp_65_85` | 112 | 45 | 64/48 | 0.662799 | -0.000802 | 0.000731 | 38/11/63 | -0.004616 | 0.000340 | 38/11/63 | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| 4 | `heat_gated_hard_p70` | 112 | 31 | 64/48 | 0.666029 | -0.000409 | 0.002279 | 26/5/81 | -0.003671 | 0.004465 | 26/5/81 | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| 5 | `hard_logit125_p70` | 112 | 31 | 64/48 | 0.666195 | -0.000377 | 0.002389 | 26/5/81 | -0.003572 | 0.004690 | 26/5/81 | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| 6 | `heat_gated_smooth_60_80` | 112 | 76 | 64/48 | 0.666469 | -0.000165 | 0.002008 | 49/29/34 | -0.003238 | 0.003634 | 49/29/34 | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| 7 | `smooth_logit_ramp_60_80` | 112 | 76 | 64/48 | 0.666882 | -0.000113 | 0.002132 | 49/29/34 | -0.003101 | 0.003885 | 49/29/34 | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| 8 | `hard_logit125_p68` | 112 | 32 | 64/48 | 0.666550 | 0.000120 | 0.002991 | 26/6/80 | -0.002382 | 0.006104 | 26/6/80 | mean_brier_not_better, brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| 9 | `raw_probability` | 112 | 0 | 64/48 | 0.653763 | 0.000000 | 0.000000 | 0/0/112 | 0.000000 | 0.000000 | 0/0/112 | none |
