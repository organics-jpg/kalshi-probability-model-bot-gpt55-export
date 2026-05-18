# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-15T06:02:57+00:00
- roots: 1
- total_candidate_rows: 719
- total_settled_markets: 2
- locked_total_entries: 2
- locked_total_pnl_cents: -28.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260515T053557Z` | 719 | 2 | 2026-05-15T05:36:15.984489+00:00 | 2026-05-15T05:51:14.680728+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `blend_95_5_same_side_refresh_120s_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 4
- accepted_entries: 5
- distinct_markets: 2
- selected_pnl_cents: 32.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 6.4
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 0.875
- last_window_pnl_cents: 32.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 2
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;avg_entry_below_10c;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150145-45` | 2026-05-15T05:36:15.984489+00:00 | 524.0 | no | 96.00 | 2.68 | 3.00 | no | 2.94 | 3.00 | False |
| `KXBTC15M-26MAY150145-45` | 2026-05-15T05:38:36.316499+00:00 | 383.7 | no | 98.00 | 0.99 | 1.00 | no | 1.00 | 1.00 | True |
| `KXBTC15M-26MAY150145-45` | 2026-05-15T05:40:40.128098+00:00 | 259.9 | yes | 0.00 | 0.00 | -0.00 | yes | 0.00 | -0.00 | True |
| `KXBTC15M-26MAY150200-00` | 2026-05-15T05:50:00.792656+00:00 | 599.2 | yes | 24.00 | 0.96 | -24.00 | yes | 0.89 | -24.00 | False |
| `KXBTC15M-26MAY150200-00` | 2026-05-15T05:51:14.680728+00:00 | 525.3 | no | 46.00 | 0.35 | 52.00 | no | 0.24 | 52.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_same_side_refresh_120s_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 5
- distinct_markets: 2
- selected_pnl_cents: 26.0
- matched_v28_delta_cents: -7.0
- avg_pnl_per_entry_cents: 5.2
- positive_root_rate: 1.0
- positive_market_rate: 0.5
- max_single_market_pnl_share: 1.0769230769230769
- last_window_pnl_cents: 26.0
- early_gt_420s_entries: 4
- locked_70_420s_entries: 1
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;avg_entry_below_10c;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150145-45` | 2026-05-15T05:36:15.984489+00:00 | 524.0 | yes | 4.00 | 1.32 | -4.00 | no | 2.94 | 3.00 | False |
| `KXBTC15M-26MAY150145-45` | 2026-05-15T05:37:19.327589+00:00 | 460.7 | no | 98.00 | 0.01 | 1.00 | no | 1.00 | 1.00 | True |
| `KXBTC15M-26MAY150145-45` | 2026-05-15T05:39:19.632572+00:00 | 340.4 | no | 98.00 | 0.50 | 1.00 | no | 1.00 | 1.00 | True |
| `KXBTC15M-26MAY150200-00` | 2026-05-15T05:50:00.792656+00:00 | 599.2 | yes | 24.00 | 2.22 | -24.00 | yes | 0.89 | -24.00 | False |
| `KXBTC15M-26MAY150200-00` | 2026-05-15T05:51:14.680728+00:00 | 525.3 | no | 46.00 | 2.34 | 52.00 | no | 0.24 | 52.00 | True |

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

