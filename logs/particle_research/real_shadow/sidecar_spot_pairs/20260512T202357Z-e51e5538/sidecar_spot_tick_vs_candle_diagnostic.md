# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T02:01:20.557072+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `0.0012402146029509842`
- Tick Brownian delta log loss vs candle: `0.002512759826870159`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.10340771443516168 | 0.35773716989376786 | 9 | -117.0 | -2.0 |
| `v28` | 18 | 1 | 0.13083855609782075 | 0.4489721516483989 | 9 | -207.0 | -92.0 |
| `candle_brownian` | 18 | 1 | 0.19588257113449023 | 0.5844474605583836 | 9 | -207.0 | -92.0 |
| `tick_brownian` | 18 | 1 | 0.19712278573744121 | 0.5869602203852538 | 9 | -207.0 | -92.0 |
| `market_side_ask` | 18 | 1 | 0.050649999999999994 | 0.25491306171645356 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
