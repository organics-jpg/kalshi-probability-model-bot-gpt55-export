# Hazard Primary Threshold Stability Scan

Generated UTC: `20260504_065238Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Tests whether raising the hazard-primary confidence floor improves block stability while preserving market coverage through a fallback prior.
- Any passing row is still only a forward-test candidate because this scan sees validation/holdout.

## Combined Read

| candidate | combined net | coverage | all splits | OOS | min positive+coverage blocks | robust |
|---|---:|---|---|---|---:|---|
| `hazard45_sec60_else_logit_thresh55_edge15` | 2035.0c | True | True | True | 63.64% | False |
| `hazard45_sec60_else_score_min60` | 1912.0c | True | True | True | 63.64% | False |
| `hazard50_sec60_else_logit_thresh55_edge15` | 1428.0c | True | False | True | 54.55% | False |
| `hazard50_sec60_else_score_min60` | 1160.0c | True | False | True | 54.55% | False |
| `hazard55_sec60_else_logit_thresh55_edge15` | 1005.0c | True | False | True | 54.55% | False |
| `hazard55_sec60_else_score_min60` | 556.0c | True | False | True | 54.55% | False |
| `hazard45_sec600_else_logit_thresh55_edge15` | 1417.0c | False | False | False | 53.33% | False |
| `hazard50_sec600_else_logit_thresh55_edge15` | 959.0c | False | False | False | 53.33% | False |
| `hazard65_sec60_else_score_min60` | 632.0c | True | False | True | 53.33% | False |
| `hazard65_sec60_else_logit_thresh55_edge15` | 578.0c | True | False | True | 53.33% | False |
| `hazard65_sec600_else_logit_thresh55_edge15` | 814.0c | False | False | False | 46.67% | False |
| `hazard55_sec600_else_logit_thresh55_edge15` | 650.0c | False | False | False | 46.67% | False |
| `hazard60_sec600_else_logit_thresh55_edge15` | 411.0c | False | False | False | 46.67% | False |
| `hazard45_sec600_else_score_min60` | 1712.0c | False | False | False | 45.45% | False |
| `hazard60_sec60_else_logit_thresh55_edge15` | -237.0c | True | False | True | 45.45% | False |
| `hazard60_sec60_else_score_min60` | -263.0c | True | False | True | 45.45% | False |
| `hazard50_sec600_else_score_min60` | 1126.0c | False | False | False | 33.33% | False |
| `hazard55_sec600_else_score_min60` | 587.0c | False | False | False | 33.33% | False |
| `hazard65_sec600_else_score_min60` | 961.0c | False | False | False | 26.67% | False |
| `hazard60_sec600_else_score_min60` | 534.0c | False | False | False | 26.67% | False |

## Split Summary

| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | coverage pass | all splits positive |
|---|---|---:|---:|---:|---:|---:|---|---|
| current | `hazard45_sec600_else_logit_thresh55_edge15` | 483.0c/2.76% | 73.17%/83.39% | 430.0c | 120.0c | -67.0c | False | False |
| v21 | `hazard45_sec600_else_logit_thresh55_edge15` | 934.0c/7.32% | 75.27%/82.35% | 391.0c | 284.0c | 259.0c | False | True |
| current | `hazard45_sec600_else_score_min60` | 902.0c/5.24% | 75.10%/81.69% | 758.0c | 224.0c | -80.0c | False | False |
| v21 | `hazard45_sec600_else_score_min60` | 810.0c/6.49% | 74.72%/80.54% | 194.0c | 314.0c | 302.0c | False | True |
| current | `hazard45_sec60_else_logit_thresh55_edge15` | 1113.0c/5.30% | 75.68%/98.98% | 630.0c | 408.0c | 75.0c | True | True |
| v21 | `hazard45_sec60_else_logit_thresh55_edge15` | 922.0c/5.92% | 75.69%/98.64% | 174.0c | 450.0c | 298.0c | True | True |
| current | `hazard45_sec60_else_score_min60` | 1104.0c/5.26% | 75.68%/98.98% | 618.0c | 408.0c | 78.0c | True | True |
| v21 | `hazard45_sec60_else_score_min60` | 808.0c/5.15% | 75.34%/99.10% | 83.0c | 448.0c | 277.0c | True | True |
| current | `hazard50_sec600_else_logit_thresh55_edge15` | 449.0c/2.52% | 74.39%/83.39% | 535.0c | 19.0c | -105.0c | False | False |
| v21 | `hazard50_sec600_else_logit_thresh55_edge15` | 510.0c/3.90% | 74.73%/82.35% | 106.0c | 210.0c | 194.0c | False | True |
| current | `hazard50_sec600_else_score_min60` | 797.0c/4.55% | 76.25%/81.36% | 795.0c | 125.0c | -123.0c | False | False |
| v21 | `hazard50_sec600_else_score_min60` | 329.0c/2.62% | 74.14%/78.73% | -67.0c | 202.0c | 194.0c | False | False |
| current | `hazard50_sec60_else_logit_thresh55_edge15` | 1245.0c/5.75% | 78.42%/98.98% | 892.0c | 259.0c | 94.0c | True | True |
| v21 | `hazard50_sec60_else_logit_thresh55_edge15` | 183.0c/1.13% | 75.23%/98.64% | -137.0c | 225.0c | 95.0c | True | False |
| current | `hazard50_sec60_else_score_min60` | 1130.0c/5.21% | 78.08%/98.98% | 779.0c | 259.0c | 92.0c | True | True |
| v21 | `hazard50_sec60_else_score_min60` | 30.0c/0.18% | 74.89%/99.10% | -238.0c | 223.0c | 45.0c | True | False |
| current | `hazard55_sec600_else_logit_thresh55_edge15` | 194.0c/1.08% | 73.98%/83.39% | 330.0c | -130.0c | -6.0c | False | False |
| v21 | `hazard55_sec600_else_logit_thresh55_edge15` | 456.0c/3.47% | 74.73%/82.35% | 58.0c | 205.0c | 193.0c | False | True |
| current | `hazard55_sec600_else_score_min60` | 441.0c/2.50% | 75.73%/81.02% | 502.0c | -32.0c | -29.0c | False | False |
| v21 | `hazard55_sec600_else_score_min60` | 146.0c/1.15% | 73.56%/78.73% | -249.0c | 202.0c | 193.0c | False | False |
| current | `hazard55_sec60_else_logit_thresh55_edge15` | 1046.0c/4.74% | 79.11%/98.98% | 306.0c | 212.0c | 528.0c | True | True |
| v21 | `hazard55_sec60_else_logit_thresh55_edge15` | -41.0c/-0.25% | 75.23%/98.64% | -409.0c | 293.0c | 75.0c | True | False |
| current | `hazard55_sec60_else_score_min60` | 889.0c/4.02% | 78.77%/98.98% | 161.0c | 214.0c | 514.0c | True | True |
| v21 | `hazard55_sec60_else_score_min60` | -333.0c/-2.00% | 74.43%/99.10% | -644.0c | 296.0c | 15.0c | True | False |
| current | `hazard60_sec600_else_logit_thresh55_edge15` | 112.0c/0.63% | 73.17%/83.39% | 372.0c | -79.0c | -181.0c | False | False |
| v21 | `hazard60_sec600_else_logit_thresh55_edge15` | 299.0c/2.28% | 73.63%/82.35% | -122.0c | 224.0c | 197.0c | False | False |
| current | `hazard60_sec600_else_score_min60` | 438.0c/2.49% | 75.31%/81.02% | 543.0c | 25.0c | -130.0c | False | False |
| v21 | `hazard60_sec600_else_score_min60` | 96.0c/0.76% | 72.99%/78.73% | -322.0c | 221.0c | 197.0c | False | False |
| current | `hazard60_sec60_else_logit_thresh55_edge15` | 556.0c/2.53% | 77.05%/98.98% | 214.0c | 182.0c | 160.0c | True | True |
| v21 | `hazard60_sec60_else_logit_thresh55_edge15` | -793.0c/-4.84% | 71.56%/98.64% | -905.0c | 13.0c | 99.0c | True | False |
| current | `hazard60_sec60_else_score_min60` | 634.0c/2.87% | 77.74%/98.98% | 235.0c | 182.0c | 217.0c | True | True |
| v21 | `hazard60_sec60_else_score_min60` | -897.0c/-5.40% | 71.69%/99.10% | -1041.0c | 107.0c | 37.0c | True | False |
| current | `hazard65_sec600_else_logit_thresh55_edge15` | 299.0c/1.69% | 73.17%/83.39% | 362.0c | 74.0c | -137.0c | False | False |
| v21 | `hazard65_sec600_else_logit_thresh55_edge15` | 515.0c/3.97% | 74.18%/82.35% | 58.0c | 261.0c | 196.0c | False | True |
| current | `hazard65_sec600_else_score_min60` | 662.0c/3.80% | 75.73%/81.02% | 611.0c | 169.0c | -118.0c | False | False |
| v21 | `hazard65_sec600_else_score_min60` | 299.0c/2.39% | 73.56%/78.73% | -150.0c | 253.0c | 196.0c | False | False |
| current | `hazard65_sec60_else_logit_thresh55_edge15` | 519.0c/2.39% | 76.03%/98.98% | -229.0c | 443.0c | 305.0c | True | False |
| v21 | `hazard65_sec60_else_logit_thresh55_edge15` | 59.0c/0.37% | 73.85%/98.64% | -363.0c | 280.0c | 142.0c | True | False |
| current | `hazard65_sec60_else_score_min60` | 708.0c/3.23% | 77.40%/98.98% | -75.0c | 437.0c | 346.0c | True | False |
| v21 | `hazard65_sec60_else_score_min60` | -76.0c/-0.47% | 73.97%/99.10% | -530.0c | 374.0c | 80.0c | True | False |

## Worst Supported Slices

Only slices with at least `12` selected markets are shown.

| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask |
|---|---|---|---:|---:|---:|---:|---:|
| v21 | `hazard60_sec60_else_logit_thresh55_edge15` | time=`sec<=600` | 70 | 43/27 | -1143.0c | -16.3c | 77.0c |
| v21 | `hazard55_sec60_else_logit_thresh55_edge15` | time=`sec<=600` | 70 | 43/27 | -1082.0c | -15.5c | 75.0c |
| v21 | `hazard60_sec60_else_score_min60` | split=`train` | 131 | 89/42 | -1041.0c | -7.9c | 75.0c |
| v21 | `hazard60_sec60_else_score_min60` | time=`sec<=600` | 75 | 48/27 | -1039.0c | -13.9c | 77.0c |
| v21 | `hazard55_sec60_else_score_min60` | time=`sec<=600` | 73 | 46/27 | -1025.0c | -14.0c | 75.0c |
| v21 | `hazard60_sec60_else_logit_thresh55_edge15` | split=`train` | 130 | 89/41 | -905.0c | -7.0c | 75.0c |
| v21 | `hazard60_sec60_else_score_min60` | side=`yes` | 118 | 82/36 | -736.0c | -6.2c | 75.0c |
| v21 | `hazard60_sec60_else_score_min60` | ask=`ask<=80` | 138 | 101/37 | -708.0c | -5.1c | 77.0c |
| v21 | `hazard60_sec60_else_logit_thresh55_edge15` | ask=`ask<=80` | 134 | 98/36 | -701.0c | -5.2c | 77.0c |
| v21 | `hazard55_sec60_else_score_min60` | split=`train` | 131 | 93/38 | -644.0c | -4.9c | 74.0c |
| v21 | `hazard60_sec60_else_logit_thresh55_edge15` | side=`yes` | 116 | 81/35 | -609.0c | -5.2c | 75.0c |
| v21 | `hazard60_sec60_else_score_min60` | selector=`hazard_primary_0.6` | 121 | 89/32 | -597.0c | -4.9c | 77.0c |
| v21 | `hazard60_sec60_else_logit_thresh55_edge15` | selector=`hazard_primary_0.6` | 121 | 89/32 | -597.0c | -4.9c | 77.0c |
| v21 | `hazard65_sec60_else_logit_thresh55_edge15` | time=`sec<=600` | 50 | 33/17 | -553.0c | -11.1c | 76.5c |
| v21 | `hazard65_sec60_else_score_min60` | split=`train` | 131 | 92/39 | -530.0c | -4.0c | 72.0c |
| current | `hazard45_sec600_else_logit_thresh55_edge15` | selector=`fallback_logit_thresh55_edge15` | 23 | 11/12 | -514.0c | -22.3c | 67.0c |

## Read

- No hazard-primary threshold row clears the combined coverage, split, OOS, and block-stability gate.
- Do not promote or lock a scanned row without fresh strict live registration.
