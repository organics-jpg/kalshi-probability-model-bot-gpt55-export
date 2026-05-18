# V2 Conditional Wait Scan

Generated UTC: `20260504_003454Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Takes v2 unless the first v2 row shows a simple instability flag, then waits for a later consensus candidate.
- Rules use only features visible on the first v2 row; later candidate rows are used only after the rule has committed to wait.

## Baseline

- Current v2 baseline: 197.0c
- V21 v2 baseline: 1283.0c

## Summary

- Wait rules scanned: 60
- Both-dataset 80% coverage rules: 53
- Both-dataset OOS-positive rules: 13

## Top Rows

| rank | rule | delta current/v21 | current net/acc/cov | v21 net/acc/cov | OOS ROI floor |
|---:|---|---:|---:|---:|---:|
| 1 | `wait_for_score_min60_if_v2_book_p_side<=0.6` | 994.0c/-621.0c | 1191.0c/74.63%/99.26% | 662.0c/73.39%/98.64% | 1.56% |
| 2 | `wait_for_score_min60_if_v2_seconds_to_close>=600` | 1090.0c/-725.0c | 1287.0c/76.03%/98.89% | 558.0c/73.85%/98.64% | 2.15% |
| 3 | `wait_for_score_min60_if_v2_score_min_book_rv15<=0.6` | 1071.0c/-749.0c | 1268.0c/76.03%/98.89% | 534.0c/73.85%/98.64% | 2.15% |
| 4 | `wait_for_score_min60_if_v2_score_min_book_rv15<=0.65` | 1071.0c/-749.0c | 1268.0c/76.03%/98.89% | 534.0c/73.85%/98.64% | 2.15% |
| 5 | `wait_for_score_min60_if_v2_score_min_book_rv15<=0.7` | 1071.0c/-749.0c | 1268.0c/76.03%/98.89% | 534.0c/73.85%/98.64% | 2.15% |
| 6 | `wait_for_score_min60_if_v2_score_min_book_rv15<=0.75` | 1071.0c/-749.0c | 1268.0c/76.03%/98.89% | 534.0c/73.85%/98.64% | 2.15% |
| 7 | `wait_for_score_min60_if_v2_book_p_side<=0.65` | 1013.0c/-724.0c | 1210.0c/75.66%/98.89% | 559.0c/73.85%/98.64% | 2.28% |
| 8 | `wait_for_score_min60_if_v2_book_p_side<=0.7` | 980.0c/-746.0c | 1177.0c/75.66%/98.89% | 537.0c/73.85%/98.64% | 2.15% |
| 9 | `wait_for_book_margin_if_v2_score_min_book_rv15<=0.6` | 866.0c/-840.0c | 1063.0c/72.54%/90.37% | 443.0c/71.70%/95.93% | 4.08% |
| 10 | `wait_for_score_min60_if_v2_seconds_to_close>=720` | 887.0c/-890.0c | 1084.0c/74.91%/98.89% | 393.0c/72.94%/98.64% | 0.39% |
| 11 | `wait_for_book_margin_if_v2_book_p_side<=0.6` | 828.0c/-837.0c | 1025.0c/72.16%/94.44% | 446.0c/71.63%/97.29% | 5.85% |
| 12 | `wait_for_book_margin_if_v2_score_min_book_rv15<=0.65` | 925.0c/-1038.0c | 1122.0c/73.21%/82.96% | 245.0c/70.87%/93.21% | 2.76% |
| 13 | `wait_for_book_margin_if_v2_book_p_side<=0.65` | 798.0c/-947.0c | 995.0c/72.57%/87.78% | 336.0c/71.29%/94.57% | 5.07% |
| 14 | `wait_for_score_min60_if_v2_book_p_side<=0.55` | 903.0c/-98.0c | 1100.0c/71.64%/99.26% | 1185.0c/72.94%/98.64% | -2.65% |
| 15 | `wait_for_score_min60_if_v2_score_min_book_rv15<=0.55` | 903.0c/-98.0c | 1100.0c/71.64%/99.26% | 1185.0c/72.94%/98.64% | -2.65% |
| 16 | `wait_for_score_min60_if_v2_adverse_move_15m>=75` | 324.0c/174.0c | 521.0c/64.93%/99.26% | 1457.0c/69.86%/99.10% | -8.57% |
| 17 | `wait_for_book_margin_if_v2_adverse_move_15m>=75` | 388.0c/58.0c | 585.0c/64.62%/96.30% | 1341.0c/69.12%/98.19% | -8.51% |
| 18 | `wait_for_book_margin_if_v2_book_p_side<=0.55` | 619.0c/-240.0c | 816.0c/69.70%/97.78% | 1043.0c/71.89%/98.19% | -1.88% |
| 19 | `wait_for_book_margin_if_v2_score_min_book_rv15<=0.55` | 619.0c/-240.0c | 816.0c/69.70%/97.78% | 1043.0c/71.89%/98.19% | -1.88% |
| 20 | `wait_for_book_margin_if_v2_abs_book_rv15_gap>=0.1` | 579.0c/-249.0c | 776.0c/67.18%/97.04% | 1034.0c/69.41%/99.10% | -7.17% |

## Read

- Best conditional wait row: `wait_for_score_min60_if_v2_book_p_side<=0.6` with current/v21 delta 994.0c/-621.0c.
- This is worth forward-lock consideration, not promotion.
