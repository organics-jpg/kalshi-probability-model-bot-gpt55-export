# Probability Variant Report

- candidate_count: 4512
- source_candidate_count: 4512
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: current_calibrated
- best_by_pnl: current_calibrated
- promotion_safe: False
- note: Fixed variants are same-sample diagnostics only. They are not promotion-safe until predeclared on a fresh locked OOS/shadow sample.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|
| particle | 0.166918 | 0.516681 | -2384.0000 | 4379 | 0.9705 | -0.5284 | -0.5444 | True | False | False | 0.170948 | -6.2225 |
| brownian | 0.166997 | 0.516914 | -2597.0000 | 4373 | 0.9692 | -0.5756 | -0.5939 | False | False | False | 0.176848 | -6.2438 |
| market | 0.127912 | 0.386150 | 0.0000 | 96 | 0.0213 | 0.0000 | 0.0000 | True | False | False | 0.000000 | 0.0000 |
| current_calibrated | 0.122272 | 0.374592 | 28435.0000 | 3503 | 0.7764 | 6.3021 | 8.1173 | True | True | False | 0.115516 | 10.5762 |
| market_current_50_50 | 0.124338 | 0.378806 | 23763.0000 | 2719 | 0.6026 | 5.2666 | 8.7396 | True | True | False | 0.068510 | 8.8652 |
| market_particle_75_25 | 0.131006 | 0.411032 | -3005.0000 | 3912 | 0.8670 | -0.6660 | -0.7681 | True | False | False | 0.033262 | -5.9264 |
| current_particle_75_25 | 0.126192 | 0.400507 | 21086.0000 | 3792 | 0.8404 | 4.6733 | 5.5607 | True | False | False | -0.124826 | 1.2943 |
| market_current_particle_40_40_20 | 0.127044 | 0.399305 | 13976.0000 | 3626 | 0.8036 | 3.0975 | 3.8544 | True | False | False | -0.151203 | -1.1339 |
