# v28 Top Candidate Mix/Match Audit

Research-only diagnostic. No live trading logic changed.

- Generated UTC: `2026-05-11T03:46:20.539654+00:00`
- Promotion status: `none_live_ready`

## Top PnL Candidates

| rank | gate | policy | settled | W/L | net | coverage | sim share |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | `top_component_parent_fill_repair_child` | `diagnostic_observable_mid_confidence_parent_fill_quarter` | 76 | 67/9 | 2233c ($22.33) | 75.2% | 34.2% |
| 2 | `top_component_parent_fill_repair_child` | `diagnostic_mid_confidence_parent_fill_quarter` | 76 | 67/9 | 2233c ($22.33) | 75.2% | 34.2% |
| 3 | `top_component_parent_fill_repair_child` | `diagnostic_observable_mid_confidence_parent_fill_half` | 76 | 67/9 | 2190c ($21.89) | 75.2% | 34.2% |
| 4 | `top_component_parent_fill_repair_child` | `diagnostic_mid_confidence_parent_fill_half` | 76 | 67/9 | 2190c ($21.89) | 75.2% | 34.2% |
| 5 | `top_component_parent_fill_repair_child` | `diagnostic_parent_fill_wide_mid_absd_ask_notch` | 76 | 67/9 | 2145c ($21.45) | 75.2% | 34.2% |
| 6 | `top_component_parent_fill_repair_child` | `diagnostic_parent_fill_mid_absd_ask_notch` | 76 | 67/9 | 2142c ($21.42) | 75.2% | 34.2% |
| 7 | `top_component_parent_fill_repair_child` | `diagnostic_smooth_parent_fill_source_risk` | 76 | 67/9 | 2127c ($21.27) | 75.2% | 34.2% |
| 8 | `top_component_false_negative_rescue_child` | `diagnostic_union_rebound` | 76 | 67/9 | 2102c ($21.02) | 75.2% | 34.2% |
| 9 | `top_component_false_negative_rescue_child` | `diagnostic_approved_union_rebound` | 76 | 67/9 | 2102c ($21.02) | 75.2% | 34.2% |
| 10 | `top_component_parent_fill_repair_child` | `diagnostic_exit_child_only_control` | 76 | 67/9 | 2102c ($21.02) | 75.2% | 34.2% |

## Top Winning Candidates

| rank | gate | policy | settled | W/L | win rate | net | coverage | sim share |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `feature_gate_soft_frontier_exit_stack` | `post_soft_stack_entry_soft_raw03_recross50_abs65_ask35_loss_guard_v1_exit` | 19 | 18/1 | 94.7% | 500c ($5.00) | 76.5% | 35.9% |
| 2 | `feature_gate_soft_frontier_exit_stack` | `post_soft_stack_entry_soft_raw03_recross50_abs50_ask35_loss_guard_v1_exit` | 19 | 18/1 | 94.7% | 500c ($5.00) | 82.4% | 42.9% |
| 3 | `feature_gate_soft_frontier_exit_stack` | `post_soft_stack_entry_soft_raw03_recross50_abs50_ask50_loss_guard_v1_exit` | 19 | 18/1 | 94.7% | 500c ($5.00) | 82.4% | 42.9% |
| 4 | `feature_gate_soft_frontier_exit_stack` | `post_soft_stack_bridge_soft_raw03_recross50_abs65_ask35_loss_guard_v1_exit` | 19 | 18/1 | 94.7% | 500c ($5.00) | 76.5% | 35.9% |
| 5 | `feature_gate_soft_frontier_exit_stack` | `post_soft_stack_bridge_soft_raw03_recross50_abs50_ask35_loss_guard_v1_exit` | 19 | 18/1 | 94.7% | 500c ($5.00) | 82.4% | 42.9% |
| 6 | `feature_gate_soft_frontier_exit_stack` | `post_soft_stack_bridge_soft_raw03_recross50_abs50_ask50_loss_guard_v1_exit` | 19 | 18/1 | 94.7% | 500c ($5.00) | 82.4% | 42.9% |
| 7 | `feature_gate_soft_frontier_exit_stack` | `post_soft_stack_entry_soft_raw03_recross50_abs65_ask35_loss_guard_v3_exit` | 19 | 18/1 | 94.7% | 476c ($4.76) | 76.5% | 35.9% |
| 8 | `feature_gate_soft_frontier_exit_stack` | `post_soft_stack_entry_soft_raw03_recross50_abs50_ask35_loss_guard_v3_exit` | 19 | 18/1 | 94.7% | 476c ($4.76) | 82.4% | 42.9% |
| 9 | `feature_gate_soft_frontier_exit_stack` | `post_soft_stack_entry_soft_raw03_recross50_abs50_ask50_loss_guard_v3_exit` | 19 | 18/1 | 94.7% | 476c ($4.76) | 82.4% | 42.9% |
| 10 | `feature_gate_soft_frontier_exit_stack` | `post_soft_stack_bridge_soft_raw03_recross50_abs65_ask35_loss_guard_v3_exit` | 19 | 18/1 | 94.7% | 476c ($4.76) | 76.5% | 35.9% |

