# v38 Edge-Hole 80% Candidate Audit

Generated UTC: `2026-05-05T02:37:12.700658+00:00`

## Scope

- Research-only audit of saved v38 edge-hole trades.
- Enforces at least 80% coverage in train, validation, and holdout.
- Uses fees plus a 1c entry haircut as the robustness metric.

## Best 80% Candidate

- Candidate: `block_market_first_edge_10_20`
- Min split coverage: 84.85%
- All fee+1c entry P&L: $5.95
- Min split fee+1c entry P&L: $1.57
- All gross P&L: $21.48
- Trades: 286

## Reference Noncompliant Row

- `block_market_first_edge_8_20` min split coverage: 78.79%
- `block_market_first_edge_8_20` all fee+1c entry P&L: $6.50

## Compliant Rows

| candidate | min cov | min 1c | all 1c | all fee | gross | trades |
|---|---:|---:|---:|---:|---:|---:|
| `block_market_first_edge_10_20` | 84.85% | $1.57 | $5.95 | $11.67 | $21.48 | 286 |
| `block_market_first_edge_10_18` | 84.85% | $1.31 | $5.02 | $10.76 | $20.62 | 287 |
| `block_market_first_edge_10_25` | 81.82% | $0.69 | $5.47 | $11.09 | $20.54 | 281 |
| `block_market_first_edge_10_22` | 81.82% | $0.69 | $5.05 | $10.71 | $20.32 | 283 |

## Day Stability

| candidate | positive days | worst 1c day | total 1c |
|---|---:|---:|---:|
| `block_market_first_edge_8_20` | 4/4 | $0.38 | $6.50 |
| `block_market_first_edge_10_20` | 3/4 | $-0.69 | $5.95 |
| `block_market_first_edge_10_25` | 3/4 | $-0.69 | $5.47 |
| `block_market_first_edge_10_22` | 3/4 | $-0.69 | $5.05 |
| `block_market_first_edge_10_18` | 3/4 | $-0.69 | $5.02 |

## LODO Among 80% Candidates

| holdout day | selected candidate | train min day | train total | holdout 1c |
|---|---|---:|---:|---:|
| `2026-05-01` | `block_market_first_edge_10_20` | $1.62 | $6.64 | $-0.69 |
| `2026-05-02` | `block_market_first_edge_10_20` | $-0.69 | $3.29 | $2.66 |
| `2026-05-03` | `block_market_first_edge_10_18` | $-0.69 | $4.33 | $0.69 |
| `2026-05-04` | `block_market_first_edge_10_25` | $-0.69 | $3.99 | $1.48 |

## Read

- Best compliant replacement for `block_market_first_edge_8_20` is `block_market_first_edge_10_20`.
- LODO-selected 80% candidate is positive on held-out day 3/4.
- This keeps the edge-hole physics family, but shifts the live-shadow candidate to obey the 80% coverage constraint.
