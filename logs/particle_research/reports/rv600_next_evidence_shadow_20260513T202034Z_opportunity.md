# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-13T20:46:30+00:00
- roots: 1
- total_candidate_rows: 810
- total_settled_markets: 2
- locked_total_entries: 14
- locked_total_pnl_cents: 875.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260513T202034Z` | 810 | 2 | 2026-05-13T20:20:36.510758+00:00 | 2026-05-13T20:35:35.780283+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `blend_95_5_max_3_entries_broad_70_600_ev10`
- accounting_mode: all_entries
- gate_count: 4
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 246.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 82.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 246.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:20:37.511033+00:00 | 562.5 | no | 17.00 | 11.50 | 82.00 | no | 10.87 | 82.00 | False |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:20:38.536741+00:00 | 561.5 | no | 17.00 | 11.48 | 82.00 | no | 10.85 | 82.00 | True |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:20:39.532681+00:00 | 560.5 | no | 17.00 | 10.57 | 82.00 | no | 10.83 | 82.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev8`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 244.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 81.33333333333333
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 244.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:20:36.510758+00:00 | 563.5 | no | 18.00 | 21.96 | 80.00 | no | 9.12 | 80.00 | False |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:20:37.511033+00:00 | 562.5 | no | 17.00 | 23.57 | 82.00 | no | 10.87 | 82.00 | True |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:20:38.536741+00:00 | 561.5 | no | 17.00 | 23.56 | 82.00 | no | 10.85 | 82.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_max_3_entries_mid_120_420_ev12`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 187.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 62.333333333333336
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 187.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:25:03.214504+00:00 | 296.8 | no | 31.00 | 12.27 | 67.00 | no | 13.94 | 67.00 | False |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:25:45.085072+00:00 | 254.9 | no | 38.00 | 12.42 | 60.00 | no | 12.63 | 60.00 | True |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:25:46.160382+00:00 | 253.8 | no | 38.00 | 12.43 | 60.00 | no | 12.64 | 60.00 | True |

