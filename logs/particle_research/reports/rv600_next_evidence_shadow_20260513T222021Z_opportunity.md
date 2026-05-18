# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-13T22:46:45+00:00
- roots: 1
- total_candidate_rows: 727
- total_settled_markets: 2
- locked_total_entries: 0
- locked_total_pnl_cents: 0
- conclusion: Native forward roots contain a small positive existing-grid candidate, but locked RV600 candidates still take zero entries. Treat the positive row as diagnostic only until it clears sample, concentration, and matched-v28 gates.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260513T222021Z` | 727 | 2 | 2026-05-13T22:20:23.059669+00:00 | 2026-05-13T22:35:22.170342+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `blend_95_5_max_3_entries_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 4
- accepted_entries: 6
- distinct_markets: 2
- selected_pnl_cents: 222.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 37.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 0.8783783783783784
- last_window_pnl_cents: 222.0
- early_gt_420s_entries: 6
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131830-30` | 2026-05-13T22:20:23.059669+00:00 | 576.9 | no | 90.00 | 1.26 | 9.00 | no | 2.43 | 9.00 | False |
| `KXBTC15M-26MAY131830-30` | 2026-05-13T22:20:24.062855+00:00 | 575.9 | no | 90.00 | 1.28 | 9.00 | no | 2.45 | 9.00 | True |
| `KXBTC15M-26MAY131830-30` | 2026-05-13T22:20:25.071718+00:00 | 574.9 | no | 90.00 | 1.30 | 9.00 | no | 2.47 | 9.00 | True |
| `KXBTC15M-26MAY131845-45` | 2026-05-13T22:35:00.915701+00:00 | 599.1 | yes | 33.00 | 1.45 | 65.00 | yes | 1.49 | 65.00 | False |
| `KXBTC15M-26MAY131845-45` | 2026-05-13T22:35:03.004325+00:00 | 597.0 | yes | 33.00 | 1.03 | 65.00 | yes | 1.07 | 65.00 | True |
| `KXBTC15M-26MAY131845-45` | 2026-05-13T22:35:04.008927+00:00 | 596.0 | yes | 33.00 | 0.56 | 65.00 | yes | 0.59 | 65.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_risk_cap_100c_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 6
- distinct_markets: 2
- selected_pnl_cents: 172.0
- matched_v28_delta_cents: -59.0
- avg_pnl_per_entry_cents: 28.666666666666668
- positive_root_rate: 1.0
- positive_market_rate: 0.5
- max_single_market_pnl_share: 1.186046511627907
- last_window_pnl_cents: 172.0
- early_gt_420s_entries: 6
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY131830-30` | 2026-05-13T22:20:23.059669+00:00 | 576.9 | yes | 11.00 | 18.96 | -11.00 | no | 2.43 | 9.00 | False |
| `KXBTC15M-26MAY131830-30` | 2026-05-13T22:20:24.062855+00:00 | 575.9 | yes | 10.00 | 19.95 | -10.00 | no | 2.45 | 9.00 | True |
| `KXBTC15M-26MAY131830-30` | 2026-05-13T22:20:25.071718+00:00 | 574.9 | yes | 11.00 | 18.93 | -11.00 | no | 2.47 | 9.00 | True |
| `KXBTC15M-26MAY131845-45` | 2026-05-13T22:35:00.915701+00:00 | 599.1 | yes | 33.00 | 0.71 | 65.00 | yes | 1.49 | 65.00 | False |
| `KXBTC15M-26MAY131845-45` | 2026-05-13T22:35:03.004325+00:00 | 597.0 | yes | 33.00 | 0.33 | 65.00 | yes | 1.07 | 65.00 | True |
| `KXBTC15M-26MAY131845-45` | 2026-05-13T22:35:14.109644+00:00 | 585.9 | yes | 24.00 | 0.44 | 74.00 | yes | -0.03 | 74.00 | True |

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

