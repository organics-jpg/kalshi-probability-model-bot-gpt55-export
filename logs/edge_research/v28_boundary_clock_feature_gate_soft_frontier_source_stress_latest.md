# v28 Boundary-Clock Feature-Gate Soft-Frontier Source Stress

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T04:16:03.727349+00:00`
- Soft-frontier freeze UTC: `2026-05-06T20:01:04.705640+00:00`

## Interpretation

- Policy-specific audit only; no live logic changes and no promotion by itself.
- Best stress row post_soft_frontier_birth_entry_soft_raw03_recross50_abs65_ask35 has 18 settled, coverage 75.0%, net 227.0c, reconstructed share 0.25, clean rows needed 0, cushion 2, blockers ['settled_lt_30', 'full_loss_cushion_lt_3'].
- Best target-coverage row post_soft_frontier_birth_entry_soft_raw03_recross50_abs65_ask35 has net 227.0c and reconstructed share 0.25.

## Policies

| policy | settled | W/L | coverage | net c | recon | clean rows needed | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| post_soft_frontier_birth_entry_soft_raw03_recross50_abs65_ask35 | 18 | 16/2 | 75.000000 | 227.000000 | 0.250000 | 0 | 2 | settled_lt_30, full_loss_cushion_lt_3 |
| post_soft_frontier_birth_bridge_soft_raw03_recross50_abs65_ask35 | 20 | 17/3 | 75.000000 | 216.000000 | 0.250000 | 0 | 2 | settled_lt_30, full_loss_cushion_lt_3 |
| post_soft_frontier_birth_bridge_soft_raw03_recross50_abs50_ask35 | 23 | 18/5 | 84.375000 | 175.000000 | 0.407407 | 5 | 1 | settled_lt_30, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| post_soft_frontier_birth_entry_soft_raw03_recross50_abs50_ask35 | 22 | 17/5 | 84.375000 | 108.000000 | 0.407407 | 5 | 1 | settled_lt_30, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| post_soft_frontier_birth_bridge_soft_raw03_recross50_abs50_ask50 | 21 | 15/6 | 78.125000 | -66.000000 | 0.400000 | 4 | 0 | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| post_soft_frontier_birth_entry_soft_raw03_recross50_abs50_ask50 | 21 | 15/6 | 78.125000 | -77.000000 | 0.400000 | 4 | 0 | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
