# RV600 Prequential Selection Diagnostic

- generated_utc: 2026-05-13T15:17:37+00:00
- selector_policy: best_all_entries
- min_train_roots: 3
- gap_roots: 0
- min_decision_ts_utc: 2026-05-13T05:37:07+00:00
- roots: 10
- split_count: 7
- skipped_split_count: 0
- locked_gate_selection_count: 0
- diagnostic_fallback_selection_count: 7
- test_total_entries: 18
- test_total_distinct_markets: 6
- test_selected_pnl_cents: -106.0
- test_matched_v28_control_pnl_cents: -106.0
- test_matched_v28_delta_cents: 0.0
- test_avg_pnl_per_entry_cents: -5.888888888888889
- positive_test_split_rate: 0.42857142857142855
- max_single_test_root_pnl_share: 0.0
- selected_variant_counts: {"blend_80_20_max_3_entries_broad_70_600_ev2": 4, "blend_95_5_max_3_entries_broad_70_600_ev12": 1, "blend_95_5_max_3_entries_broad_70_600_ev20": 1, "blend_95_5_max_3_entries_broad_70_600_ev4": 1}
- preliminary_prequential_gate_pass: False
- rejection_reason: diagnostic_fallback_used;fewer_than_25_test_entries;nonpositive_test_pnl;avg_test_entry_below_10c;positive_test_splits_below_60pct
- conclusion: Prequential scoring needed diagnostic fallback selections, so the positive or negative aggregate cannot promote an RV600 strategy.

## Method Choice

Anchored prequential selection: select a variant/accounting mode using only prior native roots, then score that frozen selection on the next root. Locked-candidate selections preserve the RV600 anti-overfitting gates; diagnostic fallbacks are reported but are never promotable.

External options checked for the modeling blocker:

- Deflated Sharpe / multiple-testing adjustment: useful for large return series, but current RV600 has too few native roots for a stable Sharpe-style correction.
- CSCV / probability of backtest overfitting: strong for many trials across a return matrix, but it would reuse scarce roots combinatorially instead of mimicking the live sequence.
- Purged or embargoed time-series CV: useful when labels overlap; this probe exposes `gap_roots` as a simple embargo, but keeps the default next-root test because roots are already settled market blocks.
- Anchored walk-forward / prequential selection: best fit here because it tests exactly the action the research loop would take next: select from prior roots only, then evaluate the next incoming market block.
- Synthetic/bootstrap replay: rejected for this completion gate because it would not be incoming-market shadow evidence.

## Roots

| root | rows | markets | first | last |
|---|---:|---:|---|---|
| `rv600_forward_native_shadow_offline_v28_20260513T115640Z` | 29 | 1 | 2026-05-13T11:56:41.964180+00:00 | 2026-05-13T11:57:36.390523+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1220Z` | 458 | 2 | 2026-05-13T12:20:59.301441+00:00 | 2026-05-13T12:31:48.010938+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1235Z` | 322 | 1 | 2026-05-13T12:36:13.151124+00:00 | 2026-05-13T12:44:00.963555+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1259Z` | 780 | 1 | 2026-05-13T13:00:35.725860+00:00 | 2026-05-13T13:14:59.444507+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1333Z` | 613 | 1 | 2026-05-13T13:33:13.790175+00:00 | 2026-05-13T13:44:39.815097+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1333Z_1400` | 340 | 1 | 2026-05-13T13:45:27.961864+00:00 | 2026-05-13T13:51:13.238917+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1407Z` | 419 | 1 | 2026-05-13T14:07:16.490058+00:00 | 2026-05-13T14:14:31.703283+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1407Z_1430` | 582 | 1 | 2026-05-13T14:15:19.876897+00:00 | 2026-05-13T14:25:15.195195+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1439Z` | 305 | 1 | 2026-05-13T14:39:16.086062+00:00 | 2026-05-13T14:44:40.564724+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1439Z_1500` | 679 | 1 | 2026-05-13T14:45:39.475423+00:00 | 2026-05-13T14:57:14.954938+00:00 |

## Splits

| split | train_roots | test_root | basis | locked_gate | variant | accounting | train_pnl | test_entries | test_pnl | test_v28 | test_delta | test_rejection |
|---:|---:|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| 0 | 3 | `rv600_forward_native_shadow_offline_v28_20260513T1259Z` | best_all_entries_diagnostic | False | `blend_95_5_max_3_entries_broad_70_600_ev4` | all_entries | 124.00 | 3 | -82.00 | -82.00 | 0.00 | fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive |
| 1 | 4 | `rv600_forward_native_shadow_offline_v28_20260513T1333Z` | best_all_entries_diagnostic | False | `blend_95_5_max_3_entries_broad_70_600_ev12` | all_entries | 102.00 | 3 | 76.00 | 76.00 | 0.00 | fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| 2 | 5 | `rv600_forward_native_shadow_offline_v28_20260513T1333Z_1400` | best_all_entries_diagnostic | False | `blend_80_20_max_3_entries_broad_70_600_ev2` | all_entries | 180.00 | 3 | 37.00 | 37.00 | 0.00 | fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| 3 | 6 | `rv600_forward_native_shadow_offline_v28_20260513T1407Z` | best_all_entries_diagnostic | False | `blend_80_20_max_3_entries_broad_70_600_ev2` | all_entries | 217.00 | 3 | 71.00 | 71.00 | 0.00 | fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| 4 | 7 | `rv600_forward_native_shadow_offline_v28_20260513T1407Z_1430` | best_all_entries_diagnostic | False | `blend_80_20_max_3_entries_broad_70_600_ev2` | all_entries | 288.00 | 3 | -151.00 | -151.00 | 0.00 | fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive |
| 5 | 8 | `rv600_forward_native_shadow_offline_v28_20260513T1439Z` | best_all_entries_diagnostic | False | `blend_80_20_max_3_entries_broad_70_600_ev2` | all_entries | 137.00 | 3 | -57.00 | -57.00 | 0.00 | fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive |
| 6 | 9 | `rv600_forward_native_shadow_offline_v28_20260513T1439Z_1500` | best_all_entries_diagnostic | False | `blend_95_5_max_3_entries_broad_70_600_ev20` | all_entries | 102.00 | 0 | 0.00 | 0.00 | 0.00 | fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive |
