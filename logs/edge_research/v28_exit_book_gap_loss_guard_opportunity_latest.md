# v28 Exit Book-Gap Loss-Guard Opportunity Denominator

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:16:23.989417+00:00`
- Freeze UTC: `2026-05-06T21:29:32.710906+00:00`
- Candidate: `book_gap_loss_guard_value_p85_reduce_p79_gap0`

## Interpretation

- This report explains opportunity availability only; it does not change the frozen book-gap loss guard.
- Post-freeze rows 59, soft exits 43, value-over-hold exits 33, probability-reduce exits 10, would-suppress rows 17.
- Fail reasons are {'not_soft_exit': 16, 'reduce_gap_below_floor': 2, 'reduce_p_hold_below_floor': 8, 'value_gap_below_floor': 18, 'value_p_hold_below_floor': 18}.

## Summary

| rows | soft exits | value exits | reduce exits | would suppress | fail reasons |
|---:|---:|---:|---:|---:|---|
| 59 | 43 | 33 | 10 | 17 | {'not_soft_exit': 16, 'reduce_gap_below_floor': 2, 'reduce_p_hold_below_floor': 8, 'value_gap_below_floor': 18, 'value_p_hold_below_floor': 18} |

## Near Misses

| market | side | result | reason | entry | exit | p_hold | bid | gap | current c | hold c | delta if suppressed | fail reasons |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY062015-15 | yes | no | mushroom_v28_exit_value_over_hold | 86 | 90 | 0.812359 | 0.900000 | -0.087641 | 8.000000 | -172.000000 | -180.000000 | value_p_hold_below_floor, value_gap_below_floor |
| KXBTC15M-26MAY062030-30 | no | no | mushroom_v28_exit_value_over_hold | 67 | 83 | 0.661475 | 0.830000 | -0.168525 | 32.000000 | 66.000000 | 34.000000 | value_p_hold_below_floor, value_gap_below_floor |
| KXBTC15M-26MAY062100-00 | yes | yes | mushroom_v28_exit_value_over_hold | 83 | 81 | 0.647591 | 0.810000 | -0.162409 | -4.000000 | 34.000000 | 38.000000 | value_p_hold_below_floor, value_gap_below_floor |
| KXBTC15M-26MAY062100-00 | yes | yes | mushroom_v28_exit_value_over_hold | 84 | 74 | 0.663692 | 0.740000 | -0.076308 | -20.000000 | 32.000000 | 52.000000 | value_p_hold_below_floor, value_gap_below_floor |
| KXBTC15M-26MAY062100-00 | yes | yes | mushroom_v28_exit_value_over_hold | 61 | 68 | 0.489234 | 0.680000 | -0.190766 | 14.000000 | 78.000000 | 64.000000 | value_p_hold_below_floor, value_gap_below_floor |
| KXBTC15M-26MAY062115-15 | yes | yes | mushroom_v28_exit_value_over_hold | 73 | 67 | 0.395750 | 0.670000 | -0.274250 | -12.000000 | 54.000000 | 66.000000 | value_p_hold_below_floor, value_gap_below_floor |
| KXBTC15M-26MAY062115-15 | no | yes | mushroom_v28_exit_value_over_hold | 69 | 52 | 0.455777 | 0.520000 | -0.064223 | -34.000000 | -138.000000 | -104.000000 | value_p_hold_below_floor, value_gap_below_floor |
| KXBTC15M-26MAY062130-30 | no | yes | mushroom_v28_probability_reduce | 76 | 60 | 0.768407 | 0.600000 | 0.168407 | -32.000000 | -152.000000 | -120.000000 | reduce_p_hold_below_floor |
| KXBTC15M-26MAY062245-45 | yes | yes | mushroom_v28_exit_value_over_hold | 86 | 90 | 0.643812 | 0.900000 | -0.256188 | 8.000000 | 28.000000 | 20.000000 | value_p_hold_below_floor, value_gap_below_floor |
| KXBTC15M-26MAY062300-00 | yes | yes | mushroom_v28_exit_value_over_hold | 87 | 95 | 0.746374 | 0.950000 | -0.203626 | 16.000000 | 26.000000 | 10.000000 | value_p_hold_below_floor, value_gap_below_floor |
| KXBTC15M-26MAY062315-15 | no | no | mushroom_v28_exit_value_over_hold | 84 | 87 | 0.811182 | 0.870000 | -0.058818 | 6.000000 | 32.000000 | 26.000000 | value_p_hold_below_floor, value_gap_below_floor |
| KXBTC15M-26MAY070000-00 | no | no | mushroom_v28_exit_value_over_hold | 78 | 79 | 0.726702 | 0.790000 | -0.063298 | 2.000000 | 44.000000 | 42.000000 | value_p_hold_below_floor, value_gap_below_floor |
