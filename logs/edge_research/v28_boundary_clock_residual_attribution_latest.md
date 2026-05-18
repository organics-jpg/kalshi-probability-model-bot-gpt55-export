# v28 Boundary-Clock Residual Attribution

Diagnostic-only: no live bot changes and no orders.

- Forward denominator: `152`

## Interpretation

- Target surface has 112 entries and 112 settled rows.
- Boundary-clock hazard explains 26 direction-wrong rows.
- Residual non-clock direction errors: 22 rows.
- Next FV work should focus only on residual non-clock errors if frozen boundary-clock validation holds up.

## Summaries

| slice | rows | settled | W/L | net c |
|---|---:|---:|---:|---:|
| target | 112 | 112 | 64/48 | -626.000000 |
| clock | 48 | 48 | 22/26 | -933.000000 |
| non_clock | 64 | 64 | 42/22 | 307.000000 |
| direction_wrong | 48 | 48 | 0/48 | -5007.000000 |
| clock_wrong | 26 | 26 | 0/26 | -2896.000000 |
| residual_wrong | 22 | 22 | 0/22 | -2111.000000 |

## Residual Wrong Rows

| market | source | side | net c | raw p | adj p | ask | edge | stc | abs d | recross | tags |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071230-30 | rejected_actionable | no | -143.000000 | 0.729882 | 0.729882 | 0.700000 | 0.029882 | 863.492000 | 0.573733 | 0.815016 | source:rejected_actionable, reason:keep_p_ge_60, p_70_80, edge_2_4pp, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY052330-30 | rejected_actionable | no | -130.000000 | 0.659176 | 0.659176 | 0.630000 | 0.029176 | 654.661000 | 0.369967 | 0.572942 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_2_4pp |
| KXBTC15M-26MAY071115-15 | rejected_actionable | no | -128.000000 | 0.635838 | 0.635838 | 0.620000 | 0.015838 | 843.330000 | 0.346131 | 0.982771 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_lt_2pp, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY060500-00 | rejected_actionable | no | -126.000000 | 0.674136 | 0.674136 | 0.610000 | 0.064136 | 783.254000 | 0.377919 | 0.620318 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, early_stc_ge_780 |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | -124.000000 | 0.610883 | 0.610883 | 0.600000 | 0.010883 | 717.804000 | 0.229994 | 0.723320 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_lt_2pp, near_boundary_absd_lte_030 |
| KXBTC15M-26MAY070545-45 | rejected_actionable | yes | -124.000000 | 0.707647 | 0.707647 | 0.600000 | 0.107647 | 855.690000 | 0.462750 | 0.622015 | source:rejected_actionable, reason:keep_p_ge_60, p_70_80, edge_ge_4pp, early_stc_ge_780 |
| KXBTC15M-26MAY052245-45 | rejected_actionable | no | -118.000000 | 0.643789 | 0.643789 | 0.570000 | 0.073789 | 752.490000 | 0.362082 | 0.663374 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp |
| KXBTC15M-26MAY060330-30 | rejected_actionable | no | -118.000000 | 0.630880 | 0.630880 | 0.570000 | 0.060880 | 884.146000 | 0.287388 | 0.689280 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, near_boundary_absd_lte_030, early_stc_ge_780 |
| KXBTC15M-26MAY070700-00 | rejected_actionable | yes | -116.000000 | 0.654812 | 0.654812 | 0.560000 | 0.094812 | 869.636000 | 0.375634 | 0.760124 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, high_recross_ge_075, early_stc_ge_780 |
| KXBTC15M-26MAY062330-30 | rejected_actionable | yes | -108.000000 | 0.546903 | 0.546903 | 0.520000 | 0.026903 | 643.441000 | 0.093136 | 0.717935 | source:rejected_actionable, reason:keep_not_turbulent, p_lt_60, edge_2_4pp, cheap_lte_55c, near_boundary_absd_lte_030 |
| KXBTC15M-26MAY062015-15 | rejected_actionable | yes | -106.000000 | 0.526847 | 0.526847 | 0.510000 | 0.016847 | 869.507000 | 0.086972 | 0.736601 | source:rejected_actionable, reason:keep_not_turbulent, p_lt_60, edge_lt_2pp, cheap_lte_55c, near_boundary_absd_lte_030, early_stc_ge_780 |
| KXBTC15M-26MAY061715-15 | rejected_actionable | yes | -104.000000 | 0.633073 | 0.633073 | 0.500000 | 0.133073 | 804.817000 | 0.324075 | 0.683095 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, cheap_lte_55c, early_stc_ge_780 |
| KXBTC15M-26MAY062345-45 | rejected_actionable | no | -96.000000 | 0.608623 | 0.608623 | 0.460000 | 0.148623 | 723.265000 | 0.276153 | 0.675325 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030 |
| KXBTC15M-26MAY060445-45 | rejected_actionable | no | -94.000000 | 0.636374 | 0.636374 | 0.450000 | 0.186374 | 864.716000 | 0.322198 | 0.666569 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, cheap_lte_55c, early_stc_ge_780 |
| KXBTC15M-26MAY060545-45 | rejected_actionable | no | -92.000000 | 0.626642 | 0.626642 | 0.440000 | 0.186642 | 807.560000 | 0.323422 | 0.689053 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, cheap_lte_55c, early_stc_ge_780 |
| KXBTC15M-26MAY062230-30 | rejected_actionable | yes | -80.000000 | 0.718015 | 0.718015 | 0.380000 | 0.338015 | 460.951000 | 0.481781 | 0.349672 | source:rejected_actionable, reason:keep_p_ge_60, p_70_80, edge_ge_4pp, cheap_lte_55c, low_recross_lte_045, late_stc_lte_480 |
| KXBTC15M-26MAY062030-30 | rejected_actionable | yes | -68.000000 | 0.544418 | 0.544418 | 0.320000 | 0.224418 | 804.712000 | 0.107412 | 0.680770 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030, early_stc_ge_780 |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | -63.000000 | 0.505710 | 0.505710 | 0.300000 | 0.205710 | 532.791000 | 0.019784 | 0.602432 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030 |
| KXBTC15M-26MAY061830-30 | rejected_actionable | yes | -49.000000 | 0.553162 | 0.553162 | 0.230000 | 0.323162 | 653.539000 | 0.098877 | 0.631576 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030 |
| KXBTC15M-26MAY062100-00 | rejected_actionable | no | -47.000000 | 0.615588 | 0.615588 | 0.220000 | 0.395588 | 683.547000 | 0.321159 | 0.515467 | source:rejected_actionable, reason:keep_p_ge_60, p_60_70, edge_ge_4pp, cheap_lte_55c |
| KXBTC15M-26MAY070100-00 | rejected_actionable | no | -47.000000 | 0.505013 | 0.505013 | 0.220000 | 0.285013 | 543.305000 | 0.032616 | 0.647900 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030 |
| KXBTC15M-26MAY061745-45 | rejected_actionable | no | -30.000000 | 0.510383 | 0.510383 | 0.140000 | 0.370383 | 668.465000 | 0.021042 | 0.689790 | source:rejected_actionable, reason:keep_edge_ge_4pp, p_lt_60, edge_ge_4pp, cheap_lte_55c, near_boundary_absd_lte_030 |

