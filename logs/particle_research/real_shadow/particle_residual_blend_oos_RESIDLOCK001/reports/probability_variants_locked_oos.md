# Probability Variant Report

- candidate_count: 3358
- source_candidate_count: 3358
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: brownian
- best_by_pnl: brownian
- promotion_safe: False
- note: Fixed variants are same-sample diagnostics only. They are not promotion-safe until predeclared on a fresh locked OOS/shadow sample.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|
| particle | 0.217047 | 0.611439 | 60332.0000 | 3045 | 0.9068 | 17.9666 | 19.8135 | False | True | True | 0.000473 | -1.0202 |
| brownian | 0.216843 | 0.611025 | 60889.0000 | 3051 | 0.9086 | 18.1325 | 19.9571 | False | True | True | 0.008830 | -1.7881 |
| market | 0.233343 | 0.628180 | 0.0000 | 96 | 0.0286 | 0.0000 | 0.0000 | False | False | True | 0.000000 | 0.0000 |
| current_calibrated | 0.242148 | 0.654385 | -24387.0000 | 2512 | 0.7481 | -7.2624 | -9.7082 | False | False | False | -0.095658 | -7.1274 |
| market_current_50_50 | 0.236943 | 0.638772 | -15401.0000 | 1874 | 0.5581 | -4.5864 | -8.2182 | False | False | True | -0.131884 | -5.7131 |
| market_particle_75_25 | 0.227065 | 0.619711 | 41763.0000 | 2314 | 0.6891 | 12.4369 | 18.0480 | False | True | True | -0.134284 | -2.4274 |
| current_particle_75_25 | 0.233302 | 0.636449 | 3479.0000 | 2521 | 0.7507 | 1.0360 | 1.3800 | False | False | True | -0.067265 | 5.3440 |
| market_current_particle_40_40_20 | 0.231055 | 0.628904 | 17059.0000 | 2037 | 0.6066 | 5.0801 | 8.3746 | False | False | True | -0.167950 | 4.3274 |
