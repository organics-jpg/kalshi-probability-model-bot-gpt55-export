# Late-Resampled Frontier Scan

Generated UTC: `20260503_194123Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Tests whether delaying first eligibility by a max seconds-to-close boundary improves the high-coverage Brownian/book frontier.
- The scan is diagnostic only; any candidate needs a separate forward lock and strict pre-resolution capture.

## Summary

- Policies scanned: 960
- Both-dataset 80% coverage policies: 422
- Both-dataset OOS-positive policies: 0

## Top Rows

| rank | policy | current net/acc/cov | v21 net/acc/cov | OOS ROI floor | BE edge floor |
|---:|---|---:|---:|---:|---:|
| 1 | `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.55; ask<=70; 120<=sec_to_close<=900` | 377.0c/62.18%/95.58% | 1413.0c/67.14%/95.02% | -6.45% | -0.039 |
| 2 | `choose=score_min_book_rv15; score_min_book_rv15>=0.60; ask<=95; 120<=sec_to_close<=900` | 1083.0c/75.61%/98.80% | 534.0c/73.85%/98.64% | -3.45% | -0.025 |
| 3 | `choose=score_min_book_rv15; score_min_book_rv15>=0.60; ask<=90; 120<=sec_to_close<=900` | 1078.0c/75.51%/98.39% | 514.0c/73.49%/97.29% | -3.45% | -0.025 |
| 4 | `choose=score_min_book_rv15; score_min_book_rv15>=0.60; ask<=80; 120<=sec_to_close<=900` | 1066.0c/75.10%/96.79% | 519.0c/72.73%/94.57% | -3.41% | -0.024 |
| 5 | `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.55; ask<=95; 120<=sec_to_close<=900` | 279.0c/63.16%/99.20% | 1283.0c/68.04%/99.10% | -7.99% | -0.050 |
| 6 | `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.55; ask<=90; 120<=sec_to_close<=900` | 279.0c/63.16%/99.20% | 1276.0c/67.89%/98.64% | -7.99% | -0.050 |
| 7 | `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.55; ask<=80; 120<=sec_to_close<=900` | 269.0c/63.01%/98.80% | 1271.0c/67.59%/97.74% | -7.99% | -0.050 |
| 8 | `choose=score_min_book_rv15; score_min_book_rv15>=0.60; ask<=95; 120<=sec_to_close<=840` | 1019.0c/75.61%/98.80% | 496.0c/73.85%/98.64% | -3.82% | -0.028 |
| 9 | `choose=score_min_book_rv15; score_min_book_rv15>=0.60; ask<=90; 120<=sec_to_close<=840` | 1014.0c/75.51%/98.39% | 476.0c/73.49%/97.29% | -3.82% | -0.028 |
| 10 | `choose=score_min_book_rv15; score_min_book_rv15>=0.60; ask<=80; 120<=sec_to_close<=840` | 995.0c/75.00%/96.39% | 481.0c/72.73%/94.57% | -3.74% | -0.027 |
| 11 | `choose=score_min_book_rv15; score_min_book_rv15>=0.55; ask<=70; 120<=sec_to_close<=900` | 374.0c/66.09%/93.57% | 995.0c/69.08%/93.67% | -13.54% | -0.088 |
| 12 | `choose=score_min_book_rv15; score_min_book_rv15>=0.55; ask<=95; 120<=sec_to_close<=900` | 489.0c/68.02%/99.20% | 832.0c/69.86%/99.10% | -8.12% | -0.055 |
| 13 | `choose=score_min_book_rv15; score_min_book_rv15>=0.55; ask<=90; 120<=sec_to_close<=900` | 489.0c/68.02%/99.20% | 825.0c/69.72%/98.64% | -8.12% | -0.055 |
| 14 | `choose=book_p_side; book_p_side>=0.60; ask<=70; 120<=sec_to_close<=900` | 510.0c/67.78%/95.98% | 803.0c/70.65%/90.95% | -9.06% | -0.059 |
| 15 | `choose=score_min_book_rv15; score_min_book_rv15>=0.55; ask<=80; 120<=sec_to_close<=900` | 479.0c/67.89%/98.80% | 820.0c/69.44%/97.74% | -8.12% | -0.055 |
| 16 | `choose=book_p_side; book_p_side>=0.60; ask<=70; 120<=sec_to_close<=840` | 749.0c/69.26%/92.77% | 510.0c/69.59%/87.78% | -7.08% | -0.047 |
| 17 | `choose=brownian_p_rv_30m; brownian_p_rv_30m>=0.65; ask<=95; 120<=sec_to_close<=900` | 724.0c/77.37%/97.59% | 490.0c/76.85%/97.74% | -13.65% | -0.103 |
| 18 | `choose=brownian_p_rv_30m; brownian_p_rv_30m>=0.55; ask<=70; 120<=sec_to_close<=900` | 31.0c/60.76%/95.18% | 1153.0c/66.35%/95.48% | -6.10% | -0.037 |
| 19 | `choose=brownian_p_rv_30m; brownian_p_rv_30m>=0.65; ask<=90; 120<=sec_to_close<=900` | 702.0c/76.99%/95.98% | 462.0c/76.42%/95.93% | -13.65% | -0.103 |
| 20 | `choose=brownian_p_rv_30m; brownian_p_rv_30m>=0.65; ask<=80; 120<=sec_to_close<=900` | 591.0c/74.89%/87.95% | 433.0c/74.61%/87.33% | -16.28% | -0.119 |

## Read

- Best diagnostic row: `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.55; ask<=70; 120<=sec_to_close<=900` with current/v21 net 377.0c/1413.0c.
- Treat this as a candidate generator, not promotion evidence; strict live registration still decides.
