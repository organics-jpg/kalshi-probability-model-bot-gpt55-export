# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-13T22:17:21+00:00
- roots: 1
- total_candidate_rows: 784
- total_settled_markets: 2
- locked_total_entries: 10
- locked_total_pnl_cents: 740.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260513T215130Z` | 784 | 2 | 2026-05-13T21:51:32.612613+00:00 | 2026-05-13T22:06:31.195957+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 6
- distinct_markets: 2
- selected_pnl_cents: 281.0
- matched_v28_delta_cents: 122.0
- avg_pnl_per_entry_cents: 46.833333333333336
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 0.6868327402135231
- last_window_pnl_cents: 281.0
- early_gt_420s_entries: 6
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131800-00` | 2026-05-13T21:51:32.612613+00:00 | 507.4 | no | 35.00 | 10.48 | 63.00 | no | 4.78 | 63.00 | False |
| `KXBTC15M-26MAY131800-00` | 2026-05-13T21:51:33.625621+00:00 | 506.4 | no | 33.00 | 12.47 | 65.00 | no | 6.77 | 65.00 | True |
| `KXBTC15M-26MAY131800-00` | 2026-05-13T21:51:34.630245+00:00 | 505.4 | no | 33.00 | 11.50 | 65.00 | no | 4.05 | 65.00 | True |
| `KXBTC15M-26MAY131815-15` | 2026-05-13T22:05:01.912837+00:00 | 598.1 | no | 69.00 | 0.22 | 29.00 | yes | -0.74 | -32.00 | False |
| `KXBTC15M-26MAY131815-15` | 2026-05-13T22:05:02.923020+00:00 | 597.1 | no | 68.00 | 1.26 | 30.00 | no | -1.24 | 30.00 | True |
| `KXBTC15M-26MAY131815-15` | 2026-05-13T22:05:03.919764+00:00 | 596.1 | no | 69.00 | 0.27 | 29.00 | yes | -0.77 | -32.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 6
- distinct_markets: 2
- selected_pnl_cents: 281.0
- matched_v28_delta_cents: 122.0
- avg_pnl_per_entry_cents: 46.833333333333336
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 0.6868327402135231
- last_window_pnl_cents: 281.0
- early_gt_420s_entries: 6
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131800-00` | 2026-05-13T21:51:32.612613+00:00 | 507.4 | no | 35.00 | 10.48 | 63.00 | no | 4.78 | 63.00 | False |
| `KXBTC15M-26MAY131800-00` | 2026-05-13T21:51:33.625621+00:00 | 506.4 | no | 33.00 | 12.47 | 65.00 | no | 6.77 | 65.00 | True |
| `KXBTC15M-26MAY131800-00` | 2026-05-13T21:51:34.630245+00:00 | 505.4 | no | 33.00 | 11.50 | 65.00 | no | 4.05 | 65.00 | True |
| `KXBTC15M-26MAY131815-15` | 2026-05-13T22:05:01.912837+00:00 | 598.1 | no | 69.00 | 0.22 | 29.00 | yes | -0.74 | -32.00 | False |
| `KXBTC15M-26MAY131815-15` | 2026-05-13T22:05:02.923020+00:00 | 597.1 | no | 68.00 | 1.26 | 30.00 | no | -1.24 | 30.00 | True |
| `KXBTC15M-26MAY131815-15` | 2026-05-13T22:05:03.919764+00:00 | 596.1 | no | 69.00 | 0.27 | 29.00 | yes | -0.77 | -32.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_max_3_entries_mid_120_420_ev12`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 2
- distinct_markets: 1
- selected_pnl_cents: 148.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 74.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 148.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 2
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131800-00` | 2026-05-13T21:55:01.126744+00:00 | 298.9 | no | 24.00 | 12.68 | 74.00 | no | 14.52 | 74.00 | False |
| `KXBTC15M-26MAY131800-00` | 2026-05-13T21:55:02.127173+00:00 | 297.9 | no | 24.00 | 12.66 | 74.00 | no | 14.50 | 74.00 | True |

