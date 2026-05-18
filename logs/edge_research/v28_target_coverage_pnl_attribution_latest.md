# v28 Target-Coverage PnL Attribution

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Forward denominator: `152`
- Entries/settled/coverage: `112/112/73.684211`
- Net cents: `-626.000000`

## Interpretation

- Target surface has 112 entries over 152 markets; 112 settled.
- Direction-wrong rows contribute -5007.0c across 48 rows.
- Side-won-but-negative rows contribute -52.0c across 2 rows.
- Do not use side-won negative-PnL rows as pure FV failures; they are exit/execution shaped.
- FV/entry work should focus on directional losers, especially recurring tags that preserve coverage.

## Class Rollups

| class | rows | settled | W/L | net c | avg c |
|---|---:|---:|---:|---:|---:|
| side_won_positive_pnl | 62 | 62 | 62/0 | 4433.000000 | 71.500000 |
| direction_wrong | 48 | 48 | 0/48 | -5007.000000 | -104.312500 |
| side_won_but_negative_pnl | 2 | 2 | 2/0 | -52.000000 | -26.000000 |

## Worst Tag Rollups

| tag | rows | settled | W/L | net c | avg c |
|---|---:|---:|---:|---:|---:|
| p_60_70 | 45 | 45 | 21/24 | -1094.000000 | -24.311111 |
| edge_lt_2pp | 22 | 22 | 10/12 | -883.000000 | -40.136364 |
| early_stc_ge_780 | 72 | 72 | 39/33 | -794.000000 | -11.027778 |
| reason:keep_p_ge_60 | 76 | 76 | 47/29 | -715.000000 | -9.407895 |
| source:rejected_actionable | 105 | 105 | 57/48 | -689.000000 | -6.561905 |
| high_recross_ge_075 | 54 | 54 | 27/27 | -625.000000 | -11.574074 |
| cheap_lte_55c | 48 | 48 | 20/28 | -373.000000 | -7.770833 |
| near_boundary_absd_lte_030 | 59 | 59 | 28/31 | -358.000000 | -6.067797 |
| edge_ge_4pp | 68 | 68 | 36/32 | -255.000000 | -3.750000 |
| reason:keep_not_turbulent | 4 | 4 | 2/2 | -52.000000 | -13.000000 |
| late_stc_lte_480 | 8 | 8 | 7/1 | 27.000000 | 3.375000 |
| expensive_ge_78c | 12 | 12 | 11/1 | 48.000000 | 4.000000 |
| source:approved_entry | 7 | 7 | 7/0 | 63.000000 | 9.000000 |
| p_lt_60 | 36 | 36 | 17/19 | 89.000000 | 2.472222 |
| p_70_80 | 18 | 18 | 13/5 | 95.000000 | 5.277778 |
| low_recross_lte_045 | 15 | 15 | 13/2 | 107.000000 | 7.133333 |
| reason:keep_edge_ge_4pp | 32 | 32 | 15/17 | 141.000000 | 4.406250 |
| far_boundary_absd_ge_075 | 12 | 12 | 12/0 | 241.000000 | 20.083333 |

## Direction-Wrong Rows

