# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-14T02:05:23+00:00
- roots: 1
- total_candidate_rows: 716
- total_settled_markets: 1
- locked_total_entries: 0
- locked_total_pnl_cents: 0
- conclusion: Native forward roots contain a small positive existing-grid candidate, but locked RV600 candidates still take zero entries. Treat the positive row as diagnostic only until it clears sample, concentration, and matched-v28 gates.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260514T014324Z` | 716 | 1 | 2026-05-14T01:45:40.962012+00:00 | 2026-05-14T01:58:27.185367+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `blend_95_5_max_3_entries_base_70_420_ev0`
- accounting_mode: all_entries
- gate_count: 4
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 8.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 2.6666666666666665
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 8.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;avg_entry_below_10c;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY132200-00` | 2026-05-14T01:53:00.241367+00:00 | 419.8 | yes | 96.00 | 0.48 | 3.00 | yes | 0.51 | 3.00 | False |
| `KXBTC15M-26MAY132200-00` | 2026-05-14T01:53:01.288960+00:00 | 418.7 | yes | 96.00 | 0.49 | 3.00 | yes | 0.53 | 3.00 | True |
| `KXBTC15M-26MAY132200-00` | 2026-05-14T01:53:03.342214+00:00 | 416.7 | yes | 97.00 | 0.55 | 2.00 | yes | 0.58 | 2.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_base_70_420_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 5.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 1.6666666666666667
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 5.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;avg_entry_below_10c;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY132200-00` | 2026-05-14T01:53:03.342214+00:00 | 416.7 | yes | 97.00 | 0.00 | 2.00 | yes | 0.58 | 2.00 | False |
| `KXBTC15M-26MAY132200-00` | 2026-05-14T01:53:09.726721+00:00 | 410.3 | yes | 97.00 | 0.85 | 2.00 | yes | 1.51 | 2.00 | True |
| `KXBTC15M-26MAY132200-00` | 2026-05-14T01:53:35.070249+00:00 | 384.9 | yes | 98.00 | 0.01 | 1.00 | yes | 0.56 | 1.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_max_3_entries_mid_120_420_ev12`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 0
- distinct_markets: 0
- selected_pnl_cents: 0
- matched_v28_delta_cents: 0
- avg_pnl_per_entry_cents: 0.0
- positive_root_rate: 0.0
- positive_market_rate: 0.0
- max_single_market_pnl_share: 0.0
- last_window_pnl_cents: 0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|

