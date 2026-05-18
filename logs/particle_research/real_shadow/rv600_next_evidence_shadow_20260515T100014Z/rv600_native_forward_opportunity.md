# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-15T10:31:56+00:00
- roots: 1
- total_candidate_rows: 763
- total_settled_markets: 2
- locked_total_entries: 1
- locked_total_pnl_cents: 37.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260515T100014Z` | 763 | 2 | 2026-05-15T10:00:32.078230+00:00 | 2026-05-15T10:15:30.319998+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `blend_95_5_max_3_entries_broad_70_600_ev2`
- accounting_mode: all_entries
- gate_count: 4
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 146.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 48.666666666666664
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 146.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150615-15` | 2026-05-15T10:05:00.027426+00:00 | 600.0 | yes | 54.00 | 2.01 | 44.00 | yes | 2.05 | 44.00 | False |
| `KXBTC15M-26MAY150615-15` | 2026-05-15T10:05:02.050940+00:00 | 597.9 | yes | 49.00 | 2.12 | 49.00 | yes | 2.16 | 49.00 | True |
| `KXBTC15M-26MAY150615-15` | 2026-05-15T10:05:04.084579+00:00 | 595.9 | yes | 45.00 | 2.81 | 53.00 | yes | 2.85 | 53.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 138.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 46.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 138.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150615-15` | 2026-05-15T10:05:00.027426+00:00 | 600.0 | yes | 54.00 | 1.22 | 44.00 | yes | 2.05 | 44.00 | False |
| `KXBTC15M-26MAY150615-15` | 2026-05-15T10:05:01.039164+00:00 | 599.0 | yes | 53.00 | 0.13 | 45.00 | yes | 0.82 | 45.00 | True |
| `KXBTC15M-26MAY150615-15` | 2026-05-15T10:05:02.050940+00:00 | 597.9 | yes | 49.00 | 1.36 | 49.00 | yes | 2.16 | 49.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_side_flip_only_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 1
- distinct_markets: 1
- selected_pnl_cents: 37.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 37.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 37.0
- early_gt_420s_entries: 1
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150615-15` | 2026-05-15T10:06:01.978901+00:00 | 538.0 | yes | 61.00 | 4.26 | 37.00 | yes | 4.72 | 37.00 | False |

