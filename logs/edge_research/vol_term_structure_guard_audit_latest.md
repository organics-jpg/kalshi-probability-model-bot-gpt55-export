# Volatility Term-Structure Guard Audit

Generated UTC: `20260504_164155Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Tests fixed short/medium/long realized-volatility ratio guards on high-coverage book/score priors.
- Strict pass requires current+v21 coverage, positive validation/holdout, positive all splits, and block stability.

## Combined Read

| candidate | combined net | combined OOS | current/v21 net | current/v21 acc | current/v21 cov | coverage | all splits | OOS | min block+ | worst block | robust |
|---|---:|---:|---:|---:|---:|---|---|---|---:|---:|---|
| `score_edge_m5__rv15_over_rv30_le_1p2` | 2216.0c | 918.0c | 1425.0c/791.0c | 76.25%/76.09% | 91.16%/83.26% | False | False | False | 45.45% | -281.0c | False |
| `score_edge_m5` | 2164.0c | 703.0c | 1286.0c/878.0c | 75.48%/76.32% | 95.73%/85.97% | True | False | False | 54.55% | -248.0c | False |
| `score_m60__rv15_over_rv30_le_1p2` | 1757.0c | 694.0c | 1192.0c/565.0c | 75.80%/74.65% | 95.73%/96.38% | True | False | False | 63.64% | -293.0c | False |
| `score_m60` | 1654.0c | 544.0c | 1120.0c/534.0c | 75.08%/73.85% | 99.09%/98.64% | True | False | False | 63.64% | -228.0c | False |
| `score_edge_m5__rv15_over_rv30_le_1` | 1602.0c | 912.0c | 1439.0c/163.0c | 78.28%/73.97% | 74.39%/66.06% | False | False | True | 9.09% | -256.0c | False |
| `score_edge_m5__rv15_minus_rv30_le_0` | 1602.0c | 912.0c | 1439.0c/163.0c | 78.28%/73.97% | 74.39%/66.06% | False | False | True | 9.09% | -256.0c | False |
| `score_edge_m5__rv15_over_rv60_le_1` | 1494.0c | 675.0c | 1024.0c/470.0c | 75.50%/74.50% | 75.91%/67.42% | False | False | False | 18.18% | -255.0c | False |
| `score_m60__rv15_minus_rv30_le_m10` | 1334.0c | 575.0c | 1211.0c/123.0c | 81.94%/74.49% | 43.90%/44.34% | False | False | False | 0.00% | -208.0c | False |
| `score_m60__rv15_over_rv60_le_1` | 1305.0c | 559.0c | 1138.0c/167.0c | 76.25%/72.73% | 79.57%/74.66% | False | False | False | 27.27% | -282.0c | False |
| `score_edge_m5__rv15_minus_rv30_le_m10` | 1274.0c | 554.0c | 1069.0c/205.0c | 80.30%/75.58% | 40.24%/38.91% | False | False | True | 0.00% | -146.0c | False |
| `book_margin` | 1243.0c | 529.0c | 818.0c/425.0c | 70.25%/71.23% | 99.39%/99.10% | True | False | False | 62.50% | -332.0c | False |
| `book_edge_m5` | 1243.0c | 529.0c | 818.0c/425.0c | 70.25%/71.23% | 99.39%/99.10% | True | False | False | 62.50% | -332.0c | False |
| `score_m60__rv15_over_rv30_le_0p8` | 1181.0c | 575.0c | 970.0c/211.0c | 82.58%/76.74% | 40.24%/38.91% | False | False | False | 0.00% | -180.0c | False |
| `score_m60__rv15_over_rv30_le_1` | 1175.0c | 637.0c | 1237.0c/-62.0c | 78.12%/72.78% | 78.05%/76.47% | False | False | False | 27.27% | -301.0c | False |
| `score_m60__rv15_minus_rv30_le_0` | 1175.0c | 637.0c | 1237.0c/-62.0c | 78.12%/72.78% | 78.05%/76.47% | False | False | False | 27.27% | -301.0c | False |
| `score_edge_m5__rv15_over_rv30_le_0p8` | 1144.0c | 484.0c | 812.0c/332.0c | 81.15%/78.67% | 37.20%/33.94% | False | False | False | 0.00% | -180.0c | False |
| `score_edge_m5__rv15_over_rv30_le_0p8__rv_sigma_t_15m_le_100` | 1126.0c | 532.0c | 823.0c/303.0c | 82.41%/78.57% | 32.93%/31.67% | False | False | True | 0.00% | -180.0c | False |
| `score_edge_m5__rv15_over_rv30_ge_0p8` | 1077.0c | 76.0c | 457.0c/620.0c | 74.30%/76.22% | 86.59%/74.21% | False | False | False | 36.36% | -273.0c | False |
| `book_margin__rv15_minus_rv30_le_m10` | 1056.0c | 412.0c | 791.0c/265.0c | 76.47%/75.25% | 46.65%/45.70% | False | False | False | 0.00% | -200.0c | False |
| `book_edge_m5__rv15_minus_rv30_le_m10` | 1056.0c | 412.0c | 791.0c/265.0c | 76.47%/75.25% | 46.65%/45.70% | False | False | False | 0.00% | -200.0c | False |
| `score_m60__rv15_over_rv30_le_0p8__rv_sigma_t_15m_le_100` | 1054.0c | 643.0c | 929.0c/125.0c | 83.33%/76.25% | 36.59%/36.20% | False | False | True | 0.00% | -180.0c | False |
| `book_margin__rv15_over_rv30_le_1p2` | 1027.0c | 658.0c | 589.0c/438.0c | 70.22%/72.22% | 97.26%/97.74% | True | False | True | 54.55% | -340.0c | False |
| `book_edge_m5__rv15_over_rv30_le_1p2` | 1027.0c | 658.0c | 589.0c/438.0c | 70.22%/72.22% | 97.26%/97.74% | True | False | True | 54.55% | -340.0c | False |
| `book_margin__rv15_over_rv30_le_0p8__rv_sigma_t_15m_le_100` | 1010.0c | 684.0c | 949.0c/61.0c | 80.77%/74.70% | 39.63%/37.56% | False | False | True | 0.00% | -151.0c | False |
| `book_edge_m5__rv15_over_rv30_le_0p8__rv_sigma_t_15m_le_100` | 1010.0c | 684.0c | 949.0c/61.0c | 80.77%/74.70% | 39.63%/37.56% | False | False | True | 0.00% | -151.0c | False |
| `score_edge_m5__rv30_over_rv60_le_1` | 989.0c | 343.0c | 304.0c/685.0c | 72.73%/77.24% | 63.72%/55.66% | False | False | False | 0.00% | -223.0c | False |
| `score_m60__rv30_over_rv60_le_1` | 832.0c | 321.0c | 274.0c/558.0c | 73.33%/76.55% | 68.60%/65.61% | False | False | False | 9.09% | -305.0c | False |
| `score_edge_m5__rv15_over_rv60_le_0p8` | 821.0c | 381.0c | 551.0c/270.0c | 76.62%/75.73% | 46.95%/46.61% | False | False | False | 0.00% | -184.0c | False |
| `book_margin__rv15_over_rv30_le_0p8` | 798.0c | 424.0c | 610.0c/188.0c | 77.08%/75.56% | 43.90%/40.72% | False | False | False | 0.00% | -146.0c | False |
| `book_edge_m5__rv15_over_rv30_le_0p8` | 798.0c | 424.0c | 610.0c/188.0c | 77.08%/75.56% | 43.90%/40.72% | False | False | False | 0.00% | -146.0c | False |
| `score_edge_m5__rv15_over_rv30_le_1__rv30_over_rv60_le_1` | 751.0c | 573.0c | 570.0c/181.0c | 76.88%/75.51% | 48.78%/44.34% | False | False | False | 0.00% | -261.0c | False |
| `score_m60__rv15_over_rv30_ge_0p8` | 706.0c | 126.0c | 334.0c/372.0c | 74.26%/74.40% | 92.38%/93.67% | True | False | False | 50.00% | -319.0c | False |
| `book_margin__rv15_over_rv30_le_1` | 696.0c | 263.0c | 560.0c/136.0c | 72.83%/72.57% | 80.79%/79.19% | False | False | False | 45.45% | -257.0c | False |
| `book_margin__rv15_minus_rv30_le_0` | 696.0c | 263.0c | 560.0c/136.0c | 72.83%/72.57% | 80.79%/79.19% | False | False | False | 45.45% | -257.0c | False |
| `book_edge_m5__rv15_over_rv30_le_1` | 696.0c | 263.0c | 560.0c/136.0c | 72.83%/72.57% | 80.79%/79.19% | False | False | False | 45.45% | -257.0c | False |
| `book_edge_m5__rv15_minus_rv30_le_0` | 696.0c | 263.0c | 560.0c/136.0c | 72.83%/72.57% | 80.79%/79.19% | False | False | False | 45.45% | -257.0c | False |
| `score_edge_m5__rv30_over_rv60_ge_1` | 674.0c | -19.0c | 490.0c/184.0c | 77.78%/76.70% | 54.88%/46.61% | False | False | False | 0.00% | -228.0c | False |
| `book_margin__rv15_over_rv60_le_1` | 673.0c | 598.0c | 738.0c/-65.0c | 71.91%/70.18% | 81.40%/77.38% | False | False | False | 27.27% | -258.0c | False |
| `book_edge_m5__rv15_over_rv60_le_1` | 673.0c | 598.0c | 738.0c/-65.0c | 71.91%/70.18% | 81.40%/77.38% | False | False | False | 27.27% | -258.0c | False |
| `book_margin__rv30_over_rv60_le_1` | 662.0c | 428.0c | 281.0c/381.0c | 70.09%/73.33% | 71.34%/67.87% | False | False | False | 18.18% | -367.0c | False |

## Split Summary

| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | coverage | all splits | OOS |
|---|---|---:|---:|---:|---:|---:|---|---|---|
| current | `book_edge_m5` | 818.0c/3.70% | 70.25%/99.39% | 794.0c | 62.0c | -38.0c | True | False | False |
| v21 | `book_edge_m5` | 425.0c/2.80% | 71.23%/99.10% | -80.0c | 212.0c | 293.0c | True | False | True |
| current | `book_edge_m5__rv15_minus_rv30_ge_0` | -439.0c/-2.46% | 70.73%/75.00% | -118.0c | 54.0c | -375.0c | False | False | False |
| v21 | `book_edge_m5__rv15_minus_rv30_ge_0` | 270.0c/2.24% | 75.46%/73.76% | 268.0c | -13.0c | 15.0c | False | False | False |
| current | `book_edge_m5__rv15_minus_rv30_ge_10` | -849.0c/-9.28% | 66.94%/37.80% | -36.0c | -188.0c | -625.0c | False | False | False |
| v21 | `book_edge_m5__rv15_minus_rv30_ge_10` | -278.0c/-4.36% | 71.76%/38.46% | -161.0c | -61.0c | -56.0c | False | False | False |
| current | `book_edge_m5__rv15_minus_rv30_le_0` | 560.0c/2.99% | 72.83%/80.79% | 535.0c | 281.0c | -256.0c | False | False | False |
| v21 | `book_edge_m5__rv15_minus_rv30_le_0` | 136.0c/1.08% | 72.57%/79.19% | -102.0c | 171.0c | 67.0c | False | False | True |
| current | `book_edge_m5__rv15_minus_rv30_le_m10` | 791.0c/7.25% | 76.47%/46.65% | 846.0c | 176.0c | -231.0c | False | False | False |
| v21 | `book_edge_m5__rv15_minus_rv30_le_m10` | 265.0c/3.61% | 75.25%/45.70% | -202.0c | 259.0c | 208.0c | False | False | True |
| current | `book_edge_m5__rv15_over_rv30_ge_0p8` | 220.0c/1.01% | 70.19%/95.12% | 516.0c | -30.0c | -266.0c | True | False | False |
| v21 | `book_edge_m5__rv15_over_rv30_ge_0p8` | 326.0c/2.18% | 72.17%/95.93% | -109.0c | 179.0c | 256.0c | True | False | True |
| current | `book_edge_m5__rv15_over_rv30_ge_1` | -439.0c/-2.46% | 70.73%/75.00% | -118.0c | 54.0c | -375.0c | False | False | False |
| v21 | `book_edge_m5__rv15_over_rv30_ge_1` | 270.0c/2.24% | 75.46%/73.76% | 268.0c | -13.0c | 15.0c | False | False | False |
| current | `book_edge_m5__rv15_over_rv30_ge_1__rv30_over_rv60_ge_1` | -43.0c/-0.43% | 76.15%/39.63% | 15.0c | -67.0c | 9.0c | False | False | False |
| v21 | `book_edge_m5__rv15_over_rv30_ge_1__rv30_over_rv60_ge_1` | 385.0c/5.91% | 81.18%/38.46% | 563.0c | -139.0c | -39.0c | False | False | False |
| current | `book_edge_m5__rv15_over_rv30_ge_1p2` | -578.0c/-8.17% | 70.65%/28.05% | -351.0c | -196.0c | -31.0c | False | False | False |
| v21 | `book_edge_m5__rv15_over_rv30_ge_1p2` | -162.0c/-3.47% | 73.77%/27.60% | 58.0c | 9.0c | -229.0c | False | False | False |
| current | `book_edge_m5__rv15_over_rv30_ge_1p2__rv_sigma_t_15m_ge_75` | 283.0c/6.71% | 78.95%/17.38% | 277.0c | 46.0c | -40.0c | False | False | False |
| v21 | `book_edge_m5__rv15_over_rv30_ge_1p2__rv_sigma_t_15m_ge_75` | 38.0c/1.33% | 74.36%/17.65% | 21.0c | 60.0c | -43.0c | False | False | False |
| current | `book_edge_m5__rv15_over_rv30_le_0p8` | 610.0c/5.82% | 77.08%/43.90% | 641.0c | 146.0c | -177.0c | False | False | False |
| v21 | `book_edge_m5__rv15_over_rv30_le_0p8` | 188.0c/2.84% | 75.56%/40.72% | -267.0c | 180.0c | 275.0c | False | False | True |
| current | `book_edge_m5__rv15_over_rv30_le_0p8__rv_sigma_t_15m_le_100` | 949.0c/9.94% | 80.77%/39.63% | 720.0c | 146.0c | 83.0c | False | True | True |
| v21 | `book_edge_m5__rv15_over_rv30_le_0p8__rv_sigma_t_15m_le_100` | 61.0c/0.99% | 74.70%/37.56% | -394.0c | 180.0c | 275.0c | False | False | True |
| current | `book_edge_m5__rv15_over_rv30_le_1` | 560.0c/2.99% | 72.83%/80.79% | 535.0c | 281.0c | -256.0c | False | False | False |
| v21 | `book_edge_m5__rv15_over_rv30_le_1` | 136.0c/1.08% | 72.57%/79.19% | -102.0c | 171.0c | 67.0c | False | False | True |
| current | `book_edge_m5__rv15_over_rv30_le_1__rv30_over_rv60_le_1` | 623.0c/4.88% | 74.86%/54.57% | 723.0c | 97.0c | -197.0c | False | False | False |
| v21 | `book_edge_m5__rv15_over_rv30_le_1__rv30_over_rv60_le_1` | -9.0c/-0.11% | 72.07%/50.23% | -513.0c | 439.0c | 65.0c | False | False | True |
| current | `book_edge_m5__rv15_over_rv30_le_1p2` | 589.0c/2.70% | 70.22%/97.26% | 475.0c | 50.0c | 64.0c | True | True | True |
| v21 | `book_edge_m5__rv15_over_rv30_le_1p2` | 438.0c/2.89% | 72.22%/97.74% | -106.0c | 200.0c | 344.0c | True | False | True |
| current | `book_edge_m5__rv15_over_rv60_ge_1` | -1040.0c/-7.30% | 67.35%/59.76% | -555.0c | -192.0c | -293.0c | False | False | False |
| v21 | `book_edge_m5__rv15_over_rv60_ge_1` | 155.0c/1.61% | 74.24%/59.73% | 100.0c | 37.0c | 18.0c | False | True | True |
| current | `book_edge_m5__rv15_over_rv60_ge_1p2` | -294.0c/-4.09% | 71.88%/29.27% | -202.0c | -96.0c | 4.0c | False | False | False |
| v21 | `book_edge_m5__rv15_over_rv60_ge_1p2` | 81.0c/1.61% | 77.27%/29.86% | 248.0c | -248.0c | 81.0c | False | False | False |
| current | `book_edge_m5__rv15_over_rv60_le_0p8` | 519.0c/4.16% | 74.71%/53.05% | 640.0c | 110.0c | -231.0c | False | False | False |
| v21 | `book_edge_m5__rv15_over_rv60_le_0p8` | -237.0c/-2.84% | 70.43%/52.04% | -573.0c | 258.0c | 78.0c | False | False | True |
| current | `book_edge_m5__rv15_over_rv60_le_1` | 738.0c/4.00% | 71.91%/81.40% | 602.0c | 381.0c | -245.0c | True | False | False |
| v21 | `book_edge_m5__rv15_over_rv60_le_1` | -65.0c/-0.54% | 70.18%/77.38% | -527.0c | 196.0c | 266.0c | False | False | True |
| current | `book_edge_m5__rv30_over_rv60_ge_1` | -119.0c/-0.78% | 71.56%/64.33% | 141.0c | -89.0c | -171.0c | False | False | False |
| v21 | `book_edge_m5__rv30_over_rv60_ge_1` | 218.0c/2.12% | 75.00%/63.35% | 636.0c | -393.0c | -25.0c | False | False | False |
| current | `book_edge_m5__rv30_over_rv60_ge_1p2` | 176.0c/4.27% | 76.79%/17.07% | -164.0c | 181.0c | 159.0c | False | False | True |
| v21 | `book_edge_m5__rv30_over_rv60_ge_1p2` | -233.0c/-11.46% | 66.67%/12.22% | -201.0c | 37.0c | -69.0c | False | False | False |
| current | `book_edge_m5__rv30_over_rv60_le_0p8` | 12.0c/0.18% | 72.22%/27.44% | 195.0c | -23.0c | -160.0c | False | False | False |
| v21 | `book_edge_m5__rv30_over_rv60_le_0p8` | -298.0c/-7.10% | 68.42%/25.79% | -425.0c | 176.0c | -49.0c | False | False | False |
| current | `book_edge_m5__rv30_over_rv60_le_1` | 281.0c/1.74% | 70.09%/71.34% | 742.0c | -179.0c | -282.0c | False | False | False |
| v21 | `book_edge_m5__rv30_over_rv60_le_1` | 381.0c/3.59% | 73.33%/67.87% | -508.0c | 490.0c | 399.0c | False | False | True |
| current | `book_margin` | 818.0c/3.70% | 70.25%/99.39% | 794.0c | 62.0c | -38.0c | True | False | False |
| v21 | `book_margin` | 425.0c/2.80% | 71.23%/99.10% | -80.0c | 212.0c | 293.0c | True | False | True |
| current | `book_margin__rv15_minus_rv30_ge_0` | -439.0c/-2.46% | 70.73%/75.00% | -118.0c | 54.0c | -375.0c | False | False | False |
| v21 | `book_margin__rv15_minus_rv30_ge_0` | 270.0c/2.24% | 75.46%/73.76% | 268.0c | -13.0c | 15.0c | False | False | False |
| current | `book_margin__rv15_minus_rv30_ge_10` | -849.0c/-9.28% | 66.94%/37.80% | -36.0c | -188.0c | -625.0c | False | False | False |
| v21 | `book_margin__rv15_minus_rv30_ge_10` | -278.0c/-4.36% | 71.76%/38.46% | -161.0c | -61.0c | -56.0c | False | False | False |
| current | `book_margin__rv15_minus_rv30_le_0` | 560.0c/2.99% | 72.83%/80.79% | 535.0c | 281.0c | -256.0c | False | False | False |
| v21 | `book_margin__rv15_minus_rv30_le_0` | 136.0c/1.08% | 72.57%/79.19% | -102.0c | 171.0c | 67.0c | False | False | True |
| current | `book_margin__rv15_minus_rv30_le_m10` | 791.0c/7.25% | 76.47%/46.65% | 846.0c | 176.0c | -231.0c | False | False | False |
| v21 | `book_margin__rv15_minus_rv30_le_m10` | 265.0c/3.61% | 75.25%/45.70% | -202.0c | 259.0c | 208.0c | False | False | True |
| current | `book_margin__rv15_over_rv30_ge_0p8` | 220.0c/1.01% | 70.19%/95.12% | 516.0c | -30.0c | -266.0c | True | False | False |
| v21 | `book_margin__rv15_over_rv30_ge_0p8` | 326.0c/2.18% | 72.17%/95.93% | -109.0c | 179.0c | 256.0c | True | False | True |
| current | `book_margin__rv15_over_rv30_ge_1` | -439.0c/-2.46% | 70.73%/75.00% | -118.0c | 54.0c | -375.0c | False | False | False |
| v21 | `book_margin__rv15_over_rv30_ge_1` | 270.0c/2.24% | 75.46%/73.76% | 268.0c | -13.0c | 15.0c | False | False | False |
| current | `book_margin__rv15_over_rv30_ge_1__rv30_over_rv60_ge_1` | -43.0c/-0.43% | 76.15%/39.63% | 15.0c | -67.0c | 9.0c | False | False | False |
| v21 | `book_margin__rv15_over_rv30_ge_1__rv30_over_rv60_ge_1` | 385.0c/5.91% | 81.18%/38.46% | 563.0c | -139.0c | -39.0c | False | False | False |
| current | `book_margin__rv15_over_rv30_ge_1p2` | -578.0c/-8.17% | 70.65%/28.05% | -351.0c | -196.0c | -31.0c | False | False | False |
| v21 | `book_margin__rv15_over_rv30_ge_1p2` | -162.0c/-3.47% | 73.77%/27.60% | 58.0c | 9.0c | -229.0c | False | False | False |
| current | `book_margin__rv15_over_rv30_ge_1p2__rv_sigma_t_15m_ge_75` | 283.0c/6.71% | 78.95%/17.38% | 277.0c | 46.0c | -40.0c | False | False | False |
| v21 | `book_margin__rv15_over_rv30_ge_1p2__rv_sigma_t_15m_ge_75` | 38.0c/1.33% | 74.36%/17.65% | 21.0c | 60.0c | -43.0c | False | False | False |
| current | `book_margin__rv15_over_rv30_le_0p8` | 610.0c/5.82% | 77.08%/43.90% | 641.0c | 146.0c | -177.0c | False | False | False |
| v21 | `book_margin__rv15_over_rv30_le_0p8` | 188.0c/2.84% | 75.56%/40.72% | -267.0c | 180.0c | 275.0c | False | False | True |
| current | `book_margin__rv15_over_rv30_le_0p8__rv_sigma_t_15m_le_100` | 949.0c/9.94% | 80.77%/39.63% | 720.0c | 146.0c | 83.0c | False | True | True |
| v21 | `book_margin__rv15_over_rv30_le_0p8__rv_sigma_t_15m_le_100` | 61.0c/0.99% | 74.70%/37.56% | -394.0c | 180.0c | 275.0c | False | False | True |
| current | `book_margin__rv15_over_rv30_le_1` | 560.0c/2.99% | 72.83%/80.79% | 535.0c | 281.0c | -256.0c | False | False | False |
| v21 | `book_margin__rv15_over_rv30_le_1` | 136.0c/1.08% | 72.57%/79.19% | -102.0c | 171.0c | 67.0c | False | False | True |
| current | `book_margin__rv15_over_rv30_le_1__rv30_over_rv60_le_1` | 623.0c/4.88% | 74.86%/54.57% | 723.0c | 97.0c | -197.0c | False | False | False |
| v21 | `book_margin__rv15_over_rv30_le_1__rv30_over_rv60_le_1` | -9.0c/-0.11% | 72.07%/50.23% | -513.0c | 439.0c | 65.0c | False | False | True |
| current | `book_margin__rv15_over_rv30_le_1p2` | 589.0c/2.70% | 70.22%/97.26% | 475.0c | 50.0c | 64.0c | True | True | True |
| v21 | `book_margin__rv15_over_rv30_le_1p2` | 438.0c/2.89% | 72.22%/97.74% | -106.0c | 200.0c | 344.0c | True | False | True |
| current | `book_margin__rv15_over_rv60_ge_1` | -1040.0c/-7.30% | 67.35%/59.76% | -555.0c | -192.0c | -293.0c | False | False | False |
| v21 | `book_margin__rv15_over_rv60_ge_1` | 155.0c/1.61% | 74.24%/59.73% | 100.0c | 37.0c | 18.0c | False | True | True |
| current | `book_margin__rv15_over_rv60_ge_1p2` | -294.0c/-4.09% | 71.88%/29.27% | -202.0c | -96.0c | 4.0c | False | False | False |
| v21 | `book_margin__rv15_over_rv60_ge_1p2` | 81.0c/1.61% | 77.27%/29.86% | 248.0c | -248.0c | 81.0c | False | False | False |
| current | `book_margin__rv15_over_rv60_le_0p8` | 519.0c/4.16% | 74.71%/53.05% | 640.0c | 110.0c | -231.0c | False | False | False |
| v21 | `book_margin__rv15_over_rv60_le_0p8` | -237.0c/-2.84% | 70.43%/52.04% | -573.0c | 258.0c | 78.0c | False | False | True |
| current | `book_margin__rv15_over_rv60_le_1` | 738.0c/4.00% | 71.91%/81.40% | 602.0c | 381.0c | -245.0c | True | False | False |
| v21 | `book_margin__rv15_over_rv60_le_1` | -65.0c/-0.54% | 70.18%/77.38% | -527.0c | 196.0c | 266.0c | False | False | True |
| current | `book_margin__rv30_over_rv60_ge_1` | -119.0c/-0.78% | 71.56%/64.33% | 141.0c | -89.0c | -171.0c | False | False | False |
| v21 | `book_margin__rv30_over_rv60_ge_1` | 218.0c/2.12% | 75.00%/63.35% | 636.0c | -393.0c | -25.0c | False | False | False |
| current | `book_margin__rv30_over_rv60_ge_1p2` | 176.0c/4.27% | 76.79%/17.07% | -164.0c | 181.0c | 159.0c | False | False | True |
| v21 | `book_margin__rv30_over_rv60_ge_1p2` | -233.0c/-11.46% | 66.67%/12.22% | -201.0c | 37.0c | -69.0c | False | False | False |
| current | `book_margin__rv30_over_rv60_le_0p8` | 12.0c/0.18% | 72.22%/27.44% | 195.0c | -23.0c | -160.0c | False | False | False |
| v21 | `book_margin__rv30_over_rv60_le_0p8` | -298.0c/-7.10% | 68.42%/25.79% | -425.0c | 176.0c | -49.0c | False | False | False |
| current | `book_margin__rv30_over_rv60_le_1` | 281.0c/1.74% | 70.09%/71.34% | 742.0c | -179.0c | -282.0c | False | False | False |
| v21 | `book_margin__rv30_over_rv60_le_1` | 381.0c/3.59% | 73.33%/67.87% | -508.0c | 490.0c | 399.0c | False | False | True |
| current | `score_edge_m5` | 1286.0c/5.74% | 75.48%/95.73% | 1271.0c | 114.0c | -99.0c | True | False | False |
| v21 | `score_edge_m5` | 878.0c/6.45% | 76.32%/85.97% | 190.0c | 393.0c | 295.0c | True | True | True |
| current | `score_edge_m5__rv15_minus_rv30_ge_0` | -344.0c/-2.35% | 73.71%/59.15% | 316.0c | -45.0c | -615.0c | False | False | False |
| v21 | `score_edge_m5__rv15_minus_rv30_ge_0` | 697.0c/8.50% | 82.41%/48.87% | 362.0c | 285.0c | 50.0c | False | True | True |
| current | `score_edge_m5__rv15_minus_rv30_ge_10` | -340.0c/-5.72% | 71.79%/23.78% | 234.0c | -203.0c | -371.0c | False | False | False |
| v21 | `score_edge_m5__rv15_minus_rv30_ge_10` | -166.0c/-5.60% | 71.79%/17.65% | -223.0c | 41.0c | 16.0c | False | False | True |
| current | `score_edge_m5__rv15_minus_rv30_le_0` | 1439.0c/8.15% | 78.28%/74.39% | 995.0c | 428.0c | 16.0c | False | True | True |
| v21 | `score_edge_m5__rv15_minus_rv30_le_0` | 163.0c/1.53% | 73.97%/66.06% | -305.0c | 292.0c | 176.0c | False | False | True |
| current | `score_edge_m5__rv15_minus_rv30_le_m10` | 1069.0c/11.22% | 80.30%/40.24% | 879.0c | 162.0c | 28.0c | False | True | True |
| v21 | `score_edge_m5__rv15_minus_rv30_le_m10` | 205.0c/3.26% | 75.58%/38.91% | -159.0c | 150.0c | 214.0c | False | False | True |
| current | `score_edge_m5__rv15_over_rv30_ge_0p8` | 457.0c/2.21% | 74.30%/86.59% | 876.0c | -156.0c | -263.0c | True | False | False |
| v21 | `score_edge_m5__rv15_over_rv30_ge_0p8` | 620.0c/5.22% | 76.22%/74.21% | 125.0c | 412.0c | 83.0c | False | True | True |
| current | `score_edge_m5__rv15_over_rv30_ge_1` | -344.0c/-2.35% | 73.71%/59.15% | 316.0c | -45.0c | -615.0c | False | False | False |
| v21 | `score_edge_m5__rv15_over_rv30_ge_1` | 697.0c/8.50% | 82.41%/48.87% | 362.0c | 285.0c | 50.0c | False | True | True |
| current | `score_edge_m5__rv15_over_rv30_ge_1__rv30_over_rv60_ge_1` | -10.0c/-0.15% | 79.27%/25.00% | 40.0c | -119.0c | 69.0c | False | False | False |
| v21 | `score_edge_m5__rv15_over_rv30_ge_1__rv30_over_rv60_ge_1` | 366.0c/11.32% | 87.80%/18.55% | 307.0c | 103.0c | -44.0c | False | False | False |
| current | `score_edge_m5__rv15_over_rv30_ge_1p2` | -535.0c/-12.94% | 67.92%/16.16% | -199.0c | -319.0c | -17.0c | False | False | False |
| v21 | `score_edge_m5__rv15_over_rv30_ge_1p2` | -60.0c/-3.23% | 72.00%/11.31% | 53.0c | 68.0c | -181.0c | False | False | False |
| current | `score_edge_m5__rv15_over_rv30_ge_1p2__rv_sigma_t_15m_ge_75` | 140.0c/6.19% | 80.00%/9.15% | 296.0c | -139.0c | -17.0c | False | False | False |
| v21 | `score_edge_m5__rv15_over_rv30_ge_1p2__rv_sigma_t_15m_ge_75` | 173.0c/15.35% | 81.25%/7.24% | 113.0c | 60.0c | 0.0c | False | False | False |
| current | `score_edge_m5__rv15_over_rv30_le_0p8` | 812.0c/8.93% | 81.15%/37.20% | 793.0c | 31.0c | -12.0c | False | False | False |
| v21 | `score_edge_m5__rv15_over_rv30_le_0p8` | 332.0c/5.96% | 78.67%/33.94% | -133.0c | 157.0c | 308.0c | False | False | True |
| current | `score_edge_m5__rv15_over_rv30_le_0p8__rv_sigma_t_15m_le_100` | 823.0c/10.19% | 82.41%/32.93% | 756.0c | 31.0c | 36.0c | False | True | True |
| v21 | `score_edge_m5__rv15_over_rv30_le_0p8__rv_sigma_t_15m_le_100` | 303.0c/5.83% | 78.57%/31.67% | -162.0c | 157.0c | 308.0c | False | False | True |
| current | `score_edge_m5__rv15_over_rv30_le_1` | 1439.0c/8.15% | 78.28%/74.39% | 995.0c | 428.0c | 16.0c | False | True | True |
| v21 | `score_edge_m5__rv15_over_rv30_le_1` | 163.0c/1.53% | 73.97%/66.06% | -305.0c | 292.0c | 176.0c | False | False | True |
| current | `score_edge_m5__rv15_over_rv30_le_1__rv30_over_rv60_le_1` | 570.0c/4.86% | 76.88%/48.78% | 589.0c | 51.0c | -70.0c | False | False | False |
| v21 | `score_edge_m5__rv15_over_rv30_le_1__rv30_over_rv60_le_1` | 181.0c/2.51% | 75.51%/44.34% | -411.0c | 539.0c | 53.0c | False | False | True |
| current | `score_edge_m5__rv15_over_rv30_le_1p2` | 1425.0c/6.67% | 76.25%/91.16% | 1170.0c | 352.0c | -97.0c | True | False | False |
| v21 | `score_edge_m5__rv15_over_rv30_le_1p2` | 791.0c/5.99% | 76.09%/83.26% | 128.0c | 385.0c | 278.0c | False | True | True |
| current | `score_edge_m5__rv15_over_rv60_ge_1` | -251.0c/-2.36% | 74.29%/42.68% | 51.0c | -248.0c | -54.0c | False | False | False |
| v21 | `score_edge_m5__rv15_over_rv60_ge_1` | 95.0c/1.69% | 77.03%/33.48% | 31.0c | 72.0c | -8.0c | False | False | False |
| current | `score_edge_m5__rv15_over_rv60_ge_1p2` | -166.0c/-3.89% | 74.55%/16.77% | 44.0c | -151.0c | -59.0c | False | False | False |
| v21 | `score_edge_m5__rv15_over_rv60_ge_1p2` | 118.0c/4.95% | 80.65%/14.03% | 159.0c | -31.0c | -10.0c | False | False | False |
| current | `score_edge_m5__rv15_over_rv60_le_0p8` | 551.0c/4.90% | 76.62%/46.95% | 621.0c | 100.0c | -170.0c | False | False | False |
| v21 | `score_edge_m5__rv15_over_rv60_le_0p8` | 270.0c/3.59% | 75.73%/46.61% | -181.0c | 297.0c | 154.0c | False | False | True |
| current | `score_edge_m5__rv15_over_rv60_le_1` | 1024.0c/5.76% | 75.50%/75.91% | 973.0c | 351.0c | -300.0c | False | False | False |
| v21 | `score_edge_m5__rv15_over_rv60_le_1` | 470.0c/4.42% | 74.50%/67.42% | -154.0c | 322.0c | 302.0c | False | False | True |
| current | `score_edge_m5__rv30_over_rv60_ge_1` | 490.0c/3.63% | 77.78%/54.88% | 419.0c | 46.0c | 25.0c | False | True | True |
| v21 | `score_edge_m5__rv30_over_rv60_ge_1` | 184.0c/2.38% | 76.70%/46.61% | 274.0c | -183.0c | 93.0c | False | False | False |
| current | `score_edge_m5__rv30_over_rv60_ge_1p2` | 411.0c/14.23% | 84.62%/11.89% | 93.0c | 147.0c | 171.0c | False | True | True |
| v21 | `score_edge_m5__rv30_over_rv60_ge_1p2` | 4.0c/0.45% | 75.00%/5.43% | -80.0c | 19.0c | 65.0c | False | False | True |
| current | `score_edge_m5__rv30_over_rv60_le_0p8` | 113.0c/1.92% | 75.00%/24.39% | 218.0c | -8.0c | -97.0c | False | False | False |
| v21 | `score_edge_m5__rv30_over_rv60_le_0p8` | -111.0c/-3.07% | 71.43%/22.17% | -245.0c | 155.0c | -21.0c | False | False | False |
| current | `score_edge_m5__rv30_over_rv60_le_1` | 304.0c/2.04% | 72.73%/63.72% | 742.0c | -52.0c | -386.0c | False | False | False |
| v21 | `score_edge_m5__rv30_over_rv60_le_1` | 685.0c/7.77% | 77.24%/55.66% | -96.0c | 534.0c | 247.0c | False | False | True |
| current | `score_m60` | 1120.0c/4.81% | 75.08%/99.09% | 1129.0c | 112.0c | -121.0c | True | False | False |
| v21 | `score_m60` | 534.0c/3.43% | 73.85%/98.64% | -19.0c | 398.0c | 155.0c | True | False | True |
| current | `score_m60__rv15_minus_rv30_ge_0` | -462.0c/-2.71% | 74.11%/68.29% | 185.0c | -66.0c | -581.0c | False | False | False |
| v21 | `score_m60__rv15_minus_rv30_ge_0` | 676.0c/5.72% | 80.13%/70.59% | 425.0c | 271.0c | -20.0c | False | False | False |
| current | `score_m60__rv15_minus_rv30_ge_10` | -562.0c/-6.97% | 72.82%/31.40% | 104.0c | -267.0c | -399.0c | False | False | False |
| v21 | `score_m60__rv15_minus_rv30_ge_10` | -268.0c/-4.21% | 74.39%/37.10% | -186.0c | -13.0c | -69.0c | False | False | False |
| current | `score_m60__rv15_minus_rv30_le_0` | 1237.0c/6.59% | 78.12%/78.05% | 850.0c | 411.0c | -24.0c | False | False | False |
| v21 | `score_m60__rv15_minus_rv30_le_0` | -62.0c/-0.50% | 72.78%/76.47% | -312.0c | 221.0c | 29.0c | False | False | True |
| current | `score_m60__rv15_minus_rv30_le_m10` | 1211.0c/11.44% | 81.94%/43.90% | 1023.0c | 209.0c | -21.0c | False | False | False |
| v21 | `score_m60__rv15_minus_rv30_le_m10` | 123.0c/1.71% | 74.49%/44.34% | -264.0c | 213.0c | 174.0c | False | False | True |
| current | `score_m60__rv15_over_rv30_ge_0p8` | 334.0c/1.51% | 74.26%/92.38% | 670.0c | -59.0c | -277.0c | True | False | False |
| v21 | `score_m60__rv15_over_rv30_ge_0p8` | 372.0c/2.48% | 74.40%/93.67% | -90.0c | 352.0c | 110.0c | True | False | True |
| current | `score_m60__rv15_over_rv30_ge_1` | -462.0c/-2.71% | 74.11%/68.29% | 185.0c | -66.0c | -581.0c | False | False | False |
| v21 | `score_m60__rv15_over_rv30_ge_1` | 676.0c/5.72% | 80.13%/70.59% | 425.0c | 271.0c | -20.0c | False | False | False |
| current | `score_m60__rv15_over_rv30_ge_1__rv30_over_rv60_ge_1` | -99.0c/-1.10% | 79.46%/34.15% | 8.0c | -152.0c | 45.0c | False | False | False |
| v21 | `score_m60__rv15_over_rv30_ge_1__rv30_over_rv60_ge_1` | 414.0c/6.48% | 83.95%/36.65% | 447.0c | 69.0c | -102.0c | False | False | False |
| current | `score_m60__rv15_over_rv30_ge_1p2` | -578.0c/-9.21% | 73.08%/23.78% | -391.0c | -212.0c | 25.0c | False | False | False |
| v21 | `score_m60__rv15_over_rv30_ge_1p2` | -251.0c/-5.64% | 73.68%/25.79% | 14.0c | -23.0c | -242.0c | False | False | False |
| current | `score_m60__rv15_over_rv30_ge_1p2__rv_sigma_t_15m_ge_75` | 237.0c/6.84% | 84.09%/13.41% | 193.0c | 28.0c | 16.0c | False | True | True |
| v21 | `score_m60__rv15_over_rv30_ge_1p2__rv_sigma_t_15m_ge_75` | -35.0c/-1.33% | 74.29%/15.84% | -7.0c | 28.0c | -56.0c | False | False | False |
| current | `score_m60__rv15_over_rv30_le_0p8` | 970.0c/9.77% | 82.58%/40.24% | 897.0c | 80.0c | -7.0c | False | False | False |
| v21 | `score_m60__rv15_over_rv30_le_0p8` | 211.0c/3.30% | 76.74%/38.91% | -291.0c | 234.0c | 268.0c | False | False | True |
| current | `score_m60__rv15_over_rv30_le_0p8__rv_sigma_t_15m_le_100` | 929.0c/10.24% | 83.33%/36.59% | 788.0c | 80.0c | 61.0c | False | True | True |
| v21 | `score_m60__rv15_over_rv30_le_0p8__rv_sigma_t_15m_le_100` | 125.0c/2.09% | 76.25%/36.20% | -377.0c | 234.0c | 268.0c | False | False | True |
| current | `score_m60__rv15_over_rv30_le_1` | 1237.0c/6.59% | 78.12%/78.05% | 850.0c | 411.0c | -24.0c | False | False | False |
| v21 | `score_m60__rv15_over_rv30_le_1` | -62.0c/-0.50% | 72.78%/76.47% | -312.0c | 221.0c | 29.0c | False | False | True |
| current | `score_m60__rv15_over_rv30_le_1__rv30_over_rv60_le_1` | 461.0c/3.65% | 76.61%/52.13% | 525.0c | 71.0c | -135.0c | False | False | False |
| v21 | `score_m60__rv15_over_rv30_le_1__rv30_over_rv60_le_1` | 0.0c/0.00% | 73.83%/48.42% | -564.0c | 497.0c | 67.0c | False | False | True |
| current | `score_m60__rv15_over_rv30_le_1p2` | 1192.0c/5.27% | 75.80%/95.73% | 1096.0c | 198.0c | -102.0c | True | False | False |
| v21 | `score_m60__rv15_over_rv30_le_1p2` | 565.0c/3.68% | 74.65%/96.38% | -33.0c | 395.0c | 203.0c | True | False | True |
| current | `score_m60__rv15_over_rv60_ge_1` | -840.0c/-6.30% | 72.25%/52.74% | -329.0c | -225.0c | -286.0c | False | False | False |
| v21 | `score_m60__rv15_over_rv60_ge_1` | 125.0c/1.35% | 76.42%/55.66% | 134.0c | 74.0c | -83.0c | False | False | False |
| current | `score_m60__rv15_over_rv60_ge_1p2` | -561.0c/-8.96% | 72.15%/24.09% | -327.0c | -232.0c | -2.0c | False | False | False |
| v21 | `score_m60__rv15_over_rv60_ge_1p2` | -54.0c/-1.14% | 77.05%/27.60% | 157.0c | -212.0c | 1.0c | False | False | False |
| current | `score_m60__rv15_over_rv60_le_0p8` | 605.0c/5.00% | 77.44%/50.00% | 628.0c | 88.0c | -111.0c | False | False | False |
| v21 | `score_m60__rv15_over_rv60_le_0p8` | -38.0c/-0.47% | 72.97%/50.23% | -352.0c | 238.0c | 76.0c | False | False | True |
| current | `score_m60__rv15_over_rv60_le_1` | 1138.0c/6.07% | 76.25%/79.57% | 1079.0c | 366.0c | -307.0c | False | False | False |
| v21 | `score_m60__rv15_over_rv60_le_1` | 167.0c/1.41% | 72.73%/74.66% | -333.0c | 319.0c | 181.0c | False | False | True |
| current | `score_m60__rv30_over_rv60_ge_1` | 419.0c/2.72% | 77.83%/61.89% | 436.0c | 12.0c | -29.0c | False | False | False |
| v21 | `score_m60__rv30_over_rv60_ge_1` | 108.0c/1.03% | 75.71%/63.35% | 436.0c | -232.0c | -96.0c | False | False | False |
| current | `score_m60__rv30_over_rv60_ge_1p2` | 169.0c/4.19% | 80.77%/15.85% | -171.0c | 172.0c | 168.0c | False | False | True |
| v21 | `score_m60__rv30_over_rv60_ge_1p2` | -310.0c/-15.42% | 65.38%/11.76% | -262.0c | 37.0c | -85.0c | False | False | False |
| current | `score_m60__rv30_over_rv60_le_0p8` | 245.0c/3.86% | 76.74%/26.22% | 307.0c | 26.0c | -88.0c | False | False | False |
| v21 | `score_m60__rv30_over_rv60_le_0p8` | -11.0c/-0.27% | 74.07%/24.43% | -209.0c | 171.0c | 27.0c | False | False | True |
| current | `score_m60__rv30_over_rv60_le_1` | 274.0c/1.69% | 73.33%/68.60% | 816.0c | -88.0c | -454.0c | False | False | False |
| v21 | `score_m60__rv30_over_rv60_le_1` | 558.0c/5.29% | 76.55%/65.61% | -305.0c | 562.0c | 301.0c | False | False | True |

## Read

- No volatility term-structure guard clears the cross-dataset robustness gates.
