# Ensemble Particle Replay Report

- candidate_count: 3414
- source_candidate_count: 3414
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: blend_50current_25particle_25rv600
- best_by_pnl: blend_50current_25particle_25rv600
- promotion_safe: False
- note: Ensemble variants are stability diagnostics only. Selecting one from locked-run summaries creates a new hypothesis that still requires a fresh predeclared locked OOS run.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|
| median_current_rv300_rv600 | 0.201324 | 0.576397 | 6789.0000 | 2737 | 0.8017 | 1.9886 | 2.4805 | True | False | False | -0.075386 | 16.4028 |
| mean_current_rv300_rv600 | 0.200793 | 0.575322 | 10887.0000 | 2671 | 0.7824 | 3.1889 | 4.0760 | True | False | False | -0.086902 | 14.5457 |
| blend_40current_30rv300_30rv600 | 0.200578 | 0.574675 | 11847.0000 | 2641 | 0.7736 | 3.4701 | 4.4858 | True | False | False | -0.090644 | 15.0047 |
| blend_50rv600_30current_20market | 0.199658 | 0.573397 | 11084.0000 | 2507 | 0.7343 | 3.2466 | 4.4212 | True | True | False | -0.124728 | 14.4953 |
| blend_40rv600_30rv300_20current_10market | 0.200512 | 0.575282 | 9195.0000 | 2625 | 0.7689 | 2.6933 | 3.5029 | True | False | False | -0.101918 | 14.3724 |
| median_market_current_rv600 | 0.202550 | 0.580464 | 5888.0000 | 2088 | 0.6116 | 1.7247 | 2.8199 | True | False | False | -0.185304 | 10.2927 |
| mean_market_current_rv300_rv600 | 0.199428 | 0.573465 | 10445.0000 | 2480 | 0.7264 | 3.0595 | 4.2117 | True | True | False | -0.121873 | 14.8208 |
| blend_50current_25particle_25rv600 | 0.196802 | 0.566467 | 17027.0000 | 3072 | 0.8998 | 4.9874 | 5.5426 | True | True | True | 0.017806 | 19.7892 |
