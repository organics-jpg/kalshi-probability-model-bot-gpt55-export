# v28 Exit Loss-Guard Mechanism Audit

Research-only. No live bot logic changes, no orders, no process control.

- Generated UTC: `2026-05-07T11:36:17.026497+00:00`

## Interpretation

- Research-only mechanism audit; no live bot changes or orders.
- Broad book-gap suppression still has observed harmful suppressions, so it remains rejected.
- Loss-guarded book-gap avoided the current dangerous false-hold rows by p_hold/gap floors, but its clean suppressions are still too few for promotion.
- book_gap_loss_guard current strict suppressions: 8 helpful / 0 harmful, delta 76.0c.
- book_gap_loss_guard_v3 current strict suppressions: 2 helpful / 0 harmful, delta 24.0c.

## Lane Summary

| lane | rows | suppressed | helpful | harmful | suppress delta | danger rows | danger suppressed | avoided harm rows | avoided harm c | avoid reasons | min p margin | min gap margin |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| `book_gap_suppression` | 55 | 24 | 19 | 4 | -165.000000 | 47 | 24 | 5 | -538.000000 | {'collapse_exit_never_suppressed': 8, 'reduce_p_hold_below_floor': 3, 'value_gap_below_floor': 12, 'value_p_hold_below_floor': 12} | -0.080968 | -0.180968 |
| `book_gap_loss_guard` | 28 | 8 | 8 | 0 | 76.000000 | 25 | 8 | 4 | -542.000000 | {'collapse_exit_never_suppressed': 3, 'reduce_p_hold_below_floor': 1, 'value_gap_below_floor': 13, 'value_p_hold_below_floor': 13} | 0.010673 | -0.048222 |
| `book_gap_loss_guard_v3` | 15 | 2 | 2 | 0 | 24.000000 | 14 | 2 | 3 | -362.000000 | {'collapse_exit_never_suppressed': 1, 'reduce_p_hold_below_floor': 1, 'value_extreme_p_hold_below_floor': 10, 'value_gap_below_floor': 10, 'value_p_hold_below_floor': 8} | 0.010673 | -0.029327 |

## Dangerous Unsuppressed Rows

### book_gap_suppression
- `KXBTC15M-26MAY070015-15` `no` hold-current `-138.000000c`, exit `mushroom_v28_exit_value_over_hold` `69`, p_hold `0.596562`, gap `-0.09343799999999991`, fair_drawdown `10.343815`, avoided by `value_p_hold_below_floor, value_gap_below_floor`
- `KXBTC15M-26MAY061300-00` `yes` hold-current `-130.000000c`, exit `mushroom_v28_probability_collapse_full` `65`, p_hold `0.66643`, gap `0.016429999999999945`, fair_drawdown `13.356971`, avoided by `collapse_exit_never_suppressed`
- `KXBTC15M-26MAY062115-15` `no` hold-current `-104.000000c`, exit `mushroom_v28_exit_value_over_hold` `52`, p_hold `0.455777`, gap `-0.06422300000000003`, fair_drawdown `14.422271`, avoided by `value_p_hold_below_floor, value_gap_below_floor`
- `KXBTC15M-26MAY060745-45` `yes` hold-current `-86.000000c`, exit `mushroom_v28_probability_collapse_full` `43`, p_hold `0.563569`, gap `0.133569`, fair_drawdown `21.643115`, avoided by `collapse_exit_never_suppressed`
- `KXBTC15M-26MAY060900-00` `yes` hold-current `-80.000000c`, exit `mushroom_v28_probability_collapse_full` `40`, p_hold `0.39732`, gap `-0.0026800000000000157`, fair_drawdown `41.268037`, avoided by `collapse_exit_never_suppressed`
- `KXBTC15M-26MAY062300-00` `yes` hold-current `10.000000c`, exit `mushroom_v28_exit_value_over_hold` `95`, p_hold `0.746374`, gap `-0.20362599999999997`, fair_drawdown `10.362646`, avoided by `value_p_hold_below_floor, value_gap_below_floor`
- `KXBTC15M-26MAY062245-45` `yes` hold-current `20.000000c`, exit `mushroom_v28_exit_value_over_hold` `90`, p_hold `0.643812`, gap `-0.25618799999999997`, fair_drawdown `15.618779`, avoided by `value_p_hold_below_floor, value_gap_below_floor`
- `KXBTC15M-26MAY060700-00` `yes` hold-current `22.000000c`, exit `mushroom_v28_exit_value_over_hold` `89`, p_hold `0.743339`, gap `-0.14666100000000004`, fair_drawdown `8.666129`, avoided by `value_p_hold_below_floor, value_gap_below_floor`

