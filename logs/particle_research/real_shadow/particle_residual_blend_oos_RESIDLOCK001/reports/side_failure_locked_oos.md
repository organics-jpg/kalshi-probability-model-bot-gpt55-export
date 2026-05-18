# Side Failure Analysis

- candidate_count: 3358
- source_candidate_count: 3358
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- selected_count: 3045
- base_total_counterfactual_pnl_cents: 60332.0000
- base_avg_counterfactual_pnl_cents_per_selected: 19.8135
- forced_yes_total_counterfactual_pnl_cents: 74128.0000
- forced_no_total_counterfactual_pnl_cents: -13796.0000
- selected_yes_total_counterfactual_pnl_cents: 74128.0000
- selected_no_total_counterfactual_pnl_cents: -13796.0000
- promotion_safe: False
- note: Side failure analysis is diagnostic only. Forced-side and side-flip counterfactuals are not a trading rule unless predeclared and validated on fresh locked OOS/shadow data.

## Selected Side Summary

| side | selected | win_rate | pnl_cents | avg_pnl | avg_ev | avg_margin | opposite_pnl | selected_minus_opposite | worse_than_opposite | avg_particle | avg_market | avg_current |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| yes | 2097 | 0.6552 | 74128.0000 | 35.3495 | 7.7110 | 18.2675 | -80153.0000 | 154281.0000 | 647 | 0.372913 | 0.283443 | 0.271642 |
| no | 948 | 0.0527 | -13796.0000 | -14.5527 | 10.8660 | 24.0093 | 11617.0000 | -25413.0000 | 801 | 0.689085 | 0.807162 | 0.784212 |

## Forced Side Summary

| side | selected | filled | win_rate | pnl_cents | avg_pnl | avg_ev |
|---|---:|---:|---:|---:|---:|---:|
| yes | 2097 | 2097 | 0.6552 | 74128.0000 | 35.3495 | 7.7110 |
| no | 948 | 948 | 0.0527 | -13796.0000 | -14.5527 | 10.8660 |

## Markets

| market | result_yes | candidates | selected | selected_yes | selected_no | yes_pnl | no_pnl | forced_yes_pnl | forced_no_pnl | selected_minus_opposite |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY111115-15 | True | 720 | 699 | 564 | 135 | 37340.0000 | -2525.0000 | 37340.0000 | -2525.0000 | 71732.0000 |
| KXBTC15M-26MAY111130-30 | True | 721 | 614 | 344 | 270 | 21157.0000 | -6986.0000 | 21157.0000 | -6986.0000 | 30109.0000 |
| KXBTC15M-26MAY111145-45 | False | 807 | 773 | 723 | 50 | -12146.0000 | 2725.0000 | -12146.0000 | 2725.0000 | -16972.0000 |
| KXBTC15M-26MAY111200-00 | True | 763 | 639 | 147 | 492 | 7950.0000 | -6965.0000 | 7950.0000 | -6965.0000 | 3429.0000 |
| KXBTC15M-26MAY111215-15 | True | 347 | 320 | 319 | 1 | 19827.0000 | -45.0000 | 19827.0000 | -45.0000 | 40570.0000 |

## Absolute EV Margin Buckets

- abs_ev_margin_rank_1_of_5: selected=609, avg_abs_margin=38.0581, yes=224, no=385, pnl=-2048.0000, selected_minus_opposite=-2871.0000
- abs_ev_margin_rank_2_of_5: selected=609, avg_abs_margin=25.4713, yes=483, no=126, pnl=13246.0000, selected_minus_opposite=28088.0000
- abs_ev_margin_rank_3_of_5: selected=609, avg_abs_margin=18.4567, yes=517, no=92, pnl=19091.0000, selected_minus_opposite=39932.0000
- abs_ev_margin_rank_4_of_5: selected=609, avg_abs_margin=12.2895, yes=473, no=136, pnl=16921.0000, selected_minus_opposite=35672.0000
- abs_ev_margin_rank_5_of_5: selected=609, avg_abs_margin=6.0000, yes=400, no=209, pnl=13122.0000, selected_minus_opposite=28047.0000
