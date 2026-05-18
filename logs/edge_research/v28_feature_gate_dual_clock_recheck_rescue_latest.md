# v28 Feature-Gate Dual-Clock Recheck Rescue

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:18:50.610821+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Dual-clock freeze UTC: `2026-05-07T09:16:37.047947+00:00`

## Interpretation

- Research-only dual-clock delayed recheck rescue; no live bot changes or orders.
- Diagnostic best late_collapse90_only has net 611.25c, delta vs current exits 176.0c, W/L 52/13, suppressed 1, blockers ['row_reconstructed_share_gt_35pct', 'diagnostic_prefreeze', 'dual_clock_rescue_not_independently_frozen'].

## Variants

| rank | variant | W/L | coverage | source | candidate | delta current | delta live | suppressed | H/H | rules | adverse >=10/25 | worst adverse | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | `late_collapse90_only` | 52/13 | 80.488% | 0.394 | 611.250 | 176.000 | 691.250 | 1 | 1/0 | {'late_collapse90': 1} | 0/0 | 0.000 | row_reconstructed_share_gt_35pct, diagnostic_prefreeze, dual_clock_rescue_not_independently_frozen |
| 2 | `fast_collapse60_only` | 52/13 | 80.488% | 0.394 | 587.250 | 152.000 | 667.250 | 1 | 1/0 | {'fast_collapse60': 1} | 0/0 | 8.000 | row_reconstructed_share_gt_35pct, diagnostic_prefreeze, dual_clock_rescue_not_independently_frozen |
| 3 | `base_no_exit_overlay` | 51/14 | 80.488% | 0.394 | 435.250 | 0.000 | 515.250 | 0 | 0/0 | {} | 0/0 | 0.000 | row_reconstructed_share_gt_35pct, diagnostic_prefreeze, dual_clock_rescue_not_independently_frozen |
| 4 | `high60_or_fast_collapse60_or_late_collapse90` | 54/12 | 80.488% | 0.394 | 828.250 | 393.000 | 908.250 | 29 | 27/2 | {'high60': 27, 'fast_collapse60': 1, 'late_collapse90': 1} | 4/4 | 88.000 | row_reconstructed_share_gt_35pct, harmful_suppression_present, post_recheck_adverse_ge_25c, diagnostic_prefreeze, dual_clock_rescue_not_independently_frozen |
| 5 | `high60_or_late_collapse90` | 53/13 | 80.488% | 0.394 | 676.250 | 241.000 | 756.250 | 28 | 26/2 | {'high60': 27, 'late_collapse90': 1} | 4/4 | 88.000 | row_reconstructed_share_gt_35pct, harmful_suppression_present, post_recheck_adverse_ge_25c, diagnostic_prefreeze, dual_clock_rescue_not_independently_frozen |
| 6 | `high60_or_fast_collapse60` | 53/13 | 80.488% | 0.394 | 652.250 | 217.000 | 732.250 | 28 | 26/2 | {'high60': 27, 'fast_collapse60': 1} | 4/4 | 88.000 | row_reconstructed_share_gt_35pct, harmful_suppression_present, post_recheck_adverse_ge_25c, diagnostic_prefreeze, dual_clock_rescue_not_independently_frozen |
| 7 | `high60_only` | 52/14 | 80.488% | 0.394 | 500.250 | 65.000 | 580.250 | 27 | 25/2 | {'high60': 27} | 4/4 | 88.000 | row_reconstructed_share_gt_35pct, harmful_suppression_present, post_recheck_adverse_ge_25c, diagnostic_prefreeze, dual_clock_rescue_not_independently_frozen |

## Suppressed Rows For Best Variant

| market | side | source | reason | current | hold | delta | rule | exit bid | recheck bid | rebound | adverse |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---:|
| KXBTC15M-26MAY062015-15 | no | approved_entry | mushroom_v28_probability_collapse_full | -60.000 | 116.000 | 176.000 | late_collapse90 | 17.000 | 27.000 | 10.000 | 0.000 |
