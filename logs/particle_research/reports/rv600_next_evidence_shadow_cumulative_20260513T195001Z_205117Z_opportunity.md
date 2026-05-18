# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-13T21:17:24+00:00
- roots: 3
- total_candidate_rows: 2403
- total_settled_markets: 6
- locked_total_entries: 42
- locked_total_pnl_cents: 512.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260513T195001Z` | 776 | 2 | 2026-05-13T19:50:03.349516+00:00 | 2026-05-13T20:05:02.418266+00:00 |
| `rv600_next_evidence_shadow_20260513T202034Z` | 810 | 2 | 2026-05-13T20:20:36.510758+00:00 | 2026-05-13T20:35:35.780283+00:00 |
| `rv600_next_evidence_shadow_20260513T205117Z` | 817 | 2 | 2026-05-13T20:51:19.560041+00:00 | 2026-05-13T21:06:18.752489+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev15`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 6
- distinct_markets: 2
- selected_pnl_cents: 188.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 31.333333333333332
- positive_root_rate: 0.3333333333333333
- positive_market_rate: 0.5
- max_single_market_pnl_share: 1.297872340425532
- last_window_pnl_cents: -56.0
- early_gt_420s_entries: 6
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:20:36.510758+00:00 | 563.5 | no | 18.00 | 21.96 | 80.00 | no | 9.12 | 80.00 | False |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:20:37.511033+00:00 | 562.5 | no | 17.00 | 23.57 | 82.00 | no | 10.87 | 82.00 | True |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:20:38.536741+00:00 | 561.5 | no | 17.00 | 23.56 | 82.00 | no | 10.85 | 82.00 | True |
| `KXBTC15M-26MAY131700-00` | 2026-05-13T20:51:19.560041+00:00 | 520.4 | yes | 19.00 | 20.90 | -19.00 | yes | 6.76 | -19.00 | False |
| `KXBTC15M-26MAY131700-00` | 2026-05-13T20:51:20.586989+00:00 | 519.4 | yes | 19.00 | 20.89 | -19.00 | yes | 6.74 | -19.00 | True |
| `KXBTC15M-26MAY131700-00` | 2026-05-13T20:51:21.602714+00:00 | 518.4 | yes | 18.00 | 21.89 | -18.00 | yes | 7.72 | -18.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev15`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 6
- distinct_markets: 2
- selected_pnl_cents: 188.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 31.333333333333332
- positive_root_rate: 0.3333333333333333
- positive_market_rate: 0.5
- max_single_market_pnl_share: 1.297872340425532
- last_window_pnl_cents: -56.0
- early_gt_420s_entries: 6
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:20:36.510758+00:00 | 563.5 | no | 18.00 | 21.96 | 80.00 | no | 9.12 | 80.00 | False |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:20:37.511033+00:00 | 562.5 | no | 17.00 | 23.57 | 82.00 | no | 10.87 | 82.00 | True |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:20:38.536741+00:00 | 561.5 | no | 17.00 | 23.56 | 82.00 | no | 10.85 | 82.00 | True |
| `KXBTC15M-26MAY131700-00` | 2026-05-13T20:51:19.560041+00:00 | 520.4 | yes | 19.00 | 20.90 | -19.00 | yes | 6.76 | -19.00 | False |
| `KXBTC15M-26MAY131700-00` | 2026-05-13T20:51:20.586989+00:00 | 519.4 | yes | 19.00 | 20.89 | -19.00 | yes | 6.74 | -19.00 | True |
| `KXBTC15M-26MAY131700-00` | 2026-05-13T20:51:21.602714+00:00 | 518.4 | yes | 18.00 | 21.89 | -18.00 | yes | 7.72 | -18.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_max_3_entries_mid_120_420_ev12`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 9
- distinct_markets: 3
- selected_pnl_cents: 111.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 12.333333333333334
- positive_root_rate: 0.3333333333333333
- positive_market_rate: 0.3333333333333333
- max_single_market_pnl_share: 1.6846846846846846
- last_window_pnl_cents: -27.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 9
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:54:57.375623+00:00 | 302.6 | no | 24.00 | 12.50 | -24.00 | no | 16.07 | -24.00 | False |
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:55:56.787769+00:00 | 243.2 | no | 17.00 | 13.94 | -17.00 | no | 19.65 | -17.00 | True |
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:56:19.102588+00:00 | 220.9 | no | 8.00 | 14.96 | -8.00 | no | 21.55 | -8.00 | True |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:25:03.214504+00:00 | 296.8 | no | 31.00 | 12.27 | 67.00 | no | 13.94 | 67.00 | False |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:25:45.085072+00:00 | 254.9 | no | 38.00 | 12.42 | 60.00 | no | 12.63 | 60.00 | True |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:25:46.160382+00:00 | 253.8 | no | 38.00 | 12.43 | 60.00 | no | 12.64 | 60.00 | True |
| `KXBTC15M-26MAY131700-00` | 2026-05-13T20:57:16.170119+00:00 | 163.8 | yes | 9.00 | 12.72 | -9.00 | yes | 16.21 | -9.00 | False |
| `KXBTC15M-26MAY131700-00` | 2026-05-13T20:57:17.224253+00:00 | 162.8 | yes | 9.00 | 12.66 | -9.00 | yes | 16.15 | -9.00 | True |
| `KXBTC15M-26MAY131700-00` | 2026-05-13T20:57:18.245692+00:00 | 161.8 | yes | 9.00 | 12.58 | -9.00 | yes | 16.08 | -9.00 | True |

