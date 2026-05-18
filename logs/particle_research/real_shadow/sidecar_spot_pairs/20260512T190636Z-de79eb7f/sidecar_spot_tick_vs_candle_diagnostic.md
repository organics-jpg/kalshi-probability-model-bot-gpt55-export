# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:20:41.330084+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `-0.0357016762447879`
- Tick Brownian delta log loss vs candle: `-0.07334063352326425`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.11602099995769903 | 0.39271402098280705 | 9 | -117.0 | -47.0 |
| `v28` | 18 | 1 | 0.15016579435416164 | 0.4902264430511033 | 9 | -207.0 | -92.0 |
| `candle_brownian` | 18 | 1 | 0.1942091263153448 | 0.5810543396452725 | 9 | -207.0 | -92.0 |
| `tick_brownian` | 18 | 1 | 0.1585074500705569 | 0.5077137061220083 | 9 | -207.0 | -92.0 |
| `market_side_ask` | 18 | 1 | 0.050649999999999994 | 0.25491306171645356 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
