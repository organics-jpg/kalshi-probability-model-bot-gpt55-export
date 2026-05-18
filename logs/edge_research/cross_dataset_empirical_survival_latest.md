# Cross-Dataset Empirical Survival

Generated UTC: `20260502_210830Z`

## Scope

- Research-only probe; no orders are submitted and no bot files are modified.
- Replaces parametric Brownian probability with empirical live-state survival tables.
- Tables train only on one capture's chronological train split, then transfer without retuning to the other capture.
- Target requires source validation/holdout and target all/train/validation/holdout to clear 95% accuracy and 80% recurring-market coverage.

## Data

- Current intervals: 166; rows: 19190
- V21 intervals: 221; rows: 6554
- Candidate rows evaluated: 3840
- Transfer target passes: 0
- Transfer Wilson passes: 0

## Top Empirical Survival Transfers

| rank | train | scheme | score | gate | source val/holdout | target all/holdout | min oos acc | min oos cov | median ask | target |
|---:|---|---|---|---|---:|---:|---:|---:|---:|---|
| 1 | current | `book_z15_time_drift5` | `emp_p` | `emp_p>=0.9; n>=50; ask<=100.0; sec>=0.0` | 100.00%/100.00% | 100.00%/100.00% | 100.00% | 55.56% | 98.0 | False |
| 2 | current | `book_z15_time_drift5` | `emp_p` | `emp_p>=0.95; n>=50; ask<=100.0; sec>=0.0` | 100.00%/100.00% | 100.00%/100.00% | 100.00% | 55.56% | 98.0 | False |
| 3 | current | `book_z15_time_adv5` | `emp_p` | `emp_p>=0.9; n>=50; ask<=100.0; sec>=0.0` | 100.00%/100.00% | 100.00%/100.00% | 100.00% | 53.33% | 98.0 | False |
| 4 | current | `book_z15_time_adv5` | `emp_lower` | `emp_lower>=0.8; n>=50; ask<=100.0; sec>=0.0` | 100.00%/100.00% | 100.00%/100.00% | 100.00% | 53.33% | 98.0 | False |
| 5 | current | `book_z15_time_adv5` | `emp_p` | `emp_p>=0.95; n>=50; ask<=100.0; sec>=0.0` | 100.00%/100.00% | 100.00%/100.00% | 100.00% | 53.33% | 98.0 | False |
| 6 | current | `book_z15_time` | `emp_p` | `emp_p>=0.75; n>=100; ask<=100.0; sec>=0.0` | 100.00%/100.00% | 100.00%/100.00% | 100.00% | 53.33% | 99.0 | False |
| 7 | current | `book_z15_time` | `emp_p` | `emp_p>=0.8; n>=100; ask<=100.0; sec>=0.0` | 100.00%/100.00% | 100.00%/100.00% | 100.00% | 53.33% | 99.0 | False |
| 8 | current | `book_z15_time` | `emp_p` | `emp_p>=0.85; n>=100; ask<=100.0; sec>=0.0` | 100.00%/100.00% | 100.00%/100.00% | 100.00% | 53.33% | 99.0 | False |
| 9 | current | `book_z15_time` | `emp_p` | `emp_p>=0.9; n>=100; ask<=100.0; sec>=0.0` | 100.00%/100.00% | 100.00%/100.00% | 100.00% | 53.33% | 99.0 | False |
| 10 | current | `book_z15_time` | `emp_p` | `emp_p>=0.95; n>=100; ask<=100.0; sec>=0.0` | 100.00%/100.00% | 100.00%/100.00% | 100.00% | 53.33% | 99.0 | False |
| 11 | current | `book_z15_time` | `emp_lower` | `emp_lower>=0.7; n>=100; ask<=100.0; sec>=0.0` | 100.00%/100.00% | 100.00%/100.00% | 100.00% | 53.33% | 99.0 | False |
| 12 | current | `book_z15_time` | `emp_lower` | `emp_lower>=0.8; n>=100; ask<=100.0; sec>=0.0` | 100.00%/100.00% | 100.00%/100.00% | 100.00% | 53.33% | 99.0 | False |
| 13 | current | `book_z15_time_drift5` | `emp_p` | `emp_p>=0.7; n>=100; ask<=100.0; sec>=0.0` | 100.00%/100.00% | 100.00%/100.00% | 100.00% | 53.33% | 99.0 | False |
| 14 | current | `book_z15_time_drift5` | `emp_p` | `emp_p>=0.75; n>=100; ask<=100.0; sec>=0.0` | 100.00%/100.00% | 100.00%/100.00% | 100.00% | 53.33% | 99.0 | False |
| 15 | current | `book_z15_time_drift5` | `emp_p` | `emp_p>=0.8; n>=100; ask<=100.0; sec>=0.0` | 100.00%/100.00% | 100.00%/100.00% | 100.00% | 53.33% | 99.0 | False |

## Read

- No empirical survival transfer cleared the 95% accuracy / 80% recurring-market target.
- Best row trained on current with scheme `book_z15_time_drift5`; min OOS accuracy 100.00%, min OOS coverage 55.56%, max median ask 98.0c.
- If target passes remain zero, the empirical-state prior does not overcome the broad-coverage physics frontier.
