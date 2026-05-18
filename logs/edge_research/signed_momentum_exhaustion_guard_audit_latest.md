# Signed Momentum Exhaustion Guard Audit

Generated UTC: `20260504_143118Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Tests fixed side-aligned signed-move caps on high-coverage book/score priors.
- Strict diagnostic pass requires current+v21 coverage, positive validation/holdout, positive all splits, and block stability.

## Combined Read

| candidate | robust | combined net | OOS net | current/v21 net | current/v21 acc | current/v21 cov | min block+ | worst block |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `score_m60_edge_m5__signed_move_30m_le_250` | False | 2354.0c | 1086.0c | 1372.0c/982.0c | 76.11%/77.05% | 91.28%/82.81% | 54.55% | -238.0c |
| `score_m60_edge_m5` | False | 2284.0c | 918.0c | 1406.0c/878.0c | 75.90%/76.32% | 95.64%/85.97% | 54.55% | -248.0c |
| `score_m60_edge_m5__signed_move_15m_le_125` | False | 2216.0c | 670.0c | 1092.0c/1124.0c | 75.09%/77.46% | 88.79%/78.28% | 45.45% | -291.0c |
| `score_m60_edge_m5__signed_move_15m_le_200` | False | 2177.0c | 889.0c | 1262.0c/915.0c | 75.25%/76.50% | 91.90%/82.81% | 45.45% | -238.0c |
| `score_m60_edge_m5__signed_move_15m_le_150` | False | 2100.0c | 722.0c | 1119.0c/981.0c | 75.17%/76.54% | 90.34%/81.00% | 45.45% | -266.0c |
| `score_m60_edge_m5__signed_move_30m_le_200` | False | 2044.0c | 849.0c | 1196.0c/848.0c | 75.52%/76.27% | 89.10%/80.09% | 45.45% | -238.0c |
| `score_m60_edge_m5__long_minus_short_move_30_5m_le_150` | False | 1897.0c | 843.0c | 1086.0c/811.0c | 75.77%/76.37% | 91.28%/82.35% | 45.45% | -238.0c |
| `score_m60_edge_m5__signed_move_max_15_30m_le_200` | False | 1890.0c | 789.0c | 1103.0c/787.0c | 75.09%/75.86% | 87.54%/78.73% | 45.45% | -238.0c |
| `score_m60_edge_m5__long_minus_short_move_30_5m_le_75` | False | 1866.0c | 701.0c | 936.0c/930.0c | 75.65%/77.98% | 84.42%/76.02% | 18.18% | -287.0c |
| `score_m60__signed_move_30m_le_250` | False | 1825.0c | 987.0c | 1176.0c/649.0c | 75.57%/74.65% | 95.64%/96.38% | 62.50% | -228.0c |
| `score_m60` | False | 1778.0c | 787.0c | 1244.0c/534.0c | 75.47%/73.85% | 99.07%/98.64% | 63.64% | -228.0c |
| `score_m60_edge_m5__signed_move_15m_le_100` | False | 1732.0c | 501.0c | 832.0c/900.0c | 74.09%/76.36% | 85.36%/74.66% | 36.36% | -318.0c |
| `score_m60_edge_m5__signed_move_30m_le_150` | False | 1727.0c | 767.0c | 881.0c/846.0c | 74.55%/76.47% | 85.67%/76.92% | 27.27% | -239.0c |
| `book_margin__signed_move_30m_le_250` | False | 1714.0c | 713.0c | 1069.0c/645.0c | 71.15%/72.43% | 97.20%/96.83% | 62.50% | -332.0c |
| `book_margin_edge_m5__signed_move_30m_le_250` | False | 1714.0c | 713.0c | 1069.0c/645.0c | 71.15%/72.43% | 97.20%/96.83% | 62.50% | -332.0c |
| `score_m60_edge_m5__signed_move_max_15_30m_le_150` | False | 1691.0c | 670.0c | 800.0c/891.0c | 74.44%/76.51% | 84.11%/75.11% | 27.27% | -226.0c |
| `score_m60__long_minus_short_move_30_5m_le_150` | False | 1656.0c | 918.0c | 1015.0c/641.0c | 75.41%/74.76% | 95.02%/95.02% | 62.50% | -239.0c |
| `score_m60_edge_m5__signed_move_15m_le_75` | False | 1637.0c | 673.0c | 777.0c/860.0c | 74.25%/76.47% | 83.49%/69.23% | 27.27% | -289.0c |
| `score_m60__signed_move_15m_le_200` | False | 1636.0c | 798.0c | 1077.0c/559.0c | 75.08%/74.07% | 97.51%/97.74% | 62.50% | -239.0c |
| `score_m60_edge_m5__long_minus_short_move_30_5m_le_100` | False | 1633.0c | 682.0c | 880.0c/753.0c | 75.09%/76.27% | 87.54%/80.09% | 36.36% | -273.0c |
| `score_m60__signed_move_30m_le_200` | False | 1572.0c | 746.0c | 1018.0c/554.0c | 75.25%/74.41% | 94.39%/95.48% | 62.50% | -239.0c |
| `score_m60_edge_m5__signed_move_30m_le_125` | False | 1549.0c | 719.0c | 934.0c/615.0c | 74.63%/75.15% | 84.74%/76.47% | 27.27% | -236.0c |
| `score_m60__signed_move_15m_le_150` | False | 1520.0c | 673.0c | 908.0c/612.0c | 74.68%/74.30% | 95.95%/96.83% | 62.50% | -281.0c |
| `score_m60_edge_m5__signed_move_30m_le_75` | False | 1490.0c | 536.0c | 726.0c/764.0c | 74.69%/77.40% | 76.32%/66.06% | 9.09% | -331.0c |
| `book_margin` | False | 1430.0c | 746.0c | 1005.0c/425.0c | 70.85%/71.23% | 99.38%/99.10% | 62.50% | -332.0c |
| `book_margin_edge_m5` | False | 1430.0c | 746.0c | 1005.0c/425.0c | 70.85%/71.23% | 99.38%/99.10% | 62.50% | -332.0c |
| `score_m60_edge_m5__signed_move_30m_le_100` | False | 1430.0c | 548.0c | 876.0c/554.0c | 74.81%/75.16% | 81.62%/72.85% | 18.18% | -233.0c |
| `score_m60_edge_m5__signed_move_max_15_30m_le_100` | False | 1387.0c | 298.0c | 673.0c/714.0c | 73.88%/76.03% | 76.32%/66.06% | 18.18% | -248.0c |
| `book_margin__signed_move_15m_le_200` | False | 1375.0c | 580.0c | 891.0c/484.0c | 70.66%/71.56% | 98.75%/98.64% | 62.50% | -332.0c |
| `book_margin_edge_m5__signed_move_15m_le_200` | False | 1375.0c | 580.0c | 891.0c/484.0c | 70.66%/71.56% | 98.75%/98.64% | 62.50% | -332.0c |

## Split Summary

| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | median edge | median signed 30m | coverage | all splits | OOS |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| current | `book_margin` | 1005.0c/4.65% | 70.85%/99.38% | 764.0c | 114.0c | 127.0c | -2.5c | 4.1c | True | True | True |
| v21 | `book_margin` | 425.0c/2.80% | 71.23%/99.10% | -80.0c | 212.0c | 293.0c | -2.5c | 17.1c | True | False | True |
| current | `book_margin__signed_move_15m_le_200` | 891.0c/4.14% | 70.66%/98.75% | 816.0c | 114.0c | -39.0c | -2.5c | 2.6c | True | False | False |
| v21 | `book_margin__signed_move_15m_le_200` | 484.0c/3.20% | 71.56%/98.64% | -21.0c | 212.0c | 293.0c | -2.5c | 15.2c | True | False | True |
| current | `book_margin__signed_move_30m_le_250` | 1069.0c/5.06% | 71.15%/97.20% | 861.0c | 114.0c | 94.0c | -2.5c | -2.4c | True | True | True |
| v21 | `book_margin__signed_move_30m_le_250` | 645.0c/4.34% | 72.43%/96.83% | 140.0c | 212.0c | 293.0c | -2.5c | 8.6c | True | True | True |
| current | `book_margin_edge_m5` | 1005.0c/4.65% | 70.85%/99.38% | 764.0c | 114.0c | 127.0c | -2.5c | 4.1c | True | True | True |
| v21 | `book_margin_edge_m5` | 425.0c/2.80% | 71.23%/99.10% | -80.0c | 212.0c | 293.0c | -2.5c | 17.1c | True | False | True |
| current | `book_margin_edge_m5__signed_move_15m_le_200` | 891.0c/4.14% | 70.66%/98.75% | 816.0c | 114.0c | -39.0c | -2.5c | 2.6c | True | False | False |
| v21 | `book_margin_edge_m5__signed_move_15m_le_200` | 484.0c/3.20% | 71.56%/98.64% | -21.0c | 212.0c | 293.0c | -2.5c | 15.2c | True | False | True |
| current | `book_margin_edge_m5__signed_move_30m_le_250` | 1069.0c/5.06% | 71.15%/97.20% | 861.0c | 114.0c | 94.0c | -2.5c | -2.4c | True | True | True |
| v21 | `book_margin_edge_m5__signed_move_30m_le_250` | 645.0c/4.34% | 72.43%/96.83% | 140.0c | 212.0c | 293.0c | -2.5c | 8.6c | True | True | True |
| current | `score_m60` | 1244.0c/5.47% | 75.47%/99.07% | 1010.0c | 280.0c | -46.0c | -4.1c | 24.0c | True | False | False |
| v21 | `score_m60` | 534.0c/3.43% | 73.85%/98.64% | -19.0c | 398.0c | 155.0c | -3.0c | 29.9c | True | False | True |
| current | `score_m60__long_minus_short_move_30_5m_le_150` | 1015.0c/4.62% | 75.41%/95.02% | 632.0c | 276.0c | 107.0c | -4.1c | 13.7c | True | True | True |
| v21 | `score_m60__long_minus_short_move_30_5m_le_150` | 641.0c/4.26% | 74.76%/95.02% | 106.0c | 380.0c | 155.0c | -3.0c | 20.2c | True | True | True |
| current | `score_m60__signed_move_15m_le_150` | 908.0c/4.11% | 74.68%/95.95% | 788.0c | 260.0c | -140.0c | -4.0c | 21.5c | True | False | False |
| v21 | `score_m60__signed_move_15m_le_150` | 612.0c/4.00% | 74.30%/96.83% | 59.0c | 398.0c | 155.0c | -3.1c | 24.3c | True | True | True |
| current | `score_m60__signed_move_15m_le_200` | 1077.0c/4.80% | 75.08%/97.51% | 832.0c | 280.0c | -35.0c | -4.1c | 22.7c | True | False | False |
| v21 | `score_m60__signed_move_15m_le_200` | 559.0c/3.62% | 74.07%/97.74% | 6.0c | 398.0c | 155.0c | -3.1c | 26.7c | True | True | True |
| current | `score_m60__signed_move_30m_le_200` | 1018.0c/4.67% | 75.25%/94.39% | 693.0c | 280.0c | 45.0c | -4.3c | 11.9c | True | True | True |
| v21 | `score_m60__signed_move_30m_le_200` | 554.0c/3.66% | 74.41%/95.48% | 133.0c | 266.0c | 155.0c | -3.1c | 20.8c | True | True | True |
| current | `score_m60__signed_move_30m_le_250` | 1176.0c/5.34% | 75.57%/95.64% | 745.0c | 280.0c | 151.0c | -4.1c | 16.2c | True | True | True |
| v21 | `score_m60__signed_move_30m_le_250` | 649.0c/4.26% | 74.65%/96.38% | 93.0c | 401.0c | 155.0c | -3.1c | 24.2c | True | True | True |
| current | `score_m60_edge_m5` | 1406.0c/6.42% | 75.90%/95.64% | 1176.0c | 155.0c | 75.0c | -2.7c | 30.5c | True | True | True |
| v21 | `score_m60_edge_m5` | 878.0c/6.45% | 76.32%/85.97% | 190.0c | 393.0c | 295.0c | -2.5c | 49.9c | True | True | True |
| current | `score_m60_edge_m5__long_minus_short_move_30_5m_le_100` | 880.0c/4.35% | 75.09%/87.54% | 783.0c | 61.0c | 36.0c | -2.7c | 16.2c | True | True | True |
| v21 | `score_m60_edge_m5__long_minus_short_move_30_5m_le_100` | 753.0c/5.91% | 76.27%/80.09% | 168.0c | 283.0c | 302.0c | -2.5c | 34.9c | False | True | True |
| current | `score_m60_edge_m5__long_minus_short_move_30_5m_le_150` | 1086.0c/5.14% | 75.77%/91.28% | 818.0c | 142.0c | 126.0c | -2.6c | 22.1c | True | True | True |
| v21 | `score_m60_edge_m5__long_minus_short_move_30_5m_le_150` | 811.0c/6.20% | 76.37%/82.35% | 236.0c | 280.0c | 295.0c | -2.5c | 38.8c | False | True | True |
| current | `score_m60_edge_m5__long_minus_short_move_30_5m_le_75` | 936.0c/4.78% | 75.65%/84.42% | 683.0c | 274.0c | -21.0c | -2.7c | 8.2c | False | False | False |
| v21 | `score_m60_edge_m5__long_minus_short_move_30_5m_le_75` | 930.0c/7.64% | 77.98%/76.02% | 482.0c | 134.0c | 314.0c | -2.5c | 23.1c | False | True | True |
| current | `score_m60_edge_m5__signed_move_15m_le_100` | 832.0c/4.27% | 74.09%/85.36% | 842.0c | 137.0c | -147.0c | -2.6c | 23.5c | False | False | False |
| v21 | `score_m60_edge_m5__signed_move_15m_le_100` | 900.0c/7.69% | 76.36%/74.66% | 389.0c | 228.0c | 283.0c | -2.5c | 28.9c | False | True | True |
| current | `score_m60_edge_m5__signed_move_15m_le_125` | 1092.0c/5.38% | 75.09%/88.79% | 1082.0c | 174.0c | -164.0c | -2.6c | 24.4c | True | False | False |
| v21 | `score_m60_edge_m5__signed_move_15m_le_125` | 1124.0c/9.16% | 77.46%/78.28% | 464.0c | 365.0c | 295.0c | -2.5c | 35.1c | False | True | True |
| current | `score_m60_edge_m5__signed_move_15m_le_150` | 1119.0c/5.41% | 75.17%/90.34% | 1085.0c | 184.0c | -150.0c | -2.7c | 25.4c | True | False | False |
| v21 | `score_m60_edge_m5__signed_move_15m_le_150` | 981.0c/7.71% | 76.54%/81.00% | 293.0c | 393.0c | 295.0c | -2.5c | 38.7c | False | True | True |
| current | `score_m60_edge_m5__signed_move_15m_le_200` | 1262.0c/6.03% | 75.25%/91.90% | 1061.0c | 216.0c | -15.0c | -2.7c | 26.4c | True | False | False |
| v21 | `score_m60_edge_m5__signed_move_15m_le_200` | 915.0c/6.99% | 76.50%/82.81% | 227.0c | 393.0c | 295.0c | -2.5c | 42.2c | False | True | True |
| current | `score_m60_edge_m5__signed_move_15m_le_75` | 777.0c/4.06% | 74.25%/83.49% | 659.0c | 128.0c | -10.0c | -2.8c | 19.8c | False | False | False |
| v21 | `score_m60_edge_m5__signed_move_15m_le_75` | 860.0c/7.93% | 76.47%/69.23% | 305.0c | 286.0c | 269.0c | -2.5c | 24.2c | False | True | True |
| current | `score_m60_edge_m5__signed_move_30m_le_100` | 876.0c/4.68% | 74.81%/81.62% | 668.0c | 178.0c | 30.0c | -2.8c | 4.8c | False | True | True |
| v21 | `score_m60_edge_m5__signed_move_30m_le_100` | 554.0c/4.80% | 75.16%/72.85% | 214.0c | -33.0c | 373.0c | -2.5c | 14.3c | False | False | False |
| current | `score_m60_edge_m5__signed_move_30m_le_125` | 934.0c/4.82% | 74.63%/84.74% | 687.0c | 243.0c | 4.0c | -2.7c | 12.6c | False | True | True |
| v21 | `score_m60_edge_m5__signed_move_30m_le_125` | 615.0c/5.09% | 75.15%/76.47% | 143.0c | 176.0c | 296.0c | -2.5c | 24.4c | False | True | True |
| current | `score_m60_edge_m5__signed_move_30m_le_150` | 881.0c/4.49% | 74.55%/85.67% | 686.0c | 151.0c | 44.0c | -2.6c | 16.2c | False | True | True |
| v21 | `score_m60_edge_m5__signed_move_30m_le_150` | 846.0c/6.96% | 76.47%/76.92% | 274.0c | 270.0c | 302.0c | -2.5c | 30.6c | False | True | True |
| current | `score_m60_edge_m5__signed_move_30m_le_200` | 1196.0c/5.86% | 75.52%/89.10% | 905.0c | 221.0c | 70.0c | -2.6c | 18.9c | True | True | True |
| v21 | `score_m60_edge_m5__signed_move_30m_le_200` | 848.0c/6.70% | 76.27%/80.09% | 290.0c | 263.0c | 295.0c | -2.5c | 38.0c | False | True | True |
| current | `score_m60_edge_m5__signed_move_30m_le_250` | 1372.0c/6.56% | 76.11%/91.28% | 974.0c | 232.0c | 166.0c | -2.6c | 24.2c | True | True | True |
| v21 | `score_m60_edge_m5__signed_move_30m_le_250` | 982.0c/7.49% | 77.05%/82.81% | 294.0c | 393.0c | 295.0c | -2.5c | 39.2c | False | True | True |
| current | `score_m60_edge_m5__signed_move_30m_le_75` | 726.0c/4.13% | 74.69%/76.32% | 588.0c | 240.0c | -102.0c | -2.6c | -8.3c | False | False | False |
| v21 | `score_m60_edge_m5__signed_move_30m_le_75` | 764.0c/7.25% | 77.40%/66.06% | 366.0c | -93.0c | 491.0c | -2.5c | 1.2c | False | False | False |
| current | `score_m60_edge_m5__signed_move_max_15_30m_le_100` | 673.0c/3.86% | 73.88%/76.32% | 596.0c | 145.0c | -68.0c | -2.7c | 4.0c | False | False | False |
| v21 | `score_m60_edge_m5__signed_move_max_15_30m_le_100` | 714.0c/6.87% | 76.03%/66.06% | 493.0c | -133.0c | 354.0c | -2.5c | 3.0c | False | False | False |
| current | `score_m60_edge_m5__signed_move_max_15_30m_le_150` | 800.0c/4.15% | 74.44%/84.11% | 702.0c | 151.0c | -53.0c | -2.5c | 15.8c | False | False | False |
| v21 | `score_m60_edge_m5__signed_move_max_15_30m_le_150` | 891.0c/7.55% | 76.51%/75.11% | 319.0c | 270.0c | 302.0c | -2.5c | 27.6c | False | True | True |
| current | `score_m60_edge_m5__signed_move_max_15_30m_le_200` | 1103.0c/5.52% | 75.09%/87.54% | 872.0c | 205.0c | 26.0c | -2.6c | 16.9c | False | True | True |
| v21 | `score_m60_edge_m5__signed_move_max_15_30m_le_200` | 787.0c/6.34% | 75.86%/78.73% | 229.0c | 263.0c | 295.0c | -2.5c | 36.2c | False | True | True |

## Block Summary

| dataset | candidate | blocks | positive+coverage blocks | worst block |
|---|---|---:|---:|---:|
| current | `book_margin` | 16 | 62.50% | -260.0c |
| current | `book_margin__signed_move_15m_le_200` | 16 | 62.50% | -278.0c |
| current | `book_margin__signed_move_30m_le_250` | 16 | 62.50% | -164.0c |
| current | `book_margin_edge_m5` | 16 | 62.50% | -260.0c |
| current | `book_margin_edge_m5__signed_move_15m_le_200` | 16 | 62.50% | -278.0c |
| current | `book_margin_edge_m5__signed_move_30m_le_250` | 16 | 62.50% | -164.0c |
| current | `score_m60` | 16 | 68.75% | -220.0c |
| current | `score_m60__long_minus_short_move_30_5m_le_150` | 16 | 62.50% | -197.0c |
| current | `score_m60__signed_move_15m_le_150` | 16 | 62.50% | -281.0c |
| current | `score_m60__signed_move_15m_le_200` | 16 | 62.50% | -239.0c |
| current | `score_m60__signed_move_30m_le_200` | 16 | 62.50% | -197.0c |
| current | `score_m60__signed_move_30m_le_250` | 16 | 62.50% | -197.0c |
| current | `score_m60_edge_m5` | 16 | 75.00% | -221.0c |
| current | `score_m60_edge_m5__long_minus_short_move_30_5m_le_100` | 16 | 62.50% | -232.0c |
| current | `score_m60_edge_m5__long_minus_short_move_30_5m_le_150` | 16 | 62.50% | -221.0c |
| current | `score_m60_edge_m5__long_minus_short_move_30_5m_le_75` | 16 | 50.00% | -163.0c |
| current | `score_m60_edge_m5__signed_move_15m_le_100` | 16 | 50.00% | -318.0c |
| current | `score_m60_edge_m5__signed_move_15m_le_125` | 16 | 56.25% | -291.0c |
| current | `score_m60_edge_m5__signed_move_15m_le_150` | 16 | 62.50% | -266.0c |
| current | `score_m60_edge_m5__signed_move_15m_le_200` | 16 | 68.75% | -224.0c |
| current | `score_m60_edge_m5__signed_move_15m_le_75` | 16 | 50.00% | -272.0c |
| current | `score_m60_edge_m5__signed_move_30m_le_100` | 16 | 37.50% | -155.0c |
| current | `score_m60_edge_m5__signed_move_30m_le_125` | 16 | 50.00% | -209.0c |
| current | `score_m60_edge_m5__signed_move_30m_le_150` | 16 | 50.00% | -155.0c |
| current | `score_m60_edge_m5__signed_move_30m_le_200` | 16 | 56.25% | -155.0c |
| current | `score_m60_edge_m5__signed_move_30m_le_250` | 16 | 62.50% | -144.0c |
| current | `score_m60_edge_m5__signed_move_30m_le_75` | 16 | 31.25% | -119.0c |
| current | `score_m60_edge_m5__signed_move_max_15_30m_le_100` | 16 | 37.50% | -190.0c |
| current | `score_m60_edge_m5__signed_move_max_15_30m_le_150` | 16 | 50.00% | -155.0c |
| current | `score_m60_edge_m5__signed_move_max_15_30m_le_200` | 16 | 50.00% | -155.0c |
| v21 | `book_margin` | 11 | 63.64% | -332.0c |
| v21 | `book_margin__signed_move_15m_le_200` | 11 | 63.64% | -332.0c |
| v21 | `book_margin__signed_move_30m_le_250` | 11 | 63.64% | -332.0c |
| v21 | `book_margin_edge_m5` | 11 | 63.64% | -332.0c |
| v21 | `book_margin_edge_m5__signed_move_15m_le_200` | 11 | 63.64% | -332.0c |
| v21 | `book_margin_edge_m5__signed_move_30m_le_250` | 11 | 63.64% | -332.0c |
| v21 | `score_m60` | 11 | 63.64% | -228.0c |
| v21 | `score_m60__long_minus_short_move_30_5m_le_150` | 11 | 63.64% | -239.0c |
| v21 | `score_m60__signed_move_15m_le_150` | 11 | 63.64% | -249.0c |
| v21 | `score_m60__signed_move_15m_le_200` | 11 | 63.64% | -228.0c |
| v21 | `score_m60__signed_move_30m_le_200` | 11 | 63.64% | -239.0c |
| v21 | `score_m60__signed_move_30m_le_250` | 11 | 63.64% | -228.0c |
| v21 | `score_m60_edge_m5` | 11 | 54.55% | -248.0c |
| v21 | `score_m60_edge_m5__long_minus_short_move_30_5m_le_100` | 11 | 36.36% | -273.0c |
| v21 | `score_m60_edge_m5__long_minus_short_move_30_5m_le_150` | 11 | 45.45% | -238.0c |
| v21 | `score_m60_edge_m5__long_minus_short_move_30_5m_le_75` | 11 | 18.18% | -287.0c |
| v21 | `score_m60_edge_m5__signed_move_15m_le_100` | 11 | 36.36% | -240.0c |
| v21 | `score_m60_edge_m5__signed_move_15m_le_125` | 11 | 45.45% | -225.0c |
| v21 | `score_m60_edge_m5__signed_move_15m_le_150` | 11 | 45.45% | -225.0c |
| v21 | `score_m60_edge_m5__signed_move_15m_le_200` | 11 | 45.45% | -238.0c |
| v21 | `score_m60_edge_m5__signed_move_15m_le_75` | 11 | 27.27% | -289.0c |
| v21 | `score_m60_edge_m5__signed_move_30m_le_100` | 11 | 18.18% | -233.0c |
| v21 | `score_m60_edge_m5__signed_move_30m_le_125` | 11 | 27.27% | -236.0c |
| v21 | `score_m60_edge_m5__signed_move_30m_le_150` | 11 | 27.27% | -239.0c |
| v21 | `score_m60_edge_m5__signed_move_30m_le_200` | 11 | 45.45% | -238.0c |
| v21 | `score_m60_edge_m5__signed_move_30m_le_250` | 11 | 54.55% | -238.0c |
| v21 | `score_m60_edge_m5__signed_move_30m_le_75` | 11 | 9.09% | -331.0c |
| v21 | `score_m60_edge_m5__signed_move_max_15_30m_le_100` | 11 | 18.18% | -248.0c |
| v21 | `score_m60_edge_m5__signed_move_max_15_30m_le_150` | 11 | 27.27% | -226.0c |
| v21 | `score_m60_edge_m5__signed_move_max_15_30m_le_200` | 11 | 45.45% | -238.0c |

## Worst Supported Slices

Only slices with at least `12` selected markets are shown.

| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask | median edge |
|---|---|---|---:|---:|---:|---:|---:|---:|
| current | `book_margin__signed_move_15m_le_150` | score=(0.625, 0.65] | 61 | 32/29 | -860.0c | -14.1c | 64.0c | -2.5c |
| current | `book_margin_edge_m5__signed_move_15m_le_150` | score=(0.625, 0.65] | 61 | 32/29 | -860.0c | -14.1c | 64.0c | -2.5c |
| current | `book_margin_edge_m5__signed_move_15m_le_125` | score=(0.625, 0.65] | 58 | 30/28 | -859.0c | -14.8c | 64.0c | -2.5c |
| current | `book_margin__signed_move_15m_le_125` | score=(0.625, 0.65] | 58 | 30/28 | -859.0c | -14.8c | 64.0c | -2.5c |
| current | `book_margin__signed_move_15m_le_100` | score=(0.625, 0.65] | 57 | 30/27 | -793.0c | -13.9c | 64.0c | -2.5c |
| current | `book_margin_edge_m5__signed_move_15m_le_100` | score=(0.625, 0.65] | 57 | 30/27 | -793.0c | -13.9c | 64.0c | -2.5c |
| current | `book_margin_edge_m5__long_minus_short_move_30_5m_le_100` | score=(0.625, 0.65] | 58 | 31/27 | -758.0c | -13.1c | 64.0c | -2.5c |
| current | `book_margin__long_minus_short_move_30_5m_le_100` | score=(0.625, 0.65] | 58 | 31/27 | -758.0c | -13.1c | 64.0c | -2.5c |
| v21 | `book_margin__signed_move_15m_le_125` | ask=(70.0, 80.0] | 44 | 26/18 | -738.0c | -16.8c | 73.0c | -2.5c |
| v21 | `book_margin_edge_m5__signed_move_15m_le_125` | ask=(70.0, 80.0] | 44 | 26/18 | -738.0c | -16.8c | 73.0c | -2.5c |
| v21 | `book_margin_edge_m5__signed_move_max_15_30m_le_150` | time=(-1.001, 600.0] | 40 | 21/19 | -737.0c | -18.4c | 66.0c | -2.5c |
| v21 | `book_margin__signed_move_max_15_30m_le_150` | time=(-1.001, 600.0] | 40 | 21/19 | -737.0c | -18.4c | 66.0c | -2.5c |
| current | `book_margin__signed_move_15m_le_150` | edge=(-5.0, -3.0] | 51 | 27/24 | -725.0c | -14.2c | 64.0c | -3.0c |
| current | `book_margin_edge_m5__signed_move_15m_le_150` | edge=(-5.0, -3.0] | 51 | 27/24 | -725.0c | -14.2c | 64.0c | -3.0c |
| current | `book_margin_edge_m5__signed_move_15m_le_100` | edge=(-5.0, -3.0] | 46 | 24/22 | -694.0c | -15.1c | 64.0c | -3.0c |
| current | `book_margin__signed_move_15m_le_100` | edge=(-5.0, -3.0] | 46 | 24/22 | -694.0c | -15.1c | 64.0c | -3.0c |
| v21 | `book_margin__signed_move_15m_le_125` | score=(0.7, 0.8] | 42 | 25/17 | -692.0c | -16.5c | 73.5c | -2.5c |
| current | `book_margin__long_minus_short_move_30_5m_le_75` | score=(0.625, 0.65] | 57 | 31/26 | -692.0c | -12.1c | 64.0c | -2.5c |

## Read

- No signed-momentum guard row clears the full robustness gate.
