# v28 Candidate Live-Validation Runway

How much future non-simulated evidence shadow candidates still need. No candidate is promoted here.

- Max simulated share: `0.35`
- Minimum settled rows: `30`

## Current Read

- Best target-coverage gross row is p50_book_plus_05_edge_nonnegative at 890.0c, but it needs 172 future actual-only entries to bring simulated share to <=35%.
- Closest row to validation by count is book_plus_03_cheap_convex needing 171 future validation rows, coverage 50.82872928176796.
- This runway is not a live-trading instruction; it defines how much forward evidence is still missing.

## Runway

| policy | coverage | gross c | sim share | future actual needed | settled needed | min validation rows | loss cushion c | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `p50_book_plus_05_edge_nonnegative` | 83.425414 | 890.000000 | 0.748344 | 172 | 0 | 172 | 890.000000 | candidate_simulated_share_gt_35pct |
| `p65_book_plus_03` | 80.110497 | -1486.000000 | 0.772414 | 175 | 0 | 175 | 0.000000 | candidate_simulated_share_gt_35pct |
| `p65_v28_premium_anchor_plus_02` | 79.558011 | -1376.000000 | 0.805556 | 188 | 0 | 188 | 0.000000 | candidate_simulated_share_gt_35pct |
| `p65_large_disagreement_anchor_plus_02` | 80.110497 | -1198.000000 | 0.813793 | 193 | 0 | 193 | 0.000000 | candidate_simulated_share_gt_35pct |
| `p65_book_plus_02` | 83.977901 | -1542.000000 | 0.822368 | 206 | 0 | 206 | 0.000000 | candidate_simulated_share_gt_35pct |
| `p55_edge_nonnegative` | 83.425414 | 305.000000 | 0.834437 | 209 | 0 | 209 | 305.000000 | candidate_simulated_share_gt_35pct |
| `book_plus_03_cheap_convex` | 50.828729 | 916.000000 | 1.000000 | 171 | 0 | 171 | 916.000000 | candidate_simulated_share_gt_35pct, coverage_below_75pct |
| `book_plus_05_no_cheap_yes_boundary` | 90.607735 | 646.000000 | 0.810976 | 216 | 0 | 216 | 646.000000 | candidate_simulated_share_gt_35pct, coverage_above_90pct |
| `book_plus_05` | 93.370166 | 132.000000 | 0.822485 | 229 | 0 | 229 | 132.000000 | candidate_simulated_share_gt_35pct, coverage_above_90pct |
| `book_plus_03_avoid_coinflip` | 94.475138 | -873.000000 | 0.918129 | 278 | 0 | 278 | 0.000000 | candidate_simulated_share_gt_35pct, coverage_above_90pct |
| `book_plus_02_avoid_coinflip_liquid` | 94.475138 | -56.000000 | 0.935673 | 287 | 0 | 287 | 0.000000 | candidate_simulated_share_gt_35pct, coverage_above_90pct |
| `book_plus_02_avoid_coinflip` | 94.475138 | -27.000000 | 0.941520 | 290 | 0 | 290 | 0.000000 | candidate_simulated_share_gt_35pct, coverage_above_90pct |
| `book_plus_03` | 96.685083 | -303.000000 | 0.954286 | 303 | 0 | 303 | 0.000000 | candidate_simulated_share_gt_35pct, coverage_above_90pct |
