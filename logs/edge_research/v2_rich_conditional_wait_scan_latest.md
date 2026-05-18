# V2 Rich Conditional Wait Scan

Generated UTC: `20260504_003454Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Takes v2 unless the first v2 row is early and optionally matches one instability condition.
- If the trigger fires, the rule waits for a later locked candidate row in the same market.
- Trigger conditions use only first-v2-row features, so the scan is causal with respect to the wait decision.

## Baseline

- Current v2 baseline: 197.0c
- V21 v2 baseline: 1283.0c

## Summary

- Wait rules scanned: 324
- Both-dataset 80% coverage rules: 300
- Both-dataset OOS-positive rules: 35

## Top Rows

| rank | rule | delta current/v21 | current net/acc/cov | v21 net/acc/cov | OOS ROI floor |
|---:|---|---:|---:|---:|---:|
| 1 | `wait_for_score_min60_if_v2_seconds_to_close>=600_AND_brownian_p_rv_15m<=0.7` | 1163.0c/-528.0c | 1360.0c/76.03%/98.89% | 755.0c/74.31%/98.64% | 0.18% |
| 2 | `wait_for_book_margin_early_if_v2_seconds_to_close>=600_AND_score_min_book_rv15<=0.6` | 981.0c/-510.0c | 1178.0c/73.11%/88.15% | 773.0c/73.27%/91.40% | 4.08% |
| 3 | `wait_for_book_margin_early_if_v2_seconds_to_close>=600_AND_book_p_side<=0.6` | 943.0c/-507.0c | 1140.0c/72.69%/92.22% | 776.0c/73.17%/92.76% | 5.85% |
| 4 | `wait_for_book_margin_early_if_v2_seconds_to_close>=720_AND_score_min_book_rv15<=0.6` | 912.0c/-498.0c | 1109.0c/72.54%/90.37% | 785.0c/73.27%/91.40% | 3.29% |
| 5 | `wait_for_book_margin_early_if_v2_seconds_to_close>=720_AND_book_p_side<=0.6` | 901.0c/-495.0c | 1098.0c/72.33%/93.70% | 788.0c/73.17%/92.76% | 4.14% |
| 6 | `wait_for_score_min60_if_v2_seconds_to_close>=600_AND_book_p_side<=0.6` | 1013.0c/-621.0c | 1210.0c/74.63%/99.26% | 662.0c/73.39%/98.64% | 1.56% |
| 7 | `wait_for_score_min60_if_v2_seconds_to_close>=600` | 1090.0c/-725.0c | 1287.0c/76.03%/98.89% | 558.0c/73.85%/98.64% | 2.15% |
| 8 | `wait_for_score_min60_if_v2_seconds_to_close>=600_AND_score_min_book_rv15<=0.6` | 1090.0c/-725.0c | 1287.0c/76.03%/98.89% | 558.0c/73.85%/98.64% | 2.15% |
| 9 | `wait_for_score_min60_if_v2_seconds_to_close>=600_AND_score_min_book_rv15<=0.65` | 1090.0c/-725.0c | 1287.0c/76.03%/98.89% | 558.0c/73.85%/98.64% | 2.15% |
| 10 | `wait_for_score_min60_if_v2_seconds_to_close>=600_AND_score_min_book_rv15<=0.7` | 1090.0c/-725.0c | 1287.0c/76.03%/98.89% | 558.0c/73.85%/98.64% | 2.15% |
| 11 | `wait_for_score_min60_if_v2_seconds_to_close>=600_AND_score_min_book_rv15<=0.75` | 1090.0c/-725.0c | 1287.0c/76.03%/98.89% | 558.0c/73.85%/98.64% | 2.15% |
| 12 | `wait_for_score_min60_if_v2_seconds_to_close>=600_AND_book_p_side<=0.65` | 1032.0c/-700.0c | 1229.0c/75.66%/98.89% | 583.0c/73.85%/98.64% | 2.28% |
| 13 | `wait_for_book_margin_early_if_v2_seconds_to_close>=600_AND_book_p_side<=0.65` | 913.0c/-617.0c | 1110.0c/73.16%/85.56% | 666.0c/72.86%/90.05% | 5.11% |
| 14 | `wait_for_score_min60_if_v2_seconds_to_close>=600_AND_book_p_side<=0.7` | 999.0c/-722.0c | 1196.0c/75.66%/98.89% | 561.0c/73.85%/98.64% | 2.15% |
| 15 | `wait_for_book_margin_early_if_v2_seconds_to_close>=720_AND_book_p_side<=0.65` | 881.0c/-605.0c | 1078.0c/72.69%/88.15% | 678.0c/72.86%/90.05% | 4.26% |
| 16 | `wait_for_book_margin_early_if_v2_seconds_to_close>=720_AND_score_min_book_rv15<=0.65` | 938.0c/-696.0c | 1135.0c/73.01%/83.70% | 587.0c/72.45%/88.69% | 1.95% |
| 17 | `wait_for_score_min60_if_v2_seconds_to_close>=600_AND_brownian_p_rv_15m<=0.65` | 864.0c/-719.0c | 1061.0c/74.16%/98.89% | 564.0c/72.94%/98.64% | 0.41% |
| 18 | `wait_for_book_margin_if_v2_seconds_to_close>=720_AND_brownian_p_rv_15m<=0.7` | 997.0c/-876.0c | 1194.0c/72.97%/82.22% | 407.0c/71.22%/92.76% | 0.88% |
| 19 | `wait_for_book_margin_if_v2_seconds_to_close>=600_AND_score_min_book_rv15<=0.6` | 881.0c/-840.0c | 1078.0c/72.54%/90.37% | 443.0c/71.70%/95.93% | 4.08% |
| 20 | `wait_for_book_margin_if_v2_seconds_to_close>=600_AND_book_p_side<=0.6` | 843.0c/-837.0c | 1040.0c/72.16%/94.44% | 446.0c/71.63%/97.29% | 5.85% |
| 21 | `wait_for_score_min60_if_v2_seconds_to_close>=720` | 887.0c/-890.0c | 1084.0c/74.91%/98.89% | 393.0c/72.94%/98.64% | 0.39% |
| 22 | `wait_for_score_min60_if_v2_seconds_to_close>=720_AND_score_min_book_rv15<=0.6` | 887.0c/-890.0c | 1084.0c/74.91%/98.89% | 393.0c/72.94%/98.64% | 0.39% |
| 23 | `wait_for_score_min60_if_v2_seconds_to_close>=720_AND_score_min_book_rv15<=0.65` | 887.0c/-890.0c | 1084.0c/74.91%/98.89% | 393.0c/72.94%/98.64% | 0.39% |
| 24 | `wait_for_score_min60_if_v2_seconds_to_close>=720_AND_score_min_book_rv15<=0.7` | 887.0c/-890.0c | 1084.0c/74.91%/98.89% | 393.0c/72.94%/98.64% | 0.39% |
| 25 | `wait_for_score_min60_if_v2_seconds_to_close>=720_AND_score_min_book_rv15<=0.75` | 887.0c/-890.0c | 1084.0c/74.91%/98.89% | 393.0c/72.94%/98.64% | 0.39% |

## Read

- Best rich wait row: `wait_for_score_min60_if_v2_seconds_to_close>=600_AND_brownian_p_rv_15m<=0.7` with current/v21 delta 1163.0c/-528.0c.
- This is a diagnostic candidate for forward-lock consideration, not promotion evidence.
