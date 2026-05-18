# v28 Exit Dashboard Coverage Audit

Research-only reporting coverage audit. No live bot changes or orders.

- Generated UTC: `2026-05-07T11:29:25.021402+00:00`
- Tracker exit-like gates: `36`
- Dashboard lanes: `28`
- Dashboard status counts: `{'dashboard_covered': 25, 'intentionally_excluded': 11}`
- Registry active missing rows: `0`

## Interpretation

- Research-only dashboard coverage audit; it checks reporting visibility, not candidate quality.
- Tracker has 36 exit-like gates; dashboard has 28 lanes.
- Dashboard status counts: {'dashboard_covered': 25, 'intentionally_excluded': 11}.
- Registry active missing rows: 0.
- No active exit/state tracker gate is missing dashboard coverage or an explicit exclusion.

## Gates Needing Dashboard Review

| gate | status | rows | post rows | max settled | max net c | sample policies |
|---|---|---:|---:|---:|---:|---|
| none | n/a | 0 | 0 | 0 | n/a | n/a |

## Covered Gates

- `dual_exit_book_gap_else_reduce`
- `exit_book_gap_loss_guard`
- `exit_book_gap_loss_guard_v2`
- `exit_book_gap_loss_guard_v3`
- `exit_book_gap_suppression`
- `exit_book_gap_value_only`
- `exit_clip_separator_watch`
- `exit_common_clock_residual_child_watch`
- `exit_midband_reduce_rescue`
- `exit_reduce_depth_gate`
- `exit_reduce_drift_guard`
- `exit_reduce_geometry_relaxed_watch`
- `exit_reduce_geometry_suppression`
- `exit_reduce_loss_control_refinement`
- `exit_reduce_observable_loss_control`
- `exit_shallow_drawdown`
- `exit_shallow_duration_lte52`
- `exit_value_reduce_depth_composite`
- `feature_gate_exit_bid_delayed_recheck`
- `feature_gate_exit_bid_suppression_watch`
- `frozen_feature_gate_value_exit_watch`
- `frozen_value_exit_feature_side_guard`
- `matched_unchanged_loss_guard_watch`
- `soft_frontier_midprice_delayed_recheck_exit`
- `soft_frontier_midprice_delayed_recheck_rescue`

## Intentional Exclusions

- `exit_reduce_suppression`: legacy_blanket_reduce_watch_superseded_by_guarded_children
- `exit_reduce_yes_suppression`: legacy_side_specific_reduce_watch_not_current_dashboard_child
- `feature_gate_book_gap_exit_stack`: entry_exit_stack_tracked_in_candidate_table_not_exit_dashboard
- `feature_gate_size_shrink_delayed_recheck_exit`: coverage_size_entry_overlay_tracked_with_feature_gate_family
- `feature_gate_size_shrink_delayed_recheck_rescue`: coverage_size_entry_overlay_tracked_with_feature_gate_family
- `feature_gate_size_shrink_exit_overlay`: coverage_size_entry_overlay_tracked_with_feature_gate_family
- `feature_gate_soft_frontier_exit_stack`: entry_exit_stack_tracked_in_candidate_table_not_exit_dashboard
- `soft_frontier_midprice_boundary_clip_exit_stack`: entry_exit_stack_tracked_in_candidate_table_not_exit_dashboard
- `soft_frontier_midprice_boundary_dual_exit_guard`: entry_exit_stack_tracked_in_candidate_table_not_exit_dashboard
- `soft_frontier_midprice_boundary_dual_exit_stack`: entry_exit_stack_tracked_in_candidate_table_not_exit_dashboard
- `soft_frontier_midprice_boundary_exit_stack`: entry_exit_stack_tracked_in_candidate_table_not_exit_dashboard

## Dashboard Lanes Without Gate Map

- none
