# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-14T06:02:25+00:00
- roots: 1
- total_candidate_rows: 731
- total_settled_markets: 2
- locked_total_entries: 2
- locked_total_pnl_cents: 4.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260514T053423Z` | 731 | 2 | 2026-05-14T05:34:25.111765+00:00 | 2026-05-14T05:49:23.885283+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev2`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 36.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 12.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 36.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY140145-45` | 2026-05-14T05:35:25.195001+00:00 | 574.8 | yes | 87.00 | 2.19 | 12.00 | yes | 0.58 | 12.00 | False |
| `KXBTC15M-26MAY140145-45` | 2026-05-14T05:35:26.209373+00:00 | 573.8 | yes | 87.00 | 2.26 | 12.00 | yes | 0.47 | 12.00 | True |
| `KXBTC15M-26MAY140145-45` | 2026-05-14T05:35:27.214440+00:00 | 572.8 | yes | 87.00 | 2.28 | 12.00 | yes | 0.49 | 12.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev2`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 36.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 12.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 36.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY140145-45` | 2026-05-14T05:35:25.195001+00:00 | 574.8 | yes | 87.00 | 2.19 | 12.00 | yes | 0.58 | 12.00 | False |
| `KXBTC15M-26MAY140145-45` | 2026-05-14T05:35:26.209373+00:00 | 573.8 | yes | 87.00 | 2.26 | 12.00 | yes | 0.47 | 12.00 | True |
| `KXBTC15M-26MAY140145-45` | 2026-05-14T05:35:27.214440+00:00 | 572.8 | yes | 87.00 | 2.28 | 12.00 | yes | 0.49 | 12.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_side_flip_only_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 2
- distinct_markets: 1
- selected_pnl_cents: 4.0
- matched_v28_delta_cents: -13.0
- avg_pnl_per_entry_cents: 2.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 4.0
- early_gt_420s_entries: 2
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;avg_entry_below_10c;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY140145-45` | 2026-05-14T05:35:38.806287+00:00 | 561.2 | yes | 87.00 | 4.94 | 12.00 | yes | 2.29 | 12.00 | False |
| `KXBTC15M-26MAY140145-45` | 2026-05-14T05:35:40.834929+00:00 | 559.2 | no | 8.00 | 7.06 | -8.00 | yes | 2.18 | 5.00 | True |

