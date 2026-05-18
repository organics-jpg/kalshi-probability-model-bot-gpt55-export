# Variant LORO Selection Diagnostic

- source_stability_report: `logs\particle_research\reports\locked_oos_stability_latest.json`
- run_count: 5
- variant_row_count: 164
- holdout_row_count: 15
- promotion_safe: False
- conclusion: No leave-one-run-out selector passes the strict holdout gates across locked runs.

## Selector Summary

| selector | holdouts | total_holdout_pnl | mean_brier | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | strict_all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| train_best_gate_score | 5 | 62814.0000 | 0.166452 | 4/5 | 4/5 | 3/5 | 2/5 | 3/5 | 4/5 | 1/5 | False |
| train_best_mean_brier | 5 | 17019.0000 | 0.170537 | 3/5 | 4/5 | 0/5 | 0/5 | 1/5 | 3/5 | 0/5 | False |
| train_best_total_pnl | 5 | -127077.0000 | 0.284136 | 1/5 | 1/5 | 0/5 | 0/5 | 3/5 | 1/5 | 0/5 | False |

## Holdouts

| selector | holdout | variant | train_runs | train_pnl | train_brier | holdout_pnl | holdout_brier | beats_brownian | beats_market | beats_current | ev_rank_pos | top_bucket_pos | strict |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|---|---|---|
| train_best_total_pnl | particle_dynamic600_oos_20260511TLOCKEDNEXT2 | online_logit:online_logit_market_mean_rolling_vol_600s | 2 | 79113.0000 | 0.151292 | 3298.0000 | 0.202449 | True | False | False | False | True | False |
| train_best_mean_brier | particle_dynamic600_oos_20260511TLOCKEDNEXT2 | online_logit:online_logit_market_mean_rolling_vol_600s | 2 | 79113.0000 | 0.151292 | 3298.0000 | 0.202449 | True | False | False | False | True | False |
| train_best_gate_score | particle_dynamic600_oos_20260511TLOCKEDNEXT2 | ensemble:blend_50rv600_30current_20market | 4 | 62584.0000 | 0.156832 | 11084.0000 | 0.199658 | True | True | False | False | True | False |
| train_best_total_pnl | particle_dynamic_oos_20260511TLOCKEDNEXT | online_logit:online_logit_particle | 3 | 80382.0000 | 0.244626 | -10033.0000 | 0.460014 | False | False | False | True | False | False |
| train_best_mean_brier | particle_dynamic_oos_20260511TLOCKEDNEXT | probability:current_particle_75_25 | 4 | 71069.0000 | 0.166543 | 23696.0000 | 0.157055 | True | False | False | True | True | False |
| train_best_gate_score | particle_dynamic_oos_20260511TLOCKEDNEXT | ensemble:blend_50current_25particle_25rv600 | 4 | 61258.0000 | 0.167685 | 25366.0000 | 0.154783 | True | False | False | True | True | False |
| train_best_total_pnl | particle_residual_blend_oos_RESIDLOCK001 | probability:current_calibrated | 4 | 105135.0000 | 0.145284 | -24387.0000 | 0.242148 | False | False | False | False | False | False |
| train_best_mean_brier | particle_residual_blend_oos_RESIDLOCK001 | probability:current_calibrated | 4 | 105135.0000 | 0.145284 | -24387.0000 | 0.242148 | False | False | False | False | False | False |
| train_best_gate_score | particle_residual_blend_oos_RESIDLOCK001 | ensemble:blend_50rv600_30current_20market | 4 | 94453.0000 | 0.146556 | -20785.0000 | 0.240762 | False | False | True | False | False | False |
| train_best_total_pnl | particle_side_consensus_oos_CONSENSUSLOCK001 | probability:brownian | 4 | 107620.0000 | 0.199504 | -33071.0000 | 0.107891 | False | False | False | True | False | False |
| train_best_mean_brier | particle_side_consensus_oos_CONSENSUSLOCK001 | dynamic:rolling_vol_600s | 4 | 62172.0000 | 0.187413 | -8207.0000 | 0.084460 | True | False | False | False | False | False |
| train_best_gate_score | particle_side_consensus_oos_CONSENSUSLOCK001 | ensemble:blend_50rv600_30current_20market | 4 | 58492.0000 | 0.187833 | 15176.0000 | 0.075656 | True | True | False | True | True | False |
| train_best_total_pnl | particle_side_safety_oos_20260511TLOCKED | online_logit:online_logit_current_calibrated | 3 | 103420.0000 | 0.201170 | -62884.0000 | 0.408177 | False | False | False | True | False | False |
| train_best_mean_brier | particle_side_safety_oos_20260511TLOCKED | probability:current_particle_75_25 | 4 | 72146.0000 | 0.164163 | 22619.0000 | 0.166575 | True | False | False | False | True | False |
| train_best_gate_score | particle_side_safety_oos_20260511TLOCKED | ensemble:blend_50rv600_30current_20market | 4 | 41695.0000 | 0.166396 | 31973.0000 | 0.161403 | True | True | True | True | True | True |