## Mix/Match Findings

- `book_gap_else_reduce`: 132 rows, W/L 89/42, net 1118c ($11.18), current-comparable net 721c ($7.21).
- Common reduce/book window: 120 rows; reduce net 902c ($9.02), book-gap net 962c ($9.62).
- `value_only_book_gap_exit` diagnostic book-gap window: 120 rows, W/L 71/49, net 727c ($7.27), suppressed W/L 0/0, loss cost 0c ($0.00).
- `value_only_book_gap_exit` strict post-freeze window: 54 rows, W/L 33/21, net 240c ($2.40), blockers ['delta_not_positive', 'suppressed_losers_present', 'suppressed_loss_control_cost_negative', 'full_loss_cushion_lt_3'].
- `value_v2_reduce_depth384_composite` diagnostic exit-freeze window: rule value_v2_reduce_depth384_p79, 132 rows, W/L 84/48, net 1188c ($11.88), delta 467c ($4.67), suppressed value/reduce 4/8, suppressed W/L 12/0, loss cost 0c ($0.00).
- `value_v2_reduce_depth384_composite` strict post-freeze window: 54 rows, W/L 38/16, net 222c ($2.22), blockers ['delta_not_positive', 'suppressed_decisions_lt_30', 'suppressed_losers_present', 'suppressed_loss_control_cost_negative', 'full_loss_cushion_lt_3'].
- `observable_reduce_loss_control_gate` diagnostic reduce-freeze window: 132 rows, W/L 82/50, delta 359c ($3.59), suppressed W/L 8/1, loss cost -120c ($-1.20).
- `observable_reduce_loss_control_gate` strict post-birth window: 54 rows, delta -58c ($-0.58), would-suppress rows 6, fail reasons {'entry_seconds_to_close_above_gate': 3, 'not_probability_reduce': 44, 'p_hold_below_gate': 1}.
- `midband_reduce_rescue` diagnostic window: 132 rows, suppressed 8, delta 518c ($5.18), loss-count reduction 8, helpful/harmful 8/0; strict post-birth rows 42 with blockers ['suppressed_decisions_lt_30', 'full_loss_cushion_lt_3'].
- `soft_frontier_midprice_boundary_shrink` best diagnostic/watch row: diagnostic_entry_quarter_midprice_boundary has 78 settled, W/L 68/10, coverage 78.2%, net 788c ($7.88), delta 70c ($0.70), band rows 3 raw/weighted -94c ($-0.94)/-24c ($-0.23), blockers ['diagnostic_only_prefreeze', 'reconstructed_share_gt_35pct'].
- `soft_frontier_midprice_boundary_with_book_gap_exit` best overlap: diagnostic_entry_quarter_midprice_boundary_book_gap_weighted_exit_stack has entry settled 78, joined exits 56, weighted exit net 1270c ($12.70), weighted delta 212c ($2.12), blockers ['entry_lane_not_strict_combo_forward', 'entry_reconstructed_share_gt_35pct', 'post_stack_joined_exit_rows_lt_30', 'post_stack_weighted_exit_full_loss_cushion_lt_3'].
- `loss_guarded_book_gap_exit` comparable book-gap window: 120 rows, W/L 78/42, net 1442c ($14.42), loss cost 0c ($0.00).
- `loss_guarded_book_gap_exit` all-exit discovery window: 173 rows, W/L 108/65, net 1632c ($16.32), loss cost -186c ($-1.86).
- `loss_guarded_book_gap_exit_v2` comparable book-gap window: 120 rows, W/L 78/42, net 1266c ($12.66), loss cost 0c ($0.00).
- `loss_guarded_book_gap_exit_v2` all-exit discovery window: 173 rows, W/L 109/64, net 1574c ($15.74), loss cost 0c ($0.00).
- `loss_guarded_book_gap_exit_v3_extreme_p` strict post-freeze window: 46 rows, W/L 33/13, net 644c ($6.44), blockers ['suppressed_decisions_lt_30'].
- `loss_guarded_book_gap_exit_v3_extreme_p` all-exit diagnostic window: 173 rows, W/L 109/64, net 1634c ($16.34), loss cost 0c ($0.00).
- The exit-policy family is still the strongest mix/match direction, but every new variant needs clean post-freeze rows before promotion.

