# OOS Stability Report

- run_count: 9
- runs: particle_side_safety_oos_20260511TLOCKED, particle_dynamic_oos_20260511TLOCKEDNEXT, particle_dynamic600_oos_20260511TLOCKEDNEXT2, particle_side_consensus_oos_CONSENSUSLOCK001, particle_residual_blend_oos_RESIDLOCK001, particle_fixed_terminal_oos_GAUSS45LOCK001, particle_fixed_terminal_oos_GAUSS45LOCK002, particle_fixed_terminal_oos_GAUSS45LOCK003, particle_spot_rv_terminal_oos_RVTERMLOCK001
- min_runs_for_stability: 2
- variant_row_count: 207
- stability_row_count: 43
- stable_candidate_count: 0
- promotion_safe: False
- note: This is a locked-run stability diagnostic. It does not promote a strategy by itself; any new variant selected from this table needs a predeclared fresh OOS run.

## Stability Rows

| source | variant | runs | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | positive_ev_rank | positive_top_bucket | beats_brownian | beats_market | beats_current | stable_all_runs |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| probability | brownian | 9 | 164407.0000 | 0.192336 | 0.564991 | 6 | 9 | 4 | 0 | 3 | 3 | False |
| probability | particle | 9 | 162539.0000 | 0.192407 | 0.565107 | 6 | 8 | 4 | 4 | 3 | 3 | False |
| static | particle | 9 | 162539.0000 | 0.192407 | 0.565107 | 6 | 8 | 4 | 4 | 3 | 3 | False |
| probability | market_current_particle_40_40_20 | 9 | 147718.0000 | 0.180615 | 0.527002 | 8 | 2 | 7 | 6 | 4 | 5 | False |
| probability | market_particle_75_25 | 9 | 140336.0000 | 0.180535 | 0.526621 | 6 | 4 | 3 | 6 | 4 | 5 | False |
| fixed_terminal | gaussian_vol45_terminal_v1 | 4 | 138771.0000 | 0.221879 | 0.624243 | 3 | 2 | 3 | 1 | 3 | 3 | False |
| probability | current_particle_75_25 | 9 | 138720.0000 | 0.182057 | 0.531452 | 8 | 3 | 8 | 6 | 3 | 4 | False |
| ensemble | blend_50current_25particle_25rv600 | 5 | 86624.0000 | 0.165104 | 0.487718 | 5 | 3 | 5 | 4 | 3 | 2 | False |
| materialized | late300_consensus_mc75_online_logit_rv600 | 3 | 82411.0000 | 0.168345 | 0.493215 | 3 | 2 | 3 | 3 | 2 | 2 | False |
| materialized | online_logit_market_mean_rolling_vol_600s | 3 | 82411.0000 | 0.168345 | 0.493215 | 3 | 2 | 3 | 3 | 2 | 2 | False |
| online_logit | online_logit_market_mean_rolling_vol_600s | 3 | 82411.0000 | 0.168345 | 0.493215 | 3 | 2 | 3 | 3 | 2 | 2 | False |
| materialized | late300_mc50_online_logit_rv600 | 3 | 81816.0000 | 0.168725 | 0.494751 | 3 | 2 | 3 | 3 | 2 | 2 | False |
| materialized | late180_mc75_online_logit_rv600 | 3 | 81284.0000 | 0.168545 | 0.494422 | 3 | 2 | 3 | 3 | 2 | 2 | False |
| online_logit | online_logit_market_mean_median_current_rv300_rv600 | 3 | 80694.0000 | 0.168839 | 0.495572 | 3 | 2 | 3 | 3 | 2 | 2 | False |
| materialized | late300_mc75_online_logit_rv600 | 3 | 78074.0000 | 0.169113 | 0.496068 | 3 | 2 | 3 | 3 | 2 | 2 | False |
| online_logit | online_logit_market_mean_rolling_vol_300s | 3 | 76099.0000 | 0.169932 | 0.499189 | 3 | 2 | 3 | 3 | 2 | 2 | False |
| ensemble | blend_50rv600_30current_20market | 5 | 73668.0000 | 0.165397 | 0.481393 | 4 | 3 | 4 | 4 | 4 | 3 | False |
| online_logit | online_logit_market_mean_current_calibrated | 3 | 71796.0000 | 0.172175 | 0.505575 | 3 | 2 | 3 | 3 | 3 | 2 | False |
| ensemble | blend_40current_30rv300_30rv600 | 5 | 70921.0000 | 0.165637 | 0.483030 | 4 | 3 | 4 | 4 | 3 | 2 | False |
| online_logit | online_logit_particle | 4 | 70349.0000 | 0.298473 | 0.891493 | 2 | 2 | 1 | 1 | 1 | 1 | False |
| ensemble | mean_current_rv300_rv600 | 5 | 67496.0000 | 0.165899 | 0.483908 | 4 | 3 | 4 | 4 | 3 | 2 | False |
| online_logit | online_logit_market_mean_blend_50current_25particle_25rv600 | 3 | 66200.0000 | 0.171807 | 0.510183 | 3 | 3 | 3 | 3 | 2 | 1 | False |
| ensemble | mean_market_current_rv300_rv600 | 5 | 65294.0000 | 0.166021 | 0.483441 | 4 | 3 | 4 | 4 | 4 | 3 | False |
| ensemble | median_current_rv300_rv600 | 5 | 61976.0000 | 0.166380 | 0.484992 | 4 | 2 | 3 | 4 | 2 | 2 | False |
| ensemble | median_market_current_rv600 | 5 | 60349.0000 | 0.166129 | 0.482801 | 4 | 3 | 4 | 4 | 3 | 3 | False |
| ensemble | blend_40rv600_30rv300_20current_10market | 5 | 60065.0000 | 0.166240 | 0.484649 | 4 | 2 | 4 | 4 | 3 | 2 | False |
| dynamic | rolling_vol_600s | 5 | 53965.0000 | 0.166822 | 0.485819 | 3 | 2 | 3 | 4 | 2 | 2 | False |
| probability | market_current_50_50 | 9 | 53606.0000 | 0.182224 | 0.528968 | 5 | 2 | 6 | 6 | 5 | 4 | False |
| online_logit | online_logit_market_mean_particle | 3 | 48864.0000 | 0.193526 | 0.571969 | 3 | 3 | 2 | 2 | 0 | 0 | False |
| dynamic | rolling_vol_300s | 5 | 43332.0000 | 0.168972 | 0.493101 | 3 | 2 | 3 | 4 | 2 | 2 | False |
| online_logit | online_logit_current_calibrated | 4 | 40536.0000 | 0.252922 | 0.772519 | 3 | 4 | 2 | 2 | 0 | 0 | False |
| dynamic | rolling_vol_300s_market25 | 5 | 39801.0000 | 0.168160 | 0.489905 | 3 | 2 | 3 | 4 | 3 | 2 | False |
| probability | current_calibrated | 9 | 38512.0000 | 0.184398 | 0.535508 | 5 | 4 | 5 | 6 | 5 | 0 | False |
| dynamic | rolling_vol_120s | 5 | 29823.0000 | 0.172970 | 0.503169 | 3 | 1 | 3 | 4 | 1 | 1 | False |
| online_logit | online_logit_rolling_vol_600s | 4 | 29259.0000 | 0.247157 | 0.743517 | 2 | 4 | 2 | 1 | 0 | 0 | False |
| online_logit | online_logit_median_current_rv300_rv600 | 4 | 27566.0000 | 0.252198 | 0.758992 | 2 | 4 | 2 | 1 | 0 | 0 | False |
| online_logit | online_logit_rolling_vol_300s | 4 | 21094.0000 | 0.256455 | 0.773182 | 2 | 4 | 2 | 0 | 0 | 0 | False |
| online_logit | online_logit_blend_50current_25particle_25rv600 | 4 | 20139.0000 | 0.256032 | 0.764088 | 2 | 4 | 2 | 1 | 1 | 0 | False |
| materialized | spot_realized_vol_terminal_oos_locked | 1 | 17528.0000 | 0.133252 | 0.430335 | 1 | 0 | 0 | 1 | 0 | 0 | False |
| spot_realized_vol_terminal | rv233_blend50_fixed65_terminal_v1 | 2 | 7632.0000 | 0.155044 | 0.477944 | 1 | 0 | 0 | 2 | 0 | 0 | False |
| side_consensus | skip_against_market_current_consensus_10_v1 | 1 | 1447.0000 | 0.108039 | 0.367319 | 1 | 1 | 0 | 0 | 0 | 0 | False |
| probability | market | 9 | 0.0000 | 0.182888 | 0.529190 | 0 | 0 | 0 | 6 | 0 | 4 | False |
| residual_blend | resid_current_rv300n20_rv600p20_particle_n10_v1 | 1 | -28864.0000 | 0.244988 | 0.660681 | 0 | 0 | 0 | 0 | 0 | 0 | False |
