# v28 Target Cluster-Penalty Source-Aware Watch

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T11:35:03.403092+00:00`
- Source-aware freeze UTC: `2026-05-07T00:01:16.649704+00:00`
- Warning: `The source penalty is a research evidence-quality stress only. It is not a deployable live-market feature.`

## Interpretation

- Source-aware cluster penalties are watch-only and intentionally blocked from live promotion.
- The useful signal is whether target coverage, positive PnL, and <=35% reconstructed share can coexist under strict forward evidence.
- diagnostic_target_window: cleanest diagnostic_target_window_medium_src_penalty100 settled 97, coverage 75.1937984496124%, net 75.0c, recon 0.4845360824742268, blockers ['source_penalty_research_only_not_live_feature', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].
- post_source_aware_birth: cleanest post_source_aware_birth_medium_src_penalty100 settled 25, coverage 75.75757575757575%, net -175.0c, recon 0.76, blockers ['source_penalty_research_only_not_live_feature', 'settled_lt_30', 'net_not_positive', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].

## diagnostic_target_window

| rank | candidate | settled/den | W/L | coverage | net c | delta vs target | recon | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `diagnostic_target_window_medium_src_penalty100` | 97/129 | 50/47 | 75.193798 | 75.000000 | 485.000000 | 0.484536 | 0 | source_penalty_research_only_not_live_feature, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 2 | `diagnostic_target_window_heavy_src_penalty050` | 97/129 | 46/51 | 75.193798 | 57.000000 | 467.000000 | 0.567010 | 0 | source_penalty_research_only_not_live_feature, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 3 | `diagnostic_target_window_medium_src_penalty050` | 97/129 | 45/52 | 75.193798 | 22.000000 | 432.000000 | 0.577320 | 0 | source_penalty_research_only_not_live_feature, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 4 | `diagnostic_target_window_light_src_penalty050` | 97/129 | 45/52 | 75.193798 | 22.000000 | 432.000000 | 0.577320 | 0 | source_penalty_research_only_not_live_feature, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 5 | `diagnostic_target_window_medium_src_penalty025` | 97/129 | 37/60 | 75.193798 | -132.000000 | 278.000000 | 0.701031 | 0 | source_penalty_research_only_not_live_feature, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

### Cleanest Variant Worst Rows

| market | source | side | won | net c | p | ask | cluster edge | source edge | source penalty | stc | abs d | recross |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY052045-45 | approved_entry | yes | False | -84.000000 | 0.904488 | 0.830000 | 0.074488 | 0.074488 | 0.000000 | 144.381000 | 1.123967 | 0.063962 |
| KXBTC15M-26MAY061300-00 | approved_entry | yes | False | -82.000000 | 0.860906 | 0.800000 | 0.060906 | 0.060906 | 0.000000 | 486.266000 | 0.913273 | 0.301730 |
| KXBTC15M-26MAY060215-15 | approved_entry | yes | False | -79.000000 | 0.869074 | 0.770000 | 0.099074 | 0.099074 | 0.000000 | 809.853000 | 0.921532 | 0.363966 |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.887777 | 0.760000 | 0.127777 | 0.127777 | 0.000000 | 628.084000 | 0.999156 | 0.303870 |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.963659 | 0.700000 | 0.263659 | 0.263659 | 0.000000 | 279.632000 | 1.543579 | 0.073753 |
| KXBTC15M-26MAY060745-45 | approved_entry | yes | False | -71.000000 | 0.851843 | 0.690000 | 0.161843 | 0.161843 | 0.000000 | 491.325000 | 0.889718 | 0.303224 |
| KXBTC15M-26MAY052000-00 | rejected_actionable | yes | False | -58.000000 | 0.767756 | 0.540000 | 0.227756 | 0.127756 | 0.100000 | 165.924000 | 0.639186 | 0.110461 |
| KXBTC15M-26MAY052330-30 | rejected_actionable | no | False | -54.000000 | 0.699662 | 0.500000 | 0.199662 | 0.099662 | 0.100000 | 534.711000 | 0.461420 | 0.426591 |
| KXBTC15M-26MAY060445-45 | rejected_actionable | no | False | -49.000000 | 0.636374 | 0.450000 | 0.160428 | 0.060428 | 0.100000 | 864.716000 | 0.322198 | 0.666569 |
| KXBTC15M-26MAY061115-15 | rejected_actionable | yes | False | -45.000000 | 0.579856 | 0.410000 | 0.169856 | 0.069856 | 0.100000 | 250.508000 | 0.172017 | 0.363463 |

## post_source_aware_birth

| rank | candidate | settled/den | W/L | coverage | net c | delta vs target | recon | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `post_source_aware_birth_medium_src_penalty100` | 25/33 | 6/19 | 75.757576 | -175.000000 | -351.000000 | 0.760000 | 0 | source_penalty_research_only_not_live_feature, settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 2 | `post_source_aware_birth_medium_src_penalty050` | 25/33 | 4/21 | 75.757576 | -298.000000 | -474.000000 | 0.840000 | 0 | source_penalty_research_only_not_live_feature, settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 3 | `post_source_aware_birth_heavy_src_penalty050` | 25/33 | 4/21 | 75.757576 | -298.000000 | -474.000000 | 0.840000 | 0 | source_penalty_research_only_not_live_feature, settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 4 | `post_source_aware_birth_medium_src_penalty025` | 25/33 | 4/21 | 75.757576 | -239.000000 | -415.000000 | 0.880000 | 0 | source_penalty_research_only_not_live_feature, settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 5 | `post_source_aware_birth_light_src_penalty050` | 25/33 | 4/21 | 75.757576 | -239.000000 | -415.000000 | 0.880000 | 0 | source_penalty_research_only_not_live_feature, settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

### Cleanest Variant Worst Rows

| market | source | side | won | net c | p | ask | cluster edge | source edge | source penalty | stc | abs d | recross |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.887777 | 0.760000 | 0.127777 | 0.127777 | 0.000000 | 628.084000 | 0.999156 | 0.303870 |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.963659 | 0.700000 | 0.263659 | 0.263659 | 0.000000 | 279.632000 | 1.543579 | 0.073753 |
| KXBTC15M-26MAY062230-30 | rejected_actionable | yes | False | -42.000000 | 0.718015 | 0.380000 | 0.338015 | 0.238015 | 0.100000 | 460.951000 | 0.481781 | 0.349672 |
| KXBTC15M-26MAY070700-00 | rejected_actionable | yes | False | -28.000000 | 0.695361 | 0.250000 | 0.445361 | 0.345361 | 0.100000 | 529.828000 | 0.477812 | 0.421130 |
| KXBTC15M-26MAY062315-15 | rejected_actionable | yes | False | -26.000000 | 0.455715 | 0.230000 | 0.225715 | 0.125715 | 0.100000 | 339.597000 | 0.098016 | 0.380120 |
| KXBTC15M-26MAY062100-00 | rejected_actionable | no | False | -25.000000 | 0.615588 | 0.220000 | 0.395588 | 0.295588 | 0.100000 | 683.547000 | 0.321159 | 0.515467 |
| KXBTC15M-26MAY070100-00 | rejected_actionable | no | False | -25.000000 | 0.505013 | 0.220000 | 0.279221 | 0.179221 | 0.100000 | 543.305000 | 0.032616 | 0.647900 |
| KXBTC15M-26MAY070530-30 | rejected_actionable | yes | False | -19.000000 | 0.457215 | 0.170000 | 0.287215 | 0.187215 | 0.100000 | 531.297000 | 0.114612 | 0.543382 |
| KXBTC15M-26MAY070715-15 | rejected_actionable | no | False | -19.000000 | 0.423617 | 0.170000 | 0.245065 | 0.145065 | 0.100000 | 677.918000 | 0.171542 | 0.725790 |
| KXBTC15M-26MAY070545-45 | rejected_actionable | yes | False | -16.000000 | 0.514100 | 0.140000 | 0.374100 | 0.274100 | 0.100000 | 399.557000 | 0.001982 | 0.469627 |
