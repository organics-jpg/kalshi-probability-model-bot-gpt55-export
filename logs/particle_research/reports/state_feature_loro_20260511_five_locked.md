# State Feature LORO Report

- run_count: 5
- holdout_row_count: 20
- promotion_safe: False
- conclusion: No timestamp-available state-feature model passes strict locked holdout gates.

## Summary

| model | holdouts | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | strict_all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| state_moneyness_time | 5 | -140527.0000 | 0.225548 | 0.664205 | 2/5 | 2/5 | 1/5 | 0/5 | 3/5 | 2/5 | 0/5 | False |
| state_plus_residuals | 5 | -174049.0000 | 0.242093 | 0.788716 | 1/5 | 1/5 | 1/5 | 0/5 | 3/5 | 2/5 | 0/5 | False |
| state_plus_market_current | 5 | -176766.0000 | 0.232197 | 0.712292 | 1/5 | 1/5 | 0/5 | 0/5 | 2/5 | 1/5 | 0/5 | False |
| state_book_cost | 5 | -186271.0000 | 0.263194 | 0.907707 | 1/5 | 1/5 | 0/5 | 0/5 | 2/5 | 1/5 | 0/5 | False |

## Holdouts

| holdout | model | train_markets | candidates | markets | selected | pnl_cents | brier | log_loss | beats_brownian | beats_market | beats_current | ev_rank | top_bucket_pnl | strict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---|
| particle_side_safety_oos_20260511TLOCKED | state_moneyness_time | 22 | 3398 | 5 | 3241 | -27096.0000 | 0.215161 | 0.628733 | False | False | False | -0.099584 | -1.2847 | False |
| particle_side_safety_oos_20260511TLOCKED | state_book_cost | 22 | 3398 | 5 | 3156 | -38394.0000 | 0.292948 | 0.928189 | False | False | False | -0.165505 | -24.9718 | False |
| particle_side_safety_oos_20260511TLOCKED | state_plus_market_current | 22 | 3398 | 5 | 3104 | -23174.0000 | 0.225487 | 0.638198 | False | False | False | -0.147552 | -16.8553 | False |
| particle_side_safety_oos_20260511TLOCKED | state_plus_residuals | 22 | 3398 | 5 | 3190 | -33570.0000 | 0.286684 | 0.857613 | False | False | False | -0.195997 | -12.9188 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | state_moneyness_time | 22 | 3501 | 5 | 3230 | -35888.0000 | 0.184508 | 0.526923 | True | False | False | 0.109325 | 0.5959 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | state_book_cost | 22 | 3501 | 5 | 3206 | -40668.0000 | 0.237353 | 0.782036 | False | False | False | -0.122824 | -33.4715 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | state_plus_market_current | 22 | 3501 | 5 | 3236 | -57120.0000 | 0.241173 | 0.697337 | False | False | False | -0.224937 | -40.4349 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | state_plus_residuals | 22 | 3501 | 5 | 3030 | -23153.0000 | 0.176626 | 0.567387 | False | False | False | 0.008221 | -14.7215 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | state_moneyness_time | 21 | 3414 | 6 | 3230 | 585.0000 | 0.275688 | 0.829091 | False | False | False | 0.056275 | -0.2002 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | state_book_cost | 21 | 3414 | 6 | 3273 | -8024.0000 | 0.220135 | 0.823510 | False | False | False | 0.200923 | 13.4496 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | state_plus_market_current | 21 | 3414 | 6 | 2941 | 9329.0000 | 0.212165 | 0.703067 | False | False | False | 0.184218 | 13.5246 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | state_plus_residuals | 21 | 3414 | 6 | 3314 | -30397.0000 | 0.258182 | 0.971087 | False | False | False | 0.073304 | 3.4321 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | state_moneyness_time | 21 | 3260 | 6 | 2893 | 18471.0000 | 0.072998 | 0.266204 | True | True | False | 0.173171 | 14.9951 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | state_book_cost | 21 | 3260 | 6 | 2948 | 939.0000 | 0.095288 | 0.303134 | True | False | False | 0.085470 | -0.5264 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | state_plus_market_current | 21 | 3260 | 6 | 2846 | -14965.0000 | 0.099548 | 0.299193 | True | False | False | 0.080011 | -8.5472 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | state_plus_residuals | 21 | 3260 | 6 | 2556 | 7028.0000 | 0.077294 | 0.255430 | True | True | False | 0.321528 | 6.3215 | False |
| particle_residual_blend_oos_RESIDLOCK001 | state_moneyness_time | 22 | 3358 | 5 | 3159 | -96599.0000 | 0.379384 | 1.070073 | False | False | False | -0.169961 | -40.1179 | False |
| particle_residual_blend_oos_RESIDLOCK001 | state_book_cost | 22 | 3358 | 5 | 3200 | -100124.0000 | 0.470244 | 1.701669 | False | False | False | -0.178501 | -52.5643 | False |
| particle_residual_blend_oos_RESIDLOCK001 | state_plus_market_current | 22 | 3358 | 5 | 3128 | -90836.0000 | 0.382614 | 1.223663 | False | False | False | -0.192180 | -44.9690 | False |
| particle_residual_blend_oos_RESIDLOCK001 | state_plus_residuals | 22 | 3358 | 5 | 3108 | -93957.0000 | 0.411678 | 1.292066 | False | False | False | -0.186857 | -42.6857 | False |

## Run Inputs

| run | rows | markets | candidate_path | label_path |
|---|---:|---:|---|---|
| particle_side_safety_oos_20260511TLOCKED | 3398 | 5 | `logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\pipeline_work\label_contexts_full_refresh.ndjson` |
| particle_dynamic_oos_20260511TLOCKEDNEXT | 3501 | 5 | `logs\particle_research\real_shadow\particle_dynamic_oos_20260511TLOCKEDNEXT\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_dynamic_oos_20260511TLOCKEDNEXT\pipeline_work\label_contexts_full_refresh.ndjson` |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | 3414 | 6 | `logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\pipeline_work\label_contexts_full_refresh.ndjson` |
| particle_side_consensus_oos_CONSENSUSLOCK001 | 3260 | 6 | `logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\pipeline_work\label_contexts_full_refresh.ndjson` |
| particle_residual_blend_oos_RESIDLOCK001 | 3358 | 5 | `logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\pipeline_work\label_contexts_full_refresh.ndjson` |
