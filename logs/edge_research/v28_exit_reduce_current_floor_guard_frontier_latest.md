# v28 Exit Reduce Current-Floor Guard Frontier

Research-only. No live bot changes, no orders, no new frozen rule.

- Generated UTC: `2026-05-07T12:03:30.960923+00:00`
- Diagnostic freeze UTC: `2026-05-06T06:33:56.987999+00:00`
- Post-composite freeze UTC: `2026-05-06T23:34:20.352483+00:00`

## Interpretation

- Research-only frontier; this does not freeze a child or alter any live/watch logic.
- A current-exit floor is observable at the exit decision and tests whether already-negative reduce exits should be excluded from hold suppression.
- diagnostic_from_exit_freezes: best v2_reduce_p78_depth384 settled 102, candidate 750.0c, delta 389.0c, suppressed 9 value/reduce 2/7, suppressed W/L 9/0, blockers ['suppressed_decisions_lt_30'].
- post_composite_birth: best v2_reduce_p75_depth384_current_ge_0 settled 24, candidate 0.0c, delta 22.0c, suppressed 1 value/reduce 1/0, suppressed W/L 1/0, blockers ['settled_lt_30', 'net_not_positive', 'suppressed_decisions_lt_30', 'full_loss_cushion_lt_3'].

## diagnostic_from_exit_freezes

| rank | variant | settled | W/L | current c | candidate c | delta c | suppressed | value/reduce | suppressed W/L | recovery c | loss cost c | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `v2_reduce_p78_depth384` | 102 | 64/38 | 361.000000 | 750.000000 | 389.000000 | 9 | 2/7 | 9/0 | 389.000000 | 0 | 7 | suppressed_decisions_lt_30 |
| 2 | `v2_reduce_p79_depth384` | 102 | 63/39 | 361.000000 | 698.000000 | 337.000000 | 8 | 2/6 | 8/0 | 337.000000 | 0 | 6 | suppressed_decisions_lt_30 |
| 3 | `v2_reduce_p795_depth384` | 102 | 62/40 | 361.000000 | 650.000000 | 289.000000 | 7 | 2/5 | 7/0 | 289.000000 | 0 | 6 | suppressed_decisions_lt_30 |
| 4 | `v2_reduce_p75_depth384_current_ge_minus10` | 102 | 61/41 | 361.000000 | 600.000000 | 239.000000 | 6 | 2/4 | 6/0 | 239.000000 | 0 | 6 | suppressed_decisions_lt_30 |
| 5 | `v2_reduce_p75_depth384_current_ge_0` | 102 | 57/45 | 361.000000 | 395.000000 | 34.000000 | 2 | 2/0 | 2/0 | 34.000000 | 0 | 3 | suppressed_decisions_lt_30 |
| 6 | `v2_reduce_p77_depth384_current_ge_0` | 102 | 57/45 | 361.000000 | 395.000000 | 34.000000 | 2 | 2/0 | 2/0 | 34.000000 | 0 | 3 | suppressed_decisions_lt_30 |
| 7 | `v2_reduce_p80_depth384` | 102 | 57/45 | 361.000000 | 395.000000 | 34.000000 | 2 | 2/0 | 2/0 | 34.000000 | 0 | 3 | suppressed_decisions_lt_30 |
| 8 | `v2_reduce_p75_depth384` | 102 | 68/34 | 361.000000 | 862.000000 | 501.000000 | 14 | 2/12 | 13/1 | 621.000000 | -120.000000 | 8 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |

### Suppressed Loser Rows

| variant | market | side | reason | current | hold | delta | p_hold | depth | gap | drawdown |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `v2_reduce_p75_depth384` | `KXBTC15M-26MAY062130-30` | `no` | `mushroom_v28_probability_reduce` | -32.000000 | -152.000000 | -120.000000 | 0.768407 | 24.000000 | 0.168407 | 6.159273 |

## post_composite_birth

| rank | variant | settled | W/L | current c | candidate c | delta c | suppressed | value/reduce | suppressed W/L | recovery c | loss cost c | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `v2_reduce_p75_depth384_current_ge_0` | 24 | 16/8 | -22.000000 | 0.000000 | 22.000000 | 1 | 1/0 | 1/0 | 22.000000 | 0 | 0 | settled_lt_30, net_not_positive, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| 2 | `v2_reduce_p75_depth384_current_ge_minus10` | 24 | 16/8 | -22.000000 | 0.000000 | 22.000000 | 1 | 1/0 | 1/0 | 22.000000 | 0 | 0 | settled_lt_30, net_not_positive, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| 3 | `v2_reduce_p78_depth384` | 24 | 16/8 | -22.000000 | 0.000000 | 22.000000 | 1 | 1/0 | 1/0 | 22.000000 | 0 | 0 | settled_lt_30, net_not_positive, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| 4 | `v2_reduce_p77_depth384_current_ge_0` | 24 | 16/8 | -22.000000 | 0.000000 | 22.000000 | 1 | 1/0 | 1/0 | 22.000000 | 0 | 0 | settled_lt_30, net_not_positive, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| 5 | `v2_reduce_p79_depth384` | 24 | 16/8 | -22.000000 | 0.000000 | 22.000000 | 1 | 1/0 | 1/0 | 22.000000 | 0 | 0 | settled_lt_30, net_not_positive, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| 6 | `v2_reduce_p795_depth384` | 24 | 16/8 | -22.000000 | 0.000000 | 22.000000 | 1 | 1/0 | 1/0 | 22.000000 | 0 | 0 | settled_lt_30, net_not_positive, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| 7 | `v2_reduce_p80_depth384` | 24 | 16/8 | -22.000000 | 0.000000 | 22.000000 | 1 | 1/0 | 1/0 | 22.000000 | 0 | 0 | settled_lt_30, net_not_positive, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| 8 | `v2_reduce_p75_depth384` | 24 | 16/8 | -22.000000 | -120.000000 | -98.000000 | 2 | 1/1 | 1/1 | 22.000000 | -120.000000 | 0 | settled_lt_30, delta_not_positive, net_not_positive, suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |

### Suppressed Loser Rows

| variant | market | side | reason | current | hold | delta | p_hold | depth | gap | drawdown |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `v2_reduce_p75_depth384` | `KXBTC15M-26MAY062130-30` | `no` | `mushroom_v28_probability_reduce` | -32.000000 | -152.000000 | -120.000000 | 0.768407 | 24.000000 | 0.168407 | 6.159273 |
