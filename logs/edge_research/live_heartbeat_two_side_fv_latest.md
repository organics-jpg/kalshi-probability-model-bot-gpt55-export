# Live Heartbeat Two-sided FV Probe

Generated UTC: `20260505_054123Z`

## Scope

- Research-only probe; no orders are submitted and no bot files are modified.
- Source: live websocket heartbeat rows from `logs/live_mushroom_v28_size2/bot.log`.
- Each heartbeat contributes both YES and NO candidate sides; score families choose one side or skip.
- BTC spot and realized-volatility physics use cached/refreshed Coinbase 1m candles.
- This is broad live telemetry, not fresh filled-trade completion evidence.

## Coverage

- Raw two-sided rows: 44442
- Rows with candle physics: 42932
- Unique markets with physics: 372
- Candle rows: 75024
- Candle range: 2026-03-14T00:54:59.999000+00:00 to 2026-05-05T03:22:59.999000+00:00

## Mode Results

### `two_side_minute_bucket`

- Opportunity rows: 5532
- Side candidate rows: 11064
- Unique markets: 372
- Target-pass models: 0

Perfect side-choice oracle:

| split | retention floor | required opportunities | max accuracy |
|---|---:|---:|---:|
| all | 75.00% | 4149 | 100.00% |
| all | 80.00% | 4426 | 100.00% |
| validation | 75.00% | 830 | 100.00% |
| validation | 80.00% | 885 | 100.00% |
| holdout | 75.00% | 831 | 100.00% |
| holdout | 80.00% | 886 | 100.00% |

Top high-retention side-choice models:

| rank | family | model | all acc | all ret | validation acc | holdout acc | holdout ret | selected | target |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | book | `book_p_side>=0.60; ask<=100` | 85.18% | 76.21% | 86.31% | 85.58% | 77.06% | 4216 | False |
| 2 | min_book_rv15 | `score_min_book_rv15>=0.55; ask<=100` | 84.11% | 79.50% | 84.16% | 84.22% | 79.58% | 4398 | False |
| 3 | brownian_rv30_book_agree | `brownian_p_rv_30m>=0.55; book agrees; ask<=100` | 83.03% | 81.71% | 83.42% | 83.76% | 81.75% | 4520 | False |
| 4 | brownian_rv15_book_agree | `brownian_p_rv_15m>=0.55; book agrees; ask<=100` | 82.83% | 82.77% | 83.01% | 83.63% | 82.20% | 4579 | False |
| 5 | drift_rv15_book_agree | `drift_p_5m_rv_15m>=0.65; book agrees; ask<=100` | 82.82% | 78.20% | 83.73% | 82.89% | 78.68% | 4326 | False |
| 6 | drift_rv15_book_agree | `drift_p_5m_rv_15m>=0.60; book agrees; ask<=100` | 82.40% | 81.06% | 83.51% | 82.41% | 81.12% | 4484 | False |
| 7 | brownian_rv30 | `brownian_p_rv_30m>=0.55; ask<=100` | 82.37% | 83.06% | 82.75% | 83.48% | 82.57% | 4595 | False |
| 8 | brownian_rv15 | `brownian_p_rv_15m>=0.55; ask<=100` | 82.21% | 84.35% | 82.36% | 83.28% | 83.20% | 4666 | False |
| 9 | book | `book_p_side>=0.55; ask<=100` | 82.20% | 87.04% | 82.78% | 82.55% | 87.99% | 4815 | False |
| 10 | mean_book_rv15 | `score_mean_book_rv15>=0.55; ask<=100` | 82.17% | 85.77% | 82.60% | 82.93% | 86.27% | 4745 | False |

Top accuracy models:

| rank | family | model | all acc | all ret | validation acc | holdout acc | holdout ret | selected | target |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | brownian_rv30 | `brownian_p_rv_30m>=0.95; ask<=90` | 100.00% | 0.18% | 100.00% | 100.00% | 0.27% | 10 | False |
| 2 | brownian_rv30_book_agree | `brownian_p_rv_30m>=0.95; book agrees; ask<=90` | 100.00% | 0.18% | 100.00% | 100.00% | 0.27% | 10 | False |
| 3 | book | `book_p_side>=0.90; ask<=90` | 100.00% | 0.25% | 100.00% | 100.00% | 0.18% | 14 | False |
| 4 | mean_book_rv15_drift5 | `score_mean_book_rv15_drift5>=0.95; ask<=90` | 100.00% | 0.18% | 100.00% | 100.00% | 0.09% | 10 | False |
| 5 | book | `book_p_side>=0.95; ask<=100` | 99.31% | 26.07% | 99.70% | 99.03% | 27.91% | 1442 | False |
| 6 | mean_book_rv15 | `score_mean_book_rv15>=0.95; ask<=100` | 98.79% | 22.40% | 99.25% | 98.88% | 24.21% | 1239 | False |
| 7 | min_book_rv15 | `score_min_book_rv15>=0.95; ask<=100` | 99.07% | 19.47% | 99.54% | 98.74% | 21.50% | 1077 | False |
| 8 | brownian_rv30 | `brownian_p_rv_30m>=0.95; ask<=100` | 98.70% | 20.81% | 98.37% | 98.79% | 22.31% | 1151 | False |
| 9 | brownian_rv30_book_agree | `brownian_p_rv_30m>=0.95; book agrees; ask<=100` | 98.70% | 20.81% | 98.37% | 98.79% | 22.31% | 1151 | False |
| 10 | mean_book_rv15_drift5 | `score_mean_book_rv15_drift5>=0.95; ask<=100` | 98.45% | 24.55% | 98.31% | 98.31% | 26.74% | 1358 | False |

