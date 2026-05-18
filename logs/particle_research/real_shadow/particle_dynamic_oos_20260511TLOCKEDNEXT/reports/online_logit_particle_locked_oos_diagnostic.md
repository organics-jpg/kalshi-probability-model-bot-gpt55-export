# Online Logit Particle Replay Report

- candidate_count: 3501
- source_candidate_count: 3501
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- learning_rate: 0.030000
- l2: 0.001000
- best_by_brier: online_logit_rolling_vol_600s
- best_by_pnl: online_logit_current_calibrated
- promotion_safe: False
- note: Online-logit calibration variants are locked-run diagnostics only. They update only after label_available_ts_utc and do not promote a strategy without a fresh predeclared OOS/shadow run.

| variant | raw_source | brier | log_loss | raw_brier | raw_log_loss | pnl_cents | selected | coverage | beats_raw | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl | updates | final_bias | final_slope |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---:|---:|---:|---:|---:|
| online_logit_particle | particle | 0.460014 | 1.376529 | 0.188032 | 0.562406 | -10033.0000 | 3479 | 0.9937 | False | False | False | False | 0.132329 | -5.0479 | 3501 | 1.578425 | 2.854848 |
| online_logit_current_calibrated | current_calibrated | 0.322206 | 1.042568 | 0.153673 | 0.463382 | 34200.0000 | 3242 | 0.9260 | False | False | False | False | 0.017750 | -11.3916 | 3501 | 0.689090 | 2.845092 |
| online_logit_rolling_vol_300s | rolling_vol_300s | 0.319041 | 0.991310 | 0.150814 | 0.458110 | 12948.0000 | 3212 | 0.9175 | False | False | False | False | 0.060586 | -9.3893 | 3501 | 0.834236 | 3.036261 |
| online_logit_rolling_vol_600s | rolling_vol_600s | 0.285990 | 0.873194 | 0.144880 | 0.437945 | 23685.0000 | 3234 | 0.9237 | False | False | False | False | 0.057594 | -7.0822 | 3501 | 0.809589 | 3.000055 |
| online_logit_median_current_rv300_rv600 | median_current_rv300_rv600 | 0.307255 | 0.947696 | 0.147550 | 0.447291 | 21977.0000 | 3222 | 0.9203 | False | False | False | False | 0.069032 | -10.1952 | 3501 | 0.816991 | 2.958276 |
| online_logit_blend_50current_25particle_25rv600 | blend_50current_25particle_25rv600 | 0.322337 | 0.998602 | 0.154783 | 0.473937 | 7025.0000 | 3240 | 0.9254 | False | False | False | False | 0.063738 | -9.6941 | 3501 | 0.823857 | 3.029077 |
