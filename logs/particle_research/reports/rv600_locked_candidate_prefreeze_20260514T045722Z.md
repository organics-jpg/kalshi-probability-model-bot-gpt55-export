# RV600 Variation Test Report

- generated_utc: 2026-05-14T05:25:54+00:00
- phase: locked
- promotion_allowed: False
- root_count: 1
- variant_count: 6
- best_by_total_pnl: rv600_primary_max_2_entries_mid_120_420_ev12
- best_locked_candidate: 
- locked_candidates: none
- conclusion: locked found best total PnL row rv600_primary_max_2_entries_mid_120_420_ev12/all_entries at 150.0c, but no candidate cleared the locked simplification gates. Keep RV600 research-only.

## Top Summary Rows

| variant | accounting | gates | entries | markets | pnl_c | v28_delta_c | avg_entry_c | avg_market_c | +roots | +markets | max_market_share | last20_c | added_avg_c | locked? | reject |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| rv600_primary_max_2_entries_mid_120_420_ev12 | all_entries | 3 | 4 | 2 | 150.0 | 0.0 | 37.50 | 75.00 | 1/1 | 0.50 | 1.07 | 150.0 | 37.50 | False | fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| rv600_primary_max_2_entries_mid_120_420_ev12 | position_capped | 3 | 4 | 2 | 150.0 | 0.0 | 37.50 | 75.00 | 1/1 | 0.50 | 1.07 | 150.0 | 37.50 | False | fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| rv600_primary_max_3_entries_mid_120_420_ev12 | all_entries | 3 | 5 | 2 | 145.0 | 0.0 | 29.00 | 72.50 | 1/1 | 0.50 | 1.10 | 145.0 | 23.33 | False | fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| rv600_primary_max_3_entries_mid_120_420_ev12 | position_capped | 3 | 5 | 2 | 145.0 | 0.0 | 29.00 | 72.50 | 1/1 | 0.50 | 1.10 | 145.0 | 23.33 | False | fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| rv600_primary_max_3_entries_base_70_420_ev12 | all_entries | 3 | 5 | 2 | 145.0 | 0.0 | 29.00 | 72.50 | 1/1 | 0.50 | 1.10 | 145.0 | 23.33 | False | fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| rv600_primary_max_3_entries_base_70_420_ev12 | position_capped | 3 | 5 | 2 | 145.0 | 0.0 | 29.00 | 72.50 | 1/1 | 0.50 | 1.10 | 145.0 | 23.33 | False | fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| rv600_primary_risk_cap_200c_mid_120_420_ev12 | all_entries | 3 | 5 | 2 | 145.0 | 0.0 | 29.00 | 72.50 | 1/1 | 0.50 | 1.10 | 145.0 | 23.33 | False | fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| rv600_primary_risk_cap_200c_mid_120_420_ev12 | position_capped | 3 | 5 | 2 | 145.0 | 0.0 | 29.00 | 72.50 | 1/1 | 0.50 | 1.10 | 145.0 | 23.33 | False | fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| rv600_primary_risk_cap_200c_base_70_420_ev12 | all_entries | 3 | 5 | 2 | 145.0 | 0.0 | 29.00 | 72.50 | 1/1 | 0.50 | 1.10 | 145.0 | 23.33 | False | fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| rv600_primary_risk_cap_200c_base_70_420_ev12 | position_capped | 3 | 5 | 2 | 145.0 | 0.0 | 29.00 | 72.50 | 1/1 | 0.50 | 1.10 | 145.0 | 23.33 | False | fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| rv600_primary_max_3_entries_mid_120_420_ev12 | one_per_side_per_market | 3 | 2 | 2 | 75.0 | 0.0 | 37.50 | 37.50 | 1/1 | 0.50 | 1.07 | 75.0 | 23.33 | False | fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| rv600_primary_max_3_entries_base_70_420_ev12 | one_per_side_per_market | 3 | 2 | 2 | 75.0 | 0.0 | 37.50 | 37.50 | 1/1 | 0.50 | 1.07 | 75.0 | 23.33 | False | fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| rv600_primary_risk_cap_200c_mid_120_420_ev12 | one_per_side_per_market | 3 | 2 | 2 | 75.0 | 0.0 | 37.50 | 37.50 | 1/1 | 0.50 | 1.07 | 75.0 | 23.33 | False | fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| rv600_primary_risk_cap_200c_base_70_420_ev12 | one_per_side_per_market | 3 | 2 | 2 | 75.0 | 0.0 | 37.50 | 37.50 | 1/1 | 0.50 | 1.07 | 75.0 | 23.33 | False | fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| rv600_primary_max_2_entries_mid_120_420_ev12 | one_per_side_per_market | 3 | 2 | 2 | 75.0 | 0.0 | 37.50 | 37.50 | 1/1 | 0.50 | 1.07 | 75.0 | 37.50 | False | fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| rv600_primary_side_flip_only_broad_70_600_ev4 | all_entries | 3 | 2 | 2 | 56.0 | 0.0 | 28.00 | 28.00 | 1/1 | 0.50 | 1.09 | 56.0 | 0.00 | False | fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| rv600_primary_side_flip_only_broad_70_600_ev4 | one_per_side_per_market | 3 | 2 | 2 | 56.0 | 0.0 | 28.00 | 28.00 | 1/1 | 0.50 | 1.09 | 56.0 | 0.00 | False | fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |
| rv600_primary_side_flip_only_broad_70_600_ev4 | position_capped | 3 | 2 | 2 | 56.0 | 0.0 | 28.00 | 28.00 | 1/1 | 0.50 | 1.09 | 56.0 | 0.00 | False | fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct |

## Roots

- rv600_next_evidence_shadow_20260514T045722Z

## Notes

- This is discovery/shadow research only; it does not place orders or change live v28 logic.
- Repeated-entry variants are reported under all_entries, one_per_side_per_market, and position_capped accounting.
- Locked-candidate eligibility is retrospective only and still requires forward-shadow validation before any live pilot.
