# v28 Feature-Gate Observable Selection-Mix Audit

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:06:12.339774+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- Selection variants use observable features only; source labels are audited after selection.
- post_feature_freeze_entry: no variant clears all gates. Best anchor_plus_min_coverage_repairs_low_recross_then_raw has 62/82 entries, W/L 43/19, weighted net 421.25c, row recon 0.3548387096774194, blockers ['row_reconstructed_share_gt_35pct'].
- post_feature_freeze_bridge: no variant clears all gates. Best anchor_plus_min_coverage_repairs_low_recross_then_raw has 62/82 entries, W/L 43/19, weighted net 421.25c, row recon 0.3548387096774194, blockers ['row_reconstructed_share_gt_35pct'].

## post_feature_freeze_entry

- Anchor rule: `raw05_recross60_abs85_asknone`
- Repair rule: `raw03_recross50_abs50_ask35`
- Size policy: `repair_low_absd_quarter_else_half`
- Anchor/control entries: `55/66`
- Coverage entry targets: `{'min75': 62, 'mid80': 66, 'max90': 73}`

| candidate | entries | settled | W/L | coverage | weighted net | row recon | exposure recon | cushion | changes | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| anchor_plus_min_coverage_repairs_low_recross_then_raw | 62 | 62 | 43/19 | 75.610% | 421.250 | 0.355 | 0.304 | 4 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_min_coverage_repairs_absd_then_raw | 62 | 62 | 44/18 | 75.610% | 420.000 | 0.355 | 0.310 | 4 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_min_coverage_repairs_pside_absd_recross | 62 | 62 | 44/18 | 75.610% | 420.000 | 0.355 | 0.310 | 4 | 10 | row_reconstructed_share_gt_35pct |
| same_market_repair_rule_raw_edge | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | 0 | row_reconstructed_share_gt_35pct |
| anchor_plus_min_coverage_repairs_raw_edge | 62 | 62 | 41/21 | 75.610% | 403.250 | 0.355 | 0.295 | 4 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_min_coverage_repairs_edge_absd_recross | 62 | 62 | 41/21 | 75.610% | 403.250 | 0.355 | 0.295 | 4 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_min_coverage_repairs_edge_absd_cheap_penalty | 62 | 62 | 41/21 | 75.610% | 403.250 | 0.355 | 0.295 | 4 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_80pct_repairs_edge_absd_recross | 66 | 66 | 44/22 | 80.488% | 398.750 | 0.394 | 0.313 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_80pct_repairs_edge_absd_cheap_penalty | 66 | 66 | 44/22 | 80.488% | 398.750 | 0.394 | 0.313 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_max90_repairs_raw_edge | 69 | 69 | 46/23 | 84.146% | 392.500 | 0.420 | 0.328 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_max90_repairs_edge_absd_recross | 69 | 69 | 46/23 | 84.146% | 392.000 | 0.420 | 0.328 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_max90_repairs_edge_absd_cheap_penalty | 69 | 69 | 46/23 | 84.146% | 392.000 | 0.420 | 0.328 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_max90_repairs_low_recross_then_raw | 69 | 69 | 46/23 | 84.146% | 391.500 | 0.420 | 0.328 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_80pct_repairs_absd_then_raw | 66 | 66 | 45/21 | 80.488% | 390.500 | 0.394 | 0.322 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_80pct_repairs_pside_absd_recross | 66 | 66 | 45/21 | 80.488% | 390.500 | 0.394 | 0.322 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_80pct_repairs_low_recross_then_raw | 66 | 66 | 44/22 | 80.488% | 385.000 | 0.394 | 0.319 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_80pct_repairs_raw_edge | 66 | 66 | 43/23 | 80.488% | 378.500 | 0.394 | 0.310 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_max90_repairs_absd_then_raw | 69 | 69 | 46/23 | 84.146% | 369.750 | 0.420 | 0.331 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_max90_repairs_pside_absd_recross | 69 | 69 | 46/23 | 84.146% | 369.750 | 0.420 | 0.331 | 3 | 10 | row_reconstructed_share_gt_35pct |
| same_market_repair_rule_edge_absd_cheap_penalty | 66 | 66 | 55/11 | 80.488% | 403.750 | 0.500 | 0.403 | 4 | 1 | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct |
| same_market_repair_rule_edge_absd_recross | 66 | 66 | 55/11 | 80.488% | 401.750 | 0.500 | 0.403 | 4 | 1 | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct |
| same_market_repair_rule_low_recross_then_raw | 66 | 66 | 55/11 | 80.488% | 229.250 | 0.530 | 0.453 | 2 | 3 | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| same_market_repair_rule_absd_then_raw | 66 | 66 | 55/11 | 80.488% | 178.500 | 0.515 | 0.426 | 1 | 3 | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| same_market_repair_rule_pside_absd_recross | 66 | 66 | 55/11 | 80.488% | 178.500 | 0.515 | 0.426 | 1 | 3 | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |

