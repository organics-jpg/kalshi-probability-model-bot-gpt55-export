# v28 Raw-Conviction Override Diagnostic

Shadow-only diagnostic. It tests whether strong raw v28 executable edge should override later book/RMT side flips.

- Raw policy: `v28_raw_p50_edge0`
- Comparison policies: `first_side_raw_later_book_p60_edge0, rmt_repetition_forget_p60_edge0, book_ask_prior_p60_edge0`

## By Later Policy Status

| bucket | count | settled | raw W/L | raw net c | raw avg c | alt settled | alt W/L | alt net c | alt - raw c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| first_side_raw_later_book_p60_edge0:same_side | 125 | 125 | 79/46 | 37.000000 | 0.296000 | 125 | 79/46 | -1257.000000 | -1294.000000 |
| first_side_raw_later_book_p60_edge0:side_flip | 44 | 44 | 22/22 | 188.000000 | 4.272727 | 44 | 22/22 | -1639.000000 | -1827.000000 |
| first_side_raw_later_book_p60_edge0:alt_missed | 3 | 3 | 0/3 | -306.000000 | -102.000000 | 0 | 0/0 | 0 | None |
| rmt_repetition_forget_p60_edge0:same_side | 120 | 120 | 78/42 | 312.000000 | 2.600000 | 120 | 78/42 | -1089.000000 | -1401.000000 |
| rmt_repetition_forget_p60_edge0:side_flip | 49 | 49 | 23/26 | -87.000000 | -1.775510 | 49 | 26/23 | -1549.000000 | -1462.000000 |
| rmt_repetition_forget_p60_edge0:alt_missed | 3 | 3 | 0/3 | -306.000000 | -102.000000 | 0 | 0/0 | 0 | None |
| book_ask_prior_p60_edge0:same_side | 118 | 118 | 77/41 | 408.000000 | 3.457627 | 118 | 77/41 | -944.000000 | -1352.000000 |
| book_ask_prior_p60_edge0:side_flip | 52 | 52 | 24/28 | -287.000000 | -5.519231 | 52 | 28/24 | -1476.000000 | -1189.000000 |
| book_ask_prior_p60_edge0:alt_missed | 2 | 2 | 0/2 | -202.000000 | -101.000000 | 0 | 0/0 | 0 | None |

## By Raw Edge Bucket

| bucket | count | settled | raw W/L | raw net c | raw avg c | alt settled | alt W/L | alt net c | alt - raw c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| first_side_raw_later_book_p60_edge0:raw_edge_ge_20pp | 11 | 11 | 4/7 | 20.000000 | 1.818182 | 11 | 9/2 | 256.000000 | 236.000000 |
| first_side_raw_later_book_p60_edge0:raw_edge_10_20pp | 22 | 22 | 10/12 | -74.000000 | -3.363636 | 22 | 9/13 | -1041.000000 | -967.000000 |
| first_side_raw_later_book_p60_edge0:raw_edge_5_10pp | 37 | 37 | 26/11 | 310.000000 | 8.378378 | 36 | 26/10 | 49.000000 | -261.000000 |
| first_side_raw_later_book_p60_edge0:raw_edge_0_5pp | 102 | 102 | 61/41 | -337.000000 | -3.303922 | 100 | 57/43 | -2160.000000 | -1823.000000 |
| rmt_repetition_forget_p60_edge0:raw_edge_ge_20pp | 11 | 11 | 4/7 | 20.000000 | 1.818182 | 11 | 8/3 | -17.000000 | -37.000000 |
| rmt_repetition_forget_p60_edge0:raw_edge_10_20pp | 22 | 22 | 10/12 | -74.000000 | -3.363636 | 22 | 11/11 | -848.000000 | -774.000000 |
| rmt_repetition_forget_p60_edge0:raw_edge_5_10pp | 37 | 37 | 26/11 | 310.000000 | 8.378378 | 36 | 27/9 | 231.000000 | -79.000000 |
| rmt_repetition_forget_p60_edge0:raw_edge_0_5pp | 102 | 102 | 61/41 | -337.000000 | -3.303922 | 100 | 58/42 | -2004.000000 | -1667.000000 |
| book_ask_prior_p60_edge0:raw_edge_ge_20pp | 11 | 11 | 4/7 | 20.000000 | 1.818182 | 11 | 7/4 | -216.000000 | -236.000000 |
| book_ask_prior_p60_edge0:raw_edge_10_20pp | 22 | 22 | 10/12 | -74.000000 | -3.363636 | 22 | 13/9 | -411.000000 | -337.000000 |
| book_ask_prior_p60_edge0:raw_edge_5_10pp | 37 | 37 | 26/11 | 310.000000 | 8.378378 | 36 | 28/8 | 458.000000 | 148.000000 |
| book_ask_prior_p60_edge0:raw_edge_0_5pp | 102 | 102 | 61/41 | -337.000000 | -3.303922 | 101 | 57/44 | -2251.000000 | -1914.000000 |

