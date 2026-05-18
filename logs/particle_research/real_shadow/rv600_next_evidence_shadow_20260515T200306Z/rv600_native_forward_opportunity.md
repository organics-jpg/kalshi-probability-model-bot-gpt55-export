# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-15T20:33:42+00:00
- roots: 1
- total_candidate_rows: 853
- total_settled_markets: 2
- locked_total_entries: 2
- locked_total_pnl_cents: 40.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260515T200306Z` | 853 | 2 | 2026-05-15T20:03:22.916288+00:00 | 2026-05-15T20:18:21.965567+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 204.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 68.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 204.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY151615-15` | 2026-05-15T20:05:00.230939+00:00 | 599.8 | no | 30.00 | 3.63 | 68.00 | no | 5.86 | 68.00 | False |
| `KXBTC15M-26MAY151615-15` | 2026-05-15T20:05:01.237700+00:00 | 598.8 | no | 30.00 | 3.47 | 68.00 | no | 5.67 | 68.00 | True |
| `KXBTC15M-26MAY151615-15` | 2026-05-15T20:05:02.251854+00:00 | 597.7 | no | 30.00 | 3.38 | 68.00 | no | 5.66 | 68.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 204.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 68.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 204.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY151615-15` | 2026-05-15T20:05:00.230939+00:00 | 599.8 | no | 30.00 | 3.63 | 68.00 | no | 5.86 | 68.00 | False |
| `KXBTC15M-26MAY151615-15` | 2026-05-15T20:05:01.237700+00:00 | 598.8 | no | 30.00 | 3.47 | 68.00 | no | 5.67 | 68.00 | True |
| `KXBTC15M-26MAY151615-15` | 2026-05-15T20:05:02.251854+00:00 | 597.7 | no | 30.00 | 3.38 | 68.00 | no | 5.66 | 68.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_side_flip_only_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 2
- distinct_markets: 1
- selected_pnl_cents: 40.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 20.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 40.0
- early_gt_420s_entries: 1
- locked_70_420s_entries: 1
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY151615-15` | 2026-05-15T20:05:06.319754+00:00 | 593.7 | no | 35.00 | 4.46 | 63.00 | no | 5.75 | 63.00 | False |
| `KXBTC15M-26MAY151615-15` | 2026-05-15T20:10:31.677057+00:00 | 268.3 | yes | 23.00 | 5.53 | -23.00 | yes | 3.98 | -23.00 | True |

