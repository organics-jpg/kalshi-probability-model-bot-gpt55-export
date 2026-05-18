# Causal Touch/Book State Frontier

Generated UTC: `20260504_154516Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Causal rule: trade touch only when touch/book alignment exists at that row; otherwise fall back to book-margin.
- Strict pass requires current+v21 80% split coverage, positive validation/holdout, positive all splits, and block stability.

## Diagnostics

- Current markets: 326
- V21 markets: 221
- Candidate specs: 49
- Strict pass rows: 0

## Top Rows

| policy | strict | combined all net | combined OOS net | min split cov | current/v21 net | current/v21 acc | touch-first current/v21 | min block+ | worst block |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `touch-first + book fallback; touch>= 0.55; touch_ask<=60; book_at_touch>=0.55; sec>=120; margin_rv15>=0` | False | 1732.0c | 758.0c | 97.78% | 1084.0c/648.0c | 70.99%/71.69% | 8/10 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.55; touch_ask<=65; book_at_touch>=0.55; sec>=120; margin_rv15>=0` | False | 1732.0c | 758.0c | 97.78% | 1084.0c/648.0c | 70.99%/71.69% | 38/48 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 1; touch_ask<=0; book_at_touch>=1; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.4; touch_ask<=55; book_at_touch>=0.55; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.4; touch_ask<=55; book_at_touch>=0.6; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.4; touch_ask<=55; book_at_touch>=0.65; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.4; touch_ask<=60; book_at_touch>=0.6; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.4; touch_ask<=60; book_at_touch>=0.65; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.4; touch_ask<=65; book_at_touch>=0.6; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 205/108 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.4; touch_ask<=65; book_at_touch>=0.65; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.45; touch_ask<=55; book_at_touch>=0.55; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.45; touch_ask<=55; book_at_touch>=0.6; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.45; touch_ask<=55; book_at_touch>=0.65; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.45; touch_ask<=60; book_at_touch>=0.6; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.45; touch_ask<=60; book_at_touch>=0.65; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.45; touch_ask<=65; book_at_touch>=0.6; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 205/108 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.45; touch_ask<=65; book_at_touch>=0.65; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.5; touch_ask<=55; book_at_touch>=0.55; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.5; touch_ask<=55; book_at_touch>=0.6; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.5; touch_ask<=55; book_at_touch>=0.65; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.5; touch_ask<=60; book_at_touch>=0.6; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.5; touch_ask<=60; book_at_touch>=0.65; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.5; touch_ask<=65; book_at_touch>=0.6; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 120/90 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.5; touch_ask<=65; book_at_touch>=0.65; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.55; touch_ask<=55; book_at_touch>=0.55; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.55; touch_ask<=55; book_at_touch>=0.6; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.55; touch_ask<=55; book_at_touch>=0.65; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.55; touch_ask<=60; book_at_touch>=0.6; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.55; touch_ask<=60; book_at_touch>=0.65; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 0/0 | 0.625 | -332.0c |
| `touch-first + book fallback; touch>= 0.55; touch_ask<=65; book_at_touch>=0.6; sec>=120; margin_rv15>=0` | False | 1376.0c | 697.0c | 97.78% | 951.0c/425.0c | 70.68%/71.23% | 33/39 | 0.625 | -332.0c |

## Read

- No causal touch/book row clears the full strict gate. Do not promote a row from this scan.
