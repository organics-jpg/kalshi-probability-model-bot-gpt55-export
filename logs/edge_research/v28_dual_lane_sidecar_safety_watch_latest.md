# v28 Dual-Lane Sidecar-Safety Watch

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-07T23:45:40.446268+00:00`
- Promotion use: `own_freeze_only`
- Freeze UTC/local: `2026-05-07T16:16:00.768697+00:00` / `2026-05-07T12:16:00.768697-04:00`
- Live baseline: `1361c ($13.61)`
- Windows since freeze / remaining: `29` / `1`
- Earliest 30-window local time: `2026-05-07T19:46:00.768697-04:00`
- Pre-sample short-circuit: `True`
- Force replay: `False`

## Read

- Research-only dual-lane sidecar-safety watch; no live bot changes or orders.
- This branch tests whether the clean observable sidecar can be a deployable fallback while parent-lane repairs mature.
- Rows before this freeze are diagnostic only and cannot promote this branch.

## Best Sidecar-Safety Lane

- Settled/W-L: `0` / `0/0`
- Coverage: `0.00%`
- Net: `0c ($0.00)`
- Recon: `n/a%`
- Cushion: `0`
- Live ready: `False`
- Blockers: `settled_lt_30, net_not_positive, full_loss_cushion_lt_3, coverage_lt_75pct, source_share_unknown, does_not_beat_refreshed_live_baseline`

## All Sidecar-Safety Lanes

| rank | lane | settled | W/L | coverage | net | recon | cushion | live ready | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `post_dual_sidecar_safety_entry_cheap_penalty025_rank_only` | 0 | 0/0 | 0.00% | 0c ($0.00) | n/a% | 0 | `False` | settled_lt_30, net_not_positive, full_loss_cushion_lt_3, coverage_lt_75pct, source_share_unknown, does_not_beat_refreshed_live_baseline |
| 2 | `post_dual_sidecar_safety_bridge_cheap_penalty025_rank_only` | 0 | 0/0 | 0.00% | 0c ($0.00) | n/a% | 0 | `False` | settled_lt_30, net_not_positive, full_loss_cushion_lt_3, coverage_lt_75pct, source_share_unknown, does_not_beat_refreshed_live_baseline |
