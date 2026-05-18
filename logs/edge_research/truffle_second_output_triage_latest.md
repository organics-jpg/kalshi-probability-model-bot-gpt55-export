# Truffle Second Output Triage

Research-only stress test over the current matched filled-trade replay. No live bot logic changed.

- Generated UTC: `2026-05-08T14:37:35.788314+00:00`
- Matched trades: `470`
- Settled labels: `469`

## Probability Sanity Check

| model | window | rows | Brier | log loss | AUC |
|---|---|---:|---:|---:|---:|
| terminal_brownian | train_1_200 | 200 | 0.1714 | 0.5271 | 0.569 |
| terminal_brownian | validation_201_300 | 100 | 0.1941 | 0.5757 | 0.622 |
| terminal_brownian | test_301_end | 169 | 0.1428 | 0.4612 | 0.530 |
| terminal_brownian | forward_after_200 | 269 | 0.1619 | 0.5038 | 0.576 |
| terminal_brownian | all | 469 | 0.1659 | 0.5137 | 0.577 |
| touch_brownian | train_1_200 | 200 | 0.2174 | 2.9770 | 0.508 |
| touch_brownian | validation_201_300 | 100 | 0.2563 | 3.4697 | 0.519 |
| touch_brownian | test_301_end | 169 | 0.1718 | 2.3718 | 0.496 |
| touch_brownian | forward_after_200 | 269 | 0.2032 | 2.7799 | 0.507 |
| touch_brownian | all | 469 | 0.2092 | 2.8640 | 0.507 |
| capped_aci | train_1_200 | 200 | 0.1640 | 0.5094 | 0.640 |
| capped_aci | validation_201_300 | 100 | 0.2026 | 0.6111 | 0.519 |
| capped_aci | test_301_end | 169 | 0.1418 | 0.4545 | 0.602 |
| capped_aci | forward_after_200 | 269 | 0.1644 | 0.5127 | 0.578 |
| capped_aci | all | 469 | 0.1642 | 0.5113 | 0.606 |
| raw_p28 | train_1_200 | 200 | 0.1835 | 0.5833 | 0.503 |
| raw_p28 | validation_201_300 | 100 | 0.2130 | 0.6533 | 0.563 |
| raw_p28 | test_301_end | 169 | 0.1468 | 0.4846 | 0.466 |
| raw_p28 | forward_after_200 | 269 | 0.1714 | 0.5473 | 0.491 |
| raw_p28 | all | 469 | 0.1766 | 0.5626 | 0.497 |

## Best Filled-Trade Overlays

| rank | strategy | train PnL | test entries | test W/L | test PnL | test avg | forward PnL | forward avg |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | robust_plus_brownian_touch_p_side_ge_0.80 | $6.26 | 63 | 34/28 (+1 flat) | $11.06 | 17.6c | $11.34 | 12.6c |
| 2 | robust_plus_brownian_touch_p_side_ge_0.60 | $6.26 | 63 | 34/28 (+1 flat) | $11.06 | 17.6c | $10.58 | 11.6c |
| 3 | robust_plus_brownian_touch_p_side_ge_0.65 | $6.26 | 63 | 34/28 (+1 flat) | $11.06 | 17.6c | $10.58 | 11.6c |
| 4 | robust_plus_brownian_touch_p_side_ge_0.70 | $6.26 | 63 | 34/28 (+1 flat) | $11.06 | 17.6c | $10.58 | 11.6c |
| 5 | robust_plus_brownian_touch_p_side_ge_0.75 | $6.26 | 63 | 34/28 (+1 flat) | $11.06 | 17.6c | $10.58 | 11.6c |
| 6 | robust_plus_brownian_terminal_p_side_ge_0.60 | $5.76 | 62 | 33/28 (+1 flat) | $10.88 | 17.5c | $11.32 | 12.9c |
| 7 | robust_plus_brownian_terminal_p_side_ge_0.65 | $5.20 | 62 | 33/28 (+1 flat) | $10.88 | 17.5c | $11.32 | 12.9c |
| 8 | robust_plus_brownian_touch_p_side_ge_0.85 | $6.26 | 62 | 33/28 (+1 flat) | $10.88 | 17.5c | $11.16 | 12.5c |
| 9 | robust_plus_brownian_terminal_p_side_ge_0.75 | $4.02 | 60 | 32/27 (+1 flat) | $10.46 | 17.4c | $10.70 | 12.6c |
| 10 | robust_plus_brownian_terminal_p_side_ge_0.70 | $4.32 | 61 | 32/28 (+1 flat) | $10.44 | 17.1c | $10.68 | 12.4c |
| 11 | robust_plus_p_calibrated_ge_0.60 | $6.62 | 59 | 31/27 (+1 flat) | $10.12 | 17.2c | $12.76 | 15.4c |
| 12 | robust_plus_brownian_terminal_p_side_ge_0.80 | $1.28 | 57 | 30/26 (+1 flat) | $9.44 | 16.6c | $9.12 | 12.0c |
| 13 | robust_plus_p_calibrated_ge_0.65 | $6.12 | 55 | 29/25 (+1 flat) | $9.24 | 16.8c | $11.84 | 15.4c |
| 14 | robust_plus_p_calibrated_ge_0.70 | $4.62 | 51 | 27/23 (+1 flat) | $8.68 | 17.0c | $11.46 | 16.4c |
| 15 | robust_plus_p_calibrated_ge_0.80 | $4.20 | 39 | 23/15 (+1 flat) | $8.25 | 21.2c | $10.67 | 20.5c |

