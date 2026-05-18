# Meta Probability LORO Report

- run_count: 5
- holdout_row_count: 20
- promotion_safe: False
- conclusion: No simple market-cluster-trained meta-probability model passes strict locked holdout gates.

## Summary

| model | holdouts | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | strict_all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| logit_current | 5 | -141229.0000 | 0.197074 | 0.556644 | 2/5 | 2/5 | 2/5 | 0/5 | 2/5 | 2/5 | 0/5 | False |
| logit_market_current_particle | 5 | -179634.0000 | 0.210560 | 0.602624 | 1/5 | 1/5 | 1/5 | 0/5 | 2/5 | 2/5 | 0/5 | False |
| current_with_residuals | 5 | -185132.0000 | 0.213973 | 0.638752 | 0/5 | 1/5 | 1/5 | 0/5 | 3/5 | 1/5 | 0/5 | False |
| logit_market_current | 5 | -193497.0000 | 0.206863 | 0.587862 | 1/5 | 1/5 | 1/5 | 0/5 | 2/5 | 2/5 | 0/5 | False |

## Holdouts

| holdout | model | train_markets | candidates | markets | selected | pnl_cents | brier | log_loss | beats_brownian | beats_market | beats_current | ev_rank | top_bucket_pnl | strict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---|
| particle_side_safety_oos_20260511TLOCKED | logit_current | 22 | 3398 | 5 | 3161 | -34662.0000 | 0.202044 | 0.567291 | False | False | False | -0.120995 | -16.3576 | False |
| particle_side_safety_oos_20260511TLOCKED | logit_market_current | 22 | 3398 | 5 | 3015 | -40061.0000 | 0.214159 | 0.596092 | False | False | False | -0.183712 | -23.0776 | False |
| particle_side_safety_oos_20260511TLOCKED | logit_market_current_particle | 22 | 3398 | 5 | 2957 | -37965.0000 | 0.215227 | 0.600926 | False | False | False | -0.137407 | -23.7776 | False |
| particle_side_safety_oos_20260511TLOCKED | current_with_residuals | 22 | 3398 | 5 | 3126 | -32554.0000 | 0.210967 | 0.599716 | False | False | False | -0.117157 | -17.2082 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | logit_current | 22 | 3501 | 5 | 3245 | -51028.0000 | 0.204153 | 0.581213 | False | False | False | -0.024363 | -10.5160 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | logit_market_current | 22 | 3501 | 5 | 3214 | -51558.0000 | 0.218002 | 0.608795 | False | False | False | -0.054532 | -14.2671 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | logit_market_current_particle | 22 | 3501 | 5 | 3220 | -51369.0000 | 0.220274 | 0.613575 | False | False | False | -0.023515 | -15.9954 | False |
| particle_dynamic_oos_20260511TLOCKEDNEXT | current_with_residuals | 22 | 3501 | 5 | 3298 | -43910.0000 | 0.220477 | 0.659309 | False | False | False | 0.012088 | -11.0559 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | logit_current | 21 | 3414 | 6 | 2484 | 13054.0000 | 0.198224 | 0.576875 | True | True | False | 0.159016 | 10.9239 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | logit_market_current | 21 | 3414 | 6 | 2589 | -17373.0000 | 0.204302 | 0.626620 | False | False | False | 0.244550 | 11.1124 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | logit_market_current_particle | 21 | 3414 | 6 | 2704 | -11935.0000 | 0.199866 | 0.606511 | False | False | False | 0.256933 | 12.3653 | False |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | current_with_residuals | 21 | 3414 | 6 | 2872 | -22131.0000 | 0.214704 | 0.673638 | False | False | False | 0.178991 | -0.6920 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | logit_current | 21 | 3260 | 6 | 2810 | 19467.0000 | 0.073689 | 0.226309 | True | True | False | 0.440038 | 16.8037 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | logit_market_current | 21 | 3260 | 6 | 2716 | 13641.0000 | 0.076680 | 0.237338 | True | True | False | 0.415815 | 11.7571 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | logit_market_current_particle | 21 | 3260 | 6 | 2770 | 15127.0000 | 0.075654 | 0.231085 | True | True | False | 0.432481 | 13.0687 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | current_with_residuals | 21 | 3260 | 6 | 2638 | -4253.0000 | 0.078603 | 0.241511 | True | True | False | 0.407541 | 16.2613 | False |
| particle_residual_blend_oos_RESIDLOCK001 | logit_current | 22 | 3358 | 5 | 2944 | -88060.0000 | 0.307258 | 0.831531 | False | False | False | -0.200906 | -36.1917 | False |
| particle_residual_blend_oos_RESIDLOCK001 | logit_market_current | 22 | 3358 | 5 | 3040 | -98146.0000 | 0.321174 | 0.870466 | False | False | False | -0.252610 | -42.5321 | False |
| particle_residual_blend_oos_RESIDLOCK001 | logit_market_current_particle | 22 | 3358 | 5 | 3093 | -93492.0000 | 0.341779 | 0.961021 | False | False | False | -0.243015 | -43.6333 | False |
| particle_residual_blend_oos_RESIDLOCK001 | current_with_residuals | 22 | 3358 | 5 | 3172 | -82284.0000 | 0.345114 | 1.019589 | False | False | False | -0.171962 | -34.2143 | False |

## Run Inputs

| run | rows | markets | candidate_path | label_path |
|---|---:|---:|---|---|
| particle_side_safety_oos_20260511TLOCKED | 3398 | 5 | `logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\pipeline_work\label_contexts_full_refresh.ndjson` |
| particle_dynamic_oos_20260511TLOCKEDNEXT | 3501 | 5 | `logs\particle_research\real_shadow\particle_dynamic_oos_20260511TLOCKEDNEXT\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_dynamic_oos_20260511TLOCKEDNEXT\pipeline_work\label_contexts_full_refresh.ndjson` |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | 3414 | 6 | `logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\pipeline_work\label_contexts_full_refresh.ndjson` |
| particle_side_consensus_oos_CONSENSUSLOCK001 | 3260 | 6 | `logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\pipeline_work\label_contexts_full_refresh.ndjson` |
| particle_residual_blend_oos_RESIDLOCK001 | 3358 | 5 | `logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\pipeline_work\label_contexts_full_refresh.ndjson` |
