# Dynamic Particle Replay Report

- candidate_count: 556
- source_candidate_count: 663
- skipped_unlabeled_count: 107
- denominator_scope: resolved_labeled_subset
- all_candidate_denominator: True
- best_by_brier: rolling_vol_300s_market25
- best_by_pnl: rolling_vol_120s
- promotion_safe: False
- note: Dynamic-vol particles are same-sample diagnostics only. They use only chronological spot observations at or before each decision, but are not promotion-safe until predeclared on fresh locked OOS/shadow data.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl | avg_vol | min_vol | max_vol |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---:|---:|---:|
| rolling_vol_120s | 0.105027 | 0.348617 | -10290.0000 | 529 | 0.9514 | -18.5072 | -19.4518 | True | False | False | -0.000722 | -18.3813 | 0.3857 | 0.2000 | 1.3462 |
| rolling_vol_300s | 0.112599 | 0.357356 | -10743.0000 | 529 | 0.9514 | -19.3219 | -20.3081 | True | False | False | -0.216161 | -22.8345 | 0.3961 | 0.2479 | 1.3462 |
| rolling_vol_600s | 0.114252 | 0.361407 | -10755.0000 | 535 | 0.9622 | -19.3435 | -20.1028 | True | False | False | -0.197237 | -19.3309 | 0.3964 | 0.2969 | 1.3462 |
| rolling_vol_300s_market25 | 0.100412 | 0.329116 | -10737.0000 | 526 | 0.9460 | -19.3112 | -20.4125 | True | False | False | -0.200654 | -22.8345 | 0.3961 | 0.2479 | 1.3462 |
