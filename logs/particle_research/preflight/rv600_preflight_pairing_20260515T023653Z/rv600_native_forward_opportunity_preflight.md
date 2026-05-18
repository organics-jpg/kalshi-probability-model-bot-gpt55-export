# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-15T02:47:29+00:00
- roots: 1
- total_candidate_rows: 28
- total_settled_markets: 1
- locked_total_entries: 1
- locked_total_pnl_cents: -67.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_preflight_pairing_20260515T023653Z` | 28 | 1 | 2026-05-15T02:36:56.171919+00:00 | 2026-05-15T02:37:23.675198+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 188.0
- matched_v28_delta_cents: 387.0
- avg_pnl_per_entry_cents: 62.666666666666664
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 188.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY142245-45` | 2026-05-15T02:36:56.171919+00:00 | 483.8 | yes | 35.00 | 2.56 | 63.00 | no | 3.02 | -67.00 | False |
| `KXBTC15M-26MAY142245-45` | 2026-05-15T02:36:57.166588+00:00 | 482.8 | yes | 36.00 | 1.31 | 62.00 | no | 4.50 | -66.00 | True |
| `KXBTC15M-26MAY142245-45` | 2026-05-15T02:36:58.168864+00:00 | 481.8 | yes | 35.00 | 2.29 | 63.00 | no | 4.53 | -66.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 188.0
- matched_v28_delta_cents: 387.0
- avg_pnl_per_entry_cents: 62.666666666666664
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 188.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY142245-45` | 2026-05-15T02:36:56.171919+00:00 | 483.8 | yes | 35.00 | 2.56 | 63.00 | no | 3.02 | -67.00 | False |
| `KXBTC15M-26MAY142245-45` | 2026-05-15T02:36:57.166588+00:00 | 482.8 | yes | 36.00 | 1.31 | 62.00 | no | 4.50 | -66.00 | True |
| `KXBTC15M-26MAY142245-45` | 2026-05-15T02:36:58.168864+00:00 | 481.8 | yes | 35.00 | 2.29 | 63.00 | no | 4.53 | -66.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_max_3_entries_mid_120_420_ev12`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 0
- distinct_markets: 0
- selected_pnl_cents: 0
- matched_v28_delta_cents: 0
- avg_pnl_per_entry_cents: 0.0
- positive_root_rate: 0.0
- positive_market_rate: 0.0
- max_single_market_pnl_share: 0.0
- last_window_pnl_cents: 0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|

