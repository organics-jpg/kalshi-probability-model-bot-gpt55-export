# RV600 PBO Stability Audit

- generated_utc: 2026-05-15T21:21:27+00:00
- decision: pbo_rejects_current_grid
- root_count: 40
- candidate_count: 7482
- valid_split_count: 512
- pbo: 0.3574
- positive_split_rate: 0.8047
- mean_selected_test_pnl_cents: 317.6289
- median_selected_test_pnl_cents: 321.0000

## Chosen Method

The current blocker is positive average PnL with unstable root/market breadth. PBO directly checks whether variants selected in-sample keep above-median rank out of sample across root splits.

## Top Selected Variants

| candidate | count | rate |
|---|---:|---:|
| `blend_95_5_max_3_entries_base_70_420_ev2|all_entries` | 87 | 0.1699 |
| `rv600_primary_max_3_entries_broad_70_600_ev4|all_entries` | 84 | 0.1641 |
| `blend_80_20_max_3_entries_base_70_420_ev4|all_entries` | 36 | 0.0703 |
| `rv600_primary_max_3_entries_broad_70_600_ev6|all_entries` | 33 | 0.0645 |
| `blend_95_5_max_3_entries_mid_180_420_ev2|all_entries` | 33 | 0.0645 |
| `rv600_primary_max_3_entries_broad_70_600_ev0|all_entries` | 29 | 0.0566 |
| `blend_90_10_max_3_entries_base_70_420_ev4|all_entries` | 23 | 0.0449 |
| `rv600_primary_max_3_entries_base_70_420_ev6|all_entries` | 12 | 0.0234 |
| `blend_95_5_max_3_entries_broad_70_600_ev0|all_entries` | 12 | 0.0234 |
| `blend_80_20_risk_cap_100c_mid_120_420_ev4|all_entries` | 10 | 0.0195 |

## Sources Considered

- selected: [Probability of Backtest Overfitting / CSCV](https://core.ac.uk/display/24041876)
- not_selected: [Deflated Sharpe Ratio](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2460551_code87814.pdf?abstractid=2460551&mirid=1) - Useful for multiple-testing inflation, but less direct for root/market breadth than split-rank PBO.
- already_tested: [Group DRO](https://arxiv.org/abs/1911.08731) - Existing group-DRO rescue still has zero support rows on the current sample.
- already_tested_adjacent: [Conformal Risk Control](https://arxiv.org/abs/2208.02814) - Existing conformal abstention rescue did not produce a prequential gate pass.
