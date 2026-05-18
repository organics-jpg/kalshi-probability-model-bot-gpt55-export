# BTC 15m Market-Interval 80% Coverage Probe

Generated UTC: `20260504_100745Z`

## Scope

- Research-only probe; no orders are submitted and no bot files are modified.
- Source: `logs\edge_research\live_heartbeat_two_side_fv_ledger_latest.csv` / mode `two_side_all_heartbeats`.
- Unit of volume is the recurring BTC 15-minute market ticker.
- A policy can fire once per resolved market; coverage is selected markets / resolved markets.
- Candidate selection is causal inside each market: first heartbeat that passes the gate becomes the trade.
- `nondegenerate_pass` additionally requires `ask_max<=95`, `min_seconds_to_close>=60`, and median ask <=90.
- Fixed fresh-shadow candidate: `choose=score_min_book_rv15; score_min_book_rv15>=0.9; ask<=100; sec_to_close>=0`.

## Coverage

- Resolved market intervals: 307
- Train intervals: 184
- Validation intervals: 61
- Holdout intervals: 62
- Candidate policies scanned: 2160
- Policies covering >=80% of intervals on every split: 1675
- Policies passing 95% accuracy and 80% interval coverage: 50
- Nondegenerate policies passing target: 0

## Target-Passing Policies

| rank | policy | all acc | all cov | val acc | val cov | holdout acc | holdout cov | median ask | median sec | target | nondeg |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=0` | 98.03% | 99.02% | 98.36% | 100.00% | 98.39% | 100.00% | 96.0 | 254.8 | True | False |
| 2 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=0; spread<=4` | 98.03% | 99.02% | 98.36% | 100.00% | 98.39% | 100.00% | 96.0 | 254.8 | True | False |
| 3 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=0; adverse15<=10_or_margin_rv15>=0.5` | 98.01% | 98.05% | 98.36% | 100.00% | 98.36% | 98.39% | 96.0 | 255.8 | True | False |
| 4 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=0; brownian15>=0.55_and_brownian30>=0.55` | 98.00% | 97.72% | 98.33% | 98.36% | 98.39% | 100.00% | 96.0 | 257.6 | True | False |
| 5 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=0; margin_rv15>=0` | 98.00% | 97.72% | 98.33% | 98.36% | 98.39% | 100.00% | 96.0 | 257.6 | True | False |
| 6 | `choose=score_min_book_rv15; score_min_book_rv15>=0.95; ask<=100; sec_to_close>=0` | 98.93% | 91.21% | 98.28% | 95.08% | 100.00% | 95.16% | 98.0 | 175.2 | True | False |
| 7 | `choose=score_min_book_rv15; score_min_book_rv15>=0.95; ask<=100; sec_to_close>=0; adverse15<=10_or_margin_rv15>=0.5` | 98.93% | 91.21% | 98.28% | 95.08% | 100.00% | 95.16% | 98.0 | 175.2 | True | False |
| 8 | `choose=score_min_book_rv15; score_min_book_rv15>=0.95; ask<=100; sec_to_close>=0; brownian15>=0.55_and_brownian30>=0.55` | 98.93% | 91.21% | 98.28% | 95.08% | 100.00% | 95.16% | 98.0 | 175.2 | True | False |
| 9 | `choose=score_min_book_rv15; score_min_book_rv15>=0.95; ask<=100; sec_to_close>=0; spread<=4` | 98.93% | 91.21% | 98.28% | 95.08% | 100.00% | 95.16% | 98.0 | 175.2 | True | False |
| 10 | `choose=score_min_book_rv15; score_min_book_rv15>=0.95; ask<=100; sec_to_close>=0; margin_rv15>=0` | 98.93% | 91.21% | 98.28% | 95.08% | 100.00% | 95.16% | 98.0 | 175.2 | True | False |
| 11 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=60` | 98.21% | 90.88% | 98.28% | 95.08% | 98.28% | 93.55% | 96.0 | 282.1 | True | False |
| 12 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=60; spread<=4` | 98.21% | 90.88% | 98.28% | 95.08% | 98.28% | 93.55% | 96.0 | 282.1 | True | False |
| 13 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=60; adverse15<=10_or_margin_rv15>=0.5` | 98.19% | 89.90% | 98.28% | 95.08% | 98.25% | 91.94% | 96.0 | 283.4 | True | False |
| 14 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=60; margin_rv15>=0` | 98.18% | 89.58% | 98.18% | 90.16% | 98.25% | 91.94% | 96.0 | 284.2 | True | False |
| 15 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=60; brownian15>=0.55_and_brownian30>=0.55` | 98.18% | 89.25% | 98.18% | 90.16% | 98.25% | 91.94% | 96.0 | 284.3 | True | False |

