# Locked Interval Logistic Monitor

Generated UTC: `20260502_184705Z`

## Scope

- Research-only monitor; no orders are submitted and no bot files are modified.
- The logistic model is serialized once and loaded on later runs.
- Fresh rows are markets with close time after the model lock close time.
- Lock close time: `2026-05-02T15:00:00+00:00`
- Candidate: `book_physics; C=0.05; p>=0.95; ask<=100; sec>=0`

## Metrics

| split | acc | coverage | Wilson low | markets | median ask | ask>=95 | ask=100 | median sec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 100.00% | 91.19% | 97.42% | 145/159 | 98.0 | 137 | 17 | 172.7 |
| train | 100.00% | 91.58% | 95.77% | 87/95 | 98.0 | 83 | 12 | 190.3 |
| validation | 100.00% | 93.75% | 88.65% | 30/32 | 98.0 | 28 | 3 | 152.1 |
| holdout | 100.00% | 87.50% | 87.94% | 28/32 | 98.0 | 26 | 2 | 166.0 |
| fresh | 100.00% | 83.33% | 72.25% | 10/12 | 97.0 | 9 | 0 | 166.0 |

## Read

- Fresh sample is far below the sample-size requirement; this is monitoring evidence only.
- All-sample median ask remains high, so degeneracy remains unresolved.
