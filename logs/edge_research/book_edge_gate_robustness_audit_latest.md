# Book/Score Fee-Aware Edge Gate Robustness Audit

Generated UTC: `20260504_110907Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Tests whether fee-aware fair-edge gates improve the book/score probability priors without losing high coverage.
- Strict pass requires current+v21 coverage, positive validation/holdout, positive all splits, and block stability.

## Combined Read

| candidate | combined net | current/v21 net | current/v21 acc | current/v21 cov | coverage | all splits | OOS | min block+ | worst block | robust |
|---|---:|---:|---:|---:|---|---|---|---:|---:|---|
| `score_min60_edge_ge_m5` | 2240.0c | 1362.0c/878.0c | 75.93%/76.32% | 96.09%/85.97% | True | True | True | 54.55% | -248.0c | False |
| `score_min60_edge_ge_m3` | 1735.0c | 1118.0c/617.0c | 75.89%/76.05% | 91.86%/75.57% | False | False | False | 27.27% | -377.0c | False |
| `score_min60_locked_equiv` | 1708.0c | 1174.0c/534.0c | 75.33%/73.85% | 99.02%/98.64% | True | False | True | 63.64% | -228.0c | False |
| `book_margin_locked_equiv` | 1376.0c | 951.0c/425.0c | 70.82%/71.23% | 99.35%/99.10% | True | False | True | 60.00% | -332.0c | False |
| `book_margin_edge_ge_m5` | 1376.0c | 951.0c/425.0c | 70.82%/71.23% | 99.35%/99.10% | True | False | True | 60.00% | -332.0c | False |
| `book_margin_edge_ge_m3` | 1340.0c | 944.0c/396.0c | 70.82%/71.23% | 99.35%/99.10% | True | False | True | 60.00% | -332.0c | False |
| `book_p625_edge_ge_m3` | 1147.0c | 1027.0c/120.0c | 73.11%/72.15% | 99.35%/99.10% | True | False | True | 54.55% | -496.0c | False |
| `book_p65_edge_ge_m3` | 32.0c | 124.0c/-92.0c | 72.94%/74.31% | 98.70%/98.64% | True | False | False | 54.55% | -435.0c | False |
| `book_margin_edge_ge_0` | 0.0c | 0.0c/0.0c | NA/NA | 0.00%/0.00% | False | False | False | 0.00% | 0.0c | False |
| `book_margin_edge_ge_2` | 0.0c | 0.0c/0.0c | NA/NA | 0.00%/0.00% | False | False | False | 0.00% | 0.0c | False |
| `book_margin_edge_ge_5` | 0.0c | 0.0c/0.0c | NA/NA | 0.00%/0.00% | False | False | False | 0.00% | 0.0c | False |
| `book_p625_edge_ge_0` | 0.0c | 0.0c/0.0c | NA/NA | 0.00%/0.00% | False | False | False | 0.00% | 0.0c | False |
| `book_p65_edge_ge_0` | 0.0c | 0.0c/0.0c | NA/NA | 0.00%/0.00% | False | False | False | 0.00% | 0.0c | False |
| `score_min60_edge_ge_0` | 0.0c | 0.0c/0.0c | NA/NA | 0.00%/0.00% | False | False | False | 0.00% | 0.0c | False |
| `score_min60_edge_ge_2` | 0.0c | 0.0c/0.0c | NA/NA | 0.00%/0.00% | False | False | False | 0.00% | 0.0c | False |
| `score_min60_edge_ge_5` | 0.0c | 0.0c/0.0c | NA/NA | 0.00%/0.00% | False | False | False | 0.00% | 0.0c | False |

## Split Summary

| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | median edge | coverage | all splits | OOS |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---|
| current | `book_margin_edge_ge_0` | 0.0c/NA | NA/0.00% | 0.0c | 0.0c | 0.0c | NA | False | False | False |
| v21 | `book_margin_edge_ge_0` | 0.0c/NA | NA/0.00% | 0.0c | 0.0c | 0.0c | NA | False | False | False |
| current | `book_margin_edge_ge_2` | 0.0c/NA | NA/0.00% | 0.0c | 0.0c | 0.0c | NA | False | False | False |
| v21 | `book_margin_edge_ge_2` | 0.0c/NA | NA/0.00% | 0.0c | 0.0c | 0.0c | NA | False | False | False |
| current | `book_margin_edge_ge_5` | 0.0c/NA | NA/0.00% | 0.0c | 0.0c | 0.0c | NA | False | False | False |
| v21 | `book_margin_edge_ge_5` | 0.0c/NA | NA/0.00% | 0.0c | 0.0c | 0.0c | NA | False | False | False |
| current | `book_margin_edge_ge_m3` | 944.0c/4.57% | 70.82%/99.35% | 596.0c | 117.0c | 231.0c | -2.5c | True | True | True |
| v21 | `book_margin_edge_ge_m3` | 396.0c/2.60% | 71.23%/99.10% | -109.0c | 212.0c | 293.0c | -2.5c | True | False | True |
| current | `book_margin_edge_ge_m5` | 951.0c/4.61% | 70.82%/99.35% | 603.0c | 117.0c | 231.0c | -2.5c | True | True | True |
| v21 | `book_margin_edge_ge_m5` | 425.0c/2.80% | 71.23%/99.10% | -80.0c | 212.0c | 293.0c | -2.5c | True | False | True |
| current | `book_margin_locked_equiv` | 951.0c/4.61% | 70.82%/99.35% | 603.0c | 117.0c | 231.0c | -2.5c | True | True | True |
| v21 | `book_margin_locked_equiv` | 425.0c/2.80% | 71.23%/99.10% | -80.0c | 212.0c | 293.0c | -2.5c | True | False | True |
| current | `book_p625_edge_ge_0` | 0.0c/NA | NA/0.00% | 0.0c | 0.0c | 0.0c | NA | False | False | False |
| v21 | `book_p625_edge_ge_0` | 0.0c/NA | NA/0.00% | 0.0c | 0.0c | 0.0c | NA | False | False | False |
| current | `book_p625_edge_ge_m3` | 1027.0c/4.83% | 73.11%/99.35% | 752.0c | 273.0c | 2.0c | -2.5c | True | True | True |
| v21 | `book_p625_edge_ge_m3` | 120.0c/0.77% | 72.15%/99.10% | -134.0c | 1.0c | 253.0c | -2.5c | True | False | True |
| current | `book_p65_edge_ge_0` | 0.0c/NA | NA/0.00% | 0.0c | 0.0c | 0.0c | NA | False | False | False |
| v21 | `book_p65_edge_ge_0` | 0.0c/NA | NA/0.00% | 0.0c | 0.0c | 0.0c | NA | False | False | False |
| current | `book_p65_edge_ge_m3` | 124.0c/0.56% | 72.94%/98.70% | -28.0c | 266.0c | -114.0c | -2.5c | True | False | False |
| v21 | `book_p65_edge_ge_m3` | -92.0c/-0.56% | 74.31%/98.64% | -534.0c | 279.0c | 163.0c | -2.5c | True | False | True |
| current | `score_min60_edge_ge_0` | 0.0c/NA | NA/0.00% | 0.0c | 0.0c | 0.0c | NA | False | False | False |
| v21 | `score_min60_edge_ge_0` | 0.0c/NA | NA/0.00% | 0.0c | 0.0c | 0.0c | NA | False | False | False |
| current | `score_min60_edge_ge_2` | 0.0c/NA | NA/0.00% | 0.0c | 0.0c | 0.0c | NA | False | False | False |
| v21 | `score_min60_edge_ge_2` | 0.0c/NA | NA/0.00% | 0.0c | 0.0c | 0.0c | NA | False | False | False |
| current | `score_min60_edge_ge_5` | 0.0c/NA | NA/0.00% | 0.0c | 0.0c | 0.0c | NA | False | False | False |
| v21 | `score_min60_edge_ge_5` | 0.0c/NA | NA/0.00% | 0.0c | 0.0c | 0.0c | NA | False | False | False |
| current | `score_min60_edge_ge_m3` | 1118.0c/5.51% | 75.89%/91.86% | 898.0c | -42.0c | 262.0c | -2.5c | True | False | False |
| v21 | `score_min60_edge_ge_m3` | 617.0c/5.11% | 76.05%/75.57% | -34.0c | 383.0c | 268.0c | -2.5c | False | False | True |
| current | `score_min60_edge_ge_m5` | 1362.0c/6.47% | 75.93%/96.09% | 973.0c | 200.0c | 189.0c | -2.6c | True | True | True |
| v21 | `score_min60_edge_ge_m5` | 878.0c/6.45% | 76.32%/85.97% | 190.0c | 393.0c | 295.0c | -2.5c | True | True | True |
| current | `score_min60_locked_equiv` | 1174.0c/5.40% | 75.33%/99.02% | 784.0c | 287.0c | 103.0c | -4.0c | True | True | True |
| v21 | `score_min60_locked_equiv` | 534.0c/3.43% | 73.85%/98.64% | -19.0c | 398.0c | 155.0c | -3.0c | True | False | True |

## Block Summary

| dataset | candidate | blocks | positive blocks | positive+coverage blocks | worst block |
|---|---|---:|---:|---:|---:|
| current | `book_margin_edge_ge_0` | 15 | 0.00% | 0.00% | 0.0c |
| current | `book_margin_edge_ge_2` | 15 | 0.00% | 0.00% | 0.0c |
| current | `book_margin_edge_ge_5` | 15 | 0.00% | 0.00% | 0.0c |
| current | `book_margin_edge_ge_m3` | 15 | 60.00% | 60.00% | -260.0c |
| current | `book_margin_edge_ge_m5` | 15 | 60.00% | 60.00% | -260.0c |
| current | `book_margin_locked_equiv` | 15 | 60.00% | 60.00% | -260.0c |
| current | `book_p625_edge_ge_0` | 15 | 0.00% | 0.00% | 0.0c |
| current | `book_p625_edge_ge_m3` | 15 | 66.67% | 66.67% | -463.0c |
| current | `book_p65_edge_ge_0` | 15 | 0.00% | 0.00% | 0.0c |
| current | `book_p65_edge_ge_m3` | 15 | 60.00% | 60.00% | -435.0c |
| current | `score_min60_edge_ge_0` | 15 | 0.00% | 0.00% | 0.0c |
| current | `score_min60_edge_ge_2` | 15 | 0.00% | 0.00% | 0.0c |
| current | `score_min60_edge_ge_5` | 15 | 0.00% | 0.00% | 0.0c |
| current | `score_min60_edge_ge_m3` | 15 | 53.33% | 53.33% | -377.0c |
| current | `score_min60_edge_ge_m5` | 15 | 73.33% | 73.33% | -221.0c |
| current | `score_min60_locked_equiv` | 15 | 66.67% | 66.67% | -220.0c |
| v21 | `book_margin_edge_ge_0` | 11 | 0.00% | 0.00% | 0.0c |
| v21 | `book_margin_edge_ge_2` | 11 | 0.00% | 0.00% | 0.0c |
| v21 | `book_margin_edge_ge_5` | 11 | 0.00% | 0.00% | 0.0c |
| v21 | `book_margin_edge_ge_m3` | 11 | 63.64% | 63.64% | -332.0c |
| v21 | `book_margin_edge_ge_m5` | 11 | 63.64% | 63.64% | -332.0c |
| v21 | `book_margin_locked_equiv` | 11 | 63.64% | 63.64% | -332.0c |
| v21 | `book_p625_edge_ge_0` | 11 | 0.00% | 0.00% | 0.0c |
| v21 | `book_p625_edge_ge_m3` | 11 | 54.55% | 54.55% | -496.0c |
| v21 | `book_p65_edge_ge_0` | 11 | 0.00% | 0.00% | 0.0c |
| v21 | `book_p65_edge_ge_m3` | 11 | 54.55% | 54.55% | -424.0c |
| v21 | `score_min60_edge_ge_0` | 11 | 0.00% | 0.00% | 0.0c |
| v21 | `score_min60_edge_ge_2` | 11 | 0.00% | 0.00% | 0.0c |
| v21 | `score_min60_edge_ge_5` | 11 | 0.00% | 0.00% | 0.0c |
| v21 | `score_min60_edge_ge_m3` | 11 | 54.55% | 27.27% | -282.0c |
| v21 | `score_min60_edge_ge_m5` | 11 | 72.73% | 54.55% | -248.0c |
| v21 | `score_min60_locked_equiv` | 11 | 63.64% | 63.64% | -228.0c |

## Worst Supported Slices

Only slices with at least `12` selected markets are shown.

| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask | median edge |
|---|---|---|---:|---:|---:|---:|---:|---:|
| v21 | `book_p65_edge_ge_m3` | ask=(70.0, 80.0] | 87 | 58/29 | -859.0c | -9.9c | 74.0c | -2.5c |
| v21 | `book_p65_edge_ge_m3` | score=(0.7, 0.8] | 83 | 56/27 | -767.0c | -9.2c | 74.0c | -2.5c |
| current | `book_p625_edge_ge_m3` | score=(0.625, 0.65] | 94 | 56/38 | -653.0c | -6.9c | 64.0c | -2.5c |
| v21 | `book_p625_edge_ge_m3` | ask=(70.0, 80.0] | 61 | 40/21 | -643.0c | -10.5c | 73.0c | -2.5c |
| v21 | `book_margin_edge_ge_m3` | ask=(70.0, 80.0] | 44 | 27/17 | -632.0c | -14.4c | 72.5c | -2.5c |
| v21 | `book_margin_edge_ge_m5` | ask=(70.0, 80.0] | 44 | 27/17 | -632.0c | -14.4c | 72.5c | -2.5c |
| v21 | `book_margin_locked_equiv` | ask=(70.0, 80.0] | 44 | 27/17 | -632.0c | -14.4c | 72.5c | -2.5c |
| current | `book_margin_locked_equiv` | score=(0.625, 0.65] | 59 | 33/26 | -625.0c | -10.6c | 64.0c | -2.5c |
| current | `book_margin_edge_ge_m5` | score=(0.625, 0.65] | 59 | 33/26 | -625.0c | -10.6c | 64.0c | -2.5c |
| current | `book_margin_edge_ge_m3` | score=(0.625, 0.65] | 59 | 33/26 | -625.0c | -10.6c | 64.0c | -2.5c |
| v21 | `book_p625_edge_ge_m3` | score=(0.7, 0.8] | 57 | 38/19 | -551.0c | -9.7c | 74.0c | -2.5c |
| v21 | `book_p65_edge_ge_m3` | split=train | 130 | 91/39 | -534.0c | -4.1c | 70.0c | -2.5c |
| v21 | `book_p65_edge_ge_m3` | time=(-1.001, 600.0] | 60 | 41/19 | -534.0c | -8.9c | 74.0c | -2.5c |
| v21 | `book_margin_edge_ge_m5` | score=(0.7, 0.8] | 41 | 26/15 | -513.0c | -12.5c | 73.0c | -2.5c |
| v21 | `book_margin_locked_equiv` | score=(0.7, 0.8] | 41 | 26/15 | -513.0c | -12.5c | 73.0c | -2.5c |
| v21 | `book_margin_edge_ge_m3` | score=(0.7, 0.8] | 41 | 26/15 | -513.0c | -12.5c | 73.0c | -2.5c |
| v21 | `score_min60_locked_equiv` | ask=(70.0, 80.0] | 59 | 40/19 | -486.0c | -8.2c | 73.0c | -4.6c |
| current | `book_margin_locked_equiv` | time=(840.0, 10000.0] | 81 | 50/31 | -482.0c | -6.0c | 64.0c | -2.5c |

## Read

- No fee-aware edge-gated row clears the full robustness gate.
