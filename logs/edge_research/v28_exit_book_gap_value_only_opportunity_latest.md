# v28 Exit Book-Gap Value-Only Opportunity Denominator

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:16:26.004480+00:00`
- Freeze UTC: `2026-05-06T23:20:01.640880+00:00`
- Candidate: `value_only_gap15_or_p75`

## Interpretation

- This report explains opportunity availability only; it does not change the frozen value-only book-gap rule.
- Post-freeze rows 54, soft exits 40, value-over-hold exits 30, probability-reduce exits 10, would-suppress rows 18.
- Fail reasons are {'collapse_kept_by_value_only_rule': 5, 'not_value_over_hold_exit': 9, 'probability_reduce_kept_by_value_only_rule': 10, 'value_gap_below_floor': 12, 'value_p_hold_below_floor': 12}.
- Probability-reduce rows are expected to stay unsuppressed in this value-only watch.

## Summary

| rows | soft exits | value exits | reduce exits | collapse exits | would suppress | delta c | suppressed W/L | fail reasons |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 54 | 40 | 30 | 10 | 5 | 18 | -98.000000 | 16/2 | {'collapse_kept_by_value_only_rule': 5, 'not_value_over_hold_exit': 9, 'probability_reduce_kept_by_value_only_rule': 10, 'value_gap_below_floor': 12, 'value_p_hold_below_floor': 12} |

## Near Misses

| market | side | result | reason | entry | exit | p_hold | bid | gap | current c | hold c | delta if suppressed | fail reasons |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY062030-30 | no | no | mushroom_v28_exit_value_over_hold | 67 | 83 | 0.661475 | 0.830000 | -0.168525 | 32.000000 | 66.000000 | 34.000000 | value_gap_below_floor, value_p_hold_below_floor |
| KXBTC15M-26MAY062100-00 | yes | yes | mushroom_v28_exit_value_over_hold | 83 | 81 | 0.647591 | 0.810000 | -0.162409 | -4.000000 | 34.000000 | 38.000000 | value_gap_below_floor, value_p_hold_below_floor |
| KXBTC15M-26MAY062100-00 | yes | yes | mushroom_v28_exit_value_over_hold | 84 | 74 | 0.663692 | 0.740000 | -0.076308 | -20.000000 | 32.000000 | 52.000000 | value_gap_below_floor, value_p_hold_below_floor |
| KXBTC15M-26MAY062100-00 | yes | yes | mushroom_v28_exit_value_over_hold | 61 | 68 | 0.489234 | 0.680000 | -0.190766 | 14.000000 | 78.000000 | 64.000000 | value_gap_below_floor, value_p_hold_below_floor |
| KXBTC15M-26MAY062115-15 | yes | yes | mushroom_v28_exit_value_over_hold | 73 | 67 | 0.395750 | 0.670000 | -0.274250 | -12.000000 | 54.000000 | 66.000000 | value_gap_below_floor, value_p_hold_below_floor |
| KXBTC15M-26MAY062115-15 | no | yes | mushroom_v28_exit_value_over_hold | 69 | 52 | 0.455777 | 0.520000 | -0.064223 | -34.000000 | -138.000000 | -104.000000 | value_gap_below_floor, value_p_hold_below_floor |
| KXBTC15M-26MAY062245-45 | yes | yes | mushroom_v28_exit_value_over_hold | 86 | 90 | 0.643812 | 0.900000 | -0.256188 | 8.000000 | 28.000000 | 20.000000 | value_gap_below_floor, value_p_hold_below_floor |
| KXBTC15M-26MAY062300-00 | yes | yes | mushroom_v28_exit_value_over_hold | 87 | 95 | 0.746374 | 0.950000 | -0.203626 | 16.000000 | 26.000000 | 10.000000 | value_gap_below_floor, value_p_hold_below_floor |
| KXBTC15M-26MAY070000-00 | no | no | mushroom_v28_exit_value_over_hold | 78 | 79 | 0.726702 | 0.790000 | -0.063298 | 2.000000 | 44.000000 | 42.000000 | value_gap_below_floor, value_p_hold_below_floor |
| KXBTC15M-26MAY070015-15 | no | yes | mushroom_v28_exit_value_over_hold | 70 | 69 | 0.596562 | 0.690000 | -0.093438 | -2.000000 | -140.000000 | -138.000000 | value_gap_below_floor, value_p_hold_below_floor |
| KXBTC15M-26MAY070115-15 | yes | yes | mushroom_v28_exit_value_over_hold | 82 | 82 | 0.679619 | 0.820000 | -0.140381 | 0.000000 | 36.000000 | 36.000000 | value_gap_below_floor, value_p_hold_below_floor |
| KXBTC15M-26MAY070830-30 | no | no | mushroom_v28_exit_value_over_hold | 77 | 70 | 0.612998 | 0.700000 | -0.087002 | -14.000000 | 46.000000 | 60.000000 | value_gap_below_floor, value_p_hold_below_floor |

## Would Suppress

| market | side | result | reason | entry | exit | p_hold | bid | gap | current c | hold c | delta if suppressed |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY062015-15 | yes | no | mushroom_v28_exit_value_over_hold | 86 | 90 | 0.812359 | 0.900000 | -0.087641 | 8.000000 | -172.000000 | -180.000000 |
| KXBTC15M-26MAY062045-45 | no | no | mushroom_v28_exit_value_over_hold | 80 | 92 | 0.891386 | 0.920000 | -0.028614 | 24.000000 | 40.000000 | 16.000000 |
| KXBTC15M-26MAY062115-15 | yes | yes | mushroom_v28_exit_value_over_hold | 88 | 99 | 0.982461 | 0.990000 | -0.007539 | 22.000000 | 24.000000 | 2.000000 |
| KXBTC15M-26MAY062215-15 | no | no | mushroom_v28_exit_value_over_hold | 84 | 89 | 0.860673 | 0.890000 | -0.029327 | 10.000000 | 32.000000 | 22.000000 |
| KXBTC15M-26MAY062315-15 | no | no | mushroom_v28_exit_value_over_hold | 84 | 87 | 0.811182 | 0.870000 | -0.058818 | 6.000000 | 32.000000 | 26.000000 |
| KXBTC15M-26MAY070030-30 | yes | yes | mushroom_v28_exit_value_over_hold | 82 | 97 | 0.921778 | 0.970000 | -0.048222 | 30.000000 | 36.000000 | 6.000000 |
| KXBTC15M-26MAY070545-45 | no | no | mushroom_v28_exit_value_over_hold | 82 | 91 | 0.892567 | 0.910000 | -0.017433 | 18.000000 | 36.000000 | 18.000000 |
| KXBTC15M-26MAY070745-45 | yes | yes | mushroom_v28_exit_value_over_hold | 68 | 85 | 0.821701 | 0.850000 | -0.028299 | 34.000000 | 64.000000 | 30.000000 |
| KXBTC15M-26MAY070815-15 | yes | yes | mushroom_v28_exit_value_over_hold | 90 | 91 | 0.890464 | 0.910000 | -0.019536 | 2.000000 | 20.000000 | 18.000000 |
| KXBTC15M-26MAY070830-30 | no | no | mushroom_v28_exit_value_over_hold | 82 | 91 | 0.825354 | 0.910000 | -0.084646 | 18.000000 | 36.000000 | 18.000000 |
| KXBTC15M-26MAY070930-30 | yes | yes | mushroom_v28_exit_value_over_hold | 80 | 97 | 0.969995 | 0.980000 | -0.010005 | 34.000000 | 40.000000 | 6.000000 |
| KXBTC15M-26MAY071015-15 | yes | yes | mushroom_v28_exit_value_over_hold | 84 | 94 | 0.923102 | 0.940000 | -0.016898 | 20.000000 | 32.000000 | 12.000000 |
