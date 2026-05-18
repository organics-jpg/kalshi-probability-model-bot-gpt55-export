# Probability Variant Report

- candidate_count: 4843
- source_candidate_count: 4843
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: brownian
- best_by_pnl: market_particle_75_25
- promotion_safe: False
- note: Fixed variants are same-sample diagnostics only. They are not promotion-safe until predeclared on a fresh locked OOS/shadow sample.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|
| particle | 0.240375 | 0.674358 | 47336.0000 | 4574 | 0.9445 | 9.7741 | 10.3489 | False | True | True | 0.268068 | 19.2915 |
| brownian | 0.240082 | 0.673718 | 48412.0000 | 4582 | 0.9461 | 9.9963 | 10.5657 | False | True | True | 0.274386 | 19.7622 |
| market | 0.256284 | 0.747331 | 0.0000 | 103 | 0.0213 | 0.0000 | 0.0000 | False | False | True | 0.000000 | 0.0000 |
| current_calibrated | 0.267632 | 0.799026 | -33331.0000 | 3863 | 0.7976 | -6.8823 | -8.6283 | False | False | False | -0.096113 | -8.2667 |
| market_current_50_50 | 0.261076 | 0.767653 | -27128.0000 | 2844 | 0.5872 | -5.6015 | -9.5387 | False | False | True | -0.182692 | -5.6135 |
| market_particle_75_25 | 0.248488 | 0.706955 | 53017.0000 | 3728 | 0.7698 | 10.9471 | 14.2213 | False | True | True | 0.093519 | 20.1032 |
| current_particle_75_25 | 0.257274 | 0.737867 | 11450.0000 | 3889 | 0.8030 | 2.3642 | 2.9442 | False | False | True | -0.033008 | 5.2023 |
| market_current_particle_40_40_20 | 0.253935 | 0.727711 | 28104.0000 | 3490 | 0.7206 | 5.8030 | 8.0527 | False | True | True | -0.064644 | 9.8233 |
