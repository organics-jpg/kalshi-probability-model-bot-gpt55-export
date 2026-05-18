# v28 Candidate vs Control Overlap

Same-market control comparison for shadow entry candidates. No candidate is promoted here.

- Baseline policy: `baseline_v28_approved`
- Baseline entries/settled/W-L/gross: `107/107/91-16/494.000000c`
- Watched markets / observation rows: `181/6798`

## Current Read

- Top gross candidate is book_plus_03_cheap_convex with 916.0c on its selected settled markets.
- Best same-market overlap delta is book_plus_03_cheap_convex at 740.0c across 48 overlapping markets.
- Best 75-90% coverage candidate by gross is p50_book_plus_05_edge_nonnegative with coverage 83.42541436464089 and gross 890.0c.
- Common blockers remain: candidate_simulated_share_gt_35pct, coverage_above_90pct, coverage_below_75pct.

## Ranked Candidates

| rank | policy | entries | settled | W/L | coverage | gross c | sim share | overlap delta | candidate-only c | baseline-only c | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `book_plus_03_cheap_convex` | 92 | 92 | 32/60 | 50.828729 | 916.000000 | 1.000000 | 740.000000 | 170.000000 | 488.000000 | candidate_simulated_share_gt_35pct, coverage_below_75pct |
| 2 | `p50_book_plus_05_edge_nonnegative` | 151 | 151 | 96/55 | 83.425414 | 890.000000 | 0.748344 | 598.000000 | -202.000000 | 0 | candidate_simulated_share_gt_35pct |
| 3 | `book_plus_05_no_cheap_yes_boundary` | 164 | 164 | 92/72 | 90.607735 | 646.000000 | 0.810976 | 84.000000 | 68.000000 | 0 | candidate_simulated_share_gt_35pct, coverage_above_90pct |
| 4 | `p55_edge_nonnegative` | 151 | 151 | 100/51 | 83.425414 | 305.000000 | 0.834437 | 117.000000 | -306.000000 | 0 | candidate_simulated_share_gt_35pct |
| 5 | `book_plus_05` | 169 | 169 | 89/80 | 93.370166 | 132.000000 | 0.822485 | -194.000000 | -168.000000 | 0 | candidate_simulated_share_gt_35pct, coverage_above_90pct |
| 6 | `book_plus_02_avoid_coinflip` | 171 | 171 | 91/80 | 94.475138 | -27.000000 | 0.941520 | -63.000000 | -458.000000 | 0 | candidate_simulated_share_gt_35pct, coverage_above_90pct |
| 7 | `book_plus_02_avoid_coinflip_liquid` | 171 | 171 | 91/80 | 94.475138 | -56.000000 | 0.935673 | -92.000000 | -458.000000 | 0 | candidate_simulated_share_gt_35pct, coverage_above_90pct |
| 8 | `book_plus_03` | 175 | 175 | 87/88 | 96.685083 | -303.000000 | 0.954286 | -469.000000 | -328.000000 | 0 | candidate_simulated_share_gt_35pct, coverage_above_90pct |
| 9 | `book_plus_03_avoid_coinflip` | 171 | 171 | 88/83 | 94.475138 | -873.000000 | 0.918129 | -481.000000 | -886.000000 | 0 | candidate_simulated_share_gt_35pct, coverage_above_90pct |
| 10 | `p65_large_disagreement_anchor_plus_02` | 145 | 145 | 101/44 | 80.110497 | -1198.000000 | 0.813793 | -932.000000 | -786.000000 | -26.000000 | candidate_simulated_share_gt_35pct |
| 11 | `p65_v28_premium_anchor_plus_02` | 144 | 144 | 100/44 | 79.558011 | -1376.000000 | 0.805556 | -1030.000000 | -866.000000 | -26.000000 | candidate_simulated_share_gt_35pct |
| 12 | `p65_book_plus_03` | 145 | 145 | 97/48 | 80.110497 | -1486.000000 | 0.772414 | -1052.000000 | -928.000000 | 0 | candidate_simulated_share_gt_35pct |
| 13 | `p65_book_plus_02` | 152 | 152 | 101/51 | 83.977901 | -1542.000000 | 0.822368 | -926.000000 | -1110.000000 | 0 | candidate_simulated_share_gt_35pct |

## Target-Coverage Rows

| policy | coverage | gross c | overlap markets | overlap delta | simulated share | blockers |
|---|---:|---:|---:|---:|---:|---|
| `p50_book_plus_05_edge_nonnegative` | 83.425414 | 890.000000 | 107 | 598.000000 | 0.748344 | candidate_simulated_share_gt_35pct |
| `p55_edge_nonnegative` | 83.425414 | 305.000000 | 107 | 117.000000 | 0.834437 | candidate_simulated_share_gt_35pct |
| `p65_large_disagreement_anchor_plus_02` | 80.110497 | -1198.000000 | 106 | -932.000000 | 0.813793 | candidate_simulated_share_gt_35pct |
| `p65_v28_premium_anchor_plus_02` | 79.558011 | -1376.000000 | 106 | -1030.000000 | 0.805556 | candidate_simulated_share_gt_35pct |
| `p65_book_plus_03` | 80.110497 | -1486.000000 | 107 | -1052.000000 | 0.772414 | candidate_simulated_share_gt_35pct |
| `p65_book_plus_02` | 83.977901 | -1542.000000 | 107 | -926.000000 | 0.822368 | candidate_simulated_share_gt_35pct |
