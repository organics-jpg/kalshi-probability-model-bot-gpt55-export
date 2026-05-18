# Spot Drift Regime Diagnostic

- eligible_run_count: 6
- skipped_run_count: 3
- spec_count: 1
- feature_count: 22892
- selected_count: 21197
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
| drift13_cap10_fixed65_blend25 | require_mid_181_600s | 3/6 | 6/6 | 11122 | 30905.0000 | -20665.0000 | False |
| drift13_cap10_fixed65_blend25 | require_late_le_300s | 3/6 | 6/6 | 6253 | 6131.0000 | -13516.0000 | False |

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

## Rule By Run

| run | spec | rule | selected | win_rate | pnl_cents |
|---|---|---|---:|---:|---:|
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
