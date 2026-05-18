# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-15T03:16:18+00:00
- roots: 1
- total_candidate_rows: 764
- total_settled_markets: 2
- locked_total_entries: 2
- locked_total_pnl_cents: 20.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260515T024708Z` | 764 | 2 | 2026-05-15T02:47:43.442996+00:00 | 2026-05-15T03:02:40.276187+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 102.0
- matched_v28_delta_cents: 213.0
- avg_pnl_per_entry_cents: 34.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 102.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY142300-00` | 2026-05-15T02:50:04.022324+00:00 | 596.0 | yes | 57.00 | 0.09 | 41.00 | no | -0.98 | -44.00 | False |
| `KXBTC15M-26MAY142300-00` | 2026-05-15T02:50:21.386607+00:00 | 578.6 | yes | 67.00 | 1.56 | 31.00 | no | -1.36 | -34.00 | True |
| `KXBTC15M-26MAY142300-00` | 2026-05-15T02:50:22.422347+00:00 | 577.6 | yes | 68.00 | 0.03 | 30.00 | no | 0.18 | -33.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 102.0
- matched_v28_delta_cents: 213.0
- avg_pnl_per_entry_cents: 34.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 102.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY142300-00` | 2026-05-15T02:50:04.022324+00:00 | 596.0 | yes | 57.00 | 0.09 | 41.00 | no | -0.98 | -44.00 | False |
| `KXBTC15M-26MAY142300-00` | 2026-05-15T02:50:21.386607+00:00 | 578.6 | yes | 67.00 | 1.56 | 31.00 | no | -1.36 | -34.00 | True |
| `KXBTC15M-26MAY142300-00` | 2026-05-15T02:50:22.422347+00:00 | 577.6 | yes | 68.00 | 0.03 | 30.00 | no | 0.18 | -33.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_side_flip_only_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 2
- distinct_markets: 1
- selected_pnl_cents: 20.0
- matched_v28_delta_cents: -15.0
- avg_pnl_per_entry_cents: 10.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 20.0
- early_gt_420s_entries: 2
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY142300-00` | 2026-05-15T02:51:27.786484+00:00 | 512.2 | yes | 70.00 | 6.33 | 28.00 | yes | 5.63 | 28.00 | False |
| `KXBTC15M-26MAY142300-00` | 2026-05-15T02:51:37.111441+00:00 | 502.9 | no | 8.00 | 4.36 | -8.00 | yes | 0.98 | 7.00 | True |

