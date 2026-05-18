# Anchor Switch LORO Report

- run_count: 8
- spec_count: 6
- min_bucket_clusters: 3
- holdout_row_count: 48
- promotion_safe: False
- conclusion: No state-bucket anchor switch passed strict locked holdout gates.

## Summary

| spec | holdouts | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | strict_all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| time_moneyness | 8 | 88987.0000 | 0.192550 | 0.559834 | 7/8 | 5/8 | 3/8 | 4/8 | 3/8 | 5/8 | 0/8 | False |
| time_spread_disagreement | 8 | 19204.0000 | 0.191336 | 0.552432 | 6/8 | 4/8 | 4/8 | 4/8 | 2/8 | 7/8 | 0/8 | False |
| global | 8 | 0.0000 | 0.189760 | 0.547070 | 0/8 | 5/8 | 0/8 | 4/8 | 0/8 | 0/8 | 0/8 | False |
| moneyness | 8 | -17557.0000 | 0.191985 | 0.557819 | 0/8 | 5/8 | 0/8 | 4/8 | 0/8 | 0/8 | 0/8 | False |
| time_moneyness_disagreement | 8 | 60962.0000 | 0.194635 | 0.565346 | 5/8 | 3/8 | 2/8 | 3/8 | 2/8 | 4/8 | 0/8 | False |
| time | 8 | -57996.0000 | 0.196259 | 0.566329 | 4/8 | 5/8 | 1/8 | 2/8 | 3/8 | 3/8 | 0/8 | False |

## Holdouts

