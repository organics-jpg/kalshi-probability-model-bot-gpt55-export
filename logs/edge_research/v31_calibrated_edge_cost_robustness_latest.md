# Calibrated Edge Cost Robustness

Generated UTC: `2026-05-04T20:00:55.906830+00:00`

## Scope

- Cost pressure test for research-only FV edge-capacity selections.
- No exits, no live orders, no bot changes.
- Robust pass means train/validation/holdout all have coverage >= 75.00% and positive net after cost.

## Robust Pass Rows

| model | min edge | cost | min split coverage | min split net | train | validation | holdout |
|---|---:|---:|---:|---:|---:|---:|---:|
| `book_time_v33drift85` | 1.0 | 3.0 | 99.49% | 28.0c | 28.0c | 48.0c | 303.0c |
| `book_time_v32drift85` | 1.0 | 2.0 | 99.49% | 122.0c | 122.0c | 221.0c | 369.0c |
| `book_time_v33drift85` | 1.0 | 2.0 | 99.49% | 114.0c | 225.0c | 114.0c | 369.0c |
| `book_v31_time_platt` | 1.0 | 2.0 | 99.49% | 4.0c | 889.0c | 102.0c | 4.0c |
| `book_v33_drift3_platt` | 2.0 | 2.0 | 85.86% | 3.0c | 17.0c | 3.0c | 40.0c |
| `book_time_v32drift85` | 1.0 | 1.5 | 99.49% | 220.5c | 220.5c | 254.0c | 402.0c |
| `book_time_v33drift85` | 1.0 | 1.5 | 99.49% | 147.0c | 323.5c | 147.0c | 402.0c |
| `book_v31_time_platt` | 1.0 | 1.5 | 99.49% | 37.0c | 987.5c | 135.0c | 37.0c |
| `book_v33_drift3_platt` | 2.0 | 1.5 | 85.86% | 31.5c | 102.0c | 31.5c | 71.5c |
| `book_v32_drift3_platt` | 2.0 | 1.5 | 86.36% | 28.5c | 49.5c | 28.5c | 125.0c |
| `book_v32_platt` | 2.0 | 1.5 | 87.88% | 16.0c | 282.0c | 16.0c | 158.0c |
| `book_v31_platt` | 2.0 | 1.5 | 87.88% | 10.5c | 300.0c | 10.5c | 164.0c |
| `book_v32_drift3_platt` | 2.2 | 1.5 | 78.79% | 6.0c | 289.0c | 6.0c | 18.0c |
| `book_v31_drift3_platt` | 2.0 | 1.5 | 85.35% | 5.5c | 5.5c | 28.5c | 38.0c |
| `book_v31_drift3_platt` | 2.2 | 1.5 | 78.79% | 5.0c | 270.5c | 5.0c | 20.0c |
| `book_time_v32drift85` | 1.0 | 1.0 | 99.49% | 287.0c | 319.0c | 287.0c | 435.0c |
| `book_time_v33drift85` | 1.0 | 1.0 | 99.49% | 180.0c | 422.0c | 180.0c | 435.0c |
| `book_v31_time_platt` | 1.0 | 1.0 | 99.49% | 70.0c | 1086.0c | 168.0c | 70.0c |
| `book_v33_drift3_platt` | 2.0 | 1.0 | 85.86% | 60.0c | 187.0c | 60.0c | 103.0c |
| `book_v31_drift3_platt` | 2.0 | 1.0 | 85.35% | 57.0c | 90.0c | 57.0c | 69.0c |
| `book_v32_drift3_platt` | 2.0 | 1.0 | 86.36% | 57.0c | 135.0c | 57.0c | 156.0c |
| `book_v32_platt` | 2.0 | 1.0 | 87.88% | 46.0c | 369.0c | 46.0c | 189.0c |
| `book_v31_platt` | 2.0 | 1.0 | 87.88% | 40.0c | 387.0c | 40.0c | 195.0c |
| `book_v32_drift3_platt` | 2.2 | 1.0 | 78.79% | 32.0c | 368.0c | 32.0c | 49.0c |
| `book_v31_drift3_platt` | 2.2 | 1.0 | 78.79% | 31.0c | 349.0c | 31.0c | 51.0c |
| `book_v32_drift3_platt` | 0.0 | 1.0 | 100.00% | 19.0c | 216.0c | 19.0c | 372.0c |
| `book_v32_drift3_platt` | 1.0 | 1.0 | 99.49% | 10.0c | 85.0c | 10.0c | 379.0c |
| `book_v31_drift3_platt` | 1.0 | 1.0 | 99.49% | 3.0c | 7.0c | 3.0c | 379.0c |
| `book_time_v32drift85` | 1.0 | 0.5 | 99.49% | 320.0c | 417.5c | 320.0c | 468.0c |
| `book_time_v33drift85` | 1.0 | 0.5 | 99.49% | 213.0c | 520.5c | 213.0c | 468.0c |
| `book_v31_time_platt` | 1.0 | 0.5 | 99.49% | 103.0c | 1184.5c | 201.0c | 103.0c |
| `book_v33_platt` | 1.0 | 0.5 | 99.49% | 90.5c | 90.5c | 199.0c | 92.0c |
| `book_v33_drift3_platt` | 2.0 | 0.5 | 85.86% | 88.5c | 272.0c | 88.5c | 134.5c |
| `book_v31_drift3_platt` | 2.0 | 0.5 | 85.35% | 85.5c | 174.5c | 85.5c | 100.0c |
| `book_v32_drift3_platt` | 2.0 | 0.5 | 86.36% | 85.5c | 220.5c | 85.5c | 187.0c |
| `book_v32_platt` | 2.0 | 0.5 | 87.88% | 76.0c | 456.0c | 76.0c | 220.0c |
| `book_v31_platt` | 2.0 | 0.5 | 87.88% | 69.5c | 474.0c | 69.5c | 226.0c |
| `book_v32_drift3_platt` | 2.2 | 0.5 | 78.79% | 58.0c | 447.0c | 58.0c | 80.0c |
| `book_v31_drift3_platt` | 2.2 | 0.5 | 78.79% | 57.0c | 427.5c | 57.0c | 82.0c |
| `book_v32_drift3_platt` | 0.0 | 0.5 | 100.00% | 52.0c | 315.0c | 52.0c | 405.0c |
| `book_v32_drift3_platt` | 1.0 | 0.5 | 99.49% | 43.0c | 183.5c | 43.0c | 412.0c |
| `book_v33_drift3_platt` | 1.0 | 0.5 | 99.49% | 40.5c | 40.5c | 44.0c | 420.0c |
| `book_v31_drift3_platt` | 1.0 | 0.5 | 99.49% | 36.0c | 105.5c | 36.0c | 412.0c |
| `book_v33_drift3_platt` | 2.2 | 0.5 | 78.79% | 12.0c | 391.5c | 12.0c | 70.0c |
| `book_time_v33drift85` | 2.0 | 0.5 | 84.34% | 4.5c | 419.5c | 258.0c | 4.5c |
| `book_time_v32drift85` | 1.0 | 0.0 | 99.49% | 353.0c | 516.0c | 353.0c | 501.0c |
| `book_time_v33drift85` | 1.0 | 0.0 | 99.49% | 246.0c | 619.0c | 246.0c | 501.0c |
| `book_v31_time_platt` | 1.0 | 0.0 | 99.49% | 136.0c | 1283.0c | 234.0c | 136.0c |
| `book_v33_platt` | 1.0 | 0.0 | 99.49% | 125.0c | 189.0c | 232.0c | 125.0c |
| `book_v33_drift3_platt` | 2.0 | 0.0 | 85.86% | 117.0c | 357.0c | 117.0c | 166.0c |
| `book_v31_drift3_platt` | 2.0 | 0.0 | 85.35% | 114.0c | 259.0c | 114.0c | 131.0c |
| `book_v32_drift3_platt` | 2.0 | 0.0 | 86.36% | 114.0c | 306.0c | 114.0c | 218.0c |
| `book_v32_platt` | 2.0 | 0.0 | 87.88% | 106.0c | 543.0c | 106.0c | 251.0c |
| `book_v31_platt` | 2.0 | 0.0 | 87.88% | 99.0c | 561.0c | 99.0c | 257.0c |
| `book_v32_drift3_platt` | 0.0 | 0.0 | 100.00% | 85.0c | 414.0c | 85.0c | 438.0c |
| `book_v32_drift3_platt` | 2.2 | 0.0 | 78.79% | 84.0c | 526.0c | 84.0c | 111.0c |
| `book_v31_drift3_platt` | 2.2 | 0.0 | 78.79% | 83.0c | 506.0c | 83.0c | 113.0c |
| `book_v33_drift3_platt` | 1.0 | 0.0 | 99.49% | 77.0c | 139.0c | 77.0c | 453.0c |
| `book_v32_drift3_platt` | 1.0 | 0.0 | 99.49% | 76.0c | 282.0c | 76.0c | 445.0c |
| `book_v31_drift3_platt` | 1.0 | 0.0 | 99.49% | 69.0c | 204.0c | 69.0c | 445.0c |
| `book_v32_platt` | 1.0 | 0.0 | 99.49% | 39.0c | 39.0c | 245.0c | 68.0c |
| `book_v33_drift3_platt` | 2.2 | 0.0 | 78.79% | 38.0c | 471.0c | 38.0c | 101.0c |
| `book_time_v33drift85` | 2.0 | 0.0 | 84.34% | 36.0c | 503.0c | 286.0c | 36.0c |
| `book_v32_platt` | 2.2 | 0.0 | 80.81% | 26.0c | 716.0c | 26.0c | 162.0c |
| `book_time_v32drift85` | 2.0 | 0.0 | 84.34% | 15.0c | 496.0c | 277.0c | 15.0c |
| `book_v33_drift3_platt` | 2.5 | 0.0 | 76.77% | 1.0c | 658.0c | 1.0c | 87.0c |

