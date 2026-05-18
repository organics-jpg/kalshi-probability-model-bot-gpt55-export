# v38 Edge-Hole Veto Candidate

Generated UTC: `2026-05-05T00:47:41.759669+00:00`

## Scope

- Tests whether the v38 10-20c model-edge band is an overconfidence hole.
- `skip_rows` variants skip only the bad row and may enter later; `block_market_first` variants skip the whole market if the first signal is in the edge-hole.
- Uses v38 `p_side>=0.65`, `edge>=0`, `0-600s` to close, and `prob52` exit.
- Research-only. No live bot logic/process/order path touched.

## Rows

| candidate | min cov | min fee net | all fee net | min 1c entry | all 1c entry | all gross | trades | block10 + | worst block10 | block20 + | worst block20 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `block_market_first_edge_8_20` | 78.79% | $2.69 | $11.84 | $1.57 | $6.50 | $20.82 | 267 | 8/10 | $-2.84 | 12/20 | $-2.32 |
| `block_market_first_edge_10_20` | 84.85% | $2.69 | $11.67 | $1.57 | $5.95 | $21.48 | 286 | 7/10 | $-3.37 | 13/20 | $-3.02 |
| `block_market_first_edge_10_18` | 84.85% | $2.45 | $10.76 | $1.31 | $5.02 | $20.62 | 287 | 7/10 | $-3.37 | 12/20 | $-3.02 |
| `block_market_first_edge_10_25` | 81.82% | $1.77 | $11.09 | $0.69 | $5.47 | $20.54 | 281 | 7/10 | $-2.81 | 12/20 | $-2.97 |
| `block_market_first_edge_10_22` | 81.82% | $1.77 | $10.71 | $0.69 | $5.05 | $20.32 | 283 | 7/10 | $-3.37 | 12/20 | $-3.36 |
| `block_market_first_edge_12_20` | 91.41% | $2.53 | $8.95 | $-0.54 | $2.89 | $19.74 | 303 | 7/10 | $-2.68 | 12/20 | $-2.94 |
| `baseline_no_veto` | 92.42% | $1.70 | $7.23 | $-2.06 | $0.95 | $18.64 | 314 | 6/10 | $-4.06 | 11/20 | $-3.51 |
| `skip_rows_edge_10_25` | 92.42% | $-0.29 | $3.21 | $-2.63 | $-3.05 | $13.96 | 313 | 6/10 | $-4.23 | 10/20 | $-3.33 |
| `skip_rows_edge_12_20` | 92.42% | $0.93 | $5.47 | $-2.81 | $-0.79 | $16.80 | 313 | 7/10 | $-4.23 | 10/20 | $-3.47 |
| `skip_rows_edge_10_20` | 92.42% | $0.77 | $3.31 | $-2.97 | $-2.95 | $14.38 | 313 | 6/10 | $-4.23 | 10/20 | $-3.57 |
| `skip_rows_edge_10_18` | 92.42% | $0.77 | $3.29 | $-2.97 | $-2.97 | $14.36 | 313 | 6/10 | $-4.23 | 10/20 | $-3.57 |
| `skip_rows_edge_10_22` | 92.42% | $0.03 | $1.25 | $-3.71 | $-5.01 | $12.18 | 313 | 5/10 | $-4.23 | 10/20 | $-3.57 |
| `skip_rows_edge_8_18` | 90.91% | $-1.33 | $1.41 | $-5.07 | $-4.83 | $12.34 | 312 | 5/10 | $-4.54 | 10/20 | $-3.76 |
| `skip_rows_edge_8_20` | 90.91% | $-1.97 | $0.79 | $-5.69 | $-5.43 | $11.68 | 311 | 4/10 | $-3.95 | 10/20 | $-3.80 |

## Read

- Best row is `block_market_first_edge_8_20` with min 1c-entry split $1.57 and all 1c-entry $6.50.
- Fee-only min split is $2.69; all fee net is $11.84.
- This is the first candidate in this branch to clear fees plus a 1c entry haircut across all splits.
