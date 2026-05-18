# v28 Target Cluster-Penalty Runway

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T01:06:57.714389+00:00`
- Freeze UTC: `2026-05-06T21:38:42.476858+00:00`

## Interpretation

- This is a runway/source-quality audit only; it does not change the frozen cluster-penalty watch.
- Post-birth post_cluster_penalty_birth_cluster_penalty_medium has 33 settled rows, 76.74418604651163% coverage, -96.0c net, and 0.9090909090909091 reconstructed share.
- Post-birth still needs 0 settled rows, 53 clean approved selected rows for source, and 396.0c for a three-full-loss cushion.
- Diagnostic best remains source-blocked too: 0.7525773195876289 reconstructed share and 112 clean rows needed for source.

## Runway

| lane | candidate | settled | coverage | net c | recon share | rows needed | clean rows needed | cushion c needed | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `post_cluster_penalty_birth` | `post_cluster_penalty_birth_cluster_penalty_medium` | 33 | 76.744186 | -96.000000 | 0.909091 | 0 | 53 | 396.000000 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `diagnostic_target_window` | `diagnostic_target_window_cluster_penalty_heavy` | 97 | 75.193798 | -84.000000 | 0.752577 | 0 | 112 | 384.000000 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
