# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-18T18:27:44.080630+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `16` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `0.005970318559447213`
- Tick Brownian delta log loss vs candle: `0.01201799922704827`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 16 | 1 | 0.123412254091389 | 0.41156222991594815 | 9 | -142.0 | -57.0 |
| `v28` | 16 | 1 | 0.1384470960841142 | 0.46535014854172035 | 8 | -224.0 | -112.0 |
| `candle_brownian` | 16 | 1 | 0.2085529183677765 | 0.6100493499289742 | 8 | -224.0 | -112.0 |
| `tick_brownian` | 16 | 1 | 0.21452323692722372 | 0.6220673491560225 | 8 | -224.0 | -112.0 |
| `market_side_ask` | 16 | 1 | 0.07565000000000001 | 0.32160740590586817 | 8 | -224.0 | -112.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