## By Status And Raw Edge

| bucket | count | settled | raw W/L | raw net c | raw avg c | alt settled | alt W/L | alt net c | alt - raw c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| first_side_raw_later_book_p60_edge0:same_side:raw_edge_ge_20pp | 4 | 4 | 3/1 | 189.000000 | 47.250000 | 4 | 3/1 | 140.000000 | -49.000000 |
| first_side_raw_later_book_p60_edge0:same_side:raw_edge_10_20pp | 11 | 11 | 4/7 | -320.000000 | -29.090909 | 11 | 4/7 | -523.000000 | -203.000000 |
| first_side_raw_later_book_p60_edge0:same_side:raw_edge_5_10pp | 34 | 34 | 25/9 | 406.000000 | 11.941176 | 34 | 25/9 | 107.000000 | -299.000000 |
| first_side_raw_later_book_p60_edge0:same_side:raw_edge_0_5pp | 76 | 76 | 47/29 | -238.000000 | -3.131579 | 76 | 47/29 | -981.000000 | -743.000000 |
| first_side_raw_later_book_p60_edge0:side_flip:raw_edge_ge_20pp | 7 | 7 | 1/6 | -169.000000 | -24.142857 | 7 | 6/1 | 116.000000 | 285.000000 |
| first_side_raw_later_book_p60_edge0:side_flip:raw_edge_10_20pp | 11 | 11 | 6/5 | 246.000000 | 22.363636 | 11 | 5/6 | -518.000000 | -764.000000 |
| first_side_raw_later_book_p60_edge0:side_flip:raw_edge_5_10pp | 2 | 2 | 1/1 | -2.000000 | -1.000000 | 2 | 1/1 | -58.000000 | -56.000000 |
| first_side_raw_later_book_p60_edge0:side_flip:raw_edge_0_5pp | 24 | 24 | 14/10 | 113.000000 | 4.708333 | 24 | 10/14 | -1179.000000 | -1292.000000 |
| rmt_repetition_forget_p60_edge0:same_side:raw_edge_ge_20pp | 3 | 3 | 2/1 | 48.000000 | 16.000000 | 3 | 2/1 | -1.000000 | -49.000000 |
| rmt_repetition_forget_p60_edge0:same_side:raw_edge_10_20pp | 9 | 9 | 4/5 | -134.000000 | -14.888889 | 9 | 4/5 | -424.000000 | -290.000000 |
| rmt_repetition_forget_p60_edge0:same_side:raw_edge_5_10pp | 33 | 33 | 25/8 | 518.000000 | 15.696970 | 33 | 25/8 | 219.000000 | -299.000000 |
| rmt_repetition_forget_p60_edge0:same_side:raw_edge_0_5pp | 75 | 75 | 47/28 | -120.000000 | -1.600000 | 75 | 47/28 | -883.000000 | -763.000000 |
| rmt_repetition_forget_p60_edge0:side_flip:raw_edge_ge_20pp | 8 | 8 | 2/6 | -28.000000 | -3.500000 | 8 | 6/2 | -16.000000 | 12.000000 |
| rmt_repetition_forget_p60_edge0:side_flip:raw_edge_10_20pp | 13 | 13 | 6/7 | 60.000000 | 4.615385 | 13 | 7/6 | -424.000000 | -484.000000 |
| rmt_repetition_forget_p60_edge0:side_flip:raw_edge_5_10pp | 3 | 3 | 1/2 | -114.000000 | -38.000000 | 3 | 2/1 | 12.000000 | 126.000000 |
| rmt_repetition_forget_p60_edge0:side_flip:raw_edge_0_5pp | 25 | 25 | 14/11 | -5.000000 | -0.200000 | 25 | 11/14 | -1121.000000 | -1116.000000 |
| book_ask_prior_p60_edge0:same_side:raw_edge_ge_20pp | 2 | 2 | 1/1 | -48.000000 | -24.000000 | 2 | 1/1 | -75.000000 | -27.000000 |
| book_ask_prior_p60_edge0:same_side:raw_edge_10_20pp | 11 | 11 | 6/5 | 88.000000 | 8.000000 | 11 | 6/5 | -308.000000 | -396.000000 |
| book_ask_prior_p60_edge0:same_side:raw_edge_5_10pp | 32 | 32 | 25/7 | 634.000000 | 19.812500 | 32 | 25/7 | 401.000000 | -233.000000 |
| book_ask_prior_p60_edge0:same_side:raw_edge_0_5pp | 73 | 73 | 45/28 | -266.000000 | -3.643836 | 73 | 45/28 | -962.000000 | -696.000000 |
| book_ask_prior_p60_edge0:side_flip:raw_edge_ge_20pp | 9 | 9 | 3/6 | 68.000000 | 7.555556 | 9 | 6/3 | -141.000000 | -209.000000 |
| book_ask_prior_p60_edge0:side_flip:raw_edge_10_20pp | 11 | 11 | 4/7 | -162.000000 | -14.727273 | 11 | 7/4 | -103.000000 | 59.000000 |
| book_ask_prior_p60_edge0:side_flip:raw_edge_5_10pp | 4 | 4 | 1/3 | -230.000000 | -57.500000 | 4 | 3/1 | 57.000000 | 287.000000 |
| book_ask_prior_p60_edge0:side_flip:raw_edge_0_5pp | 28 | 28 | 16/12 | 37.000000 | 1.321429 | 28 | 12/16 | -1289.000000 | -1326.000000 |

