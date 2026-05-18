# v28 Weak-Reversal Residual FV Shrink

Research-only; no live bot changes and no orders.

- Weak policy: `p60_recross75_near25_delay240_abstain`
- Residual zone: `side=no and raw_edge_prob in [0.05, 0.08)`

## Interpretation

- Residual zone raw rows: 12; raw avg p 0.7174160833333333 vs win rate 0.5833333333333334.
- Best FV variant is minus_08 with all Brier/logloss deltas -0.0015845515789473796/-0.0029887895193967395.
- In-zone adjusted avg p is 0.6374160833333334 with Brier/logloss deltas -0.015053239999999996/-0.028393500434269248.
- This is calibration evidence only; entry profitability still requires frozen forward validation.

## Ranked FV Variants

| variant | all rows | all Brier d | all logloss d | zone rows | zone avg p | zone win rate | zone Brier d | zone logloss d |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| minus_08 | 114 | -0.001585 | -0.002989 | 12 | 0.637416 | 0.583333 | -0.015053 | -0.028394 |
| to_book | 114 | -0.001287 | -0.002546 | 12 | 0.650833 | 0.583333 | -0.012228 | -0.024186 |
| minus_05 | 114 | -0.001148 | -0.002250 | 12 | 0.667416 | 0.583333 | -0.010908 | -0.021370 |
| book_plus_02 | 114 | -0.000961 | -0.001978 | 12 | 0.670833 | 0.583333 | -0.009128 | -0.018792 |
| book_plus_03 | 114 | -0.000766 | -0.001620 | 12 | 0.680833 | 0.583333 | -0.007278 | -0.015391 |
| minus_03 | 114 | -0.000752 | -0.001513 | 12 | 0.687416 | 0.583333 | -0.007145 | -0.014373 |
| half_to_50 | 114 | -0.000655 | -0.000564 | 12 | 0.608708 | 0.583333 | -0.006223 | -0.005354 |
| raw | 114 | 0.000000 | 0.000000 | 12 | 0.717416 | 0.583333 | 0.000000 | 0.000000 |
