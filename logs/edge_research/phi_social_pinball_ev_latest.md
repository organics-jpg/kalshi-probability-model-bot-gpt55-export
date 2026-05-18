# Phi + Social + Pinball EV Bakeoff

Research-only filled-trade replay. No live bot logic/state/order path was changed.

## Data
- Usable rows: `469` / raw rows `470`.
- Row idx range: `1` to `470`.
- BTC candles: `2026-03-14 00:54:00+00:00` to `2026-05-07 17:14:00+00:00`.

## Baselines, Forward Rows 201+
- live_all_recorded_forward_after_200: entries `269`, W/L `126/138 +5 flat`, PnL `$4.15`, avg `1.5c`.
- robust_hybrid_forward_after_200: entries `91`, W/L `48/42 +1 flat`, PnL `$10.58`, avg `11.6c`.
- robust_p_cal_ge_0p70_forward_after_200: entries `70`, W/L `38/31 +1 flat`, PnL `$11.46`, avg `16.4c`.
- robust_p_cal_ge_0p80_forward_after_200: entries `52`, W/L `32/19 +1 flat`, PnL `$10.67`, avg `20.5c`.

## WFA EV-Selection Results
| rank | feature set | gate | features | pred-vs-PnL rho | top-Q pnl | entries | W/L | pnl | avg/entry | pos windows | window pnl c |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | base_ev | robust_ev_overlay | 7 | -0.073 | $-5.98 | 87 | 47/39 +1 flat | $12.52 | 14.4c | 3/4 | -54.0,550.0,386.0,370.0 |
| 2 | social_pinball | robust_ev_overlay | 55 | 0.010 | $2.68 | 29 | 16/13 | $4.23 | 14.6c | 3/4 | -130.0,222.0,121.0,210.0 |
| 3 | phi_only | robust_ev_overlay | 31 | -0.081 | $-3.72 | 46 | 22/23 +1 flat | $3.90 | 8.5c | 3/4 | -92.0,264.0,160.0,58.0 |
| 4 | standard6_social_pinball_control | ev_all | 79 | -0.007 | $0.48 | 92 | 44/48 | $2.99 | 3.2c | 3/4 | -298.0,185.0,54.0,358.0 |
| 5 | pinball_only | robust_ev_overlay | 37 | -0.001 | $1.64 | 41 | 19/22 | $2.52 | 6.1c | 3/4 | -212.0,206.0,34.0,224.0 |
| 6 | phi_pinball | robust_ev_overlay | 68 | -0.004 | $2.05 | 31 | 15/16 | $1.89 | 6.1c | 3/4 | -206.0,110.0,125.0,160.0 |
| 7 | social_only | robust_ev_overlay | 18 | -0.052 | $-2.97 | 23 | 11/12 | $1.83 | 8.0c | 3/4 | -214.0,188.0,87.0,122.0 |
| 8 | all3_phi_social_pinball | robust_ev_overlay | 79 | -0.014 | $2.25 | 25 | 11/14 | $1.21 | 4.8c | 3/4 | -274.0,50.0,135.0,210.0 |
| 9 | phi_social | robust_ev_overlay | 42 | -0.055 | $-7.51 | 23 | 10/13 | $0.88 | 3.8c | 3/4 | -274.0,26.0,136.0,200.0 |
| 10 | social_pinball | ev_all | 55 | 0.010 | $2.68 | 91 | 44/47 | $2.09 | 2.3c | 2/4 | -28.0,95.0,-120.0,262.0 |
| 11 | standard6_social_pinball_control | robust_ev_overlay | 79 | -0.007 | $0.48 | 22 | 10/12 | $1.81 | 8.2c | 2/3 | -142.0,0.0,85.0,238.0 |
| 12 | pinball_only | ev_all | 37 | -0.001 | $1.64 | 124 | 56/68 | $0.95 | 0.8c | 2/4 | -62.0,107.0,-206.0,256.0 |
| 13 | phi_only | ev_all | 31 | -0.081 | $-3.72 | 168 | 72/94 +2 flat | $0.12 | 0.1c | 2/4 | -80.0,-26.0,68.0,50.0 |
| 14 | base_ev | ev_all | 7 | -0.073 | $-5.98 | 211 | 97/110 +4 flat | $1.73 | 0.8c | 1/4 | -116.0,-63.0,-44.0,396.0 |
| 15 | phi_pinball | ev_all | 68 | -0.004 | $2.05 | 98 | 45/53 | $-0.03 | -0.0c | 1/4 | -190.0,-33.0,-48.0,268.0 |
| 16 | all3_phi_social_pinball | ev_all | 79 | -0.014 | $2.25 | 93 | 41/52 | $-2.12 | -2.3c | 1/4 | -388.0,-15.0,-97.0,288.0 |
| 17 | phi_social | ev_all | 42 | -0.055 | $-7.51 | 110 | 46/64 | $-5.28 | -4.8c | 1/4 | -402.0,-263.0,-65.0,202.0 |
| 18 | social_only | ev_all | 18 | -0.052 | $-2.97 | 89 | 37/51 +1 flat | $-4.80 | -5.4c | 0/4 | -260.0,-43.0,-175.0,-2.0 |

## Locked Train-200 Robust EV Overlay
| feature set | threshold EV | rho | entries | W/L | pnl | avg/entry |
|---|---:|---:|---:|---:|---:|---:|
| base_ev | 4.0c | -0.045 | 81 | 42/39 | $10.08 | 12.4c |
| phi_only | 2.0c | -0.055 | 75 | 39/36 | $9.24 | 12.3c |
| standard6_social_pinball_control | 10.0c | -0.036 | 41 | 21/20 | $4.95 | 12.1c |
| social_pinball | 15.0c | -0.029 | 30 | 17/13 | $3.91 | 13.0c |
| phi_social | 12.0c | -0.054 | 41 | 19/22 | $3.36 | 8.2c |
| pinball_only | 12.0c | -0.021 | 30 | 14/16 | $3.25 | 10.8c |
| phi_pinball | 15.0c | -0.034 | 30 | 14/16 | $1.87 | 6.2c |
| social_only | 15.0c | -0.055 | 29 | 14/15 | $1.60 | 5.5c |
| all3_phi_social_pinball | 20.0c | -0.039 | 21 | 10/11 | $1.27 | 6.0c |

## Interpretation
- A credible pass should beat the robust p_cal baseline, show positive predicted-EV ranking, and avoid one-window dependence.
- Any replay-positive result here still needs all-candidate shadow logging because this table excludes skipped and unfilled opportunities.
