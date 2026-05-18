# v28 High-Win Core Broad-Fill Mix

Research-only diagnostic. No live bot changes or orders.

- Generated UTC: `2026-05-11T03:08:02.285843+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Source-proxy freeze UTC: `2026-05-07T05:43:23.438198+00:00`

## Interpretation

- This is diagnostic mix/match only because the high-win cores are pre source-proxy-freeze rows.
- The test asks whether high-win p_side/source-quality cores can be filled back to 75% coverage from broad raw03 rows using observable rankings.
- Best mix post_feature_freeze_bridge_filter_p_side_gte_85_rank_raw_fill_ask_confirm has 62 settled, W/L 49/13, coverage 75.60975609756098%, net 574.0c, recon 0.3064516129032258, blockers ['diagnostic_only_prefreeze'].

## Top Mix Rows

| rank | lane | core | fill | settled | W/L | coverage | net | recon | cushion | filler added | filler net | blockers |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `post_feature_freeze_bridge` | `filter_p_side_gte_85_rank_raw` | `ask_confirm` | 62 | 49/13 | 75.61% | 574c | 30.65% | 5 | 10 | 64c | diagnostic_only_prefreeze |
| 2 | `post_feature_freeze_entry` | `filter_p_side_gte_85_rank_raw` | `ask_confirm` | 62 | 49/13 | 75.61% | 574c | 30.65% | 5 | 10 | 64c | diagnostic_only_prefreeze |
| 3 | `post_feature_freeze_bridge` | `filter_p_side_gte_85_rank_raw` | `absd` | 62 | 49/13 | 75.61% | 568c | 30.65% | 5 | 10 | 58c | diagnostic_only_prefreeze |
| 4 | `post_feature_freeze_entry` | `filter_p_side_gte_85_rank_raw` | `absd` | 62 | 49/13 | 75.61% | 568c | 30.65% | 5 | 10 | 58c | diagnostic_only_prefreeze |
| 5 | `post_feature_freeze_bridge` | `filter_p_side_gte_85_rank_raw` | `low_recross` | 62 | 49/13 | 75.61% | 566c | 30.65% | 5 | 10 | 56c | diagnostic_only_prefreeze |
| 6 | `post_feature_freeze_entry` | `filter_p_side_gte_85_rank_raw` | `low_recross` | 62 | 49/13 | 75.61% | 566c | 30.65% | 5 | 10 | 56c | diagnostic_only_prefreeze |
| 7 | `post_feature_freeze_bridge` | `filter_p_side_gte_85_rank_raw` | `source_proxy_score` | 62 | 49/13 | 75.61% | 564c | 30.65% | 5 | 10 | 54c | diagnostic_only_prefreeze |
| 8 | `post_feature_freeze_entry` | `filter_p_side_gte_85_rank_raw` | `source_proxy_score` | 62 | 49/13 | 75.61% | 564c | 30.65% | 5 | 10 | 54c | diagnostic_only_prefreeze |
| 9 | `post_feature_freeze_bridge` | `filter_p_side_gte_85_rank_raw` | `p_side` | 62 | 49/13 | 75.61% | 425c | 30.65% | 4 | 10 | -85c | diagnostic_only_prefreeze |
| 10 | `post_feature_freeze_bridge` | `filter_p_side_gte_85_rank_raw` | `raw_edge` | 62 | 49/13 | 75.61% | 425c | 30.65% | 4 | 10 | -85c | diagnostic_only_prefreeze |
| 11 | `post_feature_freeze_entry` | `filter_p_side_gte_85_rank_raw` | `p_side` | 62 | 49/13 | 75.61% | 425c | 30.65% | 4 | 10 | -85c | diagnostic_only_prefreeze |
| 12 | `post_feature_freeze_entry` | `filter_p_side_gte_85_rank_raw` | `raw_edge` | 62 | 49/13 | 75.61% | 425c | 30.65% | 4 | 10 | -85c | diagnostic_only_prefreeze |
| 13 | `post_feature_freeze_bridge` | `filter_p_side_gte_85_rank_depth_fresh_raw` | `ask_confirm` | 62 | 50/12 | 75.61% | 631c | 38.71% | 6 | 10 | 64c | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| 14 | `post_feature_freeze_entry` | `filter_p_side_gte_85_rank_depth_fresh_raw` | `ask_confirm` | 62 | 50/12 | 75.61% | 631c | 38.71% | 6 | 10 | 64c | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| 15 | `post_feature_freeze_bridge` | `filter_p_side_gte_85_rank_depth_fresh_raw` | `absd` | 62 | 50/12 | 75.61% | 625c | 38.71% | 6 | 10 | 58c | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| 16 | `post_feature_freeze_entry` | `filter_p_side_gte_85_rank_depth_fresh_raw` | `absd` | 62 | 50/12 | 75.61% | 625c | 38.71% | 6 | 10 | 58c | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| 17 | `post_feature_freeze_bridge` | `filter_p_side_gte_85_rank_depth_fresh_raw` | `low_recross` | 62 | 50/12 | 75.61% | 623c | 38.71% | 6 | 10 | 56c | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| 18 | `post_feature_freeze_entry` | `filter_p_side_gte_85_rank_depth_fresh_raw` | `low_recross` | 62 | 50/12 | 75.61% | 623c | 38.71% | 6 | 10 | 56c | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| 19 | `post_feature_freeze_bridge` | `filter_p_side_gte_85_rank_depth_fresh_raw` | `source_proxy_score` | 62 | 50/12 | 75.61% | 621c | 38.71% | 6 | 10 | 54c | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| 20 | `post_feature_freeze_entry` | `filter_p_side_gte_85_rank_depth_fresh_raw` | `source_proxy_score` | 62 | 50/12 | 75.61% | 621c | 38.71% | 6 | 10 | 54c | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| 21 | `post_feature_freeze_bridge` | `filter_p_side_gte_85_rank_depth_fresh_raw` | `p_side` | 62 | 50/12 | 75.61% | 405c | 37.10% | 4 | 10 | -162c | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| 22 | `post_feature_freeze_bridge` | `filter_p_side_gte_85_rank_depth_fresh_raw` | `raw_edge` | 62 | 50/12 | 75.61% | 405c | 37.10% | 4 | 10 | -162c | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| 23 | `post_feature_freeze_entry` | `filter_p_side_gte_85_rank_depth_fresh_raw` | `p_side` | 62 | 50/12 | 75.61% | 405c | 37.10% | 4 | 10 | -162c | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
| 24 | `post_feature_freeze_entry` | `filter_p_side_gte_85_rank_depth_fresh_raw` | `raw_edge` | 62 | 50/12 | 75.61% | 405c | 37.10% | 4 | 10 | -162c | diagnostic_only_prefreeze, reconstructed_share_gt_35pct |
