# v32 Blend Executable Frontier

Generated UTC: `2026-05-04T20:06:35.720814+00:00`

## Scope

- Research-only executable frontier for the blended FV posterior.
- First qualifying row per market; no exits; no live orders or bot changes.
- Robust rows below require train/validation/holdout coverage >= 80% and positive net after 2c cost.

## Robust 2c-Cost Rows

| policy | split coverage min | split net min | all net | block10 positive | worst block | train/val/holdout net |
|---|---:|---:|---:|---:|---:|---:|
| `book_time_v33drift85_edge0_ask65_pside0.6_book0` | 80.30% | 144.0c | 1624.0c | 8/10 | -54.0c | 940.0/144.0/540.0c |
| `book_time_v33drift85_edge0_ask65_pside0.6_book0.52` | 80.30% | 144.0c | 1624.0c | 8/10 | -54.0c | 940.0/144.0/540.0c |
| `book_time_v33drift85_edge0_ask65_pside0.6_book0.55` | 80.30% | 144.0c | 1624.0c | 8/10 | -54.0c | 940.0/144.0/540.0c |
| `book_time_v32drift85_edge0_ask65_pside0.55_book0` | 85.86% | 246.0c | 1359.0c | 8/10 | -298.0c | 629.0/246.0/484.0c |
| `book_time_v33drift85_edge0_ask65_pside0.55_book0` | 85.86% | 246.0c | 1258.0c | 8/10 | -298.0c | 528.0/246.0/484.0c |
| `book_time_v32drift85_edge0_ask65_pside0.55_book0.52` | 85.86% | 246.0c | 1350.0c | 8/10 | -300.0c | 627.0/246.0/477.0c |
| `book_time_v33drift85_edge0_ask65_pside0.55_book0.52` | 85.86% | 246.0c | 1249.0c | 8/10 | -300.0c | 526.0/246.0/477.0c |
| `book_time_v33drift85_edge0_ask70_pside0_book0` | 100.00% | 26.0c | 777.0c | 7/10 | -91.0c | 451.0/26.0/300.0c |
| `book_time_v32drift85_edge0_ask65_pside0_book0.55` | 83.33% | 281.0c | 1598.0c | 7/10 | -96.0c | 965.0/281.0/352.0c |
| `book_time_v32drift85_edge0_ask65_pside0.55_book0.55` | 83.33% | 281.0c | 1598.0c | 7/10 | -96.0c | 965.0/281.0/352.0c |
| `book_time_v33drift85_edge0_ask65_pside0_book0.55` | 83.33% | 281.0c | 1497.0c | 7/10 | -96.0c | 864.0/281.0/352.0c |
| `book_time_v33drift85_edge0_ask65_pside0.55_book0.55` | 83.33% | 281.0c | 1497.0c | 7/10 | -96.0c | 864.0/281.0/352.0c |
| `book_time_v33drift85_edge0_ask70_pside0.55_book0` | 90.91% | 74.0c | 972.0c | 7/10 | -118.0c | 617.0/74.0/281.0c |
| `book_time_v33drift85_edge0_ask70_pside0.55_book0.52` | 90.91% | 74.0c | 963.0c | 7/10 | -120.0c | 615.0/74.0/274.0c |
| `book_time_v32drift85_edge0_ask70_pside0.55_book0` | 90.91% | 74.0c | 963.0c | 7/10 | -121.0c | 608.0/74.0/281.0c |
| `book_time_v32drift85_edge0_ask70_pside0.55_book0.52` | 90.91% | 74.0c | 954.0c | 7/10 | -123.0c | 606.0/74.0/274.0c |
| `book_time_v33drift85_edge0_ask70_pside0_book0.6` | 86.36% | 59.0c | 1161.0c | 7/10 | -143.0c | 819.0/59.0/283.0c |
| `book_time_v33drift85_edge0_ask70_pside0.55_book0.6` | 86.36% | 59.0c | 1161.0c | 7/10 | -143.0c | 819.0/59.0/283.0c |
| `book_time_v33drift85_edge0_ask70_pside0.6_book0.6` | 86.36% | 59.0c | 1161.0c | 7/10 | -143.0c | 819.0/59.0/283.0c |
| `book_time_v32drift85_edge0_ask70_pside0_book0.6` | 86.36% | 59.0c | 1151.0c | 7/10 | -143.0c | 809.0/59.0/283.0c |

## Read

- Ask/book-side shaping can improve coverage-adjusted robustness, but this is still a searched frontier.
- Treat any row here as a strict-forward shadow candidate, not a promotion.
