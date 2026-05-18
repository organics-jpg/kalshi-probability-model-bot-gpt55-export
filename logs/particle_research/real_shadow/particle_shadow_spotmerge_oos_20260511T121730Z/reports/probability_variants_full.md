# Probability Variant Report

- candidate_count: 663
- source_candidate_count: 663
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: market
- best_by_pnl: market
- promotion_safe: False
- note: Fixed variants are same-sample diagnostics only. They are not promotion-safe until predeclared on a fresh locked OOS/shadow sample.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|
| particle | 0.164121 | 0.494932 | -4638.0000 | 649 | 0.9789 | -6.9955 | -7.1464 | True | False | False | -0.008592 | -16.1988 |
| brownian | 0.164457 | 0.495451 | -4775.0000 | 648 | 0.9774 | -7.2021 | -7.3688 | False | False | False | -0.005538 | -15.9036 |
| market | 0.118342 | 0.362547 | 0.0000 | 40 | 0.0603 | 0.0000 | 0.0000 | True | False | True | 0.000000 | 0.0000 |
| current_calibrated | 0.122689 | 0.370620 | -2214.0000 | 437 | 0.6591 | -3.3394 | -5.0664 | True | False | False | -0.093388 | -2.3494 |
| market_current_50_50 | 0.119849 | 0.365503 | -2763.0000 | 338 | 0.5098 | -4.1674 | -8.1746 | True | False | True | -0.192686 | -4.9759 |
| market_particle_75_25 | 0.125785 | 0.391375 | -4543.0000 | 577 | 0.8703 | -6.8522 | -7.8735 | True | False | False | -0.101373 | -13.2651 |
| current_particle_75_25 | 0.129042 | 0.397248 | -4165.0000 | 595 | 0.8974 | -6.2821 | -7.0000 | True | False | False | -0.205432 | -7.0422 |
| market_current_particle_40_40_20 | 0.125394 | 0.387854 | -4398.0000 | 580 | 0.8748 | -6.6335 | -7.5828 | True | False | False | -0.199397 | -11.6386 |
