# v28 Side-Flip Path Diagnostic

- Early policy: `v28_raw_p50_edge0`
- Late policies: `first_side_raw_later_book_p60_edge0, rmt_repetition_forget_p60_edge0, book_ask_prior_p60_edge0`

## Summary

| late policy | status | count | settled | early wins | late wins | early net c | late net c | late - early c |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| first_side_raw_later_book_p60_edge0 | same_side | 125 | 125 | 79 | 79 | 39.000000 | -1257.000000 | -1296.000000 |
| first_side_raw_later_book_p60_edge0 | side_flip | 44 | 44 | 22 | 22 | 188.000000 | -1639.000000 | -1827.000000 |
| first_side_raw_later_book_p60_edge0 | late_policy_missed | 3 | 3 | 0 | 0 | -294.000000 | 0.000000 | 294.000000 |
| rmt_repetition_forget_p60_edge0 | same_side | 120 | 120 | 78 | 78 | 314.000000 | -1089.000000 | -1403.000000 |
| rmt_repetition_forget_p60_edge0 | side_flip | 49 | 49 | 23 | 26 | -87.000000 | -1549.000000 | -1462.000000 |
| rmt_repetition_forget_p60_edge0 | late_policy_missed | 3 | 3 | 0 | 0 | -294.000000 | 0.000000 | 294.000000 |
| book_ask_prior_p60_edge0 | same_side | 118 | 118 | 77 | 77 | 410.000000 | -944.000000 | -1354.000000 |
| book_ask_prior_p60_edge0 | side_flip | 52 | 52 | 24 | 28 | -287.000000 | -1476.000000 | -1189.000000 |
| book_ask_prior_p60_edge0 | late_policy_missed | 2 | 2 | 0 | 0 | -194.000000 | 0.000000 | 194.000000 |

## Recent Rows

