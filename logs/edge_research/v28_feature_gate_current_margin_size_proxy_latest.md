# v28 Feature-Gate Current Marginal Size Proxy

Research-only. No live bot logic changes, no process control, no orders.

- Generated UTC: `2026-05-07T17:41:52.832338+00:00`
- Feature-gate generated UTC: `2026-05-07T15:00:39.637007+00:00`
- Live snapshot net: `1333.0c ($13.33)`
- Best exposure-clean policy: `post_feature_freeze_bridge` / `raw05_anchor_plus_raw03_marginal_weight_0.05`
- Best exposure-clean coverage/net/row-source/exposure-source: `75.00%` / `345.9c ($3.46)` / `0.370` / `0.282`
- Official clean policy: `None`
- Blockers: `research_only, not_promotion_evidence, exposure_clean_but_row_source_blocked, no_policy_clears_official_row_source_gate, fresh_v28_live_collection_unhealthy`

## Read

- Marginal-size shrinkage can make exposure-source share look cleaner, but official row-source share remains above the 35% gate whenever raw03-only coverage rows are kept.
- Zeroing marginal rows restores the cleaner raw05 source profile, but then coverage drops below target.
- The current-denominator size proxy is therefore useful risk-sizing context, not a promotion repair.

## Policies

| lane | policy | entries/settled | coverage | weighted net | row source | exposure source | cushion | delta live | marginal rows/net | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `post_feature_freeze_bridge` | `raw05_anchor_plus_raw03_marginal_weight_0` | 47/41 | 65.28% | 350.0c ($3.50) | 0.277 | 0.277 | 3 | -983.0c ($-9.83) | 0/0.0c ($0.00) | `research_only, not_frozen_as_size_policy, coverage_too_low, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |
| `post_feature_freeze_bridge` | `raw05_anchor_plus_raw03_marginal_weight_0.05` | 54/48 | 75.00% | 345.9c ($3.46) | 0.370 | 0.282 | 3 | -987.1c ($-9.87) | 7/-4.2c ($-0.04) | `research_only, not_frozen_as_size_policy, row_source_share_gt_35pct, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |
| `post_feature_freeze_bridge` | `raw05_anchor_plus_raw03_marginal_weight_0.125` | 54/48 | 75.00% | 339.6c ($3.40) | 0.370 | 0.290 | 3 | -993.4c ($-9.93) | 7/-10.4c ($-0.10) | `research_only, not_frozen_as_size_policy, row_source_share_gt_35pct, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |
| `post_feature_freeze_bridge` | `raw05_anchor_plus_raw03_marginal_weight_0.25` | 54/48 | 75.00% | 329.2c ($3.29) | 0.370 | 0.303 | 3 | -1003.8c ($-10.04) | 7/-20.8c ($-0.21) | `research_only, not_frozen_as_size_policy, row_source_share_gt_35pct, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |
| `post_feature_freeze_bridge` | `raw05_anchor_plus_raw03_marginal_weight_0.5` | 54/48 | 75.00% | 308.5c ($3.08) | 0.370 | 0.327 | 3 | -1024.5c ($-10.24) | 7/-41.5c ($-0.41) | `research_only, not_frozen_as_size_policy, row_source_share_gt_35pct, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |
| `post_feature_freeze_entry` | `raw05_anchor_plus_raw03_marginal_weight_0` | 47/36 | 65.28% | 294.0c ($2.94) | 0.277 | 0.277 | 2 | -1039.0c ($-10.39) | 0/0.0c ($0.00) | `research_only, not_frozen_as_size_policy, coverage_too_low, weighted_full_loss_cushion_lt_3, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |
| `post_feature_freeze_entry` | `raw05_anchor_plus_raw03_marginal_weight_0.05` | 54/42 | 75.00% | 293.2c ($2.93) | 0.370 | 0.282 | 2 | -1039.8c ($-10.40) | 7/-0.8c ($-0.01) | `research_only, not_frozen_as_size_policy, row_source_share_gt_35pct, weighted_full_loss_cushion_lt_3, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |
| `post_feature_freeze_entry` | `raw05_anchor_plus_raw03_marginal_weight_0.125` | 54/42 | 75.00% | 292.1c ($2.92) | 0.370 | 0.290 | 2 | -1040.9c ($-10.41) | 7/-1.9c ($-0.02) | `research_only, not_frozen_as_size_policy, row_source_share_gt_35pct, weighted_full_loss_cushion_lt_3, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |
| `post_feature_freeze_entry` | `raw05_anchor_plus_raw03_marginal_weight_0.25` | 54/42 | 75.00% | 290.2c ($2.90) | 0.370 | 0.303 | 2 | -1042.8c ($-10.43) | 7/-3.8c ($-0.04) | `research_only, not_frozen_as_size_policy, row_source_share_gt_35pct, weighted_full_loss_cushion_lt_3, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |
| `post_feature_freeze_entry` | `raw05_anchor_plus_raw03_marginal_weight_0.5` | 54/42 | 75.00% | 286.5c ($2.87) | 0.370 | 0.327 | 2 | -1046.5c ($-10.46) | 7/-7.5c ($-0.07) | `research_only, not_frozen_as_size_policy, row_source_share_gt_35pct, weighted_full_loss_cushion_lt_3, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |
| `post_feature_freeze_entry` | `raw05_anchor_plus_raw03_marginal_weight_1` | 54/42 | 75.00% | 279.0c ($2.79) | 0.370 | 0.370 | 2 | -1054.0c ($-10.54) | 7/-15.0c ($-0.15) | `research_only, not_frozen_as_size_policy, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |
| `post_feature_freeze_bridge` | `raw05_anchor_plus_raw03_marginal_weight_1` | 54/48 | 75.00% | 267.0c ($2.67) | 0.370 | 0.370 | 2 | -1066.0c ($-10.66) | 7/-83.0c ($-0.83) | `research_only, not_frozen_as_size_policy, row_source_share_gt_35pct, exposure_source_share_gt_35pct, weighted_full_loss_cushion_lt_3, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |
