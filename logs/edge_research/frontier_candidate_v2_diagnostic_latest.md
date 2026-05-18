# Frontier Candidate vs V2 Diagnostic

Generated UTC: `20260504_090342Z`

## Scope

- Research-only diagnostic; no orders are submitted and no bot files or live processes are touched.
- Compares refreshed book/score forward candidates against the older Brownian v2 lock.
- Uses the current two-sided heartbeat ledger and the independent v21 ledger.

## Policy Metrics

| dataset | policy | all net/ROI | all acc/cov | holdout net/acc/cov | median ask |
|---|---|---:|---:|---:|---:|
| current | `frontier_v2` | 20.0c/0.11% | 62.80%/99.32% | -468.0c/57.63%/100.00% | 61.0c |
| current | `book_margin` | 988.0c/4.99% | 70.99%/99.32% | 252.0c/72.88%/100.00% | 64.0c |
| current | `book_margin_early` | 1018.0c/5.28% | 71.23%/96.61% | 252.0c/72.88%/100.00% | 64.0c |
| current | `book_margin_gap015` | 1267.0c/7.19% | 71.59%/89.49% | 83.0c/69.23%/88.14% | 63.0c |
| current | `score_min60` | 1227.0c/5.88% | 75.68%/98.98% | 97.0c/74.58%/100.00% | 68.0c |
| current | `score_min60_gap020` | 1394.0c/6.73% | 76.21%/98.31% | 97.0c/74.58%/100.00% | 68.0c |
| v21 | `frontier_v2` | 1283.0c/9.42% | 68.04%/99.10% | 620.0c/77.27%/97.78% | 60.0c |
| v21 | `book_margin` | 425.0c/2.80% | 71.23%/99.10% | 293.0c/77.27%/97.78% | 66.0c |
| v21 | `book_margin_early` | 719.0c/5.00% | 72.60%/94.12% | 250.0c/76.19%/93.33% | 66.0c |
| v21 | `book_margin_gap015` | 306.0c/2.07% | 70.56%/96.83% | 259.0c/76.19%/93.33% | 65.5c |
| v21 | `score_min60` | 534.0c/3.43% | 73.85%/98.64% | 155.0c/77.27%/97.78% | 68.0c |
| v21 | `score_min60_gap020` | 534.0c/3.43% | 73.85%/98.64% | 155.0c/77.27%/97.78% | 68.0c |

## Paired Deltas Versus V2

| dataset | candidate | bucket | pairs | candidate acc/net | v2 acc/net | candidate-v2 | mean delta |
|---|---|---|---:|---:|---:|---:|---:|
| current | `book_margin` | all_pairs | 293 | 70.99%/988.0c | 62.80%/20.0c | 968.0c | 3.3c |
| current | `book_margin` | same_side | 221 | 72.40%/1015.0c | 72.40%/1529.0c | -514.0c | -2.3c |
| current | `book_margin` | disagree | 72 | 66.67%/-27.0c | 33.33%/-1509.0c | 1482.0c | 20.6c |
| current | `book_margin_early` | all_pairs | 285 | 71.23%/1018.0c | 63.16%/86.0c | 932.0c | 3.3c |
| current | `book_margin_early` | same_side | 218 | 72.48%/1008.0c | 72.48%/1504.0c | -496.0c | -2.3c |
| current | `book_margin_early` | disagree | 67 | 67.16%/10.0c | 32.84%/-1418.0c | 1428.0c | 21.3c |
| current | `book_margin_gap015` | all_pairs | 264 | 71.59%/1267.0c | 62.50%/78.0c | 1189.0c | 4.5c |
| current | `book_margin_gap015` | same_side | 200 | 72.50%/1109.0c | 72.50%/1573.0c | -464.0c | -2.3c |
| current | `book_margin_gap015` | disagree | 64 | 68.75%/158.0c | 31.25%/-1495.0c | 1653.0c | 25.8c |
| current | `score_min60` | all_pairs | 292 | 75.68%/1227.0c | 62.67%/-17.0c | 1244.0c | 4.3c |
| current | `score_min60` | same_side | 218 | 75.69%/863.0c | 75.69%/2258.0c | -1395.0c | -6.4c |
| current | `score_min60` | disagree | 74 | 75.68%/364.0c | 24.32%/-2275.0c | 2639.0c | 35.7c |
| current | `score_min60_gap020` | all_pairs | 290 | 76.21%/1394.0c | 63.10%/130.0c | 1264.0c | 4.4c |
| current | `score_min60_gap020` | same_side | 216 | 76.39%/1030.0c | 76.39%/2405.0c | -1375.0c | -6.4c |
| current | `score_min60_gap020` | disagree | 74 | 75.68%/364.0c | 24.32%/-2275.0c | 2639.0c | 35.7c |
| v21 | `book_margin` | all_pairs | 219 | 71.23%/425.0c | 68.04%/1283.0c | -858.0c | -3.9c |
| v21 | `book_margin` | same_side | 162 | 76.54%/1177.0c | 76.54%/1834.0c | -657.0c | -4.1c |
| v21 | `book_margin` | disagree | 57 | 56.14%/-752.0c | 43.86%/-551.0c | -201.0c | -3.5c |
| v21 | `book_margin_early` | all_pairs | 208 | 72.60%/719.0c | 68.27%/1209.0c | -490.0c | -2.4c |
| v21 | `book_margin_early` | same_side | 157 | 77.07%/1236.0c | 77.07%/1819.0c | -583.0c | -3.7c |
| v21 | `book_margin_early` | disagree | 51 | 58.82%/-517.0c | 41.18%/-610.0c | 93.0c | 1.8c |
| v21 | `book_margin_gap015` | all_pairs | 214 | 70.56%/306.0c | 67.76%/1254.0c | -948.0c | -4.4c |
| v21 | `book_margin_gap015` | same_side | 158 | 75.95%/1094.0c | 75.95%/1749.0c | -655.0c | -4.1c |
| v21 | `book_margin_gap015` | disagree | 56 | 55.36%/-788.0c | 44.64%/-495.0c | -293.0c | -5.2c |
| v21 | `score_min60` | all_pairs | 218 | 73.85%/534.0c | 67.89%/1237.0c | -703.0c | -3.2c |
| v21 | `score_min60` | same_side | 159 | 78.62%/1115.0c | 78.62%/2136.0c | -1021.0c | -6.4c |
| v21 | `score_min60` | disagree | 59 | 61.02%/-581.0c | 38.98%/-899.0c | 318.0c | 5.4c |
| v21 | `score_min60_gap020` | all_pairs | 218 | 73.85%/534.0c | 67.89%/1237.0c | -703.0c | -3.2c |
| v21 | `score_min60_gap020` | same_side | 159 | 78.62%/1115.0c | 78.62%/2136.0c | -1021.0c | -6.4c |
| v21 | `score_min60_gap020` | disagree | 59 | 61.02%/-581.0c | 38.98%/-899.0c | 318.0c | 5.4c |

## Read

- `book_margin` paired delta current/v21: 968.0c/-858.0c versus v2.
- `book_margin_early` paired delta current/v21: 932.0c/-490.0c versus v2.
- `book_margin_gap015` paired delta current/v21: 1189.0c/-948.0c versus v2.
- `score_min60` paired delta current/v21: 1244.0c/-703.0c versus v2.
- `score_min60_gap020` paired delta current/v21: 1264.0c/-703.0c versus v2.
- A candidate that fixes current v2 failures but gives back too much v21 edge is a forward-test candidate, not a replacement.
- Promotion still requires strict pre-resolution live sample size and >=80% recurring-market coverage.
