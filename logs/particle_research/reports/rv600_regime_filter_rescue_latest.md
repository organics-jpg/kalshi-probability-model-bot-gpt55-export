# RV600 Regime-Filter Rescue

- generated_utc: 2026-05-15T21:02:15+00:00
- research_only: True
- decision: regime_filter_rescue_failed
- modeling_choice: Use a small predeclared set of causal regime predicates as abstention filters on existing RV600 grid variants, then require anchored forward validation. This targets the observed root/market instability without changing live logic or inventing a new broad entry model.

## Sources Considered

- Structural clustering of volatility regimes for dynamic trading strategies: https://arxiv.org/abs/2004.09963 - Motivates volatility/regime-conditioned abstention and online risk avoidance.
- Detecting bearish and bullish markets with hierarchical hidden Markov models: https://arxiv.org/abs/2007.14874 - Motivates using market regimes as a trading-strategy filter rather than a stand-alone forecast.
- Adaptive Conformal Inference Under Distribution Shift: https://arxiv.org/abs/2106.00170 - Motivates treating nonstationarity as an online abstention/coverage problem.
- Adaptive Conformal Predictions for Time Series: https://arxiv.org/abs/2202.07282 - Motivates time-series-safe adaptive filtering with expert aggregation ideas.
- Deflated Sharpe Ratio: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551 - Motivates rejecting best-row discoveries unless anchored forward evidence survives.

## Counts

- roots: 40
- predicate_count: 11
- summary_row_count: 130284
- positive_position_row_count: 30054
- support_row_count: 0

## Best Row

- variant: `blend_95_5_max_3_entries_base_70_420_ev2__regime_near_strike_10bp`
- accounting_mode: `position_capped`
- gate_count: `5`
- accepted_entries: `96`
- distinct_markets: `32`
- selected_pnl_cents: `1742.0`
- matched_v28_delta_cents: `0.0`
- avg_pnl_per_entry_cents: `18.145833333333332`
- positive_root_rate: `0.4`
- positive_market_rate: `0.53125`
- max_single_market_pnl_share: `0.14006888633754305`
- last_window_pnl_cents: `168.0`
- no_fill_penalty_pnl_cents: `1742.0`
- rejection_reason: `positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct`

## Anchored Forward Probe

- split_count: 37
- selection_count: 37
- test_entry_count: 115
- test_selected_pnl_cents: 157.0
- test_matched_v28_delta_cents: -404.0
- positive_test_root_rate: 0.40540540540540543
- max_single_market_pnl_share: 1.5541401273885351
- prequential_gate_pass: False

## Top Rows

| variant | accounting | gates | entries | pnl | v28 delta | pos roots | pos markets | max share | last window | rejection |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `blend_95_5_max_3_entries_base_70_420_ev2__regime_near_strike_10bp` | position_capped | 5 | 96 | 1742.0 | 0.0 | 0.40 | 0.53 | 0.14 | 168.0 | `positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct` |
| `blend_95_5_max_3_entries_mid_120_420_ev2__regime_near_strike_10bp` | position_capped | 5 | 96 | 1742.0 | 0.0 | 0.40 | 0.53 | 0.14 | 168.0 | `positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct` |
| `blend_95_5_risk_cap_200c_mid_120_420_ev2__regime_near_strike_10bp` | position_capped | 5 | 95 | 1720.0 | 0.0 | 0.40 | 0.53 | 0.14 | 168.0 | `positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct` |
| `blend_95_5_risk_cap_200c_base_70_420_ev2__regime_near_strike_10bp` | position_capped | 5 | 96 | 1712.0 | 0.0 | 0.40 | 0.52 | 0.14 | 168.0 | `positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct` |
| `blend_90_10_max_3_entries_base_70_420_ev4__regime_all` | position_capped | 4 | 100 | 1700.0 | 0.0 | 0.40 | 0.50 | 0.15 | 91.0 | `positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct` |
| `blend_90_10_max_3_entries_base_70_420_ev4__regime_rv600_low_vol_le_65` | position_capped | 5 | 100 | 1700.0 | 0.0 | 0.40 | 0.50 | 0.15 | 91.0 | `positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct` |
| `blend_90_10_max_3_entries_base_70_420_ev4__regime_v28_side_agrees` | position_capped | 5 | 100 | 1700.0 | 0.0 | 0.40 | 0.50 | 0.15 | 91.0 | `positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct` |
| `blend_90_10_max_3_entries_mid_120_420_ev4__regime_all` | position_capped | 4 | 100 | 1700.0 | 0.0 | 0.40 | 0.50 | 0.15 | 91.0 | `positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct` |
| `blend_90_10_max_3_entries_mid_120_420_ev4__regime_rv600_low_vol_le_65` | position_capped | 5 | 100 | 1700.0 | 0.0 | 0.40 | 0.50 | 0.15 | 91.0 | `positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct` |
| `blend_90_10_max_3_entries_mid_120_420_ev4__regime_v28_side_agrees` | position_capped | 5 | 100 | 1700.0 | 0.0 | 0.40 | 0.50 | 0.15 | 91.0 | `positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct` |
| `blend_90_10_risk_cap_200c_base_70_420_ev4__regime_all` | position_capped | 4 | 99 | 1691.0 | 0.0 | 0.40 | 0.50 | 0.15 | 91.0 | `positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct` |
| `blend_90_10_risk_cap_200c_base_70_420_ev4__regime_rv600_low_vol_le_65` | position_capped | 5 | 99 | 1691.0 | 0.0 | 0.40 | 0.50 | 0.15 | 91.0 | `positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct` |

## Interpretation

No predeclared causal regime filter produced a cumulative support row. The rescue remains rejected; anchored forward pass=False.
