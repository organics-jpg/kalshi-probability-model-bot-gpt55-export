# Spot Realized-Vol Terminal Diagnostic

- eligible_run_count: 6
- skipped_run_count: 3
- spec_count: 7
- promotion_safe: False
- conclusion: No timestamp-available realized-vol terminal variant clears strict eligible-run gates.

## Summary

| spec | runs | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | fallback_rows | mean_vol | strict_all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| rv233_floor20_cap150 | 6 | -65831.0000 | 0.196152 | 0.571880 | 3/6 | 3/6 | 2/6 | 2/6 | 3/6 | 3/6 | 1/6 | 557 | 0.2377 | False |
| rv610_floor20_cap200 | 6 | -77867.0000 | 0.198624 | 0.577275 | 3/6 | 3/6 | 2/6 | 3/6 | 3/6 | 3/6 | 1/6 | 192 | 0.2307 | False |
| rv89_floor20_cap150 | 6 | -93671.0000 | 0.199224 | 0.588950 | 2/6 | 3/6 | 2/6 | 1/6 | 3/6 | 2/6 | 1/6 | 696 | 0.2411 | False |
| rv34_floor20_cap150 | 6 | -109176.0000 | 0.200595 | 0.593978 | 2/6 | 3/6 | 2/6 | 1/6 | 2/6 | 2/6 | 1/6 | 750 | 0.2428 | False |
| rv233_blend50_fixed65 | 6 | 94618.0000 | 0.187150 | 0.543725 | 3/6 | 3/6 | 2/6 | 3/6 | 1/6 | 2/6 | 0/6 | 557 | 0.2377 | False |
| rv610_blend50_fixed65 | 6 | 75507.0000 | 0.188448 | 0.547171 | 3/6 | 3/6 | 2/6 | 3/6 | 1/6 | 2/6 | 0/6 | 192 | 0.2307 | False |
| rv89_blend50_fixed65 | 6 | 74191.0000 | 0.188695 | 0.548146 | 3/6 | 3/6 | 2/6 | 3/6 | 2/6 | 2/6 | 0/6 | 696 | 0.2411 | False |

## Run Rows