## Holdout High-Coverage Rows

| model | min edge | cost | coverage | selected/resolved | net after cost | ROI after cost |
|---|---:|---:|---:|---:|---:|---:|
| `book_time_v32drift85` | 1.0 | 0.0 | 100.00% | 66/66 | 501.0c | 13.54% |
| `book_time_v33drift85` | 1.0 | 0.0 | 100.00% | 66/66 | 501.0c | 13.54% |
| `book_v33_drift3_platt` | 1.0 | 0.0 | 100.00% | 66/66 | 453.0c | 12.42% |
| `book_v31_drift3_platt` | 1.0 | 0.0 | 100.00% | 66/66 | 445.0c | 12.18% |
| `book_v32_drift3_platt` | 1.0 | 0.0 | 100.00% | 66/66 | 445.0c | 12.18% |
| `book_v32_drift3_platt` | 0.0 | 0.0 | 100.00% | 66/66 | 438.0c | 11.64% |
| `book_v31_drift3_platt` | 0.0 | 0.0 | 100.00% | 66/66 | 436.0c | 11.58% |
| `book_v33_drift3_platt` | 0.0 | 0.0 | 100.00% | 66/66 | 436.0c | 11.58% |
| `book_v33_platt` | 2.5 | 0.0 | 84.85% | 56/66 | 359.0c | 10.43% |
| `book_v33_platt` | 3.5 | 0.0 | 75.76% | 50/66 | 324.0c | 9.60% |
| `book_time_v32drift85` | 0.0 | 0.0 | 100.00% | 66/66 | 322.0c | 8.52% |
| `book_platt` | 1.0 | 0.0 | 100.00% | 66/66 | 321.0c | 7.87% |
| `book_v33_platt` | 2.0 | 0.0 | 92.42% | 61/66 | 314.0c | 8.52% |
| `book_time_v33drift85` | 0.0 | 0.0 | 100.00% | 66/66 | 313.0c | 8.27% |
| `book_v31_micro_platt` | 2.2 | 0.0 | 78.79% | 52/66 | 303.0c | 8.66% |
| `book_v33_platt` | 2.2 | 0.0 | 90.91% | 60/66 | 294.0c | 7.93% |
| `book_v31_platt` | 0.0 | 0.0 | 100.00% | 66/66 | 283.0c | 7.41% |
| `book_v32_platt` | 0.0 | 0.0 | 100.00% | 66/66 | 283.0c | 7.41% |
| `book_platt` | 2.0 | 0.0 | 80.30% | 53/66 | 282.0c | 8.25% |
| `book_v33_platt` | 0.0 | 0.0 | 100.00% | 66/66 | 278.0c | 7.27% |
| `book_v33_platt` | 2.8 | 0.0 | 83.33% | 55/66 | 264.0c | 7.68% |
| `book_v31_time_platt` | 0.0 | 0.0 | 100.00% | 66/66 | 262.0c | 6.65% |
| `book_v31_platt` | 2.0 | 0.0 | 93.94% | 62/66 | 257.0c | 6.87% |
| `book_platt` | 2.2 | 0.0 | 77.27% | 51/66 | 255.0c | 7.40% |
| `book_v31_platt` | 2.5 | 0.0 | 87.88% | 58/66 | 254.0c | 7.16% |

## Read

- Gross edge capacity is not enough; fee/slippage/buffer can erase the validation margin.
- If no row survives realistic costs across splits, the model needs either stronger edge, exits, or lower-cost execution before any promotion.
