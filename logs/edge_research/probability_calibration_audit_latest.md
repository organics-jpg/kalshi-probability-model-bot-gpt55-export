# Probability Calibration Audit

Generated UTC: `20260504_101005Z`

## Scope

- Research-only calibration audit; no orders are submitted and no bot files or live processes are touched.
- Calibrations are pooled current+v21 train-only logit fits.
- EV floor is selected using train rows only, then evaluated on validation/holdout.

## Calibration Fits

| model | alpha | beta | train raw/cal logloss | validation raw/cal logloss | holdout raw/cal logloss |
|---|---:|---:|---:|---:|---:|
| `book` | 0.200 | 0.750 | 0.6704/0.6680 | 0.6833/0.6909 | 0.6510/0.6509 |
| `brownian15` | 0.200 | 0.350 | 0.6852/0.6815 | 0.7103/0.7159 | 0.6844/0.6830 |
| `brownian30` | 0.200 | 0.325 | 0.6860/0.6817 | 0.7084/0.7147 | 0.6817/0.6821 |
| `mean_book_rv15` | 0.300 | 0.700 | 0.6727/0.6660 | 0.6928/0.6998 | 0.6618/0.6519 |
| `min_book_rv15` | 0.350 | 1.600 | 0.6769/0.6577 | 0.7036/0.7204 | 0.6794/0.6511 |
| `regime_blend` | -0.150 | 1.075 | 0.6790/0.6774 | 0.7213/0.7186 | 0.6714/0.6686 |

## Train-Selected EV Gates

Coverage floor: `75.00%` on validation and holdout.

| dataset | model | edge floor | val net/cov | holdout net/cov | all net/ROI | OOS pass |
|---|---|---:|---:|---:|---:|---|
| current | `book` | -50.0c | -716.0c/100.00% | -187.0c/100.00% | -430.0c/-2.36% | False |
| v21 | `book` | -50.0c | 127.0c/100.00% | 249.0c/97.78% | 60.0c/0.46% | True |
| current | `brownian15` | -15.0c | -953.0c/100.00% | -337.0c/98.39% | -1736.0c/-10.44% | False |
| v21 | `brownian15` | -15.0c | -54.0c/100.00% | 450.0c/95.56% | 1584.0c/13.29% | False |
| current | `brownian30` | -15.0c | -953.0c/100.00% | -337.0c/98.39% | -1736.0c/-10.44% | False |
| v21 | `brownian30` | -15.0c | -54.0c/100.00% | 450.0c/95.56% | 1584.0c/13.29% | False |
| current | `mean_book_rv15` | 2.0c | -438.0c/88.52% | 159.0c/93.55% | 298.0c/1.91% | False |
| v21 | `mean_book_rv15` | 2.0c | 41.0c/88.64% | 304.0c/84.44% | 1139.0c/11.10% | True |
| current | `min_book_rv15` | 5.0c | -407.0c/100.00% | -168.0c/100.00% | 200.0c/1.08% | False |
| v21 | `min_book_rv15` | 5.0c | -235.0c/100.00% | 283.0c/95.56% | 758.0c/5.81% | False |
| current | `regime_blend` | -10.0c | -428.0c/100.00% | -745.0c/100.00% | -1608.0c/-9.29% | False |
| v21 | `regime_blend` | -10.0c | 61.0c/100.00% | 269.0c/97.78% | 886.0c/7.14% | True |

## Read

- `book` train-selected OOS pass/min val cov/min holdout cov/combined OOS net: False/100.00%/97.78%/-527.0c.
- `brownian15` train-selected OOS pass/min val cov/min holdout cov/combined OOS net: False/100.00%/95.56%/-894.0c.
- `brownian30` train-selected OOS pass/min val cov/min holdout cov/combined OOS net: False/100.00%/95.56%/-894.0c.
- `mean_book_rv15` train-selected OOS pass/min val cov/min holdout cov/combined OOS net: False/88.52%/84.44%/66.0c.
- `min_book_rv15` train-selected OOS pass/min val cov/min holdout cov/combined OOS net: False/100.00%/95.56%/-527.0c.
- `regime_blend` train-selected OOS pass/min val cov/min holdout cov/combined OOS net: False/100.00%/97.78%/-843.0c.
- No train-selected calibrated prior clears positive high-coverage OOS on both datasets.
