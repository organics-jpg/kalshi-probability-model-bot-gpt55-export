# RV600 Variation Test Report

- generated_utc: 2026-05-13T18:49:36+00:00
- phase: grid
- promotion_allowed: False
- root_count: 25
- variant_count: 3948
- best_by_total_pnl: blend_80_20_max_3_entries_broad_70_600_ev20
- best_locked_candidate: 
- locked_candidates: none
- conclusion: grid found best total PnL row blend_80_20_max_3_entries_broad_70_600_ev20/all_entries at 209.0c, but no candidate cleared the locked simplification gates. Keep RV600 research-only.

## Top Summary Rows

| variant | accounting | gates | entries | markets | pnl_c | v28_delta_c | avg_entry_c | avg_market_c | +roots | +markets | max_market_share | last20_c | added_avg_c | locked? | reject |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| blend_80_20_max_3_entries_broad_70_600_ev20 | all_entries | 4 | 15 | 5 | 209.0 | 0.0 | 13.93 | 41.80 | 2/25 | 0.40 | 1.20 | 0.0 | 14.00 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_80_20_max_3_entries_broad_70_600_ev20 | position_capped | 4 | 15 | 5 | 209.0 | 0.0 | 13.93 | 41.80 | 2/25 | 0.40 | 1.20 | 0.0 | 14.00 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_80_20_risk_cap_200c_broad_70_600_ev20 | all_entries | 4 | 15 | 5 | 209.0 | 0.0 | 13.93 | 41.80 | 2/25 | 0.40 | 1.20 | 0.0 | 14.00 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_80_20_risk_cap_200c_broad_70_600_ev20 | position_capped | 4 | 15 | 5 | 209.0 | 0.0 | 13.93 | 41.80 | 2/25 | 0.40 | 1.20 | 0.0 | 14.00 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_90_10_max_3_entries_broad_70_600_ev20 | all_entries | 4 | 15 | 5 | 195.0 | 0.0 | 13.00 | 39.00 | 2/25 | 0.40 | 1.25 | 0.0 | 12.90 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_90_10_max_3_entries_broad_70_600_ev20 | position_capped | 4 | 15 | 5 | 195.0 | 0.0 | 13.00 | 39.00 | 2/25 | 0.40 | 1.25 | 0.0 | 12.90 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_90_10_risk_cap_200c_broad_70_600_ev20 | all_entries | 4 | 15 | 5 | 195.0 | 0.0 | 13.00 | 39.00 | 2/25 | 0.40 | 1.25 | 0.0 | 12.90 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_90_10_risk_cap_200c_broad_70_600_ev20 | position_capped | 4 | 15 | 5 | 195.0 | 0.0 | 13.00 | 39.00 | 2/25 | 0.40 | 1.25 | 0.0 | 12.90 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_90_10_same_side_ev_step_3c_late_70_180_ev20 | all_entries | 4 | 8 | 4 | 193.0 | 0.0 | 24.12 | 48.25 | 1/25 | 0.25 | 1.33 | 0.0 | 37.50 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_90_10_same_side_ev_step_3c_late_70_180_ev20 | position_capped | 4 | 8 | 4 | 193.0 | 0.0 | 24.12 | 48.25 | 1/25 | 0.25 | 1.33 | 0.0 | 37.50 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_95_5_same_side_ev_step_3c_late_70_180_ev20 | all_entries | 4 | 9 | 5 | 191.0 | 0.0 | 21.22 | 38.20 | 1/25 | 0.20 | 1.34 | 0.0 | 37.50 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_95_5_same_side_ev_step_3c_late_70_180_ev20 | position_capped | 4 | 9 | 5 | 191.0 | 0.0 | 21.22 | 38.20 | 1/25 | 0.20 | 1.34 | 0.0 | 37.50 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_95_5_max_3_entries_broad_70_600_ev20 | all_entries | 4 | 18 | 6 | 189.0 | 0.0 | 10.50 | 31.50 | 2/25 | 0.33 | 1.29 | 0.0 | 10.58 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_95_5_max_3_entries_broad_70_600_ev20 | position_capped | 4 | 18 | 6 | 189.0 | 0.0 | 10.50 | 31.50 | 2/25 | 0.33 | 1.29 | 0.0 | 10.58 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_95_5_risk_cap_200c_broad_70_600_ev20 | all_entries | 4 | 18 | 6 | 189.0 | 0.0 | 10.50 | 31.50 | 2/25 | 0.33 | 1.29 | 0.0 | 10.58 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_95_5_risk_cap_200c_broad_70_600_ev20 | position_capped | 4 | 18 | 6 | 189.0 | 0.0 | 10.50 | 31.50 | 2/25 | 0.33 | 1.29 | 0.0 | 10.58 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_95_5_same_side_ev_step_5c_late_70_180_ev15 | all_entries | 4 | 8 | 5 | 184.0 | 0.0 | 23.00 | 36.80 | 1/25 | 0.20 | 1.28 | 0.0 | 52.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_95_5_same_side_ev_step_5c_late_70_180_ev15 | position_capped | 4 | 8 | 5 | 184.0 | 0.0 | 23.00 | 36.80 | 1/25 | 0.20 | 1.28 | 0.0 | 52.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_90_10_same_side_ev_step_5c_late_70_180_ev15 | all_entries | 4 | 8 | 5 | 184.0 | 0.0 | 23.00 | 36.80 | 1/25 | 0.20 | 1.28 | 0.0 | 52.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_90_10_same_side_ev_step_5c_late_70_180_ev15 | position_capped | 4 | 8 | 5 | 184.0 | 0.0 | 23.00 | 36.80 | 1/25 | 0.20 | 1.28 | 0.0 | 52.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| rv600_primary_max_3_entries_late_70_180_ev20 | all_entries | 3 | 9 | 3 | 174.0 | 0.0 | 19.33 | 58.00 | 1/25 | 0.33 | 1.51 | 0.0 | 20.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| rv600_primary_max_3_entries_late_70_180_ev20 | position_capped | 3 | 9 | 3 | 174.0 | 0.0 | 19.33 | 58.00 | 1/25 | 0.33 | 1.51 | 0.0 | 20.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| rv600_softveto6_max_3_entries_late_70_180_ev20 | all_entries | 4 | 9 | 3 | 174.0 | 0.0 | 19.33 | 58.00 | 1/25 | 0.33 | 1.51 | 0.0 | 20.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| rv600_softveto6_max_3_entries_late_70_180_ev20 | position_capped | 4 | 9 | 3 | 174.0 | 0.0 | 19.33 | 58.00 | 1/25 | 0.33 | 1.51 | 0.0 | 20.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| rv600_softveto10_max_3_entries_late_70_180_ev20 | all_entries | 4 | 9 | 3 | 174.0 | 0.0 | 19.33 | 58.00 | 1/25 | 0.33 | 1.51 | 0.0 | 20.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| rv600_softveto10_max_3_entries_late_70_180_ev20 | position_capped | 4 | 9 | 3 | 174.0 | 0.0 | 19.33 | 58.00 | 1/25 | 0.33 | 1.51 | 0.0 | 20.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| rv600_primary_risk_cap_100c_late_70_180_ev20 | all_entries | 3 | 9 | 3 | 174.0 | 0.0 | 19.33 | 58.00 | 1/25 | 0.33 | 1.51 | 0.0 | 20.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| rv600_primary_risk_cap_100c_late_70_180_ev20 | position_capped | 3 | 9 | 3 | 174.0 | 0.0 | 19.33 | 58.00 | 1/25 | 0.33 | 1.51 | 0.0 | 20.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| rv600_softveto6_risk_cap_100c_late_70_180_ev20 | all_entries | 4 | 9 | 3 | 174.0 | 0.0 | 19.33 | 58.00 | 1/25 | 0.33 | 1.51 | 0.0 | 20.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| rv600_softveto6_risk_cap_100c_late_70_180_ev20 | position_capped | 4 | 9 | 3 | 174.0 | 0.0 | 19.33 | 58.00 | 1/25 | 0.33 | 1.51 | 0.0 | 20.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| rv600_softveto10_risk_cap_100c_late_70_180_ev20 | all_entries | 4 | 9 | 3 | 174.0 | 0.0 | 19.33 | 58.00 | 1/25 | 0.33 | 1.51 | 0.0 | 20.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| rv600_softveto10_risk_cap_100c_late_70_180_ev20 | position_capped | 4 | 9 | 3 | 174.0 | 0.0 | 19.33 | 58.00 | 1/25 | 0.33 | 1.51 | 0.0 | 20.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| rv600_primary_risk_cap_200c_late_70_180_ev20 | all_entries | 3 | 9 | 3 | 174.0 | 0.0 | 19.33 | 58.00 | 1/25 | 0.33 | 1.51 | 0.0 | 20.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| rv600_primary_risk_cap_200c_late_70_180_ev20 | position_capped | 3 | 9 | 3 | 174.0 | 0.0 | 19.33 | 58.00 | 1/25 | 0.33 | 1.51 | 0.0 | 20.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| rv600_softveto6_risk_cap_200c_late_70_180_ev20 | all_entries | 4 | 9 | 3 | 174.0 | 0.0 | 19.33 | 58.00 | 1/25 | 0.33 | 1.51 | 0.0 | 20.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| rv600_softveto6_risk_cap_200c_late_70_180_ev20 | position_capped | 4 | 9 | 3 | 174.0 | 0.0 | 19.33 | 58.00 | 1/25 | 0.33 | 1.51 | 0.0 | 20.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| rv600_softveto10_risk_cap_200c_late_70_180_ev20 | all_entries | 4 | 9 | 3 | 174.0 | 0.0 | 19.33 | 58.00 | 1/25 | 0.33 | 1.51 | 0.0 | 20.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| rv600_softveto10_risk_cap_200c_late_70_180_ev20 | position_capped | 4 | 9 | 3 | 174.0 | 0.0 | 19.33 | 58.00 | 1/25 | 0.33 | 1.51 | 0.0 | 20.33 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_90_10_same_side_ev_step_3c_broad_70_600_ev20 | all_entries | 4 | 12 | 5 | 174.0 | 0.0 | 14.50 | 34.80 | 2/25 | 0.40 | 1.47 | 0.0 | 15.43 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| blend_90_10_same_side_ev_step_3c_broad_70_600_ev20 | position_capped | 4 | 12 | 5 | 174.0 | 0.0 | 14.50 | 34.80 | 2/25 | 0.40 | 1.47 | 0.0 | 15.43 | False | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |

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