| market | source | reason | side | net c | p | ask | edge | stc | abs d | recross | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY060100-00 | rejected_actionable | keep_p_ge_60 | yes | -161.000000 | 0.799928 | 0.790000 | 0.009928 | 684.076000 | 0.694496 | 0.407561 | source:rejected_actionable, reason:keep_p_ge_60, p_70_80, edge_lt_2pp, expensive_ge_78c, low_recross_lte_045 |
| KXBTC15M-26MAY061100-00 | rejected_actionable | keep_p_ge_60 | yes | -151.000000 | 0.740374 | 0.740000 | 0.000374 | 865.321000 | 0.597049 | 0.809587 | source:rejected_actionable, reason:keep_p_ge_60, p_70_80, edge_lt_2pp, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY071230-30 | rejected_actionable | keep_p_ge_60 | no | -143.000000 | 0.729882 | 0.700000 | 0.029882 | 863.492000 | 0.573733 | 0.815016 | source:rejected_actionable, reason:keep_p_ge_60, p_70_80, edge_2_4pp, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY061230-30 | rejected_actionable | keep_p_ge_60 | yes | -140.000000 | 0.681329 | 0.680000 | 0.001329 | 829.291000 | 0.451740 | 0.862457 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_lt_2pp, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY060630-30 | rejected_actionable | keep_p_ge_60 | no | -136.000000 | 0.675344 | 0.660000 | 0.015344 | 868.927000 | 0.393798 | 0.762043 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_lt_2pp, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY060245-45 | rejected_actionable | keep_p_ge_60 | no | -134.000000 | 0.660829 | 0.650000 | 0.010829 | 868.740000 | 0.346255 | 0.663720 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_lt_2pp, early_stc_ge_780 |
| KXBTC15M-26MAY052330-30 | rejected_actionable | keep_p_ge_60 | no | -130.000000 | 0.659176 | 0.630000 | 0.029176 | 654.661000 | 0.369967 | 0.572942 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_2_4pp |
| KXBTC15M-26MAY071115-15 | rejected_actionable | keep_p_ge_60 | no | -128.000000 | 0.635838 | 0.620000 | 0.015838 | 843.330000 | 0.346131 | 0.982771 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_lt_2pp, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY060500-00 | rejected_actionable | keep_p_ge_60 | no | -126.000000 | 0.674136 | 0.610000 | 0.064136 | 783.254000 | 0.377919 | 0.620318 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, early_stc_ge_780 |
| KXBTC15M-26MAY060930-30 | rejected_actionable | keep_p_ge_60 | yes | -124.000000 | 0.604377 | 0.600000 | 0.004377 | 864.340000 | 0.244982 | 1.150583 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_lt_2pp, near_boundary_absd_lte_030, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY061600-00 | rejected_actionable | keep_p_ge_60 | no | -124.000000 | 0.610883 | 0.600000 | 0.010883 | 717.804000 | 0.229994 | 0.723320 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_lt_2pp, near_boundary_absd_lte_030 |
| KXBTC15M-26MAY070545-45 | rejected_actionable | keep_p_ge_60 | yes | -124.000000 | 0.707647 | 0.600000 | 0.107647 | 855.690000 | 0.462750 | 0.622015 | source:rejected_actionable, reason:keep_p_ge_60, p_70_80, edge_ge_4pp, early_stc_ge_780 |
| KXBTC15M-26MAY071015-15 | rejected_actionable | keep_p_ge_60 | no | -124.000000 | 0.609894 | 0.600000 | 0.009894 | 864.225000 | 0.287274 | 1.102864 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_lt_2pp, near_boundary_absd_lte_030, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY071200-00 | rejected_actionable | keep_p_ge_60 | yes | -124.000000 | 0.606055 | 0.600000 | 0.006055 | 793.821000 | 0.250754 | 1.096302 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_lt_2pp, near_boundary_absd_lte_030, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY060830-30 | rejected_actionable | keep_p_ge_60 | no | -122.000000 | 0.600730 | 0.590000 | 0.010730 | 884.233000 | 0.286154 | 0.943700 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_lt_2pp, near_boundary_absd_lte_030, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY071300-00 | rejected_actionable | keep_p_ge_60 | yes | -122.000000 | 0.636040 | 0.590000 | 0.046040 | 842.515000 | 0.289227 | 1.011545 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, near_boundary_absd_lte_030, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY052245-45 | rejected_actionable | keep_p_ge_60 | no | -118.000000 | 0.643789 | 0.570000 | 0.073789 | 752.490000 | 0.362082 | 0.663374 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp |
| KXBTC15M-26MAY060330-30 | rejected_actionable | keep_p_ge_60 | no | -118.000000 | 0.630880 | 0.570000 | 0.060880 | 884.146000 | 0.287388 | 0.689280 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, near_boundary_absd_lte_030, early_stc_ge_780 |
| KXBTC15M-26MAY061045-45 | rejected_actionable | keep_p_ge_60 | no | -118.000000 | 0.601767 | 0.570000 | 0.031767 | 868.842000 | 0.212683 | 1.191443 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_2_4pp, near_boundary_absd_lte_030, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY070700-00 | rejected_actionable | keep_p_ge_60 | yes | -116.000000 | 0.654812 | 0.560000 | 0.094812 | 869.636000 | 0.375634 | 0.760124 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY060530-30 | rejected_actionable | keep_edge_ge_4pp | yes | -112.000000 | 0.588889 | 0.540000 | 0.048889 | 829.016000 | 0.202598 | 0.884715 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY062245-45 | rejected_actionable | keep_p_ge_60 | no | -112.000000 | 0.605951 | 0.540000 | 0.065951 | 841.408000 | 0.278629 | 0.786584 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY060215-15 | rejected_actionable | keep_edge_ge_4pp | yes | -110.000000 | 0.583024 | 0.530000 | 0.053024 | 884.651000 | 0.228362 | 0.792609 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY062330-30 | rejected_actionable | keep_not_turbulent | yes | -108.000000 | 0.546903 | 0.520000 | 0.026903 | 643.441000 | 0.093136 | 0.717935 | source:rejected_actionable, reason:keep_not_turbulent, p_lt_60, edge_2_4pp, cheap_lte_55c, near_boundary_absd_lte_030 |
| KXBTC15M-26MAY060030-30 | rejected_actionable | keep_p_ge_60 | yes | -106.000000 | 0.617077 | 0.510000 | 0.107077 | 853.033000 | 0.270552 | 0.831869 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY062015-15 | rejected_actionable | keep_not_turbulent | yes | -106.000000 | 0.526847 | 0.510000 | 0.016847 | 869.507000 | 0.086972 | 0.736601 | source:rejected_actionable, reason:keep_not_turbulent, p_lt_60, edge_lt_2pp, cheap_lte_55c, near_boundary_absd_lte_030, early_stc_ge_780 |
| KXBTC15M-26MAY061715-15 | rejected_actionable | keep_p_ge_60 | yes | -104.000000 | 0.633073 | 0.500000 | 0.133073 | 804.817000 | 0.324075 | 0.683095 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, cheap_lte_55c, early_stc_ge_780 |
| KXBTC15M-26MAY052015-15 | rejected_actionable | keep_edge_ge_4pp | no | -102.000000 | 0.567861 | 0.490000 | 0.077861 | 873.050000 | 0.150360 | 0.945709 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY061700-00 | rejected_actionable | keep_edge_ge_4pp | no | -102.000000 | 0.547299 | 0.490000 | 0.057299 | 759.628000 | 0.145303 | 0.799916 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030, high_recross_ge_075 |
| KXBTC15M-26MAY052030-30 | rejected_actionable | keep_edge_ge_4pp | yes | -98.000000 | 0.540780 | 0.470000 | 0.070780 | 879.629000 | 0.144729 | 1.053237 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY070630-30 | rejected_actionable | keep_p_ge_60 | yes | -98.000000 | 0.606974 | 0.470000 | 0.136974 | 875.963000 | 0.230767 | 0.826469 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY062345-45 | rejected_actionable | keep_p_ge_60 | no | -96.000000 | 0.608623 | 0.460000 | 0.148623 | 723.265000 | 0.276153 | 0.675325 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030 |
| KXBTC15M-26MAY070730-30 | rejected_actionable | keep_edge_ge_4pp | yes | -96.000000 | 0.530778 | 0.460000 | 0.070778 | 819.643000 | 0.091964 | 0.936121 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY060445-45 | rejected_actionable | keep_p_ge_60 | no | -94.000000 | 0.636374 | 0.450000 | 0.186374 | 864.716000 | 0.322198 | 0.666569 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, cheap_lte_55c, early_stc_ge_780 |
| KXBTC15M-26MAY070800-00 | rejected_actionable | keep_edge_ge_4pp | yes | -94.000000 | 0.536385 | 0.450000 | 0.086385 | 771.226000 | 0.080069 | 0.865475 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030, high_recross_ge_075 |
| KXBTC15M-26MAY060545-45 | rejected_actionable | keep_p_ge_60 | no | -92.000000 | 0.626642 | 0.440000 | 0.186642 | 807.560000 | 0.323422 | 0.689053 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, cheap_lte_55c, early_stc_ge_780 |
| KXBTC15M-26MAY061945-45 | rejected_actionable | keep_edge_ge_4pp | yes | -88.000000 | 0.542407 | 0.420000 | 0.122407 | 809.092000 | 0.132650 | 0.801256 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY060515-15 | rejected_actionable | keep_edge_ge_4pp | yes | -86.000000 | 0.532512 | 0.410000 | 0.122512 | 825.119000 | 0.141500 | 0.958625 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY070830-30 | rejected_actionable | keep_edge_ge_4pp | yes | -86.000000 | 0.514492 | 0.410000 | 0.104492 | 811.825000 | 0.078942 | 0.952791 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY060345-45 | rejected_actionable | keep_edge_ge_4pp | yes | -80.000000 | 0.515105 | 0.380000 | 0.135105 | 868.842000 | 0.064212 | 0.911219 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY062230-30 | rejected_actionable | keep_p_ge_60 | yes | -80.000000 | 0.718015 | 0.380000 | 0.338015 | 460.951000 | 0.481781 | 0.349672 | source:rejected_actionable, reason:keep_p_ge_60, p_70_80, edge_ge_4pp, cheap_lte_55c, low_recross_lte_045, late_stc_lte_480 |
| KXBTC15M-26MAY070030-30 | rejected_actionable | keep_edge_ge_4pp | no | -70.000000 | 0.523605 | 0.330000 | 0.193605 | 770.113000 | 0.059362 | 0.901651 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030, high_recross_ge_075 |
| KXBTC15M-26MAY062030-30 | rejected_actionable | keep_edge_ge_4pp | yes | -68.000000 | 0.544418 | 0.320000 | 0.224418 | 804.712000 | 0.107412 | 0.680770 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030, early_stc_ge_780 |
| KXBTC15M-26MAY070200-00 | rejected_actionable | keep_edge_ge_4pp | yes | -63.000000 | 0.505710 | 0.300000 | 0.205710 | 532.791000 | 0.019784 | 0.602432 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030 |
| KXBTC15M-26MAY061830-30 | rejected_actionable | keep_edge_ge_4pp | yes | -49.000000 | 0.553162 | 0.230000 | 0.323162 | 653.539000 | 0.098877 | 0.631576 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030 |
| KXBTC15M-26MAY062100-00 | rejected_actionable | keep_p_ge_60 | no | -47.000000 | 0.615588 | 0.220000 | 0.395588 | 683.547000 | 0.321159 | 0.515467 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, cheap_lte_55c |
| KXBTC15M-26MAY070100-00 | rejected_actionable | keep_edge_ge_4pp | no | -47.000000 | 0.505013 | 0.220000 | 0.285013 | 543.305000 | 0.032616 | 0.647900 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030 |
| KXBTC15M-26MAY061745-45 | rejected_actionable | keep_edge_ge_4pp | no | -30.000000 | 0.510383 | 0.140000 | 0.370383 | 668.465000 | 0.021042 | 0.689790 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030 |

## Side-Won Negative-PnL Rows

| market | source | reason | side | net c | p | ask | edge | stc | abs d | recross | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY052315-15 | approved_entry | keep_p_ge_60 | yes | -41.000000 | 0.884999 | 0.810000 | 0.074999 | 469.554000 | 1.030077 | 0.214824 | source:approved_entry, reason:keep_p_ge_60, p_ge_80, edge_ge_4pp, expensive_ge_78c, far_boundary_absd_ge_075, low_recross_lte_045, late_stc_lte_480 |
| KXBTC15M-26MAY061400-00 | approved_entry | keep_p_ge_60 | no | -11.000000 | 0.973640 | 0.890000 | 0.083640 | 208.945000 | 1.815216 | 0.051736 | source:approved_entry, reason:keep_p_ge_60, p_ge_80, edge_ge_4pp, expensive_ge_78c, far_boundary_absd_ge_075, low_recross_lte_045, late_stc_lte_480 |
