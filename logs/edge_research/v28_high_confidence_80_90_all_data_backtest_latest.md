# 80c vs 90c High-Confidence Backtest

- Source: `research_particle\v28_successor\live_pnl_labeled_decisions_latest.csv`
- Raw joined rows: 16284
- Unique market/time/side observations: 2040
- Unique markets: 188
- Selected FV carrier rows: 1690 across 145 markets
- Assumption: one visible taker contract at side ask, hold to settlement, local v28 fee model.
- Default table uses one entry per market, first eligible row by time.

## Core Price-Only Results
| dataset | window | band | entries | wins | wrong | win rate | net c | avg c | max DD c | remove best c | market LCB c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all_unique_price_only | 5_to_15_min | 80_plus | 74 | 63 | 11 | 0.851 | -165.3 | -2.23 | 459.2 | -183.3 | -8.98 |
| all_unique_price_only | 5_to_15_min | 80_95 | 71 | 60 | 11 | 0.845 | -172.6 | -2.43 | 460.6 | -190.6 | -9.46 |
| all_unique_price_only | 5_to_15_min | 80_90 | 57 | 47 | 10 | 0.825 | -164.0 | -2.88 | 427.0 | -182.0 | -11.17 |
| all_unique_price_only | 5_to_15_min | 85_95 | 53 | 48 | 5 | 0.906 | 32.9 | 0.62 | 325.5 | 18.9 | -5.99 |
| all_unique_price_only | 5_to_15_min | 90_plus | 39 | 38 | 1 | 0.974 | 157.8 | 4.05 | 94.8 | 148.8 | -0.26 |
| all_unique_price_only | 5_to_15_min | 90_95 | 34 | 33 | 1 | 0.971 | 145.7 | 4.29 | 94.8 | 136.7 | -0.66 |
| all_unique_price_only | 1_to_15_min | 80_plus | 100 | 83 | 12 | 0.830 | -129.2 | -1.29 | 487.3 | -147.2 | -6.55 |
| all_unique_price_only | 1_to_15_min | 80_95 | 83 | 71 | 12 | 0.855 | -148.5 | -1.79 | 491.9 | -166.5 | -8.13 |
| all_unique_price_only | 1_to_15_min | 80_90 | 64 | 54 | 10 | 0.844 | -68.0 | -1.06 | 358.0 | -86.0 | -8.52 |
| all_unique_price_only | 1_to_15_min | 85_95 | 67 | 61 | 6 | 0.910 | 57.4 | 0.86 | 387.1 | 43.4 | -4.91 |
| all_unique_price_only | 1_to_15_min | 90_plus | 74 | 63 | 2 | 0.851 | 142.1 | 1.92 | 185.2 | 133.1 | -1.22 |
| all_unique_price_only | 1_to_15_min | 90_95 | 45 | 43 | 2 | 0.956 | 108.6 | 2.41 | 188.5 | 99.6 | -2.76 |
| all_unique_price_only | last_5_min | 80_plus | 72 | 53 | 2 | 0.736 | 125.7 | 1.75 | 93.7 | 107.7 | -1.43 |
| all_unique_price_only | last_5_min | 80_95 | 29 | 27 | 2 | 0.931 | 99.2 | 3.42 | 93.7 | 81.2 | -4.52 |
| all_unique_price_only | last_5_min | 80_90 | 17 | 16 | 1 | 0.941 | 137.0 | 8.06 | 85.0 | 119.0 | -1.53 |
| all_unique_price_only | last_5_min | 85_95 | 25 | 24 | 1 | 0.960 | 100.9 | 4.04 | 93.7 | 86.9 | -2.73 |
| all_unique_price_only | last_5_min | 90_plus | 65 | 46 | 1 | 0.708 | 40.7 | 0.63 | 93.7 | 33.0 | -1.84 |
| all_unique_price_only | last_5_min | 90_95 | 19 | 18 | 1 | 0.947 | 12.3 | 0.65 | 93.7 | 4.4 | -7.96 |
| selected_fv_carrier | 5_to_15_min | 80_plus | 56 | 47 | 9 | 0.839 | -152.2 | -2.72 | 344.0 | -170.2 | -10.71 |
| selected_fv_carrier | 5_to_15_min | 80_95 | 55 | 46 | 9 | 0.836 | -155.4 | -2.83 | 345.4 | -173.4 | -10.96 |
| selected_fv_carrier | 5_to_15_min | 80_90 | 46 | 37 | 9 | 0.804 | -212.0 | -4.61 | 402.0 | -230.0 | -14.30 |
| selected_fv_carrier | 5_to_15_min | 85_95 | 40 | 37 | 3 | 0.925 | 104.1 | 2.60 | 202.4 | 90.1 | -4.21 |
| selected_fv_carrier | 5_to_15_min | 90_plus | 29 | 29 | 0 | 1.000 | 197.9 | 6.82 | -0.0 | 188.9 | 6.22 |
| selected_fv_carrier | 5_to_15_min | 90_95 | 27 | 27 | 0 | 1.000 | 192.9 | 7.14 | -0.0 | 183.9 | 6.63 |
| selected_fv_carrier | 1_to_15_min | 80_plus | 67 | 56 | 9 | 0.836 | -60.5 | -0.90 | 295.1 | -78.5 | -7.64 |
| selected_fv_carrier | 1_to_15_min | 80_95 | 63 | 54 | 9 | 0.857 | -66.6 | -1.06 | 298.0 | -84.6 | -8.23 |
| selected_fv_carrier | 1_to_15_min | 80_90 | 51 | 42 | 9 | 0.824 | -140.0 | -2.75 | 344.0 | -158.0 | -11.57 |
| selected_fv_carrier | 1_to_15_min | 85_95 | 50 | 47 | 3 | 0.940 | 193.3 | 3.87 | 202.4 | 179.3 | -1.62 |
| selected_fv_carrier | 1_to_15_min | 90_plus | 44 | 40 | 0 | 0.909 | 252.7 | 5.74 | 0.9 | 243.7 | 5.05 |
| selected_fv_carrier | 1_to_15_min | 90_95 | 36 | 36 | 0 | 1.000 | 244.5 | 6.79 | -0.0 | 235.5 | 6.34 |
| selected_fv_carrier | last_5_min | 80_plus | 42 | 33 | 1 | 0.786 | 165.9 | 3.95 | 85.0 | 147.9 | 0.08 |
| selected_fv_carrier | last_5_min | 80_95 | 25 | 24 | 1 | 0.960 | 163.9 | 6.56 | 85.0 | 145.9 | 0.13 |
| selected_fv_carrier | last_5_min | 80_90 | 15 | 14 | 1 | 0.933 | 113.0 | 7.53 | 85.0 | 95.0 | -3.36 |
| selected_fv_carrier | last_5_min | 85_95 | 21 | 21 | 0 | 1.000 | 165.6 | 7.89 | -0.0 | 151.6 | 6.71 |
| selected_fv_carrier | last_5_min | 90_plus | 35 | 27 | 0 | 0.771 | 103.9 | 2.97 | 1.2 | 96.2 | 2.16 |
| selected_fv_carrier | last_5_min | 90_95 | 17 | 17 | 0 | 1.000 | 101.0 | 5.94 | -0.0 | 93.1 | 5.42 |

