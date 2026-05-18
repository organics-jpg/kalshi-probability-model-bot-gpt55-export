# v28 Exit Watch Denominator Audit

Research-only denominator audit. No live bot changes or orders.

- Generated UTC: `2026-05-07T11:29:38.670356+00:00`
- Base scored exit rows total: `128`
- Latest base exit UTC: `2026-05-07T10:31:23.619687+00:00`
- Denominator read counts: `{'collecting_blocked': 5, 'collecting_positive_but_immature': 5, 'collecting_watch_only': 1, 'denominator_collecting_rule_not_firing': 12, 'watch_specific_overlap_not_collecting': 5}`

## Interpretation

- Research-only denominator audit; it does not score or change a rule.
- Base scored exit rows currently total 128.
- Latest generic base exit timestamp is 2026-05-07T10:31:23.619687+00:00.
- Too-new zero-row watches: [].
- Watch-specific overlap waits: ['soft_frontier_midprice_delayed_recheck_exit', 'soft_frontier_midprice_delayed_recheck_rescue', 'feature_gate_value_exit', 'feature_gate_exit_bid_suppression', 'feature_gate_exit_bid_delayed_recheck'].
- Potential join/filter denominator issues: [].
- Collecting but no rule-fire watches: ['book_gap_loss_guard_v2', 'value_reduce_depth_composite', 'reduce_depth_gate', 'reduce_loss_control_refinement', 'reduce_observable_loss_control', 'reduce_side_geometry', 'exit_reduce_drift_guard', 'midband_reduce_rescue', 'exit_clip_separator_watch', 'matched_unchanged_loss_guard_watch', 'exit_shallow_duration_lte52', 'common_clock_residual_child_exit70_79'].
- No zero-row watch currently looks like an obvious wiring break; remaining zero-row watches are watch-specific overlap waits.

## Rows

