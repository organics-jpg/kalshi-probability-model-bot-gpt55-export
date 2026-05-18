# RV600 Plan Family Rejection Ledger

- generated_utc: 2026-05-15T21:22:02+00:00
- research_only: True
- decision: no_existing_plan_family_viable

## Inputs

- grid_phase: grid
- grid_root_count: 25
- grid_variant_count: 3948
- grid_summary_row_count: 11844
- best_by_total_pnl: `blend_80_20_max_3_entries_broad_70_600_ev20`
- best_locked_candidate: ``
- promotion_allowed: False
- futility_decision: `reject_current_locked_family_for_promotion`
- futility_success_probability: 0.0000
- audit_goal_complete: False
- audit_forward_entries: 15
- audit_forward_markets: 15
- audit_forward_pnl_cents: -155.3

## Family Decisions

| family | values tested | values with rows | values with candidate | best value | best pnl | best entries | best markets | main rejection | decision |
|---|---:|---:|---:|---|---:|---:|---:|---|---|
| A_timing_windows | 7 | 7 | 0 | `broad_70_600` | 209.0 | 15 | 5 | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct | all_values_rejected |
| B_ev_thresholds | 9 | 9 | 0 | `ev20` | 209.0 | 15 | 5 | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct | all_values_rejected |
| C_repeated_entry_rules | 10 | 10 | 0 | `max_3_entries` | 209.0 | 15 | 5 | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct | all_values_rejected |
| D_side_filters | 5 | 4 | 0 | `side_by_v28_disagreement` | 6.7 | 4 | 4 | fewer_than_25_entries;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive | all_values_rejected |
| E_v28_transfer_controls | 8 | 6 | 0 | `blend_80_20` | 209.0 | 15 | 5 | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct | all_values_rejected |
| F_volatility_regime_filters | 7 | 7 | 0 | `strike_far` | 10.0 | 4 | 4 | fewer_than_25_entries;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive | all_values_rejected |
| G_microstructure_filters | 8 | 8 | 0 | `depth_ratio_3` | -170.0 | 15 | 15 | fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive | all_values_rejected |
| H_price_caps_payoff_shape | 5 | 5 | 0 | `rich_tail` | 15.0 | 1 | 1 | fewer_than_25_entries;positive_roots_below_60pct;single_market_share_above_25pct;last_window_nonpositive | all_values_rejected |

## Top Existing Rows

| variant | accounting | gates | entries | markets | pnl_c | v28_delta_c | reject |
|---|---|---:|---:|---:|---:|---:|---|
| `blend_80_20_max_3_entries_broad_70_600_ev20` | all_entries | 4 | 15 | 5 | 209.0 | 0.0 | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| `blend_80_20_max_3_entries_broad_70_600_ev20` | position_capped | 4 | 15 | 5 | 209.0 | 0.0 | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| `blend_80_20_risk_cap_200c_broad_70_600_ev20` | all_entries | 4 | 15 | 5 | 209.0 | 0.0 | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| `blend_80_20_risk_cap_200c_broad_70_600_ev20` | position_capped | 4 | 15 | 5 | 209.0 | 0.0 | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| `blend_90_10_max_3_entries_broad_70_600_ev20` | all_entries | 4 | 15 | 5 | 195.0 | 0.0 | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| `blend_90_10_max_3_entries_broad_70_600_ev20` | position_capped | 4 | 15 | 5 | 195.0 | 0.0 | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| `blend_90_10_risk_cap_200c_broad_70_600_ev20` | all_entries | 4 | 15 | 5 | 195.0 | 0.0 | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| `blend_90_10_risk_cap_200c_broad_70_600_ev20` | position_capped | 4 | 15 | 5 | 195.0 | 0.0 | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| `blend_90_10_same_side_ev_step_3c_late_70_180_ev20` | all_entries | 4 | 8 | 4 | 193.0 | 0.0 | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| `blend_90_10_same_side_ev_step_3c_late_70_180_ev20` | position_capped | 4 | 8 | 4 | 193.0 | 0.0 | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| `blend_95_5_same_side_ev_step_3c_late_70_180_ev20` | all_entries | 4 | 9 | 5 | 191.0 | 0.0 | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| `blend_95_5_same_side_ev_step_3c_late_70_180_ev20` | position_capped | 4 | 9 | 5 | 191.0 | 0.0 | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| `blend_95_5_max_3_entries_broad_70_600_ev20` | all_entries | 4 | 18 | 6 | 189.0 | 0.0 | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| `blend_95_5_max_3_entries_broad_70_600_ev20` | position_capped | 4 | 18 | 6 | 189.0 | 0.0 | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |
| `blend_95_5_risk_cap_200c_broad_70_600_ev20` | all_entries | 4 | 18 | 6 | 189.0 | 0.0 | fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct |

## Conclusion

All plan-defined RV600 families are rejected on current forward evidence.
The blockers are not missing implementation coverage; they are sparse positive rows, poor root/market stability, concentration, nonpositive recent windows, and no matched-v28 edge.
Do not promote or live-test any current RV600 family. A future RV600 attempt needs a newly frozen candidate and must restart the same anti-overfitting and forward-shadow gates from scratch.
