# Empirical Current-Anchor Diagnostic

- eligible_run_count: 6
- skipped_run_count: 3
- spec_count: 4
- candidate_ready_for_predeclared_shadow: False
- promotion_safe: False
- conclusion: No current-anchored empirical next-second spec cleared strict eligible locked-run gates.

## Summary

| spec | runs | pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_bucket | market_ev_rank | market_top_bucket | strict | fallback_current | avg_returns | avg_spot_age_ms | avg_ann_vol | strict_all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| current_emp610_w25_center | 6 | -19237.0000 | 0.189751 | 0.548716 | 2/6 | 3/6 | 2/6 | 4/6 | 2/6 | 3/6 | 3/6 | 3/6 | 1/6 | 864 | 548.59 | 12171.88 | 0.279696 | False |
| current_emp610_w10_center | 6 | -26643.0000 | 0.190067 | 0.549361 | 2/6 | 3/6 | 2/6 | 4/6 | 2/6 | 2/6 | 4/6 | 3/6 | 1/6 | 864 | 548.59 | 12171.88 | 0.279696 | False |
| current_emp987_w10_mean25 | 6 | -38652.0000 | 0.190732 | 0.551469 | 2/6 | 3/6 | 2/6 | 3/6 | 2/6 | 2/6 | 4/6 | 3/6 | 1/6 | 910 | 845.67 | 12171.88 | 0.280731 | False |
| current_emp987_w25_mean25 | 6 | -44341.0000 | 0.191536 | 0.554267 | 2/6 | 3/6 | 2/6 | 3/6 | 2/6 | 2/6 | 3/6 | 4/6 | 1/6 | 910 | 845.67 | 12171.88 | 0.280731 | False |

## Runs

