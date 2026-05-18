# v28 Midprice Source-Dilution Watch

Research-only. No live bot logic changed and no orders placed.

- Generated UTC: `2026-05-11T02:49:40.140850+00:00`
- Freeze UTC: `2026-05-07T06:29:57.062817+00:00`

## Interpretation

- Source labels are audit-only; all tested filters use observable abs_d/ask fields.
- Only post_dilution_birth lanes are strict forward evidence for this new watch.
- diagnostic_parent_entry: best control_no_extra_filter entries 47, W/L 38/8, coverage 75.80645161290323%, net 381.5c, recon 0.40425531914893614, dropped 0 for 0c, blockers ['diagnostic_only_prefreeze', 'reconstructed_share_gt_35pct'].
- diagnostic_parent_bridge: best control_no_extra_filter entries 0, W/L 0/0, coverage None%, net 0c, recon None, dropped 0 for 0c, blockers ['diagnostic_only_prefreeze', 'settled_lt_30', 'coverage_too_low', 'net_not_positive', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].
- post_dilution_birth_entry: best weak_boundary_absd_gte_060 entries 28, W/L 23/5, coverage 84.84848484848484%, net 43.0c, recon 0.39285714285714285, dropped 1 for -73.0c, blockers ['settled_lt_30', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].
- post_dilution_birth_bridge: best weak_boundary_absd_gte_060 entries 28, W/L 23/5, coverage 84.84848484848484%, net 43.0c, recon 0.39285714285714285, dropped 1 for -73.0c, blockers ['settled_lt_30', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].

## diagnostic_parent_entry

| filter | strict | entries | dropped | W/L | coverage | net | recon | cushion | dropped net | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `control_no_extra_filter` | False | 47 | 0 | 38/8 | 75.81% | 381.5c | 40.43% | 3 | 0.0c | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| `mid_or_better_ask_gte_055` | False | 41 | 6 | 35/5 | 66.13% | 373.5c | 34.15% | 3 | 8.0c | diagnostic_only_prefreeze, coverage_too_low |
| `weak_boundary_absd_gte_060` | False | 41 | 6 | 33/7 | 66.13% | 300.8c | 31.71% | 3 | 80.8c | diagnostic_only_prefreeze, coverage_too_low |
| `absd_gte_055_or_ask_gte_065` | False | 46 | 1 | 38/7 | 74.19% | 439.5c | 39.13% | 4 | -58.0c | diagnostic_only_prefreeze, coverage_too_low, reconstructed_share_gt_35pct |
| `weak_boundary_absd_gte_055` | False | 44 | 3 | 36/7 | 70.97% | 384.5c | 36.36% | 3 | -3.0c | diagnostic_only_prefreeze, coverage_too_low, reconstructed_share_gt_35pct |

### Dropped Rows For Best Filter

| market | side | source | net | weight | abs_d | ask | recross |
|---|---|---|---:|---:|---:|---:|---:|

## diagnostic_parent_bridge

| filter | strict | entries | dropped | W/L | coverage | net | recon | cushion | dropped net | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `control_no_extra_filter` | False | 0 | 0 | 0/0 | n/a | 0.0c | 0.00% | 0 | 0.0c | diagnostic_only_prefreeze, settled_lt_30, coverage_too_low, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `weak_boundary_absd_gte_055` | False | 0 | 0 | 0/0 | n/a | 0.0c | 0.00% | 0 | 0.0c | diagnostic_only_prefreeze, settled_lt_30, coverage_too_low, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `weak_boundary_absd_gte_060` | False | 0 | 0 | 0/0 | n/a | 0.0c | 0.00% | 0 | 0.0c | diagnostic_only_prefreeze, settled_lt_30, coverage_too_low, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `mid_or_better_ask_gte_055` | False | 0 | 0 | 0/0 | n/a | 0.0c | 0.00% | 0 | 0.0c | diagnostic_only_prefreeze, settled_lt_30, coverage_too_low, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `absd_gte_055_or_ask_gte_065` | False | 0 | 0 | 0/0 | n/a | 0.0c | 0.00% | 0 | 0.0c | diagnostic_only_prefreeze, settled_lt_30, coverage_too_low, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

### Dropped Rows For Best Filter

| market | side | source | net | weight | abs_d | ask | recross |
|---|---|---|---:|---:|---:|---:|---:|

## post_dilution_birth_entry

| filter | strict | entries | dropped | W/L | coverage | net | recon | cushion | dropped net | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `weak_boundary_absd_gte_060` | True | 28 | 1 | 23/5 | 84.85% | 43.0c | 39.29% | 0 | -73.0c | settled_lt_30, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `mid_or_better_ask_gte_055` | True | 28 | 1 | 23/5 | 84.85% | 17.0c | 39.29% | 0 | -47.0c | settled_lt_30, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `control_no_extra_filter` | True | 29 | 0 | 23/6 | 87.88% | -30.0c | 41.38% | 0 | 0.0c | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `weak_boundary_absd_gte_055` | True | 29 | 0 | 23/6 | 87.88% | -30.0c | 41.38% | 0 | 0.0c | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `absd_gte_055_or_ask_gte_065` | True | 29 | 0 | 23/6 | 87.88% | -30.0c | 41.38% | 0 | 0.0c | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

### Dropped Rows For Best Filter

| market | side | source | net | weight | abs_d | ask | recross |
|---|---|---|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY070900-00` | `no` | `rejected_actionable` | -73.0c | 1.0 | 0.591792 | 0.7 | 0.45720689280417326 |

## post_dilution_birth_bridge

| filter | strict | entries | dropped | W/L | coverage | net | recon | cushion | dropped net | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `weak_boundary_absd_gte_060` | True | 28 | 1 | 23/5 | 84.85% | 43.0c | 39.29% | 0 | -73.0c | settled_lt_30, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `mid_or_better_ask_gte_055` | True | 28 | 1 | 23/5 | 84.85% | 17.0c | 39.29% | 0 | -47.0c | settled_lt_30, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `control_no_extra_filter` | True | 29 | 0 | 23/6 | 87.88% | -30.0c | 41.38% | 0 | 0.0c | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `weak_boundary_absd_gte_055` | True | 29 | 0 | 23/6 | 87.88% | -30.0c | 41.38% | 0 | 0.0c | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `absd_gte_055_or_ask_gte_065` | True | 29 | 0 | 23/6 | 87.88% | -30.0c | 41.38% | 0 | 0.0c | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

### Dropped Rows For Best Filter

| market | side | source | net | weight | abs_d | ask | recross |
|---|---|---|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY070900-00` | `no` | `rejected_actionable` | -73.0c | 1.0 | 0.591792 | 0.7 | 0.45720689280417326 |
