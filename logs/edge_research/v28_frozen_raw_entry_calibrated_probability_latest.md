# v28 Frozen Raw-Entry Calibrated Probability

Forward-only calibration validator. Entry selection is fixed at raw v28 p50 edge0; overlays only change the assigned probability.

- Freeze timestamp UTC: `2026-05-05T23:30:17.615882+00:00`
- Forward market denominator: `152`
- Future entry rows: `150`

| rank | overlay | entries | settled | coverage | brier | delta | logloss | delta | avg p | win rate | net c | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | book_probability | 150 | 150 | 98.684211 | 0.217809 | -0.012290 | 0.622464 | -0.022481 | 0.560733 | 0.553333 | -1009.000000 | coverage_too_high, bucket_brier_not_better_than_raw |
| 2 | noise_shrink_light_probability | 150 | 150 | 98.684211 | 0.227417 | -0.002682 | 0.639833 | -0.005112 | 0.608259 | 0.553333 | -1009.000000 | coverage_too_high, bucket_brier_not_better_than_raw |
| 3 | raw_probability | 150 | 150 | 98.684211 | 0.230099 | 0.000000 | 0.644945 | 0.000000 | 0.625408 | 0.553333 | -1009.000000 | coverage_too_high |
| 4 | entry_conditioned_logit125_p60_only_probability | 150 | 150 | 98.684211 | 0.233080 | 0.002981 | 0.649460 | 0.004515 | 0.644022 | 0.553333 | -1009.000000 | coverage_too_high, brier_not_better_than_raw, bucket_brier_not_better_than_raw |
| 5 | entry_conditioned_logit125_probability | 150 | 150 | 98.684211 | 0.233443 | 0.003344 | 0.650140 | 0.005195 | 0.649566 | 0.553333 | -1009.000000 | coverage_too_high, brier_not_better_than_raw, bucket_brier_not_better_than_raw |
| 6 | entry_conditioned_plus03_probability | 150 | 150 | 98.684211 | 0.235324 | 0.005224 | 0.654401 | 0.009456 | 0.655383 | 0.553333 | -1009.000000 | coverage_too_high, brier_not_better_than_raw, bucket_brier_not_better_than_raw |
| 7 | entry_conditioned_plus05_probability | 150 | 150 | 98.684211 | 0.239803 | 0.009704 | 0.663176 | 0.018232 | 0.675250 | 0.553333 | -1009.000000 | coverage_too_high, brier_not_better_than_raw, bucket_brier_not_better_than_raw |

## Bucket Stability

- `book_probability` failures: approved_entries:0.029919, lower_recross:0.027735, ask_gt_60:0.010450
- `noise_shrink_light_probability` failures: approved_entries:0.001969, lower_recross:0.001901, ask_gt_60:0.001233
- `entry_conditioned_logit125_p60_only_probability` failures: all:0.002981, early_markets:0.003905, late_markets:0.002057, shadow_rejected_actionable:0.003409, near_strike_abs_d_lte_025:0.000571, away_from_strike_abs_d_gt_025:0.005663, high_recross:0.003454, spectral_dominant_factor:0.003001, raw_p_60_plus:0.005884, ask_lte_60:0.005205
- `entry_conditioned_logit125_probability` failures: all:0.003344, early_markets:0.004715, late_markets:0.001972, shadow_rejected_actionable:0.003789, near_strike_abs_d_lte_025:0.001952, away_from_strike_abs_d_gt_025:0.004893, high_recross:0.003834, spectral_dominant_factor:0.003318, raw_p_50_60:0.000735, raw_p_60_plus:0.005884, ask_lte_60:0.005723
- `entry_conditioned_plus03_probability` failures: all:0.005224, early_markets:0.004262, late_markets:0.006186, shadow_rejected_actionable:0.005703, near_strike_abs_d_lte_025:0.005819, away_from_strike_abs_d_gt_025:0.004563, high_recross:0.005727, spectral_dominant_factor:0.005041, raw_p_50_60:0.004457, raw_p_60_plus:0.005972, ask_lte_60:0.008305
- `entry_conditioned_plus05_probability` failures: all:0.009704, early_markets:0.008097, late_markets:0.011311, shadow_rejected_actionable:0.010505, near_strike_abs_d_lte_025:0.010698, away_from_strike_abs_d_gt_025:0.008598, high_recross:0.010545, spectral_dominant_factor:0.009398, raw_p_50_60:0.008428, raw_p_60_plus:0.010946, ask_lte_60:0.014841

## Future Entry Rows

