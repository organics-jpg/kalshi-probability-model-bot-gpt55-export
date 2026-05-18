# Spot Drift Regime Diagnostic

- eligible_run_count: 6
- skipped_run_count: 3
- spec_count: 5
- feature_count: 114460
- selected_count: 107430
- stable_positive_rules: 0
- candidate_ready_for_predeclared_shadow: False
- promotion_safe: False
- conclusion: No simple post-hoc drift/regime rule was positive in every eligible run.

## Rule Summary

| spec | rule | positive_runs | nonzero_runs | selected | pnl_cents | min_run_pnl_cents | stable_positive |
|---|---|---:|---:|---:|---:|---:|---|
| drift13_cap10_fixed65_blend25 | require_market_current_consensus_alignment | 5/6 | 6/6 | 1995 | 2332.0000 | -15686.0000 | False |
| drift13_cap10_fixed65_blend25 | require_abs_drift_ge_1bps | 4/6 | 6/6 | 18005 | 106976.0000 | -16718.0000 | False |
| drift13_cap10_fixed65_blend25 | require_abs_drift_ge_3bps | 4/6 | 6/6 | 16378 | 99527.0000 | -15463.0000 | False |
| drift13_cap10_fixed65_blend25 | base | 4/6 | 6/6 | 21197 | 99481.0000 | -18043.0000 | False |
| drift13_cap10_fixed65_blend25 | require_abs_drift_ge_6bps | 4/6 | 6/6 | 14327 | 88301.0000 | -13118.0000 | False |
| drift13_cap10_fixed65_blend25 | require_drift_aligned_abs_ge_1bps | 4/6 | 6/6 | 11099 | 57320.0000 | -10319.0000 | False |
| drift13_cap10_fixed65_blend25 | require_drift_aligned | 4/6 | 6/6 | 11317 | 57070.0000 | -10544.0000 | False |
| drift13_cap10_fixed65_blend25 | require_drift_aligned_abs_ge_3bps | 4/6 | 6/6 | 10324 | 53896.0000 | -9797.0000 | False |
| drift13_cap10_fixed65_blend25 | skip_drift_against | 4/6 | 6/6 | 14081 | 48168.0000 | -17340.0000 | False |
| drift13_cap10_fixed65_blend25 | require_drift_aligned_near_strike_abs_le_10bps | 4/6 | 6/6 | 8317 | 39911.0000 | -4485.0000 | False |
| drift13_cap10_fixed65_blend25 | skip_against_market_current_consensus | 4/6 | 6/6 | 2985 | 4420.0000 | -14747.0000 | False |
| drift13_cap10_fixed65_blend25 | require_near_strike_abs_le_10bps | 3/6 | 6/6 | 14657 | 59685.0000 | -7782.0000 | False |
| drift5_cap10_rv89_blend50 | require_abs_drift_ge_1bps | 3/6 | 6/6 | 15514 | 45529.0000 | -10185.0000 | False |
| drift34_cap20_rv610_blend50 | require_mid_181_600s | 3/6 | 6/6 | 11131 | 43391.0000 | -18413.0000 | False |
| drift5_cap10_rv89_blend50 | base | 3/6 | 6/6 | 21177 | 42977.0000 | -24211.0000 | False |
| drift5_cap10_rv89_blend50 | require_abs_drift_ge_3bps | 3/6 | 6/6 | 14723 | 39769.0000 | -10578.0000 | False |
| drift13_cap15_rv233_blend50 | require_mid_181_600s | 3/6 | 6/6 | 11137 | 37878.0000 | -17428.0000 | False |
| drift21_cap20_rv377_blend50 | require_mid_181_600s | 3/6 | 6/6 | 11135 | 37512.0000 | -17534.0000 | False |
| drift5_cap10_rv89_blend50 | require_mid_181_600s | 3/6 | 6/6 | 11006 | 35831.0000 | -14916.0000 | False |
| drift5_cap10_rv89_blend50 | require_abs_drift_ge_6bps | 3/6 | 6/6 | 13633 | 34790.0000 | -9535.0000 | False |
| drift13_cap10_fixed65_blend25 | require_mid_181_600s | 3/6 | 6/6 | 11122 | 30905.0000 | -20665.0000 | False |
| drift5_cap10_rv89_blend50 | require_drift_aligned | 3/6 | 6/6 | 12108 | 25638.0000 | -7038.0000 | False |
| drift5_cap10_rv89_blend50 | require_drift_aligned_abs_ge_1bps | 3/6 | 6/6 | 12010 | 25443.0000 | -7289.0000 | False |
| drift5_cap10_rv89_blend50 | skip_drift_against | 3/6 | 6/6 | 17579 | 21861.0000 | -21409.0000 | False |
| drift5_cap10_rv89_blend50 | require_drift_aligned_abs_ge_3bps | 3/6 | 6/6 | 11535 | 21751.0000 | -7248.0000 | False |
| drift5_cap10_rv89_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 3/6 | 6/6 | 8942 | 12849.0000 | -5419.0000 | False |
| drift5_cap10_rv89_blend50 | require_near_strike_abs_le_10bps | 3/6 | 6/6 | 14611 | 11620.0000 | -19367.0000 | False |
| drift5_cap10_rv89_blend50 | require_late_le_300s | 3/6 | 6/6 | 6223 | 11284.0000 | -11760.0000 | False |
| drift13_cap15_rv233_blend50 | require_late_le_300s | 3/6 | 6/6 | 6212 | 10800.0000 | -11836.0000 | False |
| drift13_cap15_rv233_blend50 | require_drift_aligned_abs_ge_1bps | 3/6 | 6/6 | 14425 | 10081.0000 | -14027.0000 | False |
| drift21_cap20_rv377_blend50 | require_late_le_300s | 3/6 | 6/6 | 6203 | 10001.0000 | -12048.0000 | False |
| drift13_cap15_rv233_blend50 | require_drift_aligned | 3/6 | 6/6 | 14635 | 9692.0000 | -14418.0000 | False |
| drift34_cap20_rv610_blend50 | require_late_le_300s | 3/6 | 6/6 | 6234 | 8519.0000 | -12745.0000 | False |
| drift13_cap15_rv233_blend50 | require_drift_aligned_abs_ge_3bps | 3/6 | 6/6 | 13546 | 6544.0000 | -12121.0000 | False |
| drift13_cap10_fixed65_blend25 | require_late_le_300s | 3/6 | 6/6 | 6253 | 6131.0000 | -13516.0000 | False |
| drift13_cap15_rv233_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 3/6 | 6/6 | 11028 | -706.0000 | -12118.0000 | False |
| drift13_cap15_rv233_blend50 | skip_drift_against | 3/6 | 6/6 | 17222 | -1690.0000 | -29703.0000 | False |
| drift13_cap15_rv233_blend50 | require_near_strike_abs_le_10bps | 3/6 | 6/6 | 15096 | -9614.0000 | -28882.0000 | False |
| drift5_cap10_rv89_blend50 | skip_against_market_current_consensus | 3/6 | 6/6 | 5456 | -25096.0000 | -34751.0000 | False |
| drift13_cap15_rv233_blend50 | require_abs_drift_ge_1bps | 2/6 | 6/6 | 18700 | 28784.0000 | -18493.0000 | False |
| drift21_cap20_rv377_blend50 | require_abs_drift_ge_1bps | 2/6 | 6/6 | 19247 | 21930.0000 | -18362.0000 | False |
| drift13_cap15_rv233_blend50 | require_abs_drift_ge_3bps | 2/6 | 6/6 | 17133 | 21530.0000 | -16292.0000 | False |
| drift13_cap15_rv233_blend50 | base | 2/6 | 6/6 | 21678 | 18875.0000 | -33550.0000 | False |
| drift21_cap20_rv377_blend50 | require_abs_drift_ge_3bps | 2/6 | 6/6 | 17222 | 16698.0000 | -15470.0000 | False |
| drift13_cap15_rv233_blend50 | require_abs_drift_ge_6bps | 2/6 | 6/6 | 15077 | 12564.0000 | -16466.0000 | False |
| drift34_cap20_rv610_blend50 | require_abs_drift_ge_1bps | 2/6 | 6/6 | 19448 | 10888.0000 | -19318.0000 | False |
| drift21_cap20_rv377_blend50 | base | 2/6 | 6/6 | 21679 | 8820.0000 | -34242.0000 | False |
| drift21_cap20_rv377_blend50 | require_abs_drift_ge_6bps | 2/6 | 6/6 | 14716 | 7978.0000 | -14838.0000 | False |
| drift34_cap20_rv610_blend50 | require_abs_drift_ge_3bps | 2/6 | 6/6 | 16949 | 7926.0000 | -16960.0000 | False |
| drift21_cap20_rv377_blend50 | require_drift_aligned_abs_ge_1bps | 2/6 | 6/6 | 14749 | 5624.0000 | -13231.0000 | False |
| drift21_cap20_rv377_blend50 | require_drift_aligned | 2/6 | 6/6 | 15044 | 5458.0000 | -13487.0000 | False |
| drift21_cap20_rv377_blend50 | require_drift_aligned_abs_ge_3bps | 2/6 | 6/6 | 13520 | 2521.0000 | -11149.0000 | False |
| drift34_cap20_rv610_blend50 | require_abs_drift_ge_6bps | 2/6 | 6/6 | 14211 | -672.0000 | -13612.0000 | False |
| drift34_cap20_rv610_blend50 | require_drift_aligned | 2/6 | 6/6 | 15086 | -2270.0000 | -14849.0000 | False |
| drift34_cap20_rv610_blend50 | require_drift_aligned_abs_ge_1bps | 2/6 | 6/6 | 14720 | -2774.0000 | -14288.0000 | False |
| drift34_cap20_rv610_blend50 | base | 2/6 | 6/6 | 21699 | -3593.0000 | -37562.0000 | False |
| drift34_cap20_rv610_blend50 | require_drift_aligned_abs_ge_3bps | 2/6 | 6/6 | 13224 | -6024.0000 | -12768.0000 | False |
| drift21_cap20_rv377_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 2/6 | 6/6 | 11430 | -6811.0000 | -11319.0000 | False |
| drift21_cap20_rv377_blend50 | skip_drift_against | 2/6 | 6/6 | 16952 | -8978.0000 | -29258.0000 | False |
| drift34_cap20_rv610_blend50 | skip_drift_against | 2/6 | 6/6 | 16722 | -17517.0000 | -33090.0000 | False |
| drift5_cap10_rv89_blend50 | require_market_current_consensus_alignment | 2/6 | 6/6 | 4358 | -31067.0000 | -36932.0000 | False |
| drift13_cap15_rv233_blend50 | skip_against_market_current_consensus | 2/6 | 6/6 | 6375 | -41642.0000 | -38089.0000 | False |
| drift13_cap15_rv233_blend50 | require_market_current_consensus_alignment | 2/6 | 6/6 | 5251 | -43115.0000 | -39007.0000 | False |
| drift21_cap20_rv377_blend50 | require_market_current_consensus_alignment | 2/6 | 6/6 | 5578 | -48035.0000 | -41656.0000 | False |
| drift34_cap20_rv610_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 1/6 | 6/6 | 11596 | -13856.0000 | -12661.0000 | False |
| drift21_cap20_rv377_blend50 | require_near_strike_abs_le_10bps | 1/6 | 6/6 | 15099 | -19582.0000 | -29893.0000 | False |
| drift34_cap20_rv610_blend50 | require_near_strike_abs_le_10bps | 1/6 | 6/6 | 15135 | -27132.0000 | -33264.0000 | False |
| drift21_cap20_rv377_blend50 | skip_against_market_current_consensus | 1/6 | 6/6 | 6701 | -49312.0000 | -39577.0000 | False |
| drift34_cap20_rv610_blend50 | skip_against_market_current_consensus | 1/6 | 6/6 | 7006 | -56324.0000 | -39794.0000 | False |
| drift34_cap20_rv610_blend50 | require_market_current_consensus_alignment | 1/6 | 6/6 | 5903 | -58461.0000 | -43972.0000 | False |

