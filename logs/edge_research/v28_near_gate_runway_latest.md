# v28 Near-Gate Runway

Research-only. No live bot logic changes, no orders, no process control.

- Generated UTC: `2026-05-07T13:36:13.284878+00:00`
- Live baseline: `925.00c`
- Rows / positive / target-positive / strict-target-positive / live-ready: `1015/802/463/122/0`

## Interpretation

- Research-only near-gate audit; no live bot changes or orders.
- Live baseline for runway math is 925c.
- Live-ready rows found: 0.
- Closest strict target-positive row is feature_gate_coverage_size_shrink / post_feature_freeze_bridge_repair_low_absd_quarter_else_half with net 369.0c, settled 45, coverage 75.40983606557377%, source share 0.41304347826086957, blockers ['row_reconstructed_share_gt_35pct', 'source_share_gt_35pct', 'does_not_beat_refreshed_live_baseline', 'live_ready_false'].
- Closest target-positive row overall is dual_lane_overlap_union / top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_quarter + post_penalty_birth_bridge_cheap_penalty025_rank_only; diagnostic/prefreeze rows still need their own strict birth if not strict_forward.
- Most common blockers among positive target-coverage rows: live_ready_false=463, source_share_gt_35pct=411, does_not_beat_refreshed_live_baseline=396, not_strict_forward=341, full_loss_cushion_lt_3=204.

## Closest Strict Target-Positive

