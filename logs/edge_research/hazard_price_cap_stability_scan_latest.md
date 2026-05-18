# Hazard Price-Cap Stability Scan

Generated UTC: `20260504_081957Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Tests stricter hazard and fallback ask caps under timestamp-causal arbitration.
- Any passing row must still be forward-locked before use.

## Combined Read

| candidate | combined net | coverage | all splits | OOS | min positive+coverage blocks | robust |
|---|---:|---|---|---|---:|---|
| `hazard_ask65_else_score60_ask80` | 2029.0c | True | True | True | 63.64% | False |
| `hazard_ask70_else_score60_ask80` | 2029.0c | True | True | True | 63.64% | False |
| `hazard_ask75_else_score60_ask80` | 2029.0c | True | True | True | 63.64% | False |
| `hazard_ask80_else_score60_ask70` | 2029.0c | True | True | True | 63.64% | False |
| `hazard_ask80_else_score60_ask75` | 2029.0c | True | True | True | 63.64% | False |
| `hazard_ask80_else_score60_ask80` | 2029.0c | True | True | True | 63.64% | False |
| `hazard_ask65_else_score60_ask95` | 1964.0c | True | True | True | 63.64% | False |
| `hazard_ask70_else_score60_ask95` | 1964.0c | True | True | True | 63.64% | False |
| `hazard_ask75_else_score60_ask95` | 1964.0c | True | True | True | 63.64% | False |
| `hazard_ask80_else_score60_ask95` | 1964.0c | True | True | True | 63.64% | False |
| `hazard_ask75_else_logit55_edge15_ask95` | 1690.0c | True | True | True | 60.00% | False |
| `hazard_ask65_else_logit55_edge15_ask95` | 1689.0c | True | True | True | 60.00% | False |
| `hazard_ask70_else_logit55_edge15_ask95` | 1689.0c | True | True | True | 60.00% | False |
| `hazard_ask75_else_logit55_edge15_ask80` | 1681.0c | True | True | True | 60.00% | False |
| `hazard_ask65_else_logit55_edge15_ask80` | 1680.0c | True | True | True | 60.00% | False |
| `hazard_ask70_else_logit55_edge15_ask80` | 1680.0c | True | True | True | 60.00% | False |
| `hazard_ask80_else_logit55_edge15_ask95` | 1671.0c | True | True | True | 60.00% | False |
| `hazard_ask80_else_logit55_edge15_ask75` | 1662.0c | True | True | True | 60.00% | False |
| `hazard_ask80_else_logit55_edge15_ask80` | 1662.0c | True | True | True | 60.00% | False |
| `hazard_ask80_else_logit55_edge15_ask70` | 1654.0c | True | True | True | 60.00% | False |
| `hazard_ask65_else_logit55_edge15_ask70` | 1970.0c | True | True | True | 54.55% | False |
| `hazard_ask70_else_logit55_edge15_ask70` | 1970.0c | True | True | True | 54.55% | False |
| `hazard_ask65_else_logit55_edge15_ask75` | 1711.0c | True | True | True | 53.33% | False |
| `hazard_ask70_else_logit55_edge15_ask75` | 1711.0c | True | True | True | 53.33% | False |
| `hazard_ask75_else_logit55_edge15_ask75` | 1673.0c | True | True | True | 53.33% | False |
| `hazard_ask75_else_logit55_edge15_ask70` | 1669.0c | True | True | True | 53.33% | False |
| `hazard_ask65_else_score60_ask70` | 2246.0c | False | True | True | 45.45% | False |
| `hazard_ask70_else_score60_ask70` | 2246.0c | False | True | True | 45.45% | False |
| `hazard_ask65_else_score60_ask75` | 2104.0c | True | True | True | 45.45% | False |
| `hazard_ask70_else_score60_ask75` | 2104.0c | True | True | True | 45.45% | False |
| `hazard_ask75_else_score60_ask70` | 2104.0c | True | True | True | 45.45% | False |
| `hazard_ask75_else_score60_ask75` | 2104.0c | True | True | True | 45.45% | False |

## Split Summary

| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | coverage pass | all splits positive |
|---|---|---:|---:|---:|---:|---:|---|---|
| current | `hazard_ask65_else_logit55_edge15_ask70` | 1147.0c/6.61% | 71.71%/87.46% | 606.0c | 459.0c | 82.0c | True | True |
| v21 | `hazard_ask65_else_logit55_edge15_ask70` | 823.0c/6.76% | 71.82%/81.90% | 225.0c | 218.0c | 380.0c | True | True |
| current | `hazard_ask65_else_logit55_edge15_ask75` | 1006.0c/5.32% | 72.36%/93.22% | 536.0c | 354.0c | 116.0c | True | True |
| v21 | `hazard_ask65_else_logit55_edge15_ask75` | 705.0c/5.11% | 72.14%/90.95% | 102.0c | 302.0c | 301.0c | True | True |
| current | `hazard_ask65_else_logit55_edge15_ask80` | 1137.0c/5.67% | 73.87%/97.29% | 554.0c | 505.0c | 78.0c | True | True |
| v21 | `hazard_ask65_else_logit55_edge15_ask80` | 543.0c/3.70% | 72.04%/95.48% | 82.0c | 339.0c | 122.0c | True | True |
| current | `hazard_ask65_else_logit55_edge15_ask95` | 1136.0c/5.52% | 74.32%/98.98% | 565.0c | 507.0c | 64.0c | True | True |
| v21 | `hazard_ask65_else_logit55_edge15_ask95` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard_ask65_else_score60_ask70` | 1397.0c/8.22% | 72.73%/85.76% | 915.0c | 403.0c | 79.0c | True | True |
| v21 | `hazard_ask65_else_score60_ask70` | 849.0c/7.22% | 72.00%/79.19% | 225.0c | 203.0c | 421.0c | False | True |
| current | `hazard_ask65_else_score60_ask75` | 1166.0c/6.16% | 73.36%/92.88% | 736.0c | 331.0c | 99.0c | True | True |
| v21 | `hazard_ask65_else_score60_ask75` | 938.0c/6.82% | 73.50%/90.50% | 183.0c | 389.0c | 366.0c | True | True |
| current | `hazard_ask65_else_score60_ask80` | 1261.0c/6.26% | 74.83%/96.95% | 753.0c | 478.0c | 30.0c | True | True |
| v21 | `hazard_ask65_else_score60_ask80` | 768.0c/5.25% | 73.33%/95.02% | 163.0c | 428.0c | 177.0c | True | True |
| current | `hazard_ask65_else_score60_ask95` | 1268.0c/6.12% | 75.34%/98.98% | 775.0c | 473.0c | 20.0c | True | True |
| v21 | `hazard_ask65_else_score60_ask95` | 696.0c/4.49% | 73.97%/99.10% | 62.0c | 419.0c | 215.0c | True | True |
| current | `hazard_ask70_else_logit55_edge15_ask70` | 1147.0c/6.61% | 71.71%/87.46% | 606.0c | 459.0c | 82.0c | True | True |
| v21 | `hazard_ask70_else_logit55_edge15_ask70` | 823.0c/6.76% | 71.82%/81.90% | 225.0c | 218.0c | 380.0c | True | True |
| current | `hazard_ask70_else_logit55_edge15_ask75` | 1006.0c/5.32% | 72.36%/93.22% | 536.0c | 354.0c | 116.0c | True | True |
| v21 | `hazard_ask70_else_logit55_edge15_ask75` | 705.0c/5.11% | 72.14%/90.95% | 102.0c | 302.0c | 301.0c | True | True |
| current | `hazard_ask70_else_logit55_edge15_ask80` | 1137.0c/5.67% | 73.87%/97.29% | 554.0c | 505.0c | 78.0c | True | True |
| v21 | `hazard_ask70_else_logit55_edge15_ask80` | 543.0c/3.70% | 72.04%/95.48% | 82.0c | 339.0c | 122.0c | True | True |
| current | `hazard_ask70_else_logit55_edge15_ask95` | 1136.0c/5.52% | 74.32%/98.98% | 565.0c | 507.0c | 64.0c | True | True |
| v21 | `hazard_ask70_else_logit55_edge15_ask95` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard_ask70_else_score60_ask70` | 1397.0c/8.22% | 72.73%/85.76% | 915.0c | 403.0c | 79.0c | True | True |
| v21 | `hazard_ask70_else_score60_ask70` | 849.0c/7.22% | 72.00%/79.19% | 225.0c | 203.0c | 421.0c | False | True |
| current | `hazard_ask70_else_score60_ask75` | 1166.0c/6.16% | 73.36%/92.88% | 736.0c | 331.0c | 99.0c | True | True |
| v21 | `hazard_ask70_else_score60_ask75` | 938.0c/6.82% | 73.50%/90.50% | 183.0c | 389.0c | 366.0c | True | True |
| current | `hazard_ask70_else_score60_ask80` | 1261.0c/6.26% | 74.83%/96.95% | 753.0c | 478.0c | 30.0c | True | True |
| v21 | `hazard_ask70_else_score60_ask80` | 768.0c/5.25% | 73.33%/95.02% | 163.0c | 428.0c | 177.0c | True | True |
| current | `hazard_ask70_else_score60_ask95` | 1268.0c/6.12% | 75.34%/98.98% | 775.0c | 473.0c | 20.0c | True | True |
| v21 | `hazard_ask70_else_score60_ask95` | 696.0c/4.49% | 73.97%/99.10% | 62.0c | 419.0c | 215.0c | True | True |
| current | `hazard_ask75_else_logit55_edge15_ask70` | 964.0c/5.09% | 72.36%/93.22% | 502.0c | 347.0c | 115.0c | True | True |
| v21 | `hazard_ask75_else_logit55_edge15_ask70` | 705.0c/5.11% | 72.14%/90.95% | 102.0c | 302.0c | 301.0c | True | True |
| current | `hazard_ask75_else_logit55_edge15_ask75` | 968.0c/5.11% | 72.36%/93.22% | 502.0c | 351.0c | 115.0c | True | True |
| v21 | `hazard_ask75_else_logit55_edge15_ask75` | 705.0c/5.11% | 72.14%/90.95% | 102.0c | 302.0c | 301.0c | True | True |
| current | `hazard_ask75_else_logit55_edge15_ask80` | 1138.0c/5.67% | 73.87%/97.29% | 559.0c | 502.0c | 77.0c | True | True |
| v21 | `hazard_ask75_else_logit55_edge15_ask80` | 543.0c/3.70% | 72.04%/95.48% | 82.0c | 339.0c | 122.0c | True | True |
| current | `hazard_ask75_else_logit55_edge15_ask95` | 1137.0c/5.53% | 74.32%/98.98% | 570.0c | 504.0c | 63.0c | True | True |
| v21 | `hazard_ask75_else_logit55_edge15_ask95` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard_ask75_else_score60_ask70` | 1166.0c/6.16% | 73.36%/92.88% | 736.0c | 331.0c | 99.0c | True | True |
| v21 | `hazard_ask75_else_score60_ask70` | 938.0c/6.82% | 73.50%/90.50% | 183.0c | 389.0c | 366.0c | True | True |
| current | `hazard_ask75_else_score60_ask75` | 1166.0c/6.16% | 73.36%/92.88% | 736.0c | 331.0c | 99.0c | True | True |
| v21 | `hazard_ask75_else_score60_ask75` | 938.0c/6.82% | 73.50%/90.50% | 183.0c | 389.0c | 366.0c | True | True |
| current | `hazard_ask75_else_score60_ask80` | 1261.0c/6.26% | 74.83%/96.95% | 753.0c | 478.0c | 30.0c | True | True |
| v21 | `hazard_ask75_else_score60_ask80` | 768.0c/5.25% | 73.33%/95.02% | 163.0c | 428.0c | 177.0c | True | True |
| current | `hazard_ask75_else_score60_ask95` | 1268.0c/6.12% | 75.34%/98.98% | 775.0c | 473.0c | 20.0c | True | True |
| v21 | `hazard_ask75_else_score60_ask95` | 696.0c/4.49% | 73.97%/99.10% | 62.0c | 419.0c | 215.0c | True | True |
| current | `hazard_ask80_else_logit55_edge15_ask70` | 1111.0c/5.53% | 73.87%/97.29% | 554.0c | 494.0c | 63.0c | True | True |
| v21 | `hazard_ask80_else_logit55_edge15_ask70` | 543.0c/3.70% | 72.04%/95.48% | 82.0c | 339.0c | 122.0c | True | True |
| current | `hazard_ask80_else_logit55_edge15_ask75` | 1119.0c/5.57% | 73.87%/97.29% | 554.0c | 502.0c | 63.0c | True | True |
| v21 | `hazard_ask80_else_logit55_edge15_ask75` | 543.0c/3.70% | 72.04%/95.48% | 82.0c | 339.0c | 122.0c | True | True |
| current | `hazard_ask80_else_logit55_edge15_ask80` | 1119.0c/5.57% | 73.87%/97.29% | 554.0c | 502.0c | 63.0c | True | True |
| v21 | `hazard_ask80_else_logit55_edge15_ask80` | 543.0c/3.70% | 72.04%/95.48% | 82.0c | 339.0c | 122.0c | True | True |
| current | `hazard_ask80_else_logit55_edge15_ask95` | 1118.0c/5.43% | 74.32%/98.98% | 565.0c | 504.0c | 49.0c | True | True |
| v21 | `hazard_ask80_else_logit55_edge15_ask95` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True |
| current | `hazard_ask80_else_score60_ask70` | 1261.0c/6.26% | 74.83%/96.95% | 753.0c | 478.0c | 30.0c | True | True |
| v21 | `hazard_ask80_else_score60_ask70` | 768.0c/5.25% | 73.33%/95.02% | 163.0c | 428.0c | 177.0c | True | True |
| current | `hazard_ask80_else_score60_ask75` | 1261.0c/6.26% | 74.83%/96.95% | 753.0c | 478.0c | 30.0c | True | True |
| v21 | `hazard_ask80_else_score60_ask75` | 768.0c/5.25% | 73.33%/95.02% | 163.0c | 428.0c | 177.0c | True | True |
| current | `hazard_ask80_else_score60_ask80` | 1261.0c/6.26% | 74.83%/96.95% | 753.0c | 478.0c | 30.0c | True | True |
| v21 | `hazard_ask80_else_score60_ask80` | 768.0c/5.25% | 73.33%/95.02% | 163.0c | 428.0c | 177.0c | True | True |
| current | `hazard_ask80_else_score60_ask95` | 1268.0c/6.12% | 75.34%/98.98% | 775.0c | 473.0c | 20.0c | True | True |
| v21 | `hazard_ask80_else_score60_ask95` | 696.0c/4.49% | 73.97%/99.10% | 62.0c | 419.0c | 215.0c | True | True |

