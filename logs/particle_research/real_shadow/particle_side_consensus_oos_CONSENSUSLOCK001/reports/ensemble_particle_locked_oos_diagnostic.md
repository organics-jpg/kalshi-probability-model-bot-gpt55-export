# Ensemble Particle Replay Report

- candidate_count: 3260
- source_candidate_count: 3260
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: blend_40current_30rv300_30rv600
- best_by_pnl: blend_40current_30rv300_30rv600
- promotion_safe: False
- note: Ensemble variants are stability diagnostics only. Selecting one from locked-run summaries creates a new hypothesis that still requires a fresh predeclared locked OOS run.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|
| median_current_rv300_rv600 | 0.081372 | 0.281030 | 3158.0000 | 2446 | 0.7503 | 0.9687 | 1.2911 | True | False | False | -0.120505 | -0.8172 |
| mean_current_rv300_rv600 | 0.075891 | 0.264439 | 13179.0000 | 2474 | 0.7589 | 4.0426 | 5.3270 | True | True | False | 0.051979 | 7.6319 |
| blend_40current_30rv300_30rv600 | 0.074407 | 0.259362 | 17149.0000 | 2428 | 0.7448 | 5.2604 | 7.0630 | True | True | False | 0.116318 | 9.9988 |
| blend_50rv600_30current_20market | 0.075656 | 0.262775 | 15176.0000 | 2207 | 0.6770 | 4.6552 | 6.8763 | True | True | False | 0.102394 | 7.2258 |
| blend_40rv600_30rv300_20current_10market | 0.078479 | 0.272803 | 6899.0000 | 2378 | 0.7294 | 2.1163 | 2.9012 | True | True | False | -0.064176 | 2.8172 |
| median_market_current_rv600 | 0.077049 | 0.264523 | 10491.0000 | 1144 | 0.3509 | 3.2181 | 9.1705 | True | True | False | 0.442280 | 12.0319 |
| mean_market_current_rv300_rv600 | 0.076526 | 0.266384 | 12368.0000 | 2266 | 0.6951 | 3.7939 | 5.4581 | True | True | False | 0.021807 | 6.5485 |
| blend_50current_25particle_25rv600 | 0.075618 | 0.268345 | 15056.0000 | 2578 | 0.7908 | 4.6184 | 5.8402 | True | True | False | -0.025902 | 5.7288 |
