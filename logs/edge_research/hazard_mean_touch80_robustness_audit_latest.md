# Hazard Mean Touch80 Robustness Audit

Generated UTC: `20260504_084631Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Replays the locked first-passage/touch-hazard selector and nearby controls on current and v21 ledgers.
- This can only prioritize strict forward collection; it is not promotion evidence.

## Split Summary

| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | coverage pass | all splits positive | OOS positive |
|---|---|---:|---:|---:|---:|---:|---|---|---|
| current | `hazard45_touch80_ask80_locked` | 916.0c/4.56% | 75.00%/94.92% | 489.0c | 392.0c | 35.0c | True | True | True |
| v21 | `hazard45_touch80_ask80_locked` | 804.0c/5.55% | 75.00%/92.31% | 69.0c | 510.0c | 225.0c | True | True | True |
| current | `hazard45_touch80_ask80_sec120_control` | 916.0c/4.56% | 75.00%/94.92% | 489.0c | 392.0c | 35.0c | True | True | True |
| v21 | `hazard45_touch80_ask80_sec120_control` | 804.0c/5.55% | 75.00%/92.31% | 69.0c | 510.0c | 225.0c | True | True | True |
| current | `hazard45_touch80_ask95_control` | 940.0c/4.46% | 75.86%/98.31% | 554.0c | 387.0c | -1.0c | True | False | False |
| v21 | `hazard45_touch80_ask95_control` | 673.0c/4.23% | 75.80%/99.10% | -116.0c | 536.0c | 253.0c | True | False | True |
| current | `hazard45_touch90_ask80_control` | 926.0c/4.59% | 75.09%/95.25% | 498.0c | 391.0c | 37.0c | True | True | True |
| v21 | `hazard45_touch90_ask80_control` | 804.0c/5.55% | 75.00%/92.31% | 69.0c | 510.0c | 225.0c | True | True | True |
| current | `hazard50_touch80_ask80_control` | 906.0c/4.58% | 77.82%/90.17% | 701.0c | 243.0c | -38.0c | True | False | False |
| v21 | `hazard50_touch80_ask80_control` | -155.0c/-1.10% | 73.94%/85.07% | -385.0c | 319.0c | -89.0c | True | False | False |

## Block Summary

| dataset | candidate | blocks | positive blocks | positive+coverage blocks | worst block |
|---|---|---:|---:|---:|---:|
| current | `hazard45_touch80_ask80_locked` | 15 | 60.00% | 60.00% | -174.0c |
| v21 | `hazard45_touch80_ask80_locked` | 11 | 63.64% | 63.64% | -240.0c |
| current | `hazard45_touch80_ask80_sec120_control` | 15 | 60.00% | 60.00% | -174.0c |
| v21 | `hazard45_touch80_ask80_sec120_control` | 11 | 63.64% | 63.64% | -240.0c |
| current | `hazard45_touch80_ask95_control` | 15 | 66.67% | 66.67% | -180.0c |
| v21 | `hazard45_touch80_ask95_control` | 11 | 63.64% | 63.64% | -225.0c |
| current | `hazard45_touch90_ask80_control` | 15 | 60.00% | 60.00% | -178.0c |
| v21 | `hazard45_touch90_ask80_control` | 11 | 63.64% | 63.64% | -240.0c |
| current | `hazard50_touch80_ask80_control` | 15 | 66.67% | 66.67% | -145.0c |
| v21 | `hazard50_touch80_ask80_control` | 11 | 45.45% | 45.45% | -373.0c |

## Worst Supported Slices

Only slices with at least `12` selected markets are shown.

| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask |
|---|---|---|---:|---:|---:|---:|---:|
| v21 | `hazard50_touch80_ask80_control` | time=`sec<=600` | 62 | 41/21 | -620.0c | -10.0c | 75.0c |
| v21 | `hazard50_touch80_ask80_control` | side=`yes` | 97 | 69/28 | -427.0c | -4.4c | 74.0c |
| v21 | `hazard45_touch80_ask95_control` | ask=`ask<=80` | 68 | 48/20 | -386.0c | -5.7c | 74.0c |
| v21 | `hazard50_touch80_ask80_control` | split=`train` | 113 | 80/33 | -385.0c | -3.4c | 73.0c |
| current | `hazard45_touch80_ask80_locked` | score=`p<=0.65` | 65 | 46/19 | -316.0c | -4.9c | 73.0c |
| current | `hazard45_touch80_ask80_sec120_control` | score=`p<=0.65` | 65 | 46/19 | -316.0c | -4.9c | 73.0c |
| v21 | `hazard50_touch80_ask80_control` | ask=`ask<=70` | 56 | 36/20 | -289.0c | -5.2c | 68.0c |
| v21 | `hazard45_touch90_ask80_control` | ask=`ask<=80` | 78 | 57/21 | -274.0c | -3.5c | 74.0c |
| v21 | `hazard45_touch80_ask80_locked` | ask=`ask<=80` | 78 | 57/21 | -274.0c | -3.5c | 74.0c |
| v21 | `hazard45_touch80_ask80_sec120_control` | ask=`ask<=80` | 78 | 57/21 | -274.0c | -3.5c | 74.0c |
| current | `hazard45_touch80_ask95_control` | score=`p<=0.65` | 64 | 46/18 | -261.0c | -4.1c | 73.5c |
| current | `hazard45_touch90_ask80_control` | score=`p<=0.65` | 59 | 42/17 | -252.0c | -4.3c | 73.0c |
| v21 | `hazard50_touch80_ask80_control` | score=`p<=0.55` | 72 | 49/23 | -238.0c | -3.3c | 70.0c |
| current | `hazard45_touch80_ask95_control` | hour=`13` | 12 | 7/5 | -194.0c | -16.2c | 72.5c |
| v21 | `hazard45_touch80_ask95_control` | hour=`15` | 12 | 7/5 | -191.0c | -15.9c | 70.0c |
| current | `hazard45_touch80_ask95_control` | time=`sec<=600` | 55 | 39/16 | -187.0c | -3.4c | 72.0c |
| current | `hazard45_touch80_ask80_sec120_control` | time=`sec<=600` | 53 | 37/16 | -185.0c | -3.5c | 72.0c |
| current | `hazard45_touch80_ask80_locked` | time=`sec<=600` | 53 | 37/16 | -185.0c | -3.5c | 72.0c |

## History

| file | candidate | combined all | current all | current val | current holdout | v21 all | v21 train | v21 val | v21 holdout |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `profit_touch_hazard_frontier_20260502_222011Z.csv` | `hazard45_touch80_ask80_locked` | 1158.0c | 354.0c | 95.0c | -14.0c | 804.0c | 69.0c | 510.0c | 225.0c |
| `profit_touch_hazard_frontier_20260503_022110Z.csv` | `hazard45_touch80_ask80_locked` | 1317.0c | 513.0c | 36.0c | 163.0c | 804.0c | 69.0c | 510.0c | 225.0c |
| `profit_touch_hazard_frontier_20260504_053420Z.csv` | `hazard45_touch80_ask80_locked` | 1691.0c | 887.0c | 529.0c | 4.0c | 804.0c | 69.0c | 510.0c | 225.0c |
| `profit_touch_hazard_frontier_latest.csv` | `hazard45_touch80_ask80_locked` | 1691.0c | 887.0c | 529.0c | 4.0c | 804.0c | 69.0c | 510.0c | 225.0c |

## Read

- `hazard45_touch80_ask80_locked` coverage/all-splits/OOS/min positive+coverage block rate/robust: True/True/True/60.00%/False.
- `hazard45_touch80_ask80_sec120_control` coverage/all-splits/OOS/min positive+coverage block rate/robust: True/True/True/60.00%/False.
- `hazard45_touch80_ask95_control` coverage/all-splits/OOS/min positive+coverage block rate/robust: True/False/False/63.64%/False.
- `hazard45_touch90_ask80_control` coverage/all-splits/OOS/min positive+coverage block rate/robust: True/True/True/60.00%/False.
- `hazard50_touch80_ask80_control` coverage/all-splits/OOS/min positive+coverage block rate/robust: True/False/False/45.45%/False.
- Passing offline robustness only justifies continued strict forward registration, not live promotion.
