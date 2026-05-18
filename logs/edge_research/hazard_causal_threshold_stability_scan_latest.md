# Causal Hazard Threshold Stability Scan

Generated UTC: `20260504_080441Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Chooses the first eligible hazard-primary or fallback signal by timestamp per market.
- Tests whether raising the hazard floor improves low-score loss modes while preserving high market coverage.
- Any passing row is still only a forward-test candidate because this scan sees validation/holdout.

## Combined Read

| candidate | combined net | coverage | all splits | OOS | min positive+coverage blocks | robust |
|---|---:|---|---|---|---:|---|
| `hazard45_sec60_else_score_min60` | 1964.0c | True | True | True | 63.64% | False |
| `hazard50_sec60_else_score_min60` | 1854.0c | True | True | True | 63.64% | False |
| `hazard55_sec60_else_score_min60` | 1670.0c | True | False | True | 63.64% | False |
| `hazard60_sec60_else_score_min60` | 1670.0c | True | False | True | 63.64% | False |
| `hazard65_sec60_else_score_min60` | 1670.0c | True | False | True | 63.64% | False |
| `hazard55_sec60_else_logit_thresh55_edge15` | 1689.0c | True | True | True | 60.00% | False |
| `hazard60_sec60_else_logit_thresh55_edge15` | 1689.0c | True | True | True | 60.00% | False |
| `hazard65_sec60_else_logit_thresh55_edge15` | 1689.0c | True | True | True | 60.00% | False |
| `hazard50_sec60_else_logit_thresh55_edge15` | 1687.0c | True | True | True | 60.00% | False |
| `hazard45_sec60_else_logit_thresh55_edge15` | 1671.0c | True | True | True | 60.00% | False |
| `hazard55_sec600_else_logit_thresh55_edge15` | 1553.0c | False | True | True | 53.33% | False |
| `hazard60_sec600_else_logit_thresh55_edge15` | 1553.0c | False | True | True | 53.33% | False |
| `hazard65_sec600_else_logit_thresh55_edge15` | 1553.0c | False | True | True | 53.33% | False |
| `hazard50_sec600_else_logit_thresh55_edge15` | 1551.0c | False | True | True | 53.33% | False |
| `hazard45_sec600_else_logit_thresh55_edge15` | 1538.0c | False | False | False | 53.33% | False |
| `hazard45_sec600_else_score_min60` | 1946.0c | False | False | False | 45.45% | False |
| `hazard50_sec600_else_score_min60` | 1945.0c | False | False | False | 40.00% | False |
| `hazard55_sec600_else_score_min60` | 1735.0c | False | True | True | 40.00% | False |
| `hazard60_sec600_else_score_min60` | 1735.0c | False | True | True | 40.00% | False |
| `hazard65_sec600_else_score_min60` | 1735.0c | False | True | True | 40.00% | False |

## Split Summary

| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | coverage pass | all splits positive |
|---|---|---:|---:|---:|---:|---:|---|---|
| current | `hazard45_sec600_else_logit_thresh55_edge15` | 846.0c/4.90% | 73.58%/83.39% | 671.0c | 187.0c | -12.0c | False | False |
| v21 | `hazard45_sec600_else_logit_thresh55_edge15` | 692.0c/5.45% | 73.63%/82.35% | 222.0c | 309.0c | 161.0c | False | True |
| current | `hazard45_sec600_else_score_min60` | 1187.0c/6.98% | 75.52%/81.69% | 965.0c | 277.0c | -55.0c | False | False |
| v21 | `hazard45_sec600_else_score_min60` | 759.0c/6.10% | 74.16%/80.54% | 129.0c | 339.0c | 291.0c | False | True |
| current | `hazard45_sec60_else_logit_thresh55_edge15` | 1118.0c/5.43% | 74.32%/98.98% | 565.0c | 504.0c | 49.0c | True | True |
| v21 | `hazard45_sec60_else_logit_thresh55_edge15` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard45_sec60_else_score_min60` | 1268.0c/6.12% | 75.34%/98.98% | 775.0c | 473.0c | 20.0c | True | True |
| v21 | `hazard45_sec60_else_score_min60` | 696.0c/4.49% | 73.97%/99.10% | 62.0c | 419.0c | 215.0c | True | True |
| current | `hazard50_sec600_else_logit_thresh55_edge15` | 859.0c/4.98% | 73.58%/83.39% | 671.0c | 187.0c | 1.0c | False | True |
| v21 | `hazard50_sec600_else_logit_thresh55_edge15` | 692.0c/5.45% | 73.63%/82.35% | 222.0c | 309.0c | 161.0c | False | True |
| current | `hazard50_sec600_else_score_min60` | 1302.0c/7.66% | 76.25%/81.36% | 1088.0c | 269.0c | -55.0c | False | False |
| v21 | `hazard50_sec600_else_score_min60` | 643.0c/5.25% | 74.14%/78.73% | 123.0c | 301.0c | 219.0c | False | True |
| current | `hazard50_sec60_else_logit_thresh55_edge15` | 1134.0c/5.51% | 74.32%/98.98% | 565.0c | 507.0c | 62.0c | True | True |
| v21 | `hazard50_sec60_else_logit_thresh55_edge15` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard50_sec60_else_score_min60` | 1296.0c/6.23% | 75.68%/98.98% | 823.0c | 453.0c | 20.0c | True | True |
| v21 | `hazard50_sec60_else_score_min60` | 558.0c/3.57% | 73.97%/99.10% | 5.0c | 398.0c | 155.0c | True | True |
| current | `hazard55_sec600_else_logit_thresh55_edge15` | 861.0c/4.99% | 73.58%/83.39% | 671.0c | 187.0c | 3.0c | False | True |
| v21 | `hazard55_sec600_else_logit_thresh55_edge15` | 692.0c/5.45% | 73.63%/82.35% | 222.0c | 309.0c | 161.0c | False | True |
| current | `hazard55_sec600_else_score_min60` | 1207.0c/7.10% | 76.15%/81.02% | 916.0c | 269.0c | 22.0c | False | True |
| v21 | `hazard55_sec600_else_score_min60` | 528.0c/4.30% | 73.56%/78.73% | 8.0c | 301.0c | 219.0c | False | True |
| current | `hazard55_sec60_else_logit_thresh55_edge15` | 1136.0c/5.52% | 74.32%/98.98% | 565.0c | 507.0c | 64.0c | True | True |
| v21 | `hazard55_sec60_else_logit_thresh55_edge15` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard55_sec60_else_score_min60` | 1227.0c/5.88% | 75.68%/98.98% | 677.0c | 453.0c | 97.0c | True | True |
| v21 | `hazard55_sec60_else_score_min60` | 443.0c/2.83% | 73.52%/99.10% | -110.0c | 398.0c | 155.0c | True | False |
| current | `hazard60_sec600_else_logit_thresh55_edge15` | 861.0c/4.99% | 73.58%/83.39% | 671.0c | 187.0c | 3.0c | False | True |
| v21 | `hazard60_sec600_else_logit_thresh55_edge15` | 692.0c/5.45% | 73.63%/82.35% | 222.0c | 309.0c | 161.0c | False | True |
| current | `hazard60_sec600_else_score_min60` | 1207.0c/7.10% | 76.15%/81.02% | 916.0c | 269.0c | 22.0c | False | True |
| v21 | `hazard60_sec600_else_score_min60` | 528.0c/4.30% | 73.56%/78.73% | 8.0c | 301.0c | 219.0c | False | True |
| current | `hazard60_sec60_else_logit_thresh55_edge15` | 1136.0c/5.52% | 74.32%/98.98% | 565.0c | 507.0c | 64.0c | True | True |
| v21 | `hazard60_sec60_else_logit_thresh55_edge15` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard60_sec60_else_score_min60` | 1227.0c/5.88% | 75.68%/98.98% | 677.0c | 453.0c | 97.0c | True | True |
| v21 | `hazard60_sec60_else_score_min60` | 443.0c/2.83% | 73.52%/99.10% | -110.0c | 398.0c | 155.0c | True | False |
| current | `hazard65_sec600_else_logit_thresh55_edge15` | 861.0c/4.99% | 73.58%/83.39% | 671.0c | 187.0c | 3.0c | False | True |
| v21 | `hazard65_sec600_else_logit_thresh55_edge15` | 692.0c/5.45% | 73.63%/82.35% | 222.0c | 309.0c | 161.0c | False | True |
| current | `hazard65_sec600_else_score_min60` | 1207.0c/7.10% | 76.15%/81.02% | 916.0c | 269.0c | 22.0c | False | True |
| v21 | `hazard65_sec600_else_score_min60` | 528.0c/4.30% | 73.56%/78.73% | 8.0c | 301.0c | 219.0c | False | True |
| current | `hazard65_sec60_else_logit_thresh55_edge15` | 1136.0c/5.52% | 74.32%/98.98% | 565.0c | 507.0c | 64.0c | True | True |
| v21 | `hazard65_sec60_else_logit_thresh55_edge15` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard65_sec60_else_score_min60` | 1227.0c/5.88% | 75.68%/98.98% | 677.0c | 453.0c | 97.0c | True | True |
| v21 | `hazard65_sec60_else_score_min60` | 443.0c/2.83% | 73.52%/99.10% | -110.0c | 398.0c | 155.0c | True | False |

