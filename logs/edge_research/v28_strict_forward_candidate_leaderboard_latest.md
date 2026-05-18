# v28 Strict-Forward Candidate Leaderboard

Research-only. Diagnostic/pre-freeze rows are excluded from promotion-ranked tables.

- Generated UTC: `2026-05-11T03:10:25.829006+00:00`
- Live baseline: `-117c ($-1.17)`
- All tracked rows with PnL: `994`
- Strict-forward rows: `520`
- Diagnostic/pre-freeze rows excluded: `474`
- Strict positive rows: `353`
- Strict target-coverage positive rows: `242`
- Strict live-ready rows: `1`

## Top Strict-Forward Positive Rows

| gate | policy | settled | W/L | coverage | net | recon | cushion | missing gates |
|---|---|---:|---:|---:|---:|---:|---:|---|
| exit_reduce_suppression | `suppress_reduce_p_hold_ge_075` | 132 | 92/40 | n/a | 1058c ($10.58) | n/a | 10 | live_ready_false |
| exit_book_gap_suppression | `suppress_soft_gap15_or_p_hold75` | 120 | 82/38 | n/a | 962c ($9.62) | n/a | 9 | live_ready_false |
| false_conviction_family_scorecard | `false_conviction_fv_entry_bridge` | 70 | 48/22 | 75.27% | 762c ($7.62) | 91.43% | 7 | source_share_high_by_0.56, live_ready_false |
| exit_reduce_yes_suppression | `suppress_yes_reduce_p_hold_ge_075` | 103 | 67/36 | n/a | 747c ($7.47) | n/a | 7 | live_ready_false |
| soft_frontier_midprice_boundary_exit_stack | `post_midprice_shrink_birth_entry_control_no_shrink_loss_guard_v1_weighted_exit_stack` | 24 | 22/2 | 80.00% | 704c ($7.04) | 8.70% | 6 | settled+6, live_ready_false |
| approved_entry_book_fv | `actual_approved_entries + book_probability` | 133 | n/a | n/a | 701c ($7.01) | 0.00% | 7 | coverage_unknown, live_ready_false |
| soft_frontier_midprice_boundary_exit_stack | `post_midprice_shrink_birth_entry_half_midprice_boundary_loss_guard_v1_weighted_exit_stack` | 24 | 22/2 | 80.00% | 701c ($7.01) | 8.70% | 6 | settled+6, live_ready_false |
| soft_frontier_midprice_boundary_exit_stack | `post_midprice_shrink_birth_entry_quarter_midprice_boundary_loss_guard_v1_weighted_exit_stack` | 24 | 22/2 | 80.00% | 700c ($7.00) | 8.70% | 6 | settled+6, live_ready_false |
| feature_gate_size_shrink_exit_overlay | `post_feature_freeze_entry_repair_low_absd_quarter_else_half_base_current_exit_control` | 66 | 51/14 | 80.49% | 693c ($6.93) | 39.39% | 6 | source_share_high_by_0.04, live_ready_false |
| feature_gate_size_shrink_exit_overlay | `post_feature_freeze_bridge_repair_low_absd_quarter_else_half_base_current_exit_control` | 66 | 51/14 | 80.49% | 693c ($6.93) | 39.39% | 6 | source_share_high_by_0.04, live_ready_false |
| soft_frontier_midprice_boundary_exit_stack | `post_midprice_shrink_birth_entry_control_no_shrink_loss_guard_v3_weighted_exit_stack` | 24 | 22/2 | 80.00% | 668c ($6.68) | 8.70% | 6 | settled+6, live_ready_false |
| soft_frontier_midprice_boundary_exit_stack | `post_midprice_shrink_birth_entry_half_midprice_boundary_loss_guard_v3_weighted_exit_stack` | 24 | 22/2 | 80.00% | 665c ($6.65) | 8.70% | 6 | settled+6, live_ready_false |
| soft_frontier_midprice_boundary_exit_stack | `post_midprice_shrink_birth_entry_quarter_midprice_boundary_loss_guard_v3_weighted_exit_stack` | 24 | 22/2 | 80.00% | 664c ($6.63) | 8.70% | 6 | settled+6, live_ready_false |
| p50_book_edge_entry | `p50_book_plus_05_edge_nonnegative` | 104 | 64/40 | 88.14% | 660c ($6.60) | 78.85% | 6 | source_share_high_by_0.44, live_ready_false |
| soft_frontier_midprice_boundary_exit_stack | `post_midprice_shrink_birth_entry_control_no_shrink_loss_guard_v2_weighted_exit_stack` | 24 | 22/2 | 80.00% | 656c ($6.56) | 8.70% | 6 | settled+6, live_ready_false |
| soft_frontier_midprice_boundary_exit_stack | `post_midprice_shrink_birth_entry_half_midprice_boundary_loss_guard_v2_weighted_exit_stack` | 24 | 22/2 | 80.00% | 653c ($6.53) | 8.70% | 6 | settled+6, live_ready_false |
| soft_frontier_midprice_boundary_exit_stack | `post_midprice_shrink_birth_entry_quarter_midprice_boundary_loss_guard_v2_weighted_exit_stack` | 24 | 22/2 | 80.00% | 652c ($6.51) | 8.70% | 6 | settled+6, live_ready_false |
| exit_book_gap_loss_guard_v3 | `book_gap_loss_guard_v3_value_gap0_or_p85_shallow_or_p95_extreme_reduce_p79_gap0` | 46 | 33/13 | n/a | 644c ($6.44) | n/a | 6 | live_ready_false |
| exit_midband_reduce_rescue | `post_birth_midband_p60_75_exit50_75_asklt80` | 42 | 30/11 | n/a | 590c ($5.90) | n/a | 0 | cushion+3, live_ready_false |
| exit_midband_reduce_rescue | `post_birth_midband_p60_75_exit50_75_asklt80_fairddgte0` | 42 | 30/11 | n/a | 590c ($5.90) | n/a | 0 | cushion+3, live_ready_false |

