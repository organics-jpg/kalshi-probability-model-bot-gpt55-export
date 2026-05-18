# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-13T21:47:22+00:00
- roots: 1
- total_candidate_rows: 823
- total_settled_markets: 2
- locked_total_entries: 5
- locked_total_pnl_cents: -65.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260513T211949Z` | 823 | 2 | 2026-05-13T21:19:51.564973+00:00 | 2026-05-13T21:34:50.672631+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_late_70_180_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 178.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 59.333333333333336
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 178.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131730-30` | 2026-05-13T21:27:01.047102+00:00 | 179.0 | no | 38.00 | 1.13 | 60.00 | no | 1.20 | 60.00 | False |
| `KXBTC15M-26MAY131730-30` | 2026-05-13T21:27:02.038308+00:00 | 178.0 | no | 38.00 | 1.11 | 60.00 | no | 1.17 | 60.00 | True |
| `KXBTC15M-26MAY131730-30` | 2026-05-13T21:27:03.047436+00:00 | 177.0 | no | 40.00 | 5.24 | 58.00 | no | 4.47 | 58.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_late_70_180_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 178.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 59.333333333333336
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 178.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131730-30` | 2026-05-13T21:27:01.047102+00:00 | 179.0 | no | 38.00 | 1.13 | 60.00 | no | 1.20 | 60.00 | False |
| `KXBTC15M-26MAY131730-30` | 2026-05-13T21:27:02.038308+00:00 | 178.0 | no | 38.00 | 1.11 | 60.00 | no | 1.17 | 60.00 | True |
| `KXBTC15M-26MAY131730-30` | 2026-05-13T21:27:03.047436+00:00 | 177.0 | no | 40.00 | 5.24 | 58.00 | no | 4.47 | 58.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_max_3_entries_mid_120_420_ev12`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 1
- distinct_markets: 1
- selected_pnl_cents: -13.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: -13.0
- positive_root_rate: 0.0
- positive_market_rate: 0.0
- max_single_market_pnl_share: 0.0
- last_window_pnl_cents: -13.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 1
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131730-30` | 2026-05-13T21:27:51.042293+00:00 | 129.0 | yes | 13.00 | 12.86 | -13.00 | yes | 16.31 | -13.00 | False |

