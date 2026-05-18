# v28 Feature-Gate Size-Shrink Source Slice

Research-only. No live bot logic changes, no orders, no process control.

- Generated UTC: `2026-05-07T12:25:43.589045+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Live baseline: `1049.000c`

## Interpretation

- Research-only source-slice audit; no live bot changes or orders.
- Live baseline for delta math is 1049c.
- post_feature_freeze_entry: current policy is 369.0c with W/L 37/8 and 75.41% coverage, but row source share stays 0.413.
- post_feature_freeze_entry: approved-only rows are 387.0c with W/L 25/1 but only 44.26% coverage; repair-added rows alone are -4.0c with W/L 12/6.
- post_feature_freeze_entry: even a post-hoc best-case source-gate trim leaves 67.21% coverage, so this branch needs fresh approved rows rather than more reconstructed repair rows.
- post_feature_freeze_bridge: current policy is 369.0c with W/L 37/8 and 75.41% coverage, but row source share stays 0.413.
- post_feature_freeze_bridge: approved-only rows are 387.0c with W/L 25/1 but only 44.26% coverage; repair-added rows alone are -4.0c with W/L 12/6.
- post_feature_freeze_bridge: even a post-hoc best-case source-gate trim leaves 67.21% coverage, so this branch needs fresh approved rows rather than more reconstructed repair rows.

## post_feature_freeze_entry

- Policy: `repair_low_absd_quarter_else_half`
- Anchor rule: `raw05_recross60_abs85_asknone`
- Repair rule: `raw03_recross50_abs50_ask35`
- Future denominator: `61`
- Source counts: `{'approved_entry': 27, 'rejected_actionable': 19}`
- Role counts: `{'anchor_overlap': 28, 'repair_added': 18}`
- Repair source counts: `{'approved_entry': 4, 'rejected_actionable': 14}`
- Clean approved rows needed if current rows are kept: `9`

### Scenarios

| scenario | entries | settled | W/L | coverage | net c | delta live c | row recon | exposure recon | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `current_weighted_policy` | 46 | 45 | 37/8 | 75.410% | 369.000 | -680.000 | 0.413 | 0.265 | 3 | row_reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `approved_only_drop_reconstructed` | 27 | 26 | 25/1 | 44.262% | 387.000 | -662.000 | 0.000 | 0.000 | 3 | settled_lt_30, coverage_too_low, does_not_beat_refreshed_live_baseline |
| `anchor_overlap_only` | 28 | 27 | 25/2 | 45.902% | 373.000 | -676.000 | 0.179 | 0.179 | 3 | settled_lt_30, coverage_too_low, does_not_beat_refreshed_live_baseline |
| `repair_added_only` | 18 | 18 | 12/6 | 29.508% | -4.000 | -1053.000 | 0.778 | 0.667 | 0 | settled_lt_30, coverage_too_low, row_reconstructed_share_gt_35pct, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `source_gate_best_case_drop_recon` | 41 | 40 | 37/3 | 67.213% | 495.250 | -553.750 | 0.341 | 0.219 | 4 | coverage_too_low, does_not_beat_refreshed_live_baseline |
| `zero_recontribution_keep_rows` | 46 | 45 | 37/8 | 75.410% | 387.000 | -662.000 | 0.413 | 0.265 | 3 | row_reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `quarter_recontribution_keep_rows` | 46 | 45 | 37/8 | 75.410% | 382.500 | -666.500 | 0.413 | 0.265 | 3 | row_reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |

### Group Attribution

| group | bucket | entries | settled | W/L | weighted net c | avg weighted net c | row recon | weight sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| role | `anchor_overlap` | 28 | 27 | 25/2 | 373.000 | 13.815 | 0.179 | 28.000 |
| role | `repair_added` | 18 | 18 | 12/6 | -4.000 | -0.222 | 0.778 | 6.000 |
| source | `approved_entry` | 27 | 26 | 25/1 | 387.000 | 14.885 | 0.000 | 25.000 |
| source | `rejected_actionable` | 19 | 19 | 12/7 | -18.000 | -0.947 | 1.000 | 9.000 |
| role_x_source | `anchor_overlap::approved_entry` | 23 | 22 | 21/1 | 365.000 | 16.591 | 0.000 | 23.000 |
| role_x_source | `anchor_overlap::rejected_actionable` | 5 | 5 | 4/1 | 8.000 | 1.600 | 1.000 | 5.000 |
| role_x_source | `repair_added::approved_entry` | 4 | 4 | 4/0 | 22.000 | 5.500 | 0.000 | 2.000 |
| role_x_source | `repair_added::rejected_actionable` | 14 | 14 | 8/6 | -26.000 | -1.857 | 1.000 | 4.000 |
| abs_d_sigma_bucket | `abs_075_125` | 17 | 17 | 17/0 | 389.000 | 22.882 | 0.059 | 16.500 |
| abs_d_sigma_bucket | `abs_ge_125` | 15 | 14 | 13/1 | 37.500 | 2.679 | 0.267 | 12.500 |
| abs_d_sigma_bucket | `abs_lt_075` | 14 | 14 | 7/7 | -57.500 | -4.107 | 1.000 | 5.000 |
| recross_bucket | `recross_015_035` | 26 | 25 | 21/4 | 282.750 | 11.310 | 0.346 | 20.500 |
| recross_bucket | `recross_ge_035` | 6 | 6 | 5/1 | 54.000 | 9.000 | 0.667 | 3.000 |
| recross_bucket | `recross_lt_015` | 14 | 14 | 11/3 | 32.250 | 2.304 | 0.429 | 10.500 |

### Worst Settled Rows

| market | side | role | source | raw net | weight | weighted net | abs d | recross | ask |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY070015-15` | no | anchor_overlap | approved_entry | -72.000 | 1.000 | -72.000 | 1.544 | 0.074 | 0.700 |
| `KXBTC15M-26MAY062130-30` | no | anchor_overlap | rejected_actionable | -65.000 | 1.000 | -65.000 | 0.624 | 0.267 | 0.610 |
| `KXBTC15M-26MAY061715-15` | yes | repair_added | rejected_actionable | -68.000 | 0.250 | -17.000 | 0.603 | 0.115 | 0.640 |
| `KXBTC15M-26MAY062345-45` | no | repair_added | rejected_actionable | -60.000 | 0.250 | -15.000 | 0.727 | 0.265 | 0.560 |
| `KXBTC15M-26MAY070630-30` | yes | repair_added | rejected_actionable | -59.000 | 0.250 | -14.750 | 0.658 | 0.372 | 0.550 |
| `KXBTC15M-26MAY062230-30` | yes | repair_added | rejected_actionable | -58.000 | 0.250 | -14.500 | 0.533 | 0.244 | 0.540 |
| `KXBTC15M-26MAY070615-15` | yes | repair_added | rejected_actionable | -47.000 | 0.250 | -11.750 | 0.631 | 0.143 | 0.430 |
| `KXBTC15M-26MAY061700-00` | no | repair_added | rejected_actionable | -42.000 | 0.250 | -10.500 | 0.665 | 0.196 | 0.380 |
| `KXBTC15M-26MAY062200-00` | no | repair_added | rejected_actionable | 4.000 | 0.500 | 2.000 | 2.371 | 0.027 | 0.950 |
| `KXBTC15M-26MAY070530-30` | no | repair_added | rejected_actionable | 7.000 | 0.500 | 3.500 | 1.455 | 0.086 | 0.910 |

