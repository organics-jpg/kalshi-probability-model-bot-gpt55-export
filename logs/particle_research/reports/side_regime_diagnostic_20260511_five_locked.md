# Side/Regime Diagnostic

- run_count: 5
- selected_count: 15689
- total_counterfactual_pnl_cents: 74321.0000
- stable_positive_rules: 0
- conclusion: No predeclared side/regime diagnostic rule is positive in every supplied run.

## Rule Summary

| rule | positive_runs | selected | total_pnl_cents | min_run_pnl_cents | stable_positive |
|---|---:|---:|---:|---:|---|
| base | 4/5 | 15689 | 74321.0000 | -32502.0000 | False |
| skip_late_300s_against_consensus_05 | 4/5 | 11456 | 67342.0000 | -29552.0000 | False |
| skip_against_consensus_10 | 4/5 | 4316 | 50174.0000 | -11187.0000 | False |
| skip_against_consensus_05 | 4/5 | 2634 | 32436.0000 | -4591.0000 | False |
| require_market_current_consensus_alignment | 4/5 | 298 | 5215.0000 | -1022.0000 | False |
| require_market_agreement | 4/5 | 305 | 5054.0000 | -1073.0000 | False |
| skip_against_consensus_20 | 3/5 | 7093 | 76632.0000 | -10762.0000 | False |
| require_current_agreement | 3/5 | 1281 | 17618.0000 | -3511.0000 | False |
| skip_against_consensus_any | 3/5 | 1288 | 17457.0000 | -3664.0000 | False |

## Buckets

| type | bucket | selected | win_rate | total_pnl_cents | avg_pnl_cents |
|---|---|---:|---:|---:|---:|
| side | no | 7764 | 0.2664 | 12893.0000 | 1.6606 |
| side | yes | 7925 | 0.3192 | 61428.0000 | 7.7512 |
| consensus | against_market_current | 14401 | 0.2636 | 56864.0000 | 3.9486 |
| consensus | aligned_with_market_current | 298 | 0.7450 | 5215.0000 | 17.5000 |
| consensus | market_current_disagree | 990 | 0.5859 | 12242.0000 | 12.3657 |
| confidence | against_strong_05pp_consensus | 1682 | 0.5119 | 17738.0000 | 10.5458 |
| confidence | against_strong_10pp_consensus | 2777 | 0.4332 | 26458.0000 | 9.5275 |
| confidence | against_strong_20pp_consensus | 8596 | 0.1139 | -2311.0000 | -0.2688 |
| confidence | aligned_consensus | 298 | 0.7450 | 5215.0000 | 17.5000 |
| confidence | mixed_or_weak | 2336 | 0.5706 | 27221.0000 | 11.6528 |
| time_to_close | 000_060s | 383 | 0.1227 | 584.0000 | 1.5248 |
| time_to_close | 061_180s | 1901 | 0.1010 | 1286.0000 | 0.6765 |
| time_to_close | 181_300s | 2279 | 0.1641 | 11919.0000 | 5.2299 |
| time_to_close | 301_600s | 5792 | 0.2964 | 25459.0000 | 4.3955 |
| time_to_close | gt_600s | 5334 | 0.4252 | 35073.0000 | 6.5754 |

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