| run | spec | candidates | markets | selected | fallback_current | avg_returns | avg_spot_age_ms | avg_ann_vol | pnl_cents | brier | beats_current | ev_rank | top_bucket | market_ev_rank | market_top_bucket | strict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| particle_side_consensus_oos_CONSENSUSLOCK001 | current_emp610_w10_center | 3260 | 6 | 2645 | 4 | 575.84 | 287.83 | 0.401113 | 35190.0000 | 0.065133 | False | 0.443331 | 18.6405 | 0.600000 | 16.4953 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | current_emp610_w25_center | 3260 | 6 | 2581 | 4 | 575.84 | 287.83 | 0.401113 | 33036.0000 | 0.067068 | False | 0.427630 | 18.1509 | 0.733333 | 16.2111 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | current_emp987_w10_mean25 | 3260 | 6 | 2627 | 4 | 884.01 | 287.83 | 0.399990 | 31539.0000 | 0.065940 | False | 0.452540 | 17.6503 | 0.733333 | 16.7306 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | current_emp987_w25_mean25 | 3260 | 6 | 2664 | 4 | 884.01 | 287.83 | 0.399990 | 24125.0000 | 0.069035 | False | 0.414080 | 15.6957 | 0.466667 | 16.7953 | False |
| particle_residual_blend_oos_RESIDLOCK001 | current_emp610_w10_center | 3358 | 5 | 2474 | 18 | 558.05 | 201.15 | 0.337908 | -23413.0000 | 0.241569 | True | -0.108887 | -9.4298 | 0.200000 | -9.0819 | False |
| particle_residual_blend_oos_RESIDLOCK001 | current_emp610_w25_center | 3358 | 5 | 2401 | 18 | 558.05 | 201.15 | 0.337908 | -22948.0000 | 0.240902 | True | -0.124822 | -10.7667 | 0.000000 | -8.8125 | False |
| particle_residual_blend_oos_RESIDLOCK001 | current_emp987_w10_mean25 | 3358 | 5 | 2462 | 27 | 853.61 | 201.15 | 0.343014 | -16430.0000 | 0.239656 | True | -0.100802 | -8.0179 | 0.600000 | -3.7889 | False |
| particle_residual_blend_oos_RESIDLOCK001 | current_emp987_w25_mean25 | 3358 | 5 | 2491 | 27 | 853.61 | 201.15 | 0.343014 | -5402.0000 | 0.236323 | True | -0.066455 | -3.0024 | 0.600000 | 5.2375 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | current_emp610_w10_center | 2514 | 4 | 1739 | 1 | 545.27 | 296.45 | 0.271151 | -4831.0000 | 0.274006 | True | -0.094553 | -2.3100 | 0.333333 | -3.9076 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | current_emp610_w25_center | 2514 | 4 | 1681 | 1 | 545.27 | 296.45 | 0.271151 | -2448.0000 | 0.272681 | True | -0.057898 | 0.0079 | 0.666667 | -2.0107 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | current_emp987_w10_mean25 | 2514 | 4 | 1756 | 9 | 826.90 | 296.45 | 0.267415 | -14700.0000 | 0.277497 | False | -0.128681 | -10.1638 | 0.000000 | -3.6426 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | current_emp987_w25_mean25 | 2514 | 4 | 1774 | 9 | 826.90 | 296.45 | 0.267415 | -22246.0000 | 0.281676 | False | -0.140791 | -18.1272 | 0.000000 | -38.4247 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | current_emp610_w10_center | 4843 | 7 | 3805 | 21 | 575.26 | 301.37 | 0.295264 | -28831.0000 | 0.265548 | True | -0.085976 | -6.9273 | -0.142857 | 6.7351 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | current_emp610_w25_center | 4843 | 7 | 3701 | 21 | 575.26 | 301.37 | 0.295264 | -21682.0000 | 0.262617 | True | -0.064923 | -4.0520 | -0.142857 | 7.1733 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | current_emp987_w10_mean25 | 4843 | 7 | 3836 | 30 | 898.52 | 301.37 | 0.303365 | -35482.0000 | 0.266897 | True | -0.085707 | -7.1569 | 0.047619 | 6.0081 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | current_emp987_w25_mean25 | 4843 | 7 | 3861 | 30 | 898.52 | 301.37 | 0.303365 | -37852.0000 | 0.266068 | True | -0.069800 | -7.0066 | -0.047619 | 5.5655 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | current_emp610_w10_center | 4405 | 6 | 3604 | 801 | 463.04 | 71621.96 | 0.166490 | -35750.0000 | 0.172508 | False | -0.052894 | -10.5672 | -0.200000 | -12.4125 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | current_emp610_w25_center | 4405 | 6 | 3637 | 801 | 463.04 | 71621.96 | 0.166490 | -37324.0000 | 0.174383 | False | -0.075103 | -13.4546 | -0.333333 | -12.4208 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | current_emp987_w10_mean25 | 4405 | 6 | 3514 | 811 | 716.77 | 71621.96 | 0.166012 | -34529.0000 | 0.173146 | False | -0.074682 | -10.8766 | -0.066667 | -12.1302 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | current_emp987_w25_mean25 | 4405 | 6 | 3535 | 811 | 716.77 | 71621.96 | 0.166012 | -35614.0000 | 0.176122 | False | -0.093726 | -15.0744 | -0.200000 | -11.8703 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | current_emp610_w10_center | 4512 | 7 | 3474 | 19 | 574.06 | 322.54 | 0.206253 | 30992.0000 | 0.121638 | True | 0.128947 | 11.7287 | 0.047619 | 3.5716 | True |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | current_emp610_w25_center | 4512 | 7 | 3450 | 19 | 574.06 | 322.54 | 0.206253 | 32129.0000 | 0.120858 | True | 0.158702 | 12.9415 | 0.333333 | 17.7308 | True |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | current_emp987_w10_mean25 | 4512 | 7 | 3540 | 29 | 894.23 | 322.54 | 0.204588 | 30950.0000 | 0.121254 | True | 0.136639 | 11.3369 | 0.047619 | 3.6135 | True |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | current_emp987_w25_mean25 | 4512 | 7 | 3547 | 29 | 894.23 | 322.54 | 0.204588 | 32648.0000 | 0.119993 | True | 0.185871 | 12.6179 | 0.142857 | 4.8671 | True |

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
