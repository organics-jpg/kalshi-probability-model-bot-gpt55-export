# Empirical Next-Second Particle Diagnostic

- eligible_run_count: 6
- skipped_run_count: 3
- spec_count: 4
- candidate_ready_for_predeclared_shadow: False
- promotion_safe: False
- conclusion: No empirical next-second particle spec cleared strict eligible locked-run gates.

## Summary

| spec | runs | pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_bucket | market_ev_rank | market_top_bucket | strict | fallback | avg_returns | avg_spot_age_ms | avg_ann_vol | strict_all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| emp1s_610_center_blend50_p96_d48 | 6 | 113066.0000 | 0.186182 | 0.543396 | 4/6 | 3/6 | 3/6 | 3/6 | 2/6 | 3/6 | 3/6 | 2/6 | 0/6 | 864 | 548.59 | 12171.88 | 0.279696 | False |
| emp1s_233_center_blend50_p96_d48 | 6 | 88921.0000 | 0.187815 | 0.546963 | 4/6 | 3/6 | 2/6 | 3/6 | 2/6 | 3/6 | 3/6 | 2/6 | 0/6 | 826 | 220.67 | 12171.88 | 0.276424 | False |
| emp1s_987_mean25_blend25_p128_d64 | 6 | 19855.0000 | 0.193497 | 0.560375 | 3/6 | 2/6 | 2/6 | 2/6 | 1/6 | 3/6 | 3/6 | 2/6 | 0/6 | 910 | 845.67 | 12171.88 | 0.280731 | False |
| emp1s_610_mean25_blend25_p128_d64 | 6 | 1113.0000 | 0.196480 | 0.568728 | 3/6 | 2/6 | 2/6 | 2/6 | 2/6 | 3/6 | 4/6 | 4/6 | 0/6 | 864 | 548.59 | 12171.88 | 0.279696 | False |

## Runs

