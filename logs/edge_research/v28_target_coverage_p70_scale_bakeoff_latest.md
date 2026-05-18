# v28 Target-Coverage p70 Scale Bakeoff

- Rows: `112`
- Best robustness-ranked scale: `1.05`

## Current Read

- Best calibration scale is 1.2 with Brier/logloss mean deltas -0.0004094725518588955/-0.00320178696744626.
- Robustness-ranked scale is 1.05 with first adverse p80 break count 1.
- If all scales break on the first adverse p80 row, the problem is sample fragility, not scale tuning.

## Ranking

| scale | rows | adjusted | avg adjusted p | brier mean | brier p95 | logloss mean | logloss p95 | adverse p80 scaled | first brier break | first logloss break | first any break |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.050000 | 112 | 31 | 0.812139 | -0.000197 | 0.000387 | -0.001079 | 0.000611 | 0.810860 | 1 | 1 | 1 |
| 1.100000 | 112 | 31 | 0.821551 | -0.000326 | 0.000853 | -0.001965 | 0.001417 | 0.821262 | 1 | 1 | 1 |
| 1.150000 | 112 | 31 | 0.830518 | -0.000395 | 0.001330 | -0.002670 | 0.002337 | 0.831212 | 1 | 1 | 1 |
| 1.200000 | 112 | 31 | 0.839056 | -0.000409 | 0.001736 | -0.003202 | 0.003215 | 0.840714 | 1 | 1 | 1 |
| 1.250000 | 112 | 31 | 0.847184 | -0.000377 | 0.002438 | -0.003572 | 0.004708 | 0.849779 | 1 | 1 | 1 |
| 1.300000 | 112 | 31 | 0.854917 | -0.000304 | 0.002915 | -0.003789 | 0.005962 | 0.858414 | 1 | 1 | 1 |
