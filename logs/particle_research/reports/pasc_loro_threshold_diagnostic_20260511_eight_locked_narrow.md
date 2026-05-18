# PASC Threshold LORO Diagnostic

- run_count: 8
- variant_count: 3
- holdout_row_count: 24
- promotion_safe: False
- conclusion: No PnL-aware threshold selector passed strict leave-one-run-out locked gates.

## Summary

| selector | holdouts | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | strict_all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| train_best_gate_score | 8 | 117634.0000 | 0.189040 | 0.547820 | 7/8 | 5/8 | 3/8 | 4/8 | 3/8 | 7/8 | 1/8 | False |
| train_best_stable_pnl | 8 | 58656.0000 | 0.193724 | 0.562428 | 6/8 | 4/8 | 2/8 | 4/8 | 3/8 | 6/8 | 1/8 | False |
| train_best_total_pnl | 8 | 109594.0000 | 0.197560 | 0.574179 | 6/8 | 0/8 | 2/8 | 3/8 | 7/8 | 5/8 | 0/8 | False |

## Holdouts

| selector | holdout | variant | min_ev | min_fill | train_pnl | train_pos_pnl | selected | holdout_pnl | brier | beats_brownian | beats_market | beats_current | ev_rank | top_bucket | strict |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---|
| train_best_total_pnl | particle_side_safety_oos_20260511TLOCKED | brownian | 0.0000 | 0.5000 | 151521.0000 | 5/7 | 3106 | 15483.0000 | 0.186462 | False | False | False | 0.069536 | 2.4788 | False |
| train_best_stable_pnl | particle_side_safety_oos_20260511TLOCKED | current_particle_75_25 | 0.0000 | 0.5000 | 95015.0000 | 6/7 | 2994 | 22619.0000 | 0.166575 | True | False | False | -0.008089 | 7.9718 | False |
| train_best_gate_score | particle_side_safety_oos_20260511TLOCKED | current_particle_75_25 | 0.0000 | 0.5000 | 95015.0000 | 6/7 | 2994 | 22619.0000 | 0.166575 | True | False | False | -0.008089 | 7.9718 | False |
| train_best_total_pnl | particle_dynamic_oos_20260511TLOCKEDNEXT | brownian | 0.0000 | 0.5000 | 151409.0000 | 5/7 | 3290 | 15595.0000 | 0.188085 | False | False | False | 0.107784 | -2.7078 | False |
| train_best_stable_pnl | particle_dynamic_oos_20260511TLOCKEDNEXT | current_particle_75_25 | 0.0000 | 0.5000 | 93938.0000 | 6/7 | 3197 | 23696.0000 | 0.157055 | True | False | False | 0.027031 | 2.2854 | False |
| train_best_gate_score | particle_dynamic_oos_20260511TLOCKEDNEXT | current_particle_75_25 | 0.0000 | 0.5000 | 93938.0000 | 6/7 | 3197 | 23696.0000 | 0.157055 | True | False | False | 0.027031 | 2.2854 | False |
| train_best_total_pnl | particle_dynamic600_oos_20260511TLOCKEDNEXT2 | brownian | 0.0000 | 0.5000 | 151351.0000 | 5/7 | 3229 | 15653.0000 | 0.206625 | False | False | False | 0.224801 | 13.7623 | False |
| train_best_stable_pnl | particle_dynamic600_oos_20260511TLOCKEDNEXT2 | current_particle_75_25 | 0.0000 | 0.5000 | 98570.0000 | 6/7 | 3047 | 19064.0000 | 0.195874 | True | True | True | 0.012836 | 20.1827 | True |
| train_best_gate_score | particle_dynamic600_oos_20260511TLOCKEDNEXT2 | current_particle_75_25 | 0.0000 | 0.5000 | 98570.0000 | 6/7 | 3047 | 19064.0000 | 0.195874 | True | True | True | 0.012836 | 20.1827 | True |
| train_best_total_pnl | particle_side_consensus_oos_CONSENSUSLOCK001 | brownian | 0.0000 | 0.5000 | 200075.0000 | 6/7 | 3062 | -33071.0000 | 0.107891 | False | False | False | 0.015718 | -6.8883 | False |
| train_best_stable_pnl | particle_side_consensus_oos_CONSENSUSLOCK001 | brownian | 0.0000 | 0.5000 | 200075.0000 | 6/7 | 3062 | -33071.0000 | 0.107891 | False | False | False | 0.015718 | -6.8883 | False |
| train_best_gate_score | particle_side_consensus_oos_CONSENSUSLOCK001 | current_particle_75_25 | 0.0000 | 0.5000 | 91727.0000 | 6/7 | 2636 | 25907.0000 | 0.070421 | True | True | False | 0.164715 | 16.0184 | False |
| train_best_total_pnl | particle_residual_blend_oos_RESIDLOCK001 | current_particle_75_25 | 0.0000 | 0.5000 | 114155.0000 | 6/7 | 2521 | 3479.0000 | 0.233302 | False | False | True | -0.067265 | 5.3440 | False |
| train_best_stable_pnl | particle_residual_blend_oos_RESIDLOCK001 | current_particle_75_25 | 0.0000 | 0.5000 | 114155.0000 | 6/7 | 2521 | 3479.0000 | 0.233302 | False | False | True | -0.067265 | 5.3440 | False |
| train_best_gate_score | particle_residual_blend_oos_RESIDLOCK001 | current_particle_75_25 | 0.0000 | 0.5000 | 114155.0000 | 6/7 | 2521 | 3479.0000 | 0.233302 | False | False | True | -0.067265 | 5.3440 | False |
| train_best_total_pnl | particle_fixed_terminal_oos_GAUSS45LOCK001 | brownian | 0.0000 | 0.5000 | 116732.0000 | 5/7 | 2422 | 50272.0000 | 0.226938 | False | True | True | 0.188858 | 21.1129 | False |
| train_best_stable_pnl | particle_fixed_terminal_oos_GAUSS45LOCK001 | current_particle_75_25 | 0.0000 | 0.5000 | 89373.0000 | 6/7 | 2110 | 28261.0000 | 0.259683 | False | True | True | -0.034961 | 17.5914 | False |
| train_best_gate_score | particle_fixed_terminal_oos_GAUSS45LOCK001 | current_particle_75_25 | 0.0000 | 0.5000 | 89373.0000 | 6/7 | 2110 | 28261.0000 | 0.259683 | False | True | True | -0.034961 | 17.5914 | False |
| train_best_total_pnl | particle_fixed_terminal_oos_GAUSS45LOCK002 | brownian | 0.0000 | 0.5000 | 118592.0000 | 5/7 | 4582 | 48412.0000 | 0.240082 | False | True | True | 0.274386 | 19.7622 | False |
| train_best_stable_pnl | particle_fixed_terminal_oos_GAUSS45LOCK002 | current_particle_75_25 | 0.0000 | 0.5000 | 106184.0000 | 6/7 | 3889 | 11450.0000 | 0.257274 | False | False | True | -0.033008 | 5.2023 | False |
| train_best_gate_score | particle_fixed_terminal_oos_GAUSS45LOCK002 | current_particle_75_25 | 0.0000 | 0.5000 | 106184.0000 | 6/7 | 3889 | 11450.0000 | 0.257274 | False | False | True | -0.033008 | 5.2023 | False |
| train_best_total_pnl | particle_fixed_terminal_oos_GAUSS45LOCK003 | brownian | 0.0000 | 0.5000 | 173233.0000 | 6/7 | 4227 | -6229.0000 | 0.191099 | False | False | False | 0.066725 | -12.0717 | False |
| train_best_stable_pnl | particle_fixed_terminal_oos_GAUSS45LOCK003 | current_particle_75_25 | 0.0000 | 0.5000 | 134476.0000 | 7/7 | 3725 | -16842.0000 | 0.172136 | True | False | False | -0.185251 | -13.3358 | False |
| train_best_gate_score | particle_fixed_terminal_oos_GAUSS45LOCK003 | current_particle_75_25 | 0.0000 | 0.5000 | 134476.0000 | 7/7 | 3725 | -16842.0000 | 0.172136 | True | False | False | -0.185251 | -13.3358 | False |

## Variants

`particle`, `brownian`, `current_particle_75_25`

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
