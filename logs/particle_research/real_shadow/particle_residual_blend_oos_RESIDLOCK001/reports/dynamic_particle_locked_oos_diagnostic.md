# Dynamic Particle Replay Report

- candidate_count: 3358
- source_candidate_count: 3358
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: rolling_vol_600s
- best_by_pnl: rolling_vol_600s
- promotion_safe: False
- note: Dynamic-vol particles are same-sample diagnostics only. They use only chronological spot observations at or before each decision, but are not promotion-safe until predeclared on fresh locked OOS/shadow data.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl | avg_vol | min_vol | max_vol |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---:|---:|---:|
| rolling_vol_120s | 0.252147 | 0.674580 | -32303.0000 | 2612 | 0.7778 | -9.6197 | -12.3672 | False | False | False | -0.189831 | -19.2869 | 0.3470 | 0.2000 | 0.8973 |
| rolling_vol_300s | 0.250824 | 0.676449 | -28637.0000 | 2485 | 0.7400 | -8.5280 | -11.5239 | False | False | False | -0.275323 | -21.4202 | 0.3448 | 0.2000 | 0.8973 |
| rolling_vol_600s | 0.244702 | 0.660198 | -20084.0000 | 2500 | 0.7445 | -5.9809 | -8.0336 | False | False | False | -0.244804 | -16.6298 | 0.3578 | 0.2426 | 0.8973 |
| rolling_vol_300s_market25 | 0.245950 | 0.661996 | -27457.0000 | 2252 | 0.6706 | -8.1766 | -12.1923 | False | False | False | -0.313304 | -21.0071 | 0.3448 | 0.2000 | 0.8973 |
