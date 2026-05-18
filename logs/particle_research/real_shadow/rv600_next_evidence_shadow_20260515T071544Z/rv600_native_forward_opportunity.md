# RV600 Native Forward Opportunity Diagnostic

- generated_utc: 2026-05-15T07:47:52+00:00
- roots: 1
- total_candidate_rows: 743
- total_settled_markets: 2
- locked_total_entries: 2
- locked_total_pnl_cents: 50.0
- conclusion: Native forward roots have entries; use the full completion audit before considering the goal complete.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_next_evidence_shadow_20260515T071544Z` | 743 | 2 | 2026-05-15T07:16:01.467306+00:00 | 2026-05-15T07:31:00.303316+00:00 |

## Candidates

### Best Existing-Grid Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 189.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 63.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 189.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150330-30` | 2026-05-15T07:20:00.291409+00:00 | 599.7 | yes | 35.00 | 1.03 | 63.00 | yes | 1.13 | 63.00 | False |
| `KXBTC15M-26MAY150330-30` | 2026-05-15T07:20:01.289898+00:00 | 598.7 | yes | 35.00 | 1.02 | 63.00 | yes | 1.12 | 63.00 | True |
| `KXBTC15M-26MAY150330-30` | 2026-05-15T07:20:10.504284+00:00 | 589.5 | yes | 35.00 | 0.75 | 63.00 | yes | 1.04 | 63.00 | True |

### Best RV600-Primary Candidate

- variant: `rv600_primary_max_3_entries_broad_70_600_ev0`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 3
- distinct_markets: 1
- selected_pnl_cents: 189.0
- matched_v28_delta_cents: 0.0
- avg_pnl_per_entry_cents: 63.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 189.0
- early_gt_420s_entries: 3
- locked_70_420s_entries: 0
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150330-30` | 2026-05-15T07:20:00.291409+00:00 | 599.7 | yes | 35.00 | 1.03 | 63.00 | yes | 1.13 | 63.00 | False |
| `KXBTC15M-26MAY150330-30` | 2026-05-15T07:20:01.289898+00:00 | 598.7 | yes | 35.00 | 1.02 | 63.00 | yes | 1.12 | 63.00 | True |
| `KXBTC15M-26MAY150330-30` | 2026-05-15T07:20:10.504284+00:00 | 589.5 | yes | 35.00 | 0.75 | 63.00 | yes | 1.04 | 63.00 | True |

### Best Locked Candidate

- variant: `rv600_primary_side_flip_only_broad_70_600_ev4`
- accounting_mode: all_entries
- gate_count: 3
- accepted_entries: 2
- distinct_markets: 1
- selected_pnl_cents: 50.0
- matched_v28_delta_cents: -7.0
- avg_pnl_per_entry_cents: 25.0
- positive_root_rate: 1.0
- positive_market_rate: 1.0
- max_single_market_pnl_share: 1.0
- last_window_pnl_cents: 50.0
- early_gt_420s_entries: 1
- locked_70_420s_entries: 1
- late_lt_70s_entries: 0
- rejection_reason: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct

| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY150330-30` | 2026-05-15T07:20:29.925889+00:00 | 570.1 | yes | 44.00 | 4.88 | 54.00 | yes | 3.18 | 54.00 | False |
| `KXBTC15M-26MAY150330-30` | 2026-05-15T07:23:57.064536+00:00 | 362.9 | no | 4.00 | 4.29 | -4.00 | yes | -0.50 | 3.00 | True |