## By Seconds To Close

| bucket | count | settled | raw W/L | raw net c | raw avg c | alt settled | alt W/L | alt net c | alt - raw c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| first_side_raw_later_book_p60_edge0:stc_120_300 | 2 | 2 | 2/0 | 89.000000 | 44.500000 | 2 | 1/1 | -145.000000 | -234.000000 |
| first_side_raw_later_book_p60_edge0:stc_300_600 | 16 | 16 | 13/3 | 307.000000 | 19.187500 | 16 | 14/2 | 382.000000 | 75.000000 |
| first_side_raw_later_book_p60_edge0:stc_gt_600 | 154 | 154 | 86/68 | -477.000000 | -3.097403 | 151 | 86/65 | -3133.000000 | -2656.000000 |
| rmt_repetition_forget_p60_edge0:stc_120_300 | 2 | 2 | 2/0 | 89.000000 | 44.500000 | 2 | 1/1 | -145.000000 | -234.000000 |
| rmt_repetition_forget_p60_edge0:stc_300_600 | 16 | 16 | 13/3 | 307.000000 | 19.187500 | 16 | 14/2 | 374.000000 | 67.000000 |
| rmt_repetition_forget_p60_edge0:stc_gt_600 | 154 | 154 | 86/68 | -477.000000 | -3.097403 | 151 | 89/62 | -2867.000000 | -2390.000000 |
| book_ask_prior_p60_edge0:stc_120_300 | 2 | 2 | 2/0 | 89.000000 | 44.500000 | 2 | 1/1 | -139.000000 | -228.000000 |
| book_ask_prior_p60_edge0:stc_300_600 | 16 | 16 | 13/3 | 307.000000 | 19.187500 | 16 | 14/2 | 466.000000 | 159.000000 |
| book_ask_prior_p60_edge0:stc_gt_600 | 154 | 154 | 86/68 | -477.000000 | -3.097403 | 152 | 90/62 | -2747.000000 | -2270.000000 |

