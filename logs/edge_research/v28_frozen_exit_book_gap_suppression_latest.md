# v28 Frozen Exit Book-Gap Suppression

- Freeze timestamp UTC: `2026-05-06T08:46:39.207330+00:00`
- Candidate: `suppress_soft_gap15_or_p_hold75`
- Rule: `If exit reason is mushroom_v28_exit_value_over_hold or mushroom_v28_probability_reduce, hold to settlement when p_hold - exit_bid >= 0.15 or p_hold >= 0.75; otherwise keep current v28 exit. Do not suppress probability_collapse_full.`
- Future rows/settled: `120/120`
- Current/candidate gross: `727.0c/962.0c`
- Delta vs current: `235.0c`
- Blockers: `suppressed_loss_control_cost_negative`

## Interpretation

- Frozen soft-exit book-gap candidate has 120 settled future rows.
- Delta versus current v28 exits is 235.0c.
- Suppressed exits: 59; winner recovery 1315.0c; loss-control cost -1080.0c.

## Rows

| market | side | result | entry | exit | reason | p_hold | bid | gap | drawdown | current c | hold c | candidate c | delta c | suppressed | worst hold mark |
|---|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| KXBTC15M-26MAY060500-00 | yes | yes | 79 | None |  | None | None | None | None | 42.0 | 42.0 | 42.0 | 0.000000 | False | None |
| KXBTC15M-26MAY060515-15 | no | no | 79 | 66 | mushroom_v28_probability_collapse_full | 0.669735 | 0.660000 | 0.009735 | 16.026514 | -26.0 | 42.0 | -26.0 | 0.000000 | False | 40 |
| KXBTC15M-26MAY060515-15 | no | no | 74 | 95 | mushroom_v28_exit_value_over_hold | 0.769032 | 0.950000 | -0.180968 | -2.903190 | 42.0 | 52.0 | 52.0 | 10.000000 | True | 40 |
| KXBTC15M-26MAY060530-30 | no | no | 78 | 95 | mushroom_v28_exit_value_over_hold | 0.899953 | 0.950000 | -0.050047 | -11.995311 | 34.0 | 44.0 | 44.0 | 10.000000 | True | 30 |
| KXBTC15M-26MAY060545-45 | yes | yes | 90 | None |  | None | None | None | None | 20.0 | 20.0 | 20.0 | 0.000000 | False | None |
| KXBTC15M-26MAY060600-00 | no | no | 75 | 81 | mushroom_v28_exit_value_over_hold | 0.804105 | 0.820000 | -0.015895 | 1.589476 | 12.0 | 50.0 | 50.0 | 38.000000 | True | -34 |
| KXBTC15M-26MAY060615-15 | yes | yes | 75 | 60 | mushroom_v28_probability_collapse_full | 0.643484 | 0.600000 | 0.043484 | 10.651569 | -30.0 | 50.0 | -30.0 | 0.000000 | False | -54 |
| KXBTC15M-26MAY060615-15 | yes | yes | 88 | None |  | None | None | None | None | 24.0 | 24.0 | 24.0 | 0.000000 | False | -54 |
| KXBTC15M-26MAY060630-30 | yes | yes | 79 | 73 | mushroom_v28_probability_reduce | 0.777774 | 0.730000 | 0.047774 | 1.222639 | -12.0 | 42.0 | 42.0 | 54.000000 | True | 26 |
| KXBTC15M-26MAY060630-30 | yes | yes | 85 | 99 | mushroom_v28_exit_value_over_hold | 0.978151 | 0.990000 | -0.011849 | -12.815129 | 28.0 | 30.0 | 30.0 | 2.000000 | True | 26 |
| KXBTC15M-26MAY060645-45 | yes | yes | 82 | 74 | mushroom_v28_probability_reduce | 0.799349 | 0.740000 | 0.059349 | 2.065125 | -16.0 | 36.0 | 36.0 | 52.000000 | True | 30 |
| KXBTC15M-26MAY060645-45 | yes | yes | 78 | 72 | mushroom_v28_probability_reduce | 0.779789 | 0.720000 | 0.059789 | 0.021114 | -12.0 | 44.0 | 44.0 | 56.000000 | True | 30 |
| KXBTC15M-26MAY060645-45 | yes | yes | 80 | 97 | mushroom_v28_exit_value_over_hold | 0.962354 | 0.970000 | -0.007646 | -16.235382 | 34.0 | 40.0 | 40.0 | 6.000000 | True | 30 |
| KXBTC15M-26MAY060700-00 | no | yes | 84 | 80 | mushroom_v28_probability_reduce | 0.799603 | 0.800000 | -0.000397 | 4.039746 | -8.0 | -168.0 | -168.0 | -160.000000 | True | 10 |
| KXBTC15M-26MAY060700-00 | yes | yes | 75 | 64 | mushroom_v28_probability_reduce | 0.748579 | 0.640000 | 0.108579 | 0.142079 | -22.0 | 50.0 | -22.0 | 0.000000 | False | 10 |
| KXBTC15M-26MAY060700-00 | yes | yes | 77 | 62 | mushroom_v28_probability_collapse_full | 0.674479 | 0.620000 | 0.054479 | 9.552131 | -30.0 | 46.0 | -30.0 | 0.000000 | False | 10 |
| KXBTC15M-26MAY060700-00 | yes | yes | 83 | 89 | mushroom_v28_exit_value_over_hold | 0.743339 | 0.890000 | -0.146661 | 8.666129 | 12.0 | 34.0 | 12.0 | 0.000000 | False | 10 |
| KXBTC15M-26MAY060715-15 | yes | yes | 81 | 93 | mushroom_v28_exit_value_over_hold | 0.920907 | 0.930000 | -0.009093 | -11.090690 | 24.0 | 38.0 | 38.0 | 14.000000 | True | 20 |
| KXBTC15M-26MAY060715-15 | yes | yes | 89 | 99 | mushroom_v28_exit_value_over_hold | 0.984061 | 0.990000 | -0.005939 | -8.406103 | 20.0 | 22.0 | 22.0 | 2.000000 | True | 20 |
| KXBTC15M-26MAY060730-30 | yes | yes | 84 | None |  | None | None | None | None | 32.0 | 32.0 | 32.0 | 0.000000 | False | None |
| KXBTC15M-26MAY060745-45 | yes | no | 69 | 57 | mushroom_v28_probability_collapse_full | 0.610349 | 0.570000 | 0.040349 | 7.965096 | -24.0 | -138.0 | -24.0 | 0.000000 | False | -156 |
| KXBTC15M-26MAY060745-45 | yes | no | 78 | 43 | mushroom_v28_probability_collapse_full | 0.563569 | 0.430000 | 0.133569 | 21.643115 | -70.0 | -156.0 | -70.0 | 0.000000 | False | -156 |
| KXBTC15M-26MAY060800-00 | yes | yes | 79 | 70 | mushroom_v28_probability_reduce | 0.738185 | 0.700000 | 0.038185 | 5.181496 | -18.0 | 42.0 | -18.0 | 0.000000 | False | -30 |
| KXBTC15M-26MAY060800-00 | yes | yes | 66 | 50 | mushroom_v28_probability_collapse_full | 0.614703 | 0.500000 | 0.114703 | 4.529724 | -32.0 | 68.0 | -32.0 | 0.000000 | False | -30 |
| KXBTC15M-26MAY060815-15 | no | no | 79 | None |  | None | None | None | None | 42.0 | 42.0 | 42.0 | 0.000000 | False | None |
| KXBTC15M-26MAY060830-30 | yes | yes | 76 | 100 | mushroom_v28_exit_value_over_hold | 0.992185 | 1.000000 | -0.007815 | -23.218487 | 48.0 | 48.0 | 48.0 | 0.000000 | True | 48 |
| KXBTC15M-26MAY060900-00 | yes | no | 78 | 73 | mushroom_v28_probability_reduce | 0.789990 | 0.730000 | 0.059990 | -0.998969 | -10.0 | -156.0 | -156.0 | -146.000000 | True | 34 |
| KXBTC15M-26MAY060900-00 | yes | no | 78 | 40 | mushroom_v28_probability_collapse_full | 0.397320 | 0.400000 | -0.002680 | 41.268037 | -76.0 | -156.0 | -76.0 | 0.000000 | False | 34 |
| KXBTC15M-26MAY060900-00 | no | no | 73 | 65 | mushroom_v28_probability_reduce | 0.721102 | 0.650000 | 0.071102 | 0.889760 | -16.0 | 54.0 | -16.0 | 0.000000 | False | 34 |
| KXBTC15M-26MAY060900-00 | no | no | 79 | 96 | mushroom_v28_exit_value_over_hold | 0.948348 | 0.960000 | -0.011652 | -15.834839 | 34.0 | 42.0 | 42.0 | 8.000000 | True | 34 |
| KXBTC15M-26MAY060915-15 | no | no | 70 | 70 | mushroom_v28_probability_reduce | 0.793762 | 0.700000 | 0.093762 | -9.376204 | 0.0 | 60.0 | 60.0 | 60.000000 | True | 48 |
| KXBTC15M-26MAY060915-15 | no | no | 75 | 100 | mushroom_v28_exit_value_over_hold | 0.994245 | 1.000000 | -0.005755 | -17.424453 | 50.0 | 50.0 | 50.0 | 0.000000 | True | 48 |
| KXBTC15M-26MAY060930-30 | no | no | 76 | 66 | mushroom_v28_probability_reduce | 0.725946 | 0.660000 | 0.065946 | 3.405368 | -20.0 | 48.0 | -20.0 | 0.000000 | False | -10 |
| KXBTC15M-26MAY060930-30 | no | no | 76 | 69 | mushroom_v28_probability_reduce | 0.787606 | 0.680000 | 0.107606 | -2.760587 | -14.0 | 48.0 | 48.0 | 62.000000 | True | -10 |
| KXBTC15M-26MAY060930-30 | no | no | 73 | 72 | mushroom_v28_probability_reduce | 0.799180 | 0.710000 | 0.089180 | -6.917970 | -3.0 | 54.0 | 54.0 | 57.000000 | True | -10 |
| KXBTC15M-26MAY060930-30 | no | no | 77 | None |  | None | None | None | None | 46.0 | 46.0 | 46.0 | 0.000000 | False | -10 |
| KXBTC15M-26MAY060945-45 | no | no | 59 | 51 | mushroom_v28_probability_collapse_full | 0.556556 | 0.510000 | 0.046556 | 3.344394 | -16.0 | 82.0 | -16.0 | 0.000000 | False | 40 |
| KXBTC15M-26MAY060945-45 | no | no | 70 | 62 | mushroom_v28_probability_collapse_full | 0.689159 | 0.620000 | 0.069159 | 1.084126 | -16.0 | 60.0 | -16.0 | 0.000000 | False | 40 |
| KXBTC15M-26MAY060945-45 | no | no | 71 | 65 | mushroom_v28_probability_reduce | 0.735773 | 0.650000 | 0.085773 | -2.577325 | -12.0 | 58.0 | -12.0 | 0.000000 | False | 40 |
| KXBTC15M-26MAY060945-45 | no | no | 72 | 96 | mushroom_v28_exit_value_over_hold | 0.950787 | 0.960000 | -0.009213 | -23.078686 | 48.0 | 56.0 | 56.0 | 8.000000 | True | 40 |
| KXBTC15M-26MAY061000-00 | no | no | 65 | None |  | None | None | None | None | 70.0 | 70.0 | 70.0 | 0.000000 | False | None |
| KXBTC15M-26MAY061015-15 | no | no | 68 | 65 | mushroom_v28_probability_reduce | 0.733426 | 0.650000 | 0.083426 | -5.342610 | -6.0 | 64.0 | -6.0 | 0.000000 | False | 4 |
| KXBTC15M-26MAY061015-15 | no | no | 70 | 70 | mushroom_v28_probability_reduce | 0.799979 | 0.700000 | 0.099979 | -9.997858 | 0.0 | 60.0 | 60.0 | 60.000000 | True | 4 |
| KXBTC15M-26MAY061015-15 | no | no | 73 | None |  | None | None | None | None | 54.0 | 54.0 | 54.0 | 0.000000 | False | 4 |
| KXBTC15M-26MAY061030-30 | yes | yes | 78 | 70 | mushroom_v28_probability_reduce | 0.752739 | 0.700000 | 0.052739 | 2.726149 | -16.0 | 44.0 | 44.0 | 60.000000 | True | -10 |
| KXBTC15M-26MAY061030-30 | yes | yes | 78 | 73 | mushroom_v28_probability_reduce | 0.796458 | 0.730000 | 0.066458 | -1.645773 | -10.0 | 44.0 | 44.0 | 54.000000 | True | -10 |
| KXBTC15M-26MAY061030-30 | yes | yes | 74 | None |  | None | None | None | None | 52.0 | 52.0 | 52.0 | 0.000000 | False | -10 |
| KXBTC15M-26MAY061045-45 | yes | yes | 80 | 77 | mushroom_v28_probability_reduce | 0.796949 | 0.770000 | 0.026949 | 0.305083 | -6.0 | 40.0 | 40.0 | 46.000000 | True | 28 |
| KXBTC15M-26MAY061045-45 | yes | yes | 84 | 98 | mushroom_v28_exit_value_over_hold | 0.975987 | 0.990000 | -0.014013 | -13.598681 | 28.0 | 32.0 | 32.0 | 4.000000 | True | 28 |
| KXBTC15M-26MAY061100-00 | no | no | 83 | 63 | mushroom_v28_probability_collapse_full | 0.704126 | 0.630000 | 0.074126 | 12.587383 | -40.0 | 34.0 | -40.0 | 0.000000 | False | -40 |
| KXBTC15M-26MAY061100-00 | no | no | 81 | None |  | None | None | None | None | 38.0 | 38.0 | 38.0 | 0.000000 | False | -40 |
| KXBTC15M-26MAY061130-30 | yes | yes | 80 | None |  | None | None | None | None | 40.0 | 40.0 | 40.0 | 0.000000 | False | None |
| KXBTC15M-26MAY061200-00 | yes | yes | 82 | 90 | mushroom_v28_exit_value_over_hold | 0.889296 | 0.900000 | -0.010704 | -7.929607 | 16.0 | 36.0 | 36.0 | 20.000000 | True | 14 |
| KXBTC15M-26MAY061300-00 | yes | no | 80 | 65 | mushroom_v28_probability_collapse_full | 0.666430 | 0.650000 | 0.016430 | 13.356971 | -30.0 | -160.0 | -30.0 | 0.000000 | False | None |
| KXBTC15M-26MAY061400-00 | no | no | 89 | 84 | mushroom_v28_exit_value_over_hold | 0.737977 | 0.840000 | -0.102023 | 15.202342 | -10.0 | 22.0 | -10.0 | 0.000000 | False | -16 |
| KXBTC15M-26MAY061415-15 | no | no | 88 | None |  | None | None | None | None | 24.0 | 24.0 | 24.0 | 0.000000 | False | None |
| KXBTC15M-26MAY061445-45 | no | no | 88 | 77 | mushroom_v28_probability_reduce | 0.797830 | 0.770000 | 0.027830 | 8.216985 | -22.0 | 24.0 | 24.0 | 46.000000 | True | 14 |
| KXBTC15M-26MAY061445-45 | no | no | 90 | 99 | mushroom_v28_exit_value_over_hold | 0.981991 | 0.990000 | -0.008009 | -8.199066 | 18.0 | 20.0 | 20.0 | 2.000000 | True | 14 |
| KXBTC15M-26MAY061545-45 | yes | yes | 84 | 95 | mushroom_v28_exit_value_over_hold | 0.935410 | 0.950000 | -0.014590 | -9.540987 | 22.0 | 32.0 | 32.0 | 10.000000 | True | 18 |
| KXBTC15M-26MAY061615-15 | yes | yes | 90 | 94 | mushroom_v28_exit_value_over_hold | 0.931218 | 0.940000 | -0.008782 | -3.121769 | 8.0 | 20.0 | 20.0 | 12.000000 | True | 10 |
| KXBTC15M-26MAY061645-45 | no | no | 76 | None |  | None | None | None | None | 48.0 | 48.0 | 48.0 | 0.000000 | False | None |
| KXBTC15M-26MAY061800-00 | no | no | 67 | 24 | mushroom_v28_probability_collapse_full | 0.552607 | 0.240000 | 0.312607 | 11.739327 | -86.0 | 66.0 | -86.0 | 0.000000 | False | -82 |
| KXBTC15M-26MAY061815-15 | no | no | 84 | 96 | mushroom_v28_exit_value_over_hold | 0.950684 | 0.960000 | -0.009316 | -11.068394 | 24.0 | 32.0 | 32.0 | 8.000000 | True | 24 |
| KXBTC15M-26MAY061830-30 | no | no | 89 | 99 | mushroom_v28_exit_value_over_hold | 0.976718 | 0.990000 | -0.013282 | -8.671753 | 20.0 | 22.0 | 22.0 | 2.000000 | True | 20 |
| KXBTC15M-26MAY061900-00 | yes | yes | 90 | None |  | None | None | None | None | 20.0 | 20.0 | 20.0 | 0.000000 | False | None |
| KXBTC15M-26MAY061915-15 | no | no | 87 | 99 | mushroom_v28_exit_value_over_hold | 0.981987 | 0.990000 | -0.008013 | -11.198704 | 24.0 | 26.0 | 26.0 | 2.000000 | True | 22 |
| KXBTC15M-26MAY062015-15 | no | no | 42 | 12 | mushroom_v28_probability_collapse_full | 0.268932 | 0.120000 | 0.148932 | 15.106811 | -60.0 | 116.0 | -60.0 | 0.000000 | False | -172 |
| KXBTC15M-26MAY062015-15 | yes | no | 86 | 90 | mushroom_v28_exit_value_over_hold | 0.812359 | 0.900000 | -0.087641 | 4.764109 | 8.0 | -172.0 | -172.0 | -180.000000 | True | -172 |
| KXBTC15M-26MAY062015-15 | yes | no | 67 | None |  | None | None | None | None | -134.0 | -134.0 | -134.0 | 0.000000 | False | -172 |
| KXBTC15M-26MAY062030-30 | no | no | 67 | 83 | mushroom_v28_exit_value_over_hold | 0.661475 | 0.830000 | -0.168525 | 0.852486 | 32.0 | 66.0 | 32.0 | 0.000000 | False | 42 |
| KXBTC15M-26MAY062045-45 | no | no | 80 | 92 | mushroom_v28_exit_value_over_hold | 0.891386 | 0.920000 | -0.028614 | -9.138584 | 24.0 | 40.0 | 40.0 | 16.000000 | True | 24 |
| KXBTC15M-26MAY062100-00 | yes | yes | 83 | 81 | mushroom_v28_exit_value_over_hold | 0.647591 | 0.810000 | -0.162409 | 18.240924 | -4.0 | 34.0 | -4.0 | 0.000000 | False | -82 |
| KXBTC15M-26MAY062100-00 | yes | yes | 84 | 74 | mushroom_v28_exit_value_over_hold | 0.663692 | 0.740000 | -0.076308 | 17.630840 | -20.0 | 32.0 | -20.0 | 0.000000 | False | -82 |
| KXBTC15M-26MAY062100-00 | yes | yes | 61 | 68 | mushroom_v28_exit_value_over_hold | 0.489234 | 0.680000 | -0.190766 | 12.076646 | 14.0 | 78.0 | 14.0 | 0.000000 | False | -82 |
| KXBTC15M-26MAY062115-15 | yes | yes | 73 | 67 | mushroom_v28_exit_value_over_hold | 0.395750 | 0.670000 | -0.274250 | 33.425046 | -12.0 | 54.0 | -12.0 | 0.000000 | False | 22 |
| KXBTC15M-26MAY062115-15 | no | yes | 69 | 52 | mushroom_v28_exit_value_over_hold | 0.455777 | 0.520000 | -0.064223 | 14.422271 | -34.0 | -138.0 | -34.0 | 0.000000 | False | 22 |
| KXBTC15M-26MAY062115-15 | yes | yes | 88 | 99 | mushroom_v28_exit_value_over_hold | 0.982461 | 0.990000 | -0.007539 | -10.246054 | 22.0 | 24.0 | 24.0 | 2.000000 | True | 22 |
| KXBTC15M-26MAY062130-30 | no | yes | 76 | 60 | mushroom_v28_probability_reduce | 0.768407 | 0.600000 | 0.168407 | 6.159273 | -32.0 | -152.0 | -152.0 | -120.000000 | True | -152 |
| KXBTC15M-26MAY062215-15 | no | no | 65 | 72 | mushroom_v28_probability_collapse_full | 0.708248 | 0.720000 | -0.011752 | -5.824841 | 14.0 | 70.0 | 14.0 | 0.000000 | False | 10 |
| KXBTC15M-26MAY062215-15 | no | no | 84 | 89 | mushroom_v28_exit_value_over_hold | 0.860673 | 0.890000 | -0.029327 | -2.067333 | 10.0 | 32.0 | 32.0 | 22.000000 | True | 10 |
| KXBTC15M-26MAY062245-45 | yes | yes | 86 | 90 | mushroom_v28_exit_value_over_hold | 0.643812 | 0.900000 | -0.256188 | 15.618779 | 8.0 | 28.0 | 8.0 | 0.000000 | False | 4 |
| KXBTC15M-26MAY062300-00 | yes | yes | 87 | 95 | mushroom_v28_exit_value_over_hold | 0.746374 | 0.950000 | -0.203626 | 10.362646 | 16.0 | 26.0 | 16.0 | 0.000000 | False | 14 |
| KXBTC15M-26MAY062315-15 | no | no | 84 | 87 | mushroom_v28_exit_value_over_hold | 0.811182 | 0.870000 | -0.058818 | 2.881757 | 6.0 | 32.0 | 32.0 | 26.000000 | True | -52 |
| KXBTC15M-26MAY070000-00 | no | no | 78 | 79 | mushroom_v28_exit_value_over_hold | 0.726702 | 0.790000 | -0.063298 | 5.329808 | 2.0 | 44.0 | 2.0 | 0.000000 | False | -14 |
| KXBTC15M-26MAY070015-15 | no | yes | 70 | 69 | mushroom_v28_exit_value_over_hold | 0.596562 | 0.690000 | -0.093438 | 10.343815 | -2.0 | -140.0 | -2.0 | 0.000000 | False | -140 |
| KXBTC15M-26MAY070030-30 | yes | yes | 82 | 97 | mushroom_v28_exit_value_over_hold | 0.921778 | 0.970000 | -0.048222 | -10.177771 | 30.0 | 36.0 | 36.0 | 6.000000 | True | 6 |
| KXBTC15M-26MAY070115-15 | yes | yes | 82 | 82 | mushroom_v28_exit_value_over_hold | 0.679619 | 0.820000 | -0.140381 | 18.038087 | 0.0 | 36.0 | 0.0 | 0.000000 | False | -6 |
| KXBTC15M-26MAY070545-45 | no | no | 82 | 91 | mushroom_v28_exit_value_over_hold | 0.892567 | 0.910000 | -0.017433 | -7.256748 | 18.0 | 36.0 | 36.0 | 18.000000 | True | -4 |
| KXBTC15M-26MAY070645-45 | yes | yes | 81 | None |  | None | None | None | None | 38.0 | 38.0 | 38.0 | 0.000000 | False | None |
| KXBTC15M-26MAY070745-45 | yes | yes | 68 | 85 | mushroom_v28_exit_value_over_hold | 0.821701 | 0.850000 | -0.028299 | -14.170103 | 34.0 | 64.0 | 64.0 | 30.000000 | True | 50 |
| KXBTC15M-26MAY070815-15 | yes | yes | 90 | 91 | mushroom_v28_exit_value_over_hold | 0.890464 | 0.910000 | -0.019536 | -1.046434 | 2.0 | 20.0 | 20.0 | 18.000000 | True | 2 |
| KXBTC15M-26MAY070830-30 | no | no | 82 | 91 | mushroom_v28_exit_value_over_hold | 0.825354 | 0.910000 | -0.084646 | -0.535395 | 18.0 | 36.0 | 36.0 | 18.000000 | True | -24 |
| KXBTC15M-26MAY070830-30 | no | no | 77 | 70 | mushroom_v28_exit_value_over_hold | 0.612998 | 0.700000 | -0.087002 | 15.700151 | -14.0 | 46.0 | -14.0 | 0.000000 | False | -24 |
| KXBTC15M-26MAY070830-30 | no | no | 77 | None |  | None | None | None | None | 46.0 | 46.0 | 46.0 | 0.000000 | False | -24 |
| KXBTC15M-26MAY070915-15 | no | no | 77 | None |  | None | None | None | None | 46.0 | 46.0 | 46.0 | 0.000000 | False | None |
| KXBTC15M-26MAY070930-30 | yes | yes | 80 | 97 | mushroom_v28_exit_value_over_hold | 0.969995 | 0.980000 | -0.010005 | -13.999536 | 34.0 | 40.0 | 40.0 | 6.000000 | True | -56 |
| KXBTC15M-26MAY070945-45 | no | no | 69 | None |  | None | None | None | None | 62.0 | 62.0 | 62.0 | 0.000000 | False | None |
| KXBTC15M-26MAY071000-00 | no | no | 73 | 55 | mushroom_v28_probability_collapse_full | 0.617577 | 0.550000 | 0.067577 | 11.242300 | -36.0 | 54.0 | -36.0 | 0.000000 | False | 12 |
| KXBTC15M-26MAY071000-00 | no | no | 71 | 79 | mushroom_v28_probability_reduce | 0.781361 | 0.790000 | -0.008639 | 6.863933 | 16.0 | 58.0 | 58.0 | 42.000000 | True | 12 |
| KXBTC15M-26MAY071015-15 | no | yes | 78 | 79 | mushroom_v28_probability_reduce | 0.789130 | 0.790000 | -0.000870 | -0.913001 | 2.0 | -156.0 | -156.0 | -158.000000 | True | 18 |
| KXBTC15M-26MAY071015-15 | no | yes | 81 | 73 | mushroom_v28_probability_reduce | 0.763980 | 0.730000 | 0.033980 | 4.602013 | -16.0 | -162.0 | -162.0 | -146.000000 | True | 18 |
| KXBTC15M-26MAY071015-15 | yes | yes | 84 | 94 | mushroom_v28_exit_value_over_hold | 0.923102 | 0.940000 | -0.016898 | -8.310249 | 20.0 | 32.0 | 32.0 | 12.000000 | True | 18 |
| KXBTC15M-26MAY071030-30 | no | no | 77 | 65 | mushroom_v28_probability_collapse_full | 0.709831 | 0.650000 | 0.059831 | 6.016933 | -24.0 | 46.0 | -24.0 | 0.000000 | False | -20 |
| KXBTC15M-26MAY071030-30 | no | no | 76 | None |  | None | None | None | None | 48.0 | 48.0 | 48.0 | 0.000000 | False | -20 |
| KXBTC15M-26MAY071045-45 | no | no | 74 | 69 | mushroom_v28_probability_reduce | 0.760529 | 0.690000 | 0.070529 | -2.052947 | -10.0 | 52.0 | 52.0 | 62.000000 | True | -14 |
| KXBTC15M-26MAY071045-45 | no | no | 75 | None |  | None | None | None | None | 50.0 | 50.0 | 50.0 | 0.000000 | False | -14 |
| KXBTC15M-26MAY071100-00 | yes | no | 83 | 85 | mushroom_v28_exit_value_over_hold | 0.836750 | 0.850000 | -0.013250 | -0.675039 | 4.0 | -166.0 | -166.0 | -170.000000 | True | -166 |
| KXBTC15M-26MAY071115-15 | yes | yes | 84 | 91 | mushroom_v28_exit_value_over_hold | 0.888844 | 0.910000 | -0.021156 | -4.884431 | 14.0 | 32.0 | 32.0 | 18.000000 | True | -112 |
| KXBTC15M-26MAY071130-30 | no | no | 85 | None |  | None | None | None | None | 30.0 | 30.0 | 30.0 | 0.000000 | False | None |
| KXBTC15M-26MAY071145-45 | yes | yes | 77 | 99 | mushroom_v28_exit_value_over_hold | 0.982146 | 0.990000 | -0.007854 | -17.214598 | 44.0 | 46.0 | 46.0 | 2.000000 | True | 44 |
| KXBTC15M-26MAY071200-00 | no | no | 77 | 98 | mushroom_v28_exit_value_over_hold | 0.961165 | 0.980000 | -0.018835 | -19.116535 | 42.0 | 46.0 | 46.0 | 4.000000 | True | 42 |
| KXBTC15M-26MAY071215-15 | no | no | 84 | 76 | mushroom_v28_probability_reduce | 0.797661 | 0.760000 | 0.037661 | 4.233856 | -16.0 | 32.0 | 32.0 | 48.000000 | True | -28 |
| KXBTC15M-26MAY071215-15 | no | no | 78 | 79 | mushroom_v28_exit_value_over_hold | 0.752304 | 0.790000 | -0.037696 | 2.769646 | 2.0 | 44.0 | 44.0 | 42.000000 | True | -28 |
| KXBTC15M-26MAY071215-15 | no | no | 80 | 76 | mushroom_v28_probability_reduce | 0.765822 | 0.760000 | 0.005822 | 3.417815 | -8.0 | 40.0 | 40.0 | 48.000000 | True | -28 |
| KXBTC15M-26MAY071230-30 | yes | yes | 77 | 72 | mushroom_v28_probability_reduce | 0.749378 | 0.720000 | 0.029378 | 2.062161 | -10.0 | 46.0 | -10.0 | 0.000000 | False | -34 |
| KXBTC15M-26MAY071230-30 | yes | yes | 84 | 65 | mushroom_v28_probability_collapse_full | 0.662903 | 0.660000 | 0.002903 | 17.709724 | -38.0 | 32.0 | -38.0 | 0.000000 | False | -34 |
| KXBTC15M-26MAY071230-30 | yes | yes | 80 | None |  | None | None | None | None | 40.0 | 40.0 | 40.0 | 0.000000 | False | -34 |
| KXBTC15M-26MAY071315-15 | yes | yes | 80 | 77 | mushroom_v28_probability_reduce | 0.798341 | 0.770000 | 0.028341 | -0.834147 | -6.0 | 40.0 | 40.0 | 46.000000 | True | 28 |
| KXBTC15M-26MAY071315-15 | yes | yes | 81 | 74 | mushroom_v28_probability_reduce | 0.784166 | 0.740000 | 0.044166 | 2.583397 | -14.0 | 38.0 | 38.0 | 52.000000 | True | 28 |
| KXBTC15M-26MAY071315-15 | yes | yes | 78 | 94 | mushroom_v28_exit_value_over_hold | 0.927498 | 0.940000 | -0.012502 | -14.749774 | 32.0 | 44.0 | 44.0 | 12.000000 | True | 28 |
