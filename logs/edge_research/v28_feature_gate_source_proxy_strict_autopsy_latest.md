# v28 Feature-Gate Source-Proxy Strict Autopsy

Research-only. No live bot logic changes, no process control, no orders.

- Generated UTC: `2026-05-07T18:24:07.698734+00:00`
- Source artifact UTC: `2026-05-07T18:04:54.700754+00:00`

## Interpretation

- This is audit-only; source labels are not deployable selection features.
- post_source_proxy_birth_entry: best stc240_core_plus_raw_edge_fillers has 28 settled, net 60.0c, row-source share 0.4642857142857143, cushion 0; needs 4 same-size source replacements or 10 clean additions, plus 240.0c for cushion.
- post_source_proxy_birth_bridge: best stc240_core_plus_raw_edge_fillers has 28 settled, net 60.0c, row-source share 0.4642857142857143, cushion 0; needs 4 same-size source replacements or 10 clean additions, plus 240.0c for cushion.

## post_source_proxy_birth_entry

- Candidate: `stc240_core_plus_raw_edge_fillers`
- Reported blockers: `settled_lt_30, row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3`
- Settled/net/source/cushion: `28` / `60.000000c` / `0.464286` / `0`
- Gate arithmetic: source replacements `4`, clean additions if no replacements `10`, net needed for cushion `240.000000c`
- Approved slice: `15` rows, `83.500000c`, W/L `13/2`
- Non-approved slice: `13` rows, `-23.500000c`, W/L `9/4`
- Losing slice: `6` rows, `-268.500000c`
- Strict read: `sample_is_still_below_30_settled, source_gate_needs_4_same-size replacements_or_10_clean_additions, cushion_needs_240.0c_more_net, non_approved_slice_is_net_negative, loss_tags={'selected_loss': 6, 'fv_or_entry_timing_error': 6, 'recross_or_boundary_churn': 5, 'source_quality_error': 4, 'notional_shrunk': 4}`

### Tag Counts

| tag | rows | weighted net c |
|---|---:|---:|
| `recross_or_boundary_churn` | 14 | -66.500000 |
| `source_quality_error` | 13 | -23.500000 |
| `thin_depth` | 13 | -3.000000 |
| `notional_shrunk` | 10 | -68.000000 |
| `fv_or_entry_timing_error` | 6 | -268.500000 |
| `selected_loss` | 6 | -268.500000 |
| `thin_raw_edge` | 5 | 33.000000 |
| `clean_or_unclassified` | 4 | 76.000000 |
| `weak_boundary_distance` | 3 | 14.250000 |
| `mid_cheap_touch` | 2 | -48.750000 |

### Worst Rows

| market | side | source | role | weighted c | raw edge | p_side | ask | abs_d | recross | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071100-00 | yes | approved_entry | core | -84.000000 | 0.054041 | 0.884041 | 0.830000 | 1.010241 | 0.305006 | selected_loss, fv_or_entry_timing_error, recross_or_boundary_churn |
| KXBTC15M-26MAY071015-15 | no | approved_entry | core | -80.000000 | 0.081092 | 0.861092 | 0.780000 | 0.936079 | 0.417623 | selected_loss, fv_or_entry_timing_error, thin_depth, recross_or_boundary_churn |
| KXBTC15M-26MAY071215-15 | yes | rejected_actionable | core | -37.500000 | 0.108282 | 0.828282 | 0.720000 | 0.790551 | 0.487740 | source_quality_error, selected_loss, fv_or_entry_timing_error, thin_depth, recross_or_boundary_churn, notional_shrunk |
| KXBTC15M-26MAY070615-15 | yes | rejected_actionable | core | -34.000000 | 0.200931 | 0.840931 | 0.640000 | 0.819952 | 0.253348 | source_quality_error, selected_loss, fv_or_entry_timing_error, thin_depth, mid_cheap_touch, notional_shrunk |
| KXBTC15M-26MAY070900-00 | no | rejected_actionable | core | -18.250000 | 0.055939 | 0.755939 | 0.700000 | 0.591792 | 0.457207 | source_quality_error, selected_loss, fv_or_entry_timing_error, weak_boundary_distance, recross_or_boundary_churn, notional_shrunk |
| KXBTC15M-26MAY070630-30 | yes | rejected_actionable | core | -14.750000 | 0.238158 | 0.788158 | 0.550000 | 0.658030 | 0.372304 | source_quality_error, selected_loss, fv_or_entry_timing_error, recross_or_boundary_churn, mid_cheap_touch, notional_shrunk |
| KXBTC15M-26MAY070530-30 | no | rejected_actionable | core | 3.500000 | 0.047387 | 0.957387 | 0.910000 | 1.454914 | 0.085902 | source_quality_error, thin_raw_edge, thin_depth, notional_shrunk |
| KXBTC15M-26MAY071245-45 | no | rejected_actionable | core | 4.000000 | 0.034347 | 0.934347 | 0.900000 | 1.285530 | 0.231360 | source_quality_error, thin_raw_edge, thin_depth, notional_shrunk |
| KXBTC15M-26MAY070200-00 | no | rejected_actionable | core | 6.500000 | 0.031860 | 0.741860 | 0.710000 | 0.556916 | 0.201448 | source_quality_error, thin_raw_edge, weak_boundary_distance, notional_shrunk |
| KXBTC15M-26MAY070600-00 | yes | rejected_actionable | core | 7.000000 | 0.122029 | 0.812029 | 0.690000 | 0.734324 | 0.201732 | source_quality_error, notional_shrunk |

