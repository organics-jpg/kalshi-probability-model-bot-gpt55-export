# Online Logit Particle Replay Report

- candidate_count: 3260
- source_candidate_count: 3260
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- learning_rate: 0.030000
- l2: 0.001000
- update_mode: candidate
- best_by_brier: online_logit_current_calibrated
- best_by_pnl: online_logit_current_calibrated
- promotion_safe: False
- note: Online-logit calibration variants are locked-run diagnostics only. They update only after label_available_ts_utc and do not promote a strategy without a fresh predeclared OOS/shadow run.

| variant | raw_source | update_mode | brier | log_loss | raw_brier | raw_log_loss | pnl_cents | selected | coverage | beats_raw | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl | updates | final_bias | final_slope |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---:|---:|---:|---:|---:|
| online_logit_particle | particle | candidate | 0.170675 | 0.476935 | 0.108039 | 0.367319 | -9072.0000 | 3050 | 0.9356 | False | False | False | False | -0.011277 | -5.2957 | 3260 | -0.653123 | 3.355333 |
| online_logit_current_calibrated | current_calibrated | candidate | 0.090039 | 0.250477 | 0.064114 | 0.216941 | 12528.0000 | 2776 | 0.8515 | False | True | False | False | 0.448952 | 17.1755 | 3260 | -1.676192 | 2.923659 |
| online_logit_rolling_vol_300s | rolling_vol_300s | candidate | 0.125339 | 0.351238 | 0.084449 | 0.292237 | -7631.0000 | 2865 | 0.8788 | False | False | False | False | 0.198151 | 11.6245 | 3260 | -1.098126 | 3.122995 |
| online_logit_rolling_vol_600s | rolling_vol_600s | candidate | 0.125176 | 0.355258 | 0.084460 | 0.289691 | -7116.0000 | 2895 | 0.8880 | False | False | False | False | 0.207036 | 11.1521 | 3260 | -0.835500 | 3.098469 |
| online_logit_median_current_rv300_rv600 | median_current_rv300_rv600 | candidate | 0.121522 | 0.341097 | 0.081372 | 0.281030 | -7018.0000 | 2855 | 0.8758 | False | False | False | False | 0.214139 | 12.1853 | 3260 | -1.086507 | 3.124752 |
| online_logit_blend_50current_25particle_25rv600 | blend_50current_25particle_25rv600 | candidate | 0.110104 | 0.308036 | 0.075618 | 0.268345 | -4696.0000 | 2927 | 0.8979 | False | False | False | False | 0.235558 | 16.2160 | 3260 | -1.259613 | 3.165430 |
