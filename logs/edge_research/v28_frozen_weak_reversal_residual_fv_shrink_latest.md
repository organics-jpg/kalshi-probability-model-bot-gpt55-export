# v28 Frozen Weak-Reversal Residual FV Shrink

Research-only; no live bot changes and no orders.

- Variant: `half_to_50`
- Freeze timestamp UTC: `2026-05-06T10:29:42.136727+00:00`
- Ready for consideration: `False`
- Blockers: `brier_not_better, logloss_not_better`

## Interpretation

- Frozen forward denominator is 108; scored rows 81.
- Raw Brier/logloss 0.23701222812462963/0.6783386257825808; variant 0.2412286129657377/0.6890751293200246.
- Promotion blocked by: brier_not_better, logloss_not_better.
- This validates calibration only; entry PnL is tracked by the separate residual repair validator.

## Metrics

| slice | rows | avg p | win rate | Brier | logloss |
|---|---:|---:|---:|---:|---:|
| raw_all | 81 | 0.698178 | 0.555556 | 0.237012 | 0.678339 |
| variant_all | 81 | 0.688932 | 0.555556 | 0.241229 | 0.689075 |
| raw_no_side | 41 | 0.696860 | 0.585366 | 0.218891 | 0.650571 |
| variant_no_side | 41 | 0.678594 | 0.585366 | 0.227221 | 0.671782 |