| run | spec | candidates | markets | selected | pnl_cents | brier | log_loss | beats_brownian | beats_market | beats_current | ev_rank | top_bucket_pnl | fallback_rows | mean_vol | strict |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---:|---:|---|
| particle_side_consensus_oos_CONSENSUSLOCK001 | rv34_floor20_cap150 | 3260 | 6 | 2494 | 27970.0000 | 0.067395 | 0.231311 | True | True | False | 0.420517 | 18.3276 | 0 | 0.2832 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | rv89_floor20_cap150 | 3260 | 6 | 2527 | 28247.0000 | 0.068400 | 0.234216 | True | True | False | 0.440561 | 18.8258 | 0 | 0.2854 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | rv233_floor20_cap150 | 3260 | 6 | 2561 | 32292.0000 | 0.067049 | 0.230738 | True | True | False | 0.454268 | 19.6061 | 0 | 0.2826 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | rv610_floor20_cap200 | 3260 | 6 | 2608 | 33683.0000 | 0.067151 | 0.229777 | True | True | False | 0.425888 | 17.5951 | 0 | 0.2797 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | rv89_blend50_fixed65 | 3260 | 6 | 2534 | -2512.0000 | 0.083450 | 0.296604 | True | False | False | -0.250575 | -5.6405 | 0 | 0.2854 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | rv233_blend50_fixed65 | 3260 | 6 | 2539 | -1758.0000 | 0.082646 | 0.294708 | True | False | False | -0.227271 | -4.3951 | 0 | 0.2826 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | rv610_blend50_fixed65 | 3260 | 6 | 2409 | -2511.0000 | 0.082697 | 0.294269 | True | False | False | -0.237659 | -3.8331 | 0 | 0.2797 | False |
| particle_residual_blend_oos_RESIDLOCK001 | rv34_floor20_cap150 | 3358 | 5 | 2828 | -70646.0000 | 0.274584 | 0.731916 | False | False | False | -0.139489 | -34.9262 | 0 | 0.2312 | False |
| particle_residual_blend_oos_RESIDLOCK001 | rv89_floor20_cap150 | 3358 | 5 | 2827 | -70758.0000 | 0.274003 | 0.730790 | False | False | False | -0.133366 | -33.0083 | 0 | 0.2299 | False |
| particle_residual_blend_oos_RESIDLOCK001 | rv233_floor20_cap150 | 3358 | 5 | 2845 | -67994.0000 | 0.271139 | 0.722708 | False | False | False | -0.112935 | -34.7012 | 0 | 0.2296 | False |
| particle_residual_blend_oos_RESIDLOCK001 | rv610_floor20_cap200 | 3358 | 5 | 2740 | -70318.0000 | 0.270879 | 0.723886 | False | False | False | -0.189557 | -44.2643 | 0 | 0.2359 | False |
| particle_residual_blend_oos_RESIDLOCK001 | rv89_blend50_fixed65 | 3358 | 5 | 2243 | -7472.0000 | 0.239017 | 0.649703 | False | False | True | -0.208176 | -4.6774 | 0 | 0.2299 | False |
| particle_residual_blend_oos_RESIDLOCK001 | rv233_blend50_fixed65 | 3358 | 5 | 2267 | -2268.0000 | 0.237660 | 0.646543 | False | False | True | -0.195527 | -3.6000 | 0 | 0.2296 | False |
| particle_residual_blend_oos_RESIDLOCK001 | rv610_blend50_fixed65 | 3358 | 5 | 2455 | -1621.0000 | 0.238302 | 0.648831 | False | False | True | -0.172018 | -5.1619 | 0 | 0.2359 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | rv34_floor20_cap150 | 2514 | 4 | 2040 | -46951.0000 | 0.297333 | 0.840832 | False | False | False | -0.066722 | -27.8283 | 0 | 0.2216 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | rv89_floor20_cap150 | 2514 | 4 | 2101 | -46491.0000 | 0.296365 | 0.851588 | False | False | False | -0.039091 | -27.0032 | 0 | 0.2171 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | rv233_floor20_cap150 | 2514 | 4 | 2048 | -49497.0000 | 0.296510 | 0.858006 | False | False | False | -0.009308 | -27.9730 | 0 | 0.2129 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | rv610_floor20_cap200 | 2514 | 4 | 2148 | -57394.0000 | 0.307494 | 0.891675 | False | False | False | -0.091229 | -41.7854 | 0 | 0.2030 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | rv89_blend50_fixed65 | 2514 | 4 | 2101 | 35571.0000 | 0.254093 | 0.690760 | False | True | True | 0.013332 | 25.9762 | 0 | 0.2171 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | rv233_blend50_fixed65 | 2514 | 4 | 2069 | 37430.0000 | 0.253952 | 0.690830 | False | True | True | -0.002683 | 21.8506 | 0 | 0.2129 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | rv610_blend50_fixed65 | 2514 | 4 | 2009 | 27870.0000 | 0.258766 | 0.702469 | False | True | True | -0.035882 | 18.8108 | 0 | 0.2030 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | rv34_floor20_cap150 | 4843 | 7 | 4083 | -24323.0000 | 0.269575 | 0.884092 | False | False | False | -0.018566 | -15.5021 | 0 | 0.2362 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | rv89_floor20_cap150 | 4843 | 7 | 4119 | -9676.0000 | 0.262471 | 0.843928 | False | False | False | 0.017690 | -8.5400 | 0 | 0.2387 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | rv233_floor20_cap150 | 4843 | 7 | 4021 | 8983.0000 | 0.250492 | 0.752369 | False | False | True | 0.147141 | 15.1049 | 0 | 0.2434 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | rv610_floor20_cap200 | 4843 | 7 | 3919 | 2457.0000 | 0.259646 | 0.761453 | False | False | True | 0.058172 | 1.7523 | 0 | 0.2462 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | rv89_blend50_fixed65 | 4843 | 7 | 3997 | 44613.0000 | 0.244100 | 0.692817 | False | True | True | 0.082886 | 16.8167 | 0 | 0.2387 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | rv233_blend50_fixed65 | 4843 | 7 | 4045 | 53582.0000 | 0.238555 | 0.674379 | False | True | True | 0.121767 | 26.5871 | 0 | 0.2434 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | rv610_blend50_fixed65 | 4843 | 7 | 4049 | 43366.0000 | 0.243538 | 0.687065 | False | True | True | 0.107702 | 21.2841 | 0 | 0.2462 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | rv34_floor20_cap150 | 4405 | 6 | 3541 | -35373.0000 | 0.176888 | 0.508707 | True | False | False | -0.062638 | -11.3076 | 750 | 0.2806 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | rv89_floor20_cap150 | 4405 | 6 | 3489 | -35585.0000 | 0.176327 | 0.506713 | True | False | False | -0.050173 | -10.3385 | 696 | 0.2730 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | rv233_floor20_cap150 | 4405 | 6 | 3451 | -32768.0000 | 0.174976 | 0.503768 | True | False | False | -0.050741 | -8.6062 | 557 | 0.2570 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | rv610_floor20_cap200 | 4405 | 6 | 3420 | -29908.0000 | 0.169951 | 0.493459 | True | False | True | -0.039811 | -6.4419 | 192 | 0.2196 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | rv89_blend50_fixed65 | 4405 | 6 | 4007 | -11253.0000 | 0.177587 | 0.527128 | True | False | False | -0.125293 | -15.0445 | 696 | 0.2730 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | rv233_blend50_fixed65 | 4405 | 6 | 3989 | -9896.0000 | 0.176837 | 0.525552 | True | False | False | -0.128930 | -13.7613 | 557 | 0.2570 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | rv610_blend50_fixed65 | 4405 | 6 | 3993 | -9006.0000 | 0.174213 | 0.520233 | True | False | False | -0.118115 | -13.0100 | 192 | 0.2196 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | rv34_floor20_cap150 | 4512 | 7 | 3402 | 40147.0000 | 0.117798 | 0.367007 | True | True | True | 0.107383 | 15.6738 | 0 | 0.2041 | True |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | rv89_floor20_cap150 | 4512 | 7 | 3380 | 40592.0000 | 0.117780 | 0.366462 | True | True | True | 0.115294 | 15.6888 | 0 | 0.2028 | True |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | rv233_floor20_cap150 | 4512 | 7 | 3416 | 43153.0000 | 0.116743 | 0.363689 | True | True | True | 0.129675 | 16.8209 | 0 | 0.2005 | True |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | rv610_floor20_cap200 | 4512 | 7 | 3427 | 43613.0000 | 0.116625 | 0.363398 | True | True | True | 0.131210 | 16.9043 | 0 | 0.2000 | True |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | rv89_blend50_fixed65 | 4512 | 7 | 4118 | 15244.0000 | 0.133922 | 0.431862 | True | False | False | -0.017585 | -3.4255 | 0 | 0.2028 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | rv233_blend50_fixed65 | 4512 | 7 | 4108 | 17528.0000 | 0.133252 | 0.430335 | True | False | False | -0.029959 | -3.3564 | 0 | 0.2005 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | rv610_blend50_fixed65 | 4512 | 7 | 4109 | 17409.0000 | 0.133172 | 0.430162 | True | False | False | -0.028658 | -3.3564 | 0 | 0.2000 | False |

