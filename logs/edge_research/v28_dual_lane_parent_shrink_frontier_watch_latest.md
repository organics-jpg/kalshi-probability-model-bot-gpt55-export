# v28 Dual-Lane Parent-Shrink Frontier Watch

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-08T04:24:41.939048+00:00`
- Promotion use: `own_freeze_only`
- Freeze UTC/local: `2026-05-07T15:33:12.317447+00:00` / `2026-05-07T11:33:12.317447-04:00`
- Live baseline: `2215c ($22.15)`
- Windows since freeze / remaining: `51` / `0`
- Earliest 30-window local time: `2026-05-07T19:03:12.317447-04:00`
- Pre-sample short-circuit: `False`
- Force replay: `False`

## Read

- Research-only dual-lane parent-shrink weight frontier; no live bot changes or orders.
- All weights share one freeze timestamp so forward evidence can compare shrink strength cleanly.
- Do not use pre-freeze diagnostic rows to promote this frontier.

## Best Frontier Union

- Label/weight: `shrink25_weight075` / `0.75`
- Settled/W-L: `7` / `7/0`
- Coverage: `100.00%`
- Net: `155c ($1.55)`
- Cushion: `1`
- Live ready: `False`
- Blockers: `settled_lt_30, full_loss_cushion_lt_3, coverage_gt_90pct, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline`

## All Frontier Unions

| rank | label | weight | sidecar | settled | W/L | coverage | net | recon | cushion | live ready | blockers |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `shrink25_weight075` | 0.75 | `post_dual_parent_shrink_frontier_entry_cheap_penalty025_rank_only` | 7 | 7/0 | 100.00% | 155c ($1.55) | 42.86% | 1 | `False` | settled_lt_30, full_loss_cushion_lt_3, coverage_gt_90pct, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 2 | `shrink25_weight075` | 0.75 | `post_dual_parent_shrink_frontier_bridge_cheap_penalty025_rank_only` | 7 | 7/0 | 100.00% | 155c ($1.55) | 42.86% | 1 | `False` | settled_lt_30, full_loss_cushion_lt_3, coverage_gt_90pct, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 3 | `shrink50_weight050` | 0.5 | `post_dual_parent_shrink_frontier_entry_cheap_penalty025_rank_only` | 7 | 7/0 | 100.00% | 147c ($1.47) | 42.86% | 1 | `False` | settled_lt_30, full_loss_cushion_lt_3, coverage_gt_90pct, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 4 | `shrink50_weight050` | 0.5 | `post_dual_parent_shrink_frontier_bridge_cheap_penalty025_rank_only` | 7 | 7/0 | 100.00% | 147c ($1.47) | 42.86% | 1 | `False` | settled_lt_30, full_loss_cushion_lt_3, coverage_gt_90pct, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 5 | `shrink75_weight025` | 0.25 | `post_dual_parent_shrink_frontier_entry_cheap_penalty025_rank_only` | 7 | 7/0 | 100.00% | 139c ($1.39) | 42.86% | 1 | `False` | settled_lt_30, full_loss_cushion_lt_3, coverage_gt_90pct, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 6 | `shrink75_weight025` | 0.25 | `post_dual_parent_shrink_frontier_bridge_cheap_penalty025_rank_only` | 7 | 7/0 | 100.00% | 139c ($1.39) | 42.86% | 1 | `False` | settled_lt_30, full_loss_cushion_lt_3, coverage_gt_90pct, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
