# v28 Hybrid/Boundary Entry Stack

Research-only: combined hybrid-veto, boundary-clock, and early-NO repair scorecard.

- Generated UTC: `2026-05-10T02:42:45.995846+00:00`
- Stack freeze UTC: `2026-05-06T15:37:04.750154+00:00`
- Coverage floor: `75.0`

## Interpretation

- Research-only: this writes scorecards only and does not change live entries.
- Promotion requires post-freeze rows, positive net, 75-90% coverage, source-quality proof, and full-loss cushion.
- diagnostic_existing_target_window: best all_three_with_boundary_fv_edge_approved_first_hybrid_edge_repair has 114 settled, coverage 75.0%, net 803.0c, blockers ['reconstructed_share_gt_35pct'].
- post_stack_freeze_window: best hybrid_veto_plus_boundary_clock_approved_only_hybrid_edge_repair has 41 settled, coverage 47.12643678160919%, net 312.0c, blockers ['coverage_too_low', 'reconstructed_share_gt_35pct'].

## diagnostic_existing_target_window

- Freeze UTC: `2026-05-05T23:30:17.615882+00:00`
- Forward denominator: `152`

| rank | candidate | repairs | coverage | net c | delta c | W/L | recon share | loss cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | all_three_with_boundary_fv_edge_approved_first_hybrid_edge_repair | 71 | 75.000000 | 803.000000 | 1409.000000 | 83/31 | 0.500000 | 8 | reconstructed_share_gt_35pct |
| 2 | all_three_with_boundary_fv_edge_approved_first_raw_clean_repair | 71 | 75.000000 | 769.000000 | 1375.000000 | 83/31 | 0.500000 | 7 | reconstructed_share_gt_35pct |
| 3 | early_no_plus_boundary_clock_approved_first_hybrid_edge_repair | 67 | 75.000000 | 731.000000 | 1337.000000 | 82/32 | 0.526316 | 7 | reconstructed_share_gt_35pct |
| 4 | early_no_plus_boundary_clock_approved_first_raw_clean_repair | 67 | 75.000000 | 697.000000 | 1303.000000 | 82/32 | 0.526316 | 6 | reconstructed_share_gt_35pct |
| 5 | all_three_without_boundary_fv_edge_approved_first_hybrid_edge_repair | 70 | 75.000000 | 641.000000 | 1247.000000 | 82/32 | 0.508772 | 6 | reconstructed_share_gt_35pct |
| 6 | all_three_without_boundary_fv_edge_approved_first_raw_clean_repair | 70 | 75.000000 | 607.000000 | 1213.000000 | 82/32 | 0.508772 | 6 | reconstructed_share_gt_35pct |
| 7 | hybrid_veto_plus_early_no_approved_first_hybrid_edge_repair | 65 | 75.000000 | 596.000000 | 1202.000000 | 82/32 | 0.517544 | 5 | reconstructed_share_gt_35pct |
| 8 | hybrid_veto_plus_early_no_approved_first_raw_clean_repair | 65 | 75.000000 | 567.000000 | 1173.000000 | 82/32 | 0.526316 | 5 | reconstructed_share_gt_35pct |
| 9 | all_three_with_boundary_fv_edge_hybrid_edge_repair | 71 | 75.000000 | 504.000000 | 1110.000000 | 79/35 | 0.535088 | 5 | reconstructed_share_gt_35pct |
| 10 | early_no_plus_boundary_clock_raw_clean_repair | 67 | 75.000000 | 469.000000 | 1075.000000 | 78/36 | 0.578947 | 4 | reconstructed_share_gt_35pct |
| 11 | all_three_with_boundary_fv_edge_raw_clean_repair | 71 | 75.000000 | 441.000000 | 1047.000000 | 78/36 | 0.552632 | 4 | reconstructed_share_gt_35pct |
| 12 | hybrid_veto_plus_early_no_hybrid_edge_repair | 65 | 75.000000 | 433.000000 | 1039.000000 | 78/36 | 0.578947 | 4 | reconstructed_share_gt_35pct |
| 13 | early_no_plus_boundary_clock_hybrid_edge_repair | 67 | 75.000000 | 431.000000 | 1037.000000 | 78/36 | 0.561404 | 4 | reconstructed_share_gt_35pct |
| 14 | hybrid_veto_plus_early_no_raw_clean_repair | 65 | 75.000000 | 367.000000 | 973.000000 | 77/37 | 0.596491 | 3 | reconstructed_share_gt_35pct |
| 15 | all_three_without_boundary_fv_edge_hybrid_edge_repair | 70 | 75.000000 | 342.000000 | 948.000000 | 78/36 | 0.543860 | 3 | reconstructed_share_gt_35pct |
| 16 | hybrid_veto_plus_boundary_clock_approved_first_raw_clean_repair | 62 | 75.000000 | 307.000000 | 913.000000 | 81/33 | 0.552632 | 3 | reconstructed_share_gt_35pct |
| 17 | early_no_plus_boundary_clock_approved_only_hybrid_edge_repair | 15 | 40.789474 | 759.000000 | 1365.000000 | 46/16 | 0.645161 | 7 | coverage_too_low, reconstructed_share_gt_35pct |
| 18 | early_no_plus_boundary_clock_approved_only_raw_clean_repair | 15 | 40.789474 | 759.000000 | 1365.000000 | 46/16 | 0.645161 | 7 | coverage_too_low, reconstructed_share_gt_35pct |
| 19 | early_no_plus_boundary_clock_source_cap35_hybrid_edge_repair | 15 | 40.789474 | 759.000000 | 1365.000000 | 46/16 | 0.645161 | 7 | coverage_too_low, reconstructed_share_gt_35pct |
| 20 | early_no_plus_boundary_clock_source_cap35_raw_clean_repair | 15 | 40.789474 | 759.000000 | 1365.000000 | 46/16 | 0.645161 | 7 | coverage_too_low, reconstructed_share_gt_35pct |
| 21 | all_three_with_boundary_fv_edge_approved_only_hybrid_edge_repair | 15 | 38.157895 | 700.000000 | 1306.000000 | 43/15 | 0.620690 | 7 | coverage_too_low, reconstructed_share_gt_35pct |
| 22 | all_three_with_boundary_fv_edge_approved_only_raw_clean_repair | 15 | 38.157895 | 700.000000 | 1306.000000 | 43/15 | 0.620690 | 7 | coverage_too_low, reconstructed_share_gt_35pct |
| 23 | all_three_with_boundary_fv_edge_source_cap35_hybrid_edge_repair | 15 | 38.157895 | 700.000000 | 1306.000000 | 43/15 | 0.620690 | 7 | coverage_too_low, reconstructed_share_gt_35pct |
| 24 | all_three_with_boundary_fv_edge_source_cap35_raw_clean_repair | 15 | 38.157895 | 700.000000 | 1306.000000 | 43/15 | 0.620690 | 7 | coverage_too_low, reconstructed_share_gt_35pct |
| 25 | hybrid_veto_plus_early_no_approved_only_hybrid_edge_repair | 15 | 42.105263 | 614.000000 | 1220.000000 | 46/18 | 0.656250 | 6 | coverage_too_low, reconstructed_share_gt_35pct |
| 26 | hybrid_veto_plus_early_no_approved_only_raw_clean_repair | 15 | 42.105263 | 614.000000 | 1220.000000 | 46/18 | 0.656250 | 6 | coverage_too_low, reconstructed_share_gt_35pct |
| 27 | hybrid_veto_plus_early_no_source_cap35_hybrid_edge_repair | 15 | 42.105263 | 614.000000 | 1220.000000 | 46/18 | 0.656250 | 6 | coverage_too_low, reconstructed_share_gt_35pct |
| 28 | hybrid_veto_plus_early_no_source_cap35_raw_clean_repair | 15 | 42.105263 | 614.000000 | 1220.000000 | 46/18 | 0.656250 | 6 | coverage_too_low, reconstructed_share_gt_35pct |
| 29 | all_three_without_boundary_fv_edge_approved_only_hybrid_edge_repair | 15 | 38.815789 | 594.000000 | 1200.000000 | 43/16 | 0.627119 | 5 | coverage_too_low, reconstructed_share_gt_35pct |
| 30 | all_three_without_boundary_fv_edge_approved_only_raw_clean_repair | 15 | 38.815789 | 594.000000 | 1200.000000 | 43/16 | 0.627119 | 5 | coverage_too_low, reconstructed_share_gt_35pct |
| 31 | all_three_without_boundary_fv_edge_source_cap35_hybrid_edge_repair | 15 | 38.815789 | 594.000000 | 1200.000000 | 43/16 | 0.627119 | 5 | coverage_too_low, reconstructed_share_gt_35pct |
| 32 | all_three_without_boundary_fv_edge_source_cap35_raw_clean_repair | 15 | 38.815789 | 594.000000 | 1200.000000 | 43/16 | 0.627119 | 5 | coverage_too_low, reconstructed_share_gt_35pct |
| 33 | hybrid_veto_plus_boundary_clock_approved_only_hybrid_edge_repair | 15 | 44.078947 | 304.000000 | 910.000000 | 46/21 | 0.671642 | 3 | coverage_too_low, reconstructed_share_gt_35pct |
| 34 | hybrid_veto_plus_boundary_clock_approved_only_raw_clean_repair | 15 | 44.078947 | 304.000000 | 910.000000 | 46/21 | 0.671642 | 3 | coverage_too_low, reconstructed_share_gt_35pct |
| 35 | hybrid_veto_plus_boundary_clock_source_cap35_hybrid_edge_repair | 15 | 44.078947 | 304.000000 | 910.000000 | 46/21 | 0.671642 | 3 | coverage_too_low, reconstructed_share_gt_35pct |
| 36 | hybrid_veto_plus_boundary_clock_source_cap35_raw_clean_repair | 15 | 44.078947 | 304.000000 | 910.000000 | 46/21 | 0.671642 | 3 | coverage_too_low, reconstructed_share_gt_35pct |
| 37 | hybrid_veto_plus_boundary_clock_approved_first_hybrid_edge_repair | 62 | 75.000000 | 282.000000 | 888.000000 | 80/34 | 0.552632 | 2 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 38 | all_three_without_boundary_fv_edge_raw_clean_repair | 70 | 75.000000 | 279.000000 | 885.000000 | 77/37 | 0.561404 | 2 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 39 | hybrid_veto_plus_boundary_clock_raw_clean_repair | 62 | 75.000000 | 190.000000 | 796.000000 | 77/37 | 0.614035 | 1 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 40 | hybrid_veto_plus_boundary_clock_hybrid_edge_repair | 62 | 75.000000 | 86.000000 | 692.000000 | 76/38 | 0.605263 | 0 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

