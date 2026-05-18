# Causal Hazard Fallback Frontier

Generated UTC: `20260504_090525Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Scores the first eligible primary/fallback signal by timestamp per market.
- Noncausal gap is the extra P&L shown by the earlier optimistic scan that let later hazard suppress earlier fallback.

## Diagnostics

- Current markets: 295
- V21 markets: 221
- Rows scanned: 7
- Strict positive OOS rows: 6

## Rows

| policy | causal combined net | noncausal gap | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | min OOS cov | fallback-before-primary current/v21 | OOS positive | strict cov |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `hazard_primary_else_score_min60: score_min_book_rv15>=0.6; ask<=95; sec>=60` | 1964.0c | -52.0c | 1268.0c/6.12% | 75.34%/98.98% | 696.0c/4.49% | 73.97%/99.10% | 97.78% | 67/48 | True | True |
| `hazard_primary_else_logit_thresh55_edge15_wait10m: blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=600` | 1774.0c | 55.0c | 861.0c/4.11% | 74.91%/98.64% | 913.0c/5.86% | 75.69%/98.64% | 97.78% | 18/13 | True | True |
| `hazard_primary_else_logit_thresh55_edge15_wait8m: blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=480` | 1761.0c | 167.0c | 988.0c/4.75% | 75.43%/97.97% | 773.0c/5.04% | 75.23%/96.83% | 96.61% | 7/8 | True | True |
| `hazard_primary_else_logit_thresh55_edge15_wait6m: blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=360` | 1754.0c | 50.0c | 934.0c/4.52% | 75.26%/97.29% | 820.0c/5.37% | 75.59%/96.38% | 95.56% | 4/4 | True | True |
| `hazard_primary_else_logit_thresh55_edge15: blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60` | 1671.0c | 364.0c | 1118.0c/5.43% | 74.32%/98.98% | 553.0c/3.60% | 72.94%/98.64% | 97.78% | 103/51 | True | True |
| `hazard_primary_else_logit_edge10: blend_logit_book_rv_hazard_mean>=0; fair_edge>=-10c; ask<=95; sec>=60` | 750.0c | 722.0c | 148.0c/0.82% | 62.12%/99.32% | 602.0c/4.39% | 65.30%/99.10% | 97.78% | 176/127 | True | True |
| `hazard_primary_else_book60: book_p_side>=0.6; ask<=95; sec>=60` | 1306.0c | 443.0c | 787.0c/4.03% | 69.05%/99.66% | 519.0c/3.42% | 71.04%/100.00% | 98.31% | 252/99 | False | True |

## Read

- Best strict causal row is `hazard_primary_else_score_min60: score_min_book_rv15>=0.6; ask<=95; sec>=60` with combined all-ledger net 1964.0c.
- Largest current noncausal optimism gap is `hazard_primary_else_logit_edge10: blend_logit_book_rv_hazard_mean>=0; fair_edge>=-10c; ask<=95; sec>=60` at 574.0c current / 148.0c v21.
