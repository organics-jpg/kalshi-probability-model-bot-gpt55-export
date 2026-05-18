# RV600 Variation Test Report

- generated_utc: 2026-05-13T05:33:39+00:00
- phase: first_candidates
- promotion_allowed: False
- root_count: 10
- variant_count: 6
- best_by_total_pnl: rv600_max3_risk200_70_420_ev10
- best_locked_candidate: 
- locked_candidates: none
- conclusion: first_candidates found best total PnL row rv600_max3_risk200_70_420_ev10/all_entries at 1519.0c, but no candidate cleared the locked simplification gates. Keep RV600 research-only.

## Top Summary Rows

| variant | accounting | gates | entries | markets | pnl_c | v28_delta_c | avg_entry_c | avg_market_c | +roots | +markets | max_market_share | last20_c | added_avg_c | locked? | reject |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| rv600_max3_risk200_70_420_ev10 | all_entries | 3 | 94 | 33 | 1519.0 | 152.0 | 16.16 | 46.03 | 7/10 | 0.58 | 0.18 | 51.0 | 13.72 | False | positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct;market_drawdown_worse_than_25pct |
| rv600_max3_risk200_70_420_ev10 | position_capped | 3 | 94 | 33 | 1519.0 | 152.0 | 16.16 | 46.03 | 7/10 | 0.58 | 0.18 | 51.0 | 13.72 | False | positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct |
| rv600_max2_evstep5_70_420_ev10 | all_entries | 3 | 56 | 33 | 863.0 | 137.0 | 15.41 | 26.15 | 8/10 | 0.58 | 0.21 | 57.0 | 7.87 | False | positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct;market_drawdown_worse_than_25pct |
| rv600_max2_evstep5_70_420_ev10 | position_capped | 3 | 56 | 33 | 863.0 | 137.0 | 15.41 | 26.15 | 8/10 | 0.58 | 0.21 | 57.0 | 7.87 | False | positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct |
| rv600_max2_refresh120_70_420_ev10 | all_entries | 3 | 56 | 33 | 776.0 | 155.0 | 13.86 | 23.52 | 7/10 | 0.55 | 0.22 | -10.0 | 4.09 | False | positive_markets_below_60pct;last_window_nonpositive;market_drawdown_worse_than_25pct |
| rv600_max2_refresh120_70_420_ev10 | position_capped | 3 | 56 | 33 | 776.0 | 155.0 | 13.86 | 23.52 | 7/10 | 0.55 | 0.22 | -10.0 | 4.09 | False | positive_markets_below_60pct;last_window_nonpositive |
| rv600_single_70_420_ev10 | all_entries | 3 | 33 | 33 | 682.0 | 17.0 | 20.67 | 20.67 | 8/10 | 0.55 | 0.14 | 9.0 | 0.00 | False | positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct;single_market_benchmark |
| rv600_single_70_420_ev10 | one_per_side_per_market | 3 | 33 | 33 | 682.0 | 17.0 | 20.67 | 20.67 | 8/10 | 0.55 | 0.14 | 9.0 | 0.00 | False | positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct |
| rv600_single_70_420_ev10 | position_capped | 3 | 33 | 33 | 682.0 | 17.0 | 20.67 | 20.67 | 8/10 | 0.55 | 0.14 | 9.0 | 0.00 | False | positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct |
| v28_95_rv600_05_70_420_ev8 | all_entries | 4 | 33 | 33 | 661.0 | 0.0 | 20.03 | 20.03 | 7/10 | 0.61 | 0.13 | 22.0 | 0.00 | False | does_not_beat_matched_v28_by_20pct;does_not_beat_single_market;added_entries_nonpositive;avg_market_not_improved |
| v28_95_rv600_05_70_420_ev8 | one_per_side_per_market | 4 | 33 | 33 | 661.0 | 0.0 | 20.03 | 20.03 | 7/10 | 0.61 | 0.13 | 22.0 | 0.00 | False | does_not_beat_matched_v28_by_20pct |
| v28_95_rv600_05_70_420_ev8 | position_capped | 4 | 33 | 33 | 661.0 | 0.0 | 20.03 | 20.03 | 7/10 | 0.61 | 0.13 | 22.0 | 0.00 | False | does_not_beat_matched_v28_by_20pct |
| rv600_max3_risk200_70_420_ev10 | one_per_side_per_market | 3 | 40 | 33 | 622.0 | 17.0 | 15.55 | 18.85 | 8/10 | 0.58 | 0.15 | 9.0 | 13.72 | False | positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct |
| rv600_v28_softveto6_max2_70_420_ev8 | all_entries | 4 | 62 | 35 | 542.0 | 163.0 | 8.74 | 15.49 | 7/10 | 0.54 | 0.31 | -34.0 | -2.56 | False | avg_entry_below_10c;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_single_market;added_entries_nonpositive;avg_market_not_improved;market_drawdown_worse_than_25pct |
| rv600_v28_softveto6_max2_70_420_ev8 | position_capped | 4 | 62 | 35 | 542.0 | 163.0 | 8.74 | 15.49 | 7/10 | 0.54 | 0.31 | -34.0 | -2.56 | False | avg_entry_below_10c;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive |
| rv600_max2_refresh120_70_420_ev10 | one_per_side_per_market | 3 | 43 | 33 | 536.0 | 17.0 | 12.47 | 16.24 | 8/10 | 0.55 | 0.16 | 6.0 | 4.09 | False | positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct |
| rv600_max2_evstep5_70_420_ev10 | one_per_side_per_market | 3 | 43 | 33 | 527.0 | 17.0 | 12.26 | 15.97 | 8/10 | 0.58 | 0.18 | 9.0 | 7.87 | False | positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct |
| rv600_v28_softveto6_max2_70_420_ev8 | one_per_side_per_market | 4 | 50 | 35 | 394.0 | 3.0 | 7.88 | 11.26 | 7/10 | 0.54 | 0.20 | -13.0 | -2.56 | False | avg_entry_below_10c;positive_markets_below_60pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |

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
