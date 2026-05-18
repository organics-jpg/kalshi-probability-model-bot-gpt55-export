# Side Failure Analysis

- candidate_count: 4512
- source_candidate_count: 4512
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- selected_count: 4379
- base_total_counterfactual_pnl_cents: -2384.0000
- base_avg_counterfactual_pnl_cents_per_selected: -0.5444
- forced_yes_total_counterfactual_pnl_cents: -49192.0000
- forced_no_total_counterfactual_pnl_cents: 46808.0000
- selected_yes_total_counterfactual_pnl_cents: -49192.0000
- selected_no_total_counterfactual_pnl_cents: 46808.0000
- promotion_safe: False
- note: Side failure analysis is diagnostic only. Forced-side and side-flip counterfactuals are not a trading rule unless predeclared and validated on fresh locked OOS/shadow data.

## Selected Side Summary

| side | selected | win_rate | pnl_cents | avg_pnl | avg_ev | avg_margin | opposite_pnl | selected_minus_opposite | worse_than_opposite | avg_particle | avg_market | avg_current |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| yes | 2708 | 0.0000 | -49192.0000 | -18.1654 | 16.4504 | 35.2613 | 42714.0000 | -91906.0000 | 2543 | 0.351602 | 0.177044 | 0.162866 |
| no | 1671 | 0.5422 | 46808.0000 | 28.0120 | 15.7063 | 34.1397 | -51345.0000 | 98153.0000 | 744 | 0.584149 | 0.753779 | 0.749015 |

## Forced Side Summary

| side | selected | filled | win_rate | pnl_cents | avg_pnl | avg_ev |
|---|---:|---:|---:|---:|---:|---:|
| yes | 2708 | 2708 | 0.0000 | -49192.0000 | -18.1654 | 16.4504 |
| no | 1671 | 1671 | 0.5422 | 46808.0000 | 28.0120 | 15.7063 |

## Markets

| market | result_yes | candidates | selected | selected_yes | selected_no | yes_pnl | no_pnl | forced_yes_pnl | forced_no_pnl | selected_minus_opposite |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY112000-00 | False | 402 | 402 | 402 | 0 | -5078.0000 | 0.0000 | -5078.0000 | 0.0000 | -9284.0000 |
| KXBTC15M-26MAY112015-15 | False | 712 | 692 | 596 | 96 | -10048.0000 | 5257.0000 | -10048.0000 | 5257.0000 | -7824.0000 |
| KXBTC15M-26MAY112030-30 | False | 767 | 738 | 523 | 215 | -7543.0000 | 12248.0000 | -7543.0000 | 12248.0000 | 11219.0000 |
| KXBTC15M-26MAY112045-45 | False | 790 | 725 | 343 | 382 | -9894.0000 | 23946.0000 | -9894.0000 | 23946.0000 | 30354.0000 |
| KXBTC15M-26MAY112100-00 | True | 765 | 765 | 0 | 765 | 0.0000 | -9784.0000 | 0.0000 | -9784.0000 | -17921.0000 |
| KXBTC15M-26MAY112115-15 | False | 705 | 692 | 479 | 213 | -5287.0000 | 15141.0000 | -5287.0000 | 15141.0000 | 21327.0000 |
| KXBTC15M-26MAY112130-30 | False | 371 | 365 | 365 | 0 | -11342.0000 | 0.0000 | -11342.0000 | 0.0000 | -21624.0000 |

## Absolute EV Margin Buckets

- abs_ev_margin_rank_1_of_5: selected=875, avg_abs_margin=57.0503, yes=482, no=393, pnl=-5471.0000, selected_minus_opposite=-9492.0000
- abs_ev_margin_rank_2_of_5: selected=876, avg_abs_margin=45.6120, yes=652, no=224, pnl=-3919.0000, selected_minus_opposite=-6016.0000
- abs_ev_margin_rank_3_of_5: selected=876, avg_abs_margin=36.2902, yes=557, no=319, pnl=2950.0000, selected_minus_opposite=8158.0000
- abs_ev_margin_rank_4_of_5: selected=876, avg_abs_margin=24.2843, yes=512, no=364, pnl=4133.0000, selected_minus_opposite=10907.0000
- abs_ev_margin_rank_5_of_5: selected=876, avg_abs_margin=10.9553, yes=505, no=371, pnl=-77.0000, selected_minus_opposite=2690.0000
