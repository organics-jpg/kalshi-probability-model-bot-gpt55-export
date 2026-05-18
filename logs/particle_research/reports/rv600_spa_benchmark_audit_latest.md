# RV600 SPA Benchmark Audit

- generated_utc: 2026-05-15T21:21:18+00:00
- research_only: True
- decision: spa_benchmark_rejects_current_grid
- root_count: 40
- candidate_count: 7482
- positive_delta_candidate_count: 2890
- spa_screen_candidate_count: 0

## Best By SPA Statistic

- variant: `rv600_primary_max_2_entries_late_70_300_ev6`
- accounting_mode: `all_entries`
- selected_pnl_cents: 659.0
- matched_v28_delta_cents: 491.0
- accepted_entries: 50
- positive_root_rate: 0.25
- positive_market_rate: 0.38461538461538464
- studentized_delta_t: 1.2731303804731615
- spa_screen_pass: False
- rejection_reason: `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;market_drawdown_worse_than_25pct`

## Best By Matched-v28 Delta

- variant: `rv600_primary_max_3_entries_late_70_300_ev4`
- accounting_mode: `all_entries`
- selected_pnl_cents: 1120.0
- matched_v28_delta_cents: 750.0
- rejection_reason: `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;market_drawdown_worse_than_25pct`

## Bootstrap

- studentized_p_value: 0.5294705294705294
- observed_studentized_max: 1.2731303804731615
- bootstrap_candidate_count: 2890
- bootstrap_count: 1000

## Chosen Method

The current RV600 blocker is not raw PnL but failure to beat matched v28 after searching thousands of variants. A studentized root-block bootstrap over matched-v28 deltas tests whether any candidate has superior predictive ability versus the benchmark while screening irrelevant poor alternatives.

## Sources Considered

- selected: Hansen Superior Predictive Ability test: [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=264569](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=264569) - Directly targets whether any searched rule beats a benchmark after multiple-comparison adjustment.
- supporting: White Reality Check: [https://www.fmg.ac.uk/publications/discussion-papers/data-snooping-technical-trading-rule-performance-and-bootstrap](https://www.fmg.ac.uk/publications/discussion-papers/data-snooping-technical-trading-rule-performance-and-bootstrap) - Existing audit already uses the max-statistic idea; SPA is more focused on benchmark superiority.
- supporting: false discovery rate for trading rules: [https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID1095202_code517200.pdf?abstractid=1095202](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID1095202_code517200.pdf?abstractid=1095202) - Reinforces treating apparent winners as possible data-snooping discoveries after transaction costs.
- supporting: Bayesian backtest overfitting: [https://www.mdpi.com/2227-9091/9/1/18](https://www.mdpi.com/2227-9091/9/1/18) - Motivates estimating whether the selected best strategy is likely a true discovery.
- not selected: hierarchical partial pooling: [https://mc-stan.org/rstanarm/articles/pooling.html](https://mc-stan.org/rstanarm/articles/pooling.html) - Useful for shrinkage, but less direct than a matched-v28 superior-predictive-ability test.
