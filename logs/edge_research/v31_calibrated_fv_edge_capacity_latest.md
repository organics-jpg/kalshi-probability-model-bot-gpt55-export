# Calibrated FV Edge Capacity

Generated UTC: `2026-05-04T20:00:20.071087+00:00`

## Scope

- Research-only fair-value edge-capacity audit.
- Causal first qualifying positive-edge row per market; no exit model.
- Gross hold-to-settlement cents only; no live orders or bot changes.

## Holdout High-Coverage Rows

| model | min edge | coverage | selected/resolved | W/L | gross net | ROI | avg edge | avg ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `book_time_v32drift85` | 1.0 | 100.00% | 66/66 | 42/24 | 501.0c | 13.54% | 2.00c | 56.05c |
| `book_time_v33drift85` | 1.0 | 100.00% | 66/66 | 42/24 | 501.0c | 13.54% | 2.00c | 56.05c |
| `book_v33_drift3_platt` | 1.0 | 100.00% | 66/66 | 41/25 | 453.0c | 12.42% | 2.15c | 55.26c |
| `book_v31_drift3_platt` | 1.0 | 100.00% | 66/66 | 41/25 | 445.0c | 12.18% | 2.15c | 55.38c |
| `book_v32_drift3_platt` | 1.0 | 100.00% | 66/66 | 41/25 | 445.0c | 12.18% | 2.16c | 55.38c |
| `book_v32_drift3_platt` | 0.0 | 100.00% | 66/66 | 42/24 | 438.0c | 11.64% | 1.83c | 57.00c |
| `book_v31_drift3_platt` | 0.0 | 100.00% | 66/66 | 42/24 | 436.0c | 11.58% | 1.81c | 57.03c |
| `book_v33_drift3_platt` | 0.0 | 100.00% | 66/66 | 42/24 | 436.0c | 11.58% | 1.82c | 57.03c |
| `book_v33_platt` | 2.5 | 84.85% | 56/66 | 38/18 | 359.0c | 10.43% | 3.20c | 61.45c |
| `book_v33_platt` | 3.5 | 75.76% | 50/66 | 37/13 | 324.0c | 9.60% | 4.01c | 67.52c |
| `book_time_v32drift85` | 0.0 | 100.00% | 66/66 | 41/25 | 322.0c | 8.52% | 1.64c | 57.24c |
| `book_platt` | 1.0 | 100.00% | 66/66 | 44/22 | 321.0c | 7.87% | 1.62c | 61.80c |
| `book_v33_platt` | 2.0 | 92.42% | 61/66 | 40/21 | 314.0c | 8.52% | 2.74c | 60.43c |
| `book_time_v33drift85` | 0.0 | 100.00% | 66/66 | 41/25 | 313.0c | 8.27% | 1.68c | 57.38c |
| `book_v31_micro_platt` | 2.2 | 78.79% | 52/66 | 38/14 | 303.0c | 8.66% | 3.50c | 67.25c |

## Best Holdout Net Rows

| model | min edge | coverage | selected/resolved | W/L | gross net | ROI | avg edge | avg ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `book_time_v32drift85` | 1.0 | 100.00% | 66/66 | 42/24 | 501.0c | 13.54% | 2.00c | 56.05c |
| `book_time_v33drift85` | 1.0 | 100.00% | 66/66 | 42/24 | 501.0c | 13.54% | 2.00c | 56.05c |
| `book_v33_drift3_platt` | 1.0 | 100.00% | 66/66 | 41/25 | 453.0c | 12.42% | 2.15c | 55.26c |
| `book_v31_drift3_platt` | 1.0 | 100.00% | 66/66 | 41/25 | 445.0c | 12.18% | 2.15c | 55.38c |
| `book_v32_drift3_platt` | 1.0 | 100.00% | 66/66 | 41/25 | 445.0c | 12.18% | 2.16c | 55.38c |
| `book_v32_drift3_platt` | 0.0 | 100.00% | 66/66 | 42/24 | 438.0c | 11.64% | 1.83c | 57.00c |
| `book_v31_drift3_platt` | 0.0 | 100.00% | 66/66 | 42/24 | 436.0c | 11.58% | 1.81c | 57.03c |
| `book_v33_drift3_platt` | 0.0 | 100.00% | 66/66 | 42/24 | 436.0c | 11.58% | 1.82c | 57.03c |
| `book_v33_platt` | 2.5 | 84.85% | 56/66 | 38/18 | 359.0c | 10.43% | 3.20c | 61.45c |
| `book_v31_drift3_platt` | 3.2 | 72.73% | 48/66 | 34/14 | 327.0c | 10.64% | 3.76c | 64.02c |
| `book_time_v33drift85` | 3.2 | 72.73% | 48/66 | 34/14 | 326.0c | 10.61% | 3.78c | 64.04c |
| `book_v33_platt` | 3.5 | 75.76% | 50/66 | 37/13 | 324.0c | 9.60% | 4.01c | 67.52c |

## Read

- This is not a live-trading proof because it ignores exits, fees, position limits, and forward sample size.
- Passing rows here only prove the calibrated FV model has enough gross ask-crossing edge capacity to investigate under the coverage constraint.
