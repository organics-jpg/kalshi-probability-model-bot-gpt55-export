# v28 Live-Ready Bottleneck Map

Research-only. No live bot logic changes, no orders, no process control.

- Generated UTC: `2026-05-07T13:47:06.385386+00:00`
- Live baseline: `925.0c`
- Controlled gate decision: `no_live_test`
- Broad/sidecar eligible: `0/0`

## Counts

- Rows / positive / target-positive / strict-target-positive / live-ready: `1015/801/464/122/0`
- Strict sidecar-positive sample/source/cushion lanes / beating live: `6/0`

## Main Bottlenecks

### Target-Positive Rows

- `source_quality`: `419`
- `live_baseline_gap`: `397`
- `frozen_forward_evidence`: `342`
- `fragility`: `273`
- `sample_or_exit_density`: `200`
- `coverage`: `2`

### Strict Target-Positive Rows

- `live_baseline_gap`: `122`
- `source_quality`: `122`
- `fragility`: `94`
- `sample_or_exit_density`: `52`

## Recommended Work Queue

| priority | branch | bottleneck | work | ready when |
|---:|---|---|---|---|
| 1 | `dual_lane_overlap_union` | `frozen_forward_evidence` | Keep the own-freeze watch alive and score only rows after its birth. Do not tune the old diagnostic row into live status. | Own-freeze union has >=30 settled, 75-90% coverage, <=35% source share, positive PnL, cushion >=3, and net above refreshed live baseline. |
| 2 | `feature_gate_coverage_size_shrink` | `source_quality_plus_live_baseline_gap` | Stop widening repair rows. Focus on fresh approved middle-distance rows or observable confirmation that can replace low-abs reconstructed repair filler. | A child born from this rule has <=35% row-source share, still covers >=75%, and closes the live-baseline gap without post-hoc source labels. |
| 3 | `boundary_clock_feature_gate_continuous_penalty` | `live_baseline_gap` | Do not mix it into size-shrink; cached union check showed only three non-overlap rows, -9c added net, and worse source share. Let it accumulate or find a pre-frozen complementary strict component that adds clean positive non-overlap rows. | A strict sidecar row clears positive PnL, >=30 settled, <=35% source share, cushion >=3, and beats or materially improves the refreshed live baseline under the controlled gate. |
| 4 | `exit_policy_children` | `sample_or_exit_density` | Track post-birth joined-exit density and adverse-path safety. Promote no exit child until the suppression population is large enough. | >=30 joined rows, >=30 suppressed decisions where applicable, positive delta/net, cushion >=3, no harmful suppression cluster. |
| 5 | `top_component_mix_portfolio` | `child_birth_evidence` | Keep child watches separated; do not merge parent diagnostic PnL with child rules as if it were frozen evidence. | Each child clears sample/source/coverage/cushion/live-baseline gates from its own freeze. |

## Closest Overall Target-Positive

