# Logit Blend Threshold Robustness Audit

Generated UTC: `20260504_063802Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Replays thresholded logit book/RV/hazard selectors on current and v21 ledgers.
- This can reject or prioritize forward collection; promotion still requires strict registered live evidence.

## Split Summary

| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | coverage pass | all splits positive | OOS positive |
|---|---|---:|---:|---:|---:|---:|---|---|---|
| current | `logit55_edge10_control` | 1209.0c/5.90% | 75.35%/98.63% | 809.0c | 401.0c | -1.0c | True | False | False |
| v21 | `logit55_edge10_control` | 809.0c/5.19% | 75.93%/97.74% | 6.0c | 537.0c | 266.0c | True | True | True |
| current | `logit55_edge10_sec600` | 1117.0c/7.12% | 75.68%/76.03% | 917.0c | 156.0c | 44.0c | False | True | True |
| v21 | `logit55_edge10_sec600` | 492.0c/4.51% | 73.55%/70.14% | 12.0c | 396.0c | 84.0c | False | True | True |
| current | `logit55_edge15_locked` | 1053.0c/5.18% | 74.05%/98.97% | 506.0c | 481.0c | 66.0c | True | True | True |
| v21 | `logit55_edge15_locked` | 553.0c/3.60% | 72.94%/98.64% | 72.0c | 330.0c | 151.0c | True | True | True |
| current | `logit55_edge15_sec600` | 778.0c/4.57% | 73.25%/83.22% | 612.0c | 179.0c | -13.0c | True | False | False |
| v21 | `logit55_edge15_sec600` | 692.0c/5.45% | 73.63%/82.35% | 222.0c | 309.0c | 161.0c | False | True | True |
| current | `logit60_edge10_control` | 741.0c/3.47% | 78.09%/96.92% | 752.0c | 205.0c | -216.0c | True | False | False |
| v21 | `logit60_edge10_control` | 441.0c/2.71% | 78.40%/96.38% | -211.0c | 400.0c | 252.0c | True | False | True |
| current | `logit60_edge15_control` | 739.0c/3.44% | 77.35%/98.29% | 632.0c | 168.0c | -61.0c | True | False | False |
| v21 | `logit60_edge15_control` | 287.0c/1.75% | 76.96%/98.19% | -262.0c | 438.0c | 111.0c | True | False | True |
| current | `logit60_edge15_sec600` | 628.0c/4.14% | 76.70%/70.55% | 720.0c | -56.0c | -36.0c | False | False | False |
| v21 | `logit60_edge15_sec600` | 402.0c/3.79% | 76.92%/64.71% | -8.0c | 397.0c | 13.0c | False | False | True |
| current | `logit65_edge10_sec600` | 485.0c/4.18% | 81.21%/51.03% | 472.0c | -15.0c | 28.0c | False | False | False |
| v21 | `logit65_edge10_sec600` | 769.0c/9.58% | 85.44%/46.61% | 412.0c | 271.0c | 86.0c | False | True | True |
| current | `logit65_edge10_strict` | 457.0c/2.08% | 81.16%/94.52% | 60.0c | 173.0c | 224.0c | True | True | True |
| v21 | `logit65_edge10_strict` | 42.0c/0.25% | 80.09%/95.48% | -433.0c | 383.0c | 92.0c | True | False | True |

## Block Summary

| dataset | candidate | blocks | positive blocks | positive+coverage blocks | worst block |
|---|---|---:|---:|---:|---:|
| current | `logit55_edge10_control` | 15 | 80.00% | 80.00% | -259.0c |
| v21 | `logit55_edge10_control` | 11 | 63.64% | 63.64% | -320.0c |
| current | `logit55_edge10_sec600` | 15 | 73.33% | 40.00% | -178.0c |
| v21 | `logit55_edge10_sec600` | 11 | 72.73% | 18.18% | -313.0c |
| current | `logit55_edge15_locked` | 15 | 60.00% | 60.00% | -250.0c |
| v21 | `logit55_edge15_locked` | 11 | 63.64% | 63.64% | -284.0c |
| current | `logit55_edge15_sec600` | 15 | 66.67% | 53.33% | -214.0c |
| v21 | `logit55_edge15_sec600` | 11 | 72.73% | 54.55% | -233.0c |
| current | `logit60_edge10_control` | 15 | 66.67% | 66.67% | -323.0c |
| v21 | `logit60_edge10_control` | 11 | 63.64% | 63.64% | -349.0c |
| current | `logit60_edge15_control` | 15 | 53.33% | 53.33% | -182.0c |
| v21 | `logit60_edge15_control` | 11 | 63.64% | 63.64% | -314.0c |
| current | `logit60_edge15_sec600` | 15 | 53.33% | 13.33% | -192.0c |
| v21 | `logit60_edge15_sec600` | 11 | 72.73% | 9.09% | -255.0c |
| current | `logit65_edge10_sec600` | 15 | 66.67% | 0.00% | -226.0c |
| v21 | `logit65_edge10_sec600` | 11 | 81.82% | 0.00% | -280.0c |
| current | `logit65_edge10_strict` | 15 | 53.33% | 53.33% | -386.0c |
| v21 | `logit65_edge10_strict` | 11 | 54.55% | 54.55% | -381.0c |

## Worst Supported Slices

Only slices with at least `12` selected markets are shown.

| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask |
|---|---|---|---:|---:|---:|---:|---:|
| v21 | `logit65_edge10_strict` | time=`sec<=600` | 81 | 57/24 | -849.0c | -10.5c | 78.0c |
| v21 | `logit65_edge10_strict` | ask=`ask<=80` | 122 | 89/33 | -497.0c | -4.1c | 75.0c |
| v21 | `logit55_edge15_locked` | ask=`ask<=80` | 51 | 34/17 | -480.0c | -9.4c | 73.0c |
| v21 | `logit65_edge10_strict` | split=`train` | 126 | 96/30 | -433.0c | -3.4c | 76.0c |
| current | `logit55_edge15_locked` | hour=`8` | 12 | 5/7 | -349.0c | -29.1c | 69.0c |
| current | `logit55_edge10_control` | hour=`8` | 12 | 5/7 | -332.0c | -27.7c | 66.0c |
| v21 | `logit55_edge15_locked` | score=`p<=0.70` | 88 | 60/28 | -284.0c | -3.2c | 70.0c |
| current | `logit55_edge15_locked` | score=`p<=0.80` | 28 | 20/8 | -266.0c | -9.5c | 79.0c |
| v21 | `logit60_edge15_control` | split=`train` | 129 | 94/35 | -262.0c | -2.0c | 72.0c |
| current | `logit55_edge10_control` | edge=`edge<=0` | 50 | 32/18 | -262.0c | -5.2c | 66.0c |
| current | `logit60_edge15_control` | score=`p<=0.80` | 54 | 41/13 | -259.0c | -4.8c | 79.5c |
| current | `logit55_edge15_sec600` | hour=`3` | 12 | 6/6 | -255.0c | -21.2c | 68.0c |
| current | `logit65_edge10_strict` | time=`sec<=600` | 95 | 74/21 | -248.0c | -2.6c | 78.0c |
| current | `logit55_edge15_locked` | hour=`3` | 16 | 9/7 | -247.0c | -15.4c | 69.5c |
| current | `logit55_edge10_sec600` | edge=`edge<=0` | 33 | 20/13 | -234.0c | -7.1c | 66.0c |
| v21 | `logit65_edge10_strict` | score=`p<=0.70` | 76 | 54/22 | -219.0c | -2.9c | 72.0c |
| v21 | `logit60_edge15_control` | hour=`15` | 12 | 7/5 | -219.0c | -18.2c | 71.0c |
| current | `logit60_edge10_control` | split=`holdout` | 57 | 41/16 | -216.0c | -3.8c | 72.0c |

## History

| file | candidate | combined all | current all | current val | current holdout | v21 all | v21 train | v21 val | v21 holdout |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `logit_blend_threshold_frontier_20260504_062030Z.csv` | `logit55_edge15_locked` | 1606.0c | 1053.0c | 481.0c | 66.0c | 553.0c | 72.0c | 330.0c | 151.0c |
| `logit_blend_threshold_frontier_latest.csv` | `logit55_edge15_locked` | 1606.0c | 1053.0c | 481.0c | 66.0c | 553.0c | 72.0c | 330.0c | 151.0c |

## Read

- `logit55_edge10_control` coverage/all-splits/OOS/min positive+coverage block rate/robust: True/False/False/63.64%/False.
- `logit55_edge10_sec600` coverage/all-splits/OOS/min positive+coverage block rate/robust: False/True/True/18.18%/False.
- `logit55_edge15_locked` coverage/all-splits/OOS/min positive+coverage block rate/robust: True/True/True/60.00%/False.
- `logit55_edge15_sec600` coverage/all-splits/OOS/min positive+coverage block rate/robust: False/False/False/53.33%/False.
- `logit60_edge10_control` coverage/all-splits/OOS/min positive+coverage block rate/robust: True/False/False/63.64%/False.
- `logit60_edge15_control` coverage/all-splits/OOS/min positive+coverage block rate/robust: True/False/False/53.33%/False.
- `logit60_edge15_sec600` coverage/all-splits/OOS/min positive+coverage block rate/robust: False/False/False/9.09%/False.
- `logit65_edge10_sec600` coverage/all-splits/OOS/min positive+coverage block rate/robust: False/False/False/0.00%/False.
- `logit65_edge10_strict` coverage/all-splits/OOS/min positive+coverage block rate/robust: True/False/True/53.33%/False.
- Robust offline diagnostics still do not replace strict live pre-registration evidence.
