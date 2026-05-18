# Side/Regime Diagnostic

- run_count: 9
- selected_count: 31272
- total_counterfactual_pnl_cents: 162539.0000
- stable_positive_rules: 0
- conclusion: No predeclared side/regime diagnostic rule is positive in every supplied run.

## Rule Summary

| rule | positive_runs | selected | total_pnl_cents | min_run_pnl_cents | stable_positive |
|---|---:|---:|---:|---:|---|
| skip_late_300s_against_consensus_05 | 8/9 | 22664 | 147857.0000 | -29552.0000 | False |
| require_market_current_consensus_alignment | 8/9 | 430 | 8770.0000 | -1022.0000 | False |
| require_market_agreement | 8/9 | 438 | 8656.0000 | -1073.0000 | False |
| base | 6/9 | 31272 | 162539.0000 | -32502.0000 | False |
| skip_against_consensus_05 | 6/9 | 4424 | 42372.0000 | -4591.0000 | False |
| require_current_agreement | 6/9 | 2187 | 26690.0000 | -3511.0000 | False |
| skip_against_consensus_any | 6/9 | 2195 | 26576.0000 | -3664.0000 | False |
| skip_against_consensus_20 | 5/9 | 13795 | 84926.0000 | -10762.0000 | False |
| skip_against_consensus_10 | 5/9 | 8278 | 45874.0000 | -11187.0000 | False |

## Buckets

| type | bucket | selected | win_rate | total_pnl_cents | avg_pnl_cents |
|---|---|---:|---:|---:|---:|
| side | no | 16612 | 0.3051 | 99726.0000 | 6.0033 |
| side | yes | 14660 | 0.2808 | 62813.0000 | 4.2847 |
| consensus | against_market_current | 29077 | 0.2707 | 135963.0000 | 4.6760 |
| consensus | aligned_with_market_current | 430 | 0.7651 | 8770.0000 | 20.3953 |
| consensus | market_current_disagree | 1765 | 0.5592 | 17806.0000 | 10.0884 |
| confidence | against_strong_05pp_consensus | 3854 | 0.3858 | 3502.0000 | 0.9087 |
| confidence | against_strong_10pp_consensus | 5517 | 0.4086 | 39052.0000 | 7.0785 |
| confidence | against_strong_20pp_consensus | 17477 | 0.1699 | 77613.0000 | 4.4409 |
| confidence | aligned_consensus | 430 | 0.7651 | 8770.0000 | 20.3953 |
| confidence | mixed_or_weak | 3994 | 0.5376 | 33602.0000 | 8.4131 |
| time_to_close | 000_060s | 666 | 0.0706 | 298.0000 | 0.4474 |
| time_to_close | 061_180s | 3865 | 0.0807 | -5927.0000 | -1.5335 |
| time_to_close | 181_300s | 4646 | 0.1722 | 24170.0000 | 5.2023 |
| time_to_close | 301_600s | 11683 | 0.2676 | 27841.0000 | 2.3830 |
| time_to_close | gt_600s | 10412 | 0.4707 | 116157.0000 | 11.1561 |

## Rule By Run

