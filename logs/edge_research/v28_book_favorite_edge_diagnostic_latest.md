# v28 Book-Favorite Edge Diagnostic

Checks whether broad candidates have realized edge over executable ask after estimated entry fees.

## Policy Summary

| policy | group | count | wins/losses | win rate | avg ask | realized edge vs ask | net c | avg net c |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| v28_raw_p50_edge0 | all | 172 | 101/71 | 0.587209 | 0.563314 | 0.023895 | -81.000000 | -0.470930 |
| v28_raw_p50_edge0 | mode_raw_exact | 172 | 101/71 | 0.587209 | 0.563314 | 0.023895 | -81.000000 | -0.470930 |
| v28_raw_p50_edge0 | mode_book_exact | 0 | None/None | None | None | None | 0.000000 | None |
| v28_raw_p50_edge0 | mode_blend | 0 | None/None | None | None | None | 0.000000 | None |
| first_side_raw_later_book_p58_edge0 | all | 171 | 105/66 | 0.614035 | 0.651930 | -0.037895 | -1927.000000 | -11.269006 |
| first_side_raw_later_book_p58_edge0 | mode_raw_exact | 51 | 32/19 | 0.627451 | 0.611569 | 0.015882 | -136.000000 | -2.666667 |
| first_side_raw_later_book_p58_edge0 | mode_book_exact | 120 | 73/47 | 0.608333 | 0.669083 | -0.060750 | -1791.000000 | -14.925000 |
| first_side_raw_later_book_p58_edge0 | mode_blend | 0 | None/None | None | None | None | 0.000000 | None |
| first_side_raw_later_book_p60_edge0 | all | 171 | 103/68 | 0.602339 | 0.668012 | -0.065673 | -2831.000000 | -16.555556 |
| first_side_raw_later_book_p60_edge0 | mode_raw_exact | 41 | 24/17 | 0.585366 | 0.635122 | -0.049756 | -626.000000 | -15.268293 |
| first_side_raw_later_book_p60_edge0 | mode_book_exact | 130 | 79/51 | 0.607692 | 0.678385 | -0.070692 | -2205.000000 | -16.961538 |
| first_side_raw_later_book_p60_edge0 | mode_blend | 0 | None/None | None | None | None | 0.000000 | None |
| rmt_repetition_forget_p58_edge0 | all | 171 | 103/68 | 0.602339 | 0.667953 | -0.065614 | -2872.000000 | -16.795322 |
| rmt_repetition_forget_p58_edge0 | mode_raw_exact | 0 | None/None | None | None | None | 0.000000 | None |
| rmt_repetition_forget_p58_edge0 | mode_book_exact | 135 | 79/56 | 0.585185 | 0.668296 | -0.083111 | -2632.000000 | -19.496296 |
| rmt_repetition_forget_p58_edge0 | mode_blend | 36 | 24/12 | 0.666667 | 0.666667 | 0.000000 | -240.000000 | -6.666667 |
| rmt_repetition_forget_p60_edge0 | all | 171 | 106/65 | 0.619883 | 0.678070 | -0.058187 | -2573.000000 | -15.046784 |
| rmt_repetition_forget_p60_edge0 | mode_raw_exact | 0 | None/None | None | None | None | 0.000000 | None |
| rmt_repetition_forget_p60_edge0 | mode_book_exact | 140 | 85/55 | 0.607143 | 0.677571 | -0.070429 | -2376.000000 | -16.971429 |
| rmt_repetition_forget_p60_edge0 | mode_blend | 31 | 21/10 | 0.677419 | 0.680323 | -0.002903 | -197.000000 | -6.354839 |
| book_ask_prior_p60_edge0 | all | 173 | 107/66 | 0.618497 | 0.671214 | -0.052717 | -2489.000000 | -14.387283 |
| book_ask_prior_p60_edge0 | mode_raw_exact | 0 | None/None | None | None | None | 0.000000 | None |
| book_ask_prior_p60_edge0 | mode_book_exact | 173 | 107/66 | 0.618497 | 0.671214 | -0.052717 | -2489.000000 | -14.387283 |
| book_ask_prior_p60_edge0 | mode_blend | 0 | None/None | None | None | None | 0.000000 | None |

## Ask Buckets

