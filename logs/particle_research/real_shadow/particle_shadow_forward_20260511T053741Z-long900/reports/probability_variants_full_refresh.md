# Probability Variant Report

- candidate_count: 753
- source_candidate_count: 753
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: market
- best_by_pnl: market
- promotion_safe: False
- note: Fixed variants are same-sample diagnostics only. They are not promotion-safe until predeclared on a fresh locked OOS/shadow sample.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|
| particle | 0.169104 | 0.516314 | -4876.0000 | 676 | 0.8977 | -6.4754 | -7.2130 | False | False | False | 0.016009 | -4.2910 |
| brownian | 0.169000 | 0.516154 | -4899.0000 | 663 | 0.8805 | -6.5060 | -7.3891 | False | False | False | 0.006025 | -3.9841 |
| market | 0.120628 | 0.362241 | 0.0000 | 36 | 0.0478 | 0.0000 | 0.0000 | True | False | True | 0.000000 | 0.0000 |
| current_calibrated | 0.135689 | 0.420971 | -3874.0000 | 636 | 0.8446 | -5.1448 | -6.0912 | True | False | False | -0.257051 | -11.8571 |
| market_current_50_50 | 0.126774 | 0.390282 | -3532.0000 | 578 | 0.7676 | -4.6906 | -6.1107 | True | False | True | -0.339165 | -8.6243 |
| market_particle_75_25 | 0.127705 | 0.396600 | -4694.0000 | 536 | 0.7118 | -6.2337 | -8.7575 | True | False | True | -0.245783 | -4.0423 |
| current_particle_75_25 | 0.142239 | 0.443225 | -4290.0000 | 643 | 0.8539 | -5.6972 | -6.6719 | True | False | False | -0.150728 | -7.9577 |
| market_current_particle_40_40_20 | 0.132541 | 0.413219 | -4332.0000 | 591 | 0.7849 | -5.7530 | -7.3299 | True | False | True | -0.216197 | -6.7937 |
