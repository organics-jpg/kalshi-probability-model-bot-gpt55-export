# v28 Feature-Gate Source-Quality Proxy Scan

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:20:25.128585+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Source-proxy watch freeze UTC: `2026-05-07T05:43:23.438198+00:00`

## Interpretation

- Source labels are audit-only; all variants select using observable row fields.
- diagnostic_feature_freeze_entry: no observable proxy clears all gates. Best filter_p_side_gte_85_rank_depth_fresh_raw has 52/82 entries, W/L 49/3, weighted net 507.5c, row recon 0.2692307692307692, blockers ['coverage_too_low'].
- diagnostic_feature_freeze_bridge: no observable proxy clears all gates. Best filter_p_side_gte_85_rank_depth_fresh_raw has 52/82 entries, W/L 49/3, weighted net 507.5c, row recon 0.2692307692307692, blockers ['coverage_too_low'].
- post_source_proxy_birth_entry: no observable proxy clears all gates. Best rank_raw_edge has 30/34 entries, W/L 24/6, weighted net 100.25c, row recon 0.43333333333333335, blockers ['row_reconstructed_share_gt_35pct', 'weighted_full_loss_cushion_lt_3'].
- post_source_proxy_birth_bridge: no observable proxy clears all gates. Best rank_raw_edge has 30/34 entries, W/L 24/6, weighted net 100.25c, row recon 0.43333333333333335, blockers ['row_reconstructed_share_gt_35pct', 'weighted_full_loss_cushion_lt_3'].

## diagnostic_feature_freeze_entry

- Freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Strict forward: `False`
- Anchor rule: `raw05_recross60_abs85_asknone`
- Repair rule: `raw03_recross50_abs50_ask35`
- Anchor/base-pool rows: `55/188`

