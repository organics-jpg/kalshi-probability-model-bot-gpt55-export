# v28 Dual-Lane Variant Contrast

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:46:05.026181+00:00`
- Precheck UTC: `2026-05-08T03:51:40.155563+00:00`
- Promotion use: `not_promotion_evidence_before_min_sample`
- Precheck/current windows: `59` / `346`
- Live baseline: `-256c ($-2.56)`
- Bridge minus entry net: `0c ($0.00)`
- Bridge minus entry coverage: `0.00%`
- Current preferred precheck lane: `entry`

## Read

- Forced replay precheck is diagnostic until 30 strict-forward settled rows exist.
- Entry union is currently the better forced-replay lane.
- At the 30-window gate, prefer the lane that clears all gates, not the one with the best immature precheck PnL.

## Forced-Replay Variants

| rank | lane | settled | W/L | coverage | net | recon | cushion | sidecar add | shared | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `entry` | 16 | 13/3 | 88.89% | 59c ($0.59) | 18.75% | 0 | 10c ($0.10) | 14 | settled_lt_30, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| 2 | `bridge` | 16 | 13/3 | 88.89% | 59c ($0.59) | 18.75% | 0 | 10c ($0.10) | 14 | settled_lt_30, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
