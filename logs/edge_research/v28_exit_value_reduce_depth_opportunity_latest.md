# v28 Exit Value + Reduce-Depth Opportunity Denominator

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:44:56.633736+00:00`
- Freeze UTC: `2026-05-06T23:34:20.352483+00:00`
- Primary rule: `value_v2_reduce_depth384`

## Interpretation

- This report explains opportunity availability only; it does not change the frozen value/reduce-depth composite.
- Primary value_v2_reduce_depth384 has post-freeze rows 54, value exits 30, reduce exits 10, would-suppress rows 11 (3/8 value/reduce), and delta -116.0c.
- Promotion runway still needs 0 settled rows, 19 suppressed decisions, and 78.0c for a three-full-loss cushion.
- Fail reasons are {'collapse_kept_by_composite_rule': 5, 'not_value_or_reduce_exit': 9, 'reduce_entry_depth_above_ceiling': 1, 'reduce_p_hold_below_floor': 1, 'value_fair_drawdown_too_deep': 10, 'value_gap_negative': 27, 'value_p_hold_below_85': 18}.

## Rules

| rule | rows | value exits | reduce exits | would suppress | value/reduce | delta c | net c | rows needed | suppressions needed | cushion c needed | fail reasons |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `value_v2_reduce_depth384_p79` | 54 | 30 | 10 | 5 | 3/2 | 152.000000 | 490.000000 | 0 | 25 | 0.000000 | {'collapse_kept_by_composite_rule': 5, 'not_value_or_reduce_exit': 9, 'reduce_entry_depth_above_ceiling': 1, 'reduce_p_hold_below_floor': 8, 'value_fair_drawdown_too_deep': 10, 'value_gap_negative': 27, 'value_p_hold_below_85': 18} |
| `value_v2_reduce_depth295` | 54 | 30 | 10 | 11 | 3/8 | -116.000000 | 222.000000 | 0 | 19 | 78.000000 | {'collapse_kept_by_composite_rule': 5, 'not_value_or_reduce_exit': 9, 'reduce_entry_depth_above_ceiling': 1, 'reduce_p_hold_below_floor': 1, 'value_fair_drawdown_too_deep': 10, 'value_gap_negative': 27, 'value_p_hold_below_85': 18} |
| `value_v2_reduce_depth384` | 54 | 30 | 10 | 11 | 3/8 | -116.000000 | 222.000000 | 0 | 19 | 78.000000 | {'collapse_kept_by_composite_rule': 5, 'not_value_or_reduce_exit': 9, 'reduce_entry_depth_above_ceiling': 1, 'reduce_p_hold_below_floor': 1, 'value_fair_drawdown_too_deep': 10, 'value_gap_negative': 27, 'value_p_hold_below_85': 18} |
| `value_only_p75_reduce_depth384` | 54 | 30 | 10 | 26 | 18/8 | -272.000000 | 66.000000 | 0 | 4 | 234.000000 | {'collapse_kept_by_composite_rule': 5, 'not_value_or_reduce_exit': 9, 'reduce_entry_depth_above_ceiling': 1, 'reduce_p_hold_below_floor': 1, 'value_gap_below_15': 12, 'value_p_hold_below_75': 12} |

## Near Misses

| market | side | result | reason | entry | exit | depth | p_hold | bid | gap | drawdown | current c | hold c | delta if suppressed | fail reasons |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY062015-15 | yes | no | mushroom_v28_exit_value_over_hold | 86 | 90 | 1557.140000 | 0.812359 | 0.900000 | -0.087641 | 4.764109 | 8.000000 | -172.000000 | -180.000000 | value_gap_negative, value_p_hold_below_85 |
| KXBTC15M-26MAY062030-30 | no | no | mushroom_v28_exit_value_over_hold | 67 | 83 | 192.080000 | 0.661475 | 0.830000 | -0.168525 | 0.852486 | 32.000000 | 66.000000 | 34.000000 | value_gap_negative, value_p_hold_below_85 |
| KXBTC15M-26MAY062045-45 | no | no | mushroom_v28_exit_value_over_hold | 80 | 92 | 182.480000 | 0.891386 | 0.920000 | -0.028614 | -9.138584 | 24.000000 | 40.000000 | 16.000000 | value_gap_negative, value_fair_drawdown_too_deep |
| KXBTC15M-26MAY062100-00 | yes | yes | mushroom_v28_exit_value_over_hold | 83 | 81 | 1091.930000 | 0.647591 | 0.810000 | -0.162409 | 18.240924 | -4.000000 | 34.000000 | 38.000000 | value_gap_negative, value_p_hold_below_85 |
| KXBTC15M-26MAY062100-00 | yes | yes | mushroom_v28_exit_value_over_hold | 84 | 74 | 65.000000 | 0.663692 | 0.740000 | -0.076308 | 17.630840 | -20.000000 | 32.000000 | 52.000000 | value_gap_negative, value_p_hold_below_85 |
| KXBTC15M-26MAY062100-00 | yes | yes | mushroom_v28_exit_value_over_hold | 61 | 68 | 633.000000 | 0.489234 | 0.680000 | -0.190766 | 12.076646 | 14.000000 | 78.000000 | 64.000000 | value_gap_negative, value_p_hold_below_85 |
| KXBTC15M-26MAY062115-15 | yes | yes | mushroom_v28_exit_value_over_hold | 73 | 67 | 1252.350000 | 0.395750 | 0.670000 | -0.274250 | 33.425046 | -12.000000 | 54.000000 | 66.000000 | value_gap_negative, value_p_hold_below_85 |
| KXBTC15M-26MAY062115-15 | no | yes | mushroom_v28_exit_value_over_hold | 69 | 52 | 111.000000 | 0.455777 | 0.520000 | -0.064223 | 14.422271 | -34.000000 | -138.000000 | -104.000000 | value_gap_negative, value_p_hold_below_85 |
| KXBTC15M-26MAY062115-15 | yes | yes | mushroom_v28_exit_value_over_hold | 88 | 99 | 50.000000 | 0.982461 | 0.990000 | -0.007539 | -10.246054 | 22.000000 | 24.000000 | 2.000000 | value_gap_negative, value_fair_drawdown_too_deep |
| KXBTC15M-26MAY062245-45 | yes | yes | mushroom_v28_exit_value_over_hold | 86 | 90 | 2329.710000 | 0.643812 | 0.900000 | -0.256188 | 15.618779 | 8.000000 | 28.000000 | 20.000000 | value_gap_negative, value_p_hold_below_85 |
| KXBTC15M-26MAY062300-00 | yes | yes | mushroom_v28_exit_value_over_hold | 87 | 95 | 1125.390000 | 0.746374 | 0.950000 | -0.203626 | 10.362646 | 16.000000 | 26.000000 | 10.000000 | value_gap_negative, value_p_hold_below_85 |
| KXBTC15M-26MAY062315-15 | no | no | mushroom_v28_exit_value_over_hold | 84 | 87 | 54.000000 | 0.811182 | 0.870000 | -0.058818 | 2.881757 | 6.000000 | 32.000000 | 26.000000 | value_gap_negative, value_p_hold_below_85 |
