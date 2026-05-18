# Probability Variant Report

- candidate_count: 4405
- source_candidate_count: 4405
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: market
- best_by_pnl: market
- promotion_safe: False
- note: Fixed variants are same-sample diagnostics only. They are not promotion-safe until predeclared on a fresh locked OOS/shadow sample.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|
| particle | 0.191180 | 0.566730 | -7134.0000 | 4214 | 0.9566 | -1.6195 | -1.6929 | False | False | False | 0.064342 | -11.5817 |
| brownian | 0.191099 | 0.566604 | -6229.0000 | 4227 | 0.9596 | -1.4141 | -1.4736 | False | False | False | 0.066725 | -12.0717 |
| market | 0.145615 | 0.436483 | 0.0000 | 102 | 0.0232 | 0.0000 | 0.0000 | True | False | True | 0.000000 | 0.0000 |
| current_calibrated | 0.171393 | 0.499813 | -30603.0000 | 3519 | 0.7989 | -6.9473 | -8.6965 | True | False | False | -0.061112 | -9.5318 |
| market_current_50_50 | 0.155214 | 0.463853 | -19070.0000 | 2869 | 0.6513 | -4.3292 | -6.6469 | True | False | True | -0.149075 | -9.6416 |
| market_particle_75_25 | 0.150947 | 0.461599 | -14580.0000 | 3678 | 0.8350 | -3.3099 | -3.9641 | True | False | True | -0.033053 | -10.7069 |
| current_particle_75_25 | 0.172136 | 0.509280 | -16842.0000 | 3725 | 0.8456 | -3.8234 | -4.5213 | True | False | False | -0.185251 | -13.3358 |
| market_current_particle_40_40_20 | 0.158554 | 0.478756 | -15310.0000 | 3503 | 0.7952 | -3.4756 | -4.3705 | True | False | True | -0.233490 | -13.0544 |
