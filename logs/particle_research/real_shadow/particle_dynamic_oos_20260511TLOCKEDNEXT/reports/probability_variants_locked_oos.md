# Probability Variant Report

- candidate_count: 3501
- source_candidate_count: 3501
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: current_calibrated
- best_by_pnl: current_calibrated
- promotion_safe: False
- note: Fixed variants are same-sample diagnostics only. They are not promotion-safe until predeclared on a fresh locked OOS/shadow sample.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|
| particle | 0.188032 | 0.562406 | 15798.0000 | 3275 | 0.9354 | 4.5124 | 4.8238 | True | False | False | 0.093831 | -2.8779 |
| brownian | 0.188085 | 0.562539 | 15595.0000 | 3290 | 0.9397 | 4.4544 | 4.7401 | False | False | False | 0.107784 | -2.7078 |
| market | 0.160965 | 0.465813 | 0.0000 | 170 | 0.0486 | 0.0000 | 0.0000 | True | False | False | 0.000000 | 0.0000 |
| current_calibrated | 0.153673 | 0.463382 | 32996.0000 | 2806 | 0.8015 | 9.4247 | 11.7591 | True | True | False | 0.007598 | 3.8516 |
| market_current_50_50 | 0.155985 | 0.461901 | 25130.0000 | 2237 | 0.6390 | 7.1779 | 11.2338 | True | True | False | -0.042124 | 3.1689 |
| market_particle_75_25 | 0.161426 | 0.482371 | 11724.0000 | 2646 | 0.7558 | 3.3488 | 4.4308 | True | False | False | -0.076802 | -2.9304 |
| current_particle_75_25 | 0.157055 | 0.479923 | 23696.0000 | 3197 | 0.9132 | 6.7684 | 7.4119 | True | False | False | 0.027031 | 2.2854 |
| market_current_particle_40_40_20 | 0.157695 | 0.475836 | 17273.0000 | 2906 | 0.8300 | 4.9337 | 5.9439 | True | False | False | -0.006309 | 0.1096 |
