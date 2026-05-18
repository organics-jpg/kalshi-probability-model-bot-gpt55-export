# v28 Feature-Gate Source Blocker Mechanism

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:26:00.961364+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- Source labels are used here only for blocker attribution and non-deployable oracle bounds.
- post_feature_freeze_entry: selected net 408.75c, row recon 0.3939393939393939; source-only weighted net -39.75c on 26 rows. Even the limited source-label replacement oracle did not clear all gates.
- post_feature_freeze_bridge: selected net 408.75c, row recon 0.3939393939393939; source-only weighted net -39.75c on 26 rows. Even the limited source-label replacement oracle did not clear all gates.

## post_feature_freeze_entry

- Selected: `66/82` rows, W/L `54/12`, weighted net `408.750c`, row recon `0.394`
- Approved selected: `40` rows, weighted net `448.500c`
- Source selected: `26` rows, weighted net `-39.750c`
- Same-market source rows with approved alternates: `3`
- Omitted approved markets available to oracle: `0`

### Source Mechanism Tags

| tag | count | W/L | weighted net |
|---|---:|---:|---:|
| source_quality_error | 26 | 17/9 | -39.750 |
| moderate_p_side_lt085 | 12 | 4/8 | -111.000 |
| thin_depth_lt100 | 10 | 7/3 | -30.500 |
| weak_boundary_distance_lt065 | 10 | 5/5 | -55.250 |
| thin_raw_edge_lt005 | 9 | 9/0 | 52.750 |
| higher_recross_gt030 | 8 | 5/3 | -19.750 |
| moderate_boundary_distance_lt085 | 7 | 3/4 | -38.000 |
| mid_ask_lt065 | 6 | 1/5 | -87.250 |
| early_observation_stc_lt240 | 5 | 3/2 | -16.750 |
| low_p_side_lt075 | 5 | 4/1 | 17.750 |
| cheap_tail_ask_lt050 | 4 | 2/2 | 2.500 |

### Worst Source Rows

| market | side | reason | net | weight | weighted | tags |
|---|---|---|---:|---:|---:|---|
| KXBTC15M-26MAY062130-30 | no | p_below_floor | -65.000 | 1.000 | -65.000 | source_quality_error, weak_boundary_distance_lt065, mid_ask_lt065, moderate_p_side_lt085 |
| KXBTC15M-26MAY071215-15 | yes | p_below_floor | -75.000 | 0.500 | -37.500 | source_quality_error, moderate_boundary_distance_lt085, moderate_p_side_lt085, higher_recross_gt030, thin_depth_lt100 |
| KXBTC15M-26MAY070900-00 | no | p_below_floor | -73.000 | 0.250 | -18.250 | source_quality_error, weak_boundary_distance_lt065, moderate_p_side_lt085, higher_recross_gt030 |
| KXBTC15M-26MAY061715-15 | yes | p_below_floor | -68.000 | 0.250 | -17.000 | source_quality_error, weak_boundary_distance_lt065, mid_ask_lt065, moderate_p_side_lt085, early_observation_stc_lt240, thin_depth_lt100 |
| KXBTC15M-26MAY062345-45 | no | p_below_floor | -60.000 | 0.250 | -15.000 | source_quality_error, moderate_boundary_distance_lt085, mid_ask_lt065, moderate_p_side_lt085 |
| KXBTC15M-26MAY070630-30 | yes | p_below_floor | -59.000 | 0.250 | -14.750 | source_quality_error, moderate_boundary_distance_lt085, mid_ask_lt065, moderate_p_side_lt085, higher_recross_gt030 |
| KXBTC15M-26MAY062230-30 | yes | p_below_floor | -58.000 | 0.250 | -14.500 | source_quality_error, weak_boundary_distance_lt065, mid_ask_lt065, low_p_side_lt075, thin_depth_lt100 |
| KXBTC15M-26MAY070615-15 | yes | p_below_floor | -47.000 | 0.250 | -11.750 | source_quality_error, weak_boundary_distance_lt065, cheap_tail_ask_lt050, moderate_p_side_lt085, early_observation_stc_lt240 |
| KXBTC15M-26MAY061700-00 | no | p_below_floor | -42.000 | 0.250 | -10.500 | source_quality_error, moderate_boundary_distance_lt085, cheap_tail_ask_lt050, moderate_p_side_lt085 |
| KXBTC15M-26MAY062200-00 | no | ask_too_high | 4.000 | 0.500 | 2.000 | source_quality_error, thin_raw_edge_lt005, early_observation_stc_lt240, thin_depth_lt100 |

