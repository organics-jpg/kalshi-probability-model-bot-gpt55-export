# RV600 Reality Check Audit

- generated_utc: 2026-05-15T21:21:42+00:00
- research_only: True
- decision: reality_check_rejects_current_grid
- root_count: 40
- candidate_count: 7482

## Best By Matched-v28 Delta

- variant: `rv600_primary_max_3_entries_late_70_300_ev4`
- accounting_mode: `all_entries`
- selected_pnl_cents: 1120.0
- matched_v28_delta_cents: 750.0
- accepted_entries: 84
- avg_pnl_per_entry_cents: 13.333333333333334
- positive_root_rate: 0.275
- positive_market_rate: 0.36666666666666664
- last_window_pnl_cents: -68.0
- rejection_reason: `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;market_drawdown_worse_than_25pct`

## Best By Selected PnL

- variant: `blend_90_10_max_3_entries_base_70_420_ev4`
- accounting_mode: `all_entries`
- selected_pnl_cents: 1700.0
- matched_v28_delta_cents: 0.0
- rejection_reason: `positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct;market_drawdown_worse_than_25pct`

## Bootstrap Checks

- mean_reality_check_p_value: 0.3736
- mean_reality_check_observed_stat: 118.5854
- studentized_reality_check_p_value: 0.7023
- studentized_reality_check_observed_stat: 1.2731

## Chosen Method

The current RV600 risk is data snooping across thousands of grid variants. A root-level bootstrap of the maximum matched-v28 delta tests whether the best apparent edge is larger than the selection effect expected from the full tested universe.

## Sources Considered

- selected: [White-style Reality Check for technical trading rules](https://www.fmg.ac.uk/publications/discussion-papers/data-snooping-technical-trading-rule-performance-and-bootstrap) - Direct fit for testing the best rule after searching a full universe of trading rules.
- partially_used: [Hansen Superior Predictive Ability test](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=264569) - Motivates the studentized companion statistic, but a full SPA implementation is unnecessary for this small root-level audit.
- not_selected: [Deflated Sharpe Ratio](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551) - Corrects Sharpe inflation, while RV600 has sparse binary-settlement PnL and a matched-v28 benchmark.
- not_selected: [Backtest PnL discounting](https://arxiv.org/abs/1902.01802) - Useful for shrinkage, but less directly tied to selecting one candidate from the tested grid.
- not_selected: [Optimal trading rules without backtesting](https://arxiv.org/abs/1408.1159) - Interesting direction, but RV600 lacks a closed-form process model reliable enough to replace shadow/replay evidence.
