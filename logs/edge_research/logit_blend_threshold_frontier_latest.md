# Logit Blend Threshold Frontier

Generated UTC: `20260504_065146Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Tests whether the logit book/RV/hazard blend needs a minimum physical-probability gate instead of pure cheap-price fair edge.
- Strict coverage target: `80.00%`; loose diagnostic floor: `75.00%`.

## Diagnostics

- Current markets: 295
- V21 markets: 221
- Rows scanned: 25
- Strict positive OOS rows: 3

## Top Rows

| policy | combined net | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | min OOS cov | OOS positive | strict cov |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-10c; ask<=95; sec>=60` | 2116.0c | 1307.0c/6.32% | 75.60%/98.64% | 809.0c/5.19% | 75.93%/97.74% | 95.56% | True | True |
| `blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60` | 1689.0c | 1136.0c/5.52% | 74.32%/98.98% | 553.0c/3.60% | 72.94%/98.64% | 97.78% | True | True |
| `blend_logit_book_rv_hazard_mean>=0.65; fair_edge>=-10c; ask<=95; sec>=60` | 532.0c | 490.0c/2.22% | 81.29%/94.24% | 42.0c/0.25% | 80.09%/95.48% | 91.11% | True | True |
| `blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-5c; ask<=95; sec>=60` | 878.0c | 423.0c/2.06% | 75.54%/94.24% | 455.0c/3.63% | 83.33%/70.59% | 68.18% | True | False |
| `blend_logit_book_rv_hazard_mean>=0.60; fair_edge>=-5c; ask<=95; sec>=60` | 803.0c | 619.0c/3.04% | 80.77%/88.14% | 184.0c/1.47% | 83.55%/68.78% | 66.67% | True | False |
| `blend_logit_book_rv_hazard_mean>=0.65; fair_edge>=-5c; ask<=95; sec>=60` | 719.0c | 582.0c/2.85% | 83.67%/85.08% | 137.0c/1.09% | 85.23%/67.42% | 64.44% | True | False |
| `blend_logit_book_rv_hazard_mean>=0.60; fair_edge>=0c; ask<=95; sec>=60` | 510.0c | 188.0c/1.51% | 78.75%/54.24% | 322.0c/10.13% | 94.59%/16.74% | 15.91% | True | False |
| `blend_logit_book_rv_hazard_mean>=0.45; fair_edge>=-5c; ask<=95; sec>=60` | 499.0c | 220.0c/1.14% | 69.50%/95.59% | 279.0c/2.23% | 78.05%/74.21% | 68.89% | True | False |
| `blend_logit_book_rv_hazard_mean>=0.45; fair_edge>=0c; ask<=95; sec>=60` | 393.0c | 169.0c/1.27% | 71.43%/64.07% | 224.0c/6.26% | 84.44%/20.36% | 18.18% | True | False |
| `blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=0c; ask<=95; sec>=60` | 385.0c | 75.0c/0.58% | 75.58%/58.31% | 310.0c/9.42% | 92.31%/17.65% | 15.91% | True | False |
| `blend_logit_book_rv_hazard_mean>=0.50; fair_edge>=-5c; ask<=95; sec>=60` | 178.0c | -57.0c/-0.29% | 70.00%/94.92% | 235.0c/1.84% | 79.75%/73.76% | 68.89% | True | False |
| `blend_logit_book_rv_hazard_mean>=0.60; fair_edge>=-10c; ask<=95; sec>=60` | 1215.0c | 774.0c/3.60% | 78.25%/96.61% | 441.0c/2.71% | 78.40%/96.38% | 93.33% | False | True |
| `blend_logit_book_rv_hazard_mean>=0.60; fair_edge>=-15c; ask<=95; sec>=60` | 1096.0c | 809.0c/3.73% | 77.59%/98.31% | 287.0c/1.75% | 76.96%/98.19% | 97.78% | False | True |
| `blend_logit_book_rv_hazard_mean>=0.45; fair_edge>=-15c; ask<=95; sec>=60` | 837.0c | -26.0c/-0.14% | 61.90%/99.66% | 863.0c/6.33% | 65.91%/99.55% | 98.31% | False | True |
| `blend_logit_book_rv_hazard_mean>=0.45; fair_edge>=-10c; ask<=95; sec>=60` | 451.0c | -109.0c/-0.58% | 63.82%/99.32% | 560.0c/3.93% | 67.58%/99.10% | 97.78% | False | True |

## Read

- Best strict diagnostic row is `blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-10c; ask<=95; sec>=60` with combined all-ledger net 2116.0c.
- Any row from this scan must be forward-locked before use because the scan sees validation/holdout.
