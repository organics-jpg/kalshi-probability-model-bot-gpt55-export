# v28 Dual-Lane Conflict-Arbiter Watch

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-08T07:04:41.721107+00:00`
- Promotion use: `own_freeze_only`
- Freeze UTC/local: `2026-05-08T04:28:41.954114+00:00` / `2026-05-08T00:28:41.954114-04:00`
- Live baseline: `2215c ($22.15)`
- Rule: `suppress ask_prob >= 0.78 and recross_hazard_score >= 0.30`
- Windows since freeze / remaining: `10` / `20`
- Earliest 30-window local time: `2026-05-08T07:58:41.954114-04:00`
- Pre-sample short-circuit: `True`
- Force replay: `False`

## Read

- Research-only own-freeze dual-lane conflict arbiter; no live bot changes or orders.
- This is a coordinator arbiter candidate, not a second independent live bot.
- The rule is observable before entry: suppress rows with ask_prob >= 0.78 and recross hazard >= 0.30.
- Rows before this freeze are diagnostic only and cannot promote this branch.

## Best Arbiter Lane

- Policy: `post_dual_overlay_filter_entry_cheap_penalty025_rank_only`
- Settled/W-L: `0` / `0/0`
- Coverage: `0.00%`
- Net: `0c ($0.00)`
- Recon: `n/a`
- Cushion: `0`
- Live ready: `False`
- Blockers: `overlay_selected_settled_lt_30, overlay_net_not_positive, overlay_full_loss_cushion_lt_3, overlay_source_share_unknown`

## All Arbiter Lanes

| rank | policy | settled | W/L | coverage | net | recon | cushion | live ready | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `post_dual_overlay_filter_entry_cheap_penalty025_rank_only` | 0 | 0/0 | 0.00% | 0c ($0.00) | n/a | 0 | `False` | overlay_selected_settled_lt_30, overlay_net_not_positive, overlay_full_loss_cushion_lt_3, overlay_source_share_unknown |
| 2 | `post_dual_overlay_filter_bridge_cheap_penalty025_rank_only` | 0 | 0/0 | 0.00% | 0c ($0.00) | n/a | 0 | `False` | overlay_selected_settled_lt_30, overlay_net_not_positive, overlay_full_loss_cushion_lt_3, overlay_source_share_unknown |