## Worst Supported Slices

Only slices with at least `12` selected markets are shown.

| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask |
|---|---|---|---:|---:|---:|---:|---:|
| v21 | `hazard55_sec60_else_score_min60` | ask=`ask<=80` | 59 | 40/19 | -486.0c | -8.2c | 73.0c |
| v21 | `hazard60_sec60_else_score_min60` | ask=`ask<=80` | 59 | 40/19 | -486.0c | -8.2c | 73.0c |
| v21 | `hazard65_sec60_else_score_min60` | ask=`ask<=80` | 59 | 40/19 | -486.0c | -8.2c | 73.0c |
| v21 | `hazard60_sec60_else_logit_thresh55_edge15` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |
| v21 | `hazard55_sec60_else_logit_thresh55_edge15` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |
| v21 | `hazard50_sec60_else_logit_thresh55_edge15` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |
| v21 | `hazard45_sec60_else_logit_thresh55_edge15` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |
| v21 | `hazard65_sec60_else_logit_thresh55_edge15` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |
| v21 | `hazard50_sec60_else_score_min60` | ask=`ask<=80` | 58 | 40/18 | -412.0c | -7.1c | 73.5c |
| v21 | `hazard45_sec60_else_score_min60` | ask=`ask<=80` | 54 | 37/17 | -408.0c | -7.6c | 73.5c |
| current | `hazard55_sec60_else_logit_thresh55_edge15` | hour=`8` | 12 | 5/7 | -349.0c | -29.1c | 69.0c |
| current | `hazard50_sec60_else_logit_thresh55_edge15` | hour=`8` | 12 | 5/7 | -349.0c | -29.1c | 69.0c |
| current | `hazard60_sec60_else_logit_thresh55_edge15` | hour=`8` | 12 | 5/7 | -349.0c | -29.1c | 69.0c |
| current | `hazard65_sec60_else_logit_thresh55_edge15` | hour=`8` | 12 | 5/7 | -349.0c | -29.1c | 69.0c |
| current | `hazard65_sec60_else_score_min60` | hour=`8` | 12 | 5/7 | -348.0c | -29.0c | 69.0c |
| current | `hazard60_sec60_else_score_min60` | hour=`8` | 12 | 5/7 | -348.0c | -29.0c | 69.0c |
| current | `hazard50_sec60_else_score_min60` | hour=`8` | 12 | 5/7 | -348.0c | -29.0c | 69.0c |
| current | `hazard55_sec60_else_score_min60` | hour=`8` | 12 | 5/7 | -348.0c | -29.0c | 69.0c |

## Read

- No causal hazard-threshold row clears the combined coverage, split, OOS, and block-stability gate.
- Do not promote or lock a scanned row without fresh strict live registration.
