# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-15T08:33:03+00:00
- roots: 1
- total_candidate_rows: 706
- total_settled_markets: 2
- locked_total_entries: 1
- locked_total_pnl_cents: 14.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260515T080148Z` | 706 | 2 | 2026-05-15T08:02:20.070310+00:00 | 2026-05-15T08:17:18.784467+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `blend_95_5_max_3_entries_broad_70_600_ev2`
- accounting_mode: all_entries
- gate_count: 4
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 42.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 14.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 42.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150415-15` | 2026-05-15T08:05:02.643743+00:00 | 597.4 | no | 85.00 | 2.43 | 14.00 | no | 2.30 | 14.00 | False |
| `KXBTC15M-26MAY150415-15` | 2026-05-15T08:05:03.649115+00:00 | 596.4 | no | 85.00 | 2.42 | 14.00 | no | 2.32 | 14.00 | True |
| `KXBTC15M-26MAY150415-15` | 2026-05-15T08:05:04.658900+00:00 | 595.3 | no | 85.00 | 2.44 | 14.00 | no | 2.34 | 14.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 42.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 14.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 42.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150415-15` | 2026-05-15T08:05:02.643743+00:00 | 597.4 | no | 85.00 | 4.79 | 14.00 | no | 2.30 | 14.00 | False |
| `KXBTC15M-26MAY150415-15` | 2026-05-15T08:05:03.649115+00:00 | 596.4 | no | 85.00 | 4.22 | 14.00 | no | 2.32 | 14.00 | True |
| `KXBTC15M-26MAY150415-15` | 2026-05-15T08:05:04.658900+00:00 | 595.3 | no | 85.00 | 4.30 | 14.00 | no | 2.34 | 14.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_side_flip_only_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 1
- distinct_markets: 1
- selected_pnl_cents: 14.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 14.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 14.0
- early_gt_420s_entries: 1
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150415-15` | 2026-05-15T08:05:02.643743+00:00 | 597.4 | no | 85.00 | 4.79 | 14.00 | no | 2.30 | 14.00 | False |

