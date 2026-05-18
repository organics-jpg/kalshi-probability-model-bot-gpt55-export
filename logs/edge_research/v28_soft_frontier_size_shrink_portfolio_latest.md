# v28 Soft-Frontier Size-Shrink Portfolio

Research-only. No live bot logic changed and no orders placed.

- Generated UTC: `2026-05-07T12:26:47.374141+00:00`
- Freeze UTC: `2026-05-07T01:52:52.999002+00:00`

## Interpretation

- This is a size/risk overlay, not a new hard entry cutoff.
- Only post_shrink_birth lanes are strict forward evidence for this candidate family.
- diagnostic_entry: best diagnostic_entry_continuous_absd_ask_shrink settled 78, coverage 78.21782178217822%, active coverage 78.21782178217822%, net 754.0363495238095c, raw 718.0c, avg weight 0.8671322362869198, recon 0.3670886075949367, tags {'higher_recross_gt_030': 24, 'collapse_same_side_reentry': 3, 'collapse_thin_edge_reentry': 4, 'thin_raw_edge_lt_005': 10, 'near_boundary_absd_lt_065': 9, 'mid_cheap_ask_lt_050': 5}, blockers ['diagnostic_only_prefreeze', 'reconstructed_share_gt_35pct'].
- diagnostic_bridge: best diagnostic_bridge_continuous_absd_ask_shrink settled 76, coverage 77.77777777777777%, active coverage 77.77777777777777%, net 721.757218095238c, raw 668.0c, avg weight 0.8708730364873222, recon 0.36363636363636365, tags {'collapse_same_side_reentry': 3, 'collapse_thin_edge_reentry': 4, 'higher_recross_gt_030': 23, 'thin_raw_edge_lt_005': 10, 'near_boundary_absd_lt_065': 9, 'mid_cheap_ask_lt_050': 5}, blockers ['diagnostic_only_prefreeze', 'reconstructed_share_gt_35pct'].
- post_feature_freeze_entry: best post_feature_freeze_entry_continuous_absd_ask_shrink settled 46, coverage 75.80645161290323%, active coverage 75.80645161290323%, net 359.9138123809524c, raw 311.0c, avg weight 0.8114206281661601, recon 0.40425531914893614, tags {'near_boundary_absd_lt_065': 9, 'thin_raw_edge_lt_005': 5, 'higher_recross_gt_030': 8, 'mid_cheap_ask_lt_050': 5, 'collapse_thin_edge_reentry': 2, 'collapse_same_side_reentry': 2}, blockers ['diagnostic_only_prefreeze', 'reconstructed_share_gt_35pct'].
- post_soft_frontier_birth_entry: best post_soft_frontier_birth_entry_continuous_absd_ask_shrink settled 39, coverage 76.92307692307692%, active coverage 76.92307692307692%, net 288.6638123809524c, raw 204.0c, avg weight 0.8109192380952381, recon 0.425, tags {'higher_recross_gt_030': 7, 'mid_cheap_ask_lt_050': 5, 'near_boundary_absd_lt_065': 7, 'collapse_thin_edge_reentry': 2, 'thin_raw_edge_lt_005': 3, 'collapse_same_side_reentry': 2}, blockers ['diagnostic_only_prefreeze', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].
- post_shrink_birth_entry: best post_shrink_birth_entry_continuous_absd_ask_shrink settled 20, coverage 72.41379310344827%, active coverage 72.41379310344827%, net 60.99020571428571c, raw -8.0c, avg weight 0.818818231292517, recon 0.42857142857142855, tags {'higher_recross_gt_030': 4, 'collapse_same_side_reentry': 2, 'near_boundary_absd_lt_065': 4, 'thin_raw_edge_lt_005': 2, 'collapse_thin_edge_reentry': 1, 'mid_cheap_ask_lt_050': 1}, blockers ['settled_lt_30', 'coverage_too_low', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].
- post_shrink_birth_bridge: best post_shrink_birth_bridge_continuous_absd_ask_shrink settled 20, coverage 72.41379310344827%, active coverage 72.41379310344827%, net 60.99020571428571c, raw -8.0c, avg weight 0.818818231292517, recon 0.42857142857142855, tags {'higher_recross_gt_030': 4, 'collapse_same_side_reentry': 2, 'near_boundary_absd_lt_065': 4, 'thin_raw_edge_lt_005': 2, 'collapse_thin_edge_reentry': 1, 'mid_cheap_ask_lt_050': 1}, blockers ['settled_lt_30', 'coverage_too_low', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].

