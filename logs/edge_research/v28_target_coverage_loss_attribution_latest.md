# v28 Target-Coverage Loss Attribution

Forward-only physical attribution for the current target-coverage surface.

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Forward denominator: `152`

## Interpretation

- Target-coverage forward loss rows: 48.
- Worst repeated physical tags are diagnostic only; new rules must be frozen before scoring.
- early_stc_ge_720: settled 82, W/L 44/38, net -856.0c.
- thin_edge_lt_3pp: settled 33, W/L 18/15, net -808.0c.
- reason_keep_p_ge_60: settled 76, W/L 47/29, net -715.0c.
- high_recross_ge_075: settled 54, W/L 27/27, net -625.0c.
- extreme_recross_ge_090: settled 25, W/L 11/14, net -496.0c.

## Tag Summaries

| tag | rows | settled | W/L | net c | avg c |
|---|---:|---:|---:|---:|---:|
| early_stc_ge_720 | 82 | 82 | 44/38 | -856.000000 | -10.439024 |
| thin_edge_lt_3pp | 33 | 33 | 18/15 | -808.000000 | -24.484848 |
| reason_keep_p_ge_60 | 76 | 76 | 47/29 | -715.000000 | -9.407895 |
| all | 112 | 112 | 64/48 | -626.000000 | -5.589286 |
| high_recross_ge_075 | 54 | 54 | 27/27 | -625.000000 | -11.574074 |
| extreme_recross_ge_090 | 25 | 25 | 11/14 | -496.000000 | -19.840000 |
| cheap_ask_lt_55 | 47 | 47 | 19/28 | -459.000000 | -9.765957 |
| weak_raw_p_lt_58 | 26 | 26 | 9/17 | -445.000000 | -17.115385 |
| large_edge_ge_10pp | 30 | 30 | 11/19 | -395.000000 | -13.166667 |
| mid_raw_p_58_65 | 41 | 41 | 21/20 | -330.000000 | -8.048780 |
| no_side | 52 | 52 | 30/22 | -323.000000 | -6.211538 |
| near_strike_absd_lte_025 | 41 | 41 | 18/23 | -307.000000 | -7.487805 |
| yes_side | 60 | 60 | 34/26 | -303.000000 | -5.050000 |
| reason_keep_not_turbulent | 4 | 4 | 2/2 | -52.000000 | -13.000000 |
| paid_high_price_thin_edge | 15 | 15 | 12/3 | 70.000000 | 4.666667 |
| weak_boundary_turbulence | 24 | 24 | 12/12 | 104.000000 | 4.333333 |
| reason_keep_edge_ge_4pp | 32 | 32 | 15/17 | 141.000000 | 4.406250 |
| high_raw_p_ge_65 | 45 | 45 | 34/11 | 149.000000 | 3.311111 |
| expensive_ask_ge_70 | 23 | 23 | 20/3 | 207.000000 | 9.000000 |
| far_from_strike_absd_gte_075 | 12 | 12 | 12/0 | 241.000000 | 20.083333 |

## Loss Rows

