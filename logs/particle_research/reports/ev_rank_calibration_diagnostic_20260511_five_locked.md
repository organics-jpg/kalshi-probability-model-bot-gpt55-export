# EV Rank / Calibration Diagnostic

- run_count: 5
- candidate_count: 16931
- selected_count: 15689
- ev_rank_correlation_sign: 0.045851
- top_ev_bucket_stable_positive: False
- best_probability_model_by_brier: current_calibrated
- best_probability_model_by_log_loss: current_calibrated
- conclusion: Top predicted EV bucket is not positive in every supplied locked run; EV ranking does not yet satisfy the particle-system promotion gate.

## EV Bucket Stability

| bucket | positive_runs | candidates | selected | total_pnl_cents | min_run_pnl_cents | avg_pnl_cents | stable_positive |
|---|---:|---:|---:|---:|---:|---:|---|
| ev_rank_1_highest | 1/5 | 3388 | 3388 | 766.0000 | -4192.0000 | 0.2261 | False |
| ev_rank_2 | 3/5 | 3387 | 3387 | 19926.0000 | -6118.0000 | 5.8831 | False |
| ev_rank_3 | 4/5 | 3385 | 3385 | 15975.0000 | -11648.0000 | 4.7194 | False |
| ev_rank_4 | 4/5 | 3387 | 3387 | 29387.0000 | -8068.0000 | 8.6764 | False |
| ev_rank_5_lowest | 3/5 | 3384 | 2142 | 8267.0000 | -3248.0000 | 2.4430 | False |

## Probability Model Summary

| model | count | brier | log_loss | mean_abs_cal_error | high_conf_count | high_conf_abs_cal_error |
|---|---:|---:|---:|---:|---:|---:|
| current_calibrated | 16931 | 0.165260 | 0.479494 | 0.225475 | 7504 | 0.102992 |
| market | 16931 | 0.170081 | 0.490636 | 0.227347 | 6711 | 0.089084 |
| brownian | 16931 | 0.181760 | 0.540564 | 0.288463 | 1888 | 0.112824 |
| particle | 16931 | 0.181858 | 0.540726 | 0.287299 | 1873 | 0.111935 |

## EV Bucket By Run

| run | bucket | candidates | selected | win_rate | avg_ev_cents | pnl_cents | avg_pnl_cents | yes | no | against_consensus |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| particle_side_safety_oos_20260511TLOCKED | ev_rank_1_highest | 680 | 680 | 0.0721 | 24.9045 | -312.0000 | -0.4588 | 429 | 251 | 674 |
| particle_side_safety_oos_20260511TLOCKED | ev_rank_2 | 680 | 680 | 0.2000 | 17.1912 | 3574.0000 | 5.2559 | 501 | 179 | 675 |
| particle_side_safety_oos_20260511TLOCKED | ev_rank_3 | 679 | 679 | 0.3343 | 11.0897 | 1939.0000 | 2.8557 | 490 | 189 | 657 |
| particle_side_safety_oos_20260511TLOCKED | ev_rank_4 | 680 | 680 | 0.4574 | 5.5638 | 4910.0000 | 7.2206 | 406 | 274 | 536 |
| particle_side_safety_oos_20260511TLOCKED | ev_rank_5_lowest | 679 | 392 | 0.6020 | 0.4532 | 4805.0000 | 7.0766 | 263 | 416 | 312 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | ev_rank_1_highest | 701 | 701 | 0.0257 | 29.1291 | -1915.0000 | -2.7318 | 235 | 466 | 693 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | ev_rank_2 | 700 | 700 | 0.1071 | 21.4226 | -1788.0000 | -2.5543 | 253 | 447 | 694 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | ev_rank_3 | 700 | 700 | 0.3571 | 12.9358 | 4056.0000 | 5.7943 | 143 | 557 | 667 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | ev_rank_4 | 700 | 700 | 0.6029 | 6.1387 | 13320.0000 | 19.0286 | 116 | 584 | 559 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | ev_rank_5_lowest | 700 | 474 | 0.5295 | 0.7053 | 2125.0000 | 3.0357 | 291 | 409 | 430 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | ev_rank_1_highest | 683 | 683 | 0.2152 | 29.3020 | 9538.0000 | 13.9649 | 153 | 530 | 662 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | ev_rank_2 | 683 | 683 | 0.2474 | 22.4357 | 7787.0000 | 11.4012 | 181 | 502 | 678 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | ev_rank_3 | 683 | 683 | 0.2299 | 15.3770 | 238.0000 | 0.3485 | 195 | 488 | 674 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | ev_rank_4 | 683 | 683 | 0.3734 | 8.6954 | 1462.0000 | 2.1406 | 269 | 414 | 640 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | ev_rank_5_lowest | 682 | 497 | 0.4064 | 1.3606 | -3248.0000 | -4.7625 | 288 | 394 | 410 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | ev_rank_1_highest | 652 | 652 | 0.0337 | 18.1855 | -4192.0000 | -6.4294 | 216 | 436 | 637 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | ev_rank_2 | 652 | 652 | 0.0552 | 10.7292 | -6118.0000 | -9.3834 | 375 | 277 | 644 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | ev_rank_3 | 652 | 652 | 0.0414 | 6.2688 | -11648.0000 | -17.8650 | 523 | 129 | 638 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | ev_rank_4 | 652 | 652 | 0.1242 | 2.9759 | -8068.0000 | -12.3742 | 521 | 131 | 628 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | ev_rank_5_lowest | 652 | 421 | 0.2447 | 0.3225 | -2476.0000 | -3.7975 | 425 | 227 | 529 |
| particle_residual_blend_oos_RESIDLOCK001 | ev_rank_1_highest | 672 | 672 | 0.0685 | 17.6918 | -2353.0000 | -3.5015 | 266 | 406 | 663 |
| particle_residual_blend_oos_RESIDLOCK001 | ev_rank_2 | 672 | 672 | 0.4598 | 10.7369 | 16471.0000 | 24.5104 | 540 | 132 | 668 |
| particle_residual_blend_oos_RESIDLOCK001 | ev_rank_3 | 671 | 671 | 0.6140 | 7.0081 | 21390.0000 | 31.8778 | 559 | 112 | 646 |
| particle_residual_blend_oos_RESIDLOCK001 | ev_rank_4 | 672 | 672 | 0.6429 | 3.5051 | 17763.0000 | 26.4330 | 510 | 162 | 589 |
| particle_residual_blend_oos_RESIDLOCK001 | ev_rank_5_lowest | 671 | 358 | 0.6285 | 0.0729 | 7061.0000 | 10.5231 | 402 | 269 | 427 |