| gate | policy | settled | W/L | coverage | net | delta live | source | cushion | strict | bottlenecks | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_quarter + post_penalty_birth_entry_cheap_penalty025_rank_only` | 76 | 64/11 | 86.36% | 2072.5c | 1147.5c | 34.2% | 20 | `False` | frozen_forward_evidence | needs_own_frozen_forward_birth, not_strict_forward |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_quarter + post_penalty_birth_entry_cheap_penalty050_rank_only` | 76 | 64/11 | 86.36% | 2072.5c | 1147.5c | 34.2% | 20 | `False` | frozen_forward_evidence | needs_own_frozen_forward_birth, not_strict_forward |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_quarter + post_penalty_birth_entry_cheap_penalty100_rank_only` | 76 | 64/11 | 86.36% | 2072.5c | 1147.5c | 34.2% | 20 | `False` | frozen_forward_evidence | needs_own_frozen_forward_birth, not_strict_forward |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_quarter + post_penalty_birth_bridge_cheap_penalty025_rank_only` | 76 | 64/11 | 86.36% | 2072.5c | 1147.5c | 34.2% | 20 | `False` | frozen_forward_evidence | needs_own_frozen_forward_birth, not_strict_forward |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_quarter + post_penalty_birth_bridge_cheap_penalty050_rank_only` | 76 | 64/11 | 86.36% | 2072.5c | 1147.5c | 34.2% | 20 | `False` | frozen_forward_evidence | needs_own_frozen_forward_birth, not_strict_forward |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_quarter + post_penalty_birth_bridge_cheap_penalty100_rank_only` | 76 | 64/11 | 86.36% | 2072.5c | 1147.5c | 34.2% | 20 | `False` | frozen_forward_evidence | needs_own_frozen_forward_birth, not_strict_forward |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_quarter + post_penalty_birth_entry_cheap_penalty025_rank_only` | 76 | 64/11 | 86.36% | 2072.5c | 1147.5c | 34.2% | 20 | `False` | frozen_forward_evidence | needs_own_frozen_forward_birth, not_strict_forward |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_quarter + post_penalty_birth_entry_cheap_penalty050_rank_only` | 76 | 64/11 | 86.36% | 2072.5c | 1147.5c | 34.2% | 20 | `False` | frozen_forward_evidence | needs_own_frozen_forward_birth, not_strict_forward |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_quarter + post_penalty_birth_entry_cheap_penalty100_rank_only` | 76 | 64/11 | 86.36% | 2072.5c | 1147.5c | 34.2% | 20 | `False` | frozen_forward_evidence | needs_own_frozen_forward_birth, not_strict_forward |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_quarter + post_penalty_birth_bridge_cheap_penalty025_rank_only` | 76 | 64/11 | 86.36% | 2072.5c | 1147.5c | 34.2% | 20 | `False` | frozen_forward_evidence | needs_own_frozen_forward_birth, not_strict_forward |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_quarter + post_penalty_birth_bridge_cheap_penalty050_rank_only` | 76 | 64/11 | 86.36% | 2072.5c | 1147.5c | 34.2% | 20 | `False` | frozen_forward_evidence | needs_own_frozen_forward_birth, not_strict_forward |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_quarter + post_penalty_birth_bridge_cheap_penalty100_rank_only` | 76 | 64/11 | 86.36% | 2072.5c | 1147.5c | 34.2% | 20 | `False` | frozen_forward_evidence | needs_own_frozen_forward_birth, not_strict_forward |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_half + post_penalty_birth_entry_cheap_penalty025_rank_only` | 76 | 64/11 | 86.36% | 2055.5c | 1130.5c | 34.2% | 20 | `False` | frozen_forward_evidence | needs_own_frozen_forward_birth, not_strict_forward |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_half + post_penalty_birth_entry_cheap_penalty050_rank_only` | 76 | 64/11 | 86.36% | 2055.5c | 1130.5c | 34.2% | 20 | `False` | frozen_forward_evidence | needs_own_frozen_forward_birth, not_strict_forward |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_half + post_penalty_birth_entry_cheap_penalty100_rank_only` | 76 | 64/11 | 86.36% | 2055.5c | 1130.5c | 34.2% | 20 | `False` | frozen_forward_evidence | needs_own_frozen_forward_birth, not_strict_forward |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_half + post_penalty_birth_bridge_cheap_penalty025_rank_only` | 76 | 64/11 | 86.36% | 2055.5c | 1130.5c | 34.2% | 20 | `False` | frozen_forward_evidence | needs_own_frozen_forward_birth, not_strict_forward |

