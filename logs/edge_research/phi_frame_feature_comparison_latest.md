# Phi-Frame Feature Comparison

Research-only filled-trade replay. No live bot logic/state/order path was changed.

## Data
- Usable rows: `469` / raw rows `470`.
- Row idx range: `1` to `470`.
- BTC candles: `2026-03-14 00:54:00+00:00` to `2026-05-07 17:14:00+00:00`.

## Probability Score, Forward Rows 201+
- Raw capped-ACI p_calibrated: Brier `0.16437`, log loss `0.51272`.
- Brownian terminal: Brier `0.16188`, log loss `0.50377`.

## Top WFA PnL Rows
| rank | family | gate | frames | brier | log_loss | entries | W/L | pnl | avg/entry | pos windows | mean abs corr |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | standard_3 | robust_overlay | 1,5,15 | 0.17083 | 0.54268 | 69 | 40/28 +1 flat | $12.33 | 17.9c | 4/4 | 0.371 |
| 2 | log_3 | robust_overlay | 1,4,16 | 0.17200 | 0.54529 | 71 | 40/30 +1 flat | $10.65 | 15.0c | 4/4 | 0.376 |
| 3 | phi_3 | robust_overlay | 1,3,8 | 0.17525 | 0.56824 | 59 | 33/25 +1 flat | $9.42 | 16.0c | 4/4 | 0.376 |
| 4 | standard_6 | robust_overlay | 1,2,3,5,10,15 | 0.18503 | 0.65593 | 65 | 37/27 +1 flat | $9.39 | 14.4c | 4/4 | 0.307 |
| 5 | phi_6 | robust_overlay | 1,2,3,5,8,13 | 0.18028 | 0.64111 | 67 | 37/29 +1 flat | $9.27 | 13.8c | 4/4 | 0.309 |
| 6 | phi_15s_seed_rounded | robust_overlay | 1,2,3,4,5,7,12 | 0.18651 | 0.65424 | 63 | 31/31 +1 flat | $7.00 | 11.1c | 4/4 | 0.330 |
| 7 | phi_seconds_rounded | robust_overlay | 1,2,3,5,8,10 | 0.18172 | 0.64240 | 69 | 37/31 +1 flat | $9.50 | 13.8c | 3/4 | 0.324 |
| 8 | log_6 | robust_overlay | 1,2,4,8,16,32 | 0.17709 | 0.56521 | 66 | 36/29 +1 flat | $8.81 | 13.3c | 3/4 | 0.289 |
| 9 | base_only | robust_overlay | base | 0.16313 | 0.50931 | 75 | 40/34 +1 flat | $8.02 | 10.7c | 3/4 | n/a |
| 10 | log_3 | model_all | 1,4,16 | 0.17200 | 0.54529 | 202 | 98/101 +3 flat | $7.01 | 3.5c | 3/4 | 0.376 |
| 11 | standard_6 | model_all | 1,2,3,5,10,15 | 0.18503 | 0.65593 | 169 | 84/82 +3 flat | $5.02 | 3.0c | 3/4 | 0.307 |
| 12 | phi_seconds_rounded | model_all | 1,2,3,5,8,10 | 0.18172 | 0.64240 | 172 | 84/85 +3 flat | $4.53 | 2.6c | 3/4 | 0.324 |
| 13 | phi_15s_seed_rounded | model_all | 1,2,3,4,5,7,12 | 0.18651 | 0.65424 | 163 | 78/82 +3 flat | $3.93 | 2.4c | 3/4 | 0.330 |
| 14 | phi_6 | model_all | 1,2,3,5,8,13 | 0.18028 | 0.64111 | 187 | 90/94 +3 flat | $3.67 | 2.0c | 3/4 | 0.309 |

## Locked Train-200 Robust Overlay
| family | frames | threshold | entries | W/L | pnl | avg/entry |
|---|---|---:|---:|---:|---:|---:|
| standard_6 | 1,2,3,5,10,15 | 0.62 | 87 | 47/39 +1 flat | $14.04 | 16.1c |
| phi_6 | 1,2,3,5,8,13 | 0.54 | 88 | 48/39 +1 flat | $13.58 | 15.4c |
| standard_3 | 1,5,15 | 0.64 | 88 | 47/40 +1 flat | $13.52 | 15.4c |
| log_3 | 1,4,16 | 0.62 | 88 | 47/40 +1 flat | $13.52 | 15.4c |
| phi_seconds_rounded | 1,2,3,5,8,10 | 0.62 | 86 | 46/39 +1 flat | $13.34 | 15.5c |
| phi_3 | 1,3,8 | 0.56 | 87 | 47/39 +1 flat | $13.32 | 15.3c |
| phi_15s_seed_rounded | 1,2,3,4,5,7,12 | 0.56 | 89 | 47/41 +1 flat | $12.76 | 14.3c |
| log_6 | 1,2,4,8,16,32 | 0.52 | 90 | 48/41 +1 flat | $10.62 | 11.8c |
| base_only | base | 0.50 | 91 | 48/42 +1 flat | $10.58 | 11.6c |

## Baseline Gates
- robust_hybrid_base_forward_after_200: entries `91`, W/L `48/42 +1 flat`, PnL `$10.58`, avg `11.6c`.
- robust_p_cal_ge_0p70_forward_after_200: entries `70`, W/L `38/31 +1 flat`, PnL `$11.46`, avg `16.4c`.
- robust_p_cal_ge_0p80_forward_after_200: entries `52`, W/L `32/19 +1 flat`, PnL `$10.67`, avg `20.5c`.

## Interpretation
- Promotion needs better probability score and more stable WFA PnL than the capped-ACI/robust baselines, not just a prettier frame list.
- Since this is filled-trade replay, any promising row still needs all-candidate shadow validation before live use.
