# Hazard Fallback Frontier

Generated UTC: `20260504_073459Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Uses hazard-mean touch80 as primary; if it skips a market, tries a high-coverage fallback.
- Any passing row must be forward-locked before use.

## Diagnostics

- Current markets: 295
- V21 markets: 221
- Rows scanned: 7
- Strict positive OOS rows: 5

## Rows

| policy | combined net | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | min OOS cov | OOS positive | strict cov |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `hazard_primary_else_logit_thresh55_edge15: blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60` | 2035.0c | 1113.0c/5.30% | 75.68%/98.98% | 922.0c/5.92% | 75.69%/98.64% | 97.78% | True | True |
| `hazard_primary_else_logit_thresh55_edge15_wait8m: blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=480` | 1928.0c | 1016.0c/4.89% | 75.43%/97.97% | 912.0c/5.97% | 75.70%/96.83% | 96.61% | True | True |
| `hazard_primary_else_score_min60: score_min_book_rv15>=0.6; ask<=95; sec>=60` | 1912.0c | 1104.0c/5.26% | 75.68%/98.98% | 808.0c/5.15% | 75.34%/99.10% | 97.78% | True | True |
| `hazard_primary_else_logit_thresh55_edge15_wait10m: blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=600` | 1829.0c | 961.0c/4.59% | 75.26%/98.64% | 868.0c/5.55% | 75.69%/98.64% | 97.78% | True | True |
| `hazard_primary_else_logit_thresh55_edge15_wait6m: blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=360` | 1804.0c | 951.0c/4.61% | 75.26%/97.29% | 853.0c/5.59% | 75.59%/96.38% | 95.56% | True | True |
| `hazard_primary_else_book60: book_p_side>=0.6; ask<=95; sec>=60` | 1749.0c | 1070.0c/5.09% | 75.17%/99.66% | 679.0c/4.32% | 74.21%/100.00% | 98.31% | False | True |
| `hazard_primary_else_logit_edge10: blend_logit_book_rv_hazard_mean>=0; fair_edge>=-10c; ask<=95; sec>=60` | 1472.0c | 722.0c/3.46% | 73.72%/99.32% | 750.0c/4.82% | 74.43%/99.10% | 97.78% | False | True |

## Read

- Best strict diagnostic row is `hazard_primary_else_logit_thresh55_edge15: blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60` with combined all-ledger net 2035.0c.
