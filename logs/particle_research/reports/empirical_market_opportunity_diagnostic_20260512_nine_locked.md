# Empirical Market Opportunity Diagnostic

- eligible_run_count: 6
- skipped_run_count: 3
- families: empirical, current_anchor
- opportunity_rows: 280
- candidate_ready_for_predeclared_shadow: False
- promotion_safe: False
- conclusion: No empirical market-opportunity spec cleared strict eligible locked-run gates.

## Summary

| family | spec | runs | markets | selected_markets | pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_bucket | strict | strict_all |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| empirical | emp1s_987_mean25_blend25_p128_d64 | 6 | 35 | 35 | 198.0000 | 0.234474 | 0.677148 | 3/6 | 3/6 | 2/6 | 2/6 | 3/6 | 3/6 | 2/6 | False |
| empirical | emp1s_610_mean25_blend25_p128_d64 | 6 | 35 | 35 | 153.0000 | 0.231879 | 0.663541 | 3/6 | 3/6 | 1/6 | 1/6 | 3/6 | 3/6 | 1/6 | False |
| current_anchor | current_emp610_w10_center | 6 | 35 | 35 | 155.0000 | 0.213411 | 0.612979 | 5/6 | 3/6 | 2/6 | 5/6 | 3/6 | 3/6 | 0/6 | False |
| current_anchor | current_emp987_w25_mean25 | 6 | 35 | 35 | -174.0000 | 0.239940 | 0.670583 | 2/6 | 2/6 | 2/6 | 4/6 | 5/6 | 2/6 | 0/6 | False |
| current_anchor | current_emp610_w25_center | 6 | 35 | 35 | -66.0000 | 0.205602 | 0.594589 | 3/6 | 3/6 | 1/6 | 4/6 | 4/6 | 3/6 | 0/6 | False |
| current_anchor | current_emp987_w10_mean25 | 6 | 35 | 35 | 213.0000 | 0.206355 | 0.594415 | 5/6 | 3/6 | 2/6 | 3/6 | 4/6 | 3/6 | 0/6 | False |
| empirical | emp1s_610_center_blend50_p96_d48 | 6 | 35 | 35 | 262.0000 | 0.135868 | 0.442105 | 6/6 | 6/6 | 1/6 | 2/6 | 3/6 | 1/6 | 0/6 | False |
| empirical | emp1s_233_center_blend50_p96_d48 | 6 | 35 | 35 | 128.0000 | 0.111808 | 0.389604 | 5/6 | 6/6 | 0/6 | 0/6 | 1/6 | 1/6 | 0/6 | False |

## Runs

