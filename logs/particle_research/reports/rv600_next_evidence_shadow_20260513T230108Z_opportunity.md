# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-13T23:31:50+00:00
- roots: 1
- total_candidate_rows: 805
- total_settled_markets: 2
- locked_total_entries: 14
- locked_total_pnl_cents: -126.0
- conclusion: Locked entries exist, but RV600-primary native forward PnL is nonpositive.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260513T230108Z` | 805 | 2 | 2026-05-13T23:01:11.039832+00:00 | 2026-05-13T23:16:09.892630+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `blend_95_5_max_3_entries_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 4
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 71.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 23.666666666666668
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 71.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131915-15` | 2026-05-13T23:05:01.093358+00:00 | 598.9 | no | 79.00 | 0.23 | 19.00 | no | 0.60 | 19.00 | False |
| `KXBTC15M-26MAY131915-15` | 2026-05-13T23:05:02.102281+00:00 | 597.9 | no | 76.00 | 1.61 | 22.00 | no | 1.96 | 22.00 | True |
| `KXBTC15M-26MAY131915-15` | 2026-05-13T23:05:06.119496+00:00 | 593.9 | no | 68.00 | 0.68 | 30.00 | no | 0.97 | 30.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_single_market_late_70_180_ev20`
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

### Best Locked Candidate

- variant: `rv600_primary_max_2_entries_mid_120_420_ev12`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 2
- distinct_markets: 1
- selected_pnl_cents: -18.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: -9.0
- positive_root_rate: 0.0
- positive_market_rate: 0.0
- max_single_market_pnl_share: 0.0
- last_window_pnl_cents: -18.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 2
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131915-15` | 2026-05-13T23:11:58.006621+00:00 | 182.0 | yes | 9.00 | 12.64 | -9.00 | yes | 9.05 | -9.00 | False |
| `KXBTC15M-26MAY131915-15` | 2026-05-13T23:11:59.006698+00:00 | 181.0 | yes | 9.00 | 12.57 | -9.00 | yes | 8.98 | -9.00 | True |

