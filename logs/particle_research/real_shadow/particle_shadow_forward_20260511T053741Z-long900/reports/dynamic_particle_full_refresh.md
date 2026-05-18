# Dynamic Particle Replay Report

- candidate_count: 753
- source_candidate_count: 753
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: rolling_vol_300s_market25
- best_by_pnl: rolling_vol_120s
- promotion_safe: False
- note: Dynamic-vol particles are same-sample diagnostics only. They use only chronological spot observations at or before each decision, but are not promotion-safe until predeclared on fresh locked OOS/shadow data.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl | avg_vol | min_vol | max_vol |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---:|---:|---:|
| rolling_vol_120s | 0.132704 | 0.387010 | -8669.0000 | 514 | 0.6826 | -11.5126 | -16.8658 | True | False | True | -0.275918 | -15.4550 | 0.2337 | 0.2000 | 0.6500 |
| rolling_vol_300s | 0.132754 | 0.386825 | -9477.0000 | 494 | 0.6560 | -12.5857 | -19.1842 | True | False | True | -0.317216 | -23.3915 | 0.2263 | 0.2000 | 0.6500 |
| rolling_vol_600s | 0.138504 | 0.399421 | -11648.0000 | 489 | 0.6494 | -15.4688 | -23.8200 | True | False | False | -0.369323 | -27.9947 | 0.2248 | 0.2000 | 0.6500 |
| rolling_vol_300s_market25 | 0.129443 | 0.380267 | -8781.0000 | 410 | 0.5445 | -11.6614 | -21.4171 | True | False | True | -0.445960 | -22.6878 | 0.2263 | 0.2000 | 0.6500 |
