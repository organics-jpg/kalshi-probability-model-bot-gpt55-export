# Anchor Regime Profile

- run_count: 7
- metric_row_count: 248
- winner_row_count: 62
- promotion_safe: False
- conclusion: No single timestamp-available anchor dominates all locked runs by Brier; anchor switching needs a stronger state signal before it is promotable.
- run_best_counts_by_brier: `{"brownian": 2, "current_calibrated": 4, "market": 0, "particle": 1}`
- market_best_counts_by_brier: `{"brownian": 7, "current_calibrated": 11, "market": 14, "particle": 6}`
- state_bucket_best_counts_by_brier: `{"brownian": 6, "current_calibrated": 5, "market": 4, "particle": 1}`

## Winner Rows

| scope | bucket | markets | candidates | best_brier | best_log_loss | best_pnl | brier_gap | best_brier_value | best_pnl_cents |
|---|---|---:|---:|---|---|---|---:|---:|---:|
| all | all_locked_rows | 38 | 24288 | current_calibrated | market | brownian | 0.000428 | 0.197031 | 173233.0000 |
| market | particle_dynamic600_oos_20260511TLOCKEDNEXT2:KXBTC15M-26MAY110530-30 | 1 | 6 | market | market | market | 0.030933 | 0.000313 | 0.0000 |
| market | particle_dynamic600_oos_20260511TLOCKEDNEXT2:KXBTC15M-26MAY110545-45 | 1 | 848 | brownian | brownian | particle | 0.000187 | 0.310914 | 49965.0000 |
| market | particle_dynamic600_oos_20260511TLOCKEDNEXT2:KXBTC15M-26MAY110600-00 | 1 | 816 | market | market | market | 0.016482 | 0.115677 | 0.0000 |
| market | particle_dynamic600_oos_20260511TLOCKEDNEXT2:KXBTC15M-26MAY110615-15 | 1 | 783 | market | market | market | 0.011800 | 0.107668 | 0.0000 |
| market | particle_dynamic600_oos_20260511TLOCKEDNEXT2:KXBTC15M-26MAY110630-30 | 1 | 712 | market | market | market | 0.008561 | 0.038288 | 0.0000 |
| market | particle_dynamic600_oos_20260511TLOCKEDNEXT2:KXBTC15M-26MAY110645-45 | 1 | 249 | current_calibrated | current_calibrated | current_calibrated | 0.030703 | 0.164704 | 5443.0000 |
| market | particle_dynamic_oos_20260511TLOCKEDNEXT:KXBTC15M-26MAY110415-15 | 1 | 534 | current_calibrated | current_calibrated | current_calibrated | 0.023154 | 0.114398 | 5754.0000 |
| market | particle_dynamic_oos_20260511TLOCKEDNEXT:KXBTC15M-26MAY110430-30 | 1 | 782 | particle | particle | brownian | 0.000016 | 0.260396 | 32375.0000 |
| market | particle_dynamic_oos_20260511TLOCKEDNEXT:KXBTC15M-26MAY110445-45 | 1 | 781 | market | market | market | 0.002799 | 0.044461 | 0.0000 |
| market | particle_dynamic_oos_20260511TLOCKEDNEXT:KXBTC15M-26MAY110500-00 | 1 | 791 | current_calibrated | current_calibrated | current_calibrated | 0.008614 | 0.163419 | 13365.0000 |
| market | particle_dynamic_oos_20260511TLOCKEDNEXT:KXBTC15M-26MAY110515-15 | 1 | 613 | market | market | market | 0.005454 | 0.075835 | 0.0000 |
| market | particle_fixed_terminal_oos_GAUSS45LOCK001:KXBTC15M-26MAY111345-45 | 1 | 650 | market | market | market | 0.009748 | 0.102196 | 0.0000 |
| market | particle_fixed_terminal_oos_GAUSS45LOCK001:KXBTC15M-26MAY111415-15 | 1 | 747 | market | market | market | 0.006107 | 0.064098 | 0.0000 |
| market | particle_fixed_terminal_oos_GAUSS45LOCK001:KXBTC15M-26MAY111430-30 | 1 | 825 | particle | particle | brownian | 0.000348 | 0.357286 | 51107.0000 |
| market | particle_fixed_terminal_oos_GAUSS45LOCK001:KXBTC15M-26MAY111445-45 | 1 | 292 | brownian | brownian | brownian | 0.001466 | 0.335949 | 13814.0000 |
| market | particle_fixed_terminal_oos_GAUSS45LOCK002:KXBTC15M-26MAY111500-00 | 1 | 446 | brownian | brownian | current_calibrated | 0.000028 | 0.222367 | 15183.0000 |
| market | particle_fixed_terminal_oos_GAUSS45LOCK002:KXBTC15M-26MAY111515-15 | 1 | 837 | market | market | particle | 0.012702 | 0.211146 | 4623.0000 |
| market | particle_fixed_terminal_oos_GAUSS45LOCK002:KXBTC15M-26MAY111530-30 | 1 | 815 | particle | particle | particle | 0.000083 | 0.280620 | 6344.0000 |
| market | particle_fixed_terminal_oos_GAUSS45LOCK002:KXBTC15M-26MAY111545-45 | 1 | 769 | market | market | market | 0.016072 | 0.134809 | 0.0000 |
| market | particle_fixed_terminal_oos_GAUSS45LOCK002:KXBTC15M-26MAY111600-00 | 1 | 805 | current_calibrated | current_calibrated | current_calibrated | 0.004350 | 0.076055 | 5990.0000 |
| market | particle_fixed_terminal_oos_GAUSS45LOCK002:KXBTC15M-26MAY111615-15 | 1 | 824 | brownian | brownian | particle | 0.000605 | 0.357761 | 44015.0000 |
| market | particle_fixed_terminal_oos_GAUSS45LOCK002:KXBTC15M-26MAY111630-30 | 1 | 347 | particle | particle | brownian | 0.000414 | 0.260269 | 12109.0000 |
| market | particle_residual_blend_oos_RESIDLOCK001:KXBTC15M-26MAY111115-15 | 1 | 720 | brownian | brownian | brownian | 0.000136 | 0.314332 | 35057.0000 |
| market | particle_residual_blend_oos_RESIDLOCK001:KXBTC15M-26MAY111130-30 | 1 | 721 | brownian | brownian | particle | 0.000681 | 0.244540 | 14171.0000 |
| market | particle_residual_blend_oos_RESIDLOCK001:KXBTC15M-26MAY111145-45 | 1 | 807 | current_calibrated | current_calibrated | current_calibrated | 0.007848 | 0.061089 | 5269.0000 |
| market | particle_residual_blend_oos_RESIDLOCK001:KXBTC15M-26MAY111200-00 | 1 | 763 | market | market | brownian | 0.003161 | 0.135236 | 1107.0000 |
| market | particle_residual_blend_oos_RESIDLOCK001:KXBTC15M-26MAY111215-15 | 1 | 347 | particle | particle | brownian | 0.000156 | 0.330081 | 20491.0000 |
| market | particle_side_consensus_oos_CONSENSUSLOCK001:KXBTC15M-26MAY110900-00 | 1 | 2 | market | market | particle | 0.000001 | 0.000000 | 0.0000 |
| market | particle_side_consensus_oos_CONSENSUSLOCK001:KXBTC15M-26MAY110915-15 | 1 | 653 | current_calibrated | current_calibrated | current_calibrated | 0.006104 | 0.009268 | 3183.0000 |
| market | particle_side_consensus_oos_CONSENSUSLOCK001:KXBTC15M-26MAY110930-30 | 1 | 765 | current_calibrated | current_calibrated | current_calibrated | 0.003031 | 0.168794 | 7318.0000 |
| market | particle_side_consensus_oos_CONSENSUSLOCK001:KXBTC15M-26MAY110945-45 | 1 | 837 | current_calibrated | current_calibrated | current_calibrated | 0.017969 | 0.041404 | 6751.0000 |
| market | particle_side_consensus_oos_CONSENSUSLOCK001:KXBTC15M-26MAY111000-00 | 1 | 822 | current_calibrated | current_calibrated | current_calibrated | 0.031754 | 0.038142 | 14210.0000 |
| market | particle_side_consensus_oos_CONSENSUSLOCK001:KXBTC15M-26MAY111015-15 | 1 | 181 | current_calibrated | current_calibrated | current_calibrated | 0.039424 | 0.043216 | 4561.0000 |
| market | particle_side_safety_oos_20260511TLOCKED:KXBTC15M-26MAY110245-45 | 1 | 659 | market | market | market | 0.012315 | 0.085872 | 0.0000 |
| market | particle_side_safety_oos_20260511TLOCKED:KXBTC15M-26MAY110300-00 | 1 | 814 | market | market | brownian | 0.015943 | 0.221092 | 7265.0000 |
| market | particle_side_safety_oos_20260511TLOCKED:KXBTC15M-26MAY110315-15 | 1 | 756 | current_calibrated | current_calibrated | current_calibrated | 0.005182 | 0.016310 | 4772.0000 |
| market | particle_side_safety_oos_20260511TLOCKED:KXBTC15M-26MAY110330-30 | 1 | 803 | particle | particle | current_calibrated | 0.000386 | 0.233884 | 26653.0000 |
| market | particle_side_safety_oos_20260511TLOCKED:KXBTC15M-26MAY110345-45 | 1 | 366 | brownian | brownian | brownian | 0.000529 | 0.240370 | 5979.0000 |
| run | particle_dynamic600_oos_20260511TLOCKEDNEXT2 | 6 | 3414 | current_calibrated | current_calibrated | particle | 0.000837 | 0.199484 | 15777.0000 |
| run | particle_dynamic_oos_20260511TLOCKEDNEXT | 5 | 3501 | current_calibrated | current_calibrated | current_calibrated | 0.007291 | 0.153673 | 32996.0000 |
| run | particle_fixed_terminal_oos_GAUSS45LOCK001 | 4 | 2514 | particle | particle | particle | 0.000149 | 0.226789 | 50400.0000 |
| run | particle_fixed_terminal_oos_GAUSS45LOCK002 | 7 | 4843 | brownian | brownian | brownian | 0.000293 | 0.240082 | 48412.0000 |
| run | particle_residual_blend_oos_RESIDLOCK001 | 5 | 3358 | brownian | brownian | brownian | 0.000204 | 0.216843 | 60889.0000 |
| run | particle_side_consensus_oos_CONSENSUSLOCK001 | 6 | 3260 | current_calibrated | current_calibrated | current_calibrated | 0.016743 | 0.064114 | 36023.0000 |
| run | particle_side_safety_oos_20260511TLOCKED | 5 | 3398 | current_calibrated | current_calibrated | current_calibrated | 0.008306 | 0.163866 | 25198.0000 |
| state_bucket | abs_mny_000_010bps | 37 | 17883 | current_calibrated | current_calibrated | brownian | 0.002358 | 0.219843 | 132697.0000 |
| state_bucket | abs_mny_011_025bps | 27 | 5763 | brownian | market | particle | 0.000007 | 0.141436 | 42244.0000 |
| state_bucket | abs_mny_026_050bps | 4 | 632 | current_calibrated | current_calibrated | current_calibrated | 0.001187 | 0.000012 | 773.0000 |
| state_bucket | abs_mny_051_100bps | 1 | 10 | current_calibrated | current_calibrated | current_calibrated | 0.000272 | 0.000000 | 10.0000 |
| state_bucket | market_minus_brownian_ge10pp | 30 | 7778 | market | market | particle | 0.004661 | 0.159284 | 47839.0000 |
| state_bucket | market_minus_brownian_le_neg10pp | 27 | 5654 | particle | particle | particle | 0.000029 | 0.189153 | 66277.0000 |
| state_bucket | market_minus_brownian_mid | 37 | 10856 | brownian | brownian | brownian | 0.000121 | 0.215827 | 59117.0000 |
| state_bucket | spread_000_001c | 38 | 20945 | current_calibrated | market | brownian | 0.000241 | 0.190644 | 149647.0000 |
| state_bucket | spread_002_003c | 36 | 3303 | brownian | brownian | brownian | 0.000341 | 0.231861 | 23387.0000 |
| state_bucket | spread_004_006c | 16 | 33 | brownian | brownian | brownian | 0.001604 | 0.205440 | 269.0000 |
| state_bucket | spread_gt006c | 4 | 7 | market | market | market | 0.053660 | 0.150911 | 0.0000 |
| state_bucket | ttc_000_060s | 22 | 572 | market | market | current_calibrated | 0.004035 | 0.017838 | 1090.0000 |
| state_bucket | ttc_061_180s | 30 | 2813 | market | market | current_calibrated | 0.002751 | 0.072694 | 7157.0000 |
| state_bucket | ttc_181_300s | 30 | 3362 | brownian | brownian | brownian | 0.000044 | 0.171102 | 38576.0000 |
| state_bucket | ttc_301_600s | 34 | 8799 | current_calibrated | market | particle | 0.001892 | 0.200243 | 62447.0000 |
| state_bucket | ttc_gt600s | 34 | 8742 | brownian | brownian | brownian | 0.000170 | 0.241681 | 70368.0000 |
