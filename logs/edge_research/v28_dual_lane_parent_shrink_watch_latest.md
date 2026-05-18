# v28 Dual-Lane Parent-Shrink Watch

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-08T04:38:00.868453+00:00`
- Promotion use: `own_freeze_only`
- Freeze UTC/local: `2026-05-07T15:19:20.874849+00:00` / `2026-05-07T11:19:20.874849-04:00`
- Live baseline: `2215c ($22.15)`
- Windows since freeze / remaining: `53` / `0`
- Earliest 30-window local time: `2026-05-07T18:49:20.874849-04:00`
- Pre-sample short-circuit: `False`
- Force replay: `False`

## Repair Rule

- Name: `dual_lane_parent_fill_high_cost_low_edge_shrink50`
- Shrink parent-fill rows when `ask_prob >= 0.78` and `raw_edge < 0.09`.
- Weight: `0.5`

## Interpretation

- Research-only dual-lane parent-shrink watch; no live bot changes or orders.
- This branch keeps coverage by shrinking confidence on expensive low-edge parent fills instead of suppressing them.

## Best Own-Freeze Repair Union

- Settled/W-L: `7` / `7/0`
- Coverage: `87.50%`
- Net: `185c ($1.85)`
- Recon: `42.86%`
- Cushion: `1`
- Live ready: `False`
- Blockers: `settled_lt_30, full_loss_cushion_lt_3, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline`

## All Repair Unions

| rank | sidecar | settled | W/L | coverage | net | recon | cushion | sidecar add | shared | live ready | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `post_dual_parent_shrink_entry_cheap_penalty025_rank_only` | 7 | 7/0 | 87.50% | 185c ($1.85) | 42.86% | 1 | 20c ($0.20) | 5 | `False` | settled_lt_30, full_loss_cushion_lt_3, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 2 | `post_dual_parent_shrink_bridge_cheap_penalty025_rank_only` | 7 | 7/0 | 87.50% | 185c ($1.85) | 42.86% | 1 | 20c ($0.20) | 5 | `False` | settled_lt_30, full_loss_cushion_lt_3, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
