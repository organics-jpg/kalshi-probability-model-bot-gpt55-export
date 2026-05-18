# v28 Dual-Lane Parent-Shrink Repair Precheck

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-08T03:53:29.954205+00:00`
- Promotion use: `not_promotion_evidence_before_min_sample`
- Freeze UTC/local: `2026-05-07T15:19:20.874849+00:00` / `2026-05-07T11:19:20.874849-04:00`
- Live baseline: `2215c ($22.15)`
- Windows since freeze / remaining: `50` / `0`
- Earliest 30-window local time: `2026-05-07T18:49:20.874849-04:00`
- Force replay: `True`
- Pre-sample short-circuit: `False`

## Read

- Forced repair replay executed into a separate diagnostic artifact.
- Rows are not promotion evidence before the repair branch reaches its own 30-settled-row gate.
- Use this only to catch scorer/join/accounting failures before the real checkpoint.

## Best Forced Repair Union

| policy | settled | W/L | coverage | net | recon | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---|
| `post_dual_parent_shrink_entry_cheap_penalty025_rank_only` | 7 | 7/0 | 87.50% | 185c ($1.85) | 42.86% | 1 | settled_lt_30, full_loss_cushion_lt_3, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |

## All Forced Repair Unions

| policy | settled | W/L | coverage | net | recon | sidecar add | shared | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `post_dual_parent_shrink_entry_cheap_penalty025_rank_only` | 7 | 7/0 | 87.50% | 185c ($1.85) | 42.86% | 20c ($0.20) | 5 | settled_lt_30, full_loss_cushion_lt_3, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `post_dual_parent_shrink_bridge_cheap_penalty025_rank_only` | 7 | 7/0 | 87.50% | 185c ($1.85) | 42.86% | 20c ($0.20) | 5 | settled_lt_30, full_loss_cushion_lt_3, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