| market | side | p | ask | edge | stc | abs d | recross | net c | reason | tags |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY060100-00 | yes | 0.799928 | 0.790000 | 0.009928 | 684.076000 | 0.694496 | 0.407561 | -161.000000 | keep_p_ge_60 | all, high_raw_p_ge_65, expensive_ask_ge_70, thin_edge_lt_3pp, yes_side, reason_keep_p_ge_60, paid_high_price_thin_edge |
| KXBTC15M-26MAY061100-00 | yes | 0.740374 | 0.740000 | 0.000374 | 865.321000 | 0.597049 | 0.809587 | -151.000000 | keep_p_ge_60 | all, high_raw_p_ge_65, expensive_ask_ge_70, thin_edge_lt_3pp, early_stc_ge_720, high_recross_ge_075, yes_side, reason_keep_p_ge_60, paid_high_price_thin_edge |
| KXBTC15M-26MAY071230-30 | no | 0.729882 | 0.700000 | 0.029882 | 863.492000 | 0.573733 | 0.815016 | -143.000000 | keep_p_ge_60 | all, high_raw_p_ge_65, expensive_ask_ge_70, thin_edge_lt_3pp, early_stc_ge_720, high_recross_ge_075, no_side, reason_keep_p_ge_60, paid_high_price_thin_edge |
| KXBTC15M-26MAY061230-30 | yes | 0.681329 | 0.680000 | 0.001329 | 829.291000 | 0.451740 | 0.862457 | -140.000000 | keep_p_ge_60 | all, high_raw_p_ge_65, thin_edge_lt_3pp, early_stc_ge_720, high_recross_ge_075, yes_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY060630-30 | no | 0.675344 | 0.660000 | 0.015344 | 868.927000 | 0.393798 | 0.762043 | -136.000000 | keep_p_ge_60 | all, high_raw_p_ge_65, thin_edge_lt_3pp, early_stc_ge_720, high_recross_ge_075, no_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY060245-45 | no | 0.660829 | 0.650000 | 0.010829 | 868.740000 | 0.346255 | 0.663720 | -134.000000 | keep_p_ge_60 | all, high_raw_p_ge_65, thin_edge_lt_3pp, early_stc_ge_720, no_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY052330-30 | no | 0.659176 | 0.630000 | 0.029176 | 654.661000 | 0.369967 | 0.572942 | -130.000000 | keep_p_ge_60 | all, high_raw_p_ge_65, thin_edge_lt_3pp, no_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY071115-15 | no | 0.635838 | 0.620000 | 0.015838 | 843.330000 | 0.346131 | 0.982771 | -128.000000 | keep_p_ge_60 | all, mid_raw_p_58_65, thin_edge_lt_3pp, early_stc_ge_720, high_recross_ge_075, extreme_recross_ge_090, no_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY060500-00 | no | 0.674136 | 0.610000 | 0.064136 | 783.254000 | 0.377919 | 0.620318 | -126.000000 | keep_p_ge_60 | all, high_raw_p_ge_65, early_stc_ge_720, no_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY060930-30 | yes | 0.604377 | 0.600000 | 0.004377 | 864.340000 | 0.244982 | 1.150583 | -124.000000 | keep_p_ge_60 | all, mid_raw_p_58_65, thin_edge_lt_3pp, early_stc_ge_720, near_strike_absd_lte_025, high_recross_ge_075, extreme_recross_ge_090, yes_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY061600-00 | no | 0.610883 | 0.600000 | 0.010883 | 717.804000 | 0.229994 | 0.723320 | -124.000000 | keep_p_ge_60 | all, mid_raw_p_58_65, thin_edge_lt_3pp, near_strike_absd_lte_025, no_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY070545-45 | yes | 0.707647 | 0.600000 | 0.107647 | 855.690000 | 0.462750 | 0.622015 | -124.000000 | keep_p_ge_60 | all, high_raw_p_ge_65, large_edge_ge_10pp, early_stc_ge_720, yes_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY071015-15 | no | 0.609894 | 0.600000 | 0.009894 | 864.225000 | 0.287274 | 1.102864 | -124.000000 | keep_p_ge_60 | all, mid_raw_p_58_65, thin_edge_lt_3pp, early_stc_ge_720, high_recross_ge_075, extreme_recross_ge_090, no_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY071200-00 | yes | 0.606055 | 0.600000 | 0.006055 | 793.821000 | 0.250754 | 1.096302 | -124.000000 | keep_p_ge_60 | all, mid_raw_p_58_65, thin_edge_lt_3pp, early_stc_ge_720, high_recross_ge_075, extreme_recross_ge_090, yes_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY060830-30 | no | 0.600730 | 0.590000 | 0.010730 | 884.233000 | 0.286154 | 0.943700 | -122.000000 | keep_p_ge_60 | all, mid_raw_p_58_65, thin_edge_lt_3pp, early_stc_ge_720, high_recross_ge_075, extreme_recross_ge_090, no_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY071300-00 | yes | 0.636040 | 0.590000 | 0.046040 | 842.515000 | 0.289227 | 1.011545 | -122.000000 | keep_p_ge_60 | all, mid_raw_p_58_65, early_stc_ge_720, high_recross_ge_075, extreme_recross_ge_090, yes_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY052245-45 | no | 0.643789 | 0.570000 | 0.073789 | 752.490000 | 0.362082 | 0.663374 | -118.000000 | keep_p_ge_60 | all, mid_raw_p_58_65, early_stc_ge_720, no_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY060330-30 | no | 0.630880 | 0.570000 | 0.060880 | 884.146000 | 0.287388 | 0.689280 | -118.000000 | keep_p_ge_60 | all, mid_raw_p_58_65, early_stc_ge_720, no_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY061045-45 | no | 0.601767 | 0.570000 | 0.031767 | 868.842000 | 0.212683 | 1.191443 | -118.000000 | keep_p_ge_60 | all, mid_raw_p_58_65, early_stc_ge_720, near_strike_absd_lte_025, high_recross_ge_075, extreme_recross_ge_090, no_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY070700-00 | yes | 0.654812 | 0.560000 | 0.094812 | 869.636000 | 0.375634 | 0.760124 | -116.000000 | keep_p_ge_60 | all, high_raw_p_ge_65, early_stc_ge_720, high_recross_ge_075, yes_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY060530-30 | yes | 0.588889 | 0.540000 | 0.048889 | 829.016000 | 0.202598 | 0.884715 | -112.000000 | keep_edge_ge_4pp | all, mid_raw_p_58_65, cheap_ask_lt_55, early_stc_ge_720, near_strike_absd_lte_025, high_recross_ge_075, yes_side, reason_keep_edge_ge_4pp, weak_boundary_turbulence |
| KXBTC15M-26MAY062245-45 | no | 0.605951 | 0.540000 | 0.065951 | 841.408000 | 0.278629 | 0.786584 | -112.000000 | keep_p_ge_60 | all, mid_raw_p_58_65, cheap_ask_lt_55, early_stc_ge_720, high_recross_ge_075, no_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY060215-15 | yes | 0.583024 | 0.530000 | 0.053024 | 884.651000 | 0.228362 | 0.792609 | -110.000000 | keep_edge_ge_4pp | all, mid_raw_p_58_65, cheap_ask_lt_55, early_stc_ge_720, near_strike_absd_lte_025, high_recross_ge_075, yes_side, reason_keep_edge_ge_4pp, weak_boundary_turbulence |
| KXBTC15M-26MAY062330-30 | yes | 0.546903 | 0.520000 | 0.026903 | 643.441000 | 0.093136 | 0.717935 | -108.000000 | keep_not_turbulent | all, weak_raw_p_lt_58, cheap_ask_lt_55, thin_edge_lt_3pp, near_strike_absd_lte_025, yes_side, reason_keep_not_turbulent |
| KXBTC15M-26MAY060030-30 | yes | 0.617077 | 0.510000 | 0.107077 | 853.033000 | 0.270552 | 0.831869 | -106.000000 | keep_p_ge_60 | all, mid_raw_p_58_65, cheap_ask_lt_55, large_edge_ge_10pp, early_stc_ge_720, high_recross_ge_075, yes_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY062015-15 | yes | 0.526847 | 0.510000 | 0.016847 | 869.507000 | 0.086972 | 0.736601 | -106.000000 | keep_not_turbulent | all, weak_raw_p_lt_58, cheap_ask_lt_55, thin_edge_lt_3pp, early_stc_ge_720, near_strike_absd_lte_025, yes_side, reason_keep_not_turbulent |
| KXBTC15M-26MAY061715-15 | yes | 0.633073 | 0.500000 | 0.133073 | 804.817000 | 0.324075 | 0.683095 | -104.000000 | keep_p_ge_60 | all, mid_raw_p_58_65, cheap_ask_lt_55, large_edge_ge_10pp, early_stc_ge_720, yes_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY052015-15 | no | 0.567861 | 0.490000 | 0.077861 | 873.050000 | 0.150360 | 0.945709 | -102.000000 | keep_edge_ge_4pp | all, weak_raw_p_lt_58, cheap_ask_lt_55, early_stc_ge_720, near_strike_absd_lte_025, high_recross_ge_075, extreme_recross_ge_090, no_side, reason_keep_edge_ge_4pp, weak_boundary_turbulence |
| KXBTC15M-26MAY061700-00 | no | 0.547299 | 0.490000 | 0.057299 | 759.628000 | 0.145303 | 0.799916 | -102.000000 | keep_edge_ge_4pp | all, weak_raw_p_lt_58, cheap_ask_lt_55, early_stc_ge_720, near_strike_absd_lte_025, high_recross_ge_075, no_side, reason_keep_edge_ge_4pp, weak_boundary_turbulence |
| KXBTC15M-26MAY052030-30 | yes | 0.540780 | 0.470000 | 0.070780 | 879.629000 | 0.144729 | 1.053237 | -98.000000 | keep_edge_ge_4pp | all, weak_raw_p_lt_58, cheap_ask_lt_55, early_stc_ge_720, near_strike_absd_lte_025, high_recross_ge_075, extreme_recross_ge_090, yes_side, reason_keep_edge_ge_4pp, weak_boundary_turbulence |
| KXBTC15M-26MAY070630-30 | yes | 0.606974 | 0.470000 | 0.136974 | 875.963000 | 0.230767 | 0.826469 | -98.000000 | keep_p_ge_60 | all, mid_raw_p_58_65, cheap_ask_lt_55, large_edge_ge_10pp, early_stc_ge_720, near_strike_absd_lte_025, high_recross_ge_075, yes_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY062345-45 | no | 0.608623 | 0.460000 | 0.148623 | 723.265000 | 0.276153 | 0.675325 | -96.000000 | keep_p_ge_60 | all, mid_raw_p_58_65, cheap_ask_lt_55, large_edge_ge_10pp, early_stc_ge_720, no_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY070730-30 | yes | 0.530778 | 0.460000 | 0.070778 | 819.643000 | 0.091964 | 0.936121 | -96.000000 | keep_edge_ge_4pp | all, weak_raw_p_lt_58, cheap_ask_lt_55, early_stc_ge_720, near_strike_absd_lte_025, high_recross_ge_075, extreme_recross_ge_090, yes_side, reason_keep_edge_ge_4pp, weak_boundary_turbulence |
| KXBTC15M-26MAY060445-45 | no | 0.636374 | 0.450000 | 0.186374 | 864.716000 | 0.322198 | 0.666569 | -94.000000 | keep_p_ge_60 | all, mid_raw_p_58_65, cheap_ask_lt_55, large_edge_ge_10pp, early_stc_ge_720, no_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY070800-00 | yes | 0.536385 | 0.450000 | 0.086385 | 771.226000 | 0.080069 | 0.865475 | -94.000000 | keep_edge_ge_4pp | all, weak_raw_p_lt_58, cheap_ask_lt_55, early_stc_ge_720, near_strike_absd_lte_025, high_recross_ge_075, yes_side, reason_keep_edge_ge_4pp, weak_boundary_turbulence |
| KXBTC15M-26MAY060545-45 | no | 0.626642 | 0.440000 | 0.186642 | 807.560000 | 0.323422 | 0.689053 | -92.000000 | keep_p_ge_60 | all, mid_raw_p_58_65, cheap_ask_lt_55, large_edge_ge_10pp, early_stc_ge_720, no_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY061945-45 | yes | 0.542407 | 0.420000 | 0.122407 | 809.092000 | 0.132650 | 0.801256 | -88.000000 | keep_edge_ge_4pp | all, weak_raw_p_lt_58, cheap_ask_lt_55, large_edge_ge_10pp, early_stc_ge_720, near_strike_absd_lte_025, high_recross_ge_075, yes_side, reason_keep_edge_ge_4pp, weak_boundary_turbulence |
| KXBTC15M-26MAY060515-15 | yes | 0.532512 | 0.410000 | 0.122512 | 825.119000 | 0.141500 | 0.958625 | -86.000000 | keep_edge_ge_4pp | all, weak_raw_p_lt_58, cheap_ask_lt_55, large_edge_ge_10pp, early_stc_ge_720, near_strike_absd_lte_025, high_recross_ge_075, extreme_recross_ge_090, yes_side, reason_keep_edge_ge_4pp, weak_boundary_turbulence |
| KXBTC15M-26MAY070830-30 | yes | 0.514492 | 0.410000 | 0.104492 | 811.825000 | 0.078942 | 0.952791 | -86.000000 | keep_edge_ge_4pp | all, weak_raw_p_lt_58, cheap_ask_lt_55, large_edge_ge_10pp, early_stc_ge_720, near_strike_absd_lte_025, high_recross_ge_075, extreme_recross_ge_090, yes_side, reason_keep_edge_ge_4pp, weak_boundary_turbulence |
| KXBTC15M-26MAY060345-45 | yes | 0.515105 | 0.380000 | 0.135105 | 868.842000 | 0.064212 | 0.911219 | -80.000000 | keep_edge_ge_4pp | all, weak_raw_p_lt_58, cheap_ask_lt_55, large_edge_ge_10pp, early_stc_ge_720, near_strike_absd_lte_025, high_recross_ge_075, extreme_recross_ge_090, yes_side, reason_keep_edge_ge_4pp, weak_boundary_turbulence |
| KXBTC15M-26MAY062230-30 | yes | 0.718015 | 0.380000 | 0.338015 | 460.951000 | 0.481781 | 0.349672 | -80.000000 | keep_p_ge_60 | all, high_raw_p_ge_65, cheap_ask_lt_55, large_edge_ge_10pp, yes_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY070030-30 | no | 0.523605 | 0.330000 | 0.193605 | 770.113000 | 0.059362 | 0.901651 | -70.000000 | keep_edge_ge_4pp | all, weak_raw_p_lt_58, cheap_ask_lt_55, large_edge_ge_10pp, early_stc_ge_720, near_strike_absd_lte_025, high_recross_ge_075, extreme_recross_ge_090, no_side, reason_keep_edge_ge_4pp, weak_boundary_turbulence |
| KXBTC15M-26MAY062030-30 | yes | 0.544418 | 0.320000 | 0.224418 | 804.712000 | 0.107412 | 0.680770 | -68.000000 | keep_edge_ge_4pp | all, weak_raw_p_lt_58, cheap_ask_lt_55, large_edge_ge_10pp, early_stc_ge_720, near_strike_absd_lte_025, yes_side, reason_keep_edge_ge_4pp |
| KXBTC15M-26MAY070200-00 | yes | 0.505710 | 0.300000 | 0.205710 | 532.791000 | 0.019784 | 0.602432 | -63.000000 | keep_edge_ge_4pp | all, weak_raw_p_lt_58, cheap_ask_lt_55, large_edge_ge_10pp, near_strike_absd_lte_025, yes_side, reason_keep_edge_ge_4pp |
| KXBTC15M-26MAY061830-30 | yes | 0.553162 | 0.230000 | 0.323162 | 653.539000 | 0.098877 | 0.631576 | -49.000000 | keep_edge_ge_4pp | all, weak_raw_p_lt_58, cheap_ask_lt_55, large_edge_ge_10pp, near_strike_absd_lte_025, yes_side, reason_keep_edge_ge_4pp |
| KXBTC15M-26MAY062100-00 | no | 0.615588 | 0.220000 | 0.395588 | 683.547000 | 0.321159 | 0.515467 | -47.000000 | keep_p_ge_60 | all, mid_raw_p_58_65, cheap_ask_lt_55, large_edge_ge_10pp, no_side, reason_keep_p_ge_60 |
| KXBTC15M-26MAY070100-00 | no | 0.505013 | 0.220000 | 0.285013 | 543.305000 | 0.032616 | 0.647900 | -47.000000 | keep_edge_ge_4pp | all, weak_raw_p_lt_58, cheap_ask_lt_55, large_edge_ge_10pp, near_strike_absd_lte_025, no_side, reason_keep_edge_ge_4pp |
| KXBTC15M-26MAY061745-45 | no | 0.510383 | 0.140000 | 0.370383 | 668.465000 | 0.021042 | 0.689790 | -30.000000 | keep_edge_ge_4pp | all, weak_raw_p_lt_58, cheap_ask_lt_55, large_edge_ge_10pp, near_strike_absd_lte_025, no_side, reason_keep_edge_ge_4pp |
