# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-14T05:25:59+00:00
- roots: 1
- total_candidate_rows: 823
- total_settled_markets: 2
- locked_total_entries: 26
- locked_total_pnl_cents: 786.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260514T045722Z` | 823 | 2 | 2026-05-14T04:57:25.085131+00:00 | 2026-05-14T05:12:24.299413+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `blend_95_5_max_3_entries_late_70_300_ev10`
- accounting_mode: all_entries
- gate_count: 4
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 253.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 84.33333333333333
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 253.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY140115-15` | 2026-05-14T05:10:17.252367+00:00 | 282.7 | no | 17.00 | 11.04 | 82.00 | no | 11.10 | 82.00 | False |
| `KXBTC15M-26MAY140115-15` | 2026-05-14T05:10:46.238525+00:00 | 253.8 | no | 13.00 | 11.88 | 86.00 | no | 11.97 | 86.00 | True |
| `KXBTC15M-26MAY140115-15` | 2026-05-14T05:10:48.331390+00:00 | 251.7 | no | 14.00 | 10.78 | 85.00 | no | 10.87 | 85.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_mid_180_420_ev10`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 243.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 81.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 243.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY140115-15` | 2026-05-14T05:10:46.238525+00:00 | 253.8 | no | 13.00 | 10.21 | 86.00 | no | 11.97 | 86.00 | False |
| `KXBTC15M-26MAY140115-15` | 2026-05-14T05:11:19.149058+00:00 | 220.9 | no | 20.00 | 11.08 | 78.00 | no | 12.54 | 78.00 | True |
| `KXBTC15M-26MAY140115-15` | 2026-05-14T05:11:20.149725+00:00 | 219.9 | no | 19.00 | 10.27 | 79.00 | no | 11.82 | 79.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_max_2_entries_mid_120_420_ev12`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 4
- distinct_markets: 2
- selected_pnl_cents: 150.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 37.5
- positive_root_rate: 1.0
- positive_market_rate: 0.5
- max_single_market_pnl_share: 1.0666666666666667
- last_window_pnl_cents: 150.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 4
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY140100-00` | 2026-05-14T04:57:25.085131+00:00 | 154.9 | no | 5.00 | 21.77 | -5.00 | no | 1.19 | -5.00 | False |
| `KXBTC15M-26MAY140100-00` | 2026-05-14T04:57:26.270029+00:00 | 153.7 | no | 5.00 | 21.69 | -5.00 | no | 1.12 | -5.00 | True |
| `KXBTC15M-26MAY140115-15` | 2026-05-14T05:12:21.256151+00:00 | 158.7 | no | 18.00 | 15.31 | 80.00 | no | 16.54 | 80.00 | False |
| `KXBTC15M-26MAY140115-15` | 2026-05-14T05:12:22.271836+00:00 | 157.7 | no | 18.00 | 12.73 | 80.00 | no | 14.04 | 80.00 | True |

