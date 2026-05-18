# Profit Lock Candidate Stability Audit

Generated UTC: `20260504_035742Z`

## Scope

- Research-only stability diagnostic; no orders are submitted and no bot files or live processes are touched.
- Compares locked candidates on current and independent v21 ledgers.
- Slice losses are diagnostic only; strict pre-registered live evidence remains the promotion gate.

## Candidate Summary

| dataset | policy | all net/ROI | all acc/cov | validation net | holdout net | OOS positive |
|---|---|---:|---:|---:|---:|---|
| current | `book_margin` | 1137.0c/6.03% | 71.68%/99.29% | 250.0c | 289.0c | True |
| current | `book_margin_early` | 1167.0c/6.37% | 71.96%/96.44% | 181.0c | 289.0c | True |
| current | `book_margin_gap015` | 1416.0c/8.49% | 72.40%/88.97% | 367.0c | 120.0c | True |
| current | `frontier_v2` | 306.0c/1.75% | 63.80%/99.29% | 319.0c | -327.0c | False |
| current | `score_min60` | 1318.0c/6.63% | 76.26%/98.93% | 748.0c | 25.0c | True |
| current | `score_min60_gap020` | 1485.0c/7.53% | 76.81%/98.22% | 748.0c | 25.0c | True |
| current | `v2_wait_score_min60_brownian70_early` | 1410.0c/7.12% | 76.26%/98.93% | 767.0c | -52.0c | False |
| current | `v2_wait_score_min60_early` | 1337.0c/6.73% | 76.26%/98.93% | 767.0c | 25.0c | True |
| v21 | `book_margin` | 425.0c/2.80% | 71.23%/99.10% | 212.0c | 293.0c | True |
| v21 | `book_margin_early` | 719.0c/5.00% | 72.60%/94.12% | 243.0c | 250.0c | True |
| v21 | `book_margin_gap015` | 306.0c/2.07% | 70.56%/96.83% | 212.0c | 259.0c | True |
| v21 | `frontier_v2` | 1283.0c/9.42% | 68.04%/99.10% | 92.0c | 620.0c | True |
| v21 | `score_min60` | 534.0c/3.43% | 73.85%/98.64% | 398.0c | 155.0c | True |
| v21 | `score_min60_gap020` | 534.0c/3.43% | 73.85%/98.64% | 398.0c | 155.0c | True |
| v21 | `v2_wait_score_min60_brownian70_early` | 755.0c/4.89% | 74.31%/98.64% | 398.0c | 208.0c | True |
| v21 | `v2_wait_score_min60_early` | 558.0c/3.59% | 73.85%/98.64% | 398.0c | 179.0c | True |

## Worst Supported Slices

Only slices with at least `8` markets are shown.

| dataset | policy | slice | markets | wins/losses | net | net/market | median ask |
|---|---|---|---:|---:|---:|---:|---:|
| current | `score_min60` | entry_hour_utc=`8` | 12 | 5/7 | -348.0c | -29.0c | 69.0c |
| current | `v2_wait_score_min60_brownian70_early` | entry_hour_utc=`8` | 12 | 5/7 | -348.0c | -29.0c | 69.0c |
| current | `v2_wait_score_min60_early` | entry_hour_utc=`8` | 12 | 5/7 | -348.0c | -29.0c | 69.0c |
| current | `score_min60_gap020` | entry_hour_utc=`8` | 12 | 5/7 | -348.0c | -29.0c | 69.0c |
| v21 | `book_margin` | entry_hour_utc=`3` | 8 | 2/6 | -334.0c | -41.8c | 64.5c |
| v21 | `book_margin_gap015` | entry_hour_utc=`3` | 8 | 2/6 | -334.0c | -41.8c | 64.5c |
| current | `frontier_v2` | split=`holdout` | 57 | 34/23 | -327.0c | -5.7c | 63.0c |
| current | `frontier_v2` | ask_bucket=`ask<=55` | 77 | 37/40 | -323.0c | -4.2c | 51.0c |
| current | `frontier_v2` | entry_hour_utc=`22` | 12 | 5/7 | -273.0c | -22.8c | 62.5c |
| v21 | `v2_wait_score_min60_early` | entry_hour_utc=`3` | 8 | 3/5 | -265.0c | -33.1c | 66.0c |
| v21 | `score_min60_gap020` | entry_hour_utc=`3` | 8 | 3/5 | -265.0c | -33.1c | 66.0c |
| v21 | `v2_wait_score_min60_brownian70_early` | entry_hour_utc=`3` | 8 | 3/5 | -265.0c | -33.1c | 66.0c |
| v21 | `score_min60` | entry_hour_utc=`3` | 8 | 3/5 | -265.0c | -33.1c | 66.0c |
| v21 | `frontier_v2` | entry_hour_utc=`3` | 8 | 3/5 | -222.0c | -27.8c | 63.0c |
| current | `frontier_v2` | entry_hour_utc=`3` | 13 | 6/7 | -203.0c | -15.6c | 61.0c |
| current | `book_margin` | entry_hour_utc=`8` | 12 | 6/6 | -199.0c | -16.6c | 65.0c |
| current | `book_margin_gap015` | entry_hour_utc=`8` | 12 | 6/6 | -199.0c | -16.6c | 65.0c |
| current | `book_margin_early` | entry_hour_utc=`3` | 12 | 6/6 | -190.0c | -15.8c | 62.0c |
| current | `frontier_v2` | entry_hour_utc=`17` | 12 | 5/7 | -190.0c | -15.8c | 58.0c |
| v21 | `book_margin` | time_bucket=`sec<=600` | 28 | 18/10 | -187.0c | -6.7c | 66.5c |

## Read

- `book_margin` coverage/OOS-positive/stressed-loss slices: True/True/24.
- `book_margin_early` coverage/OOS-positive/stressed-loss slices: True/True/18.
- `book_margin_gap015` coverage/OOS-positive/stressed-loss slices: True/True/23.
- `frontier_v2` coverage/OOS-positive/stressed-loss slices: True/False/24.
- `score_min60` coverage/OOS-positive/stressed-loss slices: True/True/20.
- `score_min60_gap020` coverage/OOS-positive/stressed-loss slices: True/True/18.
- `v2_wait_score_min60_brownian70_early` coverage/OOS-positive/stressed-loss slices: True/False/17.
- `v2_wait_score_min60_early` coverage/OOS-positive/stressed-loss slices: True/True/19.
- Candidates with supported losing slices or cross-dataset giveback should stay forward-test only.
