# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-15T11:17:10+00:00
- roots: 1
- total_candidate_rows: 665
- total_settled_markets: 2
- locked_total_entries: 2
- locked_total_pnl_cents: 14.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260515T105111Z` | 665 | 2 | 2026-05-15T10:51:26.825077+00:00 | 2026-05-15T11:06:26.076529+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 6
- distinct_markets: 2
- selected_pnl_cents: 36.0
- matched_v28_delta_cents: 84.0
- avg_pnl_per_entry_cents: 6.0
- positive_root_rate: 1.0
- positive_market_rate: 0.5
- max_single_market_pnl_share: 1.25
- last_window_pnl_cents: 36.0
- early_gt_420s_entries: 6
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;avg_entry_below_10c;positive_markets_below_60pct;single_market_share_above_25pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150700-00` | 2026-05-15T10:51:26.825077+00:00 | 513.2 | no | 3.00 | 6.91 | -3.00 | yes | 0.94 | 1.00 | False |
| `KXBTC15M-26MAY150700-00` | 2026-05-15T10:51:27.829724+00:00 | 512.2 | no | 3.00 | 6.67 | -3.00 | yes | 0.94 | 1.00 | True |
| `KXBTC15M-26MAY150700-00` | 2026-05-15T10:51:28.817554+00:00 | 511.2 | no | 3.00 | 5.94 | -3.00 | yes | 0.91 | 1.00 | True |
| `KXBTC15M-26MAY150715-15` | 2026-05-15T11:05:00.399916+00:00 | 599.6 | no | 84.00 | 0.27 | 15.00 | yes | 0.87 | -17.00 | False |
| `KXBTC15M-26MAY150715-15` | 2026-05-15T11:05:01.423969+00:00 | 598.6 | no | 84.00 | 0.27 | 15.00 | yes | 0.85 | -17.00 | True |
| `KXBTC15M-26MAY150715-15` | 2026-05-15T11:05:02.432906+00:00 | 597.6 | no | 84.00 | 0.29 | 15.00 | yes | 0.83 | -17.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 6
- distinct_markets: 2
- selected_pnl_cents: 36.0
- matched_v28_delta_cents: 84.0
- avg_pnl_per_entry_cents: 6.0
- positive_root_rate: 1.0
- positive_market_rate: 0.5
- max_single_market_pnl_share: 1.25
- last_window_pnl_cents: 36.0
- early_gt_420s_entries: 6
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;avg_entry_below_10c;positive_markets_below_60pct;single_market_share_above_25pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150700-00` | 2026-05-15T10:51:26.825077+00:00 | 513.2 | no | 3.00 | 6.91 | -3.00 | yes | 0.94 | 1.00 | False |
| `KXBTC15M-26MAY150700-00` | 2026-05-15T10:51:27.829724+00:00 | 512.2 | no | 3.00 | 6.67 | -3.00 | yes | 0.94 | 1.00 | True |
| `KXBTC15M-26MAY150700-00` | 2026-05-15T10:51:28.817554+00:00 | 511.2 | no | 3.00 | 5.94 | -3.00 | yes | 0.91 | 1.00 | True |
| `KXBTC15M-26MAY150715-15` | 2026-05-15T11:05:00.399916+00:00 | 599.6 | no | 84.00 | 0.27 | 15.00 | yes | 0.87 | -17.00 | False |
| `KXBTC15M-26MAY150715-15` | 2026-05-15T11:05:01.423969+00:00 | 598.6 | no | 84.00 | 0.27 | 15.00 | yes | 0.85 | -17.00 | True |
| `KXBTC15M-26MAY150715-15` | 2026-05-15T11:05:02.432906+00:00 | 597.6 | no | 84.00 | 0.29 | 15.00 | yes | 0.83 | -17.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_side_flip_only_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 2
- distinct_markets: 2
- selected_pnl_cents: 14.0
- matched_v28_delta_cents: -4.0
- avg_pnl_per_entry_cents: 7.0
- positive_root_rate: 1.0
- positive_market_rate: 0.5
- max_single_market_pnl_share: 1.2142857142857142
- last_window_pnl_cents: 14.0
- early_gt_420s_entries: 2
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;avg_entry_below_10c;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150700-00` | 2026-05-15T10:51:26.825077+00:00 | 513.2 | no | 3.00 | 6.91 | -3.00 | yes | 0.94 | 1.00 | False |
| `KXBTC15M-26MAY150715-15` | 2026-05-15T11:05:30.043935+00:00 | 570.0 | no | 81.00 | 4.53 | 17.00 | no | 1.28 | 17.00 | False |

