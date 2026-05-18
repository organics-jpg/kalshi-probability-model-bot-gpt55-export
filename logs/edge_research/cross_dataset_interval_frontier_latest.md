# Cross-Dataset Interval Frontier

Generated UTC: `20260502_184820Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- The same simple policy definitions are evaluated on the current heartbeat ledger and the independent v21 passive ticker ledger.
- Volume denominator is recurring BTC 15-minute markets in each dataset.
- This is a stability/falsification scan, not a promotion lock.

## Data

- Current intervals: 159
- Current side rows: 18380
- V21 intervals: 221
- V21 side rows: 6554
- Shared policies scanned: 2160
- Policies passing target on both datasets: 0
- Policies passing Wilson gate on both datasets: 0
- Nondegenerate policies passing target on both datasets: 0

## Best Shared Policies

| rank | policy | both target | nondeg | current acc | current cov | v21 acc | v21 cov | v21 holdout acc | max median ask |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `choose=book_p_side; book_p_side>=0.8; ask<=95; sec_to_close>=60; adverse15<=10_or_margin_rv15>=0.5` | False | True | 85.71% | 96.86% | 87.75% | 92.31% | 90.00% | 85.0 |
| 2 | `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60` | False | True | 87.76% | 92.45% | 86.91% | 86.43% | 89.19% | 87.0 |
| 3 | `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60; adverse15<=10_or_margin_rv15>=0.5` | False | True | 87.76% | 92.45% | 86.91% | 86.43% | 89.19% | 87.0 |
| 4 | `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60; brownian15>=0.55_and_brownian30>=0.55` | False | True | 87.76% | 92.45% | 86.91% | 86.43% | 89.19% | 87.0 |
| 5 | `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60; spread<=4` | False | True | 87.76% | 92.45% | 86.91% | 86.43% | 89.19% | 87.0 |
| 6 | `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60; margin_rv15>=0` | False | True | 87.76% | 92.45% | 86.91% | 86.43% | 89.19% | 87.0 |
| 7 | `choose=book_p_side; book_p_side>=0.8; ask<=95; sec_to_close>=120; adverse15<=10_or_margin_rv15>=0.5` | False | True | 85.03% | 92.45% | 89.01% | 86.43% | 92.31% | 85.0 |
| 8 | `choose=score_regime_blend; score_regime_blend>=0.8; ask<=95; sec_to_close>=120` | False | True | 82.99% | 92.45% | 85.05% | 87.78% | 88.89% | 83.0 |
| 9 | `choose=score_regime_blend; score_regime_blend>=0.8; ask<=95; sec_to_close>=120; adverse15<=10_or_margin_rv15>=0.5` | False | True | 82.99% | 92.45% | 85.05% | 87.78% | 88.89% | 83.0 |
| 10 | `choose=score_regime_blend; score_regime_blend>=0.8; ask<=95; sec_to_close>=120; brownian15>=0.55_and_brownian30>=0.55` | False | True | 82.99% | 92.45% | 85.05% | 87.78% | 88.89% | 83.0 |
| 11 | `choose=score_regime_blend; score_regime_blend>=0.8; ask<=95; sec_to_close>=120; spread<=4` | False | True | 82.99% | 92.45% | 85.05% | 87.78% | 88.89% | 83.0 |
| 12 | `choose=score_regime_blend; score_regime_blend>=0.8; ask<=95; sec_to_close>=120; margin_rv15>=0` | False | True | 82.99% | 92.45% | 85.05% | 87.78% | 88.89% | 83.0 |
| 13 | `choose=score_regime_blend; score_regime_blend>=0.8; ask<=95; sec_to_close>=60` | False | True | 83.55% | 95.60% | 83.82% | 92.31% | 86.84% | 83.0 |
| 14 | `choose=score_regime_blend; score_regime_blend>=0.8; ask<=95; sec_to_close>=60; adverse15<=10_or_margin_rv15>=0.5` | False | True | 83.55% | 95.60% | 83.82% | 92.31% | 86.84% | 83.0 |
| 15 | `choose=score_regime_blend; score_regime_blend>=0.8; ask<=95; sec_to_close>=60; brownian15>=0.55_and_brownian30>=0.55` | False | True | 83.55% | 95.60% | 83.82% | 92.31% | 86.84% | 83.0 |

## Read

No shared simple policy clears the 95% accuracy / 80% recurring-market coverage split target on both datasets.
No nondegenerate shared simple policy clears the target across both datasets.