| gate | policy | sample need | coverage need | clean source need | cents to live | cushion cents need |
|---|---|---:|---:|---:|---:|---:|
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_quarter + post_penalty_birth_entry_cheap_penalty025_rank_only` | 0 | 0 | 0 | 0.0c | 0.0c |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_quarter + post_penalty_birth_entry_cheap_penalty050_rank_only` | 0 | 0 | 0 | 0.0c | 0.0c |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_quarter + post_penalty_birth_entry_cheap_penalty100_rank_only` | 0 | 0 | 0 | 0.0c | 0.0c |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_quarter + post_penalty_birth_bridge_cheap_penalty025_rank_only` | 0 | 0 | 0 | 0.0c | 0.0c |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_quarter + post_penalty_birth_bridge_cheap_penalty050_rank_only` | 0 | 0 | 0 | 0.0c | 0.0c |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_quarter + post_penalty_birth_bridge_cheap_penalty100_rank_only` | 0 | 0 | 0 | 0.0c | 0.0c |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_quarter + post_penalty_birth_entry_cheap_penalty025_rank_only` | 0 | 0 | 0 | 0.0c | 0.0c |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_quarter + post_penalty_birth_entry_cheap_penalty050_rank_only` | 0 | 0 | 0 | 0.0c | 0.0c |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_quarter + post_penalty_birth_entry_cheap_penalty100_rank_only` | 0 | 0 | 0 | 0.0c | 0.0c |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_quarter + post_penalty_birth_bridge_cheap_penalty025_rank_only` | 0 | 0 | 0 | 0.0c | 0.0c |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_quarter + post_penalty_birth_bridge_cheap_penalty050_rank_only` | 0 | 0 | 0 | 0.0c | 0.0c |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_mid_confidence_parent_fill_quarter + post_penalty_birth_bridge_cheap_penalty100_rank_only` | 0 | 0 | 0 | 0.0c | 0.0c |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_half + post_penalty_birth_entry_cheap_penalty025_rank_only` | 0 | 0 | 0 | 0.0c | 0.0c |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_half + post_penalty_birth_entry_cheap_penalty050_rank_only` | 0 | 0 | 0 | 0.0c | 0.0c |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_half + post_penalty_birth_entry_cheap_penalty100_rank_only` | 0 | 0 | 0 | 0.0c | 0.0c |
| `dual_lane_overlap_union` | `top_component_parent_fill_repair_child:diagnostic_observable_mid_confidence_parent_fill_half + post_penalty_birth_bridge_cheap_penalty025_rank_only` | 0 | 0 | 0 | 0.0c | 0.0c |

## Closest Strict Target-Positive

| gate | policy | settled | W/L | coverage | net | delta live | source | cushion | strict | bottlenecks | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_low_absd_quarter_else_half` | 45 | 37/8 | 75.41% | 369.0c | -556.0c | 41.3% | 3 | `True` | source_quality, live_baseline_gap | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_low_absd_quarter_else_half` | 45 | 37/8 | 75.41% | 369.0c | -556.0c | 41.3% | 3 | `True` | source_quality, live_baseline_gap | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `feature_gate_observable_selection_mix` | `post_feature_freeze_entry_same_market_repair_rule_raw_edge` | 45 | 37/8 | 75.41% | 369.0c | -556.0c | 41.3% | 3 | `True` | source_quality, live_baseline_gap | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `feature_gate_observable_selection_mix` | `post_feature_freeze_bridge_same_market_repair_rule_raw_edge` | 45 | 37/8 | 75.41% | 369.0c | -556.0c | 41.3% | 3 | `True` | source_quality, live_baseline_gap | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_eighth` | 45 | 37/8 | 75.41% | 364.1c | -560.9c | 41.3% | 3 | `True` | source_quality, live_baseline_gap | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_eighth` | 45 | 37/8 | 75.41% | 364.1c | -560.9c | 41.3% | 3 | `True` | source_quality, live_baseline_gap | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_quarter` | 45 | 37/8 | 75.41% | 355.2c | -569.8c | 41.3% | 3 | `True` | source_quality, live_baseline_gap | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_quarter` | 45 | 37/8 | 75.41% | 355.2c | -569.8c | 41.3% | 3 | `True` | source_quality, live_baseline_gap | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_half` | 45 | 37/8 | 75.41% | 337.5c | -587.5c | 41.3% | 3 | `True` | source_quality, live_baseline_gap | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_half` | 45 | 37/8 | 75.41% | 337.5c | -587.5c | 41.3% | 3 | `True` | source_quality, live_baseline_gap | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_midcheap_quarter_else_half` | 45 | 37/8 | 75.41% | 335.0c | -590.0c | 41.3% | 3 | `True` | source_quality, live_baseline_gap | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_midcheap_quarter_else_half` | 45 | 37/8 | 75.41% | 335.0c | -590.0c | 41.3% | 3 | `True` | source_quality, live_baseline_gap | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_absd_squared` | 45 | 37/8 | 75.41% | 332.5c | -592.5c | 41.3% | 3 | `True` | source_quality, live_baseline_gap | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_absd_squared` | 45 | 37/8 | 75.41% | 332.5c | -592.5c | 41.3% | 3 | `True` | source_quality, live_baseline_gap | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_absd_recross_scaled` | 45 | 37/8 | 75.41% | 318.4c | -606.6c | 41.3% | 3 | `True` | source_quality, live_baseline_gap | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_absd_recross_scaled` | 45 | 37/8 | 75.41% | 318.4c | -606.6c | 41.3% | 3 | `True` | source_quality, live_baseline_gap | row_reconstructed_share_gt_35pct, source_share_gt_35pct, does_not_beat_refreshed_live_baseline |

| gate | policy | sample need | coverage need | clean source need | cents to live | cushion cents need |
|---|---|---:|---:|---:|---:|---:|
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_low_absd_quarter_else_half` | 0 | 0 | 9 | 557.0c | 0.0c |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_low_absd_quarter_else_half` | 0 | 0 | 9 | 557.0c | 0.0c |
| `feature_gate_observable_selection_mix` | `post_feature_freeze_entry_same_market_repair_rule_raw_edge` | 0 | 0 | 9 | 557.0c | 0.0c |
| `feature_gate_observable_selection_mix` | `post_feature_freeze_bridge_same_market_repair_rule_raw_edge` | 0 | 0 | 9 | 557.0c | 0.0c |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_eighth` | 0 | 0 | 9 | 561.9c | 0.0c |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_eighth` | 0 | 0 | 9 | 561.9c | 0.0c |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_quarter` | 0 | 0 | 9 | 570.8c | 0.0c |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_quarter` | 0 | 0 | 9 | 570.8c | 0.0c |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_half` | 0 | 0 | 9 | 588.5c | 0.0c |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_half` | 0 | 0 | 9 | 588.5c | 0.0c |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_midcheap_quarter_else_half` | 0 | 0 | 9 | 591.0c | 0.0c |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_midcheap_quarter_else_half` | 0 | 0 | 9 | 591.0c | 0.0c |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_absd_squared` | 0 | 0 | 9 | 593.5c | 0.0c |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_absd_squared` | 0 | 0 | 9 | 593.5c | 0.0c |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_entry_repair_absd_recross_scaled` | 0 | 0 | 9 | 607.6c | 0.0c |
| `feature_gate_coverage_size_shrink` | `post_feature_freeze_bridge_repair_absd_recross_scaled` | 0 | 0 | 9 | 607.6c | 0.0c |

