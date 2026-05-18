# Candidate Tradeable Delayed Path-Veto Scan

Generated UTC: `20260504_040839Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Tests delayed entry within each market rather than skipping after the first path-veto failure.
- Every row still must satisfy the locked candidate's original book/price/time gate.
- Any apparent winner still needs strict pre-resolution forward registration and sample size.

## Summary

- Rules scanned: 546
- Both-dataset 80% coverage rules: 394
- Both-dataset OOS-positive rules: 229
- Diagnostic pass rules: 0

## Top Rows

| rank | rule | diagnostic | delta current/v21 | current net/acc/cov | v21 net/acc/cov | OOS ROI floor | block pass | worst block | median delay cur/v21 |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `book_margin_early: wait until adverse_move_15m<=100 AND brownian_p_rv_15m>=0.55` | False | 430.0c/164.0c | 1588.0c/75.09%/93.31% | 883.0c/74.02%/92.31% | 6.15% | 54.55% | -327.0c | 0.0s/0.0s |
| 2 | `book_margin_early: wait until adverse_move_15m<=100 AND margin_per_rv_sigma_15m>=0.1` | False | 428.0c/75.0c | 1586.0c/74.91%/94.01% | 794.0c/73.53%/92.31% | 4.61% | 54.55% | -327.0c | 0.0s/0.0s |
| 3 | `book_margin_early: wait until adverse_move_15m<=100 AND signed_move_5m>=0` | False | 282.0c/172.0c | 1440.0c/74.91%/94.01% | 891.0c/74.75%/91.40% | 4.51% | 54.55% | -251.0c | 0.0s/0.0s |
| 4 | `book_margin_early: wait until adverse_move_15m<=100 AND abs_book_rv15_gap<=0.1` | False | 244.0c/202.0c | 1402.0c/73.51%/94.37% | 921.0c/74.38%/91.86% | 1.65% | 72.73% | -344.0c | 0.0s/0.0s |
| 5 | `book_margin_early: wait until adverse_move_15m<=150 AND brownian_p_rv_15m>=0.55` | False | 204.0c/-75.0c | 1362.0c/74.06%/93.66% | 644.0c/72.68%/92.76% | 6.53% | 54.55% | -323.0c | 0.0s/0.0s |
| 6 | `book_margin_early: wait until adverse_move_15m<=100 AND margin_per_rv_sigma_15m>=0.25` | False | 105.0c/20.0c | 1263.0c/76.40%/88.03% | 739.0c/74.87%/90.05% | 4.99% | 63.64% | -276.0c | 22.5s/0.0s |
| 7 | `book_margin_early: wait until adverse_move_15m<=100 AND brownian_p_rv_15m>=0.6` | False | 77.0c/16.0c | 1235.0c/76.40%/88.03% | 735.0c/74.87%/90.05% | 4.89% | 57.14% | -276.0c | 30.0s/0.0s |
| 8 | `book_margin_early: wait until adverse_move_15m<=75 AND signed_move_5m>=0` | False | -157.0c/223.0c | 1001.0c/73.48%/92.96% | 942.0c/75.25%/91.40% | 0.78% | 54.55% | -255.0c | 0.0s/0.0s |
| 9 | `book_margin_early: wait until adverse_move_15m<=150 AND margin_per_rv_sigma_15m>=0.1` | False | 211.0c/-164.0c | 1369.0c/73.88%/94.37% | 555.0c/72.20%/92.76% | 5.23% | 54.55% | -323.0c | 0.0s/0.0s |
| 10 | `book_margin_early: wait until adverse_move_15m<=150 AND abs_book_rv15_gap<=0.1` | False | 45.0c/-40.0c | 1203.0c/72.49%/94.72% | 679.0c/73.04%/92.31% | 2.27% | 71.43% | -340.0c | 0.0s/0.0s |
| 11 | `book_margin_early: no extra delay clause` | False | 0.0c/0.0c | 1158.0c/71.90%/96.48% | 719.0c/72.60%/94.12% | 3.18% | 63.64% | -315.0c | 0.0s/0.0s |
| 12 | `book_margin_early: wait until adverse_move_15m<=75 AND margin_per_rv_sigma_15m>=0.1` | False | 37.0c/-37.0c | 1195.0c/73.76%/92.61% | 682.0c/73.40%/91.86% | 0.98% | 45.45% | -327.0c | 0.0s/0.0s |
| 13 | `book_margin_early: wait until adverse_move_15m<=150 AND signed_move_5m>=0` | False | 52.0c/-55.0c | 1210.0c/73.88%/94.37% | 664.0c/73.40%/91.86% | 4.51% | 63.64% | -251.0c | 0.0s/0.0s |
| 14 | `book_margin_early: wait until adverse_move_15m<=150 AND margin_per_rv_sigma_15m>=0.25` | False | 28.0c/-54.0c | 1186.0c/76.00%/88.03% | 665.0c/74.37%/90.05% | 5.07% | 63.64% | -270.0c | 22.5s/0.0s |
| 15 | `book_margin_early: wait until adverse_move_15m<=150` | False | -33.0c/-20.0c | 1125.0c/71.96%/95.42% | 699.0c/72.68%/92.76% | 0.46% | 63.64% | -315.0c | 0.0s/0.0s |
| 16 | `book_margin_early: wait until adverse_move_15m<=150 AND brownian_p_rv_15m>=0.5` | False | -33.0c/-20.0c | 1125.0c/71.96%/95.42% | 699.0c/72.68%/92.76% | 0.46% | 63.64% | -315.0c | 0.0s/0.0s |
| 17 | `book_margin_early: wait until adverse_move_15m<=150 AND margin_per_rv_sigma_15m>=0` | False | -33.0c/-20.0c | 1125.0c/71.96%/95.42% | 699.0c/72.68%/92.76% | 0.46% | 63.64% | -315.0c | 0.0s/0.0s |
| 18 | `book_margin_early: wait until adverse_move_15m<=150 AND spread_cents<=4` | False | -33.0c/-20.0c | 1125.0c/71.96%/95.42% | 699.0c/72.68%/92.76% | 0.46% | 63.64% | -315.0c | 0.0s/0.0s |
| 19 | `book_margin_early: wait until adverse_move_15m<=150 AND ask_cents<=95` | False | -33.0c/-20.0c | 1125.0c/71.96%/95.42% | 699.0c/72.68%/92.76% | 0.46% | 63.64% | -315.0c | 0.0s/0.0s |
| 20 | `book_margin_early: wait until adverse_move_15m<=150 AND abs_book_rv15_gap<=0.3` | False | -34.0c/-20.0c | 1124.0c/71.96%/95.42% | 699.0c/72.68%/92.76% | 0.46% | 63.64% | -315.0c | 0.0s/0.0s |
| 21 | `book_margin_early: wait until adverse_move_15m<=150 AND ask_cents<=85` | False | -18.0c/-37.0c | 1140.0c/71.96%/95.42% | 682.0c/72.41%/91.86% | 0.46% | 63.64% | -315.0c | 0.0s/0.0s |
| 22 | `book_margin_early: wait until adverse_move_15m<=150 AND abs_book_rv15_gap<=0.2` | False | -25.0c/-31.0c | 1133.0c/71.96%/95.42% | 688.0c/72.68%/92.76% | 0.41% | 63.64% | -323.0c | 0.0s/0.0s |
| 23 | `book_margin_early: wait until adverse_move_15m<=150 AND ask_cents<=90` | False | -33.0c/-27.0c | 1125.0c/71.96%/95.42% | 692.0c/72.55%/92.31% | 0.46% | 63.64% | -315.0c | 0.0s/0.0s |
| 24 | `book_margin_early: wait until adverse_move_15m<=150 AND brownian_p_rv_15m>=0.6` | False | 0.0c/-62.0c | 1158.0c/76.00%/88.03% | 657.0c/74.37%/90.05% | 4.97% | 63.64% | -274.0c | 30.0s/0.0s |
| 25 | `book_margin_early: wait until adverse_move_15m<=100 AND signed_move_5m>=10` | False | 68.0c/-144.0c | 1226.0c/75.29%/92.61% | 575.0c/73.87%/90.05% | 3.04% | 54.55% | -291.0c | 0.0s/0.0s |
| 26 | `book_margin_early: wait until adverse_move_15m<=150 AND spread_cents<=2` | False | -32.0c/-49.0c | 1126.0c/71.96%/95.42% | 670.0c/72.68%/92.76% | 0.46% | 63.64% | -315.0c | 0.0s/0.0s |
| 27 | `book_margin: wait until adverse_move_15m<=50 AND signed_move_5m>=0` | False | -371.0c/223.0c | 757.0c/73.12%/98.24% | 648.0c/74.54%/97.74% | 3.64% | 63.64% | -396.0c | 0.0s/0.0s |
| 28 | `book_margin: wait until signed_move_5m>=0 AND signed_move_15m>=-50` | False | -371.0c/223.0c | 757.0c/73.12%/98.24% | 648.0c/74.54%/97.74% | 3.64% | 63.64% | -396.0c | 0.0s/0.0s |
| 29 | `book_margin_early: wait until adverse_move_15m<=50 AND signed_move_5m>=0` | False | -325.0c/70.0c | 833.0c/73.36%/91.20% | 789.0c/75.51%/88.69% | 0.17% | 54.55% | -216.0c | 0.0s/0.0s |
| 30 | `book_margin_early: wait until signed_move_5m>=0 AND signed_move_15m>=-50` | False | -325.0c/70.0c | 833.0c/73.36%/91.20% | 789.0c/75.51%/88.69% | 0.17% | 54.55% | -216.0c | 0.0s/0.0s |

## Read

- No delayed path-veto rule clears the diagnostic robustness screen.
- Strict registered-signal readiness remains the promotion gate.
