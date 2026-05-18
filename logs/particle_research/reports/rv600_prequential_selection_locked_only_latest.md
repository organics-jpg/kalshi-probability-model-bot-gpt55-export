# RV600 Prequential Selection Diagnostic

- generated_utc: 2026-05-13T18:39:57+00:00
- selector_policy: locked_only
- min_train_roots: 3
- gap_roots: 0
- min_decision_ts_utc: 2026-05-13T05:37:07+00:00
- roots: 23
- split_count: 0
- skipped_split_count: 20
- locked_gate_selection_count: 0
- diagnostic_fallback_selection_count: 0
- test_total_entries: 0
- test_total_distinct_markets: 0
- test_selected_pnl_cents: 0
- test_matched_v28_control_pnl_cents: 0
- test_matched_v28_delta_cents: 0
- test_avg_pnl_per_entry_cents: 0.0
- positive_test_split_rate: 0.0
- max_single_test_root_pnl_share: 0.0
- selected_variant_counts: {}
- preliminary_prequential_gate_pass: False
- rejection_reason: no_prequential_splits;fewer_than_25_test_entries;nonpositive_test_pnl
- conclusion: No prequential split could be scored from the current native RV600 roots.

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
| `rv600_forward_native_shadow_offline_v28_20260513T1522Z_1530` | 343 | 1 | 2026-05-13T15:22:39.228676+00:00 | 2026-05-13T15:29:40.688147+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1541Z_1545` | 165 | 1 | 2026-05-13T15:42:06.567353+00:00 | 2026-05-13T15:44:53.546050+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1556Z_1600` | 28 | 1 | 2026-05-13T15:56:23.359377+00:00 | 2026-05-13T15:57:13.123698+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1610Z_1615` | 208 | 1 | 2026-05-13T16:10:54.280464+00:00 | 2026-05-13T16:14:25.632471+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1626Z_1630` | 113 | 1 | 2026-05-13T16:26:29.555901+00:00 | 2026-05-13T16:28:24.568883+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1640Z_1645` | 171 | 1 | 2026-05-13T16:40:21.250250+00:00 | 2026-05-13T16:43:22.495351+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1656Z_1700` | 163 | 1 | 2026-05-13T16:56:24.920877+00:00 | 2026-05-13T16:59:18.897364+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1712Z_1715` | 16 | 1 | 2026-05-13T17:12:56.824291+00:00 | 2026-05-13T17:13:15.192788+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1722Z_1730` | 329 | 1 | 2026-05-13T17:22:17.719251+00:00 | 2026-05-13T17:28:04.449608+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1737Z_1745` | 380 | 1 | 2026-05-13T17:37:15.088282+00:00 | 2026-05-13T17:43:48.495117+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1752Z_1800` | 324 | 1 | 2026-05-13T17:53:06.283929+00:00 | 2026-05-13T17:58:41.580940+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1808Z_1815` | 339 | 1 | 2026-05-13T18:08:19.076300+00:00 | 2026-05-13T18:14:30.337025+00:00 |
| `rv600_forward_native_shadow_offline_v28_20260513T1819Z_1830` | 478 | 1 | 2026-05-13T18:19:43.058818+00:00 | 2026-05-13T18:28:35.997834+00:00 |

## Splits

| split | train_roots | test_root | basis | locked_gate | variant | accounting | train_pnl | test_entries | test_pnl | test_v28 | test_delta | test_rejection |
|---:|---:|---|---|---|---|---|---:|---:|---:|---:|---:|---|
