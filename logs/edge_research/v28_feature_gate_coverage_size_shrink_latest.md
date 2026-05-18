# v28 Feature-Gate Coverage Size-Shrink Audit

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:02:31.982243+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- This is a size/portfolio audit only; row-count source gates still matter for promotion.
- post_feature_freeze_entry: best policy repair_eighth has 66/82 entries, 66 settled, W/L 54/12, weighted net 423.5c, row/exposure recon 0.3939393939393939/0.20833333333333334, cushion 4, blockers ['row_reconstructed_share_gt_35pct'].
- post_feature_freeze_bridge: best policy repair_eighth has 66/82 entries, 66 settled, W/L 54/12, weighted net 423.5c, row/exposure recon 0.3939393939393939/0.20833333333333334, cushion 4, blockers ['row_reconstructed_share_gt_35pct'].

## post_feature_freeze_entry

- Anchor rule: `raw05_recross60_abs85_asknone`
- Repair rule: `raw03_recross50_abs50_ask35`
- Anchor/repair/added entries: `55/66/24`

| policy | entries | settled | W/L | coverage | weighted net | row recon | exposure recon | cushion | needs | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| repair_eighth | 66 | 66 | 54/12 | 80.488% | 423.500 | 0.394 | 0.208 | 4 | cov 0, clean 9, cushion 0.000c | row_reconstructed_share_gt_35pct |
| repair_low_absd_quarter_else_half | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | cov 0, clean 9, cushion 0.000c | row_reconstructed_share_gt_35pct |
| repair_quarter | 66 | 66 | 54/12 | 80.488% | 402.000 | 0.394 | 0.245 | 4 | cov 0, clean 9, cushion 0.000c | row_reconstructed_share_gt_35pct |
| repair_absd_recross_scaled | 66 | 66 | 54/12 | 80.488% | 373.014 | 0.394 | 0.301 | 3 | cov 0, clean 9, cushion 0.000c | row_reconstructed_share_gt_35pct |
| repair_low_absd_recross_eighth_else_half | 66 | 66 | 54/12 | 80.488% | 360.875 | 0.394 | 0.281 | 3 | cov 0, clean 9, cushion 0.000c | row_reconstructed_share_gt_35pct |
| repair_half | 66 | 66 | 54/12 | 80.488% | 359.000 | 0.394 | 0.306 | 3 | cov 0, clean 9, cushion 0.000c | row_reconstructed_share_gt_35pct |
| repair_midcheap_quarter_else_half | 66 | 66 | 54/12 | 80.488% | 356.500 | 0.394 | 0.292 | 3 | cov 0, clean 9, cushion 0.000c | row_reconstructed_share_gt_35pct |
| repair_absd_squared | 66 | 66 | 54/12 | 80.488% | 348.158 | 0.394 | 0.322 | 3 | cov 0, clean 9, cushion 0.000c | row_reconstructed_share_gt_35pct |
| repair_absd_linear | 66 | 66 | 54/12 | 80.488% | 315.830 | 0.394 | 0.347 | 3 | cov 0, clean 9, cushion 0.000c | row_reconstructed_share_gt_35pct |
| repair_full_control | 66 | 66 | 54/12 | 80.488% | 273.000 | 0.394 | 0.394 | 2 | cov 0, clean 9, cushion 27.000c | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |

## post_feature_freeze_bridge

- Anchor rule: `raw05_recross60_abs85_asknone`
- Repair rule: `raw03_recross50_abs50_ask35`
- Anchor/repair/added entries: `55/66/24`

| policy | entries | settled | W/L | coverage | weighted net | row recon | exposure recon | cushion | needs | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| repair_eighth | 66 | 66 | 54/12 | 80.488% | 423.500 | 0.394 | 0.208 | 4 | cov 0, clean 9, cushion 0.000c | row_reconstructed_share_gt_35pct |
| repair_low_absd_quarter_else_half | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | cov 0, clean 9, cushion 0.000c | row_reconstructed_share_gt_35pct |
| repair_quarter | 66 | 66 | 54/12 | 80.488% | 402.000 | 0.394 | 0.245 | 4 | cov 0, clean 9, cushion 0.000c | row_reconstructed_share_gt_35pct |
| repair_absd_recross_scaled | 66 | 66 | 54/12 | 80.488% | 373.014 | 0.394 | 0.301 | 3 | cov 0, clean 9, cushion 0.000c | row_reconstructed_share_gt_35pct |
| repair_low_absd_recross_eighth_else_half | 66 | 66 | 54/12 | 80.488% | 360.875 | 0.394 | 0.281 | 3 | cov 0, clean 9, cushion 0.000c | row_reconstructed_share_gt_35pct |
| repair_half | 66 | 66 | 54/12 | 80.488% | 359.000 | 0.394 | 0.306 | 3 | cov 0, clean 9, cushion 0.000c | row_reconstructed_share_gt_35pct |
| repair_midcheap_quarter_else_half | 66 | 66 | 54/12 | 80.488% | 356.500 | 0.394 | 0.292 | 3 | cov 0, clean 9, cushion 0.000c | row_reconstructed_share_gt_35pct |
| repair_absd_squared | 66 | 66 | 54/12 | 80.488% | 348.158 | 0.394 | 0.322 | 3 | cov 0, clean 9, cushion 0.000c | row_reconstructed_share_gt_35pct |
| repair_absd_linear | 66 | 66 | 54/12 | 80.488% | 315.830 | 0.394 | 0.347 | 3 | cov 0, clean 9, cushion 0.000c | row_reconstructed_share_gt_35pct |
| repair_full_control | 66 | 66 | 54/12 | 80.488% | 273.000 | 0.394 | 0.394 | 2 | cov 0, clean 9, cushion 27.000c | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