## Lanes

| lane | strict | best policy | settled | W/L | coverage | active cov | net | raw net | avg weight | recon | blockers |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| diagnostic_entry | False | `continuous_absd_ask_shrink` | 78 | 68/10 | 78.22% | 78.22% | 754c ($7.54) | 718c ($7.18) | 86.71% | 36.71% | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| diagnostic_bridge | False | `continuous_absd_ask_shrink` | 76 | 66/10 | 77.78% | 77.78% | 722c ($7.22) | 668c ($6.68) | 87.09% | 36.36% | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| post_feature_freeze_entry | False | `continuous_absd_ask_shrink` | 46 | 38/8 | 75.81% | 75.81% | 360c ($3.60) | 311c ($3.11) | 81.14% | 40.43% | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| post_soft_frontier_birth_entry | False | `continuous_absd_ask_shrink` | 39 | 31/8 | 76.92% | 76.92% | 289c ($2.89) | 204c ($2.04) | 81.09% | 42.50% | diagnostic_only_prefreeze, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| post_shrink_birth_entry | True | `continuous_absd_ask_shrink` | 20 | 15/5 | 72.41% | 72.41% | 61c ($0.61) | -8c ($-0.08) | 81.88% | 42.86% | settled_lt_30, coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| post_shrink_birth_bridge | True | `continuous_absd_ask_shrink` | 20 | 15/5 | 72.41% | 72.41% | 61c ($0.61) | -8c ($-0.08) | 81.88% | 42.86% | settled_lt_30, coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

## Variant Detail

### diagnostic_entry

| policy | settled | W/L | coverage | active cov | net | delta vs raw | avg weight | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `continuous_absd_ask_shrink` | 78 | 68/10 | 78.22% | 78.22% | 754c ($7.54) | 36c ($0.36) | 86.71% | 7 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| `quarter_near_boundary_half_midcheap` | 78 | 68/10 | 78.22% | 78.22% | 738c ($7.38) | 20c ($0.20) | 89.56% | 7 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| `half_near_boundary_or_midcheap` | 78 | 68/10 | 78.22% | 78.22% | 720c ($7.21) | 2c ($0.03) | 92.41% | 7 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| `no_size_shrink_control` | 78 | 68/10 | 78.22% | 78.22% | 718c ($7.18) | 0c ($0.00) | 100.00% | 7 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| `continuous_plus_same_side_reentry_guard` | 78 | 67/10 | 78.22% | 77.23% | 707c ($7.07) | -11c ($-0.11) | 84.18% | 7 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |

### diagnostic_bridge

| policy | settled | W/L | coverage | active cov | net | delta vs raw | avg weight | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `continuous_absd_ask_shrink` | 76 | 66/10 | 77.78% | 77.78% | 722c ($7.22) | 54c ($0.54) | 87.09% | 7 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| `quarter_near_boundary_half_midcheap` | 76 | 66/10 | 77.78% | 77.78% | 688c ($6.88) | 20c ($0.20) | 89.29% | 6 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| `continuous_plus_same_side_reentry_guard` | 76 | 65/10 | 77.78% | 76.77% | 675c ($6.75) | 7c ($0.07) | 84.49% | 6 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| `half_near_boundary_or_midcheap` | 76 | 66/10 | 77.78% | 77.78% | 670c ($6.71) | 2c ($0.03) | 92.21% | 6 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| `no_size_shrink_control` | 76 | 66/10 | 77.78% | 77.78% | 668c ($6.68) | 0c ($0.00) | 100.00% | 6 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |

### post_feature_freeze_entry

