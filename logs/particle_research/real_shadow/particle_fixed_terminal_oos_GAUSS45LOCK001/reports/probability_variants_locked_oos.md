# Probability Variant Report

- candidate_count: 2514
- source_candidate_count: 2514
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: particle
- best_by_pnl: particle
- promotion_safe: False
- note: Fixed variants are same-sample diagnostics only. They are not promotion-safe until predeclared on a fresh locked OOS/shadow sample.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|
| particle | 0.226789 | 0.631705 | 50400.0000 | 2416 | 0.9610 | 20.0477 | 20.8609 | True | True | True | 0.179358 | 21.0811 |
| brownian | 0.226938 | 0.632020 | 50272.0000 | 2422 | 0.9634 | 19.9968 | 20.7564 | False | True | True | 0.188858 | 21.1129 |
| market | 0.268521 | 0.746376 | 0.0000 | 108 | 0.0430 | 0.0000 | 0.0000 | False | False | True | 0.000000 | 0.0000 |
| current_calibrated | 0.274996 | 0.757211 | -6737.0000 | 1737 | 0.6909 | -2.6798 | -3.8785 | False | False | False | -0.123935 | -2.8188 |
| market_current_50_50 | 0.271216 | 0.748053 | -2026.0000 | 1228 | 0.4885 | -0.8059 | -1.6498 | False | False | True | -0.222628 | 1.8458 |
| market_particle_75_25 | 0.254280 | 0.694239 | 49901.0000 | 2113 | 0.8405 | 19.8492 | 23.6162 | False | True | True | 0.067057 | 20.3275 |
| current_particle_75_25 | 0.259683 | 0.707132 | 28261.0000 | 2110 | 0.8393 | 11.2414 | 13.3938 | False | True | True | -0.034961 | 17.5914 |
| market_current_particle_40_40_20 | 0.259402 | 0.707512 | 33826.0000 | 2027 | 0.8063 | 13.4551 | 16.6877 | False | True | True | -0.042631 | 18.9571 |
