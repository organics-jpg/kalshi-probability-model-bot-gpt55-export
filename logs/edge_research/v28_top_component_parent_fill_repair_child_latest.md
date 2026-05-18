# v28 Top-Component Parent-Fill Repair Child

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T23:35:06.303618+00:00`
- Child freeze UTC: `2026-05-07T10:29:46.104521+00:00`
- Parent: `rescue_drop15_plus_absd_parent_fill_to75` `1680.500c` `64/12`
- Exit child rule layered first: `diagnostic_approved_union_rebound`
- Strict scoreable rows from child freeze: `21`

## Interpretation

- Research-only parent-fill repair child; no live bot changes or orders.
- Best diagnostic child diagnostic_observable_mid_confidence_parent_fill_quarter scores 2233.0c with W/L 67/9 and 6 shrunk parent-fill rows.
- This tests whether rejected-actionable parent-fill exposure should be confidence-sized after the approved-entry exit rescue.
- Child freeze UTC is 2026-05-07T10:29:46.104521+00:00; strict rows from this child freeze are the only promotion evidence.

## Strict Runway

- Future denominator: `28`
- Future observation rows: `1157`
- Broad pass rows: `89`
- Selected parent rows: `24`
- Settled selected rows: `24`
- Pending selected rows: `0`
- Settled selected rows with exit-clock join: `10`
- Strict absd-fill rows: `21`

### Gate Runway

- Closest strict candidate: `post_parent_fill_child_birth_exit_child_only_control`
- Entries needed for 75% coverage at current denominator: `0`
- Settled rows needed for 30-row sample: `9`
- Approved rows needed for source gate if no more rejected rows are added: `0`
- Net cents needed to beat refreshed live baseline: `1168.000`
- Net cents needed for 3 full-loss cushion: `106.000`
- Exit-clock joined rows needed for mechanism sample: `20`
- Pending source counts: `{}`

### Strict Near Misses

| market | side | source | pass count | missing | raw edge | recross | abs d | ask |
|---|---|---|---:|---|---:|---:|---:|---:|
| KXBTC15M-26MAY070745-45 | yes | approved_entry | 4 |  | 0.224 | 0.198 | 1.081 | 0.680 |
| KXBTC15M-26MAY070945-45 | no | approved_entry | 4 |  | 0.164 | 0.436 | 0.883 | 0.690 |
| KXBTC15M-26MAY071000-00 | no | approved_entry | 4 |  | 0.142 | 0.484 | 0.895 | 0.710 |
| KXBTC15M-26MAY071000-00 | no | approved_entry | 4 |  | 0.132 | 0.483 | 0.929 | 0.730 |
| KXBTC15M-26MAY070830-30 | no | approved_entry | 4 |  | 0.120 | 0.127 | 1.007 | 0.770 |
| KXBTC15M-26MAY071045-45 | no | approved_entry | 4 |  | 0.115 | 0.470 | 0.954 | 0.750 |
| KXBTC15M-26MAY071215-15 | yes | rejected_actionable | 4 |  | 0.108 | 0.488 | 0.791 | 0.720 |
| KXBTC15M-26MAY070915-15 | no | approved_entry | 4 |  | 0.107 | 0.284 | 0.951 | 0.770 |

## Variants

| label | settled | W/L | coverage | net | delta live | recon | src margin | cushion | exit rescues/delta | parent fill rows/net | shrunk rows/delta | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `diagnostic_observable_mid_confidence_parent_fill_quarter` | 76 | 67/9 | 75.248% | 2233.000 | 872.000 | 0.342 | 0 | 22 | 3/422.000 | 17/145.500 | 6/130.500 | diagnostic_prefreeze, source_gate_zero_row_margin |
| `diagnostic_observable_mid_confidence_parent_fill_half` | 76 | 67/9 | 75.248% | 2189.500 | 828.500 | 0.342 | 0 | 21 | 3/422.000 | 17/102.000 | 6/87.000 | diagnostic_prefreeze, source_gate_zero_row_margin |
| `diagnostic_parent_fill_wide_mid_absd_ask_notch` | 76 | 67/9 | 75.248% | 2144.713 | 783.713 | 0.342 | 0 | 21 | 3/422.000 | 17/57.213 | 11/42.213 | diagnostic_prefreeze, source_gate_zero_row_margin |
| `diagnostic_parent_fill_mid_absd_ask_notch` | 76 | 67/9 | 75.248% | 2141.778 | 780.778 | 0.342 | 0 | 21 | 3/422.000 | 17/54.278 | 7/39.278 | diagnostic_prefreeze, source_gate_zero_row_margin |
| `diagnostic_exit_child_only_control` | 76 | 67/9 | 75.248% | 2102.500 | 741.500 | 0.342 | 0 | 21 | 3/422.000 | 17/15.000 | 0/0 | diagnostic_prefreeze, source_gate_zero_row_margin |
| `diagnostic_mid_confidence_parent_fill_quarter` | 76 | 67/9 | 75.248% | 2233.000 | 872.000 | 0.342 | 0 | 22 | 3/422.000 | 17/145.500 | 6/130.500 | diagnostic_prefreeze, source_label_diagnostic, source_gate_zero_row_margin |
| `diagnostic_mid_confidence_parent_fill_half` | 76 | 67/9 | 75.248% | 2189.500 | 828.500 | 0.342 | 0 | 21 | 3/422.000 | 17/102.000 | 6/87.000 | diagnostic_prefreeze, source_label_diagnostic, source_gate_zero_row_margin |
| `diagnostic_smooth_parent_fill_source_risk` | 76 | 67/9 | 75.248% | 2127.044 | 766.044 | 0.342 | 0 | 21 | 3/422.000 | 17/39.544 | 16/24.544 | diagnostic_prefreeze, source_label_diagnostic, source_gate_zero_row_margin |
| `diagnostic_parent_fill_all_rejected_half` | 76 | 67/9 | 75.248% | 2095.000 | 734.000 | 0.342 | 0 | 20 | 3/422.000 | 17/7.500 | 17/-7.500 | diagnostic_prefreeze, source_label_diagnostic, source_gate_zero_row_margin |
| `diagnostic_parent_fill_all_rejected_quarter` | 76 | 67/9 | 75.248% | 2091.250 | 730.250 | 0.342 | 0 | 20 | 3/422.000 | 17/3.750 | 17/-11.250 | diagnostic_prefreeze, source_label_diagnostic, source_gate_zero_row_margin |
| `post_parent_fill_child_birth_exit_child_only_control` | 21 | 19/2 | 75.000% | 194.000 | -1167.000 | 0.238 | 2 | 1 | 0/0.000 | 0/0 | 0/0 | settled_lt_30, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `post_parent_fill_child_birth_observable_mid_confidence_parent_fill_half` | 21 | 19/2 | 75.000% | 194.000 | -1167.000 | 0.238 | 2 | 1 | 0/0.000 | 0/0 | 0/0 | settled_lt_30, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `post_parent_fill_child_birth_observable_mid_confidence_parent_fill_quarter` | 21 | 19/2 | 75.000% | 194.000 | -1167.000 | 0.238 | 2 | 1 | 0/0.000 | 0/0 | 0/0 | settled_lt_30, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `post_parent_fill_child_birth_parent_fill_mid_absd_ask_notch` | 21 | 19/2 | 75.000% | 194.000 | -1167.000 | 0.238 | 2 | 1 | 0/0.000 | 0/0 | 0/0 | settled_lt_30, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `post_parent_fill_child_birth_parent_fill_wide_mid_absd_ask_notch` | 21 | 19/2 | 75.000% | 194.000 | -1167.000 | 0.238 | 2 | 1 | 0/0.000 | 0/0 | 0/0 | settled_lt_30, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `post_parent_fill_child_birth_parent_fill_all_rejected_half` | 21 | 19/2 | 75.000% | 194.000 | -1167.000 | 0.238 | 2 | 1 | 0/0.000 | 0/0 | 0/0 | source_label_diagnostic, settled_lt_30, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `post_parent_fill_child_birth_parent_fill_all_rejected_quarter` | 21 | 19/2 | 75.000% | 194.000 | -1167.000 | 0.238 | 2 | 1 | 0/0.000 | 0/0 | 0/0 | source_label_diagnostic, settled_lt_30, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `post_parent_fill_child_birth_mid_confidence_parent_fill_half` | 21 | 19/2 | 75.000% | 194.000 | -1167.000 | 0.238 | 2 | 1 | 0/0.000 | 0/0 | 0/0 | source_label_diagnostic, settled_lt_30, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `post_parent_fill_child_birth_mid_confidence_parent_fill_quarter` | 21 | 19/2 | 75.000% | 194.000 | -1167.000 | 0.238 | 2 | 1 | 0/0.000 | 0/0 | 0/0 | source_label_diagnostic, settled_lt_30, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `post_parent_fill_child_birth_smooth_parent_fill_source_risk` | 21 | 19/2 | 75.000% | 194.000 | -1167.000 | 0.238 | 2 | 1 | 0/0.000 | 0/0 | 0/0 | source_label_diagnostic, settled_lt_30, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |

## Best Variant Worst Rows

| market | side | source | component | final | scale | raw edge | abs d | ask | recross |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY060745-45 | yes | rejected_actionable | delayed_recheck_rescue:drop15_bid60 | -70.000 | 1.000 | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY061300-00 | yes | approved_entry | delayed_recheck_rescue:drop15_bid60 | -30.000 | 1.000 | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY062345-45 | no | rejected_actionable | parent_midprice_hold_fill | -15.000 | 0.250 | 0.246 | 0.727 | 0.560 | 0.265 |
| KXBTC15M-26MAY070630-30 | yes | rejected_actionable | parent_midprice_hold_fill | -14.750 | 0.250 | 0.238 | 0.658 | 0.550 | 0.372 |
| KXBTC15M-26MAY070615-15 | yes | rejected_actionable | parent_midprice_hold_fill | -11.750 | 0.250 | 0.345 | 0.631 | 0.430 | 0.143 |
| KXBTC15M-26MAY061700-00 | no | rejected_actionable | parent_midprice_hold_fill | -10.500 | 0.250 | 0.408 | 0.665 | 0.380 | 0.196 |
| KXBTC15M-26MAY062130-30 | no | rejected_actionable | delayed_recheck_rescue:drop15_bid60 | -8.000 | 1.000 | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY061715-15 | yes | rejected_actionable | parent_midprice_hold_fill | -4.250 | 0.250 | 0.125 | 0.603 | 0.640 | 0.115 |
| KXBTC15M-26MAY070015-15 | no | approved_entry | delayed_recheck_rescue:drop15_bid60 | -2.000 | 1.000 | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY062315-15 | no | rejected_actionable | delayed_recheck_rescue:drop15_bid60 | 1.500 | 1.000 | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY062200-00 | no | rejected_actionable | parent_midprice_hold_fill | 4.000 | 1.000 | 0.042 | 2.371 | 0.950 | 0.027 |
| KXBTC15M-26MAY062145-45 | yes | rejected_actionable | parent_midprice_hold_fill | 6.000 | 1.000 | 0.055 | 1.771 | 0.920 | 0.035 |
| KXBTC15M-26MAY060415-15 | yes | rejected_actionable | parent_midprice_hold_fill | 6.000 | 1.000 | 0.050 | 1.621 | 0.920 | 0.158 |
| KXBTC15M-26MAY070530-30 | no | rejected_actionable | parent_midprice_hold_fill | 7.000 | 1.000 | 0.047 | 1.455 | 0.910 | 0.086 |
