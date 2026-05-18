# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:18:53.295907+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `candle_brownian`
- Best model by log loss: `candle_brownian`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.6075140837015135 | 1.8373290148880876 | 9 | -91.0 | 171.0 |
| `v28` | 18 | 1 | 0.8992581126449097 | 2.9621468022464468 | 9 | -783.0 | -348.0 |
| `candle_brownian` | 18 | 1 | 0.4507501759638239 | 1.1128511068920854 | 9 | 774.0 | 344.0 |
| `tick_brownian` | 18 | 1 | 0.4507501759638239 | 1.1128511068920854 | 9 | 774.0 | 344.0 |
| `market_side_ask` | 18 | 1 | 0.74825 | 2.003166842449694 | 9 | 774.0 | 344.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
