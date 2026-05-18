# v28 p50 + Soft-Frontier Overlap Mix

Research-only p50/book-edge versus soft-frontier/midprice overlap test. No live orders.

- Generated UTC: `2026-05-11T03:11:01.878698+00:00`
- Lane counts: `{'soft_lanes': 3, 'p50_lanes': 5, 'portfolios': 30}`
- Candidate live-ready: `False`

## Interpretation

- This is diagnostic overlap research only; any dual child needs its own frozen forward birth.
- The key metric is add-on non-overlap PnL, because shared-market overlap does not create independent market coverage.
- A useful dual strategy should add positive non-overlap rows while keeping 75-90% coverage, <=35% reconstructed share, and cushion >=3.

## Best Positive Target-Coverage Mix

- Primary: `p50_book_edge:frozen_parent_diagnostic:p50_yes_or_no_low_recross`
- Add-on: `soft_frontier_midprice:diagnostic_entry:diagnostic_entry_quarter_midprice_boundary`
- Entries/W-L/net/coverage/recon/cushion: `102/67-35/750.000000c/86.440678%/0.686275/7`
- Add-on non-overlap entries/net: `21/42.000000c`
- Shared markets/side agree/disagree: `58/43/15`
- Blockers: `reconstructed_share_gt_35pct, live_ready_false`

## Top Portfolio Mixes

