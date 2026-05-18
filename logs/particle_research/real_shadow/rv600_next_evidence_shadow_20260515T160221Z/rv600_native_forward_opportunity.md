# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-15T16:34:06+00:00
- roots: 1
- total_candidate_rows: 824
- total_settled_markets: 2
- locked_total_entries: 15
- locked_total_pnl_cents: -532.0
- conclusion: Locked entries exist, but RV600-primary native forward PnL is nonpositive.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260515T160221Z` | 824 | 2 | 2026-05-15T16:02:42.302054+00:00 | 2026-05-15T16:17:40.828232+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `blend_90_10_same_side_ev_step_3c_late_70_240_ev0`
- accounting_mode: all_entries
- gate_count: 4
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 106.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 35.333333333333336
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 106.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY151215-15` | 2026-05-15T16:11:00.977212+00:00 | 239.0 | no | 30.00 | 11.30 | -30.00 | no | 11.66 | -30.00 | False |
| `KXBTC15M-26MAY151215-15` | 2026-05-15T16:11:20.735888+00:00 | 219.3 | yes | 31.00 | 0.43 | 67.00 | yes | 1.01 | 67.00 | True |
| `KXBTC15M-26MAY151215-15` | 2026-05-15T16:11:37.639390+00:00 | 202.4 | yes | 29.00 | 4.06 | 69.00 | yes | 4.61 | 69.00 | True |

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

- variant: `rv600_primary_side_flip_only_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 1
- distinct_markets: 1
- selected_pnl_cents: -40.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: -40.0
- positive_root_rate: 0.0
- positive_market_rate: 0.0
- max_single_market_pnl_share: 0.0
- last_window_pnl_cents: -40.0
- early_gt_420s_entries: 1
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY151215-15` | 2026-05-15T16:05:00.939692+00:00 | 599.1 | no | 40.00 | 4.26 | -40.00 | no | 6.67 | -40.00 | False |

