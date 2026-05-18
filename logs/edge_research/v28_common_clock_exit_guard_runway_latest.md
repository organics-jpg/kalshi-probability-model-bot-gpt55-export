# v28 Common-Clock Exit Guard Runway

Research-only. This probe does not place orders or edit live bot logic.

- Generated UTC: `2026-05-07T21:28:21.651048+00:00`
- Decision: `wait_for_forward_density`
- Target policy: `loss_guard_value_p85_reduce_p79_gap0`
- Live baseline: `1361c`

## Interpretation

- Best strict window is new_exit_mix_common_forward_v3 with 13 suppressions, 214.0c delta, 0 harmful suppressions, and missing gates ['live_ready_false', 'suppressed_needed_17'].
- Next concrete requirement: collect 17 more strict suppressions without adding harmful holds.

## Strict Windows

| window | settled | current | candidate | delta | W/L current | W/L candidate | suppressions | helpful/harmful | loss cost | cushion | missing gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `new_exit_mix_common_forward_v3` | 46 | 478c | 692c | 214c | 31/15 | 33/13 | 13 | 13/0 | 0c | 6 | live_ready_false, suppressed_needed_17 |
| `new_exit_mix_common_forward_v2` | 58 | 426c | 668c | 242c | 39/19 | 41/17 | 17 | 17/0 | 0c | 6 | live_ready_false, suppressed_needed_13 |
| `new_exit_mix_common_forward_v1` | 59 | 340c | 582c | 242c | 39/20 | 41/18 | 17 | 17/0 | 0c | 5 | live_ready_false, suppressed_needed_13 |
