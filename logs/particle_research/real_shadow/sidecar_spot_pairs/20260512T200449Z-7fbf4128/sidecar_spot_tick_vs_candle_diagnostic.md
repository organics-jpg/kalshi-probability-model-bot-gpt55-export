# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T02:01:16.477478+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `tick_brownian`
- Best model by log loss: `tick_brownian`
- Tick Brownian delta Brier vs candle: `-0.0030914972356765325`
- Tick Brownian delta log loss vs candle: `-0.006446082428145594`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.6074987054085863 | 1.931037939131493 | 9 | 393.0 | -2.0 |
| `v28` | 18 | 1 | 0.5207652063718594 | 1.2788423209451512 | 9 | 711.0 | 316.0 |
| `candle_brownian` | 18 | 1 | 0.3627577716155455 | 0.9220416330838188 | 9 | 711.0 | 316.0 |
| `tick_brownian` | 18 | 1 | 0.359666274379869 | 0.9155955506556732 | 9 | 711.0 | 316.0 |
| `market_side_ask` | 18 | 1 | 0.6320500000000001 | 1.5850428303493844 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
