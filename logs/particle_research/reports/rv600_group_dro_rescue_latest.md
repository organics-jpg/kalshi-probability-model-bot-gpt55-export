# RV600 Group-DRO Rescue

- generated_utc: 2026-05-15T21:05:08+00:00
- research_only: True
- decision: group_dro_rescue_failed
- modeling_choice: Evaluate existing RV600 grid variants with a group-DRO/minimax utility over bounded roots, using root lower-tail PnL, market concentration, recent-window PnL, and transaction-churn penalties. This is a selection/abstention audit only; it does not add a new live model or touch v28 logic.

## Solutions Considered

- Total-PnL re-ranking: rejected - Already failed by concentrating profit in too few roots/markets.
- Group-DRO/minimax root and market robustness: selected - Directly targets the observed worst-root and market-concentration failure.
- Cardinality/CVaR position selection: included_as_penalties - Mapped to position_capped accounting, lower-tail root PnL, and churn penalties.
- Online lazy updates: included_as_penalties - Mapped to a repeated-entry churn penalty rather than a new trading model.
- CPCV/PBO/DSR-style validation: included_as_gate - Mapped to anchored forward splits and rejection unless out-of-sample groups pass.

## Sources Considered

- Group DRO for worst-group generalization: https://arxiv.org/abs/1911.08731 - Motivates optimizing against weak groups instead of average performance only.
- Cardinality-constrained distributionally robust portfolio optimization: https://arxiv.org/abs/2112.12454 - Motivates combining robust objectives with limits on selected positions.
- Cardinality-constrained mean/CVaR portfolio optimization: https://arxiv.org/abs/1810.10563 - Motivates lower-tail risk control and cardinality constraints under costs.
- Online lazy portfolio updates with transaction costs: https://ojs.aaai.org/index.php/AAAI/article/view/8693 - Motivates avoiding churn unless an update is worth transaction costs.
- Backtest overfitting in the machine learning era: https://www.sciencedirect.com/science/article/abs/pii/S0950705124011110 - Motivates anchored, purged-style validation and false-discovery skepticism.

## Counts

- roots: 40
- summary_row_count: 11844
- positive_position_row_count: 1092
- support_row_count: 0

## Best Row

- variant: `rv600_primary_max_3_entries_base_70_420_ev6`
- accounting_mode: `position_capped`
- gate_count: `3`
- accepted_entries: `85`
- distinct_markets: `30`
- selected_pnl_cents: `1451.0000`
- matched_v28_control_pnl_cents: `781.0000`
- matched_v28_delta_cents: `670.0000`
- avg_pnl_per_entry_cents: `17.0706`
- avg_pnl_per_market_cents: `48.3667`
- positive_root_rate: `0.3750`
- positive_market_rate: `0.5000`
- max_single_market_pnl_share: `0.1875`
- last_window_pnl_cents: `38.0000`
- added_entry_count: `55`
- added_entry_pnl_cents: `881.0000`
- avg_added_entry_pnl_cents: `16.0182`
- worst_market_pnl_cents: `-117.0000`
- no_fill_penalty_pnl_cents: `1451.0000`
- rejection_reason: `positive_roots_below_60pct;positive_markets_below_60pct`
- group_dro_support: `False`
- lower_tail_root_pnl_cents: `-89.1000`
- worst_root_pnl_cents: `-117.0000`
- downside_deviation_cents: `45.8999`
- robust_score: `57.4001`
- concentration_penalty: `0.0000`
- market_penalty: `25.0000`
- root_penalty: `33.7500`
- recent_penalty: `0.0000`
- churn_penalty: `0.0000`

## Anchored Forward Probe

- split_count: 37
- selection_count: 37
- test_entry_count: 94
- test_distinct_markets: 45
- test_selected_pnl_cents: 240.0
- test_matched_v28_delta_cents: -538.0
- positive_test_root_rate: 0.3783783783783784
- max_single_market_pnl_share: 0.8375
- lower_tail_test_root_pnl_cents: -91.2
- prequential_gate_pass: False

