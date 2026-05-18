# v28 Target-Surface Hybrid FV

Research-only validation on the fixed target-coverage entry surface.

- Freeze timestamp UTC: `2026-05-06T15:20:56.478006+00:00`
- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Forward denominator: `152`
- Hypothesis: Hybrid FV should improve calibration on broad target rows without changing selected side.

## Ranking

| rank | overlay | entries | settled | W/L | coverage | brier | d brier | logloss | d logloss | avg p | win rate | net c | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | boundary_recross_shrink_probability | 112 | 112 | 64/48 | 73.684211 | 0.214606 | -0.007141 | 0.609777 | -0.015609 | 0.611004 | 0.571429 | -626.000000 | coverage_too_low |
| 2 | hybrid_confidence_shrink | 112 | 112 | 64/48 | 73.684211 | 0.217581 | -0.004166 | 0.616939 | -0.008446 | 0.636089 | 0.571429 | -626.000000 | coverage_too_low |
| 3 | noise_shrink_light_probability | 112 | 112 | 64/48 | 73.684211 | 0.218838 | -0.002909 | 0.619911 | -0.005475 | 0.635157 | 0.571429 | -626.000000 | coverage_too_low |
| 4 | raw_probability | 112 | 112 | 64/48 | 73.684211 | 0.221747 | 0.000000 | 0.625385 | 0.000000 | 0.653763 | 0.571429 | -626.000000 | coverage_too_low |

## Groups

| bucket | entries | settled | W/L | coverage | net c | avg raw p | avg hybrid p | avg ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| reason_phi_half_high_recross | 27 | 27 | 12/15 | 17.763158 | -983.000000 | 0.647355 | 0.606694 | 0.607037 |
| hybrid_vetoes_raw_edge | 28 | 28 | 15/13 | 18.421053 | -682.000000 | 0.652484 | 0.610928 | 0.638214 |
| hybrid_edge_ge_8pp | 32 | 32 | 13/19 | 21.052632 | -167.000000 | 0.591792 | 0.584372 | 0.409062 |
| hybrid_edge_4_8pp | 29 | 29 | 18/11 | 19.078947 | -94.000000 | 0.660856 | 0.652647 | 0.592414 |
| reason_phi_quarter_near_strike | 3 | 3 | 2/1 | 1.973684 | 48.000000 | 0.609656 | 0.595604 | 0.566667 |
| reason_keep_raw_weak_heavy_noise | 36 | 36 | 17/19 | 23.684211 | 89.000000 | 0.549921 | 0.549921 | 0.440556 |
| hybrid_edge_2_4pp | 13 | 13 | 10/3 | 8.552632 | 100.000000 | 0.756293 | 0.742472 | 0.713846 |
| hybrid_edge_lt_2pp | 10 | 10 | 8/2 | 6.578947 | 217.000000 | 0.701791 | 0.685715 | 0.674000 |
| reason_noise_shrink_light_default | 46 | 46 | 33/13 | 30.263158 | 220.000000 | 0.741668 | 0.723418 | 0.656739 |

## Rows

