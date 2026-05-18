# v28 Midprice Source-Dilution Runway

Research-only. No live bot changes or orders.

- Generated UTC: `2026-05-11T02:50:33.265607+00:00`
- Freeze UTC: `2026-05-07T06:29:57.062817+00:00`
- Candidate: `quarter_midprice_boundary_plus_weak_boundary_absd_gte_055`
- Any live-ready: `False`

## Interpretation

- Only post_dilution_birth lanes count as forward evidence for this branch.
- entry_runway: settled 28, coverage 84.84848484848484, net 43.0c, recon 0.39285714285714285, cushion 0, blockers ['settled_lt_30', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].
- bridge_runway: settled 28, coverage 84.84848484848484, net 43.0c, recon 0.39285714285714285, cushion 0, blockers ['settled_lt_30', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].
- No source-dilution lane is live-ready.

## Runway

| lane | filter | denom | entries | settled | W/L | coverage | net | recon | cushion | settled need | cov need | clean need | cushion need | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `entry_runway` | `weak_boundary_absd_gte_060` | 33 | 28 | 28 | 23/5 | 84.85% | 43.0c | 39.29% | 0 | 2 | 0 | 4 | 257.0c | settled_lt_30, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `bridge_runway` | `weak_boundary_absd_gte_060` | 33 | 28 | 28 | 23/5 | 84.85% | 43.0c | 39.29% | 0 | 2 | 0 | 4 | 257.0c | settled_lt_30, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
