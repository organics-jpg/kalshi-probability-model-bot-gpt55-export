# v28 Common-Clock Exit Guard Frontier

Research-only. No live bot logic changes, no process control, no orders.

- Generated UTC: `2026-05-07T21:29:54.460137+00:00`
- Decision: `monitor_readiness_frontier`
- Target policy: `loss_guard_value_p85_reduce_p79_gap0`
- Live baseline: `1361c ($13.61)`

## Readiness Frontier

- Window: `new_exit_mix_common_forward_v2`
- Candidate/current/delta: `668c ($6.68)` / `426c ($4.26)` / `242c ($2.42)`
- W/L: `41/17`
- Suppressions needed: `17/30`; missing `13`
- Helpful/harmful: `17/0`
- Loss cost/cushion: `0c ($0.00)` / `6`

## Net Leader

- Window: `new_exit_mix_common_forward_v3`
- Candidate/current/delta: `692c ($6.92)` / `478c ($4.78)` / `214c ($2.14)`
- Suppressions needed: `13/30`; missing `17`

## Ranked Windows

| window | candidate | delta | W/L | suppressions | need | helpful/harmful | loss cost | cushion | missing gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `new_exit_mix_common_forward_v2` | 668c ($6.68) | 242c ($2.42) | `41/17` | 17 | 13 | 17/0 | 0c ($0.00) | 6 | `live_ready_false, suppressed_needed_13` |
| `new_exit_mix_common_forward_v1` | 582c ($5.82) | 242c ($2.42) | `41/18` | 17 | 13 | 17/0 | 0c ($0.00) | 5 | `live_ready_false, suppressed_needed_13` |
| `new_exit_mix_common_forward_v3` | 692c ($6.92) | 214c ($2.14) | `33/13` | 13 | 17 | 13/0 | 0c ($0.00) | 6 | `live_ready_false, suppressed_needed_17` |

## Interpretation

- Use the readiness frontier for the next live-review runway because it needs the fewest strict suppressions.
- Keep the net leader alive as a sibling watch; do not switch solely for higher net while it has less forward density.
- No common-clock window may trade live until full-policy, live-readiness, single-process ownership, and reconciliation gates pass.
