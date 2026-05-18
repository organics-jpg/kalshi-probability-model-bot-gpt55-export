# v28 Exit Book-Gap Loss-Guard V3 Opportunity Denominator

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:44:59.174947+00:00`
- Freeze UTC: `2026-05-07T01:01:45.501061+00:00`
- Candidate: `book_gap_loss_guard_v3_value_gap0_or_p85_shallow_or_p95_extreme_reduce_p79_gap0`

## Interpretation

- This report explains opportunity availability only; it does not change the frozen v3 loss guard.
- Post-freeze rows 46, soft exits 34, value-over-hold exits 24, probability-reduce exits 10, v3 would-suppress rows 9.
- V3-only would-suppress rows 4 for 14.0c; this is the strict-forward cost/benefit of relaxing v2.
- Fail reasons are {'not_soft_exit': 12, 'reduce_gap_below_floor': 2, 'reduce_p_hold_below_floor': 8, 'value_extreme_p_hold_below_floor': 17, 'value_fair_drawdown_too_deep': 5, 'value_gap_below_floor': 17, 'value_p_hold_below_floor': 13}.

## Summary

| rows | soft exits | value exits | reduce exits | v2 suppress | v3 suppress | v3-only | v3 delta | v3-only delta | fail reasons |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 46 | 34 | 24 | 10 | 5 | 9 | 4 | 166.000000 | 14.000000 | {'not_soft_exit': 12, 'reduce_gap_below_floor': 2, 'reduce_p_hold_below_floor': 8, 'value_extreme_p_hold_below_floor': 17, 'value_fair_drawdown_too_deep': 5, 'value_gap_below_floor': 17, 'value_p_hold_below_floor': 13} |

## V3-Only Opportunities

| market | side | result | reason | entry | exit | p_hold | bid | gap | drawdown | current c | hold c | delta if suppressed | v2/v3 | fail reasons |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY062115-15 | yes | yes | mushroom_v28_exit_value_over_hold | 88 | 99 | 0.982461 | 0.990000 | -0.007539 | -10.246054 | 22.000000 | 24.000000 | 2.000000 | False/True |  |
| KXBTC15M-26MAY070930-30 | yes | yes | mushroom_v28_exit_value_over_hold | 80 | 97 | 0.969995 | 0.980000 | -0.010005 | -13.999536 | 34.000000 | 40.000000 | 6.000000 | False/True |  |
| KXBTC15M-26MAY071145-45 | yes | yes | mushroom_v28_exit_value_over_hold | 77 | 99 | 0.982146 | 0.990000 | -0.007854 | -17.214598 | 44.000000 | 46.000000 | 2.000000 | False/True |  |
| KXBTC15M-26MAY071200-00 | no | no | mushroom_v28_exit_value_over_hold | 77 | 98 | 0.961165 | 0.980000 | -0.018835 | -19.116535 | 42.000000 | 46.000000 | 4.000000 | False/True |  |

## Near Misses

| market | side | result | reason | entry | exit | p_hold | bid | gap | drawdown | current c | hold c | delta if suppressed | v2/v3 | fail reasons |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY062115-15 | yes | yes | mushroom_v28_exit_value_over_hold | 73 | 67 | 0.395750 | 0.670000 | -0.274250 | 33.425046 | -12.000000 | 54.000000 | 66.000000 | False/False | value_gap_below_floor, value_p_hold_below_floor, value_extreme_p_hold_below_floor |
| KXBTC15M-26MAY062115-15 | no | yes | mushroom_v28_exit_value_over_hold | 69 | 52 | 0.455777 | 0.520000 | -0.064223 | 14.422271 | -34.000000 | -138.000000 | -104.000000 | False/False | value_gap_below_floor, value_p_hold_below_floor, value_extreme_p_hold_below_floor |
| KXBTC15M-26MAY062130-30 | no | yes | mushroom_v28_probability_reduce | 76 | 60 | 0.768407 | 0.600000 | 0.168407 | 6.159273 | -32.000000 | -152.000000 | -120.000000 | False/False | reduce_p_hold_below_floor |
| KXBTC15M-26MAY062245-45 | yes | yes | mushroom_v28_exit_value_over_hold | 86 | 90 | 0.643812 | 0.900000 | -0.256188 | 15.618779 | 8.000000 | 28.000000 | 20.000000 | False/False | value_gap_below_floor, value_p_hold_below_floor, value_extreme_p_hold_below_floor |
| KXBTC15M-26MAY062300-00 | yes | yes | mushroom_v28_exit_value_over_hold | 87 | 95 | 0.746374 | 0.950000 | -0.203626 | 10.362646 | 16.000000 | 26.000000 | 10.000000 | False/False | value_gap_below_floor, value_p_hold_below_floor, value_extreme_p_hold_below_floor |
| KXBTC15M-26MAY062315-15 | no | no | mushroom_v28_exit_value_over_hold | 84 | 87 | 0.811182 | 0.870000 | -0.058818 | 2.881757 | 6.000000 | 32.000000 | 26.000000 | False/False | value_gap_below_floor, value_p_hold_below_floor, value_extreme_p_hold_below_floor |
| KXBTC15M-26MAY070000-00 | no | no | mushroom_v28_exit_value_over_hold | 78 | 79 | 0.726702 | 0.790000 | -0.063298 | 5.329808 | 2.000000 | 44.000000 | 42.000000 | False/False | value_gap_below_floor, value_p_hold_below_floor, value_extreme_p_hold_below_floor |
| KXBTC15M-26MAY070015-15 | no | yes | mushroom_v28_exit_value_over_hold | 70 | 69 | 0.596562 | 0.690000 | -0.093438 | 10.343815 | -2.000000 | -140.000000 | -138.000000 | False/False | value_gap_below_floor, value_p_hold_below_floor, value_extreme_p_hold_below_floor |
| KXBTC15M-26MAY070030-30 | yes | yes | mushroom_v28_exit_value_over_hold | 82 | 97 | 0.921778 | 0.970000 | -0.048222 | -10.177771 | 30.000000 | 36.000000 | 6.000000 | False/False | value_gap_below_floor, value_fair_drawdown_too_deep, value_extreme_p_hold_below_floor |
| KXBTC15M-26MAY070115-15 | yes | yes | mushroom_v28_exit_value_over_hold | 82 | 82 | 0.679619 | 0.820000 | -0.140381 | 18.038087 | 0.000000 | 36.000000 | 36.000000 | False/False | value_gap_below_floor, value_p_hold_below_floor, value_extreme_p_hold_below_floor |
| KXBTC15M-26MAY070545-45 | no | no | mushroom_v28_exit_value_over_hold | 82 | 91 | 0.892567 | 0.910000 | -0.017433 | -7.256748 | 18.000000 | 36.000000 | 18.000000 | False/False | value_gap_below_floor, value_fair_drawdown_too_deep, value_extreme_p_hold_below_floor |
| KXBTC15M-26MAY070745-45 | yes | yes | mushroom_v28_exit_value_over_hold | 68 | 85 | 0.821701 | 0.850000 | -0.028299 | -14.170103 | 34.000000 | 64.000000 | 30.000000 | False/False | value_gap_below_floor, value_p_hold_below_floor, value_fair_drawdown_too_deep, value_extreme_p_hold_below_floor |
