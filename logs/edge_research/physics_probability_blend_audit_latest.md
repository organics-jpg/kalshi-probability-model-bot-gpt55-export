# Physics Probability Blend Audit

Generated UTC: `20260504_065146Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Tests small fixed blends of book terminal probability, realized-vol Brownian terminal probability, first-passage/touch survival, and disagreement penalties.
- For each blend, the EV floor is selected using train splits only; validation/holdout are not used for selection.
- Strict coverage target: `80.00%`. Loose diagnostic floor: `75.00%`.

## Diagnostics

- Current markets: 295
- V21 markets: 221
- Models: 17
- EV floors per model: 13
- Train-selected strict 80% OOS pass rows: 0
- Train-selected loose 75% OOS pass rows: 0
- Diagnostic all-floor strict 80% OOS pass rows: 3

## Train-Selected Blends

| model | EV floor | min train/oos cov | train net | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | OOS positive | strict OOS cov |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| `mean_book_rv15` | -5.0c | 98.48%/97.78% | 1243.0c | 130.0c/0.74% | 60.07%/99.32% | 1243.0c/9.67% | 64.68%/98.64% | False | True |
| `logit_book_rv_hazard_mean` | -15.0c | 99.24%/98.31% | 1123.0c | 285.0c/1.64% | 60.20%/99.66% | 1056.0c/8.16% | 63.64%/99.55% | False | True |
| `mean_minus_half_disagreement` | -20.0c | 99.24%/97.78% | 1403.0c | 153.0c/0.88% | 59.52%/99.66% | 1161.0c/9.04% | 63.93%/99.10% | False | True |
| `book_hazard_50_50` | -15.0c | 99.24%/97.78% | 1220.0c | 252.0c/1.40% | 62.12%/99.32% | 1040.0c/7.84% | 65.30%/99.10% | False | True |
| `logit_book_hazard_mean` | -30.0c | 100.00%/98.31% | 1029.0c | 120.0c/0.69% | 59.86%/99.66% | 1026.0c/7.85% | 63.80%/100.00% | False | True |
| `hazard_discounted_mean15` | -30.0c | 99.24%/97.78% | 1526.0c | -120.0c/-0.69% | 58.50%/99.66% | 1258.0c/9.80% | 64.38%/99.10% | False | True |
| `book_rv_hazard_min` | -30.0c | 99.24%/97.78% | 1526.0c | -120.0c/-0.69% | 58.50%/99.66% | 1258.0c/9.80% | 64.38%/99.10% | False | True |
| `scoremin_hazard_min` | -30.0c | 99.24%/97.78% | 1526.0c | -120.0c/-0.69% | 58.50%/99.66% | 1258.0c/9.80% | 64.38%/99.10% | False | True |
| `hazard_kinetic_min` | -30.0c | 99.24%/97.78% | 1526.0c | -120.0c/-0.69% | 58.50%/99.66% | 1258.0c/9.80% | 64.38%/99.10% | False | True |
| `book_hazard_30_70` | -20.0c | 99.24%/97.78% | 1150.0c | 72.0c/0.40% | 61.09%/99.32% | 959.0c/7.30% | 64.38%/99.10% | False | True |
| `min_book_rv15` | -10.0c | 99.24%/97.78% | 965.0c | 140.0c/0.80% | 59.86%/99.66% | 783.0c/6.06% | 62.56%/99.10% | False | True |
| `book_rv_hazard_mean` | -15.0c | 99.24%/98.31% | 831.0c | 99.0c/0.57% | 59.52%/99.66% | 762.0c/5.89% | 62.27%/99.55% | False | True |
| `book_hazard_70_30` | -10.0c | 99.24%/97.78% | 1376.0c | -48.0c/-0.27% | 61.43%/99.32% | 893.0c/6.66% | 65.30%/99.10% | False | True |
| `mean_minus_disagreement` | -30.0c | 99.24%/98.31% | 771.0c | -277.0c/-1.59% | 58.16%/99.66% | 755.0c/5.88% | 61.82%/99.55% | False | True |
| `hazard_kinetic_mean` | -15.0c | 99.24%/97.78% | 890.0c | -1600.0c/-9.30% | 53.24%/99.32% | 1847.0c/14.26% | 67.58%/99.10% | False | True |
| `brownian15` | -20.0c | 99.24%/98.31% | 878.0c | -1463.0c/-9.05% | 50.00%/99.66% | 1518.0c/12.56% | 61.82%/99.55% | False | True |
| `book` | -5.0c | 100.00%/98.31% | 170.0c | -467.0c/-2.66% | 58.16%/99.66% | -94.0c/-0.71% | 59.28%/100.00% | False | True |

## Diagnostic Strict OOS Rows

| model | EV floor | min train/oos cov | train net | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | OOS positive | strict OOS cov |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| `logit_book_rv_hazard_mean` | -10.0c | 99.24%/97.78% | 298.0c | 149.0c/0.83% | 62.12%/99.32% | 788.0c/5.75% | 66.21%/99.10% | True | True |
| `logit_book_hazard_mean` | -10.0c | 98.31%/91.11% | -257.0c | 442.0c/2.18% | 71.38%/98.31% | 445.0c/2.77% | 76.74%/97.29% | True | True |
| `book_hazard_50_50` | -10.0c | 96.97%/88.89% | -162.0c | 358.0c/1.77% | 71.28%/97.97% | 494.0c/3.11% | 77.73%/95.48% | True | True |

- These rows are diagnostics, not locks, because the row itself is visible only after scanning validation/holdout.

## Read

- No train-selected blend clears positive validation/holdout P&L on both datasets at the required high coverage.
- If the hazard trial survives forward samples, the useful physics prior is likely barrier/touch survival plus explicit uncertainty shrinkage, not raw Brownian terminal confidence.
