# Locked Interval Candidate Monitor

Generated UTC: `20260502_184704Z`

## Scope

- Research-only monitor; no orders are submitted and no bot files are modified.
- Candidate definitions are frozen in `logs/edge_research/locked_interval_candidates.json`.
- Fresh rows are markets with close time after the lock close time.
- Lock close time: `2026-05-02T15:00:00+00:00`

## Candidate Results

| candidate | all acc | all cov | all median ask | fresh markets | fresh acc | fresh cov | fresh median ask | fresh ask=100 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `raw_regime_blend_high_price_20260502_1510` | 98.60% | 89.94% | 97.0 | 10/12 | 100.00% | 83.33% | 96.5 | 1 |
| `raw_score_min_book_rv15_existing_lock` | 97.95% | 91.82% | 96.0 | 10/12 | 100.00% | 83.33% | 94.0 | 0 |
| `economical_score_min_book_rv15_20260502_1511` | 88.06% | 84.28% | 88.0 | 10/12 | 90.00% | 83.33% | 85.0 | 0 |
| `staged_score_min_fallback_20260502_1511` | 100.00% | 91.19% | 97.0 | 10/12 | 100.00% | 83.33% | 97.0 | 0 |

## Read

- Fresh resolved intervals available for locked candidates: 12
- Fresh sample is far below the sample-size requirement; this is monitoring evidence only.
- High fresh ask/100c counts remain degeneracy warnings, not promotion evidence.
