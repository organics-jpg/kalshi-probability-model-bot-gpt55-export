# RV600 Variation Test Report

- generated_utc: 2026-05-13T18:36:29+00:00
- phase: locked
- promotion_allowed: False
- root_count: 25
- variant_count: 5
- best_by_total_pnl: rv600_primary_max_3_entries_mid_120_420_ev12
- best_locked_candidate: 
- locked_candidates: none
- conclusion: locked found best total PnL row rv600_primary_max_3_entries_mid_120_420_ev12/one_per_side_per_market at -155.3c, but no candidate cleared the locked simplification gates. Keep RV600 research-only.

## Top Summary Rows

| variant | accounting | gates | entries | markets | pnl_c | v28_delta_c | avg_entry_c | avg_market_c | +roots | +markets | max_market_share | last20_c | added_avg_c | locked? | reject |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| rv600_primary_max_3_entries_mid_120_420_ev12 | one_per_side_per_market | 3 | 15 | 15 | -155.3 | -7.1 | -10.35 | -10.35 | 1/25 | 0.07 | 0.00 | -6.3 | -17.19 | False | fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive |
| rv600_primary_risk_cap_200c_mid_120_420_ev12 | one_per_side_per_market | 3 | 15 | 15 | -155.3 | -7.1 | -10.35 | -10.35 | 1/25 | 0.07 | 0.00 | -6.3 | -17.19 | False | fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive |
| rv600_primary_max_2_entries_mid_120_420_ev12 | one_per_side_per_market | 3 | 15 | 15 | -155.3 | -7.1 | -10.35 | -10.35 | 1/25 | 0.07 | 0.00 | -6.3 | -18.00 | False | fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive |
| rv600_primary_max_3_entries_base_70_420_ev12 | one_per_side_per_market | 3 | 16 | 16 | -169.3 | -7.1 | -10.58 | -10.58 | 1/25 | 0.06 | 0.00 | -6.3 | -10.60 | False | fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive |
| rv600_primary_risk_cap_200c_base_70_420_ev12 | one_per_side_per_market | 3 | 16 | 16 | -169.3 | -7.1 | -10.58 | -10.58 | 1/25 | 0.06 | 0.00 | -6.3 | -10.60 | False | fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive |
| rv600_primary_max_2_entries_mid_120_420_ev12 | all_entries | 3 | 26 | 15 | -353.3 | -7.1 | -13.59 | -23.55 | 1/25 | 0.07 | 0.00 | -6.3 | -18.00 | False | nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive |
| rv600_primary_max_2_entries_mid_120_420_ev12 | position_capped | 3 | 26 | 15 | -353.3 | -7.1 | -13.59 | -23.55 | 1/25 | 0.07 | 0.00 | -6.3 | -18.00 | False | nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive |
| rv600_primary_max_3_entries_base_70_420_ev12 | all_entries | 3 | 41 | 16 | -434.3 | -7.1 | -10.59 | -27.14 | 1/25 | 0.06 | 0.00 | -6.3 | -10.60 | False | nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive |
| rv600_primary_max_3_entries_base_70_420_ev12 | position_capped | 3 | 41 | 16 | -434.3 | -7.1 | -10.59 | -27.14 | 1/25 | 0.06 | 0.00 | -6.3 | -10.60 | False | nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive |
| rv600_primary_risk_cap_200c_base_70_420_ev12 | all_entries | 3 | 41 | 16 | -434.3 | -7.1 | -10.59 | -27.14 | 1/25 | 0.06 | 0.00 | -6.3 | -10.60 | False | nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive |
| rv600_primary_risk_cap_200c_base_70_420_ev12 | position_capped | 3 | 41 | 16 | -434.3 | -7.1 | -10.59 | -27.14 | 1/25 | 0.06 | 0.00 | -6.3 | -10.60 | False | nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive |
| rv600_primary_max_3_entries_mid_120_420_ev12 | all_entries | 3 | 36 | 15 | -516.3 | -7.1 | -14.34 | -34.42 | 1/25 | 0.07 | 0.00 | -6.3 | -17.19 | False | nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive |
| rv600_primary_max_3_entries_mid_120_420_ev12 | position_capped | 3 | 36 | 15 | -516.3 | -7.1 | -14.34 | -34.42 | 1/25 | 0.07 | 0.00 | -6.3 | -17.19 | False | nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive |
| rv600_primary_risk_cap_200c_mid_120_420_ev12 | all_entries | 3 | 36 | 15 | -516.3 | -7.1 | -14.34 | -34.42 | 1/25 | 0.07 | 0.00 | -6.3 | -17.19 | False | nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive |
| rv600_primary_risk_cap_200c_mid_120_420_ev12 | position_capped | 3 | 36 | 15 | -516.3 | -7.1 | -14.34 | -34.42 | 1/25 | 0.07 | 0.00 | -6.3 | -17.19 | False | nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive |

## Roots

- rv600_forward_native_shadow_offline_v28_20260513T115640Z
- rv600_forward_native_shadow_offline_v28_20260513T1220Z
- rv600_forward_native_shadow_offline_v28_20260513T1235Z
- rv600_forward_native_shadow_offline_v28_20260513T1259Z
- rv600_forward_native_shadow_offline_v28_20260513T1333Z
- rv600_forward_native_shadow_offline_v28_20260513T1333Z_1400
- rv600_forward_native_shadow_offline_v28_20260513T1407Z
- rv600_forward_native_shadow_offline_v28_20260513T1407Z_1430
- rv600_forward_native_shadow_offline_v28_20260513T1439Z
- rv600_forward_native_shadow_offline_v28_20260513T1439Z_1500
- rv600_forward_native_shadow_offline_v28_20260513T1522Z_1530
- rv600_forward_native_shadow_offline_v28_20260513T1541Z_1545
- rv600_forward_native_shadow_offline_v28_20260513T1556Z_1600
- rv600_forward_native_shadow_offline_v28_20260513T1610Z_1615
- rv600_forward_native_shadow_offline_v28_20260513T1626Z_1630
- rv600_forward_native_shadow_offline_v28_20260513T1640Z_1645
- rv600_forward_native_shadow_offline_v28_20260513T1656Z_1700
- rv600_forward_native_shadow_offline_v28_20260513T1712Z_1715
- rv600_forward_native_shadow_offline_v28_20260513T1722Z_1730
- rv600_forward_native_shadow_offline_v28_20260513T1737Z_1745
- rv600_forward_native_shadow_offline_v28_20260513T1752Z_1800
- rv600_forward_native_shadow_offline_v28_20260513T1808Z_1815
- rv600_forward_native_shadow_offline_v28_20260513T1819Z_1830
- rv600_forward_shadow_20260513T054445Z
- rv600_sidecar_spot_pairs_forward

## Notes

- This is discovery/shadow research only; it does not place orders or change live v28 logic.
- Repeated-entry variants are reported under all_entries, one_per_side_per_market, and position_capped accounting.
- Locked-candidate eligibility is retrospective only and still requires forward-shadow validation before any live pilot.
