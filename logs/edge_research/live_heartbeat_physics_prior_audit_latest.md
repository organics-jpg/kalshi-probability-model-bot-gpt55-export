# Live Heartbeat Physics Prior Audit

Generated UTC: `20260502_135132Z`

## Scope

- Research-only probe; no orders are submitted and no bot files are modified.
- Source: live websocket heartbeat rows from `logs/live_mushroom_v28_size2/bot.log`.
- Candidate side is the book favorite at each heartbeat, bucketed by mode.
- BTC spot and realized-volatility physics use the cached Coinbase 1m candle file.
- This is not filled-trade completion evidence; heartbeat rows are correlated market states.

## Coverage

- Raw favorite heartbeat rows: 8289
- Rows with candle physics: 8265
- Unique markets with physics: 142
- Candle rows: 71328
- Candle range: 2026-03-14T00:54:59.999000+00:00 to 2026-05-02T13:46:59.999000+00:00

## Mode Results

### `favorite_minute_bucket`

- Rows: 2129
- Unique markets: 142
- Baseline all favorite accuracy: 1636/2129 = 76.84%
- Baseline holdout favorite accuracy: 339/426 = 79.58%
- Target-pass rules: 0

Perfect-selector oracle bounds:

| split | retention floor | required rows | max accuracy | 95% possible |
|---|---:|---:|---:|---|
| all | 75.00% | 1597 | 100.00% | True |
| all | 80.00% | 1704 | 96.01% | True |
| validation | 75.00% | 320 | 91.88% | False |
| validation | 80.00% | 341 | 86.22% | False |
| holdout | 75.00% | 320 | 100.00% | True |
| holdout | 80.00% | 341 | 99.41% | True |

Top high-retention rules:

| rank | family | rule | all acc | all ret | validation acc | holdout acc | holdout ret | rows | target |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | brownian_rv30 | `Phi(margin/rv30)>=0.55` | 81.23% | 80.84% | 74.34% | 84.35% | 80.99% | 1721 | False |
| 2 | brownian_rv15 | `Phi(margin/rv15)>=0.55` | 80.88% | 82.06% | 73.85% | 83.52% | 82.63% | 1747 | False |
| 3 | adverse_drift_guard | `book_mid>=0.50; block adverse15>10` | 79.82% | 79.85% | 73.57% | 81.10% | 80.75% | 1700 | False |
| 4 | drift_rv15 | `drift_p_5m_rv15>=0.65` | 81.39% | 77.22% | 73.23% | 85.23% | 76.29% | 1644 | False |
| 5 | drift_rv15 | `drift_p_5m_rv15>=0.60` | 80.81% | 80.27% | 73.16% | 85.37% | 78.64% | 1709 | False |
| 6 | book_probability_spread | `book_mid>=0.55; spread<=2` | 80.93% | 85.20% | 72.63% | 83.99% | 83.57% | 1814 | False |
| 7 | sqrt_time_boundary | `margin/sqrt(sec)>=0.25` | 80.30% | 84.64% | 72.42% | 85.04% | 80.05% | 1802 | False |
| 8 | book_probability_spread | `book_mid>=0.55; spread<=5` | 80.74% | 85.58% | 72.22% | 83.43% | 84.98% | 1822 | False |
| 9 | book_probability | `book_mid>=0.55` | 80.70% | 85.67% | 72.02% | 83.43% | 84.98% | 1824 | False |
| 10 | book_probability_spread | `book_mid>=0.55; spread<=10` | 80.70% | 85.67% | 72.02% | 83.43% | 84.98% | 1824 | False |

### `favorite_first_per_market`

- Rows: 142
- Unique markets: 142
- Baseline all favorite accuracy: 89/142 = 62.68%
- Baseline holdout favorite accuracy: 18/29 = 62.07%
- Target-pass rules: 0

Perfect-selector oracle bounds:

| split | retention floor | required rows | max accuracy | 95% possible |
|---|---:|---:|---:|---|
| all | 75.00% | 107 | 83.18% | False |
| all | 80.00% | 114 | 78.07% | False |
| validation | 75.00% | 21 | 66.67% | False |
| validation | 80.00% | 23 | 60.87% | False |
| holdout | 75.00% | 22 | 81.82% | False |
| holdout | 80.00% | 24 | 75.00% | False |

Top high-retention rules:

