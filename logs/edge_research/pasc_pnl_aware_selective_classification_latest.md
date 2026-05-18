# PASC PnL-Aware Selective Classification

Research-only replay over recorded filled trades. No live bot logic changed.

- Generated UTC: `2026-05-08T14:25:45.817537+00:00`
- Matched trades: `470`
- Settled labels: `469`
- Fill probability: `depth_ratio / (depth_ratio + 8.0), clipped to [0.05, 0.95]`
- Validation-locked min_edge: `0.3` cents
- Validation-locked min_fill: `0.6`

## Strategy Windows

| strategy | window | entries | W/L | win rate | PnL | avg/entry | live coverage | robust coverage | avg expected PnL |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| robust_hybrid_base | train_1_200 | 67 | 29/38 | 43.3% | $6.24 | 9.3c | 33.5% | 100.0% | 5.1c |
| robust_hybrid_base | validation_201_300 | 28 | 14/14 | 50.0% | $-0.48 | -1.7c | 28.0% | 100.0% | -2.2c |
| robust_hybrid_base | test_301_end | 63 | 34/28 (+1 flat) | 54.8% | $11.06 | 17.6c | 37.1% | 100.0% | 3.6c |
| robust_hybrid_base | forward_after_200 | 91 | 48/42 (+1 flat) | 53.3% | $10.58 | 11.6c | 33.7% | 100.0% | 1.8c |
| robust_hybrid_base | all | 158 | 77/80 (+1 flat) | 49.0% | $16.82 | 10.6c | 33.6% | 100.0% | 3.2c |
| robust_plus_p_cal_ge_0.70 | train_1_200 | 53 | 21/32 | 39.6% | $4.62 | 8.7c | 26.5% | 79.1% | 9.3c |
| robust_plus_p_cal_ge_0.70 | validation_201_300 | 19 | 11/8 | 57.9% | $2.78 | 14.6c | 19.0% | 67.9% | 3.5c |
| robust_plus_p_cal_ge_0.70 | test_301_end | 51 | 27/23 (+1 flat) | 54.0% | $8.68 | 17.0c | 30.0% | 81.0% | 8.1c |
| robust_plus_p_cal_ge_0.70 | forward_after_200 | 70 | 38/31 (+1 flat) | 55.1% | $11.46 | 16.4c | 25.9% | 76.9% | 6.8c |
| robust_plus_p_cal_ge_0.70 | all | 123 | 59/63 (+1 flat) | 48.4% | $16.08 | 13.1c | 26.2% | 77.8% | 7.9c |
| robust_plus_p_cal_ge_0.80 | train_1_200 | 36 | 15/21 | 41.7% | $4.20 | 11.7c | 18.0% | 53.7% | 14.2c |
| robust_plus_p_cal_ge_0.80 | validation_201_300 | 13 | 9/4 | 69.2% | $2.42 | 18.6c | 13.0% | 46.4% | 7.0c |
| robust_plus_p_cal_ge_0.80 | test_301_end | 39 | 23/15 (+1 flat) | 60.5% | $8.25 | 21.2c | 22.9% | 61.9% | 11.5c |
| robust_plus_p_cal_ge_0.80 | forward_after_200 | 52 | 32/19 (+1 flat) | 62.7% | $10.67 | 20.5c | 19.3% | 57.1% | 10.4c |
| robust_plus_p_cal_ge_0.80 | all | 88 | 47/40 (+1 flat) | 54.0% | $14.87 | 16.9c | 18.7% | 55.7% | 11.9c |
| pasc_recommended_edge0.5_fill0.35 | train_1_200 | 42 | 18/24 | 42.9% | $4.82 | 11.5c | 21.0% | 62.7% | 12.9c |
| pasc_recommended_edge0.5_fill0.35 | validation_201_300 | 14 | 9/5 | 64.3% | $2.74 | 19.6c | 14.0% | 50.0% | 6.8c |
| pasc_recommended_edge0.5_fill0.35 | test_301_end | 43 | 23/19 (+1 flat) | 54.8% | $7.44 | 17.3c | 25.3% | 68.3% | 10.7c |
| pasc_recommended_edge0.5_fill0.35 | forward_after_200 | 57 | 32/24 (+1 flat) | 57.1% | $10.18 | 17.9c | 21.1% | 62.6% | 9.7c |
| pasc_recommended_edge0.5_fill0.35 | all | 99 | 50/48 (+1 flat) | 51.0% | $15.00 | 15.2c | 21.1% | 62.7% | 11.1c |
| pasc_validation_locked | train_1_200 | 40 | 17/23 | 42.5% | $4.46 | 11.2c | 20.0% | 59.7% | 13.0c |
| pasc_validation_locked | validation_201_300 | 13 | 9/4 | 69.2% | $2.88 | 22.2c | 13.0% | 46.4% | 7.3c |
| pasc_validation_locked | test_301_end | 41 | 21/19 (+1 flat) | 52.5% | $6.24 | 15.2c | 24.1% | 65.1% | 10.7c |
| pasc_validation_locked | forward_after_200 | 54 | 30/23 (+1 flat) | 56.6% | $9.12 | 16.9c | 20.0% | 59.3% | 9.9c |
| pasc_validation_locked | all | 94 | 47/46 (+1 flat) | 50.5% | $13.58 | 14.4c | 20.0% | 59.5% | 11.2c |

