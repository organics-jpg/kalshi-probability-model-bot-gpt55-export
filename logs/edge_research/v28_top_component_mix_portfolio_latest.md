# v28 Top-Component Mix Portfolio

Research-only component mix. No live bot changes or orders.

- Generated UTC: `2026-05-11T02:52:54.104756+00:00`
- Parent denominator: `101`
- Strict denominator: `31`
- Best rescue variant: `drop15_bid60`
- Portfolio freeze UTC: `2026-05-07T09:44:04.148307+00:00`

## Interpretation

- Research-only component mix; no live bot changes or orders.
- Best diagnostic mix rescue_drop15_plus_ask_parent_fill_to75 has 76 rows, coverage 75.24752475247524%, net 1715.5c, W/L 65/11, reconstructed share 0.34210526315789475, blockers ['diagnostic_prefreeze', 'source_gate_zero_row_margin'].
- The key audit is whether exit-clock PnL remains broad after filling parent entry rows that lacked exit-clock rescue rows.
- Portfolio freeze UTC is 2026-05-07T09:44:04.148307+00:00; current scored rows are diagnostic parent rows only.
- Post-birth strict check: 27 selected parent rows, 27 settled, 0 pending, 10 joined to exit-clock rows.
- Post-birth variants are the only strict-forward evidence for this portfolio.

## Strict Forward Diagnostics

- Future denominator: `31`
- Future observation rows: `1187`
- Broad-pass rows: `93`
- Predicate pass counts: `{'raw_edge': 253, 'recross': 676, 'abs_d': 665, 'ask': 892}`
- Predicate fail counts: `{'raw_edge': 934, 'recross': 511, 'abs_d': 522, 'ask': 295}`
- Selected parent rows: `27`
- Settled selected rows: `27`
- Pending selected rows: `0`
- Settled selected rows with exit-clock join: `10`
- Settled selected rows without exit-clock join: `17`
- Strict all scored rows: `27`

### Variant Freeze Clocks

| variant | freeze UTC | denominator | selected | settled | pending | exit-clock joined |
|---|---|---:|---:|---:|---:|---:|
| `rescue_drop15_exit_clock_rows_only` | `2026-05-07T09:44:04.148307+00:00` | 31 | 27 | 27 | 0 | 10 |
| `rescue_drop15_plus_absd_parent_fill_to75` | `2026-05-07T10:03:01.566860+00:00` | 30 | 26 | 26 | 0 | 10 |
| `rescue_drop15_plus_all_parent_fill` | `2026-05-07T09:44:04.148307+00:00` | 31 | 27 | 27 | 0 | 10 |
| `rescue_drop15_plus_ask_parent_fill_to75` | `2026-05-07T10:03:01.566860+00:00` | 30 | 26 | 26 | 0 | 10 |
| `rescue_drop15_plus_observable_parent_fill_to75` | `2026-05-07T09:44:04.148307+00:00` | 31 | 27 | 27 | 0 | 10 |
| `rescue_drop15_plus_recross_parent_fill_to75` | `2026-05-07T10:03:01.566860+00:00` | 30 | 26 | 26 | 0 | 10 |

### Strict Near Miss Examples

| market | side | source | pass | missing | raw edge | recross | abs d | ask |
|---|---|---|---:|---|---:|---:|---:|---:|
| KXBTC15M-26MAY070615-15 | yes | rejected_actionable | 4 |  | 0.345 | 0.143 | 0.631 | 0.430 |
| KXBTC15M-26MAY070630-30 | yes | rejected_actionable | 4 |  | 0.238 | 0.372 | 0.658 | 0.550 |
| KXBTC15M-26MAY070745-45 | yes | approved_entry | 4 |  | 0.224 | 0.198 | 1.081 | 0.680 |
| KXBTC15M-26MAY070615-15 | yes | rejected_actionable | 4 |  | 0.201 | 0.253 | 0.820 | 0.640 |
| KXBTC15M-26MAY070945-45 | no | approved_entry | 4 |  | 0.164 | 0.436 | 0.883 | 0.690 |
| KXBTC15M-26MAY071000-00 | no | approved_entry | 4 |  | 0.142 | 0.484 | 0.895 | 0.710 |
| KXBTC15M-26MAY071000-00 | no | approved_entry | 4 |  | 0.132 | 0.483 | 0.929 | 0.730 |
| KXBTC15M-26MAY070600-00 | yes | rejected_actionable | 4 |  | 0.122 | 0.202 | 0.734 | 0.690 |
| KXBTC15M-26MAY070830-30 | no | approved_entry | 4 |  | 0.120 | 0.127 | 1.007 | 0.770 |
| KXBTC15M-26MAY071045-45 | no | approved_entry | 4 |  | 0.115 | 0.470 | 0.954 | 0.750 |

