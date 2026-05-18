# Temporal Side-Flip Diagnostic

Generated UTC: `20260504_093322Z`

## Scope

- Research-only diagnostic; no orders are submitted and no bot files or live processes are touched.
- Compares first selected book-style rows with first selected Brownian/score rows in the same market.
- Positive `anchor-reference` means the book-style row beat the later/other policy row.

## Focus Buckets

| dataset | anchor | reference | bucket | pairs | anchor acc/net | ref acc/net | anchor-ref | median ref-anchor sec |
|---|---|---|---|---:|---:|---:|---:|---:|
| current | `book_margin` | `frontier_v2` | all_pairs | 303 | 70.96%/982.0c | 62.71%/-17.0c | 999.0c | 0.0 |
| current | `book_margin` | `frontier_v2` | anchor_earlier_same_side | 68 | 66.18%/-67.0c | 66.18%/-156.0c | 89.0c | 30.0 |
| current | `book_margin` | `frontier_v2` | anchor_earlier_side_flip | 7 | 42.86%/-165.0c | 57.14%/-16.0c | -149.0c | 90.1 |
| current | `book_margin` | `score_min60` | all_pairs | 302 | 70.86%/945.0c | 75.50%/1213.0c | -268.0c | 30.0 |
| current | `book_margin` | `score_min60` | anchor_earlier_same_side | 174 | 72.41%/976.0c | 72.41%/-11.0c | 987.0c | 45.1 |
| current | `book_margin` | `score_min60` | anchor_earlier_side_flip | 24 | 20.83%/-1051.0c | 79.17%/204.0c | -1255.0c | 232.8 |
| current | `book_margin_early` | `frontier_v2` | all_pairs | 295 | 71.19%/1012.0c | 63.05%/49.0c | 963.0c | 0.0 |
| current | `book_margin_early` | `frontier_v2` | anchor_earlier_same_side | 68 | 66.18%/-67.0c | 66.18%/-156.0c | 89.0c | 30.0 |
| current | `book_margin_early` | `frontier_v2` | anchor_earlier_side_flip | 7 | 42.86%/-165.0c | 57.14%/-16.0c | -149.0c | 90.1 |
| current | `book_margin_early` | `score_min60` | all_pairs | 294 | 71.09%/975.0c | 75.85%/1305.0c | -330.0c | 30.0 |
| current | `book_margin_early` | `score_min60` | anchor_earlier_same_side | 167 | 73.05%/1038.0c | 73.05%/113.0c | 925.0c | 45.1 |
| current | `book_margin_early` | `score_min60` | anchor_earlier_side_flip | 24 | 20.83%/-1051.0c | 79.17%/204.0c | -1255.0c | 232.8 |
| current | `book_margin_gap015` | `frontier_v2` | all_pairs | 273 | 71.43%/1235.0c | 62.27%/2.0c | 1233.0c | 0.0 |
| current | `book_margin_gap015` | `frontier_v2` | anchor_earlier_same_side | 53 | 62.26%/-162.0c | 62.26%/-276.0c | 114.0c | 30.0 |
| current | `book_margin_gap015` | `frontier_v2` | anchor_earlier_side_flip | 6 | 50.00%/-94.0c | 50.00%/-81.0c | -13.0c | 90.1 |
| current | `book_margin_gap015` | `score_min60` | all_pairs | 272 | 71.32%/1198.0c | 76.10%/1403.0c | -205.0c | 30.0 |
| current | `book_margin_gap015` | `score_min60` | anchor_earlier_same_side | 147 | 72.79%/1097.0c | 72.79%/139.0c | 958.0c | 45.1 |
| current | `book_margin_gap015` | `score_min60` | anchor_earlier_side_flip | 23 | 21.74%/-982.0c | 78.26%/181.0c | -1163.0c | 225.2 |
| v21 | `book_margin` | `frontier_v2` | all_pairs | 219 | 71.23%/425.0c | 68.04%/1283.0c | -858.0c | -22.0 |
| v21 | `book_margin` | `frontier_v2` | anchor_earlier_same_side | 16 | 93.75%/413.0c | 93.75%/401.0c | 12.0c | 25.0 |
| v21 | `book_margin` | `frontier_v2` | anchor_earlier_side_flip | 2 | 0.00%/-128.0c | 100.00%/69.0c | -197.0c | 52.0 |
| v21 | `book_margin` | `score_min60` | all_pairs | 218 | 71.56%/490.0c | 73.85%/534.0c | -44.0c | 0.0 |
| v21 | `book_margin` | `score_min60` | anchor_earlier_same_side | 48 | 93.75%/1301.0c | 93.75%/964.0c | 337.0c | 60.0 |
| v21 | `book_margin` | `score_min60` | anchor_earlier_side_flip | 13 | 30.77%/-434.0c | 69.23%/-53.0c | -381.0c | 180.0 |
| v21 | `book_margin_early` | `frontier_v2` | all_pairs | 208 | 72.60%/719.0c | 68.27%/1209.0c | -490.0c | 0.0 |
| v21 | `book_margin_early` | `frontier_v2` | anchor_earlier_same_side | 16 | 93.75%/413.0c | 93.75%/401.0c | 12.0c | 25.0 |
| v21 | `book_margin_early` | `frontier_v2` | anchor_earlier_side_flip | 2 | 0.00%/-128.0c | 100.00%/69.0c | -197.0c | 52.0 |
| v21 | `book_margin_early` | `score_min60` | all_pairs | 208 | 72.60%/719.0c | 75.00%/787.0c | -68.0c | 0.0 |
| v21 | `book_margin_early` | `score_min60` | anchor_earlier_same_side | 47 | 93.62%/1265.0c | 93.62%/952.0c | 313.0c | 60.0 |
| v21 | `book_margin_early` | `score_min60` | anchor_earlier_side_flip | 13 | 30.77%/-434.0c | 69.23%/-53.0c | -381.0c | 180.0 |
| v21 | `book_margin_gap015` | `frontier_v2` | all_pairs | 214 | 70.56%/306.0c | 67.76%/1254.0c | -948.0c | -22.0 |
| v21 | `book_margin_gap015` | `frontier_v2` | anchor_earlier_same_side | 13 | 92.31%/349.0c | 92.31%/335.0c | 14.0c | 24.0 |
| v21 | `book_margin_gap015` | `frontier_v2` | anchor_earlier_side_flip | 2 | 0.00%/-128.0c | 100.00%/69.0c | -197.0c | 52.0 |
| v21 | `book_margin_gap015` | `score_min60` | all_pairs | 213 | 70.89%/371.0c | 73.24%/416.0c | -45.0c | 0.0 |
| v21 | `book_margin_gap015` | `score_min60` | anchor_earlier_same_side | 44 | 93.18%/1218.0c | 93.18%/882.0c | 336.0c | 60.0 |
| v21 | `book_margin_gap015` | `score_min60` | anchor_earlier_side_flip | 13 | 30.77%/-434.0c | 69.23%/-53.0c | -381.0c | 180.0 |

## Read

- Strongest current early-book side-flip bucket: `book_margin_gap015` vs `frontier_v2` at -13.0c over 6 paired markets.
- This is diagnostic timing evidence only; any rule change still needs strict forward registration.
