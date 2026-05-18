# v28 Feature-Gate Coverage Repair Audit

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:00:46.609635+00:00`
- Freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation
- This is a research-only repair audit; no row is promoted by this scan.
- post_feature_freeze_entry: no observable relaxation clears all gates now. Anchor raw05_recross60_abs85_asknone has 55/82 entries, net 445.0c, recon 0.2727272727272727; nearest raw03_recross60_abs85_asknone has 62/82 entries, net 469.0c, recon 0.3548387096774194, blockers ['reconstructed_share_gt_35pct'].
- post_feature_freeze_bridge: no observable relaxation clears all gates now. Anchor raw05_recross60_abs85_asknone has 55/82 entries, net 445.0c, recon 0.2727272727272727; nearest raw03_recross60_abs85_asknone has 62/82 entries, net 469.0c, recon 0.3548387096774194, blockers ['reconstructed_share_gt_35pct'].

## post_feature_freeze_entry

- Anchor: `raw05_recross60_abs85_asknone`
- Anchor selected: `55/82`
- Anchor W/L: `39/16`
- Anchor net: `445.000c`
- Anchor reconstructed share: `0.273`
- Anchor blockers: `coverage_too_low`

### Nearest Observable Repairs

| rule | selected W/L | selected cov | selected net | recon | added W/L | added net | added source | needs | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| raw03_recross60_abs85_asknone | 43/19 | 75.610% | 469.000 | 0.355 | 4/3 | 24.000 | {'rejected_actionable': 7} | cov 0, clean 1, cushion 0.000c | reconstructed_share_gt_35pct |
| raw03_recross70_abs85_asknone | 43/19 | 75.610% | 469.000 | 0.355 | 4/3 | 24.000 | {'rejected_actionable': 7} | cov 0, clean 1, cushion 0.000c | reconstructed_share_gt_35pct |
| raw03_recross50_abs85_asknone | 43/19 | 75.610% | 444.000 | 0.387 | 4/3 | 24.000 | {'rejected_actionable': 7} | cov 0, clean 7, cushion 0.000c | reconstructed_share_gt_35pct |
| raw03_recross60_abs75_asknone | 42/22 | 78.049% | 307.000 | 0.391 | 4/6 | -134.000 | {'rejected_actionable': 10} | cov 0, clean 8, cushion 0.000c | reconstructed_share_gt_35pct |
| raw03_recross70_abs75_asknone | 42/22 | 78.049% | 307.000 | 0.391 | 4/6 | -134.000 | {'rejected_actionable': 10} | cov 0, clean 8, cushion 0.000c | reconstructed_share_gt_35pct |
| raw05_recross60_abs85_asknone | 39/16 | 67.073% | 445.000 | 0.273 | 0/0 | 0 | {} | cov 7, clean 0, cushion 0.000c | coverage_too_low |
| raw05_recross70_abs85_asknone | 39/16 | 67.073% | 445.000 | 0.273 | 0/0 | 0 | {} | cov 7, clean 0, cushion 0.000c | coverage_too_low |
| raw05_recross50_abs85_asknone | 38/16 | 65.854% | 409.000 | 0.296 | 0/0 | 0 | {} | cov 8, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross60_abs75_ask35 | 48/6 | 65.854% | 392.000 | 0.185 | 10/2 | -41.000 | {'approved_entry': 5, 'rejected_actionable': 7} | cov 8, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross70_abs75_ask35 | 48/6 | 65.854% | 392.000 | 0.185 | 10/2 | -41.000 | {'approved_entry': 5, 'rejected_actionable': 7} | cov 8, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross50_abs75_ask35 | 48/6 | 65.854% | 367.000 | 0.222 | 10/2 | -41.000 | {'approved_entry': 5, 'rejected_actionable': 7} | cov 8, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross60_abs75_ask65 | 47/6 | 64.634% | 312.000 | 0.170 | 10/2 | -44.000 | {'approved_entry': 6, 'rejected_actionable': 6} | cov 9, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross70_abs75_ask65 | 47/6 | 64.634% | 312.000 | 0.170 | 10/2 | -44.000 | {'approved_entry': 6, 'rejected_actionable': 6} | cov 9, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross60_abs85_ask35 | 48/4 | 63.415% | 514.000 | 0.135 | 10/0 | 102.000 | {'approved_entry': 5, 'rejected_actionable': 5} | cov 10, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross70_abs85_ask35 | 48/4 | 63.415% | 514.000 | 0.135 | 10/0 | 102.000 | {'approved_entry': 5, 'rejected_actionable': 5} | cov 10, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross50_abs85_ask35 | 48/4 | 63.415% | 489.000 | 0.173 | 10/0 | 102.000 | {'approved_entry': 5, 'rejected_actionable': 5} | cov 10, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross60_abs85_ask65 | 47/5 | 63.415% | 387.000 | 0.135 | 10/1 | 31.000 | {'approved_entry': 6, 'rejected_actionable': 5} | cov 10, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross70_abs85_ask65 | 47/5 | 63.415% | 387.000 | 0.135 | 10/1 | 31.000 | {'approved_entry': 6, 'rejected_actionable': 5} | cov 10, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross50_abs85_ask65 | 47/5 | 63.415% | 362.000 | 0.173 | 10/1 | 31.000 | {'approved_entry': 6, 'rejected_actionable': 5} | cov 10, clean 0, cushion 0.000c | coverage_too_low |
| raw05_recross60_abs75_ask35 | 43/6 | 59.756% | 349.000 | 0.102 | 5/2 | -84.000 | {'approved_entry': 5, 'rejected_actionable': 2} | cov 13, clean 0, cushion 0.000c | coverage_too_low |

### Positive Target-Coverage Relaxations

| rule | selected W/L | selected cov | selected net | recon | added W/L | added net | added source | needs | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| raw03_recross60_abs85_asknone | 43/19 | 75.610% | 469.000 | 0.355 | 4/3 | 24.000 | {'rejected_actionable': 7} | cov 0, clean 1, cushion 0.000c | reconstructed_share_gt_35pct |
| raw03_recross70_abs85_asknone | 43/19 | 75.610% | 469.000 | 0.355 | 4/3 | 24.000 | {'rejected_actionable': 7} | cov 0, clean 1, cushion 0.000c | reconstructed_share_gt_35pct |
| raw03_recross60_abs50_ask35 | 52/14 | 80.488% | 158.000 | 0.379 | 14/9 | -254.000 | {'approved_entry': 5, 'rejected_actionable': 18} | cov 0, clean 6, cushion 142.000c | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| raw03_recross70_abs50_ask35 | 52/14 | 80.488% | 158.000 | 0.379 | 14/9 | -254.000 | {'approved_entry': 5, 'rejected_actionable': 18} | cov 0, clean 6, cushion 142.000c | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| raw03_recross50_abs85_asknone | 43/19 | 75.610% | 444.000 | 0.387 | 4/3 | 24.000 | {'rejected_actionable': 7} | cov 0, clean 7, cushion 0.000c | reconstructed_share_gt_35pct |
| raw03_recross60_abs75_asknone | 42/22 | 78.049% | 307.000 | 0.391 | 4/6 | -134.000 | {'rejected_actionable': 10} | cov 0, clean 8, cushion 0.000c | reconstructed_share_gt_35pct |
| raw03_recross70_abs75_asknone | 42/22 | 78.049% | 307.000 | 0.391 | 4/6 | -134.000 | {'rejected_actionable': 10} | cov 0, clean 8, cushion 0.000c | reconstructed_share_gt_35pct |
| raw03_recross50_abs50_ask35 | 54/12 | 80.488% | 273.000 | 0.394 | 16/8 | -172.000 | {'approved_entry': 5, 'rejected_actionable': 19} | cov 0, clean 9, cushion 27.000c | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| raw03_recross50_abs75_asknone | 42/22 | 78.049% | 282.000 | 0.422 | 4/6 | -134.000 | {'rejected_actionable': 10} | cov 0, clean 14, cushion 18.000c | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| raw05_recross50_abs50_asknone | 37/31 | 82.927% | 45.000 | 0.529 | 3/15 | -359.000 | {'rejected_actionable': 18} | cov 0, clean 35, cushion 255.000c | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

## post_feature_freeze_bridge

- Anchor: `raw05_recross60_abs85_asknone`
- Anchor selected: `55/82`
- Anchor W/L: `39/16`
- Anchor net: `445.000c`
- Anchor reconstructed share: `0.273`
- Anchor blockers: `coverage_too_low`

### Nearest Observable Repairs

| rule | selected W/L | selected cov | selected net | recon | added W/L | added net | added source | needs | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| raw03_recross60_abs85_asknone | 43/19 | 75.610% | 469.000 | 0.355 | 4/3 | 24.000 | {'rejected_actionable': 7} | cov 0, clean 1, cushion 0.000c | reconstructed_share_gt_35pct |
| raw03_recross70_abs85_asknone | 43/19 | 75.610% | 469.000 | 0.355 | 4/3 | 24.000 | {'rejected_actionable': 7} | cov 0, clean 1, cushion 0.000c | reconstructed_share_gt_35pct |
| raw03_recross50_abs85_asknone | 43/19 | 75.610% | 444.000 | 0.387 | 4/3 | 24.000 | {'rejected_actionable': 7} | cov 0, clean 7, cushion 0.000c | reconstructed_share_gt_35pct |
| raw03_recross60_abs75_asknone | 42/22 | 78.049% | 307.000 | 0.391 | 4/6 | -134.000 | {'rejected_actionable': 10} | cov 0, clean 8, cushion 0.000c | reconstructed_share_gt_35pct |
| raw03_recross70_abs75_asknone | 42/22 | 78.049% | 307.000 | 0.391 | 4/6 | -134.000 | {'rejected_actionable': 10} | cov 0, clean 8, cushion 0.000c | reconstructed_share_gt_35pct |
| raw05_recross60_abs85_asknone | 39/16 | 67.073% | 445.000 | 0.273 | 0/0 | 0 | {} | cov 7, clean 0, cushion 0.000c | coverage_too_low |
| raw05_recross70_abs85_asknone | 39/16 | 67.073% | 445.000 | 0.273 | 0/0 | 0 | {} | cov 7, clean 0, cushion 0.000c | coverage_too_low |
| raw05_recross50_abs85_asknone | 38/16 | 65.854% | 409.000 | 0.296 | 0/0 | 0 | {} | cov 8, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross60_abs75_ask35 | 48/6 | 65.854% | 392.000 | 0.185 | 10/2 | -41.000 | {'approved_entry': 5, 'rejected_actionable': 7} | cov 8, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross70_abs75_ask35 | 48/6 | 65.854% | 392.000 | 0.185 | 10/2 | -41.000 | {'approved_entry': 5, 'rejected_actionable': 7} | cov 8, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross50_abs75_ask35 | 48/6 | 65.854% | 367.000 | 0.222 | 10/2 | -41.000 | {'approved_entry': 5, 'rejected_actionable': 7} | cov 8, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross60_abs75_ask65 | 47/6 | 64.634% | 312.000 | 0.170 | 10/2 | -44.000 | {'approved_entry': 6, 'rejected_actionable': 6} | cov 9, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross70_abs75_ask65 | 47/6 | 64.634% | 312.000 | 0.170 | 10/2 | -44.000 | {'approved_entry': 6, 'rejected_actionable': 6} | cov 9, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross60_abs85_ask35 | 48/4 | 63.415% | 514.000 | 0.135 | 10/0 | 102.000 | {'approved_entry': 5, 'rejected_actionable': 5} | cov 10, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross70_abs85_ask35 | 48/4 | 63.415% | 514.000 | 0.135 | 10/0 | 102.000 | {'approved_entry': 5, 'rejected_actionable': 5} | cov 10, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross50_abs85_ask35 | 48/4 | 63.415% | 489.000 | 0.173 | 10/0 | 102.000 | {'approved_entry': 5, 'rejected_actionable': 5} | cov 10, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross60_abs85_ask65 | 47/5 | 63.415% | 387.000 | 0.135 | 10/1 | 31.000 | {'approved_entry': 6, 'rejected_actionable': 5} | cov 10, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross70_abs85_ask65 | 47/5 | 63.415% | 387.000 | 0.135 | 10/1 | 31.000 | {'approved_entry': 6, 'rejected_actionable': 5} | cov 10, clean 0, cushion 0.000c | coverage_too_low |
| raw03_recross50_abs85_ask65 | 47/5 | 63.415% | 362.000 | 0.173 | 10/1 | 31.000 | {'approved_entry': 6, 'rejected_actionable': 5} | cov 10, clean 0, cushion 0.000c | coverage_too_low |
| raw05_recross60_abs75_ask35 | 43/6 | 59.756% | 349.000 | 0.102 | 5/2 | -84.000 | {'approved_entry': 5, 'rejected_actionable': 2} | cov 13, clean 0, cushion 0.000c | coverage_too_low |

### Positive Target-Coverage Relaxations

| rule | selected W/L | selected cov | selected net | recon | added W/L | added net | added source | needs | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| raw03_recross60_abs85_asknone | 43/19 | 75.610% | 469.000 | 0.355 | 4/3 | 24.000 | {'rejected_actionable': 7} | cov 0, clean 1, cushion 0.000c | reconstructed_share_gt_35pct |
| raw03_recross70_abs85_asknone | 43/19 | 75.610% | 469.000 | 0.355 | 4/3 | 24.000 | {'rejected_actionable': 7} | cov 0, clean 1, cushion 0.000c | reconstructed_share_gt_35pct |
| raw03_recross60_abs50_ask35 | 52/14 | 80.488% | 158.000 | 0.379 | 14/9 | -254.000 | {'approved_entry': 5, 'rejected_actionable': 18} | cov 0, clean 6, cushion 142.000c | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| raw03_recross70_abs50_ask35 | 52/14 | 80.488% | 158.000 | 0.379 | 14/9 | -254.000 | {'approved_entry': 5, 'rejected_actionable': 18} | cov 0, clean 6, cushion 142.000c | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| raw03_recross50_abs85_asknone | 43/19 | 75.610% | 444.000 | 0.387 | 4/3 | 24.000 | {'rejected_actionable': 7} | cov 0, clean 7, cushion 0.000c | reconstructed_share_gt_35pct |
| raw03_recross60_abs75_asknone | 42/22 | 78.049% | 307.000 | 0.391 | 4/6 | -134.000 | {'rejected_actionable': 10} | cov 0, clean 8, cushion 0.000c | reconstructed_share_gt_35pct |
| raw03_recross70_abs75_asknone | 42/22 | 78.049% | 307.000 | 0.391 | 4/6 | -134.000 | {'rejected_actionable': 10} | cov 0, clean 8, cushion 0.000c | reconstructed_share_gt_35pct |
| raw03_recross50_abs50_ask35 | 54/12 | 80.488% | 273.000 | 0.394 | 16/8 | -172.000 | {'approved_entry': 5, 'rejected_actionable': 19} | cov 0, clean 9, cushion 27.000c | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| raw03_recross50_abs75_asknone | 42/22 | 78.049% | 282.000 | 0.422 | 4/6 | -134.000 | {'rejected_actionable': 10} | cov 0, clean 14, cushion 18.000c | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| raw05_recross50_abs50_asknone | 37/31 | 82.927% | 45.000 | 0.529 | 3/15 | -359.000 | {'rejected_actionable': 18} | cov 0, clean 35, cushion 255.000c | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
