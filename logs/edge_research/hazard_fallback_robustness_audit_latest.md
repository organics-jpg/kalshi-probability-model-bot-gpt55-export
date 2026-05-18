# Hazard Fallback Robustness Audit

Generated UTC: `20260504_064420Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Replays hazard-primary fallback rows on current and v21 ledgers.
- This can only reject or prioritize strict forward collection; it is not promotion evidence.

## Split Summary

| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | coverage pass | all splits positive | OOS positive |
|---|---|---:|---:|---:|---:|---:|---|---|---|
| current | `book60` | 994.0c/4.78% | 74.91%/99.66% | 608.0c | 390.0c | -4.0c | True | False | False |
| v21 | `book60` | 679.0c/4.32% | 74.21%/100.00% | -29.0c | 450.0c | 258.0c | True | False | True |
| current | `logit_edge10` | 646.0c/3.13% | 73.45%/99.32% | 273.0c | 374.0c | -1.0c | True | False | False |
| v21 | `logit_edge10` | 750.0c/4.82% | 74.43%/99.10% | 215.0c | 451.0c | 84.0c | True | True | True |
| current | `logit_thresh55_edge15` | 1037.0c/4.99% | 75.43%/98.97% | 579.0c | 374.0c | 84.0c | True | True | True |
| v21 | `logit_thresh55_edge15` | 922.0c/5.92% | 75.69%/98.64% | 174.0c | 450.0c | 298.0c | True | True | True |
| current | `score_min60` | 1028.0c/4.95% | 75.43%/98.97% | 567.0c | 374.0c | 87.0c | True | True | True |
| v21 | `score_min60` | 808.0c/5.15% | 75.34%/99.10% | 83.0c | 448.0c | 277.0c | True | True | True |

## Block Summary

| dataset | candidate | blocks | positive blocks | positive+coverage blocks | worst block |
|---|---|---:|---:|---:|---:|
| current | `book60` | 15 | 66.67% | 66.67% | -171.0c |
| v21 | `book60` | 11 | 54.55% | 54.55% | -299.0c |
| current | `logit_edge10` | 15 | 53.33% | 53.33% | -171.0c |
| v21 | `logit_edge10` | 11 | 63.64% | 63.64% | -229.0c |
| current | `logit_thresh55_edge15` | 15 | 66.67% | 66.67% | -171.0c |
| v21 | `logit_thresh55_edge15` | 11 | 63.64% | 63.64% | -321.0c |
| current | `score_min60` | 15 | 66.67% | 66.67% | -171.0c |
| v21 | `score_min60` | 11 | 63.64% | 63.64% | -321.0c |

## Worst Supported Slices

Only slices with at least `12` selected markets are shown.

| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask |
|---|---|---|---:|---:|---:|---:|---:|
| current | `score_min60` | hour=`8` | 12 | 5/7 | -357.0c | -29.8c | 69.0c |
| current | `logit_thresh55_edge15` | hour=`8` | 12 | 5/7 | -353.0c | -29.4c | 69.0c |
| v21 | `logit_thresh55_edge15` | ask=`ask<=80` | 78 | 57/21 | -274.0c | -3.5c | 74.0c |
| v21 | `logit_edge10` | ask=`ask<=80` | 78 | 57/21 | -274.0c | -3.5c | 74.0c |
| v21 | `score_min60` | ask=`ask<=80` | 78 | 57/21 | -274.0c | -3.5c | 74.0c |
| v21 | `book60` | ask=`ask<=80` | 78 | 57/21 | -274.0c | -3.5c | 74.0c |
| current | `book60` | hour=`8` | 12 | 6/6 | -257.0c | -21.4c | 69.0c |
| v21 | `logit_edge10` | hour=`15` | 12 | 6/6 | -248.0c | -20.7c | 69.0c |
| current | `logit_edge10` | hour=`8` | 12 | 6/6 | -247.0c | -20.6c | 69.0c |
| current | `logit_edge10` | hour=`13` | 12 | 6/6 | -246.0c | -20.5c | 70.0c |
| current | `logit_edge10` | selector=`fallback_logit_edge10` | 13 | 6/7 | -194.0c | -14.9c | 51.0c |
| current | `logit_thresh55_edge15` | hour=`13` | 12 | 7/5 | -190.0c | -15.8c | 72.5c |
| current | `score_min60` | hour=`13` | 12 | 7/5 | -190.0c | -15.8c | 72.5c |
| current | `logit_edge10` | time=`sec<=600` | 53 | 37/16 | -185.0c | -3.5c | 72.0c |
| v21 | `score_min60` | hour=`15` | 12 | 7/5 | -181.0c | -15.1c | 70.0c |
| v21 | `logit_thresh55_edge15` | hour=`15` | 12 | 7/5 | -181.0c | -15.1c | 70.0c |
| current | `logit_edge10` | ask=`ask<=60` | 26 | 13/13 | -180.0c | -6.9c | 55.0c |
| current | `book60` | hour=`9` | 12 | 7/5 | -167.0c | -13.9c | 69.0c |

## History

| file | candidate | combined all | current all | current val | current holdout | v21 all | v21 train | v21 val | v21 holdout |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `hazard_fallback_frontier_20260504_063503Z.csv` | `logit_thresh55_edge15` | 1959.0c | 1037.0c | 374.0c | 84.0c | 922.0c | 174.0c | 450.0c | 298.0c |
| `hazard_fallback_frontier_latest.csv` | `logit_thresh55_edge15` | 1959.0c | 1037.0c | 374.0c | 84.0c | 922.0c | 174.0c | 450.0c | 298.0c |

## Read

- `book60` coverage/all-splits/OOS/min positive+coverage block rate/robust: True/False/False/54.55%/False.
- `logit_edge10` coverage/all-splits/OOS/min positive+coverage block rate/robust: True/False/False/53.33%/False.
- `logit_thresh55_edge15` coverage/all-splits/OOS/min positive+coverage block rate/robust: True/True/True/63.64%/False.
- `score_min60` coverage/all-splits/OOS/min positive+coverage block rate/robust: True/True/True/63.64%/False.
- Robust offline diagnostics still require strict live pre-registration before promotion.
