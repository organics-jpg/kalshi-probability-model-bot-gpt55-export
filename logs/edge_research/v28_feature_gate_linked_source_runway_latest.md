# v28 Feature-Gate Linked Source Runway

Research-only audit overlay. No live bot changes or orders.

- Generated UTC: `2026-05-07T14:53:15.122001+00:00`

## Interpretation

- This is an audit overlay; it does not change official candidate scoring or promotion status.
- Best linked source-runway row is post_feature_freeze_entry_raw05_recross60_abs085 with net 451.0c, coverage 64.78873239436619%, reconstructed share 0.2826086956521739, and blockers ['coverage_too_low'].
- It needs 0 future clean approved selected rows to clear the source gate if no new rejected selected rows are added.

## Variants

| rank | lane | candidate | linked settled/net | coverage | recon | approved net | rejected net | clean rows needed | linked blockers |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | post_feature_freeze_entry | post_feature_freeze_entry_raw05_recross60_abs085 | 46/451.000000c | 64.788732 | 0.282609 | 387.000000 | 64.000000 | 0 | coverage_too_low |
| 2 | post_feature_freeze_bridge | post_feature_freeze_bridge_raw05_recross60_abs085 | 46/446.000000c | 64.788732 | 0.282609 | 382.000000 | 64.000000 | 0 | coverage_too_low |
| 3 | post_feature_freeze_entry | post_feature_freeze_entry_raw07_recross60_abs085 | 33/368.000000c | 46.478873 | 0.242424 | 290.000000 | 78.000000 | 0 | coverage_too_low |
| 4 | post_feature_freeze_bridge | post_feature_freeze_bridge_raw07_recross60_abs085 | 33/365.000000c | 46.478873 | 0.242424 | 287.000000 | 78.000000 | 0 | coverage_too_low |
| 5 | post_feature_freeze_entry | post_feature_freeze_entry_raw05_recross60_abs085_ask65 | 39/319.000000c | 54.929577 | 0.051282 | 305.000000 | 14.000000 | 0 | coverage_too_low |
| 6 | post_feature_freeze_bridge | post_feature_freeze_bridge_raw05_recross60_abs085_ask65 | 39/315.000000c | 54.929577 | 0.051282 | 301.000000 | 14.000000 | 0 | coverage_too_low |
| 7 | post_feature_freeze_entry | post_feature_freeze_entry_raw03_recross70_abs075 | 53/388.000000c | 74.647887 | 0.377358 | 408.000000 | -20.000000 | 5 | coverage_too_low, reconstructed_share_gt_35pct |
| 8 | post_feature_freeze_bridge | post_feature_freeze_bridge_raw03_recross70_abs075 | 53/379.000000c | 74.647887 | 0.377358 | 403.000000 | -24.000000 | 5 | coverage_too_low, reconstructed_share_gt_35pct |

## Source Split

| candidate | source | entries | settled | W/L | net c | coverage contribution |
|---|---|---:|---:|---:|---:|---:|
| post_feature_freeze_entry_raw05_recross60_abs085 | approved_entry | 33 | 33 | 30/3 | 387.000000 | 46.478873 |
| post_feature_freeze_entry_raw05_recross60_abs085 | rejected_actionable | 13 | 13 | 3/10 | 64.000000 | 18.309859 |
| post_feature_freeze_bridge_raw05_recross60_abs085 | approved_entry | 33 | 33 | 30/3 | 382.000000 | 46.478873 |
| post_feature_freeze_bridge_raw05_recross60_abs085 | rejected_actionable | 13 | 13 | 3/10 | 64.000000 | 18.309859 |
| post_feature_freeze_entry_raw07_recross60_abs085 | approved_entry | 25 | 25 | 22/3 | 290.000000 | 35.211268 |
| post_feature_freeze_entry_raw07_recross60_abs085 | rejected_actionable | 8 | 8 | 2/6 | 78.000000 | 11.267606 |
| post_feature_freeze_bridge_raw07_recross60_abs085 | approved_entry | 25 | 25 | 22/3 | 287.000000 | 35.211268 |
| post_feature_freeze_bridge_raw07_recross60_abs085 | rejected_actionable | 8 | 8 | 2/6 | 78.000000 | 11.267606 |
| post_feature_freeze_entry_raw05_recross60_abs085_ask65 | approved_entry | 37 | 37 | 33/4 | 305.000000 | 52.112676 |
| post_feature_freeze_entry_raw05_recross60_abs085_ask65 | rejected_actionable | 2 | 2 | 2/0 | 14.000000 | 2.816901 |
| post_feature_freeze_bridge_raw05_recross60_abs085_ask65 | approved_entry | 37 | 37 | 33/4 | 301.000000 | 52.112676 |
| post_feature_freeze_bridge_raw05_recross60_abs085_ask65 | rejected_actionable | 2 | 2 | 2/0 | 14.000000 | 2.816901 |
| post_feature_freeze_entry_raw03_recross70_abs075 | approved_entry | 33 | 33 | 30/3 | 408.000000 | 46.478873 |
| post_feature_freeze_entry_raw03_recross70_abs075 | rejected_actionable | 20 | 20 | 5/15 | -20.000000 | 28.169014 |
| post_feature_freeze_bridge_raw03_recross70_abs075 | approved_entry | 33 | 33 | 30/3 | 403.000000 | 46.478873 |
| post_feature_freeze_bridge_raw03_recross70_abs075 | rejected_actionable | 20 | 20 | 5/15 | -24.000000 | 28.169014 |
