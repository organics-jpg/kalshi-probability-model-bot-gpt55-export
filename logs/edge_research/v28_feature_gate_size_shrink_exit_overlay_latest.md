# v28 Feature-Gate Size-Shrink Exit Overlay Audit

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:07:57.394806+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- Exit overlays are diagnostic/research-only; no live bot logic was changed.
- post_feature_freeze_entry: best overlay repair_low_absd_quarter_else_half_base_current_exit_control has W/L 51/14, candidate net 693.25c, delta vs current exits 0.0c, suppressed 0, blockers ['row_reconstructed_share_gt_35pct'].
- post_feature_freeze_bridge: best overlay repair_low_absd_quarter_else_half_base_current_exit_control has W/L 51/14, candidate net 693.25c, delta vs current exits 0.0c, suppressed 0, blockers ['row_reconstructed_share_gt_35pct'].

## post_feature_freeze_entry

- Entry policy: `repair_low_absd_quarter_else_half`
- Entries/denominator: `66/82`

| overlay | W/L | candidate net | current-exit net | entry-hold net | delta current | delta entry | joined | suppressed | source | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| repair_low_absd_quarter_else_half_base_current_exit_control | 51/14 | 693.250 | 693.250 | 408.750 | 0.000 | 284.500 | 44 | 0 | 0.394 | 6 | row_reconstructed_share_gt_35pct |
| repair_low_absd_quarter_else_half_book_gap_only | 50/15 | 505.250 | 693.250 | 408.750 | -188.000 | 96.500 | 44 | 23 | 0.394 | 5 | row_reconstructed_share_gt_35pct, suppressed_decisions_lt_30 |
| repair_low_absd_quarter_else_half_book_gap_or_reduce_p75 | 50/15 | 505.250 | 693.250 | 408.750 | -188.000 | 96.500 | 44 | 23 | 0.394 | 5 | row_reconstructed_share_gt_35pct, suppressed_decisions_lt_30 |
| repair_low_absd_quarter_else_half_book_gap_or_clip_p60_drawdown10 | 50/15 | 505.250 | 693.250 | 408.750 | -188.000 | 96.500 | 44 | 23 | 0.394 | 5 | row_reconstructed_share_gt_35pct, suppressed_decisions_lt_30 |
| repair_low_absd_quarter_else_half_book_gap_or_reduce_p75_or_clip | 50/15 | 505.250 | 693.250 | 408.750 | -188.000 | 96.500 | 44 | 23 | 0.394 | 5 | row_reconstructed_share_gt_35pct, suppressed_decisions_lt_30 |
| repair_low_absd_quarter_else_half_reduce_p75_only | 51/14 | 469.250 | 693.250 | 408.750 | -224.000 | 60.500 | 44 | 3 | 0.394 | 4 | row_reconstructed_share_gt_35pct, suppressed_decisions_lt_30 |
| repair_low_absd_quarter_else_half_clip_p60_drawdown10_only | 51/14 | 469.250 | 693.250 | 408.750 | -224.000 | 60.500 | 44 | 3 | 0.394 | 4 | row_reconstructed_share_gt_35pct, suppressed_decisions_lt_30 |

## post_feature_freeze_bridge

- Entry policy: `repair_low_absd_quarter_else_half`
- Entries/denominator: `66/82`

| overlay | W/L | candidate net | current-exit net | entry-hold net | delta current | delta entry | joined | suppressed | source | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| repair_low_absd_quarter_else_half_base_current_exit_control | 51/14 | 693.250 | 693.250 | 408.750 | 0.000 | 284.500 | 44 | 0 | 0.394 | 6 | row_reconstructed_share_gt_35pct |
| repair_low_absd_quarter_else_half_book_gap_only | 50/15 | 505.250 | 693.250 | 408.750 | -188.000 | 96.500 | 44 | 23 | 0.394 | 5 | row_reconstructed_share_gt_35pct, suppressed_decisions_lt_30 |
| repair_low_absd_quarter_else_half_book_gap_or_reduce_p75 | 50/15 | 505.250 | 693.250 | 408.750 | -188.000 | 96.500 | 44 | 23 | 0.394 | 5 | row_reconstructed_share_gt_35pct, suppressed_decisions_lt_30 |
| repair_low_absd_quarter_else_half_book_gap_or_clip_p60_drawdown10 | 50/15 | 505.250 | 693.250 | 408.750 | -188.000 | 96.500 | 44 | 23 | 0.394 | 5 | row_reconstructed_share_gt_35pct, suppressed_decisions_lt_30 |
| repair_low_absd_quarter_else_half_book_gap_or_reduce_p75_or_clip | 50/15 | 505.250 | 693.250 | 408.750 | -188.000 | 96.500 | 44 | 23 | 0.394 | 5 | row_reconstructed_share_gt_35pct, suppressed_decisions_lt_30 |
| repair_low_absd_quarter_else_half_reduce_p75_only | 51/14 | 469.250 | 693.250 | 408.750 | -224.000 | 60.500 | 44 | 3 | 0.394 | 4 | row_reconstructed_share_gt_35pct, suppressed_decisions_lt_30 |
| repair_low_absd_quarter_else_half_clip_p60_drawdown10_only | 51/14 | 469.250 | 693.250 | 408.750 | -224.000 | 60.500 | 44 | 3 | 0.394 | 4 | row_reconstructed_share_gt_35pct, suppressed_decisions_lt_30 |
