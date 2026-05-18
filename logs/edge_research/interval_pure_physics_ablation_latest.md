# Pure-Physics Interval Ablation

Generated UTC: `20260502_181630Z`

## Scope

- Research-only probe; no orders are submitted and no bot files are modified.
- Unit of volume is the recurring BTC 15-minute market interval.
- Side choice uses only spot/strike, realized-volatility, drift, and adverse-move features.
- Book probability is not used as a chooser or model feature; ask is only used as an execution price cap.

## Coverage

- Resolved intervals: 156
- Train intervals: 93
- Validation intervals: 31
- Holdout intervals: 32
- Candidate pure-physics policies scanned: 5400
- Policies covering >=80% of intervals on every split: 3600
- Raw target-pass policies: 20
- Nondegenerate target-pass policies: 0
- Wilson-pass policies: 0

## Target-Passing Pure-Physics Policies

| rank | policy | all acc | all cov | val acc | holdout acc | Wilson low | median ask | median sec | target | nondeg |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `pure=brownian_p_rv_30m; brownian_p_rv_30m>=0.95; ask<=100; sec>=0; adverse15<=10` | 98.58% | 90.38% | 96.67% | 100.00% | 94.98% | 98.0 | 169.8 | True | False |
| 2 | `pure=score_physics_mean_rv15_rv30; score_physics_mean_rv15_rv30>=0.95; ask<=100; sec>=0; spread<=4` | 98.57% | 89.74% | 96.55% | 100.00% | 94.94% | 98.0 | 163.4 | True | False |
| 3 | `pure=score_physics_mean_rv15_rv30; score_physics_mean_rv15_rv30>=0.95; ask<=100; sec>=0` | 98.57% | 89.74% | 96.55% | 100.00% | 94.94% | 98.0 | 163.4 | True | False |
| 4 | `pure=score_physics_mean_rv15_rv30; score_physics_mean_rv15_rv30>=0.95; ask<=100; sec>=0; margin_rv15>=0.5` | 98.57% | 89.74% | 96.55% | 100.00% | 94.94% | 98.0 | 163.4 | True | False |
| 5 | `pure=score_physics_mean_rv15_rv30; score_physics_mean_rv15_rv30>=0.95; ask<=100; sec>=0; adverse15<=10` | 98.57% | 89.74% | 96.55% | 100.00% | 94.94% | 98.0 | 163.4 | True | False |
| 6 | `pure=score_physics_mean_rv15_rv30; score_physics_mean_rv15_rv30>=0.95; ask<=100; sec>=0; margin_rv15>=0` | 98.57% | 89.74% | 96.55% | 100.00% | 94.94% | 98.0 | 163.4 | True | False |
| 7 | `pure=brownian_p_rv_15m; brownian_p_rv_15m>=0.95; ask<=100; sec>=0` | 97.86% | 89.74% | 96.43% | 100.00% | 93.89% | 97.5 | 204.9 | True | False |
| 8 | `pure=brownian_p_rv_15m; brownian_p_rv_15m>=0.95; ask<=100; sec>=0; margin_rv15>=0` | 97.86% | 89.74% | 96.43% | 100.00% | 93.89% | 97.5 | 204.9 | True | False |
| 9 | `pure=brownian_p_rv_15m; brownian_p_rv_15m>=0.95; ask<=100; sec>=0; adverse15<=10` | 97.86% | 89.74% | 96.43% | 100.00% | 93.89% | 97.5 | 204.9 | True | False |
| 10 | `pure=brownian_p_rv_15m; brownian_p_rv_15m>=0.95; ask<=100; sec>=0; spread<=4` | 97.86% | 89.74% | 96.43% | 100.00% | 93.89% | 97.5 | 204.9 | True | False |
| 11 | `pure=brownian_p_rv_15m; brownian_p_rv_15m>=0.95; ask<=100; sec>=0; margin_rv15>=0.5` | 97.86% | 89.74% | 96.43% | 100.00% | 93.89% | 97.5 | 204.9 | True | False |
| 12 | `pure=score_physics_min_rv_drift; score_physics_min_rv_drift>=0.95; ask<=100; sec>=0; adverse15<=10` | 98.55% | 88.46% | 96.30% | 100.00% | 94.87% | 99.0 | 134.3 | True | False |
| 13 | `pure=score_physics_min_rv_drift; score_physics_min_rv_drift>=0.95; ask<=100; sec>=0` | 98.55% | 88.46% | 96.30% | 100.00% | 94.87% | 99.0 | 134.3 | True | False |
| 14 | `pure=score_physics_min_rv_drift; score_physics_min_rv_drift>=0.95; ask<=100; sec>=0; margin_rv15>=0.5` | 98.55% | 88.46% | 96.30% | 100.00% | 94.87% | 99.0 | 134.3 | True | False |
| 15 | `pure=score_physics_min_rv_drift; score_physics_min_rv_drift>=0.95; ask<=100; sec>=0; margin_rv15>=0` | 98.55% | 88.46% | 96.30% | 100.00% | 94.87% | 99.0 | 134.3 | True | False |

