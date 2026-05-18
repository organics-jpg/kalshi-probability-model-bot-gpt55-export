# v28 Exit Book-Gap Candidates

Research-only exit diagnostics using p_hold minus executable exit bid.

## Current Read

- Best book-gap exit policy is hold_to_settlement_control with gross 2304.0c and delta 1481.0c vs current.
- Current v28 exit gross is 823.0c over 173 trades.
- This is diagnostic only; forward promotion needs a frozen validator with future rows.

## Summary

| policy | trades | W/L | gross c | delta c | suppressed | suppressed collapse | worst mark c | winner clip c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `hold_to_settlement_control` | 173 | 146/27 | 2304.000000 | 1481.000000 | 142 | 26 | -172.000000 | -4659.000000 |
| `suppress_soft_gap15_or_p_hold75` | 173 | 115/58 | 1396.000000 | 573.000000 | 86 | 0 | -172.000000 | -4659.000000 |
| `suppress_soft_exit_hold_book_gap_ge_10pp` | 173 | 100/73 | 837.000000 | 14.000000 | 3 | 0 | -152.000000 | -4659.000000 |
| `current_v28_exit` | 173 | 98/75 | 823.000000 | 0.000000 | 0 | 0 | -134.000000 | -4659.000000 |
| `suppress_soft_exit_hold_book_gap_ge_20pp` | 173 | 98/75 | 823.000000 | 0.000000 | 0 | 0 | -134.000000 | -4659.000000 |
| `suppress_soft_gap15_drawdown_lte5` | 173 | 98/75 | 823.000000 | 0.000000 | 0 | 0 | -134.000000 | -4659.000000 |
| `suppress_soft_exit_hold_book_gap_ge_15pp` | 173 | 98/75 | 703.000000 | -120.000000 | 1 | 0 | -152.000000 | -4659.000000 |
| `suppress_reduce_gap15_keep_collapse` | 173 | 98/75 | 703.000000 | -120.000000 | 1 | 0 | -152.000000 | -4659.000000 |

## Rows