| candidate | entries | settled | W/L | coverage | weighted net | row recon | exposure recon | cushion | source | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| filter_p_side_gte_85_rank_depth_fresh_raw | 52 | 52 | 49/3 | 63.415% | 507.500 | 0.269 | 0.237 | 5 | {'approved_entry': 38, 'rejected_actionable': 14} | coverage_too_low |
| filter_p_side_gte_85_rank_raw | 52 | 52 | 48/4 | 63.415% | 459.000 | 0.173 | 0.138 | 4 | {'approved_entry': 43, 'rejected_actionable': 9} | coverage_too_low |
| filter_p_side_gte_75_rank_raw | 61 | 61 | 50/11 | 74.390% | 391.000 | 0.344 | 0.242 | 3 | {'approved_entry': 40, 'rejected_actionable': 21} | coverage_too_low |
| filter_raw_edge_gte_4_rank_raw | 61 | 61 | 49/12 | 74.390% | 380.500 | 0.344 | 0.235 | 3 | {'approved_entry': 40, 'rejected_actionable': 21} | coverage_too_low |
| filter_raw04_fresh_rank_raw | 61 | 61 | 49/12 | 74.390% | 380.500 | 0.344 | 0.235 | 3 | {'approved_entry': 40, 'rejected_actionable': 21} | coverage_too_low |
| filter_p_side_gte_80_rank_raw | 56 | 56 | 49/7 | 68.293% | 379.500 | 0.250 | 0.186 | 3 | {'approved_entry': 42, 'rejected_actionable': 14} | coverage_too_low |
| filter_raw_edge_gte_7_rank_depth_fresh_raw | 39 | 39 | 30/9 | 47.561% | 359.750 | 0.333 | 0.197 | 3 | {'approved_entry': 26, 'rejected_actionable': 13} | coverage_too_low |
| filter_raw_edge_gte_5_rank_raw | 57 | 57 | 45/12 | 69.512% | 356.000 | 0.298 | 0.194 | 3 | {'approved_entry': 40, 'rejected_actionable': 17} | coverage_too_low |
| filter_raw_edge_gte_6_rank_raw | 41 | 41 | 31/10 | 50.000% | 329.250 | 0.341 | 0.203 | 3 | {'approved_entry': 27, 'rejected_actionable': 14} | coverage_too_low |
| filter_ask_gte_60_rank_raw | 62 | 62 | 51/11 | 75.610% | 266.750 | 0.339 | 0.232 | 2 | {'approved_entry': 41, 'rejected_actionable': 21} | weighted_full_loss_cushion_lt_3 |
| rank_raw_edge | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_none_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_book_age_lte_1000_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_book_age_lte_1500_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_book_age_lte_2000_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_btc_age_lte_1000_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_btc_age_lte_1500_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_btc_age_lte_2000_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_stc_gte_60_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_p_side_gte_65_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_p_side_gte_70_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_stc_gte_120_rank_raw | 65 | 65 | 53/12 | 79.268% | 403.750 | 0.400 | 0.264 | 4 | {'approved_entry': 39, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_btc_age_lte_250_rank_raw | 66 | 66 | 54/12 | 80.488% | 380.750 | 0.394 | 0.261 | 3 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_btc_age_lte_500_rank_raw | 66 | 66 | 54/12 | 80.488% | 380.750 | 0.394 | 0.261 | 3 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_stc_gte_180_rank_raw | 62 | 62 | 50/12 | 75.610% | 373.750 | 0.387 | 0.246 | 3 | {'approved_entry': 38, 'rejected_actionable': 24} | row_reconstructed_share_gt_35pct |
| filter_ask_gte_45_rank_raw | 66 | 66 | 53/13 | 80.488% | 309.000 | 0.409 | 0.274 | 3 | {'approved_entry': 39, 'rejected_actionable': 27} | row_reconstructed_share_gt_35pct |
| filter_raw_edge_gte_7_rank_raw | 39 | 39 | 29/10 | 47.561% | 296.250 | 0.333 | 0.184 | 2 | {'approved_entry': 26, 'rejected_actionable': 13} | coverage_too_low, weighted_full_loss_cushion_lt_3 |
| filter_ask_gte_65_rank_raw | 60 | 60 | 51/9 | 73.171% | 281.750 | 0.300 | 0.200 | 2 | {'approved_entry': 42, 'rejected_actionable': 18} | coverage_too_low, weighted_full_loss_cushion_lt_3 |
| rank_depth_fresh_raw | 66 | 66 | 56/10 | 80.488% | 527.750 | 0.485 | 0.379 | 5 | {'approved_entry': 34, 'rejected_actionable': 32} | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct |
| filter_book_age_lte_1000_rank_depth_fresh_raw | 66 | 66 | 56/10 | 80.488% | 527.750 | 0.485 | 0.379 | 5 | {'approved_entry': 34, 'rejected_actionable': 32} | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct |

## diagnostic_feature_freeze_bridge

- Freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Strict forward: `False`
- Anchor rule: `raw05_recross60_abs85_asknone`
- Repair rule: `raw03_recross50_abs50_ask35`
- Anchor/base-pool rows: `55/188`

| candidate | entries | settled | W/L | coverage | weighted net | row recon | exposure recon | cushion | source | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| filter_p_side_gte_85_rank_depth_fresh_raw | 52 | 52 | 49/3 | 63.415% | 507.500 | 0.269 | 0.237 | 5 | {'approved_entry': 38, 'rejected_actionable': 14} | coverage_too_low |
| filter_p_side_gte_85_rank_raw | 52 | 52 | 48/4 | 63.415% | 459.000 | 0.173 | 0.138 | 4 | {'approved_entry': 43, 'rejected_actionable': 9} | coverage_too_low |
| filter_p_side_gte_75_rank_raw | 61 | 61 | 50/11 | 74.390% | 391.000 | 0.344 | 0.242 | 3 | {'approved_entry': 40, 'rejected_actionable': 21} | coverage_too_low |
| filter_raw_edge_gte_4_rank_raw | 61 | 61 | 49/12 | 74.390% | 380.500 | 0.344 | 0.235 | 3 | {'approved_entry': 40, 'rejected_actionable': 21} | coverage_too_low |
| filter_raw04_fresh_rank_raw | 61 | 61 | 49/12 | 74.390% | 380.500 | 0.344 | 0.235 | 3 | {'approved_entry': 40, 'rejected_actionable': 21} | coverage_too_low |
| filter_p_side_gte_80_rank_raw | 56 | 56 | 49/7 | 68.293% | 379.500 | 0.250 | 0.186 | 3 | {'approved_entry': 42, 'rejected_actionable': 14} | coverage_too_low |
| filter_raw_edge_gte_7_rank_depth_fresh_raw | 39 | 39 | 30/9 | 47.561% | 359.750 | 0.333 | 0.197 | 3 | {'approved_entry': 26, 'rejected_actionable': 13} | coverage_too_low |
| filter_raw_edge_gte_5_rank_raw | 57 | 57 | 45/12 | 69.512% | 356.000 | 0.298 | 0.194 | 3 | {'approved_entry': 40, 'rejected_actionable': 17} | coverage_too_low |
| filter_raw_edge_gte_6_rank_raw | 41 | 41 | 31/10 | 50.000% | 329.250 | 0.341 | 0.203 | 3 | {'approved_entry': 27, 'rejected_actionable': 14} | coverage_too_low |
| filter_ask_gte_60_rank_raw | 62 | 62 | 51/11 | 75.610% | 266.750 | 0.339 | 0.232 | 2 | {'approved_entry': 41, 'rejected_actionable': 21} | weighted_full_loss_cushion_lt_3 |
| rank_raw_edge | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_none_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_book_age_lte_1000_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_book_age_lte_1500_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_book_age_lte_2000_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_btc_age_lte_1000_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_btc_age_lte_1500_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_btc_age_lte_2000_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_stc_gte_60_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_p_side_gte_65_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_p_side_gte_70_rank_raw | 66 | 66 | 54/12 | 80.488% | 408.750 | 0.394 | 0.261 | 4 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_stc_gte_120_rank_raw | 65 | 65 | 53/12 | 79.268% | 403.750 | 0.400 | 0.264 | 4 | {'approved_entry': 39, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_btc_age_lte_250_rank_raw | 66 | 66 | 54/12 | 80.488% | 380.750 | 0.394 | 0.261 | 3 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_btc_age_lte_500_rank_raw | 66 | 66 | 54/12 | 80.488% | 380.750 | 0.394 | 0.261 | 3 | {'approved_entry': 40, 'rejected_actionable': 26} | row_reconstructed_share_gt_35pct |
| filter_stc_gte_180_rank_raw | 62 | 62 | 50/12 | 75.610% | 373.750 | 0.387 | 0.246 | 3 | {'approved_entry': 38, 'rejected_actionable': 24} | row_reconstructed_share_gt_35pct |
| filter_ask_gte_45_rank_raw | 66 | 66 | 53/13 | 80.488% | 309.000 | 0.409 | 0.274 | 3 | {'approved_entry': 39, 'rejected_actionable': 27} | row_reconstructed_share_gt_35pct |
| filter_raw_edge_gte_7_rank_raw | 39 | 39 | 29/10 | 47.561% | 296.250 | 0.333 | 0.184 | 2 | {'approved_entry': 26, 'rejected_actionable': 13} | coverage_too_low, weighted_full_loss_cushion_lt_3 |
| filter_ask_gte_65_rank_raw | 60 | 60 | 51/9 | 73.171% | 281.750 | 0.300 | 0.200 | 2 | {'approved_entry': 42, 'rejected_actionable': 18} | coverage_too_low, weighted_full_loss_cushion_lt_3 |
| rank_depth_fresh_raw | 66 | 66 | 56/10 | 80.488% | 527.750 | 0.485 | 0.379 | 5 | {'approved_entry': 34, 'rejected_actionable': 32} | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct |
| filter_book_age_lte_1000_rank_depth_fresh_raw | 66 | 66 | 56/10 | 80.488% | 527.750 | 0.485 | 0.379 | 5 | {'approved_entry': 34, 'rejected_actionable': 32} | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct |

## post_source_proxy_birth_entry

- Freeze UTC: `2026-05-07T05:43:23.438198+00:00`
- Strict forward: `True`
- Anchor rule: `raw05_recross60_abs85_asknone`
- Repair rule: `raw03_recross50_abs50_ask35`
- Anchor/base-pool rows: `23/96`

| candidate | entries | settled | W/L | coverage | weighted net | row recon | exposure recon | cushion | source | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| rank_raw_edge | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_none_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_book_age_lte_1000_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_book_age_lte_1500_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_book_age_lte_2000_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_btc_age_lte_250_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_btc_age_lte_500_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_btc_age_lte_1000_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_btc_age_lte_1500_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_btc_age_lte_2000_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_stc_gte_60_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_stc_gte_120_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_p_side_gte_65_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_p_side_gte_70_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_ask_gte_45_rank_raw | 30 | 30 | 24/6 | 88.235% | 78.000 | 0.433 | 0.298 | 0 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_ask_gte_50_rank_raw | 30 | 30 | 24/6 | 88.235% | 78.000 | 0.433 | 0.298 | 0 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_ask_gte_55_rank_raw | 30 | 30 | 24/6 | 88.235% | 78.000 | 0.433 | 0.298 | 0 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_raw_edge_gte_6_rank_depth_fresh_raw | 18 | 18 | 16/2 | 52.941% | 274.000 | 0.278 | 0.180 | 2 | {'approved_entry': 13, 'rejected_actionable': 5} | settled_lt_30, coverage_too_low, weighted_full_loss_cushion_lt_3 |
| filter_p_side_gte_85_rank_depth_fresh_raw | 25 | 25 | 24/1 | 73.529% | 259.000 | 0.320 | 0.273 | 2 | {'rejected_actionable': 8, 'approved_entry': 17} | settled_lt_30, coverage_too_low, weighted_full_loss_cushion_lt_3 |
| filter_p_side_gte_85_rank_raw | 25 | 25 | 23/2 | 73.529% | 189.000 | 0.280 | 0.222 | 1 | {'rejected_actionable': 7, 'approved_entry': 18} | settled_lt_30, coverage_too_low, weighted_full_loss_cushion_lt_3 |
| filter_raw_edge_gte_7_rank_depth_fresh_raw | 17 | 17 | 14/3 | 50.000% | 175.500 | 0.294 | 0.186 | 1 | {'approved_entry': 12, 'rejected_actionable': 5} | settled_lt_30, coverage_too_low, weighted_full_loss_cushion_lt_3 |
| filter_raw_edge_gte_6_rank_raw | 18 | 18 | 14/4 | 52.941% | 125.000 | 0.278 | 0.148 | 1 | {'approved_entry': 13, 'rejected_actionable': 5} | settled_lt_30, coverage_too_low, weighted_full_loss_cushion_lt_3 |
| filter_raw_edge_gte_7_rank_raw | 17 | 17 | 13/4 | 50.000% | 112.000 | 0.294 | 0.158 | 1 | {'approved_entry': 12, 'rejected_actionable': 5} | settled_lt_30, coverage_too_low, weighted_full_loss_cushion_lt_3 |
| filter_book_age_lte_500_rank_raw | 23 | 23 | 19/4 | 67.647% | 96.500 | 0.348 | 0.266 | 0 | {'approved_entry': 15, 'rejected_actionable': 8} | settled_lt_30, coverage_too_low, weighted_full_loss_cushion_lt_3 |
| filter_raw_edge_gte_5_rank_raw | 24 | 24 | 18/6 | 70.588% | 63.250 | 0.292 | 0.175 | 0 | {'approved_entry': 17, 'rejected_actionable': 7} | settled_lt_30, coverage_too_low, weighted_full_loss_cushion_lt_3 |
| rank_depth_fresh_raw | 30 | 30 | 26/4 | 88.235% | 240.750 | 0.500 | 0.398 | 2 | {'rejected_actionable': 15, 'approved_entry': 15} | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_book_age_lte_1000_rank_depth_fresh_raw | 30 | 30 | 26/4 | 88.235% | 240.750 | 0.500 | 0.398 | 2 | {'rejected_actionable': 15, 'approved_entry': 15} | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_book_age_lte_1500_rank_depth_fresh_raw | 30 | 30 | 26/4 | 88.235% | 240.750 | 0.500 | 0.398 | 2 | {'rejected_actionable': 15, 'approved_entry': 15} | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_book_age_lte_2000_rank_depth_fresh_raw | 30 | 30 | 26/4 | 88.235% | 240.750 | 0.500 | 0.398 | 2 | {'rejected_actionable': 15, 'approved_entry': 15} | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_btc_age_lte_250_rank_depth_fresh_raw | 30 | 30 | 26/4 | 88.235% | 240.750 | 0.500 | 0.398 | 2 | {'rejected_actionable': 15, 'approved_entry': 15} | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |

## post_source_proxy_birth_bridge

- Freeze UTC: `2026-05-07T05:43:23.438198+00:00`
- Strict forward: `True`
- Anchor rule: `raw05_recross60_abs85_asknone`
- Repair rule: `raw03_recross50_abs50_ask35`
- Anchor/base-pool rows: `23/96`

| candidate | entries | settled | W/L | coverage | weighted net | row recon | exposure recon | cushion | source | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| rank_raw_edge | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_none_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_book_age_lte_1000_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_book_age_lte_1500_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_book_age_lte_2000_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_btc_age_lte_250_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_btc_age_lte_500_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_btc_age_lte_1000_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_btc_age_lte_1500_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_btc_age_lte_2000_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_stc_gte_60_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_stc_gte_120_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_p_side_gte_65_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_p_side_gte_70_rank_raw | 30 | 30 | 24/6 | 88.235% | 100.250 | 0.433 | 0.290 | 1 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_ask_gte_45_rank_raw | 30 | 30 | 24/6 | 88.235% | 78.000 | 0.433 | 0.298 | 0 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_ask_gte_50_rank_raw | 30 | 30 | 24/6 | 88.235% | 78.000 | 0.433 | 0.298 | 0 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_ask_gte_55_rank_raw | 30 | 30 | 24/6 | 88.235% | 78.000 | 0.433 | 0.298 | 0 | {'rejected_actionable': 13, 'approved_entry': 17} | row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_raw_edge_gte_6_rank_depth_fresh_raw | 18 | 18 | 16/2 | 52.941% | 274.000 | 0.278 | 0.180 | 2 | {'approved_entry': 13, 'rejected_actionable': 5} | settled_lt_30, coverage_too_low, weighted_full_loss_cushion_lt_3 |
| filter_p_side_gte_85_rank_depth_fresh_raw | 25 | 25 | 24/1 | 73.529% | 259.000 | 0.320 | 0.273 | 2 | {'rejected_actionable': 8, 'approved_entry': 17} | settled_lt_30, coverage_too_low, weighted_full_loss_cushion_lt_3 |
| filter_p_side_gte_85_rank_raw | 25 | 25 | 23/2 | 73.529% | 189.000 | 0.280 | 0.222 | 1 | {'rejected_actionable': 7, 'approved_entry': 18} | settled_lt_30, coverage_too_low, weighted_full_loss_cushion_lt_3 |
| filter_raw_edge_gte_7_rank_depth_fresh_raw | 17 | 17 | 14/3 | 50.000% | 175.500 | 0.294 | 0.186 | 1 | {'approved_entry': 12, 'rejected_actionable': 5} | settled_lt_30, coverage_too_low, weighted_full_loss_cushion_lt_3 |
| filter_raw_edge_gte_6_rank_raw | 18 | 18 | 14/4 | 52.941% | 125.000 | 0.278 | 0.148 | 1 | {'approved_entry': 13, 'rejected_actionable': 5} | settled_lt_30, coverage_too_low, weighted_full_loss_cushion_lt_3 |
| filter_raw_edge_gte_7_rank_raw | 17 | 17 | 13/4 | 50.000% | 112.000 | 0.294 | 0.158 | 1 | {'approved_entry': 12, 'rejected_actionable': 5} | settled_lt_30, coverage_too_low, weighted_full_loss_cushion_lt_3 |
| filter_book_age_lte_500_rank_raw | 23 | 23 | 19/4 | 67.647% | 96.500 | 0.348 | 0.266 | 0 | {'approved_entry': 15, 'rejected_actionable': 8} | settled_lt_30, coverage_too_low, weighted_full_loss_cushion_lt_3 |
| filter_raw_edge_gte_5_rank_raw | 24 | 24 | 18/6 | 70.588% | 63.250 | 0.292 | 0.175 | 0 | {'approved_entry': 17, 'rejected_actionable': 7} | settled_lt_30, coverage_too_low, weighted_full_loss_cushion_lt_3 |
| rank_depth_fresh_raw | 30 | 30 | 26/4 | 88.235% | 240.750 | 0.500 | 0.398 | 2 | {'rejected_actionable': 15, 'approved_entry': 15} | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_book_age_lte_1000_rank_depth_fresh_raw | 30 | 30 | 26/4 | 88.235% | 240.750 | 0.500 | 0.398 | 2 | {'rejected_actionable': 15, 'approved_entry': 15} | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_book_age_lte_1500_rank_depth_fresh_raw | 30 | 30 | 26/4 | 88.235% | 240.750 | 0.500 | 0.398 | 2 | {'rejected_actionable': 15, 'approved_entry': 15} | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_book_age_lte_2000_rank_depth_fresh_raw | 30 | 30 | 26/4 | 88.235% | 240.750 | 0.500 | 0.398 | 2 | {'rejected_actionable': 15, 'approved_entry': 15} | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| filter_btc_age_lte_250_rank_depth_fresh_raw | 30 | 30 | 26/4 | 88.235% | 240.750 | 0.500 | 0.398 | 2 | {'rejected_actionable': 15, 'approved_entry': 15} | row_reconstructed_share_gt_35pct, exposure_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
