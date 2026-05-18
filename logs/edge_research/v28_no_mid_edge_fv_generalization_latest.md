# v28 NO Mid-Edge FV Generalization

Research-only; no live bot changes and no orders.

- Zone: `raw target-coverage rows with side=no and raw_edge_prob in [0.05,0.08)`

## Interpretation

- Raw NO mid-edge rows: 14; W/L 8/6; net -97.0c; avg p 0.6524786428571429 vs win rate 0.5714285714285714.
- Best broader FV variant is no_mid_to_book with all-row Brier/logloss deltas -0.0008393972756696455/-0.0011176499406210239.
- If this broader check disagrees with weak-reversal repair, treat the repair as candidate-specific until forward rows mature.

## Variants

| variant | all rows | all Brier d | all logloss d | NO mid rows | NO mid W/L | NO mid net | NO mid avg p | NO mid win rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_mid_to_book | 112 | -0.000839 | -0.001118 | 14 | 8/6 | -97.000000 | 0.586429 | 0.571429 |
| raw | 112 | 0.000000 | 0.000000 | 14 | 8/6 | -97.000000 | 0.652479 | 0.571429 |
| no_mid_half_to_50 | 112 | 0.000337 | 0.002039 | 14 | 8/6 | -97.000000 | 0.576239 | 0.571429 |