| rank | gate | policy | settled | W/L | coverage | net | delta live | source | cushion | sample need | cov need | clean source need | net to live | blockers |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_low_absd_quarter_else_half` | 45 | 37/8 | 75.41% | 369.00 | -556.00 | 0.41 | 3 | 0 | 0 | 9 | 557.00 | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |
| 2 | `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_low_absd_quarter_else_half` | 45 | 37/8 | 75.41% | 369.00 | -556.00 | 0.41 | 3 | 0 | 0 | 9 | 557.00 | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |
| 3 | `feature_gate_observable_selection_mix` | `post_feature_freeze_bridge_same_market_repair_rule_raw_edge` | 45 | 37/8 | 75.41% | 369.00 | -556.00 | 0.41 | 3 | 0 | 0 | 9 | 557.00 | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |
| 4 | `feature_gate_observable_selection_mix` | `post_feature_freeze_entry_same_market_repair_rule_raw_edge` | 45 | 37/8 | 75.41% | 369.00 | -556.00 | 0.41 | 3 | 0 | 0 | 9 | 557.00 | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |
| 5 | `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_eighth` | 45 | 37/8 | 75.41% | 364.12 | -560.88 | 0.41 | 3 | 0 | 0 | 9 | 561.88 | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |
| 6 | `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_eighth` | 45 | 37/8 | 75.41% | 364.12 | -560.88 | 0.41 | 3 | 0 | 0 | 9 | 561.88 | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |
| 7 | `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_quarter` | 45 | 37/8 | 75.41% | 355.25 | -569.75 | 0.41 | 3 | 0 | 0 | 9 | 570.75 | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |
| 8 | `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_quarter` | 45 | 37/8 | 75.41% | 355.25 | -569.75 | 0.41 | 3 | 0 | 0 | 9 | 570.75 | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |
| 9 | `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_half` | 45 | 37/8 | 75.41% | 337.50 | -587.50 | 0.41 | 3 | 0 | 0 | 9 | 588.50 | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |
| 10 | `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_half` | 45 | 37/8 | 75.41% | 337.50 | -587.50 | 0.41 | 3 | 0 | 0 | 9 | 588.50 | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |
| 11 | `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_midcheap_quarter_else_half` | 45 | 37/8 | 75.41% | 335.00 | -590.00 | 0.41 | 3 | 0 | 0 | 9 | 591.00 | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |
| 12 | `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_midcheap_quarter_else_half` | 45 | 37/8 | 75.41% | 335.00 | -590.00 | 0.41 | 3 | 0 | 0 | 9 | 591.00 | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |
| 13 | `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_absd_squared` | 45 | 37/8 | 75.41% | 332.54 | -592.46 | 0.41 | 3 | 0 | 0 | 9 | 593.46 | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |
| 14 | `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_absd_squared` | 45 | 37/8 | 75.41% | 332.54 | -592.46 | 0.41 | 3 | 0 | 0 | 9 | 593.46 | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |
| 15 | `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_absd_recross_scaled` | 45 | 37/8 | 75.41% | 318.36 | -606.64 | 0.41 | 3 | 0 | 0 | 9 | 607.64 | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |
| 16 | `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_absd_recross_scaled` | 45 | 37/8 | 75.41% | 318.36 | -606.64 | 0.41 | 3 | 0 | 0 | 9 | 607.64 | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |
| 17 | `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_low_absd_recross_eighth_else_half` | 45 | 37/8 | 75.41% | 312.00 | -613.00 | 0.41 | 3 | 0 | 0 | 9 | 614.00 | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |
| 18 | `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_low_absd_recross_eighth_else_half` | 45 | 37/8 | 75.41% | 312.00 | -613.00 | 0.41 | 3 | 0 | 0 | 9 | 614.00 | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |
| 19 | `feature_gate_observable_selection_mix` | `post_feature_freeze_bridge_same_market_repair_rule_edge_absd_cheap_penalty` | 45 | 37/8 | 75.41% | 343.00 | -582.00 | 0.48 | 3 | 0 | 0 | 17 | 583.00 | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |
| 20 | `feature_gate_observable_selection_mix` | `post_feature_freeze_entry_same_market_repair_rule_edge_absd_cheap_penalty` | 45 | 37/8 | 75.41% | 343.00 | -582.00 | 0.48 | 3 | 0 | 0 | 17 | 583.00 | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline, live_ready_false |

## Closest Target-Positive Overall

| rank | gate | policy | settled | W/L | coverage | net | delta live | source | cushion | sample need | cov need | clean source need | net to live | blockers |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_quarter + post_penalty_birth_bridge_cheap_penalty025_rank_only` | 76 | 64/11 | 86.36% | 2072.50 | 1147.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |
| 2 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_quarter + post_penalty_birth_bridge_cheap_penalty050_rank_only` | 76 | 64/11 | 86.36% | 2072.50 | 1147.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |
| 3 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_quarter + post_penalty_birth_bridge_cheap_penalty100_rank_only` | 76 | 64/11 | 86.36% | 2072.50 | 1147.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |
| 4 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_quarter + post_penalty_birth_entry_cheap_penalty025_rank_only` | 76 | 64/11 | 86.36% | 2072.50 | 1147.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |
| 5 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_quarter + post_penalty_birth_entry_cheap_penalty050_rank_only` | 76 | 64/11 | 86.36% | 2072.50 | 1147.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |
| 6 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_quarter + post_penalty_birth_entry_cheap_penalty100_rank_only` | 76 | 64/11 | 86.36% | 2072.50 | 1147.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |
| 7 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_quarter + post_penalty_birth_bridge_cheap_penalty025_rank_only` | 76 | 64/11 | 86.36% | 2072.50 | 1147.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |
| 8 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_quarter + post_penalty_birth_bridge_cheap_penalty050_rank_only` | 76 | 64/11 | 86.36% | 2072.50 | 1147.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |
| 9 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_quarter + post_penalty_birth_bridge_cheap_penalty100_rank_only` | 76 | 64/11 | 86.36% | 2072.50 | 1147.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |
| 10 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_quarter + post_penalty_birth_entry_cheap_penalty025_rank_only` | 76 | 64/11 | 86.36% | 2072.50 | 1147.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |
| 11 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_quarter + post_penalty_birth_entry_cheap_penalty050_rank_only` | 76 | 64/11 | 86.36% | 2072.50 | 1147.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |
| 12 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_quarter + post_penalty_birth_entry_cheap_penalty100_rank_only` | 76 | 64/11 | 86.36% | 2072.50 | 1147.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |
| 13 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_half + post_penalty_birth_entry_cheap_penalty025_rank_only` | 76 | 64/11 | 86.36% | 2055.50 | 1130.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |
| 14 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_half + post_penalty_birth_entry_cheap_penalty050_rank_only` | 76 | 64/11 | 86.36% | 2055.50 | 1130.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |
| 15 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_half + post_penalty_birth_bridge_cheap_penalty025_rank_only` | 76 | 64/11 | 86.36% | 2055.50 | 1130.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |
| 16 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_half + post_penalty_birth_bridge_cheap_penalty050_rank_only` | 76 | 64/11 | 86.36% | 2055.50 | 1130.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |
| 17 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_half + post_penalty_birth_bridge_cheap_penalty100_rank_only` | 76 | 64/11 | 86.36% | 2055.50 | 1130.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |
| 18 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_half + post_penalty_birth_entry_cheap_penalty025_rank_only` | 76 | 64/11 | 86.36% | 2055.50 | 1130.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |
| 19 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_half + post_penalty_birth_entry_cheap_penalty050_rank_only` | 76 | 64/11 | 86.36% | 2055.50 | 1130.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |
| 20 | `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_half + post_penalty_birth_entry_cheap_penalty100_rank_only` | 76 | 64/11 | 86.36% | 2055.50 | 1130.50 | 0.34 | 20 | 0 | 0 | 0 | 0.00 | needs_own_frozen_forward_birth, live_ready_false, not_strict_forward |

## Blocker Counts

- `live_ready_false`: `463`
- `source_share_gt_35pct`: `411`
- `does_not_beat_refreshed_live_baseline`: `396`
- `not_strict_forward`: `341`
- `full_loss_cushion_lt_3`: `204`
- `row_reconstructed_share_gt_35pct`: `194`
- `entry_lane_not_strict_combo_forward`: `153`
- `entry_reconstructed_share_gt_35pct`: `153`
- `post_stack_joined_exit_rows_lt_30`: `153`
- `post_stack_weighted_exit_full_loss_cushion_lt_3`: `153`
- `settled_lt_30`: `140`
- `post_stack_suppressed_decisions_lt_30`: `96`
- `diagnostic_suppressed_losers_present`: `69`
- `weighted_full_loss_cushion_lt_3`: `62`
- `exposure_reconstructed_share_gt_35pct`: `60`
- `reconstructed_share_gt_35pct`: `56`
- `diagnostic_prefreeze`: `52`
- `entry_full_loss_cushion_lt_3`: `37`
- `diagnostic_only_prefreeze`: `33`
- `needs_own_frozen_forward_birth`: `32`