## Best Nondegenerate 80%-Coverage Policies

| rank | policy | all acc | all cov | val acc | holdout acc | Wilson low | median ask | median sec | target | nondeg |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `pure=score_physics_mean_rv_drift; score_physics_mean_rv_drift>=0.95; ask<=100; sec>=0; adverse15<=10` | 97.89% | 91.03% | 93.33% | 100.00% | 93.97% | 97.0 | 235.1 | False | False |
| 2 | `pure=score_physics_margin_blend; score_physics_margin_blend>=0.95; ask<=100; sec>=0; spread<=4` | 97.89% | 91.03% | 93.33% | 100.00% | 93.97% | 97.0 | 230.6 | False | False |
| 3 | `pure=score_physics_margin_blend; score_physics_margin_blend>=0.95; ask<=100; sec>=0; adverse15<=10` | 97.89% | 91.03% | 93.33% | 100.00% | 93.97% | 97.0 | 230.6 | False | False |
| 4 | `pure=score_physics_margin_blend; score_physics_margin_blend>=0.95; ask<=100; sec>=0; margin_rv15>=0` | 97.89% | 91.03% | 93.33% | 100.00% | 93.97% | 97.0 | 230.6 | False | False |
| 5 | `pure=score_physics_margin_blend; score_physics_margin_blend>=0.95; ask<=100; sec>=0; margin_rv15>=0.5` | 97.89% | 91.03% | 93.33% | 100.00% | 93.97% | 97.0 | 230.6 | False | False |
| 6 | `pure=score_physics_margin_blend; score_physics_margin_blend>=0.95; ask<=100; sec>=0` | 97.89% | 91.03% | 93.33% | 100.00% | 93.97% | 97.0 | 230.6 | False | False |
| 7 | `pure=score_physics_mean_rv_drift; score_physics_mean_rv_drift>=0.95; ask<=100; sec>=0; margin_rv15>=0.5` | 97.18% | 91.03% | 93.33% | 96.30% | 92.98% | 97.0 | 235.8 | False | False |
| 8 | `pure=score_physics_mean_rv_drift; score_physics_mean_rv_drift>=0.95; ask<=100; sec>=0; margin_rv15>=0` | 97.18% | 91.03% | 93.33% | 96.30% | 92.98% | 97.0 | 235.8 | False | False |
| 9 | `pure=score_physics_mean_rv_drift; score_physics_mean_rv_drift>=0.95; ask<=100; sec>=0` | 97.18% | 91.03% | 93.33% | 96.30% | 92.98% | 97.0 | 235.8 | False | False |
| 10 | `pure=score_physics_mean_rv_drift; score_physics_mean_rv_drift>=0.95; ask<=100; sec>=0; spread<=4` | 97.18% | 91.03% | 93.33% | 96.30% | 92.98% | 97.0 | 235.8 | False | False |
| 11 | `pure=score_physics_min_rv_drift; score_physics_min_rv_drift>=0.9; ask<=100; sec>=0; adverse15<=10` | 95.83% | 92.31% | 93.33% | 100.00% | 91.21% | 96.0 | 235.8 | False | False |
| 12 | `pure=score_physics_min_rv_drift; score_physics_min_rv_drift>=0.9; ask<=100; sec>=0; spread<=4` | 95.80% | 91.67% | 93.33% | 96.30% | 91.15% | 96.0 | 237.3 | False | False |
| 13 | `pure=score_physics_min_rv_drift; score_physics_min_rv_drift>=0.9; ask<=100; sec>=0` | 95.14% | 92.31% | 93.33% | 96.30% | 90.31% | 96.0 | 236.6 | False | False |
| 14 | `pure=score_physics_min_rv_drift; score_physics_min_rv_drift>=0.9; ask<=100; sec>=0; margin_rv15>=0` | 95.14% | 92.31% | 93.33% | 96.30% | 90.31% | 96.0 | 236.6 | False | False |
| 15 | `pure=score_physics_min_rv_drift; score_physics_min_rv_drift>=0.9; ask<=100; sec>=0; margin_rv15>=0.5` | 95.14% | 92.31% | 93.33% | 96.30% | 90.31% | 96.0 | 236.6 | False | False |