## Top Rows

| variant | accounting | gates | entries | pnl | v28 delta | lower-tail | worst root | score | pos roots | pos markets | max share | rejection |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `rv600_primary_max_3_entries_base_70_420_ev6` | position_capped | 3 | 85 | 1451.0 | 670.0 | -89.1 | -117.0 | 57.4 | 0.38 | 0.50 | 0.19 | `positive_roots_below_60pct;positive_markets_below_60pct` |
| `rv600_softveto6_max_3_entries_base_70_420_ev6` | position_capped | 4 | 85 | 1451.0 | 670.0 | -89.1 | -117.0 | 57.4 | 0.38 | 0.50 | 0.19 | `positive_roots_below_60pct;positive_markets_below_60pct` |
| `rv600_softveto10_max_3_entries_base_70_420_ev6` | position_capped | 4 | 85 | 1451.0 | 670.0 | -89.1 | -117.0 | 57.4 | 0.38 | 0.50 | 0.19 | `positive_roots_below_60pct;positive_markets_below_60pct` |
| `rv600_primary_max_3_entries_mid_120_420_ev6` | position_capped | 3 | 85 | 1451.0 | 670.0 | -89.1 | -117.0 | 57.4 | 0.38 | 0.50 | 0.19 | `positive_roots_below_60pct;positive_markets_below_60pct` |
| `rv600_softveto6_max_3_entries_mid_120_420_ev6` | position_capped | 4 | 85 | 1451.0 | 670.0 | -89.1 | -117.0 | 57.4 | 0.38 | 0.50 | 0.19 | `positive_roots_below_60pct;positive_markets_below_60pct` |
| `rv600_softveto10_max_3_entries_mid_120_420_ev6` | position_capped | 4 | 85 | 1451.0 | 670.0 | -89.1 | -117.0 | 57.4 | 0.38 | 0.50 | 0.19 | `positive_roots_below_60pct;positive_markets_below_60pct` |
| `rv600_primary_risk_cap_200c_base_70_420_ev6` | position_capped | 3 | 84 | 1442.0 | 670.0 | -89.1 | -117.0 | 56.1 | 0.38 | 0.50 | 0.19 | `positive_roots_below_60pct;positive_markets_below_60pct` |
| `rv600_softveto6_risk_cap_200c_base_70_420_ev6` | position_capped | 4 | 84 | 1442.0 | 670.0 | -89.1 | -117.0 | 56.1 | 0.38 | 0.50 | 0.19 | `positive_roots_below_60pct;positive_markets_below_60pct` |
| `rv600_softveto10_risk_cap_200c_base_70_420_ev6` | position_capped | 4 | 84 | 1442.0 | 670.0 | -89.1 | -117.0 | 56.1 | 0.38 | 0.50 | 0.19 | `positive_roots_below_60pct;positive_markets_below_60pct` |
| `rv600_primary_risk_cap_200c_mid_120_420_ev6` | position_capped | 3 | 84 | 1442.0 | 670.0 | -89.1 | -117.0 | 56.1 | 0.38 | 0.50 | 0.19 | `positive_roots_below_60pct;positive_markets_below_60pct` |
| `rv600_softveto6_risk_cap_200c_mid_120_420_ev6` | position_capped | 4 | 84 | 1442.0 | 670.0 | -89.1 | -117.0 | 56.1 | 0.38 | 0.50 | 0.19 | `positive_roots_below_60pct;positive_markets_below_60pct` |
| `rv600_softveto10_risk_cap_200c_mid_120_420_ev6` | position_capped | 4 | 84 | 1442.0 | 670.0 | -89.1 | -117.0 | 56.1 | 0.38 | 0.50 | 0.19 | `positive_roots_below_60pct;positive_markets_below_60pct` |

## Interpretation

No existing RV600 row clears the group-DRO support gate. The rescue remains rejected unless fresh bounded evidence changes the root/market lower-tail profile; anchored forward pass=False.