| policy | settled | W/L | coverage | active cov | net | delta vs raw | avg weight | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `continuous_absd_ask_shrink` | 46 | 38/8 | 75.81% | 75.81% | 360c ($3.60) | 49c ($0.49) | 81.14% | 3 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| `continuous_plus_same_side_reentry_guard` | 46 | 38/8 | 75.81% | 75.81% | 336c ($3.36) | 25c ($0.25) | 79.01% | 3 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| `quarter_near_boundary_half_midcheap` | 46 | 38/8 | 75.81% | 75.81% | 331c ($3.31) | 20c ($0.20) | 82.45% | 3 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| `half_near_boundary_or_midcheap` | 46 | 38/8 | 75.81% | 75.81% | 314c ($3.13) | 2c ($0.03) | 87.23% | 3 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| `no_size_shrink_control` | 46 | 38/8 | 75.81% | 75.81% | 311c ($3.11) | 0c ($0.00) | 100.00% | 3 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |

### post_soft_frontier_birth_entry

| policy | settled | W/L | coverage | active cov | net | delta vs raw | avg weight | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `continuous_absd_ask_shrink` | 39 | 31/8 | 76.92% | 76.92% | 289c ($2.89) | 85c ($0.85) | 81.09% | 2 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `quarter_near_boundary_half_midcheap` | 39 | 31/8 | 76.92% | 76.92% | 265c ($2.65) | 61c ($0.61) | 83.12% | 2 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `continuous_plus_same_side_reentry_guard` | 39 | 31/8 | 76.92% | 76.92% | 265c ($2.65) | 61c ($0.61) | 78.59% | 2 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `half_near_boundary_or_midcheap` | 39 | 31/8 | 76.92% | 76.92% | 234c ($2.34) | 30c ($0.30) | 87.50% | 2 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `no_size_shrink_control` | 39 | 31/8 | 76.92% | 76.92% | 204c ($2.04) | 0c ($0.00) | 100.00% | 2 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

### post_shrink_birth_entry

| policy | settled | W/L | coverage | active cov | net | delta vs raw | avg weight | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `continuous_absd_ask_shrink` | 20 | 15/5 | 72.41% | 72.41% | 61c ($0.61) | 69c ($0.69) | 81.88% | 0 | settled_lt_30, coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `continuous_plus_same_side_reentry_guard` | 20 | 15/5 | 72.41% | 72.41% | 37c ($0.37) | 45c ($0.45) | 77.12% | 0 | settled_lt_30, coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `quarter_near_boundary_half_midcheap` | 20 | 15/5 | 72.41% | 72.41% | 22c ($0.22) | 30c ($0.30) | 85.71% | 0 | settled_lt_30, coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `half_near_boundary_or_midcheap` | 20 | 15/5 | 72.41% | 72.41% | 12c ($0.12) | 20c ($0.20) | 90.48% | 0 | settled_lt_30, coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `no_size_shrink_control` | 20 | 15/5 | 72.41% | 72.41% | -8c ($-0.08) | 0c ($0.00) | 100.00% | 0 | settled_lt_30, coverage_too_low, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

### post_shrink_birth_bridge

| policy | settled | W/L | coverage | active cov | net | delta vs raw | avg weight | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `continuous_absd_ask_shrink` | 20 | 15/5 | 72.41% | 72.41% | 61c ($0.61) | 69c ($0.69) | 81.88% | 0 | settled_lt_30, coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `continuous_plus_same_side_reentry_guard` | 20 | 15/5 | 72.41% | 72.41% | 37c ($0.37) | 45c ($0.45) | 77.12% | 0 | settled_lt_30, coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `quarter_near_boundary_half_midcheap` | 20 | 15/5 | 72.41% | 72.41% | 22c ($0.22) | 30c ($0.30) | 85.71% | 0 | settled_lt_30, coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `half_near_boundary_or_midcheap` | 20 | 15/5 | 72.41% | 72.41% | 12c ($0.12) | 20c ($0.20) | 90.48% | 0 | settled_lt_30, coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `no_size_shrink_control` | 20 | 15/5 | 72.41% | 72.41% | -8c ($-0.08) | 0c ($0.00) | 100.00% | 0 | settled_lt_30, coverage_too_low, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

