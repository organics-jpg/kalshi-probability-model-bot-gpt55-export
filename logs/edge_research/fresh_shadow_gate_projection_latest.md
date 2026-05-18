# Fresh Shadow Gate Projection

Generated UTC: `20260502_152508Z`

## Current Fresh State

- Rule: `ask<=100; block 15m adverse>10 unless v28 cushion>0.5`
- Fresh baseline: 10/12 contracts = 83.33%
- Fresh selected: 8/8 contracts = 100.00%
- Fresh selected retention: 66.67%
- Sample ready: False
- Accuracy gate: True
- Retention gate: False

## Minimum Future Evidence At Sample Floor

| retention floor | unit | current selected | minimum selected | add selected needed | max future blocked | selected losses allowed |
|---:|---|---:|---:|---:|---:|---:|
| 75.00% | trades | 4 | 75 | 71 | 23 | 3 |
| 75.00% | contracts | 8 | 150 | 142 | 46 | 7 |
| 80.00% | trades | 4 | 75 | 71 | 16 | 3 |
| 80.00% | contracts | 8 | 150 | 142 | 33 | 7 |

## Readout

At the 75% retention floor, the shadow needs at least 71 more selected trades and 142 more selected contracts. At that sample floor it can block at most 23 future baseline trades / 46 future baseline contracts while staying at 75% retention.
At the 80% retention floor, it can block at most 16 future baseline trades / 33 future baseline contracts at the same minimum selected sample.
Accuracy is not the current blocker on the tiny fresh sample; volume retention and sample size are.