## Probability Buckets

| run | model | bucket | count | avg_pred_p_yes | empirical_yes_rate | calibration_error | brier | log_loss |
|---|---|---|---:|---:|---:|---:|---:|---:|
| particle_side_safety_oos_20260511TLOCKED | particle | 0.0_0.1 | 46 | 0.041359 | 0.000000 | -0.041359 | 0.001814 | 0.042295 |
| particle_side_safety_oos_20260511TLOCKED | particle | 0.1_0.2 | 107 | 0.171897 | 0.000000 | -0.171897 | 0.029949 | 0.188907 |
| particle_side_safety_oos_20260511TLOCKED | particle | 0.2_0.3 | 504 | 0.252206 | 0.000000 | -0.252206 | 0.064214 | 0.291170 |
| particle_side_safety_oos_20260511TLOCKED | particle | 0.3_0.4 | 474 | 0.359410 | 0.082278 | -0.277132 | 0.148241 | 0.483323 |
| particle_side_safety_oos_20260511TLOCKED | particle | 0.4_0.5 | 1358 | 0.453516 | 0.263623 | -0.189893 | 0.230300 | 0.653531 |
| particle_side_safety_oos_20260511TLOCKED | particle | 0.5_0.6 | 737 | 0.536997 | 0.358209 | -0.178788 | 0.257577 | 0.708358 |
| particle_side_safety_oos_20260511TLOCKED | particle | 0.6_0.7 | 139 | 0.641871 | 0.863309 | 0.221439 | 0.158246 | 0.503742 |
| particle_side_safety_oos_20260511TLOCKED | particle | 0.7_0.8 | 24 | 0.734792 | 1.000000 | 0.265208 | 0.071241 | 0.308990 |
| particle_side_safety_oos_20260511TLOCKED | particle | 0.8_0.9 | 9 | 0.828778 | 1.000000 | 0.171222 | 0.029680 | 0.188065 |
| particle_side_safety_oos_20260511TLOCKED | brownian | 0.0_0.1 | 46 | 0.042329 | 0.000000 | -0.042329 | 0.001876 | 0.043298 |
| particle_side_safety_oos_20260511TLOCKED | brownian | 0.1_0.2 | 105 | 0.173586 | 0.000000 | -0.173586 | 0.030538 | 0.190952 |
| particle_side_safety_oos_20260511TLOCKED | brownian | 0.2_0.3 | 502 | 0.251420 | 0.000000 | -0.251420 | 0.063770 | 0.290075 |
| particle_side_safety_oos_20260511TLOCKED | brownian | 0.3_0.4 | 466 | 0.359366 | 0.081545 | -0.277821 | 0.147930 | 0.482646 |
| particle_side_safety_oos_20260511TLOCKED | brownian | 0.4_0.5 | 1425 | 0.455660 | 0.285614 | -0.170046 | 0.231328 | 0.655603 |
| particle_side_safety_oos_20260511TLOCKED | brownian | 0.5_0.6 | 692 | 0.539263 | 0.315029 | -0.224234 | 0.258554 | 0.710357 |
| particle_side_safety_oos_20260511TLOCKED | brownian | 0.6_0.7 | 130 | 0.643168 | 0.915385 | 0.272217 | 0.145077 | 0.476769 |
| particle_side_safety_oos_20260511TLOCKED | brownian | 0.7_0.8 | 24 | 0.734971 | 1.000000 | 0.265029 | 0.071165 | 0.308763 |
| particle_side_safety_oos_20260511TLOCKED | brownian | 0.8_0.9 | 8 | 0.833144 | 1.000000 | 0.166856 | 0.028272 | 0.182858 |
| particle_side_safety_oos_20260511TLOCKED | market | 0.0_0.1 | 724 | 0.036768 | 0.000000 | -0.036768 | 0.002053 | 0.037841 |
| particle_side_safety_oos_20260511TLOCKED | market | 0.1_0.2 | 223 | 0.145090 | 0.000000 | -0.145090 | 0.021896 | 0.157341 |
| particle_side_safety_oos_20260511TLOCKED | market | 0.2_0.3 | 339 | 0.266947 | 0.259587 | -0.007360 | 0.189054 | 0.564041 |
| particle_side_safety_oos_20260511TLOCKED | market | 0.3_0.4 | 476 | 0.343340 | 0.266807 | -0.076534 | 0.197421 | 0.584573 |
| particle_side_safety_oos_20260511TLOCKED | market | 0.4_0.5 | 518 | 0.459556 | 0.231660 | -0.227896 | 0.238763 | 0.670734 |
| particle_side_safety_oos_20260511TLOCKED | market | 0.5_0.6 | 457 | 0.542090 | 0.306346 | -0.235744 | 0.266964 | 0.727360 |
| particle_side_safety_oos_20260511TLOCKED | market | 0.6_0.7 | 204 | 0.643995 | 0.318627 | -0.325368 | 0.311165 | 0.818759 |
| particle_side_safety_oos_20260511TLOCKED | market | 0.7_0.8 | 207 | 0.739106 | 0.318841 | -0.420266 | 0.399314 | 1.029646 |
| particle_side_safety_oos_20260511TLOCKED | market | 0.8_0.9 | 99 | 0.833030 | 0.575758 | -0.257273 | 0.287705 | 0.785267 |
| particle_side_safety_oos_20260511TLOCKED | market | 0.9_1.0 | 151 | 0.966887 | 1.000000 | 0.033113 | 0.002057 | 0.034194 |
| particle_side_safety_oos_20260511TLOCKED | current_calibrated | 0.0_0.1 | 626 | 0.047579 | 0.000000 | -0.047579 | 0.002839 | 0.049067 |
| particle_side_safety_oos_20260511TLOCKED | current_calibrated | 0.1_0.2 | 272 | 0.147168 | 0.000000 | -0.147168 | 0.022596 | 0.159841 |
| particle_side_safety_oos_20260511TLOCKED | current_calibrated | 0.2_0.3 | 354 | 0.248813 | 0.211864 | -0.036948 | 0.160608 | 0.499275 |
| particle_side_safety_oos_20260511TLOCKED | current_calibrated | 0.3_0.4 | 474 | 0.347816 | 0.261603 | -0.086213 | 0.196050 | 0.581788 |
| particle_side_safety_oos_20260511TLOCKED | current_calibrated | 0.4_0.5 | 670 | 0.449589 | 0.222388 | -0.227201 | 0.223569 | 0.640018 |
| particle_side_safety_oos_20260511TLOCKED | current_calibrated | 0.5_0.6 | 487 | 0.537085 | 0.283368 | -0.253717 | 0.278507 | 0.750576 |
| particle_side_safety_oos_20260511TLOCKED | current_calibrated | 0.6_0.7 | 234 | 0.642169 | 0.551282 | -0.090887 | 0.254502 | 0.703163 |
| particle_side_safety_oos_20260511TLOCKED | current_calibrated | 0.7_0.8 | 137 | 0.732662 | 0.401460 | -0.331202 | 0.365822 | 0.956028 |
| particle_side_safety_oos_20260511TLOCKED | current_calibrated | 0.8_0.9 | 144 | 0.832988 | 1.000000 | 0.167012 | 0.027893 | 0.182736 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | particle | 0.0_0.1 | 30 | 0.060883 | 0.000000 | -0.060883 | 0.004406 | 0.063206 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | particle | 0.1_0.2 | 28 | 0.148661 | 0.000000 | -0.148661 | 0.023085 | 0.161629 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | particle | 0.2_0.3 | 86 | 0.253128 | 0.000000 | -0.253128 | 0.064914 | 0.292616 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | particle | 0.3_0.4 | 523 | 0.351820 | 0.000000 | -0.351820 | 0.124367 | 0.434287 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | particle | 0.4_0.5 | 706 | 0.474147 | 0.082153 | -0.391994 | 0.226371 | 0.645740 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | particle | 0.5_0.6 | 1306 | 0.538717 | 0.410413 | -0.128304 | 0.252056 | 0.697243 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | particle | 0.6_0.7 | 634 | 0.642536 | 0.965300 | 0.322763 | 0.135973 | 0.458528 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | particle | 0.7_0.8 | 163 | 0.740491 | 1.000000 | 0.259509 | 0.068209 | 0.301223 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | particle | 0.8_0.9 | 22 | 0.846636 | 1.000000 | 0.153364 | 0.024589 | 0.167232 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | particle | 0.9_1.0 | 3 | 0.908667 | 1.000000 | 0.091333 | 0.008354 | 0.095784 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | brownian | 0.0_0.1 | 28 | 0.058245 | 0.000000 | -0.058245 | 0.003962 | 0.060327 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | brownian | 0.1_0.2 | 33 | 0.147484 | 0.000000 | -0.147484 | 0.022940 | 0.160389 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | brownian | 0.2_0.3 | 70 | 0.247864 | 0.000000 | -0.247864 | 0.062102 | 0.285429 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | brownian | 0.3_0.4 | 540 | 0.351010 | 0.000000 | -0.351010 | 0.123791 | 0.433027 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | brownian | 0.4_0.5 | 739 | 0.477699 | 0.108254 | -0.369444 | 0.229109 | 0.651250 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | brownian | 0.5_0.6 | 1267 | 0.538769 | 0.404104 | -0.134665 | 0.251661 | 0.696441 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | brownian | 0.6_0.7 | 648 | 0.643684 | 0.966049 | 0.322366 | 0.135099 | 0.456671 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | brownian | 0.7_0.8 | 151 | 0.742212 | 1.000000 | 0.257788 | 0.067254 | 0.298842 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | brownian | 0.8_0.9 | 22 | 0.847602 | 1.000000 | 0.152398 | 0.024191 | 0.166021 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | brownian | 0.9_1.0 | 3 | 0.908427 | 1.000000 | 0.091573 | 0.008402 | 0.096051 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | market | 0.0_0.1 | 329 | 0.040775 | 0.000000 | -0.040775 | 0.002726 | 0.042210 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | market | 0.1_0.2 | 219 | 0.138858 | 0.000000 | -0.138858 | 0.019945 | 0.149948 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | market | 0.2_0.3 | 111 | 0.242432 | 0.000000 | -0.242432 | 0.059609 | 0.278383 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | market | 0.3_0.4 | 68 | 0.344118 | 0.000000 | -0.344118 | 0.119360 | 0.422877 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | market | 0.4_0.5 | 395 | 0.457430 | 0.063291 | -0.394139 | 0.211543 | 0.615842 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | market | 0.5_0.6 | 670 | 0.550858 | 0.211940 | -0.338918 | 0.280950 | 0.755493 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | market | 0.6_0.7 | 570 | 0.647553 | 0.392982 | -0.254570 | 0.297315 | 0.791210 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | market | 0.7_0.8 | 277 | 0.738520 | 0.729242 | -0.009278 | 0.197251 | 0.583677 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | market | 0.8_0.9 | 309 | 0.854693 | 0.802589 | -0.052104 | 0.150946 | 0.467156 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | market | 0.9_1.0 | 553 | 0.968445 | 1.000000 | 0.031555 | 0.001794 | 0.032496 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | current_calibrated | 0.0_0.1 | 130 | 0.038354 | 0.000000 | -0.038354 | 0.002444 | 0.039640 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | current_calibrated | 0.1_0.2 | 530 | 0.150375 | 0.000000 | -0.150375 | 0.023292 | 0.163432 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | current_calibrated | 0.2_0.3 | 69 | 0.270999 | 0.000000 | -0.270999 | 0.073740 | 0.316362 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | current_calibrated | 0.3_0.4 | 90 | 0.383512 | 0.000000 | -0.383512 | 0.147411 | 0.484135 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | current_calibrated | 0.4_0.5 | 507 | 0.453469 | 0.043393 | -0.410076 | 0.206952 | 0.606544 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | current_calibrated | 0.5_0.6 | 660 | 0.549784 | 0.337879 | -0.211905 | 0.268531 | 0.730448 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | current_calibrated | 0.6_0.7 | 334 | 0.652889 | 0.362275 | -0.290614 | 0.306950 | 0.811470 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | current_calibrated | 0.7_0.8 | 234 | 0.734472 | 0.747863 | 0.013391 | 0.191497 | 0.572902 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | current_calibrated | 0.8_0.9 | 313 | 0.852884 | 0.699681 | -0.153204 | 0.231622 | 0.681415 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | current_calibrated | 0.9_1.0 | 634 | 0.914092 | 1.000000 | 0.085908 | 0.007900 | 0.090126 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | particle | 0.2_0.3 | 7 | 0.292071 | 1.000000 | 0.707929 | 0.501179 | 1.230850 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | particle | 0.3_0.4 | 162 | 0.362593 | 0.783951 | 0.421358 | 0.357107 | 0.915586 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | particle | 0.4_0.5 | 1095 | 0.459444 | 0.863927 | 0.404483 | 0.281464 | 0.756422 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | particle | 0.5_0.6 | 1139 | 0.537480 | 0.937665 | 0.400185 | 0.215854 | 0.624512 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | particle | 0.6_0.7 | 541 | 0.645559 | 1.000000 | 0.354441 | 0.126366 | 0.438523 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | particle | 0.7_0.8 | 257 | 0.736516 | 1.000000 | 0.263484 | 0.070310 | 0.306626 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | particle | 0.8_0.9 | 202 | 0.840851 | 1.000000 | 0.159149 | 0.026151 | 0.173917 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | particle | 0.9_1.0 | 11 | 0.915409 | 1.000000 | 0.084591 | 0.007897 | 0.088804 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | brownian | 0.2_0.3 | 4 | 0.299350 | 1.000000 | 0.700650 | 0.490911 | 1.206143 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | brownian | 0.3_0.4 | 140 | 0.356173 | 0.742857 | 0.386684 | 0.356848 | 0.916408 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | brownian | 0.4_0.5 | 1128 | 0.459808 | 0.845745 | 0.385937 | 0.281785 | 0.757086 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | brownian | 0.5_0.6 | 1103 | 0.535481 | 0.959202 | 0.423721 | 0.217034 | 0.626926 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | brownian | 0.6_0.7 | 571 | 0.643706 | 1.000000 | 0.356294 | 0.127706 | 0.441432 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | brownian | 0.7_0.8 | 247 | 0.734172 | 1.000000 | 0.265828 | 0.071454 | 0.309728 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | brownian | 0.8_0.9 | 213 | 0.840064 | 1.000000 | 0.159936 | 0.026406 | 0.174857 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | brownian | 0.9_1.0 | 8 | 0.918834 | 1.000000 | 0.081166 | 0.007552 | 0.085195 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | market | 0.0_0.1 | 143 | 0.072028 | 0.958042 | 0.886014 | 0.820810 | 2.505823 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | market | 0.1_0.2 | 145 | 0.154931 | 0.917241 | 0.762310 | 0.660674 | 1.755859 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | market | 0.2_0.3 | 205 | 0.255049 | 0.760976 | 0.505927 | 0.439817 | 1.117927 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | market | 0.3_0.4 | 295 | 0.347610 | 0.891525 | 0.543915 | 0.388477 | 0.980498 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | market | 0.4_0.5 | 310 | 0.463806 | 0.793548 | 0.329742 | 0.269192 | 0.731645 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | market | 0.5_0.6 | 449 | 0.543107 | 0.817372 | 0.274265 | 0.227165 | 0.647276 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | market | 0.6_0.7 | 383 | 0.646593 | 0.973890 | 0.327298 | 0.131007 | 0.447797 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | market | 0.7_0.8 | 368 | 0.745421 | 1.000000 | 0.254579 | 0.065499 | 0.294423 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | market | 0.8_0.9 | 199 | 0.859397 | 1.000000 | 0.140603 | 0.020638 | 0.152120 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | market | 0.9_1.0 | 917 | 0.963081 | 1.000000 | 0.036919 | 0.002320 | 0.038141 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | current_calibrated | 0.0_0.1 | 54 | 0.070155 | 1.000000 | 0.929845 | 0.865070 | 2.709863 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | current_calibrated | 0.1_0.2 | 213 | 0.164604 | 0.676056 | 0.511452 | 0.479369 | 1.283755 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | current_calibrated | 0.2_0.3 | 211 | 0.257492 | 0.943128 | 0.685636 | 0.524215 | 1.300310 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | current_calibrated | 0.3_0.4 | 318 | 0.353676 | 0.893082 | 0.539406 | 0.390500 | 0.984643 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | current_calibrated | 0.4_0.5 | 510 | 0.466480 | 0.815686 | 0.349206 | 0.273851 | 0.741105 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | current_calibrated | 0.5_0.6 | 468 | 0.552276 | 0.920940 | 0.368664 | 0.203372 | 0.599247 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | current_calibrated | 0.6_0.7 | 284 | 0.649812 | 0.968310 | 0.318498 | 0.131056 | 0.447549 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | current_calibrated | 0.7_0.8 | 216 | 0.732715 | 1.000000 | 0.267285 | 0.072003 | 0.311512 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | current_calibrated | 0.8_0.9 | 304 | 0.844481 | 1.000000 | 0.155519 | 0.024796 | 0.169457 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | current_calibrated | 0.9_1.0 | 836 | 0.957267 | 1.000000 | 0.042733 | 0.002724 | 0.044165 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | particle | 0.0_0.1 | 418 | 0.045201 | 0.000000 | -0.045201 | 0.002685 | 0.046611 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | particle | 0.1_0.2 | 387 | 0.149948 | 0.000000 | -0.149948 | 0.023219 | 0.162969 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | particle | 0.2_0.3 | 293 | 0.260561 | 0.000000 | -0.260561 | 0.068745 | 0.302634 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | particle | 0.3_0.4 | 478 | 0.348043 | 0.000000 | -0.348043 | 0.121974 | 0.428770 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | particle | 0.4_0.5 | 573 | 0.446710 | 0.000000 | -0.446710 | 0.200271 | 0.593059 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | particle | 0.5_0.6 | 349 | 0.539656 | 0.240688 | -0.298968 | 0.258659 | 0.710397 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | particle | 0.6_0.7 | 309 | 0.656969 | 0.964401 | 0.307432 | 0.127046 | 0.438383 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | particle | 0.7_0.8 | 233 | 0.744032 | 0.995708 | 0.251676 | 0.068288 | 0.300377 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | particle | 0.8_0.9 | 150 | 0.859840 | 1.000000 | 0.140160 | 0.020313 | 0.151466 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | particle | 0.9_1.0 | 70 | 0.926486 | 1.000000 | 0.073514 | 0.005864 | 0.076621 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | brownian | 0.0_0.1 | 421 | 0.045583 | 0.000000 | -0.045583 | 0.002736 | 0.047020 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | brownian | 0.1_0.2 | 382 | 0.150450 | 0.000000 | -0.150450 | 0.023312 | 0.163519 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | brownian | 0.2_0.3 | 279 | 0.258966 | 0.000000 | -0.258966 | 0.067940 | 0.300496 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | brownian | 0.3_0.4 | 495 | 0.346764 | 0.000000 | -0.346764 | 0.121121 | 0.426851 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | brownian | 0.4_0.5 | 569 | 0.446339 | 0.000000 | -0.446339 | 0.199902 | 0.592328 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | brownian | 0.5_0.6 | 338 | 0.536247 | 0.210059 | -0.326187 | 0.260571 | 0.714244 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | brownian | 0.6_0.7 | 319 | 0.655119 | 0.959248 | 0.304129 | 0.129994 | 0.444598 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | brownian | 0.7_0.8 | 238 | 0.742244 | 1.000000 | 0.257756 | 0.067518 | 0.299053 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | brownian | 0.8_0.9 | 146 | 0.859962 | 1.000000 | 0.140038 | 0.020223 | 0.151287 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | brownian | 0.9_1.0 | 73 | 0.924242 | 1.000000 | 0.075758 | 0.006168 | 0.079029 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | market | 0.0_0.1 | 851 | 0.029718 | 0.000000 | -0.029718 | 0.001569 | 0.030537 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | market | 0.1_0.2 | 194 | 0.150619 | 0.000000 | -0.150619 | 0.023438 | 0.163767 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | market | 0.2_0.3 | 386 | 0.259547 | 0.000000 | -0.259547 | 0.067984 | 0.301052 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | market | 0.3_0.4 | 382 | 0.349306 | 0.000000 | -0.349306 | 0.122821 | 0.430671 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | market | 0.4_0.5 | 312 | 0.435112 | 0.000000 | -0.435112 | 0.189966 | 0.572155 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | market | 0.5_0.6 | 219 | 0.543425 | 0.000000 | -0.543425 | 0.295908 | 0.785432 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | market | 0.6_0.7 | 174 | 0.655402 | 0.586207 | -0.069195 | 0.240816 | 0.674483 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | market | 0.7_0.8 | 152 | 0.738816 | 0.934211 | 0.195395 | 0.098797 | 0.368331 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | market | 0.8_0.9 | 100 | 0.853050 | 1.000000 | 0.146950 | 0.022219 | 0.159372 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | market | 0.9_1.0 | 490 | 0.961276 | 1.000000 | 0.038724 | 0.002727 | 0.040167 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | current_calibrated | 0.0_0.1 | 1198 | 0.023303 | 0.000000 | -0.023303 | 0.001343 | 0.024008 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | current_calibrated | 0.1_0.2 | 224 | 0.145461 | 0.000000 | -0.145461 | 0.021906 | 0.157707 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | current_calibrated | 0.2_0.3 | 306 | 0.253617 | 0.000000 | -0.253617 | 0.065143 | 0.293252 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | current_calibrated | 0.3_0.4 | 263 | 0.351740 | 0.000000 | -0.351740 | 0.124657 | 0.434576 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | current_calibrated | 0.4_0.5 | 173 | 0.448640 | 0.000000 | -0.448640 | 0.202300 | 0.597051 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | current_calibrated | 0.5_0.6 | 152 | 0.550720 | 0.000000 | -0.550720 | 0.303913 | 0.801633 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | current_calibrated | 0.6_0.7 | 91 | 0.649040 | 0.373626 | -0.275414 | 0.298467 | 0.792407 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | current_calibrated | 0.7_0.8 | 144 | 0.756362 | 0.659722 | -0.096640 | 0.239654 | 0.680515 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | current_calibrated | 0.8_0.9 | 120 | 0.828629 | 0.966667 | 0.138037 | 0.051994 | 0.241964 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | current_calibrated | 0.9_1.0 | 589 | 0.975412 | 1.000000 | 0.024588 | 0.001143 | 0.025183 |
| particle_residual_blend_oos_RESIDLOCK001 | particle | 0.0_0.1 | 65 | 0.065008 | 0.000000 | -0.065008 | 0.004889 | 0.067595 |
| particle_residual_blend_oos_RESIDLOCK001 | particle | 0.1_0.2 | 65 | 0.140962 | 0.000000 | -0.140962 | 0.020630 | 0.152455 |
| particle_residual_blend_oos_RESIDLOCK001 | particle | 0.2_0.3 | 269 | 0.265602 | 0.011152 | -0.254450 | 0.075547 | 0.318749 |
| particle_residual_blend_oos_RESIDLOCK001 | particle | 0.3_0.4 | 740 | 0.357525 | 0.633784 | 0.276259 | 0.297572 | 0.790568 |
| particle_residual_blend_oos_RESIDLOCK001 | particle | 0.4_0.5 | 1226 | 0.451321 | 0.944535 | 0.493214 | 0.295833 | 0.785385 |
| particle_residual_blend_oos_RESIDLOCK001 | particle | 0.5_0.6 | 365 | 0.539522 | 0.816438 | 0.276916 | 0.231645 | 0.656325 |
| particle_residual_blend_oos_RESIDLOCK001 | particle | 0.6_0.7 | 185 | 0.655900 | 0.972973 | 0.317073 | 0.124927 | 0.434317 |
| particle_residual_blend_oos_RESIDLOCK001 | particle | 0.7_0.8 | 183 | 0.743224 | 1.000000 | 0.256776 | 0.066840 | 0.297568 |
| particle_residual_blend_oos_RESIDLOCK001 | particle | 0.8_0.9 | 158 | 0.849759 | 1.000000 | 0.150241 | 0.023630 | 0.163536 |
| particle_residual_blend_oos_RESIDLOCK001 | particle | 0.9_1.0 | 102 | 0.952127 | 1.000000 | 0.047873 | 0.003338 | 0.049633 |
| particle_residual_blend_oos_RESIDLOCK001 | brownian | 0.0_0.1 | 63 | 0.065602 | 0.000000 | -0.065602 | 0.004988 | 0.068244 |
| particle_residual_blend_oos_RESIDLOCK001 | brownian | 0.1_0.2 | 67 | 0.138109 | 0.000000 | -0.138109 | 0.019828 | 0.149131 |
| particle_residual_blend_oos_RESIDLOCK001 | brownian | 0.2_0.3 | 259 | 0.265624 | 0.000000 | -0.265624 | 0.070919 | 0.309067 |
| particle_residual_blend_oos_RESIDLOCK001 | brownian | 0.3_0.4 | 749 | 0.356518 | 0.619493 | 0.262975 | 0.294228 | 0.783671 |
| particle_residual_blend_oos_RESIDLOCK001 | brownian | 0.4_0.5 | 1268 | 0.453255 | 0.954259 | 0.501004 | 0.294860 | 0.783413 |
| particle_residual_blend_oos_RESIDLOCK001 | brownian | 0.5_0.6 | 332 | 0.544808 | 0.774096 | 0.229289 | 0.231547 | 0.656164 |
| particle_residual_blend_oos_RESIDLOCK001 | brownian | 0.6_0.7 | 172 | 0.656825 | 1.000000 | 0.343175 | 0.118379 | 0.421047 |
| particle_residual_blend_oos_RESIDLOCK001 | brownian | 0.7_0.8 | 178 | 0.739995 | 1.000000 | 0.260005 | 0.068372 | 0.301803 |
| particle_residual_blend_oos_RESIDLOCK001 | brownian | 0.8_0.9 | 175 | 0.848689 | 1.000000 | 0.151311 | 0.024085 | 0.164891 |
| particle_residual_blend_oos_RESIDLOCK001 | brownian | 0.9_1.0 | 95 | 0.956223 | 1.000000 | 0.043777 | 0.002842 | 0.045271 |
| particle_residual_blend_oos_RESIDLOCK001 | market | 0.0_0.1 | 247 | 0.038279 | 0.000000 | -0.038279 | 0.002781 | 0.039752 |
| particle_residual_blend_oos_RESIDLOCK001 | market | 0.1_0.2 | 242 | 0.150702 | 0.152893 | 0.002190 | 0.133469 | 0.442788 |
| particle_residual_blend_oos_RESIDLOCK001 | market | 0.2_0.3 | 578 | 0.260614 | 0.676471 | 0.415856 | 0.384800 | 0.989960 |
| particle_residual_blend_oos_RESIDLOCK001 | market | 0.3_0.4 | 607 | 0.348822 | 0.899506 | 0.550684 | 0.391019 | 0.985809 |
| particle_residual_blend_oos_RESIDLOCK001 | market | 0.4_0.5 | 673 | 0.447771 | 0.945022 | 0.497251 | 0.301797 | 0.797546 |
| particle_residual_blend_oos_RESIDLOCK001 | market | 0.5_0.6 | 269 | 0.544740 | 0.802974 | 0.258234 | 0.233531 | 0.660163 |
| particle_residual_blend_oos_RESIDLOCK001 | market | 0.6_0.7 | 103 | 0.643447 | 0.834951 | 0.191505 | 0.168273 | 0.524429 |
| particle_residual_blend_oos_RESIDLOCK001 | market | 0.7_0.8 | 63 | 0.755873 | 1.000000 | 0.244127 | 0.060182 | 0.280393 |
| particle_residual_blend_oos_RESIDLOCK001 | market | 0.8_0.9 | 126 | 0.852659 | 1.000000 | 0.147341 | 0.022353 | 0.159839 |
| particle_residual_blend_oos_RESIDLOCK001 | market | 0.9_1.0 | 450 | 0.966178 | 1.000000 | 0.033822 | 0.002108 | 0.034933 |
| particle_residual_blend_oos_RESIDLOCK001 | current_calibrated | 0.0_0.1 | 303 | 0.056539 | 0.000000 | -0.056539 | 0.004397 | 0.058871 |
| particle_residual_blend_oos_RESIDLOCK001 | current_calibrated | 0.1_0.2 | 450 | 0.159198 | 0.386667 | 0.227468 | 0.282120 | 0.794544 |
| particle_residual_blend_oos_RESIDLOCK001 | current_calibrated | 0.2_0.3 | 417 | 0.242082 | 0.772182 | 0.530100 | 0.455343 | 1.157553 |
| particle_residual_blend_oos_RESIDLOCK001 | current_calibrated | 0.3_0.4 | 545 | 0.356493 | 0.937615 | 0.581122 | 0.394031 | 0.991232 |
| particle_residual_blend_oos_RESIDLOCK001 | current_calibrated | 0.4_0.5 | 615 | 0.449587 | 0.951220 | 0.501632 | 0.300336 | 0.794568 |
| particle_residual_blend_oos_RESIDLOCK001 | current_calibrated | 0.5_0.6 | 262 | 0.544930 | 0.916031 | 0.371100 | 0.211166 | 0.614908 |
| particle_residual_blend_oos_RESIDLOCK001 | current_calibrated | 0.6_0.7 | 141 | 0.641127 | 0.666667 | 0.025540 | 0.227752 | 0.648541 |
| particle_residual_blend_oos_RESIDLOCK001 | current_calibrated | 0.7_0.8 | 61 | 0.760901 | 1.000000 | 0.239099 | 0.057880 | 0.273875 |
| particle_residual_blend_oos_RESIDLOCK001 | current_calibrated | 0.8_0.9 | 162 | 0.855023 | 1.000000 | 0.144977 | 0.022049 | 0.157337 |
| particle_residual_blend_oos_RESIDLOCK001 | current_calibrated | 0.9_1.0 | 402 | 0.962180 | 1.000000 | 0.037820 | 0.002423 | 0.039098 |
