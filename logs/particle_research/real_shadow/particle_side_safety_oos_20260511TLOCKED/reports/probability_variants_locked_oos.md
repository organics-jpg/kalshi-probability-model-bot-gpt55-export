# Probability Variant Report

- candidate_count: 3398
- source_candidate_count: 3398
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: current_calibrated
- best_by_pnl: current_calibrated
- promotion_safe: False
- note: Fixed variants are same-sample diagnostics only. They are not promotion-safe until predeclared on a fresh locked OOS/shadow sample.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|
| particle | 0.186131 | 0.555235 | 14916.0000 | 3111 | 0.9155 | 4.3896 | 4.7946 | True | False | False | 0.074278 | 2.0035 |
| brownian | 0.186462 | 0.555982 | 15483.0000 | 3106 | 0.9141 | 4.5565 | 4.9849 | False | False | False | 0.069536 | 2.4788 |
| market | 0.172172 | 0.492897 | 0.0000 | 115 | 0.0338 | 0.0000 | 0.0000 | True | False | False | 0.000000 | 0.0000 |
| current_calibrated | 0.163866 | 0.483483 | 25198.0000 | 2918 | 0.8587 | 7.4155 | 8.6354 | True | True | False | 0.020283 | 9.7259 |
| market_current_50_50 | 0.166618 | 0.485646 | 23147.0000 | 2372 | 0.6981 | 6.8119 | 9.7584 | True | True | False | -0.040430 | 8.9165 |
| market_particle_75_25 | 0.171093 | 0.502129 | 8419.0000 | 2553 | 0.7513 | 2.4776 | 3.2977 | True | False | False | -0.069296 | -1.7941 |
| current_particle_75_25 | 0.166575 | 0.497837 | 22619.0000 | 2994 | 0.8811 | 6.6566 | 7.5548 | True | False | False | -0.008089 | 7.9718 |
| market_current_particle_40_40_20 | 0.167576 | 0.495800 | 18452.0000 | 2746 | 0.8081 | 5.4303 | 6.7196 | True | False | False | -0.051376 | 7.1141 |