## Closest Strict Target-Coverage Positive Rows

| gate | policy | settled | W/L | coverage | net | recon | cushion | missing gates |
|---|---|---:|---:|---:|---:|---:|---:|---|
| false_conviction_family_scorecard | `false_conviction_fv_entry_bridge` | 70 | 48/22 | 75.27% | 762c ($7.62) | 91.43% | 7 | source_share_high_by_0.56, live_ready_false |
| feature_gate_size_shrink_exit_overlay | `post_feature_freeze_entry_repair_low_absd_quarter_else_half_base_current_exit_control` | 66 | 51/14 | 80.49% | 693c ($6.93) | 39.39% | 6 | source_share_high_by_0.04, live_ready_false |
| feature_gate_size_shrink_exit_overlay | `post_feature_freeze_bridge_repair_low_absd_quarter_else_half_base_current_exit_control` | 66 | 51/14 | 80.49% | 693c ($6.93) | 39.39% | 6 | source_share_high_by_0.04, live_ready_false |
| p50_book_edge_entry | `p50_book_plus_05_edge_nonnegative` | 104 | 64/40 | 88.14% | 660c ($6.60) | 78.85% | 6 | source_share_high_by_0.44, live_ready_false |
| feature_gate_size_shrink_exit_overlay | `post_feature_freeze_entry_repair_low_absd_quarter_else_half_book_gap_only` | 66 | 50/15 | 80.49% | 505c ($5.05) | 39.39% | 5 | source_share_high_by_0.04, live_ready_false |
| feature_gate_size_shrink_exit_overlay | `post_feature_freeze_entry_repair_low_absd_quarter_else_half_book_gap_or_reduce_p75` | 66 | 50/15 | 80.49% | 505c ($5.05) | 39.39% | 5 | source_share_high_by_0.04, live_ready_false |
| feature_gate_size_shrink_exit_overlay | `post_feature_freeze_entry_repair_low_absd_quarter_else_half_book_gap_or_clip_p60_drawdown10` | 66 | 50/15 | 80.49% | 505c ($5.05) | 39.39% | 5 | source_share_high_by_0.04, live_ready_false |
| feature_gate_size_shrink_exit_overlay | `post_feature_freeze_entry_repair_low_absd_quarter_else_half_book_gap_or_reduce_p75_or_clip` | 66 | 50/15 | 80.49% | 505c ($5.05) | 39.39% | 5 | source_share_high_by_0.04, live_ready_false |
| feature_gate_size_shrink_exit_overlay | `post_feature_freeze_bridge_repair_low_absd_quarter_else_half_book_gap_only` | 66 | 50/15 | 80.49% | 505c ($5.05) | 39.39% | 5 | source_share_high_by_0.04, live_ready_false |
| feature_gate_size_shrink_exit_overlay | `post_feature_freeze_bridge_repair_low_absd_quarter_else_half_book_gap_or_reduce_p75` | 66 | 50/15 | 80.49% | 505c ($5.05) | 39.39% | 5 | source_share_high_by_0.04, live_ready_false |
| feature_gate_size_shrink_exit_overlay | `post_feature_freeze_bridge_repair_low_absd_quarter_else_half_book_gap_or_clip_p60_drawdown10` | 66 | 50/15 | 80.49% | 505c ($5.05) | 39.39% | 5 | source_share_high_by_0.04, live_ready_false |
| feature_gate_size_shrink_exit_overlay | `post_feature_freeze_bridge_repair_low_absd_quarter_else_half_book_gap_or_reduce_p75_or_clip` | 66 | 50/15 | 80.49% | 505c ($5.05) | 39.39% | 5 | source_share_high_by_0.04, live_ready_false |
| feature_gate_size_shrink_exit_overlay | `post_feature_freeze_entry_repair_low_absd_quarter_else_half_reduce_p75_only` | 66 | 51/14 | 80.49% | 469c ($4.69) | 39.39% | 4 | source_share_high_by_0.04, live_ready_false |
| feature_gate_size_shrink_exit_overlay | `post_feature_freeze_entry_repair_low_absd_quarter_else_half_clip_p60_drawdown10_only` | 66 | 51/14 | 80.49% | 469c ($4.69) | 39.39% | 4 | source_share_high_by_0.04, live_ready_false |
| feature_gate_size_shrink_exit_overlay | `post_feature_freeze_bridge_repair_low_absd_quarter_else_half_reduce_p75_only` | 66 | 51/14 | 80.49% | 469c ($4.69) | 39.39% | 4 | source_share_high_by_0.04, live_ready_false |
| feature_gate_size_shrink_exit_overlay | `post_feature_freeze_bridge_repair_low_absd_quarter_else_half_clip_p60_drawdown10_only` | 66 | 51/14 | 80.49% | 469c ($4.69) | 39.39% | 4 | source_share_high_by_0.04, live_ready_false |
| soft_frontier_midprice_boundary_exit_stack | `post_midprice_shrink_birth_entry_control_no_shrink_loss_guard_v1_weighted_exit_stack` | 24 | 22/2 | 80.00% | 704c ($7.04) | 8.70% | 6 | settled+6, live_ready_false |
| soft_frontier_midprice_boundary_exit_stack | `post_midprice_shrink_birth_entry_half_midprice_boundary_loss_guard_v1_weighted_exit_stack` | 24 | 22/2 | 80.00% | 701c ($7.01) | 8.70% | 6 | settled+6, live_ready_false |
| soft_frontier_midprice_boundary_exit_stack | `post_midprice_shrink_birth_entry_quarter_midprice_boundary_loss_guard_v1_weighted_exit_stack` | 24 | 22/2 | 80.00% | 700c ($7.00) | 8.70% | 6 | settled+6, live_ready_false |
| feature_gate_coverage_size_shrink | `post_feature_freeze_entry_repair_eighth` | 66 | 54/12 | 80.49% | 424c ($4.24) | 39.39% | 4 | source_share_high_by_0.04, live_ready_false |

