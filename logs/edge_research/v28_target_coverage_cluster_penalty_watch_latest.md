# v28 Target-Coverage Cluster Penalty Watch

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T11:34:02.212562+00:00`
- Cluster penalty freeze UTC: `2026-05-06T21:38:42.476858+00:00`

## Interpretation

- Continuous cluster penalties are watch-only; post_cluster_penalty_birth is the only strict forward evidence for this new family.
- diagnostic_target_window: best diagnostic_target_window_cluster_penalty_heavy settled 97, coverage 75.1937984496124%, net -84.0c, delta vs target 326.0c, recon 0.7525773195876289, blockers ['net_not_positive', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].
- post_cluster_penalty_birth: best post_cluster_penalty_birth_cluster_penalty_medium settled 33, coverage 76.74418604651163%, net -96.0c, delta vs target -490.0c, recon 0.9090909090909091, blockers ['net_not_positive', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].

## diagnostic_target_window

| rank | candidate | settled/den | W/L | coverage | net c | delta vs target | recon | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | diagnostic_target_window_cluster_penalty_heavy | 97/129 | 36/61 | 75.193798 | -84.000000 | 326.000000 | 0.752577 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 2 | diagnostic_target_window_cluster_penalty_medium | 97/129 | 35/62 | 75.193798 | -127.000000 | 283.000000 | 0.752577 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 3 | diagnostic_target_window_cluster_penalty_light | 97/129 | 34/63 | 75.193798 | -179.000000 | 231.000000 | 0.762887 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

### Best Variant Worst Rows

| market | source | side | won | net c | p | ask | raw edge | adj edge | penalty | stc | abs d | recross |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY060215-15 | approved_entry | yes | False | -79.000000 | 0.869074 | 0.770000 | 0.099074 | 0.099074 | 0.000000 | 809.853000 | 0.921532 | 0.363966 |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.963659 | 0.700000 | 0.263659 | 0.263659 | 0.000000 | 279.632000 | 1.543579 | 0.073753 |
| KXBTC15M-26MAY060745-45 | rejected_actionable | yes | False | -64.000000 | 0.805231 | 0.600000 | 0.205231 | 0.205231 | 0.000000 | 579.162000 | 0.732436 | 0.420164 |
| KXBTC15M-26MAY052000-00 | rejected_actionable | yes | False | -58.000000 | 0.767756 | 0.540000 | 0.227756 | 0.227756 | 0.000000 | 165.924000 | 0.639186 | 0.110461 |
| KXBTC15M-26MAY052330-30 | rejected_actionable | no | False | -54.000000 | 0.699662 | 0.500000 | 0.199662 | 0.199662 | 0.000000 | 534.711000 | 0.461420 | 0.426591 |
| KXBTC15M-26MAY060445-45 | rejected_actionable | no | False | -49.000000 | 0.636374 | 0.450000 | 0.186374 | 0.147455 | 0.038919 | 864.716000 | 0.322198 | 0.666569 |
| KXBTC15M-26MAY060545-45 | rejected_actionable | no | False | -48.000000 | 0.626642 | 0.440000 | 0.186642 | 0.146526 | 0.040116 | 807.560000 | 0.323422 | 0.689053 |
| KXBTC15M-26MAY052015-15 | rejected_actionable | no | False | -46.000000 | 0.567222 | 0.420000 | 0.147222 | 0.129185 | 0.018037 | 715.500000 | 0.164719 | 0.770362 |
| KXBTC15M-26MAY061115-15 | rejected_actionable | yes | False | -45.000000 | 0.579856 | 0.410000 | 0.169856 | 0.169856 | 0.000000 | 250.508000 | 0.172017 | 0.363463 |
| KXBTC15M-26MAY062200-00 | rejected_actionable | yes | False | -43.000000 | 0.578877 | 0.390000 | 0.188877 | 0.188877 | 0.000000 | 572.926000 | 0.199550 | 0.564940 |

## post_cluster_penalty_birth

| rank | candidate | settled/den | W/L | coverage | net c | delta vs target | recon | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | post_cluster_penalty_birth_cluster_penalty_medium | 33/43 | 8/25 | 76.744186 | -96.000000 | -490.000000 | 0.909091 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 2 | post_cluster_penalty_birth_cluster_penalty_heavy | 33/43 | 7/26 | 76.744186 | -162.000000 | -556.000000 | 0.909091 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 3 | post_cluster_penalty_birth_cluster_penalty_light | 33/43 | 7/26 | 76.744186 | -170.000000 | -564.000000 | 0.909091 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

### Best Variant Worst Rows

| market | source | side | won | net c | p | ask | raw edge | adj edge | penalty | stc | abs d | recross |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.963659 | 0.700000 | 0.263659 | 0.263659 | 0.000000 | 279.632000 | 1.543579 | 0.073753 |
| KXBTC15M-26MAY062200-00 | rejected_actionable | yes | False | -43.000000 | 0.578877 | 0.390000 | 0.188877 | 0.188877 | 0.000000 | 572.926000 | 0.199550 | 0.564940 |
| KXBTC15M-26MAY062230-30 | rejected_actionable | yes | False | -42.000000 | 0.718015 | 0.380000 | 0.338015 | 0.338015 | 0.000000 | 460.951000 | 0.481781 | 0.349672 |
| KXBTC15M-26MAY062115-15 | rejected_actionable | no | False | -37.000000 | 0.604254 | 0.330000 | 0.274254 | 0.273773 | 0.000481 | 705.140000 | 0.278385 | 0.617628 |
| KXBTC15M-26MAY062030-30 | rejected_actionable | yes | False | -36.000000 | 0.544418 | 0.320000 | 0.224418 | 0.216954 | 0.007464 | 804.712000 | 0.107412 | 0.680770 |
| KXBTC15M-26MAY070700-00 | rejected_actionable | yes | False | -28.000000 | 0.695361 | 0.250000 | 0.445361 | 0.445361 | 0.000000 | 529.828000 | 0.477812 | 0.421130 |
| KXBTC15M-26MAY061930-30 | rejected_actionable | no | False | -28.000000 | 0.551840 | 0.250000 | 0.301840 | 0.294006 | 0.007834 | 624.625000 | 0.118494 | 0.688823 |
| KXBTC15M-26MAY061830-30 | rejected_actionable | yes | False | -26.000000 | 0.553162 | 0.230000 | 0.323162 | 0.320141 | 0.003021 | 653.539000 | 0.098877 | 0.631576 |
| KXBTC15M-26MAY062315-15 | rejected_actionable | yes | False | -26.000000 | 0.455715 | 0.230000 | 0.225715 | 0.225715 | 0.000000 | 339.597000 | 0.098016 | 0.380120 |
| KXBTC15M-26MAY062100-00 | rejected_actionable | no | False | -25.000000 | 0.615588 | 0.220000 | 0.395588 | 0.395588 | 0.000000 | 683.547000 | 0.321159 | 0.515467 |
