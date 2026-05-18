# Ensemble Particle Replay Report

- candidate_count: 3358
- source_candidate_count: 3358
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: blend_50current_25particle_25rv600
- best_by_pnl: blend_50current_25particle_25rv600
- promotion_safe: False
- note: Ensemble variants are stability diagnostics only. Selecting one from locked-run summaries creates a new hypothesis that still requires a fresh predeclared locked OOS run.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|
| median_current_rv300_rv600 | 0.244126 | 0.657723 | -23094.0000 | 2370 | 0.7058 | -6.8773 | -9.7443 | False | False | False | -0.285327 | -17.2929 |
| mean_current_rv300_rv600 | 0.245020 | 0.661245 | -25013.0000 | 2365 | 0.7043 | -7.4488 | -10.5763 | False | False | False | -0.278689 | -18.8452 |
| blend_40current_30rv300_30rv600 | 0.244613 | 0.660231 | -25091.0000 | 2352 | 0.7004 | -7.4720 | -10.6679 | False | False | False | -0.262994 | -16.4345 |
| blend_50rv600_30current_20market | 0.240762 | 0.649694 | -20785.0000 | 2225 | 0.6626 | -6.1897 | -9.3416 | False | False | True | -0.269418 | -12.6631 |
| blend_40rv600_30rv300_20current_10market | 0.244047 | 0.658230 | -25264.0000 | 2360 | 0.7028 | -7.5235 | -10.7051 | False | False | False | -0.302985 | -19.2964 |
| median_market_current_rv600 | 0.241830 | 0.651661 | -21534.0000 | 1591 | 0.4738 | -6.4127 | -13.5349 | False | False | True | -0.375306 | -18.1393 |
| mean_market_current_rv300_rv600 | 0.241750 | 0.651720 | -22430.0000 | 2112 | 0.6289 | -6.6796 | -10.6203 | False | False | True | -0.314535 | -18.1512 |
| blend_50current_25particle_25rv600 | 0.233889 | 0.638027 | 5655.0000 | 2499 | 0.7442 | 1.6840 | 2.2629 | False | False | True | -0.109170 | 2.0440 |
