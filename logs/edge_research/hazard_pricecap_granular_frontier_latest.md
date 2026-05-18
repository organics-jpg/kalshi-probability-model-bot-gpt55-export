# Hazard Price-Cap Granular Frontier

Generated UTC: `20260504_091200Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Scans ask caps from 73c to 80c with small score/extension variants.
- Historical current/v21 rows are diagnostic; live registry cap rows are post-hoc diagnostics and must be forward-locked before use.

## Diagnostics

- Current historical markets: 295
- V21 historical markets: 221
- Live hazard registered/resolved rows: 14/13
- Rows scanned: 32
- Strict historical + live coverage rows: 5

## Rows

| policy | combined net | min OOS cov | hist strict cov | current net/cov | v21 net/cov | live wins/losses | live net | live resolved cov | live registered cov | live P(p>BE) | live p05 edge |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `hazard>=0.45; ask<=76; sec>=60; touch_loss<=0.80` | 2129.0c | 81.82% | True | 899.0c/91.53% | 1230.0c/88.24% | 10/1 | 235.0c | 84.62% | 85.71% | 0.919 | -3.5c |
| `hazard>=0.45; ask<=77; sec>=60; touch_loss<=0.80` | 2047.0c | 84.09% | True | 860.0c/91.86% | 1187.0c/89.59% | 10/1 | 235.0c | 84.62% | 85.71% | 0.919 | -3.5c |
| `hazard>=0.45; ask<=80; sec>=60; touch_loss<=0.80` | 1720.0c | 88.89% | True | 916.0c/94.92% | 804.0c/92.31% | 11/2 | 173.0c | 100.00% | 100.00% | 0.812 | -9.9c |
| `hazard>=0.45; ask<=79; sec>=60; touch_loss<=0.80` | 1654.0c | 86.67% | True | 881.0c/93.90% | 773.0c/91.40% | 11/2 | 173.0c | 100.00% | 100.00% | 0.812 | -9.9c |
| `hazard>=0.45; ask<=78; sec>=60; touch_loss<=0.80` | 1627.0c | 84.44% | True | 847.0c/92.54% | 780.0c/90.50% | 10/1 | 235.0c | 84.62% | 85.71% | 0.919 | -3.5c |
| `hazard>=0.45; ask<=73; sec>=60; touch_loss<=0.80; margin_sigma<=0.75` | 2301.0c | 72.73% | False | 1188.0c/87.80% | 1113.0c/81.00% | 9/1 | 212.0c | 76.92% | 78.57% | 0.903 | -5.2c |
| `hazard>=0.45; ask<=73; sec>=60; touch_loss<=0.80; hazard<=0.65; margin_sigma<=0.75` | 2301.0c | 72.73% | False | 1188.0c/87.80% | 1113.0c/81.00% | 9/1 | 212.0c | 76.92% | 78.57% | 0.903 | -5.2c |
| `hazard>=0.45; ask<=73; sec>=60; touch_loss<=0.80` | 2170.0c | 75.00% | False | 1030.0c/89.49% | 1140.0c/81.45% | 9/1 | 212.0c | 76.92% | 78.57% | 0.903 | -5.2c |
| `hazard>=0.45; ask<=73; sec>=60; touch_loss<=0.80; hazard<=0.65` | 2133.0c | 75.00% | False | 993.0c/88.81% | 1140.0c/81.45% | 9/1 | 212.0c | 76.92% | 78.57% | 0.903 | -5.2c |
| `hazard>=0.45; ask<=74; sec>=60; touch_loss<=0.80; margin_sigma<=0.75` | 2057.0c | 75.00% | False | 921.0c/88.14% | 1136.0c/83.71% | 9/1 | 212.0c | 76.92% | 78.57% | 0.903 | -5.2c |
| `hazard>=0.45; ask<=74; sec>=60; touch_loss<=0.80; hazard<=0.65; margin_sigma<=0.75` | 2057.0c | 75.00% | False | 921.0c/88.14% | 1136.0c/83.71% | 9/1 | 212.0c | 76.92% | 78.57% | 0.903 | -5.2c |
| `hazard>=0.45; ask<=74; sec>=60; touch_loss<=0.80` | 2018.0c | 75.56% | False | 862.0c/89.83% | 1156.0c/84.16% | 9/1 | 212.0c | 76.92% | 78.57% | 0.903 | -5.2c |
| `hazard>=0.45; ask<=75; sec>=60; touch_loss<=0.80; margin_sigma<=0.75` | 2007.0c | 77.27% | False | 883.0c/88.81% | 1124.0c/85.97% | 10/1 | 235.0c | 84.62% | 85.71% | 0.919 | -3.5c |
| `hazard>=0.45; ask<=75; sec>=60; touch_loss<=0.80; hazard<=0.65; margin_sigma<=0.75` | 2007.0c | 77.27% | False | 883.0c/88.81% | 1124.0c/85.97% | 10/1 | 235.0c | 84.62% | 85.71% | 0.919 | -3.5c |
| `hazard>=0.45; ask<=74; sec>=60; touch_loss<=0.80; hazard<=0.65` | 1972.0c | 75.56% | False | 816.0c/89.15% | 1156.0c/84.16% | 9/1 | 212.0c | 76.92% | 78.57% | 0.903 | -5.2c |
| `hazard>=0.45; ask<=75; sec>=60; touch_loss<=0.80` | 1952.0c | 79.55% | False | 809.0c/90.51% | 1143.0c/86.43% | 10/1 | 235.0c | 84.62% | 85.71% | 0.919 | -3.5c |
| `hazard>=0.45; ask<=75; sec>=60; touch_loss<=0.80; hazard<=0.65` | 1916.0c | 79.55% | False | 772.0c/89.83% | 1144.0c/86.43% | 10/1 | 235.0c | 84.62% | 85.71% | 0.919 | -3.5c |
| `hazard>=0.45; ask<=76; sec>=60; touch_loss<=0.80; hazard<=0.65` | 2003.0c | 81.82% | True | 794.0c/90.17% | 1209.0c/87.78% | 10/1 | 235.0c | 84.62% | 85.71% | 0.919 | -3.5c |
| `hazard>=0.45; ask<=77; sec>=60; touch_loss<=0.80; margin_sigma<=0.75` | 1928.0c | 81.82% | True | 782.0c/89.49% | 1146.0c/88.69% | 10/1 | 235.0c | 84.62% | 85.71% | 0.919 | -3.5c |
| `hazard>=0.45; ask<=77; sec>=60; touch_loss<=0.80; hazard<=0.65; margin_sigma<=0.75` | 1928.0c | 81.82% | True | 782.0c/89.49% | 1146.0c/88.69% | 10/1 | 235.0c | 84.62% | 85.71% | 0.919 | -3.5c |
| `hazard>=0.45; ask<=77; sec>=60; touch_loss<=0.80; hazard<=0.65` | 1901.0c | 84.09% | True | 735.0c/90.17% | 1166.0c/89.14% | 10/1 | 235.0c | 84.62% | 85.71% | 0.919 | -3.5c |
| `hazard>=0.45; ask<=80; sec>=60; touch_loss<=0.80; hazard<=0.65; margin_sigma<=0.75` | 1669.0c | 84.09% | True | 826.0c/91.86% | 843.0c/90.05% | 11/2 | 173.0c | 100.00% | 100.00% | 0.812 | -9.9c |
| `hazard>=0.45; ask<=80; sec>=60; touch_loss<=0.80; margin_sigma<=0.75` | 1655.0c | 86.36% | True | 806.0c/91.86% | 849.0c/90.50% | 11/2 | 173.0c | 100.00% | 100.00% | 0.812 | -9.9c |
| `hazard>=0.45; ask<=80; sec>=60; touch_loss<=0.80; hazard<=0.65` | 1642.0c | 86.36% | True | 779.0c/92.54% | 863.0c/90.50% | 11/2 | 173.0c | 100.00% | 100.00% | 0.812 | -9.9c |
| `hazard>=0.45; ask<=79; sec>=60; touch_loss<=0.80; hazard<=0.65; margin_sigma<=0.75` | 1636.0c | 84.09% | True | 809.0c/91.19% | 827.0c/89.59% | 11/2 | 173.0c | 100.00% | 100.00% | 0.812 | -9.9c |
| `hazard>=0.45; ask<=78; sec>=60; touch_loss<=0.80; hazard<=0.65; margin_sigma<=0.75` | 1632.0c | 84.09% | True | 793.0c/90.51% | 839.0c/89.14% | 10/1 | 235.0c | 84.62% | 85.71% | 0.919 | -3.5c |
| `hazard>=0.45; ask<=79; sec>=60; touch_loss<=0.80; margin_sigma<=0.75` | 1623.0c | 86.36% | True | 789.0c/91.19% | 834.0c/90.05% | 11/2 | 173.0c | 100.00% | 100.00% | 0.812 | -9.9c |
| `hazard>=0.45; ask<=78; sec>=60; touch_loss<=0.80; margin_sigma<=0.75` | 1620.0c | 84.09% | True | 793.0c/90.51% | 827.0c/89.14% | 10/1 | 235.0c | 84.62% | 85.71% | 0.919 | -3.5c |
| `hazard>=0.45; ask<=79; sec>=60; touch_loss<=0.80; hazard<=0.65` | 1609.0c | 86.36% | True | 762.0c/91.86% | 847.0c/90.05% | 11/2 | 173.0c | 100.00% | 100.00% | 0.812 | -9.9c |
| `hazard>=0.45; ask<=78; sec>=60; touch_loss<=0.80; hazard<=0.65` | 1605.0c | 84.44% | True | 746.0c/91.19% | 859.0c/89.59% | 10/1 | 235.0c | 84.62% | 85.71% | 0.919 | -3.5c |
| `hazard>=0.45; ask<=76; sec>=60; touch_loss<=0.80; margin_sigma<=0.75` | 2027.0c | 79.55% | False | 838.0c/89.49% | 1189.0c/87.33% | 10/1 | 235.0c | 84.62% | 85.71% | 0.919 | -3.5c |
| `hazard>=0.45; ask<=76; sec>=60; touch_loss<=0.80; hazard<=0.65; margin_sigma<=0.75` | 2027.0c | 79.55% | False | 838.0c/89.49% | 1189.0c/87.33% | 10/1 | 235.0c | 84.62% | 85.71% | 0.919 | -3.5c |

## Read

- Best strict granular cap is `hazard>=0.45; ask<=76; sec>=60; touch_loss<=0.80` with combined historical net 2129.0c and live post-hoc net 235.0c.
- Best live post-hoc cap is `hazard>=0.45; ask<=76; sec>=60; touch_loss<=0.80` with 235.0c, but this is not promotion evidence.
