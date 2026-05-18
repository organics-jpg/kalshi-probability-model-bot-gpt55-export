# Side Failure Analysis

- candidate_count: 3398
- source_candidate_count: 3398
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- selected_count: 3111
- base_total_counterfactual_pnl_cents: 14916.0000
- base_avg_counterfactual_pnl_cents_per_selected: 4.7946
- forced_yes_total_counterfactual_pnl_cents: -13150.0000
- forced_no_total_counterfactual_pnl_cents: 28066.0000
- selected_yes_total_counterfactual_pnl_cents: -13150.0000
- selected_no_total_counterfactual_pnl_cents: 28066.0000
- promotion_safe: False
- note: Side failure analysis is diagnostic only. Forced-side and side-flip counterfactuals are not a trading rule unless predeclared and validated on fresh locked OOS/shadow data.

## Selected Side Summary

| side | selected | win_rate | pnl_cents | avg_pnl | avg_ev | avg_margin | opposite_pnl | selected_minus_opposite | worse_than_opposite | avg_particle | avg_market | avg_current |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| yes | 1982 | 0.1478 | -13150.0000 | -6.6347 | 13.4373 | 29.3318 | 8280.0000 | -21430.0000 | 1581 | 0.351489 | 0.206698 | 0.227055 |
| no | 1129 | 0.5899 | 28066.0000 | 24.8592 | 12.2517 | 27.4033 | -31340.0000 | 59406.0000 | 413 | 0.539375 | 0.675868 | 0.596033 |

## Forced Side Summary

| side | selected | filled | win_rate | pnl_cents | avg_pnl | avg_ev |
|---|---:|---:|---:|---:|---:|---:|
| yes | 1982 | 1982 | 0.1478 | -13150.0000 | -6.6347 | 13.4373 |
| no | 1129 | 1129 | 0.5899 | 28066.0000 | 24.8592 | 12.2517 |

## Markets

| market | result_yes | candidates | selected | selected_yes | selected_no | yes_pnl | no_pnl | forced_yes_pnl | forced_no_pnl | selected_minus_opposite |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY110245-45 | False | 659 | 598 | 559 | 39 | -11566.0000 | 1778.0000 | -11566.0000 | 1778.0000 | -17993.0000 |
| KXBTC15M-26MAY110300-00 | True | 814 | 756 | 293 | 463 | 18318.0000 | -11122.0000 | 18318.0000 | -11122.0000 | 16483.0000 |
| KXBTC15M-26MAY110315-15 | False | 756 | 755 | 755 | 0 | -8475.0000 | 0.0000 | -8475.0000 | 0.0000 | -15518.0000 |
| KXBTC15M-26MAY110330-30 | False | 803 | 723 | 274 | 449 | -7432.0000 | 27860.0000 | -7432.0000 | 27860.0000 | 43026.0000 |
| KXBTC15M-26MAY110345-45 | False | 366 | 279 | 101 | 178 | -3995.0000 | 9550.0000 | -3995.0000 | 9550.0000 | 11978.0000 |

## Absolute EV Margin Buckets

- abs_ev_margin_rank_1_of_5: selected=622, avg_abs_margin=52.5471, yes=377, no=245, pnl=-219.0000, selected_minus_opposite=714.0000
- abs_ev_margin_rank_2_of_5: selected=622, avg_abs_margin=37.8736, yes=460, no=162, pnl=3145.0000, selected_minus_opposite=7704.0000
- abs_ev_margin_rank_3_of_5: selected=622, avg_abs_margin=27.9192, yes=453, no=169, pnl=1960.0000, selected_minus_opposite=5696.0000
- abs_ev_margin_rank_4_of_5: selected=622, avg_abs_margin=17.3956, yes=401, no=221, pnl=3983.0000, selected_minus_opposite=9909.0000
- abs_ev_margin_rank_5_of_5: selected=623, avg_abs_margin=7.4583, yes=291, no=332, pnl=6047.0000, selected_minus_opposite=13953.0000
