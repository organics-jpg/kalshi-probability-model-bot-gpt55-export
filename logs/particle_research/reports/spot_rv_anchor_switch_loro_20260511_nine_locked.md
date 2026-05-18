# Spot RV Anchor Switch LORO Report

- eligible_run_count: 6
- skipped_run_count: 3
- anchors: brownian, market, current_calibrated, particle, rv_terminal
- hypothesis_id: rv233_blend50_fixed65_terminal_v1
- spec_count: 6
- min_bucket_clusters: 3
- holdout_row_count: 36
- candidate_ready_for_predeclared_shadow: False
- promotion_safe: False
- conclusion: No realized-vol-aware anchor switch cleared strict eligible locked holdout gates.

## Summary

| spec | holdouts | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | positive_market_ev_rank | positive_market_top_bucket | strict_gates | strict_all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| time_rv_disagreement | 6 | 102481.0000 | 0.179108 | 0.520896 | 5/6 | 3/6 | 3/6 | 5/6 | 4/6 | 5/6 | 3/6 | 4/6 | 1/6 | False |
| time_moneyness_rv_disagreement | 6 | 101308.0000 | 0.180533 | 0.527600 | 5/6 | 3/6 | 4/6 | 4/6 | 3/6 | 5/6 | 3/6 | 4/6 | 0/6 | False |
| time_moneyness | 6 | 78333.0000 | 0.181487 | 0.533153 | 5/6 | 3/6 | 2/6 | 4/6 | 2/6 | 5/6 | 2/6 | 4/6 | 0/6 | False |
| time | 6 | 55611.0000 | 0.181872 | 0.534228 | 4/6 | 3/6 | 3/6 | 4/6 | 2/6 | 4/6 | 2/6 | 4/6 | 0/6 | False |
| moneyness | 6 | -26765.0000 | 0.189755 | 0.551435 | 1/6 | 3/6 | 0/6 | 4/6 | 0/6 | 1/6 | 0/6 | 0/6 | 0/6 | False |
| global | 6 | -30603.0000 | 0.189718 | 0.547217 | 0/6 | 3/6 | 0/6 | 3/6 | 0/6 | 0/6 | 0/6 | 0/6 | 0/6 | False |

## Holdouts

