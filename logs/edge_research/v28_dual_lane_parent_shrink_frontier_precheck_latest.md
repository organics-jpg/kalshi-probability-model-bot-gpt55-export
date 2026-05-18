# v28 Dual-Lane Parent-Shrink Frontier Precheck

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-08T03:55:22.228400+00:00`
- Promotion use: `not_promotion_evidence_before_min_sample`
- Freeze UTC/local: `2026-05-07T15:33:12.317447+00:00` / `2026-05-07T11:33:12.317447-04:00`
- Live baseline: `2215c ($22.15)`
- Windows since freeze / remaining: `49` / `0`
- Earliest 30-window local time: `2026-05-07T19:03:12.317447-04:00`
- Force replay: `True`
- Pre-sample short-circuit: `False`

## Read

- Forced frontier replay executed into a separate diagnostic artifact.
- Rows are not promotion evidence before the frontier reaches its own 30-settled-row gate.
- Use this only to catch scorer/join/accounting failures and compare frozen weights diagnostically.

## Best Forced Frontier Union

| label | weight | policy | settled | W/L | coverage | net | recon | cushion | blockers |
|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| `shrink25_weight075` | 0.75 | `post_dual_parent_shrink_frontier_entry_cheap_penalty025_rank_only` | 7 | 7/0 | 100.00% | 155c ($1.55) | 42.86% | 1 | settled_lt_30, full_loss_cushion_lt_3, coverage_gt_90pct, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |

## All Forced Frontier Unions

| label | weight | policy | settled | W/L | coverage | net | recon | sidecar add | blockers |
|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| `shrink25_weight075` | 0.75 | `post_dual_parent_shrink_frontier_entry_cheap_penalty025_rank_only` | 7 | 7/0 | 100.00% | 155c ($1.55) | 42.86% | 20c ($0.20) | settled_lt_30, full_loss_cushion_lt_3, coverage_gt_90pct, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `shrink25_weight075` | 0.75 | `post_dual_parent_shrink_frontier_bridge_cheap_penalty025_rank_only` | 7 | 7/0 | 100.00% | 155c ($1.55) | 42.86% | 20c ($0.20) | settled_lt_30, full_loss_cushion_lt_3, coverage_gt_90pct, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `shrink50_weight050` | 0.5 | `post_dual_parent_shrink_frontier_entry_cheap_penalty025_rank_only` | 7 | 7/0 | 100.00% | 147c ($1.47) | 42.86% | 20c ($0.20) | settled_lt_30, full_loss_cushion_lt_3, coverage_gt_90pct, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `shrink50_weight050` | 0.5 | `post_dual_parent_shrink_frontier_bridge_cheap_penalty025_rank_only` | 7 | 7/0 | 100.00% | 147c ($1.47) | 42.86% | 20c ($0.20) | settled_lt_30, full_loss_cushion_lt_3, coverage_gt_90pct, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `shrink75_weight025` | 0.25 | `post_dual_parent_shrink_frontier_entry_cheap_penalty025_rank_only` | 7 | 7/0 | 100.00% | 139c ($1.39) | 42.86% | 20c ($0.20) | settled_lt_30, full_loss_cushion_lt_3, coverage_gt_90pct, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `shrink75_weight025` | 0.25 | `post_dual_parent_shrink_frontier_bridge_cheap_penalty025_rank_only` | 7 | 7/0 | 100.00% | 139c ($1.39) | 42.86% | 20c ($0.20) | settled_lt_30, full_loss_cushion_lt_3, coverage_gt_90pct, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
