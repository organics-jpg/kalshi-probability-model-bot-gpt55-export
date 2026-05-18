# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-15T17:18:26+00:00
- roots: 1
- total_candidate_rows: 866
- total_settled_markets: 2
- locked_total_entries: 8
- locked_total_pnl_cents: -111.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260515T164836Z` | 866 | 2 | 2026-05-15T16:48:53.069590+00:00 | 2026-05-15T17:03:51.879296+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `blend_95_5_max_3_entries_base_70_420_ev4`
- accounting_mode: all_entries
- gate_count: 4
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 240.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 80.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 240.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY151300-00` | 2026-05-15T16:53:06.879277+00:00 | 413.1 | yes | 18.00 | 5.69 | 80.00 | yes | 6.01 | 80.00 | False |
| `KXBTC15M-26MAY151300-00` | 2026-05-15T16:53:07.893000+00:00 | 412.1 | yes | 18.00 | 4.29 | 80.00 | yes | 4.61 | 80.00 | True |
| `KXBTC15M-26MAY151300-00` | 2026-05-15T16:53:08.899148+00:00 | 411.1 | yes | 18.00 | 4.26 | 80.00 | yes | 4.58 | 80.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_2_entries_late_70_300_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 2
- distinct_markets: 1
- selected_pnl_cents: 142.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 71.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 142.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 2
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY151300-00` | 2026-05-15T16:55:00.913316+00:00 | 299.1 | yes | 26.00 | 0.29 | 72.00 | yes | 6.28 | 72.00 | False |
| `KXBTC15M-26MAY151300-00` | 2026-05-15T16:55:01.908154+00:00 | 298.1 | yes | 28.00 | 0.63 | 70.00 | yes | 6.08 | 70.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_side_flip_only_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 2
- distinct_markets: 1
- selected_pnl_cents: 21.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 10.5
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 21.0
- early_gt_420s_entries: 1
- locked_70_420s_entries: 1
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY151300-00` | 2026-05-15T16:50:03.010593+00:00 | 597.0 | no | 50.00 | 4.57 | -50.00 | no | 2.70 | -50.00 | False |
| `KXBTC15M-26MAY151300-00` | 2026-05-15T16:58:35.815907+00:00 | 84.2 | yes | 27.00 | 5.42 | 71.00 | yes | 10.75 | 71.00 | True |