| market | late policy | status | early side | late side | early edge | late edge | early won | late won | early net | late net |
|---|---|---|---|---|---:|---:|---|---|---:|---:|
| KXBTC15M-26MAY071115-15 | first_side_raw_later_book_p60_edge0 | same_side | no | no | 0.015838 | 0.000000 | False | False | -128.000000 | -128.000000 |
| KXBTC15M-26MAY071115-15 | rmt_repetition_forget_p60_edge0 | same_side | no | no | 0.015838 | 0.000000 | False | False | -128.000000 | -128.000000 |
| KXBTC15M-26MAY071115-15 | book_ask_prior_p60_edge0 | same_side | no | no | 0.015838 | 0.000000 | False | False | -128.000000 | -128.000000 |
| KXBTC15M-26MAY071130-30 | first_side_raw_later_book_p60_edge0 | side_flip | no | yes | 0.002087 | 0.000000 | True | False | 80.000000 | -124.000000 |
| KXBTC15M-26MAY071130-30 | rmt_repetition_forget_p60_edge0 | side_flip | no | yes | 0.002087 | 0.000000 | True | False | 80.000000 | -124.000000 |
| KXBTC15M-26MAY071130-30 | book_ask_prior_p60_edge0 | side_flip | no | yes | 0.002087 | 0.000000 | True | False | 80.000000 | -124.000000 |
| KXBTC15M-26MAY071145-45 | first_side_raw_later_book_p60_edge0 | same_side | yes | yes | 0.035637 | 0.035637 | True | True | 74.000000 | 74.000000 |
| KXBTC15M-26MAY071145-45 | rmt_repetition_forget_p60_edge0 | same_side | yes | yes | 0.035637 | 0.017819 | True | True | 74.000000 | 74.000000 |
| KXBTC15M-26MAY071145-45 | book_ask_prior_p60_edge0 | same_side | yes | yes | 0.035637 | 0.000000 | True | True | 74.000000 | 74.000000 |
| KXBTC15M-26MAY071200-00 | first_side_raw_later_book_p60_edge0 | same_side | yes | yes | 0.006055 | 0.000000 | False | False | -124.000000 | -130.000000 |
| KXBTC15M-26MAY071200-00 | rmt_repetition_forget_p60_edge0 | same_side | yes | yes | 0.006055 | 0.000000 | False | False | -124.000000 | -130.000000 |
| KXBTC15M-26MAY071200-00 | book_ask_prior_p60_edge0 | same_side | yes | yes | 0.006055 | 0.000000 | False | False | -124.000000 | -128.000000 |
| KXBTC15M-26MAY071215-15 | first_side_raw_later_book_p60_edge0 | same_side | yes | yes | 0.039397 | 0.000000 | False | False | -98.000000 | -124.000000 |
| KXBTC15M-26MAY071215-15 | rmt_repetition_forget_p60_edge0 | same_side | yes | yes | 0.039397 | 0.000000 | False | False | -98.000000 | -124.000000 |
| KXBTC15M-26MAY071215-15 | book_ask_prior_p60_edge0 | same_side | yes | yes | 0.039397 | 0.000000 | False | False | -98.000000 | -124.000000 |
| KXBTC15M-26MAY071230-30 | first_side_raw_later_book_p60_edge0 | same_side | no | no | 0.029882 | 0.000000 | False | False | -143.000000 | -143.000000 |
| KXBTC15M-26MAY071230-30 | rmt_repetition_forget_p60_edge0 | same_side | no | no | 0.029882 | 0.000000 | False | False | -143.000000 | -143.000000 |
| KXBTC15M-26MAY071230-30 | book_ask_prior_p60_edge0 | same_side | no | no | 0.029882 | 0.000000 | False | False | -143.000000 | -128.000000 |
| KXBTC15M-26MAY071245-45 | first_side_raw_later_book_p60_edge0 | same_side | yes | yes | 0.009979 | 0.000000 | False | False | -114.000000 | -134.000000 |
| KXBTC15M-26MAY071245-45 | rmt_repetition_forget_p60_edge0 | same_side | yes | yes | 0.009979 | 0.000000 | False | False | -114.000000 | -134.000000 |
| KXBTC15M-26MAY071245-45 | book_ask_prior_p60_edge0 | same_side | yes | yes | 0.009979 | 0.000000 | False | False | -114.000000 | -134.000000 |
| KXBTC15M-26MAY071300-00 | first_side_raw_later_book_p60_edge0 | same_side | yes | yes | 0.046040 | 0.046040 | False | False | -122.000000 | -122.000000 |
| KXBTC15M-26MAY071300-00 | rmt_repetition_forget_p60_edge0 | same_side | yes | yes | 0.046040 | 0.023020 | False | False | -122.000000 | -122.000000 |
| KXBTC15M-26MAY071300-00 | book_ask_prior_p60_edge0 | same_side | yes | yes | 0.046040 | 0.000000 | False | False | -122.000000 | -140.000000 |
| KXBTC15M-26MAY071315-15 | first_side_raw_later_book_p60_edge0 | same_side | yes | yes | 0.023442 | 0.000000 | True | True | 94.000000 | 57.000000 |
| KXBTC15M-26MAY071315-15 | rmt_repetition_forget_p60_edge0 | same_side | yes | yes | 0.023442 | 0.000000 | True | True | 94.000000 | 57.000000 |
| KXBTC15M-26MAY071315-15 | book_ask_prior_p60_edge0 | same_side | yes | yes | 0.023442 | 0.000000 | True | True | 94.000000 | 57.000000 |
| KXBTC15M-26MAY071330-30 | first_side_raw_later_book_p60_edge0 | side_flip | yes | no | 0.024206 | 0.000000 | False | True | -108.000000 | 66.000000 |
| KXBTC15M-26MAY071330-30 | rmt_repetition_forget_p60_edge0 | side_flip | yes | no | 0.024206 | 0.000000 | False | True | -108.000000 | 66.000000 |
| KXBTC15M-26MAY071330-30 | book_ask_prior_p60_edge0 | side_flip | yes | no | 0.024206 | 0.000000 | False | True | -108.000000 | 76.000000 |
