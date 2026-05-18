# v28 Feature-Gate Late Collapse Recheck Rescue

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:17:00.608474+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Late rescue freeze UTC: `2026-05-07T09:09:25.393809+00:00`
- Variant-set freeze UTC: `2026-05-07T09:10:35.543805+00:00`

## Interpretation

- Research-only late collapse-recheck rescue; no live bot changes or orders.
- Diagnostic best late_collapse_delay90_exit25_recheck25_rebound8_drop15 has net 611.25c, delta vs current exits 176.0c, W/L 52/13, suppressed 1, blockers ['row_reconstructed_share_gt_35pct', 'diagnostic_prefreeze', 'late_rescue_overlay_not_independently_frozen'].
- Post-birth best base_no_exit_overlay has 29 rows and net 317.25c.

## Variants

| rank | variant | W/L | coverage | source | candidate | delta current | delta live | suppressed | H/H | adverse >=10/25 | worst adverse | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `late_collapse_delay90_exit25_recheck25_rebound8_drop15` | 52/13 | 80.488% | 0.394 | 611.250 | 176.000 | 1074.240 | 1 | 1/0 | 0/0 | 0.000 | row_reconstructed_share_gt_35pct, diagnostic_prefreeze, late_rescue_overlay_not_independently_frozen |
| 2 | `late_collapse_delay120_exit25_recheck45_rebound25_drop15` | 52/13 | 80.488% | 0.394 | 611.250 | 176.000 | 1074.240 | 1 | 1/0 | 0/0 | 0.000 | row_reconstructed_share_gt_35pct, diagnostic_prefreeze, late_rescue_overlay_not_independently_frozen |
| 3 | `late_collapse_delay150_exit25_recheck55_rebound30_drop15` | 52/13 | 80.488% | 0.394 | 611.250 | 176.000 | 1074.240 | 1 | 1/0 | 0/0 | 0.000 | row_reconstructed_share_gt_35pct, diagnostic_prefreeze, late_rescue_overlay_not_independently_frozen |
| 4 | `base_no_exit_overlay` | 51/14 | 80.488% | 0.394 | 435.250 | 0.000 | 898.240 | 0 | 0/0 | 0/0 | 0.000 | row_reconstructed_share_gt_35pct, diagnostic_prefreeze, late_rescue_overlay_not_independently_frozen |
| 5 | `combo_high60_or_late_collapse90` | 53/13 | 80.488% | 0.394 | 664.250 | 229.000 | 1127.240 | 25 | 23/2 | 3/3 | 91.000 | row_reconstructed_share_gt_35pct, harmful_suppression_present, post_recheck_adverse_ge_25c, diagnostic_prefreeze, late_rescue_overlay_not_independently_frozen |
| 6 | `combo_high60_or_late_collapse120` | 53/13 | 80.488% | 0.394 | 662.250 | 227.000 | 1125.240 | 24 | 22/2 | 3/3 | 88.000 | row_reconstructed_share_gt_35pct, harmful_suppression_present, post_recheck_adverse_ge_25c, diagnostic_prefreeze, late_rescue_overlay_not_independently_frozen |
