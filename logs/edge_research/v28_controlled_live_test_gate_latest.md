# v28 Controlled Live-Test Gate

Research-only. This probe does not place orders or edit live bot logic.

- Generated UTC: `2026-05-11T03:08:58.238337+00:00`
- Decision: `no_live_test`
- Live baseline: `-117c` from `live_mushroom_v28_size2` / `live_only`
- Open live positions: `0`
- Candidate rows: `995`
- Broad eligible: `0`
- Sidecar eligible: `0`

## Interpretation

- No candidate clears the controlled live-test gates; do not place live candidate trades.
- Closest broad row is top_component_false_negative_rescue_child / diagnostic_approved_union_rebound with net 2102.5c, W/L 67/9, coverage 75.24752475247524%, and missing gates ['live_ready_false', 'not_strict_forward', 'diagnostic_prefreeze'].
- Closest sidecar row is boundary_clock_feature_gate_continuous_penalty / post_penalty_birth_bridge_cheap_penalty025_rank_only with net 504.0c, W/L 41/10, source share 0.17647058823529413, and missing gates ['live_ready_false', 'coverage_too_low'].
- Top PnL row remains top_component_parent_fill_repair_child / diagnostic_observable_mid_confidence_parent_fill_quarter at 2233.0c, but missing gates are ['live_ready_false', 'not_strict_forward', 'diagnostic_prefreeze', 'source_gate_zero_row_margin'].

## Broad Eligible

| gate | policy | settled | W/L | coverage | net | delta live | recon | cushion | missing gates |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|

## Sidecar Eligible

| gate | policy | settled | W/L | coverage | net | delta live | recon | cushion | missing gates |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|

## Closest Broad Rows