## Run Inputs

| run | rows | markets | spot_ticks | candidate_path | label_path | spot_tick_path |
|---|---:|---:|---:|---|---|---|
| particle_side_consensus_oos_CONSENSUSLOCK001 | 3260 | 6 | 37344 | `logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\pipeline_work\label_contexts_full_refresh.ndjson` | `logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\independent_spot_ticks.ndjson` |
| particle_residual_blend_oos_RESIDLOCK001 | 3358 | 5 | 44784 | `logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\pipeline_work\label_contexts_full_refresh.ndjson` | `logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\independent_spot_ticks.ndjson` |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | 2514 | 4 | 48313 | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK001\pipeline_work\label_contexts_full_refresh.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK001\independent_spot_ticks.ndjson` |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | 4843 | 7 | 37126 | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\pipeline_work\label_contexts_full_refresh.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\independent_spot_ticks.ndjson` |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | 4405 | 6 | 35848 | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK003\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK003\pipeline_work\label_contexts_full_refresh.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK003\independent_spot_ticks.ndjson` |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | 4512 | 7 | 33754 | `logs\particle_research\real_shadow\particle_spot_rv_terminal_oos_RVTERMLOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_spot_rv_terminal_oos_RVTERMLOCK001\pipeline_work\label_contexts_full_refresh.ndjson` | `logs\particle_research\real_shadow\particle_spot_rv_terminal_oos_RVTERMLOCK001\independent_spot_ticks.ndjson` |
