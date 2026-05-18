# Probability Variant Report

- candidate_count: 3260
- source_candidate_count: 3260
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: current_calibrated
- best_by_pnl: current_calibrated
- promotion_safe: False
- note: Fixed variants are same-sample diagnostics only. They are not promotion-safe until predeclared on a fresh locked OOS/shadow sample.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|
| particle | 0.108039 | 0.367319 | -32502.0000 | 3029 | 0.9291 | -9.9699 | -10.7303 | False | False | False | -0.011048 | -6.5460 |
| brownian | 0.107891 | 0.367085 | -33071.0000 | 3062 | 0.9393 | -10.1445 | -10.8005 | False | False | False | 0.015718 | -6.8883 |
| market | 0.080857 | 0.275450 | 0.0000 | 202 | 0.0620 | 0.0000 | 0.0000 | True | False | False | 0.000000 | 0.0000 |
| current_calibrated | 0.064114 | 0.216941 | 36023.0000 | 2664 | 0.8172 | 11.0500 | 13.5221 | True | True | False | 0.441408 | 18.6393 |
| market_current_50_50 | 0.070414 | 0.243663 | 32484.0000 | 2231 | 0.6844 | 9.9644 | 14.5603 | True | True | False | 0.514319 | 18.3472 |
| market_particle_75_25 | 0.085486 | 0.296407 | -25673.0000 | 2353 | 0.7218 | -7.8752 | -10.9108 | True | False | False | -0.294462 | -6.3166 |
| current_particle_75_25 | 0.070421 | 0.250218 | 25907.0000 | 2636 | 0.8086 | 7.9469 | 9.8281 | True | True | False | 0.164715 | 16.0184 |
| market_current_particle_40_40_20 | 0.075352 | 0.266127 | 16376.0000 | 2232 | 0.6847 | 5.0233 | 7.3369 | True | True | False | 0.000162 | 8.2847 |
