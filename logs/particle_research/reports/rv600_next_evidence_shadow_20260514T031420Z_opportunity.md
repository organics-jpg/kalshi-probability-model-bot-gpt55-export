# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-14T03:44:25+00:00
- roots: 1
- total_candidate_rows: 812
- total_settled_markets: 1
- locked_total_entries: 14
- locked_total_pnl_cents: 1167.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260514T031420Z` | 812 | 1 | 2026-05-14T03:15:25.872395+00:00 | 2026-05-14T03:29:16.534145+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_base_70_420_ev2`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 291.0
- matched_v28_delta_cents: 585.0
- avg_pnl_per_entry_cents: 97.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 291.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY132330-30` | 2026-05-14T03:23:06.978707+00:00 | 413.0 | yes | 1.00 | 2.19 | 98.00 | no | -0.05 | -99.00 | False |
| `KXBTC15M-26MAY132330-30` | 2026-05-14T03:23:10.025949+00:00 | 410.0 | yes | 2.00 | 2.84 | 97.00 | no | 0.84 | -98.00 | True |
| `KXBTC15M-26MAY132330-30` | 2026-05-14T03:23:11.058086+00:00 | 408.9 | yes | 3.00 | 2.02 | 96.00 | no | 1.82 | -97.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_base_70_420_ev2`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 291.0
- matched_v28_delta_cents: 585.0
- avg_pnl_per_entry_cents: 97.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 291.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY132330-30` | 2026-05-14T03:23:06.978707+00:00 | 413.0 | yes | 1.00 | 2.19 | 98.00 | no | -0.05 | -99.00 | False |
| `KXBTC15M-26MAY132330-30` | 2026-05-14T03:23:10.025949+00:00 | 410.0 | yes | 2.00 | 2.84 | 97.00 | no | 0.84 | -98.00 | True |
| `KXBTC15M-26MAY132330-30` | 2026-05-14T03:23:11.058086+00:00 | 408.9 | yes | 3.00 | 2.02 | 96.00 | no | 1.82 | -97.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_max_3_entries_mid_120_420_ev12`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 250.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 83.33333333333333
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 250.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY132330-30` | 2026-05-14T03:27:13.393478+00:00 | 166.6 | yes | 15.00 | 12.02 | 84.00 | yes | -0.74 | 84.00 | False |
| `KXBTC15M-26MAY132330-30` | 2026-05-14T03:27:19.677118+00:00 | 160.3 | yes | 16.00 | 12.49 | 83.00 | yes | -0.08 | 83.00 | True |
| `KXBTC15M-26MAY132330-30` | 2026-05-14T03:27:20.698222+00:00 | 159.3 | yes | 16.00 | 12.71 | 83.00 | yes | 0.22 | 83.00 | True |