## Feature-Gate Exit Overlap

| lane | rule | selected | approved | entry net | joined rows | joined entry net | joined reduce exit | joined book-gap exit | ambiguous |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `post_feature_freeze_entry` | `raw05_recross60_abs085_ask65` | 47 | 45 | 344c ($3.44) | 32 | 245c ($2.45) | 426c ($4.26) | 434c ($4.34) | 13 |
| `post_feature_freeze_bridge` | `raw05_recross60_abs085_ask65` | 47 | 45 | 344c ($3.44) | 32 | 245c ($2.45) | 426c ($4.26) | 434c ($4.34) | 13 |
| `post_feature_freeze_entry` | `raw05_recross60_abs085` | 55 | 40 | 445c ($4.45) | 28 | 242c ($2.42) | 284c ($2.84) | 272c ($2.72) | 12 |
| `post_feature_freeze_bridge` | `raw05_recross60_abs085` | 55 | 40 | 445c ($4.45) | 28 | 242c ($2.42) | 284c ($2.84) | 272c ($2.72) | 12 |
| `post_feature_freeze_entry` | `raw03_recross70_abs075` | 64 | 39 | 307c ($3.07) | 28 | 242c ($2.42) | 284c ($2.84) | 272c ($2.72) | 11 |
| `post_feature_freeze_bridge` | `raw03_recross70_abs075` | 64 | 39 | 307c ($3.07) | 28 | 242c ($2.42) | 284c ($2.84) | 272c ($2.72) | 11 |
| `post_feature_freeze_entry` | `raw07_recross60_abs085` | 38 | 30 | 454c ($4.54) | 19 | 228c ($2.28) | 140c ($1.40) | 250c ($2.50) | 11 |
| `post_feature_freeze_bridge` | `raw07_recross60_abs085` | 38 | 30 | 454c ($4.54) | 19 | 228c ($2.28) | 140c ($1.40) | 250c ($2.50) | 11 |

## Forgetting / Memory Family

