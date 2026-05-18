# Online Logit Particle Replay Report

- candidate_count: 3501
- source_candidate_count: 3501
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- learning_rate: 0.030000
- l2: 0.001000
- update_mode: market_mean
- best_by_brier: online_logit_market_mean_rolling_vol_600s
- best_by_pnl: online_logit_market_mean_rolling_vol_600s
- promotion_safe: False
- note: Online-logit calibration variants are locked-run diagnostics only. They update only after label_available_ts_utc and do not promote a strategy without a fresh predeclared OOS/shadow run.

| variant | raw_source | update_mode | brier | log_loss | raw_brier | raw_log_loss | pnl_cents | selected | coverage | beats_raw | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl | updates | final_bias | final_slope |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---:|---:|---:|---:|---:|
| online_logit_market_mean_particle | particle | market_mean | 0.188345 | 0.563112 | 0.188032 | 0.562406 | 16919.0000 | 3269 | 0.9337 | False | False | False | False | 0.081138 | -2.7511 | 5 | -0.015984 | 1.019523 |
| online_logit_market_mean_current_calibrated | current_calibrated | market_mean | 0.153287 | 0.462562 | 0.153673 | 0.463382 | 32755.0000 | 2829 | 0.8081 | True | True | True | True | 0.015268 | 5.2158 | 5 | -0.022692 | 1.027804 |
| online_logit_market_mean_rolling_vol_300s | rolling_vol_300s | market_mean | 0.150504 | 0.457388 | 0.150814 | 0.458110 | 33064.0000 | 2929 | 0.8366 | True | True | True | True | 0.050800 | 15.9795 | 5 | -0.019356 | 1.029805 |
| online_logit_market_mean_rolling_vol_600s | rolling_vol_600s | market_mean | 0.144452 | 0.436916 | 0.144880 | 0.437945 | 39334.0000 | 2884 | 0.8238 | True | True | True | True | 0.084393 | 20.6712 | 5 | -0.020554 | 1.030334 |
| online_logit_market_mean_median_current_rv300_rv600 | median_current_rv300_rv600 | market_mean | 0.147157 | 0.446370 | 0.147550 | 0.447291 | 37015.0000 | 2843 | 0.8121 | True | True | True | True | 0.059896 | 15.1621 | 5 | -0.020516 | 1.029875 |
| online_logit_market_mean_blend_50current_25particle_25rv600 | blend_50current_25particle_25rv600 | market_mean | 0.154402 | 0.473092 | 0.154783 | 0.473937 | 25307.0000 | 3171 | 0.9057 | True | True | False | False | 0.049503 | 4.6712 | 5 | -0.020480 | 1.028011 |
