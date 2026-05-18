# v28 Feature-Gate Outcome Linkage Overlay

Research-only audit overlay. No live bot changes or orders.

- Generated UTC: `2026-05-07T06:43:15.017444+00:00`

## Interpretation

- Rows are ranked by linked blockers and linked net, but this remains an audit overlay.
- Best linked row is post_feature_freeze_entry_raw03_recross70_abs075 with settled 37, coverage 75.51020408163265%, net 275.0c, reconstructed share 0.43243243243243246, blockers ['reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].
- Linked-overlay live-ready rows: 0.

## Variants

| rank | lane | candidate | official settled/net | linked settled/net | coverage | recon | linked rows | cushion | linked blockers |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | post_feature_freeze_entry | post_feature_freeze_entry_raw03_recross70_abs075 | 37/275.000000c | 37/275.000000c | 75.510204 | 0.432432 | 0 | 2 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 2 | post_feature_freeze_bridge | post_feature_freeze_bridge_raw03_recross70_abs075 | 37/275.000000c | 37/275.000000c | 75.510204 | 0.432432 | 0 | 2 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 3 | post_feature_freeze_entry | post_feature_freeze_entry_raw05_recross60_abs085 | 33/275.000000c | 33/275.000000c | 67.346939 | 0.363636 | 0 | 2 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 4 | post_feature_freeze_bridge | post_feature_freeze_bridge_raw05_recross60_abs085 | 33/275.000000c | 33/275.000000c | 67.346939 | 0.363636 | 0 | 2 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 5 | post_feature_freeze_entry | post_feature_freeze_entry_raw07_recross60_abs085 | 22/222.000000c | 22/222.000000c | 44.897959 | 0.318182 | 0 | 2 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3 |
| 6 | post_feature_freeze_bridge | post_feature_freeze_bridge_raw07_recross60_abs085 | 22/222.000000c | 22/222.000000c | 44.897959 | 0.318182 | 0 | 2 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3 |
| 7 | post_feature_freeze_entry | post_feature_freeze_entry_raw05_recross60_abs085_ask65 | 26/142.000000c | 26/142.000000c | 53.061224 | 0.038462 | 0 | 1 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3 |
| 8 | post_feature_freeze_bridge | post_feature_freeze_bridge_raw05_recross60_abs085_ask65 | 26/142.000000c | 26/142.000000c | 53.061224 | 0.038462 | 0 | 1 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3 |

## Linked Rows

| candidate | market | source | side | result | won | net c | ask | edge | recross | abs d |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|
