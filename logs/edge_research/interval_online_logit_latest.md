# Chronological Interval Logistic Probe

Generated UTC: `20260502_181733Z`

## Scope

- Research-only probe; no orders are submitted and no bot files are modified.
- Models train only on the chronological train split.
- Thresholds are picked from train-market behavior; validation and holdout are forward checks.
- Unit of volume is the recurring BTC 15-minute market interval.

## Coverage

- Resolved intervals: 156
- Train / validation / holdout: 93 / 31 / 32
- Candidate policies scanned: 1440
- Target-pass policies: 9
- Wilson-pass policies: 0

## Top Policies

| rank | policy | all acc | all cov | val acc | val cov | holdout acc | holdout cov | val Wilson | holdout Wilson | train-picked | target | Wilson pass |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| 1 | `book_physics_price; C=0.05; p>=0.95; ask<=100; sec>=0` | 99.31% | 92.95% | 100.00% | 93.55% | 100.00% | 90.62% | 88.30% | 88.30% | True | True | False |
| 2 | `book_physics; C=1; p>=0.95; ask<=100; sec>=0` | 98.64% | 94.23% | 100.00% | 96.77% | 100.00% | 93.75% | 88.65% | 88.65% | True | True | False |
| 3 | `book_physics_price; C=1; p>=0.95; ask<=100; sec>=0` | 98.64% | 94.23% | 100.00% | 93.55% | 100.00% | 90.62% | 88.30% | 88.30% | True | True | False |
| 4 | `book_physics_price; C=0.1; p>=0.95; ask<=100; sec>=0` | 98.64% | 94.23% | 100.00% | 93.55% | 100.00% | 90.62% | 88.30% | 88.30% | True | True | False |
| 5 | `book_physics; C=0.3; p>=0.95; ask<=100; sec>=0` | 98.62% | 92.95% | 100.00% | 93.55% | 100.00% | 90.62% | 88.30% | 88.30% | True | True | False |
| 6 | `book_physics_price; C=0.3; p>=0.95; ask<=100; sec>=0` | 98.62% | 92.95% | 100.00% | 90.32% | 100.00% | 87.50% | 87.94% | 87.94% | True | True | False |
| 7 | `book_physics; C=0.1; p>=0.95; ask<=100; sec>=0` | 98.60% | 91.67% | 100.00% | 93.55% | 100.00% | 87.50% | 88.30% | 87.94% | True | True | False |
| 8 | `book_physics; C=0.05; p>=0.95; ask<=100; sec>=0` | 98.59% | 91.03% | 100.00% | 93.55% | 100.00% | 87.50% | 88.30% | 87.94% | True | True | False |
| 9 | `physics_no_book_price; C=0.05; p>=0.95; ask<=100; sec>=0` | 97.86% | 89.74% | 96.55% | 93.55% | 100.00% | 81.25% | 82.82% | 87.13% | True | True | False |
| 10 | `physics_no_book_price; C=0.3; p>=0.95; ask<=100; sec>=0` | 97.18% | 91.03% | 93.33% | 96.77% | 100.00% | 84.38% | 78.68% | 87.54% | True | False | False |
| 11 | `physics_no_book_price; C=1; p>=0.95; ask<=100; sec>=0` | 95.77% | 91.03% | 93.33% | 96.77% | 96.30% | 84.38% | 78.68% | 81.72% | True | False | False |
| 12 | `physics_no_book_price; C=0.1; p>=0.95; ask<=100; sec>=0` | 97.14% | 89.74% | 93.10% | 93.55% | 100.00% | 81.25% | 78.04% | 87.13% | True | False | False |
| 13 | `book_physics_price; C=0.05; p>=0.95; ask<=100; sec>=60` | 99.17% | 76.92% | 100.00% | 77.42% | 100.00% | 68.75% | 86.20% | 85.13% | False | False | False |
| 14 | `book_physics_price; C=0.05; p>=0.95; ask<=100; sec>=120` | 98.94% | 60.26% | 100.00% | 61.29% | 100.00% | 53.12% | 83.18% | 81.57% | False | False | False |
| 15 | `book_physics; C=1; p>=0.95; ask<=100; sec>=60` | 98.35% | 77.56% | 100.00% | 74.19% | 100.00% | 75.00% | 85.69% | 86.20% | False | False | False |
| 16 | `book_physics_price; C=0.1; p>=0.95; ask<=100; sec>=60` | 98.35% | 77.56% | 100.00% | 77.42% | 100.00% | 68.75% | 86.20% | 85.13% | False | False | False |
| 17 | `book_physics; C=0.3; p>=0.95; ask<=100; sec>=60` | 98.32% | 76.28% | 100.00% | 74.19% | 100.00% | 71.88% | 85.69% | 85.69% | False | False | False |
| 18 | `book_physics_price; C=0.3; p>=0.95; ask<=100; sec>=60` | 98.31% | 75.64% | 100.00% | 74.19% | 100.00% | 68.75% | 85.69% | 85.13% | False | False | False |
| 19 | `book_physics_price; C=1; p>=0.95; ask<=100; sec>=60` | 98.28% | 74.36% | 100.00% | 74.19% | 100.00% | 71.88% | 85.69% | 85.69% | False | False | False |
| 20 | `book_physics; C=0.1; p>=0.95; ask<=100; sec>=60` | 98.28% | 74.36% | 100.00% | 74.19% | 100.00% | 68.75% | 85.69% | 85.13% | False | False | False |

