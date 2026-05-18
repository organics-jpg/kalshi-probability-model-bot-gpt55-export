# v28 Soft-Frontier Mid-Price Boundary Shrink Watch

Research-only. No live bot logic changed and no orders placed.

- Generated UTC: `2026-05-11T02:47:50.270631+00:00`
- Freeze UTC: `2026-05-07T02:56:19.287272+00:00`

## Interpretation

- This freezes a continuous size/risk overlay, not a new hard entry cutoff.
- Only post_midprice_shrink_birth lanes are strict forward evidence for this candidate family.
- diagnostic_entry: best diagnostic_entry_quarter_midprice_boundary settled 78, coverage 78.21782178217822%, active coverage 78.21782178217822%, net 788.5c, raw 718.0c, band rows 3 raw/weighted -94.0/-23.5c, recon 0.3670886075949367, blockers ['diagnostic_only_prefreeze', 'reconstructed_share_gt_35pct'].
- diagnostic_bridge: best diagnostic_bridge_quarter_midprice_boundary settled 76, coverage 77.77777777777777%, active coverage 77.77777777777777%, net 738.5c, raw 668.0c, band rows 3 raw/weighted -94.0/-23.5c, recon 0.36363636363636365, blockers ['diagnostic_only_prefreeze', 'reconstructed_share_gt_35pct'].
- post_feature_freeze_entry: best post_feature_freeze_entry_quarter_midprice_boundary settled 46, coverage 75.80645161290323%, active coverage 75.80645161290323%, net 381.5c, raw 311.0c, band rows 3 raw/weighted -94.0/-23.5c, recon 0.40425531914893614, blockers ['diagnostic_only_prefreeze', 'reconstructed_share_gt_35pct'].
- post_soft_frontier_birth_entry: best post_soft_frontier_birth_entry_quarter_midprice_boundary settled 39, coverage 76.92307692307692%, active coverage 76.92307692307692%, net 274.5c, raw 204.0c, band rows 3 raw/weighted -94.0/-23.5c, recon 0.425, blockers ['diagnostic_only_prefreeze', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].
- post_midprice_shrink_birth_entry: best post_midprice_shrink_birth_entry_control_no_shrink settled 36, coverage 80.0%, active coverage 80.0%, net -46.0c, raw -46.0c, band rows 1 raw/weighted 39.0/39.0c, recon 0.4166666666666667, blockers ['net_not_positive', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].

## Lanes

| lane | strict | best policy | settled | W/L | coverage | active cov | net | raw net | band rows | band raw/weighted | avg weight | recon | blockers |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| diagnostic_entry | False | `quarter_midprice_boundary` | 78 | 68/10 | 78.22% | 78.22% | 788c ($7.88) | 718c ($7.18) | 3 | -94c ($-0.94)/-24c ($-0.23) | 97.15% | 36.71% | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| diagnostic_bridge | False | `quarter_midprice_boundary` | 76 | 66/10 | 77.78% | 77.78% | 738c ($7.38) | 668c ($6.68) | 3 | -94c ($-0.94)/-24c ($-0.23) | 97.08% | 36.36% | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| post_feature_freeze_entry | False | `quarter_midprice_boundary` | 46 | 38/8 | 75.81% | 75.81% | 382c ($3.81) | 311c ($3.11) | 3 | -94c ($-0.94)/-24c ($-0.23) | 95.21% | 40.43% | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| post_soft_frontier_birth_entry | False | `quarter_midprice_boundary` | 39 | 31/8 | 76.92% | 76.92% | 274c ($2.75) | 204c ($2.04) | 3 | -94c ($-0.94)/-24c ($-0.23) | 94.38% | 42.50% | diagnostic_only_prefreeze, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| post_midprice_shrink_birth_entry | True | `control_no_shrink` | 36 | 28/8 | 80.00% | 80.00% | -46c ($-0.46) | -46c ($-0.46) | 1 | 39c ($0.39)/39c ($0.39) | 100.00% | 41.67% | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

## Variant Detail

### diagnostic_entry

