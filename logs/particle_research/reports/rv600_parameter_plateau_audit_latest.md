# RV600 Parameter Plateau Audit

- generated_utc: 2026-05-15T20:50:08+00:00
- research_only: True
- decision: parameter_plateau_rejected
- support_count: 0

## Modeling Choice

Use a local parameter-neighborhood plateau test over existing RV600 grid variants. A candidate is not supported unless nearby timing-window and EV-threshold variants also retain positive PnL, matched-v28 edge, and root/market breadth. This targets fragile single-row selection without adding a new live strategy family.

## Sources Considered

- selected: parameter stability / robust optimization plateau heuristic: https://quanthop.com/learn/validation-robustness/stability-testing - Directly motivates preferring broad parameter plateaus over isolated optima.
- supporting: Probability of Backtest Overfitting / CSCV: https://core.ac.uk/display/24041876 - Motivates rejecting parameter choices that do not keep out-of-sample rank across splits.
- supporting: Model Confidence Set: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=522382 - Motivates treating several statistically indistinguishable candidate rules as a set.
- supporting: Stability Selection: https://arxiv.org/abs/0809.2932 - Motivates requiring repeated support under nearby/subsampled selections.
- not selected as implementation: online expert weighting: https://arxiv.org/search/cs?query=online+learning+expert+advice+trading+transaction+costs&searchtype=all - Already covered by the online-expert rescue; the current blocker is parameter fragility.

## Grid

- root_count: 40
- variant_count: 3948
- summary_row_count: 11844
- position_capped_parsed_row_count: 3780

## Thresholds

- min_neighbors: 4
- min_positive_pnl_rate: 0.75
- min_positive_delta_rate: 0.75
- min_breadth_ok_rate: 0.5
- min_base_gate_neighbors: 2
- min_median_positive_root_rate: 0.55
- min_median_positive_market_rate: 0.55

## Best Plateaus

| support | center | neighbors | pos pnl | pos delta | breadth | median pnl | median delta | median root | median market | rejection counts |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| False | `rv600_primary_max_3_entries_mid_120_420_ev4` | 9 | 1.00 | 1.00 | 0.00 | 1242.0 | 646.0 | 0.38 | 0.47 | `positive_roots_below_60pct=9; positive_markets_below_60pct=9; avg_entry_below_10c=2; single_market_share_above_25pct=2` |
| False | `rv600_softveto6_max_3_entries_mid_120_420_ev4` | 9 | 1.00 | 1.00 | 0.00 | 1242.0 | 646.0 | 0.38 | 0.47 | `positive_roots_below_60pct=9; positive_markets_below_60pct=9; avg_entry_below_10c=2; single_market_share_above_25pct=2` |
| False | `rv600_softveto10_max_3_entries_mid_120_420_ev4` | 9 | 1.00 | 1.00 | 0.00 | 1242.0 | 646.0 | 0.38 | 0.47 | `positive_roots_below_60pct=9; positive_markets_below_60pct=9; avg_entry_below_10c=2; single_market_share_above_25pct=2` |
| False | `rv600_primary_max_3_entries_mid_180_420_ev4` | 9 | 1.00 | 1.00 | 0.00 | 1242.0 | 646.0 | 0.38 | 0.46 | `positive_roots_below_60pct=9; positive_markets_below_60pct=9; avg_entry_below_10c=3; single_market_share_above_25pct=2` |
| False | `rv600_softveto6_max_3_entries_mid_180_420_ev4` | 9 | 1.00 | 1.00 | 0.00 | 1242.0 | 646.0 | 0.38 | 0.46 | `positive_roots_below_60pct=9; positive_markets_below_60pct=9; avg_entry_below_10c=3; single_market_share_above_25pct=2` |
| False | `rv600_softveto10_max_3_entries_mid_180_420_ev4` | 9 | 1.00 | 1.00 | 0.00 | 1242.0 | 646.0 | 0.38 | 0.46 | `positive_roots_below_60pct=9; positive_markets_below_60pct=9; avg_entry_below_10c=3; single_market_share_above_25pct=2` |
| False | `rv600_primary_max_3_entries_mid_120_420_ev6` | 9 | 1.00 | 1.00 | 0.00 | 1227.0 | 646.0 | 0.35 | 0.42 | `positive_roots_below_60pct=9; positive_markets_below_60pct=9; single_market_share_above_25pct=4; avg_entry_below_10c=3; last_window_nonpositive=3` |
| False | `rv600_primary_max_3_entries_base_70_420_ev4` | 9 | 1.00 | 1.00 | 0.00 | 1227.0 | 646.0 | 0.38 | 0.42 | `positive_roots_below_60pct=9; positive_markets_below_60pct=9; last_window_nonpositive=3; single_market_share_above_25pct=2` |
| False | `rv600_softveto6_max_3_entries_mid_120_420_ev6` | 9 | 1.00 | 1.00 | 0.00 | 1227.0 | 646.0 | 0.35 | 0.42 | `positive_roots_below_60pct=9; positive_markets_below_60pct=9; single_market_share_above_25pct=4; avg_entry_below_10c=3; last_window_nonpositive=3` |
| False | `rv600_softveto10_max_3_entries_mid_120_420_ev6` | 9 | 1.00 | 1.00 | 0.00 | 1227.0 | 646.0 | 0.35 | 0.42 | `positive_roots_below_60pct=9; positive_markets_below_60pct=9; single_market_share_above_25pct=4; avg_entry_below_10c=3; last_window_nonpositive=3` |

## Interpretation

No RV600 candidate has a stable local parameter plateau. The best neighborhood still fails breadth support: center=rv600_primary_max_3_entries_mid_120_420_ev4, median_positive_root_rate=0.375, median_positive_market_rate=0.465, breadth_ok_rate=0.000.
