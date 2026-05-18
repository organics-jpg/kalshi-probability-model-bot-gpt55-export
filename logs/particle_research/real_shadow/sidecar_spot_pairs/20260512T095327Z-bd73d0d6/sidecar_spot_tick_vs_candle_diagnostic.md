# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:22.915112+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `-0.0003836282320905937`
- Tick Brownian delta log loss vs candle: `-0.0008707102233257991`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.19772711452313377 | 0.857811235540939 | 8 | -53.6 | -26.8 |
| `v28` | 18 | 1 | 0.00574948546480377 | 0.07885422262343192 | 9 | -60.300000000000004 | -26.8 |
| `candle_brownian` | 18 | 1 | 0.10754774051470864 | 0.39741468252113904 | 9 | -60.300000000000004 | -26.8 |
| `tick_brownian` | 18 | 1 | 0.10716411228261805 | 0.39654397229781324 | 9 | -60.300000000000004 | -26.8 |
| `market_side_ask` | 18 | 1 | 0.0041665 | 0.06667770405535281 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
