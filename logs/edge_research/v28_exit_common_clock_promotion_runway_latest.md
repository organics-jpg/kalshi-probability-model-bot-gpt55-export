# v28 Exit Common-Clock Promotion Runway

Research-only runway. No live bot changes or orders.

- Generated UTC: `2026-05-07T18:03:24.624202+00:00`
- Common-clock generated UTC: `2026-05-07T18:03:07.655477+00:00`

## Interpretation

- This is a strict common-clock exit runway, not a promotion decision.
- Closest strict exit row is new_exit_mix_common_forward_v2 / loss_guard_value_p85_reduce_p79_gap0: 58 settled, 17 suppressed, 668.0c candidate net, 242.0c delta.
- It still needs 13 suppressed decisions and 0.0c cushion; do not use it live until strict rows mature.

## Strict Windows

| window | policy | settled | suppressed | current c | candidate c | delta c | loss cost | loss reduction | needed | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| new_exit_mix_common_forward_v2 | loss_guard_value_p85_reduce_p79_gap0 | 58 | 17 | 426.000000 | 668.000000 | 242.000000 | 0.000000 | 2 | settled 0, suppressed 13, cushion 0.000000c | suppressed+13 |
| new_exit_mix_common_forward_v1 | loss_guard_value_p85_reduce_p79_gap0 | 59 | 17 | 340.000000 | 582.000000 | 242.000000 | 0.000000 | 2 | settled 0, suppressed 13, cushion 0.000000c | suppressed+13 |
| new_exit_mix_common_forward_v3 | loss_guard_value_p85_reduce_p79_gap0 | 46 | 13 | 478.000000 | 692.000000 | 214.000000 | 0.000000 | 2 | settled 0, suppressed 17, cushion 0.000000c | suppressed+17 |
