# Spot Micro LORO Report

- eligible_run_count: 2
- skipped_run_count: 3
- holdout_row_count: 8
- windows_seconds: 1, 2, 3, 5, 8, 13, 21, 34, 55, 89
- promotion_safe: False
- conclusion: No independent-spot microstructure model passes strict eligible holdout gates; eligible tick-root count is too small for promotion even if a row looks good.

## Summary

| model | holdouts | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | strict_all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| spot_phi_returns | 2 | -20205.0000 | 0.432438 | 5.015147 | 0/2 | 0/2 | 0/2 | 0/2 | 1/2 | 1/2 | 0/2 | False |
| spot_micro_all | 2 | -34454.0000 | 0.407763 | 3.473083 | 0/2 | 0/2 | 0/2 | 0/2 | 1/2 | 1/2 | 0/2 | False |
| spot_micro_compact | 2 | -46744.0000 | 0.418714 | 3.640911 | 0/2 | 0/2 | 0/2 | 0/2 | 1/2 | 1/2 | 0/2 | False |
| spot_micro_plus_current | 2 | -76694.0000 | 0.406410 | 3.253824 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | False |

## Holdouts

| holdout | model | train_markets | candidates | markets | selected | pnl_cents | brier | log_loss | beats_brownian | beats_market | beats_current | ev_rank | top_bucket_pnl | strict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---|
| particle_side_consensus_oos_CONSENSUSLOCK001 | spot_phi_returns | 5 | 3260 | 6 | 3145 | -10953.0000 | 0.442838 | 7.319215 | False | False | False | -0.043815 | -8.7276 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | spot_micro_compact | 5 | 3260 | 6 | 3103 | -13381.0000 | 0.427356 | 5.678301 | False | False | False | -0.058731 | -11.9337 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | spot_micro_all | 5 | 3260 | 6 | 3081 | -11192.0000 | 0.385572 | 4.501514 | False | False | False | -0.043239 | -13.9791 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | spot_micro_plus_current | 5 | 3260 | 6 | 3084 | -13199.0000 | 0.406951 | 5.170774 | False | False | False | -0.053698 | -13.5963 | False |
| particle_residual_blend_oos_RESIDLOCK001 | spot_phi_returns | 6 | 3358 | 5 | 3246 | -9252.0000 | 0.422038 | 2.711079 | False | False | False | 0.165079 | 16.0083 | False |
| particle_residual_blend_oos_RESIDLOCK001 | spot_micro_compact | 6 | 3358 | 5 | 3230 | -33363.0000 | 0.410072 | 1.603521 | False | False | False | 0.054782 | 6.9893 | False |
| particle_residual_blend_oos_RESIDLOCK001 | spot_micro_all | 6 | 3358 | 5 | 3247 | -23262.0000 | 0.429954 | 2.444652 | False | False | False | 0.145465 | 11.8238 | False |
| particle_residual_blend_oos_RESIDLOCK001 | spot_micro_plus_current | 6 | 3358 | 5 | 3235 | -63495.0000 | 0.405868 | 1.336875 | False | False | False | -0.015488 | -10.7690 | False |

## Run Inputs

| run | rows | markets | spot_ticks | rows_prior_spot | rows_recent_spot | spot_tick_path |
|---|---:|---:|---:|---:|---:|---|
| particle_side_consensus_oos_CONSENSUSLOCK001 | 3260 | 6 | 37344 | 3260 | 3258 | `logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\independent_spot_ticks.ndjson` |
| particle_residual_blend_oos_RESIDLOCK001 | 3358 | 5 | 44784 | 3358 | 3358 | `logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\independent_spot_ticks.ndjson` |

## Skipped Runs

- `logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED`
- `logs\particle_research\real_shadow\particle_dynamic_oos_20260511TLOCKEDNEXT`
- `logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2`