| rank | gate | policy | settled | W/L | win rate | net | coverage | sim share | blockers |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | `rmt_forgetting_entry_bakeoff` | `rmt_memory_gate_p58_edge2` | 7 | 5/2 | 71.4% | -2c ($-0.02) | 3.9% | 71.4% | diagnostic_bakeoff, not_fresh_forward_gate |
| 2 | `rmt_forgetting_entry_bakeoff` | `rmt_aggressive_forget_p52_edge2` | 2 | 1/1 | 50.0% | -114c ($-1.14) | 1.1% | 50.0% | diagnostic_bakeoff, not_fresh_forward_gate |
| 3 | `rmt_forgetting_entry_bakeoff` | `rmt_aggressive_forget_p55_edge2` | 2 | 1/1 | 50.0% | -114c ($-1.14) | 1.1% | 50.0% | diagnostic_bakeoff, not_fresh_forward_gate |
| 4 | `rmt_forgetting_entry_bakeoff` | `rmt_aggressive_forget_p58_edge2` | 2 | 1/1 | 50.0% | -114c ($-1.14) | 1.1% | 50.0% | diagnostic_bakeoff, not_fresh_forward_gate |
| 5 | `rmt_forgetting_entry_bakeoff` | `rmt_repetition_forget_p58_edge2` | 15 | 10/5 | 66.7% | -173c ($-1.73) | 8.3% | 66.7% | diagnostic_bakeoff, not_fresh_forward_gate |
| 6 | `phi_forgetting_fv` | `phi_half_shrink_to50` | 88 | 49/39 | 55.7% | -247c ($-2.47) | 98.9% | n/a | brier_not_better_than_raw, logloss_not_better_than_raw |
| 7 | `phi_forgetting_fv` | `phi_forget_logit125` | 88 | 49/39 | 55.7% | -247c ($-2.47) | 98.9% | n/a | brier_not_better_than_raw |
| 8 | `phi_forgetting_fv` | `phi_shrink_to50` | 88 | 49/39 | 55.7% | -247c ($-2.47) | 98.9% | n/a | brier_not_better_than_raw, logloss_not_better_than_raw |
| 9 | `phi_forgetting_fv` | `phi_forget_plus03` | 88 | 49/39 | 55.7% | -247c ($-2.47) | 98.9% | n/a | brier_not_better_than_raw, logloss_not_better_than_raw |
| 10 | `phi_forgetting_fv` | `phi_forget_plus05` | 88 | 49/39 | 55.7% | -247c ($-2.47) | 98.9% | n/a | brier_not_better_than_raw, logloss_not_better_than_raw |
| 11 | `rmt_forgetting_entry_bakeoff` | `rmt_memory_gate_p55_edge2` | 10 | 5/5 | 50.0% | -332c ($-3.32) | 5.5% | 80.0% | diagnostic_bakeoff, not_fresh_forward_gate |
| 12 | `rmt_forgetting_entry_bakeoff` | `rmt_memory_gate_p52_edge2` | 12 | 6/6 | 50.0% | -340c ($-3.40) | 6.6% | 83.3% | diagnostic_bakeoff, not_fresh_forward_gate |
| 13 | `rmt_forgetting_entry_bakeoff` | `rmt_repetition_forget_p55_edge2` | 24 | 14/10 | 58.3% | -363c ($-3.63) | 13.3% | 79.2% | diagnostic_bakeoff, not_fresh_forward_gate |
| 14 | `path_rmt_forward_gate` | `selective_rmt_memory_gap_wait240_rmtedge02_or_opp` | 128 | 76/52 | 59.4% | -456c ($-4.56) | 87.1% | 90.6% | simulated_share_gt_0.35, net_not_positive |
| 15 | `rmt_forgetting_entry_bakeoff` | `rmt_repetition_forget_p52_edge2` | 31 | 17/14 | 54.8% | -459c ($-4.59) | 17.1% | 83.9% | diagnostic_bakeoff, not_fresh_forward_gate |
| 16 | `rmt_forgetting_entry_bakeoff` | `rmt_memory_gate_p50_edge0` | 175 | 107/68 | 61.1% | -674c ($-6.74) | 96.7% | 97.1% | diagnostic_bakeoff, not_fresh_forward_gate |
| 17 | `path_rmt_forward_gate` | `weakraw_rmt_memory_margin02_wait240_or_opp` | 85 | 52/33 | 61.2% | -942c ($-9.42) | 57.8% | 78.8% | simulated_share_gt_0.35, coverage_too_low, net_not_positive |
| 18 | `path_rmt_forward_gate` | `weakraw_rmt_repetition_margin02_wait240_or_opp` | 85 | 52/33 | 61.2% | -942c ($-9.42) | 57.8% | 78.8% | simulated_share_gt_0.35, coverage_too_low, net_not_positive |
| 19 | `path_rmt_forward_gate` | `selective_rmt_repetition_gap_wait240_rmtedge02_or_opp` | 132 | 75/57 | 56.8% | -986c ($-9.86) | 89.8% | 92.4% | simulated_share_gt_0.35, net_not_positive |
| 20 | `reward_memory_fv` | `reward_memory_logit125` | 140 | 77/63 | 55.0% | -1012c ($-10.12) | 98.6% | n/a | brier_not_better_than_raw, logloss_not_better_than_raw |

