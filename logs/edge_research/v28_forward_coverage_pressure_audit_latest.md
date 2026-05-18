# v28 Forward Coverage Pressure Audit

Tracks missed forward markets so coverage pressure does not turn into forced bad trades.

## Summary

| source | policy | misses | resolved | pending | near-miss net c | saved losses | missed profits | profitable negative-edge misses |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| v28_frozen_forward_candidates | book_ask_prior_p60_edge0 | 2 | 2 | 0 | 8.000000 | 0 | 2 | 0 |
| v28_frozen_forward_candidates | first_side_raw_later_book_p60_edge0 | 4 | 4 | 0 | -131.000000 | 1 | 3 | 0 |
| v28_frozen_forward_candidates | rmt_repetition_forget_p60_edge0 | 4 | 4 | 0 | -131.000000 | 1 | 3 | 0 |
| v28_frozen_forward_candidates | v28_raw_p50_edge0 | 3 | 3 | 0 | -124.000000 | 1 | 0 | 2 |

## Missed Forward Markets

| source | policy | market | status | result | class | miss reason | side | p | ask | edge | near-miss net c |
|---|---|---|---|---|---|---|---|---:|---:|---:|---:|
| v28_frozen_forward_candidates | first_side_raw_later_book_p60_edge0 | KXBTC15M-26MAY060400-00 | finalized | no | coverage_mistake_missed_profit | unknown_selection_miss | no | 0.990000 | 0.990000 | 0.000000 | 1.000000 |
| v28_frozen_forward_candidates | first_side_raw_later_book_p60_edge0 | KXBTC15M-26MAY060430-30 | finalized | yes | healthy_abstention_saved_loss | edge_below_threshold | no | 0.621335 | 0.680000 | -0.058665 | -140.000000 |
| v28_frozen_forward_candidates | first_side_raw_later_book_p60_edge0 | KXBTC15M-26MAY062330-30 | finalized | no | coverage_mistake_missed_profit | unknown_selection_miss | no | 0.960000 | 0.960000 | 0.000000 | 7.000000 |
| v28_frozen_forward_candidates | first_side_raw_later_book_p60_edge0 | KXBTC15M-26MAY070800-00 | finalized | no | coverage_mistake_missed_profit | unknown_selection_miss | no | 0.990000 | 0.990000 | 0.000000 | 1.000000 |
| v28_frozen_forward_candidates | rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY060400-00 | finalized | no | coverage_mistake_missed_profit | unknown_selection_miss | no | 0.990000 | 0.990000 | 0.000000 | 1.000000 |
| v28_frozen_forward_candidates | rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY060430-30 | finalized | yes | healthy_abstention_saved_loss | edge_below_threshold | no | 0.650667 | 0.680000 | -0.029333 | -140.000000 |
| v28_frozen_forward_candidates | rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY062330-30 | finalized | no | coverage_mistake_missed_profit | unknown_selection_miss | no | 0.960000 | 0.960000 | 0.000000 | 7.000000 |
| v28_frozen_forward_candidates | rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070800-00 | finalized | no | coverage_mistake_missed_profit | unknown_selection_miss | no | 0.990000 | 0.990000 | 0.000000 | 1.000000 |
| v28_frozen_forward_candidates | book_ask_prior_p60_edge0 | KXBTC15M-26MAY062330-30 | finalized | no | coverage_mistake_missed_profit | unknown_selection_miss | no | 0.960000 | 0.960000 | 0.000000 | 7.000000 |
| v28_frozen_forward_candidates | book_ask_prior_p60_edge0 | KXBTC15M-26MAY070800-00 | finalized | no | coverage_mistake_missed_profit | unknown_selection_miss | no | 0.990000 | 0.990000 | 0.000000 | 1.000000 |
| v28_frozen_forward_candidates | v28_raw_p50_edge0 | KXBTC15M-26MAY051930-30 | finalized | no | profitable_negative_edge_miss | edge_below_threshold | no | 0.901032 | 0.950000 | -0.048968 | 9.000000 |
| v28_frozen_forward_candidates | v28_raw_p50_edge0 | KXBTC15M-26MAY060430-30 | finalized | yes | healthy_abstention_saved_loss | edge_below_threshold | no | 0.621335 | 0.680000 | -0.058665 | -140.000000 |
| v28_frozen_forward_candidates | v28_raw_p50_edge0 | KXBTC15M-26MAY061845-45 | finalized | yes | profitable_negative_edge_miss | edge_below_threshold | yes | 0.944524 | 0.960000 | -0.015476 | 7.000000 |
