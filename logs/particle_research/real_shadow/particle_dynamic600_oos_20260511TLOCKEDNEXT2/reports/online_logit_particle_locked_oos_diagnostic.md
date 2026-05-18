# Online Logit Particle Replay Report

- candidate_count: 3414
- source_candidate_count: 3414
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- learning_rate: 0.030000
- l2: 0.001000
- best_by_brier: online_logit_particle
- best_by_pnl: online_logit_particle
- promotion_safe: False
- note: Online-logit calibration variants are locked-run diagnostics only. They update only after label_available_ts_utc and do not promote a strategy without a fresh predeclared OOS/shadow run.

| variant | raw_source | brier | log_loss | raw_brier | raw_log_loss | pnl_cents | selected | coverage | beats_raw | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl | updates | final_bias | final_slope |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---:|---:|---:|---:|---:|
| online_logit_particle | particle | 0.153412 | 0.527576 | 0.207154 | 0.600086 | 86280.0000 | 3112 | 0.9115 | True | True | True | True | 0.340001 | 16.7963 | 3414 | -0.754110 | 1.433491 |
| online_logit_current_calibrated | current_calibrated | 0.191265 | 0.595483 | 0.199484 | 0.570736 | 56692.0000 | 2981 | 0.8732 | False | True | False | False | 0.355812 | 18.6557 | 3414 | -0.302691 | 2.371683 |
| online_logit_rolling_vol_300s | rolling_vol_300s | 0.188976 | 0.600078 | 0.202030 | 0.579268 | 64009.0000 | 3020 | 0.8846 | False | False | False | False | 0.325843 | 17.9543 | 3414 | -0.492952 | 2.295528 |
| online_logit_rolling_vol_600s | rolling_vol_600s | 0.188631 | 0.597292 | 0.202355 | 0.579325 | 62860.0000 | 3002 | 0.8793 | False | True | False | False | 0.339465 | 18.3009 | 3414 | -0.422248 | 2.282298 |
| online_logit_median_current_rv300_rv600 | median_current_rv300_rv600 | 0.188673 | 0.596688 | 0.201324 | 0.576397 | 62854.0000 | 3004 | 0.8799 | False | True | False | False | 0.338264 | 18.2119 | 3414 | -0.424927 | 2.301291 |
| online_logit_blend_50current_25particle_25rv600 | blend_50current_25particle_25rv600 | 0.180842 | 0.573164 | 0.196802 | 0.566467 | 76494.0000 | 3056 | 0.8951 | False | True | True | False | 0.302333 | 18.1323 | 3414 | -0.451983 | 2.240446 |
