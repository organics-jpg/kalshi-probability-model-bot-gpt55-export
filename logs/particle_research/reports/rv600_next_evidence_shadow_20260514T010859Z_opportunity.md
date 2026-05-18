# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-14T01:35:30+00:00
- roots: 1
- total_candidate_rows: 819
- total_settled_markets: 2
- locked_total_entries: 14
- locked_total_pnl_cents: 943.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260514T010859Z` | 819 | 2 | 2026-05-14T01:09:02.233378+00:00 | 2026-05-14T01:24:01.102140+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev6`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 6
- distinct_markets: 2
- selected_pnl_cents: 337.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 56.166666666666664
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 0.5637982195845698
- last_window_pnl_cents: 337.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY132115-15` | 2026-05-14T01:09:09.936736+00:00 | 350.1 | no | 36.00 | 10.68 | 62.00 | no | 8.15 | 62.00 | False |
| `KXBTC15M-26MAY132115-15` | 2026-05-14T01:09:10.993993+00:00 | 349.0 | no | 34.00 | 11.15 | 64.00 | no | 7.54 | 64.00 | True |
| `KXBTC15M-26MAY132115-15` | 2026-05-14T01:09:11.993284+00:00 | 348.0 | no | 34.00 | 10.84 | 64.00 | no | 7.36 | 64.00 | True |
| `KXBTC15M-26MAY132130-30` | 2026-05-14T01:20:56.836891+00:00 | 543.2 | no | 49.00 | 6.22 | 49.00 | no | 6.25 | 49.00 | False |
| `KXBTC15M-26MAY132130-30` | 2026-05-14T01:20:57.843017+00:00 | 542.2 | no | 49.00 | 6.22 | 49.00 | no | 6.25 | 49.00 | True |
| `KXBTC15M-26MAY132130-30` | 2026-05-14T01:20:59.042331+00:00 | 541.0 | no | 49.00 | 6.22 | 49.00 | no | 6.26 | 49.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev6`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 6
- distinct_markets: 2
- selected_pnl_cents: 337.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 56.166666666666664
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 0.5637982195845698
- last_window_pnl_cents: 337.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY132115-15` | 2026-05-14T01:09:09.936736+00:00 | 350.1 | no | 36.00 | 10.68 | 62.00 | no | 8.15 | 62.00 | False |
| `KXBTC15M-26MAY132115-15` | 2026-05-14T01:09:10.993993+00:00 | 349.0 | no | 34.00 | 11.15 | 64.00 | no | 7.54 | 64.00 | True |
| `KXBTC15M-26MAY132115-15` | 2026-05-14T01:09:11.993284+00:00 | 348.0 | no | 34.00 | 10.84 | 64.00 | no | 7.36 | 64.00 | True |
| `KXBTC15M-26MAY132130-30` | 2026-05-14T01:20:56.836891+00:00 | 543.2 | no | 49.00 | 6.22 | 49.00 | no | 6.25 | 49.00 | False |
| `KXBTC15M-26MAY132130-30` | 2026-05-14T01:20:57.843017+00:00 | 542.2 | no | 49.00 | 6.22 | 49.00 | no | 6.25 | 49.00 | True |
| `KXBTC15M-26MAY132130-30` | 2026-05-14T01:20:59.042331+00:00 | 541.0 | no | 49.00 | 6.22 | 49.00 | no | 6.26 | 49.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_max_3_entries_mid_120_420_ev12`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 202.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 67.33333333333333
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 202.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY132115-15` | 2026-05-14T01:09:14.260092+00:00 | 345.7 | no | 31.00 | 12.11 | 67.00 | no | 7.93 | 67.00 | False |
| `KXBTC15M-26MAY132115-15` | 2026-05-14T01:09:15.270137+00:00 | 344.7 | no | 30.00 | 12.43 | 68.00 | no | 8.15 | 68.00 | True |
| `KXBTC15M-26MAY132115-15` | 2026-05-14T01:10:21.176236+00:00 | 278.8 | no | 31.00 | 13.11 | 67.00 | no | 14.00 | 67.00 | True |