| rank | primary | add-on | entries | W/L | net | coverage | recon | cushion | add-on nonoverlap | shared agree/disagree | blockers |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `p50_book_edge:frozen_parent_diagnostic:p50_full_size` | `soft_frontier_midprice:diagnostic_entry:diagnostic_entry_quarter_midprice_boundary` | 109 | 66/43 | 752.000000 | 92.372881% | 0.788991 | 7 | 5/92.000000 | 51/23 | `coverage_too_high, reconstructed_share_gt_35pct, live_ready_false` |
| 2 | `p50_book_edge:frozen_parent_diagnostic:p50_yes_or_no_low_recross` | `soft_frontier_midprice:diagnostic_entry:diagnostic_entry_quarter_midprice_boundary` | 102 | 67/35 | 750.000000 | 86.440678% | 0.686275 | 7 | 21/42.000000 | 43/15 | `reconstructed_share_gt_35pct, live_ready_false` |
| 3 | `p50_book_edge:frozen_parent_diagnostic:p50_full_size` | `soft_frontier_midprice:diagnostic_bridge:diagnostic_bridge_quarter_midprice_boundary` | 107 | 64/43 | 702.000000 | 90.677966% | 0.794393 | 7 | 3/42.000000 | 51/23 | `coverage_too_high, reconstructed_share_gt_35pct, live_ready_false` |
| 4 | `p50_book_edge:frozen_parent_diagnostic:p50_yes_or_no_low_recross` | `soft_frontier_midprice:diagnostic_bridge:diagnostic_bridge_quarter_midprice_boundary` | 100 | 65/35 | 700.000000 | 84.745763% | 0.690000 | 7 | 19/-8.000000 | 43/15 | `reconstructed_share_gt_35pct, live_ready_false` |
| 5 | `p50_book_edge:frozen_parent_diagnostic:p50_yes_only` | `soft_frontier_midprice:diagnostic_entry:diagnostic_entry_quarter_midprice_boundary` | 97 | 68/29 | 669.750000 | 82.203390% | 0.639175 | 6 | 38/341.750000 | 28/13 | `reconstructed_share_gt_35pct, live_ready_false` |
| 6 | `p50_book_edge:frozen_parent_diagnostic:p50_full_size` | `soft_frontier_midprice:post_feature_freeze_entry:post_feature_freeze_entry_quarter_midprice_boundary` | 104 | 61/43 | 660.000000 | 88.135593% | 0.788462 | 6 | 0/0 | 34/13 | `reconstructed_share_gt_35pct, live_ready_false` |
| 7 | `soft_frontier_midprice:diagnostic_entry:diagnostic_entry_quarter_midprice_boundary` | `p50_book_edge:frozen_parent_diagnostic:p50_yes_or_no_low_recross` | 102 | 81/20 | 644.500000 | 86.440678% | 0.450980 | 6 | 23/-144.000000 | 43/15 | `diagnostic_or_parent_mix_needs_own_freeze, reconstructed_share_gt_35pct, live_ready_false` |
| 8 | `soft_frontier_midprice:diagnostic_entry:diagnostic_entry_quarter_midprice_boundary` | `p50_book_edge:frozen_parent_diagnostic:p50_yes_or_no_strong_distance` | 102 | 81/20 | 644.500000 | 86.440678% | 0.450980 | 6 | 23/-144.000000 | 39/14 | `diagnostic_or_parent_mix_needs_own_freeze, reconstructed_share_gt_35pct, live_ready_false` |
| 9 | `p50_book_edge:frozen_parent_diagnostic:p50_yes_or_no_low_recross` | `soft_frontier_midprice:post_feature_freeze_entry:post_feature_freeze_entry_quarter_midprice_boundary` | 88 | 54/34 | 627.000000 | 74.576271% | 0.715909 | 6 | 7/-81.000000 | 30/10 | `coverage_too_low, reconstructed_share_gt_35pct, live_ready_false` |
| 10 | `p50_book_edge:frozen_parent_diagnostic:p50_yes_only` | `soft_frontier_midprice:diagnostic_bridge:diagnostic_bridge_quarter_midprice_boundary` | 95 | 66/29 | 619.750000 | 80.508475% | 0.642105 | 6 | 36/291.750000 | 28/13 | `reconstructed_share_gt_35pct, live_ready_false` |
| 11 | `soft_frontier_midprice:diagnostic_entry:diagnostic_entry_quarter_midprice_boundary` | `p50_book_edge:frozen_parent_diagnostic:p50_full_size` | 109 | 84/24 | 606.500000 | 92.372881% | 0.486239 | 6 | 30/-182.000000 | 51/23 | `diagnostic_or_parent_mix_needs_own_freeze, coverage_too_high, reconstructed_share_gt_35pct, live_ready_false` |
| 12 | `soft_frontier_midprice:diagnostic_bridge:diagnostic_bridge_quarter_midprice_boundary` | `p50_book_edge:frozen_parent_diagnostic:p50_yes_or_no_low_recross` | 100 | 79/20 | 594.500000 | 84.745763% | 0.450000 | 5 | 23/-144.000000 | 43/15 | `diagnostic_or_parent_mix_needs_own_freeze, reconstructed_share_gt_35pct, live_ready_false` |
| 13 | `soft_frontier_midprice:diagnostic_bridge:diagnostic_bridge_quarter_midprice_boundary` | `p50_book_edge:frozen_parent_diagnostic:p50_yes_or_no_strong_distance` | 100 | 79/20 | 594.500000 | 84.745763% | 0.450000 | 5 | 23/-144.000000 | 39/14 | `diagnostic_or_parent_mix_needs_own_freeze, reconstructed_share_gt_35pct, live_ready_false` |
| 14 | `soft_frontier_midprice:diagnostic_bridge:diagnostic_bridge_quarter_midprice_boundary` | `p50_book_edge:frozen_parent_diagnostic:p50_full_size` | 107 | 82/24 | 556.500000 | 90.677966% | 0.485981 | 5 | 30/-182.000000 | 51/23 | `diagnostic_or_parent_mix_needs_own_freeze, coverage_too_high, reconstructed_share_gt_35pct, live_ready_false` |
| 15 | `soft_frontier_midprice:diagnostic_entry:diagnostic_entry_quarter_midprice_boundary` | `p50_book_edge:frozen_parent_diagnostic:p50_quarter_no_side` | 109 | 84/24 | 554.000000 | 92.372881% | 0.486239 | 5 | 30/-234.500000 | 51/23 | `diagnostic_or_parent_mix_needs_own_freeze, coverage_too_high, reconstructed_share_gt_35pct, live_ready_false` |
| 16 | `p50_book_edge:frozen_parent_diagnostic:p50_yes_or_no_strong_distance` | `soft_frontier_midprice:diagnostic_entry:diagnostic_entry_quarter_midprice_boundary` | 102 | 68/34 | 553.750000 | 86.440678% | 0.656863 | 5 | 26/135.750000 | 39/14 | `reconstructed_share_gt_35pct, live_ready_false` |
| 17 | `soft_frontier_midprice:diagnostic_entry:diagnostic_entry_quarter_midprice_boundary` | `p50_book_edge:frozen_parent_diagnostic:p50_yes_only` | 97 | 77/19 | 536.500000 | 82.203390% | 0.453608 | 5 | 18/-252.000000 | 28/13 | `diagnostic_or_parent_mix_needs_own_freeze, reconstructed_share_gt_35pct, live_ready_false` |
| 18 | `soft_frontier_midprice:diagnostic_bridge:diagnostic_bridge_quarter_midprice_boundary` | `p50_book_edge:frozen_parent_diagnostic:p50_quarter_no_side` | 107 | 82/24 | 504.000000 | 90.677966% | 0.485981 | 5 | 30/-234.500000 | 51/23 | `diagnostic_or_parent_mix_needs_own_freeze, coverage_too_high, reconstructed_share_gt_35pct, live_ready_false` |
| 19 | `p50_book_edge:frozen_parent_diagnostic:p50_yes_or_no_strong_distance` | `soft_frontier_midprice:diagnostic_bridge:diagnostic_bridge_quarter_midprice_boundary` | 100 | 66/34 | 503.750000 | 84.745763% | 0.660000 | 5 | 24/85.750000 | 39/14 | `reconstructed_share_gt_35pct, live_ready_false` |
| 20 | `p50_book_edge:frozen_parent_diagnostic:p50_quarter_no_side` | `soft_frontier_midprice:diagnostic_entry:diagnostic_entry_quarter_midprice_boundary` | 109 | 66/43 | 503.000000 | 92.372881% | 0.788991 | 5 | 5/92.000000 | 51/23 | `coverage_too_high, reconstructed_share_gt_35pct, live_ready_false` |
| 21 | `soft_frontier_midprice:diagnostic_bridge:diagnostic_bridge_quarter_midprice_boundary` | `p50_book_edge:frozen_parent_diagnostic:p50_yes_only` | 95 | 75/19 | 486.500000 | 80.508475% | 0.452632 | 4 | 18/-252.000000 | 28/13 | `diagnostic_or_parent_mix_needs_own_freeze, reconstructed_share_gt_35pct, live_ready_false` |
| 22 | `p50_book_edge:frozen_parent_diagnostic:p50_yes_only` | `soft_frontier_midprice:post_feature_freeze_entry:post_feature_freeze_entry_quarter_midprice_boundary` | 79 | 51/28 | 457.750000 | 66.949153% | 0.696203 | 4 | 20/129.750000 | 18/9 | `coverage_too_low, reconstructed_share_gt_35pct, live_ready_false` |
| 23 | `p50_book_edge:frozen_parent_diagnostic:p50_quarter_no_side` | `soft_frontier_midprice:diagnostic_bridge:diagnostic_bridge_quarter_midprice_boundary` | 107 | 64/43 | 453.000000 | 90.677966% | 0.794393 | 4 | 3/42.000000 | 51/23 | `coverage_too_high, reconstructed_share_gt_35pct, live_ready_false` |
| 24 | `p50_book_edge:frozen_parent_diagnostic:p50_quarter_no_side` | `soft_frontier_midprice:post_feature_freeze_entry:post_feature_freeze_entry_quarter_midprice_boundary` | 104 | 61/43 | 411.000000 | 88.135593% | 0.788462 | 4 | 0/0 | 34/13 | `reconstructed_share_gt_35pct, live_ready_false` |
| 25 | `p50_book_edge:frozen_parent_diagnostic:p50_yes_or_no_strong_distance` | `soft_frontier_midprice:post_feature_freeze_entry:post_feature_freeze_entry_quarter_midprice_boundary` | 87 | 54/33 | 405.750000 | 73.728814% | 0.689655 | 4 | 11/-12.250000 | 27/9 | `coverage_too_low, reconstructed_share_gt_35pct, live_ready_false` |
