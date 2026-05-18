# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:03.989373+00:00`
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
| `candidate` | 18 | 1 | 0.43645322199612785 | 1.3202088574675424 | 10 | -466.0 | -118.0 |
| `v28` | 18 | 1 | 0.3719695441482491 | 0.9413343712922351 | 9 | -522.0 | -232.0 |
| `candle_brownian` | 18 | 1 | 0.2779885353934351 | 0.7491804932395173 | 9 | 504.0 | 224.0 |
| `tick_brownian` | 18 | 1 | 0.2779885353934351 | 0.7491804932395173 | 9 | 504.0 | 224.0 |
| `market_side_ask` | 18 | 1 | 0.325 | 0.8442405598872766 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
