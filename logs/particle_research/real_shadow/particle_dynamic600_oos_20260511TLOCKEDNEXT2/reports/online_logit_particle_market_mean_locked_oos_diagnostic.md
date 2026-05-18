# Online Logit Particle Replay Report

- candidate_count: 3414
- source_candidate_count: 3414
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- learning_rate: 0.030000
- l2: 0.001000
- update_mode: market_mean
- best_by_brier: online_logit_market_mean_blend_50current_25particle_25rv600
- best_by_pnl: online_logit_market_mean_blend_50current_25particle_25rv600
- promotion_safe: False
- note: Online-logit calibration variants are locked-run diagnostics only. They update only after label_available_ts_utc and do not promote a strategy without a fresh predeclared OOS/shadow run.

| variant | raw_source | update_mode | brier | log_loss | raw_brier | raw_log_loss | pnl_cents | selected | coverage | beats_raw | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl | updates | final_bias | final_slope |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---:|---:|---:|---:|---:|
| online_logit_market_mean_particle | particle | market_mean | 0.206377 | 0.598169 | 0.207154 | 0.600086 | 15940.0000 | 3209 | 0.9400 | True | True | False | False | 0.204842 | 14.6276 | 6 | 0.026180 | 1.018881 |
| online_logit_market_mean_current_calibrated | current_calibrated | market_mean | 0.199053 | 0.570134 | 0.199484 | 0.570736 | 13418.0000 | 2603 | 0.7624 | True | True | True | True | -0.021122 | 13.1663 | 6 | 0.025295 | 1.021992 |
| online_logit_market_mean_rolling_vol_300s | rolling_vol_300s | market_mean | 0.202160 | 0.579956 | 0.202030 | 0.579268 | 7666.0000 | 2758 | 0.8079 | False | True | False | False | -0.062384 | 13.4625 | 6 | 0.020172 | 1.019337 |
| online_logit_market_mean_rolling_vol_600s | rolling_vol_600s | market_mean | 0.202449 | 0.579953 | 0.202355 | 0.579325 | 3298.0000 | 2690 | 0.7879 | False | True | False | False | -0.089673 | 12.5035 | 6 | 0.020437 | 1.019815 |
| online_logit_market_mean_median_current_rv300_rv600 | median_current_rv300_rv600 | market_mean | 0.201440 | 0.577059 | 0.201324 | 0.576397 | 4737.0000 | 2701 | 0.7912 | False | True | False | False | -0.069786 | 14.5386 | 6 | 0.020160 | 1.019931 |
| online_logit_market_mean_blend_50current_25particle_25rv600 | blend_50current_25particle_25rv600 | market_mean | 0.196432 | 0.565480 | 0.196802 | 0.566467 | 17393.0000 | 3083 | 0.9030 | True | True | True | True | 0.024164 | 20.0023 | 6 | 0.024262 | 1.023411 |
