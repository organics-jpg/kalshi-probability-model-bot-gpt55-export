# v28 Dual-Lane Same-Window Sequence Mechanism

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-07T16:50:58.046170+00:00`
- Delta autopsy UTC: `2026-05-07T16:31:45.447560+00:00`
- Freeze UTC: `2026-05-07T13:00:17.363339+00:00`
- Candidate policy: `post_dual_union_birth_entry_cheap_penalty025_rank_only`
- Candidate minus live on same markets: `-335c ($-3.35)`

## Read

- This is a mechanism audit for same-window deficits only; it is not a promotion gate.
- Deficit markets should be used to repair exposure/exit sequencing, not to hand-pick exclusions.
- Largest mechanism bucket is live_larger_terminal_exposure_same_side with 2 row(s) and -347c ($-3.47) candidate-minus-live.
- Candidate-loss rows include live side-flip escapes, so a one-shot hold-fill parent row is missing state transition behavior.

## Mechanism Summary

| mechanism | rows | candidate net | live net | candidate-live | live trades | live qty |
|---|---:|---:|---:|---:|---:|---:|
| `live_larger_terminal_exposure_same_side` | 2 | 41c ($0.41) | 388c ($3.88) | -347c ($-3.47) | 2 | 20 |
| `live_side_flip_escaped_candidate_loss` | 2 | -164c ($-1.64) | 68c ($0.68) | -232c ($-2.32) | 14 | 32 |
| `live_same_side_exit_capture_scaled_better` | 1 | 20c ($0.20) | 228c ($2.28) | -208c ($-2.08) | 2 | 12 |

## Deficit Rows

| market | mechanism | class | side | candidate | live | delta | same-side live | opposite live | trades | sequence |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY070945-45` | `live_larger_terminal_exposure_same_side` | `candidate_positive_live_captured_more` | no | 28c ($0.28) | 300c ($3.00) | -272c ($-2.72) | 300c ($3.00) | 0c ($0.00) | 1 | 2026-05-07 09:31:35 nox12 75->0 win 300c ($3.00) |
| `KXBTC15M-26MAY071145-45` | `live_same_side_exit_capture_scaled_better` | `candidate_positive_live_captured_more` | yes | 20c ($0.20) | 228c ($2.28) | -208c ($-2.08) | 228c ($2.28) | 0c ($0.00) | 2 | 2026-05-07 11:31:43 yesx6 81->100 exited_before_settlement 114c ($1.14); 2026-05-07 11:31:43 yesx6 81->100 exited_before_settlement 114c ($1.14) |
| `KXBTC15M-26MAY071100-00` | `live_side_flip_escaped_candidate_loss` | `candidate_loss_live_escape` | yes | -84c ($-0.84) | 40c ($0.40) | -124c ($-1.24) | -12c ($-0.12) | 52c ($0.52) | 7 | 2026-05-07 10:51:11 yesx2 80->77 exited_before_settlement -6c ($-0.06); 2026-05-07 10:51:11 yesx2 80->77 exited_before_settlement -6c ($-0.06); 2026-05-07 10:52:16 yesx2 82->81 exited_before_settlement -2c ($-0.02); 2026-05-07 10:52:16 yesx2 82->81 exited_before_settlement -2c ($-0.02); 2026-05-07 10:53:13 yesx2 85->86 exited_before_settlement 2c ($0.02); 2026-05-07 10:53:13 yesx2 85->86 exited_before_settlement 2c ($0.02); 2026-05-07 10:58:38 nox4 87->0 win 52c ($0.52) |
| `KXBTC15M-26MAY071015-15` | `live_side_flip_escaped_candidate_loss` | `candidate_loss_live_escape` | no | -80c ($-0.80) | 28c ($0.28) | -108c ($-1.08) | -28c ($-0.28) | 56c ($0.56) | 7 | 2026-05-07 10:05:16 nox2 78->79 exited_before_settlement 2c ($0.02); 2026-05-07 10:05:16 nox2 78->79 exited_before_settlement 2c ($0.02); 2026-05-07 10:06:05 nox2 79->74 exited_before_settlement -10c ($-0.10); 2026-05-07 10:06:05 nox2 79->74 exited_before_settlement -10c ($-0.10); 2026-05-07 10:06:51 nox2 80->77 exited_before_settlement -6c ($-0.06); 2026-05-07 10:06:51 nox2 80->77 exited_before_settlement -6c ($-0.06); 2026-05-07 10:11:14 yesx4 86->0 win 56c ($0.56) |
| `KXBTC15M-26MAY071130-30` | `live_larger_terminal_exposure_same_side` | `candidate_positive_live_captured_more` | no | 13c ($0.13) | 88c ($0.88) | -75c ($-0.75) | 88c ($0.88) | 0c ($0.00) | 1 | 2026-05-07 11:18:38 nox8 89->0 win 88c ($0.88) |
