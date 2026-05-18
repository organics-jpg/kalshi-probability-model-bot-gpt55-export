# v28 Boundary-Clock Feature-Gate Quick Status

Research-only; compact strict-forward refresh, no live logic changes.

- Generated UTC: `2026-05-07T15:45:43.898352+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- Compact refresh only; diagnostic lanes are intentionally excluded.
- Selection uses observable feature gates; source labels are audit-only.
- post_feature_freeze_entry: best post_feature_freeze_entry_raw05_recross60_abs085 settled 43, coverage 66.66666666666667%, net 353.0c, recon 0.28, blockers ['coverage_too_low'].
- post_feature_freeze_bridge: best post_feature_freeze_bridge_raw05_recross60_abs085 settled 42, coverage 66.66666666666667%, net 177.0c, recon 0.28, blockers ['coverage_too_low', 'full_loss_cushion_lt_3'].

## post_feature_freeze_entry

- Future denominator: `75`

| rank | candidate | settled | coverage | net c | W/L | recon share | cushion | gap | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | post_feature_freeze_entry_raw05_recross60_abs085 | 43 | 66.666667 | 353.000000 | 29/14 | 0.280000 | 3 | cov+7, source+0, cushion+0.000000c | coverage_too_low |
| 2 | post_feature_freeze_entry_raw03_recross70_abs075 | 50 | 76.000000 | 286.000000 | 31/19 | 0.368421 | 2 | cov+0, source+3, cushion+14.000000c | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 3 | post_feature_freeze_entry_raw05_recross60_abs085_ask65 | 35 | 57.333333 | 227.000000 | 31/4 | 0.046512 | 2 | cov+14, source+0, cushion+73.000000c | coverage_too_low, full_loss_cushion_lt_3 |
| 4 | post_feature_freeze_entry_raw07_recross60_abs085 | 29 | 45.333333 | 277.000000 | 20/9 | 0.235294 | 2 | cov+23, source+0, cushion+23.000000c | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3 |

## post_feature_freeze_bridge

- Future denominator: `75`

| rank | candidate | settled | coverage | net c | W/L | recon share | cushion | gap | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | post_feature_freeze_bridge_raw05_recross60_abs085 | 42 | 66.666667 | 177.000000 | 27/15 | 0.280000 | 1 | cov+7, source+0, cushion+123.000000c | coverage_too_low, full_loss_cushion_lt_3 |
| 2 | post_feature_freeze_bridge_raw03_recross70_abs075 | 49 | 76.000000 | 110.000000 | 29/20 | 0.368421 | 1 | cov+0, source+3, cushion+190.000000c | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 3 | post_feature_freeze_bridge_raw05_recross60_abs085_ask65 | 33 | 57.333333 | 85.000000 | 28/5 | 0.046512 | 0 | cov+14, source+0, cushion+215.000000c | coverage_too_low, full_loss_cushion_lt_3 |
| 4 | post_feature_freeze_bridge_raw07_recross60_abs085 | 28 | 45.333333 | 200.000000 | 19/9 | 0.235294 | 2 | cov+23, source+0, cushion+100.000000c | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3 |
