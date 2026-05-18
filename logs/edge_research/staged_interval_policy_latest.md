# Staged BTC 15m Interval Policy Scan

Generated UTC: `20260502_181655Z`

## Scope

- Research-only scan; no orders are submitted and no bot files are modified.
- Unit of volume is the recurring BTC 15-minute market ticker.
- Staging is causal: at each heartbeat, economical gate is checked first, then fallback gate; first eligible heartbeat per market is selected.
- Goal is to preserve >=80% market coverage and >=95% accuracy while reducing high-price/late-entry degeneracy.

## Coverage

- Resolved intervals: 156
- Train intervals: 93
- Validation intervals: 31
- Holdout intervals: 32
- Staged candidates scanned: 1152
- Raw target-pass candidates: 108
- Less-degenerate target-pass candidates: 0

## Target-Passing Staged Candidates

| rank | stage1 markets | fallback markets | all acc | all cov | Wilson low | val acc | holdout acc | median ask | ask=100 | ROI | target | less-degen |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 8 | 134 | 100.00% | 91.03% | 97.37% | 100.00% | 100.00% | 97.0 | 22 | 3.30% | True | False |
| 2 | 8 | 134 | 100.00% | 91.03% | 97.37% | 100.00% | 100.00% | 97.0 | 22 | 3.30% | True | False |
| 3 | 8 | 134 | 100.00% | 91.03% | 97.37% | 100.00% | 100.00% | 97.0 | 22 | 3.30% | True | False |
| 4 | 8 | 134 | 100.00% | 91.03% | 97.37% | 100.00% | 100.00% | 97.0 | 22 | 3.30% | True | False |
| 5 | 10 | 128 | 100.00% | 88.46% | 97.29% | 100.00% | 100.00% | 98.0 | 32 | 2.40% | True | False |
| 6 | 10 | 128 | 100.00% | 88.46% | 97.29% | 100.00% | 100.00% | 98.0 | 32 | 2.40% | True | False |
| 7 | 9 | 129 | 100.00% | 88.46% | 97.29% | 100.00% | 100.00% | 98.0 | 33 | 2.33% | True | False |
| 8 | 9 | 129 | 100.00% | 88.46% | 97.29% | 100.00% | 100.00% | 98.0 | 33 | 2.33% | True | False |
| 9 | 10 | 128 | 99.28% | 88.46% | 96.01% | 100.00% | 100.00% | 98.0 | 26 | 2.02% | True | False |
| 10 | 10 | 128 | 99.28% | 88.46% | 96.01% | 100.00% | 100.00% | 98.0 | 26 | 2.02% | True | False |
| 11 | 9 | 129 | 99.28% | 88.46% | 96.01% | 100.00% | 100.00% | 98.0 | 27 | 1.94% | True | False |
| 12 | 9 | 129 | 99.28% | 88.46% | 96.01% | 100.00% | 100.00% | 98.0 | 27 | 1.94% | True | False |
| 13 | 9 | 144 | 98.69% | 98.08% | 95.36% | 96.77% | 100.00% | 97.0 | 9 | 2.12% | True | False |
| 14 | 9 | 144 | 98.69% | 98.08% | 95.36% | 96.77% | 100.00% | 97.0 | 9 | 2.12% | True | False |
| 15 | 9 | 144 | 98.69% | 98.08% | 95.36% | 96.77% | 100.00% | 97.0 | 9 | 2.12% | True | False |

Best row policy detail:

- Stage 1: `economical; choose=score_min_book_rv15; score_min_book_rv15>=0.9; ask<=90; sec>=60`
- Fallback: `fallback; choose=score_min_book_rv15; score_min_book_rv15>=0.9; ask<=100; sec>=0; sec<=300`

## Best Less-Degenerate Candidates

No rows.

## Best Overall Candidates

| rank | stage1 markets | fallback markets | all acc | all cov | Wilson low | val acc | holdout acc | median ask | ask=100 | ROI | target | less-degen |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 8 | 134 | 100.00% | 91.03% | 97.37% | 100.00% | 100.00% | 97.0 | 22 | 3.30% | True | False |
| 2 | 8 | 134 | 100.00% | 91.03% | 97.37% | 100.00% | 100.00% | 97.0 | 22 | 3.30% | True | False |
| 3 | 8 | 134 | 100.00% | 91.03% | 97.37% | 100.00% | 100.00% | 97.0 | 22 | 3.30% | True | False |
| 4 | 8 | 134 | 100.00% | 91.03% | 97.37% | 100.00% | 100.00% | 97.0 | 22 | 3.30% | True | False |
| 5 | 10 | 128 | 100.00% | 88.46% | 97.29% | 100.00% | 100.00% | 98.0 | 32 | 2.40% | True | False |
| 6 | 10 | 128 | 100.00% | 88.46% | 97.29% | 100.00% | 100.00% | 98.0 | 32 | 2.40% | True | False |
| 7 | 9 | 129 | 100.00% | 88.46% | 97.29% | 100.00% | 100.00% | 98.0 | 33 | 2.33% | True | False |
| 8 | 9 | 129 | 100.00% | 88.46% | 97.29% | 100.00% | 100.00% | 98.0 | 33 | 2.33% | True | False |
| 9 | 10 | 128 | 99.28% | 88.46% | 96.01% | 100.00% | 100.00% | 98.0 | 26 | 2.02% | True | False |
| 10 | 10 | 128 | 99.28% | 88.46% | 96.01% | 100.00% | 100.00% | 98.0 | 26 | 2.02% | True | False |
| 11 | 9 | 129 | 99.28% | 88.46% | 96.01% | 100.00% | 100.00% | 98.0 | 27 | 1.94% | True | False |
| 12 | 9 | 129 | 99.28% | 88.46% | 96.01% | 100.00% | 100.00% | 98.0 | 27 | 1.94% | True | False |
| 13 | 9 | 144 | 98.69% | 98.08% | 95.36% | 96.77% | 100.00% | 97.0 | 9 | 2.12% | True | False |
| 14 | 9 | 144 | 98.69% | 98.08% | 95.36% | 96.77% | 100.00% | 97.0 | 9 | 2.12% | True | False |
| 15 | 9 | 144 | 98.69% | 98.08% | 95.36% | 96.77% | 100.00% | 97.0 | 9 | 2.12% | True | False |

Best row policy detail:

- Stage 1: `economical; choose=score_min_book_rv15; score_min_book_rv15>=0.9; ask<=90; sec>=60`
- Fallback: `fallback; choose=score_min_book_rv15; score_min_book_rv15>=0.9; ask<=100; sec>=0; sec<=300`

## Conclusion

Staging can preserve raw 95% / 80% interval performance, but no staged candidate removed the high-price/sample-size degeneracy.