## post_feature_freeze_bridge

- Selected: `66/82` rows, W/L `54/12`, weighted net `408.750c`, row recon `0.394`
- Approved selected: `40` rows, weighted net `448.500c`
- Source selected: `26` rows, weighted net `-39.750c`
- Same-market source rows with approved alternates: `3`
- Omitted approved markets available to oracle: `0`

### Source Mechanism Tags

| tag | count | W/L | weighted net |
|---|---:|---:|---:|
| source_quality_error | 26 | 17/9 | -39.750 |
| moderate_p_side_lt085 | 12 | 4/8 | -111.000 |
| thin_depth_lt100 | 10 | 7/3 | -30.500 |
| weak_boundary_distance_lt065 | 10 | 5/5 | -55.250 |
| thin_raw_edge_lt005 | 9 | 9/0 | 52.750 |
| higher_recross_gt030 | 8 | 5/3 | -19.750 |
| moderate_boundary_distance_lt085 | 7 | 3/4 | -38.000 |
| mid_ask_lt065 | 6 | 1/5 | -87.250 |
| early_observation_stc_lt240 | 5 | 3/2 | -16.750 |
| low_p_side_lt075 | 5 | 4/1 | 17.750 |
| cheap_tail_ask_lt050 | 4 | 2/2 | 2.500 |

### Worst Source Rows

| market | side | reason | net | weight | weighted | tags |
|---|---|---|---:|---:|---:|---|
| KXBTC15M-26MAY062130-30 | no | p_below_floor | -65.000 | 1.000 | -65.000 | source_quality_error, weak_boundary_distance_lt065, mid_ask_lt065, moderate_p_side_lt085 |
| KXBTC15M-26MAY071215-15 | yes | p_below_floor | -75.000 | 0.500 | -37.500 | source_quality_error, moderate_boundary_distance_lt085, moderate_p_side_lt085, higher_recross_gt030, thin_depth_lt100 |
| KXBTC15M-26MAY070900-00 | no | p_below_floor | -73.000 | 0.250 | -18.250 | source_quality_error, weak_boundary_distance_lt065, moderate_p_side_lt085, higher_recross_gt030 |
| KXBTC15M-26MAY061715-15 | yes | p_below_floor | -68.000 | 0.250 | -17.000 | source_quality_error, weak_boundary_distance_lt065, mid_ask_lt065, moderate_p_side_lt085, early_observation_stc_lt240, thin_depth_lt100 |
| KXBTC15M-26MAY062345-45 | no | p_below_floor | -60.000 | 0.250 | -15.000 | source_quality_error, moderate_boundary_distance_lt085, mid_ask_lt065, moderate_p_side_lt085 |
| KXBTC15M-26MAY070630-30 | yes | p_below_floor | -59.000 | 0.250 | -14.750 | source_quality_error, moderate_boundary_distance_lt085, mid_ask_lt065, moderate_p_side_lt085, higher_recross_gt030 |
| KXBTC15M-26MAY062230-30 | yes | p_below_floor | -58.000 | 0.250 | -14.500 | source_quality_error, weak_boundary_distance_lt065, mid_ask_lt065, low_p_side_lt075, thin_depth_lt100 |
| KXBTC15M-26MAY070615-15 | yes | p_below_floor | -47.000 | 0.250 | -11.750 | source_quality_error, weak_boundary_distance_lt065, cheap_tail_ask_lt050, moderate_p_side_lt085, early_observation_stc_lt240 |
| KXBTC15M-26MAY061700-00 | no | p_below_floor | -42.000 | 0.250 | -10.500 | source_quality_error, moderate_boundary_distance_lt085, cheap_tail_ask_lt050, moderate_p_side_lt085 |
| KXBTC15M-26MAY062200-00 | no | ask_too_high | 4.000 | 0.500 | 2.000 | source_quality_error, thin_raw_edge_lt005, early_observation_stc_lt240, thin_depth_lt100 |