| policy | settled | W/L | coverage | active cov | net | delta vs raw | band rows | band raw/weighted | avg weight | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `quarter_midprice_boundary` | 78 | 68/10 | 78.22% | 78.22% | 788c ($7.88) | 70c ($0.70) | 3 | -94c ($-0.94)/-24c ($-0.23) | 97.15% | 7 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| `half_midprice_boundary` | 78 | 68/10 | 78.22% | 78.22% | 765c ($7.65) | 47c ($0.47) | 3 | -94c ($-0.94)/-47c ($-0.47) | 98.10% | 7 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| `control_no_shrink` | 78 | 68/10 | 78.22% | 78.22% | 718c ($7.18) | 0c ($0.00) | 3 | -94c ($-0.94)/-94c ($-0.94) | 100.00% | 7 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |

### diagnostic_bridge

| policy | settled | W/L | coverage | active cov | net | delta vs raw | band rows | band raw/weighted | avg weight | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `quarter_midprice_boundary` | 76 | 66/10 | 77.78% | 77.78% | 738c ($7.38) | 70c ($0.70) | 3 | -94c ($-0.94)/-24c ($-0.23) | 97.08% | 7 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| `half_midprice_boundary` | 76 | 66/10 | 77.78% | 77.78% | 715c ($7.15) | 47c ($0.47) | 3 | -94c ($-0.94)/-47c ($-0.47) | 98.05% | 7 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| `control_no_shrink` | 76 | 66/10 | 77.78% | 77.78% | 668c ($6.68) | 0c ($0.00) | 3 | -94c ($-0.94)/-94c ($-0.94) | 100.00% | 6 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |

### post_feature_freeze_entry

| policy | settled | W/L | coverage | active cov | net | delta vs raw | band rows | band raw/weighted | avg weight | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `quarter_midprice_boundary` | 46 | 38/8 | 75.81% | 75.81% | 382c ($3.81) | 70c ($0.70) | 3 | -94c ($-0.94)/-24c ($-0.23) | 95.21% | 3 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| `half_midprice_boundary` | 46 | 38/8 | 75.81% | 75.81% | 358c ($3.58) | 47c ($0.47) | 3 | -94c ($-0.94)/-47c ($-0.47) | 96.81% | 3 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| `control_no_shrink` | 46 | 38/8 | 75.81% | 75.81% | 311c ($3.11) | 0c ($0.00) | 3 | -94c ($-0.94)/-94c ($-0.94) | 100.00% | 3 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |

### post_soft_frontier_birth_entry

| policy | settled | W/L | coverage | active cov | net | delta vs raw | band rows | band raw/weighted | avg weight | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `quarter_midprice_boundary` | 39 | 31/8 | 76.92% | 76.92% | 274c ($2.75) | 70c ($0.70) | 3 | -94c ($-0.94)/-24c ($-0.23) | 94.38% | 2 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `half_midprice_boundary` | 39 | 31/8 | 76.92% | 76.92% | 251c ($2.51) | 47c ($0.47) | 3 | -94c ($-0.94)/-47c ($-0.47) | 96.25% | 2 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `control_no_shrink` | 39 | 31/8 | 76.92% | 76.92% | 204c ($2.04) | 0c ($0.00) | 3 | -94c ($-0.94)/-94c ($-0.94) | 100.00% | 2 | diagnostic_only_prefreeze, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

### post_midprice_shrink_birth_entry

| policy | settled | W/L | coverage | active cov | net | delta vs raw | band rows | band raw/weighted | avg weight | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `control_no_shrink` | 36 | 28/8 | 80.00% | 80.00% | -46c ($-0.46) | 0c ($0.00) | 1 | 39c ($0.39)/39c ($0.39) | 100.00% | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `half_midprice_boundary` | 36 | 28/8 | 80.00% | 80.00% | -66c ($-0.66) | -20c ($-0.20) | 1 | 39c ($0.39)/20c ($0.20) | 98.61% | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `quarter_midprice_boundary` | 36 | 28/8 | 80.00% | 80.00% | -75c ($-0.75) | -29c ($-0.29) | 1 | 39c ($0.39)/10c ($0.10) | 97.92% | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

