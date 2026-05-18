# Spot Realized-Vol Terminal Diagnostic

- eligible_run_count: 4
- skipped_run_count: 3
- spec_count: 7
- promotion_safe: False
- conclusion: No timestamp-available realized-vol terminal variant clears strict eligible-run gates.

## Summary

| spec | runs | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | fallback_rows | mean_vol | strict_all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| rv233_blend50_fixed65 | 4 | 86986.0000 | 0.203203 | 0.576615 | 2/4 | 1/4 | 2/4 | 3/4 | 1/4 | 2/4 | 0/4 | 0 | 0.2421 | False |
| rv89_blend50_fixed65 | 4 | 70200.0000 | 0.205165 | 0.582471 | 2/4 | 1/4 | 2/4 | 3/4 | 2/4 | 2/4 | 0/4 | 0 | 0.2428 | False |
| rv610_blend50_fixed65 | 4 | 67104.0000 | 0.205826 | 0.583159 | 2/4 | 1/4 | 2/4 | 3/4 | 1/4 | 2/4 | 0/4 | 0 | 0.2412 | False |
| rv233_floor20_cap150 | 4 | -76216.0000 | 0.221298 | 0.640955 | 2/4 | 1/4 | 1/4 | 1/4 | 2/4 | 2/4 | 0/4 | 0 | 0.2421 | False |
| rv89_floor20_cap150 | 4 | -98678.0000 | 0.225310 | 0.665130 | 1/4 | 1/4 | 1/4 | 0/4 | 2/4 | 1/4 | 0/4 | 0 | 0.2428 | False |
| rv610_floor20_cap200 | 4 | -91572.0000 | 0.226292 | 0.651698 | 2/4 | 1/4 | 1/4 | 1/4 | 2/4 | 2/4 | 0/4 | 0 | 0.2412 | False |
| rv34_floor20_cap150 | 4 | -113950.0000 | 0.227222 | 0.672038 | 1/4 | 1/4 | 1/4 | 0/4 | 1/4 | 1/4 | 0/4 | 0 | 0.2431 | False |

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

## Run Inputs

| run | rows | markets | spot_ticks | candidate_path | label_path | spot_tick_path |
|---|---:|---:|---:|---|---|---|
| particle_side_consensus_oos_CONSENSUSLOCK001 | 3260 | 6 | 37344 | `logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\pipeline_work\label_contexts_full_refresh.ndjson` | `logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\independent_spot_ticks.ndjson` |
| particle_residual_blend_oos_RESIDLOCK001 | 3358 | 5 | 44784 | `logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\pipeline_work\label_contexts_full_refresh.ndjson` | `logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\independent_spot_ticks.ndjson` |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | 2514 | 4 | 48313 | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK001\pipeline_work\label_contexts_full_refresh.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK001\independent_spot_ticks.ndjson` |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | 4843 | 7 | 37126 | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\pipeline_work\label_contexts_full_refresh.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\independent_spot_ticks.ndjson` |
