# v28 Feature-Gate Source-Proxy Coverage Repair

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:23:19.342946+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Source-proxy freeze UTC: `2026-05-07T05:43:23.438198+00:00`

## Interpretation

- The core and filler rankings use observable fields only; source labels are audit-only.
- diagnostic_feature_freeze_entry: no variant clears all gates. Best stc240_core_plus_p_side_fillers has 62/82 entries, W/L 51/11, weighted net 380.5c, row recon 0.4032258064516129, blockers ['row_reconstructed_share_gt_35pct'].
- diagnostic_feature_freeze_bridge: no variant clears all gates. Best stc240_core_plus_p_side_fillers has 62/82 entries, W/L 51/11, weighted net 380.5c, row recon 0.4032258064516129, blockers ['row_reconstructed_share_gt_35pct'].
- post_source_proxy_birth_entry: no variant clears all gates. Best stc240_core_plus_raw_edge_fillers has 28/34 entries, W/L 22/6, weighted net 60.0c, row recon 0.4642857142857143, blockers ['settled_lt_30', 'row_reconstructed_share_gt_35pct', 'weighted_full_loss_cushion_lt_3'].
- post_source_proxy_birth_bridge: no variant clears all gates. Best stc240_core_plus_raw_edge_fillers has 28/34 entries, W/L 22/6, weighted net 60.0c, row recon 0.4642857142857143, blockers ['settled_lt_30', 'row_reconstructed_share_gt_35pct', 'weighted_full_loss_cushion_lt_3'].

## diagnostic_feature_freeze_entry

- Freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Strict forward: `False`
- Core/required entries: `59/62`

| candidate | entries | settled | W/L | coverage | weighted net | row recon | exposure recon | cushion | filler source | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| stc240_core_plus_p_side_fillers | 62 | 62 | 51/11 | 75.610% | 380.500 | 0.403 | 0.282 | 3 | {'rejected_actionable': 2, 'approved_entry': 1} | row_reconstructed_share_gt_35pct |
| stc240_core_plus_absd_fillers | 62 | 62 | 51/11 | 75.610% | 380.500 | 0.403 | 0.282 | 3 | {'rejected_actionable': 2, 'approved_entry': 1} | row_reconstructed_share_gt_35pct |
| stc240_core_plus_source_proxy_score_fillers | 62 | 62 | 51/11 | 75.610% | 380.000 | 0.403 | 0.282 | 3 | {'rejected_actionable': 2, 'approved_entry': 1} | row_reconstructed_share_gt_35pct |
| stc240_core_plus_raw_edge_fillers | 62 | 62 | 50/12 | 75.610% | 375.500 | 0.387 | 0.258 | 3 | {'rejected_actionable': 1, 'approved_entry': 2} | row_reconstructed_share_gt_35pct |
| stc240_core_plus_low_recross_fillers | 62 | 62 | 51/11 | 75.610% | 375.000 | 0.403 | 0.285 | 3 | {'rejected_actionable': 2, 'approved_entry': 1} | row_reconstructed_share_gt_35pct |
| stc240_core_plus_ask_fillers | 62 | 62 | 51/11 | 75.610% | 374.000 | 0.419 | 0.295 | 3 | {'rejected_actionable': 3} | row_reconstructed_share_gt_35pct |

## diagnostic_feature_freeze_bridge

- Freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Strict forward: `False`
- Core/required entries: `59/62`