## Best FV-Filtered Selected-Carrier Results
| window | band | filter | entries | wins | wrong | win rate | net c | avg c | max DD c | market LCB c |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| last_5_min | 85_95 | abs_dsigma_le_3_5 | 21 | 21 | 0 | 1.000 | 165.6 | 7.89 | -0.0 | 6.71 |
| last_5_min | 80_90 | abs_dsigma_le_3_5 | 15 | 14 | 1 | 0.933 | 113.0 | 7.53 | 85.0 | -3.36 |
| 5_to_15_min | 90_95 | abs_dsigma_le_3_5 | 27 | 27 | 0 | 1.000 | 192.9 | 7.14 | -0.0 | 6.63 |
| 5_to_15_min | 90_95 | v28_fair_ge_ask | 12 | 12 | 0 | 1.000 | 83.3 | 6.94 | -0.0 | 6.10 |
| 1_to_15_min | 90_95 | v28_fair_ge_ask | 13 | 13 | 0 | 1.000 | 89.3 | 6.87 | -0.0 | 6.08 |
| 0_to_15_min | 90_95 | v28_fair_ge_ask | 13 | 13 | 0 | 1.000 | 89.3 | 6.87 | -0.0 | 6.08 |
| all_times | 90_95 | v28_fair_ge_ask | 13 | 13 | 0 | 1.000 | 89.3 | 6.87 | -0.0 | 6.08 |
| 5_to_15_min | 90_plus | abs_dsigma_le_3_5 | 29 | 29 | 0 | 1.000 | 197.9 | 6.82 | -0.0 | 6.22 |
| 5_to_15_min | 90_98 | abs_dsigma_le_3_5 | 29 | 29 | 0 | 1.000 | 197.9 | 6.82 | -0.0 | 6.22 |
| 1_to_15_min | 90_95 | abs_dsigma_le_3_5 | 36 | 36 | 0 | 1.000 | 244.5 | 6.79 | -0.0 | 6.34 |
| 0_to_15_min | 90_95 | abs_dsigma_le_3_5 | 36 | 36 | 0 | 1.000 | 244.5 | 6.79 | -0.0 | 6.34 |
| all_times | 90_95 | abs_dsigma_le_3_5 | 36 | 36 | 0 | 1.000 | 244.5 | 6.79 | -0.0 | 6.34 |
| 5_to_15_min | 90_95 | v28_fair_ge_90 | 17 | 17 | 0 | 1.000 | 112.7 | 6.63 | -0.0 | 5.90 |
| 5_to_15_min | 90_95 | v28_fair_ge_85 | 21 | 21 | 0 | 1.000 | 138.6 | 6.60 | -0.0 | 5.96 |
| 5_to_15_min | 90_95 | abs_dsigma_ge_1 | 21 | 21 | 0 | 1.000 | 138.6 | 6.60 | -0.0 | 5.96 |
| last_5_min | 80_95 | abs_dsigma_le_3_5 | 25 | 24 | 1 | 0.960 | 163.9 | 6.56 | 85.0 | 0.13 |
| last_5_min | 88_95 | abs_dsigma_le_3_5 | 19 | 19 | 0 | 1.000 | 124.4 | 6.55 | -0.0 | 5.81 |
| 1_to_15_min | 90_95 | v28_fair_ge_85 | 25 | 25 | 0 | 1.000 | 163.1 | 6.52 | -0.0 | 5.98 |
| 1_to_15_min | 90_95 | abs_dsigma_ge_1 | 25 | 25 | 0 | 1.000 | 163.1 | 6.52 | -0.0 | 5.98 |
| 0_to_15_min | 90_95 | v28_fair_ge_85 | 25 | 25 | 0 | 1.000 | 163.1 | 6.52 | -0.0 | 5.98 |

## Takeaways
- Broad 80c entry is fragile: 80-plus and 80-95 lose in the 1-15 minute window on the full unique dataset.
- 90c entry is much cleaner: 90-95 is strongly positive in 1-15 and 5-15 minute windows.
- The best 80-ish family is not pure 80; it is closer to 85-95 or late-window 80-95.
- Avoid no-upper-cap 99c chasing. At very high asks, correct settlement can still lose after fee/friction.