### book_gap_loss_guard
- `KXBTC15M-26MAY062015-15` `yes` hold-current `-180.000000c`, exit `mushroom_v28_exit_value_over_hold` `90`, p_hold `0.812359`, gap `-0.08764099999999997`, fair_drawdown `4.764109`, avoided by `value_p_hold_below_floor, value_gap_below_floor`
- `KXBTC15M-26MAY070015-15` `no` hold-current `-138.000000c`, exit `mushroom_v28_exit_value_over_hold` `69`, p_hold `0.596562`, gap `-0.09343799999999991`, fair_drawdown `10.343815`, avoided by `value_p_hold_below_floor, value_gap_below_floor`
- `KXBTC15M-26MAY062130-30` `no` hold-current `-120.000000c`, exit `mushroom_v28_probability_reduce` `60`, p_hold `0.768407`, gap `0.16840699999999997`, fair_drawdown `6.159273`, avoided by `reduce_p_hold_below_floor`
- `KXBTC15M-26MAY062115-15` `no` hold-current `-104.000000c`, exit `mushroom_v28_exit_value_over_hold` `52`, p_hold `0.455777`, gap `-0.06422300000000003`, fair_drawdown `14.422271`, avoided by `value_p_hold_below_floor, value_gap_below_floor`
- `KXBTC15M-26MAY062300-00` `yes` hold-current `10.000000c`, exit `mushroom_v28_exit_value_over_hold` `95`, p_hold `0.746374`, gap `-0.20362599999999997`, fair_drawdown `10.362646`, avoided by `value_p_hold_below_floor, value_gap_below_floor`
- `KXBTC15M-26MAY062245-45` `yes` hold-current `20.000000c`, exit `mushroom_v28_exit_value_over_hold` `90`, p_hold `0.643812`, gap `-0.25618799999999997`, fair_drawdown `15.618779`, avoided by `value_p_hold_below_floor, value_gap_below_floor`
- `KXBTC15M-26MAY062315-15` `no` hold-current `26.000000c`, exit `mushroom_v28_exit_value_over_hold` `87`, p_hold `0.811182`, gap `-0.05881800000000004`, fair_drawdown `2.881757`, avoided by `value_p_hold_below_floor, value_gap_below_floor`
- `KXBTC15M-26MAY062030-30` `no` hold-current `34.000000c`, exit `mushroom_v28_exit_value_over_hold` `83`, p_hold `0.661475`, gap `-0.16852499999999992`, fair_drawdown `0.852486`, avoided by `value_p_hold_below_floor, value_gap_below_floor`

### book_gap_loss_guard_v3
- `KXBTC15M-26MAY070015-15` `no` hold-current `-138.000000c`, exit `mushroom_v28_exit_value_over_hold` `69`, p_hold `0.596562`, gap `-0.09343799999999991`, fair_drawdown `10.343815`, avoided by `value_p_hold_below_floor, value_gap_below_floor, value_extreme_p_hold_below_floor`
- `KXBTC15M-26MAY062130-30` `no` hold-current `-120.000000c`, exit `mushroom_v28_probability_reduce` `60`, p_hold `0.768407`, gap `0.16840699999999997`, fair_drawdown `6.159273`, avoided by `reduce_p_hold_below_floor`
- `KXBTC15M-26MAY062115-15` `no` hold-current `-104.000000c`, exit `mushroom_v28_exit_value_over_hold` `52`, p_hold `0.455777`, gap `-0.06422300000000003`, fair_drawdown `14.422271`, avoided by `value_p_hold_below_floor, value_gap_below_floor, value_extreme_p_hold_below_floor`
- `KXBTC15M-26MAY070030-30` `yes` hold-current `6.000000c`, exit `mushroom_v28_exit_value_over_hold` `97`, p_hold `0.921778`, gap `-0.04822199999999999`, fair_drawdown `-10.177771`, avoided by `value_gap_below_floor, value_extreme_p_hold_below_floor`
- `KXBTC15M-26MAY062300-00` `yes` hold-current `10.000000c`, exit `mushroom_v28_exit_value_over_hold` `95`, p_hold `0.746374`, gap `-0.20362599999999997`, fair_drawdown `10.362646`, avoided by `value_p_hold_below_floor, value_gap_below_floor, value_extreme_p_hold_below_floor`
- `KXBTC15M-26MAY070545-45` `no` hold-current `18.000000c`, exit `mushroom_v28_exit_value_over_hold` `91`, p_hold `0.892567`, gap `-0.017433000000000032`, fair_drawdown `-7.256748`, avoided by `value_gap_below_floor, value_extreme_p_hold_below_floor`
- `KXBTC15M-26MAY062245-45` `yes` hold-current `20.000000c`, exit `mushroom_v28_exit_value_over_hold` `90`, p_hold `0.643812`, gap `-0.25618799999999997`, fair_drawdown `15.618779`, avoided by `value_p_hold_below_floor, value_gap_below_floor, value_extreme_p_hold_below_floor`
- `KXBTC15M-26MAY062315-15` `no` hold-current `26.000000c`, exit `mushroom_v28_exit_value_over_hold` `87`, p_hold `0.811182`, gap `-0.05881800000000004`, fair_drawdown `2.881757`, avoided by `value_p_hold_below_floor, value_gap_below_floor, value_extreme_p_hold_below_floor`


