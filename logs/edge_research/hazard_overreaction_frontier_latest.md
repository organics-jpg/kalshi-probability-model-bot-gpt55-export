# Hazard Overreaction Frontier

Generated UTC: `20260504_090525Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Tests whether high-score / high-price / high-extension hazard states are overreaction rather than confirmation.
- Any passing row must be forward-locked before use.

## Diagnostics

- Current markets: 295
- V21 markets: 221
- Rows scanned: 13
- Strict positive OOS rows: 4

## Rows

| policy | combined net | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | min OOS cov | OOS positive | strict cov |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `hazard>=0.45; ask<=80; sec>=60; touch_loss<=0.80` | 1720.0c | 916.0c/4.56% | 75.00%/94.92% | 804.0c/5.55% | 75.00%/92.31% | 88.89% | True | True |
| `hazard>=0.45; ask<=80; sec>=60; touch_loss<=0.80; margin_sigma<=0.65` | 1573.0c | 871.0c/4.58% | 74.81%/90.17% | 702.0c/5.20% | 73.96%/86.88% | 84.09% | True | True |
| `hazard>=0.45; ask<=80; sec>=60; touch_loss<=0.80; margin_sigma<=0.75; sec<=840` | 1257.0c | 620.0c/3.18% | 74.44%/91.53% | 637.0c/4.50% | 74.37%/90.05% | 86.36% | True | True |
| `hazard>=0.45; ask<=80; sec>=60; touch_loss<=0.80; hazard<=0.65; sec<=840` | 1244.0c | 593.0c/3.02% | 74.26%/92.20% | 651.0c/4.60% | 74.37%/90.05% | 86.36% | True | True |
| `hazard>=0.45; ask<=75; sec>=60; touch_loss<=0.80; margin_sigma<=0.75` | 2007.0c | 883.0c/4.79% | 73.66%/88.81% | 1124.0c/8.47% | 75.79%/85.97% | 77.27% | True | False |
| `hazard>=0.45; ask<=75; sec>=60; touch_loss<=0.80; hazard<=0.65; margin_sigma<=0.75` | 2007.0c | 883.0c/4.79% | 73.66%/88.81% | 1124.0c/8.47% | 75.79%/85.97% | 77.27% | True | False |
| `hazard>=0.45; ask<=75; sec>=60; touch_loss<=0.80` | 1952.0c | 809.0c/4.31% | 73.41%/90.51% | 1143.0c/8.56% | 75.92%/86.43% | 79.55% | True | False |
| `hazard>=0.45; ask<=75; sec>=60; touch_loss<=0.80; hazard<=0.65` | 1916.0c | 772.0c/4.14% | 73.21%/89.83% | 1144.0c/8.57% | 75.92%/86.43% | 79.55% | True | False |
| `hazard>=0.45; ask<=80; sec>=60; touch_loss<=0.80; hazard<=0.65; margin_sigma<=0.75` | 1669.0c | 826.0c/4.26% | 74.54%/91.86% | 843.0c/6.00% | 74.87%/90.05% | 84.09% | False | True |
| `hazard>=0.45; ask<=80; sec>=60; touch_loss<=0.80; margin_sigma<=0.75` | 1655.0c | 806.0c/4.16% | 74.54%/91.86% | 849.0c/6.00% | 75.00%/90.50% | 86.36% | False | True |
| `hazard>=0.45; ask<=80; sec>=60; touch_loss<=0.80; hazard<=0.65` | 1642.0c | 779.0c/3.99% | 74.36%/92.54% | 863.0c/6.10% | 75.00%/90.50% | 86.36% | False | True |
| `hazard>=0.45; ask<=80; sec>=60; touch_loss<=0.80; hazard<=0.6` | 1551.0c | 797.0c/4.26% | 73.86%/89.49% | 754.0c/5.61% | 73.96%/86.88% | 81.82% | False | True |
| `hazard>=0.45; ask<=80; sec>=60; touch_loss<=0.80; hazard<=0.55` | 1401.0c | 883.0c/5.01% | 73.12%/85.76% | 518.0c/4.55% | 72.12%/74.66% | 68.18% | False | False |

## Read

- Best strict diagnostic row is `hazard>=0.45; ask<=80; sec>=60; touch_loss<=0.80` with combined all-ledger net 1720.0c.
