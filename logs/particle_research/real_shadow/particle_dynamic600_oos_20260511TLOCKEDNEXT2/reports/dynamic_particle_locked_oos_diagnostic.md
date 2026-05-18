# Dynamic Particle Replay Report

- candidate_count: 3414
- source_candidate_count: 3414
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: rolling_vol_300s_market25
- best_by_pnl: rolling_vol_300s
- promotion_safe: False
- note: Dynamic-vol particles are same-sample diagnostics only. They use only chronological spot observations at or before each decision, but are not promotion-safe until predeclared on fresh locked OOS/shadow data.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl | avg_vol | min_vol | max_vol |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---:|---:|---:|
| rolling_vol_120s | 0.202549 | 0.580494 | 6013.0000 | 2866 | 0.8395 | 1.7613 | 2.0980 | True | False | False | -0.069198 | 12.1136 | 0.2396 | 0.2000 | 0.6614 |
| rolling_vol_300s | 0.202030 | 0.579268 | 8733.0000 | 2812 | 0.8237 | 2.5580 | 3.1056 | True | False | False | -0.056299 | 13.9895 | 0.2247 | 0.2000 | 0.6500 |
| rolling_vol_600s | 0.202355 | 0.579325 | 4575.0000 | 2740 | 0.8026 | 1.3401 | 1.6697 | True | False | False | -0.082977 | 12.9204 | 0.2156 | 0.2000 | 0.6500 |
| rolling_vol_300s_market25 | 0.200179 | 0.575945 | 7200.0000 | 2669 | 0.7818 | 2.1090 | 2.6976 | True | True | False | -0.072872 | 14.8431 | 0.2247 | 0.2000 | 0.6500 |
