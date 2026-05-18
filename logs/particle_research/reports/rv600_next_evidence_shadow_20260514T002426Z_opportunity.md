# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-14T00:54:09+00:00
- roots: 1
- total_candidate_rows: 763
- total_settled_markets: 2
- locked_total_entries: 5
- locked_total_pnl_cents: -145.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260514T002426Z` | 763 | 2 | 2026-05-14T00:24:29.279114+00:00 | 2026-05-14T00:39:27.916703+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `blend_95_5_max_3_entries_broad_70_600_ev2`
- accounting_mode: all_entries
- gate_count: 4
- accepted_entries: 6
- distinct_markets: 2
- selected_pnl_cents: 164.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 27.333333333333332
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 0.8719512195121951
- last_window_pnl_cents: 164.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY132030-30` | 2026-05-14T00:25:12.405193+00:00 | 287.6 | no | 50.00 | 3.53 | 48.00 | no | 3.57 | 48.00 | False |
| `KXBTC15M-26MAY132030-30` | 2026-05-14T00:25:13.402319+00:00 | 286.6 | no | 50.00 | 3.53 | 48.00 | no | 3.58 | 48.00 | True |
| `KXBTC15M-26MAY132030-30` | 2026-05-14T00:25:16.431747+00:00 | 283.6 | no | 51.00 | 2.21 | 47.00 | no | 2.26 | 47.00 | True |
| `KXBTC15M-26MAY132045-45` | 2026-05-14T00:35:00.978261+00:00 | 599.0 | yes | 93.00 | 2.25 | 6.00 | yes | 2.36 | 6.00 | False |
| `KXBTC15M-26MAY132045-45` | 2026-05-14T00:35:01.975967+00:00 | 598.0 | yes | 92.00 | 3.24 | 7.00 | yes | 3.35 | 7.00 | True |
| `KXBTC15M-26MAY132045-45` | 2026-05-14T00:35:03.005863+00:00 | 597.0 | yes | 91.00 | 3.94 | 8.00 | yes | 4.05 | 8.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_late_70_300_ev2`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 149.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 49.666666666666664
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 149.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 3
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY132030-30` | 2026-05-14T00:25:12.405193+00:00 | 287.6 | no | 50.00 | 2.65 | 48.00 | no | 3.57 | 48.00 | False |
| `KXBTC15M-26MAY132030-30` | 2026-05-14T00:25:13.402319+00:00 | 286.6 | no | 50.00 | 2.66 | 48.00 | no | 3.58 | 48.00 | True |
| `KXBTC15M-26MAY132030-30` | 2026-05-14T00:25:24.826177+00:00 | 275.2 | no | 45.00 | 2.71 | 53.00 | no | 4.18 | 53.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_max_3_entries_mid_120_420_ev12`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 1
- distinct_markets: 1
- selected_pnl_cents: -29.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: -29.0
- positive_root_rate: 0.0
- positive_market_rate: 0.0
- max_single_market_pnl_share: 0.0
- last_window_pnl_cents: -29.0
- early_gt_420s_entries: 0
- locked_70_420s_entries: 1
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY132030-30` | 2026-05-14T00:24:29.279114+00:00 | 330.7 | yes | 29.00 | 13.81 | -29.00 | yes | 1.13 | -29.00 | False |

