# Interval Path-Physics Blocker Scan

Generated UTC: `20260502_181550Z`

## Scope

- Research-only scan; no orders are submitted and no bot files are modified.
- Starts from the best economical 80%-coverage interval policy.
- Tests path-dependent physics blockers: recent favorable impulse, cushion created by recent move, deceleration, and realized-volatility ratios.
- Unit of volume remains recurring BTC 15-minute market intervals.

## Base Policy

- `choose=score_min_book_rv15; score_min_book_rv15>=0.8; ask<=95; sec_to_close>=60`
- Resolved intervals: 156

## Search Summary

- Candidate blocker rows evaluated: 14
- Target-pass rows: 0
- Wilson-pass rows: 0

## Top Path-Physics Blockers

| rank | blocker | all acc | all cov | val acc | val cov | holdout acc | holdout cov | val Wilson | holdout Wilson | target | Wilson pass |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `block decel_1v5<=-1 OR block rv_ratio_5_15>=1.5` | 89.60% | 80.13% | 89.29% | 90.32% | 91.67% | 75.00% | 72.80% | 74.15% | False | False |
| 2 | `block decel_1v5<=0` | 88.80% | 80.13% | 92.59% | 87.10% | 88.00% | 78.12% | 76.63% | 70.04% | False | False |
| 3 | `block decel_1v5<=-1 OR block decel_1v5<=0` | 88.80% | 80.13% | 92.59% | 87.10% | 88.00% | 78.12% | 76.63% | 70.04% | False | False |
| 4 | `block decel_1v5<=-1` | 88.46% | 83.33% | 89.29% | 90.32% | 88.00% | 78.12% | 72.80% | 70.04% | False | False |
| 5 | `block pre_15m_margin_per_current<=-2 OR block decel_1v5<=-1` | 88.19% | 81.41% | 88.46% | 83.87% | 88.00% | 78.12% | 71.02% | 70.04% | False | False |
| 6 | `block decel_1v5<=-1 OR block rv_ratio_15_30<=0.5` | 88.28% | 82.05% | 89.29% | 90.32% | 87.50% | 75.00% | 72.80% | 69.00% | False | False |
| 7 | `block decel_1v5<=-1 OR block margin_per_sqrt_remaining<=1` | 88.00% | 80.13% | 88.46% | 83.87% | 86.96% | 71.88% | 71.02% | 67.87% | False | False |
| 8 | `block rv_ratio_5_15>=1.5` | 88.89% | 80.77% | 86.21% | 93.55% | 91.67% | 75.00% | 69.44% | 74.15% | False | False |
| 9 | `no blocker` | 87.79% | 83.97% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 10 | `block rv_ratio_15_30<=0.5` | 87.60% | 82.69% | 86.21% | 93.55% | 87.50% | 75.00% | 69.44% | 69.00% | False | False |
| 11 | `block pre_15m_margin_per_current<=-2` | 87.50% | 82.05% | 85.19% | 87.10% | 88.00% | 78.12% | 67.52% | 70.04% | False | False |
| 12 | `block pre_15m_margin_per_current<=-2 OR block rv_ratio_15_30<=0.5` | 87.40% | 81.41% | 85.19% | 87.10% | 87.50% | 75.00% | 67.52% | 69.00% | False | False |
| 13 | `block margin_per_sqrt_remaining<=1` | 87.30% | 80.77% | 85.19% | 87.10% | 86.96% | 71.88% | 67.52% | 67.87% | False | False |
| 14 | `block rv_ratio_15_30<=0.5 OR block margin_per_sqrt_remaining<=1` | 87.20% | 80.13% | 85.19% | 87.10% | 86.96% | 71.88% | 67.52% | 67.87% | False | False |

## 80%-Coverage Path-Physics Blockers

No rows.

## Read

- Best scanned path blocker: `block decel_1v5<=-1 OR block rv_ratio_5_15>=1.5`.
- It selected 125/156 intervals (80.13%) at 89.60% accuracy.
- validation: 89.29% at 90.32%; holdout: 91.67% at 75.00%.
- If no target-pass rows are present, the side-favorable impulse prior does not rescue the economical 80%-coverage frontier by itself.
