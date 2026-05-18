# RV600 Market-Balance Rescue

- generated_utc: 2026-05-15T20:55:04+00:00
- research_only: True
- decision: market_balance_rescue_failed
- modeling_choice: Use existing RV600 grid variants only, rank them with a concentration- and market-stability-aware utility, and verify with anchored forward splits. This implements diversification/position-limit ideas without changing live logic or introducing a new broad model family.

## Sources Considered

- Return-diversification portfolio selection: https://arxiv.org/abs/2312.09707 - Motivates optimizing return jointly with diversification rather than total PnL alone.
- Mean-CVaR with cardinality/rebalancing constraints: https://link.springer.com/article/10.1007/s11831-020-09522-1 - Motivates explicit risk constraints and cardinality limits when return-only selection is too concentrated.
- Deflated Sharpe Ratio: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551 - Motivates treating best-row discovery as multiple-testing-prone until forward evidence survives.
- Purged and embargoed validation: https://en.wikipedia.org/wiki/Purged_cross-validation - Motivates time-ordered validation instead of random folds for event-driven financial labels.
- Concentration-risk constraints: https://en.wikipedia.org/wiki/Portfolio_optimization#Concentration_risk - Motivates hard upper bounds on single-component contribution/exposure.

## Counts

- summary_rows: 11844
- gate_pass_rows: 0
- positive_concentration_ok_rows: 1347
- positive_market_rate_ok_rows: 293
- positive_both_balance_ok_rows: 12
- entry_delta_concentration_ok_rows: 702

## Best Total PnL Row

- variant: `blend_90_10_max_3_entries_base_70_420_ev4`
- accounting_mode: `all_entries`
- gate_count: `4`
- accepted_entries: `100`
- distinct_markets: `34`
- selected_pnl_cents: `1700.0`
- matched_v28_delta_cents: `0.0`
- avg_pnl_per_entry_cents: `17.0`
- positive_root_rate: `0.4`
- positive_market_rate: `0.5`
- max_single_market_pnl_share: `0.14823529411764705`
- last_window_pnl_cents: `91.0`
- no_fill_penalty_pnl_cents: `1700.0`
- rejection_reason: `positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct`

## Best Market-Balanced Row

- variant: `rv600_primary_max_3_entries_broad_70_600_ev4`
- accounting_mode: `position_capped`
- gate_count: `3`
- accepted_entries: `146`
- distinct_markets: `52`
- selected_pnl_cents: `1657.0`
- matched_v28_delta_cents: `528.0`
- avg_pnl_per_entry_cents: `11.349315068493151`
- positive_root_rate: `0.475`
- positive_market_rate: `0.4230769230769231`
- max_single_market_pnl_share: `0.17380808690404345`
- last_window_pnl_cents: `189.0`
- no_fill_penalty_pnl_cents: `1657.0`
- rejection_reason: `positive_roots_below_60pct;positive_markets_below_60pct`

## Best Concentration-OK Positive Row

- variant: `blend_90_10_max_3_entries_base_70_420_ev4`
- accounting_mode: `all_entries`
- gate_count: `4`
- accepted_entries: `100`
- distinct_markets: `34`
- selected_pnl_cents: `1700.0`
- matched_v28_delta_cents: `0.0`
- avg_pnl_per_entry_cents: `17.0`
- positive_root_rate: `0.4`
- positive_market_rate: `0.5`
- max_single_market_pnl_share: `0.14823529411764705`
- last_window_pnl_cents: `91.0`
- no_fill_penalty_pnl_cents: `1700.0`
- rejection_reason: `positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct`

## Best Market-Rate-OK Positive Row

- variant: `blend_95_5_max_2_entries_mid_180_420_ev2`
- accounting_mode: `all_entries`
- gate_count: `4`
- accepted_entries: `78`
- distinct_markets: `40`
- selected_pnl_cents: `901.0`
- matched_v28_delta_cents: `0.0`
- avg_pnl_per_entry_cents: `11.551282051282051`
- positive_root_rate: `0.525`
- positive_market_rate: `0.6`
- max_single_market_pnl_share: `0.17314095449500555`
- last_window_pnl_cents: `110.0`
- no_fill_penalty_pnl_cents: `901.0`
- rejection_reason: `positive_roots_below_60pct;does_not_beat_matched_v28_by_20pct`

## Anchored Forward Probe

- split_count: 37
- selection_count: 37
- test_entry_count: 140
- test_selected_pnl_cents: 236.0
- test_matched_v28_delta_cents: -288.0
- positive_test_root_rate: 0.43243243243243246
- prequential_gate_pass: False

## Interpretation

The best market-balanced existing row is still gate-rejected, and anchored forward selection is not sufficient for completion: prequential_gate_pass=False.
