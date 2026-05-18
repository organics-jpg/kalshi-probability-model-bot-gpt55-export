# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-15T12:02:28+00:00
- roots: 1
- total_candidate_rows: 831
- total_settled_markets: 2
- locked_total_entries: 2
- locked_total_pnl_cents: 47.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260515T113027Z` | 831 | 2 | 2026-05-15T11:30:46.625309+00:00 | 2026-05-15T11:45:44.997235+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_late_70_180_ev8`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 256.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 85.33333333333333
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 256.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150745-45` | 2026-05-15T11:42:03.716341+00:00 | 176.3 | yes | 13.00 | 8.35 | 86.00 | yes | 12.54 | 86.00 | False |
| `KXBTC15M-26MAY150745-45` | 2026-05-15T11:42:04.716908+00:00 | 175.3 | yes | 14.00 | 8.51 | 85.00 | yes | 12.60 | 85.00 | True |
| `KXBTC15M-26MAY150745-45` | 2026-05-15T11:42:05.717554+00:00 | 174.3 | yes | 14.00 | 8.45 | 85.00 | yes | 12.54 | 85.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_late_70_180_ev8`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 256.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 85.33333333333333
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 256.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150745-45` | 2026-05-15T11:42:03.716341+00:00 | 176.3 | yes | 13.00 | 8.35 | 86.00 | yes | 12.54 | 86.00 | False |
| `KXBTC15M-26MAY150745-45` | 2026-05-15T11:42:04.716908+00:00 | 175.3 | yes | 14.00 | 8.51 | 85.00 | yes | 12.60 | 85.00 | True |
| `KXBTC15M-26MAY150745-45` | 2026-05-15T11:42:05.717554+00:00 | 174.3 | yes | 14.00 | 8.45 | 85.00 | yes | 12.54 | 85.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_side_flip_only_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 2
- distinct_markets: 1
- selected_pnl_cents: 47.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 23.5
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 47.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 2
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150745-45` | 2026-05-15T11:40:18.338031+00:00 | 281.7 | yes | 26.00 | 4.04 | 72.00 | yes | 7.11 | 72.00 | False |
| `KXBTC15M-26MAY150745-45` | 2026-05-15T11:43:31.627503+00:00 | 88.4 | no | 25.00 | 5.80 | -25.00 | no | 9.55 | -25.00 | True |