## Train-picked Policies

| rank | policy | all acc | all cov | val acc | val cov | holdout acc | holdout cov | val Wilson | holdout Wilson | train-picked | target | Wilson pass |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| 1 | `book_physics_price; C=0.05; p>=0.95; ask<=100; sec>=0` | 99.31% | 92.95% | 100.00% | 93.55% | 100.00% | 90.62% | 88.30% | 88.30% | True | True | False |
| 2 | `book_physics; C=1; p>=0.95; ask<=100; sec>=0` | 98.64% | 94.23% | 100.00% | 96.77% | 100.00% | 93.75% | 88.65% | 88.65% | True | True | False |
| 3 | `book_physics_price; C=1; p>=0.95; ask<=100; sec>=0` | 98.64% | 94.23% | 100.00% | 93.55% | 100.00% | 90.62% | 88.30% | 88.30% | True | True | False |
| 4 | `book_physics_price; C=0.1; p>=0.95; ask<=100; sec>=0` | 98.64% | 94.23% | 100.00% | 93.55% | 100.00% | 90.62% | 88.30% | 88.30% | True | True | False |
| 5 | `book_physics; C=0.3; p>=0.95; ask<=100; sec>=0` | 98.62% | 92.95% | 100.00% | 93.55% | 100.00% | 90.62% | 88.30% | 88.30% | True | True | False |
| 6 | `book_physics_price; C=0.3; p>=0.95; ask<=100; sec>=0` | 98.62% | 92.95% | 100.00% | 90.32% | 100.00% | 87.50% | 87.94% | 87.94% | True | True | False |
| 7 | `book_physics; C=0.1; p>=0.95; ask<=100; sec>=0` | 98.60% | 91.67% | 100.00% | 93.55% | 100.00% | 87.50% | 88.30% | 87.94% | True | True | False |
| 8 | `book_physics; C=0.05; p>=0.95; ask<=100; sec>=0` | 98.59% | 91.03% | 100.00% | 93.55% | 100.00% | 87.50% | 88.30% | 87.94% | True | True | False |
| 9 | `physics_no_book_price; C=0.05; p>=0.95; ask<=100; sec>=0` | 97.86% | 89.74% | 96.55% | 93.55% | 100.00% | 81.25% | 82.82% | 87.13% | True | True | False |
| 10 | `physics_no_book_price; C=0.3; p>=0.95; ask<=100; sec>=0` | 97.18% | 91.03% | 93.33% | 96.77% | 100.00% | 84.38% | 78.68% | 87.54% | True | False | False |
| 11 | `physics_no_book_price; C=1; p>=0.95; ask<=100; sec>=0` | 95.77% | 91.03% | 93.33% | 96.77% | 96.30% | 84.38% | 78.68% | 81.72% | True | False | False |
| 12 | `physics_no_book_price; C=0.1; p>=0.95; ask<=100; sec>=0` | 97.14% | 89.74% | 93.10% | 93.55% | 100.00% | 81.25% | 78.04% | 87.13% | True | False | False |

## 80%-Coverage Policies