| gate | policy | settled | W/L | coverage | net | delta live | recon | cushion | missing gates |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `top_component_false_negative_rescue_child` | `diagnostic_approved_union_rebound` | 76 | 67/9 | 75.25% | 2102c | 2219c | 34.21% | 21 | live_ready_false, not_strict_forward, diagnostic_prefreeze |
| `top_component_false_negative_rescue_child` | `diagnostic_union_rebound` | 76 | 67/9 | 75.25% | 2102c | 2219c | 34.21% | 21 | live_ready_false, not_strict_forward, diagnostic_prefreeze |
| `top_component_false_negative_rescue_child` | `diagnostic_low_exit_collapse_rebound` | 76 | 66/10 | 75.25% | 2008c | 2125c | 34.21% | 20 | live_ready_false, not_strict_forward, diagnostic_prefreeze |
| `top_component_false_negative_rescue_child` | `diagnostic_mid_recheck_value_rebound` | 76 | 66/10 | 75.25% | 1926c | 2043c | 34.21% | 19 | live_ready_false, not_strict_forward, diagnostic_prefreeze |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty025_rank_only` | 83 | 68/15 | 82.18% | 1842c | 1959c | 21.69% | 18 | live_ready_false, not_strict_forward, needs_own_frozen_forward_birth |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty050_rank_only` | 83 | 68/15 | 82.18% | 1842c | 1959c | 21.69% | 18 | live_ready_false, not_strict_forward, needs_own_frozen_forward_birth |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty100_rank_only` | 83 | 68/15 | 82.18% | 1842c | 1959c | 21.69% | 18 | live_ready_false, not_strict_forward, needs_own_frozen_forward_birth |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_entry_cheap_penalty025_rank_only` | 83 | 68/15 | 82.18% | 1842c | 1959c | 21.69% | 18 | live_ready_false, not_strict_forward, needs_own_frozen_forward_birth |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_entry_cheap_penalty050_rank_only` | 83 | 68/15 | 82.18% | 1842c | 1959c | 21.69% | 18 | live_ready_false, not_strict_forward, needs_own_frozen_forward_birth |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_entry_cheap_penalty100_rank_only` | 83 | 68/15 | 82.18% | 1842c | 1959c | 21.69% | 18 | live_ready_false, not_strict_forward, needs_own_frozen_forward_birth |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_plus_approved_parent_fill + post_penalty_birth_bridge_cheap_penalty025_rank_only` | 83 | 68/15 | 82.18% | 1842c | 1959c | 21.69% | 18 | live_ready_false, not_strict_forward, needs_own_frozen_forward_birth |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_plus_approved_parent_fill + post_penalty_birth_bridge_cheap_penalty050_rank_only` | 83 | 68/15 | 82.18% | 1842c | 1959c | 21.69% | 18 | live_ready_false, not_strict_forward, needs_own_frozen_forward_birth |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_plus_approved_parent_fill + post_penalty_birth_bridge_cheap_penalty100_rank_only` | 83 | 68/15 | 82.18% | 1842c | 1959c | 21.69% | 18 | live_ready_false, not_strict_forward, needs_own_frozen_forward_birth |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_plus_approved_parent_fill + post_penalty_birth_entry_cheap_penalty025_rank_only` | 83 | 68/15 | 82.18% | 1842c | 1959c | 21.69% | 18 | live_ready_false, not_strict_forward, needs_own_frozen_forward_birth |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_plus_approved_parent_fill + post_penalty_birth_entry_cheap_penalty050_rank_only` | 83 | 68/15 | 82.18% | 1842c | 1959c | 21.69% | 18 | live_ready_false, not_strict_forward, needs_own_frozen_forward_birth |

## Closest Sidecar Rows

| gate | policy | settled | W/L | coverage | net | delta live | recon | cushion | missing gates |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_bridge_cheap_penalty025_rank_only` | 51 | 41/10 | 66.23% | 504c | 621c | 17.65% | 5 | live_ready_false, coverage_too_low |
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_bridge_cheap_penalty050_rank_only` | 51 | 41/10 | 66.23% | 504c | 621c | 17.65% | 5 | live_ready_false, coverage_too_low |
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_bridge_cheap_penalty100_rank_only` | 51 | 41/10 | 66.23% | 504c | 621c | 17.65% | 5 | live_ready_false, coverage_too_low |
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_entry_cheap_penalty025_rank_only` | 51 | 41/10 | 66.23% | 504c | 621c | 17.65% | 5 | live_ready_false, coverage_too_low |
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_entry_cheap_penalty050_rank_only` | 51 | 41/10 | 66.23% | 504c | 621c | 17.65% | 5 | live_ready_false, coverage_too_low |
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_entry_cheap_penalty100_rank_only` | 51 | 41/10 | 66.23% | 504c | 621c | 17.65% | 5 | live_ready_false, coverage_too_low |
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_bridge_cheap_penalty050_floor05` | 44 | 40/4 | 57.14% | 443c | 560c | 4.55% | 4 | live_ready_false, coverage_too_low |
| `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_entry_cheap_penalty050_floor05` | 44 | 40/4 | 57.14% | 443c | 560c | 4.55% | 4 | live_ready_false, coverage_too_low |
| `approved_entry_book_raw_blend_fv` | `book_raw_blend_alpha_0p50` | 55 | 47/8 | n/a | 362c | 479c | n/a | 3 | not_strict_forward, source_share_unknown |
| `feature_gate_core_expansion_mix` | `core_only` | 40 | 36/4 | 48.78% | 357c | 474c | 5.00% | 3 | live_ready_false, coverage_outside_target |
| `feature_gate_core_expansion_mix` | `skip_source_thin_cheap_else_half` | 60 | 42/18 | 73.17% | 345c | 462c | 35.00% | 3 | live_ready_false, coverage_outside_target |
| `feature_gate_core_expansion_mix` | `skip_thin_cheap_else_half` | 60 | 42/18 | 73.17% | 345c | 462c | 35.00% | 3 | live_ready_false, coverage_outside_target |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty025_rank_only` | 83 | 68/15 | 82.18% | 1842c | 1959c | 21.69% | 18 | live_ready_false, not_strict_forward, needs_own_frozen_forward_birth |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty050_rank_only` | 83 | 68/15 | 82.18% | 1842c | 1959c | 21.69% | 18 | live_ready_false, not_strict_forward, needs_own_frozen_forward_birth |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty100_rank_only` | 83 | 68/15 | 82.18% | 1842c | 1959c | 21.69% | 18 | live_ready_false, not_strict_forward, needs_own_frozen_forward_birth |

## Top PnL Reference

| gate | policy | settled | W/L | coverage | net | delta live | recon | cushion | missing gates |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `top_component_parent_fill_repair_child` | `diagnostic_observable_mid_confidence_parent_fill_quarter` | 76 | 67/9 | 75.25% | 2233c | 2350c | 34.21% | 22 | live_ready_false, not_strict_forward, diagnostic_prefreeze, source_gate_zero_row_margin |
| `top_component_parent_fill_repair_child` | `diagnostic_mid_confidence_parent_fill_quarter` | 76 | 67/9 | 75.25% | 2233c | 2350c | 34.21% | 22 | live_ready_false, not_strict_forward, diagnostic_prefreeze, source_label_diagnostic, source_gate_zero_row_margin |
| `top_component_parent_fill_repair_child` | `diagnostic_observable_mid_confidence_parent_fill_half` | 76 | 67/9 | 75.25% | 2190c | 2306c | 34.21% | 21 | live_ready_false, not_strict_forward, diagnostic_prefreeze, source_gate_zero_row_margin |
| `top_component_parent_fill_repair_child` | `diagnostic_mid_confidence_parent_fill_half` | 76 | 67/9 | 75.25% | 2190c | 2306c | 34.21% | 21 | live_ready_false, not_strict_forward, diagnostic_prefreeze, source_label_diagnostic, source_gate_zero_row_margin |
| `top_component_parent_fill_repair_child` | `diagnostic_parent_fill_wide_mid_absd_ask_notch` | 76 | 67/9 | 75.25% | 2145c | 2262c | 34.21% | 21 | live_ready_false, not_strict_forward, diagnostic_prefreeze, source_gate_zero_row_margin |
| `top_component_parent_fill_repair_child` | `diagnostic_parent_fill_mid_absd_ask_notch` | 76 | 67/9 | 75.25% | 2142c | 2259c | 34.21% | 21 | live_ready_false, not_strict_forward, diagnostic_prefreeze, source_gate_zero_row_margin |
| `top_component_parent_fill_repair_child` | `diagnostic_smooth_parent_fill_source_risk` | 76 | 67/9 | 75.25% | 2127c | 2244c | 34.21% | 21 | live_ready_false, not_strict_forward, diagnostic_prefreeze, source_label_diagnostic, source_gate_zero_row_margin |
| `top_component_false_negative_rescue_child` | `diagnostic_union_rebound` | 76 | 67/9 | 75.25% | 2102c | 2219c | 34.21% | 21 | live_ready_false, not_strict_forward, diagnostic_prefreeze |
| `top_component_false_negative_rescue_child` | `diagnostic_approved_union_rebound` | 76 | 67/9 | 75.25% | 2102c | 2219c | 34.21% | 21 | live_ready_false, not_strict_forward, diagnostic_prefreeze |
| `top_component_parent_fill_repair_child` | `diagnostic_exit_child_only_control` | 76 | 67/9 | 75.25% | 2102c | 2219c | 34.21% | 21 | live_ready_false, not_strict_forward, diagnostic_prefreeze, source_gate_zero_row_margin |
| `top_component_parent_fill_repair_child` | `diagnostic_parent_fill_all_rejected_half` | 76 | 67/9 | 75.25% | 2095c | 2212c | 34.21% | 20 | live_ready_false, not_strict_forward, diagnostic_prefreeze, source_label_diagnostic, source_gate_zero_row_margin |
| `top_component_parent_fill_repair_child` | `diagnostic_parent_fill_all_rejected_quarter` | 76 | 67/9 | 75.25% | 2091c | 2208c | 34.21% | 20 | live_ready_false, not_strict_forward, diagnostic_prefreeze, source_label_diagnostic, source_gate_zero_row_margin |