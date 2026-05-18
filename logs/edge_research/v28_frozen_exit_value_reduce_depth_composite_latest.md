# v28 Frozen Exit Value + Reduce-Depth Composite

Research-only frozen forward watch. No live bot changes.

- Generated UTC: `2026-05-11T03:44:48.341516+00:00`
- Freeze timestamp UTC: `2026-05-06T23:34:20.352483+00:00`
- Candidate: `value_v2_reduce_depth384`
- Rule: `Suppress value-over-hold exits using the v2 book/fair-drawdown guard; suppress probability_reduce exits only when p_hold >= 0.75 and entry_depth <= 384.`
- Any live-ready primary: `False`
- Primary blockers: `delta_not_positive, suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3`

## Interpretation

- Composite is frozen independently; diagnostic rows are not promotion evidence.
- Primary candidate combines v2 value-exit guard with reduce-depth p75/depth384 guard.
- diagnostic_from_exit_freezes: best value_v2_reduce_depth384_p79 settled 132, candidate 1188.0c, delta 467.0c, suppressed 12 value/reduce 4/8, suppressed W/L 12/0, loss cost 0c, blockers ['suppressed_decisions_lt_30'].
- post_composite_birth: best value_v2_reduce_depth384_p79 settled 54, candidate 490.0c, delta 152.0c, suppressed 5 value/reduce 3/2, suppressed W/L 5/0, loss cost 0c, blockers ['suppressed_decisions_lt_30'].

## diagnostic_from_exit_freezes

| rank | rule | settled | W/L | current c | candidate c | delta c | suppressed | value/reduce | suppressed W/L | recovery c | loss cost c | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `value_v2_reduce_depth384_p79` | 132 | 84/48 | 721.000000 | 1188.000000 | 467.000000 | 12 | 4/8 | 12/0 | 467.000000 | 0 | 11 | suppressed_decisions_lt_30 |
| 2 | `value_only_p75_reduce_depth384` | 132 | 88/44 | 721.000000 | 1230.000000 | 509.000000 | 61 | 42/19 | 56/5 | 1283.000000 | -774.000000 | 12 | suppressed_losers_present, suppressed_loss_control_cost_negative |
| 3 | `value_v2_reduce_depth384` | 132 | 90/42 | 721.000000 | 1204.000000 | 483.000000 | 23 | 4/19 | 20/3 | 907.000000 | -424.000000 | 12 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| 4 | `value_v2_reduce_depth295` | 132 | 89/43 | 721.000000 | 1152.000000 | 431.000000 | 22 | 4/18 | 19/3 | 855.000000 | -424.000000 | 11 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |

## post_composite_birth

| rank | rule | settled | W/L | current c | candidate c | delta c | suppressed | value/reduce | suppressed W/L | recovery c | loss cost c | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `value_v2_reduce_depth384_p79` | 54 | 37/17 | 338.000000 | 490.000000 | 152.000000 | 5 | 3/2 | 5/0 | 152.000000 | 0 | 4 | suppressed_decisions_lt_30 |
| 2 | `value_v2_reduce_depth384` | 54 | 38/16 | 338.000000 | 222.000000 | -116.000000 | 11 | 3/8 | 8/3 | 308.000000 | -424.000000 | 2 | delta_not_positive, suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 3 | `value_v2_reduce_depth295` | 54 | 38/16 | 338.000000 | 222.000000 | -116.000000 | 11 | 3/8 | 8/3 | 308.000000 | -424.000000 | 2 | delta_not_positive, suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 4 | `value_only_p75_reduce_depth384` | 54 | 36/18 | 338.000000 | 66.000000 | -272.000000 | 26 | 18/8 | 21/5 | 502.000000 | -774.000000 | 0 | delta_not_positive, suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