| rank | policy | all acc | all cov | val acc | val cov | holdout acc | holdout cov | val Wilson | holdout Wilson | train-picked | target | Wilson pass |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| 1 | `book_physics_price; C=0.05; p>=0.95; ask<=100; sec>=0` | 99.31% | 92.95% | 100.00% | 93.55% | 100.00% | 90.62% | 88.30% | 88.30% | True | True | False |
| 2 | `book_physics; C=1; p>=0.95; ask<=100; sec>=0` | 98.64% | 94.23% | 100.00% | 96.77% | 100.00% | 93.75% | 88.65% | 88.65% | True | True | False |
| 3 | `book_physics_price; C=1; p>=0.95; ask<=100; sec>=0` | 98.64% | 94.23% | 100.00% | 93.55% | 100.00% | 90.62% | 88.30% | 88.30% | True | True | False |
| 4 | `book_physics_price; C=0.1; p>=0.95; ask<=100; sec>=0` | 98.64% | 94.23% | 100.00% | 93.55% | 100.00% | 90.62% | 88.30% | 88.30% | True | True | False |
| 5 | `book_physics; C=0.3; p>=0.95; ask<=100; sec>=0` | 98.62% | 92.95% | 100.00% | 93.55% | 100.00% | 90.62% | 88.30% | 88.30% | True | True | False |
| 6 | `book_physics_price; C=0.3; p>=0.95; ask<=100; sec>=0` | 98.62% | 92.95% | 100.00% | 90.32% | 100.00% | 87.50% | 87.94% | 87.94% | True | True | False |
| 7 | `book_physics; C=0.1; p>=0.95; ask<=100; sec>=0` | 98.60% | 91.67% | 100.00% | 93.55% | 100.00% | 87.50% | 88.30% | 87.94% | True | True | False |
| 8 | `book_physics; C=0.05; p>=0.95; ask<=100; sec>=0` | 98.59% | 91.03% | 100.00% | 93.55% | 100.00% | 87.50% | 88.30% | 87.94% | True | True | False |
| 9 | `physics_no_book_price; C=0.05; p>=0.95; ask<=100; sec>=0` | 97.86% | 89.74% | 96.55% | 93.55% | 100.00% | 81.25% | 82.82% | 87.13% | True | True | False |
| 10 | `physics_no_book_price; C=0.3; p>=0.95; ask<=100; sec>=0` | 97.18% | 91.03% | 93.33% | 96.77% | 100.00% | 84.38% | 78.68% | 87.54% | True | False | False |
| 11 | `physics_no_book_price; C=1; p>=0.95; ask<=100; sec>=0` | 95.77% | 91.03% | 93.33% | 96.77% | 96.30% | 84.38% | 78.68% | 81.72% | True | False | False |
| 12 | `physics_no_book_price; C=0.1; p>=0.95; ask<=100; sec>=0` | 97.14% | 89.74% | 93.10% | 93.55% | 100.00% | 81.25% | 78.04% | 87.13% | True | False | False |
| 13 | `physics_no_book_price; C=1; p>=0.9; ask<=100; sec>=60` | 93.18% | 84.62% | 89.29% | 90.32% | 96.00% | 78.12% | 72.80% | 80.46% | False | False | False |
| 14 | `physics_no_book_price; C=0.3; p>=0.9; ask<=100; sec>=60` | 92.48% | 85.26% | 89.29% | 90.32% | 92.31% | 81.25% | 72.80% | 75.86% | False | False | False |
| 15 | `physics_no_book_price; C=1; p>=0.9; ask<=100; sec>=0` | 93.29% | 95.51% | 87.10% | 100.00% | 96.67% | 93.75% | 71.15% | 83.33% | False | False | False |
| 16 | `physics_no_book_price; C=0.3; p>=0.9; ask<=100; sec>=0` | 92.67% | 96.15% | 87.10% | 100.00% | 93.55% | 96.88% | 71.15% | 79.28% | False | False | False |
| 17 | `book_physics; C=0.3; p>=0.9; ask<=100; sec>=60` | 92.16% | 98.08% | 87.10% | 100.00% | 93.33% | 93.75% | 71.15% | 78.68% | False | False | False |
| 18 | `book_physics; C=1; p>=0.9; ask<=100; sec>=60` | 92.16% | 98.08% | 87.10% | 100.00% | 93.33% | 93.75% | 71.15% | 78.68% | False | False | False |
| 19 | `book_physics_price; C=1; p>=0.9; ask<=100; sec>=60` | 92.16% | 98.08% | 87.10% | 100.00% | 93.33% | 93.75% | 71.15% | 78.68% | False | False | False |
| 20 | `book_physics; C=0.3; p>=0.9; ask<=95; sec>=60` | 92.00% | 96.15% | 87.10% | 100.00% | 93.10% | 90.62% | 71.15% | 78.04% | False | False | False |

## Read

- Best forward-ranked learned policy: `book_physics_price; C=0.05; p>=0.95; ask<=100; sec>=0`.
- It selected 145/156 intervals (92.95%) at 99.31% accuracy.
- validation: 100.00% accuracy at 93.55% coverage; needs 0 additional selected losses blocked without losing wins to reach 95%.
- holdout: 100.00% accuracy at 90.62% coverage; needs 0 additional selected losses blocked without losing wins to reach 95%.
- No chronological logistic policy produced a sample-size-safe 95% Wilson lower bound across splits.
