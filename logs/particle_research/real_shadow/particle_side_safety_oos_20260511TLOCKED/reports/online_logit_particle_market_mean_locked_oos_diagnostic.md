# Online Logit Particle Replay Report

- candidate_count: 3398
- source_candidate_count: 3398
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- learning_rate: 0.030000
- l2: 0.001000
- update_mode: market_mean
- best_by_brier: online_logit_market_mean_rolling_vol_300s
- best_by_pnl: online_logit_market_mean_rolling_vol_600s
- promotion_safe: False
- note: Online-logit calibration variants are locked-run diagnostics only. They update only after label_available_ts_utc and do not promote a strategy without a fresh predeclared OOS/shadow run.

| variant | raw_source | update_mode | brier | log_loss | raw_brier | raw_log_loss | pnl_cents | selected | coverage | beats_raw | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl | updates | final_bias | final_slope |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---:|---:|---:|---:|---:|
| online_logit_market_mean_particle | particle | market_mean | 0.185855 | 0.554626 | 0.186131 | 0.555235 | 16005.0000 | 3124 | 0.9194 | True | True | False | False | 0.069628 | 1.9365 | 5 | -0.033899 | 1.016998 |
| online_logit_market_mean_current_calibrated | current_calibrated | market_mean | 0.164183 | 0.484029 | 0.163866 | 0.483483 | 25623.0000 | 2919 | 0.8590 | False | True | True | False | 0.013576 | 9.6118 | 5 | -0.026175 | 1.019883 |
| online_logit_market_mean_rolling_vol_300s | rolling_vol_300s | market_mean | 0.157133 | 0.460221 | 0.156740 | 0.459442 | 35369.0000 | 2888 | 0.8499 | False | True | True | True | 0.127762 | 22.4588 | 5 | -0.023415 | 1.021499 |
| online_logit_market_mean_rolling_vol_600s | rolling_vol_600s | market_mean | 0.158132 | 0.462777 | 0.157714 | 0.461933 | 39779.0000 | 2941 | 0.8655 | False | True | True | True | 0.110709 | 20.2941 | 5 | -0.023413 | 1.021013 |
| online_logit_market_mean_median_current_rv300_rv600 | median_current_rv300_rv600 | market_mean | 0.157920 | 0.463287 | 0.157527 | 0.462518 | 38942.0000 | 2916 | 0.8582 | False | True | True | True | 0.104582 | 19.6282 | 5 | -0.023689 | 1.021147 |
| online_logit_market_mean_blend_50current_25particle_25rv600 | blend_50current_25particle_25rv600 | market_mean | 0.164587 | 0.491977 | 0.164429 | 0.491816 | 23500.0000 | 3017 | 0.8879 | False | True | True | False | 0.014637 | 11.8212 | 5 | -0.027407 | 1.020624 |
