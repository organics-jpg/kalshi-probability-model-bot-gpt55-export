# Dynamic Particle Replay Report

- candidate_count: 663
- source_candidate_count: 663
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: rolling_vol_120s
- best_by_pnl: rolling_vol_600s
- promotion_safe: False
- note: Dynamic-vol particles are same-sample diagnostics only. They use only chronological spot observations at or before each decision, but are not promotion-safe until predeclared on fresh locked OOS/shadow data.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl | avg_vol | min_vol | max_vol |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---:|---:|---:|
| rolling_vol_120s | 0.140425 | 0.428648 | -5498.0000 | 625 | 0.9427 | -8.2926 | -8.7968 | True | False | False | -0.090188 | -16.0783 | 0.3846 | 0.2000 | 1.3462 |
| rolling_vol_300s | 0.153183 | 0.449844 | -10210.0000 | 591 | 0.8914 | -15.3997 | -17.2758 | True | False | False | -0.240272 | -22.7892 | 0.3648 | 0.2000 | 1.3462 |
| rolling_vol_600s | 0.147591 | 0.438176 | -5496.0000 | 637 | 0.9608 | -8.2896 | -8.6279 | True | False | False | -0.202000 | -20.1145 | 0.3831 | 0.2969 | 1.3462 |
| rolling_vol_300s_market25 | 0.143137 | 0.426401 | -10204.0000 | 588 | 0.8869 | -15.3906 | -17.3537 | True | False | False | -0.227745 | -22.7892 | 0.3648 | 0.2000 | 1.3462 |