## post_feature_freeze_bridge

- Policy: `repair_low_absd_quarter_else_half`
- Anchor rule: `raw05_recross60_abs85_asknone`
- Repair rule: `raw03_recross50_abs50_ask35`
- Future denominator: `61`
- Source counts: `{'approved_entry': 27, 'rejected_actionable': 19}`
- Role counts: `{'anchor_overlap': 28, 'repair_added': 18}`
- Repair source counts: `{'approved_entry': 4, 'rejected_actionable': 14}`
- Clean approved rows needed if current rows are kept: `9`

### Scenarios

| scenario | entries | settled | W/L | coverage | net c | delta live c | row recon | exposure recon | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `current_weighted_policy` | 46 | 45 | 37/8 | 75.410% | 369.000 | -680.000 | 0.413 | 0.265 | 3 | row_reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `approved_only_drop_reconstructed` | 27 | 26 | 25/1 | 44.262% | 387.000 | -662.000 | 0.000 | 0.000 | 3 | settled_lt_30, coverage_too_low, does_not_beat_refreshed_live_baseline |
| `anchor_overlap_only` | 28 | 27 | 25/2 | 45.902% | 373.000 | -676.000 | 0.179 | 0.179 | 3 | settled_lt_30, coverage_too_low, does_not_beat_refreshed_live_baseline |
| `repair_added_only` | 18 | 18 | 12/6 | 29.508% | -4.000 | -1053.000 | 0.778 | 0.667 | 0 | settled_lt_30, coverage_too_low, row_reconstructed_share_gt_35pct, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `source_gate_best_case_drop_recon` | 41 | 40 | 37/3 | 67.213% | 495.250 | -553.750 | 0.341 | 0.219 | 4 | coverage_too_low, does_not_beat_refreshed_live_baseline |
| `zero_recontribution_keep_rows` | 46 | 45 | 37/8 | 75.410% | 387.000 | -662.000 | 0.413 | 0.265 | 3 | row_reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| `quarter_recontribution_keep_rows` | 46 | 45 | 37/8 | 75.410% | 382.500 | -666.500 | 0.413 | 0.265 | 3 | row_reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |

