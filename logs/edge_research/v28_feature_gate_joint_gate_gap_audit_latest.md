# v28 Feature-Gate Joint Gate Gap Audit

Research-only. No live bot logic changes, no process control, no orders.

- Generated UTC: `2026-05-07T17:37:08.289216+00:00`
- Feature-gate generated UTC: `2026-05-07T15:00:39.637007+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Candidate-vs-live generated UTC: `2026-05-07T16:31:45.290902+00:00`
- Live snapshot net: `1333c ($13.33)`
- Live collection healthy: `False`
- Blockers: `research_only, not_promotion_evidence, fresh_v28_live_collection_unhealthy, no_feature_gate_variant_clears_joint_gates`

## Read

- The current feature-gate branch is not one gate away from promotion; coverage, source share, cushion, and live-baseline gaps interact.
- Raw03-style broad rows buy coverage by adding risky/reconstructed rows and still lack cushion; dropping risky losses fixes source only by breaking coverage.
- Raw05-style rows are cleaner, but they need clean forward rows for coverage and still trail the live snapshot by far more than a normal small-row repair.
- Because v28 live collection is unhealthy, live-baseline deltas are log-snapshot context until the v28 live state is explicitly healthy again.

## Variant Gaps

| lane | candidate | entries/settled | cov | net | source | cushion | clean rows needed cov/source | cents needed cushion/live | joint blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `post_feature_freeze_bridge` | `post_feature_freeze_bridge_raw05_recross60_abs085` | 47/41 | 65.28% | 350c ($3.50) | 0.277 | 3 | 7/0 | 0c ($0.00)/983c ($9.83) | `coverage_too_low, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |
| `post_feature_freeze_entry` | `post_feature_freeze_entry_raw05_recross60_abs085` | 47/36 | 65.28% | 294c ($2.94) | 0.277 | 2 | 7/0 | 6c ($0.06)/1039c ($10.39) | `coverage_too_low, full_loss_cushion_lt_3, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |
| `post_feature_freeze_bridge` | `post_feature_freeze_bridge_raw03_recross70_abs075` | 54/48 | 75.00% | 283c ($2.83) | 0.370 | 2 | 0/4 | 17c ($0.17)/1050c ($10.50) | `reconstructed_share_gt_35pct, full_loss_cushion_lt_3, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |
| `post_feature_freeze_entry` | `post_feature_freeze_entry_raw03_recross70_abs075` | 54/42 | 75.00% | 274c ($2.74) | 0.370 | 2 | 0/4 | 26c ($0.26)/1059c ($10.59) | `reconstructed_share_gt_35pct, full_loss_cushion_lt_3, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |
| `post_feature_freeze_bridge` | `post_feature_freeze_bridge_raw05_recross60_abs085_ask65` | 40/34 | 55.56% | 217c ($2.17) | 0.050 | 2 | 14/0 | 83c ($0.83)/1116c ($11.16) | `coverage_too_low, full_loss_cushion_lt_3, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |
| `post_feature_freeze_bridge` | `post_feature_freeze_bridge_raw07_recross60_abs085` | 33/29 | 45.83% | 280c ($2.80) | 0.242 | 2 | 21/0 | 20c ($0.20)/1053c ($10.53) | `settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |
| `post_feature_freeze_entry` | `post_feature_freeze_entry_raw07_recross60_abs085` | 33/25 | 45.83% | 239c ($2.39) | 0.242 | 2 | 21/0 | 61c ($0.61)/1094c ($10.94) | `settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |
| `post_feature_freeze_entry` | `post_feature_freeze_entry_raw05_recross60_abs085_ask65` | 40/29 | 55.56% | 207c ($2.07) | 0.050 | 2 | 14/0 | 93c ($0.93)/1126c ($11.26) | `settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_live_snapshot, fresh_v28_live_collection_unhealthy` |

## Drop Risky Losses Check

| lane | candidate | read | drop count | remaining entries | coverage | source | net |
|---|---|---|---:|---:|---:|---:|---:|
| `post_feature_freeze_bridge` | `post_feature_freeze_bridge_raw05_recross60_abs085` | `source_passes_only_by_breaking_coverage` | 0 | 47 | 65.28% | 0.277 | 350c ($3.50) |
| `post_feature_freeze_entry` | `post_feature_freeze_entry_raw05_recross60_abs085` | `source_passes_only_by_breaking_coverage` | 0 | 47 | 65.28% | 0.277 | 294c ($2.94) |
| `post_feature_freeze_bridge` | `post_feature_freeze_bridge_raw03_recross70_abs075` | `source_passes_only_by_breaking_coverage` | 2 | 52 | 72.22% | 0.346 | 366c ($3.66) |
| `post_feature_freeze_entry` | `post_feature_freeze_entry_raw03_recross70_abs075` | `source_passes_only_by_breaking_coverage` | 2 | 52 | 72.22% | 0.346 | 300c ($3.00) |
| `post_feature_freeze_bridge` | `post_feature_freeze_bridge_raw05_recross60_abs085_ask65` | `source_passes_only_by_breaking_coverage` | 0 | 40 | 55.56% | 0.050 | 217c ($2.17) |
| `post_feature_freeze_bridge` | `post_feature_freeze_bridge_raw07_recross60_abs085` | `source_passes_only_by_breaking_coverage` | 0 | 33 | 45.83% | 0.242 | 280c ($2.80) |
| `post_feature_freeze_entry` | `post_feature_freeze_entry_raw07_recross60_abs085` | `source_passes_only_by_breaking_coverage` | 0 | 33 | 45.83% | 0.242 | 239c ($2.39) |
| `post_feature_freeze_entry` | `post_feature_freeze_entry_raw05_recross60_abs085_ask65` | `source_passes_only_by_breaking_coverage` | 0 | 40 | 55.56% | 0.050 | 207c ($2.07) |
