# Cross-Dataset Interval Model Transfer

Generated UTC: `20260502_181938Z`

## Scope

- Research-only probe; no orders are submitted and no bot files or live processes are touched.
- Models train on one live websocket capture's chronological train split and are evaluated on the other capture without retraining.
- Volume denominator is recurring BTC 15-minute markets.
- Candidate gates are fixed probability/ask/time thresholds applied after scoring.

## Data

- Current intervals: 156
- Current side rows: 18034
- V21 intervals: 221
- V21 side rows: 6554
- Candidate rows evaluated: 2304
- Transfer target-pass rows: 0
- Transfer Wilson-pass rows: 0
- Nondegenerate transfer target-pass rows: 0

## Best Transfer Rows

| rank | direction | model | features | gate | transfer | nondeg | source acc/cov | target acc/cov | target holdout acc/cov | median ask |
|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|
| 1 | v21_to_current | logit_C0.1 | path_physics | `p>=0.95; ask<=100; sec>=0` | False | False | 98.00%/67.87% | 100.00%/89.10% | 100.00%/81.25% | 99.0 |
| 2 | v21_to_current | logit_C0.03 | path_physics | `p>=0.95; ask<=100; sec>=0` | False | False | 100.00%/61.54% | 100.00%/87.82% | 100.00%/81.25% | 99.0 |
| 3 | v21_to_current | logit_C0.03 | book_physics_price | `p>=0.95; ask<=100; sec>=0` | False | False | 100.00%/60.63% | 100.00%/87.18% | 100.00%/81.25% | 99.0 |
| 4 | v21_to_current | logit_C0.3 | physics_only | `p>=0.98; ask<=100; sec>=0` | False | False | 100.00%/56.56% | 100.00%/86.54% | 100.00%/81.25% | 99.0 |
| 5 | v21_to_current | logit_C0.3 | book_physics | `p>=0.98; ask<=100; sec>=0` | False | False | 100.00%/55.20% | 100.00%/86.54% | 100.00%/81.25% | 100.0 |
| 6 | v21_to_current | logit_C0.3 | path_physics | `p>=0.98; ask<=100; sec>=0` | False | False | 100.00%/53.85% | 100.00%/85.90% | 100.00%/81.25% | 100.0 |
| 7 | v21_to_current | logit_C0.3 | book_physics_price | `p>=0.98; ask<=100; sec>=0` | False | False | 100.00%/52.04% | 100.00%/85.26% | 100.00%/81.25% | 100.0 |
| 8 | v21_to_current | logit_C0.1 | physics_only | `p>=0.98; ask<=100; sec>=0` | False | False | 100.00%/53.39% | 100.00%/85.26% | 100.00%/81.25% | 100.0 |
| 9 | v21_to_current | logit_C0.1 | book_physics | `p>=0.98; ask<=100; sec>=0` | False | False | 100.00%/52.04% | 100.00%/84.62% | 100.00%/81.25% | 100.0 |
| 10 | v21_to_current | logit_C0.3 | book_physics | `p>=0.95; ask<=100; sec>=0` | False | False | 97.42%/70.14% | 99.28%/89.10% | 100.00%/81.25% | 98.0 |
| 11 | v21_to_current | logit_C0.3 | book_physics_price | `p>=0.95; ask<=100; sec>=0` | False | False | 96.77%/70.14% | 99.28%/89.10% | 100.00%/81.25% | 98.0 |
| 12 | v21_to_current | logit_C0.3 | path_physics | `p>=0.95; ask<=100; sec>=0` | False | False | 96.84%/71.49% | 99.28%/89.10% | 100.00%/81.25% | 98.0 |
| 13 | v21_to_current | logit_C0.1 | book_physics | `p>=0.95; ask<=100; sec>=0` | False | False | 98.00%/67.87% | 99.28%/89.10% | 100.00%/81.25% | 98.0 |
| 14 | v21_to_current | logit_C0.1 | book_physics_price | `p>=0.95; ask<=100; sec>=0` | False | False | 97.26%/66.06% | 99.28%/89.10% | 100.00%/81.25% | 99.0 |
| 15 | v21_to_current | logit_C0.03 | book_physics | `p>=0.95; ask<=100; sec>=0` | False | False | 99.28%/62.44% | 99.28%/88.46% | 100.00%/81.25% | 99.0 |
| 16 | v21_to_current | logit_C0.03 | physics_only | `p>=0.95; ask<=100; sec>=0` | False | False | 99.29%/63.35% | 98.57%/89.74% | 100.00%/81.25% | 99.0 |
| 17 | v21_to_current | logit_C0.1 | physics_only | `p>=0.95; ask<=100; sec>=0` | False | False | 98.05%/69.68% | 97.14%/89.74% | 96.15%/81.25% | 98.0 |
| 18 | current_to_v21 | logit_C0.3 | physics_only | `p>=0.98; ask<=100; sec>=0` | False | False | 100.00%/85.90% | 100.00%/55.66% | 100.00%/51.11% | 100.0 |
| 19 | current_to_v21 | logit_C0.3 | book_physics | `p>=0.98; ask<=100; sec>=0` | False | False | 100.00%/85.90% | 100.00%/55.66% | 100.00%/51.11% | 100.0 |
| 20 | current_to_v21 | logit_C0.3 | path_physics | `p>=0.98; ask<=100; sec>=0` | False | False | 100.00%/85.26% | 100.00%/52.94% | 100.00%/48.89% | 100.0 |

## Read

No learned model/gate transfers across datasets at the 95% accuracy / 80% recurring-market coverage split target.
No nondegenerate learned transfer row clears the target.
