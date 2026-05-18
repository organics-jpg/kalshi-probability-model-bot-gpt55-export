# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-15T03:46:28+00:00
- roots: 1
- total_candidate_rows: 853
- total_settled_markets: 2
- locked_total_entries: 4
- locked_total_pnl_cents: 180.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260515T032104Z` | 853 | 2 | 2026-05-15T03:21:24.799351+00:00 | 2026-05-15T03:36:23.170224+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev2`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 6
- distinct_markets: 2
- selected_pnl_cents: 218.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 36.333333333333336
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 0.9220183486238532
- last_window_pnl_cents: 218.0
- early_gt_420s_entries: 6
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY142330-30` | 2026-05-15T03:21:24.799351+00:00 | 515.2 | yes | 31.00 | 10.29 | 67.00 | yes | 3.86 | 67.00 | False |
| `KXBTC15M-26MAY142330-30` | 2026-05-15T03:21:25.822272+00:00 | 514.2 | yes | 31.00 | 10.29 | 67.00 | yes | 3.84 | 67.00 | True |
| `KXBTC15M-26MAY142330-30` | 2026-05-15T03:21:26.837395+00:00 | 513.2 | yes | 31.00 | 10.28 | 67.00 | yes | 3.83 | 67.00 | True |
| `KXBTC15M-26MAY142345-45` | 2026-05-15T03:35:00.405070+00:00 | 599.6 | no | 94.00 | 2.26 | 5.00 | no | 2.70 | 5.00 | False |
| `KXBTC15M-26MAY142345-45` | 2026-05-15T03:35:04.502753+00:00 | 595.5 | no | 93.00 | 2.54 | 6.00 | no | 3.07 | 6.00 | True |
| `KXBTC15M-26MAY142345-45` | 2026-05-15T03:35:05.588156+00:00 | 594.4 | no | 93.00 | 2.52 | 6.00 | no | 3.08 | 6.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev2`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 6
- distinct_markets: 2
- selected_pnl_cents: 218.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 36.333333333333336
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 0.9220183486238532
- last_window_pnl_cents: 218.0
- early_gt_420s_entries: 6
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY142330-30` | 2026-05-15T03:21:24.799351+00:00 | 515.2 | yes | 31.00 | 10.29 | 67.00 | yes | 3.86 | 67.00 | False |
| `KXBTC15M-26MAY142330-30` | 2026-05-15T03:21:25.822272+00:00 | 514.2 | yes | 31.00 | 10.29 | 67.00 | yes | 3.84 | 67.00 | True |
| `KXBTC15M-26MAY142330-30` | 2026-05-15T03:21:26.837395+00:00 | 513.2 | yes | 31.00 | 10.28 | 67.00 | yes | 3.83 | 67.00 | True |
| `KXBTC15M-26MAY142345-45` | 2026-05-15T03:35:00.405070+00:00 | 599.6 | no | 94.00 | 2.26 | 5.00 | no | 2.70 | 5.00 | False |
| `KXBTC15M-26MAY142345-45` | 2026-05-15T03:35:04.502753+00:00 | 595.5 | no | 93.00 | 2.54 | 6.00 | no | 3.07 | 6.00 | True |
| `KXBTC15M-26MAY142345-45` | 2026-05-15T03:35:05.588156+00:00 | 594.4 | no | 93.00 | 2.52 | 6.00 | no | 3.08 | 6.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_max_3_entries_base_70_420_ev12`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 1
- distinct_markets: 1
- selected_pnl_cents: 65.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 65.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 65.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 1
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY142330-30` | 2026-05-15T03:28:15.981765+00:00 | 104.0 | yes | 33.00 | 13.90 | 65.00 | yes | 15.07 | 65.00 | False |