| rank | family | rule | all acc | all ret | validation acc | holdout acc | holdout ret | rows | target |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | adverse_drift_guard | `book_mid>=0.50; block adverse15>75` | 66.09% | 80.99% | 56.00% | 60.00% | 86.21% | 115 | False |
| 2 | book_probability_spread | `book_mid>=0.50; spread<=2` | 63.57% | 98.59% | 51.85% | 64.29% | 96.55% | 140 | False |
| 3 | adverse_drift_guard | `book_mid>=0.50; block adverse15>100` | 64.29% | 88.73% | 51.85% | 60.71% | 96.55% | 126 | False |
| 4 | sqrt_time_boundary | `margin/sqrt(sec)>=-0.5` | 63.64% | 92.96% | 50.00% | 64.29% | 96.55% | 132 | False |
| 5 | book_probability | `book_mid>=0.50` | 62.68% | 100.00% | 50.00% | 62.07% | 100.00% | 142 | False |
| 6 | book_probability_spread | `book_mid>=0.50; spread<=5` | 62.68% | 100.00% | 50.00% | 62.07% | 100.00% | 142 | False |
| 7 | book_probability_spread | `book_mid>=0.50; spread<=10` | 62.68% | 100.00% | 50.00% | 62.07% | 100.00% | 142 | False |
| 8 | realized_vol_cushion | `margin/rv15>=-1` | 62.68% | 100.00% | 50.00% | 62.07% | 100.00% | 142 | False |
| 9 | realized_vol_cushion | `margin/rv15>=-0.5` | 62.68% | 100.00% | 50.00% | 62.07% | 100.00% | 142 | False |
| 10 | sqrt_time_boundary | `margin/sqrt(sec)>=-1` | 62.14% | 98.59% | 50.00% | 62.07% | 100.00% | 140 | False |

### `favorite_all_heartbeats`

- Rows: 8265
- Unique markets: 142
- Baseline all favorite accuracy: 6476/8265 = 78.35%
- Baseline holdout favorite accuracy: 1331/1653 = 80.52%
- Target-pass rules: 0

Perfect-selector oracle bounds:

| split | retention floor | required rows | max accuracy | 95% possible |
|---|---:|---:|---:|---|
| all | 75.00% | 6199 | 100.00% | True |
| all | 80.00% | 6612 | 97.94% | True |
| validation | 75.00% | 1240 | 94.68% | False |
| validation | 80.00% | 1323 | 88.74% | False |
| holdout | 75.00% | 1240 | 100.00% | True |
| holdout | 80.00% | 1323 | 100.00% | True |

Top high-retention rules:

| rank | family | rule | all acc | all ret | validation acc | holdout acc | holdout ret | rows | target |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | book_probability_spread | `book_mid>=0.60; spread<=5` | 85.18% | 76.82% | 78.41% | 86.95% | 77.43% | 6349 | False |
| 2 | book_probability | `book_mid>=0.60` | 85.18% | 76.89% | 78.40% | 86.95% | 77.43% | 6355 | False |
| 3 | book_probability_spread | `book_mid>=0.60; spread<=10` | 85.17% | 76.88% | 78.38% | 86.95% | 77.43% | 6354 | False |
| 4 | book_probability_spread | `book_mid>=0.60; spread<=2` | 85.18% | 76.48% | 78.26% | 87.09% | 76.83% | 6321 | False |
| 5 | brownian_rv15 | `Phi(margin/rv15)>=0.55` | 82.43% | 81.62% | 75.51% | 84.67% | 82.88% | 6746 | False |
| 6 | brownian_rv30 | `Phi(margin/rv30)>=0.55` | 82.65% | 80.81% | 75.43% | 85.23% | 81.91% | 6679 | False |
| 7 | adverse_drift_guard | `book_mid>=0.50; block adverse15>10` | 81.23% | 79.54% | 75.37% | 82.01% | 80.70% | 6574 | False |
| 8 | drift_rv15 | `drift_p_5m_rv15>=0.65` | 82.80% | 77.22% | 75.28% | 86.49% | 76.10% | 6382 | False |
| 9 | drift_rv15 | `drift_p_5m_rv15>=0.60` | 82.19% | 80.18% | 74.81% | 86.34% | 78.83% | 6627 | False |
| 10 | sqrt_time_boundary | `margin/sqrt(sec)>=0.25` | 81.85% | 83.77% | 74.09% | 85.61% | 81.13% | 6924 | False |

## Calibration

### `book_p_side`

| bin | rows | wins | realized accuracy |
|---|---:|---:|---:|
| [0.5, 0.6) | 565 | 323 | 57.17% |
| [0.6, 0.7) | 356 | 233 | 65.45% |
| [0.7, 0.8) | 285 | 208 | 72.98% |
| [0.8, 0.9) | 266 | 226 | 84.96% |
| >=0.9 | 657 | 646 | 98.33% |

### `brownian_p_rv_15m`

| bin | rows | wins | realized accuracy |
|---|---:|---:|---:|
| [0.25, 0.5) | 149 | 91 | 61.07% |
| [0.5, 0.75) | 1035 | 664 | 64.15% |
| [0.75, 0.9) | 367 | 310 | 84.47% |
| >=0.9 | 578 | 571 | 98.79% |

### `book_minus_brownian_rv15`

| bin | rows | wins | realized accuracy |
|---|---:|---:|---:|
| [-0.25, 0) | 721 | 542 | 75.17% |
| [0, 0.25) | 1396 | 1084 | 77.65% |
| [0.25, 0.5) | 12 | 10 | 83.33% |

## Completion Read

The primary heartbeat tape does not produce a non-overfit 95% / 75% selector under the configured chronological split and sample checks.
Use this artifact to falsify priors and design the next FV surface; use locked fresh fills to complete the active goal.