| market | side | result | reason | current | hold | p_hold | bid | gap | drawdown |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY051300-00` | yes | yes | `mushroom_v28_exit_value_over_hold` | 36.000000 | 38.000000 | 0.980404 | 0.990000 | -0.009596 | -17.040444 |
| `KXBTC15M-26MAY051330-30` | yes | yes | `mushroom_v28_exit_value_over_hold` | 0.000000 | 36.000000 | 0.784419 | 0.820000 | -0.035581 | 3.558143 |
| `KXBTC15M-26MAY051545-45` | yes | yes | `mushroom_v28_exit_value_over_hold` | 16.000000 | 50.000000 | 0.811651 | 0.830000 | -0.018349 | -6.165133 |
| `KXBTC15M-26MAY051615-15` | no | yes | `mushroom_v28_probability_collapse_full` | -24.000000 | -152.000000 | 0.698446 | 0.640000 | 0.058446 | 6.155389 |
| `KXBTC15M-26MAY051615-15` | yes | yes | `mushroom_v28_probability_reduce` | 32.000000 | 88.000000 | 0.784724 | 0.720000 | 0.064724 | -22.472420 |
| `KXBTC15M-26MAY051715-15` | yes | no | `mushroom_v28_probability_reduce` | -28.000000 | -164.000000 | 0.728020 | 0.680000 | 0.048020 | 9.198017 |
| `KXBTC15M-26MAY051715-15` | yes | no | `mushroom_v28_probability_collapse_full` | -48.000000 | -138.000000 | 0.552818 | 0.450000 | 0.102818 | 13.718206 |
| `KXBTC15M-26MAY051715-15` | yes | no | `mushroom_v28_probability_collapse_full` | -22.000000 | -80.000000 | 0.351830 | 0.290000 | 0.061830 | 4.816989 |
| `KXBTC15M-26MAY051745-45` | no | no | `mushroom_v28_probability_reduce` | -10.000000 | 46.000000 | 0.791105 | 0.720000 | 0.071105 | -2.110550 |
| `KXBTC15M-26MAY051745-45` | no | no | `mushroom_v28_exit_value_over_hold` | -2.000000 | 40.000000 | 0.754469 | 0.790000 | -0.035531 | 9.553119 |
| `KXBTC15M-26MAY051800-00` | yes | yes | `mushroom_v28_probability_reduce` | -24.000000 | 44.000000 | 0.729502 | 0.660000 | 0.069502 | 5.049756 |
| `KXBTC15M-26MAY051800-00` | yes | yes | `mushroom_v28_exit_value_over_hold` | 40.000000 | 40.000000 | 0.991914 | 1.000000 | -0.008086 | -19.191381 |
| `KXBTC15M-26MAY051815-15` | yes | no | `mushroom_v28_exit_value_over_hold` | 24.000000 | -162.000000 | 0.922242 | 0.930000 | -0.007758 | -9.224209 |
| `KXBTC15M-26MAY051830-30` | no | yes | `mushroom_v28_probability_collapse_full` | -92.000000 | -160.000000 | 0.453866 | 0.340000 | 0.113866 | 34.613447 |
| `KXBTC15M-26MAY051845-45` | no | no | `` | 42.000000 | 42.000000 | None | None | None | None |
| `KXBTC15M-26MAY051900-00` | yes | yes | `` | 40.000000 | 40.000000 | None | None | None | None |
| `KXBTC15M-26MAY051915-15` | yes | yes | `mushroom_v28_exit_value_over_hold` | 34.000000 | 36.000000 | 0.968105 | 0.990000 | -0.021895 | -14.810535 |
| `KXBTC15M-26MAY051945-45` | yes | yes | `mushroom_v28_exit_value_over_hold` | 26.000000 | 52.000000 | 0.837318 | 0.870000 | -0.032682 | -9.731795 |
| `KXBTC15M-26MAY052015-15` | yes | yes | `` | 30.000000 | 30.000000 | None | None | None | None |
| `KXBTC15M-26MAY052045-45` | yes | no | `mushroom_v28_exit_value_over_hold` | -18.000000 | -158.000000 | 0.650910 | 0.700000 | -0.049090 | 15.909026 |
| `KXBTC15M-26MAY052045-45` | yes | no | `mushroom_v28_exit_value_over_hold` | 14.000000 | -166.000000 | 0.840700 | 0.900000 | -0.059300 | -1.070049 |
| `KXBTC15M-26MAY052100-00` | no | yes | `mushroom_v28_probability_collapse_full` | -30.000000 | -158.000000 | 0.709559 | 0.640000 | 0.069559 | 8.044127 |
| `KXBTC15M-26MAY052100-00` | yes | yes | `mushroom_v28_exit_value_over_hold` | 34.000000 | 88.000000 | 0.551181 | 0.730000 | -0.178819 | 0.881937 |
| `KXBTC15M-26MAY052100-00` | yes | yes | `mushroom_v28_exit_value_over_hold` | 12.000000 | 20.000000 | 0.948823 | 0.960000 | -0.011177 | -4.882288 |
| `KXBTC15M-26MAY052115-15` | yes | yes | `` | 44.000000 | 44.000000 | None | None | None | None |
| `KXBTC15M-26MAY052145-45` | yes | yes | `mushroom_v28_exit_value_over_hold` | 20.000000 | 30.000000 | 0.901383 | 0.950000 | -0.048617 | -7.138269 |
| `KXBTC15M-26MAY052200-00` | yes | yes | `mushroom_v28_exit_value_over_hold` | 12.000000 | 42.000000 | 0.827933 | 0.850000 | -0.022067 | -3.793285 |
| `KXBTC15M-26MAY052215-15` | no | no | `mushroom_v28_exit_value_over_hold` | -14.000000 | 34.000000 | 0.710513 | 0.760000 | -0.049487 | 11.948693 |
| `KXBTC15M-26MAY052245-45` | no | yes | `mushroom_v28_probability_collapse_full` | -26.000000 | -80.000000 | 0.430723 | 0.270000 | 0.160723 | -3.072314 |
| `KXBTC15M-26MAY052300-00` | yes | yes | `mushroom_v28_exit_value_over_hold` | 28.000000 | 30.000000 | 0.819882 | 0.990000 | -0.170118 | 3.011763 |
| `KXBTC15M-26MAY052315-15` | yes | yes | `mushroom_v28_probability_collapse_full` | -38.000000 | 38.000000 | 0.676259 | 0.620000 | 0.056259 | 13.374120 |
| `KXBTC15M-26MAY060045-45` | no | no | `mushroom_v28_probability_reduce` | -10.000000 | 42.000000 | 0.794727 | 0.740000 | 0.054727 | -0.472669 |
| `KXBTC15M-26MAY060045-45` | no | no | `mushroom_v28_exit_value_over_hold` | 20.000000 | 30.000000 | 0.939879 | 0.950000 | -0.010121 | -8.987878 |
| `KXBTC15M-26MAY060100-00` | no | no | `mushroom_v28_probability_reduce` | -4.000000 | 44.000000 | 0.794947 | 0.760000 | 0.034947 | -1.494734 |
| `KXBTC15M-26MAY060145-45` | no | no | `mushroom_v28_exit_value_over_hold` | 22.000000 | 24.000000 | 0.981135 | 0.990000 | -0.008865 | -10.113544 |
| `KXBTC15M-26MAY060200-00` | yes | yes | `mushroom_v28_probability_reduce` | -12.000000 | 40.000000 | 0.773728 | 0.740000 | 0.033728 | 2.627248 |
| `KXBTC15M-26MAY060200-00` | yes | yes | `mushroom_v28_exit_value_over_hold` | 6.000000 | 38.000000 | 0.826858 | 0.840000 | -0.013142 | -0.685826 |
| `KXBTC15M-26MAY060215-15` | yes | no | `mushroom_v28_probability_collapse_full` | -16.000000 | -154.000000 | 0.716457 | 0.690000 | 0.026457 | 5.354325 |
| `KXBTC15M-26MAY060215-15` | yes | no | `mushroom_v28_probability_reduce` | -26.000000 | -166.000000 | 0.744634 | 0.700000 | 0.044634 | 8.536580 |
| `KXBTC15M-26MAY060215-15` | no | no | `mushroom_v28_exit_value_over_hold` | 34.000000 | 40.000000 | 0.943338 | 0.970000 | -0.026662 | -14.333771 |
| `KXBTC15M-26MAY060230-30` | yes | yes | `mushroom_v28_probability_reduce` | -20.000000 | 32.000000 | 0.742942 | 0.740000 | 0.002942 | 9.705807 |
| `KXBTC15M-26MAY060245-45` | yes | yes | `mushroom_v28_probability_reduce` | -8.000000 | 40.000000 | 0.793334 | 0.760000 | 0.033334 | 2.666578 |
| `KXBTC15M-26MAY060245-45` | yes | yes | `mushroom_v28_probability_reduce` | -6.000000 | 46.000000 | 0.749392 | 0.740000 | 0.009392 | 2.060750 |
| `KXBTC15M-26MAY060245-45` | yes | yes | `mushroom_v28_exit_value_over_hold` | 38.000000 | 48.000000 | 0.941979 | 0.950000 | -0.008021 | -18.197939 |
| `KXBTC15M-26MAY060300-00` | yes | yes | `mushroom_v28_probability_reduce` | -14.000000 | 38.000000 | 0.780402 | 0.740000 | 0.040402 | 2.959820 |
| `KXBTC15M-26MAY060300-00` | yes | yes | `mushroom_v28_probability_collapse_full` | -30.000000 | 38.000000 | 0.718799 | 0.660000 | 0.058799 | 9.120058 |
| `KXBTC15M-26MAY060300-00` | yes | yes | `mushroom_v28_probability_reduce` | -22.000000 | 40.000000 | 0.753164 | 0.690000 | 0.063164 | 4.683642 |
| `KXBTC15M-26MAY060300-00` | yes | yes | `mushroom_v28_exit_value_over_hold` | 28.000000 | 40.000000 | 0.931555 | 0.940000 | -0.008445 | -13.155529 |
| `KXBTC15M-26MAY060315-15` | yes | yes | `mushroom_v28_exit_value_over_hold` | 26.000000 | 28.000000 | 0.975084 | 0.990000 | -0.014916 | -11.508394 |
| `KXBTC15M-26MAY060330-30` | yes | yes | `mushroom_v28_exit_value_over_hold` | -52.000000 | 42.000000 | 0.500862 | 0.530000 | -0.029138 | 28.913827 |
| `KXBTC15M-26MAY060330-30` | no | yes | `` | -18.000000 | -18.000000 | None | None | None | None |
| `KXBTC15M-26MAY060345-45` | no | no | `mushroom_v28_exit_value_over_hold` | 34.000000 | 44.000000 | 0.940325 | 0.950000 | -0.009675 | -16.032531 |
| `KXBTC15M-26MAY060445-45` | yes | yes | `mushroom_v28_exit_value_over_hold` | 18.000000 | 20.000000 | 0.980285 | 0.990000 | -0.009715 | -8.028473 |
| `KXBTC15M-26MAY060500-00` | yes | yes | `` | 42.000000 | 42.000000 | None | None | None | None |
| `KXBTC15M-26MAY060515-15` | no | no | `mushroom_v28_probability_collapse_full` | -26.000000 | 42.000000 | 0.669735 | 0.660000 | 0.009735 | 16.026514 |
| `KXBTC15M-26MAY060515-15` | no | no | `mushroom_v28_exit_value_over_hold` | 42.000000 | 52.000000 | 0.769032 | 0.950000 | -0.180968 | -2.903190 |
| `KXBTC15M-26MAY060530-30` | no | no | `mushroom_v28_exit_value_over_hold` | 34.000000 | 44.000000 | 0.899953 | 0.950000 | -0.050047 | -11.995311 |
| `KXBTC15M-26MAY060545-45` | yes | yes | `` | 20.000000 | 20.000000 | None | None | None | None |
| `KXBTC15M-26MAY060600-00` | no | no | `mushroom_v28_exit_value_over_hold` | 12.000000 | 50.000000 | 0.804105 | 0.820000 | -0.015895 | 1.589476 |
| `KXBTC15M-26MAY060615-15` | yes | yes | `mushroom_v28_probability_collapse_full` | -30.000000 | 50.000000 | 0.643484 | 0.600000 | 0.043484 | 10.651569 |
| `KXBTC15M-26MAY060615-15` | yes | yes | `` | 24.000000 | 24.000000 | None | None | None | None |
| `KXBTC15M-26MAY060630-30` | yes | yes | `mushroom_v28_probability_reduce` | -12.000000 | 42.000000 | 0.777774 | 0.730000 | 0.047774 | 1.222639 |
| `KXBTC15M-26MAY060630-30` | yes | yes | `mushroom_v28_exit_value_over_hold` | 28.000000 | 30.000000 | 0.978151 | 0.990000 | -0.011849 | -12.815129 |
| `KXBTC15M-26MAY060645-45` | yes | yes | `mushroom_v28_probability_reduce` | -16.000000 | 36.000000 | 0.799349 | 0.740000 | 0.059349 | 2.065125 |
| `KXBTC15M-26MAY060645-45` | yes | yes | `mushroom_v28_probability_reduce` | -12.000000 | 44.000000 | 0.779789 | 0.720000 | 0.059789 | 0.021114 |
| `KXBTC15M-26MAY060645-45` | yes | yes | `mushroom_v28_exit_value_over_hold` | 34.000000 | 40.000000 | 0.962354 | 0.970000 | -0.007646 | -16.235382 |
| `KXBTC15M-26MAY060700-00` | no | yes | `mushroom_v28_probability_reduce` | -8.000000 | -168.000000 | 0.799603 | 0.800000 | -0.000397 | 4.039746 |
| `KXBTC15M-26MAY060700-00` | yes | yes | `mushroom_v28_probability_reduce` | -22.000000 | 50.000000 | 0.748579 | 0.640000 | 0.108579 | 0.142079 |
| `KXBTC15M-26MAY060700-00` | yes | yes | `mushroom_v28_probability_collapse_full` | -30.000000 | 46.000000 | 0.674479 | 0.620000 | 0.054479 | 9.552131 |
| `KXBTC15M-26MAY060700-00` | yes | yes | `mushroom_v28_exit_value_over_hold` | 12.000000 | 34.000000 | 0.743339 | 0.890000 | -0.146661 | 8.666129 |
| `KXBTC15M-26MAY060715-15` | yes | yes | `mushroom_v28_exit_value_over_hold` | 24.000000 | 38.000000 | 0.920907 | 0.930000 | -0.009093 | -11.090690 |
| `KXBTC15M-26MAY060715-15` | yes | yes | `mushroom_v28_exit_value_over_hold` | 20.000000 | 22.000000 | 0.984061 | 0.990000 | -0.005939 | -8.406103 |
| `KXBTC15M-26MAY060730-30` | yes | yes | `` | 32.000000 | 32.000000 | None | None | None | None |
| `KXBTC15M-26MAY060745-45` | yes | no | `mushroom_v28_probability_collapse_full` | -24.000000 | -138.000000 | 0.610349 | 0.570000 | 0.040349 | 7.965096 |
| `KXBTC15M-26MAY060745-45` | yes | no | `mushroom_v28_probability_collapse_full` | -70.000000 | -156.000000 | 0.563569 | 0.430000 | 0.133569 | 21.643115 |
| `KXBTC15M-26MAY060800-00` | yes | yes | `mushroom_v28_probability_reduce` | -18.000000 | 42.000000 | 0.738185 | 0.700000 | 0.038185 | 5.181496 |
| `KXBTC15M-26MAY060800-00` | yes | yes | `mushroom_v28_probability_collapse_full` | -32.000000 | 68.000000 | 0.614703 | 0.500000 | 0.114703 | 4.529724 |
| `KXBTC15M-26MAY060815-15` | no | no | `` | 42.000000 | 42.000000 | None | None | None | None |
| `KXBTC15M-26MAY060830-30` | yes | yes | `mushroom_v28_exit_value_over_hold` | 48.000000 | 48.000000 | 0.992185 | 1.000000 | -0.007815 | -23.218487 |
| `KXBTC15M-26MAY060900-00` | yes | no | `mushroom_v28_probability_reduce` | -10.000000 | -156.000000 | 0.789990 | 0.730000 | 0.059990 | -0.998969 |
| `KXBTC15M-26MAY060900-00` | yes | no | `mushroom_v28_probability_collapse_full` | -76.000000 | -156.000000 | 0.397320 | 0.400000 | -0.002680 | 41.268037 |
| `KXBTC15M-26MAY060900-00` | no | no | `mushroom_v28_probability_reduce` | -16.000000 | 54.000000 | 0.721102 | 0.650000 | 0.071102 | 0.889760 |
| `KXBTC15M-26MAY060900-00` | no | no | `mushroom_v28_exit_value_over_hold` | 34.000000 | 42.000000 | 0.948348 | 0.960000 | -0.011652 | -15.834839 |
| `KXBTC15M-26MAY060915-15` | no | no | `mushroom_v28_probability_reduce` | 0.000000 | 60.000000 | 0.793762 | 0.700000 | 0.093762 | -9.376204 |
| `KXBTC15M-26MAY060915-15` | no | no | `mushroom_v28_exit_value_over_hold` | 50.000000 | 50.000000 | 0.994245 | 1.000000 | -0.005755 | -17.424453 |
| `KXBTC15M-26MAY060930-30` | no | no | `mushroom_v28_probability_reduce` | -20.000000 | 48.000000 | 0.725946 | 0.660000 | 0.065946 | 3.405368 |
| `KXBTC15M-26MAY060930-30` | no | no | `mushroom_v28_probability_reduce` | -14.000000 | 48.000000 | 0.787606 | 0.680000 | 0.107606 | -2.760587 |
| `KXBTC15M-26MAY060930-30` | no | no | `mushroom_v28_probability_reduce` | -3.000000 | 54.000000 | 0.799180 | 0.710000 | 0.089180 | -6.917970 |
| `KXBTC15M-26MAY060930-30` | no | no | `` | 46.000000 | 46.000000 | None | None | None | None |
| `KXBTC15M-26MAY060945-45` | no | no | `mushroom_v28_probability_collapse_full` | -16.000000 | 82.000000 | 0.556556 | 0.510000 | 0.046556 | 3.344394 |
| `KXBTC15M-26MAY060945-45` | no | no | `mushroom_v28_probability_collapse_full` | -16.000000 | 60.000000 | 0.689159 | 0.620000 | 0.069159 | 1.084126 |
| `KXBTC15M-26MAY060945-45` | no | no | `mushroom_v28_probability_reduce` | -12.000000 | 58.000000 | 0.735773 | 0.650000 | 0.085773 | -2.577325 |
| `KXBTC15M-26MAY060945-45` | no | no | `mushroom_v28_exit_value_over_hold` | 48.000000 | 56.000000 | 0.950787 | 0.960000 | -0.009213 | -23.078686 |
| `KXBTC15M-26MAY061000-00` | no | no | `` | 70.000000 | 70.000000 | None | None | None | None |
| `KXBTC15M-26MAY061015-15` | no | no | `mushroom_v28_probability_reduce` | -6.000000 | 64.000000 | 0.733426 | 0.650000 | 0.083426 | -5.342610 |
| `KXBTC15M-26MAY061015-15` | no | no | `mushroom_v28_probability_reduce` | 0.000000 | 60.000000 | 0.799979 | 0.700000 | 0.099979 | -9.997858 |
| `KXBTC15M-26MAY061015-15` | no | no | `` | 54.000000 | 54.000000 | None | None | None | None |
| `KXBTC15M-26MAY061030-30` | yes | yes | `mushroom_v28_probability_reduce` | -16.000000 | 44.000000 | 0.752739 | 0.700000 | 0.052739 | 2.726149 |
| `KXBTC15M-26MAY061030-30` | yes | yes | `mushroom_v28_probability_reduce` | -10.000000 | 44.000000 | 0.796458 | 0.730000 | 0.066458 | -1.645773 |
| `KXBTC15M-26MAY061030-30` | yes | yes | `` | 52.000000 | 52.000000 | None | None | None | None |
| `KXBTC15M-26MAY061045-45` | yes | yes | `mushroom_v28_probability_reduce` | -6.000000 | 40.000000 | 0.796949 | 0.770000 | 0.026949 | 0.305083 |
| `KXBTC15M-26MAY061045-45` | yes | yes | `mushroom_v28_exit_value_over_hold` | 28.000000 | 32.000000 | 0.975987 | 0.990000 | -0.014013 | -13.598681 |
| `KXBTC15M-26MAY061100-00` | no | no | `mushroom_v28_probability_collapse_full` | -40.000000 | 34.000000 | 0.704126 | 0.630000 | 0.074126 | 12.587383 |
| `KXBTC15M-26MAY061100-00` | no | no | `` | 38.000000 | 38.000000 | None | None | None | None |
| `KXBTC15M-26MAY061130-30` | yes | yes | `` | 40.000000 | 40.000000 | None | None | None | None |
| `KXBTC15M-26MAY061200-00` | yes | yes | `mushroom_v28_exit_value_over_hold` | 16.000000 | 36.000000 | 0.889296 | 0.900000 | -0.010704 | -7.929607 |
| `KXBTC15M-26MAY061300-00` | yes | no | `mushroom_v28_probability_collapse_full` | -30.000000 | -160.000000 | 0.666430 | 0.650000 | 0.016430 | 13.356971 |
| `KXBTC15M-26MAY061400-00` | no | no | `mushroom_v28_exit_value_over_hold` | -10.000000 | 22.000000 | 0.737977 | 0.840000 | -0.102023 | 15.202342 |
| `KXBTC15M-26MAY061415-15` | no | no | `` | 24.000000 | 24.000000 | None | None | None | None |
| `KXBTC15M-26MAY061445-45` | no | no | `mushroom_v28_probability_reduce` | -22.000000 | 24.000000 | 0.797830 | 0.770000 | 0.027830 | 8.216985 |
| `KXBTC15M-26MAY061445-45` | no | no | `mushroom_v28_exit_value_over_hold` | 18.000000 | 20.000000 | 0.981991 | 0.990000 | -0.008009 | -8.199066 |
| `KXBTC15M-26MAY061545-45` | yes | yes | `mushroom_v28_exit_value_over_hold` | 22.000000 | 32.000000 | 0.935410 | 0.950000 | -0.014590 | -9.540987 |
| `KXBTC15M-26MAY061615-15` | yes | yes | `mushroom_v28_exit_value_over_hold` | 8.000000 | 20.000000 | 0.931218 | 0.940000 | -0.008782 | -3.121769 |
| `KXBTC15M-26MAY061645-45` | no | no | `` | 48.000000 | 48.000000 | None | None | None | None |
| `KXBTC15M-26MAY061800-00` | no | no | `mushroom_v28_probability_collapse_full` | -86.000000 | 66.000000 | 0.552607 | 0.240000 | 0.312607 | 11.739327 |
| `KXBTC15M-26MAY061815-15` | no | no | `mushroom_v28_exit_value_over_hold` | 24.000000 | 32.000000 | 0.950684 | 0.960000 | -0.009316 | -11.068394 |
| `KXBTC15M-26MAY061830-30` | no | no | `mushroom_v28_exit_value_over_hold` | 20.000000 | 22.000000 | 0.976718 | 0.990000 | -0.013282 | -8.671753 |
| `KXBTC15M-26MAY061900-00` | yes | yes | `` | 20.000000 | 20.000000 | None | None | None | None |
| `KXBTC15M-26MAY061915-15` | no | no | `mushroom_v28_exit_value_over_hold` | 24.000000 | 26.000000 | 0.981987 | 0.990000 | -0.008013 | -11.198704 |
| `KXBTC15M-26MAY062015-15` | no | no | `mushroom_v28_probability_collapse_full` | -60.000000 | 116.000000 | 0.268932 | 0.120000 | 0.148932 | 15.106811 |
| `KXBTC15M-26MAY062015-15` | yes | no | `mushroom_v28_exit_value_over_hold` | 8.000000 | -172.000000 | 0.812359 | 0.900000 | -0.087641 | 4.764109 |
| `KXBTC15M-26MAY062015-15` | yes | no | `` | -134.000000 | -134.000000 | None | None | None | None |
| `KXBTC15M-26MAY062030-30` | no | no | `mushroom_v28_exit_value_over_hold` | 32.000000 | 66.000000 | 0.661475 | 0.830000 | -0.168525 | 0.852486 |
| `KXBTC15M-26MAY062045-45` | no | no | `mushroom_v28_exit_value_over_hold` | 24.000000 | 40.000000 | 0.891386 | 0.920000 | -0.028614 | -9.138584 |
| `KXBTC15M-26MAY062100-00` | yes | yes | `mushroom_v28_exit_value_over_hold` | -4.000000 | 34.000000 | 0.647591 | 0.810000 | -0.162409 | 18.240924 |
| `KXBTC15M-26MAY062100-00` | yes | yes | `mushroom_v28_exit_value_over_hold` | -20.000000 | 32.000000 | 0.663692 | 0.740000 | -0.076308 | 17.630840 |
| `KXBTC15M-26MAY062100-00` | yes | yes | `mushroom_v28_exit_value_over_hold` | 14.000000 | 78.000000 | 0.489234 | 0.680000 | -0.190766 | 12.076646 |
| `KXBTC15M-26MAY062115-15` | yes | yes | `mushroom_v28_exit_value_over_hold` | -12.000000 | 54.000000 | 0.395750 | 0.670000 | -0.274250 | 33.425046 |
| `KXBTC15M-26MAY062115-15` | no | yes | `mushroom_v28_exit_value_over_hold` | -34.000000 | -138.000000 | 0.455777 | 0.520000 | -0.064223 | 14.422271 |
| `KXBTC15M-26MAY062115-15` | yes | yes | `mushroom_v28_exit_value_over_hold` | 22.000000 | 24.000000 | 0.982461 | 0.990000 | -0.007539 | -10.246054 |
| `KXBTC15M-26MAY062130-30` | no | yes | `mushroom_v28_probability_reduce` | -32.000000 | -152.000000 | 0.768407 | 0.600000 | 0.168407 | 6.159273 |
| `KXBTC15M-26MAY062215-15` | no | no | `mushroom_v28_probability_collapse_full` | 14.000000 | 70.000000 | 0.708248 | 0.720000 | -0.011752 | -5.824841 |
| `KXBTC15M-26MAY062215-15` | no | no | `mushroom_v28_exit_value_over_hold` | 10.000000 | 32.000000 | 0.860673 | 0.890000 | -0.029327 | -2.067333 |
| `KXBTC15M-26MAY062245-45` | yes | yes | `mushroom_v28_exit_value_over_hold` | 8.000000 | 28.000000 | 0.643812 | 0.900000 | -0.256188 | 15.618779 |
| `KXBTC15M-26MAY062300-00` | yes | yes | `mushroom_v28_exit_value_over_hold` | 16.000000 | 26.000000 | 0.746374 | 0.950000 | -0.203626 | 10.362646 |
| `KXBTC15M-26MAY062315-15` | no | no | `mushroom_v28_exit_value_over_hold` | 6.000000 | 32.000000 | 0.811182 | 0.870000 | -0.058818 | 2.881757 |
| `KXBTC15M-26MAY070000-00` | no | no | `mushroom_v28_exit_value_over_hold` | 2.000000 | 44.000000 | 0.726702 | 0.790000 | -0.063298 | 5.329808 |
| `KXBTC15M-26MAY070015-15` | no | yes | `mushroom_v28_exit_value_over_hold` | -2.000000 | -140.000000 | 0.596562 | 0.690000 | -0.093438 | 10.343815 |
| `KXBTC15M-26MAY070030-30` | yes | yes | `mushroom_v28_exit_value_over_hold` | 30.000000 | 36.000000 | 0.921778 | 0.970000 | -0.048222 | -10.177771 |
| `KXBTC15M-26MAY070115-15` | yes | yes | `mushroom_v28_exit_value_over_hold` | 0.000000 | 36.000000 | 0.679619 | 0.820000 | -0.140381 | 18.038087 |
| `KXBTC15M-26MAY070545-45` | no | no | `mushroom_v28_exit_value_over_hold` | 18.000000 | 36.000000 | 0.892567 | 0.910000 | -0.017433 | -7.256748 |
| `KXBTC15M-26MAY070645-45` | yes | yes | `` | 38.000000 | 38.000000 | None | None | None | None |
| `KXBTC15M-26MAY070745-45` | yes | yes | `mushroom_v28_exit_value_over_hold` | 34.000000 | 64.000000 | 0.821701 | 0.850000 | -0.028299 | -14.170103 |
| `KXBTC15M-26MAY070815-15` | yes | yes | `mushroom_v28_exit_value_over_hold` | 2.000000 | 20.000000 | 0.890464 | 0.910000 | -0.019536 | -1.046434 |
| `KXBTC15M-26MAY070830-30` | no | no | `mushroom_v28_exit_value_over_hold` | 18.000000 | 36.000000 | 0.825354 | 0.910000 | -0.084646 | -0.535395 |
| `KXBTC15M-26MAY070830-30` | no | no | `mushroom_v28_exit_value_over_hold` | -14.000000 | 46.000000 | 0.612998 | 0.700000 | -0.087002 | 15.700151 |
| `KXBTC15M-26MAY070830-30` | no | no | `` | 46.000000 | 46.000000 | None | None | None | None |
| `KXBTC15M-26MAY070915-15` | no | no | `` | 46.000000 | 46.000000 | None | None | None | None |
| `KXBTC15M-26MAY070930-30` | yes | yes | `mushroom_v28_exit_value_over_hold` | 34.000000 | 40.000000 | 0.969995 | 0.980000 | -0.010005 | -13.999536 |
| `KXBTC15M-26MAY070945-45` | no | no | `` | 62.000000 | 62.000000 | None | None | None | None |
| `KXBTC15M-26MAY071000-00` | no | no | `mushroom_v28_probability_collapse_full` | -36.000000 | 54.000000 | 0.617577 | 0.550000 | 0.067577 | 11.242300 |
| `KXBTC15M-26MAY071000-00` | no | no | `mushroom_v28_probability_reduce` | 16.000000 | 58.000000 | 0.781361 | 0.790000 | -0.008639 | 6.863933 |
| `KXBTC15M-26MAY071015-15` | no | yes | `mushroom_v28_probability_reduce` | 2.000000 | -156.000000 | 0.789130 | 0.790000 | -0.000870 | -0.913001 |
| `KXBTC15M-26MAY071015-15` | no | yes | `mushroom_v28_probability_reduce` | -16.000000 | -162.000000 | 0.763980 | 0.730000 | 0.033980 | 4.602013 |
| `KXBTC15M-26MAY071015-15` | yes | yes | `mushroom_v28_exit_value_over_hold` | 20.000000 | 32.000000 | 0.923102 | 0.940000 | -0.016898 | -8.310249 |
| `KXBTC15M-26MAY071030-30` | no | no | `mushroom_v28_probability_collapse_full` | -24.000000 | 46.000000 | 0.709831 | 0.650000 | 0.059831 | 6.016933 |
| `KXBTC15M-26MAY071030-30` | no | no | `` | 48.000000 | 48.000000 | None | None | None | None |
| `KXBTC15M-26MAY071045-45` | no | no | `mushroom_v28_probability_reduce` | -10.000000 | 52.000000 | 0.760529 | 0.690000 | 0.070529 | -2.052947 |
| `KXBTC15M-26MAY071045-45` | no | no | `` | 50.000000 | 50.000000 | None | None | None | None |
| `KXBTC15M-26MAY071100-00` | yes | no | `mushroom_v28_exit_value_over_hold` | 4.000000 | -166.000000 | 0.836750 | 0.850000 | -0.013250 | -0.675039 |
| `KXBTC15M-26MAY071115-15` | yes | yes | `mushroom_v28_exit_value_over_hold` | 14.000000 | 32.000000 | 0.888844 | 0.910000 | -0.021156 | -4.884431 |
| `KXBTC15M-26MAY071130-30` | no | no | `` | 30.000000 | 30.000000 | None | None | None | None |
| `KXBTC15M-26MAY071145-45` | yes | yes | `mushroom_v28_exit_value_over_hold` | 44.000000 | 46.000000 | 0.982146 | 0.990000 | -0.007854 | -17.214598 |
| `KXBTC15M-26MAY071200-00` | no | no | `mushroom_v28_exit_value_over_hold` | 42.000000 | 46.000000 | 0.961165 | 0.980000 | -0.018835 | -19.116535 |
| `KXBTC15M-26MAY071215-15` | no | no | `mushroom_v28_probability_reduce` | -16.000000 | 32.000000 | 0.797661 | 0.760000 | 0.037661 | 4.233856 |
| `KXBTC15M-26MAY071215-15` | no | no | `mushroom_v28_exit_value_over_hold` | 2.000000 | 44.000000 | 0.752304 | 0.790000 | -0.037696 | 2.769646 |
| `KXBTC15M-26MAY071215-15` | no | no | `mushroom_v28_probability_reduce` | -8.000000 | 40.000000 | 0.765822 | 0.760000 | 0.005822 | 3.417815 |
| `KXBTC15M-26MAY071230-30` | yes | yes | `mushroom_v28_probability_reduce` | -10.000000 | 46.000000 | 0.749378 | 0.720000 | 0.029378 | 2.062161 |
| `KXBTC15M-26MAY071230-30` | yes | yes | `mushroom_v28_probability_collapse_full` | -38.000000 | 32.000000 | 0.662903 | 0.660000 | 0.002903 | 17.709724 |
| `KXBTC15M-26MAY071230-30` | yes | yes | `` | 40.000000 | 40.000000 | None | None | None | None |
| `KXBTC15M-26MAY071315-15` | yes | yes | `mushroom_v28_probability_reduce` | -6.000000 | 40.000000 | 0.798341 | 0.770000 | 0.028341 | -0.834147 |
| `KXBTC15M-26MAY071315-15` | yes | yes | `mushroom_v28_probability_reduce` | -14.000000 | 38.000000 | 0.784166 | 0.740000 | 0.044166 | 2.583397 |
| `KXBTC15M-26MAY071315-15` | yes | yes | `mushroom_v28_exit_value_over_hold` | 32.000000 | 44.000000 | 0.927498 | 0.940000 | -0.012502 | -14.749774 |
