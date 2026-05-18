# v28 Feature-Gate Size-Shrink Delayed-Recheck Rescue

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:13:29.193312+00:00`
- Policy: `repair_low_absd_quarter_else_half`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Rescue freeze UTC: `2026-05-07T08:55:51.390169+00:00`
- Live baseline: `-462.990c`

## Interpretation

- Research-only delayed-recheck collapse/rebound rescue; no live bot changes or orders.
- Diagnostic best collapse_rebound_delay60_exit45_recheck40_rebound10_drop15 has net 587.25c, delta vs current exits 152.0c, W/L 52/13, suppressed 1, blockers ['row_reconstructed_share_gt_35pct', 'diagnostic_prefreeze', 'rescue_overlay_not_independently_frozen'].
- Post-rescue-birth best base_no_exit_overlay has 29 rows and net 317.25c; only post-birth rows can become live-test evidence.

## Lanes

| lane | strict forward | denominator | entries | best variant | W/L | coverage | source | candidate | delta live | blockers |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---|
| `diagnostic_prefreeze_context` | False | 82 | 66 | `collapse_rebound_delay60_exit45_recheck40_rebound10_drop15` | 52/13 | 80.488% | 0.394 | 587.250 | 1050.240 | row_reconstructed_share_gt_35pct, diagnostic_prefreeze, rescue_overlay_not_independently_frozen |
| `post_rescue_overlay_birth` | True | 33 | 29 | `base_no_exit_overlay` | 24/5 | 87.879% | 0.414 | 317.250 | 780.240 | settled_lt_30, row_reconstructed_share_gt_35pct |

## Diagnostic Variants

| rank | variant | W/L | coverage | source | entry hold | current exit | candidate | delta current | delta live | joined | suppressed | H/H | adverse >=10/25 | worst adverse | rules | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| 1 | `collapse_rebound_delay60_exit45_recheck40_rebound10_drop15` | 52/13 | 80.488% | 0.394 | 408.750 | 435.250 | 587.250 | 152.000 | 1050.240 | 33 | 1 | 1/0 | 0/0 | 8.000 | {'collapse_rebound': 1} | 5 | row_reconstructed_share_gt_35pct, diagnostic_prefreeze, rescue_overlay_not_independently_frozen |
| 2 | `collapse_rebound_delay60_exit50_recheck45_rebound10_drop15` | 52/13 | 80.488% | 0.394 | 408.750 | 435.250 | 587.250 | 152.000 | 1050.240 | 33 | 1 | 1/0 | 0/0 | 8.000 | {'collapse_rebound': 1} | 5 | row_reconstructed_share_gt_35pct, diagnostic_prefreeze, rescue_overlay_not_independently_frozen |
| 3 | `base_no_exit_overlay` | 51/14 | 80.488% | 0.394 | 408.750 | 435.250 | 435.250 | 0.000 | 898.240 | 33 | 0 | 0/0 | 0/0 | 0.000 | {} | 4 | row_reconstructed_share_gt_35pct, diagnostic_prefreeze, rescue_overlay_not_independently_frozen |
| 4 | `combo_high60_or_collapse40` | 53/13 | 80.488% | 0.394 | 408.750 | 435.250 | 652.250 | 217.000 | 1115.240 | 33 | 28 | 26/2 | 4/4 | 88.000 | {'high_bid': 27, 'collapse_rebound': 1} | 6 | row_reconstructed_share_gt_35pct, harmful_suppression_present, post_recheck_adverse_ge_25c, diagnostic_prefreeze, rescue_overlay_not_independently_frozen |
| 5 | `high_bid_delay60_bid60_drop10` | 52/14 | 80.488% | 0.394 | 408.750 | 435.250 | 500.250 | 65.000 | 963.240 | 33 | 27 | 25/2 | 4/4 | 88.000 | {'high_bid': 27} | 5 | row_reconstructed_share_gt_35pct, harmful_suppression_present, post_recheck_adverse_ge_25c, diagnostic_prefreeze, rescue_overlay_not_independently_frozen |

## Suppressed Rows For Best Variant

| market | side | source | reason | current | hold | delta | rule | exit bid | recheck bid | rebound | post min | post adverse |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY061800-00 | no | approved_entry | mushroom_v28_probability_collapse_full | -86.000 | 66.000 | 152.000 | collapse_rebound | 29.000 | 45.000 | 16.000 | 37.000 | 8.000 |

## Worst Rows For Best Variant

| market | side | source | reason | current | hold | candidate | weight | weighted | rule | exit bid | recheck bid | rebound | drop |
|---|---|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|
| KXBTC15M-26MAY062015-15 | no | approved_entry | mushroom_v28_probability_collapse_full | -60.000 | 116.000 | -60.000 | 1.000 | -60.000 | None | 17.000 | 10.000 | -7.000 | 8.000 |
| KXBTC15M-26MAY071215-15 | yes | rejected_actionable | None | -75.000 | -75.000 | -75.000 | 0.500 | -37.500 | None | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY062130-30 | no | rejected_actionable | mushroom_v28_probability_reduce | -32.000 | -152.000 | -32.000 | 1.000 | -32.000 | None | 57.000 | 43.000 | -14.000 | 11.000 |
| KXBTC15M-26MAY070900-00 | no | rejected_actionable | None | -73.000 | -73.000 | -73.000 | 0.250 | -18.250 | None | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY061715-15 | yes | rejected_actionable | None | -68.000 | -68.000 | -68.000 | 0.250 | -17.000 | None | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY071015-15 | no | approved_entry | mushroom_v28_probability_reduce | -16.000 | -162.000 | -16.000 | 1.000 | -16.000 | None | 74.000 | 85.000 | 11.000 | 0.000 |
| KXBTC15M-26MAY062345-45 | no | rejected_actionable | None | -60.000 | -60.000 | -60.000 | 0.250 | -15.000 | None | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY070630-30 | yes | rejected_actionable | None | -59.000 | -59.000 | -59.000 | 0.250 | -14.750 | None | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY062230-30 | yes | rejected_actionable | None | -58.000 | -58.000 | -58.000 | 0.250 | -14.500 | None | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY070615-15 | yes | rejected_actionable | None | -47.000 | -47.000 | -47.000 | 0.250 | -11.750 | None | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY061700-00 | no | rejected_actionable | None | -42.000 | -42.000 | -42.000 | 0.250 | -10.500 | None | n/a | n/a | n/a | n/a |
| KXBTC15M-26MAY061400-00 | no | approved_entry | mushroom_v28_exit_value_over_hold | -10.000 | 22.000 | -10.000 | 1.000 | -10.000 | None | 81.000 | 92.000 | 11.000 | 0.000 |
