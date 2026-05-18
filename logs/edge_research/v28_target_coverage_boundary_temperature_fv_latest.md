# v28 Target-Coverage Boundary Temperature FV

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Entries/settled/denominator: `112/112/152`
- Best variant: `boundary_temp_strong`

## Current Read

- Best boundary-temperature diagnostic is boundary_temp_strong with Brier/logloss mean deltas -0.0031995235964418357/-0.010294988696450912.
- Its Brier/logloss p95 deltas are -0.0004388902675230081/-0.002473951489693075.
- Diagnostic only; freeze separately before using future rows as promotion evidence.

## Ranking

| rank | variant | rows | adjusted | W/L | avg p | brier mean | brier p95 | logloss mean | logloss p95 | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `boundary_temp_strong` | 112 | 66 | 64/48 | 0.660804 | -0.003200 | -0.000439 | -0.010295 | -0.002474 | none |
| 2 | `boundary_temp_medium` | 112 | 66 | 64/48 | 0.662478 | -0.002929 | -0.000384 | -0.009746 | -0.002238 | none |
| 3 | `boundary_temp_light` | 112 | 66 | 64/48 | 0.664152 | -0.002635 | -0.000221 | -0.009148 | -0.001835 | none |
| 4 | `thin_recross_book_blend` | 112 | 44 | 64/48 | 0.666050 | -0.002390 | -0.000026 | -0.008647 | -0.001379 | none |
| 5 | `conservative_logit125_calm_mid_or_p75` | 112 | 34 | 64/48 | 0.666383 | -0.002210 | 0.000145 | -0.008271 | -0.001020 | brier_interval_not_strictly_negative |
| 6 | `raw_probability` | 112 | 0 | 64/48 | 0.653763 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | none |
