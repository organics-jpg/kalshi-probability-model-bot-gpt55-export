# Nonlinear Phi + Social + Pinball EV Bakeoff

Research-only filled-trade replay. No live bot logic/state/order path was changed.

## Top WFA Rows
| rank | feature set | model | gate | rho | top-Q pnl | entries | W/L | pnl | avg | pos windows | window pnl c |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | base_ev | rf_d3_leaf15 | robust_ev_overlay | -0.002 | $-1.94 | 43 | 23/20 | $8.26 | 19.2c | 4/4 | 220.0,354.0,96.0,156.0 |
| 2 | base_ev | tree_d3_leaf20 | robust_ev_overlay | 0.001 | $-3.21 | 43 | 25/18 | $7.03 | 16.3c | 4/4 | 128.0,310.0,221.0,44.0 |
| 3 | phi_only | rf_d3_leaf15 | robust_ev_overlay | -0.117 | $-6.58 | 27 | 16/11 | $5.00 | 18.5c | 4/4 | 38.0,248.0,118.0,96.0 |
| 4 | base_ev | hgb_leaf20_l2 | robust_ev_overlay | 0.017 | $-2.98 | 34 | 18/16 | $4.90 | 14.4c | 4/4 | 108.0,258.0,88.0,36.0 |
| 5 | pinball_only | tree_d3_leaf20 | robust_ev_overlay | -0.075 | $-0.89 | 39 | 18/21 | $2.31 | 5.9c | 4/4 | 52.0,122.0,31.0,26.0 |
| 6 | base_ev | tree_d2_leaf20 | robust_ev_overlay | 0.002 | $-1.36 | 69 | 37/31 +1 flat | $10.92 | 15.8c | 3/4 | -6.0,414.0,314.0,370.0 |
| 7 | all3_phi_social_pinball | tree_d2_leaf20 | robust_ev_overlay | -0.068 | $-2.79 | 67 | 36/30 +1 flat | $9.92 | 14.8c | 3/4 | -84.0,486.0,246.0,344.0 |
| 8 | standard6_social_pinball_control | tree_d2_leaf20 | robust_ev_overlay | -0.049 | $2.80 | 67 | 35/31 +1 flat | $9.62 | 14.4c | 3/4 | -84.0,486.0,246.0,314.0 |
| 9 | phi_pinball | tree_d2_leaf20 | robust_ev_overlay | -0.103 | $-0.50 | 62 | 33/28 +1 flat | $9.40 | 15.2c | 3/4 | -66.0,416.0,246.0,344.0 |
| 10 | phi_only | tree_d2_leaf20 | robust_ev_overlay | -0.093 | $1.28 | 63 | 33/29 +1 flat | $9.22 | 14.6c | 3/4 | -84.0,416.0,246.0,344.0 |
| 11 | all3_phi_social_pinball | tree_d3_leaf20 | robust_ev_overlay | -0.095 | $-3.76 | 48 | 26/22 | $8.27 | 17.2c | 3/4 | -6.0,480.0,29.0,324.0 |
| 12 | standard6_social_pinball_control | tree_d3_leaf20 | robust_ev_overlay | -0.090 | $-2.52 | 41 | 22/19 | $6.15 | 15.0c | 3/4 | -6.0,480.0,29.0,112.0 |
| 13 | phi_pinball | tree_d3_leaf20 | robust_ev_overlay | -0.096 | $-2.50 | 51 | 24/27 | $5.96 | 11.7c | 3/4 | -6.0,68.0,210.0,324.0 |
| 14 | phi_only | tree_d3_leaf20 | robust_ev_overlay | -0.063 | $0.26 | 51 | 23/28 | $5.34 | 10.5c | 3/4 | -6.0,6.0,210.0,324.0 |
| 15 | phi_pinball | hgb_leaf20_l2 | robust_ev_overlay | -0.187 | $-8.77 | 29 | 16/13 | $5.22 | 18.0c | 3/4 | -50.0,188.0,52.0,332.0 |
| 16 | phi_only | hgb_leaf20_l2 | robust_ev_overlay | -0.137 | $-6.89 | 31 | 15/16 | $4.77 | 15.4c | 3/4 | -92.0,116.0,187.0,266.0 |
| 17 | social_only | tree_d3_leaf20 | robust_ev_overlay | -0.091 | $-3.52 | 36 | 20/16 | $4.62 | 12.8c | 3/4 | 28.0,480.0,64.0,-110.0 |
| 18 | social_pinball | tree_d3_leaf20 | robust_ev_overlay | -0.091 | $-3.52 | 36 | 20/16 | $4.62 | 12.8c | 3/4 | 28.0,480.0,64.0,-110.0 |
| 19 | pinball_only | tree_d2_leaf20 | robust_ev_overlay | -0.008 | $-0.78 | 46 | 23/22 +1 flat | $4.55 | 9.9c | 3/4 | -76.0,198.0,307.0,26.0 |
| 20 | pinball_only | rf_d3_leaf15 | ev_all | -0.044 | $2.67 | 133 | 64/69 | $3.36 | 2.5c | 3/4 | 148.0,191.0,-187.0,184.0 |
| 21 | pinball_only | rf_d3_leaf15 | robust_ev_overlay | -0.044 | $2.67 | 42 | 20/22 | $3.17 | 7.5c | 3/4 | -60.0,206.0,35.0,136.0 |
| 22 | social_pinball | rf_d3_leaf15 | robust_ev_overlay | -0.085 | $-0.51 | 33 | 16/17 | $3.03 | 9.2c | 3/4 | -176.0,154.0,125.0,200.0 |
| 23 | social_only | hgb_leaf20_l2 | robust_ev_overlay | -0.089 | $-4.42 | 26 | 14/12 | $2.51 | 9.7c | 3/4 | -176.0,286.0,131.0,10.0 |
| 24 | all3_phi_social_pinball | hgb_leaf20_l2 | robust_ev_overlay | -0.123 | $-1.39 | 20 | 10/10 | $2.46 | 12.3c | 3/4 | -92.0,6.0,120.0,212.0 |

## Interpretation
- This specifically checks whether the pinball idea behaves better as a shallow path model than as a linear EV model.
- Promotion still requires positive ranking and fresh all-candidate shadow validation.
