# Hazard Trigger Persistence Frontier

Generated UTC: `20260504_092137Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Tests whether hazard signals need same-side persistence after first trigger.
- Any passing row must be forward-locked before use.

## Diagnostics

- Current markets: 295
- V21 markets: 221
- Rows scanned: 10
- Strict positive OOS rows: 2

## Rows

| policy | combined net | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | min OOS cov | OOS positive | strict cov |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `hazard>=0.45; ask<=76; sec>=60; touch_loss<=0.80; persist>=0s; continuous_side` | 2129.0c | 899.0c/4.71% | 74.07%/91.53% | 1230.0c/9.00% | 76.41%/88.24% | 81.82% | True | True |
| `hazard>=0.45; ask<=80; sec>=60; touch_loss<=0.80; persist>=0s; continuous_side` | 1720.0c | 916.0c/4.56% | 75.00%/94.92% | 804.0c/5.55% | 75.00%/92.31% | 88.89% | True | True |
| `hazard>=0.45; ask<=76; sec>=60; touch_loss<=0.80; persist>=30s; continuous_side` | 768.0c | 593.0c/3.49% | 73.03%/81.69% | 175.0c/1.84% | 73.48%/59.73% | 59.09% | False | False |
| `hazard>=0.45; ask<=76; sec>=60; touch_loss<=0.80; persist>=15s; continuous_side` | 585.0c | 485.0c/2.71% | 72.73%/85.76% | 100.0c/1.04% | 72.93%/60.18% | 59.09% | False | False |
| `hazard>=0.45; ask<=80; sec>=60; touch_loss<=0.80; persist>=30s; continuous_side` | 455.0c | 632.0c/3.39% | 74.52%/87.80% | -177.0c/-1.48% | 73.29%/72.85% | 71.11% | False | False |
| `hazard>=0.45; ask<=80; sec>=60; touch_loss<=0.80; persist>=15s; continuous_side` | 356.0c | 608.0c/3.14% | 74.35%/91.19% | -252.0c/-2.09% | 72.84%/73.30% | 71.11% | False | False |
| `hazard>=0.45; ask<=76; sec>=60; touch_loss<=0.80; persist>=60s; continuous_side` | -551.0c | -333.0c/-2.32% | 70.35%/67.46% | -218.0c/-2.50% | 70.83%/54.30% | 47.73% | False | False |
| `hazard>=0.45; ask<=80; sec>=60; touch_loss<=0.80; persist>=60s; continuous_side` | -619.0c | -82.0c/-0.49% | 73.45%/76.61% | -537.0c/-4.82% | 71.14%/67.42% | 65.91% | False | False |
| `hazard>=0.45; ask<=76; sec>=60; touch_loss<=0.80; persist>=120s; continuous_side` | -749.0c | -651.0c/-6.06% | 67.79%/50.51% | -98.0c/-1.46% | 71.74%/41.63% | 34.09% | False | False |
| `hazard>=0.45; ask<=80; sec>=60; touch_loss<=0.80; persist>=120s; continuous_side` | -872.0c | -475.0c/-3.58% | 71.91%/60.34% | -397.0c/-4.62% | 71.30%/52.04% | 45.45% | False | False |

## Read

- Best strict diagnostic row is `hazard>=0.45; ask<=76; sec>=60; touch_loss<=0.80; persist>=0s; continuous_side` with combined all-ledger net 2129.0c.
