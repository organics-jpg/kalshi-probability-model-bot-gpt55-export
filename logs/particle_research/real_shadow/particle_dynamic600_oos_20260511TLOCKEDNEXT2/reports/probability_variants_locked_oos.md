# Probability Variant Report

- candidate_count: 3414
- source_candidate_count: 3414
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: market_current_particle_40_40_20
- best_by_pnl: current_particle_75_25
- promotion_safe: False
- note: Fixed variants are same-sample diagnostics only. They are not promotion-safe until predeclared on a fresh locked OOS/shadow sample.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|
| particle | 0.207154 | 0.600086 | 15777.0000 | 3229 | 0.9458 | 4.6213 | 4.8860 | False | False | False | 0.214267 | 13.6686 |
| brownian | 0.206625 | 0.599034 | 15653.0000 | 3229 | 0.9458 | 4.5849 | 4.8476 | False | False | False | 0.224801 | 13.7623 |
| market | 0.200321 | 0.584034 | 0.0000 | 55 | 0.0161 | 0.0000 | 0.0000 | True | False | False | 0.000000 | 0.0000 |
| current_calibrated | 0.199484 | 0.570736 | 10918.0000 | 2632 | 0.7709 | 3.1980 | 4.1482 | True | True | False | -0.030988 | 12.6979 |
| market_current_50_50 | 0.198209 | 0.572368 | 12707.0000 | 2162 | 0.6333 | 3.7220 | 5.8774 | True | True | False | -0.083759 | 14.7518 |
| market_particle_75_25 | 0.195028 | 0.565147 | 18770.0000 | 2769 | 0.8111 | 5.4979 | 6.7786 | True | True | True | 0.043032 | 12.9778 |
| current_particle_75_25 | 0.195874 | 0.563852 | 19064.0000 | 3047 | 0.8925 | 5.5841 | 6.2566 | True | True | True | 0.012836 | 20.1827 |
| market_current_particle_40_40_20 | 0.194923 | 0.563065 | 17962.0000 | 2894 | 0.8477 | 5.2613 | 6.2066 | True | True | True | 0.005992 | 19.1885 |