| run | rule | selected | win_rate | pnl_cents |
|---|---|---:|---:|---:|
| particle_side_safety_oos_20260511TLOCKED | base | 3111 | 0.3083 | 14916.0000 |
| particle_side_safety_oos_20260511TLOCKED | require_market_agreement | 88 | 0.9205 | 3302.0000 |
| particle_side_safety_oos_20260511TLOCKED | require_current_agreement | 363 | 0.6970 | 7595.0000 |
| particle_side_safety_oos_20260511TLOCKED | require_market_current_consensus_alignment | 85 | 0.9294 | 3259.0000 |
| particle_side_safety_oos_20260511TLOCKED | skip_against_consensus_any | 366 | 0.6967 | 7638.0000 |
| particle_side_safety_oos_20260511TLOCKED | skip_against_consensus_05 | 676 | 0.6568 | 13050.0000 |
| particle_side_safety_oos_20260511TLOCKED | skip_against_consensus_10 | 1030 | 0.6252 | 19325.0000 |
| particle_side_safety_oos_20260511TLOCKED | skip_against_consensus_20 | 1651 | 0.5015 | 17856.0000 |
| particle_side_safety_oos_20260511TLOCKED | skip_late_300s_against_consensus_05 | 2291 | 0.4064 | 19183.0000 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | base | 3275 | 0.3102 | 15798.0000 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | require_market_agreement | 86 | 0.8256 | 1813.0000 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | require_current_agreement | 358 | 0.8352 | 11760.0000 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | require_market_current_consensus_alignment | 86 | 0.8256 | 1813.0000 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | skip_against_consensus_any | 358 | 0.8352 | 11760.0000 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | skip_against_consensus_05 | 736 | 0.6957 | 15936.0000 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | skip_against_consensus_10 | 1192 | 0.6309 | 21349.0000 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | skip_against_consensus_20 | 1564 | 0.5844 | 24767.0000 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | skip_late_300s_against_consensus_05 | 2298 | 0.3925 | 13790.0000 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | base | 3229 | 0.2880 | 15777.0000 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | require_market_agreement | 22 | 0.6364 | 188.0000 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | require_current_agreement | 242 | 0.3058 | -3511.0000 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | require_market_current_consensus_alignment | 19 | 0.7368 | 341.0000 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | skip_against_consensus_any | 245 | 0.3020 | -3664.0000 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | skip_against_consensus_05 | 598 | 0.3729 | -4591.0000 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | skip_against_consensus_10 | 892 | 0.2993 | -11187.0000 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | skip_against_consensus_20 | 1539 | 0.3730 | -1327.0000 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | skip_late_300s_against_consensus_05 | 2373 | 0.3249 | 4915.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | base | 3029 | 0.0888 | -32502.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | require_market_agreement | 50 | 0.7400 | 824.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | require_current_agreement | 104 | 0.7500 | 2490.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | require_market_current_consensus_alignment | 50 | 0.7400 | 824.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | skip_against_consensus_any | 104 | 0.7500 | 2490.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | skip_against_consensus_05 | 193 | 0.6269 | 2769.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | skip_against_consensus_10 | 429 | 0.4918 | 1447.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | skip_against_consensus_20 | 932 | 0.2833 | -10762.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | skip_late_300s_against_consensus_05 | 2235 | 0.1141 | -29552.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | base | 3045 | 0.4677 | 60332.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | require_market_agreement | 59 | 0.3559 | -1073.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | require_current_agreement | 214 | 0.4486 | -716.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | require_market_current_consensus_alignment | 58 | 0.3621 | -1022.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | skip_against_consensus_any | 215 | 0.4465 | -767.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | skip_against_consensus_05 | 431 | 0.5916 | 5272.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | skip_against_consensus_10 | 773 | 0.7012 | 19240.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | skip_against_consensus_20 | 1407 | 0.7385 | 46098.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | skip_late_300s_against_consensus_05 | 2259 | 0.5936 | 59006.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | base | 2416 | 0.4284 | 50400.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | require_market_agreement | 15 | 0.6000 | 98.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | require_current_agreement | 87 | 0.4598 | -178.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | require_market_current_consensus_alignment | 14 | 0.5714 | 51.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | skip_against_consensus_any | 88 | 0.4659 | -131.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | skip_against_consensus_05 | 239 | 0.3180 | -3237.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | skip_against_consensus_10 | 472 | 0.3559 | -3532.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | skip_against_consensus_20 | 778 | 0.5013 | 8261.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | skip_late_300s_against_consensus_05 | 1832 | 0.4776 | 37899.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | base | 4574 | 0.3684 | 47336.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | require_market_agreement | 50 | 0.8400 | 1437.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | require_current_agreement | 296 | 0.5676 | 2410.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | require_market_current_consensus_alignment | 50 | 0.8400 | 1437.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | skip_against_consensus_any | 296 | 0.5676 | 2410.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | skip_against_consensus_05 | 650 | 0.4538 | -1044.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | skip_against_consensus_10 | 1144 | 0.4082 | -3808.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | skip_against_consensus_20 | 2178 | 0.3581 | -7101.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | skip_late_300s_against_consensus_05 | 3160 | 0.4342 | 34246.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | base | 4214 | 0.2283 | -7134.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | require_market_agreement | 56 | 0.8214 | 1607.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | require_current_agreement | 361 | 0.5346 | 3180.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | require_market_current_consensus_alignment | 56 | 0.8214 | 1607.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | skip_against_consensus_any | 361 | 0.5346 | 3180.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | skip_against_consensus_05 | 580 | 0.5500 | 6035.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | skip_against_consensus_10 | 1667 | 0.2921 | -9794.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | skip_against_consensus_20 | 2229 | 0.3190 | -5573.0000 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | skip_late_300s_against_consensus_05 | 3021 | 0.3174 | 3137.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | base | 4379 | 0.2069 | -2384.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | require_market_agreement | 12 | 0.9167 | 460.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | require_current_agreement | 162 | 0.6914 | 3660.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | require_market_current_consensus_alignment | 12 | 0.9167 | 460.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | skip_against_consensus_any | 162 | 0.6914 | 3660.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | skip_against_consensus_05 | 321 | 0.7196 | 8182.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | skip_against_consensus_10 | 679 | 0.6259 | 12834.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | skip_against_consensus_20 | 1517 | 0.4726 | 12707.0000 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | skip_late_300s_against_consensus_05 | 3195 | 0.2836 | 5233.0000 |
