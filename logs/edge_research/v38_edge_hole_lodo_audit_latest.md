# v38 Edge-Hole Leave-One-Day-Out Audit

Generated UTC: `2026-05-05T01:50:44.932566+00:00`

## Scope

- Uses saved retrospective candidate trades.
- For each UTC holdout day, selects the candidate with the best worst-day fee+1c-entry P&L on the other days.
- This checks whether the edge-hole range is a one-day overfit.

## LODO Selection

| holdout day | selected candidate | train min day | train total | selected holdout | primary holdout |
|---|---|---:|---:|---:|---:|
| `2026-05-01` | `block_market_first_edge_8_20` | $1.72 | $6.12 | $0.38 | $0.38 |
| `2026-05-02` | `block_market_first_edge_8_20` | $0.38 | $4.46 | $2.04 | $2.04 |
| `2026-05-03` | `block_market_first_edge_8_20` | $0.38 | $4.78 | $1.72 | $1.72 |
| `2026-05-04` | `block_market_first_edge_8_20` | $0.38 | $4.14 | $2.36 | $2.36 |

## Read

- LODO-selected candidate positive on holdout day: 4/4.
- Fixed primary `block_market_first_edge_8_20` positive on holdout day: 4/4.