| run | spec | candidates | markets | selected | fallback | avg_returns | avg_spot_age_ms | avg_ann_vol | pnl_cents | brier | beats_current | ev_rank | top_bucket | market_ev_rank | market_top_bucket | strict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| particle_side_consensus_oos_CONSENSUSLOCK001 | emp1s_233_center_blend50_p96_d48 | 3260 | 6 | 2748 | 4 | 231.27 | 287.83 | 0.400180 | -22522.0000 | 0.092665 | False | -0.224753 | -9.7730 | 0.066667 | -4.2848 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | emp1s_610_center_blend50_p96_d48 | 3260 | 6 | 2747 | 4 | 575.84 | 287.83 | 0.401113 | -22526.0000 | 0.092652 | False | -0.214832 | -9.7129 | 0.200000 | -4.2848 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | emp1s_610_mean25_blend25_p128_d64 | 3260 | 6 | 2775 | 4 | 575.84 | 287.83 | 0.401113 | -15456.0000 | 0.089537 | False | -0.143764 | -10.0393 | 0.066667 | 11.7541 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | emp1s_987_mean25_blend25_p128_d64 | 3260 | 6 | 2719 | 4 | 884.01 | 287.83 | 0.399990 | -18350.0000 | 0.091194 | False | -0.193727 | -12.6184 | -0.200000 | -8.6101 | False |
| particle_residual_blend_oos_RESIDLOCK001 | emp1s_233_center_blend50_p96_d48 | 3358 | 5 | 2725 | 8 | 225.88 | 201.15 | 0.322185 | 32334.0000 | 0.228749 | True | -0.089239 | 1.1893 | -0.400000 | -6.0550 | False |
| particle_residual_blend_oos_RESIDLOCK001 | emp1s_610_center_blend50_p96_d48 | 3358 | 5 | 2818 | 18 | 558.05 | 201.15 | 0.337908 | 42117.0000 | 0.224843 | True | -0.080802 | 1.7357 | -0.600000 | -11.5118 | False |
| particle_residual_blend_oos_RESIDLOCK001 | emp1s_610_mean25_blend25_p128_d64 | 3358 | 5 | 2850 | 18 | 558.05 | 201.15 | 0.337908 | 27708.0000 | 0.222749 | True | 0.035401 | 21.3464 | 0.200000 | 42.3806 | False |
| particle_residual_blend_oos_RESIDLOCK001 | emp1s_987_mean25_blend25_p128_d64 | 3358 | 5 | 2930 | 27 | 853.61 | 201.15 | 0.343014 | 43227.0000 | 0.218834 | True | -0.011456 | 15.0000 | 0.200000 | -20.4486 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | emp1s_233_center_blend50_p96_d48 | 2514 | 4 | 2258 | 1 | 225.10 | 296.45 | 0.279592 | 47179.0000 | 0.244070 | True | 0.102805 | 23.1653 | 0.666667 | 57.1103 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | emp1s_610_center_blend50_p96_d48 | 2514 | 4 | 2246 | 1 | 545.27 | 296.45 | 0.271151 | 49223.0000 | 0.241906 | True | 0.123687 | 28.4738 | 0.333333 | 58.9576 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | emp1s_610_mean25_blend25_p128_d64 | 2514 | 4 | 2114 | 1 | 545.27 | 296.45 | 0.271151 | -7565.0000 | 0.288725 | False | -0.109312 | -16.7520 | -0.333333 | -2.8308 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | emp1s_987_mean25_blend25_p128_d64 | 2514 | 4 | 2021 | 9 | 826.90 | 296.45 | 0.267415 | -5602.0000 | 0.282739 | False | -0.092676 | -5.6439 | -0.333333 | -1.8569 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | emp1s_233_center_blend50_p96_d48 | 4843 | 7 | 4198 | 11 | 227.94 | 301.37 | 0.285174 | 56042.0000 | 0.239946 | True | 0.139521 | 21.5136 | 0.523810 | 38.5093 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | emp1s_610_center_blend50_p96_d48 | 4843 | 7 | 4240 | 21 | 575.26 | 301.37 | 0.295264 | 59019.0000 | 0.240012 | True | 0.132710 | 21.2659 | 0.333333 | 39.8263 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | emp1s_610_mean25_blend25_p128_d64 | 4843 | 7 | 4089 | 21 | 575.26 | 301.37 | 0.295264 | 32477.0000 | 0.250398 | True | -0.005919 | 4.4385 | 0.238095 | 43.2181 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | emp1s_987_mean25_blend25_p128_d64 | 4843 | 7 | 4110 | 30 | 898.52 | 301.37 | 0.303365 | 8540.0000 | 0.254863 | True | -0.024593 | 4.6069 | 0.047619 | 4.3279 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | emp1s_233_center_blend50_p96_d48 | 4405 | 6 | 4088 | 792 | 186.20 | 71621.96 | 0.166318 | -39593.0000 | 0.188877 | False | -0.107695 | -17.3829 | -0.733333 | -27.9865 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | emp1s_610_center_blend50_p96_d48 | 4405 | 6 | 4129 | 801 | 463.04 | 71621.96 | 0.166490 | -28799.0000 | 0.184556 | False | -0.104261 | -17.0045 | -0.733333 | -22.4575 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | emp1s_610_mean25_blend25_p128_d64 | 4405 | 6 | 3943 | 801 | 463.04 | 71621.96 | 0.166490 | -53461.0000 | 0.202659 | False | -0.224392 | -29.4129 | -0.466667 | -24.6386 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | emp1s_987_mean25_blend25_p128_d64 | 4405 | 6 | 3887 | 811 | 716.77 | 71621.96 | 0.166012 | -34775.0000 | 0.192240 | False | -0.237030 | -28.9791 | -0.600000 | -25.3268 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | emp1s_233_center_blend50_p96_d48 | 4512 | 7 | 4196 | 10 | 227.65 | 322.54 | 0.205096 | 15481.0000 | 0.132580 | False | -0.012674 | -3.0567 | -0.238095 | -11.3886 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | emp1s_610_center_blend50_p96_d48 | 4512 | 7 | 4165 | 19 | 574.06 | 322.54 | 0.206253 | 14032.0000 | 0.133120 | False | -0.000422 | -2.5399 | -0.333333 | -11.7547 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | emp1s_610_mean25_blend25_p128_d64 | 4512 | 7 | 3900 | 19 | 574.06 | 322.54 | 0.206253 | 17410.0000 | 0.124812 | False | 0.030430 | 9.8493 | 0.142857 | 3.2465 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | emp1s_987_mean25_blend25_p128_d64 | 4512 | 7 | 4028 | 29 | 894.23 | 322.54 | 0.204588 | 26815.0000 | 0.121111 | False | 0.057055 | 14.6108 | 0.142857 | 4.8784 | False |

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