## Closest Strict Sidecar-Positive

| gate | policy | settled | W/L | coverage | net | delta live | source | cushion | strict | bottlenecks | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_entry_cheap_penalty025_rank_only` | 34 | 27/7 | 61.40% | 391.0c | -534.0c | 22.9% | 3 | `True` | live_baseline_gap, coverage | coverage_too_low, coverage_lt_75pct, does_not_beat_refreshed_live_baseline |
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_entry_cheap_penalty050_rank_only` | 34 | 27/7 | 61.40% | 391.0c | -534.0c | 22.9% | 3 | `True` | live_baseline_gap, coverage | coverage_too_low, coverage_lt_75pct, does_not_beat_refreshed_live_baseline |
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_entry_cheap_penalty100_rank_only` | 34 | 27/7 | 61.40% | 391.0c | -534.0c | 22.9% | 3 | `True` | live_baseline_gap, coverage | coverage_too_low, coverage_lt_75pct, does_not_beat_refreshed_live_baseline |
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_bridge_cheap_penalty025_rank_only` | 34 | 27/7 | 61.40% | 391.0c | -534.0c | 22.9% | 3 | `True` | live_baseline_gap, coverage | coverage_too_low, coverage_lt_75pct, does_not_beat_refreshed_live_baseline |
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_bridge_cheap_penalty050_rank_only` | 34 | 27/7 | 61.40% | 391.0c | -534.0c | 22.9% | 3 | `True` | live_baseline_gap, coverage | coverage_too_low, coverage_lt_75pct, does_not_beat_refreshed_live_baseline |
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_bridge_cheap_penalty100_rank_only` | 34 | 27/7 | 61.40% | 391.0c | -534.0c | 22.9% | 3 | `True` | live_baseline_gap, coverage | coverage_too_low, coverage_lt_75pct, does_not_beat_refreshed_live_baseline |

| gate | policy | sample need | coverage need | clean source need | cents to live | cushion cents need |
|---|---|---:|---:|---:|---:|---:|
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_entry_cheap_penalty025_rank_only` | 0 | 8 | 0 | 535.0c | 0.0c |
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_entry_cheap_penalty050_rank_only` | 0 | 8 | 0 | 535.0c | 0.0c |
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_entry_cheap_penalty100_rank_only` | 0 | 8 | 0 | 535.0c | 0.0c |
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_bridge_cheap_penalty025_rank_only` | 0 | 8 | 0 | 535.0c | 0.0c |
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_bridge_cheap_penalty050_rank_only` | 0 | 8 | 0 | 535.0c | 0.0c |
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_bridge_cheap_penalty100_rank_only` | 0 | 8 | 0 | 535.0c | 0.0c |

## Feature-Gate Source Feasibility

| lane | denominator | approved markets | 75% feasible under source gate | min recon share at 75% | max source-clean coverage |
|---|---:|---:|---|---:|---:|
| `post_feature_freeze_entry` | 66 | 32 | `False` | 36.0% | 74.24% |
| `post_feature_freeze_bridge` | 66 | 32 | `False` | 36.0% | 74.24% |