## Buckets

| spec | type | bucket | selected | win_rate | pnl_cents | avg_pnl_cents | positive_runs |
|---|---|---|---:|---:|---:|---:|---:|
| drift13_cap10_fixed65_blend25 | drift_abs | 000_lt_0_5bps | 2007 | 0.2521 | 9178.0000 | 4.5730 | 4/6 |
| drift13_cap10_fixed65_blend25 | drift_abs | 001_0_5_1bps | 428 | 0.1869 | 1407.0000 | 3.2874 | 4/6 |
| drift13_cap10_fixed65_blend25 | drift_abs | 002_1_3bps | 1627 | 0.2071 | 7449.0000 | 4.5784 | 3/6 |
| drift13_cap10_fixed65_blend25 | drift_abs | 003_3_6bps | 2051 | 0.2413 | 11226.0000 | 5.4734 | 3/6 |
| drift13_cap10_fixed65_blend25 | drift_abs | 004_ge_6bps | 14327 | 0.3556 | 88301.0000 | 6.1633 | 4/6 |
| drift13_cap10_fixed65_blend25 | drift_abs | fallback | 757 | 0.0225 | -18080.0000 | -23.8838 | 1/6 |
| drift13_cap10_fixed65_blend25 | drift_alignment | against_drift | 7116 | 0.2295 | 51313.0000 | 7.2109 | 5/6 |
| drift13_cap10_fixed65_blend25 | drift_alignment | aligned_with_drift | 11317 | 0.3864 | 57070.0000 | 5.0429 | 4/6 |
| drift13_cap10_fixed65_blend25 | drift_alignment | flat_or_fallback | 2764 | 0.1892 | -8902.0000 | -3.2207 | 3/6 |
| drift13_cap10_fixed65_blend25 | drift_sign | fallback | 757 | 0.0225 | -18080.0000 | -23.8838 | 1/6 |
| drift13_cap10_fixed65_blend25 | drift_sign | flat | 2007 | 0.2521 | 9178.0000 | 4.5730 | 4/6 |
| drift13_cap10_fixed65_blend25 | drift_sign | negative | 8929 | 0.3432 | 60600.0000 | 6.7869 | 5/6 |
| drift13_cap10_fixed65_blend25 | drift_sign | positive | 9504 | 0.3096 | 47783.0000 | 5.0277 | 3/6 |
| drift13_cap10_fixed65_blend25 | market_current_consensus | against_market_current | 18212 | 0.2615 | 95061.0000 | 5.2197 | 3/6 |
| drift13_cap10_fixed65_blend25 | market_current_consensus | aligned_with_market_current | 1995 | 0.6266 | 2332.0000 | 1.1689 | 5/6 |
| drift13_cap10_fixed65_blend25 | market_current_consensus | market_current_disagree | 990 | 0.5222 | 2088.0000 | 2.1091 | 3/6 |
| drift13_cap10_fixed65_blend25 | moneyness_abs | 000_le_5bps | 8044 | 0.4168 | 485.0000 | 0.0603 | 3/6 |
| drift13_cap10_fixed65_blend25 | moneyness_abs | 001_5_10bps | 6613 | 0.3123 | 59200.0000 | 8.9521 | 4/6 |
| drift13_cap10_fixed65_blend25 | moneyness_abs | 002_10_20bps | 5577 | 0.1958 | 41827.0000 | 7.4999 | 3/6 |
| drift13_cap10_fixed65_blend25 | moneyness_abs | 003_20_40bps | 855 | 0.0082 | -1926.0000 | -2.2526 | 0/6 |
| drift13_cap10_fixed65_blend25 | moneyness_abs | 004_gt_40bps | 108 | 0.1111 | -105.0000 | -0.9722 | 0/6 |
| drift13_cap10_fixed65_blend25 | moneyness_sign | spot_above_strike | 7805 | 0.2762 | 73204.0000 | 9.3791 | 3/6 |
| drift13_cap10_fixed65_blend25 | moneyness_sign | spot_below_strike | 9674 | 0.2853 | 29813.0000 | 3.0818 | 3/6 |
| drift13_cap10_fixed65_blend25 | moneyness_sign | spot_near_strike | 3718 | 0.4338 | -3536.0000 | -0.9510 | 4/6 |
| drift13_cap10_fixed65_blend25 | side | no | 11082 | 0.3264 | 69424.0000 | 6.2646 | 3/6 |
| drift13_cap10_fixed65_blend25 | side | yes | 10115 | 0.2879 | 30057.0000 | 2.9715 | 3/6 |
| drift13_cap10_fixed65_blend25 | time_to_close | 000_060s | 375 | 0.0027 | -723.0000 | -1.9280 | 0/6 |
| drift13_cap10_fixed65_blend25 | time_to_close | 061_180s | 2638 | 0.0804 | -7449.0000 | -2.8237 | 1/6 |
| drift13_cap10_fixed65_blend25 | time_to_close | 181_300s | 3240 | 0.1701 | 14303.0000 | 4.4145 | 3/6 |
| drift13_cap10_fixed65_blend25 | time_to_close | 301_600s | 7882 | 0.2780 | 16602.0000 | 2.1063 | 3/6 |
| drift13_cap10_fixed65_blend25 | time_to_close | gt_600s | 7062 | 0.5061 | 76748.0000 | 10.8677 | 5/6 |
| drift13_cap15_rv233_blend50 | drift_abs | 000_lt_0_5bps | 1835 | 0.2289 | 5779.0000 | 3.1493 | 4/6 |
| drift13_cap15_rv233_blend50 | drift_abs | 001_0_5_1bps | 391 | 0.1816 | 1473.0000 | 3.7673 | 3/6 |
| drift13_cap15_rv233_blend50 | drift_abs | 002_1_3bps | 1567 | 0.2221 | 7254.0000 | 4.6292 | 3/6 |
| drift13_cap15_rv233_blend50 | drift_abs | 003_3_6bps | 2056 | 0.2753 | 8966.0000 | 4.3609 | 5/6 |
| drift13_cap15_rv233_blend50 | drift_abs | 004_ge_6bps | 15077 | 0.3907 | 12564.0000 | 0.8333 | 2/6 |
| drift13_cap15_rv233_blend50 | drift_abs | fallback | 752 | 0.0332 | -17161.0000 | -22.8205 | 0/6 |
| drift13_cap15_rv233_blend50 | drift_alignment | against_drift | 4456 | 0.1333 | 20565.0000 | 4.6151 | 2/6 |
| drift13_cap15_rv233_blend50 | drift_alignment | aligned_with_drift | 14635 | 0.4292 | 9692.0000 | 0.6622 | 3/6 |
| drift13_cap15_rv233_blend50 | drift_alignment | flat_or_fallback | 2587 | 0.1720 | -11382.0000 | -4.3997 | 3/6 |
| drift13_cap15_rv233_blend50 | drift_sign | fallback | 752 | 0.0332 | -17161.0000 | -22.8205 | 0/6 |
| drift13_cap15_rv233_blend50 | drift_sign | flat | 1835 | 0.2289 | 5779.0000 | 3.1493 | 4/6 |
| drift13_cap15_rv233_blend50 | drift_sign | negative | 9448 | 0.3979 | 29656.0000 | 3.1389 | 4/6 |
| drift13_cap15_rv233_blend50 | drift_sign | positive | 9643 | 0.3232 | 601.0000 | 0.0623 | 3/6 |
| drift13_cap15_rv233_blend50 | market_current_consensus | against_market_current | 15303 | 0.2344 | 60517.0000 | 3.9546 | 3/6 |
| drift13_cap15_rv233_blend50 | market_current_consensus | aligned_with_market_current | 5251 | 0.5955 | -43115.0000 | -8.2108 | 2/6 |
| drift13_cap15_rv233_blend50 | market_current_consensus | market_current_disagree | 1124 | 0.5400 | 1473.0000 | 1.3105 | 3/6 |
| drift13_cap15_rv233_blend50 | moneyness_abs | 000_le_5bps | 8593 | 0.4418 | -23174.0000 | -2.6968 | 3/6 |
| drift13_cap15_rv233_blend50 | moneyness_abs | 001_5_10bps | 6503 | 0.3308 | 13560.0000 | 2.0852 | 3/6 |
| drift13_cap15_rv233_blend50 | moneyness_abs | 002_10_20bps | 5646 | 0.2347 | 29885.0000 | 5.2931 | 2/6 |
| drift13_cap15_rv233_blend50 | moneyness_abs | 003_20_40bps | 835 | 0.0407 | -1318.0000 | -1.5784 | 0/6 |
| drift13_cap15_rv233_blend50 | moneyness_abs | 004_gt_40bps | 101 | 0.1485 | -78.0000 | -0.7723 | 0/6 |
| drift13_cap15_rv233_blend50 | moneyness_sign | spot_above_strike | 7797 | 0.2964 | 38056.0000 | 4.8809 | 2/6 |
| drift13_cap15_rv233_blend50 | moneyness_sign | spot_below_strike | 9916 | 0.3304 | -7196.0000 | -0.7257 | 1/6 |
| drift13_cap15_rv233_blend50 | moneyness_sign | spot_near_strike | 3965 | 0.4373 | -11985.0000 | -3.0227 | 3/6 |
| drift13_cap15_rv233_blend50 | side | no | 11725 | 0.3637 | 30971.0000 | 2.6414 | 3/6 |
| drift13_cap15_rv233_blend50 | side | yes | 9953 | 0.3071 | -12096.0000 | -1.2153 | 2/6 |
| drift13_cap15_rv233_blend50 | time_to_close | 000_060s | 371 | 0.0027 | -639.0000 | -1.7224 | 0/6 |
| drift13_cap15_rv233_blend50 | time_to_close | 061_180s | 2618 | 0.0871 | -7227.0000 | -2.7605 | 1/6 |
| drift13_cap15_rv233_blend50 | time_to_close | 181_300s | 3223 | 0.2014 | 18666.0000 | 5.7915 | 3/6 |
| drift13_cap15_rv233_blend50 | time_to_close | 301_600s | 7914 | 0.3515 | 19212.0000 | 2.4276 | 2/6 |
| drift13_cap15_rv233_blend50 | time_to_close | gt_600s | 7552 | 0.4848 | -11137.0000 | -1.4747 | 3/6 |
| drift21_cap20_rv377_blend50 | drift_abs | 000_lt_0_5bps | 1152 | 0.1944 | 1835.0000 | 1.5929 | 4/6 |
| drift21_cap20_rv377_blend50 | drift_abs | 001_0_5_1bps | 524 | 0.1832 | 1326.0000 | 2.5305 | 3/6 |
| drift21_cap20_rv377_blend50 | drift_abs | 002_1_3bps | 2025 | 0.2207 | 5232.0000 | 2.5837 | 2/6 |
| drift21_cap20_rv377_blend50 | drift_abs | 003_3_6bps | 2506 | 0.2829 | 8720.0000 | 3.4796 | 3/6 |
| drift21_cap20_rv377_blend50 | drift_abs | 004_ge_6bps | 14716 | 0.3958 | 7978.0000 | 0.5421 | 2/6 |
| drift21_cap20_rv377_blend50 | drift_abs | fallback | 756 | 0.0489 | -16271.0000 | -21.5225 | 0/6 |
| drift21_cap20_rv377_blend50 | drift_alignment | against_drift | 4727 | 0.1263 | 17798.0000 | 3.7652 | 2/6 |
| drift21_cap20_rv377_blend50 | drift_alignment | aligned_with_drift | 15044 | 0.4307 | 5458.0000 | 0.3628 | 2/6 |
| drift21_cap20_rv377_blend50 | drift_alignment | flat_or_fallback | 1908 | 0.1368 | -14436.0000 | -7.5660 | 3/6 |
| drift21_cap20_rv377_blend50 | drift_sign | fallback | 756 | 0.0489 | -16271.0000 | -21.5225 | 0/6 |
| drift21_cap20_rv377_blend50 | drift_sign | flat | 1152 | 0.1944 | 1835.0000 | 1.5929 | 4/6 |
| drift21_cap20_rv377_blend50 | drift_sign | negative | 9912 | 0.3908 | 28011.0000 | 2.8260 | 4/6 |
| drift21_cap20_rv377_blend50 | drift_sign | positive | 9859 | 0.3249 | -4755.0000 | -0.4823 | 3/6 |
| drift21_cap20_rv377_blend50 | market_current_consensus | against_market_current | 14978 | 0.2306 | 58132.0000 | 3.8812 | 3/6 |
| drift21_cap20_rv377_blend50 | market_current_consensus | aligned_with_market_current | 5578 | 0.5927 | -48035.0000 | -8.6115 | 2/6 |
| drift21_cap20_rv377_blend50 | market_current_consensus | market_current_disagree | 1123 | 0.5147 | -1277.0000 | -1.1371 | 2/6 |
| drift21_cap20_rv377_blend50 | moneyness_abs | 000_le_5bps | 8570 | 0.4352 | -30394.0000 | -3.5466 | 3/6 |
| drift21_cap20_rv377_blend50 | moneyness_abs | 001_5_10bps | 6529 | 0.3362 | 10812.0000 | 1.6560 | 3/6 |
| drift21_cap20_rv377_blend50 | moneyness_abs | 002_10_20bps | 5649 | 0.2397 | 29531.0000 | 5.2277 | 2/6 |
| drift21_cap20_rv377_blend50 | moneyness_abs | 003_20_40bps | 833 | 0.0516 | -1057.0000 | -1.2689 | 0/6 |
| drift21_cap20_rv377_blend50 | moneyness_abs | 004_gt_40bps | 98 | 0.1633 | -72.0000 | -0.7347 | 0/6 |
| drift21_cap20_rv377_blend50 | moneyness_sign | spot_above_strike | 7786 | 0.2998 | 34438.0000 | 4.4231 | 2/6 |
| drift21_cap20_rv377_blend50 | moneyness_sign | spot_below_strike | 9936 | 0.3331 | -10884.0000 | -1.0954 | 1/6 |
| drift21_cap20_rv377_blend50 | moneyness_sign | spot_near_strike | 3957 | 0.4281 | -14734.0000 | -3.7235 | 4/6 |
| drift21_cap20_rv377_blend50 | side | no | 11587 | 0.3614 | 24144.0000 | 2.0837 | 3/6 |
| drift21_cap20_rv377_blend50 | side | yes | 10092 | 0.3121 | -15324.0000 | -1.5184 | 2/6 |
| drift21_cap20_rv377_blend50 | time_to_close | 000_060s | 371 | 0.0216 | -218.0000 | -0.5876 | 1/6 |
| drift21_cap20_rv377_blend50 | time_to_close | 061_180s | 2609 | 0.0928 | -5982.0000 | -2.2928 | 1/6 |
| drift21_cap20_rv377_blend50 | time_to_close | 181_300s | 3223 | 0.1955 | 16201.0000 | 5.0267 | 3/6 |
| drift21_cap20_rv377_blend50 | time_to_close | 301_600s | 7912 | 0.3583 | 21311.0000 | 2.6935 | 2/6 |
| drift21_cap20_rv377_blend50 | time_to_close | gt_600s | 7564 | 0.4790 | -22492.0000 | -2.9736 | 2/6 |
| drift34_cap20_rv610_blend50 | drift_abs | 000_lt_0_5bps | 879 | 0.1843 | 1093.0000 | 1.2435 | 3/6 |
| drift34_cap20_rv610_blend50 | drift_abs | 001_0_5_1bps | 615 | 0.1577 | 766.0000 | 1.2455 | 2/6 |
| drift34_cap20_rv610_blend50 | drift_abs | 002_1_3bps | 2499 | 0.1861 | 2962.0000 | 1.1853 | 3/6 |
| drift34_cap20_rv610_blend50 | drift_abs | 003_3_6bps | 2738 | 0.2867 | 8598.0000 | 3.1402 | 3/6 |
| drift34_cap20_rv610_blend50 | drift_abs | 004_ge_6bps | 14211 | 0.4057 | -672.0000 | -0.0473 | 2/6 |
| drift34_cap20_rv610_blend50 | drift_abs | fallback | 757 | 0.0489 | -16340.0000 | -21.5852 | 0/6 |
| drift34_cap20_rv610_blend50 | drift_alignment | against_drift | 4977 | 0.1175 | 13924.0000 | 2.7977 | 2/6 |
| drift34_cap20_rv610_blend50 | drift_alignment | aligned_with_drift | 15086 | 0.4327 | -2270.0000 | -0.1505 | 2/6 |
| drift34_cap20_rv610_blend50 | drift_alignment | flat_or_fallback | 1636 | 0.1216 | -15247.0000 | -9.3197 | 2/6 |
| drift34_cap20_rv610_blend50 | drift_sign | fallback | 757 | 0.0489 | -16340.0000 | -21.5852 | 0/6 |
| drift34_cap20_rv610_blend50 | drift_sign | flat | 879 | 0.1843 | 1093.0000 | 1.2435 | 3/6 |
| drift34_cap20_rv610_blend50 | drift_sign | negative | 10063 | 0.3863 | 26539.0000 | 2.6373 | 4/6 |
| drift34_cap20_rv610_blend50 | drift_sign | positive | 10000 | 0.3226 | -14885.0000 | -1.4885 | 2/6 |
| drift34_cap20_rv610_blend50 | market_current_consensus | against_market_current | 14693 | 0.2245 | 52731.0000 | 3.5889 | 3/6 |
| drift34_cap20_rv610_blend50 | market_current_consensus | aligned_with_market_current | 5903 | 0.5785 | -58461.0000 | -9.9036 | 1/6 |
| drift34_cap20_rv610_blend50 | market_current_consensus | market_current_disagree | 1103 | 0.5431 | 2137.0000 | 1.9374 | 2/6 |
| drift34_cap20_rv610_blend50 | moneyness_abs | 000_le_5bps | 8592 | 0.4259 | -37971.0000 | -4.4193 | 2/6 |
| drift34_cap20_rv610_blend50 | moneyness_abs | 001_5_10bps | 6543 | 0.3413 | 10839.0000 | 1.6566 | 2/6 |
| drift34_cap20_rv610_blend50 | moneyness_abs | 002_10_20bps | 5656 | 0.2389 | 24273.0000 | 4.2915 | 2/6 |
| drift34_cap20_rv610_blend50 | moneyness_abs | 003_20_40bps | 815 | 0.0650 | -672.0000 | -0.8245 | 0/6 |
| drift34_cap20_rv610_blend50 | moneyness_abs | 004_gt_40bps | 93 | 0.1720 | -62.0000 | -0.6667 | 0/6 |
| drift34_cap20_rv610_blend50 | moneyness_sign | spot_above_strike | 7783 | 0.2932 | 25911.0000 | 3.3292 | 1/6 |
| drift34_cap20_rv610_blend50 | moneyness_sign | spot_below_strike | 9992 | 0.3393 | -10941.0000 | -1.0950 | 1/6 |
| drift34_cap20_rv610_blend50 | moneyness_sign | spot_near_strike | 3924 | 0.4179 | -18563.0000 | -4.7306 | 4/6 |
| drift34_cap20_rv610_blend50 | side | no | 11487 | 0.3567 | 16027.0000 | 1.3952 | 3/6 |
| drift34_cap20_rv610_blend50 | side | yes | 10212 | 0.3148 | -19620.0000 | -1.9213 | 2/6 |
| drift34_cap20_rv610_blend50 | time_to_close | 000_060s | 373 | 0.0322 | -67.0000 | -0.1796 | 1/6 |
| drift34_cap20_rv610_blend50 | time_to_close | 061_180s | 2631 | 0.0977 | -5224.0000 | -1.9856 | 2/6 |
| drift34_cap20_rv610_blend50 | time_to_close | 181_300s | 3230 | 0.1867 | 13810.0000 | 4.2755 | 3/6 |
| drift34_cap20_rv610_blend50 | time_to_close | 301_600s | 7901 | 0.3681 | 29581.0000 | 3.7440 | 3/6 |
| drift34_cap20_rv610_blend50 | time_to_close | gt_600s | 7564 | 0.4669 | -41693.0000 | -5.5120 | 3/6 |
| drift5_cap10_rv89_blend50 | drift_abs | 000_lt_0_5bps | 4709 | 0.2459 | 14477.0000 | 3.0743 | 5/6 |
| drift5_cap10_rv89_blend50 | drift_abs | 001_0_5_1bps | 192 | 0.2500 | 1225.0000 | 6.3802 | 3/6 |
| drift5_cap10_rv89_blend50 | drift_abs | 002_1_3bps | 791 | 0.2541 | 5760.0000 | 7.2819 | 5/6 |
| drift5_cap10_rv89_blend50 | drift_abs | 003_3_6bps | 1090 | 0.2367 | 4979.0000 | 4.5679 | 4/6 |
| drift5_cap10_rv89_blend50 | drift_abs | 004_ge_6bps | 13633 | 0.3880 | 34790.0000 | 2.5519 | 3/6 |
| drift5_cap10_rv89_blend50 | drift_abs | fallback | 762 | 0.0210 | -18254.0000 | -23.9554 | 0/6 |
| drift5_cap10_rv89_blend50 | drift_alignment | against_drift | 3598 | 0.1487 | 21116.0000 | 5.8688 | 2/6 |
| drift5_cap10_rv89_blend50 | drift_alignment | aligned_with_drift | 12108 | 0.4346 | 25638.0000 | 2.1174 | 3/6 |
| drift5_cap10_rv89_blend50 | drift_alignment | flat_or_fallback | 5471 | 0.2146 | -3777.0000 | -0.6904 | 4/6 |
| drift5_cap10_rv89_blend50 | drift_sign | fallback | 762 | 0.0210 | -18254.0000 | -23.9554 | 0/6 |
| drift5_cap10_rv89_blend50 | drift_sign | flat | 4709 | 0.2459 | 14477.0000 | 3.0743 | 5/6 |
| drift5_cap10_rv89_blend50 | drift_sign | negative | 7801 | 0.4032 | 28226.0000 | 3.6183 | 4/6 |
| drift5_cap10_rv89_blend50 | drift_sign | positive | 7905 | 0.3355 | 18528.0000 | 2.3438 | 3/6 |
| drift5_cap10_rv89_blend50 | market_current_consensus | against_market_current | 15721 | 0.2378 | 68073.0000 | 4.3301 | 3/6 |
| drift5_cap10_rv89_blend50 | market_current_consensus | aligned_with_market_current | 4358 | 0.5987 | -31067.0000 | -7.1287 | 2/6 |
| drift5_cap10_rv89_blend50 | market_current_consensus | market_current_disagree | 1098 | 0.5674 | 5971.0000 | 5.4381 | 4/6 |
| drift5_cap10_rv89_blend50 | moneyness_abs | 000_le_5bps | 8187 | 0.4422 | -8769.0000 | -1.0711 | 2/6 |
| drift5_cap10_rv89_blend50 | moneyness_abs | 001_5_10bps | 6424 | 0.3185 | 20389.0000 | 3.1739 | 3/6 |
| drift5_cap10_rv89_blend50 | moneyness_abs | 002_10_20bps | 5621 | 0.2258 | 32938.0000 | 5.8598 | 2/6 |
| drift5_cap10_rv89_blend50 | moneyness_abs | 003_20_40bps | 848 | 0.0307 | -1486.0000 | -1.7524 | 0/6 |
| drift5_cap10_rv89_blend50 | moneyness_abs | 004_gt_40bps | 97 | 0.1031 | -95.0000 | -0.9794 | 0/6 |
| drift5_cap10_rv89_blend50 | moneyness_sign | spot_above_strike | 7707 | 0.2909 | 51145.0000 | 6.6362 | 2/6 |
| drift5_cap10_rv89_blend50 | moneyness_sign | spot_below_strike | 9638 | 0.3128 | -4265.0000 | -0.4425 | 2/6 |
| drift5_cap10_rv89_blend50 | moneyness_sign | spot_near_strike | 3832 | 0.4473 | -3903.0000 | -1.0185 | 3/6 |
| drift5_cap10_rv89_blend50 | side | no | 11758 | 0.3584 | 42037.0000 | 3.5752 | 3/6 |
| drift5_cap10_rv89_blend50 | side | yes | 9419 | 0.2927 | 940.0000 | 0.0998 | 3/6 |
| drift5_cap10_rv89_blend50 | time_to_close | 000_060s | 372 | 0.0108 | -534.0000 | -1.4355 | 0/6 |
| drift5_cap10_rv89_blend50 | time_to_close | 061_180s | 2625 | 0.0823 | -7252.0000 | -2.7627 | 1/6 |
| drift5_cap10_rv89_blend50 | time_to_close | 181_300s | 3226 | 0.1999 | 19070.0000 | 5.9113 | 3/6 |
| drift5_cap10_rv89_blend50 | time_to_close | 301_600s | 7780 | 0.3316 | 16761.0000 | 2.1544 | 3/6 |
| drift5_cap10_rv89_blend50 | time_to_close | gt_600s | 7174 | 0.4915 | 14932.0000 | 2.0814 | 2/6 |