## Variants

| rank | label | entries | W/L | coverage | pnl | delta live | source | src margin | cushion | suppressed H/H | filler rows/net | no-top delta live | no-supp delta live | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `rescue_drop15_plus_ask_parent_fill_to75` | 76 | 65/11 | 75.248% | 1715.500 | 1917.490 | 0.342 | 0 | 17 | 33/0 | 17/50.000 | 1839.490 | 1309.490 | diagnostic_prefreeze, source_gate_zero_row_margin |
| 2 | `rescue_drop15_plus_absd_parent_fill_to75` | 76 | 64/12 | 75.248% | 1680.500 | 1882.490 | 0.342 | 0 | 16 | 33/0 | 17/15.000 | 1804.490 | 1274.490 | diagnostic_prefreeze, source_gate_zero_row_margin |
| 3 | `rescue_drop15_plus_all_parent_fill` | 79 | 66/13 | 78.218% | 1677.500 | 1879.490 | 0.367 | -2 | 16 | 33/0 | 20/12.000 | 1801.490 | 1271.490 | diagnostic_prefreeze, row_reconstructed_share_gt_35pct |
| 4 | `rescue_drop15_exit_clock_rows_only` | 59 | 52/7 | 58.416% | 1665.500 | 1867.490 | 0.153 | 11 | 16 | 33/0 | 0/0 | 1789.490 | 1259.490 | diagnostic_prefreeze, coverage_too_low |
| 5 | `rescue_drop15_plus_approved_parent_fill` | 59 | 52/7 | 58.416% | 1665.500 | 1867.490 | 0.153 | 11 | 16 | 33/0 | 0/0 | 1789.490 | 1259.490 | diagnostic_prefreeze, coverage_too_low |
| 6 | `rescue_drop15_plus_observable_parent_fill_to75` | 76 | 63/13 | 75.248% | 1596.500 | 1798.490 | 0.342 | 0 | 15 | 33/0 | 17/-69.000 | 1720.490 | 1190.490 | diagnostic_prefreeze, source_gate_zero_row_margin |
| 7 | `rescue_drop15_plus_recross_parent_fill_to75` | 76 | 63/13 | 75.248% | 1556.500 | 1758.490 | 0.342 | 0 | 15 | 33/0 | 17/-109.000 | 1680.490 | 1150.490 | diagnostic_prefreeze, source_gate_zero_row_margin |
| 8 | `delayed_base_exit_clock_rows_only` | 59 | 51/8 | 58.416% | 1501.500 | 1703.490 | 0.153 | 11 | 15 | 31/0 | 0/0 | 1633.490 | 1259.490 | diagnostic_prefreeze, coverage_too_low |
| 9 | `post_birth_rescue_drop15_plus_absd_parent_fill_to75` | 23 | 20/3 | 76.667% | 135.000 | 265.990 | 0.304 | 1 | 1 | 8/2 | 0/0 | 201.990 | 449.990 | settled_lt_30, source_gate_margin_lt_2, full_loss_cushion_lt_3, harmful_suppression_present |
| 10 | `post_birth_rescue_drop15_plus_ask_parent_fill_to75` | 23 | 20/3 | 76.667% | 135.000 | 265.990 | 0.304 | 1 | 1 | 8/2 | 0/0 | 201.990 | 449.990 | settled_lt_30, source_gate_margin_lt_2, full_loss_cushion_lt_3, harmful_suppression_present |
| 11 | `post_birth_rescue_drop15_plus_recross_parent_fill_to75` | 23 | 19/4 | 76.667% | 88.000 | 218.990 | 0.304 | 1 | 0 | 8/2 | 0/0 | 154.990 | 402.990 | settled_lt_30, source_gate_margin_lt_2, full_loss_cushion_lt_3, harmful_suppression_present |
| 12 | `post_birth_rescue_drop15_exit_clock_rows_only` | 10 | 8/2 | 32.258% | 22.000 | 223.990 | 0.100 | 2 | 0 | 8/2 | 0/0 | 159.990 | 407.990 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, harmful_suppression_present |
| 13 | `post_birth_rescue_drop15_plus_all_parent_fill` | 27 | 21/6 | 87.097% | -16.000 | 114.990 | 0.407 | -2 | 0 | 8/2 | 0/0 | 50.990 | 298.990 | settled_lt_30, row_reconstructed_share_gt_35pct, net_not_positive, full_loss_cushion_lt_3, harmful_suppression_present |
| 14 | `post_birth_rescue_drop15_plus_observable_parent_fill_to75` | 24 | 18/6 | 77.419% | -48.000 | 153.990 | 0.333 | 0 | 0 | 8/2 | 0/0 | 89.990 | 337.990 | settled_lt_30, source_gate_zero_row_margin, net_not_positive, full_loss_cushion_lt_3, harmful_suppression_present |

