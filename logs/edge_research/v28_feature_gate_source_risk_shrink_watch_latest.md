# v28 Feature-Gate Source-Risk Shrink Watch

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T10:28:16.046064+00:00`
- Watch freeze UTC: `2026-05-07T06:51:18.613633+00:00`
- Feature freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- This is a notional-shrink watch using only observable source-risk features; source labels remain audit-only.
- The official row-count source gate is still a hard promotion blocker even if exposure source share improves.
- diagnostic_feature_window_entry: best risk_quarter_step has 40/54 entries, 40 settled, W/L 24/16, weighted net 222.75c, row/exposure source share 0.45/0.2786885245901639, cushion 2, blockers ['coverage_too_low', 'row_source_share_gt_35pct', 'weighted_full_loss_cushion_lt_3'].
- diagnostic_feature_window_bridge: best risk_quarter_step has 40/54 entries, 40 settled, W/L 24/16, weighted net 222.75c, row/exposure source share 0.45/0.2786885245901639, cushion 2, blockers ['coverage_too_low', 'row_source_share_gt_35pct', 'weighted_full_loss_cushion_lt_3'].
- post_source_risk_birth_entry: best risk_linear_30 has 3/5 entries, 3 settled, W/L 2/1, weighted net -13.499999999999996c, row/exposure source share 0.6666666666666666/0.4666666666666667, cushion 0, blockers ['settled_lt_30', 'coverage_too_low', 'weighted_net_not_positive', 'row_source_share_gt_35pct', 'exposure_source_share_gt_35pct', 'weighted_full_loss_cushion_lt_3'].
- post_source_risk_birth_bridge: best risk_linear_30 has 3/5 entries, 3 settled, W/L 2/1, weighted net -13.499999999999996c, row/exposure source share 0.6666666666666666/0.4666666666666667, cushion 0, blockers ['settled_lt_30', 'coverage_too_low', 'weighted_net_not_positive', 'row_source_share_gt_35pct', 'exposure_source_share_gt_35pct', 'weighted_full_loss_cushion_lt_3'].

## diagnostic_feature_window_entry

- Base rule: `raw03_recross70_abs075`
- Selected entries: `40`
- Future denominator: `54`

| rank | policy | settled | W/L | coverage | weighted net | row source | exposure source | exposure rows | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | risk_quarter_step | 40 | 24/16 | 74.074074 | 222.750000 | 0.450000 | 0.278689 | 30.500000 | 2 | coverage_too_low, row_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 2 | risk_linear_20 | 40 | 24/16 | 74.074074 | 221.750000 | 0.450000 | 0.289242 | 28.350000 | 2 | coverage_too_low, row_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 3 | risk_half_step | 40 | 24/16 | 74.074074 | 212.000000 | 0.450000 | 0.312500 | 32.000000 | 2 | coverage_too_low, row_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 4 | risk_linear_30 | 40 | 24/16 | 74.074074 | 208.000000 | 0.450000 | 0.192227 | 23.800000 | 2 | coverage_too_low, row_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 5 | cheap_thin_fifth | 40 | 24/16 | 74.074074 | 264.400000 | 0.450000 | 0.375000 | 35.200000 | 2 | coverage_too_low, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 6 | cheap_thin_quarter | 40 | 24/16 | 74.074074 | 262.250000 | 0.450000 | 0.380282 | 35.500000 | 2 | coverage_too_low, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 7 | no_shrink_control | 40 | 24/16 | 74.074074 | 230.000000 | 0.450000 | 0.450000 | 40.000000 | 2 | coverage_too_low, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |

### Best Policy Tag Attribution

- Policy: `risk_quarter_step`
- Tag counts: `{'early_observation_stc_lt240': 14, 'cheap_tail_ask_lt50': 15, 'low_p_side_lt75': 14, 'no_observable_source_risk': 12, 'thin_depth_lt100': 17, 'moderate_boundary_distance_65_85': 5, 'thin_raw_edge_lt05': 5}`
- Tag weight: `{'early_observation_stc_lt240': 7.0, 'cheap_tail_ask_lt50': 6.5, 'low_p_side_lt75': 5.5, 'no_observable_source_risk': 12.0, 'thin_depth_lt100': 11.5, 'moderate_boundary_distance_65_85': 2.75, 'thin_raw_edge_lt05': 1.75}`
- Tag weighted net cents: `{'early_observation_stc_lt240': 46.0, 'cheap_tail_ask_lt50': 79.25, 'low_p_side_lt75': 23.25, 'no_observable_source_risk': 130.0, 'thin_depth_lt100': -44.25, 'moderate_boundary_distance_65_85': -39.25, 'thin_raw_edge_lt05': 0.5}`

### Worst Weighted Rows

| market | source | side | won | net c | weight | weighted c | risk | tags | ask | p side | edge | recross | abs d | stc | depth |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 1.000000 | -78.000000 | 1.000000 | thin_depth_lt100 | 0.760000 | 0.887777 | 0.127777 | 0.303870 | 0.999156 | 628.084000 | 24.000000 |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 1.000000 | -72.000000 | 0.000000 | none | 0.700000 | 0.963659 | 0.263659 | 0.073753 | 1.543579 | 279.632000 | 522.860000 |
| KXBTC15M-26MAY070615-15 | rejected_actionable | yes | False | -68.000000 | 1.000000 | -68.000000 | 1.750000 | thin_depth_lt100, moderate_boundary_distance_65_85 | 0.640000 | 0.840931 | 0.200931 | 0.253348 | 0.819952 | 474.715000 | 60.000000 |
| KXBTC15M-26MAY062345-45 | rejected_actionable | no | False | -15.000000 | 0.250000 | -3.750000 | 5.250000 | cheap_tail_ask_lt50, low_p_side_lt75, thin_depth_lt100, moderate_boundary_distance_65_85, thin_raw_edge_lt05, early_observation_stc_lt240 | 0.130000 | 0.171601 | 0.041601 | 0.132257 | 0.784861 | 234.795000 | 55.000000 |
| KXBTC15M-26MAY061830-30 | rejected_actionable | yes | False | -6.000000 | 0.500000 | -3.000000 | 2.000000 | cheap_tail_ask_lt50, low_p_side_lt75 | 0.050000 | 0.109156 | 0.059156 | 0.160756 | 0.997837 | 409.913000 | 634.000000 |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -11.000000 | 0.250000 | -2.750000 | 4.250000 | cheap_tail_ask_lt50, low_p_side_lt75, thin_depth_lt100, moderate_boundary_distance_65_85, early_observation_stc_lt240 | 0.090000 | 0.176934 | 0.086934 | 0.122242 | 0.758696 | 225.693000 | 65.000000 |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.500000 | -2.500000 | 2.500000 | cheap_tail_ask_lt50, low_p_side_lt75, early_observation_stc_lt240 | 0.040000 | 0.102326 | 0.062326 | 0.081020 | 1.050761 | 149.506000 | 1319.700000 |
| KXBTC15M-26MAY062245-45 | rejected_actionable | no | False | -5.000000 | 0.500000 | -2.500000 | 2.500000 | cheap_tail_ask_lt50, low_p_side_lt75, early_observation_stc_lt240 | 0.040000 | 0.144085 | 0.104085 | 0.082631 | 0.877475 | 160.423000 | 1062.610000 |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.500000 | -2.000000 | 2.500000 | cheap_tail_ask_lt50, low_p_side_lt75, early_observation_stc_lt240 | 0.030000 | 0.107885 | 0.077885 | 0.087550 | 0.997935 | 204.831000 | 466.340000 |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.250000 | -1.750000 | 4.250000 | cheap_tail_ask_lt50, low_p_side_lt75, thin_depth_lt100, moderate_boundary_distance_65_85, early_observation_stc_lt240 | 0.060000 | 0.164874 | 0.104874 | 0.041740 | 0.791108 | 74.159000 | 36.000000 |

## diagnostic_feature_window_bridge

- Base rule: `raw03_recross70_abs075`
- Selected entries: `40`
- Future denominator: `54`

| rank | policy | settled | W/L | coverage | weighted net | row source | exposure source | exposure rows | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | risk_quarter_step | 40 | 24/16 | 74.074074 | 222.750000 | 0.450000 | 0.278689 | 30.500000 | 2 | coverage_too_low, row_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 2 | risk_linear_20 | 40 | 24/16 | 74.074074 | 221.750000 | 0.450000 | 0.289242 | 28.350000 | 2 | coverage_too_low, row_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 3 | risk_half_step | 40 | 24/16 | 74.074074 | 212.000000 | 0.450000 | 0.312500 | 32.000000 | 2 | coverage_too_low, row_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 4 | risk_linear_30 | 40 | 24/16 | 74.074074 | 208.000000 | 0.450000 | 0.192227 | 23.800000 | 2 | coverage_too_low, row_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 5 | cheap_thin_fifth | 40 | 24/16 | 74.074074 | 264.400000 | 0.450000 | 0.375000 | 35.200000 | 2 | coverage_too_low, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 6 | cheap_thin_quarter | 40 | 24/16 | 74.074074 | 262.250000 | 0.450000 | 0.380282 | 35.500000 | 2 | coverage_too_low, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 7 | no_shrink_control | 40 | 24/16 | 74.074074 | 230.000000 | 0.450000 | 0.450000 | 40.000000 | 2 | coverage_too_low, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |

### Best Policy Tag Attribution

- Policy: `risk_quarter_step`
- Tag counts: `{'early_observation_stc_lt240': 14, 'cheap_tail_ask_lt50': 15, 'low_p_side_lt75': 14, 'no_observable_source_risk': 12, 'thin_depth_lt100': 17, 'moderate_boundary_distance_65_85': 5, 'thin_raw_edge_lt05': 5}`
- Tag weight: `{'early_observation_stc_lt240': 7.0, 'cheap_tail_ask_lt50': 6.5, 'low_p_side_lt75': 5.5, 'no_observable_source_risk': 12.0, 'thin_depth_lt100': 11.5, 'moderate_boundary_distance_65_85': 2.75, 'thin_raw_edge_lt05': 1.75}`
- Tag weighted net cents: `{'early_observation_stc_lt240': 46.0, 'cheap_tail_ask_lt50': 79.25, 'low_p_side_lt75': 23.25, 'no_observable_source_risk': 130.0, 'thin_depth_lt100': -44.25, 'moderate_boundary_distance_65_85': -39.25, 'thin_raw_edge_lt05': 0.5}`

### Worst Weighted Rows

| market | source | side | won | net c | weight | weighted c | risk | tags | ask | p side | edge | recross | abs d | stc | depth |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 1.000000 | -78.000000 | 1.000000 | thin_depth_lt100 | 0.760000 | 0.887777 | 0.127777 | 0.303870 | 0.999156 | 628.084000 | 24.000000 |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 1.000000 | -72.000000 | 0.000000 | none | 0.700000 | 0.963659 | 0.263659 | 0.073753 | 1.543579 | 279.632000 | 522.860000 |
| KXBTC15M-26MAY070615-15 | rejected_actionable | yes | False | -68.000000 | 1.000000 | -68.000000 | 1.750000 | thin_depth_lt100, moderate_boundary_distance_65_85 | 0.640000 | 0.840931 | 0.200931 | 0.253348 | 0.819952 | 474.715000 | 60.000000 |
| KXBTC15M-26MAY062345-45 | rejected_actionable | no | False | -15.000000 | 0.250000 | -3.750000 | 5.250000 | cheap_tail_ask_lt50, low_p_side_lt75, thin_depth_lt100, moderate_boundary_distance_65_85, thin_raw_edge_lt05, early_observation_stc_lt240 | 0.130000 | 0.171601 | 0.041601 | 0.132257 | 0.784861 | 234.795000 | 55.000000 |
| KXBTC15M-26MAY061830-30 | rejected_actionable | yes | False | -6.000000 | 0.500000 | -3.000000 | 2.000000 | cheap_tail_ask_lt50, low_p_side_lt75 | 0.050000 | 0.109156 | 0.059156 | 0.160756 | 0.997837 | 409.913000 | 634.000000 |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -11.000000 | 0.250000 | -2.750000 | 4.250000 | cheap_tail_ask_lt50, low_p_side_lt75, thin_depth_lt100, moderate_boundary_distance_65_85, early_observation_stc_lt240 | 0.090000 | 0.176934 | 0.086934 | 0.122242 | 0.758696 | 225.693000 | 65.000000 |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.500000 | -2.500000 | 2.500000 | cheap_tail_ask_lt50, low_p_side_lt75, early_observation_stc_lt240 | 0.040000 | 0.102326 | 0.062326 | 0.081020 | 1.050761 | 149.506000 | 1319.700000 |
| KXBTC15M-26MAY062245-45 | rejected_actionable | no | False | -5.000000 | 0.500000 | -2.500000 | 2.500000 | cheap_tail_ask_lt50, low_p_side_lt75, early_observation_stc_lt240 | 0.040000 | 0.144085 | 0.104085 | 0.082631 | 0.877475 | 160.423000 | 1062.610000 |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.500000 | -2.000000 | 2.500000 | cheap_tail_ask_lt50, low_p_side_lt75, early_observation_stc_lt240 | 0.030000 | 0.107885 | 0.077885 | 0.087550 | 0.997935 | 204.831000 | 466.340000 |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.250000 | -1.750000 | 4.250000 | cheap_tail_ask_lt50, low_p_side_lt75, thin_depth_lt100, moderate_boundary_distance_65_85, early_observation_stc_lt240 | 0.060000 | 0.164874 | 0.104874 | 0.041740 | 0.791108 | 74.159000 | 36.000000 |

## post_source_risk_birth_entry

- Base rule: `raw03_recross70_abs075`
- Selected entries: `3`
- Future denominator: `5`

| rank | policy | settled | W/L | coverage | weighted net | row source | exposure source | exposure rows | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | risk_linear_30 | 3 | 2/1 | 60.000000 | -13.500000 | 0.666667 | 0.466667 | 1.875000 | 0 | settled_lt_30, coverage_too_low, weighted_net_not_positive, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 2 | risk_linear_20 | 3 | 2/1 | 60.000000 | -24.000000 | 0.666667 | 0.555556 | 2.250000 | 0 | settled_lt_30, coverage_too_low, weighted_net_not_positive, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 3 | no_shrink_control | 3 | 2/1 | 60.000000 | -45.000000 | 0.666667 | 0.666667 | 3.000000 | 0 | settled_lt_30, coverage_too_low, weighted_net_not_positive, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 4 | cheap_thin_quarter | 3 | 2/1 | 60.000000 | -45.000000 | 0.666667 | 0.666667 | 3.000000 | 0 | settled_lt_30, coverage_too_low, weighted_net_not_positive, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 5 | cheap_thin_fifth | 3 | 2/1 | 60.000000 | -45.000000 | 0.666667 | 0.666667 | 3.000000 | 0 | settled_lt_30, coverage_too_low, weighted_net_not_positive, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 6 | risk_half_step | 3 | 2/1 | 60.000000 | -48.500000 | 0.666667 | 0.600000 | 2.500000 | 0 | settled_lt_30, coverage_too_low, weighted_net_not_positive, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 7 | risk_quarter_step | 3 | 2/1 | 60.000000 | -48.500000 | 0.666667 | 0.600000 | 2.500000 | 0 | settled_lt_30, coverage_too_low, weighted_net_not_positive, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |

### Best Policy Tag Attribution

- Policy: `risk_linear_30`
- Tag counts: `{'thin_depth_lt100': 2, 'thin_raw_edge_lt05': 1, 'no_observable_source_risk': 1, 'moderate_boundary_distance_65_85': 1}`
- Tag weight: `{'thin_depth_lt100': 0.875, 'thin_raw_edge_lt05': 0.4, 'no_observable_source_risk': 1.0, 'moderate_boundary_distance_65_85': 0.475}`
- Tag weighted net cents: `{'thin_depth_lt100': -29.499999999999996, 'thin_raw_edge_lt05': 2.8000000000000003, 'no_observable_source_risk': 16.0, 'moderate_boundary_distance_65_85': -32.3}`

### Worst Weighted Rows

| market | source | side | won | net c | weight | weighted c | risk | tags | ask | p side | edge | recross | abs d | stc | depth |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY070615-15 | rejected_actionable | yes | False | -68.000000 | 0.475000 | -32.300000 | 1.750000 | thin_depth_lt100, moderate_boundary_distance_65_85 | 0.640000 | 0.840931 | 0.200931 | 0.253348 | 0.819952 | 474.715000 | 60.000000 |
| KXBTC15M-26MAY070530-30 | rejected_actionable | no | True | 7.000000 | 0.400000 | 2.800000 | 2.000000 | thin_depth_lt100, thin_raw_edge_lt05 | 0.910000 | 0.957387 | 0.047387 | 0.085902 | 1.454914 | 319.320000 | 40.000000 |
| KXBTC15M-26MAY070545-45 | approved_entry | no | True | 16.000000 | 1.000000 | 16.000000 | 0.000000 | none | 0.820000 | 0.925171 | 0.105171 | 0.124926 | 1.204817 | 351.487000 | 510.000000 |

## post_source_risk_birth_bridge

- Base rule: `raw03_recross70_abs075`
- Selected entries: `3`
- Future denominator: `5`

| rank | policy | settled | W/L | coverage | weighted net | row source | exposure source | exposure rows | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | risk_linear_30 | 3 | 2/1 | 60.000000 | -13.500000 | 0.666667 | 0.466667 | 1.875000 | 0 | settled_lt_30, coverage_too_low, weighted_net_not_positive, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 2 | risk_linear_20 | 3 | 2/1 | 60.000000 | -24.000000 | 0.666667 | 0.555556 | 2.250000 | 0 | settled_lt_30, coverage_too_low, weighted_net_not_positive, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 3 | no_shrink_control | 3 | 2/1 | 60.000000 | -45.000000 | 0.666667 | 0.666667 | 3.000000 | 0 | settled_lt_30, coverage_too_low, weighted_net_not_positive, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 4 | cheap_thin_quarter | 3 | 2/1 | 60.000000 | -45.000000 | 0.666667 | 0.666667 | 3.000000 | 0 | settled_lt_30, coverage_too_low, weighted_net_not_positive, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 5 | cheap_thin_fifth | 3 | 2/1 | 60.000000 | -45.000000 | 0.666667 | 0.666667 | 3.000000 | 0 | settled_lt_30, coverage_too_low, weighted_net_not_positive, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 6 | risk_half_step | 3 | 2/1 | 60.000000 | -48.500000 | 0.666667 | 0.600000 | 2.500000 | 0 | settled_lt_30, coverage_too_low, weighted_net_not_positive, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| 7 | risk_quarter_step | 3 | 2/1 | 60.000000 | -48.500000 | 0.666667 | 0.600000 | 2.500000 | 0 | settled_lt_30, coverage_too_low, weighted_net_not_positive, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3 |

### Best Policy Tag Attribution

- Policy: `risk_linear_30`
- Tag counts: `{'thin_depth_lt100': 2, 'thin_raw_edge_lt05': 1, 'no_observable_source_risk': 1, 'moderate_boundary_distance_65_85': 1}`
- Tag weight: `{'thin_depth_lt100': 0.875, 'thin_raw_edge_lt05': 0.4, 'no_observable_source_risk': 1.0, 'moderate_boundary_distance_65_85': 0.475}`
- Tag weighted net cents: `{'thin_depth_lt100': -29.499999999999996, 'thin_raw_edge_lt05': 2.8000000000000003, 'no_observable_source_risk': 16.0, 'moderate_boundary_distance_65_85': -32.3}`

### Worst Weighted Rows

| market | source | side | won | net c | weight | weighted c | risk | tags | ask | p side | edge | recross | abs d | stc | depth |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY070615-15 | rejected_actionable | yes | False | -68.000000 | 0.475000 | -32.300000 | 1.750000 | thin_depth_lt100, moderate_boundary_distance_65_85 | 0.640000 | 0.840931 | 0.200931 | 0.253348 | 0.819952 | 474.715000 | 60.000000 |
| KXBTC15M-26MAY070530-30 | rejected_actionable | no | True | 7.000000 | 0.400000 | 2.800000 | 2.000000 | thin_depth_lt100, thin_raw_edge_lt05 | 0.910000 | 0.957387 | 0.047387 | 0.085902 | 1.454914 | 319.320000 | 40.000000 |
| KXBTC15M-26MAY070545-45 | approved_entry | no | True | 16.000000 | 1.000000 | 16.000000 | 0.000000 | none | 0.820000 | 0.925171 | 0.105171 | 0.124926 | 1.204817 | 351.487000 | 510.000000 |
