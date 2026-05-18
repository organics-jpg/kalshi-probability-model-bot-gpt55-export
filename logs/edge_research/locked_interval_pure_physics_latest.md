# Locked Pure-Physics Interval Monitor

Generated UTC: `20260502_184704Z`

## Scope

- Research-only monitor; no orders are submitted and no bot files are modified.
- Candidate definitions are frozen in `logs/edge_research/locked_interval_pure_physics.json`.
- Side choice uses pure physics features; book probability is not used as a chooser or model feature.
- Ask is used only as an execution cap and degeneracy diagnostic.
- Fresh rows are markets with close time after the lock close time.
- Lock close time: `2026-05-02T15:00:00+00:00`

## Candidate Results

| candidate | target | Wilson | all acc | all cov | all Wilson low | all median ask | fresh markets | fresh acc | fresh cov | fresh median ask | fresh ask=100 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `pure_brownian_rv30_adverse15_high_price_20260502_1522` | True | False | 98.61% | 90.57% | 95.08% | 98.0 | 10/12 | 100.00% | 83.33% | 97.0 | 1 |
| `pure_physics_mean_rv15_rv30_high_price_20260502_1522` | True | False | 98.60% | 89.94% | 95.04% | 98.0 | 10/12 | 100.00% | 83.33% | 96.5 | 1 |
| `pure_brownian_rv15_spread4_best_high_coverage_20260502_1522` | False | False | 94.59% | 93.08% | 89.70% | 95.0 | 10/12 | 100.00% | 83.33% | 88.5 | 0 |
| `pure_brownian_rv30_economical_adverse15_20260502_1522` | False | False | 86.23% | 86.79% | 79.50% | 85.5 | 10/12 | 90.00% | 83.33% | 84.0 | 0 |

## Read

- Fresh resolved intervals available for locked pure-physics candidates: 12
- Fresh sample is far below the sample-size requirement; this is monitoring evidence only.
- The strongest physics-only passes still carry high-price degeneracy warnings.
- No locked pure-physics candidate has a Wilson-robust 95% accuracy proof across splits.
