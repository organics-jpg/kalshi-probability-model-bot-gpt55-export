# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-15T04:19:28+00:00
- roots: 1
- total_candidate_rows: 789
- total_settled_markets: 2
- locked_total_entries: 2
- locked_total_pnl_cents: 27.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260515T034820Z` | 789 | 2 | 2026-05-15T03:49:19.319847+00:00 | 2026-05-15T04:04:18.016754+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `blend_80_20_max_3_entries_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 4
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 168.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 56.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 168.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150000-00` | 2026-05-15T03:50:23.190699+00:00 | 576.8 | yes | 42.00 | 4.80 | 56.00 | yes | 5.69 | 56.00 | False |
| `KXBTC15M-26MAY150000-00` | 2026-05-15T03:50:24.225899+00:00 | 575.8 | yes | 42.00 | 4.79 | 56.00 | yes | 5.69 | 56.00 | True |
| `KXBTC15M-26MAY150000-00` | 2026-05-15T03:50:25.312494+00:00 | 574.7 | yes | 42.00 | 5.65 | 56.00 | yes | 6.44 | 56.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 132.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 44.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 132.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150000-00` | 2026-05-15T03:51:20.273795+00:00 | 519.7 | yes | 54.00 | 4.02 | 44.00 | yes | 1.67 | 44.00 | False |
| `KXBTC15M-26MAY150000-00` | 2026-05-15T03:51:21.265215+00:00 | 518.7 | yes | 54.00 | 4.03 | 44.00 | yes | 1.67 | 44.00 | True |
| `KXBTC15M-26MAY150000-00` | 2026-05-15T03:51:22.270529+00:00 | 517.7 | yes | 54.00 | 4.03 | 44.00 | yes | 1.68 | 44.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_side_flip_only_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 2
- distinct_markets: 1
- selected_pnl_cents: 27.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 13.5
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 27.0
- early_gt_420s_entries: 1
- locked_70_420s_entries: 1
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150000-00` | 2026-05-15T03:51:20.273795+00:00 | 519.7 | yes | 54.00 | 4.02 | 44.00 | yes | 1.67 | 44.00 | False |
| `KXBTC15M-26MAY150000-00` | 2026-05-15T03:54:53.310243+00:00 | 306.7 | no | 17.00 | 4.90 | -17.00 | no | 13.88 | -17.00 | True |

