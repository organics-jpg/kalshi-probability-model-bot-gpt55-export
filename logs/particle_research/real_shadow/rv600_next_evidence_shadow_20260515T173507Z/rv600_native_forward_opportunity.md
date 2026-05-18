# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-15T18:03:33+00:00
- roots: 1
- total_candidate_rows: 849
- total_settled_markets: 2
- locked_total_entries: 16
- locked_total_pnl_cents: -500.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260515T173507Z` | 849 | 2 | 2026-05-15T17:35:48.411937+00:00 | 2026-05-15T17:50:46.712577+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `blend_95_5_same_side_ev_step_5c_late_70_300_ev0`
- accounting_mode: all_entries
- gate_count: 4
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 134.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 44.666666666666664
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 134.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY151345-45` | 2026-05-15T17:40:00.432225+00:00 | 299.6 | no | 14.00 | 13.27 | -14.00 | no | 13.66 | -14.00 | False |
| `KXBTC15M-26MAY151345-45` | 2026-05-15T17:43:12.805139+00:00 | 107.2 | yes | 28.00 | 3.17 | 70.00 | yes | 3.53 | 70.00 | True |
| `KXBTC15M-26MAY151345-45` | 2026-05-15T17:43:49.435123+00:00 | 70.6 | yes | 20.00 | 9.25 | 78.00 | yes | 9.67 | 78.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_side_flip_only_late_70_300_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 2
- distinct_markets: 1
- selected_pnl_cents: 64.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 32.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 64.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 2
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY151345-45` | 2026-05-15T17:40:00.432225+00:00 | 299.6 | no | 14.00 | 5.73 | -14.00 | no | 13.66 | -14.00 | False |
| `KXBTC15M-26MAY151345-45` | 2026-05-15T17:43:49.435123+00:00 | 70.6 | yes | 20.00 | 1.19 | 78.00 | yes | 9.67 | 78.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_side_flip_only_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 2
- distinct_markets: 1
- selected_pnl_cents: -2.0
- matched_v28_delta_cents: 57.0
- avg_pnl_per_entry_cents: -1.0
- positive_root_rate: 0.0
- positive_market_rate: 0.0
- max_single_market_pnl_share: 0.0
- last_window_pnl_cents: -2.0
- early_gt_420s_entries: 2
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY151345-45` | 2026-05-15T17:35:48.411937+00:00 | 551.6 | no | 29.00 | 10.20 | -29.00 | no | 6.30 | -29.00 | False |
| `KXBTC15M-26MAY151345-45` | 2026-05-15T17:35:50.653755+00:00 | 549.3 | yes | 71.00 | 5.56 | 27.00 | no | 6.12 | -30.00 | True |