## Best Overall Pure-Physics Policies

| rank | policy | all acc | all cov | val acc | holdout acc | Wilson low | median ask | median sec | target | nondeg |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `pure=brownian_p_rv_30m; brownian_p_rv_30m>=0.95; ask<=100; sec>=0; adverse15<=10` | 98.58% | 90.38% | 96.67% | 100.00% | 94.98% | 98.0 | 169.8 | True | False |
| 2 | `pure=score_physics_mean_rv15_rv30; score_physics_mean_rv15_rv30>=0.95; ask<=100; sec>=0; spread<=4` | 98.57% | 89.74% | 96.55% | 100.00% | 94.94% | 98.0 | 163.4 | True | False |
| 3 | `pure=score_physics_mean_rv15_rv30; score_physics_mean_rv15_rv30>=0.95; ask<=100; sec>=0` | 98.57% | 89.74% | 96.55% | 100.00% | 94.94% | 98.0 | 163.4 | True | False |
| 4 | `pure=score_physics_mean_rv15_rv30; score_physics_mean_rv15_rv30>=0.95; ask<=100; sec>=0; margin_rv15>=0.5` | 98.57% | 89.74% | 96.55% | 100.00% | 94.94% | 98.0 | 163.4 | True | False |
| 5 | `pure=score_physics_mean_rv15_rv30; score_physics_mean_rv15_rv30>=0.95; ask<=100; sec>=0; adverse15<=10` | 98.57% | 89.74% | 96.55% | 100.00% | 94.94% | 98.0 | 163.4 | True | False |
| 6 | `pure=score_physics_mean_rv15_rv30; score_physics_mean_rv15_rv30>=0.95; ask<=100; sec>=0; margin_rv15>=0` | 98.57% | 89.74% | 96.55% | 100.00% | 94.94% | 98.0 | 163.4 | True | False |
| 7 | `pure=brownian_p_rv_15m; brownian_p_rv_15m>=0.95; ask<=100; sec>=0` | 97.86% | 89.74% | 96.43% | 100.00% | 93.89% | 97.5 | 204.9 | True | False |
| 8 | `pure=brownian_p_rv_15m; brownian_p_rv_15m>=0.95; ask<=100; sec>=0; margin_rv15>=0` | 97.86% | 89.74% | 96.43% | 100.00% | 93.89% | 97.5 | 204.9 | True | False |
| 9 | `pure=brownian_p_rv_15m; brownian_p_rv_15m>=0.95; ask<=100; sec>=0; adverse15<=10` | 97.86% | 89.74% | 96.43% | 100.00% | 93.89% | 97.5 | 204.9 | True | False |
| 10 | `pure=brownian_p_rv_15m; brownian_p_rv_15m>=0.95; ask<=100; sec>=0; spread<=4` | 97.86% | 89.74% | 96.43% | 100.00% | 93.89% | 97.5 | 204.9 | True | False |
| 11 | `pure=brownian_p_rv_15m; brownian_p_rv_15m>=0.95; ask<=100; sec>=0; margin_rv15>=0.5` | 97.86% | 89.74% | 96.43% | 100.00% | 93.89% | 97.5 | 204.9 | True | False |
| 12 | `pure=score_physics_min_rv_drift; score_physics_min_rv_drift>=0.95; ask<=100; sec>=0; adverse15<=10` | 98.55% | 88.46% | 96.30% | 100.00% | 94.87% | 99.0 | 134.3 | True | False |
| 13 | `pure=score_physics_min_rv_drift; score_physics_min_rv_drift>=0.95; ask<=100; sec>=0` | 98.55% | 88.46% | 96.30% | 100.00% | 94.87% | 99.0 | 134.3 | True | False |
| 14 | `pure=score_physics_min_rv_drift; score_physics_min_rv_drift>=0.95; ask<=100; sec>=0; margin_rv15>=0.5` | 98.55% | 88.46% | 96.30% | 100.00% | 94.87% | 99.0 | 134.3 | True | False |
| 15 | `pure=score_physics_min_rv_drift; score_physics_min_rv_drift>=0.95; ask<=100; sec>=0; margin_rv15>=0` | 98.55% | 88.46% | 96.30% | 100.00% | 94.87% | 99.0 | 134.3 | True | False |

## Read

Pure physics can reproduce a raw target pass, but the best pass still depends on high execution prices (median ask 98.0c) or weak sample bounds.