### `two_side_first_per_market`

- Opportunity rows: 372
- Side candidate rows: 744
- Unique markets: 372
- Target-pass models: 0

Perfect side-choice oracle:

| split | retention floor | required opportunities | max accuracy |
|---|---:|---:|---:|
| all | 75.00% | 279 | 100.00% |
| all | 80.00% | 298 | 100.00% |
| validation | 75.00% | 56 | 100.00% |
| validation | 80.00% | 60 | 100.00% |
| holdout | 75.00% | 57 | 100.00% |
| holdout | 80.00% | 60 | 100.00% |

Top high-retention side-choice models:

| rank | family | model | all acc | all ret | validation acc | holdout acc | holdout ret | selected | target |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | mean_book_rv15 | `score_mean_book_rv15>=0.50; ask<=100` | 58.87% | 100.00% | 58.11% | 56.00% | 100.00% | 372 | False |
| 2 | mean_book_rv15 | `score_mean_book_rv15>=0.50; ask<=90` | 58.76% | 99.73% | 58.11% | 56.00% | 100.00% | 371 | False |
| 3 | mean_book_rv15 | `score_mean_book_rv15>=0.50; ask<=95` | 58.76% | 99.73% | 58.11% | 56.00% | 100.00% | 371 | False |
| 4 | book | `book_p_side>=0.50; ask<=100` | 59.95% | 100.00% | 52.70% | 65.33% | 100.00% | 372 | False |
| 5 | book | `book_p_side>=0.50; ask<=90` | 59.84% | 99.73% | 52.70% | 65.33% | 100.00% | 371 | False |
| 6 | book | `book_p_side>=0.50; ask<=95` | 59.84% | 99.73% | 52.70% | 65.33% | 100.00% | 371 | False |
| 7 | drift_rv15 | `drift_p_5m_rv_15m>=0.60; ask<=100` | 50.16% | 84.14% | 50.00% | 50.77% | 86.67% | 313 | False |
| 8 | drift_rv15 | `drift_p_5m_rv_15m>=0.60; ask<=90` | 50.00% | 83.87% | 50.00% | 50.77% | 86.67% | 312 | False |
| 9 | drift_rv15 | `drift_p_5m_rv_15m>=0.60; ask<=95` | 50.00% | 83.87% | 50.00% | 50.77% | 86.67% | 312 | False |
| 10 | drift_rv15 | `drift_p_5m_rv_15m>=0.50; ask<=100` | 49.46% | 100.00% | 51.35% | 49.33% | 100.00% | 372 | False |

Top accuracy models:

| rank | family | model | all acc | all ret | validation acc | holdout acc | holdout ret | selected | target |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | min_book_rv15 | `score_min_book_rv15>=0.65; ask<=100` | 100.00% | 1.88% | 100.00% | 100.00% | 2.67% | 7 | False |
| 2 | min_book_rv15 | `score_min_book_rv15>=0.65; ask<=90` | 100.00% | 1.61% | 100.00% | 100.00% | 2.67% | 6 | False |
| 3 | min_book_rv15 | `score_min_book_rv15>=0.65; ask<=95` | 100.00% | 1.61% | 100.00% | 100.00% | 2.67% | 6 | False |
| 4 | mean_book_rv15 | `score_mean_book_rv15>=0.70; ask<=100` | 100.00% | 1.08% | 100.00% | 100.00% | 1.33% | 4 | False |
| 5 | mean_book_rv15 | `score_mean_book_rv15>=0.70; ask<=90` | 100.00% | 0.81% | 100.00% | 100.00% | 1.33% | 3 | False |
| 6 | mean_book_rv15 | `score_mean_book_rv15>=0.70; ask<=95` | 100.00% | 0.81% | 100.00% | 100.00% | 1.33% | 3 | False |
| 7 | book | `book_p_side>=0.65; ask<=100` | 70.59% | 13.71% | 83.33% | 72.73% | 14.67% | 51 | False |
| 8 | book | `book_p_side>=0.65; ask<=90` | 70.00% | 13.44% | 83.33% | 72.73% | 14.67% | 50 | False |
| 9 | book | `book_p_side>=0.65; ask<=95` | 70.00% | 13.44% | 83.33% | 72.73% | 14.67% | 50 | False |
| 10 | book | `book_p_side>=0.60; ask<=100` | 63.00% | 26.88% | 64.00% | 72.22% | 24.00% | 100 | False |

