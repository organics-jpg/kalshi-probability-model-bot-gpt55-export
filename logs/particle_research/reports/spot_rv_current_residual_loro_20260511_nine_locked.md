# Spot RV Current Residual LORO Report

- eligible_run_count: 6
- skipped_run_count: 3
- hypothesis_id: rv233_blend50_fixed65_terminal_v1
- coefficients: -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0
- spec_count: 6
- min_bucket_clusters: 3
- candidate_ready_for_predeclared_shadow: False
- promotion_safe: False
- conclusion: No conservative RV residual correction cleared strict eligible locked holdout gates.

## Summary

| spec | holdouts | pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_bucket | market_ev_rank | market_top_bucket | strict | strict_all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| rv_disagreement | 6 | -72830.0000 | 0.195838 | 0.608069 | 2/6 | 3/6 | 1/6 | 1/6 | 1/6 | 1/6 | 2/6 | 2/6 | 1/6 | False |
| global | 6 | -72892.0000 | 0.195769 | 0.763908 | 2/6 | 3/6 | 2/6 | 1/6 | 3/6 | 2/6 | 3/6 | 3/6 | 1/6 | False |
| time_rv_disagreement | 6 | 54559.0000 | 0.189477 | 0.646072 | 3/6 | 3/6 | 2/6 | 2/6 | 2/6 | 2/6 | 3/6 | 3/6 | 0/6 | False |
| time | 6 | 38304.0000 | 0.190042 | 0.736524 | 3/6 | 3/6 | 3/6 | 2/6 | 2/6 | 3/6 | 2/6 | 3/6 | 0/6 | False |
| time_moneyness_rv_disagreement | 6 | 32711.0000 | 0.189608 | 0.647840 | 3/6 | 3/6 | 1/6 | 2/6 | 2/6 | 2/6 | 2/6 | 2/6 | 0/6 | False |
| moneyness | 6 | -85103.0000 | 0.196554 | 0.713669 | 2/6 | 3/6 | 1/6 | 1/6 | 1/6 | 2/6 | 2/6 | 2/6 | 0/6 | False |

## Holdouts