| market | ts | side | source | p_raw | ask | raw edge | stc | abs d | recross | spectral | won | net c |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|---:|
| KXBTC15M-26MAY051945-45 | 2026-05-05T23:33:23.957336+00:00 | yes | rejected_actionable | 0.613944 | 0.510000 | 0.103944 | 696.051000 | 0.208932 | 0.721016 | spectral_dominant_factor | True | 94.000000 |
| KXBTC15M-26MAY052000-00 | 2026-05-05T23:48:56.586770+00:00 | no | rejected_actionable | 0.665463 | 0.630000 | 0.035463 | 663.416000 | 0.377796 | 0.572707 | spectral_dominant_factor | True | 70.000000 |
| KXBTC15M-26MAY052015-15 | 2026-05-06T00:00:26.952847+00:00 | no | rejected_actionable | 0.567861 | 0.490000 | 0.077861 | 873.050000 | 0.150360 | 0.945709 | spectral_dominant_factor | False | -102.000000 |
| KXBTC15M-26MAY052030-30 | 2026-05-06T00:15:20.371177+00:00 | yes | rejected_actionable | 0.540780 | 0.470000 | 0.070780 | 879.629000 | 0.144729 | 1.053237 | spectral_dominant_factor | False | -98.000000 |
| KXBTC15M-26MAY052045-45 | 2026-05-06T00:32:06.202799+00:00 | yes | rejected_actionable | 0.590266 | 0.560000 | 0.030266 | 773.798000 | 0.161783 | 0.935562 | spectral_dominant_factor | False | -116.000000 |
| KXBTC15M-26MAY052100-00 | 2026-05-06T00:46:31.822373+00:00 | yes | rejected_actionable | 0.565554 | 0.460000 | 0.105554 | 808.178000 | 0.155800 | 0.915520 | spectral_dominant_factor | True | 104.000000 |
| KXBTC15M-26MAY052115-15 | 2026-05-06T01:00:49.489174+00:00 | yes | rejected_actionable | 0.571476 | 0.530000 | 0.041476 | 850.512000 | 0.195783 | 0.945077 | spectral_dominant_factor | True | 90.000000 |
| KXBTC15M-26MAY052130-30 | 2026-05-06T01:17:49.446399+00:00 | yes | rejected_actionable | 0.822836 | 0.800000 | 0.022836 | 730.554000 | 0.789781 | 0.444053 | spectral_dominant_factor | True | 37.000000 |
| KXBTC15M-26MAY052145-45 | 2026-05-06T01:35:20.258067+00:00 | yes | rejected_actionable | 0.865417 | 0.830000 | 0.035417 | 579.745000 | 0.941969 | 0.304141 | spectral_dominant_factor | True | 32.000000 |
| KXBTC15M-26MAY052200-00 | 2026-05-06T01:46:16.552084+00:00 | no | rejected_actionable | 0.551743 | 0.520000 | 0.031743 | 823.452000 | 0.104813 | 0.987800 | spectral_dominant_factor | False | -108.000000 |
| KXBTC15M-26MAY052215-15 | 2026-05-06T02:01:20.642847+00:00 | no | rejected_actionable | 0.809232 | 0.770000 | 0.039232 | 819.362000 | 0.740524 | 0.558639 | spectral_dominant_factor | True | 43.000000 |
| KXBTC15M-26MAY052230-30 | 2026-05-06T02:23:49.063251+00:00 | no | rejected_actionable | 0.730624 | 0.650000 | 0.080624 | 370.940000 | 0.529873 | 0.288008 | spectral_dominant_factor | True | 66.000000 |
| KXBTC15M-26MAY052245-45 | 2026-05-06T02:32:27.510357+00:00 | no | rejected_actionable | 0.643789 | 0.570000 | 0.073789 | 752.490000 | 0.362082 | 0.663374 | spectral_dominant_factor | False | -118.000000 |
| KXBTC15M-26MAY052300-00 | 2026-05-06T02:52:05.427121+00:00 | yes | approved_entry | 0.918967 | 0.850000 | 0.068967 | 474.591000 | 1.210157 | 0.179195 | spectral_dominant_factor | True | 26.000000 |
| KXBTC15M-26MAY052315-15 | 2026-05-06T03:07:10.446683+00:00 | yes | approved_entry | 0.884999 | 0.810000 | 0.074999 | 469.554000 | 1.030077 | 0.214824 | spectral_dominant_factor | True | -41.000000 |
| KXBTC15M-26MAY052330-30 | 2026-05-06T03:19:05.339511+00:00 | no | rejected_actionable | 0.659176 | 0.630000 | 0.029176 | 654.661000 | 0.369967 | 0.572942 | spectral_dominant_factor | False | -130.000000 |
| KXBTC15M-26MAY052345-45 | 2026-05-06T03:30:49.979573+00:00 | no | rejected_actionable | 0.636767 | 0.630000 | 0.006767 | 850.023000 | 0.275785 | 0.899454 | spectral_dominant_factor | True | 70.000000 |
| KXBTC15M-26MAY060000-00 | 2026-05-06T03:47:27.202014+00:00 | no | rejected_actionable | 0.576655 | 0.560000 | 0.016655 | 752.798000 | 0.185582 | 0.862070 | spectral_dominant_factor | False | -116.000000 |
| KXBTC15M-26MAY060015-15 | 2026-05-06T04:03:05.375534+00:00 | yes | rejected_actionable | 0.532782 | 0.520000 | 0.012782 | 714.625000 | 0.096972 | 0.830651 | spectral_dominant_factor | False | -108.000000 |
| KXBTC15M-26MAY060030-30 | 2026-05-06T04:15:46.967766+00:00 | yes | rejected_actionable | 0.617077 | 0.510000 | 0.107077 | 853.033000 | 0.270552 | 0.831869 | spectral_dominant_factor | False | -106.000000 |
| KXBTC15M-26MAY060045-45 | 2026-05-06T04:31:21.224300+00:00 | no | rejected_actionable | 0.826505 | 0.790000 | 0.036505 | 818.779000 | 0.802399 | 0.461756 | spectral_dominant_factor | True | 39.000000 |
| KXBTC15M-26MAY060100-00 | 2026-05-06T04:48:35.924287+00:00 | yes | rejected_actionable | 0.799928 | 0.790000 | 0.009928 | 684.076000 | 0.694496 | 0.407561 | spectral_dominant_factor | False | -161.000000 |
| KXBTC15M-26MAY060115-15 | 2026-05-06T05:00:35.389901+00:00 | no | rejected_actionable | 0.513971 | 0.510000 | 0.003971 | 864.611000 | 0.056582 | 1.023107 | spectral_dominant_factor | True | 94.000000 |
| KXBTC15M-26MAY060130-30 | 2026-05-06T05:15:50.243527+00:00 | no | rejected_actionable | 0.616779 | 0.590000 | 0.026779 | 849.758000 | 0.294972 | 0.777744 | spectral_dominant_factor | True | 78.000000 |
| KXBTC15M-26MAY060145-45 | 2026-05-06T05:30:30.771905+00:00 | no | rejected_actionable | 0.557282 | 0.550000 | 0.007282 | 869.229000 | 0.151652 | 0.849189 | spectral_dominant_factor | True | 86.000000 |
| KXBTC15M-26MAY060200-00 | 2026-05-06T05:45:50.623750+00:00 | yes | rejected_actionable | 0.618277 | 0.600000 | 0.018277 | 849.377000 | 0.248684 | 0.767680 | spectral_dominant_factor | True | 76.000000 |
| KXBTC15M-26MAY060215-15 | 2026-05-06T06:00:15.350074+00:00 | yes | rejected_actionable | 0.583024 | 0.530000 | 0.053024 | 884.651000 | 0.228362 | 0.792609 | spectral_dominant_factor | False | -110.000000 |
| KXBTC15M-26MAY060230-30 | 2026-05-06T06:15:15.506316+00:00 | no | rejected_actionable | 0.574094 | 0.540000 | 0.034094 | 884.495000 | 0.196217 | 0.789327 | spectral_dominant_factor | False | -112.000000 |
| KXBTC15M-26MAY060245-45 | 2026-05-06T06:30:31.260794+00:00 | no | rejected_actionable | 0.660829 | 0.650000 | 0.010829 | 868.740000 | 0.346255 | 0.663720 | spectral_dominant_factor | False | -134.000000 |
| KXBTC15M-26MAY060300-00 | 2026-05-06T06:45:30.608279+00:00 | yes | rejected_actionable | 0.661141 | 0.640000 | 0.021141 | 869.393000 | 0.396112 | 0.620295 | spectral_dominant_factor | True | 68.000000 |
| KXBTC15M-26MAY060315-15 | 2026-05-06T07:00:15.274913+00:00 | yes | rejected_actionable | 0.512365 | 0.500000 | 0.012365 | 884.725000 | 0.043908 | 0.857943 | spectral_dominant_factor | True | 96.000000 |
| KXBTC15M-26MAY060330-30 | 2026-05-06T07:15:15.855222+00:00 | no | rejected_actionable | 0.630880 | 0.570000 | 0.060880 | 884.146000 | 0.287388 | 0.689280 | spectral_dominant_factor | False | -118.000000 |
| KXBTC15M-26MAY060345-45 | 2026-05-06T07:30:31.159028+00:00 | yes | rejected_actionable | 0.515105 | 0.380000 | 0.135105 | 868.842000 | 0.064212 | 0.911219 | spectral_dominant_factor | False | -80.000000 |
| KXBTC15M-26MAY060400-00 | 2026-05-06T07:47:33.557061+00:00 | yes | rejected_actionable | 0.539723 | 0.500000 | 0.039723 | 746.444000 | 0.059013 | 0.811777 | spectral_dominant_factor | False | -104.000000 |
| KXBTC15M-26MAY060415-15 | 2026-05-06T08:01:47.044824+00:00 | yes | rejected_actionable | 0.676831 | 0.670000 | 0.006831 | 792.955000 | 0.394255 | 0.625830 | spectral_dominant_factor | True | 62.000000 |
| KXBTC15M-26MAY060445-45 | 2026-05-06T08:30:35.287901+00:00 | no | rejected_actionable | 0.636374 | 0.450000 | 0.186374 | 864.716000 | 0.322198 | 0.666569 | spectral_dominant_factor | False | -94.000000 |
| KXBTC15M-26MAY060500-00 | 2026-05-06T08:46:56.748188+00:00 | no | rejected_actionable | 0.674136 | 0.610000 | 0.064136 | 783.254000 | 0.377919 | 0.620318 | spectral_dominant_factor | False | -126.000000 |
| KXBTC15M-26MAY060515-15 | 2026-05-06T09:01:14.882023+00:00 | yes | rejected_actionable | 0.532512 | 0.410000 | 0.122512 | 825.119000 | 0.141500 | 0.958625 | spectral_dominant_factor | False | -86.000000 |
| KXBTC15M-26MAY060530-30 | 2026-05-06T09:16:10.984992+00:00 | yes | rejected_actionable | 0.588889 | 0.540000 | 0.048889 | 829.016000 | 0.202598 | 0.884715 | spectral_dominant_factor | False | -112.000000 |
| KXBTC15M-26MAY060545-45 | 2026-05-06T09:31:32.441205+00:00 | no | rejected_actionable | 0.626642 | 0.440000 | 0.186642 | 807.560000 | 0.323422 | 0.689053 | spectral_dominant_factor | False | -92.000000 |
| KXBTC15M-26MAY060600-00 | 2026-05-06T09:45:31.115998+00:00 | no | rejected_actionable | 0.792357 | 0.750000 | 0.042357 | 868.886000 | 0.672314 | 0.552274 | spectral_dominant_factor | True | 47.000000 |
| KXBTC15M-26MAY060615-15 | 2026-05-06T10:00:30.886997+00:00 | yes | rejected_actionable | 0.598388 | 0.570000 | 0.028388 | 869.113000 | 0.248560 | 0.915169 | spectral_dominant_factor | True | 41.000000 |
| KXBTC15M-26MAY060630-30 | 2026-05-06T10:15:31.073594+00:00 | no | rejected_actionable | 0.675344 | 0.660000 | 0.015344 | 868.927000 | 0.393798 | 0.762043 | spectral_dominant_factor | False | -136.000000 |
| KXBTC15M-26MAY060645-45 | 2026-05-06T10:30:15.796592+00:00 | yes | rejected_actionable | 0.598639 | 0.590000 | 0.008639 | 884.203000 | 0.277816 | 0.856108 | spectral_dominant_factor | True | 78.000000 |
| KXBTC15M-26MAY060700-00 | 2026-05-06T10:47:35.198854+00:00 | yes | rejected_actionable | 0.527819 | 0.520000 | 0.007819 | 744.801000 | 0.101470 | 0.876433 | spectral_dominant_factor | True | 92.000000 |
| KXBTC15M-26MAY060715-15 | 2026-05-06T11:00:15.472374+00:00 | yes | rejected_actionable | 0.501801 | 0.490000 | 0.011801 | 884.529000 | 0.033519 | 1.135459 | spectral_dominant_factor | True | 98.000000 |
| KXBTC15M-26MAY060730-30 | 2026-05-06T11:15:32.603129+00:00 | yes | rejected_actionable | 0.594884 | 0.560000 | 0.034884 | 867.397000 | 0.270357 | 0.863859 | spectral_dominant_factor | True | 84.000000 |
| KXBTC15M-26MAY060745-45 | 2026-05-06T11:30:52.002231+00:00 | no | rejected_actionable | 0.553279 | 0.540000 | 0.013279 | 848.000000 | 0.063119 | 1.217111 | spectral_dominant_factor | True | 88.000000 |
| KXBTC15M-26MAY060800-00 | 2026-05-06T11:45:15.871066+00:00 | yes | rejected_actionable | 0.523411 | 0.470000 | 0.053411 | 884.129000 | 0.027808 | 1.358871 | spectral_dominant_factor | True | 102.000000 |
| KXBTC15M-26MAY060815-15 | 2026-05-06T12:00:35.460368+00:00 | no | rejected_actionable | 0.505085 | 0.490000 | 0.015085 | 864.542000 | 0.002622 | 1.192913 | spectral_dominant_factor | True | 98.000000 |
| KXBTC15M-26MAY060830-30 | 2026-05-06T12:15:15.769157+00:00 | no | rejected_actionable | 0.600730 | 0.590000 | 0.010730 | 884.233000 | 0.286154 | 0.943700 | spectral_dominant_factor | False | -122.000000 |
| KXBTC15M-26MAY060845-45 | 2026-05-06T12:30:30.896182+00:00 | yes | rejected_actionable | 0.506183 | 0.500000 | 0.006183 | 869.104000 | 0.051184 | 1.244034 | spectral_dominant_factor | False | -104.000000 |
| KXBTC15M-26MAY060900-00 | 2026-05-06T12:46:30.862247+00:00 | no | rejected_actionable | 0.586412 | 0.580000 | 0.006412 | 809.138000 | 0.220177 | 0.886305 | spectral_dominant_factor | True | 80.000000 |
| KXBTC15M-26MAY060915-15 | 2026-05-06T13:00:30.368690+00:00 | no | rejected_actionable | 0.672099 | 0.600000 | 0.072099 | 869.636000 | 0.431641 | 0.831637 | spectral_dominant_factor | True | 76.000000 |
| KXBTC15M-26MAY060930-30 | 2026-05-06T13:15:35.659762+00:00 | yes | rejected_actionable | 0.604377 | 0.600000 | 0.004377 | 864.340000 | 0.244982 | 1.150583 | spectral_dominant_factor | False | -124.000000 |
| KXBTC15M-26MAY060945-45 | 2026-05-06T13:30:15.622325+00:00 | no | rejected_actionable | 0.761891 | 0.500000 | 0.261891 | 884.381000 | 0.648099 | 0.777721 | spectral_dominant_factor | True | 96.000000 |
| KXBTC15M-26MAY061000-00 | 2026-05-06T13:45:15.622703+00:00 | no | rejected_actionable | 0.513222 | 0.500000 | 0.013222 | 884.377000 | 0.051955 | 1.411643 | spectral_dominant_factor | True | 96.000000 |
| KXBTC15M-26MAY061015-15 | 2026-05-06T14:00:16.006684+00:00 | no | rejected_actionable | 0.595554 | 0.520000 | 0.075554 | 883.995000 | 0.274143 | 1.130150 | spectral_dominant_factor | True | 92.000000 |
| KXBTC15M-26MAY061030-30 | 2026-05-06T14:15:31.060926+00:00 | yes | rejected_actionable | 0.618153 | 0.610000 | 0.008153 | 868.942000 | 0.232373 | 1.168280 | spectral_dominant_factor | True | 74.000000 |
| KXBTC15M-26MAY061045-45 | 2026-05-06T14:30:31.159666+00:00 | no | rejected_actionable | 0.601767 | 0.570000 | 0.031767 | 868.842000 | 0.212683 | 1.191443 | spectral_dominant_factor | False | -118.000000 |
| KXBTC15M-26MAY061100-00 | 2026-05-06T14:45:34.678564+00:00 | yes | rejected_actionable | 0.740374 | 0.740000 | 0.000374 | 865.321000 | 0.597049 | 0.809587 | spectral_dominant_factor | False | -151.000000 |
| KXBTC15M-26MAY061115-15 | 2026-05-06T15:00:30.452254+00:00 | yes | rejected_actionable | 0.533622 | 0.520000 | 0.013622 | 869.548000 | 0.014701 | 1.452888 | spectral_dominant_factor | False | -108.000000 |
| KXBTC15M-26MAY061130-30 | 2026-05-06T15:15:16.911180+00:00 | yes | rejected_actionable | 0.653101 | 0.650000 | 0.003101 | 883.089000 | 0.341283 | 1.056221 | spectral_dominant_factor | True | 66.000000 |
| KXBTC15M-26MAY061145-45 | 2026-05-06T15:30:16.041511+00:00 | no | rejected_actionable | 0.502076 | 0.490000 | 0.012076 | 883.958000 | 0.047895 | 1.417050 | spectral_dominant_factor | True | 98.000000 |
| KXBTC15M-26MAY061200-00 | 2026-05-06T15:45:31.071643+00:00 | yes | rejected_actionable | 0.848576 | 0.810000 | 0.038576 | 868.928000 | 0.876136 | 0.613707 | spectral_dominant_factor | True | 35.000000 |
| KXBTC15M-26MAY061215-15 | 2026-05-06T16:01:34.070460+00:00 | no | rejected_actionable | 0.536898 | 0.530000 | 0.006898 | 805.930000 | 0.085521 | 1.278404 | spectral_dominant_factor | False | -110.000000 |
| KXBTC15M-26MAY061230-30 | 2026-05-06T16:16:10.710809+00:00 | yes | rejected_actionable | 0.681329 | 0.680000 | 0.001329 | 829.291000 | 0.451740 | 0.862457 | spectral_dominant_factor | False | -140.000000 |
| KXBTC15M-26MAY061245-45 | 2026-05-06T16:30:15.611477+00:00 | no | rejected_actionable | 0.555732 | 0.520000 | 0.035732 | 884.395000 | 0.180237 | 1.211363 | spectral_dominant_factor | False | -108.000000 |
| KXBTC15M-26MAY061300-00 | 2026-05-06T16:45:15.381495+00:00 | no | rejected_actionable | 0.544132 | 0.540000 | 0.004132 | 884.627000 | 0.065489 | 1.327168 | spectral_dominant_factor | True | 88.000000 |
| KXBTC15M-26MAY061400-00 | 2026-05-06T17:56:31.054630+00:00 | no | approved_entry | 0.973640 | 0.890000 | 0.083640 | 208.945000 | 1.815216 | 0.051736 | spectral_dominant_factor | True | -11.000000 |
| KXBTC15M-26MAY061415-15 | 2026-05-06T18:02:46.011143+00:00 | no | rejected_actionable | 0.519091 | 0.480000 | 0.039091 | 733.993000 | 0.062580 | 1.049181 | spectral_dominant_factor | True | 100.000000 |
| KXBTC15M-26MAY061430-30 | 2026-05-06T18:15:35.575390+00:00 | yes | rejected_actionable | 0.678512 | 0.670000 | 0.008512 | 864.426000 | 0.424290 | 0.893555 | spectral_dominant_factor | True | 62.000000 |
| KXBTC15M-26MAY061445-45 | 2026-05-06T18:30:15.600159+00:00 | no | rejected_actionable | 0.724164 | 0.710000 | 0.014164 | 884.401000 | 0.536135 | 0.800263 | spectral_dominant_factor | True | 55.000000 |
| KXBTC15M-26MAY061500-00 | 2026-05-06T18:46:58.043514+00:00 | yes | rejected_actionable | 0.550910 | 0.550000 | 0.000910 | 781.956000 | 0.111078 | 1.002871 | spectral_dominant_factor | False | -114.000000 |
| KXBTC15M-26MAY061515-15 | 2026-05-06T19:01:49.544322+00:00 | no | rejected_actionable | 0.518915 | 0.500000 | 0.018915 | 790.458000 | 0.055914 | 1.055565 | spectral_dominant_factor | True | 96.000000 |
| KXBTC15M-26MAY061530-30 | 2026-05-06T19:16:10.045725+00:00 | no | rejected_actionable | 0.548704 | 0.530000 | 0.018704 | 829.956000 | 0.150647 | 0.995442 | spectral_dominant_factor | False | -110.000000 |
| KXBTC15M-26MAY061545-45 | 2026-05-06T19:32:38.409201+00:00 | no | rejected_actionable | 0.513617 | 0.490000 | 0.023617 | 741.592000 | 0.029383 | 0.971969 | spectral_dominant_factor | False | -102.000000 |
| KXBTC15M-26MAY061600-00 | 2026-05-06T19:48:02.198360+00:00 | no | rejected_actionable | 0.610883 | 0.600000 | 0.010883 | 717.804000 | 0.229994 | 0.723320 | spectral_dominant_factor | False | -124.000000 |
| KXBTC15M-26MAY061615-15 | 2026-05-06T20:01:55.839170+00:00 | yes | rejected_actionable | 0.770727 | 0.740000 | 0.030727 | 784.161000 | 0.652892 | 0.500664 | spectral_dominant_factor | True | 49.000000 |
| KXBTC15M-26MAY061630-30 | 2026-05-06T20:21:34.178906+00:00 | no | rejected_actionable | 0.631665 | 0.630000 | 0.001665 | 505.823000 | 0.294854 | 0.450319 | spectral_dominant_factor | True | 70.000000 |
| KXBTC15M-26MAY061645-45 | 2026-05-06T20:30:41.561221+00:00 | no | rejected_actionable | 0.736529 | 0.710000 | 0.026529 | 858.442000 | 0.561593 | 0.588375 | spectral_dominant_factor | True | 55.000000 |
| KXBTC15M-26MAY061700-00 | 2026-05-06T20:47:20.371791+00:00 | no | rejected_actionable | 0.547299 | 0.490000 | 0.057299 | 759.628000 | 0.145303 | 0.799916 | spectral_dominant_factor | False | -102.000000 |
| KXBTC15M-26MAY061715-15 | 2026-05-06T21:01:35.182941+00:00 | yes | rejected_actionable | 0.633073 | 0.500000 | 0.133073 | 804.817000 | 0.324075 | 0.683095 | spectral_dominant_factor | False | -104.000000 |
| KXBTC15M-26MAY061730-30 | 2026-05-06T21:18:50.297953+00:00 | yes | rejected_actionable | 0.670106 | 0.630000 | 0.040106 | 669.703000 | 0.379541 | 0.501796 | spectral_dominant_factor | True | 70.000000 |
| KXBTC15M-26MAY061745-45 | 2026-05-06T21:33:51.536807+00:00 | no | rejected_actionable | 0.510383 | 0.140000 | 0.370383 | 668.465000 | 0.021042 | 0.689790 | spectral_dominant_factor | False | -30.000000 |
| KXBTC15M-26MAY061800-00 | 2026-05-06T21:46:50.262624+00:00 | no | rejected_actionable | 0.700391 | 0.680000 | 0.020391 | 789.738000 | 0.442267 | 0.545766 | spectral_dominant_factor | True | 60.000000 |
| KXBTC15M-26MAY061815-15 | 2026-05-06T22:03:49.503366+00:00 | no | rejected_actionable | 0.794472 | 0.720000 | 0.074472 | 670.498000 | 0.683153 | 0.363637 | spectral_dominant_factor | True | 53.000000 |
| KXBTC15M-26MAY061830-30 | 2026-05-06T22:19:06.460649+00:00 | yes | rejected_actionable | 0.553162 | 0.230000 | 0.323162 | 653.539000 | 0.098877 | 0.631576 | spectral_dominant_factor | False | -49.000000 |
| KXBTC15M-26MAY061900-00 | 2026-05-06T22:47:13.856939+00:00 | yes | rejected_actionable | 0.501794 | 0.340000 | 0.161794 | 766.143000 | 0.001392 | 0.794136 | spectral_dominant_factor | True | 128.000000 |
| KXBTC15M-26MAY061915-15 | 2026-05-06T23:03:05.391564+00:00 | no | approved_entry | 0.923342 | 0.870000 | 0.053342 | 714.621000 | 1.171707 | 0.229504 | spectral_dominant_factor | True | 22.000000 |
| KXBTC15M-26MAY061930-30 | 2026-05-06T23:16:29.602542+00:00 | yes | rejected_actionable | 0.551364 | 0.470000 | 0.081364 | 810.397000 | 0.100563 | 0.905378 | spectral_dominant_factor | True | 102.000000 |
| KXBTC15M-26MAY061945-45 | 2026-05-06T23:31:30.909184+00:00 | yes | rejected_actionable | 0.542407 | 0.420000 | 0.122407 | 809.092000 | 0.132650 | 0.801256 | spectral_dominant_factor | False | -88.000000 |
| KXBTC15M-26MAY062000-00 | 2026-05-06T23:45:50.011935+00:00 | yes | rejected_actionable | 0.582435 | 0.500000 | 0.082435 | 849.989000 | 0.192858 | 0.673972 | spectral_dominant_factor | True | 96.000000 |
| KXBTC15M-26MAY062015-15 | 2026-05-07T00:00:30.493763+00:00 | yes | rejected_actionable | 0.526847 | 0.510000 | 0.016847 | 869.507000 | 0.086972 | 0.736601 | spectral_factor | False | -106.000000 |
| KXBTC15M-26MAY062030-30 | 2026-05-07T00:16:35.289272+00:00 | yes | rejected_actionable | 0.544418 | 0.320000 | 0.224418 | 804.712000 | 0.107412 | 0.680770 | spectral_dominant_factor | False | -68.000000 |
| KXBTC15M-26MAY062045-45 | 2026-05-07T00:31:05.341326+00:00 | no | rejected_actionable | 0.617920 | 0.510000 | 0.107920 | 834.661000 | 0.321769 | 0.590304 | spectral_dominant_factor | True | 94.000000 |
| KXBTC15M-26MAY062100-00 | 2026-05-07T00:48:36.454910+00:00 | no | rejected_actionable | 0.615588 | 0.220000 | 0.395588 | 683.547000 | 0.321159 | 0.515467 | spectral_dominant_factor | False | -47.000000 |
| KXBTC15M-26MAY062115-15 | 2026-05-07T01:00:50.289770+00:00 | yes | rejected_actionable | 0.543753 | 0.530000 | 0.013753 | 849.710000 | 0.078109 | 0.866336 | spectral_dominant_factor | True | 90.000000 |
| KXBTC15M-26MAY062130-30 | 2026-05-07T01:17:26.891763+00:00 | yes | rejected_actionable | 0.586142 | 0.410000 | 0.176142 | 753.109000 | 0.212967 | 0.800157 | spectral_dominant_factor | True | 114.000000 |
| KXBTC15M-26MAY062145-45 | 2026-05-07T01:31:39.986158+00:00 | yes | rejected_actionable | 0.600378 | 0.570000 | 0.030378 | 800.015000 | 0.250555 | 0.820982 | spectral_dominant_factor | True | 82.000000 |
| KXBTC15M-26MAY062200-00 | 2026-05-07T01:49:50.936932+00:00 | no | rejected_actionable | 0.617816 | 0.460000 | 0.157816 | 609.066000 | 0.258689 | 0.567395 | spectral_dominant_factor | True | 104.000000 |
| KXBTC15M-26MAY062215-15 | 2026-05-07T02:00:49.721290+00:00 | no | rejected_actionable | 0.661831 | 0.590000 | 0.071831 | 850.282000 | 0.404187 | 0.669869 | spectral_dominant_factor | True | 78.000000 |
| KXBTC15M-26MAY062230-30 | 2026-05-07T02:22:19.050425+00:00 | yes | rejected_actionable | 0.718015 | 0.380000 | 0.338015 | 460.951000 | 0.481781 | 0.349672 | spectral_dominant_factor | False | -80.000000 |
| KXBTC15M-26MAY062245-45 | 2026-05-07T02:30:58.594419+00:00 | no | rejected_actionable | 0.605951 | 0.540000 | 0.065951 | 841.408000 | 0.278629 | 0.786584 | spectral_dominant_factor | False | -112.000000 |
| KXBTC15M-26MAY062300-00 | 2026-05-07T02:45:44.718830+00:00 | yes | rejected_actionable | 0.758354 | 0.730000 | 0.028354 | 855.282000 | 0.609402 | 0.572785 | spectral_dominant_factor | True | 51.000000 |
| KXBTC15M-26MAY062315-15 | 2026-05-07T03:04:20.470538+00:00 | no | rejected_actionable | 0.744580 | 0.680000 | 0.064580 | 639.531000 | 0.562923 | 0.455010 | spectral_dominant_factor | True | 60.000000 |
| KXBTC15M-26MAY062330-30 | 2026-05-07T03:19:16.559045+00:00 | yes | rejected_actionable | 0.546903 | 0.520000 | 0.026903 | 643.441000 | 0.093136 | 0.717935 | spectral_dominant_factor | False | -108.000000 |
| KXBTC15M-26MAY062345-45 | 2026-05-07T03:32:56.738408+00:00 | no | rejected_actionable | 0.608623 | 0.460000 | 0.148623 | 723.265000 | 0.276153 | 0.675325 | spectral_dominant_factor | False | -96.000000 |
| KXBTC15M-26MAY070000-00 | 2026-05-07T03:53:32.799784+00:00 | no | approved_entry | 0.863962 | 0.780000 | 0.083962 | 387.203000 | 0.906372 | 0.193188 | spectral_dominant_factor | True | 0.000000 |
| KXBTC15M-26MAY070015-15 | 2026-05-07T04:03:05.166345+00:00 | yes | rejected_actionable | 0.560075 | 0.560000 | 0.000075 | 714.834000 | 0.109123 | 0.785731 | spectral_dominant_factor | True | 84.000000 |
| KXBTC15M-26MAY070030-30 | 2026-05-07T04:17:09.890473+00:00 | no | rejected_actionable | 0.523605 | 0.330000 | 0.193605 | 770.113000 | 0.059362 | 0.901651 | spectral_dominant_factor | False | -70.000000 |
| KXBTC15M-26MAY070045-45 | 2026-05-07T04:31:29.650225+00:00 | no | rejected_actionable | 0.582164 | 0.480000 | 0.102164 | 810.351000 | 0.187292 | 0.830545 | spectral_dominant_factor | True | 100.000000 |
| KXBTC15M-26MAY070100-00 | 2026-05-07T04:50:56.697956+00:00 | no | rejected_actionable | 0.505013 | 0.220000 | 0.285013 | 543.305000 | 0.032616 | 0.647900 | spectral_dominant_factor | False | -47.000000 |
| KXBTC15M-26MAY070115-15 | 2026-05-07T05:02:05.219016+00:00 | yes | rejected_actionable | 0.773654 | 0.720000 | 0.053654 | 774.782000 | 0.649457 | 0.488844 | spectral_dominant_factor | True | 53.000000 |
| KXBTC15M-26MAY070130-30 | 2026-05-07T05:20:14.362177+00:00 | no | rejected_actionable | 0.604140 | 0.590000 | 0.014140 | 585.641000 | 0.227698 | 0.544225 | spectral_dominant_factor | True | 78.000000 |
| KXBTC15M-26MAY070145-45 | 2026-05-07T05:38:23.476574+00:00 | no | rejected_actionable | 0.838040 | 0.810000 | 0.028040 | 396.525000 | 0.811917 | 0.206140 | spectral_dominant_factor | True | 35.000000 |
| KXBTC15M-26MAY070200-00 | 2026-05-07T05:51:07.209567+00:00 | yes | rejected_actionable | 0.505710 | 0.300000 | 0.205710 | 532.791000 | 0.019784 | 0.602432 | spectral_dominant_factor | False | -63.000000 |
| KXBTC15M-26MAY070530-30 | 2026-05-07T09:15:20.383837+00:00 | no | rejected_actionable | 0.540822 | 0.480000 | 0.060822 | 879.618000 | 0.132673 | 0.894668 | spectral_dominant_factor | True | 100.000000 |
| KXBTC15M-26MAY070545-45 | 2026-05-07T09:30:44.310732+00:00 | yes | rejected_actionable | 0.707647 | 0.600000 | 0.107647 | 855.690000 | 0.462750 | 0.622015 | spectral_dominant_factor | False | -124.000000 |
| KXBTC15M-26MAY070600-00 | 2026-05-07T09:51:05.324526+00:00 | yes | rejected_actionable | 0.723960 | 0.670000 | 0.053960 | 534.677000 | 0.495921 | 0.394421 | spectral_dominant_factor | True | 62.000000 |
| KXBTC15M-26MAY070615-15 | 2026-05-07T10:03:17.740674+00:00 | no | rejected_actionable | 0.610872 | 0.280000 | 0.330872 | 702.260000 | 0.275276 | 0.645491 | spectral_dominant_factor | True | 141.000000 |
| KXBTC15M-26MAY070630-30 | 2026-05-07T10:15:24.038338+00:00 | yes | rejected_actionable | 0.606974 | 0.470000 | 0.136974 | 875.963000 | 0.230767 | 0.826469 | spectral_dominant_factor | False | -98.000000 |
| KXBTC15M-26MAY070645-45 | 2026-05-07T10:31:23.542448+00:00 | yes | approved_entry | 0.895399 | 0.810000 | 0.085399 | 816.468000 | 1.013529 | 0.368798 | spectral_dominant_factor | True | 35.000000 |
| KXBTC15M-26MAY070700-00 | 2026-05-07T10:45:30.364940+00:00 | yes | rejected_actionable | 0.654812 | 0.560000 | 0.094812 | 869.636000 | 0.375634 | 0.760124 | spectral_dominant_factor | False | -116.000000 |
| KXBTC15M-26MAY070715-15 | 2026-05-07T11:01:27.746774+00:00 | yes | rejected_actionable | 0.560435 | 0.510000 | 0.050435 | 812.253000 | 0.157545 | 0.877232 | spectral_dominant_factor | True | 94.000000 |
| KXBTC15M-26MAY070730-30 | 2026-05-07T11:16:20.358076+00:00 | yes | rejected_actionable | 0.530778 | 0.460000 | 0.070778 | 819.643000 | 0.091964 | 0.936121 | spectral_dominant_factor | False | -96.000000 |
| KXBTC15M-26MAY070745-45 | 2026-05-07T11:37:05.530271+00:00 | yes | approved_entry | 0.903807 | 0.680000 | 0.223807 | 474.481000 | 1.081343 | 0.197594 | spectral_dominant_factor | True | 32.000000 |
| KXBTC15M-26MAY070800-00 | 2026-05-07T11:47:08.774218+00:00 | yes | rejected_actionable | 0.536385 | 0.450000 | 0.086385 | 771.226000 | 0.080069 | 0.865475 | spectral_dominant_factor | False | -94.000000 |
| KXBTC15M-26MAY070815-15 | 2026-05-07T12:00:17.476976+00:00 | yes | rejected_actionable | 0.501147 | 0.440000 | 0.061147 | 882.524000 | 0.024626 | 1.067161 | spectral_dominant_factor | True | 108.000000 |
| KXBTC15M-26MAY070830-30 | 2026-05-07T12:16:28.176214+00:00 | yes | rejected_actionable | 0.514492 | 0.410000 | 0.104492 | 811.825000 | 0.078942 | 0.952791 | spectral_dominant_factor | False | -86.000000 |
| KXBTC15M-26MAY070845-45 | 2026-05-07T12:35:06.865667+00:00 | yes | rejected_actionable | 0.596088 | 0.450000 | 0.146088 | 593.135000 | 0.236616 | 0.596576 | spectral_dominant_factor | True | 106.000000 |
| KXBTC15M-26MAY070900-00 | 2026-05-07T12:47:06.779003+00:00 | yes | rejected_actionable | 0.597604 | 0.550000 | 0.047604 | 773.230000 | 0.238237 | 0.771689 | spectral_dominant_factor | True | 86.000000 |
| KXBTC15M-26MAY070915-15 | 2026-05-07T13:01:20.666238+00:00 | no | rejected_actionable | 0.788001 | 0.750000 | 0.038001 | 819.337000 | 0.676857 | 0.519751 | spectral_dominant_factor | True | 47.000000 |
| KXBTC15M-26MAY070930-30 | 2026-05-07T13:15:23.392993+00:00 | no | rejected_actionable | 0.511849 | 0.480000 | 0.031849 | 876.609000 | 0.078862 | 1.050154 | spectral_dominant_factor | False | -100.000000 |
| KXBTC15M-26MAY070945-45 | 2026-05-07T13:30:39.290511+00:00 | no | rejected_actionable | 0.532085 | 0.480000 | 0.052085 | 860.716000 | 0.067417 | 1.088863 | spectral_dominant_factor | True | 100.000000 |
| KXBTC15M-26MAY071000-00 | 2026-05-07T13:45:31.041597+00:00 | yes | rejected_actionable | 0.543510 | 0.540000 | 0.003510 | 868.958000 | 0.037031 | 1.219674 | spectral_dominant_factor | False | -112.000000 |
| KXBTC15M-26MAY071015-15 | 2026-05-07T14:00:35.784823+00:00 | no | rejected_actionable | 0.609894 | 0.600000 | 0.009894 | 864.225000 | 0.287274 | 1.102864 | spectral_dominant_factor | False | -124.000000 |
| KXBTC15M-26MAY071030-30 | 2026-05-07T14:15:47.461208+00:00 | no | rejected_actionable | 0.646380 | 0.620000 | 0.026380 | 852.539000 | 0.326478 | 1.053270 | spectral_dominant_factor | True | 72.000000 |
| KXBTC15M-26MAY071045-45 | 2026-05-07T14:30:37.149093+00:00 | yes | rejected_actionable | 0.557862 | 0.550000 | 0.007862 | 862.859000 | 0.082257 | 1.306314 | spectral_dominant_factor | False | -114.000000 |
| KXBTC15M-26MAY071100-00 | 2026-05-07T14:46:22.183095+00:00 | no | rejected_actionable | 0.578800 | 0.560000 | 0.018800 | 817.821000 | 0.236964 | 1.073938 | spectral_dominant_factor | True | 84.000000 |
| KXBTC15M-26MAY071115-15 | 2026-05-07T15:00:56.671254+00:00 | no | rejected_actionable | 0.635838 | 0.620000 | 0.015838 | 843.330000 | 0.346131 | 0.982771 | spectral_dominant_factor | False | -128.000000 |
| KXBTC15M-26MAY071130-30 | 2026-05-07T15:17:58.079448+00:00 | no | rejected_actionable | 0.582087 | 0.580000 | 0.002087 | 721.923000 | 0.214446 | 0.927686 | spectral_dominant_factor | True | 80.000000 |
| KXBTC15M-26MAY071145-45 | 2026-05-07T15:30:41.084707+00:00 | yes | rejected_actionable | 0.645637 | 0.610000 | 0.035637 | 858.916000 | 0.285653 | 1.101255 | spectral_dominant_factor | True | 74.000000 |
| KXBTC15M-26MAY071200-00 | 2026-05-07T15:46:46.178909+00:00 | yes | rejected_actionable | 0.606055 | 0.600000 | 0.006055 | 793.821000 | 0.250754 | 1.096302 | spectral_dominant_factor | False | -124.000000 |
| KXBTC15M-26MAY071215-15 | 2026-05-07T16:00:35.776954+00:00 | yes | rejected_actionable | 0.509397 | 0.470000 | 0.039397 | 864.223000 | 0.020950 | 1.397041 | spectral_dominant_factor | False | -98.000000 |
| KXBTC15M-26MAY071230-30 | 2026-05-07T16:15:36.510038+00:00 | no | rejected_actionable | 0.729882 | 0.700000 | 0.029882 | 863.492000 | 0.573733 | 0.815016 | spectral_dominant_factor | False | -143.000000 |
| KXBTC15M-26MAY071245-45 | 2026-05-07T16:30:15.640699+00:00 | yes | rejected_actionable | 0.559979 | 0.550000 | 0.009979 | 884.360000 | 0.168899 | 1.255835 | spectral_dominant_factor | False | -114.000000 |
| KXBTC15M-26MAY071300-00 | 2026-05-07T16:45:57.486009+00:00 | yes | rejected_actionable | 0.636040 | 0.590000 | 0.046040 | 842.515000 | 0.289227 | 1.011545 | spectral_dominant_factor | False | -122.000000 |
| KXBTC15M-26MAY071315-15 | 2026-05-07T17:00:41.152188+00:00 | yes | rejected_actionable | 0.533442 | 0.510000 | 0.023442 | 858.849000 | 0.042710 | 1.215232 | spectral_dominant_factor | True | 94.000000 |
| KXBTC15M-26MAY071330-30 | 2026-05-07T17:15:50.488414+00:00 | yes | rejected_actionable | 0.544206 | 0.520000 | 0.024206 | 849.512000 | 0.117101 | 1.086679 | spectral_dominant_factor | False | -108.000000 |
