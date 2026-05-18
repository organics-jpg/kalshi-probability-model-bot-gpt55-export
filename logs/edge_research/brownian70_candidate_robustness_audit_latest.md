# Brownian70 Candidate Robustness Audit

Generated UTC: `20260504_101005Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Tests whether the Brownian/RV15 70% frontier row is stable enough for a separate forward lock.
- This is diagnostic only; strict pre-registered live evidence remains the promotion gate.

## Split Summary

| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | coverage pass | all splits positive | OOS positive |
|---|---|---:|---:|---:|---:|---:|---|---|---|
| current | `brownian70_ask90_sec120` | 864.0c/3.94% | 81.43%/91.21% | 254.0c | 256.0c | 354.0c | True | True | True |
| v21 | `brownian70_ask90_sec120` | 80.0c/0.50% | 79.02%/92.76% | -362.0c | 327.0c | 115.0c | True | False | True |
| current | `brownian70_sec120` | 912.0c/3.93% | 82.25%/95.44% | 298.0c | 262.0c | 352.0c | True | True | True |
| v21 | `brownian70_sec120` | 132.0c/0.78% | 79.81%/96.38% | -337.0c | 341.0c | 128.0c | True | False | True |
| current | `brownian70_sec60` | 881.0c/3.75% | 82.15%/96.74% | 261.0c | 262.0c | 358.0c | True | True | True |
| v21 | `brownian70_sec60` | 38.0c/0.22% | 79.44%/96.83% | -431.0c | 341.0c | 128.0c | True | False | True |
| current | `score_min60_lock_equiv` | 1174.0c/5.40% | 75.33%/99.02% | 784.0c | 287.0c | 103.0c | True | True | True |
| v21 | `score_min60_lock_equiv` | 534.0c/3.43% | 73.85%/98.64% | -19.0c | 398.0c | 155.0c | True | False | True |

## Block Summary

| dataset | candidate | blocks | positive blocks | positive+coverage blocks | worst block |
|---|---|---:|---:|---:|---:|
| current | `brownian70_ask90_sec120` | 15 | 73.33% | 73.33% | -298.0c |
| v21 | `brownian70_ask90_sec120` | 11 | 54.55% | 54.55% | -368.0c |
| current | `brownian70_sec120` | 15 | 73.33% | 73.33% | -290.0c |
| v21 | `brownian70_sec120` | 11 | 54.55% | 54.55% | -368.0c |
| current | `brownian70_sec60` | 15 | 73.33% | 73.33% | -290.0c |
| v21 | `brownian70_sec60` | 11 | 45.45% | 45.45% | -368.0c |
| current | `score_min60_lock_equiv` | 15 | 66.67% | 66.67% | -220.0c |
| v21 | `score_min60_lock_equiv` | 11 | 63.64% | 63.64% | -228.0c |

## Worst Supported Slices

Only slices with at least `12` selected markets are shown.

| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask |
|---|---|---|---:|---:|---:|---:|---:|
| v21 | `brownian70_ask90_sec120` | time=`sec<=600` | 74 | 51/23 | -796.0c | -10.8c | 78.0c |
| v21 | `brownian70_sec120` | time=`sec<=600` | 77 | 54/23 | -779.0c | -10.1c | 78.0c |
| v21 | `brownian70_sec60` | time=`sec<=600` | 77 | 54/23 | -779.0c | -10.1c | 78.0c |
| v21 | `brownian70_sec60` | split=`train` | 128 | 96/32 | -431.0c | -3.4c | 76.0c |
| v21 | `brownian70_ask90_sec120` | split=`train` | 123 | 92/31 | -362.0c | -2.9c | 76.0c |
| v21 | `brownian70_sec120` | split=`train` | 127 | 96/31 | -337.0c | -2.7c | 76.0c |
| current | `score_min60_lock_equiv` | hour=`9` | 15 | 8/7 | -281.0c | -18.7c | 70.0c |
| current | `score_min60_lock_equiv` | hour=`8` | 16 | 9/7 | -242.0c | -15.1c | 69.0c |
| v21 | `brownian70_sec60` | side=`yes` | 112 | 87/25 | -232.0c | -2.1c | 78.0c |
| current | `brownian70_ask90_sec120` | hour=`8` | 13 | 8/5 | -230.0c | -17.7c | 79.0c |
| current | `brownian70_sec120` | hour=`8` | 13 | 8/5 | -230.0c | -17.7c | 79.0c |
| current | `brownian70_sec60` | hour=`8` | 13 | 8/5 | -230.0c | -17.7c | 79.0c |
| v21 | `brownian70_sec60` | hour=`15` | 12 | 8/4 | -200.0c | -16.7c | 81.5c |
| v21 | `brownian70_sec120` | hour=`15` | 12 | 8/4 | -200.0c | -16.7c | 81.5c |
| current | `brownian70_sec60` | hour=`13` | 12 | 8/4 | -189.0c | -15.8c | 81.0c |
| current | `brownian70_sec120` | hour=`13` | 12 | 8/4 | -189.0c | -15.8c | 81.0c |

## History

| file | candidate | current all | current val | current holdout | v21 all | v21 train | v21 val | v21 holdout |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `cross_dataset_profit_frontier_20260502_212020Z.csv` | `brownian70_sec120` | 165.0c | 100.0c | 88.0c | 132.0c | -337.0c | 341.0c | 128.0c |
| `cross_dataset_profit_frontier_20260502_212556Z.csv` | `brownian70_sec120` | 136.0c | 105.0c | 99.0c | 132.0c | -337.0c | 341.0c | 128.0c |
| `cross_dataset_profit_frontier_20260503_134129Z.csv` | `brownian70_sec120` | 591.0c | 204.0c | 331.0c | 132.0c | -337.0c | 341.0c | 128.0c |
| `cross_dataset_profit_frontier_20260503_221153Z.csv` | `brownian70_sec120` | 623.0c | 529.0c | -49.0c | 132.0c | -337.0c | 341.0c | 128.0c |
| `cross_dataset_profit_frontier_20260504_035415Z.csv` | `brownian70_sec120` | 749.0c | 526.0c | 11.0c | 132.0c | -337.0c | 341.0c | 128.0c |
| `cross_dataset_profit_frontier_20260504_055140Z.csv` | `brownian70_sec120` | 812.0c | 275.0c | 332.0c | 132.0c | -337.0c | 341.0c | 128.0c |
| `cross_dataset_profit_frontier_20260504_100602Z.csv` | `brownian70_sec120` | 912.0c | 262.0c | 352.0c | 132.0c | -337.0c | 341.0c | 128.0c |
| `cross_dataset_profit_frontier_latest.csv` | `brownian70_sec120` | 912.0c | 262.0c | 352.0c | 132.0c | -337.0c | 341.0c | 128.0c |

## Read

- `brownian70_ask90_sec120` coverage/all-splits/OOS/min positive+coverage block rate/robust: True/False/True/54.55%/False.
- `brownian70_sec120` coverage/all-splits/OOS/min positive+coverage block rate/robust: True/False/True/54.55%/False.
- `brownian70_sec60` coverage/all-splits/OOS/min positive+coverage block rate/robust: True/False/True/45.45%/False.
- `score_min60_lock_equiv` coverage/all-splits/OOS/min positive+coverage block rate/robust: True/False/True/63.64%/False.
- A candidate that fails all-split or block stability should remain observation-only, not promotion evidence.