### Best Candidate Repairs

| market | source | side | won | net c | raw p | hybrid p | ask | raw edge | hybrid edge | recross | abs d | score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.963659 | 0.952539 | 0.700000 | 0.263659 | 0.252539 | 0.073753 | 1.543579 | 1.531676 |
| KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 25.000000 | 0.942571 | 0.936858 | 0.730000 | 0.212571 | 0.206858 | 0.239053 | 1.308547 | 1.398305 |
| KXBTC15M-26MAY061000-00 | approved_entry | no | True | 31.000000 | 0.854748 | 0.836415 | 0.650000 | 0.204748 | 0.186415 | 0.586664 | 0.901711 | 1.211980 |
| KXBTC15M-26MAY060745-45 | approved_entry | yes | False | -71.000000 | 0.851843 | 0.846082 | 0.690000 | 0.161843 | 0.156082 | 0.303224 | 0.889718 | 1.179914 |
| KXBTC15M-26MAY060900-00 | approved_entry | no | True | 25.000000 | 0.855256 | 0.852463 | 0.730000 | 0.125256 | 0.122463 | 0.145613 | 0.858522 | 1.129363 |
| KXBTC15M-26MAY071000-00 | approved_entry | no | True | 27.000000 | 0.851825 | 0.842628 | 0.710000 | 0.141825 | 0.132628 | 0.484111 | 0.895147 | 1.116211 |
| KXBTC15M-26MAY071045-45 | approved_entry | no | True | 22.000000 | 0.865260 | 0.855991 | 0.750000 | 0.115260 | 0.105991 | 0.469918 | 0.953688 | 1.080382 |
| KXBTC15M-26MAY060615-15 | approved_entry | yes | True | 23.000000 | 0.852040 | 0.845798 | 0.750000 | 0.102040 | 0.095798 | 0.328333 | 0.888798 | 1.057129 |
| KXBTC15M-26MAY060700-00 | approved_entry | yes | True | 23.000000 | 0.852084 | 0.841391 | 0.750000 | 0.102084 | 0.091391 | 0.192044 | 0.872216 | 1.055094 |
| KXBTC15M-26MAY071315-15 | approved_entry | yes | True | 20.000000 | 0.850827 | 0.848318 | 0.780000 | 0.070827 | 0.068318 | 0.132426 | 0.850077 | 1.017492 |
| KXBTC15M-26MAY060715-15 | approved_entry | yes | True | 17.000000 | 0.872115 | 0.865418 | 0.810000 | 0.062115 | 0.055418 | 0.333271 | 0.965012 | 0.999518 |
| KXBTC15M-26MAY060815-15 | approved_entry | no | True | 18.000000 | 0.860153 | 0.852470 | 0.790000 | 0.070153 | 0.062470 | 0.395024 | 0.900687 | 0.992764 |
| KXBTC15M-26MAY061300-00 | approved_entry | yes | False | -82.000000 | 0.860906 | 0.855026 | 0.800000 | 0.060906 | 0.055026 | 0.301730 | 0.913273 | 0.988072 |
| KXBTC15M-26MAY052200-00 | approved_entry | yes | True | 19.000000 | 0.850777 | 0.843118 | 0.790000 | 0.060777 | 0.053118 | 0.404344 | 0.880811 | 0.962962 |
| KXBTC15M-26MAY070930-30 | approved_entry | yes | True | 17.000000 | 0.855936 | 0.848715 | 0.800000 | 0.055936 | 0.048715 | 0.375669 | 0.878792 | 0.961838 |
| KXBTC15M-26MAY052045-45 | rejected_actionable | yes | False | -73.000000 | 0.819741 | 0.811603 | 0.700000 | 0.119741 | 0.111603 | 0.100982 | 0.766279 | 1.067078 |
| KXBTC15M-26MAY071215-15 | rejected_actionable | yes | False | -75.000000 | 0.828282 | 0.813070 | 0.720000 | 0.108282 | 0.093070 | 0.487740 | 0.790551 | 1.003522 |
| KXBTC15M-26MAY061530-30 | rejected_actionable | yes | True | 56.000000 | 0.608780 | 0.602430 | 0.400000 | 0.208780 | 0.202430 | 0.228156 | 0.226282 | 1.001938 |
| KXBTC15M-26MAY060315-15 | rejected_actionable | yes | True | 16.000000 | 0.854395 | 0.851273 | 0.810000 | 0.044395 | 0.041273 | 0.163136 | 0.837534 | 0.963425 |
| KXBTC15M-26MAY060115-15 | rejected_actionable | no | True | 24.000000 | 0.819858 | 0.796866 | 0.730000 | 0.089858 | 0.066866 | 0.405225 | 0.766642 | 0.942260 |
| KXBTC15M-26MAY071100-00 | rejected_actionable | yes | False | -84.000000 | 0.853486 | 0.847004 | 0.810000 | 0.043486 | 0.037004 | 0.339564 | 0.906587 | 0.940798 |
| KXBTC15M-26MAY071330-30 | rejected_actionable | no | True | 16.000000 | 0.864780 | 0.849769 | 0.820000 | 0.044780 | 0.029769 | 0.391694 | 0.927901 | 0.928119 |
| KXBTC15M-26MAY060230-30 | rejected_actionable | yes | True | 16.000000 | 0.830361 | 0.819240 | 0.810000 | 0.020361 | 0.009240 | 0.160401 | 0.775897 | 0.866464 |
| KXBTC15M-26MAY071245-45 | rejected_actionable | yes | False | -53.000000 | 0.636765 | 0.621263 | 0.490000 | 0.146765 | 0.131263 | 0.806353 | 0.350996 | 0.840706 |
| KXBTC15M-26MAY061245-45 | rejected_actionable | no | False | -72.000000 | 0.740496 | 0.715103 | 0.690000 | 0.050496 | 0.025103 | 0.671557 | 0.583513 | 0.747108 |
| KXBTC15M-26MAY060145-45 | rejected_actionable | no | True | 28.000000 | 0.723254 | 0.710452 | 0.690000 | 0.033254 | 0.020452 | 0.477849 | 0.517714 | 0.742215 |
| KXBTC15M-26MAY060015-15 | rejected_actionable | no | True | 40.000000 | 0.643392 | 0.621715 | 0.560000 | 0.083392 | 0.061715 | 0.509785 | 0.322451 | 0.725904 |
| KXBTC15M-26MAY061115-15 | rejected_actionable | yes | False | -72.000000 | 0.727568 | 0.706525 | 0.690000 | 0.037568 | 0.016525 | 0.603892 | 0.509565 | 0.722004 |
| KXBTC15M-26MAY061145-45 | rejected_actionable | yes | False | -74.000000 | 0.732848 | 0.715695 | 0.710000 | 0.022848 | 0.005695 | 0.613876 | 0.535356 | 0.709032 |
| KXBTC15M-26MAY060000-00 | rejected_actionable | no | False | -67.000000 | 0.678147 | 0.656372 | 0.630000 | 0.048147 | 0.026372 | 0.435236 | 0.417064 | 0.700595 |
| KXBTC15M-26MAY061415-15 | rejected_actionable | no | True | 34.000000 | 0.661034 | 0.637102 | 0.620000 | 0.041034 | 0.017102 | 0.655098 | 0.381932 | 0.643979 |
| KXBTC15M-26MAY060330-30 | approved_entry | no | False | -11.000000 | 0.999788 | 0.989716 | 0.090000 | 0.909788 | 0.899716 | 0.002807 | 3.991247 | 2.991005 |
| KXBTC15M-26MAY052245-45 | approved_entry | no | False | -42.000000 | 0.916618 | 0.905106 | 0.400000 | 0.516618 | 0.505106 | 0.141331 | 1.218811 | 1.967830 |
| KXBTC15M-26MAY062015-15 | approved_entry | no | True | 56.000000 | 0.871622 | 0.869728 | 0.420000 | 0.451622 | 0.449728 | 0.094396 | 0.916460 | 1.807928 |
| KXBTC15M-26MAY052100-00 | approved_entry | yes | True | 42.000000 | 0.856314 | 0.851669 | 0.560000 | 0.296314 | 0.291669 | 0.241416 | 0.903393 | 1.462024 |
| KXBTC15M-26MAY062215-15 | approved_entry | no | True | 33.000000 | 0.889241 | 0.874740 | 0.650000 | 0.239241 | 0.224740 | 0.319525 | 1.024084 | 1.353488 |
| KXBTC15M-26MAY060800-00 | approved_entry | yes | True | 32.000000 | 0.874265 | 0.871630 | 0.660000 | 0.214265 | 0.211630 | 0.130377 | 0.931829 | 1.331710 |
| KXBTC15M-26MAY052115-15 | approved_entry | yes | True | 19.000000 | 0.941543 | 0.936415 | 0.780000 | 0.161543 | 0.156415 | 0.215078 | 1.395955 | 1.303118 |
| KXBTC15M-26MAY062045-45 | approved_entry | no | True | 18.000000 | 0.925277 | 0.921141 | 0.800000 | 0.125277 | 0.121141 | 0.180083 | 1.216600 | 1.210881 |
| KXBTC15M-26MAY060515-15 | approved_entry | no | True | 23.000000 | 0.884180 | 0.873939 | 0.740000 | 0.144180 | 0.133939 | 0.123272 | 0.969762 | 1.183004 |
| KXBTC15M-26MAY070945-45 | approved_entry | no | True | 28.000000 | 0.853699 | 0.845363 | 0.690000 | 0.163699 | 0.155363 | 0.436427 | 0.882733 | 1.167397 |
| KXBTC15M-26MAY070030-30 | approved_entry | yes | True | 15.000000 | 0.924288 | 0.920276 | 0.820000 | 0.104288 | 0.100276 | 0.175127 | 1.178593 | 1.166749 |
| KXBTC15M-26MAY061015-15 | approved_entry | no | True | 30.000000 | 0.859312 | 0.840843 | 0.680000 | 0.179312 | 0.160843 | 0.581489 | 0.912125 | 1.166234 |
| KXBTC15M-26MAY060245-45 | approved_entry | yes | True | 21.000000 | 0.877828 | 0.876631 | 0.760000 | 0.117828 | 0.116631 | 0.058673 | 0.931315 | 1.152064 |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.887777 | 0.881414 | 0.760000 | 0.127777 | 0.121414 | 0.303870 | 0.999156 | 1.151481 |
| KXBTC15M-26MAY070830-30 | approved_entry | no | True | 21.000000 | 0.890215 | 0.879743 | 0.770000 | 0.120215 | 0.109743 | 0.126622 | 1.007446 | 1.142088 |
| KXBTC15M-26MAY060300-00 | approved_entry | yes | True | 18.000000 | 0.906682 | 0.896440 | 0.800000 | 0.106682 | 0.096440 | 0.096007 | 1.064322 | 1.137416 |
| KXBTC15M-26MAY060500-00 | approved_entry | yes | True | 18.000000 | 0.904525 | 0.891535 | 0.790000 | 0.114525 | 0.101535 | 0.224287 | 1.081154 | 1.133967 |
| KXBTC15M-26MAY060345-45 | approved_entry | no | True | 19.000000 | 0.893931 | 0.880129 | 0.780000 | 0.113931 | 0.100129 | 0.278461 | 1.004534 | 1.111787 |
| KXBTC15M-26MAY060915-15 | approved_entry | no | True | 28.000000 | 0.850409 | 0.833781 | 0.700000 | 0.150409 | 0.133781 | 0.508413 | 0.894029 | 1.109527 |
| KXBTC15M-26MAY061030-30 | approved_entry | yes | True | 23.000000 | 0.861605 | 0.855264 | 0.740000 | 0.121605 | 0.115264 | 0.324745 | 0.883983 | 1.105596 |
| KXBTC15M-26MAY060930-30 | approved_entry | no | True | 25.000000 | 0.851733 | 0.845013 | 0.730000 | 0.121733 | 0.115013 | 0.353780 | 0.859473 | 1.091391 |
| KXBTC15M-26MAY060530-30 | approved_entry | no | True | 19.000000 | 0.878245 | 0.873071 | 0.780000 | 0.098245 | 0.093071 | 0.253292 | 0.974192 | 1.088954 |
| KXBTC15M-26MAY060830-30 | approved_entry | yes | True | 21.000000 | 0.873796 | 0.860121 | 0.760000 | 0.113796 | 0.100121 | 0.307137 | 0.951357 | 1.086777 |
| KXBTC15M-26MAY071200-00 | approved_entry | no | True | 20.000000 | 0.859141 | 0.857405 | 0.770000 | 0.089141 | 0.087405 | 0.089529 | 0.918677 | 1.071420 |
| KXBTC15M-26MAY060215-15 | approved_entry | yes | False | -79.000000 | 0.869074 | 0.854439 | 0.770000 | 0.099074 | 0.084439 | 0.363966 | 0.921532 | 1.043934 |
| KXBTC15M-26MAY060100-00 | approved_entry | no | True | 20.000000 | 0.867914 | 0.855980 | 0.780000 | 0.087914 | 0.075980 | 0.230298 | 0.923286 | 1.038665 |
| KXBTC15M-26MAY060645-45 | approved_entry | yes | True | 20.000000 | 0.868675 | 0.855296 | 0.780000 | 0.088675 | 0.075296 | 0.301671 | 0.943313 | 1.032264 |
| KXBTC15M-26MAY071230-30 | approved_entry | yes | True | 21.000000 | 0.852419 | 0.846785 | 0.770000 | 0.082419 | 0.076785 | 0.296037 | 0.882196 | 1.022191 |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.861092 | 0.852949 | 0.780000 | 0.081092 | 0.072949 | 0.417623 | 0.936079 | 1.014276 |
| KXBTC15M-26MAY061130-30 | approved_entry | yes | True | 17.000000 | 0.877418 | 0.866487 | 0.800000 | 0.077418 | 0.066487 | 0.536330 | 0.989346 | 1.008755 |
| KXBTC15M-26MAY071030-30 | approved_entry | no | True | 21.000000 | 0.852278 | 0.841395 | 0.760000 | 0.092278 | 0.081395 | 0.572087 | 0.890563 | 1.005667 |
| KXBTC15M-26MAY071145-45 | approved_entry | yes | True | 20.000000 | 0.855371 | 0.844144 | 0.770000 | 0.085371 | 0.074144 | 0.585048 | 0.878426 | 0.992356 |
| KXBTC15M-26MAY060200-00 | approved_entry | yes | True | 17.000000 | 0.874865 | 0.861435 | 0.810000 | 0.064865 | 0.051435 | 0.293067 | 0.917335 | 0.990085 |
| KXBTC15M-26MAY060630-30 | approved_entry | yes | True | 19.000000 | 0.852499 | 0.847320 | 0.790000 | 0.062499 | 0.057320 | 0.272072 | 0.894900 | 0.986234 |
| KXBTC15M-26MAY061045-45 | approved_entry | yes | True | 18.000000 | 0.861569 | 0.853586 | 0.800000 | 0.061569 | 0.053586 | 0.408876 | 0.917282 | 0.975907 |
| KXBTC15M-26MAY062145-45 | rejected_actionable | no | False | -14.000000 | 0.783823 | 0.771477 | 0.120000 | 0.663823 | 0.651477 | 0.195824 | 0.666418 | 2.095172 |
| KXBTC15M-26MAY052345-45 | rejected_actionable | yes | False | -36.000000 | 0.805869 | 0.799590 | 0.320000 | 0.485869 | 0.479590 | 0.171066 | 0.746818 | 1.783996 |
| KXBTC15M-26MAY061800-00 | rejected_actionable | no | True | 72.000000 | 0.765762 | 0.753102 | 0.250000 | 0.515762 | 0.503102 | 0.230298 | 0.601549 | 1.774125 |
| KXBTC15M-26MAY061700-00 | rejected_actionable | no | False | -42.000000 | 0.788347 | 0.781552 | 0.380000 | 0.408347 | 0.401552 | 0.196391 | 0.665443 | 1.603914 |
| KXBTC15M-26MAY061945-45 | rejected_actionable | no | True | 51.000000 | 0.798947 | 0.778750 | 0.450000 | 0.348947 | 0.328750 | 0.396347 | 0.680058 | 1.443593 |