## post_feature_freeze_bridge

- Anchor rule: `raw05_recross60_abs85_asknone`
- Repair rule: `raw03_recross50_abs50_ask35`
- Size policy: `repair_low_absd_quarter_else_half`
- Anchor/control entries: `55/66`
- Coverage entry targets: `{'min75': 62, 'mid80': 66, 'max90': 73}`

| candidate | entries | settled | W/L | coverage | weighted net | row recon | exposure recon | cushion | changes | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| anchor_plus_min_coverage_repairs_low_recross_then_raw | 62 | 62 | 43/19 | 75.610% | 421.250 | 0.355 | 0.304 | 4 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_min_coverage_repairs_absd_then_raw | 62 | 62 | 44/18 | 75.610% | 420.000 | 0.355 | 0.310 | 4 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_min_coverage_repairs_pside_absd_recross | 62 | 62 | 44/18 | 75.610% | 420.000 | 0.355 | 0.310 | 4 | 10 | row_reconstructed_share_gt_35pct |
| same_market_repair_rule_raw_edge | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | 0 | row_reconstructed_share_gt_35pct |
| anchor_plus_min_coverage_repairs_raw_edge | 62 | 62 | 41/21 | 75.610% | 403.250 | 0.355 | 0.295 | 4 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_min_coverage_repairs_edge_absd_recross | 62 | 62 | 41/21 | 75.610% | 403.250 | 0.355 | 0.295 | 4 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_min_coverage_repairs_edge_absd_cheap_penalty | 62 | 62 | 41/21 | 75.610% | 403.250 | 0.355 | 0.295 | 4 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_80pct_repairs_edge_absd_recross | 66 | 66 | 44/22 | 80.488% | 398.750 | 0.394 | 0.313 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_80pct_repairs_edge_absd_cheap_penalty | 66 | 66 | 44/22 | 80.488% | 398.750 | 0.394 | 0.313 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_max90_repairs_raw_edge | 69 | 69 | 46/23 | 84.146% | 392.500 | 0.420 | 0.328 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_max90_repairs_edge_absd_recross | 69 | 69 | 46/23 | 84.146% | 392.000 | 0.420 | 0.328 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_max90_repairs_edge_absd_cheap_penalty | 69 | 69 | 46/23 | 84.146% | 392.000 | 0.420 | 0.328 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_max90_repairs_low_recross_then_raw | 69 | 69 | 46/23 | 84.146% | 391.500 | 0.420 | 0.328 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_80pct_repairs_absd_then_raw | 66 | 66 | 45/21 | 80.488% | 390.500 | 0.394 | 0.322 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_80pct_repairs_pside_absd_recross | 66 | 66 | 45/21 | 80.488% | 390.500 | 0.394 | 0.322 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_80pct_repairs_low_recross_then_raw | 66 | 66 | 44/22 | 80.488% | 385.000 | 0.394 | 0.319 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_80pct_repairs_raw_edge | 66 | 66 | 43/23 | 80.488% | 378.500 | 0.394 | 0.310 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_max90_repairs_absd_then_raw | 69 | 69 | 46/23 | 84.146% | 369.750 | 0.420 | 0.331 | 3 | 10 | row_reconstructed_share_gt_35pct |
| anchor_plus_max90_repairs_pside_absd_recross | 69 | 69 | 46/23 | 84.146% | 369.750 | 0.420 | 0.331 | 3 | 10 | row_reconstructed_share_gt_35pct |
| same_market_repair_rule_edge_absd_cheap_penalty | 66 | 66 | 55/11 | 80.488% | 403.750 | 0.500 | 0.403 | 4 | 1 | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct |
| same_market_repair_rule_edge_absd_recross | 66 | 66 | 55/11 | 80.488% | 401.750 | 0.500 | 0.403 | 4 | 1 | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct |
| same_market_repair_rule_low_recross_then_raw | 66 | 66 | 55/11 | 80.488% | 229.250 | 0.530 | 0.453 | 2 | 3 | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| same_market_repair_rule_absd_then_raw | 66 | 66 | 55/11 | 80.488% | 178.500 | 0.515 | 0.426 | 1 | 3 | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| same_market_repair_rule_pside_absd_recross | 66 | 66 | 55/11 | 80.488% | 178.500 | 0.515 | 0.426 | 1 | 3 | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