## post_source_proxy_birth_bridge

- Candidate: `stc240_core_plus_raw_edge_fillers`
- Reported blockers: `settled_lt_30, row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3`
- Settled/net/source/cushion: `28` / `60.000000c` / `0.464286` / `0`
- Gate arithmetic: source replacements `4`, clean additions if no replacements `10`, net needed for cushion `240.000000c`
- Approved slice: `15` rows, `83.500000c`, W/L `13/2`
- Non-approved slice: `13` rows, `-23.500000c`, W/L `9/4`
- Losing slice: `6` rows, `-268.500000c`
- Strict read: `sample_is_still_below_30_settled, source_gate_needs_4_same-size replacements_or_10_clean_additions, cushion_needs_240.0c_more_net, non_approved_slice_is_net_negative, loss_tags={'selected_loss': 6, 'fv_or_entry_timing_error': 6, 'recross_or_boundary_churn': 5, 'source_quality_error': 4, 'notional_shrunk': 4}`

### Tag Counts

| tag | rows | weighted net c |
|---|---:|---:|
| `recross_or_boundary_churn` | 14 | -66.500000 |
| `source_quality_error` | 13 | -23.500000 |
| `thin_depth` | 13 | -3.000000 |
| `notional_shrunk` | 10 | -68.000000 |
| `fv_or_entry_timing_error` | 6 | -268.500000 |
| `selected_loss` | 6 | -268.500000 |
| `thin_raw_edge` | 5 | 33.000000 |
| `clean_or_unclassified` | 4 | 76.000000 |
| `weak_boundary_distance` | 3 | 14.250000 |
| `mid_cheap_touch` | 2 | -48.750000 |

### Worst Rows

| market | side | source | role | weighted c | raw edge | p_side | ask | abs_d | recross | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071100-00 | yes | approved_entry | core | -84.000000 | 0.054041 | 0.884041 | 0.830000 | 1.010241 | 0.305006 | selected_loss, fv_or_entry_timing_error, recross_or_boundary_churn |
| KXBTC15M-26MAY071015-15 | no | approved_entry | core | -80.000000 | 0.081092 | 0.861092 | 0.780000 | 0.936079 | 0.417623 | selected_loss, fv_or_entry_timing_error, thin_depth, recross_or_boundary_churn |
| KXBTC15M-26MAY071215-15 | yes | rejected_actionable | core | -37.500000 | 0.108282 | 0.828282 | 0.720000 | 0.790551 | 0.487740 | source_quality_error, selected_loss, fv_or_entry_timing_error, thin_depth, recross_or_boundary_churn, notional_shrunk |
| KXBTC15M-26MAY070615-15 | yes | rejected_actionable | core | -34.000000 | 0.200931 | 0.840931 | 0.640000 | 0.819952 | 0.253348 | source_quality_error, selected_loss, fv_or_entry_timing_error, thin_depth, mid_cheap_touch, notional_shrunk |
| KXBTC15M-26MAY070900-00 | no | rejected_actionable | core | -18.250000 | 0.055939 | 0.755939 | 0.700000 | 0.591792 | 0.457207 | source_quality_error, selected_loss, fv_or_entry_timing_error, weak_boundary_distance, recross_or_boundary_churn, notional_shrunk |
| KXBTC15M-26MAY070630-30 | yes | rejected_actionable | core | -14.750000 | 0.238158 | 0.788158 | 0.550000 | 0.658030 | 0.372304 | source_quality_error, selected_loss, fv_or_entry_timing_error, recross_or_boundary_churn, mid_cheap_touch, notional_shrunk |
| KXBTC15M-26MAY070530-30 | no | rejected_actionable | core | 3.500000 | 0.047387 | 0.957387 | 0.910000 | 1.454914 | 0.085902 | source_quality_error, thin_raw_edge, thin_depth, notional_shrunk |
| KXBTC15M-26MAY071245-45 | no | rejected_actionable | core | 4.000000 | 0.034347 | 0.934347 | 0.900000 | 1.285530 | 0.231360 | source_quality_error, thin_raw_edge, thin_depth, notional_shrunk |
| KXBTC15M-26MAY070200-00 | no | rejected_actionable | core | 6.500000 | 0.031860 | 0.741860 | 0.710000 | 0.556916 | 0.201448 | source_quality_error, thin_raw_edge, weak_boundary_distance, notional_shrunk |
| KXBTC15M-26MAY070600-00 | yes | rejected_actionable | core | 7.000000 | 0.122029 | 0.812029 | 0.690000 | 0.734324 | 0.201732 | source_quality_error, notional_shrunk |
