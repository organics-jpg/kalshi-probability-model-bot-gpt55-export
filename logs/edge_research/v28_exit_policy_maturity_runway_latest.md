# v28 Exit Policy Maturity Runway

Research-only maturity/runway view. No live bot changes or orders.

- Generated UTC: `2026-05-07T11:29:44.304272+00:00`
- Failure counts: `{'exit_policy_loss_control_harm': 4, 'strict_forward_denominator_missing': 5, 'strict_net_not_positive': 5, 'suppression_density_immature': 14}`

## Interpretation

- Research-only maturity view; no row here is a promotion decision.
- A strict exit watch still needs >=30 settled rows, >=30 suppressed decisions, positive net, non-negative loss-control cost, and at least 300c net for a three-full-loss cushion.
- Closest positive watch is book_gap_loss_guard: settled 27, suppressed 8, net 2.0c, delta 76.0c; it still needs 3 rows, 22 suppressions, and 298.0c cushion.
- Primary failure counts: {'exit_policy_loss_control_harm': 4, 'strict_forward_denominator_missing': 5, 'strict_net_not_positive': 5, 'suppression_density_immature': 14}.

## Watch Runway

| lane | status | failure | settled | suppressed | net c | delta c | rows need | suppressed need | cushion c need | blockers |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `book_gap_loss_guard` | `positive_but_under_sample` | `suppression_density_immature` | 27 | 8 | 2.00 | 76.00 | 3 | 22 | 298.00 | settled_lt_30, suppressed_decisions_lt_30 |
| `common_clock_strict_forward_v2` | `positive_but_under_sample` | `suppression_density_immature` | 18 | 5 | 44.00 | 66.00 | 12 | 25 | 256.00 | settled_lt_30, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| `book_gap_loss_guard_v3` | `positive_but_under_sample` | `suppression_density_immature` | 12 | 2 | 92.00 | 24.00 | 18 | 28 | 208.00 | settled_lt_30, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| `common_clock_strict_forward_v3` | `positive_but_under_sample` | `suppression_density_immature` | 11 | 3 | 106.00 | 42.00 | 19 | 27 | 194.00 | settled_lt_30, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| `exit_shallow_drawdown` | `positive_but_under_sample` | `suppression_density_immature` | 1 | 1 | 36.00 | 18.00 | 29 | 29 | 264.00 | settled_lt_30, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| `reduce_depth_gate` | `waiting_no_suppressed_exits` | `suppression_density_immature` | 21 | 0 | 116.00 | 0.00 | 9 | 30 | 184.00 | settled_lt_30, no_suppressed_exits_yet, delta_not_positive, full_loss_cushion_lt_3 |
| `midband_reduce_rescue` | `waiting_no_suppressed_exits` | `suppression_density_immature` | 9 | 0 | 84.00 | 0.00 | 21 | 30 | 216.00 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, full_loss_cushion_lt_3 |
| `exit_reduce_drift_guard` | `waiting_no_suppressed_exits` | `suppression_density_immature` | 7 | 0 | 60.00 | 0.00 | 23 | 30 | 240.00 | settled_lt_30, suppressed_decisions_lt_30, suppressed_delta_not_positive, full_loss_cushion_lt_3 |
| `matched_unchanged_loss_guard_watch` | `waiting_rule_has_not_fired` | `suppression_density_immature` | 2 | 0 | 56.00 | 0.00 | 28 | 30 | 244.00 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, full_loss_cushion_lt_3 |
| `common_clock_residual_child_exit70_79` | `waiting_no_suppressed_exits` | `suppression_density_immature` | 1 | 0 | 36.00 | 18.00 | 29 | 30 | 264.00 | settled_lt_30, child_suppressed_decisions_lt_30, child_delta_vs_parent_not_positive, full_loss_cushion_lt_3 |
| `exit_shallow_duration_lte52` | `waiting_no_suppressed_exits` | `suppression_density_immature` | 1 | 0 | 18.00 | 0.00 | 29 | 30 | 282.00 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, full_loss_cushion_lt_3 |
| `exit_clip_separator_watch` | `waiting_rule_has_not_fired` | `suppression_density_immature` | 1 | 0 | 0.00 | 0.00 | 29 | 30 | 300.00 | post_freeze_rows_lt_30, known_hold_delta_lt_300c |
| `soft_frontier_midprice_delayed_recheck_exit` | `waiting_no_post_freeze_rows` | `strict_forward_denominator_missing` | 0 | 0 | 0.00 | 0.00 | 30 | 30 | 300.00 | joined_rows_lt_30, suppressed_decisions_lt_30, weighted_net_not_positive, delta_not_positive, full_loss_cushion_lt_3 |
| `soft_frontier_midprice_delayed_recheck_rescue` | `waiting_no_post_freeze_rows` | `strict_forward_denominator_missing` | 0 | 0 | 0.00 | 0.00 | 30 | 30 | 300.00 | joined_rows_lt_30, suppressed_decisions_lt_30, weighted_net_not_positive, delta_not_positive, full_loss_cushion_lt_3 |
| `feature_gate_value_exit` | `waiting_no_post_freeze_rows` | `strict_forward_denominator_missing` | 0 | 0 | 0.00 | 0.00 | 30 | 30 | 300.00 | settled_lt_30, net_not_positive, full_loss_cushion_lt_3, selected_side_live_overlap_only, hold_to_settlement_assumption, not_live_bot_logic |
| `feature_gate_exit_bid_suppression` | `waiting_no_post_freeze_rows` | `strict_forward_denominator_missing` | 0 | 0 | 0.00 | 0.00 | 30 | 30 | 300.00 | settled_lt_30, suppressed_decisions_lt_30, net_not_positive, delta_not_positive, full_loss_cushion_lt_3 |
| `feature_gate_exit_bid_delayed_recheck` | `waiting_no_post_freeze_rows` | `strict_forward_denominator_missing` | 0 | 0 | 0.00 | 0.00 | 30 | 30 | 300.00 | settled_lt_30, suppressed_decisions_lt_30, net_not_positive, delta_not_positive, full_loss_cushion_lt_3 |
| `book_gap_suppression` | `blocked_loss_control_cost` | `exit_policy_loss_control_harm` | 55 | 24 | -180.00 | -165.00 | 0 | 6 | 480.00 | delta_not_positive, suppressed_loss_control_cost_negative |
| `dual_exit_book_gap_else_reduce` | `blocked_loss_control_cost` | `exit_policy_loss_control_harm` | 25 | 8 | -350.00 | -242.00 | 5 | 22 | 650.00 | settled_lt_30, delta_not_positive, net_not_positive, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| `reduce_side_geometry` | `blocked_net_not_positive` | `strict_net_not_positive` | 21 | 0 | -114.00 | 0.00 | 9 | 30 | 414.00 | settled_lt_30, delta_not_positive |
| `common_clock_strict_forward_v1` | `blocked_net_not_positive` | `strict_net_not_positive` | 19 | 5 | -42.00 | 66.00 | 11 | 25 | 342.00 | settled_lt_30, suppressed_decisions_lt_30, net_not_positive, full_loss_cushion_lt_3 |
| `book_gap_value_only` | `blocked_loss_control_cost` | `exit_policy_loss_control_harm` | 18 | 4 | -306.00 | -134.00 | 12 | 26 | 606.00 | settled_lt_30, delta_not_positive, net_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| `value_reduce_depth_composite` | `blocked_net_not_positive` | `strict_net_not_positive` | 17 | 0 | -110.00 | 0.00 | 13 | 30 | 410.00 | settled_lt_30, delta_not_positive, net_not_positive, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| `book_gap_loss_guard_v2` | `blocked_net_not_positive` | `strict_net_not_positive` | 10 | 0 | -10.00 | 0.00 | 20 | 30 | 310.00 | settled_lt_30, delta_not_positive, net_not_positive, suppressed_decisions_lt_30 |
| `reduce_observable_loss_control` | `blocked_net_not_positive` | `strict_net_not_positive` | 10 | 0 | -158.00 | 0.00 | 20 | 30 | 458.00 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, full_loss_cushion_lt_3 |
| `reduce_geometry_relaxed` | `blocked_loss_control_cost` | `exit_policy_loss_control_harm` | 6 | 1 | -106.00 | -120.00 | 24 | 29 | 406.00 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, full_loss_cushion_lt_3 |
| `reduce_loss_control_refinement` | `waiting_no_suppressed_exits` | `suppression_density_immature` | 21 | 0 | 42.00 | 0.00 | 9 | 30 | 258.00 | settled_lt_30, delta_not_positive, full_loss_cushion_lt_3 |
| `value_exit_feature_side_guard` | `not_positive_or_under_sample` | `suppression_density_immature` | 1 | 1 | 18.00 | 0.00 | 29 | 29 | 282.00 | settled_lt_30, full_loss_cushion_lt_3, exit_overlap_only, not_live_bot_logic |
