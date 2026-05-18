# Ensemble Particle Replay Report

- candidate_count: 3501
- source_candidate_count: 3501
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: median_current_rv300_rv600
- best_by_pnl: blend_50rv600_30current_20market
- promotion_safe: False
- note: Ensemble variants are stability diagnostics only. Selecting one from locked-run summaries creates a new hypothesis that still requires a fresh predeclared locked OOS run.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|
| median_current_rv300_rv600 | 0.147550 | 0.447291 | 36184.0000 | 2775 | 0.7926 | 10.3353 | 13.0393 | True | True | True | 0.049129 | 15.1427 |
| mean_current_rv300_rv600 | 0.148887 | 0.451053 | 35465.0000 | 2814 | 0.8038 | 10.1300 | 12.6031 | True | True | True | 0.045805 | 12.9247 |
| blend_40current_30rv300_30rv600 | 0.149269 | 0.451929 | 34921.0000 | 2806 | 0.8015 | 9.9746 | 12.4451 | True | True | True | 0.043629 | 12.2511 |
| blend_50rv600_30current_20market | 0.149507 | 0.448335 | 36220.0000 | 2604 | 0.7438 | 10.3456 | 13.9094 | True | True | True | 0.031829 | 14.7568 |
| blend_40rv600_30rv300_20current_10market | 0.148824 | 0.449664 | 34304.0000 | 2739 | 0.7823 | 9.7983 | 12.5243 | True | True | True | 0.049838 | 13.7260 |
| median_market_current_rv600 | 0.149266 | 0.448097 | 32999.0000 | 2246 | 0.6415 | 9.4256 | 14.6923 | True | True | True | 0.036330 | 16.5365 |
| mean_market_current_rv300_rv600 | 0.150961 | 0.453373 | 33283.0000 | 2630 | 0.7512 | 9.5067 | 12.6551 | True | True | True | 0.030398 | 12.0628 |
| blend_50current_25particle_25rv600 | 0.154783 | 0.473937 | 25366.0000 | 3168 | 0.9049 | 7.2454 | 8.0069 | True | False | False | 0.044704 | 4.6792 |
