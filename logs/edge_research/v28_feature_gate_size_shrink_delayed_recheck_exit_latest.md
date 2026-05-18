# v28 Feature-Gate Size-Shrink Delayed-Recheck Exit

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:11:45.331142+00:00`
- Policy: `repair_low_absd_quarter_else_half`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Overlay freeze UTC: `2026-05-07T08:47:54.507128+00:00`
- Live baseline: `-462.990c`

## Interpretation

- Research-only delayed-recheck exit overlay; no live bot changes or orders.
- Diagnostic best variant delay60_bid60_drop10 has net 500.25c, delta vs current exits 65.0c, W/L 52/14, suppressed 27, blockers ['row_reconstructed_share_gt_35pct', 'diagnostic_prefreeze', 'exit_overlay_not_independently_frozen'].
- Post-overlay-birth best variant base_no_exit_overlay has 29 settled rows and net 317.25c; only this post-birth lane can become live-test evidence.
- This does not solve source quality; it only tests whether the current strict branch has an exit-policy repair path.

## Lanes

| lane | strict forward | denominator | entries | best variant | W/L | coverage | source | candidate | delta live | blockers |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---|
| `diagnostic_prefreeze_context` | False | 82 | 66 | `delay60_bid60_drop10` | 52/14 | 80.488% | 0.394 | 500.250 | 963.240 | row_reconstructed_share_gt_35pct, diagnostic_prefreeze, exit_overlay_not_independently_frozen |
| `post_delayed_recheck_overlay_birth` | True | 33 | 29 | `base_no_exit_overlay` | 24/5 | 87.879% | 0.414 | 317.250 | 780.240 | settled_lt_30, row_reconstructed_share_gt_35pct |

## Diagnostic Variants

| rank | variant | W/L | coverage | source | entry hold | current exit | candidate | delta current | delta live | joined | suppressed | H/H | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `delay60_bid60_drop10` | 52/14 | 80.488% | 0.394 | 408.750 | 435.250 | 500.250 | 65.000 | 963.240 | 33 | 27 | 25/2 | 5 | row_reconstructed_share_gt_35pct, diagnostic_prefreeze, exit_overlay_not_independently_frozen |
| 2 | `delay60_bid60_drop11` | 52/14 | 80.488% | 0.394 | 408.750 | 435.250 | 500.250 | 65.000 | 963.240 | 33 | 27 | 25/2 | 5 | row_reconstructed_share_gt_35pct, diagnostic_prefreeze, exit_overlay_not_independently_frozen |
| 3 | `delay60_bid65_drop10` | 52/14 | 80.488% | 0.394 | 408.750 | 435.250 | 500.250 | 65.000 | 963.240 | 33 | 27 | 25/2 | 5 | row_reconstructed_share_gt_35pct, diagnostic_prefreeze, exit_overlay_not_independently_frozen |
| 4 | `delay120_bid60_drop10` | 52/14 | 80.488% | 0.394 | 408.750 | 435.250 | 486.250 | 51.000 | 949.240 | 33 | 23 | 21/2 | 4 | row_reconstructed_share_gt_35pct, diagnostic_prefreeze, exit_overlay_not_independently_frozen |
| 5 | `base_no_exit_overlay` | 51/14 | 80.488% | 0.394 | 408.750 | 435.250 | 435.250 | 0.000 | 898.240 | 33 | 0 | 0/0 | 4 | row_reconstructed_share_gt_35pct, diagnostic_prefreeze, exit_overlay_not_independently_frozen |

## Worst Rows For Best Variant

| market | side | source | reason | current | hold | candidate | weight | weighted | exit bid | recheck bid | drop |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY071100-00 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 4.000 | -166.000 | -166.000 | 1.000 | -166.000 | 80.000 | 88.000 | 0.000 |
| KXBTC15M-26MAY071015-15 | no | approved_entry | mushroom_v28_probability_reduce | -16.000 | -162.000 | -162.000 | 1.000 | -162.000 | 74.000 | 85.000 | 0.000 |
| KXBTC15M-26MAY061800-00 | no | approved_entry | mushroom_v28_probability_collapse_full | -86.000 | 66.000 | -86.000 | 1.000 | -86.000 | 29.000 | 45.000 | 3.000 |
| KXBTC15M-26MAY062015-15 | no | approved_entry | mushroom_v28_probability_collapse_full | -60.000 | 116.000 | -60.000 | 1.000 | -60.000 | 17.000 | 10.000 | 8.000 |
| KXBTC15M-26MAY071215-15 | yes | rejected_actionable | None | -75.000 | -75.000 | -75.000 | 0.500 | -37.500 | n/a | n/a | n/a |
| KXBTC15M-26MAY062130-30 | no | rejected_actionable | mushroom_v28_probability_reduce | -32.000 | -152.000 | -32.000 | 1.000 | -32.000 | 57.000 | 43.000 | 11.000 |
| KXBTC15M-26MAY070900-00 | no | rejected_actionable | None | -73.000 | -73.000 | -73.000 | 0.250 | -18.250 | n/a | n/a | n/a |
| KXBTC15M-26MAY061715-15 | yes | rejected_actionable | None | -68.000 | -68.000 | -68.000 | 0.250 | -17.000 | n/a | n/a | n/a |
| KXBTC15M-26MAY062345-45 | no | rejected_actionable | None | -60.000 | -60.000 | -60.000 | 0.250 | -15.000 | n/a | n/a | n/a |
| KXBTC15M-26MAY070630-30 | yes | rejected_actionable | None | -59.000 | -59.000 | -59.000 | 0.250 | -14.750 | n/a | n/a | n/a |
| KXBTC15M-26MAY062230-30 | yes | rejected_actionable | None | -58.000 | -58.000 | -58.000 | 0.250 | -14.500 | n/a | n/a | n/a |
| KXBTC15M-26MAY070615-15 | yes | rejected_actionable | None | -47.000 | -47.000 | -47.000 | 0.250 | -11.750 | n/a | n/a | n/a |