### Group Attribution

| group | bucket | entries | settled | W/L | weighted net c | avg weighted net c | row recon | weight sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| role | `anchor_overlap` | 28 | 27 | 25/2 | 373.000 | 13.815 | 0.179 | 28.000 |
| role | `repair_added` | 18 | 18 | 12/6 | -4.000 | -0.222 | 0.778 | 6.000 |
| source | `approved_entry` | 27 | 26 | 25/1 | 387.000 | 14.885 | 0.000 | 25.000 |
| source | `rejected_actionable` | 19 | 19 | 12/7 | -18.000 | -0.947 | 1.000 | 9.000 |
| role_x_source | `anchor_overlap::approved_entry` | 23 | 22 | 21/1 | 365.000 | 16.591 | 0.000 | 23.000 |
| role_x_source | `anchor_overlap::rejected_actionable` | 5 | 5 | 4/1 | 8.000 | 1.600 | 1.000 | 5.000 |
| role_x_source | `repair_added::approved_entry` | 4 | 4 | 4/0 | 22.000 | 5.500 | 0.000 | 2.000 |
| role_x_source | `repair_added::rejected_actionable` | 14 | 14 | 8/6 | -26.000 | -1.857 | 1.000 | 4.000 |
| abs_d_sigma_bucket | `abs_075_125` | 17 | 17 | 17/0 | 389.000 | 22.882 | 0.059 | 16.500 |
| abs_d_sigma_bucket | `abs_ge_125` | 15 | 14 | 13/1 | 37.500 | 2.679 | 0.267 | 12.500 |
| abs_d_sigma_bucket | `abs_lt_075` | 14 | 14 | 7/7 | -57.500 | -4.107 | 1.000 | 5.000 |
| recross_bucket | `recross_015_035` | 26 | 25 | 21/4 | 282.750 | 11.310 | 0.346 | 20.500 |
| recross_bucket | `recross_ge_035` | 6 | 6 | 5/1 | 54.000 | 9.000 | 0.667 | 3.000 |
| recross_bucket | `recross_lt_015` | 14 | 14 | 11/3 | 32.250 | 2.304 | 0.429 | 10.500 |

### Worst Settled Rows

| market | side | role | source | raw net | weight | weighted net | abs d | recross | ask |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY070015-15` | no | anchor_overlap | approved_entry | -72.000 | 1.000 | -72.000 | 1.544 | 0.074 | 0.700 |
| `KXBTC15M-26MAY062130-30` | no | anchor_overlap | rejected_actionable | -65.000 | 1.000 | -65.000 | 0.624 | 0.267 | 0.610 |
| `KXBTC15M-26MAY061715-15` | yes | repair_added | rejected_actionable | -68.000 | 0.250 | -17.000 | 0.603 | 0.115 | 0.640 |
| `KXBTC15M-26MAY062345-45` | no | repair_added | rejected_actionable | -60.000 | 0.250 | -15.000 | 0.727 | 0.265 | 0.560 |
| `KXBTC15M-26MAY070630-30` | yes | repair_added | rejected_actionable | -59.000 | 0.250 | -14.750 | 0.658 | 0.372 | 0.550 |
| `KXBTC15M-26MAY062230-30` | yes | repair_added | rejected_actionable | -58.000 | 0.250 | -14.500 | 0.533 | 0.244 | 0.540 |
| `KXBTC15M-26MAY070615-15` | yes | repair_added | rejected_actionable | -47.000 | 0.250 | -11.750 | 0.631 | 0.143 | 0.430 |
| `KXBTC15M-26MAY061700-00` | no | repair_added | rejected_actionable | -42.000 | 0.250 | -10.500 | 0.665 | 0.196 | 0.380 |
| `KXBTC15M-26MAY062200-00` | no | repair_added | rejected_actionable | 4.000 | 0.500 | 2.000 | 2.371 | 0.027 | 0.950 |
| `KXBTC15M-26MAY070530-30` | no | repair_added | rejected_actionable | 7.000 | 0.500 | 3.500 | 1.455 | 0.086 | 0.910 |
