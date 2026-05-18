# v28 Dual-Lane Overlay Filter Watch

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-08T00:04:55.439978+00:00`
- Promotion use: `own_freeze_only`
- Freeze UTC/local: `2026-05-07T16:34:55.927871+00:00` / `2026-05-07T12:34:55.927871-04:00`
- Live baseline: `1361c ($13.61)`
- Windows since freeze / remaining: `29` / `1`
- Earliest 30-window local time: `2026-05-07T20:04:55.927871-04:00`
- Pre-sample short-circuit: `True`
- Force replay: `False`

## Read

- Research-only own-freeze dual-lane overlay filter; no live bot changes or orders.
- This is an overlay-only branch, not a replacement for live v28.
- The rule is observable: candidate side must be NO and recross hazard must be <= 0.30.
- Rows before this freeze are diagnostic only and cannot promote this branch.

## Best Overlay Lane

- Policy: `post_dual_overlay_filter_entry_cheap_penalty025_rank_only`
- Settled/W-L: `0` / `0/0`
- Coverage: `0.00%`
- Net: `0c ($0.00)`
- Recon: `n/a`
- Cushion: `0`
- Live ready: `False`
- Blockers: `overlay_selected_settled_lt_30, overlay_net_not_positive, overlay_full_loss_cushion_lt_3, overlay_source_share_unknown`

## All Overlay Lanes

| rank | policy | settled | W/L | coverage | net | recon | cushion | live ready | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `post_dual_overlay_filter_entry_cheap_penalty025_rank_only` | 0 | 0/0 | 0.00% | 0c ($0.00) | n/a | 0 | `False` | overlay_selected_settled_lt_30, overlay_net_not_positive, overlay_full_loss_cushion_lt_3, overlay_source_share_unknown |
| 2 | `post_dual_overlay_filter_bridge_cheap_penalty025_rank_only` | 0 | 0/0 | 0.00% | 0c ($0.00) | n/a | 0 | `False` | overlay_selected_settled_lt_30, overlay_net_not_positive, overlay_full_loss_cushion_lt_3, overlay_source_share_unknown |
