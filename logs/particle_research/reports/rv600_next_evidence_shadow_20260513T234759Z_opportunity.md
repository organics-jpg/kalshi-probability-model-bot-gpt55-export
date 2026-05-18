# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-14T00:17:56+00:00
- roots: 1
- total_candidate_rows: 836
- total_settled_markets: 2
- locked_total_entries: 6
- locked_total_pnl_cents: -170.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260513T234759Z` | 836 | 2 | 2026-05-13T23:48:02.464639+00:00 | 2026-05-14T00:03:01.606884+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_base_70_420_ev6`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 246.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 82.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 246.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY132000-00` | 2026-05-13T23:53:28.940246+00:00 | 391.1 | yes | 17.00 | 7.02 | 82.00 | yes | 8.34 | 82.00 | False |
| `KXBTC15M-26MAY132000-00` | 2026-05-13T23:53:29.950335+00:00 | 390.0 | yes | 17.00 | 6.98 | 82.00 | yes | 8.31 | 82.00 | True |
| `KXBTC15M-26MAY132000-00` | 2026-05-13T23:53:30.962221+00:00 | 389.0 | yes | 17.00 | 6.96 | 82.00 | yes | 8.31 | 82.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_base_70_420_ev6`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 246.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 82.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 246.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY132000-00` | 2026-05-13T23:53:28.940246+00:00 | 391.1 | yes | 17.00 | 7.02 | 82.00 | yes | 8.34 | 82.00 | False |
| `KXBTC15M-26MAY132000-00` | 2026-05-13T23:53:29.950335+00:00 | 390.0 | yes | 17.00 | 6.98 | 82.00 | yes | 8.31 | 82.00 | True |
| `KXBTC15M-26MAY132000-00` | 2026-05-13T23:53:30.962221+00:00 | 389.0 | yes | 17.00 | 6.96 | 82.00 | yes | 8.31 | 82.00 | True |

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

