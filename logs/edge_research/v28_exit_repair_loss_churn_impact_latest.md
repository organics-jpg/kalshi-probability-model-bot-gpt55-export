# v28 Exit Repair Loss-Churn Impact

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T15:15:32.813270+00:00`

## Interpretation

- This is a loss-count impact report only; it does not promote or change exit logic.
- Best strict-forward loss-count reducer is reduce_suppression / suppress_reduce_p_hold_ge_075: losses 31 -> 23 (8 removed), delta 189.0c, blockers ['suppressed_loss_control_cost_negative'].
- Best diagnostic-only loss-count reducer is reduce_observable_loss_control / diagnostic_from_reduce_freeze_reduce_suppress_p75_depth_lte384_or_duration_lte52: losses 39 -> 31 (8 removed), delta 87.0c.

## Strict Forward Rows

| rank | family | candidate | settled | losses current->candidate | removed | reduction | delta c | suppressed | suppressed losers | loss cost | cushion | blockers |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `reduce_suppression` | `suppress_reduce_p_hold_ge_075` | 69 | 31->23 | 8 | 25.806452% | 189.000000 | 11 | None | -306.000000 | None | suppressed_loss_control_cost_negative |
| 2 | `book_gap_suppression` | `suppress_soft_gap15_or_p_hold75` | 73 | 31->24 | 7 | 22.580645% | 399.000000 | 31 | None | -300.000000 | None | suppressed_loss_control_cost_negative |
| 3 | `reduce_yes_suppression` | `suppress_yes_reduce_p_hold_ge_075` | 65 | 26->23 | 3 | 11.538462% | 14.000000 | 4 | 1 | -146.000000 | None | suppressed_losers_present, suppressed_loss_control_cost_negative |
| 4 | `exit_value_reduce_depth_composite` | `post_composite_birth_value_only_p75_reduce_depth384` | 23 | 6->8 | -2 | -33.333333% | -360.000000 | 11 | 3 | -496.000000 | 0 | settled_lt_30, delta_not_positive, net_not_positive, suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 5 | `book_gap_loss_guard` | `book_gap_loss_guard_value_p85_reduce_p79_gap0` | 34 | 9->9 | 0 | 0.000000% | 68.000000 | 7 | None | 0.000000 | None | suppressed_decisions_lt_30 |
| 6 | `exit_value_reduce_depth_composite` | `post_composite_birth_value_v2_reduce_depth384_p79` | 23 | 6->6 | 0 | 0.000000% | 40.000000 | 2 | 0 | 0.000000 | 1 | settled_lt_30, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| 7 | `book_gap_loss_guard_v2` | `book_gap_loss_guard_v2_value_gap0_or_p85_shallowdd_reduce_p79_gap0` | 13 | 3->3 | 0 | 0.000000% | 22.000000 | 1 | None | 0.000000 | None | settled_lt_30, suppressed_decisions_lt_30 |
| 8 | `exit_value_reduce_depth_composite` | `post_composite_birth_value_v2_reduce_depth384` | 23 | 6->6 | 0 | 0.000000% | -64.000000 | 4 | 1 | -146.000000 | 0 | settled_lt_30, delta_not_positive, suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 9 | `exit_value_reduce_depth_composite` | `post_composite_birth_value_v2_reduce_depth295` | 23 | 6->6 | 0 | 0.000000% | -64.000000 | 4 | 1 | -146.000000 | 0 | settled_lt_30, delta_not_positive, suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 10 | `reduce_observable_loss_control` | `post_observable_birth_reduce_suppress_p75_exit_cents_lte_72` | 18 | 7->7 | 0 | 0.000000% | -120.000000 | 1 | 1 | -120.000000 | 0 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 11 | `reduce_observable_loss_control` | `post_observable_birth_reduce_suppress_p75_entry_stc_lte_596` | 18 | 7->7 | 0 | 0.000000% | -146.000000 | 1 | 1 | -146.000000 | 0 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 12 | `reduce_observable_loss_control` | `post_observable_birth_reduce_suppress_p75_duration_lte_52` | 18 | 7->7 | 0 | 0.000000% | -146.000000 | 1 | 1 | -146.000000 | 0 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 13 | `reduce_observable_loss_control` | `post_observable_birth_reduce_suppress_p75_entry_book_age_gte_672` | 18 | 7->7 | 0 | 0.000000% | -146.000000 | 1 | 1 | -146.000000 | 0 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 14 | `reduce_observable_loss_control` | `post_observable_birth_reduce_suppress_p75_exit_sigma_gte_110` | 18 | 7->7 | 0 | 0.000000% | -146.000000 | 1 | 1 | -146.000000 | 0 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 15 | `reduce_observable_loss_control` | `post_observable_birth_reduce_suppress_p75_entry_volshock_gte_0468` | 18 | 7->7 | 0 | 0.000000% | -146.000000 | 1 | 1 | -146.000000 | 0 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 16 | `reduce_observable_loss_control` | `post_observable_birth_reduce_suppress_p75_depth_lte384_and_duration_lte75` | 18 | 7->7 | 0 | 0.000000% | -146.000000 | 1 | 1 | -146.000000 | 0 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 17 | `reduce_observable_loss_control` | `post_observable_birth_reduce_suppress_p75_depth_lte384_or_duration_lte52` | 18 | 7->7 | 0 | 0.000000% | -224.000000 | 3 | 2 | -266.000000 | 0 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 18 | `reduce_depth_gate` | `post_depth_gate_birth_reduce_suppress_p_hold_ge_075_entry_depth_lte_384` | 18 | 5->5 | 0 | 0.000000% | 0.000000 | 0 | 0 | 0.000000 | 0 | settled_lt_30, no_suppressed_exits_yet, delta_not_positive, full_loss_cushion_lt_3 |
| 19 | `reduce_depth_gate` | `post_depth_gate_birth_reduce_suppress_p_hold_ge_075_entry_depth_lte_295` | 18 | 5->5 | 0 | 0.000000% | 0.000000 | 0 | 0 | 0.000000 | 0 | settled_lt_30, no_suppressed_exits_yet, delta_not_positive, full_loss_cushion_lt_3 |
| 20 | `reduce_depth_gate` | `post_depth_gate_birth_reduce_suppress_p_hold_ge_079_entry_depth_lte_384` | 18 | 5->5 | 0 | 0.000000% | 0.000000 | 0 | 0 | 0.000000 | 0 | settled_lt_30, no_suppressed_exits_yet, delta_not_positive, full_loss_cushion_lt_3 |
| 21 | `reduce_depth_gate` | `post_depth_gate_birth_reduce_suppress_p_hold_ge_075_entry_depth_lte_384_drawdown_lte_2p5` | 18 | 5->5 | 0 | 0.000000% | 0.000000 | 0 | 0 | 0.000000 | 0 | settled_lt_30, no_suppressed_exits_yet, delta_not_positive, full_loss_cushion_lt_3 |

## Diagnostic-Only Rows

| rank | family | candidate | settled | losses current->candidate | removed | reduction | delta c | suppressed | suppressed losers | loss cost | cushion | blockers |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `reduce_observable_loss_control` | `diagnostic_from_reduce_freeze_reduce_suppress_p75_depth_lte384_or_duration_lte52` | 90 | 39->31 | 8 | 20.512821% | 87.000000 | 12 | 3 | -424.000000 | 0 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 2 | `reduce_observable_loss_control` | `diagnostic_from_reduce_freeze_reduce_suppress_p75_exit_cents_lte_72` | 90 | 39->33 | 6 | 15.384615% | 299.000000 | 8 | 1 | -120.000000 | 2 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 3 | `reduce_observable_loss_control` | `diagnostic_from_reduce_freeze_reduce_suppress_p75_duration_lte_52` | 90 | 39->33 | 6 | 15.384615% | 99.000000 | 9 | 2 | -304.000000 | 0 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 4 | `reduce_observable_loss_control` | `diagnostic_from_reduce_freeze_reduce_suppress_p75_entry_stc_lte_596` | 90 | 39->33 | 6 | 15.384615% | 93.000000 | 9 | 2 | -304.000000 | 0 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 5 | `reduce_depth_gate` | `diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_075_entry_depth_lte_384` | 56 | 24->19 | 5 | 20.833333% | 161.000000 | 6 | 1 | -120.000000 | 1 | suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 6 | `reduce_observable_loss_control` | `diagnostic_from_reduce_freeze_reduce_suppress_p75_entry_book_age_gte_672` | 90 | 39->34 | 5 | 12.820513% | 146.000000 | 6 | 1 | -146.000000 | 1 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 7 | `reduce_observable_loss_control` | `diagnostic_from_reduce_freeze_reduce_suppress_p75_exit_sigma_gte_110` | 90 | 39->34 | 5 | 12.820513% | 97.000000 | 9 | 2 | -304.000000 | 0 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 8 | `reduce_observable_loss_control` | `diagnostic_from_reduce_freeze_reduce_suppress_p75_entry_volshock_gte_0468` | 90 | 39->34 | 5 | 12.820513% | 91.000000 | 9 | 2 | -304.000000 | 0 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 9 | `reduce_observable_loss_control` | `diagnostic_from_reduce_freeze_reduce_suppress_p75_depth_lte384_and_duration_lte75` | 90 | 39->34 | 5 | 12.820513% | 37.000000 | 8 | 2 | -304.000000 | 0 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 10 | `exit_value_reduce_depth_composite` | `diagnostic_from_exit_freezes_value_v2_reduce_depth384` | 66 | 26->22 | 4 | 15.384615% | 321.000000 | 8 | 0 | 0.000000 | 5 | suppressed_decisions_lt_30 |
| 11 | `exit_value_reduce_depth_composite` | `diagnostic_from_exit_freezes_value_v2_reduce_depth295` | 66 | 26->22 | 4 | 15.384615% | 321.000000 | 8 | 0 | 0.000000 | 5 | suppressed_decisions_lt_30 |
| 12 | `reduce_depth_gate` | `diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_075_entry_depth_lte_384_drawdown_lte_2p5` | 56 | 24->20 | 4 | 16.666667% | 219.000000 | 4 | 0 | 0.000000 | 2 | full_loss_cushion_lt_3 |
| 13 | `reduce_depth_gate` | `diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_075_entry_depth_lte_295` | 56 | 24->20 | 4 | 16.666667% | 109.000000 | 5 | 1 | -120.000000 | 1 | suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 14 | `exit_value_reduce_depth_composite` | `diagnostic_from_exit_freezes_value_only_p75_reduce_depth384` | 66 | 26->24 | 2 | 7.692308% | 175.000000 | 28 | 2 | -350.000000 | 4 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| 15 | `exit_value_reduce_depth_composite` | `diagnostic_from_exit_freezes_value_v2_reduce_depth384_p79` | 66 | 26->24 | 2 | 7.692308% | 155.000000 | 5 | 0 | 0.000000 | 3 | suppressed_decisions_lt_30 |
| 16 | `reduce_depth_gate` | `diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_079_entry_depth_lte_384` | 56 | 24->22 | 2 | 8.333333% | 109.000000 | 2 | 0 | 0.000000 | 1 | full_loss_cushion_lt_3 |
