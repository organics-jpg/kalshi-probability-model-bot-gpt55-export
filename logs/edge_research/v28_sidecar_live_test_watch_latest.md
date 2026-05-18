# v28 Sidecar Live-Test Watch

Research-only. No live bot changes or orders.

- Generated UTC: `2026-05-11T03:42:24.717213+00:00`
- Requirements: `{'coverage_requirement': 'none_for_sidecar_watch', 'min_settled': 30, 'max_simulated_or_reconstructed_share': 0.35, 'min_full_loss_cushion': 3, 'live_baseline_cents': -116.99}`
- Counts: `{'candidate_rows': 652, 'positive_rows': 518, 'sidecar_ready_rows': 0}`

## Interpretation

- Sidecar watch intentionally ignores broad coverage, but keeps sample, net, source-quality, cushion, and readiness gates.
- Live-baseline comparison is -117c from the controlled live-test gate.
- This report is a live-test review aid only; it does not place orders or change live logic.
- Closest positive sidecar is boundary_clock_feature_gate_continuous_penalty / post_penalty_birth_entry_cheap_penalty025_rank_only with 51 settled, net 504.0c, sim share 0.17647058823529413, delta live 620.99c, missing ['live_ready_false'].

## Closest Positive Sidecars

| rank | gate | policy | settled | W/L | coverage | net | delta live | sim share | cushion | ready | missing gates |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_entry_cheap_penalty025_rank_only` | 51 | 41/10 | 66.2% | 504c ($5.04) | 621c ($6.21) | 17.6% | 5 | False | live_ready_false |
| 2 | `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_entry_cheap_penalty050_rank_only` | 51 | 41/10 | 66.2% | 504c ($5.04) | 621c ($6.21) | 17.6% | 5 | False | live_ready_false |
| 3 | `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_entry_cheap_penalty100_rank_only` | 51 | 41/10 | 66.2% | 504c ($5.04) | 621c ($6.21) | 17.6% | 5 | False | live_ready_false |
| 4 | `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_bridge_cheap_penalty025_rank_only` | 51 | 41/10 | 66.2% | 504c ($5.04) | 621c ($6.21) | 17.6% | 5 | False | live_ready_false |
| 5 | `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_bridge_cheap_penalty050_rank_only` | 51 | 41/10 | 66.2% | 504c ($5.04) | 621c ($6.21) | 17.6% | 5 | False | live_ready_false |
| 6 | `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_bridge_cheap_penalty100_rank_only` | 51 | 41/10 | 66.2% | 504c ($5.04) | 621c ($6.21) | 17.6% | 5 | False | live_ready_false |
| 7 | `boundary_clock_feature_gate_candidate` | `post_feature_freeze_entry_raw07_recross60_abs085` | 38 | 29/9 | 46.3% | 454c ($4.54) | 571c ($5.71) | 21.1% | 4 | False | live_ready_false |
| 8 | `boundary_clock_feature_gate_candidate` | `post_feature_freeze_bridge_raw07_recross60_abs085` | 38 | 29/9 | 46.3% | 454c ($4.54) | 571c ($5.71) | 21.1% | 4 | False | live_ready_false |
| 9 | `boundary_clock_feature_gate_candidate` | `post_feature_freeze_entry_raw05_recross60_abs085` | 55 | 39/16 | 67.1% | 445c ($4.45) | 562c ($5.62) | 27.3% | 4 | False | live_ready_false |
| 10 | `boundary_clock_feature_gate_candidate` | `post_feature_freeze_bridge_raw05_recross60_abs085` | 55 | 39/16 | 67.1% | 445c ($4.45) | 562c ($5.62) | 27.3% | 4 | False | live_ready_false |
| 11 | `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_entry_cheap_penalty050_floor05` | 44 | 40/4 | 57.1% | 443c ($4.43) | 560c ($5.60) | 4.5% | 4 | False | live_ready_false |
| 12 | `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_bridge_cheap_penalty050_floor05` | 44 | 40/4 | 57.1% | 443c ($4.43) | 560c ($5.60) | 4.5% | 4 | False | live_ready_false |
| 13 | `feature_gate_core_expansion_mix` | `core_only` | 40 | 36/4 | 48.8% | 357c ($3.57) | 474c ($4.74) | 5.0% | 3 | False | live_ready_false |
| 14 | `feature_gate_core_expansion_mix` | `skip_thin_cheap_else_half` | 60 | 42/18 | 73.2% | 345c ($3.45) | 462c ($4.62) | 35.0% | 3 | False | live_ready_false |
| 15 | `feature_gate_core_expansion_mix` | `skip_source_thin_cheap_else_half` | 60 | 42/18 | 73.2% | 345c ($3.45) | 462c ($4.62) | 35.0% | 3 | False | live_ready_false |
| 16 | `boundary_clock_feature_gate_candidate` | `post_feature_freeze_entry_raw05_recross60_abs085_ask65` | 47 | 42/5 | 57.3% | 344c ($3.44) | 461c ($4.61) | 4.3% | 3 | False | live_ready_false |
| 17 | `boundary_clock_feature_gate_candidate` | `post_feature_freeze_bridge_raw05_recross60_abs085_ask65` | 47 | 42/5 | 57.3% | 344c ($3.44) | 461c ($4.61) | 4.3% | 3 | False | live_ready_false |
| 18 | `approved_entry_book_raw_blend_fv` | `book_raw_blend_alpha_0p50` | 55 | 47/8 | n/a | 362c ($3.62) | 479c ($4.79) | n/a | 3 | False | source_unknown |
| 19 | `approved_entry_book_fv` | `actual_approved_entries + book_probability` | 133 | n/a | n/a | 701c ($7.01) | 818c ($8.18) | 0.0% | 7 | False | control_risk_stop_active, live_ready_false |
| 20 | `feature_gate_book_gap_exit_stack` | `post_stack_entry_raw05_recross60_abs085_ask65_loss_guard_v1_exit` | 27 | 24/3 | 61.2% | 554c ($5.54) | 671c ($6.71) | 4.9% | 5 | False | sample+3, live_ready_false |

## Top Net Sidecars

| rank | gate | policy | settled | W/L | coverage | net | delta live | sim share | cushion | ready | missing gates |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_entry_cheap_penalty025_rank_only` | 83 | 68/15 | 82.2% | 1842c ($18.43) | 1959c ($19.59) | 21.7% | 18 | False | needs_own_frozen_forward_birth, live_ready_false |
| 2 | `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_entry_cheap_penalty050_rank_only` | 83 | 68/15 | 82.2% | 1842c ($18.43) | 1959c ($19.59) | 21.7% | 18 | False | needs_own_frozen_forward_birth, live_ready_false |
| 3 | `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_entry_cheap_penalty100_rank_only` | 83 | 68/15 | 82.2% | 1842c ($18.43) | 1959c ($19.59) | 21.7% | 18 | False | needs_own_frozen_forward_birth, live_ready_false |
| 4 | `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty025_rank_only` | 83 | 68/15 | 82.2% | 1842c ($18.43) | 1959c ($19.59) | 21.7% | 18 | False | needs_own_frozen_forward_birth, live_ready_false |
| 5 | `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty050_rank_only` | 83 | 68/15 | 82.2% | 1842c ($18.43) | 1959c ($19.59) | 21.7% | 18 | False | needs_own_frozen_forward_birth, live_ready_false |
| 6 | `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty100_rank_only` | 83 | 68/15 | 82.2% | 1842c ($18.43) | 1959c ($19.59) | 21.7% | 18 | False | needs_own_frozen_forward_birth, live_ready_false |
| 7 | `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_plus_approved_parent_fill + post_penalty_birth_entry_cheap_penalty025_rank_only` | 83 | 68/15 | 82.2% | 1842c ($18.43) | 1959c ($19.59) | 21.7% | 18 | False | needs_own_frozen_forward_birth, live_ready_false |
| 8 | `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_plus_approved_parent_fill + post_penalty_birth_entry_cheap_penalty050_rank_only` | 83 | 68/15 | 82.2% | 1842c ($18.43) | 1959c ($19.59) | 21.7% | 18 | False | needs_own_frozen_forward_birth, live_ready_false |
| 9 | `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_plus_approved_parent_fill + post_penalty_birth_entry_cheap_penalty100_rank_only` | 83 | 68/15 | 82.2% | 1842c ($18.43) | 1959c ($19.59) | 21.7% | 18 | False | needs_own_frozen_forward_birth, live_ready_false |
| 10 | `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_plus_approved_parent_fill + post_penalty_birth_bridge_cheap_penalty025_rank_only` | 83 | 68/15 | 82.2% | 1842c ($18.43) | 1959c ($19.59) | 21.7% | 18 | False | needs_own_frozen_forward_birth, live_ready_false |
| 11 | `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_plus_approved_parent_fill + post_penalty_birth_bridge_cheap_penalty050_rank_only` | 83 | 68/15 | 82.2% | 1842c ($18.43) | 1959c ($19.59) | 21.7% | 18 | False | needs_own_frozen_forward_birth, live_ready_false |
| 12 | `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_plus_approved_parent_fill + post_penalty_birth_bridge_cheap_penalty100_rank_only` | 83 | 68/15 | 82.2% | 1842c ($18.43) | 1959c ($19.59) | 21.7% | 18 | False | needs_own_frozen_forward_birth, live_ready_false |
| 13 | `top_component_observable_quarantine_child` | `observable_quarantine_control` | 66 | 61/4 | 75.0% | 1828c ($18.27) | 1944c ($19.44) | 24.2% | 18 | False | diagnostic_or_prefreeze_context, not_strict_forward, live_ready_false |
| 14 | `top_component_observable_quarantine_child` | `weak_touch_quarter` | 66 | 61/4 | 75.0% | 1828c ($18.27) | 1944c ($19.44) | 24.2% | 18 | False | diagnostic_or_prefreeze_context, not_strict_forward, live_ready_false |
| 15 | `top_component_observable_quarantine_child` | `weak_touch_half` | 66 | 61/4 | 75.0% | 1828c ($18.27) | 1944c ($19.44) | 24.2% | 18 | False | diagnostic_or_prefreeze_context, not_strict_forward, live_ready_false |
| 16 | `top_component_observable_quarantine_child` | `weak_touch_zero` | 66 | 61/4 | 75.0% | 1828c ($18.27) | 1944c ($19.44) | 24.2% | 18 | False | diagnostic_or_prefreeze_context, not_strict_forward, live_ready_false |
| 17 | `top_component_observable_quarantine_child` | `very_weak_touch_zero` | 66 | 61/4 | 75.0% | 1828c ($18.27) | 1944c ($19.44) | 24.2% | 18 | False | diagnostic_or_prefreeze_context, not_strict_forward, live_ready_false |
| 18 | `top_component_observable_quarantine_child` | `smooth_weak_touch` | 66 | 61/4 | 75.0% | 1813c ($18.13) | 1930c ($19.30) | 24.2% | 18 | False | diagnostic_or_prefreeze_context, not_strict_forward, live_ready_false |
| 19 | `top_component_observable_quarantine_child` | `weak_boundary_quarter` | 66 | 61/4 | 75.0% | 1806c ($18.07) | 1923c ($19.23) | 24.2% | 18 | False | diagnostic_or_prefreeze_context, not_strict_forward, live_ready_false |
| 20 | `top_component_observable_quarantine_child` | `low_ask_quarter` | 66 | 61/4 | 75.0% | 1803c ($18.03) | 1920c ($19.20) | 24.2% | 18 | False | diagnostic_or_prefreeze_context, not_strict_forward, live_ready_false |