| candidate | entries | settled | W/L | coverage | weighted net | row recon | exposure recon | cushion | filler source | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| stc240_core_plus_p_side_fillers | 62 | 62 | 51/11 | 75.610% | 380.500 | 0.403 | 0.282 | 3 | {'rejected_actionable': 2, 'approved_entry': 1} | row_reconstructed_share_gt_35pct |
| stc240_core_plus_absd_fillers | 62 | 62 | 51/11 | 75.610% | 380.500 | 0.403 | 0.282 | 3 | {'rejected_actionable': 2, 'approved_entry': 1} | row_reconstructed_share_gt_35pct |
| stc240_core_plus_source_proxy_score_fillers | 62 | 62 | 51/11 | 75.610% | 380.000 | 0.403 | 0.282 | 3 | {'rejected_actionable': 2, 'approved_entry': 1} | row_reconstructed_share_gt_35pct |
| stc240_core_plus_raw_edge_fillers | 62 | 62 | 50/12 | 75.610% | 375.500 | 0.387 | 0.258 | 3 | {'rejected_actionable': 1, 'approved_entry': 2} | row_reconstructed_share_gt_35pct |
| stc240_core_plus_low_recross_fillers | 62 | 62 | 51/11 | 75.610% | 375.000 | 0.403 | 0.285 | 3 | {'rejected_actionable': 2, 'approved_entry': 1} | row_reconstructed_share_gt_35pct |
| stc240_core_plus_ask_fillers | 62 | 62 | 51/11 | 75.610% | 374.000 | 0.419 | 0.295 | 3 | {'rejected_actionable': 3} | row_reconstructed_share_gt_35pct |

## post_source_proxy_birth_entry

- Freeze UTC: `2026-05-07T05:43:23.438198+00:00`
- Strict forward: `True`
- Core/required entries: `28/26`

| candidate | entries | settled | W/L | coverage | weighted net | row recon | exposure recon | cushion | filler source | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| stc240_core_plus_raw_edge_fillers | 28 | 28 | 22/6 | 82.353% | 60.000 | 0.464 | 0.341 | 0 | {} | settled_lt_30, row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| stc240_core_plus_p_side_fillers | 28 | 28 | 22/6 | 82.353% | 60.000 | 0.464 | 0.341 | 0 | {} | settled_lt_30, row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| stc240_core_plus_ask_fillers | 28 | 28 | 22/6 | 82.353% | 60.000 | 0.464 | 0.341 | 0 | {} | settled_lt_30, row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| stc240_core_plus_absd_fillers | 28 | 28 | 22/6 | 82.353% | 60.000 | 0.464 | 0.341 | 0 | {} | settled_lt_30, row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| stc240_core_plus_low_recross_fillers | 28 | 28 | 22/6 | 82.353% | 60.000 | 0.464 | 0.341 | 0 | {} | settled_lt_30, row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| stc240_core_plus_source_proxy_score_fillers | 28 | 28 | 22/6 | 82.353% | 60.000 | 0.464 | 0.341 | 0 | {} | settled_lt_30, row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |

## post_source_proxy_birth_bridge

- Freeze UTC: `2026-05-07T05:43:23.438198+00:00`
- Strict forward: `True`
- Core/required entries: `28/26`

| candidate | entries | settled | W/L | coverage | weighted net | row recon | exposure recon | cushion | filler source | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| stc240_core_plus_raw_edge_fillers | 28 | 28 | 22/6 | 82.353% | 60.000 | 0.464 | 0.341 | 0 | {} | settled_lt_30, row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| stc240_core_plus_p_side_fillers | 28 | 28 | 22/6 | 82.353% | 60.000 | 0.464 | 0.341 | 0 | {} | settled_lt_30, row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| stc240_core_plus_ask_fillers | 28 | 28 | 22/6 | 82.353% | 60.000 | 0.464 | 0.341 | 0 | {} | settled_lt_30, row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| stc240_core_plus_absd_fillers | 28 | 28 | 22/6 | 82.353% | 60.000 | 0.464 | 0.341 | 0 | {} | settled_lt_30, row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| stc240_core_plus_low_recross_fillers | 28 | 28 | 22/6 | 82.353% | 60.000 | 0.464 | 0.341 | 0 | {} | settled_lt_30, row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
| stc240_core_plus_source_proxy_score_fillers | 28 | 28 | 22/6 | 82.353% | 60.000 | 0.464 | 0.341 | 0 | {} | settled_lt_30, row_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3 |
