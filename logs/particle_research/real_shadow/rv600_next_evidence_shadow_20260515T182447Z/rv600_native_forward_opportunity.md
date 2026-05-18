# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-15T18:49:30+00:00
- roots: 1
- total_candidate_rows: 744
- total_settled_markets: 2
- locked_total_entries: 2
- locked_total_pnl_cents: 31.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260515T182447Z` | 744 | 2 | 2026-05-15T18:25:27.636622+00:00 | 2026-05-15T18:40:27.003202+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `blend_95_5_max_3_entries_base_70_420_ev2`
- accounting_mode: all_entries
- gate_count: 4
- accepted_entries: 4
- distinct_markets: 2
- selected_pnl_cents: 168.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 42.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 0.9821428571428571
- last_window_pnl_cents: 168.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 4
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY151430-30` | 2026-05-15T18:25:27.636622+00:00 | 272.4 | no | 96.00 | 2.33 | 3.00 | no | 2.72 | 3.00 | False |
| `KXBTC15M-26MAY151445-45` | 2026-05-15T18:38:18.271902+00:00 | 401.7 | no | 43.00 | 2.66 | 55.00 | no | 2.63 | 55.00 | False |
| `KXBTC15M-26MAY151445-45` | 2026-05-15T18:38:30.539808+00:00 | 389.5 | no | 43.00 | 2.63 | 55.00 | no | 2.59 | 55.00 | True |
| `KXBTC15M-26MAY151445-45` | 2026-05-15T18:38:31.548552+00:00 | 388.5 | no | 43.00 | 2.63 | 55.00 | no | 2.59 | 55.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_base_70_420_ev2`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 5
- distinct_markets: 2
- selected_pnl_cents: 161.0
- matched_v28_delta_cents: -12.0
- avg_pnl_per_entry_cents: 32.2
- positive_root_rate: 1.0
- positive_market_rate: 0.5
- max_single_market_pnl_share: 1.0434782608695652
- last_window_pnl_cents: 161.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 5
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY151430-30` | 2026-05-15T18:25:27.636622+00:00 | 272.4 | yes | 4.00 | 3.92 | -4.00 | no | 2.72 | 3.00 | False |
| `KXBTC15M-26MAY151430-30` | 2026-05-15T18:25:28.724514+00:00 | 271.3 | yes | 3.00 | 4.39 | -3.00 | no | 1.77 | 2.00 | True |
| `KXBTC15M-26MAY151445-45` | 2026-05-15T18:38:15.227436+00:00 | 404.8 | no | 42.00 | 2.48 | 56.00 | no | 1.87 | 56.00 | False |
| `KXBTC15M-26MAY151445-45` | 2026-05-15T18:38:16.231521+00:00 | 403.8 | no | 42.00 | 2.47 | 56.00 | no | 1.87 | 56.00 | True |
| `KXBTC15M-26MAY151445-45` | 2026-05-15T18:38:17.225465+00:00 | 402.8 | no | 42.00 | 2.47 | 56.00 | no | 1.86 | 56.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_side_flip_only_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 2
- distinct_markets: 2
- selected_pnl_cents: 31.0
- matched_v28_delta_cents: -5.0
- avg_pnl_per_entry_cents: 15.5
- positive_root_rate: 1.0
- positive_market_rate: 0.5
- max_single_market_pnl_share: 1.096774193548387
- last_window_pnl_cents: 31.0
- early_gt_420s_entries: 1
- locked_70_420s_entries: 1
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY151430-30` | 2026-05-15T18:25:28.724514+00:00 | 271.3 | yes | 3.00 | 4.39 | -3.00 | no | 1.77 | 2.00 | False |
| `KXBTC15M-26MAY151445-45` | 2026-05-15T18:35:00.962585+00:00 | 599.0 | no | 64.00 | 8.60 | 34.00 | no | 6.52 | 34.00 | False |

