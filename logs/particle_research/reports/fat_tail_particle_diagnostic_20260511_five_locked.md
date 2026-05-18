# Fat-Tail Particle Diagnostic

- run_count: 5
- spec_count: 13
- promotion_safe: False
- conclusion: No fixed fat-tail/jump-mixture terminal distribution clears strict locked-run gates.
- best_by_brier: gaussian_vol45
- best_by_pnl: gaussian_vol45

## Summary

| spec | runs | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | strict_all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| gaussian_vol45 | 5 | 99334.0000 | 0.171052 | 0.507782 | 4/5 | 4/5 | 2/5 | 1/5 | 3/5 | 3/5 | 0/5 | False |
| tail10_scale3_vol65 | 5 | 75431.0000 | 0.183703 | 0.546597 | 4/5 | 0/5 | 1/5 | 1/5 | 5/5 | 2/5 | 0/5 | False |
| tail05_scale3_vol65 | 5 | 75006.0000 | 0.182413 | 0.542834 | 4/5 | 0/5 | 1/5 | 1/5 | 5/5 | 2/5 | 0/5 | False |
| tail10_scale5_vol65 | 5 | 74880.0000 | 0.184306 | 0.548430 | 4/5 | 0/5 | 1/5 | 1/5 | 5/5 | 2/5 | 0/5 | False |
| gaussian_vol65 | 5 | 74549.0000 | 0.181179 | 0.539127 | 4/5 | 5/5 | 1/5 | 1/5 | 5/5 | 2/5 | 0/5 | False |
| tail10_scale3_down10bps_vol65 | 5 | 74281.0000 | 0.184148 | 0.547365 | 4/5 | 0/5 | 1/5 | 1/5 | 5/5 | 2/5 | 0/5 | False |
| tail20_scale3_vol65 | 5 | 73491.0000 | 0.186455 | 0.554291 | 4/5 | 0/5 | 1/5 | 1/5 | 5/5 | 1/5 | 0/5 | False |
| tail20_scale5_vol65 | 5 | 72211.0000 | 0.187791 | 0.558079 | 4/5 | 0/5 | 1/5 | 1/5 | 5/5 | 1/5 | 0/5 | False |
| tail10_scale3_up10bps_vol65 | 5 | 72020.0000 | 0.183423 | 0.546208 | 4/5 | 2/5 | 1/5 | 1/5 | 5/5 | 1/5 | 0/5 | False |
| gaussian_vol85 | 5 | 71473.0000 | 0.190084 | 0.563034 | 4/5 | 0/5 | 1/5 | 1/5 | 5/5 | 1/5 | 0/5 | False |
| tail20_scale4_up5bps_vol85 | 5 | 70266.0000 | 0.196072 | 0.578536 | 4/5 | 0/5 | 1/5 | 1/5 | 5/5 | 1/5 | 0/5 | False |
| gaussian_vol110 | 5 | 69006.0000 | 0.198914 | 0.584834 | 4/5 | 0/5 | 1/5 | 1/5 | 5/5 | 1/5 | 0/5 | False |
| tail20_scale4_down5bps_vol85 | 5 | 68989.0000 | 0.196402 | 0.579050 | 4/5 | 0/5 | 1/5 | 1/5 | 5/5 | 1/5 | 0/5 | False |

## Runs

