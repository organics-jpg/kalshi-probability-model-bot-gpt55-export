# Dynamic Particle Replay Report

- candidate_count: 3398
- source_candidate_count: 3398
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: rolling_vol_300s
- best_by_pnl: rolling_vol_600s
- promotion_safe: False
- note: Dynamic-vol particles are same-sample diagnostics only. They use only chronological spot observations at or before each decision, but are not promotion-safe until predeclared on fresh locked OOS/shadow data.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl | avg_vol | min_vol | max_vol |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---:|---:|---:|
| rolling_vol_120s | 0.161578 | 0.473216 | 33443.0000 | 2957 | 0.8702 | 9.8420 | 11.3098 | True | True | True | 0.039706 | 12.0035 | 0.2582 | 0.2000 | 0.6500 |
| rolling_vol_300s | 0.156740 | 0.459442 | 35150.0000 | 2886 | 0.8493 | 10.3443 | 12.1795 | True | True | True | 0.134767 | 25.3435 | 0.2353 | 0.2000 | 0.6500 |
| rolling_vol_600s | 0.157714 | 0.461933 | 39574.0000 | 2915 | 0.8579 | 11.6463 | 13.5760 | True | True | True | 0.118716 | 20.2388 | 0.2339 | 0.2000 | 0.6500 |
| rolling_vol_300s_market25 | 0.159770 | 0.466042 | 34498.0000 | 2729 | 0.8031 | 10.1524 | 12.6413 | True | True | True | 0.135631 | 24.3906 | 0.2353 | 0.2000 | 0.6500 |