## By Recross Hazard

| bucket | count | settled | raw W/L | raw net c | raw avg c | alt settled | alt W/L | alt net c | alt - raw c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| first_side_raw_later_book_p60_edge0:recross_high_True | 165 | 165 | 94/71 | -144.000000 | -0.872727 | 162 | 94/68 | -3126.000000 | -2982.000000 |
| first_side_raw_later_book_p60_edge0:recross_high_False | 7 | 7 | 7/0 | 63.000000 | 9.000000 | 7 | 7/0 | 230.000000 | 167.000000 |
| rmt_repetition_forget_p60_edge0:recross_high_True | 165 | 165 | 94/71 | -144.000000 | -0.872727 | 162 | 97/65 | -2868.000000 | -2724.000000 |
| rmt_repetition_forget_p60_edge0:recross_high_False | 7 | 7 | 7/0 | 63.000000 | 9.000000 | 7 | 7/0 | 230.000000 | 167.000000 |
| book_ask_prior_p60_edge0:recross_high_True | 165 | 165 | 94/71 | -144.000000 | -0.872727 | 163 | 98/65 | -2697.000000 | -2553.000000 |
| book_ask_prior_p60_edge0:recross_high_False | 7 | 7 | 7/0 | 63.000000 | 9.000000 | 7 | 7/0 | 277.000000 | 214.000000 |

## Recent Comparisons

