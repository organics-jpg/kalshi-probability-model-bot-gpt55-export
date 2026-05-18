# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-15T09:02:31+00:00
- roots: 1
- total_candidate_rows: 761
- total_settled_markets: 2
- locked_total_entries: 16
- locked_total_pnl_cents: -135.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260515T083925Z` | 761 | 2 | 2026-05-15T08:39:43.880562+00:00 | 2026-05-15T08:54:42.271089+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_late_70_300_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 11.0
- matched_v28_delta_cents: 25.0
- avg_pnl_per_entry_cents: 3.6666666666666665
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 11.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;avg_entry_below_10c;single_market_share_above_25pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150445-45` | 2026-05-15T08:40:00.347973+00:00 | 299.7 | yes | 95.00 | 2.80 | 4.00 | no | 0.41 | -5.00 | False |
| `KXBTC15M-26MAY150445-45` | 2026-05-15T08:40:01.347882+00:00 | 298.7 | yes | 95.00 | 3.07 | 4.00 | no | -0.40 | -5.00 | True |
| `KXBTC15M-26MAY150445-45` | 2026-05-15T08:40:02.353426+00:00 | 297.6 | yes | 96.00 | 2.09 | 3.00 | no | 0.53 | -4.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_late_70_300_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 11.0
- matched_v28_delta_cents: 25.0
- avg_pnl_per_entry_cents: 3.6666666666666665
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 11.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;avg_entry_below_10c;single_market_share_above_25pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150445-45` | 2026-05-15T08:40:00.347973+00:00 | 299.7 | yes | 95.00 | 2.80 | 4.00 | no | 0.41 | -5.00 | False |
| `KXBTC15M-26MAY150445-45` | 2026-05-15T08:40:01.347882+00:00 | 298.7 | yes | 95.00 | 3.07 | 4.00 | no | -0.40 | -5.00 | True |
| `KXBTC15M-26MAY150445-45` | 2026-05-15T08:40:02.353426+00:00 | 297.6 | yes | 96.00 | 2.09 | 3.00 | no | 0.53 | -4.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_max_2_entries_mid_120_420_ev12`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 2
- distinct_markets: 1
- selected_pnl_cents: -14.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: -7.0
- positive_root_rate: 0.0
- positive_market_rate: 0.0
- max_single_market_pnl_share: 0.0
- last_window_pnl_cents: -14.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 2
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150445-45` | 2026-05-15T08:39:43.880562+00:00 | 316.1 | no | 7.00 | 18.07 | -7.00 | no | -0.93 | -7.00 | False |
| `KXBTC15M-26MAY150445-45` | 2026-05-15T08:39:44.897913+00:00 | 315.1 | no | 7.00 | 18.04 | -7.00 | no | -0.96 | -7.00 | True |

