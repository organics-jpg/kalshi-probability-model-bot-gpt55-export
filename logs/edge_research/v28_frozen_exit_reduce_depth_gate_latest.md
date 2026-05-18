# v28 Frozen Exit Reduce Entry-Depth Gate

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:14:06.357762+00:00`
- Depth-gate freeze UTC: `2026-05-06T20:19:43.176664+00:00`

## Interpretation

- This is a forward-only entry-depth gate watch; pre-birth rows are diagnostic and cannot promote the rule.
- Origin separator was entry_depth le 384.0: selected W/L 11/0 and delta 587.0c.
- diagnostic_from_reduce_freeze: best diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_079_entry_depth_lte_384 settled 132, delta 397.0c, suppressed 8 W/L 8/0, loss-control cost 0c, blockers [].
- post_depth_gate_birth: best post_depth_gate_birth_reduce_suppress_p_hold_ge_079_entry_depth_lte_384 settled 60, delta 94.0c, suppressed 2 W/L 2/0, loss-control cost 0c, blockers ['full_loss_cushion_lt_3'].

## diagnostic_from_reduce_freeze

| rank | candidate | settled | current c | candidate c | delta c | suppressed | sup W/L | recovery c | loss cost c | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_079_entry_depth_lte_384 | 132 | 721.000000 | 1118.000000 | 397.000000 | 8 | 8/0 | 397.000000 | 0 | 3 | none |
| 2 | diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_075_entry_depth_lte_384 | 132 | 721.000000 | 1134.000000 | 413.000000 | 19 | 16/3 | 837.000000 | -424.000000 | 4 | suppressed_losers_present, suppressed_loss_control_cost_negative |
| 3 | diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_075_entry_depth_lte_295 | 132 | 721.000000 | 1082.000000 | 361.000000 | 18 | 15/3 | 785.000000 | -424.000000 | 3 | suppressed_losers_present, suppressed_loss_control_cost_negative |
| 4 | diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_075_entry_depth_lte_384_drawdown_lte_2p5 | 132 | 721.000000 | 990.000000 | 269.000000 | 9 | 8/1 | 427.000000 | -158.000000 | 2 | suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |

### Best Suppressed Rows

| market | side | result | reason | depth | p_hold | drawdown | current c | hold c | delta c | side won | worst mark |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| KXBTC15M-26MAY061045-45 | yes | yes | mushroom_v28_probability_reduce | 185.000000 | 0.796949 | 0.305083 | -6.000000 | 40.000000 | 46.000000 | True | 28 |
| KXBTC15M-26MAY061445-45 | no | no | mushroom_v28_probability_reduce | 55.000000 | 0.797830 | 8.216985 | -22.000000 | 24.000000 | 46.000000 | True | 14 |
| KXBTC15M-26MAY071315-15 | yes | yes | mushroom_v28_probability_reduce | 73.580000 | 0.798341 | -0.834147 | -6.000000 | 40.000000 | 46.000000 | True | 28 |
| KXBTC15M-26MAY060245-45 | yes | yes | mushroom_v28_probability_reduce | 40.000000 | 0.793334 | 2.666578 | -8.000000 | 40.000000 | 48.000000 | True | 40 |
| KXBTC15M-26MAY071215-15 | no | no | mushroom_v28_probability_reduce | 8.000000 | 0.797661 | 4.233856 | -16.000000 | 32.000000 | 48.000000 | True | -28 |
| KXBTC15M-26MAY060645-45 | yes | yes | mushroom_v28_probability_reduce | 384.000000 | 0.799349 | 2.065125 | -16.000000 | 36.000000 | 52.000000 | True | 30 |
| KXBTC15M-26MAY061030-30 | yes | yes | mushroom_v28_probability_reduce | 295.000000 | 0.796458 | -1.645773 | -10.000000 | 44.000000 | 54.000000 | True | -10 |
| KXBTC15M-26MAY060930-30 | no | no | mushroom_v28_probability_reduce | 179.000000 | 0.799180 | -6.917970 | -3.000000 | 54.000000 | 57.000000 | True | -10 |

## post_depth_gate_birth

| rank | candidate | settled | current c | candidate c | delta c | suppressed | sup W/L | recovery c | loss cost c | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | post_depth_gate_birth_reduce_suppress_p_hold_ge_079_entry_depth_lte_384 | 60 | 388.000000 | 482.000000 | 94.000000 | 2 | 2/0 | 94.000000 | 0 | 0 | full_loss_cushion_lt_3 |
| 2 | post_depth_gate_birth_reduce_suppress_p_hold_ge_075_entry_depth_lte_384_drawdown_lte_2p5 | 60 | 388.000000 | 338.000000 | -50.000000 | 3 | 2/1 | 108.000000 | -158.000000 | 0 | delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 3 | post_depth_gate_birth_reduce_suppress_p_hold_ge_075_entry_depth_lte_384 | 60 | 388.000000 | 214.000000 | -174.000000 | 8 | 5/3 | 250.000000 | -424.000000 | 0 | delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 4 | post_depth_gate_birth_reduce_suppress_p_hold_ge_075_entry_depth_lte_295 | 60 | 388.000000 | 214.000000 | -174.000000 | 8 | 5/3 | 250.000000 | -424.000000 | 0 | delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |

### Best Suppressed Rows

| market | side | result | reason | depth | p_hold | drawdown | current c | hold c | delta c | side won | worst mark |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| KXBTC15M-26MAY071315-15 | yes | yes | mushroom_v28_probability_reduce | 73.580000 | 0.798341 | -0.834147 | -6.000000 | 40.000000 | 46.000000 | True | 28 |
| KXBTC15M-26MAY071215-15 | no | no | mushroom_v28_probability_reduce | 8.000000 | 0.797661 | 4.233856 | -16.000000 | 32.000000 | 48.000000 | True | -28 |