| run | spec | candidates | markets | selected | pnl_cents | brier | log_loss | beats_brownian | beats_market | beats_current | ev_rank | top_bucket_pnl | strict |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---|
| particle_side_safety_oos_20260511TLOCKED | gaussian_vol45 | 3398 | 5 | 3143 | 19044.0000 | 0.173422 | 0.520281 | True | False | False | 0.037653 | 7.5318 | False |
| particle_side_safety_oos_20260511TLOCKED | gaussian_vol65 | 3398 | 5 | 3106 | 15483.0000 | 0.186459 | 0.555975 | True | False | False | 0.069530 | 2.4788 | False |
| particle_side_safety_oos_20260511TLOCKED | gaussian_vol85 | 3398 | 5 | 3103 | 12850.0000 | 0.196460 | 0.580305 | False | False | False | 0.104031 | -4.8294 | False |
| particle_side_safety_oos_20260511TLOCKED | gaussian_vol110 | 3398 | 5 | 3078 | 11502.0000 | 0.205579 | 0.601112 | False | False | False | 0.126571 | -5.1482 | False |
| particle_side_safety_oos_20260511TLOCKED | tail05_scale3_vol65 | 3398 | 5 | 3100 | 15067.0000 | 0.187848 | 0.559571 | False | False | False | 0.073411 | 1.3671 | False |
| particle_side_safety_oos_20260511TLOCKED | tail10_scale3_vol65 | 3398 | 5 | 3099 | 15020.0000 | 0.189278 | 0.563209 | False | False | False | 0.076889 | 0.4365 | False |
| particle_side_safety_oos_20260511TLOCKED | tail20_scale3_vol65 | 3398 | 5 | 3097 | 14196.0000 | 0.192267 | 0.570617 | False | False | False | 0.087481 | -1.6753 | False |
| particle_side_safety_oos_20260511TLOCKED | tail10_scale5_vol65 | 3398 | 5 | 3098 | 14493.0000 | 0.189912 | 0.564841 | False | False | False | 0.081528 | 0.4094 | False |
| particle_side_safety_oos_20260511TLOCKED | tail20_scale5_vol65 | 3398 | 5 | 3095 | 13744.0000 | 0.193621 | 0.573968 | False | False | False | 0.093621 | -2.1612 | False |
| particle_side_safety_oos_20260511TLOCKED | tail10_scale3_up10bps_vol65 | 3398 | 5 | 3088 | 12762.0000 | 0.191364 | 0.567920 | False | False | False | 0.084395 | -1.9612 | False |
| particle_side_safety_oos_20260511TLOCKED | tail10_scale3_down10bps_vol65 | 3398 | 5 | 3136 | 16519.0000 | 0.187351 | 0.558820 | False | False | False | 0.082298 | 2.8635 | False |
| particle_side_safety_oos_20260511TLOCKED | tail20_scale4_up5bps_vol85 | 3398 | 5 | 3073 | 10857.0000 | 0.203965 | 0.597510 | False | False | False | 0.125030 | -5.2200 | False |
| particle_side_safety_oos_20260511TLOCKED | tail20_scale4_down5bps_vol85 | 3398 | 5 | 3104 | 12560.0000 | 0.201364 | 0.591921 | False | False | False | 0.122056 | -5.0447 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | gaussian_vol45 | 3501 | 5 | 3213 | 18405.0000 | 0.172162 | 0.523394 | True | False | False | 0.048082 | -0.9167 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | gaussian_vol65 | 3501 | 5 | 3290 | 15595.0000 | 0.188079 | 0.562521 | True | False | False | 0.107785 | -2.7078 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | gaussian_vol85 | 3501 | 5 | 3307 | 12900.0000 | 0.199021 | 0.587418 | False | False | False | 0.149335 | -3.4658 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | gaussian_vol110 | 3501 | 5 | 3317 | 11633.0000 | 0.208420 | 0.607916 | False | False | False | 0.175201 | -4.2374 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | tail05_scale3_vol65 | 3501 | 5 | 3284 | 15670.0000 | 0.189600 | 0.566122 | False | False | False | 0.108023 | -2.7511 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | tail10_scale3_vol65 | 3501 | 5 | 3283 | 15505.0000 | 0.191153 | 0.569758 | False | False | False | 0.111608 | -2.6096 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | tail20_scale3_vol65 | 3501 | 5 | 3301 | 14310.0000 | 0.194357 | 0.577137 | False | False | False | 0.131314 | -2.9932 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | tail10_scale5_vol65 | 3501 | 5 | 3280 | 15284.0000 | 0.191818 | 0.571329 | False | False | False | 0.113990 | -2.5616 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | tail20_scale5_vol65 | 3501 | 5 | 3299 | 14063.0000 | 0.195751 | 0.580350 | False | False | False | 0.135313 | -3.2660 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | tail10_scale3_up10bps_vol65 | 3501 | 5 | 3258 | 10586.0000 | 0.193033 | 0.573741 | False | False | False | 0.127002 | -3.3973 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | tail10_scale3_down10bps_vol65 | 3501 | 5 | 3306 | 17141.0000 | 0.189483 | 0.566258 | False | False | False | 0.114978 | -2.6884 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | tail20_scale4_up5bps_vol85 | 3501 | 5 | 3313 | 10982.0000 | 0.206400 | 0.603593 | False | False | False | 0.169183 | -4.0023 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | tail20_scale4_down5bps_vol85 | 3501 | 5 | 3316 | 13720.0000 | 0.204301 | 0.599195 | False | False | False | 0.160388 | -3.9258 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | gaussian_vol45 | 3414 | 6 | 3225 | 15486.0000 | 0.199628 | 0.578360 | True | True | False | 0.171802 | 15.2529 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | gaussian_vol65 | 3414 | 6 | 3229 | 15653.0000 | 0.206625 | 0.599033 | True | False | False | 0.224801 | 13.7623 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | gaussian_vol85 | 3414 | 6 | 3226 | 16286.0000 | 0.212834 | 0.614668 | False | False | False | 0.248780 | 12.5738 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | gaussian_vol110 | 3414 | 6 | 3221 | 16522.0000 | 0.218849 | 0.628589 | False | False | False | 0.264177 | 11.8396 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | tail05_scale3_vol65 | 3414 | 6 | 3223 | 15861.0000 | 0.207471 | 0.601321 | False | False | False | 0.225936 | 13.0785 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | tail10_scale3_vol65 | 3414 | 6 | 3225 | 15772.0000 | 0.208353 | 0.603650 | False | False | False | 0.232483 | 13.0105 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | tail20_scale3_vol65 | 3414 | 6 | 3227 | 15740.0000 | 0.210223 | 0.608436 | False | False | False | 0.241954 | 12.6522 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | tail10_scale5_vol65 | 3414 | 6 | 3226 | 15770.0000 | 0.208752 | 0.604708 | False | False | False | 0.234644 | 13.0749 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | tail20_scale5_vol65 | 3414 | 6 | 3220 | 15534.0000 | 0.211093 | 0.610634 | False | False | False | 0.245621 | 12.1756 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | tail10_scale3_up10bps_vol65 | 3414 | 6 | 3225 | 18903.0000 | 0.203772 | 0.593755 | True | False | False | 0.228323 | 15.3384 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | tail10_scale3_down10bps_vol65 | 3414 | 6 | 3251 | 13835.0000 | 0.213107 | 0.613910 | False | False | False | 0.236521 | 9.6230 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | tail20_scale4_up5bps_vol85 | 3414 | 6 | 3228 | 17876.0000 | 0.214067 | 0.618314 | False | False | False | 0.263043 | 13.3279 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | tail20_scale4_down5bps_vol85 | 3414 | 6 | 3229 | 14435.0000 | 0.219818 | 0.630349 | False | False | False | 0.265665 | 10.7717 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | gaussian_vol45 | 3260 | 6 | 2458 | -2597.0000 | 0.087010 | 0.302132 | True | False | False | -0.258485 | -7.5276 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | gaussian_vol65 | 3260 | 6 | 3062 | -33071.0000 | 0.107891 | 0.367084 | True | False | False | 0.015706 | -6.8883 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | gaussian_vol85 | 3260 | 6 | 3140 | -36029.0000 | 0.125039 | 0.415793 | False | False | False | 0.163464 | -5.2589 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | gaussian_vol110 | 3260 | 6 | 3163 | -37950.0000 | 0.142204 | 0.460726 | False | False | False | 0.286822 | -5.1632 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | tail05_scale3_vol65 | 3260 | 6 | 3103 | -33702.0000 | 0.110321 | 0.375025 | False | False | False | 0.056299 | -6.7080 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | tail10_scale3_vol65 | 3260 | 6 | 3115 | -34203.0000 | 0.112865 | 0.383052 | False | False | False | 0.090492 | -6.2957 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | tail20_scale3_vol65 | 3260 | 6 | 3124 | -35220.0000 | 0.118296 | 0.399376 | False | False | False | 0.151420 | -5.6294 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | tail10_scale5_vol65 | 3260 | 6 | 3119 | -34412.0000 | 0.114084 | 0.387145 | False | False | False | 0.112178 | -6.1669 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | tail20_scale5_vol65 | 3260 | 6 | 3124 | -35439.0000 | 0.121020 | 0.407778 | False | False | False | 0.186743 | -5.2957 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | tail10_scale3_up10bps_vol65 | 3260 | 6 | 3102 | -36220.0000 | 0.114968 | 0.388325 | False | False | False | 0.097089 | -6.4405 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | tail10_scale3_down10bps_vol65 | 3260 | 6 | 3076 | -31821.0000 | 0.110936 | 0.378230 | False | False | False | 0.058631 | -6.0074 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | tail20_scale4_up5bps_vol85 | 3260 | 6 | 3159 | -37872.0000 | 0.138616 | 0.452491 | False | False | False | 0.283137 | -5.3104 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | tail20_scale4_down5bps_vol85 | 3260 | 6 | 3143 | -36830.0000 | 0.135897 | 0.446189 | False | False | False | 0.266940 | -4.7178 | False |
| particle_residual_blend_oos_RESIDLOCK001 | gaussian_vol45 | 3358 | 5 | 2778 | 48996.0000 | 0.223039 | 0.614742 | False | True | True | -0.040742 | 5.4095 | False |
| particle_residual_blend_oos_RESIDLOCK001 | gaussian_vol65 | 3358 | 5 | 3051 | 60889.0000 | 0.216843 | 0.611024 | True | True | True | 0.008827 | -1.7881 | False |
| particle_residual_blend_oos_RESIDLOCK001 | gaussian_vol85 | 3358 | 5 | 3125 | 65466.0000 | 0.217066 | 0.616987 | False | True | True | 0.018905 | -3.4071 | False |
| particle_residual_blend_oos_RESIDLOCK001 | gaussian_vol110 | 3358 | 5 | 3142 | 67299.0000 | 0.219520 | 0.625829 | False | True | True | 0.030281 | -3.8429 | False |
| particle_residual_blend_oos_RESIDLOCK001 | tail05_scale3_vol65 | 3358 | 5 | 3068 | 62110.0000 | 0.216824 | 0.612134 | False | True | True | 0.006545 | -2.5607 | False |
| particle_residual_blend_oos_RESIDLOCK001 | tail10_scale3_vol65 | 3358 | 5 | 3084 | 63337.0000 | 0.216867 | 0.613315 | False | True | True | 0.003658 | -2.9917 | False |
| particle_residual_blend_oos_RESIDLOCK001 | tail20_scale3_vol65 | 3358 | 5 | 3102 | 64465.0000 | 0.217132 | 0.615891 | False | True | True | 0.005889 | -3.3202 | False |
| particle_residual_blend_oos_RESIDLOCK001 | tail10_scale5_vol65 | 3358 | 5 | 3091 | 63745.0000 | 0.216965 | 0.614129 | False | True | True | 0.002564 | -2.9488 | False |
| particle_residual_blend_oos_RESIDLOCK001 | tail20_scale5_vol65 | 3358 | 5 | 3110 | 64309.0000 | 0.217467 | 0.617666 | False | True | True | 0.009033 | -3.1726 | False |
| particle_residual_blend_oos_RESIDLOCK001 | tail10_scale3_up10bps_vol65 | 3358 | 5 | 3108 | 65989.0000 | 0.213977 | 0.607299 | True | True | True | 0.015398 | -2.2095 | False |
| particle_residual_blend_oos_RESIDLOCK001 | tail10_scale3_down10bps_vol65 | 3358 | 5 | 3055 | 58607.0000 | 0.219860 | 0.619607 | False | True | True | 0.001845 | -3.2929 | False |
| particle_residual_blend_oos_RESIDLOCK001 | tail20_scale4_up5bps_vol85 | 3358 | 5 | 3148 | 68423.0000 | 0.217313 | 0.620772 | False | True | True | 0.025188 | -3.5452 | False |
| particle_residual_blend_oos_RESIDLOCK001 | tail20_scale4_down5bps_vol85 | 3358 | 5 | 3143 | 65104.0000 | 0.220631 | 0.627599 | False | True | True | 0.026383 | -3.9738 | False |

## Run Inputs

| run | rows | markets | candidate_path | label_path |
|---|---:|---:|---|---|
| particle_side_safety_oos_20260511TLOCKED | 3398 | 5 | `logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\pipeline_work\label_contexts_full_refresh.ndjson` |
| particle_dynamic_oos_20260511TLOCKEDNEXT | 3501 | 5 | `logs\particle_research\real_shadow\particle_dynamic_oos_20260511TLOCKEDNEXT\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_dynamic_oos_20260511TLOCKEDNEXT\pipeline_work\label_contexts_full_refresh.ndjson` |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | 3414 | 6 | `logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\pipeline_work\label_contexts_full_refresh.ndjson` |
| particle_side_consensus_oos_CONSENSUSLOCK001 | 3260 | 6 | `logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\pipeline_work\label_contexts_full_refresh.ndjson` |
| particle_residual_blend_oos_RESIDLOCK001 | 3358 | 5 | `logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\pipeline_work\label_contexts_full_refresh.ndjson` |