| holdout | spec | global_anchor | buckets | selected | pnl_cents | brier | beats_brownian | beats_market | beats_current | ev_rank | top_bucket | market_ev_rank | top_market_bucket | strict |
|---|---|---|---:|---:|---:|---:|---|---|---|---:|---:|---:|---:|---|
| particle_side_consensus_oos_CONSENSUSLOCK001 | global | market | 1 | 202 | 0.0000 | 0.080857 | True | False | False | 0.000000 | 0.0000 | 0.000000 | 0.0000 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | time | market | 4 | 1338 | -11786.0000 | 0.090507 | True | False | False | -0.438463 | -13.0319 | -0.200000 | -17.5755 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | moneyness | market | 3 | 899 | -2347.0000 | 0.082077 | True | False | False | -0.711793 | -2.8233 | -0.333333 | -1.1891 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | time_moneyness | market | 12 | 2102 | -7069.0000 | 0.090877 | True | False | False | -0.304742 | -7.2626 | -0.466667 | -17.7390 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | time_rv_disagreement | market | 12 | 2423 | 2708.0000 | 0.084557 | True | False | False | 0.067421 | -1.2663 | -0.200000 | -16.7490 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | time_moneyness_rv_disagreement | market | 26 | 1850 | -944.0000 | 0.088144 | True | False | False | -0.170193 | -7.2454 | -0.333333 | -17.1027 | False |
| particle_residual_blend_oos_RESIDLOCK001 | global | market | 1 | 96 | 0.0000 | 0.233343 | False | False | True | 0.000000 | 0.0000 | 0.000000 | 0.0000 | False |
| particle_residual_blend_oos_RESIDLOCK001 | time | market | 4 | 2062 | 31921.0000 | 0.219638 | False | True | True | 0.238337 | 27.9595 | 0.600000 | 37.1066 | False |
| particle_residual_blend_oos_RESIDLOCK001 | moneyness | market | 3 | 388 | -908.0000 | 0.233685 | False | False | True | -0.868411 | -1.0810 | -0.777778 | -0.3984 | False |
| particle_residual_blend_oos_RESIDLOCK001 | time_moneyness | market | 12 | 1941 | 24719.0000 | 0.220895 | False | True | True | 0.048732 | 28.5774 | -0.200000 | 13.8444 | False |
| particle_residual_blend_oos_RESIDLOCK001 | time_rv_disagreement | market | 12 | 2342 | 21716.0000 | 0.222756 | False | True | True | 0.126378 | 26.0952 | 0.600000 | 28.2363 | False |
| particle_residual_blend_oos_RESIDLOCK001 | time_moneyness_rv_disagreement | market | 28 | 2338 | 16654.0000 | 0.224549 | False | True | True | 0.073991 | 22.9679 | 0.200000 | 21.2882 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | global | market | 1 | 108 | 0.0000 | 0.268521 | False | False | True | 0.000000 | 0.0000 | 0.000000 | 0.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | time | market | 4 | 1066 | 24264.0000 | 0.246712 | False | True | True | 0.290913 | 36.7774 | 1.000000 | 46.9760 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | moneyness | market | 3 | 491 | 1152.0000 | 0.268739 | False | False | True | -0.765488 | 1.8315 | -0.666667 | -1.8005 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | time_moneyness | market | 12 | 1454 | 24591.0000 | 0.248575 | False | True | True | 0.040533 | 39.2925 | 1.000000 | 45.6473 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | time_rv_disagreement | market | 12 | 1803 | 33265.0000 | 0.244256 | False | True | True | 0.206749 | 41.1542 | 1.000000 | 47.9144 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | time_moneyness_rv_disagreement | market | 28 | 1493 | 26660.0000 | 0.248025 | False | True | True | 0.191650 | 39.3370 | 0.666667 | 45.5685 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | global | market | 1 | 103 | 0.0000 | 0.256284 | False | False | True | 0.000000 | 0.0000 | 0.000000 | 0.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | time | market | 4 | 2885 | -19652.0000 | 0.258283 | False | False | True | -0.014718 | 8.3138 | -0.047619 | 3.6136 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | moneyness | market | 4 | 170 | -6115.0000 | 0.257541 | False | False | True | -0.993572 | -5.0495 | -1.000000 | -3.7515 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | time_moneyness | market | 12 | 2403 | 2978.0000 | 0.254970 | False | False | True | -0.070255 | 6.2436 | 0.047619 | 3.7743 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | time_rv_disagreement | market | 12 | 3407 | -11934.0000 | 0.257964 | False | False | True | -0.015999 | 9.2461 | 0.142857 | 17.0228 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | time_moneyness_rv_disagreement | market | 28 | 2423 | 8653.0000 | 0.253785 | False | True | True | -0.061892 | 9.2626 | 0.142857 | 7.1482 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | global | current_calibrated | 1 | 3519 | -30603.0000 | 0.171393 | True | False | False | -0.061112 | -9.5318 | -0.333333 | -12.3016 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | time | current_calibrated | 4 | 3401 | 8815.0000 | 0.154428 | True | False | True | -0.066113 | -0.5336 | -0.333333 | -14.9596 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | moneyness | market | 4 | 2233 | -17858.0000 | 0.168101 | True | False | True | -0.263087 | -9.7123 | -0.333333 | -16.3379 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | time_moneyness | market | 12 | 2467 | 20957.0000 | 0.144225 | True | False | True | -0.072133 | 4.1407 | -0.066667 | -1.6721 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | time_rv_disagreement | market | 12 | 3298 | 12333.0000 | 0.153228 | True | False | True | -0.022595 | 1.3403 | -0.600000 | -15.1889 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | time_moneyness_rv_disagreement | market | 28 | 2516 | 19948.0000 | 0.145369 | True | False | True | -0.078888 | 4.0799 | -0.066667 | -2.6917 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | global | market | 1 | 96 | 0.0000 | 0.127912 | True | False | False | 0.000000 | 0.0000 | 0.000000 | 0.0000 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | time | market | 4 | 2237 | 22049.0000 | 0.121667 | True | True | False | -0.136097 | 13.4441 | -0.238095 | 5.5083 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | moneyness | market | 4 | 314 | -689.0000 | 0.128389 | True | False | False | -0.976744 | -0.6108 | -0.333333 | -0.3901 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | time_moneyness | market | 12 | 1972 | 12157.0000 | 0.129379 | True | False | False | -0.259612 | 3.0009 | -0.047619 | 2.5884 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | time_rv_disagreement | market | 12 | 2916 | 44393.0000 | 0.111887 | True | True | True | 0.259420 | 20.1498 | -0.047619 | 2.1709 | True |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | time_moneyness_rv_disagreement | market | 27 | 2381 | 30337.0000 | 0.123324 | True | True | False | 0.004354 | 8.7340 | -0.142857 | 5.5410 | False |

## Run Inputs

| run | rows | markets | spot_ticks | rv_fallback_rows | candidate_path | label_path | spot_tick_path |
|---|---:|---:|---:|---:|---|---|---|
| particle_side_consensus_oos_CONSENSUSLOCK001 | 3260 | 6 | 37344 | 0 | `logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\pipeline_work\label_contexts_full_refresh.ndjson` | `logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\independent_spot_ticks.ndjson` |
| particle_residual_blend_oos_RESIDLOCK001 | 3358 | 5 | 44784 | 0 | `logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\pipeline_work\label_contexts_full_refresh.ndjson` | `logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\independent_spot_ticks.ndjson` |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | 2514 | 4 | 48313 | 0 | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK001\pipeline_work\label_contexts_full_refresh.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK001\independent_spot_ticks.ndjson` |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | 4843 | 7 | 37126 | 0 | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\pipeline_work\label_contexts_full_refresh.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\independent_spot_ticks.ndjson` |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | 4405 | 6 | 35848 | 557 | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK003\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK003\pipeline_work\label_contexts_full_refresh.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK003\independent_spot_ticks.ndjson` |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | 4512 | 7 | 33754 | 0 | `logs\particle_research\real_shadow\particle_spot_rv_terminal_oos_RVTERMLOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_spot_rv_terminal_oos_RVTERMLOCK001\pipeline_work\label_contexts_full_refresh.ndjson` | `logs\particle_research\real_shadow\particle_spot_rv_terminal_oos_RVTERMLOCK001\independent_spot_ticks.ndjson` |

## Skipped Runs

- `logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED`
- `logs\particle_research\real_shadow\particle_dynamic_oos_20260511TLOCKEDNEXT`
- `logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2`