| holdout | spec | global_anchor | buckets | selected | pnl_cents | brier | beats_brownian | beats_market | beats_current | ev_rank | top_bucket | strict |
|---|---|---|---:|---:|---:|---:|---|---|---|---:|---:|---|
| particle_side_safety_oos_20260511TLOCKED | global | market | 1 | 115 | 0.0000 | 0.172172 | True | False | False | 0.000000 | 0.0000 | False |
| particle_side_safety_oos_20260511TLOCKED | time | market | 4 | 2196 | 15409.0000 | 0.166989 | True | True | False | 0.042360 | 11.3141 | False |
| particle_side_safety_oos_20260511TLOCKED | moneyness | market | 4 | 375 | -1507.0000 | 0.176110 | True | False | False | -0.970933 | -1.7729 | False |
| particle_side_safety_oos_20260511TLOCKED | time_moneyness | market | 12 | 2003 | 13557.0000 | 0.173426 | True | False | False | -0.042434 | 5.3871 | False |
| particle_side_safety_oos_20260511TLOCKED | time_moneyness_disagreement | market | 29 | 1945 | 9276.0000 | 0.175228 | True | False | False | -0.069349 | 4.0694 | False |
| particle_side_safety_oos_20260511TLOCKED | time_spread_disagreement | market | 24 | 1822 | 10933.0000 | 0.168390 | True | True | False | 0.018186 | 11.3224 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | global | market | 1 | 170 | 0.0000 | 0.160965 | True | False | False | 0.000000 | 0.0000 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | time | market | 4 | 2155 | 21673.0000 | 0.160931 | True | False | False | 0.030564 | 1.3756 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | moneyness | market | 4 | 170 | 0.0000 | 0.160965 | True | False | False | 0.000000 | 0.0000 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | time_moneyness | market | 12 | 2693 | 21918.0000 | 0.185883 | True | False | False | -0.123066 | -8.0708 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | time_moneyness_disagreement | market | 28 | 2666 | 14932.0000 | 0.189173 | False | False | False | -0.124454 | -8.2066 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | time_spread_disagreement | market | 23 | 1133 | 2147.0000 | 0.165424 | True | False | False | -0.101926 | 0.4897 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | global | market | 1 | 55 | 0.0000 | 0.200321 | True | False | False | 0.000000 | 0.0000 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | time | market | 4 | 2182 | 8975.0000 | 0.203081 | True | False | False | -0.064489 | 3.6874 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | moneyness | market | 4 | 106 | -51.0000 | 0.200906 | True | False | False | -0.995196 | -0.0597 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | time_moneyness | market | 12 | 1964 | 4548.0000 | 0.202849 | True | False | False | -0.084252 | 8.5023 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | time_moneyness_disagreement | market | 29 | 1586 | -9033.0000 | 0.210170 | False | False | False | -0.235402 | -4.0047 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | time_spread_disagreement | market | 24 | 1507 | -6036.0000 | 0.208773 | False | False | False | -0.156305 | 0.7787 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | global | market | 1 | 202 | 0.0000 | 0.080857 | True | False | False | 0.000000 | 0.0000 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | time | market | 4 | 2220 | 1725.0000 | 0.084748 | True | False | False | 0.026271 | -1.6994 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | moneyness | market | 3 | 1005 | -6914.0000 | 0.089039 | True | False | False | -0.797109 | -6.3644 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | time_moneyness | market | 12 | 2129 | -16618.0000 | 0.097047 | True | False | False | -0.276831 | -11.3141 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | time_moneyness_disagreement | market | 27 | 2085 | -18421.0000 | 0.098198 | True | False | False | -0.295128 | -11.7092 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | time_spread_disagreement | market | 23 | 1837 | -8935.0000 | 0.089854 | True | False | False | -0.217476 | -7.5043 | False |
| particle_residual_blend_oos_RESIDLOCK001 | global | market | 1 | 96 | 0.0000 | 0.233343 | False | False | True | 0.000000 | 0.0000 | False |
| particle_residual_blend_oos_RESIDLOCK001 | time | market | 4 | 1944 | -23093.0000 | 0.241567 | False | False | True | -0.057718 | -12.0167 | False |
| particle_residual_blend_oos_RESIDLOCK001 | moneyness | market | 3 | 425 | -2110.0000 | 0.235895 | False | False | True | -0.952973 | -2.5119 | False |
| particle_residual_blend_oos_RESIDLOCK001 | time_moneyness | market | 12 | 1815 | 22264.0000 | 0.221019 | False | True | True | 0.060293 | 30.1345 | False |
| particle_residual_blend_oos_RESIDLOCK001 | time_moneyness_disagreement | market | 27 | 1982 | 27341.0000 | 0.218540 | False | True | True | 0.098003 | 32.1810 | False |
| particle_residual_blend_oos_RESIDLOCK001 | time_spread_disagreement | market | 24 | 1355 | 1080.0000 | 0.229994 | False | True | True | 0.031843 | 8.1190 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | global | market | 1 | 108 | 0.0000 | 0.268521 | False | False | True | 0.000000 | 0.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | time | market | 4 | 1341 | -16866.0000 | 0.276745 | False | False | False | -0.165343 | -19.6598 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | moneyness | market | 3 | 108 | 0.0000 | 0.268521 | False | False | True | 0.000000 | 0.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | time_moneyness | market | 12 | 1192 | 27536.0000 | 0.246874 | False | True | True | 0.211710 | 43.3100 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | time_moneyness_disagreement | market | 29 | 1366 | 32727.0000 | 0.241795 | False | True | True | 0.231530 | 47.6407 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | time_spread_disagreement | market | 24 | 918 | 3289.0000 | 0.260243 | False | True | True | -0.017090 | 6.7552 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | global | market | 1 | 103 | 0.0000 | 0.256284 | False | False | True | 0.000000 | 0.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | time | market | 4 | 2631 | -36148.0000 | 0.266134 | False | False | True | -0.099025 | -16.3361 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | moneyness | market | 4 | 170 | -6115.0000 | 0.257541 | False | False | True | -0.993572 | -5.0495 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | time_moneyness | market | 12 | 2309 | 14102.0000 | 0.252880 | False | True | True | 0.002926 | 9.0636 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | time_moneyness_disagreement | market | 28 | 2656 | 10372.0000 | 0.255009 | False | False | True | -0.031980 | 9.1833 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | time_spread_disagreement | market | 23 | 2205 | 2403.0000 | 0.254288 | False | True | True | -0.043931 | 9.1082 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | global | market | 1 | 102 | 0.0000 | 0.145615 | True | False | True | 0.000000 | 0.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | time | market | 4 | 3251 | -29671.0000 | 0.169876 | True | False | False | -0.070589 | -8.6016 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | moneyness | market | 4 | 220 | -860.0000 | 0.146900 | True | False | True | -0.987645 | -0.7804 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | time_moneyness | market | 12 | 3193 | 1680.0000 | 0.160425 | True | False | True | -0.074395 | -6.5472 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | time_moneyness_disagreement | market | 28 | 3390 | -6232.0000 | 0.168964 | True | False | False | -0.063794 | -10.1588 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | time_spread_disagreement | market | 24 | 2475 | 14323.0000 | 0.153723 | True | False | True | -0.105007 | 1.4619 | False |

## Run Inputs

| run | rows | markets | candidate_path | label_path |
|---|---:|---:|---|---|
| particle_side_safety_oos_20260511TLOCKED | 3398 | 5 | `logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\pipeline_work\label_contexts_full_refresh.ndjson` |
| particle_dynamic_oos_20260511TLOCKEDNEXT | 3501 | 5 | `logs\particle_research\real_shadow\particle_dynamic_oos_20260511TLOCKEDNEXT\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_dynamic_oos_20260511TLOCKEDNEXT\pipeline_work\label_contexts_full_refresh.ndjson` |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | 3414 | 6 | `logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\pipeline_work\label_contexts_full_refresh.ndjson` |
| particle_side_consensus_oos_CONSENSUSLOCK001 | 3260 | 6 | `logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\pipeline_work\label_contexts_full_refresh.ndjson` |
| particle_residual_blend_oos_RESIDLOCK001 | 3358 | 5 | `logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\pipeline_work\label_contexts_full_refresh.ndjson` |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | 2514 | 4 | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK001\pipeline_work\label_contexts_full_refresh.ndjson` |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | 4843 | 7 | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\pipeline_work\label_contexts_full_refresh.ndjson` |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | 4405 | 6 | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK003\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK003\pipeline_work\label_contexts_full_refresh.ndjson` |