## Catastrophic Forgetting FV Overlays

These are the explicit boundary/phi/reward-memory FV overlays. They are shown separately so negative catastrophic-forgetting rows do not disappear below RMT sidecar rows.

| rank | gate | policy | settled | W/L | net | coverage | blockers |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | `phi_forgetting_fv` | `phi_half_shrink_to50` | 88 | 49/39 | -247c ($-2.47) | 98.9% | brier_not_better_than_raw, logloss_not_better_than_raw |
| 2 | `phi_forgetting_fv` | `phi_forget_logit125` | 88 | 49/39 | -247c ($-2.47) | 98.9% | brier_not_better_than_raw |
| 3 | `phi_forgetting_fv` | `phi_shrink_to50` | 88 | 49/39 | -247c ($-2.47) | 98.9% | brier_not_better_than_raw, logloss_not_better_than_raw |
| 4 | `phi_forgetting_fv` | `phi_forget_plus03` | 88 | 49/39 | -247c ($-2.47) | 98.9% | brier_not_better_than_raw, logloss_not_better_than_raw |
| 5 | `phi_forgetting_fv` | `phi_forget_plus05` | 88 | 49/39 | -247c ($-2.47) | 98.9% | brier_not_better_than_raw, logloss_not_better_than_raw |
| 6 | `reward_memory_fv` | `reward_memory_logit125` | 140 | 77/63 | -1012c ($-10.12) | 98.6% | brier_not_better_than_raw, logloss_not_better_than_raw |
| 7 | `reward_memory_fv` | `logit125_probability` | 140 | 77/63 | -1012c ($-10.12) | 98.6% | brier_not_better_than_raw, logloss_not_better_than_raw |
| 8 | `reward_memory_fv` | `reward_memory_plus05` | 140 | 77/63 | -1012c ($-10.12) | 98.6% | brier_not_better_than_raw, logloss_not_better_than_raw |
| 9 | `reward_memory_fv` | `plus05_probability` | 140 | 77/63 | -1012c ($-10.12) | 98.6% | brier_not_better_than_raw, logloss_not_better_than_raw |
| 10 | `boundary_memory_fv` | `boundary_memory_logit125` | 141 | 77/64 | -1120c ($-11.20) | 98.6% | brier_not_better_than_raw, logloss_not_better_than_raw |
| 11 | `boundary_memory_fv` | `conditional_logit125_p60_only` | 141 | 77/64 | -1120c ($-11.20) | 98.6% | brier_not_better_than_raw, logloss_not_better_than_raw |
| 12 | `boundary_memory_fv` | `boundary_memory_plus05` | 141 | 77/64 | -1120c ($-11.20) | 98.6% | brier_not_better_than_raw, logloss_not_better_than_raw |

## Sidecar Readiness

- Sidecar-ready rows: `0` out of `652` candidate rows.
- Closest positive sidecar: `boundary_clock_feature_gate_continuous_penalty / post_penalty_birth_entry_cheap_penalty025_rank_only` with 51 settled, net 504c ($5.04), cushion 5, missing gates ['live_ready_false'].

## Recommended Research Tracks