| lane | status | read | age min | watch rows | suppressed | base rows after freeze | net c | delta c | blockers |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `book_gap_suppression` | `blocked_loss_control_cost` | `collecting_blocked` | 1602.99 | 55 | 24 | 76 | -180.00 | -165.00 | delta_not_positive, suppressed_loss_control_cost_negative |
| `book_gap_loss_guard` | `positive_but_under_sample` | `collecting_positive_but_immature` | 840.10 | 27 | 8 | 25 | 2.00 | 76.00 | settled_lt_30, suppressed_decisions_lt_30 |
| `book_gap_loss_guard_v2` | `blocked_net_not_positive` | `denominator_collecting_rule_not_firing` | 808.57 | 10 | 0 | 25 | -10.00 | 0.00 | settled_lt_30, delta_not_positive, net_not_positive, suppressed_decisions_lt_30 |
| `book_gap_loss_guard_v3` | `positive_but_under_sample` | `collecting_positive_but_immature` | 627.89 | 12 | 2 | 14 | 92.00 | 24.00 | settled_lt_30, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| `book_gap_value_only` | `blocked_loss_control_cost` | `collecting_blocked` | 729.62 | 18 | 4 | 22 | -306.00 | -134.00 | settled_lt_30, delta_not_positive, net_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| `value_reduce_depth_composite` | `blocked_net_not_positive` | `denominator_collecting_rule_not_firing` | 715.31 | 17 | 0 | 22 | -110.00 | 0.00 | settled_lt_30, delta_not_positive, net_not_positive, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| `reduce_depth_gate` | `waiting_no_suppressed_exits` | `denominator_collecting_rule_not_firing` | 909.92 | 21 | 0 | 26 | 116.00 | 0.00 | settled_lt_30, no_suppressed_exits_yet, delta_not_positive, full_loss_cushion_lt_3 |
| `reduce_loss_control_refinement` | `waiting_no_suppressed_exits` | `denominator_collecting_rule_not_firing` | 920.90 | 21 | 0 | 26 | 42.00 | 0.00 | settled_lt_30, delta_not_positive, full_loss_cushion_lt_3 |
| `reduce_observable_loss_control` | `blocked_net_not_positive` | `denominator_collecting_rule_not_firing` | 681.04 | 10 | 0 | 22 | -158.00 | 0.00 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, full_loss_cushion_lt_3 |
| `reduce_side_geometry` | `blocked_net_not_positive` | `denominator_collecting_rule_not_firing` | 1239.74 | 21 | 0 | 36 | -114.00 | 0.00 | settled_lt_30, delta_not_positive |
| `reduce_geometry_relaxed` | `blocked_loss_control_cost` | `collecting_blocked` | 610.70 | 6 | 1 | 11 | -106.00 | -120.00 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, full_loss_cushion_lt_3 |
| `exit_reduce_drift_guard` | `waiting_no_suppressed_exits` | `denominator_collecting_rule_not_firing` | 539.32 | 7 | 0 | 8 | 60.00 | 0.00 | settled_lt_30, suppressed_decisions_lt_30, suppressed_delta_not_positive, full_loss_cushion_lt_3 |
| `midband_reduce_rescue` | `waiting_no_suppressed_exits` | `denominator_collecting_rule_not_firing` | 568.44 | 9 | 0 | 10 | 84.00 | 0.00 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, full_loss_cushion_lt_3 |
| `exit_clip_separator_watch` | `waiting_rule_has_not_fired` | `denominator_collecting_rule_not_firing` | 445.25 | 1 | 0 | 4 | 0.00 | 0.00 | post_freeze_rows_lt_30, known_hold_delta_lt_300c |
| `matched_unchanged_loss_guard_watch` | `waiting_rule_has_not_fired` | `denominator_collecting_rule_not_firing` | 119.52 | 2 | 0 | 1 | 56.00 | 0.00 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, full_loss_cushion_lt_3 |
| `exit_shallow_drawdown` | `positive_but_under_sample` | `collecting_positive_but_immature` | 339.23 | 1 | 1 | 1 | 36.00 | 18.00 | settled_lt_30, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| `exit_shallow_duration_lte52` | `waiting_no_suppressed_exits` | `denominator_collecting_rule_not_firing` | 334.40 | 1 | 0 | 1 | 18.00 | 0.00 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, full_loss_cushion_lt_3 |
| `dual_exit_book_gap_else_reduce` | `blocked_loss_control_cost` | `collecting_blocked` | 853.94 | 25 | 8 | 25 | -350.00 | -242.00 | settled_lt_30, delta_not_positive, net_not_positive, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| `common_clock_strict_forward_v1` | `blocked_net_not_positive` | `collecting_blocked` | 840.10 | 19 | 5 | 25 | -42.00 | 66.00 | settled_lt_30, suppressed_decisions_lt_30, net_not_positive, full_loss_cushion_lt_3 |
| `common_clock_strict_forward_v2` | `positive_but_under_sample` | `collecting_positive_but_immature` | 808.57 | 18 | 5 | 25 | 44.00 | 66.00 | settled_lt_30, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| `common_clock_strict_forward_v3` | `positive_but_under_sample` | `collecting_positive_but_immature` | 627.89 | 11 | 3 | 14 | 106.00 | 42.00 | settled_lt_30, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| `common_clock_residual_child_exit70_79` | `waiting_no_suppressed_exits` | `denominator_collecting_rule_not_firing` | 203.53 | 1 | 0 | 1 | 36.00 | 18.00 | settled_lt_30, child_suppressed_decisions_lt_30, child_delta_vs_parent_not_positive, full_loss_cushion_lt_3 |
| `soft_frontier_midprice_delayed_recheck_exit` | `waiting_no_post_freeze_rows` | `watch_specific_overlap_not_collecting` | 203.79 | 0 | 0 | 1 | 0.00 | 0.00 | joined_rows_lt_30, suppressed_decisions_lt_30, weighted_net_not_positive, delta_not_positive, full_loss_cushion_lt_3 |
| `soft_frontier_midprice_delayed_recheck_rescue` | `waiting_no_post_freeze_rows` | `watch_specific_overlap_not_collecting` | 185.59 | 0 | 0 | 1 | 0.00 | 0.00 | joined_rows_lt_30, suppressed_decisions_lt_30, weighted_net_not_positive, delta_not_positive, full_loss_cushion_lt_3 |
| `feature_gate_value_exit` | `waiting_no_post_freeze_rows` | `watch_specific_overlap_not_collecting` | 233.35 | 0 | 0 | 1 | 0.00 | 0.00 | settled_lt_30, net_not_positive, full_loss_cushion_lt_3, selected_side_live_overlap_only, hold_to_settlement_assumption, not_live_bot_logic |
| `feature_gate_exit_bid_suppression` | `waiting_no_post_freeze_rows` | `watch_specific_overlap_not_collecting` | 237.63 | 0 | 0 | 1 | 0.00 | 0.00 | settled_lt_30, suppressed_decisions_lt_30, net_not_positive, delta_not_positive, full_loss_cushion_lt_3 |
| `feature_gate_exit_bid_delayed_recheck` | `waiting_no_post_freeze_rows` | `watch_specific_overlap_not_collecting` | 214.77 | 0 | 0 | 1 | 0.00 | 0.00 | settled_lt_30, suppressed_decisions_lt_30, net_not_positive, delta_not_positive, full_loss_cushion_lt_3 |
| `value_exit_feature_side_guard` | `not_positive_or_under_sample` | `collecting_watch_only` | 226.82 | 1 | 1 | 1 | 18.00 | 0.00 | settled_lt_30, full_loss_cushion_lt_3, exit_overlap_only, not_live_bot_logic |