| market | alt policy | status | raw side | alt side | raw edge | raw stc | recross | raw won | alt won | raw net | alt net |
|---|---|---|---|---|---:|---:|---|---|---|---:|---:|
| KXBTC15M-26MAY071000-00 | first_side_raw_later_book_p60_edge0 | side_flip | yes | no | 0.003510 | 868.958000 | True | False | True | -112.000000 | 64.000000 |
| KXBTC15M-26MAY071000-00 | rmt_repetition_forget_p60_edge0 | side_flip | yes | no | 0.003510 | 868.958000 | True | False | True | -112.000000 | 64.000000 |
| KXBTC15M-26MAY071000-00 | book_ask_prior_p60_edge0 | side_flip | yes | no | 0.003510 | 868.958000 | True | False | True | -112.000000 | 64.000000 |
| KXBTC15M-26MAY071015-15 | first_side_raw_later_book_p60_edge0 | same_side | no | no | 0.009894 | 864.225000 | True | False | False | -124.000000 | -124.000000 |
| KXBTC15M-26MAY071015-15 | rmt_repetition_forget_p60_edge0 | same_side | no | no | 0.009894 | 864.225000 | True | False | False | -124.000000 | -124.000000 |
| KXBTC15M-26MAY071015-15 | book_ask_prior_p60_edge0 | same_side | no | no | 0.009894 | 864.225000 | True | False | False | -124.000000 | -124.000000 |
| KXBTC15M-26MAY071030-30 | first_side_raw_later_book_p60_edge0 | same_side | no | no | 0.026380 | 852.539000 | True | True | True | 72.000000 | 72.000000 |
| KXBTC15M-26MAY071030-30 | rmt_repetition_forget_p60_edge0 | same_side | no | no | 0.026380 | 852.539000 | True | True | True | 72.000000 | 72.000000 |
| KXBTC15M-26MAY071030-30 | book_ask_prior_p60_edge0 | same_side | no | no | 0.026380 | 852.539000 | True | True | True | 72.000000 | 72.000000 |
| KXBTC15M-26MAY071045-45 | first_side_raw_later_book_p60_edge0 | side_flip | yes | no | 0.007862 | 862.859000 | True | False | True | -114.000000 | 51.000000 |
| KXBTC15M-26MAY071045-45 | rmt_repetition_forget_p60_edge0 | side_flip | yes | no | 0.007862 | 862.859000 | True | False | True | -114.000000 | 51.000000 |
| KXBTC15M-26MAY071045-45 | book_ask_prior_p60_edge0 | side_flip | yes | no | 0.007862 | 862.859000 | True | False | True | -114.000000 | 51.000000 |
| KXBTC15M-26MAY071100-00 | first_side_raw_later_book_p60_edge0 | side_flip | no | yes | 0.018800 | 817.821000 | True | True | False | 84.000000 | -134.000000 |
| KXBTC15M-26MAY071100-00 | rmt_repetition_forget_p60_edge0 | side_flip | no | yes | 0.018800 | 817.821000 | True | True | False | 84.000000 | -134.000000 |
| KXBTC15M-26MAY071100-00 | book_ask_prior_p60_edge0 | side_flip | no | yes | 0.018800 | 817.821000 | True | True | False | 84.000000 | -134.000000 |
| KXBTC15M-26MAY071115-15 | first_side_raw_later_book_p60_edge0 | same_side | no | no | 0.015838 | 843.330000 | True | False | False | -128.000000 | -128.000000 |
| KXBTC15M-26MAY071115-15 | rmt_repetition_forget_p60_edge0 | same_side | no | no | 0.015838 | 843.330000 | True | False | False | -128.000000 | -128.000000 |
| KXBTC15M-26MAY071115-15 | book_ask_prior_p60_edge0 | same_side | no | no | 0.015838 | 843.330000 | True | False | False | -128.000000 | -128.000000 |
| KXBTC15M-26MAY071130-30 | first_side_raw_later_book_p60_edge0 | side_flip | no | yes | 0.002087 | 721.923000 | True | True | False | 80.000000 | -124.000000 |
| KXBTC15M-26MAY071130-30 | rmt_repetition_forget_p60_edge0 | side_flip | no | yes | 0.002087 | 721.923000 | True | True | False | 80.000000 | -124.000000 |
| KXBTC15M-26MAY071130-30 | book_ask_prior_p60_edge0 | side_flip | no | yes | 0.002087 | 721.923000 | True | True | False | 80.000000 | -124.000000 |
| KXBTC15M-26MAY071145-45 | first_side_raw_later_book_p60_edge0 | same_side | yes | yes | 0.035637 | 858.916000 | True | True | True | 74.000000 | 74.000000 |
| KXBTC15M-26MAY071145-45 | rmt_repetition_forget_p60_edge0 | same_side | yes | yes | 0.035637 | 858.916000 | True | True | True | 74.000000 | 74.000000 |
| KXBTC15M-26MAY071145-45 | book_ask_prior_p60_edge0 | same_side | yes | yes | 0.035637 | 858.916000 | True | True | True | 74.000000 | 74.000000 |
| KXBTC15M-26MAY071200-00 | first_side_raw_later_book_p60_edge0 | same_side | yes | yes | 0.006055 | 793.821000 | True | False | False | -124.000000 | -130.000000 |
| KXBTC15M-26MAY071200-00 | rmt_repetition_forget_p60_edge0 | same_side | yes | yes | 0.006055 | 793.821000 | True | False | False | -124.000000 | -130.000000 |
| KXBTC15M-26MAY071200-00 | book_ask_prior_p60_edge0 | same_side | yes | yes | 0.006055 | 793.821000 | True | False | False | -124.000000 | -128.000000 |
| KXBTC15M-26MAY071215-15 | first_side_raw_later_book_p60_edge0 | same_side | yes | yes | 0.039397 | 864.223000 | True | False | False | -98.000000 | -124.000000 |
| KXBTC15M-26MAY071215-15 | rmt_repetition_forget_p60_edge0 | same_side | yes | yes | 0.039397 | 864.223000 | True | False | False | -98.000000 | -124.000000 |
| KXBTC15M-26MAY071215-15 | book_ask_prior_p60_edge0 | same_side | yes | yes | 0.039397 | 864.223000 | True | False | False | -98.000000 | -124.000000 |
| KXBTC15M-26MAY071230-30 | first_side_raw_later_book_p60_edge0 | same_side | no | no | 0.029882 | 863.492000 | True | False | False | -143.000000 | -143.000000 |
| KXBTC15M-26MAY071230-30 | rmt_repetition_forget_p60_edge0 | same_side | no | no | 0.029882 | 863.492000 | True | False | False | -143.000000 | -143.000000 |
| KXBTC15M-26MAY071230-30 | book_ask_prior_p60_edge0 | same_side | no | no | 0.029882 | 863.492000 | True | False | False | -143.000000 | -128.000000 |
| KXBTC15M-26MAY071245-45 | first_side_raw_later_book_p60_edge0 | same_side | yes | yes | 0.009979 | 884.360000 | True | False | False | -114.000000 | -134.000000 |
| KXBTC15M-26MAY071245-45 | rmt_repetition_forget_p60_edge0 | same_side | yes | yes | 0.009979 | 884.360000 | True | False | False | -114.000000 | -134.000000 |
| KXBTC15M-26MAY071245-45 | book_ask_prior_p60_edge0 | same_side | yes | yes | 0.009979 | 884.360000 | True | False | False | -114.000000 | -134.000000 |
| KXBTC15M-26MAY071300-00 | first_side_raw_later_book_p60_edge0 | same_side | yes | yes | 0.046040 | 842.515000 | True | False | False | -122.000000 | -122.000000 |
| KXBTC15M-26MAY071300-00 | rmt_repetition_forget_p60_edge0 | same_side | yes | yes | 0.046040 | 842.515000 | True | False | False | -122.000000 | -122.000000 |
| KXBTC15M-26MAY071300-00 | book_ask_prior_p60_edge0 | same_side | yes | yes | 0.046040 | 842.515000 | True | False | False | -122.000000 | -140.000000 |
| KXBTC15M-26MAY071315-15 | first_side_raw_later_book_p60_edge0 | same_side | yes | yes | 0.023442 | 858.849000 | True | True | True | 94.000000 | 57.000000 |
| KXBTC15M-26MAY071315-15 | rmt_repetition_forget_p60_edge0 | same_side | yes | yes | 0.023442 | 858.849000 | True | True | True | 94.000000 | 57.000000 |
| KXBTC15M-26MAY071315-15 | book_ask_prior_p60_edge0 | same_side | yes | yes | 0.023442 | 858.849000 | True | True | True | 94.000000 | 57.000000 |
| KXBTC15M-26MAY071330-30 | first_side_raw_later_book_p60_edge0 | side_flip | yes | no | 0.024206 | 849.512000 | True | False | True | -108.000000 | 66.000000 |
| KXBTC15M-26MAY071330-30 | rmt_repetition_forget_p60_edge0 | side_flip | yes | no | 0.024206 | 849.512000 | True | False | True | -108.000000 | 66.000000 |
| KXBTC15M-26MAY071330-30 | book_ask_prior_p60_edge0 | side_flip | yes | no | 0.024206 | 849.512000 | True | False | True | -108.000000 | 76.000000 |
