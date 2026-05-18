# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-14T03:04:35+00:00
- roots: 1
- total_candidate_rows: 753
- total_settled_markets: 2
- locked_total_entries: 10
- locked_total_pnl_cents: -80.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260514T024042Z` | 753 | 2 | 2026-05-14T02:40:45.035319+00:00 | 2026-05-14T02:55:43.998325+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `blend_95_5_max_3_entries_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 4
- accepted_entries: 4
- distinct_markets: 2
- selected_pnl_cents: 7.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 1.75
- positive_root_rate: 1.0
- positive_market_rate: 0.5
- max_single_market_pnl_share: 2.142857142857143
- last_window_pnl_cents: 7.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 1
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;avg_entry_below_10c;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY132245-45` | 2026-05-14T02:40:54.251321+00:00 | 245.7 | yes | 8.00 | 4.13 | -8.00 | yes | 3.86 | -8.00 | False |
| `KXBTC15M-26MAY132300-00` | 2026-05-14T02:50:00.111620+00:00 | 599.9 | no | 94.00 | 4.39 | 5.00 | no | 4.40 | 5.00 | False |
| `KXBTC15M-26MAY132300-00` | 2026-05-14T02:50:15.498012+00:00 | 584.5 | no | 94.00 | 4.27 | 5.00 | no | 4.31 | 5.00 | True |
| `KXBTC15M-26MAY132300-00` | 2026-05-14T02:50:16.507462+00:00 | 583.5 | no | 94.00 | 4.27 | 5.00 | no | 4.32 | 5.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_2_entries_late_70_180_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 2
- distinct_markets: 1
- selected_pnl_cents: 2.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 1.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 2.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 2
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;avg_entry_below_10c;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY132245-45` | 2026-05-14T02:42:01.808617+00:00 | 178.2 | no | 98.00 | 0.58 | 1.00 | no | 0.49 | 1.00 | False |
| `KXBTC15M-26MAY132245-45` | 2026-05-14T02:42:02.834511+00:00 | 177.2 | no | 98.00 | 0.43 | 1.00 | no | 0.28 | 1.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_max_3_entries_mid_120_420_ev12`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 2
- distinct_markets: 1
- selected_pnl_cents: -16.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: -8.0
- positive_root_rate: 0.0
- positive_market_rate: 0.0
- max_single_market_pnl_share: 0.0
- last_window_pnl_cents: -16.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 2
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY132245-45` | 2026-05-14T02:40:45.035319+00:00 | 255.0 | yes | 8.00 | 25.78 | -8.00 | yes | 1.87 | -8.00 | False |
| `KXBTC15M-26MAY132245-45` | 2026-05-14T02:40:46.037930+00:00 | 254.0 | yes | 8.00 | 26.26 | -8.00 | yes | 2.61 | -8.00 | True |

