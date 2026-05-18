# Candidate Tradeable Veto Scan

Generated UTC: `20260504_032143Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Tests one-feature vetoes on locked high-coverage candidates while preserving >=80% recurring-market coverage.
- Any apparent winner still needs forward registration and live sample size.

## Summary

- Rules scanned: 168
- Both-dataset 80% coverage rules: 76
- Both-dataset OOS-positive rules: 72

## Top Rows

| rank | rule | delta current/v21 | current net/acc/cov | v21 net/acc/cov | OOS ROI floor |
|---:|---|---:|---:|---:|---:|
| 1 | `book_margin: seconds_to_close>=480` | 30.0c/294.0c | 1167.0c/71.96%/96.44% | 719.0c/72.60%/94.12% | 5.00% |
| 2 | `book_margin: adverse_move_15m<=100` | 115.0c/192.0c | 1252.0c/72.48%/91.81% | 617.0c/72.46%/93.67% | 4.70% |
| 3 | `book_margin: adverse_move_15m<=75` | 129.0c/47.0c | 1266.0c/72.80%/85.05% | 472.0c/72.02%/87.33% | 3.87% |
| 4 | `score_min60: abs_book_rv15_gap<=0.2` | 167.0c/0.0c | 1485.0c/76.81%/98.22% | 534.0c/73.85%/98.64% | 0.60% |
| 5 | `v2_wait_score_min60_early: abs_book_rv15_gap<=0.2` | 167.0c/0.0c | 1504.0c/76.81%/98.22% | 558.0c/73.85%/98.64% | 0.60% |
| 6 | `book_margin: abs_book_rv15_gap<=0.15` | 279.0c/-119.0c | 1416.0c/72.40%/88.97% | 306.0c/70.56%/96.83% | 3.55% |
| 7 | `book_margin: seconds_to_close>=360` | 38.0c/118.0c | 1175.0c/71.84%/98.58% | 543.0c/71.63%/97.29% | 6.67% |
| 8 | `book_margin: seconds_to_close>=240` | 67.0c/58.0c | 1204.0c/71.94%/98.93% | 483.0c/71.43%/98.19% | 6.67% |
| 9 | `book_margin: seconds_to_close>=600` | -143.0c/245.0c | 994.0c/71.43%/92.17% | 670.0c/72.49%/85.52% | 4.82% |
| 10 | `v2_wait_score_min60_early: seconds_to_close<=840` | -36.0c/136.0c | 1301.0c/76.60%/94.31% | 694.0c/74.88%/93.67% | 3.04% |
| 11 | `score_min60: seconds_to_close<=840` | -36.0c/136.0c | 1282.0c/76.60%/94.31% | 670.0c/74.88%/93.67% | 2.89% |
| 12 | `book_margin: abs_book_rv15_gap<=0.2` | 155.0c/-57.0c | 1292.0c/71.96%/96.44% | 368.0c/70.83%/97.74% | 6.18% |
| 13 | `book_margin: adverse_move_15m<=125` | 186.0c/-105.0c | 1323.0c/72.56%/94.66% | 320.0c/70.89%/96.38% | 5.61% |
| 14 | `score_min60: adverse_move_15m<=75` | 57.0c/19.0c | 1375.0c/76.89%/89.32% | 553.0c/74.37%/90.05% | 1.48% |
| 15 | `v2_wait_score_min60_early: adverse_move_15m<=75` | 57.0c/19.0c | 1394.0c/76.89%/89.32% | 577.0c/74.37%/90.05% | 1.48% |
| 16 | `score_min60: adverse_move_15m<=100` | 41.0c/21.0c | 1359.0c/76.60%/94.31% | 555.0c/74.06%/95.93% | 1.39% |
| 17 | `v2_wait_score_min60_early: adverse_move_15m<=100` | 41.0c/21.0c | 1378.0c/76.60%/94.31% | 579.0c/74.06%/95.93% | 1.39% |
| 18 | `score_min60: seconds_to_close>=240` | 35.0c/-7.0c | 1353.0c/76.36%/97.86% | 527.0c/73.73%/98.19% | 0.60% |
| 19 | `v2_wait_score_min60_early: seconds_to_close>=240` | 35.0c/-7.0c | 1372.0c/76.36%/97.86% | 551.0c/73.73%/98.19% | 0.60% |
| 20 | `score_min60: adverse_move_15m<=125` | 97.0c/-79.0c | 1415.0c/76.78%/95.02% | 455.0c/73.49%/97.29% | 2.15% |
| 21 | `v2_wait_score_min60_early: adverse_move_15m<=125` | 97.0c/-79.0c | 1434.0c/76.78%/95.02% | 479.0c/73.49%/97.29% | 2.15% |
| 22 | `score_min60: spread_cents<=2` | 10.0c/0.0c | 1328.0c/76.36%/97.86% | 534.0c/73.85%/98.64% | 0.60% |
| 23 | `v2_wait_score_min60_early: spread_cents<=2` | 10.0c/0.0c | 1347.0c/76.36%/97.86% | 558.0c/73.85%/98.64% | 0.60% |
| 24 | `book_margin: none` | 0.0c/0.0c | 1137.0c/71.68%/99.29% | 425.0c/71.23%/99.10% | 6.67% |
| 25 | `book_margin: book_p_side>=0.55` | 0.0c/0.0c | 1137.0c/71.68%/99.29% | 425.0c/71.23%/99.10% | 6.67% |

## Read

- Best veto row: `book_margin: seconds_to_close>=480` with current/v21 delta 30.0c/294.0c.
- Worth forward-lock consideration only if the rule is physically interpretable and live coverage remains high.
