# v28 Exit Book-Gap Loss-Guard V2 Opportunity Denominator

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:46:14.781129+00:00`
- Freeze UTC: `2026-05-06T22:01:04.415577+00:00`
- Candidate: `book_gap_loss_guard_v2_value_gap0_or_p85_shallowdd_reduce_p79_gap0`

## Interpretation

- This report explains opportunity availability only; it does not change the frozen v2 loss guard.
- Post-freeze rows 58, soft exits 43, value-over-hold exits 33, probability-reduce exits 10, would-suppress rows 5.
- Fail reasons are {'not_soft_exit': 15, 'reduce_gap_below_floor': 2, 'reduce_p_hold_below_floor': 8, 'value_fair_drawdown_too_deep': 13, 'value_gap_below_floor': 30, 'value_p_hold_below_floor': 18}.

## Summary

| rows | soft exits | value exits | reduce exits | would suppress | fail reasons |
|---:|---:|---:|---:|---:|---|
| 58 | 43 | 33 | 10 | 5 | {'not_soft_exit': 15, 'reduce_gap_below_floor': 2, 'reduce_p_hold_below_floor': 8, 'value_fair_drawdown_too_deep': 13, 'value_gap_below_floor': 30, 'value_p_hold_below_floor': 18} |

## Near Misses

| market | side | result | reason | entry | exit | p_hold | bid | gap | drawdown | current c | hold c | delta if suppressed | fail reasons |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY061815-15 | no | no | mushroom_v28_exit_value_over_hold | 84 | 96 | 0.950684 | 0.960000 | -0.009316 | -11.068394 | 24.000000 | 32.000000 | 8.000000 | value_gap_below_floor, value_fair_drawdown_too_deep |
| KXBTC15M-26MAY061830-30 | no | no | mushroom_v28_exit_value_over_hold | 89 | 99 | 0.976718 | 0.990000 | -0.013282 | -8.671753 | 20.000000 | 22.000000 | 2.000000 | value_gap_below_floor, value_fair_drawdown_too_deep |
| KXBTC15M-26MAY061915-15 | no | no | mushroom_v28_exit_value_over_hold | 87 | 99 | 0.981987 | 0.990000 | -0.008013 | -11.198704 | 24.000000 | 26.000000 | 2.000000 | value_gap_below_floor, value_fair_drawdown_too_deep |
| KXBTC15M-26MAY062015-15 | yes | no | mushroom_v28_exit_value_over_hold | 86 | 90 | 0.812359 | 0.900000 | -0.087641 | 4.764109 | 8.000000 | -172.000000 | -180.000000 | value_gap_below_floor, value_p_hold_below_floor |
| KXBTC15M-26MAY062030-30 | no | no | mushroom_v28_exit_value_over_hold | 67 | 83 | 0.661475 | 0.830000 | -0.168525 | 0.852486 | 32.000000 | 66.000000 | 34.000000 | value_gap_below_floor, value_p_hold_below_floor |
| KXBTC15M-26MAY062045-45 | no | no | mushroom_v28_exit_value_over_hold | 80 | 92 | 0.891386 | 0.920000 | -0.028614 | -9.138584 | 24.000000 | 40.000000 | 16.000000 | value_gap_below_floor, value_fair_drawdown_too_deep |
| KXBTC15M-26MAY062100-00 | yes | yes | mushroom_v28_exit_value_over_hold | 83 | 81 | 0.647591 | 0.810000 | -0.162409 | 18.240924 | -4.000000 | 34.000000 | 38.000000 | value_gap_below_floor, value_p_hold_below_floor |
| KXBTC15M-26MAY062100-00 | yes | yes | mushroom_v28_exit_value_over_hold | 84 | 74 | 0.663692 | 0.740000 | -0.076308 | 17.630840 | -20.000000 | 32.000000 | 52.000000 | value_gap_below_floor, value_p_hold_below_floor |
| KXBTC15M-26MAY062100-00 | yes | yes | mushroom_v28_exit_value_over_hold | 61 | 68 | 0.489234 | 0.680000 | -0.190766 | 12.076646 | 14.000000 | 78.000000 | 64.000000 | value_gap_below_floor, value_p_hold_below_floor |
| KXBTC15M-26MAY062115-15 | yes | yes | mushroom_v28_exit_value_over_hold | 73 | 67 | 0.395750 | 0.670000 | -0.274250 | 33.425046 | -12.000000 | 54.000000 | 66.000000 | value_gap_below_floor, value_p_hold_below_floor |
| KXBTC15M-26MAY062115-15 | no | yes | mushroom_v28_exit_value_over_hold | 69 | 52 | 0.455777 | 0.520000 | -0.064223 | 14.422271 | -34.000000 | -138.000000 | -104.000000 | value_gap_below_floor, value_p_hold_below_floor |
| KXBTC15M-26MAY062115-15 | yes | yes | mushroom_v28_exit_value_over_hold | 88 | 99 | 0.982461 | 0.990000 | -0.007539 | -10.246054 | 22.000000 | 24.000000 | 2.000000 | value_gap_below_floor, value_fair_drawdown_too_deep |