## Best Variant Attribution

| bucket | rows | W/L | net |
|---|---:|---:|---:|
| `exit_rescue` | 59 | 52/7 | 1665.500 |
| `parent_fill` | 17 | 13/4 | 50.000 |
| `approved_entry` | 50 | 45/5 | 1492.000 |
| `reconstructed_or_rejected` | 26 | 20/6 | 223.500 |

- Failure modes: `strict_forward_evidence_missing, source_quality_fragility, residual_loss_cluster`
- Source counts: `{'approved_entry': 50, 'rejected_actionable': 26}`
- Component counts: `{'delayed_recheck_rescue:drop15_bid60': 59, 'parent_midprice_hold_fill': 17}`

## Worst Rows By Best Variant

| market | side | source | component | weighted c | suppressed | exit reason | p_hold | exit bid | recheck bid | drop |
|---|---|---|---|---:|---|---|---:|---:|---:|---:|
| KXBTC15M-26MAY061800-00 | no | approved_entry | delayed_recheck_rescue:drop15_bid60 | -86.000 | False | mushroom_v28_probability_collapse_full | 0.553 | 29.000 | 45.000 | 3.000 |
| KXBTC15M-26MAY060745-45 | yes | rejected_actionable | delayed_recheck_rescue:drop15_bid60 | -70.000 | False | mushroom_v28_probability_collapse_full | 0.564 | 47.000 | 3.000 | 45.000 |
| KXBTC15M-26MAY062015-15 | no | approved_entry | delayed_recheck_rescue:drop15_bid60 | -60.000 | False | mushroom_v28_probability_collapse_full | 0.269 | 17.000 | 10.000 | 8.000 |
| KXBTC15M-26MAY062345-45 | no | rejected_actionable | parent_midprice_hold_fill | -60.000 | False | None | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY070630-30 | yes | rejected_actionable | parent_midprice_hold_fill | -59.000 | False | None | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY062230-30 | yes | rejected_actionable | parent_midprice_hold_fill | -58.000 | False | None | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY060330-30 | yes | approved_entry | delayed_recheck_rescue:drop15_bid60 | -52.000 | False | mushroom_v28_exit_value_over_hold | 0.501 | 51.000 | 43.000 | 7.000 |
| KXBTC15M-26MAY061300-00 | yes | approved_entry | delayed_recheck_rescue:drop15_bid60 | -30.000 | False | mushroom_v28_probability_collapse_full | 0.666 | n/a | n/a | n/a |
| KXBTC15M-26MAY061715-15 | yes | rejected_actionable | parent_midprice_hold_fill | -17.000 | False | None | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY062130-30 | no | rejected_actionable | delayed_recheck_rescue:drop15_bid60 | -8.000 | False | mushroom_v28_probability_reduce | 0.768 | 57.000 | 43.000 | 11.000 |
| KXBTC15M-26MAY070015-15 | no | approved_entry | delayed_recheck_rescue:drop15_bid60 | -2.000 | False | mushroom_v28_exit_value_over_hold | 0.597 | 65.000 | 52.000 | 41.000 |
| KXBTC15M-26MAY062315-15 | no | rejected_actionable | delayed_recheck_rescue:drop15_bid60 | 1.500 | False | mushroom_v28_exit_value_over_hold | 0.811 | 86.000 | 58.000 | 22.000 |
| KXBTC15M-26MAY062200-00 | no | rejected_actionable | parent_midprice_hold_fill | 4.000 | False | None | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY062145-45 | yes | rejected_actionable | parent_midprice_hold_fill | 6.000 | False | None | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY060415-15 | yes | rejected_actionable | parent_midprice_hold_fill | 6.000 | False | None | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY070530-30 | no | rejected_actionable | parent_midprice_hold_fill | 7.000 | False | None | n/a | n/a | n/a | n/a |
