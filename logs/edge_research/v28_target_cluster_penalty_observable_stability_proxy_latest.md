# v28 Target Cluster-Penalty Observable Stability Proxy

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T11:36:22.673408+00:00`
- Observable proxy freeze UTC: `2026-05-07T00:06:52.057182+00:00`
- Source label use: `audit_only_not_used_for_selection`
- Physics: Prefer rows farther from the settlement boundary with calmer recross behavior, and penalize cheap near-boundary churn that can look like false raw edge.

## Interpretation

- This watch uses only observable market features for selection; source labels are audit-only.
- Promotion still requires strict post-birth rows, positive PnL, broad coverage, <=35% reconstructed share, and full-loss cushion.
- diagnostic_target_window: best diagnostic_target_window_medium_paid_stable settled 97, coverage 75.1937984496124%, net -137.0c, recon 0.6597938144329897, blockers ['net_not_positive', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].
- post_observable_proxy_birth: best post_observable_proxy_birth_heavy_far_calm settled 25, coverage 75.75757575757575%, net -350.0c, recon 0.8, blockers ['settled_lt_30', 'net_not_positive', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].

## diagnostic_target_window

| rank | candidate | settled/den | W/L | coverage | net c | delta vs target | recon | cushion | rows/clean/cushion needed | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `diagnostic_target_window_medium_paid_stable` | 97/129 | 39/58 | 75.193798 | -137.000000 | 273.000000 | 0.659794 | 0 | 0/86/300.000000c | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 2 | `diagnostic_target_window_heavy_far_calm` | 97/129 | 37/60 | 75.193798 | -356.000000 | 54.000000 | 0.659794 | 0 | 0/86/300.000000c | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 3 | `diagnostic_target_window_light_paid_stable` | 97/129 | 37/60 | 75.193798 | -234.000000 | 176.000000 | 0.680412 | 0 | 0/92/300.000000c | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 4 | `diagnostic_target_window_medium_far_calm_medium` | 97/129 | 36/61 | 75.193798 | -348.000000 | 62.000000 | 0.690722 | 0 | 0/95/300.000000c | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 5 | `diagnostic_target_window_medium_far_calm_light` | 97/129 | 35/62 | 75.193798 | -301.000000 | 109.000000 | 0.711340 | 0 | 0/101/300.000000c | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

### Best Variant Worst Rows

| market | source | side | won | net c | p | ask | cluster edge | observable edge | far | calm | cheap unstable | paid stable | abs d | recross |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY060215-15 | approved_entry | yes | False | -79.000000 | 0.869074 | 0.770000 | 0.099074 | 0.145391 | 0.767943 | 0.393389 | 0.000000 | 0.189892 | 0.921532 | 0.363966 |
| KXBTC15M-26MAY052045-45 | rejected_actionable | yes | False | -73.000000 | 0.819741 | 0.700000 | 0.119741 | 0.174787 | 0.638566 | 0.831697 | 0.000000 | 0.227611 | 0.766279 | 0.100982 |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.963659 | 0.700000 | 0.263659 | 0.337489 | 1.000000 | 0.877079 | 0.000000 | 0.375891 | 1.543579 | 0.073753 |
| KXBTC15M-26MAY062130-30 | rejected_actionable | no | False | -65.000000 | 0.768416 | 0.610000 | 0.158416 | 0.196834 | 0.519898 | 0.554471 | 0.000000 | 0.049417 | 0.623877 | 0.267318 |
| KXBTC15M-26MAY060745-45 | rejected_actionable | yes | False | -64.000000 | 0.805231 | 0.600000 | 0.205231 | 0.239160 | 0.610363 | 0.299726 | 0.000000 | 0.026135 | 0.732436 | 0.420164 |
| KXBTC15M-26MAY052000-00 | rejected_actionable | yes | False | -58.000000 | 0.767756 | 0.540000 | 0.227756 | 0.273539 | 0.532655 | 0.815899 | 0.000000 | 0.000000 | 0.639186 | 0.110461 |
| KXBTC15M-26MAY052330-30 | rejected_actionable | no | False | -54.000000 | 0.699662 | 0.500000 | 0.199662 | 0.223713 | 0.384517 | 0.289015 | 0.000000 | 0.000000 | 0.461420 | 0.426591 |
| KXBTC15M-26MAY060445-45 | rejected_actionable | no | False | -49.000000 | 0.636374 | 0.450000 | 0.160428 | 0.171168 | 0.268498 | 0.000000 | 0.000000 | 0.000000 | 0.322198 | 0.666569 |
| KXBTC15M-26MAY060545-45 | rejected_actionable | no | False | -48.000000 | 0.626642 | 0.440000 | 0.159898 | 0.170166 | 0.269518 | 0.000000 | 0.010258 | 0.000000 | 0.323422 | 0.689053 |
| KXBTC15M-26MAY052015-15 | rejected_actionable | no | False | -46.000000 | 0.567222 | 0.420000 | 0.135197 | 0.138199 | 0.137266 | 0.000000 | 0.049772 | 0.000000 | 0.164719 | 0.770362 |

## post_observable_proxy_birth

| rank | candidate | settled/den | W/L | coverage | net c | delta vs target | recon | cushion | rows/clean/cushion needed | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `post_observable_proxy_birth_heavy_far_calm` | 25/33 | 4/21 | 75.757576 | -350.000000 | -526.000000 | 0.800000 | 0 | 5/33/300.000000c | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 2 | `post_observable_proxy_birth_medium_paid_stable` | 25/33 | 5/20 | 75.757576 | -181.000000 | -357.000000 | 0.840000 | 0 | 5/35/300.000000c | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 3 | `post_observable_proxy_birth_medium_far_calm_medium` | 25/33 | 4/21 | 75.757576 | -308.000000 | -484.000000 | 0.840000 | 0 | 5/35/300.000000c | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 4 | `post_observable_proxy_birth_medium_far_calm_light` | 25/33 | 4/21 | 75.757576 | -231.000000 | -407.000000 | 0.880000 | 0 | 5/38/300.000000c | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 5 | `post_observable_proxy_birth_light_paid_stable` | 25/33 | 4/21 | 75.757576 | -243.000000 | -419.000000 | 0.880000 | 0 | 5/38/300.000000c | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

### Best Variant Worst Rows

| market | source | side | won | net c | p | ask | cluster edge | observable edge | far | calm | cheap unstable | paid stable | abs d | recross |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.963659 | 0.700000 | 0.263659 | 0.363128 | 1.000000 | 0.877079 | 0.000000 | 0.375891 | 1.543579 | 0.073753 |
| KXBTC15M-26MAY062130-30 | rejected_actionable | no | False | -65.000000 | 0.768416 | 0.610000 | 0.158416 | 0.214561 | 0.519898 | 0.554471 | 0.000000 | 0.049417 | 0.623877 | 0.267318 |
| KXBTC15M-26MAY062345-45 | rejected_actionable | no | False | -60.000000 | 0.806238 | 0.560000 | 0.246238 | 0.307726 | 0.605808 | 0.558663 | 0.000000 | 0.009670 | 0.726970 | 0.264802 |
| KXBTC15M-26MAY062230-30 | rejected_actionable | yes | False | -42.000000 | 0.718015 | 0.380000 | 0.338015 | 0.379189 | 0.401484 | 0.417214 | 0.018769 | 0.000000 | 0.481781 | 0.349672 |
| KXBTC15M-26MAY070700-00 | rejected_actionable | yes | False | -28.000000 | 0.695361 | 0.250000 | 0.445361 | 0.476717 | 0.398177 | 0.298117 | 0.066109 | 0.000000 | 0.477812 | 0.421130 |
| KXBTC15M-26MAY062100-00 | rejected_actionable | no | False | -25.000000 | 0.615588 | 0.220000 | 0.395588 | 0.401991 | 0.267632 | 0.140888 | 0.177717 | 0.000000 | 0.321159 | 0.515467 |
| KXBTC15M-26MAY070100-00 | rejected_actionable | no | False | -25.000000 | 0.505013 | 0.220000 | 0.276326 | 0.240213 | 0.027180 | 0.000000 | 0.419377 | 0.000000 | 0.032616 | 0.647900 |
| KXBTC15M-26MAY070530-30 | rejected_actionable | yes | False | -19.000000 | 0.457215 | 0.170000 | 0.287215 | 0.263773 | 0.095510 | 0.094364 | 0.371317 | 0.000000 | 0.114612 | 0.543382 |
| KXBTC15M-26MAY070545-45 | rejected_actionable | yes | False | -16.000000 | 0.514100 | 0.140000 | 0.374100 | 0.345273 | 0.001652 | 0.217288 | 0.430046 | 0.000000 | 0.001982 | 0.469627 |
| KXBTC15M-26MAY062315-15 | rejected_actionable | yes | False | -16.000000 | 0.347772 | 0.140000 | 0.207772 | 0.240646 | 0.284826 | 0.573606 | 0.111425 | 0.000000 | 0.341791 | 0.255836 |
