# Spot Micro LORO Report

- eligible_run_count: 4
- skipped_run_count: 3
- holdout_row_count: 16
- windows_seconds: 1, 2, 3, 5, 8, 13, 21, 34, 55, 89
- promotion_safe: False
- conclusion: No independent-spot microstructure model passes strict eligible holdout gates; eligible tick-root count is too small for promotion even if a row looks good.

## Summary

| model | holdouts | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | strict_all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| spot_phi_returns | 4 | 5532.0000 | 0.429433 | 5.529054 | 2/4 | 0/4 | 0/4 | 0/4 | 3/4 | 3/4 | 0/4 | False |
| spot_micro_all | 4 | -13173.0000 | 0.404781 | 4.737524 | 1/4 | 0/4 | 0/4 | 0/4 | 3/4 | 3/4 | 0/4 | False |
| spot_micro_compact | 4 | -18800.0000 | 0.421750 | 4.844352 | 1/4 | 0/4 | 0/4 | 0/4 | 3/4 | 3/4 | 0/4 | False |
| spot_micro_plus_current | 4 | -33921.0000 | 0.427285 | 4.939251 | 0/4 | 0/4 | 0/4 | 0/4 | 3/4 | 3/4 | 0/4 | False |

## Holdouts

| holdout | model | train_markets | candidates | markets | selected | pnl_cents | brier | log_loss | beats_brownian | beats_market | beats_current | ev_rank | top_bucket_pnl | strict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---|
| particle_side_consensus_oos_CONSENSUSLOCK001 | spot_phi_returns | 16 | 3260 | 6 | 3148 | -7239.0000 | 0.451596 | 8.677134 | False | False | False | -0.024787 | -8.0196 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | spot_micro_compact | 16 | 3260 | 6 | 3117 | -3932.0000 | 0.429796 | 7.862772 | False | False | False | -0.018148 | -9.3288 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | spot_micro_all | 16 | 3260 | 6 | 3129 | -4817.0000 | 0.420093 | 7.204111 | False | False | False | -0.020195 | -10.1816 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | spot_micro_plus_current | 16 | 3260 | 6 | 3129 | -7501.0000 | 0.456639 | 8.429163 | False | False | False | -0.037558 | -8.7460 | False |
| particle_residual_blend_oos_RESIDLOCK001 | spot_phi_returns | 17 | 3358 | 5 | 3244 | -3938.0000 | 0.438866 | 5.196984 | False | False | False | 0.241467 | 15.7833 | False |
| particle_residual_blend_oos_RESIDLOCK001 | spot_micro_compact | 17 | 3358 | 5 | 3242 | -11629.0000 | 0.436911 | 4.330471 | False | False | False | 0.219688 | 19.3131 | False |
| particle_residual_blend_oos_RESIDLOCK001 | spot_micro_all | 17 | 3358 | 5 | 3241 | -15441.0000 | 0.437808 | 4.288163 | False | False | False | 0.243458 | 19.1845 | False |
| particle_residual_blend_oos_RESIDLOCK001 | spot_micro_plus_current | 17 | 3358 | 5 | 3233 | -14505.0000 | 0.436530 | 4.307375 | False | False | False | 0.205752 | 19.3440 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | spot_phi_returns | 18 | 2514 | 4 | 2430 | 3120.0000 | 0.408026 | 4.204424 | False | False | False | 0.230057 | 30.0382 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | spot_micro_compact | 18 | 2514 | 4 | 2432 | 642.0000 | 0.383510 | 3.663773 | False | False | False | 0.242833 | 31.9491 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | spot_micro_all | 18 | 2514 | 4 | 2394 | 8546.0000 | 0.341221 | 3.832212 | False | False | False | 0.326542 | 40.0223 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | spot_micro_plus_current | 18 | 2514 | 4 | 2404 | -5104.0000 | 0.381739 | 3.659114 | False | False | False | 0.246272 | 32.3990 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | spot_phi_returns | 15 | 4843 | 7 | 4735 | 13589.0000 | 0.419242 | 4.037676 | False | False | False | 0.187060 | 17.6697 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | spot_micro_compact | 15 | 4843 | 7 | 4741 | -3881.0000 | 0.436784 | 3.520391 | False | False | False | 0.209103 | 14.0347 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | spot_micro_all | 15 | 4843 | 7 | 4726 | -1461.0000 | 0.420004 | 3.625611 | False | False | False | 0.224048 | 15.0628 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | spot_micro_plus_current | 15 | 4843 | 7 | 4733 | -6811.0000 | 0.434232 | 3.361350 | False | False | False | 0.202766 | 12.8431 | False |

## Run Inputs

| run | rows | markets | spot_ticks | rows_prior_spot | rows_recent_spot | spot_tick_path |
|---|---:|---:|---:|---:|---:|---|
| particle_side_consensus_oos_CONSENSUSLOCK001 | 3260 | 6 | 37344 | 3260 | 3258 | `logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\independent_spot_ticks.ndjson` |
| particle_residual_blend_oos_RESIDLOCK001 | 3358 | 5 | 44784 | 3358 | 3358 | `logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\independent_spot_ticks.ndjson` |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | 2514 | 4 | 48313 | 2514 | 2513 | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK001\independent_spot_ticks.ndjson` |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | 4843 | 7 | 37126 | 4843 | 4843 | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\independent_spot_ticks.ndjson` |

## Skipped Runs

- `logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED`
- `logs\particle_research\real_shadow\particle_dynamic_oos_20260511TLOCKEDNEXT`
- `logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2`