| market | side | p raw | p hybrid | ask | raw edge | hybrid edge | edge bucket | reason | won | net c |
|---|---|---:|---:|---:|---:|---:|---|---|---|---:|
| KXBTC15M-26MAY051945-45 | yes | 0.613944 | 0.607292 | 0.510000 | 0.103944 | 0.097292 | hybrid_edge_ge_8pp | phi_quarter_near_strike | True | 94.000000 |
| KXBTC15M-26MAY052000-00 | no | 0.665463 | 0.642509 | 0.630000 | 0.035463 | 0.012509 | hybrid_edge_lt_2pp | noise_shrink_light_default | True | 70.000000 |
| KXBTC15M-26MAY052015-15 | no | 0.567861 | 0.567861 | 0.490000 | 0.077861 | 0.077861 | hybrid_edge_4_8pp | keep_raw_weak_heavy_noise | False | -102.000000 |
| KXBTC15M-26MAY052030-30 | yes | 0.540780 | 0.540780 | 0.470000 | 0.070780 | 0.070780 | hybrid_edge_4_8pp | keep_raw_weak_heavy_noise | False | -98.000000 |
| KXBTC15M-26MAY052100-00 | yes | 0.565554 | 0.565554 | 0.460000 | 0.105554 | 0.105554 | hybrid_edge_ge_8pp | keep_raw_weak_heavy_noise | True | 104.000000 |
| KXBTC15M-26MAY052115-15 | yes | 0.571476 | 0.571476 | 0.530000 | 0.041476 | 0.041476 | hybrid_edge_4_8pp | keep_raw_weak_heavy_noise | True | 90.000000 |
| KXBTC15M-26MAY052130-30 | yes | 0.822836 | 0.808638 | 0.800000 | 0.022836 | 0.008638 | hybrid_edge_lt_2pp | noise_shrink_light_default | True | 37.000000 |
| KXBTC15M-26MAY052145-45 | yes | 0.865417 | 0.852107 | 0.830000 | 0.035417 | 0.022107 | hybrid_edge_2_4pp | noise_shrink_light_default | True | 32.000000 |
| KXBTC15M-26MAY052215-15 | no | 0.809232 | 0.788502 | 0.770000 | 0.039232 | 0.018502 | hybrid_edge_lt_2pp | noise_shrink_light_default | True | 43.000000 |
| KXBTC15M-26MAY052230-30 | no | 0.730624 | 0.718041 | 0.650000 | 0.080624 | 0.068041 | hybrid_edge_4_8pp | noise_shrink_light_default | True | 66.000000 |
| KXBTC15M-26MAY052245-45 | no | 0.643789 | 0.622277 | 0.570000 | 0.073789 | 0.052277 | hybrid_edge_4_8pp | noise_shrink_light_default | False | -118.000000 |
| KXBTC15M-26MAY052300-00 | yes | 0.918967 | 0.906534 | 0.850000 | 0.068967 | 0.056534 | hybrid_edge_4_8pp | noise_shrink_light_default | True | 26.000000 |
| KXBTC15M-26MAY052315-15 | yes | 0.884999 | 0.872833 | 0.810000 | 0.074999 | 0.062833 | hybrid_edge_4_8pp | noise_shrink_light_default | True | -41.000000 |
| KXBTC15M-26MAY052330-30 | no | 0.659176 | 0.633906 | 0.630000 | 0.029176 | 0.003906 | hybrid_edge_lt_2pp | noise_shrink_light_default | False | -130.000000 |
| KXBTC15M-26MAY052345-45 | no | 0.636767 | 0.595332 | 0.630000 | 0.006767 | -0.034668 | hybrid_vetoes_raw_edge | phi_half_high_recross | True | 70.000000 |
| KXBTC15M-26MAY060030-30 | yes | 0.617077 | 0.603807 | 0.510000 | 0.107077 | 0.093807 | hybrid_edge_ge_8pp | phi_half_high_recross | False | -106.000000 |
| KXBTC15M-26MAY060045-45 | no | 0.826505 | 0.818364 | 0.790000 | 0.036505 | 0.028364 | hybrid_edge_2_4pp | noise_shrink_light_default | True | 39.000000 |
| KXBTC15M-26MAY060100-00 | yes | 0.799928 | 0.777761 | 0.790000 | 0.009928 | -0.012239 | hybrid_vetoes_raw_edge | noise_shrink_light_default | False | -161.000000 |
| KXBTC15M-26MAY060130-30 | no | 0.616779 | 0.581400 | 0.590000 | 0.026779 | -0.008600 | hybrid_vetoes_raw_edge | phi_half_high_recross | True | 78.000000 |
| KXBTC15M-26MAY060200-00 | yes | 0.618277 | 0.557467 | 0.600000 | 0.018277 | -0.042533 | hybrid_vetoes_raw_edge | phi_half_high_recross | True | 76.000000 |
| KXBTC15M-26MAY060215-15 | yes | 0.583024 | 0.583024 | 0.530000 | 0.053024 | 0.053024 | hybrid_edge_4_8pp | keep_raw_weak_heavy_noise | False | -110.000000 |
| KXBTC15M-26MAY060245-45 | no | 0.660829 | 0.636762 | 0.650000 | 0.010829 | -0.013238 | hybrid_vetoes_raw_edge | noise_shrink_light_default | False | -134.000000 |
| KXBTC15M-26MAY060300-00 | yes | 0.661141 | 0.637867 | 0.640000 | 0.021141 | -0.002133 | hybrid_vetoes_raw_edge | noise_shrink_light_default | True | 68.000000 |
| KXBTC15M-26MAY060330-30 | no | 0.630880 | 0.610893 | 0.570000 | 0.060880 | 0.040893 | hybrid_edge_4_8pp | noise_shrink_light_default | False | -118.000000 |
| KXBTC15M-26MAY060345-45 | yes | 0.515105 | 0.515105 | 0.380000 | 0.135105 | 0.135105 | hybrid_edge_ge_8pp | keep_raw_weak_heavy_noise | False | -80.000000 |
| KXBTC15M-26MAY060415-15 | yes | 0.676831 | 0.647636 | 0.670000 | 0.006831 | -0.022364 | hybrid_vetoes_raw_edge | noise_shrink_light_default | True | 62.000000 |
| KXBTC15M-26MAY060445-45 | no | 0.636374 | 0.615919 | 0.450000 | 0.186374 | 0.165919 | hybrid_edge_ge_8pp | noise_shrink_light_default | False | -94.000000 |
| KXBTC15M-26MAY060500-00 | no | 0.674136 | 0.645501 | 0.610000 | 0.064136 | 0.035501 | hybrid_edge_2_4pp | noise_shrink_light_default | False | -126.000000 |
| KXBTC15M-26MAY060515-15 | yes | 0.532512 | 0.532512 | 0.410000 | 0.122512 | 0.122512 | hybrid_edge_ge_8pp | keep_raw_weak_heavy_noise | False | -86.000000 |
| KXBTC15M-26MAY060530-30 | yes | 0.588889 | 0.588889 | 0.540000 | 0.048889 | 0.048889 | hybrid_edge_4_8pp | keep_raw_weak_heavy_noise | False | -112.000000 |
| KXBTC15M-26MAY060545-45 | no | 0.626642 | 0.604773 | 0.440000 | 0.186642 | 0.164773 | hybrid_edge_ge_8pp | noise_shrink_light_default | False | -92.000000 |
| KXBTC15M-26MAY060600-00 | no | 0.792357 | 0.772982 | 0.750000 | 0.042357 | 0.022982 | hybrid_edge_2_4pp | noise_shrink_light_default | True | 47.000000 |
| KXBTC15M-26MAY060630-30 | no | 0.675344 | 0.622222 | 0.660000 | 0.015344 | -0.037778 | hybrid_vetoes_raw_edge | phi_half_high_recross | False | -136.000000 |
| KXBTC15M-26MAY060645-45 | yes | 0.598639 | 0.598639 | 0.590000 | 0.008639 | 0.008639 | hybrid_edge_lt_2pp | keep_raw_weak_heavy_noise | True | 78.000000 |
| KXBTC15M-26MAY060730-30 | yes | 0.594884 | 0.594884 | 0.560000 | 0.034884 | 0.034884 | hybrid_edge_2_4pp | keep_raw_weak_heavy_noise | True | 84.000000 |
| KXBTC15M-26MAY060800-00 | yes | 0.523411 | 0.523411 | 0.470000 | 0.053411 | 0.053411 | hybrid_edge_4_8pp | keep_raw_weak_heavy_noise | True | 102.000000 |
| KXBTC15M-26MAY060830-30 | no | 0.600730 | 0.570213 | 0.590000 | 0.010730 | -0.019787 | hybrid_vetoes_raw_edge | phi_half_high_recross | False | -122.000000 |
| KXBTC15M-26MAY060915-15 | no | 0.672099 | 0.652592 | 0.600000 | 0.072099 | 0.052592 | hybrid_edge_4_8pp | phi_half_high_recross | True | 76.000000 |
| KXBTC15M-26MAY060930-30 | yes | 0.604377 | 0.550713 | 0.600000 | 0.004377 | -0.049287 | hybrid_vetoes_raw_edge | phi_half_high_recross | False | -124.000000 |
| KXBTC15M-26MAY060945-45 | no | 0.761891 | 0.761891 | 0.500000 | 0.261891 | 0.261891 | hybrid_edge_ge_8pp | phi_half_high_recross | True | 96.000000 |
| KXBTC15M-26MAY061015-15 | no | 0.595554 | 0.595554 | 0.520000 | 0.075554 | 0.075554 | hybrid_edge_4_8pp | keep_raw_weak_heavy_noise | True | 92.000000 |
| KXBTC15M-26MAY061030-30 | yes | 0.618153 | 0.557407 | 0.610000 | 0.008153 | -0.052593 | hybrid_vetoes_raw_edge | phi_half_high_recross | True | 74.000000 |
| KXBTC15M-26MAY061045-45 | no | 0.601767 | 0.549445 | 0.570000 | 0.031767 | -0.020555 | hybrid_vetoes_raw_edge | phi_half_high_recross | False | -118.000000 |
| KXBTC15M-26MAY061100-00 | yes | 0.740374 | 0.667551 | 0.740000 | 0.000374 | -0.072449 | hybrid_vetoes_raw_edge | phi_half_high_recross | False | -151.000000 |
| KXBTC15M-26MAY061130-30 | yes | 0.653101 | 0.606718 | 0.650000 | 0.003101 | -0.043282 | hybrid_vetoes_raw_edge | phi_half_high_recross | True | 66.000000 |
| KXBTC15M-26MAY061200-00 | yes | 0.848576 | 0.837024 | 0.810000 | 0.038576 | 0.027024 | hybrid_edge_2_4pp | noise_shrink_light_default | True | 35.000000 |
| KXBTC15M-26MAY061230-30 | yes | 0.681329 | 0.626394 | 0.680000 | 0.001329 | -0.053606 | hybrid_vetoes_raw_edge | phi_half_high_recross | False | -140.000000 |
| KXBTC15M-26MAY061400-00 | no | 0.973640 | 0.962844 | 0.890000 | 0.083640 | 0.072844 | hybrid_edge_4_8pp | noise_shrink_light_default | True | -11.000000 |
| KXBTC15M-26MAY061430-30 | yes | 0.678512 | 0.624430 | 0.670000 | 0.008512 | -0.045570 | hybrid_vetoes_raw_edge | phi_half_high_recross | True | 62.000000 |
| KXBTC15M-26MAY061445-45 | no | 0.724164 | 0.656252 | 0.710000 | 0.014164 | -0.053748 | hybrid_vetoes_raw_edge | phi_half_high_recross | True | 55.000000 |
| KXBTC15M-26MAY061600-00 | no | 0.610883 | 0.592575 | 0.600000 | 0.010883 | -0.007425 | hybrid_vetoes_raw_edge | phi_quarter_near_strike | False | -124.000000 |
| KXBTC15M-26MAY061615-15 | yes | 0.770727 | 0.754462 | 0.740000 | 0.030727 | 0.014462 | hybrid_edge_lt_2pp | noise_shrink_light_default | True | 49.000000 |
| KXBTC15M-26MAY061630-30 | no | 0.631665 | 0.612700 | 0.630000 | 0.001665 | -0.017300 | hybrid_vetoes_raw_edge | noise_shrink_light_default | True | 70.000000 |
| KXBTC15M-26MAY061645-45 | no | 0.736529 | 0.715098 | 0.710000 | 0.026529 | 0.005098 | hybrid_edge_lt_2pp | noise_shrink_light_default | True | 55.000000 |
| KXBTC15M-26MAY061700-00 | no | 0.547299 | 0.547299 | 0.490000 | 0.057299 | 0.057299 | hybrid_edge_4_8pp | keep_raw_weak_heavy_noise | False | -102.000000 |
| KXBTC15M-26MAY061715-15 | yes | 0.633073 | 0.612850 | 0.500000 | 0.133073 | 0.112850 | hybrid_edge_ge_8pp | noise_shrink_light_default | False | -104.000000 |
| KXBTC15M-26MAY061730-30 | yes | 0.670106 | 0.647956 | 0.630000 | 0.040106 | 0.017956 | hybrid_edge_lt_2pp | noise_shrink_light_default | True | 70.000000 |
| KXBTC15M-26MAY061745-45 | no | 0.510383 | 0.510383 | 0.140000 | 0.370383 | 0.370383 | hybrid_edge_ge_8pp | keep_raw_weak_heavy_noise | False | -30.000000 |
| KXBTC15M-26MAY061800-00 | no | 0.700391 | 0.669232 | 0.680000 | 0.020391 | -0.010768 | hybrid_vetoes_raw_edge | noise_shrink_light_default | True | 60.000000 |
| KXBTC15M-26MAY061815-15 | no | 0.794472 | 0.781622 | 0.720000 | 0.074472 | 0.061622 | hybrid_edge_4_8pp | noise_shrink_light_default | True | 53.000000 |
| KXBTC15M-26MAY061830-30 | yes | 0.553162 | 0.553162 | 0.230000 | 0.323162 | 0.323162 | hybrid_edge_ge_8pp | keep_raw_weak_heavy_noise | False | -49.000000 |
| KXBTC15M-26MAY061900-00 | yes | 0.501794 | 0.501794 | 0.340000 | 0.161794 | 0.161794 | hybrid_edge_ge_8pp | keep_raw_weak_heavy_noise | True | 128.000000 |
| KXBTC15M-26MAY061915-15 | no | 0.923342 | 0.909629 | 0.870000 | 0.053342 | 0.039629 | hybrid_edge_2_4pp | noise_shrink_light_default | True | 22.000000 |
| KXBTC15M-26MAY061930-30 | yes | 0.551364 | 0.551364 | 0.470000 | 0.081364 | 0.081364 | hybrid_edge_ge_8pp | keep_raw_weak_heavy_noise | True | 102.000000 |
| KXBTC15M-26MAY061945-45 | yes | 0.542407 | 0.542407 | 0.420000 | 0.122407 | 0.122407 | hybrid_edge_ge_8pp | keep_raw_weak_heavy_noise | False | -88.000000 |
| KXBTC15M-26MAY062000-00 | yes | 0.582435 | 0.582435 | 0.500000 | 0.082435 | 0.082435 | hybrid_edge_ge_8pp | keep_raw_weak_heavy_noise | True | 96.000000 |
| KXBTC15M-26MAY062015-15 | yes | 0.526847 | 0.526847 | 0.510000 | 0.016847 | 0.016847 | hybrid_edge_lt_2pp | keep_raw_weak_heavy_noise | False | -106.000000 |
| KXBTC15M-26MAY062030-30 | yes | 0.544418 | 0.544418 | 0.320000 | 0.224418 | 0.224418 | hybrid_edge_ge_8pp | keep_raw_weak_heavy_noise | False | -68.000000 |
| KXBTC15M-26MAY062045-45 | no | 0.617920 | 0.601313 | 0.510000 | 0.107920 | 0.091313 | hybrid_edge_ge_8pp | noise_shrink_light_default | True | 94.000000 |
| KXBTC15M-26MAY062100-00 | no | 0.615588 | 0.600347 | 0.220000 | 0.395588 | 0.380347 | hybrid_edge_ge_8pp | noise_shrink_light_default | False | -47.000000 |
| KXBTC15M-26MAY062130-30 | yes | 0.586142 | 0.586142 | 0.410000 | 0.176142 | 0.176142 | hybrid_edge_ge_8pp | keep_raw_weak_heavy_noise | True | 114.000000 |
| KXBTC15M-26MAY062145-45 | yes | 0.600378 | 0.569968 | 0.570000 | 0.030378 | -0.000032 | hybrid_vetoes_raw_edge | phi_half_high_recross | True | 82.000000 |
| KXBTC15M-26MAY062200-00 | no | 0.617816 | 0.599191 | 0.460000 | 0.157816 | 0.139191 | hybrid_edge_ge_8pp | noise_shrink_light_default | True | 104.000000 |
| KXBTC15M-26MAY062215-15 | no | 0.661831 | 0.637494 | 0.590000 | 0.071831 | 0.047494 | hybrid_edge_4_8pp | noise_shrink_light_default | True | 78.000000 |
| KXBTC15M-26MAY062230-30 | yes | 0.718015 | 0.693606 | 0.380000 | 0.338015 | 0.313606 | hybrid_edge_ge_8pp | noise_shrink_light_default | False | -80.000000 |
| KXBTC15M-26MAY062245-45 | no | 0.605951 | 0.593942 | 0.540000 | 0.065951 | 0.053942 | hybrid_edge_4_8pp | phi_half_high_recross | False | -112.000000 |
| KXBTC15M-26MAY062300-00 | yes | 0.758354 | 0.740596 | 0.730000 | 0.028354 | 0.010596 | hybrid_edge_lt_2pp | noise_shrink_light_default | True | 51.000000 |
| KXBTC15M-26MAY062315-15 | no | 0.744580 | 0.731226 | 0.680000 | 0.064580 | 0.051226 | hybrid_edge_4_8pp | noise_shrink_light_default | True | 60.000000 |
| KXBTC15M-26MAY062330-30 | yes | 0.546903 | 0.546903 | 0.520000 | 0.026903 | 0.026903 | hybrid_edge_2_4pp | keep_raw_weak_heavy_noise | False | -108.000000 |
| KXBTC15M-26MAY062345-45 | no | 0.608623 | 0.590044 | 0.460000 | 0.148623 | 0.130044 | hybrid_edge_ge_8pp | noise_shrink_light_default | False | -96.000000 |
| KXBTC15M-26MAY070000-00 | no | 0.863962 | 0.852886 | 0.780000 | 0.083962 | 0.072886 | hybrid_edge_4_8pp | noise_shrink_light_default | True | 0.000000 |
| KXBTC15M-26MAY070030-30 | no | 0.523605 | 0.523605 | 0.330000 | 0.193605 | 0.193605 | hybrid_edge_ge_8pp | keep_raw_weak_heavy_noise | False | -70.000000 |
| KXBTC15M-26MAY070045-45 | no | 0.582164 | 0.582164 | 0.480000 | 0.102164 | 0.102164 | hybrid_edge_ge_8pp | keep_raw_weak_heavy_noise | True | 100.000000 |
| KXBTC15M-26MAY070100-00 | no | 0.505013 | 0.505013 | 0.220000 | 0.285013 | 0.285013 | hybrid_edge_ge_8pp | keep_raw_weak_heavy_noise | False | -47.000000 |
| KXBTC15M-26MAY070115-15 | yes | 0.773654 | 0.752128 | 0.720000 | 0.053654 | 0.032128 | hybrid_edge_2_4pp | noise_shrink_light_default | True | 53.000000 |
| KXBTC15M-26MAY070130-30 | no | 0.604140 | 0.586946 | 0.590000 | 0.014140 | -0.003054 | hybrid_vetoes_raw_edge | phi_quarter_near_strike | True | 78.000000 |
| KXBTC15M-26MAY070145-45 | no | 0.838040 | 0.834277 | 0.810000 | 0.028040 | 0.024277 | hybrid_edge_2_4pp | noise_shrink_light_default | True | 35.000000 |
| KXBTC15M-26MAY070200-00 | yes | 0.505710 | 0.505710 | 0.300000 | 0.205710 | 0.205710 | hybrid_edge_ge_8pp | keep_raw_weak_heavy_noise | False | -63.000000 |
| KXBTC15M-26MAY070530-30 | no | 0.540822 | 0.540822 | 0.480000 | 0.060822 | 0.060822 | hybrid_edge_4_8pp | keep_raw_weak_heavy_noise | True | 100.000000 |
| KXBTC15M-26MAY070545-45 | yes | 0.707647 | 0.677613 | 0.600000 | 0.107647 | 0.077613 | hybrid_edge_4_8pp | noise_shrink_light_default | False | -124.000000 |
| KXBTC15M-26MAY070600-00 | yes | 0.723960 | 0.697683 | 0.670000 | 0.053960 | 0.027683 | hybrid_edge_2_4pp | noise_shrink_light_default | True | 62.000000 |
| KXBTC15M-26MAY070615-15 | no | 0.610872 | 0.594523 | 0.280000 | 0.330872 | 0.314523 | hybrid_edge_ge_8pp | noise_shrink_light_default | True | 141.000000 |
| KXBTC15M-26MAY070630-30 | yes | 0.606974 | 0.566114 | 0.470000 | 0.136974 | 0.096114 | hybrid_edge_ge_8pp | phi_half_high_recross | False | -98.000000 |
| KXBTC15M-26MAY070645-45 | yes | 0.895399 | 0.887525 | 0.810000 | 0.085399 | 0.077525 | hybrid_edge_4_8pp | noise_shrink_light_default | True | 35.000000 |
| KXBTC15M-26MAY070700-00 | yes | 0.654812 | 0.637264 | 0.560000 | 0.094812 | 0.077264 | hybrid_edge_4_8pp | phi_half_high_recross | False | -116.000000 |
| KXBTC15M-26MAY070715-15 | yes | 0.560435 | 0.560435 | 0.510000 | 0.050435 | 0.050435 | hybrid_edge_4_8pp | keep_raw_weak_heavy_noise | True | 94.000000 |
| KXBTC15M-26MAY070730-30 | yes | 0.530778 | 0.530778 | 0.460000 | 0.070778 | 0.070778 | hybrid_edge_4_8pp | keep_raw_weak_heavy_noise | False | -96.000000 |
| KXBTC15M-26MAY070745-45 | yes | 0.903807 | 0.899498 | 0.680000 | 0.223807 | 0.219498 | hybrid_edge_ge_8pp | noise_shrink_light_default | True | 32.000000 |
| KXBTC15M-26MAY070800-00 | yes | 0.536385 | 0.536385 | 0.450000 | 0.086385 | 0.086385 | hybrid_edge_ge_8pp | keep_raw_weak_heavy_noise | False | -94.000000 |
| KXBTC15M-26MAY070815-15 | yes | 0.501147 | 0.501147 | 0.440000 | 0.061147 | 0.061147 | hybrid_edge_4_8pp | keep_raw_weak_heavy_noise | True | 108.000000 |
| KXBTC15M-26MAY070830-30 | yes | 0.514492 | 0.514492 | 0.410000 | 0.104492 | 0.104492 | hybrid_edge_ge_8pp | keep_raw_weak_heavy_noise | False | -86.000000 |
| KXBTC15M-26MAY070845-45 | yes | 0.596088 | 0.596088 | 0.450000 | 0.146088 | 0.146088 | hybrid_edge_ge_8pp | keep_raw_weak_heavy_noise | True | 106.000000 |
| KXBTC15M-26MAY070900-00 | yes | 0.597604 | 0.597604 | 0.550000 | 0.047604 | 0.047604 | hybrid_edge_4_8pp | keep_raw_weak_heavy_noise | True | 86.000000 |
| KXBTC15M-26MAY070915-15 | no | 0.788001 | 0.770038 | 0.750000 | 0.038001 | 0.020038 | hybrid_edge_2_4pp | noise_shrink_light_default | True | 47.000000 |
| KXBTC15M-26MAY070945-45 | no | 0.532085 | 0.532085 | 0.480000 | 0.052085 | 0.052085 | hybrid_edge_4_8pp | keep_raw_weak_heavy_noise | True | 100.000000 |
| KXBTC15M-26MAY071015-15 | no | 0.609894 | 0.576601 | 0.600000 | 0.009894 | -0.023399 | hybrid_vetoes_raw_edge | phi_half_high_recross | False | -124.000000 |
| KXBTC15M-26MAY071030-30 | no | 0.646380 | 0.602033 | 0.620000 | 0.026380 | -0.017967 | hybrid_vetoes_raw_edge | phi_half_high_recross | True | 72.000000 |
| KXBTC15M-26MAY071115-15 | no | 0.635838 | 0.594685 | 0.620000 | 0.015838 | -0.025315 | hybrid_vetoes_raw_edge | phi_half_high_recross | False | -128.000000 |
| KXBTC15M-26MAY071145-45 | yes | 0.645637 | 0.601515 | 0.610000 | 0.035637 | -0.008485 | hybrid_vetoes_raw_edge | phi_half_high_recross | True | 74.000000 |
| KXBTC15M-26MAY071200-00 | yes | 0.606055 | 0.573925 | 0.600000 | 0.006055 | -0.026075 | hybrid_vetoes_raw_edge | phi_half_high_recross | False | -124.000000 |
| KXBTC15M-26MAY071230-30 | no | 0.729882 | 0.660238 | 0.700000 | 0.029882 | -0.039762 | hybrid_vetoes_raw_edge | phi_half_high_recross | False | -143.000000 |
| KXBTC15M-26MAY071300-00 | yes | 0.636040 | 0.620620 | 0.590000 | 0.046040 | 0.030620 | hybrid_edge_2_4pp | phi_half_high_recross | False | -122.000000 |
