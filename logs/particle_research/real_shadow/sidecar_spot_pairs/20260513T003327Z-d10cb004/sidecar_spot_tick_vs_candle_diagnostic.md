# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T02:01:59.488551+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `-0.042054012806668595`
- Tick Brownian delta log loss vs candle: `-0.08416621661259849`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.250723204553686 | 0.6729243661926403 | 9 | -232.0 | -2.0 |
| `v28` | 18 | 1 | 0.33681488885986177 | 0.8683522459940233 | 9 | -414.0 | -184.0 |
| `candle_brownian` | 18 | 1 | 0.2664654570639946 | 0.7260897212763875 | 9 | -414.0 | -184.0 |
| `tick_brownian` | 18 | 1 | 0.224411444257326 | 0.641923504663789 | 9 | -414.0 | -184.0 |
| `market_side_ask` | 18 | 1 | 0.20704999999999996 | 0.6070115700897187 | 9 | 405.0 | 180.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