## Excluded Top Diagnostic Rows

| gate | policy | settled | W/L | coverage | net | recon | cushion | missing gates |
|---|---|---:|---:|---:|---:|---:|---:|---|
| top_component_parent_fill_repair_child | `diagnostic_observable_mid_confidence_parent_fill_quarter` | 76 | 67/9 | 75.25% | 2233c ($22.33) | 34.21% | 22 | strict_forward_evidence, live_ready_false |
| top_component_parent_fill_repair_child | `diagnostic_mid_confidence_parent_fill_quarter` | 76 | 67/9 | 75.25% | 2233c ($22.33) | 34.21% | 22 | strict_forward_evidence, live_ready_false |
| top_component_parent_fill_repair_child | `diagnostic_observable_mid_confidence_parent_fill_half` | 76 | 67/9 | 75.25% | 2190c ($21.89) | 34.21% | 21 | strict_forward_evidence, live_ready_false |
| top_component_parent_fill_repair_child | `diagnostic_mid_confidence_parent_fill_half` | 76 | 67/9 | 75.25% | 2190c ($21.89) | 34.21% | 21 | strict_forward_evidence, live_ready_false |
| top_component_parent_fill_repair_child | `diagnostic_parent_fill_wide_mid_absd_ask_notch` | 76 | 67/9 | 75.25% | 2145c ($21.45) | 34.21% | 21 | strict_forward_evidence, live_ready_false |
| top_component_parent_fill_repair_child | `diagnostic_parent_fill_mid_absd_ask_notch` | 76 | 67/9 | 75.25% | 2142c ($21.42) | 34.21% | 21 | strict_forward_evidence, live_ready_false |
| top_component_parent_fill_repair_child | `diagnostic_smooth_parent_fill_source_risk` | 76 | 67/9 | 75.25% | 2127c ($21.27) | 34.21% | 21 | strict_forward_evidence, live_ready_false |
| top_component_false_negative_rescue_child | `diagnostic_union_rebound` | 76 | 67/9 | 75.25% | 2102c ($21.02) | 34.21% | 21 | strict_forward_evidence, live_ready_false |
| top_component_false_negative_rescue_child | `diagnostic_approved_union_rebound` | 76 | 67/9 | 75.25% | 2102c ($21.02) | 34.21% | 21 | strict_forward_evidence, live_ready_false |
| top_component_parent_fill_repair_child | `diagnostic_exit_child_only_control` | 76 | 67/9 | 75.25% | 2102c ($21.02) | 34.21% | 21 | strict_forward_evidence, live_ready_false |
| top_component_parent_fill_repair_child | `diagnostic_parent_fill_all_rejected_half` | 76 | 67/9 | 75.25% | 2095c ($20.95) | 34.21% | 20 | strict_forward_evidence, live_ready_false |
| top_component_parent_fill_repair_child | `diagnostic_parent_fill_all_rejected_quarter` | 76 | 67/9 | 75.25% | 2091c ($20.91) | 34.21% | 20 | strict_forward_evidence, live_ready_false |
| top_component_false_negative_rescue_child | `diagnostic_low_exit_collapse_rebound` | 76 | 66/10 | 75.25% | 2008c ($20.09) | 34.21% | 20 | strict_forward_evidence, live_ready_false |
| top_component_false_negative_rescue_child | `diagnostic_mid_recheck_value_rebound` | 76 | 66/10 | 75.25% | 1926c ($19.27) | 34.21% | 19 | strict_forward_evidence, live_ready_false |
| dual_lane_overlap_union | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_entry_cheap_penalty025_rank_only` | 83 | 68/15 | 82.18% | 1842c ($18.43) | 21.69% | 18 | strict_forward_evidence, live_ready_false |
| dual_lane_overlap_union | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_entry_cheap_penalty050_rank_only` | 83 | 68/15 | 82.18% | 1842c ($18.43) | 21.69% | 18 | strict_forward_evidence, live_ready_false |
| dual_lane_overlap_union | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_entry_cheap_penalty100_rank_only` | 83 | 68/15 | 82.18% | 1842c ($18.43) | 21.69% | 18 | strict_forward_evidence, live_ready_false |
| dual_lane_overlap_union | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty025_rank_only` | 83 | 68/15 | 82.18% | 1842c ($18.43) | 21.69% | 18 | strict_forward_evidence, live_ready_false |
| dual_lane_overlap_union | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty050_rank_only` | 83 | 68/15 | 82.18% | 1842c ($18.43) | 21.69% | 18 | strict_forward_evidence, live_ready_false |
| dual_lane_overlap_union | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty100_rank_only` | 83 | 68/15 | 82.18% | 1842c ($18.43) | 21.69% | 18 | strict_forward_evidence, live_ready_false |
