# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-14T04:22:31+00:00
- roots: 1
- total_candidate_rows: 767
- total_settled_markets: 2
- locked_total_entries: 0
- locked_total_pnl_cents: 0
- conclusion: Native forward roots contain a small positive existing-grid candidate, but locked RV600 candidates still take zero entries. Treat the positive row as diagnostic only until it clears sample, concentration, and matched-v28 gates.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260514T035926Z` | 767 | 2 | 2026-05-14T03:59:30.801550+00:00 | 2026-05-14T04:13:58.617455+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 104.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 34.666666666666664
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 104.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY140015-15` | 2026-05-14T04:05:00.381890+00:00 | 599.6 | yes | 62.00 | 4.25 | 36.00 | yes | 2.32 | 36.00 | False |
| `KXBTC15M-26MAY140015-15` | 2026-05-14T04:05:01.399700+00:00 | 598.6 | yes | 63.00 | 3.28 | 35.00 | yes | 1.32 | 35.00 | True |
| `KXBTC15M-26MAY140015-15` | 2026-05-14T04:05:02.438089+00:00 | 597.6 | yes | 65.00 | 1.29 | 33.00 | yes | -0.67 | 33.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 104.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 34.666666666666664
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 104.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY140015-15` | 2026-05-14T04:05:00.381890+00:00 | 599.6 | yes | 62.00 | 4.25 | 36.00 | yes | 2.32 | 36.00 | False |
| `KXBTC15M-26MAY140015-15` | 2026-05-14T04:05:01.399700+00:00 | 598.6 | yes | 63.00 | 3.28 | 35.00 | yes | 1.32 | 35.00 | True |
| `KXBTC15M-26MAY140015-15` | 2026-05-14T04:05:02.438089+00:00 | 597.6 | yes | 65.00 | 1.29 | 33.00 | yes | -0.67 | 33.00 | True |

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

