# Dynamic Particle Replay Report

- candidate_count: 3501
- source_candidate_count: 3501
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: rolling_vol_600s
- best_by_pnl: rolling_vol_600s
- promotion_safe: False
- note: Dynamic-vol particles are same-sample diagnostics only. They use only chronological spot observations at or before each decision, but are not promotion-safe until predeclared on fresh locked OOS/shadow data.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl | avg_vol | min_vol | max_vol |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---:|---:|---:|
| rolling_vol_120s | 0.162543 | 0.491293 | 27329.0000 | 2854 | 0.8152 | 7.8061 | 9.5757 | True | False | False | -0.019939 | 1.7021 | 0.2941 | 0.2000 | 0.6500 |
| rolling_vol_300s | 0.150814 | 0.458110 | 32406.0000 | 2852 | 0.8146 | 9.2562 | 11.3626 | True | True | True | 0.038545 | 15.7888 | 0.2539 | 0.2000 | 0.6500 |
| rolling_vol_600s | 0.144880 | 0.437945 | 38107.0000 | 2816 | 0.8043 | 10.8846 | 13.5323 | True | True | True | 0.075322 | 20.1735 | 0.2280 | 0.2000 | 0.6500 |
| rolling_vol_300s_market25 | 0.151990 | 0.458312 | 29408.0000 | 2667 | 0.7618 | 8.3999 | 11.0266 | True | True | True | 0.021618 | 14.5308 | 0.2539 | 0.2000 | 0.6500 |
