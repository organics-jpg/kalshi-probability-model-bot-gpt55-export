# RV600 Stability Selection Rescue

- generated_utc: 2026-05-15T20:52:33+00:00
- research_only: True
- decision: stability_selection_rescue_failed
- root_count: 40
- candidate_count: 1260
- split_count: 512
- locked_selection_count: 75
- full_support_count: 0
- test_total_entries: 3678
- test_selected_pnl_cents: -8458.0
- test_matched_v28_delta_cents: -1933.0
- test_avg_pnl_per_entry_cents: -2.2996
- preliminary_gate_pass: False
- rejection_reason: no_full_sample_support_row;selection_rate_below_threshold;nonpositive_selected_test_pnl;does_not_beat_matched_v28_by_20pct;avg_test_entry_below_10c;positive_test_splits_below_60pct

## Modeling Choice

| method | decision | source | fit |
|---|---|---|---|
| `stability_selection` | chosen | [Meinshausen and Buehlmann, Stability Selection](https://arxiv.org/abs/0809.2932) | Directly tests whether a candidate remains selected across many root subsamples. |
| `superior_predictive_ability` | not_selected | [Hansen, A Test for Superior Predictive Ability](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=264569) | Useful for data-snooping-adjusted existence tests, but less direct for selecting one simple forward-shadow candidate. |
| `deflated_sharpe_ratio` | not_selected | [Bailey and Lopez de Prado, The Deflated Sharpe Ratio](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2460551_code87814.pdf?abstractid=2460551&mirid=1) | Sharpe-style selection-bias correction is less natural than per-entry/root accounting for binary settlement trades. |
| `pbo_cscv` | already_tested | [Bailey, Borwein, Lopez de Prado, and Zhu, The Probability of Backtest Overfitting](https://www.carmamaths.org/resources/jon/backtest2.pdf) | Already implemented as the split-rank PBO audit; current grid was rejected there. |
| `empirical_bernstein_lcb` | deferred | [Maurer and Pontil, Empirical Bernstein Bounds and Sample Variance Penalization](https://arxiv.org/abs/0907.3740) | A lower-confidence-bound selector is plausible, but current root count is small enough that bounds are likely vacuous. |

## Top Stable Selections

| candidate | count | rate |
|---|---:|---:|
| `rv600_primary_single_market_base_70_420_ev0|one_per_side_per_market` | 11 | 0.0215 |
| `rv600_primary_max_3_entries_base_70_420_ev2|position_capped` | 6 | 0.0117 |
| `rv600_primary_max_3_entries_broad_70_600_ev0|position_capped` | 6 | 0.0117 |
| `rv600_primary_max_3_entries_broad_70_600_ev2|position_capped` | 6 | 0.0117 |
| `rv600_primary_side_flip_only_broad_70_600_ev4|one_per_side_per_market` | 6 | 0.0117 |
| `rv600_primary_same_side_refresh_60s_broad_70_600_ev4|one_per_side_per_market` | 5 | 0.0098 |
| `rv600_primary_max_3_entries_mid_180_420_ev2|position_capped` | 5 | 0.0098 |
| `rv600_primary_max_2_entries_broad_70_600_ev4|position_capped` | 3 | 0.0059 |
| `rv600_primary_single_market_mid_180_420_ev0|one_per_side_per_market` | 3 | 0.0059 |
| `rv600_primary_same_side_ev_step_3c_mid_180_420_ev2|position_capped` | 2 | 0.0039 |

## Best Full Diagnostic

- variant: `rv600_primary_side_flip_only_broad_70_600_ev4`
- accounting_mode: `one_per_side_per_market`
- entries: 72
- selected_pnl_cents: 472.0
- matched_v28_delta_cents: 231.0
- avg_pnl_per_entry_cents: 6.5556
- positive_root_rate: 0.6000
- positive_market_rate: 0.5192
- max_single_market_pnl_share: 0.1483
- rejection_reason: avg_entry_below_10c;positive_markets_below_60pct
