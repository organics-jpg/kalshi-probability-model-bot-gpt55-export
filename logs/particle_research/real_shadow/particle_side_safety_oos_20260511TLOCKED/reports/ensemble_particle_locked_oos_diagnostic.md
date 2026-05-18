# Ensemble Particle Replay Report

- candidate_count: 3398
- source_candidate_count: 3398
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- all_candidate_denominator: True
- best_by_brier: median_current_rv300_rv600
- best_by_pnl: median_current_rv300_rv600
- promotion_safe: False
- note: Ensemble variants are stability diagnostics only. Selecting one from locked-run summaries creates a new hypothesis that still requires a fresh predeclared locked OOS run.

| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|
| median_current_rv300_rv600 | 0.157527 | 0.462518 | 38939.0000 | 2916 | 0.8582 | 11.4594 | 13.3536 | True | True | True | 0.110456 | 20.0400 |
| mean_current_rv300_rv600 | 0.158907 | 0.467479 | 32978.0000 | 2888 | 0.8499 | 9.7051 | 11.4190 | True | True | True | 0.087216 | 20.2329 |
| blend_40current_30rv300_30rv600 | 0.159319 | 0.468952 | 32095.0000 | 2871 | 0.8449 | 9.4453 | 11.1790 | True | True | True | 0.077716 | 20.2471 |
| blend_50rv600_30current_20market | 0.161403 | 0.472764 | 31973.0000 | 2730 | 0.8034 | 9.4094 | 11.7117 | True | True | True | 0.074099 | 17.0765 |
| blend_40rv600_30rv300_20current_10market | 0.159337 | 0.467265 | 34931.0000 | 2856 | 0.8405 | 10.2799 | 12.2307 | True | True | True | 0.095843 | 20.3424 |
| median_market_current_rv600 | 0.159951 | 0.469261 | 32505.0000 | 2415 | 0.7107 | 9.5659 | 13.4596 | True | True | True | 0.113894 | 20.5082 |
| mean_market_current_rv300_rv600 | 0.161442 | 0.472264 | 31628.0000 | 2735 | 0.8049 | 9.3078 | 11.5642 | True | True | True | 0.082828 | 19.9847 |
| blend_50current_25particle_25rv600 | 0.164429 | 0.491816 | 23520.0000 | 3024 | 0.8899 | 6.9217 | 7.7778 | True | True | False | 0.018618 | 12.1624 |
