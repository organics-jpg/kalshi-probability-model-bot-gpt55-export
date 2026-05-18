# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-14T13:33:11+00:00
- roots: 1
- total_candidate_rows: 781
- total_settled_markets: 2
- locked_total_entries: 15
- locked_total_pnl_cents: -388.0
- conclusion: Locked entries exist, but RV600-primary native forward PnL is nonpositive.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260514T130107Z` | 781 | 2 | 2026-05-14T13:01:35.414600+00:00 | 2026-05-14T13:16:34.025511+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `blend_95_5_same_side_ev_step_3c_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 4
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 10.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 3.3333333333333335
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 10.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;avg_entry_below_10c;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY140915-15` | 2026-05-14T13:05:01.372757+00:00 | 598.6 | no | 20.00 | 1.02 | -20.00 | no | 0.47 | -20.00 | False |
| `KXBTC15M-26MAY140915-15` | 2026-05-14T13:05:23.891367+00:00 | 576.1 | yes | 84.00 | 0.36 | 15.00 | yes | 1.02 | 15.00 | True |
| `KXBTC15M-26MAY140915-15` | 2026-05-14T13:05:34.628499+00:00 | 565.4 | yes | 84.00 | 3.42 | 15.00 | yes | 4.10 | 15.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_single_market_late_70_180_ev10`
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
- selected_pnl_cents: -20.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: -20.0
- positive_root_rate: 0.0
- positive_market_rate: 0.0
- max_single_market_pnl_share: 0.0
- last_window_pnl_cents: -20.0
- early_gt_420s_entries: 1
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY140915-15` | 2026-05-14T13:05:00.373233+00:00 | 599.6 | no | 20.00 | 9.91 | -20.00 | no | -1.78 | -20.00 | False |

