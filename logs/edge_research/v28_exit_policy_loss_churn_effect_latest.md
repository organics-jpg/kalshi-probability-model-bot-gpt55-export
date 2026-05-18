# v28 Exit Policy Loss-Count Churn Effect

Research-only. No live bot changes or orders.

- Generated UTC: `2026-05-11T03:42:25.536661+00:00`

## Interpretation

- This is a churn-readiness lens, not a promotion decision.
- Positive loss-count reduction means fewer losing rows inside that candidate's own frozen/research window.
- Rows are not all on a common clock; use this to pick mechanisms for common-clock validation, not to promote live logic.

## Churn Ranking

| rank | lane | candidate | rows | current W/L | candidate W/L | loss count delta | net delta | suppressed | new losses | near-full delta | blockers |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `observable_reduce_loss_control_diagnostic` | `diagnostic_from_reduce_freeze_reduce_suppress_p75_depth_lte384_or_duration_lte52` | 132 | 76/56 | 92/40 | 16 | 523c ($5.23) | 21 | None |  | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| 2 | `exit_reduce_suppression` | `suppress_reduce_p_hold_ge_075` | 132 | 73/56 | 91/40 | 16 | 337c ($3.37) | 25 | 1 | 0 | suppressed_loss_control_cost_negative |
| 3 | `exit_value_reduce_depth_composite_diagnostic_from_exit_freezes` | `diagnostic_from_exit_freezes_value_v2_reduce_depth384` | 132 | 76/56 | 90/42 | 14 | 483c ($4.83) | 23 | None |  | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| 4 | `exit_reduce_depth_gate_diagnostic_from_reduce_freeze` | `diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_075_entry_depth_lte_384` | 132 | 76/56 | 90/42 | 14 | 413c ($4.13) | 19 | None |  | suppressed_losers_present, suppressed_loss_control_cost_negative |
| 5 | `exit_value_reduce_depth_composite_diagnostic_from_exit_freezes` | `diagnostic_from_exit_freezes_value_v2_reduce_depth295` | 132 | 76/56 | 89/43 | 13 | 431c ($4.31) | 22 | None |  | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| 6 | `exit_reduce_depth_gate_diagnostic_from_reduce_freeze` | `diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_075_entry_depth_lte_295` | 132 | 76/56 | 89/43 | 13 | 361c ($3.61) | 18 | None |  | suppressed_losers_present, suppressed_loss_control_cost_negative |
| 7 | `exit_value_reduce_depth_composite_diagnostic_from_exit_freezes` | `diagnostic_from_exit_freezes_value_only_p75_reduce_depth384` | 132 | 76/56 | 88/44 | 12 | 509c ($5.09) | 61 | None |  | suppressed_losers_present, suppressed_loss_control_cost_negative |
| 8 | `observable_reduce_loss_control_diagnostic` | `diagnostic_from_reduce_freeze_reduce_suppress_p75_entry_stc_lte_596` | 132 | 76/56 | 88/44 | 12 | 389c ($3.89) | 15 | None |  | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| 9 | `observable_reduce_loss_control_diagnostic` | `diagnostic_from_reduce_freeze_reduce_suppress_p75_duration_lte_52` | 132 | 76/56 | 87/45 | 11 | 351c ($3.51) | 14 | None |  | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| 10 | `exit_book_gap_suppression` | `suppress_soft_gap15_or_p_hold75` | 120 | 68/49 | 81/38 | 11 | 235c ($2.35) | 59 | 3 | 0 | suppressed_loss_control_cost_negative |
| 11 | `observable_reduce_loss_control_diagnostic` | `diagnostic_from_reduce_freeze_reduce_suppress_p75_depth_lte384_and_duration_lte75` | 132 | 76/56 | 86/46 | 10 | 289c ($2.89) | 13 | None |  | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 12 | `exit_value_reduce_depth_composite_diagnostic_from_exit_freezes` | `diagnostic_from_exit_freezes_value_v2_reduce_depth384_p79` | 132 | 76/56 | 84/48 | 8 | 467c ($4.67) | 12 | None |  | suppressed_decisions_lt_30 |
| 13 | `exit_reduce_depth_gate_diagnostic_from_reduce_freeze` | `diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_079_entry_depth_lte_384` | 132 | 76/56 | 84/48 | 8 | 397c ($3.97) | 8 | None |  |  |
| 14 | `observable_reduce_loss_control_diagnostic` | `diagnostic_from_reduce_freeze_reduce_suppress_p75_entry_book_age_gte_672` | 132 | 76/56 | 83/49 | 7 | 304c ($3.04) | 9 | None |  | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| 15 | `exit_reduce_depth_gate_diagnostic_from_reduce_freeze` | `diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_075_entry_depth_lte_384_drawdown_lte_2p5` | 132 | 76/56 | 83/49 | 7 | 269c ($2.69) | 9 | None |  | suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 16 | `observable_reduce_loss_control_diagnostic` | `diagnostic_from_reduce_freeze_reduce_suppress_p75_exit_cents_lte_72` | 132 | 76/56 | 82/50 | 6 | 359c ($3.59) | 9 | None |  | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| 17 | `observable_reduce_loss_control_diagnostic` | `diagnostic_from_reduce_freeze_reduce_suppress_p75_exit_sigma_gte_110` | 132 | 76/56 | 82/50 | 6 | 203c ($2.03) | 11 | None |  | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 18 | `exit_reduce_yes_suppression` | `suppress_yes_reduce_p_hold_ge_075` | 103 | 59/41 | 64/36 | 5 | 112c ($1.12) | 6 | 0 | 0 | suppressed_losers_present, suppressed_loss_control_cost_negative |
| 19 | `observable_reduce_loss_control_diagnostic` | `diagnostic_from_reduce_freeze_reduce_suppress_p75_entry_volshock_gte_0468` | 132 | 76/56 | 81/51 | 5 | 91c ($0.91) | 9 | None |  | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 20 | `observable_reduce_loss_control_post_birth` | `post_observable_birth_reduce_suppress_p75_depth_lte384_or_duration_lte52` | 54 | 35/19 | 39/15 | 4 | -126c ($-1.26) | 9 | None |  | suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 21 | `observable_reduce_loss_control_post_birth` | `post_observable_birth_reduce_suppress_p75_entry_stc_lte_596` | 54 | 35/19 | 38/16 | 3 | -110c ($-1.10) | 6 | None |  | suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 22 | `exit_value_reduce_depth_composite_post_composite_birth` | `post_composite_birth_value_v2_reduce_depth384` | 54 | 35/19 | 38/16 | 3 | -116c ($-1.16) | 11 | None |  | delta_not_positive, suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 23 | `exit_value_reduce_depth_composite_post_composite_birth` | `post_composite_birth_value_v2_reduce_depth295` | 54 | 35/19 | 38/16 | 3 | -116c ($-1.16) | 11 | None |  | delta_not_positive, suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 24 | `exit_reduce_depth_gate_post_depth_gate_birth` | `post_depth_gate_birth_reduce_suppress_p_hold_ge_075_entry_depth_lte_384` | 60 | 40/20 | 43/17 | 3 | -174c ($-1.74) | 8 | None |  | delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 25 | `exit_reduce_depth_gate_post_depth_gate_birth` | `post_depth_gate_birth_reduce_suppress_p_hold_ge_075_entry_depth_lte_295` | 60 | 40/20 | 43/17 | 3 | -174c ($-1.74) | 8 | None |  | delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 26 | `exit_book_gap_loss_guard` | `book_gap_loss_guard_value_p85_reduce_p79_gap0` | 59 | 38/20 | 40/18 | 2 | 242c ($2.42) | 17 | 0 | 0 | suppressed_decisions_lt_30 |
| 27 | `exit_book_gap_loss_guard_v3` | `book_gap_loss_guard_v3_value_gap0_or_p85_shallow_or_p95_extreme_reduce_p79_gap0` | 46 | 30/15 | 32/13 | 2 | 166c ($1.66) | 9 | 0 | 0 | suppressed_decisions_lt_30 |
| 28 | `exit_book_gap_loss_guard_v2` | `book_gap_loss_guard_v2_value_gap0_or_p85_shallowdd_reduce_p79_gap0` | 58 | 38/19 | 40/17 | 2 | 152c ($1.52) | 5 | 0 | 0 | suppressed_decisions_lt_30 |
| 29 | `exit_value_reduce_depth_composite_post_composite_birth` | `post_composite_birth_value_v2_reduce_depth384_p79` | 54 | 35/19 | 37/17 | 2 | 152c ($1.52) | 5 | None |  | suppressed_decisions_lt_30 |
| 30 | `exit_reduce_depth_gate_post_depth_gate_birth` | `post_depth_gate_birth_reduce_suppress_p_hold_ge_079_entry_depth_lte_384` | 60 | 40/20 | 42/18 | 2 | 94c ($0.94) | 2 | None |  | full_loss_cushion_lt_3 |
| 31 | `observable_reduce_loss_control_post_birth` | `post_observable_birth_reduce_suppress_p75_duration_lte_52` | 54 | 35/19 | 37/17 | 2 | -142c ($-1.42) | 5 | None |  | suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 32 | `observable_reduce_loss_control_post_birth` | `post_observable_birth_reduce_suppress_p75_depth_lte384_and_duration_lte75` | 54 | 35/19 | 37/17 | 2 | -142c ($-1.42) | 5 | None |  | suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 33 | `dual_exit_book_gap_else_reduce` | `dual_exit_book_gap_else_reduce` | 59 | 38/20 | 40/18 | 2 | -212c ($-2.12) | 30 | 3 | 0 | delta_not_positive, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3, degenerates_to_book_gap_on_shared_window |
| 34 | `exit_reduce_depth_gate_post_depth_gate_birth` | `post_depth_gate_birth_reduce_suppress_p_hold_ge_075_entry_depth_lte_384_drawdown_lte_2p5` | 60 | 40/20 | 41/19 | 1 | -50c ($-0.50) | 3 | None |  | delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 35 | `observable_reduce_loss_control_post_birth` | `post_observable_birth_reduce_suppress_p75_exit_cents_lte_72` | 54 | 35/19 | 36/18 | 1 | -58c ($-0.58) | 2 | None |  | suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 36 | `exit_value_reduce_depth_composite_post_composite_birth` | `post_composite_birth_value_only_p75_reduce_depth384` | 54 | 35/19 | 36/18 | 1 | -272c ($-2.72) | 26 | None |  | delta_not_positive, suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 37 | `observable_reduce_loss_control_post_birth` | `post_observable_birth_reduce_suppress_p75_entry_volshock_gte_0468` | 54 | 35/19 | 34/20 | -1 | -304c ($-3.04) | 2 | None |  | suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 38 | `observable_reduce_loss_control_post_birth` | `post_observable_birth_reduce_suppress_p75_entry_book_age_gte_672` | 54 | 35/19 | 35/19 | 0 | -146c ($-1.46) | 1 | None |  | suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 39 | `observable_reduce_loss_control_post_birth` | `post_observable_birth_reduce_suppress_p75_exit_sigma_gte_110` | 54 | 35/19 | 35/19 | 0 | -242c ($-2.42) | 3 | None |  | suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 40 | `exit_book_gap_value_only` | `value_only_gap15_or_p75` | 0 | 0/0 | 0/0 | 0 | 0c ($0.00) | 0 | 0 | 0 | delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |

## Best Loss-To-Non-Loss Examples

### exit_reduce_suppression

| market | side | result | reason | current | candidate | delta | p_hold |
|---|---|---|---|---:|---:|---:|---:|
| `KXBTC15M-26MAY060300-00` | yes | yes | mushroom_v28_probability_reduce | -22c ($-0.22) | 40c ($0.40) | 62c ($0.62) | 0.753164 |
| `KXBTC15M-26MAY060930-30` | no | no | mushroom_v28_probability_reduce | -14c ($-0.14) | 48c ($0.48) | 62c ($0.62) | 0.787606 |
| `KXBTC15M-26MAY071045-45` | no | no | mushroom_v28_probability_reduce | -10c ($-0.10) | 52c ($0.52) | 62c ($0.62) | 0.760529 |
| `KXBTC15M-26MAY061030-30` | yes | yes | mushroom_v28_probability_reduce | -16c ($-0.16) | 44c ($0.44) | 60c ($0.60) | 0.752739 |
| `KXBTC15M-26MAY060930-30` | no | no | mushroom_v28_probability_reduce | -3c ($-0.03) | 54c ($0.54) | 57c ($0.57) | 0.79918 |

