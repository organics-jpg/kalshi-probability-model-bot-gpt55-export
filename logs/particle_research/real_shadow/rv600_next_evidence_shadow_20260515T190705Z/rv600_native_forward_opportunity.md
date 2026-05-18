# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-15T19:33:57+00:00
- roots: 1
- total_candidate_rows: 795
- total_settled_markets: 2
- locked_total_entries: 3
- locked_total_pnl_cents: -46.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260515T190705Z` | 795 | 2 | 2026-05-15T19:07:24.488158+00:00 | 2026-05-15T19:22:22.814704+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_base_70_420_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 27.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 9.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 27.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;avg_entry_below_10c;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY151515-15` | 2026-05-15T19:08:00.985546+00:00 | 419.0 | no | 90.00 | 8.59 | 9.00 | no | 4.52 | 9.00 | False |
| `KXBTC15M-26MAY151515-15` | 2026-05-15T19:08:01.986416+00:00 | 418.0 | no | 90.00 | 8.55 | 9.00 | no | 4.31 | 9.00 | True |
| `KXBTC15M-26MAY151515-15` | 2026-05-15T19:08:03.011972+00:00 | 417.0 | no | 90.00 | 8.42 | 9.00 | no | 3.76 | 9.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_base_70_420_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 27.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 9.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 27.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;avg_entry_below_10c;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY151515-15` | 2026-05-15T19:08:00.985546+00:00 | 419.0 | no | 90.00 | 8.59 | 9.00 | no | 4.52 | 9.00 | False |
| `KXBTC15M-26MAY151515-15` | 2026-05-15T19:08:01.986416+00:00 | 418.0 | no | 90.00 | 8.55 | 9.00 | no | 4.31 | 9.00 | True |
| `KXBTC15M-26MAY151515-15` | 2026-05-15T19:08:03.011972+00:00 | 417.0 | no | 90.00 | 8.42 | 9.00 | no | 3.76 | 9.00 | True |

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

