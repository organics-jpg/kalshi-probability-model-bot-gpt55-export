# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-18T18:27:27.140926+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `14` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `-0.017827327801404336`
- Tick Brownian delta log loss vs candle: `-0.03572729654342632`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 14 | 1 | 0.5058071798248511 | 1.7446031645983413 | 7 | -357.0 | -153.0 |
| `v28` | 14 | 1 | 0.3427734629680588 | 0.880606514999022 | 7 | -357.0 | -153.0 |
| `candle_brownian` | 14 | 1 | 0.28141745164233367 | 0.7560612880553234 | 7 | -357.0 | -153.0 |
| `tick_brownian` | 14 | 1 | 0.26359012384092934 | 0.720333991511897 | 7 | -357.0 | -153.0 |
| `market_side_ask` | 14 | 1 | 0.25505 | 0.703248534218705 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
