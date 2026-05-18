# RV600 Variation Test Report

- generated_utc: 2026-05-13T05:36:14+00:00
- phase: grid
- promotion_allowed: False
- root_count: 10
- variant_count: 3948
- best_by_total_pnl: rv600_softveto6_max_3_entries_mid_180_420_ev2
- best_locked_candidate: rv600_primary_max_3_entries_mid_120_420_ev12
- locked_candidates: rv600_primary_max_3_entries_mid_120_420_ev12, rv600_primary_max_3_entries_base_70_420_ev12, rv600_primary_risk_cap_200c_mid_120_420_ev12, rv600_primary_risk_cap_200c_base_70_420_ev12, rv600_primary_max_2_entries_mid_120_420_ev12
- conclusion: grid found retrospective locked-candidate candidates, led by rv600_primary_max_3_entries_mid_120_420_ev12. Promotion is still blocked until fresh forward shadow reaches the predeclared sample gates.

## Top Summary Rows

| variant | accounting | gates | entries | markets | pnl_c | v28_delta_c | avg_entry_c | avg_market_c | +roots | +markets | max_market_share | last20_c | added_avg_c | locked? | reject |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| rv600_primary_max_3_entries_mid_120_420_ev12 | position_capped | 3 | 70 | 26 | 1317.0 | 288.0 | 18.81 | 50.65 | 8/10 | 0.62 | 0.20 | 113.0 | 16.55 | True |  |
| rv600_primary_max_3_entries_base_70_420_ev12 | position_capped | 3 | 73 | 26 | 1284.0 | 288.0 | 17.59 | 49.38 | 8/10 | 0.62 | 0.21 | 113.0 | 14.79 | True |  |
| rv600_primary_risk_cap_200c_mid_120_420_ev12 | position_capped | 3 | 70 | 26 | 1219.0 | 288.0 | 17.41 | 46.88 | 8/10 | 0.62 | 0.22 | 113.0 | 14.32 | True |  |
| rv600_primary_risk_cap_200c_base_70_420_ev12 | position_capped | 3 | 73 | 26 | 1186.0 | 288.0 | 16.25 | 45.62 | 8/10 | 0.62 | 0.23 | 113.0 | 12.70 | True |  |
| rv600_primary_max_2_entries_mid_120_420_ev12 | position_capped | 3 | 49 | 26 | 926.0 | 195.0 | 18.90 | 35.62 | 9/10 | 0.62 | 0.19 | 70.0 | 14.65 | True |  |
| rv600_primary_max_2_entries_base_70_420_ev12 | position_capped | 3 | 50 | 26 | 904.0 | 195.0 | 18.08 | 34.77 | 9/10 | 0.62 | 0.20 | 70.0 | 13.12 | True |  |
| rv600_primary_max_2_entries_mid_120_420_ev12 | one_per_side_per_market | 3 | 29 | 26 | 572.0 | 127.0 | 19.72 | 22.00 | 9/10 | 0.62 | 0.16 | 35.0 | 14.65 | True |  |
| rv600_primary_max_3_entries_mid_120_420_ev12 | one_per_side_per_market | 3 | 29 | 26 | 572.0 | 127.0 | 19.72 | 22.00 | 9/10 | 0.62 | 0.16 | 35.0 | 16.55 | True |  |
| rv600_primary_max_2_entries_base_70_420_ev12 | one_per_side_per_market | 3 | 30 | 26 | 550.0 | 127.0 | 18.33 | 21.15 | 9/10 | 0.62 | 0.16 | 35.0 | 13.12 | True |  |
| rv600_primary_max_3_entries_base_70_420_ev12 | one_per_side_per_market | 3 | 30 | 26 | 550.0 | 127.0 | 18.33 | 21.15 | 9/10 | 0.62 | 0.16 | 35.0 | 14.79 | True |  |
| rv600_primary_risk_cap_100c_mid_120_420_ev12 | one_per_side_per_market | 3 | 31 | 26 | 537.0 | 127.0 | 17.32 | 20.65 | 9/10 | 0.62 | 0.17 | 35.0 | 8.22 | True |  |
| rv600_primary_risk_cap_200c_mid_120_420_ev12 | one_per_side_per_market | 3 | 31 | 26 | 537.0 | 127.0 | 17.32 | 20.65 | 9/10 | 0.62 | 0.17 | 35.0 | 14.32 | True |  |
| rv600_primary_risk_cap_100c_base_70_420_ev12 | one_per_side_per_market | 3 | 32 | 26 | 515.0 | 127.0 | 16.09 | 19.81 | 9/10 | 0.62 | 0.17 | 35.0 | 6.15 | True |  |
| rv600_primary_risk_cap_200c_base_70_420_ev12 | one_per_side_per_market | 3 | 32 | 26 | 515.0 | 127.0 | 16.09 | 19.81 | 9/10 | 0.62 | 0.17 | 35.0 | 12.70 | True |  |
| rv600_primary_same_side_ev_step_3c_mid_120_420_ev12 | one_per_side_per_market | 3 | 33 | 26 | 455.0 | 127.0 | 13.79 | 17.50 | 9/10 | 0.62 | 0.16 | 35.0 | 4.72 | True |  |
| rv600_primary_same_side_ev_step_3c_base_70_420_ev12 | one_per_side_per_market | 3 | 34 | 26 | 433.0 | 127.0 | 12.74 | 16.65 | 9/10 | 0.62 | 0.15 | 35.0 | 2.38 | True |  |
| rv600_primary_same_side_refresh_60s_mid_120_420_ev12 | one_per_side_per_market | 3 | 35 | 26 | 390.0 | 127.0 | 11.14 | 15.00 | 8/10 | 0.62 | 0.19 | 35.0 | -1.13 | True |  |
| rv600_primary_same_side_ev_step_5c_mid_120_420_ev12 | one_per_side_per_market | 3 | 35 | 26 | 390.0 | 127.0 | 11.14 | 15.00 | 8/10 | 0.62 | 0.19 | 35.0 | -6.62 | True |  |
| rv600_primary_same_side_refresh_60s_base_70_420_ev12 | one_per_side_per_market | 3 | 36 | 26 | 368.0 | 127.0 | 10.22 | 14.15 | 8/10 | 0.62 | 0.17 | 35.0 | 1.48 | True |  |
| rv600_primary_same_side_ev_step_5c_base_70_420_ev12 | one_per_side_per_market | 3 | 36 | 26 | 368.0 | 127.0 | 10.22 | 14.15 | 8/10 | 0.62 | 0.17 | 35.0 | -4.88 | True |  |
| rv600_primary_side_flip_only_mid_120_420_ev12 | one_per_side_per_market | 3 | 36 | 26 | 363.0 | 127.0 | 10.08 | 13.96 | 8/10 | 0.62 | 0.20 | 35.0 | -22.60 | True |  |
| rv600_primary_side_flip_only_mid_120_420_ev12 | position_capped | 3 | 36 | 26 | 363.0 | 127.0 | 10.08 | 13.96 | 8/10 | 0.62 | 0.20 | 35.0 | -22.60 | True |  |
| rv600_primary_same_side_refresh_120s_mid_120_420_ev12 | one_per_side_per_market | 3 | 36 | 26 | 363.0 | 127.0 | 10.08 | 13.96 | 8/10 | 0.62 | 0.20 | 35.0 | -5.00 | True |  |
| rv600_primary_max_3_entries_mid_120_420_ev12 | all_entries | 3 | 70 | 26 | 1317.0 | 288.0 | 18.81 | 50.65 | 8/10 | 0.62 | 0.20 | 113.0 | 16.55 | False |  |
| rv600_softveto6_max_3_entries_mid_120_420_ev12 | all_entries | 4 | 70 | 26 | 1317.0 | 288.0 | 18.81 | 50.65 | 8/10 | 0.62 | 0.20 | 113.0 | 16.55 | False |  |
| rv600_softveto6_max_3_entries_mid_120_420_ev12 | position_capped | 4 | 70 | 26 | 1317.0 | 288.0 | 18.81 | 50.65 | 8/10 | 0.62 | 0.20 | 113.0 | 16.55 | False |  |
| rv600_softveto10_max_3_entries_mid_120_420_ev12 | all_entries | 4 | 70 | 26 | 1317.0 | 288.0 | 18.81 | 50.65 | 8/10 | 0.62 | 0.20 | 113.0 | 16.55 | False |  |
| rv600_softveto10_max_3_entries_mid_120_420_ev12 | position_capped | 4 | 70 | 26 | 1317.0 | 288.0 | 18.81 | 50.65 | 8/10 | 0.62 | 0.20 | 113.0 | 16.55 | False |  |
| rv600_primary_max_3_entries_base_70_420_ev12 | all_entries | 3 | 73 | 26 | 1284.0 | 288.0 | 17.59 | 49.38 | 8/10 | 0.62 | 0.21 | 113.0 | 14.79 | False |  |
| rv600_softveto6_max_3_entries_base_70_420_ev12 | all_entries | 4 | 73 | 26 | 1284.0 | 288.0 | 17.59 | 49.38 | 8/10 | 0.62 | 0.21 | 113.0 | 14.79 | False |  |
| rv600_softveto6_max_3_entries_base_70_420_ev12 | position_capped | 4 | 73 | 26 | 1284.0 | 288.0 | 17.59 | 49.38 | 8/10 | 0.62 | 0.21 | 113.0 | 14.79 | False |  |
| rv600_softveto10_max_3_entries_base_70_420_ev12 | all_entries | 4 | 73 | 26 | 1284.0 | 288.0 | 17.59 | 49.38 | 8/10 | 0.62 | 0.21 | 113.0 | 14.79 | False |  |
| rv600_softveto10_max_3_entries_base_70_420_ev12 | position_capped | 4 | 73 | 26 | 1284.0 | 288.0 | 17.59 | 49.38 | 8/10 | 0.62 | 0.21 | 113.0 | 14.79 | False |  |
| rv600_primary_risk_cap_200c_mid_120_420_ev12 | all_entries | 3 | 70 | 26 | 1219.0 | 288.0 | 17.41 | 46.88 | 8/10 | 0.62 | 0.22 | 113.0 | 14.32 | False |  |
| rv600_softveto6_risk_cap_200c_mid_120_420_ev12 | all_entries | 4 | 70 | 26 | 1219.0 | 288.0 | 17.41 | 46.88 | 8/10 | 0.62 | 0.22 | 113.0 | 14.32 | False |  |
| rv600_softveto6_risk_cap_200c_mid_120_420_ev12 | position_capped | 4 | 70 | 26 | 1219.0 | 288.0 | 17.41 | 46.88 | 8/10 | 0.62 | 0.22 | 113.0 | 14.32 | False |  |
| rv600_softveto10_risk_cap_200c_mid_120_420_ev12 | all_entries | 4 | 70 | 26 | 1219.0 | 288.0 | 17.41 | 46.88 | 8/10 | 0.62 | 0.22 | 113.0 | 14.32 | False |  |
| rv600_softveto10_risk_cap_200c_mid_120_420_ev12 | position_capped | 4 | 70 | 26 | 1219.0 | 288.0 | 17.41 | 46.88 | 8/10 | 0.62 | 0.22 | 113.0 | 14.32 | False |  |
| rv600_primary_risk_cap_200c_base_70_420_ev12 | all_entries | 3 | 73 | 26 | 1186.0 | 288.0 | 16.25 | 45.62 | 8/10 | 0.62 | 0.23 | 113.0 | 12.70 | False |  |
| rv600_softveto6_risk_cap_200c_base_70_420_ev12 | all_entries | 4 | 73 | 26 | 1186.0 | 288.0 | 16.25 | 45.62 | 8/10 | 0.62 | 0.23 | 113.0 | 12.70 | False |  |

## Roots

- particle_dynamic600_oos_20260511TLOCKEDNEXT2
- particle_dynamic_oos_20260511TLOCKEDNEXT
- particle_fixed_terminal_oos_GAUSS45LOCK001
- particle_fixed_terminal_oos_GAUSS45LOCK002
- particle_fixed_terminal_oos_GAUSS45LOCK003
- particle_residual_blend_oos_RESIDLOCK001
- particle_shadow_forward_20260511T053741Z-long900
- particle_side_consensus_oos_CONSENSUSLOCK001
- particle_side_safety_oos_20260511TLOCKED
- particle_spot_rv_terminal_oos_RVTERMLOCK001

## Notes

- This is discovery/shadow research only; it does not place orders or change live v28 logic.
- Repeated-entry variants are reported under all_entries, one_per_side_per_market, and position_capped accounting.
- Locked-candidate eligibility is retrospective only and still requires forward-shadow validation before any live pilot.
