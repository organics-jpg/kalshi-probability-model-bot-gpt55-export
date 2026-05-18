# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:20:28.204694+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `-0.027510996011392702`
- Tick Brownian delta log loss vs candle: `-0.05512498186671122`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.2084869799623232 | 0.5747954768756119 | 9 | -222.0 | -2.0 |
| `v28` | 18 | 1 | 0.26555634091399943 | 0.7242696797265303 | 9 | -396.0 | -176.0 |
| `candle_brownian` | 18 | 1 | 0.244267809829172 | 0.6816822935469223 | 9 | -396.0 | -176.0 |
| `tick_brownian` | 18 | 1 | 0.2167568138177793 | 0.6265573116802111 | 9 | -396.0 | -176.0 |
| `market_side_ask` | 18 | 1 | 0.18925 | 0.5709687067032417 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