## Worst Supported Slices

Only slices with at least `12` selected markets are shown.

| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask |
|---|---|---|---:|---:|---:|---:|---:|
| v21 | `hazard_ask80_else_logit55_edge15_ask95` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |
| v21 | `hazard_ask75_else_logit55_edge15_ask95` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |
| v21 | `hazard_ask70_else_logit55_edge15_ask95` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |
| v21 | `hazard_ask65_else_logit55_edge15_ask95` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |
| v21 | `hazard_ask70_else_score60_ask95` | ask=`ask<=80` | 54 | 37/17 | -408.0c | -7.6c | 73.5c |
| v21 | `hazard_ask65_else_score60_ask95` | ask=`ask<=80` | 54 | 37/17 | -408.0c | -7.6c | 73.5c |
| v21 | `hazard_ask75_else_score60_ask95` | ask=`ask<=80` | 54 | 37/17 | -408.0c | -7.6c | 73.5c |
| v21 | `hazard_ask80_else_score60_ask95` | ask=`ask<=80` | 54 | 37/17 | -408.0c | -7.6c | 73.5c |
| v21 | `hazard_ask70_else_logit55_edge15_ask80` | ask=`ask<=80` | 57 | 40/17 | -349.0c | -6.1c | 74.0c |
| v21 | `hazard_ask75_else_logit55_edge15_ask80` | ask=`ask<=80` | 57 | 40/17 | -349.0c | -6.1c | 74.0c |
| v21 | `hazard_ask80_else_logit55_edge15_ask75` | ask=`ask<=80` | 57 | 40/17 | -349.0c | -6.1c | 74.0c |
| v21 | `hazard_ask65_else_logit55_edge15_ask80` | ask=`ask<=80` | 57 | 40/17 | -349.0c | -6.1c | 74.0c |
| v21 | `hazard_ask80_else_logit55_edge15_ask80` | ask=`ask<=80` | 57 | 40/17 | -349.0c | -6.1c | 74.0c |
| current | `hazard_ask70_else_logit55_edge15_ask95` | hour=`8` | 12 | 5/7 | -349.0c | -29.1c | 69.0c |
| current | `hazard_ask65_else_logit55_edge15_ask80` | hour=`8` | 12 | 5/7 | -349.0c | -29.1c | 69.0c |
| v21 | `hazard_ask80_else_logit55_edge15_ask70` | ask=`ask<=80` | 57 | 40/17 | -349.0c | -6.1c | 74.0c |
| current | `hazard_ask70_else_logit55_edge15_ask80` | hour=`8` | 12 | 5/7 | -349.0c | -29.1c | 69.0c |
| current | `hazard_ask65_else_logit55_edge15_ask95` | hour=`8` | 12 | 5/7 | -349.0c | -29.1c | 69.0c |

## Read

- No hazard/fallback price-cap row clears coverage, split, OOS, and block-stability gates.
- Do not promote or lock a scanned row without fresh strict live registration.
