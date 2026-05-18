# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-14T02:34:14+00:00
- roots: 1
- total_candidate_rows: 827
- total_settled_markets: 2
- locked_total_entries: 14
- locked_total_pnl_cents: 1144.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260514T021209Z` | 827 | 2 | 2026-05-14T02:12:12.208428+00:00 | 2026-05-14T02:27:10.711054+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_base_70_420_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 6
- distinct_markets: 2
- selected_pnl_cents: 287.0
- matched_v28_delta_cents: 30.0
- avg_pnl_per_entry_cents: 47.833333333333336
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 0.8501742160278746
- last_window_pnl_cents: 287.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 6
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY132215-15` | 2026-05-14T02:12:12.208428+00:00 | 167.8 | no | 13.00 | 26.42 | 86.00 | no | 9.97 | 86.00 | False |
| `KXBTC15M-26MAY132215-15` | 2026-05-14T02:12:13.217170+00:00 | 166.8 | no | 17.00 | 24.72 | 82.00 | no | 11.60 | 82.00 | True |
| `KXBTC15M-26MAY132215-15` | 2026-05-14T02:12:14.209877+00:00 | 165.8 | no | 22.00 | 14.66 | 76.00 | no | 7.80 | 76.00 | True |
| `KXBTC15M-26MAY132230-30` | 2026-05-14T02:24:09.597030+00:00 | 350.4 | yes | 85.00 | 0.74 | 14.00 | no | -0.52 | -16.00 | False |
| `KXBTC15M-26MAY132230-30` | 2026-05-14T02:24:10.616087+00:00 | 349.4 | yes | 84.00 | 3.09 | 15.00 | yes | 0.88 | 15.00 | True |
| `KXBTC15M-26MAY132230-30` | 2026-05-14T02:24:11.956923+00:00 | 348.0 | yes | 85.00 | 2.13 | 14.00 | yes | -0.07 | 14.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_base_70_420_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 6
- distinct_markets: 2
- selected_pnl_cents: 287.0
- matched_v28_delta_cents: 30.0
- avg_pnl_per_entry_cents: 47.833333333333336
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 0.8501742160278746
- last_window_pnl_cents: 287.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 6
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY132215-15` | 2026-05-14T02:12:12.208428+00:00 | 167.8 | no | 13.00 | 26.42 | 86.00 | no | 9.97 | 86.00 | False |
| `KXBTC15M-26MAY132215-15` | 2026-05-14T02:12:13.217170+00:00 | 166.8 | no | 17.00 | 24.72 | 82.00 | no | 11.60 | 82.00 | True |
| `KXBTC15M-26MAY132215-15` | 2026-05-14T02:12:14.209877+00:00 | 165.8 | no | 22.00 | 14.66 | 76.00 | no | 7.80 | 76.00 | True |
| `KXBTC15M-26MAY132230-30` | 2026-05-14T02:24:09.597030+00:00 | 350.4 | yes | 85.00 | 0.74 | 14.00 | no | -0.52 | -16.00 | False |
| `KXBTC15M-26MAY132230-30` | 2026-05-14T02:24:10.616087+00:00 | 349.4 | yes | 84.00 | 3.09 | 15.00 | yes | 0.88 | 15.00 | True |
| `KXBTC15M-26MAY132230-30` | 2026-05-14T02:24:11.956923+00:00 | 348.0 | yes | 85.00 | 2.13 | 14.00 | yes | -0.07 | 14.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_max_3_entries_mid_120_420_ev12`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 244.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 81.33333333333333
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 244.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY132215-15` | 2026-05-14T02:12:12.208428+00:00 | 167.8 | no | 13.00 | 26.42 | 86.00 | no | 9.97 | 86.00 | False |
| `KXBTC15M-26MAY132215-15` | 2026-05-14T02:12:13.217170+00:00 | 166.8 | no | 17.00 | 24.72 | 82.00 | no | 11.60 | 82.00 | True |
| `KXBTC15M-26MAY132215-15` | 2026-05-14T02:12:14.209877+00:00 | 165.8 | no | 22.00 | 14.66 | 76.00 | no | 7.80 | 76.00 | True |

