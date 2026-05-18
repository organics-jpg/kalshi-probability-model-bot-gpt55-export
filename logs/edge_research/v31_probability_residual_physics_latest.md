# v31 Probability Residual Physics

Generated UTC: `2026-05-04T17:48:30.612293+00:00`

## Scope

- Calibration residual audit for FV probabilities, not trade scoring.
- Uses the all-heartbeats v31 probability replay.
- No live bot code/process or orders are touched.

## Worst Holdout Buckets

Rows floor: `100`.

| feature | bucket | rows | mean pred | realized | error | Brier | logloss |
|---|---|---:|---:|---:|---:|---:|---:|
| `book_minus_model_p_side` | `(-1.001, -0.2]` | 204 | 52.52% | 21.57% | 30.96% | 0.25517 | 0.72118 |
| `book_minus_model_p_side` | `(0.2, 1.0]` | 204 | 47.48% | 78.43% | -30.96% | 0.25517 | 0.72118 |
| `book_minus_model_p_side` | `(-0.2, -0.1]` | 619 | 45.95% | 31.99% | 13.96% | 0.20481 | 0.59770 |
| `book_minus_model_p_side` | `(0.1, 0.2]` | 619 | 54.05% | 68.01% | -13.96% | 0.20481 | 0.59770 |
| `book_minus_model_p_side` | `(0.05, 0.1]` | 787 | 54.51% | 63.15% | -8.64% | 0.18251 | 0.54516 |
| `book_minus_model_p_side` | `(-0.1, -0.05]` | 787 | 45.49% | 36.85% | 8.64% | 0.18251 | 0.54516 |
| `book_margin_cents` | `(-60.0, -25.0]` | 956 | 34.65% | 26.15% | 8.50% | 0.21713 | 0.62957 |
| `book_margin_cents` | `(25.0, 60.0]` | 921 | 65.69% | 73.51% | -7.82% | 0.21540 | 0.62508 |
| `drift_projected_margin_5m` | `(-34.155, 0.0]` | 531 | 44.85% | 50.09% | -5.25% | 0.20461 | 0.58688 |
| `drift_projected_margin_5m` | `(0.0, 34.155]` | 531 | 55.15% | 49.91% | 5.25% | 0.20461 | 0.58688 |
| `drift_projected_margin_3m` | `(84.963, 175.592]` | 784 | 73.22% | 68.62% | 4.60% | 0.14926 | 0.43265 |
| `drift_projected_margin_3m` | `(-175.592, -84.963]` | 784 | 26.78% | 31.38% | -4.60% | 0.14926 | 0.43265 |
| `signed_velocity_dps_5m` | `(0.0449, 0.101]` | 546 | 56.57% | 52.93% | 3.64% | 0.15876 | 0.46121 |
| `signed_velocity_dps_5m` | `(-0.101, -0.0449]` | 546 | 43.43% | 47.07% | -3.64% | 0.15876 | 0.46121 |
| `adverse_move_5m` | `(13.48, 30.39]` | 546 | 43.43% | 47.07% | -3.64% | 0.15876 | 0.46121 |

## Feature Residual Ranking

| feature | weighted abs error |
|---|---:|
| `book_minus_model_p_side` | 7.09% |
| `book_margin_cents` | 3.85% |
| `drift_projected_margin_5m` | 2.60% |
| `signed_velocity_dps_1m` | 1.43% |
| `drift_projected_margin_1m` | 1.26% |
| `signed_velocity_dps_5m` | 1.21% |
| `drift_projected_margin_3m` | 1.21% |
| `adverse_move_1m` | 1.15% |
| `signed_velocity_dps_3m` | 1.11% |
| `adverse_move_3m` | 1.05% |
| `adverse_move_5m` | 0.90% |
| `seconds_to_close` | 0.00% |
| `spread_cents` | 0.00% |

## Read

- Buckets with large residuals are candidates for the next FV-state correction.
- A bucket here is not a trading rule; it is a place where the probability surface is miscalibrated.