## post_stack_freeze_window

- Freeze UTC: `2026-05-06T15:37:04.750154+00:00`
- Forward denominator: `87`

| rank | candidate | repairs | coverage | net c | delta c | W/L | recon share | loss cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | hybrid_veto_plus_boundary_clock_approved_only_hybrid_edge_repair | 7 | 47.126437 | 312.000000 | 229.000000 | 27/14 | 0.707317 | 3 | coverage_too_low, reconstructed_share_gt_35pct |
| 2 | hybrid_veto_plus_boundary_clock_approved_only_raw_clean_repair | 7 | 47.126437 | 312.000000 | 229.000000 | 27/14 | 0.707317 | 3 | coverage_too_low, reconstructed_share_gt_35pct |
| 3 | hybrid_veto_plus_boundary_clock_source_cap35_hybrid_edge_repair | 7 | 47.126437 | 312.000000 | 229.000000 | 27/14 | 0.707317 | 3 | coverage_too_low, reconstructed_share_gt_35pct |
| 4 | hybrid_veto_plus_boundary_clock_source_cap35_raw_clean_repair | 7 | 47.126437 | 312.000000 | 229.000000 | 27/14 | 0.707317 | 3 | coverage_too_low, reconstructed_share_gt_35pct |
| 5 | hybrid_veto_plus_boundary_clock_hybrid_edge_repair | 32 | 75.862069 | 173.000000 | 90.000000 | 42/24 | 0.666667 | 1 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 6 | hybrid_veto_plus_boundary_clock_approved_first_hybrid_edge_repair | 32 | 75.862069 | 173.000000 | 90.000000 | 42/24 | 0.666667 | 1 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 7 | hybrid_veto_plus_boundary_clock_raw_clean_repair | 32 | 75.862069 | 95.000000 | 12.000000 | 41/25 | 0.666667 | 0 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 8 | hybrid_veto_plus_boundary_clock_approved_first_raw_clean_repair | 32 | 75.862069 | 95.000000 | 12.000000 | 41/25 | 0.666667 | 0 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 9 | all_three_with_boundary_fv_edge_hybrid_edge_repair | 35 | 75.862069 | 88.000000 | 5.000000 | 42/24 | 0.636364 | 0 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 10 | all_three_with_boundary_fv_edge_approved_first_hybrid_edge_repair | 35 | 75.862069 | 88.000000 | 5.000000 | 42/24 | 0.636364 | 0 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 11 | all_three_with_boundary_fv_edge_raw_clean_repair | 35 | 75.862069 | 10.000000 | -73.000000 | 41/25 | 0.636364 | 0 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 12 | all_three_with_boundary_fv_edge_approved_first_raw_clean_repair | 35 | 75.862069 | 10.000000 | -73.000000 | 41/25 | 0.636364 | 0 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 13 | all_three_with_boundary_fv_edge_approved_only_hybrid_edge_repair | 7 | 43.678161 | 236.000000 | 153.000000 | 25/13 | 0.684211 | 2 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 14 | all_three_with_boundary_fv_edge_approved_only_raw_clean_repair | 7 | 43.678161 | 236.000000 | 153.000000 | 25/13 | 0.684211 | 2 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 15 | all_three_with_boundary_fv_edge_source_cap35_hybrid_edge_repair | 7 | 43.678161 | 236.000000 | 153.000000 | 25/13 | 0.684211 | 2 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 16 | all_three_with_boundary_fv_edge_source_cap35_raw_clean_repair | 7 | 43.678161 | 236.000000 | 153.000000 | 25/13 | 0.684211 | 2 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 17 | early_no_plus_boundary_clock_approved_only_hybrid_edge_repair | 7 | 47.126437 | 227.000000 | 144.000000 | 27/14 | 0.707317 | 2 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 18 | early_no_plus_boundary_clock_approved_only_raw_clean_repair | 7 | 47.126437 | 227.000000 | 144.000000 | 27/14 | 0.707317 | 2 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 19 | early_no_plus_boundary_clock_source_cap35_hybrid_edge_repair | 7 | 47.126437 | 227.000000 | 144.000000 | 27/14 | 0.707317 | 2 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 20 | early_no_plus_boundary_clock_source_cap35_raw_clean_repair | 7 | 47.126437 | 227.000000 | 144.000000 | 27/14 | 0.707317 | 2 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 21 | all_three_without_boundary_fv_edge_approved_only_hybrid_edge_repair | 7 | 44.827586 | 130.000000 | 47.000000 | 25/14 | 0.692308 | 1 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 22 | all_three_without_boundary_fv_edge_approved_only_raw_clean_repair | 7 | 44.827586 | 130.000000 | 47.000000 | 25/14 | 0.692308 | 1 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 23 | all_three_without_boundary_fv_edge_source_cap35_hybrid_edge_repair | 7 | 44.827586 | 130.000000 | 47.000000 | 25/14 | 0.692308 | 1 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 24 | all_three_without_boundary_fv_edge_source_cap35_raw_clean_repair | 7 | 44.827586 | 130.000000 | 47.000000 | 25/14 | 0.692308 | 1 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 25 | hybrid_veto_plus_early_no_approved_only_hybrid_edge_repair | 7 | 47.126437 | 94.000000 | 11.000000 | 26/15 | 0.707317 | 0 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 26 | hybrid_veto_plus_early_no_approved_only_raw_clean_repair | 7 | 47.126437 | 94.000000 | 11.000000 | 26/15 | 0.707317 | 0 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 27 | hybrid_veto_plus_early_no_source_cap35_hybrid_edge_repair | 7 | 47.126437 | 94.000000 | 11.000000 | 26/15 | 0.707317 | 0 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 28 | hybrid_veto_plus_early_no_source_cap35_raw_clean_repair | 7 | 47.126437 | 94.000000 | 11.000000 | 26/15 | 0.707317 | 0 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 29 | early_no_plus_boundary_clock_hybrid_edge_repair | 32 | 75.862069 | -34.000000 | -117.000000 | 41/25 | 0.666667 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 30 | early_no_plus_boundary_clock_approved_first_hybrid_edge_repair | 32 | 75.862069 | -34.000000 | -117.000000 | 41/25 | 0.666667 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 31 | all_three_without_boundary_fv_edge_hybrid_edge_repair | 34 | 75.862069 | -74.000000 | -157.000000 | 41/25 | 0.651515 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 32 | all_three_without_boundary_fv_edge_approved_first_hybrid_edge_repair | 34 | 75.862069 | -74.000000 | -157.000000 | 41/25 | 0.651515 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 33 | early_no_plus_boundary_clock_raw_clean_repair | 32 | 75.862069 | -112.000000 | -195.000000 | 40/26 | 0.666667 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 34 | early_no_plus_boundary_clock_approved_first_raw_clean_repair | 32 | 75.862069 | -112.000000 | -195.000000 | 40/26 | 0.666667 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 35 | hybrid_veto_plus_early_no_hybrid_edge_repair | 32 | 75.862069 | -146.000000 | -229.000000 | 40/26 | 0.651515 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 36 | hybrid_veto_plus_early_no_approved_first_hybrid_edge_repair | 32 | 75.862069 | -146.000000 | -229.000000 | 40/26 | 0.651515 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 37 | all_three_without_boundary_fv_edge_raw_clean_repair | 34 | 75.862069 | -152.000000 | -235.000000 | 40/26 | 0.651515 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 38 | all_three_without_boundary_fv_edge_approved_first_raw_clean_repair | 34 | 75.862069 | -152.000000 | -235.000000 | 40/26 | 0.651515 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 39 | hybrid_veto_plus_early_no_approved_first_raw_clean_repair | 32 | 75.862069 | -159.000000 | -242.000000 | 40/26 | 0.651515 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 40 | hybrid_veto_plus_early_no_raw_clean_repair | 32 | 75.862069 | -228.000000 | -311.000000 | 39/27 | 0.666667 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

