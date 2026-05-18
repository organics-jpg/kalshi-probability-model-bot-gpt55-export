# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-13T21:48:02+00:00
- roots: 4
- total_candidate_rows: 3226
- total_settled_markets: 8
- locked_total_entries: 47
- locked_total_pnl_cents: 447.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260513T195001Z` | 776 | 2 | 2026-05-13T19:50:03.349516+00:00 | 2026-05-13T20:05:02.418266+00:00 |
| `rv600_next_evidence_shadow_20260513T202034Z` | 810 | 2 | 2026-05-13T20:20:36.510758+00:00 | 2026-05-13T20:35:35.780283+00:00 |
| `rv600_next_evidence_shadow_20260513T205117Z` | 817 | 2 | 2026-05-13T20:51:19.560041+00:00 | 2026-05-13T21:06:18.752489+00:00 |
| `rv600_next_evidence_shadow_20260513T211949Z` | 823 | 2 | 2026-05-13T21:19:51.564973+00:00 | 2026-05-13T21:34:50.672631+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_late_70_180_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 12
- distinct_markets: 4
- selected_pnl_cents: 350.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 29.166666666666668
- positive_root_rate: 0.5
- positive_market_rate: 0.5
- max_single_market_pnl_share: 0.5742857142857143
- last_window_pnl_cents: 178.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 12
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:57:00.071878+00:00 | 179.9 | no | 3.00 | 4.27 | -3.00 | no | 11.63 | -3.00 | False |
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:57:01.070427+00:00 | 178.9 | no | 3.00 | 4.58 | -3.00 | no | 12.01 | -3.00 | True |
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:57:02.111479+00:00 | 177.9 | no | 3.00 | 4.50 | -3.00 | no | 11.94 | -3.00 | True |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:27:00.135768+00:00 | 179.9 | no | 31.00 | 13.68 | 67.00 | no | 14.20 | 67.00 | False |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:27:01.132038+00:00 | 178.9 | no | 31.00 | 13.68 | 67.00 | no | 14.05 | 67.00 | True |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:27:02.138889+00:00 | 177.9 | no | 31.00 | 13.66 | 67.00 | no | 14.03 | 67.00 | True |
| `KXBTC15M-26MAY131700-00` | 2026-05-13T20:57:00.866577+00:00 | 179.1 | yes | 6.00 | 10.43 | -6.00 | yes | 14.53 | -6.00 | False |
| `KXBTC15M-26MAY131700-00` | 2026-05-13T20:57:01.866957+00:00 | 178.1 | yes | 7.00 | 8.10 | -7.00 | yes | 12.08 | -7.00 | True |
| `KXBTC15M-26MAY131700-00` | 2026-05-13T20:57:02.876291+00:00 | 177.1 | yes | 7.00 | 9.95 | -7.00 | yes | 13.84 | -7.00 | True |
| `KXBTC15M-26MAY131730-30` | 2026-05-13T21:27:01.047102+00:00 | 179.0 | no | 38.00 | 1.13 | 60.00 | no | 1.20 | 60.00 | False |
| `KXBTC15M-26MAY131730-30` | 2026-05-13T21:27:02.038308+00:00 | 178.0 | no | 38.00 | 1.11 | 60.00 | no | 1.17 | 60.00 | True |
| `KXBTC15M-26MAY131730-30` | 2026-05-13T21:27:03.047436+00:00 | 177.0 | no | 40.00 | 5.24 | 58.00 | no | 4.47 | 58.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_late_70_180_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 12
- distinct_markets: 4
- selected_pnl_cents: 350.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 29.166666666666668
- positive_root_rate: 0.5
- positive_market_rate: 0.5
- max_single_market_pnl_share: 0.5742857142857143
- last_window_pnl_cents: 178.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 12
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:57:00.071878+00:00 | 179.9 | no | 3.00 | 4.27 | -3.00 | no | 11.63 | -3.00 | False |
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:57:01.070427+00:00 | 178.9 | no | 3.00 | 4.58 | -3.00 | no | 12.01 | -3.00 | True |
| `KXBTC15M-26MAY131600-00` | 2026-05-13T19:57:02.111479+00:00 | 177.9 | no | 3.00 | 4.50 | -3.00 | no | 11.94 | -3.00 | True |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:27:00.135768+00:00 | 179.9 | no | 31.00 | 13.68 | 67.00 | no | 14.20 | 67.00 | False |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:27:01.132038+00:00 | 178.9 | no | 31.00 | 13.68 | 67.00 | no | 14.05 | 67.00 | True |
| `KXBTC15M-26MAY131630-30` | 2026-05-13T20:27:02.138889+00:00 | 177.9 | no | 31.00 | 13.66 | 67.00 | no | 14.03 | 67.00 | True |
| `KXBTC15M-26MAY131700-00` | 2026-05-13T20:57:00.866577+00:00 | 179.1 | yes | 6.00 | 10.43 | -6.00 | yes | 14.53 | -6.00 | False |
| `KXBTC15M-26MAY131700-00` | 2026-05-13T20:57:01.866957+00:00 | 178.1 | yes | 7.00 | 8.10 | -7.00 | yes | 12.08 | -7.00 | True |
| `KXBTC15M-26MAY131700-00` | 2026-05-13T20:57:02.876291+00:00 | 177.1 | yes | 7.00 | 9.95 | -7.00 | yes | 13.84 | -7.00 | True |
| `KXBTC15M-26MAY131730-30` | 2026-05-13T21:27:01.047102+00:00 | 179.0 | no | 38.00 | 1.13 | 60.00 | no | 1.20 | 60.00 | False |
| `KXBTC15M-26MAY131730-30` | 2026-05-13T21:27:02.038308+00:00 | 178.0 | no | 38.00 | 1.11 | 60.00 | no | 1.17 | 60.00 | True |
| `KXBTC15M-26MAY131730-30` | 2026-05-13T21:27:03.047436+00:00 | 177.0 | no | 40.00 | 5.24 | 58.00 | no | 4.47 | 58.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_max_3_entries_mid_120_420_ev12`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 10
- distinct_markets: 4
- selected_pnl_cents: 98.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 9.8
- positive_root_rate: 0.25
- positive_market_rate: 0.25
- max_single_market_pnl_share: 1.9081632653061225
- last_window_pnl_cents: -13.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 10
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct

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
| `KXBTC15M-26MAY131730-30` | 2026-05-13T21:27:51.042293+00:00 | 129.0 | yes | 13.00 | 12.86 | -13.00 | yes | 16.31 | -13.00 | False |

