# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-13T20:16:31+00:00
- roots: 1
- total_candidate_rows: 776
- total_settled_markets: 2
- locked_total_entries: 14
- locked_total_pnl_cents: -237.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260513T195001Z` | 776 | 2 | 2026-05-13T19:50:03.349516+00:00 | 2026-05-13T20:05:02.418266+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev2`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 5
- distinct_markets: 2
- selected_pnl_cents: 110.0
- matched_v28_delta_cents: 397.0
- avg_pnl_per_entry_cents: 22.0
- positive_root_rate: 1.0
- positive_market_rate: 0.5
- max_single_market_pnl_share: 1.7636363636363637
- last_window_pnl_cents: 110.0
- early_gt_420s_entries: 5
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:50:03.349516+00:00 | 596.7 | yes | 34.00 | 5.72 | 64.00 | no | 2.47 | -67.00 | False |
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:50:04.362166+00:00 | 595.6 | yes | 33.00 | 7.96 | 65.00 | no | -1.01 | -68.00 | True |
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:50:05.354000+00:00 | 594.6 | yes | 33.00 | 2.31 | 65.00 | no | 0.19 | -68.00 | True |
| `KXBTC15M-26MAY131615-15` | 2026-05-13T20:05:00.382909+00:00 | 599.6 | no | 43.00 | 6.64 | -43.00 | no | 7.60 | -43.00 | False |
| `KXBTC15M-26MAY131615-15` | 2026-05-13T20:05:02.418266+00:00 | 597.6 | no | 41.00 | 4.34 | -41.00 | no | 6.81 | -41.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev2`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 5
- distinct_markets: 2
- selected_pnl_cents: 110.0
- matched_v28_delta_cents: 397.0
- avg_pnl_per_entry_cents: 22.0
- positive_root_rate: 1.0
- positive_market_rate: 0.5
- max_single_market_pnl_share: 1.7636363636363637
- last_window_pnl_cents: 110.0
- early_gt_420s_entries: 5
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:50:03.349516+00:00 | 596.7 | yes | 34.00 | 5.72 | 64.00 | no | 2.47 | -67.00 | False |
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:50:04.362166+00:00 | 595.6 | yes | 33.00 | 7.96 | 65.00 | no | -1.01 | -68.00 | True |
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:50:05.354000+00:00 | 594.6 | yes | 33.00 | 2.31 | 65.00 | no | 0.19 | -68.00 | True |
| `KXBTC15M-26MAY131615-15` | 2026-05-13T20:05:00.382909+00:00 | 599.6 | no | 43.00 | 6.64 | -43.00 | no | 7.60 | -43.00 | False |
| `KXBTC15M-26MAY131615-15` | 2026-05-13T20:05:02.418266+00:00 | 597.6 | no | 41.00 | 4.34 | -41.00 | no | 6.81 | -41.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_max_2_entries_mid_120_420_ev12`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 2
- distinct_markets: 1
- selected_pnl_cents: -41.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: -20.5
- positive_root_rate: 0.0
- positive_market_rate: 0.0
- max_single_market_pnl_share: 0.0
- last_window_pnl_cents: -41.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 2
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:54:57.375623+00:00 | 302.6 | no | 24.00 | 12.50 | -24.00 | no | 16.07 | -24.00 | False |
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:55:56.787769+00:00 | 243.2 | no | 17.00 | 13.94 | -17.00 | no | 19.65 | -17.00 | True |