## Rule By Run

| run | spec | rule | selected | win_rate | pnl_cents |
|---|---|---|---:|---:|---:|
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift5_cap10_rv89_blend50 | base | 2918 | 0.2666 | -9971.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift5_cap10_rv89_blend50 | require_drift_aligned | 1952 | 0.3673 | -5495.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift5_cap10_rv89_blend50 | skip_drift_against | 2293 | 0.3332 | -6945.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift5_cap10_rv89_blend50 | require_abs_drift_ge_1bps | 2562 | 0.2849 | -8426.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift5_cap10_rv89_blend50 | require_abs_drift_ge_3bps | 2469 | 0.2920 | -7887.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift5_cap10_rv89_blend50 | require_abs_drift_ge_6bps | 2341 | 0.3029 | -7307.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift5_cap10_rv89_blend50 | require_drift_aligned_abs_ge_1bps | 1946 | 0.3684 | -5406.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift5_cap10_rv89_blend50 | require_drift_aligned_abs_ge_3bps | 1897 | 0.3753 | -4942.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift5_cap10_rv89_blend50 | require_late_le_300s | 845 | 0.0651 | -2265.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift5_cap10_rv89_blend50 | require_mid_181_600s | 1381 | 0.1586 | -7455.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift5_cap10_rv89_blend50 | require_near_strike_abs_le_10bps | 1117 | 0.4252 | -4541.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift5_cap10_rv89_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 890 | 0.4798 | -3015.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift5_cap10_rv89_blend50 | require_market_current_consensus_alignment | 721 | 0.8821 | 12448.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift5_cap10_rv89_blend50 | skip_against_market_current_consensus | 780 | 0.8551 | 12610.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap15_rv233_blend50 | base | 3058 | 0.3061 | -8724.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap15_rv233_blend50 | require_drift_aligned | 2279 | 0.4006 | -5076.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap15_rv233_blend50 | skip_drift_against | 2408 | 0.3850 | -5788.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap15_rv233_blend50 | require_abs_drift_ge_1bps | 2891 | 0.3186 | -7664.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap15_rv233_blend50 | require_abs_drift_ge_3bps | 2697 | 0.3348 | -7012.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap15_rv233_blend50 | require_abs_drift_ge_6bps | 2444 | 0.3601 | -4578.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap15_rv233_blend50 | require_drift_aligned_abs_ge_1bps | 2260 | 0.4040 | -4851.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap15_rv233_blend50 | require_drift_aligned_abs_ge_3bps | 2173 | 0.4128 | -4598.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap15_rv233_blend50 | require_late_le_300s | 842 | 0.0606 | -2988.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap15_rv233_blend50 | require_mid_181_600s | 1430 | 0.1923 | -7608.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap15_rv233_blend50 | require_near_strike_abs_le_10bps | 1232 | 0.4497 | -5287.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap15_rv233_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 1101 | 0.4850 | -4302.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap15_rv233_blend50 | require_market_current_consensus_alignment | 910 | 0.8714 | 13942.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap15_rv233_blend50 | skip_against_market_current_consensus | 971 | 0.8435 | 13379.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift21_cap20_rv377_blend50 | base | 3061 | 0.3146 | -9849.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift21_cap20_rv377_blend50 | require_drift_aligned | 2327 | 0.4074 | -6083.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift21_cap20_rv377_blend50 | skip_drift_against | 2404 | 0.3981 | -6805.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift21_cap20_rv377_blend50 | require_abs_drift_ge_1bps | 2939 | 0.3239 | -8937.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift21_cap20_rv377_blend50 | require_abs_drift_ge_3bps | 2698 | 0.3454 | -7114.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift21_cap20_rv377_blend50 | require_abs_drift_ge_6bps | 2345 | 0.3744 | -5213.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift21_cap20_rv377_blend50 | require_drift_aligned_abs_ge_1bps | 2299 | 0.4115 | -5985.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift21_cap20_rv377_blend50 | require_drift_aligned_abs_ge_3bps | 2172 | 0.4268 | -4588.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift21_cap20_rv377_blend50 | require_late_le_300s | 842 | 0.0689 | -2983.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift21_cap20_rv377_blend50 | require_mid_181_600s | 1431 | 0.2089 | -6816.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift21_cap20_rv377_blend50 | require_near_strike_abs_le_10bps | 1238 | 0.4426 | -7592.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift21_cap20_rv377_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 1128 | 0.4761 | -6344.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift21_cap20_rv377_blend50 | require_market_current_consensus_alignment | 984 | 0.8526 | 12975.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift21_cap20_rv377_blend50 | skip_against_market_current_consensus | 1044 | 0.8266 | 12228.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift34_cap20_rv610_blend50 | base | 3034 | 0.3161 | -9784.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift34_cap20_rv610_blend50 | require_drift_aligned | 2281 | 0.4060 | -7357.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift34_cap20_rv610_blend50 | skip_drift_against | 2357 | 0.3967 | -7429.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift34_cap20_rv610_blend50 | require_abs_drift_ge_1bps | 2901 | 0.3264 | -9116.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift34_cap20_rv610_blend50 | require_abs_drift_ge_3bps | 2560 | 0.3563 | -6337.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift34_cap20_rv610_blend50 | require_abs_drift_ge_6bps | 2256 | 0.3657 | -6905.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift34_cap20_rv610_blend50 | require_drift_aligned_abs_ge_1bps | 2248 | 0.4110 | -6792.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift34_cap20_rv610_blend50 | require_drift_aligned_abs_ge_3bps | 2063 | 0.4353 | -4326.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift34_cap20_rv610_blend50 | require_late_le_300s | 845 | 0.0627 | -3398.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift34_cap20_rv610_blend50 | require_mid_181_600s | 1395 | 0.1907 | -8263.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift34_cap20_rv610_blend50 | require_near_strike_abs_le_10bps | 1232 | 0.4294 | -8252.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift34_cap20_rv610_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 1128 | 0.4459 | -8664.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift34_cap20_rv610_blend50 | require_market_current_consensus_alignment | 981 | 0.8512 | 12708.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift34_cap20_rv610_blend50 | skip_against_market_current_consensus | 1046 | 0.8260 | 12402.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap10_fixed65_blend25 | base | 2901 | 0.1886 | -18043.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap10_fixed65_blend25 | require_drift_aligned | 1804 | 0.2711 | -10544.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap10_fixed65_blend25 | skip_drift_against | 1957 | 0.2591 | -11562.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap10_fixed65_blend25 | require_abs_drift_ge_1bps | 2709 | 0.1949 | -16718.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap10_fixed65_blend25 | require_abs_drift_ge_3bps | 2504 | 0.2061 | -15463.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap10_fixed65_blend25 | require_abs_drift_ge_6bps | 2258 | 0.2228 | -13118.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap10_fixed65_blend25 | require_drift_aligned_abs_ge_1bps | 1782 | 0.2738 | -10319.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap10_fixed65_blend25 | require_drift_aligned_abs_ge_3bps | 1697 | 0.2817 | -9797.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap10_fixed65_blend25 | require_late_le_300s | 845 | 0.0604 | -2606.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap10_fixed65_blend25 | require_mid_181_600s | 1408 | 0.0852 | -13355.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap10_fixed65_blend25 | require_near_strike_abs_le_10bps | 1168 | 0.3741 | -6378.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap10_fixed65_blend25 | require_drift_aligned_near_strike_abs_le_10bps | 885 | 0.4282 | -4485.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap10_fixed65_blend25 | require_market_current_consensus_alignment | 421 | 0.8670 | 8403.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap10_fixed65_blend25 | skip_against_market_current_consensus | 475 | 0.8105 | 7765.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift5_cap10_rv89_blend50 | base | 3119 | 0.3687 | -4309.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift5_cap10_rv89_blend50 | require_drift_aligned | 2365 | 0.4461 | -2986.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift5_cap10_rv89_blend50 | skip_drift_against | 2640 | 0.4295 | -2935.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift5_cap10_rv89_blend50 | require_abs_drift_ge_1bps | 2827 | 0.3771 | -4391.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift5_cap10_rv89_blend50 | require_abs_drift_ge_3bps | 2699 | 0.3831 | -4796.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift5_cap10_rv89_blend50 | require_abs_drift_ge_6bps | 2562 | 0.3911 | -4824.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift5_cap10_rv89_blend50 | require_drift_aligned_abs_ge_1bps | 2355 | 0.4471 | -2841.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift5_cap10_rv89_blend50 | require_drift_aligned_abs_ge_3bps | 2274 | 0.4490 | -3594.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift5_cap10_rv89_blend50 | require_late_le_300s | 796 | 0.1621 | 2561.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift5_cap10_rv89_blend50 | require_mid_181_600s | 1579 | 0.3667 | 4112.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift5_cap10_rv89_blend50 | require_near_strike_abs_le_10bps | 1997 | 0.4932 | 985.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift5_cap10_rv89_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 1736 | 0.5173 | 43.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift5_cap10_rv89_blend50 | require_market_current_consensus_alignment | 979 | 0.2860 | -36932.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift5_cap10_rv89_blend50 | skip_against_market_current_consensus | 1171 | 0.3450 | -34751.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap15_rv233_blend50 | base | 3235 | 0.3740 | -5107.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap15_rv233_blend50 | require_drift_aligned | 2599 | 0.4471 | -3870.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap15_rv233_blend50 | skip_drift_against | 2684 | 0.4434 | -3600.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap15_rv233_blend50 | require_abs_drift_ge_1bps | 3103 | 0.3780 | -5307.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap15_rv233_blend50 | require_abs_drift_ge_3bps | 2949 | 0.3839 | -5742.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap15_rv233_blend50 | require_abs_drift_ge_6bps | 2705 | 0.3933 | -6110.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap15_rv233_blend50 | require_drift_aligned_abs_ge_1bps | 2573 | 0.4489 | -3820.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap15_rv233_blend50 | require_drift_aligned_abs_ge_3bps | 2467 | 0.4532 | -4347.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap15_rv233_blend50 | require_late_le_300s | 793 | 0.1765 | 2828.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap15_rv233_blend50 | require_mid_181_600s | 1645 | 0.3690 | 3414.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap15_rv233_blend50 | require_near_strike_abs_le_10bps | 2092 | 0.5053 | 2702.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap15_rv233_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 1908 | 0.5288 | 1883.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap15_rv233_blend50 | require_market_current_consensus_alignment | 1039 | 0.2897 | -39007.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap15_rv233_blend50 | skip_against_market_current_consensus | 1246 | 0.3395 | -38089.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift21_cap20_rv377_blend50 | base | 3244 | 0.3628 | -9535.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift21_cap20_rv377_blend50 | require_drift_aligned | 2603 | 0.4360 | -8481.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift21_cap20_rv377_blend50 | skip_drift_against | 2677 | 0.4300 | -8363.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift21_cap20_rv377_blend50 | require_abs_drift_ge_1bps | 3134 | 0.3676 | -9520.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift21_cap20_rv377_blend50 | require_abs_drift_ge_3bps | 2913 | 0.3759 | -9485.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift21_cap20_rv377_blend50 | require_abs_drift_ge_6bps | 2574 | 0.3897 | -8536.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift21_cap20_rv377_blend50 | require_drift_aligned_abs_ge_1bps | 2581 | 0.4370 | -8365.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift21_cap20_rv377_blend50 | require_drift_aligned_abs_ge_3bps | 2431 | 0.4422 | -8566.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift21_cap20_rv377_blend50 | require_late_le_300s | 792 | 0.1654 | 1755.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift21_cap20_rv377_blend50 | require_mid_181_600s | 1650 | 0.3545 | 1089.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift21_cap20_rv377_blend50 | require_near_strike_abs_le_10bps | 2111 | 0.4927 | -1334.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift21_cap20_rv377_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 1955 | 0.5115 | -2385.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift21_cap20_rv377_blend50 | require_market_current_consensus_alignment | 1074 | 0.2756 | -41656.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift21_cap20_rv377_blend50 | skip_against_market_current_consensus | 1282 | 0.3362 | -39577.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift34_cap20_rv610_blend50 | base | 3247 | 0.3545 | -11807.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift34_cap20_rv610_blend50 | require_drift_aligned | 2593 | 0.4254 | -10955.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift34_cap20_rv610_blend50 | skip_drift_against | 2649 | 0.4202 | -11567.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift34_cap20_rv610_blend50 | require_abs_drift_ge_1bps | 3139 | 0.3606 | -10865.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift34_cap20_rv610_blend50 | require_abs_drift_ge_3bps | 2874 | 0.3709 | -11250.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift34_cap20_rv610_blend50 | require_abs_drift_ge_6bps | 2478 | 0.3862 | -10696.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift34_cap20_rv610_blend50 | require_drift_aligned_abs_ge_1bps | 2565 | 0.4269 | -10780.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift34_cap20_rv610_blend50 | require_drift_aligned_abs_ge_3bps | 2384 | 0.4333 | -11484.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift34_cap20_rv610_blend50 | require_late_le_300s | 800 | 0.1625 | 1451.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift34_cap20_rv610_blend50 | require_mid_181_600s | 1648 | 0.3847 | 7718.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift34_cap20_rv610_blend50 | require_near_strike_abs_le_10bps | 2109 | 0.4879 | -66.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift34_cap20_rv610_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 1957 | 0.5033 | -1483.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift34_cap20_rv610_blend50 | require_market_current_consensus_alignment | 1084 | 0.2565 | -43972.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift34_cap20_rv610_blend50 | skip_against_market_current_consensus | 1286 | 0.3328 | -39794.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap10_fixed65_blend25 | base | 3021 | 0.4098 | 28250.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap10_fixed65_blend25 | require_drift_aligned | 2068 | 0.4831 | 18499.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap10_fixed65_blend25 | skip_drift_against | 2175 | 0.4846 | 21140.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap10_fixed65_blend25 | require_abs_drift_ge_1bps | 2859 | 0.4089 | 25363.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap10_fixed65_blend25 | require_abs_drift_ge_3bps | 2694 | 0.4120 | 22778.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap10_fixed65_blend25 | require_abs_drift_ge_6bps | 2463 | 0.4206 | 19920.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap10_fixed65_blend25 | require_drift_aligned_abs_ge_1bps | 2042 | 0.4853 | 18367.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap10_fixed65_blend25 | require_drift_aligned_abs_ge_3bps | 1955 | 0.4895 | 16744.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap10_fixed65_blend25 | require_late_le_300s | 798 | 0.1541 | 3332.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap10_fixed65_blend25 | require_mid_181_600s | 1571 | 0.3775 | 16206.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap10_fixed65_blend25 | require_near_strike_abs_le_10bps | 1924 | 0.5748 | 28018.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap10_fixed65_blend25 | require_drift_aligned_near_strike_abs_le_10bps | 1540 | 0.5974 | 18919.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap10_fixed65_blend25 | require_market_current_consensus_alignment | 506 | 0.2964 | -15686.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap10_fixed65_blend25 | skip_against_market_current_consensus | 693 | 0.3709 | -14747.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift5_cap10_rv89_blend50 | base | 2322 | 0.4220 | 31371.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift5_cap10_rv89_blend50 | require_drift_aligned | 1358 | 0.5236 | 17594.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift5_cap10_rv89_blend50 | skip_drift_against | 1836 | 0.4668 | 22840.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift5_cap10_rv89_blend50 | require_abs_drift_ge_1bps | 1828 | 0.4557 | 26262.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift5_cap10_rv89_blend50 | require_abs_drift_ge_3bps | 1739 | 0.4652 | 25080.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift5_cap10_rv89_blend50 | require_abs_drift_ge_6bps | 1600 | 0.4750 | 23123.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift5_cap10_rv89_blend50 | require_drift_aligned_abs_ge_1bps | 1349 | 0.5271 | 17789.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift5_cap10_rv89_blend50 | require_drift_aligned_abs_ge_3bps | 1295 | 0.5344 | 16845.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift5_cap10_rv89_blend50 | require_late_le_300s | 597 | 0.2915 | 12701.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift5_cap10_rv89_blend50 | require_mid_181_600s | 1129 | 0.3286 | 18294.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift5_cap10_rv89_blend50 | require_near_strike_abs_le_10bps | 1468 | 0.5450 | 22625.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift5_cap10_rv89_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 1012 | 0.5820 | 11150.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift5_cap10_rv89_blend50 | require_market_current_consensus_alignment | 482 | 0.5207 | -6880.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift5_cap10_rv89_blend50 | skip_against_market_current_consensus | 558 | 0.5161 | -7279.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap15_rv233_blend50 | base | 2354 | 0.4274 | 27929.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap15_rv233_blend50 | require_drift_aligned | 1547 | 0.5204 | 16494.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap15_rv233_blend50 | skip_drift_against | 1753 | 0.4849 | 17169.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap15_rv233_blend50 | require_abs_drift_ge_1bps | 2100 | 0.4548 | 27047.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap15_rv233_blend50 | require_abs_drift_ge_3bps | 1915 | 0.4574 | 22777.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap15_rv233_blend50 | require_abs_drift_ge_6bps | 1701 | 0.4668 | 19986.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap15_rv233_blend50 | require_drift_aligned_abs_ge_1bps | 1518 | 0.5290 | 16585.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap15_rv233_blend50 | require_drift_aligned_abs_ge_3bps | 1414 | 0.5347 | 14478.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap15_rv233_blend50 | require_late_le_300s | 603 | 0.3002 | 13173.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap15_rv233_blend50 | require_mid_181_600s | 1095 | 0.3242 | 17284.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap15_rv233_blend50 | require_near_strike_abs_le_10bps | 1506 | 0.5538 | 21051.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap15_rv233_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 1188 | 0.5766 | 11880.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap15_rv233_blend50 | require_market_current_consensus_alignment | 588 | 0.5119 | -9430.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap15_rv233_blend50 | skip_against_market_current_consensus | 670 | 0.5134 | -9683.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift21_cap20_rv377_blend50 | base | 2382 | 0.4349 | 28503.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift21_cap20_rv377_blend50 | require_drift_aligned | 1612 | 0.5192 | 15997.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift21_cap20_rv377_blend50 | skip_drift_against | 1750 | 0.4937 | 16480.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift21_cap20_rv377_blend50 | require_abs_drift_ge_1bps | 2177 | 0.4552 | 27270.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift21_cap20_rv377_blend50 | require_abs_drift_ge_3bps | 1997 | 0.4572 | 22865.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift21_cap20_rv377_blend50 | require_abs_drift_ge_6bps | 1736 | 0.4574 | 18098.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift21_cap20_rv377_blend50 | require_drift_aligned_abs_ge_1bps | 1580 | 0.5259 | 15891.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift21_cap20_rv377_blend50 | require_drift_aligned_abs_ge_3bps | 1460 | 0.5315 | 13090.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift21_cap20_rv377_blend50 | require_late_le_300s | 597 | 0.3099 | 13680.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift21_cap20_rv377_blend50 | require_mid_181_600s | 1119 | 0.3414 | 18818.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift21_cap20_rv377_blend50 | require_near_strike_abs_le_10bps | 1519 | 0.5668 | 22676.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift21_cap20_rv377_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 1244 | 0.5820 | 13297.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift21_cap20_rv377_blend50 | require_market_current_consensus_alignment | 630 | 0.5222 | -9701.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift21_cap20_rv377_blend50 | skip_against_market_current_consensus | 709 | 0.5205 | -10097.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift34_cap20_rv610_blend50 | base | 2415 | 0.4410 | 29278.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift34_cap20_rv610_blend50 | require_drift_aligned | 1641 | 0.5210 | 14948.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift34_cap20_rv610_blend50 | skip_drift_against | 1761 | 0.5094 | 17283.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift34_cap20_rv610_blend50 | require_abs_drift_ge_1bps | 2252 | 0.4494 | 26316.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift34_cap20_rv610_blend50 | require_abs_drift_ge_3bps | 2050 | 0.4620 | 23609.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift34_cap20_rv610_blend50 | require_abs_drift_ge_6bps | 1834 | 0.4684 | 19731.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift34_cap20_rv610_blend50 | require_drift_aligned_abs_ge_1bps | 1610 | 0.5255 | 14416.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift34_cap20_rv610_blend50 | require_drift_aligned_abs_ge_3bps | 1474 | 0.5434 | 13094.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift34_cap20_rv610_blend50 | require_late_le_300s | 600 | 0.3083 | 13469.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift34_cap20_rv610_blend50 | require_mid_181_600s | 1148 | 0.3484 | 20001.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift34_cap20_rv610_blend50 | require_near_strike_abs_le_10bps | 1549 | 0.5759 | 24414.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift34_cap20_rv610_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 1296 | 0.5802 | 13861.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift34_cap20_rv610_blend50 | require_market_current_consensus_alignment | 676 | 0.5192 | -10514.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift34_cap20_rv610_blend50 | skip_against_market_current_consensus | 757 | 0.5231 | -10520.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap10_fixed65_blend25 | base | 2393 | 0.4572 | 53121.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap10_fixed65_blend25 | require_drift_aligned | 1141 | 0.5504 | 27654.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap10_fixed65_blend25 | skip_drift_against | 1363 | 0.5011 | 28819.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap10_fixed65_blend25 | require_abs_drift_ge_1bps | 2111 | 0.4879 | 51861.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap10_fixed65_blend25 | require_abs_drift_ge_3bps | 1918 | 0.4943 | 47061.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap10_fixed65_blend25 | require_abs_drift_ge_6bps | 1685 | 0.5068 | 42336.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap10_fixed65_blend25 | require_drift_aligned_abs_ge_1bps | 1110 | 0.5622 | 27618.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap10_fixed65_blend25 | require_drift_aligned_abs_ge_3bps | 1023 | 0.5748 | 25617.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap10_fixed65_blend25 | require_late_le_300s | 599 | 0.3005 | 13314.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap10_fixed65_blend25 | require_mid_181_600s | 1204 | 0.3405 | 23663.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap10_fixed65_blend25 | require_near_strike_abs_le_10bps | 1503 | 0.5742 | 38546.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap10_fixed65_blend25 | require_drift_aligned_near_strike_abs_le_10bps | 832 | 0.6202 | 19931.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap10_fixed65_blend25 | require_market_current_consensus_alignment | 199 | 0.6633 | 1459.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap10_fixed65_blend25 | skip_against_market_current_consensus | 271 | 0.6236 | 1396.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift5_cap10_rv89_blend50 | base | 4483 | 0.4406 | 42284.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift5_cap10_rv89_blend50 | require_drift_aligned | 3084 | 0.4711 | 15524.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift5_cap10_rv89_blend50 | skip_drift_against | 3742 | 0.4463 | 20037.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift5_cap10_rv89_blend50 | require_abs_drift_ge_1bps | 3740 | 0.4626 | 36542.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift5_cap10_rv89_blend50 | require_abs_drift_ge_3bps | 3512 | 0.4715 | 33317.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift5_cap10_rv89_blend50 | require_abs_drift_ge_6bps | 3163 | 0.4875 | 28835.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift5_cap10_rv89_blend50 | require_drift_aligned_abs_ge_1bps | 3040 | 0.4734 | 15051.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift5_cap10_rv89_blend50 | require_drift_aligned_abs_ge_3bps | 2890 | 0.4803 | 13256.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift5_cap10_rv89_blend50 | require_late_le_300s | 1443 | 0.2661 | 13917.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift5_cap10_rv89_blend50 | require_mid_181_600s | 2282 | 0.5158 | 44382.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift5_cap10_rv89_blend50 | require_near_strike_abs_le_10bps | 3515 | 0.3940 | -472.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift5_cap10_rv89_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 2591 | 0.4581 | -174.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift5_cap10_rv89_blend50 | require_market_current_consensus_alignment | 1046 | 0.6530 | -1683.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift5_cap10_rv89_blend50 | skip_against_market_current_consensus | 1318 | 0.6419 | 250.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap15_rv233_blend50 | base | 4597 | 0.4564 | 41368.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap15_rv233_blend50 | require_drift_aligned | 3531 | 0.4815 | 14851.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap15_rv233_blend50 | skip_drift_against | 3767 | 0.4762 | 19288.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap15_rv233_blend50 | require_abs_drift_ge_1bps | 4253 | 0.4632 | 35068.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap15_rv233_blend50 | require_abs_drift_ge_3bps | 3880 | 0.4771 | 29373.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap15_rv233_blend50 | require_abs_drift_ge_6bps | 3341 | 0.4876 | 21392.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap15_rv233_blend50 | require_drift_aligned_abs_ge_1bps | 3480 | 0.4828 | 13772.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap15_rv233_blend50 | require_drift_aligned_abs_ge_3bps | 3264 | 0.4936 | 11596.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap15_rv233_blend50 | require_late_le_300s | 1434 | 0.2685 | 13992.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap15_rv233_blend50 | require_mid_181_600s | 2288 | 0.5642 | 53067.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap15_rv233_blend50 | require_near_strike_abs_le_10bps | 3640 | 0.4140 | -446.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap15_rv233_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 2991 | 0.4674 | -2135.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap15_rv233_blend50 | require_market_current_consensus_alignment | 1249 | 0.6501 | -3064.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap15_rv233_blend50 | skip_against_market_current_consensus | 1527 | 0.6477 | -371.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift21_cap20_rv377_blend50 | base | 4579 | 0.4608 | 41161.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift21_cap20_rv377_blend50 | require_drift_aligned | 3560 | 0.4980 | 19124.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift21_cap20_rv377_blend50 | skip_drift_against | 3734 | 0.4893 | 21934.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift21_cap20_rv377_blend50 | require_abs_drift_ge_1bps | 4280 | 0.4736 | 37439.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift21_cap20_rv377_blend50 | require_abs_drift_ge_3bps | 3786 | 0.4937 | 31654.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift21_cap20_rv377_blend50 | require_abs_drift_ge_6bps | 3225 | 0.5085 | 24687.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift21_cap20_rv377_blend50 | require_drift_aligned_abs_ge_1bps | 3490 | 0.5037 | 18818.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift21_cap20_rv377_blend50 | require_drift_aligned_abs_ge_3bps | 3186 | 0.5204 | 16857.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift21_cap20_rv377_blend50 | require_late_le_300s | 1440 | 0.2743 | 14182.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift21_cap20_rv377_blend50 | require_mid_181_600s | 2282 | 0.5675 | 52655.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift21_cap20_rv377_blend50 | require_near_strike_abs_le_10bps | 3624 | 0.4183 | -48.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift21_cap20_rv377_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 3000 | 0.4787 | -227.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift21_cap20_rv377_blend50 | require_market_current_consensus_alignment | 1316 | 0.6535 | -2980.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift21_cap20_rv377_blend50 | skip_against_market_current_consensus | 1589 | 0.6476 | -859.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift34_cap20_rv610_blend50 | base | 4556 | 0.4583 | 37276.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift34_cap20_rv610_blend50 | require_drift_aligned | 3525 | 0.5092 | 20439.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift34_cap20_rv610_blend50 | skip_drift_against | 3723 | 0.4942 | 21853.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift34_cap20_rv610_blend50 | require_abs_drift_ge_1bps | 4201 | 0.4780 | 34382.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift34_cap20_rv610_blend50 | require_abs_drift_ge_3bps | 3646 | 0.5030 | 27384.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift34_cap20_rv610_blend50 | require_abs_drift_ge_6bps | 3051 | 0.5123 | 18017.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift34_cap20_rv610_blend50 | require_drift_aligned_abs_ge_1bps | 3425 | 0.5168 | 19163.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift34_cap20_rv610_blend50 | require_drift_aligned_abs_ge_3bps | 3062 | 0.5369 | 14497.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift34_cap20_rv610_blend50 | require_late_le_300s | 1435 | 0.2746 | 14438.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift34_cap20_rv610_blend50 | require_mid_181_600s | 2274 | 0.5712 | 53864.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift34_cap20_rv610_blend50 | require_near_strike_abs_le_10bps | 3598 | 0.4152 | -2548.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift34_cap20_rv610_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 2937 | 0.4821 | -1427.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift34_cap20_rv610_blend50 | require_market_current_consensus_alignment | 1404 | 0.6396 | -5204.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift34_cap20_rv610_blend50 | skip_against_market_current_consensus | 1654 | 0.6372 | -3085.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap10_fixed65_blend25 | base | 4422 | 0.3985 | 48504.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap10_fixed65_blend25 | require_drift_aligned | 2695 | 0.4360 | 21719.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap10_fixed65_blend25 | skip_drift_against | 2948 | 0.4301 | 25476.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap10_fixed65_blend25 | require_abs_drift_ge_1bps | 4048 | 0.4034 | 43083.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap10_fixed65_blend25 | require_abs_drift_ge_3bps | 3643 | 0.4167 | 38246.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap10_fixed65_blend25 | require_abs_drift_ge_6bps | 3098 | 0.4283 | 30138.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap10_fixed65_blend25 | require_drift_aligned_abs_ge_1bps | 2640 | 0.4375 | 20717.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap10_fixed65_blend25 | require_drift_aligned_abs_ge_3bps | 2438 | 0.4516 | 19031.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap10_fixed65_blend25 | require_late_le_300s | 1478 | 0.2436 | 12490.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap10_fixed65_blend25 | require_mid_181_600s | 2298 | 0.4504 | 45051.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap10_fixed65_blend25 | require_near_strike_abs_le_10bps | 3466 | 0.3304 | -425.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap10_fixed65_blend25 | require_drift_aligned_near_strike_abs_le_10bps | 2235 | 0.3978 | 60.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap10_fixed65_blend25 | require_market_current_consensus_alignment | 450 | 0.6844 | 3506.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap10_fixed65_blend25 | skip_against_market_current_consensus | 686 | 0.6720 | 6448.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift5_cap10_rv89_blend50 | base | 4078 | 0.2234 | -24211.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift5_cap10_rv89_blend50 | require_drift_aligned | 1375 | 0.3549 | -7038.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift5_cap10_rv89_blend50 | skip_drift_against | 3581 | 0.2469 | -21409.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift5_cap10_rv89_blend50 | require_abs_drift_ge_1bps | 1837 | 0.2749 | -10185.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift5_cap10_rv89_blend50 | require_abs_drift_ge_3bps | 1750 | 0.2771 | -10578.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift5_cap10_rv89_blend50 | require_abs_drift_ge_6bps | 1607 | 0.2900 | -9535.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift5_cap10_rv89_blend50 | require_drift_aligned_abs_ge_1bps | 1360 | 0.3551 | -7289.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift5_cap10_rv89_blend50 | require_drift_aligned_abs_ge_3bps | 1323 | 0.3590 | -7248.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift5_cap10_rv89_blend50 | require_late_le_300s | 1329 | 0.0406 | -11760.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift5_cap10_rv89_blend50 | require_mid_181_600s | 2324 | 0.1975 | -14916.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift5_cap10_rv89_blend50 | require_near_strike_abs_le_10bps | 3224 | 0.2705 | -19367.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift5_cap10_rv89_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 1075 | 0.4177 | -5419.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift5_cap10_rv89_blend50 | require_market_current_consensus_alignment | 522 | 0.5862 | -3095.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift5_cap10_rv89_blend50 | skip_against_market_current_consensus | 847 | 0.5348 | -3825.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap15_rv233_blend50 | base | 4162 | 0.2203 | -33550.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap15_rv233_blend50 | require_drift_aligned | 2042 | 0.3389 | -14418.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap15_rv233_blend50 | skip_drift_against | 3410 | 0.2563 | -29703.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap15_rv233_blend50 | require_abs_drift_ge_1bps | 2742 | 0.2644 | -18493.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap15_rv233_blend50 | require_abs_drift_ge_3bps | 2435 | 0.2838 | -16292.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap15_rv233_blend50 | require_abs_drift_ge_6bps | 2136 | 0.2884 | -16466.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap15_rv233_blend50 | require_drift_aligned_abs_ge_1bps | 2016 | 0.3428 | -14027.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap15_rv233_blend50 | require_drift_aligned_abs_ge_3bps | 1860 | 0.3624 | -12121.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap15_rv233_blend50 | require_late_le_300s | 1323 | 0.0385 | -11836.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap15_rv233_blend50 | require_mid_181_600s | 2353 | 0.2010 | -17428.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap15_rv233_blend50 | require_near_strike_abs_le_10bps | 3303 | 0.2634 | -28882.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap15_rv233_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 1631 | 0.3955 | -12118.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap15_rv233_blend50 | require_market_current_consensus_alignment | 671 | 0.5544 | -7289.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap15_rv233_blend50 | skip_against_market_current_consensus | 994 | 0.5080 | -9679.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift21_cap20_rv377_blend50 | base | 4178 | 0.2255 | -34242.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift21_cap20_rv377_blend50 | require_drift_aligned | 2219 | 0.3538 | -13487.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift21_cap20_rv377_blend50 | skip_drift_against | 3336 | 0.2698 | -29258.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift21_cap20_rv377_blend50 | require_abs_drift_ge_1bps | 2978 | 0.2720 | -18362.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift21_cap20_rv377_blend50 | require_abs_drift_ge_3bps | 2581 | 0.2945 | -15470.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift21_cap20_rv377_blend50 | require_abs_drift_ge_6bps | 2165 | 0.3035 | -14838.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift21_cap20_rv377_blend50 | require_drift_aligned_abs_ge_1bps | 2182 | 0.3566 | -13231.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift21_cap20_rv377_blend50 | require_drift_aligned_abs_ge_3bps | 1948 | 0.3804 | -11149.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift21_cap20_rv377_blend50 | require_late_le_300s | 1324 | 0.0363 | -12048.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift21_cap20_rv377_blend50 | require_mid_181_600s | 2351 | 0.2050 | -17534.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift21_cap20_rv377_blend50 | require_near_strike_abs_le_10bps | 3318 | 0.2676 | -29893.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift21_cap20_rv377_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 1775 | 0.4124 | -11319.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift21_cap20_rv377_blend50 | require_market_current_consensus_alignment | 751 | 0.5712 | -6876.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift21_cap20_rv377_blend50 | skip_against_market_current_consensus | 1078 | 0.5065 | -10910.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift34_cap20_rv610_blend50 | base | 4206 | 0.2254 | -37562.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift34_cap20_rv610_blend50 | require_drift_aligned | 2367 | 0.3595 | -14849.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift34_cap20_rv610_blend50 | skip_drift_against | 3322 | 0.2718 | -33090.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift34_cap20_rv610_blend50 | require_abs_drift_ge_1bps | 3115 | 0.2803 | -19318.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift34_cap20_rv610_blend50 | require_abs_drift_ge_3bps | 2684 | 0.3074 | -16960.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift34_cap20_rv610_blend50 | require_abs_drift_ge_6bps | 2104 | 0.3327 | -13612.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift34_cap20_rv610_blend50 | require_drift_aligned_abs_ge_1bps | 2295 | 0.3673 | -14288.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift34_cap20_rv610_blend50 | require_drift_aligned_abs_ge_3bps | 2033 | 0.3955 | -12768.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift34_cap20_rv610_blend50 | require_late_le_300s | 1336 | 0.0329 | -12745.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift34_cap20_rv610_blend50 | require_mid_181_600s | 2353 | 0.2048 | -18413.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift34_cap20_rv610_blend50 | require_near_strike_abs_le_10bps | 3347 | 0.2671 | -33264.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift34_cap20_rv610_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 1933 | 0.4128 | -12661.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift34_cap20_rv610_blend50 | require_market_current_consensus_alignment | 864 | 0.5417 | -10061.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift34_cap20_rv610_blend50 | skip_against_market_current_consensus | 1193 | 0.4937 | -13854.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap10_fixed65_blend25 | base | 4162 | 0.2184 | -14898.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap10_fixed65_blend25 | require_drift_aligned | 1550 | 0.2826 | -5614.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap10_fixed65_blend25 | skip_drift_against | 3009 | 0.2293 | -17340.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap10_fixed65_blend25 | require_abs_drift_ge_1bps | 2651 | 0.2441 | -3400.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap10_fixed65_blend25 | require_abs_drift_ge_3bps | 2348 | 0.2619 | -1477.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap10_fixed65_blend25 | require_abs_drift_ge_6bps | 2054 | 0.2717 | -895.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap10_fixed65_blend25 | require_drift_aligned_abs_ge_1bps | 1524 | 0.2867 | -5223.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap10_fixed65_blend25 | require_drift_aligned_abs_ge_3bps | 1383 | 0.3066 | -3800.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap10_fixed65_blend25 | require_late_le_300s | 1333 | 0.0218 | -13516.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap10_fixed65_blend25 | require_mid_181_600s | 2328 | 0.1512 | -20665.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap10_fixed65_blend25 | require_near_strike_abs_le_10bps | 3277 | 0.2774 | -7782.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap10_fixed65_blend25 | require_drift_aligned_near_strike_abs_le_10bps | 1186 | 0.3693 | -2395.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap10_fixed65_blend25 | require_market_current_consensus_alignment | 204 | 0.6324 | 984.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap10_fixed65_blend25 | skip_against_market_current_consensus | 493 | 0.4625 | -2263.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift5_cap10_rv89_blend50 | base | 4257 | 0.2765 | 7813.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift5_cap10_rv89_blend50 | require_drift_aligned | 1974 | 0.4245 | 8039.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift5_cap10_rv89_blend50 | skip_drift_against | 3487 | 0.3232 | 10273.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift5_cap10_rv89_blend50 | require_abs_drift_ge_1bps | 2720 | 0.3254 | 5727.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift5_cap10_rv89_blend50 | require_abs_drift_ge_3bps | 2554 | 0.3301 | 4633.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift5_cap10_rv89_blend50 | require_abs_drift_ge_6bps | 2360 | 0.3436 | 4498.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift5_cap10_rv89_blend50 | require_drift_aligned_abs_ge_1bps | 1960 | 0.4265 | 8139.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift5_cap10_rv89_blend50 | require_drift_aligned_abs_ge_3bps | 1856 | 0.4332 | 7434.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift5_cap10_rv89_blend50 | require_late_le_300s | 1213 | 0.0569 | -3870.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift5_cap10_rv89_blend50 | require_mid_181_600s | 2311 | 0.1817 | -8586.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift5_cap10_rv89_blend50 | require_near_strike_abs_le_10bps | 3290 | 0.3492 | 12390.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift5_cap10_rv89_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 1638 | 0.5061 | 10264.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift5_cap10_rv89_blend50 | require_market_current_consensus_alignment | 608 | 0.7451 | 5075.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift5_cap10_rv89_blend50 | skip_against_market_current_consensus | 782 | 0.7340 | 7899.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap15_rv233_blend50 | base | 4272 | 0.2701 | -3041.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap15_rv233_blend50 | require_drift_aligned | 2637 | 0.3830 | 1711.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap15_rv233_blend50 | skip_drift_against | 3200 | 0.3412 | 944.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap15_rv233_blend50 | require_abs_drift_ge_1bps | 3611 | 0.2938 | -1867.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap15_rv233_blend50 | require_abs_drift_ge_3bps | 3257 | 0.3083 | -1574.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap15_rv233_blend50 | require_abs_drift_ge_6bps | 2750 | 0.3302 | -1660.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap15_rv233_blend50 | require_drift_aligned_abs_ge_1bps | 2578 | 0.3910 | 2422.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap15_rv233_blend50 | require_drift_aligned_abs_ge_3bps | 2368 | 0.4029 | 1536.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap15_rv233_blend50 | require_late_le_300s | 1217 | 0.0575 | -4369.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap15_rv233_blend50 | require_mid_181_600s | 2326 | 0.1849 | -10851.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap15_rv233_blend50 | require_near_strike_abs_le_10bps | 3323 | 0.3385 | 1248.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap15_rv233_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 2209 | 0.4509 | 4086.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap15_rv233_blend50 | require_market_current_consensus_alignment | 794 | 0.6902 | 1733.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap15_rv233_blend50 | skip_against_market_current_consensus | 967 | 0.6763 | 2801.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift21_cap20_rv377_blend50 | base | 4235 | 0.2621 | -7218.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift21_cap20_rv377_blend50 | require_drift_aligned | 2723 | 0.3680 | -1612.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift21_cap20_rv377_blend50 | skip_drift_against | 3051 | 0.3415 | -2966.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift21_cap20_rv377_blend50 | require_abs_drift_ge_1bps | 3739 | 0.2806 | -5960.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift21_cap20_rv377_blend50 | require_abs_drift_ge_3bps | 3247 | 0.2972 | -5752.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift21_cap20_rv377_blend50 | require_abs_drift_ge_6bps | 2671 | 0.3194 | -6220.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift21_cap20_rv377_blend50 | require_drift_aligned_abs_ge_1bps | 2617 | 0.3779 | -1504.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift21_cap20_rv377_blend50 | require_drift_aligned_abs_ge_3bps | 2323 | 0.3913 | -3123.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift21_cap20_rv377_blend50 | require_late_le_300s | 1208 | 0.0522 | -4585.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift21_cap20_rv377_blend50 | require_mid_181_600s | 2302 | 0.1833 | -10700.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift21_cap20_rv377_blend50 | require_near_strike_abs_le_10bps | 3289 | 0.3259 | -3391.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift21_cap20_rv377_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 2328 | 0.4205 | 167.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift21_cap20_rv377_blend50 | require_market_current_consensus_alignment | 823 | 0.6719 | 203.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift21_cap20_rv377_blend50 | skip_against_market_current_consensus | 999 | 0.6466 | -97.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift34_cap20_rv610_blend50 | base | 4241 | 0.2596 | -10994.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift34_cap20_rv610_blend50 | require_drift_aligned | 2679 | 0.3725 | -4496.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift34_cap20_rv610_blend50 | skip_drift_against | 2910 | 0.3570 | -4567.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift34_cap20_rv610_blend50 | require_abs_drift_ge_1bps | 3840 | 0.2719 | -10511.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift34_cap20_rv610_blend50 | require_abs_drift_ge_3bps | 3135 | 0.3085 | -8520.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift34_cap20_rv610_blend50 | require_abs_drift_ge_6bps | 2488 | 0.3465 | -7207.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift34_cap20_rv610_blend50 | require_drift_aligned_abs_ge_1bps | 2577 | 0.3826 | -4493.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift34_cap20_rv610_blend50 | require_drift_aligned_abs_ge_3bps | 2208 | 0.4144 | -5037.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift34_cap20_rv610_blend50 | require_late_le_300s | 1218 | 0.0542 | -4696.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift34_cap20_rv610_blend50 | require_mid_181_600s | 2313 | 0.1859 | -11516.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift34_cap20_rv610_blend50 | require_near_strike_abs_le_10bps | 3300 | 0.3194 | -7416.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift34_cap20_rv610_blend50 | require_drift_aligned_near_strike_abs_le_10bps | 2345 | 0.4124 | -3482.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift34_cap20_rv610_blend50 | require_market_current_consensus_alignment | 894 | 0.6544 | -1418.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift34_cap20_rv610_blend50 | skip_against_market_current_consensus | 1070 | 0.6383 | -1473.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap10_fixed65_blend25 | base | 4298 | 0.2278 | 2547.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap10_fixed65_blend25 | require_drift_aligned | 2059 | 0.3128 | 5356.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap10_fixed65_blend25 | skip_drift_against | 2629 | 0.2640 | 1635.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap10_fixed65_blend25 | require_abs_drift_ge_1bps | 3627 | 0.2534 | 6787.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap10_fixed65_blend25 | require_abs_drift_ge_3bps | 3271 | 0.2696 | 8382.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap10_fixed65_blend25 | require_abs_drift_ge_6bps | 2769 | 0.2947 | 9920.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap10_fixed65_blend25 | require_drift_aligned_abs_ge_1bps | 2001 | 0.3218 | 6160.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap10_fixed65_blend25 | require_drift_aligned_abs_ge_3bps | 1828 | 0.3397 | 6101.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap10_fixed65_blend25 | require_late_le_300s | 1200 | 0.0175 | -6883.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap10_fixed65_blend25 | require_mid_181_600s | 2313 | 0.1003 | -19995.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap10_fixed65_blend25 | require_near_strike_abs_le_10bps | 3319 | 0.2886 | 7706.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap10_fixed65_blend25 | require_drift_aligned_near_strike_abs_le_10bps | 1639 | 0.3893 | 7881.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap10_fixed65_blend25 | require_market_current_consensus_alignment | 215 | 0.7721 | 3666.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap10_fixed65_blend25 | skip_against_market_current_consensus | 367 | 0.7275 | 5821.0000 |

## Run Inputs

| run | rows | markets | spot_ticks |
|---|---:|---:|---:|
| particle_side_consensus_oos_CONSENSUSLOCK001 | 3260 | 6 | 37344 |
| particle_residual_blend_oos_RESIDLOCK001 | 3358 | 5 | 44784 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | 2514 | 4 | 48313 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | 4843 | 7 | 37126 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | 4405 | 6 | 35848 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | 4512 | 7 | 33754 |

## Skipped Runs

- `logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED`
- `logs\particle_research\real_shadow\particle_dynamic_oos_20260511TLOCKEDNEXT`
- `logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2`
