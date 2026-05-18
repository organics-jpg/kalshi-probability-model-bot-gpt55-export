# v28 Boundary-Entropy FV Diagnostic

Research-only; no live bot changes or orders.

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Forward denominator: `152`
- Rows: `112`

## Current Read

- Boundary-entropy variants are diagnostic only and must be frozen before forward promotion.
- Best FV variant is entropy_book_s100 with Brier/logloss deltas -0.011616674934007004/-0.02398221407513712 over 112 settled rows.
- No boundary-entropy bridge currently lands in the 75-90% coverage band.

## FV Ranking

| variant | settled | adjusted | avg heat | Brier d | logloss d | net c |
|---|---:|---:|---:|---:|---:|---:|
| `entropy_book_s100` | 112 | 111 | 0.433043 | -0.011617 | -0.023982 | -626.000000 |
| `entropy_book_no_mid_s75` | 112 | 111 | 0.466587 | -0.009905 | -0.020341 | -626.000000 |
| `entropy_book_s75` | 112 | 111 | 0.433043 | -0.009295 | -0.019081 | -626.000000 |
| `entropy_book_s50` | 112 | 111 | 0.433043 | -0.006585 | -0.013480 | -626.000000 |
| `entropy50_no_mid_s75` | 112 | 111 | 0.466587 | -0.006382 | -0.013239 | -626.000000 |
| `entropy50_s100` | 112 | 112 | 0.433043 | -0.006380 | -0.013183 | -626.000000 |
| `entropy50_s75` | 112 | 111 | 0.433043 | -0.005193 | -0.010784 | -626.000000 |
| `entropy50_s50` | 112 | 111 | 0.433043 | -0.003734 | -0.007800 | -626.000000 |
| `raw_probability` | 112 | 0 | 0.433043 | 0.000000 | 0.000000 | -626.000000 |

## Target-Coverage Entry Bridges

| variant | floor | entries | settled | W/L | coverage | net c | skipped net c |
|---|---:|---:|---:|---:|---:|---:|---:|
