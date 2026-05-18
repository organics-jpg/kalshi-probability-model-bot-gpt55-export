# v28 Soft-Frontier Mid-Price Boundary Source Stress

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:47:50.600665+00:00`
- Candidate freeze UTC: `2026-05-07T02:56:19.287272+00:00`
- Official gate note: Promotion source quality remains row-count reconstructed share <=35%; weighted exposure share is diagnostic account-risk evidence only.

## Interpretation

- Policy-specific audit only; no live logic changes and no promotion by itself.
- Weighted reconstructed exposure can support the account-risk argument, but it does not replace the official row-count source gate.
- Best stress row diagnostic_entry_quarter_midprice_boundary has strict_forward=False, 78 settled, coverage 78.21782178217822%, net 788.5c, row reconstructed share 0.3670886075949367, weighted reconstructed exposure share 0.3485342019543974, cushion 7, blockers ['diagnostic_only_prefreeze', 'row_reconstructed_share_gt_35pct'].
- Best strict post-birth row post_midprice_shrink_birth_entry_control_no_shrink has 36 settled, net -46.0c, row reconstructed share 0.4166666666666667, weighted reconstructed exposure share 0.4166666666666667, blockers ['net_not_positive', 'row_reconstructed_share_gt_35pct', 'weighted_reconstructed_exposure_gt_35pct', 'full_loss_cushion_lt_3'].
- Exposure-only near miss: diagnostic_entry_quarter_midprice_boundary has row reconstructed share 0.3670886075949367 but weighted exposure share 0.3485342019543974 at 78 settled and 788.5c.

## Policies

| policy | strict | settled | W/L | coverage | net c | row recon | weighted recon exposure | clean rows needed | cushion | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| diagnostic_entry_quarter_midprice_boundary | False | 78 | 68/10 | 78.217822 | 788.500000 | 0.367089 | 0.348534 | 4 | 7 | diagnostic_only_prefreeze, row_reconstructed_share_gt_35pct |
| diagnostic_bridge_quarter_midprice_boundary | False | 76 | 66/10 | 77.777778 | 738.500000 | 0.363636 | 0.344482 | 3 | 7 | diagnostic_only_prefreeze, row_reconstructed_share_gt_35pct |
| diagnostic_entry_half_midprice_boundary | False | 78 | 68/10 | 78.217822 | 765.000000 | 0.367089 | 0.354839 | 4 | 7 | diagnostic_only_prefreeze, row_reconstructed_share_gt_35pct, weighted_reconstructed_exposure_gt_35pct |
| diagnostic_entry_control_no_shrink | False | 78 | 68/10 | 78.217822 | 718.000000 | 0.367089 | 0.367089 | 4 | 7 | diagnostic_only_prefreeze, row_reconstructed_share_gt_35pct, weighted_reconstructed_exposure_gt_35pct |
| diagnostic_bridge_half_midprice_boundary | False | 76 | 66/10 | 77.777778 | 715.000000 | 0.363636 | 0.350993 | 3 | 7 | diagnostic_only_prefreeze, row_reconstructed_share_gt_35pct, weighted_reconstructed_exposure_gt_35pct |
| diagnostic_bridge_control_no_shrink | False | 76 | 66/10 | 77.777778 | 668.000000 | 0.363636 | 0.363636 | 3 | 6 | diagnostic_only_prefreeze, row_reconstructed_share_gt_35pct, weighted_reconstructed_exposure_gt_35pct |
| post_feature_freeze_entry_quarter_midprice_boundary | False | 46 | 38/8 | 75.806452 | 381.500000 | 0.404255 | 0.374302 | 8 | 3 | diagnostic_only_prefreeze, row_reconstructed_share_gt_35pct, weighted_reconstructed_exposure_gt_35pct |
| post_feature_freeze_entry_half_midprice_boundary | False | 46 | 38/8 | 75.806452 | 358.000000 | 0.404255 | 0.384615 | 8 | 3 | diagnostic_only_prefreeze, row_reconstructed_share_gt_35pct, weighted_reconstructed_exposure_gt_35pct |
| post_feature_freeze_entry_control_no_shrink | False | 46 | 38/8 | 75.806452 | 311.000000 | 0.404255 | 0.404255 | 8 | 3 | diagnostic_only_prefreeze, row_reconstructed_share_gt_35pct, weighted_reconstructed_exposure_gt_35pct |
| post_soft_frontier_birth_entry_quarter_midprice_boundary | False | 39 | 31/8 | 76.923077 | 274.500000 | 0.425000 | 0.390728 | 9 | 2 | diagnostic_only_prefreeze, row_reconstructed_share_gt_35pct, weighted_reconstructed_exposure_gt_35pct, full_loss_cushion_lt_3 |
| post_soft_frontier_birth_entry_half_midprice_boundary | False | 39 | 31/8 | 76.923077 | 251.000000 | 0.425000 | 0.402597 | 9 | 2 | diagnostic_only_prefreeze, row_reconstructed_share_gt_35pct, weighted_reconstructed_exposure_gt_35pct, full_loss_cushion_lt_3 |
| post_soft_frontier_birth_entry_control_no_shrink | False | 39 | 31/8 | 76.923077 | 204.000000 | 0.425000 | 0.425000 | 9 | 2 | diagnostic_only_prefreeze, row_reconstructed_share_gt_35pct, weighted_reconstructed_exposure_gt_35pct, full_loss_cushion_lt_3 |
| post_midprice_shrink_birth_entry_control_no_shrink | True | 36 | 28/8 | 80.000000 | -46.000000 | 0.416667 | 0.416667 | 7 | 0 | net_not_positive, row_reconstructed_share_gt_35pct, weighted_reconstructed_exposure_gt_35pct, full_loss_cushion_lt_3 |
| post_midprice_shrink_birth_entry_half_midprice_boundary | True | 36 | 28/8 | 80.000000 | -65.500000 | 0.416667 | 0.408451 | 7 | 0 | net_not_positive, row_reconstructed_share_gt_35pct, weighted_reconstructed_exposure_gt_35pct, full_loss_cushion_lt_3 |
| post_midprice_shrink_birth_entry_quarter_midprice_boundary | True | 36 | 28/8 | 80.000000 | -75.250000 | 0.416667 | 0.404255 | 7 | 0 | net_not_positive, row_reconstructed_share_gt_35pct, weighted_reconstructed_exposure_gt_35pct, full_loss_cushion_lt_3 |