| holdout | spec | global_coef | buckets | nudged | selected | pnl_cents | brier | beats_current | ev_rank | top_bucket | market_ev_rank | market_top_bucket | strict |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| particle_side_consensus_oos_CONSENSUSLOCK001 | global | -0.50 | 1 | 1 | 2992 | 37460.0000 | 0.061117 | True | 0.463607 | 18.0528 | 0.600000 | 13.6381 | True |
| particle_side_consensus_oos_CONSENSUSLOCK001 | time | 0.50 | 4 | 4 | 2678 | 20158.0000 | 0.074371 | False | 0.155839 | 10.0061 | 0.066667 | 4.3677 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | moneyness | 0.75 | 3 | 3 | 2746 | 23204.0000 | 0.073498 | False | 0.086689 | 10.0135 | -0.466667 | 1.8087 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | rv_disagreement | 0.00 | 3 | 3 | 2963 | 37847.0000 | 0.060700 | True | 0.461165 | 18.9571 | 0.733333 | 21.9775 | True |
| particle_side_consensus_oos_CONSENSUSLOCK001 | time_rv_disagreement | 0.75 | 12 | 11 | 2657 | 22880.0000 | 0.073540 | False | 0.281016 | 11.4491 | 0.333333 | 8.7585 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | time_moneyness_rv_disagreement | 0.75 | 26 | 26 | 2563 | 21209.0000 | 0.073665 | False | 0.137073 | 9.4356 | -0.200000 | -0.1183 | False |
| particle_residual_blend_oos_RESIDLOCK001 | global | -0.50 | 1 | 1 | 2518 | -27730.0000 | 0.246145 | False | -0.005901 | -10.1405 | 0.200000 | 9.2627 | False |
| particle_residual_blend_oos_RESIDLOCK001 | time | 0.00 | 4 | 4 | 2299 | -4406.0000 | 0.236885 | True | -0.034437 | -3.7143 | 0.600000 | 1.6159 | False |
| particle_residual_blend_oos_RESIDLOCK001 | moneyness | -0.50 | 3 | 3 | 2531 | -28726.0000 | 0.244815 | False | -0.119876 | -10.6607 | 0.400000 | -13.3708 | False |
| particle_residual_blend_oos_RESIDLOCK001 | rv_disagreement | -0.25 | 3 | 3 | 2515 | -27618.0000 | 0.246173 | False | -0.007884 | -10.1798 | 0.200000 | 9.1958 | False |
| particle_residual_blend_oos_RESIDLOCK001 | time_rv_disagreement | 0.50 | 12 | 11 | 2229 | -7709.0000 | 0.237794 | True | -0.025249 | -4.4571 | 0.800000 | 1.9765 | False |
| particle_residual_blend_oos_RESIDLOCK001 | time_moneyness_rv_disagreement | 0.50 | 28 | 26 | 2203 | -5048.0000 | 0.235960 | True | -0.057376 | -1.3845 | 0.800000 | 4.1000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | global | -0.50 | 1 | 1 | 1957 | -30619.0000 | 0.287172 | False | -0.072198 | -25.9332 | -0.333333 | -28.8801 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | time | 0.00 | 4 | 4 | 1918 | 16422.0000 | 0.267632 | True | 0.059286 | 6.9062 | 0.000000 | -3.9384 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | moneyness | -0.50 | 3 | 3 | 1965 | -27687.0000 | 0.285949 | False | -0.180205 | -20.0620 | 0.000000 | -28.8801 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | rv_disagreement | -0.25 | 3 | 3 | 1958 | -30554.0000 | 0.287190 | False | -0.070608 | -25.5024 | -0.333333 | -28.8801 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | time_rv_disagreement | 0.50 | 12 | 12 | 1882 | 7609.0000 | 0.271120 | False | 0.081071 | -1.0461 | 0.000000 | -3.1352 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | time_moneyness_rv_disagreement | 0.50 | 28 | 28 | 1785 | 19680.0000 | 0.266718 | False | 0.056216 | 5.2655 | -0.333333 | -5.6319 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | global | -0.50 | 1 | 1 | 3926 | -53951.0000 | 0.282631 | False | -0.129962 | -31.6383 | -0.238095 | -7.8099 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | time | -0.50 | 4 | 4 | 3814 | -32483.0000 | 0.272433 | False | -0.094898 | -20.9909 | -0.047619 | 4.0366 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | moneyness | -0.50 | 4 | 4 | 3879 | -48292.0000 | 0.280386 | False | -0.115851 | -27.5491 | -0.333333 | -7.8099 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | rv_disagreement | -0.50 | 3 | 2 | 3891 | -47223.0000 | 0.277721 | False | -0.085989 | -21.7572 | -0.238095 | -7.6758 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | time_rv_disagreement | 0.00 | 12 | 12 | 3761 | -4543.0000 | 0.265141 | False | -0.053189 | -9.1908 | 0.047619 | 8.6356 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | time_moneyness_rv_disagreement | 0.00 | 28 | 25 | 3724 | -15236.0000 | 0.263340 | False | -0.074466 | -5.9529 | 0.142857 | 16.5784 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | global | -0.50 | 1 | 1 | 3876 | -28068.0000 | 0.172576 | False | 0.009146 | -6.8212 | -0.066667 | -9.4802 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | time | 0.50 | 4 | 4 | 3738 | -1644.0000 | 0.169739 | False | -0.134722 | -12.9773 | -0.733333 | -15.6537 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | moneyness | 0.25 | 4 | 4 | 3645 | -24316.0000 | 0.168523 | True | -0.118917 | -7.8848 | -0.466667 | -10.9870 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | rv_disagreement | 0.00 | 3 | 3 | 3897 | -28634.0000 | 0.174370 | False | -0.002395 | -6.7777 | -0.066667 | -9.5086 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | time_rv_disagreement | 0.75 | 12 | 11 | 3728 | -921.0000 | 0.168608 | True | -0.121272 | -11.4129 | -0.600000 | -15.4988 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | time_moneyness_rv_disagreement | 0.75 | 28 | 28 | 3600 | -4098.0000 | 0.165963 | True | -0.123635 | -9.2441 | -0.733333 | -14.5168 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | global | -0.50 | 1 | 1 | 4004 | 30016.0000 | 0.124975 | False | 0.269134 | 4.4991 | 0.428571 | 4.8105 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | time | 0.75 | 4 | 4 | 3738 | 40257.0000 | 0.119195 | False | -0.017692 | 9.9716 | -0.047619 | -9.9275 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | moneyness | 0.50 | 4 | 4 | 3682 | 20714.0000 | 0.126155 | False | -0.034729 | 4.8333 | 0.142857 | 7.6684 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | rv_disagreement | 0.25 | 3 | 3 | 4082 | 23352.0000 | 0.128877 | False | -0.026522 | -2.6587 | -0.047619 | -0.2123 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | time_rv_disagreement | 0.75 | 12 | 12 | 3653 | 37243.0000 | 0.120661 | False | -0.028075 | 11.0009 | -0.047619 | -10.4684 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | time_moneyness_rv_disagreement | 0.75 | 27 | 27 | 4042 | 16204.0000 | 0.132003 | False | -0.124689 | -3.3324 | -0.523810 | -8.8041 | False |

## Run Inputs

| run | rows | markets | spot_ticks | fallback_rows |
|---|---:|---:|---:|---:|
| particle_side_consensus_oos_CONSENSUSLOCK001 | 3260 | 6 | 37344 | 0 |
| particle_residual_blend_oos_RESIDLOCK001 | 3358 | 5 | 44784 | 0 |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | 2514 | 4 | 48313 | 0 |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | 4843 | 7 | 37126 | 0 |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | 4405 | 6 | 35848 | 557 |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | 4512 | 7 | 33754 | 0 |

## Skipped Runs

- `logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED`
- `logs\particle_research\real_shadow\particle_dynamic_oos_20260511TLOCKEDNEXT`
- `logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2`
