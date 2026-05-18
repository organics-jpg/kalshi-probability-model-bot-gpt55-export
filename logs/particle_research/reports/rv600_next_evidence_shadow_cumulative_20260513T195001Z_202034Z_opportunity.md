# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-13T20:47:04+00:00
- roots: 2
- total_candidate_rows: 1586
- total_settled_markets: 4
- locked_total_entries: 28
- locked_total_pnl_cents: 638.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260513T195001Z` | 776 | 2 | 2026-05-13T19:50:03.349516+00:00 | 2026-05-13T20:05:02.418266+00:00 |
| `rv600_next_evidence_shadow_20260513T202034Z` | 810 | 2 | 2026-05-13T20:20:36.510758+00:00 | 2026-05-13T20:35:35.780283+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev2`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 11
- distinct_markets: 4
- selected_pnl_cents: 258.0
- matched_v28_delta_cents: 397.0
- avg_pnl_per_entry_cents: 23.454545454545453
- positive_root_rate: 1.0
- positive_market_rate: 0.5
- max_single_market_pnl_share: 0.9457364341085271
- last_window_pnl_cents: 148.0
- early_gt_420s_entries: 11
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:50:03.349516+00:00 | 596.7 | yes | 34.00 | 5.72 | 64.00 | no | 2.47 | -67.00 | False |
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:50:04.362166+00:00 | 595.6 | yes | 33.00 | 7.96 | 65.00 | no | -1.01 | -68.00 | True |
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:50:05.354000+00:00 | 594.6 | yes | 33.00 | 2.31 | 65.00 | no | 0.19 | -68.00 | True |
| `KXBTC15M-26MAY131615-15` | 2026-05-13T20:05:00.382909+00:00 | 599.6 | no | 43.00 | 6.64 | -43.00 | no | 7.60 | -43.00 | False |
| `KXBTC15M-26MAY131615-15` | 2026-05-13T20:05:02.418266+00:00 | 597.6 | no | 41.00 | 4.34 | -41.00 | no | 6.81 | -41.00 | True |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:20:36.510758+00:00 | 563.5 | no | 18.00 | 21.96 | 80.00 | no | 9.12 | 80.00 | False |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:20:37.511033+00:00 | 562.5 | no | 17.00 | 23.57 | 82.00 | no | 10.87 | 82.00 | True |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:20:38.536741+00:00 | 561.5 | no | 17.00 | 23.56 | 82.00 | no | 10.85 | 82.00 | True |
| `KXBTC15M-26MAY131645-45` | 2026-05-13T20:35:00.772786+00:00 | 599.2 | no | 32.00 | 3.17 | -32.00 | no | 5.66 | -32.00 | False |
| `KXBTC15M-26MAY131645-45` | 2026-05-13T20:35:01.811656+00:00 | 598.2 | no | 32.00 | 3.16 | -32.00 | no | 5.65 | -32.00 | True |
| `KXBTC15M-26MAY131645-45` | 2026-05-13T20:35:02.865599+00:00 | 597.1 | no | 32.00 | 3.15 | -32.00 | no | 5.64 | -32.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev2`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 11
- distinct_markets: 4
- selected_pnl_cents: 258.0
- matched_v28_delta_cents: 397.0
- avg_pnl_per_entry_cents: 23.454545454545453
- positive_root_rate: 1.0
- positive_market_rate: 0.5
- max_single_market_pnl_share: 0.9457364341085271
- last_window_pnl_cents: 148.0
- early_gt_420s_entries: 11
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:50:03.349516+00:00 | 596.7 | yes | 34.00 | 5.72 | 64.00 | no | 2.47 | -67.00 | False |
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:50:04.362166+00:00 | 595.6 | yes | 33.00 | 7.96 | 65.00 | no | -1.01 | -68.00 | True |
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:50:05.354000+00:00 | 594.6 | yes | 33.00 | 2.31 | 65.00 | no | 0.19 | -68.00 | True |
| `KXBTC15M-26MAY131615-15` | 2026-05-13T20:05:00.382909+00:00 | 599.6 | no | 43.00 | 6.64 | -43.00 | no | 7.60 | -43.00 | False |
| `KXBTC15M-26MAY131615-15` | 2026-05-13T20:05:02.418266+00:00 | 597.6 | no | 41.00 | 4.34 | -41.00 | no | 6.81 | -41.00 | True |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:20:36.510758+00:00 | 563.5 | no | 18.00 | 21.96 | 80.00 | no | 9.12 | 80.00 | False |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:20:37.511033+00:00 | 562.5 | no | 17.00 | 23.57 | 82.00 | no | 10.87 | 82.00 | True |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:20:38.536741+00:00 | 561.5 | no | 17.00 | 23.56 | 82.00 | no | 10.85 | 82.00 | True |
| `KXBTC15M-26MAY131645-45` | 2026-05-13T20:35:00.772786+00:00 | 599.2 | no | 32.00 | 3.17 | -32.00 | no | 5.66 | -32.00 | False |
| `KXBTC15M-26MAY131645-45` | 2026-05-13T20:35:01.811656+00:00 | 598.2 | no | 32.00 | 3.16 | -32.00 | no | 5.65 | -32.00 | True |
| `KXBTC15M-26MAY131645-45` | 2026-05-13T20:35:02.865599+00:00 | 597.1 | no | 32.00 | 3.15 | -32.00 | no | 5.64 | -32.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_max_3_entries_mid_120_420_ev12`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 6
- distinct_markets: 2
- selected_pnl_cents: 138.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 23.0
- positive_root_rate: 0.5
- positive_market_rate: 0.5
- max_single_market_pnl_share: 1.355072463768116
- last_window_pnl_cents: 187.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 6
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:54:57.375623+00:00 | 302.6 | no | 24.00 | 12.50 | -24.00 | no | 16.07 | -24.00 | False |
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:55:56.787769+00:00 | 243.2 | no | 17.00 | 13.94 | -17.00 | no | 19.65 | -17.00 | True |
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:56:19.102588+00:00 | 220.9 | no | 8.00 | 14.96 | -8.00 | no | 21.55 | -8.00 | True |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:25:03.214504+00:00 | 296.8 | no | 31.00 | 12.27 | 67.00 | no | 13.94 | 67.00 | False |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:25:45.085072+00:00 | 254.9 | no | 38.00 | 12.42 | 60.00 | no | 12.63 | 60.00 | True |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:25:46.160382+00:00 | 253.8 | no | 38.00 | 12.43 | 60.00 | no | 12.64 | 60.00 | True |

