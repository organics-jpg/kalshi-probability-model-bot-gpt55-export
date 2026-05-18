# Book Cost/Score Hole Audit

Generated UTC: `20260504_125343Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Tests fixed cost/score vetoes on high-coverage book/score priors.
- Strict pass requires current+v21 coverage, positive validation/holdout, positive all splits, and block stability.

## Combined Read

| candidate | robust | combined net | OOS net | current/v21 net | current/v21 acc | current/v21 cov | min block+ | worst block |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `score_highask_needs_score75` | False | 2083.0c | 676.0c | 1215.0c/868.0c | 75.56%/76.85% | 99.04%/97.74% | 63.64% | -318.0c |
| `score_skip_score_lt70_ask_ge70` | False | 2030.0c | 901.0c | 1294.0c/736.0c | 75.56%/75.58% | 99.04%/98.19% | 63.64% | -249.0c |
| `score_highask_needs_score70` | False | 2030.0c | 901.0c | 1294.0c/736.0c | 75.56%/75.58% | 99.04%/98.19% | 63.64% | -249.0c |
| `score_ask_le70` | False | 1987.0c | 645.0c | 1332.0c/655.0c | 73.11%/71.35% | 84.08%/77.38% | 27.27% | -350.0c |
| `score_skip_score_lt65_ask_ge70` | False | 1804.0c | 902.0c | 1243.0c/561.0c | 75.56%/74.31% | 99.04%/98.64% | 63.64% | -250.0c |
| `score_min60_locked_equiv` | False | 1769.0c | 893.0c | 1235.0c/534.0c | 75.56%/73.85% | 99.04%/98.64% | 63.64% | -228.0c |
| `book_ask_le70` | False | 1568.0c | 497.0c | 807.0c/761.0c | 68.94%/70.50% | 93.31%/90.50% | 54.55% | -414.0c |
| `book_ask_le65` | False | 1550.0c | 438.0c | 952.0c/598.0c | 68.32%/68.83% | 83.44%/69.68% | 9.09% | -335.0c |
| `book_highask_needs_score75` | False | 1468.0c | 534.0c | 850.0c/618.0c | 70.51%/72.60% | 99.36%/99.10% | 62.50% | -358.0c |
| `book_margin_locked_equiv` | False | 1410.0c | 749.0c | 985.0c/425.0c | 70.83%/71.23% | 99.36%/99.10% | 62.50% | -332.0c |
| `book_skip_score_lt65_ask_ge70` | False | 1410.0c | 749.0c | 985.0c/425.0c | 70.83%/71.23% | 99.36%/99.10% | 62.50% | -332.0c |
| `book_skip_score_lt70_ask_ge70` | False | 1353.0c | 736.0c | 980.0c/373.0c | 70.83%/71.23% | 99.36%/99.10% | 62.50% | -333.0c |
| `book_highask_needs_score70` | False | 1353.0c | 736.0c | 980.0c/373.0c | 70.83%/71.23% | 99.36%/99.10% | 62.50% | -333.0c |
| `score_skip_score625_65_ask60_80` | False | 1190.0c | 548.0c | 1102.0c/88.0c | 76.21%/74.19% | 99.04%/98.19% | 62.50% | -297.0c |
| `score_ask_le65` | False | 722.0c | -292.0c | 413.0c/309.0c | 67.18%/68.18% | 62.10%/49.77% | 0.00% | -187.0c |
| `score_skip_score60_65_ask60_80` | False | 603.0c | 589.0c | 813.0c/-210.0c | 79.55%/76.50% | 98.09%/98.19% | 45.45% | -346.0c |
| `book_skip_score625_65_ask60_80` | False | 582.0c | 365.0c | 555.0c/27.0c | 70.51%/71.10% | 99.36%/98.64% | 54.55% | -384.0c |
| `book_skip_score60_65_ask60_80` | False | 135.0c | 566.0c | 227.0c/-92.0c | 73.23%/74.31% | 98.73%/98.64% | 54.55% | -435.0c |

## Split Summary

| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | coverage | all splits | OOS |
|---|---|---:|---:|---:|---:|---:|---|---|---|
| current | `book_ask_le65` | 952.0c/5.62% | 68.32%/83.44% | 930.0c | -107.0c | 129.0c | True | False | False |
| v21 | `book_ask_le65` | 598.0c/5.98% | 68.83%/69.68% | 182.0c | 90.0c | 326.0c | False | True | True |
| current | `book_ask_le70` | 807.0c/4.16% | 68.94%/93.31% | 866.0c | -167.0c | 108.0c | True | False | False |
| v21 | `book_ask_le70` | 761.0c/5.71% | 70.50%/90.50% | 205.0c | 164.0c | 392.0c | True | True | True |
| current | `book_highask_needs_score70` | 980.0c/4.64% | 70.83%/99.36% | 743.0c | -16.0c | 253.0c | True | False | False |
| v21 | `book_highask_needs_score70` | 373.0c/2.45% | 71.23%/99.10% | -126.0c | 211.0c | 288.0c | True | False | True |
| current | `book_highask_needs_score75` | 850.0c/4.02% | 70.51%/99.36% | 737.0c | -34.0c | 147.0c | True | False | False |
| v21 | `book_highask_needs_score75` | 618.0c/4.04% | 72.60%/99.10% | 197.0c | 139.0c | 282.0c | True | True | True |
| current | `book_margin_locked_equiv` | 985.0c/4.66% | 70.83%/99.36% | 741.0c | -11.0c | 255.0c | True | False | False |
| v21 | `book_margin_locked_equiv` | 425.0c/2.80% | 71.23%/99.10% | -80.0c | 212.0c | 293.0c | True | False | True |
| current | `book_skip_score60_65_ask60_80` | 227.0c/1.01% | 73.23%/98.73% | 103.0c | 115.0c | 9.0c | True | True | True |
| v21 | `book_skip_score60_65_ask60_80` | -92.0c/-0.56% | 74.31%/98.64% | -534.0c | 279.0c | 163.0c | True | False | True |
| current | `book_skip_score625_65_ask60_80` | 555.0c/2.59% | 70.51%/99.36% | 539.0c | -55.0c | 71.0c | True | False | False |
| v21 | `book_skip_score625_65_ask60_80` | 27.0c/0.17% | 71.10%/98.64% | -322.0c | 121.0c | 228.0c | True | False | True |
| current | `book_skip_score_lt65_ask_ge70` | 985.0c/4.66% | 70.83%/99.36% | 741.0c | -11.0c | 255.0c | True | False | False |
| v21 | `book_skip_score_lt65_ask_ge70` | 425.0c/2.80% | 71.23%/99.10% | -80.0c | 212.0c | 293.0c | True | False | True |
| current | `book_skip_score_lt70_ask_ge70` | 980.0c/4.64% | 70.83%/99.36% | 743.0c | -16.0c | 253.0c | True | False | False |
| v21 | `book_skip_score_lt70_ask_ge70` | 373.0c/2.45% | 71.23%/99.10% | -126.0c | 211.0c | 288.0c | True | False | True |
| current | `score_ask_le65` | 413.0c/3.26% | 67.18%/62.10% | 897.0c | -191.0c | -293.0c | False | False | False |
| v21 | `score_ask_le65` | 309.0c/4.30% | 68.18%/49.77% | 117.0c | 29.0c | 163.0c | False | True | True |
| current | `score_ask_le70` | 1332.0c/7.41% | 73.11%/84.08% | 1154.0c | 151.0c | 27.0c | True | True | True |
| v21 | `score_ask_le70` | 655.0c/5.67% | 71.35%/77.38% | 188.0c | 165.0c | 302.0c | False | True | True |
| current | `score_highask_needs_score70` | 1294.0c/5.83% | 75.56%/99.04% | 1084.0c | 157.0c | 53.0c | True | True | True |
| v21 | `score_highask_needs_score70` | 736.0c/4.70% | 75.58%/98.19% | 45.0c | 376.0c | 315.0c | True | True | True |
| current | `score_highask_needs_score75` | 1215.0c/5.45% | 75.56%/99.04% | 1171.0c | 122.0c | -78.0c | True | False | False |
| v21 | `score_highask_needs_score75` | 868.0c/5.52% | 76.85%/97.74% | 236.0c | 343.0c | 289.0c | True | True | True |
| current | `score_min60_locked_equiv` | 1235.0c/5.55% | 75.56%/99.04% | 895.0c | 259.0c | 81.0c | True | True | True |
| v21 | `score_min60_locked_equiv` | 534.0c/3.43% | 73.85%/98.64% | -19.0c | 398.0c | 155.0c | True | False | True |
| current | `score_skip_score60_65_ask60_80` | 813.0c/3.43% | 79.55%/98.09% | 654.0c | 74.0c | 85.0c | True | True | True |
| v21 | `score_skip_score60_65_ask60_80` | -210.0c/-1.25% | 76.50%/98.19% | -640.0c | 370.0c | 60.0c | True | False | True |
| current | `score_skip_score625_65_ask60_80` | 1102.0c/4.88% | 76.21%/99.04% | 835.0c | 37.0c | 230.0c | True | True | True |
| v21 | `score_skip_score625_65_ask60_80` | 88.0c/0.55% | 74.19%/98.19% | -193.0c | 198.0c | 83.0c | True | False | True |
| current | `score_skip_score_lt65_ask_ge70` | 1243.0c/5.58% | 75.56%/99.04% | 982.0c | 179.0c | 82.0c | True | True | True |
| v21 | `score_skip_score_lt65_ask_ge70` | 561.0c/3.59% | 74.31%/98.64% | -80.0c | 398.0c | 243.0c | True | False | True |
| current | `score_skip_score_lt70_ask_ge70` | 1294.0c/5.83% | 75.56%/99.04% | 1084.0c | 157.0c | 53.0c | True | True | True |
| v21 | `score_skip_score_lt70_ask_ge70` | 736.0c/4.70% | 75.58%/98.19% | 45.0c | 376.0c | 315.0c | True | True | True |

## Block Summary

| dataset | candidate | blocks | positive+coverage blocks | worst block |
|---|---|---:|---:|---:|
| current | `book_ask_le65` | 16 | 43.75% | -335.0c |
| current | `book_ask_le70` | 16 | 62.50% | -414.0c |
| current | `book_highask_needs_score70` | 16 | 62.50% | -260.0c |
| current | `book_highask_needs_score75` | 16 | 62.50% | -358.0c |
| current | `book_margin_locked_equiv` | 16 | 62.50% | -260.0c |
| current | `book_skip_score60_65_ask60_80` | 16 | 56.25% | -435.0c |
| current | `book_skip_score625_65_ask60_80` | 16 | 62.50% | -293.0c |
| current | `book_skip_score_lt65_ask_ge70` | 16 | 62.50% | -260.0c |
| current | `book_skip_score_lt70_ask_ge70` | 16 | 62.50% | -260.0c |
| current | `score_ask_le65` | 16 | 6.25% | -181.0c |
| current | `score_ask_le70` | 16 | 62.50% | -350.0c |
| current | `score_highask_needs_score70` | 16 | 68.75% | -244.0c |
| current | `score_highask_needs_score75` | 16 | 75.00% | -318.0c |
| current | `score_min60_locked_equiv` | 16 | 68.75% | -220.0c |
| current | `score_skip_score60_65_ask60_80` | 16 | 68.75% | -252.0c |
| current | `score_skip_score625_65_ask60_80` | 16 | 62.50% | -263.0c |
| current | `score_skip_score_lt65_ask_ge70` | 16 | 68.75% | -250.0c |
| current | `score_skip_score_lt70_ask_ge70` | 16 | 68.75% | -244.0c |
| v21 | `book_ask_le65` | 11 | 9.09% | -214.0c |
| v21 | `book_ask_le70` | 11 | 54.55% | -320.0c |
| v21 | `book_highask_needs_score70` | 11 | 63.64% | -333.0c |
| v21 | `book_highask_needs_score75` | 11 | 63.64% | -339.0c |
| v21 | `book_margin_locked_equiv` | 11 | 63.64% | -332.0c |
| v21 | `book_skip_score60_65_ask60_80` | 11 | 54.55% | -424.0c |
| v21 | `book_skip_score625_65_ask60_80` | 11 | 54.55% | -384.0c |
| v21 | `book_skip_score_lt65_ask_ge70` | 11 | 63.64% | -332.0c |
| v21 | `book_skip_score_lt70_ask_ge70` | 11 | 63.64% | -333.0c |
| v21 | `score_ask_le65` | 11 | 0.00% | -187.0c |
| v21 | `score_ask_le70` | 11 | 27.27% | -237.0c |
| v21 | `score_highask_needs_score70` | 11 | 63.64% | -249.0c |
| v21 | `score_highask_needs_score75` | 11 | 63.64% | -187.0c |
| v21 | `score_min60_locked_equiv` | 11 | 63.64% | -228.0c |
| v21 | `score_skip_score60_65_ask60_80` | 11 | 45.45% | -346.0c |
| v21 | `score_skip_score625_65_ask60_80` | 11 | 63.64% | -297.0c |
| v21 | `score_skip_score_lt65_ask_ge70` | 11 | 63.64% | -234.0c |
| v21 | `score_skip_score_lt70_ask_ge70` | 11 | 63.64% | -249.0c |

## Worst Supported Slices

Only slices with at least `12` selected markets are shown.

| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask |
|---|---|---|---:|---:|---:|---:|---:|
| v21 | `book_skip_score60_65_ask60_80` | ask=(70.0, 80.0] | 87 | 58/29 | -859.0c | -9.9c | 74.0c |
| v21 | `book_skip_score60_65_ask60_80` | score=(0.7, 0.8] | 83 | 56/27 | -767.0c | -9.2c | 74.0c |
| v21 | `book_skip_score625_65_ask60_80` | ask=(70.0, 80.0] | 59 | 38/21 | -690.0c | -11.7c | 73.0c |
| v21 | `book_highask_needs_score70` | ask=(70.0, 80.0] | 52 | 33/19 | -654.0c | -12.6c | 73.0c |
| v21 | `book_skip_score_lt70_ask_ge70` | ask=(70.0, 80.0] | 52 | 33/19 | -654.0c | -12.6c | 73.0c |
| v21 | `score_skip_score60_65_ask60_80` | split=train | 129 | 93/36 | -640.0c | -5.0c | 74.0c |
| v21 | `book_margin_locked_equiv` | ask=(70.0, 80.0] | 44 | 27/17 | -632.0c | -14.4c | 72.5c |
| v21 | `book_skip_score_lt65_ask_ge70` | ask=(70.0, 80.0] | 44 | 27/17 | -632.0c | -14.4c | 72.5c |
| current | `book_skip_score_lt70_ask_ge70` | score=(0.625, 0.65] | 60 | 34/26 | -592.0c | -9.9c | 64.0c |
| current | `book_highask_needs_score70` | score=(0.625, 0.65] | 60 | 34/26 | -592.0c | -9.9c | 64.0c |
| current | `book_margin_locked_equiv` | score=(0.625, 0.65] | 60 | 34/26 | -592.0c | -9.9c | 64.0c |
| current | `book_skip_score_lt65_ask_ge70` | score=(0.625, 0.65] | 60 | 34/26 | -592.0c | -9.9c | 64.0c |
| v21 | `book_skip_score625_65_ask60_80` | score=(0.7, 0.8] | 56 | 37/19 | -571.0c | -10.2c | 74.0c |
| v21 | `score_skip_score60_65_ask60_80` | ask=(70.0, 80.0] | 110 | 79/31 | -569.0c | -5.2c | 75.0c |
| current | `book_ask_le70` | score=(0.625, 0.65] | 64 | 37/27 | -559.0c | -8.7c | 64.0c |
| current | `book_highask_needs_score75` | score=(0.625, 0.65] | 61 | 35/26 | -558.0c | -9.1c | 64.0c |
| current | `book_ask_le70` | edge=(-5.0, -3.0] | 46 | 25/21 | -539.0c | -11.7c | 63.5c |
| v21 | `book_highask_needs_score70` | score=(0.7, 0.8] | 49 | 32/17 | -535.0c | -10.9c | 74.0c |

## Read

- No cost/score veto clears the full robustness gate.
