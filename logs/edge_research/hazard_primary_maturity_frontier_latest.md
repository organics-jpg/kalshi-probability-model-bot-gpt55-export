# Hazard Primary Maturity Frontier

Generated UTC: `20260504_094916Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Tests whether the hazard primary should wait for elapsed path information before acting.
- Any passing row must be forward-locked before use.

## Diagnostics

- Current markets: 305
- V21 markets: 221
- Rows scanned: 35
- Strict positive OOS rows: 20

## Rows

| policy | combined net | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | min OOS cov | OOS positive | strict cov |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `primary=no_cap; fallback=score60:score_min_book_rv15>=0.6; ask<=95; sec>=60` | 1965.0c | 1269.0c/5.92% | 75.17%/99.02% | 696.0c/4.49% | 73.97%/99.10% | 97.78% | True | True |
| `primary=wait30s; sec<=870; fallback=score60:score_min_book_rv15>=0.6; ask<=95; sec>=60` | 1962.0c | 1268.0c/5.92% | 75.17%/99.02% | 694.0c/4.48% | 73.97%/99.10% | 97.78% | True | True |
| `primary=no_cap; fallback=logit55_edge15_wait8m:blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=480` | 1857.0c | 1084.0c/5.04% | 75.59%/98.03% | 773.0c/5.04% | 75.23%/96.83% | 97.78% | True | True |
| `primary=no_cap; fallback=logit55_edge15_wait6m:blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=360` | 1850.0c | 1030.0c/4.82% | 75.42%/97.38% | 820.0c/5.37% | 75.59%/96.38% | 95.56% | True | True |
| `primary=wait30s; sec<=870; fallback=logit55_edge15_wait8m:blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=480` | 1838.0c | 1091.0c/5.07% | 75.59%/98.03% | 747.0c/4.87% | 75.23%/96.83% | 97.78% | True | True |
| `primary=wait30s; sec<=870; fallback=logit55_edge15_wait6m:blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=360` | 1831.0c | 1037.0c/4.85% | 75.42%/97.38% | 794.0c/5.19% | 75.59%/96.38% | 95.56% | True | True |
| `primary=no_cap; fallback=none` | 1816.0c | 1012.0c/4.87% | 75.17%/95.08% | 804.0c/5.55% | 75.00%/92.31% | 88.89% | True | True |
| `primary=wait120s; sec<=780; fallback=score60:score_min_book_rv15>=0.6; ask<=95; sec>=60` | 1799.0c | 1264.0c/5.87% | 75.50%/99.02% | 535.0c/3.44% | 73.52%/99.10% | 97.78% | True | True |
| `primary=wait30s; sec<=870; fallback=none` | 1797.0c | 1019.0c/4.90% | 75.17%/95.08% | 778.0c/5.36% | 75.00%/92.31% | 88.89% | True | True |
| `primary=wait60s; sec<=840; fallback=score60:score_min_book_rv15>=0.6; ask<=95; sec>=60` | 1730.0c | 1185.0c/5.51% | 75.17%/99.02% | 545.0c/3.50% | 73.52%/99.10% | 97.78% | True | True |
| `primary=wait180s; sec<=720; fallback=score60:score_min_book_rv15>=0.6; ask<=95; sec>=60` | 1715.0c | 1240.0c/5.75% | 75.50%/99.02% | 475.0c/3.04% | 73.52%/99.10% | 97.78% | True | True |
| `primary=no_cap; fallback=score60_wait8m:score_min_book_rv15>=0.6; ask<=95; sec>=60; sec<=480` | 1711.0c | 1078.0c/5.01% | 75.59%/98.03% | 633.0c/4.09% | 74.88%/97.29% | 97.78% | True | True |
| `primary=wait90s; sec<=810; fallback=score60:score_min_book_rv15>=0.6; ask<=95; sec>=60` | 1710.0c | 1175.0c/5.46% | 75.17%/99.02% | 535.0c/3.44% | 73.52%/99.10% | 97.78% | True | True |
| `primary=wait30s; sec<=870; fallback=score60_wait8m:score_min_book_rv15>=0.6; ask<=95; sec>=60; sec<=480` | 1692.0c | 1085.0c/5.04% | 75.59%/98.03% | 607.0c/3.92% | 74.88%/97.29% | 97.78% | True | True |
| `primary=wait300s; sec<=600; fallback=score60:score_min_book_rv15>=0.6; ask<=95; sec>=60` | 1668.0c | 1225.0c/5.68% | 75.50%/99.02% | 443.0c/2.83% | 73.52%/99.10% | 97.78% | True | True |
| `primary=wait60s; sec<=840; fallback=logit55_edge15_wait8m:blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=480` | 1450.0c | 875.0c/4.05% | 75.50%/97.70% | 575.0c/3.73% | 74.77%/96.83% | 97.78% | True | True |
| `primary=wait60s; sec<=840; fallback=logit55_edge15_wait6m:blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=360` | 1435.0c | 821.0c/3.82% | 75.34%/97.05% | 614.0c/3.99% | 75.12%/96.38% | 95.56% | True | True |
| `primary=wait60s; sec<=840; fallback=none` | 1393.0c | 803.0c/3.84% | 75.09%/94.75% | 590.0c/4.07% | 74.38%/91.86% | 86.67% | True | True |
| `primary=wait60s; sec<=840; fallback=score60_wait8m:score_min_book_rv15>=0.6; ask<=95; sec>=60; sec<=480` | 1304.0c | 869.0c/4.02% | 75.50%/97.70% | 435.0c/2.79% | 74.42%/97.29% | 97.78% | True | True |
| `primary=wait180s; sec<=720; fallback=logit55_edge15_wait8m:blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=480` | 334.0c | 161.0c/0.75% | 75.26%/94.10% | 173.0c/1.11% | 75.60%/94.57% | 93.44% | True | True |
| `primary=wait90s; sec<=810; fallback=logit55_edge15_wait8m:blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=480` | 856.0c | 876.0c/4.07% | 75.42%/97.38% | -20.0c/-0.13% | 73.21%/94.57% | 95.56% | False | True |
| `primary=wait90s; sec<=810; fallback=logit55_edge15_wait6m:blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=360` | 815.0c | 810.0c/3.80% | 75.17%/96.39% | 5.0c/0.03% | 73.30%/93.21% | 91.11% | False | True |
| `primary=wait90s; sec<=810; fallback=none` | 758.0c | 787.0c/3.82% | 74.83%/93.77% | -29.0c/-0.21% | 72.16%/87.78% | 82.22% | False | True |
| `primary=wait90s; sec<=810; fallback=score60_wait8m:score_min_book_rv15>=0.6; ask<=95; sec>=60; sec<=480` | 710.0c | 870.0c/4.04% | 75.42%/97.38% | -160.0c/-1.03% | 72.86%/95.02% | 95.56% | False | True |
| `primary=wait120s; sec<=780; fallback=logit55_edge15_wait8m:blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=480` | 529.0c | 549.0c/2.55% | 75.17%/96.39% | -20.0c/-0.13% | 73.21%/94.57% | 95.56% | False | True |
| `primary=wait120s; sec<=780; fallback=logit55_edge15_wait6m:blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=360` | 478.0c | 473.0c/2.23% | 74.83%/95.08% | 5.0c/0.03% | 73.30%/93.21% | 91.11% | False | True |
| `primary=wait120s; sec<=780; fallback=none` | 409.0c | 438.0c/2.15% | 74.29%/91.80% | -29.0c/-0.21% | 72.16%/87.78% | 82.22% | False | True |
| `primary=wait120s; sec<=780; fallback=score60_wait8m:score_min_book_rv15>=0.6; ask<=95; sec>=60; sec<=480` | 383.0c | 543.0c/2.52% | 75.17%/96.39% | -160.0c/-1.03% | 72.86%/95.02% | 95.56% | False | True |
| `primary=wait180s; sec<=720; fallback=logit55_edge15_wait6m:blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=360` | 244.0c | 70.0c/0.33% | 74.73%/92.13% | 174.0c/1.14% | 75.61%/92.76% | 88.89% | False | True |
| `primary=wait180s; sec<=720; fallback=score60_wait8m:score_min_book_rv15>=0.6; ask<=95; sec>=60; sec<=480` | 184.0c | 155.0c/0.72% | 75.26%/94.10% | 29.0c/0.18% | 75.24%/95.02% | 93.44% | False | True |
| `primary=wait180s; sec<=720; fallback=none` | 90.0c | -18.0c/-0.09% | 73.38%/86.23% | 108.0c/0.78% | 74.07%/85.52% | 80.00% | False | True |
| `primary=wait300s; sec<=600; fallback=logit55_edge15_wait8m:blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=480` | -2070.0c | -827.0c/-3.77% | 75.09%/92.13% | -1243.0c/-7.70% | 71.98%/93.67% | 88.52% | False | True |
| `primary=wait300s; sec<=600; fallback=logit55_edge15_wait6m:blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60; sec<=360` | -2215.0c | -1030.0c/-5.12% | 73.18%/85.57% | -1185.0c/-8.18% | 70.37%/85.52% | 82.22% | False | True |
| `primary=wait300s; sec<=600; fallback=score60_wait8m:score_min_book_rv15>=0.6; ask<=95; sec>=60; sec<=480` | -2222.0c | -835.0c/-3.81% | 75.09%/92.13% | -1387.0c/-8.52% | 71.63%/94.12% | 88.52% | False | True |
| `primary=wait300s; sec<=600; fallback=none` | -2174.0c | -1105.0c/-6.74% | 69.23%/72.46% | -1069.0c/-9.08% | 67.30%/71.95% | 64.44% | False | False |

## Read

- Best strict diagnostic row is `primary=no_cap; fallback=score60:score_min_book_rv15>=0.6; ask<=95; sec>=60` with combined all-ledger net 1965.0c.
