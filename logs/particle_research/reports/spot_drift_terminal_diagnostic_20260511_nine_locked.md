# Spot Drift Terminal Diagnostic

- eligible_run_count: 6
- skipped_run_count: 3
- spec_count: 5
- candidate_ready_for_predeclared_shadow: False
- promotion_safe: False
- conclusion: No next-second spot-drift terminal diagnostic cleared strict eligible locked-run gates.

## Summary

| spec | runs | pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_bucket | market_ev_rank | market_top_bucket | strict | strict_all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| drift13_cap10_fixed65_blend25 | 6 | 99481.0000 | 0.195488 | 0.568108 | 4/6 | 1/6 | 3/6 | 3/6 | 4/6 | 3/6 | 2/6 | 2/6 | 1/6 | False |
| drift5_cap10_rv89_blend50 | 6 | 42977.0000 | 0.194224 | 0.562231 | 3/6 | 3/6 | 1/6 | 3/6 | 3/6 | 4/6 | 2/6 | 3/6 | 0/6 | False |
| drift13_cap15_rv233_blend50 | 6 | 18875.0000 | 0.202668 | 0.581481 | 2/6 | 1/6 | 1/6 | 2/6 | 3/6 | 4/6 | 2/6 | 3/6 | 0/6 | False |
| drift21_cap20_rv377_blend50 | 6 | 8820.0000 | 0.206330 | 0.589919 | 2/6 | 0/6 | 1/6 | 2/6 | 3/6 | 4/6 | 2/6 | 2/6 | 0/6 | False |
| drift34_cap20_rv610_blend50 | 6 | -3593.0000 | 0.203356 | 0.583581 | 2/6 | 1/6 | 1/6 | 2/6 | 3/6 | 3/6 | 2/6 | 1/6 | 0/6 | False |

## Side Summary

| spec | side | runs | selected | win_rate | pnl_cents | avg_pnl_selected | positive_pnl_runs |
|---|---|---:|---:|---:|---:|---:|---:|
| drift13_cap10_fixed65_blend25 | no | 6 | 11082 | 0.326385 | 69424.0000 | 6.2646 | 3/6 |
| drift13_cap10_fixed65_blend25 | yes | 6 | 10115 | 0.287889 | 30057.0000 | 2.9715 | 3/6 |
| drift13_cap15_rv233_blend50 | no | 6 | 11725 | 0.363667 | 30971.0000 | 2.6414 | 3/6 |
| drift13_cap15_rv233_blend50 | yes | 6 | 9953 | 0.307144 | -12096.0000 | -1.2153 | 2/6 |
| drift21_cap20_rv377_blend50 | no | 6 | 11587 | 0.361440 | 24144.0000 | 2.0837 | 3/6 |
| drift21_cap20_rv377_blend50 | yes | 6 | 10092 | 0.312128 | -15324.0000 | -1.5184 | 2/6 |
| drift34_cap20_rv610_blend50 | no | 6 | 11487 | 0.356664 | 16027.0000 | 1.3952 | 3/6 |
| drift34_cap20_rv610_blend50 | yes | 6 | 10212 | 0.314826 | -19620.0000 | -1.9213 | 2/6 |
| drift5_cap10_rv89_blend50 | no | 6 | 11758 | 0.358394 | 42037.0000 | 3.5752 | 3/6 |
| drift5_cap10_rv89_blend50 | yes | 6 | 9419 | 0.292706 | 940.0000 | 0.0998 | 3/6 |

## Runs

