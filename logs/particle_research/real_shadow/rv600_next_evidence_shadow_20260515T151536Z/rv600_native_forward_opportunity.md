# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-15T15:47:27+00:00
- roots: 1
- total_candidate_rows: 818
- total_settled_markets: 2
- locked_total_entries: 1
- locked_total_pnl_cents: 70.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260515T151536Z` | 818 | 2 | 2026-05-15T15:15:53.301348+00:00 | 2026-05-15T15:30:50.675210+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `blend_95_5_max_3_entries_broad_70_600_ev6`
- accounting_mode: all_entries
- gate_count: 4
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 236.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 78.66666666666667
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 236.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY151130-30` | 2026-05-15T15:21:07.374107+00:00 | 532.6 | no | 28.00 | 6.83 | 70.00 | no | 6.92 | 70.00 | False |
| `KXBTC15M-26MAY151130-30` | 2026-05-15T15:22:23.036885+00:00 | 457.0 | no | 15.00 | 6.24 | 84.00 | no | 6.38 | 84.00 | True |
| `KXBTC15M-26MAY151130-30` | 2026-05-15T15:22:24.033383+00:00 | 456.0 | no | 17.00 | 6.91 | 82.00 | no | 7.03 | 82.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 231.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 77.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 231.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY151130-30` | 2026-05-15T15:21:07.374107+00:00 | 532.6 | no | 28.00 | 5.19 | 70.00 | no | 6.92 | 70.00 | False |
| `KXBTC15M-26MAY151130-30` | 2026-05-15T15:22:24.033383+00:00 | 456.0 | no | 17.00 | 4.54 | 82.00 | no | 7.03 | 82.00 | True |
| `KXBTC15M-26MAY151130-30` | 2026-05-15T15:22:25.060477+00:00 | 454.9 | no | 19.00 | 6.23 | 79.00 | no | 8.45 | 79.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_side_flip_only_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 1
- distinct_markets: 1
- selected_pnl_cents: 70.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 70.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 70.0
- early_gt_420s_entries: 1
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY151130-30` | 2026-05-15T15:21:07.374107+00:00 | 532.6 | no | 28.00 | 5.19 | 70.00 | no | 6.92 | 70.00 | False |

