# v28 Boundary-Clock Feature-Gate Candidate

Research-only; frozen candidate, no live logic changes.

- Generated UTC: `2026-05-07T18:14:31.766018+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- Selection uses only observable features; source labels are audit-only.
- diagnostic_entry: best diagnostic_entry_raw03_recross70_abs075 settled 100, coverage 82.64462809917356%, net 725.0c, recon 0.32, blockers [].
- diagnostic_bridge: best diagnostic_bridge_raw03_recross70_abs075 settled 98, coverage 82.3529411764706%, net 717.0c, recon 0.32653061224489793, blockers [].
- post_feature_freeze_entry: best post_feature_freeze_entry_raw07_recross60_abs085 settled 38, coverage 46.34146341463415%, net 454.0c, recon 0.21052631578947367, blockers ['coverage_too_low'].
- post_feature_freeze_bridge: best post_feature_freeze_bridge_raw07_recross60_abs085 settled 38, coverage 46.34146341463415%, net 454.0c, recon 0.21052631578947367, blockers ['coverage_too_low'].

## diagnostic_entry

- Freeze UTC: `2026-05-06T07:07:27.790042+00:00`
- Future denominator: `121`

| rank | candidate | settled | coverage | net c | W/L | recon share | source counts | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---|---:|---|
| 1 | diagnostic_entry_raw03_recross70_abs075 | 100 | 82.644628 | 725.000000 | 72/28 | 0.320000 | {'approved_entry': 68, 'rejected_actionable': 32} | 7 | none |
| 2 | diagnostic_entry_raw05_recross60_abs085 | 86 | 71.074380 | 859.000000 | 67/19 | 0.197674 | {'approved_entry': 69, 'rejected_actionable': 17} | 8 | coverage_too_low |
| 3 | diagnostic_entry_raw07_recross60_abs085 | 60 | 49.586777 | 836.000000 | 49/11 | 0.150000 | {'approved_entry': 51, 'rejected_actionable': 9} | 8 | coverage_too_low |
| 4 | diagnostic_entry_raw05_recross60_abs085_ask65 | 78 | 64.462810 | 775.000000 | 71/7 | 0.051282 | {'approved_entry': 74, 'rejected_actionable': 4} | 7 | coverage_too_low |

## diagnostic_bridge

- Freeze UTC: `2026-05-06T07:35:02.597585+00:00`
- Future denominator: `119`

| rank | candidate | settled | coverage | net c | W/L | recon share | source counts | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---|---:|---|
| 1 | diagnostic_bridge_raw03_recross70_abs075 | 98 | 82.352941 | 717.000000 | 71/27 | 0.326531 | {'rejected_actionable': 32, 'approved_entry': 66} | 7 | none |
| 2 | diagnostic_bridge_raw05_recross60_abs085 | 84 | 70.588235 | 851.000000 | 66/18 | 0.202381 | {'rejected_actionable': 17, 'approved_entry': 67} | 8 | coverage_too_low |
| 3 | diagnostic_bridge_raw07_recross60_abs085 | 58 | 48.739496 | 828.000000 | 48/10 | 0.155172 | {'rejected_actionable': 9, 'approved_entry': 49} | 8 | coverage_too_low |
| 4 | diagnostic_bridge_raw05_recross60_abs085_ask65 | 76 | 63.865546 | 738.000000 | 69/7 | 0.052632 | {'rejected_actionable': 4, 'approved_entry': 72} | 7 | coverage_too_low |

## post_feature_freeze_entry

- Freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Future denominator: `82`

| rank | candidate | settled | coverage | net c | W/L | recon share | source counts | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---|---:|---|
| 1 | post_feature_freeze_entry_raw07_recross60_abs085 | 38 | 46.341463 | 454.000000 | 29/9 | 0.210526 | {'approved_entry': 30, 'rejected_actionable': 8} | 4 | coverage_too_low |
| 2 | post_feature_freeze_entry_raw05_recross60_abs085 | 55 | 67.073171 | 445.000000 | 39/16 | 0.272727 | {'approved_entry': 40, 'rejected_actionable': 15} | 4 | coverage_too_low |
| 3 | post_feature_freeze_entry_raw05_recross60_abs085_ask65 | 47 | 57.317073 | 344.000000 | 42/5 | 0.042553 | {'approved_entry': 45, 'rejected_actionable': 2} | 3 | coverage_too_low |
| 4 | post_feature_freeze_entry_raw03_recross70_abs075 | 64 | 78.048780 | 307.000000 | 42/22 | 0.390625 | {'approved_entry': 39, 'rejected_actionable': 25} | 3 | reconstructed_share_gt_35pct |

## post_feature_freeze_bridge

- Freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Future denominator: `82`

| rank | candidate | settled | coverage | net c | W/L | recon share | source counts | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---|---:|---|
| 1 | post_feature_freeze_bridge_raw07_recross60_abs085 | 38 | 46.341463 | 454.000000 | 29/9 | 0.210526 | {'approved_entry': 30, 'rejected_actionable': 8} | 4 | coverage_too_low |
| 2 | post_feature_freeze_bridge_raw05_recross60_abs085 | 55 | 67.073171 | 445.000000 | 39/16 | 0.272727 | {'approved_entry': 40, 'rejected_actionable': 15} | 4 | coverage_too_low |
| 3 | post_feature_freeze_bridge_raw05_recross60_abs085_ask65 | 47 | 57.317073 | 344.000000 | 42/5 | 0.042553 | {'approved_entry': 45, 'rejected_actionable': 2} | 3 | coverage_too_low |
| 4 | post_feature_freeze_bridge_raw03_recross70_abs075 | 64 | 78.048780 | 307.000000 | 42/22 | 0.390625 | {'approved_entry': 39, 'rejected_actionable': 25} | 3 | reconstructed_share_gt_35pct |
