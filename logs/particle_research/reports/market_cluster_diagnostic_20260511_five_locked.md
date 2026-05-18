# Market Cluster Diagnostic

- run_count: 5
- market_count: 27
- candidate_count: 16931
- selected_count: 15689
- total_counterfactual_pnl_cents: 74321.0000
- ev_rank_correlation_sign: -0.139601
- top_ev_bucket_avg_market_candidate_pnl_cents: -0.354508
- best_probability_model_by_market_brier: current_calibrated
- best_probability_model_by_market_log_loss: current_calibrated
- conclusion: Market-clustered diagnostics do not support promotion: equal-market EV ranking or top-bucket profitability is weak.

## Model Summary

| model | markets | brier | log_loss | mean_abs_cal_error |
|---|---:|---:|---:|---:|
| current_calibrated | 27 | 0.130024 | 0.414496 | 0.311833 |
| market | 27 | 0.131034 | 0.415895 | 0.313308 |
| brownian | 27 | 0.166157 | 0.514524 | 0.392894 |
| particle | 27 | 0.166264 | 0.514537 | 0.392808 |

## EV Buckets

| bucket | markets | candidates | selected | avg_ev_cents | total_pnl_cents | avg_market_candidate_pnl | positive_markets |
|---|---:|---:|---:|---:|---:|---:|---:|
| ev_rank_1_highest | 6 | 3716 | 3651 | 21.1791 | 8039.0000 | -0.3545 | 1/6 |
| ev_rank_2 | 5 | 3476 | 3287 | 13.8443 | -14121.0000 | -3.8922 | 2/5 |
| ev_rank_3 | 6 | 4658 | 4270 | 10.0604 | 64629.0000 | 14.3707 | 4/6 |
| ev_rank_4 | 5 | 2629 | 2327 | 7.2392 | -11868.0000 | -3.1807 | 1/5 |
| ev_rank_5_lowest | 5 | 2452 | 2154 | 4.6902 | 27642.0000 | 11.1707 | 3/5 |

## Runs

| run | markets | candidates | selected | pnl_cents | avg_market_candidate_pnl | best_model_brier | ev_rank | top_bucket_avg_market_pnl |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | 6 | 3414 | 3229 | 15777.0000 | 1.8604 | market | 0.200000 | -7.6786 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | 5 | 3501 | 3275 | 15798.0000 | 3.6622 | current_calibrated | -0.400000 | -15.9193 |
| particle_residual_blend_oos_RESIDLOCK001 | 5 | 3358 | 3045 | 60332.0000 | 22.9269 | brownian | -0.600000 | -11.6741 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | 6 | 3260 | 3029 | -32502.0000 | -10.4860 | current_calibrated | 0.200000 | -4.2848 |
| particle_side_safety_oos_20260511TLOCKED | 5 | 3398 | 3111 | 14916.0000 | 4.6789 | market | -0.400000 | -11.2103 |

## Markets

