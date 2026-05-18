# v28 Feature-Gate Linked Rejected-Slice Mechanism

Research-only mechanism audit. No live bot changes or orders.

- Generated UTC: `2026-05-07T06:43:37.793152+00:00`
- Candidate: `post_feature_freeze_entry_raw03_recross70_abs075`
- Freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Future denominator: `49`

## Interpretation

- Source labels are audit-only here; the tags are observable failure descriptors for the rejected-actionable slice.
- Rejected-actionable slice is 3/13 for 35.0c, but losses are frequent: 13 rejected rows lose.
- Worst linked rejected-slice tags: ['thin_depth_lt100', 'moderate_boundary_distance_65_85', 'thin_raw_edge_lt05', 'cheap_tail_ask_lt50'].

## Summaries

| slice | rows | settled | W/L | net c | avg c |
|---|---:|---:|---:|---:|---:|
| selected | 37 | 37 | 22/15 | 275.000000 | 7.432432 |
| approved | 21 | 21 | 19/2 | 240.000000 | 11.428571 |
| rejected | 16 | 16 | 3/13 | 35.000000 | 2.187500 |
| rejected_losses | 13 | 13 | 0/13 | -71.000000 | -5.461538 |
| rejected_wins | 3 | 3 | 3/0 | 106.000000 | 35.333333 |

## Rejected Slice Tags

| tag | rows | settled | W/L | net c | avg c |
|---|---:|---:|---:|---:|---:|
| thin_depth_lt100 | 8 | 8 | 2/6 | -33.000000 | -4.125000 |
| moderate_boundary_distance_65_85 | 3 | 3 | 0/3 | -33.000000 | -11.000000 |
| thin_raw_edge_lt05 | 4 | 4 | 1/3 | -16.000000 | -4.000000 |
| cheap_tail_ask_lt50 | 14 | 14 | 1/13 | 25.000000 | 1.785714 |
| low_p_side_lt75 | 14 | 14 | 1/13 | 25.000000 | 1.785714 |
| source_quality_error | 16 | 16 | 3/13 | 35.000000 | 2.187500 |
| early_observation_stc_lt240 | 13 | 13 | 3/10 | 48.000000 | 3.692308 |

## Worst Rejected Rows

| market | side | won | net c | ask | p side | edge | recross | abs d | stc | depth | tags |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY062345-45 | no | False | -15.000000 | 0.130000 | 0.171601 | 0.041601 | 0.132257 | 0.784861 | 234.795000 | 55.000000 | source_quality_error, cheap_tail_ask_lt50, moderate_boundary_distance_65_85, low_p_side_lt75, early_observation_stc_lt240, thin_depth_lt100, thin_raw_edge_lt05 |
| KXBTC15M-26MAY070200-00 | yes | False | -11.000000 | 0.090000 | 0.176934 | 0.086934 | 0.122242 | 0.758696 | 225.693000 | 65.000000 | source_quality_error, cheap_tail_ask_lt50, moderate_boundary_distance_65_85, low_p_side_lt75, early_observation_stc_lt240, thin_depth_lt100 |
| KXBTC15M-26MAY061600-00 | no | False | -7.000000 | 0.060000 | 0.164874 | 0.104874 | 0.041740 | 0.791108 | 74.159000 | 36.000000 | source_quality_error, cheap_tail_ask_lt50, moderate_boundary_distance_65_85, low_p_side_lt75, early_observation_stc_lt240, thin_depth_lt100 |
| KXBTC15M-26MAY061830-30 | yes | False | -6.000000 | 0.050000 | 0.109156 | 0.059156 | 0.160756 | 0.997837 | 409.913000 | 634.000000 | source_quality_error, cheap_tail_ask_lt50, low_p_side_lt75 |
| KXBTC15M-26MAY061430-30 | no | False | -5.000000 | 0.040000 | 0.102326 | 0.062326 | 0.081020 | 1.050761 | 149.506000 | 1319.700000 | source_quality_error, cheap_tail_ask_lt50, low_p_side_lt75, early_observation_stc_lt240 |
| KXBTC15M-26MAY061730-30 | no | False | -5.000000 | 0.040000 | 0.120622 | 0.080622 | 0.099074 | 0.943937 | 240.869000 | 10.000000 | source_quality_error, cheap_tail_ask_lt50, low_p_side_lt75, thin_depth_lt100 |
| KXBTC15M-26MAY062245-45 | no | False | -5.000000 | 0.040000 | 0.144085 | 0.104085 | 0.082631 | 0.877475 | 160.423000 | 1062.610000 | source_quality_error, cheap_tail_ask_lt50, low_p_side_lt75, early_observation_stc_lt240 |
| KXBTC15M-26MAY070130-30 | yes | False | -4.000000 | 0.030000 | 0.107885 | 0.077885 | 0.087550 | 0.997935 | 204.831000 | 466.340000 | source_quality_error, cheap_tail_ask_lt50, low_p_side_lt75, early_observation_stc_lt240 |
| KXBTC15M-26MAY061415-15 | yes | False | -3.000000 | 0.020000 | 0.126664 | 0.106664 | 0.100908 | 0.937376 | 173.789000 | 8839.640000 | source_quality_error, cheap_tail_ask_lt50, low_p_side_lt75, early_observation_stc_lt240 |
| KXBTC15M-26MAY061530-30 | no | False | -3.000000 | 0.020000 | 0.095977 | 0.075977 | 0.038855 | 1.069646 | 83.609000 | 3801.480000 | source_quality_error, cheap_tail_ask_lt50, low_p_side_lt75, early_observation_stc_lt240 |