## Top Validation Grid

| min_edge | min_fill | entries | W/L | PnL | avg | robust coverage | objective |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.3 | 0.6 | 13 | 9/4 | $2.88 | 22.2c | 46.4% | 10.29 |
| 0.3 | 0.7 | 13 | 9/4 | $2.88 | 22.2c | 46.4% | 10.29 |
| 0.5 | 0.6 | 13 | 9/4 | $2.88 | 22.2c | 46.4% | 10.29 |
| 0.5 | 0.7 | 13 | 9/4 | $2.88 | 22.2c | 46.4% | 10.29 |
| 0.3 | 0.3 | 14 | 9/5 | $2.74 | 19.6c | 50.0% | 9.79 |
| 0.3 | 0.35 | 14 | 9/5 | $2.74 | 19.6c | 50.0% | 9.79 |
| 0.3 | 0.4 | 14 | 9/5 | $2.74 | 19.6c | 50.0% | 9.79 |
| 0.3 | 0.5 | 14 | 9/5 | $2.74 | 19.6c | 50.0% | 9.79 |
| 0.5 | 0.3 | 14 | 9/5 | $2.74 | 19.6c | 50.0% | 9.79 |
| 0.5 | 0.35 | 14 | 9/5 | $2.74 | 19.6c | 50.0% | 9.79 |
| 0.5 | 0.4 | 14 | 9/5 | $2.74 | 19.6c | 50.0% | 9.79 |
| 0.5 | 0.5 | 14 | 9/5 | $2.74 | 19.6c | 50.0% | 9.79 |

## Rolling WFA

- Splits: `20` rolling `50 train / 5 purge / 20 test` windows.
- Positive windows with trades: `13/17`.
- Max positive-window PnL share: `17.9%`.

| aggregate entries | W/L | PnL | avg/entry | live coverage | robust coverage |
|---:|---:|---:|---:|---:|---:|
| 65 | 34/30 (+1 flat) | $9.50 | 14.6c | 16.2% | 50.0% |

| split | locked edge | locked fill | test entries | test W/L | test PnL | test avg |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 10.0 | 0.3 | 0 | 0/0 | $0.00 | n/a |
| 2 | 0.3 | 0.3 | 2 | 0/2 | $-0.36 | -18.0c |
| 3 | 0.3 | 0.8 | 0 | 0/0 | $0.00 | n/a |
| 4 | 0.0 | 0.3 | 1 | 1/0 | $0.76 | 76.0c |
| 5 | None | None | 0 | 0/0 | $0.00 | n/a |
| 6 | 0.0 | 0.3 | 1 | 0/1 | $-0.10 | -10.0c |
| 7 | 0.0 | 0.3 | 7 | 4/3 | $1.26 | 18.0c |
| 8 | 5.0 | 0.3 | 6 | 2/4 | $-0.62 | -10.3c |
| 9 | 0.0 | 0.3 | 3 | 3/0 | $1.90 | 63.3c |
| 10 | 0.0 | 0.3 | 4 | 2/2 | $0.44 | 11.0c |
| 11 | 0.0 | 0.3 | 1 | 0/1 | $-0.16 | -16.0c |
| 12 | 0.3 | 0.3 | 5 | 3/2 | $0.94 | 18.8c |
| 13 | 0.3 | 0.6 | 2 | 2/0 | $1.10 | 55.0c |
| 14 | 0.0 | 0.6 | 2 | 2/0 | $0.84 | 42.0c |
| 15 | 0.0 | 0.6 | 10 | 3/6 (+1 flat) | $0.10 | 1.0c |
| 16 | 1.5 | 0.3 | 5 | 4/1 | $1.92 | 38.4c |
| 17 | 1.5 | 0.3 | 3 | 2/1 | $0.72 | 24.0c |
| 18 | 5.0 | 0.3 | 6 | 3/3 | $0.06 | 1.0c |
| 19 | 5.0 | 0.3 | 2 | 1/1 | $0.18 | 9.0c |
| 20 | 10.0 | 0.3 | 5 | 2/3 | $0.52 | 10.4c |