## Best 80%-Coverage Policies

| rank | policy | all acc | all cov | val acc | val cov | holdout acc | holdout cov | median ask | median sec | target | nondeg |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=0` | 98.03% | 99.02% | 98.36% | 100.00% | 98.39% | 100.00% | 96.0 | 254.8 | True | False |
| 2 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=0; spread<=4` | 98.03% | 99.02% | 98.36% | 100.00% | 98.39% | 100.00% | 96.0 | 254.8 | True | False |
| 3 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=0; adverse15<=10_or_margin_rv15>=0.5` | 98.01% | 98.05% | 98.36% | 100.00% | 98.36% | 98.39% | 96.0 | 255.8 | True | False |
| 4 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=0; brownian15>=0.55_and_brownian30>=0.55` | 98.00% | 97.72% | 98.33% | 98.36% | 98.39% | 100.00% | 96.0 | 257.6 | True | False |
| 5 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=0; margin_rv15>=0` | 98.00% | 97.72% | 98.33% | 98.36% | 98.39% | 100.00% | 96.0 | 257.6 | True | False |
| 6 | `choose=score_min_book_rv15; score_min_book_rv15>=0.95; ask<=100; sec_to_close>=0` | 98.93% | 91.21% | 98.28% | 95.08% | 100.00% | 95.16% | 98.0 | 175.2 | True | False |
| 7 | `choose=score_min_book_rv15; score_min_book_rv15>=0.95; ask<=100; sec_to_close>=0; adverse15<=10_or_margin_rv15>=0.5` | 98.93% | 91.21% | 98.28% | 95.08% | 100.00% | 95.16% | 98.0 | 175.2 | True | False |
| 8 | `choose=score_min_book_rv15; score_min_book_rv15>=0.95; ask<=100; sec_to_close>=0; brownian15>=0.55_and_brownian30>=0.55` | 98.93% | 91.21% | 98.28% | 95.08% | 100.00% | 95.16% | 98.0 | 175.2 | True | False |
| 9 | `choose=score_min_book_rv15; score_min_book_rv15>=0.95; ask<=100; sec_to_close>=0; spread<=4` | 98.93% | 91.21% | 98.28% | 95.08% | 100.00% | 95.16% | 98.0 | 175.2 | True | False |
| 10 | `choose=score_min_book_rv15; score_min_book_rv15>=0.95; ask<=100; sec_to_close>=0; margin_rv15>=0` | 98.93% | 91.21% | 98.28% | 95.08% | 100.00% | 95.16% | 98.0 | 175.2 | True | False |
| 11 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=60` | 98.21% | 90.88% | 98.28% | 95.08% | 98.28% | 93.55% | 96.0 | 282.1 | True | False |
| 12 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=60; spread<=4` | 98.21% | 90.88% | 98.28% | 95.08% | 98.28% | 93.55% | 96.0 | 282.1 | True | False |
| 13 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=60; adverse15<=10_or_margin_rv15>=0.5` | 98.19% | 89.90% | 98.28% | 95.08% | 98.25% | 91.94% | 96.0 | 283.4 | True | False |
| 14 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=60; margin_rv15>=0` | 98.18% | 89.58% | 98.18% | 90.16% | 98.25% | 91.94% | 96.0 | 284.2 | True | False |
| 15 | `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=60; brownian15>=0.55_and_brownian30>=0.55` | 98.18% | 89.25% | 98.18% | 90.16% | 98.25% | 91.94% | 96.0 | 284.3 | True | False |

## Best Nondegenerate 80%-Coverage Policies

| rank | policy | all acc | all cov | val acc | val cov | holdout acc | holdout cov | median ask | median sec | target | nondeg |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `choose=score_min_book_rv15; score_min_book_rv15>=0.8; ask<=95; sec_to_close>=60` | 90.73% | 84.36% | 92.59% | 88.52% | 96.00% | 80.65% | 88.0 | 477.9 | False | False |
| 2 | `choose=score_min_book_rv15; score_min_book_rv15>=0.8; ask<=95; sec_to_close>=60; adverse15<=10_or_margin_rv15>=0.5` | 90.73% | 84.36% | 92.59% | 88.52% | 96.00% | 80.65% | 88.0 | 477.9 | False | False |
| 3 | `choose=score_min_book_rv15; score_min_book_rv15>=0.8; ask<=95; sec_to_close>=60; brownian15>=0.55_and_brownian30>=0.55` | 90.73% | 84.36% | 92.59% | 88.52% | 96.00% | 80.65% | 88.0 | 477.9 | False | False |
| 4 | `choose=score_min_book_rv15; score_min_book_rv15>=0.8; ask<=95; sec_to_close>=60; spread<=4` | 90.73% | 84.36% | 92.59% | 88.52% | 96.00% | 80.65% | 88.0 | 477.9 | False | False |
| 5 | `choose=score_min_book_rv15; score_min_book_rv15>=0.8; ask<=95; sec_to_close>=60; margin_rv15>=0` | 90.73% | 84.36% | 92.59% | 88.52% | 96.00% | 80.65% | 88.0 | 477.9 | False | False |
| 6 | `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.8; ask<=95; sec_to_close>=60` | 88.21% | 85.67% | 89.09% | 90.16% | 94.12% | 82.26% | 88.0 | 523.5 | False | False |
| 7 | `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.8; ask<=95; sec_to_close>=60; adverse15<=10_or_margin_rv15>=0.5` | 88.21% | 85.67% | 89.09% | 90.16% | 94.12% | 82.26% | 88.0 | 523.5 | False | False |
| 8 | `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.8; ask<=95; sec_to_close>=60; brownian15>=0.55_and_brownian30>=0.55` | 88.21% | 85.67% | 89.09% | 90.16% | 94.12% | 82.26% | 88.0 | 523.5 | False | False |
| 9 | `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.8; ask<=95; sec_to_close>=60; spread<=4` | 88.21% | 85.67% | 89.09% | 90.16% | 94.12% | 82.26% | 88.0 | 523.5 | False | False |
| 10 | `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.8; ask<=95; sec_to_close>=60; margin_rv15>=0` | 88.21% | 85.67% | 89.09% | 90.16% | 94.12% | 82.26% | 88.0 | 523.5 | False | False |
| 11 | `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.8; ask<=95; sec_to_close>=120` | 87.84% | 83.06% | 88.68% | 86.89% | 94.00% | 80.65% | 87.0 | 526.7 | False | False |
| 12 | `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.8; ask<=95; sec_to_close>=120; adverse15<=10_or_margin_rv15>=0.5` | 87.84% | 83.06% | 88.68% | 86.89% | 94.00% | 80.65% | 87.0 | 526.7 | False | False |
| 13 | `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.8; ask<=95; sec_to_close>=120; brownian15>=0.55_and_brownian30>=0.55` | 87.84% | 83.06% | 88.68% | 86.89% | 94.00% | 80.65% | 87.0 | 526.7 | False | False |
| 14 | `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.8; ask<=95; sec_to_close>=120; spread<=4` | 87.84% | 83.06% | 88.68% | 86.89% | 94.00% | 80.65% | 87.0 | 526.7 | False | False |
| 15 | `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.8; ask<=95; sec_to_close>=120; margin_rv15>=0` | 87.84% | 83.06% | 88.68% | 86.89% | 94.00% | 80.65% | 87.0 | 526.7 | False | False |

## Physics Read

- Best 80%-coverage policy: `choose=book_p_side; book_p_side>=0.95; ask<=100; sec_to_close>=0`.
- It covered 304/307 intervals (99.02%) at 98.03% all accuracy.
- Validation was 98.36% at 100.00%; holdout was 98.39% at 100.00%.
- Median selected ask was 96.0 cents.
- Median selected time-to-close was 254.8 seconds.
- To reach 95% on validation from this policy without losing wins, another 0 selected losses would need to be blocked.
- To reach 95% on holdout from this policy without losing wins, another 0 selected losses would need to be blocked.

## Fixed Candidate Fresh Lock

- Lock file: `logs\edge_research\market_interval_80coverage_lock.json`
- Lock close time: `2026-05-02T14:30:00+00:00`
- Fixed candidate all accuracy: 97.92%
- Fixed candidate all interval coverage: 94.14%
- Fixed candidate validation: 96.61% at 96.72% coverage
- Fixed candidate holdout: 100.00% at 96.77% coverage
- Fresh post-lock rows are evaluated in `market_interval_80coverage_selected_latest.csv`; zero or tiny fresh counts are not completion evidence.
- Fresh resolved intervals after lock: 162
- Fresh selected intervals after lock: 155
- Fresh selected accuracy: 98.06%
- Fresh interval coverage: 95.68%
- Fresh median ask: 96.0 cents
- Fresh median seconds to close: 290.8

## Conclusion

At least one interval policy clears the raw 95% / 80% target, but the pass is likely settlement-price leakage or expensive late-entry behavior unless it also appears in the nondegenerate table.
