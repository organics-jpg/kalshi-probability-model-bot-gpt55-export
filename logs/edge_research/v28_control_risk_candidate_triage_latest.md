# v28 Control-Risk Candidate Triage

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:10:25.383751+00:00`
- Positive rows: `788` / `995`
- Positive target-coverage rows: `582`
- Positive strict rows: `225`
- Tracker-apparent control-only target rows: `4`
- Integrity-merged control-only target rows: `0`
- Integrity-merged control-only strict target rows: `0`

## Interpretation

- This is a promotion-safety report only; it does not weaken the live-readiness risk stop.
- Tracker-only blockers can understate candidate risk. After integrity blockers are merged, 0 target-coverage positive rows are blocked only by the global control-risk/live-ready status.
- Control risk remains active by loss_count; the latest risk audit shows 75 losing scored trades, 15.360501567398119% max drawdown, and 1 full-loss events.

## Tracker-Apparent Control-Only Positive

| gate | policy | settled | W/L | coverage | net | target | strict | recon | cushion | merged missing |
|---|---|---:|---:|---:|---:|---|---|---:|---:|---|
| `approved_entry_book_raw_blend_fv` | `book_raw_blend_alpha_0p50` | 55 | 47/8 | n/a | 362c | False | False | n/a | 3 | none_after_global |
| `raw_p52_boundary_turbulence_skip` | `raw_p52_skip_weakraw_nearstrike_recross90` | 88 | n/a | 77.19% | 266c | True | False | 92.0% | 2 | source_share_high_0.92, cushion+1, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `composite_false_conviction_fv` | `raw_p50_turbulence_valve_edge4_p60_recross75_near25 + composite_false_conviction_full_to_50` | 81 | 48/33 | 72.97% | 127c | False | False | n/a | n/a | coverage_low_by_2.0pp, cushion_unknown |
| `early_boundary_opposite_wait_repair` | `early_boundary_wait480_p50_opposite_side_delay480` | 80 | n/a | 75.47% | 98c | True | False | n/a | 0 | cushion+3, no_source_stress_audit, full_loss_cushion_lt_3 |
| `early_boundary_wait_repair` | `early_boundary_wait480_p50_any_side` | 80 | n/a | 75.47% | 82c | True | False | n/a | 0 | cushion+3, no_source_stress_audit, full_loss_cushion_lt_3 |
| `early_no_boundary_decay_repair_entry` | `skip_early_no_boundary_decay_repair_calm_geometry` | 85 | 56/29 | 75.22% | 27c | True | False | 69.4% | 0 | source_share_high_0.69, cushion+3, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

## Integrity-Merged Control-Only Positive

| gate | policy | settled | W/L | coverage | net | target | strict | recon | cushion | merged missing |
|---|---|---:|---:|---:|---:|---|---|---:|---:|---|
| `approved_entry_book_raw_blend_fv` | `book_raw_blend_alpha_0p50` | 55 | 47/8 | n/a | 362c | False | False | n/a | 3 | none_after_global |

## Top Positive Target Rows After Integrity

| gate | policy | settled | W/L | coverage | net | target | strict | recon | cushion | merged missing |
|---|---|---:|---:|---:|---:|---|---|---:|---:|---|
| `top_component_parent_fill_repair_child` | `diagnostic_observable_mid_confidence_parent_fill_quarter` | 76 | 67/9 | 75.25% | 2233c | True | False | 34.2% | 22 | diagnostic_prefreeze, source_gate_zero_row_margin |
| `top_component_parent_fill_repair_child` | `diagnostic_mid_confidence_parent_fill_quarter` | 76 | 67/9 | 75.25% | 2233c | True | False | 34.2% | 22 | diagnostic_prefreeze, source_label_diagnostic, source_gate_zero_row_margin |
| `top_component_parent_fill_repair_child` | `diagnostic_observable_mid_confidence_parent_fill_half` | 76 | 67/9 | 75.25% | 2190c | True | False | 34.2% | 21 | diagnostic_prefreeze, source_gate_zero_row_margin |
| `top_component_parent_fill_repair_child` | `diagnostic_mid_confidence_parent_fill_half` | 76 | 67/9 | 75.25% | 2190c | True | False | 34.2% | 21 | diagnostic_prefreeze, source_label_diagnostic, source_gate_zero_row_margin |
| `top_component_parent_fill_repair_child` | `diagnostic_parent_fill_wide_mid_absd_ask_notch` | 76 | 67/9 | 75.25% | 2145c | True | False | 34.2% | 21 | diagnostic_prefreeze, source_gate_zero_row_margin |
| `top_component_parent_fill_repair_child` | `diagnostic_parent_fill_mid_absd_ask_notch` | 76 | 67/9 | 75.25% | 2142c | True | False | 34.2% | 21 | diagnostic_prefreeze, source_gate_zero_row_margin |
| `top_component_parent_fill_repair_child` | `diagnostic_smooth_parent_fill_source_risk` | 76 | 67/9 | 75.25% | 2127c | True | False | 34.2% | 21 | diagnostic_prefreeze, source_label_diagnostic, source_gate_zero_row_margin |
| `top_component_false_negative_rescue_child` | `diagnostic_union_rebound` | 76 | 67/9 | 75.25% | 2102c | True | False | 34.2% | 21 | diagnostic_prefreeze |
| `top_component_false_negative_rescue_child` | `diagnostic_approved_union_rebound` | 76 | 67/9 | 75.25% | 2102c | True | False | 34.2% | 21 | diagnostic_prefreeze |
| `top_component_parent_fill_repair_child` | `diagnostic_exit_child_only_control` | 76 | 67/9 | 75.25% | 2102c | True | False | 34.2% | 21 | diagnostic_prefreeze, source_gate_zero_row_margin |
| `top_component_parent_fill_repair_child` | `diagnostic_parent_fill_all_rejected_half` | 76 | 67/9 | 75.25% | 2095c | True | False | 34.2% | 20 | diagnostic_prefreeze, source_label_diagnostic, source_gate_zero_row_margin |
| `top_component_parent_fill_repair_child` | `diagnostic_parent_fill_all_rejected_quarter` | 76 | 67/9 | 75.25% | 2091c | True | False | 34.2% | 20 | diagnostic_prefreeze, source_label_diagnostic, source_gate_zero_row_margin |
| `top_component_false_negative_rescue_child` | `diagnostic_low_exit_collapse_rebound` | 76 | 66/10 | 75.25% | 2008c | True | False | 34.2% | 20 | diagnostic_prefreeze |
| `top_component_false_negative_rescue_child` | `diagnostic_mid_recheck_value_rebound` | 76 | 66/10 | 75.25% | 1926c | True | False | 34.2% | 19 | diagnostic_prefreeze |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_entry_cheap_penalty025_rank_only` | 83 | 68/15 | 82.18% | 1842c | True | False | 21.7% | 18 | needs_own_frozen_forward_birth |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_entry_cheap_penalty050_rank_only` | 83 | 68/15 | 82.18% | 1842c | True | False | 21.7% | 18 | needs_own_frozen_forward_birth |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_entry_cheap_penalty100_rank_only` | 83 | 68/15 | 82.18% | 1842c | True | False | 21.7% | 18 | needs_own_frozen_forward_birth |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty025_rank_only` | 83 | 68/15 | 82.18% | 1842c | True | False | 21.7% | 18 | needs_own_frozen_forward_birth |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty050_rank_only` | 83 | 68/15 | 82.18% | 1842c | True | False | 21.7% | 18 | needs_own_frozen_forward_birth |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty100_rank_only` | 83 | 68/15 | 82.18% | 1842c | True | False | 21.7% | 18 | needs_own_frozen_forward_birth |

## Top Positive Strict Rows After Integrity

| gate | policy | settled | W/L | coverage | net | target | strict | recon | cushion | merged missing |
|---|---|---:|---:|---:|---:|---|---|---:|---:|---|
| `soft_frontier_midprice_boundary_exit_stack` | `post_midprice_shrink_birth_entry_control_no_shrink_loss_guard_v1_weighted_exit_stack` | 24 | 22/2 | 80.00% | 704c | True | True | 8.7% | 6 | settled+6, entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, post_stack_joined_exit_rows_lt_30, settled_lt_30, simulated_share_gt_35pct |
| `soft_frontier_midprice_boundary_exit_stack` | `post_midprice_shrink_birth_entry_half_midprice_boundary_loss_guard_v1_weighted_exit_stack` | 24 | 22/2 | 80.00% | 701c | True | True | 8.7% | 6 | settled+6, entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, post_stack_joined_exit_rows_lt_30, settled_lt_30, simulated_share_gt_35pct |
| `soft_frontier_midprice_boundary_exit_stack` | `post_midprice_shrink_birth_entry_quarter_midprice_boundary_loss_guard_v1_weighted_exit_stack` | 24 | 22/2 | 80.00% | 700c | True | True | 8.7% | 6 | settled+6, entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, post_stack_joined_exit_rows_lt_30, settled_lt_30, simulated_share_gt_35pct |
| `feature_gate_size_shrink_exit_overlay` | `post_feature_freeze_entry_repair_low_absd_quarter_else_half_base_current_exit_control` | 66 | 51/14 | 80.49% | 693c | True | True | 39.4% | 6 | source_share_high_0.39, row_reconstructed_share_gt_35pct, simulated_share_gt_35pct |
| `feature_gate_size_shrink_exit_overlay` | `post_feature_freeze_bridge_repair_low_absd_quarter_else_half_base_current_exit_control` | 66 | 51/14 | 80.49% | 693c | True | True | 39.4% | 6 | source_share_high_0.39, row_reconstructed_share_gt_35pct, simulated_share_gt_35pct |
| `soft_frontier_midprice_boundary_exit_stack` | `post_midprice_shrink_birth_entry_control_no_shrink_loss_guard_v3_weighted_exit_stack` | 24 | 22/2 | 80.00% | 668c | True | True | 8.7% | 6 | settled+6, entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, post_stack_joined_exit_rows_lt_30, settled_lt_30, simulated_share_gt_35pct |
| `soft_frontier_midprice_boundary_exit_stack` | `post_midprice_shrink_birth_entry_half_midprice_boundary_loss_guard_v3_weighted_exit_stack` | 24 | 22/2 | 80.00% | 665c | True | True | 8.7% | 6 | settled+6, entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, post_stack_joined_exit_rows_lt_30, settled_lt_30, simulated_share_gt_35pct |
| `soft_frontier_midprice_boundary_exit_stack` | `post_midprice_shrink_birth_entry_quarter_midprice_boundary_loss_guard_v3_weighted_exit_stack` | 24 | 22/2 | 80.00% | 664c | True | True | 8.7% | 6 | settled+6, entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, post_stack_joined_exit_rows_lt_30, settled_lt_30, simulated_share_gt_35pct |
| `soft_frontier_midprice_boundary_exit_stack` | `post_midprice_shrink_birth_entry_control_no_shrink_loss_guard_v2_weighted_exit_stack` | 24 | 22/2 | 80.00% | 656c | True | True | 8.7% | 6 | settled+6, entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, post_stack_joined_exit_rows_lt_30, settled_lt_30, simulated_share_gt_35pct |
| `soft_frontier_midprice_boundary_exit_stack` | `post_midprice_shrink_birth_entry_half_midprice_boundary_loss_guard_v2_weighted_exit_stack` | 24 | 22/2 | 80.00% | 653c | True | True | 8.7% | 6 | settled+6, entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, post_stack_joined_exit_rows_lt_30, settled_lt_30, simulated_share_gt_35pct |
| `soft_frontier_midprice_boundary_exit_stack` | `post_midprice_shrink_birth_entry_quarter_midprice_boundary_loss_guard_v2_weighted_exit_stack` | 24 | 22/2 | 80.00% | 652c | True | True | 8.7% | 6 | settled+6, entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, post_stack_joined_exit_rows_lt_30, settled_lt_30, simulated_share_gt_35pct |
| `soft_frontier_midprice_boundary_dual_exit_guard` | `post_midprice_shrink_birth_entry_control_no_shrink_or_reduce_p_hold80` | 24 | 21/3 | 80.00% | 590c | True | True | 41.7% | 5 | settled+6, source_share_high_0.42, entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, post_stack_joined_exit_rows_lt_30, post_stack_suppressed_decisions_lt_30, diagnostic_suppressed_losers_present, settled_lt_30, simulated_share_gt_35pct |
| `soft_frontier_midprice_boundary_dual_exit_guard` | `post_midprice_shrink_birth_entry_half_midprice_boundary_or_reduce_p_hold80` | 24 | 21/3 | 80.00% | 574c | True | True | 41.7% | 5 | settled+6, source_share_high_0.42, entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, post_stack_joined_exit_rows_lt_30, post_stack_suppressed_decisions_lt_30, diagnostic_suppressed_losers_present, settled_lt_30, simulated_share_gt_35pct |
| `soft_frontier_midprice_boundary_dual_exit_guard` | `post_midprice_shrink_birth_entry_quarter_midprice_boundary_or_reduce_p_hold80` | 24 | 21/3 | 80.00% | 566c | True | True | 41.7% | 5 | settled+6, source_share_high_0.42, entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, post_stack_joined_exit_rows_lt_30, post_stack_suppressed_decisions_lt_30, diagnostic_suppressed_losers_present, settled_lt_30, simulated_share_gt_35pct |
| `soft_frontier_midprice_boundary_dual_exit_guard` | `post_midprice_shrink_birth_entry_control_no_shrink_or_reduce_p_hold80_no_midprice_boundary` | 24 | 21/3 | 80.00% | 564c | True | True | 41.7% | 5 | settled+6, source_share_high_0.42, entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, post_stack_joined_exit_rows_lt_30, post_stack_suppressed_decisions_lt_30, diagnostic_suppressed_losers_present, settled_lt_30, simulated_share_gt_35pct |
| `soft_frontier_midprice_boundary_dual_exit_guard` | `post_midprice_shrink_birth_entry_half_midprice_boundary_or_reduce_p_hold80_no_midprice_boundary` | 24 | 21/3 | 80.00% | 561c | True | True | 41.7% | 5 | settled+6, source_share_high_0.42, entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, post_stack_joined_exit_rows_lt_30, post_stack_suppressed_decisions_lt_30, diagnostic_suppressed_losers_present, settled_lt_30, simulated_share_gt_35pct |
| `soft_frontier_midprice_boundary_dual_exit_guard` | `post_midprice_shrink_birth_entry_quarter_midprice_boundary_or_reduce_p_hold80_no_midprice_boundary` | 24 | 21/3 | 80.00% | 560c | True | True | 41.7% | 5 | settled+6, source_share_high_0.42, entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, post_stack_joined_exit_rows_lt_30, post_stack_suppressed_decisions_lt_30, diagnostic_suppressed_losers_present, settled_lt_30, simulated_share_gt_35pct |
| `soft_frontier_midprice_boundary_clip_exit_stack` | `post_midprice_shrink_birth_entry_control_no_shrink_clip_separator_weighted_exit_stack` | 24 | 22/2 | 80.00% | 516c | True | True | 41.7% | 5 | settled+6, source_share_high_0.42, entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, post_stack_joined_exit_rows_lt_30, post_stack_clip_decisions_lt_30, diagnostic_suppressed_losers_present, settled_lt_30, simulated_share_gt_35pct |
| `soft_frontier_midprice_boundary_dual_exit_stack` | `post_midprice_shrink_birth_entry_control_no_shrink_clip_only` | 24 | 22/2 | 80.00% | 516c | True | True | 41.7% | 5 | settled+6, source_share_high_0.42, entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, post_stack_joined_exit_rows_lt_30, post_stack_suppressed_decisions_lt_30, diagnostic_suppressed_losers_present, settled_lt_30, simulated_share_gt_35pct |
| `soft_frontier_midprice_boundary_dual_exit_stack` | `post_midprice_shrink_birth_entry_control_no_shrink_book_gap_and_clip` | 24 | 22/2 | 80.00% | 516c | True | True | 41.7% | 5 | settled+6, source_share_high_0.42, entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, post_stack_joined_exit_rows_lt_30, post_stack_suppressed_decisions_lt_30, diagnostic_suppressed_losers_present, settled_lt_30, simulated_share_gt_35pct |

## Top Missing Gates

| scope | missing gate | rows |
|---|---|---:|
| `positive` | `simulated_share_gt_35pct` | 491 |
| `positive` | `settled_lt_30` | 241 |
| `positive` | `entry_reconstructed_share_gt_35pct` | 227 |
| `positive` | `row_reconstructed_share_gt_35pct` | 217 |
| `positive` | `full_loss_cushion_lt_3` | 200 |
| `positive` | `post_stack_joined_exit_rows_lt_30` | 195 |
| `positive` | `entry_lane_not_strict_combo_forward` | 156 |
| `positive` | `post_stack_weighted_exit_full_loss_cushion_lt_3` | 156 |
| `positive` | `source_share_high_0.39` | 130 |
| `positive` | `post_stack_suppressed_decisions_lt_30` | 120 |
| `positive` | `entry_full_loss_cushion_lt_3` | 118 |
| `positive` | `diagnostic_suppressed_losers_present` | 99 |
| `positive_target` | `simulated_share_gt_35pct` | 491 |
| `positive_target` | `entry_reconstructed_share_gt_35pct` | 227 |
| `positive_target` | `row_reconstructed_share_gt_35pct` | 211 |
| `positive_target` | `settled_lt_30` | 209 |
| `positive_target` | `post_stack_joined_exit_rows_lt_30` | 195 |
| `positive_target` | `entry_lane_not_strict_combo_forward` | 156 |
| `positive_target` | `post_stack_weighted_exit_full_loss_cushion_lt_3` | 156 |
| `positive_target` | `full_loss_cushion_lt_3` | 153 |
| `positive_target` | `source_share_high_0.39` | 129 |
| `positive_target` | `post_stack_suppressed_decisions_lt_30` | 120 |
| `positive_target` | `entry_full_loss_cushion_lt_3` | 110 |
| `positive_target` | `diagnostic_suppressed_losers_present` | 99 |
| `positive_strict` | `simulated_share_gt_35pct` | 182 |
| `positive_strict` | `row_reconstructed_share_gt_35pct` | 131 |
| `positive_strict` | `settled_lt_30` | 121 |
| `positive_strict` | `full_loss_cushion_lt_3` | 76 |
| `positive_strict` | `source_share_high_0.39` | 74 |
| `positive_strict` | `source_share_high_0.42` | 39 |
| `positive_strict` | `settled+6` | 39 |
| `positive_strict` | `entry_net_not_positive` | 39 |
| `positive_strict` | `entry_reconstructed_share_gt_35pct` | 39 |
| `positive_strict` | `entry_full_loss_cushion_lt_3` | 39 |
| `positive_strict` | `post_stack_joined_exit_rows_lt_30` | 39 |
| `positive_strict` | `cushion+3` | 38 |
