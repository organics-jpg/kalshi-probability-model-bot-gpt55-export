# v28 Exit Reduce Loss-Control Refinement

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:13:54.697075+00:00`
- Refinement freeze UTC: `2026-05-06T20:08:44.785765+00:00`

## Interpretation

- This is a forward-only refinement watch; pre-birth rows are diagnostic and cannot promote the rule.
- diagnostic_from_reduce_freeze: best diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_079_or_drawdown_lte_2p5 settled 132, delta 677.0c, suppressed 23 W/L 20/3, loss-control cost -464.0c, blockers ['suppressed_losers_present', 'suppressed_loss_control_cost_negative'].
- post_refinement_birth: best post_refinement_birth_reduce_suppress_p_hold_ge_079 settled 60, delta 94.0c, suppressed 2 W/L 2/0, loss-control cost 0c, blockers ['full_loss_cushion_lt_3'].

## diagnostic_from_reduce_freeze

| rank | candidate | settled | current c | candidate c | delta c | suppressed | sup W/L | recovery c | loss cost c | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_079_or_drawdown_lte_2p5 | 132 | 721.000000 | 1398.000000 | 677.000000 | 23 | 20/3 | 1141.000000 | -464.000000 | 6 | suppressed_losers_present, suppressed_loss_control_cost_negative |
| 2 | diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_079 | 132 | 721.000000 | 1078.000000 | 357.000000 | 11 | 10/1 | 517.000000 | -160.000000 | 3 | suppressed_losers_present, suppressed_loss_control_cost_negative |
| 3 | diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_075_drawdown_lte_2p5 | 132 | 721.000000 | 1026.000000 | 305.000000 | 13 | 11/2 | 609.000000 | -304.000000 | 3 | suppressed_losers_present, suppressed_loss_control_cost_negative |
| 4 | diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_075_fair_drawdown_lte_0 | 132 | 721.000000 | 818.000000 | 97.000000 | 9 | 7/2 | 401.000000 | -304.000000 | 0 | suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |

### Best Suppressed Rows

| market | side | result | reason | p_hold | drawdown | current c | hold c | delta c | side won | worst mark |
|---|---|---|---|---:|---:|---:|---:|---:|---|---:|
| KXBTC15M-26MAY060700-00 | no | yes | mushroom_v28_probability_reduce | 0.799603 | 4.039746 | -8.000000 | -168.000000 | -160.000000 | False | 10 |
| KXBTC15M-26MAY071015-15 | no | yes | mushroom_v28_probability_reduce | 0.789130 | -0.913001 | 2.000000 | -156.000000 | -158.000000 | False | 18 |
| KXBTC15M-26MAY060900-00 | yes | no | mushroom_v28_probability_reduce | 0.789990 | -0.998969 | -10.000000 | -156.000000 | -146.000000 | False | 34 |
| KXBTC15M-26MAY061045-45 | yes | yes | mushroom_v28_probability_reduce | 0.796949 | 0.305083 | -6.000000 | 40.000000 | 46.000000 | True | 28 |
| KXBTC15M-26MAY061445-45 | no | no | mushroom_v28_probability_reduce | 0.797830 | 8.216985 | -22.000000 | 24.000000 | 46.000000 | True | 14 |
| KXBTC15M-26MAY071315-15 | yes | yes | mushroom_v28_probability_reduce | 0.798341 | -0.834147 | -6.000000 | 40.000000 | 46.000000 | True | 28 |
| KXBTC15M-26MAY060245-45 | yes | yes | mushroom_v28_probability_reduce | 0.793334 | 2.666578 | -8.000000 | 40.000000 | 48.000000 | True | 40 |
| KXBTC15M-26MAY071215-15 | no | no | mushroom_v28_probability_reduce | 0.797661 | 4.233856 | -16.000000 | 32.000000 | 48.000000 | True | -28 |
| KXBTC15M-26MAY060245-45 | yes | yes | mushroom_v28_probability_reduce | 0.749392 | 2.060750 | -6.000000 | 46.000000 | 52.000000 | True | 40 |
| KXBTC15M-26MAY060645-45 | yes | yes | mushroom_v28_probability_reduce | 0.799349 | 2.065125 | -16.000000 | 36.000000 | 52.000000 | True | 30 |
| KXBTC15M-26MAY060630-30 | yes | yes | mushroom_v28_probability_reduce | 0.777774 | 1.222639 | -12.000000 | 42.000000 | 54.000000 | True | 26 |
| KXBTC15M-26MAY061030-30 | yes | yes | mushroom_v28_probability_reduce | 0.796458 | -1.645773 | -10.000000 | 44.000000 | 54.000000 | True | -10 |
| KXBTC15M-26MAY060645-45 | yes | yes | mushroom_v28_probability_reduce | 0.779789 | 0.021114 | -12.000000 | 44.000000 | 56.000000 | True | 30 |
| KXBTC15M-26MAY071230-30 | yes | yes | mushroom_v28_probability_reduce | 0.749378 | 2.062161 | -10.000000 | 46.000000 | 56.000000 | True | -34 |
| KXBTC15M-26MAY060930-30 | no | no | mushroom_v28_probability_reduce | 0.799180 | -6.917970 | -3.000000 | 54.000000 | 57.000000 | True | -10 |
| KXBTC15M-26MAY060915-15 | no | no | mushroom_v28_probability_reduce | 0.793762 | -9.376204 | 0.000000 | 60.000000 | 60.000000 | True | 48 |
| KXBTC15M-26MAY061015-15 | no | no | mushroom_v28_probability_reduce | 0.799979 | -9.997858 | 0.000000 | 60.000000 | 60.000000 | True | 4 |
| KXBTC15M-26MAY060930-30 | no | no | mushroom_v28_probability_reduce | 0.787606 | -2.760587 | -14.000000 | 48.000000 | 62.000000 | True | -10 |
| KXBTC15M-26MAY071045-45 | no | no | mushroom_v28_probability_reduce | 0.760529 | -2.052947 | -10.000000 | 52.000000 | 62.000000 | True | -14 |
| KXBTC15M-26MAY060900-00 | no | no | mushroom_v28_probability_reduce | 0.721102 | 0.889760 | -16.000000 | 54.000000 | 70.000000 | True | 34 |
| KXBTC15M-26MAY060945-45 | no | no | mushroom_v28_probability_reduce | 0.735773 | -2.577325 | -12.000000 | 58.000000 | 70.000000 | True | 40 |
| KXBTC15M-26MAY061015-15 | no | no | mushroom_v28_probability_reduce | 0.733426 | -5.342610 | -6.000000 | 64.000000 | 70.000000 | True | 4 |
| KXBTC15M-26MAY060700-00 | yes | yes | mushroom_v28_probability_reduce | 0.748579 | 0.142079 | -22.000000 | 50.000000 | 72.000000 | True | 10 |

## post_refinement_birth

| rank | candidate | settled | current c | candidate c | delta c | suppressed | sup W/L | recovery c | loss cost c | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | post_refinement_birth_reduce_suppress_p_hold_ge_079 | 60 | 388.000000 | 482.000000 | 94.000000 | 2 | 2/0 | 94.000000 | 0 | 0 | full_loss_cushion_lt_3 |
| 2 | post_refinement_birth_reduce_suppress_p_hold_ge_079_or_drawdown_lte_2p5 | 60 | 388.000000 | 442.000000 | 54.000000 | 5 | 4/1 | 212.000000 | -158.000000 | 0 | suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 3 | post_refinement_birth_reduce_suppress_p_hold_ge_075_drawdown_lte_2p5 | 60 | 388.000000 | 338.000000 | -50.000000 | 3 | 2/1 | 108.000000 | -158.000000 | 0 | delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 4 | post_refinement_birth_reduce_suppress_p_hold_ge_075_fair_drawdown_lte_0 | 60 | 388.000000 | 338.000000 | -50.000000 | 3 | 2/1 | 108.000000 | -158.000000 | 0 | delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |

### Best Suppressed Rows

| market | side | result | reason | p_hold | drawdown | current c | hold c | delta c | side won | worst mark |
|---|---|---|---|---:|---:|---:|---:|---:|---|---:|
| KXBTC15M-26MAY071315-15 | yes | yes | mushroom_v28_probability_reduce | 0.798341 | -0.834147 | -6.000000 | 40.000000 | 46.000000 | True | 28 |
| KXBTC15M-26MAY071215-15 | no | no | mushroom_v28_probability_reduce | 0.797661 | 4.233856 | -16.000000 | 32.000000 | 48.000000 | True | -28 |