### `two_side_all_heartbeats`

- Opportunity rows: 21466
- Side candidate rows: 42932
- Unique markets: 372
- Target-pass models: 0

Perfect side-choice oracle:

| split | retention floor | required opportunities | max accuracy |
|---|---:|---:|---:|
| all | 75.00% | 16100 | 100.00% |
| all | 80.00% | 17173 | 100.00% |
| validation | 75.00% | 3220 | 100.00% |
| validation | 80.00% | 3435 | 100.00% |
| holdout | 75.00% | 3221 | 100.00% |
| holdout | 80.00% | 3436 | 100.00% |

Top high-retention side-choice models:

| rank | family | model | all acc | all ret | validation acc | holdout acc | holdout ret | selected | target |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | mean_book_rv15 | `score_mean_book_rv15>=0.60; ask<=100` | 87.02% | 76.77% | 87.92% | 86.59% | 77.95% | 16479 | False |
| 2 | book | `book_p_side>=0.60; ask<=100` | 86.32% | 79.65% | 87.42% | 86.23% | 80.83% | 17098 | False |
| 3 | mean_book_rv15_drift5 | `score_mean_book_rv15_drift5>=0.65; ask<=100` | 86.09% | 75.96% | 87.27% | 85.94% | 76.50% | 16306 | False |
| 4 | min_book_rv15 | `score_min_book_rv15>=0.55; ask<=100` | 85.71% | 79.25% | 86.07% | 85.55% | 79.46% | 17012 | False |
| 5 | drift_rv15_book_agree | `drift_p_5m_rv_15m>=0.70; book agrees; ask<=100` | 84.83% | 75.13% | 86.31% | 84.49% | 75.55% | 16128 | False |
| 6 | brownian_rv30_book_agree | `brownian_p_rv_30m>=0.55; book agrees; ask<=100` | 84.40% | 81.78% | 85.09% | 84.74% | 81.97% | 17554 | False |
| 7 | brownian_rv15_book_agree | `brownian_p_rv_15m>=0.55; book agrees; ask<=100` | 84.33% | 82.53% | 84.95% | 84.59% | 82.35% | 17715 | False |
| 8 | drift_rv15_book_agree | `drift_p_5m_rv_15m>=0.65; book agrees; ask<=100` | 84.26% | 78.50% | 85.39% | 83.92% | 79.23% | 16851 | False |
| 9 | mean_book_rv15 | `score_mean_book_rv15>=0.55; ask<=100` | 83.53% | 87.52% | 84.38% | 83.73% | 88.61% | 18787 | False |
| 10 | drift_rv15_book_agree | `drift_p_5m_rv_15m>=0.60; book agrees; ask<=100` | 83.81% | 81.30% | 85.19% | 83.40% | 81.39% | 17451 | False |

Top accuracy models:

| rank | family | model | all acc | all ret | validation acc | holdout acc | holdout ret | selected | target |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | min_book_rv15 | `score_min_book_rv15>=0.95; ask<=100` | 99.19% | 21.77% | 99.58% | 98.73% | 23.82% | 4673 | False |
| 2 | book | `book_p_side>=0.95; ask<=100` | 99.22% | 29.25% | 99.51% | 98.68% | 31.65% | 6279 | False |
| 3 | mean_book_rv15 | `score_mean_book_rv15>=0.95; ask<=100` | 98.89% | 24.80% | 99.22% | 98.42% | 26.57% | 5323 | False |
| 4 | brownian_rv30 | `brownian_p_rv_30m>=0.95; ask<=100` | 98.56% | 23.31% | 98.22% | 98.71% | 25.24% | 5003 | False |
| 5 | brownian_rv30_book_agree | `brownian_p_rv_30m>=0.95; book agrees; ask<=100` | 98.58% | 23.30% | 98.22% | 98.71% | 25.24% | 5002 | False |
| 6 | mean_book_rv15_drift5 | `score_mean_book_rv15_drift5>=0.95; ask<=100` | 98.52% | 27.06% | 98.27% | 97.99% | 29.02% | 5809 | False |
| 7 | min_book_rv15 | `score_min_book_rv15>=0.90; ask<=100` | 98.54% | 29.42% | 98.26% | 97.94% | 30.53% | 6315 | False |
| 8 | brownian_rv15 | `brownian_p_rv_15m>=0.95; ask<=100` | 98.22% | 24.09% | 98.11% | 97.85% | 25.99% | 5171 | False |
| 9 | brownian_rv15_book_agree | `brownian_p_rv_15m>=0.95; book agrees; ask<=100` | 98.30% | 24.06% | 98.11% | 97.85% | 25.99% | 5165 | False |
| 10 | mean_book_rv15 | `score_mean_book_rv15>=0.90; ask<=100` | 98.33% | 33.45% | 98.23% | 97.73% | 34.93% | 7180 | False |

## Completion Read

The primary two-sided heartbeat tape does not produce a simple non-overfit 95% / 75% side-choice model.
This falsifies the idea that merely allowing contrarian side choice fixes the current FV prior at high volume.
