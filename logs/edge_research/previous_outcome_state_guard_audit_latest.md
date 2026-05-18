# Previous Outcome State Guard Audit

Generated UTC: `20260504_162944Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Tests only causal previous-market outcome state available before the current entry.
- Strict pass requires current+v21 coverage, positive validation/holdout, positive all splits, and block stability.

## Combined Read

| candidate | combined net | combined OOS | current/v21 net | current/v21 acc | current/v21 cov | coverage | all splits | OOS | min block+ | worst block | robust |
|---|---:|---:|---:|---:|---:|---|---|---|---:|---:|---|
| `score_edge_m5` | 2164.0c | 703.0c | 1286.0c/878.0c | 75.48%/76.32% | 95.73%/85.97% | True | False | False | 54.55% | -248.0c | False |
| `score_edge_m5__skip_fade_after_flip` | 1742.0c | 380.0c | 754.0c/988.0c | 74.49%/78.52% | 75.30%/67.42% | False | False | False | 18.75% | -349.0c | False |
| `score_edge_m5__skip_follow_after_alternation` | 1666.0c | 597.0c | 962.0c/704.0c | 74.73%/75.58% | 85.67%/77.83% | False | False | False | 36.36% | -254.0c | False |
| `score_m60` | 1654.0c | 544.0c | 1120.0c/534.0c | 75.08%/73.85% | 99.09%/98.64% | True | False | False | 63.64% | -228.0c | False |
| `score_edge_m5__skip_follow_after_flip` | 1645.0c | 290.0c | 887.0c/758.0c | 75.00%/76.47% | 76.83%/69.23% | False | False | False | 9.09% | -297.0c | False |
| `score_edge_m5__skip_fade_3streak` | 1506.0c | 266.0c | 1133.0c/373.0c | 75.43%/73.45% | 88.11%/80.09% | False | False | False | 45.45% | -325.0c | False |
| `score_m60__skip_follow_after_flip` | 1402.0c | -11.0c | 781.0c/621.0c | 74.81%/75.00% | 81.10%/83.26% | False | False | False | 43.75% | -312.0c | False |
| `score_edge_m5__skip_fade_after_alternation` | 1365.0c | 316.0c | 606.0c/759.0c | 73.67%/76.33% | 85.67%/76.47% | False | False | False | 27.27% | -318.0c | False |
| `score_edge_m5__skip_follow_3streak` | 1327.0c | 586.0c | 905.0c/422.0c | 74.57%/74.42% | 88.72%/77.83% | False | False | True | 45.45% | -276.0c | False |
| `score_m60__skip_follow_after_alternation` | 1290.0c | 340.0c | 832.0c/458.0c | 74.49%/73.89% | 89.63%/91.86% | True | False | False | 63.64% | -286.0c | False |
| `book_margin__skip_follow_after_flip` | 1281.0c | 49.0c | 812.0c/469.0c | 70.91%/72.34% | 83.84%/85.07% | False | False | False | 45.45% | -369.0c | False |
| `book_edge_m5__skip_follow_after_flip` | 1281.0c | 49.0c | 812.0c/469.0c | 70.91%/72.34% | 83.84%/85.07% | False | False | False | 45.45% | -369.0c | False |
| `book_margin` | 1243.0c | 529.0c | 818.0c/425.0c | 70.25%/71.23% | 99.39%/99.10% | True | False | False | 62.50% | -332.0c | False |
| `book_edge_m5` | 1243.0c | 529.0c | 818.0c/425.0c | 70.25%/71.23% | 99.39%/99.10% | True | False | False | 62.50% | -332.0c | False |
| `score_m60__skip_fade_after_flip` | 1127.0c | -57.0c | 463.0c/664.0c | 73.76%/75.82% | 80.18%/82.35% | False | False | False | 36.36% | -397.0c | False |
| `book_margin__skip_fade_after_flip` | 1110.0c | 157.0c | 331.0c/779.0c | 69.37%/74.05% | 82.62%/83.71% | False | False | False | 37.50% | -347.0c | False |
| `book_edge_m5__skip_fade_after_flip` | 1110.0c | 157.0c | 331.0c/779.0c | 69.37%/74.05% | 82.62%/83.71% | False | False | False | 37.50% | -347.0c | False |
| `score_m60__skip_fade_3streak` | 1005.0c | 160.0c | 1071.0c/-66.0c | 75.08%/70.79% | 91.77%/91.40% | True | False | False | 63.64% | -331.0c | False |
| `score_m60__skip_fade_after_alternation` | 979.0c | 168.0c | 285.0c/694.0c | 72.79%/75.25% | 89.63%/91.40% | True | False | False | 54.55% | -392.0c | False |
| `score_edge_m5__skip_fade_2streak` | 971.0c | 264.0c | 729.0c/242.0c | 74.23%/72.78% | 79.27%/71.49% | False | False | False | 18.18% | -301.0c | False |
| `score_edge_m5__skip_follow_2streak` | 866.0c | 563.0c | 721.0c/145.0c | 74.34%/73.33% | 80.79%/67.87% | False | False | False | 0.00% | -246.0c | False |
| `score_m60__skip_follow_3streak` | 735.0c | 413.0c | 726.0c/9.0c | 74.17%/71.78% | 92.07%/91.40% | True | False | False | 36.36% | -324.0c | False |
| `book_margin__skip_follow_after_alternation` | 697.0c | 308.0c | 433.0c/264.0c | 69.33%/70.87% | 91.46%/93.21% | True | False | False | 54.55% | -332.0c | False |
| `book_edge_m5__skip_follow_after_alternation` | 697.0c | 308.0c | 433.0c/264.0c | 69.33%/70.87% | 91.46%/93.21% | True | False | False | 54.55% | -332.0c | False |
| `book_margin__skip_fade_after_alternation` | 592.0c | 219.0c | -49.0c/641.0c | 67.91%/72.68% | 90.24%/92.76% | True | False | False | 43.75% | -329.0c | False |
| `book_edge_m5__skip_fade_after_alternation` | 592.0c | 219.0c | -49.0c/641.0c | 67.91%/72.68% | 90.24%/92.76% | True | False | False | 43.75% | -329.0c | False |
| `score_edge_m5__skip_fade_prev1` | 549.0c | -59.0c | 197.0c/352.0c | 72.54%/74.36% | 58.84%/52.94% | False | False | False | 0.00% | -389.0c | False |
| `book_margin__skip_fade_3streak` | 538.0c | 125.0c | 792.0c/-254.0c | 70.63%/68.29% | 92.38%/92.76% | True | False | False | 45.45% | -481.0c | False |
| `book_edge_m5__skip_fade_3streak` | 538.0c | 125.0c | 792.0c/-254.0c | 70.63%/68.29% | 92.38%/92.76% | True | False | False | 45.45% | -481.0c | False |
| `score_edge_m5__only_follow_prev1` | 527.0c | -59.0c | 182.0c/345.0c | 72.40%/74.14% | 58.54%/52.49% | False | False | False | 0.00% | -404.0c | False |
| `score_edge_m5__skip_follow_prev1` | 312.0c | 150.0c | 287.0c/25.0c | 73.27%/72.57% | 61.59%/51.13% | False | False | False | 0.00% | -284.0c | False |
| `score_edge_m5__only_fade_prev1` | 290.0c | 150.0c | 272.0c/18.0c | 73.13%/72.32% | 61.28%/50.68% | False | False | False | 0.00% | -284.0c | False |
| `book_margin__skip_follow_3streak` | 234.0c | 253.0c | 345.0c/-111.0c | 68.93%/69.12% | 94.21%/92.31% | True | False | False | 50.00% | -463.0c | False |
| `book_edge_m5__skip_follow_3streak` | 234.0c | 253.0c | 345.0c/-111.0c | 68.93%/69.12% | 94.21%/92.31% | True | False | False | 50.00% | -463.0c | False |
| `score_m60__skip_follow_2streak` | 215.0c | 415.0c | 562.0c/-347.0c | 74.01%/70.11% | 84.45%/83.26% | False | False | False | 18.18% | -257.0c | False |
| `score_m60__skip_fade_2streak` | 185.0c | 250.0c | 570.0c/-385.0c | 73.53%/68.89% | 82.93%/81.45% | True | False | False | 43.75% | -347.0c | False |
| `score_m60__only_fade_prev1` | -7.0c | -140.0c | 260.0c/-267.0c | 73.61%/70.47% | 65.85%/67.42% | False | False | False | 0.00% | -285.0c | False |
| `score_m60__skip_follow_prev1` | -72.0c | -140.0c | 188.0c/-260.0c | 73.27%/70.67% | 66.16%/67.87% | False | False | False | 0.00% | -285.0c | False |
| `book_margin__only_fade_prev1` | -155.0c | -193.0c | 255.0c/-410.0c | 69.49%/67.74% | 71.95%/70.14% | False | False | False | 18.18% | -360.0c | False |
| `book_edge_m5__only_fade_prev1` | -155.0c | -193.0c | 255.0c/-410.0c | 69.49%/67.74% | 71.95%/70.14% | False | False | False | 18.18% | -360.0c | False |

## Split Summary

| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | median edge | coverage | all splits | OOS |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---|
| current | `book_edge_m5` | 818.0c/3.70% | 70.25%/99.39% | 794.0c | 62.0c | -38.0c | NA | True | False | False |
| v21 | `book_edge_m5` | 425.0c/2.80% | 71.23%/99.10% | -80.0c | 212.0c | 293.0c | NA | True | False | True |
| current | `book_edge_m5__only_fade_prev1` | 255.0c/1.58% | 69.49%/71.95% | 175.0c | 714.0c | -634.0c | NA | False | False | False |
| v21 | `book_edge_m5__only_fade_prev1` | -410.0c/-3.76% | 67.74%/70.14% | -137.0c | -347.0c | 74.0c | NA | False | False | False |
| current | `book_edge_m5__only_follow_prev1` | -82.0c/-0.54% | 68.02%/67.68% | 151.0c | -440.0c | 207.0c | NA | False | False | False |
| v21 | `book_edge_m5__only_follow_prev1` | -247.0c/-2.36% | 68.46%/67.42% | -469.0c | 170.0c | 52.0c | NA | False | False | True |
| current | `book_edge_m5__skip_fade_2streak` | 337.0c/1.79% | 69.06%/84.76% | 234.0c | 132.0c | -29.0c | NA | True | False | False |
| v21 | `book_edge_m5__skip_fade_2streak` | -565.0c/-4.39% | 66.49%/83.71% | -823.0c | 113.0c | 145.0c | NA | True | False | True |
| current | `book_edge_m5__skip_fade_3streak` | 792.0c/3.84% | 70.63%/92.38% | 809.0c | 160.0c | -177.0c | NA | True | False | False |
| v21 | `book_edge_m5__skip_fade_3streak` | -254.0c/-1.78% | 68.29%/92.76% | -396.0c | 141.0c | 1.0c | NA | True | False | True |
| current | `book_edge_m5__skip_fade_after_alternation` | -49.0c/-0.24% | 67.91%/90.24% | 392.0c | -354.0c | -87.0c | NA | True | False | False |
| v21 | `book_edge_m5__skip_fade_after_alternation` | 641.0c/4.50% | 72.68%/92.76% | -19.0c | 270.0c | 390.0c | NA | True | False | True |
| current | `book_edge_m5__skip_fade_after_flip` | 331.0c/1.79% | 69.37%/82.62% | 643.0c | -510.0c | 198.0c | NA | False | False | False |
| v21 | `book_edge_m5__skip_fade_after_flip` | 779.0c/6.03% | 74.05%/83.71% | 310.0c | 269.0c | 200.0c | NA | False | True | True |
| current | `book_edge_m5__skip_fade_prev1` | -150.0c/-0.98% | 67.71%/67.99% | 83.0c | -440.0c | 207.0c | NA | False | False | False |
| v21 | `book_edge_m5__skip_fade_prev1` | -240.0c/-2.28% | 68.67%/67.87% | -462.0c | 170.0c | 52.0c | NA | False | False | True |
| current | `book_edge_m5__skip_follow_2streak` | 291.0c/1.48% | 69.10%/87.80% | 149.0c | 377.0c | -235.0c | NA | True | False | False |
| v21 | `book_edge_m5__skip_follow_2streak` | -447.0c/-3.43% | 67.38%/84.62% | -592.0c | -117.0c | 262.0c | NA | True | False | False |
| current | `book_edge_m5__skip_follow_3streak` | 345.0c/1.65% | 68.93%/94.21% | 277.0c | 159.0c | -91.0c | NA | True | False | False |
| v21 | `book_edge_m5__skip_follow_3streak` | -111.0c/-0.78% | 69.12%/92.31% | -296.0c | -40.0c | 225.0c | NA | True | False | False |
| current | `book_edge_m5__skip_follow_after_alternation` | 433.0c/2.13% | 69.33%/91.46% | 422.0c | 325.0c | -314.0c | NA | True | False | False |
| v21 | `book_edge_m5__skip_follow_after_alternation` | 264.0c/1.84% | 70.87%/93.21% | -33.0c | 30.0c | 267.0c | NA | True | False | True |
| current | `book_edge_m5__skip_follow_after_flip` | 812.0c/4.35% | 70.91%/83.84% | 850.0c | 399.0c | -437.0c | NA | False | False | False |
| v21 | `book_edge_m5__skip_follow_after_flip` | 469.0c/3.57% | 72.34%/85.07% | 382.0c | -18.0c | 105.0c | NA | False | False | False |
| current | `book_edge_m5__skip_follow_prev1` | 187.0c/1.15% | 69.20%/72.26% | 107.0c | 714.0c | -634.0c | NA | False | False | False |
| v21 | `book_edge_m5__skip_follow_prev1` | -403.0c/-3.66% | 67.95%/70.59% | -130.0c | -347.0c | 74.0c | NA | False | False | False |
| current | `book_margin` | 818.0c/3.70% | 70.25%/99.39% | 794.0c | 62.0c | -38.0c | NA | True | False | False |
| v21 | `book_margin` | 425.0c/2.80% | 71.23%/99.10% | -80.0c | 212.0c | 293.0c | NA | True | False | True |
| current | `book_margin__only_fade_prev1` | 255.0c/1.58% | 69.49%/71.95% | 175.0c | 714.0c | -634.0c | NA | False | False | False |
| v21 | `book_margin__only_fade_prev1` | -410.0c/-3.76% | 67.74%/70.14% | -137.0c | -347.0c | 74.0c | NA | False | False | False |
| current | `book_margin__only_follow_prev1` | -82.0c/-0.54% | 68.02%/67.68% | 151.0c | -440.0c | 207.0c | NA | False | False | False |
| v21 | `book_margin__only_follow_prev1` | -247.0c/-2.36% | 68.46%/67.42% | -469.0c | 170.0c | 52.0c | NA | False | False | True |
| current | `book_margin__skip_fade_2streak` | 337.0c/1.79% | 69.06%/84.76% | 234.0c | 132.0c | -29.0c | NA | True | False | False |
| v21 | `book_margin__skip_fade_2streak` | -565.0c/-4.39% | 66.49%/83.71% | -823.0c | 113.0c | 145.0c | NA | True | False | True |
| current | `book_margin__skip_fade_3streak` | 792.0c/3.84% | 70.63%/92.38% | 809.0c | 160.0c | -177.0c | NA | True | False | False |
| v21 | `book_margin__skip_fade_3streak` | -254.0c/-1.78% | 68.29%/92.76% | -396.0c | 141.0c | 1.0c | NA | True | False | True |
| current | `book_margin__skip_fade_after_alternation` | -49.0c/-0.24% | 67.91%/90.24% | 392.0c | -354.0c | -87.0c | NA | True | False | False |
| v21 | `book_margin__skip_fade_after_alternation` | 641.0c/4.50% | 72.68%/92.76% | -19.0c | 270.0c | 390.0c | NA | True | False | True |
| current | `book_margin__skip_fade_after_flip` | 331.0c/1.79% | 69.37%/82.62% | 643.0c | -510.0c | 198.0c | NA | False | False | False |
| v21 | `book_margin__skip_fade_after_flip` | 779.0c/6.03% | 74.05%/83.71% | 310.0c | 269.0c | 200.0c | NA | False | True | True |
| current | `book_margin__skip_fade_prev1` | -150.0c/-0.98% | 67.71%/67.99% | 83.0c | -440.0c | 207.0c | NA | False | False | False |
| v21 | `book_margin__skip_fade_prev1` | -240.0c/-2.28% | 68.67%/67.87% | -462.0c | 170.0c | 52.0c | NA | False | False | True |
| current | `book_margin__skip_follow_2streak` | 291.0c/1.48% | 69.10%/87.80% | 149.0c | 377.0c | -235.0c | NA | True | False | False |
| v21 | `book_margin__skip_follow_2streak` | -447.0c/-3.43% | 67.38%/84.62% | -592.0c | -117.0c | 262.0c | NA | True | False | False |
| current | `book_margin__skip_follow_3streak` | 345.0c/1.65% | 68.93%/94.21% | 277.0c | 159.0c | -91.0c | NA | True | False | False |
| v21 | `book_margin__skip_follow_3streak` | -111.0c/-0.78% | 69.12%/92.31% | -296.0c | -40.0c | 225.0c | NA | True | False | False |
| current | `book_margin__skip_follow_after_alternation` | 433.0c/2.13% | 69.33%/91.46% | 422.0c | 325.0c | -314.0c | NA | True | False | False |
| v21 | `book_margin__skip_follow_after_alternation` | 264.0c/1.84% | 70.87%/93.21% | -33.0c | 30.0c | 267.0c | NA | True | False | True |
| current | `book_margin__skip_follow_after_flip` | 812.0c/4.35% | 70.91%/83.84% | 850.0c | 399.0c | -437.0c | NA | False | False | False |
| v21 | `book_margin__skip_follow_after_flip` | 469.0c/3.57% | 72.34%/85.07% | 382.0c | -18.0c | 105.0c | NA | False | False | False |
| current | `book_margin__skip_follow_prev1` | 187.0c/1.15% | 69.20%/72.26% | 107.0c | 714.0c | -634.0c | NA | False | False | False |
| v21 | `book_margin__skip_follow_prev1` | -403.0c/-3.66% | 67.95%/70.59% | -130.0c | -347.0c | 74.0c | NA | False | False | False |
| current | `score_edge_m5` | 1286.0c/5.74% | 75.48%/95.73% | 1271.0c | 114.0c | -99.0c | NA | True | False | False |
| v21 | `score_edge_m5` | 878.0c/6.45% | 76.32%/85.97% | 190.0c | 393.0c | 295.0c | NA | True | True | True |
| current | `score_edge_m5__only_fade_prev1` | 272.0c/1.89% | 73.13%/61.28% | 211.0c | 493.0c | -432.0c | NA | False | False | False |
| v21 | `score_edge_m5__only_fade_prev1` | 18.0c/0.22% | 72.32%/50.68% | -71.0c | -125.0c | 214.0c | NA | False | False | False |
| current | `score_edge_m5__only_follow_prev1` | 182.0c/1.33% | 72.40%/58.54% | 521.0c | -436.0c | 97.0c | NA | False | False | False |
| v21 | `score_edge_m5__only_follow_prev1` | 345.0c/4.18% | 74.14%/52.49% | 65.0c | 295.0c | -15.0c | NA | False | False | False |
| current | `score_edge_m5__skip_fade_2streak` | 729.0c/3.93% | 74.23%/79.27% | 857.0c | 26.0c | -154.0c | NA | False | False | False |
| v21 | `score_edge_m5__skip_fade_2streak` | 242.0c/2.15% | 72.78%/71.49% | -150.0c | 279.0c | 113.0c | NA | False | False | True |
| current | `score_edge_m5__skip_fade_3streak` | 1133.0c/5.48% | 75.43%/88.11% | 1307.0c | 17.0c | -191.0c | NA | True | False | False |
| v21 | `score_edge_m5__skip_fade_3streak` | 373.0c/2.95% | 73.45%/80.09% | -67.0c | 285.0c | 155.0c | NA | False | False | True |
| current | `score_edge_m5__skip_fade_after_alternation` | 606.0c/3.02% | 73.67%/85.67% | 935.0c | -195.0c | -134.0c | NA | True | False | False |
| v21 | `score_edge_m5__skip_fade_after_alternation` | 759.0c/6.25% | 76.33%/76.47% | 114.0c | 407.0c | 238.0c | NA | False | True | True |
| current | `score_edge_m5__skip_fade_after_flip` | 754.0c/4.27% | 74.49%/75.30% | 950.0c | -348.0c | 152.0c | NA | False | False | False |
| v21 | `score_edge_m5__skip_fade_after_flip` | 988.0c/9.22% | 78.52%/67.42% | 412.0c | 409.0c | 167.0c | NA | False | True | True |
| current | `score_edge_m5__skip_fade_prev1` | 197.0c/1.43% | 72.54%/58.84% | 536.0c | -436.0c | 97.0c | NA | False | False | False |
| v21 | `score_edge_m5__skip_fade_prev1` | 352.0c/4.22% | 74.36%/52.94% | 72.0c | 295.0c | -15.0c | NA | False | False | False |
| current | `score_edge_m5__skip_follow_2streak` | 721.0c/3.80% | 74.34%/80.79% | 574.0c | 232.0c | -85.0c | NA | False | False | False |
| v21 | `score_edge_m5__skip_follow_2streak` | 145.0c/1.34% | 73.33%/67.87% | -271.0c | 35.0c | 381.0c | NA | False | False | True |
| current | `score_edge_m5__skip_follow_3streak` | 905.0c/4.35% | 74.57%/88.72% | 791.0c | 75.0c | 39.0c | NA | True | True | True |
| v21 | `score_edge_m5__skip_follow_3streak` | 422.0c/3.41% | 74.42%/77.83% | -50.0c | 136.0c | 336.0c | NA | False | False | True |
| current | `score_edge_m5__skip_follow_after_alternation` | 962.0c/4.80% | 74.73%/85.67% | 888.0c | 377.0c | -303.0c | NA | False | False | False |
| v21 | `score_edge_m5__skip_follow_after_alternation` | 704.0c/5.73% | 75.58%/77.83% | 181.0c | 291.0c | 232.0c | NA | False | True | True |
| current | `score_edge_m5__skip_follow_after_flip` | 887.0c/4.92% | 75.00%/76.83% | 958.0c | 375.0c | -446.0c | NA | False | False | False |
| v21 | `score_edge_m5__skip_follow_after_flip` | 758.0c/6.93% | 76.47%/69.23% | 397.0c | 233.0c | 128.0c | NA | False | True | True |
| current | `score_edge_m5__skip_follow_prev1` | 287.0c/1.98% | 73.27%/61.59% | 226.0c | 493.0c | -432.0c | NA | False | False | False |
| v21 | `score_edge_m5__skip_follow_prev1` | 25.0c/0.31% | 72.57%/51.13% | -64.0c | -125.0c | 214.0c | NA | False | False | False |
| current | `score_m60` | 1120.0c/4.81% | 75.08%/99.09% | 1129.0c | 112.0c | -121.0c | NA | True | False | False |
| v21 | `score_m60` | 534.0c/3.43% | 73.85%/98.64% | -19.0c | 398.0c | 155.0c | NA | True | False | True |
| current | `score_m60__only_fade_prev1` | 260.0c/1.66% | 73.61%/65.85% | 197.0c | 561.0c | -498.0c | NA | False | False | False |
| v21 | `score_m60__only_fade_prev1` | -267.0c/-2.48% | 70.47%/67.42% | -64.0c | -200.0c | -3.0c | NA | False | False | False |
| current | `score_m60__only_follow_prev1` | -15.0c/-0.10% | 71.77%/63.72% | 376.0c | -560.0c | 169.0c | NA | False | False | False |
| v21 | `score_m60__only_follow_prev1` | -291.0c/-2.86% | 69.72%/64.25% | -331.0c | 85.0c | -45.0c | NA | False | False | False |
| current | `score_m60__skip_fade_2streak` | 570.0c/2.93% | 73.53%/82.93% | 619.0c | 48.0c | -97.0c | NA | True | False | False |
| v21 | `score_m60__skip_fade_2streak` | -385.0c/-3.01% | 68.89%/81.45% | -684.0c | 234.0c | 65.0c | NA | True | False | True |
| current | `score_m60__skip_fade_3streak` | 1071.0c/4.97% | 75.08%/91.77% | 1175.0c | 49.0c | -153.0c | NA | True | False | False |
| v21 | `score_m60__skip_fade_3streak` | -66.0c/-0.46% | 70.79%/91.40% | -330.0c | 240.0c | 24.0c | NA | True | False | True |
| current | `score_m60__skip_fade_after_alternation` | 285.0c/1.35% | 72.79%/89.63% | 780.0c | -343.0c | -152.0c | NA | True | False | False |
| v21 | `score_m60__skip_fade_after_alternation` | 694.0c/4.78% | 75.25%/91.40% | 31.0c | 422.0c | 241.0c | NA | True | True | True |
| current | `score_m60__skip_fade_after_flip` | 463.0c/2.44% | 73.76%/80.18% | 814.0c | -496.0c | 145.0c | NA | False | False | False |
| v21 | `score_m60__skip_fade_after_flip` | 664.0c/5.05% | 75.82%/82.35% | 370.0c | 249.0c | 45.0c | NA | False | True | True |
| current | `score_m60__skip_fade_prev1` | -87.0c/-0.58% | 71.43%/64.02% | 304.0c | -560.0c | 169.0c | NA | False | False | False |
| v21 | `score_m60__skip_fade_prev1` | -284.0c/-2.76% | 69.93%/64.71% | -324.0c | 85.0c | -45.0c | NA | False | False | False |
| current | `score_m60__skip_follow_2streak` | 562.0c/2.82% | 74.01%/84.45% | 336.0c | 310.0c | -84.0c | NA | False | False | False |
| v21 | `score_m60__skip_follow_2streak` | -347.0c/-2.62% | 70.11%/83.26% | -536.0c | 56.0c | 133.0c | NA | False | False | True |
| current | `score_m60__skip_follow_3streak` | 726.0c/3.35% | 74.17%/92.07% | 650.0c | 85.0c | -9.0c | NA | True | False | False |
| v21 | `score_m60__skip_follow_3streak` | 9.0c/0.06% | 71.78%/91.40% | -328.0c | 141.0c | 196.0c | NA | True | False | True |
| current | `score_m60__skip_follow_after_alternation` | 832.0c/3.95% | 74.49%/89.63% | 847.0c | 305.0c | -320.0c | NA | True | False | False |
| v21 | `score_m60__skip_follow_after_alternation` | 458.0c/3.15% | 73.89%/91.86% | 103.0c | 216.0c | 139.0c | NA | True | True | True |
| current | `score_m60__skip_follow_after_flip` | 781.0c/4.08% | 74.81%/81.10% | 953.0c | 363.0c | -535.0c | NA | False | False | False |
| v21 | `score_m60__skip_follow_after_flip` | 621.0c/4.71% | 75.00%/83.26% | 460.0c | 142.0c | 19.0c | NA | False | True | True |
| current | `score_m60__skip_follow_prev1` | 188.0c/1.20% | 73.27%/66.16% | 125.0c | 561.0c | -498.0c | NA | False | False | False |
| v21 | `score_m60__skip_follow_prev1` | -260.0c/-2.39% | 70.67%/67.87% | -57.0c | -200.0c | -3.0c | NA | False | False | False |

## Read

- No previous-outcome guard clears the cross-dataset robustness gates.
