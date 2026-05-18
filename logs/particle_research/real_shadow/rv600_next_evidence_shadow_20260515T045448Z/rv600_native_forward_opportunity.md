# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-15T05:17:31+00:00
- roots: 1
- total_candidate_rows: 751
- total_settled_markets: 2
- locked_total_entries: 13
- locked_total_pnl_cents: 9.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260515T045448Z` | 751 | 2 | 2026-05-15T04:55:02.429197+00:00 | 2026-05-15T05:10:00.938080+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_base_70_420_ev6`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 5
- distinct_markets: 2
- selected_pnl_cents: 201.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 40.2
- positive_root_rate: 1.0
- positive_market_rate: 0.5
- max_single_market_pnl_share: 1.0298507462686568
- last_window_pnl_cents: 201.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 5
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150100-00` | 2026-05-15T04:55:02.429197+00:00 | 297.6 | yes | 3.00 | 17.11 | -3.00 | yes | 0.64 | -3.00 | False |
| `KXBTC15M-26MAY150100-00` | 2026-05-15T04:55:03.427307+00:00 | 296.6 | yes | 3.00 | 16.19 | -3.00 | yes | 0.11 | -3.00 | True |
| `KXBTC15M-26MAY150115-15` | 2026-05-15T05:08:24.941669+00:00 | 395.1 | yes | 33.00 | 7.49 | 65.00 | yes | 4.98 | 65.00 | False |
| `KXBTC15M-26MAY150115-15` | 2026-05-15T05:08:26.964636+00:00 | 393.0 | yes | 27.00 | 7.49 | 71.00 | yes | 2.22 | 71.00 | True |
| `KXBTC15M-26MAY150115-15` | 2026-05-15T05:08:27.980431+00:00 | 392.0 | yes | 27.00 | 7.51 | 71.00 | yes | 2.19 | 71.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_base_70_420_ev6`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 5
- distinct_markets: 2
- selected_pnl_cents: 201.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 40.2
- positive_root_rate: 1.0
- positive_market_rate: 0.5
- max_single_market_pnl_share: 1.0298507462686568
- last_window_pnl_cents: 201.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 5
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150100-00` | 2026-05-15T04:55:02.429197+00:00 | 297.6 | yes | 3.00 | 17.11 | -3.00 | yes | 0.64 | -3.00 | False |
| `KXBTC15M-26MAY150100-00` | 2026-05-15T04:55:03.427307+00:00 | 296.6 | yes | 3.00 | 16.19 | -3.00 | yes | 0.11 | -3.00 | True |
| `KXBTC15M-26MAY150115-15` | 2026-05-15T05:08:24.941669+00:00 | 395.1 | yes | 33.00 | 7.49 | 65.00 | yes | 4.98 | 65.00 | False |
| `KXBTC15M-26MAY150115-15` | 2026-05-15T05:08:26.964636+00:00 | 393.0 | yes | 27.00 | 7.49 | 71.00 | yes | 2.22 | 71.00 | True |
| `KXBTC15M-26MAY150115-15` | 2026-05-15T05:08:27.980431+00:00 | 392.0 | yes | 27.00 | 7.51 | 71.00 | yes | 2.19 | 71.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_side_flip_only_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 2
- selected_pnl_cents: 39.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 13.0
- positive_root_rate: 1.0
- positive_market_rate: 0.5
- max_single_market_pnl_share: 1.0769230769230769
- last_window_pnl_cents: 39.0
- early_gt_420s_entries: 2
- locked_70_420s_entries: 1
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150100-00` | 2026-05-15T04:55:02.429197+00:00 | 297.6 | yes | 3.00 | 17.11 | -3.00 | yes | 0.64 | -3.00 | False |
| `KXBTC15M-26MAY150115-15` | 2026-05-15T05:05:00.507421+00:00 | 599.5 | no | 19.00 | 10.34 | -19.00 | no | 2.13 | -19.00 | False |
| `KXBTC15M-26MAY150115-15` | 2026-05-15T05:07:32.619898+00:00 | 447.4 | yes | 37.00 | 4.31 | 61.00 | yes | 2.39 | 61.00 | True |

