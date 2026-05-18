# v28 Dual-Lane Side-Flip Feasibility

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-07T16:50:58.113770+00:00`
- Promotion use: `feasibility_only_not_candidate`
- Freeze UTC: `2026-05-07T13:00:17.363339+00:00`
- Candidate policy: `post_dual_union_birth_bridge_cheap_penalty025_rank_only`
- Blockers: `research_only, not_frozen_forward, side_flip_trigger_not_observable_from_static_candidate_row, opposite_rescue_sample_too_sparse, candidate_side_flip_sample_too_sparse`

## Read

- Side-flip rescue is real in the current deficit rows, but it is sparse and derived from live sequence behavior.
- The current candidate row is static; a deployable repair would need an explicit pre-registered state-transition trigger and its own forward rows.
- Candidate-market opposite-side rescues: 2 market(s), 108c ($1.08) opposite-side net.
- All post-freeze live side-flip markets: 2 of 13 markets, net 68c ($0.68).

## Summary

| scope | markets | net | positive/negative | trades | side-flip markets | opposite rescues |
|---|---:|---:|---:|---:|---:|---:|
| all post-freeze live markets | 13 | 314c ($3.14) | 5/7 | 48 | 2 | 0 |
| all post-freeze side-flip markets | 2 | 68c ($0.68) | 2/0 | 14 | 2 | 0 |
| candidate markets | 13 | 324c ($3.24) | 5/6 | 45 | 2 | 2 |
| candidate side-flip markets | 2 | 68c ($0.68) | 2/0 | 14 | 2 | 2 |
| candidate opposite-rescue markets | 2 | 68c ($0.68) | 2/0 | 14 | 2 | 2 |

## Candidate Opposite-Rescue Rows

| market | candidate side | candidate net | same-side live | opposite live | live net | sequence |
|---|---|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY071015-15` | no | -162c ($-1.62) | -28c ($-0.28) | 56c ($0.56) | 28c ($0.28) | 2026-05-07 10:05:16 nox2 exited_before_settlement 2c ($0.02); 2026-05-07 10:05:16 nox2 exited_before_settlement 2c ($0.02); 2026-05-07 10:06:05 nox2 exited_before_settlement -10c ($-0.10); 2026-05-07 10:06:05 nox2 exited_before_settlement -10c ($-0.10); 2026-05-07 10:06:51 nox2 exited_before_settlement -6c ($-0.06); 2026-05-07 10:06:51 nox2 exited_before_settlement -6c ($-0.06); 2026-05-07 10:11:14 yesx4 win 56c ($0.56) |
| `KXBTC15M-26MAY071100-00` | yes | -166c ($-1.66) | -12c ($-0.12) | 52c ($0.52) | 40c ($0.40) | 2026-05-07 10:51:11 yesx2 exited_before_settlement -6c ($-0.06); 2026-05-07 10:51:11 yesx2 exited_before_settlement -6c ($-0.06); 2026-05-07 10:52:16 yesx2 exited_before_settlement -2c ($-0.02); 2026-05-07 10:52:16 yesx2 exited_before_settlement -2c ($-0.02); 2026-05-07 10:53:13 yesx2 exited_before_settlement 2c ($0.02); 2026-05-07 10:53:13 yesx2 exited_before_settlement 2c ($0.02); 2026-05-07 10:58:38 nox4 win 52c ($0.52) |
