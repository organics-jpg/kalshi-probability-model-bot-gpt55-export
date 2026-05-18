# v28 Feature-Gate Size-Shrink Source Runway

Research-only runway. No live bot changes or orders.

- Generated UTC: `2026-05-07T14:53:15.108515+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Refreshed live net: `1107c`

## Interpretation

- This is a source-dilution runway for an already-frozen size-shrink audit, not a new threshold search.
- post_feature_freeze_entry / repair_low_absd_quarter_else_half needs 9 approved qualifying row(s) to clear the row-source gate.
- Current weighted net is 369.0c, leaving 69.0c above the three-full-loss cushion.
- Against the refreshed live-only baseline of 1107c, this lane is -738.0c, so source dilution alone is not enough for promotion.

## Lane Runway

| lane | policy | settled | coverage | weighted net | row recon | clean rows needed | cushion surplus | delta vs live | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| post_feature_freeze_entry | repair_low_absd_quarter_else_half | 45 | 75.409836 | 369.000000 | 0.413043 | 9 | 69.000000 | -738.000000 | row_reconstructed_share_gt_35pct, below_refreshed_live_baseline |
| post_feature_freeze_bridge | repair_low_absd_quarter_else_half | 45 | 75.409836 | 369.000000 | 0.413043 | 9 | 69.000000 | -738.000000 | row_reconstructed_share_gt_35pct, below_refreshed_live_baseline |

## Best Lane Details

- Source counts: `{'approved_entry': 27, 'rejected_actionable': 19}`
- Approved/reconstructed rows: `27/19`
- Max total weighted loss while preserving cushion: `69.000000c`
- Max weighted loss per needed clean row: `7.666667c`
- Full-weight wins needed to tie live baseline: `8`
