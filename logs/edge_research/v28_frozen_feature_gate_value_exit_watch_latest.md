# v28 Frozen Feature-Gate Value Exit Watch

Research-only frozen watch. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:55:00.464715+00:00`
- Freeze timestamp UTC: `2026-05-07T07:36:17.925386+00:00`
- Primary candidate: `suppress_value_over_hold`
- Rule: `Within post_feature_freeze_entry_raw03_recross70_abs075 selected-side live overlap, suppress value_over_hold exits only; keep probability_reduce and probability_collapse exits active.`

## Interpretation

- Research-only frozen watch; no live orders or live bot changes.
- Primary post-birth best is suppress_value_or_reduce_p_hold80 with 14 rows, 327.6c, W/L 10/4.
- This is not live-ready because it is selected-side overlap only and assumes suppressed exits hold to settlement.

## diagnostic_prefreeze_context

| variant | settled | W/L | candidate c | live c | delta c | suppressed | suppressed W/L | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `suppress_value_over_hold` | 26 | 18/8 | 636.00 | 71.00 | 565.00 | 10 | 10/0 | 6 | selected_side_live_overlap_only, hold_to_settlement_assumption, not_live_bot_logic |
| `suppress_value_or_reduce_p_hold80` | 26 | 17/9 | 604.00 | 71.00 | 533.00 | 9 | 9/0 | 6 | selected_side_live_overlap_only, hold_to_settlement_assumption, not_live_bot_logic |

## post_value_exit_birth

| variant | settled | W/L | candidate c | live c | delta c | suppressed | suppressed W/L | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `suppress_value_or_reduce_p_hold80` | 14 | 10/4 | 327.60 | 240.00 | 87.60 | 5 | 4/1 | 3 | settled_lt_30, selected_side_live_overlap_only, hold_to_settlement_assumption, not_live_bot_logic |
| `suppress_value_over_hold` | 14 | 10/4 | -134.40 | 240.00 | -374.40 | 6 | 4/2 | 0 | settled_lt_30, net_not_positive, full_loss_cushion_lt_3, selected_side_live_overlap_only, hold_to_settlement_assumption, not_live_bot_logic |