| run | family | spec | candidates | markets | selected_markets | pnl_cents | avg_pnl_market | brier | beats_current | ev_rank | top_bucket | strict |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| particle_side_consensus_oos_CONSENSUSLOCK001 | empirical | emp1s_233_center_blend50_p96_d48 | 3260 | 6 | 6 | -67.0000 | -11.1667 | 0.092078 | False | 0.000000 | -2.5000 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | empirical | emp1s_610_center_blend50_p96_d48 | 3260 | 6 | 6 | 34.0000 | 5.6667 | 0.101968 | False | 0.428571 | 38.5000 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | empirical | emp1s_610_mean25_blend25_p128_d64 | 3260 | 6 | 6 | -40.0000 | -6.6667 | 0.122245 | False | 0.142857 | -3.0000 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | empirical | emp1s_987_mean25_blend25_p128_d64 | 3260 | 6 | 6 | -39.0000 | -6.5000 | 0.130412 | False | -0.142857 | -5.5000 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | current_anchor | current_emp610_w10_center | 3260 | 6 | 6 | 147.0000 | 24.5000 | 0.088941 | False | 0.333333 | 23.5000 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | current_anchor | current_emp610_w25_center | 3260 | 6 | 6 | 146.0000 | 24.3333 | 0.089498 | False | 0.333333 | 23.5000 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | current_anchor | current_emp987_w10_mean25 | 3260 | 6 | 6 | 146.0000 | 24.3333 | 0.087235 | False | 0.333333 | 23.5000 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | current_anchor | current_emp987_w25_mean25 | 3260 | 6 | 6 | 143.0000 | 23.8333 | 0.085280 | False | 0.200000 | 23.5000 | False |
| particle_residual_blend_oos_RESIDLOCK001 | empirical | emp1s_233_center_blend50_p96_d48 | 3358 | 5 | 5 | 27.0000 | 5.4000 | 0.080909 | False | -0.400000 | -8.0000 | False |
| particle_residual_blend_oos_RESIDLOCK001 | empirical | emp1s_610_center_blend50_p96_d48 | 3358 | 5 | 5 | 116.0000 | 23.2000 | 0.162833 | True | -0.200000 | -4.5000 | False |
| particle_residual_blend_oos_RESIDLOCK001 | empirical | emp1s_610_mean25_blend25_p128_d64 | 3358 | 5 | 5 | 170.0000 | 34.0000 | 0.226296 | True | 0.400000 | 7.5000 | True |
| particle_residual_blend_oos_RESIDLOCK001 | empirical | emp1s_987_mean25_blend25_p128_d64 | 3358 | 5 | 5 | 51.0000 | 10.2000 | 0.270247 | True | 0.200000 | 7.5000 | True |
| particle_residual_blend_oos_RESIDLOCK001 | current_anchor | current_emp610_w10_center | 3358 | 5 | 5 | 77.0000 | 15.4000 | 0.316092 | True | 0.600000 | 17.5000 | False |
| particle_residual_blend_oos_RESIDLOCK001 | current_anchor | current_emp610_w25_center | 3358 | 5 | 5 | -32.0000 | -6.4000 | 0.378689 | False | 0.800000 | 17.0000 | False |
| particle_residual_blend_oos_RESIDLOCK001 | current_anchor | current_emp987_w10_mean25 | 3358 | 5 | 5 | 77.0000 | 15.4000 | 0.316954 | False | 0.600000 | 17.5000 | False |
| particle_residual_blend_oos_RESIDLOCK001 | current_anchor | current_emp987_w25_mean25 | 3358 | 5 | 5 | -24.0000 | -4.8000 | 0.399869 | False | 0.800000 | 17.5000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | empirical | emp1s_233_center_blend50_p96_d48 | 2514 | 4 | 4 | 59.0000 | 14.7500 | 0.136824 | False | 0.000000 | 0.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | empirical | emp1s_610_center_blend50_p96_d48 | 2514 | 4 | 4 | 18.0000 | 4.5000 | 0.197823 | True | 0.333333 | -3.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | empirical | emp1s_610_mean25_blend25_p128_d64 | 2514 | 4 | 4 | -115.0000 | -28.7500 | 0.346217 | False | -1.000000 | -56.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | empirical | emp1s_987_mean25_blend25_p128_d64 | 2514 | 4 | 4 | -126.0000 | -31.5000 | 0.347340 | False | 0.000000 | -61.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | current_anchor | current_emp610_w10_center | 2514 | 4 | 4 | 4.0000 | 1.0000 | 0.152857 | True | -0.333333 | -3.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | current_anchor | current_emp610_w25_center | 2514 | 4 | 4 | 3.0000 | 0.7500 | 0.137591 | True | -0.333333 | -3.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | current_anchor | current_emp987_w10_mean25 | 2514 | 4 | 4 | 5.0000 | 1.2500 | 0.152028 | True | -0.333333 | -3.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | current_anchor | current_emp987_w25_mean25 | 2514 | 4 | 4 | -126.0000 | -31.5000 | 0.292452 | True | 0.666667 | -3.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | empirical | emp1s_233_center_blend50_p96_d48 | 4843 | 7 | 7 | 36.0000 | 5.1429 | 0.092814 | False | -0.600000 | -4.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | empirical | emp1s_610_center_blend50_p96_d48 | 4843 | 7 | 7 | 25.0000 | 3.5714 | 0.106372 | False | -0.142857 | -6.5000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | empirical | emp1s_610_mean25_blend25_p128_d64 | 4843 | 7 | 7 | 21.0000 | 3.0000 | 0.181637 | False | -0.142857 | 13.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | empirical | emp1s_987_mean25_blend25_p128_d64 | 4843 | 7 | 7 | 184.0000 | 26.2857 | 0.176485 | True | 0.523810 | 82.0000 | True |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | current_anchor | current_emp610_w10_center | 4843 | 7 | 7 | -153.0000 | -21.8571 | 0.304413 | True | 0.142857 | -16.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | current_anchor | current_emp610_w25_center | 4843 | 7 | 7 | -155.0000 | -22.1429 | 0.270834 | True | 0.238095 | -16.5000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | current_anchor | current_emp987_w10_mean25 | 4843 | 7 | 7 | -153.0000 | -21.8571 | 0.300738 | True | 0.142857 | -16.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | current_anchor | current_emp987_w25_mean25 | 4843 | 7 | 7 | -154.0000 | -22.0000 | 0.266775 | True | 0.142857 | -16.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | empirical | emp1s_233_center_blend50_p96_d48 | 4405 | 6 | 6 | 31.0000 | 5.1667 | 0.154940 | False | -0.142857 | -4.5000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | empirical | emp1s_610_center_blend50_p96_d48 | 4405 | 6 | 6 | 32.0000 | 5.3333 | 0.148516 | False | -0.166667 | -4.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | empirical | emp1s_610_mean25_blend25_p128_d64 | 4405 | 6 | 6 | -20.0000 | -3.3333 | 0.366813 | False | -0.200000 | -14.5000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | empirical | emp1s_987_mean25_blend25_p128_d64 | 4405 | 6 | 6 | -5.0000 | -0.8333 | 0.317736 | False | -0.200000 | -4.5000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | current_anchor | current_emp610_w10_center | 4405 | 6 | 6 | 58.0000 | 9.6667 | 0.288319 | True | -0.333333 | -2.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | current_anchor | current_emp610_w25_center | 4405 | 6 | 6 | -49.0000 | -8.1667 | 0.238159 | True | 0.066667 | -2.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | current_anchor | current_emp987_w10_mean25 | 4405 | 6 | 6 | 69.0000 | 11.5000 | 0.275589 | False | -0.333333 | -2.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | current_anchor | current_emp987_w25_mean25 | 4405 | 6 | 6 | -81.0000 | -13.5000 | 0.302662 | True | 0.333333 | -2.0000 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | empirical | emp1s_233_center_blend50_p96_d48 | 4512 | 7 | 7 | 42.0000 | 6.0000 | 0.113282 | False | 0.400000 | 38.5000 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | empirical | emp1s_610_center_blend50_p96_d48 | 4512 | 7 | 7 | 37.0000 | 5.2857 | 0.097693 | False | 0.300000 | -5.0000 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | empirical | emp1s_610_mean25_blend25_p128_d64 | 4512 | 7 | 7 | 137.0000 | 19.5714 | 0.148069 | False | 0.238095 | 9.0000 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | empirical | emp1s_987_mean25_blend25_p128_d64 | 4512 | 7 | 7 | 133.0000 | 19.0000 | 0.164622 | False | 0.200000 | 8.5000 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | current_anchor | current_emp610_w10_center | 4512 | 7 | 7 | 22.0000 | 3.1429 | 0.129845 | True | -0.142857 | 9.0000 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | current_anchor | current_emp610_w25_center | 4512 | 7 | 7 | 21.0000 | 3.0000 | 0.118839 | True | -0.238095 | 9.0000 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | current_anchor | current_emp987_w10_mean25 | 4512 | 7 | 7 | 69.0000 | 9.8571 | 0.105586 | True | 0.100000 | 9.0000 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | current_anchor | current_emp987_w25_mean25 | 4512 | 7 | 7 | 68.0000 | 9.7143 | 0.092599 | True | -0.047619 | -5.0000 | False |

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

- `logs\particle_research\real_shadow\particle_spot_rv_terminal_oos_RVTERMLOCK002`
- `logs\particle_research\real_shadow\particle_spot_rv_terminal_oos_RVTERMLOCK003`
- `logs\particle_research\real_shadow\particle_spot_rv_terminal_oos_RVTERMLOCK004`
