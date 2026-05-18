# v28 Target-Coverage Failure Clusters

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T01:06:12.426810+00:00`
- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Forward denominator: `152`
- Surface entries/settled: `112/112`
- Surface net: `-626.000000c`

## Interpretation

- Clusters are mutually exclusive and diagnostic only; they explain loss budget without defining a new promotion rule.
- Direction-wrong rows explain -5007.0c across 48 rows.
- early_no_near_boundary_decay: 16 rows, net -1792.0c, avg -112.0c; NO-side entries taken early near the strike; boundary path can decay/reverse before settlement.
- near_boundary_high_recross: 14 rows, net -1424.0c, avg -101.71428571428571c; Near-strike rows with high recross hazard; directional read is unstable.
- cheap_boundary_tail_overconfidence: 9 rows, net -622.0c, avg -69.11111111111111c; Cheap-side boundary tails looked attractive but were still direction-wrong.
- reconstructed_directional_error: 5 rows, net -593.0c, avg -118.6c; Remaining directional loss rows come from rejected-actionable evidence and need approved-entry confirmation.
- thin_edge_high_confidence_price: 4 rows, net -576.0c, avg -144.0c; High raw probability but little actual entry edge; paying near fair value leaves no error margin.
- 2 side-won negative-PnL rows remain exit/execution shaped, not pure FV direction failures.

## Direction-Wrong Clusters

| cluster | rows | net c | avg c | physical read |
|---|---:|---:|---:|---|
| early_no_near_boundary_decay | 16 | -1792.000000 | -112.000000 | NO-side entries taken early near the strike; boundary path can decay/reverse before settlement. |
| near_boundary_high_recross | 14 | -1424.000000 | -101.714286 | Near-strike rows with high recross hazard; directional read is unstable. |
| cheap_boundary_tail_overconfidence | 9 | -622.000000 | -69.111111 | Cheap-side boundary tails looked attractive but were still direction-wrong. |
| reconstructed_directional_error | 5 | -593.000000 | -118.600000 | Remaining directional loss rows come from rejected-actionable evidence and need approved-entry confirmation. |
| thin_edge_high_confidence_price | 4 | -576.000000 | -144.000000 | High raw probability but little actual entry edge; paying near fair value leaves no error margin. |

## early_no_near_boundary_decay Worst Rows

| market | side | p | ask | edge | stc | abs d | recross | net c | source | reason |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY060630-30 | no | 0.675344 | 0.660000 | 0.015344 | 868.927000 | 0.393798 | 0.762043 | -136.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY060245-45 | no | 0.660829 | 0.650000 | 0.010829 | 868.740000 | 0.346255 | 0.663720 | -134.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY071115-15 | no | 0.635838 | 0.620000 | 0.015838 | 843.330000 | 0.346131 | 0.982771 | -128.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY060500-00 | no | 0.674136 | 0.610000 | 0.064136 | 783.254000 | 0.377919 | 0.620318 | -126.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY071015-15 | no | 0.609894 | 0.600000 | 0.009894 | 864.225000 | 0.287274 | 1.102864 | -124.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY060830-30 | no | 0.600730 | 0.590000 | 0.010730 | 884.233000 | 0.286154 | 0.943700 | -122.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY052245-45 | no | 0.643789 | 0.570000 | 0.073789 | 752.490000 | 0.362082 | 0.663374 | -118.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY060330-30 | no | 0.630880 | 0.570000 | 0.060880 | 884.146000 | 0.287388 | 0.689280 | -118.000000 | rejected_actionable | keep_p_ge_60 |

## near_boundary_high_recross Worst Rows

| market | side | p | ask | edge | stc | abs d | recross | net c | source | reason |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY060930-30 | yes | 0.604377 | 0.600000 | 0.004377 | 864.340000 | 0.244982 | 1.150583 | -124.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY071200-00 | yes | 0.606055 | 0.600000 | 0.006055 | 793.821000 | 0.250754 | 1.096302 | -124.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY071300-00 | yes | 0.636040 | 0.590000 | 0.046040 | 842.515000 | 0.289227 | 1.011545 | -122.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY060530-30 | yes | 0.588889 | 0.540000 | 0.048889 | 829.016000 | 0.202598 | 0.884715 | -112.000000 | rejected_actionable | keep_edge_ge_4pp |
| KXBTC15M-26MAY060215-15 | yes | 0.583024 | 0.530000 | 0.053024 | 884.651000 | 0.228362 | 0.792609 | -110.000000 | rejected_actionable | keep_edge_ge_4pp |
| KXBTC15M-26MAY060030-30 | yes | 0.617077 | 0.510000 | 0.107077 | 853.033000 | 0.270552 | 0.831869 | -106.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY052030-30 | yes | 0.540780 | 0.470000 | 0.070780 | 879.629000 | 0.144729 | 1.053237 | -98.000000 | rejected_actionable | keep_edge_ge_4pp |
| KXBTC15M-26MAY070630-30 | yes | 0.606974 | 0.470000 | 0.136974 | 875.963000 | 0.230767 | 0.826469 | -98.000000 | rejected_actionable | keep_p_ge_60 |

## cheap_boundary_tail_overconfidence Worst Rows

| market | side | p | ask | edge | stc | abs d | recross | net c | source | reason |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY062330-30 | yes | 0.546903 | 0.520000 | 0.026903 | 643.441000 | 0.093136 | 0.717935 | -108.000000 | rejected_actionable | keep_not_turbulent |
| KXBTC15M-26MAY062015-15 | yes | 0.526847 | 0.510000 | 0.016847 | 869.507000 | 0.086972 | 0.736601 | -106.000000 | rejected_actionable | keep_not_turbulent |
| KXBTC15M-26MAY061715-15 | yes | 0.633073 | 0.500000 | 0.133073 | 804.817000 | 0.324075 | 0.683095 | -104.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY062030-30 | yes | 0.544418 | 0.320000 | 0.224418 | 804.712000 | 0.107412 | 0.680770 | -68.000000 | rejected_actionable | keep_edge_ge_4pp |
| KXBTC15M-26MAY070200-00 | yes | 0.505710 | 0.300000 | 0.205710 | 532.791000 | 0.019784 | 0.602432 | -63.000000 | rejected_actionable | keep_edge_ge_4pp |
| KXBTC15M-26MAY061830-30 | yes | 0.553162 | 0.230000 | 0.323162 | 653.539000 | 0.098877 | 0.631576 | -49.000000 | rejected_actionable | keep_edge_ge_4pp |
| KXBTC15M-26MAY062100-00 | no | 0.615588 | 0.220000 | 0.395588 | 683.547000 | 0.321159 | 0.515467 | -47.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY070100-00 | no | 0.505013 | 0.220000 | 0.285013 | 543.305000 | 0.032616 | 0.647900 | -47.000000 | rejected_actionable | keep_edge_ge_4pp |

## reconstructed_directional_error Worst Rows

| market | side | p | ask | edge | stc | abs d | recross | net c | source | reason |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY071230-30 | no | 0.729882 | 0.700000 | 0.029882 | 863.492000 | 0.573733 | 0.815016 | -143.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY052330-30 | no | 0.659176 | 0.630000 | 0.029176 | 654.661000 | 0.369967 | 0.572942 | -130.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY070545-45 | yes | 0.707647 | 0.600000 | 0.107647 | 855.690000 | 0.462750 | 0.622015 | -124.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY070700-00 | yes | 0.654812 | 0.560000 | 0.094812 | 869.636000 | 0.375634 | 0.760124 | -116.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY062230-30 | yes | 0.718015 | 0.380000 | 0.338015 | 460.951000 | 0.481781 | 0.349672 | -80.000000 | rejected_actionable | keep_p_ge_60 |

## thin_edge_high_confidence_price Worst Rows

| market | side | p | ask | edge | stc | abs d | recross | net c | source | reason |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY060100-00 | yes | 0.799928 | 0.790000 | 0.009928 | 684.076000 | 0.694496 | 0.407561 | -161.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY061100-00 | yes | 0.740374 | 0.740000 | 0.000374 | 865.321000 | 0.597049 | 0.809587 | -151.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY061230-30 | yes | 0.681329 | 0.680000 | 0.001329 | 829.291000 | 0.451740 | 0.862457 | -140.000000 | rejected_actionable | keep_p_ge_60 |
| KXBTC15M-26MAY061600-00 | no | 0.610883 | 0.600000 | 0.010883 | 717.804000 | 0.229994 | 0.723320 | -124.000000 | rejected_actionable | keep_p_ge_60 |

## Side-Won Negative-PnL Rows

| market | side | p | ask | edge | net c | source | reason |
|---|---|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY052315-15 | yes | 0.884999 | 0.810000 | 0.074999 | -41.000000 | approved_entry | keep_p_ge_60 |
| KXBTC15M-26MAY061400-00 | no | 0.973640 | 0.890000 | 0.083640 | -11.000000 | approved_entry | keep_p_ge_60 |
