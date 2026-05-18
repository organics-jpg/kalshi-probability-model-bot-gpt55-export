# Interval Loss-blocker Search

Generated UTC: `20260502_181551Z`

## Scope

- Research-only scan; no orders are submitted and no bot files are modified.
- Starts from the best economical 80%-coverage interval policy, then applies one or two simple blockers.
- Unit of volume is the recurring BTC 15-minute market interval.
- Candidate blockers are exploratory; chronological validation/holdout and Wilson bounds are shown to avoid in-sample promotion.

## Base Policy

- `choose=score_min_book_rv15; score_min_book_rv15>=0.8; ask<=95; sec_to_close>=60`
- Selected 131/156 intervals (83.97%) at 87.79% accuracy.

## Search Summary

- Resolved intervals: 156
- Base selected intervals: 131
- Candidate blocker policies scanned: 47
- Target-pass blocker policies: 0
- Wilson-pass blocker policies: 0

## Top Blocker Policies

| rank | blocker | all acc | all cov | val acc | val cov | holdout acc | holdout cov | val Wilson | holdout Wilson | target | Wilson pass |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `block drift_p_5m_rv_15m<=0.85` | 88.89% | 80.77% | 88.89% | 87.10% | 88.00% | 78.12% | 71.94% | 70.04% | False | False |
| 2 | `block drift_p_5m_rv_15m<=0.85 OR block adverse_move_5m>=5` | 88.89% | 80.77% | 88.89% | 87.10% | 88.00% | 78.12% | 71.94% | 70.04% | False | False |
| 3 | `block drift_p_5m_rv_15m<=0.85 OR block adverse_move_5m>=20` | 88.89% | 80.77% | 88.89% | 87.10% | 88.00% | 78.12% | 71.94% | 70.04% | False | False |
| 4 | `block drift_p_5m_rv_15m<=0.85 OR block adverse_move_3m>=10` | 88.80% | 80.13% | 88.89% | 87.10% | 88.00% | 78.12% | 71.94% | 70.04% | False | False |
| 5 | `block adverse_move_5m>=5` | 88.37% | 82.69% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 6 | `block adverse_move_3m>=10 OR block adverse_move_5m>=5` | 88.28% | 82.05% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 7 | `block adverse_move_3m>=5 OR block adverse_move_5m>=5` | 88.19% | 81.41% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 8 | `block adverse_move_5m>=5 OR block adverse_move_15m>=50` | 88.19% | 81.41% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 9 | `block margin_per_rv_sigma_30m<=0.5 OR block adverse_move_5m>=5` | 88.19% | 81.41% | 86.21% | 93.55% | 87.50% | 75.00% | 69.44% | 69.00% | False | False |
| 10 | `block adverse_move_5m>=5 OR block adverse_move_15m>=35` | 88.10% | 80.77% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 11 | `no blocker` | 87.79% | 83.97% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 12 | `block adverse_move_3m>=10` | 87.69% | 83.33% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 13 | `block adverse_move_5m>=20` | 87.69% | 83.33% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 14 | `block adverse_move_3m>=5` | 87.60% | 82.69% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 15 | `block adverse_move_15m>=50` | 87.60% | 82.69% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 16 | `block adverse_move_3m>=10 OR block adverse_move_5m>=20` | 87.60% | 82.69% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 17 | `block margin_per_rv_sigma_30m<=0.5` | 87.60% | 82.69% | 86.21% | 93.55% | 87.50% | 75.00% | 69.44% | 69.00% | False | False |
| 18 | `block adverse_move_15m>=35` | 87.50% | 82.05% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 19 | `block adverse_move_3m>=5 OR block adverse_move_5m>=20` | 87.50% | 82.05% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 20 | `block adverse_move_3m>=10 OR block adverse_move_15m>=50` | 87.50% | 82.05% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |

## 80%-Coverage Blocker Policies

| rank | blocker | all acc | all cov | val acc | val cov | holdout acc | holdout cov | val Wilson | holdout Wilson | target | Wilson pass |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `block drift_p_5m_rv_15m<=0.85` | 88.89% | 80.77% | 88.89% | 87.10% | 88.00% | 78.12% | 71.94% | 70.04% | False | False |
| 2 | `block drift_p_5m_rv_15m<=0.85 OR block adverse_move_5m>=5` | 88.89% | 80.77% | 88.89% | 87.10% | 88.00% | 78.12% | 71.94% | 70.04% | False | False |
| 3 | `block drift_p_5m_rv_15m<=0.85 OR block adverse_move_5m>=20` | 88.89% | 80.77% | 88.89% | 87.10% | 88.00% | 78.12% | 71.94% | 70.04% | False | False |
| 4 | `block drift_p_5m_rv_15m<=0.85 OR block adverse_move_3m>=10` | 88.80% | 80.13% | 88.89% | 87.10% | 88.00% | 78.12% | 71.94% | 70.04% | False | False |
| 5 | `block adverse_move_5m>=5` | 88.37% | 82.69% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 6 | `block adverse_move_3m>=10 OR block adverse_move_5m>=5` | 88.28% | 82.05% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 7 | `block adverse_move_3m>=5 OR block adverse_move_5m>=5` | 88.19% | 81.41% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 8 | `block adverse_move_5m>=5 OR block adverse_move_15m>=50` | 88.19% | 81.41% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 9 | `block margin_per_rv_sigma_30m<=0.5 OR block adverse_move_5m>=5` | 88.19% | 81.41% | 86.21% | 93.55% | 87.50% | 75.00% | 69.44% | 69.00% | False | False |
| 10 | `block adverse_move_5m>=5 OR block adverse_move_15m>=35` | 88.10% | 80.77% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 11 | `no blocker` | 87.79% | 83.97% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 12 | `block adverse_move_3m>=10` | 87.69% | 83.33% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 13 | `block adverse_move_5m>=20` | 87.69% | 83.33% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 14 | `block adverse_move_3m>=5` | 87.60% | 82.69% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 15 | `block adverse_move_15m>=50` | 87.60% | 82.69% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 16 | `block adverse_move_3m>=10 OR block adverse_move_5m>=20` | 87.60% | 82.69% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 17 | `block margin_per_rv_sigma_30m<=0.5` | 87.60% | 82.69% | 86.21% | 93.55% | 87.50% | 75.00% | 69.44% | 69.00% | False | False |
| 18 | `block adverse_move_15m>=35` | 87.50% | 82.05% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 19 | `block adverse_move_3m>=5 OR block adverse_move_5m>=20` | 87.50% | 82.05% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |
| 20 | `block adverse_move_3m>=10 OR block adverse_move_15m>=50` | 87.50% | 82.05% | 86.21% | 93.55% | 88.00% | 78.12% | 69.44% | 70.04% | False | False |

## Read

- Best scanned blocker: `block drift_p_5m_rv_15m<=0.85`.
- It selected 126/156 intervals (80.77%) at 88.89% accuracy.
- validation: 88.89% accuracy at 87.10% coverage; needs 2 additional selected losses blocked without losing wins to reach 95%.
- holdout: 88.00% accuracy at 78.12% coverage; needs 2 additional selected losses blocked without losing wins to reach 95%.
- No blocker combination found a nondegenerate 95% / 80% recurring-market policy.
- No blocker combination produced a sample-size-safe 95% Wilson lower bound across splits.