## Helpful Suppressed Rows

### book_gap_suppression
- `KXBTC15M-26MAY060930-30` `no` delta `62.000000c`, exit `mushroom_v28_probability_reduce` `69`, p_hold `0.787606`, gap `0.10760599999999998`, p_margin `-0.002394`, gap_margin `0.107606`
- `KXBTC15M-26MAY060915-15` `no` delta `60.000000c`, exit `mushroom_v28_probability_reduce` `70`, p_hold `0.793762`, gap `0.09376200000000001`, p_margin `0.003762`, gap_margin `0.093762`
- `KXBTC15M-26MAY061015-15` `no` delta `60.000000c`, exit `mushroom_v28_probability_reduce` `70`, p_hold `0.799979`, gap `0.09997900000000004`, p_margin `0.009979`, gap_margin `0.099979`
- `KXBTC15M-26MAY060930-30` `no` delta `57.000000c`, exit `mushroom_v28_probability_reduce` `72`, p_hold `0.79918`, gap `0.08918000000000004`, p_margin `0.009180`, gap_margin `0.089180`
- `KXBTC15M-26MAY060630-30` `yes` delta `54.000000c`, exit `mushroom_v28_probability_reduce` `73`, p_hold `0.777774`, gap `0.04777399999999998`, p_margin `-0.012226`, gap_margin `0.047774`
- `KXBTC15M-26MAY060600-00` `no` delta `38.000000c`, exit `mushroom_v28_exit_value_over_hold` `81`, p_hold `0.804105`, gap `-0.015894999999999992`, p_margin `-0.045895`, gap_margin `-0.015895`
- `KXBTC15M-26MAY062315-15` `no` delta `26.000000c`, exit `mushroom_v28_exit_value_over_hold` `87`, p_hold `0.811182`, gap `-0.05881800000000004`, p_margin `-0.038818`, gap_margin `-0.058818`
- `KXBTC15M-26MAY070545-45` `no` delta `18.000000c`, exit `mushroom_v28_exit_value_over_hold` `91`, p_hold `0.892567`, gap `-0.017433000000000032`, p_margin `0.042567`, gap_margin `-0.017433`

### book_gap_loss_guard
- `KXBTC15M-26MAY062215-15` `no` delta `22.000000c`, exit `mushroom_v28_exit_value_over_hold` `89`, p_hold `0.860673`, gap `-0.029326999999999992`, p_margin `0.010673`, gap_margin `-0.029327`
- `KXBTC15M-26MAY070545-45` `no` delta `18.000000c`, exit `mushroom_v28_exit_value_over_hold` `91`, p_hold `0.892567`, gap `-0.017433000000000032`, p_margin `0.042567`, gap_margin `-0.017433`
- `KXBTC15M-26MAY062045-45` `no` delta `16.000000c`, exit `mushroom_v28_exit_value_over_hold` `92`, p_hold `0.891386`, gap `-0.02861400000000003`, p_margin `0.041386`, gap_margin `-0.028614`
- `KXBTC15M-26MAY061815-15` `no` delta `8.000000c`, exit `mushroom_v28_exit_value_over_hold` `96`, p_hold `0.950684`, gap `-0.009315999999999991`, p_margin `0.100684`, gap_margin `-0.009316`
- `KXBTC15M-26MAY070030-30` `yes` delta `6.000000c`, exit `mushroom_v28_exit_value_over_hold` `97`, p_hold `0.921778`, gap `-0.04822199999999999`, p_margin `0.071778`, gap_margin `-0.048222`
- `KXBTC15M-26MAY061830-30` `no` delta `2.000000c`, exit `mushroom_v28_exit_value_over_hold` `99`, p_hold `0.976718`, gap `-0.013282000000000016`, p_margin `0.126718`, gap_margin `-0.013282`
- `KXBTC15M-26MAY061915-15` `no` delta `2.000000c`, exit `mushroom_v28_exit_value_over_hold` `99`, p_hold `0.981987`, gap `-0.008012999999999937`, p_margin `0.131987`, gap_margin `-0.008013`
- `KXBTC15M-26MAY062115-15` `yes` delta `2.000000c`, exit `mushroom_v28_exit_value_over_hold` `99`, p_hold `0.982461`, gap `-0.007538999999999962`, p_margin `0.132461`, gap_margin `-0.007539`

### book_gap_loss_guard_v3
- `KXBTC15M-26MAY062215-15` `no` delta `22.000000c`, exit `mushroom_v28_exit_value_over_hold` `89`, p_hold `0.860673`, gap `-0.029326999999999992`, p_margin `0.010673`, gap_margin `-0.029327`
- `KXBTC15M-26MAY062115-15` `yes` delta `2.000000c`, exit `mushroom_v28_exit_value_over_hold` `99`, p_hold `0.982461`, gap `-0.007538999999999962`, p_margin `0.132461`, gap_margin `-0.007539`

