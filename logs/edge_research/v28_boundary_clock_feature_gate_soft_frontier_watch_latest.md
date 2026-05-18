# v28 Boundary-Clock Feature-Gate Soft Frontier Watch

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:37:21.652885+00:00`
- Soft-frontier freeze UTC: `2026-05-06T20:01:04.705640+00:00`

## Interpretation

- Soft-frontier rules are observable-only and exclude cheap-tail very-near-strike failures by ask/distance floors.
- Only post_soft_frontier_birth lanes are strict forward evidence for this watch.
- diagnostic_entry: best diagnostic_entry_soft_raw03_recross50_abs65_ask35 settled 91, coverage 75.20661157024793%, net 692.0c, recon 0.2967032967032967, tags {'clean_or_unclassified': 58, 'source_quality_risk': 27, 'realized_loss': 11, 'thin_or_negative_net': 14, 'thin_raw_edge': 11, 'mid_cheap_touch': 3}, blockers [].
- diagnostic_bridge: best diagnostic_bridge_soft_raw03_recross50_abs65_ask35 settled 89, coverage 74.78991596638656%, net 642.0c, recon 0.29213483146067415, tags {'source_quality_risk': 26, 'clean_or_unclassified': 57, 'realized_loss': 11, 'thin_or_negative_net': 14, 'thin_raw_edge': 11, 'mid_cheap_touch': 3}, blockers ['coverage_too_low'].
- pre_soft_frontier_birth_entry: best pre_soft_frontier_birth_entry_soft_raw03_recross50_abs65_ask35 settled 59, coverage 71.95121951219512%, net 285.0c, recon 0.288135593220339, tags {'clean_or_unclassified': 37, 'source_quality_risk': 17, 'realized_loss': 9, 'thin_or_negative_net': 10, 'mid_cheap_touch': 3, 'thin_raw_edge': 6}, blockers ['coverage_too_low', 'full_loss_cushion_lt_3'].
- pre_soft_frontier_birth_bridge: best pre_soft_frontier_birth_bridge_soft_raw03_recross50_abs65_ask35 settled 59, coverage 71.95121951219512%, net 285.0c, recon 0.288135593220339, tags {'clean_or_unclassified': 37, 'source_quality_risk': 17, 'realized_loss': 9, 'thin_or_negative_net': 10, 'mid_cheap_touch': 3, 'thin_raw_edge': 6}, blockers ['coverage_too_low', 'full_loss_cushion_lt_3'].
- post_soft_frontier_birth_entry: best post_soft_frontier_birth_entry_soft_raw03_recross50_abs65_ask35 settled 54, coverage 75.0%, net 233.0c, recon 0.3148148148148148, tags {'source_quality_risk': 17, 'clean_or_unclassified': 32, 'realized_loss': 9, 'thin_or_negative_net': 10, 'mid_cheap_touch': 3, 'thin_raw_edge': 6}, blockers ['full_loss_cushion_lt_3'].
- post_soft_frontier_birth_bridge: best post_soft_frontier_birth_bridge_soft_raw03_recross50_abs65_ask35 settled 54, coverage 75.0%, net 233.0c, recon 0.3148148148148148, tags {'source_quality_risk': 17, 'clean_or_unclassified': 32, 'realized_loss': 9, 'thin_or_negative_net': 10, 'mid_cheap_touch': 3, 'thin_raw_edge': 6}, blockers ['full_loss_cushion_lt_3'].

## diagnostic_entry

| rank | candidate | settled/den | W/L | coverage | net c | recon | cushion | tags | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | diagnostic_entry_soft_raw03_recross50_abs65_ask35 | 91/121 | 80/11 | 75.206612 | 692.000000 | 0.296703 | 6 | {'clean_or_unclassified': 58, 'source_quality_risk': 27, 'realized_loss': 11, 'thin_or_negative_net': 14, 'thin_raw_edge': 11, 'mid_cheap_touch': 3} | none |
| 2 | diagnostic_entry_soft_raw03_recross50_abs50_ask35 | 98/121 | 84/14 | 80.991736 | 680.000000 | 0.367347 | 6 | {'clean_or_unclassified': 57, 'source_quality_risk': 36, 'realized_loss': 14, 'thin_or_negative_net': 17, 'thin_raw_edge': 14, 'near_strike_boundary_pull': 10, 'mid_cheap_touch': 5} | reconstructed_share_gt_35pct |
| 3 | diagnostic_entry_soft_raw03_recross50_abs50_ask50 | 96/121 | 81/15 | 79.338843 | 418.000000 | 0.364583 | 4 | {'clean_or_unclassified': 57, 'source_quality_risk': 35, 'realized_loss': 15, 'thin_or_negative_net': 18, 'thin_raw_edge': 14, 'near_strike_boundary_pull': 9} | reconstructed_share_gt_35pct |

## diagnostic_bridge

| rank | candidate | settled/den | W/L | coverage | net c | recon | cushion | tags | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | diagnostic_bridge_soft_raw03_recross50_abs65_ask35 | 89/119 | 78/11 | 74.789916 | 642.000000 | 0.292135 | 6 | {'source_quality_risk': 26, 'clean_or_unclassified': 57, 'realized_loss': 11, 'thin_or_negative_net': 14, 'thin_raw_edge': 11, 'mid_cheap_touch': 3} | coverage_too_low |
| 2 | diagnostic_bridge_soft_raw03_recross50_abs50_ask35 | 96/119 | 82/14 | 80.672269 | 630.000000 | 0.364583 | 6 | {'source_quality_risk': 35, 'clean_or_unclassified': 56, 'realized_loss': 14, 'thin_or_negative_net': 17, 'thin_raw_edge': 14, 'near_strike_boundary_pull': 10, 'mid_cheap_touch': 5} | reconstructed_share_gt_35pct |
| 3 | diagnostic_bridge_soft_raw03_recross50_abs50_ask50 | 94/119 | 79/15 | 78.991597 | 368.000000 | 0.361702 | 3 | {'source_quality_risk': 34, 'clean_or_unclassified': 56, 'realized_loss': 15, 'thin_or_negative_net': 18, 'thin_raw_edge': 14, 'near_strike_boundary_pull': 9} | reconstructed_share_gt_35pct |

## pre_soft_frontier_birth_entry

| rank | candidate | settled/den | W/L | coverage | net c | recon | cushion | tags | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | pre_soft_frontier_birth_entry_soft_raw03_recross50_abs65_ask35 | 59/82 | 50/9 | 71.951220 | 285.000000 | 0.288136 | 2 | {'clean_or_unclassified': 37, 'source_quality_risk': 17, 'realized_loss': 9, 'thin_or_negative_net': 10, 'mid_cheap_touch': 3, 'thin_raw_edge': 6} | coverage_too_low, full_loss_cushion_lt_3 |
| 2 | pre_soft_frontier_birth_entry_soft_raw03_recross50_abs50_ask35 | 66/82 | 54/12 | 80.487805 | 273.000000 | 0.393939 | 2 | {'clean_or_unclassified': 36, 'source_quality_risk': 26, 'thin_raw_edge': 9, 'near_strike_boundary_pull': 10, 'realized_loss': 12, 'thin_or_negative_net': 13, 'mid_cheap_touch': 5} | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 3 | pre_soft_frontier_birth_entry_soft_raw03_recross50_abs50_ask50 | 64/82 | 51/13 | 78.048780 | 11.000000 | 0.390625 | 0 | {'clean_or_unclassified': 36, 'source_quality_risk': 25, 'thin_raw_edge': 9, 'near_strike_boundary_pull': 9, 'realized_loss': 13, 'thin_or_negative_net': 14} | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

## pre_soft_frontier_birth_bridge

| rank | candidate | settled/den | W/L | coverage | net c | recon | cushion | tags | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | pre_soft_frontier_birth_bridge_soft_raw03_recross50_abs65_ask35 | 59/82 | 50/9 | 71.951220 | 285.000000 | 0.288136 | 2 | {'clean_or_unclassified': 37, 'source_quality_risk': 17, 'realized_loss': 9, 'thin_or_negative_net': 10, 'mid_cheap_touch': 3, 'thin_raw_edge': 6} | coverage_too_low, full_loss_cushion_lt_3 |
| 2 | pre_soft_frontier_birth_bridge_soft_raw03_recross50_abs50_ask35 | 66/82 | 54/12 | 80.487805 | 273.000000 | 0.393939 | 2 | {'clean_or_unclassified': 36, 'source_quality_risk': 26, 'thin_raw_edge': 9, 'near_strike_boundary_pull': 10, 'realized_loss': 12, 'thin_or_negative_net': 13, 'mid_cheap_touch': 5} | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 3 | pre_soft_frontier_birth_bridge_soft_raw03_recross50_abs50_ask50 | 64/82 | 51/13 | 78.048780 | 11.000000 | 0.390625 | 0 | {'clean_or_unclassified': 36, 'source_quality_risk': 25, 'thin_raw_edge': 9, 'near_strike_boundary_pull': 9, 'realized_loss': 13, 'thin_or_negative_net': 14} | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

## post_soft_frontier_birth_entry

| rank | candidate | settled/den | W/L | coverage | net c | recon | cushion | tags | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | post_soft_frontier_birth_entry_soft_raw03_recross50_abs65_ask35 | 54/72 | 45/9 | 75.000000 | 233.000000 | 0.314815 | 2 | {'source_quality_risk': 17, 'clean_or_unclassified': 32, 'realized_loss': 9, 'thin_or_negative_net': 10, 'mid_cheap_touch': 3, 'thin_raw_edge': 6} | full_loss_cushion_lt_3 |
| 2 | post_soft_frontier_birth_entry_soft_raw03_recross50_abs50_ask35 | 59/72 | 47/12 | 81.944444 | 166.000000 | 0.406780 | 1 | {'source_quality_risk': 24, 'clean_or_unclassified': 31, 'realized_loss': 12, 'thin_or_negative_net': 13, 'mid_cheap_touch': 5, 'near_strike_boundary_pull': 8, 'thin_raw_edge': 7} | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 3 | post_soft_frontier_birth_entry_soft_raw03_recross50_abs50_ask50 | 57/72 | 44/13 | 79.166667 | -96.000000 | 0.403509 | 0 | {'source_quality_risk': 23, 'clean_or_unclassified': 31, 'realized_loss': 13, 'thin_or_negative_net': 14, 'near_strike_boundary_pull': 7, 'thin_raw_edge': 7} | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

## post_soft_frontier_birth_bridge

| rank | candidate | settled/den | W/L | coverage | net c | recon | cushion | tags | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | post_soft_frontier_birth_bridge_soft_raw03_recross50_abs65_ask35 | 54/72 | 45/9 | 75.000000 | 233.000000 | 0.314815 | 2 | {'source_quality_risk': 17, 'clean_or_unclassified': 32, 'realized_loss': 9, 'thin_or_negative_net': 10, 'mid_cheap_touch': 3, 'thin_raw_edge': 6} | full_loss_cushion_lt_3 |
| 2 | post_soft_frontier_birth_bridge_soft_raw03_recross50_abs50_ask35 | 59/72 | 47/12 | 81.944444 | 166.000000 | 0.406780 | 1 | {'source_quality_risk': 24, 'clean_or_unclassified': 31, 'realized_loss': 12, 'thin_or_negative_net': 13, 'mid_cheap_touch': 5, 'near_strike_boundary_pull': 8, 'thin_raw_edge': 7} | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 3 | post_soft_frontier_birth_bridge_soft_raw03_recross50_abs50_ask50 | 57/72 | 44/13 | 79.166667 | -96.000000 | 0.403509 | 0 | {'source_quality_risk': 23, 'clean_or_unclassified': 31, 'realized_loss': 13, 'thin_or_negative_net': 14, 'near_strike_boundary_pull': 7, 'thin_raw_edge': 7} | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