| run | spec | candidates | markets | selected | drift_fallback | vol_fallback | avg_drift_bps | avg_vol | pnl_cents | brier | beats_current | ev_rank | top_bucket | market_ev_rank | market_top_bucket | strict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift5_cap10_rv89_blend50 | 3260 | 6 | 2918 | 5 | 0 | 0.0121 | 0.285445 | -9971.0000 | 0.096866 | False | -0.171854 | -5.8172 | -0.466667 | -5.3752 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap15_rv233_blend50 | 3260 | 6 | 3058 | 2 | 0 | 0.0694 | 0.282593 | -8724.0000 | 0.110119 | False | -0.174624 | -14.3914 | -0.600000 | -3.9831 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift21_cap20_rv377_blend50 | 3260 | 6 | 3061 | 2 | 0 | 0.2091 | 0.282341 | -9849.0000 | 0.119985 | False | -0.162078 | -17.5325 | -0.466667 | -5.0922 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift34_cap20_rv610_blend50 | 3260 | 6 | 3034 | 2 | 0 | 0.4417 | 0.279742 | -9784.0000 | 0.118188 | False | -0.171396 | -18.6577 | -0.200000 | -5.9025 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | drift13_cap10_fixed65_blend25 | 3260 | 6 | 2901 | 2 | 0 | 0.0200 | 0.650000 | -18043.0000 | 0.114353 | False | -0.225165 | -12.8037 | -0.333333 | -7.9897 | False |
| particle_residual_blend_oos_RESIDLOCK001 | drift5_cap10_rv89_blend50 | 3358 | 5 | 3119 | 0 | 0 | 0.5967 | 0.229863 | -4309.0000 | 0.234845 | True | 0.093924 | 23.6690 | 0.400000 | 6.5042 | False |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap15_rv233_blend50 | 3358 | 5 | 3235 | 0 | 0 | 1.3297 | 0.229649 | -5107.0000 | 0.237493 | False | 0.168475 | 29.6119 | 0.800000 | 0.1988 | False |
| particle_residual_blend_oos_RESIDLOCK001 | drift21_cap20_rv377_blend50 | 3358 | 5 | 3244 | 0 | 0 | 1.5819 | 0.233077 | -9535.0000 | 0.243879 | False | 0.170054 | 28.3440 | 0.400000 | 0.6343 | False |
| particle_residual_blend_oos_RESIDLOCK001 | drift34_cap20_rv610_blend50 | 3358 | 5 | 3247 | 0 | 0 | 1.8202 | 0.235853 | -11807.0000 | 0.244729 | False | 0.156957 | 23.4429 | 0.000000 | -12.9395 | False |
| particle_residual_blend_oos_RESIDLOCK001 | drift13_cap10_fixed65_blend25 | 3358 | 5 | 3021 | 0 | 0 | 0.9641 | 0.650000 | 28250.0000 | 0.220646 | True | 0.088213 | 16.5488 | -0.400000 | -11.2466 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift5_cap10_rv89_blend50 | 2514 | 4 | 2322 | 1 | 0 | 0.9204 | 0.217057 | 31371.0000 | 0.240525 | True | 0.096749 | 30.4754 | 0.666667 | 39.4036 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap15_rv233_blend50 | 2514 | 4 | 2354 | 1 | 0 | 1.7694 | 0.212884 | 27929.0000 | 0.237071 | True | 0.141757 | 36.0461 | 1.000000 | 35.5685 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift21_cap20_rv377_blend50 | 2514 | 4 | 2382 | 1 | 0 | 2.3597 | 0.209253 | 28503.0000 | 0.238302 | True | 0.135046 | 34.7234 | 0.333333 | -1.0925 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift34_cap20_rv610_blend50 | 2514 | 4 | 2415 | 1 | 0 | 2.9228 | 0.203004 | 29278.0000 | 0.234806 | True | 0.151879 | 33.1304 | 0.333333 | -0.5616 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | drift13_cap10_fixed65_blend25 | 2514 | 4 | 2393 | 1 | 0 | 1.2315 | 0.650000 | 53121.0000 | 0.224281 | True | 0.097112 | 32.0477 | 0.666667 | 61.5721 | True |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift5_cap10_rv89_blend50 | 4843 | 7 | 4483 | 0 | 0 | 0.1413 | 0.238670 | 42284.0000 | 0.256923 | True | 0.007867 | 8.8175 | -0.047619 | 17.4402 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap15_rv233_blend50 | 4843 | 7 | 4597 | 0 | 0 | 0.0286 | 0.243359 | 41368.0000 | 0.260571 | True | 0.024280 | 9.0066 | -0.238095 | 18.5574 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift21_cap20_rv377_blend50 | 4843 | 7 | 4579 | 0 | 0 | -0.0227 | 0.245632 | 41161.0000 | 0.259037 | True | 0.040458 | 10.7614 | -0.047619 | 19.3527 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift34_cap20_rv610_blend50 | 4843 | 7 | 4556 | 0 | 0 | -0.2064 | 0.246210 | 37276.0000 | 0.257255 | True | 0.036817 | 9.7539 | 0.238095 | 22.5823 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | drift13_cap10_fixed65_blend25 | 4843 | 7 | 4422 | 0 | 0 | 0.0211 | 0.650000 | 48504.0000 | 0.244515 | True | 0.084965 | 17.6301 | 0.047619 | 15.8441 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift5_cap10_rv89_blend50 | 4405 | 6 | 4078 | 778 | 696 | 0.0462 | 0.272972 | -24211.0000 | 0.190900 | False | -0.099692 | -7.3439 | -0.466667 | -18.4194 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap15_rv233_blend50 | 4405 | 6 | 4162 | 777 | 557 | -0.0468 | 0.256983 | -33550.0000 | 0.205349 | False | -0.046683 | -5.9864 | -0.466667 | -17.8635 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift21_cap20_rv377_blend50 | 4405 | 6 | 4178 | 777 | 417 | 0.3616 | 0.242599 | -34242.0000 | 0.206733 | False | -0.034966 | -7.1407 | -0.733333 | -17.1626 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift34_cap20_rv610_blend50 | 4405 | 6 | 4206 | 777 | 192 | 0.5184 | 0.219614 | -37562.0000 | 0.199668 | False | -0.001598 | -3.5381 | -0.733333 | -17.0728 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | drift13_cap10_fixed65_blend25 | 4405 | 6 | 4162 | 777 | 557 | -0.1067 | 0.650000 | -14898.0000 | 0.198345 | False | -0.001144 | -9.6606 | -1.000000 | -22.0047 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift5_cap10_rv89_blend50 | 4512 | 7 | 4257 | 3 | 0 | -0.9003 | 0.202792 | 7813.0000 | 0.145286 | False | -0.024667 | 7.3236 | -0.428571 | -11.5449 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap15_rv233_blend50 | 4512 | 7 | 4272 | 0 | 0 | -0.9703 | 0.200513 | -3041.0000 | 0.165406 | False | -0.029568 | 2.6410 | -0.619048 | -11.2747 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift21_cap20_rv377_blend50 | 4512 | 7 | 4235 | 0 | 0 | -1.0755 | 0.200010 | -7218.0000 | 0.170043 | False | -0.053427 | 0.2748 | -0.809524 | -11.0405 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift34_cap20_rv610_blend50 | 4512 | 7 | 4241 | 0 | 0 | -1.2286 | 0.200000 | -10994.0000 | 0.165491 | False | -0.044817 | -0.4362 | -0.809524 | -10.9146 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | drift13_cap10_fixed65_blend25 | 4512 | 7 | 4298 | 0 | 0 | -0.7532 | 0.650000 | 2547.0000 | 0.170788 | False | 0.004909 | -4.2394 | -0.238095 | -12.7107 | False |

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