## E-Process

| strategy | window | entries | best lambda | final capital | max capital | crossed 20 | crossed 100 |
|---|---|---:|---:|---:|---:|---|---|
| robust_hybrid_base | train_1_200 | 67 | 0.35 | 2.33 | 2.52 | no | no |
| robust_hybrid_base | test_301_end | 63 | 0.35 | 5.72 | 5.72 | no | no |
| robust_hybrid_base | forward_after_200 | 91 | 0.35 | 4.21 | 4.21 | no | no |
| robust_hybrid_base | all | 158 | 0.35 | 9.82 | 9.82 | no | no |
| robust_plus_p_cal_ge_0.70 | train_1_200 | 53 | 0.35 | 1.92 | 2.08 | no | no |
| robust_plus_p_cal_ge_0.70 | test_301_end | 51 | 0.35 | 3.96 | 3.96 | no | no |
| robust_plus_p_cal_ge_0.70 | forward_after_200 | 70 | 0.35 | 5.98 | 5.98 | no | no |
| robust_plus_p_cal_ge_0.70 | all | 123 | 0.35 | 11.50 | 11.50 | no | no |
| robust_plus_p_cal_ge_0.80 | train_1_200 | 36 | 0.35 | 1.82 | 1.97 | no | no |
| robust_plus_p_cal_ge_0.80 | test_301_end | 39 | 0.35 | 3.75 | 3.75 | no | no |
| robust_plus_p_cal_ge_0.80 | forward_after_200 | 52 | 0.35 | 5.44 | 5.44 | no | no |
| robust_plus_p_cal_ge_0.80 | all | 88 | 0.35 | 9.91 | 9.91 | no | no |
| robust_plus_touch_ge_0.80 | train_1_200 | 66 | 0.35 | 2.34 | 2.53 | no | no |
| robust_plus_touch_ge_0.80 | test_301_end | 63 | 0.35 | 5.72 | 5.72 | no | no |
| robust_plus_touch_ge_0.80 | forward_after_200 | 90 | 0.35 | 4.86 | 4.86 | no | no |
| robust_plus_touch_ge_0.80 | all | 156 | 0.35 | 11.37 | 11.37 | no | no |
| robust_plus_terminal_ge_0.70 | train_1_200 | 58 | 0.35 | 1.69 | 1.83 | no | no |
| robust_plus_terminal_ge_0.70 | test_301_end | 61 | 0.35 | 5.15 | 5.15 | no | no |
| robust_plus_terminal_ge_0.70 | forward_after_200 | 86 | 0.35 | 4.35 | 4.35 | no | no |
| robust_plus_terminal_ge_0.70 | all | 144 | 0.35 | 7.34 | 7.34 | no | no |

## Settlement Reversion Label Test

| rule | rows | fade W/L | fade win rate |
|---|---:|---:|---:|
| last_180s_dist_ge_0.0002 | 32 | 5/27 | 15.6% |
| last_180s_dist_ge_0.0005 | 10 | 0/10 | 0.0% |
| last_240s_dist_ge_0.0002 | 55 | 10/45 | 18.2% |
| last_240s_dist_ge_0.0005 | 28 | 4/24 | 14.3% |
| last_300s_dist_ge_0.0002 | 86 | 14/72 | 16.3% |
| last_300s_dist_ge_0.0005 | 52 | 7/45 | 13.5% |
| last_300s_dist_ge_0.0010 | 9 | 0/9 | 0.0% |

## Data Readiness

| strategy family | status | missing/caveat |
|---|---|---|
| brownian_bridge_crossing | testable_as_sanity_check | Kalshi resolves terminal above/below strike; touch/crossing probability is not the settlement target. |
| kalshi_spot_lead_lag | not_testable_from_470_row_replay | synchronized 100ms BTC spot ticks; Kalshi quote update timestamps for every tick; counterfactual executable asks before/after lag |
| conformal_predictive_band | partially_testable_only_as_binary_calibration | continuous settlement price label per market; rolling OHLCV feature matrix at every candidate timestamp |
| order_book_imbalance_regime | not_testable_from_matched_trade_rows | top bid/ask depth on both sides at every snapshot; persistent imbalance windows; BTC ATR/ADX regime features |
| settlement_window_mean_reversion | label_testable_not_pnl_testable | opposite-side executable ask/bid near settlement; continuous last-3-minute BTC path; news/event filter |

## Read

- The Brownian bridge/crossing strategy should be reframed as terminal probability for Kalshi settlement; touch probability is overconfident for this label.
- The current best immediate candidate remains the capped-ACI terminal-probability overlay, not pure Brownian crossing.
- Lead-lag, conformal price bands, OBI/regime, and settlement mean reversion all need richer candidate-level logging before honest PnL validation.
