# Online Logit Particle Replay Report

- candidate_count: 3398
- source_candidate_count: 3398
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- learning_rate: 0.030000
- l2: 0.001000
- best_by_brier: online_logit_rolling_vol_600s
- best_by_pnl: online_logit_particle
- promotion_safe: False
- note: Online-logit calibration variants are locked-run diagnostics only. They update only after label_available_ts_utc and do not promote a strategy without a fresh predeclared OOS/shadow run.

| variant | raw_source | brier | log_loss | raw_brier | raw_log_loss | pnl_cents | selected | coverage | beats_raw | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl | updates | final_bias | final_slope |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---:|---:|---:|---:|---:|
| online_logit_particle | particle | 0.409792 | 1.184931 | 0.186131 | 0.555235 | 3174.0000 | 3313 | 0.9750 | False | False | False | False | -0.003585 | -8.0965 | 3398 | -3.468589 | 2.740057 |
| online_logit_current_calibrated | current_calibrated | 0.408177 | 1.201550 | 0.163866 | 0.483483 | -62884.0000 | 3285 | 0.9667 | False | False | False | False | 0.118104 | -4.6624 | 3398 | -3.588167 | 1.331718 |
| online_logit_rolling_vol_300s | rolling_vol_300s | 0.392466 | 1.150103 | 0.156740 | 0.459442 | -48232.0000 | 3151 | 0.9273 | False | False | False | False | 0.012387 | -3.7471 | 3398 | -3.499487 | 1.586953 |
| online_logit_rolling_vol_600s | rolling_vol_600s | 0.388830 | 1.148324 | 0.157714 | 0.461933 | -50170.0000 | 3203 | 0.9426 | False | False | False | False | 0.019774 | -1.8012 | 3398 | -3.561264 | 1.457077 |
| online_logit_median_current_rv300_rv600 | median_current_rv300_rv600 | 0.391342 | 1.150486 | 0.157527 | 0.462518 | -50247.0000 | 3199 | 0.9414 | False | False | False | False | 0.026339 | -2.0212 | 3398 | -3.547373 | 1.507467 |
| online_logit_blend_50current_25particle_25rv600 | blend_50current_25particle_25rv600 | 0.410847 | 1.176551 | 0.164429 | 0.491816 | -58684.0000 | 3244 | 0.9547 | False | False | False | False | 0.120536 | -5.7365 | 3398 | -3.580724 | 1.820781 |
