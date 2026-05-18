# Dynamic Particle Replay Report

- candidate_count: 3260
- source_candidate_count: 3260
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: rolling_vol_300s_market25
- best_by_pnl: rolling_vol_300s_market25
- promotion_safe: False
- note: Dynamic-vol particles are same-sample diagnostics only. They use only chronological spot observations at or before each decision, but are not promotion-safe until predeclared on fresh locked OOS/shadow data.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl | avg_vol | min_vol | max_vol |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---:|---:|---:|
| rolling_vol_120s | 0.086034 | 0.296263 | -4659.0000 | 2505 | 0.7684 | -1.4291 | -1.8599 | True | False | False | -0.248673 | -9.9399 | 0.4166 | 0.2000 | 0.8110 |
| rolling_vol_300s | 0.084449 | 0.292237 | -4320.0000 | 2442 | 0.7491 | -1.3252 | -1.7690 | True | False | False | -0.234182 | -5.7693 | 0.4067 | 0.2000 | 0.6839 |
| rolling_vol_600s | 0.084460 | 0.289691 | -8207.0000 | 2470 | 0.7577 | -2.5175 | -3.3227 | True | False | False | -0.182681 | -2.8883 | 0.4008 | 0.2000 | 0.6500 |
| rolling_vol_300s_market25 | 0.082911 | 0.287231 | -3848.0000 | 2290 | 0.7025 | -1.1804 | -1.6803 | True | False | False | -0.279980 | -5.8380 | 0.4067 | 0.2000 | 0.6839 |
