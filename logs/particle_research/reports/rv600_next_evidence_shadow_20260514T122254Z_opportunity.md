# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-14T12:51:18+00:00
- roots: 1
- total_candidate_rows: 794
- total_settled_markets: 2
- locked_total_entries: 2
- locked_total_pnl_cents: -59.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260514T122254Z` | 794 | 2 | 2026-05-14T12:23:17.942353+00:00 | 2026-05-14T12:38:16.958974+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `blend_90_10_max_3_entries_base_70_420_ev2`
- accounting_mode: all_entries
- gate_count: 4
- accepted_entries: 6
- distinct_markets: 2
- selected_pnl_cents: 186.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 31.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 0.9032258064516129
- last_window_pnl_cents: 186.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 6
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY140830-30` | 2026-05-14T12:23:45.677752+00:00 | 374.3 | yes | 42.00 | 2.65 | 56.00 | yes | 2.76 | 56.00 | False |
| `KXBTC15M-26MAY140830-30` | 2026-05-14T12:23:46.692539+00:00 | 373.3 | yes | 42.00 | 2.64 | 56.00 | yes | 2.75 | 56.00 | True |
| `KXBTC15M-26MAY140830-30` | 2026-05-14T12:23:47.703968+00:00 | 372.3 | yes | 42.00 | 2.64 | 56.00 | yes | 2.75 | 56.00 | True |
| `KXBTC15M-26MAY140845-45` | 2026-05-14T12:38:00.479472+00:00 | 419.5 | yes | 93.00 | 2.79 | 6.00 | yes | 3.70 | 6.00 | False |
| `KXBTC15M-26MAY140845-45` | 2026-05-14T12:38:03.595387+00:00 | 416.4 | yes | 93.00 | 2.55 | 6.00 | yes | 3.48 | 6.00 | True |
| `KXBTC15M-26MAY140845-45` | 2026-05-14T12:38:04.587616+00:00 | 415.4 | yes | 93.00 | 2.25 | 6.00 | yes | 3.21 | 6.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_side_flip_only_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 4
- distinct_markets: 2
- selected_pnl_cents: 5.0
- matched_v28_delta_cents: -9.0
- avg_pnl_per_entry_cents: 1.25
- positive_root_rate: 1.0
- positive_market_rate: 0.5
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 5.0
- early_gt_420s_entries: 2
- locked_70_420s_entries: 2
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;avg_entry_below_10c;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY140830-30` | 2026-05-14T12:23:17.942353+00:00 | 402.1 | no | 44.00 | 3.10 | -44.00 | no | -0.18 | -44.00 | False |
| `KXBTC15M-26MAY140830-30` | 2026-05-14T12:23:32.530210+00:00 | 387.5 | yes | 49.00 | 0.55 | 49.00 | yes | 0.86 | 49.00 | True |
| `KXBTC15M-26MAY140845-45` | 2026-05-14T12:35:06.718490+00:00 | 593.3 | yes | 94.00 | 1.28 | 5.00 | yes | 4.18 | 5.00 | False |
| `KXBTC15M-26MAY140845-45` | 2026-05-14T12:36:00.991859+00:00 | 539.0 | no | 5.00 | 0.39 | -5.00 | yes | 3.30 | 4.00 | True |

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

