# Probability Variant Report

- candidate_count: 556
- source_candidate_count: 663
- skipped_unlabeled_count: 107
- denominator_scope: resolved_labeled_subset
- all_candidate_denominator: True
- best_by_brier: market
- best_by_pnl: market
- promotion_safe: False
- note: Fixed variants are same-sample diagnostics only. They are not promotion-safe until predeclared on a fresh locked OOS/shadow sample.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|
| particle | 0.141411 | 0.444365 | -10645.0000 | 544 | 0.9784 | -19.1457 | -19.5680 | True | False | False | 0.194399 | -14.7770 |
| brownian | 0.141626 | 0.444620 | -10882.0000 | 543 | 0.9766 | -19.5719 | -20.0405 | False | False | False | 0.211858 | -14.7626 |
| market | 0.069923 | 0.251250 | 0.0000 | 40 | 0.0719 | 0.0000 | 0.0000 | True | False | True | 0.000000 | 0.0000 |
| current_calibrated | 0.078148 | 0.265943 | -3971.0000 | 345 | 0.6205 | -7.1421 | -11.5101 | True | False | False | -0.211449 | -11.8345 |
| market_current_50_50 | 0.073393 | 0.257787 | -3782.0000 | 276 | 0.4964 | -6.8022 | -13.7029 | True | False | True | -0.349508 | -14.2374 |
| market_particle_75_25 | 0.083280 | 0.295284 | -9022.0000 | 503 | 0.9047 | -16.2266 | -17.9364 | True | False | False | 0.088022 | -13.4245 |
| current_particle_75_25 | 0.089485 | 0.306480 | -7854.0000 | 513 | 0.9227 | -14.1259 | -15.3099 | True | False | False | -0.240245 | -17.7770 |
| market_current_particle_40_40_20 | 0.083262 | 0.291684 | -7953.0000 | 505 | 0.9083 | -14.3040 | -15.7485 | True | False | False | -0.188626 | -17.9856 |