| policy | bucket | count | wins/losses | win rate | avg ask | realized edge vs ask | net c |
|---|---|---:|---:|---:|---:|---:|---:|
| v28_raw_p50_edge0 | ask_lt_50 | 49 | 22/27 | 0.448980 | 0.420816 | 0.028163 | 88.000000 |
| v28_raw_p50_edge0 | ask_50_59 | 63 | 34/29 | 0.539683 | 0.538413 | 0.001270 | -277.000000 |
| v28_raw_p50_edge0 | ask_60_69 | 30 | 19/11 | 0.633333 | 0.633667 | -0.000333 | -150.000000 |
| v28_raw_p50_edge0 | ask_70_79 | 18 | 14/4 | 0.777778 | 0.744444 | 0.033333 | 25.000000 |
| v28_raw_p50_edge0 | ask_80_plus | 12 | 12/0 | 1.000000 | 0.828333 | 0.171667 | 233.000000 |
| first_side_raw_later_book_p58_edge0 | ask_lt_50 | 6 | 3/3 | 0.500000 | 0.405000 | 0.095000 | 92.000000 |
| first_side_raw_later_book_p58_edge0 | ask_50_59 | 39 | 18/21 | 0.461538 | 0.568462 | -0.106923 | -1031.000000 |
| first_side_raw_later_book_p58_edge0 | ask_60_69 | 74 | 42/32 | 0.567568 | 0.635405 | -0.067838 | -1199.000000 |
| first_side_raw_later_book_p58_edge0 | ask_70_79 | 35 | 26/9 | 0.742857 | 0.734286 | 0.008571 | -45.000000 |
| first_side_raw_later_book_p58_edge0 | ask_80_plus | 17 | 16/1 | 0.941176 | 0.832941 | 0.108235 | 256.000000 |
| first_side_raw_later_book_p60_edge0 | ask_lt_50 | 4 | 1/3 | 0.250000 | 0.410000 | -0.160000 | -143.000000 |
| first_side_raw_later_book_p60_edge0 | ask_50_59 | 11 | 4/7 | 0.363636 | 0.556364 | -0.192727 | -468.000000 |
| first_side_raw_later_book_p60_edge0 | ask_60_69 | 100 | 54/46 | 0.540000 | 0.635300 | -0.095300 | -2203.000000 |
| first_side_raw_later_book_p60_edge0 | ask_70_79 | 39 | 28/11 | 0.717949 | 0.737949 | -0.020000 | -273.000000 |
| first_side_raw_later_book_p60_edge0 | ask_80_plus | 17 | 16/1 | 0.941176 | 0.832941 | 0.108235 | 256.000000 |
| rmt_repetition_forget_p58_edge0 | ask_lt_50 | 0 | None/None | None | None | None | 0.000000 |
| rmt_repetition_forget_p58_edge0 | ask_50_59 | 30 | 12/18 | 0.400000 | 0.580667 | -0.180667 | -1245.000000 |
| rmt_repetition_forget_p58_edge0 | ask_60_69 | 86 | 47/39 | 0.546512 | 0.635581 | -0.089070 | -1773.000000 |
| rmt_repetition_forget_p58_edge0 | ask_70_79 | 38 | 28/10 | 0.736842 | 0.736316 | 0.000526 | -110.000000 |
| rmt_repetition_forget_p58_edge0 | ask_80_plus | 17 | 16/1 | 0.941176 | 0.832941 | 0.108235 | 256.000000 |
| rmt_repetition_forget_p60_edge0 | ask_lt_50 | 0 | None/None | None | None | None | 0.000000 |
| rmt_repetition_forget_p60_edge0 | ask_50_59 | 5 | 2/3 | 0.400000 | 0.562000 | -0.162000 | -182.000000 |
| rmt_repetition_forget_p60_edge0 | ask_60_69 | 108 | 58/50 | 0.537037 | 0.636111 | -0.099074 | -2468.000000 |
| rmt_repetition_forget_p60_edge0 | ask_70_79 | 41 | 30/11 | 0.731707 | 0.738537 | -0.006829 | -179.000000 |
| rmt_repetition_forget_p60_edge0 | ask_80_plus | 17 | 16/1 | 0.941176 | 0.832941 | 0.108235 | 256.000000 |
| book_ask_prior_p60_edge0 | ask_lt_50 | 0 | None/None | None | None | None | 0.000000 |
| book_ask_prior_p60_edge0 | ask_50_59 | 0 | None/None | None | None | None | 0.000000 |
| book_ask_prior_p60_edge0 | ask_60_69 | 120 | 64/56 | 0.533333 | 0.633250 | -0.099917 | -2841.000000 |
| book_ask_prior_p60_edge0 | ask_70_79 | 42 | 33/9 | 0.785714 | 0.735000 | 0.050714 | 300.000000 |
| book_ask_prior_p60_edge0 | ask_80_plus | 11 | 10/1 | 0.909091 | 0.841818 | 0.067273 | 52.000000 |