## Residual Wrong Tag Rollups

| tag | rows | settled | W/L | net c |
|---|---:|---:|---:|---:|
| source:rejected_actionable | 22 | 22 | 0/22 | -2111.000000 |
| reason:keep_p_ge_60 | 15 | 15 | 0/15 | -1640.000000 |
| edge_ge_4pp | 16 | 16 | 0/16 | -1372.000000 |
| p_60_70 | 12 | 12 | 0/12 | -1293.000000 |
| early_stc_ge_780 | 11 | 11 | 0/11 | -1219.000000 |
| cheap_lte_55c | 13 | 13 | 0/13 | -984.000000 |
| near_boundary_absd_lte_030 | 10 | 10 | 0/10 | -809.000000 |
| p_lt_60 | 7 | 7 | 0/7 | -471.000000 |
| high_recross_ge_075 | 3 | 3 | 0/3 | -387.000000 |
| edge_2_4pp | 3 | 3 | 0/3 | -381.000000 |
| edge_lt_2pp | 3 | 3 | 0/3 | -358.000000 |
| p_70_80 | 3 | 3 | 0/3 | -347.000000 |
| reason:keep_edge_ge_4pp | 5 | 5 | 0/5 | -257.000000 |
| reason:keep_not_turbulent | 2 | 2 | 0/2 | -214.000000 |
| low_recross_lte_045 | 1 | 1 | 0/1 | -80.000000 |
| late_stc_lte_480 | 1 | 1 | 0/1 | -80.000000 |
