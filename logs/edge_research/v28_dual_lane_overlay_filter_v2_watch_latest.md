# v28 Dual-Lane Overlay Filter Watch

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:46:02.223702+00:00`
- Promotion use: `own_freeze_only`
- Freeze UTC/local: `2026-05-07T16:50:03.875032+00:00` / `2026-05-07T12:50:03.875032-04:00`
- Live baseline: `-256c ($-2.56)`
- Windows since freeze / remaining: `331` / `0`
- Earliest 30-window local time: `2026-05-07T20:20:03.875032-04:00`
- Pre-sample short-circuit: `False`
- Force replay: `False`

## Read

- Research-only own-freeze dual-lane overlay filter v2; no live bot changes or orders.
- This is an overlay-only branch, not a replacement for live v28.
- The rule is observable: raw edge >= 0.05, recross hazard <= 0.30, and abs distance >= 0.85.
- Rows before this freeze are diagnostic only and cannot promote this branch.

## Best Overlay Lane

- Policy: `post_dual_overlay_filter_entry_cheap_penalty025_rank_only`
- Settled/W-L: `1` / `1/0`
- Coverage: `50.00%`
- Net: `44c ($0.44)`
- Recon: `0.00%`
- Cushion: `0`
- Live ready: `False`
- Blockers: `overlay_selected_settled_lt_30, overlay_full_loss_cushion_lt_3, overlay_source_gate_zero_row_margin`

## All Overlay Lanes

| rank | policy | settled | W/L | coverage | net | recon | cushion | live ready | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `post_dual_overlay_filter_entry_cheap_penalty025_rank_only` | 1 | 1/0 | 50.00% | 44c ($0.44) | 0.00% | 0 | `False` | overlay_selected_settled_lt_30, overlay_full_loss_cushion_lt_3, overlay_source_gate_zero_row_margin |
| 2 | `post_dual_overlay_filter_bridge_cheap_penalty025_rank_only` | 1 | 1/0 | 50.00% | 44c ($0.44) | 0.00% | 0 | `False` | overlay_selected_settled_lt_30, overlay_full_loss_cushion_lt_3, overlay_source_gate_zero_row_margin |