## Execution Fill Diagnostic

- Entry submit starts: `1941`.
- Entry submit successes: `1870`.
- Entry submit rejects: `71`.
- Exchange submit success rate: `96.3%`.
- Positive fill_count among submit successes: `56.9%` (`1064` positive / `806` zero-fill).
- Median depth_ratio success/reject: `55.35` / `352.86`.
- Median book_age_ms success/reject: `109.00` / `31.00`.

## E-Process

| strategy | window | entries | best lambda | final capital | max capital | crossed 20 | crossed 100 |
|---|---|---:|---:|---:|---:|---|---|
| pasc_validation_locked | train_1_200 | 40 | 0.35 | 1.90 | 2.06 | no | no |
| pasc_validation_locked | validation_201_300 | 13 | 0.35 | 1.56 | 1.65 | no | no |
| pasc_validation_locked | test_301_end | 41 | 0.35 | 2.66 | 2.66 | no | no |
| pasc_validation_locked | forward_after_200 | 54 | 0.35 | 4.15 | 4.15 | no | no |
| pasc_validation_locked | all | 94 | 0.35 | 7.87 | 7.87 | no | no |
| robust_plus_p_cal_ge_0.70 | train_1_200 | 53 | 0.35 | 1.92 | 2.08 | no | no |
| robust_plus_p_cal_ge_0.70 | validation_201_300 | 19 | 0.35 | 1.51 | 1.59 | no | no |
| robust_plus_p_cal_ge_0.70 | test_301_end | 51 | 0.35 | 3.96 | 3.96 | no | no |
| robust_plus_p_cal_ge_0.70 | forward_after_200 | 70 | 0.35 | 5.98 | 5.98 | no | no |
| robust_plus_p_cal_ge_0.70 | all | 123 | 0.35 | 11.50 | 11.50 | no | no |
| robust_plus_p_cal_ge_0.80 | train_1_200 | 36 | 0.35 | 1.82 | 1.97 | no | no |
| robust_plus_p_cal_ge_0.80 | validation_201_300 | 13 | 0.35 | 1.45 | 1.53 | no | no |
| robust_plus_p_cal_ge_0.80 | test_301_end | 39 | 0.35 | 3.75 | 3.75 | no | no |
| robust_plus_p_cal_ge_0.80 | forward_after_200 | 52 | 0.35 | 5.44 | 5.44 | no | no |
| robust_plus_p_cal_ge_0.80 | all | 88 | 0.35 | 9.91 | 9.91 | no | no |

## Promotion Check

- Passes all: `False`

| gate | pass |
|---|---|
| test_pnl_gt_8 | False |
| test_robust_coverage_gt_20pct | True |
| test_win_rate_gt_55pct | False |
| test_avg_gt_15c | True |
| wfa_positive_trade_windows_all | False |
| wfa_no_single_window_gt_40pct_positive_pnl | True |
| e_process_test_crossed_100 | False |
| e_process_train_not_crossed_100 | True |

## Read

- PASC is conceptually right to optimize PnL instead of classification loss, but this retrospective filled-trade replay does not beat the existing ACI threshold overlays.
- The validation-locked PASC gate misses the Truffle projected PnL target on the 301-end holdout.
- The right next step is logging PASC fields for every live/shadow candidate, including non-trades and unfilled IOC attempts, before treating fill_prob as real.
