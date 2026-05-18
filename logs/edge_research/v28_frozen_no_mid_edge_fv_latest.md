# v28 Frozen NO Mid-Edge FV

Research-only; no live bot changes and no orders.

- Variant: `no_mid_to_book`
- Freeze timestamp UTC: `2026-05-06T10:33:21.044716+00:00`
- Ready for consideration: `False`
- Blockers: `brier_not_better, logloss_not_better`
- Brier/logloss delta: `0.002992138690551288/0.007193315774060016`

## Interpretation

- Frozen forward denominator is 107; scored rows 78.
- Raw Brier/logloss 0.21644742203030767/0.6144511667103113; variant 0.21943956072085896/0.6216444824843713.
- Promotion blocked by: brier_not_better, logloss_not_better.
- This is a frozen calibration overlay, not live order logic.

## Metrics

| slice | rows | avg p | win rate | Brier | logloss |
|---|---:|---:|---:|---:|---:|
| raw | 78 | 0.646068 | 0.589744 | 0.216447 | 0.614451 |
| variant | 78 | 0.637760 | 0.589744 | 0.219440 | 0.621644 |