### Best Candidate Repairs

| market | source | side | won | net c | raw p | hybrid p | ask | raw edge | hybrid edge | recross | abs d | score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.963659 | 0.952539 | 0.700000 | 0.263659 | 0.252539 | 0.073753 | 1.543579 | 1.531676 |
| KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 25.000000 | 0.942571 | 0.936858 | 0.730000 | 0.212571 | 0.206858 | 0.239053 | 1.308547 | 1.398305 |
| KXBTC15M-26MAY071000-00 | approved_entry | no | True | 27.000000 | 0.851825 | 0.842628 | 0.710000 | 0.141825 | 0.132628 | 0.484111 | 0.895147 | 1.116211 |
| KXBTC15M-26MAY071045-45 | approved_entry | no | True | 22.000000 | 0.865260 | 0.855991 | 0.750000 | 0.115260 | 0.105991 | 0.469918 | 0.953688 | 1.080382 |
| KXBTC15M-26MAY071315-15 | approved_entry | yes | True | 20.000000 | 0.850827 | 0.848318 | 0.780000 | 0.070827 | 0.068318 | 0.132426 | 0.850077 | 1.017492 |
| KXBTC15M-26MAY061300-00 | approved_entry | yes | False | -82.000000 | 0.860906 | 0.855026 | 0.800000 | 0.060906 | 0.055026 | 0.301730 | 0.913273 | 0.988072 |
| KXBTC15M-26MAY070930-30 | approved_entry | yes | True | 17.000000 | 0.855936 | 0.848715 | 0.800000 | 0.055936 | 0.048715 | 0.375669 | 0.878792 | 0.961838 |
