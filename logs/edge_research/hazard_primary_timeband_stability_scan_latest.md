# Hazard Primary Time-Band Stability Scan

Generated UTC: `20260504_081029Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Tests whether capping early hazard-primary entries improves robustness under timestamp-causal arbitration.
- Any passing row must still be forward-locked before use.

## Combined Read

| candidate | combined net | coverage | all splits | OOS | min positive+coverage blocks | robust |
|---|---:|---|---|---|---:|---|
| `hazard45_max900_else_score_min60` | 1964.0c | True | True | True | 63.64% | False |
| `hazard45_nomax_else_score_min60` | 1964.0c | True | True | True | 63.64% | False |
| `hazard50_max900_else_score_min60` | 1854.0c | True | True | True | 63.64% | False |
| `hazard50_nomax_else_score_min60` | 1854.0c | True | True | True | 63.64% | False |
| `hazard45_max780_else_score_min60` | 1798.0c | True | False | True | 63.64% | False |
| `hazard45_max660_else_score_min60` | 1682.0c | True | False | True | 63.64% | False |
| `hazard50_max780_else_score_min60` | 1675.0c | True | False | True | 63.64% | False |
| `hazard45_max420_else_score_min60` | 1670.0c | True | False | True | 63.64% | False |
| `hazard45_max540_else_score_min60` | 1670.0c | True | False | True | 63.64% | False |
| `hazard50_max420_else_score_min60` | 1670.0c | True | False | True | 63.64% | False |
| `hazard50_max540_else_score_min60` | 1670.0c | True | False | True | 63.64% | False |
| `hazard50_max660_else_score_min60` | 1670.0c | True | False | True | 63.64% | False |
| `hazard45_max540_else_logit_thresh55_edge15` | 1691.0c | True | True | True | 60.00% | False |
| `hazard50_max420_else_logit_thresh55_edge15` | 1689.0c | True | True | True | 60.00% | False |
| `hazard50_max540_else_logit_thresh55_edge15` | 1689.0c | True | True | True | 60.00% | False |
| `hazard50_max660_else_logit_thresh55_edge15` | 1689.0c | True | True | True | 60.00% | False |
| `hazard50_max780_else_logit_thresh55_edge15` | 1687.0c | True | True | True | 60.00% | False |
| `hazard50_max900_else_logit_thresh55_edge15` | 1687.0c | True | True | True | 60.00% | False |
| `hazard50_nomax_else_logit_thresh55_edge15` | 1687.0c | True | True | True | 60.00% | False |
| `hazard45_max420_else_logit_thresh55_edge15` | 1686.0c | True | True | True | 60.00% | False |
| `hazard45_max660_else_logit_thresh55_edge15` | 1686.0c | True | True | True | 60.00% | False |
| `hazard45_max780_else_logit_thresh55_edge15` | 1683.0c | True | True | True | 60.00% | False |
| `hazard45_max900_else_logit_thresh55_edge15` | 1671.0c | True | True | True | 60.00% | False |
| `hazard45_nomax_else_logit_thresh55_edge15` | 1671.0c | True | True | True | 60.00% | False |

## Split Summary

| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | coverage pass | all splits positive |
|---|---|---:|---:|---:|---:|---:|---|---|
| current | `hazard45_max420_else_logit_thresh55_edge15` | 1133.0c/5.51% | 74.32%/98.98% | 565.0c | 504.0c | 64.0c | True | True |
| v21 | `hazard45_max420_else_logit_thresh55_edge15` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard45_max420_else_score_min60` | 1227.0c/5.88% | 75.68%/98.98% | 677.0c | 453.0c | 97.0c | True | True |
| v21 | `hazard45_max420_else_score_min60` | 443.0c/2.83% | 73.52%/99.10% | -110.0c | 398.0c | 155.0c | True | False |
| current | `hazard45_max540_else_logit_thresh55_edge15` | 1138.0c/5.53% | 74.32%/98.98% | 570.0c | 504.0c | 64.0c | True | True |
| v21 | `hazard45_max540_else_logit_thresh55_edge15` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard45_max540_else_score_min60` | 1227.0c/5.88% | 75.68%/98.98% | 677.0c | 453.0c | 97.0c | True | True |
| v21 | `hazard45_max540_else_score_min60` | 443.0c/2.83% | 73.52%/99.10% | -110.0c | 398.0c | 155.0c | True | False |
| current | `hazard45_max660_else_logit_thresh55_edge15` | 1133.0c/5.51% | 74.32%/98.98% | 565.0c | 504.0c | 64.0c | True | True |
| v21 | `hazard45_max660_else_logit_thresh55_edge15` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard45_max660_else_score_min60` | 1239.0c/5.94% | 75.68%/98.98% | 677.0c | 465.0c | 97.0c | True | True |
| v21 | `hazard45_max660_else_score_min60` | 443.0c/2.83% | 73.52%/99.10% | -110.0c | 398.0c | 155.0c | True | False |
| current | `hazard45_max780_else_logit_thresh55_edge15` | 1130.0c/5.49% | 74.32%/98.98% | 565.0c | 504.0c | 61.0c | True | True |
| v21 | `hazard45_max780_else_logit_thresh55_edge15` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard45_max780_else_score_min60` | 1263.0c/6.06% | 75.68%/98.98% | 691.0c | 475.0c | 97.0c | True | True |
| v21 | `hazard45_max780_else_score_min60` | 535.0c/3.44% | 73.52%/99.10% | -71.0c | 419.0c | 187.0c | True | False |
| current | `hazard45_max900_else_logit_thresh55_edge15` | 1118.0c/5.43% | 74.32%/98.98% | 565.0c | 504.0c | 49.0c | True | True |
| v21 | `hazard45_max900_else_logit_thresh55_edge15` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard45_max900_else_score_min60` | 1268.0c/6.12% | 75.34%/98.98% | 775.0c | 473.0c | 20.0c | True | True |
| v21 | `hazard45_max900_else_score_min60` | 696.0c/4.49% | 73.97%/99.10% | 62.0c | 419.0c | 215.0c | True | True |
| current | `hazard45_nomax_else_logit_thresh55_edge15` | 1118.0c/5.43% | 74.32%/98.98% | 565.0c | 504.0c | 49.0c | True | True |
| v21 | `hazard45_nomax_else_logit_thresh55_edge15` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard45_nomax_else_score_min60` | 1268.0c/6.12% | 75.34%/98.98% | 775.0c | 473.0c | 20.0c | True | True |
| v21 | `hazard45_nomax_else_score_min60` | 696.0c/4.49% | 73.97%/99.10% | 62.0c | 419.0c | 215.0c | True | True |
| current | `hazard50_max420_else_logit_thresh55_edge15` | 1136.0c/5.52% | 74.32%/98.98% | 565.0c | 507.0c | 64.0c | True | True |
| v21 | `hazard50_max420_else_logit_thresh55_edge15` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard50_max420_else_score_min60` | 1227.0c/5.88% | 75.68%/98.98% | 677.0c | 453.0c | 97.0c | True | True |
| v21 | `hazard50_max420_else_score_min60` | 443.0c/2.83% | 73.52%/99.10% | -110.0c | 398.0c | 155.0c | True | False |
| current | `hazard50_max540_else_logit_thresh55_edge15` | 1136.0c/5.52% | 74.32%/98.98% | 565.0c | 507.0c | 64.0c | True | True |
| v21 | `hazard50_max540_else_logit_thresh55_edge15` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard50_max540_else_score_min60` | 1227.0c/5.88% | 75.68%/98.98% | 677.0c | 453.0c | 97.0c | True | True |
| v21 | `hazard50_max540_else_score_min60` | 443.0c/2.83% | 73.52%/99.10% | -110.0c | 398.0c | 155.0c | True | False |
| current | `hazard50_max660_else_logit_thresh55_edge15` | 1136.0c/5.52% | 74.32%/98.98% | 565.0c | 507.0c | 64.0c | True | True |
| v21 | `hazard50_max660_else_logit_thresh55_edge15` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard50_max660_else_score_min60` | 1227.0c/5.88% | 75.68%/98.98% | 677.0c | 453.0c | 97.0c | True | True |
| v21 | `hazard50_max660_else_score_min60` | 443.0c/2.83% | 73.52%/99.10% | -110.0c | 398.0c | 155.0c | True | False |
| current | `hazard50_max780_else_logit_thresh55_edge15` | 1134.0c/5.51% | 74.32%/98.98% | 565.0c | 507.0c | 62.0c | True | True |
| v21 | `hazard50_max780_else_logit_thresh55_edge15` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard50_max780_else_score_min60` | 1229.0c/5.89% | 75.68%/98.98% | 679.0c | 453.0c | 97.0c | True | True |
| v21 | `hazard50_max780_else_score_min60` | 446.0c/2.85% | 73.52%/99.10% | -107.0c | 398.0c | 155.0c | True | False |
| current | `hazard50_max900_else_logit_thresh55_edge15` | 1134.0c/5.51% | 74.32%/98.98% | 565.0c | 507.0c | 62.0c | True | True |
| v21 | `hazard50_max900_else_logit_thresh55_edge15` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard50_max900_else_score_min60` | 1296.0c/6.23% | 75.68%/98.98% | 823.0c | 453.0c | 20.0c | True | True |
| v21 | `hazard50_max900_else_score_min60` | 558.0c/3.57% | 73.97%/99.10% | 5.0c | 398.0c | 155.0c | True | True |
| current | `hazard50_nomax_else_logit_thresh55_edge15` | 1134.0c/5.51% | 74.32%/98.98% | 565.0c | 507.0c | 62.0c | True | True |
| v21 | `hazard50_nomax_else_logit_thresh55_edge15` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard50_nomax_else_score_min60` | 1296.0c/6.23% | 75.68%/98.98% | 823.0c | 453.0c | 20.0c | True | True |
| v21 | `hazard50_nomax_else_score_min60` | 558.0c/3.57% | 73.97%/99.10% | 5.0c | 398.0c | 155.0c | True | True |

## Worst Supported Slices

Only slices with at least `12` selected markets are shown.

| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask |
|---|---|---|---:|---:|---:|---:|---:|
| v21 | `hazard45_max780_else_score_min60` | ask=`ask<=80` | 56 | 37/19 | -557.0c | -9.9c | 73.0c |
| v21 | `hazard50_max420_else_score_min60` | ask=`ask<=80` | 59 | 40/19 | -486.0c | -8.2c | 73.0c |
| v21 | `hazard50_max540_else_score_min60` | ask=`ask<=80` | 59 | 40/19 | -486.0c | -8.2c | 73.0c |
| v21 | `hazard45_max660_else_score_min60` | ask=`ask<=80` | 59 | 40/19 | -486.0c | -8.2c | 73.0c |
| v21 | `hazard50_max660_else_score_min60` | ask=`ask<=80` | 59 | 40/19 | -486.0c | -8.2c | 73.0c |
| v21 | `hazard45_max420_else_score_min60` | ask=`ask<=80` | 59 | 40/19 | -486.0c | -8.2c | 73.0c |
| v21 | `hazard45_max540_else_score_min60` | ask=`ask<=80` | 59 | 40/19 | -486.0c | -8.2c | 73.0c |
| v21 | `hazard50_max780_else_score_min60` | ask=`ask<=80` | 59 | 40/19 | -486.0c | -8.2c | 73.0c |
| v21 | `hazard50_max660_else_logit_thresh55_edge15` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |
| v21 | `hazard45_max660_else_logit_thresh55_edge15` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |
| v21 | `hazard50_max780_else_logit_thresh55_edge15` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |
| v21 | `hazard45_max540_else_logit_thresh55_edge15` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |
| v21 | `hazard45_max780_else_logit_thresh55_edge15` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |
| v21 | `hazard45_max900_else_logit_thresh55_edge15` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |
| v21 | `hazard45_nomax_else_logit_thresh55_edge15` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |
| v21 | `hazard50_max540_else_logit_thresh55_edge15` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |
| v21 | `hazard50_max420_else_logit_thresh55_edge15` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |
| v21 | `hazard50_max900_else_logit_thresh55_edge15` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |

## Read

- No time-bounded hazard-primary row clears coverage, split, OOS, and block-stability gates.
- Do not promote or lock a scanned row without fresh strict live registration.
