# RV600 Variation Test Report

- generated_utc: 2026-05-13T15:06:27+00:00
- phase: grid
- promotion_allowed: False
- root_count: 10
- variant_count: 3948
- best_by_total_pnl: blend_80_20_max_3_entries_broad_70_600_ev2
- best_locked_candidate: 
- locked_candidates: none
- conclusion: grid found best total PnL row blend_80_20_max_3_entries_broad_70_600_ev2/all_entries at 299.0c, but no candidate cleared the locked simplification gates. Keep RV600 research-only.

## Top Summary Rows

| variant | accounting | gates | entries | markets | pnl_c | v28_delta_c | avg_entry_c | avg_market_c | +roots | +markets | max_market_share | last20_c | added_avg_c | locked? | reject |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| blend_80_20_max_3_entries_broad_70_600_ev2 | all_entries | 4 | 27 | 9 | 299.0 | 0.0 | 11.07 | 33.22 | 6/10 | 0.67 | 0.73 | 219.0 | 11.06 | False | single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_80_20_max_3_entries_broad_70_600_ev2 | position_capped | 4 | 27 | 9 | 299.0 | 0.0 | 11.07 | 33.22 | 6/10 | 0.67 | 0.73 | 219.0 | 11.06 | False | single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_80_20_risk_cap_200c_broad_70_600_ev2 | all_entries | 4 | 25 | 9 | 222.0 | 0.0 | 8.88 | 24.67 | 6/10 | 0.67 | 0.99 | 219.0 | 7.62 | False | avg_entry_below_10c;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_80_20_risk_cap_200c_broad_70_600_ev2 | position_capped | 4 | 25 | 9 | 222.0 | 0.0 | 8.88 | 24.67 | 6/10 | 0.67 | 0.99 | 219.0 | 7.62 | False | avg_entry_below_10c;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_80_20_max_2_entries_broad_70_600_ev2 | all_entries | 4 | 18 | 9 | 203.0 | 0.0 | 11.28 | 22.56 | 6/10 | 0.67 | 0.72 | 146.0 | 11.44 | False | fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_80_20_max_2_entries_broad_70_600_ev2 | position_capped | 4 | 18 | 9 | 203.0 | 0.0 | 11.28 | 22.56 | 6/10 | 0.67 | 0.72 | 146.0 | 11.44 | False | fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_95_5_max_3_entries_broad_70_600_ev0 | all_entries | 4 | 27 | 9 | 150.0 | 0.0 | 5.56 | 16.67 | 6/10 | 0.67 | 0.86 | 74.0 | 2.72 | False | avg_entry_below_10c;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_95_5_max_3_entries_broad_70_600_ev0 | position_capped | 4 | 27 | 9 | 150.0 | 0.0 | 5.56 | 16.67 | 6/10 | 0.67 | 0.86 | 74.0 | 2.72 | False | avg_entry_below_10c;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_90_10_max_3_entries_broad_70_600_ev0 | all_entries | 4 | 28 | 10 | 149.0 | 0.0 | 5.32 | 14.90 | 6/10 | 0.60 | 0.87 | 74.0 | 2.72 | False | avg_entry_below_10c;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_90_10_max_3_entries_broad_70_600_ev0 | position_capped | 4 | 28 | 10 | 149.0 | 0.0 | 5.32 | 14.90 | 6/10 | 0.60 | 0.87 | 74.0 | 2.72 | False | avg_entry_below_10c;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_95_5_max_3_entries_broad_70_600_ev4 | all_entries | 4 | 27 | 9 | 123.0 | 0.0 | 4.56 | 13.67 | 5/10 | 0.56 | 1.76 | 216.0 | 3.94 | False | avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_95_5_max_3_entries_broad_70_600_ev4 | position_capped | 4 | 27 | 9 | 123.0 | 0.0 | 4.56 | 13.67 | 5/10 | 0.56 | 1.76 | 216.0 | 3.94 | False | avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_90_10_max_3_entries_broad_70_600_ev2 | all_entries | 4 | 27 | 9 | 117.0 | 0.0 | 4.33 | 13.00 | 5/10 | 0.56 | 1.87 | 219.0 | 4.33 | False | avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_90_10_max_3_entries_broad_70_600_ev2 | position_capped | 4 | 27 | 9 | 117.0 | 0.0 | 4.33 | 13.00 | 5/10 | 0.56 | 1.87 | 219.0 | 4.33 | False | avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_95_5_max_3_entries_broad_70_600_ev2 | all_entries | 4 | 27 | 9 | 113.0 | 0.0 | 4.19 | 12.56 | 5/10 | 0.56 | 1.94 | 219.0 | 4.11 | False | avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_95_5_max_3_entries_broad_70_600_ev2 | position_capped | 4 | 27 | 9 | 113.0 | 0.0 | 4.19 | 12.56 | 5/10 | 0.56 | 1.94 | 219.0 | 4.11 | False | avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_95_5_risk_cap_200c_broad_70_600_ev4 | all_entries | 4 | 25 | 9 | 106.0 | 0.0 | 4.24 | 11.78 | 5/10 | 0.56 | 2.04 | 216.0 | 3.38 | False | avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_95_5_risk_cap_200c_broad_70_600_ev4 | position_capped | 4 | 25 | 9 | 106.0 | 0.0 | 4.24 | 11.78 | 5/10 | 0.56 | 2.04 | 216.0 | 3.38 | False | avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_95_5_max_3_entries_broad_70_600_ev20 | all_entries | 4 | 3 | 1 | 102.0 | 0.0 | 34.00 | 102.00 | 1/10 | 1.00 | 1.00 | 0.0 | 34.00 | False | fewer_than_25_entries;positive_roots_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_95_5_max_3_entries_broad_70_600_ev20 | position_capped | 4 | 3 | 1 | 102.0 | 0.0 | 34.00 | 102.00 | 1/10 | 1.00 | 1.00 | 0.0 | 34.00 | False | fewer_than_25_entries;positive_roots_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_95_5_risk_cap_200c_broad_70_600_ev20 | all_entries | 4 | 3 | 1 | 102.0 | 0.0 | 34.00 | 102.00 | 1/10 | 1.00 | 1.00 | 0.0 | 34.00 | False | fewer_than_25_entries;positive_roots_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_95_5_risk_cap_200c_broad_70_600_ev20 | position_capped | 4 | 3 | 1 | 102.0 | 0.0 | 34.00 | 102.00 | 1/10 | 1.00 | 1.00 | 0.0 | 34.00 | False | fewer_than_25_entries;positive_roots_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_95_5_single_market_broad_70_600_ev0 | all_entries | 4 | 9 | 9 | 101.0 | 0.0 | 11.22 | 11.22 | 6/10 | 0.67 | 0.72 | 73.0 | 0.00 | False | fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_95_5_single_market_broad_70_600_ev0 | one_per_side_per_market | 4 | 9 | 9 | 101.0 | 0.0 | 11.22 | 11.22 | 6/10 | 0.67 | 0.72 | 73.0 | 0.00 | False | fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_95_5_single_market_broad_70_600_ev0 | position_capped | 4 | 9 | 9 | 101.0 | 0.0 | 11.22 | 11.22 | 6/10 | 0.67 | 0.72 | 73.0 | 0.00 | False | fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_90_10_risk_cap_200c_broad_70_600_ev2 | all_entries | 4 | 25 | 9 | 101.0 | 0.0 | 4.04 | 11.22 | 5/10 | 0.56 | 2.17 | 219.0 | 3.88 | False | avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_90_10_risk_cap_200c_broad_70_600_ev2 | position_capped | 4 | 25 | 9 | 101.0 | 0.0 | 4.04 | 11.22 | 5/10 | 0.56 | 2.17 | 219.0 | 3.88 | False | avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_90_10_max_3_entries_broad_70_600_ev20 | all_entries | 4 | 3 | 1 | 101.0 | 0.0 | 33.67 | 101.00 | 1/10 | 1.00 | 1.00 | 0.0 | 33.50 | False | fewer_than_25_entries;positive_roots_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_90_10_max_3_entries_broad_70_600_ev20 | position_capped | 4 | 3 | 1 | 101.0 | 0.0 | 33.67 | 101.00 | 1/10 | 1.00 | 1.00 | 0.0 | 33.50 | False | fewer_than_25_entries;positive_roots_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_80_20_max_3_entries_broad_70_600_ev20 | all_entries | 4 | 3 | 1 | 101.0 | 0.0 | 33.67 | 101.00 | 1/10 | 1.00 | 1.00 | 0.0 | 33.50 | False | fewer_than_25_entries;positive_roots_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_80_20_max_3_entries_broad_70_600_ev20 | position_capped | 4 | 3 | 1 | 101.0 | 0.0 | 33.67 | 101.00 | 1/10 | 1.00 | 1.00 | 0.0 | 33.50 | False | fewer_than_25_entries;positive_roots_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_90_10_risk_cap_200c_broad_70_600_ev20 | all_entries | 4 | 3 | 1 | 101.0 | 0.0 | 33.67 | 101.00 | 1/10 | 1.00 | 1.00 | 0.0 | 33.50 | False | fewer_than_25_entries;positive_roots_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_90_10_risk_cap_200c_broad_70_600_ev20 | position_capped | 4 | 3 | 1 | 101.0 | 0.0 | 33.67 | 101.00 | 1/10 | 1.00 | 1.00 | 0.0 | 33.50 | False | fewer_than_25_entries;positive_roots_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_80_20_risk_cap_200c_broad_70_600_ev20 | all_entries | 4 | 3 | 1 | 101.0 | 0.0 | 33.67 | 101.00 | 1/10 | 1.00 | 1.00 | 0.0 | 33.50 | False | fewer_than_25_entries;positive_roots_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_80_20_risk_cap_200c_broad_70_600_ev20 | position_capped | 4 | 3 | 1 | 101.0 | 0.0 | 33.67 | 101.00 | 1/10 | 1.00 | 1.00 | 0.0 | 33.50 | False | fewer_than_25_entries;positive_roots_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_90_10_single_market_broad_70_600_ev0 | all_entries | 4 | 10 | 10 | 100.0 | 0.0 | 10.00 | 10.00 | 6/10 | 0.60 | 0.73 | 73.0 | 0.00 | False | fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_90_10_single_market_broad_70_600_ev0 | one_per_side_per_market | 4 | 10 | 10 | 100.0 | 0.0 | 10.00 | 10.00 | 6/10 | 0.60 | 0.73 | 73.0 | 0.00 | False | fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_90_10_single_market_broad_70_600_ev0 | position_capped | 4 | 10 | 10 | 100.0 | 0.0 | 10.00 | 10.00 | 6/10 | 0.60 | 0.73 | 73.0 | 0.00 | False | fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_80_20_single_market_broad_70_600_ev2 | all_entries | 4 | 9 | 9 | 100.0 | 0.0 | 11.11 | 11.11 | 6/10 | 0.67 | 0.73 | 73.0 | 0.00 | False | fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| blend_80_20_single_market_broad_70_600_ev2 | one_per_side_per_market | 4 | 9 | 9 | 100.0 | 0.0 | 11.11 | 11.11 | 6/10 | 0.67 | 0.73 | 73.0 | 0.00 | False | fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |

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

## Notes

- This is discovery/shadow research only; it does not place orders or change live v28 logic.
- Repeated-entry variants are reported under all_entries, one_per_side_per_market, and position_capped accounting.
- Locked-candidate eligibility is retrospective only and still requires forward-shadow validation before any live pilot.
