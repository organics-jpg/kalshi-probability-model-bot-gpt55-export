# Side Failure Analysis

- candidate_count: 753
- source_candidate_count: 753
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- selected_count: 676
- base_total_counterfactual_pnl_cents: -4876.0000
- base_avg_counterfactual_pnl_cents_per_selected: -7.2130
- forced_yes_total_counterfactual_pnl_cents: 4193.0000
- forced_no_total_counterfactual_pnl_cents: -9069.0000
- selected_yes_total_counterfactual_pnl_cents: 4193.0000
- selected_no_total_counterfactual_pnl_cents: -9069.0000
- promotion_safe: False
- note: Side failure analysis is diagnostic only. Forced-side and side-flip counterfactuals are not a trading rule unless predeclared and validated on fresh locked OOS/shadow data.

## Selected Side Summary

| side | selected | win_rate | pnl_cents | avg_pnl | avg_ev | avg_margin | opposite_pnl | selected_minus_opposite | worse_than_opposite | avg_particle | avg_market | avg_current |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| yes | 434 | 0.2327 | 4193.0000 | 9.6613 | 17.0524 | 36.0398 | -5050.0000 | 9243.0000 | 287 | 0.306232 | 0.127926 | 0.197933 |
| no | 242 | 0.0000 | -9069.0000 | -37.4752 | 8.7767 | 20.7541 | 8248.0000 | -17317.0000 | 242 | 0.528041 | 0.631302 | 0.571667 |

## Forced Side Summary

| side | selected | filled | win_rate | pnl_cents | avg_pnl | avg_ev |
|---|---:|---:|---:|---:|---:|---:|
| yes | 434 | 434 | 0.2327 | 4193.0000 | 9.6613 | 17.0524 |
| no | 242 | 242 | 0.0000 | -9069.0000 | -37.4752 | 8.7767 |

## Markets

| market | result_yes | candidates | selected | selected_yes | selected_no | yes_pnl | no_pnl | forced_yes_pnl | forced_no_pnl | selected_minus_opposite |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY110145-45 | False | 333 | 333 | 333 | 0 | -1487.0000 | 0.0000 | -1487.0000 | 0.0000 | -2444.0000 |
| KXBTC15M-26MAY110200-00 | True | 420 | 343 | 101 | 242 | 5680.0000 | -9069.0000 | 5680.0000 | -9069.0000 | -5630.0000 |

## Absolute EV Margin Buckets

- abs_ev_margin_rank_1_of_5: selected=135, avg_abs_margin=50.7405, yes=135, no=0, pnl=-578.0000, selected_minus_opposite=-945.0000
- abs_ev_margin_rank_2_of_5: selected=135, avg_abs_margin=45.0242, yes=126, no=9, pnl=-969.0000, selected_minus_opposite=-1695.0000
- abs_ev_margin_rank_3_of_5: selected=135, avg_abs_margin=33.4318, yes=51, no=84, pnl=-2497.0000, selected_minus_opposite=-4642.0000
- abs_ev_margin_rank_4_of_5: selected=135, avg_abs_margin=17.0998, yes=59, no=76, pnl=-413.0000, selected_minus_opposite=-420.0000
- abs_ev_margin_rank_5_of_5: selected=136, avg_abs_margin=6.7189, yes=63, no=73, pnl=-419.0000, selected_minus_opposite=-372.0000