- `dual_exit_book_gap_else_reduce`: Book-gap suppression dominates plain reduce-suppression on the common exit window; reduce-only rows add positive net on the wider reduce ledger. Blockers: needs_fresh_freeze, exit_loss_control_signature_not_resolved, live_ready_false.
- `value_only_book_gap_exit`: The top book-gap lane's catastrophic cost comes from probability_reduce holds; suppressing only value-over-hold exits keeps soft-exit winner recovery while removing suppressed losers on the diagnostic book-gap window. Blockers: new_freeze_settled_lt_30, needs_post_freeze_forward_rows, live_ready_false.
- `value_v2_reduce_depth384_composite`: The strongest mixed exit idea separates rich-book value exits from shallow-depth probability-reduce exits; the safer frozen primary uses v2 value guards plus p_hold>=0.75/depth<=384 reduce suppression. Blockers: new_freeze_settled_lt_30, suppressed_decisions_lt_30, needs_post_freeze_forward_rows, live_ready_false.
- `observable_reduce_loss_control_gate`: The newest observable gate combines shallow-entry-depth and very-short-duration reduce churn; it recovers diagnostic clipped winners without observed loss-control cost, but strict post-birth rows have not produced eligible probability_reduce exits yet. Blockers: settled_lt_30, suppressed_decisions_lt_30, no_post_birth_probability_reduce_rows, live_ready_false.
- `midband_reduce_rescue`: The latest reduce-harm classifier says high p_hold rich exits can be dangerous to suppress, while lower p_hold 0.60-0.75 probability-reduce clips recovered winners in diagnostic rows without observed suppression harm. Blockers: new_freeze_no_post_birth_rows, suppressed_decisions_lt_30, needs_post_freeze_forward_rows, live_ready_false.
- `loss_guarded_book_gap_exit`: The loss-guard keeps most book-gap upside while shrinking suppressed full-loss cost; on the comparable book-gap freeze window it improves current v28 by +473c with 0c observed suppressed-loss cost. Blockers: new_freeze_settled_lt_30, needs_post_freeze_forward_rows, live_ready_false.
- `loss_guarded_book_gap_exit_v2`: The stricter loss-guard v2 gives up some comparable-window upside, but removes the observed suppressed-loss cost on the broader diagnostic exit sample by refusing high-p_hold holds when the book gap is negative and fair drawdown is deep. Blockers: new_freeze_settled_lt_30, suppressed_decisions_lt_30, needs_post_freeze_forward_rows, live_ready_false.
- `loss_guarded_book_gap_exit_v3_extreme_p`: V3 keeps v2's rich-exit/negative-gap protection but tests whether extreme p_hold>=0.95 value exits recover clipped winners without reopening the lower-confidence 80-90c rich-exit failure. Blockers: new_freeze_settled_lt_30, needs_post_freeze_forward_rows, live_ready_false.
- `clean_feature_gate_with_book_gap_exit_watch`: The clean ask65 feature-gate row has zero reconstructed share and the joined approved subset improves under book-gap exit handling, but sample and coverage are too small. Blockers: settled_lt_30, coverage_too_low_for_ask65, row_join_is_partial, live_ready_false.
- `soft_frontier_feature_gate_with_guarded_exit_stack`: The soft-frontier rule is the broadest clean observable feature gate that meets target coverage diagnostically; this new frozen stack tests it with book-gap and loss-guarded exits from its own timestamp. Blockers: new_freeze_no_joined_rows, settled_lt_30, live_ready_false.
- `soft_frontier_midprice_boundary_shrink`: The strongest new mix from the broad soft-frontier branch shrinks only near-boundary mid-price rows, preserving selected-market coverage while reducing the repeated -133c diagnostic loss pocket to -33c at quarter size. Blockers: new_freeze_settled_lt_30, strict_forward_rows_zero, source_share_still_high_on_post_feature_window, live_ready_false.
- `soft_frontier_midprice_boundary_with_book_gap_exit`: The weighted overlap audit combines the top broad-entry shrink with guarded exits; diagnostic matched book-gap rows beat the live baseline, but the combination is newly frozen and strict overlap is not mature. Blockers: entry_lane_not_strict_combo_forward, strict_combo_joined_rows_lt_30, live_ready_false.
- `rmt_p58_edge2_as_narrow_sidecar_only`: RMT p58 edge2 has the highest current win rate among >=10-settled lanes, but it is tiny, mostly reconstructed, and barely overlaps the boundary-clock feature gate. Blockers: diagnostic_only, coverage_too_low, simulated_share_gt_35pct, poor_stack_overlap.

## Interpretation

- Top PnL is currently an exit-policy story, not an entry-gate story.
- Top win rate is mostly narrow and/or source-quality blocked, so it should be a sidecar/watch lane rather than the main broad strategy.
- The cleanest mature freeze is the stricter v2 loss-guard; V3 is the newest extreme-probability branch and has to earn post-freeze rows from its own timestamp.
