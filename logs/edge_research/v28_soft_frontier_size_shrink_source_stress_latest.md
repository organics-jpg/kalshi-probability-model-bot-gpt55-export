# v28 Soft-Frontier Size-Shrink Source Stress

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T02:22:53.030366+00:00`
- Portfolio freeze UTC: `2026-05-07T01:52:52.999002+00:00`

## Interpretation

- Policy-specific audit only; no live logic changes and no promotion by itself.
- Diagnostic lanes remain diagnostic even when their source share is clean enough.
- Best stress row diagnostic_bridge_no_size_shrink_control has strict_forward=False, 56 settled, coverage 80.28169014084507%, net 700.0c, reconstructed share 0.3333333333333333, cushion 7, blockers ['diagnostic_only_prefreeze'].
- Best strict post-shrink row post_shrink_birth_entry_no_size_shrink_control has 0 settled, coverage 50.0%, net 0.0c, reconstructed share 0.0, blockers ['settled_lt_30', 'coverage_too_low', 'net_not_positive', 'full_loss_cushion_lt_3'].

## Policies

| policy | strict | settled | W/L | coverage | net c | recon | clean rows needed | cushion | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| diagnostic_bridge_no_size_shrink_control | False | 56 | 51/5 | 80.281690 | 700.000000 | 0.333333 | 0 | 7 | diagnostic_only_prefreeze |
| diagnostic_bridge_quarter_near_boundary_half_midcheap | False | 56 | 51/5 | 80.281690 | 690.000000 | 0.333333 | 0 | 6 | diagnostic_only_prefreeze |
| diagnostic_bridge_continuous_absd_ask_shrink | False | 56 | 51/5 | 80.281690 | 684.767012 | 0.333333 | 0 | 6 | diagnostic_only_prefreeze |
| diagnostic_bridge_half_near_boundary_or_midcheap | False | 56 | 51/5 | 80.281690 | 682.500000 | 0.333333 | 0 | 6 | diagnostic_only_prefreeze |
| diagnostic_entry_no_size_shrink_control | False | 48 | 44/4 | 80.821918 | 670.000000 | 0.338983 | 0 | 6 | diagnostic_only_prefreeze |
| diagnostic_entry_quarter_near_boundary_half_midcheap | False | 48 | 44/4 | 80.821918 | 660.000000 | 0.338983 | 0 | 6 | diagnostic_only_prefreeze |
| diagnostic_entry_half_near_boundary_or_midcheap | False | 48 | 44/4 | 80.821918 | 652.500000 | 0.338983 | 0 | 6 | diagnostic_only_prefreeze |
| diagnostic_bridge_continuous_plus_same_side_reentry_guard | False | 56 | 50/5 | 80.281690 | 645.267012 | 0.333333 | 0 | 6 | diagnostic_only_prefreeze |
| diagnostic_entry_continuous_absd_ask_shrink | False | 48 | 44/4 | 80.821918 | 637.046144 | 0.338983 | 0 | 6 | diagnostic_only_prefreeze |
| diagnostic_entry_continuous_plus_same_side_reentry_guard | False | 48 | 44/4 | 80.821918 | 620.546144 | 0.338983 | 0 | 6 | diagnostic_only_prefreeze |
| post_feature_freeze_entry_no_size_shrink_control | False | 26 | 23/3 | 77.142857 | 345.000000 | 0.370370 | 2 | 3 | diagnostic_only_prefreeze, settled_lt_30, reconstructed_share_gt_35pct |
| post_feature_freeze_entry_quarter_near_boundary_half_midcheap | False | 26 | 23/3 | 77.142857 | 335.000000 | 0.370370 | 2 | 3 | diagnostic_only_prefreeze, settled_lt_30, reconstructed_share_gt_35pct |
| post_feature_freeze_entry_half_near_boundary_or_midcheap | False | 26 | 23/3 | 77.142857 | 327.500000 | 0.370370 | 2 | 3 | diagnostic_only_prefreeze, settled_lt_30, reconstructed_share_gt_35pct |
| post_feature_freeze_entry_continuous_absd_ask_shrink | False | 26 | 23/3 | 77.142857 | 324.923607 | 0.370370 | 2 | 3 | diagnostic_only_prefreeze, settled_lt_30, reconstructed_share_gt_35pct |
| post_feature_freeze_entry_continuous_plus_same_side_reentry_guard | False | 26 | 23/3 | 77.142857 | 308.423607 | 0.370370 | 2 | 3 | diagnostic_only_prefreeze, settled_lt_30, reconstructed_share_gt_35pct |
| post_soft_frontier_birth_entry_quarter_near_boundary_half_midcheap | False | 18 | 15/3 | 80.000000 | 237.250000 | 0.400000 | 3 | 2 | diagnostic_only_prefreeze, settled_lt_30, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| post_soft_frontier_birth_entry_continuous_absd_ask_shrink | False | 18 | 15/3 | 80.000000 | 221.673607 | 0.400000 | 3 | 2 | diagnostic_only_prefreeze, settled_lt_30, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| post_soft_frontier_birth_entry_half_near_boundary_or_midcheap | False | 18 | 15/3 | 80.000000 | 216.000000 | 0.400000 | 3 | 2 | diagnostic_only_prefreeze, settled_lt_30, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| post_soft_frontier_birth_entry_continuous_plus_same_side_reentry_guard | False | 18 | 15/3 | 80.000000 | 205.173607 | 0.400000 | 3 | 2 | diagnostic_only_prefreeze, settled_lt_30, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| post_soft_frontier_birth_entry_no_size_shrink_control | False | 18 | 15/3 | 80.000000 | 178.000000 | 0.400000 | 3 | 1 | diagnostic_only_prefreeze, settled_lt_30, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| post_shrink_birth_entry_no_size_shrink_control | True | 0 | 0/0 | 50.000000 | 0.000000 | 0.000000 | 0 | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3 |
| post_shrink_birth_entry_half_near_boundary_or_midcheap | True | 0 | 0/0 | 50.000000 | 0.000000 | 0.000000 | 0 | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3 |
| post_shrink_birth_entry_quarter_near_boundary_half_midcheap | True | 0 | 0/0 | 50.000000 | 0.000000 | 0.000000 | 0 | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3 |
| post_shrink_birth_entry_continuous_absd_ask_shrink | True | 0 | 0/0 | 50.000000 | 0.000000 | 0.000000 | 0 | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3 |
| post_shrink_birth_entry_continuous_plus_same_side_reentry_guard | True | 0 | 0/0 | 50.000000 | 0.000000 | 0.000000 | 0 | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3 |
| post_shrink_birth_bridge_no_size_shrink_control | True | 0 | 0/0 | 50.000000 | 0.000000 | 0.000000 | 0 | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3 |
| post_shrink_birth_bridge_half_near_boundary_or_midcheap | True | 0 | 0/0 | 50.000000 | 0.000000 | 0.000000 | 0 | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3 |
| post_shrink_birth_bridge_quarter_near_boundary_half_midcheap | True | 0 | 0/0 | 50.000000 | 0.000000 | 0.000000 | 0 | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3 |
| post_shrink_birth_bridge_continuous_absd_ask_shrink | True | 0 | 0/0 | 50.000000 | 0.000000 | 0.000000 | 0 | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3 |
| post_shrink_birth_bridge_continuous_plus_same_side_reentry_guard | True | 0 | 0/0 | 50.000000 | 0.000000 | 0.000000 | 0 | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3 |