| run | market | candidates | selected | result_yes | avg_particle | avg_market | avg_current | avg_ev | avg_pnl | yes_ev_share |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| particle_side_safety_oos_20260511TLOCKED | KXBTC15M-26MAY110245-45 | 659 | 598 | False | 0.368395 | 0.243604 | 0.276434 | 11.7973 | -14.8528 | 0.8816 |
| particle_side_safety_oos_20260511TLOCKED | KXBTC15M-26MAY110300-00 | 814 | 756 | True | 0.521428 | 0.595154 | 0.548018 | 12.6486 | 8.8403 | 0.3882 |
| particle_side_safety_oos_20260511TLOCKED | KXBTC15M-26MAY110315-15 | 756 | 755 | False | 0.283954 | 0.108955 | 0.102763 | 16.7708 | -11.2103 | 1.0000 |
| particle_side_safety_oos_20260511TLOCKED | KXBTC15M-26MAY110330-30 | 803 | 723 | False | 0.476497 | 0.500473 | 0.461888 | 10.3311 | 25.4396 | 0.3724 |
| particle_side_safety_oos_20260511TLOCKED | KXBTC15M-26MAY110345-45 | 366 | 279 | False | 0.489654 | 0.498046 | 0.489876 | 3.2819 | 15.1776 | 0.3743 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | KXBTC15M-26MAY110415-15 | 534 | 512 | False | 0.389199 | 0.305421 | 0.277780 | 14.0432 | 6.9213 | 0.6461 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | KXBTC15M-26MAY110430-30 | 782 | 725 | False | 0.506305 | 0.555633 | 0.548085 | 10.8238 | 41.1458 | 0.2212 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | KXBTC15M-26MAY110445-45 | 781 | 781 | True | 0.623590 | 0.844494 | 0.812376 | 21.1407 | -15.9193 | 0.0000 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | KXBTC15M-26MAY110500-00 | 791 | 673 | False | 0.426962 | 0.357927 | 0.354842 | 8.6235 | 4.7244 | 0.6271 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | KXBTC15M-26MAY110515-15 | 613 | 584 | True | 0.605187 | 0.778059 | 0.774881 | 16.2575 | -18.5612 | 0.0392 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | KXBTC15M-26MAY110530-30 | 6 | 6 | False | 0.374333 | 0.015833 | 0.176763 | 35.2257 | -1.8333 | 1.0000 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | KXBTC15M-26MAY110545-45 | 848 | 820 | True | 0.445650 | 0.324646 | 0.327987 | 17.5467 | 58.9210 | 0.8679 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | KXBTC15M-26MAY110600-00 | 816 | 768 | True | 0.558209 | 0.709638 | 0.682819 | 15.2257 | -11.8002 | 0.1581 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | KXBTC15M-26MAY110615-15 | 783 | 711 | True | 0.612771 | 0.739227 | 0.725140 | 11.7880 | -18.3321 | 0.0715 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | KXBTC15M-26MAY110630-30 | 712 | 705 | True | 0.650958 | 0.860857 | 0.847268 | 20.1332 | -13.5239 | 0.0042 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | KXBTC15M-26MAY110645-45 | 249 | 219 | False | 0.464181 | 0.422289 | 0.379180 | 6.5309 | -2.2691 | 0.6265 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | KXBTC15M-26MAY110900-00 | 2 | 2 | False | 0.080500 | 0.000000 | 0.000980 | 7.9695 | 0.0000 | 1.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | KXBTC15M-26MAY110915-15 | 653 | 653 | True | 0.756273 | 0.917236 | 0.949020 | 15.5067 | -8.5697 | 0.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | KXBTC15M-26MAY110930-30 | 765 | 682 | False | 0.404200 | 0.355261 | 0.341878 | 6.5339 | -0.8954 | 0.6837 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | KXBTC15M-26MAY110945-45 | 837 | 765 | False | 0.199123 | 0.165066 | 0.095907 | 4.1643 | -8.1589 | 0.9116 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | KXBTC15M-26MAY111000-00 | 822 | 751 | False | 0.301199 | 0.227251 | 0.154916 | 6.5380 | -17.4635 | 0.9367 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | KXBTC15M-26MAY111015-15 | 181 | 176 | True | 0.644525 | 0.717541 | 0.801151 | 6.0230 | -27.8287 | 0.0110 |
| particle_residual_blend_oos_RESIDLOCK001 | KXBTC15M-26MAY111115-15 | 720 | 699 | True | 0.452970 | 0.411361 | 0.397586 | 8.6328 | 48.3542 | 0.8028 |
| particle_residual_blend_oos_RESIDLOCK001 | KXBTC15M-26MAY111130-30 | 721 | 614 | True | 0.535216 | 0.525270 | 0.519922 | 4.7322 | 19.6546 | 0.5576 |
| particle_residual_blend_oos_RESIDLOCK001 | KXBTC15M-26MAY111145-45 | 807 | 773 | False | 0.305937 | 0.204678 | 0.184572 | 9.7144 | -11.6741 | 0.9145 |
| particle_residual_blend_oos_RESIDLOCK001 | KXBTC15M-26MAY111200-00 | 763 | 639 | True | 0.630740 | 0.717005 | 0.707630 | 9.0722 | 1.2910 | 0.2805 |
| particle_residual_blend_oos_RESIDLOCK001 | KXBTC15M-26MAY111215-15 | 347 | 320 | True | 0.427102 | 0.360634 | 0.332570 | 5.2495 | 57.0086 | 0.9942 |
